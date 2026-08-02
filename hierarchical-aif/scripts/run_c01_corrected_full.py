"""B4C01 corrected full-N run — synthetic parameter recovery / self-win sanity floor.

THE ONLY DEVIATION FROM THE COMMITTED CELL IS THE D3 SEEDING FIX.

The committed `cell_C01` seeds with
    np.random.default_rng(seed_base + sim + hash(gen) % 100000)
`hash(str)` is randomized per process when PYTHONHASHSEED is unset, so the committed cell produces
different synthetic data on every invocation and could never satisfy the protocol's byte-
determinism gate. This harness substitutes `seeding.stable_seed(...)`, a SHA-256-derived integer.
The `+ sim` term, `seed_base = 20260801`, the generator list and order, the tolerances, the
`> 0.5` self-win threshold, and the PASS/NOT_ESTABLISHED rule are UNCHANGED.

EVERY SCIENCE FUNCTION IS STILL CALLED THROUGH THE FROZEN b3/b4 MODULES:
    b4._simulate_from_model, b4._build_cohort_from_events,
    b3.fit_simple_models, b3.fit_m6, b3.scoring_params, b3.nlpd_per_event,
    b3.aggregate_motor_equal, b3.PUBLISHED, b3.committed_m3
Nothing is reimplemented here.

FROZEN CRITERIA (not restated loosely — read from the frozen artifact at run time):
    true params      : frozen B3 fits on derived_eligible_1_to_8
    tolerances       : M1 0.1 | M2 0.1 | M3 (w 0.1, log10(lf) 0.2) | M5 0.15 | M0 none
    withinTolerance  : |median(recovered) - true| <= tol   (a BIAS test, not a spread test)
    self-win         : self_win_frac > 0.5, judged against M0/M1/M2/M3/M5/M6
    PASS             : every generator withinTolerance AND self_win_frac > 0.5
                       (M0: self_win_frac only). Otherwise NOT_ESTABLISHED.
    M4/M7/M8 are SKIPPED by construction — the cell's declared design, recorded in the output.

NO FLOOR. A non-finite log density or a raising fit increments `failed`; it is never replaced,
clipped, or floored.

D4: the frozen NOT_RUN reason blames an "M4/M7-inclusive competition". This cell does not fit M4
or M7. `corrected_reasons.C01_REASON` supersedes it for reporting. The frozen artifact is NOT edited.

Prediction record committed BEFORE this harness existed:
    hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md   (commit 28ce738)
"""
from __future__ import annotations

import hashlib
import json
import math
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, corrected_reasons, seeding, status  # noqa: E402

CELL_ID = "B4C01"
PROTOCOL_VERSION = "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1"
COHORT_ID = "derived_eligible_1_to_8"
SEED_BASE = 20260801          # frozen
FROZEN_N = 200                # frozen, per generating model
GEN_MODELS = ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
              "M3_TWO_TIMESCALE", "M5_GAMMA")          # frozen order
SUB_MODELS = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
              "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"]
SKIPPED = ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]

# frozen tolerances, verbatim from cell_C01
TOL = {"M1_WEIBULL": 0.1, "M2_LOGNORMAL": 0.1,
       "M3_TWO_TIMESCALE": (0.1, 0.2), "M5_GAMMA": 0.15}
SELF_WIN_THRESHOLD = 0.5
CHECKPOINT_EVERY = 25
PROGRESS_EVERY = 10

PREDICTION_RECORD = "hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md"


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _write_json(path: Path, obj) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(obj, indent=1, sort_keys=True).replace("\r\n", "\n")
    path.write_text(body, encoding="utf-8", newline="\n")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def main():
    argv = list(sys.argv[1:])
    n_sims = int(argv[0]) if argv else FROZEN_N
    out_path = Path(argv[1]) if len(argv) > 1 else (
        HERE.parent / "results" / "motor_stack_aif" / "B4C01_CORRECTED_FULL_RESULT.json")
    progress_path = out_path.with_name(
        out_path.name.replace("_RESULT.json", "_PROGRESS.json")
        if out_path.name.endswith("_RESULT.json") else out_path.stem + "_PROGRESS.json")

    b3 = _bridge.b3()
    b4 = _bridge.b4()
    coh = _bridge.frozen_cohort(name=COHORT_ID)
    m3_pub = b3.committed_m3()
    b3res = _bridge.b3_result()
    fitted = b3res["cohorts"][COHORT_ID]["fitted"]

    out = {
        "cell": "B4C01_SYNTHETIC_PARAMETER_RECOVERY",
        "runVariant": "CORRECTED_FULL_N",
        "correctionApplied": ["D3_HASH_SEED_NONDETERMINISM"],
        "correctionNote": (
            "Only the seed derivation differs from the committed cell: stable SHA-256 seed "
            "replaces the process-varying hash(gen) term. The '+ sim' term, seed_base, generator "
            "list and order, tolerances, self-win threshold, model set, and verdict rule are "
            "unchanged."),
        "correctedReason_supersedes_frozen": corrected_reasons.C01_REASON,
        "cohort": COHORT_ID,
        "frozen_N_sim": FROZEN_N,
        "actual_N_sim_per_gen": n_sims,
        "resourceBoundPartial": n_sims < FROZEN_N,
        "seed_base": SEED_BASE,
        "gen_models": list(GEN_MODELS),
        "subModelsScored": SUB_MODELS,
        "skippedModels": SKIPPED,
        "skippedReason": (
            "M4/M7/M8 are skipped BY CONSTRUCTION in the frozen cell_C01. Self-win is judged "
            "against the 6 fitted competitors only. Recorded as a declared design limit, not a "
            "silent omission."),
        "protocolVersion": PROTOCOL_VERSION,
        "predictionRecord": PREDICTION_RECORD,
        "consumesB3ResultSha256": _sha256_file(_bridge.B3_RESULT),
        "frozenRunnerSha256": _sha256_file(_bridge.B4_RUNNER),
        "selfWinThreshold": SELF_WIN_THRESHOLD,
        "toleranceNote": (
            "withinTolerance is a BIAS test on the MEDIAN recovered parameter, not a spread test. "
            "Per-simulation spread is reported alongside it (p05/p95) but does not enter the "
            "frozen verdict."),
        "results": {},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }
    try:
        import scipy
        out["environment"]["scipy"] = scipy.__version__
    except Exception:
        pass

    print("B4C01 CORRECTED FULL RUN  n_sims=%d per generator x %d generators = %d total"
          % (n_sims, len(GEN_MODELS), n_sims * len(GEN_MODELS)), flush=True)
    print("out=%s\nprogress=%s" % (out_path, progress_path), flush=True)

    t_start = time.time()
    total_done = 0

    for gen in GEN_MODELS:
        gen_params = list(fitted[gen].get("params", []))
        tol = TOL.get(gen)
        recovered = []
        self_wins = 0
        failed = 0
        failures = []
        t_gen = time.time()

        for sim in range(n_sims):
            # ---- D3 FIX: stable SHA-256 seed replaces hash(gen) -----------------------------
            seed = seeding.stable_seed(
                cell_id="%s::%s" % (CELL_ID, gen),
                base_seed=SEED_BASE,
                replicate_index=sim,
                protocol_version=PROTOCOL_VERSION,
                cohort_id=COHORT_ID,
            )
            rng = np.random.default_rng(seed)
            try:
                ev = b4._simulate_from_model(gen, gen_params, coh, rng)
                coh_sim = b4._build_cohort_from_events(
                    "C01_%s_%d" % (gen, sim), tuple(range(1, 9)), ev)
                m1p = b3.PUBLISHED["M1_shape"]
                m2p = b3.PUBLISHED["M2_sigma"]
                fits = dict(b3.fit_simple_models(coh_sim, m3_pub, m1p, m2p))
                fits["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
                fits["M6_SEMI_MARKOV_STATE_DEPENDENT"] = b3.fit_m6(coh_sim)
                perm = {}
                for mid in SUB_MODELS:
                    p = b3.scoring_params(mid, fits[mid])
                    pe = b3.nlpd_per_event(mid, p, coh_sim)
                    perm[mid] = float(b3.aggregate_motor_equal(pe, coh_sim)["motorEqual"])
                winner = min(perm.items(), key=lambda kv: kv[1])[0]
                if winner == gen:
                    self_wins += 1
                recovered.append(list(fits[gen].get("params", [])) if gen in fits else [])
            except Exception as ex:          # NO FLOOR: a failure stays a failure
                failed += 1
                failures.append({"gen": gen, "sim": sim,
                                 "error": "%s: %s" % (type(ex).__name__, ex)})

            total_done += 1
            if (sim + 1) % PROGRESS_EVERY == 0:
                el = time.time() - t_gen
                print("  [%s] %d/%d  elapsed %.0fs  eta %.0fs  self_wins=%d fail=%d"
                      % (gen, sim + 1, n_sims, el,
                         el / (sim + 1) * (n_sims - sim - 1), self_wins, failed), flush=True)
            if total_done % CHECKPOINT_EVERY == 0:
                _write_json(progress_path, {
                    "LABEL": "PARTIAL_PROGRESS_CHECKPOINT_NOT_A_RESULT",
                    "DISCLAIMER": (
                        "Crash-recovery checkpoint of an IN-FLIGHT run. NOT a result, NOT "
                        "evidence, licenses NO verdict. The result is "
                        "B4C01_CORRECTED_FULL_RESULT.json, written only on completion."),
                    "cell": CELL_ID,
                    "simsAttemptedTotal": total_done,
                    "plannedTotal": n_sims * len(GEN_MODELS),
                    "currentGenerator": gen,
                    "elapsedS": time.time() - t_start,
                    "writtenUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                })

        completed = n_sims - failed
        summary = {
            "trueParams": gen_params,
            "n_sims": n_sims,
            "completed": completed,
            "failed": failed,
            "failures": failures,
            "self_wins": self_wins,
            "self_win_frac": (self_wins / n_sims) if n_sims else None,
            "self_win_passes": (self_wins / n_sims) > SELF_WIN_THRESHOLD if n_sims else None,
            "tolerance": tol,
            "runtimeS": time.time() - t_gen,
        }

        vals = [p for p in recovered if p]
        if vals and gen != "M0_EXPONENTIAL":
            if gen in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
                arr = np.array([p[0] for p in vals], dtype=np.float64)
                med = float(np.median(arr))
                summary["medianRecovered"] = med
                summary["biasMedian"] = med - gen_params[0]
                summary["withinTolerance"] = abs(med - gen_params[0]) <= tol
                summary["spread"] = {"p05": float(np.quantile(arr, 0.05)),
                                     "p95": float(np.quantile(arr, 0.95)),
                                     "note": "reported, does NOT enter the frozen verdict"}
            elif gen == "M3_TWO_TIMESCALE":
                w_arr = np.array([p[0] for p in vals], dtype=np.float64)
                lf_arr = np.array([math.log10(p[1]) for p in vals], dtype=np.float64)
                med_w = float(np.median(w_arr))
                med_lf = float(np.median(lf_arr))
                summary["medianRecovered"] = {"w": med_w, "lf_log10": med_lf}
                summary["biasMedian"] = {"w": med_w - gen_params[0],
                                         "lf_log10": med_lf - math.log10(gen_params[1])}
                summary["withinTolerance"] = (abs(summary["biasMedian"]["w"]) <= tol[0]
                                              and abs(summary["biasMedian"]["lf_log10"]) <= tol[1])
                summary["spread"] = {
                    "w_p05": float(np.quantile(w_arr, 0.05)),
                    "w_p95": float(np.quantile(w_arr, 0.95)),
                    "lf_log10_p05": float(np.quantile(lf_arr, 0.05)),
                    "lf_log10_p95": float(np.quantile(lf_arr, 0.95)),
                    "note": "reported, does NOT enter the frozen verdict"}

        out["results"][gen] = summary
        print("[%s] DONE self_win %d/%d frac=%.4f  withinTolerance=%s  fail=%d"
              % (gen, self_wins, n_sims, summary["self_win_frac"],
                 summary.get("withinTolerance", "n/a"), failed), flush=True)

    # ---- frozen verdict rule ------------------------------------------------------------------
    ok = True
    failing = []
    for gen, s in out["results"].items():
        if gen == "M0_EXPONENTIAL":
            if not (s["self_win_frac"] > SELF_WIN_THRESHOLD):
                ok = False
                failing.append("%s:self_win" % gen)
            continue
        if not s.get("withinTolerance", False):
            ok = False
            failing.append("%s:tolerance" % gen)
        if not (s["self_win_frac"] > SELF_WIN_THRESHOLD):
            ok = False
            failing.append("%s:self_win" % gen)

    total_runtime = time.time() - t_start
    out["runStatus"] = status.classify_run(actual_n=n_sims, planned_n=FROZEN_N)
    if out["resourceBoundPartial"]:
        out["verdict"] = "PARTIAL_RESOURCE_BOUND"
    else:
        out["verdict"] = "PASS" if ok else "NOT_ESTABLISHED"
    out["failingCriteria"] = failing
    out["frozenPredictionExpectation"] = "PASS"
    out["predictionOutcome"] = (
        "NOT_ESTABLISHED" if out["resourceBoundPartial"]
        else ("CONFIRMED" if out["verdict"] == "PASS" else "REFUTED"))
    out["totalRuntimeS"] = total_runtime
    out["secondsPerSim"] = total_runtime / max(1, n_sims * len(GEN_MODELS))
    out["claimBoundary"] = (
        "Establishes no mechanism, no biological parity, and no active-inference claim. EVERY "
        "dataset in this cell is SYNTHETIC and none may be labelled OBSERVED. Scoped to 5 "
        "generating models, 6 fitted competitors, motor-equal NLPD, one 19-motor cohort geometry. "
        "M4/M7/M8 are skipped by construction, so this cell says nothing about the mixture, "
        "hierarchical, or KDE models. A self-win failure among statistically near-equivalent "
        "nested models is a POWER statement about the holdout size, not evidence of a coding "
        "defect; a parameter-recovery failure would be materially more serious. The retained "
        "adverse B3 finding - M2_LOGNORMAL out-predicting M3 by ~0.0369 nats event-pooled - is "
        "unchanged and is reported alongside this result. M2 is an ADVERSARIAL BASELINE, never "
        "the UNI model.")

    sha = _write_json(out_path, out)
    print("\nWROTE %s\nsha256=%s" % (out_path, sha))
    print("verdict=%s  runStatus=%s  outcome=%s  failing=%r"
          % (out["verdict"], out["runStatus"], out["predictionOutcome"], failing))
    print("totalRuntimeS=%.1f  secondsPerSim=%.2f" % (total_runtime, out["secondsPerSim"]))


if __name__ == "__main__":
    main()
