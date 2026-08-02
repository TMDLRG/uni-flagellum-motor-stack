#!/usr/bin/env node

/**
 * D1 semantic remediation replay runner.
 *
 * Measures whether the frozen Phase-C semantic gate command detects the twenty-two
 * corruptions frozen in audits/phase-d/d1-semantic-remediation-protocol.v1.json.
 *
 * This runner is a SIBLING of audits/phase-c/tools/run-blind-mutation-battery.mjs.
 * The Phase-C runner is immutable historical evidence and is not modified. This one
 * differs deliberately in four ways:
 *
 *   1. The replay base commit is supplied at execution time (--base-commit), because
 *      the D1 implementation commit does not exist when the protocol is frozen.
 *   2. It admits more than twelve mutations.
 *   3. It records ATTRIBUTION: which test actually produced the matching diagnostic,
 *      so a detection cannot be credited to an unrelated failing test.
 *   4. It verifies Phase-C evidence byte-identity before and after execution.
 *
 * It performs no network access and installs no dependencies. Every declared command
 * runs on Node builtins, repository sources, and the system Python.
 */

import { createHash } from "node:crypto";
import { execFileSync, spawnSync } from "node:child_process";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  realpathSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, isAbsolute, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const SCRIPT_PATH = fileURLToPath(import.meta.url);
const REPOSITORY_ROOT = resolve(dirname(SCRIPT_PATH), "../../..");
const DEFAULT_PROTOCOL_PATH = join(
  REPOSITORY_ROOT,
  "audits/phase-d/d1-semantic-remediation-protocol.v1.json",
);
const PRESERVATION_BASELINE_PATH = join(
  REPOSITORY_ROOT,
  "audits/phase-d/phase-c-preservation-baseline.v1.json",
);
const RESULT_REPOSITORY_PATH = join(
  REPOSITORY_ROOT,
  "audits/phase-d/d1-semantic-remediation-result.v1.json",
);
const RESULT_BASENAME = "d1-semantic-remediation-result.v1.json";
const EVIDENCE_BASENAME = "d1-semantic-remediation-evidence-manifest.v1.json";

const HASH_ONLY_PATTERNS = [
  /\bsha-?256\b/i,
  /\bhash(?:es|ed)?\b/i,
  /changed bytes?/i,
  /byte[- ]identity/i,
  /snapshot/i,
  /run[ -]?id/i,
  /artifact inequality/i,
  /generic artifact identity/i,
];

function usage(message = null) {
  if (message) process.stderr.write(`${message}\n\n`);
  process.stderr.write(
    "Usage:\n" +
      "  node audits/phase-d/tools/run-d1-semantic-replay.mjs --preflight --base-commit <sha>\n" +
      "  node audits/phase-d/tools/run-d1-semantic-replay.mjs --execute --base-commit <sha> --scratch-root <absolute-empty-path> [--cleanup-clones]\n",
  );
  process.exit(message ? 2 : 0);
}

function parseArguments(argv) {
  const options = {
    mode: null,
    protocolPath: DEFAULT_PROTOCOL_PATH,
    baseCommit: null,
    scratchRoot: null,
    cleanupClones: false,
  };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--preflight" || argument === "--dry-run") {
      if (options.mode) usage("Choose exactly one mode.");
      options.mode = "preflight";
    } else if (argument === "--execute") {
      if (options.mode) usage("Choose exactly one mode.");
      options.mode = "execute";
    } else if (argument === "--protocol") {
      options.protocolPath = resolve(argv[++index] ?? usage("--protocol requires a path."));
    } else if (argument === "--base-commit") {
      options.baseCommit = argv[++index] ?? usage("--base-commit requires a commit-ish.");
    } else if (argument === "--scratch-root") {
      options.scratchRoot = argv[++index] ?? usage("--scratch-root requires a path.");
    } else if (argument === "--cleanup-clones") {
      options.cleanupClones = true;
    } else if (argument === "--help" || argument === "-h") {
      usage();
    } else {
      usage(`Unknown argument: ${argument}`);
    }
  }
  if (!options.mode) usage("A mode is required.");
  if (!options.baseCommit) usage("A --base-commit is required in both modes.");
  if (options.mode === "execute" && !options.scratchRoot) {
    usage("Execution requires an explicit --scratch-root.");
  }
  if (options.mode === "preflight" && options.scratchRoot) {
    usage("Preflight does not accept or create a scratch root.");
  }
  return options;
}

function sha256(bytes) {
  return createHash("sha256").update(bytes).digest("hex");
}

function canonicalJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function git(args, cwd = REPOSITORY_ROOT, encoding = "utf8") {
  return execFileSync("git", args, {
    cwd,
    encoding,
    maxBuffer: 128 * 1024 * 1024,
    windowsHide: true,
  });
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8"));
}

function countOccurrences(haystack, needle) {
  if (!needle) return 0;
  let count = 0;
  let offset = 0;
  for (;;) {
    const index = haystack.indexOf(needle, offset);
    if (index < 0) return count;
    count += 1;
    offset = index + needle.length;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

// ---------------------------------------------------------------------------
// Validation
// ---------------------------------------------------------------------------

function validateProtocol(protocol) {
  assert(
    protocol.schema === "uni.flagellum.d1-semantic-remediation-protocol/1.0.0",
    "Unexpected protocol schema.",
  );
  assert(Array.isArray(protocol.mutations), "mutations must be an array.");
  assert(protocol.mutations.length >= 20, "D1 requires at least twenty mutations (ten exact, ten alternate).");
  assert(Array.isArray(protocol.allowedCommands) && protocol.allowedCommands.length > 0, "allowedCommands missing.");
  const allowed = new Set(protocol.allowedCommands);

  const ids = new Set();
  const exactByProperty = new Map();
  const alternateByProperty = new Map();

  for (const mutation of protocol.mutations) {
    assert(!ids.has(mutation.id), `Duplicate mutation id: ${mutation.id}`);
    ids.add(mutation.id);
    assert(typeof mutation.propertyId === "string" && mutation.propertyId.length > 0, `${mutation.id}: propertyId missing.`);
    assert(
      ["EXACT_PHASE_C_REPLAY", "ALTERNATE_FORM", "ADVERSE_RECORD_ATTACK"].includes(mutation.class),
      `${mutation.id}: invalid class.`,
    );
    assert(typeof mutation.targetPath === "string" && mutation.targetPath.length > 0, `${mutation.id}: targetPath missing.`);
    assert(!isAbsolute(mutation.targetPath), `${mutation.id}: targetPath must be repository-relative.`);
    assert(!mutation.targetPath.includes(".."), `${mutation.id}: targetPath may not traverse upward.`);
    assert(/^[0-9a-f]{64}$/.test(mutation.preMutationSha256), `${mutation.id}: invalid raw digest.`);
    assert(mutation.patch?.encoding === "utf8", `${mutation.id}: only UTF-8 text patches are supported.`);
    assert(mutation.patch.expectedOccurrences === 1, `${mutation.id}: exact patch must require one occurrence.`);
    assert(mutation.patch.before !== mutation.patch.after, `${mutation.id}: before and after text are identical.`);
    assert(Array.isArray(mutation.regenerationCommands), `${mutation.id}: regenerationCommands missing.`);
    assert(Array.isArray(mutation.gateCommands) && mutation.gateCommands.length > 0, `${mutation.id}: gateCommands missing.`);
    assert(Array.isArray(mutation.baselineCommands), `${mutation.id}: baselineCommands missing.`);
    for (const command of [...mutation.regenerationCommands, ...mutation.gateCommands, ...mutation.baselineCommands]) {
      assert(typeof command.id === "string" && typeof command.command === "string", `${mutation.id}: malformed command.`);
      assert(allowed.has(command.command), `${mutation.id}: command outside the frozen allowlist: ${command.command}`);
    }
    assert(
      ["DETECTED_SEMANTIC", "DETECTED_BY_HASH_ONLY", "SURVIVED", "NOT_RUN", "INCONCLUSIVE"].includes(
        mutation.predictedClassification,
      ),
      `${mutation.id}: invalid predicted classification.`,
    );
    assert(
      typeof mutation.expectedFailingTest === "string" && mutation.expectedFailingTest.length > 0,
      `${mutation.id}: expectedFailingTest missing; attribution cannot be measured.`,
    );
    assert(
      Array.isArray(mutation.semanticFailurePatterns) && mutation.semanticFailurePatterns.length > 0,
      `${mutation.id}: semantic patterns missing.`,
    );
    for (const pattern of mutation.semanticFailurePatterns) new RegExp(pattern, "i");

    if (mutation.class === "EXACT_PHASE_C_REPLAY") {
      exactByProperty.set(mutation.propertyId, (exactByProperty.get(mutation.propertyId) ?? 0) + 1);
    } else if (mutation.class === "ALTERNATE_FORM") {
      alternateByProperty.set(mutation.propertyId, (alternateByProperty.get(mutation.propertyId) ?? 0) + 1);
    }
  }

  // Plan section 1.4: at least one structurally different corruption per property.
  for (const propertyId of exactByProperty.keys()) {
    assert(
      (alternateByProperty.get(propertyId) ?? 0) >= 1,
      `Property ${propertyId} has no alternate-form corruption; plan section 1.4 requires at least one.`,
    );
  }
}

function verifyPhaseCPreservation(stage) {
  const baseline = readJson(PRESERVATION_BASELINE_PATH);
  assert(
    baseline.schema === "uni.flagellum.phase-c-preservation-baseline/1.0.0",
    "Unexpected preservation baseline schema.",
  );
  const drift = [];
  for (const entry of baseline.files) {
    const absolute = join(REPOSITORY_ROOT, ...entry.path.split("/"));
    if (!existsSync(absolute)) {
      drift.push({ path: entry.path, expected: entry.sha256, actual: "MISSING" });
      continue;
    }
    const actual = sha256(readFileSync(absolute));
    if (actual !== entry.sha256) drift.push({ path: entry.path, expected: entry.sha256, actual });
  }
  // A newly ADDED file under audits/phase-c/ is also drift: the battery is frozen.
  const present = new Set();
  (function visit(dir) {
    for (const entry of readdirSync(dir, { withFileTypes: true })) {
      const p = join(dir, entry.name);
      if (entry.isDirectory()) visit(p);
      else if (entry.isFile()) present.add(relative(REPOSITORY_ROOT, p).split(sep).join("/"));
    }
  })(join(REPOSITORY_ROOT, "audits/phase-c"));
  const declared = new Set(baseline.files.map((f) => f.path));
  for (const path of present) {
    if (!declared.has(path)) drift.push({ path, expected: "ABSENT", actual: "ADDED" });
  }
  assert(
    drift.length === 0,
    `Phase-C evidence changed at ${stage}. The historical adverse battery is immutable. Drift: ${JSON.stringify(drift)}`,
  );
  return { stage, fileCount: baseline.files.length, unchanged: true };
}

function firstIntroducingCommit(path) {
  const output = git(["log", "--diff-filter=A", "--format=%H", "--", path]).trim();
  if (!output) return null;
  const commits = output.split(/\r?\n/).filter(Boolean);
  return commits[commits.length - 1];
}

function resolveBaseCommit(baseCommitish) {
  const resolved = git(["rev-parse", `${baseCommitish}^{commit}`]).trim();
  assert(/^[0-9a-f]{40}$/.test(resolved), "Base commit did not resolve to a full SHA.");
  return resolved;
}

function verifyPredictionAncestry(protocolPath, baseCommit) {
  // CORRECTION 1B. This function previously hardcoded the v1 protocol path, so the
  // --protocol flag was ignored for ANCESTRY as well as for provenance. That was
  // load-bearing, not cosmetic: the addendum protocol entered history AT the replay
  // base commit, and the strictness assertion below would have ABORTED the run had it
  // been evaluated against the protocol that actually governed it. The ancestry target
  // is now derived from the protocol actually supplied.
  const protocolRelative = relative(REPOSITORY_ROOT, resolve(protocolPath)).split(sep).join("/");
  const predictionCommit = firstIntroducingCommit("audits/phase-d/d1-semantic-remediation-predictions.v1.json");
  const protocolCommit = firstIntroducingCommit(protocolRelative);
  assert(predictionCommit, "The D1 predictions file has never been committed; prospectivity cannot be established.");
  assert(protocolCommit, `The protocol ${protocolRelative} has never been committed; prospectivity cannot be established.`);
  for (const [label, commit] of [["predictions", predictionCommit], ["protocol", protocolCommit]]) {
    assert(commit !== baseCommit, `The D1 ${label} file entered history in the replay base commit itself; ancestry is not STRICT.`);
    let isAncestor = true;
    try {
      git(["merge-base", "--is-ancestor", commit, baseCommit]);
    } catch {
      isAncestor = false;
    }
    assert(isAncestor, `The D1 ${label} commit ${commit} is not an ancestor of the replay base commit ${baseCommit}.`);
  }
  return { predictionCommit, protocolCommit, protocolPath: protocolRelative, strictAncestry: true };
}

function baseBlob(targetPath, baseCommit) {
  return git(["show", `${baseCommit}:${targetPath}`], REPOSITORY_ROOT, null);
}

function validateFrozenPatch(mutation, baseCommit) {
  const bytes = baseBlob(mutation.targetPath, baseCommit);
  assert(
    sha256(bytes) === mutation.preMutationSha256,
    `${mutation.id}: target digest at the replay base commit does not match the frozen preMutationSha256. ` +
      `This means the implementation commit CHANGED a mutation target, which the protocol forbids.`,
  );
  const text = bytes.toString("utf8");
  assert(countOccurrences(text, mutation.patch.before) === 1, `${mutation.id}: before text does not occur exactly once.`);
  assert(countOccurrences(text, mutation.patch.after) === 0, `${mutation.id}: after text already exists in the base target.`);
  const patched = text.replace(mutation.patch.before, mutation.patch.after);
  assert(patched !== text, `${mutation.id}: patch is equivalent at the byte level.`);
  return {
    targetBytes: bytes.length,
    preMutationSha256: sha256(bytes),
    postMutationSha256: sha256(Buffer.from(patched, "utf8")),
  };
}

// ---------------------------------------------------------------------------
// Execution
// ---------------------------------------------------------------------------

function ensureEmptyScratchRoot(requestedPath) {
  assert(isAbsolute(requestedPath), "--scratch-root must be an absolute path.");
  const scratchRoot = resolve(requestedPath);
  const relativeToRepository = relative(REPOSITORY_ROOT, scratchRoot);
  assert(
    relativeToRepository.startsWith("..") && !isAbsolute(relativeToRepository),
    "Scratch root must be outside the primary checkout.",
  );
  if (existsSync(scratchRoot)) {
    assert(statSync(scratchRoot).isDirectory(), "Scratch root exists and is not a directory.");
    assert(readdirSync(scratchRoot).length === 0, "Scratch root must be absent or empty.");
  } else {
    mkdirSync(scratchRoot, { recursive: true });
  }
  return realpathSync(scratchRoot);
}

function runCommand(command, cwd, logDirectory, ordinal) {
  const startedAt = new Date().toISOString();
  const result = spawnSync(command.command, {
    cwd,
    encoding: "utf8",
    maxBuffer: 128 * 1024 * 1024,
    shell: true,
    windowsHide: true,
  });
  const stdout = result.stdout ?? "";
  const stderr = result.stderr ?? "";
  const prefix = `${String(ordinal).padStart(2, "0")}-${command.id}`;
  const stdoutPath = join(logDirectory, `${prefix}.stdout.txt`);
  const stderrPath = join(logDirectory, `${prefix}.stderr.txt`);
  writeFileSync(stdoutPath, stdout, "utf8");
  writeFileSync(stderrPath, stderr, "utf8");
  return {
    id: command.id,
    command: command.command,
    startedAt,
    finishedAt: new Date().toISOString(),
    exitCode: typeof result.status === "number" ? result.status : null,
    signal: result.signal ?? null,
    spawnError: result.error ? String(result.error.stack ?? result.error) : null,
    stdoutPath,
    stderrPath,
    stdoutSha256: sha256(Buffer.from(stdout, "utf8")),
    stderrSha256: sha256(Buffer.from(stderr, "utf8")),
    stdoutBytes: Buffer.byteLength(stdout),
    stderrBytes: Buffer.byteLength(stderr),
  };
}

function commandOutput(record) {
  return `${readFileSync(record.stdoutPath, "utf8")}\n${readFileSync(record.stderrPath, "utf8")}`;
}

/** Frozen diagnostic method: remove passing TAP lines before pattern matching. */
function diagnosticText(output) {
  return output
    .split(/\r?\n/)
    .filter((line) => !/^\s*[âœ”â„¹]/u.test(line))
    .join("\n");
}

/** Extract failing test names from node --test TAP output. */
function failingTestNames(output) {
  const names = [];
  for (const line of output.split(/\r?\n/)) {
    const tap = line.match(/^\s*not ok\s+\d+\s+-\s+(.*?)\s*$/);
    if (tap) {
      names.push(tap[1].trim());
      continue;
    }
    const marked = line.match(/^\s*âœ–\s+(.*?)(?:\s+\([\d.]+ms\))?\s*$/u);
    if (marked) names.push(marked[1].trim());
  }
  return [...new Set(names)].filter(Boolean);
}

function failureSignature(records) {
  const failed = records.filter((record) => record.exitCode !== 0);
  if (!failed.length) return "ALL_DECLARED_GATE_COMMANDS_EXITED_ZERO";
  const lines = failed
    .flatMap((record) => diagnosticText(commandOutput(record)).split(/\r?\n/))
    .map((line) => line.trim())
    .filter(Boolean);
  const marked = lines.filter((line) => /^(?:âœ–|not ok\b|error\b|assertionerror\b|fail\b)/iu.test(line));
  return (marked[0] ?? lines[0] ?? "DECLARED_GATE_EXITED_NONZERO_WITHOUT_TEXT").slice(0, 1000);
}

function classify(mutation, regenerationRecords, gateRecords) {
  if (regenerationRecords.some((record) => record.exitCode !== 0)) {
    return { classification: "NOT_RUN", matchedPatterns: [], matchingLines: [], failingTests: [], attributionSatisfied: false };
  }
  const failed = gateRecords.filter((record) => record.exitCode !== 0);
  if (!failed.length) {
    return { classification: "SURVIVED", matchedPatterns: [], matchingLines: [], failingTests: [], attributionSatisfied: false };
  }
  const rawOutput = failed.map((record) => commandOutput(record)).join("\n");
  const diagnostics = failed.map((record) => diagnosticText(commandOutput(record))).join("\n");
  const tests = failingTestNames(rawOutput);

  const matchedPatterns = mutation.semanticFailurePatterns.filter((pattern) =>
    new RegExp(pattern, "i").test(diagnostics),
  );
  const matchingLines = diagnostics
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && matchedPatterns.some((pattern) => new RegExp(pattern, "i").test(line)))
    .slice(0, 20);

  // Attribution: the declared intended test must be among the failing tests.
  const wanted = mutation.expectedFailingTest.toLowerCase();
  const attributionSatisfied = tests.some((name) => name.toLowerCase().includes(wanted));

  if (matchedPatterns.length > 0) {
    return { classification: "DETECTED_SEMANTIC", matchedPatterns, matchingLines, failingTests: tests, attributionSatisfied };
  }
  const nonEmptyLines = diagnostics.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const hashOnly =
    nonEmptyLines.length > 0 &&
    nonEmptyLines.every(
      (line) => HASH_ONLY_PATTERNS.some((pattern) => pattern.test(line)) || /^[-+\d\s.:/\\()[\],]+$/.test(line),
    );
  return {
    classification: hashOnly ? "DETECTED_BY_HASH_ONLY" : "INCONCLUSIVE",
    matchedPatterns,
    matchingLines,
    failingTests: tests,
    attributionSatisfied,
  };
}

function safeRemoveClone(clonePath, cloneRoot) {
  const resolvedClone = resolve(clonePath);
  const resolvedRoot = realpathSync(cloneRoot);
  const relativeToRoot = relative(resolvedRoot, resolvedClone);
  assert(
    relativeToRoot && !relativeToRoot.startsWith("..") && !isAbsolute(relativeToRoot),
    "Refusing unsafe clone removal.",
  );
  rmSync(resolvedClone, { recursive: true, force: false });
}

function evidenceEntries(root) {
  const entries = [];
  (function visit(directory) {
    for (const name of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, name.name);
      if (name.isDirectory()) visit(path);
      else if (name.isFile()) {
        const bytes = readFileSync(path);
        entries.push({
          path: relative(root, path).split(sep).join("/"),
          sha256: sha256(bytes),
          bytes: bytes.length,
        });
      }
    }
  })(join(root, "logs"));
  return entries.sort((left, right) => left.path.localeCompare(right.path));
}

function preflight(protocol, options) {
  validateProtocol(protocol);
  const preservationBefore = verifyPhaseCPreservation("PREFLIGHT");
  const baseCommit = resolveBaseCommit(options.baseCommit);
  const ancestry = verifyPredictionAncestry(options.protocolPath, baseCommit);
  assert(!existsSync(RESULT_REPOSITORY_PATH), `Future result already exists: ${RESULT_REPOSITORY_PATH}`);

  const verified = protocol.mutations.map((mutation) => ({
    id: mutation.id,
    class: mutation.class,
    propertyId: mutation.propertyId,
    targetPath: mutation.targetPath,
    ...validateFrozenPatch(mutation, baseCommit),
    regenerationCommands: mutation.regenerationCommands.map((entry) => entry.command),
    gateCommands: mutation.gateCommands.map((entry) => entry.command),
    baselineCommands: mutation.baselineCommands.map((entry) => entry.command),
    expectedFailingTest: mutation.expectedFailingTest,
  }));

  process.stdout.write(
    canonicalJson({
      mode: "PREFLIGHT_ONLY",
      protocolId: protocol.protocolId,
      baseCommit,
      ancestry,
      preservationBefore,
      mutationCount: verified.length,
      exactCount: verified.filter((v) => v.class === "EXACT_PHASE_C_REPLAY").length,
      alternateCount: verified.filter((v) => v.class === "ALTERNATE_FORM").length,
      adverseAttackCount: verified.filter((v) => v.class === "ADVERSE_RECORD_ATTACK").length,
      patchesApplied: 0,
      regenerationCommandsExecuted: 0,
      gateCommandsExecuted: 0,
      resultExists: false,
      verified,
    }),
  );
}

function execute(protocol, options) {
  validateProtocol(protocol);
  const preservationBefore = verifyPhaseCPreservation("BEFORE_EXECUTION");
  const baseCommit = resolveBaseCommit(options.baseCommit);
  const ancestry = verifyPredictionAncestry(options.protocolPath, baseCommit);
  assert(!existsSync(RESULT_REPOSITORY_PATH), `Future result already exists: ${RESULT_REPOSITORY_PATH}`);
  for (const mutation of protocol.mutations) validateFrozenPatch(mutation, baseCommit);

  const scratchRoot = ensureEmptyScratchRoot(options.scratchRoot);
  const clonesRoot = join(scratchRoot, "clones");
  const logsRoot = join(scratchRoot, "logs");
  mkdirSync(clonesRoot);
  mkdirSync(logsRoot);

  const primaryBefore = {
    head: git(["rev-parse", "HEAD"]).trim(),
    statusPorcelain: git(["status", "--porcelain=v1", "-z"]),
  };
  assert(primaryBefore.statusPorcelain === "", "Primary checkout must be clean before execution.");
  let baseIsAncestorOfHead = true;
  try {
    git(["merge-base", "--is-ancestor", baseCommit, primaryBefore.head]);
  } catch {
    baseIsAncestorOfHead = false;
  }
  assert(baseIsAncestorOfHead, "Base commit is not an ancestor of the execution commit.");

  const outcomes = [];
  for (const mutation of protocol.mutations) {
    const clonePath = join(clonesRoot, mutation.id.toLowerCase());
    const logDirectory = join(logsRoot, mutation.id);
    mkdirSync(logDirectory);
    const outcome = {
      id: mutation.id,
      class: mutation.class,
      propertyId: mutation.propertyId,
      targetPath: mutation.targetPath,
      predictedClassification: mutation.predictedClassification,
      expectedFailingTest: mutation.expectedFailingTest,
      clonePath,
      baseCommitVerified: false,
      preMutationSha256: null,
      postMutationSha256: null,
      patchApplied: false,
      regenerationCommands: [],
      gateCommands: [],
      baselineCommands: [],
      classification: null,
      matchedPatterns: [],
      matchingDiagnosticLines: [],
      failingTests: [],
      attributionSatisfied: false,
      baselineDetected: null,
      coverageProvenance: null,
      failureSignature: null,
      cloneCleanupStatus: "NOT_ATTEMPTED",
      error: null,
    };
    try {
      git(["clone", "--no-local", "--no-checkout", REPOSITORY_ROOT, clonePath]);
      git(["config", "core.autocrlf", "false"], clonePath);
      git(["checkout", "--detach", baseCommit], clonePath);
      assert(git(["rev-parse", "HEAD"], clonePath).trim() === baseCommit, `${mutation.id}: clone base mismatch.`);
      outcome.baseCommitVerified = true;

      const targetPath = join(clonePath, ...mutation.targetPath.split("/"));
      const beforeBytes = readFileSync(targetPath);
      outcome.preMutationSha256 = sha256(beforeBytes);
      assert(outcome.preMutationSha256 === mutation.preMutationSha256, `${mutation.id}: clone target digest mismatch.`);
      const beforeText = beforeBytes.toString("utf8");
      assert(countOccurrences(beforeText, mutation.patch.before) === 1, `${mutation.id}: frozen before text mismatch in clone.`);
      const afterText = beforeText.replace(mutation.patch.before, mutation.patch.after);
      writeFileSync(targetPath, afterText, "utf8");
      outcome.postMutationSha256 = sha256(readFileSync(targetPath));
      assert(outcome.postMutationSha256 !== outcome.preMutationSha256, `${mutation.id}: patch did not change bytes.`);
      outcome.patchApplied = true;

      writeFileSync(
        join(logDirectory, "00-patch.json"),
        canonicalJson({
          id: mutation.id,
          class: mutation.class,
          propertyId: mutation.propertyId,
          targetPath: mutation.targetPath,
          preMutationSha256: outcome.preMutationSha256,
          postMutationSha256: outcome.postMutationSha256,
          diff: git(["diff", "--", mutation.targetPath], clonePath),
        }),
        "utf8",
      );

      let ordinal = 1;
      for (const command of mutation.regenerationCommands) {
        const record = runCommand(command, clonePath, logDirectory, ordinal++);
        outcome.regenerationCommands.push(record);
        if (record.exitCode !== 0) break;
      }
      if (outcome.regenerationCommands.every((record) => record.exitCode === 0)) {
        for (const command of mutation.gateCommands) {
          outcome.gateCommands.push(runCommand(command, clonePath, logDirectory, ordinal++));
        }
        // SECONDARY, NON-CLASSIFYING: coverage provenance only.
        for (const command of mutation.baselineCommands) {
          outcome.baselineCommands.push(runCommand(command, clonePath, logDirectory, ordinal++));
        }
      }

      const verdict = classify(mutation, outcome.regenerationCommands, outcome.gateCommands);
      outcome.classification = verdict.classification;
      outcome.matchedPatterns = verdict.matchedPatterns;
      outcome.matchingDiagnosticLines = verdict.matchingLines;
      outcome.failingTests = verdict.failingTests;
      outcome.attributionSatisfied = verdict.attributionSatisfied;

      if (outcome.baselineCommands.length) {
        outcome.baselineDetected = outcome.baselineCommands.some((record) => record.exitCode !== 0);
        outcome.coverageProvenance = outcome.baselineDetected
          ? "SUITE_MEMBERSHIP_MIGRATION"
          : "NEW_COVERAGE_IN_D1";
      } else {
        outcome.coverageProvenance = "NOT_MEASURED";
      }

      outcome.failureSignature =
        outcome.classification === "NOT_RUN"
          ? failureSignature(outcome.regenerationCommands)
          : failureSignature(outcome.gateCommands);
      writeFileSync(join(logDirectory, "99-clone-status.txt"), git(["status", "--short", "--branch"], clonePath), "utf8");
    } catch (error) {
      outcome.error = String(error.stack ?? error);
      if (!outcome.classification) outcome.classification = "NOT_RUN";
      outcome.failureSignature = String(error.message ?? error).slice(0, 1000);
      writeFileSync(join(logDirectory, "98-runner-error.txt"), `${outcome.error}\n`, "utf8");
    } finally {
      if (options.cleanupClones && existsSync(clonePath)) {
        safeRemoveClone(clonePath, clonesRoot);
        outcome.cloneCleanupStatus = "REMOVED_WITHIN_EXPLICIT_SCRATCH_ROOT";
      } else if (existsSync(clonePath)) {
        outcome.cloneCleanupStatus = "PRESERVED_WITHIN_EXPLICIT_SCRATCH_ROOT";
      } else {
        outcome.cloneCleanupStatus = "NO_CLONE_PRESENT";
      }
      outcomes.push(outcome);
    }
  }

  const primaryAfter = {
    head: git(["rev-parse", "HEAD"]).trim(),
    statusPorcelain: git(["status", "--porcelain=v1", "-z"]),
  };
  const primaryCheckoutUnchanged =
    primaryAfter.head === primaryBefore.head && primaryAfter.statusPorcelain === primaryBefore.statusPorcelain;
  const preservationAfter = verifyPhaseCPreservation("AFTER_EXECUTION");

  const counts = Object.fromEntries(
    ["DETECTED_SEMANTIC", "DETECTED_BY_HASH_ONLY", "SURVIVED", "NOT_RUN", "INCONCLUSIVE"].map((name) => [
      name,
      outcomes.filter((outcome) => outcome.classification === name).length,
    ]),
  );
  const attributionFailures = outcomes
    .filter((o) => o.classification === "DETECTED_SEMANTIC" && !o.attributionSatisfied)
    .map((o) => o.id);

  // CORRECTION 3. A DETECTED_SEMANTIC classification whose diagnostic cannot be
  // attributed to the declared intended test is CLASSIFIED but NOT CREDITED. The
  // original result reported only the classified count, which overstated how much
  // detection the battery is entitled to claim. Report all three numbers.
  const classifiedDetections = counts.DETECTED_SEMANTIC;
  const creditedDetections = outcomes.filter(
    (o) => o.classification === "DETECTED_SEMANTIC" && o.attributionSatisfied,
  ).length;
  const detectionAccounting = {
    classified: classifiedDetections,
    credited: creditedDetections,
    uncredited: classifiedDetections - creditedDetections,
    uncreditedIds: attributionFailures,
    rule:
      "credited = DETECTED_SEMANTIC AND attributionSatisfied. Only credited detections may be reported as " +
      "coverage. classified minus credited is reported, never absorbed.",
    AC4: attributionFailures.length === 0 ? "PASS" : "FAIL",
  };

  // CORRECTION 1. Record the protocol that was ACTUALLY executed. This field was
  // previously a hardcoded literal naming the v1 protocol, which misattributed any
  // run performed with --protocol.
  const protocolPathUsed = relative(REPOSITORY_ROOT, resolve(options.protocolPath)).split(sep).join("/");

  const result = {
    schema: "uni.flagellum.d1-semantic-remediation-result/1.0.0",
    protocolId: protocol.protocolId,
    protocolPath: protocolPathUsed,
    protocolVersion: protocol.protocolVersion ?? "v1",
    protocolSha256: sha256(readFileSync(resolve(options.protocolPath))),
    baseCommit,
    executionCommit: primaryBefore.head,
    ancestry,
    scratchRoot,
    primaryCheckoutUnchanged,
    primaryBefore,
    primaryAfter,
    phaseCPreservation: { before: preservationBefore, after: preservationAfter },
    classificationCounts: counts,
    detectionAccounting,
    attributionFailures,
    coverageProvenanceSummary: Object.fromEntries(
      ["SUITE_MEMBERSHIP_MIGRATION", "NEW_COVERAGE_IN_D1", "NOT_MEASURED"].map((name) => [
        name,
        outcomes.filter((o) => o.coverageProvenance === name).length,
      ]),
    ),
    outcomes,
  };

  const resultPath = join(scratchRoot, RESULT_BASENAME);
  writeFileSync(resultPath, canonicalJson(result), "utf8");
  const evidence = {
    schema: "uni.flagellum.d1-semantic-remediation-evidence-manifest/1.0.0",
    protocolId: protocol.protocolId,
    baseCommit,
    executionCommit: primaryBefore.head,
    result: {
      path: RESULT_BASENAME,
      sha256: sha256(readFileSync(resultPath)),
      bytes: statSync(resultPath).size,
    },
    logs: evidenceEntries(scratchRoot),
    cloneCleanupRequested: options.cleanupClones,
    primaryCheckoutUnchanged,
    phaseCPreserved: true,
  };
  const evidencePath = join(scratchRoot, EVIDENCE_BASENAME);
  writeFileSync(evidencePath, canonicalJson(evidence), "utf8");
  process.stdout.write(
    canonicalJson({
      resultPath,
      evidencePath,
      protocolPath: protocolPathUsed,
      classificationCounts: counts,
      detectionAccounting,
      attributionFailures,
      coverageProvenanceSummary: result.coverageProvenanceSummary,
      primaryCheckoutUnchanged,
    }),
  );
  if (!primaryCheckoutUnchanged) process.exitCode = 1;
}

const options = parseArguments(process.argv.slice(2));
const protocol = readJson(options.protocolPath);
if (options.mode === "preflight") preflight(protocol, options);
else execute(protocol, options);
