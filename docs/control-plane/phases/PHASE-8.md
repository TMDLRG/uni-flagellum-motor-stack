# Phase 8 — The flagellum method guards, and the fences this programme has been owed

**Status:** PRE-REGISTERED, NOT EXECUTED · **Written from:** [`PHASE-7-RESULTS.md`](PHASE-7-RESULTS.md)
**Bound:** the **flagellum repository**, which this programme has not yet touched, plus
the two fences Phase 7 proved are missing on the platform.
**No row is written to `evidence/gates.ndjson`. No P-level moves.**

---

## 0. What Phase 7 changed about this phase

1. **A fix can be worse than the defect it closes.** Item 7.6 shipped a repair that
   collapsed absent into nil one level up and was *mandated by its own test's regex*.
   Every repair in this phase gets an adversarial pass over the **repaired** function,
   not only over the original defect.
2. **A guard can be reachable around.** `node/2` refused a `:style` key by name and
   `%Scene{}` handed one to a renderer anyway. Every fence here names what can walk
   around it.
3. **A signal filed as structural stops being read** — and `drift.git_dirty_vs_clean`
   was pointing, unread, at a receipt its own commit could not reproduce.
4. **The witness is compromised** (§7.7 of Phase 7). Nothing in this phase may claim
   off-box corroboration until the writer's key is off node2.

## 1. Pre-registration — written before execution

| # | item | expected outcome | falsifier |
|-|-|-|-|
| 8.0 | premises checked; the flagellum repo's test/lint/typecheck baseline captured **before** any edit | a recorded green (or honestly red) baseline at a named HEAD | work lands on an unmeasured tree |
| 8.1 | `score.py:21,30` — bare `zip(per_event_nlpd, motor_ids)` truncates silently | drop one motor id ⇒ **raise before any mean is taken** | a mean is computed over a silently shortened pairing |
| 8.2 | `fit.py:41-54` — `res.success` stored as `"converged"` and never checked; `compare.py:277→384,402` scores unconditionally | finite params + unsuccessful termination ⇒ **halt, no artifact written** | a non-converged fit reaches a score |
| 8.3 | `compare.py:546` — P-ladder off by one (`P5 transfer` should be `P4`; `P7` omitted) | correction **as a sidecar with a new hash**; the frozen artifact is never overwritten | a frozen result JSON is edited in place |
| 8.4 | `status.py:28-40` — `actual_n > planned_n` collapses into `ELIGIBLE` | overrun is **flagged**, not silently eligible | an overrun run is scored as if it were planned |
| 8.5 | `d5_distribution_guard.py` — `release_verdict()` ignores `unscanned`; an unopenable zip yields zero findings and can return **PASS** | an unopenable archive reports `UNVERIFIED`, never `PASS` (F29) | an archive that cannot be opened is treated as clean |
| 8.6 | **the repo-wide IP-literal fence**, landed **RED**, wired into CI | ≥12 hits on the pre-fix tree; bootstrap literals allow-listed in `evidence/bootstrap_literals.json` with re-derivation and expiry | it lands green (the walk is wrong), or CI still never invokes node |
| 8.7 | **the five malformed drift comparisons repaired** under [ADR-0002 Amendment 1](../decisions/ADR-0002-gaia-projects-never-computes.md) | each repaired comparison **proved to still bite** by pointing its declared side at a bad value; before/after signal state captured | a comparison is repaired without a bite-proving mutation — indistinguishable from one loosened |
| 8.8 | replica lag split into `drift.deploy_ref_behind_head.<build>`, relation `lag` | the digest signal becomes the only in-place-edit tripwire on a deployed ledger | a tolerance is added that swallows the in-place-edit case |
| 8.9 | Carried: **`CLAUDE.md:93-97`** corrected — *last*, per [`FQDN-SEAM-DETERMINATION.md`](../FQDN-SEAM-DETERMINATION.md) | the doc is corrected **after** the code it describes is true | the doc is corrected first, closing the only signal telling the truth |
| 8.10 | Carried: **item 7.7** | the writer's key is off node2, re-measured, and only then is the anchor placed | an anchor is placed on a box the writer can write to |
| 8.11 | Inherited: `mix format` on `lib/sp/brain/language.ex` | reformatted in its own commit on its own terms | the reformat is buried in an evidence commit |

**Standing expectation:** the flagellum's released product stays CPU-only with no LLM
inference, GPU, WebGL, Three.js, analytics, accounts or network. Every guard here is
an **additive sidecar**; no frozen result or prediction JSON is overwritten.

## 2. Red tests, named before they are written

| test | must fail before the code exists, for this reason |
|-|-|
| `tests/test_score_pairing_is_total.py` | a shortened motor-id list is silently zipped and a mean is taken over it |
| `tests/test_unconverged_fit_cannot_score.py` | a fit with `success=False` reaches `compare.py`'s scorer |
| `tests/test_p_ladder_indices.py` | `P5 transfer` is asserted where the ladder says `P4`, and `P7` is absent |
| `tests/test_overrun_is_flagged.py` | `actual_n > planned_n` returns `ELIGIBLE` |
| `tests/test_unopenable_archive_is_unverified.py` | an unopenable zip returns `PASS` |
| `viewer/tests/no_ip_literal_test.cjs` | an IPv4 literal outside the bootstrap allowlist passes unnoticed anywhere in 472 files |
| `viewer/gaia/tests/drift_sides_are_comparable_test.cjs` | a drift signal whose two sides can never be equal is constructible |

Each committed **red** with its output recorded, and **with `git status --short`
inside the receipt** — the procedure added in Phase 7 after a receipt turned out not
to be reproducible from its own commit.

**Standing procedure, now five phases old:** a guard that passes vacuously is not
counted until a mutation proves it bites · any test that passes in red is named in the
receipt with the reason · a canary that fires is **replaced by what it was guarding**,
never deleted · when a guard is weakened, the trade is written down in the test itself
· a source scan states what it must **not** match · **and a fix is adversarially
reviewed as its own subject, because item 7.6's repair was the defect.**

## 3. The one thing this phase must not get wrong

The flagellum repository holds **frozen evidence** — `audits/phase-c/**` and
`audits/phase-d/**`, 250 files with a hash baseline at
`hierarchical-aif/reports/frozen-evidence-baseline.sha256`. **Any diff against it is a
contract violation and a hard stop.**

Every guard in items 8.1–8.5 sits beside code that produced frozen results. The
temptation is to re-run the corrected pipeline and replace the artifact. **Do not.**
A correction is a **new sidecar with a new hash**; the original stands, wrong, with
its correction recorded next to it. That is the same rule Phase 7 followed when a
receipt turned out to be unreproducible: the receipt was not edited.

## 4. Verification

```bash
cd ~/Documents/UNI-Flagellum/UNI-FLAGELLUM
npm ci && npm test && npm run lint && npx tsc --noEmit
npm run science:verify && npm run cross-study:verify
npm run cross-study:verify-raw          # expected EXIT 1 — BLOCKED_EXTERNAL, never a pass
python -m pytest hierarchical-aif/tests/motor_stack_aif -q
diff -q hierarchical-aif/reports/frozen-evidence-baseline.sha256 \
  <(find audits/phase-c audits/phase-d -type f -print0 | sort -z | xargs -0 sha256sum)
python hierarchical-aif/src/motor_stack_aif/claim_guard.py
```

**Acceptance:** every red test recorded red then green · every vacuous guard
mutation-tested · the frozen-evidence baseline **byte-identical** · no frozen artifact
edited · `cross-study:verify-raw` reported **BLOCKED**, never passed.

**Stop conditions:** `STOP_FROZEN_EVIDENCE_DRIFT` on any baseline diff ·
`STOP_TEST_REGRESSION` · `STOP_DESTRUCTIVE_ACTION_REQUIRED` before any write to a
frozen artifact or any host — **item 8.10 begins in this state.**

## 5. Explicitly not in this phase

Rewriting a frozen result. Moving a P-level. Claiming off-box corroboration while the
writer's key is on node2. Any claim about awareness, experience or life.

## 6. Exit condition — the phase ends by starting the next

**Phase 8 is complete only when `PHASE-9.md` exists, is committed, and is
pre-registered in this same form**, carrying: every Phase 8 disposition including each
falsifier that fired; whether the frozen baseline held; whether item 8.10 happened and
what removed the key; and its own §6 requiring `PHASE-10.md`.

A phase that closes without its successor has stopped, and stopping is legitimate only
under a declared STOP condition.
