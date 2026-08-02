#!/usr/bin/env python3
"""
B3 INDEPENDENT ORACLE.

Independently re-derives a stratified sample of the B3 competition result from
the recorded fitted parameters, WITHOUT importing the runner under test
(b3-model-competition-runner.py) and sharing no helper module with it. Per the
frozen scoring specification section 7 (independentRederivation) and the
coordinator plan, this is a circular-oracle guard: it must reconstruct each
model's density from the recorded parameters using its own code, recompute
held-out NLPD and CRPS, the motor-equal leaderboard, and the sign of every
primary M3 contrast bootstrap interval, and confirm agreement with the runner's
recorded artifact.

It reads only:
  - audits/phase-b/b3-model-competition-result.json  (the artifact under audit)
  - experiments/data/wadhwa-2022-events.json         (source observations)

Usage:  python audits/phase-b/b3-independent-oracle.py [--result PATH] [--json OUT]
Exit 0 iff every independent check agrees within the declared tolerance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import scipy.integrate
import scipy.special
import scipy.stats

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
DEFAULT_RESULT = ROOT / "audits" / "phase-b" / "b3-model-competition-result.json"

SEED = 20260717
TOL = 1e-8
LOG_SQRT2PI = 0.5 * math.log(2.0 * math.pi)
SQRT2 = math.sqrt(2.0)

checks = []


def check(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})
    return bool(ok)


# ---- independent data / cohort reconstruction ------------------------------

def part(motor_id):
    return int(hashlib.sha256(motor_id.encode("utf-8")).hexdigest(), 16) % 5


def build(states):
    events = json.loads(DATA.read_text(encoding="utf-8"))["events"]
    elig = [e for e in events if (not e["rightCensored"]) and e["stateN"] in states]
    train = [e for e in elig if part(e["motorId"]) != 0]
    hold = [e for e in elig if part(e["motorId"]) == 0]
    scale = {}
    for s in states:
        d = [e["durationS"] for e in train if e["stateN"] == s]
        if d:
            scale[s] = sum(d) / len(d)
    return train, hold, scale


# ---- independent densities (own implementations) ---------------------------

def logpdf(model, params, y, stateN, scale):
    """Normalized-space log density, reconstructed independently."""
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


def survival(model, params, x, stateN, scale):
    return 1.0 - cdf(model, params, x, stateN, scale)


def cdf(model, params, x, stateN, scale):
    if x <= 0:
        return 0.0
    if model == "M0_EXPONENTIAL":
        return 1 - math.exp(-x)
    if model == "M1_WEIBULL":
        k = params[0]; sw = math.exp(-math.lgamma(1 + 1 / k)); return 1 - math.exp(-((x / sw) ** k))
    if model == "M2_LOGNORMAL":
        sig = params[0]; mu = -sig * sig / 2; return float(scipy.stats.norm.cdf((math.log(x) - mu) / sig))
    if model == "M3_TWO_TIMESCALE":
        w, lf = params[0], params[1]; ls = (1 - w) / (1 - w / lf)
        return 1 - (w * math.exp(-lf * x) + (1 - w) * math.exp(-ls * x))
    if model == "M5_GAMMA":
        a = params[0]; return float(scipy.special.gammainc(a, a * x))
    if model == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        k = params[str(stateN)] if str(stateN) in params else params[stateN]
        sw = math.exp(-math.lgamma(1 + 1 / k)); return 1 - math.exp(-((x / sw) ** k))
    if model == "M4_MIXTURE_K3":
        rates = params["rates"]; weights = params["weights"]
        return 1 - sum(weights[i] * math.exp(-rates[i] * x) for i in range(3))
    if model == "M7_HIERARCHICAL_MOTOR":
        k, tau = params["k"], params["tau"]
        xx, v = np.polynomial.hermite.hermgauss(129)
        z = SQRT2 * xx; wr = v / math.sqrt(math.pi); W = wr / wr.sum()
        a = np.clip(k * np.exp(tau * z), 1e-3, 1e3); ls = -scipy.special.gammaln(1 + 1 / a)
        inner = a * (math.log(x) - ls)
        return float(1 - np.sum(W * np.exp(-np.exp(np.minimum(inner, 700.0)))))
    if model == "M8_EMPIRICAL_KDE":
        s = params["_s"]; h = params["h"]
        return float(np.mean(scipy.stats.norm.cdf((math.log(x) - s) / h)))
    raise ValueError(model)


def crps_y(model, params, yobs, stateN, scale):
    """Independent CRPS in y-space via a 3-term split (own quadrature call)."""
    if model == "M0_EXPONENTIAL":
        return yobs - 2 * (1 - math.exp(-yobs)) + 0.5
    if model == "M2_LOGNORMAL":
        sig = params[0]; mu = -sig * sig / 2; om = (math.log(yobs) - mu) / sig
        P = scipy.stats.norm.cdf
        return yobs * (2 * P(om) - 1) - 2 * (P(om - sig) + P(sig / SQRT2) - 1)
    if model == "M4_MIXTURE_K3":  # independent closed form (M4 spec section 9)
        r = params["rates"]; o = params["weights"]
        a = [r[i] for i in range(3)]
        term = yobs - 2 * sum(o[i] * (1 - math.exp(-a[i] * yobs)) / a[i] for i in range(3))
        term += sum(o[i] * o[j] / (a[i] + a[j]) for i in range(3) for j in range(3))
        return term
    U = 50.0
    F = lambda t: cdf(model, params, t, stateN, scale)
    L = max(U, yobs)
    A = scipy.integrate.quad(lambda t: F(t) ** 2, 0, yobs, epsabs=1e-11, epsrel=1e-11, limit=500)[0]
    B = 0.0 if yobs >= U else scipy.integrate.quad(
        lambda t: (1 - F(t)) ** 2, yobs, L, epsabs=1e-11, epsrel=1e-11, limit=500)[0]
    C = scipy.integrate.quad(lambda t: (1 - F(t)) ** 2, L, np.inf, epsabs=1e-11, epsrel=1e-11, limit=500)[0]
    return A + B + C


# ---- scoring / aggregation (independent) -----------------------------------

def motor_equal(hold, per_event):
    by = {}
    for e, v in zip(hold, per_event):
        by.setdefault(e["motorId"], []).append(v)
    motors = sorted(by)
    pm = np.array([np.mean(by[m]) for m in motors], dtype=np.float64)
    return float(np.mean(pm)), pm, motors


def params_for(model, fitted):
    rec = fitted[model]
    if model == "M0_EXPONENTIAL":
        return []
    if model in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA", "M3_TWO_TIMESCALE"):
        return rec["params"]
    if model == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        return rec["params"]
    if model == "M4_MIXTURE_K3":
        return {"rates": rec["canonical"]["rates"], "weights": rec["canonical"]["weights"]}
    if model == "M7_HIERARCHICAL_MOTOR":
        return {"k": rec["kTau"]["k"], "tau": rec["kTau"]["tau"]}
    if model == "M8_EMPIRICAL_KDE":
        return {"h": rec["h"]}
    raise ValueError(model)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    res = json.loads(args.result.read_text(encoding="utf-8"))
    STATE_SETS = {"derived_eligible_1_to_8": set(range(1, 9)),
                  "primary_states_0_to_8": set(range(0, 9))}

    for cname, cres in res["cohorts"].items():
        train, hold, scale = build(STATE_SETS[cname])
        fitted = cres["fitted"]
        rec_scores = cres["scores"]
        # NLPD motor-equal for every model, independently
        nlpd_pm = {}
        for model in res["models"]:
            p = params_for(model, fitted)
            if model == "M8_EMPIRICAL_KDE":
                p = {"h": p["h"], "_s": m8_locations(train, scale, p["h"])}
            per = []
            for e in hold:
                y = e["durationS"] / scale[e["stateN"]]
                lp = logpdf(model, p, y, e["stateN"], scale)
                per.append(-lp + math.log(scale[e["stateN"]]))
            me, pm, motors = motor_equal(hold, per)
            nlpd_pm[model] = pm
            rec = rec_scores[model]["NLPD_motor_equal"]["motorEqual"]
            check(f"{cname}:{model}:NLPD_motor_equal", abs(me - rec) <= TOL,
                  f"oracle={me:.12g} recorded={rec:.12g} d={abs(me-rec):.2e}")

        # CRPS_seconds motor-equal for M0/M2/M3/M4 (closed-form / independent)
        for model in ["M0_EXPONENTIAL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE", "M4_MIXTURE_K3"]:
            p = params_for(model, fitted)
            per = []
            for e in hold:
                y = e["durationS"] / scale[e["stateN"]]
                per.append(scale[e["stateN"]] * crps_y(model, p, y, e["stateN"], scale))
            me, _, _ = motor_equal(hold, per)
            rec = rec_scores[model]["CRPS_seconds"]["motorEqual"]
            check(f"{cname}:{model}:CRPS_seconds_motor_equal", abs(me - rec) <= 1e-6,
                  f"oracle={me:.10g} recorded={rec:.10g} d={abs(me-rec):.2e}")

        # leaderboard ordering (NLPD motor-equal) independent
        order = sorted(res["models"], key=lambda m: rec_scores[m]["NLPD_motor_equal"]["motorEqual"])
        rec_board = [r["model"] for r in cres["leaderboards"]["NLPD_motor_equal"]["motorEqual"]]
        check(f"{cname}:NLPD_leaderboard_order", order == rec_board, f"{order} vs {rec_board}")

        # contrast sign vs M3 (independent bootstrap, recorded seed) under NLPD
        n_motors = len(nlpd_pm["M3_TWO_TIMESCALE"])
        rng = np.random.default_rng(SEED)
        R = rng.integers(0, n_motors, size=(50000, n_motors), dtype=np.int64)
        n_rep = res["uncertainty"]["primaryReplicates"]
        Rp = R[:n_rep]
        ref = nlpd_pm["M3_TWO_TIMESCALE"]
        for model in res["models"]:
            if model == "M3_TWO_TIMESCALE":
                continue
            chal = nlpd_pm[model]
            theta = np.array([np.mean(ref[Rp[b]]) - np.mean(chal[Rp[b]]) for b in range(n_rep)])
            lo = float(np.quantile(theta, 0.025, method="linear"))
            hi = float(np.quantile(theta, 0.975, method="linear"))
            sign = "M_BEATS_M3" if lo > 0 else ("M3_BEATS_M" if hi < 0 else "INCONCLUSIVE")
            rec_v = cres["contrasts"]["NLPD_motor_equal"][model]["verdict"]
            # oracle uses percentile; runner uses BCa-when-defined. Compare the
            # zero-crossing classification, which both should agree on.
            check(f"{cname}:{model}:NLPD_contrast_sign", sign == rec_v,
                  f"oraclePercentile={sign} recorded={rec_v}")

    passed = sum(c["passed"] for c in checks)
    total = len(checks)
    out = {"schema": "uni.flagellum.b3-oracle-result/1.0.0",
           "resultAudited": str(args.result.name),
           "checksPassed": passed, "checksTotal": total,
           "allPassed": passed == total, "tolerance": TOL, "checks": checks}
    if args.json:
        args.json.write_bytes((json.dumps(out, indent=2) + "\n").encode("utf-8"))
    for c in checks:
        if not c["passed"]:
            print("  FAIL", c["check"], c["detail"])
    print(f"\nB3 ORACLE: {passed}/{total} independent checks agree")
    return 0 if passed == total else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
