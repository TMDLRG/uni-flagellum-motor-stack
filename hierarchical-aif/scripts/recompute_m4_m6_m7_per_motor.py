"""Recompute per-motor held-out NLPD arrays for M4, M6 and M7, and contrast them against the
F-side motor-stack candidate under the SAME paired motor-cluster bootstrap.

WHY THIS EXISTS
---------------
The F-side scoring run (H-AIF-G7) could only contrast the candidate against models whose
per-motor arrays it could construct. The frozen B3 artifact stores ONLY AGGREGATED scores, so
`M4_MIXTURE_K3`, `M6_SEMI_MARKOV_STATE_DEPENDENT` and `M7_HIERARCHICAL_MOTOR` were left
uncontrasted and the gap was recorded as a limitation in
`reports/F-SIDE-MOTOR-STACK-SCORING-REPORT.md` section 8:

    "M4 and M6 both out-score the F-side model on point estimate and neither has been
     contrasted against it under a CI-bound test."

This closes that gap. It needs NO new data, NO refitting, and touches NO held-out mark channel.

POST-HOC STATUS — DECLARED, NOT HIDDEN
--------------------------------------
The pre-registered F-side scoring protocol named its competitor set in advance:
CONTROL_CURRENT (M3) + M0/M1/M2/M5/M8. **M4, M6 and M7 were NOT in that set.** This extension is
therefore **POST_HOC**: the decision to add these three was taken after seeing that the candidate
ranked 3rd of 7 there and 5th of 9 on the published leaderboard.

What that does and does not compromise:
  - There is NO researcher degree of freedom in the numbers. The models, their fitted parameters,
    the split, the scoring rule, the aggregation, the bootstrap seed and the interval type are all
    FROZEN. Nothing here was chosen to produce a result.
  - What IS post-hoc is the SELECTION of which comparisons to run, and therefore the family size.
    The family grows from 6 contrasts to 9, which inflates family-wise error.
  - So a Bonferroni-adjusted companion interval is reported alongside the frozen nominal 95%
    interval. The frozen convention uses the nominal interval for its verdict; the adjusted one is
    reported as a SENSITIVITY and any contrast that survives only nominally is labelled as such.

These verdicts are `POST_HOC_EXPLORATORY` and may not be reported with the same standing as the
pre-registered contrasts.

MANDATORY ORACLE GATE
---------------------
Every recomputed per-motor array must reproduce its PUBLISHED motor-equal aggregate. B3 stores no
per-motor arrays, so without this check the recomputation is unvalidated. The script HALTS on
failure and emits no verdict.

D5: duration channel only. `nextStateN`/`direction`/`jump` are never requested.
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, score, status  # noqa: E402

COHORT_ID = "derived_eligible_1_to_8"
TARGETS = ["M4_MIXTURE_K3", "M6_SEMI_MARKOV_STATE_DEPENDENT", "M7_HIERARCHICAL_MOTOR"]
N_BOOT = 2000
BOOT_SEED = 20260717          # same seed as the F-side scoring run
ALPHA_NOMINAL = 0.05
FAMILY_SIZE = 9               # 6 pre-registered + 3 added here
ORACLE_TOL = 1e-12

# Corrected motor-equal resolution floor (BCa half-width of the narrowest frozen B3 contrast,
# M4_MIXTURE_K3 at 0.042070). A contrast whose whole interval lies inside +/- this is
# SCIENTIFICALLY NULL no matter what the CI says. See D10.
RESOLUTION_FLOOR_NATS = 0.042

FSIDE_RESULT = (HERE.parent / "results" / "motor_stack_aif"
                / "F_SIDE_MOTOR_STACK_SCORING_RESULT.json")
OUT = (HERE.parent / "results" / "motor_stack_aif"
       / "M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json")


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def scoring_params_from_frozen(b3, model_id: str, rec: dict):
    """Rebuild the scoring-parameter object the frozen runner would pass.

    The frozen `scoring_params()` reads keys that the RESULT JSON does not all carry verbatim:
      - M4 stores `canonical` in the result; the runner's scoring dict is
        {"rates": canonical.rates, "weights": canonical.weights}  (runner line 599).
      - M6 params arrive from JSON with STRING state keys and must be re-keyed to int, because
        the runner indexes `params[int(cohort.holdout_state[i])]`.
      - M7 uses [kTau.k, kTau.tau].
    Every reconstruction is validated by the oracle gate below.
    """
    if model_id == "M4_MIXTURE_K3":
        canon = rec["canonical"]
        return {"rates": list(canon["rates"]), "weights": list(canon["weights"])}
    if model_id == "M6_SEMI_MARKOV_STATE_DEPENDENT":
        return {int(k): float(v) for k, v in rec["params"].items()}
    if model_id == "M7_HIERARCHICAL_MOTOR":
        return [rec["kTau"]["k"], rec["kTau"]["tau"]]
    raise ValueError(model_id)


def main():
    b3 = _bridge.b3()
    coh = _bridge.frozen_cohort(name=COHORT_ID)
    b3res = _bridge.b3_result()
    fitted = b3res["cohorts"][COHORT_ID]["fitted"]
    published = b3res["cohorts"][COHORT_ID]["scores"]

    if not FSIDE_RESULT.exists():
        raise SystemExit("ABORT: F-side scoring result missing: %s" % FSIDE_RESULT)
    fside = json.loads(FSIDE_RESULT.read_text(encoding="utf-8"))

    motor_order = list(coh.holdout_motors)
    if fside["motorOrder"] != motor_order:
        raise SystemExit("ABORT: motor order differs between the F-side result and the cohort; "
                         "a paired contrast would be misaligned.")
    f_per_motor = np.asarray(fside["perMotorNLPD"]["F_MOTOR_STACK"], dtype=np.float64)
    if len(f_per_motor) != len(motor_order):
        raise SystemExit("ABORT: F-side per-motor array length mismatch.")

    out = {
        "schema": "M4-M6-M7-PER-MOTOR-CONTRASTS/1",
        "status": "POST_HOC_COVERAGE_EXTENSION",
        "postHocDeclaration": (
            "M4, M6 and M7 were NOT in the pre-registered F-side competitor set "
            "(protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md section 4). The decision to add "
            "them was taken AFTER seeing the candidate rank 3rd of 7 there. The numbers carry no "
            "researcher degree of freedom - models, fits, split, rule, seed and interval type are "
            "all frozen - but the SELECTION of comparisons is post-hoc and the family grew from 6 "
            "to 9 contrasts. Verdicts here are POST_HOC_EXPLORATORY and do not carry "
            "pre-registered standing."),
        "closesGap": ("reports/F-SIDE-MOTOR-STACK-SCORING-REPORT.md section 8: M4 and M6 "
                      "out-score the candidate on point estimate and were never contrasted."),
        "cohort": COHORT_ID,
        "channel": "DURATION_ONLY - nextStateN/direction/jump never requested (D5)",
        "scale": "SECONDS (normalised-y NLPD + log scale_N[state]), matching frozen B3",
        "aggregation": "MOTOR_EQUAL; experimental unit is the MOTOR",
        "nHoldoutMotors": len(motor_order),
        "motorOrder": motor_order,
        "consumesB3ResultSha256": _sha256_file(_bridge.B3_RESULT),
        "consumesFSideResultSha256": _sha256_file(FSIDE_RESULT),
        "bootstrap": {"nRep": N_BOOT, "seed": BOOT_SEED, "resamplingUnit": "MOTOR",
                      "intervalType": "percentile",
                      "note": "same seed and convention as the F-side scoring run"},
        "familySize": FAMILY_SIZE,
        "floorPolicy": "NO_FLOOR - a non-finite log density HALTS (frozen B3 policy)",
        "oracleGate": {"tolerance": ORACLE_TOL, "checks": []},
        "perMotorNLPD": {"F_MOTOR_STACK": f_per_motor.tolist()},
        "motorEqualNLPD": {"F_MOTOR_STACK": float(np.mean(f_per_motor))},
        "contrasts": {},
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "platform": platform.platform()},
    }

    # ---------------- recompute + oracle gate ----------------
    per_motor_by_model = {}
    for mid in TARGETS:
        params = scoring_params_from_frozen(b3, mid, fitted[mid])
        pe = b3.nlpd_per_event(mid, params, coh)          # frozen scorer, seconds scale
        agg = b3.aggregate_motor_equal(pe, coh)           # frozen aggregator
        pm = np.asarray(agg["perMotor"], dtype=np.float64)
        if not np.all(np.isfinite(pm)):
            raise SystemExit("ABORT: non-finite per-motor NLPD for %s; NO FLOOR is applied." % mid)
        per_motor_by_model[mid] = pm

        pub = published[mid]["NLPD_motor_equal"]["motorEqual"]
        residual = float(agg["motorEqual"] - pub)
        chk = {"model": mid, "publishedMotorEqual": pub,
               "recomputedMotorEqual": float(agg["motorEqual"]),
               "residual": residual, "absResidual": abs(residual),
               "pass": abs(residual) <= ORACLE_TOL,
               "publishedEventPooled": published[mid]["NLPD_motor_equal"]["eventPooled"],
               "recomputedEventPooled": float(agg["eventPooled"])}
        out["oracleGate"]["checks"].append(chk)
        out["perMotorNLPD"][mid] = pm.tolist()
        out["motorEqualNLPD"][mid] = float(agg["motorEqual"])
        print("%-32s published=%.16f recomputed=%.16f residual=%r  %s"
              % (mid, pub, agg["motorEqual"], residual, "PASS" if chk["pass"] else "FAIL"),
              flush=True)

    failed = [c["model"] for c in out["oracleGate"]["checks"] if not c["pass"]]
    out["oracleGate"]["status"] = "FAIL" if failed else "PASS"
    if failed:
        out["oracleGate"]["failedModels"] = failed
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n",
                       encoding="utf-8", newline="\n")
        raise SystemExit(
            "HALT: oracle gate FAILED for %r. The recomputed per-motor arrays do not reproduce "
            "the published aggregates, so the scale/param reconstruction is wrong. No verdict is "
            "emitted. Partial diagnostics written to %s" % (failed, OUT))

    # ---------------- paired contrasts vs the F-side candidate ----------------
    # convention: contrast = S(reference) - S(F_MOTOR_STACK); above 0 => candidate better
    z_adj = 1.0 - (ALPHA_NOMINAL / FAMILY_SIZE)     # Bonferroni companion level
    for mid in TARGETS:
        ref = per_motor_by_model[mid]
        c = score.contrast_with_ci(ref, f_per_motor, n_rep=N_BOOT, seed=BOOT_SEED,
                                   alpha=ALPHA_NOMINAL)
        # Bonferroni companion on the SAME bootstrap draws
        d = score.motor_cluster_bootstrap(f_per_motor, ref, n_rep=N_BOOT, seed=BOOT_SEED)
        a_adj = ALPHA_NOMINAL / FAMILY_SIZE
        lo_adj = float(np.percentile(d, 100 * a_adj / 2))
        hi_adj = float(np.percentile(d, 100 * (1 - a_adj / 2)))
        c["reference"] = mid
        c["challenger"] = "F_MOTOR_STACK"
        c["role"] = "ADVERSARY_POST_HOC"
        c["contrastDefinition"] = "S(%s) - S(F_MOTOR_STACK), SECONDS scale" % mid
        c["bonferroniCompanion"] = {
            "familySize": FAMILY_SIZE, "level": z_adj, "interval": [lo_adj, hi_adj],
            "verdict": status.verdict_from_ci(lo_adj, hi_adj, threshold=0.0),
            "note": ("SENSITIVITY ONLY. The frozen convention decides on the nominal 95% "
                     "interval. This companion exists because the comparison family grew "
                     "post-hoc from 6 to 9.")}
        c["survivesBonferroni"] = (c["bonferroniCompanion"]["verdict"] == c["verdict"]
                                   and c["verdict"] != "NOT_ESTABLISHED")

        # ---- D10 minimum-effect-size guard --------------------------------------------------
        # The frozen CI rule has NO practical-significance floor: a paired motor-cluster
        # bootstrap resolves an ARBITRARILY SMALL difference if its sign is consistent across
        # motors. That is statistically correct and scientifically useless. The frozen verdict is
        # reported VERBATIM and never altered; this adds the reading that must accompany it.
        lo, hi = c["interval"]
        inside_floor = max(abs(lo), abs(hi)) < RESOLUTION_FLOOR_NATS
        point_below_floor = abs(c["pointEstimate"]) < RESOLUTION_FLOOR_NATS
        if inside_floor:
            reading = "SCIENTIFICALLY_NULL"
            why = ("the ENTIRE interval lies inside +/-%.3f nats, the corrected motor-equal "
                   "resolution floor, so no scientifically material difference exists in either "
                   "direction" % RESOLUTION_FLOOR_NATS)
        elif point_below_floor:
            reading = "SUB_FLOOR_EFFECT"
            why = ("the point estimate %.3e nats is below the %.3f-nat resolution floor; any "
                   "CI-bound resolution here rests on CONSISTENCY of sign across motors, not on "
                   "effect magnitude" % (c["pointEstimate"], RESOLUTION_FLOOR_NATS))
        else:
            reading = "MATERIAL"
            why = "the point estimate exceeds the resolution floor"
        c["scientificReading"] = {
            "classification": reading,
            "why": why,
            "effectNats": abs(c["pointEstimate"]),
            "resolutionFloorNats": RESOLUTION_FLOOR_NATS,
            "floorToEffectRatio": (RESOLUTION_FLOOR_NATS / abs(c["pointEstimate"])
                                   if c["pointEstimate"] else None),
            "frozenVerdictUnaltered": c["verdict"],
        }
        c["reportableAsAWin"] = (c["verdict"] == "RESOLVED_ABOVE" and reading == "MATERIAL")
        if c["verdict"] != "NOT_ESTABLISHED" and reading != "MATERIAL":
            c["WARNING"] = (
                "STATISTICALLY RESOLVED BUT SCIENTIFICALLY NULL. The frozen CI rule excluded 0, "
                "but the effect is %.3e nats against a %.3f-nat floor. This MUST NOT be reported "
                "as one model beating another. See D10." % (abs(c["pointEstimate"]),
                                                            RESOLUTION_FLOOR_NATS))
        c["halfWidth"] = (c["interval"][1] - c["interval"][0]) / 2.0
        c["halfWidthBelongsTo"] = ("the PERCENTILE interval in `interval` (D7: the frozen B3 "
                                   "`width` field was the percentile companion while verdicts "
                                   "used BCa)")
        out["contrasts"][mid] = c
        print("%-32s point=%+.6e interval=[%+.6e, %+.6e] %-16s %s"
              % (mid, c["pointEstimate"], c["interval"][0], c["interval"][1],
                 c["verdict"], c["scientificReading"]["classification"]), flush=True)
        if "WARNING" in c:
            print("    ** %s" % c["WARNING"], flush=True)

    # ---------------- combined leaderboard ----------------
    board = dict(fside["motorEqualNLPD"])
    board.pop("F_MOTOR_STACK__JOINT_PER_MOTOR", None)
    for mid in TARGETS:
        board[mid] = out["motorEqualNLPD"][mid]
    out["combinedLeaderboardMotorEqual"] = [
        {"model": m, "motorEqual": v} for m, v in sorted(board.items(), key=lambda kv: kv[1])]
    out["candidateRank"] = 1 + [r["model"] for r in out["combinedLeaderboardMotorEqual"]].index(
        "F_MOTOR_STACK")
    out["nModelsRanked"] = len(out["combinedLeaderboardMotorEqual"])

    resolved_below = [m for m, c in out["contrasts"].items() if c["verdict"] == "RESOLVED_BELOW"]
    out["anyAdversaryResolvedBelow"] = resolved_below
    out["materialWins"] = [m for m, c in out["contrasts"].items() if c.get("reportableAsAWin")]
    out["statisticallyResolvedButNull"] = [
        m for m, c in out["contrasts"].items() if "WARNING" in c]
    out["d10Note"] = (
        "D10_NO_MINIMUM_EFFECT_SIZE_GUARD: the frozen CI-bound rule resolves a difference of any "
        "magnitude provided its sign is consistent across the 19 motors. M7 exposed this: the "
        "F-side candidate 'RESOLVED_ABOVE' M7 by 2.5e-07 nats, ~168000x below the 0.042-nat "
        "resolution floor, because the two are the SAME model to numerical precision. The frozen "
        "verdict is reported verbatim and unaltered; `scientificReading` carries the mandatory "
        "accompanying interpretation.")
    out["claimBoundary"] = (
        "POST_HOC_EXPLORATORY. Establishes no mechanism, no biological parity, and no "
        "active-inference claim. Duration-only, one cohort, 19 holdout motors, motor-equal NLPD. "
        "A point-estimate ranking is never a verdict. An interval containing 0 is NOT_ESTABLISHED "
        "- not equivalence, not 'no difference'. These contrasts were NOT pre-registered and do "
        "not carry the standing of the six that were. No P-level moves on this artifact.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(out, indent=1, sort_keys=True) + "\n"
    OUT.write_text(body, encoding="utf-8", newline="\n")
    print("\nWROTE %s\nsha256=%s" % (OUT, hashlib.sha256(body.encode("utf-8")).hexdigest()))
    print("oracleGate=%s  candidateRank=%d of %d  resolvedBelow=%r"
          % (out["oracleGate"]["status"], out["candidateRank"], out["nModelsRanked"],
             resolved_below))


if __name__ == "__main__":
    main()
