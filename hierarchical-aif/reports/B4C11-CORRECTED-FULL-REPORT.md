# B4C11 — Corrected Full-N Result Report

**Gate:** H-AIF-G5 · **Cell:** `B4C11_M7_STRUCTURAL_IDENTIFIABILITY` · **Lane:** **B** · **Date:** 2026-07-22
**Result:** `hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_RESULT.json`
sha256 `564a5b0f4461c83fe2c8792a2304dc136799b0923d887a27a60572361a851b53`
**Committed prediction:** `hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md` @ **`897c8ab`**
**Defect routed:** `D1_C11_CLUSTER_COLLAPSE`
**Maps to:** `P6` for **C11 U4 only** — a scoped, per-cell identifiability statement. **No P-level is raised.**

---

## 1. Executive result

B4C11 ran to completion at the **full frozen `N_boot = 2000`** with the D1 cluster-collapse
correction: **2000 completed, 0 failed**, `resourceBoundPartial: false`,
`runStatus = ELIGIBLE_FOR_FROZEN_VERDICT`.

**`collapseFraction_tau_lt_1e_3 = 0.0055` (11 of 2000) < 0.25 → verdict `U4_OK`.** This is
pre-committed **branch (a)**.

- **`M7_status = IDENTIFIED_ON_THIS_COHORT`** — U4 newly computed on the corrected bootstrap;
  U1/U2/U3 carried forward verbatim from the frozen artifact.
- **The withdrawn artifact stays withdrawn.** The submitted `U4_OK` — 30 of 2000 replicates under
  the defective cluster bootstrap — is **not** restored by this run. D1 moves
  **`OPEN` → `CLOSED-BY-RERUN`** for the C11 U4 lane only.
- The frozen B4 prediction `PROFILE_FLAT_OR_WEAK` is **REFUTED at full N** (both arms — see §4).

## 2. Result detail

| field | value |
|-|-|
| completed / failed | **2000 / 0** |
| `collapseFraction_tau_lt_1e_3` | **0.0055** (11 collapsed) |
| frozen criterion | `>= 0.25` → `UNSTABLE_DISPERSION_U4_FIRES`; else `U4_OK` — **unchanged** |
| verdict | **`U4_OK`** |
| `tauHatSummary` median | **0.16824474021475483** |
| `tauHatSummary` p025 / p975 | **0.0852685819370822 / 0.2270136179903497** |
| U4 group count (min/max) | **80 / 80** — one exchangeable group per draw, the D1 fix working |
| distinct motors drawn (min/max) | 40 / 60 |
| `intervalUsed` / BCa / percentile width | **`NOT_APPLICABLE` / `NOT_COMPUTED` / `NOT_COMPUTED`** — the U4 criterion is a **fraction against a threshold**, not a CI contrast, so no interval exists to quote |

**U1 / U2 / U3 carried forward** (`CARRIED_FORWARD_FROM_FROZEN_ARTIFACT`, source sha256
`f361e4dc…`): U1 `TAU_INTERIOR`, U3 `SUPPORTED_OVER_M1`, U2 `U2_OK`
(`flatLogspan_normalized = 0.06666666666666665`, far below the 0.50 fire threshold). U2 is a
deterministic profile scan on the full unresampled cohort and never touches the bootstrap, so
**D1 cannot reach it** — copied, not recomputed.

## 3. Provenance and integrity

| field | value |
|-|-|
| command | `python hierarchical-aif/scripts/run_c11_corrected_full.py 2000 …/B4C11_CORRECTED_FULL_RESULT.json --paired 25` |
| harness | `hierarchical-aif/scripts/run_c11_corrected_full.py` (sha256 `ae5d919b…`) |
| frozen runner consumed | `audits/phase-b/b4-identifiability-robustness-runner.py` sha256 `3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7` — **READ-ONLY, UNMODIFIED**. `b4._fit_m7_reduced` (26-start L-BFGS-B) and `b3.m7_train_nll` were called through it, not reimplemented |
| correction applied | **`D1_C11_CLUSTER_COLLAPSE` only.** `bootstrap.build_bootstrap_cohort` emits one exchangeable group per **draw**. **D3 does not apply** — C11 seeds arithmetically (`seed_base + b`), no `hash()` |
| seed equivalence | **`IDENTICAL_TO_FROZEN_INLINE_DRAW_SEQUENCE`** — the harness reproduces the frozen inline draw sequence and would have **aborted** otherwise |
| planned_N / actual_N | **2000 / 2000**; **0 failures** |
| started / ended (UTC) | `2026-07-22T01:40:03Z` → `2026-07-22T22:47:14Z` |
| runtime | **76 026.1 s = 21.12 h**; **38.01 s/replicate** |
| exit code | 0 |
| stderr | **0 bytes** |
| result sha256 | `564a5b0f4461c83fe2c8792a2304dc136799b0923d887a27a60572361a851b53` |

**NO FLOOR** was applied: a non-finite log density or a `None` fit would have incremented `failed`;
`failed = 0`, so every one of the 2000 replicates produced a finite optimum.

## 4. Prediction grading

### 4a. The frozen B4 prediction — REFUTED at full N

`PROFILE_FLAT_OR_WEAK` is a **disjunction** (flat tau profile *and/or* non-trivial collapse). **Both
arms fail:** U2 `flatLogspan_normalized = 0.0667` ≪ 0.50 (carried forward), and U4
`collapseFraction = 0.0055` ≪ 0.25. The `predictionOutcome` field records `REFUTED`. The earlier
`REFUTED_U4_PARTIAL` label is **superseded, not upgraded**.

### 4b. My committed directional prediction (record §7.3) — HIT on all five sub-commitments

The committed record predicted **branch (a)** — explicitly "against the mechanism's own direction of
concern," on measured magnitude. Graded against the numbers I committed:

| # | committed (§7.3) | observed | outcome |
|-|-|-|-|
| 1 | corrected tau median < 0.2196, expected **[0.12, 0.20]** | **0.16824** | **HIT** |
| 2 | `collapseFraction` in **[0.000, 0.02]** → **branch (a)** | **0.0055**, branch (a) | **HIT** |
| 3 | corrected `p025` > **1e-2** | **0.0853** | **HIT** |
| 4a | corrected tau < legacy in **>80%** of the paired subset | **100%** (`fracCorrectedBelowLegacy = 1.0`) | **HIT** |
| 4b | corrected group count exactly 80 in **100%** | **80/80** | **HIT** |

**A correction I owe on the record.** Earlier this session, watching the live counter at 330/2000
with `collapsed=0`, I said my committed prediction "appears headed for refutation." **That was a
misreading of my own committed prediction.** I conflated the *mechanism's direction of concern*
(the defective bootstrap should have suppressed collapse, so removing it makes collapse *more*
likely) with what I actually **committed** in §7.3, which was branch (a): collapse stays low.
Record §7.4 states this explicitly — "I am predicting against the mechanism's own direction of
concern." The committed prediction was branch (a), and it hit. The live-counter aside should never
have been offered as a read on the committed prediction, and the counter should not have been read
at all.

### 4c. The mechanism's direction was ALSO confirmed — and it is the honest nuance

The correction did move tau toward collapse, exactly as §7.1 argued: the paired legacy-vs-corrected
diagnostic (25 replicates, identical draws) shows corrected tau **below** legacy tau in **25 of 25**
(medians 0.21298 → 0.16822, `medianDeltaTau = −0.0546`), and legacy group counts inflated to 46–59
against the corrected 80/80. So:

- **The defective 30-replicate artifact was mildly over-optimistic about tau stability.** Its tau
  median was 0.2196 and its `p025` 0.1766; the corrected full-N run gives median **0.168** and
  `p025` **0.0853** — a distribution shifted toward zero, with a p025 roughly half the submitted
  value. The direction of concern that motivated D1 was real and is now measured.
- **But the effect is nowhere near the collapse boundary.** The smallest of the collapse-relevant
  quantities, `p025 = 0.0853`, is ~85× the `1e-3` threshold, and only 0.55% of replicates cross it.
  **The corrected verdict is still `U4_OK`.**

The honest one-line reading: *the old number was right for the wrong reason and slightly too
confident; corrected, on a valid bootstrap, M7's dispersion is still identified on this cohort.*

## 5. D1 closure

**`OPEN_UNTIL_CORRECTED_C11_FULL_RUN` → `CLOSED_BY_CORRECTED_RERUN`.**

- The corrected full-N run completed (2000/2000, 0 failed) on the D1-fixed builder, with the seed
  sequence proven identical to the frozen inline construction.
- **The withdrawn artifact stays withdrawn.** A defect that happened to produce a right-*looking*
  answer (0/30 collapse → `U4_OK`) is still a defect: it rested on 30 of 2000 replicates and a
  bootstrap that collapsed 80 draws into 46–59 groups. Neither is repairable retroactively, and the
  frozen artifact is not edited.
- The D1 **effect size is measured, not asserted**: −0.0546 median tau shift, 25/25 directional
  consistency, group-count inflation 46–59 → 80. This is the second demonstration after D2 that a
  defective/partial run produced a reading that a corrected full run revises.
- The N=5 paired diagnostic (`C11-PAIRED-DIAGNOSTIC.json`) and the 25-replicate
  `LEGACY_DEFECTIVE_FOR_COMPARISON_ONLY` arm remain **diagnostic only** and licensed no verdict;
  the verdict comes solely from the 2000 corrected replicates.

## 6. Prospectivity — `SATISFIED`

| fact | value |
|-|-|
| prediction record introduced by | **`897c8ab`**, 2026-07-22T03:23:14Z, committed at 210/2000 replicates with no result file in existence |
| B4C11 observation came into existence | 2026-07-22T22:47:14Z |
| ordering | **committed ~19.4 h BEFORE the observation** ✓ |
| content provenance | the only post-launch edit was the D9 header block; reverting it reproduces the launch-pinned sha256 `5d0a1170…` exactly |

Verdict moves `PENDING_NO_OBSERVATION_YET` → **`SATISFIED`**, pinned by
`test_b4c11_prediction_was_committed_before_its_observation`. Per D9, the flip
`PENDING → PROSPECTIVE` belongs **in the result commit**, and the prediction and result must
**never share a commit** — the result is currently uncommitted, so the ordering is intact.

## 7. Lane impact — scoped

| lane | impact |
|-|-|
| **LANE B** | B4C11 completes **the last of the four corrected cells**. `P6` for C11 U4 moves from **withdrawn** to **re-established on the corrected run only** |
| **LANE A** | duration-only B3/B4 **unchanged** |
| **LANE C** | **unaffected** — no mark field read |
| **LANE D** | **unaffected** — the F-side model is not entered in this cell |
| **LANE E** | **unaffected** — no parity receipt moves |

**B4C10's favourable M4 result was never transferable here, and is not invoked** — different model
(M4 pooled-i.i.d. vs M7 motor-grouped), different likelihood structure. This U4_OK stands on its
own corrected bootstrap.

## 8. P-ladder mapping — map, never redefine

`P6` is carried **per scope**. The scoped statement now in force:

> **`P6` for C11 U4** is **re-established on the corrected full-N run only** (`U4_OK`,
> `collapseFraction 0.0055`, N=2000) — M7's dispersion parameter is identified on the
> `derived_eligible_1_to_8` cohort under the frozen collapse criterion. The submitted 30-replicate
> artifact remains withdrawn. **`P6` for duration-only B3/B4 is unchanged; `P6` for the Wadhwa
> mark-process is retrospective-only; `P6` for the full motor-stack AIF is pending.**

**Identifiability is not correctness and is not mechanism.** U4 is a stability check on **one
parameter** (`tau`) of **one** frozen competitor (M7) on **one** cohort. It does not make M7
correct and is not evidence for any mechanism. **`P8` remains `FULL_PARITY = false`; first
unsatisfied level `P4` transfer. No P-level is raised.**

## 9. Wording

**Allowed:** "corrected full run", "U4 re-established on the corrected run only", "the withdrawn
`U4_OK` remains withdrawn", "CI-bound verdict" (where one applies), "not established".
**Forbidden as claims:** the canonical list in `claim_guard.FORBIDDEN` — referenced, not
re-transcribed. In particular this report does not assert that any diagnostic *proves* the U4
result, nor that any mechanism, parity, or active-inference claim follows from an identifiability
check.

## 10. Limitations

One cohort; 80 training motors. U4 is a stability check on a single parameter of a single competitor
under a single criterion. The corrected tau distribution is shifted toward zero relative to the
withdrawn artifact — this cell shows it does not reach the collapse boundary, not that `tau` is
sharply determined. Carried-forward U1/U2/U3 are copied from the frozen artifact and were not
recomputed here. The retained adverse B3 finding (M2 over M3, ~0.0369 nats event-pooled) is
unchanged and reported alongside.

---

`NEXT_ACT = write hierarchical-aif/reports/B4C01-B4C11-INTEGRATED-CLOSURE.md`
