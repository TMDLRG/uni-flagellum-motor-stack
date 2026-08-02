# Gap Audit — Stacked AIF Spec vs Actual Code

**Gate:** H-AIF-G6 · **Method:** 8-track parallel read-only audit, 134 findings · **Date:** 2026-07-21
**Status counts:** `PRESENT` 33 · `PARTIAL` 47 · `ABSENT` 41 · `WRONG` 13

**Do not re-run this audit.** It is recorded here so a new agent inherits it. Individual findings
were spot-verified by the builder where consequential; unverified rows are marked.

---

## Headline

**The active-inference machinery is essentially absent from the science pipeline.** All nine B3
models (M0–M8) are maximum-likelihood density fits. **No model computes a variational or an
expected free energy.** The stack that exists is a hierarchy of *statistical* models, not a stack
of inference loops.

## Core components

| component | expected | status | reality |
|-|-|-|-|
| Variational free energy `F` | `E_q[ln q − ln p]`, belief update only | **ABSENT** (science pipeline) | No `F` anywhere in `audits/phase-b/*.py` or `scripts/*.py`. Runtime `lib/uni-motor.js` computes a scalar labelled `F` from an exact categorical Bayes step where `KL ≡ 0` by construction — a readout, not a minimised objective *(unverified by builder)* |
| Expected free energy `G` | risk + ambiguity, policy selection only | **ABSENT / WRONG** | Absent from the science pipeline. Runtime version reportedly adds ambiguity twice plus an undeclared `effort` term; `docs/SCIENCE.md:83` freezes the same non-standard formula *(unverified by builder)* |
| Policy layer `π` | action sequences with horizon | **ABSENT** | No action field exists in the dataset. The action set is structurally empty |
| Policy priors `E`, policy precision `γ` | habits, softmax temperature | **ABSENT** | — |
| Sensory precision `Π` | prediction-error weighting | **ABSENT** | "precision" in-repo means numeric tolerance |
| Preferences `C`, state priors `D` | preferred/prior outcome distributions | **PARTIAL** | Only as implicit MLE priors |
| Up/down messages | `U = {q, ε, Π, F, …}` / `D = {C, D, E, γ, Π}` | **ABSENT** | No inter-level message structure |
| Markov blanket `b = {s, a}` | `p(μ,η∣b) = p(μ∣b)p(η∣b)` | **PARTIAL** | Sensory half exists as an event table; **no active state `a`** |
| Asynchronous per-level clocks | levels update at own rates | **ABSENT** | — |

## Motor-stack levels

| level | status | reality |
|-|-|-|
| `Lmotor-5` population prior `Θ` | **PARTIAL** | M7 has 2 marginal parameters; no population posterior |
| `Lmotor-4` motor identity `η_m` | **PARTIAL** | M7 integrates a per-motor latent but reports **point estimates only** — no `q(η_m)` |
| `Lmotor-3` occupancy `N_i` | **PARTIAL** | State used for cohort membership and per-state scale normalisation; no transition kernel |
| `Lmotor-2` kinetic/policy `z_i, π_i` | **ABSENT** | — |
| `Lmotor-1` hazard/survival | **ABSENT in B3** / **PRESENT elsewhere** | B3 uses plain densities and **excludes** censored events. A correct competing-risks hazard/survival implementation exists in `lib/source-first-passage.js:59-65` and `scripts/run-science-gates.py:104-116` |
| `Lmotor-0` observed blanket | **PARTIAL** | All 12 fields recorded; `nextStateN`/`direction`/`jump` **never read by B3** |

## The 13 `WRONG` findings — the consequential ones

**Builder-verified:**

1. **`M6_SEMI_MARKOV_STATE_DEPENDENT` is not semi-Markov.** It is 8 independent per-state mean-one
   Weibull fits with **no transition kernel**. Blocks any reading of B3 as evidence about
   transition structure, and means the most obvious mechanistic alternative — that transitions
   carry information beyond dwell duration — **was never entered into the competition**.
2. **C11 U4 cluster-collapse bootstrap** → defect **D1**.
3. **Resource costs overstated 17–29×** → defect **D2**.
4. **`hash()` seeding non-deterministic** → defect **D3**.
5. **C01 reason cites models the cell skips** → defect **D4**.
6. **`nextStateN = −1` in 2 holdout events; ingest never range-checks `next_state`** → defect **D6**.
7. **`width` field is the percentile companion, not the BCa/`intervalUsed` width, in 48/48 entries**
   → defect **D7**.

**Reported, NOT builder-verified** (carry as `REPORTED_UNVERIFIED`; do not repeat as fact):

8. Runtime `G(π)` double-counts ambiguity and adds an undeclared `effort` term.
9. Runtime `F` is a readout of exact Bayes; `tests/model.test.mjs` "free-energy identity is exact"
   is tautological (`KL ≡ 0` by construction).
10. Runtime agent re-executes the world's exact torque-speed constants → shared-implementation
    oracle on the speed/stator channels.
11. UI declares `q(o∣π)=Σ P(o∣s)q(s∣π)` but implements ad-hoc linear ligand extrapolation
    (constants 0.08 / 0.25).
12. Runtime models stators as a continuous ODE relaxation, not a discrete occupancy jump process.
13. `ingest-wadhwa-data.py` counts 109 right-censored dwells under `exclusions` but does **not**
    exclude them (no `continue`); all 109 are in the 1349-event artifact.

## What this implies for the build

- Building the full stack would mean building `F`, `G`, policies, precision, and message passing
  **from scratch** — none is inherited.
- **`G` cannot be tested here**: the action set is empty. See `MOTOR-STACK-AIF-SCOPE-RULING.md`.
- The **hazard/survival** and **per-motor posterior** pieces are genuinely new contributions of the
  F-side build; the frozen pipeline has neither in its competition path.
- Findings 8–13 concern the **shipped runtime**, not the science pipeline. They do not affect B3/B4
  results. They remain unverified and must be checked before being acted on.

## Provenance

Raw findings: workflow `wf_455a1ab3-222`. Verification of the Track D/E/F design documents:
`reports/ULTRACODE-TRACK-{D,E,F}-VERIFICATION.md` — note that verification **contradicted six** of
Track D's supporting receipts while its headline (full stack not identifiable) survived.
