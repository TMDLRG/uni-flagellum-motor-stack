# Correction Notice — UNI Flagellum B3/B4 Review Package

**Issued:** 2026-07-21T16:39:52Z
**Issued against:** commit `17a2f0e18c09c762ab1cefe854c0d68698803eac` (branch `phase-2/b3-model-competition`)
**Original package:** `uni-flagellum-b3-b4-evidence-17a2f0e.zip`, sha256
`ae42f203c2d156aca1d1345a27da3d522bccd6ae3bbb58cf780cef0c413087f1`
**Correction work branch:** `hierarchical-aif/motor-stack`
**Gate:** H-AIF-G2

> **Provenance note.** This work was originally requested as Phase-C closure work, but was
> namespaced under `hierarchical-aif/` to avoid collision with frozen `audits/phase-c/` evidence.
> The frozen Phase-C audits remain read-only source evidence.

---

## 1. Status

The package previously submitted for review is **corrected in place by this notice**. It is not
deleted and not silently replaced. It remains a historical artifact, but parts of its B4
interpretation are invalidated.

```text
The previously submitted package is not withdrawn for all purposes, but its B4 robustness
interpretation is corrected.

B3 leaderboard: still standing unless later evidence changes it.
B4 C11 U4: invalidated by verified cluster-collapse bootstrap defect.
B4 resource-bound labels for C01/C02/C10/C11: invalidated / require correction.
B4 C01/C02 future runs: blocked until deterministic seeding is fixed.
Full parity / mechanism claims: not licensed.
```

These defects were found by an internal read-only audit of the repository against a stacked
active-inference specification, and were then **independently reproduced and verified** before
this notice was issued. They were not reported by the reviewer.

---

## 2. What still stands

- **Package integrity receipts remain valid historical receipts.** The 43-artifact manifest,
  the determinism re-run (`f361e4dc…`), the 43/43 independent-oracle agreement, the live-remote
  ancestry proofs, and the plan §7 validation baseline were all re-verified at H-AIF-G1 on
  2026-07-21 and are unaffected by D1–D4.
- **The B3 leaderboard and B3 held-out scoring are not invalidated** by D1–D4 unless later
  evidence shows otherwise. D1 is a defect in a *bootstrap resampling* path used only by B4C11;
  B3's own M7 fit runs on the real 80-motor cohort with no resampling. The adverse headline —
  a simple lognormal (M2) out-predicting the two-timescale mixture (M3) on held-out data — is
  untouched and remains the retained headline.
- **B4C11 U2** (the 61-point τ profile) is unaffected: it runs on the real cohort at the full
  frozen contract, not on bootstrap replicates.
- **B4C11 U1 and U3** derive from B3 and are unaffected.
- **B4C10's bootstrap method is sound.** M4 is fitted on the flat pooled `train_y`, so duplicate
  motors enter correctly — it is a valid motor-cluster bootstrap. Only its *replicate count* and
  its *resource justification* are at issue (see D2).
- **The current-design control remains available and runnable.**

---

## 3. What does not stand

### D1 — B4C11 U4 `U4_OK` does not stand

The C11 U4 bootstrap resamples motors with replacement, concatenates the sampled motors' events
into a flat list, and rebuilds the cohort. `Cohort` groups training events into `train_by_motor`
**keyed by `motorId`**, so a motor drawn K times collapses into **one** group holding K copies of
its events instead of K separate exchangeable groups.

Reproduced at the declared `seed_base = 20260717`:

| b | motors drawn | distinct motors | `train_by_motor` groups | train events |
|-|-|-|-|-|
| 0 | 80 | 46 | **46** | 795 |
| 1 | 80 | 53 | **53** | 628 |
| 2 | 80 | 52 | **52** | 818 |
| 3 | 80 | 59 | **59** | 831 |
| 4 | 80 | 56 | **56** | 840 |

- Group count equals the number of **distinct** motors exactly → duplicates collapse.
- Cluster loss at b=0: **42.5%** (80 intended → 46 actual exchangeable clusters).
- Largest group inflates **70 → 153 events** (a 51-event motor drawn 3×).
- Theoretical `E[distinct] = 80(1-(1-1/80)^80) = 50.8`, consistent with the observed range.

This reaches M7's likelihood: `m7_train_nll(k, tau, train_by_motor)` iterates
`for ym in train_by_motor`, and `_fit_m7_reduced` consumes `coh.train_by_motor`. A motor drawn K
times therefore contributes `L_m^K`, over-sharpening that motor's latent while the number of
exchangeable clusters silently drops by roughly 40%.

**The direction of bias is an inference, not a measurement, but it plainly favours the conclusion
that was reported** ("τ is well determined").

Consequently:
- the reported **`U4_OK` verdict does not stand**;
- the reported **τ bootstrap CI `[0.17658259553140288, 0.27020046374673834]` must not be used
  as evidence** about between-motor dispersion;
- the `collapseFraction_tau_lt_1e_3 = 0` result from the defective runner must not be cited;
- the B4 headline sentence "B4C11 … U4 at 30 of 2000 replicates 0/30 collapsed (U4_OK)" is
  **withdrawn**;
- the C11 contribution to `M7_status = IDENTIFIED_ON_THIS_COHORT (U1/U2/U3/U4 all OK)` is
  **reduced to U1/U2/U3 only**, and the aggregate status is **NOT_ESTABLISHED** pending a
  corrected full run.

### D2 — B4 `RESOURCE_BOUND` labels are not reliable

Measured on the frozen cohort on the builder's machine:

| step | measured |
|-|-|
| `fit_simple_models` | 32.0 s |
| `fit_m6` | 20.1 s |
| C01/C02 per-simulation (simple + M6 only) | **52.1 s** |
| `_fit_m4_reduced` | **3.8 s** |
| `_fit_m7_reduced` | **36.2 s** |

Projected against frozen N versus what was recorded:

| cell | frozen N | measured projection | recorded claim | ratio |
|-|-|-|-|-|
| B4C01 | 1000 | **14.5 h** | 250–400 h, `NOT_RUN` | ~17–28× overstated |
| B4C02 | 600 | **8.7 h** | 150–250 h, `NOT_RUN` | ~17–29× overstated |
| B4C10 | 2000 | **2.1 h** | ran 100/2000 as partial | should never have been partial |
| B4C11 | 2000 | **20.1 h** | ran 30/2000 as partial | no per-cell figure was recorded |

A `RESOURCE_BOUND` status is only honest if the resource claim is true. Three of these are wrong
by more than an order of magnitude, which converted recoverable gates into permanent-looking
`NOT_RUN`s and **understated how much of B4 was actually within reach.** This is a truth-contract
issue, not a scheduling one.

**B4C02 is the most consequential instance:** it is the HIGH-risk misspecified-world discriminator
— the cell designed to test whether the adverse lognormal result is a feature of heavy-tailed
dwell shape rather than of one assumed mechanism. It was reported unrunnable at 150–250 h. It is
approximately **8.7 h**. The single most decisive piece of missing evidence in the submission was
reachable and was not attempted.

### D3 — B4C01/B4C02 seeding is non-deterministic across processes

Both cells seed via `np.random.default_rng(seed_base + sim + hash(gen) % 100000)`. CPython
randomizes `str` hashing per process and `PYTHONHASHSEED` is unset. Three consecutive processes
produced seeds `14565/95125`, `59809/55025`, `89866/26054` for the same two generator strings.

Any future C01/C02 result would be unreproducible byte-for-byte and could never satisfy the
protocol's own determinism discipline. The defect is **latent only because those cells were never
executed**. C01/C02 must not be run until this is fixed.

### D4 — B4C01's recorded reason misdescribes what the cell computes

The recorded reason states `"~15-25 min per M4/M7-inclusive competition"`, but the cell's own code
explicitly skips those models (`"skip M4/M7/M8 as they are the slow ones"`), and the cell records
`"skippedModels": ["M4_MIXTURE_K3", "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE"]`. The stated
justification does not describe the implemented computation. This is a provenance-integrity
defect in the recorded reason text, independent of the arithmetic error in D2.

---

## 4. Claim impact

```text
No full parity claim is licensed.
No biological equivalence claim is licensed.
No active-inference-demonstrated claim is licensed.
No mechanism claim is licensed from the invalidated cells.
B4 must be rerun where affected.
```

Mapping onto the **existing, unchanged** `P0–P8` ladder in `CLAUDE.md`:

| defect | existing P-level affected | effect |
|-|-|-|
| D1 | `P1` equation/implementation; `P3`/`P6` interpretation for C11 U4 | C11 U4 evidence withdrawn |
| D2 | `P0`/`P1` provenance and resource-status credibility for not-run/partial cells | statuses require reclassification |
| D3 | `P1` implementation integrity for future C01/C02 runs | blocks those runs until fixed |
| D4 | documentation/provenance integrity | recorded reason corrected in new reports only |

**No `P8` movement. No parity level rises as a result of this notice.** The pre-existing repository
verdicts are unchanged: cross-study `X16_FULL_BIOLOGICAL_PARITY = FAIL`; science-gates overall
`PARTIAL_PARITY_ONLY`.

---

## 5. Corrective action

The repository will, in this order:

1. preserve all old artifacts unmodified as historical evidence (**no deletion, no overwrite, no
   history rewrite**);
2. add failing reproducer tests for D1 and D3 **before** any fix;
3. fix the C11 cluster-bootstrap semantics so that K draws of a motor yield K exchangeable groups
   — an implementation fix to match the frozen protocol's intended cluster-bootstrap semantics,
   **not** a change to the frozen scientific protocol;
4. replace `hash()` seeding with a stable SHA-256-derived seed;
5. reclassify the resource-bound cells from measured runtime;
6. re-run the feasible cells at **full frozen N** on the corrected runner, under new corrected
   artifact names that do not overwrite the originals;
7. issue a corrected handoff package with an old-vs-new status table.

Corrected results will be written to `B4C10_CORRECTED_FULL_RESULT.json`,
`B4C11_CORRECTED_FULL_RESULT.json`, `B4C02_CORRECTED_FULL_RESULT.json`, and
`B4C01_CORRECTED_FULL_RESULT.json`. **No corrected result is claimed until its corrected run
exists.**

---

## 6. Instruction to the reviewer

Please treat the following sections of the submitted package as **superseded by this notice**:

- `HANDOFF-B3-B4.md` §5 bullet "B4C10 / B4C11 REFUTE weak-identification prediction on partial
  replicates" — the C11 half is withdrawn;
- `HANDOFF-B3-B4.md` §6 rows B4C10 and B4C11;
- `HANDOFF-B3-B4.md` §3 and §13 items 1–2 (the `RESOURCE_BOUND` and partial-replicate
  justifications);
- the corresponding `outcome.headline`, `outcome.resourceBoundLimitations`, and
  `outcome.notEstablished` text in
  `experiments/predictions/b4-identifiability-robustness.prediction.json`.

Everything else in the package — B3, the integrity receipts, C03/C04/C05/C06/C07/C08, and the
declared limitations — stands as submitted pending your review.

The reviewer's own G1 objection (that the git proofs were a text dump rather than live-repository
verification) has since been closed independently: `git ls-remote` against the origin returns
`17a2f0e18c09c762ab1cefe854c0d68698803eac`, matching local HEAD, with all five anchor commits
confirmed as ancestors of the remote branch and a pristine working tree. See
`H-AIF-G1-REPO-AND-FROZEN-EVIDENCE-INTEGRITY.md`.
