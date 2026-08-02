# World-Where-Full-Bio-Parity-Is-True — Receipt Tree

**Full biological parity is not a current status. It is the target world defined by these receipts.**

> **Prospectivity caveat that travels with every receipt below (D9).** Two artifacts this tree
> leans on are pinned by defect **D9** as **`NOT_SATISFIED`** on the commit graph: **B4C10** — its
> prediction record and its result entered the repository in ONE commit (`b9b5670`), so strict
> ancestry is *structurally unattainable* and no future commit can repair it — and the **F-side
> scoring** result, whose protocol was untracked while the result already existed. Both remain
> valid **measurements**; what they cannot carry is the word `PROSPECTIVE`. Where a node below
> cites either, read it as a **retrospectively-graded** receipt. By contrast **B4C02** is
> prospective (with a recorded mid-run-commit caveat), and **B4C11** (`897c8ab`) and **B4C01**
> (`28ce738`) had their prediction records committed ahead of their results.

**Type:** BUILDER-SUPPORT ARTIFACT. This document moves no P-level, changes no frozen verdict, and
creates no claim. It answers one question per rung: *what receipt would make this rung true, and
what would kill it?*

**Authority:** the `P0..P8` definitions live in `CLAUDE.md` and are authoritative and unchanged.
This file **does not redefine them**, does not create a v2, and does not run a parallel ladder. It
is consistent with, and subordinate to,
`hierarchical-aif/ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md` and
`hierarchical-aif/docs/BIOLOGICAL-PARITY-RECEIPT-MAP.md`. Where this file and those disagree, they
win.

**Two cells are executing as this file is written.** `B4C11_CORRECTED_FULL_RESULT.json` and
`B4C01_CORRECTED_FULL_RESULT.json` **do not exist** (verified by directory listing, this session).
Their results are therefore **not in evidence**, and this document does **not** anticipate their
outcomes in either direction. Their live progress counters are telemetry and are not cited here.

---

## Reading key

| field | meaning |
|-|-|
| **current receipt** | a real artifact that exists now, with hash and status — or `NONE` |
| **missing receipt** | the artifact that does not yet exist |
| **next action** | the smallest next step that produces the missing receipt |
| **falsifier** | the observation that would show the rung is not on track |
| **what would make this rung true** | the sufficient condition, stated so it can be checked |
| **what would kill it** | the result that would close this route rather than delay it |

**In-repo** = achievable with code, compute and analysis in this repository.
**Irreducibly external** = requires data this project does not have; no amount of modelling closes it.

---

## P0 — computational integrity

| field | content |
|-|-|
| **current receipt** | `hierarchical-aif/reports/H-AIF-G1-REPO-AND-FROZEN-EVIDENCE-INTEGRITY.md` — gate `H-AIF-G1`, status **`ESTABLISHED`**. Frozen-evidence hash baseline `hierarchical-aif/reports/frozen-evidence-baseline.sha256` (**250 files**) re-verified this session against `hierarchical-aif/reports/frozen-evidence-recheck-active-flow.sha256` (250 files): `diff` is **empty — no drift**. Determinism proven byte-identical over two full executions of the F-side scoring pipeline (`F_SIDE_MOTOR_STACK_SCORING_RESULT.json`, sha256 `b3b12720f32c0aee3bfa456f52ae0901976e59e3b43c0f2690fa7a17386ab297`). Every landed result carries a hash sidecar: `B4C10_CORRECTED_FULL.sha256` = `959a00e974641eca1c0d6f3c2f7322b8c6c8411f68ca953c7e169492c4a53dde`; `B4C02_CORRECTED_FULL.sha256` = `0633988dbfd690c0c0d12075dba4e0d8c25ddd178125064bd01fbdaf4629e398`; `M4_M6_M7_PER_MOTOR_CONTRASTS.sha256` = `751a59ef45c8aecd1bdbe5fb5ef645423572a24d1691fb199d1b3b33fb8d4dbb`. Ladder-map status: **holds**. |
| **missing receipt** | (a) the same hash-sidecar + determinism treatment applied to `B4C11_CORRECTED_FULL_RESULT.json` and `B4C01_CORRECTED_FULL_RESULT.json` once they exist; (b) a clean-clone execution of the `CLAUDE.md` required-validation block for any release claim — **`NOT_RUN`** in this working tree. |
| **next action** | On each corrected run's completion, hash the result, record the command/env sidecars already staged (`*_COMMAND.txt`, `*_ENV.txt`), and re-run the 250-file frozen-evidence diff. **In-repo.** |
| **falsifier** | Any diff against the 250-file frozen baseline; any non-byte-identical re-execution of a pipeline declared deterministic; any result JSON without a matching hash sidecar. |
| **what would make this rung true** | It is already the strongest rung: pristine remote-verified repository identity, a zero-drift frozen baseline, proven determinism, and hashed artifacts. It stays true only by continuing to hold. |
| **what would kill it** | A discovered edit under `audits/**`; a seed-dependent result that does not reproduce byte-for-byte; or a rewritten history that breaks the prediction-before-result ancestry the prospectivity checks rely on. |

## P1 — equation / implementation

| field | content |
|-|-|
| **current receipt** | **Six of the nine frozen B3 models re-derived at exact-zero oracle residual.** M3, M0, M8 in `F_SIDE_MOTOR_STACK_SCORING_RESULT.json` (`b3b12720…`); M4, M6, M7 in `M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json` (`751a59ef…`, report §3 "Oracle gate — PASS, residual exactly `0.0` on all three"). The oracle shares no code with the implementation under test. Suite state at the time of writing: **470 passed, 2 skipped, 1 xfailed** (re-measured; an earlier draft carried a stale 458 from its brief without re-running). D1 (bootstrap cluster collapse) and D3 (hash-seed nondeterminism) repaired and covered by tests under `hierarchical-aif/src/motor_stack_aif/`. Ladder-map status: **repaired in new namespace**. |
| **missing receipt** | (a) exact-zero oracle re-derivation for the **remaining three** frozen models — `M1_WEIBULL`, `M2_LOGNORMAL`, `M5_GAMMA` — which would take oracle coverage from 6/9 to **9/9**; (b) D7 closure: publish the **BCa** width beside the percentile width in the reporting layer, with the honest note that **BCa intervals exist only for the 48 frozen B3 contrasts** — for the 6 F-side contrasts and the 3 M4/M6/M7 contrasts the BCa width is **`NOT_COMPUTED`**; (c) D1 closure evidence, which is blocked on the corrected C11 run. |
| **next action** | Extend the existing independent-oracle harness to M1/M2/M5 using the frozen fitted parameters (M1 `k=0.6250888335850175`; M2 `sigma=1.5783076101407152`; M5 `shape=0.5115799798433341`) and the frozen per-state `scale_N`, and assert residual against the published motor-equal NLPD. **In-repo, cheap.** |
| **falsifier** | Any of M1/M2/M5 failing to re-derive within the declared tolerance; any oracle found to import the code under test (circular); any test whose success is vacuous. |
| **what would make this rung true** | 9/9 frozen models re-derived at declared tolerance by a code-disjoint oracle, D7 width reporting corrected without re-thresholding any verdict, and D1 closed by the corrected C11 result. |
| **what would kill it** | An oracle disagreement that traces to the frozen implementation rather than to the oracle — that would put the published leaderboard, not the new namespace, in question. |

## P2 — observational

| field | content |
|-|-|
| **current receipt** | The derived cohort `derived_eligible_1_to_8` (Wadhwa 2022, *E. coli*): **80 train motors / 793 train events; 19 holdout motors / 233 holdout events**, split `sha256_mod5(motorId)==0 => holdout`, FROZEN; right-censored events excluded from the frozen cohort. For the **duration** channel this is a source-pinned recorded measurement. For the **mark** channel the receipt is **`NONE`**: `hierarchical-aif/reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md` records **2 holdout events with `nextStateN = -1`**, **5 holdout events with zero training support**, and **15–17% of marks leaving `{1..8}`** — **`QUARANTINED`**, because the raw archive needed to adjudicate them is absent. Ladder-map status: **limited**. |
| **missing receipt** | The **raw MAT archive** re-derivation that would resolve the 2 impossible marks and re-establish the mark channel's provenance. Status **`BLOCKED_EXTERNAL` — raw archive `NOT_LOCATED`** (gate `H-AIF-G8`). |
| **next action** | Obtain the raw Wadhwa 2022 archive from its source and re-derive the mark fields under a predeclared quarantine/smoothing policy written **before** the archive is opened. **Irreducibly external** to obtain; in-repo once obtained. |
| **falsifier** | The impossible marks persist after raw re-derivation (i.e. they are in the source, not the ingest); or the smoothing constant, not the data, controls the outcome — it currently **flips the sign**. |
| **what would make this rung true** | Raw-archive provenance for every field actually used in a claim, with the mark channel either repaired or explicitly excluded from claim scope. |
| **what would kill it** | The raw archive proves unobtainable **and** the derived mark fields prove unreconstructible — which would permanently confine every mark-process statement to `retrospective-only`, independent of any modelling improvement. |

## P3 — held-out predictive

| field | content |
|-|-|
| **current receipt** | Frozen B3 result `audits/phase-b/b3-model-competition-result.json`, sha256 `5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd` — 9 models × 2 cohorts × 2 rules, held-out motor-equal NLPD on the frozen split, 44/44 independent oracle, determinism byte-identical. Leaderboard leader **M2_LOGNORMAL 3.4093141566**; reference `CONTROL_CURRENT` **M3_TWO_TIMESCALE 3.4343333331**. Corrected robustness cells landed: **B4C10** (`959a00e9…`, M4 `IDENTIFIED_ON_THIS_COHORT`, U2/U3/U4 all `OK`) and **B4C02** (`0633988d…`, frozen prediction `GENERATOR-ROBUST_ADVERSE` **REFUTED**; the adverse M2-over-M3 pattern is **generator-specific**). F-side candidate scored at held-out motor-equal **3.4326923382675303**, **`NOT_ESTABLISHED`** against `CONTROL_CURRENT` and against every serious adversary (M2, M8, M1), `RESOLVED_ABOVE` only against M0 and M5; it joined the leaderboard at **5th of 10 combined** and **did not move the level**. Ladder-map status: **stands, duration-only**. |
| **missing receipt** | A candidate whose **motor-equal contrast interval lies entirely above 0 against `CONTROL_CURRENT` (M3) and against the strongest adversaries (M2_LOGNORMAL, M8_EMPIRICAL_KDE)**, with an effect **above the ~0.042-nat resolution floor** — the corrected motor-equal half-width, BCa half-width `0.04207043063262626` from the narrowest frozen B3 contrast (M4_MIXTURE_K3). Nothing in evidence meets this. |
| **next action** | Stop extending coverage of models that re-derive the incumbent and design a candidate that can beat its own `tau → 0` limit. The F-side hierarchy reproduces frozen `M7_HIERARCHICAL_MOTOR` to `2.5e-7` nats (`exp(mu)=0.659632669755436` vs M7 `k=0.6596322379287862`; `tau=0.18372082607308418` vs `0.18372185667134974`) and buys **`+0.000615` [−0.010881, +0.011304]** over `M1_WEIBULL` — `NOT_ESTABLISHED`. **In-repo to attempt; the binding limit is 19 holdout motors, which is not in-repo.** |
| **falsifier** | An adversary's contrast interval lies entirely **below** 0 against the candidate. Not observed — so the F-side duration hypothesis is **not falsified**, and equally **not supported**, against the serious competitors. |
| **what would make this rung true** | A resolved, above-floor, CI-bound win over the control **and** the strongest simple baselines, on the frozen split, scored by the frozen rule, with the win surviving the misspecified-world discriminator. |
| **what would kill it** | The 19-motor holdout is shown to be structurally unable to resolve any effect of scientifically material size — i.e. the resolution floor exceeds the largest plausible model difference. That is a **power** limit; `NOT_ESTABLISHED` is **not** equivalence, and an underpowered contrast is **never** read as "no difference". **D10** records the complementary hazard: the frozen CI rule has no minimum-effect-size guard, so a paired **motor-cluster** bootstrap can resolve a difference of *any* magnitude if its sign is consistent across motors — M7 resolved at `+2.506984e-07` nats, ~168 000× below the floor, and is reported `RESOLVED_ABOVE but SCIENTIFICALLY_NULL`. D10 was repaired by **added interpretation**, never by re-thresholding. |

## P4 — transfer  *(first unsatisfied level)*

| field | content |
|-|-|
| **current receipt** | **`NONE`.** Status `NOT_ESTABLISHED`. One study, one cohort, one apparatus, one species (*E. coli*, Wadhwa 2022). Gate `H-AIF-G8` maps here and is `NOT_LOCATED / NOT_ESTABLISHED`. |
| **missing receipt** | A **second, independent dataset** — different lab, different apparatus — with a split declared **before** the data are opened, scored by the same frozen motor-equal rule, and a CI-bound verdict on the transferred model. |
| **next action** | Locate and license an independent flagellar-motor dwell dataset; write the data-access protocol and the predeclared split first; commit the prediction record before any observation exists. **Irreducibly external.** |
| **falsifier** | The model's held-out ranking inverts on the second dataset, or its intervals widen to `NOT_ESTABLISHED` everywhere off the calibration cohort. |
| **what would make this rung true** | A model fitted on Wadhwa 2022 predicting a foreign cohort at CI-bound advantage over the same adversaries, without refitting. |
| **what would kill it** | Nothing in this repository can kill or close it. **`P4` cannot be closed by any amount of modelling, code, or analysis here** — it requires data the project does not have. That is precisely why the movable rungs (P0, P1, P3 in-repo work, P6 per scope) are worth moving: they are what a transfer dataset would arrive to test. |

## P5 — intervention

| field | content |
|-|-|
| **current receipt** | **`NONE`.** Status `NOT_ESTABLISHED`. The dataset is **passive**: the action set is **EMPTY**, and this is **STRUCTURAL, not sample-size-limited**. The G-side is fenced by a test asserting `expected_free_energy` does not exist; it is `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER`. Note the type boundary: `F` (observational free energy over beliefs) is **not** `G` (expected free energy over policies). |
| **missing receipt** | A wet-lab perturbation dataset satisfying **all three** conditions already stated in `BIOLOGICAL-PARITY-RECEIPT-MAP.md`: (1) a manipulated variable with recorded onset time, (2) paired pre/post observation on the **same** motors, (3) enough independent motors per condition for a CI-bound verdict. |
| **next action** | Specify the intervention protocol as `DESIGN_ONLY` and use `G` **only at ORCHESTRATE level** to choose the next experiment. Do not implement `expected_free_energy`. **Irreducibly external.** |
| **falsifier** | The intervention produces no measurable change in the modelled quantity, or the pre/post pairing is broken so the motor cannot serve as its own control. |
| **what would make this rung true** | A predeclared, motor-paired perturbation whose observed response falls inside the prospectively committed prediction interval. |
| **what would kill it** | Nothing here can close it. **`P5` cannot be closed by any amount of modelling, code, or analysis in this repository.** Adding a policy layer to a passive dataset would manufacture unfalsifiable scaffolding, which is why the G-side fence is a test and not a convention. |

## P6 — structural / mechanistic  *(carried per scope; no single verdict exists)*

**There is no single `P6` verdict and none may be written.** An unscoped weakening statement is a
contract violation. `P6` is carried as separate scoped statements, each with its own receipt and
its own falsifier.

| `P6` scope | current receipt | missing receipt | next action | falsifier | what would make it true | what would kill it |
|-|-|-|-|-|-|-|
| **C11 U4** (M7 dispersion stability) | **`NONE` — the prior receipt is WITHDRAWN.** D1 cluster collapse invalidated `U4_OK`. Prediction record committed ahead of observation at `897c8ab`. `B4C11_CORRECTED_FULL_RESULT.json` **does not exist** (verified by listing). | the corrected full-N C11 result, hashed | let the in-flight run finish undisturbed, then hash it and write the old-vs-new status table | the corrected cell fails, or remains inconclusive at full N | a corrected full-N result meeting the frozen U4 criterion | the corrected run shows the original `U4_OK` was an artifact of the collapse — the honest and useful outcome, already prepaid by the withdrawal |
| **Wadhwa mark-process mechanism** | **`RETROSPECTIVE-ONLY, TRANSFER-REQUIRED`** — D5 (holdout mark channel burned, `hierarchical-aif/reports/D5-HOLDOUT-MARK-CHANNEL-BURNED.md`) and D6 (`nextStateN` unchecked) | an independent **prospective** mark dataset with a predeclared smoothing/quarantine policy | write the policy first, obtain the dataset second | the smoothing constant controls the sign of the result (it currently does); transfer fails | prospective mark-channel prediction on foreign data | the mark fields prove unreconstructible and unobtainable — permanent `retrospective-only` |
| **duration-only B3/B4** | **`UNCHANGED`.** B3 (`5d7a0589e94…`) stands; the adverse M2-over-M3 headline is retained. D1 does not touch the B3 leaderboard | a mechanism discriminator that makes the competing models disagree out-of-sample | build on B4C02's finding — the adverse pattern is generator-specific (`weibull_gamma_blend` frac `0.0050`; `three_timescale_heavy_tail` frac `0.9400`; `per_motor_heterogeneous_weibull` frac `0.0050`; `gensWithM2overM3 = 1` of 3) — and design the discriminator around the generator axis that separates them | a discriminator that cannot separate the candidates on any realisable dataset size | a design under which M2 and M3 make opposite, checkable predictions, and the observation picks one | predictive superiority is promoted to mechanism — a category error the contract forbids; predictive rank is never mechanism |
| **B4C10 / M4 identifiability** | **LANDED** (`959a00e9…`, full frozen `N_boot=2000`, 1994/2000 completed): U2 collapseFrac `0.0050150451` (fires ≥0.25), U3 span `0.4332708748` decades (fires ≥2.0), U4 `omega_3` 95% CI `[0.030746372918754247, 0.28838105457744573]`; all `OK`, M4 `IDENTIFIED_ON_THIS_COHORT` | none for this scope; it is complete as scoped | do not transfer it — different model, different likelihood structure from C11 | a re-run at the frozen criteria fires any of U2/U3/U4 | it is already true **as scoped** | **identifiability is not correctness and is not mechanism**; reading it as either would kill its value, not its status |
| **full motor-stack AIF** | **`PENDING`.** Built and scored (`b3b12720…`, `751a59ef…`) but `NOT_ESTABLISHED` against control and every serious adversary; at this resolution the candidate is a re-derivation of the incumbent M7, not an advance on it | a mechanism receipt distinct from a fit receipt | see P3 next action; a model that beats its own `tau → 0` limit | the hierarchy continues to buy nothing measurable over `M1_WEIBULL` | a structural component that earns an above-floor, CI-bound, discriminating win | the constrained stack is shown to be observationally indistinguishable from the incumbent on any dataset this cohort can supply |

## P7 — independent replication

| field | content |
|-|-|
| **current receipt** | **`NONE`.** Status `NOT_ESTABLISHED`. External review is in progress and is **not** complete; review is not replication. |
| **missing receipt** | A second lab or an independent team re-executing the frozen pipeline from the recorded artifacts and reproducing the leaderboard and the verdicts. |
| **next action** | Keep the reproduction path executable from the hashed artifacts alone (command + env sidecars, frozen baseline, clean-clone validation block) so a replicator needs nothing from this session. **In-repo preparation; irreducibly external execution.** |
| **falsifier** | An independent execution produces different numbers from the same recorded artifacts, or cannot execute at all from what is published. |
| **what would make this rung true** | Independent re-derivation of the headline results, including the **adverse** M2-over-M3 result, by a party with no access to this working tree. |
| **what would kill it** | Nothing here can close it. **`P7` cannot be closed by any amount of modelling, code, or analysis in this repository.** |

## P8 — full verdict

| field | content |
|-|-|
| **current receipt** | **`FULL_PARITY = false`.** `P8` is **conjunctive**: any single required `FAIL`, `CONTRADICTED`, `NOT_ESTABLISHED`, `BLOCKED_EXTERNAL`, `NOT_RUN`, or `INVALID_PROVENANCE` makes it false. The **first unsatisfied level is `P4` transfer**. **No P-level has been raised by any work this session**; one `P6` scope (C11 U4) was **lowered** by withdrawing defective evidence. |
| **missing receipt** | `P0`–`P7` conjunctively supported, each by a named artifact, a named scope, and a carried falsifier. |
| **next action** | Work the movable rungs (P0 maintenance, P1 to 9/9 oracle coverage, P3 discriminating design, the C11/C01 `P6` scopes) while treating P4/P5/P7 as procurement problems, not modelling problems. |
| **falsifier** | Any required level remaining `NOT_ESTABLISHED` — which is the current state. |
| **what would make this rung true** | Every rung above holding **simultaneously**, on receipts, with the adverse results still retained and still visible. `P8` is reached by supplying the evidence each level requires, **never** by relabelling a gate. |
| **what would kill it** | A transfer or intervention dataset arriving and **contradicting** the model. That is a legitimate scientific outcome and would be reported as such; a manufactured pass would not be. |

---

## Critical path — ordered by expected information gain

Ordered by how much uncertainty the receipt removes and by its ability to make competing models
disagree. `IN-REPO` and `EXTERNAL` are marked so the list cannot be misread as a work queue that
this repository could finish alone.

| # | receipt | why it ranks here | achievable |
|-|-|-|-|
| 1 | **`B4C11_CORRECTED_FULL_RESULT.json`** lands and is hashed | Restores or refutes the one `P6` scope that is currently **withdrawn**. It is the only rung movement already paid for and in flight; its prediction was committed ahead of its observation (`897c8ab`). Highest information per unit of remaining work. | IN-REPO (running — do not disturb) |
| 2 | **`B4C01_CORRECTED_FULL_RESULT.json`** lands and is hashed | Second in-flight corrected cell; prediction committed at `28ce738` with **zero** observations in existence, so its prospectivity is the cleanest in the program. | IN-REPO (running — do not disturb) |
| 3 | **Oracle re-derivation of M1, M2, M5** at exact-zero residual | Takes `P1` code-disjoint verification from **6/9 to 9/9** frozen models. Cheap, bounded, and it audits the *leader* of the leaderboard (M2) — the model carrying the retained adverse headline. Auditing the leader is worth more than auditing another also-ran. | IN-REPO |
| 4 | **D7 width-reporting correction** | Publishing BCa beside percentile removes a documented reporting defect that touches **every** verdict (`intervalUsed == bca` in 48/48). Must carry that BCa is **`NOT_COMPUTED`** for the 6 F-side and 3 M4/M6/M7 contrasts. Low cost, removes ambiguity from the whole evidence base. | IN-REPO |
| 5 | **A mechanism discriminator built on the B4C02 generator axis** | B4C02 already showed the adverse M2-over-M3 result is **generator-specific**, so "it is just heavy-tailed shape" is no longer an adequate account. This is the single highest-value *design* item: it is the receipt most able to make competing models disagree. Any threshold introduced for the design is **`DESIGN_ONLY`** and not evidential. | IN-REPO to design; the discriminating **observation** is EXTERNAL |
| 6 | **Raw MAT archive re-derivation** | Closes D6 (2 impossible marks, 5 zero-support holdout cells, 15–17% out-of-range marks) and is the only route to a mark-channel `P2` receipt. Blocked on obtaining the archive. | EXTERNAL to obtain |
| 7 | **An independent dataset with a predeclared split** | Closes the **first unsatisfied level**, `P4`. Ranked below items 1–5 only because none of this repository's work can produce it; ranked above P5/P7 because it is the binding constraint on `P8` and because it also unblocks the mark-process `P6` scope. | **IRREDUCIBLY EXTERNAL** |
| 8 | **A motor-paired intervention dataset** | The only route to `P5`, and the only thing that converts the G-side from `DESIGN_ONLY` to scoreable. The action set is empty for structural reasons, so no in-repo work substitutes. | **IRREDUCIBLY EXTERNAL** |
| 9 | **Independent replication by a second party** | The only route to `P7`. Preparation is in-repo (reproduction must run from hashed artifacts alone); execution is not. | **IRREDUCIBLY EXTERNAL** |

**The honest shape of this path:** items 1–4 are finishable here and move receipts, not levels.
Item 5 is where in-repo effort has the highest scientific leverage, and it still terminates in an
observation this project does not own. Items 7–9 are the levels that decide `P8`, and **they cannot
be closed by any amount of modelling, code, or analysis in this repository.** Saying so plainly is
what makes items 1–5 worth doing: they are the state in which an external dataset would arrive and
find a model already worth testing.

---

```text
Nature supplies the architecture candidate. The gate supplies the status.
Full biological parity is not a current status. It is the target world defined by these receipts.
```

NEXT_ACT = Run `python hierarchical-aif/src/motor_stack_aif/claim_guard.py hierarchical-aif/docs/WORLD-WHERE-FULL-BIO-PARITY-IS-TRUE-RECEIPT-TREE.md`, then leave the two in-flight corrected cells undisturbed and take critical-path item 3 — extend the code-disjoint oracle to M1_WEIBULL, M2_LOGNORMAL and M5_GAMMA to bring P1 oracle coverage from 6/9 to 9/9 frozen models.
