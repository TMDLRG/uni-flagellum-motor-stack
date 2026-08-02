"""PROBE 5 part 1 — profile log-likelihood over tau on the real training cohort.

Duration-only. Training partition ONLY. No holdout field of any kind is read here.

At each tau on the frozen-C11-U2 grid (exp(linspace(log(1e-4), log(5.0), 61))) the population
log-likelihood is maximised over mu by bounded Brent. tau is NOT free at these points: this is a
profile, not a fit.

Reuses `hierarchy.population_log_likelihood` unchanged. Nothing is written outside
results/motor_stack_aif/TAU_PROFILE_*.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import optimize

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from motor_stack_aif import compare, fit, hazard_survival as hs, hierarchy  # noqa: E402

# Frozen C11 U2 grid, transcribed from
# audits/phase-b/b4-identifiability-robustness-runner.py::cell_C11.
GRID_N = 61
GRID_LO, GRID_HI = 1e-4, 5.0
FROZEN_C11_U2_OFFSET = 1.9207          # 0.5 * chi2_{1,0.95}; frozen for the M7 cell, NOT for this one
MU_BOUNDS = (-3.0, 3.0)
MU_XATOL = 1e-5


def main() -> int:
    t_start = time.time()
    inp = compare.Inputs()
    by_motor = inp.train_by_motor
    n_motors = len(by_motor)
    n_events = int(sum(len(y) for y, _ in by_motor))

    calls = [0]

    def neg_ll(mu: float, tau: float) -> float:
        calls[0] += 1
        try:
            return -hierarchy.population_log_likelihood(by_motor, float(mu), float(tau))
        except (hs.NonFiniteLogDensity, ValueError, OverflowError, FloatingPointError):
            return 1e12

    tau_grid = np.exp(np.linspace(math.log(GRID_LO), math.log(GRID_HI), GRID_N))
    rows = []
    for tau in tau_grid:
        r = optimize.minimize_scalar(lambda m: neg_ll(m, float(tau)), bounds=MU_BOUNDS,
                                     method="bounded", options={"xatol": MU_XATOL})
        nll = float(r.fun)
        rows.append({
            "tau": float(tau),
            "muHat": float(r.x),
            "profileNLL": nll if nll < 1e11 else None,
            "profileNLLStatus": "OK" if nll < 1e11 else "NOT_COMPUTED_INFEASIBLE",
            "muAtBound": bool(abs(float(r.x) - MU_BOUNDS[0]) < 1e-4
                              or abs(float(r.x) - MU_BOUNDS[1]) < 1e-4),
        })

    finite = [r for r in rows if r["profileNLL"] is not None]
    nll_star = min(r["profileNLL"] for r in finite)
    star = [r for r in finite if r["profileNLL"] == nll_star][0]

    # tau -> TAU_MIN limit (the non-hierarchical / single-shared-shape limit)
    at_min = rows[0]
    drop_to_min = at_min["profileNLL"] - nll_star if at_min["profileNLL"] is not None else None

    # Independent recomputation of the tau -> 0 limit: a SINGLE shared mean-one Weibull shape
    # fitted by pooling every training event. tau -> 0 collapses the hierarchy onto exactly this.
    y_all = np.concatenate([y for y, _ in by_motor])
    c_all = np.zeros(len(y_all), dtype=bool)

    def pooled_nll(log_k: float) -> float:
        k = math.exp(float(log_k))
        if not (hierarchy.K_MIN_REPRESENTABLE <= k <= hierarchy.K_MAX_REPRESENTABLE):
            return 1e12
        try:
            return -float(np.sum(hs.log_event_density(
                y_all, c_all, hs.weibull_log_hazard, hs.weibull_log_survival, k)))
        except (hs.NonFiniteLogDensity, OverflowError):
            return 1e12

    rp = optimize.minimize_scalar(pooled_nll, bounds=(math.log(0.05), math.log(5.0)),
                                  method="bounded", options={"xatol": 1e-10})
    pooled = {"k": math.exp(float(rp.x)), "nll": float(rp.fun),
              "nFreeParams": 1,
              "note": "no-pooling-free single shared shape; the tau -> 0 limit of the hierarchy"}

    # flat set under the frozen C11 U2 offset, reused DESIGN_ONLY
    thresh = nll_star + FROZEN_C11_U2_OFFSET
    flat = [r["tau"] for r in finite if r["profileNLL"] <= thresh]
    denom = math.log(GRID_HI) - math.log(GRID_LO)
    logspan_raw = (math.log(max(flat)) - math.log(min(flat))) if flat else 0.0

    out = {
        "probe": "PROBE5_TAU_PROFILE",
        "splitBoundary": "TRAIN_ONLY (duration-only). No holdout field read.",
        "cohort": {"name": "derived_eligible_1_to_8", "nTrainMotors": n_motors,
                   "nTrainEvents": n_events},
        "grid": {"n": GRID_N, "lo": GRID_LO, "hi": GRID_HI,
                 "provenance": "transcribed verbatim from frozen B4C11 cell_C11 U2 tau grid"},
        "muOptimiser": {"method": "bounded Brent", "bounds": list(MU_BOUNDS), "xatol": MU_XATOL},
        "profile": rows,
        "profileMax": {"tau": star["tau"], "muHat": star["muHat"], "nll": nll_star},
        "recordedFit": {"tau": 0.18372082607308418, "mu": -0.41607215987582913,
                        "trainNLL": 575.6701064153622,
                        "source": "results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json"},
        "tauMinLimit": {"tau": at_min["tau"], "muHat": at_min["muHat"],
                        "nll": at_min["profileNLL"], "dropFromMax": drop_to_min},
        "pooledSingleShapeCheck": pooled,
        "flatnessDESIGN_ONLY": {
            "offsetUsed": FROZEN_C11_U2_OFFSET,
            "offsetProvenance": ("frozen for the B4C11 M7 U2 cell (a DIFFERENT model and a "
                                 "DIFFERENT likelihood). Reuse here is DESIGN_ONLY and is not "
                                 "evidential."),
            "nllStar": nll_star,
            "flatThreshold": thresh,
            "flatSetTauRange": [min(flat), max(flat)] if flat else None,
            "flatLogspan_raw_natural_log": logspan_raw,
            "flatLogspan_normalized": logspan_raw / denom,
            "logspanNormalizationDenominator": denom,
            "c11U2FireRule_DESIGN_ONLY_here": "normalized logspan >= 0.50",
        },
        "tauBoundsFromFit": [fit.TAU_MIN, fit.TAU_MAX],
        "llCalls": calls[0],
        "wallSeconds": time.time() - t_start,
    }
    dest = HERE / "results" / "motor_stack_aif" / "TAU_PROFILE_PROBE5_RESULT.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    print("wrote", dest)
    print("nll* = %.10f at tau = %.6g, mu = %.10f" % (nll_star, star["tau"], star["muHat"]))
    print("tau=%.6g (TAU_MIN grid end): nll = %.10f, drop = %.10f"
          % (at_min["tau"], at_min["profileNLL"], drop_to_min))
    print("pooled single-shape k = %.10f, nll = %.10f" % (pooled["k"], pooled["nll"]))
    print("flat set (DESIGN_ONLY offset %.4f): tau in [%.6g, %.6g], normalized logspan %.6f"
          % (FROZEN_C11_U2_OFFSET, min(flat), max(flat), logspan_raw / denom))
    print("llCalls = %d, wall = %.1f s" % (calls[0], out["wallSeconds"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
