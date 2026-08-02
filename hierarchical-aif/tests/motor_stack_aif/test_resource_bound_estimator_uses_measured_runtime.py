"""D2 reproducer — a RESOURCE_BOUND status must be justified by measured runtime.

RED BEFORE FIX: no estimator exists; the recorded reasons cite hour figures that are wrong by
17-29x and that describe a model set the cell does not fit.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import resource  # noqa: E402

# Measured on the frozen cohort, 2026-07-21, recorded in RESOURCE-BOUND-RECLASSIFICATION.md
MEASURED = {
    "fit_simple_models": 32.0,
    "fit_m6": 20.1,
    "_fit_m4_reduced": 3.8,
    "_fit_m7_reduced": 36.2,
}


def test_estimate_requires_measured_seconds():
    """An estimate with no measurement behind it must be refused, not guessed."""
    with pytest.raises(Exception):
        resource.estimate_hours(n=2000, per_unit_seconds=None)


def test_estimate_is_arithmetic_on_measured_runtime():
    est = resource.estimate_hours(n=2000, per_unit_seconds=MEASURED["_fit_m4_reduced"])
    assert est == pytest.approx(2000 * 3.8 / 3600.0, rel=1e-9)
    assert 2.0 < est < 2.2, "C10 at frozen N is ~2.1 h"


def test_c10_at_frozen_n_is_feasible_and_should_not_have_been_partial():
    est = resource.estimate_hours(n=2000, per_unit_seconds=MEASURED["_fit_m4_reduced"])
    assert resource.is_feasible(est, budget_hours=24.0)


def test_c02_at_frozen_n_is_feasible():
    """C02 is the HIGH-risk misspecified-world discriminator; it fits simple models + M6 only."""
    per_sim = MEASURED["fit_simple_models"] + MEASURED["fit_m6"]
    est = resource.estimate_hours(n=600, per_unit_seconds=per_sim)
    assert 8.0 < est < 9.5, "C02 at frozen N is ~8.7 h, not the recorded 150-250 h"
    assert resource.is_feasible(est, budget_hours=24.0)


def test_recorded_claims_are_flagged_against_measurement():
    """The reclassification must detect an order-of-magnitude discrepancy."""
    per_sim = MEASURED["fit_simple_models"] + MEASURED["fit_m6"]
    flag = resource.compare_to_recorded(
        measured_hours=resource.estimate_hours(n=1000, per_unit_seconds=per_sim),
        recorded_low_hours=250.0, recorded_high_hours=400.0,
    )
    assert flag["status"] == "RECORDED_OVERSTATED"
    assert flag["ratio_to_recorded_low"] > 10.0
