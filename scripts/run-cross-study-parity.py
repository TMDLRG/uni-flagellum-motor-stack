#!/usr/bin/env python3
"""Execute preregistered cross-study bacterial-motor parity gates on CPU."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy import linalg, optimize, stats


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "experiments" / "data" / "cross-study-motor-evidence.json"
PROTOCOL_PATH = ROOT / "experiments" / "cross-study-preregistration.v1.json"
STRUCTURE_PATH = ROOT / "experiments" / "structural-state-map.v1.json"
PREVIOUS_PATH = ROOT / "experiments" / "results" / "science-gates-report.json"
REPORT_PATH = ROOT / "experiments" / "results" / "cross-study-parity-report.json"
PUBLIC_REPORT_PATH = ROOT / "public" / "cross-study-parity-report.json"
AUDIT_PATH = ROOT / "experiments" / "results" / "cross-study-parity-audit.json"
PUBLIC_AUDIT_PATH = ROOT / "public" / "cross-study-parity-audit.json"
SEED = 20260717
BOOTSTRAPS = 5000


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text("utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def gate(gate_id: str, status: str, title: str, criterion: str, evidence: dict[str, Any], limitation: str) -> dict[str, Any]:
    return {"id": gate_id, "status": status, "title": title, "criterion": criterion, "evidence": evidence, "limitation": limitation}


def weighted_fit(design: np.ndarray, values: np.ndarray, standard_errors: np.ndarray) -> np.ndarray:
    weights = 1 / np.maximum(standard_errors, 1e-9)
    return np.linalg.lstsq(design * weights[:, None], values * weights, rcond=None)[0]


def rotation_gate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [row for row in rows if row["bindingRatePerSecond"] is not None and row["bindingRateSe"] is not None]
    speed = np.asarray([row["meanSpeedHz"] for row in usable], dtype=float)
    rate = np.asarray([row["bindingRatePerSecond"] for row in usable], dtype=float)
    se = np.asarray([row["bindingRateSe"] for row in usable], dtype=float)
    design = np.column_stack([np.ones(len(speed)), np.maximum(speed, 0), np.maximum(-speed, 0)])
    parameters = weighted_fit(design, rate, se)
    symmetric = np.column_stack([np.ones(len(speed)), np.abs(speed)])
    symmetric_parameters = weighted_fit(symmetric, rate, se)

    prediction = []
    constant_prediction = []
    for heldout in range(len(speed)):
        mask = np.arange(len(speed)) != heldout
        beta = weighted_fit(design[mask], rate[mask], se[mask])
        prediction.append(float(design[heldout] @ beta))
        weights = 1 / np.maximum(se[mask], 1e-9) ** 2
        constant_prediction.append(float(np.average(rate[mask], weights=weights)))
    rmse = float(np.sqrt(np.mean((np.asarray(prediction) - rate) ** 2)))
    constant_rmse = float(np.sqrt(np.mean((np.asarray(constant_prediction) - rate) ** 2)))
    improvement = 1 - rmse / constant_rmse
    fitted = design @ parameters
    symmetric_fitted = symmetric @ symmetric_parameters

    def aic(residuals: np.ndarray, parameters_count: int) -> float:
        n = len(residuals)
        sse = max(float(residuals @ residuals), 1e-300)
        return n * math.log(sse / n) + 2 * parameters_count

    return {
        "nBins": len(speed),
        "parameters": {"stallInterceptPerSecond": float(parameters[0]), "positiveSpeedSlopePerHz": float(parameters[1]), "negativeSpeedMagnitudeSlopePerHz": float(parameters[2])},
        "leaveOneBinOutRmse": rmse,
        "constantLeaveOneBinOutRmse": constant_rmse,
        "relativeRmseImprovement": improvement,
        "aic": {"directional": aic(fitted - rate, 3), "symmetric": aic(symmetric_fitted - rate, 2)},
        "pass": bool(improvement >= 0.20 and parameters[1] > 0 and parameters[2] > 0 and parameters[0] >= 0),
    }


def mean_difference_test(group_a: list[float], group_b: list[float]) -> dict[str, Any]:
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    welch = stats.ttest_ind(b, a, equal_var=False)
    difference = float(np.mean(b) - np.mean(a))
    pooled = math.sqrt(((len(a) - 1) * np.var(a, ddof=1) + (len(b) - 1) * np.var(b, ddof=1)) / (len(a) + len(b) - 2))
    cohen_d = difference / pooled
    correction = 1 - 3 / (4 * (len(a) + len(b)) - 9)
    random = np.random.default_rng(SEED)
    bootstrap = np.empty(BOOTSTRAPS)
    for index in range(BOOTSTRAPS):
        bootstrap[index] = np.mean(random.choice(b, len(b), replace=True)) - np.mean(random.choice(a, len(a), replace=True))
    interval = np.quantile(bootstrap, [0.025, 0.975])
    return {
        "nA": len(a), "nB": len(b), "meanA": float(np.mean(a)), "meanB": float(np.mean(b)),
        "meanDifference": difference, "hedgesG": float(correction * cohen_d), "welchT": float(welch.statistic), "welchP": float(welch.pvalue),
        "bootstrap95": {"lower": float(interval[0]), "upper": float(interval[1])},
    }


def torque_response(rows: list[dict[str, Any]]) -> dict[str, Any]:
    torque = np.asarray([row["torquePnNm"] for row in rows], dtype=float)
    cw_ccw = np.asarray([row["kCwToCcwPerSecond"] for row in rows], dtype=float)
    ccw_cw = np.asarray([row["kCcwToCwPerSecond"] for row in rows], dtype=float)
    bias = np.asarray([row["cwBias"] for row in rows], dtype=float)
    rho_a = stats.spearmanr(torque, cw_ccw)
    rho_b = stats.spearmanr(torque, ccw_cw)
    cv = float(np.std(bias, ddof=1) / np.mean(bias))
    return {
        "nConditions": len(rows),
        "cwToCcw": {"spearmanRho": float(rho_a.statistic), "p": float(rho_a.pvalue)},
        "ccwToCw": {"spearmanRho": float(rho_b.statistic), "p": float(rho_b.pvalue)},
        "cwBias": {"mean": float(np.mean(bias)), "sd": float(np.std(bias, ddof=1)), "coefficientOfVariation": cv},
        "pass": bool(rho_a.statistic >= 0.8 and rho_b.statistic >= 0.8 and cv < 0.15),
    }


def lattice_features(length: int = 13) -> tuple[np.ndarray, np.ndarray]:
    count = np.empty(2**length, dtype=float)
    adjacent = np.empty(2**length, dtype=float)
    for encoded in range(2**length):
        state = np.asarray([(encoded >> index) & 1 for index in range(length)], dtype=float)
        count[encoded] = np.sum(state)
        adjacent[encoded] = np.sum(state * np.roll(state, -1))
    return count, adjacent


def lattice_distribution(j_value: float, mu: float, count: np.ndarray, adjacent: np.ndarray, length: int = 13) -> np.ndarray:
    log_weight = j_value * adjacent + mu * count
    log_weight -= np.max(log_weight)
    weight = np.exp(log_weight)
    partition = np.sum(weight)
    return np.asarray([np.sum(weight[count == occupied]) / partition for occupied in range(length + 1)])


def lattice_gate(probabilities: dict[str, list[float]], moment_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels = ["300nm", "500nm", "1300nm"]
    observed = [np.asarray(probabilities[label], dtype=float) for label in labels]
    observed = [values / np.sum(values) for values in observed]
    count, adjacent = lattice_features(13)

    def residual(theta: np.ndarray, fixed_j: float | None = None) -> np.ndarray:
        j_value = float(theta[0]) if fixed_j is None else fixed_j
        mus = theta[1:] if fixed_j is None else theta
        return np.concatenate([lattice_distribution(j_value, float(mu), count, adjacent) - values for mu, values in zip(mus, observed, strict=True)])

    fitted = optimize.least_squares(residual, np.asarray([1.0, -2.0, -1.0, 0.0]), bounds=([0, -10, -10, -10], [4, 10, 10, 10]), xtol=1e-13, ftol=1e-13, gtol=1e-13)
    baseline = optimize.least_squares(lambda mu: residual(mu, fixed_j=0), np.asarray([-1.0, 0.0, 1.0]), bounds=(-10, 10), xtol=1e-13, ftol=1e-13, gtol=1e-13)
    fit_residual = residual(fitted.x)
    base_residual = residual(baseline.x, fixed_j=0)
    n = len(fit_residual)
    sse = float(fit_residual @ fit_residual)
    baseline_sse = float(base_residual @ base_residual)
    aic = n * math.log(max(sse / n, 1e-300)) + 2 * 4
    baseline_aic = n * math.log(max(baseline_sse / n, 1e-300)) + 2 * 3

    profile = []
    for j_value in np.linspace(0, 3, 31):
        candidate = optimize.least_squares(lambda mu: residual(mu, fixed_j=float(j_value)), fitted.x[1:], bounds=(-10, 10))
        candidate_residual = residual(candidate.x, fixed_j=float(j_value))
        profile.append({"J": float(j_value), "sse": float(candidate_residual @ candidate_residual)})

    def occupancy_moments(j_value: float, mu: float) -> tuple[float, float]:
        log_weight = j_value * adjacent + mu * count
        log_weight -= np.max(log_weight)
        weight = np.exp(log_weight)
        weight /= np.sum(weight)
        mean_n = float(weight @ count)
        variance_n = float(weight @ (count**2) - mean_n**2)
        return mean_n / 13, math.sqrt(max(variance_n, 0)) / 13

    def fit_moments(weighted: bool) -> dict[str, Any]:
        def objective(j_value: float) -> float:
            total = 0.0
            for row in moment_rows:
                target_mean = row["meanRelativeOccupancy"]
                mu = optimize.brentq(lambda value: occupancy_moments(j_value, value)[0] - target_mean, -20, 20)
                predicted_sd = occupancy_moments(j_value, mu)[1]
                scale = row["sdSe"] if weighted else 1.0
                total += ((predicted_sd - row["sdRelativeOccupancy"]) / scale) ** 2
            return total

        result = optimize.minimize_scalar(objective, bounds=(-2, 5), method="bounded", options={"xatol": 1e-10})
        predictions = []
        for row in moment_rows:
            mu = optimize.brentq(lambda value: occupancy_moments(float(result.x), value)[0] - row["meanRelativeOccupancy"], -20, 20)
            predictions.append({"condition": row["condition"], "mu": float(mu), "observedSd": row["sdRelativeOccupancy"], "predictedSd": occupancy_moments(float(result.x), mu)[1]})
        return {"J": float(result.x), "objective": float(result.fun), "weightedByReportedSdSe": weighted, "predictions": predictions}

    moment_unweighted = fit_moments(False)
    moment_weighted = fit_moments(True)
    return {
        "observations": n,
        "J": float(fitted.x[0]),
        "muByBead": {label: float(value) for label, value in zip(labels, fitted.x[1:], strict=True)},
        "probabilityRmse": float(np.sqrt(sse / n)),
        "sse": sse,
        "baselineJ0Sse": baseline_sse,
        "aic": aic,
        "baselineJ0Aic": baseline_aic,
        "deltaAicInFavorOfCooperativity": baseline_aic - aic,
        "profile": profile,
        "momentFits": {"unweighted": moment_unweighted, "reportedSeWeighted": moment_weighted},
        "crossStatisticJDisagreement": {"fullDistributionJ": float(fitted.x[0]), "momentJ": moment_unweighted["J"], "absoluteDifference": abs(float(fitted.x[0]) - moment_unweighted["J"])},
        "pass": bool(0.5 < fitted.x[0] < 2.0 and baseline_aic - aic >= 10 and math.sqrt(sse / n) < 0.05),
    }


def gmc_generator(n_ring: int, stators: int, gamma: float, beta: float, j_neighbor: float, free_energy: float, k0: float) -> np.ndarray:
    dtheta = 2 * math.pi / (n_ring * stators)
    unengaged_max = n_ring - stators
    state_count = (unengaged_max + 1) * (stators + 1)
    matrix = np.zeros((state_count, state_count), dtype=float)
    stoichiometry = np.asarray([[1, -1, 0, 0, -1, 1], [0, 0, 1, -1, 1, -1]], dtype=int)

    def index(nu: int, ne: int) -> int:
        return nu + (unengaged_max + 1) * ne

    def rates(nu: int, ne: int) -> np.ndarray:
        omega = (2 * ne - stators) / stators
        if beta > 0:
            omega = (stators / beta) / (1 + stators / beta) * omega
        tau_plus = 1 - omega
        tau_minus = 1 + omega
        k_minus = k0 * math.exp(free_energy / 2 + 0.5 * j_neighbor * (2 * (ne + nu) / (n_ring - 1) - 1))
        k_plus = k0 * math.exp(-free_energy / 2 - 0.5 * j_neighbor * (2 * (ne + nu - 1) / (n_ring - 1) - 1))
        rotation_rate = abs(omega) / dtheta
        return np.asarray([
            (unengaged_max - nu) * k_minus,
            nu * k_plus,
            (stators - ne) * k_minus * math.exp(gamma * tau_minus),
            ne * k_plus * math.exp(gamma * tau_plus),
            rotation_rate * (1 - ne / stators) * nu / unengaged_max,
            rotation_rate * ne / stators * (1 - nu / unengaged_max),
        ])

    for ne in range(stators + 1):
        for nu in range(unengaged_max + 1):
            source = index(nu, ne)
            source_rates = rates(nu, ne)
            matrix[source, source] = -float(np.sum(source_rates))
            for reaction in range(6):
                target_nu = nu + int(stoichiometry[0, reaction])
                target_ne = ne + int(stoichiometry[1, reaction])
                if 0 <= target_nu <= unengaged_max and 0 <= target_ne <= stators:
                    matrix[index(target_nu, target_ne), source] += source_rates[reaction]
    return matrix


def gmc_reproduction(source_marginal: list[float]) -> dict[str, Any]:
    matrix = gmc_generator(30, 6, 3.5, 0, 0, 0, 1)
    eigenvalues, eigenvectors = linalg.eig(matrix)
    stationary_index = int(np.argmin(np.abs(eigenvalues)))
    stationary = np.real(eigenvectors[:, stationary_index])
    if np.sum(stationary) < 0:
        stationary = -stationary
    stationary = np.maximum(stationary, 0)
    stationary /= np.sum(stationary)
    stationary_grid = stationary.reshape((25, 7), order="F")
    engaged = np.sum(stationary_grid, axis=0)
    source = np.asarray(source_marginal, dtype=float)
    off_diagonal = matrix.copy()
    np.fill_diagonal(off_diagonal, 0)
    column_error = float(np.max(np.abs(np.sum(matrix, axis=0))))
    residual = float(np.max(np.abs(matrix @ stationary)))
    l1 = float(np.sum(np.abs(engaged - source)))
    return {
        "states": len(stationary),
        "minimumOffDiagonalRate": float(np.min(off_diagonal)),
        "maximumColumnSumError": column_error,
        "stationaryResidualInfinityNorm": residual,
        "engagedMarginal": [float(value) for value in engaged],
        "sourceEngagedMarginal": [float(value) for value in source],
        "engagedMarginalL1": l1,
        "pass": bool(np.min(off_diagonal) >= -1e-14 and column_error < 1e-10 and residual < 1e-9 and l1 < 0.03),
    }


def switching_direction(observed_speed: np.ndarray, observed_rate: np.ndarray, lower: np.ndarray, upper: np.ndarray, model_speed: np.ndarray, model_rate: np.ndarray) -> dict[str, Any]:
    order = np.argsort(model_speed)
    model_speed = model_speed[order]
    model_rate = model_rate[order]
    supported = (observed_speed >= np.min(model_speed)) & (observed_speed <= np.max(model_speed))
    predicted = np.interp(observed_speed[supported], model_speed, model_rate)
    observed = observed_rate[supported]
    error = predicted - observed
    scale = np.where(error >= 0, upper[supported], lower[supported])
    scale = np.maximum(scale, 1e-12)
    return {
        "supportedPoints": int(np.sum(supported)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "meanAbsoluteStandardizedResidual": float(np.mean(np.abs(error) / scale)),
        "fractionWithinAsymmetricErrorBar": float(np.mean(np.abs(error) <= scale)),
    }


def gmc_switching(study: dict[str, Any]) -> dict[str, Any]:
    prediction = study["sourceSwitchingPrediction"]
    observations = study["yuan2009DigitizedSwitching"]
    model_speed = np.asarray(prediction["speedHz"], dtype=float)
    cw = switching_direction(
        np.asarray([row["speedCwHz"] for row in observations]), np.asarray([row["kCwToCcw"] for row in observations]),
        np.asarray([row["kCwToCcwLower"] for row in observations]), np.asarray([row["kCwToCcwUpper"] for row in observations]),
        model_speed, np.asarray(prediction["kCwToCcw"]),
    )
    ccw = switching_direction(
        np.asarray([row["speedCcwHz"] for row in observations]), np.asarray([row["kCcwToCw"] for row in observations]),
        np.asarray([row["kCcwToCwLower"] for row in observations]), np.asarray([row["kCcwToCwUpper"] for row in observations]),
        model_speed, np.asarray(prediction["kCcwToCw"]),
    )
    passed = all(item["fractionWithinAsymmetricErrorBar"] >= 0.60 and item["meanAbsoluteStandardizedResidual"] < 1 for item in [cw, ccw])
    return {"cwToCcw": cw, "ccwToCw": ccw, "pass": passed}


def propulsion_gate(study: dict[str, Any]) -> dict[str, Any]:
    rotation = study["rotationRates"]
    flagella = np.asarray([row["flagellaCount"] for row in rotation], dtype=float)
    motor_speed = np.asarray([row["motorRotationHz"] for row in rotation], dtype=float)
    centered = flagella - np.mean(flagella)
    slope = float(centered @ (motor_speed - np.mean(motor_speed)) / (centered @ centered))
    intercept = float(np.mean(motor_speed) - slope * np.mean(flagella))
    residual = motor_speed - (intercept + slope * flagella)
    slope_se = math.sqrt(float(residual @ residual) / (len(flagella) - 2) / float(centered @ centered))
    critical = float(stats.t.ppf(0.975, len(flagella) - 2))
    slope_interval = [slope - critical * slope_se, slope + critical * slope_se]

    observations = study["experimentalCellSpeeds"]
    observed_n = np.asarray([row["flagellaCount"] for row in observations], dtype=float)
    observed_speed = np.asarray([row["speedUmPerSecond"] for row in observations], dtype=float)
    model = study["rftSourcePredictions"]
    model_n = np.asarray([row["flagellaCount"] for row in model], dtype=float)
    model_speed = np.asarray([row["meanSpeedUmPerSecond"] for row in model], dtype=float)
    predicted = np.interp(observed_n, model_n, model_speed)
    rmse = float(np.sqrt(np.mean((predicted - observed_speed) ** 2)))
    baseline_rmse = float(np.sqrt(np.mean((np.mean(observed_speed) - observed_speed) ** 2)))
    return {
        "motorSpeed": {"n": len(motor_speed), "meanHz": float(np.mean(motor_speed)), "slopeHzPerFlagellum": slope, "slopeSe": slope_se, "slope95": {"lower": slope_interval[0], "upper": slope_interval[1]}},
        "rftCellSpeed": {"n": len(observed_speed), "rmseUmPerSecond": rmse, "constantMeanBaselineRmse": baseline_rmse, "relativeImprovement": 1 - rmse / baseline_rmse},
        "pass": bool(rmse < 2 and rmse < baseline_rmse and slope_interval[0] <= 0 <= slope_interval[1]),
    }


def main() -> None:
    corpus = load(CORPUS_PATH)
    protocol = load(PROTOCOL_PATH)
    structure = load(STRUCTURE_PATH)
    previous = load(PREVIOUS_PATH)
    studies = corpus["studies"]
    criteria = {item["id"]: item["criterion"] for item in protocol["gates"]}

    source_integrity_pass = (
        all(item["verified"] for item in corpus["sourceIntegrity"]["localArtifacts"])
        and corpus["sourceIntegrity"]["itoRawArchive"]["cacheVerification"]["status"] == "PASS"
    )
    gates: list[dict[str, Any]] = []
    gates.append(gate("X01_SOURCE_INTEGRITY", "PASS" if source_integrity_pass else "FAIL", "Immutable source bytes and parsers", criteria["X01_SOURCE_INTEGRITY"], {
        "verifiedLocalArtifacts": sum(item["verified"] for item in corpus["sourceIntegrity"]["localArtifacts"]),
        "declaredLocalArtifacts": len(corpus["sourceIntegrity"]["localArtifacts"]),
        "corpusSha256": sha256(CORPUS_PATH),
        "itoRawArchive": corpus["sourceIntegrity"]["itoRawArchive"],
    }, "The 4.09 GB Ito archive is a separately cached evidence tier whose byte count, MD5, ZIP directory, and every member CRC passed. The hashed 11.9 MB source workbook remains the artifact parsed into the current numerical gates."))

    breadth = corpus["breadth"]
    breadth_pass = len(breadth["directPrimaryArtifactFamilies"]) >= 4 and len(breadth["attributedStudies"]) >= 8 and len(breadth["observationScales"]) >= 4 and breadth["directIndependentMotorCellLowerBound"] >= 400
    gates.append(gate("X02_CORPUS_BREADTH", "PASS" if breadth_pass else "FAIL", "Cross-study breadth without pseudoreplication", criteria["X02_CORPUS_BREADTH"], breadth, "Breadth is not parity. Several older datasets are available only as digitized or aggregate evidence and are labeled accordingly."))

    rotation = rotation_gate(studies["ito2021"]["rotationBindingBins"]["20Hz"])
    rotation["binWidthRobustness"] = {width: rotation_gate(rows) for width, rows in studies["ito2021"]["rotationBindingBins"].items()}
    gates.append(gate("X03_ROTATION_GATED_ASSEMBLY", "PASS" if rotation["pass"] else "FAIL", "Rotation gates stator assembly in both directions", criteria["X03_ROTATION_GATED_ASSEMBLY"], rotation, "This reproduces an aggregate source-workbook relationship. Speed-bin points are not independent motors, and the zero-speed intervention dominates part of the contrast."))

    antani = studies["antani2021"]
    chey = mean_difference_test(antani["cheYFluorescence"]["emptyVector"], antani["cheYFluorescence"]["motAB"])
    flim = mean_difference_test(antani["fliMControl"]["control"], antani["fliMControl"]["deltaMotAB"])
    rotation_control = mean_difference_test(antani["rotationControl"]["rotating"], antani["rotationControl"]["stalled"])
    chey_pass = chey["welchP"] < 0.001 and chey["bootstrap95"]["lower"] > 0
    gates.append(gate("X04_STATOR_CHEY_COUPLING", "PASS" if chey_pass else "FAIL", "Stator presence changes CheY-associated fluorescence", criteria["X04_STATOR_CHEY_COUPLING"], {"primaryCheYContrast": chey, "fliMControl": flim, "rotatingVsStalledControl": rotation_control}, "The assay supports coupling/association; it does not by itself resolve the molecular path or establish causal direction for every downstream variable."))

    torque = torque_response(antani["torqueSwitching"])
    gates.append(gate("X05_TORQUE_SWITCHING_RESPONSE", "PASS" if torque["pass"] else "FAIL", "Torque changes both switch rates while bias stays stable", criteria["X05_TORQUE_SWITCHING_RESPONSE"], torque, "Nine plotted torque conditions are aggregate observations; a shared-cell covariance matrix is not available."))

    lattice = lattice_gate(studies["francoOnate2025"]["probabilityByBead"], studies["francoOnate2025"]["meanAndSdRows"])
    gates.append(gate("X06_FINITE_LATTICE_COOPERATIVITY", "PASS" if lattice["pass"] else "FAIL", "Exact finite-lattice occupancy reproduction", criteria["X06_FINITE_LATTICE_COOPERATIVITY"], lattice, "Aggregate probabilities average time points across motors. The inferred J can absorb unmodeled intercellular heterogeneity and is therefore not a clean molecular interaction energy."))

    gmc = gmc_reproduction(studies["mattingly2026"]["fig2PublishedEngagedMarginal"])
    gates.append(gate("X07_GMC_GENERATOR_REPRODUCTION", "PASS" if gmc["pass"] else "FAIL", "Independent CPU port of the GMC coarse generator", criteria["X07_GMC_GENERATOR_REPRODUCTION"], gmc, "The source marginal comes from the authors' simulation; agreement verifies equations and coarse statistics, not experimental truth."))

    switching = gmc_switching(studies["mattingly2026"])
    gates.append(gate("X08_GMC_SWITCHING_OBSERVATIONS", "PASS" if switching["pass"] else "FAIL", "GMC source predictions against attributed switching observations", criteria["X08_GMC_SWITCHING_OBSERVATIONS"], switching, "This is source-model reproduction against digitized legacy observations, not held-out refitting or independent laboratory validation."))

    propulsion = propulsion_gate(studies["lisevich2025"])
    gates.append(gate("X09_WHOLE_CELL_PROPULSION", "PASS" if propulsion["pass"] else "FAIL", "Motor invariance and RFT whole-cell transfer", criteria["X09_WHOLE_CELL_PROPULSION"], propulsion, "The source workbook contains ten condition/replicate values at three mean flagellar counts; this is not a universal strain- or medium-level propulsion law."))

    gates.append(gate("X10_CROSS_STUDY_PARAMETER_TRANSFER", "NOT_ESTABLISHED", "Independent cross-laboratory parameter transfer", criteria["X10_CROSS_STUDY_PARAMETER_TRANSFER"], {
        "commensurateRawTransferTests": 0,
        "reason": "Ito speed-bin assembly, Wadhwa post-electrorotation dwell events, Nord/Perez load protocols, and Antani switching assays have different interventions and observation operators. No unit-safe shared parameter was frozen on one lab and scored on another raw dataset.",
    }, "Forcing a common coefficient across these assays would create apparent unity by erasing the measurement models."))

    gates.append(gate("X11_STRUCTURAL_CONSISTENCY", "FAIL" if structure["knownConflicts"] else "PASS", "Structural and geometric claim audit", criteria["X11_STRUCTURAL_CONSISTENCY"], {
        "mappedStates": len(structure["mappings"]), "knownConflicts": structure["knownConflicts"], "cadRule": structure["cadRule"],
    }, "The current mathematical model is CAD-ready only as an abstract transparent mechanism. It is not CAD-ready as literal molecular geometry."))

    gates.append(gate("X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY", "NOT_ESTABLISHED", "Biological Active Inference identity", criteria["X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY"], {
        "discriminatingInterventions": 0,
        "competingExplanations": ["non-equilibrium statistical mechanics", "kinetic hidden-state models", "catch-bond remodeling", "speed-rate remodeling", "finite-lattice cooperativity", "resistive-force mechanics"],
    }, "Bayesian or variational representation of data does not prove that the bacterium performs that representation."))

    for gate_id, title, missing in [
        ("X13_LIVE_SIGNAL_CHAIN", "Calibrated live signal-to-prediction chain", "calibrated instrument run with prediction-before-outcome"),
        ("X14_INDEPENDENT_WET_LAB_REPLICATION", "Independent wet-lab replication", "independent laboratory, raw files, calibration, and preregistered replication"),
        ("X15_PRINTED_MODEL_VALIDATION", "Fabricated physical UNI model", "fabricated print, dimensional inspection, sensor calibration, and observed hand-driven run"),
    ]:
        gates.append(gate(gate_id, "BLOCKED_EXTERNAL", title, criteria[gate_id], {"missing": missing, "softwareCannotSubstitute": True}, "This requires new physical evidence or independent human/institutional action and cannot be completed by software alone."))

    full_pass = all(item["status"] == "PASS" for item in gates)
    gates.append(gate("X16_FULL_BIOLOGICAL_PARITY", "PASS" if full_pass else "FAIL", "Full biological parity", criteria["X16_FULL_BIOLOGICAL_PARITY"], {
        "allPriorRequiredGatesPass": full_pass,
        "nonPassGateIds": [item["id"] for item in gates if item["status"] != "PASS"],
    }, "Full parity is a conjunction, not an average score; one missing required domain is sufficient to keep the claim false."))

    protocol_hash = sha256(PROTOCOL_PATH)
    corpus_hash = sha256(CORPUS_PATH)
    runner_hash = sha256(Path(__file__))
    structure_hash = sha256(STRUCTURE_PATH)
    run_payload = {"protocol": protocol_hash, "corpus": corpus_hash, "runner": runner_hash, "structure": structure_hash, "gates": gates}
    run_id = hashlib.sha256(json.dumps(run_payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
    status_counts = {status: sum(item["status"] == status for item in gates) for status in sorted({item["status"] for item in gates})}
    report = {
        "schema": "uni.flagellum.cross-study-parity-report/1.0.0",
        "protocolId": protocol["protocolId"],
        "runId": run_id,
        "executedAt": "2026-07-17T20:30:00Z",
        "compute": "CPU_ONLY_NO_LLM_NO_GPU",
        "summary": {
            "overall": "FULL_PARITY" if full_pass else "PARTIAL_PARITY_ONLY",
            "fullBiologicalParityAchieved": full_pass,
            "statusCounts": status_counts,
            "directIndependentMotorCellLowerBound": corpus["breadth"]["directIndependentMotorCellLowerBound"],
            "directPrimaryArtifactFamilies": len(corpus["breadth"]["directPrimaryArtifactFamilies"]),
            "attributedStudies": len(corpus["breadth"]["attributedStudies"]),
            "previousSingleStudyOverall": previous["summary"]["overall"],
        },
        "modelScope": {
            "nowExpressed": ["post-perturbation stator dwell kinetics", "rotation-gated stator assembly", "torque-conditioned switching", "finite-lattice occupancy cooperativity", "non-equilibrium GMC switching", "whole-cell RFT propulsion"],
            "stillMissing": ["commensurate cross-laboratory parameter transfer", "molecular identity of hidden dwell states", "conflict-free structural geometry", "Active-Inference-specific intervention", "live calibrated signal", "independent wet-lab replication", "fabricated physical validation"],
        },
        "gates": gates,
        "claim": "The expanded model reproduces several published observational layers, but full and complete parity with real biology is not achieved.",
    }
    write_json(REPORT_PATH, report)
    write_json(PUBLIC_REPORT_PATH, report)

    artifacts = {
        "protocol": PROTOCOL_PATH,
        "corpus": CORPUS_PATH,
        "structuralStateMap": STRUCTURE_PATH,
        "evidenceIngestor": ROOT / "scripts" / "ingest-cross-study-evidence.py",
        "pythonRunner": Path(__file__),
        "rawArchiveVerifier": ROOT / "scripts" / "verify-ito-raw-archive.py",
        "independentCrossStudyVerifier": ROOT / "scripts" / "independent-cross-study-check.mjs",
        "previousScienceReport": PREVIOUS_PATH,
        "itoRawArchiveVerification": ROOT / "experiments" / "results" / "ito-raw-archive-verification.json",
        "crossStudyReport": REPORT_PATH,
    }
    audit = {
        "schema": "uni.flagellum.cross-study-parity-audit/1.0.0",
        "runId": run_id,
        "artifacts": {name: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size} for name, path in artifacts.items()},
        "upstreamArtifacts": corpus["sourceIntegrity"]["localArtifacts"],
        "largeExternalArtifactLedger": corpus["sourceIntegrity"]["itoRawArchive"]["cacheVerification"],
        "repositorySources": {
            "wadhwa": "c83119131c3ce3742460a2e3b6bd6c6e44bef4d5",
            "mattinglyGmc": "c3bb92455804fe26e7b99b22c18c2d786be0db71",
        },
        "failedGates": [item["id"] for item in gates if item["status"] == "FAIL"],
        "notEstablishedGates": [item["id"] for item in gates if item["status"] == "NOT_ESTABLISHED"],
        "externalBlocks": [item["id"] for item in gates if item["status"] == "BLOCKED_EXTERNAL"],
        "determinism": {"seed": SEED, "bootstrapReplicates": BOOTSTRAPS, "jsonNaNForbidden": True, "lineEndings": "LF"},
    }
    write_json(AUDIT_PATH, audit)
    write_json(PUBLIC_AUDIT_PATH, audit)
    print(json.dumps({"runId": run_id, "reportSha256": sha256(REPORT_PATH), "auditSha256": sha256(AUDIT_PATH), "statusCounts": status_counts, "fullParity": full_pass}))


if __name__ == "__main__":
    main()
