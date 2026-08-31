# P4-TRANSFER Data Access Protocol

**Status: DOOR PREPARED, NOT PASSED.** This document is the acquisition protocol for the lab-B
cohort that Door P4 — TRANSFER requires. It is named by the checklist itself
(`docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:85-88`, "the `<TASK>-DATA-ACCESS-PROTOCOL.md`").

**What this document does NOT claim.** It relabels no gate (`X10` stays `NOT_ESTABLISHED`,
`H-AIF-G8` stays `NOT_LOCATED`, `G08` stays `BLOCKED_EXTERNAL`). It registers no cohort. No
lab-B data has been requested, received, or read as of 2026-08-30. The lab-A (Wadhwa 2022)
holdout is **SPENT** (duration spent by B3; mark channel burned, D5) and nothing in this protocol
touches it. Adverse first: the single hard external blocker on this door is that **no independent
second stator-dwell dataset exists in the repo** (`docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:80-83`),
and this document cannot remove that blocker — only a real data release can.

Frozen counterpart: `experiments/predictions/P4-TRANSFER-PREDICTION-RECORD.v1.json` (the
declarations this protocol feeds). Acceptance criterion, verbatim
(`experiments/cross-study-preregistration.v1.json:107-109`):

> "At least one mechanistic parameterization frozen on one laboratory/study predicts a second
> laboratory's commensurate raw observations with a predeclared advantage over baselines.
> Source-paper predictions or unit-incompatible mappings do not count."

---

## 1. What is requested from each candidate lab

The same five things from every lab, because the frozen scoring rule needs all five
(`docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:41-56, 73-78`):

1. **Dwell state** — integer stator occupancy (or the lab's recorded state variable, with its
   observation operator declared so the units axis can be assessed honestly).
2. **Dwell duration** — per event, in seconds, with the censoring flag (`rightCensored`).
3. **Transition target** — the next-state record. NOTE: the mark channel is under D5/D6
   quarantine in-repo; transition targets are requested so the cohort is complete and future
   mark-process work is possible, but the P4 duration-only claim never reads them.
4. **Motor identities** — a stable per-motor identifier on every event. Without motor identities
   the cohort is unusable: the experimental unit is the MOTOR, and frames or events are never
   independent replicates (CLAUDE.md truth contract; `score.py` motor-equal aggregation).
5. **Calibration release** — the instrument calibration published with the raw data, so
   `OBSERVED` is earned (`docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:51`).

Candidate labs and their standing caveats (from the checklist, `:73-78`):

| candidate | caveat |
|---|---|
| Nord 2017 | natural target; must be made commensurate on all six axes |
| Perez-Carrasco 2022 | natural target (load axis is the work) |
| Antani 2021 | natural target (switching) |
| Ito 2021 | 4.09 GB Class-A archive integrity-verified in-repo, but **one lab, not a transfer pair** — it cannot alone satisfy X10 |
| Wadhwa 2022 | **EXCLUDED. Holdout spent (D5). It is lab A and can never be lab B.** |

## 2. Licence terms that are acceptable

- The licence **must permit**: (a) recording a committed SHA-256 of the received archive in this
  repository, and (b) publishing derived scoring artifacts (per-motor NLPD arrays, contrasts,
  verdicts) computed from the data.
- The licence **need not permit** redistribution of the raw data. The repo commits hashes and
  derived scores, not the bytes. A no-redistribution licence is acceptable; a
  no-derived-publication licence is not.
- A licence that forbids naming the source lab in the verdict is not acceptable: provenance is
  part of the claim.

## 3. Who signs

**The operator signs. Agents draft, never sign.** Data-access requests, licence acceptances, and
the per-axis commensurability sign-off are operator actions (the transcription-not-judgement
seam: agents may prepare every clerical artifact — the request letter, the axis-by-axis evidence
table with locators, the hash manifest — but the judgement that a cohort is commensurate, and any
outbound commitment to an external party, carries the operator's signature).

## 4. Intake steps (in order; the order is the protocol)

1. **Verify the prerequisite commits exist.** The prediction record
   (`experiments/predictions/P4-TRANSFER-PREDICTION-RECORD.v1.json`) and the committed
   **real-data power-atlas derivation of N** (motor-count target; the existing
   `hierarchical-aif/results/motor_stack_aif/power_atlas.json` is SYNTHETIC by its own
   `truthLabel` and does not qualify) must both be committed **before any lab-B field is read**.
   Prospectivity is decided by the commit graph (`docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md:59-61`).
2. **Hash before reading.** On receipt, compute the archive SHA-256 and register it in
   `labBRegistration.cohortSha256` of the prediction record — **before any field of the data is
   read**. The registering commit must be a strict descendant of the commits in step 1.
3. **Assess commensurability from released metadata only** (papers, methods sections,
   calibration documents — not the event data). Produce the six-axis evidence table (agent
   draft, verbatim quotes with locators). Operator signs each axis or refuses.
4. **Refusal is a first-class outcome.** A cohort failing any axis is registered in the
   prediction record as **`REFUSED-INCOMMENSURATE`** with the failing axis named, and is never
   coerced — forcing a common coefficient across incompatible assays is forbidden, and is the
   exact axis on which the current corpus already fails
   (`cross-study-parity-report.json:653`; checklist `:52-55`).
5. **Quarantine on ingest, per the existing tested machinery.** Ingest validation reuses the
   built range-check and quarantine policy, not new code:
   - `hierarchical-aif/src/motor_stack_aif/marks.py:63-92` — `prepare_mark_dataset(policy="quarantine")`
     keeps/quarantines with `quarantineReason` per row and never silently drops;
   - `hierarchical-aif/src/motor_stack_aif/events.py:21-83` — the `mark_quarantine` mode enforces
     D5/D6 at the type level;
   - tested by `hierarchical-aif/tests/motor_stack_aif/test_nextstate_range_check.py:60-66`
     (quarantine preserves, labels, and conserves counts: `kept + quarantined == all`).
   The duration channel of a defective row is quarantined with the row, never repaired by hand.
6. **Score once.** Only after registration is complete does
   `experiments/predictions/p4_transfer_harness.py` run — it refuses unregistered hashes and
   refuses a still-empty registration by construction. One scoring run per registered sha256;
   re-execution is for determinism checking only and must be byte-identical.
7. **Report whatever comes out.** All three falsifiers are legitimate reportable negatives;
   none may be tuned away. An underpowered cohort (below the derived N) is scored anyway and
   reported `UNDERPOWERED` at its actual interval width.

## 5. What would end this protocol

Receipt and registration of one commensurate cohort ends the acquisition phase; the scoring run
ends the door attempt, in either direction. A refusal on every candidate is also an honest
terminal state: it would leave X10 `NOT_ESTABLISHED` with the reason named per candidate, which
is a better record than a coerced pass.
