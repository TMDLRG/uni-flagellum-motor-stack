#!/usr/bin/env node
/** Independent Node.js oracle for cross-study report invariants and key fits. */

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));
const sha256 = (relative) => crypto.createHash("sha256").update(fs.readFileSync(path.join(root, relative))).digest("hex");
const corpus = read("experiments/data/cross-study-motor-evidence.json");
const report = read("experiments/results/cross-study-parity-report.json");
const audit = read("experiments/results/cross-study-parity-audit.json");
const failures = [];

function close(actual, expected, tolerance, label) {
  if (!Number.isFinite(actual) || Math.abs(actual - expected) > tolerance) {
    failures.push(`${label}: ${actual} versus ${expected} (tol ${tolerance})`);
  }
}

function solve(matrix, vector) {
  const n = vector.length;
  const augmented = matrix.map((row, index) => [...row, vector[index]]);
  for (let column = 0; column < n; column += 1) {
    let pivot = column;
    for (let row = column + 1; row < n; row += 1) if (Math.abs(augmented[row][column]) > Math.abs(augmented[pivot][column])) pivot = row;
    [augmented[column], augmented[pivot]] = [augmented[pivot], augmented[column]];
    const divisor = augmented[column][column];
    if (Math.abs(divisor) < 1e-14) throw new Error("Singular independent normal equation");
    for (let item = column; item <= n; item += 1) augmented[column][item] /= divisor;
    for (let row = 0; row < n; row += 1) {
      if (row === column) continue;
      const factor = augmented[row][column];
      for (let item = column; item <= n; item += 1) augmented[row][item] -= factor * augmented[column][item];
    }
  }
  return augmented.map((row) => row[n]);
}

function weightedFit(design, values, errors) {
  const p = design[0].length;
  const xtwx = Array.from({ length: p }, () => Array(p).fill(0));
  const xtwy = Array(p).fill(0);
  for (let row = 0; row < design.length; row += 1) {
    const weight = 1 / errors[row] ** 2;
    for (let a = 0; a < p; a += 1) {
      xtwy[a] += design[row][a] * values[row] * weight;
      for (let b = 0; b < p; b += 1) xtwx[a][b] += design[row][a] * design[row][b] * weight;
    }
  }
  return solve(xtwx, xtwy);
}

function interpolate(x, xs, ys) {
  for (let index = 1; index < xs.length; index += 1) {
    if (x <= xs[index]) {
      const fraction = (x - xs[index - 1]) / (xs[index] - xs[index - 1]);
      return ys[index - 1] + fraction * (ys[index] - ys[index - 1]);
    }
  }
  return ys.at(-1);
}

const gates = Object.fromEntries(report.gates.map((gate) => [gate.id, gate]));

// Recompute Ito leave-one-bin-out result with an independently written WLS solver.
const bins = corpus.studies.ito2021.rotationBindingBins["20Hz"].filter((row) => row.bindingRatePerSecond != null && row.bindingRateSe != null);
const x = bins.map((row) => [1, Math.max(row.meanSpeedHz, 0), Math.max(-row.meanSpeedHz, 0)]);
const y = bins.map((row) => row.bindingRatePerSecond);
const se = bins.map((row) => row.bindingRateSe);
const predictions = [];
const baselines = [];
for (let heldout = 0; heldout < bins.length; heldout += 1) {
  const keep = bins.map((_, index) => index).filter((index) => index !== heldout);
  const beta = weightedFit(keep.map((index) => x[index]), keep.map((index) => y[index]), keep.map((index) => se[index]));
  predictions.push(x[heldout].reduce((sum, value, index) => sum + value * beta[index], 0));
  const weights = keep.map((index) => 1 / se[index] ** 2);
  baselines.push(keep.reduce((sum, index, local) => sum + y[index] * weights[local], 0) / weights.reduce((a, b) => a + b, 0));
}
const rmse = Math.sqrt(predictions.reduce((sum, value, index) => sum + (value - y[index]) ** 2, 0) / y.length);
const baselineRmse = Math.sqrt(baselines.reduce((sum, value, index) => sum + (value - y[index]) ** 2, 0) / y.length);
close(rmse, gates.X03_ROTATION_GATED_ASSEMBLY.evidence.leaveOneBinOutRmse, 1e-10, "Ito LOO RMSE");
close(baselineRmse, gates.X03_ROTATION_GATED_ASSEMBLY.evidence.constantLeaveOneBinOutRmse, 1e-10, "Ito constant LOO RMSE");

// Re-evaluate the reported lattice solution and an independently optimized J=0 baseline.
const states = [];
for (let encoded = 0; encoded < 2 ** 13; encoded += 1) {
  const bits = Array.from({ length: 13 }, (_, index) => (encoded >> index) & 1);
  states.push({ count: bits.reduce((a, b) => a + b, 0), adjacent: bits.reduce((sum, bit, index) => sum + bit * bits[(index + 1) % 13], 0) });
}
function distribution(jValue, mu) {
  const logs = states.map((state) => jValue * state.adjacent + mu * state.count);
  const peak = Math.max(...logs);
  const weights = logs.map((value) => Math.exp(value - peak));
  const total = weights.reduce((a, b) => a + b, 0);
  return Array.from({ length: 14 }, (_, occupied) => weights.reduce((sum, value, index) => sum + (states[index].count === occupied ? value : 0), 0) / total);
}
function sse(jValue, mus, observed) {
  return observed.reduce((total, values, index) => {
    const predicted = distribution(jValue, mus[index]);
    return total + predicted.reduce((sum, value, item) => sum + (value - values[item]) ** 2, 0);
  }, 0);
}
function golden(objective, low = -10, high = 10, iterations = 60) {
  const ratio = (Math.sqrt(5) - 1) / 2;
  let left = high - ratio * (high - low);
  let right = low + ratio * (high - low);
  let fLeft = objective(left);
  let fRight = objective(right);
  for (let iteration = 0; iteration < iterations; iteration += 1) {
    if (fLeft < fRight) {
      high = right; right = left; fRight = fLeft; left = high - ratio * (high - low); fLeft = objective(left);
    } else {
      low = left; left = right; fLeft = fRight; right = low + ratio * (high - low); fRight = objective(right);
    }
  }
  return (low + high) / 2;
}
const probabilityMap = corpus.studies.francoOnate2025.probabilityByBead;
const observed = ["300nm", "500nm", "1300nm"].map((label) => {
  const total = probabilityMap[label].reduce((a, b) => a + b, 0);
  return probabilityMap[label].map((value) => value / total);
});
const lattice = gates.X06_FINITE_LATTICE_COOPERATIVITY.evidence;
close(sse(lattice.J, ["300nm", "500nm", "1300nm"].map((label) => lattice.muByBead[label]), observed), lattice.sse, 1e-10, "lattice fitted SSE");
const j0Mus = observed.map((values) => golden((mu) => sse(0, [mu], [values])));
const j0Sse = sse(0, j0Mus, observed);
close(j0Sse, lattice.baselineJ0Sse, 1e-9, "lattice J=0 SSE");

// Recompute the source GMC-to-Yuan interpolation metrics.
const model = corpus.studies.mattingly2026.sourceSwitchingPrediction;
const order = model.speedHz.map((_, index) => index).sort((a, b) => model.speedHz[a] - model.speedHz[b]);
const modelX = order.map((index) => model.speedHz[index]);
for (const [name, speedKey, rateKey, lowerKey, upperKey, modelKey, reportKey] of [
  ["CW", "speedCwHz", "kCwToCcw", "kCwToCcwLower", "kCwToCcwUpper", "kCwToCcw", "cwToCcw"],
  ["CCW", "speedCcwHz", "kCcwToCw", "kCcwToCwLower", "kCcwToCwUpper", "kCcwToCw", "ccwToCw"],
]) {
  const modelY = order.map((index) => model[modelKey][index]);
  const usable = corpus.studies.mattingly2026.yuan2009DigitizedSwitching.filter((row) => row[speedKey] >= modelX[0] && row[speedKey] <= modelX.at(-1));
  const residuals = usable.map((row) => interpolate(row[speedKey], modelX, modelY) - row[rateKey]);
  const z = residuals.map((value, index) => Math.abs(value) / Math.max(value >= 0 ? usable[index][upperKey] : usable[index][lowerKey], 1e-12));
  close(z.reduce((a, b) => a + b, 0) / z.length, gates.X08_GMC_SWITCHING_OBSERVATIONS.evidence[reportKey].meanAbsoluteStandardizedResidual, 1e-10, `${name} GMC standardized residual`);
}

// Recompute RFT cell-speed RMSE.
const lisevich = corpus.studies.lisevich2025;
const rftX = lisevich.rftSourcePredictions.map((row) => row.flagellaCount);
const rftY = lisevich.rftSourcePredictions.map((row) => row.meanSpeedUmPerSecond);
const rftResiduals = lisevich.experimentalCellSpeeds.map((row) => interpolate(row.flagellaCount, rftX, rftY) - row.speedUmPerSecond);
const rftRmse = Math.sqrt(rftResiduals.reduce((sum, value) => sum + value ** 2, 0) / rftResiduals.length);
close(rftRmse, gates.X09_WHOLE_CELL_PROPULSION.evidence.rftCellSpeed.rmseUmPerSecond, 1e-10, "RFT RMSE");

for (const artifact of Object.values(audit.artifacts)) {
  const actual = sha256(artifact.path);
  if (actual !== artifact.sha256) failures.push(`Audit SHA mismatch for ${artifact.path}`);
}
if (audit.runId !== report.runId) failures.push("Audit/report runId mismatch");
if (report.summary.fullBiologicalParityAchieved !== false) failures.push("Full parity must remain false");
if (corpus.breadth.directIndependentMotorCellLowerBound !== 409) failures.push("Direct biological-unit lower bound changed");

const result = {
  status: failures.length ? "FAIL" : "PASS",
  failures,
  checks: {
    itoLeaveOneBinOutRmse: rmse,
    latticeFittedSse: lattice.sse,
    latticeJ0Sse: j0Sse,
    rftRmse,
    auditArtifacts: Object.keys(audit.artifacts).length,
  },
};
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exitCode = 1;
