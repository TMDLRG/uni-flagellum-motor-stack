#!/usr/bin/env node
// extract_timescales.cjs - freezes every measured timescale/rate/frequency the estate holds
// into docs/classroom-assets/timescales.v1.json, values read PROGRAMMATICALLY from the
// artifacts (correct by construction), provenance carried as file + JSON path (machine-
// checkable and rewrite-stable, unlike line numbers). Deterministic; no timestamps.
//
// Epistemics vocabulary (every row carries one):
//   MEASURED                   - reported measurement from the attributed study
//   DIGITIZED_BY_THIRD_PARTY   - values digitized from a figure by another study's authors
//   MODEL_PREDICTION           - a source model's output, not an observation
//   REDUCED_MODEL              - a hand-set constant in this repo's teaching model, UNSOURCED
//   REPORTED_SUMMARY           - a source's summary statistic held without re-extraction
//   NOT_HELD                   - an explicit negative: the study holds no timescale here
'use strict';
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const rj = p => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const rows = [];
const R = (o) => rows.push(o);
const rng = a => ({ min: Math.min(...a), max: Math.max(...a), n: a.length });

// ---------------- cross-study corpus ----------------
const XS = 'experiments/data/cross-study-motor-evidence.json';
const xs = rj(XS);
const st = xs.studies;

// Antani 2021 - the only measured switching rates whose keys carry an explicit unit
const tsw = st.antani2021.torqueSwitching;
R({ group: 'switching', quantity: 'CCW->CW switching rate vs torque', values: tsw.map(r => r.kCcwToCwPerSecond),
  pairedTorquePnNm: tsw.map(r => r.torquePnNm), unitsAsHeld: 's^-1', species: 'Escherichia coli',
  sourceId: 'ANTANI_2021', doi: '10.1038/s41467-021-25774-2', epistemics: 'MEASURED',
  file: XS, jsonPath: 'studies.antani2021.torqueSwitching[].kCcwToCwPerSecond' });
R({ group: 'switching', quantity: 'CW->CCW switching rate vs torque', values: tsw.map(r => r.kCwToCcwPerSecond),
  pairedTorquePnNm: tsw.map(r => r.torquePnNm), unitsAsHeld: 's^-1', species: 'Escherichia coli',
  sourceId: 'ANTANI_2021', doi: '10.1038/s41467-021-25774-2', epistemics: 'MEASURED',
  file: XS, jsonPath: 'studies.antani2021.torqueSwitching[].kCwToCcwPerSecond' });
for (const cls of ['high', 'medium', 'low']) {
  const arr = st.antani2021.statorClassSpeedHz[cls];
  R({ group: 'rotation', quantity: 'motor speed, ' + cls + '-stator class', range: rng(arr),
    unitsAsHeld: 'Hz', species: 'Escherichia coli', sourceId: 'ANTANI_2021',
    doi: '10.1038/s41467-021-25774-2', epistemics: 'MEASURED',
    file: XS, jsonPath: 'studies.antani2021.statorClassSpeedHz.' + cls });
}
const dla = st.antani2021.dynamicLoadAdaptation;
R({ group: 'adaptation', quantity: 'dynamic load adaptation time axis (paired to mean CW bias)',
  range: rng(dla.map(r => r.timeSeconds)), unitsAsHeld: 's', species: 'Escherichia coli',
  sourceId: 'ANTANI_2021', doi: '10.1038/s41467-021-25774-2', epistemics: 'MEASURED',
  file: XS, jsonPath: 'studies.antani2021.dynamicLoadAdaptation[].timeSeconds' });

// Ito 2021
const itoMain = st.ito2021.dwellMeans.main;
R({ group: 'stator-dwell', quantity: 'per-state dwell means (states ' + itoMain.map(r => r.stateN).join(',') + ')',
  values: itoMain.map(r => r.meanDwellSeconds), se: itoMain.map(r => r.standardErrorSeconds),
  unitsAsHeld: 's', species: 'Escherichia coli', sourceId: 'ITO_2021', doi: '10.1038/s41467-021-23516-y',
  epistemics: 'MEASURED', file: XS, jsonPath: 'studies.ito2021.dwellMeans.main[].meanDwellSeconds',
  caveat: 'OPEN QUESTION, unreconciled: Ito dwell means FALL with N while Wadhwa 2022 dwell means RISE with N. The repo holds Ito sheet name but not the figure caption; whether these are the same observable is NOT established here.' });
const itoRot = st.ito2021.motors.map(m => m.rotationHz.mean);
R({ group: 'rotation', quantity: 'per-motor mean rotation rate (40 motors)', range: rng(itoRot),
  unitsAsHeld: 'Hz', species: 'Escherichia coli', sourceId: 'ITO_2021', doi: '10.1038/s41467-021-23516-y',
  epistemics: 'MEASURED', file: XS, jsonPath: 'studies.ito2021.motors[].rotationHz.mean' });
for (const bw of Object.keys(st.ito2021.rotationBindingBins)) {
  const binsRaw = st.ito2021.rotationBindingBins[bw];
  const bins = Array.isArray(binsRaw) ? binsRaw : binsRaw.bins;
  R({ group: 'stator-binding', quantity: 'stator binding rate vs rotation speed (' + bw + ' bins, n=' + bins.length + ')',
    range: rng(bins.map(b => b.bindingRatePerSecond)), unitsAsHeld: 's^-1', species: 'Escherichia coli',
    sourceId: 'ITO_2021', doi: '10.1038/s41467-021-23516-y', epistemics: 'MEASURED',
    file: XS, jsonPath: 'studies.ito2021.rotationBindingBins["' + bw + '"][].bindingRatePerSecond' });
}

// Lisevich 2025
const lr = st.lisevich2025.rotationRates;
R({ group: 'rotation', quantity: 'motor rotation (10 cells)', values: lr.map(r => r.motorRotationHz),
  unitsAsHeld: 'Hz', species: 'Escherichia coli', sourceId: 'LISEVICH_2025', doi: '10.1038/s41467-025-56980-x',
  epistemics: 'MEASURED', file: XS, jsonPath: 'studies.lisevich2025.rotationRates[].motorRotationHz' });
R({ group: 'rotation', quantity: 'filament rotation (10 cells)', values: lr.map(r => r.filamentRotationHz),
  unitsAsHeld: 'Hz', species: 'Escherichia coli', sourceId: 'LISEVICH_2025', doi: '10.1038/s41467-025-56980-x',
  epistemics: 'MEASURED', file: XS, jsonPath: 'studies.lisevich2025.rotationRates[].filamentRotationHz' });
R({ group: 'rotation', quantity: 'cell-body counter-rotation (10 cells)', values: lr.map(r => r.bodyRotationHz),
  unitsAsHeld: 'Hz', species: 'Escherichia coli', sourceId: 'LISEVICH_2025', doi: '10.1038/s41467-025-56980-x',
  epistemics: 'MEASURED', file: XS, jsonPath: 'studies.lisevich2025.rotationRates[].bodyRotationHz' });
R({ group: 'swimming', quantity: 'cell swimming speed (10 cells)',
  values: st.lisevich2025.experimentalCellSpeeds.map(r => r.speedUmPerSecond),
  unitsAsHeld: 'um s^-1', species: 'Escherichia coli', sourceId: 'LISEVICH_2025',
  doi: '10.1038/s41467-025-56980-x', epistemics: 'MEASURED',
  file: XS, jsonPath: 'studies.lisevich2025.experimentalCellSpeeds[].speedUmPerSecond' });

// Mattingly & Tu 2026 block - digitized third-party data and model predictions
const bai = st.mattingly2026.bai2010DigitizedIntervals;
R({ group: 'switching', quantity: 'mean CCW interval vs CW bias (Bai 2010, digitized)',
  values: bai.map(r => r.meanCcwIntervalSeconds), pairedCwBias: bai.map(r => r.cwBias),
  unitsAsHeld: 's', species: 'Escherichia coli (implied; no organism key on this study)',
  sourceId: 'MATTINGLY_TU_2026 (digitized from Bai 2010 - Bai 2010 itself has NO DOI, authors or title recorded in this repo)',
  doi: '10.1038/s41567-025-03105-2', epistemics: 'DIGITIZED_BY_THIRD_PARTY',
  file: XS, jsonPath: 'studies.mattingly2026.bai2010DigitizedIntervals[].meanCcwIntervalSeconds',
  caveat: 'These are INTERVALS, not rates. No k...PerSecond field exists for Bai in this repo; inverting to rates is an analysis the estate has not performed or sanctioned.' });
R({ group: 'switching', quantity: 'mean CW interval vs CW bias (Bai 2010, digitized)',
  values: bai.map(r => r.meanCwIntervalSeconds), pairedCwBias: bai.map(r => r.cwBias),
  unitsAsHeld: 's', species: 'Escherichia coli (implied)',
  sourceId: 'MATTINGLY_TU_2026 (digitized from Bai 2010)', doi: '10.1038/s41567-025-03105-2',
  epistemics: 'DIGITIZED_BY_THIRD_PARTY',
  file: XS, jsonPath: 'studies.mattingly2026.bai2010DigitizedIntervals[].meanCwIntervalSeconds' });
const yuan = st.mattingly2026.yuan2009DigitizedSwitching;
R({ group: 'switching', quantity: 'k(CCW->CW) vs speed (Yuan 2009, digitized, 15 points)',
  values: yuan.map(r => r.kCcwToCw), pairedSpeedCcwHz: yuan.map(r => r.speedCcwHz),
  unitsAsHeld: 'NOT RECORDED IN ARTIFACT (key carries no unit suffix; s^-1 implied by context but not asserted here)',
  unitNotRecordedInArtifact: true, species: 'Escherichia coli (implied)',
  sourceId: 'MATTINGLY_TU_2026 (digitized from Yuan 2009 - Yuan 2009 itself has NO DOI, authors or title recorded in this repo)',
  doi: '10.1038/s41567-025-03105-2', epistemics: 'DIGITIZED_BY_THIRD_PARTY',
  file: XS, jsonPath: 'studies.mattingly2026.yuan2009DigitizedSwitching[].kCcwToCw' });
R({ group: 'switching', quantity: 'k(CW->CCW) vs speed (Yuan 2009, digitized, 15 points)',
  values: yuan.map(r => r.kCwToCcw), unitsAsHeld: 'NOT RECORDED IN ARTIFACT',
  unitNotRecordedInArtifact: true, species: 'Escherichia coli (implied)',
  sourceId: 'MATTINGLY_TU_2026 (digitized from Yuan 2009)', doi: '10.1038/s41567-025-03105-2',
  epistemics: 'DIGITIZED_BY_THIRD_PARTY',
  file: XS, jsonPath: 'studies.mattingly2026.yuan2009DigitizedSwitching[].kCwToCcw' });
const gmc = st.mattingly2026.sourceSwitchingPrediction; // object of parallel arrays
R({ group: 'switching', quantity: 'GMC model switching prediction (k both directions vs speed)',
  values: gmc.kCcwToCw, valuesCwToCcw: gmc.kCwToCcw,
  pairedSpeedHz: gmc.speedHz,
  unitsAsHeld: 'NOT RECORDED IN ARTIFACT', unitNotRecordedInArtifact: true,
  species: 'model output, not an observation', sourceId: 'MATTINGLY_TU_2026 (GMC Gillespie model)',
  doi: '10.1038/s41567-025-03105-2', epistemics: 'MODEL_PREDICTION',
  file: XS, jsonPath: 'studies.mattingly2026.sourceSwitchingPrediction[].kCcwToCw' });
R({ group: 'switching', quantity: 'Zhu 2024 block', unitsAsHeld: null,
  species: 'Escherichia coli (implied)', sourceId: 'ZHU_2024 (via MATTINGLY_TU_2026; NO DOI, authors or title recorded in this repo)',
  epistemics: 'NOT_HELD', file: XS, jsonPath: 'studies.mattingly2026.zhu2024PairedCells',
  caveat: 'EXPLICIT NEGATIVE: the Zhu 2024 block holds cwBias and inferred CheY-P only - no switching rate, no dwell time, no frequency of any kind.' });

// Nord 2017 - rotational drag (a timescale-carrying quantity)
const nord = st.nord2017.beadConditions;
R({ group: 'load', quantity: 'rotational drag per bead condition', values: nord.map(r => r.dragPnNmS),
  pairedBeadNm: nord.map(r => r.beadNm), unitsAsHeld: 'pN nm s', species: 'Escherichia coli (implied; no organism key)',
  sourceId: 'NORD_2017', doi: '10.1073/pnas.1716007114', epistemics: 'MEASURED',
  file: XS, jsonPath: 'studies.nord2017.beadConditions[].dragPnNmS' });
R({ group: 'load', quantity: 'Franco-Onate 2025 block', unitsAsHeld: null, species: '-',
  sourceId: 'FRANCO_ONATE_2025', doi: '10.1038/s41598-025-14570-3', epistemics: 'NOT_HELD',
  file: XS, jsonPath: 'studies.francoOnate2025',
  caveat: 'EXPLICIT NEGATIVE: no timescale held - only dimensionless relative occupancy and ringSize 13.' });

// ---------------- Wadhwa 2022 events ----------------
const WE = 'experiments/data/wadhwa-2022-events.json';
const we = rj(WE);
R({ group: 'sampling', quantity: 'sampling interval (all 129 motors, single distinct value)',
  values: [we.motors[0].sampleIntervalS], unitsAsHeld: 's', species: 'Escherichia coli',
  sourceId: 'WADHWA_2022', doi: '10.1038/s41467-022-33075-5', epistemics: 'MEASURED',
  file: WE, jsonPath: 'motors[0].sampleIntervalS' });
const durs = we.events.map(e => e.durationS);
R({ group: 'stator-dwell', quantity: 'raw dwell durations (1349 events, 129 motors)', range: rng(durs),
  unitsAsHeld: 's', species: 'Escherichia coli', sourceId: 'WADHWA_2022', doi: '10.1038/s41467-022-33075-5',
  epistemics: 'MEASURED', file: WE, jsonPath: 'events[].durationS' });

// ---------------- Wadhwa D-L-T source rates ----------------
const SP = 'experiments/source-parity-reference.json';
const sp = rj(SP);
const dm = sp.declaredMechanism;
const dltVal = v => (v && typeof v === 'object') ? (v.value !== undefined ? v.value : (v.upperBound !== undefined ? v.upperBound : v.fixed)) : v;
const dltKind = v => (v && typeof v === 'object') ? (v.upperBound !== undefined ? ' (upper bound)' : (v.fixed !== undefined ? ' (fixed)' : '')) : '';
const FENCE = dm.reportedMomentFit.warning;
const dltRow = (name, obj, key) => {
  const v = obj[key];
  if (v === undefined) throw new Error('missing ' + key);
  R({ group: 'stator-kinetics', quantity: name + dltKind(v), values: [dltVal(v)],
    unitsAsHeld: 's^-1', species: 'Escherichia coli', sourceId: 'WADHWA_2022',
    doi: '10.1038/s41467-022-33075-5', epistemics: 'MEASURED', file: SP,
    jsonPath: (obj === dm.reportedDerivedRatesPerSecond ? 'declaredMechanism.reportedDerivedRatesPerSecond.' : 'declaredMechanism.reportedMomentFit.') + key,
    fence: FENCE });
};
dltRow('k_off,loose (D-L-T mechanism)', dm.reportedDerivedRatesPerSecond, 'kOffLoose');
dltRow('k_tightening', dm.reportedDerivedRatesPerSecond, 'kTightening');
dltRow('k_loosening', dm.reportedDerivedRatesPerSecond, 'kLoosening');
dltRow('k_off,tight', dm.reportedDerivedRatesPerSecond, 'kOffTight');
dltRow('sigma_plus (stator arrival)', dm.reportedMomentFit, 'sigmaPlusPerSecond');
dltRow('sigma_minus', dm.reportedMomentFit, 'sigmaMinusPerSecond');
const h = dm.reportedHiddenState;
R({ group: 'stator-kinetics', quantity: 'hidden H state: entry rate, exit rate, mean lifetime',
  values: [h.kHPerSecond, h.kMinusHPerSecond], meanLifetimeSeconds: h.meanLifetimeSeconds,
  occurrences: h.occurrences, unitsAsHeld: 's^-1 (rates), s (lifetime)', species: 'Escherichia coli',
  sourceId: 'WADHWA_2022', doi: '10.1038/s41467-022-33075-5', epistemics: 'REPORTED_SUMMARY',
  file: SP, jsonPath: 'declaredMechanism.reportedHiddenState',
  caveat: 'Status REPORTED_SUMMARY_NOT_REEXTRACTED - the H state was never re-extracted from raw data in this estate (gate G07 SOURCE_ONLY).' });
R({ group: 'stator-dwell', quantity: 'per-state mean dwell, source Figure 3 (experiment, N=0..8)',
  values: sp.sourceDataFigure3.experiment.meanDwellSeconds, unitsAsHeld: 's', species: 'Escherichia coli',
  sourceId: 'WADHWA_2022', doi: '10.1038/s41467-022-33075-5', epistemics: 'MEASURED',
  file: SP, jsonPath: 'sourceDataFigure3.experiment.meanDwellSeconds' });
R({ group: 'stator-dwell', quantity: 'per-state mean dwell, source Figure 3 (theory, N=0..8)',
  values: sp.sourceDataFigure3.theory.meanDwellSeconds, unitsAsHeld: 's', species: 'model output',
  sourceId: 'WADHWA_2022 (their model)', doi: '10.1038/s41467-022-33075-5', epistemics: 'MODEL_PREDICTION',
  file: SP, jsonPath: 'sourceDataFigure3.theory.meanDwellSeconds' });

// ---------------- our fitted quantities (training-only) ----------------
const OE = 'experiments/results/observed-experiment-report.json';
const oe = rj(OE);
const smd = oe.fittedOnTrainingOnly.stateMeanDurationS;
R({ group: 'stator-dwell', quantity: 'per-state mean dwell, OUR training fit (states ' + Object.keys(smd).join(',') + ')',
  values: Object.values(smd), unitsAsHeld: 's', species: 'Escherichia coli',
  sourceId: 'this repo, fitted on Wadhwa 2022 TRAIN split only', doi: '10.1038/s41467-022-33075-5',
  epistemics: 'MEASURED', file: OE, jsonPath: 'fittedOnTrainingOnly.stateMeanDurationS' });
const mix = oe.fittedOnTrainingOnly.normalizedDurationModels.mixture;
R({ group: 'model-fit', quantity: 'UNI two-timescale mixture: fast and slow rates',
  values: [mix.rateFast, mix.rateSlow], weightFast: mix.weightFast,
  unitsAsHeld: 'per NORMALIZED-time unit (durations divided by per-state training scale) - NOT s^-1',
  species: 'model fit', sourceId: 'this repo (M3_UNI_TWO_TIMESCALE, train-only fit)',
  epistemics: 'MODEL_PREDICTION', file: OE, jsonPath: 'fittedOnTrainingOnly.normalizedDurationModels.mixture' });

// ---------------- refit rates (science gates) ----------------
const SG = 'experiments/results/science-gates-report.json';
const sg = rj(SG);
(function () {
  let refit = null;
  (function walk(o) { if (!o || typeof o !== 'object') return;
    if (o.kPlusByN && o.sigmaPlusPerSecond !== undefined) refit = refit || o;
    for (const k of Object.keys(o)) walk(o[k]); })(sg);
  if (refit) {
    R({ group: 'stator-kinetics', quantity: 'OUR refit k_plus by state', values: Object.values(refit.kPlusByN),
      unitsAsHeld: 's^-1', species: 'Escherichia coli', sourceId: 'this repo (refit; gate G03 FAIL - refit does NOT reproduce the source figure)',
      epistemics: 'MEASURED', file: SG, jsonPath: '(first object carrying kPlusByN)',
      caveat: 'ADVERSE, retained: G03 FAIL - the refit does not reproduce the article\'s own figure arrays (max relative discrepancy 3.767).' });
  }
})();

// ---------------- reduced-model constants (UNSOURCED - never next to measured) ----------------
const um = fs.readFileSync(path.join(ROOT, 'lib', 'uni-motor.js'), 'utf8');
const grab = (re) => { const m = re.exec(um); return m ? +m[1] : null; };
R({ group: 'reduced-model', quantity: 'stator remodeling relaxation (recruit/release) - TEACHING MODEL',
  values: [grab(/remodelingTauS\s*[:=]\s*([\d.]+)/), grab(/remodelingReleaseTauS\s*[:=]\s*([\d.]+)/)].filter(v => v !== null),
  unitsAsHeld: 's', species: 'none - hand-set constant', sourceId: 'lib/uni-motor.js (NO SOURCE PIN)',
  epistemics: 'REDUCED_MODEL', unsourced: true, file: 'lib/uni-motor.js', jsonPath: 'remodelingTauS',
  caveat: 'UNSOURCED. docs/SCIENCE.md labels the whole block MODELED / TEACHING REDUCTION. Do not read next to measured values.' });

// ---------------- write ----------------
const out = { schema: 'uni.flagellum.classroom-timescales/1.0.0',
  note: 'Every value read programmatically from the named artifact at build time; provenance is file + JSON path. Nothing typed by hand. Where a key carries no unit, unitNotRecordedInArtifact is true and no unit is asserted.',
  epistemicsVocabulary: ['MEASURED', 'DIGITIZED_BY_THIRD_PARTY', 'MODEL_PREDICTION', 'REDUCED_MODEL', 'REPORTED_SUMMARY', 'NOT_HELD'],
  rows };
fs.writeFileSync(path.join(ROOT, 'docs', 'classroom-assets', 'timescales.v1.json'), JSON.stringify(out, null, 1) + '\n');
console.log('timescales.v1.json: ' + rows.length + ' rows');
for (const g of [...new Set(rows.map(r => r.group))]) console.log('  ' + g + ': ' + rows.filter(r => r.group === g).length);
