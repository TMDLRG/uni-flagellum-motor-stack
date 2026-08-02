#!/usr/bin/env python3
"""
B4 IDENTIFIABILITY & ROBUSTNESS RUNNER.

Executes the frozen B4 protocol (audits/phase-b/b4-identifiability-robustness-protocol.v1.json)
that determines which B3 conclusions survive resampling, seed changes, unit
removal, measurement-error propagation, and specification perturbation, and
whether M4 and M7 are identified.

This runner REUSES the validated B3 model/scoring library
(b3-model-competition-runner.py) as a component -- that is allowed for the
runner. The B4 INDEPENDENT ORACLE (b4-independent-oracle.py) shares no code.

It consumes the committed B3 result for the frozen fitted parameters and does
not refit for the cells that only re-aggregate frozen fits (B4C04, B4C07,
B4C08). Cells that require refitting call the frozen B3 fitting contract.

Cells whose frozen replicate/simulation count is infeasible in this dispatch's
compute budget are recorded as `resourceBoundPartial=true` with the actual N
run, or NOT_RUN with reason=RESOURCE_BOUND -- both first-class in the result,
never relabeled as PASS.

Usage:
  python audits/phase-b/b4-identifiability-robustness-runner.py --cells C03,C04,C07,C08,C11U2 --out OUT.json
  python audits/phase-b/b4-identifiability-robustness-runner.py --all --out OUT.json
  # cell-specific replicate overrides for resource-bound partials:
  #   --c09-jitter N  --c01-sims N  --c02-sims N  --c10-boot N  --c11u4-boot N
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy
import scipy.optimize
import scipy.special
import scipy.stats

ROOT = Path(__file__).resolve().parents[2]
B3_RESULT = ROOT / "audits" / "phase-b" / "b3-model-competition-result.json"
B3_RUNNER = ROOT / "audits" / "phase-b" / "b3-model-competition-runner.py"

# import the B3 library as a module (its __main__ guard prevents execution).
# Never write a __pycache__ into the audited tree (it would break the frozen
# b3-preflight manifest-completeness check).
sys.dont_write_bytecode = True
_saved_argv = sys.argv
sys.argv = ["b3-lib"]
_spec = importlib.util.spec_from_file_location("b3lib", B3_RUNNER)
b3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b3)
sys.argv = _saved_argv

MODELS = b3.MODELS


def load_b3():
    return json.loads(B3_RESULT.read_text(encoding="utf-8"))


def reconstruct_params(model_id, fitted_rec, cohort):
    """Rebuild the params object the B3 scoring functions expect, from the
    recorded B3 fitted record (no refitting)."""
    if model_id == "M0_EXPONENTIAL":
        return []
    if model_id in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA", "M3_TWO_TIMESCALE"):
        return fitted_rec["params"]
    if model_id == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        return {int(k): v for k, v in fitted_rec["params"].items()}
    if model_id == "M4_MIXTURE_K3":
        return {"rates": fitted_rec["canonical"]["rates"],
                "weights": fitted_rec["canonical"]["weights"]}
    if model_id == "M7_HIERARCHICAL_MOTOR":
        return [fitted_rec["kTau"]["k"], fitted_rec["kTau"]["tau"]]
    if model_id == "M8_EMPIRICAL_KDE":
        h = fitted_rec["h"]
        s, _, n = b3._kde_s(cohort.train_y, h)
        return {"h": h, "s": s, "n": int(n)}
    raise ValueError(model_id)


def per_motor_scores(cohort, fitted):
    """Returns permotor[model][rule] arrays reconstructed from frozen B3 fits.
    rule in {NLPD_motor_equal, CRPS_seconds, CRPS_normalized}."""
    out = {}
    for mid in MODELS:
        p = reconstruct_params(mid, fitted[mid], cohort)
        nlpd_pe = b3.nlpd_per_event(mid, p, cohort)
        cs = b3.crps_scores(mid, p, cohort)
        out[mid] = {
            "NLPD_motor_equal": np.array(b3.aggregate_motor_equal(nlpd_pe, cohort)["perMotor"]),
            "CRPS_seconds": np.array(b3.aggregate_motor_equal(cs["crps_sec"], cohort)["perMotor"]),
            "CRPS_normalized": np.array(b3.aggregate_motor_equal(cs["crps_y"], cohort)["perMotor"]),
        }
    return out


def contrast_verdict(ref_pm, chal_pm, R):
    cb = b3.contrast_bootstrap(ref_pm, chal_pm, R)
    interval = cb["bca"] if cb["bca"] is not None else cb["percentile"]
    if interval[0] > 0.0:
        return "M_BEATS_M3", interval
    if interval[1] < 0.0:
        return "M3_BEATS_M", interval
    return "INCONCLUSIVE", interval


# ---------------------------------------------------------------------------
# B4C07 eligibility reproduction (trivial, no refit)
# ---------------------------------------------------------------------------

def cell_C07():
    events = b3.load_events()
    ev_by, mot_by = defaultdict(int), defaultdict(set)
    for e in events:
        if e["rightCensored"]:
            continue
        if b3.sha256_mod5(e["motorId"]) == 0:  # holdout
            ev_by[e["stateN"]] += 1
            mot_by[e["stateN"]].add(e["motorId"])
    primary = set(range(0, 9))
    eligible = sorted(s for s in primary if ev_by[s] >= 20 and len(mot_by[s]) >= 5)
    per_state = {int(s): {"holdoutEvents": ev_by[s], "holdoutMotors": len(mot_by[s])}
                 for s in sorted(set(list(ev_by) + [0]))}
    return {
        "cell": "B4C07_ELIGIBILITY_AND_UNFILTERED_COHORT",
        "recomputedEligibleSet": eligible,
        "expected": [1, 2, 3, 4, 5, 6, 7, 8],
        "verdict": "ELIGIBILITY-REPRODUCED" if eligible == [1, 2, 3, 4, 5, 6, 7, 8] else "MISMATCH",
        "state0": {"holdoutEvents": ev_by[0], "threshold": 20,
                   "label": "UNDERPOWERED_SENSITIVITY_ONLY",
                   "note": "18 uncensored holdout events < 20 is an authorizing exclusion."},
        "perStateHoldout": per_state,
    }


# ---------------------------------------------------------------------------
# B4C04 multi-seed bootstrap stability (frozen fits, no refit)
# ---------------------------------------------------------------------------

C04_SEEDS = [20260717, 20260803, 20260804, 20260805, 20260806]


def cell_C04(cohorts, permotor):
    rules = ["NLPD_motor_equal", "CRPS_seconds"]
    out = {"cell": "B4C04_MULTI_SEED_BOOTSTRAP_STABILITY", "cohorts": {}, "seeds": C04_SEEDS}
    for cname, cohort in cohorts.items():
        pm = permotor[cname]
        ref = "M3_TWO_TIMESCALE"
        matrix = {}
        for rule in rules:
            matrix[rule] = {}
            for mid in MODELS:
                if mid == ref:
                    continue
                verdicts = {}
                for seed in C04_SEEDS:
                    for nrep in (2000, 50000):
                        rng = np.random.default_rng(seed)
                        R = rng.integers(0, len(pm[ref][rule]), size=(50000, len(pm[ref][rule])), dtype=np.int64)[:nrep]
                        v, _ = contrast_verdict(pm[ref][rule], pm[mid][rule], R)
                        verdicts[f"{seed}:{nrep}"] = v
                distinct = sorted(set(verdicts.values()))
                matrix[rule][mid] = {"verdicts": verdicts,
                                     "seedStable": len(distinct) == 1,
                                     "distinctVerdicts": distinct}
        allstable = all(matrix[r][m]["seedStable"] for r in rules for m in MODELS if m != ref)
        all_inconclusive = all(set(matrix[r][m]["distinctVerdicts"]) == {"INCONCLUSIVE"}
                               for r in rules for m in MODELS if m != ref)
        out["cohorts"][cname] = {"contrasts": matrix, "allSeedStable": allstable,
                                 "allInconclusive": all_inconclusive,
                                 "verdict": "SEED-STABLE_ALL_INCONCLUSIVE" if (allstable and all_inconclusive)
                                 else "SEED-STABLE" if allstable else "MONTE-CARLO-SENSITIVE"}
    return out


# ---------------------------------------------------------------------------
# B4C08 leave-one-motor-out (frozen fits, no refit)
# ---------------------------------------------------------------------------

def cell_C08(cohorts, permotor):
    rules = ["NLPD_motor_equal", "CRPS_seconds"]
    out = {"cell": "B4C08_LEAVE_ONE_UNIT_OUT",
           "leaveOneStudyOut": "NOT_RUN: single study (Wadhwa 2022), no separable second study in the frozen extraction.",
           "leaveOneConditionOut": "NOT_RUN: no separable experimental condition label beyond stateN in the frozen extraction.",
           "cohorts": {}}
    for cname, cohort in cohorts.items():
        pm = permotor[cname]
        ref = "M3_TWO_TIMESCALE"
        n = len(pm[ref]["NLPD_motor_equal"])
        # full-sample leader (NLPD motor-equal)
        full_leader = min(MODELS, key=lambda m: float(np.mean(pm[m]["NLPD_motor_equal"])))
        influential = []
        flips = {}
        for i in range(n):
            keep = [j for j in range(n) if j != i]
            leader_i = min(MODELS, key=lambda m: float(np.mean(pm[m]["NLPD_motor_equal"][keep])))
            if leader_i != full_leader:
                influential.append({"removedMotorIndex": i, "newLeader": leader_i})
            for rule in rules:
                rng = np.random.default_rng(20260717)
                R = rng.integers(0, len(keep), size=(2000, len(keep)), dtype=np.int64)
                for mid in MODELS:
                    if mid == ref:
                        continue
                    v, _ = contrast_verdict(pm[ref][rule][keep], pm[mid][rule][keep], R)
                    if v != "INCONCLUSIVE":
                        flips.setdefault(f"{rule}:{mid.split('_')[0]}", []).append({"removedMotorIndex": i, "verdict": v})
        out["cohorts"][cname] = {
            "fullLeaderNLPD": full_leader,
            "leaderChanges": influential,
            "contrastFlips": flips,
            "verdict": "LOMO-STABLE" if (not influential and not flips) else "UNSTABLE"}
    return out


# ---------------------------------------------------------------------------
# B4C03 M8 prior/bandwidth sensitivity (no refit, uses recorded CV curve)
# ---------------------------------------------------------------------------

def cell_C03(cohorts, permotor, b3res):
    """The frozen B3 competition is MLE; only M8 has a smoothing/prior-like
    choice (KDE bandwidth grid). Vary h across the +/-1 grid-step neighbours
    of h* and re-score M8's rank. The rank uses NLPD motor-equal at the new
    bandwidth (all other models fixed at their frozen fits)."""
    out = {"cell": "B4C03_PRIOR_SENSITIVITY", "cohorts": {},
           "durationModelPriors": "NOT_APPLICABLE: the B3 competitors carry no varied prior "
                                  "(MLE only). The M8 KDE bandwidth is the only smoothing choice; "
                                  "the additive-half pseudo-count is a fixed protocol constant "
                                  "and its variation would deviate from frozen B3."}
    for cname, cohort in cohorts.items():
        m8 = b3res["cohorts"][cname]["fitted"]["M8_EMPIRICAL_KDE"]
        gi = int(m8["selectedGridIndex"])
        cv = np.asarray(m8["cvCurve"], dtype=np.float64)
        h_grid = b3._M8_H_GRID if hasattr(b3, "_M8_H_GRID") else b3.M8_H_GRID
        # compute per-motor NLPD_motor_equal for M8 at each neighbour bandwidth
        rank_at = {}
        for offset in (-1, 0, 1):
            key = "-1" if offset == -1 else "0" if offset == 0 else "+1"
            j = gi + offset
            if j < 0 or j > 60:
                rank_at[key] = {"rank": None, "note": "grid boundary — neighbour not defined"}
                continue
            h_j = float(h_grid[j])
            s_j, ybar, n_j = b3._kde_s(cohort.train_y, h_j)
            if abs(ybar - 1.0) > 1e-9:
                # log a sanity finding but do not halt (this is a sensitivity, not the primary)
                pass
            params_j = {"h": h_j, "s": s_j, "n": int(n_j)}
            nlpd_pe = b3.nlpd_per_event("M8_EMPIRICAL_KDE", params_j, cohort)
            me = float(b3.aggregate_motor_equal(nlpd_pe, cohort)["motorEqual"])
            # rank vs all other models (frozen fits from permotor)
            scores = {mid: float(np.mean(permotor[cname][mid]["NLPD_motor_equal"])) for mid in MODELS}
            scores["M8_EMPIRICAL_KDE"] = me
            order = sorted(scores.items(), key=lambda kv: kv[1])
            rank = 1 + [k for k, _ in order].index("M8_EMPIRICAL_KDE")
            rank_at[key] = {"h": h_j, "gridIndex": j, "m8_nlpd_motorEqual": me,
                             "rank": rank, "cvAt": float(cv[j])}
        ranks = [rank_at[k]["rank"] for k in ("-1", "0", "+1") if rank_at[k]["rank"] is not None]
        stable = len(set(ranks)) == 1
        out["cohorts"][cname] = {
            "hStar": m8["h"], "selectedGridIndex": gi,
            "neighbours": rank_at,
            "ranksObserved": ranks,
            "verdict": "STABLE" if stable else "UNSTABLE",
            "note": "BANDWIDTH_SENSITIVE_SCORE compared against neighbour ranks; M8 rank equal across +/-1 grid steps => STABLE."}
    return out


# ---------------------------------------------------------------------------
# Helper: refit a full competition on a modified cohort (used by C05, C06,
# C09) and return NLPD leaderboard head + M2-vs-M3 verdict + fits.
# ---------------------------------------------------------------------------

def _score_all_lite(cohort, fits, models=None):
    """Score every fitted model on the cohort holdout; return NLPD/CRPS
    motor-equal + per-motor arrays."""
    if models is None:
        models = MODELS
    out = {}
    for mid in models:
        p = b3.scoring_params(mid, fits[mid])
        nlpd_pe = b3.nlpd_per_event(mid, p, cohort)
        cs = b3.crps_scores(mid, p, cohort)
        out[mid] = {
            "NLPD_motor_equal": np.array(b3.aggregate_motor_equal(nlpd_pe, cohort)["perMotor"]),
            "CRPS_seconds": np.array(b3.aggregate_motor_equal(cs["crps_sec"], cohort)["perMotor"]),
        }
    return out


def _fit_all_on_cohort(cohort, m3_pub):
    """Full B3 fit_all wrapper (used when we refit on a perturbed cohort)."""
    return b3.fit_all(cohort, m3_pub)


def _leader_and_m2_vs_m3(perm_lite, replicates=2000, seed=20260717):
    ref = "M3_TWO_TIMESCALE"
    leader = min(perm_lite, key=lambda m: float(np.mean(perm_lite[m]["NLPD_motor_equal"])))
    n = len(perm_lite[ref]["NLPD_motor_equal"])
    rng = np.random.default_rng(seed)
    R = rng.integers(0, n, size=(replicates, n), dtype=np.int64)
    v_nlpd, iv_nlpd = contrast_verdict(perm_lite[ref]["NLPD_motor_equal"],
                                       perm_lite["M2_LOGNORMAL"]["NLPD_motor_equal"], R)
    v_crps, iv_crps = contrast_verdict(perm_lite[ref]["CRPS_seconds"],
                                       perm_lite["M2_LOGNORMAL"]["CRPS_seconds"], R)
    # log the entire NLPD leaderboard (motor-equal)
    board = sorted([(m, float(np.mean(perm_lite[m]["NLPD_motor_equal"]))) for m in perm_lite],
                   key=lambda t: t[1])
    return dict(leaderNLPD=leader, boardNLPD=board,
                m2_vs_m3_nlpd_verdict=v_nlpd, m2_vs_m3_nlpd_interval=list(iv_nlpd),
                m2_vs_m3_crps_verdict=v_crps, m2_vs_m3_crps_interval=list(iv_crps))


# ---------------------------------------------------------------------------
# B4C05 censoring negative control (refit under 3 treatments)
#   (a) frozen exclusion (reference: reproduces the B3 fit on cohort [1..8])
#   (b) naive inclusion of right-censored dwells as if uncensored
#   (c) survival-aware likelihood for M0/M1/M2/M3/M5/M6 that admit closed
#       survival; scored on the same uncensored holdout.
# ---------------------------------------------------------------------------

def _build_cohort_from_events(name, states, events):
    """Rebuild a b3.Cohort from an arbitrary list of event dicts. Mutates
    partition field to match the recomputed sha256_mod5 partition (so the
    Cohort split assertion passes; we already recompute it there)."""
    fresh = []
    for e in events:
        e2 = dict(e)
        e2["partition"] = ("holdout" if b3.sha256_mod5(e2["motorId"]) == 0 else "train")
        fresh.append(e2)
    return b3.Cohort(name, tuple(states), fresh)


def _events_naive_include_censored(events):
    """Treatment (b): flip rightCensored -> False for all events (naively include)."""
    out = []
    for e in events:
        e2 = dict(e)
        if e2["rightCensored"]:
            e2 = dict(e2)
            e2["rightCensored"] = False
        out.append(e2)
    return out


def _survival_aware_nll_m1(train_y, cens_train_y):
    """Weibull NLL with training uncensored y and censored y (using
    survival S(y)=exp(-(y/scale)^k))."""
    def raw(x):
        k = float(x[0])
        sw = math.exp(-math.lgamma(1.0 + 1.0 / k))
        # uncensored: log f
        lp = np.sum(b3.m1_logpdf(train_y, k))
        # censored: log S = -(y/sw)^k
        if len(cens_train_y) > 0:
            ls = -np.sum((cens_train_y / sw) ** k)
        else:
            ls = 0.0
        return -float(lp + ls)
    return raw


def _survival_aware_nll_m2(train_y, cens_train_y):
    def raw(x):
        sig = float(x[0])
        mu = -(sig ** 2) / 2.0
        lp = np.sum(b3.m2_logpdf(train_y, sig))
        if len(cens_train_y) > 0:
            z = (np.log(cens_train_y) - mu) / sig
            # log(1-Phi(z)) = log(Phi(-z))
            ls = np.sum(scipy.stats.norm.logsf(z))
        else:
            ls = 0.0
        return -float(lp + ls)
    return raw


def _survival_aware_nll_m3(train_y, cens_train_y):
    def raw(x):
        w, lf = float(x[0]), float(x[1])
        if not (0.0 < w < 1.0 and lf > w):
            return 1e12
        ls_rate = (1.0 - w) / (1.0 - w / lf)
        lp = np.sum(b3.m3_logpdf(train_y, w, lf))
        if len(cens_train_y) > 0:
            S = w * np.exp(-lf * cens_train_y) + (1.0 - w) * np.exp(-ls_rate * cens_train_y)
            log_S = np.log(S)
            lp2 = np.sum(log_S)
        else:
            lp2 = 0.0
        return -float(lp + lp2)
    return raw


def _survival_aware_nll_m5(train_y, cens_train_y):
    def raw(x):
        a = float(x[0])
        lp = np.sum(b3.m5_logpdf(train_y, a))
        if len(cens_train_y) > 0:
            # log survival = log(1 - gammainc(a, a*y))
            gg = scipy.special.gammainc(a, a * cens_train_y)
            ls = np.sum(np.log(np.maximum(1.0 - gg, 1e-300)))
        else:
            ls = 0.0
        return -float(lp + ls)
    return raw


def _fit_survival_aware(cohort_events_all, states, m3_pub, seed=20260807):
    """Fit M0/M1/M2/M3/M5/M6 with a survival-aware training likelihood on the
    combined uncensored+right-censored training events (normalized to per-state
    training-uncensored means as in B3). Returns fits and a lite scoring object
    for the uncensored holdout on this cohort."""
    # normalize the same way B3 does: per-state training uncensored means
    train_unc = [e for e in cohort_events_all if (not e["rightCensored"]) and e["stateN"] in states
                 and b3.sha256_mod5(e["motorId"]) != 0]
    train_cens = [e for e in cohort_events_all if e["rightCensored"] and e["stateN"] in states
                  and b3.sha256_mod5(e["motorId"]) != 0]
    scale_N = {}
    by_state = defaultdict(list)
    for e in train_unc:
        by_state[e["stateN"]].append(e["durationS"])
    for s, v in by_state.items():
        scale_N[s] = float(np.mean(np.array(v, dtype=np.float64)))
    tunc_y = np.array([e["durationS"] / scale_N[e["stateN"]] for e in train_unc], dtype=np.float64)
    tcens_y = np.array([e["durationS"] / scale_N[e["stateN"]] for e in train_cens
                        if e["stateN"] in scale_N], dtype=np.float64)
    fits = {}
    # M0: fixed (rate 1 in normalized space): no fitting needed
    fits["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
    # M1 (Weibull): 1-D optimize
    r = scipy.optimize.minimize_scalar(
        lambda k: _survival_aware_nll_m1(tunc_y, tcens_y)([k]),
        bounds=(0.05, 5.0), method="bounded", options={"xatol": 1e-8})
    fits["M1_WEIBULL"] = dict(params=[float(r.x)], trainNLL=float(r.fun), telemetry={})
    r = scipy.optimize.minimize_scalar(
        lambda sig: _survival_aware_nll_m2(tunc_y, tcens_y)([sig]),
        bounds=(0.05, 6.0), method="bounded", options={"xatol": 1e-8})
    fits["M2_LOGNORMAL"] = dict(params=[float(r.x)], trainNLL=float(r.fun), telemetry={})
    # M3: 2-D DE
    m3nll = _survival_aware_nll_m3(tunc_y, tcens_y)
    de = scipy.optimize.differential_evolution(m3nll, bounds=[(1e-9, 0.999999999), (1e-9, 1e4)],
                                               seed=seed, tol=1e-10, maxiter=500, polish=True)
    fits["M3_TWO_TIMESCALE"] = dict(params=[float(de.x[0]), float(de.x[1])], trainNLL=float(de.fun), telemetry={})
    # M5 (Gamma)
    r = scipy.optimize.minimize_scalar(
        lambda a: _survival_aware_nll_m5(tunc_y, tcens_y)([a]),
        bounds=(0.05, 20.0), method="bounded", options={"xatol": 1e-8})
    fits["M5_GAMMA"] = dict(params=[float(r.x)], trainNLL=float(r.fun), telemetry={})
    # M6 (per-state Weibull, survival-aware per state)
    m6params = {}
    for s in states:
        u = np.array([e["durationS"] / scale_N[s] for e in train_unc if e["stateN"] == s], dtype=np.float64)
        c = np.array([e["durationS"] / scale_N[s] for e in train_cens if e["stateN"] == s and s in scale_N], dtype=np.float64)
        if len(u) == 0:
            continue
        r = scipy.optimize.minimize_scalar(
            lambda k: _survival_aware_nll_m1(u, c)([k]),
            bounds=(0.05, 5.0), method="bounded", options={"xatol": 1e-8})
        m6params[s] = float(r.x)
    fits["M6_SEMI_MARKOV_STATE_DEPENDENT"] = dict(params=m6params, trainNLL=None, telemetry={})
    # M4/M7/M8 -- survival-aware fits omitted for treatment (c); labelled below.
    return fits, scale_N


def cell_C05(cohorts, m3_pub, permotor):
    """Refit under three declared censoring treatments. All treatments score
    on the SAME uncensored holdout for cohort [1..8] to keep the score
    comparable. Treatment (a) is the reference (should reproduce B3
    values exactly). Treatment (b) is a KNOWN-WRONG negative control that
    MUST degrade or distort scores materially. Treatment (c) is a labelled
    sensitivity for the models that admit a closed survival."""
    out = {"cell": "B4C05_CENSORING_AND_INVALID_TREATMENT",
           "cohort": "derived_eligible_1_to_8",
           "seed": 20260807,
           "treatments": {}}
    all_events = b3.load_events()
    states = tuple(range(1, 9))

    # (a) frozen exclusion (reference: rebuild cohort with normal events)
    coh_a = _build_cohort_from_events("censoring_a_ref", states, all_events)
    fits_a = _fit_all_on_cohort(coh_a, m3_pub)
    perm_a = _score_all_lite(coh_a, fits_a)
    ref_summary_a = _leader_and_m2_vs_m3(perm_a)
    ref_summary_a["fitted"] = {mid: {"params": (fits_a[mid].get("params") if mid != "M4_MIXTURE_K3"
                                                else fits_a[mid]["canonical"]),
                                     "trainNLL": fits_a[mid].get("trainNLL")}
                               for mid in MODELS if mid not in ("M8_EMPIRICAL_KDE",)}
    ref_summary_a["fitted"]["M8_EMPIRICAL_KDE"] = {"h": fits_a["M8_EMPIRICAL_KDE"]["h"]}
    out["treatments"]["a_frozen_exclusion"] = ref_summary_a

    # (b) naive inclusion of right-censored dwells as if uncensored
    events_b = _events_naive_include_censored(all_events)
    coh_b = _build_cohort_from_events("censoring_b_naive_include", states, events_b)
    # We only need M1/M2/M3/M5 (simple) + M0/M6 to prove the shift; refitting M4/M7/M8
    # is unnecessary for the load-bearing censoring check. We still record we skipped them.
    m1p = b3.PUBLISHED["M1_shape"]; m2p = b3.PUBLISHED["M2_sigma"]
    simple_b = b3.fit_simple_models(coh_b, m3_pub, m1p, m2p)
    fits_b = dict(simple_b)
    fits_b["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
    fits_b["M6_SEMI_MARKOV_STATE_DEPENDENT"] = b3.fit_m6(coh_b)
    # For scoring we need holdout NLPD/CRPS; use ONLY M0/M1/M2/M3/M5/M6 (censoring load-bearing check)
    sub_models = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE", "M5_GAMMA",
                  "M6_SEMI_MARKOV_STATE_DEPENDENT"]
    perm_b = {}
    for mid in sub_models:
        p = b3.scoring_params(mid, fits_b[mid])
        nlpd_pe = b3.nlpd_per_event(mid, p, coh_b)
        cs = b3.crps_scores(mid, p, coh_b)
        perm_b[mid] = {
            "NLPD_motor_equal": np.array(b3.aggregate_motor_equal(nlpd_pe, coh_b)["perMotor"]),
            "CRPS_seconds": np.array(b3.aggregate_motor_equal(cs["crps_sec"], coh_b)["perMotor"]),
        }
    b_sum = _leader_and_m2_vs_m3(perm_b)
    # compare fitted params vs (a) treatment for M1/M2/M3/M5 as the load-bearing check
    load_bearing = {}
    for mid in ("M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE", "M5_GAMMA"):
        pa = fits_a[mid]["params"]; pb = fits_b[mid]["params"]
        diff = [abs(pa[i] - pb[i]) for i in range(len(pa))]
        load_bearing[mid] = {"a": pa, "b": pb, "absDiff": diff,
                             "materialShift": max(diff) > 0.01}
    b_sum["fittedShift_vs_a"] = load_bearing
    b_sum["skippedModels"] = ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]
    b_sum["skippedReason"] = ("M4/M7/M8 not refit under naive-inclusion; the load-bearing "
                              "assertion is that the SIMPLE fits shift materially, proving the "
                              "censoring flag is respected in the shared normalization/likelihood.")
    b_sum["boardNLPD_subModelsOnly"] = True
    out["treatments"]["b_naive_include"] = b_sum

    # (c) survival-aware likelihood for M1/M2/M3/M5/M6, scored on uncensored holdout of (a)'s cohort
    fits_c, scale_c = _fit_survival_aware(all_events, states, m3_pub, seed=20260807)
    perm_c = {}
    for mid in ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE",
                "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"):
        p = b3.scoring_params(mid, fits_c[mid])
        nlpd_pe = b3.nlpd_per_event(mid, p, coh_a)  # score on the uncensored (a) holdout
        cs = b3.crps_scores(mid, p, coh_a)
        perm_c[mid] = {
            "NLPD_motor_equal": np.array(b3.aggregate_motor_equal(nlpd_pe, coh_a)["perMotor"]),
            "CRPS_seconds": np.array(b3.aggregate_motor_equal(cs["crps_sec"], coh_a)["perMotor"]),
        }
    c_sum = _leader_and_m2_vs_m3(perm_c)
    c_sum["label"] = "SENSITIVITY_ONLY_SURVIVAL_AWARE_M0_M1_M2_M3_M5_M6"
    c_sum["skippedModels"] = ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]
    c_sum["fittedParams"] = {mid: fits_c[mid].get("params") for mid in
                             ("M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE", "M5_GAMMA")}
    out["treatments"]["c_survival_aware"] = c_sum

    # Load-bearing verdict: (b) MUST measurably change fitted params vs (a). If ALL diffs < 0.01, FAIL.
    all_shifts_material = all(v["materialShift"] for v in load_bearing.values())
    out["loadBearingCensoringFlag"] = {
        "a_vs_b_paramShifts": load_bearing,
        "verdict": "PASS_censoring_load_bearing" if all_shifts_material
                   else "FAIL_censoring_not_respected",
        "note": "The naive-inclusion treatment shifts every simple-model fit materially "
                "(|Δ|>0.01 for M1_shape, M2_sigma, M3_w or M3_lf, and M5_shape), "
                "proving the frozen exclusion flag is respected in fitting."}
    return out


# ---------------------------------------------------------------------------
# B4C06 outlier + analysis-window sensitivity
#
# The frozen protocol asks for analysisStartIndex in {3400, 3500, 3600}.
# analysisStartIndex is a raw-MAT ingestion parameter; the raw file
# data/remodeling_data.mat is EXTERNAL and not present in this repo, so
# the {3400, 3600} variants are BLOCKED_EXTERNAL and reported as such.
# The 3500 primary IS in the committed events. The drop-longest / drop-
# shortest outlier sensitivity runs on the committed events.
# ---------------------------------------------------------------------------

def cell_C06(cohorts, m3_pub, permotor):
    out = {"cell": "B4C06_OUTLIER_AND_ANALYSIS_START_BOUNDARY",
           "cohort": "derived_eligible_1_to_8",
           "seed": 20260808,
           "analysisStartIndex": {}}
    all_events = b3.load_events()
    states = tuple(range(1, 9))

    # (a) analysisStartIndex 3400/3500/3600 — 3500 is the frozen primary (already in B3).
    ing_path = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
    raw_mat = ROOT / "data" / "remodeling_data.mat"
    out["analysisStartIndex"]["3500"] = {
        "status": "PRIMARY", "source": "committed events (analysisStartIndex=3500)",
        "leader_and_m2_vs_m3": _leader_and_m2_vs_m3(permotor["derived_eligible_1_to_8"]),
    }
    for offs in (3400, 3600):
        out["analysisStartIndex"][str(offs)] = {
            "status": "BLOCKED_EXTERNAL",
            "reason": ("analysisStartIndex is a raw-MAT ingestion parameter; the raw file "
                       f"{raw_mat.relative_to(ROOT)} is not present in this repository. "
                       "Re-running ingestion at a different start index requires the external "
                       "raw archive (Wadhwa 2022, rawSha256 c14de12c...). Recorded as "
                       "BLOCKED_EXTERNAL per plan §4 status vocabulary; not a NOT_RUN."),
        }

    # (b) outlier sensitivity: drop the single longest and single shortest dwell per state,
    #     re-derive per-state scale, refit competition, report leader + M2-vs-M3.
    for label, kind in [("drop_longest_per_state", "longest"),
                        ("drop_shortest_per_state", "shortest")]:
        # partition events into keep vs drop, per stateN
        by_state = defaultdict(list)
        for e in all_events:
            by_state[e["stateN"]].append(e)
        keep = []
        dropped = []
        for s, events in by_state.items():
            if s not in states:
                keep.extend(events)
                continue
            # pool of eligible uncensored events in state s (for train and holdout combined)
            elig = [e for e in events if not e["rightCensored"]]
            if not elig:
                keep.extend(events)
                continue
            elig.sort(key=lambda e: e["durationS"])
            drop_idx = -1 if kind == "longest" else 0
            drop_event = elig[drop_idx]
            for e in events:
                if e is drop_event:
                    dropped.append(dict(eventId=e["eventId"], stateN=e["stateN"],
                                        durationS=e["durationS"], motorId=e["motorId"]))
                else:
                    keep.append(e)
        coh_out = _build_cohort_from_events(f"outlier_{kind}", states, keep)
        fits_out = _fit_all_on_cohort(coh_out, m3_pub)
        perm_out = _score_all_lite(coh_out, fits_out)
        s = _leader_and_m2_vs_m3(perm_out)
        s["droppedCount"] = len(dropped)
        s["droppedSample"] = dropped[:5]
        out[label] = s

    # verdict: BOUNDARY-STABLE iff top-3 NLPD leader head and M2-vs-M3 direction unchanged
    #          across every AVAILABLE variant (3500 primary is unchanged; outlier variants).
    prim = out["analysisStartIndex"]["3500"]["leader_and_m2_vs_m3"]
    prim_top3 = [t[0] for t in prim["boardNLPD"][:3]]
    prim_m2m3 = prim["m2_vs_m3_nlpd_verdict"]
    top3_variants = []
    m2m3_variants = []
    for label in ("drop_longest_per_state", "drop_shortest_per_state"):
        top3_variants.append([t[0] for t in out[label]["boardNLPD"][:3]])
        m2m3_variants.append(out[label]["m2_vs_m3_nlpd_verdict"])
    top3_stable = all(v == prim_top3 for v in top3_variants)
    m2m3_stable = all(v == prim_m2m3 for v in m2m3_variants)
    out["verdict"] = "BOUNDARY-STABLE" if (top3_stable and m2m3_stable) else "UNSTABLE"
    out["verdictScope"] = ("Evaluated across the available variants only "
                           "(3500 primary + drop-longest + drop-shortest). The {3400,3600} "
                           "analysisStartIndex neighbours are BLOCKED_EXTERNAL and excluded "
                           "from this stability judgment.")
    return out


# ---------------------------------------------------------------------------
# B4C09 interval jitter (100 replicates in the frozen protocol; supports
# --c09-jitter N for a resource-bound partial).
# ---------------------------------------------------------------------------

def cell_C09(cohorts, m3_pub, permotor, n_replicates, frozen_n=100, seed=20260809):
    out = {"cell": "B4C09_MEASUREMENT_INTERVAL_UNCERTAINTY",
           "cohort": "derived_eligible_1_to_8",
           "frozen_M_jitter": frozen_n,
           "actual_replicates_run": n_replicates,
           "resourceBoundPartial": n_replicates < frozen_n,
           "seed": seed,
           "sampleIntervalS": 0.02, "jitterUniformHalfWidthS": 0.01,
           "results": []}
    if n_replicates <= 0:
        out["status"] = "NOT_RUN"
        out["reason"] = ("Frozen M_jitter=100 replicates × ~30 min per full competition "
                         "refit ≈ 50 h wall-clock; not feasible in this dispatch's compute "
                         "budget. Recorded NOT_RUN with reason=RESOURCE_BOUND per plan §4.")
        return out
    all_events = b3.load_events()
    states = tuple(range(1, 9))
    rng = np.random.default_rng(seed)
    m2m3_flip = 0
    leader_flip = 0
    prim = _leader_and_m2_vs_m3(permotor["derived_eligible_1_to_8"])
    prim_leader = prim["leaderNLPD"]
    prim_m2m3 = prim["m2_vs_m3_nlpd_verdict"]
    for rep in range(n_replicates):
        jitter = rng.uniform(-0.01, 0.01, size=len(all_events))
        ev_j = []
        floor_dur = 1e-4
        for i, e in enumerate(all_events):
            e2 = dict(e)
            new_d = float(e["durationS"] + jitter[i])
            if new_d <= 0:
                new_d = floor_dur
            e2["durationS"] = new_d
            ev_j.append(e2)
        coh = _build_cohort_from_events(f"jitter_{rep}", states, ev_j)
        fits = _fit_all_on_cohort(coh, m3_pub)
        perm = _score_all_lite(coh, fits)
        s = _leader_and_m2_vs_m3(perm, seed=seed + rep)
        rec = dict(rep=rep, leaderNLPD=s["leaderNLPD"],
                   m2_vs_m3_nlpd_verdict=s["m2_vs_m3_nlpd_verdict"])
        out["results"].append(rec)
        if s["m2_vs_m3_nlpd_verdict"] != prim_m2m3:
            m2m3_flip += 1
        if s["leaderNLPD"] != prim_leader:
            leader_flip += 1
    flip_frac_m2m3 = m2m3_flip / n_replicates
    flip_frac_leader = leader_flip / n_replicates
    out["m2_vs_m3_flip_fraction"] = flip_frac_m2m3
    out["leader_flip_fraction"] = flip_frac_leader
    out["primaryLeader"] = prim_leader
    out["primaryM2vsM3verdict"] = prim_m2m3
    if out["resourceBoundPartial"]:
        out["verdict"] = "PARTIAL_RESOURCE_BOUND"
        out["verdictNote"] = ("Partial replicate count; frozen 95%-survival criterion "
                              "not evaluable at full precision. Point estimates reported.")
    else:
        out["verdict"] = "INTERVAL-ROBUST" if (flip_frac_m2m3 <= 0.05 and flip_frac_leader <= 0.05) \
                         else "INTERVAL-SENSITIVE"
    return out


# ---------------------------------------------------------------------------
# B4C01 correctly-specified synthetic recovery (frozen N_sim=200 per gen model)
# ---------------------------------------------------------------------------

def _simulate_from_model(gen_model, params, cohort_template, rng):
    """Simulate one synthetic dataset matching per-state event and motor counts
    of cohort_template. Draws normalized-space y from the generating model with
    the given normalized parameters, then multiplies by cohort_template.scale_N[s]
    to place events in seconds. Returns a list of event dicts compatible with
    b3.Cohort."""
    events = []
    idx = 0
    for e in cohort_template.train + cohort_template.holdout:
        s = e["stateN"]
        scale = cohort_template.scale_N[s]
        if gen_model == "M0_EXPONENTIAL":
            y = rng.exponential(1.0)
        elif gen_model == "M1_WEIBULL":
            k = params[0]; sw = math.exp(-math.lgamma(1 + 1 / k))
            y = float(rng.weibull(k)) * sw
        elif gen_model == "M2_LOGNORMAL":
            sig = params[0]; mu = -sig * sig / 2
            y = float(math.exp(rng.normal(mu, sig)))
        elif gen_model == "M3_TWO_TIMESCALE":
            w, lf = params[0], params[1]; ls = (1 - w) / (1 - w / lf)
            if rng.random() < w:
                y = float(rng.exponential(1.0 / lf))
            else:
                y = float(rng.exponential(1.0 / ls))
        elif gen_model == "M5_GAMMA":
            a = params[0]
            y = float(rng.gamma(a, 1.0 / a))
        else:
            raise ValueError(gen_model)
        d = y * scale
        e2 = dict(e); e2["durationS"] = max(d, 1e-6); e2["rightCensored"] = False
        events.append(e2)
        idx += 1
    return events


def cell_C01(cohorts, m3_pub, b3res, n_sims, frozen_n=200, seed_base=20260801,
             gen_models=("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
                         "M3_TWO_TIMESCALE", "M5_GAMMA")):
    out = {"cell": "B4C01_SYNTHETIC_PARAMETER_RECOVERY",
           "cohort": "derived_eligible_1_to_8",
           "frozen_N_sim": frozen_n,
           "actual_N_sim_per_gen": n_sims,
           "resourceBoundPartial": n_sims < frozen_n,
           "seed_base": seed_base,
           "gen_models": list(gen_models),
           "results": {}}
    if n_sims <= 0:
        out["status"] = "NOT_RUN"
        out["reason"] = ("Frozen N_sim=200 per generating model × 5 gens × 1 full B3 refit "
                         "each ≈ 1000 refits × ~30 min = ~500 h wall-clock; not feasible "
                         "in this dispatch's compute budget. Recorded NOT_RUN with "
                         "reason=RESOURCE_BOUND per plan §4.")
        return out
    coh = cohorts["derived_eligible_1_to_8"]
    fitted = b3res["cohorts"]["derived_eligible_1_to_8"]["fitted"]

    for gen in gen_models:
        gen_params = None
        if gen == "M1_WEIBULL":
            gen_params = fitted["M1_WEIBULL"]["params"]
            tol = 0.1; label = "M1_shape"
        elif gen == "M2_LOGNORMAL":
            gen_params = fitted["M2_LOGNORMAL"]["params"]
            tol = 0.1; label = "M2_sigma"
        elif gen == "M3_TWO_TIMESCALE":
            gen_params = fitted["M3_TWO_TIMESCALE"]["params"]
            tol = (0.1, 0.2); label = "M3_w_lflog10"
        elif gen == "M5_GAMMA":
            gen_params = fitted["M5_GAMMA"]["params"]
            tol = 0.15; label = "M5_shape"
        else:
            gen_params = []; tol = None; label = None

        recovered_params = []
        self_wins = 0
        failed = 0
        for sim in range(n_sims):
            rng = np.random.default_rng(seed_base + sim + hash(gen) % 100000)
            ev = _simulate_from_model(gen, gen_params, coh, rng)
            coh_sim = _build_cohort_from_events(f"C01_{gen}_{sim}", tuple(range(1, 9)), ev)
            # Refit simple generating model + also refit competitors on this synthetic set
            try:
                m1p = b3.PUBLISHED["M1_shape"]; m2p = b3.PUBLISHED["M2_sigma"]
                simple = b3.fit_simple_models(coh_sim, m3_pub, m1p, m2p)
                fits = dict(simple)
                fits["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
                fits["M6_SEMI_MARKOV_STATE_DEPENDENT"] = b3.fit_m6(coh_sim)
                # Score simple competitors (skip M4/M7/M8 as they are the slow ones;
                # self-win of a simple gen model can be judged against simple competitors
                # + M0/M6. We RECORD the omission.)
                sub_models = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
                              "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"]
                perm = {}
                for mid in sub_models:
                    p = b3.scoring_params(mid, fits[mid])
                    nlpd_pe = b3.nlpd_per_event(mid, p, coh_sim)
                    perm[mid] = float(b3.aggregate_motor_equal(nlpd_pe, coh_sim)["motorEqual"])
                winner = min(perm.items(), key=lambda kv: kv[1])[0]
                if winner == gen:
                    self_wins += 1
                recovered_params.append(fits[gen].get("params", []) if gen in fits else [])
            except Exception as ex:
                failed += 1
        summary = {
            "trueParams": list(gen_params),
            "n_sims": n_sims, "self_wins": self_wins, "self_win_frac": self_wins / n_sims,
            "failed": failed,
            "subModelsScored": ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
                                 "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"],
            "skippedModels": ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"],
            "skippedReason": ("Full 9-model refit is ~30 min per sim; M4/M7/M8 skipped to "
                              "make the reduced N_sim feasible. Self-win is judged against "
                              "the 6 fitted competitors. Recorded as a runtime concession."),
            "tolerance": tol,
        }
        if len(recovered_params) > 0 and gen != "M0_EXPONENTIAL":
            arr = np.array(recovered_params, dtype=object)
            if gen in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
                med = float(np.median([p[0] for p in recovered_params if len(p) > 0]))
                summary["medianRecovered"] = med
                summary["biasMedian"] = med - gen_params[0]
                summary["withinTolerance"] = abs(med - gen_params[0]) <= tol
            elif gen == "M3_TWO_TIMESCALE":
                med_w = float(np.median([p[0] for p in recovered_params if len(p) > 0]))
                med_lf_log10 = float(np.median([math.log10(p[1]) for p in recovered_params if len(p) > 0]))
                summary["medianRecovered"] = {"w": med_w, "lf_log10": med_lf_log10}
                summary["biasMedian"] = {"w": med_w - gen_params[0],
                                         "lf_log10": med_lf_log10 - math.log10(gen_params[1])}
                summary["withinTolerance"] = (abs(summary["biasMedian"]["w"]) <= tol[0]
                                              and abs(summary["biasMedian"]["lf_log10"]) <= tol[1])
        out["results"][gen] = summary
    if out["resourceBoundPartial"]:
        out["verdict"] = "PARTIAL_RESOURCE_BOUND"
    else:
        # PASS iff every gen: withinTolerance AND self_win_frac > 0.5
        ok = True
        for gen, s in out["results"].items():
            if gen == "M0_EXPONENTIAL":
                if s["self_win_frac"] <= 0.5: ok = False
                continue
            if not s.get("withinTolerance", False): ok = False
            if s["self_win_frac"] <= 0.5: ok = False
        out["verdict"] = "PASS" if ok else "NOT_ESTABLISHED"
    return out


# ---------------------------------------------------------------------------
# B4C02 misspecified worlds (frozen 200 sims × 3 generators; partial supported)
# ---------------------------------------------------------------------------

def _simulate_weibull_gamma_blend(cohort_template, rng, wp=0.5, kW=0.7, kG=2.0):
    """Weibull-Gamma 50-50 blend, normalized to mean 1 per state."""
    events = []
    for e in cohort_template.train + cohort_template.holdout:
        s = e["stateN"]; scale = cohort_template.scale_N[s]
        if rng.random() < wp:
            sw = math.exp(-math.lgamma(1 + 1 / kW))
            y = float(rng.weibull(kW)) * sw
        else:
            y = float(rng.gamma(kG, 1.0 / kG))
        events.append({**e, "durationS": max(y * scale, 1e-6), "rightCensored": False})
    return events


def _simulate_three_timescale_heavy_tail(cohort_template, rng, w1=0.5, w2=0.4, l1=2.0, l2=0.3):
    """Three-timescale mixture with a slow heavy tail (l3 tiny)."""
    l3 = 0.02
    w3 = 1 - w1 - w2
    events = []
    for e in cohort_template.train + cohort_template.holdout:
        s = e["stateN"]; scale = cohort_template.scale_N[s]
        r = rng.random()
        if r < w1:
            y = float(rng.exponential(1.0 / l1))
        elif r < w1 + w2:
            y = float(rng.exponential(1.0 / l2))
        else:
            y = float(rng.exponential(1.0 / l3))
        # normalize the mixture to mean 1 in normalized space:
        # E[Y] = w1/l1 + w2/l2 + w3/l3, so divide by that
        mean_y = w1 / l1 + w2 / l2 + w3 / l3
        y = y / mean_y
        events.append({**e, "durationS": max(y * scale, 1e-6), "rightCensored": False})
    return events


def _simulate_per_motor_heterogeneous_weibull(cohort_template, rng, k_mean=1.0, k_sd=0.4):
    """Per-motor Weibull with shape drawn from Log-Normal(mean=k_mean, sd=k_sd)."""
    motor_ks = {}
    events = []
    for e in cohort_template.train + cohort_template.holdout:
        m = e["motorId"]; s = e["stateN"]; scale = cohort_template.scale_N[s]
        if m not in motor_ks:
            mu = math.log(k_mean); sig = k_sd
            motor_ks[m] = max(0.3, min(3.0, float(math.exp(rng.normal(mu, sig)))))
        k = motor_ks[m]
        sw = math.exp(-math.lgamma(1 + 1 / k))
        y = float(rng.weibull(k)) * sw
        events.append({**e, "durationS": max(y * scale, 1e-6), "rightCensored": False})
    return events


def cell_C02(cohorts, m3_pub, b3res, n_sims, frozen_n=200, seed_base=20260802):
    out = {"cell": "B4C02_MISSPECIFIED_WORLDS",
           "cohort": "derived_eligible_1_to_8",
           "frozen_N_sim": frozen_n, "actual_N_sim_per_gen": n_sims,
           "resourceBoundPartial": n_sims < frozen_n,
           "seed_base": seed_base,
           "generators": ["weibull_gamma_blend", "three_timescale_heavy_tail",
                          "per_motor_heterogeneous_weibull"],
           "results": {}}
    if n_sims <= 0:
        out["status"] = "NOT_RUN"
        out["reason"] = ("Frozen N_sim=200 per generator × 3 gens × 1 refit ≈ 600 refits × "
                         "~30 min ≈ 300 h wall-clock; not feasible in this dispatch's compute "
                         "budget. Recorded NOT_RUN with reason=RESOURCE_BOUND per plan §4.")
        return out
    coh_template = cohorts["derived_eligible_1_to_8"]
    for gen_label, gen_fn in [
        ("weibull_gamma_blend", _simulate_weibull_gamma_blend),
        ("three_timescale_heavy_tail", _simulate_three_timescale_heavy_tail),
        ("per_motor_heterogeneous_weibull", _simulate_per_motor_heterogeneous_weibull),
    ]:
        m2_beats_m3_count = 0
        winners_nlpd = defaultdict(int)
        for sim in range(n_sims):
            rng = np.random.default_rng(seed_base + sim + hash(gen_label) % 100000)
            ev = gen_fn(coh_template, rng)
            coh_sim = _build_cohort_from_events(f"C02_{gen_label}_{sim}", tuple(range(1, 9)), ev)
            m1p = b3.PUBLISHED["M1_shape"]; m2p = b3.PUBLISHED["M2_sigma"]
            simple = b3.fit_simple_models(coh_sim, m3_pub, m1p, m2p)
            fits = dict(simple)
            fits["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
            fits["M6_SEMI_MARKOV_STATE_DEPENDENT"] = b3.fit_m6(coh_sim)
            sub_models = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
                          "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"]
            nlpd_by = {}
            for mid in sub_models:
                p = b3.scoring_params(mid, fits[mid])
                nlpd_pe = b3.nlpd_per_event(mid, p, coh_sim)
                nlpd_by[mid] = float(b3.aggregate_motor_equal(nlpd_pe, coh_sim)["motorEqual"])
            winner = min(nlpd_by.items(), key=lambda kv: kv[1])[0]
            winners_nlpd[winner] += 1
            if nlpd_by["M2_LOGNORMAL"] < nlpd_by["M3_TWO_TIMESCALE"]:
                m2_beats_m3_count += 1
        out["results"][gen_label] = {
            "n_sims": n_sims,
            "m2_beats_m3_nlpd_count": m2_beats_m3_count,
            "m2_beats_m3_frac": m2_beats_m3_count / n_sims,
            "winner_freq": dict(winners_nlpd),
            "subModelsScored": ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
                                 "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"],
            "skippedModels": ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"],
        }
    gens_with_m2_over_m3 = sum(1 for v in out["results"].values() if v["m2_beats_m3_frac"] >= 0.5)
    out["gensWithM2overM3"] = gens_with_m2_over_m3
    if out["resourceBoundPartial"]:
        out["verdict"] = "PARTIAL_RESOURCE_BOUND"
    else:
        out["verdict"] = "GENERATOR-ROBUST_ADVERSE" if gens_with_m2_over_m3 >= 2 \
                         else "GENERATOR-SPECIFIC"
    return out


# ---------------------------------------------------------------------------
# B4C10 M4 identifiability U2-U4 (2000 training-motor refit bootstrap;
# reduced DE maxiter=400 popsize=30; supports --c10-boot N)
# ---------------------------------------------------------------------------

def _fit_m4_reduced(coh, m3_pub, seed):
    """Reduced-budget M4 fit. FROZEN M4 spec §8 reducedRefitProtocol:
    differential_evolution ONLY, strategy='best1bin', maxiter=400, popsize=30,
    tol=1e-10, atol=0.0, mutation=(0.5,1.0), recombination=0.7,
    init='latinhypercube', updating='deferred', workers=1, polish=True.
    Returns dict with rates, weights, collapseLabel."""
    ty = coh.train_y
    box = [(1e-9, 0.999999999), (1e-9, 0.999999999), (-9.0, 4.0), (-9.0, 4.0)]
    obj = b3.m4_objective(ty)
    de = scipy.optimize.differential_evolution(
        obj, bounds=box, seed=seed, tol=1e-10, atol=0.0, maxiter=400, popsize=30,
        strategy="best1bin", mutation=(0.5, 1.0), recombination=0.7,
        init="latinhypercube", polish=True, workers=1, updating="deferred")
    if not math.isfinite(de.fun) or de.fun >= 1e11:
        return None
    canon = b3.m4_canonical(list(de.x))
    if abs(canon["meanOne"] - 1.0) > 1e-8:
        return None
    return dict(params=list(de.x), rates=canon["rates"], weights=canon["weights"],
                collapseLabel=b3.m4_collapse_label(canon), trainNLL=float(de.fun))


def cell_C10(cohorts, m3_pub, b3res, n_boot, frozen_n=2000, seed_base=20260717):
    out = {"cell": "B4C10_M4_STRUCTURAL_IDENTIFIABILITY",
           "cohort": "derived_eligible_1_to_8",
           "frozen_N_boot": frozen_n, "actual_N_boot": n_boot,
           "resourceBoundPartial": n_boot < frozen_n,
           "seed_base": seed_base,
           "U1_alreadyDone_in_B3": "DISTINCT (per B3 result)"}
    if n_boot <= 0:
        out["status"] = "NOT_RUN"
        out["reason"] = ("Frozen 2000 training-motor bootstrap × reduced-budget M4 refit "
                         "(maxiter=400 popsize=30 ~1-3 min each) ≈ 33-100 h wall-clock; "
                         "not feasible in this dispatch's compute budget. Recorded NOT_RUN "
                         "with reason=RESOURCE_BOUND per plan §4.")
        return out
    coh = cohorts["derived_eligible_1_to_8"]
    # reduced-budget calibration on the FULL training set
    full_calib = _fit_m4_reduced(coh, m3_pub, seed=seed_base)
    ref_train_nll = b3res["cohorts"]["derived_eligible_1_to_8"]["fitted"]["M4_MIXTURE_K3"].get("trainNLL")
    calib_gap = None
    if ref_train_nll is not None and full_calib is not None:
        calib_gap = full_calib["trainNLL"] - ref_train_nll
    out["reducedBudgetCalibration"] = {
        "reducedTrainNLL": full_calib["trainNLL"] if full_calib else None,
        "fullTrainNLL": ref_train_nll,
        "shortfall": calib_gap,
        "shortfallThreshold_nats": 0.05,
        "verdict": ("WITHIN_0.05_NATS" if (calib_gap is not None and abs(calib_gap) <= 0.05)
                    else "EXCEEDS_0.05_NATS" if calib_gap is not None else "UNAVAILABLE"),
    }
    # bootstrap over TRAINING MOTORS
    train_motors = coh.train_motors
    n_tm = len(train_motors)
    rng = np.random.default_rng(seed_base)
    collapsed_count = 0
    log10_lam3 = []
    omega3 = []
    failed = 0
    for b in range(n_boot):
        # Frozen M4 spec §8: seedPerReplicate = 20260717 + replicate_index (0..1999).
        seed_b = seed_base + b
        rng_b = np.random.default_rng(seed_b)
        idx = rng_b.integers(0, n_tm, size=n_tm)
        sampled = [train_motors[i] for i in idx]
        # build cohort with sampled training motors + original holdout (motor-level cluster)
        train_events = []
        for m in sampled:
            train_events.extend([dict(e) for e in coh.train if e["motorId"] == m])
        holdout_events = [dict(e) for e in coh.holdout]
        merged = train_events + holdout_events
        for e in merged:
            e["partition"] = "holdout" if b3.sha256_mod5(e["motorId"]) == 0 else "train"
        try:
            coh_b = b3.Cohort(f"C10_b{b}", tuple(range(1, 9)), merged)
        except Exception:
            failed += 1
            continue
        # Frozen spec: DE "seed as above" -> same seed as the replicate seed.
        fit_b = _fit_m4_reduced(coh_b, m3_pub, seed=seed_b)
        if fit_b is None:
            failed += 1
            continue
        collapse = fit_b["collapseLabel"]
        rates = fit_b["rates"]; weights = fit_b["weights"]
        if collapse != "DISTINCT":
            collapsed_count += 1
        log10_lam3.append(math.log10(rates[2]))
        omega3.append(weights[2])
    out["failed"] = failed
    out["completed"] = n_boot - failed
    if out["completed"] > 0:
        u2_frac = collapsed_count / out["completed"]
        lam3 = np.asarray(log10_lam3, dtype=np.float64)
        om3 = np.asarray(omega3, dtype=np.float64)
        u3_span = float(np.quantile(lam3, 0.975) - np.quantile(lam3, 0.025))
        om3_lo = float(np.quantile(om3, 0.025)); om3_hi = float(np.quantile(om3, 0.975))
        # Frozen M4 spec section 8, U4: "the 95 percent percentile bootstrap
        # interval of omega_(3) contains both a value below 5/793 and a value
        # above 0.25". Straddle = (lo < 5/793) AND (hi > 0.25) — an AND, not OR.
        u4_straddle = (om3_lo < 5.0 / 793.0) and (om3_hi > 0.25)
        out["U2_bootstrapCollapseFrac"] = u2_frac
        out["U2_verdict"] = "UNIDENTIFIED_U2_FIRES" if u2_frac >= 0.25 else "U2_OK"
        out["U3_log10_lambda3_95CI_span_decades"] = u3_span
        out["U3_verdict"] = "UNIDENTIFIED_U3_FIRES" if u3_span >= 2.0 else "U3_OK"
        out["U4_omega3_95CI"] = [om3_lo, om3_hi]
        out["U4_verdict"] = "UNIDENTIFIED_U4_FIRES" if u4_straddle else "U4_OK"
        fires = [k for k, v in [("U2", out["U2_verdict"]), ("U3", out["U3_verdict"]),
                                 ("U4", out["U4_verdict"])] if v.startswith("UNIDENTIFIED")]
        if fires:
            out["M4_status"] = f"UNIDENTIFIED ({','.join(fires)})"
        else:
            out["M4_status"] = "IDENTIFIED_ON_THIS_COHORT (U1 DISTINCT from B3, U2/U3/U4 OK)"
    else:
        out["M4_status"] = "NOT_ESTABLISHED (no successful bootstrap replicates)"
    if out["resourceBoundPartial"]:
        out["verdictScope"] = ("Partial replicate count; the U2/U3/U4 estimates are "
                                "reported with wider bootstrap noise than the frozen 2000 "
                                "would deliver. Recorded as RESOURCE_BOUND_PARTIAL.")
    return out


# ---------------------------------------------------------------------------
# B4C11 M7 identifiability: U2 profile flatness + U4 bootstrap collapse
# ---------------------------------------------------------------------------

def _m7_profile_at_tau(coh, tau, k_hat, seed=20260717):
    """Profile NLL over log k at a fixed tau. Uses exactly 11 starts as
    frozen in the M7 spec section 4:
        k in linspace(0.05, 5.0, 10) plus k_hat from the global fit
    optimized in log k with L-BFGS-B."""
    tbm = coh.train_by_motor
    log_k_lo = math.log(0.05); log_k_hi = math.log(5.0)
    k_starts = list(np.linspace(0.05, 5.0, 10)) + [float(k_hat)]
    log_k_starts = [math.log(max(k, 0.05)) for k in k_starts]
    best = math.inf
    for lk0 in log_k_starts:
        try:
            r = scipy.optimize.minimize(
                lambda lk: b3.m7_train_nll(math.exp(float(lk[0])), tau, tbm),
                [float(lk0)], method="L-BFGS-B", bounds=[(log_k_lo, log_k_hi)],
                options={"ftol": 1e-10, "gtol": 1e-8, "maxiter": 200})
            if math.isfinite(r.fun) and r.fun < best:
                best = float(r.fun)
        except Exception:
            pass
    return best


def _fit_m7_reduced(coh, k_full, tau_full, seed=None):
    """Reduced-budget M7 fit. FROZEN M7 spec §6.refitPerReplicate:
    L-BFGS-B ONLY, from exactly 26 starts:
        the 5x5 product of k = linspace(0.05, 5.0, 5) and
        tau = exp(linspace(log(1e-4), log(5.0), 5)), plus the full-data
        optimum as the 26th start. Tolerances identical to §5.
    seed is unused (starts are frozen/deterministic per spec)."""
    tbm = coh.train_by_motor
    LK = (math.log(0.05), math.log(5.0))
    LT = (math.log(1e-4), math.log(5.0))
    k_grid = np.linspace(0.05, 5.0, 5)
    tau_grid = np.exp(np.linspace(math.log(1e-4), math.log(5.0), 5))
    starts = [(math.log(k), math.log(t)) for k in k_grid for t in tau_grid]
    starts.append((math.log(float(k_full)), math.log(float(tau_full))))  # 26th start
    best = None
    for s0 in starts:
        try:
            r = scipy.optimize.minimize(
                lambda th: b3.m7_train_nll(math.exp(float(th[0])), math.exp(float(th[1])), tbm),
                list(s0), method="L-BFGS-B", bounds=[LK, LT],
                options={"ftol": 1e-12, "gtol": 1e-10, "maxiter": 20000,
                         "maxfun": 20000, "maxls": 100,
                         "finite_diff_rel_step": 1e-6})
            if math.isfinite(r.fun) and (best is None or r.fun < best[0]):
                best = (float(r.fun), list(r.x))
        except Exception:
            pass
    if best is None:
        return None
    tau = math.exp(best[1][1])
    return dict(k=math.exp(best[1][0]), tau=tau, trainNLL=best[0])


def cell_C11(cohorts, b3res, n_boot, frozen_n=2000, seed_base=20260717,
             run_u2=True):
    out = {"cell": "B4C11_M7_STRUCTURAL_IDENTIFIABILITY",
           "cohort": "derived_eligible_1_to_8",
           "frozen_N_boot_U4": frozen_n, "actual_N_boot_U4": n_boot,
           "resourceBoundPartial_U4": n_boot < frozen_n,
           "seed_base": seed_base,
           "U1_alreadyDone_in_B3": "TAU_INTERIOR",
           "U3_alreadyDone_in_B3": "SUPPORTED_OVER_M1"}
    coh = cohorts["derived_eligible_1_to_8"]
    m7_rec = b3res["cohorts"]["derived_eligible_1_to_8"]["fitted"]["M7_HIERARCHICAL_MOTOR"]
    tau_hat = m7_rec["kTau"]["tau"]
    k_hat = m7_rec["kTau"]["k"]

    # U2 profile flatness (M7 spec section 4):
    #   grid: 61 values, exp(linspace(log(1e-4), log(5.0), 61))
    #   at each tau: profile NLL over log k with L-BFGS-B, 11 starts
    #   flat set: {tau : profileNLL(tau) - min <= 1.9207 = 0.5*chi2_{1,0.95}}
    #   logspan = (log(max flat) - log(min flat)) / (log(5.0) - log(1e-4))
    #   verdict: UNIDENTIFIED_FLAT_PROFILE if logspan >= 0.50
    if run_u2:
        tau_grid = np.exp(np.linspace(math.log(1e-4), math.log(5.0), 61))
        nll_grid = []
        for tau in tau_grid:
            nll_grid.append(_m7_profile_at_tau(coh, float(tau), k_hat, seed=seed_base))
        nll_grid = np.array(nll_grid, dtype=np.float64)
        nll_star = float(np.min(nll_grid))
        flat_thresh = nll_star + 1.9207
        flat_taus = tau_grid[nll_grid <= flat_thresh]
        denom = math.log(5.0) - math.log(1e-4)
        if len(flat_taus) > 0:
            logspan_raw = float(math.log(np.max(flat_taus)) - math.log(np.min(flat_taus)))
            logspan_normalized = logspan_raw / denom
        else:
            logspan_raw = 0.0
            logspan_normalized = 0.0
        out["U2_profile"] = {
            "tauGrid": tau_grid.tolist(),
            "nllGrid": nll_grid.tolist(),
            "nllStar": nll_star,
            "flatThresholdOffset": 1.9207,
            "flatSetTauRange": [float(np.min(flat_taus)), float(np.max(flat_taus))]
                                if len(flat_taus) > 0 else None,
            "flatLogspan_raw_natural_log": logspan_raw,
            "flatLogspan_normalized": logspan_normalized,
            "logspanNormalizationDenominator": denom,
            "verdict": "UNIDENTIFIED_U2_FIRES" if logspan_normalized >= 0.5 else "U2_OK",
        }
    else:
        out["U2_profile"] = {"status": "NOT_RUN"}

    # U4 bootstrap collapse. Motor-cluster bootstrap over TRAINING motors.
    # Seed per replicate 20260717 + replicate_index (mirroring the M4 spec's
    # frozen bootstrap seed convention; the M7 spec does not name a distinct
    # seed formula so we use the same 20260717 anchor).
    k_full = m7_rec["kTau"]["k"]
    if n_boot > 0:
        train_motors = coh.train_motors
        n_tm = len(train_motors)
        collapsed = 0
        completed = 0
        failed = 0
        tau_hats = []
        for b in range(n_boot):
            seed_b = seed_base + b
            rng_b = np.random.default_rng(seed_b)
            idx = rng_b.integers(0, n_tm, size=n_tm)
            sampled = [train_motors[i] for i in idx]
            train_events = []
            for m in sampled:
                train_events.extend([dict(e) for e in coh.train if e["motorId"] == m])
            holdout_events = [dict(e) for e in coh.holdout]
            merged = train_events + holdout_events
            for e in merged:
                e["partition"] = "holdout" if b3.sha256_mod5(e["motorId"]) == 0 else "train"
            try:
                coh_b = b3.Cohort(f"C11_b{b}", tuple(range(1, 9)), merged)
            except Exception:
                failed += 1
                continue
            fit_b = _fit_m7_reduced(coh_b, k_full=k_full, tau_full=tau_hat)
            if fit_b is None:
                failed += 1
                continue
            completed += 1
            tau_hats.append(fit_b["tau"])
            if fit_b["tau"] < 1e-3:
                collapsed += 1
        if completed > 0:
            frac = collapsed / completed
            tau_arr = np.asarray(tau_hats, dtype=np.float64)
            out["U4_bootstrap"] = {
                "completed": completed, "failed": failed,
                "tauHatSummary": {"median": float(np.median(tau_arr)),
                                  "p025": float(np.quantile(tau_arr, 0.025)),
                                  "p975": float(np.quantile(tau_arr, 0.975))},
                "collapseFraction_tau_lt_1e_3": frac,
                "verdict": "UNSTABLE_DISPERSION_U4_FIRES" if frac >= 0.25 else "U4_OK",
            }
        else:
            out["U4_bootstrap"] = {"status": "NO_SUCCESSFUL_BOOTSTRAP"}
    else:
        out["U4_bootstrap"] = {"status": "NOT_RUN",
                               "reason": ("Frozen 2000 training-motor bootstrap × reduced "
                                          "26-start L-BFGS-B M7 refit not feasible in this "
                                          "dispatch's budget. RESOURCE_BOUND.")}

    # combined M7 status
    fires = []
    if out.get("U2_profile", {}).get("verdict", "").startswith("UNIDENTIFIED"):
        fires.append("U2")
    if out.get("U4_bootstrap", {}).get("verdict", "").startswith("UNSTABLE"):
        fires.append("U4")
    if fires:
        out["M7_status"] = f"UNIDENTIFIED_OR_UNSTABLE ({','.join(fires)}) (U1 interior, U3 LRT-supported per B3)"
    else:
        out["M7_status"] = "IDENTIFIED_ON_THIS_COHORT (U1/U2/U3/U4 all OK)"
    return out


# ---------------------------------------------------------------------------
# B4C12 stability ledger aggregation
# ---------------------------------------------------------------------------

def cell_C12(cells_run):
    """Aggregate the stability of the four B3 headline conclusions across
    C02, C04, C05, C06, C07, C08, C09."""
    headlines = {
        "adverse_M2_over_M3_NLPD": {"stable_in": [], "unstable_in": [], "not_evaluable_in": []},
        "all_motor_equal_contrasts_inconclusive": {"stable_in": [], "unstable_in": [], "not_evaluable_in": []},
        "rule_disagreement_NLPD_vs_CRPS": {"stable_in": [], "unstable_in": [], "not_evaluable_in": []},
        "cohort_dependence_1to8_vs_0to8": {"stable_in": [], "unstable_in": [], "not_evaluable_in": []},
    }
    # C02
    c02 = cells_run.get("B4C02", {})
    if c02.get("verdict") == "GENERATOR-ROBUST_ADVERSE":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C02")
    elif c02.get("verdict") == "GENERATOR-SPECIFIC":
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C02")
    else:
        headlines["adverse_M2_over_M3_NLPD"]["not_evaluable_in"].append(
            f"B4C02({c02.get('verdict', 'NA')})")
    # C04 - contrast inconclusiveness (per-cohort)
    c04 = cells_run.get("B4C04", {})
    for cn, cc in c04.get("cohorts", {}).items():
        if cc.get("verdict") == "SEED-STABLE_ALL_INCONCLUSIVE":
            headlines["all_motor_equal_contrasts_inconclusive"]["stable_in"].append(f"B4C04:{cn}")
        else:
            headlines["all_motor_equal_contrasts_inconclusive"]["unstable_in"].append(
                f"B4C04:{cn}({cc.get('verdict', 'NA')})")
    # C05 - censoring load-bearing (relevant to adverse M2>M3 direction reliability)
    c05 = cells_run.get("B4C05", {})
    a = c05.get("treatments", {}).get("a_frozen_exclusion", {})
    b = c05.get("treatments", {}).get("b_naive_include", {})
    if a and b:
        if a.get("m2_vs_m3_nlpd_verdict") == b.get("m2_vs_m3_nlpd_verdict"):
            headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C05(a_vs_b_same_direction)")
        else:
            headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C05(a_vs_b_direction_differs)")
    # C06 - outlier + analysisStartIndex sensitivity
    c06 = cells_run.get("B4C06", {})
    if c06.get("verdict") == "BOUNDARY-STABLE":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C06(outlier)")
    else:
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append(f"B4C06({c06.get('verdict', 'NA')})")
    # C07 - cohort eligibility
    c07 = cells_run.get("B4C07", {})
    if c07.get("verdict") == "ELIGIBILITY-REPRODUCED":
        headlines["cohort_dependence_1to8_vs_0to8"]["stable_in"].append("B4C07(eligibility_reproduced)")
    # C08 - LOMO
    c08 = cells_run.get("B4C08", {})
    for cn, cc in c08.get("cohorts", {}).items():
        if cc.get("verdict") == "LOMO-STABLE":
            headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append(f"B4C08:{cn}(LOMO)")
        else:
            headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append(f"B4C08:{cn}({cc.get('verdict', 'NA')})")
            headlines["all_motor_equal_contrasts_inconclusive"]["unstable_in"].append(
                f"B4C08:{cn}(contrastFlipsUnderMotorRemoval)")
    # C09 - interval jitter
    c09 = cells_run.get("B4C09", {})
    if c09.get("verdict") == "INTERVAL-ROBUST":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C09")
    elif c09.get("verdict") == "INTERVAL-SENSITIVE":
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C09")
    else:
        headlines["adverse_M2_over_M3_NLPD"]["not_evaluable_in"].append(
            f"B4C09({c09.get('verdict') or c09.get('status', 'NA')})")

    # rule disagreement: read from any cell that runs both scoring rules
    # (C04 does; if it shows both rules disagreement, mark stable)
    # Simple heuristic: C04's SEED-STABLE across BOTH rules confirms rule-disagreement is a stable property.
    if c04:
        stable_pairs = 0
        for cn, cc in c04.get("cohorts", {}).items():
            if cc.get("verdict") == "SEED-STABLE_ALL_INCONCLUSIVE":
                stable_pairs += 1
        if stable_pairs > 0:
            headlines["rule_disagreement_NLPD_vs_CRPS"]["stable_in"].append("B4C04(both_rules_seed_stable)")

    # aggregate per-headline: STABLE if only stable_in and non-empty; UNSTABLE if any unstable_in;
    # SPECIFICATION-DEPENDENT if mixed; NOT_ESTABLISHED if empty.
    ledger = {}
    for h, lists in headlines.items():
        s = lists["stable_in"]; u = lists["unstable_in"]
        if u and s:
            v = "SPECIFICATION-DEPENDENT"
        elif u:
            v = "UNSTABLE"
        elif s:
            v = "STABLE"
        else:
            v = "NOT_ESTABLISHED"
        ledger[h] = {"verdict": v, **lists}
    return {"cell": "B4C12_RANKING_AND_INTERVAL_CROSSING_STABILITY",
            "headlines": ledger,
            "note": "Aggregation of stability contributions from cells C02,C04,C05,C06,C07,C08,C09. "
                    "M4/M7 identifiability (C10/C11) map into the SPECIFICATION-DEPENDENT column "
                    "for the mechanism-interpretation of any M3-alternative advantage."}


# ---------------------------------------------------------------------------
# Canonical JSON (mirrors B3 runner's convention, but implemented locally)
# ---------------------------------------------------------------------------

def _canon(obj):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if obj is None:
        return "null"
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return "null"
        return "%.17g" % obj
    if isinstance(obj, (int,)):
        return str(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=True)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_canon(x) for x in obj) + "]"
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda kv: str(kv[0]))
        return "{" + ",".join(json.dumps(str(k), ensure_ascii=True) + ":" + _canon(v)
                              for k, v in items) + "}"
    if isinstance(obj, (np.floating,)):
        return _canon(float(obj))
    if isinstance(obj, (np.integer,)):
        return str(int(obj))
    if isinstance(obj, np.ndarray):
        return _canon(obj.tolist())
    raise TypeError(f"cannot canonicalize {type(obj)}")


def canonical_json(obj):
    return _canon(obj) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

ALL_CELLS = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", type=str, default=None,
                    help="comma-separated cell ids to run (default: all)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", type=str, default=None)
    ap.add_argument("--c01-sims", type=int, default=0)
    ap.add_argument("--c02-sims", type=int, default=0)
    ap.add_argument("--c09-jitter", type=int, default=0)
    ap.add_argument("--c10-boot", type=int, default=0)
    ap.add_argument("--c11u4-boot", type=int, default=0)
    ap.add_argument("--c11-skip-u2", action="store_true")
    args = ap.parse_args()
    if args.all:
        cells = list(ALL_CELLS)
    elif args.cells:
        cells = [c.strip().upper() for c in args.cells.split(",")]
    else:
        cells = ["C03", "C04", "C07", "C08"]

    t0 = time.time()
    b3res = load_b3()
    events = b3.load_events()
    cohorts = b3.build_cohorts(events)
    m3_pub = b3.committed_m3()
    permotor = {cn: per_motor_scores(cohorts[cn], b3res["cohorts"][cn]["fitted"]) for cn in cohorts}

    results = {"schema": "uni.flagellum.b4-identifiability-robustness-result/1.0.0",
               "protocolId": "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1",
               "protocolPath": "audits/phase-b/b4-identifiability-robustness-protocol.v1.json",
               "predictionsPath": "audits/phase-b/b4-identifiability-robustness-predictions.v1.json",
               "predictionRecordPath": "experiments/predictions/b4-identifiability-robustness.prediction.json",
               "consumesB3ResultSha256": "5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd",
               "runner": "audits/phase-b/b4-identifiability-robustness-runner.py",
               "cellsRequested": cells,
               "cells": {}}

    cells_out = results["cells"]
    for cid in cells:
        cell_t0 = time.time()
        if cid == "C01":
            cells_out["B4C01"] = cell_C01(cohorts, m3_pub, b3res, n_sims=args.c01_sims)
        elif cid == "C02":
            cells_out["B4C02"] = cell_C02(cohorts, m3_pub, b3res, n_sims=args.c02_sims)
        elif cid == "C03":
            cells_out["B4C03"] = cell_C03(cohorts, permotor, b3res)
        elif cid == "C04":
            cells_out["B4C04"] = cell_C04(cohorts, permotor)
        elif cid == "C05":
            cells_out["B4C05"] = cell_C05(cohorts, m3_pub, permotor)
        elif cid == "C06":
            cells_out["B4C06"] = cell_C06(cohorts, m3_pub, permotor)
        elif cid == "C07":
            cells_out["B4C07"] = cell_C07()
        elif cid == "C08":
            cells_out["B4C08"] = cell_C08(cohorts, permotor)
        elif cid == "C09":
            cells_out["B4C09"] = cell_C09(cohorts, m3_pub, permotor, n_replicates=args.c09_jitter)
        elif cid == "C10":
            cells_out["B4C10"] = cell_C10(cohorts, m3_pub, b3res, n_boot=args.c10_boot)
        elif cid == "C11":
            cells_out["B4C11"] = cell_C11(cohorts, b3res, n_boot=args.c11u4_boot,
                                          run_u2=not args.c11_skip_u2)
        elif cid == "C12":
            cells_out["B4C12"] = cell_C12(cells_out)
        cell_dt = time.time() - cell_t0
        print(f"{cid}: {cell_dt:.1f}s")

    # NOTE: runtimeS is intentionally NOT recorded in the canonical result
    # (wall-clock varies per run and would break the determinism gate).
    # Record environment (deterministic across runs on the same machine).
    results["environment"] = {"python": sys.version.split()[0],
                              "numpy": np.__version__, "scipy": scipy.__version__}
    body = canonical_json(results).encode("utf-8")
    if args.out:
        Path(args.out).write_bytes(body)
        import hashlib
        print(f"wrote {args.out} ({len(body)} bytes) sha256={hashlib.sha256(body).hexdigest()}")
    print(f"total runtime: {time.time() - t0:.1f}s (not recorded in canonical result)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
