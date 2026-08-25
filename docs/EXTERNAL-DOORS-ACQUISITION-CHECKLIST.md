# External-doors acquisition checklist — the parity gates no software can move

*Drafted 2026-08-19, keyed to `docs/MODEL-STATE-SNAPSHOT-2026-08-19.html`. Planning artifact,
uncommitted, for operator review. It **relabels no gate** and manufactures no pass. Every
acceptance criterion below is quoted verbatim from the frozen pre-registration
(`experiments/cross-study-preregistration.v1.json`) or the machine gate reports.*

## Why this document exists

The model sits at **P3 (held-out predictive, as an executed activity)** on the P0–P8 parity
ladder. The next rungs — **P4 transfer, P5 intervention, P7 independent replication** — and eight
`BLOCKED_EXTERNAL` gates **cannot be closed by any amount of modelling, code, or analysis in this
repository** (`docs/CROSS-STUDY-PARITY.md:251`). "Fully replicating the behaviour in inference" is
therefore a **target world defined by external receipts we do not yet hold**, not a software finish
line. This checklist is the acquisition contract for those receipts.

A door is credited **only** when real external evidence lifts its status out of
`BLOCKED_EXTERNAL` / `NOT_ESTABLISHED` — **never by relabeling**, and never by averaging a missing
domain away (`X16` stays `FAIL` while any required gate is non-PASS).

| Door | Gates | Nearest effort | Operator-gated |
|---|---|---|---|
| **P4 transfer** | X10, H-AIF-G8, G08 | in-repo scaffold ~days · external data weeks–months | data licensing / collaboration |
| **P5 intervention** | G10 / X12 (+ G09 substrate) | **12–36 months**, specialised wet lab | verdict sign-off (S4) + funding |
| **P7 live** | G11 / X13 | ~weeks (aperture already built) | instrument + prospective run |
| **P7 physical** | G13 / X15 | ~weeks, bench-scale | print + metrology |
| **P7 replication** | G12 / X14 | **months–quarters** (critical path) | engage + fund an independent lab |

---

## Door P4 — TRANSFER (first unsatisfied rung)

**Gates:** `X10_CROSS_STUDY_PARAMETER_TRANSFER` NOT_ESTABLISHED · `H-AIF-G8` NOT_LOCATED ·
`G08_LOAD_TORQUE_TRANSFER` BLOCKED_EXTERNAL.

**Acceptance criterion (verbatim, `cross-study-preregistration.v1.json:107-109`):**
> "At least one mechanistic parameterization frozen on one laboratory/study predicts a second
> laboratory's commensurate raw observations with a predeclared advantage over baselines.
> Source-paper predictions or unit-incompatible mappings do not count."

**What it needs.** A **second, independent held-out cohort** of single-motor stator/dwell series
that is **commensurate** with the current lab across all six axes, then a freeze-on-A / score-B
protocol:

1. **Strain** — same organism and genotype (E. coli behavioural evidence stays separate from
   Salmonella/Bacillus structural; a structural dataset does **not** transfer a behavioural claim).
2. **Load** — matched viscous-load / bead-size regime (G08 needs a full multi-load surface, not one
   post-electrorotation regime).
3. **Perturbation** — same intervention family; for G08/P5, recorded onset with paired pre/post on
   the **same** motors.
4. **Calibration** — instrument calibration released with the raw data, so `OBSERVED` is earned.
5. **Units** — the same observable (dwell duration, state, censor flag), so the frozen scoring rule
   transfers without a units change. Forcing a common coefficient across incompatible assays is
   forbidden — this is the exact axis on which the current corpus fails
   (`cross-study-parity-report.json:653`).
6. **Observation operator** — same measurement model mapping latent state to recorded signal.

**Protocol.** Freeze the mechanistic parameterization entirely on lab A → predeclare and **commit**
the split + scoring rule + baselines **before any lab-B held-out field is read** (prospectivity is
decided by the commit graph: the prediction commit must be a proven strict ancestor of the result
commit) → score untouched lab B **once**. The cohort must carry enough independent **motors**: 19
holdout motors is nesting-blind, and the motor count at which a 0.042-nat contrast resolves at ≥80%
is **not yet measured on real data** — derive it from a real-data power atlas, never choose N after
seeing an interval width.

**Falsifier.** Transfer is refuted / `H_PARITY` fatally weakened if, on the independent cohort with
everything predeclared: (a) a simple adversary (M2 lognormal) beats the motor-stack candidate by a
CI-bound **material** margin above the 0.042-nat floor; **or** (b) parameter recovery fails on
genuine out-of-distribution motors; **or** (c) the frozen lab-A parameterization simply fails to
beat baselines on lab B's raw observations. Each is a legitimate reportable negative; none may be
tuned away.

**Candidate sources.** Published single-motor bead-assay / fluorescent-switch stator-dwell datasets
carrying dwell state + duration + transition target **with motor identities** — **not** Wadhwa-2022
(that holdout is spent, D5). Named load/torque anchors already in-repo:
`10.1038/s41467-021-25774-2`, `10.1038/s41467-019-13030-1`. Natural targets to make commensurate:
Nord 2017, Perez-Carrasco 2022 (load), Antani 2021 (switching), Ito 2021 (assembly; its 4.09 GB
Class-A archive is integrity-verified but is one lab, not a transfer pair).

**Blocking dependencies.** The raw `data/remodeling_data.mat` archive is **absent** (blocks P2
re-derivation and Class-A transfer); no independent second stator-remodelling dataset exists in the
repo (the single hard external blocker); D5 (burned mark channel) and D6 (nextStateN range defect)
constrain any mark-process claim.

**In-repo prep that is agent-authorable now (prepares the door, does not pass it):** commit the
transfer prediction record (split, baselines, scoring rule, motor-count target, falsifier), the
`<TASK>-DATA-ACCESS-PROTOCOL.md`, and the freeze-A/score-B harness. The range-check repair,
quarantine policy, and one-step TRAIN-only conditional are already built and tested.

---

## Door P5 — INTERVENTION · "does a real bacterium implement active inference?"

**Gates:** `G10 / X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY` NOT_ESTABLISHED (the gate proper) ·
`G09_SWITCH_COOPERATIVITY` BLOCKED_EXTERNAL (assay substrate / hard co-requisite — current data
contain **no switching trajectories**). `discriminatingInterventions: 0`.

**Acceptance criterion (verbatim, `cross-study-preregistration.v1.json:119`):**
> "A preregistered intervention must distinguish an Active-Inference-specific causal prediction from
> matched kinetic, control, and non-equilibrium statistical-mechanics alternatives."

**The discriminating experiment (the crown of this whole programme).** A **2×2 factorial live
single-motor assay in E. coli**:

- **Factor 1** — stimulus gradient **present vs absent** (pragmatic / reward value on/off).
- **Factor 2** — sensory ambiguity **high vs low** (epistemic value on/off).
- **Held matched** across ambiguity levels: mean ligand concentration, viscous load, proton-motive
  force.

The Active-Inference-specific signature is the **epistemic term** `−information_gain` in the
expected-free-energy functional `G(π) = risk + ambiguity − information_gain + effort`
(`SCIENCE.md:81-89`): AIF **uniquely** predicts that **raising sensory ambiguity at zero gradient
shifts the CW/CCW switching policy** — an uncertainty-driven action taken *when there is nothing to
climb* — with a **pre-committed sign and magnitude**. The three matched alternatives structurally
**cannot** produce that effect, and each emits a committed **contradicting** prediction:

- **(a) integral-feedback chemotaxis control** → motor bias unchanged at matched mean, zero gradient;
- **(b) non-equilibrium global mechanical coupling** (Mattingly–Tu; in-repo `M_GMC`, X07 PASS) /
  catch-bond → switching set by torque/load/PMF, unchanged by ambiguity alone at matched drive;
- **(c) kinetic hidden-state dwell** (Wadhwa DLT; in-repo `M_DLT`, G02/G04 PASS) → dwell durations
  set by fitted intrinsic rates, insensitive to ambiguity at fixed mean stimulus.

This is expressly **not** Bayesian curve-fitting (the forbidden evidence): it is a prospective
sign-and-magnitude prediction of a behavioural response to an intervention on **sensory
uncertainty**, with mean stimulus and physical drive held constant. **Secondary arm** — an
optogenetic / microfluidic CheY-P clamp that opens the feedback loop; AIF predicts residual
uncertainty-modulated switching a static CheY-P→bias map cannot.

**Apparatus.** Single-motor readout at motor resolution (tethered-cell rotation or bead assay with
back-focal-plane interferometry / high-speed switch-time video); a programmable microfluidic device
with independently controllable mean, zero-mean fluctuation spectrum (ambiguity) and gradient; an
in-vivo CheY-P FRET reporter (CheY-YFP / CheZ-CFP); matched-load beads / defined-PMF medium.
**Controls (pre-registered):** dCheY/dCheA (loop broken — epistemic effect must vanish), dCheR dCheB
(adaptation disabled), smooth/tumbly-bias. **Unit = the individual motor/cell**; switching events
and frames are not independent replicates.

**Falsifier.** AIF-as-mechanism is falsified if the ambiguity factor produces **no** switching
change at zero gradient beyond the pre-committed noise floor (data inside the "no-epistemic-effect"
prediction, outside the AIF interval). The gate **fails to discriminate** (stays NOT_ESTABLISHED,
never silently a pass) if any pre-enumerated serious mimic — e.g. a noise-adaptive-gain controller —
matches the shift as well or better; such mimics must be **frozen in advance** or the discrimination
is declared collapsed.

**Estimated effort.** ESTIMATE-class: ~**12–36 months** in one specialised single-motor
bacterial-biophysics lab, then a second independent lab for G12/X14. Not on the software critical
path.

**In-repo prep that is agent-authorable now:** freeze the four competitor models with
calibration-only parameters (AIF EFE with frozen γ / C / A / B; **an integral-feedback chemotaxis
controller — NOT yet in-repo, must be added and frozen**; `M_GMC`; `M_DLT`); write the
prediction-record templates (point + interval, explicit sign + magnitude); draft the
pre-registration for **operator sign-off (S4)**. This prepares the door; only a live organism, an
intervention on uncertainty, and predictions committed before outcome can pass it.

---

## Door P7 — REPLICATION + LIVE + PHYSICAL

Three separable external acquisitions; each is individually required for `X16` full parity.

### Live signal chain — `G11 / X13` (BLOCKED_EXTERNAL)
**Acceptance (verbatim, `cross-study-preregistration.v1.json:124`):**
> "A calibrated instrument provides timestamped raw signal, uncertainty, prediction-before-outcome,
> and immutable audit linkage during the same live run."

The Web Serial **aperture is already built** (`app/uni-flagellum-lab.tsx:539-575`;
`serialAdapterImplemented: true`). Missing: a real single-motor rig (tethered-cell / bead assay)
driven by an MCU emitting the frozen serial contract — UTF-8 NDJSON at 115200 baud with
`t_ms, ligand_uM, motor_rpm, rotation, load_pNnm, pmf_mV` (`docs/HARDWARE.md:4-19`) — plus a
calibration record, an uncertainty band, the model version, and a **prediction committed before the
outcome** (device time kept independent from browser `receivedAtMs`). **Falsifier:** the prediction
commit is not a strict git ancestor of the outcome commit (retrospective); or uncalibrated; or the
two clocks collapse; or required rotation fields missing/non-finite. **Effort ~weeks** — a
bench-encoder shakedown can precede a wet motor.

### Independent replication — `G12 / X14` (BLOCKED_EXTERNAL, critical path)
**Acceptance (verbatim, `cross-study-preregistration.v1.json:129`):**
> "A laboratory independent of the model authors reproduces the predeclared effects and releases raw
> data, calibration, exclusions, and analysis provenance."

A lab **independent** of the four corpus author-groups (Wadhwa 2022, Ito 2021, Antani 2021,
Lisevich 2025) **and** of this software. Transfer the frozen protocol unchanged — including exclusion
criteria and failure rules — and require publication of all raw files, calibration, exclusions, and
provenance. `independentLaboratories: 0`. **Repository replay and independent re-implementation do
NOT count.** **Falsifier:** shared personnel / shared code; or not all artifacts released; or the
predeclared effects not reproduced under the protocol's own rules. **Effort: months–quarters,
fully external — this dominates the road to P7/P8.**

### Physical model validation — `G13 / X15` (BLOCKED_EXTERNAL)
**Acceptance (verbatim, `cross-study-preregistration.v1.json:134`):**
> "The exported UNI physical model is fabricated, measured against dimensional tolerances, and its
> sensor-to-screen math trace is tested with real inputs."

Fabricate `cad/uni-flagellum-educational-model.scad` (`parametricCadExportImplemented: true`), then
run the 10 fabrication gates (`docs/HARDWARE.md:64-73`): tolerance coupon, caliper metrology,
recorded fit/backlash, **regenerate clearance from corrected CAD (never sand evidence away)**,
per-gear print, free-rotation check, and confirm the **Markov-boundary plate has only its two
declared apertures with no undeclared shaft crossing**. Then install/calibrate rotary encoders and
bind the measured gear trajectory to the on-screen identity `θ_posterior = θ_prior + θ_likelihood`,
reporting encoder error, backlash, and calibration residual. `physicalPrintRuns: 0`,
`measuredBacklashRuns: 0`. **Falsifier:** measured angles/backlash miss the identity beyond the
declared band; or an undeclared shaft crosses the boundary plate; or clearance was sanded rather
than regenerated. **Effort ~weeks, bench-scale, largely in-house** (requires adult supervision for
small rotating parts).

---

## What must not be done

- **No relabeling.** A `BLOCKED_EXTERNAL` / `NOT_ESTABLISHED` gate leaves that status only on real
  external evidence. Turning a green software gate into a biological-parity claim is the contract
  violation this whole ladder exists to prevent.
- **No averaging** a missing external domain into a pass. `X16` is conjunctive.
- **No claim-wording drift.** No unqualified "full/exact parity with nature", no "digital life"
  (the claim fence, `CLAUDE.md`). Verdicts are operator-signed (S4).
- **Species discipline.** E. coli behavioural evidence never conflated with Salmonella/Bacillus
  structural evidence, nor a live/printed/replicated `OBSERVED` measurement with model output.

## Provenance

Every acceptance criterion above is quoted from `experiments/cross-study-preregistration.v1.json`
(X10:107-109, X12:117-119, X13:124, X14:129, X15:134, X16:139) and the machine reports
`experiments/results/cross-study-parity-report.json` and
`experiments/results/science-gates-report.json`. Requirement detail traces to
`docs/CROSS-STUDY-PARITY.md:224-251`, `docs/SCIENCE.md:81-136`, `docs/HARDWARE.md:4-73`,
`hierarchical-aif/protocols/NEXT-GATE-TRANSFER-AND-INTERVENTION-PLAN.md`, and
`hierarchical-aif/protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md`. Assembled from the
3-agent external-doors mapping, 2026-08-19.
