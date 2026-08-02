"""F_motor is an OBSERVATIONAL variational free energy / negative log marginal likelihood.

What this file pins down:

  1. ``population_log_likelihood`` is the SUM of per-motor log marginals — motors are the
     exchangeable unit and are NOT pooled into one long event vector (pooling is the
     pseudoreplication error, and it gives a numerically different answer).
  2. ``motor_log_marginal`` is a PROPER MARGINAL: the per-motor latent is integrated out. Checked
     against an independent ``scipy.integrate.quad`` over eta that shares no quadrature code with
     ``hierarchy.gauss_hermite``, and by node-count convergence on the real training cohort.
  3. F is an objective over OBSERVATIONS with a complexity term, not an expected free energy over
     policies. G has no function here; see ``test_no_G_biological_claim_in_passive_data.py``.
  4. UNITS: variational free energy is in NATS. The thermodynamic work ``tau * delta_theta`` is a
     different quantity in different units and does not live in this namespace. Note that
     ``hierarchy``/``fit`` use the symbol ``tau`` for the population SD of the log-shape — a
     DIMENSIONLESS quantity, not a torque. That collision is asserted to be documented.

Coverage note (audit): ``test_fside_motor_stack.py`` covers ``F = complexity - accuracy``, that F
responds to the accuracy term, the Gaussian KL zero case, and that a per-motor posterior has
non-zero spread. The additivity, proper-marginal, quadrature-convergence and unit-separation
properties above were not covered.

D5 declaration: duration channel only. No mark field is touched.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import integrate

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import (  # noqa: E402
    _bridge, free_energy, hazard_survival as hs, hierarchy,
)

MU, TAU = 0.0, 0.3


@pytest.fixture(scope="module")
def by_motor():
    """Real frozen training cohort, grouped by MOTOR. The cohort excludes censored events, so the
    censoring mask is all-False by construction (not an assumption: see B3 `Cohort` eligibility)."""
    coh = _bridge.frozen_cohort()
    assert len(coh.train_by_motor) == 80
    return [(np.asarray(v, dtype=np.float64), np.zeros(len(v), dtype=bool))
            for v in coh.train_by_motor]


# ---------------------------------------------------------------- 1. additivity over motors
def test_population_log_likelihood_is_the_sum_over_motors(by_motor):
    nodes = hierarchy.gauss_hermite()
    parts = [hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=nodes) for y, c in by_motor]
    total = hierarchy.population_log_likelihood(by_motor, MU, TAU)
    # Tolerance: pure floating-point summation order over 80 terms of magnitude ~8 nats.
    assert total == pytest.approx(float(np.sum(parts)), abs=1e-9)


def test_motors_are_not_pooled_into_one_exchangeable_group(by_motor):
    """NEGATIVE CONTROL against pseudoreplication.

    Concatenating two motors' events into a single motor asserts they share one latent eta. That
    is a DIFFERENT (and wrong) model, and it must give a different number. If these agreed, the
    per-motor latent would be doing nothing and the hierarchy would be decorative.
    """
    a, b = by_motor[0], by_motor[1]
    separate = (hierarchy.motor_log_marginal(a[0], a[1], MU, TAU)
                + hierarchy.motor_log_marginal(b[0], b[1], MU, TAU))
    pooled = hierarchy.motor_log_marginal(np.concatenate([a[0], b[0]]),
                                          np.concatenate([a[1], b[1]]), MU, TAU)
    assert not math.isclose(separate, pooled, rel_tol=1e-6, abs_tol=1e-6), (
        "separate=%r pooled=%r" % (separate, pooled))


def test_tau_zero_is_refused_rather_than_silently_collapsing_the_hierarchy():
    """tau -> 0 IS a different model (a single shared shape, i.e. M1). It must not be reachable
    by accident inside the marginal."""
    with pytest.raises(ValueError):
        hierarchy.motor_log_marginal(np.array([1.0]), np.array([False]), MU, 0.0)


# ---------------------------------------------------------------- 2. it is a proper marginal
def test_motor_log_marginal_matches_an_independent_quadrature_over_the_latent(by_motor):
    """INDEPENDENT ORACLE. Integrates p(events | eta) N(eta; mu, tau) over eta with adaptive
    quadrature. Shares no code with the Gauss-Hermite path except the likelihood itself.

    TOLERANCE, DERIVED FROM MEASUREMENT (not tuned until it passed):

    An earlier version of this test gated on ``err < 1e-9 * val`` using ``quad``'s DEFAULT
    accuracy request. That precondition is unsatisfiable by construction: ``quad``'s default
    ``epsrel`` is 1.49e-8 and its returned error estimate is deliberately conservative, so on
    this integrand it reports ~7.3e-11 absolute on a value of ~7.4e-4 — a reported RELATIVE
    error of ~1e-7, a hundred times looser than the precondition demanded. The check failed on
    its own guard and never reached the comparison it existed to make.

    The fix is to make the oracle WELL-CONDITIONED rather than to loosen the comparison, per the
    contract's standing lesson about fragile numerical checks. Asking ``quad`` for
    ``epsabs=0, epsrel=1e-12`` drops its reported relative error to ~1e-13 on the same integrand.

    Measured agreement at that setting, over the first 12 real training motors:
        worst |log(GH_33) - log(quad)| = 2.29e-8   (motor with n=2 events)
        typical                        ~ 1e-10, several motors exact to 1e-16
        worst quad reported rel error  = 9.9e-13
    The comparison tolerance below is 1e-6 nats absolute in log space: ~40x looser than the
    worst measured disagreement (so it is not knife-edge), and >4 orders of magnitude below the
    corrected 0.042-nat resolution floor (so anything it would let through is scientifically
    immaterial). It is still tight enough to catch a wrong prior, a missing Jacobian, a dropped
    weight normalisation, or an unintegrated latent — all of which move the answer by >1e-2.
    """
    y, c = by_motor[0]

    def integrand(eta):
        k = math.exp(eta)
        ll = float(np.sum(hs.log_event_density(y, c, hs.weibull_log_hazard,
                                               hs.weibull_log_survival, k)))
        prior = math.exp(-0.5 * ((eta - MU) / TAU) ** 2) / (TAU * math.sqrt(2.0 * math.pi))
        return math.exp(ll) * prior

    # +/- 10 tau covers the Gaussian prior to ~1e-22 of its mass.
    val, err = integrate.quad(integrand, MU - 10 * TAU, MU + 10 * TAU, limit=400,
                              epsabs=0.0, epsrel=1e-12)
    # Precondition: the ORACLE itself must be well-conditioned before it is allowed to judge.
    # 1e-9 relative is ~4 orders looser than the ~1e-13 measured, so this guards against a
    # genuinely misbehaving quadrature without being knife-edge.
    assert val > 0.0, "oracle integral is non-positive: %r" % val
    assert err < 1e-9 * val, (
        "adaptive quadrature did not reach the requested accuracy (abs err %r on value %r, "
        "relative %r); the oracle is not well-conditioned enough to judge the GH path"
        % (err, val, err / val))

    gh = hierarchy.motor_log_marginal(y, c, MU, TAU)
    assert gh == pytest.approx(math.log(val), abs=1e-6), (
        "Gauss-Hermite marginal disagrees with the independent adaptive-quadrature oracle: "
        "GH=%r quad=%r diff=%r" % (gh, math.log(val), abs(gh - math.log(val))))


def test_the_quadrature_oracle_disagrees_when_the_latent_is_NOT_integrated(by_motor):
    """Negative control for the oracle above — without it, that test could pass vacuously.

    If the tolerance were so loose that any plausible number passed, the check would be
    worthless. Here the latent is NOT integrated (the shape is pinned at its prior mean), which
    is the single most likely implementation error the oracle exists to catch. The resulting
    disagreement must be orders of magnitude larger than the 1e-6 tolerance.
    """
    y, c = by_motor[0]
    not_integrated = float(np.sum(hs.log_event_density(
        y, c, hs.weibull_log_hazard, hs.weibull_log_survival, math.exp(MU))))
    integrated = hierarchy.motor_log_marginal(y, c, MU, TAU)
    gap = abs(integrated - not_integrated)
    assert gap > 1e-3, (
        "failing to integrate the latent moved the answer by only %r nats, so the 1e-6 oracle "
        "tolerance would not distinguish a proper marginal from a plug-in point estimate" % gap)


def test_gauss_hermite_node_count_has_converged_on_the_real_cohort(by_motor):
    """Quadrature convergence: the answer must not depend on the node count that was chosen.

    Tolerance 0.01 nats TOTAL over 80 motors (1.25e-4 nats/motor). Justification: the corrected
    B3 resolution floor is ~0.042 nats on a per-event motor-equal contrast, so a total-likelihood
    wobble of 0.01 nats is a quarter of the smallest difference the study can resolve at all.
    """
    tol = 0.01
    ref_nodes = hierarchy.gauss_hermite(65)
    ref = sum(hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=ref_nodes) for y, c in by_motor)
    for n in (25, 33, 49):
        nodes = hierarchy.gauss_hermite(n)
        tot = sum(hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=nodes) for y, c in by_motor)
        assert abs(tot - ref) < tol, "n=%d differs from n=65 by %r nats" % (n, abs(tot - ref))


def test_the_convergence_check_is_not_vacuous(by_motor):
    """NON-VACUITY. A deliberately coarse 9-node rule must be OUTSIDE the tolerance above,
    otherwise the convergence assertion would pass for any node count and prove nothing."""
    ref = sum(hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=hierarchy.gauss_hermite(65))
              for y, c in by_motor)
    coarse = sum(hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=hierarchy.gauss_hermite(9))
                 for y, c in by_motor)
    assert abs(coarse - ref) > 0.01, "9-node rule was already within tolerance: %r" % abs(
        coarse - ref)


def test_a_quadrature_node_outside_the_representable_shape_domain_is_infeasible_not_a_crash(
        by_motor):
    """REGRESSION. Found while calibrating the convergence tolerance in this batch.

    ``hermegauss(97)`` places nodes at |x| ~ 18.65, so ``mu + tau*x`` reaches ``k = exp(-5.6)``
    ~ 0.0037. The mean-one scale ``1/Gamma(1 + 1/k)`` overflows a double for ``k <~ 1/170``, and
    the earlier guard band ``1e-6 < k < 1e6`` admitted those nodes, so ``OverflowError`` escaped
    the objective instead of the node being marked infeasible.

    A node outside the representable domain carries zero mass in the latent integral, and ``-inf``
    is how that is encoded. This is a DOMAIN guard, not a floor: no finite log density is ever
    clipped, and the NO_FLOOR halt on non-finite densities is untouched.
    """
    y, c = by_motor[0]
    # errstate is scoped to the extreme-node probe only. At the very edge of the representable
    # domain numpy legitimately overflows inside the guarded branch; the guard converts that node
    # to -inf (zero mass). Silencing the WARNING does not silence the ERROR: the OverflowError
    # assertion below still has to fire.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        for n in (33, 65, 97, 129):
            v = hierarchy.motor_log_marginal(y, c, MU, TAU, nodes=hierarchy.gauss_hermite(n))
            assert math.isfinite(v), "n=%d gave %r" % (n, v)

    # NON-VACUITY: the extreme nodes really do leave the representable domain ...
    x, _w = hierarchy.gauss_hermite(97)
    k_extreme = math.exp(MU + TAU * float(np.min(x)))
    assert k_extreme < hierarchy.K_MIN_REPRESENTABLE, k_extreme
    # ... and the mean-one scale genuinely overflows there, so the guard is load-bearing.
    with pytest.raises(OverflowError):
        hs.weibull_log_survival(np.array([1.0]), hierarchy.K_MIN_REPRESENTABLE * 0.5)


def test_gauss_hermite_weights_are_normalised():
    """The weights must be a probability measure, else the 'marginal' is off by a constant."""
    for n in (9, 25, 33, 65):
        _x, w = hierarchy.gauss_hermite(n)
        assert float(np.sum(w)) == pytest.approx(1.0, abs=1e-15)


def test_the_model_has_two_free_parameters_regardless_of_motor_count(by_motor):
    """The identifiability constraint: latents are integrated, never estimated. If the parameter
    count grew with motors, held-out scoring would not be honest."""
    from motor_stack_aif import fit
    small = fit.fit_motor_stack(by_motor[:6])
    assert small["nFreeParams"] == 2
    assert small["tauBounds"] == [fit.TAU_MIN, fit.TAU_MAX]


# ---------------------------------------------------------------- 3. F, not G
def test_F_reduces_to_surprise_when_the_complexity_term_vanishes():
    """F = complexity - accuracy. With q equal to the exact posterior the KL term is zero and F
    IS the negative log evidence — i.e. an objective over OBSERVATIONS."""
    log_evidence = -617.04
    assert free_energy.free_energy(0.0, log_evidence) == pytest.approx(
        free_energy.surprise_from_exact_posterior(log_evidence))


def test_F_is_an_observational_objective_not_a_policy_objective():
    d = free_energy.decompose(2.0, -5.0)
    assert d["identity"] == "F = complexity - accuracy"
    assert "observations" in d["note"]
    assert "NOT a claim that the motor performs inference" in d["note"]
    for banned in ("expected_free_energy", "expected_free_energy_nats", "policy",
                   "epistemic_value", "pragmatic_value", "G"):
        assert banned not in d, "F's decomposition must contain no G-side term (%r)" % banned


def test_complexity_and_accuracy_are_independently_load_bearing():
    """A readout that ignored one of its two terms would still satisfy a single-argument check."""
    base = free_energy.free_energy(2.0, -5.0)
    assert free_energy.free_energy(3.0, -5.0) != base
    assert free_energy.free_energy(2.0, -4.0) != base


def test_non_finite_terms_halt_rather_than_being_absorbed():
    with pytest.raises(ValueError):
        free_energy.free_energy(float("inf"), -5.0)
    with pytest.raises(ValueError):
        free_energy.free_energy(2.0, float("nan"))


# ---------------------------------------------------------------- 4. units are kept separate
def test_free_energy_quantities_are_declared_in_nats():
    d = free_energy.decompose(2.0, -5.0)
    numeric_keys = [k for k, v in d.items() if isinstance(v, float)]
    assert numeric_keys, "expected numeric fields"
    for k in numeric_keys:
        assert k.endswith("_nats"), "%r carries no declared unit" % k


def test_no_thermodynamic_work_quantity_shares_the_free_energy_namespace():
    """The contract requires ``tau * delta_theta`` (work, joules) to stay separate from
    variational free energy (nats). The separation is enforced by absence: no work-like symbol
    exists in this module, so the two can never be added together by accident."""
    src = Path(free_energy.__file__).read_text(encoding="utf-8")
    for banned in ("delta_theta", "torque", "joule", "def work", "work_nats", "_work("):
        assert banned not in src, "%r must not appear in the variational-F module" % banned
    for banned in ("work", "torque_nm", "delta_theta"):
        assert not hasattr(free_energy, banned)


def test_the_symbol_tau_is_documented_as_a_dimensionless_log_shape_sd():
    """NAME-COLLISION GUARD. `tau` in the hierarchy is the population SD of log-shape, NOT the
    torque of `tau * delta_theta`. If the docstring stopped saying so, a reader could silently
    read a thermodynamic quantity into a dimensionless one."""
    doc = hierarchy.motor_log_marginal.__doc__ or ""
    assert "eta_m ~ N(mu, tau^2)" in doc
    assert "log shape" in doc
    assert "torque" not in hierarchy.__doc__.lower()
    assert "torque" not in (doc.lower())
