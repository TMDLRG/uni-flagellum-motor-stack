# H-AIF Gates G1–G9

These gates produce receipts. They **map onto** the existing `P0..P8` ladder in `CLAUDE.md`; they
never redefine it. The mapping lives in
`ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md`.

| gate | name | maps to | status |
|-|-|-|-|
| **H-AIF-G1** | repo + frozen evidence integrity | `P0` | **ESTABLISHED** |
| **H-AIF-G2** | correction notice + defect ledger | `P1`; `P3`/`P6` interpretation | **ISSUED** (notice `PREPARED_FOR_TRANSMISSION_BY_USER`) |
| **H-AIF-G3** | failing tests for verified defects | `P1` | **COMPLETE** |
| **H-AIF-G4** | runner fixes + resource reclassification | `P1`, `P0` | **COMPLETE** |
| **H-AIF-G5** | corrected full B4 reruns | `P3`, `P6` per cell | **COMPLETE** — all four corrected cells landed at full frozen N (C02, C10, C11, C01) |
| **H-AIF-G6** | motor-stack gap audit + isolated implementation | `P1`; `P6` gap status | **AUDIT COMPLETE · F-SIDE BUILT AND SCORED** (scored under H-AIF-G7 — verdict `NOT_ESTABLISHED`; full G-side stack still design-only) |
| **H-AIF-G7** | control + adversarial comparison + F-side scoring | `P3`; `P6` discriminator pressure | **EXECUTED — verdict `NOT_ESTABLISHED`** (candidate ranks 5th of 10; reproduces frozen `M7` to 2.5e-7 nats) |
| **H-AIF-G8** | raw archive / transfer protocol status | `P2` if rederived; `P4` only with independent data | **NOT_LOCATED / NOT_ESTABLISHED** |
| **H-AIF-G9** | ledgers, ladder map, docs, handoff | no new evidence by itself | **ONGOING** |

---

## Gate detail

### H-AIF-G1 — repo + frozen evidence integrity → `P0`
Four sub-checks: live remote HEAD matches local (`git ls-remote`, not a local cache); working tree
pristine; `audits/phase-c` + `audits/phase-d` byte-identical to the Phase-1 anchor `4fcba6c`;
`hierarchical-aif/` separate. Baseline: 250 files in
`reports/frozen-evidence-baseline.sha256`. **Re-run this at the start of every session.**

### H-AIF-G2 — correction notice + defect ledger
Correct the record **before** fixing or rerunning. Letting a known-invalid claim stand unqualified
is claim laundering. Receipts: `reports/CORRECTION-NOTICE-TO-REVIEWER.md`,
`reports/CORRECTION-NOTICE-ISSUED.md`, `ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md`.

### H-AIF-G3 — failing tests before fixes → `P1`
Reproducer tests precede repair. Where strict red-then-green was not achieved, say so explicitly
rather than presenting it as compliance (see `reports/H-AIF-G4-RUNNER-FIX-REPORT.md` §5).

### H-AIF-G4 — runner fixes + resource reclassification → `P1`, `P0`
Fixes live in `hierarchical-aif/src/`; the frozen runners keep their defects so historical results
stay reproducible. Receipts: `reports/H-AIF-G4-RUNNER-FIX-REPORT.md`,
`reports/RESOURCE-BOUND-RECLASSIFICATION.md`.

### H-AIF-G5 — corrected full B4 reruns → `P3`/`P6` per cell
Run order chosen by **epistemic value**, not cost. Each cell needs a prediction record committed
before launch, full frozen N (or a prospective reduced protocol written first), corrected artifact
names that never overwrite originals, and a report with hashes.

Order: **C02** (highest epistemic value) → **C10** → **C11** (replaces the withdrawn U4) → **C01**.

### H-AIF-G6 — gap audit + isolated implementation → `P1`, `P6` gap
The audit found F, G, policy layer, priors `E`, precision `Π`, and up/down messages **absent** from
the science pipeline; all nine B3 models are MLE density fits. The F-side model is built under the
scope ruling, **and has since been scored under H-AIF-G7 — verdict `NOT_ESTABLISHED`.**

### H-AIF-G7 — control + adversarial comparison → `P3`, `P6`
The F-side candidate must be scored on the **same frozen split** and scoring rule against
`CONTROL_CURRENT` and the adversarial baselines, with a CI-bound verdict. **Executed 2026-07-22 — verdict `NOT_ESTABLISHED`**; reproduces the frozen `M7` to 2.5e-7 nats.

### H-AIF-G8 — raw archive / transfer → `P2`, `P4`
Raw MAT archive absent → `NOT_LOCATED_RAW_ARCHIVE`. No independent dataset → `P4` and `P7` remain
`NOT_ESTABLISHED`. Never infer raw confirmation from the packaged event JSON.

### H-AIF-G9 — ledgers, ladder, docs, handoff
Produces **no new evidence by itself**. Records mapped status changes only.

---

## Gate rules

1. A gate result may update a P-level only if: the existing P-level definition is named; the source
   artifact is named; the claim scope is named; the falsifier is carried; partial/not-run/negative
   states are preserved; and the update does not redefine the P-level.
2. Gates may **lower** a level on receipts. Withdrawing C11 U4 lowered `P6` for that scope. That is
   the gate working.
3. No gate may move `P8`. `P8` is conjunctive and currently `FULL_PARITY = false`, with `P4`
   transfer the first unsatisfied level.
