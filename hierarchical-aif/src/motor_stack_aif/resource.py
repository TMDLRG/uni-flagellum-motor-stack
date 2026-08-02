"""Measured-runtime resource estimation.

D2_RESOURCE_BOUND_OVERESTIMATE: a RESOURCE_BOUND status is only honest if the resource claim is
true. The committed B4 reasons cited 250-400 h (C01) and 150-250 h (C02) against measured
projections of ~14.5 h and ~8.7 h — overstated by 17-29x — and justified the cost by a model set
(M4/M7/M8) those cells explicitly skip.

This module refuses to produce an estimate without a measurement behind it.
"""
from __future__ import annotations

RECORDED_OVERSTATED = "RECORDED_OVERSTATED"
RECORDED_UNDERSTATED = "RECORDED_UNDERSTATED"
RECORDED_CONSISTENT = "RECORDED_CONSISTENT"

# Order-of-magnitude trigger for flagging a recorded claim against measurement.
OVERSTATEMENT_TRIGGER = 2.0


def estimate_hours(n: int, per_unit_seconds) -> float:
    """Project wall-clock hours from a MEASURED per-unit cost."""
    if per_unit_seconds is None:
        raise ValueError(
            "refusing to estimate without a measured per-unit runtime; "
            "measure the fit path before declaring RESOURCE_BOUND"
        )
    if per_unit_seconds <= 0:
        raise ValueError("per_unit_seconds must be positive; got %r" % per_unit_seconds)
    if n < 0:
        raise ValueError("n must be non-negative; got %r" % n)
    return n * float(per_unit_seconds) / 3600.0


def is_feasible(estimate_hours_value: float, budget_hours: float) -> bool:
    return estimate_hours_value <= budget_hours


def compare_to_recorded(measured_hours: float,
                        recorded_low_hours: float,
                        recorded_high_hours: float) -> dict:
    """Compare a measured projection against a recorded claim and flag discrepancies."""
    if measured_hours <= 0:
        raise ValueError("measured_hours must be positive")
    ratio_low = recorded_low_hours / measured_hours
    ratio_high = recorded_high_hours / measured_hours
    if ratio_low >= OVERSTATEMENT_TRIGGER:
        status = RECORDED_OVERSTATED
    elif ratio_high <= 1.0 / OVERSTATEMENT_TRIGGER:
        status = RECORDED_UNDERSTATED
    else:
        status = RECORDED_CONSISTENT
    return {
        "status": status,
        "measured_hours": measured_hours,
        "recorded_low_hours": recorded_low_hours,
        "recorded_high_hours": recorded_high_hours,
        "ratio_to_recorded_low": ratio_low,
        "ratio_to_recorded_high": ratio_high,
    }
