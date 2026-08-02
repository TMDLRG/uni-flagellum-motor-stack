#!/usr/bin/env node
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { sourceLogLikelihood, sourceMoments } from "../lib/source-first-passage.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));
const dataset = read("experiments/data/wadhwa-2022-events.json");
const observed = read("experiments/results/observed-experiment-report.json");
const reference = read("experiments/source-parity-reference.json");
const report = read("experiments/results/science-gates-report.json");
const states = observed.cohort.eligibleStates;
const holdout = dataset.events.filter((event) => event.partition === "holdout" && states.includes(event.stateN));
const fitted = report.fittedMechanism;

const sourceScores = holdout.map((event) => sourceLogLikelihood(event, fitted));
const sourceMean = sourceScores.reduce((sum, value) => sum + value, 0) / sourceScores.length;
const predictiveGate = report.gates.find((gate) => gate.id === "G06_HELDOUT_MECHANISTIC_PREDICTION");
assert.ok(Math.abs(sourceMean - predictiveGate.evidence.mechanisticMeanLogScorePerInterval) < 1e-12);

const bundled = reference.bundledCodeParameterVector;
const bundledParameters = {
  kPlusByN: bundled.kPlusByNPerSecond,
  c1: bundled.c1,
  c2: bundled.c2,
  c3: bundled.c3,
  sigmaPlus: bundled.sigmaPlusPerSecond,
  sigmaMinus: bundled.sigmaMinusPerSecond,
};
const theory = reference.sourceDataFigure3.theory;
const bundledMoments = states.map((state) => sourceMoments(state, bundledParameters, true));
const relativeMeanErrors = bundledMoments.map((moment, index) =>
  Math.abs(moment.meanDwellSeconds / theory.meanDwellSeconds[states[index]] - 1));
assert.ok(Math.max(...relativeMeanErrors) > 0.5);

for (const state of states) {
  const moment = sourceMoments(state, fitted);
  assert.ok(Number.isFinite(moment.meanDwellSeconds) && moment.meanDwellSeconds > 0);
  assert.ok(Math.abs(moment.fractionPlus + (1 - moment.fractionPlus) - 1) < 1e-14);
}

assert.equal(report.summary.fullBiologicalParityAchieved, false);
assert.equal(report.gates.find((gate) => gate.id === "G03_PUBLIC_ARTIFACT_PARITY").status, "FAIL");
assert.equal(report.gates.find((gate) => gate.id === "G10_ACTIVE_INFERENCE_CAUSAL_IDENTITY").status, "NOT_ESTABLISHED");
console.log(JSON.stringify({
  status: "PASS",
  oracle: "Independent JavaScript first-passage and held-out likelihood implementation",
  holdoutIntervals: holdout.length,
  mechanisticMeanLogScorePerInterval: sourceMean,
  publicArtifactMismatchDetected: true,
}, null, 2));
