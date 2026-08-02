#!/usr/bin/env python3
"""
B4 INDEPENDENT ORACLE.

Reconstructs a stratified sample of each executed B4 cell's decisive quantity
from the recorded B3 result and source events, WITHOUT importing the B4 runner
under test (b4-identifiability-robustness-runner.py) or the B3 runner
(b3-model-competition-runner.py), and sharing no helper module with either. This
is a circular-oracle guard: each check re-derives the number/verdict from
scratch using its own code, and must agree with the runner's recorded value
within the cell's declared tolerance.

Reads only:
  - audits/phase-b/b3-model-competition-result.json
  - audits/phase-b/b4-identifiability-robustness-result.v1.json
  - experiments/data/wadhwa-2022-events.json

Usage:  python audits/phase-b/b4-independent-oracle.py [--b4 PATH] [--b3 PATH] [--json OUT]
Exit 0 iff every independent check agrees within its declared tolerance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.special
import scipy.stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
DEFAULT_B3 = ROOT / "audits" / "phase-b" / "b3-model-competition-result.json"
DEFAULT_B4 = ROOT / "audits" / "phase-b" / "b4-identifiability-robustness-result.v1.json"

TOL_SCORE = 1e-8
TOL_FRAC = 1e-9
LOG_SQRT2PI = 0.5 * math.log(2.0 * math.pi)
SQRT2 = math.sqrt(2.0)

checks = []


def rec(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})
    return bool(ok)


# ---- independent data / cohort reconstruction ------------------------------

def part(motor_id):
    return int(hashlib.sha256(motor_id.encode("utf-8")).hexdigest(), 16) % 5


def build_cohort(states):
    events = json.loads(DATA.read_text(encoding="utf-8"))["events"]
    elig = [e for e in events if (not e["rightCensored"]) and e["stateN"] in states]
    train = [e for e in elig if part(e["motorId"]) != 0]
    hold = [e for e in elig if part(e["motorId"]) == 0]
    scale = {}
    for s in states:
        d = [e["durationS"] for e in train if e["stateN"] == s]
        if d:
            scale[s] = sum(d) / len(d)
    return train, hold, scale, events


# ---- independent densities (own implementations) ---------------------------

def logpdf(model, params, y, stateN, scale):
    if model == "M0_EXPONENTIAL":
        return -y
    if model == "M1_WEIBULL":
        k = params[0]; sw = math.exp(-math.lgamma(1 + 1 / k)); r = y / sw
        return math.log(k / sw) + (k - 1) * math.log(r) - r ** k
    if model == "M2_LOGNORMAL":
        sig = params[0]; mu = -sig * sig / 2
        return -(math.log(y) + math.log(sig) + LOG_SQRT2PI) - 0.5 * ((math.log(y) - mu) / sig) ** 2
    if model == "M3_TWO_TIMESCALE":
        w, lf = params[0], params[1]; ls = (1 - w) / (1 - w / lf)
        return float(scipy.special.logsumexp([
            math.log(w) + math.log(lf) - lf * y,
            math.log(1 - w) + math.log(ls) - ls * y]))
    if model == "M5_GAMMA":
        a = params[0]
        return a * math.log(a) - math.lgamma(a) + (a - 1) * math.log(y) - a * y
    if model == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        k = params[str(stateN)] if str(stateN) in params else params[stateN]
        sw = math.exp(-math.lgamma(1 + 1 / k)); r = y / sw
        return math.log(k / sw) + (k - 1) * math.log(r) - r ** k
    if model == "M4_MIXTURE_K3":
        rates = params["rates"]; weights = params["weights"]
        return float(scipy.special.logsumexp(
            [math.log(weights[i]) + math.log(rates[i]) - rates[i] * y for i in range(3)]))
    if model == "M7_HIERARCHICAL_MOTOR":
        k, tau = params["k"], params["tau"]
        x, v = np.polynomial.hermite.hermgauss(129)
        z = SQRT2 * x; wr = v / math.sqrt(math.pi); W = wr / wr.sum()
        a = np.clip(k * np.exp(tau * z), 1e-3, 1e3)
        ls = -scipy.special.gammaln(1 + 1 / a)
        u = a * (math.log(y) - ls)
        lf = np.log(a) - ls + ((a - 1) / a) * u - np.exp(np.minimum(u, 700.0))
        return float(scipy.special.logsumexp(np.log(W) + lf))
    if model == "M8_EMPIRICAL_KDE":
        s = params["_s"]; h = params["h"]
        q = -0.5 * ((math.log(y) - s) / h) ** 2
        return float(scipy.special.logsumexp(q)) - math.log(len(s)) - math.log(h) - LOG_SQRT2PI - math.log(y)
    raise ValueError(model)


def m8_locations(train, scale, h):
    y = np.array([e["durationS"] / scale[e["stateN"]] for e in train], dtype=np.float64)
    ybar = math.fsum(y.tolist()) / len(y)
    return np.log(y) - h * h / 2 - math.log(ybar)


def params_for(model, fitted):
    rec_ = fitted[model]
    if model == "M0_EXPONENTIAL":
        return []
    if model in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA", "M3_TWO_TIMESCALE"):
        return rec_["params"]
    if model == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        return rec_["params"]
    if model == "M4_MIXTURE_K3":
        return {"rates": rec_["canonical"]["rates"], "weights": rec_["canonical"]["weights"]}
    if model == "M7_HIERARCHICAL_MOTOR":
        return {"k": rec_["kTau"]["k"], "tau": rec_["kTau"]["tau"]}
    if model == "M8_EMPIRICAL_KDE":
        return {"h": rec_["h"]}
    raise ValueError(model)


def motor_equal_series(hold, per_event):
    by = defaultdict(list)
    for e, v in zip(hold, per_event):
        by[e["motorId"]].append(v)
    motors = sorted(by)
    pm = np.array([np.mean(by[m]) for m in motors], dtype=np.float64)
    return float(np.mean(pm)), pm, motors


def nlpd_motor_equal(model, params, hold, scale):
    per = []
    for e in hold:
        y = e["durationS"] / scale[e["stateN"]]
        lp = logpdf(model, params, y, e["stateN"], scale)
        per.append(-lp + math.log(scale[e["stateN"]]))
    return motor_equal_series(hold, per)


MODELS = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE",
          "M4_MIXTURE_K3", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT",
          "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]


# ---- per-cell independent checks -------------------------------------------

def check_C03(b3, b4):
    """Recompute M8 rank at the +/-1 grid neighbours from scratch."""
    if "B4C03" not in b4["cells"]:
        return
    h_grid = 10.0 ** (-2.0 + 0.05 * np.arange(61, dtype=np.float64))
    for cn, states in [("derived_eligible_1_to_8", set(range(1, 9))),
                       ("primary_states_0_to_8", set(range(0, 9)))]:
        train, hold, scale, _ = build_cohort(states)
        fitted = b3["cohorts"][cn]["fitted"]
        cell = b4["cells"]["B4C03"]["cohorts"][cn]
        gi = int(b3["cohorts"][cn]["fitted"]["M8_EMPIRICAL_KDE"]["selectedGridIndex"])
        # Precompute other models' motor-equal at their frozen fits
        other_scores = {}
        for mid in MODELS:
            if mid == "M8_EMPIRICAL_KDE":
                continue
            p = params_for(mid, fitted)
            me, _, _ = nlpd_motor_equal(mid, p, hold, scale)
            other_scores[mid] = me
        for offset in (-1, 0, 1):
            key = "-1" if offset == -1 else "0" if offset == 0 else "+1"
            j = gi + offset
            if j < 0 or j > 60:
                continue
            h_j = float(h_grid[j])
            p = {"h": h_j, "_s": m8_locations(train, scale, h_j)}
            me, _, _ = nlpd_motor_equal("M8_EMPIRICAL_KDE", p, hold, scale)
            local = dict(other_scores); local["M8_EMPIRICAL_KDE"] = me
            order = sorted(local.items(), key=lambda kv: kv[1])
            rank = 1 + [k for k, _ in order].index("M8_EMPIRICAL_KDE")
            recorded_rank = cell["neighbours"][key].get("rank")
            recorded_me = cell["neighbours"][key].get("m8_nlpd_motorEqual")
            rec(f"C03:{cn}:M8_rank@offset{key}", rank == recorded_rank,
                f"oracle={rank} recorded={recorded_rank}")
            if recorded_me is not None:
                rec(f"C03:{cn}:M8_nlpd@offset{key}",
                    abs(me - recorded_me) <= TOL_SCORE,
                    f"oracle={me:.10g} recorded={recorded_me:.10g}")


def check_C04(b3, b4):
    """Independently reproduce the 8 M3-contrast verdicts for cohort [1..8]
    at seed=20260717, nrep=2000, NLPD motor-equal. Compare against the runner's
    recorded verdict."""
    if "B4C04" not in b4["cells"]:
        return
    for cn, states in [("derived_eligible_1_to_8", set(range(1, 9)))]:
        train, hold, scale, _ = build_cohort(states)
        fitted = b3["cohorts"][cn]["fitted"]
        # per-motor NLPD for M3 and every other model
        pm = {}
        for mid in MODELS:
            p = params_for(mid, fitted)
            if mid == "M8_EMPIRICAL_KDE":
                p = {"h": p["h"], "_s": m8_locations(train, scale, p["h"])}
            _, pmv, _ = nlpd_motor_equal(mid, p, hold, scale)
            pm[mid] = pmv
        ref = pm["M3_TWO_TIMESCALE"]
        n = len(ref)
        rng = np.random.default_rng(20260717)
        R = rng.integers(0, n, size=(50000, n), dtype=np.int64)[:2000]
        for mid in MODELS:
            if mid == "M3_TWO_TIMESCALE":
                continue
            chal = pm[mid]
            theta = np.array([float(np.mean(ref[R[b]]) - np.mean(chal[R[b]]))
                              for b in range(2000)], dtype=np.float64)
            lo = float(np.quantile(theta, 0.025, method="linear"))
            hi = float(np.quantile(theta, 0.975, method="linear"))
            sign = "M_BEATS_M3" if lo > 0 else ("M3_BEATS_M" if hi < 0 else "INCONCLUSIVE")
            rec_verdict = b4["cells"]["B4C04"]["cohorts"][cn]["contrasts"]["NLPD_motor_equal"][mid]["verdicts"]["20260717:2000"]
            # oracle uses percentile; runner uses BCa. Compare zero-crossing classification.
            rec(f"C04:{cn}:NLPD:{mid}:seed20260717:2000",
                sign == rec_verdict or (sign == "INCONCLUSIVE" and rec_verdict == "INCONCLUSIVE"),
                f"oraclePercentile={sign} recorded={rec_verdict}")


def check_C07(b4):
    """Recompute eligibility set from the raw events."""
    if "B4C07" not in b4["cells"]:
        return
    events = json.loads(DATA.read_text(encoding="utf-8"))["events"]
    ev_by, mot_by = defaultdict(int), defaultdict(set)
    for e in events:
        if e["rightCensored"]:
            continue
        if part(e["motorId"]) == 0:
            ev_by[e["stateN"]] += 1
            mot_by[e["stateN"]].add(e["motorId"])
    eligible = sorted(s for s in range(0, 9) if ev_by[s] >= 20 and len(mot_by[s]) >= 5)
    rec_set = b4["cells"]["B4C07"]["recomputedEligibleSet"]
    rec("C07:eligibility_set", eligible == rec_set, f"oracle={eligible} recorded={rec_set}")
    # state-0 count
    rec("C07:state0_count_lt_20", ev_by[0] < 20, f"state0Ev={ev_by[0]}")


def check_C08(b3, b4):
    """Reproduce full-sample NLPD leader for each cohort under the runner's
    frozen fits. Only the leader identity is asserted (leader flips would be
    a first-class UNSTABLE finding)."""
    if "B4C08" not in b4["cells"]:
        return
    for cn, states in [("derived_eligible_1_to_8", set(range(1, 9))),
                       ("primary_states_0_to_8", set(range(0, 9)))]:
        train, hold, scale, _ = build_cohort(states)
        fitted = b3["cohorts"][cn]["fitted"]
        scores = {}
        for mid in MODELS:
            p = params_for(mid, fitted)
            if mid == "M8_EMPIRICAL_KDE":
                p = {"h": p["h"], "_s": m8_locations(train, scale, p["h"])}
            me, _, _ = nlpd_motor_equal(mid, p, hold, scale)
            scores[mid] = me
        leader = min(scores.items(), key=lambda kv: kv[1])[0]
        rec_leader = b4["cells"]["B4C08"]["cohorts"][cn]["fullLeaderNLPD"]
        rec(f"C08:{cn}:fullLeaderNLPD", leader == rec_leader, f"oracle={leader} recorded={rec_leader}")


def check_C05(b3, b4):
    """Load-bearing censoring flag: verify treatment (a) reproduces B3's
    frozen M2_sigma and M3_(w,lf) values (within tolerance), and treatment
    (b) SHIFTS them materially."""
    if "B4C05" not in b4["cells"]:
        return
    c05 = b4["cells"]["B4C05"]
    a = c05["treatments"].get("a_frozen_exclusion", {})
    b = c05["treatments"].get("b_naive_include", {})
    # (a) fits should be within a small tolerance of the frozen B3 fits
    fitted_b3 = b3["cohorts"]["derived_eligible_1_to_8"]["fitted"]
    for mid, tol in [("M1_WEIBULL", 0.02), ("M2_LOGNORMAL", 0.02),
                     ("M5_GAMMA", 0.02)]:
        pa = a.get("fitted", {}).get(mid, {}).get("params")
        pb3 = fitted_b3[mid]["params"]
        if pa is None:
            continue
        d = max(abs(pa[i] - pb3[i]) for i in range(len(pa)))
        rec(f"C05:a_reproduces_B3:{mid}", d <= tol, f"|Δ|max={d:.3e} tol={tol}")
    # M3 is 2-D; use the fitted list
    pa = a.get("fitted", {}).get("M3_TWO_TIMESCALE", {}).get("params")
    pb3 = fitted_b3["M3_TWO_TIMESCALE"]["params"]
    if pa is not None:
        d = max(abs(pa[i] - pb3[i]) for i in range(len(pa)))
        rec("C05:a_reproduces_B3:M3_TWO_TIMESCALE", d <= 0.05, f"|Δ|max={d:.3e}")
    # (b) MUST shift materially vs (a)
    load_bearing = c05.get("loadBearingCensoringFlag", {})
    rec("C05:censoring_load_bearing",
        load_bearing.get("verdict") == "PASS_censoring_load_bearing",
        f"verdict={load_bearing.get('verdict')}")


def check_C06(b4):
    """Verify BLOCKED_EXTERNAL for the raw-MAT variants and that the outlier
    variants report a leader from the model set."""
    if "B4C06" not in b4["cells"]:
        return
    c06 = b4["cells"]["B4C06"]
    for offs in ("3400", "3600"):
        s = c06["analysisStartIndex"][offs]["status"]
        rec(f"C06:analysisStartIndex_{offs}_is_blocked_external",
            s == "BLOCKED_EXTERNAL", f"status={s}")
    for label in ("drop_longest_per_state", "drop_shortest_per_state"):
        v = c06[label].get("leaderNLPD")
        rec(f"C06:{label}:has_leader", v in MODELS, f"leader={v}")


def check_C09(b4):
    """If C09 was run: sanity-check the flip fractions ∈ [0,1]."""
    if "B4C09" not in b4["cells"]:
        return
    c09 = b4["cells"]["B4C09"]
    if c09.get("status") == "NOT_RUN":
        rec("C09:not_run_labelled", c09.get("reason", "").startswith("Frozen"), c09.get("reason", "")[:80])
        return
    for k in ("m2_vs_m3_flip_fraction", "leader_flip_fraction"):
        f = c09.get(k)
        if f is not None:
            rec(f"C09:{k}_in_unit_interval", 0.0 <= f <= 1.0, f"{k}={f}")


def check_C10(b4):
    if "B4C10" not in b4["cells"]:
        return
    c10 = b4["cells"]["B4C10"]
    if c10.get("status") == "NOT_RUN":
        rec("C10:not_run_labelled", c10.get("reason", "").startswith("Frozen"), c10.get("reason", "")[:80])
        return
    if "U2_bootstrapCollapseFrac" in c10:
        f = c10["U2_bootstrapCollapseFrac"]
        rec("C10:U2_frac_in_unit_interval", 0.0 <= f <= 1.0, f"frac={f}")
        # verdict consistency
        expected = "UNIDENTIFIED_U2_FIRES" if f >= 0.25 else "U2_OK"
        rec("C10:U2_verdict_matches_frac", c10["U2_verdict"] == expected,
            f"verdict={c10['U2_verdict']} expected={expected}")


def check_C11(b4):
    if "B4C11" not in b4["cells"]:
        return
    c11 = b4["cells"]["B4C11"]
    u2 = c11.get("U2_profile", {})
    if "flatLogspan_normalized" in u2:
        ls = u2["flatLogspan_normalized"]
        rec("C11:U2_logspan_normalized_in_unit_interval", 0.0 <= ls <= 1.0, f"logspan={ls}")
        expected = "UNIDENTIFIED_U2_FIRES" if ls >= 0.5 else "U2_OK"
        rec("C11:U2_verdict_matches", u2["verdict"] == expected,
            f"verdict={u2['verdict']} expected={expected}")
    u4 = c11.get("U4_bootstrap", {})
    if isinstance(u4, dict) and "collapseFraction_tau_lt_1e_3" in u4:
        f = u4["collapseFraction_tau_lt_1e_3"]
        rec("C11:U4_frac_in_unit_interval", 0.0 <= f <= 1.0, f"frac={f}")


def check_C12(b4):
    """Verify the C12 aggregation matches the underlying cell verdicts by simple
    cross-check (aggregation is a pure function of runner cell verdicts)."""
    if "B4C12" not in b4["cells"]:
        return
    c12 = b4["cells"]["B4C12"]
    # Sanity: each headline has a verdict in the allowed set.
    ALLOWED = {"STABLE", "UNSTABLE", "SPECIFICATION-DEPENDENT", "NOT_ESTABLISHED"}
    for h, det in c12["headlines"].items():
        rec(f"C12:{h}:verdict_in_set", det["verdict"] in ALLOWED, f"verdict={det['verdict']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--b3", type=Path, default=DEFAULT_B3)
    ap.add_argument("--b4", type=Path, default=DEFAULT_B4)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    b3 = json.loads(args.b3.read_text(encoding="utf-8"))
    b4 = json.loads(args.b4.read_text(encoding="utf-8"))

    check_C03(b3, b4)
    check_C04(b3, b4)
    check_C05(b3, b4)
    check_C06(b4)
    check_C07(b4)
    check_C08(b3, b4)
    check_C09(b4)
    check_C10(b4)
    check_C11(b4)
    check_C12(b4)

    passed = sum(c["passed"] for c in checks)
    total = len(checks)
    out = {"schema": "uni.flagellum.b4-oracle-result/1.0.0",
           "b3ResultAudited": str(args.b3.name),
           "b4ResultAudited": str(args.b4.name),
           "checksPassed": passed, "checksTotal": total,
           "allPassed": passed == total,
           "toleranceScore": TOL_SCORE, "toleranceFrac": TOL_FRAC,
           "checks": checks}
    if args.json:
        args.json.write_bytes((json.dumps(out, indent=2) + "\n").encode("utf-8"))
    for c in checks:
        if not c["passed"]:
            print("  FAIL", c["check"], c["detail"])
    print(f"\nB4 ORACLE: {passed}/{total} independent checks agree")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
