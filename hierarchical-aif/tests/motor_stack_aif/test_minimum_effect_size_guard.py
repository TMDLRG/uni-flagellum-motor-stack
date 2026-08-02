"""D10 — a CI-bound verdict is not a scientific finding without a minimum effect size.

THE DEFECT, AS OBSERVED
-----------------------
The frozen convention decides a contrast by whether its paired motor-cluster bootstrap interval
excludes 0. That rule has NO practical-significance floor. A paired bootstrap resamples MOTORS, so
if a per-motor difference is CONSISTENT IN SIGN it will be "resolved" no matter how small it is.

Observed 2026-07-22, contrasting the F-side motor stack against frozen `M7_HIERARCHICAL_MOTOR`:

    point estimate  +2.506984e-07 nats
    95% interval    [+1.604451e-07, +3.374688e-07]   -> excludes 0 -> RESOLVED_ABOVE
    resolution floor 0.042 nats                      -> effect is ~168000x SMALLER

The two models are the same model to numerical precision (the F-side hierarchy re-derives M7).
Reporting that as "the candidate beats M7" would be truth laundering of the purest kind: a
numerically identical model presented as a winner on the strength of float noise with a consistent
sign.

WHAT THIS FILE ENFORCES
-----------------------
  1. The frozen verdict is NEVER altered or softened — it is reported verbatim.
  2. Every resolved contrast MUST carry a `scientificReading`, and one whose effect sits below the
     resolution floor MUST be flagged and MUST NOT be reportable as a win.
  3. The guard is not vacuous: a genuinely material effect must still classify as MATERIAL.

This does not change any frozen threshold, criterion, or interval. It adds the interpretation that
the frozen rule cannot supply on its own.

D5 declaration: no data is loaded; this reads a recorded result artifact and exercises pure logic.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import score  # noqa: E402

RESULT = (REPO / "hierarchical-aif" / "results" / "motor_stack_aif"
          / "M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json")
FLOOR = 0.042


@pytest.fixture(scope="module")
def result():
    if not RESULT.exists():
        pytest.skip("M4/M6/M7 contrast artifact not present in this working tree")
    return json.loads(RESULT.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- the observed instance
def test_the_m7_contrast_is_resolved_by_the_frozen_rule_but_flagged_as_null(result):
    """PINS D10. The frozen verdict stands; the scientific reading overrides how it may be used."""
    c = result["contrasts"]["M7_HIERARCHICAL_MOTOR"]

    # the frozen rule genuinely did resolve it - we are not pretending otherwise
    assert c["verdict"] == "RESOLVED_ABOVE"
    assert c["interval"][0] > 0.0, "the interval really does exclude 0"

    # ... and the effect is absurdly small
    assert abs(c["pointEstimate"]) < 1e-5, (
        "the M7 contrast effect grew beyond 1e-5 nats; the F-side model was supposed to be a "
        "numerical re-derivation of M7. Investigate before accepting.")

    assert c["scientificReading"]["classification"] == "SCIENTIFICALLY_NULL"
    assert "WARNING" in c, "a sub-floor resolved contrast must carry an explicit warning"
    assert c["reportableAsAWin"] is False, (
        "a 2.5e-07-nat difference must NEVER be reportable as one model beating another")


def test_no_contrast_in_the_artifact_is_reportable_as_a_win_below_the_floor(result):
    """The general rule, applied to every contrast present."""
    for mid, c in result["contrasts"].items():
        if c.get("reportableAsAWin"):
            assert abs(c["pointEstimate"]) >= FLOOR, (
                "%s is marked reportableAsAWin with an effect of %r nats, below the %r floor"
                % (mid, c["pointEstimate"], FLOOR))


def test_every_contrast_carries_a_scientific_reading(result):
    for mid, c in result["contrasts"].items():
        sr = c.get("scientificReading")
        assert sr, "%s has no scientificReading" % mid
        assert sr["classification"] in {"SCIENTIFICALLY_NULL", "SUB_FLOOR_EFFECT", "MATERIAL"}
        assert sr["frozenVerdictUnaltered"] == c["verdict"], (
            "%s: the scientific reading must carry the frozen verdict VERBATIM, never a softened "
            "version of it" % mid)


def test_the_oracle_gate_passed_so_these_arrays_are_validated(result):
    """Without the oracle gate the per-motor arrays would be unvalidated recomputations."""
    assert result["oracleGate"]["status"] == "PASS"
    for chk in result["oracleGate"]["checks"]:
        assert chk["pass"], chk
        assert chk["absResidual"] <= result["oracleGate"]["tolerance"]


def test_the_post_hoc_status_is_declared_not_hidden(result):
    assert result["status"] == "POST_HOC_COVERAGE_EXTENSION"
    assert "POST_HOC" in result["postHocDeclaration"]
    assert result["familySize"] == 9, "the family grew from 6 to 9; that must stay recorded"
    for c in result["contrasts"].values():
        assert "bonferroniCompanion" in c, "a post-hoc family needs a multiplicity sensitivity"


# ---------------------------------------------------------------- non-vacuity
def test_a_consistent_but_tiny_difference_really_does_resolve_under_the_frozen_rule():
    """NON-VACUITY / root cause. Demonstrates the mechanism D10 describes, from first principles.

    A vanishingly small difference with a consistent sign is resolved by a paired motor-cluster
    bootstrap. If this test ever fails, the mechanism behind D10 has changed and the guard should
    be re-derived rather than trusted.
    """
    rng = np.random.default_rng(12345)
    base = rng.normal(3.4, 0.8, size=19)          # 19 motors, realistic spread
    tiny = base + 1e-7                            # consistent, absurdly small offset
    c = score.contrast_with_ci(tiny, base, n_rep=2000, seed=20260717)
    assert c["verdict"] == "RESOLVED_ABOVE", (
        "a consistent 1e-7 offset no longer resolves; the D10 mechanism has changed")
    assert abs(c["pointEstimate"]) < 1e-6
    assert abs(c["pointEstimate"]) < FLOOR


def test_a_material_effect_is_still_classified_material():
    """NON-VACUITY: the guard must not simply label everything null."""
    rng = np.random.default_rng(999)
    base = rng.normal(3.4, 0.05, size=19)
    better = base - 0.20                          # far above the floor
    c = score.contrast_with_ci(base, better, n_rep=2000, seed=20260717)
    assert c["verdict"] == "RESOLVED_ABOVE"
    assert abs(c["pointEstimate"]) > FLOOR, (
        "a 0.20-nat effect must exceed the floor, otherwise the guard would suppress real findings")


def test_an_interval_wholly_inside_the_floor_is_not_called_equivalence(result):
    """`SCIENTIFICALLY_NULL` must not be read as a formal equivalence result.

    The floor is a HEURISTIC derived from the narrowest frozen B3 contrast. It was never
    pre-specified as an equivalence margin, so an interval sitting inside it is NOT a TOST-style
    equivalence claim. `CLAUDE.md`: underpowered is not equivalence.
    """
    for mid, c in result["contrasts"].items():
        sr = c["scientificReading"]
        if sr["classification"] == "SCIENTIFICALLY_NULL":
            blob = json.dumps(c).lower()
            assert "equivalen" not in blob, (
                "%s describes a sub-floor interval using equivalence language; the floor is a "
                "heuristic, not a pre-specified equivalence margin" % mid)
