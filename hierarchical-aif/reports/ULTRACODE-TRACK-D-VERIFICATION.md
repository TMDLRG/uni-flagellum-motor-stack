# TRACK D VERIFICATION — Independent Adversarial Check

**Verifier scope.** Read-only. Nothing created or edited. `audits/phase-c/**` and `audits/phase-d/**` never opened. No statistic, table, marginal, fit, or plot computed over any row of `experiments/data/wadhwa-2022-events.json` with `partition == "holdout"`. Every train-partition computation below was performed after a hard `sha256(motorId) % 5 != 0` filter applied before any other operation, and is labelled `TRAIN_ONLY`.

**Headline.** Track D's central verdict — *the full motor-stack AIF model is not identifiable on current Wadhwa data* — **survives independent check and is if anything understated**. But **six of its supporting receipts are wrong**, including two that its own key argument is built on. The document also contains one internal self-contradiction about which stages retain prospectivity, and its proposed module list contains three concrete contract hazards, one of which would silently move every NLPD by up to 0.45 nats while appearing to be a model improvement.

---

## 0. Receipt audit — what checked out, what did not

### 0.1 CONFIRMED

| Track claim | My verification | Label | Split boundary |
|---|---|---|---|
| F1 split `sha256(motorId)%5==0 → holdout`; `Cohort.__init__` HALTs on mismatch | `b3-model-competition-runner.py:89` (`sha256_mod5`), `:105-108` (halt `FAILED-SPLIT-MISMATCH`) | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| F2 eligibility excludes every right-censored event | `:109-110` — `elig = [e for e in events if (not e["rightCensored"]) and e["stateN"] in self.states]` | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| F3 B3 never reads `nextStateN`/`direction`/`jump` | Exhaustive field extraction over the runner returns exactly: `motorId`(11), `stateN`(14), `durationS`(7), `partition`(1), `rightCensored`(1) + 3 telemetry keys. **Zero** occurrences of `nextStateN`, `direction`, `jump` in all 1645 lines | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| F4 M6 is 8 independent per-state Weibull shapes, no kernel | `fit_m6` at `:445-465` loops `for s in cohort.states`, fits a 1-D box `(0.05,5.0)` per state, `m6_logpdf_perstate = m1_logpdf`. No transition term exists | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| F6 109 motors with events → 109 censored events, all terminal | `ingestion.exclusions` = `{leftTruncated:129, rightCensored:109, outOfRange:3, zeroOrNeg:0}`; `motorCount:129`, `eventCount:1349`, `uncensoredEventCount:1240` ⇒ 109 censored events, one per each of the 109 motors with ≥2 runs. Ingest appends the terminal censored dwell unconditionally (`ingest-wadhwa-data.py:64-76`) and does **not** `continue` past it | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| F8 cohort counts 793/80 train, 233/19 holdout; 818/80 and 251/19 | `b3-model-competition-result.json → cohorts.*.summary` reproduces all eight integers exactly | CHECKED_AGAINST_RESULTS | HOLDOUT_ALREADY_SPENT_DURATION_ONLY (published) |
| F9 train events/motor: min 1, median 7, mean 9.9, max 70; 22 < 5; 55 < 10 | Recomputed: min 1, median 7.0, mean 9.9125, max 70; 22 motors < 5; 55 < 10. Exact | CHECKED_AGAINST_CODE | TRAIN_ONLY |
| F10 leaderboard span 0.1387 nats (M0 3.5480 → M2 3.4093); M3 at 3.4343; widest contrast 0.3289; all 8 motor-equal contrasts INCONCLUSIVE | All exact. Span = 3.54798328 − 3.40931416 = 0.13866913. M0 width 0.32889593. 8/8 INCONCLUSIVE | CHECKED_AGAINST_RESULTS | HOLDOUT_ALREADY_SPENT_DURATION_ONLY |
| F11 `nominalElectrorotationSpeed` 7 levels, per-motor constant, no timing; B4C06 3400 = `BLOCKED_EXTERNAL` | Train motors carry exactly 7 levels `{50,100,150,200,250,272,300}`; field lives on `motors[]` not `events[]`, so it has no timing. `B4C06.analysisStartIndex.3400.status == "BLOCKED_EXTERNAL"`, raw `c14de12c…` absent | CHECKED_AGAINST_CODE + CHECKED_AGAINST_RESULTS | TRAIN_ONLY |
| §1.10 calibration target M1 = `3.4333068483897238` | Exact match in `leaderboards.NLPD_motor_equal.motorEqual` | CHECKED_AGAINST_RESULTS | HOLDOUT_ALREADY_SPENT_DURATION_ONLY |
| §1.11 target M3-vs-M2 BCa `[−0.04369843…, +0.08676352…]`, width `0.12847493…`, INCONCLUSIVE | Exact match in `contrasts.NLPD_motor_equal.M2_LOGNORMAL` | CHECKED_AGAINST_RESULTS | HOLDOUT_ALREADY_SPENT_DURATION_ONLY |
| §1.12 adverse M2−M3 gap `0.0369` event-pooled | `adverseLognormalRetention.derived_eligible_1_to_8.lognormalMinusMixtureLogDensity = 0.03686651825627818` | CHECKED_AGAINST_RESULTS | HOLDOUT_ALREADY_SPENT_DURATION_ONLY |
| §3.1 quote "does NOT establish … that the organism performs the inference" | Verbatim in `notEstablished[0]` | CHECKED_AGAINST_RESULTS | NO_DATA_ACCESS_NEEDED |
| Ladder map citations (P5 `NOT_ESTABLISHED` line 77, P6 weakened line 78, P8 `FULL_PARITY=false` first unsatisfied `P4` line 80, six-condition rule 59-66) | All four verbatim | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| S0's censoring motivation: 26.1 % of normalized exposure; Weibull shape 0.6251 → 0.5852; exponential rate 1.000 → 0.739; uncensored median 2.32 s | Recomputed independently: censored share of normalized exposure = **0.2607**; mean-one Weibull shape **0.624971 → 0.585122** (Δ = 0.0398, grid 2e-4); mean-one exponential rate **1.000000 → 0.739312**; uncensored median **2.3200 s**. All confirmed | CHECKED_AGAINST_CODE | TRAIN_ONLY |
| S1 support: train `on`: 544, `off`: 249 | Exact | CHECKED_AGAINST_CODE | TRAIN_ONLY |
| S2: "training jump support stops at +4" | Train eligible jump support = `{−4:2, −3:6, −2:35, −1:206, +1:395, +2:128, +3:16, +4:5}`. Max = +4. Confirmed | CHECKED_AGAINST_CODE | TRAIN_ONLY |
| Established fact: F, G, policies, E, Π, up/down messages absent from science pipeline | Independent grep for `expected_free_energy`, `variational_free_energy`, `policy_posterior`, `free_energy` across `audits/phase-b/*.py`, `scripts/*.py`, `lib/*.js`: **zero hits** | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |
| Cited module line numbers (`_bridge.py:16` `dont_write_bytecode`, `:57-65` `frozen_cohort`; `seeding.py:30-44` `stable_seed`; `status.py:49-59` `verdict_from_ci`; `bootstrap.py:73-96` `build_bootstrap_cohort`) | All correct within ±1 line | CHECKED_AGAINST_CODE | NO_DATA_ACCESS_NEEDED |

### 0.2 CONTRADICTED — six findings

**C1 — the narrowest B3 contrast is 0.0835 nats, not 0.1285. The resolution floor the whole document rests on is wrong by 54 %.**
`CONTRADICTED` / `HOLDOUT_ALREADY_SPENT_DURATION_ONLY`
Track F10 and §2.2, §2.3-reason-2, §5.5 and `compare.minimum_detectable_effect` (§1.11 test 5) all assert the narrowest 95 % BCa motor-equal contrast width is **0.1285 nats (M2)**, and derive a resolution floor of **≈ 0.064 nats**. Full sorted widths from `b3-model-competition-result.json → cohorts.derived_eligible_1_to_8.contrasts.NLPD_motor_equal`:

```
M4_MIXTURE_K3                    0.083461   <-- narrowest
M8_EMPIRICAL_KDE                 0.086377
M2_LOGNORMAL                     0.128475   <-- track called this the narrowest
M1_WEIBULL                       0.139926
M6_SEMI_MARKOV_STATE_DEPENDENT   0.155219
M7_HIERARCHICAL_MOTOR            0.157996
M5_GAMMA                         0.180140
M0_EXPONENTIAL                   0.328896
```

M4 and M8 are both narrower than M2. On the track's own half-width heuristic the floor is **0.0417 nats**, not 0.064. Consequence: §2.3's "factor of 2.6 below the noise floor" becomes a factor of **1.67**. The verdict direction survives (0.025 < 0.0417), but the margin is 36 % of what was claimed, and §1.11 test 5 would hard-code a wrong number into a proving test.

Separately, the half-width heuristic itself is not a minimum detectable effect. A 95 % CI half-width is the MDE at ~50 % power; the conventional 80 %-power MDE is `2.80·SE ≈ 1.43 ×` half-width. `minimum_detectable_effect(per_motor_ref, per_motor_chal, n_rep)` as specified takes **no power argument**, so it cannot compute an MDE at all — it can only return a half-width under a different name.

**C2 — §2.1's hidden-state kernel row contradicts its own formula; all three totals are understated.**
`CONTRADICTED` / `NO_DATA_ACCESS_NEEDED`
The table gives the kernel `q(z′|z,N)` the formula `S·K·(K−1)` and the value **8** at `S=8, K=2`. `8 · 2 · 1 = 16`. A `K`-state kernel conditioned on `(z, N)` has `K−1` free entries per `(z, N)` pair, i.e. 16. The three totals (72 / 104 / 184) are arithmetically consistent with the wrong 8 and are each low by 8.

**C3 — §2.1 omits the 8 per-state normalization scales, which are estimated from the training data.** *(this is the largest single count error)*
`CONTRADICTED` / `TRAIN_ONLY`
`b3-model-competition-runner.py:121-130` estimates `scale_N[s] = mean(durationS)` over **train uncensored** events per state, then normalizes `e["_y"] = durationS / scale_N[stateN]`. That is 8 free parameters fitted from the training split, and they carry the entire location structure — the proof is `B4C05 → treatments.a_frozen_exclusion.fitted.M0_EXPONENTIAL.trainNLL == 793` exactly, i.e. the mean-one exponential's training NLL equals the event count identically, because `scale_N` has already absorbed the per-state mean. `M0` is reported with `params: []` but is really an 8-parameter model.

Consequence: §1.3's proving test "*degenerate spec `n_hidden=1, mark="none", motor_effect_dim=0` reproduces M1's single free parameter, proving the counter is calibrated against a known model*" **calibrates the counter against a wrong reference**. M1 has 1 + 8 = 9 fitted parameters. A counter that passes that test is miscalibrated by construction, and every downstream count inherits the error.

Corrected totals (C2 + C3 together), same instantiation `S=8, K=2, |Π|=4, d=1`:

| | track | corrected |
|---|---|---|
| direction-mark stack | 72 | **88** |
| jump-mark (geometric) | 104 | **120** |
| jump-mark (saturated) | 184 | **200** |

**C4 — S4's data-support figures are computed on a different cohort than S4 is defined on, overstating support by ~33 %.**
`CONTRADICTED` / `TRAIN_ONLY`
§4-S4 claims "61 distinct `(state, next)` transitions observed in training, 35 with ≥ 5 observations, 28 with ≥ 10." On the frozen `derived_eligible_1_to_8` cohort (train, uncensored, states 1–8) the counts are **46 distinct, 27 with ≥ 5, 23 with ≥ 10**. The track's 61/35/28 reproduce exactly when the state restriction is dropped (train, **all** states 0–11). S4 is explicitly scoped to the `1..8` cohort, so the figures motivating it belong to a cohort S4 does not use. Not fabricated — mis-scoped, and it inflates the apparent feasibility of the kernel.

**C5 — "19 holdout motors spread over 7 load levels (6/6/3/2/2/2/2)" sums to 23, not 19.**
`CONTRADICTED` / `NO_DATA_ACCESS_NEEDED`
§3.1 row (ii) and §5.4. `6+6+3+2+2+2+2 = 23`. `experiments/data/wadhwa-2022-events.json → ingestion.holdoutMotorCount == 23`; the B3 cohort has 19 because 4 holdout motors contribute no eligible uncensored 1–8 event. The distribution and the motor count are from two different populations, presented as one. The qualitative conclusion (≤ 3 motors per level at the thin end) is unaffected and is if anything worse at n=19.

**C6 — the S0 median-censored-duration figure does not reproduce.**
`CONTRADICTED` / `TRAIN_ONLY`
§4-S0 and §5.2 claim "censored dwells have median **83.4 s**" and "median censored duration 36× the median uncensored". Recomputed on train: median censored duration over the eligible `1..8` states = **85.46 s** (n=43); over all train censored events = **94.34 s** (n=89). Neither is 83.4. The 36× ratio survives (85.46 / 2.32 = 36.8×). I did **not** test whether 83.4 is the median over the *pooled train+holdout* censored set — that would require computing over holdout rows. `NOT_CHECKED — would require holdout access; requires prospective record first.` If it turns out to be the pooled figure, that is an additional undisclosed holdout read beyond the three disclosed in §5.1.

### 0.3 Internal self-contradiction

**X1 — §5.1's own disclosure invalidates §5.1's own exemption list.**
`CHECKED_AGAINST_CODE` (the document is the artifact) / `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`
§5.1 discloses three holdout computations, the third being "*the identities of the 5 zero-support holdout mark events (§4, S2)*". Two sentences later it concludes: "*S0, S2, S3 and S4 are unaffected — their motivating numbers above were computed on training data only.*" S2's entire blocker — the five eventIds, the claim that holdout jump support reaches +5, and the `−∞`/HALT argument — is a **holdout mark-channel derivation**, disclosed in the same section that declares S2 unaffected. **S2 must be listed alongside S1 and S1b as `RETROSPECTIVE / EXPLORATORY` on this holdout.** I did not verify the five eventIds or the "+5" support claim: `NOT_CHECKED — would require holdout access; requires prospective record first.` (Train max jump is +4, verified — so the "+5" claim is *only* derivable from holdout.)

---

## Q1 — Is the full motor-stack AIF model identifiable on current Wadhwa data?

**Status: `NOT_IDENTIFIABLE_CURRENT_DATA`.** `CHECKED_AGAINST_CODE` + `CHECKED_AGAINST_RESULTS` / `TRAIN_ONLY` for the training-side counts, `HOLDOUT_ALREADY_SPENT_DURATION_ONLY` for the resolution ceiling.

I agree with Track D's verdict and reach it with a stricter count.

### Explicit parameter count vs data count

Instantiation `S=8` occupancy states, `K=2` hidden kinetic states, `η_m` 1-D lognormal random effect, `|Π|=4`, 6 levels — Track D's own spec, with C2 and C3 repaired.

| Level | Block | Formula | dir-mark | jump geom. | jump sat. |
|---|---|---|---|---|---|
| Lmotor-0 | per-state normalization scale `s_N` **(omitted by track, C3)** | `S` | 8 | 8 | 8 |
| Lmotor-1 | hazard shape `k_{N,z}` | `S·K` | 16 | 16 | 16 |
| Lmotor-1 | hazard scale (mean-one removes `S`) | `S·K − S` | 8 | 8 | 8 |
| Lmotor-2 | kernel `q(z′\|z,N)` **(corrected, C2)** | `S·K·(K−1)` | **16** | **16** | **16** |
| Lmotor-2 | initial `q(z₁\|N)` | `S·(K−1)` | 8 | 8 | 8 |
| Lmotor-0 | direction mark `p(dir\|N,z)` | `S·K` | 16 | 16 | 16 |
| Lmotor-0 | jump magnitude | `S·K·2` / `S·K·7` | — | 32 | 112 |
| Lmotor-4 | `η_m` scale `τ` + loading | `1+d` | 2 | 2 | 2 |
| Lmotor-5 | `Θ` hyperprior | `≥2` | 2 | 2 | 2 |
| policy | `ln E(π)` | `\|Π\|−1` | 3 | 3 | 3 |
| policy | precision `γ` | 1 | 1 | 1 | 1 |
| Lmotor-0 | sensory precision `Π` per channel | 3 | 3 | 3 | 3 |
| all | per-level clocks | `6−1` | 5 | 5 | 5 |
| | **TOTAL** | | **88** | **120** | **200** |

**Data count.**
- Fitting: 793 uncensored eligible training events (836 records if S0's censoring-complete likelihood is adopted), on **80** training motors. Note that 106 train motors exist in `motors[]` — 26 contribute no eligible event, so 26 `η_m` would be prior-only.
- Discrimination: **19** holdout motors / 233 holdout events. `TRAIN_ONLY` for the first, published-artifact for the second.
- Events per free parameter: **9.0** (direction), **6.6** (jump geometric), **4.0** (jump saturated).
- Latents on top: `η_m` × 80 + `z_i` × 793 + `π_i` × 793 = **1666 latents against 793 observed events** (Track D's arithmetic here is correct).

**Information-content bound, which is the argument the track does not make.** Each event carries: one positive scalar `dt`; one bit of `direction`; and `jump` over 8 observed train levels ≤ 3 bits. Even the saturated stack's 200 parameters are being asked to absorb ≈ 793 × (1 continuous + ≤ 4 bits). But the binding constraint is not fitting — it is *discrimination*, and the experimental unit there is the **motor**, of which there are 19 held out. A model with 200 parameters compared on 19 units is not underpowered by a factor; it is categorically outside the regime where a CI-bound verdict other than `NOT_ESTABLISHED` can be produced.

**The decisive empirical bound.** Nine models spanning 0 to ~8 effective free parameters plus a nonparametric KDE produce a total motor-equal spread of **0.1387 nats**, and **all 8** M3-contrasts are `INCONCLUSIVE` with the narrowest interval **0.0835 nats** wide (C1). `executionFindings[2]` states it directly: *"with 19 holdout motors every motor-equal M3-contrast interval contains zero."* Adding 80–200 parameters cannot be resolved on a holdout that cannot separate a 1-parameter Weibull from a 3-component mixture from a KDE.

---

## Q2 — Which parameters are identifiable, weakly identifiable, or not identifiable?

Per-block, with the evidence that decides each.

**`IDENTIFIABLE_WITH_CURRENT_DATA`**

| Parameter | Why | Label / split |
|---|---|---|
| `s_N`, the 8 per-state normalization scales | Sample means over 40–150 train events each; `B4C05.fitted.M0.trainNLL == 793` exactly shows they are pinned | CHECKED_AGAINST_RESULTS / TRAIN_ONLY |
| Single-state marginal hazard shape (`k_N` in a `K=1` model) | M1's shape 0.6250888 is stable to 1e-4 across the frozen-exclusion and naive-inclusion treatments' *structure*; my independent grid refit reproduces 0.624971 | CHECKED_AGAINST_CODE / TRAIN_ONLY |
| `p(direction \| N)` marginals, states 1–8 | Every state has both directions in train (`on` 544 / `off` 249); the thinnest per-state cell is well populated | CHECKED_AGAINST_CODE / TRAIN_ONLY |

**`WEAKLY_IDENTIFIABLE`**

| Parameter | Why | Label / split |
|---|---|---|
| `k_{N}` for high states (7, 8) | Per-state `s_N` estimated on the fewest events; `scale_N[8] = 24.52 s` is a mean over a heavily right-truncated sample carrying most of the discarded 26.1 % exposure | CHECKED_AGAINST_CODE / TRAIN_ONLY |
| `p(z′\|z,N)` kernel entries for rare transitions | 46 distinct `(state,next)` cells in the eligible cohort, only 23 with ≥ 10 observations (C4). The other 23 cells rest on ≤ 9 events each | CHECKED_AGAINST_CODE / TRAIN_ONLY |
| `η_m` scale `τ` | Fittable but flat. `B4C11.U2_profile.flatSetTauRange = [0.1133, 0.2331]`, `flatLogspan_raw_natural_log = 0.7213` — a 2-log-likelihood-unit flat set spanning a factor of ~2 in `τ`. And D1 withdrew the U4 bootstrap evidence; the ladder map records P6 as **weakened** | CHECKED_AGAINST_RESULTS / HOLDOUT_ALREADY_SPENT_DURATION_ONLY |
| `jump` magnitude law, low-`|jump|` cells | `{−1: 206, +1: 395, +2: 128}` are well populated; nothing else is | CHECKED_AGAINST_CODE / TRAIN_ONLY |

**`NOT_IDENTIFIABLE_CURRENT_DATA`**

| Parameter | Why |
|---|---|
| Per-motor `η_m` (all 80, and prior-only for the other 26 train motors) | Median 7 events/motor, 22 motors with < 5, 1 motor with a single event. A 1-D random effect on a heavy-tailed hazard cannot be recovered from 1–7 dwells. `CHECKED_AGAINST_CODE / TRAIN_ONLY` |
| Per-event `z_i` and any `K ≥ 2` kernel, **jointly with** the hazard shapes | Classical mixture label-switching plus scale/shape trade-off. The empirical proof is already in the artifact: M6 (8 shapes) and M3 (2-parameter mixture) and M4 (3-component mixture, 5 free) are mutually `INCONCLUSIVE` on holdout. `CHECKED_AGAINST_RESULTS` |
| Per-event `π_i` | See Q3 — structurally unidentified, not merely underpowered |
| `γ` (policy precision) | Structurally unidentified from passive data; see Q3 |
| Sensory precision `Π` per channel | Fully confounded with the hazard scale and the mark-model concentration. There is no repeated-measurement / replicate structure at the event level from which an observation-noise precision could be separated from process variance — every dwell is observed once |
| Per-level clocks (5) | The data have **one** clock: 0.02 s sampling (`sampleIntervalS = 0.01999999999998181`, uniform across train motors). Nothing in the derived dataset varies at a second timescale that could inform a per-level rate. `CHECKED_AGAINST_CODE / TRAIN_ONLY` |
| `Θ` hyperprior on `τ` | 80 motors informing a hyperprior whose first-level parameter `τ` is itself flat over a factor of 2 |
| Load-dependence of any of the above | 7 levels × ≤ 3 holdout motors per level, and no within-trace timing (F11, C5) |

---

## Q3 — Does adding a policy π improve testability, or only add unidentifiable capacity?

**Status: `NOT_IDENTIFIABLE_CURRENT_DATA`. Adding π adds unidentifiable capacity and, worse, adds a *labelling* risk with no compensating falsifier.** `CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

Testability requires that some setting of π change the predicted distribution of something recorded, in a way another setting does not. Grounded in the schema (verified: the event record has exactly 12 fields — `direction, durationS, enteredAtS, eventAtS, eventId, jump, motorId, nextStateN, partition, rightCensored, splitRemainder, stateN`), **every non-identifier field is an outcome**. There is no chosen quantity anywhere in `events[]`. In `motors[]` the only non-outcome is `nominalElectrorotationSpeed`, a per-motor constant with no onset time.

So `p(o_future | π)` cannot depend on π, and three things follow:

1. **`π_i` per event adds 793 latents that the likelihood is flat in.** If `G` is constant across policies, `q(π) = softmax(ln E)` and the data drop out of the policy posterior entirely — the marginal likelihood is unchanged by any `π_i`. This is not weak identification; the profile is exactly flat.
2. **`γ` is not identified even under the "policies index predictive hypotheses" reading.** Only the combination `ln E(π) − γG(π)` enters, and only up to an additive constant. Track D states this correctly in §3.3. See the API defect **V3** below — §1.6 test 5 states the *wrong* equivalence and would not prove it.
3. **The one thing π genuinely buys is negative.** Under reading (iii), `q(π) = softmax(ln E − γG)` is Bayesian model averaging under a nonstandard weight. Calling that a policy makes a model-averaging weight look like a behavioural choice. Track D identifies this correctly and `policies.PolicyKind.PREDICTIVE_HYPOTHESIS` with `is_evidence_bearing() == False` is the right structural response.

**Would π ever improve testability?** Only if it changed the *predictive* factorization on a channel that is scored. It does not: `score.py`'s per-event term is `−log p(o_i) + log s_{N_i}` over `{dt}` (± mark). Marginalizing a flat π out of that returns the same number. A stage that reported an improvement after adding π would be reporting an optimizer artifact.

**Net:** π adds ≥ 4 free parameters (`ln E` 3 + `γ` 1) and 793 flat latents, and buys zero discriminative power on a holdout whose entire resolvable range is 0.0417 nats. It should be built (as a typed refusal) and never fitted.

---

## Q4 — What does G mean for a passive observational dwell dataset?

**Status: `ORCHESTRATE_LEVEL_ONLY`.** `CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

I read `audits/phase-b/b3-model-competition-runner.py` in full-field terms and the event schema directly. What I found:

- The runner's **entire** interface to the world is `{motorId, stateN, durationS, rightCensored, partition}` (verified by exhaustive field extraction — see F3 above). There is no action, no control input, no time-varying covariate, no intervention flag, no experimenter variable of any kind reaching the model.
- The schema's remaining fields (`nextStateN, direction, jump, enteredAtS, eventAtS`) are *also* outcomes. Adding them (Track D's `events.py`) widens the observation space; it does not create an action space.
- `motors[].nominalElectrorotationSpeed` is the only manipulated quantity in the repository, it is a **per-motor scalar label** with no onset, and re-deriving its timing requires the raw MAT, which is `BLOCKED_EXTERNAL` (`B4C06.analysisStartIndex.3400`, `rawSha256 c14de12c…` absent).

So, precisely: **`G(π)` has a well-defined mathematical value here and a null empirical one.** `G(π) = KL[q(o_f|π) ‖ p(o_f|C)] + E_q[H[p(o_f|z_f,π)]]`. Both terms are computable. Both are constant in π, because there is no π on which `q(o_f|·)` conditions. A `G` number emitted for `wadhwa-2022-events` would be a real number with no falsifier attached to it.

**What a "policy" could range over, exhaustively, given the actual schema:**

| Candidate π | Well-defined? | What it would range over | Verdict |
|---|---|---|---|
| Agent action sequence | Yes | **Nothing** — no field is chosen | Not instantiable. The set is empty, not small |
| Experimenter load protocol | Yes | 7 values of `nominalElectrorotationSpeed` | Not testable: constant per motor, no onset time, raw archive `BLOCKED_EXTERNAL`, ≤ 3 holdout motors at the thin levels (C5) |
| The motor's own stator-exchange trajectory `z_{1:n}` | Yes | Hidden-state paths | **Category error and a truth-contract hazard.** Scoring `G` over `z` asserts the organism performs the inference — precisely what `notEstablished[0]` disclaims. This is the reading that would produce "G proves motor agency" |
| Index over predictive hypotheses (models) | Yes | The 9 B3 models, or a `StackSpec` set | Bayesian model averaging under a nonstandard weight. Legitimate as *inference*, illegitimate as *active inference* |
| Analyst's next experiment | Yes | Experiment designs | **This is the only live reading.** See Q5 |

Track D's §3 reaches the same conclusion. I confirm it independently and add that the failure is structural (empty action set), not sample-size-limited — so no amount of additional Wadhwa-2022 data would fix it.

---

## Q5 — Is G testable with current data, or ORCHESTRATE-level only?

**Status: `ORCHESTRATE_LEVEL_ONLY` for the analyst-facing use; `DESIGN_ONLY_UNTIL_INTERVENTION` for any biological claim.** `CHECKED_AGAINST_CODE` + `CHECKED_AGAINST_RESULTS` / `NO_DATA_ACCESS_NEEDED`

**Not testable as a motor claim.** The falsifier does not exist. `status.verdict_from_ci` refuses a point estimate and demands an interval; there is no contrast that could produce one, because there is no π-varying quantity to contrast.

**Genuinely usable at the ORCHESTRATE level.** `G` over *experiment designs* is well-posed and the ingredients are already in the repository:
- **Ambiguity** `E_q[H[p(o|z,π_design)]]` — the expected residual entropy of a design, computable from the frozen fits' posterior predictive.
- **Risk** `KL[q(o|π_design) ‖ p(o|C)]` where `C` encodes "designs on which competing models disagree" — the repository already quantifies disagreement: eight motor-equal contrasts all straddling zero, with widths ranging 0.083 → 0.329 nats. Expected information gain across designs is exactly the quantity that would rank "acquire the raw MAT for within-trace load timing" against "acquire a second study" against "add holdout motors."

This use is **model-selection bookkeeping for the analyst**, not a claim about the motor. It moves no P-level. It must never be reported in the same artifact scope as a motor claim, or the two readings of π will be conflated.

**Concrete recommendation, sharper than the track's.** `expected_free_energy.py` should not merely raise on `NO_ACTION_CHANNEL`; the `ActionChannel` dataclass should carry a `channel_role` field with exactly two admissible values, `MOTOR_ACTION` and `EXPERIMENT_DESIGN`, and `claim_guard` should refuse any artifact in which a `G` computed under `EXPERIMENT_DESIGN` appears alongside a motor-level P-level receipt. Track D's design leaves the ORCHESTRATE use undeclared, so an ORCHESTRATE-level `G` would flow through the guard unlabelled.

---

## Q6 — Minimum intervention/transfer data to make G a biological motor claim

**Status: `DESIGN_ONLY_UNTIL_INTERVENTION`.** `CHECKED_AGAINST_RESULTS` for the power arithmetic / `PROSPECTIVE_NEW_DATA_ONLY`

Two things must be supplied. Neither is optional; the first without the second gives an untestable design, the second without the first gives an underpowered one.

### (a) A recorded action channel with timing — the perturbation

**Perturbation.** A **within-trace step change in external load**, applied at an operator-chosen instant and recorded to the same 0.02 s clock as the stator trace. Concretely, for the Wadhwa electrorotation bead assay: hold a motor at `nominalElectrorotationSpeed = s₁` for a pre-step window, step to `s₂` at recorded time `t_step`, hold for a post-step window. Randomize `(s₁, s₂, t_step)` per motor from a **pre-registered** schedule so the intervention is exogenous to the motor's state.

Why this and not something else: it is the one manipulation the existing apparatus already performs (the 7 speed levels prove the actuator exists), and it acts on the mechanical variable the two-state remodeling hypothesis says the motor is tracking. It converts `nominalElectrorotationSpeed` from a per-motor label into a **time-stamped action channel** — which is the single missing schema element (Q4). Minimum new schema fields: `actionAtS`, `actionFrom`, `actionTo`, `actionScheduleId`, `preRegisteredScheduleSha256`.

**Second, weaker option if new wet-lab work is impossible:** recover `t_step` for existing traces from the raw MAT (`c14de12c…`). This lifts `B4C06` out of `BLOCKED_EXTERNAL` and *may* yield within-trace load changes retrospectively. It cannot support a randomized-intervention claim (no pre-registration, no exogeneity guarantee) and it would be `RETROSPECTIVE`, not `PROSPECTIVE`.

### (b) Enough motors — the power requirement, derived from this repository's own numbers

Back out the per-motor score-difference SD from the frozen contrasts. Narrowest interval (M4): half-width 0.0417 ⇒ `SE ≈ 0.0417/1.96 = 0.0213` ⇒ `σ_motor ≈ 0.0213·√19 = 0.093` nats. Widest (M0): `σ_motor ≈ 0.366` nats. Required `n = 7.85·σ²/δ²` (two-sided α=0.05, 80 % power):

| target effect δ (motor-equal nats) | n at σ = 0.093 | n at σ = 0.366 |
|---|---|---|
| 0.10 | 7 | 105 |
| 0.05 | **27** | **421** |
| 0.025 (the observed M3→M2 gap) | 108 | 1682 |

**Minimum concrete specification:**
- **≥ 60 motors held out** for the intervention contrast, and a training set of comparable size — i.e. **≥ 120 motors total**, roughly **6× the current holdout** and **1.5× the current 129-motor study.** Sixty holdout motors resolves δ ≈ 0.034 nats at σ = 0.093 and δ ≈ 0.13 at σ = 0.366; anything smaller cannot separate a `G`-driven prediction from `M2_LOGNORMAL`.
- **Paired within-motor design**, pre-step vs post-step on the same motor. This is the leverage: it cancels the between-motor variance that drives σ up to 0.366, and it is the only way to reach the 60-motor figure rather than the 400-motor one. It also makes `η_m` a nuisance rather than a target.
- **≥ 2 step directions** (load up and load down) per arm, so a monotone-drift confound is a testable alternative rather than an assumption.
- **Both load levels represented at ≥ 20 motors each.** The current 6/6/3/2/2/2/2 (C5) is unusable at the thin end regardless of total n.

**Measured response — the falsifier, committed before data.** `G` becomes a motor claim only if it makes a *risky prospective prediction that a non-AIF hazard model does not make*. The pre-registered contrast:

> Motor-equal joint NLPD on the post-step window, `[G-driven policy model] − [best B3-class hazard model refit on pre-step data + a step-indicator covariate]`, paired motor-cluster bootstrap over the ≥ 60 held-out motors, 95 % BCa. Pre-registered predicted effect and direction committed and hash-sealed before the post-step windows are unblinded. An interval containing 0 ⇒ `NOT_ESTABLISHED`.

The discriminating observable that makes this genuinely risky, rather than a curve-fitting exercise: **`G` predicts an anticipatory / ambiguity-reducing signature in the post-step dwell distribution that a reactive hazard model does not** — e.g. a transient over-representation of exploratory `z`-transitions in the first post-step window that decays as the ambiguity term falls, with the *decay rate* tied to the same `γ` that the pre-step data fixed. If `γ` must be refitted per step to keep the prediction alive, `G` has been falsified and the correct record is `CONTRADICTED`, not a retuned `γ`.

**Transfer (P4) is a separate, additional requirement.** One study (Wadhwa 2022), no independent dataset, ladder map line 76 `P4 NOT_ESTABLISHED`. Even a perfect intervention result on this apparatus establishes P5 within one study, not P4. `INDEPENDENT_TRANSFER_REQUIRED`.

---

## Module / API contract scan

Track D's design is unusually disciplined — the refusal-shaped API (`assert_no_latent_in_blanket`, `NotAScoreError`, `assert_action_channel_present`, `assert_point_estimate_is_not_a_verdict`) is the right architecture and I would keep almost all of it. The following would silently violate the contract if built as written.

### V1 — CRITICAL. `score.py`'s scale term is not frozen, and S0 as specified can move every NLPD by up to 0.45 nats while looking like a model improvement.

`CHECKED_AGAINST_CODE` / `TRAIN_ONLY`

§1.10 states the per-event score as `nlpd_i = −log p(o_i) + log scale_{N_i}`, and cites `b3-model-competition-runner.py:1046-1050`. But `scale_N` is defined at `:121-126` as the mean over **train uncensored** events per state. §1.4 (`hazard_survival.py`), §1.9 (`fit.py`) and §4-S0 all describe including the 43 censored training events in the likelihood, and **never mention `scale_N`**. There is no `assert_scale_frozen` anywhere in the proposed API.

If an implementer extends the training cohort to include censored events and lets `scale_N` follow — the natural reading of "refit with the censored events contributing `log S`" — here is the measured consequence (train-only recomputation, per-state):

```
state  scale_N (B3, train-uncensored)  scale_N (incl. censored)   Δ log scale  [nats added to every NLPD in that state]
  1              4.749153                    4.749153               +0.00000
  2              3.482609                    3.482609               +0.00000
  3              6.350886                    6.350886               +0.00000
  4              5.062716                    5.538293               +0.08978
  5              7.948454                    9.700400               +0.19919
  6             14.389919                   19.642520               +0.31117
  7             18.245270                   28.527607               +0.44697
  8             24.520584                   35.243567               +0.36277
```

**Up to +0.447 nats per event, purely from renormalization.** For scale: the *entire* nine-model leaderboard spans 0.139 nats, and the resolution floor is 0.042 nats. A silent `scale_N` shift is **3.2× the whole leaderboard** and **10× the noise floor**. §4-S0's stage table marks S0 "Comparable to B3 numbers? **yes** (same 233 events)" — same events is not sufficient; **same normalization** is the actual precondition, and it is nowhere stated.

**Required fix:** `ScoredChannelSet` must hash `scale_N` alongside the channel names, `score.leaderboard` must refuse to merge results with differing `scale_N` hashes, and `hazard_survival.event_loglik` must take `scale_N` as an explicit frozen input rather than reading it off a cohort. Without this, S0 — the one stage Track D recommends actually running — is the stage most likely to manufacture a false positive.

### V2 — `leaderboard` guards the channel set but not the density's dimension.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

§1.10: "*mark factors are unitless and add directly*" to a duration term that is a density in seconds. That is correct for a joint score on a fixed channel set, and the `ScoredChannelSet` hash correctly blocks cross-set merges. But the sum is not comparable across **mark models with different support cardinality** *within* the same declared channel set — a geometric jump law and a saturated 7-level categorical both declare `channels = {dt, jump}` and both hash identically, yet a saturated model's `log p(jump)` is bounded differently. `declare_scored_channels(names)` takes names only. It should take `(name, support_cardinality, family_tag)` triples so a support-rule change (§4-S2's unresolved (a)-vs-(b) choice) forces a new hash.

### V3 — `expected_free_energy.py` test 5 states a false equivalence; the test as written is unprovable.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

§1.6 test 5: "`(lnE, γ)` and `(lnE + cγG, γ)` give the same `q(π)` for any `c`". Check: `softmax(lnE + cγG − γG) = softmax(lnE + (c−1)γG)`, which equals `softmax(lnE − γG)` **only at `c = 0`**. The claim is false for every other `c`.

§3.3 states the *correct* invariance: `lnE′ = lnE + (γ′ − γ)G` with precision `γ′` reproduces `q(π)` — verify: `softmax(lnE + (γ′−γ)G − γ′G) = softmax(lnE − γG)` ✓. So §1.6 and §3.3 contradict each other, and §1.6 is the one that would be turned into code. A test written to §1.6's spec fails; the failure mode I'd expect is someone "fixing" it by loosening the tolerance, which converts the strongest anti-`γ`-reporting guard in the whole design into a vacuous assertion. **The test must assert the two-parameter family `(lnE + (γ′−γ)G, γ′)` over a grid of `γ′`, not a scalar `c`.**

### V4 — `claim_guard.FORBIDDEN` misses two of the contract's forbidden strings.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

The operating contract forbids **"flagellum solved"** and **"G proves motor agency"**. §1.12's `FORBIDDEN` tuple contains `"full flagellum solved"` — over-specified, so a substring scan for the listed entry misses the bare phrase "flagellum solved" — and contains **no entry at all** for "G proves motor agency". Given Q4's finding that the `π = z_{1:n}` reading is the live category error, the missing entry is the one that matters most. Also missing: `"awareness achieved"` is covered by the broader `"awareness"` ✓, but there is no entry for `"M2 is the UNI model"` variants beyond the exact string, and §1.12 test 1 tests only "casing and whitespace variants" — not substring containment. `check_text` should match on normalized substrings, and both missing phrases must be added.

### V5 — `compare.contrast` cites the wrong bootstrap object; §1.11 test 1 and §1.11's stated math are mutually exclusive as written.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

§1.11 says contrast bootstrap draws "come from `bootstrap.build_bootstrap_cohort` (`bootstrap.py:73-96`) so a motor drawn K times yields K exchangeable groups — the D1 fix." That is a **category error about which bootstrap this is**:

- `build_bootstrap_cohort` resamples **training** motors and rebuilds `train_by_motor` for **refitting** (`bootstrap.py:86-93`). Its own docstring scopes D1 to M7's `m7_train_nll`, and states M4/C10 is `UNAFFECTED`.
- B3's contrast bootstrap resamples the **19 holdout** motors with **frozen fits**: `bootstrap_index_matrix(19, n_rep)` at `:1448`, described at `:24` and `:1488` as "motor-cluster bootstrap over 19 holdout motors, FROZEN fits, common random numbers". It never touches `train_by_motor`.

Routing a held-out contrast through `build_bootstrap_cohort` would resample the wrong partition, re-derive `scale_N` per replicate (compounding V1), and make §1.11 test 1 — reproduce B3's BCa to 1e-9 — impossible. The correct citation for `compare.contrast` is B3's `contrast_bootstrap` / `bca_endpoints` (`:1145-1165`, `:1110-1143`); `build_bootstrap_cohort` belongs in `fit.py`'s parameter-recovery path, not `compare.py`.

Related, smaller: §1.11 test 1 asserts `verdict == "INCONCLUSIVE"` while §1.11's stated verdict source is `status.verdict_from_ci`, which returns `"NOT_ESTABLISHED"` (`status.py:24, 49-59`). Two vocabularies, one test. Declare the mapping explicitly or the test fails on a string compare.

### V6 — `free_energy.py` test 6 compares two different quantities on two different partitions.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

The vacuity test asserts "`−F` equals the marginal log-likelihood that `score.py` already computes, to 1e-10." But `score.py` computes a **held-out predictive** NLPD carrying the `+log scale_N` seconds-scale offset, while `−F` at the exact posterior is the **training** marginal log-evidence in normalized units. They are not the same number and should not agree. Worse, taken literally the test requires evaluating `F` on holdout blankets, which is a holdout access with no prospective record.

The *intent* — proving `F` adds no independent falsifiable content — is right and important. The correct assertion is: `−F(exact posterior)` equals the **training** log marginal likelihood computed by an independent quadrature, in normalized units, on train blankets only. Rewrite accordingly and label `TRAIN_ONLY`.

### V7 — `identifiability_budget` has a fixed verdict baked into its proving test.

`CHECKED_AGAINST_CODE` / `NO_DATA_ACCESS_NEEDED`

§1.3 test 3 asserts `identifiability_budget(...)["verdict"] == "NOT_IDENTIFIABLE_AT_THIS_N"` and says the test "fails loudly if anyone later widens the budget to manufacture a pass." Good intent, but the function signature takes `resolvable_halfwidth_nats` as a **caller-supplied argument**, so the verdict is whatever the caller passes in. Given C1 — the track passes in a number that is 54 % too large — this is not hypothetical. The half-width must be *derived* from the frozen `b3-model-competition-result.json` contrast widths inside the function, with the source contrast named in the returned dict, not passed by the caller.

### V8 — Things I would keep unchanged

`events.FIELDS` is **complete and correct**: the union of keys over all 1349 event records is exactly the 12 fields the tuple names (`CHECKED_AGAINST_CODE`, schema-key extraction only, no per-row values read). `blanket.assert_no_latent_in_blanket`, `FreeEnergy.as_score() → NotAScoreError`, `policies.PolicyKind.PREDICTIVE_HYPOTHESIS.is_evidence_bearing() == False`, `assert_point_estimate_is_not_a_verdict`, and the pseudoreplication guard in §1.10 test 4 are all correctly aimed and I found no defect in them.

---

## Verification limits — what I did not check, and why

| Item | Status |
|---|---|
| The 5 zero-support holdout mark eventIds (§1.1 test 4, §4-S2, §5.3) | `NOT_CHECKED — would require holdout access; requires prospective record first.` `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY` |
| "Holdout jump support reaches +5" | `NOT_CHECKED — would require holdout access.` Train max is +4 (verified), so +5 is derivable *only* from holdout |
| F7 "1238 of 1240 consecutive pairs contiguous; the 2 breaks in the affected holdout motor (D12-redacted)" | Partially checked. Train side is **959 / 959 perfect** on both `nextStateN[i] == stateN[i+1]` and `eventAtS[i] == enteredAtS[i+1]` (`TRAIN_ONLY`). Total pair count 1349 − 109 = 1240 ✓ arithmetically. The 2 breaks are holdout: `NOT_CHECKED — would require holdout access`; accepted as the given D6 fact |
| §5.1's three disclosed holdout statistics (0.0169 nats, −0.0204 nats, and their CIs) | `NOT_CHECKED — would require holdout access; requires prospective record first.` Not reproducible without re-burning the channel |
| Whether "83.4 s" (C6) is the pooled train+holdout censored median | `NOT_CHECKED — would require holdout access.` If it is, §5.1's disclosure is incomplete |
| Holdout load-level distribution `6/6/3/2/2/2/2` | `NOT_CHECKED` on holdout rows. The **sum** 23 was checked against the published `ingestion.holdoutMotorCount` (C5), requiring no row access |
| Outcomes of in-progress B4C02 and B4C10 corrected reruns | `NOT_CHECKED` — not returned. `B4C10` is recorded `RESOURCE_BOUND_PARTIAL` (100/2000 replicates) and `B4C02` `NOT_RUN`; nothing above depends on either |

---

## Bottom line

| Question | Verdict |
|---|---|
| Q1 full stack identifiable? | **`NOT_IDENTIFIABLE_CURRENT_DATA`** — 88 / 120 / 200 free parameters (not 72 / 104 / 184) against 793 train events on 80 motors, plus 1666 latents; and 19 holdout motors that already cannot separate a 1-parameter Weibull from a KDE |
| Q2 which parameters | 3 blocks identifiable, 4 weakly, 8 not — table in Q2 |
| Q3 does π improve testability? | **No.** `NOT_IDENTIFIABLE_CURRENT_DATA` — structurally flat likelihood in π, `γ` unidentified, +4 parameters and 793 flat latents for zero discriminative power |
| Q4 what does G mean here | Well-defined functional, **null empirical content**. Action set is empty, not small. Only surviving reading is π over *experiment designs* — `ORCHESTRATE_LEVEL_ONLY` |
| Q5 is G testable | **`ORCHESTRATE_LEVEL_ONLY`** for design ranking; **`DESIGN_ONLY_UNTIL_INTERVENTION`** for any motor claim. `expected_free_energy` must raise for `wadhwa-2022-events` |
| Q6 minimum data | Time-stamped within-trace load step at pre-registered `t_step`, paired pre/post design, ≥ 60 holdout motors (≥ 120 total), both step directions, ≥ 20 motors per level, with a hash-sealed prospective contrast against a step-indicator hazard baseline. Transfer (P4) remains separately `INDEPENDENT_TRANSFER_REQUIRED` |
| Track D's own verdict | **Correct, and understated.** But six receipts are wrong (C1–C6), one section contradicts itself (X1), and five API items would silently violate the contract if built as written (V1–V3, V5–V7). V1 is the dangerous one: it would inflate S0 — the only stage Track D recommends running — by up to 0.447 nats of pure renormalization, 10× the resolution floor |

No P-level moves. This document is a verification, not evidence. `M2_LOGNORMAL` remains an adversarial baseline out-predicting `M3_TWO_TIMESCALE` by 0.0369 nats event-pooled and 0.0250 nats motor-equal — retained and reported. `P8 FULL_PARITY = false`, first unsatisfied level `P4`.