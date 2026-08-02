"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  actionFromAgent,
  createAgent,
  createControls,
  createWorld,
  instrumentObservation,
  modelSnapshot,
  stepAgent,
  stepSyntheticSystem,
  type AgentState,
  type ActionState,
  type Controls,
  type Observation,
  type WorldState,
} from "@/lib/uni-motor.js";
import { createCadManifest, openScadFromManifest } from "@/lib/cad.js";
import { ObservedExperimentPanel } from "./observed-experiment-panel";
import { ScienceGatesPanel } from "./science-gates-panel";
import { CrossStudyParityPanel } from "./cross-study-parity-panel";
import { LivingScienceWalkthrough } from "./living-science-walkthrough";

type Panel = "loop" | "math" | "cad" | "observed" | "gates" | "cross" | "evidence";
type SourceMode = "synthetic" | "serial";
type SystemState = {
  world: WorldState;
  agent: AgentState;
  observation: Observation;
  action: ActionState;
};
type HistoryPoint = {
  t: number;
  observedLigand: number;
  predictedLigand: number;
  observedSpeed: number;
  predictedSpeed: number;
  source: string;
};

type SerialPortLike = {
  open(options: { baudRate: number }): Promise<void>;
  close(): Promise<void>;
  readable: ReadableStream<Uint8Array> | null;
};

const initialControls = createControls();
const initialWorld = createWorld();
const initialAgent = createAgent();
const initialObservation: Observation = {
  source: "SYNTHETIC_WORLD",
  deviceTimeMs: 0,
  receivedAtMs: 0,
  ligandUm: 1,
  receptorActivity: 0.34,
  motorSpeedRpm: 6200,
  rotation: "CCW",
  loadPnNm: 700,
  pmfMv: 150,
};

const initialSystem: SystemState = {
  world: initialWorld,
  agent: initialAgent,
  observation: initialObservation,
  action: actionFromAgent(initialAgent),
};

const partDetails: Record<string, { label: string; equation: string; truth: string; input: string; output: string }> = {
  "world-rotor": {
    label: "External bacterial motor",
    equation: "ΔGion → τΔθ + dissipation",
    truth: "World-process state. It is not copied into the UNI generative model.",
    input: "ion-motive force, external load, stator occupancy",
    output: "rotation, speed, torque and trajectory",
  },
  "signal-cam": {
    label: "Observation aperture",
    equation: "oₜ = sensor(worldₜ) + εₜ",
    truth: "The only inward crossing. A live serial frame is timestamped at receipt.",
    input: "ligand, motor speed, CW/CCW, load and PMF",
    output: "validated Observation record",
  },
  "prior-gear": {
    label: "Prior log-odds gear",
    equation: "θprior = κ ln[q⁻(rising)/q⁻(falling)]",
    truth: "The belief before the current observation is applied.",
    input: "previous posterior and selected transition model Bπ",
    output: "predictive prior q⁻(sₜ)",
  },
  "evidence-gear": {
    label: "Likelihood-ratio gear",
    equation: "θevidence = κ ln[p(o|rising)/p(o|falling)]",
    truth: "Measured signal evidence, not a hidden label from the world.",
    input: "change in observed ligand concentration",
    output: "likelihood over falling, flat and rising",
  },
  "posterior-gear": {
    label: "Posterior differential",
    equation: "ln Oposterior = ln Oprior + ln LR",
    truth: "Exact categorical Bayes update for this declared model.",
    input: "prior and likelihood",
    output: "q(sₜ|oₜ)",
  },
  "policy-gear": {
    label: "Expected-free-energy policy gear",
    equation: "Q(π) = softmax(−γG(π))",
    truth: "RUN and TUMBLE are compared with the same observations and horizon.",
    input: "posterior, preferences, outcome model and effort",
    output: "policy posterior and bounded action",
  },
  "prediction-gear": {
    label: "Prediction gear",
    equation: "q(oₜ₊₁|π) = Σₛ P(oₜ₊₁|sₜ₊₁)q(sₜ₊₁|π)",
    truth: "A falsifiable forecast kept separate from the next observation.",
    input: "posterior and transition/outcome models",
    output: "predicted ligand, speed, CW bias and stators",
  },
  "action-clutch": {
    label: "Bounded action aperture",
    equation: "aₜ ∈ {RUN, TUMBLE}",
    truth: "The only outward crossing. It changes the world process; it does not rewrite observations.",
    input: "selected policy",
    output: "timestamped action record",
  },
};

const evidenceRows = [
  {
    claim: "Load-dependent stator recruitment and mechanosensitive CheY-P affinity",
    status: "OBSERVED / MODELED",
    source: "Nature Communications 12, 6432 (2021)",
    href: "https://www.nature.com/articles/s41467-021-25774-2",
    fence: "Supports coupled mechanical and switching adaptation; does not establish Active Inference identity.",
  },
  {
    claim: "Multiple hidden bound states in motor mechano-adaptation",
    status: "OBSERVED / INFERRED",
    source: "Nature Communications 13, 5327 (2022)",
    href: "https://www.nature.com/articles/s41467-022-33075-5",
    fence: "The reduced stator equation here is pedagogical and not the paper's four-state fit.",
  },
  {
    claim: "Torque-speed behavior across ion motive force and stator number",
    status: "OBSERVED",
    source: "PNAS 115, 1190–1195 (2018)",
    href: "https://www.pnas.org/doi/10.1073/pnas.1708054114",
    fence: "The live curve is a transparent approximation, never a replacement for source data.",
  },
  {
    claim: "Mechanical, nonequilibrium origin of switch ultrasensitivity",
    status: "CURRENT MODEL",
    source: "Nature Physics 22, 131–138 (2026)",
    href: "https://www.nature.com/articles/s41567-025-03105-2",
    fence: "A competing mechanochemical account to test, not a settled molecular identity.",
  },
];

function downloadText(name: string, text: string, mime: string) {
  const blob = new Blob([text], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

function format(value: number | null | undefined, digits = 3) {
  if (value == null || !Number.isFinite(value)) return "not observed";
  return Number(value).toFixed(digits);
}

function logOddsAngle(value: number) {
  return Math.max(-2.8, Math.min(2.8, value || 0)) * 38;
}

function gearPath(ctx: CanvasRenderingContext2D, x: number, y: number, radius: number, teeth: number, angle: number) {
  ctx.beginPath();
  for (let i = 0; i < teeth * 4; i += 1) {
    const toothPhase = i % 4;
    const r = radius + (toothPhase === 1 || toothPhase === 2 ? radius * 0.12 : 0);
    const a = angle + (i / (teeth * 4)) * Math.PI * 2;
    const px = x + Math.cos(a) * r;
    const py = y + Math.sin(a) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
}

function drawGear(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  radius: number,
  teeth: number,
  angle: number,
  fill: string,
  label: string,
  selected: boolean,
) {
  ctx.save();
  ctx.shadowColor = selected ? "rgba(129, 230, 217, .82)" : "rgba(0,0,0,.35)";
  ctx.shadowBlur = selected ? 18 : 7;
  gearPath(ctx, x, y, radius, teeth, angle);
  ctx.fillStyle = fill;
  ctx.fill();
  ctx.strokeStyle = selected ? "#a7fff4" : "rgba(255,255,255,.42)";
  ctx.lineWidth = selected ? 3 : 1;
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(x, y, radius * 0.28, 0, Math.PI * 2);
  ctx.fillStyle = "#0b1116";
  ctx.fill();
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + Math.cos(angle) * radius * 0.75, y + Math.sin(angle) * radius * 0.75);
  ctx.strokeStyle = "rgba(255,255,255,.72)";
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.font = "500 11px ui-monospace, monospace";
  ctx.textAlign = "center";
  ctx.fillStyle = "rgba(231,241,239,.88)";
  ctx.fillText(label, x, y + radius + 21);
  ctx.restore();
}

function drawMotorCanvas(
  canvas: HTMLCanvasElement,
  system: SystemState,
  selectedPart: string,
  pulse: number,
) {
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(680, rect.width);
  const height = Math.max(480, rect.height);
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);

  const boundaryX = width * 0.36;
  const top = 32;
  const bottom = height - 36;

  // External world field.
  const field = ctx.createLinearGradient(0, 0, boundaryX, 0);
  field.addColorStop(0, "rgba(27, 166, 149, .08)");
  field.addColorStop(1, "rgba(27, 166, 149, .32)");
  ctx.fillStyle = field;
  ctx.fillRect(0, top, boundaryX - 7, bottom - top);
  ctx.strokeStyle = "rgba(97, 214, 195, .28)";
  for (let i = 0; i < 9; i += 1) {
    const fx = 18 + i * (boundaryX - 40) / 8;
    ctx.beginPath();
    ctx.arc(fx, 90 + ((i * 53) % Math.max(80, height - 180)), 3 + i * 0.5, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(124, 239, 217, ${0.18 + i * 0.035})`;
    ctx.fill();
  }
  ctx.fillStyle = "rgba(215,239,235,.9)";
  ctx.font = "500 12px ui-monospace, monospace";
  ctx.textAlign = "left";
  ctx.fillText("WORLD PROCESS · NOT INSIDE UNI", 18, 54);
  ctx.font = "400 10px ui-monospace, monospace";
  ctx.fillStyle = "rgba(178,204,201,.8)";
  ctx.fillText(`true gradient: ${system.world.trueGradient}`, 18, 72);

  // Biological motor: membrane, stators and rotor.
  const mx = boundaryX * 0.47;
  const my = height * 0.57;
  ctx.strokeStyle = "rgba(122,151,154,.62)";
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.moveTo(25, my - 76);
  ctx.lineTo(boundaryX - 25, my - 76);
  ctx.moveTo(25, my + 76);
  ctx.lineTo(boundaryX - 25, my + 76);
  ctx.stroke();
  const activeStators = Math.round(system.world.stators);
  for (let i = 0; i < 11; i += 1) {
    const angle = (i / 11) * Math.PI * 2;
    const sx = mx + Math.cos(angle) * 67;
    const sy = my + Math.sin(angle) * 67;
    ctx.fillStyle = i < activeStators ? "#d89c47" : "rgba(125,139,140,.24)";
    ctx.beginPath();
    ctx.roundRect(sx - 9, sy - 13, 18, 26, 5);
    ctx.fill();
  }
  drawGear(ctx, mx, my, 49, 34, system.world.rotorAngleRad, "#af6546", "BIOLOGICAL ROTOR", selectedPart === "world-rotor");
  ctx.strokeStyle = "rgba(218,156,71,.65)";
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(mx, my - 49);
  ctx.bezierCurveTo(mx - 22, my - 130, mx + 58, my - 155, mx + 34, my - 220);
  ctx.stroke();

  // Literal Markov boundary.
  ctx.fillStyle = "rgba(8,13,17,.92)";
  ctx.fillRect(boundaryX - 7, top, 14, bottom - top);
  ctx.strokeStyle = "#dbb368";
  ctx.lineWidth = 2;
  ctx.setLineDash([5, 5]);
  ctx.beginPath();
  ctx.moveTo(boundaryX, top);
  ctx.lineTo(boundaryX, bottom);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.save();
  ctx.translate(boundaryX + 17, height * 0.5);
  ctx.rotate(-Math.PI / 2);
  ctx.fillStyle = "rgba(239,204,137,.9)";
  ctx.font = "500 11px ui-monospace, monospace";
  ctx.textAlign = "center";
  ctx.fillText("MARKOV BOUNDARY", 0, 0);
  ctx.restore();

  const obsY = height * 0.28;
  const actY = height * 0.78;
  ctx.fillStyle = "#5fe0d0";
  ctx.fillRect(boundaryX - 10, obsY - 18, 20, 36);
  ctx.fillStyle = "#e1a95f";
  ctx.fillRect(boundaryX - 10, actY - 18, 20, 36);
  ctx.fillStyle = "rgba(229,242,239,.85)";
  ctx.font = "500 10px ui-monospace, monospace";
  ctx.textAlign = "center";
  ctx.fillText("OBSERVATION →", boundaryX, obsY - 25);
  ctx.fillText("← ACTION", boundaryX, actY + 33);

  // UNI interior and calculation gears.
  ctx.fillStyle = "rgba(50,61,86,.17)";
  ctx.fillRect(boundaryX + 8, top, width - boundaryX - 8, bottom - top);
  ctx.textAlign = "left";
  ctx.fillStyle = "rgba(215,221,242,.9)";
  ctx.font = "500 12px ui-monospace, monospace";
  ctx.fillText("UNI GENERATIVE MODEL · BELIEFS, NOT WORLD TRUTH", boundaryX + 34, 54);

  const signalX = boundaryX + 68;
  const priorX = boundaryX + 170;
  const postX = boundaryX + 310;
  const outputX = Math.min(width - 75, boundaryX + 465);
  const upperY = height * 0.31;
  const lowerY = height * 0.68;
  const postY = height * 0.5;
  const pulseX = boundaryX + ((pulse % 1) * (postX - boundaryX));
  ctx.strokeStyle = "rgba(95,224,208,.42)";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(boundaryX, obsY);
  ctx.lineTo(postX, obsY);
  ctx.stroke();
  ctx.fillStyle = "#8bfff0";
  ctx.beginPath();
  ctx.arc(pulseX, obsY, 5, 0, Math.PI * 2);
  ctx.fill();

  drawGear(ctx, signalX, upperY, 31, 18, pulse * 4, "#3c9f98", "SIGNAL", selectedPart === "signal-cam");
  drawGear(ctx, priorX, upperY, 42, 24, logOddsAngle(system.agent.priorLogOdds || 0) * Math.PI / 180, "#6574a8", "PRIOR", selectedPart === "prior-gear");
  drawGear(ctx, priorX, lowerY, 42, 24, logOddsAngle(system.agent.evidenceLogOdds || 0) * Math.PI / 180, "#8b5fa2", "LIKELIHOOD", selectedPart === "evidence-gear");
  drawGear(ctx, postX, postY, 58, 32, logOddsAngle(system.agent.posteriorLogOdds || 0) * Math.PI / 180, "#c17d4d", "POSTERIOR", selectedPart === "posterior-gear");
  drawGear(ctx, outputX, upperY, 36, 20, -system.agent.efe[0] * 2, "#a27844", "POLICY", selectedPart === "policy-gear");
  drawGear(ctx, outputX, lowerY, 36, 20, system.agent.predictedLigandUm * 2, "#498a96", "PREDICTION", selectedPart === "prediction-gear");

  // Action clutch line returning across the boundary.
  ctx.strokeStyle = "rgba(225,169,95,.66)";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(outputX, upperY + 40);
  ctx.bezierCurveTo(outputX - 25, actY, boundaryX + 90, actY, boundaryX, actY);
  ctx.stroke();
  const actionPulseX = outputX - ((pulse % 1) * (outputX - boundaryX));
  ctx.fillStyle = "#ffc477";
  ctx.beginPath();
  ctx.arc(actionPulseX, actY, selectedPart === "action-clutch" ? 8 : 5, 0, Math.PI * 2);
  ctx.fill();
}

function drawTraceCanvas(canvas: HTMLCanvasElement, history: HistoryPoint[]) {
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  const width = Math.max(500, rect.width);
  const height = Math.max(210, rect.height);
  if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
  }
  const ctx = canvas.getContext("2d");
  if (!ctx) return;
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  ctx.clearRect(0, 0, width, height);
  const pad = { l: 48, r: 18, t: 22, b: 32 };
  const plotW = width - pad.l - pad.r;
  const plotH = height - pad.t - pad.b;
  ctx.strokeStyle = "rgba(145,166,171,.22)";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const y = pad.t + (i / 4) * plotH;
    ctx.beginPath();
    ctx.moveTo(pad.l, y);
    ctx.lineTo(width - pad.r, y);
    ctx.stroke();
  }
  const points = history.length ? history : [{ t: 0, observedLigand: 1, predictedLigand: 1, observedSpeed: 6200, predictedSpeed: 6200, source: "SYNTHETIC_WORLD" }];
  const ligands = points.flatMap((p) => [p.observedLigand, p.predictedLigand]);
  const min = Math.min(...ligands) * 0.97;
  const max = Math.max(...ligands) * 1.03 + 1e-6;
  const drawLine = (key: "observedLigand" | "predictedLigand", color: string, dash: number[]) => {
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.setLineDash(dash);
    ctx.beginPath();
    points.forEach((point, index) => {
      const x = pad.l + (index / Math.max(1, points.length - 1)) * plotW;
      const y = pad.t + (1 - (point[key] - min) / Math.max(1e-6, max - min)) * plotH;
      if (index === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.setLineDash([]);
  };
  drawLine("observedLigand", "#70e2d5", []);
  drawLine("predictedLigand", "#e4ae63", [6, 4]);
  ctx.font = "400 11px ui-monospace, monospace";
  ctx.fillStyle = "rgba(206,223,221,.72)";
  ctx.textAlign = "right";
  ctx.fillText(max.toFixed(3), pad.l - 7, pad.t + 4);
  ctx.fillText(min.toFixed(3), pad.l - 7, pad.t + plotH);
  ctx.textAlign = "left";
  ctx.fillText("µM ligand", pad.l, height - 10);
  ctx.fillStyle = "#70e2d5";
  ctx.fillText("observed —", width - 192, 14);
  ctx.fillStyle = "#e4ae63";
  ctx.fillText("predicted – –", width - 102, 14);
}

function ProbabilityBars({ label, values }: { label: string; values: number[] }) {
  const classes = ["falling", "flat", "rising"];
  return (
    <div className="probability-row">
      <span>{label}</span>
      <div className="probability-track" aria-label={`${label}: ${values.map((v) => v.toFixed(3)).join(", ")}`}>
        {values.map((value, index) => (
          <i key={classes[index]} className={classes[index]} style={{ width: `${value * 100}%` }} />
        ))}
      </div>
      <code>{values.map((v) => v.toFixed(2)).join(" · ")}</code>
    </div>
  );
}

export function UniFlagellumLab() {
  const [system, setSystem] = useState<SystemState>(initialSystem);
  const [controls, setControls] = useState<Controls>(initialControls);
  const [running, setRunning] = useState(true);
  const [sourceMode, setSourceMode] = useState<SourceMode>("synthetic");
  const [serialStatus, setSerialStatus] = useState("No instrument connected");
  const [lastRawFrame, setLastRawFrame] = useState("—");
  const [selectedPart, setSelectedPart] = useState("posterior-gear");
  const [panel, setPanel] = useState<Panel>("loop");
  const [history, setHistory] = useState<HistoryPoint[]>([]);
  const [pulse, setPulse] = useState(0);
  const [clockMs, setClockMs] = useState(0);
  const [cadOptions, setCadOptions] = useState({ moduleMm: 2, thicknessMm: 6, clearanceMm: 0.28 });
  const systemRef = useRef(system);
  const controlsRef = useRef(controls);
  const sourceRef = useRef(sourceMode);
  const runningRef = useRef(running);
  const liveObservationRef = useRef<Observation | null>(null);
  const motorCanvasRef = useRef<HTMLCanvasElement>(null);
  const traceCanvasRef = useRef<HTMLCanvasElement>(null);
  const serialPortRef = useRef<SerialPortLike | null>(null);
  const serialReaderRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  useEffect(() => { systemRef.current = system; }, [system]);
  useEffect(() => { controlsRef.current = controls; }, [controls]);
  useEffect(() => { sourceRef.current = sourceMode; }, [sourceMode]);
  useEffect(() => { runningRef.current = running; }, [running]);

  useEffect(() => {
    let previous = performance.now();
    const timer = window.setInterval(() => {
      const now = performance.now();
      const epochNow = Date.now();
      setClockMs(epochNow);
      const dt = Math.min(0.1, Math.max(0.01, (now - previous) / 1000));
      previous = now;
      if (!runningRef.current) return;
      setPulse((value) => (value + dt * 0.55) % 1);
      const current = systemRef.current;
      let next: SystemState;
      if (sourceRef.current === "serial" && liveObservationRef.current) {
        const observation = liveObservationRef.current;
        const agent = stepAgent(current.agent, observation, dt);
        next = {
          world: current.world,
          agent,
          observation,
          action: actionFromAgent(agent),
        };
      } else {
        next = stepSyntheticSystem(current, controlsRef.current, dt, epochNow);
      }
      systemRef.current = next;
      setSystem(next);
      setHistory((items) => [
        ...items.slice(-179),
        {
          t: now,
          observedLigand: next.observation.ligandUm,
          predictedLigand: next.agent.predictedLigandUm,
          observedSpeed: next.observation.motorSpeedRpm,
          predictedSpeed: next.agent.predictedSpeedRpm,
          source: next.observation.source,
        },
      ]);
    }, 80);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (motorCanvasRef.current) drawMotorCanvas(motorCanvasRef.current, system, selectedPart, pulse);
    if (traceCanvasRef.current) drawTraceCanvas(traceCanvasRef.current, history);
  }, [system, selectedPart, pulse, history]);

  const reset = useCallback(() => {
    const resetSystem = { ...initialSystem, world: createWorld(), agent: createAgent() };
    systemRef.current = resetSystem;
    setSystem(resetSystem);
    setHistory([]);
  }, []);

  const connectSerial = useCallback(async () => {
    const serial = (navigator as Navigator & { serial?: { requestPort(): Promise<SerialPortLike> } }).serial;
    if (!serial) {
      setSerialStatus("Web Serial is unavailable in this browser. Use Chromium over localhost or a secure origin.");
      return;
    }
    try {
      const port = await serial.requestPort();
      await port.open({ baudRate: 115200 });
      serialPortRef.current = port;
      setSourceMode("serial");
      setSerialStatus("Live serial instrument · 115200 baud · awaiting frame");
      if (!port.readable) throw new Error("The selected port has no readable stream.");
      const reader = port.readable.getReader();
      serialReaderRef.current = reader;
      const decoder = new TextDecoder();
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split(/\r?\n/);
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.trim()) continue;
          setLastRawFrame(line.slice(0, 220));
          try {
            const observation = instrumentObservation(JSON.parse(line), Date.now());
            liveObservationRef.current = observation;
            setSerialStatus(`LIVE · frame ${observation.deviceTimeMs} ms · received ${new Date(observation.receivedAtMs).toLocaleTimeString()}`);
          } catch (error) {
            setSerialStatus(`Frame rejected · ${error instanceof Error ? error.message : "invalid input"}`);
          }
        }
      }
    } catch (error) {
      setSerialStatus(error instanceof Error ? error.message : "Serial connection failed");
      setSourceMode("synthetic");
    }
  }, []);

  const disconnectSerial = useCallback(async () => {
    try {
      await serialReaderRef.current?.cancel();
      serialReaderRef.current?.releaseLock();
      await serialPortRef.current?.close();
    } catch {
      // The port may already be closed; state is still returned to simulation.
    }
    serialReaderRef.current = null;
    serialPortRef.current = null;
    liveObservationRef.current = null;
    setSourceMode("synthetic");
    setSerialStatus("No instrument connected");
  }, []);

  const manifest = useMemo(() => createCadManifest(cadOptions), [cadOptions]);
  const selected = partDetails[selectedPart] ?? partDetails["posterior-gear"];
  const residual = system.observation.ligandUm - system.agent.predictedLigandUm;
  const receivedAge = system.observation.receivedAtMs ? Math.max(0, clockMs - system.observation.receivedAtMs) : 0;

  const selectCanvasPart = useCallback((event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = event.currentTarget;
    const rect = canvas.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width;
    const y = (event.clientY - rect.top) / rect.height;
    if (x < 0.28) setSelectedPart("world-rotor");
    else if (x < 0.46 && y < 0.5) setSelectedPart("signal-cam");
    else if (x < 0.62 && y < 0.5) setSelectedPart("prior-gear");
    else if (x < 0.62) setSelectedPart("evidence-gear");
    else if (x < 0.78) setSelectedPart("posterior-gear");
    else if (y < 0.5) setSelectedPart("policy-gear");
    else setSelectedPart("prediction-gear");
  }, []);

  return (
    <main className="lab-shell">
      <header className="site-header">
        <div>
          <p className="eyebrow">UNI VERUM · DIGITAL ORGAN 01</p>
          <h1>UNI–FLAGELLUM</h1>
          <p>From ion flux to navigation · every state, boundary, prior, prediction and residual exposed</p>
        </div>
        <div className="truth-strip" aria-label="System truth status">
          <span className={sourceMode === "serial" ? "status live" : "status synthetic"}>
            {sourceMode === "serial" ? "EXPERT ENGINE · LIVE INSTRUMENT" : "EXPERT ENGINE · SYNTHETIC WORLD"}
          </span>
          <span>CPU CANVAS2D</span>
          <span>WALKTHROUGH SOURCES LABELLED</span>
        </div>
      </header>

      <LivingScienceWalkthrough
        system={system}
        controls={controls}
        running={running}
        instrumentConnected={sourceMode === "serial"}
        onRunning={setRunning}
        onControls={setControls}
      />

      <section id="research-desk" className="research-desk" aria-labelledby="research-desk-title">
        <div className="research-desk-heading">
          <p className="eyebrow">EXPERT RESEARCH DESK · PRESERVED v0.2 MACHINERY</p>
          <h2 id="research-desk-title">Inspect every model, gate, report, and CAD analogue</h2>
        </div>

      <section className="command-bar" aria-label="Laboratory command bar">
        <button className="primary-button" type="button" onClick={() => setRunning((value) => !value)} data-testid="run-toggle">
          {running ? "Pause loop" : "Run loop"}
        </button>
        <button type="button" onClick={reset}>Reset evidence</button>
        {sourceMode === "serial" ? (
          <button type="button" onClick={disconnectSerial}>Disconnect instrument</button>
        ) : (
          <button type="button" onClick={connectSerial} data-testid="connect-serial">Connect real instrument</button>
        )}
        <div className="command-readout">
          <span>signal</span>
          <strong>{format(system.observation.ligandUm)} µM</strong>
          <span>prediction</span>
          <strong>{format(system.agent.predictedLigandUm)} µM</strong>
          <span>residual</span>
          <strong className={Math.abs(residual) > 0.05 ? "warn" : "good"}>{residual >= 0 ? "+" : ""}{format(residual)}</strong>
        </div>
      </section>

      <section className="laboratory-grid">
        <aside className="world-controls" aria-label="External world controls">
          <div className="section-heading">
            <span>01</span>
            <div><strong>World process</strong><small>external causes · never beliefs</small></div>
          </div>
          <label>
            <span>Base ligand <output>{controls.baseLigandUm.toFixed(2)} µM</output></span>
            <input type="range" min="0.05" max="4" step="0.05" value={controls.baseLigandUm} onChange={(e) => setControls({ ...controls, baseLigandUm: Number(e.target.value) })} />
          </label>
          <label>
            <span>Gradient <output>{controls.gradientPerMm.toFixed(2)} mm⁻¹</output></span>
            <input data-testid="gradient-control" type="range" min="-3" max="3" step="0.05" value={controls.gradientPerMm} onChange={(e) => setControls({ ...controls, gradientPerMm: Number(e.target.value) })} />
          </label>
          <label>
            <span>Mechanical load <output>{controls.loadPnNm.toFixed(0)} pN·nm</output></span>
            <input data-testid="load-control" type="range" min="40" max="1900" step="10" value={controls.loadPnNm} onChange={(e) => setControls({ ...controls, loadPnNm: Number(e.target.value) })} />
          </label>
          <label>
            <span>Ion-motive force <output>{controls.pmfMv.toFixed(0)} mV</output></span>
            <input type="range" min="40" max="210" step="1" value={controls.pmfMv} onChange={(e) => setControls({ ...controls, pmfMv: Number(e.target.value) })} />
          </label>
          <dl className="world-readout">
            <div><dt>Rotor</dt><dd>{system.observation.rotation} · {format(system.observation.motorSpeedRpm, 0)} rpm</dd></div>
            <div><dt>Torque</dt><dd>{format(system.world.torquePnNm, 0)} pN·nm</dd></div>
            <div><dt>Stators</dt><dd>{format(system.world.stators, 2)} / 11</dd></div>
            <div><dt>CheY-P</dt><dd>{format(system.world.cheYpUm, 2)} µM</dd></div>
          </dl>
          <p className="model-fence">In simulation these are world truth. In instrument mode, only fields present in the serial frame become observations.</p>
        </aside>

        <section className="motor-stage" aria-label="Physical and mathematical motor rendering">
          <canvas
            ref={motorCanvasRef}
            className="motor-canvas"
            onClick={selectCanvasPart}
            role="img"
            aria-label="External bacterial motor separated by a Markov boundary from UNI prior, likelihood, posterior, policy, and prediction gears"
            data-testid="motor-canvas"
          />
          <div className="stage-caption">
            <span>Observation age <strong>{receivedAge} ms</strong></span>
            <span>Action <strong>{system.action.policy}</strong></span>
            <span>q(rising) <strong>{system.agent.posterior[2].toFixed(3)}</strong></span>
            <span>F[q] <strong>{system.agent.vfe.toFixed(3)} nat</strong></span>
          </div>
        </section>

        <aside className="verum-inspector" aria-live="polite">
          <div className="section-heading">
            <span>02</span>
            <div><strong>Verum gear truth</strong><small>select any physical part</small></div>
          </div>
          <div className="part-buttons" aria-label="Physical model parts">
            {Object.entries(partDetails).map(([id, part]) => (
              <button key={id} type="button" aria-pressed={selectedPart === id} onClick={() => setSelectedPart(id)}>{part.label}</button>
            ))}
          </div>
          <article className="part-truth">
            <p className="eyebrow">{selectedPart.toUpperCase()}</p>
            <h2>{selected.label}</h2>
            <code>{selected.equation}</code>
            <p>{selected.truth}</p>
            <dl>
              <div><dt>Input</dt><dd>{selected.input}</dd></div>
              <div><dt>Output</dt><dd>{selected.output}</dd></div>
            </dl>
          </article>
        </aside>
      </section>

      <nav className="panel-tabs" aria-label="Laboratory views">
        {(["loop", "math", "cad", "observed", "gates", "cross", "evidence"] as Panel[]).map((name) => (
          <button key={name} type="button" aria-pressed={panel === name} onClick={() => setPanel(name)}>
            {name === "loop" ? "Live signal loop" : name === "math" ? "Math exposed" : name === "cad" ? "Physical UNI model" : name === "observed" ? "Observed experiment" : name === "gates" ? "Science gates" : name === "cross" ? "Cross-study parity" : "Evidence ledger"}
          </button>
        ))}
      </nav>

      {panel === "loop" && (
        <section className="panel-content loop-panel" data-testid="loop-panel">
          <div className="trace-wrap">
            <div className="section-heading"><span>03</span><div><strong>Observation against prediction</strong><small>the prediction is committed before the next signal arrives</small></div></div>
            <canvas ref={traceCanvasRef} className="trace-canvas" role="img" aria-label="Time series comparing observed and predicted ligand concentration" />
          </div>
          <div className="signal-ledger">
            <h2>Current boundary event</h2>
            <dl>
              <div><dt>Source</dt><dd>{system.observation.source}</dd></div>
              <div><dt>Device time</dt><dd>{system.observation.deviceTimeMs} ms</dd></div>
              <div><dt>Received</dt><dd>{system.observation.receivedAtMs ? new Date(system.observation.receivedAtMs).toISOString() : "not received"}</dd></div>
              <div><dt>Signal</dt><dd>{format(system.observation.ligandUm)} µM · {format(system.observation.motorSpeedRpm, 0)} rpm</dd></div>
              <div><dt>Physical inputs</dt><dd>prior {format(system.observation.priorAngleDeg, 1)}° · evidence {format(system.observation.evidenceAngleDeg, 1)}°</dd></div>
              <div><dt>Prediction error</dt><dd>{format(residual, 5)} µM</dd></div>
              <div><dt>Selected action</dt><dd>{system.action.policy} · p={format(system.action.probability)}</dd></div>
            </dl>
            <p className="serial-status">{serialStatus}</p>
            <code className="raw-frame">{lastRawFrame}</code>
          </div>
        </section>
      )}

      {panel === "math" && (
        <section className="panel-content math-panel" data-testid="math-panel">
          <div className="belief-stack">
            <div className="section-heading"><span>04</span><div><strong>Priors update in public</strong><small>falling · flat · rising</small></div></div>
            <ProbabilityBars label="q⁻ prior" values={system.agent.priorAtUpdate} />
            <ProbabilityBars label="likelihood" values={system.agent.likelihood} />
            <ProbabilityBars label="q posterior" values={system.agent.posterior} />
            <ProbabilityBars label="next prior" values={system.agent.predictivePrior} />
            <div className="log-odds-identity">
              <code>{format(system.agent.priorLogOdds)} + {format(system.agent.evidenceLogOdds)} = {format(system.agent.posteriorLogOdds)}</code>
              <span>ln prior odds + ln likelihood ratio = ln posterior odds</span>
            </div>
          </div>
          <div className="equation-stack">
            <article>
              <h2>Exact categorical update</h2>
              <code>q(sₜ) = η · p(oₜ|sₜ) · Σ Bπ(sₜ|sₜ₋₁)q(sₜ₋₁)</code>
              <p>q is the agent’s belief. It is never displayed as the world’s true gradient.</p>
            </article>
            <article>
              <h2>Variational free energy</h2>
              <code>F[q] = Σ q(s)[ln q(s) − ln p(o,s)] = KL[q||p(s|o)] − ln p(o)</code>
              <p>Current exact-update KL term: 0 by construction. F[q] = surprise = {format(system.agent.vfe)} nat for the declared categorical model.</p>
            </article>
            <article>
              <h2>Policy posterior</h2>
              <code>Q(π) = softmax(−γG(π)); G = risk + ambiguity − information gain + effort</code>
              <table>
                <thead><tr><th>π</th><th>risk</th><th>ambiguity</th><th>information</th><th>G</th><th>Q(π)</th></tr></thead>
                <tbody>
                  {(["RUN", "TUMBLE"] as const).map((policy, i) => (
                    <tr key={policy}><td>{policy}</td><td>{format(system.agent.risk[i])}</td><td>{format(system.agent.ambiguity[i])}</td><td>{format(system.agent.informationGain[i])}</td><td>{format(system.agent.efe[i])}</td><td>{format(system.agent.policyPosterior[i])}</td></tr>
                  ))}
                </tbody>
              </table>
            </article>
          </div>
          <aside className="free-energy-fence">
            <strong>Two free energies. Never silently merged.</strong>
            <p><b>Thermodynamic:</b> electrochemical ion potential becomes motor work and dissipation, measured in joules or multiples of kBT.</p>
            <p><b>Variational:</b> model evidence bound and belief consistency, measured here in natural-information units.</p>
          </aside>
        </section>
      )}

      {panel === "cad" && (
        <section className="panel-content cad-panel" data-testid="cad-panel">
          <div className="cad-controls">
            <div className="section-heading"><span>05</span><div><strong>Print the UNI model</strong><small>not the bacterial engine</small></div></div>
            <label><span>Gear module <output>{cadOptions.moduleMm.toFixed(1)} mm</output></span><input type="range" min="1.2" max="3" step="0.1" value={cadOptions.moduleMm} onChange={(e) => setCadOptions({ ...cadOptions, moduleMm: Number(e.target.value) })} /></label>
            <label><span>Part thickness <output>{cadOptions.thicknessMm.toFixed(1)} mm</output></span><input type="range" min="3" max="12" step="0.5" value={cadOptions.thicknessMm} onChange={(e) => setCadOptions({ ...cadOptions, thicknessMm: Number(e.target.value) })} /></label>
            <label><span>Fit clearance <output>{cadOptions.clearanceMm.toFixed(2)} mm</output></span><input type="range" min="0.12" max="0.6" step="0.02" value={cadOptions.clearanceMm} onChange={(e) => setCadOptions({ ...cadOptions, clearanceMm: Number(e.target.value) })} /></label>
            <div className="download-actions">
              <button className="primary-button" type="button" onClick={() => downloadText("uni-flagellum-model.scad", openScadFromManifest(manifest), "text/plain")}>Export OpenSCAD</button>
              <button type="button" onClick={() => downloadText("uni-flagellum-cad-manifest.json", JSON.stringify(manifest, null, 2), "application/json")}>Export CAD manifest</button>
              <button type="button" onClick={() => downloadText("uni-flagellum-verum-snapshot.json", JSON.stringify(modelSnapshot(system, controls), null, 2), "application/json")}>Export live Verum state</button>
            </div>
            <p className="model-fence">OpenSCAD export is a parametric conversion starting point. Slice, tolerance-test, mechanically validate and supervise classroom use before calling any part print-ready.</p>
          </div>
          <div className="parts-table-wrap">
            <table className="parts-table">
              <thead><tr><th>Part</th><th>Teeth</th><th>Pitch Ø</th><th>Outer Ø</th><th>Bore</th><th>Mathematical role</th></tr></thead>
              <tbody>{manifest.parts.map((part) => (
                <tr key={part.id}><td>{part.id}</td><td>{part.teeth}</td><td>{part.pitchDiameterMm.toFixed(1)} mm</td><td>{part.outerDiameterMm.toFixed(1)} mm</td><td>{part.boreMm.toFixed(1)} mm</td><td>{part.role}</td></tr>
              ))}</tbody>
            </table>
          </div>
          <div className="physical-principle">
            <h2>A mechanical Bayes identity</h2>
            <code>θposterior = θprior + θevidence</code>
            <p>Angles encode log-odds. Rotary encoders measure what a child turns; this screen performs the declared Bayesian calculation and reports mechanical backlash as measurement uncertainty.</p>
          </div>
        </section>
      )}

      {panel === "observed" && <ObservedExperimentPanel />}

      {panel === "gates" && <ScienceGatesPanel />}

      {panel === "cross" && <CrossStudyParityPanel />}

      {panel === "evidence" && (
        <section className="panel-content evidence-panel" data-testid="evidence-panel">
          <div className="section-heading"><span>07</span><div><strong>Claim and evidence ledger</strong><small>every limit remains visible</small></div></div>
          <div className="evidence-table-wrap">
            <table>
              <thead><tr><th>Claim</th><th>Status</th><th>Primary source</th><th>Fence</th></tr></thead>
              <tbody>{evidenceRows.map((row) => (
                <tr key={row.claim}><td>{row.claim}</td><td><span className="evidence-status">{row.status}</span></td><td><a href={row.href} target="_blank" rel="noreferrer">{row.source}</a></td><td>{row.fence}</td></tr>
              ))}</tbody>
            </table>
          </div>
          <div className="nonclaims">
            <h2>What this release does not claim</h2>
            <ul>
              <li>The bacterium literally carries a probabilistic gear computer.</li>
              <li>Variational free energy is identical to proton-motive thermodynamic free energy.</li>
              <li>The reduced world process replaces molecular simulations or observed source data.</li>
              <li>A fitted trajectory proves that biology implements this internal representation.</li>
              <li>The printed mechanism is a structural or functional bacterial motor replica.</li>
            </ul>
          </div>
        </section>
      )}

      </section>

      <footer>
        <p><strong>UNI-FLAGELLUM v0.3</strong> · Living science walkthrough · transparent CPU reference lab · source-pinned observed experiment · synthetic observations are labelled · live frames are timestamped · model and world remain separate</p>
      </footer>
    </main>
  );
}
