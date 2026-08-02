# Phase 5 — RESULTS

**Status:** EXECUTED 2026-07-26 · **Plan:** [`PHASE-5.md`](PHASE-5.md)
**Repo:** `UNI.Minecraft` `gen2-runtime` — `8c7940c` (5.0) · `1ee1533` (5.1) · `915bfbb` (5.2–5.6)
**Receipts:** `docs/receipts/control-plane/phase5_*`
**Bound honoured:** no row written to `evidence/gates.ndjson` · no P-level moved · `mc_test.exs` untouched · `mix.exs` unchanged · GAIA LAW intact.

---

## 0. Headline — item 5.0 earned its place on the first attempt, and the fleet answered a question I had got wrong

Phase 5 opened by checking three premises against a live read **before** building
on them, because four had been wrong on contact, one per phase.

**One premise was false, and so was the plan's own fallback for it.** Then the
operator stabilised L2 and instructed both approaches — and the false premise
became true for a reason that is mechanically checkable rather than hopeful.

```
Control Plane suite  238 tests, 0 failures      Full suite  792 tests, 0 failures
Gaia  12 PASS / 0 FAIL · 11 seats · 10 drift signals · lint 0 violations
```

## 1. Disposition

| # | item | disposition |
|-|-|-|
| 5.0 | check three premises first | **DONE.** Two confirmed, one false — and the fallback false too. §2 |
| 5.1 | `Witness` — an anchor the writer cannot reach | **DONE.** Phase 4's tamper attack now fails. §3 |
| 5.2 | the first real Control Plane ledger | **DONE.** Seven entries, its own history, adverse results included. §4 |
| 5.3 | `gaia_lint` proven to bite before the seat | **DONE.** Inverse-polarity check, 10 violations across 5 checks. §5 |
| 5.4 | a Gaia seat projecting the ledger verbatim | **DONE**, after my premise check turned out incomplete. §6 |
| 5.5 | the seat surfaces the residual, two-sided | **DONE.** Two like-for-like drift signals, one deliberately `absent`. §7 |
| 5.6 | inherited `mix format` | **STANDING KNOWN-FAIL**, unchanged, `lib/sp/brain/language.ex` untouched. |

## 2. ADVERSE — a premise was false, and so was its pre-registered fallback

`PHASE-5.md §0.1` assumed a second machine could hold an anchor the writer cannot
reach. **`docs/GAIA.md` had already said otherwise, months earlier:**

> the default target is the colony host — **the only box THINKER can ssh-write
> unattended** (node2 is chronically unreachable; MCP writes are approval-gated).
> That is a **second failure domain, not a fully independent custodian**.

And the plan's fallback — *"fall back to a signed anchor"* — was **also false**: a
signature is only as good as its key's custody, and the key would live on the
writer's machine. **A signature the writer can produce is not a witness.** That is
a fifth premise wrong on contact, and the first where the fallback was wrong too.

## 3. Item 5.1 — the operator stabilised L2, and the answer changed

Measured from THINKER, **with a negative control**, because a refusal alone
proves nothing:

```
offbox:node2   port22=OPEN  writer_can_write=false  "Permission denied (publickey,password)"
control:chip   port22=OPEN  writer_can_write=true
git            head=8c7940cc  branch=gen2-runtime
```

`node2` **is** L2 — the registry already carried `mcp_limb: "uni-lab-79740c"`.
Reachable to read, refused to write. The chip accepting the *same key* is what
turns node2's refusal into evidence rather than a broken probe.

### A distinction the fleet forced, found before the red run

Item 5.1 was planned around "cannot reach", which collapses two properties:

* **unforgeable** — the writer cannot write there at all. node2.
* **tamper-evident** — the writer can, but *visibly*, and prior history survives
  elsewhere. git.

Under a single strict rule, `git + L2` would be **one** independent custodian and
would not corroborate — contradicting my own test. So corroboration requires
**two distinct domains AND at least one unforgeable custodian**. `git + L2`
corroborates; `git + chip` does not.

**Phase 4's tamper attack now fails.** Truncate the store, re-anchor to the
truncated state, and `Store.attest/1` still passes — that has not changed. The
witness is what convicts it.

**The claim is `tamper_evident` and there is deliberately nothing stronger.**
node2's refusal is a *current configuration fact, not a structural law*; one key
in its `authorized_keys` ends it silently, so the probe re-measures every capture.

### Two more of mine, recorded

- **I broke `gaia-no-ip-literal`** by hardcoding three addresses in the probe —
  the exact trap that gate exists for, since a stale literal once pointed the Door
  at a dead host while the colony was live. Rewritten to name boxes and read their
  planes from the registry at runtime.
- **A test was wrong while the code was right.** It asserted that a custodian with
  a different head *and* a shorter length is `:forked`. With real anchors a
  genuinely lagging custodian *always* has a different head — the head at its own
  length. Length decides. Corrected with the reasoning, not silently flipped.

## 4. Item 5.2 — capability became practice

Phase 4 gave this body a store and it never used one. Seven entries now record
what the programme actually did: every phase, its red and green commits, its
receipt, **and its adverse result**.

**What makes "real" mean something** is that the tests reach *outside* the file:
every commit named must exist in git; every piece of evidence must exist and
**rehash to the recorded digest**; the ledger records its own construction; and a
test asserts the adverse results are present, because a ledger of only green ones
is a highlight reel.

Anchor: head `94485ef7…`, length 7, attests clean, corroborated across `git` and
`offbox`.

## 5. Item 5.3 — the lint was proven to bite before the seat existed

A lint never seen to fail is a lint nobody has tested; "0 violations" then means
"it ran". `verify_lint_bites.cjs` runs `gaia_lint` against a committed summarizing
fixture with **inverse polarity — a PASS there is a FAILURE here**.

10 violations across 5 checks, including the forbidden token in the signal **id**,
so a seat cannot smuggle a rollup in by naming it. GAIA LAW is mechanically
enforced.

## 6. ADVERSE — my premise-3 check was incomplete, and the system caught it

Premise 3 found **three** declaration sites, because it read the *verification*
gate's requirements. There is a **fourth**: `sig.cjs`'s `SEATS` allowlist, which
refuses at **construction**. The seat threw on first render.

The seat pattern is *stricter* than my check credited, not weaker — but the check
was still incomplete, and an incomplete premise check is the thing item 5.0
exists to prevent. Recorded so the next seat starts from four.

## 7. Item 5.5 — two drift signals, one deliberately absent

* `drift.control_plane_anchor_git` — anchor in the working tree vs at `HEAD`.
  **Like-for-like**, object against object, so unlike four of the slice-1 pairings
  this one **can converge** and `equal=true` will mean what a reader thinks.
* `drift.control_plane_anchor_offbox` — relation **`absent`**, deliberately.
  Placing the anchor on node2 needs an approval-gated write: a co-sign the writer
  cannot produce, **which is exactly what makes node2 a witness**. "Not yet
  placed" is the honest state, and faking it would destroy the property it
  reports.

## 8. Falsifiers

| item | falsifier | fired? |
|-|-|-|
| 5.0 | an item is built on an unchecked premise | **no** — and the check caught the false one |
| 5.1 | the tamper attack still succeeds, or the witness lives where the writer can rewrite it | no |
| 5.2 | the ledger is a demo fixture, or written by hand | no |
| 5.3 | the lint passes a summarizing fixture | no |
| 5.4 | any Gaia-derived count, rank, rollup or verdict appears | no — lint 0 violations |
| 5.5 | a disagreement renders as a single true/false | no |
| 5.6 | the reformat is buried inside an evidence commit | no — not done at all |

## 9. Verification

| command | result |
|-|-|
| `mix test` | PASS — **792 tests**, 4 doctests, 0 failures |
| `mix test test/sp/control_plane` | PASS — 238 tests, 0 failures |
| `mix format --check-formatted` — Control Plane | PASS |
| `mix format --check-formatted` — repo-wide | **standing known-fail**, item 5.6 |
| `git diff mix.exs` | empty |
| `evidence/gates.ndjson` | `964ea25c…` unchanged |
| `verify_gaia.cjs` | PASS — 12 checks, 11 seats, 10 drift signals |
| `gaia_lint.cjs` | PASS — 0 violations |
| `verify_lint_bites.cjs` | PASS — the lint refuses a summarizing seat on every check |
| `mc_test.exs` · `language.ex` | untouched |

## 10. Standing state

`P8 = FULL_PARITY = false`, first unsatisfied rung `P4`, irreducibly external.
`nursery-fenced-red-stocked` remains **FAIL**, falsified 2026-07-19.
**No verdict has been authored about any real scientific claim.** The Control
Plane now records its own history; it has adjudicated nothing.

## 11. Next act

[`PHASE-6.md`](PHASE-6.md) — rooms, airlocks and keys. Phase 5 is complete only
because that plan exists (`ORCHESTRATE-RULES.md §1`).
