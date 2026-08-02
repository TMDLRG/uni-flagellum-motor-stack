# Phase 3 — Registration, verdict authorship, and the anchor

**Status:** EXECUTED 2026-07-25 → [`PHASE-3-RESULTS.md`](PHASE-3-RESULTS.md) · item 3.6 landed **PARTIAL**, 3.7 a **standing known-fail** · **Written from:** [`PHASE-2-RESULTS.md`](PHASE-2-RESULTS.md), not from Phase 2's expectations
**Bound:** `SP.ControlPlane.{Registry, Verdict, Anchor}` in the **root zero-dep app** of `UNI.Minecraft`.
**A verdict may be authored in this phase. No row is written to the real `evidence/gates.ndjson`, and no P-level moves.**
**Authorises:** [ADR-0006](../decisions/ADR-0006-sp-controlplane-naming-and-placement.md)

---

## 0. What Phase 2 changed about this phase

Three things, and the first is not a build item — it is a question that must be
answered before the code that would answer it wrongly gets written.

1. **The canonical ledger violates its own schema twelve times** (`PHASE-2-RESULTS.md` §4.1).
   Phase 3 builds the thing that authors rows. It must not author its thirteenth
   instance, and it must not silently normalise the twelve. **The remedy is an
   operator decision and it blocks item 3.1.**
2. **The hash chain has no anchor**, so tail truncation is undetected in practice
   (§4.2). `Ledger.verify/2` already accepts one; nothing holds one. Phase 3
   makes the anchor a real artifact.
3. **A pre-registered verification command fails and it is not ours** (§4.3).
   `mix format --check-formatted` fails on `lib/sp/brain/language.ex`, committed
   with CRLF. Inherited here as item 3.7.

## 1. The operator decision that gates item 3.1

> **Twelve canonical rows carry `"pre_registration_path": null`, which the schema
> forbids. What is the remedy?**

### ANSWERED 2026-07-25 — the operator chose **option A**. Item 3.1 is DONE.

Executed the same day. Two corrections were made *before* acting, and are recorded rather than smoothed away:

1. **Eleven rows, not twelve.** Twelve violations across **eleven distinct gate names** — `broadcast-test-stages-honest` accounts for two of them. My recommendation said twelve; it was wrong.
2. **"The ledger conforms" can only mean the effective state.** Append-only means the twelve originals stay at rows 112-123 and stay non-conformant forever. Conformance is a claim about the **last row per gate name** — what `render_gates.cjs`, UNI TRACK and Gaia's gates seat all resolve to. The stronger claim is not available and is not made.

**And the first attempt was wrong, and was rolled back.** The ledger has **mixed line endings** — 58 `CRLF`, 137 bare `LF`, ending on a bare `LF`. The appender asked whether `CRLF` occurs *anywhere* and so chose the minority terminator, then added a spurious separator, leaving an undeclared blank line in canonical evidence. Caught by `git diff --numstat` showing **12 added lines for 11 rows**; rolled back to the exact pre-write digest before anything was committed. Two permanent fixes: the terminator now comes from the **last line**, and a **five-condition post-write self-check** restores the original and exits non-zero if the write cannot prove what it did.

```
sha256 34084835...bab1514 -> 964ea25c...1d8a4c44 · 195 -> 206 rows · 11 added, 0 removed
render_gates: 109 gates -> 92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING (tally unchanged)
```

Receipt: `docs/receipts/control-plane/phase3_item31_schema_correction_2026-07-25.md` in `UNI.Minecraft`. Red at `b649683`, green at `0abc2ba`.

**A gap this exposed and did not close:** the mutation was **not recorded in a Control Plane ledger entry**. `SP.ControlPlane.Ledger` has structure but **no persistence** — Phase 2 built the shape, not a store. So the audit trail for the Control Plane's first write to canonical evidence is a git commit and a receipt: the very mechanism this body exists to replace. That becomes a `PHASE-4.md` build item, alongside a home for the anchor item 3.6 needs.

The original three options are kept below as the decision record.

| option | what it means | cost |
|-|-|-|
| **A — append twelve corrective rows** | each superseding row carries `""` instead of `null`, keeping every original row intact and the correction visible in the append-only record | twelve new rows; the ledger grows; the history shows the correction, which is the point |
| **B — amend the schema to admit `null`** | `"type": ["string", "null"]`, and `null` becomes an honest "no pre-registration exists" | one line; but it retroactively legitimises rows written before anyone decided that, and `""` already means the same thing in 114 other rows |
| **C — leave the disagreement standing, pinned** | what Phase 2 did: the twelve are named, a thirteenth fails the suite, a silent repair fails the suite | no work; but the ledger stays non-conformant to its own schema indefinitely |

**This is not mine to pick.** Option A is the one that matches the append-only
discipline and the existing convention (`""`, not `null`, in 114 rows), and it is
what I would propose — but it writes twelve rows to the canonical ledger, which
is exactly the kind of act that requires a human decision rather than an agent's
judgement.

~~**Item 3.1 does not start until this is answered.**~~ Answered and executed; see above.

## 2. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 3.1 | ~~Remedy the twelve non-conformant rows~~ **DONE 2026-07-25, option A** | the ledger's **effective** state validates | **neither pre-registered falsifier fired** — no row was edited in place (`11 added, 0 removed`) and the validator was not widened. A *different* defect did fire: the appender used the wrong line terminator and left an undeclared blank line. Rolled back to the pre-write digest, fixed, re-run behind a post-write self-check. |
| 3.2 | `SP.ControlPlane.Registry` — register a gate **before** its run | a registration entry carries `pass_condition`, `falsifies_condition`, `pre_registration_path`, and lands in the ledger *before* any run entry that references it | a verdict is authored for a gate with no preceding registration entry |
| 3.3 | `SP.ControlPlane.Verdict` — author `PASS\|PARTIAL\|FAIL\|WITHHELD\|PENDING`, and nothing else | a verdict is a controlled word plus a receipt reference, never a number | a numeric or percent score is accepted as a verdict |
| 3.4 | Structural refusals from `ARCHITECTURE.md §7.1` | a verdict with no pre-registered gate, a percent score, or a bare `PARTIAL` that does not name its holding sub-claim is refused, and the refusal names what is missing | any of the three lands |
| 3.5 | Two-party authorship — the co-signer may not be the proposer | a mutation whose `authorization.granted_by` equals its `actor` is refused | an actor approves their own change |
| 3.6 | `SP.ControlPlane.Anchor` — hold the ledger's expected head and length outside the chain | `Ledger.verify/2` is fed from a real anchor artifact, and tail truncation is detected in practice rather than only in a test | a chain is verified without an anchor and reported as sound |
| 3.7 | Inherited: `mix format --check-formatted` | either `lib/sp/brain/language.ex` is normalised to LF in its own commit, separate from any evidence commit, or the failure is recorded as a standing known-fail with its reason | the reformat is buried inside a Phase 3 evidence commit |

**Standing expectation:** pure, offline, deterministic Elixir. No hex dependency.
No Phoenix. No change to `ui/`. The real `evidence/gates.ndjson` is written **only**
under item 3.1 and **only** on the operator's explicit answer to §1 — every other
item uses fixtures in `test/fixtures/control_plane/`.

## 3. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/registry_precedes_run_test.exs` | a verdict is authored for a gate that was never registered |
| `test/sp/control_plane/registry_prospectivity_test.exs` | a registration entry can be appended after the run entry it claims to precede |
| `test/sp/control_plane/verdict_vocabulary_test.exs` | `verdict: 0.93`, `"93%"` or `"MOSTLY_PASS"` is accepted |
| `test/sp/control_plane/verdict_partial_names_subclaim_test.exs` | a bare `PARTIAL` with no holding sub-claim is accepted |
| `test/sp/control_plane/verdict_requires_receipt_test.exs` | a verdict lands with no receipt reference |
| `test/sp/control_plane/cosigner_is_not_proposer_test.exs` | `actor == authorization.granted_by` is accepted |
| `test/sp/control_plane/anchor_detects_truncation_test.exs` | a truncated chain verifies against a real anchor artifact |
| ~~`test/sp/control_plane/ledger_schema_conformance_test.exs`~~ **DONE** | the canonical ledger contains a row the schema rejects and nothing fails — observed red at `b649683` (`6 tests, 4 failures`), green after |

Each is committed **red** with its failure output recorded, then made green.
**Where red-then-green is not achieved — including a guard that passes vacuously
because its subject does not yet exist — that is stated, and the guard is
mutation-tested at green before it is counted.** Phase 2 did this and it is now
the standing procedure, not a one-off.

## 4. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted                # see item 3.7 — known pre-existing FAIL on lib/sp/brain/language.ex
mix compile --warnings-as-errors --force
mix test                                    # offline; deps: [] unchanged
mix test test/sp/control_plane
git diff mix.exs                            # MUST be empty
sha256sum evidence/gates.ndjson             # unchanged unless item 3.1 was authorised
node viewer/gaia/verify_gaia.cjs            # 12 checks PASS; 8 drift signals
node viewer/gaia/gaia_lint.cjs              # 0 violations
```

**Acceptance:** all eight red tests recorded red, then green, with every vacuous
guard mutation-tested. `mix.exs` unchanged. `mc_test.exs` untouched. `verify_gaia`
still passes `gaia-drift-surfaced`. `evidence/gates.ndjson` byte-identical unless
§1 was answered A, in which case its diff is exactly twelve appended rows and
nothing else.

**Rollback:** additive under `lib/sp/control_plane/`. Item 3.1, if taken, is
append-only and therefore not rolled back by deletion — it is corrected by a
further superseding row, which is the discipline working.

**Stop conditions:** `STOP_TEST_REGRESSION` if any existing test breaks ·
`STOP_PROTOCOL_CHANGE_REQUIRED` if a hex dep looks necessary ·
`STOP_DESTRUCTIVE_ACTION_REQUIRED` before any write to the real ledger —
**item 3.1 begins in this state and does not leave it without a human answer.**

## 5. Explicitly not in this phase

Run execution. The pairing guard. Rooms, airlocks and keys. A new Gaia seat. The
lab view. Any Phoenix code. Any change to `ui/`. Moving a P-level.

## 6. Exit condition — the phase ends by starting the next

**Phase 3 is complete only when `PHASE-4.md` exists, is committed, and is
pre-registered in this same form** — written from Phase 3's *observed* results,
not from this plan's expectations. Passing all eight tests is not completion.

`PHASE-4.md` must carry:

1. Every Phase 3 disposition, including each falsifier that fired.
2. The operator's answer to §1 and what was actually done about the twelve rows.
3. Whether the anchor (3.6) made tail truncation detectable **in practice**, or
   only in a test.
4. **Ledger persistence.** Carried from item 3.1: the Control Plane's first write to
   canonical evidence was not recorded in its own ledger, because the ledger has no
   store. Until it does, the Control Plane's audit trail is git — the mechanism it
   exists to replace.
5. **The gate ledger's mixed line endings** (58 `CRLF` / 137 `LF`) as a standing hazard
   for every future appender, with the rule that took a rollback to learn: take the
   terminator from the **last line**, and prove the write afterwards.
6. The Phase 4 build items — `Run`, `Pair`, and the run-status refusals F12–F18
   from [`FAILURE-MODES.md`](../FAILURE-MODES.md) — each with a red test named
   before it is written.
7. Its own §6 requiring `PHASE-5.md`.

A phase that closes without its successor has stopped, and stopping is legitimate
only under a declared STOP condition.
