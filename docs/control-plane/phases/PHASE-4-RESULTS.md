# Phase 4 — RESULTS

**Status:** EXECUTED 2026-07-26 · **Plan:** [`PHASE-4.md`](PHASE-4.md)
**Repo:** `UNI.Minecraft` `gen2-runtime` — red `f9c5167`, green `e6a0529`
**Receipt:** `docs/receipts/control-plane/phase4_green_2026-07-26.md`
**Bound honoured:** no row written to `evidence/gates.ndjson` · no P-level moved · `mc_test.exs` untouched · `mix.exs` unchanged · no hex dependency.

---

## 0. Headline — the Control Plane can record its own writes, and two canaries fired on schedule

`SP.ControlPlane.Store` gives the ledger somewhere to live. The body that exists
to replace git-as-audit-trail no longer needs to borrow it.

```
$ mix test test/sp/control_plane
211 tests, 82 failures      # red, f9c5167
211 tests,  0 failures      # green, e6a0529
```

Test count identical across red and green. Full suite **765 tests, 0 failures**
(was 681).

The second half of the headline is that **both canaries this programme planted in
earlier phases fired**, and neither was deleted. That is the part worth reading.

## 1. Disposition of every item

| # | item | disposition |
|-|-|-|
| 4.1 | `Store` — durable append-only persistence | **DONE.** Two plain files. Append-only enforced *before* the write; a refused write writes nothing and names the `seq` where histories part. |
| 4.2 | The anchor becomes a practice | **DONE, with a named residual.** Caught in practice against loss, corruption and accident; not against a tamperer who owns the directory. See §4. |
| 4.3 | `Run` — immutable run identity | **DONE**, after correcting the item's own wording. See §5. |
| 4.4 | `Pair` — exactly one differing variable | **DONE.** Two or more differences are `VOID` and unclaimable; there is no `force`, `claim` or `override`. |
| 4.5 | Run status refusals F13–F15 | **DONE.** Six statuses, none of them a score and none of them `ELIGIBLE`. |
| 4.6 | Run failure refusals F16–F18 | **DONE.** Non-convergence halts before scoring and writes nothing; mismatched lengths raise before any aggregate; a crash is `FAILED_RUN` and outranks everything. |
| 4.7 | The mixed-EOL hazard, made mechanical | **DONE.** The 2026-07-25 rollback is now a test, including a live read proving the canonical ledger really is mixed. |

## 2. Falsifiers

| item | falsifier | fired? |
|-|-|-|
| 4.1 | a reload loses, reorders or silently repairs an entry | no |
| 4.2 | a truncated ledger reloads and is reported sound | **no for loss; YES for a tamperer** — asserted deliberately, §4 |
| 4.3 | two runs of identical inputs differ, or a field can be edited after the fact | no — after the item's wording was corrected, §5 |
| 4.4 | a two-variable result is claimable | no |
| 4.5 | a short run reads as complete, or an overrun reads as `ELIGIBLE` | no |
| 4.6 | a non-converged fit produces a result file, or a crash is recorded as a negative | no |
| 4.7 | an appender infers the terminator from anywhere else | no |

**The phase premise held.** `deps: []` carries durable persistence with `File`,
`:crypto` and stdlib `JSON`. Checked *before* anything was built on it, as the
plan required. `git diff mix.exs` is empty. No `STOP_PROTOCOL_CHANGE_REQUIRED`.

## 3. Both canaries fired, and neither was deleted

| canary | planted | outcome |
|-|-|-|
| *"STATED LIMIT — nothing persists an anchor yet"* | Phase 3, item 3.6 | **FIRED.** Replaced by the assertion it pointed at. |
| *"no Phase 2 module performs disk IO"* | Phase 2, F11 | **FIRED.** Narrowed from a blanket to an allowlist. |

Deleting a canary that fires is how a limit quietly stops being tracked. Both
were replaced with what they were guarding, and both replacements were
mutation-tested.

### A guard was deliberately weakened, and this is the exact trade

The disk-IO scan was always a **proxy** for the real rule, *a read never
actuates*, and it only held while nothing persisted anything.

- **Weaker:** one module may now touch disk.
- **Stronger:** it is an **allowlist of exactly one**. A second writer, or a
  writer inside a module that reads, now fails — which the blanket could never
  distinguish.
- **Unchanged:** every read's purity is asserted directly, function by function,
  and never depended on this scan.

## 4. Item 3.6 is upgraded — and the residual is asserted, not footnoted

**Now true:** the anchor persists beside the ledger. A reload that has lost its
tail fails to attest. Losing one entry is caught. A stale anchor no longer
attests a grown chain. An absent anchor is a refusal, never a pass.

**Still not true:** it does not stop a tamperer with write access to the store
directory, who truncates `ledger.ndjson` and rewrites `anchor.json` to match.
Nothing local can. It needs an anchor the ledger's writer cannot reach.

`store_anchor_in_practice_test.exs` **performs that attack and asserts it
succeeds.** A limit that is only written down stops being true quietly; a limit
that is asserted fails loudly when it moves.

## 5. ADVERSE — a fourth pre-registered phrase was imprecise

Item 4.3 read *"the same run twice produces byte-identical canonical bytes"*.
Taken literally that is **false and must stay false**: a run record carries
wall-clock start and end, and two executions genuinely happen at different
moments. A record that hid that would be lying.

Split into two things, tested separately: **identity** (code, env, inputs,
params, seeds, `planned_n`, `stopping_rule`, hashed into `run_id`) and **record**
(times, exit code, outputs, `actual_n`).

**`planned_n` and `stopping_rule` sit inside the identity on purpose.**
`CLAUDE.md`: *"never increase replicates after seeing a width."* Because both are
hashed, lowering the plan to make a short run look `COMPLETE`, or declaring a
stopping rule once the numbers are in, **changes what run this is**. The
laundering leaves a mark.

Four phases, four pre-registered phrases wrong on contact — §2 of Phase 3's
results, plus this. The pattern is stable: prose written before a thing exists
compresses a distinction the thing turns out to need.

## 6. ADVERSE — two of my own tests contradicted each other

`run_status_refusals_test` asserted the status vocabulary was **five** words.
`run_failure_refusals_test` asserted `:FAILED_RUN` is **in** it, *"so it cannot be
a surprise value nothing renders"*. Both mine, written an hour apart, and they
cannot both hold.

The failure test is right. Corrected to six **on the merits**, not by loosening
whichever assertion was easier to move.

## 7. ADVERSE — two real defects in `Store`, caught by my own new tests

1. **`store.ex`'s moduledoc named `evidence/gates.ndjson`** — failing the very
   guard it was written to satisfy. A module that names the canonical evidence
   file is one edit from writing to it.
2. **An empty store did not create its ledger file**, so a correctly initialised
   store loaded as `not_a_store`. An initialised store with no entries is a real
   state, not an absent one.

## 8. What is built, and the one thing that is not yet proven

| module | what |
|-|-|
| `SP.ControlPlane.Store` | durable append-only persistence; the **only** module that touches disk |
| `SP.ControlPlane.Run` | immutable identity, six statuses, three refusals from real flagellum defects |
| `SP.ControlPlane.Pair` | exactly one differing variable, or `VOID` |
| `SP.ControlPlane.Ledger` | `from_entries/1`, named as the trust boundary it is |

**Not yet proven: the Control Plane has the capability to record its own
mutations and has not yet used it.** No Control Plane ledger has been persisted
in anger. Capability is not practice — this programme has said so twice already
about the anchor, and the same distinction applies here. `PHASE-5.md` item 5.2
makes the first real entry.

## 9. Verification

| command | result |
|-|-|
| `mix test` | PASS — 765 tests, 4 doctests, 0 failures |
| `mix test test/sp/control_plane` | PASS — 211 tests, 0 failures (82 red) |
| `mix compile --warnings-as-errors --force` | PASS — 127 files |
| `mix format --check-formatted` — Control Plane | PASS |
| `mix format --check-formatted` — repo-wide | **FAIL, standing known-fail** ([PHASE-3-RESULTS](PHASE-3-RESULTS.md) §3) |
| `git diff mix.exs` | empty |
| `evidence/gates.ndjson` | `964ea25c…1d8a4c44` unchanged |
| `verify_gaia` · `gaia_lint` | PASS — 12 checks / 0 violations |
| `mc_test.exs` | untouched |

## 10. Standing state, unchanged

`P8 = FULL_PARITY = false`, first unsatisfied rung `P4`, irreducibly external.
`nursery-fenced-red-stocked` remains **FAIL**, falsified 2026-07-19.
**No verdict has been authored about any real scientific claim.**

## 11. Next act

[`PHASE-5.md`](PHASE-5.md) — the witness: an off-box anchor, the first real
Control Plane ledger, and a Gaia seat that projects it verbatim. Phase 4 is
complete only because that plan exists (`ORCHESTRATE-RULES.md §1`).
