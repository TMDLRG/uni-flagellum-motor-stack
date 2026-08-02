# Phase A — Findings

**Audited commit:** `9c3a644e4b57e8ac27f925dcec84222463063aa1`
**Phase:** A (empirical baseline). Phases B–D not executed.
**Package:** machine-readable artifacts in this directory; hashes in `package-manifest.json`.

Phase A executed the full `CLAUDE.md:107-117` required-validation block on a clean
clone for the first time, plus all three authorized external evidence retrievals.
No source file was modified.

---

## 1. Correction of the record

These corrections are recorded, not silently applied. Items 1–5 were directed;
item 6 was discovered while verifying item 3 and **retracts an earlier claim of
this audit**.

### 1.1 Git sees the working-tree CRLF change; normalized `git diff` does not

An earlier Phase A statement that "git reports a clean tree" is **WRONG and
retracted**.

| instrument | behaviour after the CRLF corruption |
|---|---|
| `git status --porcelain` | ` M public/wadhwa-2022-derived-events.json` — **does report it** |
| `git diff --numstat` | **0 lines** — does not report it |
| `git diff --stat` | empty |
| `git hash-object` (filtered) | `95ad0597…` — equals the index blob |
| `git hash-object --no-filters` | `cc7e3064…` — differs |

The corruption **cannot be committed**, because the normalized blob is unchanged.
But the on-disk bytes served to the browser and hashed by the manifest tests
**are** corrupted. The practical hazard is that a developer sees ` M`, runs
`git diff`, sees nothing, and dismisses it.

### 1.2 X01 is vacuous *as a generated report gate*

The precise scope matters. `scripts/run-cross-study-parity.py:360-363` computes
X01 from JSON literals read out of the corpus file it is meant to validate and
performs **zero** filesystem reads of the artifacts. That gate is vacuous.

Separately, `tests/cross-study-parity.test.mjs` **can** hash real source files
when they are present. Its weakness is different: line 39 wraps the hashing in
`fs.existsSync`, and line 45 explicitly accepts `checkedArtifacts === 0`.

Both statements are true and neither substitutes for the other. Saying "no
source verification exists anywhere" would be an overstatement.

### 1.3 Three motor counts exist — 129, 109 and 99

| count | meaning | source |
|---|---|---|
| **129** | `sourceMotors`, before exclusions | `observed-experiment-report.json` `cohort` |
| **109** | event-producing motors (89 train + 20 holdout) | `wadhwa-2022-events.json` partition tags |
| **99** | **frozen eligible held-out analysis: 80 train + 19 holdout** | `observed-experiment-report.json` `cohort` |

Eligibility filtering drops 9 train and 1 holdout motor between 109 and 99.

### 1.4 The Node 22 discrepancy changes artifact identity, not conclusions

It changes `runId` and the report SHA-256. It does **not** change any current
scientific conclusion: the lognormal baseline still out-scores the mixture and
the `mixtureVsWeibull` interval still straddles zero. Magnitude is 1–2 ULP.

### 1.5 Printed `PASS` literals in `independent-science-check.mjs` are not computed

`scripts/independent-science-check.mjs:48-53` emits `status: "PASS"` and
`publicArtifactMismatchDetected: true` as hard-coded literals inside a
`console.log`. The preceding `assert.equal` calls at `:44-46` are real and would
throw — they pin `fullBiologicalParityAchieved === false`, `G03 === "FAIL"` and
`G10 === "NOT_ESTABLISHED"`.

**Enforcement is genuine; printed output is partly decorative.** Separately,
`:41` asserts `Math.abs(x + (1 - x) - 1) < 1e-14`, which is true for every finite
double — a vacuous assertion inside the designated oracle.

### 1.6 RETRACTION — the earlier "99 motors refuted" claim was wrong

Earlier Phase A prose recorded, as refutation #5, that a prior reconnaissance
claim of "99 motors (80 train + 19 holdout)" was refuted because measurement
showed 109 motors partitioned 89/20.

**That refutation is itself retracted.** The error was checking the *events
file's partition tags* and never opening `observed-experiment-report.json`'s
`cohort` field, which reports `trainMotors: 80` and `holdoutMotors: 19`. The
99-motor cohort is real. The reconnaissance was correct and this audit was
wrong.

The related refutation #6 — that `rightCensoredDwells == 109` is not a
dwell/motor unit error — **stands, and is now explained by mechanism** rather
than asserted: there are exactly 109 right-censored events across exactly 109
distinct motors, at most one per motor. One right-censored final dwell per
event-producing motor. The equality is structural.

---

## 2. STOP CONDITION — the experimental unit for X02 is ambiguous

`CLAUDE.md` and the directive both require stopping rather than forcing progress
when an experimental unit is ambiguous. This is such a case.

`X02_CORPUS_BREADTH` requires *"a conservative direct-artifact lower bound of
400 independent motors/cells."* Its `lowerBoundDerivation` is
`{Antani2021: 154, Ito2021: 40, Lisevich2025: 106, Wadhwa2022: 109}` = **409**.

| convention for "independent motors" | Wadhwa | total | vs 400 |
|---|---|---|---|
| event-producing motors | 109 | **409** | **PASS** |
| the repository's own frozen analysis cohort | 99 | **399** | **FAIL** |

Facts established:

- The 109 is **computed**, not hardcoded: `ingest-cross-study-evidence.py:608`
  evaluates `len({event["motorId"] for event in wadhwa["events"]})`.
- The repository declares an experimental-unit principle at
  `docs/CROSS-STUDY-PARITY.md:38`: *"measurements of one motor remain one
  experimental unit."* This correctly forbids pseudoreplication.
- It does **not** declare whether "independent motors" means *event-producing*
  or *analyzed*. That choice is undeclared.
- The criterion's own word is **"conservative"**, and 109 is the **less**
  conservative of two defensible counts.

**This audit does not assert that X02 fails.** A motor that produced usable
events is arguably an independently observed motor. The finding is that the gate
passes by a 9-motor margin on an undeclared convention, while its own criterion
demands conservatism and the project's own frozen analysis uses the smaller
count.

**Unresolved and required before this can be closed:** whether the 154 / 40 /
106 contributions are event-producing or analyzed counts. If any is also a
generous count, the margin erodes further. This was **not** measured in Phase A.

**Decision required from Michael/Codex** — declare the convention explicitly and
justify it, or recompute the bound under the conservative convention and accept
the resulting gate status. Either is honest. Leaving it undeclared is not.

---

## 3. Adverse findings

### 3.1 CRITICAL — artifact identity depends on the JavaScript engine

See `node-runtime-divergence.json`.

`experiments/results/audit-manifest.json:53` claims that identical protocol,
event-artifact and code identities force an identical report SHA-256. All three
were held constant and only V8 varied; the SHA-256 changed.

| runtime | `runId` |
|---|---|
| Node 22.13.1 / V8 12.4 — **the declared `engines` floor** | `308d09d8…` |
| Node 25.0.0 / V8 14.1 | `1c4b71f4…` ← matches the committed artifact |

The repository cannot reproduce its own frozen evidence on its own declared
minimum runtime, and `tests/observed-experiment.test.mjs:34` fails there.
Determinism holds *within* a version (3/3 identical runs each).

A hypothesis of V8 transcendental drift was **refuted**: `Math.exp`, `Math.log`,
`Math.pow`, `Math.sin` and the full Lanczos `logGamma` are bit-identical across
V8 12.4 and 14.1. The origin is unlocalized and is the subject of red test C1.

### 3.2 HIGH — X01 source integrity is invariant to the evidence

See `x01-empty-vs-full-cache.json`. An empty cache and a cache containing 12
artifacts totalling 75,001,736 bytes, every digest independently verified,
produce a **byte-identical** report (`bd3838c4…`), X01 `PASS` in both.

No `NOT_RUN` or `EXTERNAL_VALIDATION_REQUIRED` status value exists anywhere in
the repository, and no schema or validator constrains status strings. The honest
status is unrepresentable, contrary to `CLAUDE.md:119-121`.

### 3.3 HIGH — the generator corrupts a hash-pinned artifact

See `crlf-mutation-result.json`. `run-observed-experiments.mjs:35` copies across
a `.gitattributes` eol boundary; exactly one file changes,
487,890 → 508,103 bytes (+20,213 CR), and `tests/walkthrough.test.mjs:58` fails
correctly. **The failing test already exists.** The correct write pattern also
already exists in-repo at `run-science-gates.py:590`.

### 3.4 Carried forward, not re-tested in Phase A

`run-science-gates.py:391` and `:404` pass the bare string `"PASS"` for G00 and
G01; `:407` loads `noMotorLeakage` into evidence and never reads it. Compare
`:417`, a real conditional. Mutation testing is Phase B work.

---

## 4. Positive findings, earned by measurement

1. **All 12 Tier-1 upstream digests are genuine** — 75,001,736 bytes, 12/12
   SHA-256 matches. First time these `"verified": true` fields have been checked
   against real bytes retrieved from the published URLs.
2. **The 4.09 GB Ito archive is authentic** — exact bytes, exact MD5, 505 ZIP
   entries, `zipCrcFailure: null`. The regenerated ledger is **byte-identical**
   to the committed one: the committed `PASS` was a truthful record.
3. **The raw → derived chain reproduces exactly.** The raw `.mat` matches
   `c14de12c…` and re-derivation is content-identical to the committed artifact.
4. **npm 10 compatibility is confirmed** across a fully crossed 2×2; the
   `overrides`/lockfile divergence does not break `npm ci`. The lockfile never
   left blob `984bc7f4…`, so commit `0c73d94` was never silently reverted.
5. **Production dependencies: 0 vulnerabilities.** All 12 are development-only.
6. **The adverse lognormal result survives independent rederivation** by
   `scripts/independent-statistical-check.py`, which imports zero repository
   modules: lognormal `-3.0129` vs mixture `-3.0498`.

---

## 5. Independence statement

Required by the directive: *do not claim the audit package is independent unless
its oracle does not import the implementation under test.*

| measurement | oracle | independent of the implementation? |
|---|---|---|
| Tier-1 digests, Node zip, Wadhwa `.mat` | PowerShell `Get-FileHash` | **Yes** — no repository code |
| Ito archive MD5 / SHA-256 | PowerShell `Get-FileHash` | **Yes** |
| Ito structural verification | the repository's own script | **No** — corroborated by the independent MD5 above |
| raw-vs-index blob identity | `git hash-object` + `Get-FileHash` | **Yes**, two agreeing oracles |
| **cross-runtime `runId` divergence** | harness importing `lib/observed-experiment.js` | **NO — imports the implementation under test** |

The `runId` harness deliberately imports the implementation, because it measures
that implementation's cross-runtime reproducibility, **not** its correctness. It
is not, and is not claimed to be, an independent mathematical oracle.

**No independent mathematical oracle was constructed in Phase A.** Independent
rederivation of the bootstrap, the first-passage densities, the EFE/VFE algebra
and the paper anchors is Phase B (B2) work and has not been done.

---

## 6. Explicitly not done

- Phase B: mutation battery, independent mathematics, model competition,
  identifiability, prospective design.
- Phase C: any production-code correction. No source file modified.
- Localization of the `runId` divergence.
- `npm run cross-study:ingest` — NOT RUN. Undeclared dependency on the Ito ledger
  (`ingest-cross-study-evidence.py:253-258`), and `:255` writes `public/` before
  later stages can fail.
- Corrupted-cache and substituted-cache X01 states.
- `core.autocrlf=false` and `input` behaviour.
- Whether the 154 / 40 / 106 motor contributions use the same counting
  convention as Wadhwa's 109.
- No push, tag, deploy or external mutation occurred.

---

## 7. Reproduction

```bash
git clone https://github.com/TMDLRG/UNI-FLAGELLUM.git && cd UNI-FLAGELLUM
git checkout 9c3a644e4b57e8ac27f925dcec84222463063aa1

# 3.1 requires two Node runtimes; expect different runIds
npm ci && npm test          # exit 0 on Node 25.x, exit 1 on Node 22.13.x

# 3.2 the tautology; no download required
python scripts/run-cross-study-parity.py
sha256sum experiments/results/cross-study-parity-report.json
# populate experiments/upstream-cache/ then re-run; the digest is unchanged

# 3.3 expect exactly one changed file, and git diff to report nothing
node scripts/run-observed-experiments.mjs
git diff --numstat                        # 0 lines
node --test tests/walkthrough.test.mjs    # fails at :58
```
