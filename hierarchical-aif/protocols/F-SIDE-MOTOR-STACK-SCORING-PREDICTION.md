# F-Side Motor-Stack Held-Out Scoring — Prediction Record

**PROSPECTIVITY: `NOT_SATISFIED` — not retroactively repairable (D9).**
This file is **UNTRACKED**, and the scoring result already exists (2026-07-22T01:47:14Z), so
committing it now would post-date the observation. What *is* true and is all that is claimed: it
was written prior to any held-out scoring run of the
F-side motor-stack model. The harness that will execute it,
`hierarchical-aif/src/motor_stack_aif/compare.py`, exists and has been exercised
**TRAIN-ONLY**; `compare.run_comparison()` has **not** been called.

**Gate:** H-AIF-G6 (F-side observational projection) · **Lane:** D (motor-stack AIF)
**Parity ladder:** `P3` **duration-only** only. `P5`/`P6`/`P8` untouched in either direction.
**Status on commit:** `PENDING`. It becomes `PROSPECTIVE` only in the result commit, and only if
this prediction commit is a proven strict ancestor of the result's introduction.

---

## 1. Claim under test

> **H_FSIDE_DURATION.** The constrained F-side motor stack — a two-parameter population prior over
> per-motor log-shape, with the per-motor latent **integrated out** — predicts held-out **dwell
> durations** better than `CONTROL_CURRENT` (`M3_TWO_TIMESCALE`, the frozen B3 reference model) and
> better than every simple adversary, by a **CI-bound** margin on the frozen split.

This is a claim about **held-out duration density only**. It is not a claim about mechanism, about
the mark process, about active inference, or about any biological parity level.

## 2. Experimental unit, split boundary, sample size

| item | value |
|-|-|
| experimental unit | **MOTOR** (never event, never frame) |
| split rule | frozen `sha256_mod5(motorId) == 0 => holdout`, **reused, never recomputed** |
| cohort | `derived_eligible_1_to_8` (states 1..8, right-censored events EXCLUDED by the frozen rule) |
| training | 80 motors, 793 events |
| **holdout** | **19 motors, 233 events** |
| channel | **DURATION ONLY** (`durationS` / `stateN` / `rightCensored`) |
| mark channel | **NOT READ.** `nextStateN`, `direction`, `jump` are never requested (D5). |

**Why held-out access is permitted here.** The held-out **duration** channel was already
prospectively spent by B3, and duration-only held-out scoring is the explicitly allowed reuse. The
held-out **mark** channel was burned on 2026-07-21 (D5) and is not touched by this protocol; that
quarantine is unaffected by this run in either direction.

**Right-censoring limitation, stated up front.** The frozen cohort contains **no** right-censored
events, so the censoring branch of the F-side likelihood is **unexercised** on this cohort. Any
result here says nothing about censored-dwell behaviour.

## 3. The model and its equations

```
Lmotor-5   population prior over log-shape     eta_m ~ Normal(mu, tau^2)          2 free params
Lmotor-4   per-motor latent log-shape          k_m = exp(eta_m)                   INTEGRATED OUT
Lmotor-3   occupancy state N_i                 y_i = durationS_i / scale_N[N_i]   FROZEN scale_N
Lmotor-2   kinetic mode                        NOT INSTANTIATED
Lmotor-1   hazard / survival                   mean-one Weibull(k_m)
```

Per-event held-out predictive density (**the primary scored quantity**):

```
p(y_i) = INT  f_Weibull(y_i ; k = exp(eta), mean-one)  ·  Normal(eta ; mu, tau^2)  d eta
```

evaluated by **33-node Gauss-Hermite quadrature**. Deterministic; no sampling anywhere.

**Total free parameters: 2.** `(mu, tau)`. Nothing else is estimated.

**Why the per-motor latents are integrated, not estimated.** There are 793 training events across
80 training motors — a median of roughly 7 events per motor. Estimating 80 free per-motor shapes
would fit 80 numbers to ~7 observations each, and the corrected resolution floor on this cohort is
about **0.042 nats** (motor-equal contrast half-width). Capacity at that granularity is not
identifiable and could not be scored honestly. Integrating the latent keeps the parameter count
independent of the motor count, which is the whole point of the constraint. Adding `Lmotor-2`
policies would add unidentifiable capacity, not testability.

## 4. Competitor set — why each is a serious adversary

`CONTROL_CURRENT` is **`M3_TWO_TIMESCALE`**, the frozen B3 reference model. **It is not refitted.**
Its parameters `[0.3933559993214189, 0.44485933051063775]` are read verbatim from
`audits/phase-b/b3-model-competition-result.json` and scored through the frozen B3 scoring
functions.

| model | free params | why it is a serious adversary |
|-|-|-|
| `M3_TWO_TIMESCALE` | 2 | The incumbent. Two-exponential mixture; the repository's own published duration model. Same parameter budget as the F-side model, so a win is not bought with capacity. |
| `M2_LOGNORMAL` | 1 | **Currently out-predicts the two-timescale mixture.** In the frozen B3 record M2's log density exceeds M3's by **0.03686651825627818 nats event-pooled**, and M2's holdout motor-equal NLPD (3.4093141565673215) is the best of the simple models. A one-parameter heavy-tailed density beating the mechanistic mixture is the standing adverse result of this program. M2 is an **adversarial baseline, never the UNI model**. |
| `M1_WEIBULL` | 1 | The **exact `tau -> 0` limit of the F-side model**. This is the nesting control: if the hierarchy buys nothing, the F-side model must not beat M1. Any F-side advantage over M1 is precisely the value of the population spread and nothing else. |
| `M5_GAMMA` | 1 | A different one-parameter shape family with the same mean-one normalisation; guards against the result being an artifact of the Weibull tail specifically. |
| `M0_EXPONENTIAL` | 0 | Memoryless negative control. A model that cannot beat M0 has learned nothing about duration shape. |
| `M8_EMPIRICAL_KDE` | 1 (frozen `h`) | The **flexible** adversary: a log-scale KDE that can express essentially any smooth mean-one density. Its holdout motor-equal NLPD (3.4225236184063643) is second-best in the frozen record. Bandwidth `h = 0.31622776601683794` is read from the frozen record and the KDE locations are recomputed from TRAINING events only — no cross-validation is re-run and no holdout data enters the fit. |

`M4_MIXTURE_K3`, `M6_SEMI_MARKOV_STATE_DEPENDENT` and `M7_HIERARCHICAL_MOTOR` are **not** re-scored
here (their fits are not pinned in a form this harness can reconstruct without refitting). Their
frozen published numbers remain on the record and are not superseded by anything in this run.

## 5. Scoring rule, aggregation, contrast convention, CI

| item | value |
|-|-|
| scoring rule | **NLPD** (negative log predictive density) of the held-out dwell |
| **scale** | **SECONDS**, i.e. `-log p(y) + log scale_N[state]`. Declared in the output as `scaleConvention`. |
| aggregation (primary) | **MOTOR_EQUAL** — mean over motors of that motor's mean per-event NLPD |
| aggregation (secondary) | EVENT_POOLED, continuity bridge only, **never a verdict** |
| contrast | `contrast = S(reference) - S(challenger = F_MOTOR_STACK)` |
| interval entirely **above** 0 | the F-side model predicts better than that reference |
| interval entirely **below** 0 | that reference predicts better — **adverse**, retained and reported |
| interval **contains** 0 | `NOT_ESTABLISHED` / inconclusive — **never** "no difference", **never** "equivalent" |
| CI method | paired **motor-cluster** bootstrap, **percentile** interval, 95% |
| resampling unit | **MOTOR** (19 clusters). Events are never resampled. |
| replicates | `N_BOOT = 2000` |
| seed | `20260717` (the house B3 seed), RNG constructed **once** per contrast, no `hash()` |
| decision threshold | **0.0** |
| floor policy | **NO_FLOOR** — a non-finite log density HALTS |

**Interval-type honesty (D7).** Every interval reported by this harness is a **percentile**
interval and every reported width or half-width belongs to **that** percentile interval. The frozen
B3 artifact's `width` field was the percentile companion while its verdicts used BCa; this harness
does not repeat that ambiguity.

**Two F-side scores are reported, and only one is contrasted.**
- `MARGINAL_PER_EVENT` (**PRIMARY**, the one contrasted): each holdout event scored alone under the
  latent-integrated marginal — the same information set every competitor receives.
- `JOINT_PER_MOTOR / n` (**SECONDARY**, never contrasted): the motor's events share one latent and
  therefore inform each other. It is a **different scoring rule** and is reported only so the
  difference is visible rather than buried.

## 6. Mandatory independent-oracle consistency check (HALT condition)

B3 stores only **aggregated** scores — there are **no** per-motor arrays in the frozen record — so
every per-motor array used here is recomputed. The check is therefore mandatory, not optional.

Before any verdict, the harness must reproduce B3's published motor-equal NLPD for the three
**parameter-pinned** models, so that any residual is a convention error and nothing else:

| target | published motor-equal NLPD (seconds scale) |
|-|-|
| `M3_TWO_TIMESCALE` | `3.434333333075359` |
| `M0_EXPONENTIAL` (parameter-free) | `3.54798328106296` |
| `M8_EMPIRICAL_KDE` (frozen bandwidth) | `3.4225236184063643` |

**Tolerance: `1e-12` absolute.** Justification: the oracle reads parameters verbatim from the
frozen JSON (Python float `repr` round-trips exactly), rebuilds the cohort with the frozen `Cohort`
class in the frozen event order, and takes the normalised-space log density from the frozen
`holdout_lognorm`. Every floating-point operation and every summation order therefore matches the
recorded run, so the **expected residual is exactly 0.0**; `1e-12` on a value of ~3.43 is ~3e-13
relative, about 1000 ULP of pure last-place headroom.

**This tolerance will not be loosened to make the check pass.** If the residual exceeds it, the
harness HALTS, no verdict is emitted, and **the discrepancy is the reported finding**.

**Units are the thing most likely to go silently wrong.** B3's published NLPD is on the SECONDS
scale (it includes `+log(scale_N)` per event); `score.score_motor_stack` returns NLPD on the
NORMALISED-`y` scale. That constant **cancels in a contrast and does not cancel in an absolute
score**, so the failure mode is every contrast looking right while every absolute number is wrong
by ~2 nats. The scale conversion is a single named function, and a test mutates it and asserts the
oracle check FAILS — a check that cannot fail is worthless.

## 7. Pre-committed outcome branches

| branch | condition | recorded result |
|-|-|-|
| **A** | F-side contrast interval vs `CONTROL_CURRENT` **and** vs every adversary lies entirely **above** 0 | **Support for `H_FSIDE_DURATION`, scoped to duration-only `P3` on this cohort ONLY.** No mechanism, no parity movement beyond that scoped receipt. |
| **B** | any of those intervals **contains** 0 | **`NOT_ESTABLISHED`.** This is **not** equivalence and **not** "no difference". With 19 holdout motors most contrasts are *expected* to be inconclusive against a ~0.042-nat resolution floor. Reported with the interval and its half-width. |
| **C** | any adversary's interval lies entirely **below** 0 | **NEGATIVE result against the F-side duration claim.** Retained, reported in the headline, never demoted to a footnote. If that adversary is `M2_LOGNORMAL` it *extends* the standing adverse finding rather than creating a new one. |
| **D** | oracle check fails, a non-finite density halts, or any implementation defect is found | **`FAILED_RUN`.** No verdict of any kind. Repair loop, re-register, re-run. A `FAILED_RUN` is a legitimate outcome and is reported as one. |

Branches are evaluated **per contrast**; a run can be A against `M0_EXPONENTIAL` and C against
`M2_LOGNORMAL` at the same time, and both are reported.

## 8. Directional prediction — committed, and I am willing to be wrong

Evidence used to form it, all of it legitimately available now: the **frozen published** holdout
numbers for the competitors (already spent, already on the record), and the **training-only**
in-sample behaviour of the F-side fit. The F-side **held-out** score has not been computed.

Training-only inputs to the prediction (in-sample, 80 train motors, seconds scale, from the
train-only smoke run): F-side `3.4081198592824875`, `M1` `3.4008238291287873`,
`M2` `3.339864483642674`, `M5` `3.473193289623917`, `M0` `3.7103720252098027`. Fitted F-side
`mu = -0.41607215987582913`, `tau = 0.18372082607308418`, train NLL `575.6701064153622`
(vs `M3` `537.0211284007612`, `M2` `509.28782032664856`, `M1` `583.5856062645818`).

**I predict outcome branch (B/C), not (A).** Specifically:

1. **Point location.** F-side holdout motor-equal NLPD will fall in **`[3.425, 3.442]`**, and within
   **±0.005** of the frozen `M7_HIERARCHICAL_MOTOR` value `3.4326925889658892` — because both
   integrate a per-motor Weibull shape and differ mainly in parameterisation and node count.
2. **vs `M0_EXPONENTIAL`:** contrast ≈ **+0.115** nats → **`RESOLVED_ABOVE`**. This is the only
   contrast I expect to resolve.
3. **vs `M3_TWO_TIMESCALE` (control):** |contrast| < **0.010** → **`NOT_ESTABLISHED`**.
4. **vs `M1_WEIBULL` (the `tau -> 0` nesting control):** |contrast| < **0.005** →
   **`NOT_ESTABLISHED`**. The hierarchy will buy almost nothing. `tau = 0.1837` is small.
5. **vs `M2_LOGNORMAL`:** contrast ≈ **-0.024** (M2 better) → **`NOT_ESTABLISHED`**, because 0.024
   sits below the ~0.042 floor. `RESOLVED_BELOW` is a live alternative if the per-motor difference
   is unusually consistent, and would be branch **C**.
6. **vs `M5_GAMMA`:** contrast ≈ **+0.031** → **`NOT_ESTABLISHED`** (below the floor).
7. **vs `M8_EMPIRICAL_KDE`:** contrast ≈ **-0.010** → **`NOT_ESTABLISHED`**.
8. **Strongest adversary will be `M2_LOGNORMAL`** (frozen holdout motor-equal `3.4093141565673215`,
   lowest of the adversary set).

**Reasoning.** In-sample on the training motors the F-side model is already *slightly worse* than
plain `M1_WEIBULL` on motor-equal aggregation (`3.4081` vs `3.4008`) and clearly worse than `M2`
(`3.3399`), despite a better pooled training NLL than `M1`. A model that does not win in-sample
under the primary aggregation will not win out-of-sample under it. The fitted `tau = 0.184` is
small, so the population spread is doing little work. The honest expectation is a model that is
*competitive with*, not superior to, the incumbent — and that the standing lognormal adverse result
survives.

**What would make me wrong in the interesting direction:** if between-motor shape heterogeneity is
much stronger among the 19 holdout motors than among the 80 training motors, the integrated latent
would pay off out-of-sample in a way it cannot in-sample, and contrast 4 or 5 could resolve above 0.

## 9. Falsifier

`H_FSIDE_DURATION` is **falsified** if any adversary's contrast interval lies entirely **below** 0
— i.e. a simpler or purely empirical model out-predicts the motor stack on held-out durations by a
CI-bound margin. It is **not established** (not falsified, not supported) if any required interval
contains 0.

The directional prediction of §8 is falsified item by item: any listed verdict that comes out
different, or a point location outside `[3.425, 3.442]`, is a recorded miss.

## 10. Power — stated honestly, before the numbers

- **n = 19 holdout motors.** That is the sample size for every contrast. The 233 events are **not**
  19-fold more information: events within a motor are not independent replicates.
- The corrected motor-equal resolution floor on this cohort is a half-width of about **0.042 nats**
  (the narrowest frozen B3 motor-equal contrast is `M4_MIXTURE_K3` at `0.083461`; the frozen `width`
  field is the **percentile companion**, not the BCa width — D7).
- **Detectable:** motor-equal separations of roughly **0.05 nats and larger**, and smaller ones only
  if the per-motor difference is unusually consistent (a paired design with low between-motor
  variance can resolve a small mean shift).
- **Not detectable:** the ~0.02–0.03-nat gaps that separate the leading models in the frozen record.
  Most contrasts in this run are *expected* to be inconclusive.
- **Underpowered is not equivalence.** A zero-crossing interval will be reported as
  `NOT_ESTABLISHED` with its half-width, never as "no difference", "equivalent", or "on par".
- **Replicates will not be increased after seeing a width.** `N_BOOT = 2000` and n = 19 are fixed
  here, before the run. The bootstrap replicate count is a numerical-precision knob and does not
  change the 19-motor information content.

## 11. What this CANNOT establish, even if branch (A) fires

- **No mechanism.** Predictive superiority is never promoted to mechanism. A better density is a
  better density.
- **No biological parity** at any level. `FULL_PARITY` remains `false`; this run touches `P3`
  duration-only and nothing else.
- **No active-inference claim.** The dataset is passive and the action set is empty. That is
  **structural**, not a sample-size limitation.
- **No G-side policy claim.** `expected_free_energy` does not exist in the package and a test
  enforces its absence. It must not be added.
- **Nothing about the mark process.** `P5`/`P6`/`P8` are untouched. The D5/D6 quarantines are
  unchanged in both directions.
- **Nothing about B4C11**, whose submitted `U4_OK` remains withdrawn under D1.
- **Nothing about censored dwells** (excluded from this cohort), other states, other loads, other
  species, or any other apparatus.
- **The standing adverse result is reported alongside any positive result, never instead of it:**
  `M2_LOGNORMAL` out-predicts the two-timescale mixture by ~0.0369 nats event-pooled in the frozen
  record, and `M2` is an adversarial baseline, never the UNI model.

## 12. Wording

**Allowed:** "target hypothesis" · "candidate model" · "CI-bound verdict" · "not established" ·
"duration-only held-out support on the `derived_eligible_1_to_8` cohort" · "F-side observational
projection" · "retrospective-only" · "transfer required" · "intervention required" ·
"mechanism discriminator pending" · "G-side design-only until intervention".

**Forbidden**, mechanically checked by `claim_guard.py` (use-vs-mention aware). One catalogue
entry per line so each line is self-evidently a forbidden-wording listing and not an assertion:

- forbidden wording: "biological parity achieved"
- forbidden wording: "full parity achieved"
- forbidden wording: "active inference demonstrated"
- forbidden wording: "flagellum solved"
- forbidden wording: "full motor solved"
- forbidden wording: "general intelligence"
- forbidden wording: "awareness achieved"
- forbidden wording: "human stack validated"
- forbidden wording: "G proves motor agency"
- forbidden wording: "M2 is the UNI model"
- forbidden wording: "C11 diagnostic proves U4"
- forbidden wording: "mark process prospectively validated on Wadhwa-2022"

## 13. Reproduction

```bash
python -m pytest hierarchical-aif/tests/motor_stack_aif -q
python -c "import sys; sys.path.insert(0,'hierarchical-aif/src'); \
from motor_stack_aif import compare; \
compare.write_result('hierarchical-aif/results/motor_stack_aif/F_SIDE_SCORING_RESULT.json', \
                     compare.run_comparison())"
```

Deterministic: same inputs produce identical JSON bytes (`indent=1`, `sort_keys=True`, LF).

## 14. NEXT_ACT

Commit this record. Then, and only then, run `compare.run_comparison()`, write the result, flip
this record `PENDING -> PROSPECTIVE` in the **result** commit after confirming the ancestry, and
score §8 item by item — including the items that missed.
