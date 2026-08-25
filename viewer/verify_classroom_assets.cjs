#!/usr/bin/env node
// verify_classroom_assets.cjs - the classroom gate. Checks, never trusts:
// assets exist - sizes under cap - source sha256s match the evidence manifest -
// renderer re-run is byte-identical - timescales artifact parses with expected shape -
// every served route answers 200.
'use strict';
const fs = require('fs'), path = require('path'), crypto = require('crypto'), cp = require('child_process'), http = require('http');
const ROOT = path.resolve(__dirname, '..');
const A = p => path.join(ROOT, 'docs', 'classroom-assets', p);
let fails = 0;
const ok = (name, cond, detail) => { console.log((cond ? 'PASS ' : 'FAIL ') + name + (detail ? ' - ' + detail : '')); if (!cond) fails++; };
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');

// 1. assets exist
const sm = JSON.parse(fs.readFileSync(A('structures-manifest.json'), 'utf8'));
ok('structures-manifest has 14 files', sm.files.length === 14, String(sm.files.length));
let missing = sm.files.filter(f => !fs.existsSync(A(f.file)));
ok('all rendered SVGs exist', missing.length === 0, missing.map(f => f.file).join(','));
let oversized = sm.files.filter(f => fs.statSync(A(f.file)).size > 1500000);
ok('all SVGs under 1.5MB', oversized.length === 0);
ok('room-bg.webp exists', fs.existsSync(A('room-bg.webp')));

// 2. source sha256 cross-check against the walkthrough evidence manifest
const wt = JSON.parse(fs.readFileSync(path.join(ROOT, 'public', 'walkthrough-evidence-manifest.v1.json'), 'utf8'));
for (const gz of ['public/data/structures/6ysl.cif.gz', 'public/data/structures/7e82.cif.gz']) {
  const declared = (wt.assets || []).find(a => a.path === gz);
  const got = sha(path.join(ROOT, gz));
  ok('source sha256 ' + gz.split('/').pop(), declared && declared.sha256 === got, got.slice(0, 12));
}
// MANIFEST.json sha for room-bg
const man = JSON.parse(fs.readFileSync(A('MANIFEST.json'), 'utf8'));
ok('room-bg sha256 matches MANIFEST', man.assets[0].sha256 === sha(A('room-bg.webp')));

// 2b. room anchors: exist, bound to the CURRENT background image, sane fractions
const anch = JSON.parse(fs.readFileSync(A('room-anchors.v1.json'), 'utf8'));
ok('anchors bound to room-bg sha256', anch.sourceSha256 === sha(A('room-bg.webp')),
  'stale anchors after a background change - re-run viewer/measure_room_anchors.cjs');
ok('anchor fractions sane', Object.values(anch.anchors).every(b =>
  b.x >= 0 && b.y >= 0 && b.w > 0.02 && b.h > 0.02 && b.x + b.w <= 1.001 && b.y + b.h <= 1.001));
ok('all four surfaces anchored', ['whiteboard', 'boardLeft', 'boardRight', 'benchFront']
  .every(k => anch.anchors[k]));

// 3. renderer determinism: re-run into a temp dir, byte-compare the SVG set
const tmp = fs.mkdtempSync(path.join(require('os').tmpdir(), 'clsgate-'));
try {
  const src = fs.readFileSync(path.join(ROOT, 'viewer', 'render_structure_svg.cjs'), 'utf8')
    .replace("const ROOT = path.resolve(__dirname, '..');", 'const ROOT = ' + JSON.stringify(ROOT) + ';')
    .replace("path.join(ROOT, 'docs', 'classroom-assets')", JSON.stringify(tmp));
  const tmpScript = path.join(tmp, '_render.cjs');
  fs.writeFileSync(tmpScript, src);
  cp.execSync('node ' + JSON.stringify(tmpScript), { cwd: ROOT, stdio: 'pipe' });
  let diff = 0;
  for (const f of sm.files) if (sha(A(f.file)) !== sha(path.join(tmp, f.file))) diff++;
  ok('renderer re-run byte-identical (14 SVGs)', diff === 0, diff + ' differ');
} finally { fs.rmSync(tmp, { recursive: true, force: true }); }

// 4. timescales artifact shape
const ts = JSON.parse(fs.readFileSync(A('timescales.v1.json'), 'utf8'));
ok('timescales rows present', ts.rows.length >= 30, String(ts.rows.length));
ok('every row carries epistemics + file + jsonPath',
  ts.rows.every(r => r.epistemics && r.file && r.jsonPath));
ok('unsourced reduced-model rows are flagged',
  ts.rows.filter(r => r.epistemics === 'REDUCED_MODEL').every(r => r.unsourced === true));

// 5. routes (only if the viewer is up; absence is reported, not passed)
const routes = ['/classroom', '/api/classroom', '/assets/classroom/room-bg.webp', '/assets/classroom/7e82-composite-front.svg'];
let done = 0;
routes.forEach(r => {
  http.get({ host: '127.0.0.1', port: 8111, path: r, timeout: 3000 }, res => {
    ok('route ' + r, res.statusCode === 200, String(res.statusCode)); res.resume();
    if (++done === routes.length) finish();
  }).on('error', () => { ok('route ' + r, false, 'viewer not reachable'); if (++done === routes.length) finish(); });
});
function finish() {
  console.log(fails === 0 ? 'CLASSROOM GATE: PASS' : 'CLASSROOM GATE: FAIL (' + fails + ')');
  process.exit(fails === 0 ? 0 : 1);
}
