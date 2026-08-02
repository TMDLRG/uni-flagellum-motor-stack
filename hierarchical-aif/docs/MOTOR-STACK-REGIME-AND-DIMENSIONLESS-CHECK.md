# Motor-Stack Regime and Dimensionless-Group Check

**Type:** BUILDER-SUPPORT PROBE (Probe 11). This document moves no P-level, changes no frozen
verdict, and creates no claim. It answers one question: *what regime does the frozen motor-stack
model actually live in, and what would have to be preserved for a transfer to be legitimate?*

**Split boundary declared:** `TRAIN_ONLY` for every recomputed distributional quantity;
`HOLDOUT_ALREADY_SPENT_DURATION_ONLY` for the published cohort counts (233 events / 19 motors)
that are quoted but not recomputed from held-out durations. **D5 firewall respected:** no
`nextStateN`, `direction`, or `jump` value was read at any point in producing this file.

**Channel-read disclosure (new, small, and stated rather than hidden):** to produce
§2 row `nominalElectrorotationSpeed` I counted the per-motor apparatus label
`motors[].nominalElectrorotationSpeed` for the 19 holdout motors of the frozen cohort. That field
is an **apparatus setting**, not an outcome channel, it is not listed in
`DATA-CHANNEL-SPEND-LEDGER.md`, and its holdout distribution was already referenced by
`hierarchical-aif/reports/ULTRACODE-TRACK-D-VERIFICATION.md` (row for "Experimenter load
protocol": "≤ 3 holdout motors at the thin levels"). Every statement I derive from it is marked
`DESIGN_ONLY` and is not evidential.

---

## 0. The governing constraint of this probe

**Do not transfer biology by shape. Transfer the regime and the ratio.**

This repository contains **dwell-time behavioural data only**. The observed blanket that reaches
the frozen model is exactly five fields — `{motorId, stateN, durationS, rightCensored, partition}`
(exhaustively verified in `ULTRACODE-TRACK-D-VERIFICATION.md` row F3). There is **no torque, no
viscosity, no proton-motive force, no Reynolds number, no temperature, and no CheY-P channel
anywhere in the motor-stack input**. Consequently most rows below read `NOT-MEASURED`. That is the
**correct and expected** outcome of this probe, not a gap in the probe.

`NOT-MEASURED` in this document is the same status token as `NOT_MEASURED` elsewhere in the pack:
the quantity does not exist in any artifact this model reads, and no value for it may be written.

Two symbol collisions are load-bearing and are flagged wherever they appear:

- **`tau` here is NOT a torque.** In `hierarchy.py` / `fit.py`, `tau` is the population standard
  deviation of the log Weibull shape. It is **dimensionless**. The thermodynamic work quantity
  `tau * delta_theta` (torque times angle) shares the letter and nothing else. They are never the
  same number and never share units.
- **`F` here is NOT `G`.** The F-side quantity is an observational projection over beliefs. The
  G-side (expected free energy over policies) is fenced out of the code by a test, because the
  dataset is passive and the action set is empty — structurally, not for want of sample size.

---

## 1. Measurement inventory

Columns are fixed: `quantity` · `measurand` · `value` · `unit` · `scope` · `source` · `status` ·
`falsifier`.

| quantity | measurand | value | unit | scope | source | status | falsifier |
|---|---|---|---|---|---|---|---|
| dwell time (`durationS`) | wall-clock residence in one stator-count state, between two stator-number changes, terminated by the next change | train range **0.3 … 307.5**; per-event values, 793 train events | second (s) | frozen cohort `derived_eligible_1_to_8`, *E. coli*, Wadhwa 2022, TRAIN partition | `experiments/data/wadhwa-2022-events.json`, ingested by `scripts/ingest-wadhwa-data.py` from `data/remodeling_data.mat` `sha256 c14de12c…` | **MEASURED (recorded observation, upstream-derived from a stator trace)** | a re-ingest of the raw `.mat` at the same `analysisStartIndex=3500` yielding different dwell boundaries |
| observation sampling interval `dt` | median inter-sample spacing of the source stator trace; hard-checked at ingest to be within 1e-6 of 0.02 s | **0.01999999999998181** (identical for all 129 motors) | second (s) | whole dataset, all 129 motors | `motors[].sampleIntervalS`; check at `scripts/ingest-wadhwa-data.py:114-116` | **MEASURED (instrument setting)** | any motor whose median `diff(t)` departs from 0.02 s by > 1e-6 (the ingest raises) |
| per-state mean dwell `scale_N` | arithmetic mean of TRAIN uncensored dwells within each stator-count state | 1: **4.749152542372881** · 2: **3.4826086956521736** · 3: **6.350886075949368** · 4: **5.062716049382717** · 5: **7.948453608247423** · 6: **14.389918699186993** · 7: **18.245270270270268** · 8: **24.52058394160584** | second (s) | frozen cohort, TRAIN events only (793 events, 80 motors) | frozen `audits/phase-b/b3-model-competition-result.json → cohorts.derived_eligible_1_to_8.summary.scale_N`; independently recomputed this session to the same IEEE doubles | **MEASURED / DERIVED FROM TRAIN** | recomputing the per-state train mean and getting a different double |
| normalised dwell `y` | `durationS / scale_N[stateN]` | train range **0.012234618910970076 … 20.170991026141245**; pooled train mean **exactly 1.0** by construction | **dimensionless** | frozen cohort, TRAIN | recomputed this session from the two rows above | **MEASURED (derived, dimensionless)** | a pooled train mean of `y` that is not 1.0 to floating-point tolerance |
| Weibull shape `k` (M1) | shape of the mean-one Weibull fitted to pooled normalised train dwells | **0.6250888335850175** | **dimensionless** | frozen cohort, TRAIN fit; single cohort, single study | `b3-model-competition-result.json → cohorts.derived_eligible_1_to_8.fitted.M1_WEIBULL.params[0]` | **FITTED (model parameter, not an observation)** | a refit under the frozen optimizer contract landing at a different value |
| population log-shape SD `tau` — **NOT A TORQUE** | standard deviation of `log k` across motors in the hierarchical motor stack | **0.18372082607308418** (F-side fit) · **0.18372185667134974** (frozen M7) | **dimensionless** | frozen cohort, TRAIN fit; 2 free params (`mu`, `tau`), per-motor latents integrated by 33-node Gauss–Hermite, not estimated | `hierarchical-aif` F-side scoring result (`b3b12720…`); frozen M7 params | **FITTED (dimensionless); symbol collides with torque and must never be read as one** | a refit landing outside the reported value, or `tauAtBoundary` becoming true against bounds `[1e-4, 5.0]` |
| population median shape `exp(mu)` | median of the per-motor Weibull shape distribution | **0.659632669755436** (F-side) · **0.6596322379287862** (frozen M7 `k`) | **dimensionless** | as above | as above | **FITTED** | as above |
| stator number (`stateN`) | integer count of bound stator units, supplied by the source `.mat` field `stators`; ingest rejects any non-integer within 1e-9 | integers **1 … 8** in the frozen cohort (**0 … 8** in `primary_states_0_to_8`); train events per state 1:59 · 2:69 · 3:79 · 4:81 · 5:97 · 6:123 · 7:148 · 8:137 | **count (dimensionless integer)** | frozen cohort, TRAIN counts | `events[].stateN`; `scripts/ingest-wadhwa-data.py:39-42,107-110` | **MEASURED-IN-SOURCE.** The upstream procedure that turned a speed trace into an integer stator count is **not reproduced in this repository**, and the raw `.mat` is absent (`BLOCKED_EXTERNAL`) | obtaining the raw archive `c14de12c…` and re-deriving a different stator assignment |
| stator-exchange event rate | reciprocal of the per-state mean dwell, `1/scale_N` | 1: **0.2105638829407566** · 2: **0.2871410736579276** · 3: **0.15745834329905126** · 4: **0.19752243464689814** · 5: **0.125810635538262** · 6: **0.06949309588917263** · 7: **0.054808724956486324** · 8: **0.04078206303656692** | per second (s⁻¹) | frozen cohort, TRAIN | derived from `scale_N` above | **DERIVED FROM TRAIN** | any change to `scale_N` |
| direction of the stator-number change (`direction`) | `"on"` if the next stator count is higher, `"off"` if lower — **this is stator binding/unbinding, NOT motor rotational switching (CW/CCW)** | **NOT-READ** in this probe | categorical | holdout channel is BURNED (D5), retrospective-only | `scripts/ingest-wadhwa-data.py:159` | **NOT-READ — D5 firewall; the holdout instance of this channel is `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET`** | n/a (channel status, not a value) |
| switch rate (CW↔CCW rotational switching) | rate of reversal of motor rotation direction | **NOT-MEASURED** in the motor-stack input. A CW/CCW rate channel exists in the repository for a **different study** (`experiments/data/cross-study-motor-evidence.json → studies.antani2021.torqueSwitching[].kCcwToCwPerSecond / kCwToCcwPerSecond`) and is **not joinable to any motor in this cohort** | s⁻¹ | — | — | **NOT-MEASURED (for this model)** | a dataset in which the same motors carry both stator-count dwells and rotational-switch times |
| torque | motor output torque | **NOT-MEASURED** in the motor-stack input. A torque channel exists for a different study/assay (`cross-study-motor-evidence.json → studies.antani2021.torqueSwitching[].torquePnNm`) and is **not joinable to any motor in this cohort** | pN·nm | — | — | **NOT-MEASURED (for this model)** | bead-assay or electrorotation torque calibration recorded per motor, on the same clock as the stator trace |
| viscous load | drag coefficient of the attached bead/filament load | **NOT-MEASURED** — no bead radius, no filament stub length, no drag coefficient exists in any artifact this model reads | pN·nm·s·rad⁻¹ (drag coefficient) | — | — | **NOT-MEASURED** | recorded bead diameter + medium viscosity per motor, giving a per-motor drag coefficient |
| load surrogate: `nominalElectrorotationSpeed` | per-motor scalar apparatus label carried through from the source `.mat` field `speed`; **no unit is declared anywhere in this repository** and none is asserted here | 7 levels **{50, 100, 150, 200, 250, 272, 300}**. Frozen-cohort TRAIN motors (80): 250:20 · 200:17 · 300:17 · 272:9 · 150:6 · 100:6 · 50:5. Frozen-cohort HOLDOUT motors (19): 250:6 · 272:6 · 200:3 · 300:2 · 150:1 · 50:1 · **100:0** | **UNIT NOT DECLARED IN REPOSITORY — do not assume Hz** | frozen cohort, per motor; **constant per motor, no onset time** | `motors[].nominalElectrorotationSpeed`; `scripts/ingest-wadhwa-data.py:130` | **RECORDED APPARATUS LABEL, NOT USED BY THE MODEL.** It never reaches the likelihood (F3). Every design statement derived from it below is `DESIGN_ONLY` | recovering `t_step` from the raw `.mat` (currently `BLOCKED_EXTERNAL`, `B4C06.analysisStartIndex.3400`) and finding within-trace load changes |
| Reynolds number | inertial/viscous ratio of the rotating load | **NOT-MEASURED** — requires load geometry, medium density and viscosity, and rotation rate; none exist here | **dimensionless** | — | — | **NOT-MEASURED** | bead radius + medium density/viscosity + measured rotation rate per motor |
| PMF / ion-motive force | electrochemical proton (or Na⁺) driving force across the inner membrane | **NOT-MEASURED** — the strings `PMF`, `proton`, `motive` occur **0** times in either artifact under `experiments/data/` (scanned this session) | mV | — | — | **NOT-MEASURED** | per-cell membrane-potential or pH-gradient measurement recorded alongside the stator trace |
| temperature | bath/stage temperature during the assay | **NOT-MEASURED** — `temperat` occurs **0** times in either artifact under `experiments/data/` (scanned this session) | K (or °C) | — | — | **NOT-MEASURED** | a recorded stage temperature per motor or per session |
| medium viscosity | dynamic viscosity of the assay medium | **NOT-MEASURED** | Pa·s | — | — | **NOT-MEASURED** | recorded medium composition and viscosity per session |
| CheY-P concentration | intracellular phosphorylated CheY level | **NOT-MEASURED** in the motor-stack input. A fluorescence proxy exists for a **different study** (`cross-study-motor-evidence.json → studies.antani2021.cheYFluorescence`) and is **not joinable to any motor in this cohort** | µM (or arbitrary fluorescence units) | — | — | **NOT-MEASURED (for this model)** | per-cell CheY-P reporter recorded alongside stator-count dwells |
| strain / genotype | *E. coli* strain and relevant alleles | **NOT-MEASURED as a per-motor field.** The dataset carries no strain column; the study-level attribution is Wadhwa et al. 2022 (`doi:10.1038/s41467-022-33075-5`) | categorical | study-level only | `experiments/data/wadhwa-2022-events.json → source` | **NOT-MEASURED per unit; STUDY-LEVEL ONLY** | a second strain in the same schema, enabling a strain contrast |
| fast/slow timescale ratio (M3) | ratio of the two exponential rates of the frozen two-timescale mixture, in **normalised** `y` units | `lambdaFast` = **0.44485933051063775**, implied `lambdaSlow` = **5.239879397483717**, ratio `lambdaSlow/lambdaFast` = **11.778733271636792** | **dimensionless** (rates are per unit of dimensionless `y`) | **fitted on one cohort, one study, TRAIN partition**; M3 is the reference / `CONTROL_CURRENT` model, not a winner | `b3-model-competition-result.json → …fitted.M3_TWO_TIMESCALE.params = [w, lf]`; `lambdaSlow` derived by the frozen mean-one constraint `m3_rates` at `b3-model-competition-runner.py:240-242` | **FITTED, DIMENSIONLESS, SINGLE-COHORT.** It is a property of a fitted candidate model, not an observed property of the motor | a refit on an independent cohort landing at a materially different ratio; or a reparameterisation that breaks the mean-one constraint (`w/lf + (1-w)/ls = 1`, verified = 1.0 this session) |
| M4 three-rate span | ratio of largest to smallest canonical rate of the frozen K=3 mixture | **32.89618289435011** (= **1.5171455075519444** decades) | **dimensionless** | frozen cohort, TRAIN fit | `…fitted.M4_MIXTURE_K3.canonical.rates` | **FITTED, DIMENSIONLESS** | a refit changing the canonical rates. **Note:** this is *not* the B4C10 `U3 span = 0.4332708748 decades` diagnostic; those are different quantities and must not be conflated |
| variational free energy `F` | observational free-energy projection over beliefs | reported as **nats** on the NLPD scale; **it is not `tau * delta_theta`** and carries no mechanical units | nat | F-side scoring, frozen cohort | F-side scoring result (`b3b12720…`) | **MODEL OUTPUT (not an observation)** | any artifact reporting `F` in J, pN·nm, or any energy unit |
| thermodynamic work `tau * delta_theta` | torque times rotation angle | **NOT-MEASURED** — neither factor exists in this repository's motor-stack input | J (or pN·nm) | — | — | **NOT-MEASURED** | a per-motor torque and angle record on the same clock |

---

## 2. Dimensionless groups that ARE computable here

Only four dimensionless groups can be formed from what this repository actually measures. All four
are `TRAIN_ONLY` and all four are properties of *this* cohort.

| group | definition | value | what it controls | status |
|---|---|---|---|---|
| **Π₁ — observation-resolution ratio** | `dt / scale_N[state]` | 1: **0.004211277658811302** · 2: **0.0057428214731533285** · 3: **0.003149166865978161** · 4: **0.003950448692934371** · 5: **0.0025162127107629514** · 6: **0.0013898619177821886** · 7: **0.0010961744991287293** · 8: **0.0008156412607305967** | how far into the short-dwell tail the instrument can see. The smallest observed train dwell is **0.3 s = 15 sampling intervals**; the largest is **307.5 s = 15375 intervals**. The whole model is fitted *above* a hard 15-sample floor | **MEASURED (derived)** |
| **Π₂ — state dynamic range** | `max(scale_N) / min(scale_N)` = state 8 / state 2 | **7.040866799712038** | the spread of characteristic times the per-state normalisation removes. After normalisation the model sees one pooled `y` distribution; the factor 7.04 is exactly what the normalisation hides | **MEASURED (derived)** |
| **Π₃ — mixture separation (M3)** | `lambdaSlow / lambdaFast` | **11.778733271636792** | how far apart the two candidate timescales sit *in normalised units* | **FITTED, single cohort** |
| **Π₄ — shape dispersion** | `tau` (SD of `log k`) relative to `|mu|` = 0.18372082607308418 / 0.41607215987582913 | **0.441560007590782** (recomputed this session) | how heterogeneous motors are in shape relative to the population location. `tau` is dimensionless; it is **not** a torque | **FITTED, single cohort** |

### 2.1 A regime statement that follows directly, and its adverse edge

The frozen model's timescales are fixed **only in normalised units**. Converting M3's two
components back to seconds makes them state-dependent, because `y` was divided by `scale_N`:

| state | `1/lambdaFast` in seconds | `1/lambdaSlow` in seconds |
|---|---|---|
| 1 | 10.675627589785524 | 0.906347681332801 |
| 2 | 7.82856165263436 | 0.6646352771639332 |
| 3 | 14.276166959698065 | 1.2120290552868784 |
| 4 | 11.380487498309657 | 0.9661894225683748 |
| 5 | 17.867341568678988 | 1.5169153725302171 |
| 6 | 32.347121240930996 | 2.7462308972411247 |
| 7 | 41.01357219894026 | 3.48200194818071 |
| 8 | 55.11985982953208 | 4.679608456900946 |

**There is no single pair of seconds-valued timescales in this model.** There are eight pairs,
tied together by one dimensionless ratio (Π₃ = 11.7787). Any transfer that carries "the motor has a
~10 s and a ~1 s timescale" across to another preparation is transferring a *shape*, not a regime,
and it is not licensed by this evidence.

### 2.2 Adverse finding — the `Fast`/`Slow` labels are inverted at the fitted values

`lambda` in M3 is a **rate** (`exp(-lf * y)`, `b3-model-competition-runner.py:244-252`). The fitted
`lambdaFast = 0.44485933051063775` is the **smaller** rate, so the component *named* "fast" has the
**longer** mean normalised dwell (`1/lf = 2.2479015981347104`) and the component named "slow" has
the shorter one (`1/ls = 0.19084408707578607`). The optimizer box is `lf ∈ [1e-9, 1e4]` with **no
ordering constraint** (`:424`), so nothing enforces the labelling.

Severity: **naming/resonance defect, not a numerical defect.** No score, contrast, verdict, or
gate depends on the label — M3's density is symmetric under relabelling and the frozen NLPD
3.4343333331 is unaffected. The hazard is purely in *reading*: a report that says "the fast
component carries weight 0.393" is describing the long-dwell component. Correct minimal reading:
**the mixture has a long-dwell component with weight w = 0.3933559993214189 and mean 2.2479 in
normalised units, and a short-dwell component with weight `1 - w` = 0.6066440006785811 and mean
`1/ls` = 0.19084408707578607.** Recommended
correction is **documentation only** — `audits/**` is frozen and must not be edited.

---

## 3. What would have to be matched for a transfer claim to be legitimate

A transfer of this model to another preparation, species, or apparatus is legitimate only if the
following are **matched or explicitly bounded**. Anything unmatched is an extrapolation and must
be labelled as one.

| # | group that must be preserved | why | current status |
|---|---|---|---|
| T1 | **Π₁ resolution ratio** `dt / scale_N` and the short-dwell floor | this model has never seen a dwell shorter than 15 sampling intervals. A preparation with a faster clock or shorter dwells probes a region the fit does not cover, and Weibull shape `k < 1` is exactly the regime where the unobserved short tail dominates the likelihood | **matched only to itself.** Any target with a different `dt` or a different dwell floor is `extrapolation-only` |
| T2 | **the per-state normalisation itself** (`y = duration/scale_N`) | the model is a statement about *normalised* dwells. Transfer requires the target to admit the same eight-state normalisation, i.e. the same discrete stator-count states with enough events per state to estimate `scale_N` | **structural precondition, not a number.** `NOT-MEASURED` in any target |
| T3 | **Π₂ state dynamic range** (7.0409 here) | if a target's `scale_N` spread differs materially, the pooled `y` distribution is a different mixture even if every per-state process is identical | `NOT-MEASURED` in any target |
| T4 | **load / drag regime** | the single most likely modifier of stator-exchange kinetics, and the one this dataset most conspicuously lacks. There is no drag coefficient, no bead geometry, no viscosity | **`NOT-MEASURED`.** Only a per-motor, unit-undeclared, timing-free apparatus label exists |
| T5 | **PMF regime** | sets the energy available per stator; a target at different PMF is a different mechanical regime | **`NOT-MEASURED`** |
| T6 | **temperature** | rate constants and viscosity both depend on it | **`NOT-MEASURED`** |
| T7 | **Reynolds regime** | the low-Reynolds assumption is universally assumed for this system and is **not verified from any measurement in this repository** | **`NOT-MEASURED`** |
| T8 | **CheY-P regime** | modulates switching; the stator-count process may or may not be coupled to it, and this dataset cannot say | **`NOT-MEASURED`** |
| T9 | **experimental unit and event-count profile** | 80 train / 19 holdout motors; median 7 train events per motor. Motor-equal scoring means the transfer target must supply enough *motors*, not enough *events* | **MEASURED here; `NOT-MEASURED` in any target** |
| T10 | **resolution floor of the comparison** | corrected motor-equal half-width ≈ **0.042 nats**. A transfer that cannot resolve 0.042 nats cannot adjudicate between any two of the nine frozen models except at the extremes | **MEASURED here** |

**Consequence.** Of the ten preconditions, **three** (T1, T2/T3 partially, T9/T10) are measurable
in this repository and **six** are `NOT-MEASURED` outright. A transfer claim is therefore
**`transfer required` / `intervention required`** — the missing groups are missing *data*, not
missing analysis, and no amount of further modelling on Wadhwa-2022 supplies them. This is the same
wall the P-ladder already records: `P4`/`P5`/`P7` cannot be closed by any modelling in this
repository.

---

## 4. Validity-domain map

Classification vocabulary per `CLAUDE.md`: supported · tentatively supported · contradicted ·
unidentifiable · **unobserved** · extrapolation-only.

| dimension | region actually covered | classification | note |
|---|---|---|---|
| **species** | *E. coli* only, one study (Wadhwa 2022) | **tentatively supported** for *E. coli* in this preparation | *Salmonella* / *Bacillus* structural evidence elsewhere in the repository is a different evidence body and must never be merged with this behavioural cohort |
| **strain** | not recorded per motor; study-level only | **unobserved** | no strain contrast is possible |
| **motor** | 99 motors in the frozen cohort (80 train / 19 holdout) | **supported** as the experimental unit; **underpowered** for between-condition contrasts | 19 holdout motors is the binding limit on every CI |
| **cell** | one motor per trace; cell-level covariates absent | **unobserved** | |
| **load** | 7 apparatus levels, per-motor constant, no onset, unit not declared; holdout has **1** motor at level 50, **1** at 150, **0** at 100 | **unidentifiable** for any load-response claim; `DESIGN_ONLY` for design arithmetic | the model never reads this field at all (F3), so load is *marginalised over*, not controlled |
| **PMF** | none | **unobserved** | |
| **stator state** | integer states 1–8 (0–8 in the wider cohort); event counts 59–148 per state | **supported** over 1–8 on this cohort | state 0 is excluded from the frozen cohort by rule; states > 8 never occur |
| **temperature** | none | **unobserved** | |
| **viscosity** | none | **unobserved** | |
| **CheY-P** | none | **unobserved** | |
| **apparatus** | one apparatus, one sampling clock (`dt = 0.01999999999998181 s`), one `analysisStartIndex = 3500` | **supported** only for itself; `analysisStartIndex = 3400` sensitivity is `BLOCKED_EXTERNAL` | the raw `.mat` `c14de12c…` is absent, so apparatus sensitivity is unresolvable here |
| **timescale** | dwells from 0.3 s to 307.5 s (15 to 15375 samples) | **supported** inside that window; **extrapolation-only** below 0.3 s and above 307.5 s | sub-0.3 s behaviour is exactly where a shape `k ≈ 0.625` model puts most of its hazard, and it is unobserved |
| **study** | one study | **unobserved** across studies | a single study cannot exhibit between-study variance |
| **model formulation** | 9 frozen B3 models + constrained motor stack; leaderboard span 0.1387 nats against a ≈0.042 nat resolution floor | **unidentifiable between most pairs.** M2-over-M3 was shown **generator-specific**, so the frozen `GENERATOR-ROBUST_ADVERSE` reading is **refuted** (B4C02, `0633988d…`) | the adverse M2-over-M3 result is retained and is not generic heavy-tailed shape |
| **rotational switching (CW/CCW)** | not in this dataset at all — `direction` here is stator on/off | **unobserved** | a real risk of cross-reading: "switch" in the flagellar literature usually means CW/CCW, and it does **not** mean that here |

**Count:** of 15 domain dimensions, **2** are supported, **1** is tentatively supported, **2** are
unidentifiable, **1** is mixed supported/extrapolation-only, **8** are unobserved, **0** are
contradicted. That distribution — mostly unobserved — is the honest regime portrait of this model.

---

## 5. What this probe did NOT do

- **NOT_RUN — COMPUTE_BUDGET:** no bootstrap, refit, or simulation was executed. Two corrected-full
  runs (B4C11, B4C01) are in flight and no compute was spent that could contend with them. Their
  live progress counters were not read and are not cited anywhere in this document.
- **NOT_CHECKED — would require holdout access:** the held-out normalised-`y` range, the held-out
  per-state dwell means, and any held-out recomputation of Π₁/Π₂. Every distributional number here
  is `TRAIN_ONLY`.
- **NOT-MEASURED:** every physical measurand in §1 marked as such. No value was estimated,
  imputed, borrowed from literature, or carried across from another study. The Antani-2021 torque
  and CheY channels exist in this repository and were deliberately **not** used as substitutes —
  they belong to a different study, a different assay, and different motors.
- **No threshold was invented.** The only thresholds used are frozen ones (the ≈0.042 nat
  resolution floor; the B4C10 U2/U3/U4 firing rules, quoted but not re-evaluated). Every design
  statement derived from the load label is marked `DESIGN_ONLY` and is not evidential.

---

## 6. Falsifiers for this document itself

1. Recomputing `scale_N` from the frozen TRAIN partition and getting different IEEE doubles.
2. Finding any torque, viscosity, temperature, PMF, or Reynolds field reachable by the motor-stack
   likelihood. (Exhaustive field extraction says the interface is five fields; a sixth would
   falsify §0.)
3. Finding an ordering constraint on `lf` that makes the `Fast`/`Slow` labels of §2.2 correct.
4. Recovering `t_step` from the raw `.mat` `c14de12c…`, which would move the load dimension out of
   **unidentifiable** — retrospectively only, never prospectively.

---

NEXT_ACT = Add a documentation-only correction note to `hierarchical-aif/docs/` recording the M3 `lambdaFast`/`lambdaSlow` label inversion found in §2.2 (frozen `audits/**` stays untouched), and register T1–T10 as the transfer preconditions checklist in the P4 transfer lane so no future transfer proposal can skip a `NOT-MEASURED` group.
