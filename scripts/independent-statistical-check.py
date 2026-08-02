#!/usr/bin/env python3
"""Independent SciPy oracle for the JavaScript observed-experiment engine.

This implementation deliberately does not import or translate the production
analysis functions. It rebuilds the frozen likelihoods with NumPy/SciPy and
fails if the point estimates or fitted parameters disagree.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy import optimize, special


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "experiments" / "data" / "wadhwa-2022-events.json").read_text("utf-8"))
REPORT = json.loads((ROOT / "experiments" / "results" / "observed-experiment-report.json").read_text("utf-8"))
STATES = REPORT["cohort"]["eligibleStates"]


events = [
    event
    for event in DATA["events"]
    if not event["rightCensored"] and event["stateN"] in STATES
]
train = [event for event in events if event["partition"] == "train"]
holdout = [event for event in events if event["partition"] == "holdout"]
state_means = {
    state: float(np.mean([event["durationS"] for event in train if event["stateN"] == state]))
    for state in STATES
}
train_y = np.asarray([event["durationS"] / state_means[event["stateN"]] for event in train])
holdout_y = np.asarray([event["durationS"] / state_means[event["stateN"]] for event in holdout])
holdout_scale = np.asarray([state_means[event["stateN"]] for event in holdout])


def weibull_logpdf(y: np.ndarray, shape: float) -> np.ndarray:
    scale = math.exp(-special.gammaln(1 + 1 / shape))
    ratio = y / scale
    return math.log(shape) - math.log(scale) + (shape - 1) * np.log(ratio) - ratio**shape


def lognormal_logpdf(y: np.ndarray, sigma: float) -> np.ndarray:
    mu = -(sigma**2) / 2
    return -np.log(y * sigma * math.sqrt(2 * math.pi)) - 0.5 * ((np.log(y) - mu) / sigma) ** 2


weibull_shape = float(
    optimize.minimize_scalar(
        lambda shape: -float(np.mean(weibull_logpdf(train_y, shape))),
        bounds=(0.12, 5),
        method="bounded",
        options={"xatol": 1e-12},
    ).x
)
lognormal_sigma = float(
    optimize.minimize_scalar(
        lambda sigma: -float(np.mean(lognormal_logpdf(train_y, sigma))),
        bounds=(0.05, 5),
        method="bounded",
        options={"xatol": 1e-12},
    ).x
)


def decode_mixture(parameters: np.ndarray) -> tuple[float, float, float]:
    weight = 1 / (1 + math.exp(-float(parameters[0])))
    rate_fast = 1 + math.exp(float(parameters[1]))
    rate_slow = (1 - weight) / (1 - weight / rate_fast)
    return weight, rate_fast, rate_slow


def mixture_logpdf(y: np.ndarray, parameters: np.ndarray) -> np.ndarray:
    weight, rate_fast, rate_slow = decode_mixture(parameters)
    terms = np.vstack(
        [
            math.log(weight) + math.log(rate_fast) - rate_fast * y,
            math.log(1 - weight) + math.log(rate_slow) - rate_slow * y,
        ]
    )
    return special.logsumexp(terms, axis=0)


mixture_result = optimize.minimize(
    lambda parameters: -float(np.mean(mixture_logpdf(train_y, parameters))),
    x0=np.asarray([math.log(0.6 / 0.4), math.log(5 - 1)]),
    method="Nelder-Mead",
    options={"xatol": 1e-12, "fatol": 1e-12, "maxiter": 5000},
)
if not mixture_result.success:
    raise RuntimeError(f"Independent mixture optimization failed: {mixture_result.message}")
weight_fast, rate_fast, rate_slow = decode_mixture(mixture_result.x)


jacobian = -np.log(holdout_scale)
scores = {
    "exponential": float(np.mean(-holdout_y + jacobian)),
    "weibull": float(np.mean(weibull_logpdf(holdout_y, weibull_shape) + jacobian)),
    "lognormal": float(np.mean(lognormal_logpdf(holdout_y, lognormal_sigma) + jacobian)),
    "mixture": float(np.mean(mixture_logpdf(holdout_y, mixture_result.x) + jacobian)),
}
state_cv = []
for state in STATES:
    values = np.asarray([event["durationS"] for event in holdout if event["stateN"] == state])
    state_cv.append(float(np.var(values, ddof=1) / np.mean(values) ** 2))
mean_cv = float(np.mean(state_cv))


expected_models = REPORT["fittedOnTrainingOnly"]["normalizedDurationModels"]
expected_scores = REPORT["heldoutResults"]["meanLogScoreNatsPerEvent"]
checks = {
    "weibullShape": (weibull_shape, expected_models["weibull"]["shape"]),
    "lognormalSigma": (lognormal_sigma, expected_models["lognormal"]["sigma"]),
    "mixtureWeightFast": (weight_fast, expected_models["mixture"]["weightFast"]),
    "mixtureRateFast": (rate_fast, expected_models["mixture"]["rateFast"]),
    "mixtureRateSlow": (rate_slow, expected_models["mixture"]["rateSlow"]),
    "meanCvSquared": (mean_cv, REPORT["heldoutResults"]["meanCvSquaredAcrossStates"]),
    **{f"score.{name}": (value, expected_scores[name]) for name, value in scores.items()},
}

for name, (observed, expected) in checks.items():
    tolerance = 2e-5 if name.startswith("mixture") else 2e-7
    if not math.isclose(observed, expected, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"{name} mismatch: independent={observed}, production={expected}")

print(
    json.dumps(
        {
            "status": "PASS",
            "oracle": "Independent NumPy/SciPy likelihood and optimization implementation",
            "trainEvents": len(train),
            "holdoutEvents": len(holdout),
            "checks": {name: {"independent": values[0], "production": values[1]} for name, values in checks.items()},
        },
        indent=2,
    )
)
