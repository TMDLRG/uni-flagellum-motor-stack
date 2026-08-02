"""PROBE 2 — power atlas for motor-equal scoring.

EVERYTHING PRODUCED HERE IS SYNTHETIC. No output of this script may ever be labelled OBSERVED.

What it does
------------
It does NOT refit any model. It simulates PER-MOTOR NLPD ARRAYS with a KNOWN injected effect and
runs the *existing* frozen paired motor-cluster bootstrap (`score.contrast_with_ci`) on them. That
isolates exactly one question: at a given motor count, per-motor dispersion, and paired-difference
consistency, what does this design RESOLVE?

Calibration to real recorded numbers
------------------------------------
Two generator constants are taken from the recorded F-side artifact, never invented:
  sigma_b  = across-motor SD (ddof=1) of `perMotorNLPD.F_MOTOR_STACK`
  mu0      = `candidate.motorEqual`
The consistency axis `rho` is the Pearson correlation between the two paired per-motor score
arrays; the real recorded contrasts sit in rho ~ [0.967, 0.9996], which is why the grid spans it.

Parameterization
----------------
  challenger_i = mu0 + sigma_b * z1_i
  ref_i        = mu0 + effect + sigma_b * (rho*z1_i + sqrt(1-rho^2)*z2_i)
  => per-motor difference d_i = ref_i - challenger_i has mean `effect` and
     SD sigma_d = sigma_b * sqrt(2 - 2*rho).
The reported contrast is S(ref) - S(challenger), the frozen convention: interval entirely above 0
=> challenger better.

Independent analytic cross-check
--------------------------------
A normal-approximation power expression that shares no code with the bootstrap is evaluated for
every cell, so a bootstrap implementation error would show up as a divergence.
"""
from __future__ import annotations

import json
import math
import pathlib
import platform
import sys
import time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from motor_stack_aif import score  # noqa: E402

FROZEN_FLOOR_NATS = 0.042            # frozen resolution floor (motor-equal half-width), NOT invented
DESIGN_ONLY_POWER_TARGET = 0.80      # DESIGN_ONLY — not an evidential threshold
BOOT_N_REP = 2000                    # matches the frozen B3 / F-side bootstrap replicate count
BASE_SEED = 20260721

F_RESULT = ROOT / "results" / "motor_stack_aif" / "F_SIDE_MOTOR_STACK_SCORING_RESULT.json"
OUT = ROOT / "results" / "motor_stack_aif" / "power_atlas.json"

N_MOTORS_GRID = [19, 30, 50, 100, 200]
EFFECT_GRID = [0.0, 1e-6, 0.005, 0.01, 0.02, 0.042, 0.08, 0.15]
RHO_GRID = [0.90, 0.97, 0.99, 0.999, 0.9999]

SIMS_SMALL = 200   # n_motors <= 50
SIMS_LARGE = 120   # n_motors in {100, 200}  (COMPUTE_BUDGET trim, MC SE reported per cell)


def normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def analytic_resolve_rate(effect: float, sigma_d: float, n: int) -> float:
    """Two-sided normal-approximation probability the 95% interval excludes 0.

    Shares no code with the bootstrap. sigma_d == 0 is the degenerate limit: any non-zero effect
    resolves with probability 1, a zero effect never does.
    """
    if sigma_d <= 0.0:
        return 1.0 if effect != 0.0 else 0.0
    se = sigma_d / math.sqrt(n)
    z = 1.959963984540054
    return normal_cdf(effect / se - z) + normal_cdf(-effect / se - z)


def analytic_mde(sigma_d: float, n: int, power: float) -> float:
    """Effect size reaching `power` two-sided at alpha=0.05 (normal approximation)."""
    z_a = 1.959963984540054
    # inverse normal cdf for `power` via bisection (no scipy dependency)
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if normal_cdf(mid) < power:
            lo = mid
        else:
            hi = mid
    z_b = 0.5 * (lo + hi)
    return (z_a + z_b) * sigma_d / math.sqrt(n)


def analytic_n_for(effect: float, sigma_d: float, power: float) -> float:
    z_a = 1.959963984540054
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if normal_cdf(mid) < power:
            lo = mid
        else:
            hi = mid
    z_b = 0.5 * (lo + hi)
    if effect <= 0.0:
        return float("inf")
    return ((z_a + z_b) * sigma_d / effect) ** 2


def materiality(effect: float) -> str:
    if effect == 0.0:
        return "NULL_NEGATIVE_CONTROL"
    if abs(effect) >= FROZEN_FLOOR_NATS:
        return "MATERIAL_AT_OR_ABOVE_FROZEN_FLOOR"
    return "IMMATERIAL_BELOW_FROZEN_FLOOR"


def run_cell(n_motors: int, effect: float, rho: float, sigma_b: float, mu0: float,
             n_sims: int, cell_seed: int, sigma_d_override: float | None = None) -> dict:
    """`sigma_d_override` bypasses the rho parameterization.

    Needed for the near-degenerate regime: at rho = 1 - 2.3e-14, `2 - 2*rho` loses ~1% of its
    value to float64 cancellation, so setting the per-motor difference SD directly is the honest
    construction. When it is used, `rho` is reported as the implied value, not the input.
    """
    if sigma_d_override is None:
        sigma_d = sigma_b * math.sqrt(max(0.0, 2.0 - 2.0 * rho))
    else:
        sigma_d = float(sigma_d_override)
        rho = 1.0 - 0.5 * (sigma_d / sigma_b) ** 2
    rng = np.random.default_rng(cell_seed)
    resolved = 0
    resolved_above = 0
    resolved_below = 0
    widths = np.empty(n_sims, dtype=np.float64)
    points = np.empty(n_sims, dtype=np.float64)
    for s in range(n_sims):
        z1 = rng.standard_normal(n_motors)
        z2 = rng.standard_normal(n_motors)
        challenger = mu0 + sigma_b * z1
        # The paired motor-cluster bootstrap statistic is mean(d[idx]) - a function of the per-motor
        # DIFFERENCE array alone. Building d directly is numerically exact at every rho, and is
        # distributionally identical to the equal-marginal correlated construction.
        ref = challenger + effect + sigma_d * z2
        res = score.contrast_with_ci(ref, challenger, n_rep=BOOT_N_REP, seed=cell_seed + 1 + s)
        widths[s] = res["width"]
        points[s] = res["pointEstimate"]
        v = res["verdict"]
        if v != "NOT_ESTABLISHED":
            resolved += 1
            if v == "RESOLVED_ABOVE":
                resolved_above += 1
            else:
                resolved_below += 1
    rate = resolved / n_sims
    mc_se = math.sqrt(max(rate * (1.0 - rate), 0.0) / n_sims)
    return {
        "nMotors": n_motors,
        "injectedEffectNats": effect,
        "consistencyRho": rho,
        "perMotorDiffSD": sigma_d,
        "nSims": n_sims,
        "resolveRate": rate,
        "resolveRateMonteCarloSE": mc_se,
        "resolvedAboveFrac": resolved_above / n_sims,
        "resolvedBelowFrac": resolved_below / n_sims,
        "meanCIWidthNats": float(widths.mean()),
        "meanCIHalfWidthNats": float(widths.mean() / 2.0),
        "medianCIHalfWidthNats": float(np.median(widths) / 2.0),
        "meanPointEstimateNats": float(points.mean()),
        # point-estimate direction only — the modal-winner / self-win analogue. A point estimate is
        # never a verdict; this is reported alongside resolveRate, never instead of it.
        "pointFavorsChallengerFrac": float((points > 0).mean()),
        "analyticResolveRate": analytic_resolve_rate(effect, sigma_d, n_motors),
        "materiality": materiality(effect),
        "cellSeed": cell_seed,
    }


def interp_threshold(xs, ys, target):
    """Smallest x on the grid where y crosses `target`, linearly interpolated. None if never."""
    for i in range(1, len(xs)):
        if ys[i - 1] < target <= ys[i]:
            x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
            if y1 == y0:
                return float(x1)
            return float(x0 + (target - y0) * (x1 - x0) / (y1 - y0))
    if ys and ys[0] >= target:
        return float(xs[0])
    return None


def main() -> None:
    t0 = time.perf_counter()
    fres = json.loads(F_RESULT.read_text(encoding="utf-8"))
    per_motor = {k: np.asarray(v, dtype=np.float64) for k, v in fres["perMotorNLPD"].items()}
    f_arr = per_motor["F_MOTOR_STACK"]
    sigma_b = float(f_arr.std(ddof=1))
    mu0 = float(fres["candidate"]["motorEqual"])

    ext = json.loads((ROOT / "results" / "motor_stack_aif"
                      / "M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json").read_text(encoding="utf-8"))
    per_motor_ext = {k: np.asarray(v, dtype=np.float64)
                     for k, v in ext["perMotorNLPD"].items()}

    def anchor(name, arr, src):
        diff = arr - f_arr
        sd = float(diff.std(ddof=1))
        se = sd / math.sqrt(len(diff)) if sd > 0 else 0.0
        return {
            "reference": name,
            "challenger": "F_MOTOR_STACK",
            "meanPerMotorDiffNats": float(diff.mean()),
            "perMotorDiffSD": sd,
            "impliedEqualMarginalRho": float(1.0 - 0.5 * (sd / sigma_b) ** 2),
            "pearsonRhoWithCandidate": float(np.corrcoef(arr, f_arr)[0, 1]),
            "effectOverStandardError": float(diff.mean() / se) if se > 0 else None,
            "nPositivePerMotorDiffs": int((diff > 0).sum()),
            "nMotors": int(len(diff)),
            "materiality": materiality(abs(float(diff.mean()))),
            "provenance": src,
        }

    real_anchors = []
    for name, arr in sorted(per_motor.items()):
        if name.startswith("F_MOTOR_STACK"):
            continue
        real_anchors.append(anchor(
            name, arr, "RECORDED artifact F_SIDE_MOTOR_STACK_SCORING_RESULT.json perMotorNLPD"))
    for name, arr in sorted(per_motor_ext.items()):
        if name.startswith("F_MOTOR_STACK"):
            continue
        real_anchors.append(anchor(
            name, arr, "RECORDED artifact M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json perMotorNLPD"))

    cells = []
    for rho in RHO_GRID:
        for n_motors in N_MOTORS_GRID:
            n_sims = SIMS_SMALL if n_motors <= 50 else SIMS_LARGE
            for effect in EFFECT_GRID:
                seed = BASE_SEED + int(round(rho * 1e6)) * 1000 + n_motors * 100 \
                    + int(round(effect * 1e7)) % 97
                cells.append(run_cell(n_motors, effect, rho, sigma_b, mu0, n_sims, seed))

    # --- derived design answers -------------------------------------------------------------
    mde_at_19 = []
    for rho in RHO_GRID:
        sub = sorted([c for c in cells if c["consistencyRho"] == rho and c["nMotors"] == 19],
                     key=lambda c: c["injectedEffectNats"])
        xs = [c["injectedEffectNats"] for c in sub]
        ys = [c["resolveRate"] for c in sub]
        sigma_d = sigma_b * math.sqrt(2.0 - 2.0 * rho)
        emp = interp_threshold(xs, ys, DESIGN_ONLY_POWER_TARGET)
        mde_at_19.append({
            "consistencyRho": rho,
            "perMotorDiffSD": sigma_d,
            "empiricalMDE80Nats": emp,
            "empiricalMDE80Status": ("INTERPOLATED_ON_GRID" if emp is not None
                                     else "ABOVE_GRID_MAX_0.15 — NOT_COMPUTED"),
            "analyticMDE80Nats": analytic_mde(sigma_d, 19, DESIGN_ONLY_POWER_TARGET),
            "materialityOfAnalyticMDE": materiality(analytic_mde(sigma_d, 19,
                                                                 DESIGN_ONLY_POWER_TARGET)),
            "powerTargetLabel": "DESIGN_ONLY — 0.80 is a design convention, not evidential",
        })

    n_for_floor = []
    for rho in RHO_GRID:
        sub = sorted([c for c in cells if c["consistencyRho"] == rho
                      and c["injectedEffectNats"] == FROZEN_FLOOR_NATS],
                     key=lambda c: c["nMotors"])
        xs = [c["nMotors"] for c in sub]
        ys = [c["resolveRate"] for c in sub]
        sigma_d = sigma_b * math.sqrt(2.0 - 2.0 * rho)
        emp = interp_threshold(xs, ys, DESIGN_ONLY_POWER_TARGET)
        n_for_floor.append({
            "consistencyRho": rho,
            "perMotorDiffSD": sigma_d,
            "effectNats": FROZEN_FLOOR_NATS,
            "empiricalNMotorsFor80pct": emp,
            "empiricalStatus": ("INTERPOLATED_ON_GRID" if emp is not None
                                else "ABOVE_GRID_MAX_200_MOTORS — NOT_COMPUTED"),
            "analyticNMotorsFor80pct": analytic_n_for(FROZEN_FLOOR_NATS, sigma_d,
                                                      DESIGN_ONLY_POWER_TARGET),
            "powerTargetLabel": "DESIGN_ONLY — 0.80 is a design convention, not evidential",
        })

    # --- analytic sizing at each REAL recorded per-motor dispersion ----------------------------
    # Analytic only (normal approximation, no bootstrap): zero extra compute, and it answers
    # "what would this SPECIFIC recorded comparison need?" rather than a grid abstraction.
    per_anchor_sizing = []
    for a in real_anchors:
        sd = a["perMotorDiffSD"]
        mde = analytic_mde(sd, 19, DESIGN_ONLY_POWER_TARGET)
        per_anchor_sizing.append({
            "reference": a["reference"],
            "recordedPerMotorDiffSD": sd,
            "recordedMeanDiffNats": a["meanPerMotorDiffNats"],
            "analyticMDE80At19Motors": mde,
            "mde80IsAboveFrozenFloor": bool(mde > FROZEN_FLOOR_NATS),
            "analyticMotorsFor80pctAtFrozenFloor": analytic_n_for(
                FROZEN_FLOOR_NATS, sd, DESIGN_ONLY_POWER_TARGET),
            "method": "normal approximation, alpha=0.05 two-sided, power target 0.80 DESIGN_ONLY; "
                      "shares no code with the bootstrap",
        })

    # --- D10 demonstration: near-degenerate consistency, microscopic effect --------------------
    m7 = per_motor_ext["M7_HIERARCHICAL_MOTOR"]
    m7_diff = m7 - f_arr
    d10_effect = float(m7_diff.mean())
    d10_sigma_d = float(m7_diff.std(ddof=1))
    d10 = run_cell(19, d10_effect, float("nan"), sigma_b, mu0, 400, BASE_SEED + 777,
                   sigma_d_override=d10_sigma_d)
    d10["note"] = (
        "SYNTHETIC. The injected effect and the per-motor difference SD are set to the RECORDED "
        "M7-vs-candidate values so the regime is the real one; every resolve/width number below "
        "is simulated and is NOT the recorded M7 result."
    )
    d10["injectedEffectSource"] = ("mean of (M7_HIERARCHICAL_MOTOR - F_MOTOR_STACK) per-motor "
                                   "NLPD in M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json")
    d10["perMotorDiffSDSource"] = "std(ddof=1) of the same recorded difference array"
    d10["d10Reading"] = (
        "Resolve-rate and materiality are SEPARATE axes. A cell can resolve at high rate while the "
        "injected effect sits far below the frozen 0.042-nat floor: consistency, not magnitude, is "
        "what the paired motor-cluster bootstrap responds to."
    )

    # --- D10 counterfactual: same microscopic effect, ordinary consistency ---------------------
    d10_cf = run_cell(19, d10_effect, float("nan"), sigma_b, mu0, 200, BASE_SEED + 778,
                      sigma_d_override=float(
                          (per_motor["M3_TWO_TIMESCALE"] - f_arr).std(ddof=1)))
    d10_cf["note"] = (
        "SYNTHETIC negative counterpart: the SAME microscopic effect at the per-motor difference "
        "dispersion recorded for M3_TWO_TIMESCALE. Isolates consistency as the operative variable."
    )

    # --- negative control roll-up -------------------------------------------------------------
    null_cells = [c for c in cells if c["injectedEffectNats"] == 0.0]
    null_rates = [c["resolveRate"] for c in null_cells]
    by_n = []
    for n_motors in N_MOTORS_GRID:
        sub = [c for c in null_cells if c["nMotors"] == n_motors]
        rates = [c["resolveRate"] for c in sub]
        tot_sims = sum(c["nSims"] for c in sub)
        pooled = float(np.average(rates, weights=[c["nSims"] for c in sub]))
        by_n.append({
            "nMotors": n_motors,
            "pooledFalseResolveRate": pooled,
            "pooledSims": tot_sims,
            "pooledMonteCarloSE": math.sqrt(pooled * (1 - pooled) / tot_sims),
            "excessOverNominal": pooled - 0.05,
        })
    negative_control = {
        "description": "effect == 0 cells. The frozen percentile motor-cluster bootstrap at "
                       "alpha=0.05 should falsely resolve ~5% of the time. Excess over nominal is "
                       "an anti-conservatism diagnostic of the ASSAY, measured on SYNTHETIC data.",
        "nCells": len(null_cells),
        "meanResolveRate": float(np.mean(null_rates)),
        "minResolveRate": float(np.min(null_rates)),
        "maxResolveRate": float(np.max(null_rates)),
        "nominalAlpha": 0.05,
        "byMotorCount": by_n,
    }

    out = {
        "schema": "power_atlas/v1",
        "probe": "PROBE 2 — POWER ATLAS FOR MOTOR-EQUAL SCORING",
        "truthLabel": "SYNTHETIC — every number under `cells`, `derived`, `d10Demonstration` and "
                      "`negativeControl` is simulated. Nothing here is OBSERVED. This probe is "
                      "BUILDER-SUPPORT: it moves no P-level and creates no claim.",
        "generatedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "bootstrapUnderTest": "motor_stack_aif.score.contrast_with_ci (frozen implementation, "
                              "resampling unit = MOTOR, percentile interval)",
        "bootstrapReplicates": BOOT_N_REP,
        "intervalType": "percentile — BCa is NOT computed here (D7: BCa exists only for the 48 "
                        "frozen B3 contrasts)",
        "contrastConvention": "contrast = S(reference) - S(challenger); interval entirely above 0 "
                              "=> challenger better",
        "calibration": {
            "sigmaBAcrossMotorSD": sigma_b,
            "sigmaBSource": "std(ddof=1) of perMotorNLPD.F_MOTOR_STACK in "
                            "F_SIDE_MOTOR_STACK_SCORING_RESULT.json (19 motors)",
            "mu0": mu0,
            "mu0Source": "candidate.motorEqual in F_SIDE_MOTOR_STACK_SCORING_RESULT.json",
            "realHoldoutMotors": 19,
            "realHoldoutEvents": 233,
            "eventsPerMotorObserved": {"min": 3, "median": 7, "max": 50, "mean": 233 / 19,
                                       "source": "_bridge.frozen_cohort().holdout_by_motor"},
        },
        "realAnchors": real_anchors,
        "thresholds": {
            "frozenResolutionFloorNats": FROZEN_FLOOR_NATS,
            "frozenResolutionFloorProvenance": "BCa half-width of the narrowest frozen B3 "
                                               "contrast M4_MIXTURE_K3 — FROZEN, not invented",
            "powerTarget": DESIGN_ONLY_POWER_TARGET,
            "powerTargetLabel": "DESIGN_ONLY — introduced for design sizing, NOT evidential",
        },
        "axes": {
            "nMotors": N_MOTORS_GRID,
            "injectedEffectNats": EFFECT_GRID,
            "consistencyRho": RHO_GRID,
            "eventsPerMotor": "NOT_SWEPT — held at the observed holdout allocation. Sweeping it "
                              "would require refitting every model on subsampled events, which is "
                              "NOT_RUN — COMPUTE_BUDGET.",
            "modelFamily": "NOT_SWEPT — the atlas is generator-agnostic by construction: a model "
                           "family enters only through (sigmaB, rho, effect), and the real "
                           "(rho, effect) of all six recorded F-side pairs are listed in "
                           "`realAnchors`.",
            "generator": "SYNTHETIC_GAUSSIAN_PAIRED_PER_MOTOR_SCORES",
        },
        "cells": cells,
        "derived": {
            "detectableEffectAt19Motors": mde_at_19,
            "motorsNeededForFrozenFloorEffect": n_for_floor,
            "perRealAnchorSizing": per_anchor_sizing,
        },
        "d10Demonstration": d10,
        "d10Counterfactual": d10_cf,
        "negativeControl": negative_control,
        "notRun": [
            {"item": "events-per-motor sweep", "status": "NOT_RUN — COMPUTE_BUDGET",
             "reason": "requires refitting every model family on subsampled per-motor event sets; "
                       "two long runs are in flight and the fence caps this probe at ~2 minutes."},
            {"item": "BCa intervals for any atlas cell", "status": "NOT_COMPUTED",
             "reason": "D7: BCa companions exist only for the 48 frozen B3 contrasts. Computing a "
                       "BCa here would invent a comparison that has no frozen counterpart."},
            {"item": "non-Gaussian per-motor score generators (heavy-tailed, skewed)",
             "status": "NOT_RUN — COMPUTE_BUDGET",
             "reason": "the recorded per-motor NLPD arrays are 19 points, too few to fit a "
                       "defensible non-Gaussian shape; a shape assumption would be invented."},
            {"item": "resolve-rate at n_motors between 200 and the analytic requirement",
             "status": "NOT_RUN — grid capped at 200 motors",
             "reason": "cells above the grid report the analytic requirement only, labelled as "
                       "such."},
        ],
        "runtimeSeconds": None,
    }
    out["runtimeSeconds"] = time.perf_counter() - t0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, sort_keys=False), encoding="utf-8")
    print("WROTE %s" % OUT)
    print("sigma_b (across-motor SD of F per-motor NLPD, ddof=1) = %.10f" % sigma_b)
    print("cells = %d   runtime = %.1f s" % (len(cells), out["runtimeSeconds"]))
    print("negative control (effect=0): mean resolve rate %.4f  range [%.4f, %.4f]"
          % (negative_control["meanResolveRate"], negative_control["minResolveRate"],
             negative_control["maxResolveRate"]))
    print("--- resolve rate at n=19 ---")
    for rho in RHO_GRID:
        row = [c for c in cells if c["consistencyRho"] == rho and c["nMotors"] == 19]
        row.sort(key=lambda c: c["injectedEffectNats"])
        print("rho=%-8g sd_d=%.5f  " % (rho, row[0]["perMotorDiffSD"])
              + "  ".join("%g:%.3f(a%.3f)" % (c["injectedEffectNats"], c["resolveRate"],
                                              c["analyticResolveRate"]) for c in row))
    print("--- MDE80 at 19 motors (DESIGN_ONLY target) ---")
    for r in mde_at_19:
        print("rho=%-8g emp=%s analytic=%.6f" % (r["consistencyRho"],
                                                 r["empiricalMDE80Nats"], r["analyticMDE80Nats"]))
    print("--- motors needed for a 0.042-nat effect at 80%% (DESIGN_ONLY) ---")
    for r in n_for_floor:
        print("rho=%-8g emp=%s analytic=%.2f" % (r["consistencyRho"],
                                                 r["empiricalNMotorsFor80pct"],
                                                 r["analyticNMotorsFor80pct"]))
    print("--- analytic sizing at each RECORDED per-motor dispersion (n=19) ---")
    for r in per_anchor_sizing:
        print("%-32s sd_d=%.6e  MDE80=%.6f  nFor0.042=%.2f"
              % (r["reference"], r["recordedPerMotorDiffSD"], r["analyticMDE80At19Motors"],
                 r["analyticMotorsFor80pctAtFrozenFloor"]))
    print("--- negative control by motor count (nominal 0.05) ---")
    for r in by_n:
        print("n=%-4d falseResolve=%.4f +/- %.4f  (excess %+.4f, %d sims)"
              % (r["nMotors"], r["pooledFalseResolveRate"], r["pooledMonteCarloSE"],
                 r["excessOverNominal"], r["pooledSims"]))
    print("--- D10 cell (M7-calibrated): effect=%.6e sd_d=%.6e n=19 -> resolveRate %.4f "
          "(analytic %.4f), meanHalfWidth %.3e"
          % (d10_effect, d10_sigma_d, d10["resolveRate"], d10["analyticResolveRate"],
             d10["meanCIHalfWidthNats"]))
    print("--- D10 counterfactual (same effect, M3 dispersion): resolveRate %.4f, sd_d=%.6e"
          % (d10_cf["resolveRate"], d10_cf["perMotorDiffSD"]))
    print("--- F per-motor array cross-file agreement: max|diff| = %.3e"
          % float(np.max(np.abs(per_motor_ext["F_MOTOR_STACK"] - f_arr))))


if __name__ == "__main__":
    main()
