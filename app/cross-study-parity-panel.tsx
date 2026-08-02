import crossStudyReport from "@/experiments/results/cross-study-parity-report.json";
import evidenceCorpus from "@/experiments/data/cross-study-motor-evidence.json";

const report = crossStudyReport;
const corpus = evidenceCorpus;
const gateById = Object.fromEntries(report.gates.map((gate) => [gate.id, gate]));

type RotationEvidence = {
  parameters: {
    stallInterceptPerSecond: number;
    positiveSpeedSlopePerHz: number;
    negativeSpeedMagnitudeSlopePerHz: number;
  };
  relativeRmseImprovement: number;
};

type LatticeEvidence = {
  J: number;
  deltaAicInFavorOfCooperativity: number;
  momentFits: { unweighted: { J: number } };
  crossStatisticJDisagreement: { absoluteDifference: number };
};

type GmcEvidence = {
  engagedMarginalL1: number;
  maximumColumnSumError: number;
};

type PropulsionEvidence = {
  motorSpeed: { meanHz: number; slope95: { lower: number; upper: number } };
  rftCellSpeed: { rmseUmPerSecond: number; relativeImprovement: number };
};

const rotation = gateById.X03_ROTATION_GATED_ASSEMBLY.evidence as RotationEvidence;
const lattice = gateById.X06_FINITE_LATTICE_COOPERATIVITY.evidence as LatticeEvidence;
const gmc = gateById.X07_GMC_GENERATOR_REPRODUCTION.evidence as GmcEvidence;
const propulsion = gateById.X09_WHOLE_CELL_PROPULSION.evidence as PropulsionEvidence;
const assemblyBins = corpus.studies.ito2021.rotationBindingBins["20Hz"];

const statusMeaning: Record<string, string> = {
  PASS: "criterion met",
  FAIL: "falsifier retained",
  NOT_ESTABLISHED: "claim unsupported",
  BLOCKED_EXTERNAL: "physical work required",
};

const modelLayers = [
  { id: "DLT", scale: "single-motor dwell", equation: "S_N(t) = sum_j a_j exp[-(k+_N + k-_j)t]", signal: "duration, direction, censoring" },
  { id: "ROTATION", scale: "stator assembly", equation: "b(w) = b0 + a+ max(w,0) + a- max(-w,0)", signal: "speed-bin binding rate" },
  { id: "LATTICE13", scale: "occupancy ensemble", equation: "P(phi) proportional to exp[J sum phi_i phi_(i+1) + mu sum phi_i]", signal: "P(N | bead/load class)" },
  { id: "GMC", scale: "motor switching", equation: "dq/dt = A(torque, speed, engagement) q", signal: "CW/CCW intervals and rates" },
  { id: "RFT", scale: "whole swimming cell", equation: "F_body + sum F_flagella = 0; T_body + sum T_flagella = 0", signal: "motor Hz, flagella count, cell speed" },
];

function fmt(value: number, digits = 3) {
  return Number(value).toFixed(digits);
}

function xScale(speed: number) {
  return 62 + ((speed + 100) / 200) * 696;
}

function yScale(rate: number) {
  return 188 - (rate / 2.7) * 155;
}

function modelRate(speed: number) {
  const parameters = rotation.parameters;
  return parameters.stallInterceptPerSecond
    + parameters.positiveSpeedSlopePerHz * Math.max(speed, 0)
    + parameters.negativeSpeedMagnitudeSlopePerHz * Math.max(-speed, 0);
}

export function CrossStudyParityPanel() {
  const modelPath = Array.from({ length: 101 }, (_, index) => -100 + index * 2)
    .map((speed, index) => `${index ? "L" : "M"}${xScale(speed)},${yScale(modelRate(speed))}`)
    .join(" ");
  const jX = (value: number) => 90 + (value / 1.5) * 650;

  return (
    <section className="panel-content cross-study-panel" data-testid="cross-study-parity-panel">
      <header className="cross-verdict">
        <div>
          <span>CROSS-STUDY PARITY VERDICT</span>
          <strong>More biology is expressed. Full parity remains false.</strong>
          <p>{report.summary.statusCounts.PASS} of 16 gates pass across {report.summary.attributedStudies} attributed studies and a conservative lower bound of {report.summary.directIndependentMotorCellLowerBound} independent motors or cells.</p>
        </div>
        <dl>
          <div><dt>direct artifacts</dt><dd>{report.summary.directPrimaryArtifactFamilies}</dd></div>
          <div><dt>raw Ito samples</dt><dd>{(corpus.studies.ito2021.rotationSampleCount + corpus.studies.ito2021.statorSampleCount).toLocaleString()}</dd></div>
          <div><dt>status</dt><dd>PARTIAL</dd></div>
        </dl>
      </header>

      <div className="cross-model-flow" aria-label="Evidence is transformed by assay-specific mathematical models">
        <span>observed signal</span><b>assay observation operator</b><i aria-hidden="true">-&gt;</i><b>mechanistic module</b><i aria-hidden="true">-&gt;</i><b>prediction + residual</b><i aria-hidden="true">-&gt;</i><span>gate + claim fence</span>
      </div>

      <div className="cross-model-grid">
        {modelLayers.map((layer) => (
          <article key={layer.id}>
            <span>{layer.id} / {layer.scale}</span>
            <code>{layer.equation}</code>
            <small>observes: {layer.signal}</small>
          </article>
        ))}
      </div>

      <div className="cross-plots">
        <figure>
          <figcaption><strong>Rotation-gated stator binding</strong><span>Ito 2021 / 20 Hz bins / source workbook</span></figcaption>
          <svg viewBox="0 0 820 220" role="img" aria-labelledby="rotation-title rotation-desc">
            <title id="rotation-title">Stator binding rate versus signed motor speed</title>
            <desc id="rotation-desc">Binding is low at stall and higher for both assisting and hindering rotation. Points include reported standard error bars; the line is the preregistered directional piecewise model.</desc>
            {[0, 1, 2].map((tick) => <g key={tick}><line className="plot-grid" x1="62" x2="758" y1={yScale(tick)} y2={yScale(tick)} /><text x="52" y={yScale(tick) + 4} textAnchor="end">{tick}</text></g>)}
            {[-100, -50, 0, 50, 100].map((tick) => <g key={tick}><line className="plot-grid" x1={xScale(tick)} x2={xScale(tick)} y1="28" y2="188" /><text x={xScale(tick)} y="207" textAnchor="middle">{tick}</text></g>)}
            <path className="cross-model-line" d={modelPath} />
            {assemblyBins.map((row) => {
              const rate = row.bindingRatePerSecond;
              const error = row.bindingRateSe;
              if (rate == null || error == null) return null;
              return <g key={`${row.leftHz}-${row.rightHz}`}>
                <line className="cross-error-bar" x1={xScale(row.meanSpeedHz)} x2={xScale(row.meanSpeedHz)} y1={yScale(rate - error)} y2={yScale(rate + error)} />
                <circle className="cross-observed-point" cx={xScale(row.meanSpeedHz)} cy={yScale(rate)} r="4" />
              </g>;
            })}
            <text x="410" y="218" textAnchor="middle">signed rotation speed (Hz)</text>
            <text x="13" y="108" transform="rotate(-90 13 108)" textAnchor="middle">binding rate (s^-1)</text>
          </svg>
          <p>Leave-one-bin-out RMSE improves {fmt(rotation.relativeRmseImprovement * 100, 1)}% over a constant-rate baseline. Both signed-speed slopes are positive.</p>
        </figure>

        <figure>
          <figcaption><strong>One lattice, incompatible J estimates</strong><span>same L=13 equation / different published summaries</span></figcaption>
          <svg viewBox="0 0 820 220" role="img" aria-labelledby="j-title j-desc">
            <title id="j-title">Interaction parameter disagreement</title>
            <desc id="j-desc">The published moment analysis and its independent reproduction give J near 1.2, while the full occupancy distributions give J near 0.21 and do not improve AIC over no cooperativity.</desc>
            <line className="j-axis" x1="90" x2="740" y1="120" y2="120" />
            {[0, 0.5, 1, 1.5].map((tick) => <g key={tick}><line className="j-tick" x1={jX(tick)} x2={jX(tick)} y1="114" y2="126" /><text x={jX(tick)} y="145" textAnchor="middle">{tick.toFixed(1)}</text></g>)}
            <g><circle className="j-distribution" cx={jX(lattice.J)} cy="120" r="8" /><text x={jX(lattice.J)} y="91" textAnchor="middle">full P(N): J={fmt(lattice.J)}</text></g>
            <g><path className="j-moment" d={`M${jX(lattice.momentFits.unweighted.J)},108 l10,20 h-20 z`} /><text x={jX(lattice.momentFits.unweighted.J)} y="174" textAnchor="middle">moments: J={fmt(lattice.momentFits.unweighted.J)}</text></g>
            <g><line className="j-published" x1={jX(1.21)} x2={jX(1.21)} y1="55" y2="105" /><text x={jX(1.21)} y="43" textAnchor="middle">published 1.21 +/- 0.22</text></g>
          </svg>
          <p>The full-distribution fit differs by {fmt(lattice.crossStatisticJDisagreement.absoluteDifference)} and has Delta AIC {fmt(lattice.deltaAicInFavorOfCooperativity)} versus J=0. This gate fails.</p>
        </figure>
      </div>

      <div className="cross-evidence-readout">
        <article><span>GMC generator</span><strong>L1={fmt(gmc.engagedMarginalL1, 4)}</strong><small>column error {gmc.maximumColumnSumError.toExponential(2)}</small></article>
        <article><span>whole-cell RFT</span><strong>RMSE={fmt(propulsion.rftCellSpeed.rmseUmPerSecond)} um/s</strong><small>{fmt(propulsion.rftCellSpeed.relativeImprovement * 100, 1)}% over mean baseline</small></article>
        <article><span>motor speed</span><strong>{fmt(propulsion.motorSpeed.meanHz, 1)} Hz</strong><small>slope 95% [{fmt(propulsion.motorSpeed.slope95.lower)}, {fmt(propulsion.motorSpeed.slope95.upper)}]</small></article>
      </div>

      <div className="cross-gate-flow" role="list" aria-label="Cross-study parity gates">
        {report.gates.map((gate) => (
          <article key={gate.id} role="listitem" data-status={gate.status}>
            <span>{gate.id}</span><strong>{gate.title}</strong><b>{gate.status.replaceAll("_", " ")}</b><small>{statusMeaning[gate.status]}</small>
          </article>
        ))}
      </div>

      <div className="gate-ledger-wrap">
        <table className="gate-ledger">
          <thead><tr><th>Gate</th><th>Status</th><th>Objective criterion</th><th>Limitation retained</th></tr></thead>
          <tbody>{report.gates.map((gate) => (
            <tr key={gate.id}>
              <td><code>{gate.id}</code><strong>{gate.title}</strong></td>
              <td><span data-status={gate.status}>{gate.status.replaceAll("_", " ")}</span></td>
              <td>{gate.criterion}</td>
              <td>{gate.limitation}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>

      <footer className="science-audit-footer">
        <div><strong>The organism-shaped plan changes when evidence disagrees.</strong><p>The next valid moves are commensurate cross-lab transfer, molecular identification of dwell states, conflict-free structural geometry, a discriminating causal intervention, a calibrated live run, independent wet-lab replication, and fabricated-model validation.</p></div>
        <div className="download-actions">
          <a className="audit-link" href="/cross-study-parity-report.json" download>Parity report</a>
          <a className="audit-link" href="/cross-study-parity-audit.json" download>Audit manifest</a>
          <a className="audit-link" href="/cross-study-motor-evidence.json" download>Evidence corpus</a>
          <a className="audit-link" href="/ito-raw-archive-verification.json" download>4.09 GB source verification</a>
        </div>
      </footer>
    </section>
  );
}
