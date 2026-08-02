# B4C02 — Corrected Full-N Result Report

**Gate:** H-AIF-G5 · **Cell:** `B4C02_MISSPECIFIED_WORLDS` · **Lane:** **B** · **Date:** 2026-07-22
**Result:** `hierarchical-aif/results/motor_stack_aif/B4C02_CORRECTED_FULL_RESULT.json`
sha256 `0633988dbfd690c0c0d12075dba4e0d8c25ddd178125064bd01fbdaf4629e398`
**Prediction record:** `hierarchical-aif/protocols/B4C02-CORRECTED-FULL-PREDICTION.md`
**Maps to existing ladder:** constrains the *interpretation* of `P3`. **No P-level is raised.**

---

## 1. Executive result

B4C02 ran to completion at the **full frozen N = 200 simulations per generator, 600 total**, with
**zero failures** and `resourceBoundPartial: false`. `runStatus = ELIGIBLE_FOR_FROZEN_VERDICT`.

**Observed `gensWithM2overM3 = 1` of 3 → verdict `GENERATOR-SPECIFIC` → the frozen prediction
`GENERATOR-ROBUST_ADVERSE` is REFUTED at full N.**

By the outcome mapping committed in §6 of the prediction record, this means: **the adverse
M2-over-M3 result is NOT generic to heavy-tailed dwell shape.** `H_SHAPE_ARTIFACT` is **weakened**.
Per the committed interpretation, this *strengthens the case that the M2-vs-M3 contrast carries
mechanism-relevant information* — **but it establishes no mechanism by itself, and this report
makes no mechanistic claim.**

## 2. The three generators — full results

| generator (world) | m2 beats m3 | fraction | verdict vs 0.5 | modal winner |
|-|-|-|-|-|
| `weibull_gamma_blend` | 1 / 200 | **0.0050** | below | `M3_TWO_TIMESCALE` (81) |
| `three_timescale_heavy_tail` | 188 / 200 | **0.9400** | **above** | `M2_LOGNORMAL` (187) |
| `per_motor_heterogeneous_weibull` | 1 / 200 | **0.0050** | below | `M3_TWO_TIMESCALE` (82) |

`gensWithM2overM3 = #{generators with m2_beats_m3_frac >= 0.5} = **1**`. Frozen criterion:
`>= 2 of 3` → `GENERATOR-ROBUST_ADVERSE`; otherwise `GENERATOR-SPECIFIC`. **1 ≤ 1 → GENERATOR-SPECIFIC.**

### Full winner frequencies (200 sims each, 6 competitors)

| generator | M0 | M1 | M2 | M3 | M5 | M6 |
|-|-|-|-|-|-|-|
| `weibull_gamma_blend` | 34 | 27 | **1** | **81** | 28 | 29 |
| `three_timescale_heavy_tail` | 0 | 1 | **187** | 12 | 0 | 0 |
| `per_motor_heterogeneous_weibull` | 39 | 23 | **1** | **82** | 30 | 25 |

**The separation is extreme, not marginal.** M2 wins 187/200 under the three-timescale heavy-tail
world and 1/200 under each of the other two. This is not a threshold that was barely missed; two of
the three generators put M2's win rate at half a percent.

### What the pattern says, stated carefully

The one world in which the lognormal reliably out-predicts the two-timescale mixture is the world
whose truth is a **three-timescale heavy tail** — i.e. a process with *more* timescales than M3 can
express. Under a Weibull–Gamma blend or per-motor heterogeneous Weibull, M3 wins outright.

That is a **hypothesis-generating** observation about the simulated worlds, not a finding about the
real cohort. It is consistent with — and does **not** establish — the reading that the real data's
M2-over-M3 gap reflects unmodelled tail structure rather than generic shape. Distinguishing those
requires evidence this cell does not contain.

## 3. Provenance

| field | value |
|-|-|
| harness | `hierarchical-aif/scripts/run_c02_corrected_full.py` (corrected) |
| correction applied | **`D3_HASH_SEED_NONDETERMINISM` only** |
| frozen runner functions used | `b4._simulate_*`, `b4._build_cohort_from_events`, `b3.fit_simple_models`, `b3.fit_m6`, `b3.scoring_params`, `b3.nlpd_per_event`, `b3.aggregate_motor_equal` — all called through the **frozen** modules |
| `seed_base` | `20260802` — **unchanged** |
| cohort | `derived_eligible_1_to_8` |
| planned N / actual N | **200 / 200 per generator**; 600 total; **0 failures** |
| `resourceBoundPartial` | `false` |
| `runStatus` | `ELIGIBLE_FOR_FROZEN_VERDICT` |
| started / ended (UTC) | `2026-07-21T17:51:02Z` → `2026-07-22T02:01:15Z` |
| runtime | **29 409.1 s = 8.17 h** |
| stderr | 0 bytes |
| HEAD at launch | `17a2f0e18c09c762ab1cefe854c0d68698803eac` |
| python / numpy / scipy | 3.12.10 / 2.3.5 / 1.16.3 |
| result sha256 | `0633988dbfd690c0c0d12075dba4e0d8c25ddd178125064bd01fbdaf4629e398` |

**Determinism.** `PYTHONHASHSEED` was unset, and that is now irrelevant: the D3 fix replaces
`hash(gen_label)` with `seeding.stable_seed`, a SHA-256-derived integer. This run is reproducible;
a run of the committed cell would not have been, because the committed cell produces different
synthetic data on every invocation. **This run is therefore not bit-comparable to the committed
cell — it could not have been, and the prediction record said so in advance.**

**D2 note.** The recorded `RESOURCE_BOUND` reason claimed 150–250 h. The measured cost is
**8.17 h**, against the re-measured estimate of 8.7 h — an 18–31× overstatement in the original,
and the first cost estimate this programme has made that came in *accurate*.

## 4. Prospectivity — `SATISFIED`, with the one caveat stated

**This is the only cell in the current batch whose prediction was committed before its
observation.**

| fact | value |
|-|-|
| prediction record introduced in | `b9b5670`, **2026-07-21T22:44:31Z** |
| B4C02 result came into existence | **2026-07-22T02:01:15Z** |
| ordering | **prediction committed 3 h 17 min BEFORE the observation** ✓ |

**Caveat, stated rather than omitted.** The commit occurred **mid-run**. Reconstructing the
generator timeline from the recorded runtimes (`17:51:02Z` start; 11 227 s + 9 266 s + 8 916 s), at
the moment of commit `weibull_gamma_blend` had completed (fraction `0.0050`) and
`three_timescale_heavy_tail` was in progress with its progress counter visible in the log. So one
generator's outcome, and a trend in a second, were on disk when the prediction was committed.

That cuts **in favour of** the prediction's honesty rather than against it: with one generator
already failing the threshold and one trending above it, the committed prediction
`GENERATOR-ROBUST_ADVERSE` required the *third, entirely unobserved* generator to pass. It did not.
**The prediction was committed against the partial evidence available, not tuned to it — and it was
refuted.**

Graded: **`PROSPECTIVE_WITH_MID_RUN_COMMIT_CAVEAT`.** Compare B4C10 and the F-side scoring, both
`NOT_SATISFIED` (D9).

## 5. Prediction outcome, against the committed mapping

The mapping applied here is the one committed in §6 of the prediction record, not one selected
afterwards:

> `gensWithM2overM3 <= 1` → `GENERATOR-SPECIFIC` → **prediction REFUTED** — `H_SHAPE_ARTIFACT`
> weakened. "The adverse result is **not** generic to heavy-tailed shape. This **strengthens** the
> case that the M2-vs-M3 contrast carries mechanism-relevant information — but establishes no
> mechanism by itself."

| hypothesis | status after this run |
|-|-|
| `H_SHAPE_ARTIFACT` — the adverse result is generic heavy-tailed shape | **WEAKENED** at full frozen N |
| `H_MECHANISM_INFORMATIVE` — it reflects the specific generating mechanism | **strengthened, not established** |
| `H_NOT_ESTABLISHED` — generators do not separate the explanations | **ruled out at this N** — the separation is 0.0050 / 0.9400 / 0.0050 |

**I predicted `GENERATOR-ROBUST_ADVERSE` and was wrong.** That is the recorded outcome, and being
wrong in the pre-committed direction is the point of committing it.

## 6. Scope boundary — what this cell cannot do, reproduced from §7 of the prediction record

- It **cannot** establish biological parity, mechanism, or active inference.
- It **cannot** promote M2 to "the UNI model." M2 is an **adversarial baseline**.
- It **cannot** move `P6` structural/mechanistic on its own; it constrains the *interpretation* of `P3`.
- **M3 is not vindicated.** M3 winning under two synthetic worlds says nothing about M3 on the real
  cohort, where the held-out adverse result stands unchanged.
- **M4 / M7 / M8 are skipped by construction** (the cell's declared design — see D4), so this cell
  says nothing about the mixture, hierarchical, or KDE models.
- It says nothing about the F-side motor-stack model, which is **not entered** in this competition.
- These are **simulated worlds**. No result here is an observation of a bacterium. Nothing in this
  report may be labelled `OBSERVED`.

## 7. The real-data adverse finding is UNCHANGED

The retained B3 adverse result — `M2_LOGNORMAL` out-predicting `M3_TWO_TIMESCALE` by ≈0.0369 nats
event-pooled on held-out data — **stands exactly as before.** B4C02 does not overturn it, weaken
it, or explain it away. It changes only what may be *inferred* from it: the pattern is not a
generic consequence of heavy-tailed shape, so "it's just shape" is no longer an adequate account.

Independently, the F-side scoring run this session found `M2_LOGNORMAL` (`3.4093`) and
`M8_EMPIRICAL_KDE` (`3.4225`) still out-predicting the F-side motor stack (`3.4327`) on point
estimate, `NOT_ESTABLISHED` under CI. **Both adverse results are reported alongside this one, never
instead of it.**

## 8. Lane impact — scoped

| lane | impact |
|-|-|
| **LANE B** | C02 moves `NOT_RUN / RESOURCE_BOUND` → **full-N result with a frozen verdict**. D2's route is one cell from complete |
| **LANE A** | duration-only B3/B4 evidence **unchanged**. The B3 leaderboard, the adverse M2-over-M3 result, and every B3 interval are untouched |
| **LANE C** | **unaffected** — no mark field is read by this cell |
| **LANE D** | **unaffected** — the motor-stack AIF model is not entered in this competition |
| **LANE E** | **unaffected** — no parity receipt moves |

## 9. Limitations

- **Simulated worlds only.** Three generators do not span the space of plausible misspecification.
  A fourth world could behave like the third.
- **6 competitors, not 9.** M4/M7/M8 are skipped by design, so "M3 wins" means "M3 wins among the
  six entered."
- **Single cohort geometry.** Every simulated dataset is built on the `derived_eligible_1_to_8`
  cohort structure — 19 holdout motors — so the sampling noise of that geometry is inherited.
- **`m2_beats_m3_frac` is a win-rate, not an effect size.** A 0.94 win rate says how *often* M2
  wins under that world, not by how much, and no interval is attached to the per-generator
  fractions. The frozen criterion is a count over generators, and that is what is reported.
- Being refuted in the pre-committed direction is a **recorded outcome, not a defect**.

## 10. Gate status

| gate | status | receipt |
|-|-|-|
| **H-AIF-G5** | **B4C02 COMPLETE at full frozen N** — verdict `GENERATOR-SPECIFIC`, prediction `REFUTED` | this report; `B4C02_CORRECTED_FULL_RESULT.json` `0633988d…` |

Remaining under G5: **B4C11 running**; **B4C01 queued** (≈14.5 h measured budget).

---

`NEXT_ACT = commit protocols/B4C11-CORRECTED-FULL-PREDICTION.md BEFORE the running B4C11 result lands (time-limited, requires the human principal — it is the only way B4C11 becomes prospective); continue supervising PID 26756 (B4C11); recompute per-motor NLPD arrays for M4/M6/M7 from their frozen fitted params so they can be contrasted against the F-side candidate under the same paired motor-cluster bootstrap`
