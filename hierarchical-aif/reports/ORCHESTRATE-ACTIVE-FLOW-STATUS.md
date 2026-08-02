# ORCHESTRATE — Active-Flow Status

**Snapshot:** 2026-07-22T02:10Z  ·  **UPDATED: B4C02 landed at 02:01:15Z** · **HEAD:** `b9b5670602a2afde158b53ea5e8135180f8c02f5`
**Branch:** `hierarchical-aif/motor-stack` · **Two authorized commits this session — `897c8ab` (B4C11 prediction record) and `28ce738` (B4C01 prediction record), one file each. Nothing pushed.**

> Alignment was the gate, not the destination. This records what was **executed** after it.

---

## 1. Executive verdict

The flow ran without hitting a STOP condition. **B4C10 landed at full frozen N and was reported;
B4C11 was prepared, smoke-tested, defect-fixed, and LAUNCHED; the F-side motor stack was built out,
scored, and returned a CI-bound `NOT_ESTABLISHED`; and three new defects (D8, D9, plus a latent
partial-run defect in the C11 harness) were found and routed.** The test suite went from
**71 passed / 1 xfailed** to **438 passed / 1 skipped / 1 xfailed** (three consecutive clean runs). Frozen evidence is byte-identical
throughout. The claim guard reports 0 violations.

**The two most important scientific statements produced, both adverse:**

1. **The F-side motor stack reproduces the frozen `M7_HIERARCHICAL_MOTOR` to `2.5e-7` nats.** At
   the resolution this study can achieve it is not a new model but a re-derivation of the
   incumbent, and it buys nothing measurable over its own `tau → 0` limit `M1_WEIBULL`
   (contrast `+0.000615`, half-width `0.0111`). `M2_LOGNORMAL` and `M8_EMPIRICAL_KDE` still
   out-predict it on point estimate.
2. **Prospectivity was being over-claimed (D9).** Reports asserted predictions were "committed
   before execution." The commit graph falsifies that for B4C10 and for the F-side scoring. No
   measurement is affected; the epistemic *grade* was. This is now mechanically guarded.
   **My own first D9 write-up was itself wrong** and was corrected: I recorded the B4C10 result as
   uncommitted, when `git log --diff-filter=A` shows prediction and result entered in **one
   commit** (`b9b5670`). The conclusion is unchanged and stronger — same-commit introduction makes
   strict ancestry *structurally unattainable*, so there is no mechanical test left to launder.
   Found by the adversarial verification lane, and recorded rather than silently patched.

**B4C11 was rescued from D9.** On authorization, commit `897c8ab` pre-registered its prediction
record while the run was at 210/2000 replicates with no result on disk — so B4C11 will be a
**genuinely prospective** cell, unlike B4C10 (prediction and result in one commit, structurally
unrepairable) and the F-side scoring (result already existed). Two of the four cells in this batch
now carry real prospective standing: **B4C02** (satisfied, with a mid-run-commit caveat) and
**B4C11** (pending, ordering secured).

**No P-level was raised by any of this work.** `P8` remains `FULL_PARITY = false`; the first
unsatisfied level is still `P4` transfer.

## 2. What ACTs were performed after alignment

| # | ACT | receipt |
|-|-|-|
| 1 | Contract recheck: frozen-evidence hash over all 250 files; working-tree scope check | `reports/frozen-evidence-recheck-active-flow.sha256` — diff EMPTY |
| 2 | Supervised C02/C10; hashed the completed C10 | `results/.../B4C10_CORRECTED_FULL.sha256` |
| 3 | Wrote the B4C10 full-N report against its pre-committed outcome mapping | `reports/B4C10-CORRECTED-FULL-REPORT.md` |
| 4 | Wrote the B4C11 prediction record, corrected harness, and launcher | `protocols/B4C11-CORRECTED-FULL-PREDICTION.md`, `scripts/run_c11_corrected_full.py`, `scripts/launch_B4C11_corrected_full.sh` |
| 5 | Smoke-tested C11 at N=1 and N=2 to scratch paths; measured real per-replicate cost | ≈24.7 s per M7 refit → ≈14 h projected, vs a recorded 20.1 h estimate |
| 6 | **Found and fixed a latent defect in the C11 harness**: `M7_status` ignored `resourceBoundPartial` and reported `IDENTIFIED_ON_THIS_COHORT` on a 2-replicate run — the exact D2 failure mode | `scripts/run_c11_corrected_full.py`; re-verified at N=1 |
| 7 | **LAUNCHED B4C11** at frozen `N_boot = 2000` | `results/.../B4C11_CORRECTED_FULL_ENV.txt`, `started_utc=2026-07-22T01:40:03Z` |
| 8 | Built `compare.py` + pre-registered scoring protocol + 32 harness tests | `src/motor_stack_aif/compare.py`, `protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md` |
| 9 | **RAN the F-side held-out scoring**, with a determinism gate and a 3-model independent oracle | `results/.../F_SIDE_MOTOR_STACK_SCORING_RESULT.json` sha256 `b3b12720…` |
| 10 | Wrote the scoring report incl. an honest 7/8 prediction scorecard with the miss recorded | `reports/F-SIDE-MOTOR-STACK-SCORING-REPORT.md` |
| 11 | Wrote the required test battery; audited coverage rather than creating filename shims | 10 new test files |
| 12 | **Found D8**: the closure ledger claimed two test files that did not exist | `tests/.../test_interval_width_provenance.py` (delivered, 4/4 mutations caught) |
| 13 | **Found D9**: prospectivity over-claimed; built a commit-graph guard | `tests/.../test_prospectivity_claims_match_commit_graph.py` |
| 14 | Reconciled D7's two-story status on a substantive change of state, not a relabel | ledger `status_reconciliation` row |
| 15 | Corrected the **unscoped** "`P6` is weakened" formulation still sitting in the P-ladder map | `ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md` §5a |
| 16 | Added a working claim-guard CLI (none existed; the documented module path is not importable) | `src/motor_stack_aif/claim_guard.py::main` |
| 17 | Updated the parity receipt map, ladder map, closure ledger; appended FLOW cards | see §9, §10 |
| 18 | **B4C02 landed**; hashed, reported against its committed mapping, D2 row updated | `reports/B4C02-CORRECTED-FULL-REPORT.md`, `results/.../B4C02_CORRECTED_FULL.sha256` |
| 19 | Acted on adversarial verification: fixed an unlabelled percentile width (D7 recurrence) and **corrected my own D9 factual error** | `reports/B4C10-CORRECTED-FULL-REPORT.md` §6, §12.6; ledger D9 `evidence` row |

## 3. Contract recheck

| check | result |
|-|-|
| `audits/phase-c` + `audits/phase-d` sha256 over 250 files | **IDENTICAL to baseline. NO DRIFT.** |
| working tree outside `hierarchical-aif/` | **clean** — `git diff --stat -- audits/` empty at start and at snapshot |
| test baseline on arrival | 71 passed, 1 xfailed |
| `git status` | only `hierarchical-aif/**` paths modified/untracked |

**No STOP condition was encountered.**

## 4. C02 status — **COMPLETE** (landed 2026-07-22T02:01:15Z)

Full frozen **N = 200 per generator, 600 sims, ZERO failures**, `resourceBoundPartial: false`,
`runStatus = ELIGIBLE_FOR_FROZEN_VERDICT`. Runtime **29 409.1 s = 8.17 h** against a recorded
`RESOURCE_BOUND` claim of 150–250 h. Result sha256
`0633988dbfd690c0c0d12075dba4e0d8c25ddd178125064bd01fbdaf4629e398`.

| generator | m2 beats m3 | fraction | modal winner |
|-|-|-|-|
| `weibull_gamma_blend` | 1 / 200 | **0.0050** | `M3_TWO_TIMESCALE` (81) |
| `three_timescale_heavy_tail` | 188 / 200 | **0.9400** | `M2_LOGNORMAL` (187) |
| `per_motor_heterogeneous_weibull` | 1 / 200 | **0.0050** | `M3_TWO_TIMESCALE` (82) |

**`gensWithM2overM3 = 1` of 3 → `GENERATOR-SPECIFIC` → the frozen prediction
`GENERATOR-ROBUST_ADVERSE` is REFUTED at full N.** `H_SHAPE_ARTIFACT` is **weakened**: the adverse
M2-over-M3 result is **not** generic to heavy-tailed dwell shape. Per the committed mapping this
*strengthens* the case that the M2-vs-M3 contrast carries mechanism-relevant information — **and
establishes no mechanism.** The separation is extreme (0.0050 / 0.9400 / 0.0050), not marginal.

**I predicted `GENERATOR-ROBUST_ADVERSE` and was wrong.** That is the recorded outcome.

**Prospectivity: `SATISFIED` — the only cell in this batch.** Prediction committed
2026-07-21T22:44:31Z, observation 2026-07-22T02:01:15Z: committed **3 h 17 min before** the
observation. Caveat stated: the commit was mid-run, with generator 1 already complete and failing
the threshold — so the prediction was committed **against** the partial evidence, not tuned to it.
Graded `PROSPECTIVE_WITH_MID_RUN_COMMIT_CAVEAT`.

Report: `reports/B4C02-CORRECTED-FULL-REPORT.md`. **The real-data adverse M2-over-M3 finding is
unchanged.**

## 5. C10 status — COMPLETE

Full frozen `N_boot = 2000` on the **byte-identical frozen runner** (`3e21edac…`), `--cells C10
--c10-boot 2000`. Result sha256 `959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde`,
runtime 8372.7 s, **completed 1994 / failed 6**, `resourceBoundPartial: false`.

| check | criterion (fires at) | observed | verdict |
|-|-|-|-|
| U2 collapse fraction | ≥ 0.25 | `0.0050150451` | `U2_OK` |
| U3 `log10(lambda_3)` 95% span | ≥ 2.0 decades | `0.4332708748` | `U3_OK` |
| U4 `omega_3` 95% CI straddle | `lo < 5/793` **and** `hi > 0.25` | `[0.0307464, 0.2883811]`, `lo` ≫ `0.006305` | `U4_OK` |
| reduced-budget calibration | ≤ 0.05 nats | `8.80e-11` | `WITHIN_0.05_NATS` |

Every observed value sits **far** from its threshold — this is a well-separated result, not a
marginal call. The frozen prediction `UNIDENTIFIED_OR_WEAK` is **REFUTED at full N, within B4C10
scope only**.

**Boundary, stated hard: C10 may NOT be used to repair C11.** Different model (M4 pooled-i.i.d.
mixture vs M7 motor-grouped hierarchy), different likelihood structure. **Identifiability is not
correctness and is not mechanism.**

**Prospectivity: `NOT_SATISFIED`** — prediction committed 2 h 33 min *after* the run finished (D9).
Recorded as a retrospectively-graded refutation, never as `PROSPECTIVE`.

## 6. C11 — prepared, corrected, and LAUNCHED

**RUNNING.** PID 26756, `started_utc=2026-07-22T01:40:03Z`, frozen `N_boot = 2000` + 25 paired
legacy-vs-corrected diagnostic replicates.

- **Seed equivalence PROVEN and enforced:** the harness reproduces the frozen inline draw sequence
  (`seed_b = 20260717 + b`) and **aborts** if it does not.
- **Frozen spec reproduced exactly**: threshold `collapseFraction ≥ 0.25`, 26-start L-BFGS-B via
  `b4._fit_m7_reduced` (**not** reimplemented), no floor, `N = 2000`.
- **U1/U2/U3 carried forward verbatim** from the frozen artifact with source path + sha256, labelled
  `CARRIED_FORWARD_FROM_FROZEN_ARTIFACT`. U2 is a deterministic profile scan that never touches the
  bootstrap, so D1 cannot reach it.
- The submitted `U4_OK` — **30 of 2000** replicates under the defective bootstrap — **remains
  withdrawn regardless of what this run returns**, and the harness records that in its own output.
- Measured ≈24.7 s per M7 refit → **≈14 h projected**, against a recorded 20.1 h estimate.

**Its progress log is not a result.** No C11 number is quoted or interpreted in this report.

**Prospectivity: `NOT_SATISFIED` today — but FIXABLE, and the window is open.** The prediction
record is untracked; **the C11 result does not exist yet.** Committing
`protocols/B4C11-CORRECTED-FULL-PREDICTION.md` before that result lands would make B4C11 a
genuinely prospective cell. **That requires the human principal.** See §17.

## 7. F-side motor-stack build status

**BUILT.** 2 free parameters `(mu, tau)`; per-motor latents integrated by 33-node Gauss-Hermite,
never estimated, so parameter count is independent of motor count. Censoring-correct hazard/survival,
`NO_FLOOR`, motor-equal scoring, motor-resampling bootstrap. G-side remains **fenced**: a test
asserts `expected_free_energy` does not exist, and the reason recorded is **structural** (empty
action set in a passive dataset), not sample-size-limited.

**Verified in the main loop, not merely asserted:**

- `motor_log_marginal` agrees with an independent adaptive-quadrature oracle to **4.7e-14** in log
  space, and Gauss-Hermite is converged (n=17 off by 1.5e-8; n=33…257 stable to 4.6e-14).
- A `hierarchy.py` domain guard changed during this session was audited: `k ≥ 1/170` is **derived**
  from the IEEE overflow bound of the mean-one Weibull scale (`exp(lgamma(172))` overflows,
  `exp(lgamma(171)) = 7.26e306` is finite), not tuned. The previous `1e-6` guard could only ever
  crash, never return a value, so **no previously-working result can change**.

## 8. F-side scoring status — EXECUTED

Result `b3b12720f32c0aee3bfa456f52ae0901976e59e3b43c0f2690fa7a17386ab297`.

- **Determinism PROVEN**: full pipeline executed twice, canonical bytes compared, `BYTE_IDENTICAL`.
- **Independent oracle PASS with residual exactly `0.0`** on three frozen models (M3, M0, M8),
  tolerance `1e-12`. B3 stores only aggregates, so every per-motor array was recomputed — which is
  why this check is mandatory. The harness **halts** rather than warning if it fails.

| reference | role | point | 95% percentile interval | verdict |
|-|-|-|-|-|
| `M0_EXPONENTIAL` | ADVERSARY | `+0.115291` | `[+0.013040, +0.227497]` | **RESOLVED_ABOVE** |
| `M5_GAMMA` | ADVERSARY | `+0.031036` | `[+0.004459, +0.054473]` | **RESOLVED_ABOVE** |
| `M3_TWO_TIMESCALE` | **CONTROL** | `+0.001641` | `[-0.077147, +0.080849]` | `NOT_ESTABLISHED` |
| `M1_WEIBULL` | ADVERSARY | `+0.000615` | `[-0.010881, +0.011304]` | `NOT_ESTABLISHED` |
| `M8_EMPIRICAL_KDE` | ADVERSARY | `-0.010169` | `[-0.084506, +0.064475]` | `NOT_ESTABLISHED` |
| `M2_LOGNORMAL` | ADVERSARY | `-0.023378` | `[-0.104886, +0.067038]` | `NOT_ESTABLISHED` |

**Pre-committed branch (B).** Not (A) — it does not beat the control or the serious adversaries.
Not (C) — no adversary resolved below 0, so the hypothesis is **not falsified** either.
`NOT_ESTABLISHED` **is not equivalence**; with 19 holdout motors most contrasts were expected to be
inconclusive, and were.

**Prediction scorecard: 7 of 8 hits, 1 recorded miss.** The miss (item 6) is instructive and is
reported, not buried: the `M5_GAMMA` contrast **resolved** at a half-width of `0.0250`, *below* the
~`0.042` nat "floor" — because that floor is a heuristic from the narrowest frozen B3 contrast, not
a bound, and a paired motor-cluster bootstrap resolves on **consistency of sign**, not magnitude
alone. A calibration caveat is recorded: the competitors' published holdout scores were already
legitimately in hand, so most contrasts followed by arithmetic once the point location was
predicted. **The scorecard measures the reasoning, not new evidence.**

## 9. Defect closure ledger status

| id | closure_status | blocked_by |
|-|-|-|
| D1 C11 cluster collapse | `OPEN_UNTIL_CORRECTED_C11_FULL_RUN` | **run now IN FLIGHT** |
| D2 resource overestimate | `CLOSING_BY_RECLASSIFICATION_AND_FULL_RUNS` | C02 running; C10 landed; C01 queued |
| D3 hash seeding | `CLOSING_BY_STABLE_SHA256_SEEDING` | in use by C02 now |
| D4 C01 reason mismatch | `CLOSED_AS_HISTORICAL_DEFECT_WITH_XFAIL` | — |
| D5 holdout mark burned | `QUARANTINED_RETROSPECTIVE_ONLY` | independent dataset |
| D6 `nextStateN` unchecked | `QUARANTINE_POLICY_BUILT_RAW_ARCHIVE_REQUIRED` | raw archive (absent) |
| D7 width = percentile not BCa | `CLOSING_BY_FORWARD_GUARD_AND_CORRECTED_FLOOR` | **reconciled this session** |
| **D8** ledger claimed undelivered tests | `CLOSED_BY_DELIVERED_AND_MUTATION_TESTED_RECEIPTS` | — |
| **D9** prospectivity not established | `QUARANTINED_RELABELLED_NOT_RETROACTIVELY_REPAIRABLE` | **commit prediction records BEFORE their runs** |

`test_defect_closure_ledger.py` now mechanically enforces that every defect names an
`affected_lane` **and** `unaffected_lanes`, carries a routed `closure_status`, and **claims only
test files that exist** — the guard that would have caught D8 on the day it was written.

**D2 pattern, measured not asserted:** every re-measured cost has come in *below* the figure that
justified a partial run — C10 at 2.3 h, C11 projecting ≈14 h against 20.1 h.

## 10. Biological parity receipt map status

Updated for LANE B (C10 landed) and LANE D (built **and scored**), each with current receipts, next
receipt, falsifier, and status. The required framing is intact:

> **Full biological parity is not a current status. It is the target world defined by these
> receipts.** — and every lane asks *"what would make this lane true?"*, not *"why this lane fails."*

LANE D's next receipt is now concrete and cheap: **per-motor arrays for `M4`, `M6` and `M7`** so the
three models that match or out-score the candidate can be contrasted under the same paired
bootstrap. It needs no new data.

## 11. Claim guard result

```
CLAIM GUARD: 0 violation(s) across 6 path(s).
```
Report: `reports/CLAIM-GUARD-ACTIVE-FLOW-REPORT.md`. A working CLI was added — the documented
`python -m hierarchical-aif.src...` path is not importable (hyphenated directory) and the module had
no entry point. It exits non-zero on violation so it can be gated.

It caught 8 real violations in the draft C11 prediction record: a forbidden-wording catalogue that
soft-wrapped, defeating the guard's own same-line use/mention rule. **Fixed by referencing the
canonical list rather than loosening the guard.**

**Passing this guard is necessary, not sufficient.** It checks wording, never whether evidence
supports a claim.

## 12. Existing P0–P8 mapping

| level | status | note |
|-|-|-|
| `P0` | **holds** | frozen-evidence integrity re-verified; determinism proven byte-identical |
| `P1` | **strengthened** | F-side marginal verified against an independent oracle; scoring harness reproduces three frozen models at exact-zero residual |
| `P2` | unchanged | no new observation |
| `P3` | **unchanged; B3 stands** | H-AIF-G7 added a candidate **without moving the level** — `NOT_ESTABLISHED` is not equivalence |
| `P4` | `NOT_ESTABLISHED` | single study; **first unsatisfied level** |
| `P5` | `NOT_ESTABLISHED` | unchanged |
| `P6` | **carried per scope — there is no single `P6` verdict** | C11 U4 withdrawn (run in flight); Wadhwa mark process retrospective-only; duration-only B3/B4 unchanged; full motor-stack AIF pending |
| `P7` | `NOT_ESTABLISHED` | external review in progress |
| `P8` | **`FULL_PARITY = false`** | conjunctive; unchanged |

The unscoped "`P6` is weakened" formulation that still sat in the ladder map was **replaced** with
the four scoped statements the contract requires.

## 13. What got repaired

- C11 harness reporting `IDENTIFIED_ON_THIS_COHORT` on a partial run (the D2 failure mode).
- An independent-oracle test whose own precondition was unsatisfiable — fixed by **tightening the
  oracle** (`epsrel=1e-12`), not by loosening the comparison, with the tolerance derived from
  measurement and a negative control added.
- Two ledger-claimed tests that did not exist (D8).
- D7's contradictory status, reconciled on a substantive change of state.
- The unscoped `P6` statement in the ladder map.
- Prospectivity over-claims across four prediction records and two reports (D9).
- A missing claim-guard CLI.

## 14. What got scored

The F-side motor stack, against `CONTROL_CURRENT` (M3) and five adversaries, on the frozen
duration-only holdout split, motor-equal, CI-bound. Verdict `NOT_ESTABLISHED` against the control
and every serious adversary. **The retained adverse lognormal finding is extended, not overturned.**

## 15. What got launched

**B4C11 corrected full run**, `N_boot = 2000`, 2026-07-22T01:40:03Z, PID 26756.

## 16. What remains running

| run | state | expectation |
|-|-|-|
| **B4C02** | **COMPLETE** 2026-07-22T02:01:15Z | verdict `GENERATOR-SPECIFIC`, prediction REFUTED |
| **B4C11** | RUNNING, PID 26756, 30/2000 | ≈14–16 h (first 25 replicates carry the doubled legacy arm) |

## 17. What is blocked, and the exact receipt needed

| item | blocker | exact receipt required |
|-|-|-|
| **B4C11 prospectivity** | ~~untracked~~ **RESOLVED 2026-07-22T03:23:14Z** | **DONE.** The principal authorized; commit `897c8ab` introduced the prediction record **alone**, while the run was at 210/2000 and **no result file existed**. Verdict `NOT_SATISFIED_PREDICTION_NOT_COMMITTED` → `PENDING_NO_OBSERVATION_YET` → `SATISFIED` on landing. Pinned by `test_b4c11_prediction_was_committed_before_its_observation` |
| B4C10 / F-side prospectivity | observation already existed | **None. Not retroactively repairable.** Only future cells can be prospective |
| D1 closure | C11 result | the running job |
| B4C01 | ~~not started~~ **PRE-REGISTERED AND LAUNCHED** | Prediction record committed `28ce738` at 04:05:29Z with the cell never having run at any N; launched 04:13:27Z. Measured 61.4 s/sim under contention with C11 → ≈17 h (the record projected 13.6 h from C02's rate; the gap is contention and is recorded, not hidden) |
| `M4`/`M6`/`M7` contrasts | no per-motor arrays in the frozen record | recompute per-motor NLPD from frozen fitted params via the existing oracle route — no new data needed |
| D5 / D6 mark lane | held-out mark channel burned; raw archive absent | an independent prospective mark dataset; raw-archive re-derivation |
| `P4` transfer | single study | an independent dataset |
| G-side | empty action set — **structural** | intervention data: a manipulated variable with recorded onset, paired pre/post on the same motors, enough motors per condition |
| Correction notice | external transmission | **the human principal must send it. It is prepared, NOT sent, and I do not claim transmission** |

## 18. Exact next ACT

```text
NEXT_ACT = [B4C02 DONE - reported, hashed, ledger updated 2026-07-22T02:01:15Z]
           SUPERSEDED BLOCK, retained for the record:
           monitor PID 29340 (B4C02) to completion; on completion:
             sha256sum results/motor_stack_aif/B4C02_CORRECTED_FULL_RESULT.json
               -> results/motor_stack_aif/B4C02_CORRECTED_FULL.sha256
             write reports/B4C02-CORRECTED-FULL-REPORT.md, applying the outcome mapping
               already committed in protocols/B4C02-CORRECTED-FULL-PREDICTION.md
               (frozen criterion: gensWithM2overM3 >= 2 of 3 -> GENERATOR-ROBUST_ADVERSE)
             record that B4C02 IS genuinely prospective - its prediction record was committed
               2026-07-21T22:44:31Z, before any C02 observation existed (the only such cell)
             update the D2 row in the closure ledger; append a FLOW card; rerun the claim guard
           THEN continue supervising PID 26756 (B4C11, ~14-16 h) and, while it runs, recompute
             per-motor NLPD arrays for M4_MIXTURE_K3, M6_SEMI_MARKOV_STATE_DEPENDENT and
             M7_HIERARCHICAL_MOTOR from their frozen fitted params so the three models that
             match or out-score the F-side candidate can be contrasted under the same paired
             motor-cluster bootstrap - the cheapest remaining receipt for LANE D, needing no
             new data and touching no held-out mark channel
```

### Updated NEXT_ACT after B4C02 landed

```text
NEXT_ACT = (1) TIME-LIMITED, REQUIRES THE HUMAN PRINCIPAL: commit
               protocols/B4C11-CORRECTED-FULL-PREDICTION.md BEFORE the running B4C11 result
               lands (~14 h window). It is the only way B4C11 becomes a prospective cell;
               after the result exists the opportunity is gone permanently (D9).
           (2) supervise PID 26756 (B4C11, 30/2000 at snapshot). On completion: sha256 the
               result, write reports/B4C11-CORRECTED-FULL-REPORT.md against the committed
               prediction record, and move D1 from OPEN to its routed closure.
           (3) while it runs: recompute per-motor NLPD arrays for M4_MIXTURE_K3,
               M6_SEMI_MARKOV_STATE_DEPENDENT and M7_HIERARCHICAL_MOTOR from their frozen
               fitted params, so the three models that match or out-score the F-side candidate
               can be contrasted under the same paired motor-cluster bootstrap. Cheapest
               remaining LANE D receipt; no new data; touches no held-out mark channel.
           (4) B4C01 queued (~14.5 h measured). Commit its prediction record BEFORE launching.
```

**This report is not a stopping condition.** No STOP condition is in force.
