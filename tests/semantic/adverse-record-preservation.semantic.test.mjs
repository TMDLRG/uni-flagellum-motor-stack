// Semantic gate: the historical Phase-C adverse result may not be laundered.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   property D1P11_ADVERSE_RECORD_PRESERVATION.
//
// The Phase-C blind mutation battery produced 10 SURVIVED and 0 DETECTED_SEMANTIC.
// That is ADVERSE evidence about semantic coverage. CLAUDE.md requires that failed,
// blocked, external and not-run gates remain visible, and that apparent harmony is
// never created by suppressing an adverse result.
//
// D1 adds detection for those same ten properties. That makes this gate necessary
// rather than decorative: once a later phase can show detection, there is a standing
// incentive to quietly restate the earlier 0/10 outcome. This gate makes deletion,
// count laundering, outcome relabelling, and silent divergence between the canonical
// result and its preserved evidence copy all fail loudly.
//
// Oracle independence: the expected counts and mutation identifiers are frozen literals
// restated here and in the D1 protocol. This gate does not consult the Phase-C runner
// or its classifier to decide what the historical outcome was.
//
// Not satisfied by hash: the primary assertions are on PARSED COUNTS and identifiers,
// which are semantic content and fail on their own under laundering. The canonical
// versus evidence-copy byte comparison is an ADDITIONAL consistency assertion, not the
// basis of the gate.
//
// Target corruptions:
//   D1P01_ADVERSE_COUNTS_LAUNDERED         canonical counts rewritten as favourable
//   D1P02_ADVERSE_EVIDENCE_COPY_DIVERGED   only the evidence copy rewritten

import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

const CANONICAL_RESULT = path.join(root, "audits", "phase-c", "blind-mutation-result.codex.v1.json");
const EVIDENCE_RESULT = path.join(
  root,
  "audits",
  "phase-c",
  "blind-mutation-evidence.codex.v1",
  "blind-mutation-result.codex.v1.json",
);

// The frozen historical outcome. Ten fresh, independently authored corruptions were
// applied and NONE was detected by the semantic suite as it stood at that time.
const FROZEN_ADVERSE_COUNTS = {
  DETECTED_SEMANTIC: 0,
  DETECTED_BY_HASH_ONLY: 0,
  SURVIVED: 10,
  NOT_RUN: 0,
  INCONCLUSIVE: 0,
};

const FROZEN_SURVIVOR_IDS = [
  "CXM01_SECONDS_DENSITY_JACOBIAN_OMITTED",
  "CXM02_SURVIVAL_POSTERIOR_USES_EVENT_DENSITY",
  "CXM03_SAMPLE_VARIANCE_BESSEL_CORRECTION_DROPPED",
  "CXM04_HIDDEN_TRUE_GRADIENT_CROSSES_BOUNDARY",
  "CXM05_INSTRUMENT_STATOR_COUNT_UNBOUNDED",
  "CXM06_STATOR_RECRUITMENT_ERASES_LOAD_RESPONSE",
  "CXM07_FIRST_PASSAGE_WEIGHTS_NOT_NORMALIZED",
  "CXM08_OFF_HAZARD_OMITS_STATOR_MULTIPLICITY",
  "CXM09_EXPONENTIAL_SECOND_MOMENT_FACTOR_DROPPED",
  "CXM10_PERIODIC_LATTICE_OPENED",
];

const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

test("D1P11 historical phase-c adverse 0/10 detection result is preserved unlaundered", () => {
  assert.ok(
    fs.existsSync(CANONICAL_RESULT),
    "The adverse Phase-C blind mutation result has been DELETED. The 0/10 semantic detection outcome is historical " +
      "evidence and must remain visible; removing it is truth laundering, not remediation.",
  );

  const result = JSON.parse(fs.readFileSync(CANONICAL_RESULT, "utf8"));

  assert.deepEqual(
    result.classificationCounts,
    FROZEN_ADVERSE_COUNTS,
    "The adverse Phase-C classification counts have been altered. " +
      `The frozen historical outcome is ${JSON.stringify(FROZEN_ADVERSE_COUNTS)} -- ten SURVIVED and zero ` +
      `DETECTED_SEMANTIC -- observed ${JSON.stringify(result.classificationCounts)}. Later phases may ADD new ` +
      "detection evidence; they may never restate this 0/10 result as favourable.",
  );

  const observedIds = result.outcomes.map((outcome) => outcome.id).sort();
  assert.deepEqual(
    observedIds,
    [...FROZEN_SURVIVOR_IDS].sort(),
    "The set of Phase-C mutation outcomes has changed. " +
      `Expected the ten frozen survivor identifiers, observed ${JSON.stringify(observedIds)}. ` +
      "Removing an adverse outcome row is truth laundering.",
  );

  for (const outcome of result.outcomes) {
    assert.equal(
      outcome.classification,
      "SURVIVED",
      `Phase-C outcome ${outcome.id} has been relabelled from SURVIVED to ${outcome.classification}. ` +
        "The historical adverse result records that this corruption was NOT detected by the semantic suite as it " +
        "stood at that time. D1 detection of the same property is separate later evidence and may not be " +
        "backdated into the Phase-C record.",
    );
  }
});

test("D1P11 the preserved phase-c evidence copy has not silently diverged from the canonical adverse result", () => {
  assert.ok(
    fs.existsSync(EVIDENCE_RESULT),
    "The preserved evidence copy of the adverse Phase-C result is missing. Both the canonical result and its " +
      "evidence copy are part of the historical record.",
  );

  const canonicalBytes = fs.readFileSync(CANONICAL_RESULT);
  const evidenceBytes = fs.readFileSync(EVIDENCE_RESULT);

  const evidence = JSON.parse(evidenceBytes.toString("utf8"));
  assert.deepEqual(
    evidence.classificationCounts,
    FROZEN_ADVERSE_COUNTS,
    "The PRESERVED EVIDENCE COPY of the adverse Phase-C result carries altered classification counts. " +
      `Expected ${JSON.stringify(FROZEN_ADVERSE_COUNTS)}, observed ${JSON.stringify(evidence.classificationCounts)}. ` +
      "Laundering the evidence copy while leaving the canonical file intact is still laundering.",
  );

  assert.equal(
    sha256(evidenceBytes),
    sha256(canonicalBytes),
    "The canonical adverse Phase-C result and its preserved evidence copy have DIVERGED. " +
      `Canonical digest ${sha256(canonicalBytes)}, evidence copy digest ${sha256(evidenceBytes)}. ` +
      "Two copies of the same adverse record must agree; a silent divergence means one of them has been edited.",
  );
});

test("D1P11 the phase-c adverse result is not weakened by the D1 remediation contract", () => {
  // D1 is target-specific remediation. It must not be described anywhere in its own
  // frozen contract as establishing general or future robustness, and it must keep the
  // Phase-C outcome addressable rather than superseded.
  const protocolPath = path.join(root, "audits", "phase-d", "d1-semantic-remediation-protocol.v1.json");
  assert.ok(
    fs.existsSync(protocolPath),
    "The D1 remediation protocol is missing; the remediation claim boundary cannot be checked.",
  );
  const protocol = JSON.parse(fs.readFileSync(protocolPath, "utf8"));

  // Structural, not prose matching. A raw text search cannot tell an affirmative claim
  // apart from the protocol's own prohibition of that claim, so the assertions below
  // read declared FIELDS whose meaning is fixed by the schema.
  assert.ok(
    /TARGET COVERAGE/i.test(protocol.claimBoundary.whatThisMeasures + protocol.claimBoundary.whatThisDoesNotMeasure),
    "The D1 protocol no longer declares its result as TARGET COVERAGE. Remediation of ten known corruptions is " +
      "target coverage, not evidence of general or future robustness.",
  );
  assert.ok(
    /robustness/i.test(protocol.claimBoundary.whatThisDoesNotMeasure),
    "The D1 protocol no longer excludes general or future robustness in its whatThisDoesNotMeasure boundary. " +
      "Detecting corruptions that were known when the gates were written cannot support a robustness claim.",
  );
  assert.ok(
    typeof protocol.claimBoundary.notBlind === "string" && protocol.claimBoundary.notBlind.length > 0,
    "The D1 protocol must continue to disclose that this battery is deliberately NOT blind, so the low evidential " +
      "weight of its confirmation stays visible.",
  );
  assert.ok(
    /P0/.test(protocol.claimBoundary.parityLadderEffect) && /cannot move P2/i.test(protocol.claimBoundary.parityLadderEffect),
    "The D1 protocol no longer bounds its effect to the P0 and P1 parity levels. Semantic regression coverage " +
      "produces no new observation and cannot move observational parity or above.",
  );

  const predictionsPath = path.join(root, "audits", "phase-d", "d1-semantic-remediation-predictions.v1.json");
  const predictions = JSON.parse(fs.readFileSync(predictionsPath, "utf8"));
  const forbidden = predictions.whatAConfirmedResultWouldAndWouldNotLicense?.forbidden ?? [];
  assert.ok(
    forbidden.some((entry) => /robustness/i.test(entry)),
    "The D1 predictions record no longer forbids claiming general or future robustness from a confirmed result.",
  );
  assert.ok(
    forbidden.some((entry) => /restat|weaken/i.test(entry) && /phase-?c|0\/10/i.test(entry)),
    "The D1 predictions record no longer forbids restating or weakening the Phase-C 0/10 adverse result.",
  );
});
