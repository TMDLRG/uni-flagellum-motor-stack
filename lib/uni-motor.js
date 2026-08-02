/**
 * UNI-FLAGELLUM transparent CPU reference kernel.
 *
 * The world process and the UNI agent are deliberately separate.  The world
 * owns physical state.  The agent receives only an Observation record and
 * returns an Action record.  Nothing in this file claims that the reduced
 * educational equations replace a molecular mechanism or wet-lab evidence.
 */

export const GRADIENT_STATES = ["falling", "flat", "rising"];
export const OUTCOME_STATES = ["lower", "same", "higher"];
export const POLICY_NAMES = ["RUN", "TUMBLE"];

const EPSILON = 1e-12;

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function normalize(values) {
  const safe = values.map((value) => Math.max(EPSILON, Number(value) || 0));
  const total = safe.reduce((sum, value) => sum + value, 0);
  return safe.map((value) => value / total);
}

export function softmax(logValues) {
  const peak = Math.max(...logValues);
  return normalize(logValues.map((value) => Math.exp(value - peak)));
}

export function entropy(probabilities) {
  return -normalize(probabilities).reduce(
    (sum, value) => sum + value * Math.log(Math.max(EPSILON, value)),
    0,
  );
}

export function klDivergence(q, p) {
  const qn = normalize(q);
  const pn = normalize(p);
  return qn.reduce(
    (sum, value, index) =>
      sum + value * Math.log(Math.max(EPSILON, value) / Math.max(EPSILON, pn[index])),
    0,
  );
}

export function hellinger(p, q) {
  const pn = normalize(p);
  const qn = normalize(q);
  return Math.sqrt(
    0.5 *
      pn.reduce(
        (sum, value, index) =>
          sum + (Math.sqrt(value) - Math.sqrt(qn[index])) ** 2,
        0,
      ),
  );
}

function gaussian(value, mean, sigma) {
  const z = (value - mean) / sigma;
  return Math.exp(-0.5 * z * z) / (sigma * Math.sqrt(2 * Math.PI));
}

export function createWorld(overrides = {}) {
  return {
    timeS: 0,
    xUm: 0,
    yUm: 0,
    headingRad: 0,
    ligandUm: 1.0,
    previousLigandUm: 1.0,
    receptorActivity: 0.34,
    methylation: 2.2,
    cheYpUm: 3.2,
    stators: 5.0,
    torquePnNm: 700,
    speedRpm: 6200,
    cwBias: 0.25,
    rotation: "CCW",
    rotorAngleRad: 0,
    trueGradient: "rising",
    ...overrides,
  };
}

export function createAgent(overrides = {}) {
  return {
    timeS: 0,
    posterior: [0.15, 0.35, 0.5],
    predictivePrior: [0.15, 0.35, 0.5],
    priorAtUpdate: [0.15, 0.35, 0.5],
    likelihood: [1 / 3, 1 / 3, 1 / 3],
    policyPosterior: [0.7, 0.3],
    efe: [0, 0],
    risk: [0, 0],
    ambiguity: [0, 0],
    informationGain: [0, 0],
    selectedPolicy: "RUN",
    predictedLigandUm: 1.0,
    predictedSpeedRpm: 6200,
    predictedCwBias: 0.25,
    predictedStators: 5.0,
    vfe: 0,
    surprise: 0,
    evidenceLogOdds: 0,
    posteriorLogOdds: 0,
    observationCount: 0,
    lastObservation: null,
    ...overrides,
  };
}

export function createControls(overrides = {}) {
  return {
    baseLigandUm: 1.0,
    gradientPerMm: 1.15,
    loadPnNm: 700,
    pmfMv: 150,
    sensoryNoise: 0.025,
    timeScale: 1,
    ...overrides,
  };
}

/** A deterministic, bounded signal used only to make the synthetic world noisy. */
function deterministicNoise(timeS, channel) {
  return Math.sin(timeS * (4.17 + channel * 0.31) + channel * 1.73);
}

/**
 * Reduced, evidence-linked world process.
 *
 * Receptor activity is an MWC-style phenomenological mapping; CheY-P, stator
 * exchange and torque-speed dynamics are deliberately coarse.  These are
 * visible model choices, not hidden biological facts.
 */
export function stepWorld(world, action, controls, dtS) {
  const dt = clamp(dtS * controls.timeScale, 0.001, 0.1);
  const next = { ...world, timeS: world.timeS + dt };

  const run = action?.policy !== "TUMBLE";
  if (run) {
    const speedUmS = clamp(world.speedRpm / 500, 2, 35);
    next.xUm += Math.cos(world.headingRad) * speedUmS * dt;
    next.yUm += Math.sin(world.headingRad) * speedUmS * dt;
  } else {
    next.headingRad = world.headingRad + 2.15 * dt + 0.6 * deterministicNoise(next.timeS, 1) * dt;
  }

  next.previousLigandUm = world.ligandUm;
  const spatialExponent = clamp((controls.gradientPerMm * next.xUm) / 1000, -4, 4);
  next.ligandUm = Math.max(0.001, controls.baseLigandUm * Math.exp(spatialExponent));

  // MWC-style receptor free-energy difference. Increasing attractant lowers
  // activity; methylation restores the operating point.
  const receptorTeams = 6;
  const kOffUm = 0.02;
  const kOnUm = 0.5;
  const epsilonM = 0.46;
  const ligandTerm = Math.log((1 + next.ligandUm / kOffUm) / (1 + next.ligandUm / kOnUm));
  const receptorFreeEnergy = receptorTeams * (1.0 - epsilonM * world.methylation + ligandTerm);
  const receptorActivity = 1 / (1 + Math.exp(clamp(receptorFreeEnergy, -20, 20)));
  next.receptorActivity = world.receptorActivity + (receptorActivity - world.receptorActivity) * dt / 0.12;
  next.methylation = clamp(
    world.methylation + (0.34 - next.receptorActivity) * 0.72 * dt,
    0,
    8,
  );

  const cheYTarget = 1.0 + 8.5 * next.receptorActivity;
  next.cheYpUm = world.cheYpUm + (cheYTarget - world.cheYpUm) * dt / 0.35;

  const loadFraction = controls.loadPnNm / (controls.loadPnNm + 420);
  const statorTarget = 1 + 10 * loadFraction;
  const remodelingTauS = statorTarget > world.stators ? 6.5 : 3.2;
  next.stators = clamp(
    world.stators + (statorTarget - world.stators) * dt / remodelingTauS,
    0,
    11,
  );

  const pmfFraction = clamp(controls.pmfMv / 150, 0.1, 1.5);
  const stallTorque = next.stators * 180 * pmfFraction;
  next.torquePnNm = Math.min(controls.loadPnNm, stallTorque);
  const zeroLoadRpm = 18000 * pmfFraction;
  next.speedRpm = Math.max(0, zeroLoadRpm * (1 - clamp(controls.loadPnNm / Math.max(1, stallTorque), 0, 0.995)));

  const kdUm = clamp(5.8 - 2.5 * (next.torquePnNm / 1800), 2.5, 6.2);
  const hill = 6;
  next.cwBias = next.cheYpUm ** hill / (kdUm ** hill + next.cheYpUm ** hill);
  const switchWave = 0.5 + 0.5 * Math.sin(next.timeS * (0.7 + next.cwBias * 3.2));
  next.rotation = switchWave < next.cwBias ? "CW" : "CCW";
  next.rotorAngleRad = world.rotorAngleRad + (next.rotation === "CW" ? 1 : -1) * (next.speedRpm / 60) * 2 * Math.PI * dt;
  next.trueGradient = controls.gradientPerMm < -0.08 ? "falling" : controls.gradientPerMm > 0.08 ? "rising" : "flat";
  return next;
}

/**
 * The Markov boundary. Hidden world state is not copied into this observation.
 */
export function observeWorld(world, controls, receivedAtMs) {
  const noise = controls.sensoryNoise * deterministicNoise(world.timeS, 3);
  const ligandObserved = Math.max(0.001, world.ligandUm * (1 + noise));
  return {
    source: "SYNTHETIC_WORLD",
    deviceTimeMs: Math.round(world.timeS * 1000),
    receivedAtMs,
    ligandUm: ligandObserved,
    receptorActivity: clamp(world.receptorActivity + noise * 0.1, 0, 1),
    motorSpeedRpm: Math.max(0, world.speedRpm * (1 + noise * 0.25)),
    rotation: world.rotation,
    loadPnNm: controls.loadPnNm,
    pmfMv: controls.pmfMv,
  };
}

/** Validate and normalize an external newline-delimited JSON instrument frame. */
export function instrumentObservation(frame, receivedAtMs) {
  const ligandUm = Number(frame.ligand_uM ?? frame.ligandUm);
  const motorSpeedRpm = Number(frame.motor_rpm ?? frame.motorSpeedRpm);
  const loadPnNm = Number(frame.load_pNnm ?? frame.loadPnNm);
  const pmfMv = Number(frame.pmf_mV ?? frame.pmfMv);
  if (![ligandUm, motorSpeedRpm, loadPnNm, pmfMv].every(Number.isFinite)) {
    throw new Error("Instrument frame requires finite ligand_uM, motor_rpm, load_pNnm, and pmf_mV.");
  }
  const rotation = String(frame.rotation ?? (Number(frame.cw) ? "CW" : "CCW")).toUpperCase();
  if (rotation !== "CW" && rotation !== "CCW") {
    throw new Error("Instrument rotation must be CW or CCW.");
  }
  return {
    source: "LIVE_SERIAL_INSTRUMENT",
    deviceTimeMs: Number(frame.t_ms ?? frame.deviceTimeMs ?? 0),
    receivedAtMs,
    ligandUm: Math.max(0.001, ligandUm),
    receptorActivity: Number.isFinite(Number(frame.receptor_activity))
      ? clamp(Number(frame.receptor_activity), 0, 1)
      : null,
    motorSpeedRpm: Math.max(0, motorSpeedRpm),
    rotation,
    loadPnNm: Math.max(0, loadPnNm),
    pmfMv: Math.max(0, pmfMv),
    cheYpUm: Number.isFinite(Number(frame.cheyp_uM)) ? Math.max(0, Number(frame.cheyp_uM)) : null,
    stators: Number.isFinite(Number(frame.stators)) ? clamp(Number(frame.stators), 0, 11) : null,
    priorAngleDeg: Number.isFinite(Number(frame.prior_angle_deg)) ? Number(frame.prior_angle_deg) : null,
    evidenceAngleDeg: Number.isFinite(Number(frame.evidence_angle_deg)) ? Number(frame.evidence_angle_deg) : null,
  };
}

function transitionPrior(posterior, policy) {
  // B matrices are column-stochastic. RUN preserves gradient evidence;
  // TUMBLE intentionally broadens directional belief.
  const bRun = [
    [0.82, 0.12, 0.06],
    [0.14, 0.76, 0.14],
    [0.04, 0.12, 0.80],
  ];
  const bTumble = [
    [0.42, 0.30, 0.28],
    [0.31, 0.40, 0.31],
    [0.27, 0.30, 0.41],
  ];
  const matrix = policy === "TUMBLE" ? bTumble : bRun;
  return normalize(matrix.map((row) => row.reduce((sum, value, i) => sum + value * posterior[i], 0)));
}

function bayesUpdateWithLikelihood(prior, normalizedLikelihood) {
  const joint = prior.map((value, index) => value * normalizedLikelihood[index]);
  const evidence = Math.max(EPSILON, joint.reduce((sum, value) => sum + value, 0));
  const posterior = joint.map((value) => value / evidence);
  const vfe = posterior.reduce(
    (sum, value, index) =>
      sum + value * (Math.log(Math.max(EPSILON, value)) - Math.log(Math.max(EPSILON, joint[index]))),
    0,
  );
  const kl = klDivergence(posterior, normalize(joint));
  const surprise = -Math.log(evidence);
  return { posterior, likelihood: normalizedLikelihood, joint, evidence, vfe, kl, surprise };
}

export function bayesUpdate(prior, ligandRateUmS) {
  const means = [-0.08, 0, 0.08];
  const sigma = 0.045;
  const likelihoodRaw = means.map((mean) => gaussian(ligandRateUmS, mean, sigma));
  // The observation channel is represented as a categorical evidence vector
  // over the three declared hidden states. Normalizing here keeps p(o|s) in
  // [0,1] for the educational discrete model and makes surprisal non-negative.
  const normalizedLikelihood = normalize(likelihoodRaw);
  return bayesUpdateWithLikelihood(prior, normalizedLikelihood);
}

function distributionFromLogOdds(logOdds, flatMass = 0.16) {
  const risingShare = 1 / (1 + Math.exp(-clamp(logOdds, -12, 12)));
  const directionalMass = 1 - flatMass;
  return normalize([
    directionalMass * (1 - risingShare),
    flatMass,
    directionalMass * risingShare,
  ]);
}

const outcomeLikelihood = [
  [0.74, 0.18, 0.08],
  [0.16, 0.68, 0.16],
  [0.08, 0.18, 0.74],
];

function policyTerms(posterior, policy) {
  const qState = transitionPrior(posterior, policy);
  const qOutcome = [0, 0, 0];
  for (let state = 0; state < 3; state += 1) {
    for (let outcome = 0; outcome < 3; outcome += 1) {
      qOutcome[outcome] += qState[state] * outcomeLikelihood[state][outcome];
    }
  }
  const preferences = normalize([0.06, 0.24, 0.70]);
  const risk = qOutcome.reduce(
    (sum, value, index) => sum - value * Math.log(Math.max(EPSILON, preferences[index])),
    0,
  );
  const ambiguity = qState.reduce(
    (sum, value, state) => sum + value * entropy(outcomeLikelihood[state]),
    0,
  );
  const informationGain = entropy(qOutcome) - ambiguity;
  const effort = policy === "TUMBLE" ? 0.07 : 0.02;
  const efe = risk + ambiguity - informationGain + effort;
  return { qState, qOutcome: normalize(qOutcome), risk, ambiguity, informationGain, effort, efe };
}

export function stepAgent(agent, observation, dtS) {
  const dt = Math.max(0.001, dtS);
  const previousLigand = agent.lastObservation?.ligandUm ?? observation.ligandUm;
  const ligandRate = clamp((observation.ligandUm - previousLigand) / dt, -0.25, 0.25);
  const encoderPrior = observation.priorAngleDeg == null
    ? null
    : distributionFromLogOdds(observation.priorAngleDeg / 38, 0.18);
  const prior = encoderPrior ?? transitionPrior(agent.posterior, agent.selectedPolicy);
  const encoderLikelihood = observation.evidenceAngleDeg == null
    ? null
    : distributionFromLogOdds(observation.evidenceAngleDeg / 38, 0.12);
  const update = encoderLikelihood
    ? bayesUpdateWithLikelihood(prior, encoderLikelihood)
    : bayesUpdate(prior, ligandRate);
  const run = policyTerms(update.posterior, "RUN");
  const tumble = policyTerms(update.posterior, "TUMBLE");
  const policyPosterior = softmax([-4 * run.efe, -4 * tumble.efe]);
  const selectedPolicy = policyPosterior[0] >= policyPosterior[1] ? "RUN" : "TUMBLE";
  const signedRate = (-update.posterior[0] + update.posterior[2]) * 0.08;
  const predictedStators = clamp(1 + 10 * observation.loadPnNm / (observation.loadPnNm + 420), 0, 11);
  const stallTorque = predictedStators * 180 * clamp(observation.pmfMv / 150, 0.1, 1.5);
  const predictedSpeedRpm = Math.max(
    0,
    18000 * clamp(observation.pmfMv / 150, 0.1, 1.5) *
      (1 - clamp(observation.loadPnNm / Math.max(1, stallTorque), 0, 0.995)),
  );

  const risingPriorOdds = Math.max(EPSILON, prior[2]) / Math.max(EPSILON, prior[0]);
  const risingLikelihoodOdds = Math.max(EPSILON, update.likelihood[2]) / Math.max(EPSILON, update.likelihood[0]);
  const risingPosteriorOdds = Math.max(EPSILON, update.posterior[2]) / Math.max(EPSILON, update.posterior[0]);
  return {
    ...agent,
    timeS: agent.timeS + dt,
    priorAtUpdate: prior,
    predictivePrior: transitionPrior(update.posterior, selectedPolicy),
    posterior: update.posterior,
    likelihood: update.likelihood,
    policyPosterior,
    efe: [run.efe, tumble.efe],
    risk: [run.risk, tumble.risk],
    ambiguity: [run.ambiguity, tumble.ambiguity],
    informationGain: [run.informationGain, tumble.informationGain],
    selectedPolicy,
    predictedLigandUm: Math.max(0.001, observation.ligandUm + signedRate * 0.25),
    predictedSpeedRpm,
    predictedCwBias: observation.rotation === "CW" ? 0.6 : 0.25,
    predictedStators,
    vfe: update.vfe,
    surprise: update.surprise,
    evidenceLogOdds: Math.log(risingLikelihoodOdds),
    posteriorLogOdds: Math.log(risingPosteriorOdds),
    priorLogOdds: Math.log(risingPriorOdds),
    observationCount: agent.observationCount + 1,
    lastObservation: observation,
  };
}

export function actionFromAgent(agent) {
  return {
    policy: agent.selectedPolicy,
    selectedAtS: agent.timeS,
    probability: agent.selectedPolicy === "RUN" ? agent.policyPosterior[0] : agent.policyPosterior[1],
  };
}

export function stepSyntheticSystem(system, controls, dtS, receivedAtMs) {
  const action = actionFromAgent(system.agent);
  const world = stepWorld(system.world, action, controls, dtS);
  const observation = observeWorld(world, controls, receivedAtMs);
  const agent = stepAgent(system.agent, observation, dtS);
  return { world, agent, observation, action };
}

export function modelSnapshot(system, controls) {
  return {
    schema: "uni.flagellum.snapshot/1.0.0",
    capturedAt: new Date().toISOString(),
    separation: {
      worldOwns: ["ligand field", "position", "load", "motor mechanism", "true gradient"],
      boundaryCarries: ["timestamped observation", "bounded action"],
      agentOwns: ["generative model", "priors", "posterior", "policy beliefs", "prediction"],
    },
    controls,
    world: system.world,
    observation: system.observation,
    agent: system.agent,
    action: system.action,
  };
}
