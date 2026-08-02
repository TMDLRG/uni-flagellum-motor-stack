"""The censoring contract, checked against an INDEPENDENT closed form.

    uncensored : log p(o) = log h(y) + log S(y)
    censored   : log p(o) = log S(y)

so that, holding y fixed,

    log p(uncensored) - log p(censored) == log h(y)     EXACTLY.

Coverage note (audit): ``test_fside_motor_stack.py`` already asserts the two branches, but it does
so by comparing ``log_event_density`` against ``hs.weibull_log_hazard`` + ``hs.weibull_log_survival``
— i.e. against the same module's own components. That is a composition check, not an oracle. This
file supplies the missing oracle: hazard and survival are recomputed from ``scipy.stats``
(``weibull_min`` / ``expon``), which shares no code with ``hazard_survival.py``.

FROZEN-COHORT NOTE: the frozen B3 cohort EXCLUDES right-censored events
(``Cohort`` eligibility is ``(not rightCensored) and stateN in states``). Everything asserted here
is therefore a property of the LIKELIHOOD MACHINERY, not a property of the frozen cohort, and it
does not change any published B3 number.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import hazard_survival as hs  # noqa: E402

# Tolerances. `TOL` is an absolute tolerance in nats on quantities of order 1-10.
# 1e-12 is ~1e4 x machine epsilon, which is the realistic accumulation of a handful of
# transcendental evaluations (gammaln, log, pow) in double precision. It is NOT tuned: the
# observed residuals are at the 1e-15 level (see the assertion messages on failure).
TOL = 1e-12

SHAPES = [0.6, 1.0, 1.7]
YS = np.array([0.05, 0.3, 1.0, 2.5, 7.0])


def _independent_weibull(y, k):
    """Mean-one Weibull hazard/survival from scipy.stats — no shared code with the module."""
    lam = 1.0 / math.exp(math.lgamma(1.0 + 1.0 / k))
    d = stats.weibull_min(c=k, scale=lam)
    log_s = d.logsf(y)
    log_f = d.logpdf(y)
    return log_f - log_s, log_s          # log h = log f - log S


# ---------------------------------------------------------------- the difference identity
@pytest.mark.parametrize("k", SHAPES)
def test_uncensored_minus_censored_equals_log_hazard(k):
    """THE property: the censoring flag is worth exactly log h(y), no more and no less."""
    unc = hs.log_event_density(YS, np.zeros(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    cen = hs.log_event_density(YS, np.ones(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    log_h_indep, _ = _independent_weibull(YS, k)
    resid = np.abs((unc - cen) - log_h_indep)
    assert np.max(resid) < TOL, "max residual vs scipy log-hazard = %r" % float(np.max(resid))


@pytest.mark.parametrize("k", SHAPES)
def test_censored_contribution_is_the_independent_log_survival(k):
    cen = hs.log_event_density(YS, np.ones(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    _, log_s_indep = _independent_weibull(YS, k)
    assert np.max(np.abs(cen - log_s_indep)) < TOL


@pytest.mark.parametrize("k", SHAPES)
def test_uncensored_contribution_is_the_independent_log_density(k):
    unc = hs.log_event_density(YS, np.zeros(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    lam = 1.0 / math.exp(math.lgamma(1.0 + 1.0 / k))
    log_f = stats.weibull_min(c=k, scale=lam).logpdf(YS)
    assert np.max(np.abs(unc - log_f)) < TOL


def test_exponential_branch_against_scipy():
    unc = hs.log_event_density(YS, np.zeros(YS.shape, bool),
                               hs.exp_log_hazard, hs.exp_log_survival)
    cen = hs.log_event_density(YS, np.ones(YS.shape, bool),
                               hs.exp_log_hazard, hs.exp_log_survival)
    d = stats.expon()
    assert np.max(np.abs(unc - d.logpdf(YS))) < TOL
    assert np.max(np.abs(cen - d.logsf(YS))) < TOL
    # log h == 0 for the unit exponential, so the flag is worth exactly nothing here.
    assert np.max(np.abs(unc - cen)) < TOL


# ---------------------------------------------------------------- negative controls
@pytest.mark.parametrize("k", SHAPES)
def test_mislabelling_a_censored_event_changes_the_likelihood(k):
    """NEGATIVE CONTROL. If the branch were ignored (or its sign flipped) this would not move.

    We require a MATERIAL change, not merely a non-equality: log h(y) is bounded away from 0 for
    every y used here, so an implementation that dropped the hazard term must be caught.
    """
    unc = hs.log_event_density(YS, np.zeros(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    cen = hs.log_event_density(YS, np.ones(YS.shape, bool),
                               hs.weibull_log_hazard, hs.weibull_log_survival, k)
    if k == 1.0:
        pytest.skip("unit exponential has log h == 0 by construction; covered separately")
    assert np.min(np.abs(unc - cen)) > 1e-3


@pytest.mark.parametrize("k", SHAPES)
def test_a_single_mislabelled_event_moves_the_total_log_likelihood(k):
    """Motor-level consequence: one wrong censoring flag must not be absorbed silently."""
    c_true = np.array([False, True, False, True, False])
    c_wrong = c_true.copy()
    c_wrong[1] = False                      # censored event relabelled as an observed transition
    a = float(np.sum(hs.log_event_density(YS, c_true, hs.weibull_log_hazard,
                                          hs.weibull_log_survival, k)))
    b = float(np.sum(hs.log_event_density(YS, c_wrong, hs.weibull_log_hazard,
                                          hs.weibull_log_survival, k)))
    log_h_indep, _ = _independent_weibull(YS, k)
    assert abs((b - a) - log_h_indep[1]) < TOL


def test_censoring_mask_must_be_aligned_with_the_durations():
    """A shape mismatch is a HALT, not a broadcast. Broadcasting would silently mis-assign flags."""
    with pytest.raises(ValueError):
        hs.log_event_density(YS, np.array([True, False]),
                             hs.weibull_log_hazard, hs.weibull_log_survival, 0.7)


def test_all_censored_and_all_uncensored_paths_are_both_reachable():
    """Guards the `if np.any(~c)` short-circuit: an all-censored batch must still be finite."""
    all_c = hs.log_event_density(YS, np.ones(YS.shape, bool),
                                 hs.weibull_log_hazard, hs.weibull_log_survival, 0.6)
    all_u = hs.log_event_density(YS, np.zeros(YS.shape, bool),
                                 hs.weibull_log_hazard, hs.weibull_log_survival, 0.6)
    assert np.all(np.isfinite(all_c)) and np.all(np.isfinite(all_u))
    assert not np.allclose(all_c, all_u)


def test_no_floor_is_applied_to_a_censored_batch():
    """NO_FLOOR policy: a non-finite contribution halts rather than being clipped."""
    with pytest.raises(hs.NonFiniteLogDensity):
        hs.log_event_density(np.array([0.0]), np.array([False]),
                             hs.weibull_log_hazard, hs.weibull_log_survival, 0.7)
