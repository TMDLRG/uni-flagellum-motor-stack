# B4C11 — Corrected Full-N Prediction Record

**PROSPECTIVITY: `NOT_SATISFIED` TODAY, BUT STILL FIXABLE — AND THE WINDOW IS OPEN (D9).**
Written 2026-07-21 prior to the corrected B4C11 full-N run, and its exact bytes are pinned at
launch time by `B4C11_CORRECTED_FULL_ENV.txt`
(`predictionRecord=... sha256 5d0a1170b78a860ca971cb9227ab86d90d60665a3345d28dc1a56ce437526ea1`,
`started_utc=2026-07-22T01:40:03Z`). But this file is **UNTRACKED**, and an uncommitted prediction
cannot satisfy the commit-graph test.

**The B4C11 result does not exist yet** (run projected ≈14 h). **Committing this file before that
result lands would make B4C11 a genuinely prospective cell.** That requires the human principal,
since nothing in this programme is committed without authorization. It is the single
highest-value, time-limited action available in this batch.
**Gate:** H-AIF-G5 · **Cell:** `B4C11_M7_STRUCTURAL_IDENTIFIABILITY` · **Lane:** **B** (corrected B4 robustness)
**Defect routed:** `D1_C11_CLUSTER_COLLAPSE` (OPEN → this run is its repair attempt)

---

## 1. Purpose

Re-execute the C11 **U4 motor-cluster bootstrap** at the **frozen `N_boot = 2000`** with the D1
cluster-collapse defect corrected, so that the withdrawn `U4_OK` is either re-established on a
valid bootstrap or replaced by an honest `UNSTABLE_DISPERSION_U4_FIRES`.

The submitted C11 `U4_OK` is **withdrawn** and stays withdrawn regardless of what this run returns.
It came from **30 of 2000** replicates (`resourceBoundPartial_U4: true`) built with a bootstrap that
collapsed 80 motor draws into ~46 groups. Neither problem can be repaired retroactively.

Frozen recorded artifact under repair:
`audits/phase-b/b4-identifiability-robustness-result.v1.json`
sha256 `f361e4dcf5fb8e1bf1724844b0581ebd1392027bfb694220944f3d048f1807f3`,
cell `B4C11`, `U4_bootstrap = {completed: 30, failed: 0, collapseFraction_tau_lt_1e_3: 0,
tauHatSummary: {median: 0.2196403657219113, p025: 0.17658259553140288, p975: 0.27020046374673834},
verdict: "U4_OK"}`. **That artifact is not modified by this run and is not overwritten.**

## 2. Planned run

| field | value |
|-|-|
| `planned_N` (frozen `N_boot`) | **2000** |
| corrected runner | `hierarchical-aif/scripts/run_c11_corrected_full.py` |
| launcher | `hierarchical-aif/scripts/launch_B4C11_corrected_full.sh` |
| result path | `hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_RESULT.json` |
| cohort | `derived_eligible_1_to_8` (80 training motors, 19 holdout motors) |
| `seed_base` | **20260717** (frozen) |
| per-replicate seed | `seed_b = 20260717 + b`; `np.random.default_rng(seed_b)`; `idx = rng_b.integers(0, 80, size=80)` |
| protocol version | `PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1` |

Exact planned command:

```bash
bash hierarchical-aif/scripts/launch_B4C11_corrected_full.sh 2000
# equivalently:
python hierarchical-aif/scripts/run_c11_corrected_full.py 2000 \
  hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_RESULT.json
```

**D3 does not apply to C11.** The frozen C11 seeding is pure arithmetic (`seed_base + b`); there is
no `hash()` anywhere in the U4 path. The corrected harness reproduces that arithmetic seeding
byte-for-byte and does **not** substitute `seeding.stable_seed`.

## 3. The one and only deviation: corrected cluster-bootstrap semantics

The committed `cell_C11` assembles each replicate's events and rebuilds `b3.Cohort(f"C11_b{b}", …)`.
`Cohort` groups `train_by_motor` **by `motorId`**, so a motor drawn `K` times collapses into **one**
group holding `K` copies rather than `K` exchangeable groups. `m7_train_nll` iterates
`train_by_motor`, so a `K`-fold group contributes `L_m^K` and over-sharpens that motor's latent.

**Measured** (not asserted), `seed_base = 20260717`:

| b | draws | legacy groups | corrected groups |
|-|-|-|-|
| 0 | 80 | 46 | 80 |
| 1 | 80 | 53 | 80 |
| 2 | 80 | 52 | 80 |
| 3 | 80 | 59 | 80 |
| 4 | 80 | 56 | 80 |

Source: `hierarchical-aif/results/motor_stack_aif/C11-PAIRED-DIAGNOSTIC.json`
sha256 `fad54c32c1e0e6e7d75290f70926743b3b776e7fd088864f4285962ea362f630`.
At `b = 0` the largest legacy group inflates 70 → 153 events (42.5% cluster loss).

The correction is `motor_stack_aif.bootstrap.build_bootstrap_cohort`: it builds the cohort
**identically** to the legacy path (same split derivation, same bootstrap-resampled per-state
scales, same normalised `_y`, bit-identical flat `train_y`) and then rebuilds **only**
`train_by_motor` as one group per **draw**, with `bootstrap_group_origin` carrying the source
motorId as **metadata only**.

Nothing else changes: not the threshold, not the criterion, not `N_boot`, not `seed_base`, not the
26-start L-BFGS-B `_fit_m7_reduced` budget or tolerances, not the cohort, not the model.

## 4. Frozen criteria (unchanged — do not touch)

- `collapseFraction_tau_lt_1e_3 = #{tau_hat < 1e-3} / completed`
- `collapseFraction >= 0.25` → `UNSTABLE_DISPERSION_U4_FIRES`; otherwise `U4_OK`.
- Per replicate: `_fit_m7_reduced` = L-BFGS-B **only**, exactly 26 starts (5×5 product of
  `k = linspace(0.05, 5.0, 5)` × `tau = exp(linspace(log 1e-4, log 5.0, 5))`, plus the full-data
  optimum as the 26th), bounds `log k ∈ [log 0.05, log 5.0]`, `log tau ∈ [log 1e-4, log 5.0]`,
  `ftol 1e-12, gtol 1e-10, maxiter/maxfun 20000, maxls 100, finite_diff_rel_step 1e-6`,
  minimising `b3.m7_train_nll(k, tau, coh.train_by_motor)`.
- `k_full` / `tau_full` (the 26th start) come from frozen B3
  `fitted.M7_HIERARCHICAL_MOTOR.kTau` in `audits/phase-b/b3-model-competition-result.json`
  (sha256 `5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd`).
- **NO FLOOR.** A non-finite log density or a `None` fit increments `failed`. It is never replaced,
  clipped, or floored.

## 5. U1 / U2 / U3 — decision and written justification

| check | decision | justification |
|-|-|-|
| **U1** `TAU_INTERIOR` | `CARRIED_FORWARD_FROM_FROZEN_ARTIFACT` | Settled in B3 on the full unresampled cohort. No bootstrap involved. The corrected run copies the recorded string verbatim; it does not recompute. |
| **U3** `SUPPORTED_OVER_M1` | `CARRIED_FORWARD_FROM_FROZEN_ARTIFACT` | Settled in B3 (LRT on the full cohort). No bootstrap involved. Copied verbatim. |
| **U2** profile flatness | `CARRIED_FORWARD_FROM_FROZEN_ARTIFACT` | **See below.** |

**Why U2 is carried forward, not rerun.** U2 is a deterministic 61-point profile-likelihood scan
(`tau_grid = exp(linspace(log 1e-4, log 5.0, 61))`, flat-set offset `1.9207 = 0.5·chi2_{1,0.95}`,
`logspan_normalized >= 0.50` → `UNIDENTIFIED_U2_FIRES`) computed on the **full, unresampled**
`derived_eligible_1_to_8` cohort. It never calls the bootstrap, never constructs a resampled
cohort, and never touches `train_by_motor` grouping other than the frozen 1:1 motor grouping.
**D1 is a bootstrap-resampling defect and therefore cannot reach U2.** Recomputing it could only
reproduce the same numbers at real cost, and a recompute-then-relabel would be an untraceable
duplicate of frozen evidence.

The corrected harness therefore **copies the `U2_profile` object byte-for-byte out of the frozen
artifact at run time** (via `_bridge.b4_result()["cells"]["B4C11"]["U2_profile"]`), records the
source path and its sha256, and labels it
`"provenance": "CARRIED_FORWARD_FROM_FROZEN_ARTIFACT"`. It is **not** recomputed and **not**
relabelled as new evidence. Recorded values being carried forward:
`verdict = "U2_OK"`, `flatLogspan_normalized = 0.06666666666666665`,
`flatSetTauRange = [0.11332624602040679, 0.2331283928719889]`, `nllStar = 575.7067684471608`.

Consequence, stated plainly: the corrected run's `M7_status` is a **composite** of one newly
computed check (U4) and three carried-forward checks (U1/U2/U3). It is not a fresh full
identifiability assessment and must never be reported as one.

## 6. Pre-committed outcome branches

| # | observed at N = 2000 | verdict | pre-committed consequence |
|-|-|-|-|
| **(a)** | `collapseFraction_tau_lt_1e_3 < 0.25` | `U4_OK` | U4 is re-established for C11 **on the corrected run only, at frozen N**. It does **not** retroactively validate the withdrawn 30-replicate artifact, which stays withdrawn and stays visible. `D1` moves OPEN → CLOSED-BY-RERUN for the C11 U4 lane only. The frozen B4 prediction `PROFILE_FLAT_OR_WEAK` is **REFUTED at full N** for the U4 arm; the earlier `REFUTED_U4_PARTIAL` label is superseded, not upgraded. |
| **(b)** | `collapseFraction_tau_lt_1e_3 >= 0.25` | `UNSTABLE_DISPERSION_U4_FIRES` | M7's dispersion parameter is **unstable** on this cohort under a valid motor-cluster bootstrap, and the original `U4_OK` was an **artifact of the cluster collapse**. `M7_status` becomes `UNIDENTIFIED_OR_UNSTABLE (U4)`. The frozen B4 prediction `PROFILE_FLAT_OR_WEAK` is **CONFIRMED at full N**. **This is the scientifically more informative branch** — it converts a defect report into a measured, quantified correction of a published verdict, and it is a second demonstration (after D2) that a partial/defective run produced a misleading reading. It is the branch this record most wants to be able to report. |
| **(c)** | run incomplete (`actual_N_boot < 2000`), `completed == 0`, or `completed` too low to bound the fraction | `PARTIAL_NOT_ESTABLISHED` / `NO_SUCCESSFUL_BOOTSTRAP` | **No verdict.** `status.classify_run` returns `PARTIAL_NOT_ESTABLISHED` or `NOT_RUN`. To reach a verdict this branch needs: the full 2000 replicates completed on the corrected builder, `failed` reported, and no post-hoc stopping. Underpowered is **not** equivalence; a partial run may never be read as `U4_OK`. |

**Falsifier of branch (a):** any corrected full-N run with `collapseFraction >= 0.25`.
**Falsifier of branch (b):** any corrected full-N run with `collapseFraction < 0.25`.
There is no outcome under which the withdrawn artifact is restored.

## 7. Directional prediction I am willing to be wrong about — with its mechanism

### 7.1 The mechanism argument (direction)

The defective builder concatenates a motor drawn `K` times into a single group whose likelihood is
`L_m^K`. That over-sharpens each duplicated motor's latent `eta_m`, pushing the per-motor posterior
mass toward its own mode and **inflating the apparent between-motor spread** that `tau` must
explain. Removing the collapse should therefore **reduce** fitted `tau`, and lower `tau` is closer
to the collapse boundary. **Mechanistically, the correction should make tau-collapse MORE likely,
not less.**

### 7.2 The measured evidence (magnitude)

Paired diagnostic, identical draws in both arms, N = 5
(`C11-PAIRED-DIAGNOSTIC.json`, sha256 `fad54c32…`):

| b | legacy tau | corrected tau | delta |
|-|-|-|-|
| 0 | 0.19906013275874299 | 0.1186009353493865 | −0.0805 |
| 1 | 0.23470934095126772 | 0.20020183204985909 | −0.0345 |
| 2 | 0.21282561461868615 | 0.15626676308339552 | −0.0566 |
| 3 | 0.19144852455063333 | 0.15874692004144833 | −0.0327 |
| 4 | 0.18485220647323228 | 0.1331883135999573 | −0.0517 |

Corrected tau is **lower in 5 of 5 paired replicates** (medians 0.19906 → 0.15627). The mechanism's
**direction is confirmed** by measurement. But the **magnitude** is ~0.03–0.08 in tau, while the
collapse threshold is `1e-3`. The smallest corrected tau observed is 0.1186 — roughly **119×** the
collapse threshold. A shift of that size does not come close to producing a collapse.

### 7.3 What I commit to

1. **Direction (committed, high confidence):** the corrected `tauHatSummary.median` at N = 2000
   will be **strictly less than the frozen recorded 0.2196403657219113**. I expect it in
   **[0.12, 0.20]**.
2. **Collapse fraction (committed, this is the risky one):** `collapseFraction_tau_lt_1e_3` will be
   **< 0.05**, and most likely exactly **0.000**. I commit to a pre-registered interval of
   **[0.000, 0.02]**. → I am predicting **branch (a)**.
3. **Corrected `p025` of tau** will remain **> 1e-2**, i.e. two orders of magnitude above the
   collapse boundary.
4. **Paired legacy-vs-corrected block:** corrected tau will be lower than legacy tau in
   **> 80%** of the paired subset, and corrected group count will be exactly 80 in **100%**.

### 7.4 How I could be wrong, and what that would mean

Five replicates cannot bound a rare-event fraction. A collapse fraction of 0.25 requires a heavy
**left tail** of the corrected tau distribution that N = 5 has no power to detect; 0/5 above a 119×
margin is suggestive, not conclusive. If prediction 2 fails and branch (b) fires, the honest reading
is that the corrected bootstrap exposes a bimodal tau landscape — a subpopulation of resamples in
which the 26-start optimiser finds the degenerate `tau → 0` corner — that the diagnostic's five
draws never sampled. **That outcome is recorded as an outcome, not as a failure**, and it is the
more informative branch per §6.

I am predicting against the mechanism's own direction of concern. I am doing so on measured
magnitude, and I am naming that tension rather than hiding it.

## 8. Old-vs-new comparison plan — the D1 effect size must be MEASURED, not asserted

The corrected run additionally executes a **paired subset** (default 25 replicates, seeds
`b = 0 … 24` — the same seeds, the same draws) through
`bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE`, and records both arms side by side under

```json
"legacyVsCorrectedPaired": {
  "label": "LEGACY_DEFECTIVE_FOR_COMPARISON_ONLY",
  "disclaimer": "The legacy arm reproduces defect D1. It is a defect-magnitude measurement. It is NOT evidence, NOT a result, and licenses NO verdict."
}
```

Recorded per paired replicate: `legacyGroups`, `correctedGroups`, `nDistinctDrawn`, `legacyTau`,
`correctedTau`, `legacyK`, `correctedK`, `deltaTau = correctedTau - legacyTau`; plus medians, the
sign count, and the fraction of paired replicates in which corrected < legacy.

**No verdict may ever be drawn from the legacy arm.** It exists only so the D1 effect size is a
measured number in the record.

## 9. Lane scoping — explicit

**Affected: LANE B, C11 U4 only.**

- The withdrawn `U4_OK` for `B4C11_M7_STRUCTURAL_IDENTIFIABILITY`.
- `M7_status` for the `derived_eligible_1_to_8` cohort, insofar as it depends on U4.
- Defect `D1_C11_CLUSTER_COLLAPSE`.

**Unaffected, and stated as unaffected:**

- **LANE A** — duration-only B3/B4 held-out scoring. Unchanged. The M2-over-M3 adverse result
  (~0.0369 nats event-pooled) is unchanged and is reported alongside whatever this run returns.
- **B4C10** (`B4C10_CORRECTED_FULL_RESULT.json`, sha256
  `959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde`). M4 fits the flat pooled
  `coh.train_y`, which the correction leaves bit-identical
  (`test_m4_pooled_path_is_unchanged_by_the_fix`). Unaffected **unless** a C11 result actively
  contradicts it, which it structurally cannot.
- **C11 U1, U2, U3** — settled in B3 without any bootstrap. Unaffected by D1 and unaffected by this
  run (see §5).
- **LANE C** (mark process) — untouched. This run is duration-only and never reads a mark channel.
- **LANE D** (motor-stack AIF) — untouched. M7 is a frozen B3 competitor, not the F-side model.
- **LANE E** (parity ladder) — no P-level moves on this run alone.

**C10's favourable result may NOT be transferred to C11.** They are different models (M4 mixture vs
M7 hierarchical) with different likelihood structures (pooled i.i.d. vs motor-grouped). A favourable
C10 says nothing whatsoever about M7 identifiability or about the withdrawn C11 `U4_OK`.

## 10. Required pre-run checks — each with the test that proves it

| # | check | proving test / command |
|-|-|-|
| 1 | corrected bootstrap preserves the draw count: 80 draws → 80 groups | `test_c11_bootstrap_preserves_exchangeable_motor_draws.py::test_corrected_bootstrap_preserves_draw_count` and `::test_corrected_bootstrap_group_count_is_stable_across_replicates` |
| 2 | duplicate sampled motorIds remain SEPARATE groups (not one `K`-fold group) | `test_bootstrap_duplicate_motors_remain_distinct_groups.py::test_duplicated_motor_yields_k_separate_groups`, `::test_duplicated_motor_is_not_concatenated_into_one_group` |
| 3 | original motorId is metadata only (`bootstrap_group_origin`), never a grouping key | `test_bootstrap_duplicate_motors_remain_distinct_groups.py::test_group_origin_metadata_is_preserved` |
| 4 | train/holdout split unchanged (still `sha256_mod5(motorId) == 0` → holdout) | `bootstrap._assemble` re-derives `partition` from `b3.sha256_mod5` and `b3.Cohort` HALTS on mismatch; `test_c11_bootstrap_preserves_exchangeable_motor_draws.py::test_frozen_cohort_has_80_training_motors` |
| 5 | per-state scales unchanged relative to the legacy builder | `test_bootstrap_duplicate_motors_remain_distinct_groups.py::test_m4_pooled_path_is_unchanged_by_the_fix` (`train_y` is `durationS / scale_N[stateN]`; identical sorted `train_y` ⇒ identical scales) |
| 6 | flat `train_y` bit-identical to legacy | `::test_m4_pooled_path_is_unchanged_by_the_fix`, `::test_total_event_mass_is_conserved_by_the_fix` |
| 7 | arithmetic seeding in use, matching the frozen C11 exactly | in-harness `seedEquivalenceCheck`: `bootstrap.draw_motors(train_motors, default_rng(20260717+b))` is asserted equal to the frozen inline `rng.integers(0, n_tm, size=n_tm)` indexing for `b = 0,1,2`; the harness aborts if it differs |
| 8 | the OLD frozen artifact is untouched | `git status --short audits/` empty; `hierarchical-aif/reports/frozen-evidence-baseline.sha256` recheck; the launcher writes only under `hierarchical-aif/results/motor_stack_aif/` |
| 9 | the canonical result is never silently overwritten | `launch_B4C11_corrected_full.sh` exits non-zero if `B4C11_CORRECTED_FULL_RESULT.json` already exists |

Command that must be green before launch:

```bash
python -m pytest hierarchical-aif/tests/motor_stack_aif -q
# baseline at HEAD b9b5670: 71 passed, 1 xfailed
```

## 11. Expected runtime — an operational estimate, not a measurement

**The recorded figure is ≈20.1 h.** Its basis: `hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md`
line 50, D2 evidence row — a measured **36.2 s** for a single `_fit_m7_reduced`, projected as
`2000 × 36.2 s = 72 400 s ≈ 20.1 h`. **That is a projection from a single-fit measurement, not a
measurement of the run.**

D2's lesson is precisely that unmeasured cost estimates were wrong by **17–29×** (C01 recorded
250–400 h vs ≈14.5 h measured; C02 recorded 150–250 h vs ≈8.7 h measured), and those bad estimates
caused real cells to be recorded `NOT_RUN` and `resourceBoundPartial`. So this record does not rely
on the projection.

**Independent measurement already in hand:** the paired diagnostic ran 5 replicates × 2 arms =
**10 `_fit_m7_reduced` fits in 307.5444803237915 s** ⇒ **30.75 s per fit**
(`C11-PAIRED-DIAGNOSTIC.json`). Projection from that: `2000 × 30.75 s = 61 509 s ≈ 17.1 h`.

**Smoke-test measurement (recorded before the full run — see §11.1).** A `N_BOOT = 3` smoke run of
the corrected harness to a throwaway path measured the real per-replicate cost of *this* harness,
including cohort assembly and the paired legacy arm. The projection below is re-derived from that
measurement and supersedes both figures above.

### 11.1 MEASURED — smoke test of `run_c11_corrected_full.py`

Two smoke runs of the corrected harness, `N_BOOT = 3`, to **throwaway scratch paths** (never to the
canonical result path). Both completed 3/3 with `failed = 0`.

| run | command (result path abbreviated to `<scratch>`) | fits performed | `totalRuntimeS` (measured) |
|-|-|-|-|
| A | `python hierarchical-aif/scripts/run_c11_corrected_full.py 3 <scratch>/B4C11_SMOKE_THROWAWAY_RESULT.json --paired 2` | 3 corrected + 2 legacy | **130.4045786857605** |
| B | `python hierarchical-aif/scripts/run_c11_corrected_full.py 3 <scratch>/B4C11_SMOKE_CORRARM_RESULT.json --paired 0` | 3 corrected | **94.99591636657715** |

**Per-arm cost, derived from A and B:**

```
corrected arm : 94.99591636657715 / 3           = 31.6653 s per replicate
legacy arm    : (130.4045786857605 - 94.99592) / 2 = 17.7043 s per fit
```

The legacy arm is *cheaper* per fit, as expected: it iterates ~46–53 collapsed groups instead of 80,
so `m7_train_nll` does less work. That asymmetry is itself a signature of D1.

**Re-derived full-run projection (this is the operative estimate):**

```
corrected arm : 2000 × 31.6653 s = 63 330.6 s = 17.59 h
paired legacy :   25 × 17.7043 s =    442.6 s =  0.12 h
projected total ≈ 63 773 s ≈ 17.7 h   (single process, 1 core, no parallelism)
```

The recorded **20.1 h** is a **1.13×** overestimate of this projection — the same direction as D2,
but nowhere near D2's 17–29× magnitude. The 20.1 h figure was, for this cell, roughly right.

The projection assumes per-replicate cost is stationary across seeds. A resample whose 26-start
optimiser wanders costs more, and the smoke measured only 3 seeds (`b = 0,1,2`), so treat **17.7 h**
as a central estimate with a plausible band of roughly **14–24 h**, **not a bound**.

**Additional smoke observations (all measured, all pre-run):**

- `seedEquivalenceCheck = IDENTICAL_TO_FROZEN_INLINE_DRAW_SEQUENCE` for `b = 0,1,2`.
- Corrected `groupCountMin = groupCountMax = 80` — one group per draw, every replicate.
- `nDistinctDrawn` ranged 46–53, so duplicates were genuinely present and genuinely un-collapsed.
- Corrected `tauHats = [0.1186009353493865, 0.20020183204985909, 0.15626676308339552]` — **bit-identical
  across runs A and B, and bit-identical to the pre-existing paired diagnostic**. Determinism holds.
- Paired arm at `b = 0,1`: legacy groups 46, 53 vs corrected 80, 80; legacy tau
  0.19906013275874299, 0.23470934095126772 vs corrected 0.1186009353493865, 0.20020183204985909;
  `fracCorrectedBelowLegacy = 1.0`.
- `verdict = PARTIAL_NOT_ESTABLISHED`, `runStatus = PARTIAL_NOT_ESTABLISHED`,
  `predictionOutcome = NOT_ESTABLISHED` at `N = 3`. **The harness correctly refuses to emit a U4
  verdict from a partial run.** The smoke `collapseFraction = 0.0` is a partial-run number and
  licenses nothing.

Checkpointing every 25 replicates to `B4C11_CORRECTED_FULL_PROGRESS.json` (verified written by the
smoke run, self-labelled `PARTIAL_PROGRESS_CHECKPOINT_NOT_A_RESULT`) bounds worst-case crash loss to
≈13 minutes of compute.

Runtime is an *operational* number: filling this section in before launch changed no criterion,
threshold, `N`, seed, model, or outcome branch. §4, §6, and §7 are untouched.

Checkpointing every 25 replicates to `B4C11_CORRECTED_FULL_PROGRESS.json` bounds worst-case loss to
~11 minutes of compute. **Checkpoints are progress, never results** — the file self-labels
`PARTIAL_PROGRESS_CHECKPOINT_NOT_A_RESULT`.

## 12. What this cell cannot do, whatever it returns

- It cannot establish biological parity, mechanism, or active inference.
- It cannot promote M7 to "the correct model". U4 is an **identifiability/stability** check on one
  parameter of one frozen competitor on one cohort — not a predictive claim and not a mechanism.
- It cannot move `P6` structural/mechanistic on its own.
- It cannot repair, restore, or re-credit the withdrawn 30-replicate artifact.
- It cannot transfer to C10, to M4, to the mark process, or to the F-side motor-stack AIF model.
- The adverse B3 result (M2_LOGNORMAL out-predicting M3 by ≈0.0369 nats event-pooled; narrowest
  motor-equal contrast M4_MIXTURE_K3 at 0.083461 against a resolution floor of ≈0.042 nats
  half-width) is **retained and reported alongside** this result, never instead of it. M2 is an
  **adversarial baseline**, never the UNI model.

## 13. Wording

**Allowed:**
"The corrected full run of B4C11 at frozen `N_boot = 2000` supports / does not support M7 `tau`
stability (U4) on the `derived_eligible_1_to_8` cohort under the frozen `collapseFraction >= 0.25`
criterion." · "candidate model" · "target hypothesis" · "CI-bound verdict" · "not established" ·
"retrospective-only" · "transfer required" · "intervention required" ·
"mechanism discriminator pending" · "corrected full run" ·
"U4 re-established on the corrected run only" ·
"the withdrawn `U4_OK` remains withdrawn".

**Forbidden (mechanically checked by `claim_guard.py`).** The canonical forbidden-wording list is
maintained in `claim_guard.FORBIDDEN` and in the H-AIF operating contract; it is referenced here
rather than re-transcribed. Re-transcribing it across wrapped lines defeats the guard's own
use/mention rule — the guard only accepts a negation or catalogue cue on the *same line* as the
phrase, so a catalogue that soft-wraps reads as a bare assertion on every line after the first.
This section previously carried such a wrapped catalogue and the guard correctly flagged 8
violations in it; the fix is to reference the list, not to loosen the guard.

Forbidden in this document specifically: any claim that the corrected run restores the withdrawn
artifact; any transfer of B4C10's favourable M4 result to M7; any statement that U4 is settled
before the run completes; and any unscoped sentence of the form "U4 is fine" or "U4 is broken".
Every U4 statement names the run it came from and the `N` it ran at.

## 14. NEXT_ACT

`launch_B4C11_corrected_full.sh 2000` — launched by the orchestrator, not by the preparing agent.
On completion: record sha256, update
`hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md` D1 routing, append a FLOW card,
and run `claim_guard.py` over the report batch.
