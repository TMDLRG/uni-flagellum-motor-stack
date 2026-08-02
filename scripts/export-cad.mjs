import { mkdir, writeFile } from "node:fs/promises";
import { createCadManifest, openScadFromManifest } from "../lib/cad.js";

const manifest = createCadManifest({ moduleMm: 2, thicknessMm: 6, clearanceMm: 0.28 });
await mkdir(new URL("../cad/", import.meta.url), { recursive: true });
await writeFile(new URL("../cad/uni-flagellum-educational-model.json", import.meta.url), `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
await writeFile(new URL("../cad/uni-flagellum-educational-model.scad", import.meta.url), openScadFromManifest(manifest), "utf8");

console.log(`Exported ${manifest.parts.length} parts under ${manifest.schema}.`);
