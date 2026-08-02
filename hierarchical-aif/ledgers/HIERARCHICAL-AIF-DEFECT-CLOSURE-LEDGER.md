# Hierarchical-AIF Defect **Closure** Ledger

**Opened:** 2026-07-21 (realignment) · **Gate:** H-AIF-G9 · **Append-only.**

> **Why this ledger exists.** The defect ledger records *what is wrong*. It was being used as if
> recording a defect completed the work. It does not. A defect is a completed FLOW result only when
> it is routed into **repair, quarantine, rerun, transfer, or falsification**. This ledger tracks
> that routing, and it names the lanes a defect does **not** touch so that a local failure is never
> reported as a global retreat.

## Lanes

| lane | scope |
|-|-|
| **LANE A** | duration-only B3/B4 evidence |
| **LANE B** | corrected B4 robustness cells |
| **LANE C** | mark process / `nextStateN` / `jump` |
| **LANE D** | motor-stack AIF implementation |
| **LANE E** | biological parity ladder |
| **LANE F** | governance / reporting / claim guard |

---

## D1_C11_CLUSTER_COLLAPSE

| field | value |
|-|-|
| affected_lane | **LANE B** — B4C11 U4 only |
| unaffected_lanes | **LANE A** (B3 leaderboard, adverse M2-over-M3, all B3 intervals); **B4C10** (M4 fits pooled `train_y`, duplicates enter correctly); C11 U2 profile; C11 U1/U3; **LANE C/D/E** |
| defect_summary | Bootstrap regrouped resampled motors by `motorId`, collapsing K draws of a motor into one K-fold group. 80 draws → 46 groups at the declared seed. |
| repair_or_quarantine_action | **REPAIRED** — `bootstrap.build_bootstrap_cohort` emits one exchangeable group per draw; legacy path retained as `..._LEGACY_DEFECTIVE` for old-vs-new comparison. Split, scales, and pooled `train_y` provably unchanged. |
| test_added | `test_c11_bootstrap_preserves_exchangeable_motor_draws.py`, `test_bootstrap_duplicate_motors_remain_distinct_groups.py` (9 tests) |
| rerun_required | **DONE.** B4C11 corrected full frozen N=2000 landed 2026-07-22T22:47:14Z: `564a5b0f…`, 2000/2000 completed, 0 failed, seed sequence proven identical to the frozen inline construction |
| gate_impact | H-AIF-G5 |
| existing_P_level_impact | **`P6` for C11 U4 is now RE-ESTABLISHED on the corrected run only** (`U4_OK`, `collapseFraction 0.0055` at N=2000). The submitted 30-replicate artifact stays withdrawn. No other `P6` scope affected, and no level is raised — identifiability is not correctness and is not mechanism. |
| closure_status | `CLOSED_BY_CORRECTED_RERUN` |
| next_action | **DONE.** The D1 effect size is now MEASURED, not asserted: paired legacy-vs-corrected (25 replicates, identical draws) shows corrected tau below legacy in 25/25 (median shift −0.0546), and group counts inflated 46–59 → the corrected 80/80. The withdrawn artifact's tau median 0.2196 / p025 0.1766 was mildly over-optimistic; corrected full-N gives 0.168 / 0.0853, still comfortably above the collapse boundary. Second demonstration after D2 that a defective/partial run produced a reading a corrected full run revises |
| blocking_or_nonblocking | **Blocks C11 U4 only** |

## D2_RESOURCE_BOUND_OVERESTIMATE

| field | value |
|-|-|
| affected_lane | **LANE F** — resource-status reporting |
| unaffected_lanes | model math; duration likelihood; every recorded verdict |
| defect_summary | Recorded `RESOURCE_BOUND` costs overstated 17–29×; C01 14.5 h not 250–400 h, C02 8.7 h not 150–250 h, C10 2.1 h. |
| repair_or_quarantine_action | **CLOSING** — `resource.py` refuses estimates without measured runtime and flags ≥2× discrepancies; `RESOURCE-BOUND-RECLASSIFICATION.md` issued; four cells rescheduled at full frozen N |
| test_added | `test_resource_bound_estimator_uses_measured_runtime.py` (6 tests) |
| rerun_required | **ALL FOUR LANDED at full frozen N, 0 failures each.** B4C02 8.17 h (vs recorded 150–250 h), B4C10 2.3 h (vs "infeasible"), B4C01 16.83 h (vs 250–400 h), **B4C11 21.12 h** (vs the 20.1 h estimate — the one figure that came in slightly *over*, recorded honestly). Every `RESOURCE_BOUND` reason is now discharged by measurement |
| gate_impact | H-AIF-G4 → G5 |
| existing_P_level_impact | `P0`/`P1` provenance only. No scientific level moves. |
| closure_status | `CLOSED_BY_RECLASSIFICATION_AND_FOUR_COMPLETED_FULL_RUNS` |
| next_action | **DONE — all four resource-bound reruns landed.** `resource.py` refuses unmeasured estimates and flags ≥2× discrepancies going forward. **Refinement earned by B4C01:** its N=1 smoke measured **61.42 s/sim under contention** and predicted the realised **60.58 s/sim** to 1.4%, while the cross-cell projection from B4C02's 49.015 s/sim understated it by 1.24× — *measure in the regime the run will actually face* |
| blocking_or_nonblocking | **Nonblocking once reclassified** |

## D3_HASH_SEED_NONDETERMINISM

| field | value |
|-|-|
| affected_lane | **LANE B** — C01/C02 future reproducibility |
| unaffected_lanes | C10 (arithmetic seeds); B3; every completed frozen artifact |
| defect_summary | C01/C02 seeded via `hash(str)`, randomized per process with `PYTHONHASHSEED` unset. |
| repair_or_quarantine_action | **REPAIRED** — `seeding.stable_seed` derives a SHA-256 seed from declared protocol inputs; `legacy_seed` retained to pin the defect |
| test_added | `test_hash_seed_determinism.py` (4 tests, incl. cross-process subprocess check) |
| rerun_required | **N/A** — neither cell had ever run; the corrected harness is in use for C02 now |
| gate_impact | H-AIF-G4 |
| existing_P_level_impact | `P1` for future C01/C02 only |
| closure_status | `CLOSED_BY_STABLE_SHA256_SEEDING_AND_TWO_COMPLETED_RUNS` |
| next_action | **DONE.** Both cells that carried the `hash()` defect have completed on the corrected harness with `PYTHONHASHSEED` unset: **B4C02** (`0633988d…`, 600/600 sims, 0 failures) and **B4C01** (`8256cb12…`, 1000/1000 sims, 0 failures). The stable SHA-256 seed is in production use and no further action is owed |
| blocking_or_nonblocking | **Blocks old C01/C02 runner only** |

## D4_C01_REASON_MISMATCH

| field | value |
|-|-|
| affected_lane | **LANE F** — historical documentation |
| unaffected_lanes | model math; duration scoring; all verdicts |
| defect_summary | Frozen C01 reason cites an "M4/M7-inclusive competition" for a cell that skips M4/M7/M8. |
| repair_or_quarantine_action | **CLOSED as historical** — frozen artifact deliberately NOT edited; `corrected_reasons.py` supplies replacement text for new reports |
| test_added | `test_c01_reason_matches_actual_model_set.py` — strict-xfail against the frozen artifact (an XPASS would signal frozen-evidence mutation) |
| rerun_required | No |
| gate_impact | H-AIF-G3/G4 |
| existing_P_level_impact | Documentation/provenance only |
| closure_status | `CLOSED_AS_HISTORICAL_DEFECT_WITH_XFAIL` |
| next_action | Do not edit frozen artifact; new reports state the correct reason |
| blocking_or_nonblocking | **Nonblocking** |

## D5_HOLDOUT_MARK_CHANNEL_BURNED

| field | value |
|-|-|
| affected_lane | **LANE C** — prospective mark claims on Wadhwa-2022 |
| unaffected_lanes | **LANE A** duration-only B3/B4 (B3 reads only `durationS`/`stateN`/`rightCensored`); running C02/C10; all B4 cells; **LANE D** F-side duration model |
| defect_summary | My Track C brief lacked a split boundary, so an agent read held-out `nextStateN`/`jump`. |
| repair_or_quarantine_action | **QUARANTINED** — channel marked retrospective-only in `DATA-CHANNEL-SPEND-LEDGER.md`; D5 firewall now pasted into every subagent brief (held on first test); `<TASK>-DATA-ACCESS-PROTOCOL.md` required before any held-out touch |
| test_added | `test_no_holdout_mark_read.py` (this batch) |
| rerun_required | **Not repairable by rerun** — requires independent data |
| gate_impact | H-AIF-G2; strengthens H-AIF-G8 |
| existing_P_level_impact | **`P6` for Wadhwa mark-process mechanism is retrospective-only and transfer-required.** `P4`/`P7` requirements strengthened. `P3` duration-only untouched. |
| closure_status | `QUARANTINED_RETROSPECTIVE_ONLY` |
| next_action | Independent dataset or new prospective split for any mark claim |
| blocking_or_nonblocking | **Blocks prospective mark claim on this dataset only** |

## D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED

| field | value |
|-|-|
| affected_lane | **LANE C** — closed mark-chain modelling |
| unaffected_lanes | duration-only B3/B4; all B4 cells; **LANE D** F-side duration model |
| defect_summary | Ingest range-checks the dwell's state but writes `next_state` unchecked; 2 holdout events carry `nextStateN = -1`. 5 holdout events have zero training support; 15–17% of marks leave `{1..8}`. |
| repair_or_quarantine_action | **QUARANTINE POLICY BUILT** — `marks.py` offers `strict` (raises), `quarantine` (labels), `retain_labelled` (tags); **no silent-drop policy exists**. `assert_closed_alphabet` refuses closed-chain assumptions. Frozen dataset NOT edited. |
| test_added | `test_nextstate_range_check.py` (7 tests) |
| rerun_required | Raw archive re-derivation (absent) |
| gate_impact | H-AIF-G8 |
| existing_P_level_impact | **`P2` limited for mark fields**; `P6` for closed mark-chain mechanism blocked. Duration lanes untouched. |
| closure_status | `QUARANTINE_POLICY_BUILT_RAW_ARCHIVE_REQUIRED` |
| next_action | Raw archive re-derivation or independent mark data |
| blocking_or_nonblocking | **Blocks closed mark-chain mechanism claim only** |

## D7_WIDTH_FIELD_PERCENTILE_NOT_BCA

| field | value |
|-|-|
| affected_lane | **LANE F** — reporting; resolution/power arguments |
| unaffected_lanes | **All verdicts** — `intervalUsed == bca` in 48/48 and drives every decision; every contrast stays `INCONCLUSIVE` under both intervals |
| defect_summary | Published `width` equals the percentile-companion width in 48/48 entries, never the BCa width. Max divergence 0.0247 nats. |
| repair_or_quarantine_action | **CLOSING** — frozen artifact not edited; new reports must state which interval a width refers to and prefer `intervalUsed`; corrected resolution floor is **0.042 nats**, not Track D's 0.064 |
| test_added | `test_interval_width_provenance.py` — **DELIVERED 2026-07-22** (8 tests). Was previously claimed but absent; see **D8** |
| rerun_required | **Recompute any resolution/power argument** built on `width` |
| gate_impact | H-AIF-G9 |
| existing_P_level_impact | `P0`/`P1` reporting integrity. **No verdict and no scientific level moves.** |
| closure_status | `CLOSING_BY_FORWARD_GUARD_AND_CORRECTED_FLOOR` |
| status_reconciliation | **2026-07-22.** This row previously read `OPEN_UNTIL_WIDTH_FIELDS_CORRECTED_IN_NEW_REPORTS` while the closure-summary table listed D7 under `CLOSING`. The ledger told two stories; `test_defect_closure_ledger.py` held the disagreement visible as a strict xfail rather than editing the ledger to manufacture agreement. It is reconciled here on a **substantive change of state**, not by relabelling: (1) the forward guard now exists and is mutation-tested — `score.contrast_with_ci` must emit `intervalType` and a width equal to the width of the interval it reports alongside; (2) the corrected floor **≈0.042 nats** is now asserted by test against the frozen BCa endpoints, with the narrowest motor-equal contrast confirmed as `M4_MIXTURE_K3`; (3) the frozen artifact remains unedited and the defect stays pinned at 48/48 |
| next_action | Any *future* report quoting a width must quote the `intervalUsed` (BCa) width and say so. No further repair is owed |
| blocking_or_nonblocking | **Blocks power/resolution wording, not verdicts** |

## D8_LEDGER_CLAIMED_UNDELIVERED_TESTS

| field | value |
|-|-|
| affected_lane | **LANE F** — governance / receipt integrity |
| unaffected_lanes | **LANE A** duration-only B3/B4; **LANE B** C02/C10/C11 (C10's full-N result and C11's corrected run are untouched); **LANE C**; **LANE D** F-side model and its scoring; **LANE E**. **No scientific verdict is affected by this defect** — it is a defect in what this ledger *claimed*, not in any measurement |
| defect_summary | This ledger recorded two tests as delivered receipts that **did not exist on disk**: D5's `test_added: test_no_holdout_mark_read.py (this batch)` and D7's `test_added: test_interval_width_provenance.py (this batch)`. Found 2026-07-22 by listing `hierarchical-aif/tests/motor_stack_aif/`. The repairs those rows describe were real and the analyses were correct; the *receipts* were not delivered. D5's and D7's `closure_status` were therefore overstated |
| why_this_matters | This ledger exists precisely because "recording a defect is not closing it". A ledger that claims an undelivered receipt reproduces the failure mode it was built to prevent, one level up. It is the governance analogue of a green gate read as biological parity |
| repair_or_quarantine_action | **CLOSED BY DELIVERY.** Both tests now exist. `test_interval_width_provenance.py` (8 tests) independently reproduced D7 from the frozen artifact before pinning it: **48/48** contrast entries carry `width == percentile` width, **0/48** carry the BCa width, `intervalUsed == bca` in **48/48**, max BCa-vs-percentile divergence **0.024688739601508747** nats. `test_no_holdout_mark_read.py` was delivered in the same batch |
| test_added | `test_interval_width_provenance.py` (8 tests) · `test_no_holdout_mark_read.py`. **Mutation-tested**: 4/4 deliberate mutations caught — width relabelled as BCa (truth-laundering the defect away), `intervalUsed` switched to percentile, a zero-crossing verdict flipped to `NO_DIFFERENCE`, and `beatsM3` sign-inverted |
| structural_fix | `test_defect_closure_ledger.py` now parses this ledger and asserts every defect is present, carries a `closure_status` from the allowed vocabulary, and names **both** `affected_lane` and `unaffected_lanes`. A future undelivered receipt is caught mechanically |
| rerun_required | No — no run consumed the missing tests |
| gate_impact | H-AIF-G3 (failing tests for verified defects), H-AIF-G9 (ledger integrity) |
| existing_P_level_impact | **`P0`/`P1` receipt integrity only. No scientific level moves, and no verdict changes.** D7's substantive consequence is unchanged: the corrected resolution floor is **≈0.042 nats**, not 0.064 |
| closure_status | `CLOSED_BY_DELIVERED_AND_MUTATION_TESTED_RECEIPTS` |
| next_action | None. Kept visible as a permanent record that the ledger was audited against disk, not trusted |
| blocking_or_nonblocking | **Nonblocking** |

## D9_PROSPECTIVITY_NOT_ESTABLISHED_BY_COMMIT_GRAPH

| field | value |
|-|-|
| affected_lane | **LANE F** — provenance of every prospective *label* · **LANE B** and **LANE D** insofar as their reports wrongly asserted that predictions had been "committed before execution" |
| unaffected_lanes | **Every measured value.** No number, interval, verdict, threshold, seed, or hash is affected. The B4C10 result, the F-side scoring result, and the running B4C11 are unchanged. What is affected is the **epistemic grade** attachable to them, not their content |
| defect_summary | Reports asserted predictions were **"committed before execution."** The commit graph falsifies that for all three prediction records written this session. `CLAUDE.md`: *"a prediction is prospective only if it was committed before its observation"* and *"prospectivity is decided by the commit graph, not by prose."* |
| evidence | **B4C10:** the prediction record **and the result** entered the repo in **the SAME commit** `b9b5670` at **2026-07-21T22:44:31Z**; the run finished at **~20:11:51Z** — committed **2 h 33 min after** the observation existed. Same-commit introduction makes the strict-ancestor requirement **structurally unattainable**, not merely unmet: a commit cannot be its own strict ancestor. *(An earlier version of this row wrongly recorded the result as uncommitted; corrected 2026-07-22 after adversarial verification ran `git log --diff-filter=A` on both paths.)* **B4C11:** `protocols/B4C11-CORRECTED-FULL-PREDICTION.md` is **UNTRACKED**; the run launched 2026-07-22T01:40:03Z. **F-side scoring:** `protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md` is **UNTRACKED**; the scoring ran 2026-07-22T01:47Z. Verified with `git log`, `git ls-files --error-unmatch`, and artifact mtimes |
| why_the_mechanical_test_must_not_launder_it | For **B4C10** there is nothing left to launder: prediction and result share one commit, so ancestry is foreclosed outright. For the **F-side scoring** (protocol untracked, result already on disk) committing now would introduce the prediction *after* the observation existed — **passing a naive ancestry check while failing the substantive one**. The ancestry test is necessary, not sufficient, and must never be used to manufacture a `PROSPECTIVE` label after the fact |
| repair_or_quarantine_action | **QUARANTINED BY RELABELLING, NOT REPAIRABLE RETROACTIVELY.** All three results are labelled **retrospectively graded against a pre-written prediction**, which is strictly weaker than prospective. `reports/B4C10-CORRECTED-FULL-REPORT.md` §6 and §12.9 now grade prospectivity **`NOT_SATISFIED`** (a closed negative), replacing an earlier `NOT_VERIFIED` that wrongly implied a check that might still pass |
| mitigating_receipt_that_does_exist | For **B4C11** the launcher recorded the prediction record's sha256 `5d0a1170b78a860ca971cb9227ab86d90d60665a3345d28dc1a56ce437526ea1` into `B4C11_CORRECTED_FULL_ENV.txt` **at launch time** (`started_utc=2026-07-22T01:40:03Z`), which pins the prediction's exact content to a moment before any C11 observation existed. That is real evidence, and it is **weaker than a commit** because it is self-attested by the same process |
| test_added | `test_prospectivity_claims_match_commit_graph.py` — a **mechanical commit-graph guard**, not a wording guard alone. It (a) fails any hierarchical-aif document that asserts "committed before execution" without a same-line qualification, (b) runs the real ancestry test against `git` and **pins B4C10 at `NOT_SATISFIED_COMMITTED_AFTER_OBSERVATION`**, (c) asserts uncommitted prediction records cannot support a prospective label, and (d) keeps the B4C11 launch-time sha256 receipt visible. Non-vacuity guards included: the scanner is proved to catch the original D9 wording, and git availability is asserted so the ancestry checks cannot silently pass |
| rerun_required | **No rerun can repair the label.** Only *future* cells can be genuinely prospective |
| gate_impact | H-AIF-G5, H-AIF-G7, H-AIF-G9 |
| existing_P_level_impact | **No P-level moves in either direction.** `P3` duration-only unchanged; the B4C10 identifiability statement and the F-side `NOT_ESTABLISHED` verdict stand on their measured content. What is withdrawn is the *word* `PROSPECTIVE`, which was never applied as a label to any of these results — only implied by the phrase "committed before execution" |
| closure_status | `QUARANTINED_RELABELLED_NOT_RETROACTIVELY_REPAIRABLE` — for B4C10 and the F-side scoring, permanently. **B4C11 escaped it** (`897c8ab`, committed at 210/2000), and **B4C01 never entered it** (`28ce738`, committed with zero observations in existence). The defect is now also **structurally prevented going forward** by the launcher's uncommitted-prediction refusal |
| next_action | **B4C11: DONE — the window was taken.** On 2026-07-22T03:23:14Z the principal authorized, and commit `897c8ab` introduced `protocols/B4C11-CORRECTED-FULL-PREDICTION.md` **alone**, while the run was at 210/2000 replicates and **no result file existed**. Verdict moved `NOT_SATISFIED_PREDICTION_NOT_COMMITTED` → `PENDING_NO_OBSERVATION_YET`, and will become `SATISFIED` when the result lands. Pinned by `test_b4c11_prediction_was_committed_before_its_observation`. **B4C01: DONE, and it is the clean case.** Commit `28ce738` (2026-07-22T04:05:29Z) introduced `protocols/B4C01-CORRECTED-FULL-PREDICTION.md` **alone**, while the cell had **never been executed at any N** (frozen artifact `status=NOT_RUN`, `actual_N=0`; no smoke test, no partial, no result anywhere). Launched afterwards at 04:13:27Z. Committed blob, on-disk bytes and launch-pinned sha256 are **all identical** (`5e08cfd3…`) — no post-commit drift, unlike B4C11. **The `launch_B4C01_corrected_full.sh` launcher now REFUSES to run if the prediction record is uncommitted (exit 7), making D9 structurally unrepeatable for future cells.** Flip `PENDING → PROSPECTIVE` only in the result commit |
| blocking_or_nonblocking | **Blocks the `PROSPECTIVE` label on B4C10, B4C11 and the F-side scoring only. Blocks no verdict and no measurement** |

## D10_NO_MINIMUM_EFFECT_SIZE_GUARD

| field | value |
|-|-|
| affected_lane | **LANE F** - verdict interpretation across every CI-bound contrast; **LANE D** - the F-side scoring readout |
| unaffected_lanes | **Every measurement and every interval is correct.** No number, seed, threshold, or frozen criterion is wrong. **LANE A** B3 leaderboard unchanged; **LANE B** C02/C10 verdicts unchanged (their criteria are fractions/spans, not CI contrasts); **LANE C** untouched; **LANE E** no receipt moves |
| defect_summary | The frozen convention decides a contrast solely by whether its paired motor-cluster bootstrap interval excludes 0. It has **no practical-significance floor**. Because the bootstrap resamples MOTORS, a difference of **any magnitude** resolves provided its sign is **consistent** across motors |
| evidence | Contrasting the F-side candidate against frozen `M7_HIERARCHICAL_MOTOR`: point `+2.506984e-07` nats, 95% interval `[+1.604451e-07, +3.374688e-07]`, which excludes 0 and yields `RESOLVED_ABOVE`. The effect is **~168 000x below** the 0.042-nat resolution floor. 16 of 19 per-motor differences positive. The two models are the same model to numerical precision - the F-side hierarchy re-derives M7 via 33-node Gauss-Hermite |
| why_this_matters | Reporting that as "the candidate beats M7" would be **truth laundering**: a numerically identical model presented as a winner on consistent float noise. It is the failure mode the contract's "predictive superiority is never promoted to mechanism" rule exists to prevent, one level lower down |
| also_explains | The recorded miss in the F-side prediction scorecard (item 6): `M5_GAMMA` at `+0.031` nats resolved despite sitting below the ~0.042 floor. Same mechanism, milder. **The floor predicts what is scientifically material, NOT what the bootstrap will call** |
| repair_or_quarantine_action | **REPAIRED BY ADDED INTERPRETATION, NOT BY RE-THRESHOLDING.** The frozen verdict is reported **verbatim and unaltered** - never softened, suppressed, or re-thresholded. Every contrast now carries `scientificReading` (`MATERIAL` / `SUB_FLOOR_EFFECT` / `SCIENTIFICALLY_NULL`), a `reportableAsAWin` flag that is false whenever a resolved verdict sits below the floor, and an explicit `WARNING` string. **No frozen threshold, criterion, seed, or interval was changed** |
| test_added | `test_minimum_effect_size_guard.py` (8 tests). Includes a **from-first-principles non-vacuity test** reproducing the mechanism on synthetic data (a consistent `1e-7` offset resolves), a counter-test that a genuine `0.20`-nat effect still classifies `MATERIAL` so the guard cannot suppress real findings, and a test forbidding equivalence language on sub-floor intervals |
| rerun_required | **No.** Every recorded interval is correct as computed; only the accompanying interpretation was missing |
| gate_impact | H-AIF-G7, H-AIF-G9 |
| existing_P_level_impact | **`P0`/`P1` reporting integrity only. No verdict changes and no scientific level moves.** `P3` duration-only unchanged. Specifically: the F-side candidate is **not** credited with beating `M7` |
| closure_status | `CLOSED_BY_ADDED_INTERPRETATION_AND_TESTED_GUARD` |
| next_action | Apply `scientificReading` to any future CI-bound contrast before it is reported as a win. A sub-floor resolved verdict is a precision artifact, not a finding |
| blocking_or_nonblocking | **Nonblocking.** It blocks a *wording* - "beats" - not any measurement |

## D11_FABRICATED_NUMBERS_IN_GENERATED_REPORTS

| field | value |
|-|-|
| affected_lane | **LANE F** - report integrity in generated builder-support artifacts |
| unaffected_lanes | **Every recorded artifact and every verdict.** No result JSON, no frozen record and no CI verdict was affected. Both defects were in PROSE that misquoted a value the underlying artifact recorded correctly. **LANE A/B/C/D/E** untouched; the running B4C11 and B4C01 cells untouched |
| defect_summary | Two numbers in the builder-support probe pack could not be traced to any artifact, both in `reports/POWER-ATLAS-MOTOR-EQUAL-SCORING.md`: (1) a Monte-Carlo SE quoted as `0.043` for the worst cross-check cell where the artifact records `0.03952847075210474`; (2) a D10-counterfactual mean CI half-width quoted as `0.0790` where the artifact records `0.07996917206325926`. The second is the instructive one: `0.0790` is not a rounding of anything in that row - it is the **recorded M3 percentile half-width `0.0789979` transplanted from a different table in the same document** |
| why_this_matters | A transplanted neighbouring number is the hardest fabrication class to catch by eye: it is real, precise and locally plausible. It is exactly what the contract's never-invent-a-number rule targets, and it survived the authoring agent's own wording-guard run - because that guard checks WORDING and never numeric provenance |
| detection | Caught **pre-publication** by the adversarial verification lane, briefed to trace every numeric claim to a source and to treat an untraceable number as CRITICAL. Independently re-verified by the orchestrator against `power_atlas.json` before any correction was applied |
| repair_or_quarantine_action | **REPAIRED.** Both values corrected to the recorded artifact values, each carrying an inline note naming the error. Four further reporting defects found in the same sweep were corrected with them: an atlas-prediction label set `P1..P4` colliding with the frozen `P0..P8` ladder **inside the same document** (renamed `A1..A4` with a label note); free-parameter counts that were load-bearing for a hypothesis; a self-contradicting count; and a latent `or beatsM3` disjunct that could have set a win flag without consulting the interval |
| test_added | **A mechanical guard now exists.** `src/motor_stack_aif/numeric_provenance_guard` (module) + `test_numeric_provenance_guard.py` (9 tests) + `test_report_numbers_trace_to_artifacts.py` (6 tests). The guard checks **declared** provenance: a decimal may be ANCHORED to a `file.json#dotted.path` (and must match it at display precision), RECOMPUTED by a named script, or explicitly `DESIGN_ONLY` / `NOT_COMPUTED` / `NOT_MEASURED`. **The failing class is `ANCHORED_MISMATCH`** — a number that names a source and contradicts it. On mismatch the guard searches every artifact for a field whose value *does* round to the quoted figure and names it, turning "this number is wrong" into "this number is the value of *that* field" |
| test_catches_the_known_defects | **Both D11 values are covered by tests that fail without the fix.** `0.043` (invented — appears in no artifact) and `0.0790` (**transplanted** — the recorded M3 percentile half-width `0.0789979` pointed at the D10-counterfactual field) are each caught as `ANCHORED_MISMATCH`. A dedicated non-vacuity test proves the hard case is hard: `find_transplant_source` confirms `0.0790` **does** match a real recorded field, so a naive "does this number appear anywhere?" check would have **PASSED** it. Provenance is about the POINTER, not the digits |
| scope_stated_honestly | This does **not** make numeric provenance decidable in general, and the guard says so in its own report. `UNANCHORED` numbers are reported and do **not** fail, because reports legitimately carry counts, dates and derived arithmetic — a guard that fires on everything is a guard nobody reads. **Numeric provenance is also not decidable by a wording guard**, which is why the claim-guard wording check passed both values clean. The general control remains an adversarial reader briefed to trace every number |
| rerun_required | No. The underlying `power_atlas.json` was correct throughout; determinism and input hashes re-verified |
| gate_impact | H-AIF-G9 |
| existing_P_level_impact | **None. Every verdict, every P-level and every frozen record is unchanged and untouched.** `P3` duration-only unchanged; `P0`/`P1` receipts unchanged. This is report-integrity provenance only. The artifacts involved are builder-support probes that carry no evidential standing by construction, so no level could move even in principle |
| closure_status | `CLOSED_BY_CORRECTION_AND_TESTED_MECHANICAL_GUARD` |
| next_action | Run `numeric_provenance_guard.py` alongside the wording guard after every report batch. Anchor any number a report asserts as a quoted artifact value. Keep the trace-every-number brief mandatory: treat an untraceable number as CRITICAL and a plausible number matching a neighbouring table as the prime suspect. Do not mistake either guard for full numeric coverage |
| blocking_or_nonblocking | **Nonblocking** |

---

## Scoped P-level statements now in force

Replacing the unscoped "P6 weaker" formulation:

- **`P6` for C11 U4** — withdrawn until corrected C11 lands.
- **`P6` for Wadhwa mark-process mechanism** — retrospective-only, transfer-required (D5, D6).
- **`P6` for duration-only B3/B4** — **unchanged** until corrected B4 results land.
- **`P6` for full motor-stack AIF** — pending constrained implementation and scoring.
- **`P3` duration-only** — unchanged; B3 stands.
- **`P2` mark fields** — limited (D6). `P2` duration fields unchanged.

## Closure summary

| status | defects |
|-|-|
| `CLOSED` | D1, D2, D3, D4, D8, D10, D11 |
| `CLOSING` (forward-discipline only, no rerun owed) | D7 |
| `CLOSING` (D12 containment: guard + redaction + round-trip-verified successor archive; incident stays NEGATIVE, transmission principal-gated) | D12 |
| `QUARANTINED` (bounded, needs external data or not retroactively repairable) | D5, D6, D9 |
| `OPEN` | *(none — the last open defect closed when its corrected run landed)* |

**All twelve defects are routed. Seven are CLOSED (D1, D2, D3, D4, D8, D10, D11); two are CLOSING
(D7 forward-discipline with no rerun owed; D12 containment — guard + redaction + round-trip-verified
successor archive, with the incident permanently NEGATIVE and transmission principal-gated); three
are QUARANTINED with an explicit external route (D5/D6 need independent data; D9 is not retroactively
repairable and is quarantined by relabelling). **Zero OPEN.** All four corrected B4 cells have landed
at full frozen N.**

### Run-state as of 2026-07-22T01:40Z

| defect | blocking run | state |
|-|-|-|
| D1 | B4C11 corrected full `N_boot = 2000` | **LANDED** 2026-07-22T22:47:14Z — `564a5b0f…`, 2000/2000, 0 failed, `U4_OK` (collapse 0.0055), 21.12 h at 38.01 s/replicate. D1 `CLOSED_BY_CORRECTED_RERUN` |
| D2 | B4C02, B4C10, B4C01 | **ALL THREE LANDED.** B4C10 `959a00e9…` (8372.7 s); B4C02 `0633988d…` (8.17 h); B4C01 `8256cb12…` (16.83 h). **B4C11 still running** |
| D3 | **CLOSED** | both affected cells completed on the corrected harness: B4C02 and B4C01, 0 failures each |

**D2 note, measured not asserted:** every cost re-measured so far has come in *below* the figure
that justified a partial run — C10 at 2.3 h measured, and C11 projecting ≈14 h against a recorded
20.1 h estimate. The pattern that produced D2 keeps reproducing, which is why the C11 harness now
records `secondsPerReplicate` in its own result.

---

## D12_DISTRIBUTABLE_MARK_IDENTITY_LEAK

| field | value |
|-|-|
| affected_lane | **LANE C** (mark process) — distributable documents only; **LANE F** (governance/reporting) |
| unaffected_lanes | **LANE A/B** (duration-only evidence never touched); **LANE D/E** (motor-stack AIF, parity ladder — no P-level moves) |
| defect_summary | Real event-level identifiers, an associated real motor identifier, and record-shaped held-out mark tuples (found by D6) survived in distributable surfaces beyond the external D5 safety review's own JSON/JSONL/Markdown-scoped scan, which missed a `.py` test fixture entirely. Found via external review; independently reproduced by the new `d5_distribution_guard` (16 findings, 3 files, pre-redaction). |
| repair_or_quarantine_action | **REPAIRED (redaction sub-step only).** 4 distributable surfaces redacted to "below-physical-minimum target-state marks" wording, preserving the scientific finding while removing event/motor identifiers and row-level tuples: `reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md`, `protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md`, `ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md`, `reports/ULTRACODE-TRACK-D-VERIFICATION.md` (found by package-stage scan, not in the original 4 named surfaces). `tests/motor_stack_aif/test_nextstate_range_check.py` explicitly **NOT redacted** (functional regression fixture; must be excluded from distribution packages, not textually altered — see `reports/D12-INCIDENT-CONTAINMENT-REPORT.md` §2). Frozen results, `audits/phase-b/**`, and the raw/served datasets explicitly **NOT touched** — see report §3. |
| test_added | `test_d5_distribution_guard.py` (12 tests, all synthetic fixtures — no real identifier used); includes a permanent regression gate (`test_named_d12_surfaces_are_clean_after_redaction`) that fails if any of the 3 redacted `.md` surfaces regresses |
| rerun_required | N/A — documentation/prose defect, not a computational result |
| gate_impact | new gate, D5-lineage; H-AIF-G2 (correction record) |
| existing_P_level_impact | **NONE** — no P-level moves; this is containment **only**, not science, and the P0..P8 ladder is **unchanged**. Per authorization: "Effect on P-levels: NONE." |
| closure_status | `CLOSING_BY_CONTAINMENT_REMEDIATION` — guard built, 4 distributable surfaces redacted, successor archive round-trip-verified (see `reports/D12-SUCCESSOR-ARCHIVE-RECEIPT.md`). **Incident state `NEGATIVE` and permanent — never `CLOSED_BY_REDACTION`**; it does not clear when the remediation gate reaches `PASS`. Historical archive `UNI-FLAGELLUM-haif-closure-e21747c.zip` `WITHDRAWN_D5_UNSAFE` (sha256 `7b28f0d6…41b2`). Transmission principal-gated; prior distribution cannot be recalled. |
| next_action | Build `d5_distribution_guard`-verified successor archive (staging → scan → manifest → archive → unpack → rescan → recompute hash → confirm no withdrawn blobs/bundle → sanitized ancestry receipt) before the remediation gate can reach `PASS`. Transmission of the withdrawal notice remains principal-gated. |
| blocking_or_nonblocking | **Non-blocking for in-repo push of the redacted HEAD; blocking for any future external distribution package until the successor archive passes the round-trip.** |

**D12 note.** `e21747c` and all commits before this repair keep the original, unredacted content in
git history — this is deliberate and authorized ("preserve `e21747c`... unchanged in the
authoritative audit history"; no amend, rebase, or force-push). D12 redacts the **current working
tree going forward**; it does not and cannot retroactively scrub history. The `NEGATIVE` incident
state accounts for exactly that residual.
