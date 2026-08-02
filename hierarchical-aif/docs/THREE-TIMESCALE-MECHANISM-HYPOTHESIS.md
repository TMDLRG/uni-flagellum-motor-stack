# THREE-TIMESCALE MECHANISM HYPOTHESIS — DESIGN NOTE

**Status: DESIGN NOTE / HYPOTHESIS-GENERATING / NON-EVIDENTIAL.**
This document asserts no mechanism. It creates no claim, moves no P-level, and changes no frozen
verdict. It compares five structurally distinct explanations of one already-recorded adverse
result and, for each, names the outcome that would remove it.

- Scope: cohort `derived_eligible_1_to_8` (Wadhwa 2022, *E. coli*), duration channel only.
- Experimental unit: the MOTOR. Events inside a motor are not independent replicates.
- Species boundary: *E. coli* behavioural evidence only. No *Salmonella* or *Bacillus* structural
  evidence enters this note.
- Held-out mark channel (`nextStateN` / `direction` / `jump`): NOT READ by this probe.
- Every number below carries its source. Anything unavailable is `NOT_MEASURED`,
  `NOT_COMPUTED`, or `NOT_RUN` with a reason.

---

## 1. The opening observation, stated at its real scope

B4C02 (`hierarchical-aif/results/motor_stack_aif/B4C02_CORRECTED_FULL_RESULT.json`, landed
`0633988d…`, full frozen N=200 per generator, 600 simulations, 0 failures) asked whether the
M2-over-M3 held-out advantage is generic to heavy-tailed worlds. It is not.

| simulated generator | `m2_beats_m3_frac` | modal NLPD winner |
| --- | --- | --- |
| `weibull_gamma_blend` | 0.0050 | M3_TWO_TIMESCALE, 81/200 |
| `three_timescale_heavy_tail` | **0.9400** | M2_LOGNORMAL, 187/200 |
| `per_motor_heterogeneous_weibull` | 0.0050 | M3_TWO_TIMESCALE, 82/200 |

`gensWithM2overM3 = 1` of 3 → recorded verdict `GENERATOR-SPECIFIC`; the frozen
`GENERATOR-ROBUST_ADVERSE` expectation is REFUTED.

**What this licenses.** In SIMULATED worlds, the single world where the lognormal reliably
out-scores the two-timescale mixture is the world carrying more timescales than M3 can express.
That is an observation about a generator the repository wrote, scored by the repository's own
fitting path.

**What this does not license.** It is not evidence about the real cohort. No simulation result may
be relabelled observed. The real-data adverse result (M2 3.4093141566 vs M3 3.4343333331 on the
frozen held-out motor-equal leaderboard) is unchanged by B4C02 in either direction: B4C02 removed
one explanation of it (generic heavy tail) and left the remaining explanations untested against
each other.

**Caveat carried, not hidden.** The C02 generator seeding uses `hash(gen_label)` (defect D3,
CLOSING). The landed C02 artifact records its own seeds and runtime, so the recorded numbers stand
as recorded; the seed construction is a reproducibility defect tracked separately, not a
re-interpretation of these fractions.

---

## 2. Geometry of the winning simulated world versus the real fitted structure

Computed this probe from frozen constants (command in §9). All quantities are in the mean-one
normalised-`y` space that both the generator and M4 use, so ratios are directly comparable.

| quantity | `three_timescale_heavy_tail` generator | M4_MIXTURE_K3 fitted on the real cohort |
| --- | --- | --- |
| component rates | 2.0 / 0.3 / 0.02 | 7.410301079721995 / 1.0269138959905078 / 0.2252632502537158 |
| component weights | 0.5 / 0.4 / 0.1 | 0.45920454549250384 / 0.4220782557784245 / 0.11871719872907172 |
| fastest : slowest rate ratio | **100.0** (2.0 decades) | **32.89618289435011** (1.5171455075519444 decades) |
| share of total mean dwell time in the slowest component | 0.7594936708860759 | 0.5270153857558194 |

The slow-component **weight** the generator uses (0.1) and the weight M4 fits (0.1187) are close.
The **rate separation** is not: the generator's third timescale sits 100× below its fastest, the
fitted third component sits ~33× below. The simulated world in which the lognormal reliably wins
is more extreme in separation than the closest three-timescale structure actually fitted to the
real cohort. This is a descriptive comparison of two parameter vectors; it is `DESIGN_ONLY` and
carries no interval and no verdict.

**A structural limit of B4C02 relevant to hypothesis 5.** All three C02 generators write
`"rightCensored": False` on every simulated event
(`audits/phase-b/b4-identifiability-robustness-runner.py`, lines 883–932). The simulated worlds
contain no censoring at all, so B4C02 cannot speak to any censoring explanation. That lane is
untested by C02 by construction.

---

## 3. New measurement made by this probe: the censoring census

Duration channel only, train and holdout, states 1–8, from `events.load_events(mode='duration_only')`.

- States 1–8 events present in the source: **1080**. Retained by the frozen cohort: **1026**
  (793 train + 233 holdout). Right-censored and therefore EXCLUDED: **54** (5.0%).
- Median duration of retained events **2.42 s**; median duration of the excluded censored events
  **83.35 s**.
- Of the 20 longest state-1–8 dwells in the source, **14 are right-censored** and so are absent
  from every score in this repository.
- The exclusion is strongly state-dependent:

| state | n (1–8 source) | censored | censored fraction | longest retained (s) | longest censored (s) | frozen `scale_N` | frozen M6 shape `k` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 84 | 0 | 0.0000 | 53.46 | — | 4.749152542372881 | 0.6990234669824187 |
| 2 | 91 | 0 | 0.0000 | 61.56 | — | 3.4826086956521736 | 0.7233702022424247 |
| 3 | 106 | 0 | 0.0000 | 60.46 | — | 6.350886075949368 | 0.6925132420478101 |
| 4 | 104 | 1 | 0.0096 | 102.12 | 44.06 | 5.062716049382717 | 0.7289889570450139 |
| 5 | 127 | 3 | 0.0236 | 128.36 | 190.08 | 7.948453608247423 | 0.6925342829524168 |
| 6 | 160 | 5 | 0.0312 | 288.20 | 327.52 | 14.389918699186993 | 0.5513548296218598 |
| 7 | 210 | 17 | 0.0810 | 219.26 | 343.12 | 18.245270270270268 | 0.5934453696369055 |
| 8 | 198 | 28 | 0.1414 | 307.50 | 325.28 | 24.52058394160584 | 0.5437856270600075 |

M6 shapes are read from
`audits/phase-b/b3-model-competition-result.json` →
`cohorts.derived_eligible_1_to_8.fitted.M6_SEMI_MARKOV_STATE_DEPENDENT.params`.

Descriptive rank correlations across the 8 states (Spearman): censored-fraction vs `k`
rho = −0.7319250547114; `scale_N` vs `k` rho = −0.880952380952381; `scale_N` vs censored-fraction
rho = +0.9271050693011065. **The accompanying p-values are NOT INTERPRETABLE and are deliberately
omitted from any conclusion**: the 8 states are nested inside the same motors, so they are not
independent replicates, and the experimental unit is the motor. These rho values are shown to
expose a confound, not to support anything.

**Censoring-sensitivity side computation (`DESIGN_ONLY`, train partition only, no interval).**
A free two-parameter Weibull in seconds was fitted per state twice: once dropping censored events
(what the frozen cohort does) and once retaining them as right-censored survival contributions.

| state | n uncensored (train) | n censored (train) | `k` drop-censored | `k` censoring-aware | delta |
| --- | --- | --- | --- | --- | --- |
| 1 | 59 | 0 | 0.702501 | 0.702501 | 0.0 |
| 2 | 69 | 0 | 0.726302 | 0.726302 | 0.0 |
| 3 | 79 | 0 | 0.695164 | 0.695164 | 0.0 |
| 4 | 81 | 1 | 0.731947 | 0.703062 | −0.028885 |
| 5 | 97 | 3 | 0.696450 | 0.639390 | −0.057061 |
| 6 | 123 | 4 | 0.561152 | 0.509572 | −0.051580 |
| 7 | 148 | 15 | 0.597128 | 0.512384 | −0.084744 |
| 8 | 137 | 20 | 0.548904 | 0.487591 | −0.061313 |

Two readings, both bounded:

1. The drop-censored column tracks the frozen M6 shapes closely (state 1: 0.702501 here vs
   0.6990234669824187 frozen; state 8: 0.548904 here vs 0.5437856270600075 frozen) despite a
   different parameterisation (free scale in seconds versus mean-one normalised `y` with frozen
   `scale_N`). This is a weak consistency check, **not** an independent oracle — no tolerance was
   declared in advance and no interval was computed.
2. Restoring the censored events as survival terms moves every affected shape DOWN, i.e. toward a
   heavier tail. The naive form of hypothesis 5 — "dropping long dwells manufactures the heavy
   tail" — is directionally contradicted by this: dropping them appears to UNDERSTATE tail
   heaviness, not create it. No confidence interval was computed for any delta, so this is a
   direction to be tested, never a verdict.

---

## 4. The five candidate explanations

Contrast convention throughout: `contrast = S(reference) − S(challenger)`; interval entirely above
zero means the challenger scores better; an interval containing zero is `NOT_ESTABLISHED`. The
corrected motor-equal resolution floor is ≈0.042 nats (BCa half-width of the narrowest frozen B3
contrast, M4_MIXTURE_K3, BCa width 0.08414086126525253). Per D10, that floor states what is
scientifically material; it is not what the bootstrap will call.

### H1 — shape-only lognormal (descriptive tail, no kinetic content)

The held-out advantage is a curve-fitting fact: a **one**-parameter mean-one lognormal happens to
track the empirical dwell shape better than a **two**-parameter two-component exponential mixture,
with no implied kinetics.

> **Free-parameter counts, corrected against the frozen implementation.** Every simple competitor
> is parameterised in MEAN-ONE form, which removes one degree of freedom apiece: `M2_LOGNORMAL`
> has **1** free parameter (`sigma`; `mu = -sigma^2/2`), `M1_WEIBULL` **1** (`k`), `M5_GAMMA` **1**
> (`shape`), `M3_TWO_TIMESCALE` **2** (`w`, `lambdaFast`, with `lambdaSlow` fixed by mean-one), and
> the F-side candidate **2** (`mu`, `tau`). An earlier draft of this note called M2, M1 and M5
> "two-parameter"; that was wrong. **The correction strengthens H1's premise rather than weakening
> it**: the model that wins on held-out data is *simpler* than the mixture it beats, which is
> exactly what a shape-only account predicts and what a timescale-count account does not.

- **Support would look like:** the advantage tracks shape flexibility and not timescale count —
  e.g. other flexible one-parameter shapes (M1 3.4333068484, M5 3.4637286552) and the
  nonparametric M8_EMPIRICAL_KDE (3.4225236184) cluster with M2 rather than with M3, and the
  ordering is stable under leave-one-motor-out.
- **What would kill it:** a model with the same number of free shape parameters but strictly more
  timescale structure resolving ABOVE M2 by more than the floor. Alternatively, a parameter-count
  matched flexible shape that fails while a three-rate model succeeds.
- **Next discriminator:** leave-one-motor-out refit and rescore of the frozen 9-model family on
  `derived_eligible_1_to_8`, reporting rank stability of M2 vs M8 vs M4 per held-out motor.
- **Data required:** none beyond the frozen cohort and the duration channel.
- **Runnable now?** YES on currently allowed data. Cost `NOT_MEASURED` in this probe; it is a
  refit-per-motor sweep and must be budgeted against the two runs in flight.
- **Admissible?** Yes — it carries a killer.

### H2 — three-timescale latent kinetic process (a real third, slow rate)

There is a genuine third, slow kinetic component in the dwell process; M3's two timescales cannot
express it, and the lognormal's tail absorbs the misfit.

- **Support would look like:** a three-rate model resolving above BOTH M2 and M3 by more than the
  floor, with the third rate identified rather than collapsed, and with the same slow component
  recovered in an independent motor population.
- **What would kill it:** (a) the third component being unidentifiable on data of this size —
  which B4C10 did NOT find, see §5; (b) a three-rate model failing to beat a two-parameter
  shape-only model on identical splits and scoring; (c) the slow component failing to reappear in
  transfer, i.e. being a property of this cohort's recording window rather than of motors.
- **Next discriminator:** the strongest one is NOT another fit on this cohort — it is a
  load/PMF/temperature contrast in which a kinetic third rate must shift in a predicted direction
  while a descriptive shape parameter need not. That is a **mechanism discriminator pending**.
- **Data required:** a second *E. coli* dwell dataset recorded under a different load or PMF
  condition, with per-motor identity, or a longer recording window on the same strain.
- **Runnable now?** NO — **transfer required**. On current data only the weaker, retrospective
  version (does a three-rate model beat two-parameter shapes here) is runnable, and that version
  has already returned `NOT_ESTABLISHED`, see §5.
- **Admissible?** Yes — it carries a killer, but the decisive one is out of reach on this dataset.

### H3 — motor heterogeneity (between-motor variation masquerading as a tail)

There is no third timescale and no unusual within-motor shape; motors simply differ, and pooling
them produces an apparently heavy tail.

- **Support would look like:** a per-motor hierarchical model absorbing the advantage — i.e. once
  between-motor spread is modelled, M2's edge over the hierarchical candidate disappears or
  reverses by more than the floor.
- **What would kill it:** heterogeneity being fitted and the pooled tail surviving anyway. The
  current evidence is closer to this than to support: the F-side constrained motor stack (2 free
  parameters, per-motor latents integrated by 33-node Gauss–Hermite) scores 3.4326923382675303 and
  its contrast against M2 is −0.023378 [−0.104886, +0.067038] → `NOT_ESTABLISHED`. Modelling
  heterogeneity did not resolve the advantage away, and it also did not establish the reverse.
  **Underpowered is not equivalence**: with 19 holdout motors this interval is wide and the
  question is open.
- **Also relevant, and adverse to a strong version of H3:** B4C02's
  `per_motor_heterogeneous_weibull` world produced `m2_beats_m3_frac = 0.0050`. In a simulated
  world that is pure motor heterogeneity, the lognormal does NOT acquire the advantage it holds on
  the real cohort. Simulation evidence only; it is not observation.
- **Next discriminator:** a per-motor posterior predictive check — simulate dwell sets from the
  fitted hierarchy and ask whether the real per-motor upper tail quantiles fall inside the
  predictive envelope, motor by motor, with the motor as the resampling unit.
- **Data required:** none beyond the frozen cohort; the machinery exists
  (`hierarchy.posterior_motor_shape`, `score.motor_cluster_bootstrap`).
- **Runnable now?** YES on currently allowed data. `NOT_RUN — COMPUTE_BUDGET` in this probe.
- **Admissible?** Yes — it carries a killer, and part of the killer has already fired.

### H4 — state-conditioned hazard (the 8 states genuinely differ)

The tail is an aggregation artifact across states: each state has its own hazard, and pooling
states with different shapes produces an apparently heavy pooled tail.

- **Support would look like:** the per-state model resolving above the pooled models by more than
  the floor. It does not. M6_SEMI_MARKOV_STATE_DEPENDENT — which IS exactly this hypothesis, one
  free Weibull shape per state, 8 free parameters — scores 3.4298889710, 4th of 9, and its frozen
  contrast against the M3 reference is +0.004444362107038025 BCa [−0.06918232190147591,
  +0.08741095807674587] → `NOT_ESTABLISHED`. Against the F-side candidate the M6 contrast is
  −2.803367e-03 [−1.899034e-02, +1.391343e-02], whose whole interval lies inside ±0.042 and is
  therefore recorded `SCIENTIFICALLY_NULL`.
- **What would kill it:** exactly what is observed — spending 8 free parameters on per-state
  shapes buys no resolved improvement over 1–2 parameter pooled models. The fitted per-state
  shapes span only 0.5437856270600075 to 0.7289889570450139, a ratio of 1.3405815100084815; all
  eight sit below 1, so every state is individually heavy-tailed. **Read as: all eight per-state
  point estimates are consistent with a within-state heavy tail.** These are eight POINT ESTIMATES
  with **no interval computed on any of them**, so this is not a CI-bound result and cannot carry a
  conclusion by itself. An earlier draft asserted "state conditioning does not explain the tail
  because the tail is present within every state"; that asserted more than the arithmetic supports
  and is **withdrawn**. The interval-bearing version is `NOT_COMPUTED` and is named in the
  discriminator below.
- **Next discriminator:** none needed for the strong version — it is already effectively removed.
  The residual live version is narrower: are the states 6–8 shapes genuinely lower than states
  1–5, with the motor as the resampling unit? That requires a motor-clustered contrast on a
  per-state shape statistic, not the p-values in §3.
- **Data required:** none beyond the frozen cohort.
- **Runnable now?** YES. `NOT_RUN — COMPUTE_BUDGET`.
- **Admissible?** Yes — and its killer has largely fired already.

### H5 — censoring / long-dwell artifact

The frozen cohort excludes right-censored events entirely, so the longest dwells are
systematically absent and the surviving sample misrepresents the tail.

- **The specific risk, stated precisely.** 54 of 1080 state-1–8 events (5.0%) are dropped; their
  median duration is 83.35 s against 2.42 s for the retained events; 14 of the 20 longest dwells
  are among the dropped; and the drop rate rises monotonically with state dwell scale, from 0.0000
  in states 1–3 to 0.1414 in state 8. Whatever lives in the far tail of the slow states is
  under-observed here — and the far tail of the slow states is precisely where a third timescale
  would be visible. **H5 is therefore not only a rival to H2; it is the reason H2 may be
  untestable on this cohort.**
- **Support would look like:** the model ranking changing materially when censored events are
  restored as survival contributions — specifically, the M2-over-M3 gap narrowing or reversing
  under a censoring-aware likelihood on the same motors.
- **What would kill it:** the ranking being stable under a censoring-aware refit. The §3 side
  computation gives the first directional evidence and it does not favour the naive version:
  restoring censored events moves fitted shapes DOWN (heavier tail) in every affected state, by
  0.028885 to 0.084744. Exclusion appears to bias toward a LIGHTER tail, so the observed heavy
  tail is unlikely to have been manufactured by the exclusion. That kills the "artifact creates
  the tail" reading; it does NOT kill the "artifact hides the third timescale" reading.
- **Next discriminator:** rescore the full frozen 9-model family under a censoring-aware
  likelihood (`hazard_survival.log_event_density` plus an explicit `log S` term for censored
  events) on a cohort variant that retains the 54 censored events, with motor-clustered intervals
  and the same split rule. This is a NEW cohort and must be declared as such — it can never be
  compared to the frozen leaderboard as though it were the same scoring path.
- **Data required:** none beyond the source events already present; the censored records exist in
  the source and are excluded at cohort construction, not missing from the data.
- **Runnable now?** YES on currently allowed data, with one hard condition: it requires a NEW,
  separately named cohort and a pre-registered prediction, because it changes the scored sample.
  `NOT_RUN — COMPUTE_BUDGET` in this probe.
- **Admissible?** Yes — it carries a killer, and half of it has already fired.

---

## 5. What M4_MIXTURE_K3 does and does not license

M4 is the closest already-fitted structure to H2: a three-component exponential mixture with
canonical rates [7.410301079721995, 1.0269138959905078, 0.2252632502537158] and weights
[0.45920454549250384, 0.4220782557784245, 0.11871719872907172].

**It licenses three things.**

1. **Three timescales are estimable here.** B4C10 at full frozen `N_boot = 2000` (1994 completed,
   6 failed) returned U2 collapse fraction 0.0050150451 (fires at ≥0.25), U3 span
   0.4332708748 decades (fires at ≥2.0), and U4 omega_3 95% CI [0.030746372918754247,
   0.28838105457744573] (fires only if lo < 0.006305 AND hi > 0.25). All `OK`;
   `IDENTIFIED_ON_THIS_COHORT`. The third component does not collapse. So "unidentifiable" is not
   available as a reason to dismiss H2 on this cohort.
2. **It scores well.** 3.4241154309, 3rd of 9 on the frozen held-out motor-equal leaderboard,
   ahead of M3 (3.4343333331) and M6 (3.4298889710).
3. **It does not settle the question.** Its contrast against the F-side candidate is
   −8.576907e-03 [−7.114909e-02, +5.540236e-02] → `NOT_ESTABLISHED`, recorded `SUB_FLOOR_EFFECT`.

**It licenses none of the following.** M4 fitting well is not evidence that three kinetic rates
exist in the motor. A three-component exponential mixture is also a flexible three-parameter shape
family, so on this data H1 and H2 make near-identical predictions — that is the core
identifiability problem of this whole note. B4C10's `IDENTIFIED_ON_THIS_COHORT` is a statement
about estimator stability under resampling, not about physical reality; the same verdict would be
returned for a mixture fitted to data generated by a smooth heavy-tailed shape with no discrete
rates at all. And M4 ranking 3rd while its contrast is `NOT_ESTABLISHED` is exactly the
underpowered case: 19 holdout motors cannot separate these families.

**Prospectivity, stated plainly.** B4C10 is `NOT_SATISFIED` and structurally unattainable — its
prediction and result shared one commit (D9). The F-side scoring is also `NOT_SATISFIED`. Nothing
in §5 is a prospective result.

---

## 6. The identifiability collision that dominates all five

Three of the hypotheses are competing to explain the same single number — the fitted Weibull
shape — through different routes, and on this cohort they occupy overlapping ranges:

| source of shape variation | range of the shape parameter | ratio |
| --- | --- | --- |
| H4, across the 8 states (frozen M6 params) | 0.5437856270600075 → 0.7289889570450139 | 1.3405815100084815 |
| H3, ±1 population SD across motors (F-side `exp(mu ± tau)`) | 0.5489252595745205 → 0.7926675834629069 | 1.4440355396968148 |

These two ranges nearly coincide. A shape difference of this size can be produced by state
identity, by motor identity, or by neither — and 19 holdout motors × 233 events cannot tell them
apart. Any discriminator that varies only the model family, on only this cohort, will keep
returning `NOT_ESTABLISHED`. That is the D10 lesson applied forward: the frozen CI rule will
happily resolve a difference of any magnitude whose sign is consistent across motors, and will
equally fail to resolve a large difference whose sign is not.

**The consequence for design.** The highest-information next steps are the ones that change what
is OBSERVED, not the ones that change what is FITTED.

---

## 7. Admissibility audit — does every hypothesis carry a killer?

| # | hypothesis | killer named? | killer already fired? | decisive discriminator on current data? |
| --- | --- | --- | --- | --- |
| H1 | shape-only lognormal | YES | no | partially (LOMO rank stability) |
| H2 | three-timescale kinetics | YES | no | **NO — transfer required** |
| H3 | motor heterogeneity | YES | partially (F-side did not absorb it; C02 heterogeneous world gave 0.0050) | partially |
| H4 | state-conditioned hazard | YES | **largely — M6 spends 8 parameters and resolves nothing; all 8 per-state shapes are below 1** | strong version already removed |
| H5 | censoring artifact | YES | partially — direction of the §3 sensitivity contradicts the "creates the tail" reading | YES, on a newly declared cohort |

All five are admissible. None is currently a bare hypothesis without a falsifier.

**H2 is the weakest-tested and the most consequential.** It is the only one whose decisive test
cannot be run in this repository, and it is the one B4C02's winning generator points at. That
asymmetry — most interesting, least testable here — is the honest headline of this note.

---

## 8. Discriminator queue, ordered by expected information gain (`DESIGN_ONLY`)

Ordering is a design judgement, not a measured quantity. No threshold below is evidential.

1. **Censoring-aware rescore on a newly declared cohort variant** (H5, and H2 indirectly). Highest
   value per unit compute: it uses data already in hand that the frozen cohort throws away, and
   the discarded events are exactly the long dwells the hypotheses disagree about. Requires a new
   cohort name, a pre-registered prediction committed before the run, and it may never be compared
   against the frozen leaderboard as if it were the same scoring path.
2. **Per-motor posterior predictive check of the fitted hierarchy** (H3). Uses existing machinery,
   resamples motors, and can fire a killer without any new data.
3. **Leave-one-motor-out rank stability of the 9-model family** (H1 vs H2/H3). Tests whether the
   ordering is a property of the population or of a few motors.
4. **Motor-clustered contrast of per-state shapes, states 6–8 versus 1–5** (H4 residual version).
   Replaces the non-inferential rank correlations of §3 with a motor-unit interval.
5. **Load / PMF / temperature transfer dataset** (H2, decisive). **Transfer required.** This is the
   only entry that can separate a kinetic rate from a descriptive shape, because a kinetic rate is
   required to move in a predicted direction under a physical perturbation while a descriptive
   shape parameter carries no such obligation. Until such data exists, H2 remains a
   **mechanism discriminator pending**.

Items 1–4 are runnable on currently allowed data; all four are `NOT_RUN — COMPUTE_BUDGET` for this
probe, which held itself to short single-process computations while two long runs are in flight.
Item 5 cannot be produced by any modelling in this repository. This mirrors the standing position
that `P4` transfer, `P5`, and `P7` are not closable by internal work.

---

## 9. Provenance of every computed number in this note

Values quoted from frozen artifacts:

- B4C02 fractions, winner frequencies, verdict —
  `hierarchical-aif/results/motor_stack_aif/B4C02_CORRECTED_FULL_RESULT.json`.
- Generator constants and the `rightCensored: False` fact —
  `audits/phase-b/b4-identifiability-robustness-runner.py` lines 883–932 (frozen, read-only).
- M6 per-state shapes, M6 contrast intervals, M6 scores —
  `audits/phase-b/b3-model-competition-result.json` →
  `cohorts.derived_eligible_1_to_8.{fitted,contrasts,scores}.M6_SEMI_MARKOV_STATE_DEPENDENT`.
- M6 definition (one mean-one Weibull shape per state, fitted independently) —
  `audits/phase-b/b3-model-competition-runner.py` lines 265–271 and 443–462.
- Leaderboard, M4 canonical parameters, B4C10 diagnostics, F-side fit and contrasts, floor,
  M4/M6/M7 per-motor contrasts — the established-facts record carried into this probe.

Values computed by this probe (commands are in the report accompanying this note):

- Rate-ratio and time-share comparison of §2.
- The censoring census and per-state table of §3.
- The Spearman rank correlations of §3, explicitly non-inferential.
- The censoring-sensitivity Weibull refits of §3, train partition only, `DESIGN_ONLY`, no interval.

## 10. Limitations

- No hypothesis in this note is tested by this note. Sections 3 and 6 supply measurements that
  constrain the design; they establish nothing about the motor.
- The §3 censoring-sensitivity refits use a free two-parameter Weibull in seconds. That is not the
  frozen scoring path (mean-one normalised `y` with frozen `scale_N`), so its shapes are not
  interchangeable with the frozen M6 parameters and the deltas carry no interval.
- Whether the direction of the censoring bias survives the mean-one renormalisation used by the
  frozen path is `NOT_COMPUTED`.
- Nothing here touches the held-out mark channel. Any hypothesis about transition structure rather
  than dwell duration is `NOT_CHECKED — would require holdout access` and would be
  retrospective-only under D5 in any case.
- No P-level moves. `P8` remains `FULL_PARITY = false`; the first unsatisfied level remains `P4`
  transfer, which is the level H2's decisive discriminator sits behind.

NEXT_ACT = Draft `hierarchical-aif/protocols/CENSORING-AWARE-COHORT-PREDICTION.md` — a
pre-registered prediction whose prospectivity is NOT decided by this prose but by the commit
graph (D9), for discriminator 1: a newly named cohort
variant retaining the 54 right-censored state-1–8 events as survival contributions, rescoring the
frozen 9-model family with motor-clustered intervals, declared non-comparable to the frozen
leaderboard, and stating in advance which outcome removes hypothesis 5.
