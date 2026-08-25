#!/usr/bin/env node
// UNI-FLAGELLUM BIO VIEW - the BIOLOGICAL programme. Zero deps, CPU-only, caches nothing.
// Port 8111. This is the mission surface; the colony viewer on :8110 is a different subsystem.
const http = require('http'), fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.resolve(__dirname, '..');
const PORT = 8111;
const rd = p => { try { return fs.readFileSync(path.join(ROOT, p), 'utf8'); } catch (e) { return null; } };
const rj = p => { try { return JSON.parse(rd(p)); } catch (e) { return null; } };
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function gates() {
  const sci = rj('experiments/results/science-gates-report.json');
  const xs = rj('experiments/results/cross-study-parity-report.json');
  const pick = (r) => {
    if (!r) return null;
    const g = (r.gates || []).map(x => ({ id: x.id || x.gateId, status: x.status }));
    return { summary: r.summary || null, gates: g };
  };
  return { science: pick(sci), cross: pick(xs) };
}
function readDrafts() {
  try {
    return fs.readFileSync(path.join(ROOT, 'evidence', 'blanket_drafts.ndjson'), 'utf8')
      .split(String.fromCharCode(10)).filter(Boolean).map(l => { try { return JSON.parse(l); } catch (e) { return null; } }).filter(Boolean);
  } catch (e) { return []; }
}
function gitlog() {
  try {
    return cp.execSync('git log -10 --pretty=format:%h%x1f%s%x1f%ad --date=short', { cwd: ROOT })
      .toString().trim().split('\n').map(l => { const p = l.split('\x1f'); return { h: p[0], s: p[1], d: p[2] }; });
  } catch (e) { return []; }
}


// ---- static assets (classroom SVGs, media) — sanitized, allowlisted, Range-capable ----
const STATIC = { '/assets/classroom/': 'docs/classroom-assets/', '/assets/media/': 'public/media/', '/sources/': 'docs/sources/' };
const MIME = { '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp',
  '.jpg': 'image/jpeg', '.json': 'application/json', '.mp4': 'video/mp4',
  '.html': 'text/html; charset=utf-8', '.txt': 'text/plain; charset=utf-8', '.md': 'text/plain; charset=utf-8', '.pdf': 'application/pdf' };
const NAME_OK = /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/; // single flat segment: no /, \, :, .. survive this
function serveStatic(req, res, u) {
  let dec; try { dec = decodeURIComponent(u); } catch (e) { res.writeHead(400); res.end('bad url'); return true; }
  const pfx = Object.keys(STATIC).find(p => dec.startsWith(p));
  if (!pfx) return false;
  const name = dec.slice(pfx.length);
  const ext = path.extname(name).toLowerCase();
  const fail = () => { res.writeHead(404, { 'content-type': 'text/plain' }); res.end('not found'); return true; };
  if (!NAME_OK.test(name) || name.includes('..') || !MIME[ext]) return fail();
  const abs = path.join(ROOT, STATIC[pfx], name);
  let st; try { st = fs.statSync(abs); } catch (e) { return fail(); }
  if (!st.isFile()) return fail();
  const total = st.size;
  res.setHeader('Accept-Ranges', 'bytes');
  res.setHeader('Cache-Control', 'no-store');
  const m = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range || '');
  let start = 0, end = total - 1, code = 200;
  if (m && (m[1] || m[2])) {
    if (m[1]) { start = +m[1]; end = m[2] ? Math.min(+m[2], total - 1) : total - 1; }
    else { start = Math.max(0, total - +m[2]); }
    if (start > end || start >= total) { res.writeHead(416, { 'content-range': 'bytes */' + total }); res.end(); return true; }
    code = 206; res.setHeader('Content-Range', 'bytes ' + start + '-' + end + '/' + total);
  }
  res.writeHead(code, { 'content-type': MIME[ext], 'content-length': end - start + 1 });
  if (req.method === 'HEAD') { res.end(); return true; }
  fs.createReadStream(abs, { start, end }).pipe(res);
  return true;
}

const DASH = [
'<!doctype html><meta charset="utf-8"><title>UNI-FLAGELLUM - the biological programme</title>',
'<style>',
':root{--bg:#0e1116;--pan:#161b22;--ln:#2a3441;--tx:#e6edf3;--dim:#93a1b0;--acc:#7f9fdd;',
'--ok:#4bd18a;--bad:#ff7a7a;--warn:#e8bb55;--gold:#d9b45f;--mono:ui-monospace,Consolas,monospace}',
'*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:15px/1.6 ui-sans-serif,Segoe UI,Roboto,sans-serif}',
'header{position:sticky;top:0;background:#0e1116ee;border-bottom:1px solid var(--ln);padding:12px 20px;display:flex;gap:16px;align-items:center;flex-wrap:wrap;z-index:9}',
'h1{font-size:16px;margin:0;font-weight:600}',
'.links a{color:var(--dim);text-decoration:none;font-size:13px;margin-right:14px;border-bottom:1px dotted var(--ln)}',
'.links a:hover{color:var(--acc)}.stamp{margin-left:auto;font:11px var(--mono);color:var(--dim)}',
'main{padding:18px 20px;max-width:1280px;margin:0 auto}',
'section{background:var(--pan);border:1px solid var(--ln);border-radius:12px;padding:18px 20px;margin:14px 0}',
'h2{font-size:12.5px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);margin:0 0 12px;font-weight:600}',
'.verdict{border-color:var(--bad);background:#241315}',
'.verdict h3{margin:0 0 8px;font-size:20px;color:#fff}',
'table{border-collapse:collapse;width:100%;font-size:13.5px}',
'th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--ln)}',
'th{color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:.5px}',
'td.v{font-family:var(--mono);white-space:nowrap}tr.win td{background:#241315}',
'.chip{display:inline-block;font:11px var(--mono);font-weight:600;padding:2px 9px;border-radius:20px}',
'.PASS{color:var(--ok);background:#12271c}.FAIL{color:var(--bad);background:#2a1516}',
'.NOT_ESTABLISHED,.SOURCE_ONLY{color:var(--warn);background:#2a2110}',
'.BLOCKED_EXTERNAL{color:#8ba0e0;background:#161b2e}',
'.gwrap{display:flex;flex-wrap:wrap;gap:6px}',
'.g{font:11px var(--mono);padding:3px 8px;border-radius:6px;border:1px solid var(--ln)}',
'.commit{display:grid;grid-template-columns:64px 1fr 80px;gap:8px;padding:4px 0;border-bottom:1px solid var(--ln);font-size:12.5px}',
'.sha{font:11px var(--mono);color:var(--acc)}.dt{font:11px var(--mono);color:var(--dim)}',
'.say{color:var(--dim);font-size:13px}',
'.big{font:26px var(--mono);font-weight:700}',
'</style>',
'<header><h1>UNI-FLAGELLUM &mdash; the biological programme</h1>',
'<span class="links"><a href="/classroom">THE CLASSROOM</a><a href="/blankets">BLANKET BUILDER</a><a href="/models">THE MODELS</a><a href="/architecture">the architecture</a><a href="/snapshot">state snapshot</a>',
'<a href="/doors">external doors</a><a href="/api/state">json</a></span>',
'<span class="stamp" id="st"></span></header><main id="m">loading&hellip;</main>',
'<script>',
'function chip(s){return "<span class=\\"chip "+s+"\\">"+s+"</span>";}',
'function tick(){fetch("/api/state?t="+Date.now()).then(function(r){return r.json();}).then(function(d){',
'document.getElementById("st").textContent=new Date().toLocaleTimeString()+" \\u00b7 read live from the result files";',
'var sci=d.gates.science,xs=d.gates.cross;',
'function board(o){if(!o)return "<span class=\\"say\\">(report not readable)</span>";',
'return "<div class=\\"gwrap\\">"+o.gates.map(function(g){return "<span class=\\"g "+g.status+"\\">"+g.id.split("_")[0]+" "+g.status+"</span>";}).join("")+"</div>";}',
'var commits=(d.commits||[]).map(function(c){return "<div class=\\"commit\\"><span class=\\"sha\\">"+c.h+"</span><span>"+',
'String(c.s).replace(/&/g,"&amp;").replace(/</g,"&lt;")+"</span><span class=\\"dt\\">"+c.d+"</span></div>";}).join("");',
'document.getElementById("m").innerHTML=',
'"<section class=\\"verdict\\"><h3>The mechanism loses to a two-parameter curve.</h3>"',
'+"<p>On the only real held-out <i>E. coli</i> data here, a plain <b>lognormal</b> (3.4093) out-predicts our "',
'+"two-timescale mechanism (3.4343) and every mechanistic candidate. Every contrast crosses zero &rArr; <b>NOT_ESTABLISHED</b>.</p>"',
'+"<p style=\\"margin-bottom:0\\"><b>Full biological parity is FALSE.</b> Cross-lab transfer tests: 0 &middot; discriminating interventions: 0 &middot; independent laboratories: 0.</p></section>"',
'+"<section><h2>The three &mdash; the rivals our model must beat</h2><table>"',
'+"<tr><th>model</th><th>what it is</th><th>held-out score</th></tr>"',
'+"<tr class=\\"win\\"><td>M2 lognormal</td><td class=\\"say\\">2 parameters, no mechanism</td><td class=\\"v\\">3.4093 &larr; wins</td></tr>"',
'+"<tr><td>M1 Weibull</td><td class=\\"say\\">1 free shape; our own &tau;&rarr;0 limit</td><td class=\\"v\\">3.4333</td></tr>"',
'+"<tr><td>M0 exponential</td><td class=\\"say\\">the memoryless null</td><td class=\\"v\\">3.5480</td></tr>"',
'+"<tr><td><b>M3 two-timescale</b></td><td class=\\"say\\"><b>ours</b> &mdash; the mechanistic claim</td><td class=\\"v\\">3.4343</td></tr>"',
'+"</table><p class=\\"say\\">Motor-equal NLPD, 19 held-out motors, lower better. Ours places 4th of 4. "',
'+"Settled from code: lib/observed-experiment.js:325-329 holds exactly three rivals.</p></section>"',
'+"<section><h2>Science gates &middot; G00&ndash;G13</h2>"+board(sci)+"</section>"',
'+"<section><h2>Cross-study gates &middot; X01&ndash;X16</h2>"+board(xs)+"</section>"',
'+"<section><h2>Recent commits (this repo)</h2>"+commits+"</section>";',
'}).catch(function(e){});}',
'tick();setInterval(tick,4000);',
'</script>'
].join('\n');

function page(title, body) {
  return '<!doctype html><meta charset="utf-8"><title>' + esc(title) + '</title>'
    + '<style>body{background:#0e1116;color:#e6edf3;font:15px/1.65 ui-sans-serif,Segoe UI,sans-serif;max-width:1000px;margin:0 auto;padding:26px}'
    + 'pre{white-space:pre-wrap;font:12.5px ui-monospace,Consolas,monospace}a{color:#7f9fdd}</style>'
    + '<p><a href="/">&larr; dashboard</a></p>' + body;
}

http.createServer((req, res) => {
  const u = (req.url || '/').split('?')[0];
  const send = (c, t, b) => { res.writeHead(c, { 'content-type': t, 'cache-control': 'no-store' }); res.end(b); };
  if (serveStatic(req, res, u)) return;
  if (u === '/') return send(200, 'text/html; charset=utf-8', DASH);
  if (u === '/blankets') { const f = rd('docs/blankets.html'); return f ? send(200, 'text/html; charset=utf-8', f) : send(404, 'text/plain', 'not found'); }
  if (u === '/api/blankets') {
    return send(200, 'application/json', JSON.stringify({
      asIs: rj('docs/classroom-assets/blankets-as-is.v1.json'),
      inventory: rj('docs/classroom-assets/signal-inventory.v1.json'),
      drafts: readDrafts(),
      now: Date.now()
    }));
  }
  if (u === '/api/blanket-draft' && req.method === 'POST') {
    let body = '';
    req.on('data', c => { body += c; if (body.length > 512000) req.destroy(); });
    req.on('end', () => {
      try {
        const draft = JSON.parse(body);
        // append-only: drafts are never edited or deleted, only superseded
        const row = JSON.stringify({ savedAt: new Date().toISOString(), draft }) + String.fromCharCode(10);
        fs.appendFileSync(path.join(ROOT, 'evidence', 'blanket_drafts.ndjson'), row);
        send(200, 'application/json', JSON.stringify({ ok: true, count: readDrafts().length }));
      } catch (e) { send(400, 'application/json', JSON.stringify({ ok: false, error: String(e) })); }
    });
    return;
  }
  if (u === '/classroom') { const f = rd('docs/classroom.html'); return f ? send(200, 'text/html; charset=utf-8', f) : send(404, 'text/plain', 'not found'); }
  if (u === '/api/classroom') {
    return send(200, 'application/json', JSON.stringify({
      manifest: rj('public/walkthrough-evidence-manifest.v1.json'),
      structures: rj('docs/classroom-assets/structures-manifest.json'),
      timescales: rj('docs/classroom-assets/timescales.v1.json'),
      fitted: (rj('experiments/results/observed-experiment-report.json') || {}).fittedOnTrainingOnly || null,
      gates: gates(), now: Date.now()
    }));
  }
  if (u === '/api/state') return send(200, 'application/json', JSON.stringify({ gates: gates(), commits: gitlog(), now: Date.now() }, null, 1));
  if (u === '/api/models') {
    return send(200, 'application/json', JSON.stringify({
      fside: rj('hierarchical-aif/results/motor_stack_aif/F_SIDE_MOTOR_STACK_SCORING_RESULT.json'),
      observed: rj('experiments/results/observed-experiment-report.json'),
      b3models: (rj('audits/phase-b/b3-model-competition-result.json') || {}).models || null,
      now: Date.now()
    }));
  }
  if (u === '/models') { const f = rd('docs/models.html'); return f ? send(200, 'text/html; charset=utf-8', f) : send(404, 'text/plain', 'not found'); }
  if (u === '/architecture') { const f = rd('docs/architecture.html'); return f ? send(200, 'text/html; charset=utf-8', f) : send(404, 'text/plain', 'not found'); }
  if (u === '/snapshot') { const f = rd('docs/MODEL-STATE-SNAPSHOT-2026-08-19.html'); return f ? send(200, 'text/html; charset=utf-8', f) : send(404, 'text/plain', 'not found'); }
  if (u === '/doors') { const f = rd('docs/EXTERNAL-DOORS-ACQUISITION-CHECKLIST.md'); return f ? send(200, 'text/html; charset=utf-8', page('External doors', '<pre>' + esc(f) + '</pre>')) : send(404, 'text/plain', 'not found'); }
  send(404, 'text/plain', 'not found');
}).listen(PORT, '127.0.0.1', () => console.log('UNI-FLAGELLUM BIO VIEW on http://127.0.0.1:' + PORT + '/'));
