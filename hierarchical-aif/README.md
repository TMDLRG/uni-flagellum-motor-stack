# hierarchical-aif — START HERE

**If you are a new agent in this repository, read this file completely before taking any action.**

This directory holds the Hierarchical Active-Inference (H-AIF) program: the correction of defects
found in the submitted B3/B4 evidence package, the corrected reruns, and the constrained F-side
motor-stack model.

> **Provenance note.** This work was originally requested as "Phase-C closure" work, but is
> namespaced under `hierarchical-aif/` to avoid collision with frozen `audits/phase-c/` evidence.
> The frozen Phase-C audits remain read-only source evidence.

---

## Read in this order

| # | file | why |
|-|-|-|
| 1 | `../CLAUDE.md` § "Hierarchical-AIF program" | the binding contract |
| 2 | `docs/CURRENT-STATE-AND-NEXT-ACT.md` | **live state — what is running, what is next** |
| 3 | `docs/ORCHESTRATE-RULES.md` | FLOW, STOP conditions, lanes, firewall |
| 4 | `docs/H-AIF-GATES.md` | gate definitions G1–G9 |
| 5 | `ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md` | every defect and its routing |
| 6 | `docs/MOTOR-STACK-AIF-SCOPE-RULING.md` | what may be built and scored, and what is fenced |
| 7 | `docs/DATA-CHANNEL-SPEND-LEDGER.md` | **which data channels are already spent or burned** |

## The five rules that matter most

1. **`audits/phase-c/**` and `audits/phase-d/**` are frozen.** So is `audits/phase-b/**`. Verify
   against `reports/frozen-evidence-baseline.sha256` before and after any work session. A diff is a
   hard stop.
2. **Reading held-out data is irreversible.** Declare a split boundary for every analysis. Paste the
   D5 firewall into every subagent brief. See `docs/SUBAGENT-BRIEF-TEMPLATE.md`.
3. **Alignment is not a stop state.** Every RECORD ends with `NEXT_ACT`. Reports and passing tests
   are not endpoints.
4. **Never write an unscoped weakening statement.** Name the lane.
5. **`P0..P8` is authoritative and unchanged.** H-AIF gates map onto it; they never redefine it.

## Layout

```text
docs/        rulings, gate definitions, contracts, receipt maps
ledgers/     defect ledger, defect CLOSURE ledger, gate->P-ladder map, negatives/partials
protocols/   pre-run prediction records (written BEFORE a run) and data-access protocols
reports/     gate reports, run reports, FLOW-JOURNAL.jsonl, claim-guard reports, hash baselines
results/     run outputs + logs + hashes (motor_stack_aif/)
scripts/     run harnesses and launchers
src/         motor_stack_aif package
tests/       pytest suite (currently 71 passed, 1 strict-xfail)
```

## Running the suite

```bash
python -m pytest hierarchical-aif/tests/motor_stack_aif -q
```

The single `xfail` is intentional and **strict**: it pins defect D4 against a frozen artifact that
must not be edited. An `XPASS` there means the frozen evidence was mutated — a contract violation.

## The `src/motor_stack_aif` package

| module | role |
|-|-|
| `_bridge.py` | read-only loader for the frozen B3/B4 runners |
| `events.py` | typed `ObservedEvent`; **enforces the D5 firewall in code** |
| `hazard_survival.py` | uncensored `log h + log S`, censored `log S`; **no floor**, non-finite HALTs |
| `hierarchy.py` | Lmotor-5..1; per-motor latents integrated by quadrature, **2 free params** |
| `free_energy.py` | `F = complexity − accuracy`. **Contains no `G` by design** |
| `fit.py` | deterministic Nelder-Mead, no RNG |
| `score.py` | motor-equal scoring; bootstrap resamples **motors**; CI-bound verdicts |
| `baselines.py` | M0/M1/M2/M5 — **adversaries, never the UNI model** |
| `bootstrap.py` | corrected cluster bootstrap (D1) + retained legacy defective path |
| `seeding.py` | `stable_seed` (D3) + retained `legacy_seed` to pin the defect |
| `marks.py` | D6 quarantine policies; **no silent-drop policy exists** |
| `status.py` | run-status and CI-bound verdict semantics |
| `resource.py` | refuses cost estimates without measured runtime (D2) |
| `claim_guard.py` | forbidden-wording clamp with use/mention handling |

## What this program has NOT established

No P-level has been raised. The F-side model is **built but not yet scored**. Full biological
parity is not a current status — it is the target world defined by the receipts in
`docs/BIOLOGICAL-PARITY-RECEIPT-MAP.md`.
