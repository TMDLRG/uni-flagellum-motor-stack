# Subagent Brief Template

**Paste §1 verbatim into every subagent brief that touches this repository.** Defect D5 happened
because a brief omitted it.

---

## 1. D5 HELD-OUT DATA FIREWALL — paste verbatim

```text
=========================  D5 HELD-OUT DATA FIREWALL  =========================
A prior read-only audit track was asked for "empirical marginals of direction/jump per state" and,
in answering, READ THE HELD-OUT MARK CHANNEL. That permanently burned it: no future mark-process
claim on Wadhwa-2022 can ever be labelled PROSPECTIVE. Reading held-out data is IRREVERSIBLE.
Read-only is NOT consequence-free.

BINDING RULES FOR YOU:
1. You may read CODE freely (any .py/.js/.ts/.md/.json under audits/, scripts/, lib/, app/,
   hierarchical-aif/).
2. You may read RECORDED RESULT ARTIFACTS freely (audits/phase-b/*result*.json) - those are
   already-spent, published numbers.
3. You MUST NOT compute any new statistic, table, marginal, correlation, plot, or model fit over
   experiments/data/wadhwa-2022-events.json rows whose partition == "holdout".
4. If a verification would require touching holdout rows, DO NOT DO IT. Instead report:
   "NOT_CHECKED - would require holdout access; requires prospective record first."
   That is a CORRECT and VALUABLE answer here. It is never a failure.
5. TRAIN-partition reads are permitted where genuinely necessary, but say so explicitly and
   declare the split boundary of anything you compute.
Every claim you emit must carry a split-boundary label from:
   TRAIN_ONLY | HOLDOUT_ALREADY_SPENT_DURATION_ONLY | HOLDOUT_ALREADY_SPENT_DIRECTION |
   HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY | INDEPENDENT_TRANSFER_REQUIRED |
   PROSPECTIVE_NEW_DATA_ONLY | NO_DATA_ACCESS_NEEDED
===============================================================================
```

## 2. Contract block — paste verbatim

```text
CONTRACT:
- audits/phase-c/**, audits/phase-d/**, audits/phase-b/** are FROZEN read-only. Never edit.
- Existing parity ladder P0..P8 in CLAUDE.md is authoritative and must NOT be redefined:
  P0 computational integrity, P1 equation/implementation, P2 observational, P3 held-out predictive,
  P4 transfer, P5 intervention, P6 structural/mechanistic, P7 independent replication, P8 full verdict.
  P8 is conjunctive and currently false.
- FORBIDDEN language: "biological parity achieved", "active inference demonstrated", "flagellum
  solved", "general intelligence", "awareness achieved", "M2 is the UNI model", "G proves motor
  agency". A design document is NOT evidence and raises NO P-level.
- M2_LOGNORMAL is an ADVERSARIAL BASELINE. It currently out-predicts the two-timescale mixture M3
  on held-out data - a retained adverse result.
- Experimental unit is the MOTOR: 80 training / 19 holdout motors. Bootstraps resample MOTORS.
  Underpowered is NOT equivalence. Point estimates are never verdicts; CI-bound only.
- No floor anywhere: a non-finite log density HALTS.
```

## 3. Verification status vocabulary — require it

```text
CHECKED_AGAINST_CODE      - you opened the file and confirmed it
CHECKED_AGAINST_RESULTS   - confirmed against a recorded result artifact
REPORTED_BY_TRACK         - asserted by a prior track; you did not verify
NOT_CHECKED               - not verified (say why; holdout-blocked counts here)
CONTRADICTED              - you checked and the prior claim is WRONG (say what is actually true)
```

State explicitly: *"Being adversarial is the job. A CONTRADICTED finding is the most valuable
output you can produce."* This is what surfaced D7 and the Track D ranking error.

## 4. Established facts to hand the agent

```text
- F, G, policy layer, policy priors E, sensory precision Pi, up/down messages are ABSENT from the
  science pipeline. All 9 B3 models are MLE density fits; none computes F or G.
- M6_SEMI_MARKOV is NOT semi-Markov: 8 independent per-state Weibull fits, no transition kernel.
  nextStateN/direction/jump exist in the data and are never read by B3.
- Verified defects D1-D7 - see ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md.
- The recorded `width` field is the PERCENTILE companion width, not the BCa/intervalUsed width (D7).
  Narrowest motor-equal contrast is M4 at 0.083461; resolution floor is ~0.042 nats.
- One study only (Wadhwa 2022). No transfer dataset. Raw MAT archive ABSENT.
```

## 5. Builder-side rules when spawning agents

1. **Never** ask for "marginals", "distributions", "summary statistics", or "what does the data
   look like" without naming the partition. That phrasing is what caused D5.
2. If a task might touch held-out fields, write `protocols/<TASK>-DATA-ACCESS-PROTOCOL.md` first:
   fields to read, split, forbidden fields, claim boundary, prospective status, falsifier, stop
   condition.
3. **Verify a subagent's consequential claims yourself before repeating them.** Track D's headline
   survived; six of its receipts did not.
4. When two independent computations disagree, **investigate the disagreement** — do not pick one.
   That is how D7 was found.
5. Keep spawn counts low and briefs precise. A vague brief is a live hazard, not merely inefficient.
