"""Hazard / survival internal consistency, with the exact guarantee kept separate from the
numerical check.

Per the operating contract's execution-rigor lesson ("separate the exact guarantee from the
fragile numerical check"), this file is organised in two tiers:

  TIER 1 — EXACT.  ``S(0) = 1`` and ``exp(log S) == scipy.stats.weibull_min.sf`` hold to machine
           precision. These are the hard checks; they are never loosened.
  TIER 2 — INDEPENDENT NUMERICAL.  ``log S(y) = -integral_0^y h(u) du``, unit mass and unit mean,
           evaluated with ``scipy.integrate.quad`` (adaptive, handles the ``y^(k-1)`` endpoint
           singularity for k < 1). The frozen M7 mean-one check used a UNIFORM grid and was
           fragile for exactly that reason; ``hazard_survival.survival_integrates_to_one`` already
           works around it with a log-spaced grid. Nothing is loosened here — the measured
           residuals are reported in the assertion messages so a reviewer sees the real number.

Coverage note (audit): ``test_fside_motor_stack.py`` covers unit mass (via the module's own
log-spaced helper) and mean-one (via the analytic scale identity). The gaps closed here are the
integral identity ``log S = -∫h``, ``S(0)=1``, monotonicity, and an oracle for mass/mean that
shares no code with ``hazard_survival.py``.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import integrate, stats

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import hazard_survival as hs  # noqa: E402

SHAPES = [0.6, 1.0, 1.7]
YS = [0.05, 0.3, 1.0, 2.5, 7.0]

# Tolerance justification:
#   EXACT_TOL   1e-14 nats — a handful of double-precision transcendental calls; observed 2.2e-16.
#   QUAD_TOL    1e-12      — the measured residual of the -integral identity is <= 8.9e-15;
#                            1e-12 leaves two orders of headroom without hiding a real error.
#   MOMENT_TOL  1e-8       — set to `scipy.integrate.quad`'s OWN reported absolute error bound on
#                            the improper [0, inf) integrals (up to 1.4e-8 here), not to the
#                            residual. Tightening below the quadrature's declared accuracy would
#                            be testing the quadrature, not the model.
EXACT_TOL = 1e-14
QUAD_TOL = 1e-12
MOMENT_TOL = 1e-8


def _mean_one_scale(k):
    return 1.0 / math.exp(math.lgamma(1.0 + 1.0 / k))


def _h(u, k):
    return float(np.exp(hs.weibull_log_hazard(np.array([u], dtype=np.float64), k))[0])


def _f(u, k):
    a = np.array([u], dtype=np.float64)
    return float(np.exp(hs.weibull_log_hazard(a, k) + hs.weibull_log_survival(a, k))[0])


# ---------------------------------------------------------------- TIER 1: exact guarantees
@pytest.mark.parametrize("k", SHAPES)
def test_survival_at_zero_is_exactly_one(k):
    s0 = float(np.exp(hs.weibull_log_survival(np.array([0.0]), k))[0])
    assert s0 == 1.0, "S(0) must be exactly 1, got %r" % s0


def test_exponential_survival_at_zero_is_exactly_one():
    assert float(np.exp(hs.exp_log_survival(np.array([0.0])))[0]) == 1.0


@pytest.mark.parametrize("k", SHAPES)
def test_survival_matches_scipy_exactly(k):
    """EXACT. Independent implementation, no shared code."""
    y = np.array(YS)
    got = np.exp(hs.weibull_log_survival(y, k))
    ref = stats.weibull_min(c=k, scale=_mean_one_scale(k)).sf(y)
    d = float(np.max(np.abs(got - ref)))
    assert d < EXACT_TOL, "max |S - scipy.sf| = %r" % d


@pytest.mark.parametrize("k", SHAPES)
def test_survival_is_monotone_non_increasing(k):
    y = np.linspace(0.0, 30.0, 20001)
    log_s = hs.weibull_log_survival(y, k)
    d = np.diff(log_s)
    assert np.all(d <= 0.0), "log S increased at %d of %d steps" % (int(np.sum(d > 0)), len(d))
    assert log_s[-1] < log_s[0], "S must actually decay, not be constant"


@pytest.mark.parametrize("k", SHAPES)
def test_hazard_is_strictly_positive(k):
    y = np.linspace(1e-6, 30.0, 5001)
    assert np.all(np.exp(hs.weibull_log_hazard(y, k)) > 0.0)


# ---------------------------------------------------------------- TIER 2: independent numerics
@pytest.mark.parametrize("k", SHAPES)
def test_log_survival_equals_minus_integrated_hazard(k):
    """THE consistency condition: log S(y) = -integral_0^y h(u) du."""
    worst = 0.0
    for y in YS:
        integral, _err = integrate.quad(_h, 0.0, y, args=(k,), limit=400)
        got = float(hs.weibull_log_survival(np.array([y]), k)[0])
        worst = max(worst, abs(got - (-integral)))
    assert worst < QUAD_TOL, "max |log S + integral h| = %r (k=%r)" % (worst, k)


def test_exponential_log_survival_equals_minus_integrated_hazard():
    for y in YS:
        integral, _ = integrate.quad(lambda u: float(np.exp(hs.exp_log_hazard(np.array([u])))[0]),
                                     0.0, y, limit=200)
        assert abs(float(hs.exp_log_survival(np.array([y]))[0]) + integral) < QUAD_TOL


@pytest.mark.parametrize("k", SHAPES)
def test_implied_density_has_unit_mass_by_adaptive_quadrature(k):
    mass, err = integrate.quad(_f, 0.0, np.inf, args=(k,), limit=500)
    assert abs(mass - 1.0) < MOMENT_TOL, "mass=%r (quad err bound %r)" % (mass, err)


@pytest.mark.parametrize("k", SHAPES)
def test_implied_density_has_unit_mean_by_adaptive_quadrature(k):
    """MEAN-ONE is the B3 normalisation convention. If it broke, every score shifts."""
    mean, err = integrate.quad(lambda u, kk: u * _f(u, kk), 0.0, np.inf, args=(k,), limit=500)
    assert abs(mean - 1.0) < MOMENT_TOL, "mean=%r (quad err bound %r)" % (mean, err)


@pytest.mark.parametrize("k", SHAPES)
def test_mean_one_also_holds_against_scipys_closed_form_moment(k):
    """Independent closed form: a second witness that does not use quadrature at all."""
    m = stats.weibull_min(c=k, scale=_mean_one_scale(k)).mean()
    assert abs(m - 1.0) < 1e-12, "scipy closed-form mean = %r" % m


# ---------------------------------------------------------------- non-vacuity
def test_a_wrongly_scaled_weibull_would_fail_the_mean_one_check():
    """NEGATIVE CONTROL. If the mean-one scale were dropped (lambda = 1), the mean is
    Gamma(1 + 1/k) != 1 and the check above must be able to see it."""
    k = 0.6
    wrong_mean = stats.weibull_min(c=k, scale=1.0).mean()
    assert abs(wrong_mean - 1.0) > MOMENT_TOL
