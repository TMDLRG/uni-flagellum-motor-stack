# Phase 7 — RESULTS

**Status:** ACCEPTANCE NOT MET — 9 of 12 items closed, but **2 of the phase's 7 acceptance clauses FAIL**
**Written from:** what happened, not from [`PHASE-7.md`](PHASE-7.md)'s expectations.
**Phase 7 is NOT complete, and it is not merely incomplete — it FAILS ITS OWN ACCEPTANCE.**

> I marked this `EXECUTED` on first writing and that was a degradation, corrected here.
> §4 of [`PHASE-7.md`](PHASE-7.md) is a conjunction of seven clauses. **Two fail:**
>
> 1. *"the witness still refuses the writer's key"* — **FALSE.** It accepts it (§1).
> 2. *"the two fixtures distinguishable with no text read, reviewed by `/organic-operator`
>    and not only by me"* — **NEVER DONE.** `ui/lib/sp_ui_web/live/lab_live.ex` does not
>    exist. `SP.ControlPlane.Scene` has **no caller outside its own tests**.
>
> PHASE-7.md's **Bound** line reads *"`SP.ControlPlane.Scene` in the root zero-dep app,
> **and a renderer in `ui/`**"*. I built the core half, closed the phase, and wrote a
> results document. Nine items closing is not the same as a phase passing, and
> recording the gap in prose while the status line said EXECUTED is exactly the
> apparent harmony the truth contract forbids.

---

## 1. The headline, and it is adverse

**The off-box witness is compromised.** node2 answers and the writer's key works —
identified directly (`hostname` = `uni-lab-79740c`, machine-id `1eeab8064da94079`,
both declared planes), not inferred from an unreachable probe.

It was custodian for exactly one reason: the writer could not write there. The anchor
now stands on **git alone — tamper-evident, not unforgeable.**

Within one session the reading went `corroborated` (03:48) → `blocked_unreachable`
(14:51) → `compromised` (17:05). Item 7.10's vocabulary, built hours earlier, held all
three apart. `witness.json`'s own `claim_note` predicted it: *"adding the writer's key
to that box would end it silently, which is why it is re-measured on every capture."*
**It was not silent.**

## 2. Dispositions

| # | item | disposition |
|-|-|-|
| 7.0 | premises checked, the open failure reproduced | **DONE** — reproduced at seed 2000; it was *my* test, not a suite flake. `async: true` + one `git` subprocess per sha, 33 cases racing for process slots. Fixed at the root, not retried |
| 7.1 | `Scene` — a pure function of state | **DONE** |
| 7.2 | **F24** — unbacked renders as fog, not an error | **DONE** |
| 7.3 | **F25** — evidence absent ⇒ fog and entry refused | **SUPERSEDED** by 7.9 on the operator's co-sign; the guarantee moved to authoring |
| 7.4 | **F26** — liveness only from a real probe | **DONE** |
| 7.5 | **F27** — the claim fence | **DONE** — and it was already structural: 8 of 11 tests passed in red because a node has no prose field |
| 7.6 | material from `truth_class`, no style flag | **DONE** — see §3 |
| 7.7 | place the anchor off-box | **BLOCKED** — not on a co-sign. The premise is gone (§1). An anchor I could place alone is not a witness, and I could place it alone |
| 7.8 | `mix format --check-formatted` | **STANDING KNOWN-FAIL** on `lib/sp/brain/language.ex`, carried since Phase 3, reformat still owed its own commit |
| 7.9 | fog is walkable; refusal moves to the desk | **DONE** — F25 amended, 5/5 mutations killed |
| 7.10 | witness gates report BLOCKED | **DONE** — and it found §1 on its first live run |
| 7.11 | address all drift | **PARTIAL** — 8 signals triaged, ADR-0002 amended, 2 signals now `equal: true`; the five malformed comparisons are co-signed and not yet repaired |

## 3. What item 7.6 cost, and why it is the item of this phase

**My first fix was worse than the defect it closed.** The red was real —
`material(%{truth_class: :OBSERVED})` with no `receipt_ref` key drew `:lit_solid`. I
closed it with a bare `def material(_), do: :fog`, went green, killed eleven
mutations, and was about to commit.

An adversarial pass over the same function found the fix answered `:fog` for `nil`,
for `42`, for a whole `%Scene{}` — **collapsing absent into nil one level up**, the
distinction the module is built on. It moved `entry/1`'s crash *later* rather than
removing it. And **a test in that same file mandated the broken fallback by regex**,
so the guard and the defect agreed with each other. Green proved nothing.

**And the falsifier was reachable twice without adding a function**: `%Scene{}` is
publicly constructible, so a hand-built scene skipped `of/1` and handed a renderer a
`:style` key that `node/2` refuses *by name*; and item 7.2's live-document guard did
not bind row to class, so swapping the `OBSERVED` and `SIMULATED` cells in §8.2 left
the whole suite green — **the authority document is a second place that chooses the
appearance.**

## 4. The two questions `PHASE-7.md` §7 requires answered

**Were the two fixtures distinguishable in a screenshot with no text read, and who
said so besides me?** **NOT ESTABLISHED. Nobody said so besides me, because I did not
build them.** `Scene` has no renderer — `material/1` has **no production caller**, and
the repository's only THREE renderer chooses appearance from simulator fields and
never sees a truth class. Phase 7 is evidenced **at the data layer only**. The
`/organic-operator` review named in §3 has not run and had nothing to review.

**Did item 7.7 happen, and what approval carried it?** **No.** See §1 and §7.7 above.
No approval was sought, because the co-sign was never the blocker.

**Was the unnamed Phase 6 failure reproduced, retired, or still open?**
**Reproduced and fixed** — item 7.0. It was not a suite flake and the Phase 6 claim
that it "likely" was is retracted.

## 5. Corrections this phase added to the programme (11–15)

Recorded in [`PHASE-7.md`](PHASE-7.md) §6: a fix can be worse than the defect it
closes · a fence can be reachable around · the authority document is a second place
that chooses the appearance · a signal filed as structural stops being read · a
receipt captured from a dirty tree is evidence about a state no commit contains.

## 6. Verification at close

`964 tests, 0 failures` · `mix format` PASS on all control-plane files · `mix.exs` and
`ui/mix.exs` unchanged · `evidence/gates.ndjson` byte-identical
(`964ea25cfe8666cae89aed23dac55bb483b654730a3259269d5e42d91d8a4c44`) · Gaia **12/12**
· `gaia_lint` 0 violations · `verify_lint_bites` PASS · schema-pointer gate PASS
(146/146).

**`verify_host_tracking` 6 PASS / 1 FAIL** — `chip-names-resolve-via-dns`, because
`music.uni-lab.local` is `ENOTFOUND`. Pre-existing, re-verified against the prior
registry, carried visibly.

**No row was written to `evidence/gates.ndjson`. No P-level moved.**

## 7. Exit condition

[`PHASE-8.md`](PHASE-8.md) exists and is pre-registered — but **Phase 7 does not close.**
Its acceptance is a conjunction and two clauses fail. Phase 8 may proceed on the
flagellum guards, which are independent; Phase 7 stays open and its two failing
clauses are carried by name:

1. **the renderer was never built** — `ui/lib/sp_ui_web/live/lab_live.ex`, and with it
   the whole reason `Scene` exists. This is MINE and I skipped it.
2. **the witness accepts the writer's key** — not mine; see §1.
