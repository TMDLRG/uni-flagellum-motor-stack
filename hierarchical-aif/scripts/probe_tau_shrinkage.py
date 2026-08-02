"""PROBE 5 part 2 — posterior shrinkage of eta_m and motor-level heterogeneity evidence.

Duration-only. Training partition ONLY. No holdout field of any kind is read here.

Section 2: `hierarchy.posterior_motor_shape` at the RECORDED fit (mu, tau), per training motor.
Section 3: events-per-motor distribution, and a null calibration of the between-motor spread of
           the NO-POOLING per-motor log-shape MLE under the tau -> 0 (single shared shape)
           generator. The simulated replicates are SIMULATION, never observation.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import optimize, special

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from motor_stack_aif import compare, hazard_survival as hs, hierarchy  # noqa: E402

# Recorded F-side fit, read from the landed artifact (not refitted here).
FIT_JSON = HERE / "results" / "motor_stack_aif" / "F_SIDE_MOTOR_STACK_SCORING_RESULT.json"

LOGK_BOUNDS = (math.log(0.05), math.log(5.0))   # same box the frozen M7 U2 profile uses
N_NULL_REP = 300
NULL_SEED = 20260717


def _motor_nll(log_k: float, y: np.ndarray, c: np.ndarray) -> float:
    k = math.exp(float(log_k))
    if not (hierarchy.K_MIN_REPRESENTABLE <= k <= hierarchy.K_MAX_REPRESENTABLE):
        return 1e12
    try:
        return -float(np.sum(hs.log_event_density(
            y, c, hs.weibull_log_hazard, hs.weibull_log_survival, k)))
    except (hs.NonFiniteLogDensity, OverflowError):
        return 1e12


def _nopool_eta(y: np.ndarray, c: np.ndarray):
    r = optimize.minimize_scalar(lambda lk: _motor_nll(lk, y, c), bounds=LOGK_BOUNDS,
                                 method="bounded", options={"xatol": 1e-8})
    eta = float(r.x)
    at_bound = bool(abs(eta - LOGK_BOUNDS[0]) < 1e-6 or abs(eta - LOGK_BOUNDS[1]) < 1e-6)
    # observed-information SE by central second difference of the profile in eta
    h = 1e-3
    f0 = float(r.fun)
    fp = _motor_nll(eta + h, y, c)
    fm = _motor_nll(eta - h, y, c)
    curv = (fp - 2.0 * f0 + fm) / (h * h)
    se = float(math.sqrt(1.0 / curv)) if curv > 0 else None
    return eta, se, at_bound


def _weibull_mean_one_rvs(k: float, n: int, rng) -> np.ndarray:
    lam = 1.0 / math.exp(special.gammaln(1.0 + 1.0 / k))
    u = rng.random(n)
    return lam * np.power(-np.log1p(-u), 1.0 / k)


def main() -> int:
    t0 = time.time()
    rec = json.loads(FIT_JSON.read_text(encoding="utf-8"))
    fitrec = rec["fitted"]["F_MOTOR_STACK"]
    mu = float(fitrec["mu"])
    tau = float(fitrec["tau"])

    inp = compare.Inputs()
    by_motor = inp.train_by_motor
    counts = np.array([len(y) for y, _ in by_motor], dtype=int)

    # ---------------------------------------------------------------- section 2: shrinkage
    per_motor = []
    for (y, c) in by_motor:
        post = hierarchy.posterior_motor_shape(y, c, mu, tau)
        eta_np, se_np, at_bound = _nopool_eta(y, c)
        b = (tau * tau) / (tau * tau + se_np * se_np) if se_np is not None else None
        per_motor.append({
            "nEvents": int(len(y)),
            "etaPosteriorMean": post["eta_mean"],
            "etaPosteriorSD": post["eta_sd"],
            "kPosteriorExpOfMean": post["k_mean_exp"],
            "etaNoPoolMLE": eta_np,
            "etaNoPoolSE": se_np,
            "noPoolAtBound": at_bound,
            "weightOnData_B": b,
            "shrinkageTowardPopulation_1minusB": (1.0 - b) if b is not None else None,
        })

    post_means = np.array([p["etaPosteriorMean"] for p in per_motor])
    post_sds = np.array([p["etaPosteriorSD"] for p in per_motor])
    nopool = np.array([p["etaNoPoolMLE"] for p in per_motor])
    ses = np.array([p["etaNoPoolSE"] for p in per_motor if p["etaNoPoolSE"] is not None])
    bs = np.array([p["weightOnData_B"] for p in per_motor if p["weightOnData_B"] is not None])

    # empirical shrinkage: how far posterior means travel from mu relative to no-pooling
    denom = nopool - mu
    ok = np.abs(denom) > 1e-9
    travel = (post_means[ok] - mu) / denom[ok]

    shrinkage = {
        "populationMu": mu,
        "populationTau": tau,
        "posteriorMeanEta": {"sd": float(np.std(post_means, ddof=1)),
                             "min": float(post_means.min()), "max": float(post_means.max()),
                             "range": float(post_means.max() - post_means.min()),
                             "mean": float(post_means.mean())},
        "posteriorSDEta": {"mean": float(post_sds.mean()), "min": float(post_sds.min()),
                           "max": float(post_sds.max())},
        "noPoolEta": {"sd": float(np.std(nopool, ddof=1)), "min": float(nopool.min()),
                      "max": float(nopool.max()), "mean": float(nopool.mean()),
                      "nAtBound": int(sum(1 for p in per_motor if p["noPoolAtBound"]))},
        "noPoolSE": {"mean": float(ses.mean()), "median": float(np.median(ses)),
                     "min": float(ses.min()), "max": float(ses.max()), "n": int(len(ses))},
        "weightOnData_B": {"mean": float(bs.mean()), "median": float(np.median(bs)),
                           "min": float(bs.min()), "max": float(bs.max())},
        "shrinkageTowardPopulation_1minusB": {
            "mean": float((1 - bs).mean()), "median": float(np.median(1 - bs)),
            "min": float((1 - bs).min()), "max": float((1 - bs).max())},
        "empiricalTravelFraction_postMinusMu_over_noPoolMinusMu": {
            "mean": float(travel.mean()), "median": float(np.median(travel)),
            "min": float(travel.min()), "max": float(travel.max()), "n": int(len(travel))},
        "sdRatio_posteriorOverNoPool": float(np.std(post_means, ddof=1)
                                             / np.std(nopool, ddof=1)),
        "posteriorSDvsPriorSD_meanRatio": float(post_sds.mean() / tau),
    }

    # ------------------------------------------- section 3: heterogeneity vs sampling noise
    q = np.percentile(counts, [0, 25, 50, 75, 100])
    events_per_motor = {
        "nMotors": int(len(counts)), "nEvents": int(counts.sum()),
        "min": int(q[0]), "q25": float(q[1]), "median": float(q[2]), "q75": float(q[3]),
        "max": int(q[4]), "mean": float(counts.mean()),
        "nMotorsWithAtMost5Events": int(np.sum(counts <= 5)),
        "nMotorsWithAtMost10Events": int(np.sum(counts <= 10)),
    }

    # tau -> 0 null generator: one shared shape, pooled MLE, each motor keeps its own n_m
    y_all = np.concatenate([y for y, _ in by_motor])
    c_all = np.zeros(len(y_all), dtype=bool)
    rp = optimize.minimize_scalar(lambda lk: _motor_nll(lk, y_all, c_all), bounds=LOGK_BOUNDS,
                                  method="bounded", options={"xatol": 1e-10})
    k_null = math.exp(float(rp.x))

    observed_sd = float(np.std(nopool, ddof=1))
    rng = np.random.default_rng(NULL_SEED)
    null_sds = np.empty(N_NULL_REP, dtype=np.float64)
    for b in range(N_NULL_REP):
        etas = np.empty(len(counts), dtype=np.float64)
        for i, n in enumerate(counts):
            ys = _weibull_mean_one_rvs(k_null, int(n), rng)
            cs = np.zeros(int(n), dtype=bool)
            e, _se, _ab = _nopool_eta(ys, cs)
            etas[i] = e
        null_sds[b] = np.std(etas, ddof=1)

    n_ge = int(np.sum(null_sds >= observed_sd))
    heterogeneity = {
        "statistic": "SD across motors of the NO-POOLING per-motor log-shape MLE (eta)",
        "observedSD": observed_sd,
        "nullGenerator": {
            "kind": "SIMULATION, not observation",
            "model": "single shared mean-one Weibull shape (the tau -> 0 limit)",
            "kNull": k_null,
            "eventsPerMotorPreserved": True,
            "nRep": N_NULL_REP, "seed": NULL_SEED,
        },
        "nullSD": {"mean": float(null_sds.mean()), "sd": float(np.std(null_sds, ddof=1)),
                   "p025": float(np.percentile(null_sds, 2.5)),
                   "median": float(np.percentile(null_sds, 50)),
                   "p975": float(np.percentile(null_sds, 97.5)),
                   "max": float(null_sds.max())},
        "nNullReplicatesAtOrAboveObserved": n_ge,
        "monteCarloTailFraction_(nGE+1)/(nRep+1)": (n_ge + 1) / (N_NULL_REP + 1),
        "excessVarianceEstimate_sq": observed_sd ** 2 - float((null_sds ** 2).mean()),
        "impliedExcessSD": (math.sqrt(observed_sd ** 2 - float((null_sds ** 2).mean()))
                            if observed_sd ** 2 > float((null_sds ** 2).mean()) else None),
        "note": ("The null calibration uses the parametric tau -> 0 generator with the pooled "
                 "MLE plugged in; it is a Monte-Carlo reference distribution, not a source-pinned "
                 "measurement. The plug-in ignores uncertainty in k_null."),
    }

    out = {
        "probe": "PROBE5_SHRINKAGE_AND_HETEROGENEITY",
        "splitBoundary": "TRAIN_ONLY (duration-only). No holdout field read.",
        "recordedFitUsed": {"mu": mu, "tau": tau, "source": str(FIT_JSON.name)},
        "shrinkage": shrinkage,
        "eventsPerMotor": events_per_motor,
        "heterogeneity": heterogeneity,
        "perMotor": per_motor,
        "wallSeconds": time.time() - t0,
    }
    dest = HERE / "results" / "motor_stack_aif" / "TAU_SHRINKAGE_PROBE5_RESULT.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print("wrote", dest)
    print("posterior eta: sd=%.10f mean_sd=%.10f  (tau=%.10f)"
          % (shrinkage["posteriorMeanEta"]["sd"], shrinkage["posteriorSDEta"]["mean"], tau))
    print("no-pool eta sd=%.10f  nAtBound=%d" % (shrinkage["noPoolEta"]["sd"],
                                                 shrinkage["noPoolEta"]["nAtBound"]))
    print("sdRatio post/nopool = %.10f" % shrinkage["sdRatio_posteriorOverNoPool"])
    print("mean B (weight on data) = %.10f ; mean shrinkage 1-B = %.10f"
          % (shrinkage["weightOnData_B"]["mean"],
             shrinkage["shrinkageTowardPopulation_1minusB"]["mean"]))
    print("events/motor: min=%d q25=%.1f med=%.1f q75=%.1f max=%d"
          % (events_per_motor["min"], events_per_motor["q25"], events_per_motor["median"],
             events_per_motor["q75"], events_per_motor["max"]))
    print("heterogeneity: observedSD=%.10f null mean=%.10f p975=%.10f nGE=%d/%d"
          % (observed_sd, heterogeneity["nullSD"]["mean"], heterogeneity["nullSD"]["p975"],
             n_ge, N_NULL_REP))
    print("wall = %.1f s" % out["wallSeconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
