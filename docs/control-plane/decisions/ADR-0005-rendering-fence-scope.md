# ADR-0005 — The flagellum's CPU-only rendering fence does not bind the lab

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Michael, Veritas, Custos

## Context

`CLAUDE.md` in the flagellum repository states the released product "must remain CPU-only and must contain no LLM inference, GPU computation, WebGL, WebGPU, Three.js, analytics, accounts, or hidden network calls."

An earlier draft of this architecture applied that sentence to the whole platform and concluded that all biological visuals must be SVG or Canvas 2D, and that a rendered lab was forbidden.

That was a scope error. The sentence governs **one project's released product**. The platform it sits on already renders in THREE with shadows and ACES tone mapping on an NVIDIA T1000 — `ui/priv/static/world.js` is described in its own header as "a game-quality 3D god-view", and the broadcast path is explicitly GPU-composited.

## Decision

The fence is scoped to the artifact it names.

- The **flagellum released product** remains CPU-only, no WebGL, no GPU, no accounts, no network. Unchanged, and enforced by its own tests.
- The **lab view may render fully** — WebGL, GPU, shadows, tone mapping — because it is the operator's instrument on THINKER, not a published CPU-only artifact.
- The **flagellum's portal inside the lab** renders like any other portal, while the product behind it keeps its own build constraints. The portal shows that product; it does not relax it.

## Consequences

**Positive.** The lab can be the immersive environment the mission needs without weakening any published claim. Each artifact carries the fence it actually earned.

**Negative.** Two rendering regimes exist in one platform, so a contributor must know which artifact they are touching. Mitigated by the flagellum's own airtight build test, which fails if a forbidden runtime path enters its bundle.

## Alternatives considered

**Apply CPU-only everywhere.** Rejected: it forbids the lab the operator requires, and imposes on the platform a constraint that exists to make one *published scientific product* independently reproducible on any machine.

**Drop the flagellum fence to unify.** Rejected outright. That fence is a released-product guarantee and a claim-integrity control; loosening it to simplify an internal tool trades evidence for convenience.

## Falsifier

A GPU, WebGL, network or account dependency appearing in the flagellum released build. Its existing airtight build test is the mechanical check and must stay green.
