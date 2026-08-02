"""B4C11 corrected full-N run — M7 structural identifiability, U4 motor-cluster bootstrap.

THE ONLY DEVIATION FROM THE COMMITTED CELL IS THE D1 CLUSTER-BOOTSTRAP FIX.

The committed `cell_C11` assembles each replicate's resampled events and rebuilds
`b3.Cohort(f"C11_b{b}", ...)`. `Cohort` groups `train_by_motor` BY `motorId`, so a motor drawn K
times collapses into ONE group holding K copies instead of K exchangeable groups. `m7_train_nll`
iterates `train_by_motor`, so a K-fold group contributes L_m^K and over-sharpens that motor's
latent. Measured at seed_base=20260717, b=0: 80 draws -> 46 groups (42.5% cluster loss).

This harness substitutes `motor_stack_aif.bootstrap.build_bootstrap_cohort`, which builds the
cohort IDENTICALLY (same split derivation, same bootstrap-resampled per-state scales, same
normalised `_y`, bit-identical flat `train_y`) and rebuilds ONLY `train_by_motor` as one group per
DRAW. The source motorId survives as metadata in `bootstrap_group_origin`, never as a grouping key.

EVERY SCIENCE FUNCTION IS STILL CALLED THROUGH THE FROZEN b3/b4 MODULES:
    b4._fit_m7_reduced          (26-start L-BFGS-B, frozen tolerances - NOT reimplemented here)
    b3.m7_train_nll             (via _fit_m7_reduced)
    b3.Cohort, b3.sha256_mod5   (via bootstrap._assemble)
    _bridge.frozen_cohort()     (rebuilds derived_eligible_1_to_8 exactly as B4 does)

NOT CHANGED: threshold (collapseFraction >= 0.25), criterion, frozen N_boot = 2000, seed_base =
20260717, the arithmetic per-replicate seeding, the cohort, the model, the optimiser budget.

D3 DOES NOT APPLY. C11 seeds arithmetically (`seed_base + b`); there is no `hash()` in the U4
path, so `seeding.stable_seed` is deliberately NOT substituted here. The harness asserts that its
draw sequence is identical to the frozen inline construction before doing any work.

U1 / U2 / U3 are CARRIED FORWARD VERBATIM from the frozen artifact, not recomputed. U2 is a
deterministic profile scan on the full unresampled cohort and never touches the bootstrap, so D1
cannot reach it. See section 5 of the prediction record for the written justification.

NO FLOOR. A non-finite log density or a `None` fit increments `failed`. It is never replaced,
clipped, or floored.

Prediction record committed before execution:
    hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, bootstrap, status  # noqa: E402

CELL_ID = "B4C11_M7_STRUCTURAL_IDENTIFIABILITY"
PROTOCOL_VERSION = "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1"
COHORT_ID = "derived_eligible_1_to_8"
SEED_BASE = 20260717          # frozen
FROZEN_N_BOOT = 2000          # frozen
COLLAPSE_TAU_THRESHOLD = 1e-3     # frozen
COLLAPSE_FRACTION_FIRES_AT = 0.25  # frozen
DEFAULT_PAIRED = 25           # legacy-vs-corrected comparison subset (diagnostic only)
CHECKPOINT_EVERY = 25
PROGRESS_EVERY = 10

PREDICTION_RECORD = "hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md"


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _seed_equivalence_check(train_motors, n_check=3):
    """Prove this harness draws EXACTLY what the frozen inline C11 code draws.

    Frozen inline construction:
        rng_b = np.random.default_rng(seed_base + b)
        idx   = rng_b.integers(0, n_tm, size=n_tm)
        sampled = [train_motors[i] for i in idx]
    """
    n_tm = len(train_motors)
    for b in range(n_check):
        frozen_rng = np.random.default_rng(SEED_BASE + b)
        frozen_idx = frozen_rng.integers(0, n_tm, size=n_tm)
        frozen_sampled = [train_motors[i] for i in frozen_idx]

        harness_rng = np.random.default_rng(SEED_BASE + b)
        harness_sampled = bootstrap.draw_motors(train_motors, harness_rng)

        if harness_sampled != frozen_sampled:
            raise SystemExit(
                "ABORT: seed equivalence check FAILED at b=%d. The corrected harness does not "
                "reproduce the frozen C11 draw sequence. Refusing to run." % b)
    return {"checked_replicates": n_check,
            "result": "IDENTICAL_TO_FROZEN_INLINE_DRAW_SEQUENCE",
            "formula": "seed_b = %d + b ; default_rng(seed_b).integers(0, %d, size=%d)"
                       % (SEED_BASE, n_tm, n_tm)}


def _write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(obj, indent=1, sort_keys=True).replace("\r\n", "\n")
    path.write_text(body, encoding="utf-8", newline="\n")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _summary(tau_arr):
    a = np.asarray(tau_arr, dtype=np.float64)
    return {"median": float(np.median(a)),
            "p025": float(np.quantile(a, 0.025)),
            "p975": float(np.quantile(a, 0.975))}


def main():
    argv = [a for a in sys.argv[1:]]
    n_paired = DEFAULT_PAIRED
    if "--paired" in argv:
        i = argv.index("--paired")
        n_paired = int(argv[i + 1])
        del argv[i:i + 2]

    n_boot = int(argv[0]) if len(argv) > 0 else FROZEN_N_BOOT
    out_path = Path(argv[1]) if len(argv) > 1 else (
        HERE.parent / "results" / "motor_stack_aif" / "B4C11_CORRECTED_FULL_RESULT.json")
    n_paired = min(n_paired, n_boot)
    progress_path = out_path.with_name(
        out_path.name.replace("_RESULT.json", "_PROGRESS.json")
        if out_path.name.endswith("_RESULT.json") else out_path.stem + "_PROGRESS.json")

    b3 = _bridge.b3()
    b4 = _bridge.b4()
    coh = _bridge.frozen_cohort(name=COHORT_ID)

    b3res = _bridge.b3_result()
    m7_rec = b3res["cohorts"][COHORT_ID]["fitted"]["M7_HIERARCHICAL_MOTOR"]
    k_full = m7_rec["kTau"]["k"]
    tau_full = m7_rec["kTau"]["tau"]

    # ---- carried-forward U1/U2/U3, copied VERBATIM from the frozen artifact -----------------
    frozen_c11 = _bridge.b4_result()["cells"]["B4C11"]
    carried = {
        "provenance": "CARRIED_FORWARD_FROM_FROZEN_ARTIFACT",
        "sourceArtifact": "audits/phase-b/b4-identifiability-robustness-result.v1.json",
        "sourceArtifactSha256": _sha256_file(_bridge.B4_RESULT),
        "sourceCell": "B4C11",
        "justification": (
            "U1 (tau interior) and U3 (LRT support over M1) were settled in B3 on the full "
            "unresampled cohort. U2 is a deterministic 61-point profile-likelihood scan on the "
            "full unresampled cohort; it never constructs a bootstrap replicate and never touches "
            "train_by_motor grouping, so defect D1 (a bootstrap-resampling defect) cannot reach "
            "it. These values are COPIED, not recomputed and not relabelled."),
        "U1": frozen_c11["U1_alreadyDone_in_B3"],
        "U3": frozen_c11["U3_alreadyDone_in_B3"],
        "U2_profile": frozen_c11["U2_profile"],
    }

    train_motors = list(coh.train_motors)
    n_tm = len(train_motors)
    seed_check = _seed_equivalence_check(train_motors)

    print("B4C11 CORRECTED FULL RUN  n_boot=%d  paired_subset=%d  train_motors=%d"
          % (n_boot, n_paired, n_tm), flush=True)
    print("seedEquivalenceCheck: %s" % seed_check["result"], flush=True)
    print("out=%s\nprogress=%s" % (out_path, progress_path), flush=True)

    t_start = time.time()
    completed = 0
    failed = 0
    collapsed = 0
    tau_hats = []
    k_hats = []
    group_counts = []
    distinct_counts = []
    failures = []
    paired_rows = []

    for b in range(n_boot):
        seed_b = SEED_BASE + b
        rng_b = np.random.default_rng(seed_b)
        sampled = bootstrap.draw_motors(train_motors, rng_b)
        n_distinct = len(set(sampled))

        # ---- CORRECTED ARM (this is the evidence) -------------------------------------------
        corr_tau = None
        corr_k = None
        corr_groups = None
        try:
            coh_b = bootstrap.build_bootstrap_cohort(
                coh, sampled, name="C11_b%d" % b, states=tuple(range(1, 9)))
            corr_groups = len(coh_b.train_by_motor)
            fit_b = b4._fit_m7_reduced(coh_b, k_full=k_full, tau_full=tau_full)
        except Exception as ex:                      # cohort build or fit raised
            failed += 1
            failures.append({"replicate": b, "stage": "corrected",
                             "error": "%s: %s" % (type(ex).__name__, ex)})
            fit_b = None
        else:
            if fit_b is None:                        # NO FLOOR: a failed fit stays failed
                failed += 1
                failures.append({"replicate": b, "stage": "corrected",
                                 "error": "_fit_m7_reduced returned None (no finite optimum)"})
            else:
                completed += 1
                corr_tau = float(fit_b["tau"])
                corr_k = float(fit_b["k"])
                tau_hats.append(corr_tau)
                k_hats.append(corr_k)
                group_counts.append(corr_groups)
                distinct_counts.append(n_distinct)
                if corr_tau < COLLAPSE_TAU_THRESHOLD:
                    collapsed += 1

        # ---- LEGACY_DEFECTIVE_FOR_COMPARISON_ONLY arm, same draws ---------------------------
        if b < n_paired:
            row = {"replicate": b, "seed": seed_b, "nDraws": len(sampled),
                   "nDistinctDrawn": n_distinct,
                   "correctedGroups": corr_groups, "correctedTau": corr_tau,
                   "correctedK": corr_k}
            try:
                coh_l = bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE(
                    coh, sampled, name="C11_legacy_b%d" % b, states=tuple(range(1, 9)))
                fit_l = b4._fit_m7_reduced(coh_l, k_full=k_full, tau_full=tau_full)
                row["legacyGroups"] = len(coh_l.train_by_motor)
                row["legacyTau"] = None if fit_l is None else float(fit_l["tau"])
                row["legacyK"] = None if fit_l is None else float(fit_l["k"])
            except Exception as ex:
                row["legacyError"] = "%s: %s" % (type(ex).__name__, ex)
            if row.get("legacyTau") is not None and corr_tau is not None:
                row["deltaTau_corrected_minus_legacy"] = corr_tau - row["legacyTau"]
            paired_rows.append(row)

        done = b + 1
        if done % PROGRESS_EVERY == 0:
            el = time.time() - t_start
            eta = el / done * (n_boot - done)
            print("  [C11] %d/%d  elapsed %.0fs  eta %.0fs  completed=%d failed=%d "
                  "collapsed=%d  tau_med=%s"
                  % (done, n_boot, el, eta, completed, failed, collapsed,
                     ("%.6f" % float(np.median(tau_hats))) if tau_hats else "n/a"), flush=True)

        if done % CHECKPOINT_EVERY == 0 or done == n_boot:
            _write_json(progress_path, {
                "LABEL": "PARTIAL_PROGRESS_CHECKPOINT_NOT_A_RESULT",
                "DISCLAIMER": (
                    "This file is a crash-recovery checkpoint of an IN-FLIGHT run. It is NOT a "
                    "result, NOT evidence, and licenses NO verdict. Do not read, quote, or "
                    "predicate anything on these numbers. The result is "
                    "B4C11_CORRECTED_FULL_RESULT.json, written only on completion."),
                "cell": CELL_ID,
                "replicatesAttempted": done,
                "plannedN": n_boot,
                "frozen_N_boot": FROZEN_N_BOOT,
                "completed": completed, "failed": failed, "collapsed": collapsed,
                "elapsedS": time.time() - t_start,
                "writtenUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            })

    total_runtime = time.time() - t_start

    # ---- U4 verdict by the FROZEN threshold ---------------------------------------------------
    if completed > 0:
        frac = collapsed / completed
        u4 = {
            "completed": completed,
            "failed": failed,
            "tauHatSummary": _summary(tau_hats),
            "kHatSummary": _summary(k_hats),
            "collapseFraction_tau_lt_1e_3": frac,
            "collapseTauThreshold": COLLAPSE_TAU_THRESHOLD,
            "collapseFractionFiresAt": COLLAPSE_FRACTION_FIRES_AT,
            "verdict": ("UNSTABLE_DISPERSION_U4_FIRES"
                        if frac >= COLLAPSE_FRACTION_FIRES_AT else "U4_OK"),
            "tauHats": tau_hats,
            "groupCountMin": int(min(group_counts)) if group_counts else None,
            "groupCountMax": int(max(group_counts)) if group_counts else None,
            "nDistinctDrawnMin": int(min(distinct_counts)) if distinct_counts else None,
            "nDistinctDrawnMax": int(max(distinct_counts)) if distinct_counts else None,
        }
    else:
        frac = None
        u4 = {"status": "NO_SUCCESSFUL_BOOTSTRAP", "completed": 0, "failed": failed,
              "verdict": None}

    # ---- paired legacy-vs-corrected effect size (diagnostic, never evidence) -------------------
    both = [r for r in paired_rows
            if r.get("legacyTau") is not None and r.get("correctedTau") is not None]
    paired_block = {
        "label": "LEGACY_DEFECTIVE_FOR_COMPARISON_ONLY",
        "disclaimer": (
            "The legacy arm deliberately reproduces defect D1 on identical draws. It is a "
            "defect-magnitude MEASUREMENT. It is NOT evidence, NOT a result, and licenses NO "
            "verdict. No U4 status may be derived from it."),
        "nPairedRequested": n_paired,
        "nPairedWithBothArms": len(both),
        "rows": paired_rows,
    }
    if both:
        lt = [r["legacyTau"] for r in both]
        ct = [r["correctedTau"] for r in both]
        paired_block["legacyTauMedian"] = float(np.median(lt))
        paired_block["correctedTauMedian"] = float(np.median(ct))
        paired_block["medianDeltaTau_corrected_minus_legacy"] = float(
            np.median([r["deltaTau_corrected_minus_legacy"] for r in both]))
        paired_block["fracCorrectedBelowLegacy"] = float(
            sum(1 for r in both if r["correctedTau"] < r["legacyTau"]) / len(both))
        paired_block["legacyGroupsMin"] = int(min(r["legacyGroups"] for r in both))
        paired_block["legacyGroupsMax"] = int(max(r["legacyGroups"] for r in both))
        paired_block["correctedGroupsMin"] = int(min(r["correctedGroups"] for r in both))
        paired_block["correctedGroupsMax"] = int(max(r["correctedGroups"] for r in both))

    # ---- composite M7 status (U4 new; U1/U2/U3 carried forward) --------------------------------
    run_status = status.classify_run(actual_n=n_boot, planned_n=FROZEN_N_BOOT)
    resource_bound_partial = n_boot < FROZEN_N_BOOT

    fires = []
    if str(carried["U2_profile"].get("verdict", "")).startswith("UNIDENTIFIED"):
        fires.append("U2")
    if str(u4.get("verdict") or "").startswith("UNSTABLE"):
        fires.append("U4")
    if resource_bound_partial:
        # A PARTIAL run may not report an identifiability STATUS, even though the arithmetic
        # threshold can still be evaluated on the replicates that ran. This is the D2 lesson made
        # structural: the submitted C11 U4_OK came from 30 of 2000 replicates and read as a
        # settled status. Never again from this harness.
        m7_status = ("PARTIAL_NOT_ESTABLISHED (%d of %d replicates; the frozen threshold was "
                     "evaluated but a partial replicate count licenses no identifiability status)"
                     % (n_boot, FROZEN_N_BOOT))
    elif u4.get("verdict") is None:
        m7_status = "NOT_ESTABLISHED (U4 has no verdict on this run)"
    elif fires:
        m7_status = ("UNIDENTIFIED_OR_UNSTABLE (%s) (U1 interior, U3 LRT-supported per B3 - "
                     "carried forward)" % ",".join(fires))
    else:
        m7_status = ("IDENTIFIED_ON_THIS_COHORT (U4 newly computed on the corrected bootstrap; "
                     "U1/U2/U3 carried forward from the frozen artifact)")

    out = {
        "cell": CELL_ID,
        "runVariant": "CORRECTED_FULL_N",
        "correctionApplied": ["D1_C11_CLUSTER_COLLAPSE"],
        "correctionNote": (
            "Only the bootstrap cohort GROUPING differs from the committed cell: each of the 80 "
            "motor draws becomes its own exchangeable group in train_by_motor instead of "
            "collapsing duplicates by motorId. Split derivation, per-state scales, flat train_y, "
            "seeding, threshold, criterion, N, model, and the 26-start L-BFGS-B budget are "
            "unchanged. D3 does not apply: C11 seeding is arithmetic, not hash-derived."),
        "cohort": COHORT_ID,
        "frozen_N_boot": FROZEN_N_BOOT,
        "actual_N_boot": n_boot,
        "resourceBoundPartial": resource_bound_partial,
        "seed_base": SEED_BASE,
        "seedFormula": "seed_b = %d + b ; np.random.default_rng(seed_b)" % SEED_BASE,
        "seedEquivalenceCheck": seed_check,
        "protocolVersion": PROTOCOL_VERSION,
        "predictionRecord": PREDICTION_RECORD,
        "consumesB3ResultSha256": _sha256_file(_bridge.B3_RESULT),
        "consumesB4ResultSha256": _sha256_file(_bridge.B4_RESULT),
        "frozenRunnerSha256": _sha256_file(_bridge.B4_RUNNER),
        "completed": completed,
        "failed": failed,
        "failures": failures,
        "collapsedCount": collapsed,
        "collapseFraction_tau_lt_1e_3": frac,
        "tauHatSummary": u4.get("tauHatSummary"),
        "verdict": (u4.get("verdict") if not resource_bound_partial
                    else "PARTIAL_NOT_ESTABLISHED"),
        "U4_bootstrap": u4,
        "carriedForward_U1_U2_U3": carried,
        "M7_status": m7_status,
        "legacyVsCorrectedPaired": paired_block,
        "runStatus": run_status,
        "frozenPredictionExpectation": "PROFILE_FLAT_OR_WEAK",
        "frozenPredictionFalsifier": (
            "A sharp tau profile (small logspan) and a near-zero bootstrap collapse fraction, "
            "which would make tau well-identified."),
        "predictionOutcome": (
            "NOT_ESTABLISHED" if (resource_bound_partial or u4.get("verdict") is None)
            else ("CONFIRMED" if u4.get("verdict") == "UNSTABLE_DISPERSION_U4_FIRES"
                  else "REFUTED")),
        "withdrawnArtifactStatus": (
            "The submitted C11 U4_OK (30 of 2000 replicates, defective cluster bootstrap) remains "
            "WITHDRAWN and is NOT restored by this run, whatever this run returns."),
        "totalRuntimeS": total_runtime,
        "secondsPerReplicate": (total_runtime / n_boot) if n_boot else None,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
        "claimBoundary": (
            "Establishes no mechanism, no biological parity, and no active-inference claim. U4 is "
            "an identifiability/stability check on ONE parameter (tau) of ONE frozen competitor "
            "(M7_HIERARCHICAL_MOTOR) on ONE cohort (derived_eligible_1_to_8, 80 training motors), "
            "under the frozen collapseFraction >= 0.25 criterion. The experimental unit is the "
            "MOTOR. This result does not transfer to C10/M4, to the mark process, or to the "
            "F-side motor-stack AIF model, and it does not move any P-level on its own. The "
            "retained adverse B3 finding - M2_LOGNORMAL out-predicting M3 by ~0.0369 nats "
            "event-pooled - is unchanged and is reported alongside this result, never instead of "
            "it. M2 is an ADVERSARIAL BASELINE, never the UNI model."),
    }

    try:
        b4_env = _bridge.b4_result().get("environment")
        if b4_env:
            out["environment"]["frozenRunEnvironment"] = b4_env
    except Exception:
        pass

    try:
        import scipy
        out["environment"]["scipy"] = scipy.__version__
    except Exception:
        pass

    sha = _write_json(out_path, out)
    print("\nWROTE %s\nsha256=%s" % (out_path, sha))
    print("verdict=%s  runStatus=%s  completed=%d  failed=%d  collapseFraction=%s  outcome=%s"
          % (out["verdict"], run_status, completed, failed,
             ("%.6f" % frac) if frac is not None else "n/a", out["predictionOutcome"]))
    print("M7_status=%s" % m7_status)
    print("totalRuntimeS=%.1f  secondsPerReplicate=%.2f"
          % (total_runtime, total_runtime / n_boot if n_boot else float("nan")))


if __name__ == "__main__":
    main()
