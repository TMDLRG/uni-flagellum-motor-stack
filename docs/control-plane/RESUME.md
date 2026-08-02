# PHASE 9 — RESUME POINT

*Marked 2026-07-28. This file is corrected whenever it becomes false; a resume point that lies is
worse than none. It had been false in every material clause since 2026-07-27 — see THE CORRECTION
at the end, which is kept rather than deleted.*

## THE NEXT ACT

<!-- BEGIN GENERATED uni.state.next_act — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**NEXT ACT: CHECKPOINT-E — the operator's.**

CHECKPOINT E -- the operator's. Two images side by side at http://127.0.0.1:8103/lab/l6. He says whether they differ with NO TEXT READ, and if so whether the reason is that the MATERIAL (truth_class) changed. That is the step's falsifier and it is M8, the operator's eye.

Declared at `stages[id=4].steps[id=4.6]`. Blocked on: M8 -- the operator's eye. No gate can stand in for it, and none is being asked to. Measured 2026-07-29: both images are real and they differ -- GET /api/lab/shot?swap=0 returns 3371 bytes and ?swap=1 returns 3375 bytes, both valid PNG, sha256 6eed6e94... and 0321be29..., embedded side by side at viewer/lab/l6.html:52-53. The surface is ready; the eye is not a gate.

Retired: **L6** (Stage 4 step 4.6 -- build L6, THE GAUNTLET THEN THE CO-SIGN, shipped `6234f3d`).
<!-- END GENERATED uni.state.next_act -->

The plan is the source of truth, not this file:
`UNI.Minecraft/evidence/remediation/phase9_plan.json`. `viewer/verify_plan_consistency.cjs` holds it
to its own vocabulary, because it had carried two different next acts at once — and since 2026-07-29
it also refuses a `$.next_act` that is absent or points backwards.

*This section said **"build L6"** for six hours after L6 shipped at `6234f3d`, and so did four other
documents. It is generated now.*

## WHERE THE STAGES STAND

| stage | status | detail |
|---|---|---|
| 0 CONSERVE | DONE | 5/5 |
| 1 THE INSTRUMENTS | DONE | 9/9 |
| 2 THE RECORDER | DONE | 7/7 — closed by step 2.7, the operator's ruling of 2026-07-27 |
| 3 THE REFUSALS | BLOCKED | 5 DONE, 3.3 BLOCKED on the operator (the presence mint is S6) |
| 4 THE UNRUN AND UNWIRED | IN_PROGRESS | 5 DONE; 4.6 IN_PROGRESS — every build DONE, waiting on Checkpoint E, which is the operator's |
| 5 THE DOCUMENTS | PLANNED | 4 PLANNED + 1 OPERATOR. Last, always — editing a document to match a broken world closes the only signal telling the truth |
| 6 THE FINAL RUN | PLANNED | 4 PLANNED + 1 OPERATOR |

<!-- BEGIN GENERATED uni.state.plan_tally — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Plan:** 7 stages · 43 steps (31 DONE · 1 IN_PROGRESS · 1 BLOCKED · 8 PLANNED · 2 OPERATOR) · 7 builds under step 4.6, 7 DONE.
<!-- END GENERATED uni.state.plan_tally -->

Step 2.7 was added during execution — a necessary repair, not an invention, and the register now
records it as such.

## MEASURED STATE

<!-- BEGIN GENERATED uni.state.gates — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Gates:** **34 registered**, of which **31 `ci:true`** and 3 `ci:false` (`colony`, `hud`, `overlays` — listed, never run, never a fabricated pass). **7 lab gates** (`lab-l0`, `lab-l1`, `lab-l2-shot`, `lab-l3`, `lab-l4`, `lab-l5`, `lab-l6`).

Both numbers are stated because both were written before without saying which was which:
one banner paragraph said 25 and another said 23, and a single file said 23 at one line and
25 at another. Neither was the registered count.
<!-- END GENERATED uni.state.gates -->

<!-- BEGIN GENERATED uni.state.gate_ledger — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Gate ledger** `evidence/gates.ndjson` — `1daac9124c0ce483...`, **207 rows / 110 unique names**. Last row per name: 93 PASS · 4 PARTIAL · 12 PENDING · 1 FAIL.

The per-name tally is stated as such because the per-ROW tally is a different set of numbers,
and a count whose derivation is unstated is how a backlog and the history of a backlog came
to be reported as one word.
<!-- END GENERATED uni.state.gate_ledger -->
<!-- BEGIN GENERATED uni.state.registry_ledger_gap — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Registry vs. the canonical ledger:** of **34 registered gates, 1 appear in `evidence/gates.ndjson`** and **33 do not** (0 of those carry a glob `gate_row`, which no kebab-case row can ever bear). `gate_row.schema.json` says every gate the project claims MUST be represented there.

**The intersection is NOT empty, and four governing documents said it was.** They declared "EVERY registered gate has ZERO rows" and "the intersection is empty by `id` *and* by `gate_row`" for two weeks after a row landed for one of them on 2026-07-17 — inside the paragraph that says these numbers are generated. It was hand-written. It is not any more.

Authoring the missing rows is **S4 — the operator's**, but the blocker is not his signature: `desk.preRegistration()` reports most of them blocked on an empty `receipt_path` the schema requires, which is a pre-registration document an agent owes him. He could not append them today even if he wanted to.
<!-- END GENERATED uni.state.registry_ledger_gap -->

<!-- BEGIN GENERATED uni.state.control_plane — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Control-plane ledger:** 32 entries, tip `b90b74980f47b93a...` at seq 32. Anchor declares length 32, head `b90b74980f47b93a...` — **they agree.**
<!-- END GENERATED uni.state.control_plane -->

<!-- BEGIN GENERATED uni.state.how_to_measure — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**Three things are deliberately NOT stated here, because no committed file can hold them
honestly.** They are facts about a *run* or about *now*, not about the tree:

| question | the command |
| --- | --- |
| Are the trees clean? | `git -C <tree> status -sb` |
| Does the Elixir suite pass? | `mix test` |
| Do the gates pass? | `node viewer/gate_runner.cjs` |

This banner used to answer all three. The gate-runner answer was measured at 06:01:09 on
2026-07-29 and was false by 06:04:06 — a half-life of 176 seconds — and it was committed
reading as present tense. Run the commands.
<!-- END GENERATED uni.state.how_to_measure -->

**Three gates are RED, and as of 2026-07-29 each reason is MEASURED, not inherited.**

- **`ip-fence` — red by acceptance, confirmed.** `8/8 self-checks PASS, 30 live literal(s)` against an
  acceptance asking for **≥12**: *"a green fence here is a broken walk."* Its M5 historical replay
  finds 34 uses on the pre-fix tree. Working exactly as designed.
- **`host-tracking` — 6 PASS / 1 FAIL**, and the one failure is `chip-names-resolve-via-dns`:
  `music -> 100.100.188.48 via=declared`, the name not answering so the stable overlay plane answers
  instead. On the operator's `not_mine` list. **This description was HALF WRONG until today** — the
  gate was failing **two** checks, and the second was `no-chip-literal-in-consumer-code` pointing at
  `viewer/track/verify_track.cjs:109`, a `10.190.245.5` inside the chip's real `/24` planted by an
  agent in a *fixture of addresses that must be refused*. A mention, not a use — and the fence was
  right anyway, because nothing distinguishes a fixture from a hardcoded endpoint by inspection.
  Swapped to RFC 5737 documentation space; the TRACK gate still passes 7/7.
- **`gate-attempts` — 8/9**, `evidence/gates.ndjson` hashes `1daac912…` against a pin of `964ea25c…`
  hardcoded in four places (so `mix test` is red too). Commit `2dcbfd2` legitimately appended a probe
  row carrying no pin update and no ledger entry. **Advancing that pin is S4 — the operator's.**

*The lesson worth keeping: two of these three were described in the documents by inherited prose, and
one of those descriptions understated a real defect authored by the agent that wrote the description.*

*This section used to state a test count, a gate-runner tally and "both trees clean". All three were
deleted rather than corrected: they are facts about a **run** or about **now**, and the gate-runner
one was measured at 06:01:09 on 2026-07-29 and false by 06:04:06 — 176 seconds — while committed
reading as present tense.*

## WHAT MUST NOT BE SOFTENED

1. **The off-box witness is COMPROMISED** — node2 accepts the writer's key,
   `independent_custodians: 0`. Tamper-evident, **not** unforgeable. Removing that key is **S1**.
<!-- @claim archived: this entry QUOTES the false declaration it replaces ("the intersection is empty").
     It was 1 of 32 from 2026-07-17. The quote IS the evidence; do not delete it. -->
2. **Most registered gates have no row in the canonical ledger — the count is in the generated block
   above, not restated here.** This used to read *"EVERY registered gate has ZERO rows... the
   intersection is empty by `id` **and** by `gate_row`"* — **false since 2026-07-17**. The row schema
   says every gate the project claims MUST be represented there. Appending is **S4 — the operator's**,
   but the blocker is NOT his signature: most rows are blocked on an empty `receipt_path` the schema
   requires, which is a pre-registration document an agent owes him. `/lab/l5` prints each exact line.
3. **No verdict has yet been authored about a real scientific claim**, and
   `runs/pureworld_qa_gate.exs` still raises `@scaffold`, so `colony_on_program` stays blocked.
4. **F31 is `presence_evident`, not unforgeable**, and it binds this codebase's paths only. The OBS
   WebSocket on `127.0.0.1:4455` still has **no authentication** — S2, the operator's studio.

## STILL OPEN, AND THE OPERATOR'S ALONE

- **ADR-0008** (human presence for go-live) is PROPOSED, **not adopted** — S5
- **the presence mint does not exist**, so the airlock has no door — S6
- **`truth_class` is absent from the gate row schema**, which is why the lab's floor is entirely
  fog — S5
- **S10 names a count and no members** ("the nine PENDING science gates"): the scaffolded set is
  EIGHT, pending now is TWELVE, ever pending is FIFTY-NINE. Nothing can enforce it. Naming the nine
  is his.
- **whether the three CLAUDE.md RESUME banners are S5-exempt.** Corrected 2026-07-28 on the reading
  that a block declaring itself "navigation and measured state only, it amends no law" may have its
  measured facts corrected without amending anything. Flagged for his ruling, not assumed closed.

## THE CORRECTION — what this file said until 2026-07-28, and why it is kept

Every material clause was false:

- *"Present the ledger collision to Michael and get his ruling before touching Stage 2 again"* —
  **resolved 2026-07-27** by step 2.7.
- *"Stage 2 is IN_PROGRESS, 5 of 6 DONE, 1 (step 2.6) marked `DONE_WITH_DEFECT`"* — false on every
  clause, and **`DONE_WITH_DEFECT` is not in the plan's status vocabulary at all**, which is the
  error step 3.3's own `status_correction` field warns about.
- *"Stages 3–6 are unstarted, PLANNED"* — Stage 3 is 5/6 DONE, Stage 4 is 5/6 DONE.
- *"mix test 1016 tests, 1 failure"*, *"42 steps"*, *"Gaia gate 12/12"*, *"ledger.ndjson now 11
  entries"*, *"not a production caller yet (Stage 4 item 4.1)"* — all superseded.
- *"the go-live guard is still a string comparison … F31 has no code and no test"* — F31 has a
  guard, a gate and an operator's prover.
- *"The next act: … then move to Stage 3"* — four stages stale.

It is kept because the failure is the lesson: **this file has no gate.** Nothing checks it, so it
drifts silently, and the only defence is that whoever reads it verifies the numbers against the
world first. The plan has `verify_plan_consistency.cjs`; this does not.
