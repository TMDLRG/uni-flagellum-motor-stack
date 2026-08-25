# ADR-0011 — The Proto programme's execution constitution: source-of-truth, authority, and assumptions

- **Status:** **Accepted — operator-authorised 2026-08-06.** In force.
- **Date:** 2026-08-06
- **Deciders:** Michael (operator — signed all three sections as drafted), Claude Code (drafted)
- **Signed text:** `evidence/proto/PROTO-PROGRAM-INTAKE-v1-DRAFT.md` §3, §9, §10 — reproduced **verbatim** below. The operator's words were: *"sign all three as drafted."*
- **Class:** S5 — a contract amendment. **Performed by the operator, which is the authority S5 reserves.** An agent drafted it; an agent did not adopt it.
- **Prompted by:** Jules (`g-688a2a1cd58481919ef1e0b5e25053fd`), which when asked what it needs to design multi-agent work at this scale named all three of these as required inputs and named the first *"one of the most important inputs"*, adding that without it *"VERIFY cannot resolve conflicts; it can only identify them."* Full exchange: `evidence/proto/jules-exchange-001-program-intake.md`.

## Context

The Proto programme is 27 interdependent plans executed as multi-agent workflow runs, 5–15 agents at a time. Three things that a single-agent, single-chat estate could leave implicit become load-bearing the moment work is parallelised:

1. **What wins when two sources disagree.** The estate has never written this down. Without it, every agent that meets a contradiction resolves it by preference, and five agents produce five locally reasonable answers that fail at integration.
2. **What each agent is allowed to *cause*.** The estate has prohibitions — the ten STOPs — but no role×permission grid. Prohibitions stop the worst acts; they do not stop a builder approving its own work, or a reviewer quietly repairing an implementation and then passing it.
3. **What an agent may decide alone.** Without a stated policy an agent either escalates everything (useless) or escalates nothing (dangerous), and which one you get is a property of the model's mood that day.

**The estate has a live, measured case proving item 1 is not theoretical.** Three governing documents — `UNI-Flagellum/CLAUDE.md:107`, `UNI.Minecraft/CLAUDE.md:791`, and `docs/control-plane/LIMITATIONS.md:72` — currently declare the OBS WebSocket on `:4455` unauthenticated. **It was passworded on 2026-08-04** (`viewer/lib/obs_auth.cjs`, commit `4590111`, `auth_required = true`, 32-character password). All three statements sit inside the estate's own *"four things that must not be softened"* list. And the gate that exists to catch exactly this — `limitations-doc-cannot-drift` — holds `LIMITATIONS.md` against the `@limitation` blocks **in code**, so doc and code agree with each other while both disagree with the world, and **the gate stays green.**

That is the argument for the one controversial clause below.

## Decision

### 1 · SOURCE-OF-TRUTH HIERARCHY — highest wins

| # | Source | Note |
|---|---|---|
| 1 | **The operator's live ruling** | Spoken or typed, in-session. Supersedes everything. |
| 2 | **The ten STOPs** (`evidence/remediation/phase9_plan.json` `stops[]`) | Constitutional. An agent may never act past one, even under a ruling that did not name it. |
| 3 | **Measured live system state** | What a command returns *now*, with the command cited. |
| 4 | **`evidence/**` artifacts** (append-only ledgers, receipts, gate rows) | Immutable; hash-chained where applicable. |
| 5 | **Committed code** | What actually runs. |
| 6 | **Tests** | Authoritative for *intent*; may themselves be obsolete — a failing test is a finding, not automatically a defect. |
| 7 | **ADRs** | Binding until superseded by a later ADR or an operator ruling. |
| 8 | **`CLAUDE.md` and other governing documents** | **Deliberately demoted — see below.** |
| 9 | **`PROTO-SCRATCH-PLAN.md` §12.x corrections** | Later corrections supersede earlier sections of the same document. |
| 10 | **`PROTO-SCRATCH-PLAN.md` §0–§11** | Authored 2026-07-30, partly refuted. Source map: intake §5. |
| 11 | **Other prose documentation** | |
| 12 | **Agent inference** | Lowest. Never authoritative. |

**The deliberate inversion.** Governing documents rank **below** measured live state and committed code. This is unusual and it is intentional. **A document that has been wrong for two days, inside its own "must not be softened" list, while its own guard reads green, cannot outrank a live measurement.** The `:4455` case above is the demonstrating instance.

**This does not weaken governing documents; it changes what they are for.** They remain authoritative for *intent, policy and prohibition* — levels 2 and 7 sit above code precisely because the STOPs and ADRs are not descriptions of the world. What is demoted is a governing document's claim about **present factual state**, which is the only thing a live measurement can contradict.

**Subsidiary rulings, all signed:**

- **Repository behaviour overrides documentation.** Yes.
- **Tests may be obsolete.** A failing test is a finding, not automatically a defect.
- **A later plan may intentionally supersede an earlier one**, if it says so in its own text.
- **`PROTO-SCRATCH-PLAN.md` is MIXED authority** — normative, descriptive, historical and superseded material in one file. It must always be cited by section, never as a whole.

### 2 · ROLE × AUTHORITY MATRIX

| Role | Change code | Change requirements | Approve local work | Approve integration | Write `evidence/**` | Cross a STOP |
|---|---|---|---|---|---|---|
| **Orchestrator** | no | no | coordinates | coordinates | append-only, never `gates.ndjson` | never |
| **Builder** | declared write scope only | no | **no** | no | its own receipts only | never |
| **Reviewer** | no | no | recommend / reject | no | verdict rows only | never |
| **Integrator** | authorised fixes only | no | no | **yes** | integration receipts | never |
| **Michael** | yes | **yes** | yes | yes | yes | **only he can** |

**The three clauses that carry the matrix:**

1. **A builder may report LOCAL completion but may NEVER declare a plan integrated.** *(Register E — "the code works" ≠ "anything runs the code".)*
2. **A reviewer may not quietly repair the implementation and then approve its own work.** *(The four-proof cycle's M2/M4 independence requirement, arrived at independently by Jules.)*
3. **No role may cross a STOP under any instruction, including an operator instruction that did not name the STOP.** Crossing requires the operator naming the specific STOP.

### 3 · ASSUMPTION POLICY

**MAY INFER — no escalation, no disclosure.** Internal names where no canonical name exists; report and section formatting; ordering of independent read-only investigative steps; scratchpad organisation; commit-message prose (not content).

**MAY INFER — MUST DISCLOSE in the handoff.** Intent behind an ambiguous non-critical requirement; proposed internal abstractions; parallelisation boundaries; added test coverage for an explicitly stated requirement; local refactoring with unchanged public behaviour; interpretation of *descriptive* (not normative) source material; **which section of a mixed-authority document a requirement was drawn from.**

**MUST NOT INFER — stop and ask.** Anything touching a STOP; source precedence when two canonical sources disagree; security, privacy, credentials, or key lifecycle; destructive or irreversible operations; public interfaces and schemas; acceptance criteria; dependency direction; **whether a measurement was actually taken**; **whether a claim is OBSERVED versus derived**; anything that would soften, delete, or reword an adverse result.

**And the clause added for this estate specifically:**

> **An agent may never infer that a prior agent's claim is true. Every inherited number is re-measured, or carried explicitly as UNVERIFIED.**

This is D3 plus `cite-command-not-counterpart`. It is the single rule that would have prevented the most expensive failures on record — including, on the night this ADR was drafted, one by the agent that drafted it.

## Consequences

**Immediate and mechanical:**

- Every agent prompt in the Proto programme carries §1 as its precedence rule, §2 as its role contract, and §3 as its escalation boundary. They become the shared "execution constitution" block Jules recommends for limiting instruction drift across parallel workers.
- **`ADR-0008` (human presence for go-live) remains `PROPOSED — NOT ADOPTED`.** This ADR does not touch it and must not be read as adopting it.
- Three governing documents are now *demonstrably* below live measurement in precedence, which makes correcting the stale `:4455` claim a documentation repair rather than a contradiction of authority. **That correction is still the operator's**, because it softens a stated limitation inside the "must not be softened" list.

**What this ADR does NOT do:**

- It does not add, remove, or reinterpret any of the ten STOPs.
- It does not grant any agent a new capability. Every row of §2 is at or below what agents could already do; the matrix constrains rather than widens.
- It does not resolve the verdict-enum defect. `gate_row.schema.json` still cannot express `BLOCKED`, `NOT_RUN`, or `EXTERNAL_VALIDATION_REQUIRED` while `CLAUDE.md:267` declares all six valid. **That remains an open S5 amendment and is operator queue item 15** — and Jules independently requires `status: BLOCKED` in its own handoff schema, so the defect now has two independent witnesses.

**Falsifiers — how to tell if this ADR is being obeyed:**

- **F-ADR11-1.** An agent handoff that reports `COMPLETE` for a plan without an integrator's approval violates §2 clause 1. Detectable by joining handoff rows against integration receipts; a `COMPLETE` with no integrator row is a violation.
- **F-ADR11-2.** A reviewer's verdict row whose `agent_id` matches the builder's `agent_id` for the same task violates §2 clause 2. Detectable by self-join.
- **F-ADR11-3.** Any agent output asserting a factual number without a command in the same artifact violates §3's inherited-claim clause. Detectable by a linter over handoff `evidence.commands_run`.

**None of these three detectors exists yet.** They are named here so that the absence is recorded rather than assumed away, per the estate's own rule that a declared control with no enforcer must say so. Compare the measured STOP enforcement counts — `S7 0, S8 0, S9 0` — where three declared stops have no enforcer in any `viewer/*.cjs` and this was discovered only by grepping for it.

## Related

- `evidence/proto/jules-exchange-001-program-intake.md` — the exchange that named these three as required inputs.
- `evidence/proto/PROTO-PROGRAM-INTAKE-v1-DRAFT.md` — the packet these sections were drafted in.
- `evidence/proto/JULES-PIPE-MECHANISM.md` — how the exchange was conducted and captured.
- `PROTO-SCRATCH-PLAN.md` §12.14 — the operator's companion ruling deleting the two cycle-creating dependency edges, signed the same moment as this ADR.
- [ADR-0008](ADR-0008-human-presence-for-go-live.md) — PROPOSED, not adopted. Untouched by this ADR.
