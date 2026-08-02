This document is design-only reference architecture. This repo contains no organ, language, self-model, reasoning, dreaming, or awareness dataset. Nothing in this file is runnable evidence. Nothing in this file raises any P-level.

# Human L0–L12 Reference Architecture (DESIGN-ONLY)

**Status:** `NOT-BUILT` · `NOT-SCORED` · `NOT-CLAIMED` · `DESIGN-ONLY`

---

## 1. Why this file exists, and why it stays inert

The stacked active-inference architecture is described across two stacks. Only one of them has
data in this repository.

| stack | data here? | status |
|-|-|-|
| Human/reference `L0..L12` | **none** | design context only — this file |
| Flagellum motor `Lmotor-5..0` | yes (Wadhwa 2022) | runnable and scoreable |

Implementing `L0..L12` would produce scaffolding that no gate in this repository can ever test.
Impressive-looking unfalsifiable code is precisely what the truth contract exists to prevent, so
the human stack is recorded as architecture and **not** built.

## 2. The reference stack

Each level would carry: external states `η`, sensory states `s`, active states `a`, internal
states `μ`, blanket `b = {s, a}` with `p(μ, η | b) = p(μ | b) · p(η | b)`; a variational free
energy `F` used **only** for belief update; and, where the level can act, an expected free energy
`G` used **only** for policy selection.

| level | domain | would need data of type |
|-|-|-|
| L0 | molecular / channel / reaction | single-molecule kinetics |
| L1 | cellular homeostasis | intracellular state time series |
| L2 | tissue / metabolic fields | spatial metabolite fields |
| L3 | organ systems | physiological control signals |
| L4 | affect / precision / allostasis | interoceptive + autonomic recordings |
| L5 | sensorimotor control | proprioception, kinematics |
| L6 | perception / world model | multimodal sensory scenes |
| L7 | language / symbolic action | text, speech, discourse state |
| L8 | self-model / metacognition | confidence and error-monitoring data |
| L9 | reasoning / model selection | hypothesis-test traces |
| L10 | social / normative / long horizon | social and institutional records |
| L11 | offline replay / dreaming | internally generated sample traces |
| L12 | awareness boundary | **open question — no closed model accepted** |

**None of these datasets exists in this repository.**

## 3. What the architecture legitimately contributes

Nature and this architecture supply a **candidate structure**: nested inference, typed blankets,
per-level clocks, bottom-up evidence and top-down priors/preferences/precision. That motivated the
motor-stack design — hierarchy over motors, hazard/survival at the observation boundary, state
conditioning.

**Nature supplies the architecture candidate. The gate supplies the status.** A citation to
biology never moves a UNI gate.

## 4. The scale-ladder rule

A quantity fitted at one rung may not be silently moved to another. A dwell-time shape parameter
estimated from 19 holdout motors says nothing about organ control, language, or awareness. The
motor stack is an instantiation at one rung of this architecture; it is not evidence for the rest
of the ladder.

## 5. L12 stays open

The awareness boundary is not a deliverable. No closed model is accepted, and the honest program
position is a developmental active-inference simulation — a toy world, not a person. Any future
work here must first define a falsifiable criterion and then risk it.

## 6. Forbidden readings of this file

- that the human stack is built, validated, or partially demonstrated
- that motor-stack results transfer upward to any human level
- that architectural correspondence with biology constitutes parity evidence
- that `G` at any level is biologically tested by this repository

See `MOTOR-STACK-AIF-SCOPE-RULING.md` for what **is** buildable and scoreable.
