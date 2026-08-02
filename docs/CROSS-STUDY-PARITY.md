# Cross-study biological parity program

## Verdict

The expanded UNI-FLAGELLUM model expresses substantially more observed
biology, but **full and complete parity is false**. The frozen protocol has 16
conjunctive gates: 8 PASS, 3 FAIL, 2 NOT_ESTABLISHED, and 3 BLOCKED_EXTERNAL.
No score averaging can turn a missing required domain into parity.

The strongest new positive result is not a claim of one universal equation. It
is a traceable modular model spanning stator dwell kinetics, rotation-gated
assembly, stator/CheY association, torque-conditioned switching, a
non-equilibrium switching generator, occupancy statistics, and whole-cell
propulsion. The strongest new falsifier is that the exact 13-site lattice gives
incompatible interaction strengths when fitted to full occupancy distributions
versus occupancy moments.

This release is deterministic, CPU-only, and contains no LLM or GPU in the
runtime or analysis path.

## Evidence population and independence

The corpus contains 11 explicitly attributed studies across five observation
scales. Four study families provide direct primary artifacts. The conservative
lower bound is 409 independent motors or cells:

| Direct study | Conservative independent-unit count |
|---|---:|
| Wadhwa 2022 | 109 motors |
| Ito 2021 | 40 motors/cells |
| Antani 2021 | 154 motors/cells |
| Lisevich 2025 | 106 cells |
| **Total lower bound** | **409** |

The lower bound deliberately avoids pseudoreplication. Ito's source workbook
contains 191,920 rotation samples and 159,800 stator-occupancy samples, but
those 351,720 time samples are not counted as independent organisms. Multiple
measurements of one motor remain one experimental unit.

The separately cached Ito raw-trace archive is 4,085,227,742 bytes. A full
streaming verification matched MD5
`d42879e66142ff7190f256f4276db111`, parsed 505 ZIP entries, and found no member
CRC failure. The normal test suite checks the committed verification ledger
instead of rehashing 4.09 GB. `npm run cross-study:verify-raw` repeats the deep
archive audit when the external cache is present.

## Evidence classes

| Tier | Meaning | Eligible use |
|---|---|---|
| A | Raw or motor/cell-level artifact from the primary study | Direct reanalysis with the study's independence unit |
| B | Primary-study source workbook with plotted values or aggregates | Source reproduction and aggregate model discrimination |
| C | Values digitized or reanalyzed by a later primary paper with attribution | Attributed comparison only |
| D | Narrative or table-only published constraint | Constraint or design input, never raw-data replication |

The protocol was frozen after inspecting published sources but before coded
gate execution. It is therefore a post-publication reproduction and stress
test, not a blind preregistration or independent confirmation.

## Model organism: modules, boundaries, and equations

The model is one auditable organism in the engineering sense: every module has
a declared biological domain, observation operator, units, evidence tier, and
claim boundary. It is not one undifferentiated parameter vector. Parameters
cross a study boundary only when strains, interventions, loads, units, and
measurement operators are commensurate.

### M_DLT: post-perturbation stator dwell kinetics

For stator occupancy `N`, the source-derived first-passage survival is a finite
mixture:

```text
S_N(t) = sum_j a_j(N) exp[-r_j(N)t]
r_j(N) = k_+(N) + N sigma_- + j(sigma_+ - sigma_-)
P_+(t|N) = k_+(N) S_N(t)
P_-(t|N) = -dS_N(t)/dt - P_+(t|N)
```

Observed event direction, dwell duration, censoring, and motor identity define
the likelihood. This module remains partially identified; its hidden
timescales are not molecular identities.

### M_ROTATION_GATE: signed rotation-dependent stator binding

```text
b(omega) = b0 + a_plus max(omega, 0) + a_minus max(-omega, 0)
```

Weighted fits use the source-reported standard errors. Prediction is evaluated
by leaving out a complete speed bin, never an individual time point. The
20-Hz-bin fit gives:

```text
b0      = 0.1544997646 s^-1
a_plus  = 0.0176841082 s^-1 Hz^-1
a_minus = 0.0319566693 s^-1 Hz^-1
LOO RMSE = 0.8293641
constant-baseline LOO RMSE = 1.4544735
relative improvement = 42.9784%
```

The criterion also passes at 5-Hz and 10-Hz bin widths. This supports a signed
speed-rate relationship in the source aggregate. It does not make speed bins
independent motors, and it does not identify a molecular sensor.

### M_LATTICE13: exact finite occupancy lattice

For binary occupancy `phi_i` on a periodic lattice of length 13:

```text
P(phi | J, mu) = exp[J sum_i phi_i phi_(i+1) + mu sum_i phi_i] / Z(J, mu)
P(N | J, mu) = sum_{phi: sum phi_i=N} P(phi | J, mu)
```

The implementation enumerates all `2^13 = 8192` states exactly. It jointly
fits three bead/load distributions with a shared `J` and load-specific `mu`.
It also independently fits the reported occupancy standard deviations, which
reproduces the published moment estimate.

This is a decisive internal disagreement:

```text
full-distribution J = 0.2106346292
moment-fit J         = 1.1875632937
reported-SE-weighted moment J = 1.0705756792
absolute cross-statistic difference = 0.9769286644
full-distribution probability RMSE = 0.0344230431
Delta AIC in favor of J>0 model = -1.4588058431
```

The probability RMSE is small, but the extra cooperative parameter is not
favored over `J=0`, and the preregistered range/AIC criteria fail. This does not
erase the measured occupancy distributions. It shows that a single molecular
interaction energy is not identified consistently by these aggregate
statistics under this lattice model.

### M_GMC: non-equilibrium switching generator

The CPU port uses a continuous-time Markov generator over engaged and
unengaged conformational counts. Local torque exponentially modulates engaged
subunit switching rates; rotor motion exchanges engaged and unengaged
subunits. For generator `Q` and stationary distribution `pi`:

```text
Q_ij >= 0 for i != j
sum_i Q_ij = 0
Q pi = 0
sum_i pi_i = 1
```

At the frozen source condition, the independent port has 175 states, maximum
column-sum error `8.53e-14`, stationary residual `9.55e-15`, and engaged-state
marginal L1 error `0.0176053` against the authors' source output. This verifies
the ported generator and stationary calculation, not experimental truth.

Against attributed Yuan 2009 switching observations inside the source model's
speed support, 7 of 11 points in each switching direction fall within the
digitized asymmetric error bar. Mean absolute standardized residuals are
`0.7876` for CW-to-CCW and `0.8760` for CCW-to-CW. This passes the frozen source
reproduction gate but is not held-out cross-laboratory parameter transfer.

### M_RFT: whole-cell propulsion

Published resistive-force-theory predictions are compared with independently
reported cell speed at matched flagellar count. The ten-point source comparison
has RMSE `1.7274107 um/s`, versus `2.0537120 um/s` for a constant-mean baseline,
a `15.8884%` improvement. The measured motor-speed slope is
`-0.5112 Hz/flagellum`, with 95% interval `[-2.1945, 1.1721]`, which includes
zero. This supports the declared source-level propulsion gate, not a universal
strain- and medium-independent law.

## Additional observed couplings

Antani motor/cell-level fluorescence gives a MotAB-associated CheY signal
difference of `1.13324`, Hedges `g=0.7774`, Welch `p=0.000817`, and a 5,000
motor-bootstrap 95% interval `[0.56641, 1.82915]`. The required FliM and
rotating-versus-stalled controls are retained and nonsignificant (`p=0.6087`
and `p=0.5678`). This supports association/coupling, not an unrestricted causal
chain.

Across nine Antani torque conditions, torque correlations are `rho=1.0000` for
CW-to-CCW and `rho=0.9333` for CCW-to-CW, while CW-bias coefficient of variation
is `0.1000`. These are aggregate condition-level results because a shared-cell
covariance artifact is unavailable.

## Gate ledger

| Gate | Status | What the result establishes |
|---|---|---|
| X01 source integrity | PASS | Frozen manageable artifacts plus the separately verified 4.09 GB raw tier are integrity-bound. |
| X02 corpus breadth | PASS | 11 attributed studies, 5 scales, 4 direct artifact families, and at least 409 independent units. |
| X03 rotation-gated assembly | PASS | Directional piecewise rate beats the constant-bin baseline robustly across 5/10/20-Hz binning. |
| X04 stator/CheY coupling | PASS | Required motor-level contrast and controls meet the frozen statistical rule. |
| X05 torque/switching response | PASS | Both transition rates rise monotonically while bias remains comparatively stable. |
| X06 finite-lattice cooperativity | **FAIL** | Full distributions and moments imply incompatible `J`; `J>0` is not AIC-favored. |
| X07 GMC generator | PASS | Independent stationary generator port meets numerical invariants and source-marginal tolerance. |
| X08 GMC switching observations | PASS | Source prediction meets the frozen attributed-observation threshold in both directions. |
| X09 whole-cell propulsion | PASS | Source RFT prediction beats the constant baseline and motor-speed slope includes zero. |
| X10 cross-study parameter transfer | NOT ESTABLISHED | No unit-safe parameter frozen in one lab has yet predicted commensurate raw observations from another. |
| X11 structural consistency | **FAIL** | Lattice size is not resolved molecular geometry; DLT hidden states lack molecular identity. |
| X12 Active-Inference causal identity | NOT ESTABLISHED | No intervention discriminates Active Inference from matched kinetic/control alternatives. |
| X13 live signal chain | BLOCKED EXTERNAL | Requires a calibrated motor/instrument run with prediction committed before outcome. |
| X14 independent wet-lab replication | BLOCKED EXTERNAL | Requires a laboratory independent of the model authors and this software. |
| X15 printed model validation | BLOCKED EXTERNAL | Requires fabrication, metrology, calibration, and a measured hand-driven run. |
| X16 full biological parity | **FAIL** | Full parity is the conjunction of X01-X15; several required gates are non-PASS. |

## Structural and CAD truth boundary

Five model-state mappings are explicit in
`experiments/structural-state-map.v1.json`. Two conflicts remain:

1. The 13-site occupancy lattice is an assay-specific statistical model, not
   established E. coli molecular slot geometry.
2. DLT weak/strong or age-mixture states are phenomenological until a separate
   molecular measurement identifies them.

The physical export is therefore CAD-ready as a transparent, manipulable UNI
mathematical model. It is not a literal molecular replica of the flagellar
motor. Only dimensions and multiplicities with direct structural provenance
may drive literal molecular geometry; phenomenological states must remain
visually labeled mathematical layers.

## What a complete model still requires

The next discovery cycle is constrained by evidence, not by adding equations:

1. **Commensurate raw transfer:** identify two laboratories with compatible
   strain, load, perturbation, calibration, and observation operator; freeze
   parameters on lab A and score untouched lab B against declared baselines.
2. **Latent-state identification:** collect a simultaneous molecular reporter
   and rotation/stator-occupancy trace to test whether DLT mixture states map to
   specific conformations or binding states.
3. **Distribution-level cooperativity:** acquire motor-resolved occupancy
   distributions and repeated load conditions so cell heterogeneity is not
   absorbed into `J`; compare lattice, independent-site, mixture, and kinetic
   alternatives with held-out motors.
4. **Active-Inference discrimination:** preregister an intervention for which
   an Active-Inference-specific policy/preference model and matched kinetic,
   feedback-control, and non-equilibrium models make different quantitative
   predictions. Bayesian fitting alone is not such evidence.
5. **Live prospective run:** timestamp raw voltage/position, calibration,
   uncertainty, model version, and prediction before revealing the outcome.
6. **Independent replication:** transfer the frozen protocol, including
   exclusions and failure rules, to an independent laboratory and publish all
   raw files and calibration.
7. **Physical validation:** fabricate the abstract UNI model, inspect
   tolerances/backlash, calibrate sensors, and bind a hand-driven mechanical
   trajectory to the same on-screen math ledger.

No software-only action can honestly complete items 5-7. They remain executable
experimental contracts rather than simulated passes.

## Reproduction

The large raw archive is external and ignored by Git. With it present, repeat
the deep integrity check once; the other commands are routine and CPU-only.

```bash
npm run cross-study:verify-raw
npm run cross-study:ingest
npm run cross-study:run
npm run cross-study:verify
npm run science:verify
npm test
npm run lint
```

`cross-study:verify` is a separately implemented JavaScript checker for the
Ito leave-one-bin-out error, exact-lattice SSE and optimized `J=0` baseline,
GMC source comparisons, RFT error, and audit hashes. Running the Python runner
twice must leave report and audit bytes unchanged.

Machine-readable execution artifacts:

- `experiments/cross-study-preregistration.v1.json`
- `experiments/data/cross-study-motor-evidence.json`
- `experiments/structural-state-map.v1.json`
- `experiments/results/ito-raw-archive-verification.json`
- `experiments/results/cross-study-parity-report.json`
- `experiments/results/cross-study-parity-audit.json`
- `scripts/ingest-cross-study-evidence.py`
- `scripts/run-cross-study-parity.py`
- `scripts/independent-cross-study-check.mjs`

The public copies under `public/` are byte-compared in tests where applicable,
so the rendered Verum ledger and downloadable evidence cannot silently diverge
from the experiment results.
