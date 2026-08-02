import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { runObservedExperiment } from "../lib/observed-experiment.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const protocolPath = path.join(root, "experiments", "preregistration.v1.json");
const datasetPath = path.join(root, "experiments", "data", "wadhwa-2022-events.json");
const reportPath = path.join(root, "experiments", "results", "observed-experiment-report.json");
const publicPath = path.join(root, "public", "observed-experiment-report.json");
const publicProtocolPath = path.join(root, "public", "observed-experiment-preregistration.json");
const publicEventsPath = path.join(root, "public", "wadhwa-2022-derived-events.json");
const auditPath = path.join(root, "experiments", "results", "audit-manifest.json");
const publicAuditPath = path.join(root, "public", "observed-experiment-audit.json");
const analysisPath = path.join(root, "lib", "observed-experiment.js");
const runnerPath = fileURLToPath(import.meta.url);

const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
const protocol = JSON.parse(fs.readFileSync(protocolPath, "utf8"));
const dataset = JSON.parse(fs.readFileSync(datasetPath, "utf8"));
const report = runObservedExperiment(dataset, protocol, {
  protocolSha256: sha256(protocolPath),
  derivedEventsSha256: sha256(datasetPath),
  analysisCodeSha256: sha256(analysisPath),
  runnerSha256: sha256(runnerPath),
  rawSourceSha256: dataset.source.observedRawSha256,
  rawSourceCommit: dataset.source.commit,
});
const serialized = `${JSON.stringify(report, null, 2)}\n`;
fs.mkdirSync(path.dirname(reportPath), { recursive: true });
fs.writeFileSync(reportPath, serialized);
fs.writeFileSync(publicPath, serialized);
fs.copyFileSync(protocolPath, publicProtocolPath);
// The derived-event artifact is pinned by SHA-256 in lib/walkthrough.js and in
// experiments/walkthrough-evidence-manifest.v1.json, and .gitattributes gives the
// source eol=crlf while this served mirror is eol=lf. A raw byte copy therefore
// corrupts the mirror on every regeneration. Write canonical LF instead, matching
// the pattern already used in scripts/run-science-gates.py.
fs.writeFileSync(publicEventsPath, fs.readFileSync(datasetPath, "utf8").replace(/\r\n/g, "\n"));
const audit = {
  schema: "uni.flagellum.experiment-audit/1.0.0",
  protocolId: protocol.protocolId,
  runId: report.runId,
  source: {
    repository: dataset.source.repository,
    commit: dataset.source.commit,
    rawPath: dataset.source.rawPath,
    rawSha256: dataset.source.observedRawSha256,
  },
  artifacts: {
    protocol: { path: "experiments/preregistration.v1.json", sha256: sha256(protocolPath) },
    derivedEvents: { path: "experiments/data/wadhwa-2022-events.json", sha256: sha256(datasetPath) },
    analysisCode: { path: "lib/observed-experiment.js", sha256: sha256(analysisPath) },
    runner: { path: "scripts/run-observed-experiments.mjs", sha256: sha256(runnerPath) },
    report: { path: "experiments/results/observed-experiment-report.json", sha256: crypto.createHash("sha256").update(serialized).digest("hex") },
  },
  deterministicReplay: "Run the analysis twice from identical protocol, event artifact, and code identities; the report SHA-256 must be identical.",
};
const serializedAudit = `${JSON.stringify(audit, null, 2)}\n`;
fs.writeFileSync(auditPath, serializedAudit);
fs.writeFileSync(publicAuditPath, serializedAudit);
console.log(JSON.stringify({
  runId: report.runId,
  reportSha256: crypto.createHash("sha256").update(serialized).digest("hex"),
  auditSha256: crypto.createHash("sha256").update(serializedAudit).digest("hex"),
  cohort: report.cohort,
  claims: report.claims,
}, null, 2));
