# Motor-Stack Markov Blanket — Justification, Not Assertion

**Status:** `BUILDER_SUPPORT_PROBE` · **Probe:** 10 · **Date:** 2026-07-22
**Gate mapping:** informs `H-AIF-G6` (scope ruling). **Moves no P-level. Changes no frozen verdict.
Creates no claim.**
**Split boundary declared:** `TRAIN_ONLY` for every new read performed for this document.
Holdout motor/event counts quoted below are re-echoed already-published summary values, not new reads.
**Held-out mark channel:** `nextStateN` / `direction` / `jump` were **NOT** read, printed, or reasoned
from at any point in producing this document.

---

## 0. Why this document exists

A Markov blanket is a **modelling choice about where to cut the world**, not a fact discovered in
the data. Any partition can be *written down*; only some partitions carry the conditional
independence that makes them worth anything. This document therefore does two things the codebase
did not previously do in one place:

1. it names, for every variable in the motor stack, which side of the cut it is on **and why**;
2. it states, for every one of those assignments, **what breaks if the assignment is wrong**.

The second column is the load-bearing one. A partition with no stated failure consequence is a
diagram, not a model.

### 0.1 Two blankets, never to be conflated

The single largest source of category error in this lane is that there are **two** candidate
blankets, and only one of them is instantiated.

| | **Blanket A — the ANALYST's** (instantiated) | **Blanket B — the MOTOR's** (not instantiated) |
|-|-|-|
| internal states | `mu`, `tau`, and the per-motor belief `q(eta_m)` from `hierarchy.posterior_motor_shape` | motor chemistry / mechanics / switch complex |
| sensory states | recorded fields of `events[]` | ligand binding, PMF sensing, torque load sensing |
| active states | choice of next experiment — exercised at ORCHESTRATE level, **outside** the dataset | stator engagement / disengagement, switch |
| external states | the physical motor, the cell, and the apparatus | everything outside the motor |
| status | scored on the frozen split | **entirely unobserved in this dataset** |

Everything scored in `hierarchical-aif/` is Blanket A. `free_energy.py:7-10` says this in the module
docstring, and `docs/MOTOR-STACK-AIF-SCOPE-RULING.md` §2 says it again: computing `F_motor` is the
analyst's fitting objective and it is not evidence that the organism performs inference. Blanket B
is `DESIGN_ONLY`. Where this document says "internal state" without qualification, it means
internal to **Blanket A**.

### 0.2 The formal condition being asserted

The standard partition is `external psi`, `sensory s`, `active a`, `internal mu`, with blanket
`b = s ∪ a`, and the substantive requirement

```text
mu  ⫫  psi  |  b
```

That is the *whole content* of the choice. Naming boxes costs nothing; the conditional independence
is what would have to hold. §5 examines whether it does, and §6 states the reason it currently
cannot be checked.

---

## 1. Data actually available (verified, this session)

Source: `experiments/data/wadhwa-2022-events.json`, schema `uni.flagellum.observed-events/1.0.0`,
protocol `UNI-FLAGELLUM-OBS-001`. Loaded via `motor_stack_aif._bridge.b3().load_events()` and
`_bridge.frozen_cohort()`.

| quantity | value | how obtained |
|-|-|-|
| event records, all partitions | 1349 | `len(b3().load_events())` |
| event record fields | 12: `direction`, `durationS`, `enteredAtS`, `eventAtS`, `eventId`, `jump`, `motorId`, `nextStateN`, `partition`, `rightCensored`, `splitRemainder`, `stateN` | key names only |
| motor records | 129 | `len(d['motors'])` |
| motor record fields | 8: `analysisSamples`, `motorId`, `nominalElectrorotationSpeed`, `partition`, `runCount`, `sampleIntervalS`, `sourceSamples`, `splitRemainder` | key names only |
| frozen cohort `derived_eligible_1_to_8` | 80 train motors / 793 train events; 19 holdout motors / 233 holdout events; states `(1..8)` | `frozen_cohort()` (already-published values) |
| TRAIN-only `nominalElectrorotationSpeed` levels | 7 levels over exactly 80 train motors: `{50: 5, 100: 6, 150: 6, 200: 17, 250: 20, 272: 9, 300: 17}` | new TRAIN_ONLY read, this session |
| TRAIN-only `sampleIntervalS` | one distinct value, `0.01999999999998181` s, for all 80 train motors | new TRAIN_ONLY read, this session |
| TRAIN-only `runCount` | 26 distinct values spanning 3 to 83 recordings per motor | new TRAIN_ONLY read, this session |
| holdout-side values of the three fields above | **NOT_READ** — deliberate channel-spend avoidance | — |

**The motor record contains no load, no PMF, no stator number, no temperature, no viscosity, and no
CheY-P field.** That is a schema fact, verified above, and it drives §4 and §6.

---

## 2. The partition

Legend: `INT` internal (Blanket A) · `SENS` sensory · `ACT` active · `EXT` external ·
`OBS-BLANKET` an element of the recorded blanket surface · `META` not a state at all.

### 2.1 `durationS` — **SENS** (observed blanket, `Lmotor-0`)

**Justification.** It is the channel — the only channel — from which `mu`, `tau` and `q(eta_m)` are
updated. It is causally downstream of the motor's hidden dynamics and upstream of nothing in the
model. `hierarchy.motor_log_marginal` consumes exactly the normalised `y` derived from it, and the
frozen NLPD is published in seconds as normalised-`y` NLPD `+ log scale_N[state]`.

**Consequence if wrong.** If `durationS` is not conditionally sufficient — that is, if it also
carries apparatus and analysis-pipeline state — then the sensory channel is contaminated and
`eta_m` absorbs instrument variation along with motor variation. One contamination route is closed
on the train side and one is open:

- **closed:** `sampleIntervalS` is a single constant `0.02` s across all 80 train motors, so
  dwell-time resolution does not vary between train motors.
- **open:** `runCount` spans 3 to 83 per motor. Recording effort is *not* constant, it is nested
  inside `motorId`, and it therefore travels with `eta_m`. Whether that matters is
  **NOT_MEASURED**; it is a live confound route, not a demonstrated one.

### 2.2 `rightCensored` — **SENS**, but *excluded* rather than conditioned in the frozen cohort

**Justification.** It is a recorded fact about the *observation process*, produced jointly by the
motor and the recording window. `hazard_survival.log_event_density` takes a censoring vector and
`hierarchy.motor_log_marginal` threads `censored_motor` through, so the F-side implementation is
built to condition on it.

**Consequence if wrong.** The frozen cohort **excludes right-censored events entirely**. Exclusion
is not conditioning. Dropping the longest, truncated dwells is a length-biased selection on the
sensory channel, which shifts the tail the shape parameter is estimated from. This is already on
record as `Lmotor-1 ABSENT in B3` in `docs/GAP-AUDIT-FULL-HIERARCHICAL-MOTOR-MODEL.md:40`. The
magnitude of the induced bias is **NOT_MEASURED** in this document. If the classification is wrong
— if censoring is really an external nuisance independent of shape — nothing breaks; if it is
right, every shape estimate on this cohort carries an unquantified selection bias.

### 2.3 `stateN` — **SENS / conditioning index** (`Lmotor-3`)

**Justification.** Recorded per event; selects the frozen per-state normalisation `scale_N`. It is
the observed index of motor occupancy that makes dwell times from different stator numbers
commensurable.

**Consequence if wrong.** `stateN` is arguably itself a **reconstruction** — a stator number
inferred by a step-detection procedure from a bead trace — rather than a directly recorded
measurement. Under the truth contract a reconstruction may not be relabelled observed, and whether
this field earns the `OBSERVED` label depends on source pinning that this document did **not**
verify (**NOT_CHECKED — would require the raw archive, which is `BLOCKED_EXTERNAL`**). If a
`stateN` assignment is wrong, `y = durationS / scale_N[stateN]` is mis-normalised *and* the
published seconds-scale NLPD is shifted by `log scale_N[state]` for that event — the error enters
twice, once in the likelihood and once in the reporting scale.

### 2.4 `motorId` — **META. Not a state.**

**Justification.** `docs/DATA-CHANNEL-SPEND-LEDGER.md:44` rules it "Structural, not an observable",
permits it for "Defining the split; motor-cluster resampling", and forbids "Using motor identity as
a predictor". Its two legitimate roles are (a) the frozen split `sha256_mod5(motorId)==0 =>
holdout` and (b) marking the exchangeable unit — `events.split_by_motor` carries the comment
"Group events by motor - the experimental unit. Never group by event."

**Consequence if wrong — and this one is not hypothetical.** **D1** is exactly the failure mode.
Per `ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md:30`, the C11 bootstrap "regrouped resampled
motors by `motorId`, collapsing K draws of a motor into one K-fold group. 80 draws → 46 groups at
the declared seed." The objects being grouped there were bootstrap **draws**, which are
exchangeable by construction; grouping them by the identity label destroyed that exchangeability.
The lesson generalises: a grouping key is safe only where the grouped objects are the units it
indexes. `P6` for C11 U4 is withdrawn until the corrected run lands; `P6` for duration-only B3/B4 is
unchanged.

### 2.5 `eta_m`, the per-motor log-shape — **INT (of Blanket A)**

**Justification.** `eta_m ~ Normal(mu, tau^2)`, `k_m = exp(eta_m)`, integrated out by 33-node
Gauss-Hermite quadrature and **never estimated as a free parameter**. The whole model carries 2 free
parameters (`mu`, `tau`), so parameter count does not grow with motor count — `hierarchy.py:14-17`
records that this is the point of the constraint. `posterior_motor_shape` returns `q(eta_m)` as a
mean/sd pair; that is a belief held by the analyst.

**Consequence if wrong — two distinct failures.**
- If `eta_m` is read as an internal state **of the motor**, the document has asserted that the
  organism carries the representation. `free_energy.py:7-10` and the scope ruling both disclaim
  that reading, and the B3 result's own `notEstablished[0]` disclaims it as well.
- If `eta_m` is in fact absorbing **external** variation, then it sits on both sides of the cut and
  the partition is invalid as a blanket. This is the strongest objection and it gets §6 to itself.

**Unit note.** `tau` here is the population SD of the log-shape and is **dimensionless**. It is not
a torque. The thermodynamic `tau * delta_theta` is a different quantity with different units and is
never mixed with variational free energy in this stack.

### 2.6 Latent kinetic mode `z_i` (`Lmotor-2`) — **EXT, declared and NOT INSTANTIATED**

**Justification.** `hierarchy.py:11` records `Lmotor-2 kinetic mode : NOT INSTANTIATED - no
identifiable capacity`, and `hierarchy.py:19` records the reason: "Adding Lmotor-2 policies would
add unidentifiable capacity, not testability." With 793 training events over 80 motors against a
corrected motor-equal resolution floor of ≈0.042 nats (BCa half-width of the narrowest frozen B3
contrast, M4_MIXTURE_K3: BCa width 0.08414086126525253), a per-event hidden mode cannot be
constrained. Declaring the layer external and empty is a *choice recorded in code*, which is the
correct way to hold a boundary.

**Consequence if wrong.** If a real kinetic mode drives dwell statistics, the mean-one Weibull with
a per-motor shape is a marginalisation over it, and the fitted shape is a mixture artefact rather
than a motor property. Note what the evidence says about *detecting* that: **B4C02** (landed,
`0633988d…`, full frozen N=200/generator, 600 sims, 0 failures) found M2-over-M3 at frac 0.9400 for
`three_timescale_heavy_tail` but 0.0050 for both `weibull_gamma_blend` and
`per_motor_heterogeneous_weibull` — 1 of 3 generators — so the frozen `GENERATOR-ROBUST_ADVERSE`
label was **REFUTED**. Heavy-tailed dwell shape does **not** uniquely identify a hidden-mode
structure. The `Lmotor-2` omission is therefore not currently detectable from shape alone.

### 2.7 External biological conditions — **EXT, UNOBSERVED IN THIS DATASET**

Load, PMF, stator state, temperature, viscosity, CheY-P condition.

**Justification.** §1 verified that the 8-field motor record contains none of them. The nearest
recorded quantity is `nominalElectrorotationSpeed`, which
`reports/ULTRACODE-TRACK-D-VERIFICATION.md:195` calls "the only manipulated quantity in the
repository", and which is "a **per-motor scalar label** with no onset". This session independently
confirmed 7 levels over the 80 train motors: `{50: 5, 100: 6, 150: 6, 200: 17, 250: 20, 272: 9,
300: 17}`.

**The distinction that matters: `UNOBSERVED` is not `ABSENT`.** These variables act on every motor
in the recording. They are missing from the *record*, not from the *world*. The consequences run
in both directions:

- Treating them as **absent** would license reading the fitted model as a description of motors in
  general, when it is a description of motors under whatever unrecorded conditions happened to
  obtain. Every unsampled condition is `extrapolation-only`, never `supported`.
- Treating them as **unobserved external states** is the honest classification, and it immediately
  implies the model cannot license any condition-conditional statement at all.

**Consequence if wrong.** If any of these varies *within* a motor during recording and materially
moves dwell statistics, then even the per-motor `eta_m` is a time-average over a varying external
state, and the exchangeability of events within a motor — the assumption `motor_log_marginal`
relies on when it integrates a motor's events jointly against one `eta_m` — fails. That is
**NOT_CHECKED**: no within-recording condition timeseries exists in this dataset.

### 2.8 Action / policy status — **ABSENT. The active set is empty.**

Treated in §3 as a required ruling.

### 2.9 Remaining recorded fields

| field | class | note |
|-|-|-|
| `sampleIntervalS`, `analysisSamples`, `sourceSamples`, `runCount` | **EXT — observation-process state** | Constant `0.02` s interval on train motors; `runCount` 3–83, nested in `motorId`, an open confound route (§2.1) |
| `enteredAtS`, `eventAtS`, `eventId`, `splitRemainder`, `partition` | **META — bookkeeping** | Ledger line 45: "Not scientific observables"; forbidden use is "Use as covariates" |
| `nextStateN`, `direction`, `jump` | **OBS-BLANKET, quarantined** | Train-side available; holdout side is D5-burned, `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET`, and `events.load_events` raises `HoldoutMarkAccessError` unless the caller acknowledges it in writing. Not used here. |

---

## 3. Required rulings, stated plainly

### R1 — The active channel is ABSENT, so the blanket is incomplete in the formal sense

There is no action field in the event record and no action field in the motor record. The set is
**empty, not small**. `docs/MOTOR-STACK-AIF-SCOPE-RULING.md:51` records this, and it is structural:
no additional quantity of Wadhwa-2022 passive recording would create the channel.

Therefore, in the standard partition `b = s ∪ a`, this stack has `a = ∅` and `b = s`. **A partition
without active states is not a full Markov blanket.** What is instantiated is a *sensory-only
boundary* — a conditional-independence screen over a passively observed system. The document says
this rather than presenting the partition as complete, because the missing half is precisely the
half that would carry any agency reading. The blanket is incomplete, and the incompleteness is
declared, not repaired by wording.

### R2 — F-side blanket is testable; G-side active policy is design-only until intervention

`F_motor = E_q[ ln q(Theta, eta, z) - ln p(o, z, eta, Theta) ] = complexity - accuracy` is a
belief-update objective over *recorded* observations. It needs a likelihood, a hierarchy over the
experimental unit, and an approximate posterior — all three exist here, and the F-side model was
scored on the frozen split (held-out motor-equal NLPD `3.4326923382675303`, 2 free params
`mu = -0.41607215987582913`, `tau = 0.18372082607308418`, train NLL `575.6701064153622`,
determinism proven byte-identical over two full executions, independent-oracle residual exactly
`0.0`).

`G_motor(pi)` ranges over **policies over actions**. With `a = ∅` there is nothing for `pi` to range
over. G-side is `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER`, and the fence is enforced in code:
`free_energy.py:12-14` records that there is deliberately no expected-free-energy function, and
three separate tests assert the absence
(`test_fside_motor_stack.py::test_no_expected_free_energy_function_exists`,
`test_F_motor_observational_objective.py`, `test_no_G_biological_claim_in_passive_data.py`).
**F is an objective over beliefs; G would be an objective over policies. They are not the same
quantity and are never summed.**

### R3 — `motorId` is metadata and a grouping key, never a state

See §2.4. The forbidden use is naming motor identity as a predictor. **D1 is the recorded cost of
using the grouping key where the objects being grouped were not the units it indexes.**

### R4 — External biological conditions are UNOBSERVED, not absent from the world

See §2.7. The blanket may therefore license statements about *the recorded observable*, and may not
license statements about how motors behave under conditions the record does not carry.

### R5 — This partition is a modelling choice, and it is currently justified by design coherence
rather than by a resolved predictive gain

Stated bluntly because it is the weakest point in the lane, and it is adverse:

The F-side hierarchy is numerically the same object as the frozen M7 baseline. `exp(mu) =
0.659632669755436` against M7 `k = 0.6596322379287862`; `tau = 0.18372082607308418` against M7
`tau = 0.18372185667134974`. The M7 contrast came out at `+2.506984e-07` nats
`[+1.604451e-07, +3.374688e-07]` — `RESOLVED_ABOVE` by the frozen CI rule, and **SCIENTIFICALLY_NULL**,
roughly 168 000× below the ≈0.042 nats floor. That pairing is **D10**: a paired motor-cluster
bootstrap resamples motors, so it resolves a difference of any magnitude whose sign is consistent
across motors. The floor states what is scientifically material; the bootstrap states only what it
will call.

The honest reading: **the blanket partition as scored has not been shown to buy resolved predictive
content over a model carrying the same two numbers.** Its justification today is coherence of the
partition and identifiability discipline, not a resolved win. The candidate ranks 5th of 10 combined.

---

## 4. What the partition would have to satisfy, and what is checkable

| required property | status | why |
|-|-|-|
| `mu ⫫ psi \| b` (internal independent of external given the blanket) | **NOT_CHECKED** | `psi` — load, PMF, stator number, temperature, viscosity, CheY-P — is unobserved (§2.7). An independence claim cannot be tested against a variable that was never recorded. |
| Events exchangeable within a motor given `eta_m` | **NOT_CHECKED** | Requires a within-recording condition timeseries; none exists. |
| Motors exchangeable given `(mu, tau)` | **partially supported** | `population_log_likelihood` assumes it. `nominalElectrorotationSpeed` varies between motors at 7 levels, which is a *known* between-motor inhomogeneity the model does not condition on. |
| Sensory channel free of instrument variation | **partially supported** | `sampleIntervalS` constant at `0.02` s on train motors; `runCount` 3–83 remains an open route. |
| Active states well defined | **FAILS by construction** | `a = ∅` (R1). |

---

## 5. The strongest objection

**Objection.** If the external states that actually drive dwell statistics — load, PMF, stator
number — are unobserved, and if they differ between motors, then a per-motor latent fitted to
per-motor dwell data will soak up that between-motor external variation. Under that reading `eta_m`
is not an internal property of a motor at all; it is a **condition-absorbing nuisance term wearing
an internal-state label**. Both readings produce the same likelihood, the same fitted `(mu, tau)`,
and the same held-out NLPD.

**This objection is not speculative here — the design makes it unfalsifiable on the current data.**
The one recorded condition proxy, `nominalElectrorotationSpeed`, is **constant within each motor**.
It is therefore perfectly nested inside `motorId`, and `eta_m` is indexed by `motorId`. There is
**zero within-motor contrast** in the only external covariate the dataset carries. A design with no
within-unit variation in a covariate cannot separate that covariate from a unit-level latent — the
two are collinear by construction, not by bad luck.

**The current data cannot distinguish the two readings.** That is a statement about identifiability,
not about effect size. It is not a finding that `eta_m` is internal, and it is not a finding that it
is external. Both remain live.

### 5.1 Discriminators, ranked by strength

| id | design | what separates the readings | availability |
|-|-|-|-|
| **D-1** | **Within-motor load step.** Hold a motor at level `s1`, step to `s2` at a recorded onset `t_step` timestamped against dwell boundaries, hold a post-step window. Randomise `(s1, s2, t_step)` per motor from a pre-registered schedule. Refit `q(eta_m)` on the pre and post windows separately. | Internal-state reading predicts `q(eta_m)` is **stable across the step** relative to its own posterior sd. Absorber reading predicts it **shifts with the step**. Within-unit, so it does not depend on between-motor exchangeability. | **`PROSPECTIVE_NEW_DATA_ONLY`.** Blocked twice: `nominalElectrorotationSpeed` has no onset time, and the raw archive is `BLOCKED_EXTERNAL` (`B4C06.analysisStartIndex.3400`, `rawSha256 c14de12c…` absent). |
| **D-2** | **Test–retest on the same motor.** Two recording sessions separated in time under nominally identical conditions; independent `q(eta_m)` from each. | Internal reading predicts across-session agreement beyond what the motor's condition assignment explains. Absorber reading predicts agreement no better than the condition label predicts. | **`NOT_CHECKED`.** `runCount` exists per motor but the frozen cohort does not separate sessions into independent estimates; re-derivation needs the raw archive (`BLOCKED_EXTERNAL`). |
| **D-3** | **Between-motor covariate association, train-only.** Regress the posterior `eta_m` mean from `hierarchy.posterior_motor_shape` on `nominalElectrorotationSpeed` across the 80 train motors, with a motor-level bootstrap. | A resolved association is evidence `eta_m` carries external variation. | **Runnable today** on train data with no new spend — and it is the **weakest** of the three. |

### 5.2 Why the only runnable discriminator is the weakest — stated as the honest headline

D-3 is the one test available now, and three separate limits cap what it could deliver:

1. **It cannot establish direction.** Even a resolved association is confounded unless level
   assignment was exogenous to the motor. Whether assignment was randomised is **NOT_CHECKED** and
   verifying it requires the raw archive (`BLOCKED_EXTERNAL`).
2. **A null result would establish nothing.** 7 levels with cells of 5, 6, 6, 17, 20, 9, 17 motors
   is thin. An interval crossing zero is `NOT_ESTABLISHED`, never "no association" and never
   "independent". **Underpowered is not equivalence.**
3. **A positive result would not rescue the partition either.** It would show `eta_m` is *partly*
   external, which invalidates the internal-state label without telling us what the internal state
   would have been.

**D-3 was NOT_RUN in this probe** — deliberately. It would produce a new analysis number, and a
builder-support probe may not create a claim. It is specified here precisely enough to be
pre-registered and run as its own bounded change, with its prediction committed first.

---

## 6. What would kill this lane

| kill condition | effect |
|-|-|
| D-1 shows `q(eta_m)` moves with a within-motor load step by more than its posterior sd (**`DESIGN_ONLY`**: the 1x-posterior-sd cut is introduced by this document, is NOT a frozen criterion, and must be pre-registered before any such experiment) | The internal-state reading of `Lmotor-4` is **contradicted**. `eta_m` must be relabelled a condition-absorbing term. The F-side held-out NLPD survives as a predictive statement; its blanket interpretation is withdrawn. |
| D-3 shows a resolved association with the load proxy *and* assignment is shown exogenous | Same relabelling, on weaker evidence, retrospectively only. |
| A within-recording condition timeseries shows the external state varies during a recording | Within-motor event exchangeability fails; `motor_log_marginal`'s joint integration over one `eta_m` per motor is misspecified. |
| `stateN` is shown to be a reconstruction whose error is state-dependent | `scale_N` normalisation and the published seconds-scale NLPD are both biased; the leaderboard ordering would need rechecking. |
| Censoring exclusion is shown to bias the shape estimate materially | Every shape on this cohort carries a selection bias; the ≈0.042 nats floor would need re-derivation. |

**What would NOT kill it, and what would not save it:** any additional quantity of *passive*
Wadhwa-2022 recording. The blocking limitation is the absence of a within-unit manipulated variable
with a recorded onset. That is structural. Transfer to an independent dataset carrying condition
covariates, or intervention, are the two routes — `P4` transfer is the first unsatisfied level on
the ladder, and `P4`/`P5`/`P7` cannot be closed by any modelling in this repository.

---

## 7. Adverse findings and limitations

1. **The blanket partition has not been shown to buy resolved predictive content.** §3 R5. The
   F-side hierarchy equals frozen M7 to ~7 significant figures in both parameters, and the contrast
   against it is `SCIENTIFICALLY_NULL`.
2. **The central conditional independence `mu ⫫ psi | b` is untestable on this dataset**, because
   `psi` was never recorded. §4.
3. **`eta_m` and the sole recorded condition proxy are collinear by design.** Zero within-motor
   contrast. §5.
4. **The blanket has no active half.** `a = ∅`, structurally. §3 R1.
5. **`nominalElectrorotationSpeed` is absent from
   `docs/DATA-CHANNEL-SPEND-LEDGER.md`.** It is a real per-motor field, it is the only manipulated
   quantity in the repository, and it has no ledger row assigning it a split status or a permitted
   claim. This document read it TRAIN_ONLY and declares that spend here. **The ledger gap is a
   defect-shaped finding and should be routed, not just noted.**
6. **`runCount` varies 3–83 per motor and is nested in `motorId`**, so recording effort travels with
   `eta_m`. Impact **NOT_MEASURED**.
7. **Censored events are excluded, not conditioned**, in the frozen cohort. Bias magnitude
   **NOT_MEASURED**.
8. No FLOW card was appended to `reports/FLOW-JOURNAL.jsonl` by this probe, to avoid a concurrent
   write while two long runs are in flight. The parent orchestrator should append it.

---

## 8. Standing frame

```text
Nature supplies the architecture candidate.
The gate supplies the status.
A partition is a choice; only the conditional independence it asserts can be earned.
```

The partition in §2 is defensible as a design. It is **not** established as the correct cut of the
world, and the one measurement that would test its central claim does not exist in this dataset.

NEXT_ACT = Open a defect-ledger row for the unledgered `nominalElectrorotationSpeed` channel (assign it a split status, permitted claim, and forbidden claim in `docs/DATA-CHANNEL-SPEND-LEDGER.md`), then pre-register discriminator D-3 as its own bounded TRAIN_ONLY change — prediction and falsifier committed before the regression of posterior `eta_m` on the 7 train load levels is ever run.
