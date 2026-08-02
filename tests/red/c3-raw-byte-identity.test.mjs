// RED TEST C3 — raw evidence-byte identity across platforms and regeneration.
//
// EXPECTED TO FAIL at 9c3a644. This test encodes the defect, not the fix.
//
// Defect: scripts/run-observed-experiments.mjs:35 performs
//   fs.copyFileSync(datasetPath, publicEventsPath)
// across a .gitattributes eol boundary. .gitattributes:3 pins
// experiments/data/wadhwa-2022-events.json to eol=crlf; the public mirror is
// governed by the global eol=lf rule. Both resolve to ONE identical LF blob in
// the index, so:
//   - git status DOES report " M" after the copy
//   - git diff --numstat reports 0 lines (normalized blob unchanged)
//   - the corruption cannot be committed
//   - but the bytes served to the browser and hashed by the manifest ARE wrong
//
// The generator must write canonical bytes rather than copy platform-dependent
// line endings. The correct pattern already exists in-repo at
// scripts/run-science-gates.py:590 — write_text(..., newline="\n").
//
// Hash-pinned evidence should additionally be marked -text so git preserves
// exact bytes on every platform, as audits/** already is.

import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const sha256 = (p) => crypto.createHash("sha256").update(fs.readFileSync(p)).digest("hex");
const git = (args, cwd = ROOT) => execFileSync("git", args, { cwd, encoding: "utf8" }).trim();

const SOURCE = "experiments/data/wadhwa-2022-events.json";
const MIRROR = "public/wadhwa-2022-derived-events.json";

test("C3a: hash-pinned evidence artifacts carry identical eol attributes", () => {
  const attrOf = (f) => git(["check-attr", "text", "eol", "--", f]);
  const a = attrOf(SOURCE);
  const b = attrOf(MIRROR);
  const norm = (s) => s.split("\n").map((l) => l.split(": ").slice(1).join(": ")).join(" | ");
  assert.equal(
    norm(a),
    norm(b),
    `Two files carrying the SAME logical content have DIFFERENT eol attributes:\n` +
      `  ${SOURCE}: ${norm(a)}\n  ${MIRROR}: ${norm(b)}\n` +
      `Any byte-for-byte copy between them is therefore a corrupting operation.`
  );
});

test("C3b: hash-pinned evidence has one on-disk identity, not two", () => {
  const rawSource = git(["hash-object", "--no-filters", "--", SOURCE]);
  const rawMirror = git(["hash-object", "--no-filters", "--", MIRROR]);
  const idxSource = git(["hash-object", "--", SOURCE]);
  const idxMirror = git(["hash-object", "--", MIRROR]);
  assert.equal(idxSource, idxMirror, "precondition: the two files share one index blob");
  assert.equal(
    rawSource,
    rawMirror,
    `One logical artifact has TWO on-disk identities:\n` +
      `  ${SOURCE}: raw ${rawSource} (${fs.statSync(path.join(ROOT, SOURCE)).size} bytes)\n` +
      `  ${MIRROR}: raw ${rawMirror} (${fs.statSync(path.join(ROOT, MIRROR)).size} bytes)\n` +
      `Both normalize to index blob ${idxSource}. An external verifier who downloads ` +
      `the audit manifest and the served file cannot reconcile their SHA-256 values.`
  );
});

test("C3c: hash-pinned evidence is protected from eol filtering (-text)", () => {
  const out = git(["check-attr", "text", "--", SOURCE, MIRROR]);
  const unset = out.split("\n").every((l) => l.endsWith(": unset"));
  assert.ok(
    unset,
    `Hash-pinned evidence is still subject to eol filtering:\n${out}\n` +
      `Mark these paths -text (as audits/** already is) so git preserves exact bytes ` +
      `on every platform once the generator emits canonical LF.`
  );
});

test("C3d: raw evidence bytes are stable under core.autocrlf true, false and input", (t) => {
  const digests = {};
  for (const mode of ["true", "false", "input"]) {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), `uni-c3-${mode}-`));
    try {
      execFileSync("git", ["clone", "--quiet", "--no-hardlinks", "--config", `core.autocrlf=${mode}`, ROOT, dir], { encoding: "utf8" });
      execFileSync("git", ["checkout", "--quiet", "9c3a644e4b57e8ac27f925dcec84222463063aa1"], { cwd: dir, encoding: "utf8" });
      digests[mode] = {
        source: sha256(path.join(dir, SOURCE)),
        mirror: sha256(path.join(dir, MIRROR)),
        sourceBytes: fs.statSync(path.join(dir, SOURCE)).size,
        mirrorBytes: fs.statSync(path.join(dir, MIRROR)).size,
      };
      t.diagnostic(`autocrlf=${mode}: source ${digests[mode].sourceBytes}B ${digests[mode].source.slice(0, 12)} | mirror ${digests[mode].mirrorBytes}B ${digests[mode].mirror.slice(0, 12)}`);
    } finally {
      fs.rmSync(dir, { recursive: true, force: true });
    }
  }
  const sourceSet = new Set(Object.values(digests).map((d) => d.source));
  const mirrorSet = new Set(Object.values(digests).map((d) => d.mirror));
  assert.equal(sourceSet.size, 1, `${SOURCE} materializes with ${sourceSet.size} distinct digests across autocrlf settings; a manifest pin cannot be platform-independent.`);
  assert.equal(mirrorSet.size, 1, `${MIRROR} materializes with ${mirrorSet.size} distinct digests across autocrlf settings.`);
});

test("C3e: regenerating the observed experiment does not change the served mirror", (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "uni-c3-regen-"));
  try {
    // Deliberately clones the CURRENT HEAD rather than the audited commit. An
    // earlier version pinned 9c3a644, which meant this test could never turn
    // green once the defect was fixed - it was a historical record, not a gate.
    execFileSync("git", ["clone", "--quiet", "--no-hardlinks", ROOT, dir], { encoding: "utf8" });
    const before = sha256(path.join(dir, MIRROR));
    execFileSync(process.execPath, ["scripts/run-observed-experiments.mjs"], { cwd: dir, encoding: "utf8", stdio: "pipe" });
    const after = sha256(path.join(dir, MIRROR));
    const numstat = execFileSync("git", ["diff", "--numstat", "--", MIRROR], { cwd: dir, encoding: "utf8" }).trim();
    t.diagnostic(`before ${before.slice(0, 16)} after ${after.slice(0, 16)}`);
    t.diagnostic(`git diff --numstat after regeneration: ${JSON.stringify(numstat)} (empty means git cannot see it)`);
    assert.equal(
      before,
      after,
      `Regeneration changed the served mirror's bytes. run-observed-experiments.mjs:35 ` +
        `copies eol=crlf source bytes over the eol=lf mirror. git diff reported ` +
        `${numstat === "" ? "NOTHING" : numstat}, so the corruption is invisible to a content diff.`
    );
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});
