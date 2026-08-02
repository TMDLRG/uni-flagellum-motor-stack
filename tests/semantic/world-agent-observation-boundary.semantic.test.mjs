// Semantic gate: the world/agent boundary and the physical validity of instrument input.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   properties D1P04_HIDDEN_WORLD_OBSERVATION_BOUNDARY,
//              D1P05_INSTRUMENT_STATOR_RANGE,
//              D1P06_LOAD_DEPENDENT_STATOR_RECRUITMENT.
//
// The repository claims a declared Markov boundary: the world owns physical state,
// the boundary carries a timestamped Observation and a bounded Action, and the agent
// owns only its generative model. If a latent world variable crosses that boundary,
// an observation record contains oracle truth that no physical instrument measures
// and the claimed world/agent separation is invalid.
//
// Oracle independence: expectations are a frozen literal key list, structural deep
// equality, literal integers, and the declared closed form 1 + 10 L/(L + 420)
// evaluated in this file. No production function is used to build an expectation.
// No sha256, runId, snapshot or committed artifact is read.
//
// Target corruptions:
//   D1X04 world.trueGradient copied into the observation
//   D1A04 world.methylation copied in under a DIFFERENT field name
//   D1X05 instrument stator clamp removed
//   D1A05 instrument stator clamp widened to 0..20
//   D1X06 stator target made constant
//   D1A06 stator target load response inverted

import test from "node:test";
import assert from "node:assert/strict";

import {
  createAgent,
  createControls,
  createWorld,
  instrumentObservation,
  observeWorld,
  stepAgent,
  stepWorld,
} from "../../lib/uni-motor.js";

// The nine fields a physical instrument can actually deliver. Frozen literal.
const DECLARED_OBSERVATION_KEYS = [
  "deviceTimeMs",
  "ligandUm",
  "loadPnNm",
  "motorSpeedRpm",
  "pmfMv",
  "receivedAtMs",
  "receptorActivity",
  "rotation",
  "source",
];

// Fields the world owns and the boundary must NOT carry.
const HIDDEN_WORLD_FIELDS_A = {
  trueGradient: "rising",
  methylation: 2.2,
  cheYpUm: 3.2,
  xUm: 1,
  yUm: 2,
  torquePnNm: 700,
  stators: 5,
  cwBias: 0.25,
  rotorAngleRad: 0.4,
  previousLigandUm: 0.9,
};
const HIDDEN_WORLD_FIELDS_B = {
  trueGradient: "falling",
  methylation: 7.9,
  cheYpUm: 9.9,
  xUm: -50,
  yUm: 33,
  torquePnNm: 111,
  stators: 1,
  cwBias: 0.99,
  rotorAngleRad: 3.3,
  previousLigandUm: 0.1,
};

const STATOR_TOLERANCE = 1e-9;

/** The declared mechanosensitive recruitment relation, written out here as the oracle. */
function declaredStatorTarget(loadPnNm) {
  return 1 + 10 * (loadPnNm / (loadPnNm + 420));
}

test("D1P04 observation excludes hidden world truth at the markov boundary", () => {
  const controls = createControls({});
  const world = createWorld(HIDDEN_WORLD_FIELDS_A);
  const observation = observeWorld(world, controls, 1000);
  const observedKeys = Object.keys(observation).sort();

  assert.deepEqual(
    observedKeys,
    DECLARED_OBSERVATION_KEYS,
    "The observation record does not carry exactly the declared instrument-measurable fields. " +
      `Declared boundary key set ${JSON.stringify(DECLARED_OBSERVATION_KEYS)}, observed ${JSON.stringify(observedKeys)}. ` +
      "Any extra key means hidden world state has crossed the markov boundary into an observation, which invalidates " +
      "the claimed world/agent separation.",
  );

  for (const forbidden of Object.keys(HIDDEN_WORLD_FIELDS_A)) {
    assert.ok(
      !(forbidden in observation),
      `The hidden world field '${forbidden}' is present in the observation record. A latent world variable has ` +
        "crossed the markov boundary; an observation may not contain oracle truth a physical instrument cannot measure.",
    );
  }
});

test("D1P04 observation is invariant to hidden world state under any field name", () => {
  // Value-level, name-independent leak detection. Two worlds differ ONLY in fields the
  // instrument cannot measure and agree on every observable field. Their observation
  // records must be indistinguishable. This detects a leak under a RENAMED field, which
  // a key-name allowlist alone would not catch.
  const controls = createControls({});
  const observationA = observeWorld(createWorld(HIDDEN_WORLD_FIELDS_A), controls, 1000);
  const observationB = observeWorld(createWorld(HIDDEN_WORLD_FIELDS_B), controls, 1000);

  assert.deepEqual(
    observationB,
    observationA,
    "Two worlds that differ ONLY in hidden state produced DIFFERENT observation records. " +
      "Some hidden world variable is leaking across the markov boundary, whatever the leaked field is named. " +
      `Observation A ${JSON.stringify(observationA)} versus observation B ${JSON.stringify(observationB)}.`,
  );
});

test("D1P04 the agent receives an observation and never the world object", () => {
  const controls = createControls({});
  const observation = observeWorld(createWorld(HIDDEN_WORLD_FIELDS_A), controls, 1000);
  const agent = stepAgent(createAgent({}), observation, 0.02);

  assert.equal(
    stepAgent.length,
    3,
    "stepAgent no longer takes exactly (agent, observation, dtS). The agent must not be handed the world object; " +
      "a changed arity suggests hidden world state is reaching the agent directly.",
  );
  const retainedKeys = Object.keys(agent.lastObservation ?? {}).sort();
  assert.deepEqual(
    retainedKeys,
    DECLARED_OBSERVATION_KEYS,
    "The observation retained by the agent contains keys outside the declared boundary set. " +
      `Observed ${JSON.stringify(retainedKeys)}. The agent may retain only what crossed the markov boundary.`,
  );
});

test("D1P05 live instrument stator occupancy is bounded to the physical zero to eleven range", () => {
  const frame = { ligand_uM: 1, motor_rpm: 6000, load_pNnm: 700, pmf_mV: 150, rotation: "CCW" };
  const statorsFor = (stators) => instrumentObservation({ ...frame, stators }, 0).stators;

  assert.equal(
    statorsFor(20),
    11,
    "An impossible instrument stator count of 20 was accepted instead of being clamped to the declared maximum 11. " +
      "A flagellar motor cannot host more than eleven stator units; an out-of-range instrument reading must not enter " +
      "model state as if it were a biologically valid measurement.",
  );
  assert.equal(
    statorsFor(-3),
    0,
    "A negative instrument stator count of -3 was accepted instead of being clamped to zero. " +
      "Negative stator occupancy is physically impossible.",
  );
  assert.equal(statorsFor(11), 11, "An in-range instrument stator count of 11 must pass through unchanged.");
  assert.equal(statorsFor(0), 0, "An in-range instrument stator count of 0 must pass through unchanged.");
  assert.equal(statorsFor(7), 7, "An in-range instrument stator count of 7 must pass through unchanged.");
  assert.equal(
    instrumentObservation({ ...frame }, 0).stators,
    null,
    "An absent instrument stator reading must be null, not fabricated.",
  );
  assert.equal(
    instrumentObservation({ ...frame, stators: "abc" }, 0).stators,
    null,
    "A non-finite instrument stator reading must be null, not coerced.",
  );

  // DECLARED LIMITATION — integrality is NOT_ESTABLISHED and is deliberately NOT gated.
  //
  // Production clamps but does not quantize, so instrument stator occupancy of 7.5 is
  // currently accepted. No repository document declares integral live occupancy, so
  // this gate asserts only the declared 0..11 bound.
  //
  // CORRECTION 4 (Codex review of fb9aa336). An earlier revision of this gate asserted
  // statorsFor(7.5) === 7.5, which PINNED fractional occupancy as REQUIRED behaviour.
  // That was wrong in both directions: it converted an unestablished sub-property into
  // an enforced contract, and it would have FAILED a future correct change that added
  // integrality enforcement — turning a genuine improvement into a red gate. The
  // assertion is withdrawn. Integrality stays NOT_ESTABLISHED in
  // audits/phase-d/d1-semantic-remediation-protocol.v1.json and is recorded, not gated.
  // Production remains unchanged; nothing here licenses either quantizing or not
  // quantizing live stator occupancy.
});

test("D1P06 mechanosensitive stator recruitment increases with load", () => {
  // Agent side: a single call yields the declared relation exactly.
  for (const loadPnNm of [0, 700, 3780]) {
    const observation = {
      ...observeWorld(createWorld({}), createControls({ loadPnNm }), 0),
      loadPnNm,
      pmfMv: 150,
    };
    const predicted = stepAgent(createAgent({}), observation, 0.02).predictedStators;
    const expected = declaredStatorTarget(loadPnNm);
    assert.ok(
      Math.abs(predicted - expected) < STATOR_TOLERANCE,
      `Predicted stator occupancy does not follow the declared load-dependent stator recruitment relation. ` +
        `At load ${loadPnNm} pN nm the declared target 1 + 10 L/(L + 420) is ${expected}, observed ${predicted}. ` +
        "Mechanosensitive recruitment must make occupancy an increasing function of external load.",
    );
  }

  // World side: integrate to steady state and compare with the declared target.
  const steadyStateStators = (loadPnNm) => {
    let world = createWorld({ stators: 5 });
    const controls = createControls({ loadPnNm });
    for (let step = 0; step < 3000; step += 1) world = stepWorld(world, { policy: "RUN" }, controls, 0.1);
    return world.stators;
  };

  const lowLoad = steadyStateStators(100);
  const highLoad = steadyStateStators(5000);

  assert.ok(
    Math.abs(lowLoad - declaredStatorTarget(100)) < STATOR_TOLERANCE,
    `Steady-state stator occupancy at low load does not reach the declared mechanosensitive recruitment target. ` +
      `Expected ${declaredStatorTarget(100)}, observed ${lowLoad}.`,
  );
  assert.ok(
    Math.abs(highLoad - declaredStatorTarget(5000)) < STATOR_TOLERANCE,
    `Steady-state stator occupancy at high load does not reach the declared mechanosensitive recruitment target. ` +
      `Expected ${declaredStatorTarget(5000)}, observed ${highLoad}.`,
  );
  assert.ok(
    highLoad - lowLoad > 5,
    "Steady-state stator occupancy did not increase with external load. " +
      `Occupancy at 100 pN nm is ${lowLoad} and at 5000 pN nm is ${highLoad}, a difference of ${highLoad - lowLoad}. ` +
      "A load-independent or inverted stator recruitment target erases the declared mechanosensitivity while the " +
      "model continues to be described as load-responsive.",
  );
});
