"""Lmotor-5..Lmotor-2 — the constrained hierarchy actually built.

DELIBERATELY MINIMAL. The identifiability analysis says the full stack (population prior +
per-motor latents + per-event hidden kinetic state + policies) is not identifiable at 793 training
events / 80 training motors / 19 holdout motors, against a corrected resolution floor of ~0.042
nats. So this module implements only the layers the data can constrain:

    Lmotor-5  population prior over log-shape : (mu, tau)          2 params
    Lmotor-4  per-motor latent log-shape      : eta_m ~ N(mu, tau) integrated out, NOT free
    Lmotor-3  occupancy state N_i             : per-state mean normalisation (frozen scale_N)
    Lmotor-2  kinetic mode                    : NOT INSTANTIATED - no identifiable capacity
    Lmotor-1  hazard/survival                 : mean-one Weibull with motor-specific shape

Total free parameters: 2. Per-motor latents are integrated by quadrature, not estimated, so the
parameter count does not grow with the number of motors. That is the whole point of the
constraint: a model with 80 free per-motor shapes would fit 80 numbers to a median of 7 events
each and could not be scored honestly.

Adding Lmotor-2 policies would add unidentifiable capacity, not testability. That decision is
recorded here rather than left implicit.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import special

from . import hazard_survival as hs

# Gauss-Hermite nodes for integrating the per-motor latent. 33 nodes is ample for a smooth
# 1-D Gaussian integral and keeps the fit deterministic (no sampling).
_GH_NODES = 33

# Smallest shape whose MEAN-ONE scale is representable in IEEE double.
#   lambda(k) = 1 / exp(lgamma(1 + 1/k))  and math.exp overflows above ~709.78.
#   lgamma(171) = 706.573 (finite), lgamma(172) = 711.715 (overflow), so 1 + 1/k <= 171,
#   i.e. k >= 1/170. DERIVED from the overflow bound, not tuned to a result.
# The previous guard (1e-6) was three orders of magnitude too permissive: the Nelder-Mead fit
# walked a quadrature node into k ~ 1e-6 and raised OverflowError out of the objective instead of
# marking the node infeasible. A node outside the representable domain contributes zero mass to
# the latent integral, which is what -inf encodes here. NO FLOOR is applied to finite densities.
K_MIN_REPRESENTABLE = 1.0 / 170.0
K_MAX_REPRESENTABLE = 1e6


def gauss_hermite(n: int = _GH_NODES):
    x, w = np.polynomial.hermite_e.hermegauss(n)
    return x, w / np.sum(w)


def motor_log_marginal(y_motor, censored_motor, mu: float, tau: float, nodes=None) -> float:
    """log p(events of one motor | mu, tau), integrating the per-motor latent eta_m.

        eta_m ~ N(mu, tau^2)        (log shape)
        k_m   = exp(eta_m)
        events ~ mean-one Weibull(k_m), with censoring handled by hazard/survival

    The motor is the exchangeable unit: its events share eta_m and are integrated jointly.
    """
    if tau <= 0:
        raise ValueError("tau must be positive")
    x, w = nodes if nodes is not None else gauss_hermite()
    y = np.asarray(y_motor, dtype=np.float64)
    c = np.asarray(censored_motor, dtype=bool)

    logliks = np.empty(len(x), dtype=np.float64)
    for i, xi in enumerate(x):
        k = math.exp(mu + tau * xi)
        if not (K_MIN_REPRESENTABLE <= k <= K_MAX_REPRESENTABLE):
            logliks[i] = -np.inf
            continue
        try:
            ll = hs.log_event_density(y, c, hs.weibull_log_hazard, hs.weibull_log_survival, k)
            logliks[i] = float(np.sum(ll))
        except (hs.NonFiniteLogDensity, OverflowError):
            logliks[i] = -np.inf
    return float(special.logsumexp(logliks, b=w))


def population_log_likelihood(by_motor, mu: float, tau: float) -> float:
    """Sum of per-motor log marginals. Motors are independent given (mu, tau)."""
    nodes = gauss_hermite()
    total = 0.0
    for y, c in by_motor:
        total += motor_log_marginal(y, c, mu, tau, nodes=nodes)
    if not math.isfinite(total):
        raise hs.NonFiniteLogDensity("population log-likelihood is non-finite; no floor applied")
    return total


def posterior_motor_shape(y_motor, censored_motor, mu: float, tau: float):
    """Posterior mean/sd of eta_m for one motor - the Lmotor-4 belief q(eta_m).

    This is the per-motor POSTERIOR the frozen M7 never forms (M7 reports point estimates only).
    """
    x, w = gauss_hermite()
    y = np.asarray(y_motor, dtype=np.float64)
    c = np.asarray(censored_motor, dtype=bool)
    logliks = np.empty(len(x), dtype=np.float64)
    for i, xi in enumerate(x):
        k = math.exp(mu + tau * xi)
        if not (K_MIN_REPRESENTABLE <= k <= K_MAX_REPRESENTABLE):
            logliks[i] = -np.inf
            continue
        try:
            logliks[i] = float(np.sum(
                hs.log_event_density(y, c, hs.weibull_log_hazard, hs.weibull_log_survival, k)))
        except (hs.NonFiniteLogDensity, OverflowError):
            logliks[i] = -np.inf
    logw = logliks + np.log(w)
    logw -= special.logsumexp(logw)
    post = np.exp(logw)
    eta = mu + tau * x
    mean = float(np.sum(post * eta))
    var = float(np.sum(post * (eta - mean) ** 2))
    return {"eta_mean": mean, "eta_sd": math.sqrt(max(var, 0.0)),
            "k_mean_exp": math.exp(mean)}
