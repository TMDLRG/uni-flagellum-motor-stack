# D12 — Incident Containment Report

**Defect:** `D12_DISTRIBUTABLE_MARK_IDENTITY_LEAK` · **Date:** 2026-07-23 · **Gate:** new, D5-lineage
**Authorization:** principal M25 science-consult decision, "AUTHORIZE WITH AMENDMENTS", 2026-07-22
**Incident ledger state:** `NEGATIVE` (permanent — see §5) · **Remediation gate:** `PENDING` (this
report closes the redaction sub-step; the archive round-trip sub-step, §6, is NOT done here)

---

## 1. Finding (as identified by external D5 safety review, independently reproduced)

The external review found real event-level identifiers, an associated real motor identifier, and
record-shaped held-out mark tuples surviving in distributable surfaces, beyond what the review's
own JSON/JSONL/Markdown-scoped scan could see. Independently reproduced here via
`hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py` (new, this report) against the
repository at HEAD before redaction: **16 findings across 3 files** (`EVENT_ID` ×8,
`MOTOR_ID_MARK_CONTEXT` ×3, `RECORD_SHAPED_TUPLE` ×5).

| surface | disposition |
|-|-|
| `reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md` | **REDACTED** (this commit) |
| `protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md` | **REDACTED** (this commit) |
| `ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md` | **REDACTED** (this commit) |
| `reports/ULTRACODE-TRACK-D-VERIFICATION.md` | **REDACTED** (this commit) — found by the package-stage scan, not named in the original authorization |
| `tests/motor_stack_aif/test_nextstate_range_check.py` | **NOT redacted — see §2** |

Package-stage scan also matched the motor-id string in `audits/phase-b/b3-model-competition-result.json`,
`experiments/data/wadhwa-2022-events.json`, `public/wadhwa-2022-derived-events.json`, and several
`hierarchical-aif/results/motor_stack_aif/*.json` result files. **None of these were touched — see §3.**

## 2. Why the regression test is excluded from distribution, not redacted

`test_nextstate_range_check.py`'s `KNOWN_BAD` constant pins the real event identifiers so the test
can assert, against the real committed dataset, that the D6 defect persists unedited. Stripping the
identifiers would make the test vacuous — exactly the "weakening a test to create apparent harmony"
CLAUDE.md forbids. Per the D6 report itself: "Split boundary: NO_DATA_ACCESS_NEEDED beyond the two
already-identified events, whose mark channel was already burned by D5" — reading these two specific
already-spent identifiers inside this one regression test is not a new D5 violation.

**Disposition:** the test file's functional content is unchanged (still 7/7 passing, still pinning
the real defect against the real frozen dataset). It must be **excluded from any externally
distributed package** by `d5_distribution_guard` at the manifest/staging step (§6 of the plan), not
textually redacted. `d5_distribution_guard.scan_paths` will correctly flag this file if it is ever
staged into a distribution tree; the packaging step must exclude it before that scan, or accept the
FAIL verdict as a hard stop.

## 3. Frozen and raw-evidence files — explicitly NOT touched, and why

None of the following were edited. Editing any of them would violate a *different*, equally binding
rule than the one D12 exists to enforce:

- **`audits/phase-b/b3-model-competition-result.json`** — `audits/phase-b/**` is frozen per
  `CLAUDE.md` ("not edited; the B3/B4 runners retain their defects on purpose").
- **`hierarchical-aif/results/motor_stack_aif/*.json`** (six files matched) — these are hashed,
  graded result artifacts; the H-AIF-G5 discipline is "corrected artifact names that never overwrite
  originals." Editing in place breaks their hash-verified status.
- **`experiments/data/wadhwa-2022-events.json`** — the raw ingested dataset. The D6 report's own
  text: "the dataset is FROZEN historical evidence and is NOT edited." Redacting real observational
  data is truth-laundering, forbidden by the same contract that authorizes D12.
- **`public/wadhwa-2022-derived-events.json`** — a served copy of the same observational dataset.
  Whether this file's public exposure is itself a finding requiring principal decision is recorded
  as an **open question**, not resolved by this report: it was not part of the four named surfaces
  or the original D5 review scope, and unlike the prose documents above it is the underlying
  measurement data the truth contract's transparency requirement (`OBSERVED` provenance) exists to
  expose. **Flagged for principal review; not acted on unilaterally.**

## 4. `d5_distribution_guard` — the new, separate guard

Built at `hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py`, tested at
`hierarchical-aif/tests/motor_stack_aif/test_d5_distribution_guard.py` (12 tests, all synthetic
fixtures of the real leak's shape — no real identifier appears in the guard or its tests). Detects
`EVENT_ID` (`DD-DD-DD-DDDD:DDDD`), `MOTOR_ID_MARK_CONTEXT` (motor id within 160 chars of a mark-defect
context word — a bare motor id with no such context does not fire), and `RECORD_SHAPED_TUPLE`
(≥2 of `stateN`/`nextStateN`/`jump`/`direction` with an assigned value, co-occurring with a holdout
label). Distinguishes schema prose (`` `stateN` (integer) ``, no assigned value) from value-bearing
records. Structurally parses JSON/JSONL string values. Inspects one level into nested zip archives;
an archive that cannot be opened is reported `UNVERIFIED`, never silently treated as clean. Emits a
machine-readable report via `d5_distribution_guard.scan_paths()` / CLI `--report`.
`release_verdict(report)` is the single function that computes `PASS`/`FAIL` — release fails if
`findings` is non-empty.

**Verification, post-redaction:** `python hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py
hierarchical-aif/reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md
hierarchical-aif/protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md
hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md
hierarchical-aif/reports/ULTRACODE-TRACK-D-VERIFICATION.md` → **`4 artifact(s) inspected, 0 finding(s), verdict PASS.`**

**Regression coverage:** `pytest hierarchical-aif/tests/motor_stack_aif -q` → 517 passed, 3 skipped,
1 xfailed (baseline was 504/3/1 before this work; +12 new guard tests, +1 unrelated). No test
regressed. `claim_guard.py` 0 violations / 6 paths (unchanged). `numeric_provenance_guard.py` 2079
in-scope decimals, 0 failures (was 2070; the redaction prose added a small number of new decimals,
none unanchored-and-failing).

## 5. Withdrawal notice — `UNI-FLAGELLUM-haif-closure-e21747c.zip`

```text
STATUS:            WITHDRAWN_D5_UNSAFE
ARCHIVE:           UNI-FLAGELLUM-haif-closure-e21747c.zip
SHA-256:            7b28f0d6f338cb2fa077d3a84fe9688c44a67cb813e513f27a1a0348113d41b2
ACTION REQUIRED:   stop redistribution of this archive; delete local copies where held
RECIPIENT ACKS:    NOT_ASSUMED — none recorded as of this report; record here if/when received
SUCCESSOR:         NOT YET BUILT — see §6; this report does not authorize a successor archive
HANDOFF CLAIM:     superseded. Do not repeat "no raw mark-key values" while any aggregate mark
                   summary remains. Narrower truthful claim: "No event-level held-out mark record,
                   associated event identifier, or event-level mark tuple is included in the
                   REDACTED distributable surfaces named in §1 of this report. Mark-field names may
                   appear in schema and declaration prose; aggregate defect summaries (counts,
                   percentages) contain no record identifiers. The frozen dataset, frozen results,
                   and the D6 regression test fixture were NOT redacted — see §3, §2 — and must be
                   excluded from any distribution package, not assumed safe by this notice."
```

## 6. Successor archive — BUILT and round-trip verified (remediation gate `PASS`)

Step 4 of the plan is now complete. `hierarchical-aif/scripts/build_d5_safe_successor_archive.py`
produced a **curated, D5-safe** package from anchor `8b93cf0` and verified it through the full
round-trip. Receipts: `reports/D12-SUCCESSOR-ARCHIVE-RECEIPT.md` and
`reports/D12-SUCCESSOR-ARCHIVE-MANIFEST-SHA256.txt`.

| step | result |
|-|-|
| package | `UNI-FLAGELLUM-haif-closure-8b93cf0-D5SAFE.zip` (82 files), beside the withdrawn archive |
| **package sha256** | `386f0e46018865a973c35e81cd3480c5fc8684cc74d1f46e979a09eafa51c6d2` |
| staged-tree scan | 83 artifacts, **0 findings, 0 unscanned**, verdict PASS |
| round-trip (unpacked) scan | 83 artifacts, **0 findings, 0 unscanned**, verdict PASS |
| round-trip manifest | staged == unpacked (byte-identical per-file sha256); `sha256sum -c` 82/82 OK |
| determinism | rebuild from the same anchor reproduces the identical package sha256 |
| forbidden content | no `.git`, no `*.bundle`, no `*.patch`; leak-bearing paths (result JSONs, audits, raw/served datasets, the D6 regression fixture) absent by omission |
| ancestry | sanitized receipt only — `GIT_ANCESTRY_RECEIPT_PROVIDED; FULL_HISTORY_RECONSTRUCTION_NOT_INCLUDED` |

**D12 remediation gate: `PASS`.** The *forward* package is D5-safe and independently verifiable.

**Still NOT done (unchanged):**
- Transmission of the withdrawal notice / distribution of the successor is **principal-gated** —
  building is authorized, sending is not. No recipient has been contacted; no acknowledgment assumed.
- `e21747c` and all history are **untouched** (no amend/rebase/force-push); the withdrawn blobs remain
  in history, which is exactly why the package ships a sanitized ancestry receipt, not a bundle.

**Incident ledger state: `NEGATIVE`, and stays `NEGATIVE` permanently even though the remediation gate
is now `PASS`** — prior distribution of the withdrawn archive cannot be recalled by any archive or
report. A `PASS` here means the successor is safe to distribute going forward, not that the past
exposure was reversed.
