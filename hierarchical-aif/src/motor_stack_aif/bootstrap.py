"""Motor-cluster bootstrap cohort construction.

SCIENTIFIC INTENT (frozen B4 protocol, C10/C11): a *motor-cluster* bootstrap. Motors are the
experimental unit. Resample motors with replacement; if motor m is drawn K times it must
contribute K INDEPENDENT EXCHANGEABLE GROUPS, because the bootstrap approximates the sampling
distribution over motors.

D1_C11_CLUSTER_COLLAPSE
-----------------------
The committed B4 runner concatenates the sampled motors' events into a flat list and rebuilds
`b3.Cohort`, which groups training events into `train_by_motor` keyed by `motorId`. A motor drawn
K times therefore collapses into ONE group holding K copies of its events instead of K separate
groups. Measured at seed_base=20260717, b=0: 80 motors drawn -> 46 groups (42.5% cluster loss);
largest group inflates 70 -> 153 events. A K-fold group contributes L_m^K to the grouped
likelihood, over-sharpening that motor's latent.

Scope of the defect:
  - M7 (`m7_train_nll` iterates `train_by_motor`)  -> AFFECTED   (C11 U4)
  - M4 (`_fit_m4_reduced` uses flat `coh.train_y`) -> UNAFFECTED (C10): duplicates enter
    correctly for a pooled i.i.d. likelihood, so C10's bootstrap is valid as written.

WHY THE FIX IS SURGICAL
-----------------------
`b3.Cohort.__init__` derives train/holdout membership from `sha256_mod5(motorId)` and HALTS on
any mismatch with the event's `partition` field. Renaming `motorId` to a synthetic draw id would
therefore re-derive the split from the synthetic name and scatter bootstrap training draws into
the holdout set - leakage strictly worse than the defect being fixed. So the corrected builder:

  1. builds the cohort exactly as the legacy path does (preserving the frozen split, the
     bootstrap-resampled per-state scales, and the normalized `_y`), then
  2. rebuilds ONLY `train_by_motor` so that each DRAW is its own exchangeable group.

`train_y` (flat, pooled) is deliberately left untouched, so M4/C10 behaviour is bit-identical to
the legacy path. This is an implementation fix to match the frozen protocol's intended
cluster-bootstrap semantics. It changes no frozen threshold, criterion, seed, or N.
"""
from __future__ import annotations

import numpy as np

from . import _bridge


def draw_motors(train_motors, rng):
    """Draw len(train_motors) motors with replacement. Single-construction RNG in, list out."""
    n = len(train_motors)
    idx = rng.integers(0, n, size=n)
    return [train_motors[i] for i in idx]


def _assemble(coh, sampled, name, states):
    """Shared assembly: exactly the committed runner's event construction."""
    b3 = _bridge.b3()
    train_events = []
    for m in sampled:
        train_events.extend([dict(e) for e in coh.train if e["motorId"] == m])
    holdout_events = [dict(e) for e in coh.holdout]
    merged = train_events + holdout_events
    for e in merged:
        e["partition"] = "holdout" if b3.sha256_mod5(e["motorId"]) == 0 else "train"
    return b3.Cohort(name, tuple(states), merged)


def build_bootstrap_cohort_LEGACY_DEFECTIVE(coh, sampled, name="boot",
                                            states=tuple(range(1, 9))):
    """Verbatim semantics of the committed B4 runner. Retained for old-vs-new comparison.

    DO NOT USE FOR NEW EVIDENCE - collapses duplicate motor draws by motorId (D1).
    """
    return _assemble(coh, sampled, name, states)


def build_bootstrap_cohort(coh, sampled, name="boot", states=tuple(range(1, 9))):
    """Corrected motor-cluster bootstrap.

    Identical to the legacy path except that `train_by_motor` carries one group PER DRAW, so a
    motor drawn K times yields K exchangeable groups. `original_motor_id` per group is exposed
    on the returned cohort as `bootstrap_group_origin` for provenance.
    """
    coh_b = _assemble(coh, sampled, name, states)

    # Rebuild the grouped view: one group per DRAW, in draw order (deterministic).
    # Normalize with the bootstrap cohort's own per-state scales, exactly as Cohort did.
    groups = []
    origin = []
    for draw_idx, m in enumerate(sampled):
        ys = [e["durationS"] / coh_b.scale_N[e["stateN"]]
              for e in coh.train
              if e["motorId"] == m and (not e["rightCensored"]) and e["stateN"] in states]
        groups.append(np.array(ys, dtype=np.float64))
        origin.append("draw_%03d_%s" % (draw_idx, m))

    coh_b.train_by_motor = groups
    coh_b.bootstrap_group_origin = origin
    coh_b.bootstrap_n_draws = len(sampled)
    return coh_b
