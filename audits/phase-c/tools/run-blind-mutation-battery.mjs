#!/usr/bin/env node

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
  "audits/phase-c/blind-mutation-protocol.codex.v1.json",
);
const RESULT_BASENAME = "blind-mutation-result.codex.v1.json";
const EVIDENCE_BASENAME = "blind-mutation-evidence-manifest.codex.v1.json";
const ALLOWED_COMMANDS = new Set([
  "npm run experiment:run",
  "npm run science:run",
  "npm run cross-study:run",
  "node --test tests/semantic/*.mjs",
]);
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
      "  node audits/phase-c/tools/run-blind-mutation-battery.mjs --preflight\n" +
      "  node audits/phase-c/tools/run-blind-mutation-battery.mjs --execute --scratch-root <absolute-empty-path> [--cleanup-clones]\n",
  );
  process.exit(message ? 2 : 0);
}

function parseArguments(argv) {
  const options = {
    mode: null,
    protocolPath: DEFAULT_PROTOCOL_PATH,
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
    maxBuffer: 64 * 1024 * 1024,
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
  while (true) {
    const index = haystack.indexOf(needle, offset);
    if (index < 0) return count;
    count += 1;
    offset = index + needle.length;
  }
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function validateProtocol(protocol) {
  assert(protocol.schema === "uni.flagellum.blind-mutation-protocol/1.0.0", "Unexpected protocol schema.");
  assert(/^[0-9a-f]{40}$/.test(protocol.baseCommit), "baseCommit must be a full SHA.");
  assert(Array.isArray(protocol.mutations), "mutations must be an array.");
  assert(protocol.mutations.length >= 8 && protocol.mutations.length <= 12, "Protocol must contain 8-12 mutations.");
  const ids = new Set();
  for (const mutation of protocol.mutations) {
    assert(!ids.has(mutation.id), `Duplicate mutation id: ${mutation.id}`);
    ids.add(mutation.id);
    assert(typeof mutation.targetPath === "string" && mutation.targetPath.length > 0, `${mutation.id}: targetPath missing.`);
    assert(!isAbsolute(mutation.targetPath), `${mutation.id}: targetPath must be repository-relative.`);
    assert(!mutation.targetPath.includes(".."), `${mutation.id}: targetPath may not traverse upward.`);
    assert(/^[0-9a-f]{64}$/.test(mutation.preMutationSha256), `${mutation.id}: invalid raw digest.`);
    assert(mutation.patch?.encoding === "utf8", `${mutation.id}: only UTF-8 text patches are supported.`);
    assert(mutation.patch.expectedOccurrences === 1, `${mutation.id}: exact patch must require one occurrence.`);
    assert(mutation.patch.before !== mutation.patch.after, `${mutation.id}: before and after text are identical.`);
    assert(typeof mutation.scientificHarm === "string" && mutation.scientificHarm.length > 0, `${mutation.id}: scientific harm missing.`);
    assert(Array.isArray(mutation.regenerationCommands), `${mutation.id}: regenerationCommands missing.`);
    assert(Array.isArray(mutation.gateCommands) && mutation.gateCommands.length > 0, `${mutation.id}: gateCommands missing.`);
    for (const command of [...mutation.regenerationCommands, ...mutation.gateCommands]) {
      assert(typeof command.id === "string" && typeof command.command === "string", `${mutation.id}: malformed command.`);
      assert(ALLOWED_COMMANDS.has(command.command), `${mutation.id}: command is outside the frozen allowlist: ${command.command}`);
    }
    assert(
      ["DETECTED_SEMANTIC", "DETECTED_BY_HASH_ONLY", "SURVIVED", "NOT_RUN", "INCONCLUSIVE"].includes(
        mutation.predictedClassification,
      ),
      `${mutation.id}: invalid predicted classification.`,
    );
    assert(Array.isArray(mutation.semanticFailurePatterns) && mutation.semanticFailurePatterns.length > 0, `${mutation.id}: semantic patterns missing.`);
    for (const pattern of mutation.semanticFailurePatterns) new RegExp(pattern, "i");
  }
}

function baseBlob(mutation, baseCommit) {
  return git(["show", `${baseCommit}:${mutation.targetPath}`], REPOSITORY_ROOT, null);
}

function validateFrozenPatch(mutation, baseCommit) {
  const bytes = baseBlob(mutation, baseCommit);
  assert(sha256(bytes) === mutation.preMutationSha256, `${mutation.id}: raw base digest mismatch.`);
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

function preflight(protocol) {
  validateProtocol(protocol);
  const commitType = git(["cat-file", "-t", protocol.baseCommit]).trim();
  assert(commitType === "commit", "Declared base is not a commit.");
  const verified = protocol.mutations.map((mutation) => ({
    id: mutation.id,
    targetPath: mutation.targetPath,
    ...validateFrozenPatch(mutation, protocol.baseCommit),
    regenerationCommands: mutation.regenerationCommands.map((entry) => entry.command),
    gateCommands: mutation.gateCommands.map((entry) => entry.command),
  }));
  const futureResult = join(REPOSITORY_ROOT, "audits/phase-c", RESULT_BASENAME);
  assert(!existsSync(futureResult), `Future result already exists: ${futureResult}`);
  process.stdout.write(
    canonicalJson({
      mode: "PREFLIGHT_ONLY",
      baseCommit: protocol.baseCommit,
      mutationCount: verified.length,
      patchesApplied: 0,
      regenerationCommandsExecuted: 0,
      gateCommandsExecuted: 0,
      resultExists: false,
      verified,
    }),
  );
}

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
    maxBuffer: 64 * 1024 * 1024,
    shell: true,
    windowsHide: true,
  });
  const stdout = result.stdout ?? "";
  const stderr = result.stderr ?? "";
  const exitCode = typeof result.status === "number" ? result.status : null;
  const signal = result.signal ?? null;
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
    exitCode,
    signal,
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

function diagnosticText(output) {
  return output
    .split(/\r?\n/)
    .filter((line) => !/^\s*[✔ℹ]/u.test(line))
    .join("\n");
}

function failureSignature(gateRecords) {
  const failed = gateRecords.filter((record) => record.exitCode !== 0);
  if (!failed.length) return "ALL_DECLARED_GATE_COMMANDS_EXITED_ZERO";
  const lines = failed
    .flatMap((record) => diagnosticText(commandOutput(record)).split(/\r?\n/))
    .map((line) => line.trim())
    .filter(Boolean);
  const marked = lines.filter((line) => /^(?:✖|not ok\b|error\b|assertionerror\b|fail\b)/iu.test(line));
  return (marked[0] ?? lines[0] ?? "DECLARED_GATE_EXITED_NONZERO_WITHOUT_TEXT").slice(0, 1000);
}

function classify(mutation, regenerationRecords, gateRecords) {
  if (regenerationRecords.some((record) => record.exitCode !== 0)) return "NOT_RUN";
  const failed = gateRecords.filter((record) => record.exitCode !== 0);
  if (!failed.length) return "SURVIVED";
  const diagnostics = failed.map((record) => diagnosticText(commandOutput(record))).join("\n");
  const semantic = mutation.semanticFailurePatterns.some((pattern) => new RegExp(pattern, "i").test(diagnostics));
  if (semantic) return "DETECTED_SEMANTIC";
  const nonEmptyLines = diagnostics.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const hashOnly = nonEmptyLines.length > 0 && nonEmptyLines.every(
    (line) => HASH_ONLY_PATTERNS.some((pattern) => pattern.test(line)) || /^[-+\d\s.:/\\()[\],]+$/.test(line),
  );
  return hashOnly ? "DETECTED_BY_HASH_ONLY" : "INCONCLUSIVE";
}

function safeRemoveClone(clonePath, cloneRoot) {
  const resolvedClone = resolve(clonePath);
  const resolvedRoot = realpathSync(cloneRoot);
  const relativeToRoot = relative(resolvedRoot, resolvedClone);
  assert(relativeToRoot && !relativeToRoot.startsWith("..") && !isAbsolute(relativeToRoot), "Refusing unsafe clone removal.");
  rmSync(resolvedClone, { recursive: true, force: false });
}

function evidenceEntries(root) {
  const entries = [];
  function visit(directory) {
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
  }
  visit(join(root, "logs"));
  return entries.sort((left, right) => left.path.localeCompare(right.path));
}

function execute(protocol, options) {
  validateProtocol(protocol);
  for (const mutation of protocol.mutations) validateFrozenPatch(mutation, protocol.baseCommit);
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
  assert(
    git(["merge-base", "--is-ancestor", protocol.baseCommit, primaryBefore.head], REPOSITORY_ROOT, null).length === 0,
    "Base commit is not an ancestor of the execution commit.",
  );

  const outcomes = [];
  for (const mutation of protocol.mutations) {
    const clonePath = join(clonesRoot, mutation.id.toLowerCase());
    const logDirectory = join(logsRoot, mutation.id);
    mkdirSync(logDirectory);
    const outcome = {
      id: mutation.id,
      targetPath: mutation.targetPath,
      predictedClassification: mutation.predictedClassification,
      clonePath,
      baseCommitVerified: false,
      preMutationSha256: null,
      postMutationSha256: null,
      patchApplied: false,
      regenerationCommands: [],
      gateCommands: [],
      classification: null,
      failureSignature: null,
      cloneCleanupStatus: "NOT_ATTEMPTED",
      error: null,
    };
    try {
      git(["clone", "--no-local", "--no-checkout", REPOSITORY_ROOT, clonePath]);
      git(["config", "core.autocrlf", "false"], clonePath);
      git(["checkout", "--detach", protocol.baseCommit], clonePath);
      const cloneHead = git(["rev-parse", "HEAD"], clonePath).trim();
      assert(cloneHead === protocol.baseCommit, `${mutation.id}: clone base mismatch.`);
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
      assert(countOccurrences(afterText, mutation.patch.after) === 1, `${mutation.id}: after text was not written exactly once.`);
      outcome.patchApplied = true;

      writeFileSync(
        join(logDirectory, "00-patch.json"),
        canonicalJson({
          id: mutation.id,
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
      }
      outcome.classification = classify(mutation, outcome.regenerationCommands, outcome.gateCommands);
      outcome.failureSignature = outcome.classification === "NOT_RUN"
        ? failureSignature(outcome.regenerationCommands)
        : failureSignature(outcome.gateCommands);
      writeFileSync(join(logDirectory, "99-clone-status.txt"), git(["status", "--short", "--branch"], clonePath), "utf8");
    } catch (error) {
      outcome.error = String(error.stack ?? error);
      if (!outcome.classification) outcome.classification = outcome.patchApplied ? "NOT_RUN" : "NOT_RUN";
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
  const counts = Object.fromEntries(
    ["DETECTED_SEMANTIC", "DETECTED_BY_HASH_ONLY", "SURVIVED", "NOT_RUN", "INCONCLUSIVE"].map((name) => [
      name,
      outcomes.filter((outcome) => outcome.classification === name).length,
    ]),
  );
  const result = {
    schema: "uni.flagellum.blind-mutation-result/1.0.0",
    protocolId: protocol.protocolId,
    baseCommit: protocol.baseCommit,
    executionCommit: primaryBefore.head,
    scratchRoot,
    primaryCheckoutUnchanged,
    primaryBefore,
    primaryAfter,
    classificationCounts: counts,
    outcomes,
  };
  const resultPath = join(scratchRoot, RESULT_BASENAME);
  writeFileSync(resultPath, canonicalJson(result), "utf8");
  const evidence = {
    schema: "uni.flagellum.blind-mutation-evidence-manifest/1.0.0",
    protocolId: protocol.protocolId,
    baseCommit: protocol.baseCommit,
    executionCommit: primaryBefore.head,
    result: {
      path: RESULT_BASENAME,
      sha256: sha256(readFileSync(resultPath)),
      bytes: statSync(resultPath).size,
    },
    logs: evidenceEntries(scratchRoot),
    cloneCleanupRequested: options.cleanupClones,
    primaryCheckoutUnchanged,
  };
  const evidencePath = join(scratchRoot, EVIDENCE_BASENAME);
  writeFileSync(evidencePath, canonicalJson(evidence), "utf8");
  process.stdout.write(canonicalJson({ resultPath, evidencePath, classificationCounts: counts, primaryCheckoutUnchanged }));
  if (!primaryCheckoutUnchanged) process.exitCode = 1;
}

const options = parseArguments(process.argv.slice(2));
const protocol = readJson(options.protocolPath);
if (options.mode === "preflight") preflight(protocol);
else execute(protocol, options);
