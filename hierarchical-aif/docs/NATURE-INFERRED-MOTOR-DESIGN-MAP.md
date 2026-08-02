# Nature-Inferred Motor Design Map

**Status:** BUILDER-SUPPORT DESIGN MAP. Raises no `P`-level, changes no frozen verdict, creates no
claim. It answers one question per row: *which design element came from a biological observation,
and what does the receipt actually say about it?*

---

## 0. The fence — read this before the table

> **Nature motivates the candidate architecture; gates decide status.**

A nature citation is **never** a UNI gate. Nature is a **search heuristic, not a proof surface**.
Citing a flagellar-motor observation tells you where it was reasonable to look for a modelling
principle. It tells you nothing about whether the resulting software predicts held-out dwell
times, and it can move no gate by itself.

Three separate things are kept apart in every row below and must never be collapsed:

| kind | what it is | what it licenses |
|-|-|-|
| **inspiration** | a published biological observation that motivated a design choice | a candidate to test. Nothing else. |
| **implementation** | code in `hierarchical-aif/src/motor_stack_aif/` | a thing that can be run and tested |
| **receipt** | a test, a frozen artifact, a CI-bound contrast | the only thing that sets `UNI status` |

The `nature observation` column is the **inspiration** column. Reading it as evidence for this
cohort is the exact category error this document exists to prevent. If a row's `current test` cell
says `NO_CURRENT_TEST`, then no amount of biological citation in that same row upgrades it.

### Species discipline (contract-binding)

This cohort is ***E. coli* behavioural** evidence: Wadhwa 2022, stator-occupancy dwell events,
cohort `derived_eligible_1_to_8`, 80 train / **19 holdout motors**, 793 / 233 events.

Structural facts from other species appear in this repository — *Salmonella* rod/hook/basal-body
(PDB `7E82`), *Salmonella* switching visualisation (Singh et al. 2024,
DOI `10.1038/s41564-024-01674-1`), *Bacillus subtilis* MotA5MotB2 homologous geometry (PDB
`6YSL`), catalogued in `docs/LIVING-SCIENCE-WALKTHROUGH.md`. Wherever such a fact is named below
it is labelled **`STRUCTURAL / <species>`** and carries this rider:

> A *Salmonella* or *Bacillus* structural fact is **not** behavioural evidence and is **not**
> evidence for this *E. coli* cohort. These did not come from one measured specimen, and no row
> below may be read as though they did.

### Status vocabulary used

| status | meaning |
|-|-|
| `TESTED_AND_SUPPORTED_SCOPED` | a named receipt supports it, **only** inside the named scope |
| `TESTED_NOT_ESTABLISHED` | contrasted under the frozen CI rule; the interval crosses 0 or sits inside the resolution floor. **Underpowered is not equivalence.** |
| `IMPLEMENTED_UNTESTED` | the code exists and runs; no receipt discriminates it |
| `NO_CURRENT_TEST` | no test addresses it at all; the falsifier column says what would create one |
| `DESIGN_ONLY` | specified deliberately and deliberately not instantiated; not evidential |
| `FENCED` | absence is enforced by a test; adding it is a contract violation |
| `BLOCKED_EXTERNAL` | needs data this project does not have (second dataset / intervention / raw archive) |
| `QUARANTINED` | evidence exists but its status was destroyed by a defect; retrospective-only |

---

## 1. The map

Columns are terse by design; §2 expands each row with its receipt. Wide table — scroll right.

| # | nature observation (INSPIRATION ONLY) | function | constraint regime | extracted principle | software/model equivalent | current test | falsifier | UNI status |
|-|-|-|-|-|-|-|-|-|
| **R1** | Motors of the same strain, same apparatus, differ systematically from one another (*E. coli* behavioural, Wadhwa 2022; superset 1349 events / 99 motors per the parent rationale §2) | pooling motors would attribute between-motor spread to within-motor noise | frozen cohort: 80 train motors / 793 train events, **median 7 events per training motor** (`hierarchy.py` docstring); 19 holdout motors | **nested inference over an exchangeable unit** | `hierarchy.py` `Lmotor-5` population prior `(mu, tau)` + `Lmotor-4` per-motor latent `eta_m` **integrated** by 33-node Gauss-Hermite, not estimated | `test_fside_motor_stack.py::test_hierarchy_integrates_latent_not_free_per_motor_params`; F-side scoring contrast vs `M1_WEIBULL` (the pooled `tau -> 0` limit) | the hierarchy fails to beat its own `tau -> 0` limit on held-out motors under a CI-bound verdict | **`TESTED_NOT_ESTABLISHED`** — vs `M1_WEIBULL` `+0.000615 [-0.010881, +0.011304]`, interval crosses 0. Corrected **B4C11** in flight; **D1** OPEN. |
| **R2** | A dwell that has not yet ended still constrains the timing law; motor traces terminate for apparatus reasons, not biological ones | keep information from unfinished dwells instead of discarding or truncating them | 109 right-censored dwells exist in the 1349-event superset (parent rationale §2); **the frozen scored cohort excludes them entirely** | **survival-aware likelihood**: `censored -> log S`, `uncensored -> log h + log S` | `hazard_survival.py` `log_event_density`; **no floor** — a non-finite log density HALTS | `test_censoring_likelihood.py` (9 test functions incl. mislabelling mutation + no-floor); `test_fside_motor_stack.py::test_censoring_is_load_bearing` | a censored-bearing cohort where the censoring branch changes the held-out ranking, or where the frozen exclusion rule was itself the reason a model won | **`IMPLEMENTED_UNTESTED` on real held-out data** (the branch is `TESTED_AND_SUPPORTED_SCOPED` at `P1` identity level only — **zero censored events in the frozen scored cohort**) |
| **R3** | Dwell-time distributions in molecular motors are non-exponential; hazard is not constant over a dwell | a memoryless law is the wrong default for a multi-step molecular transition | frozen `scale_N` spans `4.749152542372881` (state 1) to `24.52058394160584` (state 8), seconds; 793 train events | **hazard/survival form rather than a rate constant** | `hazard_survival.py` mean-one Weibull `weibull_log_hazard` / `weibull_log_survival`; exponential retained as adversary `M0` | `test_hazard_survival_consistency.py`: `log S == -∫h` , scipy agreement, monotonicity, strict positivity | the exponential adversary `M0` matches or beats the candidate on held-out motors | **`TESTED_AND_SUPPORTED_SCOPED`** — vs `M0_EXPONENTIAL` `+0.115291 [+0.013040, +0.227497]` `RESOLVED_ABOVE`. Scope: *this* cohort, motor-equal NLPD, 19 holdout motors. Non-exponential timing, **not** mechanism. |
| **R4** | Individual motors carry a persistent property across their own dwells (same motor, repeated events) | per-unit variation is structure, not noise | median ~7 events per motor — 80 free per-motor shapes would be unscoreable | **integrate per-unit latents; do not free-fit them** | `hierarchy.py::motor_log_marginal` — `eta_m ~ N(mu, tau^2)`, `k_m = exp(eta_m)`, integrated jointly per motor. Total free params: **2** | fitted `tau = 0.18372082607308418`, `tauAtBoundary = false`, bounds `[1e-4, 5.0]` (`F_SIDE_MOTOR_STACK_SCORING_RESULT.json`, `b3b12720…`); contrast vs `M7_HIERARCHICAL_MOTOR` | `tau` collapses to its lower bound, or the heterogeneity level buys no resolvable held-out gain | **`TESTED_NOT_ESTABLISHED`** — `tau` is fitted away from boundary (fit-side), but vs `M7` the contrast is `+2.506984e-07 [+1.604451e-07, +3.374688e-07]`: `RESOLVED_ABOVE` **and** `SCIENTIFICALLY_NULL` (**D10**). The F-side hierarchy **is** `M7` to numerical precision. |
| **R5** | Stator occupancy state changes dwell statistics (*E. coli* behavioural; occupancy `N` in `{1..8}` on this cohort) | dwell law must be conditioned on occupancy, not marginalised over it | 8 occupancy states; per-state event counts unequal | **state-conditioned dynamics** | frozen per-state `scale_N` normalisation, `y = duration / scale_N[state]`; seconds-scale NLPD `= normalised-y NLPD + log scale_N[state]` | `test_compare_harness.py::test_frozen_scale_N_matches_the_published_record`; `::test_seconds_scale_is_the_normalised_scale_plus_log_scale_N`; **mutation test** — dropping the `+log(scale_N)` Jacobian halts the oracle | a **state-pooled ablation** (one global scale) matches the state-conditioned model on the same frozen split | **`IMPLEMENTED_UNTESTED` as a mechanism claim** (the Jacobian/units layer alone is `TESTED_AND_SUPPORTED_SCOPED` at `P1`). `scale_N` is a **shared inherited normalisation** — it cancels in every contrast, so no contrast can discriminate it. No ablation exists. |
| **R6** | An external observer of a cell never sees internal state — only the surface record the apparatus emits | the analyst must be typed out of the hidden state, not merely asked to behave | one study; packaged event JSON; raw MAT archive **absent** (`NOT_LOCATED_RAW_ARCHIVE`) | **Markov blanket / strict observation boundary** | `events.py` `Lmotor-0` typed `ObservedEvent` (frozen dataclass, immutable); three modes; `HoldoutMarkAccessError`; `duration_only` is the **default** | `test_no_holdout_mark_read.py` (14 test functions, incl. detector negative controls + use/mention); `test_duration_event_schema.py` (13 test functions, incl. independent `sha256_mod5` recomputation of the split) | a scoring path reads a channel outside its declared boundary, or the split can be recomputed to something other than the frozen partition | **`TESTED_AND_SUPPORTED_SCOPED`** — scope is the **software boundary** (`P0`/`P1`). It is **not** a claim that the biological blanket sits at this cut. |
| **R7** | The motor switches occupancy: it goes somewhere next, in a direction, by a jump size (*E. coli* behavioural). **`STRUCTURAL / Salmonella`**: directional switching is also visualised structurally (Singh et al. 2024) — structural, not behavioural, **not evidence for this cohort** | the mark channel `{nextStateN, direction, jump}` is where mechanism would live | **D5**: holdout mark channel **BURNED** by a read with no prospective record. **D6**: 2 holdout events carry `nextStateN = -1` (physically impossible); 5 holdout events have zero training support; **15.1% train / 16.7% holdout** marks point outside `{1..8}` | **switch/dwell factorisation** — dwell timing and the transition mark are separate objects | `marks.py` (`flag_impossible_marks`, `prepare_mark_dataset`, policies `strict`/`quarantine`/`retain_labelled`); mark modes in `events.py` | a second, independent dataset with an unspent mark channel, pre-registered before its holdout is read | **`QUARANTINED` + `BLOCKED_EXTERNAL`** — any mark-process result on Wadhwa-2022 is `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET` and can never be labelled prospective. Open alphabet ⇒ **not** a closed Markov chain; a mark likelihood is a one-step-ahead conditional, **not** a trajectory likelihood. |
| **R8** | Dwell magnitude and dwell *shape* are different biological questions; occupancy sets the scale, the transition kinetics set the shape | separate the state-scale nuisance from the shape parameter under test | frozen B3 convention must be matched exactly or scores are not comparable | **mean-one normalisation**: all densities are parameterised so `E[Y] = 1` on `y = duration / scale_N` | `hazard_survival.py::_weibull_scale` — `lambda(k) = 1 / exp(lgamma(1 + 1/k))`; `K_MIN_REPRESENTABLE = 1/170` **derived** from the IEEE overflow bound, not tuned | `test_hazard_survival_consistency.py`: unit mass and unit mean by **adaptive** quadrature, plus scipy closed-form moment, plus negative control `test_a_wrongly_scaled_weibull_would_fail_the_mean_one_check`; `test_baselines_remain_adversarial.py` mean-one for every baseline | any baseline or the candidate is not mean-one, or a scale-vs-shape confound survives the normalisation | **`TESTED_AND_SUPPORTED_SCOPED`** — scope is the **mathematical identity** (`P1`) and comparability with the frozen B3 convention. Not a biological claim. |
| **R9** | Replication in motor biology is across **motors**, not across frames or events within one trace | 233 holdout events are not 233 independent replicates | **19 holdout motors** is the binding constraint on every verdict | **the motor is the experimental unit** | `score.py` `motor_equal_nlpd`, `per_motor_means`, `motor_cluster_bootstrap` (resamples MOTORS), `contrast_with_ci` | `test_motor_equal_scoring.py` (10 test functions) incl. `test_an_event_level_bootstrap_would_produce_values_outside_the_motor_lattice`; `test_bootstrap_duplicate_motors_remain_distinct_groups.py`; `test_minimum_effect_size_guard.py` (8 test functions, **D10**) | a resampling unit other than the motor changes a published verdict; or duplicate drawn motors are silently merged into one cluster | **`TESTED_AND_SUPPORTED_SCOPED`** — scope `P0`/`P1` statistical correctness. **D10** is CLOSED by added interpretation (`scientificReading`, `reportableAsAWin`), never by re-thresholding. |
| **R10** | Motors are thought to occupy discrete kinetic modes within a given occupancy state | a per-event hidden kinetic mode would be the natural next level | 793 train events against a corrected motor-equal resolution floor of **≈0.042 nats** | **do not add capacity the data cannot resolve** | `hierarchy.py` `Lmotor-2` kinetic mode — **specified and deliberately NOT instantiated** | none. It is not built. `M4_MIXTURE_K3` is the nearest instantiated relative and its contrast is `-8.576907e-03 [-7.114909e-02, +5.540236e-02]` `NOT_ESTABLISHED` (`SUB_FLOOR_EFFECT`) | enough independent motors that a mixture-mode model resolves a **material** (`> 0.042` nat) gain over the 2-parameter candidate | **`DESIGN_ONLY`** — flexibility that cannot be resolved is not neutral; it is a way to look complete while being untestable. |
| **R11** | A bacterium acts on its world — it swims, it tumbles, it responds to gradients | policy selection over actions would be the G-side object | **the dataset is passive; the action set is EMPTY. This is STRUCTURAL, not sample-size-limited.** No amount of additional Wadhwa-2022 data changes it | **do not compute an expected-free-energy quantity where no policy exists** | **nothing.** `free_energy.py` implements `F` (observational, `complexity - accuracy`) and *only* `F` | `test_fside_motor_stack.py::test_no_expected_free_energy_function_exists`; `test_no_G_biological_claim_in_passive_data.py` (13 test functions: identifier scan, planted-symbol positive control, use/mention control, no action field in schema, and a test that the recorded reason is **structural** and **not** attributed to sample size) | an intervention dataset with recorded perturbations and responses — i.e. a real action set | **`FENCED`** — G-side is **design-only until intervention or transfer**. Adding an expected-free-energy function is a contract violation caught by a test. `F` is not `G`; `F` is over beliefs, `G` would be over policies. |
| **R12** | Stator stoichiometry, torque-speed curves, PMF biophysics, ion flux, protein geometry. **`STRUCTURAL / Salmonella`** PDB `7E82`; **`STRUCTURAL / Bacillus subtilis`** PDB `6YSL` — structural, other species, **not evidence for this *E. coli* behavioural cohort** | biological embodiment: the *form* of the machine | this cohort records dwell durations and occupancy states. It records **no** torque, **no** PMF, **no** temperature sweep, **no** load series | **copy PRINCIPLE, not FORM** — reproducing embodiment detail in software is imitation, and moves no gate | **nothing.** Deliberately not modelled | `NO_CURRENT_TEST` — and by design there is nothing here to test on this cohort | a dataset carrying load, PMF, stator-count or temperature covariates, on which a form-bearing model out-predicts the form-free candidate at motor-equal resolution | **`NO_CURRENT_TEST` / `BLOCKED_EXTERNAL`** — `P5` interventional and `P7` independent replication are **not established** and cannot be closed by any modelling in this repository. |
| **R13** | Note on units, recorded to prevent a collision, not derived from an observation | — | — | keep thermodynamic work `tau * delta_theta` separate from variational free energy | `hierarchy`/`fit` use `tau` for the **population SD of the log-shape** — **DIMENSIONLESS**, **not a torque**. `free_energy.py` `F` is in **nats** | the symbol is documented in `hierarchy.py`'s module docstring and in `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` field naming | a report that reads `tau = 0.1837` as a torque, or adds a nats quantity to a work quantity | **`TESTED_AND_SUPPORTED_SCOPED`** (documentation-level only; there is **no mechanical unit checker** in this package — see §4 gap G3) |

---

## 2. Row detail — the receipt behind each status

### R1 · nested motor hierarchy `Lmotor-5..Lmotor-0`

The architecture as built: `Lmotor-5` population prior `(mu, tau)` → `Lmotor-4` per-motor latent
`eta_m` (integrated) → `Lmotor-3` occupancy state (frozen `scale_N`) → `Lmotor-2` kinetic mode
(**not instantiated**, R10) → `Lmotor-1` hazard/survival → `Lmotor-0` observed blanket.

The clean ablation of the hierarchy is **not** `M0`. It is `M1_WEIBULL` — the pooled, single-shape
`tau -> 0` limit of the same likelihood family. Verbatim from
`F_SIDE_MOTOR_STACK_SCORING_RESULT.json` `contrasts.M1_WEIBULL`: `pointEstimate`
`0.0006145100976836924`, `interval` `[-0.010880659688579656, 0.011303987651464963]`,
`halfWidth` `0.01109232367002231` (**percentile**, `intervalType: "percentile"` — D7),
`resamplingUnit: "MOTOR"`, `nRep 2000`, `seed 20260717`, `verdict: "NOT_ESTABLISHED"`,
`atOrBelowResolutionFloor: true`.

**The nesting currently buys nothing resolvable on 19 holdout motors.** This is an adverse result
for the architecture and is reported as the headline of this row, not as a footnote. The artifact's
own `interpretation` field says it: this is not equivalence and not "no difference".

`OPEN`: **D1** — the C11 cluster-collapse defect invalidates the previous `U4_OK` reading;
the corrected full run is in flight. Nothing in this document may be read from that run's live
counters, which are telemetry, not results.

### R2 · censoring — the honest gap

`test_censoring_likelihood.py` proves the branch is mathematically right, including a mutation
test showing that mislabelling one event moves the total log-likelihood, and a no-floor test. But
the frozen cohort `derived_eligible_1_to_8` **excludes right-censored events entirely**. So the
branch is correct-by-test and **unexercised by any scoring run**. That is a coverage gap in the
implemented likelihood, not a property of any result.

### R3 · hazard/survival timing

The only element in this map whose *biological-flavoured* reading is supported by a resolved
held-out contrast. Verbatim from `contrasts.M0_EXPONENTIAL`: `pointEstimate`
`0.11529094279542929`, `interval` `[0.013039958895400987, 0.22749707235626093]`, `halfWidth`
`0.10722855673042997` (percentile), `verdict: "RESOLVED_ABOVE"`,
`atOrBelowResolutionFloor: false`. The point estimate sits above the `≈0.042` nat resolution
floor, so the effect is **material**, not merely resolved — note that the interval's lower end
`0.0130…` does **not**, so materiality here is a statement about the point estimate, not a
CI-bound guarantee of materiality. Scope discipline: this supports *non-exponential
dwell timing on this cohort*. Predictive superiority is never promoted to mechanism.

### R4 · motor-specific heterogeneity and D10

`fitted.F_MOTOR_STACK`: `mu = -0.41607215987582913`, `tau = 0.18372082607308418`,
`k_population_median = 0.659632669755436`, `trainNLL = 575.6701064153622`, `converged true`,
`tauAtBoundary false`, `nfev 165`, `nit 83`. Against `M7_HIERARCHICAL_MOTOR` frozen
`tau = 0.18372185667134974` and `k = 0.6596322379287862`.
They agree to ~7 significant figures. From `M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json`
`contrasts.M7_HIERARCHICAL_MOTOR`: `pointEstimate 2.5069835851709854e-07`,
`interval [1.6044512352276248e-07, 3.3746883763884875e-07]`, `verdict "RESOLVED_ABOVE"`,
`scientificReading.classification "SCIENTIFICALLY_NULL"`,
`floorToEffectRatio 167532.01037467283` against `resolutionFloorNats 0.042`. That contrast is the
numerical shadow of two implementations of the same model — which is exactly why
**D10** was raised and closed **by adding interpretation**, never by moving a threshold.

### R5 · state conditioning — structurally undiscriminable here

Every model on the leaderboard, candidate and adversary alike, consumes the same frozen
per-state `scale_N`. It is a shared change of variable. Its `+log(scale_N)` Jacobian is
load-bearing for *units* (mutation test halts the oracle when it is dropped) but it **cancels in
every contrast**. No receipt in this repository discriminates state-conditioned from state-pooled
dynamics, and none can until a state-pooled ablation is built and scored on the same split.

### R6 · the blanket boundary

Typed, immutable, mode-gated, and defended by 27 test functions across two files (14 + 13) including detector
positive and negative controls. What it establishes is that **the software** cannot cross its
declared boundary. It establishes nothing about where a biological Markov blanket sits, and this
row must not be cited as though it did.

### R7 · switch/dwell structure — the burned lane

Two independent defects, both preserved:

- **D5** — the held-out mark channel was read by a read-only audit brief with no split boundary.
  Irreversible. One study, no second holdout, unrepairable in this dataset.
- **D6** — impossible marks (`nextStateN = -1`, 2 holdout events), 5 holdout events with zero
  training support, and an **open alphabet** (15.1% train / 16.7% holdout marks leave `{1..8}`).
  The frozen dataset is **not edited**; `marks.py` forces an explicit policy decision instead.

`test_nextstate_range_check.py` and `test_no_holdout_mark_read.py` keep both quarantines live.

### R8 · mean-one normalisation

Note the earned lesson embedded here: the unit-mean check uses **adaptive** quadrature precisely
because a uniform-grid mean-one integral can miss a `y^(a-1)` singularity while the analytic
node-weight sum is exact. The exact guarantee and the numerical check are kept as separate
objects.

### R9 · motor as experimental unit

The `D10` interaction matters for design: a paired motor-cluster bootstrap resamples motors, so it
resolves a difference of **any magnitude** whose sign is **consistent** across motors. The
`≈0.042` nat floor predicts what is scientifically **material**; it does not predict what the
bootstrap will **call**. Both numbers are needed and they answer different questions.

### R10 / R11 · the two deliberate absences

`Lmotor-2` is absent because it would be unidentifiable. G-side is absent because there is no
action set. These are different reasons and must not be merged: the first is a resolution
argument that more motors could in principle overturn; the second is **structural** and more
passive data cannot touch it.

---

## 3. Where this document disagrees with the existing rationale

`docs/NATURE-INFERRED-MOTOR-STACK-DESIGN-RATIONALE.md` is the parent document and this map is
consistent with it, with three deliberate divergences recorded here rather than made silently:

1. **Rationale §3 lists "Hierarchy" as an extracted principle that "lands" at `Lmotor-5/4`.**
   That is true as implementation. This map adds the receipt the parent predates: the hierarchy
   level is `TESTED_NOT_ESTABLISHED` against its own `tau -> 0` limit (`M1`,
   `+0.000615 [-0.010881, +0.011304]`). The parent should not be read as implying the principle is
   supported by evidence; it is supported by **motivation**.
2. **Rationale §3 lists "State conditioning" as landing at "per-state scale normalisation".**
   This map records that the normalisation is *shared by every competing model*, therefore
   structurally undiscriminable in any current contrast (R5). The parent does not say this.
3. **Rationale §9 falsifier 2 says "Falsifier 2 is live right now — B4C02 is running."**
   That statement is now stale: **B4C02 LANDED** (`0633988d…`). Its outcome was
   `gensWithM2overM3 = 1` of 3 → **GENERATOR-SPECIFIC**, so the frozen prediction of
   `GENERATOR-ROBUST_ADVERSE` was **REFUTED** — the adverse M2-over-M3 result is **not** a generic
   heavy-tailed shape artifact. The parent document's §9 text should be updated when someone next
   edits it; this map does not edit it.

No other disagreement. The parent's §10 forbidden readings are adopted here verbatim in spirit and
extended by §0 above.

---

## 4. Gaps this map exposes (design observations, not verdicts)

| id | gap | what would close it |
|-|-|-|
| **G1** | No state-pooled ablation exists, so R5's principle has never been tested as a hypothesis | build a single-global-scale variant, score it on the same frozen split under the same paired bootstrap. Needs **no new data**. |
| **G2** | The censoring branch (R2) has never seen a real censored event in a scored run | a cohort definition that retains right-censored dwells, pre-registered before scoring |
| **G3** | Unit discipline for `tau` (R13) is documentary only | a mechanical checker that refuses to combine a nats-valued quantity with a work-valued quantity, with a planted-violation positive control |
| **G4** | `H-AIF-G7` is recorded as `NOT RUN` in `docs/H-AIF-GATES.md` line 15, but the F-side scoring **has** executed (`b3b12720…`, report §9 records `H-AIF-G7 EXECUTED`) | the gates table is stale relative to the working tree. **This map does not edit it.** Reconcile in the next ledger pass. |

**`DESIGN_ONLY` thresholds introduced by this document: none.** Every numeric threshold quoted
(`≈0.042` nat floor, `5/793 = 0.006305`, `0.25`, `2.0` decades) is a **frozen** criterion quoted
from an existing artifact, not a new one.

---

## 5. Forbidden readings of this map

- that a filled `nature observation` cell is evidence for the row's software element;
- that a row with `NO_CURRENT_TEST` is neutral or presumed fine — it is **unmeasured**;
- that `TESTED_NOT_ESTABLISHED` means the two models are equivalent. It does not. With 19 holdout
  motors most contrasts are inconclusive; **underpowered is not equivalence**;
- that *Salmonella* or *Bacillus* structural evidence says anything about this *E. coli*
  behavioural cohort, or that any of them came from one measured specimen;
- that computing `F` implies the motor performs inference. The B3 result's own `notEstablished`
  disclaims that reading and this map does not license it;
- that this document moved any `P`-level. It moved none. `P8` remains `FULL_PARITY = false` and
  the first unsatisfied level remains `P4` transfer.

NEXT_ACT = build the R5 state-pooled ablation (gap G1) as a `DESIGN_ONLY`-free, receipt-bearing contrast — a single-global-scale variant scored on the frozen `derived_eligible_1_to_8` split under the same paired motor-cluster bootstrap — and pre-register its prediction record BEFORE running it, so state conditioning stops being `IMPLEMENTED_UNTESTED`; do not launch it while B4C11 and B4C01 are in flight
