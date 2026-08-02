# H-AIF Gate → Existing P-Ladder Map

**This file is a MAPPING, not a new ladder.**

> The hierarchical-AIF gates do not replace the existing P0–P8 ladder. They produce new receipts
> that map onto the existing ladder definitions in `CLAUDE.md`.

---

## 1. The existing ladder (authoritative, unchanged)

Defined in `CLAUDE.md`. **Not redefined here. No v2. No parallel Q-ladder.**

```text
P0 = computational integrity
P1 = equation / implementation
P2 = observational
P3 = held-out predictive
P4 = transfer
P5 = intervention
P6 = structural / mechanistic
P7 = independent replication
P8 = full verdict
```

`P8` is **conjunctive**: any single required `FAIL`, `CONTRADICTED`, `NOT_ESTABLISHED`,
`BLOCKED_EXTERNAL`, `NOT_RUN`, or `INVALID_PROVENANCE` makes `FULL_PARITY = false`.

## 2. Gate definitions (new work)

```text
H-AIF-G1 = repo + frozen evidence integrity
H-AIF-G2 = correction notice + defect ledger
H-AIF-G3 = failing tests for verified defects
H-AIF-G4 = runner fixes and resource-bound reclassification
H-AIF-G5 = corrected full B4 reruns
H-AIF-G6 = full motor-stack AIF gap audit + isolated implementation
H-AIF-G7 = current design control + adversarial alternatives + corrected AIF scoring
H-AIF-G8 = raw archive / transfer protocol status
H-AIF-G9 = ledger/ladders/docs/handoff update
```

## 3. Mapping

| gate | maps to | status | receipt |
|-|-|-|-|
| H-AIF-G1 | `P0` computational integrity | **ESTABLISHED** | `reports/H-AIF-G1-REPO-AND-FROZEN-EVIDENCE-INTEGRITY.md` |
| H-AIF-G2 | `P1`; `P3`/`P6` interpretation (via D1); `P0`/`P1` provenance (via D2/D4) | **ISSUED** | `reports/CORRECTION-NOTICE-TO-REVIEWER.md`, `ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md` |
| H-AIF-G3 | `P1` equation/implementation | **COMPLETE** | `results/motor_stack_aif/H-AIF-G3-FAILING-TESTS-BEFORE-FIX.txt` |
| H-AIF-G4 | `P1` equation/implementation; `P0` provenance | **COMPLETE** | `reports/H-AIF-G4-RUNNER-FIX-REPORT.md`, `reports/RESOURCE-BOUND-RECLASSIFICATION.md` |
| H-AIF-G5 | `P3` held-out predictive; `P6` structural/mechanistic (per cell) | **COMPLETE — all four corrected cells landed at full frozen N.** B4C10, B4C02, B4C01, **B4C11** (`564a5b0f…`, `U4_OK`, collapse 0.0055). Every cell's prediction record was committed ahead of its result except B4C10 (D9, structurally unattainable) `B4C10` (`959a00e9…`), `B4C02` (`0633988d…`), `B4C01` (`8256cb12…`), **`B4C11` (`564a5b0f…`)** — each + report. B4C11 prospectivity **SATISFIED** (prediction `897c8ab` committed ~19.4 h before the observation) |
| H-AIF-G6 | `P1`; and `P6` gap status | **AUDIT COMPLETE / IMPLEMENTATION NOT_STARTED** | `docs/GAP-AUDIT-FULL-HIERARCHICAL-MOTOR-MODEL.md` |
| H-AIF-G7 | `P3`; `P6` discriminator pressure | **EXECUTED — verdict `NOT_ESTABLISHED`** against control and strongest adversaries; `RESOLVED_ABOVE` only vs M0/M5. **Coverage extended 2026-07-22**: M4/M6/M7 contrasted post-hoc, **neither M4 nor M6 resolves**; candidate ranks 5th of 10; M7 exposed **D10** | `results/.../F_SIDE_MOTOR_STACK_SCORING_RESULT.json` (`b3b12720…`), `results/.../M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json` (`751a59ef…`), reports for both |
| H-AIF-G8 | `P2` observational *if* raw archive rederived; `P4` transfer *only* if an independent dataset exists | **NOT_LOCATED / NOT_ESTABLISHED** | pending |
| H-AIF-G9 | no new evidence by itself; records mapped status changes only | **IN PROGRESS** | this file |

## 4. Ledger rule

A gate result may update a P-level **only if all six hold**:

1. the existing P-level definition is named;
2. the source artifact is named;
3. the claim scope is named;
4. the falsifier is carried;
5. partial / not-run / negative states are preserved;
6. the update does not redefine the P-level.

## 5. Current P-level status after this correction round

| level | status | note |
|-|-|-|
| `P0` computational integrity | **holds — strengthened** | H-AIF-G1 receipts; D2/D4 are provenance defects in *reason text*, corrected in new reports without editing frozen artifacts |
| `P1` equation/implementation | **defect found and fixed in the new namespace** | D1 bootstrap collapse + D3 seeding; corrected implementations under `hierarchical-aif/src/`; the committed runner retains its defect and its results are withdrawn, not silently patched |
| `P2` observational | **unchanged** | no new observation; raw archive not located |
| `P3` held-out predictive | **unchanged; B3 stands — and its INTERPRETATION is now measured** | D1 does not touch the B3 leaderboard. The adverse M2-over-M3 result remains the retained headline. **B4C01 (`8256cb12…`) measured what this design can resolve**: under correct specification the two structurally distinctive generators self-win at 0.885 and 0.935, but `M0_EXPONENTIAL` — nested inside M1 and M5 and a degenerate limit of M3 — self-wins only **0.290**, against a `>0.5` criterion. The assay is **nesting-blind at 19 holdout motors**, not uniformly underpowered. An `INCONCLUSIVE` contrast between nested near-equivalent models is therefore the EXPECTED output of the design and is not evidence about the models. This **constrains interpretation and raises no level**. **H-AIF-G7 added a candidate without moving the level**: the F-side motor stack scored `NOT_ESTABLISHED` against `CONTROL_CURRENT` and every serious adversary, and reproduces the frozen `M7` to `2.5e-7` nats. A `NOT_ESTABLISHED` verdict is not equivalence and does not raise `P3` |
| `P4` transfer | `NOT_ESTABLISHED` | single study; no independent dataset |
| `P5` intervention | `NOT_ESTABLISHED` | unchanged |
| `P6` structural/mechanistic | **scoped — see the four statements below; there is no single `P6` verdict** | An unscoped "`P6` is weakened" is forbidden by `CLAUDE.md` and was replaced by the closure ledger. `P6` is carried per scope, never in aggregate |
| `P7` independent replication | `NOT_ESTABLISHED` | external review in progress; not complete |
| `P8` full verdict | **`FULL_PARITY = false`** | unchanged. First unsatisfied level remains `P4` transfer |

### 5a. `P6` carried per scope (the required form)

An unscoped weakening statement is a contract violation: a local failure must never be reported as
a global retreat. `P6` is therefore carried as four separate statements, each with its own receipt
and its own falsifier.

| `P6` scope | status | receipt / blocker |
|-|-|-|
| `P6` for **C11 U4** (M7 dispersion stability) | **RE-ESTABLISHED on the corrected full-N run only** (`U4_OK`, collapse 0.0055, N=2000). The withdrawn 30-replicate artifact stays withdrawn | `B4C11_CORRECTED_FULL_RESULT.json` (`564a5b0f…`), `reports/B4C11-CORRECTED-FULL-REPORT.md`; D1 `CLOSED_BY_CORRECTED_RERUN` |
| `P6` for **Wadhwa mark-process mechanism** | **RETROSPECTIVE-ONLY, TRANSFER-REQUIRED** | D5 (holdout mark channel burned), D6 (`nextStateN` unchecked); needs an independent dataset |
| `P6` for **duration-only B3/B4** | **UNCHANGED** | D1 does not touch the B3 leaderboard; the adverse M2-over-M3 result stands |
| `P6` for **full motor-stack AIF** | **PENDING** constrained implementation + scoring | H-AIF-G6 built / H-AIF-G7 scoring |

`P6` for **B4C10 / M4 identifiability** is a *separate* scope again: B4C10 at full frozen N=2000
supports M4 identifiability on the `derived_eligible_1_to_8` cohort under the frozen U2/U3/U4
criteria. **Identifiability is not correctness and is not mechanism**, and this result may not be
transferred to C11 (different model, different likelihood structure).

**No P-level was raised by this round.** `P6` for C11 U4 was **lowered** (withdrawing defective
evidence) and then **re-established on the corrected run only** — the gate working end to end:
withdraw on defect, restore on a valid rerun, and never restore the defective artifact itself.
B4C10/B4C02/B4C01/B4C11 landing at full N removed four `RESOURCE_BOUND`/withdrawn states without
raising any level. Identifiability is not correctness and is not mechanism.
