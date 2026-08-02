export interface CadPart {
  id: string;
  label: string;
  teeth: number;
  role: string;
  x: number;
  y: number;
  encoder: boolean;
  moduleMm: number;
  pitchDiameterMm: number;
  outerDiameterMm: number;
  thicknessMm: number;
  boreMm: number;
  clearanceMm: number;
  material: string;
}

export interface CadManifest {
  schema: string;
  identity: string;
  explicitNonClaim: string;
  units: string;
  printProfile: Record<string, string | number>;
  electronicsInterface: Record<string, unknown>;
  mathematicalTransmission: Record<string, string>;
  parts: CadPart[];
  assembly: string[];
}

export const CAD_SCHEMA: string;
export function createCadManifest(options?: Record<string, unknown>): CadManifest;
export function openScadFromManifest(manifest: CadManifest): string;
