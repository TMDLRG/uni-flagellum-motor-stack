# ADR-0007 — The `ui/` read-only contract is clarified, not widened

- **Status:** Accepted — operator-authorised 2026-07-25
- **Date:** 2026-07-25
- **Deciders:** Michael (authorised the amendment), Veritas, Custos
- **Amends:** `ui/mix.exs:26-29` in `UNI.Minecraft` (branch `gen2-runtime`)

## Context

`ui/mix.exs:26-29` stated:

> This is the ONLY part of the repository that takes hex dependencies. The pure `stratified_palimpsest` core stays dependency-free; the UI consumes it as a path dependency and **only ever READS** its state / the evidence log.

That sentence is a deliberate fence and it has held. But the lab view ([ADR-0003](ADR-0003-control-plane-is-the-lab.md)) is a surface the operator authors verdicts from, and it renders in `ui/`. A surface that authors cannot be inside an app that never writes.

Two ways to resolve it: widen the fence, or make the surface a proposer. **Widening a written fence to fit a new feature is the failure mode this whole architecture is built to prevent** — it is how a control gets weakened one convenient exception at a time.

## Decision

The fence is **clarified, not widened.** The amendment states what the UI still may not do, then names the single new ability precisely:

- The UI still **NEVER** writes engine state, and **NEVER** writes `evidence/gates.ndjson` or any receipt.
- It gained exactly one ability: it may **SUBMIT a command** to `SP.ControlPlane`, which validates, authorises and performs every write itself.
- **The UI proposes; the Control Plane authors.**
- A LiveView that mutated a ledger, gate row or receipt directly violates this contract exactly as it did before.

Three consequences remain binding and are written into the amendment:

1. A polled read still actuates **nothing** — the Door's law, inherited verbatim.
2. The write path stays testable offline in the zero-dep core, with no Phoenix in the loop.
3. `ui/` remains the only place hex dependencies live.

## Consequences

**Positive.** The lab view can exist without any component gaining write access it should not have. The rule stays one sentence a reviewer can check: *does this code write, or does it ask?* Because the write path is in the zero-dep core, every refusal is provable by an offline, deterministic test.

**Negative.** A round trip is added: the surface must ask rather than act, so a verdict cannot be written from the LiveView process. That is the intent, not a cost to be optimised away.

**Neutral.** The amendment adds 13 comment lines to `ui/mix.exs`. No code, no dependency, no behaviour changed by this ADR alone.

## Alternatives considered

**Widen the contract to "reads and writes".** Rejected. It removes the only mechanical statement of the boundary and licenses any future LiveView to write anything.

**Leave the contract untouched and put the lab view outside `ui/`.** Viable — a fourth Mix project with its own endpoint. Rejected for now: it duplicates the Phoenix/LiveView/Bandit stack and the `world.js` hook machinery for one surface, and puts the room on the far side of a network boundary from the views it sits beside. Revisit if the command surface ever grows beyond proposing.

**Say nothing and just add the route.** Rejected outright. A silent contract change is indistinguishable from a violation, and the next reader would have no way to tell which it was.

## Falsifier

Any write to engine state, `evidence/gates.ndjson`, or a receipt originating from `ui/`. Any `ui/` code path that mutates canonical state without going through `SP.ControlPlane`. Any polled read in `ui/` that actuates something.

## Receipt

`ui/mix.exs` in `UNI.Minecraft` @ `cdf73c89` (branch `gen2-runtime`), amended in place — comment-only, 13 insertions, zero code change. The pre-existing dirty file in that tree (` M test/sp/brain/mc_test.exs`) is user-owned and was not touched.
