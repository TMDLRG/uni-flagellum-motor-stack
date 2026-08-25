# Current State and NEXT_ACT

**Snapshot:** 2026-07-23 · **HEAD:** `84ddc766532e83e06ddd1ea0617c350b717c32d7`
**Branch:** `hierarchical-aif/motor-stack` · **Pushed to `origin/hierarchical-aif/motor-stack`.**
**Science anchor is still `e21747c`** (corrected B4 closure); commits on top of it are the OODA
next-cycle plan (`da89a41`) and the **D12 incident containment** (`7e9b22b`…`84ddc76`) — governance,
no P-level moved.

> **This file is the live state for the next session. Re-verify it on arrival** — the commands in §1
> re-establish it in under a minute. This snapshot describes a **closed batch**, not work in flight.

---

## 0. One-line status

```text
H-AIF corrected B4 closure: COMPLETE (science anchor e21747c).
D12 incident containment: COMPLETE + pushed — leaked held-out mark identity redacted from
  distributable surfaces, d5_distribution_guard built, D5-safe successor archive round-trip-verified,
  remediation gate PASS. Incident stays NEGATIVE permanently; transmission principal-gated.
next gate: P4 transfer / P5 intervention discriminator — REQUIRES EXTERNAL DATA.
The binding constraint is now data, not model math.
```

## 1. Verify first (do not trust this file blindly)

```bash
cd UNI-FLAGELLUM
git log -1 --format='%H %s'                       # expect 84ddc76 … "D12 successor archive … gate PASS"
git status --short                                # expect CLEAN (nothing tracked pending)
diff -q hierarchical-aif/reports/frozen-evidence-baseline.sha256 \
        <(find audits/phase-c audits/phase-d -type f -print0 | sort -z | xargs -0 sha256sum)  # IDENTICAL
python -m pytest hierarchical-aif/tests/motor_stack_aif -q                 # 573 passed, 3 skipped, 1 xfailed (577 collected; measured 2026-08-19)
python hierarchical-aif/src/motor_stack_aif/claim_guard.py hierarchical-aif/reports hierarchical-aif/docs hierarchical-aif/ledgers hierarchical-aif/protocols hierarchical-aif/scripts hierarchical-aif/results   # 0 violations
python hierarchical-aif/src/motor_stack_aif/numeric_provenance_guard.py hierarchical-aif/reports hierarchical-aif/docs hierarchical-aif/ledgers hierarchical-aif/protocols   # 0 failures
python hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py hierarchical-aif/reports hierarchical-aif/protocols hierarchical-aif/ledgers hierarchical-aif/docs   # 0 findings (D12 distribution guard)
```

## 2. The corrected B4 package — CLOSED for this batch

All four corrected cells landed at full frozen N, 0 failures each, graded against committed
predictions. Each hash verifies `sha256sum -c` OK.

| cell | verdict | result hash | prospectivity | report |
|-|-|-|-|-|
| **B4C01** | `NOT_ESTABLISHED` (M0 self-win 0.290; recovery intact) | `8256cb12…` | **SATISFIED** (cleanest; committed with zero observations) | `reports/B4C01-CORRECTED-FULL-REPORT.md` |
| **B4C02** | `GENERATOR-SPECIFIC` (adverse M2-over-M3 not generic shape) | `0633988d…` | **SATISFIED** (mid-run-commit caveat) | `reports/B4C02-CORRECTED-FULL-REPORT.md` |
| **B4C10** | `IDENTIFIED_ON_THIS_COHORT` (U2/U3/U4 OK) | `959a00e9…` | **NOT_SATISFIED** (shared commit; D9, permanent) | `reports/B4C10-CORRECTED-FULL-REPORT.md` |
| **B4C11** | `U4_OK` (collapse 0.0055; groups 80/80) | `564a5b0f…` | **SATISFIED** (~19.4 h before observation) | `reports/B4C11-CORRECTED-FULL-REPORT.md` |

Integrated reading: `reports/B4C01-B4C11-INTEGRATED-CLOSURE.md`;
phase closure: `reports/PHASE-HIERARCHICAL-AIF-CORRECTED-CLOSURE.md`;
one-row-per-cell index: `reports/CORRECTED-CELL-RESULT-INDEX.md`.

## 3. Defect closure state

**7 CLOSED · 2 CLOSING · 3 QUARANTINED · 0 OPEN** (D12 added this cycle).
Ledger: `ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md`.

| id | status |
|-|-|
| D1 C11 cluster collapse | **CLOSED_BY_CORRECTED_RERUN** — B4C11 landed; the submitted 30-replicate `U4_OK` stays **withdrawn** |
| D2 resource overestimate | **CLOSED** — all four reruns landed (2.3–21.1 h vs 150–400 h claims) |
| D3 hash-seed nondeterminism | **CLOSED** — C01/C02 ran deterministically, 0 failures |
| D4 C01 reason mismatch | CLOSED (historical, strict-xfail) |
| D5 holdout mark burned | **QUARANTINED — retrospective-only, transfer-required** |
| D6 `nextStateN` unchecked | **QUARANTINED — raw archive required** |
| D7 width = percentile not BCa | CLOSING (forward-discipline; corrected floor 0.042; guard live) |
| D8 ledger claimed undelivered tests | CLOSED (delivered + mutation-tested) |
| D9 prospectivity by commit graph | **QUARANTINED — B4C10 + F-side permanently NOT_SATISFIED; launcher now refuses uncommitted predictions** |
| D10 no minimum effect size | CLOSED (interpretation layer; frozen verdicts unaltered) |
| D11 fabricated/transplanted numbers | CLOSED (`numeric_provenance_guard` + tests) |
| D12 distributable mark-identity leak | **CLOSING_BY_CONTAINMENT** — 4 surfaces redacted, `d5_distribution_guard` built (16 tests), D5-safe successor archive round-trip-verified (`386f0e46…`), remediation gate **PASS**. Incident **NEGATIVE permanent**; `haif-closure-e21747c.zip` **WITHDRAWN_D5_UNSAFE**; transmission principal-gated |

## 4. Scientific standing

| area | standing |
|-|-|
| Corrected B4 package | **Closed for this batch** |
| C01 (synthetic calibration) | The 19-motor motor-equal assay is **nesting-blind / power-limited** for near-equivalent models. Distinctive shapes resolve (M3 0.935, M2 0.885); a true exponential self-wins only 0.290. **Not a fitter defect** — recovery intact |
| C11 (M7 hierarchy) | M7's `tau` remains **identified** under the corrected bootstrap. Identification is **not** necessity and **not** mechanism |
| F-side model | Built and scored; **NOT_ESTABLISHED** against serious adversaries; reproduces frozen M7 to 2.5e-7 nats; buys nothing over its `tau→0` limit M1. **Architecture, not evidence, on current data** |
| M2/lognormal | **Still a live adversary** — leads the held-out leaderboard; kept alive by design |
| P8 / full biological parity | **Not established.** No claim of parity, active inference, or G-side policy from passive data |
| First missing rung | **P4 transfer** |
| Next scientific gain | **Requires external transfer or intervention data** |

**No P-level was raised by this phase.** `P8 = FULL_PARITY = false`. `P4`/`P5`/`P7` are irreducibly
external and cannot be closed by any modelling in this repository.

## 5. NEXT_ACT — the next move is OUTSIDE this repo

**Do not mine the same Wadhwa duration data further.** It has reached the limit of what it can fairly
say; more analysis on it would create post-hoc structure, not stronger evidence. The next useful
work is converting the plan into an external-data acquisition checklist and obtaining that data.

```text
NEXT_ACT = convert protocols/NEXT-GATE-TRANSFER-AND-INTERVENTION-PLAN.md into an
           external-data ACQUISITION CHECKLIST, then acquire/design:

  1. an independent transfer cohort (single-motor dwell series, independent of Wadhwa 2022,
     enough independent MOTORS to beat the nesting-blindness C01 measured)
  2. a PRE-REGISTERED scoring rule committed BEFORE the data is touched (D9 discipline)
  3. adversaries kept alive: M2/lognormal, M4/M7 hierarchy, three-timescale kinetics,
     censoring artifact — a predeclared discriminator must be able to REMOVE one or more
  4. an intervention/perturbation path if G-side policy selection is to become testable
     (load / stator / PMF, recorded onset, paired pre/post on the same motors)
  5. treat mark-process evidence as TRANSFER-REQUIRED — D5/D6 quarantined the current channel
```

**Method discipline that governs the next gate:**
- Alternatives stay alive until a predeclared discriminator removes them (strong inference).
- The verdict is the bound/criterion set **before** the result, never a preferred interpretation after.
- Prospectivity is decided by the **commit graph**, not by prose (D9). Commit the prediction record
  before the run; flip `PENDING → PROSPECTIVE` only in the result commit.
- Nature can guide the motor-stack architecture but **cannot move a UNI gate** without build receipts.
- No rung rises without scoped evidence; negatives, partials, and bounds stay part of the record.

## 6. Standing reminders

- **Pushed.** `hierarchical-aif/motor-stack` is on `origin` at `84ddc76`; `e21747c` remains the
  science anchor and is preserved unchanged (no amend/rebase/force-push).
- `audits/phase-b/**` (B3/B4 runners) and `audits/phase-c|d/**` (250 frozen files) are **frozen,
  read-only**. Never edit; any diff is a hard stop.
- The correction notice to the external reviewer is **prepared, not sent**; only the principal
  transmits it. Likewise the **D5-safe successor archive** (`UNI-FLAGELLUM-haif-closure-8b93cf0-D5SAFE.zip`,
  sha256 `386f0e46…`) is built and verified but **not distributed** — transmission is principal-gated.
- The withdrawn archive `UNI-FLAGELLUM-haif-closure-e21747c.zip` is **WITHDRAWN_D5_UNSAFE**; the D12
  incident state is **NEGATIVE and permanent** (prior distribution cannot be recalled).
- **Open, flagged for principal decision:** `public/wadhwa-2022-derived-events.json` (served held-out
  dataset — exposure question, not acted on); `status.py` overrun-semantics **PENDING** (pre-P4);
  the user-owned dirty edit to this doc has now been reconciled and committed.
- Three mechanical guards run after every report batch: `claim_guard` (wording),
  `numeric_provenance_guard` (declared numbers), and `d5_distribution_guard` (held-out mark identity
  in distributables). All three are **necessary, not sufficient**.
```
NEXT_ACT = convert NEXT-GATE-TRANSFER-AND-INTERVENTION-PLAN.md into an external-data acquisition checklist
```
