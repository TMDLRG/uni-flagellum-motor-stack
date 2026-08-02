"use client";

import { useEffect, useMemo, useState } from "react";
import type { RuntimeMode, WalkthroughStep } from "@/lib/walkthrough.js";

export type NotebookDraft = {
  prediction: string;
  observation: string;
  calculation: string;
  interpretation: string;
  alternativeExplanation: string;
  confidence: number;
};

type GuidedTeacherProps = {
  step: WalkthroughStep;
  stepCount: number;
  mode: RuntimeMode;
  running: boolean;
  deeper: boolean;
  draft: NotebookDraft;
  recordSaved: boolean;
  onDraft: (draft: NotebookDraft) => void;
  onBack: () => void;
  onNext: () => void;
  onPause: () => void;
  onRepeat: () => void;
  onDeeper: () => void;
  onExit: () => void;
  onSave: () => void;
};

function authoredSpeech(step: WalkthroughStep) {
  const n = step.narration;
  return [step.title, n.what, n.why, n.evidence, n.couldMean, n.doesNotEstablish, n.test, n.reproduce].join(" ");
}

export function GuidedTeacher({
  step, stepCount, mode, running, deeper, draft, recordSaved,
  onDraft, onBack, onNext, onPause, onRepeat, onDeeper, onExit, onSave,
}: GuidedTeacherProps) {
  const [speaking, setSpeaking] = useState(false);
  const speechAvailable = typeof window !== "undefined" && "speechSynthesis" in window;
  const progress = useMemo(() => Math.round(((step.index + 1) / stepCount) * 100), [step.index, stepCount]);

  useEffect(() => () => {
    if (typeof window !== "undefined") window.speechSynthesis?.cancel();
  }, []);

  const hearNarration = () => {
    if (!speechAvailable) return;
    window.speechSynthesis.cancel();
    if (speaking) { setSpeaking(false); return; }
    const utterance = new SpeechSynthesisUtterance(authoredSpeech(step));
    utterance.rate = 0.94;
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    setSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const update = <K extends keyof NotebookDraft>(key: K, value: NotebookDraft[K]) => onDraft({ ...draft, [key]: value });

  return (
    <aside className="teacher-panel" aria-labelledby="teacher-title">
      <div className="teacher-progress">
        <span>GUIDED LABORATORY · STEP {step.index + 1} OF {stepCount}</span>
        <progress value={progress} max="100" aria-label={`Walkthrough ${progress}% complete`}>{progress}%</progress>
      </div>
      <p className="eyebrow">{mode.replaceAll("_", " ")} · {step.camera.toUpperCase()} SCALE</p>
      <h2 id="teacher-title">{step.title}</h2>
      <p className="teacher-live">{step.liveExperience}</p>

      <div className="teacher-actions" aria-label="Walkthrough controls">
        <button type="button" onClick={onBack} disabled={step.index === 0}>Back</button>
        <button className="primary-button" type="button" onClick={onNext}>{step.index === stepCount - 1 ? "Finish" : "Next"}</button>
        <button type="button" onClick={onPause}>{running ? "Pause" : "Resume"}</button>
        <button type="button" onClick={onRepeat}>Repeat</button>
        <button type="button" onClick={hearNarration} disabled={!speechAvailable}>{speaking ? "Stop narration" : "Hear narration"}</button>
        <button type="button" aria-pressed={deeper} onClick={onDeeper}>{deeper ? "Hide deeper mathematics" : "Show deeper mathematics"}</button>
        <button type="button" onClick={onExit}>Exit walkthrough</button>
      </div>

      <div className="teacher-lesson" aria-live="polite">
        <section><h3>What is happening?</h3><p>{step.narration.what}</p></section>
        <section><h3>Why is it happening?</h3><p>{step.narration.why}</p></section>
        <section><h3>What does the evidence show?</h3><p>{step.narration.evidence}</p></section>
        <section><h3>What could it mean?</h3><p>{step.narration.couldMean}</p></section>
        <section className="truth-warning"><h3>What does it not establish?</h3><p>{step.narration.doesNotEstablish}</p></section>
        <section><h3>How would we test competing explanations?</h3><p>{step.narration.test}</p></section>
        <section><h3>How can another person reproduce it?</h3><p>{step.narration.reproduce}</p></section>
        {deeper && <section className="deeper-math"><h3>Deeper mathematics</h3><p><code>{step.narration.deeperMath}</code></p></section>}
      </div>

      <section className="paper-exercise" aria-labelledby="paper-title">
        <p className="eyebrow">PENCIL + PAPER</p>
        <h3 id="paper-title">Rebuild the claim without this screen</h3>
        <p>{step.paper}</p>
      </section>

      <section className="observer-notebook" aria-labelledby="notebook-title">
        <div className="notebook-heading">
          <div><p className="eyebrow">PRIVATE LOCAL NOTEBOOK</p><h3 id="notebook-title">What did you personally see?</h3></div>
          <span>{recordSaved ? "SAVED LOCALLY" : "NOT YET SAVED"}</span>
        </div>
        <label>Prior prediction<textarea value={draft.prediction} onChange={(event) => update("prediction", event.target.value)} placeholder={step.activity} /></label>
        <label>Observed values<textarea value={draft.observation} onChange={(event) => update("observation", event.target.value)} placeholder="Record time, source, units, and missing fields." /></label>
        <label>Calculation<textarea value={draft.calculation} onChange={(event) => update("calculation", event.target.value)} placeholder={step.paper} /></label>
        <label>Interpretation<textarea value={draft.interpretation} onChange={(event) => update("interpretation", event.target.value)} placeholder="What does this result support?" /></label>
        <label>Alternative explanation<textarea value={draft.alternativeExplanation} onChange={(event) => update("alternativeExplanation", event.target.value)} placeholder="Name at least one competing explanation or limitation." /></label>
        <label className="confidence-label"><span>Confidence <output>{draft.confidence}%</output></span><input type="range" min="0" max="100" step="5" value={draft.confidence} onChange={(event) => update("confidence", Number(event.target.value))} /></label>
        <button className="primary-button" type="button" onClick={onSave}>Save this observation</button>
        <p className="completion-criterion"><strong>Completion criterion:</strong> {step.completion}</p>
      </section>
    </aside>
  );
}
