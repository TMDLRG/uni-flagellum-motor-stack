# ADR-0006 — The body is `SP.ControlPlane`, and it lives in the zero-dep core

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Michael (operator, decided the name), Veritas, Custos

## Context

An earlier draft placed this body in a Phoenix app with its lab view at `ui/lib/sp_ui_web/live/lab_live.ex`. A deeper inventory of the canonical repo (`UNI.Minecraft`, branch `gen2-runtime`, HEAD `cdf73c89`, on THINKER) showed that wrong on two counts.

**Both names were already taken, in this codebase, meaning different things:**

- `lib/sp/producer.ex:1-3` — *"The Producer UNI host — **the live show-running control plane**. A singleton GenServer that every beat assembles ALL telemetry…"*
- `lib/sp/lab.ex:1-3` — *"The Stratified Palimpsest **Hard-Science Lab** — a bounded, deterministic, zero-dependency set of pure physical/biochemical models…"* (bioenergetics, physics, planetary_data, radiation, solar_energy)

Building a third body under both names would collapse three distinct things — the failure this architecture exists to prevent.

**The placement violated a written contract:**

- `mix.exs:30-33` — the root app has **zero deps by design**, *"so that `mix test` is fully offline and deterministic (no hex fetch required)"*. Even `Jason` is deliberately absent: `test/gate_registry_integrity_test.exs:34` uses stdlib `JSON.decode/1` with the comment *"this repo is deliberately zero-dep, so Jason must not become available here"*.
- `ui/mix.exs:26-29` — *"the UI consumes it as a path dependency and **only ever READS** its state / the evidence log."*

A verdict-authoring surface had been placed inside the app contractually forbidden from writing.

## Decision

**Name.** The module namespace is **`SP.ControlPlane`**. It is free — `SP.Producer` uses the phrase only in prose, never as a module. The operator's word is kept, and the collision is resolved by explicit disambiguation in both directions rather than by renaming either existing thing:

- `SP.Producer` is the **show's** control plane — camera, narration, cast, broadcast.
- `SP.ControlPlane` is the **science's** control plane — gates, runs, verdicts, receipts, rooms.
- `SP.Lab` remains the **hard-science model namespace**. The room is `SP.ControlPlane.LabView` / `SpUiWeb.LabLive`, both free.

A one-line clarification to `SP.Producer`'s moduledoc is part of this work, not an afterthought.

**Placement.** `SP.ControlPlane.**` lives in the **root zero-dep app**: pure, offline, deterministic, stdlib `JSON` only, tested with the existing hand-rolled `SP.Prop` (`test/support/sp_prop.ex`). It owns `Ledger`, `GateRow`, `Command`, `Registry`, `Verdict`, `Run`, `Pair`, `Room`, `Key`. The lab view renders in `ui/` and **proposes**; every write is performed by the core. See [ADR-0007](ADR-0007-ui-contract-amendment.md).

## Consequences

**Positive.** The write path is testable offline with no Phoenix in the loop, matching the repo's strongest convention. Three bodies keep three names. Supervision has a proven slot — `SP.Show.Supervisor` (`rest_for_one`, permanent children, hosted by `SpUi.Application`, env-gated) is the pattern to follow.

**Negative.** Zero-dep means no JSON Schema library; `gate_row.schema.json` must be enforced by hand-written validation in Elixir. Mitigated by the fact that `test/gate_registry_integrity_test.exs` already does exactly this with stdlib `JSON`, and should be extended rather than duplicated.

**Neutral.** The name `SP.ControlPlane` will read oddly beside `SP.Producer`'s moduledoc until that one-line clarification lands. It lands in the same change.

## Alternatives considered

**A new top-level name to avoid the collision entirely** (`SP.Adjudicator`, `SP.Chamber`). Rejected by the operator: the body is the control plane and it is the lab; renaming it to dodge a prose collision loses the meaning the operator set.

**Put it in `ui/` with the rest of the web stack.** Rejected: violates the read-only contract, and makes the write path untestable without Phoenix and hex deps.

**A third Mix project.** Viable, and the fallback if the core ever needs a dependency. Rejected for now: the logic is pure and belongs with the engine it governs; a third project adds a boundary with nothing on the far side of it.

## Falsifier

If the core Control Plane requires a hex dependency, the placement was wrong. If authoring a verdict requires `ui/` to write a ledger, gate row or receipt directly, the placement was wrong. If a reader confuses `SP.Producer` with `SP.ControlPlane` after the disambiguation lands, the naming was wrong.
