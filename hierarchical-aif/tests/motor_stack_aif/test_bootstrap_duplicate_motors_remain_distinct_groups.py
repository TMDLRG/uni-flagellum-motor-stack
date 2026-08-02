"""D1 reproducer — a motor drawn K times must become K groups, not one K-fold group.

This is the mechanism test. Its sibling counts groups; this one proves the duplicated motor's
events are NOT concatenated into a single group whose likelihood becomes L_m^K.

NOTE ON CONSTRUCTION: `b3.Cohort` halts with BLOCKED-SCALE-UNDEFINED if any holdout state lacks
a training scale, so a draw list must cover all eligible states. Tests therefore duplicate motors
ON TOP OF a state-covering base sample rather than drawing a handful of motors in isolation.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, bootstrap  # noqa: E402


@pytest.fixture(scope="module")
def coh():
    return _bridge.frozen_cohort()


@pytest.fixture(scope="module")
def base_plus_dup(coh):
    """All 80 motors (guarantees state coverage) plus 2 extra draws of one motor."""
    dup = coh.train_motors[0]
    return dup, list(coh.train_motors) + [dup, dup]


def test_duplicated_motor_yields_k_separate_groups(coh, base_plus_dup):
    dup, sampled = base_plus_dup
    coh_b = bootstrap.build_bootstrap_cohort(coh, sampled, name="dup")

    assert len(coh_b.train_by_motor) == len(sampled) == 82, (
        "82 draws must give 82 exchangeable groups, got %d" % len(coh_b.train_by_motor)
    )
    origin = coh_b.bootstrap_group_origin
    dup_groups = [i for i, o in enumerate(origin) if o.endswith(dup)]
    assert len(dup_groups) == 3, "motor drawn 3x must appear as 3 groups, got %d" % len(dup_groups)

    sizes = {len(coh_b.train_by_motor[i]) for i in dup_groups}
    assert len(sizes) == 1, "the 3 copies must be identical in size, got %r" % sizes


def test_duplicated_motor_is_not_concatenated_into_one_group(coh, base_plus_dup):
    """The defective path folds the duplicates into one group. The corrected path must not."""
    dup, sampled = base_plus_dup

    legacy = bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE(coh, sampled, name="l")
    corrected = bootstrap.build_bootstrap_cohort(coh, sampled, name="c")

    # legacy groups by motorId -> 80 distinct ids for 82 draws
    assert len(legacy.train_by_motor) == 80, "D1: legacy collapses 82 draws to 80 groups"
    assert len(corrected.train_by_motor) == 82

    n_single = len([e for e in coh.train if e["motorId"] == dup
                    and (not e["rightCensored"]) and e["stateN"] in coh.states])
    legacy_sizes = sorted((len(g) for g in legacy.train_by_motor), reverse=True)
    assert 3 * n_single in legacy_sizes, (
        "D1: the duplicated motor should appear as one 3x-sized group of %d events; sizes=%r"
        % (3 * n_single, legacy_sizes[:5])
    )


def test_group_origin_metadata_is_preserved(coh, base_plus_dup):
    dup, sampled = base_plus_dup
    coh_b = bootstrap.build_bootstrap_cohort(coh, sampled, name="dup")
    origin = getattr(coh_b, "bootstrap_group_origin", None)
    assert origin is not None, "corrected bootstrap must expose bootstrap_group_origin"
    assert len(origin) == len(sampled)
    assert len(set(origin)) == len(origin), "every draw must have a distinct group id"
    assert all(o.startswith("draw_") for o in origin)


def test_m4_pooled_path_is_unchanged_by_the_fix(coh):
    """C10/M4 uses flat train_y. The fix must not perturb it at all."""
    rng = np.random.default_rng(20260717)
    sampled = bootstrap.draw_motors(coh.train_motors, rng)

    legacy = bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE(coh, sampled, name="l")
    corrected = bootstrap.build_bootstrap_cohort(coh, sampled, name="c")

    assert legacy.train_y.shape == corrected.train_y.shape
    assert np.allclose(np.sort(legacy.train_y), np.sort(corrected.train_y)), (
        "the pooled i.i.d. sample must be identical; only the GROUPING changes"
    )


def test_total_event_mass_is_conserved_by_the_fix(coh):
    """Regrouping must not add or drop events."""
    rng = np.random.default_rng(20260717)
    sampled = bootstrap.draw_motors(coh.train_motors, rng)
    legacy = bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE(coh, sampled, name="l")
    corrected = bootstrap.build_bootstrap_cohort(coh, sampled, name="c")

    n_legacy = sum(len(g) for g in legacy.train_by_motor)
    n_corrected = sum(len(g) for g in corrected.train_by_motor)
    assert n_legacy == n_corrected, (
        "grouped event mass must be conserved: legacy=%d corrected=%d" % (n_legacy, n_corrected)
    )
