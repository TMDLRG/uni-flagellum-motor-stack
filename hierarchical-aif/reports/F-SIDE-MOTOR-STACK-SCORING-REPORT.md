# F-Side Motor-Stack — Held-Out Scoring Result

**Gate:** H-AIF-G7 · **Lane:** **D** (motor-stack AIF) · **Date:** 2026-07-22
**Prediction record (WRITTEN before this run; NOT committed before it — prospectivity
`NOT_SATISFIED`, see §2 and D9):**
`hierarchical-aif/protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md`
**Result:** `hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json`
sha256 `b3b12720f32c0aee3bfa456f52ae0901976e59e3b43c0f2690fa7a17386ab297` (22 789 bytes)
**Maps to existing ladder:** `P3` held-out predictive, **duration-only scope**. **No P-level is raised.**

---

## 1. Executive result

The constrained F-side motor-stack model was fitted on the 80 training motors and scored on the 19
frozen holdout motors under the frozen motor-equal NLPD rule. **Outcome: pre-committed branch (B),
`NOT_ESTABLISHED`, against the control and against every serious adversary.** Two contrasts
resolved above zero, both against weak adversaries (`M0_EXPONENTIAL`, `M5_GAMMA`).

The single most important number in this report is not a contrast. It is this:

| quantity | value |
|-|-|
| F-side motor-stack, held-out motor-equal NLPD | `3.4326923382675303` |
| frozen `M7_HIERARCHICAL_MOTOR`, same quantity | `3.4326925889658892` |
| **difference** | **`2.5069835896118775e-07` nats** |

**The F-side model reproduces the incumbent hierarchical model to within 2.5e-7 nats. At the
resolution this study can achieve it is not a new model; it is a re-derivation of `M7`.** That is
the honest headline, and it is an adverse result for the hypothesis that the constrained motor
stack buys predictive power. It is also a strong implementation receipt: two independently written
hierarchies agree to 7 significant figures.

## 2. Provenance and integrity

| field | value |
|-|-|
| harness | `hierarchical-aif/src/motor_stack_aif/compare.py` |
| protocol | `hierarchical-aif/protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md` — **written** before execution; **NOT committed** before it. Prospectivity `NOT_SATISFIED` (D9): the protocol is untracked and the result already exists, so no commit can now precede the observation. This is a **retrospectively-graded** result against a pre-written prediction |
| cohort | `derived_eligible_1_to_8` — 80 train motors / 793 train events; 19 holdout motors / 233 holdout events |
| split | frozen `sha256_mod5(motorId) == 0 => holdout`. **Reused, not recomputed** |
| channel | **`DURATION_ONLY`.** `nextStateN` / `direction` / `jump` never requested (D5) |
| scale | **SECONDS** = normalised-`y` NLPD `+ log scale_N[state]`, matching frozen B3 |
| aggregation | MOTOR_EQUAL primary; experimental unit is the **MOTOR** |
| bootstrap | 2000 replicates, **resampling MOTORS**, single-construction RNG, seed `20260717`, common random numbers across contrasts |
| interval | **percentile** (labelled as such, per D7) |
| floor policy | **NO_FLOOR** — a non-finite log density halts |
| determinism | **PROVEN**: the full pipeline was executed twice and the canonical bytes compared — `BYTE_IDENTICAL=True` |
| runtime | 26.9 s and 27.3 s for the two executions |

### Independent-oracle consistency check — **PASS, residual exactly `0.0`**

B3 stores **only aggregated** scores; there are no per-motor arrays in the frozen record, so every
per-motor array here had to be recomputed. That is precisely why this check is mandatory and not
optional. Three frozen models were re-derived from their recorded parameters and compared against
their published motor-equal values:

| model | published | recomputed | residual | per-motor max abs diff |
|-|-|-|-|-|
| `M3_TWO_TIMESCALE` | `3.4343333330753589` | `3.4343333330753589` | **`0.0`** | `8.88e-16` |
| `M0_EXPONENTIAL` | `3.5479832810629599` | `3.5479832810629599` | **`0.0`** | `8.88e-16` |
| `M8_EMPIRICAL_KDE` | `3.4225236184063643` | `3.4225236184063643` | **`0.0`** | `8.88e-16` |

Tolerance `1e-12`, and the observed residual is exact zero. The harness **halts** rather than
warning if this check fails; it never proceeds to a verdict on an unvalidated scale convention.
This is what licenses the seconds-vs-normalised handling for every other model in the table.

## 3. Held-out leaderboard (motor-equal NLPD, seconds scale, lower is better)

| rank | model | motor-equal NLPD | role |
|-|-|-|-|
| 1 | `M2_LOGNORMAL` | `3.4093141583` | ADVERSARY |
| 2 | `M8_EMPIRICAL_KDE` | `3.4225236184` | ADVERSARY |
| 3 | **`F_MOTOR_STACK`** | **`3.4326923383`** | **candidate** |
| 4 | `M1_WEIBULL` | `3.4333068484` | ADVERSARY |
| 5 | `M3_TWO_TIMESCALE` | `3.4343333331` | **CONTROL_CURRENT** |
| 6 | `M5_GAMMA` | `3.4637286497` | ADVERSARY |
| 7 | `M0_EXPONENTIAL` | `3.5479832811` | ADVERSARY |

Placed into the **full frozen 9-model B3 leaderboard**, the F-side model would sit **5th of 9**,
between `M6_SEMI_MARKOV_STATE_DEPENDENT` (`3.4298889710`) and `M1_WEIBULL` (`3.4333068484`), and
below `M2_LOGNORMAL`, `M8_EMPIRICAL_KDE`, `M4_MIXTURE_K3` (`3.4241154309`) and `M6`.

**A point-estimate ranking is not a verdict.** The CI-bound verdicts follow.

## 4. Contrasts — CI-bound verdicts

Convention: `contrast = S(reference) - S(F_MOTOR_STACK)`. Interval entirely **above** 0 ⇒ the
F-side model is better; entirely **below** 0 ⇒ the reference is better; **contains** 0 ⇒
`NOT_ESTABLISHED`.

| reference | role | point | 95% percentile interval | half-width | verdict |
|-|-|-|-|-|-|
| `M0_EXPONENTIAL` | ADVERSARY | `+0.115291` | `[+0.013040, +0.227497]` | `0.1072` | **RESOLVED_ABOVE** |
| `M5_GAMMA` | ADVERSARY | `+0.031036` | `[+0.004459, +0.054473]` | `0.0250` | **RESOLVED_ABOVE** |
| `M3_TWO_TIMESCALE` | **CONTROL** | `+0.001641` | `[-0.077147, +0.080849]` | `0.0790` | `NOT_ESTABLISHED` |
| `M1_WEIBULL` | ADVERSARY | `+0.000615` | `[-0.010881, +0.011304]` | `0.0111` | `NOT_ESTABLISHED` |
| `M8_EMPIRICAL_KDE` | ADVERSARY | `-0.010169` | `[-0.084506, +0.064475]` | `0.0745` | `NOT_ESTABLISHED` |
| `M2_LOGNORMAL` | ADVERSARY | `-0.023378` | `[-0.104886, +0.067038]` | `0.0860` | `NOT_ESTABLISHED` |

**Branch determination, per the pre-committed table:**

- **Not branch (A).** Branch A required the interval against the control **and every** adversary
  to lie entirely above 0. Four of six contain 0.
- **Branch (B) is the governing outcome** for the control and for all three serious adversaries
  (`M2`, `M8`, `M1`). `NOT_ESTABLISHED` — **this is not equivalence and not "no difference."**
- **Not branch (C).** No adversary's interval lies entirely below 0, so `H_FSIDE_DURATION` is
  **not falsified** either. `M2_LOGNORMAL` and `M8_EMPIRICAL_KDE` lead on point estimate but their
  intervals cross 0.
- Two contrasts **resolved above 0** against the two weakest adversaries. Beating a unit
  exponential and a gamma is a floor check, not a scientific claim.

### The `M1_WEIBULL` contrast is the informative one

`M1` is the `tau -> 0` nesting control: it is exactly what the F-side model collapses to if the
population spread does no work. The contrast is `+0.000615` nats with a half-width of `0.0111` —
the tightest contrast in the table, and centred essentially on zero. **The entire hierarchical
apparatus — a population prior over log-shape with per-motor latents integrated by 33-node
Gauss-Hermite quadrature — buys approximately nothing over a single pooled Weibull on held-out
duration prediction at this sample size.** The fitted `tau = 0.1837` is small, consistent with
that reading.

## 5. Prediction scorecard — the pre-committed §8 predictions, scored

The prediction record committed eight specific claims before the numbers existed. Scored honestly:

| # | prediction | observed | outcome |
|-|-|-|-|
| 1 | point in `[3.425, 3.442]`, within ±0.005 of `M7` `3.4326925889658892` | `3.4326923383`; `|Δ|` vs M7 = `2.51e-07` | **HIT** |
| 2 | vs `M0` ≈ `+0.115` → `RESOLVED_ABOVE` | `+0.115291`, `RESOLVED_ABOVE` | **HIT** |
| 3 | vs `M3` control, `|contrast| < 0.010` → `NOT_ESTABLISHED` | `+0.001641`, `NOT_ESTABLISHED` | **HIT** |
| 4 | vs `M1`, `|contrast| < 0.005` → `NOT_ESTABLISHED` | `+0.000615`, `NOT_ESTABLISHED` | **HIT** |
| 5 | vs `M2` ≈ `-0.024` → `NOT_ESTABLISHED` | `-0.023378`, `NOT_ESTABLISHED` | **HIT** |
| 6 | vs `M5` ≈ `+0.031` → **`NOT_ESTABLISHED`** (below the floor) | `+0.031036`, **`RESOLVED_ABOVE`** | **MISS on the verdict** (point estimate hit to 4e-5) |
| 7 | vs `M8` ≈ `-0.010` → `NOT_ESTABLISHED` | `-0.010169`, `NOT_ESTABLISHED` | **HIT** |
| 8 | strongest adversary = `M2_LOGNORMAL` | `M2_LOGNORMAL` | **HIT** |

**Seven of eight, with one recorded miss.** The miss is item 6 and it is methodologically
instructive, so it is not buried:

> The `M5_GAMMA` contrast **resolved** with a half-width of `0.0250`, well **below** the ~`0.042`
> nat resolution floor the protocol used as its rule of thumb. The floor is a *heuristic derived
> from the narrowest frozen B3 contrast*, not a bound. A contrast can resolve below it when the
> per-motor difference is unusually **consistent in sign** across motors, because the paired
> motor-cluster bootstrap is sensitive to consistency, not just magnitude. The protocol's §10
> anticipated this in words ("unless the per-motor difference is unusually consistent") but §8
> still predicted the wrong verdict. **Recorded as a miss.**

**Calibration caveat, stated so the scorecard is not over-read.** The prediction was formed with
the frozen *published* holdout scores of the competitors already in hand (legitimately — that
channel was spent by B3). Given a predicted F-side point location, most contrasts follow by
arithmetic. The genuinely risky commitment was item 1, the point location itself, and the reason it
landed to `2.5e-7` is the finding of §1: the F-side model and `M7` are the same model to this
resolution. **The scorecard measures the reasoning, not new evidence.**

## 6. Adverse results — retained, in the headline

1. **`M2_LOGNORMAL` out-predicts the F-side motor stack on point estimate** (`3.4093` vs `3.4327`,
   contrast `-0.023378`). The interval crosses 0, so this is `NOT_ESTABLISHED`, **not** a
   refutation — and equally **not** a defence. The standing B3 adverse finding (M2 over M3 by
   ~`0.0369` nats event-pooled) is **extended, not overturned**: a two-parameter lognormal remains
   the best point performer on this cohort, ahead of every mechanistic candidate including this one.
2. **`M8_EMPIRICAL_KDE`, a purely empirical model with no mechanism at all, also out-predicts the
   F-side motor stack on point estimate** (`3.4225` vs `3.4327`).
3. **The hierarchy buys nothing measurable over `M1_WEIBULL`** (§4).
4. **The F-side model is not distinguishable from the incumbent `M7`** (§1).
5. `M2_LOGNORMAL` is an **ADVERSARIAL BASELINE, never the UNI model.** Its performance is retained
   as an adverse result about the mechanistic candidates, not promoted to a claim about lognormal
   mechanism.

## 7. What this establishes, and what it does not

**Establishes (scoped):** on the `derived_eligible_1_to_8` cohort of this single passive dataset,
at 19 holdout motors, under motor-equal NLPD on the seconds scale, the constrained F-side motor
stack predicts held-out **durations** better than `M0_EXPONENTIAL` and `M5_GAMMA` by a CI-bound
margin, and is `NOT_ESTABLISHED` against the current design and against every serious adversary.
The implementation is deterministic, censoring-correct, no-floor, motor-equal, and reproduces three
frozen models to exact zero residual.

**Does not establish — none of this moves:**

- **No mechanism.** Predictive ordering is never promoted to mechanism.
- **No biological parity at any level.** Full biological parity is not a current status.
- **No active-inference claim.** The dataset is passive and the action set is empty.
- **No G-side policy claim.** `expected_free_energy` does not exist in this package, a test
  enforces its absence, and it must not be added. G-side remains design-only until intervention or
  transfer.
- **Nothing about the mark process.** `nextStateN`/`direction`/`jump` were not read (D5).
- **Nothing about `B4C11`,** whose `U4_OK` remains **withdrawn** (D1). The corrected C11 run is in
  flight; this result does not speak to it.
- **`P4` transfer, `P5` intervention, `P6` structural/mechanistic, `P8` full verdict are untouched
  in either direction.** `P8` remains `FULL_PARITY = false`; the first unsatisfied level is still
  `P4` transfer.

## 8. Limitations

- **n = 19 holdout motors.** The 233 holdout events are **not** 19-fold more information; events
  within a motor are not independent replicates. Most contrasts are expected to be inconclusive,
  and they were.
- **Underpowered is not equivalence.** Every `NOT_ESTABLISHED` above is reported with its interval
  and half-width. Replicates were **not** increased after seeing a width, and must not be.
- **One cohort, one study, one species context** (*E. coli* behavioural evidence). No transfer.
- **Right-censored events are excluded by the frozen cohort**, so the F-side censoring branch is
  correct-by-test but **unexercised by this scoring run**. That is a real gap in coverage of the
  implemented likelihood, not a property of the result.
- The intervals are **percentile**, not BCa. The frozen B3 verdicts used BCa (`intervalUsed`). The
  half-widths quoted here belong to the percentile intervals and are labelled as such (D7).
- `M4_MIXTURE_K3`, `M6_SEMI_MARKOV_STATE_DEPENDENT` and `M7_HIERARCHICAL_MOTOR` were **not**
  contrasted here — only their published aggregates are available, and a paired motor-cluster
  bootstrap needs per-motor arrays. Their published point scores are quoted for placement only.
  **This was a genuine coverage gap. It is now CLOSED** - see
  `reports/M4-M6-M7-PER-MOTOR-CONTRASTS-REPORT.md` (post-hoc extension, `751a59ef...`). All three
  per-motor arrays were re-derived from their frozen fits and reproduce their published aggregates
  at **exact zero residual**. Outcome: **neither `M4` nor `M6` resolves against the candidate**
  (`NOT_ESTABLISHED` both, nominal and Bonferroni), and the `M7` contrast exposed **D10** - the
  frozen CI rule has no minimum-effect-size guard and "resolved" a `2.5e-07`-nat difference. The
  candidate ranks **5th of 10** combined.
- A `RuntimeWarning: overflow encountered in power` is emitted from `weibull_log_survival` during
  the fit. It is benign and by design: extreme quadrature nodes produce a non-finite density, which
  `_check` converts to `NonFiniteLogDensity`, which the marginal maps to `-inf` (zero mass for that
  node). No floor is applied. It is recorded here rather than silenced.

## 9. Gate status

| gate | status | receipt |
|-|-|-|
| **H-AIF-G7** | **EXECUTED — verdict `NOT_ESTABLISHED` against control and strongest adversaries** | this report; `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` `b3b12720…` |

`P3` duration-only: **unchanged.** B3 stands. The F-side candidate joins the leaderboard without
displacing anything and without being displaced by a CI-bound margin.

## 10. What would make LANE D true

Framing the next receipt as "what would make this lane true", not "why it fails":

1. **Per-motor arrays for `M4`, `M6`, `M7`** so the three models that out-score or match the F-side
   candidate can be contrasted under the same paired bootstrap. This is the cheapest highest-value
   next step and needs no new data.
2. **More independent motors.** The binding constraint is 19 holdout motors, not model quality. A
   second dataset with independent motors would move `P4` and sharpen every contrast here.
3. **A model that predicts something `M1_WEIBULL` cannot.** The hierarchy currently buys nothing;
   an F-side model earns its complexity only by beating its own `tau -> 0` limit.
4. **Censored observations**, to exercise the implemented censoring branch on real data.
5. **Intervention data** for any G-side claim. No amount of passive data substitutes; the action
   set is empty, which is structural.

---

`NEXT_ACT = monitor B4C02 (running) and B4C11 (running, launched 2026-07-22T01:40:03Z); on each completion sha256 the result, write its report against its pre-committed prediction record, and update the defect closure ledger (D1 for C11, D2 for C02)`
