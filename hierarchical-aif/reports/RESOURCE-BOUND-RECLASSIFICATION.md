# Resource-Bound Reclassification (D2)

**Gate:** H-AIF-G4 · **Measured:** 2026-07-21 · **Maps to existing ladder:** `P0`/`P1` provenance
**Machine:** Windows 11 Pro 10.0.26200, Python 3.12.10, numpy 2.3.5, scipy 1.16.3, CPU-only
**Cohort:** `derived_eligible_1_to_8` (80 training motors / 793 training events / 19 holdout motors)

The recorded resource estimates in the committed B4 result are **withdrawn**. A `RESOURCE_BOUND`
status is only honest if the resource claim is true.

---

## 1. Measured per-unit runtimes

Each figure is a single timed call on the frozen cohort. Reproduce with
`python hierarchical-aif/scripts/../../<scratch>/verify_timing.py`.

| fit path | measured | used by |
|-|-|-|
| `b3.fit_simple_models` | **32.0 s** | C01, C02 |
| `b3.fit_m6` | **20.1 s** | C01, C02 |
| C01/C02 per-simulation (simple + M6) | **52.1 s** | C01, C02 |
| `b4._fit_m4_reduced` | **3.8 s** | C10 |
| `b4._fit_m7_reduced` | **36.2 s** | C11 U4 |
| `b4._m7_profile_at_tau` | ~2.9 s (audit figure, not re-timed) | C11 U2 |

**C01 and C02 do not run a 9-model competition.** The runner comment reads
`"skip M4/M7/M8 as they are the slow ones"`, and the cells record
`skippedModels = [M4_MIXTURE_K3, M7_HIERARCHICAL_MOTOR, M8_EMPIRICAL_KDE]`. The cost driver is
the simple model set plus M6.

## 2. Reclassification

| cell | frozen N | per-unit | **measured projection** | recorded claim | ratio | old status | **new status** |
|-|-|-|-|-|-|-|-|
| B4C01 | 1000 sims | 52.1 s | **14.5 h** | 250–400 h | 17–28× over | `NOT_RUN=RESOURCE_BOUND` | **SCHEDULED_FULL_N** (after D3 fix) |
| B4C02 | 600 sims | 52.1 s | **8.7 h** | 150–250 h | 17–29× over | `NOT_RUN=RESOURCE_BOUND` | **SCHEDULED_FULL_N — PRIORITY** (after D3 fix) |
| B4C10 | 2000 boots | 3.8 s | **2.1 h** | ran 100/2000 | — | `resourceBoundPartial` | **SCHEDULED_FULL_N** (unblocked now) |
| B4C11 U4 | 2000 boots | 36.2 s | **20.1 h** | ran 30/2000 | — | `resourceBoundPartial` | **SCHEDULED_FULL_N** (after D1 fix) |
| B4C09 | 100 jitter refits | full 9-model refit | not re-timed; audit suggests the recorded 25–40 h may be **understated** | 25–40 h | — | `NOT_RUN=RESOURCE_BOUND` | **`NOT_RUN` STANDS**, reason to be re-derived |

Total for the four schedulable cells: **≈45.4 h** of CPU-only compute, versus the ≈433–650 h
implied by the recorded reasons.

## 3. Consequences

- **B4C10 should never have been partial.** At 2.1 h it was always within reach. Its bootstrap
  method is sound (M4 fits the flat pooled `train_y`, so duplicates enter correctly), so only the
  replicate count was ever at issue.
- **B4C02 is the priority.** It is the HIGH-risk misspecified-world discriminator — the cell
  designed to test whether the adverse lognormal result reflects heavy-tailed dwell shape rather
  than one assumed mechanism. It was presented as unreachable at 150–250 h. It is ≈8.7 h. This is
  the most decisive missing evidence in the entire submission.
- **B4C11 remains blocked on D1**, not on cost. Running it at full N on the defective bootstrap
  would produce 2000 replicates of an invalid statistic.
- **B4C01/B4C02 remain blocked on D3** (non-deterministic `hash()` seeding) regardless of cost.

## 4. Ordering rationale

```text
1. B4C10   2.1 h   unblocked now; D1 does not affect it; method already sound
2. B4C11  20.1 h   requires the D1 bootstrap fix first
3. B4C02   8.7 h   requires the D3 seeding fix first; highest scientific value
4. B4C01  14.5 h   requires the D3 seeding fix first
```

Cheapest-and-unblocked first, then highest-value-once-unblocked. Every run at **full frozen N**;
no reduced N is used, so no prospective reduced protocol is required. If any run must later be
reduced, a prospective reduced protocol will be written **before** it starts.

## 5. Honest limits of this reclassification

- Timings are **single measurements on one machine**, not distributions. They are point estimates
  and could vary by a factor of ~2 on different hardware; they do not vary by the 17–29× needed
  to rescue the recorded figures.
- `_fit_m4_reduced` and `_fit_m7_reduced` were timed on the **real** cohort. Bootstrap replicates
  resample it, so per-replicate cost may differ modestly with the resampled event count.
- C01/C02 timings assume the synthetic-data generation cost is small relative to the fit cost.
  This was not separately measured.
- **B4C09 was not re-timed.** Its `NOT_RUN` status stands; only its stated reason is in question,
  and in the opposite direction (possibly understated). This is recorded as `R7` in the defect
  ledger as `REPORTED_UNVERIFIED`.

None of these caveats changes the conclusion: the recorded justifications are wrong by more than
an order of magnitude, and the cells are schedulable.
