// SEMANTIC GATE — PROSPECTIVITY PROVENANCE
//
// WHAT THIS GATE ASSERTS
// ----------------------
// A prediction is prospective only if it was committed before its observation.
// This gate makes that claim CHECKABLE against the git commit DAG, which is an
// oracle this repository's analysis pipeline does not write.
//
// Every prediction record declares a prospectivity class. This gate independently
// MEASURES the class from git topology and asserts that the declaration equals the
// measurement. A record may not claim PROSPECTIVE unless the commit that first
// introduced the prediction is a STRICT ANCESTOR of the commit that first
// introduced the result artifact it predicts.
//
// WHY THIS EXISTS
// ---------------
// Mutation M11 falsified the protocol freeze date so the preregistration claimed
// to postdate the results it governs. Nothing in the suite detected the ordering
// violation; only a sha256 moved. A self-declared timestamp inside a file is not
// evidence of ordering, because the same edit that writes the claim writes the
// timestamp. Commit ancestry is different: to forge it you must rewrite history,
// which changes every descendant commit id, including HEAD.
//
// The audit that discovered M11 then committed the same defect: its prediction
// file and its result ledger entered history in ONE commit (b675978), so git
// cannot corroborate prediction-before-execution for it either. That record is
// included below, declared honestly as TIMING_UNVERIFIED. This gate exists to
// keep it declared honestly.
//
// NON-ROUTES (deliberate)
// -----------------------
// This gate computes no sha256, reads no runId, touches no artifact digest, and
// never compares a fresh computation against a stored report. Delete every hash
// in the repository and this gate is unaffected. Its only inputs are the
// prediction records and `git`.
//
// NO WALL CLOCK
// -------------
// Ordering is decided by `git merge-base --is-ancestor` — pure DAG reachability.
// Committer and author timestamps are NEVER consulted; they are attacker-supplied
// strings (`GIT_COMMITTER_DATE`) and carry no ordering guarantee.
//
// HONEST DEGRADATION
// ------------------
// If git is unavailable, or the working tree is not a repository, or the history
// is shallow, the gate reports NOT_RUN and SKIPS. It never passes vacuously and
// never upgrades an unverifiable record to PROSPECTIVE.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");

// ---------------------------------------------------------------------------
// 1. PREDICTION RECORD FORMAT
// ---------------------------------------------------------------------------
//
// A prediction record is an object with:
//
//   recordId            stable identifier, unique within the repository
//   claim               what is asserted, in words, before the result exists
//   falsifier           the observation that would refute the claim
//   madeAgainstCommit   the git commit the prediction was written AGAINST.
//                       Must exist, must be an ancestor of HEAD, and must be an
//                       ancestor-or-self of the commit that introduced the
//                       prediction file. This is the prediction's ANCHOR: it
//                       pins the state of the world the predictor could see.
//   predictionPath      repo-relative path of the file carrying the prediction
//   resultPaths         repo-relative paths of the result artifacts the
//                       prediction governs
//   prospectivity       DECLARED class. One of:
//                         "PROSPECTIVE"       prediction strictly precedes every
//                                             result artifact in commit ancestry
//                         "TIMING_UNVERIFIED" ordering cannot be corroborated by
//                                             git (same commit, result first, or
//                                             either side uncommitted)
//                         "PENDING"           prediction committed, result does
//                                             not exist yet, anywhere
//   note                free text; never load-bearing
//
// Records live in this file (canonical, worked examples) and/or on disk as
// experiments/predictions/*.prediction.json. Both are checked identically.

/** @type {Array<object>} */
const EMBEDDED_RECORDS = [
  {
    recordId: "B1-MUTATION-BATTERY-V1",
    claim:
      "The 15-mutation patch set frozen in b1-mutation-patch-set.v1.json, when " +
      "executed against the repository, will produce a ledger in which a majority " +
      "of semantic corruptions are detected only by a moved artifact hash rather " +
      "than by any assertion naming the corrupted property.",
    falsifier:
      "A ledger in which every mutation produces at least one failure line that " +
      "names the semantic property it corrupted would refute the claim.",
    madeAgainstCommit: "392ae947c0a1e095e28024748b410970b0e067eb",
    predictionPath: "audits/phase-b/b1-mutation-patch-set.v1.json",
    resultPaths: ["audits/phase-b/b1-mutation-ledger.json"],
    prospectivity: "PROSPECTIVE",
    note:
      "The frozen patch set entered history at 4aef241; the executed ledger at " +
      "1fc6758, a descendant. Git corroborates prediction-before-execution.",
  },
  {
    recordId: "B1-RERUN-ON-C3-FIXED-TREE",
    claim:
      "Re-running the mutation battery against the C3-fixed tree removes the " +
      "WADHWA_2022_EVENTS hash failure from every row, and no mutation flips from " +
      "DETECTED to SURVIVED.",
    falsifier:
      "Any row still carrying the WADHWA_2022_EVENTS hash failure, or any " +
      "mutation flipping from DETECTED to SURVIVED, would refute the claim.",
    madeAgainstCommit: "1630a68f48d777ec8db07b6fa36433cb4fdc0de8",
    predictionPath:
      "audits/phase-b/b1-rerun-prediction-committed-before-execution.txt",
    resultPaths: ["audits/phase-b/b1-mutation-ledger-rerun.json"],
    prospectivity: "TIMING_UNVERIFIED",
    note:
      "ADVERSE PROVENANCE RESULT. The prediction text was written before the " +
      "battery ran, but it was COMMITTED in the same commit (b675978) as the " +
      "ledger it predicts. Git therefore cannot corroborate the ordering. The " +
      "record is downgraded rather than asserted. This is the defect this gate " +
      "was built to keep visible.",
  },
  {
    recordId: "C3-CANONICAL-WRITE-FIX",
    claim:
      "Replacing the raw byte copy at scripts/run-observed-experiments.mjs:35 " +
      "with a canonical-LF write stops regeneration corrupting the served " +
      "derived-event mirror, and removes the CRLF confound from the B1 " +
      "mutation battery.",
    falsifier:
      "Any tracked file other than the generator changing bytes, or npm test " +
      "ceasing to exit 0, or red test C3e remaining red, would refute the claim.",
    madeAgainstCommit: "1fc67583f55d811899f08138d0d462220b5d63df",
    predictionPath:
      "audits/phase-b/c3-fix-prediction-committed-before-change.txt",
    // The result here is an EDIT to a long-lived file, not a new file, so
    // path-introduction cannot witness it. resultCommit measures the actual
    // event: both the prediction and the fix entered history in 1630a68.
    resultCommit: "1630a68f48d777ec8db07b6fa36433cb4fdc0de8",
    resultPaths: [
      "scripts/run-observed-experiments.mjs",
      "experiments/results/observed-experiment-report.json",
    ],
    prospectivity: "TIMING_UNVERIFIED",
    note:
      "ADVERSE PROVENANCE RESULT, the SECOND of two. The prediction text was " +
      "written before the production fix was made, but it was COMMITTED in the " +
      "same commit (1630a68) as the fix it predicts. Git therefore cannot " +
      "corroborate the ordering. Two of the six predictions in that record were " +
      "additionally REFUTED on execution: P-C3-1 predicted zero changed files " +
      "and ten changed, and P-C3-5 predicted no committed artifact would change " +
      "bytes and ten did. The filename asserts " +
      "'committed-before-change', which git contradicts; the file is preserved " +
      "with that misleading name rather than renamed, because renaming would " +
      "erase the record of the error. Added at Codex's instruction after review " +
      "found this gate documented only the B1 rerun violation and not this one.",
  },
];

const RECORD_FIELDS = [
  "recordId",
  "claim",
  "falsifier",
  "madeAgainstCommit",
  "predictionPath",
  "resultPaths",
  "prospectivity",
];

const VALID_CLASSES = new Set(["PROSPECTIVE", "TIMING_UNVERIFIED", "PENDING"]);

const DISK_RECORD_DIR = path.join(ROOT, "experiments", "predictions");

function loadDiskRecords() {
  if (!fs.existsSync(DISK_RECORD_DIR)) return [];
  return fs
    .readdirSync(DISK_RECORD_DIR)
    .filter((n) => n.endsWith(".prediction.json"))
    .sort()
    .map((n) => {
      const p = path.join(DISK_RECORD_DIR, n);
      const parsed = JSON.parse(fs.readFileSync(p, "utf8"));
      return { ...parsed, __origin: `experiments/predictions/${n}` };
    });
}

const ALL_RECORDS = [
  ...EMBEDDED_RECORDS.map((r) => ({
    ...r,
    __origin: "tests/semantic/prospectivity-provenance.test.mjs",
  })),
  ...loadDiskRecords(),
];

// ---------------------------------------------------------------------------
// 2. GIT ADAPTER
// ---------------------------------------------------------------------------

function git(args, cwd) {
  try {
    const out = execFileSync("git", args, {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      windowsHide: true,
    });
    return { ok: true, out: out.replace(/\r\n/g, "\n").trim() };
  } catch (err) {
    return { ok: false, out: "", err: String((err && err.message) || err) };
  }
}

/**
 * Why this repository may not be able to answer provenance questions.
 * Returns null when git is usable, otherwise a NOT_RUN reason string.
 */
function gitUnavailableReason(cwd) {
  const version = git(["--version"], cwd);
  if (!version.ok) return "git executable not available on PATH";
  const inside = git(["rev-parse", "--is-inside-work-tree"], cwd);
  if (!inside.ok || inside.out !== "true") return "not inside a git work tree";
  const head = git(["rev-parse", "--verify", "HEAD"], cwd);
  if (!head.ok) return "repository has no commits reachable from HEAD";
  const shallow = git(["rev-parse", "--is-shallow-repository"], cwd);
  if (shallow.ok && shallow.out === "true") {
    return "repository history is shallow; commit ancestry is not decidable";
  }
  return null;
}

function commitExists(sha, cwd) {
  return git(["cat-file", "-e", `${sha}^{commit}`], cwd).ok;
}

function isAncestor(a, b, cwd) {
  // Strictly: reachability. `--is-ancestor X X` is TRUE in git, so callers that
  // need STRICT ancestry must also compare the two ids.
  return git(["merge-base", "--is-ancestor", a, b], cwd).ok;
}

/**
 * Commits that ADDED `relPath`, newest first, restricted to HEAD's history.
 * `--diff-filter=A` selects only additions, so a later content edit cannot be
 * mistaken for an introduction.
 */
function addingCommits(relPath, cwd) {
  const r = git(
    [
      "log",
      "--diff-filter=A",
      "--format=%H",
      "--no-merges",
      "HEAD",
      "--",
      relPath.split(path.sep).join("/"),
    ],
    cwd,
  );
  if (!r.ok || r.out === "") return [];
  return r.out.split("\n").map((s) => s.trim()).filter(Boolean);
}

// Conservative selection, chosen so that claiming PROSPECTIVE is HARDER, never
// easier, when a path was added more than once (delete/re-add):
//   prediction -> the NEWEST introduction (latest possible authorship)
//   result     -> the OLDEST introduction (earliest possible existence)
const newestIntroduction = (relPath, cwd) => addingCommits(relPath, cwd)[0] ?? null;
const oldestIntroduction = (relPath, cwd) => {
  const c = addingCommits(relPath, cwd);
  return c.length ? c[c.length - 1] : null;
};

// ---------------------------------------------------------------------------
// 3. THE CLASSIFIER — the machinery under test
// ---------------------------------------------------------------------------
//
// Pure function of (record, repo). Returns a measured class and a reason.
// It has NO path that yields PROSPECTIVE without a strict ancestry proof.

/** Paths actually CHANGED by one commit. diff-tree, not --diff-filter=A, so a
 *  MODIFICATION counts - which is the whole point for a record whose result is an
 *  edit to a long-lived file rather than a new file. */
function pathsChangedByCommit(commitish, cwd) {
  const r = git(["diff-tree", "--no-commit-id", "--name-only", "-r", commitish], cwd);
  if (!r.ok) return null;
  return new Set(r.out.split("\n").map((s) => s.trim()).filter(Boolean));
}

/**
 * When a record declares `resultCommit`, the result is an EDIT to an existing
 * file, so path-introduction cannot witness it. Measure the declared commit
 * directly instead. This path can still only reach PROSPECTIVE via strict
 * ancestry, never by assertion.
 */
function measureViaResultCommit(record, cwd) {
  const rc = record.resultCommit;
  if (!commitExists(rc, cwd)) {
    return { klass: "TIMING_UNVERIFIED", reason: `RESULT_COMMIT_NOT_IN_HISTORY:${rc.slice(0, 8)}`, predAdd: null, results: [] };
  }
  if (!isAncestor(rc, "HEAD", cwd)) {
    return { klass: "TIMING_UNVERIFIED", reason: `RESULT_COMMIT_NOT_REACHABLE_FROM_HEAD:${rc.slice(0, 8)}`, predAdd: null, results: [] };
  }

  const changed = pathsChangedByCommit(rc, cwd);
  const results = record.resultPaths.map((rel) => ({
    path: rel,
    add: rc,
    onDisk: fs.existsSync(path.join(cwd, rel)),
    changedByResultCommit: changed ? changed.has(rel.split(path.sep).join("/")) : false,
  }));
  const notChanged = results.filter((r) => !r.changedByResultCommit);
  if (notChanged.length) {
    return {
      klass: "TIMING_UNVERIFIED",
      reason: `RESULT_COMMIT_DID_NOT_CHANGE_PATH:${notChanged.map((r) => r.path).join(",")}`,
      predAdd: newestIntroduction(record.predictionPath, cwd),
      results,
    };
  }

  const predAdd = newestIntroduction(record.predictionPath, cwd);
  if (predAdd === null) {
    return { klass: "TIMING_UNVERIFIED", reason: "PREDICTION_NOT_IN_HISTORY", predAdd, results };
  }
  if (predAdd === rc) {
    return { klass: "TIMING_UNVERIFIED", reason: `SAME_COMMIT:${rc.slice(0, 8)}`, predAdd, results };
  }
  if (!isAncestor(predAdd, rc, cwd)) {
    return { klass: "TIMING_UNVERIFIED", reason: `RESULT_NOT_DESCENDED_FROM_PREDICTION:${rc.slice(0, 8)}`, predAdd, results };
  }
  return { klass: "PROSPECTIVE", reason: "STRICT_ANCESTRY_PROVEN_VIA_RESULT_COMMIT", predAdd, results };
}

function measureProspectivity(record, cwd) {
  if (record.resultCommit) return measureViaResultCommit(record, cwd);

  const predAdd = newestIntroduction(record.predictionPath, cwd);
  const predOnDisk = fs.existsSync(path.join(cwd, record.predictionPath));

  const results = record.resultPaths.map((rel) => ({
    path: rel,
    add: oldestIntroduction(rel, cwd),
    onDisk: fs.existsSync(path.join(cwd, rel)),
  }));

  const anyResultInHistory = results.some((r) => r.add !== null);
  const anyResultOnDisk = results.some((r) => r.onDisk);

  if (predAdd === null) {
    if (!anyResultInHistory && !anyResultOnDisk) {
      return predOnDisk
        ? { klass: "PENDING", reason: "PREDICTION_UNCOMMITTED_NO_RESULT", predAdd, results }
        : { klass: "PENDING", reason: "NOTHING_PRESENT", predAdd, results };
    }
    return {
      klass: "TIMING_UNVERIFIED",
      reason: "PREDICTION_NOT_IN_HISTORY",
      predAdd,
      results,
    };
  }

  if (!anyResultInHistory) {
    if (anyResultOnDisk) {
      return {
        klass: "TIMING_UNVERIFIED",
        reason: "RESULT_ON_DISK_BUT_UNCOMMITTED",
        predAdd,
        results,
      };
    }
    return { klass: "PENDING", reason: "RESULT_DOES_NOT_EXIST_YET", predAdd, results };
  }

  // Every result artifact must be strictly downstream of the prediction.
  for (const r of results) {
    if (r.add === null) {
      return {
        klass: "TIMING_UNVERIFIED",
        reason: `RESULT_NOT_IN_HISTORY:${r.path}`,
        predAdd,
        results,
      };
    }
    if (r.add === predAdd) {
      return {
        klass: "TIMING_UNVERIFIED",
        reason: `SAME_COMMIT:${r.path}`,
        predAdd,
        results,
      };
    }
    if (!isAncestor(predAdd, r.add, cwd)) {
      return {
        klass: "TIMING_UNVERIFIED",
        reason: `RESULT_NOT_DESCENDED_FROM_PREDICTION:${r.path}`,
        predAdd,
        results,
      };
    }
  }

  return { klass: "PROSPECTIVE", reason: "STRICT_ANCESTRY_PROVEN", predAdd, results };
}

// ---------------------------------------------------------------------------
// 4. FIXTURE BUILDER — synthetic repositories with hand-calculable answers
// ---------------------------------------------------------------------------

const tempRoots = [];

function makeRepo() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "prospectivity-fixture-"));
  tempRoots.push(dir);
  const r = git(["init", "-q", "--initial-branch=main"], dir);
  if (!r.ok) {
    // Older git without --initial-branch
    const fallback = git(["init", "-q"], dir);
    assert.ok(fallback.ok, `fixture git init failed: ${fallback.err}`);
  }
  git(["config", "user.name", "Fixture"], dir);
  git(["config", "user.email", "fixture@example.invalid"], dir);
  git(["config", "commit.gpgsign", "false"], dir);
  git(["config", "core.autocrlf", "false"], dir);
  return dir;
}

/** Write files and make one commit. Returns the commit sha. */
function commitFiles(dir, files, message) {
  for (const [rel, body] of Object.entries(files)) {
    const abs = path.join(dir, rel);
    fs.mkdirSync(path.dirname(abs), { recursive: true });
    fs.writeFileSync(abs, body, "utf8");
  }
  const add = git(["add", "-A"], dir);
  assert.ok(add.ok, `fixture git add failed: ${add.err}`);
  const commit = git(["commit", "-q", "--no-verify", "-m", message], dir);
  assert.ok(commit.ok, `fixture git commit failed: ${commit.err}`);
  const head = git(["rev-parse", "HEAD"], dir);
  assert.ok(head.ok, "fixture HEAD unreadable");
  return head.out;
}

const fixtureRecord = (over) => ({
  recordId: "FIXTURE",
  claim: "fixture claim",
  falsifier: "fixture falsifier",
  madeAgainstCommit: "0".repeat(40),
  predictionPath: "pred.txt",
  resultPaths: ["result.json"],
  prospectivity: "PROSPECTIVE",
  ...over,
});

process.on("exit", () => {
  for (const dir of tempRoots) {
    try {
      fs.rmSync(dir, { recursive: true, force: true, maxRetries: 5 });
    } catch {
      /* best effort; fixtures live in the OS temp dir */
    }
  }
});

// ---------------------------------------------------------------------------
// 5. TESTS
// ---------------------------------------------------------------------------

const NOT_RUN = gitUnavailableReason(ROOT);
if (NOT_RUN) {
  console.error(
    `PROSPECTIVITY GATE: NOT_RUN — ${NOT_RUN}. ` +
      `No prospectivity claim is verified and none may be reported as verified.`,
  );
}

// --- 5a. Classifier behaviour on synthetic repositories -------------------
// Hand-calculable: each fixture's commit order is written literally below, so
// the expected class is derivable by reading the test, not by running the code.

test("SYNTHETIC: prediction committed one commit before its result => PROSPECTIVE", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  const c1 = commitFiles(dir, { "pred.txt": "I predict X\n" }, "commit 1: prediction");
  const c2 = commitFiles(dir, { "result.json": "{\"x\":1}\n" }, "commit 2: result");
  assert.notEqual(c1, c2, "fixture must produce two distinct commits");

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "PROSPECTIVE",
    `Prospectivity classifier failed to certify a genuinely prospective pair. ` +
      `Prediction added at ${c1}, result added at ${c2} (a strict descendant). ` +
      `Classifier said ${m.klass} (${m.reason}). If this fails the gate is ` +
      `over-strict and would suppress honest prospective claims.`,
  );
  assert.equal(m.predAdd, c1);
});

test("SYNTHETIC: prediction and result in the SAME commit => TIMING_UNVERIFIED, never upgraded", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  const c1 = commitFiles(
    dir,
    { "pred.txt": "I predict X\n", "result.json": "{\"x\":1}\n" },
    "commit 1: prediction AND result together",
  );

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "TIMING_UNVERIFIED",
    `PROSPECTIVITY LAUNDERING: a prediction and the result it predicts entered ` +
      `history in one and the same commit (${c1}), yet the classifier returned ` +
      `${m.klass}. A prediction that first appears alongside its own result ` +
      `carries no evidence of having preceded it. This class must never be ` +
      `upgraded to PROSPECTIVE.`,
  );
  assert.equal(m.reason, "SAME_COMMIT:result.json");
});

test("SYNTHETIC: result committed BEFORE the prediction => TIMING_UNVERIFIED", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  commitFiles(dir, { "result.json": "{\"x\":1}\n" }, "commit 1: result");
  commitFiles(dir, { "pred.txt": "I predict X\n" }, "commit 2: prediction, too late");

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "TIMING_UNVERIFIED",
    `POSTDICTION SOLD AS PREDICTION: the result artifact entered history before ` +
      `the prediction that claims to govern it, yet the classifier returned ` +
      `${m.klass} (${m.reason}).`,
  );
  assert.equal(m.reason, "RESULT_NOT_DESCENDED_FROM_PREDICTION:result.json");
});

test("SYNTHETIC: prediction committed, result does not exist => PENDING", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  commitFiles(dir, { "pred.txt": "I predict X\n" }, "commit 1: prediction only");

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "PENDING",
    `An open prediction whose result does not yet exist must classify PENDING, ` +
      `not ${m.klass}. Got reason ${m.reason}.`,
  );
});

test("SYNTHETIC: result written but NOT committed cannot make a prediction PROSPECTIVE", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  commitFiles(dir, { "pred.txt": "I predict X\n" }, "commit 1: prediction only");
  fs.writeFileSync(path.join(dir, "result.json"), "{\"x\":1}\n", "utf8");

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "TIMING_UNVERIFIED",
    `A result present in the working tree but absent from history leaves the ` +
      `ordering unwitnessed. Classifier returned ${m.klass} (${m.reason}).`,
  );
  assert.equal(m.reason, "RESULT_ON_DISK_BUT_UNCOMMITTED");
});

test("SYNTHETIC: prospectivity is decided by ancestry, NOT by commit timestamps", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  // The result commit is stamped a full year EARLIER than the prediction commit
  // that it descends from. Timestamps are attacker-controlled; ancestry is not.
  const dir = makeRepo();
  const stamp = (dir2, files, message, date) => {
    for (const [rel, body] of Object.entries(files)) {
      fs.writeFileSync(path.join(dir2, rel), body, "utf8");
    }
    git(["add", "-A"], dir2);
    const r = execFileSync(
      "git",
      ["commit", "-q", "--no-verify", "-m", message],
      {
        cwd: dir2,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
        windowsHide: true,
        env: {
          ...process.env,
          GIT_AUTHOR_DATE: date,
          GIT_COMMITTER_DATE: date,
        },
      },
    );
    void r;
    return git(["rev-parse", "HEAD"], dir2).out;
  };

  const c1 = stamp(dir, { "pred.txt": "I predict X\n" }, "prediction", "2026-01-01T00:00:00+0000");
  const c2 = stamp(dir, { "result.json": "{\"x\":1}\n" }, "result", "2025-01-01T00:00:00+0000");
  assert.notEqual(c1, c2);

  const m = measureProspectivity(fixtureRecord(), dir);

  assert.equal(
    m.klass,
    "PROSPECTIVE",
    `Prospectivity must be read off the commit DAG. The result commit here bears ` +
      `an earlier timestamp than its own parent, which is legal in git and freely ` +
      `forgeable. A classifier that consults timestamps would misreport this pair. ` +
      `Got ${m.klass} (${m.reason}).`,
  );
});

test("SYNTHETIC: a fabricated anchor commit is not accepted as an anchor", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const dir = makeRepo();
  commitFiles(dir, { "pred.txt": "I predict X\n" }, "commit 1");
  const bogus = "deadbeef".repeat(5); // 40 hex chars, no such object

  assert.equal(
    commitExists(bogus, dir),
    false,
    `An anchor commit id that names no object in the repository must not resolve. ` +
      `If it did, madeAgainstCommit could be filled with arbitrary text and the ` +
      `prediction would be anchored to nothing.`,
  );
});

// --- 5b. Record schema ---------------------------------------------------

test("Every prediction record is well formed and carries claim, falsifier and anchor", () => {
  assert.ok(
    ALL_RECORDS.length > 0,
    `PROSPECTIVITY GATE HAS NOTHING TO CHECK: zero prediction records were found. ` +
      `The gate must not pass with an empty corpus. Add records to ` +
      `experiments/predictions/*.prediction.json or to EMBEDDED_RECORDS in ` +
      `tests/semantic/prospectivity-provenance.test.mjs.`,
  );

  const seen = new Set();
  for (const rec of ALL_RECORDS) {
    const where = `${rec.__origin}#${rec.recordId ?? "<no recordId>"}`;

    for (const field of RECORD_FIELDS) {
      assert.ok(
        rec[field] !== undefined && rec[field] !== null && rec[field] !== "",
        `Prediction record ${where} is missing required field '${field}'. A record ` +
          `without ${field} cannot support a prospectivity claim.`,
      );
    }

    assert.ok(
      typeof rec.claim === "string" && rec.claim.trim().length >= 20,
      `Prediction record ${where} has no substantive 'claim'. A prospectivity ` +
        `claim over an empty prediction is meaningless.`,
    );
    assert.ok(
      typeof rec.falsifier === "string" && rec.falsifier.trim().length >= 20,
      `Prediction record ${where} has no substantive 'falsifier'. An unfalsifiable ` +
        `prediction cannot be prospectively confirmed, only decorated.`,
    );
    assert.ok(
      Array.isArray(rec.resultPaths) && rec.resultPaths.length > 0,
      `Prediction record ${where} names no result artifacts. A prediction that ` +
        `governs nothing cannot be ordered against anything.`,
    );
    assert.ok(
      VALID_CLASSES.has(rec.prospectivity),
      `Prediction record ${where} declares prospectivity class ` +
        `'${rec.prospectivity}', which is not one of ` +
        `${[...VALID_CLASSES].join(", ")}.`,
    );
    assert.ok(
      /^[0-9a-f]{40}$/.test(rec.madeAgainstCommit),
      `Prediction record ${where} declares madeAgainstCommit ` +
        `'${rec.madeAgainstCommit}', which is not a full 40-character commit id. ` +
        `Abbreviated or symbolic anchors are rejected because they can be ` +
        `re-pointed without editing the record.`,
    );
    assert.ok(
      !rec.resultPaths.includes(rec.predictionPath),
      `Prediction record ${where} lists its own prediction file as a result ` +
        `artifact. That is a circular provenance claim.`,
    );

    assert.ok(
      !seen.has(rec.recordId),
      `Duplicate prediction recordId '${rec.recordId}' at ${where}. Record ids ` +
        `must be unique or a failing record can be shadowed by a passing one.`,
    );
    seen.add(rec.recordId);
  }
});

// --- 5c. The anchor commit is real and in this history --------------------

test("Every prediction anchor commit exists and precedes the prediction it anchors", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  let checked = 0;
  for (const rec of ALL_RECORDS) {
    const where = `${rec.__origin}#${rec.recordId}`;
    const predAdd = newestIntroduction(rec.predictionPath, ROOT);
    const anchorPresent = commitExists(rec.madeAgainstCommit, ROOT);

    if (!anchorPresent && predAdd === null) {
      // Neither the anchor nor the prediction is in this branch's history.
      // The record belongs to a history we cannot see. Report, do not judge.
      console.error(
        `PROSPECTIVITY GATE: NOT_RUN for ${where} — neither anchor ` +
          `${rec.madeAgainstCommit.slice(0, 8)} nor prediction file ` +
          `'${rec.predictionPath}' is reachable from HEAD.`,
      );
      continue;
    }

    assert.ok(
      anchorPresent,
      `FABRICATED PROSPECTIVITY ANCHOR at ${where}: madeAgainstCommit ` +
        `${rec.madeAgainstCommit} names no commit in this repository, yet the ` +
        `prediction file '${rec.predictionPath}' IS in history. A prediction ` +
        `anchored to a non-existent commit pins nothing; its claim to have been ` +
        `made against a known state of the world is unsupported.`,
    );

    assert.ok(
      isAncestor(rec.madeAgainstCommit, "HEAD", ROOT),
      `PROSPECTIVITY ANCHOR OUTSIDE HISTORY at ${where}: madeAgainstCommit ` +
        `${rec.madeAgainstCommit.slice(0, 8)} exists but is not an ancestor of ` +
        `HEAD. The prediction claims to have been made against a state that this ` +
        `line of history never passed through.`,
    );

    if (predAdd !== null) {
      assert.ok(
        isAncestor(rec.madeAgainstCommit, predAdd, ROOT),
        `PROSPECTIVITY ANCHOR INVERTED at ${where}: the prediction file ` +
          `'${rec.predictionPath}' was introduced at ${predAdd.slice(0, 8)}, but ` +
          `its declared anchor ${rec.madeAgainstCommit.slice(0, 8)} is not an ` +
          `ancestor of that commit. The prediction cannot have been written ` +
          `against a state that did not yet exist. This is the commit-graph ` +
          `analogue of a preregistration dated after the results it governs.`,
      );
      checked += 1;
    }
  }

  console.error(
    `PROSPECTIVITY GATE: ${checked}/${ALL_RECORDS.length} anchors verified against ` +
      `commit ancestry.`,
  );
});

// --- 5d. THE GATE: declared class must equal measured class ---------------

test("Declared prospectivity equals prospectivity measured from commit ancestry", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  const summary = [];
  for (const rec of ALL_RECORDS) {
    const where = `${rec.__origin}#${rec.recordId}`;
    const measured = measureProspectivity(rec, ROOT);
    summary.push(`  ${rec.recordId}: declared=${rec.prospectivity} measured=${measured.klass} (${measured.reason})`);

    if (measured.reason === "NOTHING_PRESENT") {
      console.error(
        `PROSPECTIVITY GATE: NOT_RUN for ${where} — neither the prediction file ` +
          `nor any result artifact is present in this tree or its history.`,
      );
      continue;
    }

    // The load-bearing assertion. Named in full so the failure line says what
    // broke, not that a byte moved.
    if (rec.prospectivity === "PROSPECTIVE" && measured.klass !== "PROSPECTIVE") {
      const sameCommit = measured.reason.startsWith("SAME_COMMIT:");
      assert.fail(
        `PROSPECTIVITY VIOLATION at ${where}\n` +
          `  DECLARED : PROSPECTIVE (prediction committed strictly before its result)\n` +
          `  MEASURED : ${measured.klass} — ${measured.reason}\n` +
          `  prediction '${rec.predictionPath}' introduced at ` +
          `${measured.predAdd ? measured.predAdd.slice(0, 8) : "<not in history>"}\n` +
          measured.results
            .map(
              (r) =>
                `  result     '${r.path}' introduced at ` +
                `${r.add ? r.add.slice(0, 8) : r.onDisk ? "<uncommitted>" : "<absent>"}`,
            )
            .join("\n") +
          `\n` +
          (sameCommit
            ? `  A prediction and the result it predicts entered history in ONE AND ` +
              `THE SAME COMMIT. Git cannot witness that the prediction preceded the ` +
              `observation, because both became facts at the same instant of ` +
              `history. This is exactly the defect that mutation M11 exploited: a ` +
              `self-declared ordering with no independent witness.\n`
            : `  The commit graph does not place the prediction strictly before its ` +
              `result.\n`) +
          `  REQUIRED CORRECTION: change 'prospectivity' to "TIMING_UNVERIFIED" and ` +
          `keep the adverse provenance visible. Do NOT re-commit the files to ` +
          `manufacture an ordering that did not happen.`,
      );
    }

    if (rec.prospectivity !== "PROSPECTIVE" && measured.klass === "PROSPECTIVE") {
      assert.fail(
        `PROSPECTIVITY UNDER-DECLARED at ${where}\n` +
          `  DECLARED : ${rec.prospectivity}\n` +
          `  MEASURED : PROSPECTIVE — ${measured.reason}\n` +
          `  Git corroborates that the prediction preceded its result, but the ` +
          `record does not claim it. Either the record is stale or the result ` +
          `artifact list is wrong. A provenance ledger that misreports in the ` +
          `conservative direction is still misreporting.`,
      );
    }

    assert.equal(
      rec.prospectivity,
      measured.klass,
      `PROSPECTIVITY CLASS MISMATCH at ${where}: the record declares ` +
        `'${rec.prospectivity}' but commit ancestry measures '${measured.klass}' ` +
        `(${measured.reason}). The declared class of a prediction record must ` +
        `equal what git can actually witness.`,
    );
  }

  console.error(`PROSPECTIVITY GATE: class ledger\n${summary.join("\n")}`);
});

// --- 5e. The corpus must contain the known adverse case -------------------

test("The known same-commit provenance defect remains declared and visible", (t) => {
  if (NOT_RUN) return t.skip(`NOT_RUN — ${NOT_RUN}`);

  // BOTH known adverse records must survive. Protecting only one let the other
  // be deleted silently, which is what review found.
  const REQUIRED_ADVERSE = [
    { id: "B1-RERUN-ON-C3-FIXED-TREE", committedTogetherIn: "b675978", requireReason: null },
    { id: "C3-CANONICAL-WRITE-FIX", committedTogetherIn: "1630a68", requireReason: "SAME_COMMIT" },
  ];

  for (const want of REQUIRED_ADVERSE) {
    const rec = ALL_RECORDS.find((r) => r.recordId === want.id);
    assert.ok(
      rec,
      `THE ADVERSE PROVENANCE RECORD ${want.id} HAS BEEN REMOVED FROM THE CORPUS.\n` +
        `  That record documents a real provenance failure by this audit: a ` +
        `prediction committed in the same commit (${want.committedTogetherIn}) as the ` +
        `result it predicts. Deleting the record deletes the adverse result.\n` +
        `  Both known adverse records are required: ` +
        `${REQUIRED_ADVERSE.map((w) => w.id).join(" and ")}. Restore it.`,
    );
    assert.equal(
      rec.prospectivity,
      "TIMING_UNVERIFIED",
      `The adverse record ${want.id} has been upgraded to '${rec.prospectivity}'. Its ` +
        `prediction and its result entered history together in ${want.committedTogetherIn}; ` +
        `no ordering was ever witnessed. Upgrading it launders an unverified timing ` +
        `claim into a prospective one.`,
    );

    const measured = measureProspectivity(rec, ROOT);
    if (measured.reason === "NOTHING_PRESENT") continue;

    assert.ok(
      measured.klass !== "PROSPECTIVE",
      `Git now reports ${want.id} as PROSPECTIVE. Since these files were committed ` +
        `together, this can only mean history was rewritten. Ordering evidence that ` +
        `appears after the fact is not evidence.`,
    );

    if (want.requireReason) {
      assert.ok(
        measured.reason.startsWith(want.requireReason),
        `${want.id} must be measured as ${want.requireReason}, proving the actual ` +
          `same-commit event. Measured reason was '${measured.reason}'.\n` +
          `  A generic RESULT_NOT_DESCENDED_FROM_PREDICTION is NOT sufficient: it ` +
          `says only that ancestry could not be shown, which is also what a missing ` +
          `file produces. The record must demonstrate that the prediction and its ` +
          `result entered history in ONE commit.`,
      );
    }
  }
});
