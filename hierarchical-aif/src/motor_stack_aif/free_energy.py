"""F_motor — the observational variational free energy.

    F_motor = E_q[ ln q(Theta, eta, z) - ln p(o, z, eta, Theta) ]
            = KL[ q || prior ] - E_q[ ln p(o | latents) ]
            = complexity - accuracy

WHAT THIS IS: the ANALYST's objective for fitting a hierarchical model to recorded dwell times.
WHAT THIS IS NOT: a claim that the motor performs inference. The B3 result's own `notEstablished`
explicitly disclaims that reading, and computing F here does not license it. See
`docs/MOTOR-STACK-AIF-SCOPE-RULING.md`.

There is deliberately NO expected-free-energy function in this module. G requires policies over
actions; this dataset has none. G-side is DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER, and the
absence of the function is the fence.
"""
from __future__ import annotations

import numpy as np


def gaussian_kl(mu_q, sd_q, mu_p, sd_p):
    """KL[ N(mu_q, sd_q^2) || N(mu_p, sd_p^2) ], elementwise, in nats."""
    mu_q = np.asarray(mu_q, dtype=np.float64)
    sd_q = np.asarray(sd_q, dtype=np.float64)
    mu_p = np.asarray(mu_p, dtype=np.float64)
    sd_p = np.asarray(sd_p, dtype=np.float64)
    if np.any(sd_q <= 0) or np.any(sd_p <= 0):
        raise ValueError("standard deviations must be positive")
    return (np.log(sd_p / sd_q)
            + (sd_q ** 2 + (mu_q - mu_p) ** 2) / (2.0 * sd_p ** 2)
            - 0.5)


def free_energy(complexity: float, accuracy: float) -> float:
    """F = complexity - accuracy. Both in nats.

    complexity = KL[q(latents) || p(latents)]
    accuracy   = E_q[ log p(observations | latents) ]
    """
    c = float(complexity)
    a = float(accuracy)
    if not np.isfinite(c) or not np.isfinite(a):
        raise ValueError("F requires finite complexity and accuracy; got %r, %r" % (c, a))
    return c - a


def decompose(complexity: float, accuracy: float) -> dict:
    """Return F with its two named terms kept separate and units declared."""
    return {
        "complexity_nats": float(complexity),
        "accuracy_nats": float(accuracy),
        "free_energy_nats": free_energy(complexity, accuracy),
        "identity": "F = complexity - accuracy",
        "note": ("F is the analyst's fitting objective over recorded observations. It is NOT a "
                 "claim that the motor performs inference."),
    }


def surprise_from_exact_posterior(log_evidence: float) -> float:
    """When q IS the exact posterior, F reduces to surprise = -log p(o).

    Recorded because the shipped runtime computes exactly this and labels it F, with a KL term
    that is identically zero by construction. That is a valid readout, but it is NOT evidence
    that any objective was minimised.
    """
    return -float(log_evidence)
