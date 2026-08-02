export type GradientState = "falling" | "flat" | "rising";
export type PolicyName = "RUN" | "TUMBLE";

export interface Controls {
  baseLigandUm: number;
  gradientPerMm: number;
  loadPnNm: number;
  pmfMv: number;
  sensoryNoise: number;
  timeScale: number;
}

export interface Observation {
  source: string;
  deviceTimeMs: number;
  receivedAtMs: number;
  ligandUm: number;
  receptorActivity: number | null;
  motorSpeedRpm: number;
  rotation: "CW" | "CCW";
  loadPnNm: number;
  pmfMv: number;
  cheYpUm?: number | null;
  stators?: number | null;
  priorAngleDeg?: number | null;
  evidenceAngleDeg?: number | null;
}

export interface WorldState {
  timeS: number;
  xUm: number;
  yUm: number;
  headingRad: number;
  ligandUm: number;
  previousLigandUm: number;
  receptorActivity: number;
  methylation: number;
  cheYpUm: number;
  stators: number;
  torquePnNm: number;
  speedRpm: number;
  cwBias: number;
  rotation: "CW" | "CCW";
  rotorAngleRad: number;
  trueGradient: GradientState;
}

export interface AgentState {
  timeS: number;
  posterior: number[];
  predictivePrior: number[];
  priorAtUpdate: number[];
  likelihood: number[];
  policyPosterior: number[];
  efe: number[];
  risk: number[];
  ambiguity: number[];
  informationGain: number[];
  selectedPolicy: PolicyName;
  predictedLigandUm: number;
  predictedSpeedRpm: number;
  predictedCwBias: number;
  predictedStators: number;
  vfe: number;
  surprise: number;
  evidenceLogOdds: number;
  posteriorLogOdds: number;
  priorLogOdds?: number;
  observationCount: number;
  lastObservation: Observation | null;
}

export interface ActionState {
  policy: PolicyName;
  selectedAtS: number;
  probability: number;
}

export interface SystemState {
  world: WorldState;
  agent: AgentState;
  observation: Observation;
  action: ActionState;
}

export interface BayesUpdate {
  posterior: number[];
  likelihood: number[];
  joint: number[];
  evidence: number;
  vfe: number;
  kl: number;
  surprise: number;
}

export const GRADIENT_STATES: string[];
export const OUTCOME_STATES: string[];
export const POLICY_NAMES: string[];
export function clamp(value: number, min: number, max: number): number;
export function normalize(values: number[]): number[];
export function softmax(logValues: number[]): number[];
export function entropy(probabilities: number[]): number;
export function klDivergence(q: number[], p: number[]): number;
export function hellinger(p: number[], q: number[]): number;
export function createWorld(overrides?: Partial<WorldState>): WorldState;
export function createAgent(overrides?: Partial<AgentState>): AgentState;
export function createControls(overrides?: Partial<Controls>): Controls;
export function stepWorld(world: WorldState, action: ActionState, controls: Controls, dtS: number): WorldState;
export function observeWorld(world: WorldState, controls: Controls, receivedAtMs: number): Observation;
export function instrumentObservation(frame: Record<string, unknown>, receivedAtMs: number): Observation;
export function bayesUpdate(prior: number[], ligandRateUmS: number): BayesUpdate;
export function stepAgent(agent: AgentState, observation: Observation, dtS: number): AgentState;
export function actionFromAgent(agent: AgentState): ActionState;
export function stepSyntheticSystem(system: SystemState, controls: Controls, dtS: number, receivedAtMs: number): SystemState;
export function modelSnapshot(system: SystemState, controls: Controls): Record<string, unknown>;
