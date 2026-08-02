# B4C01 — Corrected Full-N Prediction Record

**PROSPECTIVITY: decided by the commit graph, never by this sentence (D9).** This record does
not assert its own standing; the ordering is asserted by
`test_b4c01_prediction_was_committed_before_any_observation` and is recomputed from `git` on every
test run.

What *is* directly verifiable at the time of writing, and is all that is claimed here:
`B4C01` has **never been executed at any N**. The frozen artifact records `status: NOT_RUN`,
`actual_N: 0`; there is no smoke test, no partial run, and no result file for this cell anywhere in
the repository. If the commit graph then places this record ahead of the first B4C01 observation,
this cell will have the **cleanest** standing in the batch — B4C02's record was committed mid-run
and B4C11's at 210/2000 replicates, so both had partial evidence in existence, whereas here there
is none of any kind to have been influenced by.

**Gate:** H-AIF-G5 · **Cell:** `B4C01_SYNTHETIC_PARAMETER_RECOVERY` · **Lane:** **B**
**Defects routed:** `D3_HASH_SEED_NONDETERMINISM` (corrected here) · `D2` (cost re-measured) ·
`D4` (the frozen reason text is wrong about this cell's model set)

---

## 1. Purpose

B4C01 is the **correct-specification sanity floor**. It asks: when data are generated *from* a
competitor with its own frozen parameters, does the B3 pipeline (a) recover those parameters within
tolerance, and (b) let that model win its own competition more often than not?

It is the control that makes every other B4 cell interpretable. If the pipeline cannot recover a
model from its own synthetic data, no adverse or favourable result elsewhere can be trusted.

**It has never been run.** The frozen artifact records `NOT_RUN` with a `RESOURCE_BOUND` reason.

## 2. Planned run

| field | value |
|-|-|
| `planned_N` per generator (frozen `N_sim`) | **200** |
| generators | **5** — `M0_EXPONENTIAL`, `M1_WEIBULL`, `M2_LOGNORMAL`, `M3_TWO_TIMESCALE`, `M5_GAMMA` |
| total simulations | **1000** |
| `seed_base` | **20260801** (frozen) |
| cohort | `derived_eligible_1_to_8` (80 train motors / 19 holdout motors) |
| corrected harness | `hierarchical-aif/scripts/run_c01_corrected_full.py` |
| launcher | `hierarchical-aif/scripts/launch_B4C01_corrected_full.sh` |
| result path | `hierarchical-aif/results/motor_stack_aif/B4C01_CORRECTED_FULL_RESULT.json` |
| protocol version | `PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1` |

## 3. The one and only deviation: the D3 seeding fix

The committed `cell_C01` seeds each simulation with:

```python
rng = np.random.default_rng(seed_base + sim + hash(gen) % 100000)
```

`hash(str)` is randomized per process when `PYTHONHASHSEED` is unset, so the committed cell
**produces different synthetic data on every invocation** and can never satisfy a byte-determinism
gate. This is defect **D3**, identical in kind to the one corrected for B4C02.

The corrected harness substitutes `seeding.stable_seed(cell_id, base_seed, replicate_index,
protocol_version, cohort_id)`, a SHA-256-derived integer. **Nothing else changes.** Every science
function is still called through the frozen `b3`/`b4` modules:
`b4._simulate_from_model`, `b4._build_cohort_from_events`, `b3.fit_simple_models`, `b3.fit_m6`,
`b3.scoring_params`, `b3.nlpd_per_event`, `b3.aggregate_motor_equal`.

**Consequence, stated plainly:** because the seed derivation changes, this run is **not**
bit-comparable to a hypothetical run of the committed cell. It could not have been anyway — the
committed cell is non-deterministic by construction. This run is reproducible; that one was not.

## 4. Frozen criteria — unchanged, not restated loosely

True parameters are the **frozen B3 fits** on `derived_eligible_1_to_8`, read from
`audits/phase-b/b3-model-competition-result.json` (sha256 `5d7a0589…`):

| generator | true parameter(s) | frozen tolerance on median bias |
|-|-|-|
| `M0_EXPONENTIAL` | *(none)* | — (self-win only) |
| `M1_WEIBULL` | `k = 0.6250888335850175` | `0.1` |
| `M2_LOGNORMAL` | `sigma = 1.5783076101407152` | `0.1` |
| `M3_TWO_TIMESCALE` | `w = 0.3933559993214189`, `lambdaFast = 0.44485933051063775` (`log10 = -0.35177729607742336`) | `w`: `0.1`, `log10(lambdaFast)`: `0.2` |
| `M5_GAMMA` | `shape = 0.5115799798433341` | `0.15` |

**Verdict rule (frozen, verbatim from `cell_C01`):**

> `PASS` iff for **every** generator: `withinTolerance` **AND** `self_win_frac > 0.5`.
> For `M0_EXPONENTIAL` (no parameters) only `self_win_frac > 0.5` applies.
> Otherwise `NOT_ESTABLISHED`.

- Scoring: **motor-equal NLPD** on each simulation's own synthetic holdout.
- Competitors scored per simulation: **`M0`, `M1`, `M2`, `M3`, `M5`, `M6_SEMI_MARKOV_STATE_DEPENDENT`**.
- **`M4_MIXTURE_K3`, `M7_HIERARCHICAL_MOTOR`, `M8_EMPIRICAL_KDE` are SKIPPED by construction.**
  This is the cell's declared design and is recorded in its own output as a runtime concession.
- `withinTolerance` is judged on the **median** recovered parameter across simulations, i.e. it
  tests **bias**, not spread. A model could be wildly variable per simulation and still pass this
  criterion. **That is a real weakness of the frozen criterion and it is not being fixed here** —
  the frozen rule is applied as written, and the spread is reported alongside it.

### D4 — the frozen reason text is wrong about this cell

The frozen artifact justifies `NOT_RUN` with *"~1000 refits × ~15–25 min per **M4/M7-inclusive**
competition = ~250–400 h"*. **This cell does not fit M4 or M7.** The corrected reason
(`corrected_reasons.C01_REASON`) supersedes it for reporting; the frozen artifact is **not edited**.

## 5. Expected runtime — MEASURED, not asserted (D2)

The completed B4C02 run used the **same** per-simulation fit path (`fit_simple_models` + `fit_m6` +
scoring of the same 6 competitors):

```
B4C02 measured: 29 409.096617221832 s over 600 simulations = 49.015 s/sim
B4C01 projection: 1000 simulations x 49.015 s = 49 015 s = 13.62 h
```

This supersedes both the frozen 250–400 h claim (overstated ~18–29×) and the earlier 14.5 h
estimate derived from component timings. **The projection is anchored to a completed full-N run of
a structurally identical cell, not to a component estimate.** The harness will record its own
`secondsPerSim` so this projection is itself falsifiable.

## 6. Pre-committed outcome branches

| # | observed at full N | verdict | pre-committed consequence |
|-|-|-|-|
| **(a)** | every generator: `withinTolerance` **and** `self_win_frac > 0.5` | **`PASS`** | The frozen expectation is **CONFIRMED**. The B3 pipeline recovers correctly-specified models. This is a **sanity floor being met — it is not evidence for any mechanism, for M3, or for the motor-stack model.** It strengthens the *interpretability* of B4C02's adverse result by showing the pipeline is not systematically biased. |
| **(b)** | any generator fails **either** condition | **`NOT_ESTABLISHED`** | The frozen expectation is **REFUTED**. The failing generator(s) are named. **This does not automatically invalidate B3** — the correct reading depends on *which* condition failed and *which* model. A self-win failure among statistically near-equivalent nested models is a **power/identifiability** statement about the 19-motor holdout, not evidence of a coding defect. A parameter-recovery failure would be far more serious and would put `P1` for the affected fitter in question. **The report must distinguish these two cases explicitly.** |
| **(c)** | run incomplete / `n_sims < 200` | **`PARTIAL_RESOURCE_BOUND`** | No verdict. `status.classify_run` governs. Per D2, a partial run must never be reported as a status. |
| **(d)** | harness defect, non-finite density halt, or crash | **`FAILED_RUN`** | No verdict of any kind. Repair loop. A crashed run is not a scientific negative. |

## 7. Directional prediction — committed, and I expect to be wrong about the headline

**The frozen expectation is `PASS`. I predict `NOT_ESTABLISHED` (branch b).**

**Parameter recovery: I predict ALL FOUR parameterised generators pass `withinTolerance`.**
Maximum-likelihood estimates are consistent, the tolerances are generous relative to the parameter
scales (e.g. `0.1` on `k = 0.625` is 16%), and the criterion is on the **median** over 200
simulations, which suppresses per-simulation variance almost entirely.

**Self-win: I predict `M0_EXPONENTIAL` is the failure point, with `self_win_frac` in `[0.20, 0.50]`,
most likely `0.30–0.40`.**

*Mechanism for that prediction.* `M0_EXPONENTIAL` is **nested inside** `M1_WEIBULL` (`k = 1`),
inside `M5_GAMMA` (`shape = 1`), and is a degenerate limit of `M3_TWO_TIMESCALE`. When the truth is
exponential, those competitors fit it essentially as well; the only penalty they pay out-of-sample
is the estimation variance of one or two extra parameters, of order `p / 2n ≈ 0.0006` nats. That
signal is **far smaller than the sampling noise of a motor-equal score over 19 synthetic holdout
motors**. So the argmin over `{M0, M1, M5, M3}` is close to a coin toss among four
near-indistinguishable models, and `M0` must beat **all five** competitors simultaneously to
self-win. Near-random selection among ~4 equivalent models puts `self_win_frac` near `0.25–0.40`,
below the `0.5` threshold.

**Secondary risk: `M5_GAMMA`, `self_win_frac` in `[0.40, 0.70]`.** Gamma with `shape = 0.512` and
Weibull with `k = 0.625` produce very similar densities on this support; `M1` is its closest rival.

**Predicted ordering of `self_win_frac`, lowest to highest:**
`M0_EXPONENTIAL` < `M5_GAMMA` < `M3_TWO_TIMESCALE` < `M1_WEIBULL` < `M2_LOGNORMAL`.
I predict `M2_LOGNORMAL > 0.80` — `sigma = 1.578` is a distinctive heavy tail no competitor here
mimics well. I predict `M3_TWO_TIMESCALE` in `[0.50, 0.80]`, with `M2` its main threat: B4C02
showed `M2` beating `M3` in 94% of simulations from a *three*-timescale world, and a two-timescale
world is the adjacent case.

**What would make me wrong in the interesting direction.** If `M0`'s `self_win_frac` comes in well
above `0.5`, the out-of-sample penalty for unnecessary parameters is materially larger than
`p / 2n` at this sample size — which would say something useful about how sharply this design
punishes over-parameterisation, and would strengthen every B3 contrast.

## 8. Falsifier

- The **frozen prediction (`PASS`)** is falsified if any generator fails either condition.
- **My prediction is falsified item by item:** a `PASS` verdict; or `M0_EXPONENTIAL` with
  `self_win_frac > 0.5`; or any parameterised generator failing `withinTolerance`; or the predicted
  ordering of `self_win_frac` coming out different. Each is a recorded miss.

## 9. What this cell cannot do, whatever it returns

- It **cannot** establish biological parity, mechanism, or active inference. Every dataset here is
  **synthetic**; nothing in this cell may be labelled `OBSERVED`.
- It **cannot** promote any model to "the UNI model." `M2_LOGNORMAL` remains an adversarial baseline.
- A `PASS` **does not vindicate M3** and does not support the F-side motor-stack model, which is not
  entered in this competition.
- Because `M4`/`M7`/`M8` are skipped, this cell says nothing about the mixture, hierarchical, or KDE
  models.
- It **cannot** move `P6`. It speaks to `P0`/`P1` pipeline integrity and constrains the
  interpretation of `P3`.
- A `NOT_ESTABLISHED` driven by nested-model near-equivalence is a **power statement about a
  19-motor holdout**, not a defect finding. Reporting it as "the B3 pipeline is broken" would be a
  misreading, and is forbidden.

## 10. Wording

**Allowed:** "B4C01 at full frozen N supports / does not support parameter recovery and self-win
for the simple model set on synthetic data, within its frozen scope (5 generators, 6 competitors,
motor-equal NLPD, single 19-motor cohort geometry)." · "sanity floor met / not met" ·
"not established" · "power-limited at this holdout size".

**Forbidden as claims** (canonical list in `claim_guard.FORBIDDEN` and the H-AIF contract;
referenced, not re-transcribed, so a wrapped catalogue cannot read as an assertion): any parity,
mechanism, active-inference, or "solved" claim; "M2 is the UNI model"; "M3 is vindicated"; any
statement that this cell tests the motor-stack AIF model or the mark process.

## 11. Required pre-run checks

- Corrected harness reproduces the frozen generator list, order, and `seed_base = 20260801`.
- `stable_seed` substitutes **only** for `hash(gen) % 100000`; the `+ sim` term and every other
  arithmetic input are unchanged.
- True parameters are read from the frozen B3 artifact at run time, never hard-coded.
- Tolerances, the `> 0.5` self-win threshold, and the `PASS`/`NOT_ESTABLISHED` rule are unmodified.
- `M4`/`M7`/`M8` remain skipped and the omission is recorded in the result.
- **NO FLOOR** — a non-finite log density increments `failed`; it is never replaced or clipped.
- Frozen artifacts under `audits/**` are untouched; the harness only reads them.
- Deterministic JSON output (`indent=1, sort_keys=True`, LF) with a printed sha256.

## 12. NEXT_ACT

```text
NEXT_ACT = commit THIS record first (no B4C01 observation exists yet, so its prospective standing
           is clean); then build hierarchical-aif/scripts/run_c01_corrected_full.py, smoke-test it
           to a scratch path, and launch at the frozen N_sim = 200 x 5 generators
```
