# Negatives and Partials — preserved, never absorbed

Adverse results, refuted predictions, partial runs, not-run cells, and blocked externals. **These
are first-class evidence.** They are reported alongside every later result, never instead of one.

---

## 1. Retained adverse results

| id | result | status |
|-|-|-|
| **ADVERSE-LOGNORMAL** | A simple lognormal (M2) **out-predicts** the two-timescale UNI mixture (M3) on held-out data under motor-equal NLPD, in both cohorts. Event-pooled gap 0.03687 / 0.03872 reproduces B2. | **RETAINED — HEADLINE.** Not superseded by any later work. Predictive superiority is never promoted to mechanism. |
| **ALL-CONTRASTS-INCONCLUSIVE** | All 8 motor-equal M3 contrasts are `INCONCLUSIVE` at 19 holdout motors. B4C04 shows this is seed-stable across 5 seeds × 2 replicate counts × 2 rules × 2 cohorts. | **RETAINED.** A sample property, not a seed artifact. **Underpowered is not equivalence.** |
| **RULE-DISAGREEMENT** | M2 ranks first under NLPD and near-last under CRPS-seconds. | **RETAINED.** Scoring-rule dependence is real. |
| **M7-MEAN-ONE-FRAGILITY** | The frozen M7 uniform-grid mean-one trapezoid mis-integrates the near-zero `y^(a-1)` singularity (0.9999942). The property holds **exactly** (analytic weight sum 1 to 1e-15). | **RECORDED VERBATIM.** Tolerance not loosened. |

## 2. Refuted frozen predictions (B4)

| cell | prediction | observed | outcome |
|-|-|-|-|
| B4C03 | STABLE | M8 rank 2→3 at +1 bandwidth grid step | **REFUTED** |
| B4C06 | BOUNDARY-STABLE | top-3 reorders under drop-longest | **REFUTED** |
| B4C08 | LOMO-STABLE | 2 non-primary contrasts flip under single-motor removal | **REFUTED** |
| B4C10 | UNIDENTIFIED_OR_WEAK | U2/U3/U4 all OK at 100/2000 | **REFUTED_PARTIAL** — being re-run at full N |
| B4C11 | PROFILE_FLAT_OR_WEAK | U2 OK (full contract); U4 OK at 30/2000 | **REFUTED_U4_PARTIAL → U4 WITHDRAWN** (D1) |

A refuted prediction closes as refuted and stays visible.

## 3. Withdrawn claims

| claim | reason | route back |
|-|-|-|
| B4C11 `U4_OK`; τ CI `[0.17658, 0.27020]` | D1 cluster-collapse bootstrap: 80 draws → 46 groups | corrected C11 full N=2000 |
| `RESOURCE_BOUND` justifications for C01/C02/C10/C11 | D2: overstated 17–29× vs measured | reclassification issued; runs scheduled |
| Track D resolution floor ≈0.064 nats | wrong narrowest contrast (M2 vs actual M4) + D7 | corrected floor **≈0.042 nats** |

## 4. Not run / blocked

| item | status | why |
|-|-|-|
| B4C01, B4C02, B4C09 (original) | `NOT_RUN` historical | recorded `RESOURCE_BOUND`; **justification since withdrawn** (D2). C02 now running; C01 queued; C09 still `NOT_RUN` |
| B4C06 `analysisStartIndex ∈ {3400, 3600}` | `BLOCKED_EXTERNAL` | raw MAT archive absent |
| Leave-one-study-out, leave-one-condition-out | `NOT_RUN` **by construction** | single study; no separable condition label |
| Raw archive re-derivation | `NOT_LOCATED_RAW_ARCHIVE` | `data/remodeling_data.mat` absent |
| `P4` transfer, `P7` replication | `NOT_ESTABLISHED` | no independent dataset — **not closable by modelling** |
| `P5` intervention | `NOT_ESTABLISHED` | no perturbation data — **not closable by modelling** |
| G-side biological policy selection | `DESIGN_ONLY_UNTIL_INTERVENTION` | passive dataset; action set structurally empty |
| Prospective mark-process claims | `RETROSPECTIVE_ONLY` | **D5** — holdout mark channel burned |

## 5. Self-inflicted process negatives

Recorded because a laboratory that hides its own procedural failures cannot be trusted with its
scientific ones.

| id | what | cost |
|-|-|-|
| **D5** | A subagent brief with no split boundary caused a read of the held-out mark channel | Permanent within this dataset. Mitigated only by the channel having had little resolving power (contrast `NOT_ESTABLISHED`, sign flips with the smoothing constant) |
| **Claim-guard self-reference** | Guard scanned its own phrase dictionary (19 false hits); then its own FAIL report (124) | Fixed via documented exclusions |
| **Claim-guard cross-line masking** | A `"forbidden"` on a previous line masked a real claim on the next | Fixed: negation must be same-line. Would have passed a genuine parity claim under a forbidden-wording table |
| **Test conflated "small" with "unresolvable"** | A uniform paired offset is genuinely resolvable; the test asserted otherwise | Split into two tests; distinction documented |
| **TDD ordering not strictly red-then-green** | D1/D3 corrected paths were authored with their tests | Disclosed in `H-AIF-G4-RUNNER-FIX-REPORT.md` §5 rather than presented as compliance |

## 6. Carried Phase-1 limitations (must reach the final ledger)

- D1 honest headline is **20/23 credited**, not 22/23. **AC4 FAILS.**
- `D1A10B_LATTICE_SINGLE_BOND_DOUBLE_COUNTED`: real detection, no strict prospective ancestry →
  prospective status `NOT_ESTABLISHED`.
- Live stator integrality remains `NOT_ESTABLISHED`.
- Mojibake in three Unicode diagnostic regexes in the corrected D1 runner (do not use it to create
  new evidence).
- `package-manifest-addendum-v2.json` scope limitation (lists 6 artifacts, not itself).

## 7. Repository-level verdicts (unchanged, not authored by this program)

```text
cross-study X16_FULL_BIOLOGICAL_PARITY = FAIL
  X06, X11 FAIL; X10, X12 NOT_ESTABLISHED; X13, X14, X15 BLOCKED_EXTERNAL; X01-05, X07-09 PASS
science-gates overall = PARTIAL_PARITY_ONLY  (G03, G05, G06 FAIL)
observed-experiment H1/H2 SUPPORTED_WITHIN_PROTOCOL; H4 INCONCLUSIVE
```

Gates move only by real evidence, never by relabeling.
