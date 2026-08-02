# Next-Gate Plan — Transfer and Intervention

**Date:** 2026-07-22 · **Gate targets:** `P4` transfer, `P5` intervention, `P6` mechanism · **Status:**
DESIGN-ONLY. This plan proposes receipts; it runs nothing, moves no P-level, and asserts no claim.

> Every threshold in this plan is `DESIGN_ONLY` unless it is a frozen criterion. The dataset in hand
> is passive *E. coli* dwell-time behaviour (Wadhwa 2022); everything below requires data this
> repository does not have.

---

## 0. Why a next gate at all — the binding constraint, measured

The corrected phase established, from two independent directions, that **the binding constraint is
data, not model math**:

- **B4C01 (assay side):** the 19-motor motor-equal design is *nesting-blind* — it cannot separate
  nested near-equivalent dwell families even under correct specification.
- **F-side + D10 (model side):** the candidate is `NOT_ESTABLISHED` against every serious adversary
  and the CI rule resolves numerically-null differences.

Re-scoring the same duration data cannot move `P4`–`P8`. The next gain requires an experiment that
makes structurally distinct hypotheses **disagree**. Strong inference: keep them all alive until a
predeclared experiment can exclude one or more.

## 1. What independent dataset would discharge P4 (transfer)?

**Requirement:** a second held-out cohort of single-motor dwell-time series, independent of Wadhwa
2022, with:
- **enough independent MOTORS** that a motor-equal contrast can resolve a real difference —
  B4C01/the power atlas indicate 19 is nesting-blind; a `DESIGN_ONLY` target is the motor count at
  which a 0.042-nat contrast resolves at ≥80% (from the synthetic power atlas, **not** yet measured
  on real data — `NOT_MEASURED`);
- a **predeclared `sha256_mod5`-style split** committed *before* any scoring (D9 discipline);
- the **same observable** (dwell duration, state, censor flag) so the frozen scoring rule transfers
  without a units change.

**What it would license:** a `P4` transfer statement — a scoped result holding on a *second* cohort.
**What it would not:** any mechanism or parity claim; transfer is necessary for `P8`, not sufficient.
**Candidate sources (design-only, unverified):** other published bead-assay / fluorescent-switch
motor datasets; a re-analysis partner. Species discipline: keep *E. coli* behavioural evidence
separate from *Salmonella*/*Bacillus* structural evidence — a structural dataset does **not**
transfer a behavioural claim.

## 2. What perturbation would make G-side policy selection testable (P5)?

**The fence, restated:** the current dataset is passive and the **action set is EMPTY** — structural,
not sample-size. `expected_free_energy` does not exist in the package and a test enforces its
absence. G stays `DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER`. This section proposes what data would
*change* that, not code to add now.

**Candidate perturbations**, each needing a manipulated variable with **recorded onset time**,
**paired pre/post on the same motors**, and enough independent motors per condition for a CI-bound
verdict (minimum N `NOT_MEASURED` — derive from a real-data power atlas once one exists):

| perturbation | manipulated variable | what it would test |
|-|-|-|
| load step | viscous load / bead size, stepped at `t_step` | does dwell-state structure respond as a policy would, or as a passive rate change |
| stator availability | stator number / MotA-MotB occupancy | does the switch reorganise under changed torque capacity |
| ion-motive force | PMF collapse/restoration | does the motor's dwell policy track its energy budget |
| recovery | time course back to baseline after any of the above | is there a return trajectory a passive model cannot produce |

**The core discriminator this must answer (§3).**

## 3. What mechanism discriminator would separate AIF-motor-stack from M2 / M4 / M7?

This is the crux and it is currently **unanswered** — stated honestly rather than filled.

The models to separate: **AIF motor-stack policy selection · M2/lognormal shape · M4/M7 hierarchy ·
three-timescale kinetics · censoring artifact.** On **passive duration data they are
near-equivalent** (F-side ≈ M7 to 2.5e-7; M2 leads; B4C01 shows the assay is nesting-blind). So no
duration-only discriminator exists — that is the measured finding, not a gap to paper over.

A discriminator must therefore live in a channel the models predict **differently**:
- **AIF policy selection predicts a response to intervention that a fixed-rate model does not** — a
  change in the *policy* (dwell-state transition structure) following a perturbation onset, beyond
  the change a passive rate model predicts from the altered load/PMF alone. **Naming a concrete,
  pre-registerable such prediction is the open design task.** If it cannot be named, G stays fenced
  and unfalsifiable here — which is itself the correct, reportable status.
- **Three-timescale kinetics vs shape** is separable with a **mark/transition** channel (the dwell
  *sequence*, not just durations) — which routes through §4.
- **Censoring artifact** is separable with a **censored-inclusive cohort** — the F-side censoring
  branch is correct-by-test but unexercised on real data (the frozen cohort excludes censored
  events).

**Honest status: no single discriminator yet separates all five on obtainable data. The plan is to
build the ones that are namable (censoring-inclusive scoring; a transition-channel likelihood after
D5/D6 repair) and to flag the AIF-vs-passive discriminator as requiring an intervention design that
does not yet have a concrete pre-registerable prediction.**

## 4. What mark-process repair is required after D5 / D6?

Detailed in `protocols/MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md`. Summary of what is owed:
- **The Wadhwa holdout mark channel is retrospective-only** (D5, burned) — a **new prospective
  split or an independent dataset** is required for any prospective mark claim.
- **The `nextStateN` range defect (D6)** must be repaired at ingest (2 holdout events carry
  `nextStateN = -1`; 15–17% of marks leave `{1..8}`) via **raw-archive re-derivation** before any
  closed-chain likelihood is valid. `marks.py` already offers strict/quarantine/retain policies; no
  silent-drop policy exists.
- **Smoothing must be predeclared** — the ledger records that the smoothing constant currently
  *flips the sign* of the result, so it must be committed before any new mark analysis.

## 5. What result would KILL the biological-parity target hypothesis?

`H_PARITY` (the target world, kept alive as a hypothesis) would be **falsified / fatally weakened** by:
- **a simple adversary winning by a CI-bound, MATERIAL margin on an independent transfer cohort** —
  e.g. M2/lognormal beating the motor-stack candidate above the resolution floor on a *second*
  dataset (not merely `NOT_ESTABLISHED`, and not sub-floor per D10);
- **an intervention showing dwell-state reorganisation fully explained by a passive rate change** —
  no policy-like signal beyond the mechanical consequence of the perturbation;
- **parameter-recovery failure on real transfer data** — the fitters biased on genuine
  out-of-distribution motors (distinct from B4C01's benign synthetic recovery);
- **irreparable mark-process invalidity** — the impossible marks proving a real ingest/model
  incompatibility rather than a fixable range-check.

## 6. What result would STRENGTHEN it?

- **A risky prospective prediction whose prospectivity is decided by the commit graph, not by
  prose (D9) — its record committed ahead of the observation, confirmed on an independent
  cohort** — the only kind of evidence that moves `P4`/`P7` and that this programme's discipline is
  built to produce.
- **An intervention discriminator where AIF policy selection predicts a response M2/M4/M7 do not, and
  the observed response matches** — the only route to a non-fenced `P5`/`P6`.
- **The censoring-inclusive cohort showing the F-side censoring branch carries real predictive
  advantage** — the one currently-untested distinctiveness of the F-side model.
- **A transition-channel likelihood (post D5/D6 repair) separating three-timescale kinetics from
  shape** on valid mark data.

None of these is achievable on the data in hand. **That is the honest boundary of this phase, and
reporting it is a legitimate scientific outcome, not an incomplete task.**

## 7. Priority order (expected information gain × obtainability)

1. **Censoring-inclusive cohort + rescore** — highest obtainability (needs only a re-derived cohort
   retaining right-censored events), directly tests the F-side model's one untested distinctiveness,
   and discriminates the censoring-artifact hypothesis. Pre-register first.
2. **Independent transfer cohort** — moves `P4`, directly relaxes B4C01's nesting-blindness. External
   data; highest scientific value.
3. **Mark-process repair (D6 raw archive) + transition-channel likelihood** — separates kinetics
   from shape; blocked on external archive.
4. **Intervention design** — moves `P5`/G-side; blocked on the open discriminator question of §3 and
   on wet-lab data.

---

`NEXT_ACT = prepare the commit (no push); present git status, files, tests, guards, hashes, and the proposed commit command to the principal`
