// Semantic gate: train/holdout motor independence.
//
// WHAT THIS GATE ASSERTS (and why it is not a regression lock):
//
//   The experimental unit of independence declared in experiments/preregistration.v1.json
//   is the motor/cell. Every scientific claim in the observed experiment is a HELD-OUT
//   claim: parameters are fitted on training motors and scored on motors the fit never
//   saw. If one motor's events straddle the partition boundary, or if any holdout
//   observation reaches a fitted parameter, the held-out claim is void -- the numbers may
//   still be self-consistent and every hash in the repository may still agree.
//
//   This file therefore asserts the PROPERTY, not the bytes:
//     G1  runObservedExperiment REFUSES a dataset in which one motor appears in both
//         partitions, and the refusal names motor leakage.
//     G2  On the real frozen dataset the partitions are disjoint at motor granularity,
//         and every motor's partition equals the preregistered split rule recomputed
//         here from the motor name (the stored `partition` / `splitRemainder` fields
//         are treated as untrusted and are checked, not believed).
//     G3  Fitted parameters are a function of TRAINING data only. Proven two ways:
//         (a) on a synthetic fixture whose holdout values are deliberately far from the
//             training values, the fitted state mean and the fitted direction
//             probability equal HAND-CALCULATED training-only values (1.75 s and
//             12.5/31) and are nowhere near the pooled values (9.625 s and 42.5/61);
//         (b) on the real frozen dataset, arbitrarily corrupting every holdout duration
//             and every holdout direction leaves `fittedOnTrainingOnly` bit-identical
//             while `heldoutResults` moves -- an invariance test with a live negative
//             control.
//
// NON-CIRCULARITY: no sha256 of any artifact, no runId, no comparison against
// experiments/results/*.json, and no stored expected number produced by this pipeline is
// used anywhere below. G3(a)'s expectations are arithmetic done by hand from the fixture
// this file constructs. G2 recomputes the split with node:crypto -- that is the
// preregistered split FUNCTION (`sha256(motorName) mod 5`), i.e. a scientific definition
// being re-derived, not an artifact digest being compared.
//
// DETERMINISM: no network, no clock, no dependence on experiments/upstream-cache/.
// Bootstrap replicate counts are lowered on in-test COPIES of the protocol object purely
// for runtime; replicate count cannot affect any fitted parameter (see fitDurationModels,
// which never reads protocol.uncertainty).

import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { runObservedExperiment } from "../../lib/observed-experiment.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");
const readJson = (...parts) => JSON.parse(fs.readFileSync(path.join(root, ...parts), "utf8"));

// ---------------------------------------------------------------------------
// Synthetic fixture construction.
//
// runObservedExperiment reads exactly these event fields: motorId, partition, stateN,
// durationS, direction, rightCensored. It reads dataset.protocolId, dataset.ingestion
// .{motorCount,eventCount,exclusions} (report bookkeeping only), and from the protocol
// scope.primaryStates, split.method, uncertainty.{seed,replicates}.
//
// FABRICATED MINIMUM: `ingestion` counts/exclusions and `split.method` are report-only
// strings and are set to obviously synthetic values; they cannot influence any assertion
// below. Every field that participates in arithmetic is constructed explicitly here.
// ---------------------------------------------------------------------------

const SYNTHETIC_PROTOCOL = {
  protocolId: "SEMANTIC-FIXTURE-LEAKAGE",
  scope: { primaryStates: [1] },
  split: { method: "synthetic fixture: partition assigned literally, not by hash" },
  uncertainty: { seed: 7, replicates: 8 },
};

// 2 of every 5 training events are "on" -> exactly 12 "on" out of 30.
const trainDirection = (index) => (index % 5 === 0 || index % 5 === 1 ? "on" : "off");

function syntheticEvent({ motorId, partition, durationS, direction }) {
  return { motorId, partition, stateN: 1, durationS, direction, rightCensored: false };
}

// 5 training motors x 6 events, durations {0.5,1.0,1.5,2.0,2.5,3.0}s.
//   training sum = 5 * 10.5 = 52.5 s over 30 events -> training mean = 1.75 s exactly.
// 5 holdout motors x 6 events, durations {5,10,15,20,25,30}s.
//   holdout sum = 5 * 105 = 525 s over 30 events.
//   pooled mean would be (52.5 + 525) / 60 = 9.625 s -- 5.5x the training mean.
// All 30 holdout events are "on"; only 12 of 30 training events are.
//   training-only Jeffreys estimate = (12 + 0.5) / (30 + 1) = 12.5 / 31.
//   pooled estimate would be (42 + 0.5) / (60 + 1) = 42.5 / 61.
function buildCleanSyntheticDataset() {
  const events = [];
  let trainIndex = 0;
  for (let motor = 1; motor <= 5; motor += 1) {
    for (let j = 1; j <= 6; j += 1) {
      events.push(syntheticEvent({
        motorId: `TRAIN-${motor}`,
        partition: "train",
        durationS: 0.5 * j,
        direction: trainDirection(trainIndex),
      }));
      trainIndex += 1;
    }
  }
  for (let motor = 1; motor <= 5; motor += 1) {
    for (let j = 1; j <= 6; j += 1) {
      events.push(syntheticEvent({
        motorId: `HOLDOUT-${motor}`,
        partition: "holdout",
        durationS: 5 * j,
        direction: "on",
      }));
    }
  }
  return {
    protocolId: SYNTHETIC_PROTOCOL.protocolId,
    ingestion: { motorCount: 10, eventCount: events.length, exclusions: { synthetic: true } },
    events,
  };
}

// The clean fixture plus ONE motor whose events straddle the partition boundary.
// Counts stay above every eligibility floor (>=20 train events, >=20 holdout events,
// >=5 distinct holdout motors), so with the guard removed this dataset analyses to
// completion rather than failing for some unrelated reason.
function buildLeakingSyntheticDataset() {
  const dataset = buildCleanSyntheticDataset();
  const events = [...dataset.events];
  for (let j = 1; j <= 4; j += 1) {
    events.push(syntheticEvent({
      motorId: "MOTOR-IN-BOTH-PARTITIONS",
      partition: "train",
      durationS: 0.5 * j,
      direction: "on",
    }));
    events.push(syntheticEvent({
      motorId: "MOTOR-IN-BOTH-PARTITIONS",
      partition: "holdout",
      durationS: 5 * j,
      direction: "on",
    }));
  }
  return { ...dataset, ingestion: { ...dataset.ingestion, eventCount: events.length }, events };
}

// ---------------------------------------------------------------------------
// G1 -- the guard itself.
// ---------------------------------------------------------------------------

test("G1 a motor present in both partitions is refused, and the refusal names motor leakage", () => {
  const leaking = buildLeakingSyntheticDataset();

  const trainMotors = new Set(leaking.events.filter((e) => e.partition === "train").map((e) => e.motorId));
  const holdoutMotors = new Set(leaking.events.filter((e) => e.partition === "holdout").map((e) => e.motorId));
  const straddling = [...trainMotors].filter((id) => holdoutMotors.has(id));
  assert.deepEqual(
    straddling,
    ["MOTOR-IN-BOTH-PARTITIONS"],
    "FIXTURE SELF-CHECK FAILED: the synthetic dataset was supposed to contain exactly one "
      + "motor straddling the train/holdout boundary. The gate below would be vacuous.",
  );

  let thrown = null;
  let returned = null;
  try {
    returned = runObservedExperiment(leaking, SYNTHETIC_PROTOCOL, {});
  } catch (error) {
    thrown = error;
  }

  if (thrown === null) {
    assert.fail(
      "TRAIN/HOLDOUT MOTOR INDEPENDENCE IS NOT ENFORCED.\n"
      + "runObservedExperiment ACCEPTED a dataset in which motor 'MOTOR-IN-BOTH-PARTITIONS' "
      + "contributes 4 uncensored events to the training partition and 4 to the holdout "
      + "partition, and returned a finished report claiming "
      + `audit.noMotorLeakage = ${JSON.stringify(returned?.audit?.noMotorLeakage)} over `
      + `${returned?.cohort?.holdoutMotors} holdout motors.\n`
      + "The preregistered unit of independence is the motor/cell "
      + "(experiments/preregistration.v1.json -> scope.unitOfIndependence, "
      + "split.leakageControl, qualityGates: 'No motor may appear in both train and holdout "
      + "partitions'). With that rule unenforced, every held-out claim (H1, H2, H4) is "
      + "scored partly on motors whose own events set the fitted parameters, so the "
      + "reported held-out advantage is no longer a held-out quantity.",
    );
  }

  const message = String(thrown && thrown.message);
  assert.match(
    message,
    /leak/i,
    "The leaking dataset was rejected, but NOT for leakage. The refusal must name the "
    + "violated property -- one motor appearing in both the train and holdout partitions -- "
    + `so that a reader can tell partition contamination from an unrelated failure. Actual refusal: ${message}`,
  );
});

// ---------------------------------------------------------------------------
// G2 -- the invariant the guard exists to protect, on the real frozen dataset.
// ---------------------------------------------------------------------------

test("G2 the frozen dataset's partitions are disjoint at motor granularity", () => {
  const dataset = readJson("experiments", "data", "wadhwa-2022-events.json");
  const byPartition = new Map();
  for (const event of dataset.events) {
    if (!byPartition.has(event.partition)) byPartition.set(event.partition, new Set());
    byPartition.get(event.partition).add(event.motorId);
  }
  assert.deepEqual(
    [...byPartition.keys()].sort(),
    ["holdout", "train"],
    "The frozen dataset declares partitions other than exactly {train, holdout}. The "
    + "two-partition held-out design is not what the data implements.",
  );

  const train = byPartition.get("train");
  const holdout = byPartition.get("holdout");
  const straddling = [...train].filter((id) => holdout.has(id)).sort();
  assert.deepEqual(
    straddling,
    [],
    "MOTOR LEAKAGE IN THE FROZEN DATASET: these motors contribute events to BOTH the "
    + `training and the holdout partition: ${JSON.stringify(straddling)}. `
    + "Held-out scores computed from this dataset are contaminated by the fitting set at "
    + "the declared unit of independence (motor/cell).",
  );
  assert.ok(
    train.size > 0 && holdout.size > 0,
    `Degenerate split: train motors = ${train.size}, holdout motors = ${holdout.size}. `
    + "A held-out claim requires both partitions to be non-empty.",
  );
});

test("G2 every motor's partition equals the preregistered sha256(motorName) mod 5 rule, recomputed here", () => {
  const dataset = readJson("experiments", "data", "wadhwa-2022-events.json");
  const protocol = readJson("experiments", "preregistration.v1.json");

  const trainingRemainders = new Set(protocol.split.trainingRemainders);
  const holdoutRemainders = new Set(protocol.split.holdoutRemainders);
  assert.ok(
    trainingRemainders.size > 0 && holdoutRemainders.size > 0,
    "The preregistration no longer declares both training and holdout remainder classes; "
    + "the split rule is not a partition of the motor population.",
  );
  for (const remainder of trainingRemainders) {
    assert.ok(
      !holdoutRemainders.has(remainder),
      `Remainder class ${remainder} is declared as BOTH a training and a holdout class in `
      + "experiments/preregistration.v1.json. The preregistered split rule itself assigns "
      + "some motors to both sides, which is motor leakage written into the protocol.",
    );
  }
  const declaredClasses = [...trainingRemainders, ...holdoutRemainders].sort((a, b) => a - b);
  assert.deepEqual(
    declaredClasses,
    [0, 1, 2, 3, 4],
    "The preregistered remainder classes do not cover 0..4 exactly once, so 'sha256 mod 5' "
    + `does not assign every motor to exactly one partition. Declared: ${JSON.stringify(declaredClasses)}`,
  );

  // Independent re-derivation of the split. The stored `partition` and `splitRemainder`
  // fields are inputs under test, not oracles.
  const expectedPartition = (motorId) => {
    const digest = crypto.createHash("sha256").update(motorId, "utf8").digest("hex");
    const remainder = Number(BigInt(`0x${digest}`) % 5n);
    if (holdoutRemainders.has(remainder)) return { partition: "holdout", remainder };
    if (trainingRemainders.has(remainder)) return { partition: "train", remainder };
    return { partition: null, remainder };
  };

  const misassigned = [];
  const seen = new Map();
  for (const event of dataset.events) {
    if (!seen.has(event.motorId)) seen.set(event.motorId, expectedPartition(event.motorId));
    const expected = seen.get(event.motorId);
    if (event.partition !== expected.partition) {
      misassigned.push({
        motorId: event.motorId,
        storedPartition: event.partition,
        storedRemainder: event.splitRemainder,
        recomputedRemainder: expected.remainder,
        requiredPartition: expected.partition,
      });
    }
  }

  assert.deepEqual(
    misassigned.slice(0, 5),
    [],
    "SPLIT ASSIGNMENT DOES NOT FOLLOW THE PREREGISTERED RULE. The preregistration freezes "
    + "the partition as a deterministic function of the motor NAME "
    + `(${JSON.stringify(protocol.split.method)}, holdout remainders `
    + `${JSON.stringify(protocol.split.holdoutRemainders)}). Recomputing that function here `
    + `disagrees with the dataset's stored partition for ${misassigned.length} event(s) `
    + `across ${new Set(misassigned.map((row) => row.motorId)).size} motor(s). `
    + "A partition that is not a fixed function of the motor identity can be chosen after "
    + "seeing outcomes, which is exactly the freedom the frozen split exists to remove. "
    + `First offenders: ${JSON.stringify(misassigned.slice(0, 5))}`,
  );

  assert.ok(
    seen.size >= 2,
    `Only ${seen.size} distinct motor(s) in the frozen dataset; a motor-clustered held-out `
    + "design is not identifiable.",
  );
});

// ---------------------------------------------------------------------------
// G3 -- no holdout observation reaches a fitted parameter.
// ---------------------------------------------------------------------------

// Returns a dotted path to the first structural or numeric difference, or null.
function firstDifference(a, b, at = "") {
  if (Object.is(a, b)) return null;
  if (typeof a !== typeof b || a === null || b === null) return at || "<root>";
  if (typeof a !== "object") return at || "<root>";
  if (Array.isArray(a) !== Array.isArray(b)) return at || "<root>";
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const key of [...keys].sort()) {
    const where = at ? `${at}.${key}` : key;
    if (!(key in a) || !(key in b)) return where;
    const difference = firstDifference(a[key], b[key], where);
    if (difference !== null) return difference;
  }
  return null;
}

test("G3 fitted parameters equal HAND-CALCULATED training-only values, not pooled values", () => {
  const dataset = buildCleanSyntheticDataset();
  const report = runObservedExperiment(dataset, SYNTHETIC_PROTOCOL, {});

  // Hand arithmetic, done from the fixture definition above, not from any artifact:
  //   training durations for N=1: 5 motors x {0.5,1.0,1.5,2.0,2.5,3.0} = 52.5 s / 30 events
  const HAND_TRAINING_MEAN_S = 1.75;
  //   pooling holdout in would give (52.5 + 525) / 60
  const POOLED_MEAN_S = 9.625;
  //   training "on" events: 12 of 30, Jeffreys -> (12 + 0.5) / (30 + 1)
  const HAND_TRAINING_ON_PROBABILITY = 12.5 / 31;
  //   pooling holdout in would give (12 + 30 + 0.5) / (30 + 30 + 1)
  const POOLED_ON_PROBABILITY = 42.5 / 61;

  const fittedMean = report.fittedOnTrainingOnly.stateMeanDurationS[1];
  assert.equal(
    fittedMean,
    HAND_TRAINING_MEAN_S,
    "HOLDOUT DURATIONS REACHED A FITTED PARAMETER. The per-state mean dwell time is a "
    + "TRAINING-ONLY normalisation constant, and on this fixture its hand-calculated value "
    + `is 52.5 s / 30 training events = ${HAND_TRAINING_MEAN_S} s. Observed `
    + `${fittedMean} s. The value obtained by pooling the holdout events in would be `
    + `${POOLED_MEAN_S} s. If the fitted normalisation has seen holdout durations, the `
    + "held-out log-score comparison (H2) is scored against a scale the holdout data helped "
    + "choose, and it is no longer a held-out comparison.",
  );

  const fittedOn = report.fittedOnTrainingOnly.direction.globalOnProbability;
  assert.equal(
    fittedOn,
    HAND_TRAINING_ON_PROBABILITY,
    "HOLDOUT TRANSITION DIRECTIONS REACHED A FITTED PARAMETER. The global on-probability is "
    + "a training-only Jeffreys estimate; on this fixture 12 of 30 training events are 'on', "
    + `so it must equal (12 + 0.5) / (30 + 1) = ${HAND_TRAINING_ON_PROBABILITY}. Observed `
    + `${fittedOn}. The value obtained by pooling the holdout events in (all 30 of which are `
    + `'on') would be ${POOLED_ON_PROBABILITY}. A direction predictor that has seen held-out `
    + "outcomes cannot support H4.",
  );

  const fittedByState = report.fittedOnTrainingOnly.direction.onProbabilityByState[1];
  assert.equal(
    fittedByState,
    HAND_TRAINING_ON_PROBABILITY,
    "The state-conditioned on-probability for N=1 is not the training-only Jeffreys "
    + `estimate (12 + 0.5) / (30 + 1) = ${HAND_TRAINING_ON_PROBABILITY}; observed `
    + `${fittedByState}. Pooled-with-holdout would be ${POOLED_ON_PROBABILITY}.`,
  );

  assert.equal(
    report.cohort.trainEvents,
    30,
    `Fixture self-check: expected 30 eligible training events, saw ${report.cohort.trainEvents}. `
    + "The hand-calculated expectations above assume that count.",
  );
  assert.equal(
    report.cohort.holdoutEvents,
    30,
    `Fixture self-check: expected 30 eligible holdout events, saw ${report.cohort.holdoutEvents}. `
    + "If the holdout events were silently dropped, the separation between the training-only "
    + "and pooled expectations above would be untested.",
  );
});

test("G3 corrupting every holdout observation leaves the real dataset's fitted parameters unmoved", () => {
  const dataset = readJson("experiments", "data", "wadhwa-2022-events.json");
  const protocol = readJson("experiments", "preregistration.v1.json");
  // Replicate count affects only bootstrap intervals in heldoutResults, never a fitted
  // parameter. Lowered here on an in-test copy purely to keep this gate fast; no
  // repository file is modified.
  protocol.uncertainty = { ...protocol.uncertainty, replicates: 24 };

  const baseline = runObservedExperiment(dataset, protocol, {});

  // Deterministic, hash-free corruption of the holdout half only: stretch every held-out
  // duration by 37x and force every held-out transition direction to "on". Counts,
  // motor identities, states and censoring flags are untouched, so eligibility and the
  // partition structure are identical; only holdout VALUES move.
  const corrupted = {
    ...dataset,
    events: dataset.events.map((event) => (event.partition === "holdout"
      ? { ...event, durationS: event.durationS * 37, direction: "on" }
      : event)),
  };
  const perturbed = runObservedExperiment(corrupted, protocol, {});

  const fittedDifference = firstDifference(
    baseline.fittedOnTrainingOnly,
    perturbed.fittedOnTrainingOnly,
  );
  assert.equal(
    fittedDifference,
    null,
    "A FITTED PARAMETER DEPENDS ON HELD-OUT DATA. Every held-out duration was multiplied by "
    + "37 and every held-out transition direction was forced to 'on'; no training event was "
    + `touched. The fitted quantity at fittedOnTrainingOnly.${fittedDifference} nevertheless `
    + `changed from ${JSON.stringify(getPath(baseline.fittedOnTrainingOnly, fittedDifference))} `
    + `to ${JSON.stringify(getPath(perturbed.fittedOnTrainingOnly, fittedDifference))}. `
    + "Training-only fitting means exactly this: holdout observations must be able to move "
    + "arbitrarily without moving a single fitted parameter. They moved one, so H1/H2/H4 are "
    + "not held-out results.",
  );

  const cohortDifference = firstDifference(
    { trainMotors: baseline.cohort.trainMotors, trainEvents: baseline.cohort.trainEvents, eligibleStates: baseline.cohort.eligibleStates },
    { trainMotors: perturbed.cohort.trainMotors, trainEvents: perturbed.cohort.trainEvents, eligibleStates: perturbed.cohort.eligibleStates },
  );
  assert.equal(
    cohortDifference,
    null,
    `The training cohort itself (${cohortDifference}) changed when only holdout VALUES were `
    + "perturbed. Which motors and events are used for fitting must not depend on held-out "
    + "observations.",
  );

  // Negative control: the perturbation must actually be consequential downstream, otherwise
  // the invariance above could pass vacuously (e.g. if holdout events were being dropped).
  const heldoutDifference = firstDifference(baseline.heldoutResults, perturbed.heldoutResults);
  assert.notEqual(
    heldoutDifference,
    null,
    "NEGATIVE CONTROL FAILED: multiplying every held-out duration by 37 and forcing every "
    + "held-out direction to 'on' changed NOTHING in heldoutResults. The held-out scores are "
    + "therefore not functions of the held-out observations, so the invariance asserted above "
    + "is vacuous and this gate proves nothing.",
  );
});

function getPath(object, dotted) {
  if (!dotted) return undefined;
  return dotted.split(".").reduce((current, key) => (current == null ? current : current[key]), object);
}
