"""Fit the constrained F-side motor-stack model.

Two free parameters only: (mu, tau) of the population prior over log-shape. Per-motor latents are
integrated by Gauss-Hermite quadrature, never estimated freely, so the parameter count does not
grow with motor count.

Deterministic: Nelder-Mead from a fixed simplex, no RNG anywhere in the fit path.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import optimize

from . import hierarchy
from . import hazard_survival as hs

# tau is bounded away from 0 because tau -> 0 collapses the hierarchy to a single shared shape
# (i.e. M1), which is a DIFFERENT model. The boundary is reported, never silently crossed.
TAU_MIN = 1e-4
TAU_MAX = 5.0
MU_MIN, MU_MAX = -5.0, 5.0


def _objective(theta, by_motor):
    mu, log_tau = float(theta[0]), float(theta[1])
    tau = math.exp(log_tau)
    if not (MU_MIN <= mu <= MU_MAX) or not (TAU_MIN <= tau <= TAU_MAX):
        return 1e12
    try:
        return -hierarchy.population_log_likelihood(by_motor, mu, tau)
    except (hs.NonFiniteLogDensity, ValueError, FloatingPointError, OverflowError):
        # OverflowError: defence in depth. hierarchy now guards the representable-k domain at the
        # quadrature node, but an infeasible region must never escape the objective as a crash.
        return 1e12


def fit_motor_stack(by_motor, x0=(0.0, math.log(0.3))) -> dict:
    """Fit (mu, tau). `by_motor` is a list of (y_array, censored_array), one per training motor."""
    res = optimize.minimize(
        _objective, np.asarray(x0, dtype=np.float64), args=(by_motor,),
        method="Nelder-Mead",
        options={"xatol": 1e-8, "fatol": 1e-8, "maxiter": 4000, "maxfev": 4000},
    )
    mu = float(res.x[0])
    tau = math.exp(float(res.x[1]))
    at_boundary = (tau <= TAU_MIN * 1.01) or (tau >= TAU_MAX * 0.99)
    return {
        "mu": mu,
        "tau": tau,
        "k_population_median": math.exp(mu),
        "trainNLL": float(res.fun),
        "converged": bool(res.success),
        "nit": int(res.nit),
        "nfev": int(res.nfev),
        "tauAtBoundary": at_boundary,
        "tauBounds": [TAU_MIN, TAU_MAX],
        "nFreeParams": 2,
        "note": ("Per-motor latents integrated by 33-node Gauss-Hermite quadrature, NOT estimated. "
                 "Parameter count is independent of motor count."),
    }
