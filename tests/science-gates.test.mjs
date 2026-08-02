import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import {
  sourceCoefficients,
  sourceDensities,
  sourceLogLikelihood,
  sourceMoments,
  sourceSurvival,
} from "../lib/source-first-passage.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));
const sha256 = (relative) => createHash("sha256").update(fs.readFileSync(path.join(root, relative))).digest("hex");
const report = read("experiments/results/science-gates-report.json");
const audit = read("experiments/results/science-gates-audit.json");
const dataset = read("experiments/data/wadhwa-2022-events.json");
const fitted = report.fittedMechanism;

test("first-passage coefficients and competing risks are normalized", () => {
  for (let state = 1; state <= 8; state += 1) {
    const weights = sourceCoefficients(state, fitted.c1, fitted.c2, fitted.c3);
    assert.ok(weights.every((value) => value >= 0));
    assert.ok(Math.abs(weights.reduce((sum, value) => sum + value, 0) - 1) < 1e-12);
    assert.ok(Math.abs(sourceSurvival(0, state, fitted) - 1) < 1e-12);
    const moments = sourceMoments(state, fitted);
    assert.ok(moments.meanDwellSeconds > 0);
    assert.ok(moments.fractionPlus >= 0 && moments.fractionPlus <= 1);
  }
});

test("analytic density equals the negative survival derivative", () => {
  const time = 7.25;
  const step = 1e-5;
  for (let state = 1; state <= 8; state += 1) {
    const density = sourceDensities(time, state, fitted).total;
    const derivative = (sourceSurvival(time + step, state, fitted) - sourceSurvival(time - step, state, fitted)) / (2 * step);
    assert.ok(Math.abs(density + derivative) < 2e-8);
  }
});

test("right-censored observations contribute survival, never an invented direction", () => {
  const censored = dataset.events.find((event) => event.rightCensored && event.stateN >= 1 && event.stateN <= 8);
  assert.ok(censored);
  assert.equal(censored.direction, null);
  assert.ok(Math.abs(sourceLogLikelihood(censored, fitted) - Math.log(sourceSurvival(censored.durationS, censored.stateN, fitted))) < 1e-12);
});

test("science ledger preserves failed and external gates", () => {
  assert.equal(report.summary.overall, "PARTIAL_PARITY_ONLY");
  assert.equal(report.summary.fullBiologicalParityAchieved, false);
  assert.ok(report.gates.some((gate) => gate.status === "FAIL"));
  assert.ok(report.gates.some((gate) => gate.status === "BLOCKED_EXTERNAL"));
  assert.equal(report.gates.find((gate) => gate.id === "G03_PUBLIC_ARTIFACT_PARITY").status, "FAIL");
  assert.equal(report.gates.find((gate) => gate.id === "G06_HELDOUT_MECHANISTIC_PREDICTION").status, "FAIL");
  assert.equal(report.gates.find((gate) => gate.id === "G10_ACTIVE_INFERENCE_CAUSAL_IDENTITY").status, "NOT_ESTABLISHED");
});

test("audit manifest binds the science report to its inputs and implementations", () => {
  assert.equal(audit.runId, report.runId);
  for (const artifact of Object.values(audit.artifacts)) {
    assert.equal(artifact.sha256, sha256(artifact.path), `SHA-256 mismatch for ${artifact.path}`);
  }
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/results/science-gates-report.json")),
    fs.readFileSync(path.join(root, "public/science-gates-report.json")),
  );
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/results/science-gates-audit.json")),
    fs.readFileSync(path.join(root, "public/science-gates-audit.json")),
  );
  assert.match(audit.artifacts.pythonGateRunner.sha256, /^[a-f0-9]{64}$/);
  assert.match(audit.artifacts.javascriptEquationOracle.sha256, /^[a-f0-9]{64}$/);
  assert.deepEqual(audit.externalBlocks.sort(), report.gates.filter((gate) => gate.status === "BLOCKED_EXTERNAL").map((gate) => gate.id).sort());
});
