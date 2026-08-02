import observedReport from "@/experiments/results/observed-experiment-report.json";

const report = observedReport;
const results = report.heldoutResults;
const models = report.fittedOnTrainingOnly.normalizedDurationModels;

const colors = {
  observed: "#70e2d5",
  exponential: "#ef8f78",
  weibull: "#8492cb",
  lognormal: "#87d7a1",
  mixture: "#e4ae63",
};

function pointsFor(
  rows: Array<Record<string, number>>,
  xKey: string,
  yKey: string,
  width: number,
  height: number,
  xMax: number,
) {
  const left = 48;
  const right = 14;
  const top = 16;
  const bottom = 34;
  return rows.map((row) => {
    const x = left + (row[xKey] / xMax) * (width - left - right);
    const y = top + (1 - row[yKey]) * (height - top - bottom);
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  }).join(" ");
}

function SurvivalPlot() {
  const width = 760;
  const height = 280;
  const rows = report.curves.survival;
  const xMax = rows.at(-1)?.normalizedTime ?? 1;
  const series = ["observed", "exponential", "weibull", "lognormal", "mixture"] as const;
  return (
    <figure className="observed-plot">
      <figcaption>
        <strong>Held-out survival prediction</strong>
        <span>fraction of dwell events still unchanged after normalized time</span>
      </figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="survival-title survival-description">
        <title id="survival-title">Observed and predicted dwell-event survival curves</title>
        <desc id="survival-description">Observed holdout survival is compared with exponential, Weibull, lognormal, and UNI two-timescale predictions fitted only on training motors.</desc>
        {[0, 0.25, 0.5, 0.75, 1].map((value) => {
          const y = 16 + (1 - value) * (height - 50);
          return <g key={value}><line x1="48" x2={width - 14} y1={y} y2={y} className="plot-grid" /><text x="41" y={y + 4} textAnchor="end">{value.toFixed(2)}</text></g>;
        })}
        {[0, 0.25, 0.5, 0.75, 1].map((fraction) => {
          const x = 48 + fraction * (width - 62);
          return <g key={fraction}><line x1={x} x2={x} y1="16" y2={height - 34} className="plot-grid" /><text x={x} y={height - 13} textAnchor="middle">{(xMax * fraction).toFixed(1)}</text></g>;
        })}
        {series.map((name) => (
          <polyline
            key={name}
            points={pointsFor(rows, "normalizedTime", name, width, height, xMax)}
            fill="none"
            stroke={colors[name]}
            strokeWidth={name === "observed" ? 3 : 2}
            strokeDasharray={name === "observed" ? undefined : name === "mixture" ? "8 4" : "3 4"}
          />
        ))}
        <text x="12" y="14">S(t)</text>
        <text x={width - 14} y={height - 13} textAnchor="end">duration / training mean for N</text>
      </svg>
      <div className="plot-legend" aria-label="Survival plot legend">
        {series.map((name) => <span key={name}><i style={{ background: colors[name] }} />{name === "mixture" ? "UNI two-timescale" : name}</span>)}
      </div>
    </figure>
  );
}

function PosteriorPlot() {
  const width = 760;
  const height = 230;
  const rows = report.curves.posteriorSlow;
  const xMax = rows.at(-1)?.normalizedTime ?? 1;
  return (
    <figure className="observed-plot posterior-plot">
      <figcaption>
        <strong>Prior → posterior while nothing happens</strong>
        <span>survival itself is evidence for the slower predictive timescale</span>
      </figcaption>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby="posterior-title posterior-description">
        <title id="posterior-title">Posterior probability of the slower latent timescale</title>
        <desc id="posterior-description">The frozen two-timescale model starts with its training-fitted prior and updates toward the slower timescale as a held-out dwell survives.</desc>
        {[0, 0.5, 1].map((value) => {
          const y = 16 + (1 - value) * (height - 50);
          return <g key={value}><line x1="48" x2={width - 14} y1={y} y2={y} className="plot-grid" /><text x="41" y={y + 4} textAnchor="end">{value.toFixed(1)}</text></g>;
        })}
        <polyline points={pointsFor(rows, "normalizedTime", "posteriorSlow", width, height, xMax)} fill="none" stroke={colors.mixture} strokeWidth="3" />
        <circle cx="48" cy={16 + (1 - rows[0].posteriorSlow) * (height - 50)} r="5" fill={colors.observed} />
        <circle cx={width - 14} cy={16 + (1 - rows.at(-1)!.posteriorSlow) * (height - 50)} r="5" fill={colors.mixture} />
        <text x="12" y="14">q(slow)</text>
        <text x={width - 14} y={height - 13} textAnchor="end">normalized elapsed dwell time</text>
      </svg>
      <code className="observed-equation">q(slow | T &gt; t) = (1−w)e<sup>−λslow·t</sup> / [w e<sup>−λfast·t</sup> + (1−w)e<sup>−λslow·t</sup>]</code>
      <p className="plot-reading">q(slow): {rows[0].posteriorSlow.toFixed(3)} prior → {rows.at(-1)!.posteriorSlow.toFixed(3)} after the held-out 90th-percentile survival time.</p>
    </figure>
  );
}

function CvPlot() {
  const maximum = Math.max(...results.stateSummary.map((row) => row.cvSquared), 5);
  return (
    <figure className="cv-plot">
      <figcaption><strong>Observed timing variability by stator count</strong><span>CV² = 1 is the memoryless prediction</span></figcaption>
      <div className="cv-bars" role="img" aria-label="Held-out squared coefficient of variation for stator states one through eight; every state is above the memoryless value of one">
        {results.stateSummary.map((row) => (
          <div key={row.stateN} className="cv-column">
            <div className="cv-track">
              <i className="cv-null" style={{ bottom: `${(1 / maximum) * 100}%` }} />
              <b style={{ height: `${(row.cvSquared / maximum) * 100}%` }}><span>{row.cvSquared.toFixed(2)}</span></b>
            </div>
            <span>N={row.stateN}</span>
          </div>
        ))}
      </div>
    </figure>
  );
}

const modelRows = [
  { id: "M0", name: "Memoryless exponential", score: results.meanLogScoreNatsPerEvent.exponential, note: "frozen null" },
  { id: "M1", name: `Weibull (shape ${models.weibull.shape.toFixed(3)})`, score: results.meanLogScoreNatsPerEvent.weibull, note: "flexible survival" },
  { id: "M2", name: `Lognormal (σ ${models.lognormal.sigma.toFixed(3)})`, score: results.meanLogScoreNatsPerEvent.lognormal, note: "best held-out score" },
  { id: "M3", name: "UNI two-timescale mixture", score: results.meanLogScoreNatsPerEvent.mixture, note: "beats M0; not M2" },
];

const claimLabels: Record<string, string> = {
  H1_OVERDISPERSION: "H1 · OVERDISPERSION",
  H2_HELDOUT_LOG_SCORE: "H2 · HELD-OUT LOG SCORE",
  H3_SURVIVAL_POSTERIOR: "H3 · SURVIVAL POSTERIOR",
  H4_DIRECTION: "H4 · DIRECTION",
};

const statusLabels: Record<string, string> = {
  SUPPORTED_WITHIN_PROTOCOL: "SUPPORTED · FROZEN PROTOCOL",
  MODEL_CONSEQUENCE_CONFIRMED: "DECLARED MODEL CONSEQUENCE",
  INCONCLUSIVE_POINT_ESTIMATE_ONLY: "INCONCLUSIVE · INTERVAL CROSSES ZERO",
  NOT_SUPPORTED: "NOT SUPPORTED",
};

type NumericClaim = {
  observed: number;
  interval95: { lower: number; upper: number } | null;
};

export function ObservedExperimentPanel() {
  const h1 = report.claims.find((claim) => claim.hypothesisId === "H1_OVERDISPERSION") as NumericClaim;
  const h2 = report.claims.find((claim) => claim.hypothesisId === "H2_HELDOUT_LOG_SCORE") as NumericClaim;
  const versusLognormal = results.pairedMixtureAdvantageNatsPerEvent.mixtureVsLognormal;
  return (
    <section className="panel-content observed-panel" data-testid="observed-panel">
      <div className="observed-header">
        <div className="section-heading"><span>06</span><div><strong>Observed motor experiment</strong><small>source-pinned · motor-level holdout · CPU-only</small></div></div>
        <div className="experiment-verdict">
          <span>RESULT</span>
          <strong>Real timing rejects the simple memoryless model. The UNI mixture predicts better than that null—but a lognormal predicts slightly better than UNI.</strong>
          <p>No biological Active Inference identity is claimed. The adverse comparison stays visible.</p>
          <code className="fitted-parameters">M3 frozen fit: w={models.mixture.weightFast.toFixed(3)} · λfast={models.mixture.rateFast.toFixed(3)} · λslow={models.mixture.rateSlow.toFixed(3)}</code>
        </div>
      </div>

      <dl className="experiment-counts">
        <div><dt>Source cohort</dt><dd>{report.cohort.sourceMotors} single motors</dd></div>
        <div><dt>Frozen fit</dt><dd>{report.cohort.trainMotors} motors · {report.cohort.trainEvents} events</dd></div>
        <div><dt>Untouched holdout</dt><dd>{report.cohort.holdoutMotors} motors · {report.cohort.holdoutEvents} events</dd></div>
        <div><dt>Observed states</dt><dd>N = {report.cohort.eligibleStates.join(", ")}</dd></div>
      </dl>

      <div className="observed-plots">
        <SurvivalPlot />
        <PosteriorPlot />
      </div>

      <div className="experiment-analysis-grid">
        <CvPlot />
        <div className="model-score-table">
          <h2>Held-out predictive log score</h2>
          <p>Higher is better. Every parameter and state scale came only from training motors.</p>
          <table>
            <thead><tr><th>Model</th><th>nats / event</th><th>Reading</th></tr></thead>
            <tbody>{modelRows.map((row) => <tr key={row.id}><td><code>{row.id}</code> {row.name}</td><td>{row.score.toFixed(3)}</td><td>{row.note}</td></tr>)}</tbody>
          </table>
          <dl className="comparison-readout">
            <div><dt>M3 − memoryless</dt><dd>+{h2.observed.toFixed(3)} [{h2.interval95!.lower.toFixed(3)}, {h2.interval95!.upper.toFixed(3)}]</dd></div>
            <div><dt>M3 − lognormal</dt><dd>{versusLognormal.toFixed(3)} [{results.pairedMixtureAdvantageInterval95.mixtureVsLognormal.lower.toFixed(3)}, {results.pairedMixtureAdvantageInterval95.mixtureVsLognormal.upper.toFixed(3)}]</dd></div>
            <div><dt>Mean held-out CV²</dt><dd>{h1.observed.toFixed(3)} [{h1.interval95!.lower.toFixed(3)}, {h1.interval95!.upper.toFixed(3)}]</dd></div>
          </dl>
        </div>
      </div>

      <div className="claim-ledger">
        <h2>What this run permits us to say</h2>
        {report.claims.map((claim) => (
          <article key={claim.hypothesisId}>
            <span className="evidence-status">{claimLabels[claim.hypothesisId]}</span>
            <b className="claim-status">{statusLabels[claim.status] ?? claim.status}</b>
            <p>{claim.claim}</p>
            <small>{claim.fence}</small>
          </article>
        ))}
      </div>

      <div className="audit-lineage">
        <div>
          <h2>Reproduce and audit</h2>
          <p>Raw observations → validated dwell events → motor-level split → training-only fit → frozen held-out score → cluster-bootstrap uncertainty.</p>
        </div>
        <dl>
          <div><dt>Protocol</dt><dd>{report.protocolId}</dd></div>
          <div><dt>Source commit</dt><dd>{report.identities.rawSourceCommit.slice(0, 12)}</dd></div>
          <div><dt>Raw SHA-256</dt><dd>{report.identities.rawSourceSha256.slice(0, 16)}…</dd></div>
          <div><dt>Run SHA-256</dt><dd>{report.runId.slice(0, 16)}…</dd></div>
        </dl>
        <div className="download-actions">
          <a className="primary-button audit-link" href="/observed-experiment-report.json" download>Download full result JSON</a>
          <a className="audit-link" href="/observed-experiment-preregistration.json" download>Frozen protocol JSON</a>
          <a className="audit-link" href="/observed-experiment-audit.json" download>Audit manifest JSON</a>
          <a className="audit-link" href="/wadhwa-2022-derived-events.json" download>Derived event data</a>
          <a className="audit-link" href="https://doi.org/10.1038/s41467-022-33075-5" target="_blank" rel="noreferrer">Primary paper</a>
          <a className="audit-link" href="https://github.com/navishwadhwa/multi-state-remodeling/tree/c83119131c3ce3742460a2e3b6bd6c6e44bef4d5" target="_blank" rel="noreferrer">Pinned source</a>
        </div>
      </div>
    </section>
  );
}
