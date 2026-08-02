# Phase-E audit — scientific math workbench and repository state

**Audited tree:** `feature/scientific-math-workbench` at `c23f686`, worktree
`UNI-FLAGELLUM-math-workbench`.
**Audit date:** 2026-07-21.
**Method:** six parallel dimension audits (truth contract, numerical rederivation,
test adversarial, documentation drift, product/runtime, data provenance), each finding
then put to an independent adversarial verifier instructed to refute it by default;
plus a completeness critic tasked with finding what the six dimensions missed; plus
direct execution by the orchestrator.

**Raw findings 74 · confirmed after adversarial verification 55 · refuted 19.**
Confirmed severities: 2 blocking, 9 major, 18 minor, 26 informational.

The two blocking findings were **not** produced by the six dimensions. They were found
by the completeness critic and then confirmed by direct execution. This is itself the
audit's most important methodological result: a dimension set aimed at the served page
audited the shop window and missed the instrument behind it.

---

## 1. Observed outcomes

Every gate in the `CLAUDE.md` required-validation block was executed in this worktree
on 2026-07-21. Literal results:

| Gate | Result | Evidence |
|---|---|---|
| `npm test` | **PASS** | 103/103, then build, then `tests/rendered-html.test.mjs` 2/2 |
| `npm run build` | **PASS** | 5/5 vinext environments; routes `/`, `/math-workbench` |
| `npx tsc --noEmit` | **PASS** | no diagnostics |
| `npm run lint` | **PASS** | no diagnostics |
| `npm run science:verify` | **PASS** | 244 holdout intervals; mean log score `-3.8380834245644038`/interval; `publicArtifactMismatchDetected: true` |
| `npm run cross-study:verify` | **PASS** | 0 failures; `itoLeaveOneBinOutRmse 0.8293641328245378`, `latticeFittedSse 0.04976772774792293`, `rftRmse 1.7274106879853608`, 10 audit artifacts |
| `npm run cross-study:verify-raw` | **BLOCKED** | `experiments/upstream-cache/ito-2021-raw-data.zip` absent (4.09 GB, gitignored) |
| `npm audit --omit=dev --audit-level=moderate` | **PASS** | 0 vulnerabilities (production) |
| `npm audit` (including dev) | **13 vulnerabilities, 8 high** | `vite` 8.0.0–8.0.15, `ws` 8.0.0–8.20.1, `undici`/`miniflare` |

Production and development dependency risk are reported separately, as required.
`cross-study:verify-raw` is **BLOCKED**, not passed, and must never be reported as a
pass from this clone.

**Executable-surface sweep (orchestrator, headless).** 81 corner trajectories × 200
steps (16,200 agent steps) across all four declared slider ranges at min/default/max;
320 duration-calculator cells over eight states × ten durations spanning `1e-3`–`1e8` s;
72 DLT cells. Results: no non-finite value; posterior and policy posterior normalise to
1 within 1e-9; surprise never negative; stators within [0,11]; speed never negative; two
identical 100-step runs bit-identical; `P₊ + P₋ = −dS/dt` to <1e-4 relative; mean dwell
equals ∫S dt to <1e-3. **No defect found in this sweep.**

---

## 2. Blocking findings

### E-B01 — A gate renders PASS with zero evidence on disk

- **Severity:** blocking. **Affected claim:** `X01_SOURCE_INTEGRITY: PASS`, and by
  conjunction every cross-study parity claim that rests on source integrity.
- **File and line:** `experiments/data/cross-study-motor-evidence.json`
  (`sourceIntegrity.localArtifacts`), surfaced at
  `app/math-workbench/scientific-math-workbench.tsx:377` via `statusClass`;
  guard at `tests/cross-study-parity.test.mjs:37,45`.
- **Reproduction and evidence:**
  ```
  X01_SOURCE_INTEGRITY -> PASS
  declared artifacts: 12
  present on disk  : 0
  all verified==True? True
  experiments/upstream-cache: No such file or directory
  ```
  The gate's own criterion begins *"Every cached artifact matches its frozen SHA-256 and
  byte size; each ZIP passes CRC testing…"*. No cached artifact exists.
  `tests/red/c2-source-byte-gate.test.mjs` already fails at HEAD with exactly this
  diagnosis and is excluded from `npm test` by design.
- **Root cause:** the gate result is derived from frozen `verified: true` claims inside
  the evidence file rather than from current verification.
  `tests/cross-study-parity.test.mjs:37` asserts `artifact.verified === true` — reading
  the claim — and `:45` short-circuits on `checkedArtifacts === 0`, making the block
  vacuous precisely when the evidence is absent.
- **Minimal correction:** compute X01's status at report-generation time from artifacts
  actually present. When `experiments/upstream-cache/` is absent, X01 must emit
  `BLOCKED_EXTERNAL`, not `PASS`. Remove the `checkedArtifacts === 0` short-circuit so
  the test fails rather than passes vacuously.
- **Required failing test:** a test asserting that for every
  `sourceIntegrity.localArtifacts[]` entry, either the file exists and its SHA-256
  recomputes, or the gate status is not `PASS`.
- **Validation:** `npm run cross-study:run && npm run cross-study:verify && npm test`.
- **Rollback:** revert the status-computation commit; the report regenerates.
- **Scientific impact:** this is a direct violation of the `CLAUDE.md` required-validation
  clause *"If a required dataset, archive, instrument, credential, or service is absent,
  mark its gate `BLOCKED`, `NOT RUN`, or `EXTERNAL VALIDATION REQUIRED`; never report a
  pass."* A green badge on the only served page currently asserts verified source
  integrity that has not been performed in this clone.

### E-B02 — A green test enforces a truth-contract violation

- **Severity:** blocking. **Affected claim:** the `OBSERVED` truth class itself.
- **File and line:** `lib/walkthrough.js:356-359`; enforced at
  `tests/walkthrough.test.mjs:41`.
- **Evidence:**
  ```js
  export function truthClassForMode(mode) {
    if (mode === "OBSERVED_REPLAY" || mode === "LIVE_INSTRUMENT") return "OBSERVED";
  ```
  ```js
  assert.equal(truthClassForMode("LIVE_INSTRUMENT"), "OBSERVED");
  ```
- **Root cause:** an unpinned live serial stream is classified `OBSERVED` and written into
  every exported lesson record via `createObserverRecord` (`lib/walkthrough.js:387`).
  `CLAUDE.md` permits `OBSERVED` only for *source-pinned recorded measurements*; a live
  instrument frame has no source pin, no protocol id and no hash.
  `audits/phase-b/b1-mutation-ledger.json` already records this as `M03b … SURVIVED`
  — *"the derived-labelled-OBSERVED route is live and unguarded"* — an open, recorded,
  undischarged hole.
- **Minimal correction:** introduce a distinct class for live instrument data
  (`LIVE_UNPINNED` or equivalent) and update `TRUTH_CLASSES`; or require a source pin
  before `OBSERVED` is returned. Update `tests/walkthrough.test.mjs:41` to assert the
  new class — the test currently pins the violation and must be changed with the code.
- **Required failing test:** a semantic test asserting that no runtime mode without a
  `sourceBinding`/pin can yield `OBSERVED`.
- **Validation:** `npm test`.
- **Mitigating fact, recorded not used as an excuse:** the walkthrough is not served at
  HEAD (`/` redirects to `/math-workbench`), so no user currently sees this label. The
  code path and the test that enforces it are both live in the tree.
- **Scientific impact:** this is the exact truth-laundering the contract exists to
  prevent, and it is currently protected by a passing test.

---

## 3. Major findings

### E-M01 — The shipped expected free energy double-counts ambiguity

- **Severity:** major. **Affected claim:** the `EFE` equation card
  (`G(π) = risk + ambiguity − information gain + effort`), `docs/SCIENCE.md:83`, and
  worksheet 5, which instructs the reader to compute a value the tool does not produce.
- **File and line:** `lib/uni-motor.js:328`.
- **Evidence.** `informationGain = entropy(qOutcome) − ambiguity` (`:326`), and `risk`
  (`:318`) is a **cross-entropy** `−Σ q(o) ln C(o)`, not a KL divergence. Substituting:

  ```
  G_code = crossEntropy + ambiguity − (H[q(o)] − ambiguity) + effort
         = (crossEntropy − H[q(o)]) + 2·ambiguity + effort
         = KL[q(o) ‖ C]        + 2·ambiguity + effort
  ```

  Independent numerical confirmation (`crossEntropy − H == KL` verified to 1e-12;
  `G_code == KL + 2·ambiguity` verified to 1e-12). On the real model after 40 steps:

  | policy | `G` shipped | ambiguity | `G` canonical | inflation |
  |---|---|---|---|---|
  | RUN | 2.087727 | 0.802929 | 1.284799 | +62.5 % |
  | TUMBLE | 2.057086 | 0.776965 | 1.280121 | +60.7 % |

  The error does **not** cancel between policies, because the duplicated ambiguity differs
  per policy. `G(RUN) − G(TUMBLE)` is `0.030642` shipped versus `0.004678` canonical — a
  6.5× inflation of the decision-relevant difference, moving the policy posterior from
  `[0.495322, 0.504678]` to `[0.469397, 0.530603]`. **This changes action selection.**
- **Root cause:** `risk` is a cross-entropy while the assembly at `:328` is written as if
  it were a KL divergence, so the epistemic term is both added (as `ambiguity`) and
  subtracted-then-re-added (inside `−informationGain`).
- **Minimal correction:** delete the `+ ambiguity` addend at `:328`, giving
  `efe = risk − informationGain + effort`, which is identically `KL + ambiguity + effort`.
  Land this **in one commit together with** `docs/SCIENCE.md:83` and
  `scientific-math-workbench.tsx:125`, so declared equation, implementation and UI never
  disagree mid-sequence.
- **Required failing test:** an independent-oracle test that computes
  `KL[q(o)‖C] + ambiguity + effort` from the posterior without importing `policyTerms`,
  and asserts equality with `agent.efe` to 1e-12. It must fail on the current tree.
- **Validation:** `npm test`; the closed-loop trajectory changes, so any pinned
  trajectory fixture must be regenerated and the regeneration recorded.
- **Rollback:** revert the single commit.
- **Scientific impact:** a shipped scientific equation is wrong, and the repository's own
  record predicted this gap: `audits/phase-a/phase-a-findings.md:227-228` states that
  independent rederivation of the EFE/VFE algebra *"is Phase B (B2) work and has not been
  done"*, and `docs/audit/PHASE-A-FINDINGS.md:336` lists "EFE algebra verdict" under
  *Explicitly NOT done*. This audit supplies that verdict, and it is adverse.

### E-M02 — Four CSS custom properties are used and never declared

- **Severity:** major. **Affected claim:** the entire visual truth-status channel on the
  only served page.
- **File and line:** `app/globals.css` — 21 `var()` references to `--cyan`, `--gold`,
  `--void`, `--failure`; zero declarations anywhere in the repository. `:root` declares
  sixteen different tokens (`--signal`, `--prediction`, `--ground`, `--danger`, …).
- **Evidence:** `grep -c "var(--cyan\|var(--gold\|var(--void\|var(--failure)" → 21`;
  `grep "\-\-cyan:\|--gold:\|--void:\|--failure:" → no match`.
- **Root cause:** the workbench stylesheet was written against a token vocabulary that
  differs from the one `:root` defines.
- **Consequence:** every one of the 21 declarations is invalid-at-computed-value-time.
  The `ProbabilityRow` bars render fully transparent (invisible), and the
  `.workbench-status pass` / `fail` / `unresolved` badges render identically — the
  PASS/FAIL/UNRESOLVED colour channel is dead.
- **Minimal correction:** add four aliases to `:root`
  (`--cyan: var(--signal); --gold: var(--prediction); --void: var(--ground);
  --failure: var(--danger);`) or rewrite the 21 call sites. Four lines, fully reversible.
- **Required failing test:** parse `app/globals.css`, extract every `var(--name)`
  reference and every `--name:` declaration, assert reference ⊆ declaration. Currently red
  for four names.
- **Scientific impact:** the badge colour is one of the seven declared resonance axes
  ("UI truth badge and species label"). It is currently non-functional, and this was not
  detected by the reported live browser testing.

### E-M03 — The strongest truth claim in the repository is guarded by a vacuous regex

- **Severity:** major. **File and line:** `tests/rendered-html.test.mjs:37`.
- **Evidence:** `assert.match(html, /full biological parity[\s\S]*?FALSE/i)`. The lazy
  any-character bridge plus `/i` lets the nav buttons' `aria-pressed="false"` satisfy the
  match. The assertion cannot fail even if the rendered parity value were `TRUE`.
- **Minimal correction:** assert the exact data-bound substring
  (`/full biological parity <!-- -->FALSE<\/code>/`), or parse
  `crossStudy.summary.fullBiologicalParityAchieved` from the flight payload and assert
  `=== false`. Deleting the `/i` flag alone is the one-character stopgap.
- **Companion:** `:36` `assert.match(html, /B3[\s\S]*?PENDING/)` is satisfied by a
  hardcoded literal `PENDING` span in the flow tab, so it passes even if the data-bound
  B3 prospectivity string were replaced by a fabricated result (E-m10).

### E-M04 — Truth-laundering on the product's badge surface is undetectable

- **Severity:** major. **File and line:**
  `app/math-workbench/scientific-math-workbench.tsx:80` (`modelCatalog`).
- **Evidence:** no test in the suite reads `modelCatalog`. Relabelling all eleven `truth`
  strings to `"OBSERVED"` leaves `npm test` (103/103), the build, `tsc` and lint green.
- **Root cause:** `modelCatalog` is a module-private literal inside a client component
  with no exported surface and no schema.
- **Minimal correction:** move `modelCatalog` to a plain data module, export it, constrain
  `truth` to a frozen allow-list, and assert that only entries whose `source` resolves
  into a source-pinned module may carry an `OBSERVED`-class label.
- **Scientific impact:** `CLAUDE.md` names this exact mutation class as one the suite must
  detect: *"Mutation tests must demonstrate that truth laundering … [is] detected."*
  It is not.

### E-M05 — Five of six workbench views have zero rendered-HTML coverage

- **Severity:** major. **File and line:** `tests/rendered-html.test.mjs:29`.
- **Evidence:** the workbench is a client component whose default view is `"flow"`; only
  the flow tab is server-rendered. The equation library, gate ledgers, both calculators,
  the planned/not-run panel and the twelve printable worksheets are never rendered by any
  test.
- **Minimal correction:** either add a non-DOM structural test importing `modelCatalog`
  and the gate-status classifier, or drive the initial view from a search parameter so
  `/math-workbench?view=evidence` is server-renderable and assertable. The latter also
  makes each view deep-linkable and citable.

### E-M06 — The analysis-code provenance pin is stale

- **Severity:** major. **File and line:**
  `experiments/results/observed-experiment-report.json:9`
  (`identities.analysisCodeSha256`).
- **Evidence:** `lib/observed-experiment.js` was refactored in `09ec601` and now hashes to
  `85a4a2e9…`; the frozen report, `experiments/results/audit-manifest.json` and
  `public/observed-experiment-report.json` all still declare `b757971e…`. No test in
  `npm test` re-verifies the pin.
- **Minimal correction:** re-run `npm run experiment:run` so all three carry the current
  digest, and add the manifest-verification loop (mirroring
  `tests/science-gates.test.mjs:62-66`) to `tests/observed-experiment.test.mjs`. The
  numeric report must be unchanged; the existing replay test proves it.
- **Do not** rewrite the `preMutationSha256: b757971e…` entries under `audits/phase-c`
  and `audits/phase-d` — those are append-only history.

### E-M07 — The shipped worker bundle leaks build-machine absolute paths

- **Severity:** major. **File and line:** `dist/server/index.js:14546`.
- **Evidence:** the Cloudflare worker bundle hard-codes absolute Windows build-machine
  filesystem paths — including the developer's username — as the `@font-face` `src` URLs.
  Every deployed page emits them in its `<head>`, so all Geist/Geist Mono font requests
  fail and the local path is publicly disclosed. Eleven font files ship unreferenced.
- **Root cause:** a path-separator bug inside `vinext`'s font plugin
  (`node_modules/vinext/dist/plugins/fonts.js`), not repository code.
- **Minimal correction:** drop `next/font/google` from `app/layout.tsx` and reference the
  already-emitted `woff2` files with hand-written `@font-face` rules using `/assets/…`
  URLs. This additionally removes a build-time network fetch to `fonts.gstatic.com`.
- **Note:** established by reading the plugin source on a Windows build host. Linux/CI
  build behaviour is **NOT VERIFIED**.

### E-M08 — "Prediction residual" is not a residual

- **Severity:** major. **File and line:**
  `app/math-workbench/scientific-math-workbench.tsx:325`.
- **Evidence:** the tile renders `observation.ligandUm − agent.predictedLigandUm`, but
  `predictedLigandUm` is computed *from that same observation* inside the same `stepAgent`
  call (`lib/uni-motor.js:375`). The displayed number is algebraically `−signedRate·0.25`
  and can never be a prediction-versus-later-observation residual.
- **Root cause:** the prediction and the observation it is differenced against are from the
  same tick.
- **Minimal correction:** either relabel to "model self-term (one-step extrapolation
  offset)" and state that no prospective residual is computed, or carry the previous
  step's `predictedLigandUm` in `SystemState` and difference the *current* observation
  against the *previous* prediction — then the label is earned.
- **Scientific impact:** `docs/VERUM.md` defines `RESIDUAL` as *"observed minus predicted
  with units"* and `PREDICTED` as *"committed forecast for comparison with a later
  observation."* The shipped tile satisfies neither.

### E-M09 — The documented reproduction path does not work

- **Severity:** major. **File and line:** `README.md:9-14`;
  `docs/LIVING-SCIENCE-WALKTHROUGH.md:132`.
- **Evidence:** both instruct the reader to complete the thirteen-step walkthrough at the
  root URL. `/` returns HTTP 307 to `/math-workbench`; the walkthrough is unreachable in
  the committed deploy.
- **Minimal correction:** add a `STATUS: NOT SERVED` banner to the walkthrough document
  and correct the README's surface inventory. See §6.

---

## 4. What the six dimensions missed

The completeness critic's findings, beyond the two blocking items already given. Each is
grounded in a file read at HEAD; the first four were confirmed by the orchestrator.

1. **`docs/VERUM.md` contradicts `CLAUDE.md` on the definition of `OBSERVED`.**
   VERUM:6 — *"crossed the declared sensor boundary with a timestamp"*. CLAUDE.md —
   *"Only source-pinned recorded measurements may be labelled OBSERVED."* These are
   different contracts, and VERUM's is what licenses both E-B02 and the "Observed ligand"
   label on synthetic data. **Two governing documents disagree; the resolution decides
   whether several findings are defects at all.** This must be settled before the
   builder's truth lattice is frozen.
2. **VERUM declares a closed 11-class vocabulary** and says *"The UI must never upgrade
   one class into another."* The workbench invents roughly seventeen badge strings outside
   it (`RUNNABLE MODEL`, `ADVERSE RETAINED`, `BLIND COVERAGE FAILURE`, `FALSE TODAY`, …).
   The rule is unenforceable against an open vocabulary.
3. **A fabricated timestamp in a provenance artifact.**
   `scripts/verify-ito-raw-archive.py:71` writes `"verifiedAt": "2026-07-17T21:00:00Z"` as
   a hardcoded literal on every run, into `experiments/results/ito-raw-archive-verification.json`
   and its public mirror, and `tests/cross-study-parity.test.mjs:47-51` reads that file as
   evidence. Whatever the byte-reproducibility motive, the field asserts a verification
   time that is not the verification time.
4. **Two SHA-256 identities for one logical artifact.**
   `experiments/data/wadhwa-2022-events.json` (CRLF, `32ec7ebf`, 508 103 bytes) and
   `public/wadhwa-2022-derived-events.json` (LF, `d119ca60`, 487 890 bytes) are the same
   evidence pinned twice, in `observed-experiment-report.json` and in
   `lib/walkthrough.js` respectively.
5. **Circular oracles in the science suite, not just the workbench tests.**
   `tests/cross-study-parity.test.mjs:68-73` asserts on numbers the Python script under
   test computed about itself; nothing rebuilds the 175×175 GMC generator or recomputes
   its stationary eigenvector. `scripts/independent-science-check.mjs:41` contains
   `assert.ok(Math.abs(x + (1 − x) − 1) < 1e-14)`, true for every finite double, and `:48`
   and `:52` emit `status:"PASS"` and `publicArtifactMismatchDetected:true` as hardcoded
   literals. `science:verify` is a required gate.
6. **Four of eight green cross-study gates have no independent rederivation.**
   `scripts/independent-cross-study-check.mjs` re-derives only X03, X06, X08, X09. X02,
   X04, X05 and X07 are not independently checked, contradicting *"Numerically rederive
   important results through an independent implementation."*
7. **The Python side has no runtime identity.** `requirements-experiments.txt` pins
   `numpy==2.3.5 scipy==1.16.3`, but nothing binds any report to them, while the gates
   depend on `least_squares`, `brentq` and `linalg.eig`. The JS side already concluded
   *"artifact identity includes runtime identity"* (`tests/red/README.md`) and never
   applied it. This audit's environment matched by luck: Python 3.12.10, numpy 2.3.5,
   scipy 1.16.3.
8. **Open, undischarged obligations in the ledgers.** `SEMANTIC-COVERAGE-LEDGER.md`
   Entry 3: **AC4 FAILS**, headline is 20 credited not 22; **AF1 is BLOCKING** and its
   "whether to re-run is Codex's call" decision was **never made**; the blind battery
   remains 0/10. `phase-b-roadmap.v2.json` lists B1/B3/B4/B5 as NOT STARTED while
   `b1-mutation-ledger.json` holds 16 results and B3/B4 results exist on a sibling branch
   (§5). `b1-mutation-ledger.json` records that the headline adverse lognormal result is
   defended by **exactly one assertion** (`tests/observed-experiment.test.mjs:47-48`), and
   that removing it leaves all three verify gates green.
9. **The red tests are frozen to `9c3a644e…`, four commits behind HEAD**, so even when
   re-run they cannot measure the current tree. C2 was re-run during this audit and still
   fails.
10. **Mathematical claims with no test at all:** `lib/cad.js` gear geometry (144 lines,
    only three regex string matches); the GMC generator's stoichiometry and Arrhenius
    forms; the lattice `J`-fit's profile likelihood; `logGamma`'s Lanczos approximation
    (`erf` was tested, `logGamma` was not); and `lib/walkthrough.js:361-374`, the only
    place in the repository where joules and nats appear together — tested circularly.
11. **`lib/observed-experiment.d.ts` omits `runObservedExperiment`,** which the module
    exports. Nothing tests that declarations match runtime exports, so `tsc --noEmit`
    passes over drifted types.

---

## 5. Cross-branch state divergence

Not a defect in this branch, but a repository-information fact that changes what this
branch's surface means.

`phase-2/b3-model-competition` contains executed, committed results that this branch
renders as non-existent:

| | this branch | `phase-2/b3-model-competition` |
|---|---|---|
| B3 prospectivity | `PENDING` | `PROSPECTIVE`, flipped in the result commit against prediction commit `e5b4969…` |
| B3 result | absent; the page prints *"B3 has no result in this accepted state"* | `audits/phase-b/b3-model-competition-result.json`, 36 per-cell outcomes, CONFIRMED/UNRESOLVED |
| B4 robustness | `NOT RUN` | result, runner, independent oracle, five evidence bundles |
| `CLAUDE.md` | 159 lines | +72 lines: parity-ladder and execution-rigor sections |

The workbench is **honest but stale**: by the sibling branch's own rule — *"Prospectivity
is decided by the commit graph, not by prose"* — flipping the badge on this branch would
be wrong. But if this branch is what deploys, the public surface understates the completed
science by two audit phases.

The B3 result also refines the headline adverse finding in a way this branch's prose does
not capture: the ~0.0369-nat lognormal advantage is an **event-pooled** quantity, and the
result file explicitly warns that motor-equal primary numbers *"are NOT directly
comparable to the repository's published event-pooled figures."* The workbench presents
the event-pooled numbers without that distinction.

**Consequence for `CLAUDE.md`:** this branch's copy is behind. Any edit here must extend
the sibling branch's version, or the merge will drop the earned execution-rigor lessons.

---

## 6. Minor and informational findings

Confirmed, with file and line. Corrections are given in the plan of record (§7).

| id | severity | site | finding |
|---|---|---|---|
| DOC-01 | minor | `README.md:3` | README never mentions `/math-workbench`, the workbench-only deploy, or the `/` redirect |
| DOC-03 | minor | `README.md:44,61` | describes the Observed-experiment and Science-gates surfaces in the present tense; both are inside the paused lab |
| DOC-04 | minor | `README.md:23` | `npm install` where `CLAUDE.md:108` requires `npm ci`; recorded by Phase A and uncorrected |
| DOC-06 | minor | — | **no document anywhere describes the math workbench** |
| DOC-08 | minor | `README.md:17` | garbled duplicated phrase "Synthetic and recorded, synthetic, and live signals" |
| DOC-09 | minor | `README.md:33-40` | the `npm test` inventory omits the math-workbench bindings test and the root-redirect test |
| DOC-13 | info | `CLAUDE_ULTRACODE_…:139-153` | instructs an auditor to complete 13 walkthrough steps that no route serves |
| NR-04 | minor | `lib/duration-models.js:65` | A&S 7.1.26 `erf` has ~1.4e-7 absolute error → ~7e-8 in `S(y)`, but survival is printed to 8 decimals |
| NR-05 | info | `lib/uni-motor.js:188` | the 0.995 clip means the motor can never stall; reports positive speed with torque < load |
| NR-07 | info | `lib/source-first-passage.js:31` | `sourceTerms(0, …)` yields NaN (`kPlusByN` has no key `0`); unreachable from the UI today |
| NR-08 | info | `lib/uni-motor.js:348` | policy precision γ = 4 is an undeclared magic number with no sensitivity analysis |
| PRD-03 | minor | `app/globals.css:698` | native Ctrl+P from any tab other than *Print worksheets* prints nothing |
| PRD-09 | minor | `…workbench.tsx:214` | view is client state, so without JavaScript only the flow view exists |
| PRD-06 | info | `app/math-workbench/page.tsx:20` | throws on missing D1 accounting with no `error.tsx` anywhere |
| PRD-07 | info | `…workbench.tsx:284` | a `<nav>` of `aria-pressed` toggles, not a tablist; buttons are not associated with the panel |
| PRD-08 | info | `…workbench.tsx:331` | no `scope` on any `<th>`, no `<caption>` on any of the four tables |
| PRD-10 | info | `app/page.tsx:9` | **VERIFIED SAFE** — `redirect()` emits 307, not 308; no permanent-cache hazard |
| PRD-11 | info | `app/chatgpt-auth.ts` | **CPU-only sweep clean**: no GPU/WebGL/WebGPU/Three.js/WebSocket/analytics anywhere in `app/`, `lib/`, `public/`. `chatgpt-auth.ts` is unreachable dead code; delete it |
| PRD-12 | info | — | **VERIFIED**: every retained laboratory component is fully eliminated from both bundles (JS); the laboratory CSS block is not |
| PRD-13 | info | `…workbench.tsx:239` | **VERIFIED CLEAN**: no `Date.now()`, `new Date()` or `Math.random()` reaches any rendered value |
| PROV-02 | minor | `…workbench.tsx:406` | the "Executable sources" footer omits `lib/duration-models.js`, which computes most of what the page shows |
| PROV-03 | minor | `audit-manifest.json:11` | written by the runner, never read or verified by any test in `npm test` |
| PROV-06 | info | `…workbench.tsx:373` | the M3−M2 and M3−M1 paired intervals both cross zero and the page never says so; M3−M1 is not rendered at all |
| PROV-07 | info | `…workbench.tsx:352` | the DLT calculator runs parameters from a fit whose recovery and held-out gates (G05, G06) **FAILED** |
| PROV-09 | info | `lib/observed-experiment.js:225` | **CONFIRMED CORRECT** with one nuance: parameters are training-only, but the *set of eligible states* is chosen using all data |
| PROV-10 | info | `lib/observed-experiment.js:251` | **CONFIRMED CORRECT**: intervals are motor-cluster bootstrap, not event resampling — no pseudoreplication |
| TC-04 | minor | `page.tsx:26` | the only served surface names **no species anywhere**; `page.tsx` drops `observedReport.dataFlow`, where the *E. coli* attribution lives |
| TC-05 | minor | `…workbench.tsx:365` | the four hypothesis records with explicit overclaim fences — including the guard against reading the workbench as evidence that a motor performs Bayesian inference — are unreachable |
| TC-06/TSA-07 | minor | `…workbench.tsx:198` | `statusClass` substring-matches `"SUPPORTED"`, so `NOT_SUPPORTED` would render green. Latent today; fix **before** TC-05, whose correction makes it live |
| TC-07 | minor | `…workbench.tsx:323` | "Observed ligand"/"Observed speed" printed from a synthetic world with no marker, while a sibling tab uses a green OBSERVED badge for real measurements |
| TC-09/TSA-11 | info | `…workbench.tsx:138` | the DURATION card cites `lib/observed-experiment.js`, which only re-exports; the implementation and the component's import are `lib/duration-models.js` |
| TC-10/TSA-12 | info | `…workbench.tsx:85` | `fᵣ` shown with no unit (dimensionless, kT) one card from `F[q]` in nats; the equation shows steady-state `aᵣ` while the code applies a 0.12 s lag |
| TC-12 | info | `…workbench.tsx:368` | the card states 129 source motors while 80 + 19 = 99 are accounted for, with no on-screen reconciliation |
| TC-13/DOC-16 | info | `…workbench.tsx:273` | "Return to laboratory" targets `/`, which redirects back — a self-loop asserting a surface that is not served |
| TSA-04 | info | `tests/math-workbench.test.mjs:54` | tautology: `sourceDensities` returns `total` literally as `plus + minus` |
| TSA-06 | minor | `tests/math-workbench.test.mjs:88` | the shadow-implementation guard blocks only three exact names declared with `function`; an arrow function evades it |
| TSA-10 | info | `tests/math-workbench.test.mjs:76` | three of four assertions are weak or duplicated; a constant-returning stub passes the purity check |
| TC-14 | info | `tests/math-workbench.test.mjs:82` | nothing covers `statusClass`, any truth badge, the equation-card class, or species labelling |

---

## 7. Refuted candidates, kept visible

Nineteen candidate findings did not survive adversarial verification. The ones worth
recording because a future reader will re-derive the suspicion:

- **Weibull scale and lognormal `mu` inconsistency.** `logWeibull` derives its scale from
  `weibullScale(shape)` while `survival()` reads `models.weibull.scale`; the same split
  exists for lognormal `mu`. **Refuted by execution:** for the frozen fitted parameters the
  derived and stored values are identical to relative error 0
  (`0.6996038164387606`; `mu = −1.245527443530609`). Density and survival are the same
  distribution. The structural fragility remains — a future refit that writes only one of
  the two would silently diverge — but there is no live defect.
- **`redirect()` emits a cacheable 308.** Refuted: it emits 307.
- **Non-determinism from `Date.now()`/`Math.random()` in rendered values.** Refuted by
  sweep: two identical 100-step runs are bit-identical.
- **Pseudoreplication in the 95 % intervals.** Refuted: motor-cluster bootstrap confirmed
  in `lib/observed-experiment.js:251`.
- **Train/holdout leakage.** Refuted: the split is at motor granularity and parameters are
  training-only; proven by existing gates G1–G3.
- **Mobile horizontal page overflow.** Refuted: no page scroll occurs. The real symptom is
  narrower — the gate id **overprints** the title and badge at 320 px. Re-filed as minor.

---

## 8. Coverage limitations

Stated so that no reader mistakes this audit's scope for the repository's.

1. **No live browser testing was performed.** The sandboxed browser in this environment
   cannot reach the host loopback (`vinext dev` binds `[::1]` only and ignores `--host`),
   and the proxy workaround was denied. All product findings are static-analysis or
   build-output based. **Rendering, interaction and accessibility were not observed in a
   real browser.** E-M02 in particular predicts a *visual* failure that has not been seen.
2. **No automated accessibility run** (no axe, no Lighthouse, no assistive technology).
3. **Linux/CI build behaviour is NOT VERIFIED.** E-M07's confinement to Windows build
   hosts rests on reading the vinext plugin source, not on producing a POSIX build.
4. **No systematic mutation battery was run against `app/math-workbench/`.** E-M04's hole
   was demonstrated by hand-mutating scratch copies, not by executing the suite against a
   mutated repository.
5. **The cross-study Python gates were not rederived** (`scripts/run-cross-study-parity.py`),
   nor the lattice/GMC/RFT modules beyond their catalogue citations, nor the CAD export.
6. **No deployed artifact outside this worktree was checked.** `git show main:app/page.tsx`
   returns `<UniFlagellumLab />`, so published `main` differs from this branch; whether any
   live deployment serves either shape is NOT VERIFIED.
7. **Sibling branches were enumerated only where they bore on B3 prospectivity** (§5).
8. Several findings were established by reconstructing code paths in a scratchpad. The
   repository was never modified; `git status` was clean before and after.

---

## 9. Adverse results

Kept visible, per contract, and not softened.

- A shipped scientific equation is wrong (E-M01), and the repository's own record shows it
  was known to be unverified.
- A gate reports PASS with zero evidence on disk (E-B01).
- A passing test enforces a truth-contract violation (E-B02).
- The strongest truth claim in the repository is guarded by an assertion that cannot fail
  (E-M03), and truth laundering on the badge surface is undetectable (E-M04).
- A published provenance pin is false (E-M06).
- The shipped bundle discloses the build machine's filesystem path including the OS
  username (E-M07).
- The truth-status colour channel is dead on the only served page (E-M02).
- Two secondary held-out comparisons cross zero and the served page says so nowhere;
  the M3−M1 interval is not rendered at all (PROV-06).
- Four hypothesis records carrying explicit overclaim fences are unreachable in the
  deployed product (TC-05).
- Two governing documents disagree on the definition of `OBSERVED` (§4.1).
- `AC4` still FAILS and `AF1` remains BLOCKING and undecided (§4.8).
- The Phase-C blind mutation battery remains 0/10.
- `M2` lognormal still out-scores `M3` on held-out point score.
- `cross-study:verify-raw` is BLOCKED; 8 high-severity dev-dependency advisories are open.

---

## 10. Release-claim status

**Not established by this audit.** One required gate (`cross-study:verify-raw`) is
`BLOCKED_EXTERNAL` from this clone, the raw-source byte chain is
`EXTERNAL VALIDATION REQUIRED`, and two blocking findings are open. Passing the software
tests is necessary but is not proof of biological parity. The repository's own reports
continue to record `fullBiologicalParityAchieved: false`, four of seven computational
gates passing, and B3 `PENDING` **on this branch**.

Correction order and the implementation plan that depends on it are in
[docs/UNI-STACK-BUILDER-PLAN.md](../UNI-STACK-BUILDER-PLAN.md) §11 (Phase 0.5 onward) and
in the working notes accompanying this audit.
