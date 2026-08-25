#!/usr/bin/env node
// measure_room_anchors.cjs - measures the classroom background's surfaces from its PIXELS
// and freezes them as docs/classroom-assets/room-anchors.v1.json. The page positions every
// overlay from this file, so placement is measured, not eyeballed, and updating placement
// means editing ONE file. Anchors are BOUND to the exact image by sha256: regenerate the
// background and the gate fails until anchors are re-measured.
// Zero npm deps: ffmpeg (on PATH) decodes webp -> PPM; the PPM is parsed here.
'use strict';
const fs = require('fs'), path = require('path'), os = require('os'), cp = require('child_process'), crypto = require('crypto');
const ROOT = path.resolve(__dirname, '..');
const IMG = path.join(ROOT, 'docs', 'classroom-assets', 'room-bg.webp');
const OUT = path.join(ROOT, 'docs', 'classroom-assets', 'room-anchors.v1.json');

const sha = crypto.createHash('sha256').update(fs.readFileSync(IMG)).digest('hex');
const tmp = path.join(os.tmpdir(), 'room-anchors-' + process.pid + '.ppm');
cp.execSync('ffmpeg -y -loglevel error -i "' + IMG + '" -f image2 -vcodec ppm "' + tmp + '"');
const buf = fs.readFileSync(tmp); fs.unlinkSync(tmp);

// --- parse P6 PPM ---
let off = 0, fields = [];
while (fields.length < 4) {
  let line = '';
  while (buf[off] !== 10) { line += String.fromCharCode(buf[off]); off++; }
  off++;
  line = line.replace(/#.*/, '').trim();
  if (line) fields.push(...line.split(/\s+/));
}
if (fields[0] !== 'P6') { console.error('not P6'); process.exit(1); }
const W = +fields[1], H = +fields[2];
const px = buf.subarray(off);
const luma = (x, y) => { const i = (y * W + x) * 3; return 0.299 * px[i] + 0.587 * px[i + 1] + 0.114 * px[i + 2]; };

// --- whiteboard: largest bright box in the central band ---
// row/col profiles of bright pixels (luma > 170) restricted to the central 60% of x
let rows = new Array(H).fill(0), cols = new Array(W).fill(0);
for (let y = 0; y < H; y++) for (let x = Math.floor(W * .2); x < Math.floor(W * .8); x++)
  if (luma(x, y) > 170) { rows[y]++; cols[x]++; }
const band = (arr, frac) => {
  // largest contiguous run above threshold (gaps <= 4 tolerated) - shadows and
  // stray dark corners must not stretch a surface's box
  const max = Math.max(...arr), th = max * frac;
  let best = [-1, -1], cur = -1, gap = 0, last = -1;
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] > th) {
      if (cur < 0) cur = i;
      last = i; gap = 0;
    } else if (cur >= 0 && ++gap > 4) {
      if (last - cur > best[1] - best[0]) best = [cur, last];
      cur = -1;
    }
  }
  if (cur >= 0 && last - cur > best[1] - best[0]) best = [cur, last];
  return best;
};
const [wbY0, wbY1] = band(rows, .35);
// columns measured only within the whiteboard's rows
cols = new Array(W).fill(0);
for (let y = wbY0; y <= wbY1; y++) for (let x = 0; x < W; x++) if (luma(x, y) > 170) cols[x]++;
const [wbX0, wbX1] = band(cols, .35);

// --- dark boards: near-NEUTRAL dark pixels. The boards are neutral black; the door and
// wood panelling are saturated brown, so chroma (max-min channel) separates them. ---
const isBoardPx = (x, y) => {
  const i = (y * W + x) * 3, r0 = px[i], g0 = px[i + 1], b0 = px[i + 2];
  const mx = Math.max(r0, g0, b0), mn = Math.min(r0, g0, b0);
  return mx < 80 && (mx - mn) < 22;
};
function darkBoard(x0, x1) {
  let r = new Array(H).fill(0), c = new Array(W).fill(0);
  for (let y = Math.floor(H * .16); y < Math.floor(H * .68); y++)
    for (let x = x0; x < x1; x++) if (isBoardPx(x, y)) { r[y]++; c[x]++; }
  const [y0, y1] = band(r, .35), [cx0, cx1] = band(c, .3);
  // top-edge slope: first dark row per column across the box (perspective evidence)
  const tops = [];
  for (let x = cx0; x <= cx1; x += 4) {
    for (let y = Math.floor(H * .16); y < Math.floor(H * .68); y++)
      if (isBoardPx(x, y)) { tops.push([x, y]); break; }
  }
  let slope = 0;
  if (tops.length > 4) {
    const n = tops.length, mx = tops.reduce((s, p) => s + p[0], 0) / n, my = tops.reduce((s, p) => s + p[1], 0) / n;
    slope = tops.reduce((s, p) => s + (p[0] - mx) * (p[1] - my), 0) / tops.reduce((s, p) => s + (p[0] - mx) ** 2, 0);
  }
  return { x0: cx0, x1: cx1, y0, y1, topSlope: +slope.toFixed(4) };
}
const L = darkBoard(0, Math.floor(W * .22));
const R = darkBoard(Math.floor(W * .78), W);

// --- bench front: strongest horizontal luma edge in the center-bottom, then down to ~97% ---
let bestY = 0, bestG = 0;
for (let y = Math.floor(H * .58); y < Math.floor(H * .92); y++) {
  let g = 0;
  for (let x = Math.floor(W * .35); x < Math.floor(W * .65); x += 3)
    g += Math.abs(luma(x, y + 2) - luma(x, y - 2));
  if (g > bestG) { bestG = g; bestY = y; }
}

const f = (v, total) => +(v / total).toFixed(4);
const anchors = {
  schema: 'uni.flagellum.classroom-room-anchors/1.0.0',
  sourceImage: 'room-bg.webp',
  sourceSha256: sha,
  imageSize: { w: W, h: H },
  method: 'measured from pixels by viewer/measure_room_anchors.cjs (ffmpeg->PPM, bright luma>170 for the whiteboard; boards = neutral-dark (max channel<80, chroma<22) to exclude the brown door/wood; largest-contiguous-run banding, center-gradient bench edge). Fractions of image size. tuning.* values are HAND-ADJUSTABLE presentation parameters; re-run the script only when the background image changes.',
  anchors: {
    whiteboard: { x: f(wbX0, W), y: f(wbY0, H), w: f(wbX1 - wbX0, W), h: f(wbY1 - wbY0, H) },
    boardLeft:  { x: f(L.x0, W), y: f(L.y0, H), w: f(L.x1 - L.x0, W), h: f(L.y1 - L.y0, H), topSlope: L.topSlope },
    boardRight: { x: f(R.x0, W), y: f(R.y0, H), w: f(R.x1 - R.x0, W), h: f(R.y1 - R.y0, H), topSlope: R.topSlope },
    benchFront: { x: 0.22, y: f(bestY, H), w: 0.56, h: f(Math.floor(H * .97) - bestY, H), note: 'y measured (tabletop front edge); x/w centered by design' }
  },
  tuning: {
    boardLeft:  { rotateY: 30,  inset: 0.10 },
    boardRight: { rotateY: -30, inset: 0.10 },
    whiteboard: { inset: 0.06 },
    benchFront: { plaqueOffsetY: 0.35 }
  }
};
fs.writeFileSync(OUT, JSON.stringify(anchors, null, 1) + '\n');
console.log('room-anchors.v1.json written; image ' + W + 'x' + H + ' sha ' + sha.slice(0, 12));
console.log('whiteboard', JSON.stringify(anchors.anchors.whiteboard));
console.log('boardLeft ', JSON.stringify(anchors.anchors.boardLeft));
console.log('boardRight', JSON.stringify(anchors.anchors.boardRight));
console.log('benchFront', JSON.stringify(anchors.anchors.benchFront));
