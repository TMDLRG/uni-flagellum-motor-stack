const EPS = 1e-300;

export function sourceCoefficients(stateN, c1, c2, c3, codeN0Branch = false) {
  const cs = stateN === 0 && !codeN0Branch
    ? []
    : stateN < 2
      ? [c1]
      : stateN < 3
        ? [c1, c2]
        : [c1, c2, c3];
  let coefficients = [1];
  for (const c of cs) {
    const next = Array(coefficients.length + 1).fill(0);
    coefficients.forEach((value, index) => {
      next[index] += value * (1 - c);
      next[index + 1] += value * c;
    });
    coefficients = next;
  }
  return coefficients;
}

export function sourceTerms(stateN, parameters, codeN0Branch = false) {
  const coefficients = sourceCoefficients(
    stateN,
    parameters.c1,
    parameters.c2,
    parameters.c3,
    codeN0Branch,
  );
  const kPlus = parameters.kPlusByN[stateN];
  const sigmaPlus = parameters.sigmaPlusPerSecond ?? parameters.sigmaPlus;
  const sigmaMinus = parameters.sigmaMinusPerSecond ?? parameters.sigmaMinus;
  const deltaSigma = sigmaPlus - sigmaMinus;
  return coefficients.map((weight, component) => ({
    component,
    weight,
    totalRate: kPlus + stateN * sigmaMinus + component * deltaSigma,
    offRate: stateN * sigmaMinus + component * deltaSigma,
  }));
}

export function sourceSurvival(timeSeconds, stateN, parameters, codeN0Branch = false) {
  return sourceTerms(stateN, parameters, codeN0Branch)
    .reduce((sum, term) => sum + term.weight * Math.exp(-term.totalRate * timeSeconds), 0);
}

export function sourceDensities(timeSeconds, stateN, parameters, codeN0Branch = false) {
  const terms = sourceTerms(stateN, parameters, codeN0Branch);
  const survival = terms.reduce((sum, term) => sum + term.weight * Math.exp(-term.totalRate * timeSeconds), 0);
  const plus = parameters.kPlusByN[stateN] * survival;
  const minus = terms.reduce(
    (sum, term) => sum + term.weight * term.offRate * Math.exp(-term.totalRate * timeSeconds),
    0,
  );
  return { survival, plus, minus, total: plus + minus };
}

export function sourceLogLikelihood(event, parameters) {
  const densities = sourceDensities(event.durationS, event.stateN, parameters);
  if (event.rightCensored) return Math.log(Math.max(EPS, densities.survival));
  if (event.direction === "on") return Math.log(Math.max(EPS, densities.plus));
  if (event.direction === "off") return Math.log(Math.max(EPS, densities.minus));
  throw new Error(`Uncensored event ${event.eventId ?? "unknown"} has no competing-risk direction.`);
}

export function sourceMoments(stateN, parameters, codeN0Branch = false) {
  const terms = sourceTerms(stateN, parameters, codeN0Branch);
  const mean = terms.reduce((sum, term) => sum + term.weight / term.totalRate, 0);
  const secondMoment = 2 * terms.reduce((sum, term) => sum + term.weight / (term.totalRate ** 2), 0);
  const fractionPlus = stateN === 0 && codeN0Branch ? 1 : parameters.kPlusByN[stateN] * mean;
  return {
    meanDwellSeconds: mean,
    fractionPlus,
    normalizedVariance: secondMoment / (mean ** 2) - 1,
  };
}
