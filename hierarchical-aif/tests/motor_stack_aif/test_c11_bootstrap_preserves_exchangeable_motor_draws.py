"""D1 reproducer — the C11 U4 bootstrap must preserve the number of exchangeable draws.

RED BEFORE FIX: the legacy path collapses 80 draws to ~46 groups.
GREEN AFTER FIX: the corrected path yields exactly 80 groups.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, bootstrap  # noqa: E402

SEED_BASE = 20260717  # the seed declared in the frozen B4 protocol for C11


@pytest.fixture(scope="module")
def coh():
    return _bridge.frozen_cohort()


def test_frozen_cohort_has_80_training_motors(coh):
    assert len(coh.train_motors) == 80
    assert len(coh.train_by_motor) == 80, "unresampled cohort must group 1:1 by motor"


def test_corrected_bootstrap_preserves_draw_count(coh):
    """If 80 motors are drawn with replacement, 80 exchangeable groups must survive."""
    rng = np.random.default_rng(SEED_BASE)
    sampled = bootstrap.draw_motors(coh.train_motors, rng)
    assert len(sampled) == 80

    coh_b = bootstrap.build_bootstrap_cohort(coh, sampled, name="C11_b0")

    assert len(coh_b.train_by_motor) == 80, (
        "corrected cluster bootstrap must yield one exchangeable group per DRAW; "
        "got %d groups for 80 draws" % len(coh_b.train_by_motor)
    )


def test_legacy_bootstrap_demonstrates_the_defect(coh):
    """Pin the defective behaviour so the correction is auditable, not just asserted."""
    rng = np.random.default_rng(SEED_BASE)
    sampled = bootstrap.draw_motors(coh.train_motors, rng)
    legacy = bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE(coh, sampled, name="legacy_b0")

    n_distinct = len(set(sampled))
    assert len(legacy.train_by_motor) == n_distinct, (
        "legacy groups collapse to the DISTINCT motor count - this is D1"
    )
    assert len(legacy.train_by_motor) < 80, "D1: cluster count is silently reduced"


def test_corrected_bootstrap_group_count_is_stable_across_replicates(coh):
    """Every replicate must expose the full draw count, not a random subset."""
    for b in range(5):
        rng = np.random.default_rng(SEED_BASE + b)
        sampled = bootstrap.draw_motors(coh.train_motors, rng)
        coh_b = bootstrap.build_bootstrap_cohort(coh, sampled, name="C11_b%d" % b)
        assert len(coh_b.train_by_motor) == 80, (
            "replicate %d yielded %d groups, expected 80" % (b, len(coh_b.train_by_motor))
        )
