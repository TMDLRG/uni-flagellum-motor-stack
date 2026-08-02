"""Tests for the F-side scoring harness `compare.py`.

The load-bearing test in this file is the MUTATION test on the independent-oracle consistency
check: a check that cannot fail is worthless, so the scale convention is deliberately broken and
the harness is asserted to HALT.

Everything here is TRAIN-ONLY or recomputes numbers the frozen B3 record already published. No
test computes the F-side HELD-OUT score - that is the prospective quantity and it belongs to the
protocol run, not to the test suite.
"""
import ast
import io
import json
import math
import sys
import tokenize
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import compare, hierarchy, score, status  # noqa: E402

COMPARE_SOURCE = (SRC / "motor_stack_aif" / "compare.py").read_text(encoding="utf-8")


def _executable_tokens(src: str) -> set:
    """NAME/OP tokens of `src` with comments and string literals removed.

    Prose may describe the D5 quarantine; executable code may not dereference it.
    """
    out = set()
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.STRING, tokenize.NL, tokenize.NEWLINE):
            continue
        if getattr(tokenize, "FSTRING_MIDDLE", None) is not None \
                and tok.type == tokenize.FSTRING_MIDDLE:
            continue
        if tok.type == tokenize.NAME:
            out.add(tok.string)
    return out


def _literal_keys(src: str) -> set:
    """Every string literal used as a subscript key or as the argument of a `.get(...)` call."""
    out = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and isinstance(node.slice.value, str):
            out.add(node.slice.value)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("get", "pop", "setdefault") and node.args \
                and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            out.add(node.args[0].value)
    return out


@pytest.fixture(scope="module")
def inp():
    return compare.Inputs()


@pytest.fixture(scope="module")
def pinned(inp):
    """M3 + M8 only: parameter-pinned, no optimisation, enough for the oracle check."""
    return compare.fit_pinned_only(inp)


# ===================================================================== the oracle, and its mutant
def test_oracle_reproduces_the_frozen_published_m3_motor_equal_exactly(inp, pinned):
    """The crux. B3 stores no per-motor arrays, so this recomputation is mandatory."""
    out = compare.oracle_consistency_check(inp, pinned)
    assert out["status"] == "PASS"
    m3 = [c for c in out["checks"] if c["model"] == compare.CONTROL_CURRENT][0]
    assert m3["publishedMotorEqual"] == 3.434333333075359
    assert m3["absResidual"] <= compare.ORACLE_TOL, m3
    # the declared expectation is EXACT agreement, not merely within tolerance
    assert m3["residual"] == 0.0, m3


def test_oracle_covers_a_parameter_free_and_a_flexible_model_too(inp, pinned):
    out = compare.oracle_consistency_check(inp, pinned)
    got = {c["model"]: c for c in out["checks"]}
    assert set(got) == {"M3_TWO_TIMESCALE", "M0_EXPONENTIAL", "M8_EMPIRICAL_KDE"}
    assert got["M0_EXPONENTIAL"]["publishedMotorEqual"] == 3.54798328106296
    assert got["M8_EMPIRICAL_KDE"]["publishedMotorEqual"] == 3.4225236184063643
    for c in got.values():
        assert c["pass"] and c["perEventMaxAbsDiffVsFrozenRunner"] == 0.0, c


def test_MUTANT_scale_convention_makes_the_oracle_check_FAIL_and_HALT(inp, pinned):
    """MUTATION TEST. Drop the +log(scale_N) Jacobian and the oracle must halt.

    This is the whole reason the check exists: the units error cancels in a contrast and does NOT
    cancel in an absolute score, so without this check the harness would produce right-looking
    contrasts on top of wrong-by-~2-nats absolute numbers.
    """
    with pytest.raises(compare.OracleConsistencyError) as exc:
        compare.oracle_consistency_check(inp, pinned, scale_mode=compare.SCALE_NORMALISED)
    assert "HALTS" in str(exc.value)


def test_MUTANT_wrong_pinned_parameters_make_the_oracle_check_FAIL(inp, pinned):
    """A second, independent mutation: perturb M3's frozen params in the LAST decimal place."""
    broken = {k: dict(v) for k, v in pinned.items()}
    broken["M8_EMPIRICAL_KDE"]["_kdeParams"] = pinned["M8_EMPIRICAL_KDE"]["_kdeParams"]
    p = list(pinned[compare.CONTROL_CURRENT]["paramsVector"])
    broken[compare.CONTROL_CURRENT]["paramsVector"] = [p[0] * (1 + 1e-9), p[1]]
    with pytest.raises(compare.OracleConsistencyError):
        compare.oracle_consistency_check(inp, broken)


def test_oracle_tolerance_is_not_silently_loose():
    """A tolerance wide enough to absorb a real convention error is not a check."""
    assert compare.ORACLE_TOL <= 1e-10, "oracle tolerance must stay tight; do not loosen it"


# ===================================================================== units
def test_seconds_scale_is_the_normalised_scale_plus_log_scale_N(inp):
    states = [1, 6, 8]
    base = np.array([0.0, 0.0, 0.0])
    sec = compare.to_seconds_scale(base, states, inp.scale_n)
    for got, s in zip(sec, states):
        assert got == pytest.approx(math.log(inp.scale_n[s]), rel=1e-15)
    norm = compare.to_seconds_scale(base, states, inp.scale_n,
                                    mode=compare.SCALE_NORMALISED)
    assert np.all(norm == base)
    assert not np.allclose(sec, norm), "the two scales must be distinguishable"


def test_the_scale_offset_cancels_in_a_contrast_but_not_in_an_absolute_score(inp):
    """The exact reason the oracle check is mandatory, asserted as a property."""
    states = [1, 2, 3, 4]
    a = np.array([1.0, 2.0, 1.5, 0.5])
    b = np.array([1.2, 1.9, 1.7, 0.4])
    a_s = compare.to_seconds_scale(a, states, inp.scale_n)
    b_s = compare.to_seconds_scale(b, states, inp.scale_n)
    assert np.allclose(a_s - b_s, a - b), "a common Jacobian must cancel in a contrast"
    assert not np.isclose(float(np.mean(a_s)), float(np.mean(a))), \
        "and must NOT cancel in an absolute score"


# ===================================================================== alignment
def test_per_motor_arrays_are_aligned_by_motor_id_across_models(inp, pinned):
    b3 = compare._bridge.b3()
    arrays = {}
    for mid, params in ((compare.CONTROL_CURRENT,
                         list(pinned[compare.CONTROL_CURRENT]["paramsVector"])),
                        ("M0_EXPONENTIAL", []),
                        ("M8_EMPIRICAL_KDE", pinned["M8_EMPIRICAL_KDE"]["_kdeParams"])):
        logn = np.asarray(b3.holdout_lognorm(mid, params, inp.cohort), dtype=np.float64)
        pe = compare.to_seconds_scale(-logn, inp.holdout_states, inp.scale_n)
        agg = compare.aggregate(pe, inp.holdout_motor_ids, inp.holdout_motors)
        arrays[mid] = agg["perMotor"]
        # the frozen runner's own aggregation, which is aligned to cohort.holdout_motors.
        # Tolerance is ULP-level and DECLARED: the frozen runner averages a motor's events in its
        # own within-motor sort order while per_motor_means uses frozen row order, so the sums
        # differ in the last few bits. Same multiset, different summation order.
        frozen = b3.aggregate_motor_equal(b3.nlpd_per_event(mid, params, inp.cohort), inp.cohort)
        diff = float(np.max(np.abs(agg["perMotor"] - np.array(frozen["perMotor"]))))
        assert diff <= compare.PER_MOTOR_ULP_TOL, (mid, diff)
        # and the aggregate the verdict depends on is EXACT
        assert agg["motorEqual"] == frozen["motorEqual"], mid
    assert all(len(v) == 19 for v in arrays.values())
    assert inp.holdout_motors == sorted(inp.holdout_motors)
    # different models must give different per-motor arrays, else alignment is vacuous
    assert not np.allclose(arrays["M0_EXPONENTIAL"], arrays["M8_EMPIRICAL_KDE"])


def test_aggregate_refuses_a_misaligned_motor_order(inp):
    pe = np.zeros(len(inp.holdout_motor_ids))
    scrambled = list(reversed(inp.holdout_motors))
    with pytest.raises(AssertionError):
        compare.aggregate(pe, inp.holdout_motor_ids, scrambled)


def test_motor_equal_is_not_event_pooled(inp, pinned):
    """If these coincided, the motor-equal aggregation would be doing nothing."""
    b3 = compare._bridge.b3()
    logn = np.asarray(b3.holdout_lognorm("M0_EXPONENTIAL", [], inp.cohort), dtype=np.float64)
    pe = compare.to_seconds_scale(-logn, inp.holdout_states, inp.scale_n)
    agg = compare.aggregate(pe, inp.holdout_motor_ids, inp.holdout_motors)
    assert agg["motorEqual"] != agg["eventPooled"]


# ===================================================================== contrast sign convention
def test_contrast_sign_matches_B3_challenger_better_means_interval_above_zero():
    """B3: contrast = S(reference) - S(challenger); above 0 => challenger wins.

    Construct a case where the challenger is KNOWN better (lower NLPD on every motor) and assert
    the interval sits entirely above 0.
    """
    rng = np.random.default_rng(7)
    ref = rng.normal(3.5, 0.4, 19)
    challenger = ref - 0.25                       # unambiguously better
    out = score.contrast_with_ci(ref, challenger, n_rep=500, seed=compare.BOOT_SEED)
    assert out["pointEstimate"] == pytest.approx(0.25)
    assert out["interval"][0] > 0.0
    assert out["verdict"] == status.RESOLVED_ABOVE


def test_contrast_sign_reference_better_means_interval_below_zero():
    rng = np.random.default_rng(7)
    ref = rng.normal(3.5, 0.4, 19)
    challenger = ref + 0.25                       # unambiguously worse
    out = score.contrast_with_ci(ref, challenger, n_rep=500, seed=compare.BOOT_SEED)
    assert out["interval"][1] < 0.0
    assert out["verdict"] == status.RESOLVED_BELOW


def test_harness_contrast_map_carries_the_convention_and_a_CI_bound_verdict():
    """Drive `contrasts()` with synthetic per-motor arrays: sign, verdict, and labelling."""
    n = 19
    per_model = {}
    base = np.linspace(3.30, 3.60, n)
    per_model[compare.FSIDE] = {"perMotor": base}
    for mid in (compare.CONTROL_CURRENT,) + compare.ADVERSARIES:
        per_model[mid] = {"perMotor": base + 0.30}       # every reference is worse
    cmap = compare.contrasts(per_model, n_rep=400)
    assert set(cmap) == set((compare.CONTROL_CURRENT,) + compare.ADVERSARIES)
    for mid, c in cmap.items():
        assert c["challenger"] == compare.FSIDE and c["reference"] == mid
        assert c["pointEstimate"] == pytest.approx(0.30)
        assert c["verdict"] == status.RESOLVED_ABOVE
        assert c["intervalType"] == "percentile"
        assert c["resamplingUnit"] == "MOTOR"
        assert "percentile" in c["halfWidthBelongsTo"].lower()
    assert cmap[compare.CONTROL_CURRENT]["role"] == "CONTROL_CURRENT"
    assert cmap["M2_LOGNORMAL"]["role"] == "ADVERSARY"


def test_zero_crossing_interval_is_reported_as_not_established_never_as_equivalence():
    rng = np.random.default_rng(3)
    n = 19
    base = rng.normal(3.43, 0.35, n)
    per_model = {compare.FSIDE: {"perMotor": base}}
    for mid in (compare.CONTROL_CURRENT,) + compare.ADVERSARIES:
        per_model[mid] = {"perMotor": base + rng.normal(0.001, 0.30, n)}
    cmap = compare.contrasts(per_model, n_rep=2000)
    c = cmap[compare.CONTROL_CURRENT]
    assert c["verdict"] == status.NOT_ESTABLISHED
    text = c["interpretation"].lower()
    assert "not equivalence" in text and "underpowered is not equivalence" in text
    for banned in ("no difference between", "equivalent to", "on par"):
        assert banned not in text


def test_strongest_adversary_is_selected_by_point_estimate_but_never_verdicted_by_it():
    per_model = {m: {"motorEqual": v} for m, v in
                 (("M0_EXPONENTIAL", 3.55), ("M1_WEIBULL", 3.44), ("M2_LOGNORMAL", 3.41),
                  ("M5_GAMMA", 3.47), ("M8_EMPIRICAL_KDE", 3.42))}
    out = compare.strongest_adversary(per_model)
    assert out["model"] == "M2_LOGNORMAL"
    assert [r["model"] for r in out["ranking"]][0] == "M2_LOGNORMAL"
    assert "never a verdict" in out["selectionBasis"]


# ===================================================================== bootstrap unit
def test_bootstrap_resamples_motors_not_events():
    """19 motors => at most 19 distinct values can appear in any resample of the per-motor array.

    If the bootstrap resampled the 233 EVENTS the per-motor structure would be destroyed and the
    contrast variance would collapse - the pseudoreplication failure mode.
    """
    a = np.arange(19, dtype=np.float64)
    b = a + 1.0
    d = score.motor_cluster_bootstrap(a, b, n_rep=1000, seed=compare.BOOT_SEED)
    assert len(d) == 1000
    assert np.allclose(d, 1.0), "a paired constant shift must give a constant contrast"

    # the resampled means must be reachable as means of 19 draws from 19 motors
    d2 = score.motor_cluster_bootstrap(a, np.zeros(19), n_rep=2000, seed=1)
    scaled = -d2 * 19.0
    assert np.allclose(scaled, np.round(scaled), atol=1e-9), \
        "resampled sums must be integer sums of MOTOR values, not event values"


def test_bootstrap_uses_a_single_construction_rng_and_no_python_hash():
    src = (SRC / "motor_stack_aif" / "score.py").read_text(encoding="utf-8")
    assert src.count("default_rng(") == 1, "RNG must be constructed exactly once"
    # `hash(` must not appear as executable code (D3: PYTHONHASHSEED makes it nondeterministic).
    assert "hash" not in _executable_tokens(COMPARE_SOURCE), \
        "python hash() is nondeterministic across runs (D3)"


# ===================================================================== determinism
def test_same_seed_gives_identical_bytes():
    n = 19
    rng = np.random.default_rng(11)
    base = rng.normal(3.43, 0.3, n)
    per_model = {compare.FSIDE: {"perMotor": base}}
    for mid in (compare.CONTROL_CURRENT,) + compare.ADVERSARIES:
        per_model[mid] = {"perMotor": base + rng.normal(0.01, 0.2, n)}
    a = compare.to_json(compare.contrasts(per_model, n_rep=500, seed=compare.BOOT_SEED))
    b = compare.to_json(compare.contrasts(per_model, n_rep=500, seed=compare.BOOT_SEED))
    assert a == b
    c = compare.to_json(compare.contrasts(per_model, n_rep=500, seed=compare.BOOT_SEED + 1))
    assert a != c, "a different seed must actually change the bootstrap draw"


def test_canonical_json_is_indent1_sortkeys_and_lf_terminated():
    text = compare.to_json({"b": 1, "a": {"d": 2, "c": 3}})
    assert text.endswith("\n") and "\r" not in text
    assert text.splitlines()[1].startswith(' "a"'), "indent=1, sort_keys=True"
    json.loads(text)


def test_canonical_json_refuses_nan():
    with pytest.raises(ValueError):
        compare.to_json({"x": float("nan")})


# ===================================================================== D5 firewall
def test_compare_never_requests_mark_fields():
    """No mark field name survives as EXECUTABLE code.

    Comments and string literals are stripped by `_executable_tokens`, so the D5 quarantine may be
    described in prose (and the denylist may hold the names as strings) while any real
    dereference - `e["nextStateN"]`, `raw.get("jump")`, an attribute, a variable - would show up
    in the token stream and fail this test.
    """
    assert set(compare._FORBIDDEN_EVENT_FIELDS) == {"nextStateN", "direction", "jump"}
    assert not (set(compare._ALLOWED_EVENT_FIELDS) & set(compare._FORBIDDEN_EVENT_FIELDS))
    toks = _executable_tokens(COMPARE_SOURCE)
    for banned in ("nextStateN", "jump", "direction"):
        assert banned not in toks, "mark field %r appears as executable code in compare.py" % banned


def test_the_mark_field_scan_is_not_vacuous():
    """The scan must actually catch a real dereference - otherwise it proves nothing."""
    toks = _executable_tokens('x = e["nextStateN"] + raw.get("jump")\n')
    # string literals are stripped, so a dict lookup by literal key is caught via the ast pass
    assert "nextStateN" in _literal_keys('x = e["nextStateN"]\n')
    assert "jump" in _literal_keys('raw.get("jump")\n')
    assert "nextStateN" not in _literal_keys('# nextStateN is never read\n')
    # and compare.py's own subscript/keyword literals never name a mark field
    for k in _literal_keys(COMPARE_SOURCE):
        assert k not in compare._FORBIDDEN_EVENT_FIELDS, k
    assert toks is not None


def test_project_event_copies_only_the_allow_list_and_touches_nothing_else():
    class MarkTrap(dict):
        def __getitem__(self, k):
            if k in compare._FORBIDDEN_EVENT_FIELDS:
                raise AssertionError("D5 VIOLATION: compare.py read mark field %r" % k)
            return dict.__getitem__(self, k)

        def get(self, k, default=None):
            if k in compare._FORBIDDEN_EVENT_FIELDS:
                raise AssertionError("D5 VIOLATION: compare.py read mark field %r" % k)
            return dict.get(self, k, default)

    raw = MarkTrap(eventId="e1", motorId="m1", partition="holdout", stateN=3,
                   durationS=4.0, rightCensored=False, _y=0.63, _rowidx=0,
                   nextStateN=4, direction="CW", jump=1)
    out = compare.project_event(raw)
    assert set(out) == set(compare._ALLOWED_EVENT_FIELDS)
    assert "nextStateN" not in out and "jump" not in out and "direction" not in out


def test_inputs_carry_no_mark_fields(inp):
    for row in inp.holdout_rows:
        assert not (set(row) & set(compare._FORBIDDEN_EVENT_FIELDS))
    prov = inp.split_provenance()
    assert prov["channel"] == "DURATION_ONLY"
    assert "NOT_READ" in prov["markChannel"]


# ===================================================================== split provenance
def test_split_is_the_frozen_one_not_a_recomputed_one(inp):
    prov = inp.split_provenance()
    assert prov["nHoldoutMotors"] == 19 and prov["nTrainMotors"] == 80
    assert prov["nHoldoutEvents"] == 233 and prov["nTrainEvents"] == 793
    assert prov["splitRecomputed"] is False
    assert inp.holdout_motors == compare._bridge.b3_result()["cohorts"][
        compare.COHORT_NAME]["holdoutMotors"]


def test_frozen_scale_N_matches_the_published_record(inp):
    published = compare._bridge.b3_result()["cohorts"][compare.COHORT_NAME]["scaleN"]
    assert inp.scale_n == {int(k): v for k, v in published.items()}


def test_control_current_is_M3_and_is_not_refitted(inp, pinned):
    assert compare.CONTROL_CURRENT == "M3_TWO_TIMESCALE"
    f = pinned[compare.CONTROL_CURRENT]
    assert f["paramsVector"] == [0.3933559993214189, 0.44485933051063775]
    assert "NOT refitted" in f["source"]


def test_no_floor_policy_halts_on_a_nonfinite_score():
    with pytest.raises(compare.NonFiniteScore):
        compare._check_finite(np.array([1.0, np.inf]), "test")


# ===================================================================== full-run plumbing
def test_run_comparison_plumbing_executes_without_computing_the_prospective_score(
        monkeypatch, inp, pinned):
    """STRUCTURAL dry run of `score_all` -> `contrasts` -> `build_result` -> `to_json`.

    The F-side HELD-OUT scorers are stubbed with constants, so the prospective quantity - the
    held-out score of the TRAIN-FITTED motor stack - is NOT computed here. Everything else runs
    for real, including the adversary scoring (which only recomputes numbers B3 already
    published) and the canonical serialisation.
    """
    from motor_stack_aif import baselines
    monkeypatch.setattr(compare, "score_fside_marginal_per_event",
                        lambda f, y, c, nodes=None: np.full(len(y), 1.234))
    monkeypatch.setattr(score, "score_motor_stack", lambda f, bym: np.full(len(bym), 1.111))

    fitted = dict(pinned)
    fitted[compare.FSIDE] = {"mu": 0.0, "tau": 0.5, "nFreeParams": 2, "source": "STUB_NOT_A_FIT"}
    for n in ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
        fitted[n] = baselines.FITTERS[n](inp.train_y)

    oracle = compare.oracle_consistency_check(inp, fitted)
    per_model = compare.score_all(inp, fitted)
    cmap = compare.contrasts(per_model, n_rep=200)
    result = compare.build_result(inp, fitted, oracle, per_model, cmap)
    text = compare.to_json(result)
    round_tripped = json.loads(text)

    assert round_tripped["oracleConsistencyCheck"]["status"] == "PASS"
    assert round_tripped["scaleConvention"]["reportedScale"] == compare.SCALE_SECONDS
    assert round_tripped["splitProvenance"]["nHoldoutMotors"] == 19
    assert round_tripped["control"]["refitted"] is False
    assert round_tripped["intervalType"] == "percentile"
    assert round_tripped["floorPolicy"].startswith("NO_FLOOR")
    assert round_tripped["resolution"]["halfWidthFloorNats"] == 0.042
    assert "claimBoundary" in round_tripped
    assert all(len(v) == 19 for v in round_tripped["perMotorNLPD"].values())
    # the SECONDARY joint-per-motor score is present and explicitly not contrasted
    assert compare.FSIDE + "__JOINT_PER_MOTOR" in round_tripped["perMotorNLPD"]
    assert compare.FSIDE + "__JOINT_PER_MOTOR" not in round_tripped["contrasts"]
    assert compare.to_json(result) == text, "serialisation must be byte-stable"


def test_refitted_adversaries_reproduce_the_frozen_published_holdout_scores(inp):
    """Independent-implementation check on the ADVERSARIES.

    The F-side fitters and log densities are a separate implementation from the frozen runner's,
    with a different optimiser contract, so agreement here is not circular. Tolerance is set by
    OPTIMISER convergence (B3 uses a 301-start grid/DE contract, the F-side a bounded scalar
    minimise), not by scoring convention - which is why it is looser than ORACLE_TOL and is
    declared separately rather than folded into it.
    """
    from motor_stack_aif import baselines
    published = inp.published["scores"]
    for name in ("M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
        f = baselines.FITTERS[name](inp.train_y)
        logn = np.asarray(baselines.LOGPDF[name](inp.holdout_y, f["params"]), dtype=np.float64)
        pe = compare.to_seconds_scale(-logn, inp.holdout_states, inp.scale_n)
        agg = compare.aggregate(pe, inp.holdout_motor_ids, inp.holdout_motors)
        ref = published[name]["NLPD_motor_equal"]["motorEqual"]
        assert agg["motorEqual"] == pytest.approx(ref, abs=1e-7), (name, agg["motorEqual"], ref)


# ===================================================================== regression: k-domain guard
def test_extreme_latent_does_not_crash_the_marginal_with_OverflowError():
    """REGRESSION. The old guard (1e-6 < k) let the optimiser reach k where the mean-one Weibull
    scale exp(-lgamma(1+1/k)) overflows IEEE double, raising OverflowError out of the objective
    instead of marking the quadrature node infeasible. That crashed fit_motor_stack on the real
    training cohort.
    """
    y = np.array([0.5, 1.5])
    c = np.array([False, False])
    ll = hierarchy.motor_log_marginal(y, c, mu=-30.0, tau=3.0)       # drives k far below 1/170
    assert isinstance(ll, float)
    post = hierarchy.posterior_motor_shape(y, c, mu=-30.0, tau=3.0)
    assert set(post) == {"eta_mean", "eta_sd", "k_mean_exp"}


def test_k_min_representable_is_derived_from_the_overflow_bound_not_tuned():
    from scipy import special
    k = hierarchy.K_MIN_REPRESENTABLE
    assert math.isfinite(math.exp(special.gammaln(1.0 + 1.0 / k)))
    with pytest.raises(OverflowError):
        math.exp(special.gammaln(1.0 + 1.0 / (k * 0.99)))
