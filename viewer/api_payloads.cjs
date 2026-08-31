// api_payloads.cjs — the ONE definition of what /api/classroom and /api/models aggregate.
//
// Two consumers, one truth:
//   1. viewer/bio_view.cjs serves these payloads LIVE (adding `now` at request time);
//   2. viewer/make_classroom_fixtures.cjs captures the same payloads as COMMITTED FIXTURES
//      (adding a `fixture` provenance block instead of `now`), so the vendored public copies of
//      the classroom and models pages can show real recorded engine output instead of a dead
//      fetch.
//
// The reader is INJECTABLE for one reason: a fixture claims "these are the bytes at commit X",
// so the fixture maker reads through `git show HEAD:<path>` — the commit's bytes — while the
// live server reads the working tree. Two aggregations that drift is how a live page and its
// recording would quietly start disagreeing; one module is the fix.
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const fsRead = (p) => { try { return fs.readFileSync(path.join(ROOT, p), "utf8"); } catch (e) { return null; } };

const SOURCES = {
  classroom: [
    "public/walkthrough-evidence-manifest.v1.json",
    "docs/classroom-assets/structures-manifest.json",
    "docs/classroom-assets/timescales.v1.json",
    "experiments/results/observed-experiment-report.json",
    "experiments/results/science-gates-report.json",
    "experiments/results/cross-study-parity-report.json",
  ],
  models: [
    "hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json",
    "experiments/results/observed-experiment-report.json",
    "audits/phase-b/b3-model-competition-result.json",
  ],
};

function make(read) {
  const rd = read || fsRead;
  const rj = (p) => { try { return JSON.parse(rd(p)); } catch (e) { return null; } };

  function gates() {
    const sci = rj("experiments/results/science-gates-report.json");
    const xs = rj("experiments/results/cross-study-parity-report.json");
    const pick = (r) => {
      if (!r) return null;
      const g = (r.gates || []).map((x) => ({ id: x.id || x.gateId, status: x.status }));
      return { summary: r.summary || null, gates: g };
    };
    return { science: pick(sci), cross: pick(xs) };
  }

  return {
    gates,
    classroomPayload: () => ({
      manifest: rj("public/walkthrough-evidence-manifest.v1.json"),
      structures: rj("docs/classroom-assets/structures-manifest.json"),
      timescales: rj("docs/classroom-assets/timescales.v1.json"),
      fitted: (rj("experiments/results/observed-experiment-report.json") || {}).fittedOnTrainingOnly || null,
      gates: gates(),
    }),
    modelsPayload: () => ({
      fside: rj("hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json"),
      observed: rj("experiments/results/observed-experiment-report.json"),
      b3models: (rj("audits/phase-b/b3-model-competition-result.json") || {}).models || null,
    }),
  };
}

module.exports = { make, SOURCES };
