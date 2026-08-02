"""Held-out scoring — motor-equal, on the frozen split.

Rules enforced here:
  - the experimental unit is the MOTOR; motor-equal aggregation weights each motor equally
  - the frozen sha256_mod5(motorId) split is reused, never recomputed differently
  - bootstrap resamples MOTORS, never events (pseudoreplication guard)
  - CI-bound verdicts only; a point estimate is never a verdict
  - duration-only: this module never touches mark fields (D5 firewall)
"""
from __future__ import annotations

import numpy as np

from . import hierarchy, status


def _require_aligned(per_event_nlpd, motor_ids, where: str) -> None:
    """F17: score and motor-id arrays of different length RAISE BEFORE ANY AGGREGATE.

    `zip` stopping at the shorter argument is the most expensive convenience in numerical Python.
    A score array and a motor-id array that disagree produce a MEAN OVER A SILENTLY SHORTENED
    PAIRING: every event past the truncation point is dropped, the number that comes out is
    well-formed, and nothing anywhere says so. The unit here is the MOTOR, so dropping events
    silently reweights the motors that survive.

    Both lengths are named, because a caller who cannot see which side is short cannot fix it.
    """
    n, m = len(per_event_nlpd), len(motor_ids)
    if n != m:
        raise ValueError(
            "%s: %d scores and %d motor ids. These must align one-to-one; zipping them would "
            "silently drop %d and return a mean over the remainder (F17)." % (where, n, m, abs(n - m)))


def motor_equal_nlpd(per_event_nlpd, motor_ids) -> float:
    """Mean over motors of the per-motor mean. Each motor contributes equally."""
    _require_aligned(per_event_nlpd, motor_ids, "motor_equal_nlpd")
    per_event_nlpd = np.asarray(per_event_nlpd, dtype=np.float64)
    by: dict = {}
    for v, m in zip(per_event_nlpd, motor_ids):
        by.setdefault(m, []).append(v)
    per_motor = np.array([np.mean(v) for _, v in sorted(by.items())], dtype=np.float64)
    return float(np.mean(per_motor))


def per_motor_means(per_event_nlpd, motor_ids):
    _require_aligned(per_event_nlpd, motor_ids, "per_motor_means")
    per_event_nlpd = np.asarray(per_event_nlpd, dtype=np.float64)
    by: dict = {}
    for v, m in zip(per_event_nlpd, motor_ids):
        by.setdefault(m, []).append(v)
    keys = sorted(by)
    return keys, np.array([np.mean(by[k]) for k in keys], dtype=np.float64)


def motor_cluster_bootstrap(per_motor_a, per_motor_b, n_rep=2000, seed=20260717):
    """Paired motor-cluster bootstrap of the contrast (b - a).

    Resamples MOTORS with replacement. Single-construction RNG, strict prefix - the pattern the
    frozen C04 cell uses correctly and the pattern D1's C11 cell got wrong.
    """
    a = np.asarray(per_motor_a, dtype=np.float64)
    b = np.asarray(per_motor_b, dtype=np.float64)
    if a.shape != b.shape:
        raise ValueError("paired arrays must have equal length: %r vs %r" % (a.shape, b.shape))
    n = len(a)
    rng = np.random.default_rng(seed)                    # constructed ONCE
    idx = rng.integers(0, n, size=(n_rep, n))            # motors, not events
    diffs = (b[idx] - a[idx]).mean(axis=1)
    return diffs


def contrast_with_ci(per_motor_ref, per_motor_challenger, n_rep=2000, seed=20260717,
                     alpha=0.05):
    """Percentile CI of (ref - challenger). Positive interval above 0 => challenger better."""
    d = motor_cluster_bootstrap(per_motor_challenger, per_motor_ref, n_rep=n_rep, seed=seed)
    lo = float(np.percentile(d, 100 * alpha / 2))
    hi = float(np.percentile(d, 100 * (1 - alpha / 2)))
    point = float(np.mean(np.asarray(per_motor_ref) - np.asarray(per_motor_challenger)))
    return {
        "pointEstimate": point,
        "interval": [lo, hi],
        "width": hi - lo,
        "intervalType": "percentile",
        "nRep": n_rep,
        "seed": seed,
        "resamplingUnit": "MOTOR",
        "verdict": status.verdict_from_ci(lo, hi, threshold=0.0),
        "note": ("Width reported here is the PERCENTILE width and is labelled as such - see D7, "
                 "where the frozen artifact's `width` field silently reported the companion "
                 "interval while verdicts used BCa."),
    }


def score_motor_stack(fit_params, by_motor_holdout):
    """Held-out per-motor mean NLPD under the fitted hierarchical model.

    Uses the per-motor marginal (latent integrated), which is the honest predictive quantity for a
    motor not seen in training.
    """
    mu, tau = fit_params["mu"], fit_params["tau"]
    nodes = hierarchy.gauss_hermite()
    out = []
    for y, c in by_motor_holdout:
        ll = hierarchy.motor_log_marginal(y, c, mu, tau, nodes=nodes)
        out.append(-ll / len(y))       # mean NLPD per event within this motor
    return np.array(out, dtype=np.float64)
