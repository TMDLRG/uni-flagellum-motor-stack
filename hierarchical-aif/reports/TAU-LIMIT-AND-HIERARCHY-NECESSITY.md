# TAU-LIMIT AND HIERARCHY NECESSITY — builder-support probe (PROBE 5)

**Status: BUILDER-SUPPORT PROBE. Not a verdict.** Nothing here moves a P-level, changes a frozen
verdict, or creates a claim. `P8` remains `FULL_PARITY = false`; the first unsatisfied level
remains `P4` transfer. No P-level is raised or lowered by this document.

**Question.** Is the hierarchy (`Lmotor-5` population prior over log-shape, `Lmotor-4` per-motor
latent `eta_m` integrated out) doing work, or does the fitted model sit at its non-hierarchical
limit? The recorded F-side contrast against `M1_WEIBULL` is `+0.0006145100976836924` nats with
percentile half-width `0.01109232367002231` — the tightest contrast in the F-side set and centred
essentially on zero. This probe makes that a formal question with real computations.

**Split boundary: `TRAIN_ONLY` (duration-only).** Every computation in sections 1–4 uses the 80
training motors / 793 training events of the frozen `derived_eligible_1_to_8` cohort. No holdout
field is read by either script. The held-out numbers in section 5 are **reused verbatim from the
landed F-side artifact**, not recomputed. `nextStateN`, `direction` and `jump` were not read at any
point (D5 firewall).

**Units.** `tau` here is the population SD of the **log-shape** — **dimensionless**. It is *not* a
torque, and `tau * delta_theta` thermodynamic work does not appear anywhere in this document. The
profile axis is training **negative log-likelihood in nats** over 793 events; the held-out axis in
section 5 is motor-equal NLPD in nats per event on the SECONDS scale. These two axes are different
quantities and are never added.

## Artifacts and commands

| what | path |
|---|---|
| profile script | `hierarchical-aif/scripts/probe_tau_profile.py` |
| profile result | `hierarchical-aif/results/motor_stack_aif/TAU_PROFILE_PROBE5_RESULT.json` |
| shrinkage script | `hierarchical-aif/scripts/probe_tau_shrinkage.py` |
| shrinkage result | `hierarchical-aif/results/motor_stack_aif/TAU_SHRINKAGE_PROBE5_RESULT.json` |

```bash
cd hierarchical-aif
python scripts/probe_tau_profile.py        # 687 population-LL calls, 119.5 s wall
python scripts/probe_tau_shrinkage.py      # 30.3 s wall
```

Both reuse `hierarchy.population_log_likelihood`, `hierarchy.posterior_motor_shape` and
`hazard_survival` unchanged. No module was rewritten. No test was touched.

---

## 1. Profile log-likelihood over tau

**Method.** `tau` grid = `exp(linspace(log(1e-4), log(5.0), 61))` — transcribed verbatim from the
frozen `cell_C11` U2 grid in `audits/phase-b/b4-identifiability-robustness-runner.py`. The grid
endpoints coincide with `fit.TAU_MIN = 1e-4` and `fit.TAU_MAX = 5.0`. At each grid `tau`, `mu` was
re-optimised by bounded Brent on `[-3.0, 3.0]`, `xatol = 1e-5`. `tau` is **fixed** at each point:
this is a profile, not a fit. All 61 points returned finite values; `mu_hat` never touched its
bound.

**Curve (selected grid points; full 61 in the JSON).**

| i | tau | mu_hat | profile NLL (nats) | drop from max |
|---:|---:|---:|---:|---:|
| 0 | 0.0001 | -0.46986280 | 583.58559523 | 7.87880641 |
| 10 | 0.000606962 | -0.46986094 | 583.58519972 | 7.87841090 |
| 20 | 0.00368403 | -0.46979231 | 583.57064943 | 7.86386061 |
| 25 | 0.0090762 | -0.46943747 | 583.49546848 | 7.78867966 |
| 30 | 0.0223607 | -0.46737755 | 583.06095332 | 7.35416450 |
| 35 | 0.0550891 | -0.45739028 | 581.02022456 | 5.31343574 |
| 40 | 0.135721 | -0.42876387 | 576.42693140 | 0.72014258 |
| **42** | **0.19466102373808658** | **-0.4136969677540446** | **575.7067888179371** | **0.0 (grid max)** |
| 45 | 0.33437 | -0.39426441 | 581.10042347 | 5.39363465 |
| 50 | 0.823774 | -0.45242646 | 620.24512199 | 44.53833318 |
| 55 | 2.0295 | -0.52598963 | 686.39711640 | 110.69032758 |
| 60 | 5.0 | -0.47022482 | 703.58635390 | 127.87956509 |

**Consistency against the landed fit.** The grid maximum `575.7067888179371` sits
`0.036682402574911066` nats **above** the recorded free-fit `trainNLL = 575.6701064153622` at
`tau_hat = 0.18372082607308418`. That is the correct sign — `tau_hat` is not a grid point, so the
constrained grid optimum cannot beat the free optimum. This is a cross-check, not a new result.

**The tau -> TAU_MIN limit.** At `tau = 1e-4` the profile NLL is `583.5855952300938`, i.e. a drop
of **`7.878806412156678` nats** from the grid maximum. Per training event that is
`0.009935443142694423` nats/event over 793 events. The likelihood-ratio statistic is
`2 * 7.878806412156678 = 15.757612824313355`.

**Independent check that the tau -> 0 limit IS the non-hierarchical model.** Fitting a single
shared mean-one Weibull shape to all 793 pooled training events (one free parameter, no hierarchy)
by an independent 1-D bounded Brent gives `k = 0.6250888368122796`, NLL `583.5856062645817`.

- Against the frozen `M1_WEIBULL` fitted `k = 0.6250888335850175`: absolute difference
  `3.227262013183463e-09`, relative `5.162885400902826e-09`.
- Against the profile at `tau = 1e-4` (`583.5855952300938`): difference `1.1034487897632062e-05`
  nats, consistent with the `xatol = 1e-5` Brent tolerance on `mu`.

So the `tau -> 0` corner of this hierarchy **is** `M1_WEIBULL`, reproduced to 8 significant
figures by a separate implementation. That is the anchor the rest of this probe hangs on.

**Flatness criterion — `DESIGN_ONLY`.** The frozen `B4C11` U2 cell declares a flat set
`{tau : profileNLL(tau) - min <= 1.9207}` where `1.9207 = 0.5 * chi2_{1,0.95}`, normalises the
log-span by `log(5.0) - log(1e-4) = 10.819778284410281`, and fires
`UNIDENTIFIED_FLAT_PROFILE` at normalised log-span `>= 0.50`. Applying that offset here:

| quantity | value |
|---|---|
| `nllStar` | `575.7067888179371` |
| flat threshold | `577.6274888179371` |
| flat set tau range | `[0.11332624602040679, 0.2331283928719889]` |
| grid points in flat set | 5 of 61 |
| raw log-span (natural log) | `0.7213185522940186` |
| **normalised log-span** | **`0.06666666666666665`** |
| C11 U2 fire rule (reused `DESIGN_ONLY`) | normalised log-span `>= 0.50` |

`0.0667` is `7.5x` below the C11 fire rule, and the drop to the `tau -> TAU_MIN` corner
(`7.8788` nats) is `4.102049467463257x` the `1.9207` offset.

> **`DESIGN_ONLY` — this reuse is not evidential.** `1.9207` was frozen for the **B4C11 M7 cell**:
> a different model (`M7_HIERARCHICAL_MOTOR`, point-estimate per-motor shapes) with a different
> likelihood (`b3.m7_train_nll`) and a different nuisance parameter being profiled out. It was
> never frozen for the F-side marginal likelihood. Reusing it here is a **design-time** yardstick
> so this probe is not inventing a threshold; it is **not** a frozen criterion for this cell and
> confers no status. There is **no** frozen flatness criterion for the F-side profile. Nor is the
> `chi2_{1}` calibration itself appropriate at the `tau -> 0` corner: `tau = 0` is on the boundary
> of the parameter space, where the reference distribution is a chi-bar mixture, not `chi2_1`.
> A calibrated reference distribution for this statistic is **`NOT_RUN — COMPUTE_BUDGET`**
> (see §3).

**Reading.** The profile is *not* flat in `tau` and the fitted `tau` does *not* sit at its
non-hierarchical limit **in training log-likelihood**. The training data prefer a positive `tau`
by roughly 7.9 nats over the whole 793-event training set. That is an **in-sample training**
statement about the likelihood surface. It is not a held-out statement, and §5 shows the two
disagree in practical size by more than an order of magnitude.

---

## 2. Posterior shrinkage of eta_m

**Method.** `hierarchy.posterior_motor_shape(y_m, c_m, mu, tau)` at the **recorded** fit
`mu = -0.41607215987582913`, `tau = 0.18372082607308418` (read from
`F_SIDE_MOTOR_STACK_SCORING_RESULT.json`, not refitted), for each of the 80 training motors.
A **no-pooling** comparator `eta^np_m` was obtained per motor by unpenalised 1-D bounded-Brent MLE
of the log-shape on `[log 0.05, log 5.0]` — the same box the frozen M7 U2 profile uses — with an
observed-information SE from a central second difference of the per-motor profile.

| quantity | value |
|---|---|
| posterior mean `eta` — SD across 80 motors | `0.10452532086846263` |
| posterior mean `eta` — range | `[-0.6931133350924024, -0.22970397293420786]`, span `0.4634093621581945` |
| posterior mean `eta` — mean | `-0.4160725085519582` (population `mu` = `-0.41607215987582913`) |
| posterior SD of `eta` — mean over motors | `0.1499519706567764` |
| posterior SD of `eta` — min / max | `0.07758422130301702` / `0.18256736852532654` |
| mean posterior SD / prior SD (`tau`) | `0.8161947334001507` |
| no-pooling `eta` — SD across motors | `0.4244847489301593` |
| no-pooling `eta` — SE, mean / median | `0.33478638677309` / `0.2790197574101846` |
| no-pooling MLEs hitting the box bound | 1 of 80 |
| single-event training motors | **7 of 80** — recomputed directly from `coh.train_by_motor`. An earlier draft said 1 and attributed the single bound-hit to "the" single-event motor; the cohort has SEVEN, so the bound-hit count is not the single-event count |
| events per training motor | min 1, median 7, max 70 |

**Shrinkage factors.**

| factor | mean | median | min | max |
|---|---:|---:|---:|---:|
| weight on own data `B_m = tau^2/(tau^2 + se_m^2)` | `0.32770293276724` | `0.302477939329217` | `0.004032899513228368` | `0.8193161135444185` |
| shrinkage toward population `1 - B_m` | `0.67229706723276` | `0.697522060670783` | `0.18068388645558153` | `0.9959671004867716` |
| empirical travel `(E[eta_m|y] - mu) / (eta^np_m - mu)` | `0.3239796507183491` | `0.2985340266708879` | `-0.46307952127664115` | `0.8221089877194633` |

Aggregate: `SD(posterior means) / SD(no-pooling MLEs) = 0.24624046242391676`. **69 of 80** motors
have `1 - B_m > 0.5`; **7 of 80** have `1 - B_m > 0.9`. The extreme case is the motor with
**1 event**: `eta^np = 1.6094378597456587` (at the box bound), `se = 2.8871688630597583`,
`B = 0.004032899513228368`, posterior mean `-0.37916259362785415` — i.e. it is returned to the
population mean almost exactly, which is the hierarchy behaving correctly rather than a defect.

**Reading.** Posterior means travel roughly **a third** of the no-pooling distance from the
population mean and retain about **a quarter** of the no-pooling between-motor spread. Motors are
**not** all collapsed onto the population mean — 45 of 80 sit within `0.5 * tau` of `mu`, so 35 do
not, and the widest posterior mean sits `0.27704117521657323` from `mu`, about `1.5 * tau`. But
the mean posterior SD (`0.1500`) is `0.816` of the prior SD `tau`, meaning a typical motor's
duration record moves its own belief only modestly off the prior. **The hierarchy is doing
something and it is small.** That is the honest statement; it is not "the hierarchy is doing
nothing" and it is not evidence that the pooling is buying prediction.

---

## 3. Motor-level heterogeneity evidence

**Events per motor, real training cohort (80 motors, 793 events).**

| min | q25 | median | q75 | max | mean | motors with <= 5 events | motors with <= 10 events |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 4.0 | 7.0 | 11.0 | 70 | 9.9125 | 26 | 58 |

The distribution is heavily right-skewed: the median motor contributes 7 events while a single
motor contributes 70. Twenty-six motors contribute at most 5 events each.

**Test.** Statistic = SD across motors of the **no-pooling** per-motor log-shape MLE. Null
generator = the `tau -> 0` limit, i.e. one shared mean-one Weibull shape at the pooled MLE
`k_null = 0.6250888368122796`, with **each motor's own `n_m` preserved**, 300 replicates, seed
`20260717`.

> **These replicates are SIMULATION.** They are a Monte-Carlo reference distribution and may never
> be labelled `OBSERVED`. The plug-in `k_null` ignores estimation uncertainty in `k_null` itself.

| quantity | value |
|---|---|
| observed SD (real cohort) | `0.4244847489301593` |
| null SD — mean | `0.4392477594483711` |
| null SD — SD across replicates | `0.05704560188967387` |
| null SD — 2.5% / 50% / 97.5% | `0.3375852347365378` / `0.4370122161469224` / `0.5453959757815685` |
| null replicates at or above observed | **175 of 300** |
| Monte-Carlo tail fraction `(n>=obs + 1)/(nRep + 1)` | `0.584717607973422` |
| observed variance minus mean null variance | `-0.01599464546541901` (negative) |
| implied excess SD | **`NOT_COMPUTED` — the variance excess is negative** |

**Reading — and this is the adverse result of the probe.** The observed between-motor spread of
per-motor dwell-shape estimates is **below** the mean spread produced by a generator with **zero**
between-motor heterogeneity. On this statistic, the apparent variation in dwell shape across motors
is entirely consistent with within-motor sampling noise at a median of 7 events per motor.

**This is `NOT_ESTABLISHED`, not equivalence.** The statistic is badly underpowered for the
effect size at issue: if the true between-motor SD were `tau = 0.18372082607308418`, the expected
observed SD would be roughly `sqrt(0.4392^2 + 0.1837^2) = 0.47612176605716156` — comfortably inside
the null 97.5th percentile of `0.5453959757815685`. So this test **could not have detected**
`tau = 0.184` even if it were exactly right. It does not contradict §1; it shows that a
moment-style statistic built on noisy per-motor point estimates throws away the information the
marginal likelihood in §1 keeps.

**`NOT_RUN — COMPUTE_BUDGET`.** The properly matched test is a parametric-bootstrap calibration of
the §1 profile statistic itself: simulate under `tau -> 0` at `k_null` preserving each `n_m`, and
for **each** replicate refit the full 2-parameter hierarchy and recompute the drop to
`tau = TAU_MIN`, giving a boundary-correct null distribution for `2 * 7.878806412156678` without
assuming `chi2_1`. Each replicate costs one `fit_motor_stack` call; the measured cost of a single
profile point (11 population-LL evaluations) was `~1.65 s`, and a full fit is `nfev = 165` LL
evaluations, so ~`2.1 s` per replicate and **~10.5 minutes for 300 replicates** in one process.
That exceeds this pack's compute fence and would contend with the two in-flight long runs.
It is **not run**, and its absence is why §1 reports a statistic and no p-value.

---

## 4. tau-at-boundary

`fit.py` bounds `tau` to `[TAU_MIN, TAU_MAX] = [1e-4, 5.0]` and flags
`tauAtBoundary = (tau <= TAU_MIN * 1.01) or (tau >= TAU_MAX * 0.99)`. The module comment states the
reason explicitly: `tau -> 0` collapses the hierarchy to a single shared shape, which is a
**different model**, so the boundary is reported rather than silently crossed. §1 confirms that
comment numerically — the `tau -> 0` corner reproduces `M1_WEIBULL`'s `k` to `3.2e-09`.

| check | value | source |
|---|---|---|
| recorded F-side `tau` | `0.18372082607308418` | `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` `fitted.F_MOTOR_STACK` |
| recorded `tauAtBoundary` | `false` | same |
| distance to `TAU_MIN` (log units) | `log(0.18372/1e-4) = 7.51` — nowhere near | this probe |
| distance to `TAU_MAX` | `0.1837` vs `5.0` | this probe |
| profile grid maximum `tau` | `0.19466102373808658` (grid index 42 of 61) — interior | this probe |
| `DESIGN_ONLY` flat set | `[0.11332624602040679, 0.2331283928719889]` — touches neither bound | this probe |
| frozen `B4C11` U1 | `TAU_INTERIOR` (`out["U1_alreadyDone_in_B3"]`) | frozen runner `cell_C11` |

So the frozen M7 U1 verdict and the F-side fit agree: `tau` is interior, on both the point estimate
and the whole `DESIGN_ONLY` flat set.

> **`tau` being interior is NOT evidence of a mechanism.** It is a statement about where a
> two-parameter likelihood surface peaks on 793 dwell durations. It licenses no claim about
> stators, CheY-P, load, torque, or any physical process. A hierarchy diagram is a parameterisation,
> not a mechanism, and this probe exists partly to prevent that inference.

---

## 5. Comparison to M1_WEIBULL — recorded, not recomputed

Reused verbatim from the landed F-side artifact. **No new contrast was computed.**

| field | value |
|---|---|
| contrast | `S(M1_WEIBULL) - S(F_MOTOR_STACK)`, motor-equal NLPD, SECONDS scale |
| point estimate | `+0.0006145100976836924` nats |
| interval | `[-0.010880659688579656, +0.011303987651464963]` |
| half-width | `0.01109232367002231` (percentile; BCa is **`NOT_COMPUTED`** for F-side contrasts) |
| `intervalType` / `nRep` / `seed` | `percentile` / `2000` / `20260717` |
| verdict | **`NOT_ESTABLISHED`** |
| `atOrBelowResolutionFloor` | `true` |

The frozen resolution floor is a motor-equal half-width of `0.042` nats over 19 holdout motors.
This contrast's half-width is `0.0111`, i.e. `3.715827656374414x` **narrower** than the floor — so
even the whole interval lies inside what the cohort treats as scientifically immaterial. Per
**D10**, the floor states what is scientifically **material**, not what the bootstrap will
**call**; a narrow interval that still contains 0 is `NOT_ESTABLISHED` and remains so.

**The number that matters for this probe.** Training gain from the hierarchy over its own
`tau -> 0` limit: `0.009935443142694423` nats/event (§1). Held-out gain over `M1_WEIBULL`:
`+0.000615` nats/event, interval crossing 0. The training gain is
`16.155192101942152x` the held-out point estimate, and the held-out point estimate is itself
`~68x` below the `0.042` materiality floor. **The hierarchy is preferred in training and its
held-out benefit over the non-hierarchical limit is `NOT_ESTABLISHED` at this sample size.**

Note the structural relationship this sits next to: the F-side hierarchy coincides with
`M7_HIERARCHICAL_MOTOR` to numerical precision (`exp(mu) = 0.659632669755436` vs M7
`k = 0.6596322379287862`; `tau = 0.18372082607308418` vs M7 `tau = 0.18372185667134974`), which is
why the recorded F-vs-M7 contrast is `+2.506984e-07` nats — `RESOLVED_ABOVE` but recorded as
`SCIENTIFICALLY_NULL`. The F-side candidate is bracketed on one side by a model it nearly *is*
(M7) and on the other by its own degenerate limit (M1), and it separates from neither.

---

## 6. When the hierarchy is justified, and when it is decoration

**Builder-facing conclusion.** On this cohort the hierarchy is *load-bearing for inference* and
*not demonstrably load-bearing for prediction*.

**Where it is justified — keep it:**

1. **Small-`n` motors.** 26 of 80 training motors have `<= 5` events; one has a single event. Its
   no-pooling MLE runs to the box bound with `se = 2.887`. Pooling returns it to `mu` with
   `1 - B = 0.996`. Any no-pooling alternative would have to special-case these motors, and a
   per-motor free-shape model would fit 80 numbers to a median of 7 events each — the exact
   failure the `hierarchy.py` docstring says the design refuses.
2. **Parameter economy under the frozen scoring rule.** The hierarchy carries **2** free
   parameters regardless of motor count because `eta_m` is integrated by 33-node Gauss-Hermite,
   never estimated. Against `M1_WEIBULL`'s 1 parameter, the training likelihood buys `7.88` nats
   for that one extra parameter. The structure is cheap.
3. **It gives a per-motor posterior at all.** `posterior_motor_shape` yields `q(eta_m)` with a
   real SD (`0.078`–`0.183`). `M7_HIERARCHICAL_MOTOR` reports point estimates only. If the next
   step is a per-motor **prediction with uncertainty**, only the hierarchy can supply it.

**Where it is decoration — do not sell it:**

1. **Held-out separation from its own `tau -> 0` limit is `NOT_ESTABLISHED`** (§5). A builder may
   not describe the hierarchy as predictively necessary on this cohort.
2. **The heterogeneity it models is not independently detectable** by a per-motor-estimate
   statistic on this cohort (§3) — and that statistic is underpowered, so this is `NOT_ESTABLISHED`
   in both directions, never "no heterogeneity" and never "the motors are equivalent".
3. **A hierarchy diagram is not a mechanism.** Nothing in §1–§4 identifies a physical source of
   between-motor variation. Between-motor differences in dwell shape, if real, are confounded on
   this dataset with load, stator number, PMF, temperature, and cell-to-cell state, none of which
   is a covariate here. Attributing `tau` to any of those would be an unsupported inference.
4. **The `Lmotor-2` kinetic-mode layer stays uninstantiated.** If a 2-parameter hierarchy cannot
   separate itself from a 1-parameter model on held-out data, adding a further latent layer adds
   unidentifiable capacity, not testability.

**The receipt that would make the "hierarchy is necessary" lane true.** Held-out motor-equal
separation of the hierarchy from `M1_WEIBULL` with an interval that excludes 0 **and** lies outside
`+/- 0.042` nats. At the observed per-event effect size (`~0.0006` held-out, `~0.0099` training)
that is not reachable by re-analysis of these 19 holdout motors: it needs either far more motors,
or motors with genuinely larger dwell-shape dispersion, or a covariate that predicts `eta_m` — all
of which require **transfer** (`P4`) or **intervention** (`P6`), neither of which this repository's
passive dataset can supply. The action set is empty; that is structural, not sample-size-limited.

**The receipt that would kill the lane.** A boundary-correct null calibration of the §1 profile
statistic (the `NOT_RUN — COMPUTE_BUDGET` item in §3) in which the observed
`2 * 7.878806412156678 = 15.7576` falls inside the `tau -> 0` null distribution. That would mean
the training-side preference for a positive `tau` is itself an artefact of the boundary geometry
rather than evidence of dispersion, and the honest description of the hierarchy would collapse to
decoration in both directions. That computation is specified, cheap in principle (~10.5 min), and
should be run before anyone describes `tau > 0` as supported.

---

## Limitations and things this probe did not compute

- **`NOT_RUN — COMPUTE_BUDGET`:** boundary-correct parametric-bootstrap null for the §1 profile
  statistic (~10.5 min, one process). No p-value is attached to `7.8788` nats anywhere above.
- **`NOT_COMPUTED`:** BCa intervals for any F-side contrast. Per **D7**, BCa exists only for the 48
  frozen B3 contrasts; the F-side contrasts are percentile only. No BCa was computed or estimated.
- **`NOT_COMPUTED`:** implied excess between-motor SD in §3 — the variance excess is negative
  (`-0.01599464546541901`).
- **`NOT_CHECKED`:** anything about the mark process (`nextStateN`, `direction`, `jump`). Would
  require holdout access; the D5 firewall was not crossed.
- **Right-censoring is unexercised.** The frozen cohort excludes right-censored events entirely
  (`compare.Inputs` asserts this), so the censoring branch of the F-side likelihood is untested by
  every number here. Sections 1–3 all pass all-`False` censoring arrays.
- **The §3 null is a plug-in.** `k_null` was fixed at the pooled MLE; uncertainty in `k_null` is
  not propagated, which if anything makes the null spread slightly too narrow — and the observed
  SD is already below the null mean, so correcting it would not change the direction.
- **`mu` optimiser tolerance.** `xatol = 1e-5` on `mu` leaves `~1.1e-05` nats of slack in the
  profile (measured against the independent pooled fit). Every reported drop is `>= 0.72` nats at
  the reported grid points, so this slack does not affect any statement made.
- **Only one cohort, one species, one study.** `derived_eligible_1_to_8` from Wadhwa 2022,
  *E. coli* behavioural evidence. Nothing here transfers to *Salmonella* or *Bacillus* structural
  evidence, and no cross-species statement is made.
- **Two long runs (B4C11, B4C01) were in flight throughout.** Neither was read, cited, disturbed,
  nor written to. No counter from either progress log appears in this document.

NEXT_ACT = run the boundary-correct parametric-bootstrap null for the §1 profile drop (300 replicates under the tau -> 0 generator at k_null = 0.6250888368122796, each replicate refitting fit_motor_stack and recomputing the drop to TAU_MIN), as a single ~10.5-minute process scheduled AFTER B4C11 and B4C01 have landed, so that `tau > 0` is either supported by a calibrated reference distribution or withdrawn to decoration.
