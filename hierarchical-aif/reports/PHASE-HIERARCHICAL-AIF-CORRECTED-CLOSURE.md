# Phase Closure — Hierarchical-AIF Corrected B4 Programme

**Date:** 2026-07-22 · **Gate:** H-AIF-G5 complete, H-AIF-G9 recorded · **Scope:** the corrected B4
programme (C01/C02/C10/C11), the F-side motor-stack build and scoring, and the eleven defects
routed along the way. This is a **status closure**, not a release. It introduces no new claim.

> **Full biological parity is not a current status. It is the target world defined by the receipts.**
> Nothing in this phase is evidence of it.

---

## 1. What was corrected

- **D1 — C11 cluster-collapse bootstrap.** The committed runner regrouped resampled motors by
  `motorId`, collapsing 80 draws into 46–59 groups and over-sharpening each duplicated motor's
  latent. Repaired by `bootstrap.build_bootstrap_cohort` (one exchangeable group per draw), and the
  corrected full-N run landed.
- **D3 — hash-seed nondeterminism.** C01/C02 seeded via process-varying `hash(str)`. Replaced by
  `seeding.stable_seed` (SHA-256). Both affected cells completed deterministically.
- **D2 — resource-bound overestimate.** Four cells were `NOT_RUN`/partial on cost claims of
  150–400 h; all four ran in 2.3–21.1 h. Every `RESOURCE_BOUND` reason is discharged by measurement.
- **D4 — C01 reason mismatch** (superseded in new reports; frozen artifact not edited).
- **D7 — width = percentile not BCa** (forward guard + corrected 0.042-nat floor).
- **D8 — ledger claimed undelivered tests** (delivered + mutation-tested).
- **D10 — CI rule has no minimum effect size** (added interpretation layer; frozen verdicts
  unaltered).
- **D11 — fabricated/transplanted numbers in a generated report** (corrected + a mechanical
  `numeric_provenance_guard`).

## 2. What now stands

- **All four corrected B4 cells landed at full frozen N, 0 failures each** (C11 had 0/2000 failed;
  C10 had 6/2000). Each hashed, verified, and reported against its committed prediction.
- **B3 stands unchanged.** The corrected work touched none of the B3 leaderboard.
- **The F-side motor-stack model is built, scored, and reproduces six frozen models at exact-zero
  oracle residual.** Determinism proven byte-identical.
- **Two mechanical guards** now defend the namespace: `claim_guard` (wording) and
  `numeric_provenance_guard` (declared numbers).
- **Test suite: 501 passed, 2 skipped, 1 xfailed.** Frozen evidence: 250 files, no drift.

## 3. What was withdrawn

- **The submitted C11 `U4_OK`** (30 of 2000 replicates under the defective bootstrap). It is
  **withdrawn and stays withdrawn** — not restored by the corrected run. A defect that produced a
  right-*looking* answer is still a defect.
- **The `PROSPECTIVE` label from B4C10 and the F-side scoring** — both are `NOT_SATISFIED` by the
  commit graph (D9); their prediction and result entered the repo in one commit (B4C10) or the
  protocol was untracked while the result existed (F-side). The measurements stand; the *label* does
  not.
- **The 250–400 h and 150–250 h `RESOURCE_BOUND` cost claims** — superseded by measured runtimes.

## 4. What was replaced

- **C11 U4** — the withdrawn 30-replicate reading is replaced by the corrected full-N `U4_OK`
  (collapse 0.0055, N=2000, groups 80/80), **within C11 U4 scope only**.
- **The "0.064-nat resolution floor"** — replaced by the corrected BCa half-width **0.042 nats**
  (D7), which drives the materiality reading.
- **The frozen C01/C02/C10/C11 `NOT_RUN`/partial statuses** — replaced by full-N results, without
  editing the frozen artifacts.

## 5. What remains NOT_ESTABLISHED

- **`P4` transfer** — the first unsatisfied level. No independent dataset.
- **`P5` intervention** — the action set is empty; **structural**, not sample-size.
- **`P6`** — carried per scope: C11 U4 re-established (corrected run only); Wadhwa mark-process
  retrospective-only (D5/D6); full motor-stack AIF pending a mechanism discriminator.
- **`P7` independent replication** — external review in progress, not complete.
- **The candidate's superiority over any serious adversary** — `NOT_ESTABLISHED` throughout.

## 6. What C01 says about assay power

Under **correct specification**, the 19-motor motor-equal assay:
- **resolves structurally distinct models** (M3 self-wins 0.935, M2 0.885), but
- **is nesting-blind** — a true exponential wins its own competition only **0.290** of the time,
  barely above the ~0.25 that near-random selection among ~4 indistinguishable models gives.

**Parameter recovery is intact** (all four parameterised generators 1–2 orders inside tolerance), so
this is **not a fitter defect** — it is a measured statement that this design cannot separate nested
near-equivalent dwell families at this cohort size. **"Underpowered is not equivalence" now has a
number.**

## 7. What C11 says about M7 hierarchy stability

On a **valid** bootstrap, M7's dispersion parameter `tau` is **identified** on this cohort
(`U4_OK`, collapse 0.0055) — it does not silently degenerate to `tau → 0` under resampling. The
corrected distribution is shifted toward zero relative to the withdrawn artifact (p025 0.1766 →
0.0853), so the old number was mildly over-optimistic, but the effect is ~85× from the collapse
boundary. **Identification is not necessity and is not mechanism.**

## 8. What F-side scoring says about the candidate model

The constrained F-side motor stack:
- scored **`NOT_ESTABLISHED`** against `CONTROL_CURRENT` (M3) and every serious adversary;
- **reproduces frozen M7 to `2.5e-7` nats** — at this resolution a re-derivation of the incumbent,
  not a new model;
- **buys nothing measurable over its own `tau → 0` limit `M1_WEIBULL`** (contrast `+0.000615`,
  half-width `0.0111`);
- ranks **5th of 10** on the combined leaderboard;
- exposed **D10** via a `2.5e-7`-nat "resolved" contrast against M7.

**The hierarchy is architecture, not evidence, on the current data** — a design signal.

## 9. Why M2 remains a serious adversary

`M2_LOGNORMAL` leads the held-out motor-equal leaderboard (`3.4093`), ahead of every mechanistic
candidate including the F-side stack (`3.4327`). B4C02 showed this advantage is **generator-specific**
(it appears under a three-timescale world, 0.94, and vanishes under the others, 0.005) — so "it is
just heavy-tailed shape" is **not** an adequate account, which makes the M2-over-M3 result *more*
interesting, not less. M2 is a **one-parameter adversarial baseline, never the UNI model**, and it
is kept alive precisely because it is not yet beaten. Keeping it alive is strong inference.

## 10. Why full biological parity is not inferred

- Every B4C01/B4C02 dataset is **SYNTHETIC**; none may be labelled `OBSERVED`.
- B4C10/B4C11 are **identifiability checks on frozen fits**, not observations, not mechanism.
- The F-side model **beats no serious adversary** and is a re-derivation of M7.
- **`P4`, `P5`, `P7` are irreducibly external** and unsatisfied.
- `P8` is **conjunctive** and `FULL_PARITY = false`; the first unsatisfied level is `P4`.

No result in this phase licenses a claim of biological parity, active inference demonstrated, or
G-side biological policy selection. The dataset is passive; the action set is empty.

## 11. Existing P0–P8 mapping

| level | status | note |
|-|-|-|
| `P0` computational integrity | **holds — strengthened** | frozen baseline re-verified; determinism proven; two mechanical guards |
| `P1` equation/implementation | **defects found and fixed in the new namespace; strengthened** | D1/D3 corrected; six frozen models reproduced at exact-zero oracle residual |
| `P2` observational | **unchanged** | no new observation; raw archive not located |
| `P3` held-out predictive | **unchanged; B3 stands — interpretation now measured** | B4C01 characterises the assay's nesting-blindness; the F-side candidate joined at 5th of 10 without moving the level |
| `P4` transfer | **`NOT_ESTABLISHED` — first unsatisfied** | single study; irreducibly external |
| `P5` intervention | **`NOT_ESTABLISHED`** | empty action set; structural; irreducibly external |
| `P6` structural/mechanistic | **carried per scope** | C11 U4 re-established (corrected run only); duration-only unchanged; mark-process retrospective-only; full AIF pending |
| `P7` independent replication | **`NOT_ESTABLISHED`** | irreducibly external |
| `P8` full verdict | **`FULL_PARITY = false`** | conjunctive; first unsatisfied `P4` |

**No P-level was raised by this phase.** One `P6` scope (C11 U4) was lowered on defect and
re-established on the corrected run — the gate working end to end.

## 12. Next required receipts for P4 / P5 / P6 / P7 / P8

| level | receipt required | in-repo? |
|-|-|-|
| `P4` | an independent held-out cohort with a predeclared split and enough independent motors to resolve the contrasts B4C01 showed this cohort cannot | **NO — external data** |
| `P5` | perturbation data: a manipulated variable (load / stator / PMF) with recorded onset, paired pre/post on the same motors, enough motors per condition for a CI-bound verdict | **NO — external data** |
| `P6` | a mechanism discriminator that makes AIF-motor-stack / M2 / M4 / M7 / three-timescale / censoring **disagree** under transfer or intervention; plus raw-archive re-derivation for the mark process (D5/D6) | **partly** — discriminator design is in-repo; the data is not |
| `P7` | a second lab/dataset reproducing a scoped result | **NO — external** |
| `P8` | `P0`–`P7` conjunctively satisfied | **NO** |

**`P4`, `P5`, `P7` cannot be closed by any modelling in this repository.** The next-gate plan
(`protocols/NEXT-GATE-TRANSFER-AND-INTERVENTION-PLAN.md`) specifies the external receipts.

---

`NEXT_ACT = write hierarchical-aif/protocols/NEXT-GATE-TRANSFER-AND-INTERVENTION-PLAN.md`
