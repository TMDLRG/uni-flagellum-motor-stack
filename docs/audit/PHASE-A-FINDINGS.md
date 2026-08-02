# Independent Audit — Phase A Findings

**Audited commit:** `9c3a644e4b57e8ac27f925dcec84222463063aa1` (`main`)
**Auditor:** Claude Opus 4.8, independent verification engineer
**Contracts followed:** `CLAUDE.md`, `docs/CLAUDE_ULTRACODE_INDEPENDENT_AUDIT_PROMPT.md`
**Flow:** `OBSERVE → BOUND → PREDICT → ACT → VERIFY → FALSIFY → UPDATE → RECORD`
**Status:** Phase A (empirical baseline) complete. Phases B–D not started.

This document exists to be reviewed and challenged. Predictions were committed
before execution; refutations of the auditor's own claims are recorded in
§7 rather than silently corrected.

---

## 1. Scope and method

Phase A executed the full `CLAUDE.md:107-117` required-validation block for the
first time, on a genuinely clean clone, plus all three authorized external
evidence retrievals.

**Isolation discipline.** The primary checkout was never written to. All
execution occurred in five independent `--no-hardlinks` clones. `git worktree`
was deliberately *not* used, because `worktree add` writes metadata into the
primary's `.git/`. The primary was proved byte-identical to its pre-audit state
by raw on-disk hashing of all 106 tracked files (not by `git status` — see §4③).

**Instrument.** Two independent hash oracles were used throughout
(`git hash-object --no-filters` and PowerShell `Get-FileHash`), cross-checked
and agreeing on all 106 files. Raw on-disk hashing was used for every
comparison because git's content model is blind to the defect class in §4③.

**Environment.** Windows 11 build 26200, i7-10700T 8C/16T, 63.7 GB RAM.
Node v25.0.0 / npm 11.6.2 ambient; Node v22.13.1 / npm 10.9.2 provisioned as a
checksum-verified portable extraction with zero global mutation.
Python 3.12.10, numpy 2.3.5, scipy 1.16.3 (exact match to
`requirements-experiments.txt`). See `evidence/host.txt`.

---

## 2. Gate ledger — all gates executed

| Gate | Result | Note |
|---|---|---|
| `npm ci` | **PASS** | all four matrix cells, exit 0 |
| `npm test` | **PASS** (Node 25) / **FAIL** (Node 22.13.1) | see §4① |
| `npm run lint` | **PASS** | exit 0 |
| `npx tsc --noEmit` | **PASS** | exit 0 |
| `npm run science:verify` | **PASS** | exit 0 |
| `npm run cross-study:verify` | **PASS** | exit 0 |
| `npm run experiment:verify` | **PASS** | independent Python oracle |
| `npm run cross-study:verify-raw` | **PASS** | was BLOCKED; now earned, §5② |
| `npm audit --omit=dev --audit-level=moderate` | **PASS** | **0 production vulnerabilities** |
| `npm audit` | **FAIL** | 12 (1 low, 5 moderate, 6 high) — **all development-only** |

Excluded by design: `db:generate` (writes tracked `drizzle/meta/_journal.json`)
and `scripts/export-cad.mjs` (unwired to any npm script). Neither is in the
required-validation set.

### npm / Node compatibility matrix

| Cell | Node | npm | `npm ci` | `npm test` |
|---|---|---|---|---|
| A | 25.0.0 | 11.6.2 | exit 0 | **exit 0** |
| B | 25.0.0 | 10.9.8 | exit 0 | **exit 0** |
| C | 22.13.1 | 10.9.2 | exit 0 | **exit 1** |
| D | 22.13.1 | 11.6.2 | exit 0 | **exit 1** |

Fully crossed. The failure depends solely on the **Node** axis; the npm axis has
no effect. `package-lock.json` was verified to remain at blob
`984bc7f4d989d4872ea00354c529ae22a13de1e1` after *every* npm invocation —
commit `0c73d94` was never silently reverted.

**`CLAUDE.md:105` (npm 10 compatibility) is CONFIRMED.** The suspected hazard —
`package.json:50-52` declaring `overrides.postcss` while `package-lock.json`
contains no `overrides` key — does **not** break npm 10's `ci` sync check.

---

## 3. Test accounting

`34` is the first `node --test` invocation over five files:
`model(9) + observed-experiment(7) + science-gates(5) + cross-study-parity(6) + walkthrough(7) = 34`.
`tests/rendered-html.test.mjs` is a **35th** case in a separate post-build
invocation that imports `dist/server/index.js`. Because `package.json:12` chains
with `&&`, a failure in the first invocation means the build never runs and the
35th test **never executes** — it is `NOT RUN`, not passing.

---

## 4. Adverse findings

### ① CRITICAL — artifact identity depends on the Node version

`experiments/results/observed-experiment-report.json` carries `runId`
`1c4b71f42193bb74edd5634da6ff1ea38dd3ab4767f9aadfb783d4a5b0def666`.

| Runtime | `runId` produced |
|---|---|
| Node 22.13.1 (V8 12.4) — **the declared `engines` floor** | `308d09d83fe556ef9d4ea03948ae34acbebcb5f8493a73cec773bb41d6dd1884` |
| Node 25.0.0 (V8 14.1) | `1c4b71f42193bb74edd5634da6ff1ea38dd3ab4767f9aadfb783d4a5b0def666` ✅ matches committed |

**Affected claim.** `experiments/results/audit-manifest.json:53` states:

> *"Run the analysis twice from identical protocol, event artifact, and code
> identities; the report SHA-256 must be identical."*

All three named identities were held constant. Only V8 differed. The report
SHA-256 changed. **The stated determinism condition is insufficient** — the true
condition includes the JavaScript engine version.

**Consequence.** `package.json:6` declares `engines.node >= 22.13.0`, but on that
exact floor the repository cannot reproduce its own frozen evidence and
`tests/observed-experiment.test.mjs:34` fails.

**Magnitude — stated plainly so this is not over-read.** The divergence is 1–2
ULP (17th significant digit), confined to the 2000-replicate bootstrap interval
`mixtureVsWeibull` and a small number of Weibull calibration entries:

```
weibull            0.05514041629405715  vs  0.05514041629405717
mixtureVsWeibull   lower -0.017969164982541544  vs  -0.01796916498254155
```

**No scientific conclusion moves.** The lognormal still out-scores the mixture;
the interval still straddles zero. This is a reproducibility and
evidence-chain-identity defect, **not** a scientific-invalidity finding.

**Determinism holds within a version.** Three consecutive runs on each of Node
22.13.1 and Node 25.0.0 produced identical `runId`s. This is a clean,
reproducible cross-version dependency, not flakiness.

**Open question (not resolved).** A probe of `Math.exp`, `Math.log`, `Math.pow`,
`Math.sin` and the full Lanczos `logGamma` across V8 12.4 and 14.1 found
**bit-identical** results. The auditor's hypothesis of transcendental drift is
**refuted**. The divergence originates somewhere in the bootstrap accumulation
path and has not yet been localized.

Evidence: `evidence/runid-node22.txt`, `evidence/runid-node25.txt`.

### ② HIGH — `X01_SOURCE_INTEGRITY` is a proven tautology

`scripts/run-cross-study-parity.py:360-363` computes X01 from
`all(item["verified"])` and `cacheVerification["status"] == "PASS"` — JSON
literals read out of the corpus file the gate is meant to validate. It touches
the filesystem zero times.

This was demonstrated empirically, not merely read from source:

| Run | `experiments/upstream-cache/` contents | Report SHA-256 | X01 |
|---|---|---|---|
| 1 | **empty** | `bd3838c40b8d2563…` | **PASS** |
| 2 | **12 artifacts, 75,001,736 B, every digest verified** | `bd3838c40b8d2563…` | **PASS** |

Adding 75 MB of genuine, independently-verified upstream evidence changed the
report by **zero bytes**. Meanwhile X01's own evidence block declares
`"declaredLocalArtifacts": 12` and cites a 4,085,227,742-byte archive.

`tests/cross-study-parity.test.mjs:39` wraps the only real hashing in
`fs.existsSync`, and `:45` explicitly blesses `checkedArtifacts === 0`.

**No `NOT_RUN` or `EXTERNAL_VALIDATION_REQUIRED` status value exists anywhere in
the repository.** The complete vocabulary is `PASS`, `FAIL`, `NOT_ESTABLISHED`,
`BLOCKED_EXTERNAL`, `SOURCE_ONLY`. The honest status is currently
unrepresentable, contrary to `CLAUDE.md:119-121`.

### ③ HIGH — `experiment:run` corrupts a hash-pinned artifact, invisibly to `git diff`

`scripts/run-observed-experiments.mjs:35` performs
`fs.copyFileSync(datasetPath, publicEventsPath)` across a `.gitattributes` eol
boundary. `.gitattributes:3` pins `experiments/data/wadhwa-2022-events.json` to
`eol=crlf` (508,103 B on disk); `public/wadhwa-2022-derived-events.json` is
`eol=lf` (487,890 B). **Both resolve to one identical LF blob in the index.**

Demonstrated end-to-end:

1. Run the three generators → **exactly one** file changes on disk (predicted in
   advance and confirmed): `public/wadhwa-2022-derived-events.json`,
   487,890 → 508,103 B, sha256 `d119ca60…` → `32ec7ebf…`, +20,213 CR bytes.
2. `git diff --numstat` reports **0 lines**. `git diff --stat` is empty. The
   normalized blob is unchanged, so the corruption **cannot even be committed**.
3. `git status --porcelain` shows ` M` — but a developer inspecting with
   `git diff` sees nothing and would reasonably dismiss it as an eol flag.
4. `tests/walkthrough.test.mjs:58` **fails correctly**:
   `WADHWA_2022_EVENTS hash + '32ec7ebf…' - 'd119ca60…'`, exit 1.

**The failing test for this defect already exists.** No new test is required;
the correction should reuse the pattern already used correctly at
`scripts/run-science-gates.py:590` (`write_text(..., newline="\n")`).

Evidence: `evidence/generator-rerun-changed-files.txt`,
`evidence/raw-index-divergence.txt`.

### ④ Prior finding, unchanged by Phase A

`scripts/run-science-gates.py:391` and `:404` pass the bare string `"PASS"` for
`G00_SOURCE_IDENTITY` and `G01_OBSERVATION_BOUNDARY`. Compare `:417`, a real
conditional. `G01` loads `observed_report["audit"]["noMotorLeakage"]` into its
evidence at `:407` and never reads it. Not yet mutation-tested (Phase B).

---

## 5. Positive findings, earned by measurement

### ① All 12 Tier-1 upstream digests are genuine

All 12 artifacts were retrieved from their published Springer/Zenodo URLs and
independently hashed. **12/12 SHA-256 digests match the repository's declared
pins exactly**, totalling precisely 75,001,736 bytes. This is the first time the
`"verified": true` assertions in
`experiments/data/cross-study-motor-evidence.json` have ever been checked
against real bytes. They are true.
Evidence: `evidence/tier1-digest-verification.json`.

### ② The 4.09 GB Ito archive is authentic, and its committed ledger was truthful

Retrieved from Figshare DOI `10.6084/m9.figshare.14371232.v2`. Observed
4,085,227,742 bytes and MD5 `d42879e66142ff7190f256f4276db111` — both exact.
`scripts/verify-ito-raw-archive.py` then confirmed 505 ZIP entries,
10,160,270,466 uncompressed bytes, and `zipCrcFailure: null` — **every member
CRC verified** — in 64 s.

The regenerated ledger is **byte-identical** to the committed
`experiments/results/ito-raw-archive-verification.json` (raw blob
`bd9c386f09fc92af1cff5a59c1300dace28bbc34` before and after). The committed
`PASS` was a truthful record of an archive the repository could not prove it
had.

**Limitation retained:** this tier is pinned by **MD5 only**; no SHA-256 for it
exists anywhere in the repository. MD5 establishes accidental-corruption
integrity, not adversarial provenance. This audit computed and records
SHA-256 `4b266cdedc0242ad3cb6bd2022fde761b06ec275a46ccf8bead56b60f5b5efac`
(`evidence/tier2-independent-hashes.txt`) so a stronger pin is available.

### ③ The raw → derived ingestion chain reproduces exactly

The Wadhwa raw `.mat` was retrieved at pinned commit `c8311913` and hashes to
`c14de12cc11df8af2ab87f1ec94629eebc249c0e1475c24f850f5a28ddd1ea22` — matching
`experiments/preregistration.v1.json:15` exactly.

Re-deriving through `scripts/ingest-wadhwa-data.py` (output redirected to a
scratch path, never over the tracked artifact) produced a file
**content-identical** to the committed `experiments/data/wadhwa-2022-events.json`
(`JSON.stringify` equality). The full raw → derived transformation is
reproducible from genuine source.

### ④ Sample-size discipline is sound

Direct measurement: 1,349 events across **109 distinct `motorId`s**, partitioned
89 train + 20 holdout = 109. The cross-study corpus uses 109, and
`154 + 40 + 106 + 109 = 409` against `X02_CORPUS_BREADTH`'s threshold of 400.
**X02 is sound.**

Note: the ingest script's *transient stdout* reports `motorCount: 129`
(106 train + 23 holdout) — the pre-exclusion cohort. This number appears in no
artifact and does not propagate. It is a cosmetic logging discrepancy, but a
reader recording it from the console would get a number 20 higher than the
motors actually represented.

### ⑤ The adverse lognormal result survives independent rederivation

`npm run experiment:verify` (`scripts/independent-statistical-check.py`, zero
repo imports, independent SciPy refit) reports:

```
score.lognormal  independent -3.012890173336541   production -3.012890170946554
score.mixture    independent -3.049756690911415   production -3.0497565695441344
```

The lognormal baseline out-scores the project's own two-timescale mixture, and
this is confirmed by a second implementation in a different language. The
repository's most important self-criticism is genuine and independently
replicated.

### ⑥ Other confirmations

- Determinism is exact **within** a Node version (3/3 identical runs each).
- Production dependency tree: **0 vulnerabilities**. All 12 are dev-only.
- CRLF/LF split materializes identically in fresh clones.
- `scripts/verify-ito-raw-archive.py:33-34` hard-exits on a missing cache and
  never fabricates a pass — honest by contrast with X01.

---

## 6. Nuance on the "independent" oracle

`scripts/independent-science-check.mjs` emits `status: "PASS"` and
`publicArtifactMismatchDetected: true` as **hard-coded literals** inside its
`console.log` (`:48-53`). However, the `assert.equal` calls at `:44-46` are real
and would throw — they pin `fullBiologicalParityAchieved === false`,
`G03 === "FAIL"` and `G10 === "NOT_ESTABLISHED"`.

**Its enforcement is genuine; its reported output is partly decorative.** Both
facts belong in the record. Separately, `:41` contains
`assert.ok(Math.abs(x + (1 - x) - 1) < 1e-14)`, which is identically true for
every finite double — a vacuous assertion inside the designated oracle.

---

## 7. Refutations — including of the auditor's own claims

Recorded rather than silently corrected, per `CLAUDE.md:33-35`.

| # | Claim | Status |
|---|---|---|
| 1 | *Auditor:* "`git status` will report a clean tree after CRLF corruption" | **Refuted.** `git status` shows ` M`; it is `git diff` that reports nothing. |
| 2 | *Auditor:* the external requirement is "a 4.09 GB archive" | **Refuted.** Two distinct tiers: 75 MB (SHA-256) + 4.09 GB (MD5). |
| 3 | *Auditor:* retrieval information may be missing from the repo | **Refuted.** All 13 artifacts plus the raw `.mat` have in-repo URLs or DOI+commit. |
| 4 | *Auditor:* V8 transcendental drift explains the `runId` divergence | **Refuted.** Primitives and `logGamma` are bit-identical across V8 12.4 and 14.1. |
| 5 | *Prior recon:* only 99 Wadhwa motors are analyzed → 399 vs a 400 threshold → X02 fails | **Refuted.** 109 motors, all partitioned; 409 vs 400; X02 passes. |
| 6 | *Prior recon:* `109` may be `rightCensoredDwells` mistaken for a motor count | **Refuted.** 109 is the true count of distinct `motorId`s. The coincidence is real but meaningless. |

---

## 8. Resonance ledger

| Axis | Pre-audit | After Phase A | Driver |
|---|---|---|---|
| 1 source observation & provenance | DISSONANT | **PARTIAL ↑** | every upstream digest verified genuine; raw→derived chain reproduces |
| 2 variables, units, equations | PARTIAL | PARTIAL | untouched by Phase A |
| 3 implementation & deterministic runtime | PARTIAL | **DISSONANT ↓** | §4① Node-dependent artifact identity |
| 4 prospective prediction | DISSONANT | DISSONANT | unrecoverable; no tags, no signatures |
| 5 UI truth badge & species label | DISSONANT | DISSONANT | untouched by Phase A |
| 6 gate criterion & result | PARTIAL | **DISSONANT ↓** | §4② vacuity now *proven*, not inferred |
| 7 report, export, artifact hash | PARTIAL | PARTIAL | mirrors byte-exact; reproduction command now qualified by §4① |

**Thesis, now empirically confirmed at four independent points** (G01, X01, the
Ito ledger, the raw ingestion chain): *the repository's claims are substantially
true; the gates that assert them frequently do not test them.* The science is
honest; several guarantees are unearned.

---

## 9. Explicitly NOT done

- **Phase B** — mutation battery (12 mandated mutations + 4 named falsifiers),
  independent rederivation of bootstrap intervals, EFE algebra verdict.
- **Phase C** — any code correction. No source file has been modified.
- **Phase D** — deep falsification, model competition, validity-domain map.
- The `runId` divergence has **not** been localized to a specific operation.
- `npm run cross-study:ingest` was **not** run. It has an undeclared dependency
  on `verify-raw` (`scripts/ingest-cross-study-evidence.py:253-258` raises
  unless the Ito ledger is `PASS`), and `:255` writes `public/` before later
  stages can fail — a partial-run mutation hazard.
- No push, publish, tag, deploy, or external mutation occurred.

---

## 10. Reproduction

```bash
git clone https://github.com/TMDLRG/UNI-FLAGELLUM.git && cd UNI-FLAGELLUM
git checkout 9c3a644e4b57e8ac27f925dcec84222463063aa1

# §4① — requires two Node runtimes; expect different runIds
npm ci && npm test          # exit 0 on Node 25.x, exit 1 on Node 22.13.x

# §4② — the tautology, no download required
python scripts/run-cross-study-parity.py
sha256sum experiments/results/cross-study-parity-report.json
# populate experiments/upstream-cache/ then re-run; the digest is unchanged

# §4③ — expect exactly one changed file, and `git diff` to report nothing
node scripts/run-observed-experiments.mjs
git diff --numstat            # 0 lines
node --test tests/walkthrough.test.mjs   # fails at :58
```

---

## 11. Decision points for the reviewing agent

1. **§4① severity.** Is a Node-version-dependent `runId` a release blocker, or a
   documentation fix (`engines` pin + a stated reproduction runtime)? Note that
   pinning `engines.node` to the runtime that actually produced the artifacts
   would make the claim true without touching any science.
2. **§4② remediation shape.** Introducing `NOT_RUN` touches nine files. Should
   the status vocabulary become a validated single source of truth (none exists
   today — a typo'd status renders unstyled, unglossed, and fails no test)?
3. **§4③ correction choice.** Normalize on write, or unify the `.gitattributes`
   eol? The latter changes the on-disk bytes of
   `experiments/data/wadhwa-2022-events.json` and cascades into
   `audit-manifest.json:18` and the dual-identity problem.
4. **Published-number cascade.** If G00/G01 become real conditionals and any
   status changes, `runId` changes and README / `docs/SCIENCE-GATES.md` / the
   walkthrough / the UI must move together in one auditable commit.
   Pre-committed rule: report whether the number moved *before* any framing.
5. **Phase B ordering.** Recommend independent rederivation of the mixture fit
   **before** any deeper model competition: if the mixture sits on a local
   optimum of the grid-then-refine search at
   `lib/observed-experiment.js:105-135`, every comparison against it — including
   the celebrated lognormal result — is a comparison against a mis-fit model.
6. **`README.md:23` instructs `npm install`**, which under npm 11 rewrites
   `package-lock.json` and silently reverts commit `0c73d94`. Only `npm ci` is
   safe. Recommend correcting the instruction.
7. **`README.md:89` calls `cross-study:verify-raw` "optional"**; `CLAUDE.md:127`
   lists it as required, and it is in fact a hard dependency of
   `cross-study:ingest`. Recommend resolving toward `CLAUDE.md`.
