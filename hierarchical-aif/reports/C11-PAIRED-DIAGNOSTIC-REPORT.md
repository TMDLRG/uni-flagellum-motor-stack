# C11 Paired Diagnostic — does D1 materially move τ?

**Gate:** H-AIF-G4 (fix validation) · **Run:** 2026-07-21 · **Runtime:** 308 s
**Artifact:** `hierarchical-aif/results/motor_stack_aif/C11-PAIRED-DIAGNOSTIC.json`
**Script:** `hierarchical-aif/scripts/c11_paired_diagnostic.py`

> **THIS IS A DIAGNOSTIC AT N=5. IT IS NOT THE CORRECTED C11 RESULT AND IT LICENSES NO VERDICT.**
> The corrected C11 U4 result requires the full frozen N=2000 run (H-AIF-G5, ≈20.1 h).

## Design

Five bootstrap replicates at the declared `seed_base = 20260717`. Both arms consume **identical
motor draws** — the RNG is constructed once per replicate and the same `sampled` list is fed to
both builders, so the arms differ *only* in cluster-grouping semantics. Paired by construction.

## Result

| replicate | legacy τ | corrected τ | Δ | groups (legacy/corrected) |
|-|-|-|-|-|
| b=0 | 0.19906 | 0.11860 | **−0.08046** | 46 / 80 |
| b=1 | 0.23471 | 0.20020 | **−0.03451** | 53 / 80 |
| b=2 | 0.21283 | 0.15627 | **−0.05656** | 52 / 80 |
| b=3 | 0.19145 | 0.15875 | **−0.03270** | 59 / 80 |
| b=4 | 0.18485 | 0.13319 | **−0.05166** | 56 / 80 |

- **Corrected τ is lower in 5 of 5 paired replicates.** Exact two-sided sign test **p = 0.0625** —
  the most extreme result obtainable at N=5, and **not** below 0.05. Suggestive, not significant.
- **Spread widens 1.64×**: legacy 0.04986 → corrected 0.08160.
- **Collapse fraction (τ < 1e-3) is 0 in both arms**, so the `U4` collapse criterion itself is not
  what D1 disturbs — the *interval* is.
- **4 of 5 corrected τ values fall below the recorded U4 CI lower bound** of 0.17658
  (0.1186, 0.1563, 0.1587, 0.1332). The recorded interval `[0.17658, 0.27020]` appears both
  shifted high and too narrow.

## Interpretation

The direction was **predicted from the mechanism before the run**: collapsing K draws of a motor
into one group raises that motor's contribution to `L_m^K`, over-sharpening its latent and
reducing the effective number of exchangeable clusters (80 → 46–59 here). Over-sharpening should
produce τ estimates that are **higher and less variable** than a correct cluster bootstrap. That
is exactly what the legacy arm shows relative to the corrected arm.

So D1 is not a cosmetic bookkeeping error. It **materially moves the reported quantity, in the
direction that favoured the conclusion that was reported** ("τ is well determined"). This is
confirmatory evidence for the D1 entry in the defect ledger and for withdrawing `U4_OK`.

## What this does NOT establish

- It does **not** establish the corrected τ interval. N=5 is far below the frozen N=2000.
- It does **not** establish that the corrected C11 U4 verdict will be `UNIDENTIFIED`. The
  corrected spread is wider, but whether it crosses the frozen U4 criterion is unknown until the
  full run.
- p = 0.0625 does **not** clear a conventional significance threshold. Five paired replicates
  cannot, even in the best case.
- The τ values here come from `_fit_m7_reduced` (reduced optimizer budget), matching the
  committed C11 U4 path — not from a full-budget M7 fit.

## Consequence for scheduling

This raises the priority of the corrected C11 full-N rerun: the affected quantity demonstrably
moves, so the withdrawn `U4_OK` cannot be restored by assertion — only by the ≈20.1 h corrected
run at frozen N=2000.
