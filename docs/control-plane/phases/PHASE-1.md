# Phase 1 — Drift disposition and baseline truth

**Status:** EXECUTED 2026-07-25 → [`PHASE-1-RESULTS.md`](PHASE-1-RESULTS.md) · **Authorised:** operator, 2026-07-25
**Bound:** documentation and audit corrections only. **No new code. No gate verdict authored. No P-level moved.**
**Repos:** `UNI.Minecraft` @ `cdf73c89` (branch `gen2-runtime`, canonical) · `UNI-FLAGELLUM` @ `58f6645`

---

## 0. Why this phase exists

Phase 1 is not a warm-up. It is the **falsification test of ADR-0002's central claim** — that a doc-versus-receipt disagreement is surfaced by Gaia, resolved by a human or the Control Plane, and clears. If a drift will not clear, the source is wrong, not the document, and that is a finding about the system rather than a chore.

It runs before any code because the Control Plane's first job is to prevent exactly this class of defect, and building a fix for a defect you have not measured is how you get a fix aimed at the wrong thing.

## 1. Pre-registration — written before execution

Per `LAB_PROTOCOL.md §II`, expectations and falsifiers are committed **before** the work. Anything discovered that contradicts these is a finding, not an embarrassment to be smoothed over.

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 1.1 | Correct my own audit numbers to canonical | `ARCHITECTURE.md` states 195 rows / 109 unique / 92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING | any number in my docs still traceable to the chip's deployed copy |
| 1.2 | `drift.fqdn_cjs` | doc fix: `CLAUDE.md:94` cites `viewer/fqdn.cjs`; the file is `viewer/hud/fqdn.cjs`. Drift clears on the next Gaia capture | the file is genuinely absent, i.e. the **code** is wrong and a doc fix would launder it |
| 1.3 | `drift.gate_row_schema_path` | doc fix: a doc cites `gate_row.v1.json` as a path; the real path is `production/schemas/gate_row.schema.json`, and `gate_row.v1.json` is the schema's `$id` **URI**, not a path | the drift persists after the doc fix, meaning the comparison itself is malformed |
| 1.4 | `drift.resolver_planned` | registry declares `dnsmasq (planned)`; live resolution reports `tracking`/`fresh`. **Expected NOT to clear by a doc edit** — the registry's declared state is a plan, the observation is reality | it clears trivially, meaning I misread which side is authoritative |
| 1.5 | `drift.self_caps_doc_vs_served` | `GAIA.md` is stale (85 signals vs 305 live; documents a `relay` seat that is not live; omits `organic-operator`). Correcting it clears the drift | the served CAPS is wrong and the doc is right — then the **code** is the defect |
| 1.6 | `drift.git_dirty_vs_clean` | **WILL NOT CLEAR. Not mine to clear.** ` M test/sp/brain/mc_test.exs` is user-owned | I touch it |
| 1.7 | Record the `FAIL` gate | `nursery-fenced-red-stocked` (Phase 2, class B, 2026-07-19) is FALSIFIED — F1 and F3 fired. It must ride visibly in every status I write | it is omitted from a summary, or softened |

**Standing expectation:** 5 Gaia drift signals exist; **at most 4 are clearable by me**; **at least 1 (1.6) is structurally not mine**. A phase that reports "all drift cleared" has either touched a user-owned file or laundered something.

## 2. Retractions carried into this phase

Recorded because a superseded finding must remain visible, not be quietly replaced.

| retracted claim | truth | how I got it wrong |
|-|-|-|
| *"`GATES.md` has drifted from its ledger — 189/87/4/14 vs 191/105/89/4/12"* | **`GATES.md` is correct on canonical.** It reads 109 unique / 195 rows / 92·4·1·12, matching the ledger exactly | I read both from the chip's **deployed copy** (`/home/uni/build_9e6cee1`) and reported it as canonical |
| *"Gaia is not running"* | Gaia is running on THINKER with 305 signals | probed `127.0.0.1:8096` on the chip; Gaia runs on THINKER |
| *"`gaia-boot-persistent` is UNPROVEN"* | PASS since the real 2026-07-14 reboot | trusted `GAIA.md`'s stale §0 over the ledger |
| *"191 rows / 105 unique gates"* | 195 rows / 109 unique, and there is **1 FAIL** | same stale replica |

**The lesson, and it is the architecture's own thesis:** I measured a replica and called it the system, twice. A deployed copy that has silently drifted from canonical is precisely what Gaia exists to surface and what the Control Plane exists to prevent. It is worth noting that **nothing in the current system detects chip-vs-canonical ledger drift** — Gaia watches THINKER's tree only. That is a candidate for Phase 2.

## 3. Work items

Each item: act → observe → record disposition. A disposition of `NOT_CLEARED` with a named reason is a **valid, complete** outcome.

**1.1 Correct the audit numbers** — `UNI-FLAGELLUM`: `ARCHITECTURE.md` §2, §15, `workspace.dsl` gate-ledger description, `views.md`. Every ledger number must cite canonical and say so.

**1.2–1.5 Dispose of four drifts** — `UNI.Minecraft`, doc edits only. For each: apply the fix, re-capture `/api/gaia`, record whether the drift cleared, and if not, why. **Do not edit code to make a drift go away.**

**1.6 Leave the dirty-tree drift alone** — record it as `NOT_CLEARED — USER_OWNED`.

**1.7 Surface the FAIL gate** — add `nursery-fenced-red-stocked` to the architecture's honest-state block, with its falsifier verbatim and its claim fence intact (*"model variables only; survival = in-world persistence; ZERO weight for awareness/experience/life"*).

## 4. Verification

```bash
# canonical repo — nothing may change but documentation
cd ~/Documents/UNI.Minecraft
git diff --stat                     # doc files only; mc_test.exs untouched
mix test                            # unchanged: no code was edited
node viewer/verify_gaia.cjs         # exit 0
node viewer/render_gates.cjs        # GATES.md must be byte-identical after re-render

# drift re-capture, per item
curl -s http://127.0.0.1:8096/api/gaia | \
  python -c "import sys,json;[print(s['id'], json.loads(s['value']['raw'])['equal']) \
  for s in json.load(sys.stdin)['result']['signals'] if s['seat']=='drift']"
```

**Acceptance:** every one of the five drifts has a written disposition — `CLEARED` with its re-capture, or `NOT_CLEARED` with its reason. `mix test` unchanged. `GATES.md` byte-identical after re-render (proving it was already correct). Zero code files modified. `mc_test.exs` untouched.

**Falsifier for the whole phase:** a drift that clears because I edited code rather than a document, or a `GATES.md` that changes on re-render (which would mean my "not drifted" retraction is itself wrong).

**Rollback:** every change is a doc edit in a git repo; `git revert` per commit.

**Stop conditions:** `STOP_FROZEN_EVIDENCE_DRIFT` · `STOP_DESTRUCTIVE_ACTION_REQUIRED` · a drift whose honest fix is a code change (that is Phase 2 work, pre-registered, not smuggled into Phase 1).

## 5. Exit condition — the phase does not end when the work ends

Per `ORCHESTRATE-RULES.md §1`: *"Every RECORD step must end with `NEXT_ACT`… Writing a report, passing tests, creating a ledger, or declaring alignment are not stopping conditions."*

**Phase 1 is complete only when `docs/control-plane/phases/PHASE-2.md` exists, is committed, and is pre-registered in the same form as this document.** Finishing the work items is not completion. Passing verification is not completion. The phase ends by starting the next one.

`PHASE-2.md` must be written **from Phase 1's observed results**, not from this plan's assumptions, and must carry:

1. Every Phase 1 disposition, including each `NOT_CLEARED` and its reason.
2. Any drift whose honest fix is a code change, now pre-registered as Phase 2 work with its own falsifier.
3. The chip-vs-canonical ledger drift that **nothing currently detects** — scoped as a decision: is it a defect, a deployment artifact, or a new Gaia seat?
4. The Phase 2 build items from `ARCHITECTURE.md §12` — `SP.ControlPlane.{Ledger,GateRow,Command}` in the root zero-dep app — each with a red test named **before** it is written.
5. Its own §5 exit condition requiring `PHASE-3.md`.

**The recursion is the rule, not a flourish.** Every phase document ends by requiring the next. A phase that closes without its successor written has stopped, and stopping is only legitimate under a declared STOP condition.

## 6. What Phase 1 explicitly does not do

Write code. Author a gate verdict. Append to `evidence/gates.ndjson`. Move a P-level. Touch `mc_test.exs`. Edit any file to make a drift disappear. Claim the system is drift-free.
