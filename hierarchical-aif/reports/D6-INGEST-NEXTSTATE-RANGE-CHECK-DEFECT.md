# D6 — Ingest Writes Out-of-Range `nextStateN`

**Defect:** `D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED` · **Date:** 2026-07-21 · **Gate:** H-AIF-G2
**Classification:** `INGEST_MARK_FIELD_DEFECT` **+** `RAW_ARCHIVE_REQUIRED_TO_RESOLVE_OR_CONFIRM`
**Status:** `VERIFIED` (independently reproduced by the builder)
**Split boundary of this analysis:** the two affected events are in the holdout partition; the
mark channel there was already burned by D5, so inspecting them adds no new spend.

---

## 1. Finding

Two events record a **physically impossible stator count** (a below-physical-minimum target-state
mark, `nextStateN` below the physical floor of 0 stators) in the mark field. Both events are in the
holdout partition, both from the same holdout motor.

> **D12 redaction notice.** The exact event identifiers, the source motor identifier, and the
> per-event `stateN`/`nextStateN`/`jump`/`direction` values were removed from this distributable
> report per the D12 incident-remediation ruling (event-level held-out mark data must not survive
> in a shipped artifact). The scientific finding below is unchanged: two holdout events carry
> `nextStateN` values below the physical floor. The event-level record used to be reproducible
> internally via `tests/motor_stack_aif/test_nextstate_range_check.py`, which is itself excluded
> from external distribution (see D12 report) because its regression-testing purpose requires
> keeping the literal identifiers.

## 2. Root cause — exact source lines

`scripts/ingest-wadhwa-data.py`:

```python
141            if dwell["state"] < 0 or dwell["state"] > 11:
142                exclusions["outOfRangeDwells"] += 1
143                continue                      # <-- the DWELL's own state IS range-checked
...
147            next_state = dwell["nextState"]   # <-- read with NO range check
...
158                    "nextStateN": next_state,                     # written through
159                    "direction": None if next_state is None else ("on" if next_state > dwell["state"] else "off"),
160                    "jump": None if next_state is None else next_state - dwell["state"],
```

`grep -n next_state` returns only lines 147, 158, 159, 160 — **there is no range check on
`next_state` anywhere.**

Mechanism: the out-of-range dwell itself is correctly excluded (`outOfRangeDwells: 3`), but its
**predecessor** is retained and keeps a mark pointing at the excluded, impossible state. So the
exclusion is applied to the dwell but not propagated to the mark of the event before it.

## 3. Reproduction

```bash
python -c "import json;print([(e['eventId'],e['stateN'],e['nextStateN'],e['jump'],e['partition']) \
 for e in json.load(open('experiments/data/wadhwa-2022-events.json'))['events'] \
 if (e.get('nextStateN') if e.get('nextStateN') is not None else 0)<0])"
```

## 4. Consequence — a falsified boundary assumption

A mark model that enforces the physical reflecting boundary `P(jump < 0 | N = 0) = 0` assigns
`log p = −inf` to the first below-physical-minimum event named above. Under the runner's declared **no-floor policy**
(`b3-model-competition-runner.py`: non-finite log density HALTS), such a model **cannot be fitted
or scored** on this extraction without an explicit decision about these two events.

So: **the reflecting-boundary assumption at N = 0 is falsified by the recorded data at exactly one
event.** Either the step-fitting produced an impossible transition, or the ingest mis-propagated an
exclusion. **This is undecidable here — the raw MAT archive (`data/remodeling_data.mat`) is
absent** (`P2` observational is already `BLOCKED_EXTERNAL` for that reason).

## 5. Related structural constraints on any mark model

Both independently verified by the builder:

| constraint | measurement |
|-|-|
| Holdout events with **zero training support** under an unsmoothed `(N,N')` kernel | **5 of 233**, including the below-physical-minimum pair from §1. Each gives `log p = −inf` → HALT. Row-level `(N,N')` pairs are D12-redacted as reconstructable held-out record fragments; the count and consequence are unchanged. |
| Marks leaving the modelled state set `{1..8}` | **train 120/793 = 15.1%** (targets `{0:24, 9:84, 10:11, 11:1}`); **holdout 39/233 = 16.7%** (targets `{−1:1, 0:15, 9:21, 10:2}`) |

Implications:
1. **Smoothing is mandatory and outcome-determining.** An unsmoothed kernel HALTs. And the
   smoothing constant is not innocuous: in the Track C contrast it flipped the *sign* of the
   headline effect between α = 0.1 and α = 0.5. A hyperparameter that decides the direction of a
   result must be frozen in advance, not chosen after seeing outcomes.
2. **The process is not a closed Markov chain on the cohort.** With 15–17% of marks leaving
   `{1..8}`, either the alphabet must include out-of-cohort states or that mass is silently
   discarded and the remaining likelihood is inflated. A mark-bearing likelihood here is a
   **one-step-ahead conditional prediction, not a trajectory likelihood**, and must be described
   as such in its own artifact.

## 6. Impact on existing work

| area | impact |
|-|-|
| B3 duration results | **NONE** — B3 never reads the mark |
| B4 cells C01–C12 | **NONE** — no B4 cell reads the mark |
| Corrected runs C02/C10/C11/C01 | **NONE** |
| Any future mark-chain model over `{1..8}` | **INVALID until D6 is resolved or explicitly handled** |

## 7. Existing P-level mapping

| level | effect |
|-|-|
| `P2` observational | **Limitation recorded** for mark fields. Cannot be resolved without the raw archive, which is absent. |
| `P6` structural/mechanistic | **Limitation** — mark-chain mechanism models are blocked on this extraction. |
| `P0` provenance | Minor — the extraction contains a physically impossible recorded value. |
| `P4` / `P7` | **Requirement reinforced** — a clean mark channel needs independent data (also required by D5). |

No level rises.

## 8. Corrective action

1. **Do NOT edit the committed dataset.** It is the historical record; the defect is preserved.
2. Any future mark model must declare its handling of these two events explicitly — **reject**,
   **quarantine with an explicit status**, or **retain under a documented raw-data-defect label** —
   and must never silently drop them.
3. Regression test added: `hierarchical-aif/tests/motor_stack_aif/test_nextstate_range_check.py`.
4. If the raw archive is ever obtained, re-derive these two events first; that single check
   discriminates "step-fitting artifact" from "ingest defect".
