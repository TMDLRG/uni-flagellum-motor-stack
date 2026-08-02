"""Motor-equal aggregation and the pseudoreplication guard.

The experimental unit is the MOTOR. Two distinct errors are fenced here:

  AGGREGATION      — weighting by event count lets one heavily-sampled motor dominate the score.
                     Motor-equal must give each motor weight 1/n regardless of its event count.
  RESAMPLING       — bootstrapping EVENTS treats repeated dwells of one motor as independent
                     biological replicates. The resample index space must have cardinality n
                     (motors), not the event count.

Coverage note (audit): ``test_fside_motor_stack.py`` covers an 11-event / 2-motor motor-equal mean
and a degenerate paired-shift bootstrap. Neither compares motor-equal against event-pooled on an
extreme count imbalance, and neither demonstrates the resample index space. Both gaps are closed
here, with the event-level alternative constructed explicitly as the negative control.

B3 convention reminder: MOTOR_EQUAL is the PRIMARY aggregation; EVENT_POOLED exists only as a
continuity bridge. This file asserts they genuinely differ, so the choice between them is a real
scientific decision and not a formatting preference.

D5 declaration: no data is loaded here at all; these are properties of the estimator.
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import score  # noqa: E402


def _event_pooled(nlpd, motor_ids):
    """The continuity-bridge aggregation, written out independently of the module under test."""
    return float(np.mean(np.asarray(nlpd, dtype=np.float64)))


# ---------------------------------------------------------------- aggregation
def test_one_hundred_event_motor_does_not_dominate_a_two_event_motor():
    """The designed extreme case: motor A has 100 events scoring 1.0, motor B has 2 scoring 5.0."""
    nlpd = [1.0] * 100 + [5.0] * 2
    motors = ["A"] * 100 + ["B"] * 2

    motor_equal = score.motor_equal_nlpd(nlpd, motors)
    pooled = _event_pooled(nlpd, motors)

    assert motor_equal == pytest.approx(3.0)                      # (1.0 + 5.0) / 2
    assert pooled == pytest.approx((100 * 1.0 + 2 * 5.0) / 102)   # ~1.0784
    # PREDICTED DIRECTION: the well-sampled motor is the EASY one, so pooling flatters the model.
    assert motor_equal > pooled


def test_the_direction_flips_when_the_well_sampled_motor_is_the_hard_one():
    """Non-vacuity: the inequality above must track the data, not be a fixed artefact."""
    nlpd = [5.0] * 100 + [1.0] * 2
    motors = ["A"] * 100 + ["B"] * 2
    assert score.motor_equal_nlpd(nlpd, motors) == pytest.approx(3.0)
    assert score.motor_equal_nlpd(nlpd, motors) < _event_pooled(nlpd, motors)


def test_motor_equal_is_invariant_to_replicating_one_motors_events():
    """Duplicating a motor's events (more frames, same motor) must not change the score at all.
    This is the frame-counting error stated as an invariance."""
    base_nlpd = [1.0, 3.0, 2.0, 8.0]
    base_motors = ["A", "A", "B", "C"]
    before = score.motor_equal_nlpd(base_nlpd, base_motors)

    # motor A observed 10x longer: same per-event values, ten times as many of them
    dup_nlpd = [1.0, 3.0] * 10 + [2.0, 8.0]
    dup_motors = ["A", "A"] * 10 + ["B", "C"]
    after = score.motor_equal_nlpd(dup_nlpd, dup_motors)

    assert after == pytest.approx(before)
    assert _event_pooled(dup_nlpd, dup_motors) != pytest.approx(
        _event_pooled(base_nlpd, base_motors)), "event-pooled SHOULD move; that is the point"


def test_per_motor_means_returns_one_value_per_motor_in_sorted_order():
    nlpd = [1.0, 3.0, 10.0, 4.0, 6.0]
    motors = ["m2", "m2", "m1", "m3", "m3"]
    keys, means = score.per_motor_means(nlpd, motors)
    assert keys == ["m1", "m2", "m3"]
    assert list(means) == [10.0, 2.0, 5.0]
    assert len(means) == len(set(motors))


# ---------------------------------------------------------------- resampling unit
def test_bootstrap_index_space_has_cardinality_equal_to_the_motor_count():
    """PSEUDOREPLICATION GUARD.

    With n motors, every bootstrap replicate mean must lie in the finite lattice of means over
    multisets of size n drawn from the n per-motor values. Any event-level resampling would
    produce values outside that lattice.
    """
    # Values chosen so that no two distinct multisets share a mean (1, 10, 100 are linearly
    # independent over the small integers used here). With 1, 2, 4 the multisets {1,1,4} and
    # {2,2,2} collide at mean 2.0 and the lattice would have 9 members, not 10 - which would
    # weaken the cardinality claim without any bug being present.
    per_motor = np.array([1.0, 10.0, 100.0])
    n = len(per_motor)
    lattice = {round(float(np.mean(c)), 12)
               for c in itertools.product(per_motor, repeat=n)}
    assert len(lattice) == 10          # multisets of size 3 from 3 distinct values: C(5,3)

    reps = score.motor_cluster_bootstrap(np.zeros(n), per_motor, n_rep=4000, seed=7)
    observed = {round(float(v), 12) for v in reps}
    assert observed <= lattice, "values outside the motor lattice: %r" % (observed - lattice)
    assert observed == lattice, "with 4000 replicates every motor multiset should appear"


def test_an_event_level_bootstrap_would_produce_values_outside_the_motor_lattice():
    """NEGATIVE CONTROL. Motor A contributes two events, motor B one. Event-level resampling can
    reach means (2.0, 3.0) that motor-level resampling cannot. If the estimator ever produced
    those, it would be counting dwells as independent biological replicates."""
    events_vals = np.array([1.0, 1.0, 4.0])        # A, A, B
    per_motor = np.array([1.0, 4.0])               # motor means

    motor_lattice = {round(float(np.mean(c)), 12)
                     for c in itertools.product(per_motor, repeat=len(per_motor))}
    event_lattice = {round(float(np.mean(c)), 12)
                     for c in itertools.product(events_vals, repeat=len(events_vals))}
    assert event_lattice - motor_lattice, "the two designs must be distinguishable"

    reps = score.motor_cluster_bootstrap(np.zeros(2), per_motor, n_rep=2000, seed=11)
    observed = {round(float(v), 12) for v in reps}
    assert observed <= motor_lattice
    assert not (observed & (event_lattice - motor_lattice))


def test_bootstrap_is_paired_and_refuses_unequal_arrays():
    """Unpaired resampling would break the within-motor pairing that makes the contrast valid."""
    with pytest.raises(ValueError):
        score.motor_cluster_bootstrap(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))


def test_bootstrap_is_deterministic_for_a_fixed_seed():
    a = np.array([1.0, 2.0, 4.0, 8.0])
    b = a + np.array([0.1, -0.2, 0.3, 0.0])
    r1 = score.motor_cluster_bootstrap(a, b, n_rep=500, seed=42)
    r2 = score.motor_cluster_bootstrap(a, b, n_rep=500, seed=42)
    assert np.array_equal(r1, r2)
    r3 = score.motor_cluster_bootstrap(a, b, n_rep=500, seed=43)
    assert not np.array_equal(r1, r3)


def test_contrast_declares_the_motor_as_the_resampling_unit():
    a = np.array([3.0, 3.2, 2.9, 3.1, 3.3])
    out = score.contrast_with_ci(a, a + 0.05, n_rep=500)
    assert out["resamplingUnit"] == "MOTOR"
    assert out["intervalType"] == "percentile"
    assert "D7" in out["note"], "the width's interval family must stay labelled"


def test_score_motor_stack_returns_one_number_per_motor():
    """The held-out score is per MOTOR, so 19 holdout motors give 19 numbers - never 233 events."""
    from motor_stack_aif import fit
    rng = np.random.default_rng(3)
    by_motor = [(rng.gamma(2.0, 0.5, size=k), np.zeros(k, dtype=bool))
                for k in (3, 7, 2, 11)]
    params = {"mu": 0.0, "tau": 0.3}
    out = score.score_motor_stack(params, by_motor)
    assert out.shape == (4,)
    assert np.all(np.isfinite(out))
    assert fit.TAU_MIN < params["tau"] < fit.TAU_MAX
