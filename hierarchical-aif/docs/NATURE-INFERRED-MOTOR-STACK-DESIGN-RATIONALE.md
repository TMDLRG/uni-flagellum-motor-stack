# Nature-Inferred Motor-Stack Design Rationale

**Status:** DESIGN RATIONALE. Raises no P-level by itself.

```text
Nature supplies the architecture candidate. The gate supplies the status.
```

Biology may motivate what we build. Only a receipt moves a gate. **Never write "nature proves
parity."**

---

## 1. Function

Bacterial flagellar-motor behaviour: stator occupancy and remodelling, transitions between
occupancy states, dwell timing in each state, switching, and load adaptation.

## 2. Constraint regime

Molecular motor; stochastic transitions; **limited observations** (1349 events, 99 motors, one
study); strong **motor-level heterogeneity**; **right-censored** dwells (109, one terminal per
motor trace); no recorded interventions.

## 3. Extracted principles (what we take)

| principle | why it transfers | where it lands |
|-|-|-|
| **Hierarchy** | motors differ; pooling them is a modelling error, not a convenience | `Lmotor-5/4` — population prior + per-motor latent |
| **Markov blanket** | the analyst sees only the blanket, never hidden state | `Lmotor-0` observed event record |
| **Hazard / survival** | a dwell that has not ended still carries information | `hazard_survival.py` — censored `log S`, uncensored `log h + log S` |
| **State conditioning** | dwell statistics depend on occupancy | per-state scale normalisation |
| **Motor as experimental unit** | replication is across motors, not events | motor-equal scoring, motor-cluster bootstrap |

## 4. What is FORM — deliberately not copied

Stator stoichiometry, torque-speed curves, protein structure, PMF biophysics, ion flux. These are
biological embodiment details. Reproducing them in software would be **imitation, not evidence**,
and would not make any gate move.

## 5. What is PRINCIPLE — implemented

Nested inference over an exchangeable unit; survival-aware likelihood; per-unit heterogeneity
integrated rather than freely estimated; state-conditioned dynamics; a strict observation boundary.

## 6. What can be tested NOW

- duration likelihood on held-out motors (`durationS` was prospectively spent — legitimate)
- censoring correctness
- motor-level hierarchy
- state conditioning
- comparison against control and adversarial baselines under a CI-bound verdict

## 7. What CANNOT be tested now

| item | why |
|-|-|
| biological `G` / policy selection | dataset is passive; **action set structurally empty** |
| prospective mark process | holdout mark channel burned (**D5**) — retrospective-only |
| closed mark-chain model | impossible marks + open alphabet (**D6**) |
| intervention response | no perturbation data (`P5`) |
| transfer | one study only (`P4`, `P7`) |

## 8. Deliberate simplicity

The constrained F-side model has **2 free parameters**. Per-motor latents are integrated by
33-node Gauss-Hermite quadrature rather than estimated, so parameter count does not grow with motor
count. A model with 80 free per-motor shapes would fit 80 numbers to a median of 7 events each and
could not be honestly scored.

**Adding `Lmotor-2` policies would add unidentifiable capacity, not testability.** That is why the
level is specified in the architecture and deliberately not instantiated. Against a corrected
resolution floor of **≈0.042 nats**, flexibility that cannot be resolved is not neutral — it is a
way to look complete while being untestable.

## 9. Falsifiers

The design is wrong, or at least unsupported, if:

1. adversarial dwell baselines (M0/M1/M2/M5/M8) win or tie under corrected CI-bound tests;
2. corrected **B4C02** shows the adverse M2-over-M3 result reproduces under misspecified
   generators — i.e. it is a heavy-tailed **shape artifact**, not mechanism-bearing;
3. corrected **B4C11** fails to support the motor-level hierarchy;
4. the model proves unidentifiable at the achievable resolution;
5. independent transfer fails.

**Falsifier 2 is live right now** — B4C02 is running, and its frozen prediction expects
`GENERATOR-ROBUST_ADVERSE`, which if confirmed **weakens** the mechanistic reading of M3's loss.
The design was committed to that test before its outcome was known.

## 10. Forbidden readings

- that biological correspondence constitutes parity evidence
- that architectural inspiration substitutes for a receipt
- that the motor stack demonstrates anything about the human `L0..L12` stack
- that computing `F` implies the motor performs inference
