# UNI PLATFORM — AGENT CALIBRATION PROMPT

*Paste the block below to a fresh agent. It is self-contained. Written 2026-07-26; updated 2026-07-27, and again 2026-07-28 when a sweep found this file's own
opening section instructing agents to halt on a defect that had been resolved the day before. Read the whole thing — several
mistakes below were made by your predecessor this same session, twice, and every one is cheap to repeat.*

---

## ⟢ THE ONE THING TO DO BEFORE ANYTHING ELSE

**Read `UNI.Minecraft/evidence/remediation/phase9_plan.json` and do what its `$.next_act` says.**
That file is the single source of truth, UNI TRACK renders it live, Gaia emits it verbatim, and
`viewer/verify_plan_consistency.cjs` holds it to its own vocabulary.

**Until 2026-07-29 this instruction pointed at a key that did not exist.** `$.next_act` was absent,
so the instruction silently fell through to the prose below it — and that prose said *"build L6"* for
six hours after L6 shipped at `6234f3d`. An instruction pointing at an absent field is worse than no
instruction, because it reads as satisfied. The key exists now, `verify_plan_consistency.cjs` check
3b fails if it is ever absent again, and the block below is **generated from it** rather than
restated. Do not trust a next act written in prose anywhere, including here.

<!-- BEGIN GENERATED uni.state.next_act — DO NOT EDIT. node viewer/generate_state_blocks.cjs -->
**NEXT ACT: CHECKPOINT-E — the operator's.**

CHECKPOINT E -- the operator's. Two images side by side at http://127.0.0.1:8103/lab/l6. He says whether they differ with NO TEXT READ, and if so whether the reason is that the MATERIAL (truth_class) changed. That is the step's falsifier and it is M8, the operator's eye.

Declared at `stages[id=4].steps[id=4.6]`. Blocked on: M8 -- the operator's eye. No gate can stand in for it, and none is being asked to. Measured 2026-07-29: both images are real and they differ -- GET /api/lab/shot?swap=0 returns 3371 bytes and ?swap=1 returns 3375 bytes, both valid PNG, sha256 6eed6e94... and 0321be29..., embedded side by side at viewer/lab/l6.html:52-53. The surface is ready; the eye is not a gate.

Retired: **L6** (Stage 4 step 4.6 -- build L6, THE GAUNTLET THEN THE CO-SIGN, shipped `6234f3d`).
<!-- END GENERATED uni.state.next_act -->

*Everything else in this file is hand-written and may be stale. Only what is inside a
`BEGIN GENERATED` / `END GENERATED` pair is regenerated from the artifact it describes.*

**Then read §6, KNOWN-FALSE DOCUMENTS, before trusting any other file in this repository.**

### What this section used to say, and why that matters more than what it says now

Until 2026-07-28 this — the first thing a fresh agent is told to read — opened with:

> **The test suite is RED — 1 failure — and Stage 2 is not closed.** … **Do not attempt to silently
> fix this.** Present the two options to Michael, get his ruling, act on it, then close Stage 2.

**Michael ruled on 2026-07-27. Step 2.7 closed it.** Seq 12 supersedes the seq 9 reference; Stage 2
is DONE, 7 of 7; the suite is green. A fresh agent following the old instruction would have stopped
and asked for a decision that had already been made — the most expensive possible failure for a
calibration document, because it is the one file written to be obeyed before anything is verified.

It is corrected in place rather than deleted, because a resume point that has been wrong is itself
the most useful thing it can tell you: **this file goes stale silently, nothing gates it, and you
should verify every measured number in it against the world before you act on it.**

---

## 0 · WHO YOU ARE WORKING FOR

**Michael Polzin — the organic operator.** He works by conversation, not by reading test output.

- **Speak** via `mcp__claude-voice__speak` for every finding, every phase edge, every adverse result, and
  every question that is his. Keep spoken lines under ~40 seconds or the call times out — **it has timed
  out repeatedly this session; if it does, say the thing in text instead of giving up on saying it.**
- **Adverse results are spoken FIRST**, never appended where they read as a footnote.
- **Correct yourself out loud, in the same breath, before acting on the correction.** This session did
  that twice for real mistakes (see §5, traps 13 and 14) and it read as trustworthy, not as failure.
- **Lead text with the outcome in one sentence.** Never open with a table, a heading, or a bullet list.
  Never paste test output — say "1016 tests, one failure" and move on.
- **Detail belongs in UNI TRACK, not in chat.** Post findings via `POST /api/comment` as they happen, not
  only at the end — this session missed one for several turns and had to catch up later. Don't repeat that.
- **Never offer him A/B menus for routine work.** The flow has one next act — take it, or recommend and
  ask for a co-sign. The ledger-collision choice above is a genuine exception: it is *his* decision, not a
  menu you're avoiding making yourself.
- He has said of himself: *"as the organic operator I am anxious and need to see what will happen before
  it does… i have no production nor broadcast experience."* Design for that.

## 1 · READ THESE FIRST, IN THIS ORDER

**Repo A — `C:\Users\mpolz\Documents\UNI.Minecraft`** (branch `gen2-runtime`) — the platform. All code.
**Repo B — `C:\Users\mpolz\Documents\UNI-Flagellum\UNI-FLAGELLUM`** (branch `hierarchical-aif/motor-stack`)
— governance + the flagellum science.

1. `UNI.Minecraft/CLAUDE.md` — the platform contract. **§93–97 is the strongest law and is currently
   false; see §6.** Its resume-point banner was stale twice — once describing pre-Stage-1 state, and
   again on 2026-07-29 in six places at once. **Its measured state is now GENERATED** by
   `node viewer/generate_state_blocks.cjs`; everything outside a `BEGIN GENERATED` pair in that banner
   is still hand-written and can still be wrong.
2. `UNI-FLAGELLUM/CLAUDE.md` — the science contract, the parity ladder `P0..P8`, and the binding
   operator-communication section. **Same generated-block note applies.**
3. `UNI-FLAGELLUM/docs/control-plane/ARCHITECTURE.md` — the body of record.
4. `UNI-FLAGELLUM/docs/control-plane/phases/PHASE-9-REMEDIATION.md` — the live phase register.
5. `UNI.Minecraft/evidence/remediation/phase9_plan.json` — **THE SINGLE SOURCE OF TRUTH for all work.**
   Read it FRESH every session — its hash changes every time a step closes, so don't trust a quoted
   hash from any document, including this one. **The step count is deliberately not stated here.** It
   said "42" while the plan held 43, in a sentence whose own point was that quoted values go stale.
   The count is in the generated block at the top of this file, and in `$.next_act` in the plan.
6. `UNI-FLAGELLUM/docs/control-plane/RESONANCE-TRIAGE-2026-07-26.md` — 17 original breaks, walked line by
   line. **5 of them were repaired in Stage 1 step 1.5 — see §2.5-B for exactly which and how.**
7. `UNI-FLAGELLUM/docs/control-plane/decisions/ADR-0001..0007` — especially **0001** (four bodies),
   **0002 + Amendment 1** (drift comparisons — Amendment 1's Decision 5 and Decision 8 governed all of
   step 1.5's work and are worth re-reading before touching any drift signal), **0003** (the Control Plane
   *is* the lab).
8. `UNI-FLAGELLUM/docs/control-plane/FAILURE-MODES.md` — F1–F31. **Still stale; correcting it is Stage 5,
   untouched this session.**

Then look at the live surfaces: **UNI TRACK `http://127.0.0.1:8102/`** (the plan renders at the top),
**Gaia `http://127.0.0.1:8096/api/gaia`**, **the Door `http://127.0.0.1:8090/`**, **the voice log
`http://127.0.0.1:5858`**. All three Node bodies were restarted off-air at the end of this session and
report `boot_git_commit = 937b7a7` — if they read differently when you check, either time has passed and
someone else restarted them, or they've gone stale again exactly as step 1.1 exists to detect. Check
`/api/identity` (Door, TRACK) or the envelope (Gaia) before trusting anything else they report.

## 2 · THE STATE, MEASURED 2026-07-27 (end of the session that ran Stages 1–2)

```
UNI.Minecraft   HEAD 937b7a7  gen2-runtime                 tree clean, pushed, origin matches
UNI-FLAGELLUM   HEAD 3e793f9  hierarchical-aif/motor-stack tree clean (untouched this session)
evidence/gates.ndjson  sha256 964ea25cfe8666ca…   206 rows — UNCHANGED ALL SESSION. S4 held throughout;
                        re-verified at the end, byte-identical to the value CLAUDE.md's banner cites.
hierarchical-aif frozen-evidence baseline          byte-identical, re-verified. S3 held throughout.
phase9_plan.json       42 steps: 19 DONE, 1 DONE_WITH_DEFECT, 20 PLANNED, 2 OPERATOR
mix test               1016 tests, 1 FAILURE — the seq-11 ledger collision. Nothing else is red.
Gaia gate              12/12 PASS · gaia_lint 0 violations · 6 new gates added this session (golden pins,
                        drift well-formedness, deploy-lag tripwire, capture-age fence, witness-blocked,
                        boot-identity already existed from 1.1)
Gaia drift signals      resonance (drift.remediation_plan_vs_artifacts) = equal:true, live, on current code.
                        witness independence (drift.witness_independence) = equal:false — CORRECT, S1 still
                        stands. capture-age fence (drift.capture_age_fence) = equal:false — CORRECT,
                        real captures are genuinely stale (replica capture from 2026-07-26T03:33, witness
                        capture from 2026-07-26T17:05); this is honest, not a defect.
Door :8090 UP (boot 937b7a7) · Gaia :8096 UP (boot 937b7a7) · TRACK :8102 UP (boot 937b7a7) ·
HUD :8100 UP (MVID served since step 1.1, service-account swap done, not re-verified this session)
CI                     runs for real now (first time ever in this repo's history, confirmed via
                        `gh run list` returning zero rows before step 1.3). gates-node, gates-python,
                        Test & QA, Overlooker UI all wired. A real push (not just the canary) has run:
                        gates-node RED on host-tracking (known, not_mine); Test & QA RED on 10 pre-existing
                        defects unrelated to any change this session made (see §2.4 below).
Control Plane          ledger.ndjson NOW 11 entries (was 7 at session start). Verifies structurally,
                        anchored. ONE entry (seq 11) cannot pass the pre-existing evidence-rehash test —
                        see the banner at the top of this file and §2.5-A.
```

### The five things that must not be softened (updated from four — one resolved, one is new)

1. **NEW, ACUTE: seq 11 of the Control Plane ledger cannot pass its own evidence-rehash check, and cannot
   be repaired without either accepting it permanently or rebuilding the ledger.** See the banner at the
   top and §2.5-A. This is the most acute open item and gates Stage 2's closure.
2. **The off-box witness is still COMPROMISED**, unchanged since 2026-07-26. node2 answers the writer's
   own key, `independent_custodians: 0`. **Now READ and ENFORCED**, not merely true and unread: step 1.8
   built `drift.witness_independence`, which forces the claim to `BLOCKED` rather than letting it render
   silently, and `viewer/gaia/verify_witness_blocked.cjs` proves the refusal (not the repair) is real.
   **Removing the writer's key remains S1 — the one repair an agent must not perform.**
3. **Phase 7 FAILS its own acceptance** — 2 of 7 clauses, unchanged: the witness clause, and *"two
   fixtures distinguishable with no text read"* (the renderer was never built). **Now formally RECORDED**,
   not merely known: the Control Plane's own ledger states `acceptance: "NOT_MET"` at seq 9, with both
   failing clauses named in the entry, and a test (`phase7_is_not_recorded_as_a_pass_test.exs`) reads the
   real ledger every suite run and fails if anyone ever supersedes that with a passing entry.
4. **RESOLVED, not softened: the Door and both watchdogs were 50 commits behind; this specific staleness
   is fixed.** Step 1.1 built boot-time build identity for all four bodies (a `module_set_sha256` for Node,
   an assembly MVID for the HUD, loaded-bytecode hashing for the Control Plane). The healer now
   annunciates a stale body but **never auto-restarts, and never restarts under air** — the general risk
   of a body running stale bytes is now *detected*, not eliminated, which is the honest claim to make.
5. **The Control Plane's own ledger stopped recording at Phase 5 — RESOLVED for the record, with a real
   mistake attached.** Phases 6 and 7 are now backfilled (step 2.4), the repair of the recorder itself was
   bootstrapped honestly — the ledger states it *ingested an account* and explicitly did **not** witness
   Stages 0–2 (step 2.5) — and an anti-silence guard now fails the suite if any future DONE step goes
   unrecorded (step 2.6). **But closing 2.6 is where the seq-10/seq-11 collision happened** — see item 1.
   Separately, unchanged: **no verdict has ever been authored about a real scientific claim.** That is a
   different, still-true, still-open fact (Stage 3/4 territory, F28–F31, the nine PENDING science gates)
   — do not conflate "the ledger records process history again" with "a scientific verdict exists."

## 2.5-A · THE LEDGER COLLISION, IN FULL

Step 2.6 needed a *current* account of Stages 0–2's completion (the bootstrap script derives one from
`phase9_plan.json` and writes it to `evidence/remediation/prelude.ndjson`). The prior account, ingested at
seq 10 in step 2.5, lived at that same path. Regenerating and re-ingesting overwrote the file **and then
ingested the new bytes as seq 11**, while seq 10's ledger entry still names the *old* hash against the
*same path name*.

```
seq 10  resulting.prelude_sha256 = 6d9e1e0d1fea783b6746e7c66da57c7f4216855971622870c6a02502376fdb46
seq 11  resulting.prelude_sha256 = 2c87d457ee38d3a4d75177bbfe0385a760959990dcfb509f229bf4675d37f572
both    resulting.prelude_path   = "evidence/remediation/prelude.ndjson"   (ONE path, mutable)
```

One file cannot hash to two values. `control_plane_ledger_is_real_test.exs`'s check that *"EVERY piece of
evidence exists on disk and rehashes to what the entry recorded"* will therefore **always** fail for
exactly one of these two entries, whichever bytes the file currently holds. As of `937b7a7`, the file
holds seq 10's original bytes (restored deliberately, so the *older* reference — valid when it was made —
is intact), and the live failure sits on seq 11.

**This cannot be fixed by editing.** The ledger is append-only:
- Seq 11 cannot be edited or withdrawn without violating the append-only property.
- Appending a *third* entry does not stop the test from reading seq 11's (now permanently wrong) evidence.
- Restoring the file satisfies seq 10 and breaks seq 11; the newer bytes would satisfy seq 11 and break
  seq 10. There is no third state.
- There was, in fact, **never a single git commit** where both entries' evidence was simultaneously
  correct on disk — check this yourself with `git log -p -- evidence/remediation/prelude.ndjson` before
  assuming otherwise. This may be worth formally classifying against **S9** ("a receipt cannot be
  reproduced from its own commit"), though S9 as written speaks of *receipts*; whether a Control-Plane
  ledger evidence entry is the same class of thing is worth a considered answer, not an assumption either
  way.

**What was mitigated, not fixed:** both accounts now exist forever, immutable and content-addressed, at
`evidence/remediation/prelude_6d9e1e0d.ndjson` and `evidence/remediation/prelude_2c87d457.ndjson` — no
bytes are lost, and both remain independently hash-verifiable by anyone. The bootstrap script
(`scripts/control_plane_bootstrap_prelude.exs`) now *also* writes an immutable, content-addressed copy on
every run, so this specific class of mistake cannot recur going forward — but it does not and cannot touch
the two entries already committed.

**The lesson, stated for the trap list too (§5, trap 14): an append-only record must never point at a
mutable path. Evidence has to be content-addressed at the moment it is first referenced, never afterwards.**

**Present both paths to Michael, plainly, and let him choose:**
- **(a) Accept a permanently-red entry**, with this whole account attached to it in the plan and the
  ledger's own commit history. The ledger stays honest about its own repair having gone wrong once — which
  is arguably the most on-brand outcome this whole programme could produce.
- **(b) Authorise a ledger rebuild.** This is NOT a small ask: rebuilding an append-only ledger is exactly
  the class of action `S3`/`S4`-adjacent caution exists to prevent by default, and doing it would need its
  own explicit, narrow authorization and its own new proof that the rebuild is faithful to everything the
  ledger legitimately recorded (all 9 prior entries, correctly). Do not default to this path because it
  "sounds cleaner" — it is the larger, riskier decision of the two, not the safer one.

Do not silently pick one. Speak the finding first (it is an adverse result — see §0), present the choice,
and act only once Michael rules.

## 2.5-B · WHAT STAGE 1 AND STAGE 2 ACTUALLY BUILT (so you don't re-derive it)

**Stage 1 — THE INSTRUMENTS — DONE, 9/9, closed and cross-verified against itself (step 1.9's own
proof-2 re-inventory, from a clean worktree, diffed against the Stage-0 baseline, changed rows and
unchanged rows both shown).**

- **1.1** Boot-time build identity on all four bodies. `viewer/build_identity.cjs` (Node), assembly MVID
  (HUD), loaded-bytecode hashing (Control Plane, `SP.ControlPlane.BuildIdentity`). The healer's second
  clause annunciates, never restarts. **Found and fixed a real defect via proof 2:** the HEAD reader
  returned `null` inside a git worktree (`.git` is a *file* there, not a directory) — fixed, worktree-aware.
- **1.2** `viewer/gate_runner.cjs` invokes every registered node gate un-piped and asserts
  `exit==0 <=> verdict==PASS` + registry completeness. Caught its own author's registry gap
  (`viewer/hud/verify_hud.cjs` missing) red-first.
- **1.3** CI actually runs — confirmed it had NEVER run, ever, via `gh run list` returning zero rows.
  Fixed the trigger (`gen2-runtime` was never in the matched branch list). Watched a canary go red live
  on GitHub Actions (run `30226371980`), then deleted the canary branch. **Corrected a prediction against
  real measurement afterward: `bridge_test.exs` was predicted to fail on Linux from a local Docker
  reproduction — it actually PASSES in real CI; the local failure was a Docker resource artifact and was
  retracted. The git-history test was predicted to pass with `.git` present — it actually FAILS in real
  CI, because `actions/checkout` uses `fetch-depth: 1`, which a full local clone had masked.** Read that
  retraction in full before trusting any container-based CI simulation again — match the checkout depth,
  not just "does `.git` exist."
- **1.4** Golden sha pins on Gaia's 3 core sources. Found the pin was **self-erasing**: deleting the
  manifest, or dropping one file's entry, made an edited file read "unpinned" and raised nothing. Fixed.
  Then **found the pins didn't survive a checkout at all**: every `.cjs` blob in git is pure LF, but with
  no `.gitattributes` rule, Windows checked them out 42-CRLF/53-LF split — a Windows-taken pin could never
  match Linux CI. Fixed with `*.cjs text eol=lf`; renormalized; verified on Linux with `sha256sum`
  (a tool sharing no code with the subject).
- **1.5** Repaired 4 of the 5 malformed drift comparisons named in Amendment 1 (prose-vs-path,
  prose-vs-array, JSON-vs-document category errors) so `equal:true` is *reachable*. **Two converged the
  instant they became well-formed** (`gate_row_schema_path`, `self_caps_doc_vs_served`) — proving Amendment
  1's own claim that the "corrections already made become visible as progress." The other two
  (`fqdn_cjs`, `resolver_planned`) now each name one actionable fact instead of thousands of bytes of
  category error — and `resolver_planned` independently rediscovered the exact `music.uni-lab.local`
  finding host-tracking already carries (cross-instrument corroboration, unprompted). The 5th family
  (`replica_ledger.*`) was deliberately **not** repaired — see 1.6.
- **1.6** `drift.deploy_ref_behind_head.<build>` with relation `lag` (Amendment 1 Decision 6). No
  tolerance anywhere — uses the ledger's append-only property: an honest lag must be a byte-exact prefix
  of canonical. **Found live: of 3 chip deployments, 1 is a clean prefix (lag 15/206), 2 are NOT prefixes
  of canonical at ANY length under ANY normalization** — a real divergence the old digest-vs-digest
  comparison could never distinguish from ordinary lag.
- **1.7** Capture-age fence, bound 3600s (inherited from `SP.ControlPlane.Witness`'s own bound, not
  invented). Found both real captures already stale (23.7h and 10.2h) and were being rendered as current
  values with no age test at all. Now withheld as `STALE_CAPTURE`, not silently served.
- **1.8** `independent_custodians: 0` now forces `BLOCKED`. The number was **computed and written on every
  capture and read by nothing** — not a wrong value, a correct one nobody consulted. Fixed; proven to
  clear if a real custodian ever appears (not a constant "no").
- **1.9** Re-ran Stage 0's instrument inventory from a clean worktree, diffed, showed unchanged rows.
  `host_tracking` was byte-identical and still exit 1/FAIL — **the honesty check that mattered**: nothing
  improved by accident.

**Stage 2 — THE RECORDER — 5 of 6 DONE, 1 (2.6) DONE_WITH_DEFECT, stage marked IN_PROGRESS. Do not close
it until the operator rules on §2.5-A.**

- **2.1** Direct tests for `GateRow.new/1` and `Store.write_artifact`. Found a REAL path traversal:
  `write_artifact/2` took a whole path and wrote it with zero containment. Fixed
  (`write_artifact/3` takes dir+filename separately, refuses escapes). **Self-caught a real regression
  mid-fix**: the first patch to `Run.score_to/3` wrote the artifact *before* checking `may_score?/1`,
  breaking "a halted run leaves no artifact behind." Fixed in the same breath.
- **2.2** Restored `seat_projects_verbatim_test.exs` — pre-registered at `PHASE-5.md:63`, never written,
  never mentioned again for **four phases**. Nothing noticed. That silence is the actual failure this step
  closes, more than the test's content.
- **2.3** `SP.ControlPlane.Recorder` — loads what's stored and appends one entry, instead of rebuilding
  the whole chain from a literal list (what the old script did, which would have jammed the moment any
  historical receipt's bytes changed even slightly — and 2.4 needed to append to that exact ledger).
  **F10 (the "only Command may write" guard) caught a direct `Ledger.append` call in the first draft** —
  the guard was right, the draft was wrong; fixed to submit through `Command`.
- **2.4** Backfilled Phases 6–7. Phase 7 recorded `acceptance: "NOT_MET"` with both failing clauses named
  in the entry — the pre-registered falsifier for this step, honoured. **Self-corrected a wrong test
  assumption:** assumed at most one ledger entry per phase; Phase 5 legitimately has three (per-item, not
  per-phase) — the ledger was right, the test was wrong, fixed.
- **2.5** THE BOOTSTRAP. The recorder was broken *during* Stages 0–2, so it could not witness its own
  repair. The account went to a prelude file that says in its own bytes it is not the ledger; the ledger
  records only that it *ingested* that account (`transition: "account.ingested"`,
  `witnessed_by_this_ledger: false`, explicit). **This is where the mutable-path mistake was made on the
  re-run — see §2.5-A.**
- **2.6** The anti-silence guard (`ledger_has_not_fallen_out_of_practice_test.exs`) — **it works and it
  fired on real data before it passed**, correctly reporting step 2.5 as done-but-unrecorded before the
  account was refreshed. That's the property the falsifier demanded. Closing it is what produced the
  seq-11 collision.

## 3 · THE FLOW — non-negotiable

```
OBSERVE -> BOUND -> PREDICT -> ACT -> VERIFY -> FALSIFY -> UPDATE -> RECORD -> NEXT_ACT
```

Every RECORD ends with a NEXT_ACT. **Writing a report, passing tests, or declaring alignment are not
stopping conditions.** Stop only on a declared STOP (§7).

### The four-proof cycle — binding for every step, and it earned its keep again this session

| | what it is | how it fails |
|-|-|-|
| **1 · PROVE** | red first, **failing for the pre-registered reason**, smallest fix, green. | it passed for the wrong reason |
| **2 · RE-MEASURE** | re-run the *instrument* from a clean `git worktree`, diff against baseline, **show unchanged rows too**. | it measured the same wrong thing twice |
| **3 · A DIFFERENT METHOD** | named BEFORE you start; shares no code with the subject; run against the repaired function. **If it disagrees with proof 1, proof 3 wins.** | a hidden shared dependency |
| **4 · THE OPERATOR PROVES IT** | one command, prints its own expected output. | he checked something that wasn't the claim |

**Proof 2 (the clean-worktree remeasure) found two real, separate defects this session** — the worktree-null
HEAD reader (1.1) and the CRLF checkout mismatch (1.4). **Proof 3 (a different method) found that a local
container simulation is not the same instrument as real CI** (1.3's bridge_test/git-history retraction).
Neither proof is a formality. Do them for real, or you will ship exactly the class of bug they exist to
catch.

### Standing procedure — updated with what this session earned

- A guard that passes **vacuously** is not counted until a **mutation proves it bites**.
- Any test that passes in red is **named in the receipt with the reason**.
- **A canary that fires is REPLACED by what it was guarding, never deleted.**
- **A source scan states what it must NOT match** (use vs mention — this convicted honest documentation
  again this session, twice: a schema-path citation inside a comment *explaining* the trap, and a fixture
  path inside a comment *describing* the fixture. Even your OWN new gate's comments are not exempt.)
- **Every receipt records `git status --short` at capture time.**
- **BLOCKED is a reportable outcome, never a pass.** *Unreachable* and *compromised* never collapse.
- **NEW: format under the CI toolchain, not your local one.** `mix format` under Elixir 1.19.5 (this box)
  and 1.18.4 (CI) disagree on real code — 81 files disagreed this session, a genuine version-behavior
  difference, verified via a clean-room Linux container run before touching anything, not assumed.
  Reformat inside a matching container (`elixir:1.18-otp-27` via Docker) before every commit that touches
  `.ex`/`.exs` files, and re-verify `mix format --check-formatted` inside that same container.
- **NEW: an append-only record must never point at a MUTABLE path.** Evidence referenced by hash must be
  content-addressed at the moment it is first referenced — see §2.5-A. Learned by breaking it, this session.
- **NEW: identity/coverage checks over a shared field are vacuous.** The ledger's own `transition` field is
  `"phase.executed"` for every one of its entries — `recorded?(transition)` cannot distinguish one phase
  from another and would silently report every phase as already-recorded. Use a predicate over the
  *content* (`recorded_by/2`), never equality on a field the domain doesn't actually vary.
- **NEW: piping a live/long-running command loses its real exit code — reconfirmed, not just remembered.**
  `gh run watch ... | tail -60` reported a misleadingly-successful exit while the underlying CI run had
  actually failed, on this session's own watch of a real GitHub Actions run. This is the *exact* Stage-0
  lesson (trap #1 below), caught again, in a brand-new tool, because the lesson is about pipes in general,
  not about any one script.
- **NEW: a repo's own pre-existing guard catching YOUR new mistake is a good outcome, not a bad one — say
  which it is.** Both `F10` (step 2.3) and the evidence-rehash test (step 2.6) caught real mistakes made
  *this session*, before any human did. Report them as "the guard worked," not as unrelated bad luck.

## 4 · THE PLAN IS LIVE — UPDATE THE FILE, NOT A DOCUMENT

`UNI.Minecraft/evidence/remediation/phase9_plan.json` is the source of truth. **TRACK renders it live and
Gaia projects it verbatim.** When a step completes, **you edit that file** — the surfaces follow
automatically. Its hash changes every edit; never trust a quoted hash for it, including any in this file —
read it fresh.

`drift.remediation_plan_vs_artifacts` — **THE RESONANCE SIGNAL** — compares what the plan **claims** is
DONE against what **exists on disk**, live, on whatever code is currently running. Verified at the end of
this session, on freshly-restarted current code: **`equal: true`.** If you mark a step DONE whose artifact
is absent, it goes unequal immediately.

**Your next act is presenting §2.5-A to Michael and getting his ruling — before touching Stage 2 further.**
Once ruled, close Stage 2 accordingly (the plan's own status field for stage `2` and step `2.6` need to
move from `IN_PROGRESS`/`DONE_WITH_DEFECT` once resolved) and proceed to **Stage 3 — THE REFUSALS THAT DO
NOT EXIST** (F28–F31 tests; F31 in particular — the go-live guard is a string comparison on unauthenticated
loopback `:8098`, and it has no code and no test yet).

## 5 · THE TRAPS — every one of these has already caught someone, several caught someone THIS session

1. **NEVER pipe when you need an exit code.** `node gate.cjs | tail -3` gives you *tail's* status. This
   produced a false Stage-0 defect report, AND it produced a false "the CI run succeeded" reading this
   session (`gh run watch | tail`) — same trap, different command, months apart in the programme's life,
   caught both times only by reading the raw output instead of trusting the pipe's exit code.
2. **USE vs MENTION has convicted honest documentation SEVEN times now, not five.** Two new convictions
   this session: a schema-path citation inside a comment *explaining* why the path must not appear, and a
   fixture IP/path inside a comment *describing* the fixture. Even a brand-new gate's own explanatory
   comments are not exempt from the fences it enforces on everyone else.
3. **A FIX CAN BE WORSE THAN THE DEFECT.** Phase 7 item 7.6, unchanged from before. This session's closest
   call: the first `Run.score_to/3` patch (step 2.1) wrote the artifact before checking `may_score?/1`,
   caught and fixed in the same breath before it was committed.
4. **A FENCE CAN BE REACHABLE AROUND.** Unchanged example (Scene/`:style`).
5. **DO NOT EDIT `ARCHITECTURE.md` §8.2 or add a function to `SP.ControlPlane.Scene`.** Unchanged.
6. **`git diff ui/mix.exs` and `git diff mix.exs` must stay meaningfully understood, not blindly empty.**
   The root `mix.exs` WAS changed this session — deliberately, to drop Elixir 1.17 (operator-ruled) — so
   "must stay empty" is now the wrong instruction; the right one is "any change to it must be a ruled,
   explicit decision, never incidental." Re-read `elixir: "~> 1.18"` and its adjacent comment before
   assuming the version floor is still 1.17.
7. **GAIA NEVER COMPUTES.** Unchanged, and every new signal this session (golden pins, drift
   well-formedness, deploy-lag, capture-age, witness-independence) was built to that law: project the
   source's own fields verbatim, name the blocking conditions, never author a verdict.
8. **A signal filed as STRUCTURAL stops being read.** Unchanged principle; this session's
   `drift.deploy_ref_behind_head` exists specifically so a lag (structural, expected) and an in-place edit
   (a real fault) never collapse into one unreadable "digests differ."
9. **CODE BEFORE DOC, EVERYWHERE.** Unchanged. One exception exercised this session: the *retraction* of
   finding (B) about the gate ledger having "drifted" (it hadn't — it was a CRLF checkout artifact) was
   corrected the moment it was discovered, in the plan file, in TRACK, and out loud — because a wrong
   finding left standing is worse than the finding itself.
10. **Don't restart a long-lived service casually.** Unchanged, but this session also shows the other side
    of it: restarting off-air, deliberately, to serve current code IS the correct move once you've
    confirmed off-air and have a reason (proving a fix landed, or — as at the very end of this session —
    confirming resonance against genuinely current code instead of a 5-commits-stale process).
11. **Any unknown working-tree change is USER-OWNED.** Unchanged.
12. **NEW: CI's declared toolchain and your local one are not the same Elixir, and `mix format` disagrees
    between them on real code.** Format inside a matching container before every commit touching `.ex`/
    `.exs`; do not trust your local `mix format --check-formatted` as CI's answer.
13. **NEW: an append-only record must never point at a MUTABLE path.** See §2.5-A. This is the newest,
    still-unresolved defect in the whole programme as of this handoff.
14. **NEW: `.gitattributes` does not cover every extension by default, and a Windows-taken hash can never
    match a Linux CI checkout of the identical commit if it doesn't.** Caught for `.cjs` (step 1.4, fixed)
    and for `evidence/gates.ndjson` (misdiagnosed as ledger "drift," then correctly retracted — it was
    CRLF-vs-LF, not content drift). Before trusting ANY cross-platform hash comparison, check
    `git show HEAD:<path>` (the blob) against the working-tree file for CR bytes.
15. **NEW: identity/coverage checks must use a predicate over content, never equality on a shared field.**
    The ledger's `transition` field cannot distinguish phases from each other. Use `recorded_by/2`, and
    audit any future "is this already done?" check the same way before trusting it.
16. **NEW: a container-based CI simulation is not CI. Match the checkout depth, not just presence of `.git`.**
    A full local clone masked a real `fetch-depth: 1` failure in step 1.3; a local Docker Desktop
    environment produced a Port-timeout failure that real CI never showed. Trust real CI's own measured
    result over any local proxy, always — and say so explicitly when correcting a proxy-based prediction.
17. **NEW: touching MANY files' mtimes at once (a bulk renormalize, a mass line-ending fix) can put Mix's
    incremental compiler into a transiently INCONSISTENT state**, even when the byte content is provably
    unchanged. Caught at the very end of this session: renormalizing 278 `.ex`/`.exs` files' line endings
    (content-identical, verified via `git diff --stat` showing nothing) made `test/sp/golden_test.exs`
    fail with a wildly different result (46 vs 250 survived ticks) immediately afterward — which looked
    exactly like a real behavioral regression. **It was not.** `mix clean && mix compile --force` followed
    by a fresh `mix test` reproduced the correct, golden-matching result every time. Before treating ANY
    surprising test failure that follows a bulk file-touch as a real finding, rule out incremental-compile
    inconsistency FIRST with a full clean rebuild — it is cheap, and the alternative is reporting a false
    regression (or worse, silently "fixing" a golden file that was never actually wrong).

## 6 · KNOWN-FALSE DOCUMENTS — do not trust these lines

- **`UNI.Minecraft/CLAUDE.md:93-97`** — names `viewer/fqdn.cjs` as the enforcement seam. **That file has
  never existed on any ref.** **RECONFIRMED independently this session** via the now-repaired
  `drift.fqdn_cjs` signal, which reads live: `a="viewer/fqdn.cjs"`, `b=""`. Two unrelated instruments
  (the original investigation, and this session's drift-signal repair) now agree. **Correcting this is
  step 5.5 of the plan and is explicitly `OPERATOR`-gated — not yours.**
- **`ARCHITECTURE.md:372-379`** — still claims the witness refuses the writer's key. Still false, unchanged.
- **`ARCHITECTURE.md:365,:370,:390`**, **`README.md:3`**, **`RESUME.md`** (see below), **`FAILURE-MODES.md:3,:127`**
  — all stale; each is a step in Stage 5, untouched this session.
- **`PHASE-7.md:79`** — unchanged, still a Stage 5 item.
- **`RESUME.md`** was updated as part of this handoff to reflect Stage 1 DONE / Stage 2 IN_PROGRESS — it
  should now agree with this file. If it doesn't when you read it, something changed since and this note
  is itself now stale; trust the live plan JSON over any document, always.
- **The resume-point banners at the top of `UNI.Minecraft/CLAUDE.md` and `UNI-FLAGELLUM/CLAUDE.md`** —
  both still describe the 2026-07-26, pre-Stage-1 state (Stage 0 only). Both banners explicitly say
  *"navigation and measured state only, amends no law"*, which reads as an invitation to correct them —
  but this agent chose **not** to edit `CLAUDE.md` at all this session, given `S5` ("any contract
  amendment — CLAUDE.md, an ADR, a FAILURE-MODES.md statement") names that whole file, and the banner's
  own claim to be law-free is not the same as it being unambiguously outside `S5`'s scope. **This is worth
  a direct, explicit ruling from Michael** — either "yes, the banner is fair game, keep it current
  yourselves" or "no, treat all of CLAUDE.md including the banner as S5." Ask, rather than assume either way.

## 7 · STOP CONDITIONS — halt and wait

| | | held this session? |
|-|-|-|
| **S1** | The writer's key on node2. THE ONE REPAIR YOU MUST NOT PERFORM. | **Held.** Never touched; witness-blocked signal built to detect and refuse, not repair. |
| **S2** | Any write to a host (ssh, MCP mutation, deploy) | **Held.** No host was written to; all off-air restarts were local process restarts, not deploys. |
| **S3** | Any write to a frozen artifact | **Held.** Frozen-evidence baseline re-verified byte-identical at session end. |
| **S4** | Any write to `evidence/gates.ndjson` | **Held.** Re-verified byte-identical (`964ea25c…`) at session end, despite extensive gate-related work elsewhere. |
| **S5** | Any contract amendment — CLAUDE.md, an ADR, a FAILURE-MODES.md statement | **Held.** CLAUDE.md untouched, including its arguably-law-free banner (see §6). |
| **S6** | Go-live, in any form | **Held.** Not approached; Stage 3+ territory. |
| **S7** | Proof 3 disagrees with proof 1 — speak it, stop | **Fired once, correctly**: step 1.3's real-CI result disagreed with the container-based proof 3 prediction on 2 of 11 tests; spoken, corrected, not silently reconciled. |
| **S8** | A pre-registered falsifier fires — that is a RESULT | **Fired several times, all correctly reported**: the F10 catch (2.3), the evidence-rehash catch (2.6), the golden-pin self-erasure (1.4), the 2.6 guard's own pre-fix red result. |
| **S9** | A receipt cannot be reproduced from its own commit | **Possibly adjacent to the seq-11 collision — see §2.5-A. Not formally invoked; worth the next agent or Michael classifying explicitly rather than assuming either way.** |
| **S10** | Running any of the nine PENDING science gates | **Held.** Not approached. |

**Proceed without stopping:** writing a red test · reading anything · committing to the working branch ·
correcting yourself out loud · restarting a Node body off-air once you've confirmed off-air and have a
reason.

## 8 · NOT YOURS

The ledger-collision choice in §2.5-A (accept-red vs. rebuild) · the writer's key on node2 (and with it
items 7.7/8.10) · the router's `[redacted: client-identifier]` search suffix · whether `music.uni-lab.local` is a real
service · the colony ruling (close the science, or narrow the fence on the record) · `CLAUDE.md:93-97` ·
whether the CLAUDE.md resume-point banners are `S5`-exempt (see §6) · **go-live**.

## 9 · THE ROAD TO AIR — untouched this session, still runs THROUGH the science

Go-live is blocked by exactly two computed gates in `viewer/infra.cjs:244-285` — `plumbing` (2 of 6 up) and
`colony_on_program` (blocked on a science gate whose runner raises `@scaffold`). **The go-live guard is
still a string comparison** on unauthenticated loopback `:8098`, guarding 1 of ≥5 paths to air. **F31 has
no code and no test.** This is Stage 3 step 3.3 and remains the most safety-relevant unbuilt item in the
programme. Nothing in this section changed this session — Stages 1–2 were entirely about instruments and
the recorder, not about air.

## 10 · VERIFY EVERYTHING WITH THESE

```bash
cd C:/Users/mpolz/Documents/UNI.Minecraft

mix clean && mix compile --force --warnings-as-errors  # ALWAYS do this before trusting a test count if you
                                                        # or a prior session touched many files' mtimes at
                                                        # once (see §5 trap 17) — an incremental-compile
                                                        # inconsistency can produce a false regression.
mix test                                        # expect 1016 tests, 1 failure (seq-11 collision — see §2.5-A;
                                                 # do NOT try to make this pass without an operator ruling)
git diff mix.exs                                # NOT expected empty anymore — "~> 1.18" is the ruled floor
sha256sum evidence/gates.ndjson                  # 964ea25c… — unless S4 was authorised since this was written

node viewer/gate_runner.cjs                     # law-consistent across all registered gates; host-tracking
                                                 # is the one known, tracked, not_mine FAIL
node viewer/verify_gate_runner.cjs              # the runner's own meta-gate
node viewer/gaia/verify_gaia.cjs                # 12/12 PASS
node viewer/gaia/gaia_lint.cjs                  # 0 violations
node viewer/gaia/verify_golden_pins.cjs         # NEW, step 1.4 — 5/5
node viewer/gaia/verify_drift_wellformed.cjs    # NEW, step 1.5 — 5/5
node viewer/gaia/verify_capture_age_fence.cjs   # NEW, step 1.7 — 6/6
node viewer/gaia/verify_witness_blocked.cjs     # NEW, step 1.8 — 6/6, proves the REFUSAL not a repair
node viewer/gaia/verify_deploy_lag_tripwire.cjs # NEW, step 1.6 — 5/5
node viewer/reinventory_gates.cjs               # NEW, step 1.9 — Stage 1's own proof-2 instrument
node viewer/verify_host_tracking.cjs            # exits 1: music.uni-lab.local — PRE-EXISTING, not_mine

curl -s http://127.0.0.1:8102/api/track | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const p=JSON.parse(s).plan;const st=p.stages.find(x=>x.id==='2');console.log('stage2:',st.status)})"
curl -s http://127.0.0.1:8096/api/gaia | node -e "let s='';process.stdin.on('data',d=>s+=d).on('end',()=>{const j=JSON.parse(s);const r=(j.result.signals||[]).find(x=>x.id==='drift.remediation_plan_vs_artifacts');console.log('resonance equal:',JSON.parse(r.value.raw).equal)})"

cd C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM
diff -q hierarchical-aif/reports/frozen-evidence-baseline.sha256 \
  <(find audits/phase-c audits/phase-d -type f -print0 | sort -z | xargs -0 sha256sum)   # MUST be identical
```

## 11 · WHAT "DONE" MEANS

The programme is finished when, and only when:

- every step in `phase9_plan.json` is `DONE` with its four proofs recorded, or is honestly
  `BLOCKED`/`OPERATOR`/`DONE_WITH_DEFECT` **with the reason named** — *(vocabulary note: `DONE_WITH_DEFECT`
  was introduced this session for step 2.6; it is not yet in `status_vocabulary` in the plan schema and
  should probably be added there formally, or resolved away entirely once §2.5-A is ruled)*;
- **the lab exists**, and a simulated fixture and an observed fixture are distinguishable in a still
  screenshot with no text read — **untouched this session, Stage 4**;
- **every Node gate runs in CI, and a canary branch has been watched to go red** — **DONE, step 1.3**,
  watched live on GitHub Actions run `30229474567` (canary) and the real push's own run `30229474567`
  region — check the plan's own record for the exact run IDs rather than trusting this line;
- **F28–F31 have tests, and F31's refusal is proved by a fresh adversarial agent finding no path** —
  **NOT YET, Stage 3, all steps PLANNED**;
- **the Control Plane records its own history again** — **DONE, with one open defect**, steps 2.4/2.5/2.6,
  see §2.5-A — **and has at least one production caller** — **NOT YET**; the recorder is invoked by
  one-shot `mix run` scripts, never by a live process. That's Stage 4 step 4.1;
- **every body serves a boot-time build identity, and no watchdog can be fooled by a healthy process
  running stale bytes** — **DONE, step 1.1**, extended by capture-age (1.7) and witness-independence (1.8);
- **the soak ladder has been climbed rung by rung** — **untouched, Stage 6**;
- `PHASE-10.md` exists and is pre-registered — **not yet, Stage 6**.

**Then, and only then, Michael types go-live himself.**

## 12 · FINALLY

Report honestly. **A `BLOCKED`, a `FAIL`, a retraction, or a falsifier firing is the product working** —
carry it visibly and say it first. This session did that repeatedly, including about its own mistakes
(the score_to reordering, the F10 catch, the gates.ndjson retraction, and now the ledger collision), and
every one of those corrections made the record more trustworthy, not less. Never manufacture a pass. Never
let a green software gate be read as biological parity. And never claim the word `tamper_proof`: nothing
on this fleet delivers it, and the code already says so.

**Your first act: read `phase9_plan.json` fresh, open TRACK, confirm resonance still holds on CURRENT
code (restart the Node bodies off-air first if they're stale — check `/api/identity` before trusting
anything else), then speak §2.5-A to Michael and wait for his ruling before touching Stage 2 again.**
