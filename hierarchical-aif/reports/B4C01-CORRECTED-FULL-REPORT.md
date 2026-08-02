# B4C01 — Corrected Full-N Result Report

**Gate:** H-AIF-G5 · **Cell:** `B4C01_SYNTHETIC_PARAMETER_RECOVERY` · **Lane:** **B** · **Date:** 2026-07-22
**Result:** `hierarchical-aif/results/motor_stack_aif/B4C01_CORRECTED_FULL_RESULT.json`
sha256 `8256cb120376f46bf00b537d2ad665f9d50335e3eed3727a1299129195dfb65b`
**Committed prediction:** `hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md` @ **`28ce738`**
**Maps to:** `P0`/`P1` pipeline integrity; constrains the *interpretation* of `P3`. **No P-level is raised.**

---

## 1. Executive result

B4C01 ran to completion at the **full frozen N = 200 simulations per generator × 5 generators =
1000 simulations**, with **zero failures** and `resourceBoundPartial: false`.
`runStatus = ELIGIBLE_FOR_FROZEN_VERDICT`.

**Verdict `NOT_ESTABLISHED`. The frozen expectation `PASS` is REFUTED at full N.**

**Exactly one criterion failed:** `failingCriteria = ['M0_EXPONENTIAL:self_win']`.

**All four parameterised generators recovered their true parameters well inside tolerance.** The
failure is entirely in **self-win**, and entirely in the one generator that every other competitor
nests.

Per the four-way classification pre-committed in the landing template, this is unambiguously:

> **CLASS B — self-win / power failure with parameter recovery intact.**
> **This is a POWER / ASSAY-RESOLUTION finding, NOT a fitter defect.** Reading it as "the B3
> pipeline is broken" is a misreading and is forbidden.

## 2. Results by generator

| generator | n | failed | `self_win_frac` | passes `>0.5` | true param | median recovered | median bias | tolerance | `withinTolerance` |
|-|-|-|-|-|-|-|-|-|-|
| `M0_EXPONENTIAL` | 200 | 0 | **0.290** | **NO** | *(none)* | — | — | — | n/a |
| `M1_WEIBULL` | 200 | 0 | 0.590 | yes | `0.6250888335850175` | `0.6285001063169614` | `+0.0034112727` | `0.1` | **True** |
| `M2_LOGNORMAL` | 200 | 0 | 0.885 | yes | `1.5783076101407152` | `1.5566808259465263` | `−0.0216267842` | `0.1` | **True** |
| `M3_TWO_TIMESCALE` | 200 | 0 | **0.935** | yes | `w 0.3933559993214189`, `lf 0.44485933051063775` | `w 0.40076557267272755`, `log10(lf) −0.34272092193630915` | `w +0.0074095734`, `log10(lf) +0.0090563741` | `w 0.1`, `log10(lf) 0.2` | **True** |
| `M5_GAMMA` | 200 | 0 | 0.670 | yes | `0.5115799798433341` | `0.5122069255579786` | `+0.0006269457` | `0.15` | **True** |

**Parameter recovery is not merely inside tolerance — it is inside it by one to two orders of
magnitude.** The largest bias is M2's `−0.0216` against a `0.1` tolerance (22% of budget); M5's is
`+0.00063` against `0.15` (0.4% of budget). The fitters are unbiased on their own synthetic data.
**`P1` for the simple-model fitters is in no way implicated.**

## 3. What actually failed, and why it is a statement about the assay

`M0_EXPONENTIAL` self-won **58 of 200** simulations (0.290) against the frozen `> 0.5` threshold.

The mechanism was pre-committed in §7 of the prediction record and the result matches it:
`M0_EXPONENTIAL` is **nested inside** `M1_WEIBULL` (`k = 1`), **inside** `M5_GAMMA`
(`shape = 1`), and is a **degenerate limit** of `M3_TWO_TIMESCALE`. When the truth is exponential,
those three fit it essentially as well; the only price they pay out-of-sample is the estimation
variance of one or two extra parameters, of order `p / 2n ≈ 0.0006` nats — **far below the sampling
noise of a motor-equal score over 19 synthetic holdout motors**. And M0 must beat **all five**
competitors simultaneously to self-win.

**0.290 sits just above the ~0.25 that near-random selection among four indistinguishable models
would give.** That residual is the true model's real but unresolvable edge.

**The assay is not uniformly blind — and that is the sharper finding.** The two structurally
distinctive generators self-win strongly: `M3_TWO_TIMESCALE` at **0.935** and `M2_LOGNORMAL` at
**0.885**. The design resolves models that differ in shape. It is **specifically blind between a
model and the competitors that nest it**. "Underpowered" understates it; the correct statement is
*nesting-blind at this holdout size*.

### What this licenses about the rest of the programme

This is the sanity-floor control that makes other cells interpretable, so its failure mode matters
beyond itself. It means: **an `INCONCLUSIVE`/`NOT_ESTABLISHED` contrast between nested or
near-equivalent models in B3 or in the F-side scoring is the expected output of this design, not
evidence about the models.** It is direct, measured support for the standing caution that
underpowered is not equivalence — and it now has a number attached.

It does **not** license doubting B3's resolved contrasts, nor the adverse M2-over-M3 finding: those
involve structurally distinct models, exactly the case this cell shows the assay *can* resolve.

## 4. Prediction scorecard — graded against the COMMITTED record, unrevised

The prediction record was committed at `28ce738` while the cell had **never been executed at any N**.

| # | committed claim (§7) | observed | outcome |
|-|-|-|-|
| 1 | verdict **`NOT_ESTABLISHED`**, not the frozen `PASS` | `NOT_ESTABLISHED` | **HIT** |
| 2 | **all four** parameterised generators pass `withinTolerance` | all four `True` | **HIT** |
| 3 | `M0_EXPONENTIAL` is the failure point | `failingCriteria = ['M0_EXPONENTIAL:self_win']` — the only failure | **HIT** |
| 4 | M0 `self_win_frac` ∈ **[0.20, 0.50]** | **0.290** | **HIT** |
| 4a | …"most likely 0.30–0.40" | 0.290 | **narrow miss** — inside the committed band, marginally below the stated modal sub-band |
| 5 | secondary risk `M5_GAMMA` ∈ [0.40, 0.70] | 0.670 | **HIT** |
| 6 | `M2_LOGNORMAL` > 0.80 | 0.885 | **HIT** |
| 7 | `M3_TWO_TIMESCALE` ∈ [0.50, 0.80], "M2 its main threat" | **0.935** | **MISS** — M3 self-won far more strongly than predicted |
| 8 | ordering **M0 < M5 < M3 < M1 < M2** | **M0 < M1 < M5 < M2 < M3** | **MISS** |

**Six clean hits, one narrow miss, two misses.** The misses are recorded, not absorbed:

- **Item 7/8 — I underestimated M3.** I reasoned from B4C02 that M2 threatens M3 in heavy-tailed
  worlds, and carried that into M3's *own* world. Wrong: when the generator **is** the
  two-timescale process, M3 self-wins at 0.935 — the highest of any generator. The B4C02 lesson
  (M2 beats M3 under a *three*-timescale truth) does not transfer to M3's correctly-specified case,
  and I over-transferred it.
- **Item 8 — the ordering.** I placed M5 below M1; observed M1 (0.590) below M5 (0.670). Both are
  one-parameter shapes competing against each other and against M0; I have no principled account of
  which should lose more, and the prediction claimed more resolution than my reasoning supported.

**The primary structural claim — `NOT_ESTABLISHED` driven by M0 self-win with recovery intact — was
correct, and it was the risky part.** The frozen expectation said `PASS`.

## 5. Provenance

| field | value |
|-|-|
| command | `python hierarchical-aif/scripts/run_c01_corrected_full.py 200 …/B4C01_CORRECTED_FULL_RESULT.json` |
| harness | `hierarchical-aif/scripts/run_c01_corrected_full.py` (sha256 `e4474fb7…`) |
| frozen runner consumed | `audits/phase-b/b4-identifiability-robustness-runner.py` sha256 `3e21edac97a2b68faec087e73de307439348e89e778b6e97d84809bbf1e135a7` — **READ-ONLY, UNMODIFIED** |
| correction applied | **`D3_HASH_SEED_NONDETERMINISM` only** — `seeding.stable_seed` replaces `hash(gen) % 100000`. `+ sim`, `seed_base = 20260801`, generators/order, tolerances, `> 0.5` threshold, model set and verdict rule all unchanged |
| planned_N / actual_N | **200 / 200** per generator; 1000 total; **0 failures** |
| started / ended (UTC) | `2026-07-22T04:13:27Z` → `2026-07-22T21:03:09Z` |
| runtime | **60 577.5 s = 16.83 h**; **60.58 s/sim** |
| exit code | 0 |
| stderr | **0 bytes** |
| result sha256 | `8256cb120376f46bf00b537d2ad665f9d50335e3eed3727a1299129195dfb65b` |
| `intervalUsed` / BCa width / percentile width | **`NOT_APPLICABLE` / `NOT_COMPUTED` / `NOT_COMPUTED`** — the frozen C01 criteria are a **median-bias tolerance** and a **win fraction**. Neither is a CI contrast, so no interval exists to quote |

### D2 — the cost lesson, inverted this time

| estimate | value | error |
|-|-|-|
| frozen `NOT_RUN` reason | 250–400 h | **overstated ~15–24×** |
| projection in the committed record (from B4C02's 49.015 s/sim) | 13.62 h | **understated 1.24×** |
| **N=1 smoke test, measured under contention** | **61.42 s/sim** | **accurate to 1.4%** (actual 60.58) |

The smoke measurement taken *under the conditions the run would actually face* beat the
cross-cell projection. B4C02's rate was measured while it shared the box differently; B4C01 ran its
whole life alongside B4C11. **Measure in the regime you will run in** — a refinement of D2, and the
committed record's promise that "the harness will record its own `secondsPerSim` so this projection
is itself falsifiable" was honoured, and it falsified it.

### D4 — the frozen reason text remains wrong, and is superseded not edited

The frozen artifact justified `NOT_RUN` with *"~15–25 min per **M4/M7-inclusive** competition"*.
**This cell fits neither M4 nor M7.** `corrected_reasons.C01_REASON` supersedes it for reporting;
the frozen artifact is **not edited**.

## 6. Prospectivity — `SATISFIED`, and the cleanest in the batch

| fact | value |
|-|-|
| prediction record introduced by | **`28ce738`**, 2026-07-22T04:05:29Z |
| B4C01 observation came into existence | 2026-07-22T21:03:09Z |
| ordering | **committed 16 h 58 min BEFORE the observation** ✓ |
| state at commit time | the cell had **never run at any N** — frozen artifact `status=NOT_RUN`, `actual_N=0`; no smoke test, no partial, no result anywhere |
| content drift | **none** — committed blob == on-disk == launch-pinned `5e08cfd3…` |

Unlike B4C02 (committed mid-run) and B4C11 (committed at 210/2000), **there was no partial evidence
of any kind in existence** when this prediction was committed. Compare B4C10 and the F-side
scoring, both permanently `NOT_SATISFIED` under D9.

Per D9, the flip `PENDING → PROSPECTIVE` belongs **in the result commit**, and the prediction and
result must **never share a commit**. The result is currently uncommitted; that ordering is intact.

## 7. Lane impact — scoped

| lane | impact |
|-|-|
| **LANE B** | B4C01 moves `NOT_RUN` → **full-N result with a frozen verdict**. Three of four corrected cells have now landed; **B4C11 is still running** |
| **LANE A** | duration-only B3/B4 **unchanged**. Every dataset in this cell is **SYNTHETIC** |
| **LANE C** | **unaffected** — no mark field read |
| **LANE D** | **unaffected** by the verdict — but §3's finding *contextualises* the F-side `NOT_ESTABLISHED` results, which is an interpretation, not a change to them |
| **LANE E** | **unaffected** — no parity receipt moves |

**D3 closes**: the corrected harness ran deterministically to completion with `PYTHONHASHSEED`
unset and 0 failures. **D2** remains `CLOSING` until B4C11 lands.

## 8. What this cell cannot do

- **No mechanism, no biological parity, no active-inference claim.** Every dataset is **SYNTHETIC**;
  nothing here may be labelled `OBSERVED`.
- **It cannot move `P6`.** It speaks to `P0`/`P1` integrity and constrains the interpretation of `P3`.
- **`M4`/`M7`/`M8` are skipped by construction**, so it says nothing about the mixture,
  hierarchical or KDE models — including the F-side candidate, which is not entered.
- **It does not invalidate B3.** The failure is confined to nested near-equivalent models; the
  distinctive generators self-win at 0.885 and 0.935.
- `withinTolerance` tests **bias on the median, not spread** — a real weakness of the frozen
  criterion, applied as written rather than fixed here.

## 9. Limitations

Five generators do not span plausible model space. One cohort geometry — every simulated dataset
inherits the `derived_eligible_1_to_8` structure and its 19-holdout-motor sampling noise. Self-win
is a **win-rate, not an effect size**, and carries no interval; the frozen criterion is a bare
threshold comparison, so no CI-bound statement about `0.290` is available and none is made.

---

`NEXT_ACT = supervise PID 26756 (B4C11, 1820/2000, ~1.9 h out; watcher bgd8slocg armed). On landing: sha256sum the result into B4C11_CORRECTED_FULL.sha256, fill reports/templates/B4C11-CORRECTED-FULL-REPORT.TEMPLATE.md into reports/B4C11-CORRECTED-FULL-REPORT.md against committed prediction 897c8ab, route D1, update the P-ladder mapping, run both guards and the suite`
