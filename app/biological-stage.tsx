"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { SystemState } from "@/lib/uni-motor.js";
import type { CameraLevel, ReplayFrame, RuntimeMode } from "@/lib/walkthrough.js";

type BiologicalStageProps = {
  camera: CameraLevel;
  mode: RuntimeMode;
  replayFrame: ReplayFrame;
  running: boolean;
  system: SystemState;
};

type Palette = {
  ink: string;
  muted: string;
  ground: string;
  line: string;
  signal: string;
  prediction: string;
  belief: string;
  evidence: string;
  danger: string;
  good: string;
};

const fallbackPalette: Palette = {
  ink: "#e7f0ef", muted: "#9db1af", ground: "#071014", line: "#43605f",
  signal: "#70e2d5", prediction: "#e4ae63", belief: "#8492cb",
  evidence: "#af75bd", danger: "#ef8f78", good: "#87d7a1",
};

function paletteFrom(canvas: HTMLCanvasElement): Palette {
  const css = getComputedStyle(canvas);
  const read = (name: string, fallback: string) => css.getPropertyValue(name).trim() || fallback;
  return {
    ink: read("--ink", fallbackPalette.ink), muted: read("--muted", fallbackPalette.muted),
    ground: read("--ground", fallbackPalette.ground), line: read("--line-strong", fallbackPalette.line),
    signal: read("--signal", fallbackPalette.signal), prediction: read("--prediction", fallbackPalette.prediction),
    belief: read("--belief", fallbackPalette.belief), evidence: read("--evidence", fallbackPalette.evidence),
    danger: read("--danger", fallbackPalette.danger), good: read("--good", fallbackPalette.good),
  };
}

function text(ctx: CanvasRenderingContext2D, value: string, x: number, y: number, color: string, size = 12, align: CanvasTextAlign = "left") {
  ctx.fillStyle = color;
  ctx.font = `500 ${size}px ui-monospace, SFMono-Regular, Consolas, monospace`;
  ctx.textAlign = align;
  ctx.fillText(value, x, y);
}

function arrow(ctx: CanvasRenderingContext2D, x1: number, y1: number, x2: number, y2: number, color: string, label?: string) {
  const angle = Math.atan2(y2 - y1, x2 - x1);
  ctx.strokeStyle = color;
  ctx.fillStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - Math.cos(angle - 0.55) * 9, y2 - Math.sin(angle - 0.55) * 9);
  ctx.lineTo(x2 - Math.cos(angle + 0.55) * 9, y2 - Math.sin(angle + 0.55) * 9);
  ctx.closePath(); ctx.fill();
  if (label) text(ctx, label, (x1 + x2) / 2, (y1 + y2) / 2 - 7, color, 11, "center");
}

function helix(ctx: CanvasRenderingContext2D, startX: number, startY: number, length: number, amplitude: number, phase: number, color: string, spread = 0) {
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i <= 90; i += 1) {
    const t = i / 90;
    const x = startX - t * length;
    const y = startY + Math.sin(t * Math.PI * 9 + phase) * amplitude + spread * t * t;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();
}

function drawCell(ctx: CanvasRenderingContext2D, width: number, height: number, phase: number, system: SystemState, p: Palette, bundleDetail = false) {
  const isTumble = system.observation.rotation === "CW";
  const cx = width * (bundleDetail ? 0.69 : 0.62);
  const cy = height * 0.5;
  const bodyW = Math.min(width * (bundleDetail ? 0.34 : 0.29), 260);
  const bodyH = bodyW * 0.37;

  const gradient = ctx.createLinearGradient(0, 0, width, 0);
  gradient.addColorStop(0, "rgba(112,226,213,0.01)");
  gradient.addColorStop(1, "rgba(112,226,213,0.17)");
  ctx.fillStyle = gradient; ctx.fillRect(0, 0, width, height);
  for (let i = 0; i < 22; i += 1) {
    const x = ((i * 83 + 31) % 101) / 101 * width;
    const y = ((i * 47 + 13) % 97) / 97 * height;
    const r = 1.2 + 3 * (x / width);
    ctx.fillStyle = p.signal; ctx.globalAlpha = 0.12 + 0.35 * (x / width);
    ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(bundleDetail ? 0 : Math.sin(phase * 0.2) * 0.04);
  ctx.fillStyle = "rgba(112,226,213,0.14)";
  ctx.strokeStyle = p.signal; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.roundRect(-bodyW / 2, -bodyH / 2, bodyW, bodyH, bodyH / 2); ctx.fill(); ctx.stroke();
  for (let i = 0; i < 24; i += 1) {
    const angle = i * 2.399;
    const rx = Math.cos(angle) * bodyW * 0.37;
    const ry = Math.sin(angle * 1.7) * bodyH * 0.29;
    ctx.fillStyle = i % 3 ? p.good : p.prediction;
    ctx.globalAlpha = 0.42;
    ctx.beginPath(); ctx.arc(rx, ry, 1.7, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;
  const originX = -bodyW / 2 + 3;
  const flagLength = Math.min(width * 0.48, 360);
  [-0.25, -0.08, 0.1, 0.27, 0.42].forEach((offset, index) => {
    const spread = isTumble ? (index - 2) * bodyH * 0.54 : offset * bodyH * 0.13;
    helix(ctx, originX, offset * bodyH, flagLength, bundleDetail ? 11 : 7, phase * (isTumble ? -2.2 : 2.8) + index * 0.6, index === 2 ? p.signal : p.muted, spread);
  });
  ctx.restore();

  ctx.setLineDash([5, 5]); ctx.strokeStyle = p.prediction; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(width * 0.1, height * 0.76); ctx.bezierCurveTo(width * 0.3, height * 0.58, width * 0.44, height * 0.78, cx - bodyW * 0.6, cy + bodyH); ctx.stroke(); ctx.setLineDash([]);
  text(ctx, isTumble ? "CW · BUNDLE SEPARATES · TUMBLE" : "CCW · BUNDLE FORMS · RUN", 18, 28, isTumble ? p.danger : p.good, 13);
  text(ctx, "E. coli behavioural reconstruction", 18, 47, p.muted, 11);
  const scaleX = width - 132;
  ctx.strokeStyle = p.ink; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(scaleX, height - 28); ctx.lineTo(scaleX + 80, height - 28); ctx.stroke();
  text(ctx, bundleDetail ? "0.5 µm" : "1 µm", scaleX + 40, height - 35, p.ink, 11, "center");
}

function drawMotor(ctx: CanvasRenderingContext2D, width: number, height: number, phase: number, system: SystemState, mode: RuntimeMode, replayFrame: ReplayFrame, p: Palette) {
  const cx = width * 0.51;
  const top = height * 0.11;
  const innerY = height * 0.59;
  const outerY = height * 0.28;
  const pgY = height * 0.42;
  const rotorR = Math.min(width, height) * 0.115;

  const membrane = (y: number, label: string, color: string) => {
    ctx.fillStyle = color; ctx.fillRect(0, y - 8, width, 16);
    ctx.strokeStyle = p.line; ctx.strokeRect(0, y - 8, width, 16);
    text(ctx, label, 15, y - 15, p.muted, 10);
  };
  membrane(outerY, "OUTER MEMBRANE", "rgba(132,146,203,0.20)");
  membrane(pgY, "PEPTIDOGLYCAN", "rgba(228,174,99,0.16)");
  membrane(innerY, "INNER MEMBRANE", "rgba(112,226,213,0.18)");

  ctx.strokeStyle = p.ink; ctx.lineWidth = 10; ctx.beginPath(); ctx.moveTo(cx, top - 20); ctx.lineTo(cx, innerY + rotorR * 1.5); ctx.stroke();
  ctx.strokeStyle = p.signal; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx, top - 30); ctx.bezierCurveTo(cx + 58, top - 54, cx - 52, top - 82, cx + 8, top - 110); ctx.stroke();
  text(ctx, "FILAMENT", cx + 18, top - 76, p.signal, 10);
  text(ctx, "HOOK", cx + 22, top + 14, p.muted, 10);
  text(ctx, "ROD", cx + 18, pgY - 15, p.muted, 10);

  const ring = (y: number, r: number, label: string, color: string) => {
    ctx.strokeStyle = color; ctx.lineWidth = 7; ctx.beginPath(); ctx.ellipse(cx, y, r, r * 0.24, 0, 0, Math.PI * 2); ctx.stroke();
    text(ctx, label, cx + r + 15, y + 4, color, 10);
  };
  ring(outerY, rotorR * 0.58, "L RING", p.belief);
  ring(pgY, rotorR * 0.74, "P RING", p.prediction);
  ring(innerY, rotorR, "MS RING", p.signal);
  ring(innerY + rotorR * 0.82, rotorR * 1.16, "C RING · FliG/FliM/FliN", p.evidence);

  for (let i = 0; i < 7; i += 1) {
    const a = i / 7 * Math.PI * 2 + phase * (system.observation.rotation === "CW" ? -1 : 1);
    const x = cx + Math.cos(a) * rotorR * 1.48;
    const y = innerY + Math.sin(a) * rotorR * 0.45;
    ctx.fillStyle = "rgba(228,174,99,0.23)"; ctx.strokeStyle = p.prediction; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.roundRect(x - 14, y - 18, 28, 36, 9); ctx.fill(); ctx.stroke();
  }
  text(ctx, "MotA₅MotB₂ STATORS · homologous structural constraint", 15, height - 50, p.prediction, 10);

  for (let i = 0; i < 16; i += 1) {
    const x = ((i * 61) % 97) / 97 * width;
    const y = innerY - 30 + ((phase * 52 + i * 29) % 46);
    ctx.fillStyle = p.signal; ctx.globalAlpha = 0.4 + (i % 3) * 0.18;
    ctx.beginPath(); ctx.arc(x, y, 2.5, 0, Math.PI * 2); ctx.fill();
  }
  ctx.globalAlpha = 1;
  arrow(ctx, 40, innerY - 42, 40, innerY + 38, p.signal, "H⁺ flow");
  if (mode === "OBSERVED_REPLAY") {
    text(ctx, `MEASURED: ${replayFrame.measured.stateN} → ${replayFrame.measured.nextStateN} stators · ${replayFrame.measured.durationS.toFixed(2)} s`, 15, 27, p.good, 12);
    text(ctx, "rotation and speed missing from this event record", 15, 45, p.danger, 10);
  } else {
    text(ctx, `${system.observation.rotation} · ${Math.round(system.observation.motorSpeedRpm)} rpm`, 15, 27, system.observation.rotation === "CW" ? p.danger : p.good, 12);
  }
  text(ctx, "25 nm schematic scale · not a direct optical view", width - 15, height - 20, p.muted, 10, "right");
}

function probabilityBar(ctx: CanvasRenderingContext2D, x: number, y: number, width: number, value: number, label: string, color: string, p: Palette) {
  text(ctx, label, x, y - 7, p.muted, 10);
  ctx.fillStyle = "rgba(255,255,255,0.05)"; ctx.fillRect(x, y, width, 13);
  ctx.fillStyle = color; ctx.fillRect(x, y, width * Math.max(0, Math.min(1, value)), 13);
  text(ctx, value.toFixed(3), x + width + 8, y + 11, p.ink, 10);
}

function drawInference(ctx: CanvasRenderingContext2D, width: number, height: number, system: SystemState, p: Palette) {
  const boundaryX = width * 0.44;
  ctx.fillStyle = "rgba(228,174,99,0.04)"; ctx.fillRect(0, 0, boundaryX, height);
  ctx.fillStyle = "rgba(132,146,203,0.05)"; ctx.fillRect(boundaryX, 0, width - boundaryX, height);
  ctx.setLineDash([8, 7]); ctx.strokeStyle = p.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(boundaryX, 25); ctx.lineTo(boundaryX, height - 25); ctx.stroke(); ctx.setLineDash([]);
  text(ctx, "WORLD PROCESS", 18, 28, p.prediction, 13);
  text(ctx, "MARKOV BOUNDARY", boundaryX + 8, 28, p.ink, 11);
  text(ctx, "UNI GENERATIVE MODEL", boundaryX + 28, 58, p.belief, 13);

  const worldX = boundaryX * 0.48;
  const worldY = height * 0.46;
  ctx.strokeStyle = p.prediction; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(worldX, worldY, 58, 0, Math.PI * 2); ctx.stroke();
  text(ctx, "motor + cell", worldX, worldY - 5, p.ink, 11, "center");
  text(ctx, "hidden causes", worldX, worldY + 15, p.muted, 10, "center");
  arrow(ctx, worldX + 62, worldY - 35, boundaryX + 1, worldY - 35, p.signal, "observation oₜ");
  arrow(ctx, boundaryX - 1, worldY + 52, worldX + 62, worldY + 52, p.evidence, "action aₜ");

  const x = boundaryX + 45;
  const barW = Math.max(110, width - x - 95);
  probabilityBar(ctx, x, height * 0.24, barW, system.agent.priorAtUpdate[2] ?? 0, "prior q⁻(rising)", p.belief, p);
  probabilityBar(ctx, x, height * 0.39, barW, system.agent.likelihood[2] ?? 0, "likelihood p(o|rising)", p.evidence, p);
  probabilityBar(ctx, x, height * 0.54, barW, system.agent.posterior[2] ?? 0, "posterior q(rising|o)", p.signal, p);
  probabilityBar(ctx, x, height * 0.69, barW, system.agent.policyPosterior[0] ?? 0, "policy Q(RUN)", p.good, p);
  text(ctx, `committed prediction: ${system.agent.predictedLigandUm.toFixed(3)} µM`, x, height * 0.84, p.prediction, 11);
  const residual = system.observation.ligandUm - system.agent.predictedLigandUm;
  text(ctx, `later observation: ${system.observation.ligandUm.toFixed(3)} µM · residual ${residual >= 0 ? "+" : ""}${residual.toFixed(3)}`, x, height * 0.9, Math.abs(residual) > 0.05 ? p.danger : p.good, 11);
}

export function BiologicalStage({ camera, mode, replayFrame, running, system }: BiologicalStageProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const systemRef = useRef(system);
  const [videoTime, setVideoTime] = useState(0);
  const [videoRunning, setVideoRunning] = useState(false);
  const media = camera === "motor"
    ? { src: "/media/singh-2024-switching.mp4", poster: "/media/singh-2024-switching.webp", label: "Salmonella structural study", badge: "STRUCTURAL RECONSTRUCTION" }
    : { src: "/media/mears-2014-run-tumble.mp4", poster: "/media/mears-2014-run-tumble.webp", label: "E. coli fluorescent microscopy", badge: "OBSERVED" };
  const stageLabel = useMemo(() => {
    if (camera === "cell") return "E. coli cell and helical flagella in a ligand field with run or tumble trajectory";
    if (camera === "bundle") return "Close view of CCW bundled flagella or CW separated flagella";
    if (camera === "motor") return "Flagellar motor cutaway with membranes, rod, hook, rings, stators and proton flow";
    return "World process and UNI generative model separated by a Markov boundary with prior, likelihood, posterior, policy, prediction, action and residual";
  }, [camera]);

  useEffect(() => { systemRef.current = system; }, [system]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let frame = 0;
    let start = performance.now();
    const render = (now: number) => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const pixelWidth = Math.max(1, Math.round(rect.width * dpr));
      const pixelHeight = Math.max(1, Math.round(rect.height * dpr));
      if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) { canvas.width = pixelWidth; canvas.height = pixelHeight; }
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const width = rect.width; const height = rect.height; const p = paletteFrom(canvas);
      ctx.clearRect(0, 0, width, height); ctx.fillStyle = p.ground; ctx.fillRect(0, 0, width, height);
      const phase = reducedMotion || !running ? 0.8 : (now - start) / 1000;
      const latestSystem = systemRef.current;
      if (camera === "cell") drawCell(ctx, width, height, phase, latestSystem, p, false);
      if (camera === "bundle") drawCell(ctx, width, height, phase, latestSystem, p, true);
      if (camera === "motor") drawMotor(ctx, width, height, phase, latestSystem, mode, replayFrame, p);
      if (camera === "inference") drawInference(ctx, width, height, latestSystem, p);
      if (!reducedMotion && running) frame = requestAnimationFrame(render);
    };
    frame = requestAnimationFrame(render);
    const resize = () => { start = performance.now(); cancelAnimationFrame(frame); frame = requestAnimationFrame(render); };
    window.addEventListener("resize", resize);
    return () => { cancelAnimationFrame(frame); window.removeEventListener("resize", resize); };
  }, [camera, mode, replayFrame, running]);

  return (
    <section className="living-stage" aria-label="Synchronized observed and reconstructed biology">
      <div className="living-stage-head">
        <div>
          <p className="eyebrow">MULTISCALE BIOLOGICAL STAGE · {camera.toUpperCase()}</p>
          <h2>Observation beside reconstruction</h2>
        </div>
        <div className="runtime-readout" aria-live="polite">
          <span>{mode.replaceAll("_", " ")}</span>
          <strong>{mode === "OBSERVED_REPLAY" ? `${replayFrame.motorId} · ${replayFrame.eventId}` : `${system.observation.rotation} · ${Math.round(system.observation.motorSpeedRpm)} rpm`}</strong>
        </div>
      </div>
      <div className="dual-truth-stage">
        <figure className="observed-media">
          <div className="truth-badge observed">{media.badge}</div>
          <video
            controls loop muted playsInline preload="metadata" poster={media.poster} src={media.src}
            onPlay={() => setVideoRunning(true)} onPause={() => setVideoRunning(false)}
            onTimeUpdate={(event) => setVideoTime(event.currentTarget.currentTime)}
            aria-label={`${media.label}, locally pinned licensed source video`}
          >Your browser cannot play the locally pinned source video.</video>
          <figcaption>
            <strong>{media.label}</strong>
            <span>{camera === "motor" ? "Singh et al. 2024 · Salmonella · CC BY 4.0" : "Mears et al. 2014 · E. coli · CC BY 4.0"}</span>
            <span>{videoRunning ? "playing" : "paused"} · {videoTime.toFixed(1)} s · source pixels are not model output</span>
          </figcaption>
        </figure>
        <figure className="reconstruction-media">
          <div className={`truth-badge ${camera === "inference" ? "analogue" : "reconstruction"}`}>
            {camera === "inference" ? "UNI PHYSICAL ANALOGUE" : "STRUCTURAL RECONSTRUCTION"}
          </div>
          <canvas ref={canvasRef} role="img" aria-label={stageLabel} data-testid="biological-canvas" />
          <figcaption>
            <strong>{camera === "motor" ? "Cross-species constrained cutaway" : camera === "inference" ? "Declared inference mirror" : "Synchronized E. coli reconstruction"}</strong>
            <span>{camera === "motor" ? "Salmonella basal body + Bacillus MotA₅MotB₂ geometry remain labelled" : "Rendered on CPU with deterministic model state"}</span>
          </figcaption>
        </figure>
      </div>
      <div className="truth-legend" aria-label="Truth class legend">
        <span className="truth-badge observed">OBSERVED</span><span>source pixels or recorded fields</span>
        <span className="truth-badge reconstruction">STRUCTURAL RECONSTRUCTION</span><span>evidence-constrained anatomy</span>
        <span className="truth-badge model">REDUCED MODEL</span><span>declared calculation</span>
        <span className="truth-badge analogue">UNI PHYSICAL ANALOGUE</span><span>teaching mechanism, not bacterial anatomy</span>
      </div>
    </section>
  );
}
