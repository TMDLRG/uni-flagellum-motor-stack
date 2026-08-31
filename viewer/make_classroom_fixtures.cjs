#!/usr/bin/env node
// make_classroom_fixtures.cjs — capture the /api/classroom and /api/models payloads as COMMITTED
// FIXTURES, so the vendored public copies of the classroom and models pages can render real
// recorded engine output instead of a dead fetch — and say RECORDED while doing it.
//
// WHAT A FIXTURE IS HERE, PRECISELY: the same aggregation the live viewer serves, built through
// viewer/api_payloads.cjs (one definition, two consumers), read via `git show HEAD:<path>` so the
// bytes are THE COMMIT'S bytes — a dirty working tree cannot leak into a file that names a commit.
// Instead of the live handler's `now`, a fixture carries a `fixture` provenance block: recorded,
// the commit it was read at, when, and by what. The pages key their honesty on that block: a
// response with `fixture.recorded` renders a RECORDED stamp, never the live one.
//
// REFUSALS, because a fixture is a claim:
//   - refuses if any source artifact is MODIFIED in the working tree (the fixture would then
//     describe bytes nobody has committed);
//   - refuses if any source artifact is unreadable at HEAD (an aggregation of nulls is not a
//     recording, it is an empty box with a provenance label);
//   - refuses if the serialized output matches any pattern the public site's publish gate would
//     refuse (machine paths, private addresses) — listed by name, never scrubbed silently.
//
// Output: docs/classroom-assets/api-classroom.fixture.json and api-models.fixture.json — inside
// the classroom asset set ON PURPOSE: that directory is already enumerated, byte-verified and
// served at /assets/classroom/ by both the live viewer (STATIC map in bio_view.cjs) and the
// public site's rooms pipeline, so no new path, rewrite or proxy is needed anywhere.
//
//   Run:  node viewer/make_classroom_fixtures.cjs
"use strict";

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execFileSync } = require("child_process");
const { make, SOURCES } = require("./api_payloads.cjs");

const ROOT = path.resolve(__dirname, "..");
const git = (args) => execFileSync("git", args, { cwd: ROOT, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });

const head = git(["rev-parse", "HEAD"]).trim();
const headUtc = git(["show", "-s", "--format=%cI", "HEAD"]).trim();

// ── refusal 1: no source artifact may be dirty ───────────────────────────────────────────────────
const allSources = [...new Set([...SOURCES.classroom, ...SOURCES.models])];
const dirty = git(["status", "--porcelain", "--", ...allSources]).trim();
if (dirty) {
  console.error("REFUSED — source artifact(s) modified in the working tree; a fixture names a commit and must capture that commit's bytes:");
  console.error(dirty);
  process.exit(1);
}

// ── read through the commit, not the tree ────────────────────────────────────────────────────────
const gitRead = (p) => { try { return git(["show", `HEAD:${p}`]); } catch (e) { return null; } };
for (const p of allSources) {
  if (gitRead(p) === null) { console.error(`REFUSED — ${p} unreadable at HEAD; an aggregation of nulls is not a recording.`); process.exit(1); }
}
const payloads = make(gitRead);

const stamp = (kind) => ({
  recorded: true,
  kind,
  generated_by: "viewer/make_classroom_fixtures.cjs",
  source_commit: head,
  source_commit_utc: headUtc,
  generated_utc: new Date().toISOString(),
  note: "The same artifacts the live viewer aggregates, captured at the commit named — recorded engine output, not a live read. A page that receives this block must say RECORDED, never live.",
});

const out = [
  { file: "docs/classroom-assets/api-classroom.fixture.json", body: { fixture: stamp("classroom"), ...payloads.classroomPayload() } },
  { file: "docs/classroom-assets/api-models.fixture.json", body: { fixture: stamp("models"), ...payloads.modelsPayload() } },
];

// ── refusal 3: nothing the publish gate would refuse ─────────────────────────────────────────────
const FORBIDDEN = [/[A-Za-z]:\\+Users/i, /[A-Za-z]:\/Users/i, /127\.0\.0\.1/, /192\.168\./, /\b\w+\.local\b/, /\bmpolz\b/i];
for (const o of out) {
  const s = JSON.stringify(o.body);
  const hits = FORBIDDEN.filter((re) => re.test(s));
  if (hits.length) {
    console.error(`REFUSED — ${o.file} would carry pattern(s) the publish gate refuses: ${hits.map(String).join(" ")}`);
    console.error("Nothing is scrubbed silently; the value must leave the SOURCE artifact first.");
    process.exit(1);
  }
}

for (const o of out) {
  const abs = path.join(ROOT, o.file);
  const bytes = JSON.stringify(o.body, null, 1) + "\n";
  fs.writeFileSync(abs, bytes);
  console.log(`wrote ${o.file}  ${bytes.length} bytes  sha256 ${crypto.createHash("sha256").update(bytes).digest("hex").slice(0, 16)}  @ ${head.slice(0, 12)}`);
}
console.log("fixtures capture HEAD; commit them, then advance the public rooms pin to that commit.");
