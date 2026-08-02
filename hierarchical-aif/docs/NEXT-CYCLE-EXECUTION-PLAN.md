# UNI-FLAGELLUM — Next-cycle execution plan (OODA, ultracode 3-body)

**Durable location:** `hierarchical-aif/docs/NEXT-CYCLE-EXECUTION-PLAN.md` (this file is the single source
of truth; the rendered companion is `hierarchical-aif/docs/NEXT-CYCLE-PLAN.html`, a self-contained,
CPU-only, no-network standalone page — open it directly with `file://`).
**Anchor:** HEAD `e21747c`, branch `hierarchical-aif/motor-stack`, nothing pushed.
**Method:** OBSERVE→BOUND→PREDICT→ACT→VERIFY→FALSIFY→UPDATE→RECORD, processed by a 9-agent ultracode
workflow with a 3-body adversarial review (2 new personas). This document is **DESIGN — authorized to
build, not a result.** Nothing here has moved a P-level. It is a standalone plan document, not a served route.

---

## 0. Honest headline (lead with the outcome)

- **The model math is done for this batch; the binding constraint is DATA, not math.** The first
  missing rung is **P4 transfer**, which is *irreducibly external* — no in-repo work closes it.
- **This cycle exactly 4 gates can move to durable green with in-repo OBSERVED evidence** — and
  **zero of them raise any P-level.** They are: restore P0, restore H-AIF-G1, bring the **D12
  remediation gate PENDING→PASS**, and close **H-AIF-G9**.
- **Green now = 16 of 31 gates — but only ONE of those 16 (P2) is genuinely observational, and it is
  LIMITED** (mark fields quarantined, raw archive not located). The other 15 are computational-
  integrity / equation-implementation / defect-closure gates. *Do not read "16 green" as "16
  biological observations."*
- **10 gates are EXTERNAL-BLOCKED** (P4, P5, P6, P7, P8, H-AIF-G8 raw archive, D5, D6, D9, and the new
  accessibility gate which ships NOT_ESTABLISHED). **1 is design-only** (H-AIF-G6, the human L0..L12 stack).
- **The adverse result rides at the top, co-equal:** a simple **lognormal (M2) still out-scores the
  flagship two-timescale UNI model (M3) on held-out data** (M2 −3.013 vs M3 −3.050 nats/event; the
  M3−M2 interval crosses zero → *unresolved at this sample size*, not "M2 wins," not "no difference").
- **P8 = FULL_PARITY = false.** No parity, active-inference, life, consciousness, or "soul" claim is
  minted from passive data — at any layer, including the child-facing one.

**Gate forecast:** greenNow **16** · remediation-clearable this cycle **4** · external-blocked **10** ·
design-only **1** · total **31**. `oneCycleClearCount = 4`.

---

## 1. OBSERVE — what the resample actually showed (durable receipts)

Live re-run at HEAD `e21747c` (not copied from the snapshot doc). Reproduce with the §1 commands in
`hierarchical-aif/docs/CURRENT-STATE-AND-NEXT-ACT.md` plus the four gate commands below.

| check | command | OBSERVED | class |
|-|-|-|-|
| science:verify | `npm run science:verify` | **PASS** (244 holdout intervals, mean log-score/interval −3.8380834; asserts `fullBiologicalParityAchieved=false`, `G03_PUBLIC_ARTIFACT_PARITY=FAIL`, `G10=NOT_ESTABLISHED`) | GREEN |
| cross-study:verify | `npm run cross-study:verify` | **PASS** (itoLOO RMSE 0.829, latticeFittedSse 0.0498, rftRmse 1.727, 10 artifacts) | GREEN |
| cross-study:verify-raw | `npm run cross-study:verify-raw` | **EXIT 1 — BLOCKED_EXTERNAL** (missing `experiments/upstream-cache/ito-2021-raw-data.zip`) | BLOCKED |
| pytest motor_stack_aif | `python -m pytest hierarchical-aif/tests/motor_stack_aif -q` | **504 passed / 3 skipped / 1 xfailed** | GREEN* |
| claim_guard | `claim_guard.py <6 paths>` | **0 violations / 6 paths** | GREEN (scope-limited, see §5) |
| numeric_provenance_guard | `numeric_provenance_guard.py <4 paths>` | **2070 in-scope decimals, 0 failures** | GREEN |

\* **Preserved discrepancy:** the live-state doc §1 predicts `505 passed, 2 skipped`; observed
`504 passed, 3 skipped` (same total 508). One test skipped in this environment that passed in the
recorded run. Snapshot↔environment drift, flagged not hidden.

**Two resonance disagreements to keep visible, with their receipts (do not launder):**
1. `publicArtifactMismatchDetected: true` (`scripts/independent-science-check.mjs:52`) is the
   independent oracle **asserting the expected `G03_PUBLIC_ARTIFACT_PARITY = FAIL`** (lines 44–46) —
   i.e. science:verify PASS *includes verifying that the public artifact correctly does not match and
   that parity is correctly false.* It is a green that confirms an honest negative. Surface it **with**
   this receipt; never fold it into "P0 strengthened."
2. **The working tree is DIRTY** — `M hierarchical-aif/docs/CURRENT-STATE-AND-NEXT-ACT.md` (a
   106+/109− uncommitted rewrite). This trips H-AIF-G1's own verbatim falsifier ("a non-clean working
   tree presented as clean"), so **P0 and H-AIF-G1 are currently DIRTY-CLAIM-WITHDRAWN** until the tree
   is clean. **This file is USER-OWNED** (per CLAUDE.md, treat unknown working-tree changes as
   user-owned) → committing or reverting it is **PRINCIPAL-GATED (Michael's call), not an agent action.**

**Topology.** Real repo `UNI-FLAGELLUM/` @ `e21747c`. `UNI-FLAGELLUM-math-workbench/` is a **git
worktree of the same repo** on `feature/scientific-math-workbench` @ `c23f686`; it adds the
`/math-workbench` route (6 views) the base app lacks. Three distribution archives sit on disk (see §3).

---

## 2. Independently verified defect facts (observed, not relayed)

| finding | receipt (file:line) | status |
|-|-|-|
| compare.py P-ladder metadata off-by-one | `compare.py:546` literally: *"P3 duration-only ONLY. P5 transfer, P6 intervention, P8 full verdict…"* — transfer is **P4** not P5, intervention is **P5** not P6, **P7 independent replication omitted** | CONFIRMED |
| score.py silent zip-truncation | `score.py:17` & `:29` — `for v, m in zip(per_event_nlpd, motor_ids)` truncates to shorter input before any shape check | CONFIRMED |
| claim_guard scope gap | `claim_guard.py:96` — `patterns=("*.md","*.json","*.jsonl")`; the 32 KB public teaching surface `lib/walkthrough.js` + narration is **outside** the clamp | CONFIRMED |
| D12 is narrative-only | `git grep WITHDRAWN_D5_UNSAFE` = **0 tracked files**; `git grep D12` = 1 hit, an unrelated video filename | CONFIRMED |
| failure-count sentence to correct | `reports/PHASE-HIERARCHICAL-AIF-CORRECTED-CLOSURE.md:32` — *"All four corrected B4 cells landed at full frozen N, 0 failures each"* (collides with withdrawn C11 U4) | LOCATED |
| archive to withdraw | `UNI-FLAGELLUM-haif-closure-e21747c.zip` SHA-256 `7b28f0d6f338cb2fa077d3a84fe9688c44a67cb813e513f27a1a0348113d41b2` | CAPTURED |

---

## 3. Distribution-archive exposure record (Custodian requirement)

Three built, distributable objects are on disk at the wrapper root. Member-level D5-safety is
**NOT_CHECKED / UNVERIFIED** (opening members is firewall-barred to design-only agents). Treat as
UNVERIFIED, never "safe." **Transmission is external and principal-only. These packets are NOT closure
evidence.**

| archive | SHA-256 | disposition |
|-|-|-|
| `UNI-FLAGELLUM-haif-closure-e21747c.zip` | `7b28f0d6…41b2` | **candidate WITHDRAWN_D5_UNSAFE** (D12 target) |
| `UNI-FLAGELLUM-EXTERNAL-REVIEW-e21747c.zip` | `4f8945b1…6f87` | member timestamps 2026-07-23; UNVERIFIED |
| `uni-flagellum-b3-b4-evidence-17a2f0e.zip` | `ae42f203…87f1` | UNVERIFIED |

---

## 4. The 3-body persona charter (odd, majority-adversarial, tension-holding)

Every decision is held by **≥3 perspectives, always odd, majority adversarial.** Michael sits INSIDE
as a present member; the two NEW personas hold the adversarial majority; the existing lab team plugs in
for FE-touching changes.

| persona | role | mandate | default verdict |
|-|-|-|-|
| **Michael — Regenerative Architect** *(new: inside)* | proponent, present member | Algebra-up layering of every result, every time; all math/bytes/renderings surfaced OUTSIDE (meaning: in the repo, version-controlled — never on an external surface); CPU-only. Channel ambition into the honest non-science lane. Owns reviewer-transmission personally. Won't manufacture a pass. | SIGN_WITH_CHANGES |
| **Custodian of the Boundary** *(new adversary #1)* | irreversibility + integrity floor | No gate green on a false receipt; clean tree before any green. Distribution is irreversible → D12 never collapses to CLOSED_BY_REDACTION; incident stays NEGATIVE permanently. No frozen-artifact overwrite; sanitized ancestry receipt, not a git bundle. Un-scanned archive = UNVERIFIED. | **REJECT** |
| **Devil's Pedagogue** *(new adversary #2)* | anti-laundering + pedagogy integrity | Fail-closed method guards; forbid EFE/L0..L12 scaffolding on passive data (test-enforced absence); forbid D10 sub-floor laundering (F-side's ~2.5e-7-nat effect is never "beats M7"); identifiability is not mechanism; every simplified layer carries a truth badge + a "what it drops" caveat + a path back up. | **REJECT** |
| Existing lab team | deep FE-touching council | Math-Breaker → Architect → Experimentalist → Embodiment → AIF Theorist (merge); Organic Operator guards the operator-facing `/math-workbench`. | WITHHELD |

**3-body verdicts this round:** Custodian **REJECT** (dirty tree; D12 narrative-only; archives on disk;
mismatch flag laundering) · Devil's Pedagogue **SIGN_WITH_CHANGES** (teaching surface unscored;
OBSERVED-class conflation; adverse result demoted) · Michael **SIGN_WITH_CHANGES** (accessibility
unscored; teaching stack homeless; shortest-path-to-P4 unranked). **All required changes are folded into
§6; all preserved tensions into §7.**

---

## 5. What the two adversaries added (beyond the authorization)

1. **The teaching surface is unscored and unclamped.** `lib/walkthrough.js` + spoken narration (the
   channel a *child* hears) is outside `claim_guard`. Resonance channel #5 (UI truth badge + species
   label) has **zero gate coverage.** → new UI-truth-badge runtime gate + species-label gate + a sibling
   `*.js`/narration clamp; until then annotate "claim_guard 0 EXCLUDES the teaching surface."
2. **OBSERVED-class conflation.** "16 green" must be split: **1 (LIMITED) observational** vs 15
   process/implementation/defect gates. No banner may let a reader hear "16 biological observations."
3. **Adverse M2-beats-M3 result demoted.** Promote it into the headline, co-equal with the green count.
4. **Reconstruction-beside-microscopy (walkthrough step 2) and multi-species cutaway (step 3)** need a
   *runtime* receipt that the truth badge + per-species label render, can't be desynced, and survive a
   screenshot/share — a doc table is not runtime enforcement.
5. **`publicArtifactMismatchDetected` must be surfaced with its receipt** (see §1).

---

## 6. Execution plan — 11 steps, strictly sequenced (containment first)

**Sequencing rule (principal M25 authorization):** CONTAINMENT precedes everything; METHOD guards land as
additive sidecars; UI-WORKBENCH + LAYMAN-LAYERING add the honest teaching surface; SCIENCE-EXTERNAL is
pre-registration ONLY. **P4/P5/P6/P7/P8 stay external-blocked and unmoved. Nothing is pushed or
transmitted — building in-repo is authorized; sending is principal-only.**

### Track A — CONTAINMENT (owner: Custodian)

**Step 1 — Restore the integrity floor. [PRINCIPAL-GATED]**
Commit *or* revert the dirty user-owned `hierarchical-aif/docs/CURRENT-STATE-AND-NEXT-ACT.md`, then
re-run science:verify / cross-study:verify / pytest (504p/3s/1xf) / claim_guard 0 / numeric_provenance
2070-0. Preserve `e21747c` — **no amend/rebase/force-push.**
→ *Durable evidence:* clean `git status -sb` + re-run PASS receipts → **P0 and H-AIF-G1 re-established green.**
→ *Blocked by:* the file is user-owned — **Michael decides commit vs revert; agents do not touch it.**

**Step 2 — Build `d5_distribution_guard` (SEPARATE guard; do NOT overload numeric_provenance_guard).**
Runs on the STAGED tree AND the finished round-trip archive. Structurally parses JSON/JSONL string
*values* (not just keys); scans md/txt/code/logs/manifests/generated reports; inspects or rejects nested
archives; detects real event-id patterns, motor-ids co-located with holdout mark context, record-shaped
`stateN/nextStateN/jump/direction`+holdout combos; distinguishes schema/declaration prose from
value-bearing records; permits synthetic fixtures only with an explicit synthetic marker; **fails on
pre-redaction examples + mutation variants**; emits a machine-readable report of every inspected artifact
+ exception. **Failing tests written first.**
→ *Release falsifier:* any real event-id / associated motor-id / event-level mark tuple surviving any
shipped artifact FAILS release.

**Step 3 — D12 incident-remediation (build the receipts that don't yet exist).**
Redact event-level identifiers, motor-ids tied to the mark defect, and record-shaped mark tuples from
EVERY distributable surface: `reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md`;
`protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md`; `ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md`;
`tests/motor_stack_aif/test_nextstate_range_check.py`; + every package-stage scan hit. Prefer
*"below-physical-minimum target-state marks"* over the exact value; aggregate counts may remain **only**
with no event-id/motor-id/reconstructable tuple. Narrow the handoff claim from *"no raw mark-key values."*
Add a tracked WITHDRAWAL notice for `UNI-FLAGELLUM-haif-closure-e21747c.zip` (name + SHA-256, no records
reproduced; states: WITHDRAWN_D5_UNSAFE / stop redistribution / request deletion / record acks without
assuming them / name successor once it exists). Record D12 as **incident=NEGATIVE, remediation
gate=PENDING, historical archive=WITHDRAWN_D5_UNSAFE, residual=prior distribution cannot be recalled.**
→ **D12 never collapses to CLOSED_BY_REDACTION; the historical NEGATIVE remains even after the gate passes.**

**Step 4 — Build the D5-safe successor archive (this is what moves D12 PENDING→PASS).**
Pipeline: new anchor → `d5_distribution_guard` scan of staged tree → manifest → archive → unpack clean →
rescan → recompute manifest+hash → confirm no withdrawn blobs/patches/bundles → include withdrawal notice
+ D12 report. Use a **SANITIZED ANCESTRY RECEIPT** (commit ids/parents/timestamps/payloads/name-status/
commands/receipt hashes), classed `GIT_ANCESTRY_RECEIPT_PROVIDED; FULL_HISTORY_RECONSTRUCTION_NOT_INCLUDED`
— **do NOT place a git bundle in the archive** (it would carry the withdrawn blobs).
→ *Blocked by:* re-distribution/transmission stays principal-gated. Building is authorized; sending is not.

### Track B — METHOD (additive sidecars; owners: Devil's Pedagogue + Custodian; move NO P-level)

**Step 5 — Fail-closed method guards.** (a) score.py `motor_equal_nlpd`/`per_motor_means`: replace bare
`zip` with checks for equal event-score & motor-id lengths, non-empty, finite scores, non-empty & finite
paired motor arrays, valid bootstrap request, complete expected-motor coverage at aggregation. (b) Optimizer
fail-closed: a fitted object whose optimizer reports non-convergence must not enter scoring/result
assembly — **one shared eligibility assertion across every scoring entry point.** *Mutation falsifiers:*
remove one motor-id or one event score → aggregation raises before any mean; force finite params +
unsuccessful termination → scoring halts, no artifact written.

**Step 6 — Canonical P-ladder metadata restoration in `compare.py:546`.** → P4 transfer, P5 intervention,
P6 structural/mechanistic, P7 independent replication, P8 full verdict. **Issue correction SIDECARS with
new hashes; do NOT overwrite frozen result/prediction JSON.** `status.py` overrun-semantics stays PENDING
(must resolve before external P4; need not delay D12).

**Step 7 — Failure-count + D9 corrections.** Add `CORRECTION-NOTICE-e21747c.md` quoting the false
historical failure-count sentence (`PHASE-…-CLOSURE.md:32`), the corrected cell-specific status, and the
superseding commit (original commit message stays historical). D9: separate
`historical_evidence_at_defect_open` / `current_repo_disposition` / `external_handoff_evidence_limit`; add
a status addendum; keep B4C10 & F-side **NOT_SATISFIED**; **do NOT edit original B4C11 prediction bytes.**
→ *Blocked by:* transmission of the correction notice is **principal-gated (Michael only)** — prepare, never send.

**Step 8 — Reduce the disclosed G5 resonance disagreement in the same change.** Correct the stale
`H-AIF-GATES.md` "IN PROGRESS" to match the ladder-map "COMPLETE" (no frozen artifact touched). **Closes
H-AIF-G9.** Moves no P-level.

### Track C — UI-WORKBENCH + LAYMAN-LAYERING (owners: Michael + Organic Operator + Devil's Pedagogue)

**Step 9 — Add a first-class ACCESSIBILITY/PEDAGOGY gate + honest OUTSIDE-IN-REPO rendering, bound to the
workbench** (route `/math-workbench`, named commit). Render the TRUE gate state (16 green / 4 clearable /
10 external-blocked / 1 design-only; P8=false; first-missing P4) where **no simplification layer may
relabel a status.** Add the UI-truth-badge runtime gate + species-label gate + a `*.js`/narration sibling
clamp (§5). CPU-only; no LLM/GPU/WebGL/WebGPU/Three.js/analytics/accounts/hidden-network. **Ship the
accessibility gate NOT_ESTABLISHED with a stated falsifier** — usability is a claim, not an achievement.
Flag `app/chatgpt-auth.ts` as a release risk (accounts/network the release forbids).

**Step 10 — Declare the NON-science lane for the L0..L12 teaching stack.** A reduced teaching model over a
reduced/synthetic world, carrying NO P-level, NO `expected_free_energy` on passive data, NO mechanism
claim. Keep H-AIF-G6's **test-enforced absence** of any EFE function in passive-data scope. This gives the
platform ambition an honest home without laundering; it does not build L0..L12 content on passive data.

### Track D — SCIENCE-EXTERNAL (owner: Experimentalist / AIF Theorist; pre-registration ONLY)

**Step 11 — Pre-register the shortest path to P4 (D9 discipline, committed BEFORE any data is touched).**
Rank external blockers by expected information gain; commit the scoring rule for the single cheapest
independent transfer cohort — an independent single-motor dwell series with **enough independent MOTORS to
beat the C01 nesting-blindness** (M0 self-win 0.290). **Do NOT execute.** P4 stays external-blocked and
unmoved; P4 execution is gated on containment + guards in place AND real external data acquired.

---

## 7. Preserved tensions (do NOT resolve by weakening)

1. **M2/lognormal still leads the held-out leaderboard** — kept alive by design; mechanistic ambition may
   not bury the adverse result.
2. **P8 FULL_PARITY=false**, first missing rung P4 transfer, irreducibly external.
3. **Mechanism is RETROSPECTIVE-ONLY / TRANSFER-REQUIRED** (D5/D6); identifiability and architecture are
   **not** mechanism; no aggregate P6 is asserted.
4. **L0..L12 stack + any EFE stay OFF passive data** via test-enforced absence (H-AIF-G6 design-only) —
   ambition vs falsifiability, preserved not collapsed.
5. **Accessibility / 5-to-199 path ships NOT_ESTABLISHED with a falsifier** — a hypothesis, not an
   achievement; any layer that relabels a status is rejected.
6. **D10 sub-floor guard:** the F-side ~2.5e-7-nat (~168,000× sub-floor) effect may never be "beats M7."
7. **D12 incident stays NEGATIVE permanently** even after the remediation gate passes; prior distribution
   cannot be recalled; un-scanned archive members are UNVERIFIED, never safe.
8. **Reviewer / correction-notice transmission stays principal-gated (Michael only).**
9. **H-AIF-G8 raw archive not located**; packaged event JSON may never be read as raw confirmation.
10. **Species + units fences:** E. coli behavioral kept distinct from Salmonella/Bacillus structural;
    nats (free energy, log score) never converted to joules (τ·Δθ work).

---

## 8. Algebra-up layering (the child-to-scientist ladder, badge-invariant)

Every load-bearing object is taught on the **same 3-rung scaffold; the rungs climb only in MATHEMATICAL
machinery, never in evidential authority.** The truth badge is IDENTICAL across all three rungs of an
object, and each object states **exactly what the simplification drops.** The full content is rendered in
the companion page `hierarchical-aif/docs/NEXT-CYCLE-PLAN.html`. Objects: dwell-time first-passage survival
(MODEL, gates G03/G05/G06 FAILED); held-out log score / NLPD (MODEL); M3 two-timescale vs M2 lognormal
(MODEL, M2 leads); motor-cluster bootstrap CI (MODEL); the P0..P8 ladder itself (DESIGN); free energy in
nats vs τ·Δθ work in joules (MODEL, no conversion, E-M01 open); the exact log-odds Bayesian update / UNI
gear (MODEL); finite-lattice cooperativity falsifier (MODEL, X06/X11 FAIL); CV²>1 overdispersion (MODEL,
the one clearly-resolved held-out result).

**10 overclaim guards** bind the scaffold (badge invariance; prediction-is-not-mechanism; no nats↔joules
conversion; adverse results ride with every summary; resolved-vs-unresolved decided by the interval;
conjunctive ladder; species/class separation; no consciousness/life/soul claim; D5 firewall in every
teaching example; open defects stay visible even at the child rung).

---

## 9. Authorization, rollback, and what this cycle is NOT

- **Authorized to build:** steps 2–11 in-repo (containment guards, method sidecars, teaching gates,
  pre-registration). **Principal-gated:** step 1 (user-owned file), all transmission/redistribution.
- **Not authorized:** amend/rebase/force-push of `e21747c`; git bundle in the successor archive; editing
  frozen `audits/phase-b|c|d/**` or frozen result/prediction bytes; overwriting the user-owned working file.
- **Rollback:** every step is additive (new files / sidecars) or a scoped metadata edit; `e21747c` and all
  frozen artifacts remain byte-identical, so rollback = discard the new files.
- **This cycle raises NO P-level.** It is containment + method integrity + an honest teaching surface. The
  next *scientific* gain (P4) requires external data and begins only after containment + guards are in place.

---

## 10. Governance note — critical information lives IN this repo

This plan and its rendered page are **version-controlled files inside the repository**, not an external
hosted surface. Critical UNI-FLAGELLUM information (plans, gate state, evidence, findings, decisions) is
kept in the repo, reproducible from recorded in-repo artifacts, with no hidden external or network
dependency — consistent with the truth/resonance contract and the CPU-only, no-network release rules.
