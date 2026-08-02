// RED TEST C2 — source-byte gates.
//
// EXPECTED TO FAIL at 9c3a644. This test encodes the defect, not the fix.
//
// Claim under test: X01_SOURCE_INTEGRITY reports PASS in the generated
// cross-study report, asserting integrity over 12 local artifacts and a
// 4,085,227,742-byte external archive.
//
// Observed: scripts/run-cross-study-parity.py:360-363 computes X01 from
//   all(item["verified"]) and cacheVerification["status"] == "PASS"
// which are JSON literals read out of the corpus file the gate is meant to
// validate. The gate performs zero filesystem reads of the artifacts, so its
// result is invariant to whether any of them exist.
//
// A frozen "verified": true field is an EVIDENCE CLAIM about a past
// verification. It is not current verification.
//
// This test specifies the gate SPLIT the directive requires:
//   source declaration integrity | required local-byte availability |
//   current-byte hash verification | large-archive structural verification |
//   parser/input binding
//
// A source-byte gate must be PASS only after current files were opened and
// verified; NOT RUN or BLOCKED when required files are absent; FAIL when
// sizes, hashes, archive structure or parser binding disagree.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));

const report = readJson(path.join(ROOT, "experiments/results/cross-study-parity-report.json"));
const corpus = readJson(path.join(ROOT, "experiments/data/cross-study-motor-evidence.json"));
const CACHE = path.join(ROOT, "experiments/upstream-cache");
const artifacts = corpus.sourceIntegrity.localArtifacts;
const gate = (idPrefix) => report.gates.find((g) => g.id.startsWith(idPrefix));

test("C2a: a NOT_RUN status exists in the gate vocabulary", () => {
  const statuses = new Set(report.gates.map((g) => g.status));
  assert.ok(
    statuses.has("NOT_RUN") || statuses.has("EXTERNAL_VALIDATION_REQUIRED"),
    `CLAUDE.md:119-121 requires an absent dataset to be marked BLOCKED / NOT RUN / ` +
      `EXTERNAL VALIDATION REQUIRED. Vocabulary in use is [${[...statuses].join(", ")}]. ` +
      `The honest status is currently unrepresentable.`
  );
});

test("C2b: a status validator constrains gate status strings", () => {
  const candidates = [
    "experiments/gate-status-vocabulary.v1.json",
    "lib/gate-status.js",
    "scripts/gate_status.py",
  ].map((p) => path.join(ROOT, p));
  assert.ok(
    candidates.some((p) => fs.existsSync(p)),
    "No single source of truth constrains gate status strings. A typo'd status " +
      "would render unstyled and unglossed in the UI and fail no test."
  );
});

test("C2c: X01 reports the number of artifacts it actually opened", () => {
  const x01 = gate("X01");
  assert.ok(x01, "X01 gate not found");
  const ev = x01.evidence ?? {};
  assert.ok(
    Object.prototype.hasOwnProperty.call(ev, "artifactsHashed") &&
      Object.prototype.hasOwnProperty.call(ev, "bytesHashed"),
    `X01 evidence must report artifactsHashed and bytesHashed so a reader can tell ` +
      `how much was actually verified. Present keys: [${Object.keys(ev).join(", ")}]`
  );
});

test("C2d: X01 is NOT PASS while the artifacts it claims to verify are absent", () => {
  const present = artifacts.filter((a) => fs.existsSync(path.join(ROOT, path.basename(a.cachePath ?? a.path))) ||
    fs.existsSync(path.join(ROOT, a.cachePath ?? a.path)));
  const x01 = gate("X01");
  if (present.length === artifacts.length) {
    assert.equal(x01.status, "PASS", "all artifacts present, so PASS is expected");
    return;
  }
  assert.notEqual(
    x01.status,
    "PASS",
    `X01 reports PASS while ${artifacts.length - present.length} of ${artifacts.length} declared ` +
      `local artifacts are absent from ${path.relative(ROOT, CACHE)}. A gate asserting source ` +
      `integrity must not pass over bytes it never opened.`
  );
});

test("C2e: frozen 'verified' literals are not the basis of the gate result", () => {
  const allFrozenTrue = artifacts.every((a) => a.verified === true);
  const x01 = gate("X01");
  const anyPresent = artifacts.some((a) => fs.existsSync(path.join(ROOT, a.cachePath ?? a.path)));
  assert.ok(
    !(allFrozenTrue && x01.status === "PASS" && !anyPresent),
    "Every localArtifacts[].verified is frozen true, X01 is PASS, and no artifact is " +
      "present on disk. The gate result is therefore derived from evidence claims " +
      "rather than from current verification."
  );
});

// Cache-state matrix the directive requires. These are specifications for the
// remediated gate; they cannot pass against a gate that never reads the filesystem.
for (const state of ["empty", "partial", "corrupted", "substituted"]) {
  test(`C2f[${state}]: the generated report changes when the cache is ${state}`, (t) => {
    t.skip(
      `NOT RUN. Requires re-running scripts/run-cross-study-parity.py against a ${state} ` +
        `cache in an isolated worktree and diffing the emitted report. Phase A established ` +
        `that the empty and complete states produce a BYTE-IDENTICAL report ` +
        `(sha256 bd3838c40b8d256342427e59c615679e0b004d757f21093ef640079a591ee384 in both), ` +
        `so this family is expected to fail for every state until X01 reads bytes.`
    );
  });
}
