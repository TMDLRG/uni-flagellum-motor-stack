"""F-side motor-stack tests: censoring, normalisation, F/G separation, firewall, scoring unit."""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import (  # noqa: E402
    baselines, events, free_energy, hazard_survival as hs, hierarchy, score,
)


# ------------------------------------------------------------------ censoring likelihood
def test_censored_uses_survival_only_uncensored_uses_hazard_times_survival():
    y = np.array([0.5, 1.5, 2.0])
    cens = np.array([False, True, False])
    got = hs.log_event_density(y, cens, hs.exp_log_hazard, hs.exp_log_survival)
    assert got[1] == pytest.approx(hs.exp_log_survival(y)[1]), "censored must be S(t) only"
    for i in (0, 2):
        expect = hs.exp_log_hazard(y)[i] + hs.exp_log_survival(y)[i]
        assert got[i] == pytest.approx(expect), "uncensored must be h(t)*S(t)"


def test_censoring_is_load_bearing():
    """Treating a censored event as uncensored must change the answer."""
    y = np.array([3.0])
    as_cens = hs.log_event_density(y, np.array([True]), hs.weibull_log_hazard,
                                   hs.weibull_log_survival, 0.7)
    as_unc = hs.log_event_density(y, np.array([False]), hs.weibull_log_hazard,
                                  hs.weibull_log_survival, 0.7)
    assert not np.isclose(as_cens[0], as_unc[0])


def test_no_floor_halts_on_nonfinite():
    with pytest.raises(hs.NonFiniteLogDensity):
        hs.weibull_log_hazard(np.array([0.0]), 0.7)   # log(0) at shape<1 -> -inf, must HALT


# ------------------------------------------------------------------ normalisation
@pytest.mark.parametrize("k", [0.6, 1.0, 1.7])
def test_weibull_density_integrates_to_one(k):
    total = hs.survival_integrates_to_one(hs.weibull_log_hazard, hs.weibull_log_survival, k)
    assert total == pytest.approx(1.0, abs=2e-3), "implied density must normalise, got %r" % total


@pytest.mark.parametrize("k", [0.6, 1.0, 1.7])
def test_weibull_is_mean_one(k):
    """The B3 convention is mean-one on the normalised scale."""
    lam = hs._weibull_scale(k)
    mean = lam * math.exp(math.lgamma(1.0 + 1.0 / k))
    assert mean == pytest.approx(1.0, rel=1e-12)


def test_baselines_are_mean_one():
    y = np.logspace(-9, 2.2, 300001)
    for name, params in (("M2_LOGNORMAL", {"sigma": 0.9}), ("M5_GAMMA", {"shape": 1.4})):
        f = np.exp(baselines.LOGPDF[name](y, params))
        mass = np.trapezoid(f, y) if hasattr(np, "trapezoid") else np.trapz(f, y)
        mean = (np.trapezoid(y * f, y) if hasattr(np, "trapezoid") else np.trapz(y * f, y))
        assert mass == pytest.approx(1.0, abs=3e-3), "%s mass=%r" % (name, mass)
        assert mean == pytest.approx(1.0, abs=5e-3), "%s mean=%r" % (name, mean)


# ------------------------------------------------------------------ F / G separation
def test_free_energy_is_complexity_minus_accuracy():
    assert free_energy.free_energy(2.5, 1.5) == pytest.approx(1.0)
    d = free_energy.decompose(2.5, 1.5)
    assert d["identity"] == "F = complexity - accuracy"
    assert d["free_energy_nats"] == pytest.approx(1.0)


def test_F_changes_with_accuracy():
    """F must actually respond to the data term, not be a constant readout."""
    assert free_energy.free_energy(1.0, 2.0) != free_energy.free_energy(1.0, 3.0)


def test_no_expected_free_energy_function_exists():
    """G-side is DESIGN_ONLY_UNTIL_INTERVENTION. Its ABSENCE is the fence."""
    for banned in ("expected_free_energy", "policy_posterior", "G_motor", "select_policy"):
        assert not hasattr(free_energy, banned), (
            "%s must not exist: this dataset is passive, with no actions to define a policy over. "
            "Adding it would invite a biological policy-selection claim the data cannot test."
            % banned)


def test_gaussian_kl_is_zero_for_identical_distributions():
    assert free_energy.gaussian_kl(0.3, 1.2, 0.3, 1.2) == pytest.approx(0.0, abs=1e-15)


# ------------------------------------------------------------------ D5 firewall
def test_duration_only_mode_never_returns_marks():
    ev = events.load_events(mode=events.DURATION_ONLY, states=range(1, 9))
    assert ev, "expected events"
    assert all(e.next_state_n is None and e.jump is None and e.direction is None for e in ev)


def test_holdout_mark_access_is_refused_without_acknowledgement():
    with pytest.raises(events.HoldoutMarkAccessError):
        events.load_events(mode=events.MARK_RETROSPECTIVE, states=range(1, 9))


def test_train_only_mark_access_is_permitted():
    ev = events.load_events(mode=events.MARK_RETROSPECTIVE, states=range(1, 9),
                            partition="train")
    assert ev and all(e.partition == "train" for e in ev)


def test_acknowledged_holdout_mark_access_is_permitted_but_explicit():
    ev = events.load_events(mode=events.MARK_RETROSPECTIVE, states=range(1, 9),
                            acknowledge_retrospective_holdout_marks=True)
    assert any(e.is_holdout for e in ev)


# ------------------------------------------------------------------ scoring unit
def test_motor_equal_weights_motors_not_events():
    """A motor with many events must not dominate."""
    nlpd = [1.0] * 10 + [3.0]
    motors = ["A"] * 10 + ["B"]
    assert score.motor_equal_nlpd(nlpd, motors) == pytest.approx(2.0)   # not 1.18


def test_bootstrap_resamples_motors_not_events():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    d = score.motor_cluster_bootstrap(a, a + 0.5, n_rep=500, seed=1)
    assert len(d) == 500
    assert np.all(np.isclose(d, 0.5)), "paired identical shift must give a constant contrast"


def test_a_consistent_paired_shift_IS_resolvable():
    """A tiny but perfectly consistent per-motor difference is genuinely resolvable.

    'Small' is not the same as 'unresolvable'. In a PAIRED design a uniform offset has zero
    between-motor variance, so the interval is degenerate and correctly excludes zero. Recorded
    explicitly because conflating the two is how an underpowered study talks itself into
    'no difference'.
    """
    rng = np.random.default_rng(0)
    a = rng.normal(3.0, 0.5, 19)
    out = score.contrast_with_ci(a, a + 0.001, n_rep=500)
    assert out["verdict"] == "RESOLVED_BELOW"
    assert out["width"] == pytest.approx(0.0, abs=1e-12)


def test_a_small_effect_with_between_motor_noise_is_NOT_established():
    """The realistic case: a small mean effect swamped by between-motor variability."""
    rng = np.random.default_rng(0)
    a = rng.normal(3.0, 0.5, 19)
    challenger = a + rng.normal(0.001, 0.30, 19)      # tiny mean, large spread
    out = score.contrast_with_ci(a, challenger, n_rep=2000)
    assert out["verdict"] == "NOT_ESTABLISHED", out
    assert out["interval"][0] < 0 < out["interval"][1]
    assert out["resamplingUnit"] == "MOTOR"


def test_point_estimate_alone_cannot_produce_a_verdict():
    with pytest.raises(Exception):
        score.status.verdict_from_ci(None, None, threshold=0.0)


def test_hierarchy_integrates_latent_not_free_per_motor_params():
    y = np.array([0.5, 1.2, 2.0])
    c = np.array([False, False, True])
    ll = hierarchy.motor_log_marginal(y, c, mu=0.0, tau=0.3)
    assert math.isfinite(ll)
    post = hierarchy.posterior_motor_shape(y, c, mu=0.0, tau=0.3)
    assert set(post) == {"eta_mean", "eta_sd", "k_mean_exp"}
    assert post["eta_sd"] > 0, "a per-motor POSTERIOR must have non-zero spread"
