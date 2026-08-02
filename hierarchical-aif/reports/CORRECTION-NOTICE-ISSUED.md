# Correction Notice — Issuance Record

**Status:** `PREPARED_FOR_TRANSMISSION_BY_USER`
**Prepared:** 2026-07-21T16:39:52Z · **Marker written:** 2026-07-21T17:51:00Z
**Gate:** H-AIF-G2

> **The reviewer has NOT received this.** I do not transmit to external parties. This notice is
> prepared and hashed; the human principal sends it. Until the principal confirms transmission,
> the status stays `PREPARED_FOR_TRANSMISSION_BY_USER` and must not be reported as "issued to
> the reviewer".

---

## 1. Artifacts

| item | value |
|-|-|
| correction notice | `hierarchical-aif/reports/CORRECTION-NOTICE-TO-REVIEWER.md` |
| defect ledger | `hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md` |
| runner fix report | `hierarchical-aif/reports/H-AIF-G4-RUNNER-FIX-REPORT.md` |
| resource reclassification | `hierarchical-aif/reports/RESOURCE-BOUND-RECLASSIFICATION.md` |
| C11 paired diagnostic | `hierarchical-aif/reports/C11-PAIRED-DIAGNOSTIC-REPORT.md` |
| original package | `uni-flagellum-b3-b4-evidence-17a2f0e.zip` sha256 `ae42f203c2d156aca1d1345a27da3d522bccd6ae3bbb58cf780cef0c413087f1` |
| commit under review | `17a2f0e18c09c762ab1cefe854c0d68698803eac` |

## 2. Corrected claims summary

- **B3 leaderboard is NOT invalidated** by D1–D4 unless later evidence shows otherwise. D1 is a
  defect in a bootstrap resampling path used only by B4C11; B3's M7 fit uses the real 80-motor
  cohort with no resampling. The adverse M2-over-M3 headline stands and remains retained.
- **B4C11 U4 `U4_OK` is withdrawn.** The cluster bootstrap collapsed duplicate motor draws by
  `motorId` (80 draws → 46 groups at the declared seed).
- **The old C11 τ CI `[0.17658, 0.27020]` must not be cited.**
- **The `RESOURCE_BOUND` labels for C01/C02/C10/C11 are withdrawn**; measured runtimes are 17–29×
  lower than recorded.
- **C01/C02 were blocked** until deterministic seeding was fixed (D3). That fix is now applied in
  the corrected harness.
- **No full parity, mechanism, or active-inference-demonstrated claim is licensed.**
- Corrected full-N runs are **in progress**; no corrected result is claimed until it exists.

## 3. Ladder impact

No P-level evidence movement is created by the notice itself. It **corrects the interpretation**
of `P1`, and of `P3`/`P6` as they were represented in the prior package. `P6` is **lowered** by
the withdrawal of C11 U4. Nothing is raised.

## 4. Exact text block to send to the reviewer

```text
CORRECTION NOTICE — UNI Flagellum B3/B4 review package (commit 17a2f0e18c09c762ab1cefe854c0d68698803eac)

Since submitting the package I ran an internal read-only audit of the repository and then
independently reproduced what it found. Four defects are confirmed. Three of them affect claims in
the package you are holding. I am sending this before the corrected runs finish, because letting
the package stand unqualified while I know it contains an invalid claim would be claim laundering.

WHAT STILL STANDS
- All package integrity receipts: 43-artifact manifest, determinism re-run (f361e4dc...),
  43/43 independent-oracle agreement, preflight 46/46, plan section 7 validation baseline.
  All re-verified 2026-07-21 and unaffected by these defects.
- The B3 leaderboard and B3 held-out scoring. The defect below is in a bootstrap resampling path
  used only by B4C11; B3's M7 fit runs on the real 80-motor cohort with no resampling.
- The retained adverse headline: a simple lognormal (M2) out-predicts the two-timescale mixture
  (M3) on held-out data.
- B4 cells C03, C04, C05, C06, C07, C08 and B4C11's U2 profile.
- Your G1 objection is now closed independently: git ls-remote against the origin returns
  17a2f0e18c09c762ab1cefe854c0d68698803eac matching local HEAD, with all five anchor commits
  confirmed as ancestors of the remote branch and a pristine working tree.

WHAT DOES NOT STAND
1. B4C11 U4 "U4_OK" is WITHDRAWN. The cluster bootstrap concatenated resampled motors' events and
   then regrouped them by motorId, so a motor drawn K times collapsed into ONE group of K copies
   instead of K exchangeable groups. Reproduced at the declared seed 20260717: 80 motors drawn ->
   46 groups (42.5% cluster loss); largest group inflated 70 -> 153 events. This reaches M7's
   grouped likelihood, so a duplicated motor contributes L_m^K and its latent is over-sharpened.
   The tau CI [0.17658, 0.27020] must not be used as evidence. A paired N=5 diagnostic confirms the
   effect is material and in the direction that favoured the reported conclusion (corrected tau
   lower in 5/5 replicates, spread 1.64x wider) - that diagnostic is not a verdict.

2. The RESOURCE_BOUND justifications for B4C01/C02/C10/C11 are WITHDRAWN. Measured on the frozen
   cohort: C01 ~14.5 h (recorded 250-400 h), C02 ~8.7 h (recorded 150-250 h), C10 ~2.1 h,
   C11 ~20.1 h. Overstated by 17-29x. C10 should never have been partial. Most importantly, B4C02 -
   the HIGH-risk misspecified-world discriminator, the cell that tests whether the adverse lognormal
   result is a shape artifact - was presented as unreachable and is in fact ~8.7 h.

3. B4C01/B4C02 seeding was non-deterministic across processes (Python hash() of a generator-name
   string, PYTHONHASHSEED unset). Latent only because neither cell had ever run.

4. B4C01's recorded reason cites an "M4/M7-inclusive competition" for a cell whose code explicitly
   skips M4/M7/M8.

CLAIM IMPACT
No full parity, mechanism, or active-inference-demonstrated claim is licensed. P6
structural/mechanistic is LOWERED by the withdrawal of C11 U4. No P-level is raised.

CORRECTIVE ACTION IN PROGRESS
Old artifacts are preserved unmodified as historical evidence - nothing deleted, overwritten, or
rewritten. Reproducer tests were added before any fix. The bootstrap and seeding are fixed in an
isolated namespace. Corrected full-frozen-N runs are now executing, B4C02 first because it has the
highest epistemic value. Results will be issued under new names (B4C02_CORRECTED_FULL_RESULT.json
etc.) with an old-vs-new status table.

Please treat as superseded: HANDOFF-B3-B4.md section 5 (the C11 half), section 6 rows B4C10 and
B4C11, section 3 and section 13 items 1-2, and the corresponding outcome text in the B4 prediction
record. Everything else stands as submitted, pending your review.
```

## 5. Hash of the notice

Recorded in `hierarchical-aif/reports/CORRECTION-NOTICE.sha256`.
