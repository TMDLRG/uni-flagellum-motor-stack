# Data-Channel Spend Ledger

**Opened:** 2026-07-21 (gate H-AIF-G2, after D5) · **Append-only.**
**Dataset:** `experiments/data/wadhwa-2022-events.json` — 1349 events, 99 motors, single study
(Wadhwa 2022). Split: `holdout` iff `sha256_mod5(motorId) == 0`, else `train`.

A *channel* is a field × split. Once a held-out channel is read by any analysis, it is **spent**:
no later claim on it can be `PROSPECTIVE`. Reading is irreversible. This ledger records what has
been spent, by whom, and what claims each channel can still support.

> **Why this exists:** D5. A read-only audit track was asked for "empirical marginals of
> direction/jump per state" and, in answering, read the held-out mark channel. Nothing was written
> and no file was modified — and the channel was destroyed anyway. Read-only is not
> consequence-free.

---

## 1. Split-boundary vocabulary

Every new analysis must declare exactly one:

```text
TRAIN_ONLY
HOLDOUT_ALREADY_SPENT_DURATION_ONLY
HOLDOUT_ALREADY_SPENT_DIRECTION
HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY
INDEPENDENT_TRANSFER_REQUIRED
PROSPECTIVE_NEW_DATA_ONLY
NO_DATA_ACCESS_NEEDED
```

## 2. Ledger

| field | split | first_read_by | first_read_artifact | prospective_status | claim_allowed | claim_forbidden | notes |
|-|-|-|-|-|-|-|-|
| `durationS` | **holdout** | B2/B3 held-out scoring (pre-existing, authorised) | `audits/phase-b/b3-model-competition-result.json` | **SPENT — legitimately, under a committed prospective record** (`e5b4969` prediction-only commit preceded `9f24848` result) | Held-out predictive scoring of duration models; the retained adverse M2-over-M3 result | New "prospective" duration claims on this holdout without a fresh prediction commit | This spend was correct: prediction was committed before the result. Duration is the channel B3/B4 are built on. |
| `durationS` | train | B2/B3 fitting | `b3-model-competition-runner.py` | n/a (training) | Model fitting | Using training fit as held-out evidence | — |
| `stateN` | **holdout** | cohort eligibility + per-state scale normalisation | `b3-model-competition-result.json` (`summary.scale_N`, `holdoutMotorEventCounts`) | **SPENT** — used to define cohorts `[1..8]` / `[0..8]`, to normalise `_y`, and in B4C07 eligibility reproduction | Cohort membership, state-stratified scoring, eligibility statements | Treating a new state-conditional analysis on this holdout as prospective | Per-state holdout counts are published in the B4 result (`B4C07.perStateHoldout`). |
| `rightCensored` | **holdout** | cohort construction (exclusion flag) | `b3-model-competition-result.json`; `B4C05` censoring sensitivity | **SPENT** | Censoring-treatment sensitivity; the 18-uncensored-events-at-state-0 exclusion | Prospective censoring claims on this holdout | B3 competition EXCLUDES censored holdout events by frozen rule. |
| `direction` | **holdout** | competing-risks first-passage likelihood (pre-existing) | `lib/source-first-passage.js:59-65`; `scripts/run-science-gates.py:104-115,181-197` | **SPENT — before D5**, by a committed gate | Cause-specific (on/off) first-passage scoring | Claiming the binary direction channel is unspent | I initially and wrongly assumed the whole mark was unused. `direction` was already consumed. |
| `nextStateN` | **holdout** | **UltraCode Track C, 2026-07-21 (D5)** | `hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md` (D5); Track C body | **BURNED — improperly, with no prospective record** | **Retrospective / exploratory analysis only** | **Any `PROSPECTIVE` mark-process claim on Wadhwa-2022** | Cannot be repaired in this dataset: one study, no second holdout. |
| `jump` | **holdout** | **UltraCode Track C, 2026-07-21 (D5)** | same as above | **BURNED — improperly** | Retrospective / exploratory only | Any `PROSPECTIVE` mark-magnitude claim on Wadhwa-2022 | Joint `(N, N')` transition structure also exposed. |
| `nextStateN`, `jump` | train | Track C; also D6 verification | Track C body; defect ledger D6 | Training data — free to use | Fitting a mark model on training | Presenting a training fit as held-out evidence | Training-side use remains fully available. |
| `motorId` | both | split derivation `sha256_mod5(motorId)` | `b3-model-competition-runner.py` | Structural, not an observable | Defining the split; motor-cluster resampling | Using motor identity as a predictor | The split itself must never change. |
| `eventId`, `enteredAtS`, `eventAtS`, `splitRemainder`, `partition` | both | bookkeeping | — | Not scientific observables | Provenance/ordering | Use as covariates | — |

## 3. Consequences now in force

1. **Mark-process models on Wadhwa-2022 are `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET`.** They
   may still be built and reported — labelled as exploratory — but they cannot move `P3` as
   prospective held-out evidence.
2. **Prospective mark-process mechanism evidence now requires `INDEPENDENT_TRANSFER_REQUIRED`** —
   a new dataset with a new prospective split. This folds the mark question into the `P4`/`P7`
   requirement the project already carries.
3. **`durationS` on holdout remains legitimately spent**, so B3/B4 duration work is unaffected and
   the corrected C02/C10/C11/C01 runs are unaffected — none of them reads the mark.

## 4. Access protocol required before any new data-touching task

Any task that might touch held-out fields must first write
`hierarchical-aif/protocols/<TASK>-DATA-ACCESS-PROTOCOL.md` declaring: fields to read, split to
read, fields forbidden, claim boundary, prospective/exploratory status, falsifier, stop condition.

The Track C brief did none of this. That omission is the root cause of D5, and the requirement
exists so it cannot recur silently.
