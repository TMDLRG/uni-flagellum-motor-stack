// Semantic gate: seconds-scale predictive density and finite-sample dispersion.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   properties D1P01_SECONDS_DENSITY_JACOBIAN and D1P03_SAMPLE_VARIANCE_BESSEL.
//
// This gate asserts the MEANING of two declared statistical properties, not the
// stability of any artifact. It routes through NO sha256, NO runId, NO committed
// report file and NO snapshot. Every expected value below is a closed-form rational
// or logarithm computed by hand from the literal fixture durations, so the oracle is
// arithmetic and never the pipeline.
//
// Oracle independence: scoreEvents, logDensity and the model-fitting routines are
// module-private and are never called by this file. The expectations are derived
// from the declared equations, not from production output.
//
// Target corruptions (Phase-C survivors CXM01 and CXM03, plus alternate forms):
//   D1X01 jacobian deleted        D1A01 jacobian sign inverted
//   D1X03 n-1 replaced by n       D1A03 n-1 replaced by n+1

import test from "node:test";
import assert from "node:assert/strict";

import { runObservedExperiment, sampleVariance } from "../../lib/observed-experiment.js";

const PROTOCOL_ID = "SYNTHETIC-D1-DENSITY-SCALE-GATE";
const STATE = 2;

// ---------------------------------------------------------------------------
// Synthetic fixture with hand-calculable per-state means.
//
// TRAIN,   state 2, uncensored: 4 motors x (1,3,5,1,3,5) s = 24 dwells
//     sum = 4 * 18 = 72 s over 24 dwells -> training scale = 3 s EXACTLY
// HOLDOUT, state 2, uncensored: 5 motors x (1,2,3,4,5) s = 25 dwells
//     sum = 5 * 15 = 75 s over 25 dwells -> holdout mean = 3 s EXACTLY
//
// The memoryless model has logDensity(y) = -y on the NORMALIZED scale, where
// y = t / scale. Reporting that score on the SECONDS scale requires the
// change-of-variables Jacobian -log(scale):
//
//     log p_T(t) = log p_Y(t / scale) - log(scale)
//
// so the mean held-out log score is
//
//     -(mean(t) / scale) - log(scale) = -(3/3) - ln(3) = -1 - ln(3)
//
// If the Jacobian is omitted the same quantity is exactly -1.
// If its sign is inverted the same quantity is -1 + ln(3).
// The three values are separated by ln(3) = 1.0986... which is 10^12 times the
// declared tolerance.
//
// Dispersion: the 25 holdout durations are five copies of (1,2,3,4,5), so the
// mean is 3 and the summed squared deviation is 5 * (4+1+0+1+4) = 50 over n = 25.
//     sample variance   = 50 / 24            (Bessel, n-1)
//     population value  = 50 / 25
//     cvSquared         = (50/24) / 3^2 = 0.2314814814814815 EXACTLY
// ---------------------------------------------------------------------------

const EXPECTED_MEAN_LOG_SCORE_SECONDS = -1 - Math.log(3);
const VALUE_IF_JACOBIAN_OMITTED = -1;
const VALUE_IF_JACOBIAN_SIGN_INVERTED = -1 + Math.log(3);
const EXPECTED_CV_SQUARED = (50 / 24) / 9;
const VALUE_IF_POPULATION_VARIANCE = (50 / 25) / 9;
const TOLERANCE = 1e-12;

function makeEvent({ motorId, index, partition, durationS }) {
  return {
    eventId: `${motorId}:${String(index).padStart(4, "0")}`,
    motorId,
    partition,
    splitRemainder: partition === "train" ? 1 : 0,
    stateN: STATE,
    enteredAtS: 100 + index,
    durationS,
    eventAtS: 100 + index + durationS,
    nextStateN: STATE + (index % 2 === 0 ? 1 : -1),
    direction: index % 2 === 0 ? "on" : "off",
    jump: index % 2 === 0 ? 1 : -1,
    rightCensored: false,
  };
}

/** timeUnitScale = 1 expresses durations in seconds; 2 expresses the SAME dwells in half-seconds. */
function buildFixtureEvents(timeUnitScale) {
  const events = [];
  const trainDurations = [1, 3, 5, 1, 3, 5];
  for (let motor = 0; motor < 4; motor += 1) {
    for (let i = 0; i < trainDurations.length; i += 1) {
      events.push(makeEvent({
        motorId: `train-motor-${motor}`,
        index: i + 1,
        partition: "train",
        durationS: trainDurations[i] * timeUnitScale,
      }));
    }
  }
  for (let motor = 0; motor < 5; motor += 1) {
    for (let i = 1; i <= 5; i += 1) {
      events.push(makeEvent({
        motorId: `holdout-motor-${motor}`,
        index: i,
        partition: "holdout",
        durationS: i * timeUnitScale,
      }));
    }
  }
  return events;
}

function buildDataset(events) {
  return {
    schema: "uni.flagellum.synthetic-d1-density-fixture/1.0.0",
    protocolId: PROTOCOL_ID,
    ingestion: {
      script: "tests/semantic/density-scale-and-dispersion.semantic.test.mjs",
      motorCount: new Set(events.map((event) => event.motorId)).size,
      eventCount: events.length,
      exclusions: [],
    },
    motors: [...new Set(events.map((event) => event.motorId))].sort(),
    events,
  };
}

const protocol = {
  protocolId: PROTOCOL_ID,
  scope: { primaryStates: [STATE] },
  split: { method: "synthetic fixture: motor name prefix" },
  uncertainty: { replicates: 8, seed: 20260720, interval: "Percentile 95%" },
};

const runSeconds = runObservedExperiment(buildDataset(buildFixtureEvents(1)), protocol, { fixture: "synthetic" });
const runHalfSeconds = runObservedExperiment(buildDataset(buildFixtureEvents(2)), protocol, { fixture: "synthetic" });

test("D1P01 seconds-scale predictive density carries the change-of-variables jacobian", () => {
  assert.equal(
    runSeconds.fittedOnTrainingOnly.stateMeanDurationS[STATE],
    3,
    "Fixture precondition failed: the training-only duration scale must be exactly 3 s.",
  );
  assert.equal(
    runSeconds.cohort.holdoutEvents,
    25,
    "Fixture precondition failed: the held-out cohort must contain exactly 25 dwells.",
  );

  const observed = runSeconds.heldoutResults.meanLogScoreNatsPerEvent.exponential;

  assert.ok(
    Math.abs(observed - EXPECTED_MEAN_LOG_SCORE_SECONDS) < TOLERANCE,
    "The seconds-scale mean log predictive density is missing or misapplying its change-of-variables jacobian. " +
      `Hand-calculated seconds-scale value -1 - ln(3) = ${EXPECTED_MEAN_LOG_SCORE_SECONDS}, observed ${observed}. ` +
      "A density reported in nats per event on the seconds scale must include the jacobian -log(scale); " +
      "omitting it reports a density on normalized duration while labelling it a seconds-scale density.",
  );

  assert.ok(
    Math.abs(observed - VALUE_IF_JACOBIAN_OMITTED) > 1,
    "The seconds-scale mean log predictive density equals the value obtained when the jacobian is OMITTED " +
      `(${VALUE_IF_JACOBIAN_OMITTED}). The change-of-variables term is absent.`,
  );
  assert.ok(
    Math.abs(observed - VALUE_IF_JACOBIAN_SIGN_INVERTED) > 1,
    "The seconds-scale mean log predictive density equals the value obtained when the jacobian sign is INVERTED " +
      `(${VALUE_IF_JACOBIAN_SIGN_INVERTED}). The change-of-variables term has the wrong sign.`,
  );
});

test("D1P01 seconds-scale predictive density is equivariant under unit reparameterization", () => {
  // The SAME dwells re-expressed in half-seconds leave the normalized duration y
  // unchanged and multiply the scale by k = 2. A correctly normalized seconds-scale
  // density must therefore shift by exactly -ln(k). With the jacobian omitted the
  // shift is exactly zero, because the normalized-scale density is unit-invariant.
  const shift =
    runHalfSeconds.heldoutResults.meanLogScoreNatsPerEvent.exponential -
    runSeconds.heldoutResults.meanLogScoreNatsPerEvent.exponential;

  assert.ok(
    Math.abs(shift - -Math.log(2)) < TOLERANCE,
    "The reported predictive density is not a proper seconds-scale density under change-of-variables. " +
      `Re-expressing every dwell in half-seconds must shift the mean log score by exactly -ln(2) = ${-Math.log(2)}, ` +
      `observed shift ${shift}. A shift of zero means the jacobian is absent and the quantity is a density on ` +
      "normalized duration, not an absolute predictive density in nats per event on the seconds scale.",
  );
});

test("D1P03 sample variance uses the bessel n-1 denominator", () => {
  // Literal fixture: mean 5, summed squared deviation 32, n = 8.
  const values = [2, 4, 4, 4, 5, 5, 7, 9];
  const observed = sampleVariance(values);

  assert.ok(
    Math.abs(observed - 32 / 7) < TOLERANCE,
    "sampleVariance does not apply the Bessel n-1 denominator. " +
      `For [2,4,4,4,5,5,7,9] the hand-calculated sample variance is 32/7 = ${32 / 7}, observed ${observed}. ` +
      "A quantity reported as a sample variance must be the unbiased estimate.",
  );
  assert.ok(
    Math.abs(observed - 32 / 8) > 0.5,
    `sampleVariance returned the POPULATION value 32/8 = ${32 / 8}. The Bessel n-1 denominator has been dropped, ` +
      "which systematically shrinks every finite-sample dispersion estimate while still reporting it as a sample estimate.",
  );
  assert.ok(
    Math.abs(sampleVariance([1, 3]) - 2) < TOLERANCE,
    `sampleVariance([1,3]) must equal 2 under the n-1 denominator, observed ${sampleVariance([1, 3])}. ` +
      "The population denominator gives 1 and an n+1 denominator gives 2/3.",
  );
  assert.equal(
    sampleVariance([5]),
    0,
    "sampleVariance must return 0 for n < 2 by the declared rule; a sample variance is undefined for one observation.",
  );
});

test("D1P03 reported cvSquared propagates the bessel n-1 denominator into the held-out state summary", () => {
  // Structurally independent of the exported helper: this asserts the REPORT-level
  // quantity, so a corruption that bypasses sampleVariance is still detected.
  const observed = runSeconds.heldoutResults.stateSummary[0].cvSquared;

  assert.ok(
    Math.abs(observed - EXPECTED_CV_SQUARED) < TOLERANCE,
    "The reported held-out cvSquared does not carry the Bessel n-1 denominator. " +
      `Twenty-five holdout dwells of five copies of (1,2,3,4,5) have mean 3 and summed squared deviation 50, so ` +
      `cvSquared = (50/24)/9 = ${EXPECTED_CV_SQUARED}, observed ${observed}. ` +
      "This is a sample variance divided by a squared mean and must use the n-1 denominator.",
  );
  assert.ok(
    Math.abs(observed - VALUE_IF_POPULATION_VARIANCE) > 1e-3,
    `The reported cvSquared equals the POPULATION-denominator value (50/25)/9 = ${VALUE_IF_POPULATION_VARIANCE}. ` +
      "Overdispersion is being understated because the sample variance lost its Bessel correction.",
  );
});
