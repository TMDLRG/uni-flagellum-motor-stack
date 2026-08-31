# UNI-FLAGELLUM Agent Operating Contract

> ## ⟢ RESUME POINT — read this before anything else (marked 2026-07-28)
>
> **We are in PHASE 9 — RETURN TO RESONANCE, mid Stage 4.** This block is **navigation and
> measured state only. It amends no law.** Every law below it stands unchanged.
>
> **If you have no context, read
> `UNI-FLAGELLUM/docs/control-plane/AGENT-CALIBRATION-PROMPT.md` first.** It is
> self-contained and carries every trap that has already caught someone.
>
> - **The plan is not a document.** `UNI.Minecraft/evidence/remediation/phase9_plan.json`
>   is the single source of truth. **UNI TRACK `http://127.0.0.1:8102/` renders it live and
>   Gaia projects it verbatim.** When a step completes, edit that file; the surfaces follow.
>   `viewer/verify_plan_consistency.cjs` now holds it to its own vocabulary — it exists because
>   the plan carried two different next acts at once.
> - **Register:** `UNI-FLAGELLUM/docs/control-plane/phases/PHASE-9-REMEDIATION.md`
> - **Resume detail:** `UNI-FLAGELLUM/docs/control-plane/RESUME.md`
>
> **THE STATE BELOW IS GENERATED, NOT WRITTEN.** Every number between a `BEGIN GENERATED` and its
> `END GENERATED` is produced by `node viewer/generate_state_blocks.cjs` from the artifact it
> describes. **Do not edit inside a block; edit the artifact and regenerate.** This banner used to
> carry these numbers by hand and was measurably wrong in six places on 2026-07-29 — 25 gates in one
> paragraph and 23 in another (both wrong, 28), a ledger of 31 (32), "six" lab gates (seven), and a
> next act that had shipped six hours earlier.
>
> <!-- BEGIN GENERATED uni.state.next_act prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **NEXT ACT: RESUME-THE-LIVE-FRONTS — AGENTS**
>
> Two live fronts, both agent work, both measured live since 2026-08-19: (1) the whiteboard defect programme -- docs/whiteboard/DEFECTS-AND-REPAIRS.md, every repair proven on the real engine before it ships; (2) the public University assembly -- labs, course, falsification wall and contribution surfaces served from the documentation estate, every page pinned to the commit it was read from. The checkpoint this key used to name was ruled out by the operator; see was.
>
> Declared at `docs/whiteboard/DEFECTS-AND-REPAIRS.md and the UNI.Public estate (the University routes)`. Blocked on: nothing -- both fronts accept agent work today; operator dependencies inside them (per-repair co-signs) are queued as they arise, and none gates the next step
>
> Retired: **L6** (Stage 4 step 4.6 -- build L6, THE GAUNTLET THEN THE CO-SIGN, shipped `6234f3d`); **CHECKPOINT-E** (WITHDRAWN by operator ruling 2026-08-10: the two-image shot surface at the lab viewer was ruled a fatal hallucination -- never resurface it.).
> <!-- END GENERATED uni.state.next_act -->
>
> <!-- BEGIN GENERATED uni.state.plan_tally prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Plan:** 7 stages · 43 steps (31 DONE · 1 BLOCKED · 8 PLANNED · 3 OPERATOR) · 7 builds under step 4.6, 7 DONE.
> <!-- END GENERATED uni.state.plan_tally -->
>
> <!-- BEGIN GENERATED uni.state.gates prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Gates:** **36 registered**, of which **33 `ci:true`** and 3 `ci:false` (`colony`, `hud`, `overlays` — listed, never run, never a fabricated pass). **7 lab gates** (`lab-l0`, `lab-l1`, `lab-l2-shot`, `lab-l3`, `lab-l4`, `lab-l5`, `lab-l6`).
>
> Both numbers are stated because both were written before without saying which was which:
> one banner paragraph said 25 and another said 23, and a single file said 23 at one line and
> 25 at another. Neither was the registered count.
> <!-- END GENERATED uni.state.gates -->
>
> <!-- BEGIN GENERATED uni.state.gate_ledger prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Gate ledger** `evidence/gates.ndjson` — `ca8fd61ab5380994...`, **212 rows / 112 unique names**. Last row per name: 94 PASS · 5 PARTIAL · 12 PENDING · 1 FAIL.
>
> The per-name tally is stated as such because the per-ROW tally is a different set of numbers,
> and a count whose derivation is unstated is how a backlog and the history of a backlog came
> to be reported as one word.
> <!-- END GENERATED uni.state.gate_ledger -->
>
> <!-- BEGIN GENERATED uni.state.registry_ledger_gap prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Registry vs. the canonical ledger:** of **36 registered gates, 1 appear in `evidence/gates.ndjson`** and **35 do not** (0 of those carry a glob `gate_row`, which no kebab-case row can ever bear). `gate_row.schema.json` says every gate the project claims MUST be represented there.
>
> **The intersection is NOT empty, and four governing documents said it was.** They declared "EVERY registered gate has ZERO rows" and "the intersection is empty by `id` *and* by `gate_row`" for two weeks after a row landed for one of them on 2026-07-17 — inside the paragraph that says these numbers are generated. It was hand-written. It is not any more.
>
> Authoring the missing rows is **S4 — the operator's**, but the blocker is not his signature: `desk.preRegistration()` reports most of them blocked on an empty `receipt_path` the schema requires, which is a pre-registration document an agent owes him. He could not append them today even if he wanted to.
> <!-- END GENERATED uni.state.registry_ledger_gap -->
>
> <!-- BEGIN GENERATED uni.state.control_plane prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Control-plane ledger:** 32 entries, tip `b90b74980f47b93a...` at seq 32. Anchor declares length 32, head `b90b74980f47b93a...` — **they agree.**
> <!-- END GENERATED uni.state.control_plane -->
>
> <!-- BEGIN GENERATED uni.state.how_to_measure prefix="> " — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
> **Three things are deliberately NOT stated here, because no committed file can hold them
> honestly.** They are facts about a *run* or about *now*, not about the tree:
>
> | question | the command |
> | --- | --- |
> | Are the trees clean? | `git -C <tree> status -sb` |
> | Does the Elixir suite pass? | `mix test` |
> | Do the gates pass? | `node viewer/gate_runner.cjs` |
>
> This banner used to answer all three. The gate-runner answer was measured at 06:01:09 on
> 2026-07-29 and was false by 06:04:06 — a half-life of 176 seconds — and it was committed
> reading as present tense. Run the commands.
> <!-- END GENERATED uni.state.how_to_measure -->
>
> **Four things that must not be softened:**
> 1. **The off-box witness is COMPROMISED** — node2 accepts the writer's key,
>    `independent_custodians: 0`. The anchor stands on git alone: tamper-evident, **not**
>    unforgeable. **Removing that key is S1 — the one repair an agent must not perform.**
> 2. **Phase 7's witness clause still FAILS.** Its *other* failing clause — "two fixtures
>    distinguishable with no text read" — is **closed**: the renderer exists (`viewer/lab/`, and the
>    lab-gate count is in the generated block above, not restated here), and
>    `verify_shot.cjs --mutate` proves it bites in greyscale. Measured 2026-07-29: both images are
>    real and differ — `/api/lab/shot?swap=0` is 3371 bytes and `?swap=1` is 3375, both valid PNG
>    with different sha256, embedded side by side at `viewer/lab/l6.html:52-53`.
> <!-- @claim archived: the sentence below QUOTES the false declaration it replaces. It said the
>      registry/ledger intersection was EMPTY. It was 1 of 32 from 2026-07-17 and stayed wrong for two
>      weeks. The quote IS the evidence that this list carried a false entry; do not delete it. -->
> 3. **Most registered gates have no row in the canonical ledger — the count is in the generated block
>    above and is NOT restated here.** This entry used to read *"EVERY registered gate has ZERO rows...
>    the intersection is empty by `id` *and* by `gate_row`"* — **false since 2026-07-17**, and it was
>    hand-written inside the banner that says its numbers are generated. `gate_row.schema.json` says
>    every gate the project claims MUST be represented there. Appending is **S4 — the operator's** — but
>    the blocker is NOT his signature: most rows are blocked on an empty `receipt_path` the schema
>    requires, which is a pre-registration document an agent owes him. The desk at `/lab/l5` prints
>    each exact line.
> 4. **The go-live guard is real and refuses all seven paths, and it is `presence_evident`, NOT
>    unforgeable.** F31 has code, a gate and an operator's prover. It binds *this codebase's*
>    paths — **the OBS WebSocket on `:4455` still has no authentication (S2, his) — and it is bound to `::`,
>    ALL INTERFACES, reachable from the LAN *and* the tailnet. Every prior line here said
>    `127.0.0.1:4455`, which was FALSE and understated the exposure (`LIMITATIONS.md`
>    `f31.obs-unauthenticated`, measured 2026-07-29).**
>
> **The road to air runs THROUGH the science:** `colony_on_program` is blocked on
> `forage-pureworld-graduation`, whose runner `runs/pureworld_qa_gate.exs` **still raises
> `@scaffold`**. And **no verdict has yet been authored about a real scientific claim.**
>
> <!-- @claim archived: this paragraph QUOTES the stale declarations it is correcting; the quotes are the evidence and must not be edited away -->
> **Corrected 2026-07-28 (this banner was false in seven places):** it said 42 steps (43), 964
> tests, *"the renderer was never built"*, *"nothing detects running-but-not-the-committed-bytes"*
> (step 1.1 built boot identity on all four bodies), *"the ledger stopped recording at Phase 5"*,
> *"F31 has no code and no test"*, and **"NEXT ACT: Stage 1 step 1.1"** — four stages stale.
>
> **Corrected AGAIN 2026-07-29, and this time the fix is structural.** Within six hours of that
> correction the banner was stale again, in six places: it said 25 registered gates in one paragraph
> and 23 in another (28), a ledger of 31 (32), *"six"* lab gates (seven), `gates.ndjson` unchanged at
> `964ea25c…` (it moved to `1daac912…` when a probe row landed), and **a NEXT ACT of "build L6" six
> hours after L6 shipped at `6234f3d`** — while the plan itself said the next act was Checkpoint E.
> `AGENT-CALIBRATION-PROMPT.md` tells every fresh agent to obey the next act *before verifying
> anything*, so a fresh agent would have rebuilt a finished build. **That is why the numbers above
> are now generated and no longer written.** A hand-written number is a claim with a half-life; these
> had a half-life of six hours, and one of them — a gate-runner tally — had a half-life of 176
> seconds.
>
> <!-- @claim archived: this paragraph QUOTES the stale `NEXT ACT:` declaration it is correcting. The quote IS the evidence that the untracked copy misdirected a fresh agent, and deleting it to satisfy the gate would destroy the only record of the defect. -->
> **Corrected A THIRD TIME 2026-07-30, and the third correction was of the second one's own claim.**
> The paragraph above used to end by saying all three copies of this block were **byte-identical**,
> md5 `003fc92d…`. **They were not, and the structural fix itself is what made them differ.** The
> generated blocks were installed in the two TRACKED copies and not in the third, so for a day the
> count was **6 blocks, 6 blocks and ZERO** — and that third copy, `Documents/UNI-Flagellum/CLAUDE.md`,
> the file an agent starting there reads first, still declared **"NEXT ACT: Stage 4 step 4.6 — build
> L6"** with L6 finished and receipted. The precise failure was in `UNI.Minecraft`:
> `viewer/state_blocks.cjs` defined an `OUT_OF_TREE` root and exported it, but made it the root of
> **no declared document** — so `verify_claims.cjs`, the gate whose entire reason for existing is a
> stale `NEXT ACT:` declaration, could not see the one document that still carried one. **That blind
> spot also means the 07-29 audit's own count was an undercount:** it reported *five* documents
> carrying the stale declaration, and the true number was six — the sixth being the copy no
> instrument could reach. All three copies now carry all six blocks and drift under the same gate.
> The untracked copy is **still tracked
> by no git repository**, so no diff and no CI run can ever reach it; only the gate can, and only when
> someone runs it. That remains a standing hazard, not a fixed one.


This repository is a living science instrument. Work as one coherent organism,
but never erase the boundaries that make the organism scientifically honest.
The world process, recorded observation, reconstruction, reduced model, UNI
analogue, inference state, human interpretation, and release claim are distinct.

## Mission

Build the strongest reproducible account of bacterial flagellar-motor behavior
that survives serious alternatives. Map where the model works, where it fails,
and which observation would most reduce uncertainty. Passing software tests is
necessary but is not proof of biological parity, general intelligence, human
parity, or scientific significance.

The released product must remain CPU-only and must contain no LLM inference,
GPU computation, WebGL, WebGPU, Three.js, analytics, accounts, or hidden network
calls. Development agents may use their own tools, but those tools may not
become undeclared runtime dependencies.

## Resonance and flow

Resonance is a testable consistency condition across:

1. source observation and provenance;
2. declared variables, units, equations, and assumptions;
3. implementation and deterministic runtime state;
4. prospective prediction and later observation;
5. UI truth badge and species label;
6. gate criterion, result, uncertainty, and limitation;
7. report, notebook export, reproduction command, and artifact hash.

If these disagree, preserve the disagreement and reduce it through evidence.
Do not create apparent harmony by weakening tests, retuning a holdout, changing
labels, suppressing adverse results, or rewriting history.

Follow this Active Inference execution flow for every bounded change:

`OBSERVE -> BOUND -> PREDICT -> ACT -> VERIFY -> FALSIFY -> UPDATE -> RECORD`

- **Observe:** inspect repository state, instructions, evidence, and current gates.
- **Bound:** name the claim, system boundary, experimental unit, species, scale,
  dependencies, authorization, and rollback.
- **Predict:** write the expected result and falsifier before changing code or
  revealing held-out evidence.
- **Act:** make the smallest reversible change that can test the prediction.
- **Verify:** run the narrow test, then the relevant full gates.
- **Falsify:** test serious alternatives, negative controls, mutations, leakage,
  misspecification, and edge cases.
- **Update:** revise confidence and next action from results, including null or
  adverse results.
- **Record:** preserve commands, outputs, hashes, uncertainty, limitations, and
  reproduction instructions.

## Truth contract

- Only source-pinned recorded measurements may be labelled `OBSERVED`.
- A reconstruction, simulation, derived field, inferred latent state, or model
  output may never be relabelled observed.
- Keep *E. coli* behavioral evidence separate from *Salmonella* and *Bacillus*
  structural evidence. Never imply that they came from one measured specimen.
- Keep thermodynamic work `tau * delta_theta` separate from variational free
  energy and preserve their units.
- Keep priors, likelihoods, approximate posteriors, exact model posteriors,
  policies, predictions, actions, observations, and residuals distinct.
- Never silently mix mean-field, Bethe, marginal, or message-passing schemes.
- Do not count frames, time points, or repeated events as independent biological
  replicates when the experimental unit is a motor, cell, or culture.
- Calibration, training, holdout, and prospective evidence must remain separate.
- A prediction is prospective only if it was committed before its observation.
- Failed, blocked, external, and not-run gates remain visible.

## Repository discipline

Begin by reading this file, `README.md`, relevant files in `docs/`, protocols,
evidence manifests, gate ledgers, and tests. Then inspect:

```bash
git status -sb
git log -3 --oneline
git remote -v
node --version
npm --version
python --version
```

Treat unknown working-tree changes as user-owned. Do not reset, discard, delete,
or overwrite them. Use isolated branches or worktrees for destructive tests and
mutation experiments. Never push, publish, deploy, change access, or mutate an
external system without explicit authorization.

Use documentation-first TDD:

1. state the claim and acceptance criterion;
2. identify evidence, assumptions, units, and falsifier;
3. add a test that fails for the correct reason;
4. implement the smallest correction;
5. run focused and full validation;
6. update the gate ledger and documentation;
7. preserve pre-fix evidence and rollback instructions.

## Required validation

Use a genuinely clean clone for release claims. The deployment environment must
remain compatible with npm 10 as well as the declared local runtime.

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

If a required dataset, archive, instrument, credential, or service is absent,
mark its gate `BLOCKED`, `NOT RUN`, or `EXTERNAL VALIDATION REQUIRED`; never
report a pass. Report production and development dependency risk separately.

Numerically rederive important results through an independent implementation.
Audit tests for vacuous success, circular oracles, shared implementation,
unjustified tolerances, leakage, pseudoreplication, and missing negative controls.
Mutation tests must demonstrate that truth laundering, species swaps, hash
changes, split leakage, sign inversions, normalization errors, and removal of
adverse results are detected.

## Deep falsification after green gates

All existing gates passing starts deeper work; it does not end it. Run serious
model competition, ablation, parameter recovery, posterior predictive checks,
negative controls, robustness sweeps, leave-one-unit/study/condition-out tests,
and frozen prospective predictions. Compare against simpler and flexible
alternatives on identical splits and scoring rules.

Map the validity domain across species, strain, motor, cell, load, PMF, stator
state, temperature, viscosity, CheY-P condition, apparatus, timescale, study,
and model formulation. Classify every region as supported, tentatively
supported, contradicted, unidentifiable, unobserved, or extrapolation-only.

Prioritize experiments by expected information gain and their ability to make
competing models disagree. A potentially transformative discovery requires
risky prospective prediction, independent replication, explanatory reach, and
survival against serious alternatives. Do not use prestige as a gate.

## Communication

Lead with observed outcomes. Separate fact, inference, hypothesis, and ambition.
Always include adverse results and limitations. Every reported delta needs:

- severity and affected claim;
- file and line;
- reproduction command and evidence;
- root cause and minimal correction;
- required failing test;
- validation, rollback, and scientific impact.

Use `docs/CLAUDE_ULTRACODE_INDEPENDENT_AUDIT_PROMPT.md` for the full independent
audit and paste-back contract.

## The parity ladder is the spine; state it honestly every time

Every status report names where the work sits on `P0..P8` (computational
integrity, equation/implementation, observational, held-out predictive,
transfer, interventional, structural/mechanistic, independent replication, full
verdict) and gives the receipt for each: the exact artifact, gate id, and status.
`P8` is conjunctive — any single required `FAIL`, `CONTRADICTED`,
`NOT_ESTABLISHED`, `BLOCKED_EXTERNAL`, `NOT_RUN`, or `INVALID_PROVENANCE` makes
`FULL_PARITY=false`, and the report names the first unsatisfied level. This is a
statement about what the *current evidence* licenses, not a limit on the pursuit:
every gate that real evidence moves, moves, and the goal of a faithful,
fully-validated model stays live. Per plan §1 the boundary is on CLAIM WORDING —
the released product may not assert an *unqualified* claim of "full and exact
parity with nature" or call itself "digital life"; the strongest *allowable*
positive claim is bounded parity at the declared observational and intervention
resolution, over the frozen validity domain, within the frozen tolerances,
supported by independent evidence and reproducible from the recorded artifacts.
A higher claim is reached by supplying the evidence each level requires, never by
relabeling a gate. Never let a green software gate be read as biological parity,
and never average a missing external domain away.

## Execution-rigor lessons (earned, binding)

These were paid for with real defects. They are contract, not advice.

- **Separate the exact guarantee from the fragile numerical check, and never
  loosen a frozen tolerance.** A mandated verification can be numerically
  inadequate even when the property it checks holds exactly (a uniform-grid
  mean-one integral missed a `y^(a-1)` singularity while the analytic node-weight
  sum was exact to 1e-15). Keep the exact guarantee as the hard halt, add a
  well-conditioned independent check, and record the mandated-but-fragile result
  verbatim as a finding for the reviewer. Do not silently soften it and do not
  let it block the whole result without saying so.
- **Report credited, not classified.** A detection whose diagnostic cannot be
  attributed to its declared intended test is classified but not credited; the
  headline is the credited count and the gap is reported, never absorbed. An
  acceptance criterion scoped to a subset is evaluated on that subset, quoted
  verbatim, not paraphrased.
- **Prospectivity is decided by the commit graph, not by prose.** Flip a
  prediction record `PENDING -> PROSPECTIVE` only in the result commit, after the
  prediction commit is a proven strict ancestor of the result's introduction.
  A `PROSPECTIVE` declaration whose result is uncommitted is rejected by the gate.
- **Determinism is a gate, not a hope.** Prove it by executing the full pipeline
  twice and comparing canonical bytes. Seed every stochastic step once; forbid
  event-level resampling when the unit is the motor.
- **The independent oracle shares no code.** It reconstructs each quantity from
  the recorded parameters with its own implementation and must agree within a
  declared tolerance. An oracle that imports the code under test is circular and
  worthless.
- **Distinguish new coverage from suite-membership migration.** Moving an
  existing check into a classified gate is not the same as discovering a missing
  invariant. Say which it is.
- **A simpler baseline beating the mechanistic model is the headline, retained.**
  When a lognormal out-predicts the two-timescale UNI mixture on held-out data,
  that adverse result is reported alongside every later result, never instead of
  it, and predictive superiority of any model is never promoted to mechanism.
- **Underpowered is not equivalence.** With few experimental units (e.g. 19
  holdout motors) most contrasts are inconclusive. Report "not resolved at this
  sample size" with the interval width; never read a zero-crossing interval as
  "no difference," and never increase replicates after seeing a width.
- **Governance precedence is explicit.** When an integration document governs
  component specifications on conflict, it wins; record every integration
  decision (which document governed, which clause was superseded) in the result
  so a reviewer can rule on it rather than reverse-engineer it.
- **A halt or a blocked external gate is a legitimate, reportable scientific
  outcome.** Completing a plan with `BLOCKED_EXTERNAL` and honest `NOT_ESTABLISHED`
  statuses is a successful negative verdict, not an incomplete task. Do not
  manufacture a pass, and do not rush a frozen protocol to force one.

## Hierarchical-AIF program (H-AIF) — binding operating contract

This section governs all work in the `hierarchical-aif/` namespace. A new agent must read
`hierarchical-aif/README.md` before acting, then
`hierarchical-aif/docs/CURRENT-STATE-AND-NEXT-ACT.md` for live state.

### Path contract

- `audits/phase-c/**` and `audits/phase-d/**` are **frozen, read-only historical evidence**.
  A hash baseline of all 250 files lives at
  `hierarchical-aif/reports/frozen-evidence-baseline.sha256`. Any diff against it is a contract
  violation and a hard stop.
- `audits/phase-b/**` is likewise not edited; the B3/B4 runners retain their defects on purpose so
  the historical results stay reproducible.
- **All new work goes under `hierarchical-aif/`** (`docs/`, `src/`, `tests/`, `results/`,
  `ledgers/`, `reports/`, `protocols/`, `scripts/`).
- Never create `phase-c/`, `docs/phase-c/`, `tests/phase-c/`, or `results/phase-c/`. That name is
  already taken by frozen evidence, and reusing it blurs two unrelated evidence bodies.

### Gates and ladder

- New gates are `H-AIF-G1..G9` (see `hierarchical-aif/docs/H-AIF-GATES.md`).
- The existing `P0..P8` parity ladder in this file is **authoritative and unchanged**. H-AIF gates
  produce receipts that **map onto** it via
  `hierarchical-aif/ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md`.
- Never redefine `P0..P8`, never create a v2, never run a parallel ladder.

### Scope

- The **flagellum motor stack** (`Lmotor-5..Lmotor-0`) is the runnable, scoreable scope.
- The **human `L0..L12` stack is DESIGN-ONLY / NOT-BUILT / NOT-SCORED / NOT-CLAIMED.** This
  repository contains no organ, language, self-model, reasoning, dreaming, or awareness dataset.
  Implementing it would create unfalsifiable scaffolding.
- **F-side observable projection: BUILD AND SCORE NOW.**
  **G-side biological policy selection: DESIGN-ONLY UNTIL INTERVENTION OR TRANSFER.** The dataset
  is passive; the action set is empty, which is structural, not sample-size-limited. The absence
  of an `expected_free_energy` function is enforced by a test.

### FLOW — and alignment is not a stop state

```text
PERCEIVE -> BOUND -> PREDICT -> CHOOSE -> ACT -> OBSERVE -> UPDATE -> RECORD -> NEXT_ACT
```

Every RECORD ends with `NEXT_ACT`. Writing a report, passing tests, creating a ledger, or
declaring alignment are **not** stopping conditions. While a long run executes, work a safe
non-interfering lane. Append a FLOW card to `hierarchical-aif/reports/FLOW-JOURNAL.jsonl` for
every major action. Stop only for a declared STOP condition
(`hierarchical-aif/docs/ORCHESTRATE-RULES.md`).

### Held-out data firewall (earned from defect D5)

**Reading held-out data is irreversible. Read-only is not consequence-free.** A read-only audit
task, given a brief with no split boundary, read the held-out mark channel and permanently
destroyed its prospective status.

- Every analysis declares a split boundary from the fixed vocabulary in
  `hierarchical-aif/docs/DATA-CHANNEL-SPEND-LEDGER.md`.
- Any task that might touch held-out fields first writes
  `hierarchical-aif/protocols/<TASK>-DATA-ACCESS-PROTOCOL.md`.
- Every subagent brief pastes the D5 firewall verbatim from
  `hierarchical-aif/docs/SUBAGENT-BRIEF-TEMPLATE.md`. An agent answering
  `NOT_CHECKED — would require holdout access` is giving a **correct and valuable** answer.

### Defects are closed by action, not by recording

A defect is a completed FLOW result only when routed into **repair, quarantine, rerun, transfer,
or falsification**. `hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md` tracks
that routing and — critically — names the lanes each defect does **not** touch.

**Never write an unscoped weakening statement.** Not "P6 is weaker", but "P6 for C11 U4 is
withdrawn until the corrected C11 run lands; P6 for duration-only B3/B4 is unchanged."

Lanes: **A** duration-only B3/B4 · **B** corrected B4 robustness · **C** mark process ·
**D** motor-stack AIF · **E** parity ladder · **F** governance/reporting.

### Claim clamp

`hierarchical-aif/src/motor_stack_aif/claim_guard.py` mechanically clamps forbidden claim wording
and must be run after every report batch. It distinguishes use from mention. Passing it is
**necessary, not sufficient** — it checks wording, never whether evidence supports a claim.

### Standing frame

```text
Nature supplies the architecture candidate. The gate supplies the status.
Full biological parity is not a current status. It is the target world defined by the receipts.
```

Keep `H_PARITY` alive as a target hypothesis, keep the current design as control, keep the simple
baselines alive as adversaries, and move a P-level only by a scoped receipt.

---

## Communication with the operator (binding, added 2026-07-25 at his request)

Michael is the **organic operator**. He works by conversation. Test-summary dumps do not
work for him and are not an acceptable primary channel.

### Speak

Use `mcp__claude-voice__speak` — it is confirmed working (Piper, local, `en_GB-jenny_dioco-medium`
by default) — for **every** one of these:

- opening or closing a phase;
- any finding, and **especially** an adverse result, a falsified prediction, or a retraction;
- when a decision is his to make — speak the question, then stop;
- when work completes, or when it is blocked and needs him.

Keep spoken lines short and human. Say the thing, not the report. The transcript persists at
`http://127.0.0.1:5858` and is rendered live in UNI TRACK.

### Be conversational in text too

Lead with the outcome in the first sentence, in plain language. No wall-of-text status blocks,
no pasted test output, no table as the opening move. Write as if talking to him, because you are.

### Detail belongs in TRACK, not in chat

**UNI TRACK — `http://127.0.0.1:8102/`** (`viewer/track/track_server.cjs` in `UNI.Minecraft`) is the
persistent surface. It carries, read live and never cached: where the work came from, where it is,
where it is going, what is done, what is left, what is predicted next, the calibration, and the exact
next scope. Start it if it is down.

If you catch yourself writing a long status block in chat, that content belongs in TRACK. Put it
there and say the one sentence that matters.

Claude comments on specific items with `POST http://127.0.0.1:8102/api/comment {target,text}` —
append-only to `evidence/track_comments.ndjson`, version-controlled, never edited.

### Never bury an adverse result

A `FAIL`, a retraction, a falsified prediction, a `NOT_CLEARED` — these are **spoken** and said
**first**, never appended at the end where they read as a footnote. An adverse result carried
honestly is the product working.

### Ask, do not assume

When a choice is the operator's — naming, scope, a contract amendment, anything principal-gated —
speak the question and wait. Do not quietly pick and proceed.

### Reinforced 2026-07-25, second time of asking

Michael asked twice. That means the first version was not doing its job, so this is
concrete rather than aspirational.

**The failure mode is not "too long". It is "structured like a report".** A status
block, a table as the opening move, a list of everything done in order of doing it —
these are formats for a reader who is auditing. Michael is not auditing; he is working.
He wants to know what happened, what it means, and what is next, in that order, in
sentences.

Do this:

- **Open with the outcome, in one sentence, in plain words.** If there is an adverse
  result, it IS the opening sentence — not a section further down and never a footnote.
- **Say the thing that changed his picture of the world.** Not the sequence of steps.
  "The ledger violates its own schema in twelve places" is the news. "I ran the
  validator against the canonical ledger" is not.
- **Name the number that matters and drop the rest.** Detail belongs in TRACK, in the
  receipt, and in the commit message — all three of which persist and are searchable.
- **Speak the same thing, shorter.** `mcp__claude-voice__speak` on every finding, every
  phase edge, every adverse result, every question that is his. Spoken lines are shorter
  than written ones and carry no formatting at all.
- **Correct yourself out loud, in the same breath, before acting on it.** If a count was
  wrong, if a recommendation was off, if a write went wrong — say so first, plainly,
  then say what you did about it. A correction carried quietly is worse than the error.

Do not do this:

- open with a table, a heading, or a bullet list;
- narrate the order you did things in;
- append the bad news to the end where it reads as a caveat;
- offer a menu of options when the flow has one next act — recommend, and ask for the
  co-sign;
- paste test output into chat. Say "621 tests, zero failures" and move on.
