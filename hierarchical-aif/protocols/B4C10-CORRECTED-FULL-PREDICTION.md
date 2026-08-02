# B4C10 — Corrected Full-N Prediction Record

**PROSPECTIVITY: `NOT_SATISFIED` — and not retroactively repairable (D9).**
This file was *written* 2026-07-21 prior to the full-N B4C10 run, but it was **committed
2026-07-21T22:44:31Z in `b9b5670`, 2 h 33 min AFTER the run finished** (~20:11:51Z) and after the
result already existed on disk. Per `CLAUDE.md`, a prediction is prospective only if it was
committed before its observation. **This cell's result may never be labelled `PROSPECTIVE`.** It is
a retrospectively-graded refutation against a pre-written prediction, which is strictly weaker.
**Gate:** H-AIF-G5 · **Cell:** `B4C10_M4_STRUCTURAL_IDENTIFIABILITY`

---

## 1. Purpose

Complete the M4 three-component-mixture identifiability bootstrap (U2/U3/U4) at the **frozen
N_boot = 2000**. It was previously executed at **100 of 2000** replicates (5%) and labelled
`resourceBoundPartial`, on a resource justification since measured at **≈2.1 h** (D2). At that
cost it should never have been partial.

## 2. Runs on the FROZEN runner, unmodified

Unlike B4C02, this cell requires **no code change**:

- **D1 does not apply.** `_fit_m4_reduced` fits the flat pooled `coh.train_y`; duplicate motor
  draws enter correctly, so the bootstrap is a valid motor-cluster bootstrap for a pooled i.i.d.
  likelihood. Verified by `test_m4_pooled_path_is_unchanged_by_the_fix`.
- **D3 does not apply.** C10 seeds with `np.random.default_rng(seed_base)` and `seed_b = seed_base + b`
  — arithmetic, no `hash()`.

Therefore this run invokes the **committed, byte-identical** runner
`audits/phase-b/b4-identifiability-robustness-runner.py` (sha256 `3e21edac97a2b68f…`) with
`--cells C10 --c10-boot 2000`. Strongest possible provenance: the only change from the recorded
run is the replicate count, which is the frozen value.

## 3. Frozen criteria (unchanged)

| check | criterion |
|-|-|
| U2 | bootstrap **collapse fraction** of degenerate M4 fits |
| U3 | width of the `log10(lambda_3)` 95% interval, in decades |
| U4 | `omega_3` 95% interval |

Recorded at 100/2000: `U2_bootstrapCollapseFrac = 0`; `U3 span = 0.40821` decades;
`U4 omega_3 95% CI = [0.03813, 0.31659]`; all three `OK`; `M4_status = IDENTIFIED_ON_THIS_COHORT`.
The frozen prediction was `UNIDENTIFIED_OR_WEAK`, recorded as `REFUTED_PARTIAL`.

## 4. Hypotheses held alive

| id | claim |
|-|-|
| `H_M4_IDENTIFIED` | M4 is identified on this cohort; the 100-replicate reading survives at full N. |
| `H_M4_WEAK` | At full N the collapse fraction rises and/or the intervals widen, so U2/U3/U4 fires and the frozen `UNIDENTIFIED_OR_WEAK` prediction is upheld. |
| `H_NOT_ESTABLISHED` | Intervals do not close against the frozen criteria. |

## 5. Pre-committed outcome mapping

| observed at N=2000 | result | claim impact |
|-|-|-|
| U2/U3/U4 all `OK` | frozen prediction `UNIDENTIFIED_OR_WEAK` **REFUTED at full N** | The earlier `REFUTED_PARTIAL` is upgraded to a full-N refutation **within C10 scope only**. M4 identifiability on this cohort is supported. This is a `P1`/`P6`-scoped statement about one model's identifiability — **not** evidence for any mechanism. |
| any of U2/U3/U4 fires | frozen prediction **CONFIRMED at full N** | The 100-replicate reading was an artifact of partial sampling. The prior `REFUTED_PARTIAL` is **withdrawn**. This would be a second instance of a partial run misleading a verdict — materially reinforcing D2's lesson. |
| interval fails to close / run incomplete | `PARTIAL_NOT_ESTABLISHED` | No verdict. |

**Falsifier of the 100-replicate reading:** any of U2/U3/U4 firing at full N.

**Prediction I am willing to be wrong about:** I expect U2/U3/U4 to remain `OK` at full N, because
0/100 collapses is reasonably strong evidence against a high collapse rate. But 100 replicates
cannot bound a rare-event fraction tightly, so a nonzero collapse fraction at 2000 is entirely
possible and would be the more interesting outcome.

## 6. Explicit boundary

**C10 may not be used to repair C11.** They concern different models (M4 vs M7) and different
likelihood structures (pooled i.i.d. vs motor-grouped). A favourable C10 says nothing about M7
identifiability, and nothing about the withdrawn C11 `U4_OK`.

## 7. Expected runtime

≈2.1 h (2000 × 3.8 s measured). Frozen N; **no reduced protocol required**.

## 8. Wording

**Allowed:** "B4C10 at full frozen N=2000 supports / does not support M4 identifiability on the
`derived_eligible_1_to_8` cohort under the frozen U2/U3/U4 criteria."

**Forbidden:** "M4 is the correct model" · "mixture mechanism confirmed" · any transfer of this
result to M7, to C11, or to mechanism/parity claims.
