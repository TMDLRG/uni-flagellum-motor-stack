# ADR-0003 — The Control Plane is the lab; the room and the machinery are one body

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Michael, Veritas, Custos

## Context

Every existing surface either shows one world to an audience (the colony's control center, Director cam, `/stream`, `/broadcast`), or shows a machine's own state (the HUD), or shows signals (Gaia). None is a place to *work* across every project at once.

The operator's requirement: a UI *"a bit like a video game, that brings me and the world into the lab from a visuals and rendering perspective — this must be an immersive experience."*

A follow-on correction ruled out the easy answer: UNI.Minecraft's Overlooker is the **colony's** god-view of its own world, not the lab. The lab view does not exist and must be built.

## Decision

The Control Plane is **the lab**. Its user interface is an immersive rendered environment, not a dashboard, and it is a container **inside** the Control Plane rather than a separate body.

You author a verdict by standing at the thing you are ruling on. The run under way renders mid-room at the scale of a thing you can walk around, its pre-registered gate and falsifier beside it, before the run has an answer.

Rooms (green, clean, sterile) are volumes with two-key airlocks. Projects are portals: look through to that world's own view, step through to work in it. A portal never re-derives its world's state and never reimplements its renderer. Gaia is the sky — always in view, never enterable.

## Consequences

**Positive.** No split between "the tool that decides" and "the screen that shows deciding", so there is no state to synchronise between them and no second address. Spatial affordances carry epistemic meaning: a room that will not open *is* the refusal, with no dialog needed.

**Negative.** A rendered surface is heavier to build and test than a form. Mitigated by borrowing the platform's proven technique — a server pushing a compact scene per tick into a THREE renderer — rather than inventing one. Screenshot-based acceptance tests are required (see the render contract in `ARCHITECTURE.md` §8.2).

**Neutral.** The lab is watched by Gaia like anything else and gets no privileged view of itself.

## Alternatives considered

**A dashboard.** Rejected by the operator, and it fails the requirement: dashboards report, this body decides.

**Reuse the Overlooker as the lab.** Rejected explicitly by the operator. It is one world's view of itself; the lab spans every project and holds rooms, airlocks and authorship the Overlooker has no concept of.

**Lab view as a fifth body.** Rejected: it would put the room and its command path on opposite sides of a network boundary, re-creating exactly the split this decision removes.

## Falsifier

If the lab view can display a state the Control Plane's command path did not produce, or if authoring a verdict requires leaving the room, this decision has been violated.
