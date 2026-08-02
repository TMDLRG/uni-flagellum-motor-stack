"""Adversarial baselines — deliberately simple, deliberately kept alive.

These are ADVERSARIES, never the UNI model. M2_LOGNORMAL in particular currently out-predicts the
two-timescale mixture on held-out data; that adverse result is retained, and this module exists so
the motor-stack candidate must beat these on the SAME split under a CI-bound verdict, not merely
look sophisticated.

All are mean-one on the normalised scale y = duration / scale_N, matching the B3 convention.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import special, stats

from . import hazard_survival as hs

MEAN_ONE = "mean-one on y = duration / scale_N (B3 convention)"


def m0_exponential_logpdf(y, _params=None):
    y = np.asarray(y, dtype=np.float64)
    return -y  # rate 1


def m1_weibull_logpdf(y, k):
    y = np.asarray(y, dtype=np.float64)
    return hs.weibull_log_hazard(y, k) + hs.weibull_log_survival(y, k)


def m2_lognormal_logpdf(y, sigma):
    """Mean-one lognormal: mu = -sigma^2/2."""
    y = np.asarray(y, dtype=np.float64)
    mu = -0.5 * sigma * sigma
    return (-np.log(y) - math.log(sigma) - 0.5 * math.log(2 * math.pi)
            - (np.log(y) - mu) ** 2 / (2 * sigma * sigma))


def m5_gamma_logpdf(y, shape):
    """Mean-one gamma: rate = shape."""
    y = np.asarray(y, dtype=np.float64)
    return (shape * math.log(shape) - special.gammaln(shape)
            + (shape - 1.0) * np.log(y) - shape * y)


def fit_m1(y):
    y = np.asarray(y, dtype=np.float64)
    r = _scalar_fit(lambda k: -np.sum(m1_weibull_logpdf(y, k)), 0.05, 5.0)
    return {"model": "M1_WEIBULL", "params": {"k": r[0]}, "trainNLL": r[1]}


def fit_m2(y):
    y = np.asarray(y, dtype=np.float64)
    r = _scalar_fit(lambda s: -np.sum(m2_lognormal_logpdf(y, s)), 0.05, 5.0)
    return {"model": "M2_LOGNORMAL", "params": {"sigma": r[0]}, "trainNLL": r[1]}


def fit_m5(y):
    y = np.asarray(y, dtype=np.float64)
    r = _scalar_fit(lambda a: -np.sum(m5_gamma_logpdf(y, a)), 0.05, 20.0)
    return {"model": "M5_GAMMA", "params": {"shape": r[0]}, "trainNLL": r[1]}


def fit_m0(y):
    y = np.asarray(y, dtype=np.float64)
    return {"model": "M0_EXPONENTIAL", "params": {},
            "trainNLL": float(-np.sum(m0_exponential_logpdf(y)))}


def _scalar_fit(nll, lo, hi):
    from scipy import optimize
    r = optimize.minimize_scalar(nll, bounds=(lo, hi), method="bounded",
                                 options={"xatol": 1e-10})
    return float(r.x), float(r.fun)


LOGPDF = {
    "M0_EXPONENTIAL": lambda y, p: m0_exponential_logpdf(y),
    "M1_WEIBULL": lambda y, p: m1_weibull_logpdf(y, p["k"]),
    "M2_LOGNORMAL": lambda y, p: m2_lognormal_logpdf(y, p["sigma"]),
    "M5_GAMMA": lambda y, p: m5_gamma_logpdf(y, p["shape"]),
}

FITTERS = {"M0_EXPONENTIAL": fit_m0, "M1_WEIBULL": fit_m1,
           "M2_LOGNORMAL": fit_m2, "M5_GAMMA": fit_m5}

IS_ADVERSARIAL = set(LOGPDF)   # every model here is an adversary, never the UNI model
