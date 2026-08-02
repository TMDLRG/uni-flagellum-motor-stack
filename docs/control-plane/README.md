# Control Plane — architecture

**PART DESIGN, PART BUILT. This directory moves no P-level.** Phase 2 built the ledger and the command path; Phase 3 added registration, verdict authorship, the anchor and the two-party rule; Phase 4 added persistence, runs and the pairing guard; Phase 5 added the witness and the body's first real ledger of its own history; Phase 6 added rooms, keys and airlocks. Only the lab view remains. Live state and next act: [`RESUME.md`](RESUME.md), or UNI TRACK at `http://127.0.0.1:8102/`.

## How this is maintained

Architecture is **model-as-code**. There are no hand-drawn diagrams — see [ADR-0004](decisions/ADR-0004-model-as-code-not-svg.md) for why the SVGs that were here were deleted.

| file | role | edit when |
|-|-|-|
| [`workspace.dsl`](workspace.dsl) | **The model of record.** C4 in Structurizr DSL — typed people, containers, relationships, deployment nodes. One model, many views. | any element or relationship changes |
| [`views.md`](views.md) | **Projections.** Mermaid — renders natively in GitHub with no build step. Context, containers, deployment, evidence spine, three state machines, one sequence. | a view needs to show something different |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | **The prose the model cannot carry.** Contracts, domain model, interfaces, invariants, failure modes, acceptance criteria, build sequence. | behaviour or a contract changes |
| [`decisions/`](decisions/) | **Why.** ADRs in MADR format, each with a falsifier. | a consequential choice is made or reversed |
| [`DATA-SPEC.md`](DATA-SPEC.md) | **Shapes.** Ledger entry, receipt, gate row, scene node, drift comparison. | a field is added or a type changes |
| [`FAILURE-MODES.md`](FAILURE-MODES.md) | **Refusals.** 31 numbered, each written as a testable statement with its falsifier. | a new refusal is identified |
| [`ARCHITECTURE-AUDIT.md`](ARCHITECTURE-AUDIT.md) | **Proof.** Every claim checked against a live read, not another document. | the architecture changes |

**The rule:** if a relationship appears in a view but not in `workspace.dsl`, the model is wrong. The DSL is authoritative where the two disagree.

**Rendering the DSL** uses `structurizr-cli` + PlantUML, both **installed** (user-local, Temurin JDK 17). `bash render.sh` validates, exports and renders all five views into [`generated/`](generated/). `views.md` still exists because it renders anywhere with nothing installed.

## The one thing to read first

There are **four** bodies, and none may be collapsed into another ([ADR-0001](decisions/ADR-0001-four-bodies.md)):

| body | responsibility | acts? | authors a verdict? |
|-|-|-|-|
| **The Door** `:8090` · built | admission, release, keys, journey | on a threshold | no |
| **The Control Plane** · partly built | runs the science — **this is the lab** | on the science | **yes, only this body** — but it has not yet |
| **Gaia** `:8096` · built | projects signals with provenance | **no** | **no** |
| **The HUD** `:8100` · built | shows and carries | no | no |

Gaia may never act, so it cannot be a control plane. The Control Plane authors verdicts, so it can never be Gaia. Collapsing either into the other removes the witness that makes every claim checkable.

## Phases

Execution is phased, and **each phase document ends by requiring the next** — per `ORCHESTRATE-RULES.md §1`, writing a report or passing tests is not a stopping condition. A phase is complete only when its successor's plan exists, pre-registered in the same form.

| phase | status | ends when |
|-|-|-|
| [Phase 1](phases/PHASE-1.md) — drift disposition and baseline truth | **EXECUTED** → [results](phases/PHASE-1-RESULTS.md) | ✔ `PHASE-2.md` written and committed |
| [Phase 2](phases/PHASE-2.md) — the ledger and the command path | **EXECUTED** → [results](phases/PHASE-2-RESULTS.md) | ✔ `PHASE-3.md` written and committed |
| [Phase 3](phases/PHASE-3.md) — registration, verdict authorship, the anchor | **EXECUTED** → [results](phases/PHASE-3-RESULTS.md) · item 3.6 **PARTIAL**, 3.7 **known-fail** | ✔ `PHASE-4.md` written and committed |
| [Phase 4](phases/PHASE-4.md) — persistence, runs, the pairing guard | **EXECUTED** → [results](phases/PHASE-4-RESULTS.md) · both canaries fired | ✔ `PHASE-5.md` written and committed |
| [Phase 5](phases/PHASE-5.md) — the witness, the first real ledger, a Gaia seat | **EXECUTED** → [results](phases/PHASE-5-RESULTS.md) · item 6.6 carries one operator-gated write | ✔ `PHASE-6.md` written and committed |
| [Phase 6](phases/PHASE-6.md) — rooms, airlocks and keys | **EXECUTED** → [results](phases/PHASE-6-RESULTS.md) · one unnamed full-suite failure carried open | ✔ `PHASE-7.md` written and committed |
| [Phase 7](phases/PHASE-7.md) — the lab view, and a scene that cannot lie | PRE-REGISTERED, not executed | `phases/PHASE-8.md` is written and committed |

Each plan pre-registers its expected outcomes and falsifiers **before** execution (`LAB_PROTOCOL.md §II`). A `NOT_CLEARED` disposition with a named reason is a valid, complete outcome — not a failure to be tidied away.

## Decisions

| ADR | decision |
|-|-|
| [0001](decisions/ADR-0001-four-bodies.md) | Four bodies, none collapsible into another |
| [0002](decisions/ADR-0002-gaia-projects-never-computes.md) | Verdicts are authored by the Control Plane and projected by Gaia, never computed by Gaia |
| [0003](decisions/ADR-0003-control-plane-is-the-lab.md) | The Control Plane is the lab; room and machinery are one body |
| [0004](decisions/ADR-0004-model-as-code-not-svg.md) | Architecture is model-as-code; hand-authored SVG is not an architecture format |
| [0005](decisions/ADR-0005-rendering-fence-scope.md) | The flagellum's CPU-only rendering fence does not bind the lab |
| [0006](decisions/ADR-0006-sp-controlplane-naming-and-placement.md) | The body is `SP.ControlPlane`, and it lives in the zero-dep core |
| [0007](decisions/ADR-0007-ui-contract-amendment.md) | The `ui/` read-only contract is clarified, not widened |
| [0009](decisions/ADR-0009-gaia-is-the-authoritative-projection.md) | Gaia is the sole authoritative **projection** of platform state, never an author of it — `SP.ControlPlane` authors, the ledgers record, Gaia projects (**PROPOSED — NOT ADOPTED**) |

## Scope note

The Control Plane is platform-wide. `UNI-FLAGELLUM` is one project under it, alongside the UNI.Minecraft colony, metabolism, forage, motor and producer. This directory lives here because this is the version-controlled tree available; see `ARCHITECTURE.md` §14.3 and §14.5.
