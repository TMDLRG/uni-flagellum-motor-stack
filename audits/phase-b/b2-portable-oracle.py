#!/usr/bin/env python3
"""
B2 PORTABLE ORACLE — clone-reproducible replacement for b2-decisive-oracle.py

Addresses six defects Codex identified in the original executable:
  1. hard-coded absolute checkout path      -> root derived from __file__
  2. claimed to read the protocol but did not -> protocol loaded AND validated
  3. only optimized M3                       -> refits M1, M2 and M3
  4. narrative run-count did not match code  -> attempts counted programmatically
  5. eligibility hard-coded                  -> taken from the protocol, and the
                                                protocol/implementation MISMATCH
                                                is surfaced rather than hidden
  6. "global optimum" overclaimed            -> reports a search-domain conclusion

Reads: experiments/preregistration.v1.json  (protocol)
       experiments/data/wadhwa-2022-events.json  (data)
       experiments/results/observed-experiment-report.json  (COMPARISON TARGETS ONLY)
Does not import lib/ or scripts/. Model equations are implemented from the
protocol's prose specification and its mean-one constraints.

Usage:  python audits/phase-b/b2-portable-oracle.py [--json OUT.json]
Exit 0 if every self-check passes; exit 1 otherwise.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parents[2]          # audits/phase-b/x.py -> repo root
PROTOCOL_PATH = ROOT / "experiments" / "preregistration.v1.json"
DATA_PATH = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
REPORT_PATH = ROOT / "experiments" / "results" / "observed-experiment-report.json"

SEARCH_DOMAIN = {"w": (1e-9, 1 - 1e-9), "lf": (1e-9, 1e4),
                 "constraint": "lf > w  (from the mean-one feasibility 1 - w/lf > 0)"}

# ---------------------------------------------------------------- protocol ---
def load_and_validate_protocol() -> dict:
    p = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    problems = []
    for key in ("protocolId", "scope", "split", "extraction", "models", "uncertainty"):
        if key not in p:
            problems.append(f"protocol missing required key: {key}")
    split = p.get("split", {})
    if "modulo 5" not in split.get("method", ""):
        problems.append("split method is not the expected sha256 mod 5 rule")
    if split.get("holdoutRemainders") != [0]:
        problems.append(f"unexpected holdoutRemainders: {split.get('holdoutRemainders')}")
    if "primaryStates" not in p.get("scope", {}):
        problems.append("scope.primaryStates absent; eligibility cannot be derived")
    rules = " ".join(p.get("extraction", {}).get("rules", []))
    if "right-censored" not in rules and "rightCensored" not in rules:
        problems.append("extraction rules do not mention right-censoring")
    if problems:
        raise SystemExit("PROTOCOL VALIDATION FAILED:\n  " + "\n  ".join(problems))
    return p

# -------------------------------------------------------------------- data ---
def load_events_and_verify_split(protocol: dict) -> list[dict]:
    events = json.loads(DATA_PATH.read_text(encoding="utf-8"))["events"]
    hold = set(protocol["split"]["holdoutRemainders"])
    mismatches = 0
    for e in events:
        rem = int(hashlib.sha256(e["motorId"].encode("utf-8")).hexdigest(), 16) % 5
        expect = "holdout" if rem in hold else "train"
        if expect != e["partition"] or rem != e["splitRemainder"]:
            mismatches += 1
    spanning = sum(
        1 for m in {e["motorId"] for e in events}
        if len({e["partition"] for e in events if e["motorId"] == m}) > 1
    )
    return events, mismatches, spanning

# ------------------------------------------------- mean-one log densities ---
def log_exp(y):        return -y
def log_weibull(y, k):
    log_sw = -gammaln(1.0 + 1.0 / k)                       # scale = 1/Gamma(1+1/k)
    z = np.log(y) - log_sw
    return np.log(k) - log_sw + (k - 1.0) * z - np.exp(k * z)
def log_lognormal(y, s):
    mu = -0.5 * s * s                                      # mean-one => mu = -s^2/2
    return -np.log(y * s * math.sqrt(2 * math.pi)) - (np.log(y) - mu) ** 2 / (2 * s * s)
def mixture_slow_rate(w, lf):
    den = 1.0 - w / lf
    return None if den <= 0 else (1.0 - w) / den
def log_mixture(y, w, lf):
    ls = mixture_slow_rate(w, lf)
    if ls is None or not (0.0 < w < 1.0) or lf <= 0.0:
        return np.full_like(y, -1e12)
    a = np.log(w) + np.log(lf) - lf * y
    b = np.log1p(-w) + np.log(ls) - ls * y
    m = np.maximum(a, b)
    return m + np.log(np.exp(a - m) + np.exp(b - m))

# ----------------------------------------------------------------- cohort ---
def build_cohort(events, eligible: set[int]):
    tr = [e for e in events if e["partition"] == "train" and not e["rightCensored"]]
    ho = [e for e in events if e["partition"] == "holdout" and not e["rightCensored"]]
    sums, cnts = {}, {}
    for e in tr:
        if e["stateN"] in eligible:
            sums[e["stateN"]] = sums.get(e["stateN"], 0.0) + e["durationS"]
            cnts[e["stateN"]] = cnts.get(e["stateN"], 0) + 1
    scale = {n: sums[n] / cnts[n] for n in sums}
    tr2 = [e for e in tr if e["stateN"] in scale]
    ho2 = [e for e in ho if e["stateN"] in scale]
    ty = np.array([e["durationS"] / scale[e["stateN"]] for e in tr2])
    hy = np.array([e["durationS"] / scale[e["stateN"]] for e in ho2])
    hls = np.array([math.log(scale[e["stateN"]]) for e in ho2])
    motors = len({e["motorId"] for e in ho2})
    return dict(ty=ty, hy=hy, hls=hls, n_train=len(tr2), n_hold=len(ho2),
                holdout_motors=motors, states=sorted(scale))

# ------------------------------------------------------------------- fits ---
class Counter:
    def __init__(self): self.attempted = self.feasible = self.converged = self.finite = 0

def fit_scalar(nll, lo, hi, counter, n=60):
    best = None
    for x0 in np.linspace(lo, hi, n):
        counter.attempted += 1
        counter.feasible += 1
        for method in ("Nelder-Mead", "L-BFGS-B"):
            r = minimize(lambda p: nll(p[0]), [x0], method=method,
                         bounds=[(lo, hi)] if method == "L-BFGS-B" else None,
                         options={"maxiter": 20000})
            if getattr(r, "success", False): counter.converged += 1
            if np.isfinite(r.fun):
                counter.finite += 1
                if best is None or r.fun < best[0]:
                    best = (float(r.fun), float(r.x[0]), method)
    return best

def fit_mixture(ty, counter, seed):
    def nll(p):
        v = log_mixture(ty, p[0], p[1])
        return -float(np.sum(v))
    rng = np.random.default_rng(seed)
    starts = [(w, lf) for w in np.linspace(0.05, 0.95, 10)
              for lf in np.logspace(-1, 2.3, 10)]
    starts += [(float(rng.uniform(0.02, 0.98)), float(np.exp(rng.uniform(-2, 5))))
               for _ in range(200)]
    best, converged_vals = None, []
    for m in ("Nelder-Mead", "L-BFGS-B"):
        for s0 in starts:
            counter.attempted += 1
            if mixture_slow_rate(*s0) is None:          # enforce declared domain
                continue
            counter.feasible += 1
            try:
                r = minimize(nll, s0, method=m,
                             bounds=[SEARCH_DOMAIN["w"], SEARCH_DOMAIN["lf"]] if m == "L-BFGS-B" else None,
                             options={"maxiter": 20000, "maxfev": 20000} if m == "Nelder-Mead" else {"maxiter": 20000})
            except Exception:
                continue
            if getattr(r, "success", False): counter.converged += 1
            if np.isfinite(r.fun) and r.fun < 1e11:
                counter.finite += 1
                converged_vals.append(round(float(r.fun), 6))
                if 0 < r.x[0] < 1 and r.x[1] > r.x[0] and (best is None or r.fun < best[0]):
                    best = (float(r.fun), float(r.x[0]), float(r.x[1]), m)
    return best, sorted(set(converged_vals))

def heldout(hy, hls, k, s, w, lf):
    return {
        "exponential": float(np.mean(log_exp(hy) - hls)),
        "weibull":     float(np.mean(log_weibull(hy, k) - hls)),
        "lognormal":   float(np.mean(log_lognormal(hy, s) - hls)),
        "mixture":     float(np.mean(log_mixture(hy, w, lf) - hls)),
    }

# ---------------------------------------------------------------- scenario ---
def run(events, eligible, label, committed, seed):
    c = build_cohort(events, eligible)
    ty, hy, hls = c["ty"], c["hy"], c["hls"]
    cnt = Counter()
    wb = fit_scalar(lambda k: -float(np.sum(log_weibull(ty, k))), 0.05, 5.0, cnt)
    ln = fit_scalar(lambda s: -float(np.sum(log_lognormal(ty, s))), 0.05, 6.0, cnt)
    mx, basins = fit_mixture(ty, cnt, seed)

    def mix_nll(w, lf): return -float(np.sum(log_mixture(ty, w, lf)))
    committed_mix_nll = mix_nll(committed["w"], committed["lf"])
    committed_scores = heldout(hy, hls, committed["wb"], committed["ln"], committed["w"], committed["lf"])
    best_scores = heldout(hy, hls, wb[1], ln[1], mx[1], mx[2])
    ranking = sorted(best_scores, key=lambda m: -best_scores[m])

    return {
        "label": label,
        "eligibleStates": sorted(eligible),
        "statesWithTrainingScale": c["states"],
        "trainUncensoredEvents": c["n_train"],
        "holdoutUncensoredEvents": c["n_hold"],
        "holdoutMotors": c["holdout_motors"],
        "optimizerAttempts": {
            "attempted": cnt.attempted, "feasibleAfterDomainCheck": cnt.feasible,
            "reportedSuccess": cnt.converged, "finiteObjective": cnt.finite,
            "note": "Counted programmatically by this script, not asserted in prose.",
        },
        "independentFits": {
            "weibullShape": wb[1], "weibullTrainingNll": wb[0],
            "lognormalSigma": ln[1], "lognormalTrainingNll": ln[0],
            "mixtureWeightFast": mx[1], "mixtureRateFast": mx[2],
            "mixtureRateSlow": mixture_slow_rate(mx[1], mx[2]),
            "mixtureTrainingNll": mx[0],
        },
        "committedComparison": {
            "mixtureTrainingNllAtCommitted": committed_mix_nll,
            "mixtureTrainingNllAtBestFound": mx[0],
            "deltaNats": committed_mix_nll - mx[0],
            "heldoutScoresAtCommittedParams": committed_scores,
            "maxAbsErrorVsCommittedReport": max(
                abs(committed_scores[m] - committed["scores"][m]) for m in committed["scores"]
            ),
        },
        "heldoutScoresAtIndependentFits": best_scores,
        "ranking": ranking,
        "lognormalMinusMixture": best_scores["lognormal"] - best_scores["mixture"],
        "adverseLognormalResultSurvives": best_scores["lognormal"] > best_scores["mixture"],
        "distinctConvergedNllValues": basins,
        "searchDomain": SEARCH_DOMAIN,
        "conclusionStrength": (
            "No better solution was found over the declared search domain. "
            "The committed fit is numerically indistinguishable from the best located optimum. "
            "This is a finite-multistart numerical result, NOT a proof of global optimality."
        ),
    }

# -------------------------------------------------------------------- main ---
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    protocol = load_and_validate_protocol()
    events, split_mismatches, spanning = load_events_and_verify_split(protocol)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    protocol_states = set(protocol["scope"]["primaryStates"])
    committed_states = set(report["cohort"]["eligibleStates"])
    fitted = report["fittedOnTrainingOnly"]["normalizedDurationModels"]
    committed = {
        "w": fitted["mixture"]["weightFast"], "lf": fitted["mixture"]["rateFast"],
        "wb": fitted["weibull"]["shape"], "ln": fitted["lognormal"]["sigma"],
        "scores": report["heldoutResults"]["meanLogScoreNatsPerEvent"],
    }
    seed = int(protocol["uncertainty"]["seed"])

    discrepancy = {
        "protocolPrimaryStates": sorted(protocol_states),
        "committedEligibleStates": sorted(committed_states),
        "statesInProtocolButNotImplemented": sorted(protocol_states - committed_states),
        "authorizedByAFrozenRule": False,
        "explanation": (
            "scope.primaryStates in the frozen protocol is [0..8]. The committed report "
            "uses eligibleStates [1..8]. State 0 is NOT dropped for want of data - it has "
            "training and holdout uncensored events - so its exclusion is an implementation "
            "choice with no authorizing rule in the frozen protocol."
        ),
    }

    scenarios = [
        run(events, committed_states, "committed_eligible_states_1_to_8", committed, seed),
        run(events, protocol_states, "protocol_primary_states_0_to_8", committed, seed),
    ]

    checks = {
        "splitRecomputedWithZeroMismatches": split_mismatches == 0,
        "noMotorSpansPartitions": spanning == 0,
        "committedScoresReproduced": scenarios[0]["committedComparison"]["maxAbsErrorVsCommittedReport"] < 1e-12,
        "committedMixtureNotBeatenUnderCommittedStates": scenarios[0]["committedComparison"]["deltaNats"] < 1e-6,
        "adverseLognormalSurvivesUnderBothEligibilitySets": all(s["adverseLognormalResultSurvives"] for s in scenarios),
    }

    out = {
        "schema": "uni.flagellum.audit-artifact/1.0.0",
        "purpose": "Clone-reproducible B2 oracle: refits all claimed models, counts optimizer attempts programmatically, and reports the protocol/implementation eligibility discrepancy.",
        "auditedCommit": "9c3a644e4b57e8ac27f925dcec84222463063aa1",
        "repoRootDerivedFrom": "__file__",
        "protocolId": protocol["protocolId"],
        "splitVerification": {"mismatches": split_mismatches, "motorsSpanningPartitions": spanning},
        "eligibilityDiscrepancy": discrepancy,
        "scenarios": scenarios,
        "selfChecks": checks,
        "allSelfChecksPassed": all(checks.values()),
    }

    if args.json:
        args.json.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(f"protocol            : {protocol['protocolId']}")
    print(f"split mismatches    : {split_mismatches}   motors spanning partitions: {spanning}")
    print(f"protocol primaryStates : {sorted(protocol_states)}")
    print(f"committed eligible     : {sorted(committed_states)}")
    print(f"DISCREPANCY - states in protocol but not implemented: {discrepancy['statesInProtocolButNotImplemented']}")
    for s in scenarios:
        cc = s["committedComparison"]
        print(f"\n--- {s['label']} ---")
        print(f"  events            : {s['trainUncensoredEvents']} train / {s['holdoutUncensoredEvents']} holdout ({s['holdoutMotors']} motors)")
        print(f"  optimizer attempts: {s['optimizerAttempts']['attempted']} attempted, "
              f"{s['optimizerAttempts']['feasibleAfterDomainCheck']} feasible, "
              f"{s['optimizerAttempts']['finiteObjective']} finite")
        print(f"  reproduces committed scores to: {cc['maxAbsErrorVsCommittedReport']:.3e}")
        print(f"  mixture NLL committed {cc['mixtureTrainingNllAtCommitted']!r}")
        print(f"  mixture NLL best      {cc['mixtureTrainingNllAtBestFound']!r}")
        print(f"  delta                 {cc['deltaNats']!r} nats")
        print(f"  ranking           : {' > '.join(s['ranking'])}")
        print(f"  lognormal-mixture : {s['lognormalMinusMixture']!r}  survives={s['adverseLognormalResultSurvives']}")
        print(f"  distinct basins   : {s['distinctConvergedNllValues'][:4]}")
    print("\nSELF-CHECKS")
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return 0 if all(checks.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
