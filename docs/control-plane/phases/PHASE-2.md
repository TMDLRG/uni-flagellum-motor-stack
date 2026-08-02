# Phase 2 — The ledger and the command path

**Status:** EXECUTED 2026-07-25 → [`PHASE-2-RESULTS.md`](PHASE-2-RESULTS.md) · **Written from:** [`PHASE-1-RESULTS.md`](PHASE-1-RESULTS.md), not from Phase 1's assumptions
**Bound:** first code of the Control Plane. `SP.ControlPlane.{Ledger,GateRow,Command}` in the **root zero-dep app** of `UNI.Minecraft`. **No verdict authored. No row appended to the real ledger. No P-level moved.**
**Authorises:** [ADR-0006](../decisions/ADR-0006-sp-controlplane-naming-and-placement.md), [ADR-0007](../decisions/ADR-0007-ui-contract-amendment.md)

---

## 0. What Phase 1 changed about this phase

Phase 1 found that **four of five drift signals compare different kinds of thing and can never converge**. That is not a documentation problem, and it reshapes Phase 2 in three ways:

1. **The Control Plane's own drift detection must compare like with like** — receipt-to-receipt, hash-to-hash — never prose to a file listing. Phase 1 is the worked example of how a comparison can be honest, mechanical, and still uninformative.
2. ~~**A new work item exists:** nothing detects chip-versus-canonical ledger drift.~~ **DONE 2026-07-25, out of phase order.** `drift.replica_ledger.*` now compares the canonical ledger digest against each replica's, agent-captured via `viewer/gaia/replica_ledger_probe.cjs`. Three replicas, all `DIFFERS`, none holding evidence canonical lacks. See item 2.7.
3. **`equal=false` is not evidence of staleness.** Any Control Plane surface that renders drift must show both sides, never a bare boolean.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 2.1 | `SP.ControlPlane.Ledger` — append-only, hash-chained | `append/2` links `prev_hash`; `verify/1` walks the chain; tampering any past entry fails verification | an entry can be edited or deleted with `verify/1` still passing |
| 2.2 | `SP.ControlPlane.GateRow` — build + validate | a row is validated against `production/schemas/gate_row.schema.json` in **hand-written Elixir with stdlib `JSON`**, no hex dep; `supersedes` chains a revision without mutating the superseded row | a row missing a required key, or with a verdict outside the enum, is accepted |
| 2.3 | `SP.ControlPlane.Command` — the only writer | every canonical mutation records actor, role, utc, unix_ns, prior, transition, authorization, evidence, resulting, hash | any write path exists that does not pass through `Command` |
| 2.4 | Inherit the Door's law | a read function performs no write and spawns nothing | a read has a side effect |
| 2.5 | Zero-dep proven | `mix test` runs offline with `deps: []` unchanged; `SP.Prop` used for property tests | a hex dependency is added to the root app |
| 2.6 | **Like-for-like drift** — `SP.ControlPlane.Drift` | compares only values of the same type (hash↔hash, verdict↔verdict) and refuses a cross-type comparison at construction | a comparison is constructed between a prose string and a command output |
| 2.7 | ~~Chip-vs-canonical ledger drift~~ | **CLOSED AHEAD OF THE PHASE, 2026-07-25.** Its falsifier — *"a seat is built before the decision is recorded"* — **fired**: the operator ruled "build the seat" and I built it the same hour. The ruling IS the decision being recorded, so the item is satisfied, but not in the order this plan pre-registered. Recorded rather than back-dated. | *(fired; see left)* |

**Standing expectation:** every item lands as pure, offline, deterministic Elixir with **no hex dependency and no Phoenix in the loop**. The real `evidence/gates.ndjson` is **not written** in this phase — all tests use fixtures in `test/fixtures/`.

## 2. Red tests, named before they are written

Per `LAB_PROTOCOL.md §II` and the flagellum's documentation-first TDD, each test is named and its failure mode stated **before** implementation:

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/ledger_append_only_test.exs` | editing entry *n* leaves `verify/1` passing |
| `test/sp/control_plane/ledger_chain_tamper_test.exs` | a truncated chain verifies |
| `test/sp/control_plane/gate_row_schema_test.exs` | a row with `verdict: "MOSTLY_PASS"` is accepted |
| `test/sp/control_plane/gate_row_supersedes_test.exs` | a revision mutates the row it supersedes |
| `test/sp/control_plane/command_is_only_writer_test.exs` | a write succeeds outside `Command` |
| `test/sp/control_plane/read_never_actuates_test.exs` | a read function mutates or spawns |
| `test/sp/control_plane/drift_like_for_like_test.exs` | a prose-vs-file-listing comparison is constructible |

Each is committed **red** with its failure output recorded, then made green. Red-then-green is proven, not asserted — where it is not achieved, that is stated rather than presented as compliance (`H-AIF-G3`'s standing rule).

## 3. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted
mix compile --warnings-as-errors --force
mix test                                   # offline; deps: [] unchanged
mix test test/sp/control_plane             # the new suite
git diff mix.exs                           # MUST be empty — no dependency added
node viewer/verify_gaia.cjs                # 12 gates PASS; 8 drift signals surfaced (5 original + 3 replica-ledger)
```

**Acceptance:** all seven red tests recorded red, then green. `mix.exs` unchanged. `evidence/gates.ndjson` byte-identical (this phase writes no row). `mc_test.exs` untouched. `verify_gaia.cjs` still passes `gaia-drift-surfaced`.

**Rollback:** the module is additive under `lib/sp/control_plane/`; delete the directory and its tests. Nothing existing is modified except the addition of a moduledoc disambiguation line to `SP.Producer` (ADR-0006).

**Stop conditions:** `STOP_TEST_REGRESSION` if any existing test breaks · `STOP_PROTOCOL_CHANGE_REQUIRED` if a hex dep looks necessary · `STOP_DESTRUCTIVE_ACTION_REQUIRED` before any write to the real ledger.

## 4. Explicitly not in this phase

Authoring a verdict. Appending to the real `evidence/gates.ndjson`. The lab view. Rooms and airlocks. A new Gaia seat. Any Phoenix code. Any change to `ui/`.

## 5. Exit condition — the phase ends by starting the next

**Phase 2 is complete only when `PHASE-3.md` exists, is committed, and is pre-registered in this same form** — written from Phase 2's *observed* results, not from this plan's expectations. Passing all seven tests is not completion.

`PHASE-3.md` must carry:

1. Every Phase 2 disposition, including each falsifier that fired.
2. The recorded decision on chip-vs-canonical drift (item 2.7) and what it implies.
3. The Phase 3 build items — `Registry`, `Verdict`, and the structural refusals from `ARCHITECTURE.md` §7.1 — each with a red test named before it is written.
4. Its own §5 requiring `PHASE-4.md`.

A phase that closes without its successor has stopped, and stopping is legitimate only under a declared STOP condition.
