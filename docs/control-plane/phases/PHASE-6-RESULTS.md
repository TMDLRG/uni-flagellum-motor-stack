# Phase 6 — RESULTS

**Status:** EXECUTED 2026-07-26 · **Plan:** [`PHASE-6.md`](PHASE-6.md)
**Repo:** `UNI.Minecraft` `gen2-runtime` — `915d3fa` (6.0) · `a26488c` (red) · `d524ad1` (green)
**Receipts:** `docs/receipts/control-plane/phase6_*`
**Bound honoured:** no row written to `evidence/gates.ndjson` · no P-level moved · `mc_test.exs` untouched · `mix.exs` unchanged.

---

## 0. Headline — item 6.0 found a false premise for the second phase running, and this one would have cost a rebuild

`authorization` had a single `granted_by`. **An airlock needs two keys.** The
ledger entry had nowhere to put the second one.

Had item 6.0 checked only the command vocabulary — which *is* extensible, and
whose extension is legitimate — I would have concluded the premise held, built
the whole Room, and hit the wall at F20.

```
Control Plane suite  286 tests, 0 failures  (47 failing at red)
Full suite           840 tests, 0 failures  — but see §2
```

## 1. ADVERSE — an unreproduced full-suite failure I cannot name

A full-suite run reported **1 failure**. The Control Plane suite was 286/0, so it
was outside this work. **I did not capture the output before re-running.** Two
subsequent full runs were 840/0.

So the honest statement is: **one unreproduced failure, test unknown, root cause
not established.** This suite has a documented flake history — `test_helper.exs`
carries a long note about five timing-sensitive tests in a danger band against
the wall-clock budget — and that is the *likely* explanation. Likely is not
established, and I am not recording it as a flake.

It is written into the green commit rather than dropped, because a failure you
cannot name is exactly the kind that gets quietly assumed away.

## 2. Disposition

| # | item | disposition |
|-|-|-|
| 6.0 | check premises, and name each check's blind spot | **DONE.** One false, one confirmed-with-correction, one confirmed-with-its-limitation. §3 |
| 6.1 | `Room` — `green → clean → sterile` | **DONE.** Refusals name every unmet condition and leave the room untouched. |
| 6.2 | **F19** — sterile entry demands an execution receipt | **DONE**, and the receipt must exist **on disk**. |
| 6.3 | **F20** — two valid keys | **DONE.** Distinct parties, operator required, refusal names which *kind* is missing. |
| 6.4 | **F21** — no override | **DONE**, as **absence**: there is nothing to call. |
| 6.5 | **F22** — sterile exit demands a contamination check and manifest recompute | **DONE.** Both, both on disk, both hashed. |
| 6.6 | place the anchor off-box | **NOT STARTED — operator-gated.** Carried to Phase 7. |
| 6.7 | inherited `mix format` | **STANDING KNOWN-FAIL**, unchanged. |

## 3. What item 6.0 found, and what each check could not see

| premise | result | the blind spot, stated in advance |
|-|-|-|
| approvals can carry a co-sign | **CONFIRMED** | I read the **stated categorical rule** and saw the queue refuse self-approval; I did **not** enumerate every tool and watch each one gate. A tool that quietly bypassed the queue would not have been caught. |
| the entry can record a room transition | **FALSE** | *"check the DATA-SPEC, not just the code"* — and that is what caught it. |
| nothing already models rooms | **CONFIRMED-WITH-CORRECTION** | *"a differently-named equivalent would not match a grep for 'room'"* — `stage` returned 117 files and `mode` 383, too broad to mean anything. Searching for the **shape** found `door_journey.cjs`. |

### The remedy, and why it is additive

`authorization.co_signers` — optional. The **seven entries already in the Control
Plane ledger carry none and still verify**, which is asserted by a test that
passed in *red* for exactly that reason. `DATA-SPEC.md` §1 is amended; this is the
**second** correction to that section, after Phase 3's `prior` rule.

### The shape is borrowed, not invented

`viewer/door_journey.cjs` already models a gated progression: every step is
`{id, label, check}` returning `{done, detail}`, and `detail` says *why not yet*
in words a reader can act on. `Room` mirrors it rather than creating a second
vocabulary for one idea.

It remains a **different body** ([ADR-0001](../decisions/ADR-0001-four-bodies.md)):
the Door's checks probe **live state** for a broadcast threshold; a room's
conditions are **receipts** for a lab one.

## 4. Decisions worth carrying

- **Two keys means two parties, with authority.** Distinct holders, at least one
  an operator. Two agent keys are one party wearing two hats. This is the third
  instance of one idea: `Command` refuses self-authorisation, `node2` refuses the
  writer's key, an airlock refuses one party.
- **A room's receipt must exist on disk** — deliberately the *opposite* of
  `Verdict`, where authorship must not depend on the file already being written.
  You may not stand in a sterile room on the strength of a receipt that is not
  there. Each is hashed into the transition, so a later edit is detectable.
- **Leaving is gated too.** A sterile room is sterile because what leaves it is
  accounted for.
- **F21 is absence, not refusal.** There is nothing to call. A refused control
  still teaches that the door is there — the same reasoning as the render
  contract's *refusals are absent, not greyed*.
- **An unmet condition is not a failure.** `conditions/4` is a pure read that
  always answers. A room nobody has scanned yet does not render red; a surface
  that paints it red teaches an operator to ignore red. Same honesty as
  `drift.control_plane_anchor_offbox` reading `absent`.

## 5. ADVERSE — three of my own tests were wrong and the code was right

- The bypass scan used `~w` with an **escaped space**, so `"def force"` split into
  two words and `"def"` matched every file — **the guard was firing on itself.**
  It also could not tell a definition from `writ.ex`'s prose *warning about*
  bypasses. Rewritten to target definitions.
- **Two tests read `history/1` as newest-first** when it is oldest-first, like
  `Ledger.entries/1`.

Corrected on the merits with the reasoning in the test, not silently flipped.

## 6. Falsifiers

| item | falsifier | fired? |
|-|-|-|
| 6.0 | an item built on an unchecked premise, or a check whose gaps were not named | **no** — and it caught the false premise |
| 6.1 | a room advances with a condition unmet, or refuses without saying which | no |
| 6.2 | the door opens without an execution receipt | no |
| 6.3 | one key admits | no |
| 6.4 | any bypass exists | no |
| 6.5 | exit succeeds unchecked | no |
| 6.6 | the anchor is placed by a path the writer could have taken alone | **not started** — that is the point |
| 6.7 | the reformat is buried in an evidence commit | no |

Mutation-tested: injecting a bypass, dropping the operator requirement, and
letting a receipt not exist each fail the guard that covers them.

## 7. Verification

| command | result |
|-|-|
| `mix test test/sp/control_plane` | PASS — 286 tests, 0 failures (47 red) |
| `mix test` | PASS — 840 tests, 0 failures · **§1: one earlier run showed 1 failure, unreproduced and unnamed** |
| `mix compile --warnings-as-errors --force` | PASS |
| `mix format --check-formatted` — Control Plane | PASS |
| `mix format --check-formatted` — repo-wide | **standing known-fail**, item 6.7 |
| `git diff mix.exs` | empty |
| `evidence/gates.ndjson` | `964ea25c…` unchanged |
| `verify_gaia` · `gaia_lint` · `verify_lint_bites` | PASS · 0 violations · still refuses a summarizing fixture |

## 8. Standing state

`P8 = FULL_PARITY = false`, first unsatisfied rung `P4`, irreducibly external.
`nursery-fenced-red-stocked` remains **FAIL**, falsified 2026-07-19.
**No verdict has been authored about any real scientific claim.**

## 9. Next act

[`PHASE-7.md`](PHASE-7.md) — the lab view and the rendering refusals. Phase 6 is
complete only because that plan exists (`ORCHESTRATE-RULES.md §1`).
