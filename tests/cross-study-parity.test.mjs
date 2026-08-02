import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (relative) => JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));
const sha256 = (relative) => crypto.createHash("sha256").update(fs.readFileSync(path.join(root, relative))).digest("hex");
const corpus = read("experiments/data/cross-study-motor-evidence.json");
const protocol = read("experiments/cross-study-preregistration.v1.json");
const report = read("experiments/results/cross-study-parity-report.json");
const audit = read("experiments/results/cross-study-parity-audit.json");

test("cross-study protocol has one result for every ordered gate", () => {
  assert.equal(protocol.gates.length, 16);
  assert.deepEqual(report.gates.map((gate) => gate.id), protocol.gates.map((gate) => gate.id));
  assert.equal(new Set(report.gates.map((gate) => gate.id)).size, 16);
  assert.deepEqual(report.summary.statusCounts, { BLOCKED_EXTERNAL: 3, FAIL: 3, NOT_ESTABLISHED: 2, PASS: 8 });
});

test("source corpus expands biological units without counting time points as replicates", () => {
  assert.equal(corpus.breadth.directIndependentMotorCellLowerBound, 409);
  assert.equal(corpus.breadth.directPrimaryArtifactFamilies.length, 4);
  assert.equal(corpus.breadth.attributedStudies.length, 11);
  assert.equal(corpus.studies.ito2021.motorCount, 40);
  assert.equal(corpus.studies.ito2021.rotationSampleCount, 191920);
  assert.equal(corpus.studies.ito2021.statorSampleCount, 159800);
  assert.match(corpus.breadth.warning, /never counted as independent biological units/i);
});

test("all frozen cached upstream artifacts remain byte-identical when present", () => {
  let checkedArtifacts = 0;
  for (const artifact of corpus.sourceIntegrity.localArtifacts) {
    const actual = path.join(root, artifact.cachePath);
    assert.equal(artifact.verified, true);
    assert.match(artifact.sha256, /^[a-f0-9]{64}$/);
    if (fs.existsSync(actual)) {
      checkedArtifacts += 1;
      assert.equal(fs.statSync(actual).size, artifact.bytes, artifact.id);
      assert.equal(sha256(artifact.cachePath), artifact.sha256, artifact.id);
    }
  }
  assert.ok(checkedArtifacts === 0 || checkedArtifacts === corpus.sourceIntegrity.localArtifacts.length, "source cache must be complete or absent");
  const raw = corpus.sourceIntegrity.itoRawArchive.cacheVerification;
  assert.equal(raw.status, "PASS");
  assert.equal(raw.expected.bytes, 4085227742);
  assert.equal(raw.expected.md5, "d42879e66142ff7190f256f4276db111");
  assert.equal(raw.observed.zipEntryCount, 505);
  assert.equal(raw.observed.zipCrcFailure, null);
});

test("expanded mechanistic gates preserve passes and falsifiers", () => {
  const gates = Object.fromEntries(report.gates.map((gate) => [gate.id, gate]));
  for (const id of ["X01_SOURCE_INTEGRITY", "X02_CORPUS_BREADTH", "X03_ROTATION_GATED_ASSEMBLY", "X04_STATOR_CHEY_COUPLING", "X05_TORQUE_SWITCHING_RESPONSE", "X07_GMC_GENERATOR_REPRODUCTION", "X08_GMC_SWITCHING_OBSERVATIONS", "X09_WHOLE_CELL_PROPULSION"]) {
    assert.equal(gates[id].status, "PASS", id);
  }
  assert.equal(gates.X06_FINITE_LATTICE_COOPERATIVITY.status, "FAIL");
  assert.ok(gates.X06_FINITE_LATTICE_COOPERATIVITY.evidence.crossStatisticJDisagreement.absoluteDifference > 0.9);
  assert.ok(Math.abs(gates.X06_FINITE_LATTICE_COOPERATIVITY.evidence.momentFits.unweighted.J - 1.21) < 0.05);
  assert.equal(gates.X11_STRUCTURAL_CONSISTENCY.status, "FAIL");
  assert.equal(gates.X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY.status, "NOT_ESTABLISHED");
  assert.equal(gates.X16_FULL_BIOLOGICAL_PARITY.status, "FAIL");
  assert.equal(report.summary.fullBiologicalParityAchieved, false);
});

test("GMC generator satisfies stochastic-matrix and source-marginal tolerances", () => {
  const evidence = report.gates.find((gate) => gate.id === "X07_GMC_GENERATOR_REPRODUCTION").evidence;
  assert.ok(evidence.minimumOffDiagonalRate >= -1e-14);
  assert.ok(evidence.maximumColumnSumError < 1e-10);
  assert.ok(evidence.stationaryResidualInfinityNorm < 1e-9);
  assert.ok(evidence.engagedMarginalL1 < 0.03);
});

test("audit binds report, corpus, protocol, structure map, and runner bytes", () => {
  assert.equal(audit.runId, report.runId);
  for (const artifact of Object.values(audit.artifacts)) {
    assert.equal(sha256(artifact.path), artifact.sha256, artifact.path);
    assert.equal(fs.statSync(path.join(root, artifact.path)).size, artifact.bytes, artifact.path);
  }
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/results/cross-study-parity-report.json")),
    fs.readFileSync(path.join(root, "public/cross-study-parity-report.json")),
  );
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/results/cross-study-parity-audit.json")),
    fs.readFileSync(path.join(root, "public/cross-study-parity-audit.json")),
  );
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/data/cross-study-motor-evidence.json")),
    fs.readFileSync(path.join(root, "public/cross-study-motor-evidence.json")),
  );
  assert.deepEqual(
    fs.readFileSync(path.join(root, "experiments/results/ito-raw-archive-verification.json")),
    fs.readFileSync(path.join(root, "public/ito-raw-archive-verification.json")),
  );
});
