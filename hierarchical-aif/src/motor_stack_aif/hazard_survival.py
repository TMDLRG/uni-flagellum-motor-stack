"""Lmotor-1 hazard / survival.

The censoring contract, which the B3 competition does NOT implement (it excludes censored events
by a frozen rule) but which lib/source-first-passage.js does:

    uncensored : log p(o) = log h(t) + log S(t)
    censored   : log p(o) = log S(t)

NO FLOOR. A non-finite log density is a HALT, matching the frozen runner's declared policy. A
floor would silently convert an impossible event into a merely-unlikely one and inflate every
score that follows.

Distributions are parameterised in MEAN-ONE form on the normalised scale y = duration / scale_N,
matching the B3 convention so scores are comparable.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import special


class NonFiniteLogDensity(FloatingPointError):
    """Raised instead of flooring. Mirrors the frozen runner's no-floor HALT policy."""


def _check(arr, what: str):
    a = np.asarray(arr, dtype=np.float64)
    if not np.all(np.isfinite(a)):
        bad = int(np.sum(~np.isfinite(a)))
        raise NonFiniteLogDensity(
            "%s produced %d non-finite value(s); no floor is applied by policy" % (what, bad))
    return a


# ---------------------------------------------------------------- exponential (mean-one)
def exp_log_hazard(y):
    y = np.asarray(y, dtype=np.float64)
    return _check(np.zeros_like(y), "exp_log_hazard")   # h = 1 => log h = 0


def exp_log_survival(y):
    y = np.asarray(y, dtype=np.float64)
    return _check(-y, "exp_log_survival")


# ---------------------------------------------------------------- Weibull (mean-one, shape k)
def _weibull_scale(k: float) -> float:
    """lambda such that E[Y] = 1 for shape k."""
    return 1.0 / math.exp(special.gammaln(1.0 + 1.0 / k))


def weibull_log_hazard(y, k: float):
    y = np.asarray(y, dtype=np.float64)
    lam = _weibull_scale(k)
    with np.errstate(divide="ignore"):
        out = math.log(k) - k * math.log(lam) + (k - 1.0) * np.log(y)
    return _check(out, "weibull_log_hazard")


def weibull_log_survival(y, k: float):
    y = np.asarray(y, dtype=np.float64)
    lam = _weibull_scale(k)
    return _check(-np.power(y / lam, k), "weibull_log_survival")


# ---------------------------------------------------------------- generic assembly
def log_event_density(y, right_censored, log_hazard_fn, log_survival_fn, *args, **kw):
    """Assemble the censored/uncensored likelihood.

        uncensored : log h(t) + log S(t)
        censored   : log S(t)
    """
    y = np.asarray(y, dtype=np.float64)
    c = np.asarray(right_censored, dtype=bool)
    if y.shape != c.shape:
        raise ValueError("y and right_censored must have the same shape: %r vs %r"
                         % (y.shape, c.shape))
    ls = log_survival_fn(y, *args, **kw)
    out = np.array(ls, dtype=np.float64, copy=True)
    if np.any(~c):
        lh = log_hazard_fn(y, *args, **kw)
        out[~c] = lh[~c] + ls[~c]
    return _check(out, "log_event_density")


def survival_integrates_to_one(log_hazard_fn, log_survival_fn, *args,
                               upper=60.0, n=400001, **kw) -> float:
    """Numerically integrate the implied density f(y) = h(y)S(y) over [0, upper].

    Uses a log-spaced grid: a uniform grid mis-integrates the y^(k-1) singularity for k < 1, which
    is exactly the fragility recorded against the frozen M7 mean-one check. Returns the integral,
    which should approach 1.
    """
    y = np.logspace(-12, math.log10(upper), n)
    lh = log_hazard_fn(y, *args, **kw)
    ls = log_survival_fn(y, *args, **kw)
    f = np.exp(lh + ls)
    return float(np.trapezoid(f, y)) if hasattr(np, "trapezoid") else float(np.trapz(f, y))
