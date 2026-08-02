// Semantic gate: right-censored dwell treatment.
//
// Frozen protocol rule (experiments/preregistration.v1.json, extraction.rules):
//   "Retain the last dwell as right-censored for provenance but exclude it from
//    uncensored duration likelihoods."
//
// This gate asserts the MEANING of that rule, not the stability of any artifact.
// It routes through NO sha256, NO runId, NO committed report file, and NO stored
// pipeline output. It is built entirely from a synthetic fixture whose expected
// values are hand-calculated below, so the oracle is arithmetic, not the pipeline.
//
// Target corruption (mutation M06): deleting `!event.rightCensored &&` from the
// cohort filter in lib/observed-experiment.js, which admits right-censored dwells
// into the uncensored duration likelihood.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { runObservedExperiment } from "../../lib/observed-experiment.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

const PROTOCOL_ID = "SYNTHETIC-CENSORING-SEMANTIC-GATE";
const STATE = 2;

// ---------------------------------------------------------------------------
// Synthetic fixture with hand-calculable per-state means.
//
// TRAIN, state 2, UNCENSORED: 24 dwells = 8x1s + 8x3s + 8x5s
//     sum = 8*1 + 8*3 + 8*5 = 8 + 24 + 40 = 72 s over 24 dwells -> mean = 3 s exactly
// TRAIN, state 2, RIGHT-CENSORED: 24 dwells of 1 s
//     sum = 24 s over 24 dwells
// If censored dwells are wrongly admitted:
//     (72 + 24) / (24 + 24) = 96 / 48 = 2 s exactly
//
// So the protocol-correct training mean is 3 and the corrupted mean is 2.
// Both are exact binary floats; no tolerance is required.
//
// HOLDOUT, state 2, UNCENSORED: 5 motors x 5 dwells of 1,2,3,4,5 s = 25 dwells
// HOLDOUT, state 2, RIGHT-CENSORED: 5 motors x 2 dwells of 1 s = 10 dwells
// Correct holdout cohort = 25 events; corrupted holdout cohort = 35 events.
// ---------------------------------------------------------------------------

const EXPECTED_TRAIN_MEAN_EXCLUDING_CENSORED = 3;
const EXPECTED_TRAIN_MEAN_IF_CENSORED_ADMITTED = 2;
const EXPECTED_TRAIN_COHORT_EXCLUDING_CENSORED = 24;
const EXPECTED_TRAIN_COHORT_IF_CENSORED_ADMITTED = 48;
const EXPECTED_HOLDOUT_COHORT_EXCLUDING_CENSORED = 25;
const EXPECTED_HOLDOUT_COHORT_IF_CENSORED_ADMITTED = 35;

function makeEvent({ motorId, index, partition, durationS, rightCensored }) {
  return {
    eventId: `${motorId}:${String(index).padStart(4, "0")}`,
    motorId,
    partition,
    splitRemainder: partition === "train" ? 1 : 0,
    stateN: STATE,
    enteredAtS: 100 + index,
    durationS,
    eventAtS: 100 + index + durationS,
    nextStateN: rightCensored ? null : STATE + (index % 2 === 0 ? 1 : -1),
    direction: rightCensored ? null : index % 2 === 0 ? "on" : "off",
    jump: rightCensored ? null : index % 2 === 0 ? 1 : -1,
    rightCensored,
  };
}

function buildFixtureEvents() {
  const events = [];

  // ---- TRAIN: 4 motors x 6 uncensored dwells = 24, durations cycle 1,3,5 ----
  const trainDurations = [1, 3, 5, 1, 3, 5]; // per motor sum = 18; 4 motors -> 72 s
  for (let motor = 0; motor < 4; motor += 1) {
    const motorId = `train-motor-${motor}`;
    for (let i = 0; i < trainDurations.length; i += 1) {
      events.push(makeEvent({
        motorId,
        index: i + 1,
        partition: "train",
        durationS: trainDurations[i],
        rightCensored: false,
      }));
    }
    // ---- TRAIN censored tail: 6 dwells of 1 s per motor -> 24 total, sum 24 s ----
    for (let i = 0; i < 6; i += 1) {
      events.push(makeEvent({
        motorId,
        index: 100 + i,
        partition: "train",
        durationS: 1,
        rightCensored: true,
      }));
    }
  }

  // ---- HOLDOUT: 5 motors x 5 uncensored dwells (1..5 s) = 25 ----
  for (let motor = 0; motor < 5; motor += 1) {
    const motorId = `holdout-motor-${motor}`;
    for (let i = 1; i <= 5; i += 1) {
      events.push(makeEvent({
        motorId,
        index: i,
        partition: "holdout",
        durationS: i,
        rightCensored: false,
      }));
    }
    // ---- HOLDOUT censored tail: 2 dwells of 1 s per motor -> 10 total ----
    for (let i = 0; i < 2; i += 1) {
      events.push(makeEvent({
        motorId,
        index: 100 + i,
        partition: "holdout",
        durationS: 1,
        rightCensored: true,
      }));
    }
  }

  return events;
}

function buildDataset(events) {
  const censoredCount = events.filter((event) => event.rightCensored).length;
  return {
    schema: "uni.flagellum.synthetic-censoring-fixture/1.0.0",
    protocolId: PROTOCOL_ID,
    ingestion: {
      script: "tests/semantic/censoring-exclusion.semantic.test.mjs",
      motorCount: new Set(events.map((event) => event.motorId)).size,
      // Provenance census: EVERY dwell, censored ones included.
      eventCount: events.length,
      uncensoredEventCount: events.length - censoredCount,
      exclusions: { leftTruncatedDwells: 0, rightCensoredDwells: censoredCount, outOfRangeDwells: 0, zeroOrNegativeDurationDwells: 0 },
    },
    motors: [...new Set(events.map((event) => event.motorId))].sort(),
    events,
  };
}

const protocol = {
  protocolId: PROTOCOL_ID,
  scope: { primaryStates: [STATE] },
  split: { method: "synthetic fixture: motor name prefix" },
  uncertainty: { replicates: 8, seed: 20260717, interval: "Percentile 95%" },
};

// Deep clone so no run can observe another run's mutations.
const clone = (value) => JSON.parse(JSON.stringify(value));

const fixtureEvents = buildFixtureEvents();

// Run A: protocol-correct input (censored dwells present and flagged).
const datasetWithFlags = buildDataset(clone(fixtureEvents));
const runWithFlags = runObservedExperiment(datasetWithFlags, protocol, { fixture: "synthetic" });

// Run B: censored dwells physically absent from the record.
const datasetWithoutCensoredRows = buildDataset(clone(fixtureEvents).filter((event) => !event.rightCensored));
const runWithoutCensoredRows = runObservedExperiment(datasetWithoutCensoredRows, protocol, { fixture: "synthetic" });

// Run C: censoring information erased (every flag forced false). This is the
// M06 corruption expressed in the DATA rather than the code, and it exists only
// to prove the fixture actually discriminates.
const datasetFlagsStripped = buildDataset(clone(fixtureEvents).map((event) => ({ ...event, rightCensored: false })));
const runFlagsStripped = runObservedExperiment(datasetFlagsStripped, protocol, { fixture: "synthetic" });

test("right-censored dwells are excluded from the uncensored duration likelihood (hand-calculated mean)", () => {
  assert.deepEqual(
    runWithFlags.cohort.eligibleStates,
    [STATE],
    `Fixture is not exercising the intended state; expected state ${STATE} to be the eligible state.`,
  );
  assert.equal(
    runWithFlags.fittedOnTrainingOnly.stateMeanDurationS[STATE],
    EXPECTED_TRAIN_MEAN_EXCLUDING_CENSORED,
    "CENSORING SEMANTICS VIOLATED: the training mean dwell time for state "
      + `${STATE} is ${runWithFlags.fittedOnTrainingOnly.stateMeanDurationS[STATE]} s, but excluding the `
      + `right-censored dwells gives exactly ${EXPECTED_TRAIN_MEAN_EXCLUDING_CENSORED} s by hand `
      + "(72 s over 24 uncensored dwells). A value of "
      + `${EXPECTED_TRAIN_MEAN_IF_CENSORED_ADMITTED} s means right-censored dwells ENTERED the `
      + "uncensored duration likelihood, contradicting the frozen protocol rule "
      + "'exclude it from uncensored duration likelihoods'.",
  );
});

test("the fixture discriminates: admitting censored dwells changes the mean to a different hand-calculated value", () => {
  assert.equal(
    runFlagsStripped.fittedOnTrainingOnly.stateMeanDurationS[STATE],
    EXPECTED_TRAIN_MEAN_IF_CENSORED_ADMITTED,
    "This fixture no longer distinguishes inclusion from exclusion of censored dwells: with every "
      + "rightCensored flag forced false the training mean should be exactly "
      + `${EXPECTED_TRAIN_MEAN_IF_CENSORED_ADMITTED} s (96 s over 48 dwells). The exclusion assertion `
      + "above would therefore be vacuous.",
  );
  assert.notEqual(
    EXPECTED_TRAIN_MEAN_EXCLUDING_CENSORED,
    EXPECTED_TRAIN_MEAN_IF_CENSORED_ADMITTED,
    "Included and excluded means must differ for this gate to have power.",
  );
  assert.equal(
    runFlagsStripped.cohort.trainEvents,
    EXPECTED_TRAIN_COHORT_IF_CENSORED_ADMITTED,
    "Admitting censored dwells must enlarge the training cohort to 48; the fixture is not discriminating.",
  );
  assert.equal(
    runFlagsStripped.cohort.holdoutEvents,
    EXPECTED_HOLDOUT_COHORT_IF_CENSORED_ADMITTED,
    "Admitting censored dwells must enlarge the held-out cohort to 35; the fixture is not discriminating.",
  );
});

test("censored dwells exert zero influence on the likelihood: flagged-present run equals censored-absent run", () => {
  const message = "CENSORING SEMANTICS VIOLATED: removing the right-censored dwells from the record changed "
    + "the fitted/held-out result. A correctly excluded dwell cannot influence any likelihood quantity, "
    + "so a record containing flagged censored dwells must yield the same numbers as a record without them. "
    + "This difference means censored dwells are participating in the uncensored duration likelihood.";

  assert.deepEqual(
    runWithFlags.fittedOnTrainingOnly.stateMeanDurationS,
    runWithoutCensoredRows.fittedOnTrainingOnly.stateMeanDurationS,
    `${message} (field: fittedOnTrainingOnly.stateMeanDurationS)`,
  );
  assert.deepEqual(
    runWithFlags.fittedOnTrainingOnly.normalizedDurationModels,
    runWithoutCensoredRows.fittedOnTrainingOnly.normalizedDurationModels,
    `${message} (field: fittedOnTrainingOnly.normalizedDurationModels)`,
  );
  assert.deepEqual(
    runWithFlags.heldoutResults.meanLogScoreNatsPerEvent,
    runWithoutCensoredRows.heldoutResults.meanLogScoreNatsPerEvent,
    `${message} (field: heldoutResults.meanLogScoreNatsPerEvent)`,
  );
  assert.deepEqual(
    runWithFlags.heldoutResults.pairedMixtureAdvantageNatsPerEvent,
    runWithoutCensoredRows.heldoutResults.pairedMixtureAdvantageNatsPerEvent,
    `${message} (field: heldoutResults.pairedMixtureAdvantageNatsPerEvent)`,
  );
  assert.equal(
    runWithFlags.cohort.trainEvents,
    runWithoutCensoredRows.cohort.trainEvents,
    `${message} (field: cohort.trainEvents)`,
  );
  assert.equal(
    runWithFlags.cohort.holdoutEvents,
    runWithoutCensoredRows.cohort.holdoutEvents,
    `${message} (field: cohort.holdoutEvents)`,
  );
});

test("likelihood cohort sizes equal the independently counted uncensored eligible events", () => {
  // Counted here from the fixture by this test's own filter, not read from the pipeline.
  const eligible = (partition) => fixtureEvents.filter(
    (event) => event.partition === partition && event.stateN === STATE && event.rightCensored === false,
  ).length;

  const trainExpected = eligible("train");
  const holdoutExpected = eligible("holdout");

  assert.equal(trainExpected, EXPECTED_TRAIN_COHORT_EXCLUDING_CENSORED, "Fixture drifted: expected 24 uncensored train dwells.");
  assert.equal(holdoutExpected, EXPECTED_HOLDOUT_COHORT_EXCLUDING_CENSORED, "Fixture drifted: expected 25 uncensored holdout dwells.");

  assert.equal(
    runWithFlags.cohort.trainEvents,
    trainExpected,
    `CENSORING COHORT ACCOUNTING VIOLATED: ${runWithFlags.cohort.trainEvents} events entered the training `
      + `likelihood but only ${trainExpected} uncensored eligible training dwells exist in the record. `
      + `The surplus is ${runWithFlags.cohort.trainEvents - trainExpected} right-censored dwell(s) that must have been excluded.`,
  );
  assert.equal(
    runWithFlags.cohort.holdoutEvents,
    holdoutExpected,
    `CENSORING COHORT ACCOUNTING VIOLATED: ${runWithFlags.cohort.holdoutEvents} events were scored on the `
      + `held-out partition but only ${holdoutExpected} uncensored eligible held-out dwells exist in the record. `
      + `The surplus is ${runWithFlags.cohort.holdoutEvents - holdoutExpected} right-censored dwell(s) that must have been excluded.`,
  );
});

test("right-censored dwells are RETAINED in the record for provenance", () => {
  const censoredInFixture = fixtureEvents.filter((event) => event.rightCensored);
  assert.ok(censoredInFixture.length > 0, "Fixture must contain right-censored dwells to test retention.");

  // The analysis must not consume, drop, or rewrite the censored dwells it excludes.
  const censoredAfterRun = datasetWithFlags.events.filter((event) => event.rightCensored);
  assert.equal(
    censoredAfterRun.length,
    censoredInFixture.length,
    "PROVENANCE RETENTION VIOLATED: right-censored dwells were removed from the observation record. "
      + "The frozen protocol requires BOTH halves: 'Retain the last dwell as right-censored for provenance "
      + "but exclude it from uncensored duration likelihoods.' Exclusion from the likelihood must not be "
      + "implemented by deleting the observation.",
  );
  for (const event of censoredAfterRun) {
    assert.equal(
      event.rightCensored,
      true,
      `PROVENANCE RETENTION VIOLATED: censored dwell ${event.eventId} lost its rightCensored flag; a censored `
        + "dwell may never be relabelled as a completed, uncensored observation.",
    );
    assert.equal(
      event.direction,
      null,
      `PROVENANCE RETENTION VIOLATED: censored dwell ${event.eventId} carries a transition direction. A dwell `
        + "whose end was never observed cannot have an observed direction.",
    );
    assert.ok(
      Number.isFinite(event.durationS) && event.durationS > 0,
      `PROVENANCE RETENTION VIOLATED: censored dwell ${event.eventId} lost its recorded duration.`,
    );
  }

  // The provenance census counts every dwell; the likelihood cohorts count only the uncensored ones.
  assert.equal(
    runWithFlags.cohort.sourceEvents,
    fixtureEvents.length,
    "PROVENANCE RETENTION VIOLATED: the reported source-event census does not equal the total number of "
      + "recorded dwells. Right-censored dwells must still be counted as observed provenance even though "
      + "they are excluded from the likelihood.",
  );
  assert.equal(
    runWithFlags.cohort.sourceEvents - (runWithFlags.cohort.trainEvents + runWithFlags.cohort.holdoutEvents),
    censoredInFixture.length,
    "CENSORING BOOKKEEPING VIOLATED: the gap between the retained provenance census and the combined "
      + "likelihood cohorts must be exactly the number of right-censored dwells "
      + `(${censoredInFixture.length}). It is `
      + `${runWithFlags.cohort.sourceEvents - (runWithFlags.cohort.trainEvents + runWithFlags.cohort.holdoutEvents)}.`,
  );
});

test("the frozen protocol still declares both halves of the censoring rule", () => {
  const protocolPath = path.join(root, "experiments/preregistration.v1.json");
  const frozen = JSON.parse(fs.readFileSync(protocolPath, "utf8"));
  const rules = frozen?.extraction?.rules ?? [];
  const censoringRule = rules.find((rule) => /right-censored/i.test(rule));

  assert.ok(
    censoringRule,
    "FROZEN PROTOCOL RULE MISSING: experiments/preregistration.v1.json no longer contains any extraction "
      + "rule governing right-censored dwells. The censoring treatment asserted by this gate would be unbound.",
  );
  assert.match(
    censoringRule,
    /retain/i,
    "FROZEN PROTOCOL RULE WEAKENED: the right-censoring rule no longer requires RETAINING the censored dwell "
      + `for provenance. Current text: "${censoringRule}"`,
  );
  assert.match(
    censoringRule,
    /provenance/i,
    "FROZEN PROTOCOL RULE WEAKENED: the right-censoring rule no longer states that retention is for PROVENANCE. "
      + `Current text: "${censoringRule}"`,
  );
  assert.match(
    censoringRule,
    /exclude/i,
    "FROZEN PROTOCOL RULE WEAKENED: the right-censoring rule no longer requires EXCLUDING the censored dwell "
      + `from the uncensored duration likelihoods. Current text: "${censoringRule}"`,
  );
  assert.match(
    censoringRule,
    /likelihood/i,
    "FROZEN PROTOCOL RULE WEAKENED: the right-censoring rule no longer names the LIKELIHOOD as the thing the "
      + `censored dwell is excluded from. Current text: "${censoringRule}"`,
  );
});
