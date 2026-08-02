# Scientific math workbench

Route: `/math-workbench`. Source: `app/math-workbench/page.tsx` (server, loads the frozen
reports) and `app/math-workbench/scientific-math-workbench.tsx` (client, 6 views).

This document exists because `CLAUDE.md` requires every surface to declare its evidence,
assumptions, units, falsifier, gate ledger, reproduction command and limitations. Nothing
here is new science; the workbench renders quantities computed elsewhere and executes the
repository's own model functions.

---

## 1. What the workbench is

A repository-native instrument that makes the committed mathematics **executable and
inspectable in the browser without re-implementing any of it**. Every number it displays
comes from one of two places:

1. **live execution** of `lib/uni-motor.js`, `lib/duration-models.js` or
   `lib/source-first-passage.js` in the browser, on CPU, deterministically; or
2. **frozen JSON reports** loaded server-side from `experiments/results/` and `audits/`.

It computes no quantity of its own. `tests/math-workbench.test.mjs` pins the calculators to
the library functions and guards against shadow re-implementations.

## 2. What the workbench is not

- It is **not** a new experiment. It runs no fit, produces no result artifact, and writes
  nothing.
- It is **not** evidence that a bacterial motor performs Bayesian inference. The synthetic
  agent loop is a reduced teaching model over a reduced synthetic world.
- It is **not** a claim of biological parity. `fullBiologicalParityAchieved` is `false` and
  is printed on the page.
- The `Execute the math` view runs a **synthetic world**, not recorded data. Its "observed
  ligand"/"observed speed" tiles are observations *of the simulation*.

---

## 3. Views

| View | Content | Evidence class |
|---|---|---|
| **Model stack** | the nine-step world → observation → prior → likelihood → posterior → policy → action → prediction sequence, and four status cards | modelled + report-derived |
| **Execute the math** | live stepping of `stepSyntheticSystem`, four controls, prior/likelihood/posterior/free-energy panels | modelled, synthetic |
| **Equation library** | 11 catalogued modules with equation, plain meaning, inputs, outputs, truth class and source binding; plus the M0–M3 dwell calculator and the DLT first-passage calculator | mixed; each card declares its own class |
| **Measured evidence** | the observed cohort, held-out model scores, and both gate ledgers | observed + report-derived |
| **Planned, not run** | B3's nine frozen competitors and B4 robustness, all marked pending/not-run | frozen prediction |
| **Print worksheets** | twelve hand-calculation worksheets | teaching material |

---

## 4. Evidence, units and assumptions

### 4.1 Observed dwell analysis

- **Protocol:** `UNI-FLAGELLUM-OBS-001`. **Source:** Wadhwa et al. 2022 single-motor
  stator-remodeling dataset, pinned by `identities.rawSourceSha256` and
  `identities.rawSourceCommit`.
- **Species:** *Escherichia coli*. This is behavioural/kinetic evidence and is kept
  separate from the *Salmonella* and *Bacillus* structural evidence used elsewhere in the
  repository. The two are never combined into one specimen claim.
- **Experimental unit:** the **motor**. Events are not independent replicates; all
  uncertainty is motor-cluster bootstrap.
- **Cohort reconciliation** (the page shows the first number; this is the full chain):

  | quantity | value |
  |---|---|
  | source motors | 129 |
  | source events | 1349 |
  | excluded: left-truncated dwells | 129 |
  | excluded: right-censored dwells | 109 |
  | excluded: out-of-range dwells | 3 |
  | training motors / events | 80 / 793 |
  | holdout motors / events | 19 / 233 |

  80 + 19 = 99 motors carry scored events; the remaining 30 of the 129 source motors
  contribute no eligible event after exclusions.
- **Split rule:** `sha256(motorName) mod 5`, at motor granularity, recomputed
  independently by `tests/semantic/train-holdout-leakage.semantic.test.mjs`.
- **Fitting:** all parameters are estimated on training events only. One declared nuance:
  the *set of eligible states* (N = 1…8) was chosen using all data, not training only.
- **Units:** durations in seconds; log scores in **nats per event**; `μ_N` in seconds.

### 4.2 Duration models

Scored on the normalized duration `y = t/μ_N`, then mapped to seconds with the Jacobian
`log f_seconds(t) = log f_normalized(y) − log μ_N`. Each normalized model is constrained
to unit mean, so `μ_N` carries the scale and the shapes are compared on equal footing.

| model | form | frozen training parameters |
|---|---|---|
| M0 memoryless | `f(y) = e^{−y}` | none |
| M1 Weibull | scale `= 1/Γ(1+1/k)` | `k = 0.625088844276203`, `scale = 0.6996038164387606` |
| M2 lognormal | `μ_log = −σ²/2` | `σ = 1.5783076021679734`, `μ = −1.245527443530609` |
| M3 two-timescale | `w λ_f e^{−λ_f y} + (1−w) λ_s e^{−λ_s y}` | `w = 0.6066448974609373`, `λ_f = 5.239865393555934`, `λ_s = 0.44485855808292624` |

### 4.3 Held-out result, including the adverse one

Mean log score, nats per event (higher is better):

| model | score |
|---|---|
| M0 exponential | −3.259938023731547 |
| M1 Weibull | −3.0962841768378104 |
| **M2 lognormal** | **−3.012890170946554** |
| M3 UNI two-timescale | −3.0497565695441344 |

Paired advantages of M3, with motor-cluster bootstrap 95 % intervals:

| contrast | point | 95 % interval | reading |
|---|---|---|---|
| M3 − M0 | +0.210181454187411 | [0.06918462236407662, 0.3247183938187771] | resolved: M3 beats the memoryless null |
| M3 − M1 | +0.046527607293676804 | [−0.01796916498254155, 0.084962018775231] | **crosses zero — not resolved** |
| M3 − M2 | −0.03686639859758028 | [−0.06803225348050351, 0.014817954207609459] | **crosses zero — not resolved** |

**The adverse result is retained:** a lognormal baseline out-scores the UNI two-timescale
model on held-out point score. The M3 − M2 interval crosses zero, so the correct statement
is *"not resolved at this sample size"*, not *"no difference"* and not *"M2 wins"*.
With 19 holdout motors most contrasts are underpowered.

Mean CV² across states: `3.149531339591441`, 95 % interval
[1.5141240937044127, 3.5675042610575742] — above 1, so held-out dwell timing rejects the
homogeneous memoryless prediction within the frozen population.

### 4.4 Fences that apply to every reading of this page

Carried verbatim from `observedReport.claims`:

- Overdispersion **does not** uniquely identify a molecular hidden state; heterogeneity and
  nonstationarity remain alternatives.
- Predictive superiority **does not** prove that the fitted timescales are molecular states,
  that the organism performs the inference, or that any mechanism is identified.

### 4.5 Variational and expected free energy

- `F[q]` is in **nats**. It is model evidence, not mechanical work, not joules.
  Thermodynamic work `τ·Δθ` is a separate quantity with separate units and is never added
  to, converted from, or compared with `F`.
- The likelihood is normalized to a categorical evidence vector over the three declared
  hidden states before the update, so the reported "surprise" is the surprisal under a
  renormalized categorical channel, not under a continuous density.

> **Known defect, open at the time of writing.** The shipped expected free energy at
> `lib/uni-motor.js:328` evaluates to `KL[q(o)‖C] + 2·ambiguity + effort`, not the
> canonical `KL + ambiguity + effort`, because `risk` is a cross-entropy and the epistemic
> term is counted twice. On the real model this inflates `G` by ~61 % and inflates
> `G(RUN) − G(TUMBLE)` by 6.5×, which **changes action selection**. See
> [docs/audit/PHASE-E-WORKBENCH-AUDIT.md](audit/PHASE-E-WORKBENCH-AUDIT.md) finding E-M01.
> Until it is corrected, the `EFE` equation card and worksheet 5 describe a quantity the
> tool does not produce.

### 4.6 DLT first-passage module

`S_N(t) = Σ_j a_j e^{−r_j t}` with `r_j = k₊(N) + N σ₋ + j(σ₊ − σ₋)`;
`P₊(t|N) = k₊(N) S_N(t)`; `P₋(t|N) = −dS_N/dt − P₊(t|N)`. A censored dwell contributes only
its survival probability. Verified numerically in this repository: `Σ_j a_j = 1`,
`S` monotone non-increasing, `P₊ + P₋ = −dS/dt` to <1e-4 relative, and mean dwell `= ∫S dt`
to <1e-3.

> The DLT calculator executes parameters from a fit whose **parameter-recovery (G05) and
> held-out mechanistic prediction (G06) gates FAILED**, and whose public-artifact parity
> gate (G03) also FAILED. The numbers are reproducible; they are not validated mechanism.

---

## 5. Gate ledgers as rendered

**Single-study mechanistic gates** (14 total): 4 PASS, 3 FAIL, 1 SOURCE_ONLY,
1 NOT_ESTABLISHED, 5 BLOCKED_EXTERNAL.
Of the seven *computational* gates G00–G06: **4 pass (G00, G01, G02, G04), 3 fail
(G03, G05, G06)**.

**Cross-study parity gates** (16 total): 8 PASS, 3 FAIL, 2 NOT_ESTABLISHED,
3 BLOCKED_EXTERNAL. Overall `PARTIAL_PARITY_ONLY`;
`fullBiologicalParityAchieved: false`; 11 attributed studies; conservative lower bound of
409 independent motors/cells.

> **Known defect, open.** `X01_SOURCE_INTEGRITY` renders `PASS` while zero of its twelve
> declared cached artifacts are present on disk. Per `CLAUDE.md` it must be
> `BLOCKED_EXTERNAL` in a clone without `experiments/upstream-cache/`. See audit finding
> E-B01. Do not read that green badge as verified source integrity.

---

## 6. Falsifiers

The workbench itself is falsified if any of the following is shown:

1. A displayed value differs from the value produced by the named source function for the
   same inputs. *Test:* `tests/math-workbench.test.mjs`.
2. A truth badge names an evidence class the underlying quantity does not have.
   *Currently unprotected* — see audit finding E-M04.
3. A gate with status `FAIL`, `NOT_RUN`, `BLOCKED_EXTERNAL` or `NOT_ESTABLISHED` renders
   with the pass affordance. *Currently latent* — see TC-06.
4. The rendered `fullBiologicalParityAchieved` is anything but `false` while any required
   gate is unmet. *Currently guarded by a vacuous assertion* — see E-M03.
5. Two identical runs from the same controls produce different trajectories.
   *Verified deterministic:* 16,200-step sweep, bit-identical replay.

---

## 7. Reproduction

```bash
npm ci
npm test                      # 103 tests + build + 2 rendered-route tests
npm run lint
npx tsc --noEmit
npm run science:verify
npm run cross-study:verify
npm run cross-study:verify-raw   # BLOCKED without experiments/upstream-cache/ (4.09 GB)
npm audit --omit=dev --audit-level=moderate
npm audit
npm run dev -- --port 3107
```

Then open `http://localhost:3107/math-workbench`.

> **Note.** `vinext dev` binds `[::1]` (IPv6 loopback) only and does not honour `--host`.
> If your browser resolves `localhost` to `127.0.0.1` first, use
> `http://[::1]:3107/math-workbench`. The route is not reachable from another device.

The page footer's reproduction strip lists only four of these commands. `npm run lint`,
`npx tsc --noEmit`, `npm audit` and `cross-study:verify-raw` are also required by
`CLAUDE.md` and are omitted from that strip.

---

## 8. Limitations

- **No live browser verification exists in the audit record.** All product findings to date
  are static-analysis or build-output based.
- **The truth-status colour channel is currently non-functional**: `app/globals.css`
  references four CSS custom properties that are never declared, so the probability bars
  render invisible and PASS/FAIL/UNRESOLVED badges render identically (audit E-M02).
- **No species label appears anywhere on the served page** (audit TC-04), although the
  underlying report carries the *E. coli* attribution.
- **The four overclaim fences in §4.4 are not rendered** by the workbench (audit TC-05).
- **Only the default `flow` view is server-rendered**; the other five views require
  JavaScript and have no rendered-HTML test coverage (audit E-M05).
- **B3 shows `PENDING` on this branch.** Executed B3 and B4 results exist on
  `phase-2/b3-model-competition`. This branch's badge is correct for its own commit graph
  and stale with respect to the science. See audit §5.
- `npm test` covers 103 tests; `tests/red/*` is excluded by design and several of its cells
  are red at HEAD.

---

## 9. Related documents

- [docs/audit/PHASE-E-WORKBENCH-AUDIT.md](audit/PHASE-E-WORKBENCH-AUDIT.md) — the audit this
  document's warnings come from
- [docs/UNI-STACK-BUILDER-PLAN.md](UNI-STACK-BUILDER-PLAN.md) — the hierarchical builder that
  supersedes this surface
- [docs/OBSERVED-EXPERIMENT.md](OBSERVED-EXPERIMENT.md) · [docs/SCIENCE-GATES.md](SCIENCE-GATES.md) ·
  [docs/CROSS-STUDY-PARITY.md](CROSS-STUDY-PARITY.md) · [docs/VERUM.md](VERUM.md)
