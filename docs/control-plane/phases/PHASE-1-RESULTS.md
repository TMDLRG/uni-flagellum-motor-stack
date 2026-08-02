# Phase 1 — RESULTS

**Status:** EXECUTED 2026-07-25 · **Plan:** [`PHASE-1.md`](PHASE-1.md) (pre-registered before execution)
**Bound honoured:** documentation only. No code written. No gate verdict authored. No P-level moved. `mc_test.exs` untouched.

---

## 0. Headline — the pre-registration was falsified, and that is the result

> **Four of the five Gaia drift signals can never read `equal=true`. Not because the documentation is wrong, but because the two sides being compared are different kinds of thing.** No documentation edit can clear them. `equal=false` is their permanent, normal reading.

I predicted three doc fixes would clear three drifts. All three predictions are **false**, and false for a structural reason rather than a contingent one. Phase 1's falsifier — *"the file is genuinely absent, i.e. the code is wrong and a doc fix would launder it"* — **fired on item 1.2**, and the same mechanism turned out to govern 1.3 and 1.5.

Had I executed the plan as written, I would have edited three documents, observed nothing clear, and been tempted to edit the collector to make it clear. That is the laundering the phase was built to prevent.

## 1. The evidence

`viewer/gaia/collectors.cjs:741-749` — the comparison is a pure byte equality:

```js
function driftSignal(id, a, b, relation) {
  const equal = a.raw === b.raw;
  ...
}
```

All five signals are pushed **unconditionally** (`out.push(driftSignal(...))`), so the `gaia-drift-surfaced` gate — which requires the five to *exist*, not to be unequal (`verify_gaia.cjs:514-521`) — stays PASS either way. Clearing a drift would not break that gate. The problem is different: **the comparison cannot be satisfied.**

| drift | side A | side B | can `equal` ever be true? |
|-|-|-|-|
| `drift.fqdn_cjs` | a **line of `CLAUDE.md` prose** (`grepFirst`) | `git ls-files viewer/fqdn.cjs` output | **No.** Prose ≠ a file listing, and B is hard-coded to a path that does not exist. Only creating `viewer/fqdn.cjs` changes B. |
| `drift.gate_row_schema_path` | a **doc line** citing `gate_row.v1.json` | `ls production/schemas/gate_row*.json` | **No.** Same type mismatch. Removing the citation makes A a fallback string, still ≠ B. |
| `drift.resolver_planned` | `"dnsmasq (planned)"` | a **JSON array** of live resolve states | **No.** A plan label ≠ an observation array. |
| `drift.git_dirty_vs_clean` | `""` (hard-coded "expected clean") | `git status --short` | **Yes** — clears when the tree is clean. |
| `drift.self_caps_doc_vs_served` | `canonicalRaw(CAPS)`, a JSON object | **the entire 51 KB `GAIA.md` file** | **No.** A JSON blob ≠ a markdown document. |

## 2. What this means, stated carefully

**Gaia is behaving correctly.** GAIA LAW requires a mechanical byte-comparison and forbids Gaia from judging. It reports exactly what it computed. There is no violation here.

**The instrument is nonetheless not measuring what it appears to measure.** A reader seeing `drift.fqdn_cjs equal=false` reasonably infers *"the documentation is stale"*. But it would read `false` even if `CLAUDE.md` were perfect. For four of five, the boolean carries **no information about documentation correctness**.

**The signals are still valuable** — they carry both byte-sets verbatim with provenance, so a human can read A and B and judge. The defect is that the `equal` boolean invites a conclusion it cannot support.

**ADR-0002 is not invalidated.** "The Control Plane authors, Gaia projects, drift is surfaced and never silently reconciled" all hold. What is corrected is my assumption that these five were *actionable defects awaiting a fix*. They are **standing monitors**, and four have a comparison that cannot converge.

## 3. Disposition of every item

| # | item | disposition |
|-|-|-|
| 1.1 | correct my audit numbers to canonical | **DONE.** 195 rows / 109 unique / 92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING, in `ARCHITECTURE.md` §2, §5, §12 and `workspace.dsl` |
| 1.2 | `drift.fqdn_cjs` | **NOT_CLEARED — STRUCTURAL.** Side B is hard-coded `git ls-files viewer/fqdn.cjs`. No doc edit can change it. **Falsifier fired.** Not edited. |
| 1.3 | `drift.gate_row_schema_path` | **NOT_CLEARED — STRUCTURAL.** Doc line vs file listing. Not edited. |
| 1.4 | `drift.resolver_planned` | **NOT_CLEARED — STRUCTURAL.** Predicted not to clear; correct, but for a stronger reason than predicted. |
| 1.5 | `drift.self_caps_doc_vs_served` | **NOT_CLEARED — STRUCTURAL.** JSON CAPS vs the whole of `GAIA.md`. Not edited. |
| 1.6 | `drift.git_dirty_vs_clean` | **NOT_CLEARED — USER_OWNED.** ` M test/sp/brain/mc_test.exs`. Untouched, as pre-registered. The only one of the five that *could* clear. |
| 1.7 | surface the `FAIL` gate | **DONE.** `nursery-fenced-red-stocked` now rides in `ARCHITECTURE.md` §5 and §12 with its falsifier and claim fence. |

**Five drifts, zero cleared.** Pre-registration said *"at most 4 clearable, at least 1 structurally not mine."* Observed: **at most 1 clearable (1.6), and that one is not mine either.** Worse than predicted, in the informative direction.

## 4. Retractions confirmed

`GATES.md` is **correct on canonical** — `109 unique gates (195 total rows)`, `92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING`, matching its ledger exactly. My "drifted" claim was measured against the chip's deployed copy. Retracted. Also retracted and corrected in the architecture: "Gaia is not running", "`gaia-boot-persistent` UNPROVEN", "191 rows / 105 unique".

## 5. Verification

No code file was modified in `UNI.Minecraft`; `git status --short` still shows only the user-owned `mc_test.exs`. `GATES.md` was **not** re-rendered — it did not need to be, which is itself the confirmation that the retraction in §4 is correct. Changes are confined to `UNI-FLAGELLUM/docs/control-plane/`.

**A phase that reports "all drift cleared" has laundered something.** This one reports zero cleared, with a structural reason for each.

## 6. NEXT_ACT

Per `ORCHESTRATE-RULES.md §1` and [`PHASE-1.md`](PHASE-1.md) §5, Phase 1 is complete only when its successor is written. → **[`PHASE-2.md`](PHASE-2.md)**, committed alongside this document.
