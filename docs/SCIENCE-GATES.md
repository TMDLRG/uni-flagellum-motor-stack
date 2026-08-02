# Scientific parity gates

> **Cross-study extension:** This document records the original Wadhwa-focused
> gate cycle. The broader, later protocol is documented in
> [CROSS-STUDY-PARITY.md](CROSS-STUDY-PARITY.md). It adds 11 attributed studies,
> at least 409 independent motors/cells, rotation/load/switching/propulsion
> layers, and 16 new gates. Evidence relevant to the original G08/G09 now
> exists in assay-specific modules, but unit-safe cross-laboratory parameter
> transfer is still not established and must not be inferred by merging unlike
> experiments.

## Verdict

The current release has **partial computational parity only**. Four of seven
executable computational gates pass. Three fail. Five further gates require new
instrument, biological, laboratory, or physical-print evidence; a biological
Active-Inference identity is not established.

This is the intended behavior of a science gate: a negative result remains a
negative result in the JSON, tests, documentation, and rendered laboratory.

## What was added

The previous observed experiment fitted generic normalized duration families.
It did not implement the mechanism analyzed by Wadhwa et al. The parity layer
now implements the source paper's D–L–T first-passage reduction:

```text
S_N(t) = Σ_j a_j exp(-r_j t)
r_j = k_+(N) + Nσ_- + j(σ_+ - σ_-)

P_+(t|N) = k_+(N) S_N(t)
P_-(t|N) = -dS_N(t)/dt - P_+(t|N)
```

For `N=1`, `a=[1-c1,c1]`; for `N=2`, the weights are the convolution
of `[1-c1,c1]` and `[1-c2,c2]`; and for `N≥3`, a third factor using `c3`
is included. The weights are normalized and nonnegative under the fitted
constraints.

An observed on transition contributes `log P_+(t|N)`, an off transition
contributes `log P_-(t|N)`, and a right-censored interval contributes
`log S_N(c)`. All events from one motor stay in one partition. Parameters are
fitted only on training motors.

The paper handles the short-lived H state separately by a threshold classifier.
The present likelihood therefore cannot honestly be called a unified D–L–T–H
likelihood. H-state reproduction remains a separate gate.

## Gate results

| Gate | Result | Finding |
|---|---|---|
| G00 source identity | PASS | Raw observations, source workbook, code bundle, derived events, and implementations have SHA-256 identities. |
| G01 separation | PASS | No motor leakage; world observations, latent model, fitting data, and held-out outcomes remain distinct. |
| G02 first-passage math | PASS | Coefficients, survival, rates, and integrated competing-risk densities satisfy the declared equations. |
| G03 public artifact parity | **FAIL** | The public repository's bundled parameter vector does not reproduce the article source workbook's Figure 3 theory arrays. |
| G04 censored joint likelihood | PASS | 76 training and 16 held-out censored intervals in eligible states contribute survival likelihoods. |
| G05 synthetic recovery | **FAIL** | Two of three recovery experiments passed; one missed the frozen tolerance for `c2`. |
| G06 held-out mechanism | **FAIL** | Point advantage over memoryless was `0.0583` nat/interval, but the 95% motor-cluster interval `[-0.0158, 0.1326]` crosses zero. |
| G07 H-state reconstruction | SOURCE ONLY | The source reports 43 wells and rates; the current artifact cannot reconstruct the authors' classification decisions. |
| G08 load/torque transfer | BLOCKED EXTERNAL | The dataset contains one post-electrorotation high-load adaptation regime. |
| G09 switching cooperativity | BLOCKED EXTERNAL | These records do not contain the switching trajectories needed to compare current cooperativity mechanisms. |
| G10 Active-Inference identity | NOT ESTABLISHED | No biological posterior, preference, policy posterior, or UNI-selected intervention was observed. |
| G11 live instrument | BLOCKED EXTERNAL | The serial aperture exists, but no calibrated live motor was connected in this release. |
| G12 independent replication | BLOCKED EXTERNAL | Repository replay is not independent biological replication. |
| G13 printed mechanism | BLOCKED EXTERNAL | CAD exists; no print, tolerance, backlash, or safety run exists. |

## Public-artifact discrepancy

The article reports a moment fit near `c1=0.30`, `c2=0.12`, `c3=0.06`,
`σ+=0.19 s^-1`, and `σ-≤0.0005 s^-1`. Its uncertainty notation is the
parameter displacement producing a 50% loss increase, not a confidence
interval.

The bundled file `fitting_parameters.txt` instead contains `c1=0.613638`,
`c2=0.308125`, `c3=0.162786`, `σ+=0.095787 s^-1`, and `σ-=10^-8 s^-1`.
Running the published code equations with that vector produces a maximum
relative Figure 3 mean-dwell discrepancy of `3.767`, a maximum absolute
`f+` discrepancy of `0.443`, and a maximum absolute normalized-variance
discrepancy of `3.862` against the article's source-data workbook.

There is a second internal discrepancy. The paper's equation says `N=0` has a
single exponential survival, which requires normalized variance `V=1`. The
source workbook reports theory `V(0)=1.5920577617`. The public Python function
applies its `c1` mixture branch to `N=0` for mean and variance while separately
forcing `f+(0)=1`. The ledger records this conflict; it does not choose a silent
correction.

This finding concerns reproducibility of the public theory artifacts. It does
not erase or refute the observed single-motor records.

## Mechanistic fit and identifiability

The training-only censored maximum-likelihood fit gives:

```text
σ+ = 0.1173812392 s^-1
σ- = 0.0005383373 s^-1
c1 = 0.4623986758
c2 = 0.0004212689
c3 = 0.0000010723
```

The collapse of `c2` and `c3` toward zero matters. Under this split, extraction,
and likelihood, three arrival-age coefficients are not practically identified.
The synthetic recovery suite reached the frozen acceptance bounds in two of
three seeds; the third missed `c2` by `0.1384` when the limit was `0.12`.

This is not a reason to remove the failed gate. It is evidence that more data,
a stronger measurement model, or a simpler parameterization is needed before
the coefficients can be assigned stable biological meaning.

## Held-out prediction

The mechanistic model and a state-specific memoryless competing-risk baseline
were fitted on the same training intervals. Every eligible held-out interval,
including its censoring indicator and observed exit direction, was then scored.

```text
D–L–T mean log score:        -3.83808 nat/interval
memoryless mean log score:   -3.89634 nat/interval
difference:                   0.05826 nat/interval
motor-cluster 95% interval:  [-0.01580, 0.13264]
```

The point estimate favors D–L–T, but the interval includes zero. Therefore the
frozen predictive gate fails. It is not reported as “almost proved.”

## Reproduction and audit

```bash
python -m pip install -r requirements-experiments.txt
npm run science:run
npm run science:verify
npm test
```

`science:run` performs the CPU-only fit, 2,000 motor-cluster bootstraps, and
three deterministic parameter-recovery experiments. `science:verify` is an
independent JavaScript implementation of the first-passage equations and
held-out likelihood. Running `science:run` twice must produce the same report
and audit hashes.

Machine-readable artifacts:

- `experiments/source-parity-reference.json`
- `experiments/results/science-gates-report.json`
- `experiments/results/science-gates-audit.json`
- `lib/source-first-passage.js`
- `scripts/run-science-gates.py`
- `scripts/independent-science-check.mjs`

## Work required for biological parity

1. Obtain a tagged final source parameter artifact or author clarification for
   G03 while retaining the original mismatch in provenance.
2. Freeze and independently implement the H-well classifier for G07.
3. Acquire raw motor-identified multi-load occupancy, torque, and switching
   observations for G08 and G09.
4. Prospectively commit predictions before a calibrated live run for G11.
5. Obtain an independent laboratory replication for G12.
6. Print, instrument, measure, and safety-review the physical UNI mechanism for
   G13.

Until those gates are actually executed, “full parity” remains false.
