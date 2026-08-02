"""The baselines must stay ADVERSARIES, not straw men.

The retained adverse finding of this programme is that M2_LOGNORMAL — a two-parameter-free,
one-parameter-fitted shape with no mechanism in it at all — out-predicts the two-timescale
mixture M3 on held-out data. A test suite that let the baselines quietly degrade would launder
that finding away without anyone editing a single result file.

What is asserted:

  MEAN-ONE      every baseline is mean-one on y = duration / scale_N, checked against a scipy
                closed-form moment (independent implementation, no shared code).
  LOG-DENSITY   each ``LOGPDF`` entry matches the corresponding ``scipy.stats`` log-pdf.
  REAL FIT      each fitter attains a finite, non-degenerate train NLL on the REAL frozen training
                cohort, with the parameter strictly interior to its search bounds.
  REDERIVATION  each refitted train NLL reproduces the FROZEN B3 artifact value. This is the
                independent-oracle requirement: a different optimiser, in a different module,
                landing on the same number.
  ADVERSARIAL   M2 genuinely beats M3 on the frozen held-out score, in BOTH aggregations, and the
                adverse-retention record is still present in the artifact.

UNITS: the frozen ``NLPD_motor_equal`` numbers quoted here are on the SECONDS scale (they carry
the ``+log(scale_N)`` Jacobian). Only frozen-vs-frozen comparisons are made with them, so the
constant cancels; no F-side normalised-``y`` score is compared against them anywhere in this file.

D5 declaration: duration channel only.
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

from motor_stack_aif import _bridge, baselines  # noqa: E402

COHORT = "derived_eligible_1_to_8"

# Tolerances.
#   NLL_REL 1e-10 — the two implementations use different optimisers; the frozen and refitted
#                   train NLLs agree to ~1e-15 relative in practice, so 1e-10 is loose enough to
#                   survive a libm difference and tight enough that a real model change fails.
#   PAR_REL 1e-6  — the NLL surface is flat near the optimum, so the ARGMIN is the less precisely
#                   determined quantity. Observed worst disagreement is 4.6e-8 relative (M5).
#   MOMENT  1e-12 — closed-form scipy moments; no quadrature involved.
NLL_REL = 1e-10
PAR_REL = 1e-6
MOMENT_TOL = 1e-12


@pytest.fixture(scope="module")
def train_y():
    coh = _bridge.frozen_cohort()
    y = np.asarray(coh.train_y, dtype=np.float64)
    assert len(y) == 793, "frozen training event count changed: %d" % len(y)
    return y


@pytest.fixture(scope="module")
def frozen():
    return _bridge.b3_result()["cohorts"][COHORT]


@pytest.fixture(scope="module")
def fits(train_y):
    return {name: fn(train_y) for name, fn in baselines.FITTERS.items()}


def _scipy_dist(name, params):
    """Independent construction of the same mean-one law from scipy.stats."""
    if name == "M0_EXPONENTIAL":
        return stats.expon(scale=1.0)
    if name == "M1_WEIBULL":
        k = params["k"]
        return stats.weibull_min(c=k, scale=1.0 / math.exp(math.lgamma(1.0 + 1.0 / k)))
    if name == "M2_LOGNORMAL":
        s = params["sigma"]
        return stats.lognorm(s=s, scale=math.exp(-0.5 * s * s))
    if name == "M5_GAMMA":
        a = params["shape"]
        return stats.gamma(a=a, scale=1.0 / a)
    raise AssertionError("no independent construction declared for %r" % name)


# ---------------------------------------------------------------- the roster itself
def test_every_baseline_is_declared_adversarial():
    assert baselines.IS_ADVERSARIAL == set(baselines.LOGPDF)
    assert set(baselines.FITTERS) == set(baselines.LOGPDF)
    assert len(baselines.IS_ADVERSARIAL) >= 4


def test_no_UNI_candidate_hides_inside_the_adversary_roster():
    """M3/M4/M7 are the mechanistic candidates. If one appeared here it would be scored as its own
    adversary — a circular oracle."""
    for name in baselines.LOGPDF:
        assert not name.startswith(("M3", "M4", "M6", "M7", "M8"))
        assert "UNI" not in name


# ---------------------------------------------------------------- mean-one on y
@pytest.mark.parametrize("name", sorted(baselines.LOGPDF))
def test_baseline_is_mean_one_on_the_normalised_scale(name, fits):
    d = _scipy_dist(name, fits[name]["params"])
    assert abs(d.mean() - 1.0) < MOMENT_TOL, "%s mean = %r" % (name, d.mean())


@pytest.mark.parametrize("name", sorted(baselines.LOGPDF))
def test_baseline_logpdf_matches_an_independent_scipy_implementation(name, fits):
    y = np.array([0.05, 0.3, 1.0, 2.5, 7.0])
    got = baselines.LOGPDF[name](y, fits[name]["params"])
    ref = _scipy_dist(name, fits[name]["params"]).logpdf(y)
    err = float(np.max(np.abs(got - ref)))
    assert err < 1e-12, "%s max |logpdf - scipy| = %r" % (name, err)


def test_the_mean_one_check_would_catch_a_mis_scaled_baseline():
    """NON-VACUITY. A gamma with rate 1 instead of rate=shape is not mean-one."""
    a = 0.51
    assert abs(stats.gamma(a=a, scale=1.0).mean() - 1.0) > 0.1


# ---------------------------------------------------------------- real fits, not straw men
@pytest.mark.parametrize("name", sorted(baselines.FITTERS))
def test_baseline_attains_a_finite_non_degenerate_train_nll(name, fits, train_y):
    r = fits[name]
    assert math.isfinite(r["trainNLL"])
    assert 0.0 < r["trainNLL"] < 10.0 * len(train_y), r
    # a real fit must beat the fixed-parameter null it generalises, or it is not fitting anything
    if name != "M0_EXPONENTIAL":
        assert r["trainNLL"] < fits["M0_EXPONENTIAL"]["trainNLL"], (
            "%s does not improve on the parameter-free exponential" % name)


@pytest.mark.parametrize("name,key,lo,hi", [
    ("M1_WEIBULL", "k", 0.05, 5.0),
    ("M2_LOGNORMAL", "sigma", 0.05, 5.0),
    ("M5_GAMMA", "shape", 0.05, 20.0),
])
def test_fitted_parameter_is_strictly_interior_to_its_search_bounds(name, key, lo, hi, fits):
    """A parameter pinned to a bound is a degenerate fit — the model was never given a chance."""
    v = fits[name]["params"][key]
    assert lo * 1.01 < v < hi * 0.99, "%s %s=%r sits on a bound" % (name, key, v)


# ---------------------------------------------------------------- independent rederivation
@pytest.mark.parametrize("name", sorted(baselines.FITTERS))
def test_refit_reproduces_the_frozen_b3_train_nll(name, fits, frozen):
    ref = float(frozen["fitted"][name]["trainNLL"])
    got = float(fits[name]["trainNLL"])
    assert got == pytest.approx(ref, rel=NLL_REL), "%s frozen=%r refit=%r" % (name, ref, got)


@pytest.mark.parametrize("name,key", [
    ("M1_WEIBULL", "k"), ("M2_LOGNORMAL", "sigma"), ("M5_GAMMA", "shape"),
])
def test_refit_reproduces_the_frozen_b3_parameter(name, key, fits, frozen):
    ref = float(frozen["fitted"][name]["params"][0])
    got = float(fits[name]["params"][key])
    assert got == pytest.approx(ref, rel=PAR_REL), "%s frozen=%r refit=%r" % (name, ref, got)


# ---------------------------------------------------------------- the adverse finding survives
def test_M2_lognormal_beats_M3_on_the_frozen_holdout_in_both_aggregations(frozen):
    """THE RETAINED ADVERSE RESULT. Lower NLPD is better. Both numbers are on the seconds scale
    and come from the same frozen artifact, so the Jacobian constant cancels."""
    m2 = frozen["scores"]["M2_LOGNORMAL"]["NLPD_motor_equal"]
    m3 = frozen["scores"]["M3_TWO_TIMESCALE"]["NLPD_motor_equal"]
    assert m2["eventPooled"] < m3["eventPooled"], (m2, m3)
    assert m2["motorEqual"] < m3["motorEqual"], (m2, m3)


def test_M2_also_beats_M3_on_training_fit(fits, frozen):
    """Rederived locally: the adversary is not merely lucky on the holdout."""
    assert fits["M2_LOGNORMAL"]["trainNLL"] < float(
        frozen["fitted"]["M3_TWO_TIMESCALE"]["trainNLL"])


def test_the_adverse_retention_record_is_still_present_in_the_frozen_artifact():
    """Deleting this record would be the cleanest possible way to launder the adverse result."""
    rec = _bridge.b3_result()["adverseLognormalRetention"][COHORT]
    assert rec["lognormalMinusMixtureLogDensity"] > 0.0
    assert rec["m2EventPooledNLPD"] < rec["m3EventPooledNLPD"]
    assert "retained" in rec["note"]


def test_M2_is_never_promoted_out_of_the_adversary_set():
    """Predictive superiority is not mechanism. M2 stays an adversary by construction."""
    assert "M2_LOGNORMAL" in baselines.IS_ADVERSARIAL
    assert baselines.MEAN_ONE.startswith("mean-one on y")
