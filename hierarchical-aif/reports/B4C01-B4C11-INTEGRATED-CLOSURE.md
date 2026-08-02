# B4C01 + B4C11 — Integrated Closure

**Date:** 2026-07-22 · **Gate:** H-AIF-G5 (all four corrected cells now landed) · **Lane:** **B**
**Scope:** the two cells that landed after connectivity loss. This document integrates them; it
introduces no new claim, moves no P-level, and asserts nothing about biological parity.

> **Neither B4C01 nor B4C11 is evidence of biological parity.** B4C01 scores *synthetic* data;
> B4C11 is an identifiability check on one parameter of one frozen competitor. Full biological
> parity is not a current status. It is the target world defined by the receipts.

---

## 1. B4C01 — result and interpretation

**`8256cb12…`**, full frozen N (200/generator × 5 = 1000 sims), **0 failures**, prospectivity
**`SATISFIED`** (committed `28ce738` with the cell never having run at any N).

**Verdict `NOT_ESTABLISHED`; single failing criterion `M0_EXPONENTIAL:self_win` (0.290 < 0.5).**
All four parameterised generators recovered their true parameters **1–2 orders of magnitude inside
tolerance**.

**Class B — a power / assay-resolution finding, not a fitter defect.** The design resolves
structurally distinct generators (M3 self-wins 0.935, M2 0.885) but is **nesting-blind**: M0 —
nested inside M1 (`k=1`) and M5 (`shape=1`), a degenerate limit of M3 — cannot reliably win its own
competition because the out-of-sample penalty for the competitors' extra parameters (~`p/2n` ≈
0.0006 nats) sits far below the sampling noise of a motor-equal score over 19 synthetic holdout
motors. Full detail: `reports/B4C01-CORRECTED-FULL-REPORT.md`.

## 2. B4C11 — result and interpretation

**`564a5b0f…`**, full frozen `N_boot = 2000`, **0 failures**, seed sequence proven
`IDENTICAL_TO_FROZEN_INLINE_DRAW_SEQUENCE`, group counts **80/80** (the D1 fix working),
prospectivity **`SATISFIED`** (committed `897c8ab` ~19.4 h before the observation).

**`collapseFraction_tau_lt_1e_3 = 0.0055` < 0.25 → `U4_OK`** (branch a). M7's dispersion parameter
`tau` is **identified on this cohort** under the frozen criterion, on a *valid* motor-cluster
bootstrap. The submitted 30-replicate artifact **stays withdrawn**.

**The honest nuance, measured not asserted.** The correction moved `tau` toward collapse exactly as
the D1 mechanism argued — corrected tau below legacy in **25/25** paired replicates
(`medianDeltaTau = −0.0546`), the withdrawn artifact's `p025` 0.1766 dropping to a corrected 0.0853.
The old number was mildly over-optimistic. But at ~85× the collapse boundary with 0.55% of
replicates crossing, **the corrected verdict is still `U4_OK`**. Full detail:
`reports/B4C11-CORRECTED-FULL-REPORT.md`.

## 3. D1 / D2 / D3 closure state

| defect | status | receipt |
|-|-|-|
| **D1** C11 cluster collapse | **`CLOSED_BY_CORRECTED_RERUN`** | B4C11 `564a5b0f…`, 2000/2000, `U4_OK`; effect size measured (−0.0546 tau, 25/25 directional, groups 46–59 → 80). Withdrawn artifact stays withdrawn |
| **D2** resource overestimate | **`CLOSING` → effectively discharged for the four cells** | all four re-measured **far below** the figures that justified their partial/NOT_RUN status: C10 2.3 h (not "infeasible"), C02 8.17 h (not 150–250 h), C01 16.83 h (not 250–400 h), C11 21.12 h (not the 20.1 h estimate — the one that came in slightly *over*, and honestly recorded). Refinement earned: **measure in the regime the run will run in** — C01's under-contention smoke (61.42 s/sim) beat the cross-cell projection (49.0) at predicting the realised 60.58 |
| **D3** hash-seed nondeterminism | **`CLOSED`** | both `hash()`-affected cells (C02, C01) completed deterministically with `PYTHONHASHSEED` unset, 0 failures each |

**Closure summary is now: 6 CLOSED (D1, D3, D4, D8, D10, D11), 2 CLOSING (D2, D7), 3 QUARANTINED
(D5, D6, D9), 0 OPEN.** No defect is unrouted.

## 4. What B4C01 says about assay power

This is the sanity-floor control that makes every other B4 and F-side result interpretable, and it
now carries a **measured** statement about what the motor-equal assay can and cannot resolve at 19
holdout motors:

- **It resolves structurally distinct models** — a two-timescale generator self-wins 0.935, a
  distinctive-tail lognormal 0.885.
- **It is nesting-blind** — a true exponential wins its own competition only 0.290 of the time,
  barely above the ~0.25 that near-random selection among ~4 indistinguishable models would give.
- Therefore: **an `INCONCLUSIVE` / `NOT_ESTABLISHED` contrast between nested or near-equivalent
  models is the *expected output* of this design, not evidence about the models.** "Underpowered is
  not equivalence" now has a number attached, and a sharper name: *nesting-blind at this cohort
  size.*

## 5. What B4C11 says about hierarchy stability

- On a **valid** bootstrap, M7's dispersion parameter is **identified** on this cohort (`U4_OK`,
  collapse 0.0055) — the hierarchy does not silently degenerate to `tau → 0` under resampling.
- **But identification is not necessity, and it is not mechanism.** B4C11 says `tau` is *estimable*;
  it says nothing about whether the hierarchy *earns its complexity*. That question was answered
  separately and adversely: the tau-limit probe and the F-side scoring found the F-side hierarchy
  buys **nothing measurable** over its own `tau → 0` limit `M1_WEIBULL` (contrast `+0.000615`,
  half-width `0.0111`), and reproduces frozen M7 to `2.5e-7` nats.
- So the two readings sit together honestly: **`tau` is identified (B4C11) and simultaneously does
  little predictive work (F-side / tau-limit).** A parameter can be well-determined and
  near-useless; both are true here, and neither is mechanism.

## 6. Implication for B3 / F-side inconclusive contrasts

B4C01 and B4C11 **converge on the same reading of every inconclusive contrast in the programme**,
from two independent directions:

- **B4C01 (assay side):** the design cannot separate nested near-equivalent models at 19 motors,
  *even under correct specification*.
- **F-side + D10 (model side):** the candidate is `NOT_ESTABLISHED` against M3/M2/M8/M1, and the one
  contrast that "resolved" (M7, 2.5e-7 nats) did so only because the two models are numerically
  identical — the CI rule has no minimum effect size.

**Together:** the pervasive `INCONCLUSIVE`/`NOT_ESTABLISHED`/`SUB_FLOOR` verdicts across B3 and the
F-side scoring are a **property of the assay at this sample size and of the models' near-equivalence
on duration alone**, not a set of pending questions that more analysis will resolve. The binding
constraint is **data (independent motors), not model math or code**. This is the single most
important integrated conclusion, and it is a statement about *interpretation* — it raises no level
and changes no frozen verdict.

## 7. What got stronger

- **`P0`/`P1` implementation integrity.** All four corrected cells ran deterministically with 0
  failures; six frozen models reproduced at exact-zero oracle residual; two guards (`claim_guard`,
  `numeric_provenance_guard`) now mechanically defend wording and declared-number provenance.
- **`P6` for C11 U4** — withdrawn on defect, then **re-established on the corrected run only**. The
  gate ran end to end: withdraw the defective evidence, restore on a valid rerun, never restore the
  defective artifact.
- **Prospective discipline.** Three of the four cells (C02, C01, C11) are genuinely prospective by
  commit graph; the two that cannot be (B4C10, F-side) are pinned `NOT_SATISFIED` by D9, and a
  launcher now refuses to run on an uncommitted prediction.
- **The interpretation of `P3`** — now backed by a measured power characterisation (B4C01) rather
  than a bare "underpowered" caveat.

## 8. What got weaker

- **Nothing in the evidence base.** No frozen verdict was overturned; no measurement was retracted.
- **Confidence in the submitted C11 `U4_OK` — correctly.** It was withdrawn (defective bootstrap,
  30 replicates) and replaced, not restored. The corrected tau distribution is shifted toward zero
  relative to the withdrawn artifact, so any prior over-reliance on that specific number is now
  known to have been slightly misplaced — a weakening of a *defective claim*, which is the gate
  working, not a retreat.
- **The case that the constrained hierarchy is a *distinct, useful* model.** B4C11 (identified) plus
  F-side (buys nothing over M1, reproduces M7) leaves the hierarchy as **architecture, not
  evidence** on the current data — a design signal, recorded as such.

## 9. What remains owed for P4 / P5 / P6 / P7 / P8

| level | status | what is owed — and can it be closed in-repo? |
|-|-|-|
| `P4` transfer | `NOT_ESTABLISHED` — **first unsatisfied level** | an independent dataset with a predeclared split. **Cannot be closed by any modelling in this repository** |
| `P5` intervention | `NOT_ESTABLISHED` | perturbation data with recorded onset (load / stator / PMF), paired pre-post on the same motors. The action set is empty — **structural**, not sample-size. `expected_free_energy` stays fenced. **Cannot be closed in-repo** |
| `P6` structural/mechanistic | **carried per scope** | C11 U4 **re-established (corrected run only)**; duration-only B3/B4 unchanged; Wadhwa mark-process retrospective-only (D5/D6); full motor-stack AIF pending. A mechanism discriminator that makes competing models disagree is owed — and B4C01 shows duration alone cannot supply it at this cohort size |
| `P7` independent replication | `NOT_ESTABLISHED` | a second lab/dataset. **Cannot be closed in-repo** |
| `P8` full verdict | **`FULL_PARITY = false`** | conjunctive; unchanged. First unsatisfied level remains `P4` |

**`P4`, `P5` and `P7` are irreducibly external.** Saying so plainly is what makes the movable rungs
worth moving.

## 10. Next highest-EFE action

B4C01 identified the binding constraint precisely: **the assay cannot discriminate near-equivalent
models on duration alone at 19 motors.** So the highest-expected-information-gain action is *not*
more modelling on this cohort — the tau-limit, F-side, materiality and D10 work already showed that
path is exhausted. It is to **make competing models disagree**, which requires either:

1. **more independent motors** (a transfer cohort — moves `P4`, and directly relaxes the nesting
   blindness B4C01 measured), or
2. **an intervention channel** (moves `P5`, and is the only route that makes the G-side testable at
   all).

Both are **external-data** actions. Inside the repository, the honest next step is not a new science
run but to consolidate: the four corrected cells and the F-side scoring are complete, all defects
are routed, and the receipt tree (`docs/WORLD-WHERE-FULL-BIO-PARITY-IS-TRUE-RECEIPT-TREE.md`)
already names the external receipts each remaining rung needs. **The programme is at a genuine
data-bound boundary, and reporting that boundary is a legitimate scientific outcome, not an
incomplete task.**

---

`NEXT_ACT = git status --short  # review the full corrected-cell + closure batch; nothing is committed or pushed. Present the four-cell + integrated-closure state to the principal for the commit/authorization decision (per D9, the result commits are what flip C02/C01/C11 PENDING -> PROSPECTIVE).`
