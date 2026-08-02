# Phase 4 — Persistence, runs, and the pairing guard

**Status:** EXECUTED 2026-07-26 → [`PHASE-4-RESULTS.md`](PHASE-4-RESULTS.md) · **Written from:** [`PHASE-3-RESULTS.md`](PHASE-3-RESULTS.md), not from Phase 3's expectations
**Bound:** `SP.ControlPlane.{Store, Run, Pair}` in the **root zero-dep app** of `UNI.Minecraft`.
**This phase writes to disk for the first time. No row is written to `evidence/gates.ndjson`. No P-level moves.**
**Authorises:** [ADR-0006](../decisions/ADR-0006-sp-controlplane-naming-and-placement.md)

---

## 0. What Phase 3 changed about this phase

Four things, and two of them are inherited defects rather than new features.

1. **The Control Plane cannot record its own mutations.** Its first write to
   canonical evidence (item 3.1) went unrecorded in its own ledger, because
   `Ledger` has structure and no store. Its audit trail was a git commit and a
   receipt — **the mechanism this body exists to replace.** Item 4.1.
2. **The anchor is a mechanism, not a practice.** Item 3.6 landed `PARTIAL`:
   nothing holds an anchor across a process boundary, so tail truncation is
   detected only when someone happens to be holding one. Persistence is what
   closes it, so 4.1 and 4.2 are the same work seen twice.
3. **`evidence/gates.ndjson` has mixed line endings** — 58 `CRLF`, 137 bare `LF`,
   ending on `LF`. This already cost one rolled-back write. Item 4.7.
4. **Three pre-registered premises were wrong in Phase 3, all mine.** Every item
   below that rests on an assumption says so, and names the check that would show
   it false **before** the item is built on it.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 4.1 | `SP.ControlPlane.Store` — durable, append-only ledger persistence | a ledger written by one process is read back by another, byte-identical, and `verify/1` passes over it | a reload loses, reorders or silently repairs an entry |
| 4.2 | The anchor becomes a **practice** | the store writes an anchor alongside the ledger, and a reload that has lost its tail **fails to attest** | a truncated ledger reloads and is reported sound |
| 4.3 | `SP.ControlPlane.Run` — immutable run identity | a run records code identity, env identity, inputs, params, seeds, start/end in `unix_ns` **and** UTC, exit code and output hashes; the same run twice produces byte-identical canonical bytes | two runs of identical inputs differ, or a field can be edited after the fact |
| 4.4 | `SP.ControlPlane.Pair` — exactly one differing variable | two arms differing in one variable are comparable; two differences mark the run **`VOID`, unclaimable** | a two-variable result is claimable |
| 4.5 | Run status refusals **F13–F15** | `actual_n = 0 → NOT_RUN`; `0 < actual_n < planned` with no prior stopping rule → `PARTIAL_NOT_ESTABLISHED`; `actual_n > planned → OVERRUN`, flagged | a short run reads as complete, or an overrun reads as `ELIGIBLE` |
| 4.6 | Run failure refusals **F16–F18** | non-convergence halts **before** scoring and writes no artifact; mismatched array lengths raise **before** any aggregate; a crash records `FAILED_RUN` and stays inspectable | a non-converged fit produces a result file, or a crash is recorded as a scientific negative |
| 4.7 | The mixed-EOL hazard, made mechanical | any appender takes its terminator from the **last line** and proves the write afterwards; a test asserts this over the real ledger's shape | an appender infers the terminator from anywhere else |

**Standing expectation:** pure, offline, deterministic Elixir. **No hex
dependency.** No Phoenix. No change to `ui/`. `evidence/gates.ndjson` is **not
written** — item 3.1's authorisation was specific to it and does not carry
forward. Store fixtures live under a temporary directory, never in `evidence/`.

**A premise this phase rests on, named so it can be checked first:** that
`deps: []` can carry durable persistence with stdlib alone (`File`, `:erlang.term_to_binary`
or canonical JSON). If it cannot, that is `STOP_PROTOCOL_CHANGE_REQUIRED` and the
phase halts for a decision rather than quietly adding a dependency.

## 2. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/store_roundtrip_test.exs` | a ledger written and reloaded loses or reorders an entry |
| `test/sp/control_plane/store_append_only_test.exs` | a stored ledger can be rewritten in place rather than appended to |
| `test/sp/control_plane/store_anchor_in_practice_test.exs` | a reload that has lost its tail is reported sound |
| `test/sp/control_plane/run_identity_determinism_test.exs` | the same run twice produces different canonical bytes |
| `test/sp/control_plane/pair_one_variable_test.exs` | a two-variable comparison is claimable instead of `VOID` |
| `test/sp/control_plane/run_status_refusals_test.exs` | a short run reads as complete; an overrun reads as `ELIGIBLE` |
| `test/sp/control_plane/run_failure_refusals_test.exs` | a non-converged fit writes a result artifact |
| `test/sp/control_plane/appender_takes_last_line_terminator_test.exs` | an appender infers the terminator from anywhere but the last line |

Each is committed **red** with its failure output recorded, then made green.

**Standing procedure, earned in Phase 2 and confirmed in Phase 3:** a guard that
passes **vacuously** in red is not counted until a **mutation proves it bites**.
Any test that passes red is named in the receipt with the reason, and every one
that is a guard rather than a positive control is mutation-tested at green.

## 3. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted        # repo-wide FAILS on lib/sp/brain/language.ex — standing known-fail, PHASE-3-RESULTS §3
mix compile --warnings-as-errors --force
mix test
mix test test/sp/control_plane
git diff mix.exs                    # MUST be empty
sha256sum evidence/gates.ndjson     # MUST be unchanged — this phase writes no row
node viewer/gaia/verify_gaia.cjs
node viewer/gaia/gaia_lint.cjs
```

**Acceptance:** all eight red tests recorded red, then green, with every vacuous
guard mutation-tested. `mix.exs` unchanged. `evidence/gates.ndjson` byte-identical.
`lib/sp/brain/language.ex` and `test/sp/brain/mc_test.exs` untouched.

**Rollback:** additive under `lib/sp/control_plane/`. The store writes only to
paths it created; deleting the module and its directory leaves nothing behind.

**Stop conditions:** `STOP_TEST_REGRESSION` · `STOP_PROTOCOL_CHANGE_REQUIRED` if
durable persistence appears to need a hex dependency · `STOP_DESTRUCTIVE_ACTION_REQUIRED`
before any write outside the store's own directory.

## 4. Explicitly not in this phase

Rooms, airlocks and keys. The lab view. A new Gaia seat. Any Phoenix code. Any
change to `ui/`. Any write to `evidence/gates.ndjson`. Moving a P-level.

## 5. The three corrections Phase 3 made, carried so they are not re-made

1. **`prior` may be `null` at any `seq`.** `DATA-SPEC.md` §1's original rule
   confused the ledger's first entry with a subject's first entry. It survived
   because nothing tested it.
2. **Eleven corrective rows, not twelve.** Twelve violations across eleven gate
   names. A count repeated from memory is not a count.
3. **`lib/sp/brain/language.ex` is unformatted, not merely CRLF-terminated.** The
   symptom was read as the cause.

## 6. Exit condition — the phase ends by starting the next

**Phase 4 is complete only when `PHASE-5.md` exists, is committed, and is
pre-registered in this same form** — written from Phase 4's *observed* results.
Passing all eight tests is not completion.

`PHASE-5.md` must carry:

1. Every Phase 4 disposition, including each falsifier that fired.
2. Whether item 4.2 closed item 3.6's `PARTIAL` — is tail truncation detected **in
   practice** now, and what is the evidence?
3. Whether the store required a hex dependency, and if so what was decided.
4. Whether the Control Plane can now **record its own mutations**, and the first
   entry that proves it.
5. The Phase 5 build items — the Gaia seat projecting the Control Plane ledger
   verbatim, with `gaia_lint.cjs` made to FAIL a deliberately summarizing fixture
   **before** the real seat is added — each with a red test named before it is
   written.
6. Its own §6 requiring `PHASE-6.md`.

A phase that closes without its successor has stopped, and stopping is legitimate
only under a declared STOP condition.
