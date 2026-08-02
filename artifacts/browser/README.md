# Browser verification evidence

Generated from the running local v0.3 application on 2026-07-19 with
`agent-browser` 0.32.2. These are verification captures, not biological
evidence.

| Capture | Viewport | Result |
|---|---:|---|
| `desktop.png` | 1440 x 1000 | First viewport shows licensed Mears microscopy beside the CPU Canvas2D cell reconstruction |
| `tablet-768.png` | 768 x 1000 | No horizontal document overflow; biological canvas 525 x 455 CSS px |
| `mobile-320-fixed.png` | 320 x 900 | No horizontal document overflow; biological canvas 297 x 360 CSS px; no walkthrough control smaller than 42 x 42 CSS px |

`mobile-320.png` is the retained pre-fix capture. Its matching automated check
reported a 376 px document width in a 320 px viewport. It is kept as adverse UI
evidence; `mobile-320-fixed.png` and the repeat measurement establish the fix.

Additional automated browser evidence:

- source video decoded with no media error at its pinned 256 x 376 pixels;
- framework error-overlay check returned `OK`;
- browser page-error list was empty;
- all thirteen guided steps were reached with keyboard focus plus `Enter`;
- reduced-motion media query was active when emulated and the biological stage
  retained a CPU `CanvasRenderingContext2D`;
- a separate visible human pass saved thirteen observer records and reported
  `EXPORT -> RE-IMPORT PASS`, with the manifest and hashes preserved.
