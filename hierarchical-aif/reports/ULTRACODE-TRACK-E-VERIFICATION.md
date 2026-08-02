# TRACK E VERIFICATION — MECHANISM DISCRIMINATOR (E1)

**Verifier scope:** code + recorded result artifacts + TRAIN-partition reads (declared inline). No holdout row was read, computed over, or aggregated by this verification. All holdout quantities cited below come from `audits/phase-b/b3-model-competition-result.json` and `experiments/results/science-gates-report.json` — already-spent published numbers.

**Headline:** the design contains three genuinely valuable findings (E0.1, E0.3, E0.4), and one loud CONTRADICTION on the D5 firewall. It is **not decisive**, its verdict-bearing decision rule is **unreachable at 19 motors by its own arithmetic**, and its negative-control battery has **zero power against the most likely implementation bug**. Recommendation stated in §9.

---

## 1. CHECK 1 — DOES IT RELY ON THE BURNED MARK CHANNEL? **YES. CONTRADICTED.**

### 1.1 The entire discriminator is built on the burned channel

**CHECKED_AGAINST_CODE · HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY**

Every primary statistic in §1.1 is a function of `direction` / `jump` / `nextStateN`:

| statistic | mark dependence |
|---|---|
| Δ_exit | `d_i` = `direction` of event *i* |
| Δ_mem | `a_i` = `direction` of event *i−1* |
| Π_mem | `direction × direction` joint |
| E1-C2 | `direction` (global swap) |
| E1-C5(ii) | `jump` (restrict to \|jump\|=1) |
| E1-S `D_a`…`D_d` | every rung carries `p(N' \| N)` = `nextStateN` |
| ICC | **the only mark-free statistic in the protocol** |

So 3 of 4 primaries, 2 of 8 controls, and 4 of 4 ladder rungs consume the channel that D5 permanently burned.

### 1.2 The document contradicts itself on prospectivity

**CONTRADICTED · CHECKED_AGAINST_CODE**

- §0 E0.5 asserts: *"The arrival-direction observable is **genuinely unspent**."*
- §6.4 asserts: *"It is **quasi-prospective, not prospective**."*

Both cannot stand. The binding fact is §6.4, and even that is too generous. The correct label under the D5 contract is **`HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`** — not "quasi-prospective". The prior UltraCode track's read of *"empirical marginals of direction/jump per state"* is precisely the marginal that Δ_exit and Π_mem are built from. Δ_exit and Π_mem are **not fresh statistics at all**; they are a re-slicing of an already-read marginal.

Δ_mem (the lag-1 joint) is the one functional the repo has genuinely never computed — I confirm the code side of E0.5:

- `grep -c "direction\|jump\|nextStateN" audits/phase-b/b3-model-competition-runner.py` → **0**. **CHECKED_AGAINST_CODE.** B3 never touched the mark channel. Credit to the track: this part of E0.5 is correct and non-obvious.
- But `scripts/run-science-gates.py:312-314` scores **holdout** events through `event_scores(holdout, mechanism)` → `sourceLogLikelihood` (`lib/source-first-passage.js`, branches on `event.direction`) and `memoryless_scores(holdout, memoryless)` (branches on `event["direction"]`). **CHECKED_AGAINST_CODE.** The holdout **exit-direction** channel is spent inside the released science gates, independently of the UltraCode track.

Net: the *channel* is burned twice over; only the *lag-1 bivariate functional* is unread. "Genuinely unspent" is wrong.

### 1.3 The track spent MORE of the burned channel while designing the protocol — and mislabelled it

**CONTRADICTED · HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY**

§1.4 states: *"The holdout was touched for **counts only** — no effect estimate on any holdout motor was computed."*

That defence is not available, because §4 reports these **holdout mark-channel statistics**:

| §4 quantity | what it actually is |
|---|---|
| `holdout exit counts: 150 on / 83 off` | **a holdout `direction` marginal** — the exact object that burned the channel |
| `holdout arrival-labelled rows: 215` | a holdout lag-1 `direction` derived count |
| `motors with both arrival arms: 16 / 19` | a holdout arrival-direction per-motor contingency |
| `motors with both exit directions: 16 / 19` | a holdout exit-direction per-motor contingency |
| `per-motor row counts: 49, 43, 30, 11, …, 2, 0` | per-motor arrival-labelled counts |

I can corroborate the last row's provenance without touching holdout data: `b3-model-competition-result.json → cohorts.derived_eligible_1_to_8.holdoutMotorEventCounts` gives `{50, 44, 31, 12, 10, 10, 10, 8, 8, 7, 7, 6, 5, 5, 5, 4, 4, 4, 3}` (sum 233). The §4 vector is **exactly each of these minus one**, plus a 20th motor at 0 — i.e. it is the per-motor count of events *possessing a lag-1 arrival label*. **CHECKED_AGAINST_RESULTS.** That is a mark-channel derivative, not a "count".

A marginal is not an effect estimate — the track is right about that narrow point. But "counts only" is the wrong characterisation, and it matters: the arm sizes were known **before** §2.4 registered one-sided hypotheses and **before** §4 declared the effective N. A pre-registration written with holdout arm sizes in hand is weaker than one written blind, even if arm sizes are ancillary under the conditional permutation test of §2.5.

### 1.4 E0.1 burned holdout reads to verify something provable from two lines of source

**CONTRADICTED (method) · CHECKED_AGAINST_CODE**

E0.1 reports: *"Verified over all 1349 events: `direction != sign(jump)` in **0** cases."* That computation ranged over holdout `direction`/`jump`/`nextStateN`.

It was unnecessary. `scripts/ingest-wadhwa-data.py:159-160`:

```python
"direction": None if next_state is None else ("on" if next_state > dwell["state"] else "off"),
"jump":      None if next_state is None else next_state - dwell["state"],
```

The redundancy is **true by construction** — both fields are pure functions of `(next_state, state)`. No data read is required to establish it. **E0.1's substantive conclusion is CORRECT and is the single most valuable finding in the document** (see §5.1 below); its *verification method* spent holdout mark reads it did not need.

One edge case the track's blanket statement misses: `jump == 0` maps to `direction = "off"` while `sign(0) = 0`. **TRAIN_ONLY**, I confirm 0 events with `jump == 0` among 1048 train events and 0 direction/jump inconsistencies. Holdout: **NOT_CHECKED — would require holdout mark access; requires prospective record first.**

---

## 2. CHECK 2 — ARE THE ADVERSARIAL BASELINES AND THE CURRENT-DESIGN CONTROL NAMED?

**Named: YES. Entered as competitors: NO.** **CHECKED_AGAINST_CODE + CHECKED_AGAINST_RESULTS · NO_DATA_ACCESS_NEEDED**

The nine B3 models are confirmed present in the result artifact: `M0_EXPONENTIAL, M1_WEIBULL, M2_LOGNORMAL, M3_TWO_TIMESCALE, M4_MIXTURE_K3, M5_GAMMA, M6_SEMI_MARKOV_STATE_DEPENDENT, M7_HIERARCHICAL_MOTOR, M8_EMPIRICAL_KDE`.

§1.2 names all five required adversarial baselines (M0, M1, M2, M5, M8) under class (a), plus M4 and M3; assigns M6 to (b) and M7 to (c). The current-design control is named twice: the D-L-T model (`lib/source-first-passage.js`) and the memoryless competing-risk baseline (`scripts/run-science-gates.py:176-196`) both appear under class (b). **Requirement met on naming.**

**But the naming is rhetorical, not operational.** No E1 cell puts an adversarial baseline into a contest:

- **E1 primary** (Δ_exit / Δ_mem / Π_mem / ICC) is model-free. The baselines appear only as *predicted zeros* in a decision table. Since **all seven** class-(a) models predict Δ_exit = Δ_mem = Π_mem = 0 identically, the primary cannot rank them — it can only reject the class. The track says this (§3, "(a) is falsified as a *complete* account") and is correct to.
- **E1-S ladder**: `D_a` is *"lognormal `p(dt|N)` × multinomial `p(N'|N)`"* — per-state, in seconds-space. That is **not M2**. M2 is a single mean-one shape fitted in normalised `y = dt/scale_N` space and shared across all eight states (`b3-model-competition-runner.py:196+`; `m0_logpdf(y)` and siblings take no state argument — **CHECKED_AGAINST_CODE**). **`D_a` is a new, untested, more flexible model.** If `D_b` beats `D_a`, that is uninterpretable as evidence for state-dependent hazard unless `D_a` is at least as strong as the standing adversarial winner. **Defect: M2_LOGNORMAL must be a floor rung of the ladder, or every ladder contrast is confounded with `D_a`'s unknown quality.**
- **E1-X** is the only cell that touches real baselines, and it uses exactly two (M2, M3).

---

## 3. CHECK 3 — CI-BOUND VERDICT WITH MOTOR AS RESAMPLING UNIT?

**Resampling unit: YES. Estimand: NO — the point estimate is event-weighted.** **CONTRADICTED**

**Correct:** §2.2 declares experimental unit = MOTOR; §2.5 resamples the 19 holdout `motorId`s with replacement carrying whole chains; §2.7 is CI-bound with "point estimates are never verdicts"; §5 E1-C3 explicitly runs the event-level bootstrap as a labelled pseudoreplication demonstration. That is correct discipline.

**The contradiction:** §2.2's registered primary estimator is Cochran–Mantel–Haenszel weighted,

> `Δ̂ = Σ_s w_s (ȳ_s,on − ȳ_s,off) / Σ_s w_s`, `w_s = n_on·n_off/(n_on+n_off)`

The weights are **event counts**. B3's declared primary aggregation is `"primary": "MOTOR_EQUAL (v3 R3)"` (**CHECKED_AGAINST_RESULTS**, `b3-model-competition-result.json → aggregation`). E1's primary estimator therefore **abandons B3's frozen motor-equal aggregation** in favour of an event-weighted one. Three motors carry 125/233 = 54% of holdout events (**CHECKED_AGAINST_RESULTS**), so under CMH weights those three dominate the point estimate. A motor-cluster bootstrap corrects the **variance**; it does not correct the **estimand**.

This is not a stylistic quibble — it breaks §4:

**§4 computes MDE from the *per-motor unweighted* between-motor sd (1.429, 1.443), which is the sampling sd of a motor-equal estimator. It does not describe the CMH estimator registered in §2.2.** The power table and the registered primary are two different tests. One of them must change.

### 3.1 The corrected-bootstrap requirement is impossible as written

**CONTRADICTED · CHECKED_AGAINST_CODE**

§2.5: *"E1 must import that corrected bootstrap or reproduce its test."*

`hierarchical-aif/src/motor_stack_aif/bootstrap.py` cannot be imported for E1:

1. `draw_motors(train_motors, rng)` and `_assemble(coh, sampled, …)` resample **`coh.train`** and pass `holdout_events = [dict(e) for e in coh.holdout]` through **unchanged**. It resamples the wrong partition — E1 needs holdout motors resampled and train fixed.
2. `_assemble` rebuilds a full `b3.Cohort`, which recomputes `scale_N` from the resampled train (`b3-model-competition-runner.py:115-120`). E1 explicitly requires `scale_N` **frozen**. Importing it would unfreeze the normalisation per replicate.

3. **The D1 defect does not even bite E1's primary.** The module docstring states the defect scope precisely: `train_by_motor` grouping for M7's grouped likelihood is AFFECTED; M4's pooled flat likelihood is UNAFFECTED. For a CMH-weighted stratum contrast, collapsing a motor drawn K times is **algebraically identical** to keeping K distinct clusters: doubling `n_on` and `n_off` doubles `w = n_on n_off/(n_on+n_off)` exactly and leaves the stratum mean difference unchanged. **Δ_exit / Δ_mem / Π_mem are invariant to D1 by construction.**

Where D1 *does* bite E1 is **ICC** (a variance component computed per motor group: collapsing duplicates inflates group size and shifts `var_between`/`var_within`) and **E1-S rung `D_c`** (motor-level frailty). §2.5's blanket requirement points the reader at the wrong target and leaves the two genuinely at-risk statistics unguarded. **Defect.**

---

## 4. CHECK 4 — IS THE FROZEN SPLIT PRESERVED?

**Substantially YES, with one specification inconsistency.**

**CHECKED_AGAINST_CODE.** Line references verified exactly:

| track cites | actual | status |
|---|---|---|
| `sha256_mod5` at `:88-89` | `def sha256_mod5` lines 88-89 | exact |
| `FAILED-SPLIT-MISMATCH` halt at `:104-108` | halt at lines 104-108 | exact |
| censoring exclusion at `:109-110` | `elig = [… not e["rightCensored"] …]` lines 109-110 | exact |
| per-state training scale at `:117-121` | `by_state` loop 116-118, `scale_N` 119-120, `_y` at 130 | ±1, substantively correct |
| ingest `direction`/`jump` at `:159-160` | exact | exact |
| `run-science-gates.py:176-196` memoryless | `fit_memoryless` 176-185, `memoryless_scores` 187-196 | exact |
| `run-science-gates.py:454-467` G06 | `gate("G06_…")` block 453-467 | ±1 |

Frozen counts **CHECKED_AGAINST_RESULTS**: `summary = {train: 793, trainMotors: 80, holdout: 233, holdoutMotors: 19}` for `derived_eligible_1_to_8`. Matches §2.1 exactly. E1-C7 (split mutation must HALT) and the reassertion requirement are correct.

**Inconsistency:** §2.1 freezes the cohort at 233/19, but §2.3 *repairs* B3's right-censoring exclusion and makes a **stratified log-rank on censored-inclusive data** the primary estimator. The primary therefore runs on up to ~252 events while the runner asserts 233. The cohort E1 actually analyses is **not** the frozen B3 cohort. This is defensible science — inheriting an undeclared exclusion is worse — but the artifact must declare **two** cohorts with two counts, and §2.1's table as written would make the runner assert a number it does not use.

### 4.1 Unflagged: D6 corrupts the mark channel on holdout, and E1 consumes it

**CHECKED_AGAINST_CODE · HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY**

`scripts/ingest-wadhwa-data.py:141-143` range-checks `dwell["state"]` and `continue`s on failure. `next_state = dwell["nextState"]` at `:147` is **never range-checked** — confirmed, the only occurrences of `next_state`/`nextState` in the file are lines 59, 73, 147, 158, 159, 160, none validating. Per established fact D6, this writes `nextStateN = -1` for **2 holdout events**.

Those two rows carry `direction = "off"` and `jump = -1 − stateN` (i.e. **\|jump\| ≥ 1, plausibly ≥ 2**) — a fabricated "off" exit and a fabricated "off" arrival for the successor event.

**TRACK E NEVER MENTIONS D6.** These corrupted rows land directly in:

- Δ_exit (spurious `off` arm member),
- Δ_mem (spurious `off` **arrival** for the following event),
- Π_mem (spurious cell),
- **E1-C5(ii)**, the veto control, which keys on `|jump| = 1` — the corrupted rows are exactly the large-`|jump|` rows the artifact hypothesis (e) predicts.

With 16 effective motors and a median holdout motor carrying 5–8 events, two corrupted rows landing in a small motor can move that motor's per-motor Δ materially. **The protocol contains no exclusion rule, no sensitivity analysis, and no mention.** This must be a pre-registered exclusion with the count declared, not discovered at analysis time.

**TRAIN_ONLY** control read: 0 train events have out-of-range `nextStateN`, so the defect is holdout-side only in this cohort — which is the worst place for it.

---

## 5. THE THREE FINDINGS THAT ARE GENUINELY GOOD — AND ONE THAT IS BROKEN

### 5.1 E0.1 (mark triple-counting): **CONFIRMED, and it is the most valuable line in the document**

**CHECKED_AGAINST_CODE · NO_DATA_ACCESS_NEEDED.** Writing `p(N'_i, direction_i, jump_i | ·)` would count one degree of freedom three times. Given `N_i`, the pair `(direction_i, jump_i)` is a deterministic function of `N'_i` (`ingest:159-160`). Any `F_motor` built on the four-coordinate blanket inflates the mark contribution ~3× relative to the dwell contribution. **This is a real defect found before implementation and it should be propagated to whichever track owns the target-stack specification.**

### 5.2 E0.3 (undeclared 0.300 s left truncation): **CONFIRMED and under-sold**

**CHECKED_AGAINST_CODE + TRAIN_ONLY.**

- `grep -rn "truncat"` across `audits/phase-b`, `scripts`, `lib`, `experiments`, `hierarchical-aif` (`.py/.js/.mjs/.ts`) returns **zero hits**. No competitor carries a truncation term.
- **TRAIN_ONLY** (declared: 793 train, states 1–8, uncensored): `min = 0.300 s`, 22 events at exactly 0.300 s, 98 events below 0.5 s, and the support is quantised on a **0.02 s grid** (0.30, 0.32, 0.34, …). The floor is 15 samples and it is **present in the train partition alone** — so `t_min` is freezable from train and E1-X is executable without any new holdout read.
- `hierarchical-aif/protocols/B4C02-CORRECTED-FULL-PREDICTION.md` names exactly the three generators the track claims (`weibull_gamma_blend`, `three_timescale_heavy_tail`, `per_motor_heterogeneous_weibull`) and contains **no** mention of truncation, floor, or `t_min`. **CHECKED_AGAINST_CODE.** The track is right that B4C02 structurally cannot detect this.

**I can strengthen the track's case quantitatively.** Using `scale_N` from the published artifact (**CHECKED_AGAINST_RESULTS**): `{1: 4.749, 2: 3.483, 3: 6.351, 4: 5.063, 5: 7.948, 6: 14.390, 7: 18.245, 8: 24.521}`. The truncation point in the models' normalised `y`-space is `y_min(N) = 0.300 / scale_N(N)`, ranging **0.0122 (N=8) to 0.0861 (N=2)**. Under a mean-one exponential the omitted renormalisation is `−log S(y_min) ≈ y_min`, i.e. **0.012–0.086 nats per event**.

The retained adverse M2−M3 gap is **0.0369 nats/event** (**CHECKED_AGAINST_RESULTS**, `adverseLognormalRetention.derived_eligible_1_to_8`). **The omitted term is of the same order as, and at N=2 is 2.3× larger than, the effect it is invoked to explain.** E1-X's #1 ranking in §7 is correct and I endorse it independently.

**But E1-X has two defects the track did not catch:**

**(a) Leakage in `t_min`.** §2.9 sets `t_min = 0.300 s` at *"the observed detection floor"* — observed over **all 1240 uncensored dwells**, i.e. train **and holdout**. §5 E1-C5 is scrupulous about this (*"threshold frozen from the training partition"*); §2.9 is not. A truncation parameter estimated with holdout durations in scope, used in a refit that is then scored on holdout, is a leakage path. **TRAIN_ONLY** verification above shows the floor is 0.300 s in train alone, so the fix is free: **declare `t_min` train-frozen.** As written, E1-X is `HOLDOUT_ALREADY_SPENT_DURATION_ONLY`-contaminated.

**(b) The correction is written in the wrong space and breaks the model family.** §2.9 writes `log p(dt_i) → log p(dt_i) − log S(t_min | N_i)`. But every B3 competitor is a **mean-one density in `y`, with a single shape shared across all eight states** (`m0_logpdf(y)` etc. take no state argument — **CHECKED_AGAINST_CODE**). So (i) the correction must be `− log S_y(0.300/scale_N(N_i))`, which is **state-dependent** and therefore breaks the cross-state pooling that defines the fit; and (ii) a left-truncated mean-one density **no longer has mean one**, so the truncated refit is not a member of the frozen family. §2.9 must specify whether the mean-one constraint is imposed pre- or post-truncation. These are different models and they will give different answers.

### 5.3 E0.4 (per-state normalisation removed state-dependent means): **CONFIRMED**

**CHECKED_AGAINST_CODE.** `b3-model-competition-runner.py:116-120, 130` divides each dwell by the training mean for its state before scoring. B3 therefore tested state-dependence of *shape* only, never of *mean*. Correct and material.

**Consequence the track half-notices:** because `scale_N` depends only on state and strata are `(motor, state)`, **the normalisation cancels exactly in every within-stratum difference**. Δ_exit and Δ_mem are numerically identical whether computed on `log y` or `log dt`. Therefore **E1-C8** (*"compute `scale_N` from holdout → must HALT or flag LEAKAGE"*) is **vacuous for all three primary contrasts** — no leakage is possible through a constant that cancels. It is a real control only for E1-S. Registering an invariant-by-construction check as a mandatory leakage guard whose failure invalidates the primary is exactly the vacuous-success pattern the operating contract warns against. **Demote E1-C8 to E1-S scope, or state explicitly that it is a code-path smoke test with no inferential content.**

### 5.4 E0.2 (G06 already ran the naive test): **numbers CONFIRMED, interpretation OVERSTATED**

**CHECKED_AGAINST_RESULTS.** `science-gates-report.json` G06 reproduces every quoted figure to the last digit: `status: FAIL`, mechanistic `−3.838083424564402`, memoryless `−3.8963417959275564`, advantage `+0.05825837136315377`, interval `[−0.015801079856724822, +0.13264344169039152]`, 2000 replicates, seed 20260717. Half-width = **0.0742** ✓. G05 `status: FAIL`, `passedReplicates: 2 / 3` ✓.

**CHECKED_AGAINST_CODE.** The coupling argument is sound in structure: `lib/source-first-passage.js` `sourceDensities` gives `plus = kPlus·survival` and `minus = Σ w_j r_j e^{−Λ_j t}`, so direction and dwell are dependent under D-L-T; `fit_memoryless` gives constant cause-specific hazards, so they are independent under the baseline.

**Overstatement:** the track concludes *"G06 is therefore **already** a dwell×direction-coupling test."* It is not a **clean** one. D-L-T differs from the memoryless baseline in **two** ways simultaneously — the coupling **and** the dwell shape (multi-exponential mixture vs single exponential). The +0.058 nats is a sum of both contributions with no decomposition. G06 bounds the **total** predictive gain of the whole mechanistic model; it does not isolate coupling. The resolution figure (±0.074 nats/interval) is valid and useful; the causal reading is not. **REPORTED_BY_TRACK, partially CONTRADICTED.**

---

## 6. CHECK 5 — POWER. THE HONEST ANSWER IS: **ALMOST NOTHING IS DETECTABLE, AND THE PROTOCOL'S OWN DECISION RULE IS UNREACHABLE.**

**NO_DATA_ACCESS_NEEDED** — all of this is standard sample-size arithmetic over already-published interval widths.

### 6.1 The empirical resolution floor at 19 motors, from published intervals

**CHECKED_AGAINST_RESULTS.** `b3-model-competition-result.json → cohorts.derived_eligible_1_to_8.contrasts.NLPD_motor_equal`, every model vs M3, motor-cluster BCa:

| model | point | BCa | width | verdict |
|---|---|---|---|---|
| M0_EXPONENTIAL | −0.11365 | [−0.29763, +0.03305] | 0.3289 | INCONCLUSIVE |
| M1_WEIBULL | +0.00103 | [−0.06815, +0.07204] | 0.1399 | INCONCLUSIVE |
| **M2_LOGNORMAL** | **+0.02502** | **[−0.04370, +0.08676]** | **0.1285** | **INCONCLUSIVE** |
| M4_MIXTURE_K3 | +0.01022 | [−0.02446, +0.05968] | 0.0835 | INCONCLUSIVE |
| M5_GAMMA | −0.02940 | [−0.12351, +0.05984] | 0.1801 | INCONCLUSIVE |
| M6_SEMI_MARKOV | +0.00444 | [−0.06918, +0.08741] | 0.1552 | INCONCLUSIVE |
| M7_HIERARCHICAL | +0.00164 | [−0.07740, +0.08035] | 0.1580 | INCONCLUSIVE |
| M8_EMPIRICAL_KDE | +0.01181 | [−0.02814, +0.05767] | 0.0864 | INCONCLUSIVE |

**Eight of eight INCONCLUSIVE. Not one CI excludes zero.** Best achievable half-width on a per-event log-score contrast at 19 motors is **±0.042 nats**; typical is ±0.064–0.090.

Add G06's ±0.074 nats/interval on the joint dwell×direction score, also FAIL.

**Two independent predictive-contest routes, 9 density models plus a mechanistic model plus a memoryless baseline, and zero CI-excluding-zero outcomes.** That is the calibration any new discriminator must beat.

### 6.2 This breaks E1-X's registered decision criterion

**CONTRADICTED.** §2.9 registers: *"if the M2-over-M3 advantage **narrows by more than half, or reverses**, the adverse result is an artifact."*

The M2-over-M3 advantage on B3's **motor-equal primary** is `+0.02502` with BCa `[−0.0437, +0.0868]`. **A "50% narrowing" of a quantity whose 95% interval spans from −0.044 to +0.087 is not a measurable event.** Monte Carlo noise and refit variation alone will move a point estimate of 0.025 by more than half. The criterion is a point-estimate rule on a statistically null quantity.

Compounding it: the *retained adverse finding* is the **event-pooled** number, `0.0369` nats (`adverseLognormalRetention`), which carries **no interval at all** in the artifact. §2.9 does not say which of the two it targets. **Estimand ambiguous, criterion untestable as written.**

**Repairable, and worth repairing:** score the **paired** difference `(M2−M3)_truncated − (M2−M3)_untruncated` per motor, under the same motor-cluster bootstrap with **common random numbers**. Paired contrasts on the same holdout motors are dramatically tighter than either marginal, and — given §5.2's finding that the omitted term is 0.012–0.086 nats against a 0.037-nat gap — a paired design plausibly *does* have resolution here. **This is the one E1 cell I judge to be worth running, and only after this repair plus the train-frozen `t_min` fix.**

### 6.3 E1 primary: MDE arithmetic verified, then pushed through the actual decision rule

**Track's numbers reproduce.** Their MDE uses two-sided `z = 1.96 + 0.842 = 2.802`:
`2.802 × 1.429 / √19 = 0.9186` ✓ (0.918); `2.802 × 1.443 / √19 = 0.9276` ✓ (0.927); `@16 → 1.0009` ✓ (1.000). Required-N figures also reproduce: 0.44 → 84, 0.50 → 65, 1.32 → 9, 1.00 → 16, 0.92 → 19. G06 route `(0.074/0.058)² × 19 = 30.9` ✓ → ~31 holdout → 155 total at the 1-in-5 split.

**Two errors:**

1. **Sidedness mismatch.** §2.4 registers **one-sided** hypotheses and §2.7 uses a one-sided lower bound, but the MDE table is computed **two-sided**. The one-sided MDE is `2.487 × 1.429/√19 = 0.815`. The power table does not describe the registered test.
2. **Design-effect slip.** §4 writes `1 + (m̄−1)·ICC` then computes `1 + 11.3(0.26) ≈ 3.9` — using `m̄` where the formula says `m̄−1`. With `m̄ = 215/19 = 11.32`, the correct DE is `1 + 10.32(0.26) = 3.68`, effective n ≈ 58, not ≈ 55. §5 E1-C3 applies the same formula **correctly** (`1 + (12.3−1)(0.26) = 3.93`). Internally inconsistent.

**The error that matters — §4 never propagates power through §2.7.** §2.6 explicitly designates the **Bonferroni-0.9875 interval, not the nominal one, as verdict-bearing**. One-sided α = 0.0125 → `z = 2.2414`:

> **Verdict-bearing MDE = (2.2414 + 0.8416) × 1.429 / √19 = 1.011 log units.**

**The training effect is +0.923. The MDE of the interval that actually decides the verdict is 1.011. The protocol is underpowered against its own registered effect size, before any control is applied.**

Carrying it through all four §2.7 conditions, at the **optimistic** assumption that the holdout effect equals training exactly:

| condition | power |
|---|---|
| (1) Bonferroni one-sided lower bound > 0, n = 19 | `z = 0.923·√19/1.429 − 2.2414 = 0.574` → **72%** |
| (1) at effective n = 16 (16/19 motors have both arms) | `z = 0.343` → **63%** |
| (3) E1-C5 restricted, nominal, tolerating 50% attenuation | `z = 0.4615·4/1.429 − 1.645 = −0.353` → **36%** |
| (2), (4) | ~1 (permutation p and null control track condition 1) |

**Joint probability of emitting `MEMORY_SUPPORTED` ≈ 0.63 × 0.36 ≈ 23%, at the optimistic effect size.** If the holdout effect is half of training — entirely ordinary, and *expected* here because the direction was selected from training by inspecting 8/8 sign consistency, i.e. winner's curse — **joint power falls below 5%.**

**§2.7 condition 3 is internally self-contradictory.** It tolerates ≥50% attenuation while demanding the attenuated estimate's CI still exclude zero. Detecting 0.46 log units at the nominal one-sided bound needs `n = (2.487×1.429/0.46)² = 60` motors; at the Bonferroni bound, `n = (3.083×1.429/0.4615)² = 91`. The `≥50%` clause does no work: the only way condition 3 passes is if the effect does **not** attenuate at all. And the `|jump| = 1` restriction of C5(ii) discards ~25–30% of rows and dissolves strata that lose an arm, shrinking effective N further — a cost §4 never books.

### 6.4 What N would actually be required

Per-motor sd from training: 1.429 (Δ_mem), 1.443 (Δ_exit). Frozen split is 1-in-5.

| target | holdout motors | total motors | available (99–109) |
|---|---|---|---|
| Δ_mem @ 0.923, **Bonferroni** one-sided, 80% | **23** | **115** | ✗ (19 / ~99–109) |
| Δ_mem @ 0.46 (the attenuation §2.7 tolerates), Bonferroni | **91** | **456** | ✗ |
| Δ_exit @ 0.44, two-sided nominal (track's own) | 84 | 420 | ✗ |
| Δ_exit @ 0.44, Bonferroni | **102** | **510** | ✗ |
| G06-sized predictive gain (+0.058 nats) | **31** | **155** | ✗ |
| `MEMORY_ABSENT` at ±0.25 margin | ≳ **300** | ≳ 1500 | ✗ |

**Not one target is reachable.** The single closest — 23 holdout motors for the un-attenuated optimistic Δ_mem — still exceeds the 19 available, and it is exactly the case in which the winner's-curse correction bites hardest.

**Plain answer to the question asked:** *at 19 holdout motors, almost nothing is detectable.* The one statistic whose training effect even approaches the resolution floor (Δ_mem) is powered at roughly 63–72% on its first condition and ~23% jointly, under assumptions that are systematically optimistic. **`MEMORY_SUPPORTED` is a pre-registered near-certain `NOT_ESTABLISHED`.** No reanalysis of Wadhwa 2022 changes this. **`INDEPENDENT_TRANSFER_REQUIRED` / `PROSPECTIVE_NEW_DATA_ONLY`.**

**Credit where due:** §4 and §6.6 register `MEMORY_ABSENT` as **unattainable in advance**, so no null can be laundered into an absence claim. That is exactly right and is the strongest governance feature of the document. The failure is that §4 stops one step short — it never applies the same honesty to `MEMORY_SUPPORTED`.

---

## 7. CHECK 6 — NEGATIVE CONTROLS

**All three required controls present. The battery has a structural blind spot.**

| required | present | assessment |
|---|---|---|
| label scrambling | **E1-C1** within-stratum arrival-label permutation | present; see defect below |
| direction reversal | **E1-C2** global on↔off swap | present but **near-vacuous** — a difference of means flips sign by algebra; this is an implementation smoke test, not a scientific control. Referenced file `tests/semantic/orientation-direction-and-score-sign.test.mjs` **exists** (**CHECKED_AGAINST_CODE**). |
| event-level bootstrap (pseudoreplication) | **E1-C3** | **best control in the document.** Correctly framed as a demonstration, never a result; predicts CI ≈ 2.0× too narrow (`√3.93 = 1.98` ✓); and mandates disclosure if the event-level CI would flip the verdict. Exemplary. |

Plus C4 (lag profile), C5 (artifact veto), C6 (motor-ID scramble), C7 (split mutation → HALT), C8 (scale mutation).

### 7.1 The blind spot: **eight negative controls, zero positive controls**

**This is the most serious methodological gap after the D5 issue.**

Consider the single most likely implementation bug in this design: the lag-1 arrival join is wrong — off-by-one in the within-motor ordering, a silent `None` from the contiguity filter, or a merge that drops every arrival label. Such an estimator returns Δ ≈ 0 always. Walk it through the battery:

- **C1** (scramble → null centred on 0): **passes** — an always-zero estimator gives a null centred on 0.
- **C2** (reversal → sign flips, magnitude preserved to 1e-12): **passes** — `0 = −0`.
- **C3** (event bootstrap narrower): **passes** — both widths shrink toward 0.
- **C4** (lag profile): **passes**, and worse — a flat profile is explicitly *interpreted in §5 as scientific evidence* ("evidence against a first-order latent and for a motor-level or artifact explanation"). **A bug is converted into a finding.**
- **C5, C6, C7, C8**: unaffected or pass.

**An always-zero estimator passes all eight controls and emits `NOT_ESTABLISHED`, which is indistinguishable from the expected outcome.** The battery has zero power against the failure mode most likely to occur.

**Required addition:** a **positive control** — inject a synthetic Δ_mem of known magnitude (e.g. 0.92 log units) into holdout-shaped surrogate data with the real motor/state/arm structure, and require the estimator to recover it within tolerance at the claimed MDE. Without this, a null from E1 is uninterpretable.

### 7.2 Missing control: within-motor non-stationarity

There is **no control for time-varying covariates within a motor's recording.** Stratifying on `(motor, state)` removes the motor's *mean* level and the state composition; it does **not** remove within-motor drift. Wadhwa 2022 is a stator-remodelling-under-load-change experiment (`nominalElectrorotationSpeed` is recorded per motor at `ingest:130`, **CHECKED_AGAINST_CODE**). If load, PMF, or bead attachment drifts across a recording, then events with `arrival = on` (concentrated during the motor's climb in N) systematically differ from `arrival = off` events (concentrated during descent) — **at the same N, in the same motor, with no cross-event latent whatsoever.**

Add: stratify on `(motor, state, trajectory-half)`, or include the within-motor event index as a covariate, or permute arrival labels within time-blocks. Without it, explanation **(f) non-stationarity** is fully confounded with **(d) memory** and is not in the decision table at all.

### 7.3 E1-C1 is not computable as specified

**E1-C1** demands *"the observed-null 95% **coverage** within [0.93, 0.97]."* Coverage is a property measured over **repeated datasets**, not over repeated permutations of one dataset. Measuring it requires a bootstrap nested inside each permutation — 20000 × 20000 resamples. §7 costs "E1 primary + controls C1–C8" at **"minutes."** Either the coverage criterion means something undefined, or the cost estimate is off by orders of magnitude. Given established defect D2 (resource estimates already found overstated 17–29× in this repo), unsupported cost estimates are a live governance issue here — this one runs the other way.

---

## 8. CHECK 7 — IS IT DECISIVE? **NO. Brutally: it separates two of five explanations, and its veto control cannot do the job it exists to do.**

### 8.1 What the design does separate

Genuinely correct and well-argued: within-`(motor, state)` stratification does structurally neutralise **(c) motor heterogeneity** (the motor effect is exchangeable within its own events, so it cancels in every within-stratum contrast) and **(b) composition effects across states**. Δ_mem ≠ 0 surviving stratification really would falsify a memoryless-in-`N` Markov account. **That much is sound.**

Also correct: §1.3 registers the adverse discovery that plain serial correlation of durations is dead (`lag1 r = −0.0706`, `lag2 +0.0958`, `lag3 −0.1217`, sign-alternating, all within noise — **REPORTED_BY_TRACK**, TRAIN_ONLY per the track's own declaration; I did not recompute) and correctly refuses to make it the primary. Retaining a dead statistic as C4 rather than deleting it is exactly the discipline the operating contract demands.

### 8.2 Defect 1 — the veto control cannot distinguish the two hypotheses it exists to distinguish

**This is the central decisiveness failure.**

**E1-C5** has veto power: if Δ_mem loses >50% of its magnitude after excluding `dt < 0.460 s`, the signal is reassigned to **(e) segmentation artifact** and `MEMORY_SUPPORTED` is vetoed.

But **(d) a genuine mechanistic memory would plausibly live in short dwells too.** The repository's own gate `G07_H_STATE_REEXTRACTION` is about *"the 43 short hidden-state wells and the reported `k_h` and `k_-h`"* (**CHECKED_AGAINST_CODE**, `run-science-gates.py:468+`). A short-lived hidden intermediate state is a **named mechanistic hypothesis in this very repository**, and it predicts that the memory signal concentrates in exactly the short dwells C5 excludes.

So C5 is a **magnitude filter that both (d) and (e) predict will behave the same way**, and it is asymmetrically wired to veto. Under it:

- real short-lived latent → effect collapses → **vetoed as artifact** (false negative),
- segmentation flicker → effect collapses → vetoed (true negative).

**The control has ~100% power against (e) and ~0% specificity against a short-timescale (d).** A control that vetoes the hypothesis it is testing is not a discriminator.

C5(ii) — restrict to `|jump| = 1` — **is** a genuine artifact discriminator (merged/split segments produce `|jump| > 1`; a stator-kinetic mechanism should not care). It should be **promoted to the primary artifact control and C5(i) demoted to a reported sensitivity**. And C5(ii) must first exclude the D6-corrupted rows (§4.1), which are precisely large-`|jump|` fabrications.

### 8.3 Defect 2 — the decision table omits two live explanations

| explanation | in table? | predicts Δ_mem > 0? |
|---|---|---|
| (a) shape-only | yes | no |
| (b) state-dependent hazard | yes | no |
| (c) heterogeneity | yes | no |
| (d) policy/memory | yes | **yes** |
| (e) segmentation artifact | yes (added by track — good catch) | **yes** |
| **(f) within-motor non-stationarity** | **NO** | **yes** (§7.2) |
| **(g) boundary/cohort-edge effects** | **NO** | **yes** (below) |

**(g):** the cohort is states 1–8, but `ingest` admits states 0–11. An event at N = 8 whose predecessor was N = 9 carries `arrival = off` **derived from an event outside the cohort**; an event at N = 1 whose predecessor was N = 0 carries `arrival = on` likewise. §1.1 says arrival is *"defined only for events whose predecessor is contiguous and uncensored"* — it **never says whether the predecessor must be cohort-eligible**. This is not cosmetic: it changes the estimand, and it likely explains the unreconciled 215-vs-214 count in §4 (233 − 19 = 214 arrival-labelled rows if predecessors must be in-cohort; §4 reports 215). **The definition must be pinned before freezing, and the two variants will not give the same Δ_mem.**

At the boundary states the arrival label is *mechanically* correlated with position in the state range, and the state range is a **cohort-definition artifact**, not a physical boundary. This produces Δ_mem ≠ 0 with no memory.

### 8.4 Defect 3 — the "every model predicts exactly 0" claim proves too much

§1.2 is the load-bearing argument: *"**Every** model in the repository predicts Δ_mem = 0 **exactly**, for structural reasons."*

That is correct — **and it is the problem**. It means Δ_mem is not a *model discriminator*; it is a **goodness-of-fit residual test against the entire model class at once**. A rejection tells you all nine B3 models plus D-L-T plus the memoryless baseline are incomplete. It does **not** tell you *which* replacement class is right, because **(d), (e), (f), and (g) all predict the identical observable** — a positive stratified Δ_mem — and the protocol's only tool for separating them is E1-C5, which §8.2 shows cannot do it, plus C4's lag profile, which is confounded by the same drift that generates (f).

**So the answer to "would all four predict nearly the same observable?" is: yes for (d)/(e)/(f)/(g), and structurally-zero for (a)/(b)/(c).** The design cleanly separates *{a,b,c} vs {d,e,f,g}* and then **cannot separate within the second group** — which is the only group where a mechanism claim could live. The track is honest that (e) is live and gives it veto power; it does not see (f) or (g) at all.

### 8.5 What the design would actually license, at best

§6.1 states it correctly and I endorse it verbatim: a confirmed Δ_mem ≠ 0 licenses **exactly one** statement — *"a memoryless-in-N model is falsified for this dataset"* — and licenses **nothing** about F, G, policy priors `E`, precision `Π`, message passing, or active inference. §6.8's note that a positive Δ_mem is fully consistent with a two-conformation chemical stator model with no inference-theoretic content is correct and important.

Given the burned channel, even that statement is **retrospective-only** and raises **no P-level**. It is a within-P3 residual diagnostic on a re-used cohort, not new predictive evidence. The document's §3 headline framing ("Kills (b): Markov-in-N is then falsified regardless of how well D_b scores") is stronger than §6 permits, and §6 should govern.

---

## 9. VERDICT

**REJECT AS A MECHANISM DISCRIMINATOR. PARTIALLY SALVAGE.**

**Kill or hold:**

- **E1 primary (Δ_mem / Δ_exit / Π_mem / ICC) — DO NOT RUN as a verdict-bearing cell.** It rests entirely on the burned mark channel (§1), its verdict-bearing Bonferroni MDE (1.011) exceeds its own registered effect (0.923) (§6.3), joint power is ~23% at the optimistic effect and <5% at half of it, and its veto control cannot separate (d) from (e) (§8.2) while (f) and (g) are unmodelled (§8.3). Running it consumes the last usable read of a burned channel to buy a near-certain `NOT_ESTABLISHED`.
- **E1-S ladder — DO NOT RUN.** The track itself declares it *"expected to return NOT_ESTABLISHED for most or all rungs"*; §6.1's published intervals (8/8 INCONCLUSIVE, half-widths 0.042–0.165 nats) confirm it; and `D_a` is not M2, so the contrasts would be uninterpretable even if powered (§2).

**Salvage — one cell, after three repairs:**

- **E1-X (left-truncation repair)** is the highest-value item in the document and I endorse its #1 ranking independently: the omitted renormalisation is **0.012–0.086 nats/event** against an adverse gap of **0.037 nats** (§5.2), no competitor carries a truncation term (`grep "truncat"` → 0 hits), and B4C02's three generators structurally cannot detect it. **Required before running:**
  1. freeze `t_min = 0.300 s` from the **train** partition (verified available: TRAIN_ONLY min = 0.300 s, 22 events at the floor, 0.02 s grid) — as written it is holdout-contaminated;
  2. specify the correction in normalised `y`-space with state-dependent `y_min(N) = 0.300/scale_N(N)`, and state whether the mean-one constraint is imposed pre- or post-truncation — otherwise the refit is a different model family;
  3. replace the untestable *"narrows by more than half"* rule with a **paired** motor-cluster BCa contrast on `(M2−M3)_truncated − (M2−M3)_untruncated` under common random numbers, and name which estimand (motor-equal +0.025, or event-pooled +0.0369) is the target.
- **Propagate E0.1 immediately** to whichever track owns the target-stack blanket. The `p(N', direction, jump | ·)` triple-count is a real pre-implementation defect and is free to fix now (§5.1).

**Mandatory before any E1 cell is unfrozen:**

1. Relabel the entire protocol `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`; delete "genuinely unspent" from E0.5; record that §4's `150 on / 83 off` and the per-motor arrival vector are themselves holdout mark reads made during design (§1.3).
2. Add a **positive control** with an injected known Δ_mem — the current 8-control battery is passed in full by an always-zero estimator (§7.1).
3. Add a **within-motor non-stationarity control** and add explanations **(f)** and **(g)** to the decision table (§7.2, §8.3).
4. Pre-register exclusion of the **D6** `nextStateN = -1` holdout rows with counts declared; they land directly in Δ_mem, Π_mem, and the `|jump|=1` veto (§4.1).
5. Reconcile §2.2 (CMH event-weighted) with §4 (per-motor sd) and with B3's frozen `MOTOR_EQUAL` primary — pick one estimand (§3).
6. Drop the `build_bootstrap_cohort` import requirement (it resamples train, unfreezes `scale_N`, and is a no-op for the CMH contrasts); apply D1 discipline where it actually bites: **ICC** and `D_c` (§3.1).
7. Demote **E1-C8** to E1-S scope — `scale_N` cancels exactly in within-`(motor,state)` contrasts, so it is invariant by construction (§5.3).
8. Fix: §4's design-effect slip (3.68, not 3.9); the two-sided MDE table under one-sided registered tests (0.815, not 0.918); §2.1's 233/19 assertion versus §2.3's censoring-inclusive primary; §7's "minutes" cost against C1's nested coverage requirement.

**Standing constraints unchanged by anything in Track E:** M2_LOGNORMAL remains an adversarial baseline (§6.7 correctly says E1-X does not promote it). One study, no transfer set, raw MAT archive absent — P4 and P7 unreachable. B4C02 and B4C10 have not returned; nothing here anticipates their outcomes. **A design document is not evidence and raises no P-level.**