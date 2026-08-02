# Phase 7 — The lab view: a room you can stand in that cannot lie to you

**Status:** ACCEPTANCE NOT MET — 2 of 7 clauses fail → [`PHASE-7-RESULTS.md`](PHASE-7-RESULTS.md) · **Written from:** [`PHASE-6-RESULTS.md`](PHASE-6-RESULTS.md), not from Phase 6's expectations

> **This line was stale for six items.** Items 7.0–7.6 were committed and pushed to
> `UNI.Minecraft` while this file — and the whole of `UNI-FLAGELLUM` — sat at Phase 6.
> UNI TRACK reads this status live and correctly reported Phase 7 as not started; the
> instrument was right and the governance was five commits behind the code. Recorded
> rather than quietly corrected, because *"the track is not tracking"* turned out to
> mean *"the track is tracking you"*.
**Bound:** `SP.ControlPlane.Scene` in the **root zero-dep app**, and a renderer in `ui/`.
**This is the first phase that touches `ui/`.** [ADR-0007](../decisions/ADR-0007-ui-contract-amendment.md) permits it: the UI proposes, the Control Plane authors.
**No row is written to `evidence/gates.ndjson`. No P-level moves.**

---

## 0. What Phase 6 changed about this phase

1. **A test can fire on itself.** The bypass scan used `~w` with an escaped space
   and matched `"def"` in every file. A guard that cannot tell a definition from
   prose is noise. Every source scan in this phase states what it must *not*
   match.
2. **An unmet condition is not a failure**, and this phase is where that becomes
   visible rather than merely true. `Room.conditions/4` already answers honestly;
   a renderer that paints not-yet-scanned red would undo it in one stylesheet.
3. **One full-suite failure remains unnamed** (`PHASE-6-RESULTS.md` §1). Item 7.0
   reproduces or retires it before new work lands on top.
4. **Item 6.6 is still open and still the operator's.**

## 0.1 Item 7.0 — check the premises, name each check's blind spot, and clear the open failure

| premise | check | how the check itself could be wrong |
|-|-|-|
| the unnamed Phase 6 failure is a known flake | run the full suite N times capturing output; compare any failure against `test_helper.exs`'s named danger band | N runs that pass do not prove absence — record the count and call it *not reproduced in N*, never *fixed* |
| `ui/` can render without the Control Plane writing | read `ui/mix.exs`'s amended contract and confirm the render path is a pure read of a `Scene` | a LiveView that *appears* read-only may still mount a process that mutates — check for spawn, not just for writes |
| a screenshot can distinguish simulated from observed **with no text read** | build both fixtures and look | "distinguishable to me" is not "distinguishable to a tired operator at hour three" — this needs `/organic-operator`, not my own eye |

**The third premise's blind spot is the one that matters.** I am not a
substitute for the human-flow review, and a rendering I find obvious may be one
that fails at hour three of a live show.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 7.0 | premises checked, blind spots named, the open failure reproduced or recorded as not-reproduced-in-N | each stated with its limitation | new work lands on top of an unexplained failure |
| 7.1 | `SP.ControlPlane.Scene` — a pure function of state | every node carries `truth_class`, `receipt_ref`, `evidence_class`, `captured_at`; building a scene spawns nothing and writes nothing | a scene node is built that carries none of them |
| 7.2 | **F24** — a node missing `truth_class` or `receipt_ref` renders as **fog** | fog, and the fog is *not an error path* — it is the honest depiction of an unbacked assertion | it renders as anything else, or as an error |
| 7.3 | **F25** — evidence absent ⇒ fog **and entry refused** | you cannot walk into a state nothing backs | an unbacked state renders solid, or is enterable |
| 7.4 | **F26** — liveness renders **only** from a real probe | no frame rate, glow or motion implies live; a `live: null` node shows no liveness at all | motion or glow implies live |
| 7.5 | **F27** — a gate demonstrates a **behaviour** | the material depicts what was measured; nothing depicts awareness, experience or life | any material implies more than the behaviour |
| 7.6 | the renderer selects material **from `truth_class`**, not from a style flag | changing `truth_class` changes the material; there is no `style:` field to override it | a style flag exists that can make simulated look observed |
| 7.7 | Carried from Phase 6: **place the anchor off-box** | one approval-gated write; `drift.control_plane_anchor_offbox` stops reading `absent` | the anchor is placed by a path the writer could have taken alone |
| 7.8 | Inherited: `mix format --check-formatted` | standing known-fail with its reason, or reformatted in its own commit on its own terms | the reformat is buried in an evidence commit |
| 7.9 | **Fog is walkable** — resolve the contradiction between `ARCHITECTURE.md` §8.3 and `FAILURE-MODES.md` F25 | you may stand in the unknown; you may not author a verdict from inside it. The refusal MOVES from the door to the desk and is **absent, not greyed** | fog becomes walkable and the authoring refusal does not appear anywhere — a guard deleted rather than relocated |
| 7.10 | the witness gates report **BLOCKED** when the custodian is unreachable | unreachable is distinguished from refused; neither is ever reported as a pass | an unreachable custodian yields a green suite, or a stale capture is left standing in for a live one |
| 7.11 | **address all drift** — 8 live signals, disposed | each signal fixed, or classified structural with both sides verified true on a named date by a named command | a signal is made green by loosening its comparison, or filed structural without re-reading its sides |

**Items 7.9–7.11 were pre-registered on 2026-07-26, mid-phase, after the operator
co-signed two contract amendments and asked for all drift addressed.** They are
written here *before* their code, in the same form as 7.0–7.8, because a phase that
grows new items informally has stopped being pre-registered.

**Standing expectation:** `Scene` is pure, offline, deterministic Elixir in the
zero-dep core with **no hex dependency**. The renderer lives in `ui/` and
**proposes only** — every write still goes through `Command`.

**The flagellum's rendering fence does not bind here** ([ADR-0005](../decisions/ADR-0005-rendering-fence-scope.md)),
but **nothing in this phase may imply awareness, experience or life**, which is
not a rendering choice — it is the claim fence.

## 2. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `test/sp/control_plane/scene_is_pure_test.exs` | building a scene spawns, writes, or differs between identical calls |
| `test/sp/control_plane/scene_node_requires_truth_class_test.exs` | a node without `truth_class` or `receipt_ref` is built as solid |
| `test/sp/control_plane/fog_is_not_an_error_test.exs` | fog is returned as an error rather than as a state |
| `test/sp/control_plane/absent_evidence_refuses_entry_test.exs` | an unbacked state is enterable |
| `test/sp/control_plane/liveness_only_from_probe_test.exs` | a node with `live: null` carries any liveness signal |
| `test/sp/control_plane/material_comes_from_truth_class_test.exs` | a style flag exists that can make simulated look observed |
| `test/sp/control_plane/claim_fence_in_the_scene_test.exs` | any material, label or token in the scene implies awareness, experience or life |

Each committed **red** with its output recorded.

**Standing procedure, now four phases old:**
- a guard that passes **vacuously** in red is not counted until a **mutation
  proves it bites**;
- any test that passes in red is **named in the receipt with the reason**;
- a **canary that fires is replaced by what it was guarding**, never deleted;
- when a guard is **weakened**, the trade is written down in the test itself;
- **a source scan states what it must not match**, because a scan that fires on
  itself is noise (Phase 6).

## 3. The one thing this phase must not get wrong

`ARCHITECTURE.md`'s render contract exists because **a picture persuades faster
than it can be checked.** A scene that looks alive will be believed to be alive,
whatever the caption says.

So the acceptance bar for 7.5 is not "no misleading label". It is: **a simulated
fixture and an observed fixture are distinguishable in a screenshot with no text
read**, and **nothing renders as awareness, experience or life** — which no
amount of styling can be argued into, because the claim fence is not a style.

This is the item to take to `/organic-operator` before believing my own eye.

## 4. Verification

```bash
cd ~/Documents/UNI.Minecraft
mix format --check-formatted        # repo-wide FAILS on lib/sp/brain/language.ex — known, item 7.8
mix compile --warnings-as-errors --force
mix test                            # capture the output; item 7.0 depends on it
mix test test/sp/control_plane
git diff mix.exs                    # MUST be empty
git diff ui/mix.exs                 # MUST be empty — no hex dep added to the UI either
sha256sum evidence/gates.ndjson     # MUST be unchanged
node viewer/gaia/verify_gaia.cjs
node viewer/gaia/gaia_lint.cjs
node viewer/gaia/verify_lint_bites.cjs
node viewer/gaia/witness_probe.cjs  # the off-box refusal is RE-MEASURED, never assumed
```

**Acceptance:** all seven red tests recorded red then green · every vacuous guard
mutation-tested · `mix.exs` and `ui/mix.exs` unchanged · `evidence/gates.ndjson`
byte-identical · Gaia still 12/12 · the witness still refuses the writer's key ·
**and the two fixtures distinguishable with no text read, reviewed by
`/organic-operator` and not only by me.**

**Rollback:** `Scene` is additive in the core. The renderer is additive in `ui/`
and removable without touching the core.

**Stop conditions:** `STOP_TEST_REGRESSION` · `STOP_PROTOCOL_CHANGE_REQUIRED` if
rendering appears to need a hex dependency in the core ·
`STOP_DESTRUCTIVE_ACTION_REQUIRED` before any write to the real gate ledger or to
any host — **item 7.7 begins in this state.**

## 5. Explicitly not in this phase

Any write to `evidence/gates.ndjson`. Moving a P-level. Authoring a verdict about
any real scientific claim. Going live. Any claim about awareness, experience or
life, in code, in a label, or in a material.

## 6. The corrections this programme carries

1. `prior` may be `null` at any `seq`. (P3)
2. Eleven corrective rows, not twelve. (P3)
3. `language.ex` is unformatted, not merely CRLF-terminated. (P3)
4. A run's identity is not its record. (P4)
5. A local anchor cannot outrank a local writer. (P4)
6. Capability is not practice. (P4, P5)
7. A premise check can itself be incomplete. (P5)
8. A signature the writer can produce is not a witness. (P5)
9. **The ledger entry had no home for a second key.** (P6)
10. **A source scan can fire on itself.** (P6)
11. **A fix can be worse than the defect it closes.** (P7, item 7.6) Making
    `material/1` total with a bare catch-all answered `:fog` — *somebody looked and
    there is nothing* — for `nil`, for an integer, for a whole `%Scene{}`. It
    collapsed absent into nil one level up, moved `entry/1`'s crash later rather
    than removing it, and **was mandated by its own test's regex**, so the guard and
    the defect agreed with each other. Green proved nothing.
12. **A fence can be reachable around.** (P7, item 7.6) `%Scene{}` is publicly
    constructible — Elixir cannot make a struct private — so a hand-built scene
    skipped `of/1` and handed a renderer a `:style` key that `node/2` refuses **by
    name**. The falsifier was reached without adding a function.
13. **The authority document is a second place that chooses the appearance.** (P7,
    item 7.6) Item 7.2's live-read guard did not bind row to class: swapping the
    `OBSERVED` and `SIMULATED` cells in §8.2 left the whole suite green.
14. **A signal filed as structural stops being read.** (P7, item 7.11)
    `drift.git_dirty_vs_clean` was an accepted oscillation and was pointing, unread,
    at a committed receipt its own commit could not reproduce. `STRUCTURAL` must
    mean *unequal by construction **and** both sides verified true, on this date, by
    this command* — never *unequal, stop looking*.
15. **A receipt captured from a dirty tree is evidence about a state no commit
    contains.** (P7) Standing procedure now records `git status --short` **inside**
    every receipt.

## 7. Exit condition — the phase ends by starting the next

**Phase 7 is complete only when `PHASE-8.md` exists, is committed, and is
pre-registered in this same form.**

`PHASE-8.md` must carry:

1. Every Phase 7 disposition, including each falsifier that fired.
2. Whether the two fixtures were distinguishable with **no text read**, and who
   said so besides me.
3. Whether item 7.7 happened, and the one approval that carried it.
4. Whether the unnamed Phase 6 failure was reproduced, retired, or is still open.
5. The Phase 8 build items — the flagellum method guards (`score.py`'s silent
   `zip` truncation, `fit.py`'s unchecked convergence, `compare.py`'s P-ladder
   off-by-one, `status.py`'s `OVERRUN` collapse, and `d5_distribution_guard.py`'s
   two defects) — each with a red test named before it is written, **in the
   flagellum repository, which this programme has not yet touched.**
6. Its own §7 requiring `PHASE-9.md`.

A phase that closes without its successor has stopped, and stopping is legitimate
only under a declared STOP condition.
