# B4C10 — Corrected Full-N Result Report

**Gate:** H-AIF-G5 · **Cell:** `B4C10_M4_STRUCTURAL_IDENTIFIABILITY` · **Date:** 2026-07-21
**Branch:** `hierarchical-aif/motor-stack`
**Maps to existing ladder:** `P1` equation/implementation, `P0` provenance; a **scoped**
identifiability statement that touches the `P6` discussion **without raising any P-level**
**Prediction record (WRITTEN before execution; NOT committed before execution — it entered the
repo in the SAME commit as the result, so prospectivity is `NOT_SATISFIED` and structurally
unattainable, see §6):**
`hierarchical-aif/protocols/B4C10-CORRECTED-FULL-PREDICTION.md`
**Lane:** LANE B (corrected B4 robustness cells)

**No frozen artifact was modified.** The runner is the committed, byte-identical
`audits/phase-b/b4-identifiability-robustness-runner.py`. The only difference from the recorded
run is the replicate count, moved from 100 to the frozen 2000.

---

## 1. Executive result

B4C10 ran to completion at the **full frozen `N_boot = 2000`**: 1994 replicates completed, 6
failed, `resourceBoundPartial: false`. All three frozen identifiability checks returned OK —
`U2_bootstrapCollapseFrac = 0.0050150451354062184` (fires at ≥ 0.25), `U3` `log10(lambda_3)` 95%
interval span `= 0.43327087478677417` decades (fires at ≥ 2.0), and `U4` `omega_3` 95% percentile
interval `= [0.030746372918754247, 0.28838105457744573]` (fires only if it straddles, i.e. `lo <
5/793` **and** `hi > 0.25`; the lower bound does not, so U4 does not fire). The runner therefore
recorded `M4_status = "IDENTIFIED_ON_THIS_COHORT (U1 DISTINCT from B3, U2/U3/U4 OK)"`, and the
reduced-budget calibration shortfall was `8.7993612396530807e-11` nats against a 0.05-nat
threshold (`WITHIN_0.05_NATS`). By the mapping committed in §5 of the prediction record, the frozen
prediction `UNIDENTIFIED_OR_WEAK` is **REFUTED AT FULL N, within B4C10 scope only**: B4C10 at full
frozen N=2000 supports M4 identifiability on the `derived_eligible_1_to_8` cohort under the frozen
U2/U3/U4 criteria. This is an identifiability statement about one model on one cohort. It is not
evidence for any mechanism, it does not make M4 correct, and it may not be transferred to M7, to
C11, or to any parity claim.

## 2. Provenance

| field | value | source |
|-|-|-|
| command | `python audits/phase-b/b4-identifiability-robustness-runner.py --cells C10 --c10-boot 2000 --out hierarchical-aif/results/motor_stack_aif/B4C10_CORRECTED_FULL_RESULT.json` | `…/B4C10_CORRECTED_FULL_COMMAND.txt` |
| runner | `audits/phase-b/b4-identifiability-robustness-runner.py` | frozen path |
| runner sha256 | `3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7` | recomputed this session with `sha256sum`; matches the `3e21edac97a2b68f…` prefix recorded in the ENV file and in the prediction record §2 |
| runner status | **FROZEN, BYTE-IDENTICAL, UNMODIFIED** — `correctionApplied = NONE` | ENV file; see §8 for why no correction was needed |
| only change from the recorded run | replicate count `100 -> 2000` (the frozen N) | ENV file |
| python | 3.12.10 | ENV file **and** `environment` block inside the result JSON |
| numpy | 2.3.5 | ENV file and result JSON |
| scipy | 1.16.3 | ENV file and result JSON |
| HEAD at run start | `17a2f0e18c09c762ab1cefe854c0d68698803eac` | ENV file |
| HEAD at report time | `b9b5670602a2afde158b53ea5e8135180f8c02f5` | `git log -1 --format=%H` |
| start | `2026-07-21T17:51:13Z` | ENV file (`started_utc`) |
| end | **NOT_RECORDED.** Derived as `≈2026-07-21T20:11:51Z` (start + 8437.9 s total) — DERIVED, not an artifact field | — |
| C10 cell runtime | **8372.7 s** = 2.3258 h | STDOUT log |
| total process runtime | 8437.9 s = 2.3439 h (explicitly "not recorded in canonical result") | STDOUT log |
| stderr | 0 bytes | `…_STDERR.log` |
| result sha256 | `959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde` | **recomputed this session with `sha256sum`; MATCHES** the value in `B4C10_CORRECTED_FULL.sha256` and the value the runner printed to stdout. **No mismatch.** |
| result size | 1426 bytes | stdout; matches on-disk size |
| consumed B3 result sha256 | `5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd` | result JSON |
| protocol | `PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1` | result JSON |
| schema | `uni.flagellum.b4-identifiability-robustness-result/1.0.0` | result JSON |
| seed base | `20260717`; per-replicate seed `seed_base + b`, `b = 0..1999` | result JSON; runner line 1063 |

Three independent hash witnesses agree (stdout at write time, the `.sha256` sidecar, and a fresh
`sha256sum` at report time). The result file has not drifted since it was written.

## 3. Planned vs actual N, and the 6 failures

| quantity | value |
|-|-|
| `frozen_N_boot` | 2000 |
| `actual_N_boot` (attempted) | 2000 |
| `completed` | 1994 |
| `failed` | **6** (0.30% of attempted) |
| `resourceBoundPartial` | `false` |

The run is a full-N run: every one of the 2000 frozen replicates was attempted. Six did not yield
a usable fit.

**Does the JSON record a reason for the 6 failures? NO — `NOT_RECORDED.`** The result object
carries only the integer `failed: 6`. Reading the frozen runner (`cell_C10`, lines 1060–1092)
shows exactly two code paths that increment it, and the runner distinguishes neither in the output:

1. `b3.Cohort(f"C10_b{b}", …)` raises while rebuilding the resampled cohort (line 1076–1079); or
2. `_fit_m4_reduced` returns `None` (lines 1081–1084), which happens when the differential-evolution
   objective is non-finite or `>= 1e11` (line 1015), or when the canonicalised mixture violates the
   mean-one constraint by more than `1e-8` (line 1018).

**What would be needed to attribute them.** The frozen runner may not be edited, so attribution
requires an out-of-tree replay under `hierarchical-aif/`: re-run the deterministic per-replicate
seed sequence `20260717 + b` for `b = 0..1999`, reconstruct each bootstrap cohort by the same
recipe, and record which of the three exit conditions fired for each failing `b`. The seeds are
arithmetic and the pipeline is deterministic, so this replay is exactly reproducible; it costs
another full-N pass (≈2.3 h). It has **not** been done. Until it is, the failure cause is
`NOT_ESTABLISHED`.

**Why this is not waved away.** Failure path 2 is *not* neutral: a non-finite objective or a
mean-one violation is the kind of numerical outcome that a near-degenerate mixture can produce.
Dropping such replicates is potentially informative (non-random) missingness, and it biases the U2
collapse fraction **downward**. That is a real, named risk, not a rounding detail.

**Bounded sensitivity, computed rather than asserted.** The recorded collapse fraction implies a
collapsed count of `0.0050150451354062184 × 1994 = 10.0` exactly, i.e. **10 collapsed of 1994
completed**. Under the adversarial worst case that *all 6 failures were collapses*, the fraction
over all 2000 attempted replicates would be `(10 + 6) / 2000 = 0.008`, versus the U2 firing
threshold of 0.25 — a factor of **31.25** below it. Under the benign case it is `10 / 2000 = 0.005`.
**The U2 verdict is therefore insensitive to the attribution of the 6 failures.** No comparable
bound is available for U3 and U4, because the failed replicates contribute no `log10(lambda_3)` or
`omega_3` value at all and their quantile influence cannot be bounded without knowing what those
values would have been — that remains **NOT_COMPUTED**.

## 4. Criteria and results

Criteria and thresholds are read from the frozen runner (`cell_C10`, lines 1094–1114); they were
not chosen or restated for this report.

| check | frozen criterion | fires when | observed | margin | verdict |
|-|-|-|-|-|-|
| **U1** | component distinctness, already settled in B3 | — | `"DISTINCT (per B3 result)"` | — | carried over from B3, **not re-derived here** |
| **U2** | bootstrap collapse fraction of degenerate M4 fits (`collapseLabel != "DISTINCT"`), over `completed` | `frac >= 0.25` | **0.0050150451354062184** (10 of 1994) | 49.85× below threshold | **`U2_OK`** |
| **U3** | span of the `log10(lambda_3)` 95% percentile interval, in decades (`q0.975 - q0.025`) | `span >= 2.0` | **0.43327087478677417 decades** | 4.62× below threshold | **`U3_OK`** |
| **U4** | `omega_3` 95% percentile interval straddles the degeneracy window: `lo < 5/793` **AND** `hi > 0.25` (an AND, per the frozen spec comment at lines 1099–1102) | straddle `== True` | **`[0.030746372918754247, 0.28838105457744573]`** | see below | **`U4_OK`** |

**U4 read precisely.** `5/793 = 0.006305170239596469` (five events' worth of weight out of the 793
training events). The observed lower bound `0.030746…` is **4.88× above** that point, so
`lo < 5/793` is **False**. The observed upper bound `0.288381…` **is** above 0.25, so `hi > 0.25`
is **True**. Because the criterion is a conjunction, `U4_OK` here is carried **entirely by the
lower bound**; the upper half of the straddle condition is satisfied. Anyone reading `U4_OK` as
"the interval is comfortably away from both degeneracy edges" would be reading it wrong.

**Reduced-budget calibration** (the check that the reduced DE budget — `maxiter=400, popsize=30` —
does not under-fit relative to B3's full M4 fit):

| field | value |
|-|-|
| `fullTrainNLL` (B3 published M4 fit) | 517.66154037090291 |
| `reducedTrainNLL` (this run, full training set, seed 20260717) | 517.66154037099091 |
| `shortfall` | **8.7993612396530807e-11 nats** |
| `shortfallThreshold_nats` | 0.05 |
| verdict | **`WITHIN_0.05_NATS`** |

These calibration numbers are **bit-for-bit identical to the recorded 100-replicate run** (see §5),
which is expected: the calibration fit uses `seed_base` on the unresampled cohort and does not
depend on `n_boot`. It is a reproducibility witness, not new independent evidence.

*Units note:* the calibration NLLs are training negative log-likelihoods produced by the B3/B4
pipeline on its own scale, and the shortfall is a difference of two such quantities, so it is in
nats regardless. The collapse fraction is dimensionless; the U3 span is in decades of `log10` rate;
`omega_3` is a mixture weight (dimensionless, in [0,1]). None of these is an NLPD, so the
seconds-vs-normalised-`y` Jacobian question that governs B3 NLPD comparisons does not arise here.

## 5. Old (100/2000 partial) vs new (2000/2000 full)

Old column from `audits/phase-b/b4-identifiability-robustness-result.v1.json`, cell `B4C10`
(frozen, read-only). New column from `B4C10_CORRECTED_FULL_RESULT.json`.

| field | old: 100/2000 partial | new: 2000/2000 full | change |
|-|-|-|-|
| `actual_N_boot` | 100 | **2000** | full frozen N |
| `completed` / `failed` | 100 / 0 | **1994 / 6** | 6 failures appear only at full N |
| `resourceBoundPartial` | `true` | **`false`** | partial status retired |
| `verdictScope` | `"Partial replicate count… Recorded as RESOURCE_BOUND_PARTIAL."` | **field absent** (runner emits it only when partial) | — |
| `U2_bootstrapCollapseFrac` | 0 | **0.0050150451354062184** | 0 → 0.005015 |
| `U2_verdict` | `U2_OK` | `U2_OK` | unchanged |
| `U3` span (decades) | 0.4082097415726904 | **0.43327087478677417** | **+0.0250611** (+6.1%) |
| `U3_verdict` | `U3_OK` | `U3_OK` | unchanged |
| `U4` `omega_3` 95% CI | [0.0381335112536136, 0.31658793968579624] | **[0.030746372918754247, 0.28838105457744573]** | lo −0.0073871, hi −0.0282069 |
| `U4` CI width | 0.27845442843218265 | **0.25763468165869147** | −0.0208197 (narrower) |
| `U4_verdict` | `U4_OK` | `U4_OK` | unchanged |
| `M4_status` | `IDENTIFIED_ON_THIS_COHORT (…)` | same string | unchanged |
| `reducedBudgetCalibration.shortfall` | 8.799361239653081e-11 | 8.7993612396530807e-11 | identical (see §4) |
| `seed_base` | 20260717 | 20260717 | unchanged |

**The collapse fraction is the instructive one, and it is the D2 lesson in miniature.** The partial
run observed **0 collapses in 100** replicates and recorded `U2_bootstrapCollapseFrac = 0`. A count
of zero **cannot bound a rare-event fraction tightly**: the exact one-sided 97.5% Clopper–Pearson
upper limit for 0/100 is **0.0362**, and the familiar rule-of-three bound is ≈0.03. The full-N
value of **0.005015** sits comfortably inside that band. Indeed, if the true replicate-collapse
rate is 0.005015, the probability of observing zero collapses in 100 draws is
`(1 − 0.005015)^100 = 0.605` — the partial reading was the *more likely* observation, not a fluke.
So the two readings are **entirely consistent**; the partial one simply carried no information
about where in `[0, 0.036]` the fraction lay, and reporting it as the bare point value `0` overstated
what 100 replicates could say.

This is exactly the D2 failure mode — a partial run presented with the precision of a full one —
and this time it happens to land in the **benign direction**: the true fraction is small, the
verdict does not flip, and the earlier reading survives. **That is luck about the direction, not
vindication of the practice.** The identical procedure applied to a cell where the rare event is
common would have produced a wrong verdict, and the prediction record §5 explicitly reserved that
outcome as the more interesting one.

The U3 span *widened* (+6.1%) and the U4 interval *narrowed* (−0.0208) on going from 100 to 2000
replicates. Neither movement is large relative to its threshold, and neither is treated here as a
finding: with 100 replicates the 2.5%/97.5% empirical quantiles are each estimated from a handful
of order statistics, so movement of this size is expected Monte-Carlo behaviour of the quantile
estimator.

**Statistical scope of every number in this section.** These are **bootstrap-replicate** fractions
and **bootstrap** intervals. A bootstrap replicate is *not* a biological replicate. The binomial
arithmetic above is a statement about Monte-Carlo sampling noise in the resampler, not a biological
inference. The experimental unit remains the **motor**, and the resampling unit here is the
training motor (80 of them, drawn with replacement, `n_tm = 80` per replicate). Nothing in this
cell increases the biological sample size.

## 6. Prediction outcome

The frozen prediction for this cell was **`UNIDENTIFIED_OR_WEAK`**. Its falsifier, stated in the
prediction record §5, was "any of U2/U3/U4 firing at full N" — no such firing occurred; the
committed mapping's first row is the one that applies.

> | observed at N=2000 | result | claim impact |
> |-|-|-|
> | U2/U3/U4 all `OK` | frozen prediction `UNIDENTIFIED_OR_WEAK` **REFUTED at full N** | The earlier `REFUTED_PARTIAL` is upgraded to a full-N refutation **within C10 scope only**. M4 identifiability on this cohort is supported. This is a `P1`/`P6`-scoped statement about one model's identifiability — **not** evidence for any mechanism. |

Applying it:

- **The frozen prediction `UNIDENTIFIED_OR_WEAK` is REFUTED AT FULL N, within B4C10 scope only.**
- **The earlier `REFUTED_PARTIAL` is upgraded to a full-N refutation**, again within B4C10 scope
  only. The upgrade is licensed because the run reached the frozen N with `resourceBoundPartial:
  false`, not because the numbers looked favourable.
- Of the three hypotheses held alive in prediction record §4, `H_M4_IDENTIFIED` is **supported on
  this cohort under these criteria**; `H_M4_WEAK` is **not supported at full N**; and
  `H_NOT_ESTABLISHED` does not apply, because all three intervals closed against the frozen
  criteria.

**Being wrong in the pre-committed direction is the recorded outcome, not a defect.** The
prediction was written before the run, committed, and then contradicted by the evidence. That is a
prediction record working correctly. The prediction record itself said as much: "Prediction I am
willing to be wrong about." No criterion, threshold, seed, or N was changed after seeing a number,
and the mapping applied here is the one that was committed, not one selected afterwards.

**Prospectivity: `NOT_SATISFIED`. This is a closed negative, not a pending check.**

An earlier draft of this report graded the ancestry check `NOT_VERIFIED`, which wrongly implied a
check that might still pass. It cannot pass. The commit graph was inspected:

| fact | value |
|-|-|
| commit introducing `B4C10-CORRECTED-FULL-PREDICTION.md` | `b9b5670`, **2026-07-21T22:44:31Z** |
| commit introducing `B4C10_CORRECTED_FULL_RESULT.json` | **`b9b5670` — THE SAME COMMIT** |
| B4C10 result written to disk | **2026-07-21T20:11:51Z** (`started_utc` 17:51:13Z + 8437.9 s) |

**The prediction and the result entered the repository in ONE commit**, 2 h 33 min after the run
had already finished. Per `CLAUDE.md` — *"a prediction is prospective only if it was committed
before its observation"* and *"prospectivity is decided by the commit graph, not by prose"* — the
required strict-ancestor relation is **structurally unattainable for this pair**: a commit cannot
be its own strict ancestor. **This result may not be labelled `PROSPECTIVE`, and no future commit
can repair it.**

> **Correction, recorded rather than silently fixed.** An earlier draft of this section asserted
> that the result was "NOT COMMITTED — still an untracked working-tree file", and reasoned that a
> future commit would satisfy the mechanical ancestry test while failing the substantive one. That
> premise was **false**: `git log --diff-filter=A` shows the result was already committed, in
> `b9b5670`, alongside the prediction. The conclusion is unchanged and in fact stronger — there is
> no mechanical test left to launder, because same-commit introduction forecloses ancestry
> outright. Found by adversarial verification of this report.

What **is** verified, and all this report claims: the prediction file records
`UNIDENTIFIED_OR_WEAK` with its outcome mapping fixed in advance of *this report*; the outcome
contradicts it; and the mapping applied is the recorded one, not one selected afterwards. That
makes this a **retrospectively-graded refutation on a pre-written prediction**, which is weaker
than a prospective refutation and is labelled as such throughout.

Tracked as **D9** in `ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md`, which also records the
only receipt that fixes this going forward: commit the prediction record **before launching** the
run it predicts.

## 7. Scope boundary — hard

Reproducing prediction record §6 verbatim:

> **C10 may not be used to repair C11.** They concern different models (M4 vs M7) and different
> likelihood structures (pooled i.i.d. vs motor-grouped). A favourable C10 says nothing about M7
> identifiability, and nothing about the withdrawn C11 `U4_OK`.

Spelled out:

- **Different models.** C10 tests `M4_MIXTURE_K3`, a three-component mixture. C11 tests
  `M7_HIERARCHICAL_MOTOR`, a motor-grouped hierarchy. They do not share parameters, a parameter
  count, or an identifiability geometry.
- **Different likelihood structures.** `_fit_m4_reduced` fits the **flat pooled** `coh.train_y`.
  M7's training NLL iterates `coh.train_by_motor` — the **grouped** structure that D1 corrupts.
  This structural difference is the reason C10 is valid on the frozen runner while C11 is not; it
  is the same fact, and it cuts in both directions.
- **Therefore:** this result does **NOT** restore, repair, support, or partially support the
  withdrawn C11 `U4_OK`. `P6` for C11 U4 remains **withdrawn** pending the corrected full-N C11 run
  (defect D1, `OPEN_UNTIL_CORRECTED_C11_FULL_RUN`). Nothing in this report may be cited toward it.

**Identifiability is not mechanism, and identifiability is not correctness.** U2/U3/U4 ask only
whether the fitted M4 parameters are *recoverable and distinguishable* on this cohort under
bootstrap resampling. A model can be perfectly identifiable and completely wrong about the biology;
an identifiable mixture is still a curve-fitting object until an independent mechanistic prediction
survives. Specifically:

- M4 being identified on this cohort does **not** make M4 correct.
- M4 being identified does **not** make M4 the UNI model. It is a competitor in the B3 leaderboard.
- No mixture mechanism is confirmed, implied, or supported by this result.
- The finding is bounded to **one cohort** (`derived_eligible_1_to_8`), **one model**, **one
  criterion set**, and **one resampling scheme**.

## 8. Defect impact

**D2 — resource-bound overestimate: second, independent confirmation.**
`RESOURCE-BOUND-RECLASSIFICATION.md` §2 projected B4C10 at **2.1 h** from a measured per-unit
`_fit_m4_reduced` cost of 3.8 s (2000 × 3.8 s = 7600 s = 2.111 h). The completed run measured
**8372.7 s = 2.326 h** — a ratio of **1.102**, i.e. the projection was accurate to within 10.2%,
with the excess attributable to CPU contention (the B4C02 full-N run was executing concurrently on
the same machine). Effective per-replicate cost under contention was **4.186 s**.

The first confirmation was the per-unit timing measurement itself (an extrapolation); this is the
second and stronger one, because it is an **end-to-end wall-clock measurement of the whole cell**
rather than a projection. Set against the runner's own stated cost model for this cell — the
`NOT_RUN` branch text at lines 1033–1036, `"≈ 33-100 h wall-clock; not feasible in this dispatch's
compute budget"` — the measured 2.326 h is **14.2× to 43.0× cheaper**. *Precision note:* that
33–100 h text sits in the `n_boot <= 0` branch, which this cell never took; the recorded partial
artifact for B4C10 carries no hour figure of its own, only `resourceBoundPartial: true` and the
`verdictScope` string. So the comparison is against the runner's stated cost model for the frozen
N, not against a number in the C10 result object. Either way, **B4C10 should never have been
partial**, and the record now shows that on measurement.

**D1 — cluster-bootstrap collapse: does NOT apply to C10.** `_fit_m4_reduced` fits the flat pooled
`coh.train_y` (runner line 1008), so duplicate motor draws enter the likelihood correctly and the
motor-cluster bootstrap is valid as written for a pooled i.i.d. likelihood. This is asserted by
`test_m4_pooled_path_is_unchanged_by_the_fix`, which compares sorted `train_y` between the legacy
and corrected arms, and it is recorded in the closure ledger's D1 `unaffected_lanes` field. **No
correction was applied to this run** (`correctionApplied = NONE`), and none was needed.

**D3 — hash-seed non-determinism: does NOT apply to C10.** C10 seeds with
`np.random.default_rng(seed_base)` and `seed_b = seed_base + b` (runner lines 1056, 1063) —
arithmetic only, no `hash()`. Confirmed by reading the frozen runner. The D3 closure ledger entry
lists C10 under `unaffected_lanes` for the same reason.

**D7 — `width` field provenance.** Not applicable in the direction that matters, but stated for
discipline: the U3 span and the U4 interval reported here are **percentile bootstrap** quantities
(`np.quantile` at 0.025/0.975, runner lines 1097–1098), computed directly by the C10 cell. They
are not BCa intervals and are not the B3 `width` field that D7 concerns. Any width quoted from this
report must be labelled **percentile**.

**D5/D6 — held-out data firewall.** This cell reads the frozen `derived_eligible_1_to_8` cohort's
duration channel and carries the original holdout events through cohort reconstruction unchanged
(runner lines 1071–1074) purely so that `b3.Cohort` can re-derive the frozen split. **No held-out
mark field (`nextStateN`, `direction`, `jump`) is read, printed, or reasoned about anywhere in this
cell or in this report.** No new data channel was spent.

## 9. Lane impact

| lane | scope | impact of this result |
|-|-|-|
| **LANE A** — duration-only B3/B4 evidence | B3 leaderboard, B3 intervals, the adverse M2-over-M3 finding | **UNAFFECTED.** No B3 number is recomputed, revised, or reinterpreted here. The B3 result was consumed read-only at sha256 `5d7a0589e94…` for the M4 `fullTrainNLL` reference only. |
| **LANE B** — corrected B4 robustness cells | B4C01/C02/C10/C11 | **THIS CELL MOVES.** B4C10 goes from `resourceBoundPartial` (100/2000, `RESOURCE_BOUND`) to a **full-N result at the frozen N=2000**. **B4C11 is UNAFFECTED and still blocked** on the corrected D1 rerun (see §7). B4C02 and B4C01 are **UNAFFECTED** by this cell's outcome; C02's own run is a separate matter and nothing here is predicated on it. |
| **LANE C** — mark process / `nextStateN` / `jump` | D5/D6 quarantine | **UNAFFECTED.** No mark field was touched. The retrospective-only quarantine stands exactly as written. |
| **LANE D** — motor-stack AIF implementation | `hierarchical-aif/src/motor_stack_aif/` | **UNAFFECTED.** No F-side module was invoked, changed, or scored by this run. The G-side fence (no `expected_free_energy`) is untouched. |
| **LANE E** — biological parity ladder | `P0..P8` | **UNAFFECTED.** See §10: no P-level moves. `FULL_PARITY = false` is unchanged, and the first unsatisfied level remains `P4` transfer. |
| **LANE F** — governance / reporting / claim guard | statuses, reason text, resource claims | **MOVES, narrowly.** D2 gains its second confirmation (§8) and the B4C10 row of the reclassification schedule can be marked delivered. No verdict elsewhere changes. |

## 10. P-ladder mapping

Per `hierarchical-aif/ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md`, this is a
**H-AIF-G5** receipt (`corrected full B4 reruns`), which that map routes to `P3` held-out
predictive and `P6` structural/mechanistic **per cell**. For *this* cell the honest routing is
narrower than the gate's general mapping:

| level | what this receipt is | movement |
|-|-|-|
| `P0` computational integrity | frozen runner, hash-verified result, full frozen N, deterministic arithmetic seeds, zero stderr | **no movement** — `P0` already holds |
| `P1` equation/implementation | a **parameter-recoverability / identifiability** statement about M4's fitted parameters under a motor-cluster bootstrap on one cohort | **no movement** |
| `P3` held-out predictive | **nothing.** C10 scores no held-out prediction. It is a training-cohort bootstrap; the holdout events pass through only so the frozen split can be re-derived | **no movement** |
| `P6` structural/mechanistic | a **negative-space** contribution only: it removes "M4 might be unidentifiable" as an objection on this cohort. Removing an objection is not supplying mechanistic evidence | **no movement** |
| `P4`, `P5`, `P7`, `P8` | untouched | **no movement** |

**Explicitly: NO P-LEVEL IS RAISED BY THIS RESULT.** It is a `P1`/`P6`-scoped identifiability
statement about **one model** on **one cohort**, exactly as the prediction record's committed
mapping said it would be. `P6` for C11 U4 remains withdrawn. `P6` for duration-only B3/B4 remains
unchanged. `P8` remains `FULL_PARITY = false` with `P4` transfer as the first unsatisfied level.
The map's ledger rule §4 is satisfied here only in the sense that it licenses **no** update: the
level definitions are named, the artifact is named, the scope is named, the falsifier is carried,
and the partial/negative states are preserved — and the conclusion of applying it is that nothing
moves.

## 11. Reproduction

```bash
cd C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM
python audits/phase-b/b4-identifiability-robustness-runner.py \
  --cells C10 --c10-boot 2000 \
  --out hierarchical-aif/results/motor_stack_aif/B4C10_CORRECTED_FULL_RESULT.json
```

Expected artifact sha256:

```text
959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde
```

Verify with:

```bash
sha256sum hierarchical-aif/results/motor_stack_aif/B4C10_CORRECTED_FULL_RESULT.json
sha256sum audits/phase-b/b4-identifiability-robustness-runner.py
# runner must be 3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7
```

Environment required for byte-identity: python 3.12.10, numpy 2.3.5, scipy 1.16.3, CPU-only,
single worker (`workers=1`, `updating="deferred"` are fixed in `_fit_m4_reduced`). Expected
wall-clock ≈2.1–2.4 h depending on machine contention. All seeds are arithmetic
(`20260717 + b`), so the result should be reproducible bit-for-bit on the same scipy version;
**bit-identity across scipy versions is not claimed and has not been tested** — `differential_evolution`'s
internals are version-sensitive.

## 12. Limitations and adverse notes

1. **1994 of 2000, not 2000 of 2000.** Six replicates failed with **no recorded reason**
   (`NOT_RECORDED`). Attribution requires the out-of-tree replay described in §3 and has not been
   done. The U2 verdict is bounded against the worst case (0.008 vs a 0.25 threshold); the U3 and
   U4 quantiles are **not** so bounded — that sensitivity is `NOT_COMPUTED`.
2. **One cohort.** `derived_eligible_1_to_8` only. 80 training motors, 793 training events, 19
   holdout motors. Right-censored events are excluded from the frozen cohort entirely, so this
   result says nothing about censored dwells.
3. **19 holdout motors is a small number of experimental units**, and the experimental unit is the
   **motor**. This cell does not use the holdout for scoring, but the surrounding evidence body is
   built on those 19 units, and no result here enlarges them. Underpowered is not equivalence.
4. **Bootstrap replicates are not biological replicates.** Every interval here is a Monte-Carlo
   interval over resampled training motors, not a confidence statement about a population of
   motors, cells, or cultures.
5. **The adverse M2-over-M3 result stands, untouched and unremediated.** `M2_LOGNORMAL` — an
   adversarial baseline, never the UNI model — out-predicts the reference `M3_TWO_TIMESCALE` by
   ≈0.0369 nats event-pooled on held-out data. Nothing in B4C10 addresses, weakens, or explains
   that finding. It is reported alongside this result, never instead of it.
6. **Related resolution note (D7).** The narrowest motor-equal B3 contrast is `M4_MIXTURE_K3` at a
   **percentile** width of 0.083461 (**BCa** width 0.084141), and the corrected resolution floor is
   ≈0.042 nats (**BCa** half-width 0.042070; percentile half-width 0.041730) — not the 0.064
   figure that came from the mislabelled `width` field. Every width here carries its interval
   label, because quoting 0.083461 bare would repeat the exact D7 defect this note exists to
   correct. That B4C10 concerns M4 and that M4 holds
   the narrowest B3 contrast are **separate facts about the same model**; neither supports the
   other.
7. **Identifiability ≠ correctness ≠ mechanism.** Restated because it is the single most likely
   misreading of this report. `M4_status = IDENTIFIED_ON_THIS_COHORT` is a statement about
   parameter recoverability under resampling, full stop.
8. **The `U1` component is inherited, not re-derived.** `U1_alreadyDone_in_B3: "DISTINCT (per B3
   result)"` is copied from the B3 artifact. The `M4_status` string asserts U1; this run did not
   re-test it.
9. **Prospectivity is `NOT_SATISFIED`** (§6) — a **closed negative**, not a pending check. The
   prediction record was committed in `b9b5670` at 2026-07-21T22:44:31Z, **2 h 33 min after** the
   run finished at ~20:11:51Z. This refutation is **retrospectively graded against a pre-written
   prediction** and may never be labelled `PROSPECTIVE`. Tracked as **D9**.
10. **Concurrency caveat on the timing claim.** The 8372.7 s figure was measured while B4C02 ran
    concurrently. It is therefore an upper bound on the uncontended cost of this cell, which
    strengthens rather than weakens the D2 conclusion, but it is a single measurement on one
    machine and not a distribution.
11. **B4C02 is still running.** Its partial log is not a result and is not referenced, quoted, or
    relied upon anywhere in this report.

---

`NEXT_ACT = Update the H-AIF-G5 row and the B4C10 row of RESOURCE-BOUND-RECLASSIFICATION.md /
HIERARCHICAL-AIF-NEGATIVES-AND-PARTIALS.md to record B4C10 as FULL_N_DELIVERED with this report
and sha256 959a00e9… as its receipt; run claim_guard over this report; then, once B4C02 lands,
queue B4C11 at the frozen N=2000 on the CORRECTED build_bootstrap_cohort — that run, and only that
run, can address the withdrawn C11 U4 and defect D1. Do NOT let this favourable C10 shorten,
reduce, or pre-judge it.`
