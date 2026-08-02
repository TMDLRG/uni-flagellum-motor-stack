import assert from "node:assert/strict";
import test from "node:test";
import {
  bayesUpdate,
  createAgent,
  createControls,
  createWorld,
  hellinger,
  instrumentObservation,
  observeWorld,
  stepAgent,
  stepSyntheticSystem,
} from "../lib/uni-motor.js";
import { createCadManifest, openScadFromManifest } from "../lib/cad.js";

const close = (a, b, tolerance = 1e-10) => Math.abs(a - b) <= tolerance;

test("categorical posterior normalizes and free-energy identity is exact", () => {
  const update = bayesUpdate([0.2, 0.3, 0.5], 0.06);
  assert.ok(close(update.posterior.reduce((a, b) => a + b, 0), 1));
  assert.ok(update.posterior[2] > update.posterior[0]);
  assert.ok(close(update.vfe, update.surprise + update.kl));
  assert.ok(close(update.kl, 0));
});

test("log posterior odds equal log prior odds plus log likelihood ratio", () => {
  const prior = [0.25, 0.25, 0.5];
  const update = bayesUpdate(prior, 0.04);
  const lhs = Math.log(update.posterior[2] / update.posterior[0]);
  const rhs = Math.log(prior[2] / prior[0]) + Math.log(update.likelihood[2] / update.likelihood[0]);
  assert.ok(close(lhs, rhs));
});

test("Markov observation excludes hidden world truth", () => {
  const world = createWorld({ trueGradient: "rising", stators: 7.2 });
  const observation = observeWorld(world, createControls(), 1000);
  assert.equal("trueGradient" in observation, false);
  assert.equal("stators" in observation, false);
  assert.equal(observation.source, "SYNTHETIC_WORLD");
});

test("same initial state and controls replay deterministically", () => {
  const controls = createControls({ sensoryNoise: 0.02 });
  const make = () => ({ world: createWorld(), agent: createAgent(), observation: null, action: { policy: "RUN" } });
  const a = stepSyntheticSystem(make(), controls, 0.05, 1000);
  const b = stepSyntheticSystem(make(), controls, 0.05, 1000);
  assert.deepEqual(a, b);
});

test("policy posterior normalizes after a real observation record", () => {
  const observation = instrumentObservation({ t_ms: 10, ligand_uM: 1.1, motor_rpm: 6100, rotation: "CCW", load_pNnm: 700, pmf_mV: 150 }, 1000);
  const agent = stepAgent(createAgent(), observation, 0.08);
  assert.ok(close(agent.policyPosterior[0] + agent.policyPosterior[1], 1));
  assert.ok(["RUN", "TUMBLE"].includes(agent.selectedPolicy));
});

test("physical encoder angles drive the exact log-odds calculation", () => {
  const observation = instrumentObservation({
    t_ms: 10,
    ligand_uM: 1.1,
    motor_rpm: 6100,
    rotation: "CCW",
    load_pNnm: 700,
    pmf_mV: 150,
    prior_angle_deg: 38,
    evidence_angle_deg: -19,
  }, 1000);
  const agent = stepAgent(createAgent(), observation, 0.08);
  assert.ok(close(agent.priorLogOdds, 1));
  assert.ok(close(agent.evidenceLogOdds, -0.5));
  assert.ok(close(agent.posteriorLogOdds, 0.5));
});

test("instrument validation rejects incomplete or non-finite frames", () => {
  assert.throws(() => instrumentObservation({ ligand_uM: 1 }, 0), /requires finite/);
  assert.throws(() => instrumentObservation({ ligand_uM: 1, motor_rpm: 1, load_pNnm: 1, pmf_mV: 1, rotation: "SIDEWAYS" }, 0), /CW or CCW/);
});

test("Hellinger distance is symmetric and bounded", () => {
  const a = hellinger([0.2, 0.3, 0.5], [0.7, 0.2, 0.1]);
  const b = hellinger([0.7, 0.2, 0.1], [0.2, 0.3, 0.5]);
  assert.ok(close(a, b));
  assert.ok(a >= 0 && a <= 1);
});

test("CAD export names the model, boundary and explicit non-claim", () => {
  const manifest = createCadManifest({ moduleMm: 2, clearanceMm: 0.28 });
  assert.equal(manifest.parts.length, 8);
  assert.match(manifest.explicitNonClaim, /not a scale model/i);
  assert.equal(manifest.mathematicalTransmission.identity, "theta_posterior = theta_prior + theta_likelihood");
  const scad = openScadFromManifest(manifest);
  assert.match(scad, /module spur_gear/);
  assert.match(scad, /module markov_boundary/);
  assert.match(scad, /NOT A BACTERIAL MOTOR CAD MODEL/);
});
