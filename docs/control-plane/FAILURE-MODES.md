# Failure modes — every refusal as a testable statement

**Status: F1–F23 and F28–F30 are BUILT and tested. F31's refusal is BUILT and refusing; the human-presence mint it needs does NOT exist, so go-live is closed rather than guarded. F24–F27 remain DESIGN.** See the status section at the foot — and read the two corrections there before trusting anything above them. Each row is a refusal the Control Plane must make, written so it can be a test that fails for the correct reason before the code exists. `ARCHITECTURE.md §10` states these in prose; this file makes them executable.

The form is deliberate: **given** a condition, the system **must refuse**, and the **falsifier** is the observation that would prove it does not.

---

## Authorship

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F1 | a verdict is authored with no pre-registered gate | refuse, naming the missing gate | a verdict lands without a registration entry preceding it in the ledger | 3 |
| F2 | a verdict carries a percent or a score | refuse | a numeric score is accepted as a verdict | 3 |
| F3 | a `PARTIAL` does not name which sub-claim holds | refuse | a bare `PARTIAL` is accepted | 3 |
| F4 | the co-signer is the proposer | refuse | an actor approves their own change | 3 |
| F5 | a gate row fails `gate_row.schema.json` | refuse | a row with `verdict: "MOSTLY_PASS"` is written | 2 |
| F6 | a revision would mutate the row it supersedes | refuse | a superseded row's bytes change | 2 |

## The ledger

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F7 | a past entry is edited | `verify/1` fails | the chain verifies after an edit | 2 |
| F8 | an entry is deleted | `verify/1` fails | the chain verifies after a deletion | 2 |
| F9 | `seq` is non-contiguous | `verify/1` fails | a gap verifies | 2 |
| F10 | a write is attempted outside `Command` | refuse | the ledger grows without a `Command` call | 2 |
| F11 | a read is performed | nothing is spawned, nothing mutates | a `GET` or a poll causes an actuation | 2 |

## Runs

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F12 | two or more variables differ between arms | mark the run `VOID`, unclaimable | a two-variable result is claimed | 4 |
| F13 | `actual_n = 0` | record `NOT_RUN` | an empty run reports a verdict | 4 |
| F14 | `0 < actual_n < planned_n` with no prior stopping rule | record `PARTIAL_NOT_ESTABLISHED` | a short run is treated as complete | 4 |
| F15 | `actual_n > planned_n` | flag `OVERRUN` | an overrun silently reads `ELIGIBLE` | 4 |
| F16 | an optimizer reports non-convergence | halt before scoring; **write no artifact** | a non-converged fit produces a result file | 4 |
| F17 | score and motor-id arrays differ in length | raise **before** any aggregate | a mean is computed over truncated pairs | 4 |
| F18 | a run crashes | record `FAILED_RUN`, keep it inspectable | a crash is recorded as a scientific negative | 4 |

## Rooms and keys

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F19 | sterile entry without an execution receipt | refuse, naming the missing receipt | the door opens without it | 6 |
| F20 | an airlock with fewer than two valid keys | refuse, naming which key | one key admits | 6 |
| F21 | an override is attempted | there is no override path to attempt | any bypass exists | 6 |
| F22 | sterile exit without a contamination check | refuse | exit succeeds unchecked | 6 |

## Drift and rendering

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F23 | a comparison between two different kinds | refuse **at construction** | a prose-vs-file-listing comparison is constructible | 2 |
| F24 | a scene node lacks `truth_class` or `receipt_ref` | render as fog | it renders as anything else | 7 |
| F25 | evidence for a state is absent | render fog, **refuse authoring from inside it** | an unbacked state renders as solid, **or a verdict can be authored from inside fog** | 7 |
| F26 | liveness is not from a real probe | render no liveness | motion or glow implies live | 7 |
| F27 | a gate demonstrates a behaviour | render the behaviour only | any material depicts awareness, experience or life | 7 |

### F25 amended 2026-07-26 — the refusal moved from the door to the desk

**F25 previously read "render fog, refuse entry", and it contradicted
`ARCHITECTURE.md` §8.3**, which says in its own words:

> Fog is walkable but nothing inside it may be acted on. **You may stand in the
> unknown; you may not author a verdict from inside it.**

Item 7.3 implemented F25's version — `enterable?/1` returned false for fog — and
nothing in the codebase read §8.3. Two authoritative documents disagreed and the
code silently picked one. Found by an adversarial audit during item 7.6; **resolved
toward §8.3 on the operator's co-sign, 2026-07-26.**

**This is a relaxation at the door, and it is stated as one.** You can now stand in
an unbacked state, which item 7.3 explicitly argued against: *"a room you can enter
is a room you will stand in and reason from."* That argument was not wrong — it was
answering the wrong question. You must be able to **look at** what is unbacked;
that is how you find out what is missing. What you must not do is **author from
there**, and that is now a hard refusal rather than a locked door.

The guard is **relocated, not deleted** — the standing rule that a canary which
fires is replaced by what it was guarding. If fog became walkable and no authoring
refusal appeared anywhere, a guard would have been removed under cover of a
contract amendment. Item 7.9's falsifier is exactly that.

And per §10 the refusal renders **absent, not greyed**: from inside fog the
authoring action is not offered at all, because *a greyed control still teaches that
the action exists*.

## Distribution and safety

| # | given | must | falsifier | phase |
|-|-|-|-|-|
| F28 | frozen evidence hashes drift | `STOP_FROZEN_EVIDENCE_DRIFT`, halt everything | work continues past a drift | any |
| F29 | an archive cannot be opened | report `UNVERIFIED` | it is treated as clean | any |
| F30 | files in a distribution are unscanned | fail closed | `release_verdict` returns `PASS` with unscanned files | any |
| F31 | go-live is requested by an agent | refuse — it is typed by a human | any agent path reaches go-live | any |

---

## How these become tests

Phase 2 covers **F5–F11 and F23** — the ones its modules own. Each is committed **red**, with its failure output recorded, before the code exists. The remainder are pre-registered here so a later phase inherits the statement rather than inventing it.

A refusal that cannot be demonstrated failing first is not a guard; it is a hope.

## Status — updated per phase, most recent last

**F5–F11 and F23 are IMPLEMENTED and tested** (`UNI.Minecraft` `75e2fc4`, `test/sp/control_plane/`, 61 tests). Red run recorded at `47d0ef9`: 59 tests, 56 failures, every one an `UndefinedFunctionError` against a module not yet written.

**F8 is implemented with a stated limit.** Deletion from the *middle* is caught. Deletion from the *tail* is not — a prefix of a valid chain is a valid chain, and no hash chain can see that. `Ledger.verify/2` catches it against an out-of-chain anchor, but **nothing holds an anchor yet**, so today the refusal is demonstrated only in a test. Phase 3 item 3.6 makes it real.

**F10 required two guards, and one of them was vacuous when first written.** Elixir cannot restrict callers, so the runtime writ type-gate only stops an *accidental* second writer. The fence that holds is a static source scan — which cannot fail before its subject exists. Both scans were therefore **mutation-tested at green**: injecting the violation made each fail as required. That procedure is now standing: a guard that passed vacuously in red is not counted until a mutation proves it bites.

**F1–F4 are IMPLEMENTED and tested** (Phase 3, `UNI.Minecraft` `8ff5591`, 127 tests). F1 by `Registry` — a verdict for an unregistered gate is refused, and prospectivity is positional: registration must be the *first* entry mentioning its gate. F2 and F3 by `Verdict` — no number, no percent, no near-miss silently normalised, and no bare `PARTIAL`. F4 by `Command`, not `Verdict`, because the two-party rule binds *every* mutation; compared case- and whitespace-insensitively.

**F8's stated limit is now closed for loss, and open for tampering.** `SP.ControlPlane.Store` persists the anchor beside the ledger, so a reload that has lost its tail fails to attest — truncation is caught **in practice**, across restarts, against loss, corruption and accident. It is **not** caught against a tamperer with write access to the store directory, who truncates the ledger and rewrites the anchor to match. A test **performs that attack and asserts it succeeds**, so the limit cannot quietly stop being true. Phase 5 item 5.1.

**F12–F18 are IMPLEMENTED and tested** (Phase 4, `UNI.Minecraft` `e6a0529`, 211 tests). F12 by `Pair` — two differences are `VOID` and unclaimable, and there is no `force`, `claim` or `override`. F13–F15 by `Run.status/1`, whose six words include `FAILED_RUN` and exclude `ELIGIBLE`. F16–F18 by `Run.may_score?/1`, `Run.score_to/3` and `Run.aggregate/2`, each written against a defect that is still live in the flagellum: `res.success` stored and never read, a bare `zip` truncating silently, and a crash recordable as a scientific negative. `aggregate/2` additionally refuses a repeated unit id — frames are not independent replicates.

**F8's residual is now CLOSED for tampering too, at the cost of an honest caveat.** `SP.ControlPlane.Witness` corroborates the local anchor against custodians in two domains, one of which — `node2` — **refuses every credential the writer holds while answering on port 22**. Measured with a negative control (the chip *accepts* the same key), so the refusal is evidence rather than a broken probe. Phase 4's tamper attack now fails. The claim is `tamper_evident`, **not** the stronger word: node2's refusal is a current configuration fact, not a structural law, so it is re-measured on every capture rather than trusted once.

**F19–F22 are IMPLEMENTED and tested** (Phase 6, `UNI.Minecraft` `d524ad1`, 286 tests). F19 and F22 by `Room` — a receipt must exist **on disk**, deliberately the opposite of `Verdict`, where authorship must not depend on the file being written yet; and every receipt is hashed into the transition, so a later edit is detectable. F20 by `Key` — two **distinct parties** with an **operator** among them; two agent keys are one party wearing two hats, and the refusal names which *kind* is missing. F21 as **absence**: there is nothing to call, because a refused control still teaches that the door is there.

**F19–F22 needed a spec change to be expressible at all.** `authorization` carried one `granted_by`; an airlock needs two. `authorization.co_signers` is the additive remedy — see `DATA-SPEC.md` §1.

**F28–F30 are IMPLEMENTED and tested** (Phase 9 stage 3, steps 3.1–3.2, `UNI.Minecraft` and
`UNI-FLAGELLUM`, 2026-07-27). All three were violated **LIVE**, and in two of them the words for
the repair were already written with no consumer.

F29 and F30 by `d5_distribution_guard.release_verdict/1`, which now returns a third word. It had
two, so *"we could not look"* and *"we looked and found nothing"* both came out as `PASS`.
`scan_archive` had always returned a note reading `"archive could not be opened - treated as
UNVERIFIED, not clean"`, and `scan_paths` took only `sub["findings"]` and dropped that note one
function short of the verdict; `scan_paths` had collected `unscanned` since the day it was written,
under a docstring promising *"a skipped file is NOT a clean file… a caller can fail on it"*, and
the verdict function had never looked at it. The step's pre-registered falsifier — *"a caller
treats UNVERIFIED as truthy"* — was **live in `main()`**, which returned `1 if verdict == "FAIL"
else 0`. Exit 0 is now reserved for `PASS`.

F28 by `frozen_evidence_guard`, wired at `pytest_sessionstart` so the session refuses to start on
a drifted tree. **There had been no checker at all.** The 250-file baseline had been pinned since
2026-07-21, `CLAUDE.md` called any diff "a contract violation and a hard stop", and nothing in
either repository had ever compared them; Phase 9 step 0.4 verified it **once, by hand**. A human
who remembers to run `sha256sum -c` is a habit, and a habit is what a frozen baseline exists to
stop relying on. The guard checks **both directions**: `sha256sum -c` cannot see a file *added* to
a frozen tree, so the roots are walked as well.

**F31's REFUSAL is BUILT. F31 IS NOT FINISHED, AND GO-LIVE IS CLOSED RATHER THAN GUARDED**
(Phase 9 stage 3 step 3.3). Measured before the work: **seven** code paths reached `StartStream`,
not the "1 of ≥5" the remediation plan estimated, and between them they had **two string
comparisons** — one on unauthenticated loopback, one on `argv`. Five had nothing, including
`/api/broadcast_test`, which is public by owner directive. Two of those five contain the word
`StartStream` **nowhere**: they take their request type from `argv` and from a JSON file, so no
literal search could ever have found them, which is exactly how they stayed unguarded.

All seven now pass one chokepoint, `viewer/golive_guard.cjs`, which refuses by default and
**throws** rather than returning — a refusal you can assign to a variable is a refusal you can
ignore. But the **human-presence token it requires is not minted by anything**, because minting is
what *opens* the door and that is the operator's. So every path refuses, nothing can open it, and
that is a shut door rather than a guarded one. `ADR-0008` is `PROPOSED, not adopted`.

**The claim level is `presence_evident`, NOT unforgeable**, and it is stated in the module, in
every grant it issues, in the gate output and in the operator's prover rather than filed here. An
agent already inside the operator's live desktop session, with read access to the token, can
replay it. **And OBS WebSocket listens on `127.0.0.1:4455` with no authentication**, so four lines
of Node that never import the guard reach the same actuator. **F31 binds this codebase's paths to
air. It does not bind the box.** Closing that needs OBS WebSocket auth, which is the operator's
studio configuration.

**CORRECTION — the F8 residual is NOT closed, and the paragraph above claiming it is has been
false since at least 2026-07-26.** That paragraph says `node2` *"refuses every credential the
writer holds"*. The live capture (`viewer/gaia/witness.json`) says
`independent_custodians: 0` and `qualifies_as_witness: false` for `offbox:node2` — the writer's key
is accepted, so the second domain is not independent and the two-domain corroboration Phase 5
relied on does not hold. **Phase 5's closure of
`test/sp/control_plane/store_anchor_in_practice_test.exs:145` is therefore VOID**: the RESIDUAL
test still passes, and it still means what it always meant — an adversary who owns the store
directory can rewrite the ledger and the anchor together, and nothing local catches it. The local
anchor stands on git alone: **tamper-evident, not unforgeable.**

Removing that key is `S1` — the one repair an agent must not perform, because using write access
to erase the evidence of write access destroys the last proof rather than restoring a witness. The
paragraph above is **left standing rather than rewritten**, for the same reason a ledger entry is:
what was believed at the time is part of the record.

**F24–F27 remain DESIGN.** Nothing in Phase 9 stage 3 touched them, and they are not claimed.
