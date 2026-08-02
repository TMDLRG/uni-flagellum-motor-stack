# TEMPLATE — B4C01 Corrected Full-N Result Report

> **THIS IS A TEMPLATE, NOT A RESULT.** `B4C01` had not landed when this file was written. Every
> `<<FILL>>` marker is an unfilled slot. This file carries **no result, no verdict and no
> evidence**, and it must never be cited. The landed report goes to
> `hierarchical-aif/reports/B4C01-CORRECTED-FULL-REPORT.md`; this skeleton stays here.

**Gate:** H-AIF-G5 · **Cell:** `B4C01_SYNTHETIC_PARAMETER_RECOVERY` · **Lane:** **B**
**Defects routed:** `D3` (corrected here) · `D2` (cost re-measured) · `D4` (frozen reason text wrong)

---

## 1. Provenance

| field | value |
|-|-|
| committed prediction record | `hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md` |
| **committed prediction commit** | **`28ce738`** (2026-07-22T04:05:29Z) |
| committed prediction sha256 | `5e08cfd396bf7e8567ab4c4556e6b78dd84ab963e9c7919e1c9f4e1afbfeda8d` — committed blob == on-disk == launch-pinned, **no drift** |
| command | `<<FILL from B4C01_CORRECTED_FULL_COMMAND.txt>>` |
| harness | `hierarchical-aif/scripts/run_c01_corrected_full.py` (sha256 `e4474fb7…`) |
| frozen runner consumed | `audits/phase-b/b4-identifiability-robustness-runner.py` sha256 `3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7` — **READ-ONLY, UNMODIFIED** |
| correction applied | `D3_HASH_SEED_NONDETERMINISM` only (`seeding.stable_seed` replaces `hash(gen) % 100000`). `+ sim`, `seed_base = 20260801`, generators, tolerances, self-win threshold, model set and verdict rule **all unchanged** |
| planned_N (frozen) | **200 per generator × 5 generators = 1000 simulations** |
| actual_N | `<<FILL>>` |
| completed / failed per generator | `<<FILL>>` |
| runtime | `<<FILL>>`; harness records `secondsPerSim`. Projection was 13.62 h from B4C02's measured 49.015 s/sim; the N=1 smoke measured 61.42 s/sim **under contention with B4C11** — report the realised figure and the gap |
| result sha256 | `<<FILL — from B4C01_CORRECTED_FULL.sha256>>` |
| stderr bytes | `<<FILL>>` |

**D4:** the frozen `NOT_RUN` reason blames an *"M4/M7-inclusive competition"*. **This cell does not
fit M4 or M7.** `corrected_reasons.C01_REASON` supersedes it for reporting; the frozen artifact is
**not edited**.

## 2. Criterion and result

Frozen rule, verbatim: **`PASS` iff for EVERY generator `withinTolerance` AND `self_win_frac > 0.5`**
(`M0_EXPONENTIAL`: self-win only). Otherwise `NOT_ESTABLISHED`.

| generator | true param | tolerance | median recovered | bias | withinTolerance | self_win_frac | self-win passes |
|-|-|-|-|-|-|-|-|
| `M0_EXPONENTIAL` | *(none)* | — | — | — | — | `<<FILL>>` | `<<FILL>>` |
| `M1_WEIBULL` | `k = 0.6250888335850175` | `0.1` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` |
| `M2_LOGNORMAL` | `sigma = 1.5783076101407152` | `0.1` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` |
| `M3_TWO_TIMESCALE` | `w = 0.3933559993214189`, `lambdaFast = 0.44485933051063775` | `w 0.1`, `log10(lf) 0.2` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` |
| `M5_GAMMA` | `shape = 0.5115799798433341` | `0.15` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` | `<<FILL>>` |

| field | value |
|-|-|
| `intervalUsed` | **`NOT_APPLICABLE`** — the frozen C01 criteria are a **median-bias tolerance** and a **win fraction**, neither of which is a CI contrast |
| BCa width | **`NOT_COMPUTED`** — no interval is computed by this cell |
| percentile width | **`NOT_COMPUTED`** — same reason |
| verdict | `<<FILL>>` |
| runStatus | `<<FILL>>` |

**`withinTolerance` is a BIAS test on the MEDIAN, not a spread test.** A generator could be wildly
variable per simulation and still pass. The spread (`p05`/`p95`) is reported alongside but does
**not** enter the frozen verdict. That weakness is the frozen criterion's, and it is applied as
written rather than fixed here.

## 3. Failure classification — the required split, decided BEFORE reading the numbers

Classify the outcome into exactly one of these, and say which:

| class | condition | reading |
|-|-|-|
| **A. PASS** | every generator passes both conditions | sanity floor met. **Not evidence for any mechanism, for M3, or for the motor-stack model.** It strengthens the *interpretability* of B4C02's adverse result |
| **B. self-win / power failure** | `withinTolerance` passes everywhere, but some generator has `self_win_frac <= 0.5` | **POWER / ASSAY-RESOLUTION finding, NOT a fitter defect.** Nested near-equivalent models cannot be separated by a motor-equal score over 19 synthetic holdout motors. Reporting this as "the B3 pipeline is broken" is a **misreading and is forbidden** |
| **C. parameter-recovery failure** | any generator fails `withinTolerance` | **Materially more serious.** Puts `P1` for the affected fitter in question. Name the fitter, the bias, and the tolerance it exceeded |
| **D. FAILED_RUN** | harness defect, non-finite halt, or crash | No verdict of any kind. Repair loop. **A crashed run is not a scientific negative** |

If **both** B and C occur, report both and do not let the milder one absorb the graver.

## 4. Prediction grading — grade against the COMMITTED record, never revise it

Frozen expectation: **`PASS`**. The committed record predicts **`NOT_ESTABLISHED`**, with
`M0_EXPONENTIAL` the failure point at `self_win_frac` ∈ [0.20, 0.50] (most likely 0.30–0.40),
because M0 is nested inside M1 (`k=1`) and M5 (`shape=1`) and is a degenerate limit of M3, so the
~`p/2n` ≈ 0.0006-nat out-of-sample penalty sits far below the sampling noise of a motor-equal score
over 19 synthetic holdout motors. Predicted ordering: **M0 < M5 < M3 < M1 < M2**, with M2 > 0.80.

| item | committed | observed | outcome |
|-|-|-|-|
| frozen expectation | `PASS` | `<<FILL>>` | `<<CONFIRMED / REFUTED>>` |
| verdict prediction | `NOT_ESTABLISHED` | `<<FILL>>` | `<<SURVIVED / REFUTED>>` |
| M0 self_win_frac in [0.20, 0.50] | yes | `<<FILL>>` | `<<HIT / MISS>>` |
| all four parameterised generators `withinTolerance` | yes | `<<FILL>>` | `<<HIT / MISS>>` |
| ordering M0 < M5 < M3 < M1 < M2 | yes | `<<FILL>>` | `<<HIT / MISS>>` |
| M2 self_win_frac > 0.80 | yes | `<<FILL>>` | `<<HIT / MISS>>` |

Record every miss item by item. **This is the cleanest prospective cell in the batch** — committed
with zero observations of any kind in existence — so its scorecard carries real weight, and shading
it would waste the one cell that was set up properly.

## 5. Lane and defect impact

| lane | impact |
|-|-|
| **LANE B** | `<<FILL>>` — completes the four corrected cells |
| **LANE A** | duration-only B3/B4 **unchanged** — every dataset here is SYNTHETIC |
| **LANE C** | **unaffected** — no mark field read |
| **LANE D** | **unaffected** — the F-side model is not entered |
| **LANE E** | `<<FILL>>` |

**D3** closes if the run completes deterministically. **D2** closes when all four corrected cells
have landed — report the measured cost against the frozen 250–400 h claim.

## 6. P-ladder mapping — map, never redefine

This cell speaks to **`P0`/`P1` pipeline integrity** and constrains the **interpretation of `P3`**.
It **cannot move `P6`**. Every dataset is **SYNTHETIC** and none may be labelled `OBSERVED`.
A class-B outcome is a statement about the **assay**, not the models, and must be written that way.
`P8` remains `FULL_PARITY = false`; first unsatisfied level `P4`.

## 7. Prospectivity

Prediction record committed **`28ce738`** at 2026-07-22T04:05:29Z, while the cell had **never run
at any N** (frozen artifact `status=NOT_RUN`, `actual_N=0`; no smoke test, no partial, no result
anywhere). Committed blob == on-disk == launch-pinned `5e08cfd3…`, **no drift**. Verdict moves
`PENDING_NO_OBSERVATION_YET` → **`SATISFIED`** on landing, pinned by
`test_b4c01_prediction_was_committed_before_any_observation`. Per D9, flip
`PENDING → PROSPECTIVE` **only in the result commit**; prediction and result must **never share a
commit**.

## 8. Wording

**Allowed:** "sanity floor met / not met", "power-limited at this holdout size", "not established",
"corrected full run", "CI-bound verdict" (where one applies).
**Forbidden as claims:** canonical list in `claim_guard.FORBIDDEN` — reference it, do **not**
re-transcribe it as a wrapped catalogue. Also forbidden here: any statement that this cell tests
the motor-stack AIF model or the mark process; "M3 is vindicated"; "M2 is the UNI model".

## 9. Limitations

`<<FILL>>` — at minimum: **synthetic worlds only**; 5 generators, 6 fitted competitors (M4/M7/M8
skipped **by construction**, so this cell says nothing about the mixture, hierarchical or KDE
models); one cohort geometry with 19 holdout motors, whose sampling noise is inherited by every
simulation; `withinTolerance` tests bias, not spread.

---

`NEXT_ACT = <<FILL>>`
