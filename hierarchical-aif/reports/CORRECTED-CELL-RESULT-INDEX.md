# Corrected-Cell Result Index

**Date:** 2026-07-22 · **Gate:** H-AIF-G5 (all four landed) · One row per corrected B4 cell.
Every hash below is verified by `sha256sum -c` against its sidecar. **No P-level is raised by any
cell.**

---

## Index

| field | **B4C01** | **B4C02** | **B4C10** | **B4C11** |
|-|-|-|-|-|
| cell | `B4C01_SYNTHETIC_PARAMETER_RECOVERY` | `B4C02_MISSPECIFIED_WORLDS` | `B4C10_M4_STRUCTURAL_IDENTIFIABILITY` | `B4C11_M7_STRUCTURAL_IDENTIFIABILITY` |
| planned_N | 200/gen × 5 = 1000 sims | 200/gen × 3 = 600 sims | `N_boot` 2000 | `N_boot` 2000 |
| actual_N | 1000 sims (0 failed) | 600 sims (0 failed) | 2000 boot (1994 completed / 6 failed) | 2000 boot (2000 completed / 0 failed) |
| status | `ELIGIBLE_FOR_FROZEN_VERDICT` | `ELIGIBLE_FOR_FROZEN_VERDICT` | complete, `resourceBoundPartial:false` | `ELIGIBLE_FOR_FROZEN_VERDICT` |
| result_hash | `8256cb120376f46bf00b537d2ad665f9d50335e3eed3727a1299129195dfb65b` | `0633988dbfd690c0c0d12075dba4e0d8c25ddd178125064bd01fbdaf4629e398` | `959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde` | `564a5b0f4461c83fe2c8792a2304dc136799b0923d887a27a60572361a851b53` |
| report_path | `reports/B4C01-CORRECTED-FULL-REPORT.md` | `reports/B4C02-CORRECTED-FULL-REPORT.md` | `reports/B4C10-CORRECTED-FULL-REPORT.md` | `reports/B4C11-CORRECTED-FULL-REPORT.md` |
| prediction_commit | **`28ce738`** | **`b9b5670`** | **`b9b5670`** | **`897c8ab`** |
| prospectivity_status | **`SATISFIED`** — committed with the cell never having run at any N (cleanest in the batch) | **`SATISFIED`** — committed 3 h 17 min before the observation (mid-run-commit caveat recorded) | **`NOT_SATISFIED`** — prediction and result share commit `b9b5670`; strict ancestry structurally unattainable (D9) | **`SATISFIED`** — committed ~19.4 h before the observation |
| old_status | `NOT_RUN` (`RESOURCE_BOUND`, claimed 250–400 h) | `NOT_RUN` (`RESOURCE_BOUND`, claimed 150–250 h) | `RESOURCE_BOUND_PARTIAL` (100/2000, 5%) | submitted `U4_OK` on 30/2000 under a **defective** bootstrap — **WITHDRAWN** |
| corrected_status | **`NOT_ESTABLISHED`** — failing criterion `M0_EXPONENTIAL:self_win` (0.290); all four parameterised generators `withinTolerance` | **`GENERATOR-SPECIFIC`** — `gensWithM2overM3 = 1` of 3 | **`IDENTIFIED_ON_THIS_COHORT`** — U2/U3/U4 all `OK` at full N | **`U4_OK`** — `collapseFraction 0.0055` < 0.25; group counts 80/80 |
| prediction_outcome | frozen `PASS` **REFUTED**; my committed directional prediction hit the primary structural claim (6 of 9 sub-items) | frozen `GENERATOR-ROBUST_ADVERSE` **REFUTED** | frozen `UNIDENTIFIED_OR_WEAK` **REFUTED** (within C10 scope) | frozen `PROFILE_FLAT_OR_WEAK` **REFUTED**; my committed §7.3 directional prediction **HIT all 5 sub-commitments** |
| defect_impacted | **D3 CLOSED** (deterministic corrected run); D4 superseded (reason text); D2 measured 16.83 h | **D3 CLOSED**; D2 measured 8.17 h | D2 measured 2.3 h; D1/D3 do **not** apply (M4 pooled `train_y`, arithmetic seeds) | **D1 CLOSED_BY_CORRECTED_RERUN**; D2 measured 21.12 h |
| P-level mapping | `P0`/`P1` integrity; constrains interpretation of `P3`. **Cannot move `P6`.** Synthetic data — none `OBSERVED` | constrains interpretation of the adverse `P3` result (shape-artifact **weakened**). No mechanism | `P1`/`P6` scoped: M4 identifiability on one cohort. **Identifiability ≠ correctness ≠ mechanism** | **`P6` for C11 U4 re-established on the corrected run only.** No other scope; no level raised |
| allowed wording | "sanity floor not met", "power-limited / nesting-blind at this holdout size", "not established" | "generator-specific", "the adverse result is not generic heavy-tailed shape", "not established" | "supports M4 identifiability on this cohort under the frozen U2/U3/U4 criteria" | "U4 re-established on the corrected run only", "the withdrawn `U4_OK` remains withdrawn" |
| forbidden wording | any claim this tests the motor-stack AIF model or the mark process; "M3 is vindicated"; "M2 is the UNI model" | "mechanism demonstrated"; "M3 is vindicated"; any transfer of a synthetic result to the real cohort as observation | "M4 is the correct model"; "mixture mechanism confirmed"; transfer to M7/C11/parity | any diagnostic-*proves*-U4 phrasing; transfer of B4C10's M4 result to C11; any mechanism/parity claim |

## Cross-cutting facts

- **Every dataset in B4C01 and B4C02 is SYNTHETIC.** Nothing in those two cells may be labelled
  `OBSERVED`. B4C10 and B4C11 are identifiability checks on frozen fits, not new observations either.
- **Three of four cells are genuinely prospective** by commit graph (C01, C02, C11). **B4C10 cannot
  be** — prediction and result entered in one commit — and is pinned `NOT_SATISFIED` by D9, not
  relabelled.
- **No cell raised a P-level.** `P8` remains `FULL_PARITY = false`; first unsatisfied level `P4`.

---

`NEXT_ACT = update the defect closure ledger to its final freeze state, then write PHASE-HIERARCHICAL-AIF-CORRECTED-CLOSURE.md`
