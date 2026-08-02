# ORCHESTRATE Rules — FLOW, STOP conditions, lanes, firewall

Binding for every agent working in `hierarchical-aif/`.

---

## 1. FLOW — and the NEXT_ACT requirement

```text
PERCEIVE -> BOUND -> PREDICT -> CHOOSE -> ACT -> OBSERVE -> UPDATE -> RECORD -> NEXT_ACT
```

**Every RECORD step must end with `NEXT_ACT`.** If no immediate ACT is possible, write the exact
blocker and the exact receipt needed to unblock it.

### Alignment is not a stop state

Do **not** stop after:

- saying you are aligned
- writing a report
- creating a ledger
- tests passing
- discovering a defect
- the next step being long

`"Awaiting"` is permitted **only** for a genuinely running process, and while awaiting you must
work a safe non-interfering lane (§4).

Append a FLOW card to `reports/FLOW-JOURNAL.jsonl` for every major action:

```json
{"flow_id":"F0NN","gate":"H-AIF-G#","step":"PERCEIVE|BOUND|PREDICT|CHOOSE|ACT|OBSERVE|UPDATE|RECORD",
 "question":"...","state_before":"...","alive_hypotheses":["..."],"falsifier":"...",
 "action":"...","receipt":"...","state_after":"...","next_action":"..."}
```

Externalize decisions as audit-ready records. Do not dump private reasoning.

## 2. STOP conditions — the only legitimate stops

| id | condition |
|-|-|
| `STOP_FROZEN_EVIDENCE_DRIFT` | frozen audits changed or hash mismatch appears |
| `STOP_DESTRUCTIVE_ACTION_REQUIRED` | next action would modify frozen evidence, push to remote, delete historical artifacts, or transmit externally |
| `STOP_PROTOCOL_CHANGE_REQUIRED` | next action requires changing planned N, scoring rule, held-out access, threshold, or stopping rule |
| `STOP_RESOURCE_COLLISION` | starting another job would corrupt an active job |
| `STOP_TEST_REGRESSION` | a required test fails in a way that invalidates the current runner or model path |
| `STOP_MISSING_FILE_OR_COMMAND` | a required runner/protocol/result path cannot be located after search |
| `STOP_USER_EXTERNAL_TRANSMISSION` | the user must personally send something; never claim transmission |

**Everything else is a FLOW action, not a stop.**

## 3. Lanes — scope every impact

| lane | scope |
|-|-|
| **A** | duration-only B3/B4 evidence |
| **B** | corrected B4 robustness cells |
| **C** | mark process / `nextStateN` / `jump` |
| **D** | motor-stack AIF implementation |
| **E** | biological parity ladder |
| **F** | governance / reporting / claim guard |

**Forbidden:** `"P6 is weaker"`.
**Required:** `"P6 for C11 U4 is withdrawn until the corrected C11 run lands; P6 for duration-only
B3/B4 is unchanged."`

A defect in one lane never licenses a global retreat.

## 4. Safe non-interfering work while long runs execute

Allowed:

- complete F-side implementation and tests
- prepare prediction records and launch scripts for queued cells
- prepare the F-side scoring harness
- update the defect **closure** ledger
- run the claim guard
- update the biological-parity receipt map

Forbidden while runs execute:

- new broad exploratory audits
- **any** new held-out read
- new mark-process analyses
- new parity claims
- unscoped weakening statements

## 5. The D5 held-out data firewall

**Reading held-out data is irreversible. Read-only is not consequence-free.**

D5: a read-only track was briefed to report "empirical marginals of direction/jump per state." The
brief carried no split boundary. The agent read the held-out mark channel to answer it. Nothing was
written, no file was modified, and the channel was destroyed anyway — no mark-process claim on
Wadhwa-2022 can ever be `PROSPECTIVE` again. One study, no second holdout, unrepairable.

Rules now in force:

1. Every analysis declares a split boundary:
   `TRAIN_ONLY` · `HOLDOUT_ALREADY_SPENT_DURATION_ONLY` · `HOLDOUT_ALREADY_SPENT_DIRECTION` ·
   `HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY` · `INDEPENDENT_TRANSFER_REQUIRED` ·
   `PROSPECTIVE_NEW_DATA_ONLY` · `NO_DATA_ACCESS_NEEDED`
2. Consult `docs/DATA-CHANNEL-SPEND-LEDGER.md` before touching any field.
3. Any task that might touch held-out fields first writes
   `protocols/<TASK>-DATA-ACCESS-PROTOCOL.md`.
4. Every subagent brief pastes the firewall from `docs/SUBAGENT-BRIEF-TEMPLATE.md`.
5. `NOT_CHECKED — would require holdout access` is a **correct and valuable** answer, never a
   failure.

The firewall is also enforced in code: `events.load_events(mode=MARK_RETROSPECTIVE)` raises
`HoldoutMarkAccessError` unless the caller explicitly acknowledges retrospective status.

## 6. Defect closure discipline

A defect is a completed FLOW result only when routed into **repair, quarantine, rerun, transfer,
or falsification**. Every defect row must carry `closure_status`, `last_action`, `next_action`,
`blocked_by`, and `not_blocked_lanes`.

Closure vocabulary:

```text
CLOSED
CLOSING_BY_TESTED_REPAIR
QUARANTINED_WITH_TRANSFER_ROUTE
OPEN_AWAITING_CORRECTED_RUN
FALSIFIED_AND_RETIRED
```

If a defect is not closing, name the **exact missing receipt**.

## 7. Evidence discipline (inherited, still binding)

- Partial logs are **not** results. Never interpret a running job's stdout as a finding.
- A crashed run is `FAILED_RUN`, not a scientific negative.
- `actual_N = 0` → `NOT_RUN`; `0 < actual_N < planned_N` → `PARTIAL_NOT_ESTABLISHED` unless a
  prospective sequential stopping rule was declared **before** the run.
- Point estimates are never verdicts. A CI crossing the threshold is `NOT_ESTABLISHED`.
- The experimental unit is the **motor**. Bootstraps resample motors, never events.
- Underpowered is **not** equivalence. But note: a small yet *consistent* paired effect **is**
  resolvable — "small" and "unresolvable" are different claims.
- No floor anywhere. A non-finite log density HALTs.
- Prediction records are committed **before** the run they describe.
- Never overwrite a historical artifact. Corrected results take new names.

## 8. Strong inference

Keep alive until a predeclared discriminator removes them:

- `H_PARITY` as **target hypothesis**
- the current design as **control**
- M0/M1/M2/M5/M8 as **adversaries** — M2 currently out-predicts the mechanism on held-out data,
  and that adverse result is retained
- negative controls: invalid censoring, event-level bootstrap, orientation/label scrambling

Nature may motivate the architecture. Only a gate moves a status.
