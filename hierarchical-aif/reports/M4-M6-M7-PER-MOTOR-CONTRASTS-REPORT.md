# M4 / M6 / M7 Per-Motor Contrasts — closing the F-side coverage gap

**Gate:** H-AIF-G7 (extension) · **Lane:** **D** · **Date:** 2026-07-22
**Result:** `hierarchical-aif/results/motor_stack_aif/M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json`
sha256 `751a59ef45c8aecd1bdbe5fb5ef645423572a24d1691fb199d1b3b33fb8d4dbb`
**Status:** **`POST_HOC_COVERAGE_EXTENSION`** — see §2. **No P-level moves on this artifact.**

---

## 1. What this closes, and what it found

The F-side scoring report recorded a coverage gap in its own §8:

> `M4_MIXTURE_K3`, `M6_SEMI_MARKOV_STATE_DEPENDENT` and `M7_HIERARCHICAL_MOTOR` were **not**
> contrasted — only their published aggregates are available, and a paired motor-cluster bootstrap
> needs per-motor arrays. **This is a genuine coverage gap**: `M4` and `M6` both out-score the
> F-side model on point estimate and neither has been contrasted against it under a CI-bound test.

That gap is now closed. B3 stores only aggregates, so all three per-motor arrays were re-derived
from their **frozen fitted parameters** through the **frozen scoring functions** — no refitting, no
new data, no held-out mark channel.

**Headline: neither M4 nor M6 resolves against the candidate. And the M7 contrast exposed a defect
in the verdict rule itself (D10) that is more important than any of the three contrasts.**

## 2. Post-hoc status — declared, not hidden

The pre-registered F-side protocol named its competitor set in advance: `CONTROL_CURRENT` (M3) plus
`M0`/`M1`/`M2`/`M5`/`M8`. **M4, M6 and M7 were not in it.** The decision to add them was taken
*after* seeing the candidate rank 3rd of 7 there.

| what is post-hoc | what is not |
|-|-|
| The **selection** of which comparisons to run, and therefore the family size (6 → **9** contrasts) | The **numbers**. Models, fitted parameters, split, scoring rule, aggregation, bootstrap seed and interval type are all frozen. Nothing was chosen to produce a result |

A Bonferroni companion at `alpha/9` is reported as a **sensitivity**; the frozen convention decides
on the nominal 95% interval. These verdicts are **`POST_HOC_EXPLORATORY`** and do **not** carry the
standing of the six pre-registered contrasts.

## 3. Oracle gate — PASS, residual exactly `0.0` on all three

B3 stores no per-motor arrays, so an unvalidated recomputation would be worthless. The gate HALTS
the script and emits no verdict on failure.

| model | published motor-equal | recomputed | residual |
|-|-|-|-|
| `M4_MIXTURE_K3` | `3.4241154309421407` | `3.4241154309421407` | **`0.0`** |
| `M6_SEMI_MARKOV_STATE_DEPENDENT` | `3.4298889709683209` | `3.4298889709683209` | **`0.0`** |
| `M7_HIERARCHICAL_MOTOR` | `3.4326925889658892` | `3.4326925889658892` | **`0.0`** |

Two reconstructions were non-obvious and are therefore worth naming, because the gate is what
proves they were right: `M4`'s scoring dict had to be rebuilt from `canonical` (`{rates, weights}`
— the result JSON carries no `m4params` key), and `M6`'s per-state parameters arrive from JSON with
**string** keys and must be re-keyed to `int` because the frozen scorer indexes by integer state.
Either mistake would have produced plausible-looking numbers; both were caught by the exact-zero
requirement.

**Six frozen models have now been reproduced to exact zero residual** (M3, M0, M8 in the F-side run;
M4, M6, M7 here). That is a strong `P1` implementation receipt for the scoring path.

## 4. Contrasts

Convention: `contrast = S(reference) - S(F_MOTOR_STACK)`; above 0 ⇒ candidate better.

| reference | point (nats) | 95% percentile interval | frozen verdict | Bonferroni (α/9) | **scientific reading** |
|-|-|-|-|-|-|
| `M4_MIXTURE_K3` | `-8.577e-03` | `[-7.115e-02, +5.540e-02]` | `NOT_ESTABLISHED` | `NOT_ESTABLISHED` | `SUB_FLOOR_EFFECT` |
| `M6_SEMI_MARKOV_STATE_DEPENDENT` | `-2.803e-03` | `[-1.899e-02, +1.391e-02]` | `NOT_ESTABLISHED` | `NOT_ESTABLISHED` | `SCIENTIFICALLY_NULL` |
| `M7_HIERARCHICAL_MOTOR` | `+2.507e-07` | `[+1.604e-07, +3.375e-07]` | **`RESOLVED_ABOVE`** | `RESOLVED_ABOVE` | **`SCIENTIFICALLY_NULL` ⚠** |

**M4 and M6 lead on point estimate but neither resolves.** The gap the F-side report flagged is
closed with a null: at 19 holdout motors these differences are not resolvable. `NOT_ESTABLISHED` is
**not** equivalence.

**M6's entire interval lies inside ±0.042 nats.** No scientifically material difference is
detectable in either direction. That is a stronger statement than a bare `NOT_ESTABLISHED` — but it
is **not** a formal equivalence result, because the floor is a heuristic derived from the narrowest
frozen B3 contrast and was never pre-specified as an equivalence margin. A test enforces that no
equivalence language attaches to it.

**Combined leaderboard: the candidate ranks 5th of 10.**

## 5. D10 — the verdict rule has no minimum effect size

**This is the real finding, and it is adverse to the methodology, not to any model.**

The `M7` contrast was **resolved** by the frozen rule: the interval `[+1.60e-07, +3.37e-07]`
genuinely excludes 0. But the effect is `2.507e-07` nats — about **168 000× below** the 0.042-nat
resolution floor.

Root cause, verified from first principles by test: a paired motor-cluster bootstrap resamples
**motors**, so it resolves a difference of **any magnitude** provided the sign is **consistent**
across them. Here 16 of 19 per-motor differences were positive with a mean of `+2.5e-07`, because
the F-side hierarchy **is** `M7` to numerical precision — the same model reached by a different
quadrature (33-node Gauss-Hermite vs M7's own), differing only in float noise.

Reporting that as "the F-side candidate beats `M7`" would be **truth laundering**: a numerically
identical model presented as a winner on the strength of consistent float noise.

**Handling.** The frozen verdict is reported **verbatim and unaltered** — it is not softened,
suppressed, or re-thresholded. Every contrast now additionally carries a `scientificReading`
(`MATERIAL` / `SUB_FLOOR_EFFECT` / `SCIENTIFICALLY_NULL`) and a `reportableAsAWin` flag which is
false whenever a resolved verdict sits below the floor. This changes **no** frozen threshold,
criterion, or interval.

**This also explains the recorded miss in the F-side prediction scorecard.** Item 6 predicted
`M5_GAMMA` would be `NOT_ESTABLISHED` because its `+0.031` effect sits below the ~0.042 floor; it
resolved instead. Same mechanism, milder form: the floor is about **consistency**, not magnitude.
D10 supersedes the "resolution floor" as a predictor of what will resolve — the floor tells you
what is *scientifically material*, not what the bootstrap will *call*.

## 6. What this does not establish

- **No mechanism, no biological parity, no active-inference claim.** Duration-only, one cohort, 19
  holdout motors.
- **No P-level moves.** These contrasts are post-hoc and exploratory.
- **The candidate did not beat anything here.** Two nulls and one artifact.
- **`M7` is not displaced**, and the F-side model is not shown superior to it — the two are the
  same model at this resolution, which was already the headline of the F-side report.
- The retained adverse finding stands: `M2_LOGNORMAL` (`3.4093`) and `M8_EMPIRICAL_KDE` (`3.4225`)
  still lead the candidate (`3.4327`) on point estimate.

## 7. Limitations

- **Post-hoc selection**, family size 9, Bonferroni companion reported (no contrast's verdict
  changed under it).
- **Percentile intervals**, not BCa. The frozen B3 verdicts used BCa (`intervalUsed`); every
  half-width here is labelled percentile (D7).
- **19 holdout motors.** The binding constraint throughout.
- The `SCIENTIFICALLY_NULL` classification uses a **heuristic** floor, not a pre-specified
  equivalence margin.
- `M7`'s parameters (`k = 0.6596322379287862`, `tau = 0.18372185667134974`) versus the F-side fit
  (`exp(mu) = 0.6596326697…`, `tau = 0.18372082607…`) differ in the 6th–7th significant figure.
  The contrast is measuring that, and nothing else.

---

`NEXT_ACT = python -m pytest hierarchical-aif/tests/motor_stack_aif -q && watch PID 26756 (B4C11) and PID 32988 (B4C01) to completion`
