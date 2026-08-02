# Observed single-motor experiment

## Result in one sentence

In a motor-level held-out analysis of the source-pinned Wadhwa et al. single-
motor stator-remodeling data, dwell-time variability rejected a homogeneous
memoryless process and the frozen UNI two-timescale mixture predicted unseen
durations better than that null; however, a lognormal baseline achieved a
slightly better held-out log score than the UNI mixture.

This is evidence about dwell-time structure and predictive models. It is not
evidence that a bacterium performs Active Inference or contains the latent
variables used by UNI.

## Source identity

- Primary article: Wadhwa et al., *Nature Communications* 13, 5327 (2022),
  <https://doi.org/10.1038/s41467-022-33075-5>
- Public source repository:
  <https://github.com/navishwadhwa/multi-state-remodeling>
- Frozen source commit: `c83119131c3ce3742460a2e3b6bd6c6e44bef4d5`
- Raw file: `data/remodeling_data.mat`
- Raw SHA-256:
  `c14de12cc11df8af2ab87f1ec94629eebc249c0e1475c24f850f5a28ddd1ea22`
- Source repository license: MIT

The source paper reports 50 Hz stator-remodeling traces from individual
tethered *E. coli* motors after electrorotation is removed and load increases.
The public raw artifact contains 129 motor records.

## Frozen protocol and data boundary

`experiments/preregistration.v1.json` was frozen before this implementation
computed its outcomes. The source paper's conclusion was already known, so this
is honestly classified as a local reproduction and prospective held-out
prediction protocol—not blind discovery or third-party preregistration.

The observation boundary contains only:

```text
motor identity, timestamp, step-fitted stator occupancy
```

The analysis never reads a source-paper molecular label as a hidden truth. It
also never uses holdout durations or transition directions to fit parameters.
All events from a motor stay in one partition:

```text
partition(motor) = SHA256(motor_name) mod 5
holdout when remainder = 0; training otherwise
```

The first dwell in the analysis window is discarded as left-truncated. The last
dwell is recorded as right-censored and excluded from the uncensored duration
likelihood. Primary states are `N = 0..8`; the frozen eligibility gate requires
at least 20 holdout events from at least five holdout motors for each state.

## Predictive models

For every eligible stator count `N`, the training mean duration `μ_N` is frozen
and each duration is normalized:

```text
y = t / μ_N
```

All model densities have mean one on the normalized scale. The seconds-scale
predictive density includes the Jacobian `1/μ_N`.

### M0: homogeneous memoryless baseline

```text
p(y) = exp(-y)
S(y) = exp(-y)
CV² = Var(T) / E[T]² = 1
```

### M1: Weibull baseline

One common shape `k` is fitted on training events. Its scale is constrained to
`1 / Γ(1 + 1/k)` so the normalized mean remains one.

### M2: lognormal baseline

One common `σ` is fitted on training events, with `μ_log = -σ²/2` so the
normalized mean remains one.

### M3: UNI two-timescale generative model

```text
p(y) = w λ_fast exp(-λ_fast y)
     + (1-w) λ_slow exp(-λ_slow y)

w/λ_fast + (1-w)/λ_slow = 1
```

`w` and `λ_fast` are fitted on training data. `λ_slow` is fixed by the mean-one
constraint. When an observed dwell survives without a transition, the declared
Bayesian posterior is exact:

```text
q(slow | T > y)
  = (1-w) exp(-λ_slow y)
    / [w exp(-λ_fast y) + (1-w) exp(-λ_slow y)]
```

This is an inference performed by the UNI analysis model. The historical data
contain no measurement of a bacterium's posterior, so the posterior is never
attributed to the biological motor.

## Results

The frozen eligibility rule retained states `N = 1..8`, 793 training events
from 80 motors, and 233 held-out events from 19 different motors.

The mean held-out `CV²` across eligible states was `3.150`, with a 95% motor-
cluster bootstrap interval `[1.514, 3.568]`. The complete interval lies above
the memoryless value of one.

Training-fitted M3 improved held-out log predictive density over M0 by `0.210`
nats per event, with 95% motor-cluster interval `[0.069, 0.325]`.

Held-out mean log scores, where higher is better:

| Model | nats/event |
|---|---:|
| M0 exponential | -3.260 |
| M1 Weibull | -3.096 |
| M2 lognormal | **-3.013** |
| M3 UNI two-timescale | -3.050 |

M3 minus M2 was `-0.037` nats per event, interval `[-0.068, 0.015]`. Therefore
the observed run does **not** establish M3 as the best tested predictive model.
M3 beats the strict memoryless null, is unresolved against Weibull, and is
slightly worse than lognormal on this holdout.

State-conditioned transition-direction frequencies slightly improved the point
estimate of holdout log loss, but the interval crossed zero. That secondary
result is inconclusive.

## What was proved, supported, and left open

The exact algebra proves only consequences of each declared probability model.
The deterministic tests establish that the code implements those declared
calculations for the tested contracts.

Within the frozen analysis population, the observed data support:

- dwell timing inconsistent with a homogeneous memoryless duration model;
- held-out predictive value in modeling more than one timescale;
- an exact shift toward the slower M3 posterior when a dwell survives longer.

The run does not distinguish among all causes of non-memoryless timing.
Cell-to-cell heterogeneity, temporal nonstationarity, continuous rate mixtures,
measurement segmentation, and discrete molecular states remain competing
explanations. The lognormal result makes this limitation empirical, not merely
verbal.

The data contain no action selected by a UNI agent, no policy manipulation, and
no measurement of a biological belief. Consequently, this experiment tests the
observation/prediction part of the generative model only. It does not test an
Active Inference action loop.

## Uncertainty and audit trail

All reported intervals use 2,000 nonparametric bootstrap replicates with motors,
not events, as the resampling unit; seed `20260717`. The event artifact preserves
every exclusion and censored dwell. The result JSON preserves fitted parameters,
state summaries, scores, calibration diagnostics, curves, claims, limitations,
and code/data identities.

Machine-readable artifacts:

- `experiments/preregistration.v1.json`
- `experiments/data/wadhwa-2022-events.json`
- `experiments/results/observed-experiment-report.json`
- `experiments/results/audit-manifest.json`

## Reproduce

Install the frozen CPU analysis dependencies, obtain the pinned upstream raw
file, and run:

```bash
python -m pip install -r requirements-experiments.txt
python scripts/ingest-wadhwa-data.py /path/to/remodeling_data.mat
npm run experiment:run
npm run experiment:verify
npm test
```

Ingestion stops on a raw-file hash mismatch. Running the experiment twice from
identical protocol, event, and code identities must produce an identical report
SHA-256. `experiment:verify` independently rebuilds the model fits, held-out
scores and overdispersion statistic with NumPy/SciPy and fails if they disagree
with the production JavaScript engine.
