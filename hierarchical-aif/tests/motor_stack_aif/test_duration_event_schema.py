"""Lmotor-0 observed-blanket schema and split integrity — DURATION CHANNEL ONLY.

D5 declaration: every call in this file uses ``mode='duration_only'``. No mark field
(``nextStateN`` / ``direction`` / ``jump``) is read, printed, or reasoned about anywhere here.

Coverage note (audit): ``test_fside_motor_stack.py::test_duration_only_mode_never_returns_marks``
already asserts the mark fields are ``None`` for the ``states=1..8`` subset. This file closes the
gaps that check left open: the record TYPE and immutability, duration positivity/finiteness, the
declared state alphabet (and that filtering it is load-bearing), the partition vocabulary, and
that ``partition`` agrees with an INDEPENDENTLY recomputed ``sha256(motorId) % 5``.
"""
from __future__ import annotations

import dataclasses
import hashlib
import math
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, events  # noqa: E402

# The state set the frozen B3 `derived_eligible_1_to_8` cohort models.
DECLARED_ALPHABET = frozenset(range(1, 9))

# The frozen split rule, restated from the B3 protocol rather than imported from the runner.
# Reimplementing it here is deliberate: importing `b3.sha256_mod5` would make the check circular.
def independent_sha256_mod5(motor_id: str) -> int:
    return int(hashlib.sha256(motor_id.encode("utf-8")).hexdigest(), 16) % 5


@pytest.fixture(scope="module")
def ev_alphabet():
    return events.load_events(mode=events.DURATION_ONLY, states=range(1, 9))


@pytest.fixture(scope="module")
def ev_all():
    return events.load_events(mode=events.DURATION_ONLY)


# ---------------------------------------------------------------- typing / immutability
def test_records_are_the_frozen_typed_dataclass(ev_all):
    assert ev_all, "expected a non-empty observed blanket"
    assert dataclasses.is_dataclass(events.ObservedEvent)
    for e in ev_all:
        assert isinstance(e, events.ObservedEvent)


def test_record_field_types_are_exactly_as_declared(ev_all):
    """A silently str-typed stateN or int-typed durationS would poison every downstream scale."""
    for e in ev_all:
        assert type(e.event_id) is str
        assert type(e.motor_id) is str
        assert type(e.partition) is str
        assert type(e.state_n) is int and not isinstance(e.state_n, bool)
        assert type(e.duration_s) is float
        assert type(e.right_censored) is bool


def test_records_are_immutable(ev_all):
    """Frozen: a scoring pass must not be able to edit an observation in place."""
    with pytest.raises(dataclasses.FrozenInstanceError):
        ev_all[0].duration_s = 1.0


# ---------------------------------------------------------------- duration channel only
def test_duration_only_leaves_every_mark_field_none_on_the_whole_dataset(ev_all):
    """Extends the existing states=1..8 check to the UNFILTERED dataset and to `has_mark`."""
    for e in ev_all:
        assert e.next_state_n is None
        assert e.direction is None
        assert e.jump is None
        assert e.has_mark is False


# ---------------------------------------------------------------- durations
def test_durations_are_positive_and_finite(ev_all):
    for e in ev_all:
        assert math.isfinite(e.duration_s), e.event_id
        assert e.duration_s > 0.0, e.event_id


def test_right_censoring_flag_is_present_and_both_values_occur(ev_all):
    """If no event were censored the censoring branch would never be exercised by real data."""
    n_cens = sum(1 for e in ev_all if e.right_censored)
    assert 0 < n_cens < len(ev_all), "expected both censored and uncensored events, got %d/%d" % (
        n_cens, len(ev_all))


# ---------------------------------------------------------------- state alphabet
def test_state_filter_returns_only_the_declared_alphabet(ev_alphabet):
    assert ev_alphabet
    assert {e.state_n for e in ev_alphabet} <= DECLARED_ALPHABET


def test_the_state_filter_is_load_bearing(ev_all, ev_alphabet):
    """Non-vacuity: the raw dataset genuinely contains states OUTSIDE {1..8}.

    Without this the alphabet assertion above could pass on a dataset that never had anything to
    filter, which would make it a vacuous success.
    """
    raw_states = {e.state_n for e in ev_all}
    assert raw_states - DECLARED_ALPHABET, "no out-of-alphabet states present; filter untested"
    assert len(ev_alphabet) < len(ev_all)


# ---------------------------------------------------------------- partition integrity
def test_partition_vocabulary_is_exactly_train_or_holdout(ev_all):
    assert {e.partition for e in ev_all} == {"train", "holdout"}


def test_partition_agrees_with_independently_recomputed_sha256_mod5(ev_all):
    for e in ev_all:
        expected = "holdout" if independent_sha256_mod5(e.motor_id) == 0 else "train"
        assert e.partition == expected, (
            "split mismatch for %s (motor %s): field=%s recomputed=%s"
            % (e.event_id, e.motor_id, e.partition, expected))
        assert e.is_holdout == (expected == "holdout")


def test_partition_filter_is_honoured(ev_all):
    train = events.load_events(mode=events.DURATION_ONLY, partition="train")
    hold = events.load_events(mode=events.DURATION_ONLY, partition="holdout")
    assert all(e.partition == "train" for e in train)
    assert all(e.partition == "holdout" for e in hold)
    assert len(train) + len(hold) == len(ev_all)


def test_motor_counts_match_the_frozen_split(ev_all):
    """80 training motors / 19 holdout motors is the frozen B3 split; drift here invalidates
    every motor-equal score computed against B3."""
    train_motors = {e.motor_id for e in ev_all if e.partition == "train"}
    hold_motors = {e.motor_id for e in ev_all if e.partition == "holdout"}
    assert not (train_motors & hold_motors), "a motor may not straddle the split"
    coh = _bridge.frozen_cohort()
    # Motor counts on the ELIGIBLE cohort (uncensored, states 1..8) are the frozen 80/19.
    assert len(coh.train_motors) == 80
    assert len(coh.holdout_motors) == 19


def test_split_by_motor_groups_by_the_experimental_unit(ev_all):
    grouped = events.split_by_motor(ev_all)
    assert sum(len(v) for v in grouped.values()) == len(ev_all)
    assert len(grouped) == len({e.motor_id for e in ev_all})
    for mid, evs in grouped.items():
        assert all(e.motor_id == mid for e in evs)
