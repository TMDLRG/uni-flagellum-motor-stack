# G-SIDE INTERVENTION DISCRIMINATOR — design protocol

**Status: `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER`. This document is a builder-support probe.
It moves no P-level, changes no frozen verdict, and creates no claim.**

---

## 0. FENCE (binding; stated first, never violated below)

- The Wadhwa-2022 `derived_eligible_1_to_8` dataset is **passive**. **The action set is empty.**
  That is **STRUCTURAL, not sample-size-limited** — no quantity of additional passive dwell-time
  observation substitutes for an intervention. This is the reason recorded in
  `hierarchical-aif/docs/MOTOR-STACK-AIF-SCOPE-RULING.md` §3 and enforced verbatim by
  `hierarchical-aif/tests/motor_stack_aif/test_no_G_biological_claim_in_passive_data.py`.
- `expected_free_energy` **does not exist** in `motor_stack_aif` and **must not** be added.
  Its absence is the fence, not an oversight. Two test modules enforce it
  (`test_no_G_biological_claim_in_passive_data.py`, `test_fside_motor_stack.py::
  test_no_expected_free_energy_function_exists`). **This protocol does not propose adding it, and
  no section below may be read as authorising it.** The symbol may be introduced only after
  intervention data with a recorded onset time exists in the repository.
- **F is not G.** `F_motor` is a variational free energy **over beliefs given recorded
  observations** — an analyst's fitting objective, evaluated **after** the observation exists.
  `G_motor(pi)` is an expected free energy **over policies**, scored **before** the action is
  taken, and it presupposes an action to score. Computing `F_motor` asserts nothing about whether
  the organism performs inference. Nothing in this document merges the two.
- **Underpowered is not equivalence.** Every verdict contemplated here is CI-bound. An interval
  crossing threshold is `NOT_ESTABLISHED` — never "no effect", never "equivalent".
- This document proposes **wet-lab data acquisition**, which this repository cannot perform.
  `P5` intervention therefore remains `NOT_ESTABLISHED` and **cannot be closed by any modelling
  in this repository.**

---

## 1. Units and symbol discipline

| symbol | meaning here | unit |
|-|-|-|
| `durationS` | recorded dwell duration | seconds |
| NLPD | negative log predictive density, motor-equal | nats (B3 publishes seconds-scale = normalised-`y` NLPD + `log scale_N[state]`) |
| `tau` (in `hierarchy` / `fit`) | population SD of the log-shape | **DIMENSIONLESS** |
| `tau * delta_theta` | thermodynamic work | energy (pN·nm) |
| bead diameter | viscous load proxy | nm |
| PMF | proton-motive force | mV |
| stator number | occupancy count | dimensionless integer |
| `t_onset` | perturbation onset timestamp | seconds, on the same clock as dwell boundaries |

**Symbol collision, explicit:** the `tau` fitted by `fit.fit_motor_stack`
(`0.18372082607308418`, source `F_SIDE_MOTOR_STACK_SCORING_RESULT.json`, sha256 `b3b12720…`) is
the dimensionless population SD of the log-shape. It is **not** a torque and must never be
multiplied by an angle. Thermodynamic work stays in its own units and its own paragraph.

---

## 2. The three requirements already on record

From `hierarchical-aif/docs/BIOLOGICAL-PARITY-RECEIPT-MAP.md` §"The G-side requirement, stated
concretely" (lines 51–57), restated identically in `MOTOR-STACK-AIF-SCOPE-RULING.md` §4. All
three are required; **no one of them is sufficient**:

1. **A manipulated variable with recorded onset time** — a load step, PMF step, stator-availability
   step, or electrorotation change, timestamped against dwell boundaries.
2. **Paired pre/post observation on the same motors**, so the response is measured **within unit**.
3. **Enough independent motors under each condition** to give a CI-bound verdict on the response.

The receipt map's own note that the exact motor count is "to be derived, not guessed" is honoured
in §4 below: it is reported as `NOT_MEASURED`, with the measurement machinery supplied and the
one measured variance anchor that exists labelled for what it actually is.

---

## 3. Candidate perturbations

The **experimental unit is the MOTOR** throughout. Dwell events within a motor are not independent
replicates; every design below aggregates to a per-motor statistic first, then resamples motors.
`t_onset` is mandatory in every row — without it, pre and post cannot be separated and the
manipulated variable is not a manipulated variable.

### 3.1 Load perturbation (viscous load / bead size)

| field | content |
|-|-|
| manipulated variable | viscous drag on the load, via bead diameter or medium viscosity |
| must be recorded | `t_onset` (s, same clock as dwell boundaries); bead diameter (nm) or viscosity (Pa·s) pre and post; speed trace (Hz); motor id; temperature (°C); the dwell segmentation applied identically pre and post |
| paired design | same motors observed under load L1 → step → load L2 → (optionally) step back to L1; the return arm is the recovery test in §3.4 |
| minimum independent motors per condition | **`NOT_MEASURED`** — no intervention response variance exists in this repository. See §4 |
| falsifier | the per-motor paired dwell-statistic change has a CI containing zero at the pre-registered N, **and** a sham arm (bead exchanged for an identical bead) shows a change of the same magnitude. Either alone leaves the result `NOT_ESTABLISHED`, not refuted |
| what it would license | **at most** that dwell structure depends on mechanical load. It would license `P5`-relevant evidence for *responsiveness*. It would **not** license a policy-selection reading — see §5 |
| hazard | segmentation thresholds tuned per load silently manufacture the effect. Segmentation must be frozen and identical across arms, pre-registered before unblinding |

### 3.2 Stator availability perturbation

| field | content |
|-|-|
| manipulated variable | number of engaged stator units (MotA-MotB occupancy), via inducible expression, a resurrection protocol, or controlled de-energisation |
| must be recorded | `t_onset`; an independent stator-count readout (fluorescent MotB spots, or resolved speed steps) with its own uncertainty; speed trace; motor id |
| paired design | same motors tracked across a stator-count transition; per-motor pre/post pairing at matched load |
| minimum independent motors per condition | **`NOT_MEASURED`** |
| falsifier | dwell-statistic change CI contains zero across the stator transition, **and** the stator-count readout is itself resolved (a null with an unresolved stator count is `NOT_CHECKED`, not a refutation) |
| what it would license | a torque-generating-unit-count dependence of the dwell process. Structural (`P6`-relevant) if and only if the stator readout is independent of the dwell readout — otherwise the two channels share an instrument and the result is circular |
| hazard | stator number and load co-vary through speed. Without matched load this design confounds §3.1 and §3.2 |

### 3.3 Energy / ion-motive-force perturbation

| field | content |
|-|-|
| manipulated variable | PMF, via protonophore addition (collapse) or washout / re-energisation (restoration) |
| must be recorded | `t_onset` of addition **and** of washout; PMF proxy (mV) or at minimum the applied agent concentration and the speed trace; motor id; temperature |
| paired design | same motors: baseline → collapse → restoration. This is the only perturbation in this list that is naturally **bidirectional on one motor**, which makes it the strongest paired design available |
| minimum independent motors per condition | **`NOT_MEASURED`** |
| falsifier | dwell statistics are invariant across a *verified* PMF change (CI-bound), or the restoration arm fails to return toward baseline while the collapse arm showed an effect — the latter indicates irreversible damage and invalidates the paired assumption rather than refuting the target hypothesis |
| what it would license | energetic dependence of the dwell process. **Nothing about policy.** A thermodynamic dependence is not an inference |
| hazard | protonophores are pleiotropic. A PMF-collapse effect is not attributable to PMF alone without a dose series and a vehicle-only sham |

### 3.4 Recovery after perturbation (time course back to baseline)

| field | content |
|-|-|
| manipulated variable | **time since removal of the perturbation**, `t - t_offset` |
| must be recorded | `t_onset` **and** `t_offset`; a continuous per-motor time series through the whole episode, not summary statistics per phase |
| paired design | each motor is its own baseline; the recovery trajectory is a within-motor curve, and the per-motor statistic is a recovery time constant (s) or a return-fraction at a pre-registered horizon |
| minimum independent motors per condition | **`NOT_MEASURED`** |
| falsifier | recovery time constants are not distinguishable from the baseline drift measured in an unperturbed time-matched control arm. **A time-matched unperturbed control arm is mandatory** — without it, drift and recovery are not separable |
| what it would license | **the highest-information arm of the five for the F-side model**, because it produces a *dynamic* target that a static duration density cannot fit by construction. It is what would create the first genuine time-conditional prediction task in this project |
| hazard | photobleaching, cell death, and stage drift all produce monotone "recovery-shaped" trajectories. The unperturbed control arm is the only defence |

### 3.5 State-transition response (does dwell-state structure change under perturbation)

| field | content |
|-|-|
| manipulated variable | any of §3.1–§3.3, with the **state-resolved** dwell structure as the readout rather than the pooled duration |
| must be recorded | `t_onset`; the state assignment and the transition sequence, produced by a segmentation frozen **before** the perturbation arm is unblinded |
| paired design | per-motor, per-state paired pre/post; the per-motor statistic is a vector over states `{1..8}` and multiplicity must be handled (Bonferroni companion, as already done for the M4/M6/M7 family extension) |
| minimum independent motors per condition | **`NOT_MEASURED`**, and **strictly larger than §3.1–§3.3** because the readout is multivariate |
| falsifier | the state-resolved response is fully explained by the pooled duration response — i.e. a pooled-only model is not out-predicted by the state-resolved model on held-out motors under the same scoring rule |
| what it would license | `P6`-relevant structural evidence about *which* part of the dwell process is load- / stator- / PMF-sensitive |
| **D5/D6 constraint** | this arm requires a **mark channel** (which state follows which). On the current dataset that channel is `QUARANTINED`: D5 burned the held-out mark channel (retrospective-only), and D6 records 2 impossible marks, 5 zero-support holdout cells, and 15–17% of marks leaving `{1..8}`. **A new intervention dataset must therefore carry its own mark channel with a predeclared smoothing/quarantine policy committed before observation.** Reusing the current mark channel for this arm is not available |

---

## 4. Minimum independent motors per condition — what is measured and what is not

### 4.1 The honest headline

**`NOT_MEASURED` for the intervention design — and the premise below is now STALE.** A power atlas
was produced in the same probe batch as this protocol
(`hierarchical-aif/results/motor_stack_aif/power_atlas.json`,
`reports/POWER-ATLAS-MOTOR-EQUAL-SCORING.md`). It is a **synthetic** motor-equal resolve-rate
atlas and does **not** supply a minimum-N for an *intervention* design, which needs a within-motor
pre/post contrast the atlas never simulates. The required minimum N therefore remains
`NOT_MEASURED` — for that reason, not for absence. Historical note — when this section was
drafted, a search of
`hierarchical-aif/docs/`, `hierarchical-aif/ledgers/`, and the whole `hierarchical-aif/` tree
returns no power-atlas artifact (command and output in the return record). Deriving a required N
needs a **minimum effect size of interest** and a **variance of the intervention response**.
Neither exists, because no intervention has been performed. Any number stated for these would be
invented, and this document does not state one.

### 4.2 The one variance anchor that does exist — and what it is not

Computed from `hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json`
(sha256 `b3b12720…`), field `perMotorNLPD`, across the 19 frozen holdout motors:

| quantity | value | unit |
|-|-|-|
| n motors | 19 | motors |
| between-motor SD of per-motor NLPD (F-side candidate) | 0.9182141349243506 | nats |
| between-motor SD of per-motor NLPD (M3 control) | 1.0227160437071596 | nats |
| mean paired per-motor difference `M3 − F` | 0.0016409948078282934 | nats |
| **SD of the paired per-motor difference `M3 − F`** | **0.18831385847627796** | nats |
| Pearson r of per-motor NLPD, M3 vs F | 0.9869331362237367 | dimensionless |
| SD of the difference **if the pairing were discarded** (`sqrt(sd_M3² + sd_F²)`) | 1.3744327206636557 | nats |
| **pairing gain** (unpaired SD ÷ paired SD) | **7.298627577304907** × | dimensionless |

Two consistency checks, both passed, both against artifacts not used to produce the numbers:

- the mean paired difference `0.0016409948078282934` reproduces the frozen F-side M3 contrast
  point estimate `+0.001641` (established fact);
- the normal-approximation half-width at n=19, `1.96 × 0.18831385847627796 / sqrt(19) =
  0.0846762376`, sits close to the published M3 percentile half-width
  `(0.080849 − (−0.077147)) / 2 = 0.0789980000`.

**What this anchor is NOT.** It is the per-motor SD of a **model-versus-model NLPD difference on
passive duration data**. It is **not** the variance of a motor's response to a manipulated
variable. There is no evidence that an intervention response has this variance, and assuming it
does is an assumption with no support. It is reported here because it is the only measured
motor-level paired variance in this repository, and because the **pairing gain of 7.30×** is the
one transferable design lesson: **requirement (2), paired pre/post on the same motors, is not a
nicety — on the only motor-level paired quantity ever measured here it reduced the SD of the
difference by a factor of 7.3, i.e. it cut the required motor count by roughly its square.**

### 4.3 The sizing relation (supply the machinery, not a fabricated N)

For a per-motor paired response with SD `s_d` (nats or whatever the response unit is) and a
target CI half-width `d` in the same unit:

```text
n_motors  ≈  ( 1.96 * s_d / d )^2          [normal approximation; the frozen path uses a
                                            paired motor-cluster bootstrap, which is what
                                            any real design must be sized against]
```

`s_d` for **any** intervention response is **`NOT_MEASURED`**. A pilot arm exists precisely to
measure it, and the pilot's own N is not derivable in advance either.

**`DESIGN_ONLY` illustration — NOT EVIDENTIAL, and not a prediction about any intervention.**
Substituting the §4.2 NLPD paired SD `0.18831385847627796` purely to show the shape of the curve:

| target half-width `d` | n motors (ceil) |
|-|-|
| 0.300 | 2 |
| 0.200 | 4 |
| 0.150 | 7 |
| 0.100 | 14 |
| 0.050 | 55 |
| 0.042 | 78 |

The `0.042` row uses the corrected motor-equal resolution floor
(BCa half-width `0.04207043063262626`, narrowest frozen B3 contrast, M4_MIXTURE_K3) as `d`.
**These rows are `DESIGN_ONLY`. They describe an NLPD contrast, not an intervention response, and
they must not be quoted as a required motor count for any perturbation in §3.**

### 4.4 The minimum-effect-size guard is mandatory here (D10)

D10 recorded that the frozen CI rule has **no minimum-effect-size guard**: a paired motor-cluster
bootstrap resamples MOTORS, so it resolves a difference of **any** magnitude whose **sign is
consistent** across motors. M7 exposed this at `+2.506984e-07` nats — roughly 168 000× below the
floor — and was repaired by added interpretation (`scientificReading`, `reportableAsAWin`), never
by re-thresholding.

**An intervention design is exactly where this bites hardest**, because a systematic instrument
shift between the pre and post arms (focus drift, stage settling, illumination change) is
*perfectly sign-consistent across motors* and will resolve. Therefore every arm in §3 must
pre-register:

- a **minimum effect size of interest**, declared **before** unblinding, in the response's own
  unit — `NOT_MEASURED` at present and to be set by domain judgement, not by the observed data;
- a **sham / time-matched control arm** whose measured shift bounds the instrument-drift floor;
- reporting of both the interval **and** the scientific reading, exactly as the D10 repair does.

---

## 5. THE CORE QUESTION — what does policy selection predict that M2 / M4 / M7 do not?

### 5.1 The answer, stated without softening

**Against M2 / M4 / M7 as they actually exist: nothing testable, because those models make no
prediction about an intervention at all.**

`M2_LOGNORMAL`, `M4_MIXTURE_K3`, and `M7_HIERARCHICAL_MOTOR` are unconditional dwell-duration
densities. None of them takes a manipulated variable as an argument. Under a load step, a stator
step, or a PMF step, they are **silent, not wrong**. "Policy selection predicts a response and M2
does not" is therefore **not a discriminator** — it is a comparison against an undefined baseline,
and treating it as evidence would be the emptiest possible way to appear to close `P5`.

Any honest discriminator must first extend the incumbents to **stimulus-conditioned** form: M2/M4/M7
refitted with the manipulated variable and `t - t_onset` as covariates, on identical splits and the
identical scoring rule. Only then does the comparison have two live sides. **That extension is a
prerequisite of the experiment, not a result of it.**

### 5.2 Once the incumbents are stimulus-conditioned, what is left?

Three candidate signatures were examined. Two collapse.

| candidate signature | does it separate policy selection from the stimulus-conditioned incumbents? | ruling |
|-|-|-|
| **Goal-directed invariance** — the same outcome reached by a different trajectory when the plant changes | Separates goal-directed from open-loop. But a classical feedback controller with a setpoint predicts this identically, and so does a stimulus-conditioned density model with enough covariates | **NOT A DISCRIMINATOR** for policy selection specifically |
| **Anticipation before onset** — statistics change before `t_onset` when the perturbation schedule is learnable | Genuinely absent from a model conditioned only on the *realised* stimulus. But any history-dependent hazard model with memory reproduces it, and it requires a randomised-schedule negative-control arm to mean anything | **WEAK** — discriminates *predictive* from *reactive*, not policy selection from prediction |
| **Epistemic term** — action taken to reduce uncertainty **at a cost to** the pragmatic/setpoint objective | This is the only axis on which an expected-free-energy account makes a prediction that neither a setpoint controller nor a stimulus-conditioned density model makes | **THE ONLY REAL AXIS — and it is not instantiable here** (§5.3) |

### 5.3 Why the one real axis is not instantiable at the motor

Testing the epistemic term requires an **observable action channel in which information gain and
setpoint attainment dissociate** — a situation where the system can pay a measurable pragmatic cost
to obtain a measurable reduction in uncertainty, and where the analyst can observe the action
separately from the state it produces.

At the single flagellar motor, with the observables this project has or could plausibly acquire:

- there is no recorded action channel at all (`ObservedEvent` carries `event_id`, `motor_id`,
  `partition`, `state_n`, `duration_s`, `right_censored`, `next_state_n`, `direction`, `jump`,
  `meta` — and a test asserts exactly that field set);
- the nearest candidate, the motor's own stator-exchange or switching trajectory, is scored as a
  **category error** by `MOTOR-STACK-AIF-SCOPE-RULING.md` §3: treating a hidden-state trajectory as
  a policy asserts that the organism performs the inference, which is the very thing at issue;
- the experimenter's protocol is an **experimenter** policy, not the motor's. Scoring it says
  something about the laboratory, not about the motor.

### 5.4 Verdict of this probe

**A discriminating prediction that separates biological policy selection from the
stimulus-conditioned incumbents cannot currently be named at the single-motor level.** The only
axis that would separate them — the epistemic term — has no instantiable action channel in this
system with the recorded or plausibly recordable observables.

Therefore, and stated plainly because it is the most valuable output of this probe:

> **G is currently unfalsifiable in this system and must stay fenced.** `G_motor` biological policy
> selection remains `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER`, and the intervention arms in §3,
> even if all five were executed perfectly, would **not** by themselves make it falsifiable. They
> would make **responsiveness** and **stimulus-conditioned prediction** testable — which is worth
> doing, and is `P5`- and `P6`-relevant — but responsiveness is not policy selection.

No discriminator was manufactured to fill this section. The absence is the finding.

### 5.5 What would change this verdict

Recorded here so a future agent can check whether the fence is still correct, not as a plan:

1. an observable, separately recorded action channel at the motor or cell level in which an
   uncertainty-reducing action is **pragmatically costly**, so the two expected-free-energy terms
   dissociate;
2. or **transfer** of the question to a level where an action channel already exists and is
   recorded with onset times (chemotactic run-and-tumble decisions of a whole cell in a controlled
   gradient are the obvious candidate) — noting that this changes the **experimental unit** from
   motor to cell, which invalidates every motor-level variance figure in §4 and requires its own
   split, its own frozen cohort, and its own pre-registration;
3. and, in either case, a **pre-registered stimulus-conditioned M2/M4/M7 family** as the adversary,
   scored on the identical split with the identical rule, before the policy account is scored.

Until at least (1) or (2) exists in the repository as data with recorded onset times, adding
`expected_free_energy` to the package would create unfalsifiable scaffolding. The tests that
prevent it are correct and must not be weakened.

---

## 6. What this document does NOT do

- It does **not** add, propose adding, or design an `expected_free_energy` symbol, a policy
  posterior, a policy prior, or an action-set field. The package fence stands unchanged.
- It does **not** move `P5`, `P6`, or any other level. `P5` intervention stays `NOT_ESTABLISHED`;
  `P4` remains the first unsatisfied level; `P8` `FULL_PARITY = false` is unchanged.
- It does **not** license reading held-out `nextStateN`, `direction`, or `jump`. §3.5 explicitly
  routes the mark-channel requirement to a **new** dataset because D5/D6 quarantined the current one.
- It does **not** report a required motor count. Every such cell reads `NOT_MEASURED`, and the
  §4.3 table is labelled `DESIGN_ONLY` and non-evidential.
- It does **not** claim that any perturbation in §3 would establish that the motor performs
  inference. On the evidence and the argument in §5, none of them would.

---

## 7. Provenance of every number in this document

| number | source |
|-|-|
| per-motor NLPD arrays, 19 motors | `hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json`, field `perMotorNLPD`, sha256 `b3b12720…` |
| SDs, Pearson r, pairing gain, paired-difference mean | computed this session from that file (command in the return record) |
| M3 contrast point estimate `+0.001641`, interval `[-0.077147, +0.080849]` | frozen F-side scoring result (established fact) |
| resolution floor BCa half-width `0.04207043063262626` | narrowest frozen B3 contrast, M4_MIXTURE_K3 (established fact; supersedes the D7-mislabelled 0.064) |
| M7 exposure figure `+2.506984e-07` nats | M4/M6/M7 per-motor extension, `751a59ef…` (established fact) |
| fitted `tau = 0.18372082607308418` | F-side scoring result `fitted.F_MOTOR_STACK` (established fact) |
| D5 / D6 / D7 / D10 statements | `hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md` |
| the three G-side requirements | `hierarchical-aif/docs/BIOLOGICAL-PARITY-RECEIPT-MAP.md` lines 51–57; `MOTOR-STACK-AIF-SCOPE-RULING.md` §4 |
| `ObservedEvent` field set | `hierarchical-aif/tests/motor_stack_aif/test_no_G_biological_claim_in_passive_data.py::test_the_observation_schema_declares_no_action_field` |

Everything not in this table that would have been a number is written `NOT_MEASURED`,
`NOT_COMPUTED`, or `DESIGN_ONLY`.

---

NEXT_ACT = Run `python hierarchical-aif/src/motor_stack_aif/claim_guard.py hierarchical-aif/protocols/G-SIDE-INTERVENTION-DISCRIMINATOR.md`, then — without touching the two runs in flight — record in `hierarchical-aif/docs/BIOLOGICAL-PARITY-RECEIPT-MAP.md` LANE D that the G-side discriminator search returned NO instantiable discriminator at the single-motor level, so the fence is retained on argument and not only on missing data.
