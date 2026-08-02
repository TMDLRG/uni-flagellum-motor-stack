// Semantic gate: what the slow-state posterior is conditioned on.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   property D1P02_SURVIVAL_CONDITIONED_POSTERIOR.
//
// posteriorSlowGivenSurvival(t) is the posterior probability of the SLOW latent
// component given the observation T > t. It must weight the components by
// SURVIVOR MASS
//
//     w_i * exp(-lambda_i * t)
//
// and NOT by the instantaneous EVENT DENSITY
//
//     w_i * lambda_i * exp(-lambda_i * t)
//
// These are different observations. "The dwell has lasted at least t" and "the
// dwell ends at instant t" carry different information about which latent
// timescale generated it, and they yield different latent-state probabilities
// whenever the component rates differ.
//
// Why the pre-existing check did not catch this: the H3 claim asserts only that
// the posterior curve is MONOTONE. Both the correct survivor form and the
// event-density form are monotone increasing for rateSlow < rateFast, so
// monotonicity is satisfied by the corruption and cannot discriminate.
//
// Oracle independence: the expectations are the declared survivor ratio recomputed
// inline from Math.exp and literal mixture constants. posteriorSlowGivenSurvival is
// never used to build its own expectation. No sha256, runId or artifact is read.
//
// Target corruptions:
//   D1X02 both masses rate-weighted (Phase-C survivor CXM02)
//   D1A02 slow mass evaluated at the FAST rate, which is invisible at t = 0

import test from "node:test";
import assert from "node:assert/strict";

import { posteriorSlowGivenSurvival } from "../../lib/observed-experiment.js";

const MIXTURE = { weightFast: 0.25, rateFast: 4, rateSlow: 0.5 };
const TOLERANCE = 1e-12;

/** Independent reimplementation of the DECLARED survivor-conditioned posterior. */
function survivorConditionedPosterior(normalizedTime) {
  const slowSurvivorMass = (1 - MIXTURE.weightFast) * Math.exp(-MIXTURE.rateSlow * normalizedTime);
  const fastSurvivorMass = MIXTURE.weightFast * Math.exp(-MIXTURE.rateFast * normalizedTime);
  return slowSurvivorMass / (slowSurvivorMass + fastSurvivorMass);
}

/** The competing hypothesis: conditioning on an event at instant t instead of on survival. */
function eventDensityConditionedPosterior(normalizedTime) {
  const slow = (1 - MIXTURE.weightFast) * MIXTURE.rateSlow * Math.exp(-MIXTURE.rateSlow * normalizedTime);
  const fast = MIXTURE.weightFast * MIXTURE.rateFast * Math.exp(-MIXTURE.rateFast * normalizedTime);
  return slow / (slow + fast);
}

test("D1P02 slow-state posterior conditions on survival not on event density", () => {
  // At t = 0 survival is certain, so a survivor-conditioned posterior must return the
  // PRIOR slow weight exactly. 1 - weightFast = 0.75.
  const atZero = posteriorSlowGivenSurvival(0, MIXTURE);

  assert.ok(
    Math.abs(atZero - 0.75) < TOLERANCE,
    "The slow-state posterior at time zero does not equal the prior slow weight. " +
      `Conditioning on survival gives exactly 1 - weightFast = 0.75, observed ${atZero}. ` +
      "A posterior conditioned on survivor mass must reduce to the prior at t = 0, because surviving " +
      "zero time carries no information.",
  );

  const eventDensityValue = eventDensityConditionedPosterior(0);
  assert.ok(
    Math.abs(atZero - eventDensityValue) > 0.1,
    "The slow-state posterior at time zero equals the EVENT DENSITY conditioned value " +
      `${eventDensityValue}, not the survival conditioned value 0.75. The posterior is being computed for the ` +
      "observation 'a transition occurs at this instant' while the reported claim is about 'surviving longer " +
      "without a transition'. Those are different observations.",
  );
});

test("D1P02 slow-state posterior equals the independently recomputed survivor mass ratio", () => {
  // This is the invariant that catches a corruption preserving the survivor FORM but
  // corrupting the rate identity. Such a corruption is exactly invisible at t = 0,
  // where every exponential equals 1, and is detectable only at t > 0.
  for (const normalizedTime of [0.25, 0.5, 1, 2, 4]) {
    const observed = posteriorSlowGivenSurvival(normalizedTime, MIXTURE);
    const expected = survivorConditionedPosterior(normalizedTime);
    assert.ok(
      Math.abs(observed - expected) < TOLERANCE,
      `The slow-state posterior at normalized time ${normalizedTime} does not equal the declared survivor mass ` +
        `ratio. Independently recomputed survival conditioned value ${expected}, observed ${observed}. ` +
        "The posterior must weight each latent component by its own survivor mass w_i exp(-lambda_i t), using " +
        "the slow rate for the slow component and the fast rate for the fast component.",
    );
  }
});

test("D1P02 slow-state posterior increases with survival and saturates toward the slow component", () => {
  // Direction and limit, independent of the exact algebra. Surviving longer without a
  // transition must move posterior mass toward the SLOWER timescale.
  const early = posteriorSlowGivenSurvival(0, MIXTURE);
  const late = posteriorSlowGivenSurvival(6, MIXTURE);
  assert.ok(
    late > early,
    "Surviving longer without a transition did not increase posterior mass on the slower latent timescale. " +
      `Posterior at t = 0 is ${early} and at t = 6 is ${late}. Survival conditioning must favour the slow component.`,
  );
  assert.ok(
    late > 0.999,
    `The slow-state posterior after long survival is ${late}, which has not saturated toward the slow component. ` +
      "With rateSlow = 0.5 and rateFast = 4 the fast survivor mass is negligible at t = 6.",
  );
});
