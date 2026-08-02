# Semantic Coverage Ledger

**Purpose:** an append-only record of what the Phase-C semantic gate command has been
*measured* to detect, and what it has been measured *not* to detect.

**Append-only rule.** Entries are added. No entry is edited to make an earlier adverse
measurement look better. The Phase-C `0/10` result below is permanent.

**Contracts followed:** `CLAUDE.md`,
`audits/coordinator/claude-three-phase-parity-completion-plan.v1.md`
**Flow:** `OBSERVE → BOUND → PREDICT → ACT → VERIFY → FALSIFY → UPDATE → RECORD`

---

## Entry 1 — Phase C: blind mutation battery, `0/10` detection (ADVERSE)

**Protocol:** `audits/phase-c/blind-mutation-protocol.codex.v1.json`
**Prediction commit:** `b95e714d6f4f07b02eb369eb43fed1d1567b1acd`
**Result commit:** `cc9ba769f580367d75441325ca967aed7bd738c8`
**Result:** `audits/phase-c/blind-mutation-result.codex.v1.json`
**Author:** Codex, independently and blind to the semantic test sources.

Ten fresh corruptions of named biological, statistical, and scientific-boundary
properties were applied in isolated clones and measured against the semantic gate
command `node --test tests/semantic/*.mjs`.

| Classification | Count |
|---|---|
| `DETECTED_SEMANTIC` | **0** |
| `DETECTED_BY_HASH_ONLY` | 0 |
| `SURVIVED` | **10** |
| `NOT_RUN` | 0 |
| `INCONCLUSIVE` | 0 |

**This is adverse evidence about semantic coverage.** At that commit the semantic gate
detected none of the ten. The ten properties were: seconds-scale density Jacobian;
survival-conditioned posterior; sample-variance Bessel correction; hidden-world
observation boundary; physical stator-count range; load-dependent stator recruitment;
first-passage weight normalization; stator-multiplicity off hazard; exponential-mixture
second moment; periodic 13-site lattice topology.

**What it did not mean.** It did not mean the production code was wrong — the mutations
were injected defects, not discovered ones. It measured the *instrument*, not the science.

---

## Entry 2 — Phase D1: target-specific semantic remediation

**Protocol:** `audits/phase-d/d1-semantic-remediation-protocol.v1.json`
(execution addendum: `...-protocol-addendum-v2.json`)
**Predictions:** `audits/phase-d/d1-semantic-remediation-predictions.v1.json`
**Result:** `audits/phase-d/d1-semantic-remediation-result.v1.json`
**Author:** Claude, with full prior knowledge of the Phase-C battery.

Independent scientific invariants for the same ten properties were added to
`tests/semantic/`, then measured by replaying twenty-three corruptions: the ten exact
Phase-C patches, eleven structurally different alternate forms, and two adverse-record
laundering attacks.

| Classification | Count |
|---|---|
| `DETECTED_SEMANTIC` | **22** |
| `DETECTED_BY_HASH_ONLY` | 0 |
| `SURVIVED` | **1** |
| `NOT_RUN` | 0 |
| `INCONCLUSIVE` | 0 |

> **Read with Entry 3.** These are *classified* counts. Two of the 22 could not be
> attributed to their declared intended test, so the **creditable** figure is
> **20 of 23**, and **AC4 FAILS**. Do not quote 22 as coverage.

The single `SURVIVED` is `D1A10`, proven a null mutation before execution (see finding 2
below). Semantic suite: 33 → 55 tests. Negative control: an unmutated bare clone at the
replay base commit runs 55/55 green, so every detection is mutation-caused.

### What this establishes

**Target coverage established** over the ten named properties, verified by both exact
and alternate-form replay.

### What this does NOT establish

**Future robustness is not established.** These corruptions were authored with complete
knowledge of the production source and of the Phase-C battery, and the gates were
designed specifically to detect them. Confirmation is therefore a low-risk prediction.
It says nothing about defects nobody has thought of.

The distinction matters because Entry 1 was *blind* and Entry 2 was *not*. A blind
`0/10` and a sighted `20/23` are not comparable numbers, and it would be spin to
present them as a before/after improvement in detection capability.

### Coverage provenance — new coverage versus suite-membership migration

Several of the ten were already detected before D1, by commands that the Phase-C
protocol deliberately excluded from per-mutation classification (`npm test`,
`npm run cross-study:verify`). For those properties D1 moved an existing check into the
classified gate; it did not discover a missing invariant.

**Measured (frozen, binary on baseline exit code):** 15 of 23 cells
`SUITE_MEMBERSHIP_MIGRATION`, 8 `NEW_COVERAGE_IN_D1`.

**Post-hoc refinement** (`audits/phase-d/d1-coverage-provenance-posthoc.v1.json`,
authored after execution and explicitly labelled as such — it does *not* override the
frozen field): of the 15 migrations, 10 were genuine semantic baseline detections and 5
were baseline failures that only noticed an *artifact-identity change* caused by
regeneration. A hash mismatch is not semantic detection under the Phase-C rules.

So the honest split is roughly: **10 migrations, 13 genuinely new semantic coverage.**
The frozen binary field remains the measurement of record; reporting a migration as new
coverage is forbidden, and so is quietly upgrading a hash-only baseline failure into a
claimed pre-existing invariant.

### Adverse and null findings recorded in D1

1. **Non-integral stator occupancy is accepted.** `instrumentObservation` clamps live
   stator counts to `0..11` but does not quantize them: `7.5` passes. No repository
   document declares integral occupancy. The bound is gated; the integrality
   sub-property is recorded `NOT_ESTABLISHED`. Production was **not** changed to satisfy
   a test.

2. **One frozen alternate-form cell was a null mutation.**
   `D1A10_LATTICE_NEXT_NEAREST_NEIGHBOUR_RING` replaced the nearest-neighbour ring with
   a next-nearest-neighbour ring. Because the lattice has 13 sites and 13 is prime, the
   relabelling `s → 2s mod 13` is a graph isomorphism: occupancy count is preserved and
   the marginal occupancy distribution is identical. Measured difference in recomputed
   residuals: `1.6e-16`, against `2.6e-4` for the genuine open-chain corruption.
   **No observable of this model can distinguish the two.** Prediction `P-D1-2` for that
   cell is therefore **FALSIFIED**, and is recorded as falsified rather than rewritten.
   A genuine alternate (`D1A10B`, one bond double-counted, which breaks translational
   symmetry and is not an isomorphism) was added by append-only addendum before any
   replay was executed.

   This is a limitation of the lattice gate, now declared: **any bond-offset relabelling
   on a prime-length ring is undetectable, because it is not a corruption.**

3. **The lattice anti-vacuity control is coupled to `J` being identifiably nonzero.**
   If a future honest refit yielded `J ≈ 0`, the periodic and open-chain topologies
   coincide and the control fires for a scientific rather than a corruption reason.

4. **Acceptance criterion AC4 FAILED as literally specified.** `attributionSatisfied`
   is false for 2 of 23 cells. In both, the frozen `expectedFailingTest` named the wrong
   *sibling test within the correct property*:
   - `D1A02` was caught by the survivor-mass-ratio and saturation tests, while the
     `t = 0` test correctly **passed** — the mutation is provably invisible at the
     origin, exactly as the protocol itself predicted. The protocol nonetheless named
     the `t = 0` test as the expected one.
   - `D1P02_ADVERSE_EVIDENCE_COPY_DIVERGED` was caught by the evidence-copy divergence
     test, while the protocol named the canonical-record test.

   Detection was correct in both cases and attribution to the intended **property**
   holds; attribution to the intended **test name** does not. These are protocol
   labelling errors and are recorded rather than corrected retroactively.

5. **Prediction `P-D1-7` refuted as literally stated.** It predicted the baseline
   ordinary suite would not detect `D1X09`. The baseline exited nonzero, so the frozen
   field records a migration. The post-hoc analysis finds that failure was an
   artifact-identity change, consistent with the underlying claim that
   `normalizedVariance` has no reader in the JavaScript codebase — but the literal
   prediction is refuted and closes as refuted.

6. **Instrument imperfection.** The runner's failing-test-name extractor also captures
   the spec reporter's `failing tests:` summary header as if it were a test name. It is
   filtered when reporting but is present in the raw result JSON.

---

---

## Entry 3 — Phase D1 correction package 01 (Codex `REJECT_BLOCKING`)

**Record:** `audits/phase-d/d1-correction-package.v1.json`
**Reviewed commit:** `fb9aa3369fded56a9be7ac4998d01933599a2d73`
**Verdict:** `REJECT_BLOCKING` → one bounded correction package (plan §5 budget now spent).

Codex rejected the Phase-1 handoff on five blocking defects. All five were confirmed
against the artifacts. **No measurement was re-run and no classification changed.**

| # | Defect | Correction |
|---|---|---|
| C1 | The result recorded `protocolPath` = the **v1** protocol, but the run actually used **addendum v2**. | Authoritative binding recorded and *proven* by cell containment (`D1A10B` exists only in the addendum). Runner now derives the path and records `protocolVersion` + `protocolSha256`. Erroneous original preserved unedited. |
| C2 | Addendum timing was narrative only. | Recorded as **`AFTER_IMPLEMENTATION_BEFORE_EXECUTION`**. `D1A10B` may not be presented as a pre-implementation frozen prediction. |
| C3 | Headline reported **22** detections while separately listing 2 attribution failures. | Accounting is **22 classified, 20 credited, 2 uncredited, AC4 = FAIL**. D1 may claim **20 of 23**, not 22. AC4's frozen text is scoped to the 22 classified detections and is now quoted verbatim. |
| C4 | A gate asserted `statorsFor(7.5) === 7.5`, pinning fractional occupancy as *required* behaviour. | Assertion removed. Integrality stays `NOT_ESTABLISHED`. The 0..11 bound remains fully gated. |
| C5 | The handoff claimed, as a blanket over the suite, that **no** assertion uses SHA-256. False. | Claim **withdrawn**. Three files compute SHA-256; one is a D1 gate using a digest as a *secondary* criterion. It was **never the sole basis of any classification** — though it *did* fire in `D1P01`, so the draft's "produced zero classifications" wording was itself wrong and is corrected. The same false claim is also frozen in `d1-semantic-remediation-predictions.v1.json` (P-D1-4 rationale); that file is preserved unedited, so the remedy is disclosure. |

### Additional finding, discovered while correcting — `AF1`, BLOCKING

Codex asked for five corrections. Applying them surfaced a sixth, which is **more
serious than three of the five** and is recorded rather than deferred.

`verifyPredictionAncestry` hardcoded the **v1** protocol path. The strictness rule it
guards requires that the governing protocol *not* have entered history in the replay
base commit. The executed addendum entered history at `8baead2` — **which is the replay
base commit**. The hardcoded path is the **only** reason the replay was permitted to run.

Proved by running the corrected instrument against the run that was actually performed:

```
node audits/phase-d/tools/run-d1-semantic-replay.mjs --preflight \
  --base-commit 8baead2... --protocol ...protocol-addendum-v2.json
→ Error: The D1 protocol file entered history in the replay base commit itself;
  ancestry is not STRICT.   (exit 1)
```

**The corrected instrument refuses the run that was performed.** Consequences:

* `ancestry.strictAncestry = true` in the preserved result is true of **v1**, and false
  of the protocol that actually governed the run. That field is now listed as superseded.
* The **ten exact replays are unaffected** — v1 protocol and v1 predictions do have
  strict ancestry.
* `D1A10B` (addendum-only) keeps a real, reproducible detection but **loses prospective
  standing**: `NOT_ESTABLISHED` as a prospective prediction.
* **AC5 for `D1P10` is downgraded** to `SATISFIED_WITHOUT_STRICT_PROSPECTIVE_ANCESTRY`,
  because that property's only surviving alternate form is `D1A10B`.

No re-execution was performed. Whether to re-run under a strictly-ancestral protocol is
Codex's call, not something to be absorbed silently into this package.

**Corrected headline for Phase D1:** 23 cells → **20 credited detections**, 2 classified
but uncredited, 1 SURVIVED (the proven null mutation), 0 hash-only, 0 not-run.
**AC4 FAILS. AC5 for D1P10 is downgraded.**

All corrections are held in place by `tests/semantic/d1-correction-integrity.semantic.test.mjs`,
whose guards were negative-control tested against the pre-correction text. Those guards
are literal-pattern scans scoped to `tests/semantic/`; that limitation is stated in the
correction record rather than papered over.

Every historical result, protocol, prediction, evidence log, Phase-C artifact and
production file remains byte-identical.

**Process note.** This package was adversarially self-reviewed before commit by six
independent reviewers instructed to refute it. They found `AF1` plus five overstatements
in the draft — including a second false claim of exactly the kind Codex had just caught.
All were corrected before commit. The correction budget is spent.

---

## Standing rules for future entries

1. Record the classification counts verbatim, including adverse ones.
2. State whether the battery was blind or sighted. Never compare a blind count with a
   sighted count as if they measured the same thing.
3. Separate new coverage from suite-membership migration.
4. A falsified prediction closes as falsified.
5. Detecting known corruptions is target coverage. It is never evidence of general or
   future robustness.
6. No entry may restate, weaken, or supersede Entry 1.
7. Report **credited** detections, never classified detections, as the coverage figure.
   A detection that cannot be attributed to its declared intended test is classified but
   not credited, and the difference is reported rather than absorbed.
8. Do not make blanket claims about the whole suite that were only checked on part of
   it. Scope the claim to what was actually enumerated.
9. A gate may not pin behaviour that the same phase records as `NOT_ESTABLISHED`.
10. When a correction surfaces a defect worse than the ones being corrected, record it in
    the same package at full severity. Do not defer it to make the package look clean.
