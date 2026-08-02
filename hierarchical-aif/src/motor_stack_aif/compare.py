"""F-side motor-stack scoring harness — held-out model competition on the FROZEN B3 split.

WHAT THIS DOES
--------------
Puts the F-side motor-stack candidate on the SAME held-out split, the SAME cohort, the SAME
scoring rule and the SAME aggregation as the frozen B3 model competition, so its held-out score is
comparable to the recorded control and adversaries rather than merely plausible-looking.

Protocol: `hierarchical-aif/protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md`, which is
pre-registered BEFORE this harness is run on holdout.

D5 HELD-OUT DATA FIREWALL
-------------------------
This module is DURATION-ONLY. It never reads, loads, prints or reasons about the held-out mark
channel (`nextStateN`, `direction`, `jump`). Every raw event dict that enters this module is
projected through `project_event()`, which copies an explicit allow-list of fields and nothing
else. `_FORBIDDEN_EVENT_FIELDS` is declared once, is never dereferenced, and exists so the guard
is checkable by a test rather than by trust. The held-out DURATION channel was already
prospectively spent by B3; duration-only held-out scoring is the permitted use.

UNITS — THE THING MOST LIKELY TO GO SILENTLY WRONG
--------------------------------------------------
B3's published `NLPD_motor_equal` is on the SECONDS scale: it is the negative log density of the
observed dwell in seconds, i.e. the normalised-`y` log density plus the Jacobian `+log(scale_N)`
per event. The F-side `score.score_motor_stack` returns NLPD on the NORMALISED `y` scale, with no
Jacobian. The two differ by a per-event constant. That constant CANCELS in a contrast and does NOT
cancel in an absolute score, so a mistake here would leave every contrast looking right while
every absolute number was wrong by ~2 nats.

Every number this module reports is on ONE declared scale (`SECONDS`), recorded in the output as
`scaleConvention`. The `to_seconds_scale()` conversion is a single named function so the
independent-oracle check below can be mutated to prove it actually fires.

NO FLOOR
--------
A non-finite log density HALTS, matching B3's declared `NO_FLOOR` policy. A floor would convert an
impossible observation into a merely unlikely one and inflate every score downstream.

DETERMINISM
-----------
Fixed bootstrap seed, RNG constructed exactly once per contrast (common random numbers across
contrasts, as B3 does), no Python-hash-derived seeding (D3), no ambient randomness. Same inputs
produce identical JSON bytes.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from . import _bridge, baselines, fit, hierarchy, score, status

# --------------------------------------------------------------------------- frozen constants
COHORT_NAME = "derived_eligible_1_to_8"
COHORT_STATES = tuple(range(1, 9))

FSIDE = "F_MOTOR_STACK"
CONTROL_CURRENT = "M3_TWO_TIMESCALE"
ADVERSARIES = ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA", "M8_EMPIRICAL_KDE")

#: Every reported NLPD is on this scale. See the module docstring.
SCALE_SECONDS = "SECONDS"
SCALE_NORMALISED = "NORMALISED_Y"

#: Bootstrap. Same seed as the frozen B3 runner so the resampling stream is the house stream.
BOOT_SEED = 20260717
N_BOOT = 2000

#: Corrected resolution floor (motor-equal contrast half-width), from the B3 recheck.
RESOLUTION_FLOOR_HALFWIDTH_NATS = 0.042

#: Decision threshold for every contrast. A contrast interval containing this is NOT_ESTABLISHED.
DECISION_THRESHOLD = 0.0

#: Independent-oracle tolerance. JUSTIFICATION: the oracle recomputes B3's published aggregate
#: from parameters read verbatim out of the frozen JSON (Python float repr round-trips exactly)
#: on a cohort rebuilt by the frozen `Cohort` class in the frozen event order, using the frozen
#: `holdout_lognorm`. Every floating-point operation and every summation order is therefore
#: identical to the recorded run, so the expected residual is EXACTLY 0.0 and the only admissible
#: slack is last-place noise. 1e-12 absolute on a value of ~3.43 is ~3e-13 relative, i.e. about
#: 1000 ULP of headroom. This tolerance is NOT to be loosened to make a check pass: if the residual
#: exceeds it, the convention is wrong and the discrepancy is the finding.
ORACLE_TOL = 1e-12

#: Per-motor arrays are compared against the frozen runner's own aggregation under a SEPARATE,
#: looser tolerance, and here is exactly why. The frozen runner averages a motor's events in its
#: own within-motor order (sorted by `durationS, stateN, rowidx`); `score.per_motor_means` averages
#: them in frozen ROW order. Same multiset, different floating-point summation order, so the
#: per-motor means can differ in the last few ULP even when every per-event value is bit-identical.
#: Measured difference on this cohort: 8.881784197001252e-16 (4 ULP at ~3.4). This is recorded as
#: an observation, not absorbed: the motor-equal AGGREGATE residual against the published number is
#: nevertheless exactly 0.0, which is the number the verdict depends on.
PER_MOTOR_ULP_TOL = 1e-13

# --------------------------------------------------------------------------- D5 field guard
#: Declared once, NEVER dereferenced. Present so a test can assert the allow-list excludes them.
_FORBIDDEN_EVENT_FIELDS = ("nextStateN", "direction", "jump")

#: The only raw-event fields this module is permitted to read.
_ALLOWED_EVENT_FIELDS = ("eventId", "motorId", "partition", "stateN", "durationS",
                         "rightCensored", "_y", "_rowidx")


def project_event(raw) -> dict:
    """Copy the duration-only allow-list out of a frozen raw event dict.

    The single door through which raw event dicts enter this module. Mark fields are not in the
    allow-list, are never requested, and cannot leak through.
    """
    return {k: raw[k] for k in _ALLOWED_EVENT_FIELDS if k in raw}


class OracleConsistencyError(RuntimeError):
    """The recomputed convention does not reproduce the frozen published number.

    Raised as a HALT. The harness must never proceed to a verdict on an unvalidated convention.
    """


class NonFiniteScore(RuntimeError):
    """A non-finite NLPD. NO FLOOR is applied - this halts, matching B3."""


# =========================================================================== inputs
class Inputs:
    """Frozen cohort projected to duration-only fields, plus the frozen published record."""

    def __init__(self):
        self.cohort = _bridge.frozen_cohort(states=COHORT_STATES, name=COHORT_NAME)
        coh = self.cohort
        self.published = _bridge.b3_result()["cohorts"][COHORT_NAME]

        self.holdout_motors = list(coh.holdout_motors)
        self.train_motors = list(coh.train_motors)
        self.scale_n = {int(k): float(v) for k, v in coh.scale_N.items()}

        # duration-only projections, in the frozen holdout row order
        self.holdout_rows = [project_event(e) for e in coh.holdout]
        self.holdout_motor_ids = [r["motorId"] for r in self.holdout_rows]
        self.holdout_states = [int(r["stateN"]) for r in self.holdout_rows]
        self.holdout_y = np.asarray(coh.holdout_y, dtype=np.float64)
        self.holdout_censored = np.array(
            [bool(r["rightCensored"]) for r in self.holdout_rows], dtype=bool)

        # training data, grouped by motor (the experimental unit) and pooled
        self.train_y = np.asarray(coh.train_y, dtype=np.float64)
        self.train_by_motor = [(np.asarray(a, dtype=np.float64),
                                np.zeros(len(a), dtype=bool))
                               for a in coh.train_by_motor]

        # holdout grouped by motor, in the SAME order as holdout_motors (sorted motor id)
        self.holdout_by_motor = []
        for m in self.holdout_motors:
            rows = [project_event(e) for e in coh.holdout_by_motor[m]]
            y = np.array([r["_y"] for r in rows], dtype=np.float64)
            c = np.array([bool(r["rightCensored"]) for r in rows], dtype=bool)
            self.holdout_by_motor.append((y, c))

        # the frozen cohort EXCLUDES right-censored events; assert rather than assume
        if bool(self.holdout_censored.any()):
            raise AssertionError(
                "frozen cohort must contain no right-censored events; the censoring branch of the "
                "F-side likelihood is therefore UNEXERCISED on this cohort and that limitation is "
                "recorded, not hidden")

    def split_provenance(self) -> dict:
        return {
            "cohort": COHORT_NAME,
            "states": list(COHORT_STATES),
            "splitRule": "sha256_mod5(motorId) == 0 => holdout, else train (FROZEN, reused)",
            "splitRecomputed": False,
            "rightCensoredPolicy": ("EXCLUDED from the frozen cohort entirely; the F-side "
                                    "censoring branch is unexercised here"),
            "nTrainMotors": len(self.train_motors),
            "nHoldoutMotors": len(self.holdout_motors),
            "nTrainEvents": int(len(self.train_y)),
            "nHoldoutEvents": int(len(self.holdout_y)),
            "holdoutMotors": list(self.holdout_motors),
            "channel": "DURATION_ONLY",
            "markChannel": ("NOT_READ - nextStateN/direction/jump are never requested (D5)"),
            "holdoutDurationStatus": ("already prospectively spent by B3; duration-only held-out "
                                      "scoring is the permitted reuse"),
        }


# =========================================================================== scale handling
def to_seconds_scale(nlpd_normalised, states, scale_n, mode: str = SCALE_SECONDS):
    """Convert per-event NLPD from the normalised-`y` scale to the SECONDS scale.

        y = duration / scale_N[state]
        -log p(duration) = -log p(y) + log scale_N[state]

    `mode=SCALE_NORMALISED` deliberately SKIPS the Jacobian. That is the units defect this
    harness exists to catch; it is a parameter so the oracle check can be mutated and shown to
    fire, rather than being asserted to fire.
    """
    arr = np.asarray(nlpd_normalised, dtype=np.float64)
    if mode == SCALE_NORMALISED:
        return arr
    if mode != SCALE_SECONDS:
        raise ValueError("unknown scale mode %r" % (mode,))
    jac = np.array([math.log(scale_n[int(s)]) for s in states], dtype=np.float64)
    return arr + jac


def _check_finite(arr, what: str):
    a = np.asarray(arr, dtype=np.float64)
    if not np.all(np.isfinite(a)):
        raise NonFiniteScore(
            "%s produced %d non-finite value(s); NO FLOOR is applied by policy (matches B3)"
            % (what, int(np.sum(~np.isfinite(a)))))
    return a


def aggregate(per_event_nlpd, motor_ids, expected_motor_order):
    """Motor-equal aggregation, asserted to be aligned to the expected motor order."""
    keys, per_motor = score.per_motor_means(per_event_nlpd, motor_ids)
    if list(keys) != list(expected_motor_order):
        raise AssertionError("per-motor arrays are misaligned: %r vs %r"
                             % (list(keys), list(expected_motor_order)))
    return {
        "perMotor": per_motor,
        "motorEqual": float(np.mean(per_motor)),
        "eventPooled": float(np.mean(np.asarray(per_event_nlpd, dtype=np.float64))),
    }


# =========================================================================== fitting (TRAIN ONLY)
def fit_pinned_only(inp: Inputs) -> dict:
    """The two PARAMETER-PINNED competitors: CONTROL_CURRENT M3 and the frozen-bandwidth M8.

    Neither involves an optimisation, so this is cheap and is enough to run the independent-oracle
    consistency check on its own.
    """
    out = {}
    p3 = list(inp.published["fitted"][CONTROL_CURRENT]["params"])
    out[CONTROL_CURRENT] = {
        "model": CONTROL_CURRENT,
        "params": {"w": float(p3[0]), "lambdaFast": float(p3[1])},
        "paramsVector": p3,
        "trainNLL": float(inp.published["fitted"][CONTROL_CURRENT]["trainNLL"]),
        "source": "FROZEN_B3_RESULT (NOT refitted - this is CONTROL_CURRENT)",
        "fittedOn": "TRAIN_ONLY (frozen B3 fit, reused verbatim)",
    }

    b3 = _bridge.b3()
    h = float(inp.published["fitted"]["M8_EMPIRICAL_KDE"]["h"])
    s, ybar, n = b3._kde_s(inp.train_y, h)
    out["M8_EMPIRICAL_KDE"] = {
        "model": "M8_EMPIRICAL_KDE",
        "params": {"h": h, "nKdeLocations": int(n)},
        "_kdeParams": {"h": h, "s": s, "n": int(n)},
        "ybarDeviation": abs(float(ybar) - 1.0),
        "source": ("FROZEN_B3_BANDWIDTH: h read from the frozen record; the KDE locations s are "
                   "recomputed deterministically from the TRAINING events only. No cross-"
                   "validation is re-run and no holdout data enters the fit."),
        "fittedOn": "TRAIN_ONLY (bandwidth frozen, locations from 793 training events)",
        "included": True,
        "inclusionReason": ("INCLUDED: obtainable from the frozen record with no new exploratory "
                            "holdout work, and its recomputed holdout aggregate reproduces the "
                            "published M8 score exactly, which makes it a third oracle."),
    }
    return out


def fit_train_only(inp: Inputs) -> dict:
    """Fit every refittable competitor on TRAINING data only, plus the pinned ones.

    M3 is NOT refitted: it is CONTROL_CURRENT and its parameters are read verbatim from the frozen
    B3 record. M8's bandwidth is likewise read from the frozen record; only its KDE locations are
    recomputed, deterministically, from the training events.
    """
    out = fit_pinned_only(inp)

    out[FSIDE] = fit.fit_motor_stack(inp.train_by_motor)
    out[FSIDE]["fittedOn"] = "TRAIN_ONLY (80 motors, motor-grouped marginal likelihood)"
    out[FSIDE]["source"] = "F_SIDE_FIT"

    for name in ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
        f = baselines.FITTERS[name](inp.train_y)
        f["fittedOn"] = "TRAIN_ONLY (pooled training _y, 793 events)"
        f["source"] = "F_SIDE_FIT"
        out[name] = f
    return out


# =========================================================================== independent oracle
def oracle_consistency_check(inp: Inputs, fitted: dict,
                             scale_mode: str = SCALE_SECONDS,
                             tol: float = ORACLE_TOL) -> dict:
    """Reproduce B3's published motor-equal NLPD for the parameter-pinned models. HALTS on failure.

    Three targets, all with parameters that are pinned rather than refitted, so any residual is a
    convention error and nothing else:

      M3_TWO_TIMESCALE  - params verbatim from the frozen record (CONTROL_CURRENT)
      M0_EXPONENTIAL    - parameter-FREE, so it is an unconditional check on scale + aggregation
      M8_EMPIRICAL_KDE  - bandwidth frozen, locations deterministic from training events

    The B3 normalised-space log density is taken from the frozen `holdout_lognorm`; the SCALE
    conversion and the MOTOR-EQUAL aggregation are this module's own. That is what is under test.
    A second, redundant check compares the per-event vector against `b3.nlpd_per_event`.
    """
    b3 = _bridge.b3()
    coh = inp.cohort
    checks = []

    targets = [
        (CONTROL_CURRENT, list(fitted[CONTROL_CURRENT]["paramsVector"]),
         "frozen B3 fitted params, not refitted"),
        ("M0_EXPONENTIAL", [], "parameter-free: an unconditional scale/aggregation check"),
        ("M8_EMPIRICAL_KDE", fitted["M8_EMPIRICAL_KDE"]["_kdeParams"],
         "frozen bandwidth, training-only locations"),
    ]

    for model_id, params, why in targets:
        logn = np.asarray(b3.holdout_lognorm(model_id, params, coh), dtype=np.float64)
        mine = to_seconds_scale(-logn, inp.holdout_states, inp.scale_n, mode=scale_mode)
        _check_finite(mine, "oracle per-event NLPD for %s" % model_id)
        agg = aggregate(mine, inp.holdout_motor_ids, inp.holdout_motors)
        published = float(inp.published["scores"][model_id]["NLPD_motor_equal"]["motorEqual"])
        residual = float(agg["motorEqual"] - published)

        # redundant path: the frozen runner's own per-event NLPD and its own per-motor array
        frozen_pe = np.asarray(b3.nlpd_per_event(model_id, params, coh), dtype=np.float64)
        per_event_max_abs_diff = float(np.max(np.abs(mine - frozen_pe)))
        frozen_agg = b3.aggregate_motor_equal(frozen_pe, coh)
        per_motor_max_abs_diff = float(np.max(np.abs(
            agg["perMotor"] - np.asarray(frozen_agg["perMotor"], dtype=np.float64))))

        checks.append({
            "model": model_id,
            "why": why,
            "recomputedMotorEqual": float(agg["motorEqual"]),
            "publishedMotorEqual": published,
            "residual": residual,
            "absResidual": abs(residual),
            "perEventMaxAbsDiffVsFrozenRunner": per_event_max_abs_diff,
            "perMotorMaxAbsDiffVsFrozenRunner": per_motor_max_abs_diff,
            "perMotorTolerance": PER_MOTOR_ULP_TOL,
            "tolerance": tol,
            "pass": bool(abs(residual) <= tol
                         and per_event_max_abs_diff <= tol
                         and per_motor_max_abs_diff <= PER_MOTOR_ULP_TOL),
        })

    failures = [c for c in checks if not c["pass"]]
    result = {
        "status": "PASS" if not failures else "FAIL",
        "scaleMode": scale_mode,
        "tolerance": tol,
        "toleranceJustification": (
            "Parameters are read verbatim from the frozen JSON and the cohort is rebuilt by the "
            "frozen Cohort class in the frozen event order, so every FP operation and summation "
            "order matches the recorded run: the expected residual is exactly 0.0 and 1e-12 "
            "absolute (~3e-13 relative, ~1000 ULP) is pure last-place headroom. The tolerance is "
            "not to be loosened; a residual above it is a convention error and is the finding."),
        "checks": checks,
        "note": ("B3 stores only AGGREGATED scores - there are no per-motor arrays in the frozen "
                 "record - so every per-motor array here is recomputed. That is exactly why this "
                 "check is mandatory rather than optional."),
    }
    if failures:
        raise OracleConsistencyError(
            "independent-oracle consistency check FAILED under scale mode %r; the harness HALTS "
            "and does not proceed to a verdict on an unvalidated convention. Failures: %s"
            % (scale_mode, json.dumps(failures, sort_keys=True)))
    return result


# =========================================================================== scoring
_B3_PARAM_KEY = {"M0_EXPONENTIAL": None, "M1_WEIBULL": "k",
                 "M2_LOGNORMAL": "sigma", "M5_GAMMA": "shape"}


def _b3_param_vector(model_id: str, params: dict) -> list:
    """Translate an F-side baseline parameter dict into the frozen runner's positional vector."""
    key = _B3_PARAM_KEY[model_id]
    return [] if key is None else [float(params[key])]


class NotConverged(RuntimeError):
    """F16: a fit that did not converge must halt BEFORE scoring, and write no artifact."""


def _require_converged(fitted: dict, where: str) -> None:
    """An optimiser that reports failure has still returned finite parameters.

    Scoring them yields a finite NLPD that is comparable-looking and meaningless. The halt belongs
    at the SCORING boundary rather than at the fit, because a fit is allowed to fail — what is not
    allowed is a failed fit being scored as though it had succeeded.

    ABSENCE OF THE FLAG IS NOT EVIDENCE OF CONVERGENCE. Defaulting a missing `converged` to True
    is the same bug wearing a different hat, so it is refused too.
    """
    if fitted.get("converged") is not True:
        raise NotConverged(
            "%s: refusing to score a fit whose convergence is %r. The optimiser did not report "
            "success, and its parameters are finite regardless — scoring them produces a number "
            "that looks comparable and is not (F16)." % (where, fitted.get("converged")))


def score_fside_marginal_per_event(fitted_fside: dict, y, censored, nodes=None):
    """Per-event marginal NLPD on the NORMALISED scale, latent integrated.

    Each event is scored under p(y_i) = INT f(y_i | k=exp(eta)) N(eta; mu, tau) d eta - i.e. the
    same information set every other competitor gets (one event, no help from the motor's other
    events). This is the DIRECTLY COMPARABLE score and is the PRIMARY one.
    """
    _require_converged(fitted_fside, "score_fside_marginal_per_event")
    mu, tau = float(fitted_fside["mu"]), float(fitted_fside["tau"])
    nodes = nodes if nodes is not None else hierarchy.gauss_hermite()
    y = np.asarray(y, dtype=np.float64)
    c = np.asarray(censored, dtype=bool)
    out = np.empty(len(y), dtype=np.float64)
    for i in range(len(y)):
        ll = hierarchy.motor_log_marginal(y[i:i + 1], c[i:i + 1], mu, tau, nodes=nodes)
        out[i] = -ll
    return _check_finite(out, "F-side per-event marginal NLPD")


def score_all(inp: Inputs, fitted: dict) -> dict:
    """Per-motor mean NLPD on the SECONDS scale for every competitor, aligned to holdout_motors."""
    b3 = _bridge.b3()
    coh = inp.cohort
    per_model = {}

    # ---- adversaries + control, via the F-side logpdf where one exists, else the frozen library
    for model_id in (CONTROL_CURRENT,) + ADVERSARIES:
        cross = None
        if model_id in baselines.LOGPDF:
            params = fitted[model_id]["params"]
            logn = np.asarray(baselines.LOGPDF[model_id](inp.holdout_y, params),
                              dtype=np.float64)
            impl = "F_SIDE_INDEPENDENT_IMPLEMENTATION"
            # independent-implementation cross-check: the frozen B3 density at the SAME params.
            # Reported, never used to correct the F-side number.
            b3p = _b3_param_vector(model_id, params)
            frozen_logn = np.asarray(b3.holdout_lognorm(model_id, b3p, coh), dtype=np.float64)
            cross = float(np.max(np.abs(logn - frozen_logn)))
        elif model_id == CONTROL_CURRENT:
            logn = np.asarray(
                b3.holdout_lognorm(model_id, list(fitted[model_id]["paramsVector"]), coh),
                dtype=np.float64)
            impl = "FROZEN_B3_SCORING_FUNCTION (control is not reimplemented or refitted)"
        elif model_id == "M8_EMPIRICAL_KDE":
            logn = np.asarray(
                b3.holdout_lognorm(model_id, fitted[model_id]["_kdeParams"], coh),
                dtype=np.float64)
            impl = "FROZEN_B3_SCORING_FUNCTION (frozen bandwidth, training-only locations)"
        else:
            raise ValueError(model_id)

        pe = to_seconds_scale(-logn, inp.holdout_states, inp.scale_n)
        _check_finite(pe, "per-event NLPD for %s" % model_id)
        agg = aggregate(pe, inp.holdout_motor_ids, inp.holdout_motors)
        agg["implementation"] = impl
        agg["scale"] = SCALE_SECONDS
        if cross is not None:
            agg["maxAbsLogDensityDiffVsFrozenB3AtSameParams"] = cross
        per_model[model_id] = agg

    # ---- F-side: PRIMARY marginal-per-event
    pe_norm = score_fside_marginal_per_event(fitted[FSIDE], inp.holdout_y, inp.holdout_censored)
    pe_sec = to_seconds_scale(pe_norm, inp.holdout_states, inp.scale_n)
    _check_finite(pe_sec, "per-event NLPD for %s" % FSIDE)
    agg = aggregate(pe_sec, inp.holdout_motor_ids, inp.holdout_motors)
    agg["implementation"] = "F_SIDE (33-node Gauss-Hermite marginal, latent integrated)"
    agg["scale"] = SCALE_SECONDS
    agg["informationSet"] = ("MARGINAL_PER_EVENT - each holdout event scored alone, the same "
                             "information set every competitor gets. PRIMARY.")
    per_model[FSIDE] = agg

    # ---- F-side: SECONDARY joint-per-motor, reported because it is a DIFFERENT information set
    joint_norm = score.score_motor_stack(fitted[FSIDE], inp.holdout_by_motor)
    mean_log_scale = np.array(
        [float(np.mean([math.log(inp.scale_n[int(r["stateN"])])
                        for r in (project_event(e) for e in coh.holdout_by_motor[m])]))
         for m in inp.holdout_motors], dtype=np.float64)
    joint_sec = np.asarray(joint_norm, dtype=np.float64) + mean_log_scale
    _check_finite(joint_sec, "F-side joint-per-motor NLPD")
    per_model[FSIDE + "__JOINT_PER_MOTOR"] = {
        "perMotor": joint_sec,
        "motorEqual": float(np.mean(joint_sec)),
        "eventPooled": None,
        "scale": SCALE_SECONDS,
        "implementation": "F_SIDE score.score_motor_stack + per-motor mean log scale_N",
        "informationSet": (
            "JOINT_PER_MOTOR / n - the motor's events share one latent and inform each other, "
            "so this is NOT the same scoring rule as the per-event competitors. SECONDARY, "
            "reported for completeness and never contrasted against the others."),
    }
    return per_model


# =========================================================================== contrasts
def contrasts(per_model: dict, n_rep: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    """Paired motor-cluster bootstrap contrasts of the F-side model against every competitor.

    CONVENTION (B3's, verbatim in direction):
        contrast = S(reference) - S(challenger)
        interval entirely ABOVE 0  => the CHALLENGER (F-side) predicts better than the reference
        interval entirely BELOW 0  => the REFERENCE predicts better than the F-side
        interval CONTAINS 0        => INCONCLUSIVE / NOT_ESTABLISHED (never "equivalent")
    """
    chal = np.asarray(per_model[FSIDE]["perMotor"], dtype=np.float64)
    out = {}
    for ref_id in (CONTROL_CURRENT,) + ADVERSARIES:
        ref = np.asarray(per_model[ref_id]["perMotor"], dtype=np.float64)
        c = score.contrast_with_ci(ref, chal, n_rep=n_rep, seed=seed)
        lo, hi = c["interval"]
        c["reference"] = ref_id
        c["challenger"] = FSIDE
        c["contrastDefinition"] = "S(%s) - S(%s), SECONDS scale" % (ref_id, FSIDE)
        c["role"] = "CONTROL_CURRENT" if ref_id == CONTROL_CURRENT else "ADVERSARY"
        c["verdict"] = status.verdict_from_ci(lo, hi, threshold=DECISION_THRESHOLD)
        c["interpretation"] = _interpret(c["verdict"], ref_id)
        c["halfWidth"] = 0.5 * (hi - lo)
        c["halfWidthBelongsTo"] = ("the PERCENTILE interval reported in `interval` (D7: the frozen "
                                   "B3 `width` field was the percentile companion while verdicts "
                                   "used BCa; this harness reports percentile intervals only and "
                                   "says so)")
        c["atOrBelowResolutionFloor"] = bool(
            abs(c["pointEstimate"]) <= RESOLUTION_FLOOR_HALFWIDTH_NATS)
        out[ref_id] = c
    return out


def _interpret(verdict: str, ref_id: str) -> str:
    if verdict == status.RESOLVED_ABOVE:
        return ("Interval entirely above 0: the F-side motor stack predicts held-out DURATIONS "
                "better than %s on this cohort, at this sample size. Duration-only, no mechanism."
                % ref_id)
    if verdict == status.RESOLVED_BELOW:
        return ("Interval entirely below 0: %s predicts held-out DURATIONS better than the F-side "
                "motor stack. ADVERSE result against the F-side duration claim; retained and "
                "reported." % ref_id)
    return ("Interval contains 0: NOT_ESTABLISHED against %s. This is NOT equivalence and NOT "
            "'no difference'. With 19 holdout motors most contrasts are expected to be "
            "inconclusive against a ~%.3f-nat resolution floor. Underpowered is not equivalence."
            % (ref_id, RESOLUTION_FLOOR_HALFWIDTH_NATS))


def strongest_adversary(per_model: dict) -> dict:
    """The adversary with the LOWEST motor-equal NLPD point estimate.

    A point estimate is used ONLY to SELECT which adversary to name. It is never a verdict; the
    verdict for that adversary is the CI-bound contrast, identical to the others.
    """
    ranked = sorted(((m, float(per_model[m]["motorEqual"])) for m in ADVERSARIES),
                    key=lambda t: t[1])
    return {
        "model": ranked[0][0],
        "motorEqualNLPD": ranked[0][1],
        "ranking": [{"model": m, "motorEqual": v} for m, v in ranked],
        "selectionBasis": ("POINT ESTIMATE, used only to name which adversary is strongest. A "
                           "point estimate is never a verdict; see contrasts[<model>].verdict."),
    }


# =========================================================================== assembly
def _claim_boundary(oracle: dict) -> dict:
    return {
        "scope": ("Held-out DURATION prediction on the frozen derived_eligible_1_to_8 cohort of "
                  "Wadhwa-2022, 19 holdout motors, motor-equal NLPD, seconds scale."),
        # CORRECTED (Phase 8 item 8.3, landed in Phase 9 step 4.3). This read "P5 transfer, P6
        # intervention, P8 full verdict" — off by one against CLAUDE.md's ladder, and P7 was
        # omitted entirely. Every level above transfer was shifted up, which reads as a stronger
        # claim than the evidence licenses; and P7, independent replication, is the level this
        # programme is furthest from and the easiest to forget by leaving it off the list.
        "parityLadder": ("P3 duration-only ONLY. P4 transfer, P5 intervention, P6 mechanism, "
                         "P7 independent replication, P8 full verdict are untouched by this "
                         "result in either direction."),
        "doesNotEstablish": [
            "no mechanism: predictive ordering is never promoted to mechanism",
            "no biological parity at any level",
            "no active-inference claim: the dataset is passive and the action set is empty",
            ("no G-side policy claim; the expected-free-energy function does not exist in this "
             "package, a test enforces its absence, and it must not be added"),
            "nothing about the MARK process (nextStateN/direction/jump) - not read here (D5)",
            "nothing about species beyond E. coli behavioural evidence in this dataset",
            "nothing about B4C11, whose U4_OK remains withdrawn (D1)",
        ],
        "adverseRetained": ("M2_LOGNORMAL out-predicts the two-timescale mixture M3 by ~0.0369 "
                            "nats event-pooled in the frozen B3 record. M2 is an ADVERSARIAL "
                            "baseline, never the UNI model. This adverse result is reported "
                            "alongside this result, never instead of it."),
        "oracleStatus": oracle["status"],
        "allowedWording": ["target hypothesis", "candidate model", "CI-bound verdict",
                           "not established", "duration-only held-out support",
                           "F-side observational projection"],
    }


def build_result(inp: Inputs, fitted: dict, oracle: dict, per_model: dict,
                 contrast_map: dict) -> dict:
    fside_me = float(per_model[FSIDE]["motorEqual"])
    ordered = sorted(((m, float(per_model[m]["motorEqual"]))
                      for m in (FSIDE, CONTROL_CURRENT) + ADVERSARIES), key=lambda t: t[1])

    fitted_public = {}
    for k, v in fitted.items():
        fitted_public[k] = {kk: vv for kk, vv in v.items() if not kk.startswith("_")}

    return {
        "schema": "F-SIDE-MOTOR-STACK-SCORING/1",
        "protocol": "hierarchical-aif/protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md",
        "splitProvenance": inp.split_provenance(),
        "scaleConvention": {
            "reportedScale": SCALE_SECONDS,
            "definition": ("NLPD of the observed dwell in SECONDS = -log p(y) + log scale_N[state]"
                           ", y = durationS / scale_N[stateN]"),
            "matchesFrozenB3": True,
            "warning": ("score.score_motor_stack returns NORMALISED-y NLPD with no Jacobian. The "
                        "constant cancels in a CONTRAST and does not cancel in an ABSOLUTE score. "
                        "Every number in this file is on the SECONDS scale."),
            "scaleN": {str(k): v for k, v in sorted(inp.scale_n.items())},
        },
        "fitted": fitted_public,
        "oracleConsistencyCheck": oracle,
        "motorOrder": list(inp.holdout_motors),
        "perMotorNLPD": {m: [float(x) for x in np.asarray(per_model[m]["perMotor"])]
                         for m in per_model},
        "motorEqualNLPD": {m: float(per_model[m]["motorEqual"]) for m in per_model},
        "eventPooledNLPD": {m: (None if per_model[m].get("eventPooled") is None
                                else float(per_model[m]["eventPooled"]))
                            for m in per_model},
        "leaderboardMotorEqual": [{"model": m, "motorEqual": v} for m, v in ordered],
        "control": {"model": CONTROL_CURRENT, "role": "CONTROL_CURRENT",
                    "refitted": False,
                    "motorEqual": float(per_model[CONTROL_CURRENT]["motorEqual"])},
        "candidate": {"model": FSIDE, "motorEqual": fside_me, "nFreeParams": 2},
        "contrasts": contrast_map,
        "strongestAdversary": strongest_adversary(per_model),
        "aggregation": {"primary": "MOTOR_EQUAL", "experimentalUnit": "MOTOR",
                        "secondary": "EVENT_POOLED (continuity bridge only, never a verdict)"},
        "contrastConvention": ("contrast = S(reference) - S(challenger=%s). Interval entirely "
                              "above 0 => challenger better; entirely below 0 => reference "
                              "better; contains 0 => NOT_ESTABLISHED." % FSIDE),
        "intervalType": "percentile",
        "determinism": {"seed": BOOT_SEED, "nRep": N_BOOT,
                        "rngConstruction": "np.random.default_rng(seed) constructed ONCE per "
                                           "contrast; common random numbers across contrasts",
                        "resamplingUnit": "MOTOR", "usesPythonHash": False},
        "floorPolicy": "NO_FLOOR - a non-finite log density HALTS (matches frozen B3)",
        "resolution": {
            "halfWidthFloorNats": RESOLUTION_FLOOR_HALFWIDTH_NATS,
            "nHoldoutMotors": len(inp.holdout_motors),
            "canResolve": ("Differences whose paired per-motor contrast interval excludes 0. In "
                           "practice, with 19 motors, roughly >~%.3f nats of motor-equal "
                           "separation unless the per-motor difference is unusually consistent."
                           % RESOLUTION_FLOOR_HALFWIDTH_NATS),
            "cannotResolve": ("Anything smaller. An interval crossing 0 is NOT_ESTABLISHED / "
                              "INCONCLUSIVE - never 'no difference' and never 'equivalent'. "
                              "Underpowered is not equivalence. Replicates were not and must not "
                              "be increased after seeing a width."),
        },
        "m8Inclusion": {
            "included": True,
            "reason": fitted["M8_EMPIRICAL_KDE"]["inclusionReason"],
        },
        "claimBoundary": _claim_boundary(oracle),
    }


# =========================================================================== entry points
def run_comparison(n_rep: int = N_BOOT, seed: int = BOOT_SEED) -> dict:
    """FULL held-out comparison. Do not run before the protocol is committed."""
    inp = Inputs()
    fitted = fit_train_only(inp)
    oracle = oracle_consistency_check(inp, fitted)      # HALTS on failure
    per_model = score_all(inp, fitted)
    cmap = contrasts(per_model, n_rep=n_rep, seed=seed)
    return build_result(inp, fitted, oracle, per_model, cmap)


def smoke_train_only(n_rep: int = 200, seed: int = BOOT_SEED) -> dict:
    """End-to-end execution proof that touches NO held-out F-side score.

    Fits on train, runs the oracle check (which only recomputes numbers B3 already published), and
    scores the F-side model and the adversaries on the TRAINING motors. The held-out F-side score
    - the actual prospective quantity - is deliberately NOT computed here.
    """
    inp = Inputs()
    fitted = fit_train_only(inp)
    oracle = oracle_consistency_check(inp, fitted)

    train_motor_ids = []
    train_states = []
    train_y = []
    for e in inp.cohort.train:
        r = project_event(e)
        train_motor_ids.append(r["motorId"])
        train_states.append(int(r["stateN"]))
        train_y.append(float(r["_y"]))
    train_y = np.asarray(train_y, dtype=np.float64)

    per_model = {}
    for model_id in ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
        logn = np.asarray(baselines.LOGPDF[model_id](train_y, fitted[model_id]["params"]),
                          dtype=np.float64)
        pe = to_seconds_scale(-logn, train_states, inp.scale_n)
        per_model[model_id] = aggregate(pe, train_motor_ids, inp.train_motors)

    pe_f = to_seconds_scale(
        score_fside_marginal_per_event(fitted[FSIDE], train_y, np.zeros(len(train_y), bool)),
        train_states, inp.scale_n)
    per_model[FSIDE] = aggregate(pe_f, train_motor_ids, inp.train_motors)

    cmap = {}
    chal = per_model[FSIDE]["perMotor"]
    for ref_id in ("M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M5_GAMMA"):
        c = score.contrast_with_ci(per_model[ref_id]["perMotor"], chal, n_rep=n_rep, seed=seed)
        c["verdict"] = status.verdict_from_ci(c["interval"][0], c["interval"][1],
                                              threshold=DECISION_THRESHOLD)
        cmap[ref_id] = c

    return {
        "mode": "SMOKE_TRAIN_ONLY",
        "isVerdict": False,
        "warning": ("IN-SAMPLE training-motor scores. These are NOT held-out scores, carry NO "
                    "predictive claim, and must never be reported as a result. Execution proof "
                    "only. The held-out F-side score is deliberately not computed here."),
        "oracleConsistencyCheck": oracle,
        "fittedFSide": {k: v for k, v in fitted[FSIDE].items() if not k.startswith("_")},
        "trainMotorEqualNLPD_seconds": {m: per_model[m]["motorEqual"] for m in per_model},
        "trainContrasts": {k: {"pointEstimate": v["pointEstimate"], "interval": v["interval"],
                               "verdict": v["verdict"]} for k, v in cmap.items()},
        "nTrainMotors": len(inp.train_motors),
    }


def to_json(result: dict) -> str:
    """Deterministic canonical serialisation: indent=1, sort_keys=True, trailing LF."""
    return json.dumps(result, indent=1, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + "\n"


def write_result(path, result: dict) -> str:
    text = to_json(result)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return text
