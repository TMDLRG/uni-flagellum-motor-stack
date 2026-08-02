# Run Landing Mode — Status

**Snapshot:** 2026-07-22T10:25:39Z · **HEAD:** `28ce7380a9b6001b373756f3a47eabaa0f73fd6e`
**Branch:** `hierarchical-aif/motor-stack` · **Nothing pushed.**
**Mode:** RUN LANDING. No new probe packs, no new audits, no new science analyses.

> **Neither cell has landed.** Every number below is provenance or telemetry. **No result, no
> verdict, and no P-level movement is reported in this file**, because there is none to report.

---

## 1. B4C11 status — RUNNING

| field | value |
|-|-|
| process | **PID 26756, ALIVE** (30 786 CPU-seconds at check time) |
| progress | 890 / 2000 replicates |
| failed | 0 |
| `RESULT.json` | **ABSENT** |
| `STDERR` | **0 bytes** |
| launched | 2026-07-22T01:40:03Z |
| committed prediction | **`897c8ab`**, committed at 210/2000 with no result file in existence |
| prospectivity | `PENDING_NO_OBSERVATION_YET` → becomes `SATISFIED` on landing |

**Its progress counters are TELEMETRY, not results**, and are deliberately not quoted, interpreted,
or carried into any statement here. The committed prediction stands **unrevised**.

**Landing is pre-routed both ways** (template §5): the withdrawn `U4_OK` — 30 of 2000 replicates
under a defective bootstrap — **stays withdrawn regardless of outcome**. If corrected `U4_OK`
lands, D1 closes **by corrected rerun**, re-establishing U4 *on the corrected run only*. If
corrected U4 fires, D1 closes as a **substantive correction against the old U4**. The N=5 paired
diagnostic and the 25-replicate legacy arm remain **diagnostic only** and license no verdict.

## 2. B4C01 status — RUNNING

| field | value |
|-|-|
| process | **PID 32988, ALIVE** (21 669 CPU-seconds at check time) |
| progress | generator 2 of 5 complete; 3 generators remain |
| failed | 0 |
| `RESULT.json` | **ABSENT** |
| `STDERR` | **0 bytes** |
| launched | 2026-07-22T04:13:27Z |
| committed prediction | **`28ce738`**, committed while the cell had **never run at any N** |
| prospectivity | `PENDING_NO_OBSERVATION_YET` → becomes `SATISFIED` on landing |

Same discipline: per-generator counters are telemetry. **This is the cleanest prospective cell in
the batch** — committed with zero observations of any kind in existence, committed blob == on-disk
== launch-pinned (`5e08cfd3…`, no drift) — so its scorecard will carry real weight and must not be
shaded.

**Landing is pre-routed into four classes** (template §3), decided before any number is read:
**PASS** · **self-win / power failure** (a statement about the ASSAY, not a fitter defect — the
"pipeline is broken" reading is explicitly forbidden) · **parameter-recovery failure** (materially
graver; puts `P1` for the affected fitter in question) · **FAILED_RUN** (no verdict; a crash is not
a scientific negative). If both occur, both are reported and the milder does not absorb the graver.

## 3. Watcher status — BOTH ARMED, NEITHER FIRED

| watcher | cell | state |
|-|-|-|
| `bmscgn2g9` | B4C11 | **ARMED**, no landing |
| `bde1anrzk` | B4C01 | **ARMED**, no landing |

Each exits on **either** condition — `RESULT.json` appearing, **or** the PID disappearing with no
result (→ `FAILED_RUN`). Silence is therefore informative: it means neither has landed and neither
has crashed. Coverage of the failure path was deliberate; a watcher that only greps for success is
silent through a crash.

## 4. D11 numeric provenance guard — DELIVERED AND PROVEN

**D11:** the wording guard cannot check a number. Two figures reached a report untraceable, and the
harder one was **not invented** — `0.0790` was the recorded M3 percentile half-width
`0.0789979` **transplanted from a different table in the same document**.

**Built:** `src/motor_stack_aif/numeric_provenance_guard` (module) + a CLI.

A decimal may be **ANCHORED** to a `file.json#dotted.path` (and must match it **at display
precision**), **RECOMPUTED** by a named script, or explicitly `DESIGN_ONLY` / `NOT_COMPUTED` /
`NOT_MEASURED`. The failing class is **`ANCHORED_MISMATCH`** — a number that names a source and
contradicts it. On mismatch the guard searches every artifact for a field whose value *does* round
to the quoted figure and **names it**.

**Proven end-to-end, not merely unit-tested.** Reintroducing both original D11 values into a copy
of the power atlas produced exit code 1 and:

```
FAIL …:66   0.043   declared source holds 0.03952847075210474, which does not round to 0.043
                    | TRANSPLANT SUSPECT: power_atlas.json#cells.29.meanPointEstimateNats=0.0434549…
FAIL …:203  0.0790  declared source holds 0.07996917206325926, which does not round to 0.0790
                    | TRANSPLANT SUSPECT: F_SIDE_MOTOR_STACK_SCORING_RESULT.json#contrasts
                      .M3_TWO_TIMESCALE.halfWidth=0.07899792887310705
```

The transplant diagnosis **independently rediscovered the actual source** of the `0.0790` defect.

**Tests:** `test_numeric_provenance_guard.py` (9) + `test_report_numbers_trace_to_artifacts.py` (6).
A dedicated non-vacuity test proves the hard case is hard: `find_transplant_source` confirms
`0.0790` **does** match a real recorded field, so a naive *"does this number appear anywhere?"*
check would have **PASSED** it. **Provenance is about the POINTER, not the digits.**

**Live over the namespace:** 1939 in-scope decimals, **0 failures**; 2 `ANCHORED_OK`,
4 `RECOMPUTED`, 126 `MARKED`, the remainder `UNANCHORED`.
Report: `reports/NUMERIC-PROVENANCE-GUARD-REPORT.md`.

**Scope, stated honestly and repeated in the guard's own output:** this makes *declared* provenance
checkable. It does **not** make numeric provenance decidable in general. `UNANCHORED` is reported
and does **not** fail — reports legitimately carry counts, dates and derived arithmetic, and a
guard that fires on everything is a guard nobody reads. The general control remains an adversarial
reader briefed to trace every number.

**D11 closure:** `CLOSED_BY_CORRECTION_AND_TESTED_MECHANICAL_GUARD`.

### A defect the guard work surfaced in itself

An earlier draft of the guard re-declared the string `NOT_ESTABLISHED` in its marker tuple. The
suite's AST scan (`test_verdict_strings_are_defined_in_exactly_one_module`) caught it: `status.py`
owns the verdict vocabulary so that **no other module can emit a verdict without having seen an
interval**. Fixed by importing from `status` rather than re-declaring. The check was right and a
literal is a literal regardless of the author's intent.

## 5. Suite status

**`497 passed, 2 skipped, 1 xfailed`** — up from 485 at the start of this mode (+12: 9 provenance
guard, 6 report-number tracing, less overlap). **No test weakened or deleted.**

## 6. Claim guard status

**`0 violations across 6 paths`** (`reports`, `docs`, `ledgers`, `protocols`, `scripts`, `results`).
Report: `reports/CLAIM-GUARD-ACTIVE-FLOW-REPORT.md`.

## 7. Frozen evidence status

**IDENTICAL — NO DRIFT.** Full sha256 recheck over all **250** files under `audits/phase-c` and
`audits/phase-d` against the pinned baseline; `diff` clean. Receipt:
`reports/frozen-evidence-recheck-run-landing.sha256`. `git diff --stat -- audits/` empty, and
nothing outside `hierarchical-aif/` is modified.

## 8. Also delivered in this mode

- **Landing templates** at `reports/templates/B4C11-…TEMPLATE.md` and `B4C01-…TEMPLATE.md`, so
  landing is mechanical and no required field is forgotten under time pressure. They are kept in a
  `templates/` subdirectory and headed with an explicit **"TEMPLATE, NOT A RESULT"** banner, so a
  pre-filled skeleton can never be mistaken for a landed report or cited as one.
- Every template carries the full required field set: committed prediction hash, command, runner
  provenance, planned/actual N, runtime, output hash, criterion, `intervalUsed`, BCa and percentile
  width (or **`NOT_COMPUTED`** with the reason — for both cells the criteria are fractions and
  tolerances, **not CI contrasts**, so no interval exists), old vs corrected status, prediction
  grading, lane scoping, P-mapping, allowed/forbidden wording, and `NEXT_ACT`.

## 9. Probe-pack claims — unchanged and still fenced

The 12 builder-support artifacts remain **`POST_HOC_EXPLORATORY`**. None has moved a P-level,
altered a frozen verdict, or become parity evidence. `DESIGN_ONLY`, `NOT_COMPUTED`,
`NOT_MEASURED` and `NOT_APPLICABLE_DIFFERENT_UNITS` labels are retained where they were applied.
`P8` remains `FULL_PARITY = false`; the first unsatisfied level is still **`P4` transfer**.

---

`NEXT_ACT = tail -1 hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_STDOUT.log && tail -1 hierarchical-aif/results/motor_stack_aif/B4C01_CORRECTED_FULL_STDOUT.log`

On a watcher firing, the landing sequence is mechanical:

```bash
# 1. hash the result
sha256sum hierarchical-aif/results/motor_stack_aif/B4C<NN>_CORRECTED_FULL_RESULT.json \
  > hierarchical-aif/results/motor_stack_aif/B4C<NN>_CORRECTED_FULL.sha256
# 2. fill the template into the canonical report path, grading against the COMMITTED prediction
#    (897c8ab for C11, 28ce738 for C01) - never revise the prediction
# 3. route the defect closure ledger (D1 for C11; D2/D3 for C01)
# 4. update the P-ladder MAPPING without redefining any level
# 5. run both guards and the suite
python hierarchical-aif/src/motor_stack_aif/claim_guard.py hierarchical-aif/reports hierarchical-aif/docs hierarchical-aif/ledgers hierarchical-aif/protocols hierarchical-aif/scripts hierarchical-aif/results --report hierarchical-aif/reports/CLAIM-GUARD-ACTIVE-FLOW-REPORT.md
python hierarchical-aif/src/motor_stack_aif/numeric_provenance_guard.py hierarchical-aif/reports hierarchical-aif/docs hierarchical-aif/ledgers hierarchical-aif/protocols --report hierarchical-aif/reports/NUMERIC-PROVENANCE-GUARD-REPORT.md
python -m pytest hierarchical-aif/tests/motor_stack_aif -q
```

If a PID is gone and no `RESULT.json` exists: status is **`FAILED_RUN`**, write the failed-run
repair report, and **do not treat it as a scientific negative**.
