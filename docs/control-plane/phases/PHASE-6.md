# Phase 6 — Rooms, airlocks and keys

**Status:** EXECUTED 2026-07-26 → [`PHASE-6-RESULTS.md`](PHASE-6-RESULTS.md) · item 6.6 NOT STARTED (operator-gated, carried to PHASE-7 item 7.7); 6.7 remains a standing known-fail · **Written from:** [`PHASE-5-RESULTS.md`](PHASE-5-RESULTS.md), not from Phase 5's expectations
**Bound:** `SP.ControlPlane.{Room, Key}` in the **root zero-dep app** of `UNI.Minecraft`.
**No row is written to `evidence/gates.ndjson`. No P-level moves. No lab view.**
**Authorises:** [ADR-0006](../decisions/ADR-0006-sp-controlplane-naming-and-placement.md)

---

## 0. What Phase 5 changed about this phase

1. **A premise check can itself be incomplete.** Item 5.0 found three declaration
   sites for a Gaia seat; there were four. The fourth refused at construction and
   the seat threw on first render. So item 6.0 checks premises **and states how
   the check itself could be incomplete**.
2. **The two-party rule now has a second instance.** `Command` refuses a
   self-authorised mutation; node2 refuses the writer's key. An airlock's two keys
   are the same idea a third time, and should reuse the vocabulary rather than
   inventing one.
3. **A "not yet placed" state is honest and must survive.** `drift.control_plane_anchor_offbox`
   reads `absent` on purpose. Rooms will have the same shape — a condition not yet
   met is not a failure, and must not render as one.
4. **The anchor is still not placed off-box.** It needs one operator co-sign
   through the approval-gated MCP. Item 6.6.

## 0.1 Item 6.0 — check the premises, and check the check

| premise | check | how the check itself could be wrong |
|-|-|-|
| `uni-approvald` can carry a human co-sign for a key | call it read-only and read its queue shape | it may gate only *some* verbs; enumerate them rather than sampling one |
| a room transition can be recorded with the existing command vocabulary | read `Command`'s `@commands` and the `Ledger` entry shape | a transition may need a field the entry has no home for — check the DATA-SPEC, not just the code |
| no existing surface already models rooms | grep the platform before building a second one | a differently-named equivalent (a "stage", a "mode") would not match a grep for "room" |

**Recording the check is part of the item, and so is recording its blind spot.**
Five premises have been wrong on contact, and the sixth was a check that was
merely incomplete.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 6.0 | verify the premises above, and name each check's blind spot | each confirmed against a live read, with its own limitation stated | an item is built on an unchecked premise, or on a check whose gaps were not named |
| 6.1 | `SP.ControlPlane.Room` — `green → clean → sterile` | a transition is refused unless its conditions are met, and the refusal **names the missing receipt** | a room advances with a condition unmet, or refuses without saying which |
| 6.2 | **F19** — sterile entry demands an execution receipt | refused, naming the receipt | the door opens without it |
| 6.3 | **F20** — an airlock needs two valid keys | refused, naming **which** key is missing | one key admits |
| 6.4 | **F21** — there is no override | no bypass exists **to attempt**; a source scan finds no `force`, `override` or `skip` path | any bypass exists |
| 6.5 | **F22** — sterile exit demands a contamination check and a manifest recompute | refused without it | exit succeeds unchecked |
| 6.6 | **Operator-gated:** place the Control Plane anchor on the off-box custodian | the anchor exists on node2 via one approval-gated write, and `drift.control_plane_anchor_offbox` stops reading `absent` | the anchor is placed by a path the writer could have taken alone — which would destroy the property it is meant to prove |
| 6.7 | Inherited: `mix format --check-formatted` | still a standing known-fail with its reason, or reformatted in its own commit on its own terms | the reformat is buried inside an evidence commit |

**Standing expectation:** pure, offline, deterministic Elixir. No hex dependency.
No Phoenix. No `ui/` change. **No row into `evidence/gates.ndjson`.**

**Item 6.6 does not start without the operator**, and that is not an obstacle —
it is the mechanism. An anchor the writer could place alone would not be a
witness.

## 2. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/room_transition_conditions_test.exs` | a room advances with a condition unmet |
| `test/sp/control_plane/sterile_entry_needs_receipt_test.exs` | the door opens with no execution receipt |
| `test/sp/control_plane/airlock_two_keys_test.exs` | one key admits, or the refusal does not say which key is missing |
| `test/sp/control_plane/no_override_path_test.exs` | a bypass exists to attempt |
| `test/sp/control_plane/sterile_exit_contamination_test.exs` | exit succeeds with no contamination check |
| `test/sp/control_plane/room_not_yet_met_is_not_failure_test.exs` | an unmet condition renders as a failure rather than as not-yet-met |

Each committed **red** with its output recorded.

**Standing procedure, now three phases old:**
- a guard that passes **vacuously** in red is not counted until a **mutation
  proves it bites**;
- any test that passes in red is **named in the receipt with the reason**;
- a **canary that fires is replaced by what it was guarding**, never deleted;
- when a guard is **weakened**, the trade is written down in the test itself.

## 3. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted        # repo-wide FAILS on lib/sp/brain/language.ex — known, item 6.7
mix compile --warnings-as-errors --force
mix test
mix test test/sp/control_plane
git diff mix.exs                    # MUST be empty
sha256sum evidence/gates.ndjson     # MUST be unchanged
node viewer/gaia/verify_gaia.cjs    # 12 checks PASS, 11 seats
node viewer/gaia/gaia_lint.cjs      # 0 violations
node viewer/gaia/verify_lint_bites.cjs   # INVERSE: the lint must still refuse a summarizing fixture
node viewer/gaia/witness_probe.cjs  # the off-box refusal is RE-MEASURED, never assumed
```

**Acceptance:** all six red tests recorded red then green · every vacuous guard
mutation-tested · `mix.exs` unchanged · `evidence/gates.ndjson` byte-identical ·
Gaia still 12/12 · the witness still refuses the writer's key.

**Rollback:** additive under `lib/sp/control_plane/`. Item 6.6, if taken, is a
write to another host and is undone by the same approval-gated path — not by this
agent alone.

**Stop conditions:** `STOP_TEST_REGRESSION` · `STOP_PROTOCOL_CHANGE_REQUIRED` ·
`STOP_DESTRUCTIVE_ACTION_REQUIRED` before any write to the real gate ledger or to
any host — **item 6.6 begins in this state and does not leave it without a human.**

## 4. Explicitly not in this phase

The lab view. Any Phoenix code. Any `ui/` change. Any write to
`evidence/gates.ndjson`. Moving a P-level. Authoring a verdict about any real
scientific claim.

## 5. The corrections this programme carries

1. `prior` may be `null` at any `seq` — a creation event has no prior state. (P3)
2. Eleven corrective rows, not twelve — a count from memory is not a count. (P3)
3. `language.ex` is unformatted, not merely CRLF-terminated. (P3)
4. A run's identity is not its record — two executions differ, and must. (P4)
5. A local anchor cannot outrank a local writer. (P4)
6. Capability is not practice. (P4, and again in P5)
7. **A premise check can itself be incomplete** — three declaration sites, not
   four. (P5)
8. **A signature the writer can produce is not a witness.** (P5)

## 6. Exit condition — the phase ends by starting the next

**Phase 6 is complete only when `PHASE-7.md` exists, is committed, and is
pre-registered in this same form.**

`PHASE-7.md` must carry:

1. Every Phase 6 disposition, including each falsifier that fired.
2. Whether item 6.6 happened, and if so the one approval that carried it.
3. Whether any room condition can be met without a receipt — and the evidence.
4. The Phase 7 build items — the lab view, `Scene`, and the rendering refusals
   F24–F27 — each with a red test named before it is written, including the one
   that matters most: **a fixture with absent evidence must render as fog, and a
   simulated fixture must be distinguishable from an observed one in a screenshot
   with no text read.**
5. Its own §6 requiring `PHASE-8.md`.

A phase that closes without its successor has stopped, and stopping is legitimate
only under a declared STOP condition.
