# F-SIDE DISTINCTIVENESS MAP

**Status:** BUILDER-SUPPORT PROBE. Not a verdict. Moves no P-level, changes no frozen verdict,
creates no claim. It answers one question: *which components of the F-side motor stack are
evidence, and which are architecture?*

**Scope:** the constrained F-side observational projection as implemented in
`hierarchical-aif/src/motor_stack_aif/` and scored by `compare.py` on the frozen
`derived_eligible_1_to_8` cohort (Wadhwa 2022, *E. coli*, 80 train motors / 793 train events,
19 holdout motors / 233 holdout events). Duration-only. Held-out `nextStateN` / `direction` /
`jump` were **not** read by this probe (D5 firewall; `events.load_events(mode='duration_only')`
is the module default and `compare.project_event` allow-lists the duration fields).

**Builder rule applied throughout:** *if a component does not create a new testable prediction on
data this repository holds, it is architecture, not evidence.*

---

## 1. The headline the map has to explain

The frozen record says the F-side candidate reproduces M7 to numerical precision:

| quantity | F-side | frozen M7 | difference | source |
|---|---|---|---|---|
| population shape | `exp(mu) = 0.659632669755436` | `k = 0.6596322379287862` | `+4.318266497715939e-07` (rel `6.546475823066334e-07`) | probe `[header]` |
| shape dispersion | `tau = 0.18372082607308418` | `tau = 0.18372185667134974` | `-1.0305982655611778e-06` (rel `5.6095572091063735e-06`) | probe `[header]` |
| held-out motor-equal NLPD (seconds) | `3.4326923382675303` | `3.4326925890` | `2.5073246989748554e-07` | frozen B3 leaderboard + F-side result |
| frozen contrast S(M7) − S(F-side) | — | — | `+2.506984e-07` `[+1.604451e-07, +3.374688e-07]` **RESOLVED_ABOVE but SCIENTIFICALLY_NULL** | `M4-M6-M7-PER-MOTOR-CONTRASTS-REPORT.md` |

`0.042 / 2.506984e-07 = 167531.98265325985` — the resolved separation sits about
1.7e5 times below the corrected motor-equal resolution floor. **D10 is the reading:** the paired
motor-cluster bootstrap resolves a difference of any magnitude when its sign is consistent across
motors, so `RESOLVED_ABOVE` here is a statement about sign consistency, not about scientific
material. This is a design signal about the model, treated as such below.

**This is a re-derivation of M7, not an independent competitor, at the level of the fitted
predictive density.** The parameterisations coincide exactly on paper:

```
frozen M7 :  k_m = k * exp(tau * z_m),  z_m ~ N(0,1)   =>  log k_m = log k + tau * z_m
F-side    :  k_m = exp(eta_m),  eta_m ~ N(mu, tau^2)   =>  log k_m = mu     + tau * x
```

with `mu <-> log k` and `tau <-> tau`. The residual `~1e-6` is optimiser placement, not model
structure.

### What would have to differ for the F-side model to be a distinct model

None of these is currently implemented. Each is a *structural* change, not a retune:

1. **A different latent link.** `eta_m` on log-shape reproduces M7 by construction. A latent on
   the *scale* (with shape shared), or a joint `(shape, scale)` latent, is a different marginal.
2. **A latent that is not exchangeable across motors** — e.g. indexed by `stateN`, load, or
   occupancy — so the population prior carries structure M7 has no slot for.
3. **A prior that is not Gaussian in log-shape** (mixture, heavy-tailed, or bounded), which
   changes the marginal even at matched mean and variance.
4. **A likelihood M7 does not have** — the censoring branch actually exercised on censored
   observations (see component C4).
5. **A reported quantity M7 cannot produce**, scored against something. `posterior_motor_shape`
   is such a quantity, and it is currently scored against nothing (component C5).
6. **A second observation channel.** M7 is a duration model. Everything the F-side stack currently
   does is also a duration model. Distinctiveness on durations alone is bounded by how much of
   `p(y)` the two parameterisations can disagree about — measured below as `[B]`,
   max `3.8437083222930823e-05` nats per event over a 6-decade `y` grid.

---

## 2. Component map

`is_testable_current_data` = does this component generate a prediction that the frozen cohort can
put a CI around, today, without new data?

| component | is_new_math | is_new_data_use | is_testable_current_data | does_it_differ_from_M7 | does_it_differ_from_M1 | adversary_it_can_beat | falsifier | keep/drop/transfer |
|---|---|---|---|---|---|---|---|---|
| **C1** population prior over log-shape `(mu, tau)` (`hierarchy.motor_log_marginal`, `fit.fit_motor_stack`) | NO — same lognormal random effect on shape as M7 | NO — frozen train split, durations only | YES — already scored | NO (mu = log k, tau = tau; residual `~1e-6`) | YES — median `0.0557` nats/event vs its own `tau->0` limit at the same `mu` (probe `[E]`) | NONE ESTABLISHED. Frozen contrasts: M0 `+0.115291 [+0.013040,+0.227497]` and M5 `+0.031036 [+0.004459,+0.054473]` RESOLVED_ABOVE; M1/M2/M3/M8 NOT_ESTABLISHED | Refit on a cohort where `tau` hits `TAU_MIN` (collapse to M1) or `TAU_MAX`; or an M7 refit that lands at a different `(k, tau)` under the same data | **KEEP as architecture, not as evidence.** It is the model. It is not a *new* model |
| **C2** per-motor latent by 33-node Gauss-Hermite (`hierarchy.gauss_hermite`, `hermegauss`) vs M7's 129-node `hermgauss` | NO — same 1-D Gaussian integral, probabilists' vs physicists' Hermite | NO | Testable but ALREADY ANSWERED NULL: at identical params, max `|dlogp| = 6.453021228480793e-09`, median `8.881784197001252e-16` over a 6-decade `y` grid (probe `[A]`) | NO — the difference is at quadrature noise | YES — this is the machinery that makes C1 a marginal rather than a point shape | NONE. A quadrature choice is not an adversary-beating claim | Raise to 129/257 nodes and show the held-out motor-equal NLPD moves by more than `1e-8` (**`DESIGN_ONLY`** — introduced here for design purposes, NOT a frozen criterion, evidential for nothing) | **KEEP (correct and cheap). ARCHITECTURE.** Node count is not a scientific degree of freedom here |
| **C3** mean-one Weibull hazard/survival parameterisation (`hazard_survival.weibull_log_*`) | NO — identical to frozen M1/M7 mean-one form `lambda(k) = 1/Gamma(1+1/k)` | NO | YES via the normalisation check: `survival_integrates_to_one` returns `0.9999999725282323` at `k = exp(mu)` (probe `[G]`) | NO — same closed form; F-side computes hazard and survival SEPARATELY, M7 emits a fused `logf` matrix | NO — M1 is this exact density at a single shared `k` | NONE by itself | Show the implied density fails to integrate to 1, or that the mean is not 1, at a fitted `k` | **KEEP. ARCHITECTURE** — but it is the component that makes C4 possible, which is the one genuinely distinct capability |
| **C4** censoring branch (`hazard_survival.log_event_density`: uncensored `log h + log S`, censored `log S`) | YES relative to the frozen B3 family — M7's `m7_logf_matrix` has NO censoring path at all | **NO — and this is the finding.** The frozen cohort EXCLUDES right-censored events; `compare.Inputs.__init__` raises if any survive | **NO on the frozen cohort — UNEXERCISED ON REAL DATA.** Correct-by-test only: `test_censoring_likelihood.py` proves `log p(unc) - log p(cens) = log h(y)` exactly; measured at `k = exp(mu)`, `y=[0.5,1,2]` that is `[0.015098891744682486, -0.22082576356905292, -0.456750418882788]` (probe `[H]`) | YES — a capability M7 does not have | YES — a capability M1 does not have | NONE ON CURRENT DATA. It cannot beat any adversary because no scored event exercises it | Re-derive the frozen cohort WITH right-censored events retained, refit, rescore; if the F-side held-out NLPD does not separate from M7 there either, the branch is architecture on that cohort too | **KEEP + TRANSFER.** This is the single strongest *distinctiveness* candidate and it is currently untested on observation. It needs a censored-inclusive cohort or a transfer dataset, not more modelling |
| **C5** `posterior_motor_shape` — the per-motor belief `q(eta_m)` (mean, sd, `k_mean_exp`) | YES relative to M7, which reports POINT estimates only and forms no per-motor posterior | NO — it is never called on holdout | **NO — it is scored against nothing.** Confirmed: `posterior_motor_shape` appears only in `hierarchy.py` and in tests; grep for `eta_sd` / `posterior_motor_shape` / `etaSd` across `hierarchical-aif/results/` and `hierarchical-aif/reports/` returns NO file | YES — M7 has no `q(eta_m)` | YES — M1 has no per-motor latent at all | NONE ON CURRENT DATA, because it emits no scored prediction | Score it: hold out one event per motor, predict it from `q(eta_m)` fitted on that motor's other events, and contrast against the marginal `p(y)`. If the posterior-conditioned score does not beat the marginal, the posterior is decoration | **KEEP + PROMOTE TO EVIDENCE.** Cheapest route from architecture to evidence in this list. Currently **ARCHITECTURE** |
| **C6** no-floor halt policy (`NonFiniteLogDensity`, `compare.NonFiniteScore`) | NO — mirrors B3's declared `NO_FLOOR` | NO | Indirectly: the frozen F-side run completed with no halt, which is an observation about the data, not about the model | NO — same declared policy | NO | NONE | Introduce a floor and show any published score changes — if it does, the previous number was floored | **KEEP. ARCHITECTURE / INTEGRITY CONTROL** |
| **C7** motor-equal scoring (`score.motor_equal_nlpd`, `score.per_motor_means`, `compare.aggregate`) | NO — B3's own aggregation, reproduced | NO — reuses the frozen split, `splitRecomputed: false` | YES as a CONTROL: the independent-oracle check reproduced B3's published motor-equal NLPD with residual **exactly 0.0** on M3 / M0 / M8 | NO — identical rule, applied to both | NO | NONE — it is the ruler, not a competitor | Mutate `to_seconds_scale` to skip the Jacobian; the oracle residual must leave `1e-12` | **KEEP. ARCHITECTURE / MEASUREMENT INSTRUMENT.** Its value is that it makes the F-side number comparable, not that it is new |
| **C8** motor-resampling bootstrap (`score.motor_cluster_bootstrap`, single-construction RNG, resamples MOTORS) | NO — the pattern the frozen C04 cell already uses correctly | NO | YES — every F-side verdict is one of its intervals | NO | NO | NONE | Resample EVENTS instead and show the intervals shrink — that shrinkage is the pseudoreplication the unit rule forbids | **KEEP. ARCHITECTURE / INTEGRITY CONTROL.** Note D10: it has no minimum-effect-size guard, which is why C1's M7 contrast resolved at `2.5e-07` nats |
| **C9** typed D5 firewall (`events.load_events` modes, `HoldoutMarkAccessError`, `compare._FORBIDDEN_EVENT_FIELDS` + `project_event` allow-list) | NO mathematically | NO — its whole purpose is to PREVENT a data use | NO — it makes no prediction about motors | Not comparable — M7 has no such concept | Not comparable | NONE | Request holdout marks without the acknowledgement flag and confirm the raise; add a mark field to the allow-list and confirm a test fails | **KEEP. ARCHITECTURE / GOVERNANCE.** Zero scientific content, high governance value. Explicitly NOT evidence |
| **C10** `K_MIN_REPRESENTABLE = 1/170` domain guard (derived from the IEEE overflow bound `lgamma(171)` finite / `lgamma(172)` overflow) | Marginally — M7 instead CLIPS node shapes to `[1e-3, 1e3]`; F-side assigns `-inf` (zero mass) to out-of-domain nodes. Clipping moves mass to a boundary shape; exclusion removes it | NO | **NO AT THE FITTED OPTIMUM.** At `tau = 0.18372`, M7 clips **0 of 129** nodes and F-side excludes **0 of 33** (probe `[F]`). The policies first diverge at `tau = 0.5` (M7 clips 35/129, F-side excludes 1/33) and grow to `tau = 5` (119/129 vs 26/33) | YES in policy, NO in effect on this cohort | YES — M1 has no quadrature nodes | NONE | Fit on a cohort whose `tau` exceeds ~0.5 and show the two domain policies give different held-out scores | **KEEP. ARCHITECTURE.** A real difference from M7 that this cohort's `tau` never reaches |
| **C11** *(extra)* `free_energy.py` `F = complexity - accuracy`, `gaussian_kl`, `surprise_from_exact_posterior` | NO — standard variational decomposition | NO | **NO.** grep for `free_energy` / `complexity_nats` across `hierarchical-aif/results/` returns NO file — the decomposition reaches no scored artifact | Not comparable — M7 reports an NLL, not a decomposed F | Not comparable | NONE | Report `complexity` and `accuracy` separately for the fitted stack and show the sum reproduces `trainNLL = 575.6701064153622` up to the KL term; then show a model comparison that turns on the split | **KEEP. ARCHITECTURE.** It is the F-side observational projection's vocabulary, not its evidence. The G-side fence (no `expected_free_energy`, enforced by test) stays; the dataset is passive and the action set is EMPTY, which is structural |
| **C12** *(extra)* `score.score_motor_stack` JOINT_PER_MOTOR secondary score | NO mathematically | NO | Not as a contrast — `compare.py` labels it "never contrasted against the others" because it is a DIFFERENT information set (a motor's events inform each other) | YES — M7 publishes only the marginal-per-event score | YES | NONE, by construction — it is excluded from contrasts on purpose | Contrast it against the per-event competitors and watch the comparison become unsound | **KEEP as reported-but-uncontrasted. ARCHITECTURE.** Correctly fenced |

---

## 3. Evidence vs architecture — the verdict of the builder rule

**Components that currently produce a testable prediction on data this repository holds (EVIDENCE):**

- **C1** the `(mu, tau)` population prior. It is the only component with a scored held-out number
  and CI-bound contrasts. Its two RESOLVED_ABOVE results are against M0 and M5; against M1, M2,
  M3 and M8 the result is `NOT_ESTABLISHED` — which is **not** equivalence and **not** "no
  difference". Underpowered is not equivalence.
- **C7 / C8** as the measurement instrument and the interval rule. They are evidence about the
  *scoring*, not about the motor. The independent-oracle residual of exactly `0.0` is a real
  receipt about C7.

**Components that are ARCHITECTURE — correct, tested, and currently producing no new testable
prediction:** C2, C3, C6, C9, C10, C11, C12.

**Components that are ARCHITECTURE TODAY but are one bounded experiment away from evidence:**

- **C5 `posterior_motor_shape`** — needs a scoring rule, not new data. This is the highest
  information-gain-per-cost item in the map.
- **C4 the censoring branch** — needs data the frozen cohort deliberately excludes. Transfer or
  cohort re-derivation required; no amount of modelling on `derived_eligible_1_to_8` can exercise
  it.

---

## 4. What the numbers say about how much room there is at all

Measured on a synthetic log-spaced `y` grid over `[1e-4, 1e2]`, 2001 points — **no dataset was
loaded for this probe**:

| comparison | max `|dlogp|` | median `|dlogp|` | reading |
|---|---|---|---|
| `[A]` F-side 33-node vs M7 129-node, IDENTICAL params | `6.453021228480793e-09` | `8.881784197001252e-16` | the quadrature choice is not a modelling choice here |
| `[B]` F-side vs M7, EACH AT ITS OWN fitted params | `3.8437083222930823e-05` | `1.7188155483349732e-06` | the entire pointwise disagreement between the two fitted models |
| `[C]` F-side vs frozen M1 (`k = 0.6250888335850175`) | `6.818525730561962` | `0.06875493217032691` | the hierarchy is pointwise FAR from M1 |
| `[D]` F-side at `tau = TAU_MIN = 1e-4` vs plain mean-one Weibull at `k = exp(mu)` | `1.7051171770532392e-05` | — | the `tau -> 0` collapse to M1-form is real and numerically clean |
| `[E]` F-side at fitted `tau` vs its own `tau -> 0` limit, same `mu` | `9.747243324446924` | `0.055692754431005076` | `tau` is the whole of what the hierarchy adds over a single shared shape |

**The adverse reading, retained.** `[C]` and `[E]` say the F-side density differs from M1 by a
median of `0.0557`–`0.0688` nats per event on this grid — yet the frozen held-out contrast against
M1 is `+0.000615 [-0.010881, +0.011304]` **NOT_ESTABLISHED**, and the leaderboard gap is
`0.0006145101324697144` nats. Two honest readings, both retained: (i) the log-spaced grid weights
tails the observed durations barely populate, so pointwise divergence overstates scored
divergence; (ii) with 19 holdout motors the scoring rule cannot separate them regardless. The
probe **cannot** distinguish these without an observed-`y`-weighted divergence, which would be a
holdout computation and is **NOT_RUN — COMPUTE_BUDGET / SCOPE**. The grid is synthetic and the
divergence numbers are therefore a property of the two densities, never an observation about
motors.

---

## 5. Limitations of this map

- Every number in §1 that is not from probe output is read from frozen records; nothing here was
  refitted or rescored.
- §4 is computed on a **synthetic** `y` grid. It is a numerical property of two functions. It is
  not observation and carries no predictive claim.
- No held-out score was recomputed. No bootstrap was re-run. The C11/C01 corrected runs in flight
  were not touched, and none of their live counters was read or used.
- This probe read no held-out mark field. Any question here that would need `nextStateN`,
  `direction` or `jump` is **NOT_CHECKED — would require holdout access**.
- The map judges DISTINCTIVENESS, not correctness. Every component listed as architecture is, as
  far as its tests go, correct.
- P-ladder unchanged: `P8` `FULL_PARITY = false`, first unsatisfied level `P4` transfer. This
  probe moves nothing.

---

NEXT_ACT = Draft `hierarchical-aif/protocols/C5-POSTERIOR-MOTOR-SHAPE-SCORING-PREDICTION.md` pre-registering a leave-one-event-out-within-motor scoring rule for `posterior_motor_shape`, contrasted against the marginal per-event score on the SAME 19 holdout motors with the frozen seed 20260717 / nRep 2000 motor-cluster bootstrap — the one component in this map that can move from architecture to evidence without new data.
