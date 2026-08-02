# ADR-0001 — Four bodies, none collapsible into another

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Michael (operator), Veritas (scientific falsifier), Custos (systems and release adversary)

## Context

The platform has three always-on surfaces, stated verbatim in `docs/HUD.md`: *"The HUD is the third always-on surface, alongside The Door (`viewer/launcher.cjs` on `:8090`) and Gaia (`viewer/gaia/gaia_server.cjs` on `:8096`)."*

Steps 1–6 of the evidence spine — register a gate, run paired, observe, adversarial review, author a verdict, write a receipt — belong to none of them. They are performed by hand by whichever agent is working.

Two earlier drafts of this architecture collapsed bodies to make the design tidier. One declared "the HUD is the control plane". Another made the control plane Gaia-centred. Both were rejected by the operator, the second after days of work had to be reverted.

## Decision

There are **four** bodies, each with its own address, own law and own lifecycle:

| body | responsibility | may it act? | may it author a verdict? |
|-|-|-|-|
| The Door `:8090` | admission, release, keys, journey | yes, on a threshold | no |
| The Control Plane | runs the science; **is the lab** | yes, on the science | **yes — only this body** |
| Gaia `:8096` | projects signals with provenance | **no** | **no** |
| The HUD `:8100` | shows and carries | no | no |

## Consequences

**Positive.** Each body has a single reason to change. Gaia stays a credible witness precisely because it cannot act on what it reports. The Door's hard-won law — *a polled read never spawns anything*, burned in by two recorded spawn storms — is inherited rather than re-derived.

**Negative.** Four services to run, supervise and prove. More inter-body contracts. A reader expecting one "app" must learn the separation first, which is why it is the first thing in the README.

**Neutral.** The lab view is a container inside the Control Plane, not a fifth body — the room and the machinery are one body (see [ADR-0003](ADR-0003-control-plane-is-the-lab.md)).

## Alternatives considered

**One surface that does everything.** Rejected: it forces Gaia to act, which its own fences forbid by construction (`G-PA`: no mutating HTTP route, no effectful MCP tool).

**Three bodies, folding the Control Plane into the Door.** Rejected: the Door governs a threshold. Running experiments and authoring verdicts is a different responsibility with a different failure mode, and merging them puts science execution behind a door verb.

**Three bodies, folding the Control Plane into the HUD.** Rejected and previously attempted. The HUD is a display whose law is *never fabricate*; giving it authorship makes it the source of the state it displays, and there is then nothing left to check it against.

## Falsifier

If a body is found doing another body's job — Gaia computing a verdict, the HUD authoring state, the Door running a experiment — this ADR has been violated and the change is rejected regardless of how well it works.
