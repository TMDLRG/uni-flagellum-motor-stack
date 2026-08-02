# MATERIALITY MAP — ALL 57 HELD-OUT CONTRASTS

**Status:** BUILDER-SUPPORT PROBE. Interpretation layer only.
**Artifact:** `hierarchical-aif/results/motor_stack_aif/materiality_map_all_contrasts.json`
**Builder:** `hierarchical-aif/scripts/build_materiality_map.py`
**Channel:** DURATION_ONLY — `nextStateN` / `direction` / `jump` were never requested (D5).
**No new science.** No refit, no bootstrap, no data load. Every number is copied from a frozen
artifact or derived from it by subtraction. **No frozen verdict is altered. No P-level moves.**

---

## 1. Headline

Of the **57** contrasts this repository holds, **25** are scored in NLPD nats and can be compared
against the resolution floor at all. The other **32** are CRPS and are excluded on units grounds
(section 3).

Among the 25 nats-scale contrasts:

| `scientificReading` | count |
|---|---|
| `MATERIAL` (effect exceeds the 0.042-nat floor) | **3** |
| `SUB_FLOOR_EFFECT` (point estimate below the floor) | **19** |
| `SCIENTIFICALLY_NULL` (whole interval inside ±0.042) | **3** |

**22 of 25 nats-scale contrasts sit at or below the resolution floor.**

And `reportableAsAWin` — frozen verdict resolved **and** effect above the floor — is true for
**exactly one contrast in the entire repository**:

> `FSIDE | derived_eligible_1_to_8 | NLPD_motor_equal | M0_EXPONENTIAL`
> effect `+0.11529094279542929` nats, percentile interval `[+0.013039958895400987,
> +0.22749707235626093]`, frozen verdict `RESOLVED_ABOVE`, effect/floor `2.745`.

That is the F-side motor stack out-predicting a single-rate exponential on held-out durations.
It is the weakest adversary in the set. Nothing else clears both bars.

Frozen verdicts across all 57 rows: `INCONCLUSIVE` 48 · `NOT_ESTABLISHED` 6 · `RESOLVED_ABOVE` 3.
**All 48 frozen B3 contrasts are `INCONCLUSIVE`** — the frozen record already said so; this map
only adds why.

---

## 2. The resolution floor — what it is and what it is not

`resolutionFloor = 0.042` nats/event. It is a **HALF-width**.

**Derivation:** the BCa half-width of the narrowest frozen B3 contrast — cohort
`derived_eligible_1_to_8`, rule `NLPD_motor_equal`, model `M4_MIXTURE_K3`. BCa width
`0.08414086126525253`, half `0.04207043063262626`, used as `0.042` (the same constant already
hard-coded in `scripts/recompute_m4_m6_m7_per_motor.py` and recorded as
`resolution.halfWidthFloorNats` in the F-side result).

**It is a HEURISTIC.** It was not pre-specified, it is not an equivalence margin, and **no verdict
anywhere in this repository was decided by it**. It describes what this assay can *resolve*; it
does not describe what the bootstrap will *call*. The superseded figure `0.064` came from the
mislabelled `width` field (D7).

**Cohort provenance:** the floor was derived on `derived_eligible_1_to_8`. Rows from
`primary_states_0_to_8` carry `floorTransferCaveat = true` in the JSON — same units, different
cohort, so the comparison is indicative rather than exact.

`MATERIAL` means *large enough to matter*. It does **not** mean resolved. Two of the three
`MATERIAL` rows carry the frozen verdict `INCONCLUSIVE` (section 5).

---

## 3. Units fence — the CRPS rules do not get a floor

B3 scores three rules: `NLPD_motor_equal`, `CRPS_normalized`, `CRPS_seconds`. The 0.042 figure is
a **nats/event** quantity. `CRPS_seconds` is in seconds; `CRPS_normalized` is dimensionless CRPS
on normalised `y`. Neither is nats.

Therefore for all **32** CRPS rows the JSON emits:

```
resolutionFloor      = NOT_APPLICABLE_DIFFERENT_UNITS
effectToFloorRatio   = NOT_APPLICABLE_DIFFERENT_UNITS
scientificReading    = NOT_APPLICABLE_DIFFERENT_UNITS
reportableAsAWin     = NOT_APPLICABLE_DIFFERENT_UNITS
```

Carrying a nats floor onto a CRPS scale would be a units error of exactly the kind the truth
contract forbids. Their frozen verdicts, point estimates, BCa widths and percentile widths are
still recorded in full — only the floor comparison is withheld. A CRPS-side materiality floor is
**`NOT_COMPUTED`**; deriving one would need the same narrowest-contrast construction repeated in
CRPS units, which this probe did not do.

---

## 4. BCa availability — `NOT_COMPUTED` for 9 of 57

| source | n | BCa | percentile |
|---|---|---|---|
| frozen B3 (`audits/phase-b/b3-model-competition-result.json`) | 48 | recorded | recorded |
| F-side scoring | 6 | **`NOT_COMPUTED`** | recorded |
| M4/M6/M7 post-hoc extension | 3 | **`NOT_COMPUTED`** | recorded |

The F-side harness and the M4/M6/M7 extension emit **percentile intervals only** — they never ran
a BCa. `BCaWidth` for those 9 rows is the literal string `NOT_COMPUTED`. This probe does not
compute, estimate, impute or approximate a BCa for them. Doing so would manufacture a number that
no run ever produced, and it would not be comparable with the frozen 48 in any case, because it
would come from a different harness.

**D7 re-checked independently here**, by subtracting the frozen `bca` / `percentile` arrays rather
than trusting the ledger text:

- `publishedWidthField` equals the **percentile** width in **48 / 48** contrasts, the BCa width in
  **0 / 48**.
- `intervalUsed` equals the **bca** array in **48 / 48**, the percentile array in **0 / 48**.

So the published `width` describes an interval that decided nothing, and the interval that decided
every verdict had its width unpublished. Confirmed, from the artifact.

---

## 5. The `MATERIAL` three

| contrast | effect (nats) | interval used | frozen verdict | effect/floor |
|---|---|---|---|---|
| `B3 \| derived_eligible_1_to_8 \| NLPD_motor_equal \| M0_EXPONENTIAL` | −0.11364994798760097 | BCa [−0.2976329610292661, +0.033046345388860206] | `INCONCLUSIVE` | 2.706 |
| `B3 \| primary_states_0_to_8 \| NLPD_motor_equal \| M0_EXPONENTIAL` | −0.11083877217046956 | BCa [−0.2898862199167767, +0.030385869927553467] | `INCONCLUSIVE` | 2.639 |
| `FSIDE \| derived_eligible_1_to_8 \| NLPD_motor_equal \| M0_EXPONENTIAL` | +0.11529094279542929 | percentile [+0.013039958895400987, +0.22749707235626093] | `RESOLVED_ABOVE` | 2.745 |

Every material effect in this repository involves **M0_EXPONENTIAL**, and nothing else. The single
largest signal the assay contains is *"a one-parameter exponential is worse"*.

Note the first two rows: on the B3 sign convention `contrast = S(M3) - S(M0)`, a negative point
estimate means the reference `M3_TWO_TIMESCALE` scored better than `M0_EXPONENTIAL` by ~0.11 nats
— **2.7× the floor** — and the frozen BCa interval **still crossed zero**. The largest effect in
the frozen B3 NLPD set is not resolved by the frozen B3 bootstrap. That is the power limit
speaking, not the models.

---

## 6. The D10 class — frozen verdict resolved, effect below the floor

Two contrasts, both already carrying the interpretation in their own artifacts:

1. **`FSIDE | derived_eligible_1_to_8 | NLPD_motor_equal | M5_GAMMA`**
   effect `+0.031036` nats, percentile `[+0.004459…, +0.054473…]`, frozen verdict
   `RESOLVED_ABOVE`, effect/floor `0.739` → `SUB_FLOOR_EFFECT`.
   The interval reaches outside the floor on one side, so this is not `SCIENTIFICALLY_NULL`, but
   the point estimate sits below it. The resolution rests on **consistency of sign across the 19
   motors**, not on effect magnitude.

2. **`M4M6M7 | derived_eligible_1_to_8 | NLPD_motor_equal | M7_HIERARCHICAL_MOTOR`**
   effect `+2.506984e-07` nats, percentile `[+1.604451e-07, +3.374688e-07]`, frozen verdict
   `RESOLVED_ABOVE`, effect/floor `5.969e-06` → `SCIENTIFICALLY_NULL`.
   This is D10's exhibit: ~168 000× below the floor, resolved because the F-side hierarchy **is**
   M7 to numerical precision (`exp(mu)=0.6596326697…` vs M7 `k=0.6596322379…`;
   `tau=0.18372083` vs `0.18372186`). Its own artifact already carries the mandatory `WARNING`.

Both frozen verdicts are reported **verbatim and unaltered**. The reading sits beside the verdict,
never on top of it. Neither is `reportableAsAWin`.

One further row deserves naming even though its verdict did not resolve:
**`FSIDE | … | M1_WEIBULL`**, effect `+6.145101e-04`, interval
`[−0.010881…, +0.011304…]` — the *entire* interval lies inside ±0.042, so it is
`SCIENTIFICALLY_NULL` rather than merely inconclusive. Together with
**`M4M6M7 | … | M6_SEMI_MARKOV_STATE_DEPENDENT`** (`−2.803367e-03`, interval
`[−0.018990…, +0.013913…]`) these are the only two contrasts where the assay can say the
difference is small *and* bounded — which is a stronger statement than `NOT_ESTABLISHED`, and
still not a statement of sameness.

---

## 7. `underpowered` flags already present in the frozen record

The frozen B3 artifact carries its own `underpowered` boolean. It is **true in 25 of the 48**
frozen contrasts. Verbatim list:

**`derived_eligible_1_to_8`**
- `CRPS_normalized`: M0_EXPONENTIAL, M2_LOGNORMAL, M4_MIXTURE_K3, M5_GAMMA
- `CRPS_seconds`: M0_EXPONENTIAL, M4_MIXTURE_K3, M5_GAMMA
- `NLPD_motor_equal`: M0_EXPONENTIAL, M5_GAMMA, M6_SEMI_MARKOV_STATE_DEPENDENT,
  M7_HIERARCHICAL_MOTOR

**`primary_states_0_to_8`**
- `CRPS_normalized`: M0_EXPONENTIAL, M2_LOGNORMAL, M4_MIXTURE_K3, M5_GAMMA, M8_EMPIRICAL_KDE
- `CRPS_seconds`: M0_EXPONENTIAL, M2_LOGNORMAL, M4_MIXTURE_K3, M5_GAMMA, M7_HIERARCHICAL_MOTOR,
  M8_EMPIRICAL_KDE
- `NLPD_motor_equal`: M0_EXPONENTIAL, M5_GAMMA, M7_HIERARCHICAL_MOTOR

The F-side and M4/M6/M7 artifacts carry **no** `underpowered` field, so those 9 rows record
`frozenUnderpowered = NOT_COMPUTED`. Their harness reported power differently (via
`resolution.canResolve` / `atOrBelowResolutionFloor`), and this probe does not back-fill a flag
that run never emitted.

---

## 8. What a wall of sub-floor contrasts actually means

**It is a statement about the assay, not about the models.**

The binding constraint is **19 holdout motors**. The experimental unit is the MOTOR; the 233
holdout events inside them are not independent replicates. A paired motor-cluster bootstrap over
19 clusters cannot separate models that differ by a few hundredths of a nat unless the sign of the
per-motor difference happens to be near-unanimous — which is precisely how M7 "resolved" at
2.5e-07 nats and how M5_GAMMA resolved at 0.031.

Consequences that must travel with any use of this map:

- An interval containing 0 is **`NOT_ESTABLISHED`**. It is never "no difference" and never
  "equivalent". **Underpowered is not equivalence.**
- 22 of 25 nats-scale contrasts being at or below the floor does **not** rank the models. It says
  the instrument cannot separate them here.
- Replicates were not increased after seeing a width, and must not be.
- Nothing in this map is prospective. The F-side scoring rows are `NOT_SATISFIED` on prospectivity
  (D9); the M4/M6/M7 rows are `NOT_SATISFIED` and additionally `POST_HOC_EXPLORATORY`. The frozen
  B3 rows retain whatever standing their own record gives them; this probe does not re-adjudicate
  it.
- No mechanism is established by any row here. Predictive ordering on held-out durations is not
  mechanism, and this is duration-only, one dataset, one species (*E. coli*, Wadhwa 2022),
  retrospective-only.

---

## 9. Reproduction

```bash
python hierarchical-aif/scripts/build_materiality_map.py
```

Input hashes (recorded in the JSON under `inputs`):

| artifact | sha256 |
|---|---|
| `audits/phase-b/b3-model-competition-result.json` | `5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd` |
| `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` | `b3b12720f32c0aee3bfa456f52ae0901976e59e3b43c0f2690fa7a17386ab297` |
| `M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json` | `751a59ef45c8aecd1bdbe5fb5ef645423572a24d1691fb199d1b3b33fb8d4dbb` |

`audits/**` was read only; `git status --porcelain audits/` is empty after this probe.

Output sha256 of `materiality_map_all_contrasts.json` at build time:
`1aecdec94e37d402f73e821ff237e3a7af3b6c620545ba4f60eee6bdeb2e287b`.

**Self-check built into the script:** for the three M4/M6/M7 rows the re-derived
`scientificReading` is compared against the `classification` already stored in
`M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json`, and the script HALTS on any disagreement. It did not
halt — all three agree, which is evidence that the rule transcribed here is the same rule that
artifact used.

**Field additions beyond the nine requested.** Each row carries the nine required fields
(`frozenVerdict`, `effectSize`, `intervalUsed`, `BCaWidth`, `percentileWidth`, `resolutionFloor`,
`effectToFloorRatio`, `scientificReading`, `reportableAsAWin`) plus identification keys
(`contrastId`, `source`, `sourceArtifact`, `cohort`, `rule`, `units`, `reference`, `challenger`,
`signConvention`, `nHoldoutMotors`) and provenance flags (`intervalUsedValues`,
`publishedWidthField`, `scientificReadingWhy`, `frozenBeatsM3`, `frozenUnderpowered`,
`floorTransferCaveat`, `prospectivity`). The additions are identification and caveats; none of
them is a computed result.

## 10. Limitations

- The floor is a heuristic derived from one contrast on one cohort. It is not a registered margin.
- `MATERIAL` is a magnitude statement only. It carries no verdict.
- CRPS materiality is `NOT_COMPUTED` — 32 of 57 rows are therefore uncharacterised on materiality.
- BCa widths for 9 of 57 rows are `NOT_COMPUTED` and were deliberately not imputed, so BCa-vs-
  percentile width divergence cannot be assessed for the F-side or M4/M6/M7 families.
- Cross-cohort floor transfer to `primary_states_0_to_8` is flagged, not validated.
- This probe read no held-out mark channel and therefore says nothing about `nextStateN`,
  `direction` or `jump`. Any question about those is `NOT_CHECKED — would require holdout access`.

## What would make this lane true, and what would kill it

An earlier draft of this map diagnosed the assay without naming a discriminator. That is the gap
this section closes.

**The lane:** *the motor-equal held-out scoring assay can distinguish the candidate models it is
being asked to distinguish.* On the present evidence it largely cannot: of 25 NLPD-nats rows,
**3 are `MATERIAL`, 19 are `SUB_FLOOR_EFFECT` and 3 are `SCIENTIFICALLY_NULL`**, and the frozen
record already carries **25 `underpowered` flags**. Exactly **one** row is `reportableAsAWin`
(`FSIDE | derived_eligible_1_to_8 | NLPD_motor_equal | M0_EXPONENTIAL`) — beating a unit
exponential. **That is a statement about the assay, not about the models.**

**Receipt that would make the lane true.** An independent held-out cohort with enough MOTORS that
the motor-equal half-width falls below the stated floor for the contrasts that matter — so that a
real difference between `M2_LOGNORMAL`, `M4_MIXTURE_K3`, `M6_SEMI_MARKOV_STATE_DEPENDENT`,
`M7_HIERARCHICAL_MOTOR` and the F-side candidate could resolve at all. The required motor count is
**`NOT_COMPUTED` here**; the companion probe `reports/POWER-ATLAS-MOTOR-EQUAL-SCORING.md` estimates
it on **synthetic** data, and any target resolve-rate used there is `DESIGN_ONLY`. Because such a
cohort is external data, this receipt sits on `P4` transfer — **which no modelling in this
repository can close**.

**What would kill it.**

1. **The single reportable win fails to reproduce.** If, on an independent cohort, the
   F-side-over-`M0_EXPONENTIAL` contrast no longer excludes 0, the one `reportableAsAWin` row in
   this map is **withdrawn** and the assay retains no material win at all.
2. **A larger cohort still resolves nothing material.** If motor count rises substantially and the
   serious contrasts remain `SUB_FLOOR_EFFECT`, then these models are genuinely indistinguishable
   on duration alone, and discriminating evidence must come from a different channel —
   intervention, transfer, or the quarantined mark process — not from more motors.
3. **A sub-floor contrast is reported as a win anywhere downstream.** That would be D10 recurring;
   `reportableAsAWin` exists precisely to make it mechanically detectable.

**What this map cannot do:** it changes no frozen verdict, moves no P-level, and adds no claim. It
supplies the materiality reading the frozen CI rule does not.

NEXT_ACT = Derive a CRPS-units resolution floor by the same narrowest-frozen-contrast construction (narrowest BCa half-width among the 16 `CRPS_seconds` and separately the 16 `CRPS_normalized` frozen B3 contrasts), so the 32 CRPS rows currently `NOT_APPLICABLE_DIFFERENT_UNITS` can be given a units-correct materiality reading; label it `DESIGN_ONLY` and do not let it touch any frozen verdict.
