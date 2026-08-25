# Classroom build — resume point (2026-08-20)

**Where this stands when the QA interrupt began.** Plan of record:
`C:\Users\mpolz\.claude\plans\peppy-doodling-dewdrop.md` (approved by the operator 2026-08-20).

## Done and verified (gate `viewer/verify_classroom_assets.cjs` = PASS, 15/15)
1. `viewer/bio_view.cjs` — static routes (`/assets/classroom/`, `/assets/media/`) with flat-segment
   sanitization + single-Range mp4 streaming (206 verified) + `/classroom` + `/api/classroom`.
2. `viewer/render_structure_svg.cjs` — zero-dep mmCIF→SVG: 14 SVGs from the two deposited
   structures (6YSL 1,324 CA · 7E82 13,700 CA), deterministic (two runs byte-identical),
   source sha256 cross-checked against `public/walkthrough-evidence-manifest.v1.json`.
3. Room background via ChatGPT in Chrome (operator-directed), `docs/classroom-assets/room-bg.webp`,
   provenance in `docs/classroom-assets/MANIFEST.json` (truthClass ILLUSTRATION, prompt verbatim).
4. `viewer/extract_timescales.cjs` → `docs/classroom-assets/timescales.v1.json` — 38 rows, values
   read programmatically, 3 rows hand-traced to source (all MATCH), epistemics vocabulary enforced.
5. `docs/classroom.html` at `/classroom` — hero room + hotspots, specimen bench (10 entity parts +
   2 composites + anatomy map + 2 videos), whiteboard (D-L-T with measured rates, B0–B8 ladder,
   statistical-vs-mechanistic finding), frequency wall (38 rows live), mind–body wall
   (BODY MEASURED / MIND NOT_ESTABLISHED / THIRD MIND OPERATOR-HYPOTHESIS + conjecture board).
6. `docs/models.html` — §0 parity map installed (MISNAMED/NEUTERED/ABSENT per layer, blanket a=∅,
   UNSOURCED kernel-constants callout). `docs/architecture.html` — classroom link + UNSOURCED flag.
7. `viewer/verify_classroom_assets.cjs` — the gate, PASS.

## QA interrupt — SERVED and closed (2026-08-20)
Defects found by measurement and fixed, gate re-run PASS: portrait video capped (was 868px);
anatomy label collisions zeroed (bbox test); 7E82 flipped hook-up, verified in SVG bytes
(mean-y hook 116 < rod 247 < MS ring 386); drawer closes on backdrop; no horizontal overflow on
any of the four pages. Committed 6bcb28c + e8fd781.

## Second operator direction — SERVED (2026-08-20): navigation drawn ON the room
"make the navigation appear on the image so it looks drawn on the boards and is clickable."
Done: always-visible labels rendered as part of each surface — marker ink on the whiteboard
(title, underline, subtitle, a small hand-drawn D-L-T sketch), chalk on both dark side boards
set in each board's perspective (rotateY ±30°), a brass plaque on the bench front. All are the
click targets (whole-zone anchors, aria-labels); sizes in container-query units so they scale
with the room; hover brightens. Top nav upgraded from bare links to visible buttons.
Iterated against screenshots three times (tap-line off the board edge; sketch on the bench top;
chalk overhang) — each fixed and re-shot.

## Third operator direction — SERVED (2026-08-20): durable anchors for the room
"black boards need adjusting and this needs to be durable... anchors or some point that allows
better placement and pinning of overlays so it is easy to update."
Done, measured not eyeballed: `viewer/measure_room_anchors.cjs` measures the four surfaces FROM
THE IMAGE PIXELS (whiteboard by brightness; the black boards by neutral-darkness with a chroma
cut that excludes the brown door/wood; bench edge by the strongest horizontal gradient;
largest-contiguous-run banding so shadows cannot stretch a box) and freezes them in
`docs/classroom-assets/room-anchors.v1.json`, BOUND to the background by sha256. The page
positions every overlay from that file; `?debug=anchors` draws the measured boxes for the eye.
TO ADJUST PLACEMENT: edit room-anchors.v1.json (anchors = measured geometry; tuning = hand
parameters: per-board rotateY, insets, plaque offset). TO CHANGE THE BACKGROUND: replace
room-bg.webp, update MANIFEST.json, re-run measure_room_anchors.cjs — the gate FAILS on a
sha mismatch until you do. Gate extended with the anchors contract; PASS.

## To resume — the remaining plan
1. `node viewer/verify_classroom_assets.cjs` must PASS (last run: PASS 15/15).
2. Operator walk-through of /classroom — the eye test is his (M8). His verdict may add tuning.
3. Standing open items displayed in-room, awaiting HIS rulings (agents must not resolve):
   layer-naming ruling · kernel rewiring to sourced constants · Antani workbook acquisition
   (the estate's first candidate two-rung join — recommended FIRST door) · Johnson/Singh DOI
   conflict.
4. "Stable and ready for more lab work" (his stated goal): the surfaces are committed and
   gate-covered; the science next-acts remain the acquisition doors above plus the two
   no-new-data acts already specified on /architecture: re-run the frozen competition to a NEW
   path (never bare — phase-b overwrite hazard), and the state-pooled ablation that would let
   occupancy influence a verdict for the first time.

## Known black-screen episode, accounted
Mid-scroll screenshots without waits captured unpainted compositor frames on the 13,000-px page.
Re-walked the identical path with 2 s waits: every frame painted; DOM complete throughout; no
console errors. Not a page defect — but it is exactly why the QA pass below re-checks by
measurement, not by trust.
