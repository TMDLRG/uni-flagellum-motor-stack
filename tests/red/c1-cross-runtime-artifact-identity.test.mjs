// RED TEST C1 — cross-runtime artifact identity.
//
// EXPECTED TO FAIL at 9c3a644. This test encodes the defect, not the fix.
//
// Claim under test: experiments/results/audit-manifest.json:53 —
//   "Run the analysis twice from identical protocol, event artifact, and code
//    identities; the report SHA-256 must be identical."
//
// Observed: holding all three identities constant and varying only the
// JavaScript engine changes the report SHA-256 and therefore runId.
//
// ROOT CAUSE (localized, audits/phase-a):
//   V8's Math.pow / ** is not bit-reproducible across versions. At the fitted
//   Weibull parameters (shape 0.625088844276203, scale 0.6996038164387606),
//   418 of 4000 sampled evaluations differ by 1 ULP between V8 12.4 and 14.1.
//   lib/observed-experiment.js:178 evaluates (y / scale) ** shape, so Weibull
//   survival and log-scores inherit the difference, which propagates into the
//   paired advantage mean, the bootstrap interval, and finally runId.
//
//   ECMA-262 permits Math.pow to be implementation-approximated. Bit-identical
//   cross-engine results are therefore NOT guaranteed by the language, and
//   raising the engines floor cannot make this contract true in general.
//
// Run with a second runtime available:
//   UNI_ALT_NODE=/path/to/other/node node --test tests/red/c1-cross-runtime-artifact-identity.test.mjs

import test from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const ALT = process.env.UNI_ALT_NODE;
// On Windows an absolute path is not a valid ESM specifier; it must be a file:// URL.
const IMPL_URL = pathToFileURL(path.join(ROOT, "lib", "observed-experiment.js")).href;

const HARNESS = `
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { runObservedExperiment } from ${JSON.stringify(IMPL_URL)};
const ROOT = ${JSON.stringify(ROOT.replace(/\\\\/g, "/"))};
const sha256 = (f) => crypto.createHash("sha256").update(fs.readFileSync(f)).digest("hex");
const P = (...a) => path.join(ROOT, ...a);
const protocolPath = P("experiments", "preregistration.v1.json");
const datasetPath = P("experiments", "data", "wadhwa-2022-events.json");
const dataset = JSON.parse(fs.readFileSync(datasetPath, "utf8"));
const report = runObservedExperiment(dataset, JSON.parse(fs.readFileSync(protocolPath, "utf8")), {
  protocolSha256: sha256(protocolPath),
  derivedEventsSha256: sha256(datasetPath),
  analysisCodeSha256: sha256(P("lib", "observed-experiment.js")),
  runnerSha256: sha256(P("scripts", "run-observed-experiments.mjs")),
  rawSourceSha256: dataset.source.observedRawSha256,
  rawSourceCommit: dataset.source.commit,
});
const serialized = JSON.stringify(report, null, 2) + "\\n";
console.log(JSON.stringify({
  node: process.version,
  v8: process.versions.v8,
  runId: report.runId,
  reportSha256: crypto.createHash("sha256").update(serialized).digest("hex"),
  weibullSurvival28: report.curves?.survival?.[28]?.weibull ?? null,
}));
`;

function runUnder(nodeBin) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "uni-c1-"));
  const file = path.join(dir, "harness.mjs");
  fs.writeFileSync(file, HARNESS);
  try {
    return JSON.parse(execFileSync(nodeBin, [file], { encoding: "utf8" }));
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

test("C1: report SHA-256 is identical across JavaScript engines given identical protocol, data and code identities", (t) => {
  if (!ALT) {
    // Absence of a second runtime is NOT a pass. Skip loudly.
    t.skip("UNI_ALT_NODE not set — a second Node runtime is required. NOT RUN, not passing.");
    return;
  }
  const here = runUnder(process.execPath);
  const there = runUnder(ALT);

  t.diagnostic(`this runtime : ${here.node} v8=${here.v8} runId=${here.runId}`);
  t.diagnostic(`other runtime: ${there.node} v8=${there.v8} runId=${there.runId}`);

  assert.equal(
    here.reportSha256,
    there.reportSha256,
    `report SHA-256 differs across engines (${here.node}/v8 ${here.v8} vs ${there.node}/v8 ${there.v8}). ` +
      `The audit-manifest determinism claim names only protocol, event artifact and code identities; ` +
      `runtime identity is an undeclared input.`
  );
  assert.equal(here.runId, there.runId, "runId differs across engines");
});

test("C1a: Math.pow is bit-reproducible across engines at the fitted Weibull parameters", (t) => {
  if (!ALT) {
    t.skip("UNI_ALT_NODE not set — NOT RUN, not passing.");
    return;
  }
  const probe = `
    const shape = 0.625088844276203, scale = 0.6996038164387606;
    const out = [];
    for (let i = 1; i <= 4000; i++) out.push(((i * 0.001) / scale) ** shape);
    console.log(require("node:crypto").createHash("sha256").update(out.map((v) => v.toExponential(20)).join(",")).digest("hex"));
  `;
  const run = (bin) => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "uni-c1p-"));
    const f = path.join(dir, "p.cjs");
    fs.writeFileSync(f, probe);
    try { return execFileSync(bin, [f], { encoding: "utf8" }).trim(); } finally { fs.rmSync(dir, { recursive: true, force: true }); }
  };
  const a = run(process.execPath);
  const b = run(ALT);
  t.diagnostic(`pow digest here : ${a}`);
  t.diagnostic(`pow digest there: ${b}`);
  assert.equal(a, b, "Math.pow results differ across engines — ECMA-262 permits implementation-approximated results, so this cannot be fixed by pinning a floor version alone.");
});
