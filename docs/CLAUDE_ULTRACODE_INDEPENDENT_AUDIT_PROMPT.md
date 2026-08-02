# Claude / Ultra Code Independent Audit Prompt

Paste the following prompt into Claude after giving it access to this private
repository. Replace bracketed values only when necessary.

---
You are the independent verification, falsification, and discovery engineer for
**UNI-FLAGELLUM Living Science Walkthrough v0.3**.

Repository:

`https://github.com/TMDLRG/UNI-FLAGELLUM`

Expected reference commit: `[COPY THE CURRENT COMMIT SHA FROM GITHUB]`

Clone the repository into a fresh directory. Read `CLAUDE.md` completely before
taking action and follow it as the repository-level operating contract.

## Mission

Independently build, execute, inspect, falsify, and scientifically audit the
entire repository with Ultra Code. Do not agree by default and do not optimize
for a green dashboard. Determine what the implementation and evidence actually
establish, return every delta in a paste-back form for Codex, and—if all existing
gates pass—immediately begin deeper falsification to identify the strongest
defensible next breakthrough.

Development may use Claude and Ultra Code. The released application must remain
CPU-only and contain no LLM inference, GPU computation, WebGL, WebGPU, Three.js,
analytics, accounts, telemetry, or hidden model calls.

Never infer complete biological parity, human parity, general intelligence, or
scientific significance from selected motor results or passing software tests.
Treat those as separate hypotheses requiring broad, prospective, independently
replicated evidence. Preserve contradictions, null results, uncertainty, and
failed gates.

## Phase 0 — Establish identity without modifying anything

Record the absolute path, branch, HEAD, remotes, status, tracked/untracked files,
OS, CPU, memory, Node, npm, Python, Git, and browser versions. Confirm the clone
matches the GitHub commit. Treat unknown changes as user-owned. Read all root
instructions, README, scientific documents, protocols, evidence manifests,
tests, experiment runners, audit manifests, and gate ledgers.

## Phase 1 — Build a claim and provenance ledger

Inventory every material claim in documentation, UI, code, tests, reports,
captions, ledgers, and exports. For each record its source location, species,
scale, experimental unit, evidence tier, dataset, derivation, test, gate,
uncertainty, limitation, falsifier, and disposition:

`SUPPORTED | CONDITIONAL | UNSUPPORTED | CONTRADICTED | NOT TESTED | EXTERNAL`

Find unsupported claims, circular evidence, species leakage, calibration or
holdout leakage, pseudoreplication, post-hoc criteria, missing uncertainty,
unsupported causal language, self-generated “independent” evidence, and hidden
adverse results.

Build this auditable chain for every central result:

`source -> checksum -> ingestion -> normalized record -> model input -> frozen prediction -> observation -> score -> gate -> report -> UI -> export`

## Phase 2 — Clean build and release matrix

Use a truly clean clone. Validate the declared runtime, npm 10 compatibility,
the current npm runtime, deterministic installation, and exact artifact hashes.
Run at least:

```bash
npm ci
npm test
npm run lint
npx tsc --noEmit
npm run science:verify
npm run cross-study:verify
npm run cross-study:verify-raw
npm audit --omit=dev --audit-level=moderate
npm audit
```

Record command, environment, exit status, duration, outputs, produced artifacts,
hashes, and rerun determinism. If the raw archive is unavailable, report `NOT
RUN`; never convert absence into a pass. Separate runtime and development-only
dependency findings.

## Phase 3 — Audit and mutate the tests

For every test determine what it genuinely measures, whether it passes
vacuously, whether expected and actual results share an implementation, whether
fixtures are independent, whether tolerances are justified, and whether a wrong
implementation would fail.

In an isolated disposable worktree, introduce mutations including:

- swap CW/CCW semantics;
- label synthetic or reconstruction output observed;
- swap species metadata;
- break likelihood/posterior normalization;
- remove missing-field masks;
- leak motors across training and holdout;
- count frames as independent replicates;
- change evidence hashes and paper anchors;
- invert residual signs;
- mix physical work and variational free energy;
- remove an adverse result;
- compute a “prediction” after revealing the observation.

Every relevant mutation must be detected. Report surviving mutations as gaps.
Never commit mutations to the source branch.

## Phase 4 — Independently rederive the mathematics

For every central mathematical path state variables, units, domains,
assumptions, boundary conditions, normalization, derivation, implementation,
independent oracle, hand calculation, sensitivity, identifiability, and failure
conditions. Audit at least prior/likelihood/posterior odds, categorical
normalization, variational free energy, surprise, residuals, policies, Hellinger
distance, first-passage distributions, survival, competing risks, censoring,
torque/work, load-speed response, stator engagement, CW bias, run probability,
lattice-J comparison, GMC, RFT, cross-study effects, model scores, tolerances,
and floating-point stability.

Test zero probabilities, extreme priors, contradictory or missing evidence,
degenerate matrices, short/long dwell times, all/no censoring, imbalanced units,
outliers, duplicated/reordered data, unit perturbations, alternative priors,
parameterizations, and inference schemes. Central results require two
independently implemented numerical routes.

## Phase 5 — Audit evidence and truth boundaries

Recalculate every local SHA-256 and verify DOI/archive identity, authors,
license, species, scale, permitted claim, transformations, and UI caption.
Explicitly inspect Mears, Singh, PDB 7E82, PDB 6YSL, Wadhwa, Ito, Antani, GMC,
RFT, generated reports, and audit manifests. Demonstrate that runtime state,
imports, missing assets, or query parameters cannot relabel reconstruction,
derived data, inference, or synthetic output as observed.

## Phase 6 — Complete the human/browser walkthrough

Keep the application visible. Test 320px, phone, tablet, laptop, desktop, high
zoom, 200% zoom where feasible, reduced motion, keyboard-only operation,
screen-reader names, and touch targets. Complete all 13 steps as a new observer.
Before revealing evidence, enter a prior prediction; then record observation,
paper calculation, interpretation, alternative explanation, and confidence.

Export JSON and CSV, print the worksheet, re-import JSON, and verify exact
round-trip integrity of records, manifest, model run, and dataset hashes. Confirm
local-only storage and inspect console/network traffic. Fail the release for
undeclared LLM, analytics, telemetry, unpinned evidence, GPU APIs, or unexpected
third parties. Confirm Canvas2D, optional browser-native speech, persistent
captions, truth badges, species boundaries, visible scale bars, non-overlapping
labels, recognizable motor layers, and a distinct inference/Markov boundary.

## Phase 7 — Deep falsification even after green gates

Form explicit null hypotheses for implementation error, data leakage, flexible
fit, non-identifiability, cross-study confounding, failure of prospective
prediction, alternative mechanisms, scale transfer, pedagogical analogy, and
parity overclaim. For each specify falsifier, data, experimental unit, controls,
sample-size rationale, stopping rule, preregistration, and analysis before
revealing results.

Run parallel isolated experiment families with deterministic seeds:

1. leave-one-motor/cell/study/condition/species/intervention-out and temporal
   forward prediction;
2. identical-split comparison against constant, empirical, Markov, semi-Markov,
   survival, flexible spline/GAM, HMM, hierarchical Bayesian, and credible
   non-UNI mechanistic baselines;
3. ablations of priors, slow state, policy, residual feedback, stator state,
   load, PMF, CheY-P proxy, lattice coupling, motor identity, and study effects;
4. parameter recovery in correctly specified and misspecified synthetic worlds;
5. posterior predictive checks of dwell, hazard, survival, tails, dispersion,
   unit variability, autocorrelation, switching asymmetry, and load dependence;
6. robustness across priors, seeds, exclusions, outliers, discretization,
   censoring, uncertainty, tolerances, bounds, units, and structure;
7. negative controls using stratified shuffles, identity shuffles, time shifts,
   irrelevant covariates, reversed time, broken boundaries, and conditions where
   the mechanism should not apply;
8. frozen prospective manifests containing code/data/split/model hashes,
   prediction, uncertainty, score, threshold, and timestamp before reveal;
9. model-disagreement mapping to find feasible, maximally discriminating future
   measurements;
10. causal intervention designs for PMF, load, stator availability, CheY-P,
    temperature, viscosity, components, and ligand environment.

Map the validity domain over species, strain, motor, cell, stator count, load,
PMF, temperature, viscosity, signaling, apparatus, timescale, scale, source,
formulation, and parameter regime. Classify regions as supported, tentative,
contradicted, unidentifiable, unobserved, or extrapolation-only. Identify where
UNI beats serious alternatives, ties simpler models, fails, or requires
study-specific tuning.

Rank next experiments by expected information gain, discriminating power,
feasibility, independence, reproducibility, cost, and self-deception risk. For
each candidate breakthrough specify hypothesis, alternatives, mathematical
change, biological meaning, data, frozen prediction, sample-size rationale,
accept/reject thresholds, replication, and what success would and would not
establish. Prestige is not an acceptance criterion.

## Modification policy

Start read-only. If a delta is found, preserve pre-fix evidence, add a failing
test, prepare the smallest patch in an isolated branch, run focused and complete
validation, and report rollback. Do not weaken gates or rewrite historical
reports. Do not push, deploy, publish, change access, or mutate external systems
without Michael's explicit authorization.

## Multi-agent verification: three buckets, never two (earned 2026-07-28)

When this audit fans out — a finding raised by one agent and handed to another to
**refute** — the results must be classified into **three** buckets, and the third
is the one this rule exists to protect:

- **CONFIRMED** — the refuter ran the reproduction and the defect survived.
- **REFUTED** — the refuter ran the reproduction and it did not hold.
- **UNVERIFIED** — the refuter produced **no verdict**: it died, errored, timed
  out, or returned null. An unexamined finding is **not** a refuted one.

The defect this prevents was committed by the audit harness itself. A fan-out
review bucketed findings as `confirmed = f.verdict.real` and
`refuted = !f.verdict.real`. A `null` verdict — what a dead agent returns —
fell into `refuted`, where it read as *checked and cleared*. Three of the run's
agents died on API errors, so **two never-examined findings were reported as
dismissed**, and one entire attack lens contributed zero findings with nothing
saying so. Reporting an unexamined finding as a cleared one is the precise
failure — a weaker claim wearing a stronger name — that this whole audit exists
to catch, reproduced in the tool doing the catching.

Binding for every multi-agent audit here:

1. Bucket into `confirmed / refuted / unverified`. A missing, null, or errored
   verdict is `unverified` — never `refuted`.
2. Report **per-lens counts including zeros**. A lens that produced nothing is a
   visible line, so a dead lens cannot hide as an absence.
3. The headline states `unverified` alongside `confirmed`. "22 confirmed, 3
   refuted" is dishonest if 2 of those 3 were never examined; the honest headline
   is "22 confirmed, 1 refuted, 2 unverified — re-run those two."
4. An `unverified` finding is re-run until it lands in `confirmed` or `refuted`,
   or is carried as an explicit open item. It is never closed by silence.

## Required paste-back report

Return one Markdown report using these exact sections:

1. `# CLAUDE / ULTRA CODE INDEPENDENT AUDIT`
2. `## Executive Verdict` — commit, tree state, software/science/release verdicts,
   strongest result, largest risk, best next experiment.
3. `## Commands Actually Run` — command, environment, exit, duration, artifact.
4. `## Gate Ledger` — `PASS | FAIL | BLOCKED | NOT RUN | EXTERNAL VALIDATION REQUIRED`.
5. `## Deltas Found` — numbered deltas with severity, domain, affected claim,
   file/line, observed/expected behavior, evidence, reproduction, root cause,
   correction, failing test, risk, conclusion impact, patch status, and diff.
6. `## Surviving Mutations`.
7. `## Mathematical Independent Checks`.
8. `## Evidence and Provenance Findings`.
9. `## Human Walkthrough Record`.
10. `## Deep Falsification Results` — hypothesis, alternatives, data/hash, unit,
    sample, split, frozen prediction, metric, uncertainty, baseline, outcome,
    interpretations, command, artifact/hash.
11. `## Failed and Adverse Results` — this section may never be omitted.
12. `## Validity-Domain Map`.
13. `## Candidate Model Breakthroughs` ranked by information gain.
14. `## Exact Next Actions for Codex` — bounded actions with prerequisites,
    files, failing test, implementation, validation, evidence, rollback, and
    acceptance criterion.
15. `## Paste-Back Capsule` — audited commit, clean/dirty state, gate counts,
    delta counts, top discoveries, top actions, artifact paths, and exact commands.

If no implementation delta exists, write exactly:

`NO IMPLEMENTATION DELTAS FOUND IN THE EXECUTED TEST DOMAIN.`

Then continue into deep falsification. “All executed gates passed” is the
strongest allowed conclusion from green gates alone.

Your governing objective is:

> Find the strongest world in which the model survives serious alternatives,
> map precisely where it fails, and let risky prospective evidence—not desire—
> decide whether that world can expand.

---
