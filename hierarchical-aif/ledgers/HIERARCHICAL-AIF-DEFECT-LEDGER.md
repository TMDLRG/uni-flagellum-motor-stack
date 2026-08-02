# Hierarchical-AIF Defect Ledger

**Gate:** H-AIF-G2 · **Opened:** 2026-07-21T16:39:52Z · **Repo HEAD:** `17a2f0e18c09c762ab1cefe854c0d68698803eac`
**Branch:** `hierarchical-aif/motor-stack` · **Append-only.** Rows are never deleted; status changes are appended.

> The hierarchical-AIF gates do not replace the existing P0–P8 ladder. They produce new receipts
> that map onto the existing ladder definitions in `CLAUDE.md`.

Verification standard: every defect below was surfaced by a read-only audit and then
**independently reproduced by the builder** before entering this ledger. Findings that were
surfaced but not yet independently reproduced are listed separately in §5 as `REPORTED_UNVERIFIED`
and carry no claim impact until verified.

---

## D1_C11_CLUSTER_COLLAPSE

| field | value |
|-|-|
| **defect_id** | `D1_C11_CLUSTER_COLLAPSE` |
| **affected_artifact** | `audits/phase-b/b4-identifiability-robustness-result.v1.json` (`cells.B4C11.U4_bootstrap`); `audits/phase-b/b4-evidence.v1/c11.evidence.json`; `experiments/predictions/b4-identifiability-robustness.prediction.json` (`outcome.headline`) |
| **affected_claim** | B4C11 U4 `U4_OK`; `collapseFraction_tau_lt_1e_3 = 0`; τ CI `[0.17658259553140288, 0.27020046374673834]`; aggregate `M7_status = IDENTIFIED_ON_THIS_COHORT (U1/U2/U3/U4 all OK)`; prediction outcome `REFUTED_U4_PARTIAL` |
| **affected_gate** | B4C11 (U4 only) |
| **affected_existing_P_level** | `P1` equation/implementation; `P3`/`P6` interpretation for C11 U4 |
| **evidence** | 80 training motors resampled with replacement produce only **46** `train_by_motor` groups at `seed_base=20260717, b=0` (b=1..4 → 53/52/59/56). Group count == distinct-motor count exactly. Largest group inflates 70 → 153 events. Theoretical `E[distinct]=50.8` matches. |
| **source_file_line** | `audits/phase-b/b3-model-competition-runner.py:147-151` (`tbm.setdefault(e["motorId"], [])` — grouping keyed by motorId); `audits/phase-b/b4-identifiability-robustness-runner.py:1247-1264` (C11 U4 resample loop); reaches M7 via `b3-model-competition-runner.py:638-642` (`m7_train_nll` iterates `train_by_motor`) and `b4-…-runner.py:1133,1158` |
| **reproduction_command** | `python <scratch>/verify_c11.py` — rebuilds the frozen cohort, replays the C11 resample at the declared seed, prints drawn/distinct/group counts |
| **falsifier** | If a corrected bootstrap that preserves K exchangeable groups per K draws reproduces the same τ CI and `collapseFraction=0`, then D1 had no material effect on the U4 verdict and the original conclusion is restored. |
| **confirmatory_evidence** | Paired N=5 diagnostic (identical draws, both arms), 2026-07-21: corrected τ **lower in 5/5** replicates (Δ −0.033 to −0.080; exact two-sided sign test **p=0.0625**, not significant at N=5); spread widens **1.64×**; **4 of 5** corrected τ fall **below** the recorded CI lower bound 0.17658; collapse fraction 0 in both arms. Direction was predicted from the mechanism before running. Diagnostic only — licenses no verdict. See `reports/C11-PAIRED-DIAGNOSTIC-REPORT.md`. |
| **status** | `VERIFIED_BLOCKING` |
| **old_status** | `U4_OK` (reported, 30/2000 replicates) |
| **corrected_status** | `NOT_ESTABLISHED` pending corrected full-N rerun |
| **B3_impact** | **NONE.** B3's M7 fit uses the real 80-motor cohort with no resampling. The B3 leaderboard, the adverse M2-over-M3 headline, and all B3 scoring are unaffected. |
| **B4_impact** | **C11 U4 only.** C11 U2 (61-pt profile on the real cohort) unaffected; C11 U1/U3 derive from B3 and are unaffected; **C10 unaffected** because `_fit_m4_reduced` uses the flat pooled `coh.train_y`, so duplicates enter correctly — a valid cluster bootstrap for a pooled i.i.d. likelihood. |
| **corrective_action** | Failing reproducer tests (H-AIF-G3) → corrected bootstrap assigning `bootstrap_group_id = draw_<idx>_<motorId>` while retaining `original_motor_id` as metadata; fit M7 over `bootstrap_group_id` (H-AIF-G4) → full frozen-N rerun (H-AIF-G5) |
| **allowed_wording** | "The C11 U4 bootstrap verdict is withdrawn pending a corrected full-N rerun." · "M7 identifiability on this cohort is supported by U1/U2/U3 and NOT_ESTABLISHED at U4." |
| **forbidden_wording** | "M7 is identified." · "U4_OK." · "τ is well determined." · any citation of the τ CI from the defective runner. |

---

## D2_RESOURCE_BOUND_OVERESTIMATE

| field | value |
|-|-|
| **defect_id** | `D2_RESOURCE_BOUND_OVERESTIMATE` |
| **affected_artifact** | `audits/phase-b/b4-identifiability-robustness-result.v1.json` (`cells.B4C01.reason`, `cells.B4C02.reason`, `cells.B4C09.reason`, `cells.B4C10.verdictScope`); `experiments/predictions/b4-…prediction.json` (`outcome.resourceBoundLimitations`) |
| **affected_claim** | That B4C01/B4C02 are infeasible (`NOT_RUN`, `reason=RESOURCE_BOUND`) and that B4C10/B4C11 could only run partially |
| **affected_gate** | B4C01, B4C02, B4C10, B4C11 (and the C09 figure, in the opposite direction) |
| **affected_existing_P_level** | `P0`/`P1` provenance and resource-status credibility for the not-run/partial cells |
| **evidence** | Measured on the frozen cohort: `fit_simple_models` 32.0 s; `fit_m6` 20.1 s (C01/C02 per-sim **52.1 s**); `_fit_m4_reduced` **3.8 s**; `_fit_m7_reduced` **36.2 s**. Projections: C01 ≈ **14.5 h** (recorded 250–400 h); C02 ≈ **8.7 h** (recorded 150–250 h); C10 ≈ **2.1 h** (ran 100/2000); C11 ≈ **20.1 h** (ran 30/2000). |
| **source_file_line** | `audits/phase-b/b4-identifiability-robustness-runner.py:768-835` (C01), `:935-1000` (C02), `:1024-1070` (C10), `:1240-1275` (C11); recorded reasons in `b4-assemble.py:340-360` |
| **reproduction_command** | `python <scratch>/verify_timing.py` — times each fit path on the frozen cohort and projects against frozen N |
| **falsifier** | If an independent timing run on comparable hardware reproduces the recorded 250–400 h / 150–250 h figures, the original resource claims stand and this row is withdrawn. |
| **status** | `VERIFIED_BLOCKING` |
| **old_status** | C01 `NOT_RUN=RESOURCE_BOUND`; C02 `NOT_RUN=RESOURCE_BOUND`; C10 `resourceBoundPartial` 100/2000; C11 U4 `resourceBoundPartial` 30/2000 |
| **corrected_status** | All four **scheduled for full frozen N**; resource justifications withdrawn pending `RESOURCE-BOUND-RECLASSIFICATION.md` |
| **B3_impact** | **NONE.** |
| **B4_impact** | Converts three cells previously presented as out of reach into scheduled work. **B4C02 — the HIGH-risk misspecified-world discriminator, the most decisive missing evidence in the submission — is ≈8.7 h, not 150–250 h.** |
| **corrective_action** | Measured-runtime estimator + `hierarchical-aif/reports/RESOURCE-BOUND-RECLASSIFICATION.md` (H-AIF-G4); then full-N runs in order C10 → C11 → C02 → C01 (H-AIF-G5) |
| **allowed_wording** | "The recorded resource justifications are withdrawn; measured runtimes place these cells within reach and they are scheduled at full frozen N." |
| **forbidden_wording** | "B4C02 is infeasible." · "These cells require 100+ hours." · any citation of the recorded hour figures as current fact. |

---

## D3_HASH_SEED_NONDETERMINISM

| field | value |
|-|-|
| **defect_id** | `D3_HASH_SEED_NONDETERMINISM` |
| **affected_artifact** | `audits/phase-b/b4-identifiability-robustness-runner.py` (C01, C02 code paths). **No result artifact affected — neither cell has ever been executed.** |
| **affected_claim** | Any future B4C01/B4C02 result's reproducibility; the protocol's `sharedDiscipline.determinism` requirement |
| **affected_gate** | B4C01, B4C02 (prospective) |
| **affected_existing_P_level** | `P1` implementation integrity for future C01/C02 runs |
| **evidence** | `np.random.default_rng(seed_base + sim + hash(gen) % 100000)`. CPython randomizes `str` hashing per process; `PYTHONHASHSEED` is unset in this environment. Three consecutive processes returned `14565/95125`, `59809/55025`, `89866/26054` for the same two generator strings. |
| **source_file_line** | `audits/phase-b/b4-identifiability-robustness-runner.py:810` (C01), `:959` (C02) |
| **reproduction_command** | `for i in 1 2 3; do python -c "print(hash('WEIBULL_GAMMA_BLEND')%100000)"; done` — three different values |
| **falsifier** | If `PYTHONHASHSEED` is pinned in the declared run environment, or the seeds prove stable across processes, the determinism requirement is met by the environment and this row is downgraded. |
| **status** | `VERIFIED_LATENT` (real defect; no result contaminated because the cells never ran) |
| **old_status** | Undetected; cells `NOT_RUN` |
| **corrected_status** | **BLOCKING for any C01/C02 run** until replaced with a stable SHA-256-derived seed |
| **B3_impact** | **NONE.** |
| **B4_impact** | C01/C02 must not be executed until fixed. Correct reference pattern already exists in-repo at C04 (single-construction RNG, strict-prefix slice). |
| **corrective_action** | `seed_int = int.from_bytes(sha256(seed_material).digest()[:8], "big") % 2**32` with `seed_material` = cell_id + base_seed + replicate_index + protocol_version + cohort_id (H-AIF-G4) |
| **allowed_wording** | "C01/C02 seeding is non-deterministic across processes and is blocked pending a stable-hash fix." |
| **forbidden_wording** | Any presentation of a C01/C02 result produced with `hash()` seeding as reproducible. |

---

## D4_C01_REASON_MISMATCH

| field | value |
|-|-|
| **defect_id** | `D4_C01_REASON_MISMATCH` |
| **affected_artifact** | `audits/phase-b/b4-identifiability-robustness-result.v1.json` (`cells.B4C01.reason`) |
| **affected_claim** | The stated justification for B4C01's `NOT_RUN` status |
| **affected_gate** | B4C01 |
| **affected_existing_P_level** | documentation/provenance integrity (no numeric P-level moves) |
| **evidence** | Recorded reason: `"≈ 1000 refits × ~15-25 min per M4/M7-inclusive competition"`. The cell's code comment reads `"skip M4/M7/M8 as they are the slow ones"`, and the sibling cell records `"skippedModels": ["M4_MIXTURE_K3","M7_HIERARCHICAL_MOTOR","M8_EMPIRICAL_KDE"]`. The justification describes a computation the cell does not perform. |
| **source_file_line** | `audits/phase-b/b4-identifiability-robustness-runner.py:816-823`; reason text at `b4-assemble.py:341-349` |
| **reproduction_command** | `sed -n '810,835p' audits/phase-b/b4-identifiability-robustness-runner.py` |
| **falsifier** | If the C01 code path does in fact fit M4/M7/M8, the reason text is accurate and this row is withdrawn. |
| **status** | `VERIFIED_DOCUMENTATION` |
| **old_status** | Reason accepted as written |
| **corrected_status** | Reason superseded in new reports; **old artifact left unmodified as historical record** |
| **B3_impact** | **NONE.** |
| **B4_impact** | Compounds D2: the overstated hour figure was justified by a model set the cell never fits. |
| **corrective_action** | Correct the reason text in new reports only; add `test_c01_reason_matches_actual_model_set.py` (H-AIF-G3) |
| **allowed_wording** | "The recorded C01 reason misdescribes the cell's model set and is superseded in the corrected reports." |
| **forbidden_wording** | Editing or overwriting the original recorded reason in the frozen result artifact. |

---

## D5_HOLDOUT_MARK_CHANNEL_BURNED — SELF-INFLICTED BY THE BUILDER

| field | value |
|-|-|
| **defect_id** | `D5_HOLDOUT_MARK_CHANNEL_BURNED` |
| **cause** | **My own instruction.** In the H-AIF UltraCode Track C brief I asked an agent for "the empirical marginals of direction/jump per state" and "what happens at state boundaries". That directed it to read the **held-out** mark channel and to run a held-out contrast (pooled vs state-conditional transition kernel, motor-equal NLPD, 2000-replicate motor bootstrap). No frozen gate had ever read `nextStateN` or `jump`. |
| **affected_artifact** | `experiments/data/wadhwa-2022-events.json` — the `nextStateN` / `jump` channel on the 19 holdout motors; joint `(N, N')` transition structure |
| **affected_claim** | Any FUTURE mark-process claim on the Wadhwa-2022 holdout |
| **affected_existing_P_level** | `P3` held-out predictive — for the mark channel only |
| **evidence** | Track C document contains per-state mark marginals and a held-out contrast table with CIs. Verified independently: 2 events with `nextStateN < 0`; 15.1% train / 16.7% holdout marks leave states {1..8}; 5 holdout events with zero training support. |
| **scope — what is NOT contaminated** | **B3 is unaffected.** B3 scores `durationS` only, and holdout durations were already public in `b3-model-competition-result.json`. `direction` was already consumed on holdout by the committed competing-risks likelihood (`lib/source-first-passage.js:59-65`, `scripts/run-science-gates.py:104-115,181-197`). The newly burned channel is specifically **`nextStateN` / `jump` magnitude and the joint `(N,N')` structure**. |
| **falsifier** | If a reviewer finds that `nextStateN`/`jump` on holdout were already consumed by a committed gate before 2026-07-21, the channel was already spent and D5 is downgraded. |
| **status** | `VERIFIED_IRREVERSIBLE` |
| **corrected_status** | Any mark-process model built on this dataset is **retrospective / exploratory**, never `PROSPECTIVE`. There is one study and no second holdout, so this **cannot be repaired within this dataset.** |
| **B3_impact** | **NONE.** |
| **B4_impact** | **NONE** — no B4 cell reads the mark. |
| **mitigating fact (not an excuse)** | The contrast came back `NOT_ESTABLISHED`: the CI crosses zero at every smoothing constant α ∈ {0.1, 0.5, 1.0, 2.0} **and the point estimate changes sign** between α=0.1 and α=0.5. So the channel had little resolving power at 19 holdout motors to begin with. This bounds the practical cost; it does not undo the loss. |
| **corrective_action** | (1) Record here permanently. (2) The mark-process question folds into the **transfer requirement** — a genuinely prospective mark test now needs an independent dataset, which `P4` already requires. (3) Standing rule added below. |
| **process rule adopted** | **Any brief that could cause an agent to read held-out data must state the split explicitly and restrict analysis to the training partition unless a prospective record is committed first.** My Track C brief did not, and that is the root cause. Read-only is not the same as consequence-free: reading held-out data is itself an irreversible act. |
| **allowed_wording** | "Mark-process findings on Wadhwa-2022 are retrospective/exploratory; the holdout mark channel was consumed on 2026-07-21." |
| **forbidden_wording** | Labelling any mark-process result on this dataset `PROSPECTIVE`. |

---

## D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED

| field | value |
|-|-|
| **defect_id** | `D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED` |
| **affected_artifact** | `experiments/data/wadhwa-2022-events.json` (2 events); `scripts/ingest-wadhwa-data.py` |
| **affected_claim** | Physical validity of the recorded mark; any boundary assumption at `N = 0` |
| **affected_existing_P_level** | `P2` observational; `P0` provenance |
| **evidence** | 2 below-physical-minimum target-state marks (`nextStateN` below the physical floor of 0 stators). **Both in the holdout partition, both from the same holdout motor.** A stator count of −1 is physically impossible. Event-level identifiers D12-redacted; see `reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md` §1. |
| **source_file_line** | `scripts/ingest-wadhwa-data.py:141-143` range-checks `dwell["state"]` (`< 0 or > 11`, with `continue`); `:147` reads `next_state` and `:158-160` write it **with no range check**. The out-of-range dwell is excluded but its **predecessor** keeps a mark pointing at the impossible state. |
| **reproduction_command** | `python -c "import json;[print(e['eventId'],e['stateN'],e['nextStateN']) for e in json.load(open('experiments/data/wadhwa-2022-events.json'))['events'] if (e.get('nextStateN') or 0)<0]"` |
| **falsifier** | If the raw Wadhwa MAT archive shows a genuine −1 stator state, this is a faithful recording and the defect is in the physical assumption, not the ingest. **Cannot be resolved here — the raw archive is absent (`P2` blocked).** |
| **status** | `VERIFIED` |
| **B3_impact** | **NONE** — B3 never reads the mark. |
| **B4_impact** | **NONE.** |
| **consequence** | A reflecting-boundary assumption `P(jump < 0 \| N=0) = 0` assigns `−inf` to the first below-physical-minimum event named above. So **the reflecting-boundary assumption at N=0 is falsified by the recorded data at exactly one event** — either a step-fitting defect or an ingest defect. Undecidable without the raw archive. |
| **corrective_action** | Do **not** edit the committed dataset. Record here; any future mark model must declare its handling of these 2 events explicitly and must not silently drop them. |
| **related structural constraints** | (a) **5 holdout events have zero training support** under an unsmoothed `(N,N')` kernel → `log p = −inf` → the runner's no-floor policy HALTS. Smoothing becomes a mandatory, **outcome-determining** hyperparameter (it flips the sign of the D5 contrast). (b) **15.1% of training / 16.7% of holdout marks leave the modelled set {1..8}** → the process is **not** a closed Markov chain on the cohort; a mark-bearing likelihood is a one-step-ahead conditional, not a trajectory likelihood. |

---

## D7_WIDTH_FIELD_FROM_COMPANION_INTERVAL

| field | value |
|-|-|
| **defect_id** | `D7_WIDTH_FIELD_FROM_COMPANION_INTERVAL` |
| **discovered_by** | Builder, while resolving a numeric disagreement between the Track D verification agent and my own recomputation (agent said M4 width 0.083461; I computed 0.084141 from the recorded `bca` bounds) |
| **affected_artifact** | `audits/phase-b/b3-model-competition-result.json` — the `width` field of **every** contrast entry |
| **affected_claim** | Any statement quoting a contrast `width` as the uncertainty of the **primary** interval; any power, resolution-floor, or minimum-detectable-effect argument built on it |
| **affected_existing_P_level** | `P0`/`P1` provenance and reporting integrity. **Not** `P3` — verdicts are unaffected (see below). |
| **evidence** | Across **48 of 48** contrast entries (2 cohorts × 2 rules × ≤8 models): `intervalUsed == bca` in **48/48**; `width` equals the **percentile companion** width in **48/48**; `width` equals the BCa width in **0/48**. Max abs difference between `width` and the width of `intervalUsed` = **0.02468874** nats. |
| **example** | `derived_eligible_1_to_8 / NLPD_motor_equal / M4_MIXTURE_K3`: `bca = [-0.02446025, +0.05968061]` (width **0.08414086**), `percentile = [-0.02833760, +0.05512299]` (width **0.08346059**), recorded `width = 0.08346059`, `intervalUsed = bca`. |
| **reproduction_command** | Iterate `cohorts.*.contrasts.*.*` and compare `width` against `intervalUsed[1]-intervalUsed[0]` and `percentile[1]-percentile[0]`. |
| **declared intent** | `uncertainty.interval` states *"95% BCa primary + percentile companion"*. The `width` field is **not** documented as referring to the companion, so a reader would reasonably take it to describe the primary. |
| **falsifier** | Repository documentation showing `width` is defined as the percentile-companion width by design. If so this is a documentation gap, not a reporting defect. |
| **status** | `VERIFIED` |
| **materiality** | **Verdicts are UNAFFECTED** — `INCONCLUSIVE`/`beatsM3` are decided by `intervalUsed` (BCa), which is correct in all 48 entries. The defect is that the published `width` describes a different interval from the one that decided the verdict. Max discrepancy 0.0247 nats is ~67% of the 0.0369 event-pooled adverse M2-over-M3 gap, so it is material to any resolution or power argument. |
| **B3_impact** | No verdict changes. All 8 motor-equal M3 contrasts remain `INCONCLUSIVE` under both intervals. |
| **B4_impact** | None directly. But B4-adjacent reasoning that quoted `width` inherits the wrong number. |
| **downstream_error_it_caused** | The Track D design document built its resolution-floor argument on `width`, compounding this with a separate ranking error (see below), producing a floor overstated by **1.53×**. |
| **corrective_action** | Do **not** edit the frozen artifact. Any hierarchical-aif document quoting an interval width must state which interval it refers to and prefer `intervalUsed`. Recommend a future `widthPrimary` / `widthCompanion` split for new artifacts. |
| **allowed_wording** | "The recorded `width` field reports the percentile-companion width; the primary BCa width must be computed from `intervalUsed`." |
| **forbidden_wording** | Quoting `width` as "the 95% BCa interval width". |

**Related ranking error (Track D, CONTRADICTED and independently confirmed by me):** Track D asserted
the narrowest motor-equal contrast is `M2_LOGNORMAL` at 0.128475. It is not. Sorted by recorded
`width`, the narrowest is **`M4_MIXTURE_K3` (0.083461)**, then `M8_EMPIRICAL_KDE` (0.086377), with
`M2_LOGNORMAL` **third of eight** (0.128475). Using BCa widths the order is the same
(M4 0.084141 < M8 0.085807 < M2 0.130462). Track D's resolution floor of ≈0.064 nats should be
≈0.042 nats — **overstated by 1.53×**. Its identifiability verdict survives the correction, but with
a materially smaller margin than it claimed.

---

## 5. Reported but NOT YET independently verified

These were surfaced by the H-AIF-G2 audit but have **not** been reproduced by the builder. They
carry **no claim impact** and license **no** correction until verified. They are recorded here so
they are not lost.

| id | summary | files | status |
|-|-|-|-|
| `R1_EFE_DOUBLE_AMBIGUITY` | Runtime `G(π)` computes `risk` as cross-entropy rather than KL and subtracts an `informationGain` defined as `H(q(o)) − ambiguity`, so ambiguity may enter twice; plus an undeclared `effort` term (0.02/0.07). `docs/SCIENCE.md:83` freezes the same non-standard formula, so code and doc agree with each other but differ from standard EFE. | `lib/uni-motor.js:309-330`, `docs/SCIENCE.md:80-88` | `REPORTED_UNVERIFIED` |
| `R2_F_IS_READOUT_NOT_OBJECTIVE` | Runtime `F` is a scalar readout of an exact closed-form categorical Bayes step; the KL term is ≡0 by construction, and `tests/model.test.mjs` "free-energy identity is exact" is therefore tautological. | `lib/uni-motor.js:268-291`, `tests/model.test.mjs:18-24` | `REPORTED_UNVERIFIED` |
| `R3_RUNTIME_SHARED_ORACLE` | Agent re-executes the world's exact torque-speed constants (420/180/18000/150), so it predicts the world by construction on the speed/stator channels. | `lib/uni-motor.js:175-188, 351-357` | `REPORTED_UNVERIFIED` |
| `R4_UI_EQUATION_MISMATCH` | UI displays `q(o|π)=Σ P(o|s)q(s|π)` while the implemented ligand prediction is a linear extrapolation with constants 0.08/0.25. | `app/uni-flagellum-lab.tsx:113-119`, `lib/uni-motor.js:350,375` | `REPORTED_UNVERIFIED` |
| `R5_INGEST_EXCLUSIONS_MISLABEL` | 109 right-censored dwells are counted under `exclusions` but not excluded (no `continue`); all 109 appear in the 1349-event artifact. | `scripts/ingest-wadhwa-data.py:139-146,190` | `REPORTED_UNVERIFIED` |
| `R6_M6_NOT_SEMI_MARKOV` | `M6_SEMI_MARKOV_STATE_DEPENDENT` is 8 independent per-state mean-one Weibull fits with no transition kernel; `nextStateN`/`direction`/`jump` exist in the data and are never read by B3. | `audits/phase-b/b3-model-competition-runner.py:265-271,443-462` | `REPORTED_UNVERIFIED` |
| `R7_C09_COST_UNDERSTATED` | C09's recorded 25–40 h may be *understated* (~63 h by one estimate); the `NOT_RUN` status stands either way. | `b4-…-result.v1.json` `cells.B4C09.reason` | `REPORTED_UNVERIFIED` |

`R6` is scientifically significant if verified: it would mean the most obvious mechanistic
alternative — that transitions carry information beyond dwell duration — was never entered into
the B3 competition, which bears directly on the "serious alternatives" claim.
