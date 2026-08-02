# CENSORING STRESS DISCRIMINATOR — PROBE 6

**Type:** BUILDER-SUPPORT PROBE. Not a verdict. Moves no P-level, changes no frozen verdict,
creates no claim.
**Date:** 2026-07-22 · **Repo HEAD at probe time:** `28ce738`
**Lane:** D (motor-stack AIF) with a bounded read into lane A (duration-only B3/B4).
**Split boundary:** `duration_only`. No held-out `nextStateN`, `direction` or `jump` was read,
loaded, printed or reasoned from. The D5 firewall was not approached.
**Experimental unit:** the MOTOR. All held-out scores are motor-equal.
**Compute:** three short single-process runs, 2.4 s + 14.5 s + 11.4 s wall. No parallel compute.
No write to `results/`. No write under `audits/`.

---

## 0. The central fact this probe is built around

The frozen B3 cohort **excludes right-censored events entirely**. The rule is one line:

```
audits/phase-b/b3-model-competition-runner.py:109-110
        elig = [e for e in events
                if (not e["rightCensored"]) and e["stateN"] in self.states]
```

Consequences that govern everything below:

1. The F-side motor stack's censoring branch
   (`hazard_survival.log_event_density`: uncensored `log h + log S`, censored `log S`) is
   **correct-by-test but UNEXERCISED on the frozen cohort.** Every event it has ever scored had
   `rightCensored = False`. Its censoring correctness has therefore contributed **zero** to the
   F-side held-out result.
2. Therefore **no censoring comparison in this probe can be run on the real cohort.** Sections 2
   and 3 are SYNTHETIC with a KNOWN generating shape. Section 1 is the only OBSERVED section, and
   it reports the *consequence of the exclusion*, not a censoring comparison.

The two are labelled sharply throughout: **[OBSERVED]** vs **[SYNTHETIC]**.

---

## 1. [OBSERVED] What the exclusion removes from the real ingest

Source: Wadhwa 2022 *E. coli* ingest via `_bridge.b3().load_events()` — the duration channel only.
These are recorded measurements. Reproduction commands in §7.

| Quantity | Value |
| --- | --- |
| Raw ingest events (all states 0–11) | **1349** |
| `rightCensored = true` in raw ingest | **109** (8.0801% of 1349) |
| `rightCensored = false` | 1240 |
| Distinct motors in raw ingest | **109** |
| Motors carrying ≥1 censored event | **109** (all of them) |
| Censored events per motor | min **1**, max **1** — exactly one per motor |
| Motors whose events are *all* censored | **5** |
| Censored events in states 1–8 (the cohort's state domain) | **54** of 1080 in-band events = **5.0000%** |
| Censored events outside states 1–8 | **55** |
| Frozen cohort survivors | 793 train + 233 holdout events; 80 train + 19 holdout motors |
| Raw motors → cohort motors | 109 → **99** |

Censored-event state distribution (raw): `{4:1, 5:3, 6:5, 7:17, 8:28, 9:29, 10:19, 11:7}` —
**zero** censored events in states 0, 1, 2, 3.

**The censored events are the long ones.**

| Duration statistic (seconds) | censored | uncensored |
| --- | --- | --- |
| median | **89.260000** | **3.250000** |
| mean | **123.286239** | **15.688484** |
| max | 357.180000 | 307.500000 |

**Within-motor position of the censored dwell** (104 motors with ≥1 uncensored event):

- **48 of 104 motors (46.1538%)** have their censored dwell longer than **every** uncensored dwell
  they contribute.
- Mean within-motor quantile rank of the censored dwell among that motor's uncensored dwells:
  **0.802900165**.

**Removed dwell-time mass:**

- All states: censored 13438.2000 s vs uncensored 19453.7200 s → **40.8556%** of recorded
  dwell-time sits in censored events.
- States 1–8 only: censored 6240.6800 s vs uncensored 12775.3200 s → **32.8180%** of in-band
  recorded dwell-time is removed by the exclusion.

**Reading (fact, not inference).** The frozen filter drops 5.0% of in-band *events* but 32.8% of
in-band *dwell-time*, and it does so non-randomly: it removes each motor's terminal dwell, which is
the longest observation that motor supplies in 46% of cases. The frozen cohort is a
**tail-depleted subpopulation**, and every model on the B3 leaderboard was fitted and scored on
that subpopulation.

---

## 2. [SYNTHETIC] Design of the censoring stress

A world where the truth is known, built to resemble the cohort without being it.

| Element | Value | Provenance |
| --- | --- | --- |
| Generating family | mean-one Weibull on normalised `y`, single shared shape | matches `hazard_survival` |
| `k_true` | **0.625088844276203** | frozen B3 `PUBLISHED["M1_shape"]` — real anchor |
| Per-state scale (seconds) | frozen `scale_N`, 3.4826…→24.5206… | frozen cohort constant |
| State frequencies | empirical raw-ingest frequencies over states 1–8 | measured, not invented |
| Train | 80 motors × 10 events = 800 | sized to the real 80 motors / 793 events |
| Held-out | 300 motors × 10 events = 3000, **fully observed** | deliberately large: keeps the score precise |
| Replicates | **R = 40** | |
| Seed | 20260722, drawn once | |
| Observation window `W` | **60.0 s** and **20.0 s** | **`DESIGN_ONLY`** — not evidential |
| Upper-tail trim | top **5%** by rank | **`DESIGN_ONLY`** — not evidential |

**Matched oracle.** Every replicate also fits the *same draw* with no censoring at the true scale.
All treatment effects are reported as differences against that matched oracle (`dk`, `dsigma`,
`dNLPD`), so the shared sampling fluctuation is differenced out. Oracle performance:

- `k_hat` = **0.626741** (sd 0.014650, se 0.002316); bias vs `k_true` = **+0.001652**.
- `sigma_hat` (mean-one lognormal, B3 M2 form) = **1.793632** (sd 0.041098).
- Held-out motor-equal NLPD in **seconds** = Weibull **3.122483**, lognormal **3.247492**;
  gap (lognormal − Weibull) = **+0.125009** (se 0.001874). Positive = the true family wins.

**Two normalisation modes, because normalisation is a second censoring handle.**

- **Mode A `SCALE_TRUE`** — normalise by the true `scale_N`. Isolates the *likelihood* treatment.
  Counterfactual; no pipeline does this.
- **Mode B `SCALE_FROZEN_RULE`** — per-state scale = mean duration of **uncensored events only**,
  which is exactly `Cohort.scale_N` at lines 115–120. **This is what the real pipeline does**,
  regardless of which likelihood is used afterwards.

All held-out NLPD is reported in **seconds** (B3 convention: normalised-`y` NLPD + `log scale`), so
scores remain comparable across treatments that disagree about the scale.

**Five stress treatments.** T1 correct survival likelihood · T2 drop censored · T3 treat censored
as completed events · T4 upper-tail trim · T5 state-specific censor sensitivity (§3.4).

**Realised censoring rates** (mean over 40 replicates): W=60 → **0.043375** (sd 0.006865);
W=20 → **0.173250** (sd 0.014765).

**Window calibration against the real cohort — this decides which row to read.**

| | event fraction censored | true dwell-**time** fraction in censored events |
| --- | --- | --- |
| REAL, states 1–8 | **0.050000** | **0.328180** |
| SYNTH W = 60 s | 0.043698 | **0.362572** |
| SYNTH W = 20 s | 0.174755 | 0.707841 |

**W = 60 s is the row that resembles the real cohort**, on both event rate and removed time mass.
W = 20 s is a deliberate over-stress, roughly four times the real exposure.

---

## 3. [SYNTHETIC] Results

`dk` = shape minus matched oracle shape. **`dk` negative = apparently HEAVIER tail.**
`dsigma` = lognormal sigma minus oracle sigma. **`dsigma` positive = apparently HEAVIER tail.**
`dNLPD_s` = held-out motor-equal seconds-NLPD penalty vs the oracle, on the **full** population.
All values are means over R = 40; `se` is the standard error over replicates.

### 3.1 Mode A — likelihood treatment only, true scale held fixed

| Window | Treatment | n used | `dk` (se) | `dsigma` (se) | `dNLPD_s` |
| --- | --- | --- | --- | --- | --- |
| **W=60** (real-like) | T1 correct survival | 800 | **−0.000068** (0.000707) | +0.006501 (0.000258) | **+0.000088** |
| W=60 | T2 drop censored | 765 | +0.011479 (0.000762) | +0.014076 (0.000477) | +0.000589 |
| W=60 | T3 censored-as-events | 800 | +0.020149 (0.000806) | −0.006743 (0.000245) | +0.001313 |
| W=60 | T4 trim upper 5% | 760 | +0.010311 (0.000836) | +0.017289 (0.000316) | +0.000499 |
| **W=20** (over-stress) | T1 correct survival | 800 | **+0.000244** (0.000852) | +0.014472 (0.000349) | **+0.000023** |
| W=20 | T2 drop censored | 661 | **−0.032968** (0.001092) | **+0.093467** (0.001659) | +0.002000 |
| W=20 | T3 censored-as-events | 800 | **+0.046985** (0.001216) | −0.020617 (0.000424) | +0.005703 |
| W=20 | T4 trim upper 5% | 760 | +0.024584 (0.001184) | +0.009592 (0.000455) | +0.001887 |

**Findings.**

1. **T1 recovers the truth.** At both windows the correct survival likelihood is statistically
   indistinguishable from the matched no-censoring oracle: `dk` = −0.000068 (se 0.000707) and
   +0.000244 (se 0.000852), both intervals containing 0. The censoring branch does what it is
   documented to do.
2. **Direction of induced error is NOT fixed.** T2 (drop) moves the shape *up* at 4.3% censoring
   (+0.011479, lighter tail) and *down* at 17.3% censoring (−0.032968, heavier tail), with the
   lognormal sigma inflated by **+0.093467**. T3 (censored-as-events) moves the shape *up* at both
   rates. So "mistreating censoring manufactures a heavy tail" is **regime-dependent, not a rule**.
3. **At the real-like exposure the likelihood handle alone is immaterial.** Every W=60 Mode A
   `dNLPD_s` is ≤ **+0.001313** nats — roughly **32×** below the corrected motor-equal resolution
   floor of ≈0.042 nats. On the frozen cohort's censoring exposure, getting the censoring
   *likelihood* wrong would not be detectable by the frozen CI machinery.

### 3.2 Mode B — the frozen normalisation rule. This is where the cost lives.

| Window | Treatment | `dk` (se) | `dsigma` (se) | `dNLPD_s` |
| --- | --- | --- | --- | --- |
| **W=60** | T1 correct survival | +0.015331 (0.000961) | −0.064000 (0.002383) | **+0.035502** |
| W=60 | T2 drop censored | +0.052330 (0.001289) | −0.067306 (0.002670) | **+0.042561** |
| W=60 | T3 censored-as-events | +0.040073 (0.000817) | −0.079673 (0.002480) | +0.039388 |
| W=60 | T4 trim upper 5% | +0.054025 (0.001436) | −0.065201 (0.002747) | **+0.043165** |
| **W=20** | T1 correct survival | +0.021765 (0.001815) | −0.152206 (0.002692) | +0.242476 |
| W=20 | T2 drop censored | +0.123779 (0.002460) | −0.150979 (0.003764) | +0.347152 |
| W=20 | T3 censored-as-events | +0.114474 (0.001485) | −0.214837 (0.002612) | +0.333112 |
| W=20 | T4 trim upper 5% | +0.116354 (0.001672) | −0.198286 (0.002811) | +0.335884 |

**Findings.**

4. **The normalisation handle dominates the likelihood handle by one to two orders of magnitude.**
   At W=60 the frozen-rule scale costs **+0.035502** seconds-NLPD even under the *correct*
   likelihood, against **+0.000088** for the same likelihood at the true scale — a factor of ~403.
5. **Two of four W=60 Mode B cells sit at or above the 0.042-nat resolution floor**
   (+0.042561 drop-censored, +0.043165 trim). The other two sit **below** it: +0.039388
   censored-as-events and +0.035502 correct-survival — the latter was omitted entirely from an
   earlier draft of this sentence, which also miscounted two as three. At the real
   cohort's censoring exposure, the cost of estimating `scale_N` from the tail-depleted set is
   **at the edge of scientific materiality** in this synthetic world.
6. **Under the frozen rule the induced error points toward a LIGHTER apparent tail, not heavier:**
   `dk` positive and `dsigma` negative in all eight Mode B cells. This is the opposite direction
   to the Mode A drop-censored cell at high censoring, and it matters for §4.

### 3.3 The estimand split — why the frozen score cannot see any of this

Same Mode B fitted models, scored two ways. `gap` = lognormal − Weibull seconds-NLPD; **positive =
the true (Weibull) family wins**. Oracle gap = **+0.125009** (se 0.001874).

| Window | Treatment | gap on **FULL** population (se) | gap on **ELIGIBLE** subpop — the B3 analogue (se) |
| --- | --- | --- | --- |
| W=60 | T1 correct survival | +0.140334 (0.002045) | +0.157192 (0.002097) |
| W=60 | T2 drop censored | **+0.133403** (0.002203) | +0.158603 (0.002131) |
| W=60 | T3 censored-as-events | +0.136811 (0.002110) | +0.159106 (0.002136) |
| W=60 | T4 trim upper 5% | +0.132722 (0.002262) | +0.158329 (0.002135) |
| W=20 | T1 correct survival | +0.091373 (0.003242) | +0.183698 (0.002389) |
| W=20 | **T2 drop censored** | **−0.012847** (0.006853) | **+0.197343** (0.002410) |
| W=20 | T3 censored-as-events | +0.006371 (0.004557) | +0.202660 (0.002587) |
| W=20 | T4 trim upper 5% | +0.001466 (0.004998) | +0.200496 (0.002503) |

**Findings.**

7. **At the over-stress window the true family's advantage collapses.** W=20 drop-censored under
   the frozen normalisation takes the gap from +0.125009 to **−0.012847**. The paired shift is
   **−0.137856** (se 0.006084), 95% normal interval **[−0.149781, −0.125932]**, excluding 0 →
   the *collapse* is resolved. The *absolute* gap interval is
   **[−0.026279, +0.000585]**, which **contains 0** → an actual preference inversion is
   **`NOT_ESTABLISHED`**. Underpowered here is not equivalence, and a point estimate below zero is
   not a verdict.
8. **The B3-style score is blind to the collapse.** The identical fitted models, scored on the
   eligible (uncensored-only) subpopulation, report **+0.197343** (se 0.002410) — the true family
   winning by *more* than the oracle does. A score computed only on the surviving subpopulation
   cannot detect a mis-specification that lives in the removed tail. **This is the single most
   actionable receipt in this probe.**
9. **At the real-like window there is no collapse.** W=60 drop-censored keeps the gap at
   **+0.133403** (se 0.002203), statistically indistinguishable from the oracle's +0.125009. In
   this synthetic world, at the frozen cohort's actual censoring exposure, the exclusion does not
   reorder the families.

### 3.4 T5 — state-specific censor sensitivity

Because `scale_N` ranges from 3.4826 s (state 2) to 24.5206 s (state 8), a **fixed observation
window censors high-N states far more**. Realised per-state censoring rates, R = 40:

| state | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scale_N` (s) | 4.749 | 3.483 | 6.351 | 5.063 | 7.948 | 14.390 | 18.245 | 24.521 |
| censor rate W=60 | 0.0027 | **0.0007** | 0.0053 | 0.0034 | 0.0119 | 0.0485 | 0.0705 | **0.1095** |
| censor rate W=20 | 0.0476 | **0.0220** | 0.0721 | 0.0534 | 0.1096 | 0.2140 | 0.2598 | **0.3306** |

The rate tracks `scale_N`, not the state index — a **157×** spread at W=60 (state 2 → state 8).
Censoring is therefore a **state-confounded** nuisance: any state-dependent structure inferred from
a windowed dataset is partly a censoring gradient.

**Single-draw stratified fit** (separate configuration: 200 motors × 8 events, true scale,
**R = 1, no uncertainty, indicative only — not evidential**):

| Window | Stratum | censor rate | `k_hat` correct | `k_hat` drop-censored |
| --- | --- | --- | --- | --- |
| W=60 | low-N (1,2,3) | 0.000000 | 0.671695 | 0.671695 |
| W=60 | high-N (6,7,8) | 0.083233 | 0.639279 | 0.659478 |
| W=20 | low-N (1,2,3) | 0.062500 | 0.662156 | 0.693297 |
| W=20 | high-N (6,7,8) | **0.283474** | 0.644286 | **0.557724** (sigma 1.790846 → **1.947100**) |

The drop-censored bias **flips sign between strata** at W=20: upward (lighter tail) in low-N,
downward (heavier tail) in high-N. A single pooled shape estimate averages two opposite biases.

**Methodological note preserved.** A first pass used a *quantile*-based 5% trim. At W=20 it removed
**zero** observations and T4 collapsed byte-for-byte onto T3, because 17–18% of observed durations
pile up exactly at the window boundary, putting the 95th percentile *at* the window. Upper-tail
trimming is **inoperative** once a hard window has already truncated the tail. The reported T4 uses
a rank-based trim instead. This is a real property of trimming windowed data, not a fixed bug.

---

## 4. The builder question, answered

> Does mistreating censoring manufacture an apparent heavy tail?

**Conditionally yes, and the condition is not met by the frozen cohort.**

- **Yes** in one specific regime: dropping censored dwells while the normalisation is held at the
  untruncated scale, at ~17% censoring, moves the shape to `dk` = **−0.032968** and inflates the
  lognormal sigma by **+0.093467** — an apparently heavier tail (Mode A, W=20).
- **No** in the regime the frozen pipeline actually occupies: under the frozen `scale_N` rule the
  bias runs the other way in **all eight** Mode B cells (`dk` positive, `dsigma` negative) — an
  apparently **lighter** tail. The two handles partially cancel, and the normalisation handle wins.
- **At the real-like exposure** (W=60, matched to the real cohort on both 5.0% event rate and 32.8%
  removed time mass) the family ordering is untouched: gap +0.133403 (se 0.002203) vs oracle
  +0.125009 (se 0.001874).

### 4.1 Relevance to the retained M2-over-M3 adverse result — stated as a hypothesis, and
### the probe's own evidence is against it

The **target hypothesis** would be: *the M2_LOGNORMAL-over-M3_TWO_TIMESCALE held-out advantage is
partly an artifact of the frozen cohort's exclusion of right-censored dwells.*

**This probe does not support that hypothesis, and supplies one datum against it.** In a world
whose truth is a Weibull, at the censoring exposure that matches the real cohort, the frozen
exclusion did not reorder the families (finding 9), and the induced bias pointed toward a *lighter*
apparent tail (finding 6) — the wrong direction to explain a lognormal advantage.

Three limits on that negative reading, all of which must travel with it:

1. **The generator is a Weibull, not a two-timescale mixture.** M3's structure is not represented.
   Whether the exclusion differentially damages a mixture is **`NOT_COMPUTED`** here.
2. **The real censoring is structurally different from a fixed window.** The real data has exactly
   one censored dwell per motor — a terminal segment, median 89.26 s, longest in that motor 46% of
   the time. A fixed window censors independently per event. The two mechanisms match on rate and
   on removed time mass but not on *within-motor structure*, and the motor is the experimental unit.
3. **The frozen adverse result already has a stronger explanation on the table.** B4C02 established
   that the M2-over-M3 result is **GENERATOR-SPECIFIC** (`gensWithM2overM3 = 1` of 3), refuting the
   frozen `GENERATOR-ROBUST_ADVERSE` reading. That is a landed result on real machinery; this is a
   synthetic caricature. B4C02 governs.

**Nothing in §4.1 changes any frozen verdict.** The M2-over-M3 adverse result is retained exactly
as it stands.

---

## 5. Claim impact

**Bounded, and the bound is tight.**

- **The F-side model's censoring correctness is currently carrying no observable weight.** The
  frozen cohort contains no censored event, so the censoring branch has never fired on real data.
  Its held-out advantage — M0 +0.115291 `RESOLVED_ABOVE`, M5 +0.031036 `RESOLVED_ABOVE`, everything
  else `NOT_ESTABLISHED` — is entirely attributable to the hierarchy and the Weibull hazard shape,
  **not** to censoring handling. Any narrative that credits the censoring-correct likelihood for
  the F-side result is unsupported.
- **"Its advantage vanishes under every treatment" is not what was measured.** At the real-like
  exposure the *likelihood* treatment is immaterial (≤ +0.001313 nats, ~32× below the 0.042 floor),
  so the F-side advantage is neither created nor destroyed by censoring handling. It is
  **untested** on this axis, which is a different status from tested-and-null.
- **The result that does bind:** at the real-like exposure, the frozen `scale_N` rule costs
  **+0.035502 to +0.043165** seconds-NLPD against the full untruncated population — three of four
  cells at or above the 0.042 resolution floor — and **the B3-style eligible-subpopulation score
  cannot see any of it** (finding 8). This is a statement about the *estimand* the frozen
  leaderboard targets, not about any model's correctness on that estimand.
- **The frozen leaderboard is valid for what it measures.** It scores the tail-depleted eligible
  subpopulation and it does so correctly. It is **not** a leaderboard on the untruncated dwell-time
  distribution of the motor, and no result in this repository should be read as one.

**Scoping, per contract.** P6 for duration-only B3/B4 is unchanged by this probe. P6 for C11 U4
remains withdrawn pending the corrected run. No P-level moved. The first unsatisfied level remains
P4 transfer.

---

## 6. What would make this lane true, and what would kill it

**Receipt that would exercise the censoring branch on real data (the only one available):**
build a *new*, separately named cohort — not the frozen one — that retains the 54 in-band
right-censored events; recompute `scale_N` on it (it will differ, so it is a different cohort by
construction); fit the F-side motor stack with `hazard_survival.log_event_density` and the real
censor flags; and **pre-register the held-out comparison in a commit that is a strict ancestor of
the result commit**, or the receipt is retrospective from birth (D9).

**Falsifier that would kill the lane.** If the censored-inclusive cohort's F-side held-out
contrasts, motor-equal and CI-bound, are `NOT_ESTABLISHED` against M1_WEIBULL with a half-width
below ~0.042 nats, then the censoring-correct likelihood is not carrying the mechanism on this
dataset and should be reported as machinery that is correct but not load-bearing.

**What would kill the §4.1 hypothesis outright.** Re-run §3 with a two-timescale generator matching
the frozen M3 parameters (`w = 0.393356`, `lambdaFast = 0.444859`, `lambdaSlow = 5.239879`) and a
per-motor *terminal* censoring mechanism instead of a fixed window. If the M2-vs-M3 ordering is
unchanged at 5.0% event / 32.8% time exposure, the censoring-artifact explanation is dead.
**`NOT_RUN — COMPUTE_BUDGET`** in this probe (two long runs are in flight; this needs a replicated
mixture-fitting sweep, which is not a sub-two-minute single-process job).

**Threshold hygiene.** The two observation windows (60 s, 20 s) and the 5% trim fraction are
**`DESIGN_ONLY`** and carry no evidential weight. The 0.042-nat resolution floor is the frozen
corrected motor-equal BCa half-width (M4_MIXTURE_K3, BCa width 0.08414086126525253) and is used
here only as a materiality yardstick, not as a pass/fail criterion. No threshold was introduced.

---

## 7. Reproduction

```bash
cd C:/Users/mpolz/Documents/UNI-Flagellum/UNI-FLAGELLUM

# Section 1 - OBSERVED real-data counts (duration channel only)
python -c "import sys; sys.path.insert(0,'hierarchical-aif/src'); \
from motor_stack_aif import _bridge; raw=_bridge.b3().load_events(); \
print(len(raw), sum(1 for e in raw if e['rightCensored']))"

# Sections 2-3 - SYNTHETIC (scripts held in the session scratchpad, not committed)
python probe6_censoring.py   # v1, single draw, 2.4 s   - T5 stratified + trim degeneracy
python probe6_v2.py          # R=40, both modes, 14.5 s - tables 3.1 / 3.2
python probe6_v3.py          # R=40, estimand split, 11.4 s - table 3.3
```

Scratchpad location:
`C:\Users\mpolz\AppData\Local\Temp\claude\C--Users-mpolz-Documents-UNI-Flagellum\42f0792e-ab52-4a4d-8991-5e9fdc602268\scratchpad\`
(`probe6_censoring.py`, `probe6_v2.py`, `probe6_v3.py`, and the three JSON outputs).
These are probe scripts, not repository machinery; nothing under `src/`, `results/` or `audits/`
was modified.

---

## 8. Limitations and what was NOT computed

- **`NOT_MEASURED`** — any real-data censoring *comparison*. Structurally impossible: the frozen
  cohort has zero censored events. Only the *consequence of the exclusion* is observable.
- **`NOT_COMPUTED`** — a two-timescale (M3-structured) generator under censoring stress.
  **Reason: `COMPUTE_BUDGET`**, see §6.
- **`NOT_COMPUTED`** — a per-motor *terminal* censoring mechanism matching the real one-censored-
  dwell-per-motor structure. The fixed-window caricature matches on rate and time mass, not on
  within-motor structure.
- **`NOT_COMPUTED`** — the hierarchical (mu, tau) F-side model under censoring stress. §3 uses a
  single shared shape so that parameter recovery is unambiguous. Whether the hierarchy absorbs or
  amplifies censoring bias is untested.
- **`NOT_COMPUTED`** — a joint ML fit of per-state scale *and* shape under censoring. Mode B uses
  the frozen plug-in rule because that is what the pipeline does; a censoring-corrected scale
  estimator was not built.
- **`NOT_CHECKED`** — any held-out mark quantity. Would require holdout `nextStateN`/`direction`/
  `jump` access, which the D5 firewall forbids. This is the correct answer, not a gap.
- The synthetic intervals in §3 are normal-approximation intervals over 40 replicate draws. They
  are **not** the frozen motor-cluster BCa bootstrap and must never be compared to a frozen
  verdict interval.
- All §2–§4 numbers are simulation output. They are model output and are never `OBSERVED`.
  Only §1 is `OBSERVED`.

---

**Probe status:** COMPLETE. No P-level moved. No frozen verdict changed. No claim created.

NEXT_ACT = Draft `hierarchical-aif/protocols/CENSORED-INCLUSIVE-COHORT-PREDICTION.md` pre-registering, BEFORE any fit is run, the F-side held-out contrast on a new separately-named censored-inclusive cohort retaining the 54 in-band right-censored events, with the falsifier from §6 written into the protocol and the prediction commit made a strict ancestor of the result commit.
