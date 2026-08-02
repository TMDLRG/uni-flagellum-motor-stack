"""B4C02 corrected full-N run — misspecified-world discriminator.

THE ONLY DEVIATION FROM THE COMMITTED CELL IS THE D3 SEEDING FIX.

The committed `cell_C02` seeds with `np.random.default_rng(seed_base + sim + hash(gen_label) % 100000)`.
`hash(str)` is randomized per process (PYTHONHASHSEED unset), so the committed cell produces
different synthetic data on every invocation and could never satisfy the protocol's byte-
determinism gate. This harness substitutes `seeding.stable_seed(...)`, a SHA-256-derived integer.

Everything else is called through the SAME b3/b4 functions the committed cell uses:
    _simulate_weibull_gamma_blend, _simulate_three_timescale_heavy_tail,
    _simulate_per_motor_heterogeneous_weibull, _build_cohort_from_events,
    b3.fit_simple_models, b3.fit_m6, b3.scoring_params, b3.nlpd_per_event,
    b3.aggregate_motor_equal
No threshold, N, criterion, model set, or seed_base is changed. seed_base = 20260802 (frozen).

Frozen criterion: gensWithM2overM3 = #{generators with m2_beats_m3_frac >= 0.5}
                  >= 2 of 3 -> GENERATOR-ROBUST_ADVERSE ; else GENERATOR-SPECIFIC

Prediction record committed before execution:
    hierarchical-aif/protocols/B4C02-CORRECTED-FULL-PREDICTION.md
"""
from __future__ import annotations

import json
import platform
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, seeding, status  # noqa: E402

CELL_ID = "B4C02"
PROTOCOL_VERSION = "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1"
COHORT_ID = "derived_eligible_1_to_8"
SEED_BASE = 20260802          # frozen
FROZEN_N = 200                # frozen, per generator
SUB_MODELS = ["M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
              "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT"]
SKIPPED = ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]


def main():
    n_sims = int(sys.argv[1]) if len(sys.argv) > 1 else FROZEN_N
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        HERE.parent / "results" / "motor_stack_aif" / "B4C02_CORRECTED_FULL_RESULT.json")

    b3 = _bridge.b3()
    b4 = _bridge.b4()
    coh_template = _bridge.frozen_cohort(name=COHORT_ID)
    m3_pub = b3.committed_m3()

    generators = [
        ("weibull_gamma_blend", b4._simulate_weibull_gamma_blend),
        ("three_timescale_heavy_tail", b4._simulate_three_timescale_heavy_tail),
        ("per_motor_heterogeneous_weibull", b4._simulate_per_motor_heterogeneous_weibull),
    ]

    out = {
        "cell": "B4C02_MISSPECIFIED_WORLDS",
        "runVariant": "CORRECTED_FULL_N",
        "correctionApplied": ["D3_HASH_SEED_NONDETERMINISM"],
        "correctionNote": (
            "Only the seed derivation differs from the committed cell: stable SHA-256 seed "
            "replaces process-varying hash(). No threshold, N, criterion, model set, or "
            "seed_base changed."),
        "cohort": COHORT_ID,
        "frozen_N_sim": FROZEN_N,
        "actual_N_sim_per_gen": n_sims,
        "resourceBoundPartial": n_sims < FROZEN_N,
        "seed_base": SEED_BASE,
        "protocolVersion": PROTOCOL_VERSION,
        "predictionRecord": "hierarchical-aif/protocols/B4C02-CORRECTED-FULL-PREDICTION.md",
        "consumesB3ResultSha256": _bridge.b3_result().get("schema") and None,
        "generators": [g for g, _ in generators],
        "results": {},
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
        },
    }

    t_start = time.time()
    for gen_label, gen_fn in generators:
        m2_beats_m3 = 0
        winners = defaultdict(int)
        failures = 0
        t_gen = time.time()
        for sim in range(n_sims):
            seed = seeding.stable_seed(
                cell_id="%s::%s" % (CELL_ID, gen_label),
                base_seed=SEED_BASE,
                replicate_index=sim,
                protocol_version=PROTOCOL_VERSION,
                cohort_id=COHORT_ID,
            )
            rng = np.random.default_rng(seed)
            try:
                ev = gen_fn(coh_template, rng)
                coh_sim = b4._build_cohort_from_events(
                    "C02_%s_%d" % (gen_label, sim), tuple(range(1, 9)), ev)
                m1p = b3.PUBLISHED["M1_shape"]
                m2p = b3.PUBLISHED["M2_sigma"]
                fits = dict(b3.fit_simple_models(coh_sim, m3_pub, m1p, m2p))
                fits["M0_EXPONENTIAL"] = dict(params=[], trainNLL=None, telemetry={})
                fits["M6_SEMI_MARKOV_STATE_DEPENDENT"] = b3.fit_m6(coh_sim)
                nlpd_by = {}
                for mid in SUB_MODELS:
                    p = b3.scoring_params(mid, fits[mid])
                    pe = b3.nlpd_per_event(mid, p, coh_sim)
                    nlpd_by[mid] = float(b3.aggregate_motor_equal(pe, coh_sim)["motorEqual"])
                winners[min(nlpd_by.items(), key=lambda kv: kv[1])[0]] += 1
                if nlpd_by["M2_LOGNORMAL"] < nlpd_by["M3_TWO_TIMESCALE"]:
                    m2_beats_m3 += 1
            except Exception as ex:
                failures += 1
                print("  sim %d FAILED: %s: %s" % (sim, type(ex).__name__, ex), flush=True)
            if (sim + 1) % 10 == 0:
                el = time.time() - t_gen
                print("  [%s] %d/%d  elapsed %.0fs  eta %.0fs  m2>m3=%d fail=%d"
                      % (gen_label, sim + 1, n_sims, el,
                         el / (sim + 1) * (n_sims - sim - 1), m2_beats_m3, failures), flush=True)
        completed = n_sims - failures
        out["results"][gen_label] = {
            "n_sims": n_sims,
            "completed": completed,
            "failures": failures,
            "m2_beats_m3_nlpd_count": m2_beats_m3,
            "m2_beats_m3_frac": (m2_beats_m3 / completed) if completed else None,
            "winner_freq": dict(winners),
            "subModelsScored": SUB_MODELS,
            "skippedModels": SKIPPED,
            "runtimeS": time.time() - t_gen,
        }
        print("[%s] DONE m2>m3 %d/%d frac=%.4f" %
              (gen_label, m2_beats_m3, completed,
               (m2_beats_m3 / completed) if completed else float("nan")), flush=True)

    gens_over = sum(1 for v in out["results"].values()
                    if v["m2_beats_m3_frac"] is not None and v["m2_beats_m3_frac"] >= 0.5)
    out["gensWithM2overM3"] = gens_over
    out["runStatus"] = status.classify_run(actual_n=n_sims, planned_n=FROZEN_N)
    if out["resourceBoundPartial"]:
        out["verdict"] = "PARTIAL_RESOURCE_BOUND"
    else:
        out["verdict"] = ("GENERATOR-ROBUST_ADVERSE" if gens_over >= 2 else "GENERATOR-SPECIFIC")
    out["frozenPredictionExpectation"] = "GENERATOR-ROBUST_ADVERSE"
    out["predictionOutcome"] = (
        "CONFIRMED" if out["verdict"] == "GENERATOR-ROBUST_ADVERSE"
        else ("REFUTED" if out["verdict"] == "GENERATOR-SPECIFIC" else "NOT_ESTABLISHED"))
    out["totalRuntimeS"] = time.time() - t_start
    out["claimBoundary"] = (
        "Establishes no mechanism, no biological parity, no active-inference claim. Scoped to 3 "
        "misspecified generators, 6 simple competitors, motor-equal NLPD, one 19-motor cohort. "
        "M4/M7/M8 are skipped by construction. M2 is an ADVERSARIAL BASELINE, never the UNI model.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(out, indent=1, sort_keys=True).replace("\r\n", "\n")
    out_path.write_text(body, encoding="utf-8", newline="\n")
    import hashlib
    print("\nWROTE %s\nsha256=%s\nverdict=%s  gensWithM2overM3=%d  outcome=%s"
          % (out_path, hashlib.sha256(body.encode("utf-8")).hexdigest(),
             out["verdict"], gens_over, out["predictionOutcome"]))


if __name__ == "__main__":
    main()
