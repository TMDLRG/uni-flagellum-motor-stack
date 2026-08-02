# Motor-Stack AIF — Scope Ruling

**Gate:** H-AIF-G6 · **Date:** 2026-07-21 · **Status:** RULING IN FORCE
**Maps to existing ladder:** `P1` (implementation); `P3` only if scored

---

## 1. The ruling

```text
F-side observable projection      : BUILD_AND_SCORE_NOW
G-side biological policy selection: DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER
```

The model is **not** abandoned because one half of it is untestable on passive data. The half that
observational data *can* score is built now; the half that requires actions is fenced with an
explicit route to testability, not deleted.

## 2. Why F-side is buildable now

`F_motor` is a **belief-update objective over observations**. It needs only:

- a likelihood for what was recorded (dwell durations, with censoring),
- a hierarchy over the experimental unit (motors),
- an approximate posterior.

All three exist in this dataset. `F_motor` scores how well a nested generative model explains
held-out dwell durations. That is a legitimate observational projection of the stacked
architecture, and it is directly comparable to the existing competitors on the frozen split.

```text
F_motor = E_q[ ln q(Theta, eta, z) - ln p(o, z, eta, Theta) ]
```

**Nothing about computing `F_motor` asserts that the organism performs inference.** It is the
analyst's objective for fitting a hierarchical model. Keeping that distinction is the whole reason
this ruling exists.

## 3. Why G-side is fenced

`G_motor(pi)` scores **policies over future observations**:

```text
G_motor(pi) = KL[ q(o_future|pi) || p(o_future|C_motor) ] + E_q[ H[ p(o_future|z_future,pi) ] ]
```

A policy must range over **actions**. In this dataset there are none:

| candidate `pi` | verdict |
|-|-|
| Agent action sequence | **Not instantiable** — no action field exists. The set is empty, not small. |
| Experimenter load protocol | **Not testable** — `nominalElectrorotationSpeed` is constant per motor with no onset time; raw archive `BLOCKED_EXTERNAL` |
| The motor's own stator-exchange trajectory | **Category error and truth-contract hazard** — scoring `G` over hidden states asserts the organism performs the inference, which the B3 result's own `notEstablished[0]` disclaims |
| Index over predictive hypotheses | Legitimate as *inference* (model averaging under a nonstandard weight); **illegitimate as active inference** |
| Analyst's next experiment | **The only live reading** — ORCHESTRATE-level experiment choice |

The failure is **structural, not sample-size-limited**: the action set is empty, so no amount of
additional Wadhwa-2022 data would fix it. This is why the fence is a data requirement, not a
"collect more of the same" note.

**Classification:** `G_motor` biological policy selection = `DESIGN_ONLY_UNTIL_INTERVENTION`.
`G` may still be used at the **ORCHESTRATE level** to choose which experiment to run next — that
is how B4C02 was selected over the cheaper B4C10 — and that use is a laboratory-process choice,
never a claim about the motor.

## 4. What would make G a biological motor claim

Minimum required data — all three, not any one:

1. **A manipulated variable with recorded onset time** (load step, PMF step, or electrorotation
   change), timestamped against dwell boundaries.
2. **Paired pre/post observation on the same motors**, so the response is within-unit.
3. **Enough independent motors under each condition** to give a CI-bound verdict on the response.
   With the current resolution floor of ≈0.042 nats and 19 holdout motors, a between-condition
   contrast would need substantially more units — the exact number to be derived, not guessed,
   before any such run.

Absent these, any `G`-based motor claim is `NOT_ESTABLISHED` by construction.

## 5. Lane status under this ruling

| lane | status |
|-|-|
| **LANE A** duration-only B3/B4 | Valid within scope. Unchanged. |
| **LANE B** corrected robustness | In flight (C02, C10 running; C11, C01 queued). |
| **LANE C** mark process | **Retrospective-only** after D5; closed-chain modelling blocked by D6. Not used by the F-side build. |
| **LANE D** motor-stack AIF | **F-side: BUILD NOW.** G-side: design-only. |
| **LANE E** parity ladder | `P1` may move on implementation; `P3` only if scored; `P5`/`P6`/`P8` unaffected by this ruling. |

## 6. What the F-side build may and may not move

- **May move `P1`** (equation/implementation) once implemented and tested.
- **May inform `P3`** (held-out predictive) **only if scored** on the frozen split against the
  current-design control and the adversarial baselines, with a CI-bound verdict.
- **May not move `P5`, `P6`, or `P8`** without additional receipts.
- **May not** read held-out mark fields (D5 firewall).
- **May not** treat a favourable `F_motor` score as evidence that the motor performs inference.

## 7. Standing frame

```text
Nature supplies the architecture candidate.
The gate supplies the status.
Full biological parity is not a current status. It is the target world defined by the receipts.
```
