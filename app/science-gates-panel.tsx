import scienceReport from "@/experiments/results/science-gates-report.json";

const report = scienceReport;
const gates = report.gates;
const fitted = report.fittedMechanism;
const sourceGate = gates.find((gate) => gate.id === "G03_PUBLIC_ARTIFACT_PARITY")!;
const predictiveGate = gates.find((gate) => gate.id === "G06_HELDOUT_MECHANISTIC_PREDICTION")!;
const recoveryGate = gates.find((gate) => gate.id === "G05_SYNTHETIC_RECOVERY")!;

const statusMeaning: Record<string, string> = {
  PASS: "criterion met",
  FAIL: "criterion not met",
  BLOCKED_EXTERNAL: "new external work required",
  NOT_ESTABLISHED: "claim is not supported",
  SOURCE_ONLY: "reported by source; not independently reconstructed",
};

function format(value: number, digits = 3) {
  return Number(value).toFixed(digits);
}

export function ScienceGatesPanel() {
  const predictive = predictiveGate.evidence as {
    advantageNatsPerInterval: number;
    advantageInterval95: { lower: number; upper: number };
  };
  const source = sourceGate.evidence as {
    momentMismatch: {
      maxRelativeMeanError: number;
      maxAbsoluteFractionPlusError: number;
      maxAbsoluteNormalizedVarianceError: number;
    };
    parameterIntervalChecks: Record<string, boolean>;
    n0Contradiction: string;
  };
  const recovery = recoveryGate.evidence as { passedReplicates: number; totalReplicates: number };

  return (
    <section className="panel-content science-gates-panel" data-testid="science-gates-panel">
      <header className="science-verdict">
        <div>
          <span>PARITY VERDICT</span>
          <strong>Full parity is not achieved.</strong>
          <p>{report.summary.computationalGatesPassed} of {report.summary.computationalGatesEvaluated} executable computational gates passed. Five biological or physical gates require new external work.</p>
        </div>
        <dl>
          {Object.entries(report.summary.statusCounts).map(([status, count]) => (
            <div key={status}><dt>{status.replaceAll("_", " ")}</dt><dd>{count}</dd></div>
          ))}
        </dl>
      </header>

      <div className="gate-flow" role="list" aria-label="Ordered scientific parity gates">
        {gates.map((gate) => (
          <article key={gate.id} role="listitem" data-status={gate.status}>
            <span>{gate.id.slice(0, 3)}</span>
            <strong>{gate.name}</strong>
            <b>{gate.status.replaceAll("_", " ")}</b>
            <small>{statusMeaning[gate.status]}</small>
          </article>
        ))}
      </div>

      <div className="mechanism-parity">
        <article>
          <div className="section-heading"><span>08</span><div><strong>Mechanism now implemented</strong><small>source first-passage form · censored competing risks</small></div></div>
          <code>S<sub>N</sub>(t) = Σ<sub>j</sub> a<sub>j</sub> exp(−[k<sub>+</sub>(N) + Nσ<sub>−</sub> + j(σ<sub>+</sub>−σ<sub>−</sub>)]t)</code>
          <code>P<sub>+</sub>(t|N)=k<sub>+</sub>(N)S<sub>N</sub>(t) · P<sub>−</sub>(t|N)=−dS/dt−P<sub>+</sub>(t|N)</code>
          <code>right-censored at c: ℒ=S<sub>N</sub>(c)</code>
          <p>The fitted model corresponds to the paper&apos;s D–L–T first-passage reduction. H is not hidden inside this likelihood: the source separates that state by a short-timescale classifier.</p>
        </article>
        <dl className="kinetic-parameters">
          <div><dt>σ<sub>+</sub></dt><dd>{format(fitted.sigmaPlusPerSecond, 5)} s⁻¹</dd></div>
          <div><dt>σ<sub>−</sub></dt><dd>{format(fitted.sigmaMinusPerSecond, 6)} s⁻¹</dd></div>
          <div><dt>c₁</dt><dd>{format(fitted.c1, 5)}</dd></div>
          <div><dt>c₂</dt><dd>{format(fitted.c2, 6)}</dd></div>
          <div><dt>c₃</dt><dd>{fitted.c3.toExponential(3)}</dd></div>
          <div><dt>recovery</dt><dd>{recovery.passedReplicates}/{recovery.totalReplicates} runs</dd></div>
        </dl>
      </div>

      <div className="failed-gate-analysis">
        <article>
          <span className="gate-id">G03 · PUBLIC ARTIFACT PARITY · FAIL</span>
          <h2>The public artifacts disagree</h2>
          <p>The bundled parameter vector does not regenerate the article&apos;s own Figure 3 theory arrays. Its largest relative mean-dwell error is {format(source.momentMismatch.maxRelativeMeanError * 100, 1)}%, and c₁/c₂ fall outside the article&apos;s stated 50%-loss ranges.</p>
          <p className="gate-fence">{source.n0Contradiction}</p>
        </article>
        <article>
          <span className="gate-id">G05 · PARAMETER RECOVERY · FAIL</span>
          <h2>One recovery run failed</h2>
          <p>Two of three deterministic synthetic experiments recovered every parameter within the frozen tolerances. The third missed c₂. The fitted c₂ and c₃ also collapsed toward zero, so three arrival-age coefficients are not practically identified by this split and likelihood.</p>
          <p className="gate-fence">Self-recovery tests implementation identifiability only; it cannot establish molecular identity.</p>
        </article>
        <article>
          <span className="gate-id">G06 · HELD-OUT PREDICTION · FAIL</span>
          <h2>Promising point estimate, uncertain motors</h2>
          <p>The D–L–T model improved held-out joint log score by {format(predictive.advantageNatsPerInterval, 4)} nat per interval, but the motor-cluster 95% interval [{format(predictive.advantageInterval95.lower, 4)}, {format(predictive.advantageInterval95.upper, 4)}] crosses zero.</p>
          <p className="gate-fence">The mechanistic model has not beaten the memoryless competing-risk baseline under the frozen uncertainty criterion.</p>
        </article>
      </div>

      <div className="gate-ledger-wrap">
        <table className="gate-ledger">
          <thead><tr><th>Gate</th><th>Status</th><th>Objective criterion</th><th>Limitation that remains</th></tr></thead>
          <tbody>{gates.map((gate) => (
            <tr key={gate.id}>
              <td><code>{gate.id}</code><strong>{gate.name}</strong></td>
              <td><span data-status={gate.status}>{gate.status.replaceAll("_", " ")}</span></td>
              <td>{gate.criterion}</td>
              <td>{gate.limitation}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>

      <footer className="science-audit-footer">
        <div>
          <strong>Next work is defined by the failed and blocked gates.</strong>
          <p>Resolve the source artifact mismatch; independently specify H-well detection; acquire motor-identified multi-load records; run a prospective live instrument protocol; then obtain independent wet-lab and physical-print replication.</p>
        </div>
        <div className="download-actions">
          <a className="audit-link" href="/science-gates-report.json" download>Science gate JSON</a>
          <a className="audit-link" href="/science-gates-audit.json" download>Audit manifest</a>
          <a className="audit-link" href="/observed-experiment-report.json" download>Observed report</a>
        </div>
      </footer>
    </section>
  );
}
