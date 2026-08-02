export type RuntimeMode = "OBSERVED_REPLAY" | "SYNTHETIC_WORLD" | "LIVE_INSTRUMENT";
export type TruthClass = "OBSERVED" | "STRUCTURAL_RECONSTRUCTION" | "REDUCED_MODEL" | "UNI_PHYSICAL_ANALOGUE";
export type CameraLevel = "cell" | "bundle" | "motor" | "inference";

export interface EvidenceAsset {
  id: string;
  kind: "video" | "structure" | "dataset";
  evidenceType: "observed" | "derived" | "reconstruction" | "model";
  sourceClass: TruthClass;
  species: string;
  scale: string;
  citation: string;
  doi: string;
  href: string;
  localPath: string | null;
  sha256: string;
  rawSourceSha256?: string;
  license: string;
  permittedClaim: string;
}

export interface WalkthroughStep {
  id: string;
  index: number;
  title: string;
  camera: CameraLevel;
  runtimeMode: RuntimeMode;
  liveExperience: string;
  activity: string;
  paper: string;
  completion: string;
  narration: {
    what: string;
    why: string;
    evidence: string;
    couldMean: string;
    doesNotEstablish: string;
    test: string;
    reproduce: string;
    deeperMath: string;
  };
  evidenceIds: string[];
  gateIds: string[];
}

export interface ReplayFrame {
  sourceId: string;
  eventId: string;
  motorId: string;
  partition: "holdout";
  experimentalTimeS: number;
  measured: {
    stateN: number;
    durationS: number;
    eventAtS: number;
    nextStateN: number;
    direction: "on" | "off";
    jump: number;
    rightCensored: false;
  };
  missingFields: string[];
  citation: string;
}

export interface ObserverRecord {
  schema: string;
  sessionId: string;
  stepId: string;
  recordedAt: string;
  runtimeMode: RuntimeMode;
  truthClass: TruthClass;
  inputState: Record<string, unknown>;
  prediction: string;
  observation: string;
  calculation: string;
  interpretation: string;
  alternativeExplanation: string;
  confidence: number;
  evidenceIds: string[];
  gateIds: string[];
  applicationCommit: string;
  modelRunId: string | null;
  datasetHashes: Record<string, string>;
}

export interface LessonExport {
  schema: string;
  walkthroughSchema: string;
  manifestId: string;
  exportedAt: string;
  applicationCommit: string;
  modelRunId: string | null;
  gateStatusCounts: Record<string, number>;
  evidenceHashes: Record<string, string>;
  steps: Array<Pick<WalkthroughStep, "id" | "index" | "title" | "evidenceIds" | "gateIds">>;
  records: ObserverRecord[];
  reproduction: string[];
}

export const WALKTHROUGH_SCHEMA: string;
export const LESSON_EXPORT_SCHEMA: string;
export const WALKTHROUGH_MANIFEST_ID: string;
export const RUNTIME_MODES: RuntimeMode[];
export const TRUTH_CLASSES: TruthClass[];
export const EVIDENCE_ASSETS: EvidenceAsset[];
export const WALKTHROUGH_STEPS: WalkthroughStep[];
export const REPLAY_FRAMES: ReplayFrame[];
export function getReplayFrame(index: number): ReplayFrame;
export function truthClassForMode(mode: RuntimeMode): TruthClass;
export function paperExampleResults(): Record<string, number>;
export function createObserverRecord(input: Record<string, unknown>): ObserverRecord;
export function createLessonExport(records: ObserverRecord[], metadata?: Record<string, unknown>): LessonExport;
export function validateLessonExport(value: unknown): { valid: boolean; errors: string[] };
export function recordsToCsv(records: ObserverRecord[]): string;
export function validateWalkthrough(): { valid: boolean; errors: string[] };
