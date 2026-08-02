"use client";

import { useCallback, useEffect, useState } from "react";
import type { ChangeEvent } from "react";
import type { Controls, SystemState } from "@/lib/uni-motor.js";
import {
  EVIDENCE_ASSETS,
  REPLAY_FRAMES,
  WALKTHROUGH_STEPS,
  createLessonExport,
  createObserverRecord,
  getReplayFrame,
  paperExampleResults,
  recordsToCsv,
  validateLessonExport,
  type CameraLevel,
  type LessonExport,
  type ObserverRecord,
  type RuntimeMode,
} from "@/lib/walkthrough.js";
import observedReport from "@/experiments/results/observed-experiment-report.json";
import scienceReport from "@/experiments/results/science-gates-report.json";
import crossStudyReport from "@/experiments/results/cross-study-parity-report.json";
import { BiologicalStage } from "./biological-stage";
import { GuidedTeacher, type NotebookDraft } from "./guided-teacher";

type LivingScienceWalkthroughProps = {
  system: SystemState;
  controls: Controls;
  running: boolean;
  instrumentConnected: boolean;
  onRunning: (running: boolean) => void;
  onControls: (controls: Controls) => void;
};

const STORAGE_KEY = "uni.flagellum.observer-notebook.v1";
const APPLICATION_COMMIT = process.env.NEXT_PUBLIC_COMMIT_SHA || "LOCAL-WORKTREE";
const emptyDraft: NotebookDraft = { prediction: "", observation: "", calculation: "", interpretation: "", alternativeExplanation: "", confidence: 50 };

function newSessionId() {
  return typeof crypto !== "undefined" && "randomUUID" in crypto ? crypto.randomUUID() : `local-${Date.now()}`;
}

function loadLocalNotebook(): { records: ObserverRecord[]; status: string } {
  if (typeof window === "undefined") return { records: [], status: "Notebook is stored only in this browser." };
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return { records: [], status: "Notebook is stored only in this browser." };
    const parsed = JSON.parse(saved) as LessonExport;
    const validation = validateLessonExport(parsed);
    if (validation.valid) return { records: parsed.records, status: `Restored ${parsed.records.length} local observation records.` };
  } catch { /* Invalid local data is ignored without leaving the browser. */ }
  return { records: [], status: "Saved notebook could not be restored; no data left this browser." };
}

function downloadText(name: string, contents: string, mime: string) {
  const url = URL.createObjectURL(new Blob([contents], { type: mime }));
  const anchor = document.createElement("a");
  anchor.href = url; anchor.download = name; anchor.click();
  URL.revokeObjectURL(url);
}

function countStatuses() {
  const counts: Record<string, number> = {};
  for (const report of [scienceReport, crossStudyReport]) {
    for (const [status, count] of Object.entries(report.summary.statusCounts)) counts[status] = (counts[status] || 0) + Number(count);
  }
  return counts;
}

type GateRecord = { id: string; title?: string; name?: string; status: string; criterion: string; limitation?: string; evidence: unknown };
const gateRecords = [...scienceReport.gates, ...crossStudyReport.gates] as GateRecord[];

function evidencePreview(evidence: unknown) {
  const serialized = JSON.stringify(evidence);
  return serialized.length > 260 ? `${serialized.slice(0, 257)}…` : serialized;
}

function GateTrace({ gateIds }: { gateIds: string[] }) {
  return (
    <section className="gate-trace" aria-labelledby="gate-trace-title">
      <div><p className="eyebrow">GATE TRACE</p><h3 id="gate-trace-title">Criteria, adverse results, and reproduction</h3></div>
      <div>{gateIds.map((id) => {
        const gate = gateRecords.find((candidate) => candidate.id === id);
        if (!gate) return null;
        const isCross = id.startsWith("X");
        return <details key={id} open={gate.status === "FAIL" || gate.status === "NOT_ESTABLISHED"}>
          <summary><span>{id}</span><strong>{gate.title || gate.name}</strong><b data-status={gate.status}>{gate.status.replaceAll("_", " ")}</b></summary>
          <dl>
            <div><dt>Criterion</dt><dd>{gate.criterion}</dd></div>
            <div><dt>Observed / derived value</dt><dd><code>{evidencePreview(gate.evidence)}</code></dd></div>
            <div><dt>Uncertainty</dt><dd>Intervals, sample units, and unavailable uncertainty remain exactly as recorded in the signed report evidence object; absence is not replaced by a guess.</dd></div>
            <div><dt>Limitation</dt><dd>{gate.limitation || "No separate limitation field; the criterion and evidence fence govern this gate."}</dd></div>
            <div><dt>Source artifact</dt><dd><a href="#research-desk">{isCross ? "experiments/results/cross-study-parity-report.json" : "experiments/results/science-gates-report.json"}</a></dd></div>
            <div><dt>Reproduce</dt><dd><code>{isCross ? "npm run cross-study:verify" : "npm run science:verify"}</code></dd></div>
          </dl>
        </details>;
      })}</div>
    </section>
  );
}

function ScientificReadout({ stepIndex, frame, system }: { stepIndex: number; frame: ReturnType<typeof getReplayFrame>; system: SystemState }) {
  const paper = paperExampleResults();
  const lattice = crossStudyReport.gates.find((gate) => gate.id === "X06_FINITE_LATTICE_COOPERATIVITY")!;
  const latticeEvidence = lattice.evidence as {
    J: number; baselineJ0Sse: number; sse: number; deltaAicInFavorOfCooperativity: number;
    momentFits: { unweighted: { J: number } }; crossStatisticJDisagreement: { absoluteDifference: number };
  };
  const heldout = observedReport.heldoutResults;
  const residual = system.observation.ligandUm - system.agent.predictedLigandUm;

  if (stepIndex < 4) return (
    <div className="science-readout">
      <span className="truth-badge model">REDUCED MODEL</span>
      <strong>Paper anchor</strong>
      <code>12 µm ÷ 0.6 s = {paper.cellSpeedUmS.toFixed(1)} µm/s</code>
      <p>Measure pixels against the visible source scale before converting. The animation does not supply a microscopy calibration.</p>
    </div>
  );
  if (stepIndex === 4) return (
    <div className="science-readout">
      <span className="truth-badge model">REDUCED MODEL</span><strong>Mechanical work, not variational free energy</strong>
      <code>W = τΔθ = 700 pN·nm × 2π = {paper.revolutionWorkJ.toExponential(3)} J ≈ {paper.revolutionWorkKbt.toFixed(0)} kBT at 300 K</code>
      <p>The torque is a declared exercise value. No energetic efficiency is inferred from this multiplication.</p>
    </div>
  );
  if (stepIndex === 5) return (
    <div className="science-readout">
      <span className="truth-badge model">REDUCED MODEL</span><strong>Independent-motor paper exercise</strong>
      <code>P(all three CCW) = (1 − 0.10)³ = {paper.allCcwProbability.toFixed(3)}</code>
      <p>Independence is an explicit simplifying assumption, not a biological fact.</p>
    </div>
  );
  if (stepIndex >= 6 && stepIndex <= 8) return (
    <div className="science-readout">
      <span className="truth-badge model">REDUCED MODEL</span><strong>Committed prediction ledger</strong>
      <dl>
        <div><dt>Prior q⁻(rising)</dt><dd>{system.agent.priorAtUpdate[2].toFixed(4)}</dd></div>
        <div><dt>Likelihood</dt><dd>{system.agent.likelihood[2].toFixed(4)}</dd></div>
        <div><dt>Posterior</dt><dd>{system.agent.posterior[2].toFixed(4)}</dd></div>
        <div><dt>Prediction</dt><dd>{system.agent.predictedLigandUm.toFixed(4)} µM</dd></div>
        <div><dt>Observed later</dt><dd>{system.observation.ligandUm.toFixed(4)} µM</dd></div>
        <div><dt>Residual</dt><dd>{residual >= 0 ? "+" : ""}{residual.toFixed(4)} µM</dd></div>
        <div><dt>F[q]</dt><dd>{system.agent.vfe.toFixed(4)} nat</dd></div>
      </dl>
      <code>Opost = Oprior × LR; example 2 × 3 = {paper.posteriorOdds}, so P = 6/7 = {paper.posteriorConditionalProbability.toFixed(4)}</code>
    </div>
  );
  if (stepIndex === 9) return (
    <div className="science-readout">
      <span className="truth-badge observed">OBSERVED</span><strong>Frozen held-out event</strong>
      <dl>
        <div><dt>Motor unit</dt><dd>{frame.motorId}</dd></div><div><dt>Event</dt><dd>{frame.eventId}</dd></div>
        <div><dt>Stators</dt><dd>{frame.measured.stateN} → {frame.measured.nextStateN}</dd></div><div><dt>Dwell</dt><dd>{frame.measured.durationS.toFixed(2)} s</dd></div>
        <div><dt>Missing</dt><dd>{frame.missingFields.join(", ")}</dd></div>
      </dl>
      <p>Held-out mixture advantage versus exponential: {heldout.pairedMixtureAdvantageNatsPerEvent.mixtureVsExponential.toFixed(3)} nat/event, 95% motor-cluster interval [{heldout.pairedMixtureAdvantageInterval95.mixtureVsExponential.lower.toFixed(3)}, {heldout.pairedMixtureAdvantageInterval95.mixtureVsExponential.upper.toFixed(3)}]. It did not beat lognormal.</p>
    </div>
  );
  if (stepIndex === 10) return (
    <div className="science-readout">
      <span className="truth-badge observed">OBSERVED + DERIVED</span><strong>Cross-study gate ledger</strong>
      <p>{crossStudyReport.summary.attributedStudies} attributed studies; at least {crossStudyReport.summary.directIndependentMotorCellLowerBound} directly reported independent motor/cell units.</p>
      <dl>{Object.entries(crossStudyReport.summary.statusCounts).map(([status, count]) => <div key={status}><dt>{status.replaceAll("_", " ")}</dt><dd>{count}</dd></div>)}</dl>
      <p>Study-level evidence does not become hundreds of independent replicates by counting every time point.</p>
    </div>
  );
  if (stepIndex === 11) return (
    <div className="science-readout falsifier-readout">
      <span className="truth-badge failure">FAIL · FALSIFIER RETAINED</span><strong>Incompatible lattice J estimates</strong>
      <dl>
        <div><dt>Full distribution J</dt><dd>{latticeEvidence.J.toFixed(3)}</dd></div>
        <div><dt>Moment-fit J</dt><dd>{latticeEvidence.momentFits.unweighted.J.toFixed(3)}</dd></div>
        <div><dt>|difference|</dt><dd>{latticeEvidence.crossStatisticJDisagreement.absoluteDifference.toFixed(3)}</dd></div>
        <div><dt>SSE J=0</dt><dd>{latticeEvidence.baselineJ0Sse.toFixed(5)}</dd></div>
        <div><dt>SSE fitted J</dt><dd>{latticeEvidence.sse.toFixed(5)}</dd></div>
        <div><dt>ΔAIC for cooperation</dt><dd>{latticeEvidence.deltaAicInFavorOfCooperativity.toFixed(3)}</dd></div>
      </dl>
      <p>{lattice.limitation}</p>
    </div>
  );
  return (
    <div className="science-readout falsifier-readout">
      <span className="truth-badge failure">PARTIAL PARITY ONLY</span><strong>The honest release result</strong>
      <p>{scienceReport.summary.proofClaim} Cross-study full biological parity: {String(crossStudyReport.summary.fullBiologicalParityAchieved)}.</p>
      <dl>{Object.entries(countStatuses()).map(([status, count]) => <div key={status}><dt>{status.replaceAll("_", " ")}</dt><dd>{count}</dd></div>)}</dl>
      <code>npm ci · npm test · npm run science:verify · npm run cross-study:verify</code>
    </div>
  );
}

export function LivingScienceWalkthrough({ system, controls, running, instrumentConnected, onRunning, onControls }: LivingScienceWalkthroughProps) {
  const [guided, setGuided] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [camera, setCamera] = useState<CameraLevel>("cell");
  const [mode, setMode] = useState<RuntimeMode>("OBSERVED_REPLAY");
  const [deeper, setDeeper] = useState(false);
  const [replayIndex, setReplayIndex] = useState(0);
  const [sessionId] = useState(newSessionId);
  const [drafts, setDrafts] = useState<Record<string, NotebookDraft>>({});
  const [records, setRecords] = useState<ObserverRecord[]>([]);
  const [notebookStatus, setNotebookStatus] = useState("Notebook is stored only in this browser.");
  const step = WALKTHROUGH_STEPS[stepIndex];
  const frame = getReplayFrame(replayIndex);
  const draft = drafts[step.id] || emptyDraft;

  useEffect(() => {
    const timer = window.setTimeout(() => {
      const local = loadLocalNotebook();
      setRecords(local.records); setNotebookStatus(local.status);
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  const lessonExport = useCallback((currentRecords = records) => createLessonExport(currentRecords, {
    applicationCommit: APPLICATION_COMMIT,
    modelRunId: observedReport.runId,
    gateStatusCounts: countStatuses(),
  }), [records]);

  const persist = useCallback((next: ObserverRecord[]) => {
    const value = lessonExport(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
    setRecords(next);
    setNotebookStatus(`Saved ${next.length} observation record${next.length === 1 ? "" : "s"} locally.`);
  }, [lessonExport]);

  const saveRecord = () => {
    const nextRecord = createObserverRecord({
      sessionId, stepId: step.id, runtimeMode: mode,
      inputState: mode === "OBSERVED_REPLAY" ? frame : { controls, observation: system.observation, prior: system.agent.priorAtUpdate },
      ...draft, applicationCommit: APPLICATION_COMMIT, modelRunId: observedReport.runId,
      datasetHashes: Object.fromEntries(EVIDENCE_ASSETS.map((asset) => [asset.id, asset.sha256])),
    });
    const next = [...records.filter((record) => !(record.sessionId === sessionId && record.stepId === step.id)), nextRecord];
    persist(next);
  };

  const changeStep = (next: number) => {
    const clamped = Math.max(0, Math.min(WALKTHROUGH_STEPS.length - 1, next));
    const nextStep = WALKTHROUGH_STEPS[clamped];
    setStepIndex(clamped); setCamera(nextStep.camera); setMode(nextStep.runtimeMode);
    setReplayIndex(clamped % REPLAY_FRAMES.length); setDeeper(false);
  };

  const exportJson = () => downloadText("uni-flagellum-observer-notebook.json", JSON.stringify(lessonExport(), null, 2), "application/json");
  const exportCsv = () => downloadText("uni-flagellum-observer-notebook.csv", recordsToCsv(records), "text/csv");
  const validateRoundTrip = () => {
    const roundTrip = JSON.parse(JSON.stringify(lessonExport()));
    const validation = validateLessonExport(roundTrip);
    if (validation.valid) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(roundTrip));
      setRecords(roundTrip.records);
      setNotebookStatus(`EXPORT → RE-IMPORT PASS · ${roundTrip.records.length} records, manifest and hashes preserved.`);
    } else setNotebookStatus(`ROUND-TRIP FAIL · ${validation.errors.join(" ")}`);
  };
  const importNotebook = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]; if (!file) return;
    try {
      const parsed = JSON.parse(await file.text()) as LessonExport;
      const validation = validateLessonExport(parsed);
      if (!validation.valid) throw new Error(validation.errors.join(" "));
      persist(parsed.records); setNotebookStatus(`IMPORT PASS · ${parsed.records.length} records restored from ${file.name}.`);
    } catch (error) { setNotebookStatus(`IMPORT REJECTED · ${error instanceof Error ? error.message : "invalid file"}`); }
    event.target.value = "";
  };

  return (
    <section className="living-walkthrough" aria-labelledby="living-lab-title" data-testid="living-walkthrough">
      <header className="walkthrough-intro">
        <div>
          <p className="eyebrow">PUBLIC LIVING SCIENCE WALKTHROUGH · v0.3</p>
          <h2 id="living-lab-title">Watch the life. Enter the motor. Challenge the model.</h2>
          <p>Recognizable biology first, measured signals second, inference and mathematics only after their truth boundaries are visible.</p>
        </div>
        {!guided ? <div className="walkthrough-entry">
          <button className="primary-button" type="button" onClick={() => { setGuided(true); changeStep(0); }}>Begin guided laboratory</button>
          <button type="button" onClick={() => setGuided(false)}>Explore freely</button>
        </div> : <span className="guided-status">GUIDED LAB ACTIVE</span>}
      </header>

      {!guided && <div className="free-explore-controls" aria-label="Free exploration controls">
        <div><span>Camera</span>{(["cell", "bundle", "motor", "inference"] as CameraLevel[]).map((value) => <button key={value} type="button" aria-pressed={camera === value} onClick={() => setCamera(value)}>{value}</button>)}</div>
        <label>Source mode<select value={mode} onChange={(event) => setMode(event.target.value as RuntimeMode)}>
          <option value="OBSERVED_REPLAY">OBSERVED REPLAY</option><option value="SYNTHETIC_WORLD">SYNTHETIC WORLD</option>
          <option value="LIVE_INSTRUMENT" disabled={!instrumentConnected}>LIVE INSTRUMENT{instrumentConnected ? "" : " · connect below"}</option>
        </select></label>
      </div>}

      <div className={guided ? "walkthrough-layout guided" : "walkthrough-layout"}>
        <div className="walkthrough-stage-column">
          <BiologicalStage camera={camera} mode={mode} replayFrame={frame} running={running} system={system} />
          {mode === "OBSERVED_REPLAY" && <div className="replay-controls" aria-label="Recorded replay controls">
            <button type="button" onClick={() => setReplayIndex((value) => value - 1)}>Previous recorded event</button>
            <span>Holdout event {((replayIndex % REPLAY_FRAMES.length) + REPLAY_FRAMES.length) % REPLAY_FRAMES.length + 1} of {REPLAY_FRAMES.length}</span>
            <button type="button" onClick={() => setReplayIndex((value) => value + 1)}>Next recorded event</button>
          </div>}
          {mode === "SYNTHETIC_WORLD" && <div className="walkthrough-parameters" aria-label="Reduced-model controls">
            <label><span>Ion-motive force <output>{controls.pmfMv.toFixed(0)} mV</output></span><input type="range" min="40" max="210" step="1" value={controls.pmfMv} onChange={(event) => onControls({ ...controls, pmfMv: Number(event.target.value) })} /></label>
            <label><span>Mechanical load <output>{controls.loadPnNm.toFixed(0)} pN·nm</output></span><input type="range" min="40" max="1900" step="10" value={controls.loadPnNm} onChange={(event) => onControls({ ...controls, loadPnNm: Number(event.target.value) })} /></label>
          </div>}
          <ScientificReadout stepIndex={guided ? stepIndex : camera === "inference" ? 8 : camera === "motor" ? 4 : 2} frame={frame} system={system} />
          {guided && <GateTrace gateIds={step.gateIds} />}
          {guided && stepIndex === 12 && <div className="continuation-actions"><a className="primary-button" href="#research-desk">Open gate ledger and CAD analogue</a><span>The printable UNI mechanism encodes log-odds addition; it is never a bacterial-motor replica.</span></div>}
          <section className="evidence-sources" aria-labelledby="source-title">
            <div><p className="eyebrow">SOURCE-PINNED EVIDENCE</p><h3 id="source-title">What this step may claim</h3></div>
            <div className="source-list">{EVIDENCE_ASSETS.filter((asset) => !guided || step.evidenceIds.includes(asset.id)).map((asset) => <article key={asset.id}>
              <span className={`truth-badge ${asset.sourceClass.toLowerCase()}`}>{asset.evidenceType === "derived" ? "OBSERVED · DERIVED TABLE" : asset.sourceClass.replaceAll("_", " ")}</span>
              <strong>{asset.citation}</strong><span>{asset.species} · {asset.scale} · {asset.license}</span>
              <p>{asset.permittedClaim}</p><a href={asset.href} target="_blank" rel="noreferrer">Open primary source</a><code>SHA-256 {asset.sha256}</code>
            </article>)}</div>
          </section>
        </div>

        {guided && <GuidedTeacher
          step={step} stepCount={WALKTHROUGH_STEPS.length} mode={mode} running={running} deeper={deeper}
          draft={draft} recordSaved={records.some((record) => record.sessionId === sessionId && record.stepId === step.id)}
          onDraft={(value) => setDrafts((current) => ({ ...current, [step.id]: value }))}
          onBack={() => changeStep(stepIndex - 1)} onNext={() => stepIndex === WALKTHROUGH_STEPS.length - 1 ? setGuided(false) : changeStep(stepIndex + 1)}
          onPause={() => onRunning(!running)} onRepeat={() => { setReplayIndex(stepIndex % REPLAY_FRAMES.length); onRunning(false); window.setTimeout(() => onRunning(true), 120); }}
          onDeeper={() => setDeeper((value) => !value)} onExit={() => setGuided(false)} onSave={saveRecord}
        />}
      </div>

      <section className="notebook-export" aria-labelledby="export-title">
        <div><p className="eyebrow">LOCAL OBSERVER EVIDENCE</p><h2 id="export-title">Your reproducible notebook</h2><p aria-live="polite" data-testid="notebook-status">{notebookStatus}</p></div>
        <div className="notebook-actions">
          <button type="button" onClick={exportJson}>Export JSON</button><button type="button" onClick={exportCsv}>Export CSV</button>
          <button type="button" onClick={() => window.print()}>Print worksheet</button><button type="button" onClick={validateRoundTrip} data-testid="roundtrip-test">Export → re-import self-test</button>
          <label className="file-import">Import JSON<input type="file" accept="application/json,.json" onChange={importNotebook} /></label>
        </div>
        <p>No name, account, analytics, submission, cloud storage, or network upload. Browser storage only. Clear it by clearing this site&apos;s local data.</p>
      </section>
    </section>
  );
}
