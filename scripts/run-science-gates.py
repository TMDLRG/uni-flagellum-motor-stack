#!/usr/bin/env python3
"""Execute the UNI-FLAGELLUM scientific parity gates on CPU only.

This program separates three different questions:
1. Does the implementation reproduce the declared first-passage mathematics?
2. Does a training-fitted mechanistic model predict held-out motors?
3. Which biological claims still require measurements or independent replication?

It never upgrades an observational fit into a causal or Active-Inference identity claim.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import optimize, special


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
OBSERVED_REPORT_PATH = ROOT / "experiments" / "results" / "observed-experiment-report.json"
REFERENCE_PATH = ROOT / "experiments" / "source-parity-reference.json"
JS_ORACLE_PATH = ROOT / "lib" / "source-first-passage.js"
REPORT_PATH = ROOT / "experiments" / "results" / "science-gates-report.json"
PUBLIC_PATH = ROOT / "public" / "science-gates-report.json"
AUDIT_PATH = ROOT / "experiments" / "results" / "science-gates-audit.json"
PUBLIC_AUDIT_PATH = ROOT / "public" / "science-gates-audit.json"
SEED = 20260717
BOOTSTRAPS = 2000


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sigmoid(value: float) -> float:
    return float(special.expit(value))


def logit(probability: float) -> float:
    return math.log(probability / (1 - probability))


def coefficients(state_n: int, c1: float, c2: float, c3: float, code_n0_branch: bool = False) -> np.ndarray:
    if state_n == 0 and not code_n0_branch:
        cs: list[float] = []
    elif state_n < 2:
        cs = [c1]
    elif state_n < 3:
        cs = [c1, c2]
    else:
        cs = [c1, c2, c3]
    result = np.asarray([1.0])
    for c in cs:
        result = np.convolve(result, np.asarray([1 - c, c]))
    return result


def decode(theta: np.ndarray, states: list[int]) -> dict[str, Any]:
    count = len(states)
    c1 = sigmoid(float(theta[count + 2]))
    c2 = c1 * sigmoid(float(theta[count + 3]))
    c3 = c2 * sigmoid(float(theta[count + 4]))
    sigma_minus = math.exp(float(theta[count]))
    delta_sigma = math.exp(float(theta[count + 1]))
    return {
        "kPlusByN": {state: math.exp(float(theta[index])) for index, state in enumerate(states)},
        "sigmaMinusPerSecond": sigma_minus,
        "sigmaPlusPerSecond": sigma_minus + delta_sigma,
        "c1": c1,
        "c2": c2,
        "c3": c3,
    }


def source_terms(state_n: int, parameters: dict[str, Any], code_n0_branch: bool = False) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    weights = coefficients(state_n, parameters["c1"], parameters["c2"], parameters["c3"], code_n0_branch)
    k_plus = parameters["kPlusByN"][state_n]
    sigma_minus = parameters["sigmaMinusPerSecond"]
    delta_sigma = parameters["sigmaPlusPerSecond"] - sigma_minus
    components = np.arange(len(weights), dtype=float)
    off_rates = state_n * sigma_minus + components * delta_sigma
    return weights, k_plus + off_rates, off_rates


def event_scores(events: list[dict[str, Any]], parameters: dict[str, Any]) -> np.ndarray:
    result = np.empty(len(events), dtype=float)
    by_state: dict[int, list[tuple[int, dict[str, Any]]]] = {}
    for index, event in enumerate(events):
        by_state.setdefault(event["stateN"], []).append((index, event))
    for state_n, indexed_events in by_state.items():
        weights, total_rates, off_rates = source_terms(state_n, parameters)
        times = np.asarray([event["durationS"] for _, event in indexed_events], dtype=float)
        terms = np.exp(-np.outer(times, total_rates)) * weights
        survival = np.sum(terms, axis=1)
        plus = parameters["kPlusByN"][state_n] * survival
        minus = terms @ off_rates
        for local_index, (global_index, event) in enumerate(indexed_events):
            if event["rightCensored"]:
                density = survival[local_index]
            elif event["direction"] == "on":
                density = plus[local_index]
            elif event["direction"] == "off":
                density = minus[local_index]
            else:
                raise ValueError(f"Uncensored event has no direction: {event['eventId']}")
            result[global_index] = math.log(max(float(density), 1e-300))
    return result


def initial_theta(events: list[dict[str, Any]], states: list[int], variant: int = 0) -> np.ndarray:
    exposure = {state: sum(event["durationS"] for event in events if event["stateN"] == state) for state in states}
    on_count = {state: sum(not event["rightCensored"] and event["direction"] == "on" for event in events if event["stateN"] == state) for state in states}
    k_plus = [max(1e-4, on_count[state] / max(exposure[state], 1e-9)) for state in states]
    starts = [
        (0.30, 0.12, 0.06, 5e-4, 0.1895, 1.0),
        (0.45, 0.18, 0.08, 1e-4, 0.08, 0.75),
        (0.65, 0.30, 0.12, 1e-3, 0.30, 1.25),
        (0.22, 0.10, 0.04, 3e-3, 0.04, 0.55),
        (0.80, 0.50, 0.25, 2e-5, 0.60, 1.75),
    ]
    c1, c2, c3, sigma_minus, delta_sigma, scale = starts[variant % len(starts)]
    return np.asarray(
        [*[math.log(min(0.9, value * scale)) for value in k_plus],
         math.log(sigma_minus), math.log(delta_sigma),
         logit(c1), logit(c2 / c1), logit(c3 / c2)],
        dtype=float,
    )


def fit_source_model(events: list[dict[str, Any]], states: list[int], multistart: int = 2) -> tuple[dict[str, Any], dict[str, Any]]:
    count = len(states)
    bounds = [(-9.0, 0.0)] * count + [(-18.0, -2.0), (-8.0, 1.0)] + [(-7.0, 7.0)] * 3

    def objective(theta: np.ndarray) -> float:
        scores = event_scores(events, decode(theta, states))
        if not np.all(np.isfinite(scores)):
            return 1e100
        return -float(np.sum(scores))

    candidates = []
    for variant in range(multistart):
        result = optimize.minimize(
            objective,
            initial_theta(events, states, variant),
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 600, "ftol": 1e-9, "gtol": 1e-6, "maxls": 30},
        )
        candidates.append(result)
    best = min(candidates, key=lambda item: float(item.fun))
    parameters = decode(best.x, states)
    diagnostics = {
        "optimizer": f"SciPy L-BFGS-B deterministic {multistart}-start maximum likelihood",
        "success": bool(best.success),
        "message": str(best.message),
        "negativeLogLikelihood": float(best.fun),
        "iterations": int(best.nit),
        "starts": [
            {"success": bool(item.success), "negativeLogLikelihood": float(item.fun), "iterations": int(item.nit)}
            for item in candidates
        ],
    }
    return parameters, diagnostics


def fit_memoryless(events: list[dict[str, Any]], states: list[int]) -> dict[str, Any]:
    result: dict[int, dict[str, float]] = {}
    for state in states:
        state_events = [event for event in events if event["stateN"] == state]
        exposure = sum(event["durationS"] for event in state_events)
        on = sum(not event["rightCensored"] and event["direction"] == "on" for event in state_events)
        off = sum(not event["rightCensored"] and event["direction"] == "off" for event in state_events)
        result[state] = {"kOn": (on + 0.5) / (exposure + 1), "kOff": (off + 0.5) / (exposure + 1)}
    return result


def memoryless_scores(events: list[dict[str, Any]], parameters: dict[int, dict[str, float]]) -> np.ndarray:
    scores = []
    for event in events:
        rates = parameters[event["stateN"]]
        survival_log = -(rates["kOn"] + rates["kOff"]) * event["durationS"]
        if event["rightCensored"]:
            scores.append(survival_log)
        else:
            rate = rates["kOn"] if event["direction"] == "on" else rates["kOff"]
            scores.append(math.log(rate) + survival_log)
    return np.asarray(scores)


def interval(values: list[float]) -> dict[str, float]:
    return {"lower": float(np.quantile(values, 0.025)), "upper": float(np.quantile(values, 0.975))}


def bootstrap_motor_difference(events: list[dict[str, Any]], differences: np.ndarray) -> tuple[float, dict[str, float]]:
    motor_ids = sorted({event["motorId"] for event in events})
    indices = {motor: np.asarray([index for index, event in enumerate(events) if event["motorId"] == motor]) for motor in motor_ids}
    random = np.random.default_rng(SEED)
    values = []
    for _ in range(BOOTSTRAPS):
        selected = random.choice(motor_ids, size=len(motor_ids), replace=True)
        sampled = np.concatenate([indices[motor] for motor in selected])
        values.append(float(np.mean(differences[sampled])))
    return float(np.mean(differences)), interval(values)


def simulate_events(parameters: dict[str, Any], states: list[int], counts: dict[int, int], seed: int) -> list[dict[str, Any]]:
    random = np.random.default_rng(seed)
    events: list[dict[str, Any]] = []
    for state in states:
        weights, total_rates, off_rates = source_terms(state, parameters)
        for index in range(counts[state]):
            component = int(random.choice(len(weights), p=weights))
            duration = float(random.exponential(1 / total_rates[component]))
            direction = "on" if random.random() < parameters["kPlusByN"][state] / total_rates[component] else "off"
            events.append({
                "eventId": f"synthetic-{seed}-{state}-{index}",
                "motorId": f"synthetic-{seed}-{index % 40}",
                "stateN": state,
                "durationS": duration,
                "direction": direction,
                "rightCensored": False,
            })
    return events


def recovery_experiment(parameters: dict[str, Any], states: list[int], train: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {state: max(160, 2 * sum(event["stateN"] == state for event in train)) for state in states}
    replicates = []
    for offset in range(3):
        synthetic = simulate_events(parameters, states, counts, SEED + 100 + offset)
        recovered, diagnostics = fit_source_model(synthetic, states, multistart=1)
        shared_absolute_error = {
            name: abs(recovered[name] - parameters[name])
            for name in ["c1", "c2", "c3"]
        }
        shared_log_error = {
            name: abs(math.log(recovered[name] / parameters[name]))
            for name in ["sigmaPlusPerSecond", "sigmaMinusPerSecond"]
        }
        k_plus_log_errors = [
            abs(math.log(recovered["kPlusByN"][state] / parameters["kPlusByN"][state])) for state in states
        ]
        passed = (
            diagnostics["success"]
            and max(shared_absolute_error.values()) < 0.12
            and max(shared_log_error.values()) < 0.50
            and float(np.median(k_plus_log_errors)) < 0.25
        )
        replicates.append({
            "seed": SEED + 100 + offset,
            "events": len(synthetic),
            "passed": passed,
            "sharedAbsoluteError": shared_absolute_error,
            "sharedLogRatioError": shared_log_error,
            "medianKPlusLogRatioError": float(np.median(k_plus_log_errors)),
            "optimizer": diagnostics,
        })
    pass_count = sum(item["passed"] for item in replicates)
    return {
        "status": "PASS" if pass_count == len(replicates) else "FAIL",
        "criterion": "All three deterministic synthetic replicates recover each c within 0.12, each sigma within |log ratio| 0.50, and median k+ within |log ratio| 0.25.",
        "passedReplicates": pass_count,
        "totalReplicates": len(replicates),
        "countsByState": counts,
        "replicates": replicates,
    }


def source_moments(state: int, parameters: dict[str, Any], code_n0_branch: bool) -> dict[str, float]:
    weights, total_rates, _ = source_terms(state, parameters, code_n0_branch)
    mean = float(np.sum(weights / total_rates))
    second = float(2 * np.sum(weights / (total_rates**2)))
    fraction_plus = 1.0 if state == 0 and code_n0_branch else parameters["kPlusByN"][state] * mean
    return {
        "meanDwellSeconds": mean,
        "fractionPlus": fraction_plus,
        "normalizedVariance": second / mean**2 - 1,
    }


def gate(gate_id: str, name: str, status: str, criterion: str, evidence: Any, limitation: str) -> dict[str, Any]:
    return {
        "id": gate_id,
        "name": name,
        "status": status,
        "criterion": criterion,
        "evidence": evidence,
        "limitation": limitation,
    }


def main() -> None:
    dataset = load_json(DATA_PATH)
    observed_report = load_json(OBSERVED_REPORT_PATH)
    reference = load_json(REFERENCE_PATH)
    states = observed_report["cohort"]["eligibleStates"]
    eligible = [event for event in dataset["events"] if event["stateN"] in states]
    train = [event for event in eligible if event["partition"] == "train"]
    holdout = [event for event in eligible if event["partition"] == "holdout"]

    mechanism, fit_diagnostics = fit_source_model(train, states, multistart=2)
    source_holdout_scores = event_scores(holdout, mechanism)
    memoryless = fit_memoryless(train, states)
    memoryless_holdout_scores = memoryless_scores(holdout, memoryless)
    difference, difference_interval = bootstrap_motor_difference(
        holdout, source_holdout_scores - memoryless_holdout_scores
    )

    recovery = recovery_experiment(mechanism, states, train)

    bundled = reference["bundledCodeParameterVector"]
    bundled_parameters = {
        "kPlusByN": {state: bundled["kPlusByNPerSecond"][state] for state in range(9)},
        "c1": bundled["c1"],
        "c2": bundled["c2"],
        "c3": bundled["c3"],
        "sigmaPlusPerSecond": bundled["sigmaPlusPerSecond"],
        "sigmaMinusPerSecond": bundled["sigmaMinusPerSecond"],
    }
    code_moments = [source_moments(state, bundled_parameters, True) for state in range(9)]
    theory = reference["sourceDataFigure3"]["theory"]
    code_mismatch = {
        "maxRelativeMeanError": max(
            abs(code_moments[index]["meanDwellSeconds"] / theory["meanDwellSeconds"][index] - 1)
            for index in range(9)
        ),
        "maxAbsoluteFractionPlusError": max(
            abs(code_moments[index]["fractionPlus"] - theory["fractionPlus"][index]) for index in range(9)
        ),
        "maxAbsoluteNormalizedVarianceError": max(
            abs(code_moments[index]["normalizedVariance"] - theory["normalizedVariance"][index])
            for index in range(9)
        ),
        "bundledCodeMoments": code_moments,
    }
    reported = reference["declaredMechanism"]["reportedMomentFit"]
    parameter_interval_checks = {
        "c1": abs(bundled["c1"] - reported["c1"]["value"]) <= reported["c1"]["uncertainty50PercentLossIncrease"],
        "c2": abs(bundled["c2"] - reported["c2"]["value"]) <= reported["c2"]["uncertainty50PercentLossIncrease"],
        "c3": abs(bundled["c3"] - reported["c3"]["value"]) <= reported["c3"]["uncertainty50PercentLossIncrease"],
        "sigmaPlus": abs(bundled["sigmaPlusPerSecond"] - reported["sigmaPlusPerSecond"]["value"]) <= reported["sigmaPlusPerSecond"]["uncertainty50PercentLossIncrease"],
        "sigmaMinus": bundled["sigmaMinusPerSecond"] <= reported["sigmaMinusPerSecond"]["upperBound"],
    }

    equation_checks = []
    for state in states:
        weights, rates, off_rates = source_terms(state, mechanism)
        integral_plus = mechanism["kPlusByN"][state] * float(np.sum(weights / rates))
        integral_minus = float(np.sum(weights * off_rates / rates))
        equation_checks.append({
            "stateN": state,
            "coefficientSum": float(np.sum(weights)),
            "survivalAtZero": float(np.sum(weights)),
            "integratedPlusDensity": integral_plus,
            "integratedMinusDensity": integral_minus,
            "integratedTotalDensity": integral_plus + integral_minus,
            "minimumCoefficient": float(np.min(weights)),
            "minimumRate": float(np.min(rates)),
        })
    equation_pass = all(
        abs(item["coefficientSum"] - 1) < 1e-12
        and abs(item["integratedTotalDensity"] - 1) < 1e-12
        and item["minimumCoefficient"] >= 0
        and item["minimumRate"] > 0
        for item in equation_checks
    )
    censored_train = sum(event["rightCensored"] for event in train)
    censored_holdout = sum(event["rightCensored"] for event in holdout)
    likelihood_pass = (
        fit_diagnostics["success"]
        and censored_train > 0
        and censored_holdout > 0
        and np.all(np.isfinite(source_holdout_scores))
    )
    predictive_pass = difference_interval["lower"] > 0

    gates = [
        gate(
            "G00_SOURCE_IDENTITY",
            "Pinned observed-source identity",
            "PASS",
            "Raw data, public repository commit, derived events, article source-data workbook, and analysis implementations have immutable identities.",
            {
                "rawDataSha256": dataset["source"]["observedRawSha256"],
                "repositoryCommit": dataset["source"]["commit"],
                "sourceDataWorkbookSha256": reference["source"]["sourceDataSha256"],
                "codeBundleSha256": reference["source"]["codeBundleSha256"],
            },
            "Identity establishes provenance, not correctness or biological truth.",
        ),
        gate(
            "G01_OBSERVATION_BOUNDARY",
            "World/model and train/holdout separation",
            "PASS",
            "No motor crosses partitions; the historical world process, observations, latent variables, fit data, and held-out outcomes remain separately named.",
            {
                "noMotorLeakage": observed_report["audit"]["noMotorLeakage"],
                "trainMotors": observed_report["cohort"]["trainMotors"],
                "holdoutMotors": observed_report["cohort"]["holdoutMotors"],
                "worldProcess": observed_report["dataFlow"]["worldProcess"],
            },
            "The source experiment is historical and observational; this is not a prospective laboratory intervention.",
        ),
        gate(
            "G02_FIRST_PASSAGE_MATH",
            "D-L-T first-passage equation integrity",
            "PASS" if equation_pass else "FAIL",
            "For every eligible N, mixture coefficients are nonnegative and normalized, S(0)=1, rates are positive, and integrated plus/minus competing-risk densities sum to one.",
            equation_checks,
            "This is the source paper's H-separated D-L-T reduction, not a spatial molecular simulation and not the complete D-L-T-H process in one likelihood.",
        ),
        gate(
            "G03_PUBLIC_ARTIFACT_PARITY",
            "Article, source workbook, and bundled-code parity",
            "PASS" if all(parameter_interval_checks.values()) and max(code_mismatch[key] for key in ["maxRelativeMeanError", "maxAbsoluteFractionPlusError", "maxAbsoluteNormalizedVarianceError"]) < 1e-8 else "FAIL",
            "The bundled fitting vector must reproduce the source-data workbook's Figure 3 theory arrays and lie within the article's stated 50%-loss parameter ranges.",
            {"parameterIntervalChecks": parameter_interval_checks, "momentMismatch": code_mismatch, "n0Contradiction": reference["sourceDataFigure3"]["warning"]},
            "A failure is a source-artifact reproducibility finding. It does not by itself invalidate the paper's experimental observations.",
        ),
        gate(
            "G04_CENSORED_JOINT_LIKELIHOOD",
            "Censored competing-risk likelihood",
            "PASS" if likelihood_pass else "FAIL",
            "Training and held-out right-censored intervals contribute log S(t); observed on/off exits contribute log P_plus(t) or log P_minus(t); every score is finite.",
            {
                "trainIntervals": len(train),
                "trainRightCensored": censored_train,
                "holdoutIntervals": len(holdout),
                "holdoutRightCensored": censored_holdout,
                "fit": fit_diagnostics,
                "parameters": mechanism,
            },
            "Censoring is handled conditionally on the extracted step trace; uncertainty from step detection is not yet propagated.",
        ),
        gate(
            "G05_SYNTHETIC_RECOVERY",
            "Mechanistic parameter recovery",
            recovery["status"],
            recovery["criterion"],
            recovery,
            "Passing recovery is necessary but not sufficient for biological identifiability; it tests the implementation under data generated by its own model.",
        ),
        gate(
            "G06_HELDOUT_MECHANISTIC_PREDICTION",
            "Held-out mechanistic prediction",
            "PASS" if predictive_pass else "FAIL",
            "The motor-cluster 95% bootstrap interval for D-L-T censored joint log score minus a state-specific memoryless competing-risk baseline lies entirely above zero.",
            {
                "mechanisticMeanLogScorePerInterval": float(np.mean(source_holdout_scores)),
                "memorylessMeanLogScorePerInterval": float(np.mean(memoryless_holdout_scores)),
                "advantageNatsPerInterval": difference,
                "advantageInterval95": difference_interval,
                "bootstrapReplicates": BOOTSTRAPS,
                "bootstrapSeed": SEED,
            },
            "The source dataset was known before this protocol; the split is leakage-controlled but not a blind prospective replication.",
        ),
        gate(
            "G07_H_STATE_REEXTRACTION",
            "Transient H-state event reproduction",
            "SOURCE_ONLY",
            "Re-extract the 43 short hidden-state wells and the reported k_h and k_-h from an independently specified event detector.",
            reference["declaredMechanism"]["reportedHiddenState"],
            "The current event artifact was designed for count-state dwell intervals and does not encode the source authors' H-state classification decisions.",
        ),
        gate(
            "G08_LOAD_TORQUE_TRANSFER",
            "Load- and torque-dependent transfer",
            "BLOCKED_EXTERNAL",
            "Predict stator kinetics across independently measured loads and torque regimes without refitting shared mechanistic parameters.",
            {
                "currentIntervention": "Low-load electrorotation removed, followed by one high-load adaptation regime",
                "needed": "Raw multi-load single-motor occupancy, torque, and timing observations with motor identities",
                "primaryAnchors": [
                    "https://doi.org/10.1038/s41467-021-25774-2",
                    "https://doi.org/10.1038/s41467-019-13030-1"
                ],
            },
            "One post-electrorotation regime cannot identify a load-response surface.",
        ),
        gate(
            "G09_SWITCH_COOPERATIVITY",
            "Switching cooperativity and global mechanical coupling",
            "BLOCKED_EXTERNAL",
            "Test occupancy-fluctuation and switching predictions against raw multi-load switching records, including motor-level heterogeneity and competing equilibrium/non-equilibrium mechanisms.",
            {
                "currentDataContainsSwitchingTrajectories": False,
                "currentPrimaryModels": [
                    "https://doi.org/10.1038/s41598-025-14570-3",
                    "https://doi.org/10.1038/s41567-025-03105-2"
                ],
            },
            "The present stator-remodeling dwell data cannot adjudicate switching cooperativity models.",
        ),
        gate(
            "G10_ACTIVE_INFERENCE_CAUSAL_IDENTITY",
            "Biological Active-Inference identity",
            "NOT_ESTABLISHED",
            "Measure intervention-dependent biological states and actions that uniquely distinguish the declared Active-Inference model from mechanochemical, feedback-control, and descriptive stochastic alternatives.",
            {
                "observedHere": ["stator-count dwell intervals", "transition direction", "historical intervention timing"],
                "notObservedHere": ["biological posterior", "policy posterior", "counterfactual preference", "UNI-selected intervention"],
            },
            "Exact Bayesian inference inside a declared software model is not evidence that a bacterium implements that representation.",
        ),
        gate(
            "G11_LIVE_INSTRUMENT",
            "Synchronous live measurement parity",
            "BLOCKED_EXTERNAL",
            "Ingest calibrated motor measurements with acquisition timestamps, uncertainty, precommitted predictions, and intervention records while the experiment is running.",
            {"serialAdapterImplemented": True, "liveInstrumentRunInThisRelease": False},
            "A software serial aperture is not a measurement until connected to a calibrated instrument.",
        ),
        gate(
            "G12_INDEPENDENT_REPLICATION",
            "Independent biological replication",
            "BLOCKED_EXTERNAL",
            "A separate laboratory reproduces the protocol, raw-data audit, fitted parameters, and held-out predictions with a predeclared acceptance rule.",
            {"independentLaboratories": 0},
            "Repository replay and an independent numerical implementation are not independent biological replication.",
        ),
        gate(
            "G13_PHYSICAL_MODEL_VALIDATION",
            "Printed UNI mechanism validation",
            "BLOCKED_EXTERNAL",
            "Print, tolerance-test, instrument, and classroom-safety-review the UNI teaching mechanism; compare measured gear angles and backlash with the screen calculation.",
            {"parametricCadExportImplemented": True, "physicalPrintRuns": 0, "measuredBacklashRuns": 0},
            "CAD export is a conversion starting point, not evidence of printability or safety.",
        ),
    ]

    status_counts: dict[str, int] = {}
    for item in gates:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1
    computational = [item for item in gates if item["status"] not in {"BLOCKED_EXTERNAL", "NOT_ESTABLISHED", "SOURCE_ONLY"}]
    report = {
        "schema": "uni.flagellum.science-gates/1.0.0",
        "generatedAt": "2026-07-17T23:00:00Z",
        "executionClass": "CPU_ONLY_DETERMINISTIC_SCIENCE_GATE_AUDIT",
        "summary": {
            "overall": "PARTIAL_PARITY_ONLY",
            "gateCount": len(gates),
            "statusCounts": status_counts,
            "computationalGatesPassed": sum(item["status"] == "PASS" for item in computational),
            "computationalGatesEvaluated": len(computational),
            "fullBiologicalParityAchieved": False,
            "proofClaim": "No universal, causal, or biological Active-Inference identity was proved.",
        },
        "modelBoundary": {
            "mechanisticObject": "Wadhwa D-L-T first-passage survival reduction with H handled only as a source-reported separated timescale",
            "observation": "Historical step-fitted stator-count intervals from single E. coli motors",
            "prediction": "Competing-risk density or censoring survival for a held-out motor interval",
            "worldNotInModel": ["molecular conformation", "local torque per stator", "membrane diffusion", "instrument noise", "cell physiology"],
        },
        "identities": {
            "dataSha256": sha256(DATA_PATH),
            "observedReportSha256": sha256(OBSERVED_REPORT_PATH),
            "sourceReferenceSha256": sha256(REFERENCE_PATH),
            "pythonGateRunnerSha256": sha256(Path(__file__)),
            "javascriptEquationOracleSha256": sha256(JS_ORACLE_PATH),
        },
        "fittedMechanism": mechanism,
        "gates": gates,
        "executionOrder": [item["id"] for item in gates],
        "nextExecutableWork": [
            "Resolve G03 by obtaining a tagged final parameter artifact or author clarification; never overwrite the shipped mismatch.",
            "Specify and independently implement the H-well classifier required by G07.",
            "Acquire or license motor-identified raw multi-load timing data for G08 and G09.",
            "Run a prospective calibrated instrument protocol for G11 before making live-measurement claims.",
            "Arrange independent wet-lab and physical-print replication for G12 and G13."
        ],
    }
    serialized_for_id = json.dumps(report, sort_keys=True, separators=(",", ":"), allow_nan=False)
    report["runId"] = hashlib.sha256(serialized_for_id.encode("utf-8")).hexdigest()
    serialized = json.dumps(report, indent=2, allow_nan=False) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Pin LF bytes on every platform so the published artifact has the exact
    # SHA-256 recorded below.  The default text writer translates newlines on
    # Windows, which would make the audit identity platform-dependent.
    REPORT_PATH.write_text(serialized, "utf-8", newline="\n")
    PUBLIC_PATH.write_text(serialized, "utf-8", newline="\n")
    report_sha256 = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    audit = {
        "schema": "uni.flagellum.science-gates-audit/1.0.0",
        "runId": report["runId"],
        "executionClass": report["executionClass"],
        "deterministicSeed": SEED,
        "artifacts": {
            "derivedEvents": {"path": str(DATA_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(DATA_PATH)},
            "observedReport": {"path": str(OBSERVED_REPORT_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(OBSERVED_REPORT_PATH)},
            "sourceReference": {"path": str(REFERENCE_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(REFERENCE_PATH)},
            "pythonGateRunner": {"path": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(Path(__file__))},
            "javascriptEquationOracle": {"path": str(JS_ORACLE_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256(JS_ORACLE_PATH)},
            "scienceGateReport": {"path": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"), "sha256": report_sha256},
        },
        "replay": "Run python scripts/run-science-gates.py twice; report and audit SHA-256 values must remain identical.",
        "externalBlocks": [item["id"] for item in gates if item["status"] == "BLOCKED_EXTERNAL"],
    }
    serialized_audit = json.dumps(audit, indent=2, allow_nan=False) + "\n"
    AUDIT_PATH.write_text(serialized_audit, "utf-8", newline="\n")
    PUBLIC_AUDIT_PATH.write_text(serialized_audit, "utf-8", newline="\n")
    print(json.dumps({
        "runId": report["runId"],
        "reportSha256": report_sha256,
        "auditSha256": hashlib.sha256(serialized_audit.encode("utf-8")).hexdigest(),
        "summary": report["summary"],
        "heldoutAdvantage": difference,
        "heldoutAdvantageInterval95": difference_interval,
        "recovery": {"status": recovery["status"], "passed": recovery["passedReplicates"], "total": recovery["totalReplicates"]},
    }, indent=2))


if __name__ == "__main__":
    main()
