# Mark-Process Transfer Rescue Protocol

**Type:** BUILDER-SUPPORT DESIGN PROTOCOL. **This document moves no P-level, changes no frozen
verdict, and creates no claim.** It answers one question: *what receipt would make the mark-process
lane true, and what would kill it?*
**Lane:** LANE C (mark process). **Gate touched:** H-AIF-G8 (design only).
**Split boundary of this document:** `NO_DATA_ACCESS_NEEDED` — no dataset field was read to write
it. Every quantity below is quoted from an existing recorded artifact.
**D5 firewall compliance:** held-out `nextStateN`, `direction` and `jump` were **not** read while
writing this protocol. Everything cited comes from `reports/D5-HOLDOUT-MARK-CHANNEL-BURNED.md`,
`reports/D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md`, `docs/DATA-CHANNEL-SPEND-LEDGER.md` and
`ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md`.

---

## 0. Status, stated up front

D5 and D6 do not kill the mark process. They **reclassify** it. The three standing statements:

1. **Wadhwa-2022 `nextStateN` / `jump` mark claims are `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET`
   — retrospective-only on this dataset.** The held-out mark channel was spent by a read-only
   audit track (D5) with no prospective record in existence at the time. Reading is the
   irreversible act; nothing was written and the channel was destroyed anyway.
2. **A prospective mark-mechanism receipt now requires transfer or a new split
   (`INDEPENDENT_TRANSFER_REQUIRED`).** This dataset is one study with one holdout partition and
   there is no second holdout to spend. No modelling in this repository can supply it.
3. **The closed mark chain is `BLOCKED` until the `nextStateN` range defect is resolved.** D6
   records 2 holdout events carrying `nextStateN = -1`, 5 holdout events with zero training
   support under an unsmoothed `(N,N')` kernel, and 15–17% of marks leaving `{1..8}`. The raw MAT
   archive that would discriminate step-fitting artifact from ingest defect is absent.

Nothing in this protocol asserts that the mark process has been prospectively validated on
Wadhwa-2022 — that specific wording is forbidden and would be false.

## 1. Recorded facts this protocol is built on (no re-derivation)

| fact | value | source |
|-|-|-|
| Cohort `derived_eligible_1_to_8` | 80 train motors / 793 train events; 19 holdout motors / 233 holdout events | frozen cohort, established |
| Impossible marks | 2 below-physical-minimum target-state marks (`nextStateN` below the physical floor); both events holdout, both from the same holdout motor. Event-level identifiers are D12-redacted; see `reports/D6-...md` §1 handling notice | `reports/D6-...md` §1 |
| Root cause | `scripts/ingest-wadhwa-data.py:141-143` range-checks the **dwell's own** state; `next_state` is read at line 147 and written through at lines 158/159/160 with **no range check** (`grep -n next_state` returns only 147, 158, 159, 160) | verified 2026-07-22, `grep -n next_state scripts/ingest-wadhwa-data.py` |
| Exclusion counter | `outOfRangeDwells: 3` — the offending dwell is excluded, its **predecessor** is retained with a mark pointing at the excluded state | `reports/D6-...md` §2 |
| Zero training support | **5 of 233** holdout events have zero training support under an unsmoothed `(N,N')` kernel; each gives `log p = -inf` under an unsmoothed kernel → HALT | `reports/D6-...md` §5 |
| Alphabet escape | train **120/793 = 15.1%** (targets `{0:24, 9:84, 10:11, 11:1}`); holdout **39/233 = 16.7%** (targets `{-1:1, 0:15, 9:21, 10:2}`) | `reports/D6-...md` §5 |
| Smoothing sensitivity | Track C held-out contrast: CI crossed zero at **every** α ∈ {0.1, 0.5, 1.0, 2.0}; the point estimate **changed sign** between α = 0.1 and α = 0.5 | `reports/D5-...md` §7 |
| Raw archive | `data/remodeling_data.mat` — **ABSENT**. `find . -name "*.mat" -not -path "./node_modules/*"` returned nothing (2026-07-22). Ingest declares it as positional arg `raw_mat` at `scripts/ingest-wadhwa-data.py:82` | verified 2026-07-22 |
| Executable machinery | `src/motor_stack_aif/marks.py` — policies `strict` / `quarantine` / `retain_labelled`, `flag_impossible_marks`, `mark_alphabet_escape`, `assert_closed_alphabet`; **no silent-drop policy exists** | read 2026-07-22 |
| Test receipts | `tests/motor_stack_aif/test_nextstate_range_check.py` **7 passed in 1.26s**; `tests/motor_stack_aif/test_no_holdout_mark_read.py` **33 passed in 3.84s** | run 2026-07-22 |

The mitigating fact from D5 §7 is recorded, not offered as an excuse: at 19 holdout motors the
mark channel had very little resolving power. That **bounds** the cost of the loss. It does not
undo it, and an inconclusive interval is `NOT_ESTABLISHED` — it is never a statement that the
pooled and state-conditional kernels are equivalent. Underpowered is not equivalence.

---

## 2. RAW ARCHIVE RE-DERIVATION

**Required.** Obtain `data/remodeling_data.mat` (the Wadhwa-2022 raw step-fitting archive), then
re-run `scripts/ingest-wadhwa-data.py` against it under a fresh output path — **the committed
`experiments/data/wadhwa-2022-events.json` is the historical record and is not edited.** Compare
the re-derived extraction to the committed one event-by-event. The single discriminating check is
the two below-physical-minimum target-state mark events identified in D6 §1 (event identifiers
D12-redacted; the raw-archive re-derivation script resolves them internally against the committed
dataset without reproducing them in this document):

- if the raw archive also carries a transition into a negative stator count → the **step fitting**
  produced an impossible transition, and the recorded value is faithful to the source;
- if the raw archive carries a legal target and the `-1` appears only after ingest → the **ingest**
  mis-propagated the `outOfRangeDwells` exclusion into the predecessor's mark.

**Licenses:** a `P0` provenance statement about which of the two mechanisms produced the impossible
value; the removal of a blocking ambiguity from the D6 closure row; a documented, source-pinned
handling decision for those two events.

**Does NOT license:** any prospective mark claim. Re-deriving the extraction does not un-spend the
held-out mark channel — D5 is about *reading*, not about *file contents*. It also does not license
editing the committed dataset, nor re-labelling any re-derived field `OBSERVED` beyond what the raw
archive itself pins.

**Falsifier:** re-derivation shows the committed extraction is faithful **and** the raw archive
itself contains the negative target. Then the reflecting-boundary assumption `P(jump < 0 | N = 0)
= 0` is contradicted by the source measurement, not by a pipeline artifact, and every mark model
that enforces that boundary is refuted at that event rather than rescued.

**Status today:** `BLOCKED_EXTERNAL` — archive absent, verified.

---

## 3. RANGE-CHECK REPAIR

**Required.** A validation layer that refuses to let an out-of-physical-range mark pass silently
into any mark model. Physical bounds are `PHYSICAL_MIN_STATORS = 0`, `PHYSICAL_MAX_STATORS = 11`
(`src/motor_stack_aif/marks.py:20-21`). The repair is **detection plus a forced decision**, never a
correction of the recorded value.

**Already built and executable in this repository today.** `flag_impossible_marks()` returns one
record per offending event carrying `eventId`, `motorId`, `stateN`, `nextStateN`, `jump`,
`partition` and a `reason` from `{NEXT_STATE_BELOW_PHYSICAL_MINIMUM,
NEXT_STATE_ABOVE_PHYSICAL_MAXIMUM}`. The regression receipt
`tests/motor_stack_aif/test_nextstate_range_check.py` includes
`test_the_known_defect_is_still_present_and_unedited`, which fails if anyone repairs the defect by
editing the frozen dataset.

**Licenses:** a mark pipeline that cannot ingest a physically impossible stator count without an
explicit, recorded operator decision; a `P1` implementation-integrity statement about the mark
path.

**Does NOT license:** any statement about *biology*. A range check is a software invariant. It says
nothing about whether stator remodelling is Markovian, state-dependent, or mechanistically
interesting. It also does not license patching `scripts/ingest-wadhwa-data.py` and re-emitting the
frozen dataset in place — the defect is preserved on purpose.

**Falsifier:** the guard fails to fire on a synthetic event carrying `nextStateN = -1` or
`nextStateN = 12`; or the frozen dataset stops containing the two known defect events, which would
mean the record was edited rather than annotated.

**Status today:** `EXECUTABLE_NOW — BUILT AND TESTED` (7 tests, 1.26s).

---

## 4. QUARANTINE POLICY

**Required.** Every mark analysis must declare exactly one impossible-mark policy in its own
artifact, from the closed set in `marks.py:23`:

| policy | behaviour | when to use |
|-|-|-|
| `strict` | raises `ImpossibleMarkError` listing the offending `eventId`s | default; refuses to proceed silently |
| `quarantine` | returns `(kept, quarantined)`, stamping `quarantineReason` + `quarantineDefect = "D6_INGEST_NEXTSTATE_NOT_RANGE_CHECKED"` | when the analysis is scored on the remaining events and the exclusion must stay visible |
| `retain_labelled` | returns `(kept, [])` with `rawDataDefect` + `rawDataDefectReason` on the affected events | when the analysis must score every event and the defect is carried as a documented label |

**There is deliberately no policy that drops the events silently** — `prepare_mark_dataset` raises
`ValueError` on any policy name outside the three. The quarantined count is part of the result, not
a footnote: an artifact that reports a score without reporting how many events were quarantined is
incomplete.

**Licenses:** a reportable mark analysis whose event exclusions are auditable; comparison between
two mark models **only if both declare the same policy**.

**Does NOT license:** comparing a `quarantine` run against a `retain_labelled` run as if the
difference were a modelling result. Different policies score different event sets, so the contrast
is confounded by the exclusion, not by the model. It also does not license treating quarantine as a
repair — the underlying ambiguity stays open until §2.

**Falsifier:** a mark analysis is found that passes `marks.py` yet silently changes its scored
event count; or two published mark contrasts are found to differ in policy while being compared
head-to-head.

**Status today:** `EXECUTABLE_NOW — BUILT AND TESTED` (covered by
`test_preparation_refuses_silent_drop`, `test_quarantine_policy_preserves_and_labels`,
`test_documented_defect_policy_retains_with_label`, `test_unknown_policy_is_rejected`).

---

## 5. PREDECLARED SMOOTHING

**This is the section that matters most, and the ordering is the whole point.**

An unsmoothed `(N,N')` kernel **HALTs**: 5 of 233 holdout events have zero training support, each
producing `log p = -inf` under the no-floor policy. So smoothing is not a stylistic choice — it is
**mandatory**, and it is **outcome-determining**. The recorded evidence: in the Track C held-out
contrast the point estimate **changed sign** between α = 0.1 and α = 0.5, while the interval
crossed zero at all four constants α ∈ {0.1, 0.5, 1.0, 2.0}.

A hyperparameter that decides the **direction** of a result is not a nuisance parameter. If α is
chosen after the outcomes are visible, the analyst — not the data — picks the sign of the headline.
Predeclaring α does not make the analysis more accurate; it makes the analysis **falsifiable**.
That is the entire function of the ordering: with α fixed in advance, an adverse result cannot be
tuned away, and a favourable result cannot have been manufactured by selection. With α fixed
afterwards, the contrast has no evidential content at all, however narrow its interval looks.

**Required, in this order, before any new mark analysis:**

1. Write and **commit** a prediction record naming: the smoothing family (e.g. additive-α
   Dirichlet / Laplace on the `(N,N')` count table), the exact constant α, the alphabet the counts
   are laid over, the impossible-mark policy from §4, the scoring rule, the resampling unit
   (**MOTOR**), the seed, and the falsifier — **with zero observations of the new outcome in
   existence**. Prospectivity is decided by the commit graph, not by prose: the prediction commit
   must be a proven strict ancestor of the result's introduction.
2. If α cannot be justified a priori, predeclare a **sensitivity grid** and predeclare the reading
   rule for it. The honest reading rule is: *if the sign of the contrast is not stable across the
   whole predeclared grid, the result is reported as `NOT_ESTABLISHED — SMOOTHING_DEPENDENT`, and
   no direction is claimed.* Declaring the grid after seeing the grid is the failure mode this
   clause exists to prevent.
3. Only then run.

**Licenses:** a mark contrast whose sign can be trusted as coming from the data, on whatever split
its data-access protocol declares.

**Does NOT license:** promoting a predeclared-α result on **this** dataset to prospective status.
Predeclaring α repairs the *hyperparameter selection* problem; it does not repair D5. On
Wadhwa-2022 the held-out mark channel is already spent, so even a perfectly predeclared analysis
there remains `RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET`. The two defects are independent and both
must be cleared.

**Falsifier:** a mark result is published whose α was fixed after any outcome was visible; or the
predeclared grid is found to have been widened, narrowed, or re-centred between the prediction
commit and the result commit.

**Status today:** `EXECUTABLE_NOW as a procedure` (the prediction record can be written and
committed today) but **evidentially inert on this dataset** — see §6.

---

## 6. INDEPENDENT DATASET REQUIREMENT

**Required.** A stator-remodelling dataset that is **not** Wadhwa-2022, carrying dwell state,
dwell duration, and the transition target, with:

- a **new split** defined and committed before any held-out field is read;
- enough **motors** — the experimental unit is the motor, and 19 holdout motors gave the mark
  channel very little resolving power; the required count must be justified from the effect size
  a mark model is expected to produce, not chosen after seeing an interval width;
- a declared `<TASK>-DATA-ACCESS-PROTOCOL.md` naming fields to read, split, forbidden fields, claim
  boundary, prospective status, falsifier and stop condition, per the D5 process rule;
- provenance sufficient to pin the transition targets to a recorded measurement, so `OBSERVED` is
  earned rather than asserted.

**Licenses:** the *only* route to a prospective mark-mechanism receipt. This folds the mark question
into the `P4` transfer and `P7` independent-replication requirements the project already carries —
it does not create a new requirement, it strengthens two existing ones.

**Does NOT license:** anything retroactive. A clean second dataset does not restore prospective
status to Wadhwa-2022; the Wadhwa mark result would become, at best, a retrospective consistency
check against the new prospective one. It also does not license averaging the two studies into one
verdict — cross-study pooling is its own gate with its own leakage risks.

**Falsifier of the transfer itself:** the mark structure that fits Wadhwa-2022 fails on the
independent dataset under the predeclared α and the predeclared scoring rule. That is a real,
informative outcome and must be reported as such, not absorbed.

**Status today:** `BLOCKED_EXTERNAL` — no such dataset is in this repository.

---

## 7. ONE-STEP CONDITIONAL MARK LIKELIHOOD

**Required.** Because 15.1% of training and 16.7% of holdout marks point **outside** `{1..8}`, the
observed process is not a closed chain on the cohort. The only structurally honest object available
on this extraction is a **one-step-ahead conditional**: `p(N' | N, ...)` scored on events whose
*originating* state is in the cohort, with the target alphabet **extended** to cover the observed
escape targets (`{-1, 0, 9, 10, 11}` alongside `{1..8}`) or with the escape mass assigned to an
explicit `OUT_OF_COHORT` absorbing symbol. Either choice must be declared; both are legitimate; a
third option — discarding the escape mass — is not, because it inflates the remaining likelihood.

The artifact must say, in its own words, that it is a one-step-ahead conditional prediction and
**not** a trajectory likelihood.

**Licenses:** a scoreable mark-bearing term for the motor stack; a like-for-like contrast between a
pooled kernel and a state-conditional kernel under the same alphabet, same policy, same α, same
motor-cluster resampling; a `P1`/`P3`-shaped statement scoped to whatever split its data-access
protocol permits.

**Does NOT license:** any statement about long-run occupancy, stationary distribution, mean first
passage, or trajectory probability. Those are properties of a closed chain, and this object is not
one. It also does not license reading a one-step conditional advantage as **mechanism** —
predictive superiority is never promoted to mechanism anywhere in this program.

**Falsifier:** the escape fraction is found to be materially different from the recorded 15.1% /
16.7% under the declared cohort and policy, which would mean the alphabet was mis-specified; or the
scored event count does not equal the declared eligible count minus the declared quarantine count.

**Status today:** `EXECUTABLE_NOW on the training partition only`
(`TRAIN_ONLY`). On the holdout it is
`HOLDOUT_MARK_CHANNEL_BURNED_RETROSPECTIVE_ONLY`.

---

## 8. CLOSED-CHAIN LIKELIHOOD ONLY IF VALID

**Required.** A closed-chain (trajectory) likelihood over `{1..8}` may be written **only** when all
of the following hold simultaneously:

1. §2 raw-archive re-derivation has resolved the two impossible marks, or the cohort is redefined
   so that the escape mass genuinely vanishes;
2. `assert_closed_alphabet(events, states=(1..8), partition=...)` returns without raising — it
   currently raises, by design, and `test_closed_chain_assumption_is_refused` locks that behaviour
   in;
3. the impossible-mark policy from §4 is declared and the quarantined count is reported;
4. the smoothing constant from §5 is predeclared and committed.

Until all four hold, a closed-chain likelihood is **invalid on this extraction**, not merely
imprecise. `assert_closed_alphabet` is the executable gate: it is not a warning, it raises
`OpenMarkAlphabetError` and stops the analysis.

**Licenses (only once valid):** trajectory-level statements — occupancy, dwell-sequence
probability, first-passage structure over the closed alphabet.

**Does NOT license:** trajectory statements obtained by *narrowing the cohort until the escapes
disappear*, unless that narrowing was predeclared and its biological meaning is defended. Shrinking
the state set to force a closed alphabet is alphabet-shopping, and it produces a chain that is
closed by construction rather than by observation.

**Falsifier:** `assert_closed_alphabet` raises on the cohort a published closed-chain result claims
to cover; or the escape targets recorded in D6 are present in the scored data of any artifact that
asserts closure.

**Status today:** `BLOCKED` — conditions 1 and 2 are not met, and condition 1 is
`BLOCKED_EXTERNAL`.

---

## 9. Executable-today ledger

| section | status today | why |
|-|-|-|
| §3 range-check repair | **EXECUTABLE_NOW — BUILT AND TESTED** | `marks.py` + `test_nextstate_range_check.py`, 7 passed in 1.26s |
| §4 quarantine policy | **EXECUTABLE_NOW — BUILT AND TESTED** | three named policies, no silent-drop path, same test file |
| §5 predeclared smoothing | **EXECUTABLE_NOW as procedure; evidentially inert on this dataset** | the prediction record can be committed today, but D5 caps any Wadhwa mark result at retrospective-only |
| §7 one-step conditional | **EXECUTABLE_NOW on `TRAIN_ONLY`** | training marks are unspent; holdout marks are burned |
| §2 raw archive re-derivation | **BLOCKED_EXTERNAL** | `data/remodeling_data.mat` absent (verified: no `*.mat` in the tree) |
| §6 independent dataset | **BLOCKED_EXTERNAL** | no second stator-remodelling dataset in this repository |
| §8 closed-chain likelihood | **BLOCKED** | depends on §2 (external) and on §7's escape mass |

## 10. What this protocol explicitly does not do

- It does not raise `P2`, `P3`, `P4`, `P6`, `P7` or `P8`. **No P-level is moved by this document.**
- It does not restore prospective status to any Wadhwa-2022 mark field. Reading is irreversible.
- It does not re-threshold, re-open, or re-interpret any frozen B3/B4 verdict. B3 duration scoring
  never reads the mark; no B4 cell reads the mark; the F-side duration model does not read the mark.
- It introduces **no new evidential threshold**. The physical bounds `0..11` are the physics of
  stator occupancy, not a tuned criterion. Any α grid a future analysis predeclares is
  `DESIGN_ONLY` until it is committed inside a prediction record.
- It contains no claim that the mark process has been validated on any dataset.

## 11. Scoped standing statements (never unscoped)

- **`P6` for the Wadhwa mark-process mechanism** is retrospective-only and transfer-required (D5,
  D6). **`P6` for duration-only B3/B4 is unchanged.**
- **`P2` for mark fields** carries the D6 limitation. **`P2` for duration fields is unchanged.**
- **`P3` duration-only held-out evidence is untouched** by D5 and D6.
- **`P4` and `P7` requirements are strengthened**, because transfer is now also the only route to a
  prospective mark receipt.

---

NEXT_ACT = Write and commit `hierarchical-aif/protocols/MARK-KERNEL-TRAIN-ONLY-DATA-ACCESS-PROTOCOL.md` declaring split boundary `TRAIN_ONLY`, forbidden fields (held-out `nextStateN`/`direction`/`jump`), impossible-mark policy `quarantine`, a predeclared additive-alpha grid with its sign-stability reading rule, motor-level resampling, and the falsifier — committed with zero new outcomes in existence — so that the §7 one-step conditional becomes runnable on the training partition without spending anything.
