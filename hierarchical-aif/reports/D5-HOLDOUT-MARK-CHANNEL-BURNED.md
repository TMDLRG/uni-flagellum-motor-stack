# D5 — Held-Out Mark Channel Burned

**Defect:** `D5_HOLDOUT_MARK_CHANNEL_BURNED` · **Date:** 2026-07-21 · **Gate:** H-AIF-G2
**Status:** `VERIFIED_IRREVERSIBLE` · **Class:** **process defect, not a biological result**
**Cause:** the builder (me). Not the reviewer, not a subagent acting outside its brief.

---

## 1. What happened

While running UltraCode design tracks in parallel with the corrected B4 runs, I briefed a
read-only track (Track C) to plan how the mark process — `nextStateN`, `direction`, `jump` — could
be integrated into a motor-stack likelihood.

To answer that brief the agent read the mark fields **on the 19 holdout motors**, computed
per-state mark marginals, and ran a held-out contrast (pooled vs state-conditional transition
kernel, motor-equal NLPD, 2000-replicate motor-cluster bootstrap, four smoothing constants).

No file was written. No frozen artifact was touched. The agent obeyed its brief exactly. **The
channel was destroyed anyway**, because reading held-out data is itself the irreversible act.

## 2. The exact instruction that caused it

From my Track C brief:

> "1. What are the empirical marginals of direction/jump per state? How many events have a
> non-null mark? What happens at state boundaries (state 0, state 11)?"

That question has no train/holdout qualifier. It asks for marginals of the whole dataset. A
competent agent answering it will read the holdout. **The brief contained no split boundary, no
forbidden-field list, and no data-access protocol.** That omission is the root cause.

## 3. Fields burned

| field | split | status |
|-|-|-|
| `nextStateN` | holdout | **BURNED** — retrospective/exploratory only |
| `jump` | holdout | **BURNED** — retrospective/exploratory only |
| joint `(N, N')` transition structure | holdout | **BURNED** |

## 4. Fields already spent BEFORE D5 (not attributable to this incident)

| field | split | spent by |
|-|-|-|
| `durationS` | holdout | B2/B3 held-out scoring — **legitimately**, under a committed prospective record (`e5b4969` preceded `9f24848`) |
| `stateN` | holdout | cohort eligibility, per-state scale normalisation, B4C07 |
| `rightCensored` | holdout | cohort construction; B4C05 censoring sensitivity |
| `direction` | holdout | the pre-existing competing-risks first-passage likelihood (`lib/source-first-passage.js:59-65`, `scripts/run-science-gates.py:104-115,181-197`) |

I initially assumed the mark was entirely unused. That was **wrong**: `direction` had already been
consumed by a committed gate. Only the mark *magnitude* (`nextStateN`, `jump`) was unspent, and
that is precisely what D5 destroyed.

## 5. What is unaffected

- **B3 duration scoring is unaffected.** B3 reads `durationS`, `stateN`, `rightCensored` only. It
  never reads the mark (`b3-model-competition-runner.py:109-110` filters on `rightCensored` and
  `stateN`). The leaderboard, the adverse M2-over-M3 headline, and every B3 interval stand.
- **The corrected B4 runs are unaffected.** B4C02, B4C10, B4C11 and B4C01 read no mark field.
  The runs currently executing are not contaminated.
- **All B4 cells C03–C08 are unaffected.**
- **Package integrity receipts are unaffected.**
- **D1–D4 findings are unaffected.**

## 6. What is now retrospective only

Any mark-process model on Wadhwa-2022 — transition kernels, direction/jump-bearing likelihoods,
mark-conditioned hazards, or any motor-stack `Lmotor-0` term including
`p(N', direction, jump | ...)` — must be labelled:

```text
RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET
```

Such work is still permitted and still useful. It simply cannot be presented as prospective
held-out evidence, and cannot move `P3` on that basis.

## 7. Claim impact

- No claim moves up. No P-level rises.
- Prospective mark-process **mechanism** evidence now requires an independent dataset with a new
  prospective split.
- **D5 is a process defect, not a biological result.** It says nothing whatsoever about flagellar
  motors. It is a statement about how this laboratory handled its own evidence.

**Mitigating fact, recorded but not offered as an excuse:** the held-out contrast the track ran
came back `NOT_ESTABLISHED` — the CI crossed zero at every smoothing constant α ∈ {0.1, 0.5, 1.0,
2.0}, and the point estimate **changed sign** between α = 0.1 and α = 0.5. The channel had very
little resolving power at 19 holdout motors. That bounds the practical cost of the loss. It does
not undo it, and it would not have excused the omission had the result been decisive.

## 8. Existing P-level impact

| level | effect |
|-|-|
| `P3` held-out predictive | **Limited for the mark channel only.** Duration-based held-out evidence is untouched. |
| `P6` structural/mechanistic | **Weakened.** A mark-process mechanism claim can no longer be established prospectively on this dataset. Combined with the withdrawal of C11 U4, `P6` is weaker than the submitted package represented. |
| `P4` transfer | **Requirement strengthened** — now also the only route to prospective mark evidence. |
| `P7` independent replication | **Requirement strengthened**, same reason. |

No level rises. `P8` unchanged: `FULL_PARITY = false`.

## 9. Process rule added (now binding)

> **Any brief that could cause an agent to read held-out data must declare the split explicitly
> and restrict analysis to the training partition, unless a prospective record is committed
> first.**

Supporting machinery, now in force:

1. `hierarchical-aif/docs/DATA-CHANNEL-SPEND-LEDGER.md` — every field × split, who spent it, what
   it can still support.
2. A mandatory split-boundary label on every analysis, from a fixed vocabulary.
3. `hierarchical-aif/protocols/<TASK>-DATA-ACCESS-PROTOCOL.md` required before any task that might
   touch held-out fields — declaring fields to read, split, forbidden fields, claim boundary,
   prospective status, falsifier, stop condition.
4. The D5 firewall text is now pasted verbatim into every subagent brief that touches this
   repository, instructing agents to answer `NOT_CHECKED — would require holdout access` rather
   than read. That answer is explicitly framed as correct and valuable, never a failure.

## 10. Future prevention

- The firewall clause was applied immediately to the Track D/E/F verification workflow launched
  after D5 was discovered.
- Verification agents are now required to emit a split-boundary label on every claim.
- Recommended follow-on (not yet built): a check that greps analysis scripts under
  `hierarchical-aif/` for reads of `partition == "holdout"` and fails unless a matching
  `-DATA-ACCESS-PROTOCOL.md` exists.

## 11. Honest summary

I built a firewall **after** driving through the wall. The rule in §9 is the rule that would have
prevented this, and it did not exist because I did not think to write it until an agent had
already spent the channel. The loss is permanent within this dataset, it is bounded, and it is
recorded here rather than absorbed.
