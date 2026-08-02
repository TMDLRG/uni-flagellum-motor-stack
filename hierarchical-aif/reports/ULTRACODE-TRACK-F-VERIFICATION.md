# TRACK F VERIFICATION — Parity-Evidence Map vs. Recorded Gate Verdicts

**Verifier scope:** read-only. No file created or edited. No holdout-partition statistic computed. One declared TRAIN-partition count executed (§4.1), disclosed inline.
**Target:** `.../scratchpad/tracks/TRACK_F.md` (Track F — Biological Parity Evidence Requirements)
**Repository:** `C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM`, branch `hierarchical-aif/motor-stack`, HEAD `17a2f0e` — **CHECKED_AGAINST_CODE** (`git log -1` → `17a2f0e audit(phase-b): B4 identifiability & robustness result + PROSPECTIVE flip`), **NO_DATA_ACCESS_NEEDED**.

**Headline:** Track F's parity-evidence map is **substantially accurate** — every gate id, status, and headline numeric I checked reproduces from the recorded artifacts, to the digit. It is **not** guilty of the failure modes the contract targets: it does not redefine the ladder, does not claim a design document raises a level, and does not launder M2_LOGNORMAL. **Four defects survive verification**, one of which is a genuine numeric CONTRADICTION traceable to a repository documentation error, and one of which is a scientifically material omission: **Track F does not know about D5 or D6, and its single proposed runnable route to P3 is dead because of D5.**

---

## 1. Ground-truth confirmation (as ordered by the task)

### 1.1 Cross-study parity — CONFIRMED

**CHECKED_AGAINST_RESULTS** | `NO_DATA_ACCESS_NEEDED`
Source: `C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM/experiments/results/cross-study-parity-report.json`

`summary.overall = "PARTIAL_PARITY_ONLY"`, `summary.fullBiologicalParityAchieved = false`, `statusCounts = {PASS: 8, FAIL: 3, NOT_ESTABLISHED: 2, BLOCKED_EXTERNAL: 3}`. Full enumeration as recorded:

| Gate id | Recorded status |
|---|---|
| `X01_SOURCE_INTEGRITY` | PASS |
| `X02_CORPUS_BREADTH` | PASS |
| `X03_ROTATION_GATED_ASSEMBLY` | PASS |
| `X04_STATOR_CHEY_COUPLING` | PASS |
| `X05_TORQUE_SWITCHING_RESPONSE` | PASS |
| `X06_FINITE_LATTICE_COOPERATIVITY` | **FAIL** |
| `X07_GMC_GENERATOR_REPRODUCTION` | PASS |
| `X08_GMC_SWITCHING_OBSERVATIONS` | PASS |
| `X09_WHOLE_CELL_PROPULSION` | PASS |
| `X10_CROSS_STUDY_PARAMETER_TRANSFER` | **NOT_ESTABLISHED** |
| `X11_STRUCTURAL_CONSISTENCY` | **FAIL** |
| `X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY` | **NOT_ESTABLISHED** |
| `X13_LIVE_SIGNAL_CHAIN` | **BLOCKED_EXTERNAL** |
| `X14_INDEPENDENT_WET_LAB_REPLICATION` | **BLOCKED_EXTERNAL** |
| `X15_PRINTED_MODEL_VALIDATION` | **BLOCKED_EXTERNAL** |
| `X16_FULL_BIOLOGICAL_PARITY` | **FAIL** |

`X16` evidence verbatim: `allPriorRequiredGatesPass: false`, `nonPassGateIds = ["X06_FINITE_LATTICE_COOPERATIVITY","X10_CROSS_STUDY_PARAMETER_TRANSFER","X11_STRUCTURAL_CONSISTENCY","X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY","X13_LIVE_SIGNAL_CHAIN","X14_INDEPENDENT_WET_LAB_REPLICATION","X15_PRINTED_MODEL_VALIDATION"]`.

**One precision note on the task's own ground-truth statement.** The task framed cross-study as "X06, X11 FAIL". The recorded `statusCounts.FAIL` is **3**, not 2 — `X16_FULL_BIOLOGICAL_PARITY` is itself carried as a `FAIL` cell, not merely as a derived verdict. Track F states this correctly at F.9 (`X16_FULL_BIOLOGICAL_PARITY = FAIL`). No disagreement with Track F; noted so the count is not later misquoted as "two failures".

### 1.2 Science gates — CONFIRMED

**CHECKED_AGAINST_RESULTS** | `NO_DATA_ACCESS_NEEDED`
Source: `.../experiments/results/science-gates-report.json`

`summary.overall = "PARTIAL_PARITY_ONLY"`, `fullBiologicalParityAchieved = false`, `proofClaim = "No universal, causal, or biological Active-Inference identity was proved."`, `gateCount = 14`, `statusCounts = {PASS: 4, FAIL: 3, SOURCE_ONLY: 1, BLOCKED_EXTERNAL: 5, NOT_ESTABLISHED: 1}`.

The three FAILs are exactly `G03_PUBLIC_ARTIFACT_PARITY`, `G05_SYNTHETIC_RECOVERY`, `G06_HELDOUT_MECHANISTIC_PREDICTION` — as the task stated. Full enumeration: `G00` PASS, `G01_OBSERVATION_BOUNDARY` PASS, `G02` PASS, `G03` FAIL, `G04` PASS, `G05` FAIL, `G06` FAIL, `G07_H_STATE_REEXTRACTION` **SOURCE_ONLY**, `G08` BLOCKED_EXTERNAL, `G09_SWITCH_COOPERATIVITY` BLOCKED_EXTERNAL, `G10` NOT_ESTABLISHED, `G11` BLOCKED_EXTERNAL, `G12` BLOCKED_EXTERNAL, `G13` BLOCKED_EXTERNAL.

**Gap in Track F (not a contradiction, an omission):** `G07_H_STATE_REEXTRACTION = SOURCE_ONLY` and `G09_SWITCH_COOPERATIVITY = BLOCKED_EXTERNAL` appear **nowhere** in Track F. `SOURCE_ONLY` is a non-PASS status; under the frozen verdict algorithm it counts against the conjunction exactly as `FAIL` does. Track F's P2 section claims to enumerate observational evidence and does not mention that the transient H-state reproduction is source-only. **CHECKED_AGAINST_RESULTS** | `NO_DATA_ACCESS_NEEDED`.

### 1.3 Observed experiment H1/H2/H4 — CONFIRMED, with a status-string correction

**CHECKED_AGAINST_RESULTS** | `HOLDOUT_ALREADY_SPENT_DURATION_ONLY` (H1/H2) / `HOLDOUT_ALREADY_SPENT_DIRECTION` (H4)
Source: `.../experiments/results/observed-experiment-report.json → claims`

- `H1_OVERDISPERSION` = `SUPPORTED_WITHIN_PROTOCOL`, observed `3.149531339591441`, interval95 `[1.5141240937, 3.5675042611]`. ✓
- `H2_HELDOUT_LOG_SCORE` = `SUPPORTED_WITHIN_PROTOCOL`, observed `0.210181454187411` nats/event, interval95 `[0.0691846224, 0.3247183938]`. ✓
- `H4_DIRECTION` = **`INCONCLUSIVE_POINT_ESTIMATE_ONLY`** (not the bare string `INCONCLUSIVE`), observed `0.008775508769140683`, interval95 `[-0.0283851190, 0.0484046190]`. ✓ in substance; the exact recorded token is longer than both the task's phrasing and Track F's.
- **Not mentioned by Track F at all:** `H3_SURVIVAL_POSTERIOR` = `MODEL_CONSEQUENCE_CONFIRMED`, with the fence *"This is exact inference in the declared model, illustrated with observed durations; it is not evidence that a bacterium represents this posterior."* This is the single most abuse-prone claim in the repository (it is the one that superficially reads as "the motor infers"), and Track F's P5 section — the section whose whole job is to prevent that misreading — never cites it. **CHECKED_AGAINST_RESULTS**.

### 1.4 Ladder authority — CONFIRMED, contract satisfied

**CHECKED_AGAINST_CODE** | `NO_DATA_ACCESS_NEEDED`

`audits/coordinator/claude-three-phase-parity-completion-plan.v1.md`: `## 3. Operational parity ladder` at line 61; the P0 table row at line **68**; P8 row at line **76**; `` `P8` is conjunctive `` at line **78**. Verdict algorithm `Pn = PASS only if P0..P(n-1) PASS and all required Pn cells PASS` at line **545** (Track F cites `544-546` — correct as a range). Level names match Track F's usage verbatim; **Track F does not redefine the ladder.** Contract clause satisfied.

Repo `CLAUDE.md:163-182` restates the ladder in prose (`P0..P8`, conjunctive, "the report names the first unsatisfied level"). Track F's citation is accurate.

---

## 2. Per-level map verification (F.0 table and F.1–F.9)

Every numeric below was re-read from the artifact. `✓` = reproduces to the digit.

| Level | Track F assertion | Verification |
|---|---|---|
| **P0** | `G00` PASS, `X01` PASS; Phase-C `SURVIVED=10`; Phase-D `AC4=FAIL`, 20/23 credited | **CHECKED_AGAINST_RESULTS ✓.** `audits/phase-c/blind-mutation-result.codex.v1.json → classificationCounts = {DETECTED_SEMANTIC: 0, DETECTED_BY_HASH_ONLY: 0, SURVIVED: 10, NOT_RUN: 0, INCONCLUSIVE: 0}`. `audits/phase-d/d1-semantic-remediation-result.v1.json → classificationCounts = {DETECTED_SEMANTIC: 22, DETECTED_BY_HASH_ONLY: 0, SURVIVED: 1, NOT_RUN: 0, INCONCLUSIVE: 0}`; `coverageProvenanceSummary = {SUITE_MEMBERSHIP_MIGRATION: 15, NEW_COVERAGE_IN_D1: 8, NOT_MEASURED: 0}`. `d1-correction-package.v1.json → C3_DETECTION_ACCOUNTING.authoritativeAccounting`: `creditedDetections: 20`, `uncreditedIds: ["D1A02_SURVIVAL_POSTERIOR_SLOW_USES_FAST_RATE","D1P02_ADVERSE_EVIDENCE_COPY_DIVERGED"]`, `survivedIds: ["D1A10_LATTICE_NEXT_NEAREST_NEIGHBOUR_RING"]`, `"AC4": "FAIL"`, `headlineRule: "Phase D1 may claim 20 CREDITED detections out of 23 cells. It may NOT claim 22."` |
| **P0** | manifest hashes raw `c14de12c…`, events `32ec7ebf…`, code `b757971e…`, report `7ad8a21f…` | **CHECKED_AGAINST_RESULTS ✓** all four, `experiments/results/audit-manifest.json`. Source commit `c83119131c3ce3742460a2e3b6bd6c6e44bef4d5` ✓. `deterministicReplay` is indeed a prose string, not an executed receipt ✓. |
| **P0** | `data/remodeling_data.mat` absent | **CHECKED_AGAINST_CODE ✓.** No `data/` directory exists at repo root. Ingestion entry point requires an external path: `docs/OBSERVED-EXPERIMENT.md` — `python scripts/ingest-wadhwa-data.py /path/to/remodeling_data.mat`. |
| **P1** | `G02` PASS; `X07` PASS (175 states, col-sum `8.53e-14`, stationary `9.55e-15`, L1 `0.0176053`); `G03` FAIL | **CHECKED_AGAINST_RESULTS ✓** all. `G03` evidence: `maxRelativeMeanError = 3.7673463880` (→3.767 ✓), `maxAbsoluteFractionPlusError = 0.4425832725` (→0.443 ✓), `maxAbsoluteNormalizedVarianceError = 3.8622701732` (→3.862 ✓), `n0Contradiction` naming `V(N=0)=1.5920577617` ✓. Bundled vector `c1=0.613638, c2=0.308125, c3=0.162786, σ+=0.095787, σ-=10^-8` ✓ (`docs/SCIENCE-GATES.md:76-77`). **Omission:** Track F does not report `parameterIntervalChecks = {c1: false, c2: false, c3: true, sigmaPlus: true, sigmaMinus: true}` — i.e. `G03` fails on **two** independent criteria (moment reproduction *and* the article's 50%-loss interval), not one. |
| **P2** | `X06` FAIL: full-dist `J=0.2106346292` vs moment `J=1.1875632937`, diff `0.9769286644`, ΔAIC `-1.4588058431` | **CHECKED_AGAINST_RESULTS ✓** to every digit. |
| **P2** | `X03` LOO RMSE `0.8294` vs `1.4545`, `42.98%`, robust at 5/10/20 Hz | **CHECKED_AGAINST_RESULTS ✓** (`0.8293641328` / `1.4544734802` / `0.4297839431`; `binWidthRobustness` has `pass: true` at all three widths). |
| **P2** | `X04` Hedges `g=0.7774`, Welch `p=0.000817`, 5,000-bootstrap CI `[0.56641, 1.82915]`; FliM `p=0.6087`, rotating-vs-stalled `p=0.5678` | **CHECKED_AGAINST_RESULTS ✓** all five. Bootstrap count confirmed **CHECKED_AGAINST_CODE**: `scripts/run-cross-study-parity.py:26` — `BOOTSTRAPS = 5000`. |
| **P2** | `X08` 7/11 each direction; `X09` RMSE `1.7274` vs `2.0537` | **CHECKED_AGAINST_RESULTS ✓** (`fractionWithinAsymmetricErrorBar = 0.63636…` × 11 = 7, both directions; `1.7274106880` / `2.0537120441`). |
| **P2** | `G04` PASS: "**76 training + 16 holdout** censored intervals contribute `log S(t)`" | **CONTRADICTED — see §4.1.** |
| **P3** | `G06` FAIL: `+0.05826`, `[-0.01580, 0.13264]` | **CHECKED_AGAINST_RESULTS ✓** (`advantageNatsPerInterval = 0.0582583714`; `advantageInterval95 = {-0.0158010799, 0.1326434417}`; `bootstrapReplicates: 2000`, `bootstrapSeed: 20260717`). |
| **P3** | M3 beats M0 by `0.210`, `[0.069, 0.325]` | **CHECKED_AGAINST_RESULTS ✓.** |
| **P3** | M2 `expectation=BEATS_M3`, `result=UNRESOLVED`, point `+0.02502`, `[-0.04370, 0.08676]`; `lognormalMinusMixtureLogDensity = 0.03687` retained | **CHECKED_AGAINST_RESULTS ✓** (`b3-model-competition-result.json`: point `0.0250191765`, `intervalUsed [-0.0436984312, 0.0867635193]`, `underpowered: false`; `adverseLognormalRetention.derived_eligible_1_to_8.lognormalMinusMixtureLogDensity = 0.03686651826`). |
| **P3** | 19 holdout motors, 233 events, 80/793 train; `underpowered: true` for M0, M5, M6, M7 | **CHECKED_AGAINST_RESULTS ✓** (`cohorts.derived_eligible_1_to_8.summary = {holdout: 233, holdoutMotors: 19, train: 793, trainMotors: 80}`; underpowered flags on M0/M5/M6/M7 under `NLPD_motor_equal`). Note the flag set is scoring-rule-specific — more models are flagged under `CRPS_seconds`. |
| **P4** | `X10` NOT_ESTABLISHED, `commensurateRawTransferTests: 0`, reason verbatim; `G08` BLOCKED_EXTERNAL | **CHECKED_AGAINST_RESULTS ✓** including the `limitation` quote *"Forcing a common coefficient across these assays would create apparent unity by erasing the measurement models."* |
| **P5** | `G10` NOT_ESTABLISHED with `notObservedHere = [biological posterior, policy posterior, counterfactual preference, UNI-selected intervention]` and the limitation verbatim; `X12` `discriminatingInterventions: 0` against six named alternatives; `X13` `softwareCannotSubstitute: true` | **CHECKED_AGAINST_RESULTS ✓** — all four `notObservedHere` entries, the limitation string, all six competing explanations, and the boolean. |
| **P5** | F/G/policy/E/Π/messages absent **from the science pipeline**; all nine B3 models are MLE density fits | **CHECKED_AGAINST_CODE ✓, correctly scoped.** B3 models are exactly `M0_EXPONENTIAL … M8_EMPIRICAL_KDE`. `grep -rln "expectedFreeEnergy\|variationalFreeEnergy\|policyPosterior" scripts/ lib/` returns **only** `lib/uni-motor.js` / `.d.ts` (EFE + `policyPosterior` softmax at lines 348-349), and `grep -rln "uni-motor" scripts/` returns **nothing** — the FE machinery exists in the app-side simulation and is not imported by any science-pipeline script. Track F's qualifier "absent from the science pipeline" is precisely right; a looser "absent from the repository" would have been false. Credit where due. |
| **P6** | `X11` FAIL with `STRUCT-CONFLICT-01` / `-02`; `G05` FAIL 2/3 replicates, third missed `c2` by `0.1384` vs limit `0.12`; `c2=0.0004212689`, `c3=0.0000010723` | **CHECKED_AGAINST_RESULTS ✓** (`replicates[2]`: `seed 20260819`, `passed: false`, `sharedAbsoluteError.c2 = 0.1383933784`; `G04.evidence.parameters.c2 = 0.0004212689`, `c3 = 1.0722928878e-06`). Both structural conflicts reproduce verbatim, including "at least 11 torque-generating units". |
| **P7** | `G12` BLOCKED_EXTERNAL, `independentLaboratories: 0`, limitation verbatim; `X14`/`X15` `softwareCannotSubstitute: true`; `physicalPrintRuns: 0`, `measuredBacklashRuns: 0` | **CHECKED_AGAINST_RESULTS ✓** for `G12`, `X14`, `X15`. `NOT_CHECKED` for the literal keys `physicalPrintRuns` / `measuredBacklashRuns` — `X15.evidence` records `{missing: "fabricated print, dimensional inspection, sensor calibration, and observed hand-driven run", softwareCannotSubstitute: true}`; those two named counters are not keys in the cross-study artifact. Substance correct; key names appear to be Track F's paraphrase. |
| **P8** | `X16` FAIL, `overall = PARTIAL_PARITY_ONLY`, `fullBiologicalParityAchieved = false`, `proofClaim` verbatim | **CHECKED_AGAINST_RESULTS ✓.** |

**Citation-hygiene note (low severity, CHECKED_AGAINST_CODE).** Track F's line anchors into `scripts/run-science-gates.py` are off by one for `G02` (id at 415, cited 414), `G03` (423 / 422), `G04` (431 / 430), `G05` (446 / 445), `G06` (454 / 453), `G08` (477 / 476), `G10` (506 / 505), `G12` (525 / 524) — consistent with citing the `gates.append(gate(` opening line — but `G00` is cited at its id line (389). Same class of drift into `audits/phase-b/b3-model-competition-runner.py`: the censoring filter `if (not e["rightCensored"]) and e["stateN"] in self.states` is at line **109**, cited as `:110`. Docs anchors drift ±2 lines. All cross-study anchors (`366, 392, 395, 403, 408, 412, 418-422, 425`) are **exact**. `lib/source-first-passage.js:61` is **exact** — `if (event.rightCensored) return Math.log(Math.max(EPS, densities.survival));`. Not material to any claim; flagged so a reader chasing an anchor does not conclude the artifact moved.

---

## 3. The five questions

### Q1 — Which level is the FIRST unsatisfied one, and therefore the binding constraint on P8?

**Track F's answer (P0) is CORRECT.** **CHECKED_AGAINST_RESULTS + CHECKED_AGAINST_CODE** | `NO_DATA_ACCESS_NEEDED`.

Under the frozen algorithm at `audits/coordinator/claude-three-phase-parity-completion-plan.v1.md:545`, `Pn = PASS only if P0..P(n-1) PASS and all required Pn cells PASS`. P0's required cells are not all PASS: `AC4 = FAIL` verbatim in `audits/phase-d/d1-correction-package.v1.json`, with `creditedDetections: 20` of 23 cells and `D1A10_LATTICE_NEXT_NEAREST_NEIGHBOUR_RING` recorded `SURVIVED` against target `scripts/run-cross-study-parity.py`. Therefore **P0 is the first unsatisfied level and is today's binding constraint on P8.** Track F's two qualifications — that P0 is the *cheapest* constraint (closable without a laboratory) and that closing it does not bring P1–P7 near — are both sound.

**One correction to Track F's own labelling.** Track F's F.0 table assigns P0 the status **`NOT_ESTABLISHED`**. The governing cell is recorded as **`FAIL`** (`"AC4": "FAIL"`). Under the plan's status vocabulary, `FAIL` is the stronger, adverse status; `NOT_ESTABLISHED` means "the evidence does not decide". P0 is not undecided — an acceptance criterion was evaluated and *failed*. **The correct P0 ladder label is FAIL, and Track F softens it.** This is the one place in the document where the error runs in the self-favouring direction. **CHECKED_AGAINST_RESULTS** | `NO_DATA_ACCESS_NEEDED`.

Secondary methodological note: the plan's status vocabulary (`PASS / FAIL / CONTRADICTED / NOT_ESTABLISHED / BLOCKED_EXTERNAL / NOT_RUN`) governs **cells and parity dimensions**; the ladder itself is binary-with-ordering (`Pn = PASS` or not, plus "name the first unsatisfied level"). Track F's per-level statuses (P1=FAIL, P3=NOT_ESTABLISHED, P6=FAIL…) are legitimate *cell-aggregation summaries* but are not ladder verdicts, and a reader could mistake "P3 = NOT_ESTABLISHED" for a weaker statement than "P3 is not PASS and is unreachable while P0 is open". Track F does state the ordering explicitly, so this is presentation, not redefinition — the contract clause is not breached.

### Q2 — Which levels can NEVER be closed by software alone?

**Track F answers this correctly and plainly at F.10 §2. Confirmed and restated here without hedge.**

- **P5 (interventional) — cannot be closed by software. Ever.** **CHECKED_AGAINST_RESULTS** | `PROSPECTIVE_NEW_DATA_ONLY`. `X13_LIVE_SIGNAL_CHAIN.evidence.softwareCannotSubstitute = true`; `X12.evidence.discriminatingInterventions = 0`; `G10.limitation` verbatim: *"Exact Bayesian inference inside a declared software model is not evidence that a bacterium implements that representation."* **No model, no model class, no hierarchical AIF stack, no additional bootstrap replicates, no longer compute run, and no additional agent moves P5.** It requires physical manipulation of living motors with the prediction committed before the outcome. Track F's compounding argument — that `Lmotor-0 = {dt, N', direction, jump, censor}` contains **no motor-selected action**, so `q(π) = softmax(ln E(π) − γ G(π))` has no separable observable consequence and any `G_motor` term merely reparameterizes the same marked point-process density — is a correct in-principle identifiability argument and I endorse it. It means P5 is blocked **twice**: no wet lab, and no action variable.
- **P6 (structural/mechanistic) — cannot be closed by software. Ever.** **CHECKED_AGAINST_RESULTS** | `INDEPENDENT_TRANSFER_REQUIRED` / `PROSPECTIVE_NEW_DATA_ONLY`. Requires an independent molecular measurement (simultaneous reporter + rotation/occupancy trace). `CLAUDE.md:215-218` is binding: predictive superiority is never promoted to mechanism. **A better fit, of any margin, on any dataset, cannot move P6.**
- **P7 (independent replication) — cannot be closed by software. Ever.** **CHECKED_AGAINST_RESULTS** | `INDEPENDENT_TRANSFER_REQUIRED`. `G12.evidence.independentLaboratories = 0`; `G12.limitation` verbatim: *"Repository replay and an independent numerical implementation are not independent biological replication."* Track F's explicit non-substitute list (independent JS/Python oracles, Codex verdicts, a second AI agent, a second runtime, a clean clone, a second bootstrap seed, another machine) is correct and should be carried verbatim into any deliverable.
- **P4 (transfer) — not closable by modelling in this repository**, but blocked by *acquisition* rather than by physics. `X10.evidence.commensurateRawTransferTests = 0`. Track F's distinction (acquisition-blocked, not permanently impossible) is fair.
- **`G13`/`X15` (printed mechanism)** additionally require fabrication, dimensional metrology, sensor calibration, and safety review.

### Q3 — Does the track anywhere imply a P-level moves UP as a result of design work?

**NO. CHECKED_AGAINST_CODE (full read of `TRACK_F.md`) | `NO_DATA_ACCESS_NEEDED`.** No CONTRADICTED finding on this axis.

The document self-declares at line 3: *"DESIGN / EVIDENCE-MAP ONLY. It raises no P-level. It creates no receipt. Every status below is copied from an existing frozen artifact, not asserted."* F.10 §2 closes with the required corollary: *"building the hierarchical motor-stack AIF model raises no P-level by itself."* Every `Next experiment` block is framed as an obligation or an acquisition task, never as an accomplished raise. F.6 goes further and states the P5 blocker is *"a limitation in principle, not a compute limitation"* — the opposite of design-as-evidence.

The closest thing to an exposure is F.10 §2's clause (b), *"contribute to P2 by scoring the currently unscored mark channel"*. That is a claim about **executing a scoring run**, not about design — so it does not breach this clause. It does, however, breach the D5 firewall, which is §3 Q5 and §4.2 below.

### Q4 — The strongest claim the current evidence actually licenses

Track F's F.10 §3 sentence is **close to correct and materially better than anything else in the repository**, but it has two defects: it asserts the mark channel is unscored (false at repository scope — §4.3), and it omits the P0 caveat, so it presents an evidence claim resting on artifacts whose raw→events ingestion has never been re-executed in this tree. My corrected sentence:

> **On the frozen `sha256_mod5(motorId)` motor split of the single-study, single-laboratory Wadhwa et al. 2022 *E. coli* post-electrorotation stator-remodeling event artifact (SHA-256 `32ec7ebf45bf7776ebef239351d2304cc3cead6d1be7749a2478e44a323f25db`, whose raw→events derivation is asserted by recorded hash and has never been re-executed in this tree because `data/remodeling_data.mat` is absent, and whose semantic-mutation coverage is credited at 20 of 23 cells with `AC4 = FAIL` and one surviving undetected lattice-adjacency corruption), restricted to 233 uncensored held-out dwell durations in states `N=1..8` from 19 held-out motors fitted on 793 training events from 80 disjoint training motors, a training-only two-timescale mixture assigns higher held-out log predictive density than a homogeneous memoryless model by 0.210 nats/event with a motor-clustered 95% interval of `[0.069, 0.325]`, and the mean held-out `CV²` is 3.150 with motor-clustered 95% interval `[1.514, 3.568]` lying entirely above the memoryless value of one — while a one-parameter lognormal baseline out-predicts that same mixture point-wise on the same holdout (recorded motor-clustered `M3 − M2` interval `[-0.0680, 0.0148]`, point `-0.0369` nats/event) — so the evidence licenses only the statement that *E. coli* post-electrorotation stator-remodeling dwell timing is inconsistent with a homogeneous memoryless process at this observation resolution, and licenses nothing whatever about mechanism, latent-state identity, cross-laboratory transfer, intervention response, active inference, or biological parity.**

**CHECKED_AGAINST_RESULTS** | `HOLDOUT_ALREADY_SPENT_DURATION_ONLY`.

Supporting receipt Track F missed, which *strengthens* its own adverse position: `experiments/results/observed-experiment-report.json → pairedMixtureAdvantageInterval95.mixtureVsLognormal = {lower: -0.0680322535, upper: 0.0148179542}` with `pairedMixtureAdvantageNatsPerEvent.mixtureVsLognormal = -0.0368663986`. Track F's P3 "Exact missing receipt" asks for "a motor-clustered 95% interval for `[candidate model − M2_LOGNORMAL]`" as if none existed. **One already exists for M3, it is recorded, it contains zero, and its point estimate is negative.** A second recorded adverse detail Track F omits: in the same report's `calibration` block the lognormal has the best KS statistic (`0.0622`) of all four models, better than the mixture (`0.0775`). The lognormal is not merely tying on log score — it is better calibrated. Both facts belong in the retained adverse record.

### Q5 — Does the track incorporate D5 (mark→P4/P7) and D6 (limits P2 for mark fields)?

**NO to both. This is the most consequential finding in this verification.** **CHECKED_AGAINST_CODE (full text read of `TRACK_F.md`)** | `NO_DATA_ACCESS_NEEDED`.

The strings `D5` and `D6` appear nowhere in Track F. Neither does any equivalent concept: no mention that the held-out mark channel was read by a prior track, no mention that mark-process claims on Wadhwa-2022 can no longer be prospective, and no mention that ingest writes an out-of-range `nextStateN` for holdout events. Consequences in §4.2 and §4.4.

---

## 4. Findings, ranked by severity

### 4.1 CONTRADICTED — Track F's `G04` censoring counts are wrong, and so is the repository document it copied

**Track F F.3 states:** *"`G04_CENSORED_JOINT_LIKELIHOOD` = PASS … **76 training + 16 holdout** censored intervals contribute `log S(t)`."*

**What is actually true.** **CHECKED_AGAINST_RESULTS** — `experiments/results/science-gates-report.json → G04_CENSORED_JOINT_LIKELIHOOD.evidence`:

```
trainIntervals: 836   trainRightCensored: 43
holdoutIntervals: 244 holdoutRightCensored: 11
```

**Root cause — not Track F's invention.** **CHECKED_AGAINST_CODE**: `docs/SCIENCE-GATES.md:58` reads *"| G04 censored joint likelihood | PASS | **76 training and 16 held-out** censored intervals in eligible states contribute survival likelihoods. |"*. Track F faithfully copied a repository document that **disagrees with its own machine-readable artifact**. This is a live resonance defect under the operating contract clause 7 (report vs artifact must agree).

**Independent adjudication.**
- Train leg — **CHECKED_AGAINST_CODE, split boundary `TRAIN_ONLY`, computation declared:** I counted rows of `experiments/data/wadhwa-2022-events.json` with `partition == "train"` only. Result: 1048 train rows; `rightCensored` true across all states = **89**; `rightCensored` true and `1 ≤ stateN ≤ 8` = **43**; uncensored and `1 ≤ stateN ≤ 8` = **793**. The artifact's `trainRightCensored: 43` is correct and reconciles exactly with B3's `train: 793` (43 + 793 = 836 = `trainIntervals`). **The doc's "76" matches nothing** — not the eligible-state count (43), not the all-state count (89).
- Holdout leg — **CHECKED_AGAINST_RESULTS by arithmetic on already-published numbers only, no holdout row read:** `holdoutIntervals 244` − B3 `holdout: 233` = **11**, matching `holdoutRightCensored: 11`. The doc's "16" matches nothing. I did **not** count holdout rows; that would have been a new statistic over the holdout partition. Split boundary: `HOLDOUT_ALREADY_SPENT_DURATION_ONLY` (both operands are published figures).

**Impact.** Low on any scientific conclusion — `G04` PASSes either way and no downstream number depends on the count. High on evidence hygiene: it is a documentation-vs-artifact contradiction sitting in the summary table of the primary gate document, and Track F propagated it without checking. Any deliverable quoting "76/16" is quoting a defect.

**Minimal correction (for the owner, not applied by me — read-only run):** amend `docs/SCIENCE-GATES.md:58` to `43 training and 11 held-out`, and add a failing-first test asserting the doc table row equals `science-gates-report.json → G04.evidence.{trainRightCensored, holdoutRightCensored}`. That class of test does not currently exist, which is why the drift survived.

### 4.2 CONTRADICTED (in consequence) — Track F's only runnable route to P3 is dead under D5

**Track F F.4 states:** *"Two honest routes only: 1. More experimental units — external. 2. **More information per unit — score the currently unscored mark channel and the currently excluded censored events. This adds likelihood terms without adding motors and is the only route runnable in this repository.** It must be pre-registered…"* — echoed at F.3's missing-receipt (b), F.10 §2 clause (b), and F.11 item 5 (*"the single largest piece of runnable unexploited information in the repository — and the only route to P3 that does not require new motors"*).

**Why this is contradicted.** P3 requires *held-out predictive* parity — a frozen model scored on **untouched** motors, with the prediction committed before the scoring run. Per the established facts governing this verification, a prior UltraCode track **read the held-out mark channel** while answering a request for empirical direction/jump marginals per state. That read is irreversible. **No mark-process claim on Wadhwa-2022 can ever again be labelled PROSPECTIVE.** A mark-channel likelihood scored on this holdout is therefore `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY` and **cannot carry P3**. Track F instructs the reader to pre-register a contrast that can no longer be pre-registered.

**Independently corroborated without invoking D5. CHECKED_AGAINST_RESULTS** | `HOLDOUT_ALREADY_SPENT_DIRECTION`: the `direction` mark was *already* spent on the holdout before any UltraCode track existed — `observed-experiment-report.json → claims[H4_DIRECTION]` records a held-out state-conditioned direction log-loss (`0.6464397923` vs global `0.6552153011`), Brier scores, and a motor-clustered interval. `docs/OBSERVED-EXPERIMENT.md:139-140` narrates it. So even on a strict reading, the direction sub-channel of the mark process was consumed by H4 and is retrospective-only regardless of D5.

**What survives.** The censoring/`log S(t)` leg of Track F's proposal is **not** mark-process evidence and is **not** burned — right-censored held-out intervals are already scored by `G04`/`G06` under the correct treatment at `lib/source-first-passage.js:61`, and restoring them inside the B3 competition is a legitimate, runnable P2/P3 contribution. Track F conflated two proposals with very different evidential standing into one bullet. **The correct rewrite of F.4 route 2 is: censoring-inclusive rescore = runnable and prospective-eligible; mark-channel scoring = runnable but RETROSPECTIVE_ONLY on this dataset, hence `INDEPENDENT_TRANSFER_REQUIRED` / `PROSPECTIVE_NEW_DATA_ONLY` for any P3 or P4/P7 credit.**

Corollary Track F does not state and must: **the mark-process mechanism question has been pushed off this dataset entirely.** It is now a P4 (independent transfer dataset) or P7 (independent laboratory) question. That relocation *strengthens* Track F's overall thesis — the last runnable-looking lever was smaller than advertised — but it must be stated, or a reader will spend effort on a route that cannot pay.

### 4.3 CONTRADICTED — "the mark process of the observation is entirely unscored" is false at repository scope

**Track F F.3 states:** *"the B3 competition reads none of the mark fields … **The mark process of the observation is entirely unscored.**"* Repeated in F.3's Allowed wording and embedded in the F.10 §3 strongest-claim sentence as "the transition-mark channel unscored".

**First clause: TRUE. CHECKED_AGAINST_CODE** — `audits/phase-b/b3-model-competition-runner.py:108-109`:
```python
elig = [e for e in events
        if (not e["rightCensored"]) and e["stateN"] in self.states]
```
B3 filters on `rightCensored` and `stateN` only; `nextStateN`, `direction`, `jump` are never read by the nine-model competition. ✓

**Second clause: FALSE.** The `direction` mark **is** scored, on the holdout, in two separate places:
1. **CHECKED_AGAINST_CODE** — `lib/source-first-passage.js:59-65`, `sourceLogLikelihood`: censored → `log S(t)`; `direction === "on"` → `log P₊`; `direction === "off"` → `log P₋`; and it **throws** on an uncensored event with no direction. This is the likelihood used by `G04` and `G06`. `docs/SCIENCE-GATES.md:117-118` says so in prose: *"Every eligible held-out interval, **including its censoring indicator and observed exit direction**, was then scored."*
2. **CHECKED_AGAINST_RESULTS** — `H4_DIRECTION` scores state-conditioned direction on the holdout (§4.2).

What is genuinely unscored is narrower and must be stated that way: **`nextStateN` and `jump` are unscored anywhere; `direction` is unscored *within the B3 nine-model competition* but is scored by `G04`, `G06`, and `H4`.** As written, Track F's sentence would let a reader believe the direction channel is fresh. It is not — it is spent. Split boundary: `HOLDOUT_ALREADY_SPENT_DIRECTION`.

### 4.4 Omission with a code-verified mechanism — D6 limits P2/P3 for mark fields, and the contamination reaches `G04`/`G06`

**Track F never mentions D6.** Its P2 section lists `nextStateN`, `direction`, `jump`, `rightCensored` as clean available channels.

**Mechanism confirmed in code. CHECKED_AGAINST_CODE** | `NO_DATA_ACCESS_NEEDED` — `scripts/ingest-wadhwa-data.py:141-160`:
```python
if dwell["state"] < 0 or dwell["state"] > 11:      # entered state IS range-checked
    exclusions["outOfRangeDwells"] += 1
    continue
...
next_state = dwell["nextState"]                    # NOT range-checked
...
"nextStateN": next_state,
"direction": None if next_state is None else ("on" if next_state > dwell["state"] else "off"),
"jump":      None if next_state is None else next_state - dwell["state"],
```
The asymmetry the established fact describes is exactly present: `state` is range-checked, `next_state` is not, and the row is emitted regardless.

**A consequence Track F could not have drawn but which follows from the code alone, and which I have not seen stated anywhere:** because `direction` and `jump` are *derived* from `next_state`, a corrupt `next_state` does not merely corrupt `nextStateN` — it silently manufactures a **plausible-looking** `direction`. A `next_state` of `-1` is less than every valid `state`, so the row is emitted with `direction: "off"` and a large negative `jump`, and **nothing downstream can distinguish it from a genuine off-transition**. `sourceLogLikelihood` will not throw (it throws only on `direction === null`); it will score the event as an off-exit via `log P₋`.

Therefore, given the established fact that 2 holdout events carry `nextStateN = -1`: **those 2 events are inside `G04`'s 233 uncensored held-out intervals and inside `G06`'s held-out score, contributing a fabricated `log P₋` term.** `G06` already FAILs, so this cannot flip a pass to a fail; but it means `G06`'s recorded advantage `+0.05826` and interval `[-0.01580, 0.13264]` are computed over a holdout set containing 2 rows with synthesized direction marks. That is a **P2 provenance limitation on every direction-dependent held-out number in the repository**, and it is invisible in the current ledger.

**Quantifying the effect is NOT_CHECKED — it would require re-scoring holdout rows, i.e. holdout access. Requires a prospective record first.** The correct disposition is: record the limitation, add a failing-first range check on `next_state` in `scripts/ingest-wadhwa-data.py` mirroring the `state` check, re-ingest when `data/remodeling_data.mat` is obtained, and mark the `G04`/`G06` direction-dependent figures `RETROSPECTIVE, MARK-CONTAMINATED (n=2)` until then. Track F's P2 section must carry this; at present it does not.

### 4.5 Overstatement — "the lattice topology is not equation-locked by any control" is too strong

**Track F F.1 item 2 / F.2 / F.11 item 1** present `D1A10` as showing the lattice interaction topology *"is detected by nothing in the suite"* and *"not equation-locked by any control"*.

**What the artifact actually records. CHECKED_AGAINST_RESULTS** — `audits/phase-d/d1-semantic-remediation-result.v1.json → outcomes`:
- `D1A10_LATTICE_NEXT_NEAREST_NEIGHBOUR_RING`: `propertyId: D1P10_PERIODIC_LATTICE_TOPOLOGY`, `targetPath: scripts/run-cross-study-parity.py`, `expectedFailingTest: "periodic thirteen-site lattice retains its wraparound bond"`, **`predictedClassification: "SURVIVED"`** — it was *predicted* to survive and did; the gate run exited `0`.
- **`D1A10B_LATTICE_SINGLE_BOND_DOUBLE_COUNTED`**: same property, same target, `predictedClassification: "DETECTED_SEMANTIC"`, and its `d1-semantic` gate command **exited `1`** — i.e. the wraparound-bond test **does** fire on a different corruption of the same topology.

So the property is **partially** covered: one control exists and detects one topology corruption; a next-nearest-neighbour rewrite escapes it. **Track F never mentions `D1A10B`.** The honest statement is *"the periodic-lattice topology property has one control, which detects a double-counted-bond corruption but not a next-nearest-neighbour rewrite; the adjacency set itself is unpinned."* Track F's stronger phrasing overstates the hole.

**Counterweight that partially rescues Track F. CHECKED_AGAINST_RESULTS** — `d1-correction-package.v1.json` records of the addendum: *"Its revised D1A10 prediction and its added D1A10B cell were authored with knowledge of the implemented gates AND entered history in the very commit used as the replay base. They carry materially lower evidential weight than the ten exact replays"*, with `ruleForReaders: "D1A10B may not be presented as a pre-implementation frozen prediction, and may not be presented as having strict prospective ancestry."` So the one control that *does* fire is itself post-hoc. Track F's conclusion (the topology is under-locked, and this weakens `X06`'s verification standing) stands; its supporting sentence is too absolute and should be replaced with the two-part statement above.

### 4.6 Omissions of record (each CHECKED_AGAINST_RESULTS, `NO_DATA_ACCESS_NEEDED`)

| # | Omission | Why it matters |
|---|---|---|
| a | `G07_H_STATE_REEXTRACTION = SOURCE_ONLY` and `G09_SWITCH_COOPERATIVITY = BLOCKED_EXTERNAL` absent from Track F entirely | Two non-PASS science gates missing from a document whose purpose is a complete evidence map. `SOURCE_ONLY` counts against the conjunction. |
| b | `H3_SURVIVAL_POSTERIOR = MODEL_CONSEQUENCE_CONFIRMED` not cited in F.6 (P5) | It is the repository's most misreadable claim; its recorded fence (*"not evidence that a bacterium represents this posterior"*) is exactly the P5 boundary Track F is defending, and Track F leaves the strongest available quotation on the table. |
| c | `G03.parameterIntervalChecks = {c1: false, c2: false, …}` not reported | `G03` FAILs on two independent criteria, not one. |
| d | `pairedMixtureAdvantageInterval95.mixtureVsLognormal = [-0.0680, 0.0148]` and the lognormal's superior KS calibration (`0.0622` vs `0.0775`) not reported | Both *strengthen* the retained adverse result Track F is right to insist on. |
| e | `M8_EMPIRICAL_KDE` also carried `expectation: BEATS_M3` and returned `UNRESOLVED` (point `+0.0118`, `[-0.0281, 0.0577]`) | Track F names only M2 as an unresolved-against-M3 challenger; there were two. |
| f | `underpowered` flags are scoring-rule-specific | Track F cites the `NLPD_motor_equal` set (M0, M5, M6, M7); under `CRPS_seconds` the set is wider. Correct as far as it goes, unqualified as written. |

---

## 5. NOT_CHECKED register — verifications deliberately not performed

Each of the following would have required computing a new statistic over `experiments/data/wadhwa-2022-events.json` rows with `partition == "holdout"`. Per the firewall, **not done**, and this is the correct outcome, not a gap in effort.

1. **Direct count of holdout right-censored intervals (the "16" in §4.1).** `NOT_CHECKED — would require holdout access; requires prospective record first.` Adjudicated instead by arithmetic on two already-published figures (244 − 233 = 11). Split boundary: `HOLDOUT_ALREADY_SPENT_DURATION_ONLY`.
2. **Count/identity of the D6-affected holdout rows (`nextStateN = -1`).** `NOT_CHECKED — would require holdout access; requires prospective record first.` Mechanism confirmed from `scripts/ingest-wadhwa-data.py` alone (§4.4); the count is taken as given from the established-facts block, `REPORTED_BY_TRACK`.
3. **Magnitude of the D6 contamination on `G04`/`G06` held-out log scores.** `NOT_CHECKED — would require holdout re-scoring; requires prospective record first.` Split boundary: `HOLDOUT_ALREADY_SPENT_DURATION_ONLY` for the existing figures; any *new* estimate is `PROSPECTIVE_NEW_DATA_ONLY`.
4. **Any empirical marginal, table, or correlation over holdout `direction` / `jump` / `nextStateN`.** `NOT_CHECKED` and will remain so. Split boundary: `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`.
5. **Whether `D1A10`'s escape actually changes the `X06` `J` estimate.** `NOT_CHECKED` — would require executing the mutated `scripts/run-cross-study-parity.py`, i.e. a write/run in a frozen tree. Split boundary: `NO_DATA_ACCESS_NEEDED` but out of scope for a read-only verification.
6. **Outcomes of the in-progress corrected runs `B4C02` (misspecified-world discriminator) and `B4C10` (M4 bootstrap).** `NOT_CHECKED — not returned.` No claim in this document assumes either outcome. Track F likewise makes no assumption about them, correctly.
7. **`X15` keys `physicalPrintRuns` / `measuredBacklashRuns`.** `NOT_CHECKED` — not present as keys in `cross-study-parity-report.json`; substance (`softwareCannotSubstitute: true`, missing fabrication/inspection/calibration) confirmed instead.

---

## 6. Verdict on Track F

**ACCEPT WITH REQUIRED CORRECTIONS.** The parity-evidence map is faithful: every gate id, status, and headline numeric that I re-read reproduces from the frozen artifacts, generally to ten significant figures. The forbidden-language contract is honoured throughout — no "parity achieved", no "active inference demonstrated", no promotion of `M2_LOGNORMAL` to model status, no design-raises-a-level claim, and the F/G-absence statement is scoped precisely to the science pipeline where a looser claim would have been false. The P5 in-principle identifiability argument (no action channel ⇒ `G_motor` observationally equivalent to a reparameterized marked point process) is the document's strongest original contribution and survives scrutiny.

Required before Track F is used as a basis for any deliverable:

1. **Fix the `G04` counts** to `43 training / 11 held-out right-censored`, and raise the underlying `docs/SCIENCE-GATES.md:58` doc-vs-artifact contradiction as a separate delta with a failing-first test. *(§4.1)*
2. **Withdraw "score the mark channel" as a P3 route.** Split F.4 route 2 into (i) censoring-inclusive rescore — runnable, prospective-eligible; (ii) mark-channel likelihood — `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`, credit relocated to P4/P7. *(§4.2)*
3. **Replace "the mark process is entirely unscored"** with the accurate scoping: `nextStateN`/`jump` unscored anywhere; `direction` unscored *within B3* but already spent on the holdout by `G04`, `G06`, and `H4`. *(§4.3)*
4. **Add D6 to P2** with its code-verified mechanism and the previously unstated consequence that a corrupt `next_state` manufactures a plausible `direction` that flows undetected into `G04`/`G06` holdout scoring. *(§4.4)*
5. **Soften the `D1A10` claim** to acknowledge `D1A10B` and the one (post-hoc, lower-weight) wraparound-bond control that does fire. *(§4.5)*
6. **Relabel P0 `FAIL`, not `NOT_ESTABLISHED`** — the governing cell records `"AC4": "FAIL"`. *(§3 Q1)*
7. **Add `G07` (SOURCE_ONLY) and `G09` (BLOCKED_EXTERNAL)** to the map, and cite `H3`'s fence in P5. *(§4.6 a, b)*

None of these corrections moves any P-level. P0 remains the first unsatisfied level and the binding constraint on P8; P5, P6, and P7 remain permanently closed to software, and no model, no additional compute, and no additional agent will ever change that.