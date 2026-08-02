"""Phase 9 step 4.3 — Phase 8 items 8.1 to 8.4, four silent collapses that must become halts.

MUST FAIL BEFORE THE CODE EXISTS, for this reason:
  each of these turns a fault into a NUMBER. Nothing raises, nothing warns, and the result is
  indistinguishable from a sound one.

    8.1  score.py       bare `zip(per_event_nlpd, motor_ids)` truncates silently
                        F17: arrays of different length must RAISE BEFORE ANY AGGREGATE
    8.2  fit.py         `res.success` stored as "converged" and never checked
                        F16: halt before scoring; write no artifact
    8.3  compare.py     the P-ladder is off by one and omits P7 entirely
    8.4  status.py      `actual_n > planned_n` collapses into ELIGIBLE
                        F15: an overrun is FLAGGED, not silently eligible

MEASURED LIVE 2026-07-27, all four still present. These are not hypotheticals: the flagellum's
own defect ledger records each of them, and the Control Plane's `Run` module was written against
them in Phase 4 — the refusals were built for a body that still had the disease.

## Why a length mismatch must raise rather than warn

`zip` stopping at the shorter argument is the most expensive convenience in numerical Python. A
score array and a motor-id array that disagree produce a MEAN over a silently shortened pairing:
every event after the truncation point is dropped, the number that comes out is well-formed, and
nothing anywhere says so. The unit here is the MOTOR, so dropping events silently reweights the
motors that survive.

## Why a non-converged fit must not reach a score

An optimiser that reports failure has still returned finite parameters. Scoring them yields a
finite NLPD that is comparable-looking and meaningless. F16 says halt BEFORE scoring, and the
halt belongs at the scoring boundary rather than at the fit, because a fit is allowed to fail —
what is not allowed is a failed fit being scored as though it had succeeded.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import compare, score, status  # noqa: E402

def _code_only(path: Path) -> str:
    """Source with whole-line comments stripped — USE, not MENTION.

    The first version of this file scanned the raw source for "P5 transfer" and CONVICTED THE
    COMMENT THAT RECORDS THE OLD WORDING. That is precisely the trap step 4.4's falsifier names —
    "it convicts a comment recording a removal" — and it caught me here first, which is the
    cheapest place it could have.

    A correction that cannot say what it corrected is a worse document. So the comment stays and
    the scanner learns the difference.
    """
    return "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


COMPARE_SRC = _code_only(SRC / "motor_stack_aif" / "compare.py")


# ---- 8.1: a length mismatch raises before any aggregate --------------------------------------


def test_8_1_motor_equal_nlpd_RAISES_when_the_arrays_disagree():
    with pytest.raises(ValueError) as exc:
        score.motor_equal_nlpd([1.0, 2.0, 3.0], ["m1", "m2"])
    assert "3" in str(exc.value) and "2" in str(exc.value), (
        "the refusal must name BOTH lengths — a caller who cannot see which side is short "
        "cannot fix it: %r" % str(exc.value))


def test_8_1_per_motor_means_RAISES_when_the_arrays_disagree():
    with pytest.raises(ValueError):
        score.per_motor_means([1.0, 2.0, 3.0], ["m1", "m2"])


def test_8_1_it_raises_in_BOTH_directions_not_only_when_scores_are_longer():
    with pytest.raises(ValueError):
        score.motor_equal_nlpd([1.0], ["m1", "m2", "m3"])


def test_8_1_NEGATIVE_CONTROL_equal_lengths_still_compute():
    """A guard that refuses everything is not a guard."""
    v = score.motor_equal_nlpd([1.0, 3.0, 5.0, 7.0], ["m1", "m1", "m2", "m2"])
    assert v == pytest.approx((2.0 + 6.0) / 2)

    keys, means = score.per_motor_means([1.0, 3.0, 5.0], ["m1", "m1", "m2"])
    assert keys == ["m1", "m2"] and means == pytest.approx([2.0, 5.0])


def test_8_1_THE_DEFECT_ITSELF_a_truncated_pairing_changes_the_answer():
    """The reason this matters, stated as a number rather than as a worry."""
    full = score.motor_equal_nlpd([1.0, 3.0, 5.0, 100.0], ["m1", "m1", "m2", "m2"])
    truncated = score.motor_equal_nlpd([1.0, 3.0, 5.0], ["m1", "m1", "m2"])
    assert full != pytest.approx(truncated), (
        "dropping one event moved the motor-equal mean; before this guard, that drop was silent")


# ---- 8.2: a non-converged fit never reaches a score -------------------------------------------


def _fit(converged: bool) -> dict:
    return {"mu": 0.0, "tau": 0.3, "converged": converged, "trainNLL": 1.0}


def test_8_2_scoring_a_NON_CONVERGED_fit_HALTS():
    with pytest.raises(Exception) as exc:
        compare.score_fside_marginal_per_event(_fit(False), [1.0, 2.0], [False, False])
    assert "converg" in str(exc.value).lower(), (
        "the halt must say WHY — 'it failed' is not a finding: %r" % str(exc.value))


def test_8_2_NEGATIVE_CONTROL_a_converged_fit_still_scores():
    out = compare.score_fside_marginal_per_event(_fit(True), [1.0, 2.0], [False, False])
    assert len(out) == 2 and np.all(np.isfinite(out))


def test_8_2_a_fit_with_NO_convergence_field_is_refused_rather_than_assumed_good():
    """Absence of the flag is not evidence of convergence. Defaulting to True is the bug."""
    with pytest.raises(Exception):
        compare.score_fside_marginal_per_event({"mu": 0.0, "tau": 0.3}, [1.0], [False])


# ---- 8.3: the parity ladder is off by one and omits P7 ----------------------------------------


def test_8_3_the_ladder_no_longer_calls_transfer_P5():
    assert "P5 transfer" not in COMPARE_SRC, (
        "CLAUDE.md's ladder is P4 transfer, P5 interventional. Calling transfer P5 shifts every "
        "level above it and reads as a stronger claim than the evidence licenses.")


def test_8_3_the_ladder_names_transfer_as_P4_and_intervention_as_P5():
    assert "P4 transfer" in COMPARE_SRC
    assert "P5 intervention" in COMPARE_SRC


def test_8_3_P7_independent_replication_is_no_longer_omitted():
    assert "P7" in COMPARE_SRC, (
        "P7 is independent replication — the level this programme is furthest from and the one "
        "most easily forgotten by omitting it from the list a reader sees")


# ---- 8.4: an overrun is flagged, not silently eligible ----------------------------------------


def test_8_4_an_OVERRUN_is_its_own_word():
    assert status.classify_run(actual_n=25, planned_n=19) == status.OVERRUN


def test_8_4_NEGATIVE_CONTROL_exactly_planned_is_still_ELIGIBLE():
    assert status.classify_run(actual_n=19, planned_n=19) == status.ELIGIBLE


def test_8_4_the_other_words_are_untouched():
    assert status.classify_run(actual_n=0, planned_n=19) == status.NOT_RUN
    assert status.classify_run(actual_n=5, planned_n=19) == status.PARTIAL
    assert status.classify_run(actual_n=5, planned_n=19, prospective_stopping_rule=True) == status.ELIGIBLE


def test_8_4_AN_OVERRUN_MAY_NOT_CLAIM_A_REFUTATION():
    """F15's point. An overrun is not a longer success — nobody pre-registered stopping there."""
    assert status.may_claim_refutation(actual_n=25, planned_n=19) is False
    assert status.may_claim_refutation(actual_n=19, planned_n=19) is True
