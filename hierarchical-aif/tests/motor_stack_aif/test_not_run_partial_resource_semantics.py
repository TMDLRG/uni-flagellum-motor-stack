"""Status semantics — actual_N vs planned_N must map to the frozen status vocabulary.

    actual_N == 0                      -> NOT_RUN
    0 < actual_N < planned_N           -> PARTIAL_NOT_ESTABLISHED
                                          (unless a PROSPECTIVE sequential stopping rule exists)
    actual_N == planned_N              -> ELIGIBLE_FOR_FROZEN_VERDICT

A point-estimate "win" whose CI crosses the threshold is NOT_ESTABLISHED.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import status  # noqa: E402


def test_zero_replicates_is_not_run():
    assert status.classify_run(actual_n=0, planned_n=2000) == "NOT_RUN"


def test_partial_replicates_is_not_established():
    assert status.classify_run(actual_n=30, planned_n=2000) == "PARTIAL_NOT_ESTABLISHED"
    assert status.classify_run(actual_n=100, planned_n=2000) == "PARTIAL_NOT_ESTABLISHED"
    assert status.classify_run(actual_n=1999, planned_n=2000) == "PARTIAL_NOT_ESTABLISHED"


def test_full_replicates_is_eligible_for_verdict():
    assert status.classify_run(actual_n=2000, planned_n=2000) == "ELIGIBLE_FOR_FROZEN_VERDICT"


def test_partial_may_be_stronger_only_with_prospective_stopping_rule():
    assert status.classify_run(
        actual_n=30, planned_n=2000, prospective_stopping_rule=True
    ) == "ELIGIBLE_FOR_FROZEN_VERDICT"


def test_a_partial_run_may_not_be_reported_as_a_refutation():
    """B4C11 U4 reported REFUTED_U4_PARTIAL from 30/2000 with no stopping rule."""
    assert not status.may_claim_refutation(actual_n=30, planned_n=2000)
    assert not status.may_claim_refutation(actual_n=100, planned_n=2000)
    assert status.may_claim_refutation(actual_n=2000, planned_n=2000)


def test_ci_crossing_threshold_is_not_established():
    assert status.verdict_from_ci(lo=-0.043, hi=0.086, threshold=0.0) == "NOT_ESTABLISHED"
    assert status.verdict_from_ci(lo=0.01, hi=0.086, threshold=0.0) == "RESOLVED_ABOVE"
    assert status.verdict_from_ci(lo=-0.09, hi=-0.01, threshold=0.0) == "RESOLVED_BELOW"


def test_point_estimate_alone_never_produces_a_verdict():
    with pytest.raises(Exception):
        status.verdict_from_ci(lo=None, hi=None, threshold=0.0)
