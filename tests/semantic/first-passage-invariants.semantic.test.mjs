// Semantic gate: first-passage probability, competing-risk hazard, and moments.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   properties D1P07_FIRST_PASSAGE_WEIGHT_NORMALIZATION,
//              D1P08_OFF_HAZARD_STATOR_MULTIPLICITY,
//              D1P09_EXPONENTIAL_SECOND_MOMENT.
//
// Coverage provenance, stated honestly: tests/science-gates.test.mjs ALREADY asserts
// the coefficient sum and the density/negative-survival-derivative identity. That file
// runs under npm test, which the Phase-C protocol explicitly excluded from per-mutation
// classification. For D1P07 and D1P08 this gate is therefore primarily SUITE MEMBERSHIP
// MIGRATION plus new order-sensitivity and per-component assertions. D1P09 is different:
// normalizedVariance has no reader anywhere in the JavaScript codebase outside its own
// definition, so its invariant is genuinely new coverage.
//
// Oracle independence: expectations are closed-form Bernoulli-convolution weights and
// textbook exponential moments written as literals, plus two numerical oracles that use
// DIFFERENT production functions from the ones under test -- a central difference of
// sourceSurvival to check sourceDensities, and Simpson quadrature of 2 t S(t) to check
// sourceMoments. No sha256, runId, snapshot or committed artifact is read.
//
// Target corruptions:
//   D1X07 shift branch mis-weighted     D1A07 retain branch corrupted
//   D1X08 stator multiplicity dropped   D1A08 component term dropped
//   D1X09 factor of two deleted         D1A09 factor inflated to three

import test from "node:test";
import assert from "node:assert/strict";

import {
  sourceCoefficients,
  sourceDensities,
  sourceMoments,
  sourceSurvival,
  sourceTerms,
} from "../../lib/source-first-passage.js";

// Literal parameters. Chosen so every expected value is hand-calculable and so the
// off-hazard multiplicity signal is large: sigmaMinus = 0.5 rather than the fitted
// 5.4e-4, which would put the corruption signal near central-difference noise.
const PARAMETERS = {
  kPlusByN: { 0: 0.25, 1: 0.2, 2: 0.2, 3: 0.2 },
  sigmaPlusPerSecond: 1.5,
  sigmaMinusPerSecond: 0.5,
  c1: 0.3,
  c2: 0.5,
  c3: 0.2,
};

// A pure single-exponential branch: stateN = 0 with codeN0Branch = false yields an
// empty coefficient list, hence exactly one term with totalRate = kPlusByN[0] = 0.25.
const SINGLE_EXPONENTIAL = {
  kPlusByN: { 0: 0.25 },
  sigmaPlusPerSecond: 0.5,
  sigmaMinusPerSecond: 0.1,
  c1: 0.3,
  c2: 0.5,
  c3: 0.2,
};

const EXACT_TOLERANCE = 1e-12;
const CONSERVATION_TOLERANCE = 1e-8;
const QUADRATURE_TOLERANCE = 1e-9;

// Hand-calculated Bernoulli convolutions for c1 = 0.3, c2 = 0.5, c3 = 0.2.
//   N=1: [1-c1, c1]                                = [0.7, 0.3]
//   N=2: convolve with (1-c2, c2)                  = [0.35, 0.5, 0.15]
//   N=3: convolve with (1-c3, c3)                  = [0.28, 0.47, 0.22, 0.03]
const EXPECTED_COEFFICIENTS = {
  1: [0.7, 0.3],
  2: [0.35, 0.5, 0.15],
  3: [0.28, 0.47, 0.22, 0.03],
};

function closeEnough(actual, expected, tolerance) {
  return actual.length === expected.length && actual.every((value, i) => Math.abs(value - expected[i]) < tolerance);
}

test("D1P07 first-passage mixture weights are a normalized bernoulli convolution", () => {
  for (const stateN of [1, 2, 3]) {
    const observed = sourceCoefficients(stateN, PARAMETERS.c1, PARAMETERS.c2, PARAMETERS.c3);
    const expected = EXPECTED_COEFFICIENTS[stateN];

    // The full VECTOR, not only its sum. A corruption that swaps the retain and shift
    // factors still sums to one but reverses component ordering; a sum-only assertion
    // would be vacuous against it.
    assert.ok(
      closeEnough(observed, expected, EXACT_TOLERANCE),
      `The first-passage coefficient vector at N = ${stateN} is not the declared Bernoulli convolution. ` +
        `Hand-calculated mixture weights ${JSON.stringify(expected)}, observed ${JSON.stringify(observed)}. ` +
        "The component weights are a convolution of independent Bernoulli(c_i) choices; both their VALUES and " +
        "their ORDER carry meaning.",
    );

    const sum = observed.reduce((total, value) => total + value, 0);
    assert.ok(
      Math.abs(sum - 1) < EXACT_TOLERANCE,
      `The first-passage coefficients at N = ${stateN} are not normalized: the mixture weight sum is ${sum}, ` +
        "not 1. The D-L-T mixture is then not a probability distribution and every integrated event probability " +
        "derived from it is false.",
    );
    assert.ok(
      observed.every((value) => value >= 0),
      `A first-passage coefficient at N = ${stateN} is negative: ${JSON.stringify(observed)}. ` +
        "Mixture weights are probabilities.",
    );

    const survivalAtZero = sourceSurvival(0, stateN, PARAMETERS);
    assert.ok(
      Math.abs(survivalAtZero - 1) < EXACT_TOLERANCE,
      `Survival at zero for N = ${stateN} is ${survivalAtZero}, not 1. S(0) equals the coefficient sum, so a ` +
        "non-unit value proves the first-passage mixture weights are not normalized.",
    );
  }
});

test("D1P08 competing-risk off hazard carries n-fold stator detachment multiplicity", () => {
  // With N occupied stators there are N independent baseline detachment opportunities.
  // deltaSigma = sigmaPlus - sigmaMinus = 1.0, so at N = 2:
  //   offRate   = 2 * 0.5 + component * 1.0 = [1, 2, 3]
  //   totalRate = kPlus + offRate           = [1.2, 2.2, 3.2]
  const terms = sourceTerms(2, PARAMETERS);
  const observedOffRates = terms.map((term) => term.offRate);
  const observedTotalRates = terms.map((term) => term.totalRate);

  assert.ok(
    closeEnough(observedOffRates, [1, 2, 3], EXACT_TOLERANCE),
    "The competing-risk off hazard does not carry the declared N-fold stator detachment multiplicity. " +
      `At N = 2 with sigmaMinus = 0.5 the hand-calculated off rates are [1, 2, 3], observed ` +
      `${JSON.stringify(observedOffRates)}. Omitting the stator multiplicity understates the off-transition hazard ` +
      "by (N-1) * sigmaMinus; dropping the component term makes the hazard constant across mixture components.",
  );
  assert.ok(
    closeEnough(observedTotalRates, [1.2, 2.2, 3.2], EXACT_TOLERANCE),
    `The total rate at N = 2 is not the hand-calculated [1.2, 2.2, 3.2], observed ${JSON.stringify(observedTotalRates)}.`,
  );

  // Structurally independent oracle: competing-risk conservation. The total event
  // density must equal the negative survival derivative. This must be asserted at
  // N >= 2, because the multiplicity residual is exactly (N-1) * sigmaMinus * S(t),
  // which vanishes identically at N = 1 and would make an N = 1 fixture vacuous.
  for (const stateN of [2, 3]) {
    const time = 1;
    const step = 1e-5;
    const totalDensity = sourceDensities(time, stateN, PARAMETERS).total;
    const survivalDerivative =
      (sourceSurvival(time + step, stateN, PARAMETERS) - sourceSurvival(time - step, stateN, PARAMETERS)) / (2 * step);
    const residual = Math.abs(totalDensity + survivalDerivative);

    assert.ok(
      residual < CONSERVATION_TOLERANCE,
      `Competing-risk conservation fails at N = ${stateN}: the total event density does not equal the negative ` +
        `survival derivative. Residual ${residual}. The on and off densities must together account for all ` +
        "probability leaving the state, so an off hazard missing its stator multiplicity leaves the density " +
        "inconsistent with the declared survival rate.",
    );
  }
});

test("D1P09 exponential-mixture second moment retains its factor of two", () => {
  // A single exponential has E[T] = 1/rate, E[T^2] = 2/rate^2 and therefore a squared
  // coefficient of variation of exactly 1. With rate = 0.25 the mean is 4.
  const moments = sourceMoments(0, SINGLE_EXPONENTIAL);

  assert.ok(
    Math.abs(moments.meanDwellSeconds - 4) < EXACT_TOLERANCE,
    `Fixture precondition failed: the single-exponential mean dwell must be 1/0.25 = 4, observed ` +
      `${moments.meanDwellSeconds}.`,
  );
  assert.ok(
    Math.abs(moments.normalizedVariance - 1) < EXACT_TOLERANCE,
    "The exponential-mixture second moment has lost its factor of two. " +
      `A memoryless exponential has normalized variance exactly 1, observed ${moments.normalizedVariance}. ` +
      "Dropping the factor of two reports the simplest memoryless branch as though it had zero normalized " +
      "first-passage variance; inflating it overstates dispersion.",
  );

  // Structurally independent oracle on a multi-component state:
  //   E[T^2] = integral from 0 to infinity of 2 t S(t) dt
  // computed by Simpson quadrature of sourceSurvival, a DIFFERENT production function
  // from sourceMoments under test.
  const multi = sourceMoments(2, PARAMETERS);
  const analyticSecondMoment = (multi.normalizedVariance + 1) * multi.meanDwellSeconds ** 2;

  const upper = 400;
  const steps = 200000;
  const width = upper / steps;
  let sum = 0;
  for (let i = 0; i <= steps; i += 1) {
    const t = i * width;
    const weight = i === 0 || i === steps ? 1 : i % 2 === 1 ? 4 : 2;
    sum += weight * 2 * t * sourceSurvival(t, 2, PARAMETERS);
  }
  const quadratureSecondMoment = (sum * width) / 3;
  const relativeError = Math.abs(analyticSecondMoment / quadratureSecondMoment - 1);

  assert.ok(
    relativeError < QUADRATURE_TOLERANCE,
    "The analytic first-passage second moment disagrees with independent quadrature of 2 t S(t). " +
      `Analytic E[T^2] ${analyticSecondMoment}, quadrature ${quadratureSecondMoment}, relative error ` +
      `${relativeError}. The exponential-mixture second moment must equal 2 * sum_i w_i / R_i^2; a missing or ` +
      "altered factor of two changes the normalized variance by a factor of two.",
  );
});
