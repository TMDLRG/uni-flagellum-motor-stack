# POWER ATLAS — MOTOR-EQUAL SCORING (PROBE 2)

<!-- prov: 0.03952847075210474 = power_atlas.json#cells.108.resolveRateMonteCarloSE -->
<!-- prov: 0.0800 = power_atlas.json#d10Counterfactual.meanCIHalfWidthNats -->
<!-- prov: 0.0876 = RECOMPUTED by scripts/power_atlas.py (max |resolveRate - analyticResolveRate| over cells) -->
<!-- prov: 0.0169 = RECOMPUTED by scripts/power_atlas.py (mean |resolveRate - analyticResolveRate| over cells) -->

**Status:** BUILDER-SUPPORT PROBE. Moves no P-level, changes no frozen verdict, creates no claim.
It answers one design question: *at the current motor count and scoring rule, what effect sizes can
this design actually resolve, and what would make the assay severe?*

**Truth label.** Every resolve-rate, CI width and power number in the ATLAS section is **SYNTHETIC**
— produced by simulating per-motor NLPD arrays with a known injected effect and running the frozen
paired motor-cluster bootstrap on them. Nothing here is `OBSERVED`. The only recorded quantities
are the calibration constants and the real anchors, each carrying its source artifact inline.

- Artifact: `hierarchical-aif/results/motor_stack_aif/power_atlas.json`
  (sha256 `66311a07866b916c77a44faab4bc22688db1e4e7fd6438bce77b1ba8ffe8976b`, 162654 bytes)
- Generator: `hierarchical-aif/scripts/power_atlas.py`
- Reproduce: `cd hierarchical-aif && python scripts/power_atlas.py`
- Runtime: 89.5 s, single process, 200 grid cells + 2 special cells.

---

## 0. Prediction and falsifier, recorded before the sweep ran

> **Label note.** These atlas predictions are numbered `A1`–`A4`. They are **not** parity-ladder
> levels. `P0`–`P8` in this document always mean the frozen ladder defined in `CLAUDE.md`, which
> this probe does not touch and cannot move.

| # | Prediction | Falsifier | Outcome |
|---|---|---|---|
| A1 | At effect 0 the frozen 95% rule falsely resolves ≈0.05 of repetitions | pooled false-resolve materially above 0.05 => the assay is anti-conservative | **PARTIALLY FALSIFIED** — 0.0730 ± 0.0082 at 19 motors, +0.0230 over nominal (≈2.8 Monte-Carlo SE) |
| A2 | At 19 motors and consistency typical of the real contrasts, a 0.042-nat effect is **not** reliably resolvable | resolve-rate at effect 0.042, n=19 exceeding 0.80 | **HELD** — 0.110 / 0.170 / 0.325 at rho 0.90 / 0.97 / 0.99 |
| A3 | A microscopic effect resolves at ~100% when per-motor differences are near-degenerate (D10) | D10 cell resolve-rate near the null rate | **HELD** — 1.0000 at effect 2.507e-07 nats |
| A4 | The bootstrap tracks an independent normal-approximation power expression | max divergence over 200 cells exceeding Monte-Carlo error by a wide margin | **HELD** — max |empirical − analytic| = 0.0876, mean 0.0169 |

---

## 1. Method (what was and was not computed)

No model was refit. The atlas isolates the scoring rule from the modelling by construction:

```
challenger_i = mu0 + sigma_b * z1_i
ref_i        = challenger_i + effect + sigma_d * z2_i          i = 1..n_motors
contrast     = S(ref) - S(challenger)        # frozen convention
```

then `motor_stack_aif.score.contrast_with_ci(ref, challenger, n_rep=2000)` — the **frozen**
implementation, resampling unit MOTOR, percentile interval — is run on each synthetic pair.

This is exact rather than approximate: the paired motor-cluster bootstrap statistic is
`mean(d[idx])`, a function of the per-motor **difference** array alone. The score levels never
enter the statistic. That is why one Gaussian difference generator covers every model family:
a family enters the atlas only through the pair `(effect, sigma_d)`, and the real `(effect, sigma_d)`
of all nine recorded comparisons are tabulated in §3.

**Consistency axis.** `rho` is the equal-marginal correlation between the two per-motor score
arrays, so `sigma_d = sigma_b * sqrt(2 - 2*rho)`. The recorded contrasts live in
rho ∈ [0.9674, 0.99999999999998], which is what the grid spans.

**Independent cross-check.** Every cell also carries a normal-approximation power value computed
by a routine that shares no code with the bootstrap (`analytic_resolve_rate`). Max divergence over
200 cells: **0.0876** (worst cell n=100, effect 0.02, rho 0.99, 120 sims; that cell's recorded
`resolveRateMonteCarloSE` is **0.03952847075210474**); mean
**0.0169**.

**Determinism.** Two full executions, canonical JSON bytes compared with `generatedUtc` and
`runtimeSeconds` excluded (both are volatile by design): **identical**, canonical sha256
`0816896e16ed8c67d48229652df35a3e1e258945308acea014e389b194311bad` on both runs. Byte-identity of
the raw file is *not* claimed, because the file embeds a timestamp and a wall-clock runtime.

### Calibration constants — recorded, not invented

| Constant | Value | Source |
|---|---|---|
| `sigma_b` across-motor SD of per-motor NLPD (ddof=1) | **0.9182141349** | `std(perMotorNLPD.F_MOTOR_STACK)` in `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` |
| `mu0` | 3.4326923382675303 | `candidate.motorEqual`, same artifact |
| holdout motors | 19 | frozen cohort `derived_eligible_1_to_8` |
| holdout events | 233 | frozen cohort |
| events per motor | min 3, median 7, max 50, mean 12.2632 | `_bridge.frozen_cohort().holdout_by_motor` |
| resolution floor | 0.042 nats half-width | FROZEN (BCa half-width of the narrowest frozen B3 contrast, M4_MIXTURE_K3) |
| power target 0.80 | **`DESIGN_ONLY`** | introduced here for sizing; **not evidential**, no verdict may cite it |

### Axes not swept

| Axis | Status |
|---|---|
| events per motor | `NOT_SWEPT` — held at the observed holdout allocation. Sweeping it requires refitting every model family on subsampled per-motor event sets: `NOT_RUN — COMPUTE_BUDGET` (two long runs in flight; this probe is fenced to ~2 minutes). |
| model family | `NOT_SWEPT` — generator-agnostic by construction (see §1); the nine real families appear as anchors in §3. |
| non-Gaussian per-motor difference shapes | `NOT_RUN — COMPUTE_BUDGET`, and a shape fitted to 19 points would be an invented assumption. |
| BCa intervals | `NOT_COMPUTED` — D7: BCa companions exist only for the 48 frozen B3 contrasts. Computing one here would fabricate a comparison with no frozen counterpart. |
| motor counts above 200 | grid capped at 200; larger requirements are reported as **analytic only**, labelled as such. |

---

## 2. The atlas at 19 motors — the actual design

Resolve-rate over synthetic repetitions (200 per cell, Monte-Carlo SE ≤ 0.036).
Analytic cross-check in parentheses.

| rho | `sigma_d` | e=0 | 1e-06 | 0.005 | 0.01 | 0.02 | **0.042** | 0.08 | 0.15 |
|---|---|---|---|---|---|---|---|---|---|
| 0.90 | 0.41064 | 0.060 (0.050) | 0.115 (0.050) | 0.085 (0.050) | 0.095 (0.051) | 0.090 (0.055) | **0.110** (0.073) | 0.215 (0.136) | 0.380 (0.357) |
| 0.97 | 0.22492 | 0.085 (0.050) | 0.035 (0.050) | 0.070 (0.051) | 0.080 (0.054) | 0.105 (0.067) | **0.170** (0.129) | 0.365 (0.341) | 0.830 (0.828) |
| 0.99 | 0.12986 | 0.100 (0.050) | 0.075 (0.050) | 0.070 (0.053) | 0.105 (0.063) | 0.135 (0.103) | **0.325** (0.291) | 0.785 (0.766) | 1.000 (0.999) |
| 0.999 | 0.04106 | 0.055 (0.050) | 0.075 (0.050) | 0.080 (0.083) | 0.240 (0.186) | 0.605 (0.565) | **1.000** (0.994) | 1.000 (1.000) | 1.000 (1.000) |
| 0.9999 | 0.01299 | 0.065 (0.050) | 0.070 (0.050) | 0.430 (0.389) | 0.910 (0.919) | 1.000 (1.000) | **1.000** (1.000) | 1.000 (1.000) | 1.000 (1.000) |

Materiality of each column, against the frozen floor, is fixed and independent of the table:
`0` = `NULL_NEGATIVE_CONTROL` · `1e-06`, `0.005`, `0.01`, `0.02` = `IMMATERIAL_BELOW_FROZEN_FLOOR` ·
`0.042`, `0.08`, `0.15` = `MATERIAL_AT_OR_ABOVE_FROZEN_FLOOR`.

### Detectable effect size at 19 motors (80% target — `DESIGN_ONLY`)

| rho | `sigma_d` | empirical MDE80 (grid-interpolated) | analytic MDE80 | above frozen floor? |
|---|---|---|---|---|
| 0.90 | 0.41064 | `NOT_COMPUTED` — above grid max 0.15 | 0.263928 | yes |
| 0.97 | 0.22492 | 0.14548387096774196 | 0.144559 | yes |
| 0.99 | 0.12986 | 0.08488372093023257 | 0.083461 | yes |
| 0.999 | 0.04106 | 0.03086075949367089 | 0.026393 | no |
| 0.9999 | 0.01299 | 0.008854166666666666 | 0.008346 | no |

### Motors needed to resolve a 0.042-nat effect at 80% (`DESIGN_ONLY`)

| rho | empirical (grid-interpolated) | analytic |
|---|---|---|
| 0.90 | `NOT_COMPUTED` — above grid max 200 motors | 750.29 |
| 0.97 | `NOT_COMPUTED` — above grid max 200 motors | 225.09 |
| 0.99 | 85.79545454545456 | 75.03 |
| 0.999 | 19.0 (already satisfied at the actual motor count) | 7.50 |
| 0.9999 | 19.0 (already satisfied at the actual motor count) | 0.75 |

Resolve-rate at the frozen-floor effect across the motor-count axis:

| rho | n=19 | n=30 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|
| 0.90 | 0.110 | 0.165 | 0.130 | 0.217 | 0.317 |
| 0.97 | 0.170 | 0.210 | 0.260 | 0.542 | 0.750 |
| 0.99 | 0.325 | 0.485 | 0.590 | 0.883 | 1.000 |
| 0.999 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| 0.9999 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Mean CI **half-width** (nats) in the same cells — this is what the 0.042 floor should be compared to:

| rho | n=19 | n=30 | n=50 | n=100 | n=200 |
|---|---|---|---|---|---|
| 0.90 | 0.17772 | 0.14039 | 0.11091 | 0.07945 | 0.05608 |
| 0.97 | 0.09413 | 0.07751 | 0.06152 | 0.04298 | 0.03104 |
| 0.99 | 0.05546 | 0.04525 | 0.03545 | 0.02535 | 0.01787 |
| 0.999 | 0.01770 | 0.01419 | 0.01111 | 0.00790 | 0.00567 |
| 0.9999 | 0.00566 | 0.00448 | 0.00355 | 0.00249 | 0.00180 |

---

## 3. Real anchors — where the recorded comparisons actually sit

All values below are **recorded**, read from `perMotorNLPD` arrays in
`F_SIDE_MOTOR_STACK_SCORING_RESULT.json` and `M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json`
(the `F_MOTOR_STACK` array agrees between the two files to max |diff| = 0.000e+00).
Sizing columns are analytic, at n=19, 80% `DESIGN_ONLY`.

| reference | recorded mean diff (nats) | recorded `sigma_d` | Pearson rho | +ve motors | analytic MDE80 @19 | analytic n for 0.042 |
|---|---|---|---|---|---|---|
| M0_EXPONENTIAL | +0.1152909428 | 0.2469900535 | 0.9674154175 | 12/19 | 0.158747 | 271.44 |
| M2_LOGNORMAL | −0.0233781800 | 0.1991732001 | 0.9951826731 | 8/19 | 0.128014 | 176.51 |
| M3_TWO_TIMESCALE (control) | +0.0016409948 | 0.1883138585 | 0.9869331362 | 10/19 | 0.121035 | 157.79 |
| M8_EMPIRICAL_KDE | −0.0101687199 | 0.1784560652 | 0.9910073160 | 10/19 | 0.114699 | 141.70 |
| M4_MIXTURE_K3 | −0.0085769073 | 0.1516825015 | 0.9940733445 | 11/19 | 0.097491 | 102.37 |
| M5_GAMMA | +0.0310363114 | 0.0579256911 | 0.9985105153 | 16/19 | 0.037230 | 14.93 |
| M6_SEMI_MARKOV | −0.0028033673 | 0.0405122451 | 0.9993226774 | 6/19 | 0.026038 | 7.30 |
| M1_WEIBULL | +0.0006145101 | 0.0258832745 | 0.9996485647 | 10/19 | 0.016636 | 2.98 |
| M7_HIERARCHICAL_MOTOR | +2.5069835852e-07 | 2.0416535512e-07 | 0.9999999999999771 | 16/19 | 0.000000 | 0.00 |

Recorded percentile **half-widths** at 19 motors, same artifact: M0 0.1072286 · M2 0.0859624 ·
M3 0.0789979 · M8 0.0744904 · M5 0.0250071 · M1 0.0110923. The frozen 0.042 floor is the
**narrowest** frozen B3 contrast, not a typical one — real half-widths at this motor count span
roughly 0.011 to 0.107.

### The load-bearing split in that table

The nine anchors fall into two disjoint regimes, and the atlas says they demand opposite things.

- **Serious adversaries** (M0, M2, M3, M8, M4): `sigma_d` ≈ 0.15–0.25. Analytic MDE80 at 19 motors
  is **0.097 to 0.159 nats — 2.3x to 3.8x the frozen 0.042 floor**. At the actual motor count this
  design cannot reliably resolve even a *material* difference against the models it most needs to
  beat. Required motor counts to reach the floor at 80%: **102 to 271**.
- **Near-duplicates of the candidate** (M1, M6, M7): `sigma_d` ≈ 2e-07 to 0.026. These resolve
  easily — and every effect they could resolve is far below the floor. This is the D10 zone.

---

## 4. Resolve-rate and materiality are separate axes (D10, demonstrated)

Two synthetic cells, both at 19 motors, both with the **same** injected effect
2.506984e-07 nats — approximately 168 000x below the frozen floor. Only the per-motor difference
dispersion differs, and both dispersions are taken from recorded arrays.

| cell | injected effect | `sigma_d` (source) | resolve-rate | mean CI half-width | materiality |
|---|---|---|---|---|---|
| D10 demonstration | 2.506984e-07 | 2.041654e-07 (recorded M7 − candidate) | **1.0000** (analytic 0.9997) | 8.708e-08 | `IMMATERIAL_BELOW_FROZEN_FLOOR` |
| D10 counterfactual | 2.506984e-07 | 1.883139e-01 (recorded M3 − candidate) | 0.0850 | 0.0800 | `IMMATERIAL_BELOW_FROZEN_FLOOR` |

Same magnitude; resolve-rate 1.0000 versus 0.0850. **Consistency, not magnitude, is what the paired
motor-cluster bootstrap responds to.** A design that resolves at 100% can be resolving something of
no scientific size at all, so this atlas reports resolve-rate and materiality as two independent
columns everywhere. They are not the same question, and a report that collapses them will present
an immaterial difference as a finding.

These cells are SYNTHETIC. They are calibrated to the recorded M7/M3 numbers so the regime is the
real one, but they are not a reproduction of the recorded M7 contrast and must not be cited as one.

The **point-estimate direction** (`pointFavorsChallengerFrac`, the self-win analogue) is recorded
per cell alongside resolve-rate. At 19 motors, effect 0.02 it runs 0.580 / 0.675 / 0.675 / 0.985 /
1.000 across the rho grid while resolve-rate runs 0.090 / 0.105 / 0.135 / 0.605 / 1.000 — a modal
win fraction can be near 1 while the CI-bound verdict remains `NOT_ESTABLISHED`. A point estimate
is never a verdict.

---

## 5. Adverse finding — the assay is anti-conservative at 19 motors

Negative control (injected effect exactly 0; the frozen alpha is 0.05), pooled over the rho grid:

| n motors | false-resolve rate | Monte-Carlo SE | excess over nominal 0.05 | sims |
|---|---|---|---|---|
| **19** | **0.0730** | 0.0082 | **+0.0230** | 1000 |
| 30 | 0.0550 | 0.0072 | +0.0050 | 1000 |
| 50 | 0.0590 | 0.0075 | +0.0090 | 1000 |
| 100 | 0.0350 | 0.0075 | −0.0150 | 600 |
| 200 | 0.0617 | 0.0098 | +0.0117 | 600 |

At the actual motor count the frozen percentile motor-cluster bootstrap falsely resolved 7.30% of
synthetic null repetitions against a nominal 5%, about 2.8 Monte-Carlo SE above nominal. This is a
property of the percentile bootstrap at 19 clusters, measured on SYNTHETIC Gaussian data.

Scope and limits of this finding, stated precisely:

- It is **not** evidence that any recorded verdict is wrong. It is a design diagnostic.
- It does **not** apply to the 48 frozen B3 contrasts as a criticism of *their* interval choice:
  those used BCa, which exists precisely to correct percentile bias, and per D7 `intervalUsed` was
  `bca` in 48/48. The F-side contrasts, the M4/M6/M7 extension, and this atlas are **percentile
  only**; their BCa companions are `NOT_COMPUTED`.
- It is measured under a Gaussian per-motor difference generator. Under the real, unknown
  difference distribution the excess is `NOT_MEASURED`.

---

## 6. Executive summary — better model math, or more/different data?

**Answer from the atlas: more and different DATA — specifically more motors, and a second study.
Model math alone cannot make this assay severe.**

The reasoning is three recorded numbers plus one atlas column.

1. The entire frozen B3 leaderboard spans **0.1386691245 nats** across all nine models, and the
   **top seven span 0.0250191765 nats** — *below* the frozen 0.042 floor. Seven of nine models are
   mutually immaterial by the project's own materiality standard before any power question is asked.
2. Against the serious adversaries the recorded per-motor difference dispersion is `sigma_d` ≈
   0.15–0.25 (§3). To resolve the top-seven spread of 0.0250191765 nats at 80% (`DESIGN_ONLY`) the
   analytic motor requirement is **288.5 (vs M4) · 399.3 (vs M8) · 444.7 (vs M3) · 497.4 (vs M2) ·
   764.9 (vs M0)** — against **19** available.
3. For a 0.042-nat effect to be resolvable at 80% with the 19 motors that exist, the per-motor
   difference SD would have to be **≤ 0.065346**. The recorded values against M2/M3/M8/M4 are
   0.1992 / 0.1883 / 0.1785 / 0.1517 — a **2.32x to 3.05x** reduction in per-motor difference
   dispersion would be required.
4. Better math that reduces `sigma_d` against **near-duplicates** buys nothing: that is exactly the
   D10 zone, where the design resolves effects ~1e-07 nats that no one should report as a win
   (§4). The recorded M7 anchor is the existence proof.

So the binding constraint is the number of experimental units and the narrowness of the channel,
not the sophistication of the density model. A model improvement of 0.02 nats — larger than six of
the eight recorded contrasts — is unresolvable at 19 motors against every serious adversary, and
would be immaterial even if it resolved.

**What would make the assay severe.** Severity requires that the design be *able* to reject.
Ranked by how much it moves the atlas:

- **More motors.** The only lever that moves the serious comparisons. ~100 motors buys 0.883
  resolve-rate at the floor for rho 0.99; ~200 buys 1.000 at rho 0.99 and 0.750 at rho 0.97; the
  rho 0.90 regime stays out of reach at 200 (0.317). Transfer to a second independent study
  (the `P4` level, which no modelling in this repository can close) supplies both motors and the
  study axis at once.
- **A channel where candidate models genuinely disagree.** All nine models compress into 0.139
  nats on the duration channel; the mark channel is where they would separate, and it is
  quarantined under D5. `intervention required` / `transfer required` is the honest status.
- **Pre-declared minimum material effect, reported with power at that effect.** The floor exists;
  what is missing from the reporting surface is the power *at* it. The columns in §2 supply that.
- **Report resolve-rate and materiality as separate columns everywhere.** Already the D10 repair
  by added interpretation; this atlas quantifies why it is load-bearing.
- Reducing the percentile bootstrap's small-n anti-conservatism (§5) improves calibration but does
  **not** improve severity — a better-calibrated interval at 19 motors is still ~2.5x too wide for
  the comparisons that matter.

**Which cells would change this answer.** The conclusion is not unconditional. It flips if:

- Any new candidate shows recorded `sigma_d ≤ 0.065346` against **M2, M3 or M8** (not against a
  near-duplicate) while its mean difference stays at or above 0.042 — then 19 motors would suffice
  and the answer becomes *better math*. Cell to check: §3 columns 3 and 6 for the new model.
- The real per-motor difference distribution is far from Gaussian in a way that shrinks the
  bootstrap width — `NOT_MEASURED` here, and the shape is unidentifiable from 19 points.
- The events-per-motor axis turns out to dominate `sigma_d` — `NOT_RUN — COMPUTE_BUDGET`; would
  require refitting each family on subsampled event sets. If halving events per motor barely moved
  `sigma_d`, more events per motor would be confirmed as the wrong lever and motors the right one;
  if it moved `sigma_d` steeply, longer recordings per motor become competitive with more motors.
- Rows at n between 200 and ~500 motors: the atlas grid stops at 200, so the rho 0.90 and 0.97
  requirements are analytic extrapolations, not simulated. Simulating them would confirm or refute
  the 225–765 motor figures.

**What this probe does not do.** It establishes nothing about biology, mechanism, or any model's
correctness. It moves no P-level; the first unsatisfied level remains `P4` transfer, unchanged by
this probe. `P6` for duration-only B3/B4 is unchanged; `P6` for C11 U4 remains withdrawn pending
the corrected run. No frozen verdict is touched. Every synthetic number here would be worthless as
evidence about the motor and is offered only as evidence about the *instrument*.

---

NEXT_ACT = Extend the atlas grid to n_motors in {300, 500} for rho in {0.90, 0.97} at the frozen-floor effect to replace the analytic 225.09 / 750.29 motor requirements with simulated resolve-rates, and run it only after B4C11 (PID 26756) and B4C01 (PID 32988) have both landed, so the compute fence is clear.
