# B4C02 — Corrected Full-N Prediction Record

**PROSPECTIVITY: `PENDING_SATISFIABLE`** (graded by the commit graph, not by prose — D9).
Written 2026-07-21 prior to any B4C02 run, and **committed 2026-07-21T22:44:31Z in `b9b5670`,
which is before any B4C02 observation exists** — the run is still in flight and no result file has
been written. If the result lands after that commit, as it must, this cell's prediction **is**
genuinely prospective. This is the only cell in the current batch for which that holds.
**Gate:** H-AIF-G5 · **Cell:** `B4C02_MISSPECIFIED_WORLDS` · **Priority:** HIGHEST (epistemic value)

---

## 1. Purpose

B4C02 is the **misspecified-world discriminator**. It asks whether the B3 adverse result — a
simple lognormal (M2) out-predicting the two-timescale mixture (M3) on held-out data — is a
**generic feature of heavy-tailed dwell shape** rather than evidence about any particular
mechanism.

It was recorded `NOT_RUN` with a `RESOURCE_BOUND` reason claiming 150–250 h. Measured cost is
**≈8.7 h** (D2). It is the single most decisive piece of missing evidence in the submitted
package.

## 2. Why this cell runs first

Under active-inference action selection, when ambiguity is high the next action should be the one
with the highest **epistemic value**, not the cheapest. B4C10 is cheaper (2.1 h) but resolves less:
it completes a replicate count on a cell whose method was never in doubt. B4C02 discriminates
between two live explanations of the headline adverse result. It runs first.

## 3. Design (frozen, unchanged)

Three misspecified generators, each simulating datasets from a world that is **not** any competitor:

| generator | world |
|-|-|
| `weibull_gamma_blend` | Weibull–Gamma blend |
| `three_timescale_heavy_tail` | 3-timescale heavy tail |
| `per_motor_heterogeneous_weibull` | per-motor heterogeneous Weibull |

- **planned_N = 200 simulations per generator** (frozen), 600 total.
- Each simulation: rebuild cohort → fit M0, M1, M2, M3, M5, M6 → score **motor-equal NLPD** on the
  simulated holdout → record the winner and whether M2 beats M3.
- **M4/M7/M8 are skipped by construction** — this is the cell's declared design, and the honest
  statement of its model set (see D4).
- **Frozen criterion:** `gensWithM2overM3 = #{generators with m2_beats_m3_frac >= 0.5}`.
  `>= 2 of 3` → `GENERATOR-ROBUST_ADVERSE`; otherwise `GENERATOR-SPECIFIC`.

## 4. The single deviation from the committed runner

**D3 seeding fix only.** The committed cell seeds with
`np.random.default_rng(seed_base + sim + hash(gen_label) % 100000)`, which is non-deterministic
across processes. The corrected harness substitutes
`seeding.stable_seed(cell_id, base_seed, replicate_index, protocol_version, cohort_id)`,
a SHA-256-derived integer.

Everything else — generators, cohort construction, fitting, scoring, aggregation, criterion — is
called through the **same** `b3`/`b4` functions. No threshold, no N, no criterion, no model set is
changed. `seed_base = 20260802` is unchanged.

Consequence to state plainly: because the seed derivation changes, this run is **not** bit-
comparable to a hypothetical run of the committed cell. It could not have been anyway — the
committed cell produces different data on every invocation. This run is reproducible; that one
was not.

## 5. Hypotheses held alive

| id | claim |
|-|-|
| `H_SHAPE_ARTIFACT` | The adverse M2-over-M3 result arises from heavy-tailed dwell **shape** and reappears under worlds with no two-timescale mechanism. |
| `H_MECHANISM_INFORMATIVE` | The adverse result reflects something about the **specific** generating mechanism and does not reproduce under generic misspecification. |
| `H_NOT_ESTABLISHED` | The generators do not separate the explanations at this N. |

## 6. Pre-committed outcome mapping

| observed | result | interpretation | claim impact |
|-|-|-|-|
| `gensWithM2overM3 >= 2` → `GENERATOR-ROBUST_ADVERSE` | **prediction CONFIRMED** | `H_SHAPE_ARTIFACT` supported within scope | **Weakens** any mechanistic reading of M3's held-out loss. The adverse result stays retained but is reframed as shape-driven. Does **not** vindicate M3, and does **not** support the motor-stack AIF model. |
| `gensWithM2overM3 <= 1` → `GENERATOR-SPECIFIC` | **prediction REFUTED** | `H_SHAPE_ARTIFACT` weakened | The adverse result is **not** generic to heavy-tailed shape. This **strengthens** the case that the M2-vs-M3 contrast carries mechanism-relevant information — but establishes no mechanism by itself. |
| any generator run fails / N incomplete | `PARTIAL_NOT_ESTABLISHED` | — | No verdict. Status per `status.classify_run`. |

**Falsifier of the frozen prediction:** `gensWithM2overM3 <= 1` at full frozen N.

## 7. What this cell cannot do, whatever it returns

- It cannot establish biological parity, mechanism, or active inference.
- It cannot promote M2 to "the UNI model" — M2 is an **adversarial baseline**.
- It cannot move `P6` structural/mechanistic on its own; it constrains *interpretation* of `P3`.
- A `GENERATOR-ROBUST_ADVERSE` result is **not** a defeat of the motor-stack AIF model, which is
  not entered in this competition. It is a statement about what the M2/M3 contrast can support.
- Because M4/M7/M8 are skipped, this cell says nothing about the mixture, hierarchical, or KDE
  models.

## 8. Expected runtime

≈8.7 h (600 sims × 52.1 s measured). Frozen N; **no reduced protocol required**.

## 9. Wording

**Allowed:** "B4C02 corrected full run supports / weakens / does not establish the shape-artifact
explanation of the adverse M2-over-M3 result within its frozen scope (3 generators, 6 simple
competitors, motor-equal NLPD, single 19-motor cohort)."

**Forbidden:** "mechanism demonstrated" · "biological parity" · "active inference proved" ·
"full flagellum parity" · "M2 is the UNI model" · "M3 is vindicated" · any statement that this
cell tests the motor-stack AIF model.
