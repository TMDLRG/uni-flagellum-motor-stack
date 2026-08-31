"""P4 TRANSFER freeze-A / score-B harness — refuses first, scores second, relabels nothing.

WHAT THIS IS
------------
The executable half of experiments/predictions/P4-TRANSFER-PREDICTION-RECORD.v1.json: the
freeze-on-A / score-B-once harness that Door P4 — TRANSFER declares as agent-authorable prep
(docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:85-88). Acceptance criterion under test, verbatim
(experiments/cross-study-preregistration.v1.json:107-109, X10): "At least one mechanistic
parameterization frozen on one laboratory/study predicts a second laboratory's commensurate raw
observations with a predeclared advantage over baselines."

WHAT THIS DOES NOT CLAIM
------------------------
- It relabels no gate. X10 stays NOT_ESTABLISHED, H-AIF-G8 stays NOT_LOCATED, G08 stays
  BLOCKED_EXTERNAL, no matter what this prints. A verdict JSON from this harness is INPUT to the
  operator/gate process, never a gate result.
- It reads no held-out data. The lab-A (Wadhwa 2022) holdout is SPENT (duration spent by B3;
  mark channel burned, D5) and is not read here. No lab-B cohort exists as of 2026-08-30, and
  this harness REFUSES to score anything whose sha256 is not registered in the prediction record
  (registration itself requires the record's commit-graph preconditions).
- It does not reimplement the scoring rule. Every scored number is produced by the frozen
  implementations (a second implementation of a frozen rule is a drift channel):
    hierarchical-aif/src/motor_stack_aif/score.py:35   motor_equal_nlpd
    hierarchical-aif/src/motor_stack_aif/score.py:46   per_motor_means
    hierarchical-aif/src/motor_stack_aif/score.py:73   contrast_with_ci (percentile, MOTOR unit,
                                                       N=2000, seed=20260717, threshold 0.0)
    hierarchical-aif/src/motor_stack_aif/compare.py:189 to_seconds_scale (the single Jacobian)
    hierarchical-aif/src/motor_stack_aif/compare.py:405 score_fside_marginal_per_event
    hierarchical-aif/src/motor_stack_aif/baselines.py:27,32 m1/m2 frozen densities

REFUSAL BEHAVIOUR (the point of the file)
-----------------------------------------
(a) lab-B file sha256 not registered in the record        -> REFUSED_SHA_NOT_REGISTERED, exit 2
(b) record's labBRegistration still not_established       -> REFUSED_REGISTRATION_NOT_ESTABLISHED
(b') motor-count derivation (N) still not_established     -> REFUSED_N_NOT_DERIVED
(units) any event outside the frozen state support 1..8   -> REFUSED_INCOMMENSURATE (axis: units)
Frozen lab-A artifact bytes not matching the record's sha -> HALT (frozen-evidence mismatch), exit 1.

SELF-TEST (--self-test)
-----------------------
Runs the full path on SYNTHETIC data generated in memory, clearly labelled SYNTHETIC, never
written under experiments/data or anywhere else. Proves the machinery bites: the refusal paths
refuse (unregistered sha; not_established registration) and the scoring path scores. Synthetic
numbers move no gate and appear in no artifact.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT / "hierarchical-aif" / "src"))
sys.dont_write_bytecode = True

import numpy as np  # noqa: E402

from motor_stack_aif import baselines, compare, score, status  # noqa: E402

RECORD_PATH = REPO_ROOT / "experiments" / "predictions" / "P4-TRANSFER-PREDICTION-RECORD.v1.json"

#: Frozen floor and contrast machinery constants come from the frozen module, not from copies.
FLOOR = compare.RESOLUTION_FLOOR_HALFWIDTH_NATS          # 0.042 nats
BOOT_SEED = compare.BOOT_SEED                            # 20260717
N_BOOT = compare.N_BOOT                                  # 2000

#: Duration-only allow-list. Mark fields (nextStateN, direction, jump) are NEVER requested (D5).
_ALLOWED_FIELDS = ("motorId", "stateN", "durationS", "rightCensored")

EXIT_OK, EXIT_HALT, EXIT_REFUSED = 0, 1, 2


class FrozenEvidenceMismatch(RuntimeError):
    """A lab-A artifact's bytes do not match the sha256 the record froze. HALT, no verdict."""


# --------------------------------------------------------------------------- record + freeze
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_record() -> dict:
    return json.loads(RECORD_PATH.read_text(encoding="utf-8"))


def verify_lab_a_freeze(record: dict) -> dict:
    """Hash-verify every pinned lab-A artifact, then read the frozen parameters FROM THE
    ARTIFACTS (the record's quoted numbers are for humans; the artifacts are authoritative)."""
    by_path = {}
    for art in record["split"]["labA"]["frozenArtifacts"]:
        p = REPO_ROOT / art["path"]
        digest = sha256_bytes(p.read_bytes())
        if digest != art["sha256"]:
            raise FrozenEvidenceMismatch(
                "%s hashes to %s but the record froze %s. HALT: the lab-A freeze is broken and "
                "no verdict may be computed on an unverified parameterization."
                % (art["path"], digest, art["sha256"]))
        by_path[art["path"]] = p

    b3 = json.loads(by_path["audits/phase-b/b3-model-competition-result.json"]
                    .read_text(encoding="utf-8"))
    fside = json.loads(
        by_path["hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json"]
        .read_text(encoding="utf-8"))
    cohort = b3["cohorts"]["derived_eligible_1_to_8"]
    return {
        "scale_n": {int(k): float(v) for k, v in cohort["scaleN"].items()},
        "m1_k": float(cohort["fitted"]["M1_WEIBULL"]["params"][0]),
        "m2_sigma": float(cohort["fitted"]["M2_LOGNORMAL"]["params"][0]),
        "fside": {
            "converged": True,
            "mu": float(fside["fitted"]["F_MOTOR_STACK"]["mu"]),
            "tau": float(fside["fitted"]["F_MOTOR_STACK"]["tau"]),
        },
    }


# --------------------------------------------------------------------------- refusals
def _refusal(code: str, detail: str) -> dict:
    return {"refused": True, "code": code, "detail": detail,
            "rule": "experiments/predictions/P4-TRANSFER-PREDICTION-RECORD.v1.json "
                    "labBRegistration + motorCountTarget; docs/P4-TRANSFER-DATA-ACCESS-PROTOCOL.md "
                    "section 4"}


def _established(field) -> bool:
    return not (isinstance(field, dict) and "not_established" in field)


def check_registration(record: dict, cohort_sha256: str):
    """Refusal gates, in declared order. Returns None if scoring may proceed."""
    reg = record["labBRegistration"]
    markers = [k for k in ("cohortSha256", "motorCount", "licence", "commensurabilitySignoff")
               if not _established(reg.get(k))]
    if markers:
        return _refusal(
            "REFUSED_REGISTRATION_NOT_ESTABLISHED",
            "labBRegistration still carries not_established markers on: %s. No commensurate "
            "lab-B cohort is registered; there is nothing this harness may legitimately score."
            % ", ".join(markers))
    if not _established(record["motorCountTarget"]["declaredN"]):
        return _refusal(
            "REFUSED_N_NOT_DERIVED",
            "motorCountTarget.declaredN is not established: the committed real-data power-atlas "
            "derivation must exist BEFORE any lab-B field is read "
            "(docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:61-64).")
    registered = reg["cohortSha256"]
    if isinstance(registered, dict):
        registered = registered.get("value")
    if cohort_sha256 != registered:
        return _refusal(
            "REFUSED_SHA_NOT_REGISTERED",
            "cohort bytes hash to %s but the record registers %s. The registered hash is written "
            "BEFORE any field is read; a mismatch means these are not the registered bytes."
            % (cohort_sha256, registered))
    return None


# --------------------------------------------------------------------------- scoring (delegated)
def _project_events(raw_events):
    """Duration-only projection. Mark fields cannot pass this door (D5)."""
    return [{k: e[k] for k in _ALLOWED_FIELDS if k in e} for e in raw_events]


def score_cohort(record: dict, cohort: dict, cohort_sha256: str) -> dict:
    """Score a REGISTERED lab-B cohort once. Every number is delegated to the frozen scorer."""
    frozen = verify_lab_a_freeze(record)
    scale_n = frozen["scale_n"]

    events = _project_events(cohort["events"])
    bad_state = [e for e in events if int(e["stateN"]) not in scale_n]
    if bad_state:
        return _refusal(
            "REFUSED_INCOMMENSURATE",
            "axis: units — %d event(s) carry stateN outside the frozen support %s. The frozen "
            "scale_N does not extend, and forcing a common coefficient across incompatible "
            "assays is forbidden (cross-study-parity-report.json:653). Register as "
            "REFUSED-INCOMMENSURATE; never coerce." % (len(bad_state), sorted(scale_n)))

    # Frozen cohort rule (derived_eligible_1_to_8): right-censored events are EXCLUDED, counted.
    kept = [e for e in events if not bool(e.get("rightCensored", False))]
    n_censored_excluded = len(events) - len(kept)
    if not kept:
        return _refusal("REFUSED_INCOMMENSURATE",
                        "axis: units — zero uncensored events remain under the frozen cohort rule.")

    motor_ids = [str(e["motorId"]) for e in kept]
    states = np.array([int(e["stateN"]) for e in kept], dtype=np.int64)
    dur = np.array([float(e["durationS"]) for e in kept], dtype=np.float64)
    y = dur / np.array([scale_n[int(s)] for s in states], dtype=np.float64)
    censored = np.zeros(len(kept), dtype=bool)

    # Per-event NLPD, normalised scale, then the single frozen Jacobian to SECONDS.
    per_event = {
        "F_MOTOR_STACK": compare.score_fside_marginal_per_event(frozen["fside"], y, censored),
        "M1_WEIBULL": -baselines.m1_weibull_logpdf(y, frozen["m1_k"]),
        "M2_LOGNORMAL": -baselines.m2_lognormal_logpdf(y, frozen["m2_sigma"]),
    }
    per_event = {m: compare.to_seconds_scale(v, states, scale_n) for m, v in per_event.items()}

    per_motor, motor_equal = {}, {}
    keys_ref = None
    for m, v in per_event.items():
        keys, pm = score.per_motor_means(v, motor_ids)
        if keys_ref is None:
            keys_ref = keys
        assert list(keys) == list(keys_ref), "per-motor arrays misaligned across models"
        per_motor[m] = pm
        motor_equal[m] = float(score.motor_equal_nlpd(v, motor_ids))

    contrasts = {
        ref: score.contrast_with_ci(per_motor[ref], per_motor["F_MOTOR_STACK"],
                                    n_rep=N_BOOT, seed=BOOT_SEED)
        for ref in ("M1_WEIBULL", "M2_LOGNORMAL")
    }

    # ------------------------------------------------------------------ falsifiers (pre-declared)
    m2_lo, m2_hi = contrasts["M2_LOGNORMAL"]["interval"]
    fals_a_fired = bool(m2_hi < -FLOOR)
    verdicts = {ref: c["verdict"] for ref, c in contrasts.items()}
    fals_c_fired = any(v == status.RESOLVED_BELOW for v in verdicts.values())
    advantage = all(v == status.RESOLVED_ABOVE for v in verdicts.values())

    if fals_a_fired or fals_c_fired:
        door_outcome = "FALSIFIED — legitimate reportable negative, retained, not tuned away"
    elif advantage:
        door_outcome = ("PREDECLARED_ADVANTAGE_ESTABLISHED — input to the operator/gate process; "
                        "this harness relabels no gate and X10 is not moved by this output")
    else:
        door_outcome = ("NOT_ESTABLISHED — at least one baseline contrast contains 0; the "
                        "predeclared advantage is absent. Inconclusive is neither a pass nor a "
                        "refutation, and is never 'equivalent'.")

    declared_n = record["motorCountTarget"]["declaredN"]
    n_motors = len(keys_ref)
    if isinstance(declared_n, dict):
        declared_n_value = declared_n.get("value")
    else:
        declared_n_value = declared_n
    if isinstance(declared_n_value, (int, float)) and math.isfinite(float(declared_n_value)):
        power_status = ("ADEQUATE_BY_DECLARED_N" if n_motors >= declared_n_value
                        else "UNDERPOWERED — scored anyway, reported at actual interval width, "
                             "never widened away")
    else:
        power_status = "UNASSESSED — declaredN carries no numeric value"

    return {
        "schema": "uni.flagellum.p4-transfer-verdict/1.0.0",
        "recordId": record["recordId"],
        "doorStatus": "This verdict does not pass Door P4. Gate relabeling is not this file's to do.",
        "cohortSha256": cohort_sha256,
        "cohortTruthLabel": cohort.get("truthLabel", "UNDECLARED"),
        "nMotors": n_motors,
        "nEventsScored": len(kept),
        "nCensoredExcludedByFrozenRule": n_censored_excluded,
        "scaleConvention": "SECONDS (compare.to_seconds_scale, the single frozen Jacobian)",
        "aggregation": "MOTOR_EQUAL (score.motor_equal_nlpd; experimental unit = MOTOR)",
        "motorEqualNLPD": motor_equal,
        "contrasts": contrasts,
        "powerStatus": power_status,
        "falsifiers": {
            "FALSIFIER_A_M2_MATERIAL_ADVERSE": {
                "fired": fals_a_fired,
                "basis": "S(M2)-S(F) 95%% percentile interval [%r, %r]; fires iff hi < -%r"
                         % (m2_lo, m2_hi, FLOOR),
            },
            "FALSIFIER_B_PARAM_RECOVERY_OOD": {
                "fired": None,
                "statusNote": "NOT_EVALUATED_BY_THIS_HARNESS — requires the identifiability/"
                          "recovery machinery (audits/phase-b/b4-identifiability-robustness-"
                          "runner.py lineage) run against this cohort. Never silently passed.",
            },
            "FALSIFIER_C_FAILS_TO_BEAT_BASELINES": {
                "fired": fals_c_fired,
                "perBaselineVerdicts": verdicts,
                "basis": "fires iff any baseline contrast resolves entirely below 0",
            },
        },
        "doorOutcome": door_outcome,
    }


# --------------------------------------------------------------------------- self-test
def _synthetic_cohort(seed: int = 20260830) -> dict:
    """In-memory SYNTHETIC cohort. Never written to disk. Moves no gate, earns no label."""
    rng = np.random.default_rng(seed)
    events = []
    for m in range(24):
        motor = "SYN-MOTOR-%02d" % m
        for _ in range(int(rng.integers(4, 14))):
            state = int(rng.integers(1, 9))
            # lognormal-ish mean-one-ish normalised dwell, scaled to seconds by the frozen scale_N
            y = float(np.exp(rng.normal(-0.5, 1.0)))
            events.append({
                "motorId": motor,
                "stateN": state,
                "durationS": y * _SELF_TEST_SCALE_N[state],
                "rightCensored": bool(rng.random() < 0.03),
            })
    return {
        "truthLabel": "SYNTHETIC — generated in memory by p4_transfer_harness.py --self-test. "
                      "Nothing here is OBSERVED. No gate, no P-level, no claim.",
        "events": events,
    }


_SELF_TEST_SCALE_N = {1: 4.749152542372881, 2: 3.4826086956521736, 3: 6.350886075949368,
                      4: 5.062716049382717, 5: 7.948453608247423, 6: 14.389918699186993,
                      7: 18.245270270270268, 8: 24.52058394160584}


def self_test() -> int:
    record = load_record()
    cohort = _synthetic_cohort()
    cohort_bytes = json.dumps(cohort, sort_keys=True).encode("utf-8")
    cohort_sha = sha256_bytes(cohort_bytes)
    failures = []

    def check(name: str, ok: bool, detail: str = ""):
        line = "%s %s%s" % ("PASS" if ok else "FAIL", name, (" — " + detail) if detail else "")
        print(line)
        if not ok:
            failures.append(name)

    # 1. REFUSAL (b): the committed record's registration is not_established -> refuse.
    r1 = check_registration(record, cohort_sha)
    check("refusal-not-established", bool(r1) and r1["code"] == "REFUSED_REGISTRATION_NOT_ESTABLISHED",
          (r1 or {}).get("code", "no refusal emitted"))

    # 2. REFUSAL (a): registration filled, but with a DIFFERENT sha -> refuse.
    reg_wrong = copy.deepcopy(record)
    reg_wrong["labBRegistration"] = {
        "cohortSha256": "0" * 64, "motorCount": 24, "licence": "SYNTHETIC-SELF-TEST",
        "commensurabilitySignoff": "SYNTHETIC-SELF-TEST (no operator signature is claimed)"}
    reg_wrong["motorCountTarget"] = dict(reg_wrong["motorCountTarget"], declaredN=9999)
    r2 = check_registration(reg_wrong, cohort_sha)
    check("refusal-unregistered-sha", bool(r2) and r2["code"] == "REFUSED_SHA_NOT_REGISTERED",
          (r2 or {}).get("code", "no refusal emitted"))

    # 3. SCORING PATH: registration matches the synthetic bytes -> the frozen scorer scores.
    reg_ok = copy.deepcopy(reg_wrong)
    reg_ok["labBRegistration"]["cohortSha256"] = cohort_sha
    r3 = check_registration(reg_ok, cohort_sha)
    check("registration-accepts-registered-sha", r3 is None,
          "" if r3 is None else r3["code"])
    verdict = score_cohort(reg_ok, cohort, cohort_sha)
    check("scoring-path-scores", not verdict.get("refused")
          and all(math.isfinite(v) for v in verdict["motorEqualNLPD"].values()),
          "motorEqualNLPD=%s" % json.dumps(verdict.get("motorEqualNLPD", {})))
    check("verdict-carries-three-falsifiers",
          set(verdict.get("falsifiers", {})) == {"FALSIFIER_A_M2_MATERIAL_ADVERSE",
                                                 "FALSIFIER_B_PARAM_RECOVERY_OOD",
                                                 "FALSIFIER_C_FAILS_TO_BEAT_BASELINES"})
    check("falsifier-b-not-silently-passed",
          verdict["falsifiers"]["FALSIFIER_B_PARAM_RECOVERY_OOD"]["fired"] is None)
    check("verdict-declares-underpowered",
          "UNDERPOWERED" in verdict["powerStatus"],
          "declaredN=9999 vs 24 synthetic motors -> %s" % verdict["powerStatus"])
    check("verdict-relabels-no-gate", "does not pass Door P4" in verdict["doorStatus"])

    # 4. Determinism of the scoring path (same bytes, same numbers).
    verdict2 = score_cohort(reg_ok, cohort, cohort_sha)
    check("scoring-deterministic",
          json.dumps(verdict, sort_keys=True) == json.dumps(verdict2, sort_keys=True))

    # 5. The freeze check bites: corrupt one pinned sha and the harness HALTS.
    broken = copy.deepcopy(reg_ok)
    broken["split"]["labA"]["frozenArtifacts"][0]["sha256"] = "f" * 64
    try:
        score_cohort(broken, cohort, cohort_sha)
        check("frozen-evidence-check-bites", False, "no halt on corrupted lab-A pin")
    except FrozenEvidenceMismatch:
        check("frozen-evidence-check-bites", True)

    print("SELF-TEST %s — synthetic only; no gate moved; no file written."
          % ("PASS" if not failures else ("FAIL: " + ", ".join(failures))))
    return EXIT_OK if not failures else EXIT_HALT


# --------------------------------------------------------------------------- entry
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--cohort", help="path to a REGISTERED lab-B cohort JSON "
                                     "({truthLabel, events:[{motorId,stateN,durationS,rightCensored}]})")
    ap.add_argument("--self-test", action="store_true",
                    help="prove refusal paths refuse and the scoring path scores, on in-memory "
                         "SYNTHETIC data")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.cohort:
        ap.error("either --cohort or --self-test is required")

    record = load_record()
    cohort_path = Path(args.cohort)
    cohort_bytes = cohort_path.read_bytes()
    cohort_sha = sha256_bytes(cohort_bytes)

    refusal = check_registration(record, cohort_sha)
    if refusal:
        print(json.dumps(refusal, indent=2))
        return EXIT_REFUSED

    cohort = json.loads(cohort_bytes.decode("utf-8"))
    out = score_cohort(record, cohort, cohort_sha)
    print(json.dumps(out, indent=2))
    return EXIT_REFUSED if out.get("refused") else EXIT_OK


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FrozenEvidenceMismatch as exc:
        print("HALT: %s" % exc, file=sys.stderr)
        raise SystemExit(EXIT_HALT)
