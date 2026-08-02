import crypto from "node:crypto";

const EPS = 1e-12;
const SQRT_TWO_PI = Math.sqrt(2 * Math.PI);

export function mean(values) {
  return values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length);
}

export function sampleVariance(values) {
  if (values.length < 2) return 0;
  const center = mean(values);
  return values.reduce((sum, value) => sum + (value - center) ** 2, 0) / (values.length - 1);
}

function quantile(values, probability) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const index = (sorted.length - 1) * probability;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return sorted[lower];
  return sorted[lower] * (upper - index) + sorted[upper] * (index - lower);
}

function logSumExp(a, b) {
  const maximum = Math.max(a, b);
  return maximum + Math.log(Math.exp(a - maximum) + Math.exp(b - maximum));
}

// Lanczos approximation, sufficient for the bounded Weibull shape search.
function logGamma(z) {
  const coefficients = [
    0.9999999999998099,
    676.5203681218851,
    -1259.1392167224028,
    771.3234287776531,
    -176.6150291621406,
    12.5073432786869,
    -0.1385710952657201,
    9.984369578019572e-6,
    1.5056327351493116e-7,
  ];
  if (z < 0.5) return Math.log(Math.PI) - Math.log(Math.sin(Math.PI * z)) - logGamma(1 - z);
  let x = coefficients[0];
  const shifted = z - 1;
  for (let i = 1; i < coefficients.length; i += 1) x += coefficients[i] / (shifted + i);
  const t = shifted + coefficients.length - 1.5;
  return 0.5 * Math.log(2 * Math.PI) + (shifted + 0.5) * Math.log(t) - t + Math.log(x);
}

function goldenMinimum(objective, lower, upper, iterations = 100) {
  const ratio = (Math.sqrt(5) - 1) / 2;
  let a = lower;
  let b = upper;
  let c = b - ratio * (b - a);
  let d = a + ratio * (b - a);
  let fc = objective(c);
  let fd = objective(d);
  for (let i = 0; i < iterations; i += 1) {
    if (fc <= fd) {
      b = d;
      d = c;
      fd = fc;
      c = b - ratio * (b - a);
      fc = objective(c);
    } else {
      a = c;
      c = d;
      fc = fd;
      d = a + ratio * (b - a);
      fd = objective(d);
    }
  }
  return (a + b) / 2;
}

function weibullScale(shape) {
  return Math.exp(-logGamma(1 + 1 / shape));
}

function logWeibull(y, shape) {
  const scale = weibullScale(shape);
  const ratio = y / scale;
  return Math.log(shape) - Math.log(scale) + (shape - 1) * Math.log(ratio) - ratio ** shape;
}

function logLognormal(y, sigma) {
  const mu = -(sigma ** 2) / 2;
  const standardized = (Math.log(y) - mu) / sigma;
  return -Math.log(y * sigma * SQRT_TWO_PI) - 0.5 * standardized ** 2;
}

function mixtureSlowRate(weightFast, rateFast) {
  return (1 - weightFast) / (1 - weightFast / rateFast);
}

function logMixture(y, model) {
  return logSumExp(
    Math.log(model.weightFast) + Math.log(model.rateFast) - model.rateFast * y,
    Math.log(1 - model.weightFast) + Math.log(model.rateSlow) - model.rateSlow * y,
  );
}

export function fitDurationModels(normalizedTrainDurations) {
  if (normalizedTrainDurations.some((value) => !Number.isFinite(value) || value <= 0)) {
    throw new Error("Duration fitting requires finite positive normalized durations.");
  }
  const averageNll = (logDensity) => -mean(normalizedTrainDurations.map(logDensity));
  const weibullShape = goldenMinimum((shape) => averageNll((y) => logWeibull(y, shape)), 0.12, 5);
  const lognormalSigma = goldenMinimum((sigma) => averageNll((y) => logLognormal(y, sigma)), 0.05, 5);

  const mixtureObjective = (weightFast, logRateFast) => {
    const rateFast = Math.exp(logRateFast);
    const rateSlow = mixtureSlowRate(weightFast, rateFast);
    if (!(rateSlow > 0 && rateSlow < 1 && rateFast > 1)) return Number.POSITIVE_INFINITY;
    return averageNll((y) => logMixture(y, { weightFast, rateFast, rateSlow }));
  };
  let best = { weightFast: 0.5, logRateFast: Math.log(3), nll: Number.POSITIVE_INFINITY };
  for (let wi = 1; wi < 50; wi += 1) {
    const weightFast = wi / 50;
    for (let ri = 0; ri <= 80; ri += 1) {
      const logRateFast = Math.log(1.02) + (ri / 80) * (Math.log(80) - Math.log(1.02));
      const nll = mixtureObjective(weightFast, logRateFast);
      if (nll < best.nll) best = { weightFast, logRateFast, nll };
    }
  }
  let stepWeight = 0.03;
  let stepRate = 0.2;
  for (let iteration = 0; iteration < 100; iteration += 1) {
    let improved = false;
    for (const dw of [-stepWeight, 0, stepWeight]) {
      for (const dr of [-stepRate, 0, stepRate]) {
        if (dw === 0 && dr === 0) continue;
        const weightFast = Math.min(0.995, Math.max(0.005, best.weightFast + dw));
        const logRateFast = Math.min(Math.log(200), Math.max(Math.log(1.0001), best.logRateFast + dr));
        const nll = mixtureObjective(weightFast, logRateFast);
        if (nll + 1e-12 < best.nll) {
          best = { weightFast, logRateFast, nll };
          improved = true;
        }
      }
    }
    if (!improved) {
      stepWeight /= 2;
      stepRate /= 2;
    }
    if (stepWeight < 1e-7 && stepRate < 1e-7) break;
  }
  const rateFast = Math.exp(best.logRateFast);
  const rateSlow = mixtureSlowRate(best.weightFast, rateFast);
  return {
    exponential: { id: "M0_MEMORYLESS" },
    weibull: { id: "M1_WEIBULL", shape: weibullShape, scale: weibullScale(weibullShape) },
    lognormal: { id: "M2_LOGNORMAL", sigma: lognormalSigma, mu: -(lognormalSigma ** 2) / 2 },
    mixture: { id: "M3_UNI_TWO_TIMESCALE", weightFast: best.weightFast, rateFast, rateSlow },
  };
}

function logDensity(modelName, y, models) {
  if (modelName === "exponential") return -y;
  if (modelName === "weibull") return logWeibull(y, models.weibull.shape);
  if (modelName === "lognormal") return logLognormal(y, models.lognormal.sigma);
  if (modelName === "mixture") return logMixture(y, models.mixture);
  throw new Error(`Unknown model ${modelName}`);
}

function erf(value) {
  const sign = value < 0 ? -1 : 1;
  const x = Math.abs(value);
  const t = 1 / (1 + 0.3275911 * x);
  const polynomial = (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t;
  return sign * (1 - polynomial * Math.exp(-x * x));
}

function survival(modelName, y, models) {
  if (modelName === "exponential") return Math.exp(-y);
  if (modelName === "weibull") return Math.exp(-((y / models.weibull.scale) ** models.weibull.shape));
  if (modelName === "lognormal") {
    if (y <= 0) return 1;
    const z = (Math.log(y) - models.lognormal.mu) / (models.lognormal.sigma * Math.sqrt(2));
    return Math.max(0, Math.min(1, 0.5 * (1 - erf(z))));
  }
  if (modelName === "mixture") {
    const model = models.mixture;
    return model.weightFast * Math.exp(-model.rateFast * y) + (1 - model.weightFast) * Math.exp(-model.rateSlow * y);
  }
  throw new Error(`Unknown model ${modelName}`);
}

function inverseCdf(modelName, probability, models) {
  const targetSurvival = 1 - probability;
  let lower = 0;
  let upper = 1;
  while (survival(modelName, upper, models) > targetSurvival && upper < 1e6) upper *= 2;
  for (let i = 0; i < 100; i += 1) {
    const middle = (lower + upper) / 2;
    if (survival(modelName, middle, models) > targetSurvival) lower = middle;
    else upper = middle;
  }
  return (lower + upper) / 2;
}

export function posteriorSlowGivenSurvival(normalizedTime, mixture) {
  const slowMass = (1 - mixture.weightFast) * Math.exp(-mixture.rateSlow * normalizedTime);
  const fastMass = mixture.weightFast * Math.exp(-mixture.rateFast * normalizedTime);
  return slowMass / Math.max(EPS, slowMass + fastMass);
}

function seededRandom(seed) {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) | 0;
    let value = Math.imul(state ^ (state >>> 15), 1 | state);
    value = value + Math.imul(value ^ (value >>> 7), 61 | value) ^ value;
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

function interval(values) {
  return { lower: quantile(values, 0.025), upper: quantile(values, 0.975) };
}

function stateSummary(events, states) {
  return states.map((stateN) => {
    const selected = events.filter((event) => event.stateN === stateN);
    const durations = selected.map((event) => event.durationS);
    const onCount = selected.filter((event) => event.direction === "on").length;
    return {
      stateN,
      events: selected.length,
      motors: new Set(selected.map((event) => event.motorId)).size,
      meanDurationS: mean(durations),
      cvSquared: sampleVariance(durations) / Math.max(EPS, mean(durations) ** 2),
      onFraction: onCount / Math.max(1, selected.length),
    };
  });
}

function scoreEvents(events, stateMeans, models) {
  return events.map((event) => {
    const scale = stateMeans[event.stateN];
    const y = event.durationS / scale;
    const jacobian = -Math.log(scale);
    return {
      ...event,
      normalizedDuration: y,
      logScores: {
        exponential: logDensity("exponential", y, models) + jacobian,
        weibull: logDensity("weibull", y, models) + jacobian,
        lognormal: logDensity("lognormal", y, models) + jacobian,
        mixture: logDensity("mixture", y, models) + jacobian,
      },
    };
  });
}

function ksUniform(values) {
  const sorted = [...values].sort((a, b) => a - b);
  let statistic = 0;
  for (let i = 0; i < sorted.length; i += 1) {
    statistic = Math.max(statistic, Math.abs(sorted[i] - i / sorted.length), Math.abs((i + 1) / sorted.length - sorted[i]));
  }
  return statistic;
}

function directionMetrics(events, stateProbabilities, globalProbability) {
  const score = (probability, outcome) => {
    const p = Math.min(1 - EPS, Math.max(EPS, probability));
    return {
      logLoss: -(outcome * Math.log(p) + (1 - outcome) * Math.log(1 - p)),
      brier: (p - outcome) ** 2,
    };
  };
  const rows = events.map((event) => {
    const outcome = event.direction === "on" ? 1 : 0;
    return {
      motorId: event.motorId,
      state: score(stateProbabilities[event.stateN], outcome),
      global: score(globalProbability, outcome),
    };
  });
  return {
    stateLogLoss: mean(rows.map((row) => row.state.logLoss)),
    globalLogLoss: mean(rows.map((row) => row.global.logLoss)),
    stateBrier: mean(rows.map((row) => row.state.brier)),
    globalBrier: mean(rows.map((row) => row.global.brier)),
    rows,
  };
}

export function runObservedExperiment(dataset, protocol, identities = {}) {
  if (dataset.protocolId !== protocol.protocolId) throw new Error("Dataset/protocol identity mismatch.");
  const states = protocol.scope.primaryStates;
  const uncensored = dataset.events.filter((event) => !event.rightCensored && states.includes(event.stateN));
  const train = uncensored.filter((event) => event.partition === "train");
  const holdoutAll = uncensored.filter((event) => event.partition === "holdout");
  const trainIds = new Set(train.map((event) => event.motorId));
  const holdoutIdsAll = new Set(holdoutAll.map((event) => event.motorId));
  if ([...trainIds].some((id) => holdoutIdsAll.has(id))) throw new Error("Motor leakage detected.");

  const trainByState = Object.fromEntries(states.map((stateN) => [stateN, train.filter((event) => event.stateN === stateN)]));
  const holdoutByState = Object.fromEntries(states.map((stateN) => [stateN, holdoutAll.filter((event) => event.stateN === stateN)]));
  const stateMeans = Object.fromEntries(states.map((stateN) => [stateN, mean(trainByState[stateN].map((event) => event.durationS))]));
  const eligibleStates = states.filter(
    (stateN) => trainByState[stateN].length >= 20 && holdoutByState[stateN].length >= 20 && new Set(holdoutByState[stateN].map((event) => event.motorId)).size >= 5,
  );
  if (!eligibleStates.length) throw new Error("No primary states satisfy the frozen eligibility rule.");
  const trainEligible = train.filter((event) => eligibleStates.includes(event.stateN));
  const holdout = holdoutAll.filter((event) => eligibleStates.includes(event.stateN));
  const normalizedTrain = trainEligible.map((event) => event.durationS / stateMeans[event.stateN]);
  const models = fitDurationModels(normalizedTrain);
  const scored = scoreEvents(holdout, stateMeans, models);

  const trainOn = trainEligible.filter((event) => event.direction === "on").length;
  const globalDirectionProbability = (trainOn + 0.5) / (trainEligible.length + 1);
  const stateDirectionProbabilities = Object.fromEntries(eligibleStates.map((stateN) => {
    const events = trainByState[stateN];
    const on = events.filter((event) => event.direction === "on").length;
    return [stateN, (on + 0.5) / (events.length + 1)];
  }));
  const direction = directionMetrics(scored, stateDirectionProbabilities, globalDirectionProbability);

  const pointCv = mean(stateSummary(holdout, eligibleStates).map((row) => row.cvSquared));
  const pointDelta = {
    mixtureVsExponential: mean(scored.map((event) => event.logScores.mixture - event.logScores.exponential)),
    mixtureVsWeibull: mean(scored.map((event) => event.logScores.mixture - event.logScores.weibull)),
    mixtureVsLognormal: mean(scored.map((event) => event.logScores.mixture - event.logScores.lognormal)),
  };

  const random = seededRandom(protocol.uncertainty.seed);
  const holdoutMotorIds = [...new Set(scored.map((event) => event.motorId))].sort();
  const eventsByMotor = Object.fromEntries(holdoutMotorIds.map((id) => [id, scored.filter((event) => event.motorId === id)]));
  const bootstrap = { cv: [], exp: [], weibull: [], lognormal: [], direction: [] };
  for (let replicate = 0; replicate < protocol.uncertainty.replicates; replicate += 1) {
    const sampled = [];
    for (let i = 0; i < holdoutMotorIds.length; i += 1) {
      const id = holdoutMotorIds[Math.floor(random() * holdoutMotorIds.length)];
      sampled.push(...eventsByMotor[id]);
    }
    const eligibleInReplicate = eligibleStates.filter((stateN) => sampled.filter((event) => event.stateN === stateN).length >= 2);
    bootstrap.cv.push(mean(stateSummary(sampled, eligibleInReplicate).map((row) => row.cvSquared)));
    bootstrap.exp.push(mean(sampled.map((event) => event.logScores.mixture - event.logScores.exponential)));
    bootstrap.weibull.push(mean(sampled.map((event) => event.logScores.mixture - event.logScores.weibull)));
    bootstrap.lognormal.push(mean(sampled.map((event) => event.logScores.mixture - event.logScores.lognormal)));
    const sampledDirection = directionMetrics(sampled, stateDirectionProbabilities, globalDirectionProbability);
    bootstrap.direction.push(sampledDirection.globalLogLoss - sampledDirection.stateLogLoss);
  }

  const cvInterval = interval(bootstrap.cv);
  const deltaIntervals = {
    mixtureVsExponential: interval(bootstrap.exp),
    mixtureVsWeibull: interval(bootstrap.weibull),
    mixtureVsLognormal: interval(bootstrap.lognormal),
  };
  const normalizedHoldout = scored.map((event) => event.normalizedDuration);
  const q90 = quantile(normalizedHoldout, 0.9);
  const posteriorCurve = Array.from({ length: 41 }, (_, index) => {
    const normalizedTime = (index / 40) * q90;
    return {
      normalizedTime,
      posteriorSlow: posteriorSlowGivenSurvival(normalizedTime, models.mixture),
    };
  });
  const posteriorMonotone = posteriorCurve.every((point, index) => index === 0 || point.posteriorSlow + 1e-12 >= posteriorCurve[index - 1].posteriorSlow);

  const maxCurveTime = Math.min(10, Math.max(3, quantile(normalizedHoldout, 0.98)));
  const survivalCurve = Array.from({ length: 61 }, (_, index) => {
    const normalizedTime = (index / 60) * maxCurveTime;
    return {
      normalizedTime,
      observed: normalizedHoldout.filter((value) => value > normalizedTime).length / normalizedHoldout.length,
      exponential: survival("exponential", normalizedTime, models),
      weibull: survival("weibull", normalizedTime, models),
      lognormal: survival("lognormal", normalizedTime, models),
      mixture: survival("mixture", normalizedTime, models),
    };
  });

  const calibration = {};
  for (const modelName of ["exponential", "weibull", "lognormal", "mixture"]) {
    const pit = normalizedHoldout.map((value) => 1 - survival(modelName, value, models));
    const coverage = {};
    for (const level of [0.5, 0.8, 0.95]) {
      const lower = inverseCdf(modelName, (1 - level) / 2, models);
      const upper = inverseCdf(modelName, 1 - (1 - level) / 2, models);
      coverage[String(level)] = normalizedHoldout.filter((value) => value >= lower && value <= upper).length / normalizedHoldout.length;
    }
    calibration[modelName] = { pitMean: mean(pit), pitVariance: sampleVariance(pit), ksStatistic: ksUniform(pit), centralCoverage: coverage };
  }

  const h1Pass = cvInterval.lower > 1;
  const h2Pass = deltaIntervals.mixtureVsExponential.lower > 0;
  const directionImprovement = direction.globalLogLoss - direction.stateLogLoss;
  const directionInterval = interval(bootstrap.direction);
  const claims = [
    {
      hypothesisId: "H1_OVERDISPERSION",
      status: h1Pass ? "SUPPORTED_WITHIN_PROTOCOL" : "NOT_SUPPORTED",
      observed: pointCv,
      interval95: cvInterval,
      claim: h1Pass
        ? "Held-out dwell timing rejects the homogeneous memoryless duration prediction within the frozen analysis population."
        : "Held-out dwell timing did not reject the homogeneous memoryless duration prediction under the frozen criterion.",
      fence: "This does not uniquely identify a molecular hidden state; heterogeneity and nonstationarity remain alternatives.",
    },
    {
      hypothesisId: "H2_HELDOUT_LOG_SCORE",
      status: h2Pass ? "SUPPORTED_WITHIN_PROTOCOL" : "NOT_SUPPORTED",
      observed: pointDelta.mixtureVsExponential,
      interval95: deltaIntervals.mixtureVsExponential,
      unit: "nats per event",
      claim: h2Pass
        ? "The training-fitted two-timescale mixture assigned higher predictive density to held-out dwell events than the memoryless baseline."
        : "The training-fitted two-timescale mixture did not beat the memoryless baseline under the frozen held-out criterion.",
      fence: "Predictive superiority does not prove that the latent mixture components are biological states or that the motor performs Bayesian inference.",
    },
    {
      hypothesisId: "H3_SURVIVAL_POSTERIOR",
      status: posteriorMonotone ? "MODEL_CONSEQUENCE_CONFIRMED" : "MODEL_CONSEQUENCE_FAILED",
      observed: { initial: posteriorCurve[0].posteriorSlow, atHoldoutQ90: posteriorCurve.at(-1).posteriorSlow },
      claim: "Within the frozen mixture model, surviving longer without a transition increases posterior mass on the slower latent timescale.",
      fence: "This is exact inference in the declared model, illustrated with observed durations; it is not evidence that a bacterium represents this posterior.",
    },
    {
      hypothesisId: "H4_DIRECTION",
      status: directionImprovement > 0 && directionInterval.lower > 0
        ? "SUPPORTED_WITHIN_PROTOCOL"
        : directionImprovement > 0
          ? "INCONCLUSIVE_POINT_ESTIMATE_ONLY"
          : "NOT_SUPPORTED",
      observed: directionImprovement,
      interval95: directionInterval,
      unit: "log-loss reduction per event",
      claim: "Training-only stator-count-conditioned transition frequencies were evaluated on held-out motors.",
      fence: directionImprovement > 0 && directionInterval.lower <= 0
        ? "The point estimate improved, but the motor-cluster interval crosses zero. Secondary and inconclusive; it cannot rescue a failed duration hypothesis."
        : "Secondary check; it cannot rescue a failed duration hypothesis.",
    },
  ];

  const report = {
    schema: "uni.flagellum.observed-experiment/1.0.0",
    protocolId: protocol.protocolId,
    runId: null,
    executionClass: "CPU_ONLY_DETERMINISTIC_HELDOUT_ANALYSIS",
    identities,
    dataFlow: {
      worldProcess: "Previously recorded individual E. coli flagellar-motor stator-remodeling traces",
      observedBoundary: ["motor identity", "timestamp", "step-fitted stator occupancy"],
      hiddenFromModel: ["source-paper molecular interpretation", "holdout durations during fitting", "holdout transition direction during fitting"],
      inference: "Training-fitted survival likelihood updates posterior mass over two predictive timescales.",
      prediction: "Frozen probability density and survival curve for events from held-out motors.",
    },
    cohort: {
      sourceMotors: dataset.ingestion.motorCount,
      sourceEvents: dataset.ingestion.eventCount,
      trainMotors: new Set(trainEligible.map((event) => event.motorId)).size,
      holdoutMotors: holdoutMotorIds.length,
      trainEvents: trainEligible.length,
      holdoutEvents: scored.length,
      eligibleStates,
      exclusions: dataset.ingestion.exclusions,
    },
    fittedOnTrainingOnly: {
      stateMeanDurationS: stateMeans,
      normalizedDurationModels: models,
      direction: { globalOnProbability: globalDirectionProbability, onProbabilityByState: stateDirectionProbabilities },
    },
    heldoutResults: {
      stateSummary: stateSummary(holdout, eligibleStates),
      meanLogScoreNatsPerEvent: Object.fromEntries(["exponential", "weibull", "lognormal", "mixture"].map((name) => [name, mean(scored.map((event) => event.logScores[name]))])),
      pairedMixtureAdvantageNatsPerEvent: pointDelta,
      pairedMixtureAdvantageInterval95: deltaIntervals,
      meanCvSquaredAcrossStates: pointCv,
      meanCvSquaredInterval95: cvInterval,
      calibration,
      direction: {
        stateConditionedLogLoss: direction.stateLogLoss,
        globalLogLoss: direction.globalLogLoss,
        stateConditionedBrier: direction.stateBrier,
        globalBrier: direction.globalBrier,
        logLossImprovement: directionImprovement,
        logLossImprovementInterval95: directionInterval,
      },
    },
    claims,
    curves: { survival: survivalCurve, posteriorSlow: posteriorCurve },
    audit: {
      bootstrapReplicates: protocol.uncertainty.replicates,
      bootstrapSeed: protocol.uncertainty.seed,
      splitMethod: protocol.split.method,
      noMotorLeakage: true,
      outcomeAccessDuringFit: false,
      exactModelFencesRetained: true,
    },
  };
  report.runId = crypto.createHash("sha256").update(JSON.stringify(report)).digest("hex");
  return report;
}
