# Phase 2 — RESULTS

**Status:** EXECUTED 2026-07-25 · **Plan:** [`PHASE-2.md`](PHASE-2.md) (pre-registered before execution, not edited after)
**Repo:** `UNI.Minecraft` `gen2-runtime` — red `47d0ef9`, green `75e2fc4`
**Receipts:** `docs/receipts/control-plane/phase2_red_2026-07-25.md` · `…_green_2026-07-25.md` (in `UNI.Minecraft`)
**Bound honoured:** no verdict authored · no row appended to the canonical ledger · no P-level moved · `mc_test.exs` untouched · `mix.exs` unchanged.

---

## 0. Headline — the code landed, and it immediately found something wrong with the ledger it was written to serve

All seven pre-registered tests were committed **red** with their failure output
recorded, then made green. 61 tests, 0 failures. The full suite is 615 tests,
0 failures.

But the interesting result is not the green. **Writing the schema validator by
hand surfaced twelve rows in the canonical gate ledger that violate the schema
the ledger is judged by, and that no existing guard catches.** That is what the
Control Plane is for, and it happened on the first day it could compile.

## 1. Disposition of every pre-registered item

| # | item | disposition |
|-|-|-|
| 2.1 | `Ledger` — append-only, hash-chained | **DONE**, with a stated limitation: `verify/1` cannot detect tail truncation. `verify/2` takes an out-of-chain anchor; nothing holds one yet. |
| 2.2 | `GateRow` — build + validate, `supersedes` without mutation | **DONE**. Hand-written against `gate_row.schema.json`, stdlib `JSON` only. Supersession follows the *observed* ledger convention (reuse the name, list it in `supersedes`) rather than an invented one. |
| 2.3 | `Command` — the only writer | **DONE**, by two guards: a runtime type gate (`%Command.Writ{}` demanded, everything else `{:error, :unauthorized_writer}`) and a static source scan of `lib/`. Both were mutation-tested. |
| 2.4 | Inherit the Door's law — a read never actuates | **DONE**. Every read proven pure, non-spawning, silent, and non-writing, plus a source scan proving no Phase 2 module performs disk IO or names the canonical ledger file. |
| 2.5 | Zero-dep proven | **DONE**. `git diff mix.exs` empty. `:crypto`, `Base`, stdlib `JSON`. No hex dependency. `SP.Prop` was not needed — the properties here are exhaustive over small enumerable sets, not sampled. |
| 2.6 | `Drift` — like-for-like | **DONE**. Cross-kind pairing refused at construction, in both directions, with identical raw bytes explicitly not excusing it. |
| 2.7 | Chip-vs-canonical ledger drift | **CLOSED AHEAD OF THE PHASE** on 2026-07-25, as recorded in the plan. Its falsifier fired; see §3. |

## 2. Falsifiers that fired

| falsifier | fired? | what happened |
|-|-|-|
| 2.1 — an entry can be edited with `verify/1` still passing | **partially** | Not by *editing* — editing is caught. By **tail truncation**, which no hash chain can catch. Recorded as a limitation of the mechanism and asserted in the suite, not designed around. |
| 2.2 — a row missing a key, or a verdict outside the enum, is accepted | no | Refused, and the refusal names the field. |
| 2.3 — a write path exists that does not pass through `Command` | no | Mutation-tested: adding a writer reference to a second module fails the suite. |
| 2.4 — a read has a side effect | no | |
| 2.5 — a hex dependency is added | no | |
| 2.6 — a prose-vs-command-output comparison is constructed | no | Refused at construction. |
| 2.7 — a seat is built before the decision is recorded | **yes**, before the phase | Recorded in `PHASE-2.md` rather than back-dated. |

## 3. Item 2.7 — the recorded decision, and what it implies

The chip replicas' copies of the gate ledger differ from canonical. The operator
ruled "build the seat", and it was built the same hour — which fired 2.7's own
falsifier, since the plan had pre-registered a decision-only item.

`drift.replica_ledger.*` now compares the canonical ledger's sha256 against each
replica's, agent-captured. Three replicas, all `DIFFERS`, **none holding evidence
canonical lacks**. It is the only like-for-like (hash↔hash) drift comparison on
the platform.

**What it implies for Phase 3.** A replica that merely lags is not a fault; a
replica that lags *without anything noticing* is. The seat makes the lag
observable. It does not make it correct, and it does not decide what to do about
it. Deciding requires the thing Phase 3 builds: a registered claim with a stated
pass condition. Until then the signal reads `DIFFERS` and means only that.

## 4. Three adverse results

### 4.1 The canonical ledger violates its own schema, twelve times

**Rows 112–123 of `evidence/gates.ndjson` carry `"pre_registration_path": null`.**
The schema declares that property `"type": "string"`. JSON Schema 2020-12 does not
admit `null` for a string.

```
112 broadcast-test-stages-honest          118 cc-status-honest-fields
113 status-endpoint-honest                119 cc-per-endpoint-fanout-rows
114 gaia-probe-not-envelope               120 cc-broadcast-metadata-surface
115 broadcast-test-stages-honest          121 cc-glass-badge-honest-rename
116 publisher-pin-claim-retracted         122 music-service-integration-first-class
117 cc-writestate-honest-freshness        123 cam-mic-hardened-defaults
```

**Why nothing caught it.** The enforcing test is more permissive than the thing
it enforces. `test/gate_registry_integrity_test.exs:61` reads
`if row["pre_registration_path"] not in [nil, ""] do` — it steps over `null`
deliberately, because that line guards receipt *existence*. It was never meant to
type-check, and nothing else does. The gap is *between* two guards.

The validator was not weakened. The ledger was not edited — digest identical
before and after this phase. The twelve are pinned by name so a thirteenth fails
the suite and so does a silent repair, and a third test asserts the tolerant line
still reads as quoted so the finding cannot rot into a claim about moved code.

**The remedy is the operator's decision** and is pre-registered in
[`PHASE-3.md`](PHASE-3.md) §1 as the first item.

### 4.2 A hash chain cannot detect truncation from the tail

A prefix of a valid chain *is* a valid chain: every `prev_hash` resolves, `seq`
is contiguous from 1. Deletion from the middle is caught. Deletion from the end
is not, and no internal hashing fixes it.

`verify/2` accepts an out-of-chain anchor (`head:`, `length:`) and does catch it —
but **nothing yet holds that anchor.** In practice, today, tail truncation is
undetected. Phase 3 owns the anchor.

### 4.3 A pre-registered verification command fails, and it predates this phase

`PHASE-2.md §3` lists `mix format --check-formatted`. It **FAILS** on
`lib/sp/brain/language.ex` — a file this phase did not touch, unmodified in the
working tree, last changed at `aa8586f`, and **committed with CRLF line endings**.
Every Phase 2 file passes the same check.

Not fixed here: reformatting an untouched file in another subsystem would put an
unrelated diff inside an evidence commit. Inherited by Phase 3.

## 5. Red-then-green, proven rather than asserted

| | red `47d0ef9` | green `75e2fc4` |
|-|-|-|
| `mix test test/sp/control_plane` | **59 tests, 56 failures** | **61 tests, 0 failures** |

Every red failure was `UndefinedFunctionError` against a module not yet written —
failing for the stated reason, not an accidental one.

**Three tests passed in red. Two of them passed vacuously**, and this was recorded
at the time rather than counted as compliance: both are static source scans over
`lib/sp/control_plane/`, a directory that did not exist. A source scan cannot fail
before its subject is written.

At green, both were **mutation-tested**:

| mutation | guard | result |
|-|-|-|
| a `Ledger.append` reference added to a second module | "no module in lib/ other than command.ex calls the ledger writer" | **FAILED as required** |
| a `File.write` to the canonical ledger added to a Phase 2 module | "this whole phase writes no row to the canonical ledger" | **FAILED as required** |

Both reverted; diff empty; suite returned to 61/0.

Two tests were **added** between red and green, both to record §4.1. Neither
weakens a check.

## 6. Verification

| command | result |
|-|-|
| `mix format --check-formatted` | **FAIL — pre-existing**, §4.3. Phase 2 files pass. |
| `mix compile --warnings-as-errors --force` | PASS — 121 files, no warnings |
| `mix test` | PASS — 615 tests, 4 doctests, 0 failures (was 554) |
| `mix test test/sp/control_plane` | PASS — 61 tests, 0 failures |
| `git diff mix.exs` | empty |
| `evidence/gates.ndjson` sha256 | `34084835…bab1514` before **and** after |
| `node viewer/gaia/verify_gaia.cjs` | PASS — 12 checks, 0 FAIL, 308 signals, 8 drift signals |
| `node viewer/gaia/gaia_lint.cjs` | PASS — 0 violations |
| `test/sp/brain/mc_test.exs` | untouched |

## 7. Standing state, unchanged by this phase

`P8 = FULL_PARITY = false`, first unsatisfied rung `P4`, irreducibly external.
Gate `nursery-fenced-red-stocked` remains **FAIL**, falsified 2026-07-19.
No verdict was authored. No gate was registered. Go-live remains human-typed.

## 8. Next act

[`PHASE-3.md`](PHASE-3.md) — registration and verdict authorship. Phase 2 is
complete only because that plan exists, committed and pre-registered in this same
form (`ORCHESTRATE-RULES.md §1`).
