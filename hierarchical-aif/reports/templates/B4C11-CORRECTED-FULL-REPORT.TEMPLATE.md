# TEMPLATE — B4C11 Corrected Full-N Result Report

> **THIS IS A TEMPLATE, NOT A RESULT.** `B4C11` had not landed when this file was written. Every
> `<<FILL>>` marker is an unfilled slot. This file carries **no result, no verdict and no
> evidence**, and it must never be cited. The landed report goes to
> `hierarchical-aif/reports/B4C11-CORRECTED-FULL-REPORT.md`; this skeleton stays here.
> Purpose: make landing mechanical so no required field is forgotten under time pressure.

**Gate:** H-AIF-G5 · **Cell:** `B4C11_M7_STRUCTURAL_IDENTIFIABILITY` · **Lane:** **B**
**Defect routed:** `D1_C11_CLUSTER_COLLAPSE`

---

## 1. Provenance

| field | value |
|-|-|
| committed prediction record | `hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md` |
| **committed prediction commit** | **`897c8ab`** (2026-07-22T03:23:14Z) |
| committed prediction sha256 | `5e08cfd3…` → **verify at landing**; note the launch-pinned bytes were `5d0a1170…` and the only post-launch change was the D9 header block (proven by reverting it and rehashing) |
| command | `<<FILL from B4C11_CORRECTED_FULL_COMMAND.txt>>` |
| harness | `hierarchical-aif/scripts/run_c11_corrected_full.py` (sha256 `ae5d919b…`) |
| frozen runner consumed | `audits/phase-b/b4-identifiability-robustness-runner.py` sha256 `3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7` — **READ-ONLY, UNMODIFIED** |
| correction applied | `D1_C11_CLUSTER_COLLAPSE` only. **D3 does not apply** — C11 seeds arithmetically (`seed_base + b`), no `hash()` |
| seed convention | `seed_b = 20260717 + b`; `np.random.default_rng(seed_b)`; verified by the harness's seed-equivalence check, which **aborts** if it does not reproduce the frozen inline draw sequence |
| planned_N (frozen) | **2000** |
| actual_N | `<<FILL>>` |
| completed / failed | `<<FILL>>` |
| runtime | `<<FILL>>` (harness records `secondsPerReplicate`) |
| result sha256 | `<<FILL — from B4C11_CORRECTED_FULL.sha256>>` |
| stderr bytes | `<<FILL>>` |

## 2. Criterion and result

| field | value |
|-|-|
| frozen criterion | `collapseFraction = #{tau_hat < 1e-3} / completed`; **fires at `>= 0.25`** → `UNSTABLE_DISPERSION_U4_FIRES`, else `U4_OK` |
| observed collapseFraction | `<<FILL>>` |
| tauHatSummary (median / p025 / p975) | `<<FILL>>` |
| `intervalUsed` | `<<FILL — or NOT_APPLICABLE: the U4 criterion is a FRACTION against a threshold, not a CI contrast>>` |
| BCa width | `<<FILL or NOT_COMPUTED>>` |
| percentile width | `<<FILL or NOT_COMPUTED>>` |
| verdict | `<<FILL>>` |
| runStatus | `<<FILL from status.classify_run>>` |

**U1 / U2 / U3** are `CARRIED_FORWARD_FROM_FROZEN_ARTIFACT`, not recomputed — copied verbatim with
source path and sha256. U2 is a deterministic profile scan on the full unresampled cohort and never
touches the bootstrap, so **D1 cannot reach it**.

## 3. Old vs corrected status

| | old (frozen artifact) | corrected run |
|-|-|-|
| replicates | **30 of 2000** (`resourceBoundPartial_U4: true`) | `<<FILL>>` |
| bootstrap | **defective** — duplicate motor draws collapsed by `motorId` (80 draws → 46 groups at seed 20260717, b=0) | corrected: one exchangeable group per **draw** |
| collapseFraction | `0` | `<<FILL>>` |
| tau median | `0.2196403657219113` | `<<FILL>>` |
| verdict | `U4_OK` — **WITHDRAWN** | `<<FILL>>` |

## 4. Prediction grading — grade against the COMMITTED record, never revise it

The frozen B4 prediction is `PROFILE_FLAT_OR_WEAK`, a **disjunction**: flat tau profile (U2)
**and/or** non-trivial bootstrap collapse (U4). **The U2 arm is already refuted**
(`flatLogspan_normalized = 0.06666666666666665` against a 0.50 threshold), so the corrected U4 run
alone decides it.

| item | committed | observed | outcome |
|-|-|-|-|
| frozen expectation | `PROFILE_FLAT_OR_WEAK` | `<<FILL>>` | `<<CONFIRMED / REFUTED / NOT_ESTABLISHED>>` |
| my directional prediction (record §7) | removing the cluster collapse should make tau-collapse **MORE** likely | `<<FILL>>` | `<<SURVIVED / REFUTED / PARTIALLY SURVIVED>>` |

**State the miss plainly if it is a miss.** Being wrong in the pre-committed direction is the
recorded outcome, not a defect.

## 5. D1 closure — the routing is pre-committed, both branches

- **The old artifact stays withdrawn regardless of outcome.** The submitted `U4_OK` rested on 30 of
  2000 replicates under a defective bootstrap. Neither problem is repairable retroactively.
- **If corrected `U4_OK` lands:** D1 closes **by corrected rerun**. U4 is re-established for C11
  **on the corrected run only, at frozen N**. It does **not** retroactively validate the withdrawn
  artifact. A defect that happened to produce a right-looking answer is still a defect.
- **If corrected U4 fires:** D1 closes as a **substantive correction against the old U4** — the
  original reading was an artifact of the cluster collapse. This is the more informative branch.
- **If the run is incomplete / no successful bootstrap:** `PARTIAL_NOT_ESTABLISHED`, no verdict,
  D1 stays `OPEN`. A partial run may never be reported as a status (D2).
- **The N=5 paired diagnostic remains DIAGNOSTIC ONLY** and licenses no verdict. Likewise the
  25-replicate `LEGACY_DEFECTIVE_FOR_COMPARISON_ONLY` arm is a defect-magnitude **measurement**,
  never evidence.

## 6. Lane impact — scoped, never global

| lane | impact |
|-|-|
| **LANE B** | `<<FILL>>` — C11 U4 only |
| **LANE A** | duration-only B3/B4 **unchanged** |
| **LANE C** | **unaffected** — no mark field read |
| **LANE D** | **unaffected** — the F-side model is not entered in this cell |
| **LANE E** | `<<FILL>>` |

**B4C10's favourable M4 result may NOT be transferred here** — different model, different
likelihood structure.

## 7. P-ladder mapping — map, never redefine

`P6` is carried **per scope**. This cell speaks to **`P6` for C11 U4 only**. State the scoped
sentence, e.g.: *"`P6` for C11 U4 is `<<FILL>>` on the corrected run; `P6` for duration-only B3/B4
is unchanged; `P6` for the Wadhwa mark process remains retrospective-only."*
**No unscoped weakening statement.** `P8` remains `FULL_PARITY = false`; first unsatisfied level
`P4`.

## 8. Prospectivity

`B4C11` prediction record committed **`897c8ab`** at 2026-07-22T03:23:14Z, while the run was at
210/2000 replicates and **no result file existed**. Verdict moves
`PENDING_NO_OBSERVATION_YET` → **`SATISFIED`** on landing, pinned by
`test_b4c11_prediction_was_committed_before_its_observation`. Per D9, flip `PENDING → PROSPECTIVE`
**only in the result commit**, and the prediction and result must **never share a commit**.

## 9. Wording

**Allowed:** "corrected full run", "CI-bound verdict", "not established", "U4 re-established on the
corrected run only", "the withdrawn `U4_OK` remains withdrawn", "target hypothesis".
**Forbidden as claims:** the canonical list lives in `claim_guard.FORBIDDEN` — reference it, do
**not** re-transcribe it as a wrapped catalogue (a soft-wrapped list reads as a bare assertion and
fails the guard; that has already happened once).

## 10. Limitations

`<<FILL>>` — at minimum: one cohort; 80 training motors; U4 is a stability check on **one
parameter** of **one** frozen competitor; identifiability is not correctness and is not mechanism;
the retained adverse M2-over-M3 finding is unchanged and reported alongside.

---

`NEXT_ACT = <<FILL>>`
