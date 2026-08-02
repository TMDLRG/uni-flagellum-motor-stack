# The Control Plane — architecture

**Status: PART DESIGN, PART BUILT. No P-level is moved by this document.**
Authored 2026-07-25 against directly inspected state; §3.2 records what has since landed.
Phase 2 built `Ledger`, `GateRow`, `Command` and `Drift`; Phase 3 added `Registry`, `Verdict`, `Anchor` and the two-party rule, and made the gate ledger's effective state conform to its own schema; Phase 4 added `Store`, `Run` and `Pair`; Phase 5 added `Witness`, the first real Control Plane ledger, and a Gaia seat that projects it verbatim; Phase 6 added `Room` and `Key`. Only the lab view remains unbuilt.

**Model of record:** [`workspace.dsl`](workspace.dsl) (C4 / Structurizr DSL). **Views:** [`views.md`](views.md) (Mermaid, renders with no build step). **Decisions:** [`decisions/`](decisions/). This file carries what the model cannot: contracts, invariants, failure modes and acceptance criteria. Where a view and the DSL disagree, the DSL wins — see [ADR-0004](decisions/ADR-0004-model-as-code-not-svg.md).

Placement note: this document lives in the `UNI-FLAGELLUM` repository, but the Control Plane is **platform-wide**, not a flagellum component. **Resolved 2026-07-25:** the canonical platform repo is `UNI.Minecraft` on **THINKER** (branch `gen2-runtime`, HEAD `cdf73c89`), byte-matching the `git.head` signal Gaia serves; the chip's `/home/uni/build_*` trees have no git and are deployed copies. The code lands there ([ADR-0006](decisions/ADR-0006-sp-controlplane-naming-and-placement.md)); whether this document follows it remains open (§14.5).

---

## 1. Purpose and scope

### 1.1 What the Control Plane is

The body that **runs the science and authors every verdict**, across every project on the platform. It is also **the lab**: the room the operator stands in and works from. The machinery and the room are one body, because a verdict is authored by standing at the thing being ruled on.

### 1.2 What it is not

- **Not Gaia.** Gaia may never act or author a verdict (§3.3). A Gaia-centred control plane is structurally impossible, not merely undesirable.
- **Not the Door.** The Door governs a threshold; it does not run experiments.
- **Not the HUD.** The HUD displays and authors nothing.
- **Not UNI.Minecraft's control center.** That is a live-television vision mixer for one world (§4.1).
- **Not a dashboard.** Dashboards report. This body decides.

### 1.3 Non-goals

Replacing any existing surface. Re-deriving any world's state. Holding a stream key. Typing go-live. Rendering awareness, experience or life in any form.

---

## 2. The problem this solves

Two gaps, verified:

**The machinery has no home.** Steps 1–6 of the evidence spine — register a gate, run paired, observe, adversarial review, author the verdict, write the receipt — are performed by hand by whichever agent is working. Steps 7–9 work: `gates.ndjson` is append-only at **206 rows / 109 unique gates** (canonical: `UNI.Minecraft` @ `gen2-runtime`), and `gaia_lint.cjs` mechanically fails the build on summarization or lost provenance.

**Gate status drifts because nothing owns it.** In the flagellum repo, `H-AIF-G7` is recorded `NOT RUN` at `hierarchical-aif/docs/H-AIF-GATES.md:15` and `EXECUTED — NOT_ESTABLISHED` at `hierarchical-aif/ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md:53`. G5 and G6 disagree likewise. Gate status is hand-written prose in nine files.

**The fix is not to let Gaia compute the truth** — GAIA LAW forbids it. One body authors; Gaia projects both the claim and the receipt and surfaces the disagreement.

**There is nowhere to stand.** Every surface shows one world to an audience, or one machine's own state, or signals. None is a lab you enter and work in across every project at once.

---

## 3. The four bodies

### 3.1 The Door — BUILT

`viewer/launcher.cjs` on `:8090`. Living map at `/door`, rendering `/api/door/state` + `/api/door/journey` on a 3s poll.

| aspect | contract |
|-|-|
| Responsibility | Admission and release. Key custody. The journey. |
| Verbs | `POST /api/door/open`, `/api/door/close` — loopback + `x-uni-cc` |
| Journey | `studio_ready → feature_test → go_live → run_of_show → off_air`; state on disk, survives reboot; steps arm synchronously |
| Ledger | `door_lifecycle.cjs` appends actor, method and prediction per verb |
| **Law** | **A polled read never spawns anything.** Every actuation is a deliberate operator click or an explicit verb. |
| Breakers | Reads are pure observers · OS mutex `UNI_STUDIO_UP` · idempotent windows. Any one alone stops a spawn storm; all three are in. |
| Gates | `door-lifecycle-circle`, `door-boot-persistent`, `door-storm-breakers` |

**The Control Plane inherits the Door's law verbatim.** It is the hardest-won rule on the platform — burned in by two recorded spawn storms — and re-deriving it would be negligent.

### 3.2 The Control Plane — PARTLY BUILT

Its own service, own address, own append-only ledger. Detailed in §5–§9.

**Built, 2026-07-25** (`UNI.Minecraft` `75e2fc4`, root zero-dep app, `deps: []` unchanged): `SP.ControlPlane.Ledger` (append-only, hash-chained, canonical serialization), `SP.ControlPlane.GateRow` (hand-written implementation of `gate_row.schema.json`), `SP.ControlPlane.Command` (the only writer, guarded by a writ type gate **and** a static source scan, both mutation-tested), `SP.ControlPlane.Drift` (cross-kind comparison refused at construction). 61 tests. Receipts and full disposition: [`phases/PHASE-2-RESULTS.md`](phases/PHASE-2-RESULTS.md).

**Added 2026-07-25, Phase 3** (`8ff5591`): `Registry` (registration must be the *first* entry mentioning its gate — prospectivity by position, not by wording), `Verdict` (five controlled words, no number, no percent, no bare `PARTIAL`, a named receipt), `Anchor` (the head and length a hash chain cannot hold about itself), and the **two-party rule** in `Command` — the proposer may not be the co-signer, on every mutation. 127 tests. Full disposition: [`phases/PHASE-3-RESULTS.md`](phases/PHASE-3-RESULTS.md).

**Added 2026-07-26, Phase 4** (`e6a0529`): `Store` (durable, append-only, the **only** module that touches disk; append-only enforced *before* the write), `Run` (immutable identity distinct from its execution record; `planned_n` and `stopping_rule` hashed into the identity so neither can be declared or lowered after the numbers are seen), `Pair` (exactly one differing variable, or `VOID` and unclaimable). 211 tests. Full disposition: [`phases/PHASE-4-RESULTS.md`](phases/PHASE-4-RESULTS.md).

**Added 2026-07-26, Phase 5** (`915bfbb`): `Witness` (corroboration across two failure domains, one of which refuses the writer's key), the **first real Control Plane ledger** — seven entries recording this programme's own history, adverse results included — and the **`control-plane` Gaia seat**, carrying every entry's exact bytes and deriving nothing from them.

**Added 2026-07-26, Phase 6** (`d524ad1`): `Room` (`green → clean → sterile`, every refusal naming each unmet condition and leaving the room untouched) and `Key` (two **distinct parties** with an **operator** among them). Receipts must exist **on disk** and are hashed into the transition. Leaving is gated too. There is **no override to call** — F21 is satisfied by absence, not refusal.

**Not built:** `Scene` and the lab view. **No verdict has been authored by this body about any real scientific claim** — the vocabulary exists and refuses correctly; it has adjudicated nothing.

**First write to canonical evidence, 2026-07-25** (Phase 3 item 3.1, operator-authorised): eleven superseding rows appended through `GateRow.supersede/2`, correcting `pre_registration_path: null` to `""`. No verdict changed; the tally is identical. **The mutation was not recorded in a Control Plane ledger entry** — `Ledger` has structure but no persistence, so the audit trail is a git commit and a receipt, which is the mechanism this body exists to replace. That gap is a Phase 4 build item.

**Two limitations that ride with what is built.** First: a local anchor cannot outrank a local writer. `Store` persists the anchor, so truncation is now caught **in practice** across restarts, against loss, corruption and accident — but **not** against a tamperer with write access to the store directory, who truncates the ledger and rewrites the anchor to match. A test performs that attack and asserts it succeeds. Phase 5 item 5.1 puts the anchor out of the writer's reach. Second: **the Control Plane can now record its own mutations and has not yet done so.** Capability is not practice; no Control Plane ledger has been persisted in anger. Phase 5 item 5.2 writes the first real one. And the canonical ledger **violated its own schema in twelve places** (`pre_registration_path: null`, rows 112–123). **Remedied 2026-07-25** by eleven superseding rows — eleven, not twelve, because one gate accounts for two violations. Append-only means the twelve originals remain at 112–123 and remain non-conformant forever; conformance is now true of the **effective state**, the last row per gate name, and only that claim is made.

### 3.3 Gaia — BUILT

`viewer/gaia/**`, HTTP `:8096`, mirror read-only MCP, running on THINKER.

**Live-audited 2026-07-25** (not taken from `GAIA.md`, which is stale at 85 signals): **308 signals**, **0 provenance-incomplete**. Seats: `gates 197 · sessions 25 · infra 24 · gaia-self 15 · studio 11 · colony 9 · organic-operator 8 · science 7 · drift 5 · repo 4`. The documented `relay` seat is not live; `organic-operator` is live and undocumented. Envelope shape is `{schema_version, envelope{...}, result{signals:[...]}}` — signals are nested under `result`, not top level. `gaia-boot-persistent` is **PASS** (ledger: `PARTIAL → PARTIAL → PASS`, closed on the real 2026-07-14 reboot).

**Eight drift signals are live** (five at the 2026-07-25 audit, three added the same day), all `equal=false`. The original five: `drift.fqdn_cjs` (absent), `drift.gate_row_schema_path` (declared_vs_observed), `drift.resolver_planned` (declared_vs_observed), `drift.git_dirty_vs_clean` (snapshot_vs_live), `drift.self_caps_doc_vs_served` (self). The mechanism [ADR-0002](decisions/ADR-0002-gaia-projects-never-computes.md) depends on is not speculative — it is running.

Added 2026-07-25: `drift.replica_ledger.*`, one per chip replica of the gate ledger — canonical digest read live against each replica's digest as captured. **These are the only like-for-like comparisons on the platform** (hex digest against hex digest), so `equal` there means what a reader thinks it means. Built after a stale replica fooled an audit into reporting 191 rows and no FAIL when canonical held 195 and one. Capture is agent-driven via `viewer/gaia/replica_ledger_probe.cjs` — Gaia is not an ssh client and mirrors the capture rather than fabricating it.

**GAIA LAW.** Gaia shows only direct signals with provenance. It never summarizes, represents, editorializes, scores, ranks, narrates, or authors a verdict. A raw signal losslessly projected is allowed. A count, percent, rank or rollup **that Gaia itself computes** is a build defect, even if it looks harmless.

A source's *own* computed verdict — a gate row's `PASS|PARTIAL|FAIL|WITHHELD|PENDING`, a source's own "count 3" bytes — is carried **verbatim with that source as locator**. That is projection, not derivation.

**Fences.** Read-only over everything. **G-PA**: never triggers an outward action, never holds a stream key; the HTTP surface has no mutating route by construction and no MCP tool is effectful. Claim fence: carries verdicts verbatim, never converts a behavioural row into an awareness claim. No IP literals in `viewer/gaia/*` — hosts derive from the infra registry.

**Consequences for this design:**
1. The Control Plane must author verdicts, because Gaia cannot.
2. The Control Plane must write receipts Gaia can project **verbatim** — no field may require Gaia to compute anything.
3. Drift is reported by Gaia and resolved by the Control Plane. Never the reverse.

### 3.4 The HUD — BUILT

`UNI.Hud.Service` (JSON, loopback `127.0.0.1:8100`, not LAN-reachable) + `UNI.Hud.Widget` (native WPF, always-on-top, `WindowChrome`). No HTML, no browser page.

**Law: never fabricates a state.** Stale, missing or unreachable renders `SYNCING` — *"we do not know" is not "off"*. Every value traces to a named upstream field and carries a `source`. Sparklines for continuous magnitudes only; binaries render as pills. Colony fps flat = FROZEN even while every process reports up.

---

## 4. What already exists that the lab looks through

### 4.1 UNI.Minecraft's own surfaces

The colony carries a complete observation and production stack. The lab **looks through these and never reimplements them**.

| surface | what |
|-|-|
| Control center `:8098`, air `:8097` | Live-TV vision mixer: `preview take cut cue projector camlayout overlay music watermark voice clip thumbs devices endpoints fanout role share unifeed preflight broadcast_test telemetry slotstates golive offair` |
| Glass cockpit | `uni-cockpit-kiosk.service` — `cage` + `chromium --kiosk` on tty1 serving `/glass/` |
| Overlooker | Omniscient per-tick world view; `world.js` THREE god-view with terrain, shadows, water, fog, stars, glowing avatar + trail; **Markov-blanket monitor** re-derives per tick that the agent received only the opaque observation |
| Director cam `:3020` | prismarine colony cam, raw 3D feed |
| `/stream` | Director third-person follow-cam on the star agent; scene banner, lower-third caption + ticker, health/food/tension cards; shared Q&A from any device |
| `overlay_server :8099`, `/broadcast` | overlay pages + one-GPU-Chrome composite for one dumb encoder |
| OBS scenes | `Colony Live`, `Colony Cam`, `Mind Cockpit`, `Broadcast`; the colony scene carries an honest gate ticker |

### 4.2 The evidence store

`evidence/gates.ndjson` — append-only, **206 rows / 109 unique gates** (canonical, after the 2026-07-25 schema-conformance correction appended 11 superseding rows). Current tally **92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING**; the FAIL is `nursery-fenced-red-stocked`, falsified 2026-07-19 (F1 and F3 both fired), claim fence intact. Per row: `schema_version`, `name`, `phase`, `pass_condition`, `falsifies_condition`, `receipt_path`, `verdict`. Verdicts `PASS | PARTIAL | FAIL | WITHHELD | PENDING`.

### 4.3 The language faculty

`SP.Brain.Narrator` — English, Mandarin, Hindi, Spanish, Arabic with **no language model**; gates 14/15 forbid any neural layer. Structure from active inference over designed priors; surface from authored lexicon + per-language clause templates. Held to a published arithmetic grade-4 rubric (`grade = 2.0 + 1.2·(mean_clauses − 1) + 0.15·(mean_words − 6)`). Deterministic per cast. Declared limits: English self-certified; Arabic (nominal sentences, case) and Hindi (gender) want native-speaker review.

Any Latin semantic anchor or IPA layer **extends this faculty** and may not introduce a neural dependency.

---

## 5. Domain model

Names reuse `gates.ndjson` where it already has one. New entities are added, never substituted.

```
Actor        id, kind{human,agent,service,reviewer,external}, role, scope, identity_evidence
Project      id, name, world_ref, gate_namespace, fences[]
Experiment   id, project_id, question, claim_under_test, protocol_ref, controls[],
             falsifier, gate_id, owner
Gate         name, phase, pass_condition, falsifies_condition, receipt_path, verdict,
             registered_at, registered_by, prereq_gates[]
Run          id, experiment_id, arm{treatment|control}, pair_id, code_identity,
             env_identity, inputs[], params, seeds, started_unix_ns, ended_unix_ns,
             status, outputs[], logs[], receipt_id
Arm          run_id, differing_variable   -- exactly one per pair, or the pair is VOID
Observation  id, run_id, method, captured_at, units, calibration, uncertainty,
             source{RCON|probe|collector}, raw_ref
Derivation   id, source_observation_ids[], formula, assumptions, units, code_ref,
             output, independent_recompute
Decision     id, subject{gate|release|room|claim}, reviews[3], keys[], evidence[],
             result, residual_uncertainty, reversibility, authored_by, authored_at
Receipt      id, decision_id, commit, artifacts[{path,sha256}], log_paths[], reproduce_cmd
Room         id, kind{green,clean,sterile}, entry_conditions[], exit_conditions[],
             occupancy, manifest_ref
Key          id, holder, authority, scope, issued_at, expires_at, single_use, decision_ref
LedgerEntry  seq, utc, unix_ns, actor, role, prior_state, transition, authorization,
             evidence[], resulting_state, hash, prev_hash
```

**Truth class** is carried on every renderable and every claim:
`OBSERVED | STRUCTURAL_RECONSTRUCTION | REDUCED_MODEL | DERIVED | SIMULATED | UNKNOWN`

**Evidence class** is carried verbatim from the source when it declares one, else `C`: `A | B | C | Sec | pending` (Gaia's vocabulary — do not invent a parallel one).

**Run status**: `DESIGNED | READY | RUNNING | COMPLETE | FAILED_RUN | VOID`.
`FAILED_RUN` is never a scientific negative. `VOID` means more than one variable differed.

---

## 6. Interfaces

### 6.1 Exposed by the Control Plane

All mutations are explicit verbs. **No GET actuates anything.**

```
GET   /api/cp/state                 current projection (pure read)
GET   /api/cp/gate/{name}           gate + its receipt refs
GET   /api/cp/run/{id}              run record
GET   /api/cp/ledger                append-only entries
GET   /api/cp/scene                 the compact scene for the lab renderer

POST  /api/cp/gate/register         {name, phase, pass_condition, falsifies_condition}
POST  /api/cp/run/start             {experiment_id, arm, pair_id}
POST  /api/cp/run/stop              {run_id, reason}          -- always available
POST  /api/cp/verdict/author        {gate_name, verdict, reasons[], receipt}
POST  /api/cp/room/request          {room_id, keys[]}
POST  /api/cp/stop-all              emergency stop, never blocked
```

Refusals return the missing precondition by name, never a generic error.

### 6.2 Consumed

Door `/api/door/state` and `/api/door/journey` (read-only). `uni-approvald` for the human co-sign. RCON for behavioural confirmation. Project runners. Existing guards: `claim_guard`, `numeric_provenance_guard`, `d5_distribution_guard`, `verify_gaia`, `gaia_lint`.

### 6.3 Emitted

Append-only ledger entries; receipts; `gates.ndjson` rows. All shaped so **Gaia projects them verbatim** — every value is source bytes or a source's own verdict, never something Gaia must compute.

---

## 7. State machines

### 7.1 Gate

```
(none) → REGISTERED → [run executes] → ADJUDICATED{PASS|PARTIAL|FAIL|WITHHELD} → (append)
                    ↘ PENDING (registered, not yet run)
```
Rules: registration must precede its run — prospectivity is decided by the commit graph, not prose. A gate may be **lowered** on receipts; that is the gate working. `PARTIAL` must name exactly which sub-claim holds. No percent scores. A verdict without a pre-registered gate is refused.

### 7.2 Run

```
DESIGNED → READY → RUNNING → COMPLETE → (observations → derivation → decision → receipt)
                          ↘ FAILED_RUN   (inspectable, never a negative result)
                          ↘ VOID          (>1 variable differed; re-run cleanly)
```
`actual_n = 0` → `NOT_RUN`. `0 < actual_n < planned_n` → `PARTIAL_NOT_ESTABLISHED` unless a prospective stopping rule was declared **before** the run. `actual_n > planned_n` is an **overrun** and must be flagged, not silently treated as complete.

### 7.3 Room and airlock

```
outside → [green: open] → green
green  → [2 keys]                          → clean
clean  → [2 keys + passing scan]           → sterile
sterile→ [contamination check + manifest recompute] → out
```
Every transition emits a ledger entry and a receipt. A failed condition names the missing receipt. **There is no override path.**

---

## 8. The lab view

### 8.1 Pipeline

```
command path (only writer)
   → projection builder (pure function of state, no side effects)
   → scene contract (every node carries truth_class, receipt_ref, evidence_class, captured_at)
   → renderer (THREE, on the T1000)
   → interaction (explicit verbs only)
```

A scene node **without** `truth_class` and `receipt_ref` renders as fog. It is not an error; it is the honest depiction of an unbacked assertion.

**Rendering constraint scope.** The flagellum *released product* forbids WebGL, GPU, Three.js, accounts and network. That fence is the flagellum's and still binds it. The **lab does not inherit it** — this platform already renders in THREE with shadows and ACES tone mapping. The flagellum's portal, viewed from inside the lab, still respects the flagellum's own build.

### 8.2 Render contract — acceptance criteria

A viewer must read epistemic status from a still screenshot with no text.

| truth class | material |
|-|-|
| `OBSERVED` | lit, solid, full shadow — **nothing else may look like this** |
| `STRUCTURAL_RECONSTRUCTION` | solid but visibly rebuilt; seams shown, not smoothed |
| `REDUCED_MODEL` / `DERIVED` | translucent — you see through a calculation |
| `SIMULATED` / rehearsal | visibly staged; green-room light follows the object wherever carried |
| `UNKNOWN` / `UNVERIFIED` | fog — never absent, never empty, never quietly clean |

**Two rules that stop the room from lying:**
1. No frame rate, glow, motion or particle may imply liveness. Liveness renders **only** from a real probe result. A frozen colony looks frozen while every process reports up.
2. Passing a gate renders the named behaviour and nothing more. **No material, light or room in this lab can depict awareness, experience or life.**

### 8.3 Spatial model

Operating floor (arrival, the run under way, verdict authorship, emergency stop). Rooms green → clean → sterile as volumes with two-key airlocks. World portals along one wall — look through to that world's own view, step through to work in it; a portal never re-derives its world's state and a down world renders dark. Gaia overhead: always in view, never enterable, no gesture reaches it.

Fog is walkable but nothing inside it may be acted on. You may stand in the unknown; you may not author a verdict from inside it.

**Refusal is the feature.** An action the evidence does not license is **absent, not greyed** — a greyed control still teaches that the action exists.

---

## 9. Storage, provenance, authorization

**Storage.** Append-only ledger; content-addressed artifacts (`path` + `sha256`); receipts beside their claims; `gates.ndjson` extended, never rewritten. Corrections are new entries. History is extended, never edited. Volatile captures stay out of git with a committed index and last-N retention.

**Run identity.** Every run records code identity, environment identity, inputs, parameters, seeds, start/end in Unix nanoseconds **and** UTC ISO-8601, exit code and output hashes. Determinism is proven by executing twice and comparing canonical bytes, not assumed. Known hazard on the platform: a self-hashing `runId` is **not** bit-reproducible across Node/V8 versions — that is a recorded red test, not a bug to hide.

**Authorization.** The agent proposes; only the operator co-signs; never its own change. Two keys for irreversible transitions, each with holder, authority, timestamp, scope, hashed decision record, single-use where appropriate. `uni-approvald` provides the human co-sign. **G-PA actions — go-live, transmission, distribution — are typed by hand and are not in this room.**

---

## 10. Failure modes and refusals

| condition | behaviour |
|-|-|
| verdict without a pre-registered gate | refused, gate named |
| more than one variable between arms | run marked `VOID`, result unclaimable |
| room entry condition unmet | door does not open, missing receipt named |
| optimizer non-convergence | scoring halts, **no artifact written** |
| array shape mismatch | raises before any aggregate is computed |
| overrun (`actual_n > planned_n`) | flagged, never silently `ELIGIBLE` |
| archive cannot be opened | `UNVERIFIED`, never clean |
| unscanned files in a distribution | fail-closed |
| frozen evidence hash drift | `STOP_FROZEN_EVIDENCE_DRIFT`, halt everything |
| a scene node without truth class | renders as fog |

---

## 11. Observability

Gaia gains **one new seat** projecting the Control Plane's ledger and receipts verbatim, exactly as `studio.doors.register` and `studio.doors.journey` already project the Door. Signals must satisfy the frozen key-set, carry `locator`/`captured_at`/`sha256`/`byte_len`, rehash exactly, and trip no forbidden token. **The lab is watched by the same organ it displays; it gets no privileged unhashed view of itself.**

Doc-vs-receipt disagreement emits a drift signal: `{a, b, relation, equal}`, both byte-sets verbatim, no severity, no diff-percent, no judgment.

---

## 12. Build sequence

| # | phase | body | gate |
|-|-|-|-|
| 0 | Access, baseline, resolve the two unknowns | — | frozen-evidence diff clean |
| 1 | Drift disposition and baseline truth — see [`phases/PHASE-1.md`](phases/PHASE-1.md) | — | **EXECUTED**: 4 of 5 drifts are structurally permanent; see [`phases/PHASE-1-RESULTS.md`](phases/PHASE-1-RESULTS.md) |
| 2 | `SP.ControlPlane.{Ledger,GateRow,Command}` in the **root zero-dep app** | Control Plane | a read spawns nothing; append-only proven |
| 3 | Gate registration + verdict authorship | Control Plane | each refusal proven by a red fixture |
| 4 | Gaia seat over the Control Plane | Gaia | `gaia_lint` FAILS a summarizing fixture first |
| 5 | Rooms + airlocks | Door | sterile without receipt does not open |
| 5b | **The lab view** | Control Plane | simulated vs observed distinguishable in a screenshot with no text |
| 6 | Flagellum method guards | flagellum | four mutation falsifiers |
| 7 | Resolve the gate-status drift | Control Plane + Gaia | drift surfaced, then reconciled |
| 8 | HUD projections | HUD | never fabricates; unknown is `SYNCING` |
| 9 | Language, education, broadcast | producer | no neural layer enters the language path |

One cure at a time. A second does not start until the prior is verdict-recorded.

---

## 13. Governance

Three perspectives per material decision, two adversarial: **Michael** (regenerative, operator, inside), **Veritas** (scientific falsifier — the existing *Devil's Pedagogue*), **Custos** (systems and release adversary — the existing *Custodian of the Boundary*). FE-touching changes first pass the lab council: math-breaker → architect → experimentalist → embodiment → AIF theorist.

A majority may choose among safe, evidence-supported options. A majority may **never** convert an unsupported claim into a fact, waive a safety requirement, erase historical evidence, declare inaccessible material reviewed, or advance a gate without its evidence.

---

## 14. Open questions — operator decisions

1. **`public/wadhwa-2022-derived-events.json` (487 KB) is served to every visitor** of the flagellum product: 1349 events with `eventId`, `motorId`, `nextStateN`, `jump`, and both `train` and `holdout` partitions. Recorded at `hierarchical-aif/reports/D12-INCIDENT-CONTAINMENT-REPORT.md:60-65` as *"flagged for principal review; not acted on unilaterally"* — a genuine conflict between the D5 burn and the truth contract's `OBSERVED` transparency requirement.
2. Transmission of the correction notice and the D5-safe successor archive — principal-gated, never an agent action.
3. ~~Which `build_*` tree is canonical~~ **RESOLVED 2026-07-25.** The canonical repo is `UNI.Minecraft` on **THINKER**, branch `gen2-runtime`, HEAD `cdf73c89` — byte-matching the `git.head` signal Gaia serves. The chip's `/home/uni/build_*` trees have no git and are deployed copies.
4. Where the **biological zoo** and **digital-DNA** bodies live. `find` across `/opt/uni`, `/var/lib/uni`, `/etc/uni` and `/home/uni` returned none — `NOT_LOCATED`.
5. Where the Control Plane's own code and this document should live, given (3).

---

## 15. Honest state

```
Colony source: DOWN, deliberately, for a generative-model rebuild.
Broadcast platform: PROVEN but IDLE. No program. G2 HELD. Nothing on air.
Gaia: RUNNING on THINKER. 308 signals, 0 provenance-incomplete, 8 live drift signals.
      gaia-boot-persistent PASS since the real 2026-07-14 reboot. GAIA.md is stale (says 85).
Door: RUNNING (:8090).   HUD: BUILT, native WPF, loopback-only by design.
Control Plane: PARTLY BUILT -> Ledger, GateRow, Command, Drift (75e2fc4) + Registry, Verdict,
      Anchor, two-party rule (8ff5591) + Store, Run, Pair (e6a0529). 211 tests.
      Witness, Room + Key, Scene NOT BUILT.
      No verdict authored about any real scientific claim.
      Tail truncation: caught in practice, AND the tamper attack now FAILS -- Witness
      corroborates across two domains, one being node2, which REFUSES every credential
      THINKER holds while answering on 22 (measured with the chip as negative control).
      Claim is tamper_EVIDENT, not proof: that refusal is a current config fact, not a
      structural law, so it is re-measured every capture.
      It HAS now recorded its own history: 7 entries, anchor 94485ef7..., attests clean.
      The anchor is NOT YET placed off-box -- that needs one operator co-sign through the
      approval-gated MCP, which is exactly what makes node2 a witness. Carried to PHASE-7 item 7.7.
Rooms: BUILT. green -> clean -> sterile, two distinct parties with an operator, receipts that
      must EXIST on disk and are hashed in. No override exists to call.
OPEN: one full-suite failure seen once, unreproduced and UNNAMED (PHASE-6-RESULTS §1).
      Likely the documented timing flake; likely is not established. PHASE-7 item 7.0 clears it.
Gate ledger: 206 rows / 109 unique. EFFECTIVE state conforms to gate_row.schema.json since
      2026-07-25 (11 superseding rows, operator-authorised, no verdict changed). The 12
      historical violations remain at rows 112-123 and always will -- the file is append-only.
Gate ledger EOL: MIXED (58 CRLF / 137 LF). A latent hazard for any future appender; one
      write was rolled back over it. Any appender must take the LAST line's terminator.
Lab view: NOT BUILT -> SpUiWeb.LabLive; ui/ proposes, the core authors (ADR-0007).
mix format --check-formatted: FAILS, pre-existing, lib/sp/brain/language.ex, CRLF. Not ours.
UNI.Minecraft surfaces: BUILT — control center, cockpit, Overlooker, Director cam, /stream, /broadcast.
Language faculty: BUILT, five languages, no neural layer.
Zoo / digital DNA: NOT_LOCATED.
Flagellum: P8 = FULL_PARITY = false; first unsatisfied rung P4, irreducibly external.
D12: incident NEGATIVE permanently; remediation gate PASS; successor archive built, NOT distributed.
Gates passed by this document: 0. It is a design and moves nothing.
No result has been elevated beyond the available evidence.
```
