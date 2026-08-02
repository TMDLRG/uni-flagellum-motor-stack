# H-AIF-G4 — Runner Fix Report

**Gate:** H-AIF-G4 · **Date:** 2026-07-21 · **Branch:** `hierarchical-aif/motor-stack`
**Maps to existing ladder:** `P1` equation/implementation; `P0` provenance
**Preceded by:** H-AIF-G3 reproducer tests (required before any fix)

**No frozen artifact was modified.** `audits/phase-b/*`, `audits/phase-c/**`, and
`audits/phase-d/**` are byte-identical to their committed state. All corrected implementations
live in the new `hierarchical-aif/` namespace. The committed runner **retains its defect on
purpose**, so the old evidence remains reproducible as the historical record.

---

## 1. D1 — cluster-bootstrap collapse

### Old behaviour (retained as `build_bootstrap_cohort_LEGACY_DEFECTIVE`)

Sampled motors' events are concatenated into a flat list and `b3.Cohort` is rebuilt. `Cohort`
groups training events into `train_by_motor` **keyed by `motorId`**, so K draws of a motor
collapse into ONE group holding K copies of its events.

| seed 20260717, b | draws | distinct motors | `train_by_motor` groups |
|-|-|-|-|
| 0 | 80 | 46 | **46** |
| 1 | 80 | 53 | **53** |
| 2 | 80 | 52 | **52** |
| 3 | 80 | 59 | **59** |
| 4 | 80 | 56 | **56** |

Group count equals the distinct-motor count exactly. Largest group inflates 70 → 153 events.

### New behaviour (`build_bootstrap_cohort`)

Each **draw** becomes its own exchangeable group; K draws of a motor yield K groups.
`bootstrap_group_origin` records `draw_<idx>_<motorId>` per group for provenance. Verified: 80
draws → **80 groups**, stable across replicates.

### Why the fix is surgical, and a leakage trap avoided

The obvious implementation — renaming `motorId` to a synthetic draw id — **is wrong and was
rejected**. `b3.Cohort.__init__` derives train/holdout membership from `sha256_mod5(motorId)` and
halts on mismatch. Renaming would re-derive the split from the synthetic name and scatter
bootstrap *training* draws into the *holdout* set: leakage strictly worse than the defect being
fixed. My first draft did exactly this; the reproducer tests caught it via
`BLOCKED-SCALE-UNDEFINED` before it could produce a number.

The corrected builder therefore:
1. assembles the cohort **exactly** as the legacy path does — preserving the frozen split, the
   bootstrap-resampled per-state scales `scale_N`, and the normalized `_y`; then
2. rebuilds **only** `train_by_motor`, one group per draw, normalized with the bootstrap
   cohort's own `scale_N`.

`train_y` (flat, pooled) is deliberately untouched, so **M4/C10 behaviour is unchanged** —
asserted by `test_m4_pooled_path_is_unchanged_by_the_fix`, which compares sorted `train_y`
between arms.

**This changes no frozen threshold, criterion, seed, or N.** It is an implementation fix to match
the frozen protocol's intended cluster-bootstrap semantics.

### Scope

| consumer | uses | affected |
|-|-|-|
| M7 (`m7_train_nll` iterates `train_by_motor`) | grouped likelihood | **YES** — C11 U4 |
| M4 (`_fit_m4_reduced` uses flat `train_y`) | pooled i.i.d. | no — C10 valid as written |
| B3 M7 fit (real cohort, no resampling) | 80 real groups | no |

## 2. D3 — non-deterministic seeding

**Old:** `np.random.default_rng(seed_base + sim + hash(gen) % 100000)`. `hash(str)` is randomized
per process; `PYTHONHASHSEED` unset. Three processes → `14565/95125`, `59809/55025`, `89866/26054`.

**New:** `seeding.stable_seed(cell_id, base_seed, replicate_index, protocol_version, cohort_id)`
→ `int.from_bytes(sha256(material).digest()[:8], "big") % 2**32`.

Verified across subprocesses with `PYTHONHASHSEED ∈ {0, 1, 12345, random}`: **one distinct value**.
The legacy function is retained and a test asserts it *does* vary, pinning the defect.

## 3. D2 / D4 — provenance corrections

`resource.py` refuses to produce an estimate without a measured per-unit runtime
(`estimate_hours(per_unit_seconds=None)` raises) and flags recorded claims that differ from
measurement by ≥2×. `corrected_reasons.py` supplies replacement reason text grounded in measured
runtime for reporting only — the frozen artifact is not edited. See
`RESOURCE-BOUND-RECLASSIFICATION.md`.

`status.py` encodes the run-status vocabulary so a partial run cannot be reported as a verdict:
`may_claim_refutation(30, 2000)` → `False`. Under this rule the original
`REFUTED_U4_PARTIAL` (30/2000, no prospective stopping rule) **could not have been emitted**.

## 4. Files changed

Added (all new, all under `hierarchical-aif/`):

```text
src/motor_stack_aif/__init__.py
src/motor_stack_aif/_bridge.py             read-only loader for the frozen runners
src/motor_stack_aif/bootstrap.py           legacy + corrected cluster bootstrap
src/motor_stack_aif/seeding.py             legacy_seed (pinned) + stable_seed
src/motor_stack_aif/status.py              run-status and CI-bound verdict semantics
src/motor_stack_aif/resource.py            measured-runtime estimator
src/motor_stack_aif/corrected_reasons.py   replacement reason text
tests/motor_stack_aif/*.py                 6 test modules, 30 tests
scripts/c11_paired_diagnostic.py           paired legacy-vs-corrected diagnostic
```

Modified: **none outside `hierarchical-aif/`.**

## 5. Test results

```text
29 passed, 1 xfailed
```

The xfail is `test_frozen_c01_reason_mismatch_is_a_known_historical_defect`, marked
`strict=True`: it asserts against the frozen artifact, which must not be edited, so it is
*expected* to fail. Strictness means an **XPASS would itself fail the suite** — a tripwire that
fires if the frozen artifact is ever mutated.

### Honest note on TDD ordering

The contract asked for red-before-green on D1/D3. What actually happened: the corrected
implementation and the tests were authored in the same step, so the *corrected-path* assertions
were green on their first execution. The defects are instead pinned by explicit **legacy-path
assertions that pass by asserting the defect exists** —
`test_legacy_bootstrap_demonstrates_the_defect` (groups < 80) and
`test_legacy_seed_demonstrates_the_defect` (seeds differ across processes). D4 is pinned as a
strict xfail against the frozen artifact.

That is a valid reproducer set, but it is **not** the strict red→green sequence that was
requested, and I am recording the difference rather than presenting it as compliance. Genuine red
states *were* observed and captured during development:
`H-AIF-G3-FAILING-TESTS-BEFORE-FIX.txt` records the first run — 4 failed, 11 passed, 2 collection
errors — including the `BLOCKED-SCALE-UNDEFINED` leakage trap described in §1.

## 6. Impact

**On old artifacts:** none. They remain byte-identical and reproducible, defect included.

**On future runs:** C11 must use `build_bootstrap_cohort`; C01/C02 must use `stable_seed`. Both
are prerequisites recorded in the reclassification schedule. C10 is unblocked immediately since
D1 does not affect it.

**On claims:** no claim is advanced by this gate. One (`P6`, via C11 U4) was withdrawn at
H-AIF-G2 and is not restored here — restoration requires the corrected full-N rerun at H-AIF-G5.
