import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import test from "node:test";
import scienceReport from "../experiments/results/science-gates-report.json" with { type: "json" };
import crossStudyReport from "../experiments/results/cross-study-parity-report.json" with { type: "json" };
import {
  EVIDENCE_ASSETS, LESSON_EXPORT_SCHEMA, REPLAY_FRAMES, RUNTIME_MODES, TRUTH_CLASSES,
  WALKTHROUGH_STEPS, createLessonExport, createObserverRecord, getReplayFrame,
  paperExampleResults, recordsToCsv, truthClassForMode, validateLessonExport, validateWalkthrough,
} from "../lib/walkthrough.js";

const root = new URL("..", import.meta.url).pathname.replace(/^\/(.:)/, "$1");

async function sha256(path) {
  return createHash("sha256").update(await readFile(path)).digest("hex");
}

test("walkthrough has 13 ordered, evidence-bound, gate-bound lessons", () => {
  assert.deepEqual(validateWalkthrough(), { valid: true, errors: [] });
  assert.equal(WALKTHROUGH_STEPS.length, 13);
  assert.deepEqual(WALKTHROUGH_STEPS.map((step) => step.index), [...Array(13).keys()]);
  assert.equal(new Set(WALKTHROUGH_STEPS.map((step) => step.id)).size, 13);
  const evidenceIds = new Set(EVIDENCE_ASSETS.map((asset) => asset.id));
  const gateIds = new Set([...scienceReport.gates, ...crossStudyReport.gates].map((gate) => gate.id));
  for (const step of WALKTHROUGH_STEPS) {
    assert.ok(step.evidenceIds.length > 0, `${step.id} must cite evidence`);
    assert.ok(step.gateIds.length > 0, `${step.id} must cite gates`);
    assert.ok(step.evidenceIds.every((id) => evidenceIds.has(id)), `${step.id} evidence reference`);
    assert.ok(step.gateIds.every((id) => gateIds.has(id)), `${step.id} gate reference`);
    assert.ok(Object.values(step.narration).every((value) => value.length > 20), `${step.id} authored teacher text`);
  }
});

test("truth contract retains species and evidence-class separation", () => {
  assert.deepEqual(RUNTIME_MODES, ["OBSERVED_REPLAY", "SYNTHETIC_WORLD", "LIVE_INSTRUMENT"]);
  assert.deepEqual(TRUTH_CLASSES, ["OBSERVED", "STRUCTURAL_RECONSTRUCTION", "REDUCED_MODEL", "UNI_PHYSICAL_ANALOGUE"]);
  assert.equal(truthClassForMode("SYNTHETIC_WORLD"), "REDUCED_MODEL");
  assert.equal(truthClassForMode("OBSERVED_REPLAY"), "OBSERVED");
  assert.equal(truthClassForMode("LIVE_INSTRUMENT"), "OBSERVED");
  const mears = EVIDENCE_ASSETS.find((asset) => asset.id === "MEARS_2014_VIDEO_1");
  const basalBody = EVIDENCE_ASSETS.find((asset) => asset.id === "PDB_7E82");
  const stator = EVIDENCE_ASSETS.find((asset) => asset.id === "PDB_6YSL");
  assert.equal(mears.species, "Escherichia coli");
  assert.match(basalBody.species, /Salmonella/);
  assert.equal(stator.species, "Bacillus subtilis");
  assert.notEqual(mears.species, basalBody.species);
  assert.notEqual(basalBody.species, stator.species);
  assert.ok(EVIDENCE_ASSETS.filter((asset) => asset.kind === "structure").every((asset) => asset.sourceClass === "STRUCTURAL_RECONSTRUCTION"));
  assert.ok(EVIDENCE_ASSETS.filter((asset) => asset.evidenceType === "reconstruction").every((asset) => asset.sourceClass === "STRUCTURAL_RECONSTRUCTION"));
  assert.ok(EVIDENCE_ASSETS.every((asset) => ["observed", "derived", "reconstruction", "model"].includes(asset.evidenceType)));
});

test("all local evidence assets match pinned SHA-256 identities", async () => {
  for (const asset of EVIDENCE_ASSETS.filter((candidate) => candidate.localPath)) {
    const path = join(root, "public", asset.localPath.replace(/^\//, ""));
    assert.equal(await sha256(path), asset.sha256, `${asset.id} hash`);
  }
  const manifest = JSON.parse(await readFile(join(root, "experiments", "walkthrough-evidence-manifest.v1.json"), "utf8"));
  const publicManifest = JSON.parse(await readFile(join(root, "public", "walkthrough-evidence-manifest.v1.json"), "utf8"));
  assert.deepEqual(publicManifest, manifest);
  for (const item of manifest.assets) assert.equal(await sha256(join(root, item.path)), item.sha256, `${item.id} manifest hash`);
});

test("recorded replay is deterministic, frozen, and exposes missing fields", () => {
  assert.equal(REPLAY_FRAMES.length, 12);
  assert.deepEqual(getReplayFrame(0), getReplayFrame(12));
  assert.deepEqual(getReplayFrame(-1), getReplayFrame(11));
  for (const frame of REPLAY_FRAMES) {
    assert.equal(frame.partition, "holdout");
    assert.ok(frame.motorId && frame.eventId);
    assert.ok(frame.measured.durationS > 0);
    assert.equal(frame.measured.rightCensored, false);
    assert.deepEqual(frame.missingFields, ["ligandUm", "motorSpeedRpm", "rotation", "loadPnNm", "pmfMv", "cheYpUm"]);
  }
});

test("every pencil-and-paper numerical anchor reproduces independently", () => {
  const values = paperExampleResults();
  const kbt = 1.380649e-23 * 300;
  const work = 700e-21 * 2 * Math.PI;
  assert.equal(values.cellSpeedUmS, 20);
  assert.ok(Math.abs(values.revolutionWorkJ - work) < 1e-30);
  assert.ok(Math.abs(values.revolutionWorkKbt - work / kbt) < 1e-10);
  assert.ok(Math.abs(values.allCcwProbability - 0.729) < 1e-15);
  assert.equal(values.posteriorOdds, 6);
  assert.equal(values.posteriorConditionalProbability, 6 / 7);
  assert.ok(Math.abs(values.residualUm + 0.02) < 1e-12);
  assert.ok(Math.abs(values.logScoreAdvantageNat - Math.log(2.5)) < 1e-12);
  assert.ok(Math.abs(values.rmse - 0.2) < 1e-12);
});

test("observer notebook exports, imports, and rejects truth laundering", () => {
  const datasetHashes = Object.fromEntries(EVIDENCE_ASSETS.map((asset) => [asset.id, asset.sha256]));
  const observed = createObserverRecord({ sessionId: "test-session", stepId: WALKTHROUGH_STEPS[9].id, runtimeMode: "OBSERVED_REPLAY", prediction: "on", observation: "6 to 7 stators", calculation: "7-6=1", interpretation: "event adds stators", alternativeExplanation: "state extraction error", confidence: 65, datasetHashes });
  const synthetic = createObserverRecord({ sessionId: "test-session", stepId: WALKTHROUGH_STEPS[7].id, runtimeMode: "SYNTHETIC_WORLD", prediction: "rising", observation: "model signal", alternativeExplanation: "parameter sensitivity", confidence: 50, datasetHashes });
  assert.equal(observed.truthClass, "OBSERVED");
  assert.equal(synthetic.truthClass, "REDUCED_MODEL");
  const exported = createLessonExport([observed, synthetic], { applicationCommit: "test", modelRunId: "run-test" });
  assert.equal(exported.schema, LESSON_EXPORT_SCHEMA);
  const roundTrip = JSON.parse(JSON.stringify(exported));
  assert.deepEqual(validateLessonExport(roundTrip), { valid: true, errors: [] });
  assert.deepEqual(roundTrip.records, [observed, synthetic]);
  roundTrip.records[1].truthClass = "OBSERVED";
  const rejected = validateLessonExport(roundTrip);
  assert.equal(rejected.valid, false);
  assert.match(rejected.errors.join(" "), /Truth class mismatch/);
  const csv = recordsToCsv([observed]);
  assert.match(csv, /sessionId,stepId/);
  assert.match(csv, /test-session/);
});

test("walkthrough application contains no LLM or GPU runtime", async () => {
  const files = ["biological-stage.tsx", "guided-teacher.tsx", "living-science-walkthrough.tsx"];
  const source = (await Promise.all(files.map((file) => readFile(join(root, "app", file), "utf8")))).join("\n");
  assert.doesNotMatch(source, /WebGL|WebGPU|from\s+["']three(?:\.js)?["']|@react-three|navigator\.gpu/i);
  assert.doesNotMatch(source, /openai|anthropic|gemini|languageModel|chatCompletion|generateText/i);
  assert.doesNotMatch(source, /fetch\s*\(|XMLHttpRequest|WebSocket/i);
  assert.match(source, /getContext\("2d"\)/);
  assert.match(source, /SpeechSynthesisUtterance/);
});
