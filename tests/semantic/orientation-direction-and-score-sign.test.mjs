// SEMANTIC GATE: orientation of the direction outcome and of every paired
// model-comparison score.
//
// WHAT THIS GATE IS FOR
// ---------------------
// Two corruption classes previously reached the audit undetected except as a
// SHA-256 mismatch on the emitted report:
//
//   M01  lib/observed-experiment.js  directionMetrics()
//        `event.direction === "on" ? 1 : 0`  ->  `? 0 : 1`
//   M05  lib/observed-experiment.js  runObservedExperiment()
//        `event.logScores.mixture - event.logScores.weibull`
//        ->  `event.logScores.weibull - event.logScores.mixture`
//
// Both are ORIENTATION errors: the magnitude of a quantity is preserved and its
// MEANING is reversed. A digest can only report that a byte moved. This gate
// asserts the meaning.
//
// DESIGN RULES OBEYED HERE
//   * No sha256, no runId, no artifact digest, no committed-report comparison.
//     Deleting every hash in the repository would not affect this file.
//   * No fresh-vs-stored comparison against anything this implementation wrote.
//   * Fixtures are synthetic and constructed so the correct answers are
//     HAND-CALCULABLE in closed form, written here as arithmetic on integers.
//   * The protocol object is built inline. The gate never reads
//     experiments/preregistration.v1.json, experiments/data/, or
//     experiments/upstream-cache/, and touches no clock and no network.
//
// PUBLIC SURFACE NOTE
//   `directionMetrics`, `scoreEvents` and `logDensity` are NOT exported from
//   lib/observed-experiment.js. This gate therefore drives the whole pipeline
//   through the exported `runObservedExperiment(dataset, protocol, identities)`
//   and reads the orientation-bearing fields off the returned report. No export
//   change is proposed, because none could be verified from here.

import test from "node:test";
import assert from "node:assert/strict";
import { runObservedExperiment } from "../../lib/observed-experiment.js";

// ---------------------------------------------------------------------------
// Fixture construction
// ---------------------------------------------------------------------------

const PROTOCOL_ID = "SYNTHETIC-ORIENTATION-FIXTURE";

// Ground-truth two-timescale mixture on the mean-one normalized time axis.
// weightFast/rateFast/rateSlow satisfy w/rf + (1-w)/rs = 1, so E[y] = 1:
//   0.7/5 + 0.3/rs = 1  ->  rs = 0.3/0.86
// This is the M3_UNI_TWO_TIMESCALE family itself. The exponential, Weibull and
// lognormal baselines are therefore MIS-SPECIFIED BY CONSTRUCTION for this
// data, which is what makes the sign of every paired advantage predictable
// without reading it off the pipeline.
const TRUE_WEIGHT_FAST = 0.7;
const TRUE_RATE_FAST = 5;
const TRUE_RATE_SLOW = 0.3 / 0.86;

// Per-state duration scales, in seconds. Deliberately unequal so that the
// state-mean normalization is exercised rather than being a no-op.
const STATE_SCALE = { 1: 2.0, 2: 0.5 };

const TRAIN_EVENTS_PER_STATE = 60;
const HOLDOUT_EVENTS_PER_STATE = 40;
const TRAIN_MOTORS = 10;
const HOLDOUT_MOTORS = 8;

function trueMixtureSurvival(y) {
  return (
    TRUE_WEIGHT_FAST * Math.exp(-TRUE_RATE_FAST * y) +
    (1 - TRUE_WEIGHT_FAST) * Math.exp(-TRUE_RATE_SLOW * y)
  );
}

// Deterministic inverse-CDF by bisection. No RNG anywhere in this file.
function trueMixtureQuantile(p) {
  const targetSurvival = 1 - p;
  let lower = 0;
  let upper = 1;
  while (trueMixtureSurvival(upper) > targetSurvival && upper < 1e6) upper *= 2;
  for (let i = 0; i < 200; i += 1) {
    const middle = (lower + upper) / 2;
    if (trueMixtureSurvival(middle) > targetSurvival) lower = middle;
    else upper = middle;
  }
  return (lower + upper) / 2;
}

// Direction is assigned by an unambiguous rule:
//   every event in stator state 1 is "on"
//   every event in stator state 2 is "off"
// in BOTH partitions. State-conditioning is therefore near-perfect and the
// pooled global predictor is exactly a coin flip, which pins every direction
// statistic to a closed form (see the constants below).
function directionForState(stateN) {
  return stateN === 1 ? "on" : "off";
}

function buildDataset() {
  const events = [];
  const motorIds = new Set();

  const addPartition = (partition, motorCount, eventsPerState) => {
    for (const stateN of [1, 2]) {
      for (let i = 0; i < eventsPerState; i += 1) {
        // Round-robin motor assignment: every motor carries events in BOTH
        // states, so any motor-cluster bootstrap resample stays balanced and
        // the reported interval is deterministic.
        const prefix = partition === "train" ? "T" : "H";
        const motorId = `${prefix}${String(i % motorCount).padStart(2, "0")}`;
        motorIds.add(motorId);
        const u = (i + 0.5) / eventsPerState; // deterministic quantile grid
        events.push({
          motorId,
          stateN,
          partition,
          rightCensored: false,
          durationS: trueMixtureQuantile(u) * STATE_SCALE[stateN],
          direction: directionForState(stateN),
        });
      }
    }
  };

  addPartition("train", TRAIN_MOTORS, TRAIN_EVENTS_PER_STATE);
  addPartition("holdout", HOLDOUT_MOTORS, HOLDOUT_EVENTS_PER_STATE);

  return {
    protocolId: PROTOCOL_ID,
    ingestion: { motorCount: motorIds.size, eventCount: events.length, exclusions: [] },
    events,
  };
}

const protocol = {
  protocolId: PROTOCOL_ID,
  scope: { primaryStates: [1, 2] },
  split: { method: "synthetic fixture: motors are pre-partitioned by identifier prefix" },
  uncertainty: { replicates: 200, seed: 12345 },
};

const dataset = buildDataset();
const report = runObservedExperiment(dataset, protocol, {});

// ---------------------------------------------------------------------------
// Hand-calculated direction constants
// ---------------------------------------------------------------------------
//
// The implementation uses a Jeffreys-prior Bernoulli estimate, (k + 0.5)/(n + 1).
//
//   state 1 train: 60 events, 60 of them "on"  -> p1 = 60.5 / 61
//   state 2 train: 60 events,  0 of them "on"  -> p2 =  0.5 / 61
//   pooled train:  120 events, 60 "on"         -> pG = 60.5 / 121 = 0.5 EXACTLY
//
// Holdout: 40 events in state 1 (all "on", outcome 1)
//          40 events in state 2 (all "off", outcome 0)
//
//   state-conditioned log loss
//     = 0.5 * (-ln(60.5/61))            [state 1, outcome 1, -ln(p1)]
//     + 0.5 * (-ln(1 - 0.5/61))         [state 2, outcome 0, -ln(1-p2)]
//     = -ln(60.5/61)                    because 1 - 0.5/61 = 60.5/61
//
//   global log loss = 0.5*(-ln 0.5) + 0.5*(-ln 0.5) = ln 2
//
//   state-conditioned Brier
//     = 0.5*(60.5/61 - 1)^2 + 0.5*(0.5/61 - 0)^2 = (0.5/61)^2
//   global Brier = (0.5)^2 = 0.25
//
// Under the M01 inversion (outcome 1 <-> 0) the state-conditioned log loss
// becomes -ln(0.5/61) = 4.80..., a factor of ~583 larger, and the improvement
// flips sign. The global log loss is INVARIANT under M01 because pG is exactly
// 0.5 -- which is precisely what makes the state-conditioned number a clean
// orientation probe.

const P_STATE_1 = 60.5 / 61;
const P_STATE_2 = 0.5 / 61;
const P_GLOBAL = 0.5;

const EXPECTED_STATE_LOG_LOSS = -Math.log(60.5 / 61);
const EXPECTED_GLOBAL_LOG_LOSS = Math.log(2);
const EXPECTED_STATE_BRIER = (0.5 / 61) ** 2;
const EXPECTED_GLOBAL_BRIER = 0.25;

// Value the state-conditioned log loss would take if the on/off outcome were
// inverted. Asserted against as an explicit negative control.
const INVERTED_STATE_LOG_LOSS = -Math.log(0.5 / 61);

const TOL = 1e-11;

function near(actual, expected, message) {
  assert.ok(
    Number.isFinite(actual) && Math.abs(actual - expected) <= TOL,
    `${message}\n  expected (hand-calculated): ${expected}\n  actual   (from pipeline):   ${actual}`,
  );
}

// ---------------------------------------------------------------------------
// 1. The fixture must actually reach the code paths under test.
// ---------------------------------------------------------------------------

test("fixture guard: both synthetic stator states are eligible and fully scored", () => {
  assert.deepEqual(
    report.cohort.eligibleStates,
    [1, 2],
    "Fixture guard failed: the synthetic states did not clear the eligibility rule, so the " +
      "orientation assertions below would be vacuous.",
  );
  assert.equal(
    report.cohort.holdoutEvents,
    2 * HOLDOUT_EVENTS_PER_STATE,
    "Fixture guard failed: not every synthetic holdout event was scored, so the hand-calculated " +
      "direction constants no longer apply.",
  );
  assert.equal(report.cohort.holdoutMotors, HOLDOUT_MOTORS);
  assert.equal(report.cohort.trainEvents, 2 * TRAIN_EVENTS_PER_STATE);
});

// ---------------------------------------------------------------------------
// 2. Direction semantics: "on" must mean outcome 1.
// ---------------------------------------------------------------------------

test('direction semantics: "on" is the positive outcome in the training-fitted probabilities', () => {
  const fitted = report.fittedOnTrainingOnly.direction;

  near(
    fitted.onProbabilityByState["1"],
    P_STATE_1,
    'DIRECTION ORIENTATION ERROR: onProbabilityByState[1] is not the probability of "on".\n' +
      "  In this fixture ALL 60 training events in stator state 1 have direction \"on\", so the\n" +
      "  Jeffreys estimate of P(on | N=1) must be 60.5/61 ~= 0.9918. A value near 0.5/61 ~= 0.0082\n" +
      "  means the on/off labels have been swapped: the field named onProbability is reporting\n" +
      '  P(off) instead.',
  );

  near(
    fitted.onProbabilityByState["2"],
    P_STATE_2,
    'DIRECTION ORIENTATION ERROR: onProbabilityByState[2] is not the probability of "on".\n' +
      '  ALL 60 training events in stator state 2 have direction "off", so P(on | N=2) must be\n' +
      "  0.5/61 ~= 0.0082. A value near 0.9918 means the on/off labels have been swapped.",
  );

  near(
    fitted.globalOnProbability,
    P_GLOBAL,
    "DIRECTION ORIENTATION ERROR: the pooled training P(on) is not 0.5.\n" +
      '  The fixture contains exactly 60 "on" and 60 "off" training events, so the Jeffreys\n' +
      "  pooled estimate is 60.5/121 = 0.5 exactly.",
  );
});

test('direction semantics: held-out outcome 1 is "on" (hand-calculated log loss and Brier score)', () => {
  const direction = report.heldoutResults.direction;

  // The load-bearing assertion for M01.
  near(
    direction.stateConditionedLogLoss,
    EXPECTED_STATE_LOG_LOSS,
    "DIRECTION ORIENTATION ERROR: the held-out on/off outcome is inverted.\n" +
      '  Every held-out event in state 1 is "on" and every held-out event in state 2 is "off",\n' +
      "  and the training-fitted probabilities match those labels almost exactly. The\n" +
      `  state-conditioned log loss must therefore be -ln(60.5/61) = ${EXPECTED_STATE_LOG_LOSS}.\n` +
      `  If the outcome indicator has been flipped ("on" scored as 0), this value becomes\n` +
      `  -ln(0.5/61) = ${INVERTED_STATE_LOG_LOSS}, about 583x larger.\n` +
      "  Check the outcome mapping in directionMetrics(): event.direction === \"on\" must map to 1.",
  );

  assert.ok(
    Math.abs(direction.stateConditionedLogLoss - INVERTED_STATE_LOG_LOSS) > 1,
    "DIRECTION ORIENTATION ERROR (negative control): the state-conditioned held-out log loss " +
      `equals the value expected under an INVERTED on/off outcome (${INVERTED_STATE_LOG_LOSS}). ` +
      'The direction predictor is being scored against the complement of the observed label.',
  );

  near(
    direction.globalLogLoss,
    EXPECTED_GLOBAL_LOG_LOSS,
    "DIRECTION BASELINE ERROR: the pooled-baseline held-out log loss is not ln 2.\n" +
      "  The pooled training probability is exactly 0.5, so scoring any balanced held-out set\n" +
      "  against it must give exactly ln 2 = 0.6931471805599453 nats per event.",
  );

  near(
    direction.stateConditionedBrier,
    EXPECTED_STATE_BRIER,
    "DIRECTION ORIENTATION ERROR: the state-conditioned held-out Brier score is inconsistent " +
      'with "on" being the positive outcome.\n' +
      `  Hand-calculated value is (0.5/61)^2 = ${EXPECTED_STATE_BRIER}. Under an inverted outcome ` +
      `it becomes (60.5/61)^2 ~= ${(60.5 / 61) ** 2}.`,
  );

  near(
    direction.globalBrier,
    EXPECTED_GLOBAL_BRIER,
    "DIRECTION BASELINE ERROR: the pooled-baseline held-out Brier score is not 0.25, which is " +
      "the only value a probability of exactly 0.5 can produce.",
  );
});

test('direction semantics: stateSummary.onFraction counts "on", not "off"', () => {
  const rows = Object.fromEntries(report.heldoutResults.stateSummary.map((row) => [row.stateN, row]));

  near(
    rows[1].onFraction,
    1,
    'DIRECTION ORIENTATION ERROR: stateSummary onFraction for state 1 is not 1.\n' +
      '  Every held-out event in state 1 has direction "on", so the fraction of "on" events is 1. ' +
      'A value of 0 means onFraction is counting "off" events.',
  );
  near(
    rows[2].onFraction,
    0,
    'DIRECTION ORIENTATION ERROR: stateSummary onFraction for state 2 is not 0.\n' +
      '  Every held-out event in state 2 has direction "off", so the fraction of "on" events is 0. ' +
      'A value of 1 means onFraction is counting "off" events.',
  );
});

// ---------------------------------------------------------------------------
// 3. Anchoring identity: state-conditioning was CONSTRUCTED to beat the pooled
//    baseline. The reported improvement must be positive.
// ---------------------------------------------------------------------------

test("anchoring identity: state-conditioned direction predictor was constructed to beat the pooled baseline", () => {
  const direction = report.heldoutResults.direction;

  assert.ok(
    direction.logLossImprovement > 0,
    "ADVANTAGE HAS THE WRONG SIGN: the state-conditioned direction predictor was constructed " +
      "to beat the pooled global predictor, and the reported logLossImprovement is not positive.\n" +
      "  In this fixture state N determines direction with certainty, while the pooled predictor " +
      "is exactly a coin flip. The state-conditioned predictor MUST win.\n" +
      `  expected: > 0 (about ${EXPECTED_GLOBAL_LOG_LOSS - EXPECTED_STATE_LOG_LOSS})\n` +
      `  actual:   ${direction.logLossImprovement}\n` +
      "  Either logLossImprovement is defined as (state - global) instead of (global - state), " +
      "or the on/off outcome indicator is inverted.",
  );

  near(
    direction.logLossImprovement,
    EXPECTED_GLOBAL_LOG_LOSS - EXPECTED_STATE_LOG_LOSS,
    "DIRECTION ORIENTATION ERROR: logLossImprovement does not equal " +
      "(globalLogLoss - stateConditionedLogLoss) as hand-calculated for this fixture. " +
      "A lower log loss must read as a POSITIVE improvement.",
  );

  assert.ok(
    direction.logLossImprovementInterval95.lower > 0,
    "ADVANTAGE HAS THE WRONG SIGN: the motor-cluster bootstrap interval for the direction " +
      "improvement does not lie above zero, although state-conditioning was constructed to be " +
      "perfect on every motor in this fixture.\n" +
      `  interval: [${direction.logLossImprovementInterval95.lower}, ${direction.logLossImprovementInterval95.upper}]`,
  );

  assert.ok(
    report.heldoutResults.direction.stateConditionedBrier < report.heldoutResults.direction.globalBrier,
    "ADVANTAGE HAS THE WRONG SIGN: the state-conditioned Brier score is not lower than the " +
      "pooled-baseline Brier score, although state-conditioning was constructed to be perfect.",
  );
});

// ---------------------------------------------------------------------------
// 4. Paired model-comparison sign convention.
//
//    The durations were generated from the M3_UNI_TWO_TIMESCALE family itself.
//    M0 (exponential), M1 (Weibull) and M2 (lognormal) are mis-specified by
//    construction. "pairedMixtureAdvantage" must therefore be POSITIVE for all
//    three comparisons: the name says mixture ADVANTAGE, so the orientation is
//    (mixture - baseline).
// ---------------------------------------------------------------------------

const BASELINES = ["exponential", "weibull", "lognormal"];
const KEY_FOR = {
  exponential: "mixtureVsExponential",
  weibull: "mixtureVsWeibull",
  lognormal: "mixtureVsLognormal",
};
const MODEL_ID = {
  exponential: "M0_MEMORYLESS",
  weibull: "M1_WEIBULL",
  lognormal: "M2_LOGNORMAL",
  mixture: "M3_UNI_TWO_TIMESCALE",
};

test("anchoring identity: the generating model outscores every mis-specified baseline", () => {
  const scores = report.heldoutResults.meanLogScoreNatsPerEvent;
  for (const baseline of BASELINES) {
    assert.ok(
      scores.mixture > scores[baseline],
      "ANCHORING IDENTITY VIOLATED: the model that generated the data does not have the highest " +
        "mean held-out log score.\n" +
        `  ${MODEL_ID.mixture} (mixture) was the generating distribution for this fixture; ` +
        `${MODEL_ID[baseline]} (${baseline}) is mis-specified by construction.\n` +
        `  mean log score mixture:  ${scores.mixture}\n` +
        `  mean log score ${baseline}: ${scores[baseline]}\n` +
        "  A higher log density must read as a HIGHER score. If the sign of the log score has " +
        "been flipped, better-fitting models will appear worse.",
    );
  }
});

test("paired advantage sign convention: mixture was constructed to beat every baseline", () => {
  const paired = report.heldoutResults.pairedMixtureAdvantageNatsPerEvent;
  for (const baseline of BASELINES) {
    const key = KEY_FOR[baseline];
    assert.ok(
      Number.isFinite(paired[key]),
      `pairedMixtureAdvantageNatsPerEvent.${key} is missing or non-finite.`,
    );
    assert.ok(
      paired[key] > 0,
      `ADVANTAGE HAS THE WRONG SIGN: ${MODEL_ID.mixture} (mixture) was constructed to beat ` +
        `${MODEL_ID[baseline]} (${baseline}), but pairedMixtureAdvantageNatsPerEvent.${key} is ` +
        `${paired[key]}, which is not positive.\n` +
        "  The held-out durations in this fixture were drawn from the two-timescale mixture " +
        "itself, so the mixture is the correctly specified model and the baseline is not.\n" +
        `  A "mixture advantage" must be oriented (mixture - ${baseline}). A negated value of ` +
        "the right magnitude means the subtraction operands have been transposed.",
    );
  }
});

test("paired advantage sign convention: bootstrap intervals agree in sign with the point estimate", () => {
  const paired = report.heldoutResults.pairedMixtureAdvantageNatsPerEvent;
  const intervals = report.heldoutResults.pairedMixtureAdvantageInterval95;
  for (const baseline of BASELINES) {
    const key = KEY_FOR[baseline];
    assert.ok(
      intervals[key].lower > 0,
      `ADVANTAGE HAS THE WRONG SIGN: ${MODEL_ID.mixture} (mixture) was constructed to beat ` +
        `${MODEL_ID[baseline]} (${baseline}), but the 95% motor-cluster bootstrap interval for ` +
        `${key} is [${intervals[key].lower}, ${intervals[key].upper}], which does not lie above zero.`,
    );
    assert.ok(
      intervals[key].lower <= paired[key] && paired[key] <= intervals[key].upper,
      `ORIENTATION MISMATCH: the point estimate for ${key} (${paired[key]}) lies outside its own ` +
        `bootstrap interval [${intervals[key].lower}, ${intervals[key].upper}]. The point estimate ` +
        "and the resampled estimate are not oriented the same way.",
    );
  }
});

// ---------------------------------------------------------------------------
// 5. Independent recomputation of the paired advantages.
//
//    The log densities below are written from the textbook definitions in this
//    file. They share no code with lib/observed-experiment.js: only the FITTED
//    PARAMETERS are taken from the report (parameters, not scores -- the
//    corruption under test is in the scoring orientation, not in the fit).
//    The state means are recomputed here from the training events directly.
//
//    Under M05 this assertion fails with a value of exactly the right magnitude
//    and the wrong sign, which is the clearest possible signature.
// ---------------------------------------------------------------------------

const SQRT_TWO_PI = Math.sqrt(2 * Math.PI);
const arithmeticMean = (values) => values.reduce((a, b) => a + b, 0) / values.length;

function independentLogDensity(name, y, models) {
  if (name === "exponential") return -y;
  if (name === "weibull") {
    const { shape, scale } = models.weibull;
    const ratio = y / scale;
    return Math.log(shape / scale) + (shape - 1) * Math.log(ratio) - ratio ** shape;
  }
  if (name === "lognormal") {
    const { sigma, mu } = models.lognormal;
    const z = (Math.log(y) - mu) / sigma;
    return -Math.log(y * sigma * SQRT_TWO_PI) - 0.5 * z * z;
  }
  if (name === "mixture") {
    const { weightFast, rateFast, rateSlow } = models.mixture;
    return Math.log(
      weightFast * rateFast * Math.exp(-rateFast * y) +
        (1 - weightFast) * rateSlow * Math.exp(-rateSlow * y),
    );
  }
  throw new Error(`independentLogDensity: unknown model ${name}`);
}

test("independent recomputation: paired advantages match an oracle written from the density definitions", () => {
  const models = report.fittedOnTrainingOnly.normalizedDurationModels;

  // Recompute the per-state training mean durations here, from the fixture.
  const stateMeans = {};
  for (const stateN of [1, 2]) {
    const durations = dataset.events
      .filter((event) => event.partition === "train" && event.stateN === stateN)
      .map((event) => event.durationS);
    stateMeans[stateN] = arithmeticMean(durations);
  }

  const normalizedHoldout = dataset.events
    .filter((event) => event.partition === "holdout")
    .map((event) => event.durationS / stateMeans[event.stateN]);

  const paired = report.heldoutResults.pairedMixtureAdvantageNatsPerEvent;

  for (const baseline of BASELINES) {
    const key = KEY_FOR[baseline];
    // The -log(scale) Jacobian is identical for both models of a pair and
    // cancels exactly in the difference, so it is omitted here.
    const oracle = arithmeticMean(
      normalizedHoldout.map(
        (y) => independentLogDensity("mixture", y, models) - independentLogDensity(baseline, y, models),
      ),
    );
    assert.ok(
      Math.abs(paired[key] - oracle) <= 1e-9,
      `ADVANTAGE HAS THE WRONG ORIENTATION: ${key} disagrees with an independent recomputation ` +
        "from the log-density definitions.\n" +
        `  independent oracle (mixture - ${baseline}): ${oracle}\n` +
        `  reported ${key}:                            ${paired[key]}\n` +
        (Math.abs(paired[key] + oracle) <= 1e-9
          ? `  The reported value is the EXACT NEGATION of the oracle. ${MODEL_ID.mixture} (mixture) ` +
            `was constructed to beat ${MODEL_ID[baseline]} (${baseline}); the subtraction operands ` +
            "have been transposed to (baseline - mixture).\n"
          : "  The magnitudes also differ, so this is not a pure sign flip.\n"),
    );
  }
});

test("internal orientation identity: paired advantage equals the difference of the reported mean log scores", () => {
  // mean(a_i - b_i) == mean(a_i) - mean(b_i) is an exact algebraic identity.
  // meanLogScoreNatsPerEvent is aggregated by a different expression in the
  // implementation than pairedMixtureAdvantageNatsPerEvent, so transposing the
  // operands of one and not the other breaks this identity by exactly 2x.
  const scores = report.heldoutResults.meanLogScoreNatsPerEvent;
  const paired = report.heldoutResults.pairedMixtureAdvantageNatsPerEvent;
  for (const baseline of BASELINES) {
    const key = KEY_FOR[baseline];
    const expected = scores.mixture - scores[baseline];
    assert.ok(
      Math.abs(paired[key] - expected) <= 1e-9,
      `ADVANTAGE HAS THE WRONG SIGN: ${key} is not equal to ` +
        `meanLogScore.mixture - meanLogScore.${baseline}, which it must equal by linearity of the ` +
        "mean.\n" +
        `  meanLogScore.mixture - meanLogScore.${baseline}: ${expected}\n` +
        `  reported ${key}:                                 ${paired[key]}\n` +
        `  ${MODEL_ID.mixture} (mixture) was constructed to beat ${MODEL_ID[baseline]} ` +
        `(${baseline}); if the reported value is the negation, the paired difference is oriented ` +
        `(${baseline} - mixture).`,
    );
  }
});

// ---------------------------------------------------------------------------
// 6. Determinism. No clock, no network, no RNG outside the implementation's
//    own seeded bootstrap.
// ---------------------------------------------------------------------------

test("determinism: a second run of the same fixture reproduces every orientation-bearing value", () => {
  const again = runObservedExperiment(buildDataset(), protocol, {});
  assert.deepEqual(
    again.heldoutResults.direction,
    report.heldoutResults.direction,
    "The direction statistics are not reproducible across runs of the same fixture.",
  );
  assert.deepEqual(
    again.heldoutResults.pairedMixtureAdvantageNatsPerEvent,
    report.heldoutResults.pairedMixtureAdvantageNatsPerEvent,
    "The paired model-comparison statistics are not reproducible across runs of the same fixture.",
  );
});
