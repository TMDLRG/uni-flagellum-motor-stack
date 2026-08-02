# Scientific and mathematical contract

## Scope

The release is a cross-scale, evidence-linked teaching and experiment surface.
It does not assert that a bacterium contains literal gears, that the reduced
world equations replace molecular models, or that a successful fit establishes
the biological implementation of an internal probabilistic representation.

## Separation

`stepWorld(world, action, controls, dt)` is the external world process. It owns
ligand-field state, true gradient, cell pose, receptor state, CheY-P, stator
occupancy, torque, rotor speed and direction.

`observeWorld(world, controls, receivedAt)` is the sensory boundary. The
Observation schema intentionally excludes true gradient and stator occupancy.

`stepAgent(agent, observation, dt)` receives only the Observation record. It
cannot import, reference or inspect the world object. It returns beliefs,
predictions and a bounded RUN/TUMBLE action.

## Biological world equations

The synthetic world uses an explicitly reduced MWC-style receptor mapping:

```
f_r = N[ε₀ − ε_m m + ln((1 + L/K_off)/(1 + L/K_on))]
a_r = 1/(1 + exp(f_r))
dm/dt = k_m(a_target − a_r)
```

CheY-P relaxes toward a receptor-activity-dependent target. Stator occupancy
relaxes toward a load-dependent target between zero and eleven units. Stall
torque is proportional to stator occupancy and ion-motive force. Speed falls
with external load. A torque-dependent effective dissociation constant feeds a
Hill switching curve.

These equations are **MODELED / TEACHING REDUCTION**. Their variables and units
are visible in the interface. They are not fitted reproductions of any one
primary paper.

## Exact categorical inference

Hidden gradient state:

```
s ∈ {falling, flat, rising}
```

Predictive prior and update:

```
q⁻(s_t) = Σ B_π(s_t|s_{t-1}) q(s_{t-1})
q(s_t) = η p(o_t|s_t) q⁻(s_t)
```

For rising against falling, the physical gear identity is exact:

```
ln O_posterior = ln O_prior + ln likelihood-ratio
```

Angles encode these natural-log odds. The browser calculation is authoritative;
measured backlash becomes uncertainty rather than a hidden correction.

## Variational free energy

```
F[q] = Σ_s q(s)[ln q(s) − ln p(o,s)]
     = KL[q(s) || p(s|o)] − ln p(o)
     ≥ −ln p(o)
```

The present categorical update uses the exact posterior under its declared
model, so the KL term is zero to numerical tolerance. `q` remains conceptually
and structurally distinct from the exact posterior even where equality is
tested.

## Expected free energy

```
G(π) = risk(π) + ambiguity(π) − information_gain(π) + effort(π)
Q(π) = softmax(−γG(π))
```

RUN and TUMBLE receive the same observations, preference vector, outcome model,
horizon and precision. Each term is emitted separately in the UI.

## Two free energies

Thermodynamic free energy from the ion gradient performs motor work and is
reported in physical energy units. Variational free energy is an
information-theoretic model-evidence quantity reported in nats. They are not
numerically substituted for each other.

## Primary evidence anchors

1. Antani et al., *Nature Communications* 12, 6432 (2021), mechanosensitive
   stator recruitment and CheY-P binding.
   <https://doi.org/10.1038/s41467-021-25774-2>
2. Wadhwa et al., *Nature Communications* 13, 5327 (2022), multi-state
   mechano-adaptation.
   <https://doi.org/10.1038/s41467-022-33075-5>
3. Lo et al., *PNAS* 115, 1190–1195 (2018), zero-load speed, ion-motive force
   and stator-number scaling.
   <https://doi.org/10.1073/pnas.1708054114>
4. Mattingly and Tu, *Nature Physics* 22, 131–138 (2026), nonequilibrium global
   mechanical coupling as a current theoretical account.
   <https://doi.org/10.1038/s41567-025-03105-2>

## Release falsifiers

- A hidden world field enters `stepAgent`.
- A synthetic frame is labeled as a live measurement.
- Prediction is overwritten by the later observation instead of scored.
- Posterior probabilities fail normalization or the VFE identity.
- RUN and TUMBLE are scored with unequal information.
- A thermodynamic quantity is shown with informational units or vice versa.
- The physical model is described as a bacterial-motor replica.

## Observed-data result

The laboratory now includes a source-pinned, motor-level held-out analysis of
the Wadhwa et al. 2022 single-motor stator-remodeling data. The held-out timing
rejects a homogeneous memoryless duration model, and the frozen two-timescale
UNI mixture predicts the held-out durations better than that null. A lognormal
baseline obtains a slightly better held-out log score than UNI, so the run does
not establish the UNI mixture as the best tested model and does not identify its
latent components with biological states.

This historical observational dataset does not contain a UNI-selected action or
a measured biological posterior. It constrains only the observation and
prediction portion of the declared generative model. See
[`docs/OBSERVED-EXPERIMENT.md`](OBSERVED-EXPERIMENT.md) for the full protocol,
equations, results, uncertainty, alternatives and reproducibility trail.

## Scientific parity status

The mechanistic parity layer now implements the source paper's D–L–T
first-passage survival equation, a joint on/off competing-risk likelihood, and
right-censoring contributions. It also executes source-artifact parity,
synthetic parameter recovery, and motor-level held-out prediction gates.

Full parity is not achieved. The public code bundle does not reproduce the
article's source-workbook theory arrays, one of three parameter-recovery runs
fails its frozen tolerance, and the held-out mechanistic advantage has a
motor-cluster interval crossing zero. Load transfer, switching cooperativity,
live instrumentation, independent biological replication, and physical-print
validation require new external work. No biological Active-Inference identity
is established.

See [`docs/SCIENCE-GATES.md`](SCIENCE-GATES.md) and the machine-readable
`experiments/results/science-gates-report.json` ledger.
