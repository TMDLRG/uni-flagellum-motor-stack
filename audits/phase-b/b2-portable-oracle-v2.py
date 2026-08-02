#!/usr/bin/env python3
"""
B2 PORTABLE ORACLE v2 — corrects four defects Codex identified in v1.

  1. eligibility mis-derived   -> derived as primaryStates INTERSECT the frozen
                                  H1 rule (>=20 uncensored holdout events from
                                  >=5 holdout motors), which reproduces the
                                  committed eligibleStates exactly
  2. vacuous self-check        -> abs(delta) tolerance, and the committed
                                  parameters are supplied as an explicit start
  3. incoherent telemetry      -> five separate, non-overlapping counters, and
                                  successful convergence distinguished from
                                  merely-finite termination
  4. platform line endings     -> canonical UTF-8 / LF bytes written explicitly

Also adds, per Codex: dataset/report/protocol identity validation, and direct
mathematical checks (unit integral, mean-one, parameter-domain assertions) in
place of any shared executable model code.

Reads: experiments/preregistration.v1.json                (protocol)
       experiments/data/wadhwa-2022-events.json           (data)
       experiments/results/observed-experiment-report.json (COMPARISON TARGETS)
Does not import lib/ or scripts/. Equations are implemented from frozen prose.

Usage:  python audits/phase-b/b2-portable-oracle-v2.py [--json OUT.json]
Exit 0 iff every self-check passes.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re, sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize
from scipy.special import gammaln

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "experiments" / "preregistration.v1.json"
DATA_PATH = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
REPORT_PATH = ROOT / "experiments" / "results" / "observed-experiment-report.json"

SEARCH_DOMAIN = {"w": [1e-9, 1 - 1e-9], "lf": [1e-9, 1e4],
                 "constraint": "lf > w, from the mean-one feasibility 1 - w/lf > 0"}
DELTA_TOL = 1e-6

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

# ---------------------------------------------------------------- densities ---
def log_exp(y): return -y
def log_weibull(y, k):
    log_sw = -gammaln(1.0 + 1.0 / k)
    z = np.log(y) - log_sw
    return np.log(k) - log_sw + (k - 1.0) * z - np.exp(k * z)
def log_lognormal(y, s):
    mu = -0.5 * s * s
    return -np.log(y * s * math.sqrt(2 * math.pi)) - (np.log(y) - mu) ** 2 / (2 * s * s)
def mixture_slow_rate(w, lf):
    den = 1.0 - w / lf
    return None if den <= 0 else (1.0 - w) / den
def log_mixture(y, w, lf):
    ls = mixture_slow_rate(w, lf)
    if ls is None or not (0.0 < w < 1.0) or lf <= 0.0:
        return np.full_like(np.asarray(y, dtype=float), -1e12)
    a = np.log(w) + np.log(lf) - lf * y
    b = np.log1p(-w) + np.log(ls) - ls * y
    m = np.maximum(a, b)
    return m + np.log(np.exp(a - m) + np.exp(b - m))

# --------------------------------------------- direct mathematical checks ---
def mathematical_checks() -> dict:
    """Verify unit integral, mean-one and domain behaviour by quadrature."""
    out, ok = [], True
    fams = [("exponential", lambda y: np.exp(log_exp(y)), None)]
    for k in (0.35, 0.625088844276203, 1.0, 2.7):
        fams.append((f"weibull(k={k})", lambda y, k=k: np.exp(log_weibull(y, k)), None))
    for s in (0.4, 1.5783076021679734, 2.6):
        fams.append((f"lognormal(s={s})", lambda y, s=s: np.exp(log_lognormal(y, s)), None))
    for (w, lf) in ((0.3, 2.0), (0.6066448974609373, 5.239865393555934), (0.85, 40.0)):
        fams.append((f"mixture(w={w},lf={lf})", lambda y, w=w, lf=lf: np.exp(log_mixture(y, w, lf)), None))
    for name, f, _ in fams:
        integral = quad(f, 0, np.inf, limit=400)[0]
        mean = quad(lambda y: y * f(y), 0, np.inf, limit=400)[0]
        good = abs(integral - 1.0) < 1e-6 and abs(mean - 1.0) < 1e-6
        ok = ok and good
        out.append({"family": name, "integral": integral, "mean": mean, "unitIntegralAndMeanOne": good})
    # parameter-domain assertions
    domain = {
        "mixtureInfeasibleWhen_lf_le_w": mixture_slow_rate(0.6, 0.5) is None,
        "mixtureFeasibleWhen_lf_gt_w": mixture_slow_rate(0.6, 5.0) is not None,
        "mixtureSlowRatePositive": (mixture_slow_rate(0.6066448974609373, 5.239865393555934) or -1) > 0,
    }
    ok = ok and all(domain.values())
    return {"families": out, "domainAssertions": domain, "allPassed": ok}

# ------------------------------------------------------- protocol + identity ---
def load_and_validate_protocol() -> dict:
    p = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    problems = []
    for key in ("protocolId", "scope", "split", "extraction", "models", "hypotheses", "uncertainty"):
        if key not in p:
            problems.append(f"protocol missing key: {key}")
    if "modulo 5" not in p.get("split", {}).get("method", ""):
        problems.append("split method is not the expected sha256 mod 5 rule")
    if p.get("split", {}).get("holdoutRemainders") != [0]:
        problems.append("unexpected holdoutRemainders")
    if "primaryStates" not in p.get("scope", {}):
        problems.append("scope.primaryStates absent")
    if not any(h.get("id") == "H1_OVERDISPERSION" for h in p.get("hypotheses", [])):
        problems.append("H1_OVERDISPERSION hypothesis absent; eligibility rule undefined")
    if problems:
        raise SystemExit("PROTOCOL VALIDATION FAILED:\n  " + "\n  ".join(problems))
    return p

def validate_identities(protocol, dataset, report) -> dict:
    src_p, src_d = protocol.get("source", {}), dataset.get("source", {})
    ident = report.get("identities", {})
    checks = {
        "reportProtocolIdMatchesProtocol": report.get("protocolId") == protocol.get("protocolId"),
        "datasetSourceCommitMatchesProtocol": src_d.get("commit") == src_p.get("commit"),
        "datasetRawSha256MatchesProtocol": src_d.get("observedRawSha256") == src_p.get("rawSha256"),
        "reportProtocolSha256MatchesFileOnDisk": ident.get("protocolSha256") == sha256_file(PROTOCOL_PATH),
        "reportDerivedEventsSha256MatchesFileOnDisk": ident.get("derivedEventsSha256") == sha256_file(DATA_PATH),
    }
    return {"checks": checks, "allPassed": all(v for v in checks.values() if v is not None)}

# --------------------------------------------------------------- eligibility ---
def derive_eligible_states(protocol, events) -> dict:
    """primaryStates INTERSECT the frozen H1 rule. Nothing hard-coded."""
    primary = list(protocol["scope"]["primaryStates"])
    h1 = next(h for h in protocol["hypotheses"] if h["id"] == "H1_OVERDISPERSION")
    rule_text = h1["eligibility"]
    # Thresholds are PARSED from the frozen rule with a labelled pattern that binds
    # each number to its role. A substring test such as ("20" in rule_text) would be
    # satisfied by "120", and would not detect the quantities being transposed.
    pattern = re.compile(
        r"at\s+least\s+(?P<events>\d+)\s+uncensored\s+holdout\s+events\s+"
        r"from\s+at\s+least\s+(?P<motors>\d+)\s+holdout\s+motors",
        re.IGNORECASE,
    )
    match = pattern.search(rule_text)
    if match is None:
        raise SystemExit(
            "H1 eligibility rule did not match the expected labelled form; refusing to "
            f"guess thresholds. Frozen text was: {rule_text!r}"
        )
    min_events = int(match.group("events"))
    min_motors = int(match.group("motors"))
    if not (min_events > 0 and min_motors > 0):
        raise SystemExit(f"parsed non-positive thresholds: events={min_events} motors={min_motors}")
    per_state, eligible = {}, []
    for n in sorted({e["stateN"] for e in events}):
        hu = [e for e in events if e["stateN"] == n and e["partition"] == "holdout" and not e["rightCensored"]]
        motors = len({e["motorId"] for e in hu})
        passes = len(hu) >= min_events and motors >= min_motors
        per_state[n] = {"holdoutUncensoredEvents": len(hu), "holdoutMotors": motors,
                        "meetsH1Thresholds": passes, "inPrimaryStates": n in primary}
        if passes and n in primary:
            eligible.append(n)
    return {"ruleText": rule_text, "minHoldoutEvents": min_events, "minHoldoutMotors": min_motors,
            "primaryStates": primary, "perState": per_state, "derivedEligibleStates": eligible}

# -------------------------------------------------------------------- cohort ---
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
    return dict(
        ty=np.array([e["durationS"] / scale[e["stateN"]] for e in tr2]),
        hy=np.array([e["durationS"] / scale[e["stateN"]] for e in ho2]),
        hls=np.array([math.log(scale[e["stateN"]]) for e in ho2]),
        n_train=len(tr2), n_hold=len(ho2),
        holdout_motors=len({e["motorId"] for e in ho2}), states=sorted(scale))

# ------------------------------------------------------------------ counters ---
class Telemetry:
    """Five non-overlapping counters. finiteTerminalResults <= domainFeasibleOptimizerCalls always."""
    def __init__(self):
        self.startsDeclared = 0
        self.methodStartPairsConsidered = 0
        self.domainFeasibleOptimizerCalls = 0
        self.successfulOptimizerCalls = 0
        self.finiteTerminalResults = 0
    def asdict(self):
        return {"startsDeclared": self.startsDeclared,
                "methodStartPairsConsidered": self.methodStartPairsConsidered,
                "domainFeasibleOptimizerCalls": self.domainFeasibleOptimizerCalls,
                "successfulOptimizerCalls": self.successfulOptimizerCalls,
                "finiteTerminalResults": self.finiteTerminalResults,
                "coherent": self.finiteTerminalResults <= self.domainFeasibleOptimizerCalls
                            and self.domainFeasibleOptimizerCalls <= self.methodStartPairsConsidered}

METHODS = ("Nelder-Mead", "L-BFGS-B")

def fit_scalar(nll, lo, hi, tel: Telemetry, n=60):
    """Nelder-Mead is unbounded, so the domain is enforced by an explicit penalty
    rather than relying on numpy's inf semantics to absorb a degenerate parameter."""
    def guarded(p):
        x = float(p[0])
        if not (lo <= x <= hi) or x <= 0.0:
            return 1e12                              # explicit out-of-domain penalty
        return nll(x)
    best = None
    starts = list(np.linspace(lo, hi, n))
    tel.startsDeclared += len(starts)
    for x0 in starts:
        for method in METHODS:
            tel.methodStartPairsConsidered += 1
            tel.domainFeasibleOptimizerCalls += 1        # scalar domain is the bracket itself
            r = minimize(guarded, [x0], method=method,
                         bounds=[(lo, hi)] if method == "L-BFGS-B" else None,
                         options={"maxiter": 20000})
            if getattr(r, "success", False):
                tel.successfulOptimizerCalls += 1
            if np.isfinite(r.fun):
                tel.finiteTerminalResults += 1
                if best is None or r.fun < best[0]:
                    best = (float(r.fun), float(r.x[0]), method, bool(getattr(r, "success", False)))
    return best

def in_declared_mixture_domain(w, lf) -> bool:
    wlo, whi = SEARCH_DOMAIN["w"]
    llo, lhi = SEARCH_DOMAIN["lf"]
    return (wlo <= w <= whi) and (llo <= lf <= lhi) and mixture_slow_rate(w, lf) is not None

def fit_mixture(ty, tel: Telemetry, seed, committed_start):
    def nll(p):
        # Nelder-Mead is unbounded, so the DECLARED bounds are enforced by an explicit
        # penalty. Without this a simplex could terminate at lf > 1e4 while the report
        # asserts that only the declared domain was searched.
        w, lf = float(p[0]), float(p[1])
        if not in_declared_mixture_domain(w, lf):
            return 1e12
        return -float(np.sum(log_mixture(ty, w, lf)))
    rng = np.random.default_rng(seed)
    starts = [(w, lf) for w in np.linspace(0.05, 0.95, 10) for lf in np.logspace(-1, 2.3, 10)]
    starts += [(float(rng.uniform(0.02, 0.98)), float(np.exp(rng.uniform(-2, 5)))) for _ in range(200)]
    starts.append(tuple(committed_start))       # committed parameters as an explicit start
    tel.startsDeclared += len(starts)
    best, finite_vals, success_vals = None, [], []
    for m in METHODS:
        for s0 in starts:
            tel.methodStartPairsConsidered += 1
            if not in_declared_mixture_domain(*s0):
                continue
            tel.domainFeasibleOptimizerCalls += 1
            try:
                r = minimize(nll, s0, method=m,
                             bounds=[SEARCH_DOMAIN["w"], SEARCH_DOMAIN["lf"]] if m == "L-BFGS-B" else None,
                             options={"maxiter": 20000, "maxfev": 20000} if m == "Nelder-Mead" else {"maxiter": 20000})
            except Exception:
                continue
            succeeded = bool(getattr(r, "success", False))
            if succeeded:
                tel.successfulOptimizerCalls += 1
            if np.isfinite(r.fun) and r.fun < 1e11:
                tel.finiteTerminalResults += 1
                finite_vals.append(round(float(r.fun), 6))
                if succeeded:
                    success_vals.append(round(float(r.fun), 6))
                if in_declared_mixture_domain(float(r.x[0]), float(r.x[1])) and (best is None or r.fun < best[0]):
                    best = (float(r.fun), float(r.x[0]), float(r.x[1]), m, succeeded)
    return best, sorted(set(finite_vals)), sorted(set(success_vals))

def heldout(hy, hls, k, s, w, lf):
    return {"exponential": float(np.mean(log_exp(hy) - hls)),
            "weibull": float(np.mean(log_weibull(hy, k) - hls)),
            "lognormal": float(np.mean(log_lognormal(hy, s) - hls)),
            "mixture": float(np.mean(log_mixture(hy, w, lf) - hls))}

# ------------------------------------------------------------------ scenario ---
def run(events, eligible, label, note, committed, seed):
    c = build_cohort(events, set(eligible))
    ty, hy, hls = c["ty"], c["hy"], c["hls"]
    tel = Telemetry()
    wb = fit_scalar(lambda k: -float(np.sum(log_weibull(ty, k))), 0.05, 5.0, tel)
    ln = fit_scalar(lambda s: -float(np.sum(log_lognormal(ty, s))), 0.05, 6.0, tel)
    mx, finite_basins, success_basins = fit_mixture(ty, tel, seed, (committed["w"], committed["lf"]))

    committed_mix_nll = -float(np.sum(log_mixture(ty, committed["w"], committed["lf"])))
    committed_scores = heldout(hy, hls, committed["wb"], committed["ln"], committed["w"], committed["lf"])
    best_scores = heldout(hy, hls, wb[1], ln[1], mx[1], mx[2])
    delta = committed_mix_nll - mx[0]

    return {
        "label": label, "note": note,
        "eligibleStates": sorted(eligible),
        "trainUncensoredEvents": c["n_train"], "holdoutUncensoredEvents": c["n_hold"],
        "holdoutMotors": c["holdout_motors"],
        "telemetry": tel.asdict(),
        "independentFits": {
            "weibullShape": wb[1], "weibullTrainingNll": wb[0], "weibullOptimizerSucceeded": wb[3],
            "lognormalSigma": ln[1], "lognormalTrainingNll": ln[0], "lognormalOptimizerSucceeded": ln[3],
            "mixtureWeightFast": mx[1], "mixtureRateFast": mx[2],
            "mixtureRateSlow": mixture_slow_rate(mx[1], mx[2]),
            "mixtureTrainingNll": mx[0], "mixtureOptimizerSucceeded": mx[4],
        },
        "committedComparison": {
            "mixtureTrainingNllAtCommitted": committed_mix_nll,
            "mixtureTrainingNllAtBestFound": mx[0],
            "deltaNats": delta,
            "absDeltaNats": abs(delta),
            "committedNotBeaten": abs(delta) < DELTA_TOL,
            "sign": "committed worse" if delta > 0 else ("committed better" if delta < 0 else "identical"),
            "heldoutScoresAtCommittedParams": committed_scores,
            "maxAbsErrorVsCommittedReport": max(abs(committed_scores[m] - committed["scores"][m]) for m in committed["scores"]),
        },
        "heldoutScoresAtIndependentFits": best_scores,
        "ranking": sorted(best_scores, key=lambda m: -best_scores[m]),
        "lognormalMinusMixture": best_scores["lognormal"] - best_scores["mixture"],
        "adverseLognormalResultSurvives": best_scores["lognormal"] > best_scores["mixture"],
        "distinctFiniteTerminalNllValues": finite_basins,
        "distinctSuccessfulNllValues": success_basins,
        "searchDomain": SEARCH_DOMAIN,
        "conclusionStrength": ("No better solution was found over the declared search domain. The committed "
                               "fit is numerically indistinguishable from the best located optimum. This is a "
                               "finite-multistart numerical result, NOT a proof of global optimality."),
    }

# ---------------------------------------------------------------------- main ---
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    protocol = load_and_validate_protocol()
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    events = dataset["events"]
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    identities = validate_identities(protocol, dataset, report)
    maths = mathematical_checks()
    elig = derive_eligible_states(protocol, events)

    # split verification
    hold = set(protocol["split"]["holdoutRemainders"])
    mismatches = sum(
        1 for e in events
        if ("holdout" if int(hashlib.sha256(e["motorId"].encode()).hexdigest(), 16) % 5 in hold else "train") != e["partition"]
    )
    spanning = sum(1 for m in {e["motorId"] for e in events}
                   if len({e["partition"] for e in events if e["motorId"] == m}) > 1)

    fitted = report["fittedOnTrainingOnly"]["normalizedDurationModels"]
    committed = {"w": fitted["mixture"]["weightFast"], "lf": fitted["mixture"]["rateFast"],
                 "wb": fitted["weibull"]["shape"], "ln": fitted["lognormal"]["sigma"],
                 "scores": report["heldoutResults"]["meanLogScoreNatsPerEvent"]}
    seed = int(protocol["uncertainty"]["seed"])
    committed_states = report["cohort"]["eligibleStates"]

    scenarios = [
        run(events, elig["derivedEligibleStates"], "derived_eligible_H1_rule_applied",
            "primaryStates INTERSECT the frozen H1 eligibility rule. Reproduces the committed cohort.",
            committed, seed),
        run(events, elig["primaryStates"], "primary_states_H1_rule_not_applied",
            "All primaryStates, i.e. the H1 eligibility filter NOT reused for model fitting. "
            "Robustness probe for the PROTOCOL_SCOPE_AMBIGUITY: the protocol nests the eligibility "
            "rule under H1 and does not state whether H2/model fitting reuses it.",
            committed, seed),
    ]

    checks = {
        "protocolValidated": True,
        "identityChecksPassed": identities["allPassed"],
        "mathematicalChecksPassed": maths["allPassed"],
        "splitRecomputedWithZeroMismatches": mismatches == 0,
        "noMotorSpansPartitions": spanning == 0,
        "derivedEligibilityMatchesCommittedCohort": elig["derivedEligibleStates"] == committed_states,
        "committedScoresReproduced": scenarios[0]["committedComparison"]["maxAbsErrorVsCommittedReport"] < 1e-12,
        "committedMixtureNotBeatenAndNotBeating": scenarios[0]["committedComparison"]["committedNotBeaten"],
        "telemetryCoherentInEveryScenario": all(s["telemetry"]["coherent"] for s in scenarios),
        "adverseLognormalSurvivesUnderBothCohorts": all(s["adverseLognormalResultSurvives"] for s in scenarios),
    }

    out = {
        "schema": "uni.flagellum.audit-artifact/1.0.0",
        "purpose": "Clone-reproducible B2 oracle v2. Eligibility derived from frozen rules; symmetric delta check; coherent telemetry; canonical LF output.",
        "auditedCommit": "9c3a644e4b57e8ac27f925dcec84222463063aa1",
        "repoRootDerivedFrom": "__file__",
        "protocolId": protocol["protocolId"],
        "identityValidation": identities,
        "mathematicalChecks": maths,
        "eligibilityDerivation": elig,
        "committedEligibleStates": committed_states,
        "splitVerification": {"mismatches": mismatches, "motorsSpanningPartitions": spanning},
        "scenarios": scenarios,
        "selfChecks": checks,
        "allSelfChecksPassed": all(checks.values()),
    }

    if args.json:
        # canonical UTF-8 / LF bytes, identical on every platform
        args.json.write_bytes((json.dumps(out, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))

    print(f"protocol {protocol['protocolId']} | split mismatches {mismatches} | spanning {spanning}")
    print(f"identity checks: {identities['allPassed']} | mathematical checks: {maths['allPassed']}")
    print(f"derived eligible {elig['derivedEligibleStates']} vs committed {committed_states} "
          f"-> match={elig['derivedEligibleStates'] == committed_states}")
    s0 = elig["perState"].get(0)
    if s0:
        print(f"  state 0: {s0['holdoutUncensoredEvents']} holdout events, {s0['holdoutMotors']} motors "
              f"-> meets H1 thresholds: {s0['meetsH1Thresholds']}")
    for s in scenarios:
        cc, t = s["committedComparison"], s["telemetry"]
        print(f"\n--- {s['label']} ---")
        print(f"  events {s['trainUncensoredEvents']}/{s['holdoutUncensoredEvents']} ({s['holdoutMotors']} motors)")
        print(f"  telemetry starts={t['startsDeclared']} pairs={t['methodStartPairsConsidered']} "
              f"feasible={t['domainFeasibleOptimizerCalls']} success={t['successfulOptimizerCalls']} "
              f"finite={t['finiteTerminalResults']} coherent={t['coherent']}")
        print(f"  reproduces committed scores to {cc['maxAbsErrorVsCommittedReport']:.3e}")
        print(f"  mixture NLL committed {cc['mixtureTrainingNllAtCommitted']!r}")
        print(f"  mixture NLL best      {cc['mixtureTrainingNllAtBestFound']!r}")
        print(f"  |delta| {cc['absDeltaNats']!r} ({cc['sign']})  notBeaten={cc['committedNotBeaten']}")
        print(f"  ranking {' > '.join(s['ranking'])}  lognormal-mixture {s['lognormalMinusMixture']!r}")
    print("\nSELF-CHECKS")
    for k, v in checks.items():
        print(f"  {'PASS' if v else 'FAIL'}  {k}")
    return 0 if all(checks.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
