import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { posteriorSlowGivenSurvival, runObservedExperiment } from "../lib/observed-experiment.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const protocolPath = path.join(root, "experiments", "preregistration.v1.json");
const datasetPath = path.join(root, "experiments", "data", "wadhwa-2022-events.json");
const reportPath = path.join(root, "experiments", "results", "observed-experiment-report.json");
const protocol = JSON.parse(fs.readFileSync(protocolPath, "utf8"));
const dataset = JSON.parse(fs.readFileSync(datasetPath, "utf8"));
const frozenReport = JSON.parse(fs.readFileSync(reportPath, "utf8"));

const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

test("observed event artifact retains the pinned raw-data identity", () => {
  assert.equal(dataset.source.commit, "c83119131c3ce3742460a2e3b6bd6c6e44bef4d5");
  assert.equal(dataset.source.observedRawSha256, "c14de12cc11df8af2ab87f1ec94629eebc249c0e1475c24f850f5a28ddd1ea22");
  assert.equal(dataset.source.observedRawSha256, protocol.source.rawSha256);
  assert.equal(dataset.ingestion.motorCount, 129);
  assert.equal(dataset.ingestion.analysisStartIndex, 3500);
});

test("motor-level partition prevents train/holdout leakage", () => {
  const train = new Set(dataset.motors.filter((motor) => motor.partition === "train").map((motor) => motor.motorId));
  const holdout = new Set(dataset.motors.filter((motor) => motor.partition === "holdout").map((motor) => motor.motorId));
  assert.equal([...train].some((id) => holdout.has(id)), false);
  for (const event of dataset.events) assert.equal(event.partition, train.has(event.motorId) ? "train" : "holdout");
});

test("frozen observed analysis replays byte-for-value deterministically", () => {
  const identities = frozenReport.identities;
  assert.equal(identities.protocolSha256, sha256(protocolPath));
  assert.equal(identities.derivedEventsSha256, sha256(datasetPath));
  const first = runObservedExperiment(dataset, protocol, identities);
  const second = runObservedExperiment(dataset, protocol, identities);
  assert.deepEqual(first, second);
  assert.deepEqual(first, frozenReport);
});

test("held-out analysis reports the adverse flexible-baseline comparison", () => {
  const results = frozenReport.heldoutResults;
  assert.ok(results.pairedMixtureAdvantageInterval95.mixtureVsExponential.lower > 0);
  assert.ok(results.pairedMixtureAdvantageNatsPerEvent.mixtureVsLognormal < 0);
  assert.ok(results.meanLogScoreNatsPerEvent.lognormal > results.meanLogScoreNatsPerEvent.mixture);
  const h2 = frozenReport.claims.find((claim) => claim.hypothesisId === "H2_HELDOUT_LOG_SCORE");
  assert.match(h2.fence, /does not prove/i);
});

test("overdispersion gate is evaluated only on eligible held-out stator states", () => {
  assert.deepEqual(frozenReport.cohort.eligibleStates, [1, 2, 3, 4, 5, 6, 7, 8]);
  assert.ok(frozenReport.heldoutResults.meanCvSquaredInterval95.lower > 1);
  for (const row of frozenReport.heldoutResults.stateSummary) {
    assert.ok(row.events >= 20);
    assert.ok(row.motors >= 5);
  }
});

test("survival evidence monotonically increases the slow-timescale posterior", () => {
  const mixture = frozenReport.fittedOnTrainingOnly.normalizedDurationModels.mixture;
  let previous = posteriorSlowGivenSurvival(0, mixture);
  for (let time = 0.05; time <= 12; time += 0.05) {
    const current = posteriorSlowGivenSurvival(time, mixture);
    assert.ok(current + 1e-12 >= previous);
    previous = current;
  }
});

test("observed report cannot be confused with a live instrument run", () => {
  assert.equal(frozenReport.executionClass, "CPU_ONLY_DETERMINISTIC_HELDOUT_ANALYSIS");
  assert.match(frozenReport.dataFlow.worldProcess, /Previously recorded/);
  assert.equal("LIVE_SERIAL_INSTRUMENT" in frozenReport, false);
  assert.equal(frozenReport.audit.outcomeAccessDuringFit, false);
});
