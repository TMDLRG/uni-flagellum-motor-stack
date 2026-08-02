# ADR-0008 — Human presence is required to go live

- **Status:** **PROPOSED — NOT ADOPTED. This document is not in force.**
- **Date:** 2026-07-27
- **Deciders:** Michael (has not yet ruled) — drafted by Claude under Phase 9 step 3.3
- **Amends:** nothing yet. It proposes a contract for `viewer/golive_guard.cjs` in `UNI.Minecraft`
  (branch `gen2-runtime`) and for `FAILURE-MODES.md` F31.

An ADR is a contract, and a contract amendment is `S5` — the operator's, never an agent's. This
was drafted by Claude on 2026-07-27 during Phase 9 step 3.3 so that there is something concrete to
rule on. **Until Michael adopts it, the code it describes is already built and already refusing,
which is the safe direction: the door is shut and nothing can open it.**

---

## Context

`FAILURE-MODES.md` declares:

> F31 | go-live is requested by an agent | refuse — it is typed by a human | falsifier: any agent
> path reaches go-live

Measured on 2026-07-27, before this step, the repository had **six code paths that reach
`StartStream`**, and between them **two string comparisons**:

| path | guard, before |
|-|-|
| `command_center.cjs` `/api/golive` | `confirm === "CONFIRM"` — on unauthenticated loopback |
| `studio.cjs` `golive CONFIRM` | `arg === "CONFIRM"` — on argv |
| `command_center.cjs` `/api/broadcast_test` | **nothing**, and public by owner directive |
| `obs_golive.cjs` | **nothing** |
| `obs_streamtest.cjs` | **nothing** |
| `obs_ctl.cjs` | **nothing** — and its request type comes from `argv`, so a search for the word `StartStream` cannot even see it |

A seventh was found while building the gate: `obs_req.cjs` sends an arbitrary
`{requestType, requestData}` read from a JSON file named on `argv`. It contains the word
`StartStream` nowhere and is a complete path to air.

`curl -X POST 127.0.0.1:8098/api/golive -d '{"confirm":"CONFIRM"}'` is one line. Four of the seven
paths did not ask for even that.

## Decision

**Go-live requires a human-presence token, and every path to air passes one chokepoint.**

`viewer/golive_guard.cjs` is the only function in this repository that may say yes. It refuses
unless a token exists that is:

1. **present** — absence is refusal, never a default-allow;
2. **fresh** — minted within 120 seconds, because it attests presence *a moment ago* and nothing
   longer;
3. **interactive** — minted by a desktop session, which excludes service sessions, scheduled
   tasks, remote shells and every script in this repository;
4. **single-use** — a nonce, spent on actuation, so a token cannot be replayed.

Refusal **throws** rather than returning. A refusal you can assign to a variable is a refusal you
can ignore, and that is precisely how five of the seven paths came to have no guard at all.

The typed `CONFIRM` is kept on both paths that had it. It stops a slip of the hand. It is no
longer the thing standing between an agent and the air.

## Claim level: `presence_evident`. NOT unforgeable.

This wording appears in the module, in every grant the guard issues, in the gate output, and in
the operator-facing prover. It is not a caveat in a design document.

**What it buys:** no headless agent, service-session process, scheduled task, remote shell, CI
job, or script in this repository can go live.

**What it does not buy:** an agent already running inside the operator's live desktop session,
with read access to the token, can replay it before it expires.

**And the harder limit, stated because it is the real one:** OBS WebSocket listens on
`127.0.0.1:4455` **with no authentication** — `obs_ctl.cjs`'s own header says so. Every path
guarded here is a path *through this repository*. Four lines of Node that never import the guard
reach the same actuator directly. **F31 binds this codebase's paths to air. It does not bind the
box.**

Closing that means enabling authentication on the OBS WebSocket server. That is a change to the
operator's studio configuration — `S2`, "any write to a host" — and is his.

## What is NOT decided here, and is the reason this needs a ruling

**The minting side does not exist.** The plan names the intended mechanism: a token minted by the
interactive-session WPF widget (the HUD). It is not built, and building it is what *opens* the
door — `S6`, "go-live, in any form".

So the current state is: **every path to air refuses, and there is no way to make one allow.** For
a guard, that is the correct resting state. It also means go-live is currently closed, by
construction, until Michael rules this ADR and the mint is built to match it.

## Consequences

- Go-live cannot happen until the mint exists. Deliberate. The door is not open by default and
  never was meant to be.
- `viewer/verify_golive_refuses_agents.cjs` discovers `StartStream` call sites from the filesystem
  and fails if any is unguarded, so an eighth path fails the gate on the day it is added rather
  than the day it is used. It also requires every OBS forwarder to be **classified** in a table a
  human has to read — internal builders are distinguished from externally-driven ones by
  declaration, not by a hidden regex.
- `viewer/prove_golive_refuses_me.cjs` is the operator's probe: an agent trying to go live down
  every path, refusing every time, exiting non-zero if any gets through.
- Presence tokens are machine-local and git-ignored. Committing one would make a live claim that a
  human is at this desk into a shared secret.

## The question this ADR is asking

1. Is `presence_evident` an acceptable claim level for opening a public broadcast, given it is
   explicitly not unforgeable against an agent inside the operator's own session?
2. Should OBS WebSocket authentication be enabled, which is the only thing that would make the
   guard bind the box rather than the codebase?
3. Who mints, and from where — the WPF HUD as planned, or another interactive surface?

Until these are answered, the guard refuses everything, and that is not a failure state.
