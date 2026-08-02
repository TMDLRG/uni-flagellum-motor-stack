"""Run-status and verdict semantics.

Encodes the frozen status vocabulary so a partial run cannot be reported as a verdict:

    actual_N == 0                -> NOT_RUN
    0 < actual_N < planned_N     -> PARTIAL_NOT_ESTABLISHED
                                    (stronger ONLY with a PROSPECTIVE sequential stopping rule
                                     declared before the run)
    actual_N == planned_N        -> ELIGIBLE_FOR_FROZEN_VERDICT

A point estimate is never a verdict. A confidence interval that crosses the decision threshold
is NOT_ESTABLISHED, however large the point-estimate gap.

This module exists because B4C11 U4 reported REFUTED_U4_PARTIAL from 30 of 2000 replicates with
no prospective stopping rule (see D1/D2 in the defect ledger).
"""
from __future__ import annotations

NOT_RUN = "NOT_RUN"
PARTIAL = "PARTIAL_NOT_ESTABLISHED"
ELIGIBLE = "ELIGIBLE_FOR_FROZEN_VERDICT"
# F15 (Phase 8 item 8.4). `actual_n > planned_n` used to fall into ELIGIBLE with everything else
# that met its plan. An overrun is NOT a longer success: nobody pre-registered stopping there, so
# the stopping point was chosen after seeing the data. It gets its own word.
OVERRUN = "OVERRUN"

NOT_ESTABLISHED = "NOT_ESTABLISHED"
RESOLVED_ABOVE = "RESOLVED_ABOVE"
RESOLVED_BELOW = "RESOLVED_BELOW"


def classify_run(actual_n: int, planned_n: int,
                 prospective_stopping_rule: bool = False) -> str:
    if planned_n <= 0:
        raise ValueError("planned_n must be positive; got %r" % planned_n)
    if actual_n < 0:
        raise ValueError("actual_n must be non-negative; got %r" % actual_n)
    if actual_n == 0:
        return NOT_RUN
    if actual_n > planned_n:
        return OVERRUN
    if actual_n == planned_n:
        return ELIGIBLE
    if prospective_stopping_rule:
        return ELIGIBLE
    return PARTIAL


def may_claim_refutation(actual_n: int, planned_n: int,
                         prospective_stopping_rule: bool = False) -> bool:
    """A frozen prediction may only be refuted from a run eligible for a frozen verdict."""
    return classify_run(actual_n, planned_n, prospective_stopping_rule) == ELIGIBLE


def verdict_from_ci(lo, hi, threshold: float = 0.0) -> str:
    """CI-bound verdict. Point estimates are refused outright."""
    if lo is None or hi is None:
        raise ValueError(
            "a verdict requires an interval; a point estimate is not a verdict"
        )
    if lo > hi:
        raise ValueError("interval bounds inverted: lo=%r hi=%r" % (lo, hi))
    if lo <= threshold <= hi:
        return NOT_ESTABLISHED
    return RESOLVED_ABOVE if lo > threshold else RESOLVED_BELOW
