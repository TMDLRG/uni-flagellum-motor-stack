# Biological Parity Receipt Map

**Full biological parity is not a current status. It is the target world defined by these receipts.**

The framing question for every lane is **"What would make this lane true?"** — never "why this lane
fails." Existing `P0..P8` definitions in `CLAUDE.md` are authoritative and unchanged.

---

## LANE A — duration-only B3/B4 evidence

| | |
|-|-|
| **current receipts** | B3 result `5d7a0589…` (9 models × 2 cohorts × 2 rules, 36 cells); held-out motor-equal NLPD on the frozen `sha256_mod5` split; 44/44 independent oracle; preflight 46/46; determinism byte-identical |
| **current status** | **STANDS.** Retained adverse result: M2 lognormal out-predicts the M3 two-timescale mixture on held-out data. All 8 motor-equal M3 contrasts `INCONCLUSIVE` at 19 holdout motors |
| **next receipt** | **C02 and C10 have landed**; C11 running, C01 queued. B4C02 shows the adverse M2-over-M3 pattern is **generator-specific**, not a generic heavy-tail artifact — so "it is just shape" is no longer an adequate account of the retained adverse result. **No mechanism is established by this.** Next: C11, C01 |
| **falsifier** | an adversarial baseline survives or wins under corrected CI-bound tests |
| **maps to** | `P3` held-out predictive (duration-only scope) |

## LANE B — corrected robustness

| | |
|-|-|
| **current receipts** | C03–C08 executed; D1 bootstrap repaired + tested; D3 stable seeding repaired + tested; resource costs re-measured; **B4C10 LANDED at full frozen N_boot=2000** (`959a00e9…`, 8372.7 s, 1994/2000 completed, U2/U3/U4 all `OK`) on the byte-identical frozen runner; **B4C02 LANDED at full frozen N=200/generator** (`0633988d…`, 8.17 h, 600/600 sims, 0 failures, `ELIGIBLE_FOR_FROZEN_VERDICT`) |
| **current status** | **IN PROGRESS.** C10 **complete**; **C02 complete** (`GENERATOR-SPECIFIC`, frozen prediction `GENERATOR-ROBUST_ADVERSE` **REFUTED** at full N — the adverse M2-over-M3 result is **not** generic to heavy-tailed shape); C11 **running**; C01 queued. C11 U4 remains withdrawn pending its corrected run — **B4C10's favourable result may not be transferred to C11** (M4 pooled-i.i.d. vs M7 motor-grouped; different likelihood structure) |
| **next receipt** | the two remaining corrected full-N results (**C11 running**, **C01 queued**), each hashed, with old-vs-new status tables |
| **falsifier** | corrected cells fail, or remain inconclusive at full N |
| **maps to** | `P3`, `P6` per cell |

## LANE C — mark process

| | |
|-|-|
| **current receipts** | schema carries `nextStateN`/`direction`/`jump`; B3 never reads them; D6 quarantine policies implemented and tested |
| **current status** | **QUARANTINED.** Holdout mark channel burned (D5) → retrospective-only on this dataset. Closed-chain modelling blocked by D6: 2 impossible marks, 5 zero-support holdout cells, 15–17% of marks leave `{1..8}` |
| **next receipt** | raw-archive re-derivation of the 2 impossible marks **and** an independent prospective mark dataset with a predeclared smoothing/quarantine policy |
| **falsifier** | impossible marks persist unresolved; smoothing constant controls the outcome (it currently flips the sign); transfer fails |
| **maps to** | `P2` (mark fields), `P6`; prospective route now runs through `P4`/`P7` |

## LANE D — motor-stack AIF

| | |
|-|-|
| **current receipts** | constrained F-side model built: 2 free params, per-motor latents integrated by quadrature, censoring-correct hazard/survival, no floor, motor-equal scoring, motor-resampling bootstrap; **385 tests pass**. **SCORED 2026-07-22** — `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` sha256 `b3b12720…`, determinism proven byte-identical over two full executions, independent-oracle check **PASS with residual exactly `0.0`** against three frozen models (M3, M0, M8) |
| **current status** | **BUILT AND SCORED. Verdict `NOT_ESTABLISHED`** against `CONTROL_CURRENT` (M3) and against every serious adversary (M2, M8, M1); `RESOLVED_ABOVE` only against the two weakest (M0, M5). **The F-side model reproduces the frozen `M7_HIERARCHICAL_MOTOR` to `2.5e-7` nats — at this resolution it is a re-derivation of the incumbent, not an advance on it.** The hierarchy buys nothing measurable over its own `tau → 0` limit `M1_WEIBULL` (contrast `+0.000615`, half-width `0.0111`). G-side fenced: `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER` |
| **retained adverse** | `M2_LOGNORMAL` (`3.4093`) and `M8_EMPIRICAL_KDE` (`3.4225`) both out-predict the F-side motor stack (`3.4327`) on point estimate. Both intervals cross 0, so this is `NOT_ESTABLISHED` — **not** a refutation and equally **not** a defence. The standing lognormal adverse finding is **extended, not overturned** |
| **next receipt** | per-motor arrays for M4/M6/M7 **DELIVERED 2026-07-22** (`751a59ef...`): all three re-derived at **exact zero** oracle residual; **neither M4 nor M6 resolves** against the candidate; M7 exposed **D10** (no minimum-effect-size guard). Candidate ranks **5th of 10**. Remaining: more independent motors; a model that beats its own `tau → 0` limit; censored observations to exercise the unexercised censoring branch |
| **falsifier** | an adversary's contrast interval lies entirely **below** 0. Not observed — so `H_FSIDE_DURATION` is **not falsified**, and equally **not supported**, against the serious competitors |
| **maps to** | `P1` on implementation (**strengthened**: exact-zero oracle residual + proven determinism); `P3` duration-only scope — **unchanged, B3 stands.** No P-level raised |

### The G-side requirement, stated concretely

`G` needs policies over **actions**; this dataset has none — the action set is empty, which is
structural, not sample-size-limited. To make `G` a biological motor claim requires **all three**:
(1) a manipulated variable with recorded onset time, (2) paired pre/post observation on the same
motors, (3) enough independent motors per condition for a CI-bound verdict. Until then `G` is used
only at ORCHESTRATE level to choose the next experiment.

## LANE E — full biological parity

| | |
|-|-|
| **current receipts** | `P0` H-AIF-G1 established; `P1` corrected implementations tested; `P3` duration-only B3 stands |
| **current status** | **`FULL_PARITY = false`.** `P8` is conjunctive; **`P4` transfer is the first unsatisfied level** |
| **next receipt** | `P0`–`P7` conjunctively supported |
| **falsifier** | any required level remains `NOT_ESTABLISHED` |

### Per-level status

| level | status | missing receipt |
|-|-|-|
| `P0` computational integrity | **holds** | maintain frozen baseline; correct D7 width reporting |
| `P1` equation / implementation | **repaired in new namespace** | F-side scoring; corrected runs complete |
| `P2` observational | **limited** | raw MAT archive absent (`BLOCKED_EXTERNAL`); D6 unresolved for mark fields |
| `P3` held-out predictive | **stands, duration-only** | corrected B4 results; F-side scored comparison |
| `P4` transfer | `NOT_ESTABLISHED` | an independent dataset with a predeclared split — **cannot be closed by modelling** |
| `P5` intervention | `NOT_ESTABLISHED` | wet-lab perturbation with recorded response — **cannot be closed by modelling** |
| `P6` structural / mechanistic | **scoped**: C11 U4 withdrawn pending rerun; mark-mechanism retrospective-only; duration-only unchanged | corrected C11; a mechanism discriminator; independent mark data |
| `P7` independent replication | `NOT_ESTABLISHED` | a second lab/dataset — **cannot be closed by modelling** |
| `P8` full verdict | **false** | all of the above |

**`P4`, `P5`, and `P7` cannot be closed by any amount of modelling, code, or analysis in this
repository.** They require data this project does not have. Saying so plainly is not defeatism; it
is what makes the levels that *are* movable worth moving.

## Strongest claim currently licensed

> On a single 19-motor *E. coli* cohort (Wadhwa 2022), under a frozen `sha256_mod5` split and
> motor-equal NLPD/CRPS scoring, a simple lognormal dwell model out-predicts the two-timescale
> mixture on held-out data, and every motor-equal contrast against the reference mechanism is
> inconclusive at this sample size. No mechanism, transfer, intervention, or parity claim is
> supported.

## Standing frame

```text
Nature supplies the architecture candidate. The gate supplies the status.
Full biological parity is not a current status. It is the target world defined by these receipts.
```
