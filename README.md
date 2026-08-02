# UNI-FLAGELLUM

UNI-FLAGELLUM is a transparent, CPU-only digital-organ laboratory that keeps a
bacterial flagellar-motor world process separate from a UNI Active Inference
agent. It exposes the observation crossing, predictive prior, likelihood,
posterior, variational free energy, expected-free-energy policy comparison,
prediction, action and prediction error as they update.

Version 0.3 begins with a thirteen-step living-science walkthrough: licensed
*E. coli* run/tumble microscopy beside a synchronized CPU Canvas2D biological
reconstruction, a labelled multi-species motor cutaway, a separated inference
mirror, authored optional narration, worked paper exercises, gate traceability,
and a private local observer notebook with JSON/CSV/print export and validated
import. See [docs/LIVING-SCIENCE-WALKTHROUGH.md](docs/LIVING-SCIENCE-WALKTHROUGH.md).

The browser can replay frozen observed records, run a deterministic synthetic world, or accept live,
newline-delimited JSON measurements from a serial instrument. Synthetic and
recorded, synthetic, and live signals are never presented under the same label.

## Start

```bash
npm install
npm run dev
```

## Validate

```bash
npm test
```

The test suite checks posterior normalization, the variational-free-energy
identity, log-odds addition, Markov-boundary separation, deterministic replay,
policy normalization, instrument validation, Hellinger distance, CAD
non-claims, observed-data identity, motor-level split integrity, deterministic
experiment replay, censored first-passage likelihoods, failed-gate retention,
adverse-baseline reporting, cross-study source integrity, exact finite-lattice
and GMC invariants, independent numerical reproduction, audit hashes, and the
rendered product shell.

## Reproduce the observed experiment

The `Observed experiment` surface is generated from the source-pinned Wadhwa et
al. 2022 single-motor stator-remodeling dataset. It uses a motor-level holdout,
training-only model fitting and motor-cluster bootstrap uncertainty. It keeps the
result that a lognormal baseline slightly out-scores the UNI two-timescale model
fully visible.

```bash
python -m pip install -r requirements-experiments.txt
python scripts/ingest-wadhwa-data.py /path/to/remodeling_data.mat
npm run experiment:run
npm test
```

See [docs/OBSERVED-EXPERIMENT.md](docs/OBSERVED-EXPERIMENT.md) for the source
hash, frozen protocol, equations, results, limitations and audit trail.

## Execute the scientific parity gates

The `Science gates` surface implements the source paper's D–L–T first-passage
reduction, includes right-censored intervals in a joint on/off likelihood,
tests parameter recovery, evaluates held-out motors, and records every missing
biological or physical gate. The current result is partial parity: four of seven
computational gates pass, three fail, and full biological parity is false.

```bash
npm run science:run
npm run science:verify
npm test
```

See [docs/SCIENCE-GATES.md](docs/SCIENCE-GATES.md) for the exact equations,
source-artifact discrepancy, fitted parameters, gate criteria, results and next
experiments.

## Execute the cross-study parity program

The expanded program binds 11 attributed studies across five observation
scales and conservatively counts at least 409 independent motors/cells. It adds
rotation-gated assembly, stator/CheY coupling, torque-conditioned switching,
an exact 13-site lattice stress test, an independently ported non-equilibrium
GMC generator, and whole-cell propulsion. Eight of 16 gates pass; full parity
remains false because three gates fail, two are not established, and three
require new physical evidence.

```bash
npm run cross-study:verify-raw  # optional deep check when the 4.09 GB cache is present
npm run cross-study:ingest
npm run cross-study:run
npm run cross-study:verify
npm test
```

See [docs/CROSS-STUDY-PARITY.md](docs/CROSS-STUDY-PARITY.md) for evidence tiers,
sample-size discipline, equations, exact results, structural/CAD boundaries,
the full gate ledger, and the remaining experimental contracts.

## Export the physical UNI model

```bash
node scripts/export-cad.mjs
```

This produces a parametric OpenSCAD assembly and machine-readable manifest in
`cad/`. The print is the UNI mathematical model, not a structural or functional
replica of the bacterial engine. Print and measure the tolerance coupon before
printing the full mechanism.

## Scientific discipline

- The world process owns physical truth; the agent never reads hidden state.
- The observation and action records are the only boundary crossings.
- Thermodynamic free energy and variational free energy retain separate units,
  equations and evidence.
- Current biological observations, reduced teaching equations and UNI
  interpretations remain separately labeled.
- Every prediction is retained separately from the later observation and
  residual.

See [docs/SCIENCE.md](docs/SCIENCE.md),
[docs/SCIENCE-GATES.md](docs/SCIENCE-GATES.md),
[docs/CROSS-STUDY-PARITY.md](docs/CROSS-STUDY-PARITY.md),
[docs/HARDWARE.md](docs/HARDWARE.md), and [docs/VERUM.md](docs/VERUM.md).

## Independent agent audit

Repository agents must follow [CLAUDE.md](CLAUDE.md). To commission an
independent Claude / Ultra Code build, validation, mutation, falsification, and
paste-back audit, use
[docs/CLAUDE_ULTRACODE_INDEPENDENT_AUDIT_PROMPT.md](docs/CLAUDE_ULTRACODE_INDEPENDENT_AUDIT_PROMPT.md).
