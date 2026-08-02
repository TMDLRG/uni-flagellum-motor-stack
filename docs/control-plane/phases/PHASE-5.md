# Phase 5 — The witness: an anchor the writer cannot reach, and a seat that only projects

**Status:** EXECUTED 2026-07-26 → [`PHASE-5-RESULTS.md`](PHASE-5-RESULTS.md) · item 5.1's premise was FALSE until L2 was stabilised; 5.6 remains a standing known-fail · **Written from:** [`PHASE-4-RESULTS.md`](PHASE-4-RESULTS.md), not from Phase 4's expectations
**Bound:** `SP.ControlPlane.Witness` in the root zero-dep app, the **first real Control Plane ledger**, and one new **Gaia seat** in `viewer/gaia/`.
**Authorises:** [ADR-0002](../decisions/ADR-0002-gaia-projects-never-computes.md), [ADR-0006](../decisions/ADR-0006-sp-controlplane-naming-and-placement.md)

---

## 0. What Phase 4 changed about this phase

1. **The anchor is local, and a local anchor cannot outrank a local writer.** A
   test performs that attack and asserts it succeeds. Item 5.1.
2. **The Control Plane can record its own mutations and never has.** Capability
   is not practice — this programme has now made that distinction twice about the
   anchor, and it applies here unchanged. Item 5.2.
3. **Four pre-registered phrases have been wrong on contact, one per phase.** So
   every item below states the assumption it rests on and the check that would
   show it false, and item 5.0 exists.

## 0.1 Item 5.0 — check the premises before building on them

Before any code:

| premise | check | if false |
|-|-|-|
| a second machine on the mesh can hold an anchor the writer cannot reach | reach it read-only and confirm the writer has no credential to it | fall back to a signed anchor and record why |
| `gaia_lint.cjs` will actually fail a summarizing seat | **write the summarizing fixture and watch it fail, before writing the real seat** | the lint is decorative and its repair is this phase, not the seat |
| Gaia's seat pattern admits a new source without changing GAIA LAW | read `organic-operator` and `science` as the worked examples | `STOP_PROTOCOL_CHANGE_REQUIRED` |

**Recording the check is part of the item.** A premise assumed is a premise that
turns out wrong at the worst moment.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 5.0 | Verify the three premises above | each confirmed against a live read, or the phase re-plans | an item is built on an unchecked premise |
| 5.1 | `SP.ControlPlane.Witness` — an anchor the ledger's writer cannot reach | the store's anchor is mirrored somewhere the writing process has no write credential for; the tamper attack from Phase 4 now **fails** | the tamper attack still succeeds, or the witness lives where the writer can rewrite it |
| 5.2 | **The first real Control Plane ledger** — record this programme's own history | phases 2–5 land as entries, persisted and anchored, each with actor, authority, prior, resulting and evidence; `Store.attest/1` passes over it | the ledger is a demo fixture rather than the real record, or it is written by hand |
| 5.3 | `gaia_lint.cjs` proven to bite **before** the seat exists | a deliberately summarizing fixture (a `total` field, a rank, a computed count) makes `gaia_lint` **FAIL**, recorded red | the lint passes a summarizing fixture — in which case the lint is the defect and the seat waits |
| 5.4 | A Gaia seat projecting the Control Plane ledger **verbatim** | every signal carries locator, ISO `captured_at`, sha256 and byte length; `verify_gaia` still passes 12/12; the seat is declared in `caps.cjs`, the signal enum and `GAIA.md` | any Gaia-derived count, rank, rollup or verdict appears |
| 5.5 | The seat surfaces the residual, not just the state | if the witness disagrees with the local anchor, that is a **drift signal** with both sides carried, never a bare boolean | a disagreement is rendered as a single true/false |
| 5.6 | Inherited: `mix format --check-formatted` | still a standing known-fail with its reason, **or** `lib/sp/brain/language.ex` is reformatted in its own commit proposed on its own terms | the reformat is buried inside a Phase 5 evidence commit |

**Standing expectation:** pure, offline, deterministic Elixir for `Witness`. No
hex dependency. No Phoenix. No `ui/` change. **No row is written to
`evidence/gates.ndjson`** — item 3.1's authorisation was specific to it and does
not carry forward. Any gate row this phase would like to write is **proposed to
the operator**, not appended.

**GAIA LAW is not negotiable here.** The seat projects; it never computes. A
source's own verdict carried verbatim is projection. A count Gaia computes is a
build defect even if it looks harmless.

## 2. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/witness_out_of_reach_test.exs` | the tamper attack from Phase 4 still succeeds with a witness present |
| `test/sp/control_plane/witness_disagreement_is_two_sided_test.exs` | a witness/anchor disagreement reduces to a boolean |
| `test/sp/control_plane/control_plane_ledger_is_real_test.exs` | the recorded ledger is a fixture, not this programme's actual history |
| `viewer/gaia/fixtures/summarizing_seat_fixture.cjs` (+ lint run) | `gaia_lint` PASSES a fixture carrying a computed total |
| `test/sp/control_plane/seat_projects_verbatim_test.exs` | a projected signal differs from its source bytes |

Each committed **red** with its output recorded. **Standing procedure:** a guard
that passes vacuously in red is not counted until a mutation proves it bites, and
any test that passes red is named in the receipt with the reason.

**And a new standing rule, earned in Phase 4:** a canary that fires is
**replaced by what it was guarding**, never deleted. Deleting a canary is how a
limit quietly stops being tracked.

## 3. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted        # repo-wide FAILS on lib/sp/brain/language.ex — known, item 5.6
mix compile --warnings-as-errors --force
mix test
mix test test/sp/control_plane
git diff mix.exs                    # MUST be empty
sha256sum evidence/gates.ndjson     # MUST be unchanged — this phase writes no row
node viewer/gaia/gaia_lint.cjs      # 0 violations, AND proven to fail a summarizing fixture (5.3)
node viewer/gaia/verify_gaia.cjs    # 12 checks PASS, including every-emitted-seat-declared
```

**Acceptance:** all five red tests recorded red then green · every vacuous guard
mutation-tested · `mix.exs` unchanged · `evidence/gates.ndjson` byte-identical ·
`verify_gaia` still 12/12 with the new seat declared in all three places ·
`gaia_lint` 0 violations **and** demonstrated to fail a summarizing fixture.

**Rollback:** `Witness` is additive. The Gaia seat is additive and removable from
`collectors.cjs` plus its three declarations. The Control Plane ledger written by
5.2 is **append-only and is not rolled back by deletion** — a correction is a
further entry, which is the discipline working.

**Stop conditions:** `STOP_TEST_REGRESSION` · `STOP_PROTOCOL_CHANGE_REQUIRED` if
the seat cannot be added without changing GAIA LAW · `STOP_DESTRUCTIVE_ACTION_REQUIRED`
before any write to the real gate ledger or to any host the witness lives on.

## 4. Explicitly not in this phase

Rooms, airlocks and keys. The lab view. Any Phoenix code. Any `ui/` change. Any
write to `evidence/gates.ndjson`. Moving a P-level. Authoring a verdict about any
real scientific claim.

## 5. The corrections this programme has accumulated, carried so they are not re-made

1. **`prior` may be `null` at any `seq`** — a creation event has no prior state
   wherever it lands. (Phase 3)
2. **Eleven corrective rows, not twelve** — a count repeated from memory is not a
   count. (Phase 3)
3. **`language.ex` is unformatted, not merely CRLF-terminated** — the symptom was
   read as the cause. (Phase 3)
4. **A run's identity is not its record** — two executions differ, and must.
   (Phase 4)
5. **A local anchor cannot outrank a local writer.** (Phase 4)
6. **Capability is not practice** — said twice about the anchor, and true again
   about the ledger. (Phase 4)

## 6. Exit condition — the phase ends by starting the next

**Phase 5 is complete only when `PHASE-6.md` exists, is committed, and is
pre-registered in this same form** — written from Phase 5's *observed* results.

`PHASE-6.md` must carry:

1. Every Phase 5 disposition, including each falsifier that fired.
2. Whether the tamper attack now **fails**, and where the witness actually lives.
3. Whether `gaia_lint` was **proven** to bite before the seat was added — and if
   it was not, what was done about the lint.
4. The first Control Plane ledger's digest and entry count, and whether
   `Store.attest/1` passes over it.
5. The Phase 6 build items — rooms, airlocks and keys, F19–F22 — each with a red
   test named before it is written.
6. Its own §6 requiring `PHASE-7.md`.

A phase that closes without its successor has stopped, and stopping is legitimate
only under a declared STOP condition.
