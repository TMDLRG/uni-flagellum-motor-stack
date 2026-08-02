// Semantic gate: the Phase-D1 correction package stays applied.
//
// Correction record: audits/phase-d/d1-correction-package.v1.json
// Reviewed commit:   fb9aa3369fded56a9be7ac4998d01933599a2d73 (Codex: REJECT_BLOCKING)
//
// Codex issued one bounded correction package against Phase D1. Each correction below
// is MECHANICALLY re-checked here, so that a later edit cannot quietly undo it and so
// that the correction record cannot drift away from the artifacts it describes.
//
// This gate deliberately checks CONSISTENCY BETWEEN DECLARATION AND ARTIFACT. It does
// not re-run any mutation and it does not re-measure any classification. The historical
// result is treated as immutable input.
//
// Oracle independence: every expectation is either a literal frozen in the correction
// record and independently restated here, or a quantity recomputed from the historical
// result's own outcomes array. No production function is used to build an expectation.

import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const phaseD = path.join(root, "audits", "phase-d");

const correction = JSON.parse(fs.readFileSync(path.join(phaseD, "d1-correction-package.v1.json"), "utf8"));
const result = JSON.parse(fs.readFileSync(path.join(phaseD, "d1-semantic-remediation-result.v1.json"), "utf8"));

const byId = (id) => correction.corrections.find((entry) => entry.id === id);
const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

test("D1C0 every historical D1 artifact named by the correction package is byte-identical", () => {
  // The correction package repairs the instrument and adds records. If it has silently
  // edited a measurement instead, this fails.
  for (const entry of correction.preservationContract.byteIdenticalArtifacts) {
    const absolute = path.join(root, ...entry.path.split("/"));
    assert.ok(fs.existsSync(absolute), `Preserved artifact is missing: ${entry.path}`);
    assert.equal(
      sha256(fs.readFileSync(absolute)),
      entry.sha256,
      `Preserved artifact ${entry.path} is NOT byte-identical. A correction package may add records and repair the ` +
        "instrument; it may never rewrite a historical measurement, protocol, prediction or evidence log.",
    );
  }
});

test("D1C1 the historical result is bound to the protocol that actually governed it", () => {
  const c1 = byId("C1_RESULT_PROTOCOL_BINDING");
  const executedPath = c1.authoritativeBinding.executedProtocolPath;
  const absolute = path.join(root, ...executedPath.split("/"));

  assert.ok(fs.existsSync(absolute), `The declared executed protocol is missing: ${executedPath}`);
  assert.equal(
    sha256(fs.readFileSync(absolute)),
    c1.authoritativeBinding.executedProtocolSha256,
    `The declared executed protocol ${executedPath} no longer matches its recorded digest.`,
  );

  // The binding is not taken on trust: the executed protocol must actually CONTAIN every
  // cell that appears in the historical result. The superseded v1 protocol does not.
  const executed = JSON.parse(fs.readFileSync(absolute, "utf8"));
  const executedIds = new Set(executed.mutations.map((mutation) => mutation.id));
  const resultIds = result.outcomes.map((outcome) => outcome.id);

  for (const id of resultIds) {
    assert.ok(
      executedIds.has(id),
      `The historical result contains outcome ${id}, which does not exist in the declared executed protocol ` +
        `${executedPath}. The result/protocol binding recorded in the correction package is wrong.`,
    );
  }
  assert.equal(
    resultIds.length,
    c1.authoritativeBinding.cellCount,
    `The historical result has ${resultIds.length} outcomes but the correction package declares ` +
      `${c1.authoritativeBinding.cellCount} cells.`,
  );

  // Every superseded value must remain visible in the result as the erroneous original.
  for (const entry of c1.authoritativeBinding.supersededFieldsInHistoricalResult) {
    const actual = entry.field.split(".").reduce((node, key) => node?.[key], result);
    assert.deepEqual(
      actual,
      entry.recordedValue,
      `The historical result field '${entry.field}' has been edited. It must be preserved unedited as the ` +
        "erroneous original; the correction record is what supersedes it.",
    );
  }
});

test("D1C1 the replay runner derives both provenance and ancestry from the supplied protocol", () => {
  // Root-cause repair, not just a record. TWO hardcoded references existed: one in the
  // result object (provenance) and one in verifyPredictionAncestry (a precondition gate).
  // The second was load-bearing -- see AF1 in the correction package.
  const runner = fs.readFileSync(path.join(phaseD, "tools", "run-d1-semantic-replay.mjs"), "utf8");
  const code = runner
    .split(/\r?\n/)
    .filter((line) => !line.trim().startsWith("//") && !line.trim().startsWith("*"))
    .join("\n");

  // Only ONE phase-d protocol path literal may remain: the declared default constant.
  const literals = code.match(/"audits\/phase-d\/[^"]*protocol[^"]*\.json"/g) ?? [];
  assert.equal(
    literals.length,
    1,
    `The replay runner contains ${literals.length} hardcoded phase-d protocol path literals: ` +
      `${JSON.stringify(literals)}. Exactly one is permitted, the DEFAULT_PROTOCOL_PATH constant. Any other ` +
      "occurrence means --protocol is being ignored somewhere, as it was for both provenance and ancestry.",
  );
  assert.ok(
    /const DEFAULT_PROTOCOL_PATH/.test(code),
    "The one permitted protocol path literal is no longer the DEFAULT_PROTOCOL_PATH constant.",
  );
  assert.ok(
    /protocolPath:\s*protocolPathUsed/.test(code),
    "The replay runner no longer records the actually-used protocol path in its result.",
  );
  assert.ok(
    /protocolSha256:/.test(code),
    "The replay runner no longer records a digest of the protocol it executed.",
  );
  assert.ok(
    /function verifyPredictionAncestry\(protocolPath,/.test(code) &&
      /verifyPredictionAncestry\(options\.protocolPath,/.test(code),
    "The replay runner's ancestry check no longer takes the SUPPLIED protocol path. A hardcoded ancestry target " +
      "lets a protocol with non-strict ancestry pass a precondition it should fail, which is exactly what " +
      "happened to the addendum protocol at base commit 8baead2 (correction package AF1).",
  );
});

test("D1C1 the non-strict ancestry of the executed protocol is disclosed, not buried", () => {
  const af1 = correction.additionalFindingsDiscoveredWhileCorrecting.find(
    (entry) => entry.id === "AF1_ANCESTRY_PATH_HARDCODED_AND_LOAD_BEARING",
  );
  assert.ok(af1, "AF1 is missing. The load-bearing ancestry defect must remain recorded.");
  assert.equal(af1.severity, "BLOCKING", "AF1 has been downgraded below BLOCKING.");

  // The historical result's ancestry fields must be named as superseded, not just protocolPath.
  const superseded = byId("C1_RESULT_PROTOCOL_BINDING").authoritativeBinding.supersededFieldsInHistoricalResult;
  const fields = superseded.map((entry) => entry.field);
  for (const required of ["protocolPath", "ancestry.protocolCommit", "ancestry.strictAncestry"]) {
    assert.ok(
      fields.includes(required),
      `The historical result field '${required}' is no longer listed as superseded. The preserved result certifies ` +
        "strict prospective ancestry for a protocol that did not govern the run; every affected field must be named.",
    );
  }
  // And the preserved result must still carry the erroneous originals, unedited.
  assert.equal(result.ancestry.strictAncestry, true, "The historical result's ancestry block has been edited.");
  assert.equal(
    result.ancestry.protocolCommit,
    "0a460a66458cd5e82c8ed18197548374739020d9",
    "The historical result's ancestry.protocolCommit has been edited. It must be preserved as the erroneous original.",
  );
});

test("D1C2 the addendum is recorded as AFTER_IMPLEMENTATION_BEFORE_EXECUTION", () => {
  const c2 = byId("C2_ADDENDUM_TIMING");
  assert.equal(
    c2.authoritativeTiming.value,
    "AFTER_IMPLEMENTATION_BEFORE_EXECUTION",
    "The addendum timing classification has changed. The addendum was written after the gates were implemented " +
      "and before any replay was executed; it does not carry pre-implementation prospectivity.",
  );
  assert.ok(
    c2.authoritativeTiming.vocabulary.includes("AFTER_IMPLEMENTATION_BEFORE_EXECUTION"),
    "The timing vocabulary no longer contains the declared value.",
  );
  const ordering = c2.authoritativeTiming.commitOrdering;
  for (const key of ["predictionCommit", "implementationCommit", "addendumCommit", "resultCommit"]) {
    assert.ok(/^[0-9a-f]{40}$/.test(ordering[key]), `${key} is not a full commit SHA.`);
  }
  assert.ok(
    /lower evidential weight|weaker/i.test(c2.authoritativeTiming.evidentialConsequence),
    "The addendum's reduced evidential weight is no longer stated. A pre-execution but post-implementation " +
      "prediction is weaker evidence than a pre-implementation one and must be reported as such.",
  );
});

test("D1C3 detection accounting is 22 classified, 20 credited, 2 uncredited, AC4 FAIL", () => {
  const c3 = byId("C3_DETECTION_ACCOUNTING").authoritativeAccounting;

  // Recomputed from the historical result itself, not copied from the declaration.
  const detected = result.outcomes.filter((o) => o.classification === "DETECTED_SEMANTIC");
  const credited = detected.filter((o) => o.attributionSatisfied);
  const uncredited = detected.filter((o) => !o.attributionSatisfied);

  assert.equal(
    detected.length,
    c3.classifiedDetectedSemantic,
    `Recomputed classified detections (${detected.length}) disagree with the correction record ` +
      `(${c3.classifiedDetectedSemantic}).`,
  );
  assert.equal(
    credited.length,
    c3.creditedDetections,
    `Recomputed CREDITED detections (${credited.length}) disagree with the correction record ` +
      `(${c3.creditedDetections}). Only detections attributable to their declared intended test may be credited.`,
  );
  assert.equal(
    uncredited.length,
    c3.uncreditedDetections,
    `Recomputed UNCREDITED detections (${uncredited.length}) disagree with the correction record ` +
      `(${c3.uncreditedDetections}).`,
  );
  assert.deepEqual(
    uncredited.map((o) => o.id).sort(),
    [...c3.uncreditedIds].sort(),
    "The set of uncredited detections has changed. The two attribution failures must remain visible and named.",
  );
  assert.equal(
    c3.AC4,
    "FAIL",
    "Acceptance criterion AC4 is no longer recorded as FAIL. AC4 is scoped to the twenty-two CLASSIFIED " +
      "detections and required every one of them to be attributable to its declared intended test; two are not.",
  );
  // The frozen AC4 text must be quoted verbatim, so the paraphrase cannot drift again.
  const addendum = JSON.parse(
    fs.readFileSync(path.join(phaseD, "d1-semantic-remediation-protocol-addendum-v2.json"), "utf8"),
  );
  assert.equal(
    c3.AC4FrozenText,
    addendum.acceptanceCriteria.AC4,
    "The AC4 text quoted in the correction record no longer matches the frozen criterion verbatim. AC4 is scoped " +
      "to the twenty-two classified detections, not to all twenty-three cells.",
  );
  // Guard the third, out-of-scope attribution failure so it stays visible.
  const allFalse = result.outcomes.filter((o) => !o.attributionSatisfied).map((o) => o.id);
  assert.equal(
    allFalse.length,
    3,
    `Expected exactly three outcomes with attributionSatisfied=false (two classified detections plus the SURVIVED ` +
      `cell), observed ${allFalse.length}: ${JSON.stringify(allFalse)}. Only the two classified ones bear on AC4.`,
  );
  assert.equal(
    c3.creditedDetections + c3.uncreditedDetections,
    c3.classifiedDetectedSemantic,
    "Detection accounting does not balance: credited plus uncredited must equal classified.",
  );
});

test("D1C4 no semantic gate pins fractional stator occupancy as required behaviour", () => {
  // Integrality is NOT_ESTABLISHED. A gate must not require the current non-quantizing
  // behaviour, because that would fail a future correct change that added quantization.
  const directory = path.join(root, "tests", "semantic");
  for (const name of fs.readdirSync(directory)) {
    if (!name.endsWith(".mjs")) continue;
    const source = fs.readFileSync(path.join(directory, name), "utf8");
    const assertions = source
      .split(/\r?\n/)
      .filter((line) => !line.trim().startsWith("//"))
      .join("\n");
    assert.ok(
      !/statorsFor\(\s*\d+\.\d+\s*\)/.test(assertions),
      `${name} asserts on a FRACTIONAL instrument stator occupancy. Integrality is recorded NOT_ESTABLISHED; ` +
        "pinning the current non-quantizing behaviour would convert an unestablished sub-property into an " +
        "enforced contract and would fail a future correct change that added integrality enforcement.",
    );
  }
});

test("D1C4 the declared physical stator bound remains gated", () => {
  // The correction removed only the integrality pin. The bound itself must survive.
  const source = fs.readFileSync(
    path.join(root, "tests", "semantic", "world-agent-observation-boundary.semantic.test.mjs"),
    "utf8",
  );
  assert.ok(
    /statorsFor\(20\)/.test(source) && /statorsFor\(-3\)/.test(source),
    "The 0..11 instrument stator bound is no longer gated. Removing the integrality pin must not remove the " +
      "declared physical range check.",
  );
});

test("D1C5 the SHA-256 usage inventory matches the withdrawn-claim record", () => {
  const c5 = byId("C5_SHA256_BLANKET_CLAIM_WITHDRAWN");
  const declared = new Set(c5.sha256Inventory.map((entry) => path.basename(entry.file)));

  const directory = path.join(root, "tests", "semantic");
  const observed = new Set();
  for (const name of fs.readdirSync(directory)) {
    if (!name.endsWith(".mjs")) continue;
    const source = fs.readFileSync(path.join(directory, name), "utf8");
    const code = source
      .split(/\r?\n/)
      .filter((line) => !line.trim().startsWith("//"))
      .join("\n");
    if (/createHash\(\s*["']sha256["']\s*\)/.test(code)) observed.add(name);
  }

  assert.deepEqual(
    [...observed].sort(),
    [...declared].sort(),
    "The set of semantic gates computing SHA-256 no longer matches the declared inventory in the correction " +
      "package. The blanket claim that no assertion uses SHA-256 was WITHDRAWN as false; any new digest-based " +
      "criterion must be added to that inventory rather than left undeclared.",
  );

  assert.ok(
    /never the SOLE basis/i.test(c5.replacementClaim),
    "The replacement claim no longer states the precise, scoped SHA-256 position. An earlier draft claimed the " +
      "digest assertion produced ZERO classifications, which is false: it executed and failed in " +
      "D1P01_ADVERSE_COUNTS_LAUNDERED. The defensible claim is that it was never the SOLE basis of any classification.",
  );

  // Every inventory entry must be honest about whether it was ever decisive.
  for (const item of c5.sha256Inventory) {
    assert.equal(
      item.wasSoleBasisOfAnyClassification,
      false,
      `SHA-256 inventory entry ${item.file} now claims a digest was the sole basis of a classification. That would ` +
        "make the corresponding detection hash-only, not semantic.",
    );
  }

  // The withdrawn claim also lives, frozen, in the predictions file. That must stay disclosed.
  const locations = c5.locationsOfTheWithdrawnClaim ?? [];
  assert.ok(
    locations.some((entry) => /predictions\.v1\.json/.test(entry.where)),
    "The correction record no longer discloses that the withdrawn SHA-256 claim is ALSO frozen in " +
      "audits/phase-d/d1-semantic-remediation-predictions.v1.json as the P-D1-4 rationale. That file is preserved " +
      "byte-identically, so disclosure is the only available remedy and it may not be dropped.",
  );

  // The classifier weakness behind DETECTED_BY_HASH_ONLY = 0 must remain disclosed.
  assert.ok(
    /unreachable/i.test(c5.classifierWeaknessDisclosed?.finding ?? ""),
    "The correction record no longer discloses that DETECTED_BY_HASH_ONLY is unreachable for the adverse-record " +
      "gate because of semantic-pattern precedence in the classifier.",
  );
  assert.equal(
    result.classificationCounts.DETECTED_BY_HASH_ONLY,
    0,
    "The historical hash-only count has changed. It is an immutable measurement.",
  );
});
