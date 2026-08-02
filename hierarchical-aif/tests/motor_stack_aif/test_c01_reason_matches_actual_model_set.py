"""D4 reproducer — a cell's recorded reason must describe the computation it performs.

The committed B4C01 reason cites "~15-25 min per M4/M7-inclusive competition", but the cell's
code explicitly skips M4/M7/M8. The recorded justification describes a computation the cell does
not perform.

This test reads the FROZEN result artifact read-only. It never modifies it.
"""
import re
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge  # noqa: E402

# The models B4C01/B4C02 actually fit, per the runner source.
C01_ACTUAL_MODELS = {
    "M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL",
    "M3_TWO_TIMESCALE", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT",
}
C01_SKIPPED_MODELS = {"M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"}


@pytest.fixture(scope="module")
def c01_reason():
    cells = _bridge.b4_result()["cells"]
    return cells["B4C01"].get("reason", "")


@pytest.mark.xfail(
    strict=True,
    reason="D4_C01_REASON_MISMATCH: the FROZEN B4 artifact cites M4/M7 as the cost driver for a "
           "cell that skips them. The artifact is historical evidence and must NOT be edited, so "
           "this stays xfail. strict=True means an XPASS is itself a failure - it would indicate "
           "the frozen artifact was mutated, which is a contract violation.",
)
def test_frozen_c01_reason_mismatch_is_a_known_historical_defect(c01_reason):
    """D4 pinned against the frozen artifact. Expected to fail; must never be 'fixed' in place."""
    mentions_m4 = bool(re.search(r"\bM4\b", c01_reason))
    mentions_m7 = bool(re.search(r"\bM7\b", c01_reason))
    assert not (mentions_m4 or mentions_m7), (
        "B4C01 skips M4/M7/M8 but its recorded reason cites them as the cost driver: %r"
        % c01_reason
    )


def test_corrected_reason_matches_the_actual_model_set():
    """The replacement reason used in corrected reports must describe what the cell computes."""
    from motor_stack_aif import corrected_reasons

    reason = corrected_reasons.C01_REASON

    # The defect was citing M4/M7 as the COST DRIVER. Naming them as skipped is correct and
    # required, so test for the defective framing rather than for the mere substring.
    assert "M4/M7-inclusive" not in reason, (
        "corrected reason must not attribute cost to an M4/M7-inclusive competition"
    )
    assert re.search(r"skips?\s+M4", reason), (
        "corrected reason must state that M4 is skipped"
    )
    assert "simple" in reason.lower() or "M6" in reason, (
        "corrected reason should name the model set actually fitted"
    )
    assert "14.5" in reason or "measured" in reason.lower(), (
        "corrected reason must be grounded in measured runtime"
    )


def test_every_corrected_reason_is_grounded_in_measurement():
    """No corrected reason may assert a cost without a measured basis."""
    from motor_stack_aif import corrected_reasons

    for cell, reason in corrected_reasons.BY_CELL.items():
        assert "measured" in reason.lower(), (
            "%s corrected reason must cite measured runtime" % cell
        )
        assert "M4/M7-inclusive" not in reason, (
            "%s must not reuse the defective cost framing" % cell
        )


def test_runner_source_confirms_the_skip():
    """Ground the claim in the runner source, not only in the artifact text."""
    src = (_bridge.REPO_ROOT / "audits" / "phase-b"
           / "b4-identifiability-robustness-runner.py").read_text(encoding="utf-8")
    assert "skip M4/M7/M8" in src, "expected the runner to document the skip"
    for m in C01_SKIPPED_MODELS:
        assert m in src


def test_actual_model_set_is_the_simple_competitors():
    src = (_bridge.REPO_ROOT / "audits" / "phase-b"
           / "b4-identifiability-robustness-runner.py").read_text(encoding="utf-8")
    for m in C01_ACTUAL_MODELS:
        assert m in src, "expected %s in the C01 sub_models list" % m
