# Claude three-phase parity completion plan

Status: **FROZEN COORDINATOR HANDOFF**

Plan version: `1.0.0`

Plan base: `cc9ba769f580367d75441325ca967aed7bd738c8`

Execution agent: **Claude, active builder and recorder**

Review agent: **Codex, independent reviewer and phase gatekeeper**

## 1. Mission and truth boundary

Complete the remaining software, model-comparison, robustness, and evidence-
packaging work needed to decide whether UNI-FLAGELLUM has reached a declared
level of parity with the bacterial flagellar motor. Produce evidence that
another investigator can inspect and reproduce from a clean clone.

The work is not allowed to assume the desired answer. Its purpose is to detect
the world in which a bounded parity claim is true and to distinguish it from
the worlds in which the claim is false, unresolved, or blocked by missing
external evidence.

Nature is not a finite software oracle. Therefore this plan does not permit an
unqualified claim of “full and exact parity with nature.” The strongest
allowable positive claim is:

> Parity at the declared observational and intervention resolution, over the
> frozen validity domain, within the frozen tolerances, supported by independent
> evidence and reproducible from the recorded artifacts.

The digital motor also may not be called literal “digital life.” A flagellar-
motor model does not by itself demonstrate metabolism, autonomous maintenance,
reproduction, or evolution. Those are outside this repository’s present claim
boundary.

## 2. Current evidence anchor

Claude must begin from the following witnessed state and preserve it:

- `main` remains `9c3a644`.
- Phase-C prediction commit:
  `b95e714d6f4f07b02eb369eb43fed1d1567b1acd`.
- Phase-C result commit:
  `cc9ba769f580367d75441325ca967aed7bd738c8`.
- The prediction commit is the direct parent of the result commit.
- The blind battery produced 10 `SURVIVED`, 0 `DETECTED_SEMANTIC`,
  0 `DETECTED_BY_HASH_ONLY`, 0 `NOT_RUN`, and 0 `INCONCLUSIVE`.
- The ten survivors are adverse evidence about semantic coverage. They are not
  evidence for biological parity.
- B3’s prediction-only commit is `e5b4969`; its prediction record is `PENDING`;
  its result does not exist.
- Existing cross-study verdict: full biological parity is false, with required
  gates failed, not established, or externally blocked.

The original Phase-C result, logs, frozen protocol, frozen predictions, and
runner are immutable historical evidence. Remediation creates new artifacts;
it never overwrites or relabels the adverse result.

## 3. Operational parity ladder

Every release claim must name one level from this ladder. A higher level
requires every lower level to pass.

| Level | Name | Required evidence |
|---|---|---|
| P0 | Computational integrity | Clean-build determinism, source provenance, artifact identity, unit checks, and non-vacuous independent verification. |
| P1 | Equation/implementation parity | The implementation satisfies the declared equations and invariants under hand-calculable positive and negative controls. |
| P2 | Observational parity | Source-pinned recorded observations are reproduced within frozen uncertainty and experimental-unit rules. |
| P3 | Held-out predictive parity | Frozen models predict untouched motors/cells/conditions better than serious baselines under proper scoring rules. |
| P4 | Transfer parity | Parameters fitted in one compatible study/lab predict commensurate observations from another without refitting. |
| P5 | Interventional parity | Frozen models correctly predict outcomes of manipulations chosen to make serious alternatives disagree. |
| P6 | Structural/mechanistic parity | Latent states and geometry have independent molecular measurements; phenomenological states are not promoted by fit alone. |
| P7 | Independent replication | An independent investigator/lab executes the frozen protocol and reproduces the result with raw data and calibration. |
| P8 | Declared full-parity verdict | P0-P7 all pass over the same declared validity domain, with no required `FAIL`, `NOT_ESTABLISHED`, `BLOCKED`, or `NOT_RUN`. |

`P8` is conjunctive. Scores may not be averaged to hide a missing domain. A
positive result outside the frozen domain is `EXTRAPOLATION_ONLY`, not parity.

## 4. Status vocabulary

Every cell and every parity dimension must use exactly one status:

- `PASS`
- `FAIL`
- `CONTRADICTED`
- `NOT_ESTABLISHED`
- `BLOCKED_EXTERNAL`
- `NOT_RUN`
- `INVALID_PROVENANCE`

Only `PASS` satisfies a required conjunct. Missing data, unavailable hardware,
failed regeneration, absent credentials, or an inaccessible external archive
can never become `PASS` by simulation or prose.

## 5. Division of labor

### Claude

Claude is the active builder for all three phases. Claude observes, freezes
predictions, implements, executes, preserves adverse outcomes, and prepares the
phase handoff. Claude does not self-approve a phase.

### Codex

Codex reviews only at the end of each phase. Codex independently checks commit
ancestry, raw artifacts, calculations, failure behavior, claim strength, and
reproducibility. Codex returns one verdict:

- `ACCEPT`
- `ACCEPT_WITH_LIMITATIONS`
- `REJECT_BLOCKING`

Codex should identify only defects capable of changing the scientific result,
provenance, reproducibility, or release claim. Stylistic improvements do not
reopen a phase.

### Correction budget

Each phase permits one bounded correction package after Codex review. Claude
must verify each reported defect before editing, preserve the original result,
and add an append-only correction. If a blocking defect remains after that
package, the phase remains rejected and the unresolved condition is recorded.
Do not enter an indefinite review volley.

## 6. Rules applying to every phase

1. Follow `OBSERVE -> BOUND -> PREDICT -> ACT -> VERIFY -> FALSIFY -> UPDATE -> RECORD`.
2. Read `CLAUDE.md`, relevant frozen protocols, evidence manifests, and public
   scientific contracts before acting.
3. Treat unknown working-tree changes as user-owned. Never reset or overwrite
   them.
4. Work on a dedicated phase branch based on the last Codex-accepted commit.
5. A phase prediction/protocol enters a prediction-only commit before the code
   or result it governs. Push that commit before execution.
6. The prediction commit, implementation commit, and result commit are distinct.
7. Never amend or rewrite commits used as prospectivity evidence.
8. Destructive or mutation work occurs only in one disposable clean clone per
   experimental cell. The primary checkout is never mutated.
9. Use source-pinned raw observations. Never relabel modeled, reconstructed, or
   inferred values as `OBSERVED`.
10. Split by the biological experimental unit—motor, cell, culture, or study—
    never by events or frames when doing so creates leakage or pseudoreplication.
11. Preserve species, strain, load, apparatus, units, censoring, calibration,
    and observation-operator boundaries.
12. Every stochastic operation has a frozen seed and records its resampling unit.
13. Every fit declares bounds, starts, convergence criteria, failure behavior,
    and telemetry before results are revealed.
14. Report all attempted, feasible, finite, converged, and selected fits with
    non-overlapping counter semantics.
15. A finite search supports “no better solution found over the declared
    domain,” never “proved global optimum.”
16. Independent oracles may not import the implementation under test or compare
    only against artifacts emitted by that same implementation.
17. A hash gate establishes identity, not semantic correctness. Semantic gates
    require independent mathematical or biological invariants.
18. Null, adverse, failed, and not-run results remain visible with the same
    prominence as favorable results.
19. No threshold, cohort, model, scoring rule, or exclusion may be changed after
    seeing the governed result.
20. Do not execute external publishing, laboratory, instrument, fabrication,
    credentialed, or registration actions without explicit user authorization.

## 7. Required validation baseline

At the beginning and end of every phase, record versions and run the applicable
clean-clone checks:

```text
git status --short --branch
git log -3 --oneline
git remote -v
node --version
npm --version
python --version
npm ci
npm test
npm run lint
npx tsc --noEmit
npm run experiment:verify
npm run science:verify
npm run cross-study:verify
npm run cross-study:verify-raw
npm audit --omit=dev --audit-level=moderate
npm audit
python audits/phase-b/b3-preflight.py
```

An external raw archive that is absent is reported as `BLOCKED_EXTERNAL` or
`NOT_RUN`; its historical verification ledger may be checked but may not be
presented as a fresh deep verification.

---

# PHASE 1 — Semantic measurement-system closure

## 1.1 Objective

Convert the ten Phase-C survivors into durable semantic regression protection
without claiming that target-specific remediation measures general future
robustness.

The ten named properties are:

1. seconds-scale density Jacobian;
2. survival-conditioned posterior;
3. sample-variance/Bessel correction;
4. hidden-world observation boundary;
5. physical stator-count range;
6. load-dependent stator recruitment;
7. first-passage weight normalization;
8. stator-multiplicity off hazard;
9. exponential-mixture second moment;
10. periodic 13-site lattice topology.

## 1.2 Required artifacts

Create new, versioned paths. Suggested names:

- `audits/phase-d/d1-semantic-remediation-protocol.v1.json`
- `audits/phase-d/d1-semantic-remediation-predictions.v1.json`
- `experiments/predictions/d1-semantic-remediation.prediction.json`
- `audits/phase-d/d1-semantic-remediation-result.v1.json`
- `audits/phase-d/d1-semantic-remediation-evidence.v1/`
- `audits/phase-d/package-manifest.json`
- focused semantic tests grouped by independent scientific invariant;
- an append-only documentation update describing both the original 0/10
  detection result and the later target-specific remediation.

## 1.3 Commit discipline

1. `D1 PREDICTION-ONLY`: freeze every proposed invariant, fixture, expected
   failure, falsifier, test command, and mutation-replay classification.
2. `D1 IMPLEMENTATION`: add the semantic tests/gates. Do not run or commit the
   governed replay result in this commit.
3. `D1 RESULT`: run the frozen replay in isolated clones, preserve raw logs and
   classifications, update prospectivity status, and commit the result.

## 1.4 Gate-design requirements

Each property needs:

- a hand-calculable positive fixture;
- a hand-calculable negative fixture;
- a failure diagnostic naming the biological/statistical property;
- a proof that the check is not satisfied solely by a source hash, run ID,
  report byte identity, or snapshot;
- a proof that the oracle does not call the production function it checks;
- a deletion/adverse-record preservation assertion where applicable;
- at least one structurally different implementation of the same corruption,
  not only the exact text replacement from the original battery.

Minimum invariant examples:

- a seconds-scale density numerically integrates to one after change of
  variables;
- a survival-conditioned slow-state posterior uses survivor mass, not event
  density;
- sample variance reproduces a small literal `n-1` fixture;
- `Observation` excludes hidden world truth and the agent cannot receive the
  world object;
- live stator occupancy is integral and bounded `0..11`;
- load perturbation changes the declared recruitment target in the specified
  direction;
- first-passage weights sum to one and `S(0)=1`;
- the competing-risk off contribution contains the declared `N` multiplicity
  and conserves total event mass;
- the exponential-mixture second moment contains its factor of two;
- a 13-site periodic ring includes the wraparound interaction and differs from
  an open chain on a literal discriminating configuration.

## 1.5 Acceptance criteria

- All ten frozen corruptions reach the intended behavior.
- All ten are `DETECTED_SEMANTIC` by a matching frozen diagnostic.
- None is classified only by a hash or byte identity failure.
- At least one alternate-form corruption per property is also detected.
- Removing the historical 0/10 adverse result fails loudly.
- The original Phase-C evidence remains byte-identical.
- Clean-tree focused tests and the complete required validation baseline pass,
  except explicitly external checks.
- Documentation says “target coverage established,” not “future robustness
  established.”

## 1.6 Claude handoff to Codex

Report commits, branch, prediction ancestry, files changed, test counts, a
20-row table covering exact and alternate mutations, semantic diagnostics,
oracle independence, evidence hashes, adverse-result preservation, clean-clone
commands, and every limitation.

## 1.7 Codex review gate

Codex independently:

- verifies the three-commit ordering and immutable Phase-C evidence;
- checks each oracle against a literal calculation;
- attempts deletion and semantic-laundering attacks;
- applies a small set of unannounced structural variants to detect hard-coded
  exact-patch matching;
- confirms that production behavior was not altered merely to satisfy tests;
- reruns the clean-clone validation.

Phase 2 begins only after `ACCEPT` or an explicit
`ACCEPT_WITH_LIMITATIONS` whose limitations cannot affect B3/B4.

---

# PHASE 2 — Frozen model competition and robustness

## 2.1 Objective

Execute the already-frozen B3 competition without retuning, then determine
which rankings and scientific conclusions survive B4 identifiability and
robustness analysis.

Predictive superiority and mechanistic truth remain separate claims.

## 2.2 B3 immutable inputs

The following predate execution and may not be rewritten:

- `audits/phase-b/b3-competition-protocol.v1.json`
- `audits/phase-b/b3-competition-protocol-addendum-v2.json`
- `audits/phase-b/b3-integration-addendum-v3.json`
- `audits/phase-b/b3-predictions.v1.json`
- `experiments/predictions/b3-model-competition.prediction.json`
- component specifications under `audits/phase-b/b3-specs/`
- prediction commit `e5b4969`.

Before any B3 fit, verify `b3-preflight.py` passes 46/46, the result is absent,
and the prediction record measures `PENDING`.

## 2.3 B3 execution requirements

1. Commit the production-independent B3 runner and independent verification
   code before producing the result.
2. Execute all 36 frozen cells: 9 models × 2 scoring rules × 2 cohorts,
   including explicit M3 reference rows.
3. Preserve model bounds, starts, selection rules, seeds, censoring behavior,
   cohort definitions, and failure rules exactly as frozen.
4. Preserve the historical lognormal advantage whether confirmed or refuted.
5. Emit the required canonical artifact:
   `audits/phase-b/b3-model-competition-result.json`.
6. Preserve lossless per-cell logs, optimizer telemetry, fitted parameters,
   scores, motor-cluster bootstrap distributions/intervals, leaderboard ties,
   and prediction confirmations/refutations.
7. Change the B3 record from `PENDING` to `PROSPECTIVE` only in the result
   commit after strict ancestry is real.
8. Independently recompute selected likelihoods, CRPS values, leaderboard
   ordering, and intervals without importing the implementation under test.

No failed model may disappear from the denominator. `UNIDENTIFIED`, infeasible,
nonfinite, nonconverged, and boundary-selected fits remain visible.

## 2.4 B4 prediction freeze

After B3 is committed—but before any B4 cell is executed—commit a new B4
protocol, per-cell predictions, falsifiers, and prediction record. B4 may use
the observed B3 leaderboard to choose declared sensitivity targets; it may not
use unseen B4 results to choose thresholds.

B4 must cover:

- correctly specified synthetic parameter recovery;
- misspecified synthetic worlds;
- prior sensitivity where priors exist;
- multiple frozen bootstrap seeds;
- censoring assumptions and explicit invalid-treatment negative controls;
- outlier rules and the `analysisStartIndex=3500` boundary;
- the actual frozen eligibility derivation, plus any protocol-deviating
  unfiltered cohort labeled as sensitivity only;
- leave-one-motor-out, leave-one-study-out, and leave-one-condition-out checks
  where the data support them;
- propagation of the `0.02 s` measurement interval uncertainty;
- practical and structural identifiability;
- ranking and interval-crossing stability.

Do not repeat the retracted claim that state 0 lacks an authorizing exclusion.
State 0 has 18 uncensored holdout events and fails the frozen threshold of 20.
The remaining issue is only the historical scope wording, not an unauthorized
cohort exclusion.

## 2.5 B4 artifacts

Suggested versioned deliverables:

- `audits/phase-b/b4-identifiability-robustness-protocol.v1.json`
- `audits/phase-b/b4-identifiability-robustness-predictions.v1.json`
- `experiments/predictions/b4-identifiability-robustness.prediction.json`
- `audits/phase-b/b4-identifiability-robustness-result.v1.json`
- `audits/phase-b/b4-evidence.v1/`
- an independent oracle and manifest.

## 2.6 Phase-2 acceptance criteria

- B3 prediction ancestry is strict and machine-verified.
- All 36 cells are present and accounting is internally coherent.
- Each model is scored on identical declared observations for a given
  cohort/rule.
- NLPD and CRPS are implemented as frozen proper scoring rules.
- Bootstrap resamples motors, not events.
- Independent calculations reproduce the decisive rankings and interval signs
  within frozen tolerances.
- B4 predictions strictly predate B4 results.
- Every required B4 sensitivity cell is present or explicitly `NOT_RUN` with a
  reason; it is never silently omitted.
- The result names which conclusions are stable, unstable, unidentified, or
  dependent on specification.
- No winning predictive model is promoted to molecular mechanism without
  independent mechanistic evidence.
- Full clean-clone validation passes, except explicitly external checks.

## 2.7 Claude handoff to Codex

Report B3 and B4 commit sequences, ancestry, all model/cell accounting,
prediction results, leaderboards, uncertainty, optimizer telemetry,
identifiability results, every conclusion that moved, independent-oracle
agreement, evidence hashes, commands, runtime, and adverse findings.

## 2.8 Codex review gate

Codex independently:

- verifies all frozen B3 inputs are byte-identical;
- recomputes a stratified sample of per-event scores and motor bootstraps;
- checks that the two scoring rules use identical held-out observations;
- verifies no failed starts/models/cells were dropped;
- confirms all B4 choices were frozen before their outcomes;
- probes leakage, pseudoreplication, label orientation, cohort semantics,
  uncertainty, and non-identifiability;
- reruns decisive cells from a clean clone;
- audits the claim language against the actual intervals.

Phase 3 begins only after `ACCEPT` or explicit
`ACCEPT_WITH_LIMITATIONS` with those limitations carried into the parity ledger.

---

# PHASE 3 — Prospective parity trial and public evidence package

## 3.1 Objective

Create the falsifiable contract and reproducible public evidence needed to
decide the parity ladder. Execute every software- and existing-data-based cell
that can honestly run. Preserve all external requirements as external; never
replace a missing experiment with synthetic evidence.

## 3.2 Prediction-only contract

Before any new parity evaluation, commit:

- a machine-readable parity claim matrix for P0-P8;
- the exact validity domain: species, strain, motor/cell population, load, PMF,
  stator state, temperature, viscosity, CheY-P condition, apparatus, time scale,
  study, and observation operator;
- required evidence paths, independent units, thresholds, uncertainty rules,
  and failure rules for every cell;
- a B5 prospective experiment chosen from the maximum model-disagreement region
  revealed by accepted B3/B4 results;
- explicit predictions from the leading UNI and non-UNI alternatives;
- a power/sample-size rationale and stopping rule;
- calibration, exclusions, missing-data, censoring, and analysis plans;
- an external timestamp/registration requirement;
- an independent replication and raw-data release plan.

Suggested artifacts:

- `audits/phase-f/f1-parity-validation-protocol.v1.json`
- `experiments/parity-claim-matrix.v1.json`
- `audits/phase-b/b5-prospective-contract.v1.json`
- `experiments/predictions/f1-parity-validation.prediction.json`

Git ancestry is necessary repository evidence, but the future wet-lab protocol
must also receive an immutable timestamp or registration receipt outside this
repository before observations are revealed. Claude prepares the artifact but
does not publish or register it without explicit user authorization.

## 3.3 Existing-evidence execution

Execute and record all cells supportable by source-pinned existing evidence:

- source and provenance integrity;
- equation and semantic invariant coverage;
- deterministic report regeneration;
- held-out motor/cell prediction;
- serious-model competition and robustness;
- commensurate cross-study parameter transfer if compatible datasets and units
  actually exist;
- structural-state mappings and unresolved molecular identities;
- Active-Inference discrimination only if a real intervention distinguishes it
  from matched kinetic/control alternatives;
- clean-clone and independent-language reproduction.

If two studies are not commensurate enough for parameter transfer, record
`NOT_ESTABLISHED`; do not manufacture transfer through unit conversion,
rebinning, or refitting after seeing the target.

## 3.4 External evidence cells

The following can pass only with new real-world evidence:

- calibrated live prospective motor/instrument run;
- independent wet-lab replication;
- molecular identification of phenomenological latent states;
- intervention discriminating UNI/Active Inference from serious alternatives;
- fabrication, metrology, calibration, and measured physical-model validation.

Until those artifacts exist with valid provenance, these cells remain
`BLOCKED_EXTERNAL` or `NOT_ESTABLISHED`. Completing this plan with such statuses
is a scientifically successful negative verdict, not an incomplete software
task.

## 3.5 Reproducible evidence bundle

Produce:

- `experiments/results/parity-verdict.v1.json`
- `experiments/results/parity-evidence-manifest.v1.json`
- `audits/phase-f/f1-parity-validation-result.v1.json`
- `audits/phase-f/f1-evidence.v1/`
- `docs/PARITY-VERDICT.md`
- one CPU-only, noninteractive reproduction entry point;
- an independent checker in a different implementation path/language;
- exact dependency, runtime, source, protocol, prediction, result, and raw-data
  identities;
- all commands, exit codes, stdout/stderr hashes, run durations, and machine
  limitations;
- at least two fresh clean-clone reproductions from the same frozen commit;
- a comparison proving deterministic artifacts are byte-identical and numerical
  artifacts agree within predeclared tolerances;
- a public-reader table linking every claim to its observation, unit, source,
  code, test, result, uncertainty, limitation, and falsifier.

Same-machine clean clones establish rebuild repeatability, not independent-lab
replication. The ledger must state that distinction.

## 3.6 Verdict algorithm

The verdict must be computed, not editorially selected:

```text
P0 = PASS only if all required P0 cells PASS
Pn = PASS only if P0..P(n-1) PASS and all required Pn cells PASS
FULL_PARITY = PASS only if P0..P7 all PASS over one declared domain
otherwise FULL_PARITY = false
```

Any required `FAIL`, `CONTRADICTED`, `NOT_ESTABLISHED`, `BLOCKED_EXTERNAL`,
`NOT_RUN`, or `INVALID_PROVENANCE` forces `FULL_PARITY=false`. The report must
name the first unsatisfied level and every remaining blocker.

A true result permits only the bounded P8 wording in Section 1. A false result
must say exactly which lower level is supported and what observation could
change the verdict.

## 3.7 Phase-3 acceptance criteria

- The parity matrix and B5 contract predate every governed result.
- No observed value comes from simulation or reconstruction.
- Every required cell has exactly one allowed status and a resolvable evidence
  path or explicit external blocker.
- The verdict is reproduced independently from the machine-readable matrix.
- Two clean clones reproduce the committed deterministic artifacts.
- Public documentation and machine-readable verdict agree exactly.
- The package retains adverse B1, B2, B3, B4, Phase-C, and Phase-D evidence.
- No missing external domain is averaged away.
- No “digital life,” “exact replica,” universal, or molecular-identity claim
  exceeds the measured evidence.

## 3.8 Claude final handoff to Codex

Report:

1. complete commit graph and branch;
2. strict prediction/result ancestry;
3. full P0-P8 matrix;
4. computed parity verdict and first unsatisfied level;
5. every external blocker;
6. clean-clone reproduction results and artifact digests;
7. independent-checker agreement;
8. source/raw-data identities;
9. model, scoring, uncertainty, and experimental-unit definitions;
10. all adverse and contradicted results;
11. exact public reproduction command;
12. release wording that the evidence permits and wording it forbids.

## 3.9 Codex final validation

Codex independently:

- starts from a genuinely fresh clone at the claimed final commit;
- verifies all manifests and prediction ancestry;
- reruns the public reproduction entry point and independent checker;
- recalculates the conjunctive verdict without importing the verdict writer;
- samples raw observations back to their pinned sources;
- checks biological units, species, experimental units, leakage, censoring,
  observation boundaries, intervention ordering, and structural labels;
- confirms that external blockers were not converted into passes;
- compares the public narrative to the machine-readable result;
- issues the final `ACCEPT`, `ACCEPT_WITH_LIMITATIONS`, or `REJECT_BLOCKING`.

Codex acceptance validates the evidence package and the bounded verdict. It does
not make Codex an independent wet-lab replication.

## 8. Anti-spin termination rules

1. Each phase has one named objective, one prediction chain, one result package,
   one Codex review, and at most one correction package.
2. No new audit phase is invented to avoid an adverse result.
3. A falsified prediction closes as falsified; it is not rewritten.
4. A blocked external gate closes as blocked until new external state changes.
5. New scientific work is admitted only if it can change a parity-ladder status
   or distinguish serious models.
6. Test-count growth, code volume, and artifact count are not measures of
   scientific progress.
7. At each handoff Claude states what changed in the parity ladder. If no status
   could change, the work was maintenance and may not delay the next phase.
8. After Phase 3 and final Codex validation, the program closes with the measured
   verdict. Further work requires new data, a new intervention, or a new model
   that makes a prospectively distinguishable prediction.

## 9. First instruction to Claude

Begin Phase 1 only. Do not execute B3 or prepare Phase 3 yet.

Create a branch from the commit containing this plan, verify the Current
evidence anchor, freeze the D1 prediction-only commit, implement and execute D1
under the required three-commit discipline, push the phase branch, and return
the Section 1.6 handoff. Then stop for Codex review.
