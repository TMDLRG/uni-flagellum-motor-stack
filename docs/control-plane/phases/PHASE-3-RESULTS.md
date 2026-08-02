# Phase 3 — RESULTS

**Status:** EXECUTED 2026-07-25 · **Plan:** [`PHASE-3.md`](PHASE-3.md)
**Repo:** `UNI.Minecraft` `gen2-runtime` — item 3.1 red `b649683` / green `0abc2ba`; items 3.2–3.6 red `219d8b0` / green `8ff5591`
**Receipts:** `docs/receipts/control-plane/phase3_item31_schema_correction_2026-07-25.md` · `…/phase3_green_2026-07-25.md`
**Bound honoured:** no run executed · no P-level moved · `mc_test.exs` untouched · `mix.exs` unchanged · one authorised write to canonical evidence (item 3.1) and no other.

---

## 0. Headline — three pre-registered premises were wrong, and all three were mine

The code landed and the suite is green. That is not the result.

The result is that **three things this phase was built on turned out to be false
when acted upon**: my own data specification, my own count of the rows needing
correction, and my own diagnosis of the inherited format failure. Each was an
assumption written as a fact. Each was caught by trying to use it.

```
$ mix test test/sp/control_plane
127 tests, 56 failures      # red, 219d8b0
127 tests,  0 failures      # green, 8ff5591
```

Test count identical across red and green: nothing was added to make anything pass.
Full suite **681 tests, 0 failures** (was 621).

## 1. Disposition of every item

| # | item | disposition |
|-|-|-|
| 3.1 | Remedy the non-conformant rows | **DONE**, operator-authorised option A. Eleven superseding rows. Effective state conforms; the twelve historical violations remain and always will. |
| 3.2 | `Registry` — register before the run | **DONE.** Prospectivity is positional: registration must be the first entry mentioning its gate, in `resulting` or in `prior`, under any transition. |
| 3.3 | `Verdict` — five words, nothing else | **DONE.** Numbers, percents, near-misses and unknown keys all refused. |
| 3.4 | Structural refusals from `ARCHITECTURE.md §7.1` | **DONE.** No registration → no verdict; no percent score; no bare `PARTIAL`. |
| 3.5 | Two-party authorship | **DONE**, in `Command` rather than `Verdict`, because it binds every mutation. Case- and whitespace-insensitive. |
| 3.6 | `Anchor` | **PARTIAL** — see §4. The mechanism holds; *"in practice"* does not. |
| 3.7 | Inherited `mix format` failure | **STANDING KNOWN-FAIL**, option (b). Option (a) was unavailable; see §3. |

## 2. ADVERSE — `DATA-SPEC.md` §1 was wrong, and shipped in Phase 2

§1 said `prior` may be `null` **"only for `seq = 1`"**, and `Ledger` enforced
exactly that.

Both were wrong. **Registering a new gate as the fifth ledger entry genuinely has
no prior state.** The rule confused *the ledger's* first entry with *this
subject's* first entry — a category error that reads as rigour.

It survived Phase 2 because **no test covered it**. A rule with no test is a
comment that happens to run. Phase 3 found it on the first attempt to register
anything, before a line of Phase 3 code existed.

Corrected: `prior` may be `nil` at any `seq`. Supplying the right value is the
authoring module's job; chain integrity is the ledger's. `DATA-SPEC.md` §1 is
amended, and the rule now has a test.

## 3. ADVERSE — item 3.7's premise was wrong, and its pre-registered fix does not exist

The plan offered **(a)** normalise `lib/sp/brain/language.ex` to LF in its own
commit, or **(b)** record a standing known-fail.

Option (a) rested on my assumption that the failure was **line endings only** —
the failure diff renders CRLF markers prominently, and I read the symptom as the
cause. Tested directly: 333 CRLF pairs converted to LF, and
`mix format --check-formatted` **still fails**. The file is genuinely
unformatted. A real reformat is **93 added / 29 removed lines, 85/21 of them
non-whitespace**, in the language subsystem that `CLAUDE.md` names among the
invariant-guarded areas.

**Option (b) taken.** Reformatting another subsystem is a deliberate style change
that belongs in its own commit, proposed on its own terms — not inside a Control
Plane evidence commit. Every Control Plane file passes the same check.
`language.ex` was modified twice during the investigation and reverted to
byte-identical `HEAD` both times.

## 4. Item 3.6 is PARTIAL, and this is what holds

**Holds:** the anchor mechanism exists. It round-trips through canonical bytes,
and it catches truncation by one entry, truncation by many, unexpected growth
past the anchor, and a forged head at the right length. There is deliberately no
`attest/1` — soundness cannot be claimed without something held outside the chain.

**Does not hold:** *"in practice"*, which is what the item pre-registered.
`SP.ControlPlane.Ledger` has **no persistence**, so nothing holds an anchor across
a process boundary and nothing can compare today's chain against yesterday's head.

A test asserts the limit and **fires when it stops being true**, scanning the
namespace for any persistence primitive. Mutation-tested: injecting `File.write`
makes it fail. Phase 4 owns the store.

## 5. Item 3.1 — what was actually done, and what went wrong doing it

Operator answered **option A**. Eleven superseding rows — **eleven, not the
twelve I recommended**, because `broadcast-test-stages-honest` accounts for two of
the twelve violations. Corrected before acting, not after.

`195 → 206` rows, `11 added / 0 removed`, tally unchanged at
`92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING`. Authored through
`GateRow.supersede/2`, not by hand.

**The first attempt was wrong and was rolled back.** The ledger has **mixed line
endings** — 58 `CRLF`, 137 bare `LF`, ending on `LF`. The appender asked whether
`CRLF` appeared *anywhere* and chose the minority terminator, then added a
spurious separator, leaving an undeclared blank line in canonical evidence.
Caught by `git diff --numstat` showing 12 added lines for 11 rows; rolled back to
the exact pre-write digest before anything was committed. Fixed twice over: the
terminator now comes from the **last line**, and a **five-condition post-write
self-check** restores the original and exits non-zero if the write cannot prove
what it did.

**"The ledger conforms" can only mean the effective state.** Append-only means the
twelve originals stay at rows 112–123 and stay non-conformant forever. Only the
last-row-per-name claim is available, and only it is made.

## 6. A conflict between two of my own tests, resolved before either was committed

The receipt cannot live in a verdict entry's `evidence` list. `Command` requires a
real `sha256` there; producing one means reading the file, which makes authorship
depend on the receipt already existing — contradicting the test that says it must
not. The other exit was weakening `Command`'s evidence rule: a guard traded for a
convenience.

Resolved by putting the pointer in `resulting.receipt_ref`, and written into the
test's own moduledoc so the tension is not later rediscovered as a bug.

## 7. Falsifiers

| item | falsifier | fired? |
|-|-|-|
| 3.1 | a row is edited in place, or the validator is widened | **no** — `11 added, 0 removed`; validator untouched. A *different* defect fired (§5). |
| 3.2 | a verdict is authored for a gate with no preceding registration | no |
| 3.3 | a numeric or percent score is accepted as a verdict | no |
| 3.4 | a verdict with no gate, a percent, or a bare `PARTIAL` lands | no |
| 3.5 | an actor approves their own change | no |
| 3.6 | a chain is verified without an anchor and reported as sound | **not fully closed** — `Ledger.verify/1` still reports internal soundness by design; `Anchor` refuses to, and has no arity-1 form. The gap is persistence, §4. |
| 3.7 | the reformat is buried inside a Phase 3 evidence commit | **no** — it was not done at all, and why is recorded. |

## 8. Verification

| command | result |
|-|-|
| `mix test` | PASS — 681 tests, 4 doctests, 0 failures |
| `mix test test/sp/control_plane` | PASS — 127 tests, 0 failures (56 red at `219d8b0`) |
| `mix compile --warnings-as-errors --force` | PASS |
| `mix format --check-formatted` — Control Plane files | PASS |
| `mix format --check-formatted` — repo-wide | **FAIL, standing known-fail** (§3) |
| `git diff mix.exs` | empty |
| `evidence/gates.ndjson` | `964ea25c…1d8a4c44` — unchanged since item 3.1 |
| `node viewer/gaia/verify_gaia.cjs` | PASS — 12 checks, 0 FAIL |
| `node viewer/gaia/gaia_lint.cjs` | PASS — 0 violations |
| `lib/sp/brain/language.ex` · `test/sp/brain/mc_test.exs` | untouched |

## 9. A commit message with a stale number, corrected rather than rewritten

`219d8b0` says *"55 of 126 failing"*. The recorded run is **56 of 127** — one test
was added while resolving §6, between writing the message and the final run. The
receipt is the number to trust. History is not rewritten to hide it.

## 10. Standing state, unchanged

`P8 = FULL_PARITY = false`, first unsatisfied rung `P4`, irreducibly external.
`nursery-fenced-red-stocked` remains **FAIL**, falsified 2026-07-19.
No verdict has been authored about any real scientific claim — the vocabulary now
exists and refuses correctly; it has adjudicated nothing.

## 11. Next act

[`PHASE-4.md`](PHASE-4.md) — persistence, runs, and the pairing guard. Phase 3 is
complete only because that plan exists, committed and pre-registered in this same
form (`ORCHESTRATE-RULES.md §1`).
