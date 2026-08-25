#!/usr/bin/env node
// render_structure_svg.cjs - zero-dep mmCIF -> SVG backbone renderer.
// Every plotted point is a literally deposited CA atom position. CPU-only, deterministic:
// no timestamps, fixed PCA sign convention; two runs must be byte-identical.
// Provenance: recomputes each source sha256 and hard-fails on mismatch with
// public/walkthrough-evidence-manifest.v1.json. Species labels ride inside every SVG
// (lib/walkthrough.js:468 - structural evidence must retain cross-species labels).
'use strict';
const fs = require('fs'), path = require('path'), zlib = require('zlib'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'docs', 'classroom-assets');
const PX_PER_ANG = 1.4;           // ONE global scale so relative part sizes are physically true
const MAX_SVG_BYTES = 1500000;
const SEG_MAX = 30;               // CA per polyline segment (depth-sort granularity)

const STRUCTURES = [
  { pdbId: '6YSL', gz: 'public/data/structures/6ysl.cif.gz', species: 'Bacillus subtilis',
    label: 'MotA5MotB2 stator complex', truthClass: 'STRUCTURAL_RECONSTRUCTION',
    citation: 'PDB 6YSL; Deme et al., Nature Microbiology 5, 1553-1564 (2020)', doi: '10.2210/pdb6YSL/pdb',
    palette: { '1': '#7f9fdd', '2': '#e8bb55' } },
  { pdbId: '7E82', gz: 'public/data/structures/7e82.cif.gz', species: 'Salmonella enterica', flipFront: true, // deposited +z runs INTO the cell; flip so the hook is up, matching the anatomy map
    label: 'flagellar rod with partial hook', truthClass: 'STRUCTURAL_RECONSTRUCTION',
    citation: 'PDB 7E82; Tan et al., Cell 184, 2665-2679.e19 (2021)', doi: '10.2210/pdb7E82/pdb',
    palette: { '1': '#7f9fdd', '2': '#4bd18a', '3': '#e8bb55', '4': '#d9b45f',
               '5': '#ff9d7a', '6': '#6fd3c7', '7': '#c39df0', '8': '#ff7a7a' } },
];

function die(msg) { console.error('FATAL: ' + msg); process.exit(1); }
function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }

// Verbatim declared sha256 for a structure from the walkthrough evidence manifest.
function declaredSha(manifest, gzPath) {
  let found = null;
  (function walk(o) {
    if (!o || typeof o !== 'object') return;
    if (o.path === gzPath && o.sha256) found = o.sha256;
    for (const k of Object.keys(o)) walk(o[k]);
  })(manifest);
  return found;
}

// Quote-aware tokenizer for mmCIF loop data lines (handles quoted multi-word values).
function cifTokens(line) {
  const out = []; let i = 0; const n = line.length;
  while (i < n) {
    while (i < n && (line[i] === ' ' || line[i] === '\t')) i++;
    if (i >= n) break;
    const q = line[i];
    if (q === "'" || q === '"') {
      let j = i + 1;
      while (j < n && !(line[j] === q && (j + 1 >= n || line[j + 1] === ' ' || line[j + 1] === '\t'))) j++;
      out.push(line.slice(i + 1, j)); i = j + 1;
    } else {
      let j = i;
      while (j < n && line[j] !== ' ' && line[j] !== '\t') j++;
      out.push(line.slice(i, j)); i = j;
    }
  }
  return out;
}

function parseCif(text) {
  const lines = text.split('\n');
  // --- locate _atom_site loop headers ---
  const col = {}; let headerCount = 0, atomStart = -1;
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].startsWith('_atom_site.')) {
      let j = i, k = 0;
      while (j < lines.length && lines[j].startsWith('_atom_site.')) {
        col[lines[j].trim().slice('_atom_site.'.length)] = k++; j++;
      }
      headerCount = k; atomStart = j; break;
    }
  }
  if (atomStart < 0) die('no _atom_site loop found');
  for (const need of ['group_PDB', 'label_atom_id', 'type_symbol', 'label_asym_id',
    'label_entity_id', 'label_seq_id', 'Cartn_x', 'Cartn_y', 'Cartn_z', 'pdbx_PDB_model_num'])
    if (!(need in col)) die('missing _atom_site.' + need);
  // --- CA atoms ---
  const atoms = []; let totalAtomRows = 0;
  for (let j = atomStart; j < lines.length; j++) {
    const L = lines[j];
    if (!L || L[0] === '#') break;
    const t = L.trim().split(/\s+/);
    if (t.length !== headerCount) die('atom row field count ' + t.length + ' != header ' + headerCount + ' at line ' + (j + 1));
    if (t[col.group_PDB] !== 'ATOM') continue;
    totalAtomRows++;
    if (t[col.label_atom_id] !== 'CA' || t[col.type_symbol] !== 'C') continue;
    if (t[col.pdbx_PDB_model_num] !== '1') continue;
    atoms.push({ chain: t[col.label_asym_id], entity: t[col.label_entity_id],
      seq: parseInt(t[col.label_seq_id], 10),
      x: +t[col.Cartn_x], y: +t[col.Cartn_y], z: +t[col.Cartn_z] });
  }
  // --- entity descriptions (verbatim) ---
  const entityDesc = {};
  for (let j = 0; j < lines.length; j++) {
    if (lines[j].trim() === '_entity.id' || lines[j].startsWith('_entity.id ')) {
      const hdr = []; let k = j;
      while (k < lines.length && lines[k].startsWith('_entity.')) { hdr.push(lines[k].trim().slice('_entity.'.length)); k++; }
      const di = hdr.indexOf('pdbx_description'), ii = hdr.indexOf('id');
      if (di < 0 || ii < 0) break;
      while (k < lines.length && lines[k] && lines[k][0] !== '#' && !lines[k].startsWith('_')) {
        const t = cifTokens(lines[k]);
        if (t.length === hdr.length) entityDesc[t[ii]] = t[di];
        k++;
      }
      break;
    }
  }
  // --- EM resolution (single key-value line) ---
  let resolution = null;
  for (const L of lines) {
    const m = /^_em_3d_reconstruction\.resolution\s+([\d.]+)/.exec(L);
    if (m) { resolution = m[1]; break; }
  }
  return { atoms, totalAtomRows, entityDesc, resolution };
}

// PCA principal axis via deterministic power iteration.
function pcaFrame(atoms) {
  const n = atoms.length;
  let cx = 0, cy = 0, cz = 0;
  for (const a of atoms) { cx += a.x; cy += a.y; cz += a.z; }
  cx /= n; cy /= n; cz /= n;
  let xx = 0, yy = 0, zz = 0, xy = 0, xz = 0, yz = 0;
  for (const a of atoms) {
    const dx = a.x - cx, dy = a.y - cy, dz = a.z - cz;
    xx += dx * dx; yy += dy * dy; zz += dz * dz; xy += dx * dy; xz += dx * dz; yz += dy * dz;
  }
  const C = [[xx, xy, xz], [xy, yy, yz], [xz, yz, zz]];
  let u = [0, 0, 1];
  for (let it = 0; it < 60; it++) {
    const v = [
      C[0][0] * u[0] + C[0][1] * u[1] + C[0][2] * u[2],
      C[1][0] * u[0] + C[1][1] * u[1] + C[1][2] * u[2],
      C[2][0] * u[0] + C[2][1] * u[1] + C[2][2] * u[2]];
    const m = Math.hypot(v[0], v[1], v[2]);
    u = [v[0] / m, v[1] / m, v[2] / m];
  }
  if (u[2] < 0 || (u[2] === 0 && u[1] < 0)) u = [-u[0], -u[1], -u[2]]; // fixed sign
  const ref = Math.abs(u[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
  const dot = ref[0] * u[0] + ref[1] * u[1] + ref[2] * u[2];
  let r = [ref[0] - dot * u[0], ref[1] - dot * u[1], ref[2] - dot * u[2]];
  const rm = Math.hypot(r[0], r[1], r[2]); r = [r[0] / rm, r[1] / rm, r[2] / rm];
  const d = [u[1] * r[2] - u[2] * r[1], u[2] * r[0] - u[0] * r[2], u[0] * r[1] - u[1] * r[0]];
  return { c: [cx, cy, cz], u, r, d };
}

function project(a, F, view, flipFront) {
  const p = [a.x - F.c[0], a.y - F.c[1], a.z - F.c[2]];
  const du = p[0] * F.u[0] + p[1] * F.u[1] + p[2] * F.u[2];
  const dr = p[0] * F.r[0] + p[1] * F.r[1] + p[2] * F.r[2];
  const dd = p[0] * F.d[0] + p[1] * F.d[1] + p[2] * F.d[2];
  const fy = flipFront ? du : -du; // flip is presentation only; coordinates remain the deposited atoms
  return view === 'front' ? { sx: dr, sy: fy, depth: dd } : { sx: dr, sy: dd, depth: du };
}

// Build chain traces -> segments of <=SEG_MAX consecutive CA (break on seq gap > 1)
function buildSegments(atoms, F, view, entityFilter, flipFront) {
  const byChain = new Map();
  for (const a of atoms) {
    if (entityFilter && a.entity !== entityFilter) continue;
    if (!byChain.has(a.chain)) byChain.set(a.chain, []);
    byChain.get(a.chain).push(a);
  }
  const segs = [];
  const chains = [...byChain.keys()].sort();
  for (const ch of chains) {
    const list = byChain.get(ch).slice().sort((a, b) => a.seq - b.seq);
    let cur = [];
    const flush = () => {
      if (cur.length >= 2) {
        for (let i = 0; i < cur.length; i += SEG_MAX - 1) {
          const part = cur.slice(i, i + SEG_MAX);
          if (part.length >= 2) {
            let dsum = 0;
            const pts = part.map(a => { const q = project(a, F, view, flipFront); dsum += q.depth; return q; });
            segs.push({ entity: part[0].entity, depth: dsum / part.length, pts });
          }
        }
      }
      cur = [];
    };
    for (let i = 0; i < list.length; i++) {
      if (cur.length && list[i].seq !== cur[cur.length - 1].seq + 1) flush();
      cur.push(list[i]);
    }
    flush();
  }
  segs.sort((a, b) => a.depth - b.depth); // back -> front (painter)
  return segs;
}

function svgFor(segs, meta) {
  let minX = 1e9, maxX = -1e9, minY = 1e9, maxY = -1e9, minD = 1e9, maxD = -1e9;
  for (const s of segs) {
    if (s.depth < minD) minD = s.depth; if (s.depth > maxD) maxD = s.depth;
    for (const p of s.pts) {
      if (p.sx < minX) minX = p.sx; if (p.sx > maxX) maxX = p.sx;
      if (p.sy < minY) minY = p.sy; if (p.sy > maxY) maxY = p.sy;
    }
  }
  const M = 16, CAP = 44;
  const W = (maxX - minX) * PX_PER_ANG + 2 * M;
  const H = (maxY - minY) * PX_PER_ANG + 2 * M + CAP;
  const X = v => ((v - minX) * PX_PER_ANG + M).toFixed(1);
  const Y = v => ((v - minY) * PX_PER_ANG + M).toFixed(1);
  const dSpan = (maxD - minD) || 1;
  const polys = segs.map(s => {
    const op = (0.35 + 0.65 * (s.depth - minD) / dSpan).toFixed(2);
    const pts = s.pts.map(p => X(p.sx) + ',' + Y(p.sy)).join(' ');
    return '<polyline stroke="' + meta.palette[s.entity] + '" stroke-opacity="' + op + '" points="' + pts + '"/>';
  }).join('\n');
  // scale bar
  const barA = meta.mini ? 50 : 100;
  const barPx = barA * PX_PER_ANG;
  const by = +(H - CAP + 14).toFixed(1);
  const caption = 'PDB ' + meta.pdbId + ' · ' + meta.species + ' · EM' +
    (meta.resolution ? ' ' + meta.resolution + ' Å' : '') + ' · ' + meta.caCount + ' deposited CA atoms · CC0';
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + Math.ceil(W) + ' ' + Math.ceil(H) +
    '" role="img">\n<title>' + meta.title + '</title>\n' +
    '<g fill="none" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">\n' + polys + '\n</g>\n' +
    '<g font-family="ui-monospace,Consolas,monospace" font-size="10" fill="#93a1b0">\n' +
    '<line x1="' + M + '" y1="' + by + '" x2="' + (M + barPx) + '" y2="' + by + '" stroke="#93a1b0" stroke-width="1.5"/>\n' +
    '<text x="' + (M + barPx + 6) + '" y="' + (by + 3.5) + '">' + barA + ' Å</text>\n' +
    '<text x="' + M + '" y="' + (by + 16) + '">' + caption + '</text>\n' +
    '</g>\n</svg>\n';
}

function slugify(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''); }

// ---------------- main ----------------
const wtManifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'public', 'walkthrough-evidence-manifest.v1.json'), 'utf8'));
if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });
const manifest = { schema: 'uni.flagellum.classroom-structures/1.0.0', pxPerAngstrom: PX_PER_ANG,
  renderer: 'viewer/render_structure_svg.cjs', note: 'Every plotted point is a deposited CA atom position; nothing is drawn by hand.', files: [] };

for (const S of STRUCTURES) {
  const gzBuf = fs.readFileSync(path.join(ROOT, S.gz));
  const gotSha = sha256(gzBuf);
  const wantSha = declaredSha(wtManifest, S.gz);
  if (!wantSha) die('no declared sha256 found in walkthrough manifest for ' + S.gz);
  if (gotSha !== wantSha) die('sha256 mismatch for ' + S.gz + ': recomputed ' + gotSha + ' != declared ' + wantSha);
  const parsed = parseCif(zlib.gunzipSync(gzBuf).toString('utf8'));
  const atoms = parsed.atoms;
  console.log(S.pdbId + ': ' + parsed.totalAtomRows + ' ATOM rows, ' + atoms.length + ' CA, entities: ' +
    Object.entries(parsed.entityDesc).map(([k, v]) => k + '=' + v).join(' | '));
  const F = pcaFrame(atoms);
  const entities = [...new Set(atoms.map(a => a.entity))].sort((a, b) => +a - +b);
  const entStats = {};
  for (const e of entities) {
    const list = atoms.filter(a => a.entity === e);
    entStats[e] = { caCount: list.length, chains: [...new Set(list.map(a => a.chain))].sort() };
  }
  const emit = (name, segs, meta) => {
    const svg = svgFor(segs, meta);
    if (Buffer.byteLength(svg) > MAX_SVG_BYTES) die(name + ' exceeds ' + MAX_SVG_BYTES + ' bytes');
    fs.writeFileSync(path.join(OUT, name), svg);
    manifest.files.push({ file: name, pdbId: S.pdbId, species: S.species, truthClass: S.truthClass,
      citation: S.citation, doi: S.doi, sourcePath: S.gz, sourceSha256: gotSha,
      view: meta.view, entityId: meta.entityId || null, description: meta.desc || S.label,
      caCount: meta.caCount, chains: meta.chains || null, color: meta.entityId ? S.palette[meta.entityId] : null,
      bytes: Buffer.byteLength(svg) });
    console.log('  wrote ' + name + ' (' + Buffer.byteLength(svg) + ' B)');
  };
  for (const view of ['front', 'top']) {
    const segs = buildSegments(atoms, F, view, null, S.flipFront && view === 'front');
    emit(S.pdbId.toLowerCase() + '-composite-' + view + '.svg', segs, {
      pdbId: S.pdbId, species: S.species, resolution: parsed.resolution, palette: S.palette, view,
      caCount: atoms.length, mini: false,
      title: 'PDB ' + S.pdbId + ' — ' + S.label + ', ' + S.species + ' — ' + view +
        ' orthographic CA trace, ' + atoms.length + ' deposited CA atoms, ' + PX_PER_ANG + ' px/Å' });
  }
  for (const e of entities) {
    const desc = parsed.entityDesc[e] || ('entity ' + e);
    const segs = buildSegments(atoms, F, 'front', e, !!S.flipFront);
    emit(S.pdbId.toLowerCase() + '-e' + e + '-' + slugify(desc) + '-front.svg', segs, {
      pdbId: S.pdbId, species: S.species, resolution: parsed.resolution, palette: S.palette, view: 'front',
      entityId: e, desc, caCount: entStats[e].caCount, chains: entStats[e].chains, mini: true,
      title: 'PDB ' + S.pdbId + ' entity ' + e + ' — ' + desc + ' (' + entStats[e].chains.length +
        ' chains), ' + S.species + ' — front CA trace, ' + entStats[e].caCount + ' deposited CA atoms' });
  }
}
fs.writeFileSync(path.join(OUT, 'structures-manifest.json'), JSON.stringify(manifest, null, 1) + '\n');
console.log('structures-manifest.json written (' + manifest.files.length + ' files)');
