# THE LABORATORY PLAN

**The single plan of record for building the real UNI laboratory.**
Drafted 2026-07-29 from six independent measuring lenses across three trees, then revised twice
against three adversarial audits.

**This file replaces its own first draft**, committed at `4f6485e` at this same path on 2026-07-28.
That draft is retrievable with `git show 4f6485e:docs/THE-LABORATORY-PLAN.md`. **Its section 2 is
refuted below** — it declared a conflict between the plan of record's offline clause and the
operator's architecture. There is no conflict; there are two modes and a door. Three of its factual
claims were also measured false and are corrected here: the flagellum **is** deployed on the chip;
`app/globals.css` in MAIN is 544 lines with no dead truth channel; and chip integration does **not**
turn the test suite red.

> **THIS DOCUMENT IS NOT YET FINISHED, AND THE UNFINISHED PARTS ARE NAMED.** Three audit passes have
> run. The architecture and the measurements survived all three — the second auditor's words were
> *"this plan does not fabricate"*, after independently re-deriving about twenty-five of its numbers.
> What has **not** converged is internal consistency: see **§10.4b** and **§10.4c**, which record, in
> the auditors' own words, every contradiction still standing. The largest are listed in this file's
> commit message. **Do not treat an unresolved item as settled because the surrounding prose is
> confident.**
>
> **A process warning about this file.** During the third pass two agents edited it *while auditing
> it*, in parallel, and it was untracked at the time — it grew from 455,213 to 473,952 bytes mid-run.
> Line numbers cited inside §10.4b and §10.4c therefore refer to a revision that no longer exists and
> cannot be retrieved. That is the same failure this document exists to prevent, committed against
> the document itself, by the agent that wrote it. It is now under version control precisely so that
> it cannot happen again silently.

---

## THE THREE THINGS TO SAY BEFORE ANYTHING ELSE

**One. The laboratory is already deployed on the chip, it is PROMOTED, it answers over TLS, and the
scientific equation in the promoted bytes is wrong.**
`/opt/uni/flagellum/prod/PROMOTE_STATUS` reads `PROMOTED` (9 bytes, sha256
`537f3f73efdab7fa1fb379f4f99f9bde21c4a0aa697bb5712ef1f5e53b6c5b46`).
`/etc/uni/uni-flag-workbench.conf` publishes `workbench.uni-lab.solwright.com` on 443 to
`127.0.0.1:8791`; a `curl --ssl-no-revoke` from this box returns `307 -> /math-workbench -> 200`
with **no authentication**. The file `/opt/uni/flagellum/prod/src/lib/uni-motor.js`
hashes `852b38d14e1de9e1baae9bda7c37fb2426911fb1b04b4f594d026373d4b50313` and contains
`efe = risk + ambiguity - informationGain + effort`, which expands to
`KL[q(o)||C] + 2*ambiguity + effort` — ambiguity counted twice
(`UNI-FLAGELLUM/lib/uni-motor.js:318-328`). Three lenses read those bytes off the chip
independently. Worksheet 5 asks a reader to hand-calculate a quantity the tool does not produce.

> **Two corrections to this paragraph, both made after it was first written, both material.**
> **(a) "on the public internet" is WITHDRAWN.** Re-measured 2026-07-29: plain `curl` from this box
> **fails** (exit 35, schannel `CRYPT_E_NO_REVOCATION_CHECK`); `--ssl-no-revoke` succeeds, and
> `remote_ip` is **`10.190.245.121`** — the chip's **private RFC1918** LAN address, resolved by the
> LAN DNS server `Linksys00425` at `10.190.245.188`. **Whether that name is reachable from outside
> this LAN is NOT ESTABLISHED**, and no probe from this box can settle it.
> **(b) "it is serving" is narrowed to "it answers".** The vhost answers; whether a *process* is
> serving the promoted `/opt/uni/flagellum/prod/src` bytes specifically is **NOT ESTABLISHED** — see
> **THE CHIP WAS PROBED**, below. **DEPLOYED and PROMOTED are certain. SERVING is not.**

**Two. The deployment that is running cannot be rebuilt by anybody.** There is no deploy script,
no quadlet unit, no Containerfile, no ssh transport and no CI for the flagellum in any of the
three trees. No commit, no receipt and no ledger entry anywhere names `/opt/uni/flagellum`,
`uni-flag-prod` or `uni-flag-test`. The deployed tree has **no `.git`**, so every staleness
detector in the repository is structurally unable to reach it. A rollback today is not possible;
a redeploy today is a guess.

**Three. Production dependency risk went backwards with no code change.**
`npm audit --omit=dev --audit-level=moderate` reports **3 HIGH** today — and, re-measured this
session, they are on **three different packages**, not one: **`next`** (middleware/proxy bypass,
Server Actions DoS, SSRF), **`postcss`** (arbitrary file read and path traversal via
`sourceMappingURL`), and **`sharp`** (libvips CVE-2026-33327/33328/35590/35591). That is against
**0 production vulnerabilities** recorded eight days ago at
`docs/audit/PHASE-E-WORKBENCH-AUDIT.md:36`. Total went 13 -> 19, high 8 -> 14. **All three advertise
the same fix, `next@16.2.12`, `isSemVerMajor: false`** — outside the declared range, so the
correction is itself a release-scope decision, not a patch. *(A previous revision attributed all
three to `sharp`; a reader would have planned a `sharp` bump and never learned that two of the three
are `next` and `postcss`.)*

Everything below is built so that these three facts become impossible to have again.

---

## THE CHIP WAS PROBED

**This is not recalled and it is not inferred. Every line below was produced this session by direct
live probe of the chip over the `uni-lab` MCP, using read-only tools only.**

**THE MOST IMPORTANT SENTENCE IN THIS DOCUMENT: the defective expected free energy is the PROMOTED
artifact on the chip.** Not a draft of it, not a branch that might get promoted — the file sitting
in `/opt/uni/flagellum/prod/src/lib/uni-motor.js`, under a `PROMOTE_STATUS` that reads `PROMOTED`.

| measured | value |
|---|---|
| the box | hostname `uni-lab`, uptime **13 days 13:39**, load average **7.62**, **39 GiB** RAM |
| its addresses | LAN `eno4` **10.190.245.121** · mesh `wg0` **10.13.13.1** · tailscale **100.100.188.48** |
| `/opt/uni/flagellum/` | exactly two entries: `test/` and `prod/` |
| `/opt/uni/flagellum/prod/` | `PROMOTE_STATUS` (9 B) and `src/` |
| `PROMOTE_STATUS` content | exactly `PROMOTED` + newline; sha256 `537f3f73efdab7fa1fb379f4f99f9bde21c4a0aa697bb5712ef1f5e53b6c5b46` |
| `/opt/uni/flagellum/prod/src/` | a full Next.js tree — `app/ lib/ tests/ docs/ experiments/ audits/ scripts/ public/ node_modules/ package.json next.config.ts tsconfig.json vite.config.ts worker/ drizzle/ cad/ db/ dist/ build/ artifacts/ examples/ CLAUDE.md README.md` |
| prod `lib/uni-motor.js` | sha256 `852b38d14e1de9e1baae9bda7c37fb2426911fb1b04b4f594d026373d4b50313` — **byte-identical to the local copy in BOTH local trees** |

**Read on the chip's own file, verbatim:**

```js
const informationGain = entropy(qOutcome) - ambiguity;
const effort = policy === "TUMBLE" ? 0.07 : 0.02;
const efe = risk + ambiguity - informationGain + effort;
```

Substituting the second line into the third gives
`efe = KL(qOutcome ‖ preferences) + 2·ambiguity + effort`. **The ambiguity term is counted twice.**
And it does not cancel between the two policies: `ambiguity` is computed from `qState`, which comes
from the **policy's own** transition matrix (`bRun` vs `bTumble` in `transitionPrior`). So the
doubling distorts the **difference** `G(RUN) − G(TUMBLE)`, and that difference is exactly what
`softmax([-4*run.efe, -4*tumble.efe])` turns into the action.

> **The algebra above is VERIFIED by reading the promoted file. The audit's magnitudes — 60.7–62.5%
> inflation of `G`, 6.5× on `G(RUN) − G(TUMBLE)` — were NOT re-executed this session and remain
> UNVERIFIED.** They are carried in section 10 and nowhere else.

### What was NOT established, and must not be claimed

- **Whether a PROCESS is currently serving those bytes.** `os_systemctl_status` **correctly refused**
  the unit name `flagellum-prod.service` as outside the MCP allowlist (evidence class `Sec`), and
  `podman_ps` returned a truncated tail showing `aion-softphone-1002`, `aion-admin`, `swu-leads`,
  `uni-glass-intakes`, `uni-dns`, `wildbill-funnel`, `wildbill-funnel-uat` and **no flagellum
  container**. **DEPLOYED = certain. PROMOTED = certain. SERVING = NOT ESTABLISHED.**
- **Whether the built `dist/` on the chip contains the defect.** The *source* was hashed. The bundle
  was not.
- **Whether the promotion transport copies `app/` wholesale.** `/opt/uni/flagellum/prod/src/app/`
  was not enumerated this session.

### And the registry is stale, not silent

`viewer/infra_registry.json` holds **21 services across 4 boxes** (`uni-lab`, `thinker`, `node2`,
`tab`). A substring search returns **FALSE for every one of**: `8790`, `8791`, `flagellum`,
`Flagellum`, `8102`, `8103`, `5858`, `8104`. The registry's `_lan_dynamic_law` is confirmed — the
DHCP lease did move to `.121`. **So the registry is stale with respect to the flagellum deployment.
It is not evidence that the deployment is absent.**

---

## FOUR THINGS THE AGENT TOLD THE OPERATOR THAT WERE WRONG

**Said first, in one line each, before anything is built on top of them.**

1. **"The flagellum is not on the chip."** **FALSE.** It is deployed at `/opt/uni/flagellum/prod/`
   and its `PROMOTE_STATUS` reads `PROMOTED`; the promoted `lib/uni-motor.js` is byte-identical to
   both local copies.
2. **"The truth-signal colour channel is dead on the served page."** **FALSE where it was said.**
   MAIN's `app/globals.css` (544 lines) uses 18 `var()` names and declares 18; the only two
   undeclared are `--font-geist-sans` / `--font-geist-mono`, injected by `next/font` via
   `app/layout.tsx`. **MAIN has no dead truth channel.** The dead channel is **STALE-only** —
   `UNI-FLAGELLUM-math-workbench/app/globals.css` (702 lines) uses 23 and declares 18, leaving
   `--cyan --failure --gold --void` plus the same two font vars. **It arrives in MAIN only when the
   workbench is ported, which is W3.**
3. **"Chip integration turns the test suite red."** **FALSE.**
   `tests/walkthrough.test.mjs:114-122` is a single test named *"walkthrough application contains no
   LLM or GPU runtime"*. It reads **exactly three files** — `biological-stage.tsx`,
   `guided-teacher.tsx`, `living-science-walkthrough.tsx` — joins them, and asserts `doesNotMatch`
   for WebGL/WebGPU/three, for `openai|anthropic|gemini|languageModel|chatCompletion|generateText`,
   and at `:119` for `fetch`/`XMLHttpRequest`/`WebSocket`. **It is not repository-wide.** An
   observation channel added anywhere outside those three files does **not** turn the suite red.
   The test is already drawing a kernel/shell boundary — **around three files instead of a
   directory** — which is precisely what §0 replaces with a boundary a build enforces.
4. **"The infrastructure registry proves the flagellum is not deployed."** **FALSE.** The registry
   is stale: 21 services, and no substring match for `flagellum`, `8790`, `8791`, `8102`, `8103`,
   `5858` or `8104`. Absence from a stale registry is not absence from the box.

**And a fifth, about this document's own predecessor.** The FIRST DRAFT of this plan, committed at
`4f6485e` as `UNI-FLAGELLUM/docs/THE-LABORATORY-PLAN.md`, is **superseded**. Three of its factual
claims were checked and all three were wrong (the flagellum is on the chip; MAIN's `globals.css` is
544 lines, not 702; chip integration does not turn the suite red). **It must carry a RETRACTED
banner at its head naming this document as its replacement** — that is a work item in **W0**, and it
is written into W0's acceptance criteria in §7.3.

**And a sixth, which this document told the operator itself, one revision ago.** A previous pass of
this plan stood here and claimed that `lib/uni-motor.js`'s `modelSnapshot()` calling
`new Date().toISOString()` was *"a **fourth** ambient clock, beyond the two this plan names in
`walkthrough.js` and the one at `uni-motor.js:408`."* **RETRACTED. It is the clock at
`uni-motor.js:408`, counted twice.** Measured this session: `grep -n "Date\.now()\|new Date("
lib/uni-motor.js` returns exactly one hit, `408: capturedAt: new Date().toISOString(),`, and `:405`
is `export function modelSnapshot(system, controls) {` — the same line, inside the named function.
`grep -rn "Date\.now()\|performance\.now()\|new Date()" lib/` over MAIN returns exactly **three**
ambient clocks in the kernel: `uni-motor.js:408`, `walkthrough.js:385`, `walkthrough.js:408`. **The
coincidence that `walkthrough.js` also carries one at `:408` is what generated the error.** §2.1's
purity table and §9.2 both had it right all along, and the fabricated line contradicted them from
the head of the same document. It is recorded rather than deleted, and it is in §3.9's casebook.
**Three clocks, not four; all three sealed in W2.**

---

# 0. THE SURFACE DECISION

> **Numbering note.** Section 0 is **additive**. Nothing below it renumbers. The same convention is
> used once more, for **§3A THE SHELL**, so that six authors' cross-references all remain valid.

## In plain words

**The plan as drafted builds the laboratory twice, in two languages, in two repositories, and never
says so.** Section 4 puts the chalkboard, the equation cards, the disclosure ladder and the twelve
worksheets in MAIN's React app. Section 5 opens by insisting the opposite — *"Each wing below is a
new floor in **that** building, served by **that** server, gated by **that** runner. Nothing in this
section proposes a second surface"* — and then specifies every wing in `UNI.Minecraft/viewer/lab/`,
which I measured this session as 13 `.cjs` + 6 `.html`, 5,326 lines, **no React and no build step**.
The same eleven-model catalog, the same stepping loop and the same twelve worksheets are specified
in both. Whichever one you looked at, you would believe you were looking at the lab.

**The decision: ONE application, in MAIN, with two wings.** `app/(product)/` is the thing that gets
promoted to the chip. `app/(lab)/` is the laboratory, and it is never promoted. A gate fails the
release if any laboratory route survives into the release artifact.

**The one reason that matters: a boundary you cannot check is not a boundary.** Section 1 says
*"The UI and runtime could never be the same."* With two labs in two repositories, that sentence is
a promise someone has to keep by remembering. With one application and two wings, it is a gate that
runs, goes red, and names the file that broke it. That is the whole reason. Everything else — less
code, one place to look, no drift between two catalogs — is a bonus.

**And it costs nothing to try.** I searched the entire repository for code that depends on where
those files sit. **Exactly one line breaks.**

---

## 0.1 The feasibility verdict, tested against disk

I did not take the recommendation on trust. Four things had to be true, and I checked each one.

**Does this stack even support route groups?** This is not a Next.js question. `package.json:9-11`
runs `vinext dev` / `vinext build` / `vinext start` — **the `next` CLI is never invoked**.
`next` 16.2.6 is a dependency; `vinext` 0.0.50 is the thing that actually builds and serves. So I
read vinext's router rather than Next's docs.

It supports them. `node_modules/vinext/dist/routing/app-route-graph.js:1018-1023`:

```js
function isInvisibleSegment(segment) {
	if (segment === ".") return true;
	if (segment.startsWith("(") && segment.endsWith(")")) return true;
	if (segment.startsWith("@")) return true;
	return false;
}
```

and `routing/app-router.js:14` documents it outright: `app/(group)/page.tsx -> / (route groups are
transparent)`. The STALE worktree already proves nested app routes work in this exact stack —
`app/math-workbench/page.tsx` serves `/math-workbench`. **VERDICT: feasible, measured, not novel.**

**What is the current shape?** `find app -type d` returns only `app`. The directory is **flat: 11
files, zero subdirectories**, and there is no route group anywhere in either tree. So this is a first
move, not a retrofit into an existing convention.

**What breaks when `page.tsx` moves?** One line. `tests/walkthrough.test.mjs:116`:

```js
const source = (await Promise.all(files.map((file) => readFile(join(root, "app", file), "utf8")))).join("\n");
```

That hard-codes `app/<file>` for `biological-stage.tsx`, `guided-teacher.tsx`,
`living-science-walkthrough.tsx`. Move them and it fails with ENOENT. A repo-wide grep for the
literal `app/` across every `.mjs`, `.cjs`, `.js`, `.ts`, `.tsx`, `.json`, `.py` and `.yml` outside
`node_modules`, `dist`, `.next` and `build` returned **no other hit**. `eslint.config.mjs` names no
app paths. No script, no gate, no manifest references them.

`tests/rendered-html.test.mjs` **survives untouched**, and this is the load-bearing detail: it
fetches `http://localhost/` from the built worker (`:5,9`) and asserts only on URL and rendered text.
Route groups are URL-transparent, so `/` is still `/`.

**And the one that failed.** Here the recommendation as handed to me is **wrong**, and I am not going
to write it up as given.

> *"the release pipeline promotes ONLY the product group"* — route groups cannot do this.

Route groups affect **URLs only**. Every route in `app/` compiles into **one** Cloudflare Worker:
`worker/index.ts:43` (`return handler.fetch(request, env, ctx);` — `:42` is the closing brace above
it) hands every non-image request to `vinext/server/app-router-entry`, a single
handler, bundled by `@cloudflare/vite-plugin` into `dist/`. A laboratory built as a plain route group
ships to the chip **in its entirety**, chip-observation channel and all. The decision would have been
a slogan wearing a directory name — precisely the failure it was proposed to fix.

**The repair is real and I measured it.** vinext honours `pageExtensions` end-to-end: normalized at
`config/next-config.js:286,303`, carried through `cli.js:285`, consumed by the app router at
`index.js:789` and by the prerenderer, build report and route-rule emitter. And
`routing/file-matcher.js:26-36` builds the page regex as `` (^(page|route)|[\\/](page|route))\.(?:<exts>)$ `` — the leaf pattern at `:33` interpolates `names`, and for the page matcher (`:35`) `names` is `(page|route)`, never the bare `page` an earlier revision wrote here — so a
file named **`page.lab.tsx` is invisible under the default `[tsx, ts, jsx, js]`** and becomes a page
**only** when `"lab.tsx"` is added to the list. Compound extensions are legal —
`normalizePageExtensions` strips leading dots and nothing else.

So: **route groups give the URLs and the human clarity; `pageExtensions` gives the exclusion.** You
need both. The recommendation survives with that amendment, and it is stronger for it, because the
exclusion now happens in the route graph — the lab is not stripped from the bundle afterwards, it
never enters it.

---

## 0.2 The decision, stated once

> **There is one laboratory application. It lives in `UNI-FLAGELLUM/app/`. It has two wings.**
>
> **`app/(product)/`** — the living-science walkthrough and the biological stage. CPU-only, no
> network, self-contained. This is what is promoted to `/opt/uni/flagellum/prod/src`. Every routable
> file here is a plain `page.tsx` / `layout.tsx`.
>
> **`app/(lab)/`** — the map, the chalkboard, the proofs, the wings and their benches, the intake, the
> casebook, the airlock desk, the compare view, the stepper. *(The classroom is **not** here: §3.6
> folds it into `/lab/l5` chip-side, and §7.4 records that as `NOT_SCHEDULED`.)* **Never promoted.** This is the **only**
> place the chip-observation channel may live. Every routable file here is named `*.lab.tsx` /
> `*.lab.ts`.
>
> **A release build cannot see the laboratory.** `next.config.ts` sets `pageExtensions` from
> `UNI_SURFACE`; the lab extensions are absent from a release build, so lab pages are not routes,
> their layouts are unreachable, and nothing they import enters the bundle.
>
> **`UNI.Minecraft/viewer/lab/`, TRACK, Gaia and HUD stop competing to be the face. They become data
> sources the laboratory reads.**

---

## 0.3 The exact file moves

All 11 files in MAIN `app/` are accounted for. Line counts measured this session with `wc -l`,
blanks included.

**To `app/(product)/` — 8 files, 2,214 lines. Pure `git mv`; no content edit.**

| From | To | Lines |
|---|---|---|
| `app/page.tsx` | `app/(product)/page.tsx` | 12 |
| `app/uni-flagellum-lab.tsx` | `app/(product)/uni-flagellum-lab.tsx` | 880 |
| `app/living-science-walkthrough.tsx` | `app/(product)/living-science-walkthrough.tsx` | 337 |
| `app/biological-stage.tsx` | `app/(product)/biological-stage.tsx` | 319 |
| `app/observed-experiment-panel.tsx` | `app/(product)/observed-experiment-panel.tsx` | 232 |
| `app/cross-study-parity-panel.tsx` | `app/(product)/cross-study-parity-panel.tsx` | 187 |
| `app/science-gates-panel.tsx` | `app/(product)/science-gates-panel.tsx` | 130 |
| `app/guided-teacher.tsx` | `app/(product)/guided-teacher.tsx` | 117 |

They all move together, so every relative import between them (`page.tsx:2` imports
`./uni-flagellum-lab`) stays correct with **no edit**. **`/` keeps serving the product**, so every
one of the twelve assertions in `tests/rendered-html.test.mjs:20-31` stays at its current address —
see §3A.10, which is written against this fact.

**Stays at `app/` root — 2 files, 564 lines.** `layout.tsx` (20) is the root layout: it owns
`<html>`/`<body>` and the `next/font` variables, and both wings nest inside it. `globals.css` (544)
stays beside it because `layout.tsx:3` imports `./globals.css`. Do not move either; moving them is
what would turn a two-line change into a debugging session. **Note the constraint this puts on
§3A.5: the laboratory FRAME may not live in the root layout, because the root layout is shared with
the product. It lives in `app/(lab)/layout.lab.tsx`.**

**To `app/(lab)/` — 1 file, 86 lines.** `app/chatgpt-auth.ts` → `app/(lab)/chatgpt-auth.ts`.
**See §0.6 — this is an adverse finding, not a tidy-up.**

**New files created — and EVERY ROUTE HAS AN OWNER.** The previous draft of this table declared ten
routes and §7 scheduled only some of them; two of the ten contradicted other sections outright. The
OWNS column below is now part of the table, and **§7.4 holds it to §7 mechanically.** A row with no
owner is a route nobody is building.

| New file | Route | What it is | OWNS |
|---|---|---|---|
| `app/(lab)/layout.lab.tsx` | — | Lab chrome: **THE FRAME** (§3A.5), the rail linking every wing. `.lab.tsx` so it is not even recognised as a layout in a release build. | **W2b** |
| `app/(lab)/lab-frame.tsx` | — | The frame component itself (§3A.5). Not `page.*`, so never a route — see the measured page regex below. | **W2b** |
| `app/(lab)/lab/page.lab.tsx` | `/lab` | The laboratory front door and **THE MAP** (§3A.4) | **W2b** |
| `app/(lab)/lab/wing/[wing]/page.lab.tsx` | `/lab/wing/<wing>` | **The one wing route.** Manifest-driven, `generateStaticParams` from `lib/shell/wings.js`. Every bench is one of these (§0.9 decision 2). | **W2b** |
| `app/(lab)/lab/wing/[wing]/[room]/page.lab.tsx` | `/lab/wing/<wing>/<room>` | The second and last level. There is no third. | **W2b** |
| `app/(lab)/lab/wing/[wing]/layout.lab.tsx` | — | THE WING FRAME — tri-mode banner, offline badge (§7.1a W22) | **W22** |
| `app/(lab)/lab/chalkboard/page.lab.tsx` | `/lab/chalkboard` | §4 lands here. **The chalkboard is LABORATORY, not product** (§0.9 decision 3). | **W3** |
| `app/(lab)/lab/proof/page.lab.tsx` | `/lab/proof` | The derivation index (§4.6) | **W16** |
| `app/(lab)/lab/proof/[id]/page.lab.tsx` | `/lab/proof/<id>` | One derivation, rendered (§4.6) | **W16** |
| `app/(lab)/lab/stepper/page.lab.tsx` | `/lab/stepper` | §4.10, the tick tape. **§4.10 already cited this row; the row did not exist.** | **W31** |
| `app/(lab)/lab/intake/page.lab.tsx` | `/lab/intake` | §3.4 | **W18** |
| `app/(lab)/lab/casebook/page.lab.tsx` | `/lab/casebook` | §3.9, the LLM casebook | **W17** |
| `app/(lab)/lab/airlock/page.lab.tsx` | `/lab/airlock` | §3.8 | **W19** |
| `app/(lab)/lab/compare/page.lab.tsx` | `/lab/compare` | §2, offline/online compare | **W11** |
| `app/(lab)/api/chip/route.lab.ts` | `/api/chip` | **The single declared chip-observation channel.** The only file in either wing permitted to name a chip host or port. | **W9** |
| `scripts/verify-release-excludes-lab.mjs` | — | The gate (§0.4) | **W2a** |
| `UNI.Minecraft/viewer/verify_release_excludes_lab.cjs` | — | Registry shim (§0.4) | **W2a** |

**Two rows the previous draft declared and this pass WITHDRAWS, each with its reason:**

| withdrawn row | why |
|---|---|
| `app/(lab)/lab/bench/page.lab.tsx` | **Contradicted `/lab/wing/[wing]` in the same table.** §0.9 decision 2 keeps the manifest-driven route; a bench is a kind of room. |
| `app/(lab)/lab/classroom/page.lab.tsx` | **`NOT_SCHEDULED`, and §3.6 says so in its own heading:** *"THE DESK BECOMES A CLASSROOM — fold into L5, do not build a new room."* The classroom is `/lab/l5` on `127.0.0.1:8103`, reached as a portal. It is correctly absent from §3A.4's `STANDING` manifest, and under §3A.10 criterion 6 a route file with no manifest entry **fails**, so this row would have turned the shell's own suite red. |

**Why a non-`page` file in `app/(lab)/` can never become a route — measured, not assumed.**
`node_modules/vinext/dist/routing/file-matcher.js:35` builds the app-router page regex as
`createLeafPattern(["page", "route"])`, and `:31-33` expands that to
`(^(page|route)|[\\/](page|route))\.(?:<ext>|…)$`. **Only a file whose basename is `page` or
`route` is a route**, at any `pageExtensions` setting. So `lab-frame.tsx`, `equation-card.tsx`,
`worksheet.tsx` and every per-wing panel module are unroutable in **both** builds by construction —
which is why they are safe to keep beside the routes they serve.

No collision: `app/(product)/page.tsx` resolves to `/`, `app/(lab)/lab/page.lab.tsx` resolves to
`/lab`. vinext throws `You cannot have two routes that resolve to the same path`
(`routing/route-validation.js:94`) if that ever stops being true — the collision is caught by the
build, not by review.

**The config edit — `next.config.ts`, currently an empty object at `:3-5`:**

```ts
import type { NextConfig } from "next";

// The laboratory is compiled ONLY when UNI_SURFACE=lab.
// A release build never sees a *.lab.tsx file, so lab routes are not in the
// route graph, their layouts are unreachable, and nothing they import is bundled.
const LAB = process.env.UNI_SURFACE === "lab";

const nextConfig: NextConfig = {
  pageExtensions: LAB
    ? ["lab.tsx", "lab.ts", "tsx", "ts", "jsx", "js"]
    : ["tsx", "ts", "jsx", "js"],
};

export default nextConfig;
```

**`package.json` scripts** gain `build:release` and `build:lab`. Note `npm test` at `:12` already
runs `npm run build` mid-suite — leave `build` pointing at the release build so the existing suite
keeps testing the shipped thing. **Windows caveat, unresolved:** the local shell is PowerShell, where
`UNI_SURFACE=lab vinext build` is POSIX syntax and **does not set the variable**. Use `cross-env` or
an equivalent, and settle it when `package.json` is actually edited — this was not tested.

**The one edit to an existing test.** `tests/walkthrough.test.mjs:116` — change
`join(root, "app", file)` to `join(root, "app", "(product)", file)`. That is the entire breakage
surface.

---

## 0.4 THE RELEASE-EXCLUSION GATE

**Named file:** `UNI-FLAGELLUM/scripts/verify-release-excludes-lab.mjs`
**Registry shim:** `UNI.Minecraft/viewer/verify_release_excludes_lab.cjs`

A shim is required, and I checked why rather than assuming. All 28 entries in
`UNI.Minecraft/viewer/gate_registry.json` have `file` paths of the form `viewer/**.cjs` relative to
the UNI.Minecraft root. **No registry entry has ever pointed into the MAIN tree.** Rather than invent
a cross-tree path convention inside a gate about boundaries, the shim spawns the MAIN script and
forwards its exit code.

Registry entry — matching the measured schema (`id`, `file`, `ci` and `gate_row` on **all 28**;
`timeout_ms` on **1 of 28** and `external_needs` on **3 of 28**, both optional — re-measured this
session, and an earlier revision called the five-key form "the schema exactly"), and
using a **slug**, because the registry has never used F-numbers:

```json
{
  "id": "release-excludes-lab",
  "file": "viewer/verify_release_excludes_lab.cjs",
  "ci": true,
  "gate_row": "release-excludes-lab-boundary",
  "timeout_ms": 600000
}
```

> ### §0.9 decision 4 rewrote this gate. What the previous draft specified, and why it was vacuous.
>
> The draft derived the lab route list **by scanning `app/(lab)/**/page.lab.tsx`** and asserted each
> such route is not `200` in the release. **That is a source regex wearing a behavioural name, and it
> has a hole the size of the whole chalkboard:** a laboratory surface authored at a *product* path —
> which is exactly where §4 put the chalkboard, at `app/math-workbench/` — is invisible to the scan,
> so the gate goes **GREEN with all five assertions satisfied while the laboratory ships**. The scan
> can only ever ask about routes that already obey the rule. **The direction of the assertion was
> backwards, and reversing it is the fix.**

**What it reads.** Two built artifacts and the route manifest each one emits. **Not one line of
`app/` is read.**

1. `UNI_SURFACE` unset → `npm run build:release -- --prerender-all`
2. `UNI_SURFACE=lab` → `npm run build:lab -- --prerender-all`

**THE EMITTED ROUTE MANIFEST — found on disk this session, and here is exactly where.**
`node_modules/vinext/dist/build/run-prerender.js:83` sets `manifestDir = path.join(root,"dist","server")`
and `:176-180` writes into it; `build/prerender.js:789-816` (`writePrerenderIndex`) gives its shape:

```jsonc
// dist/server/vinext-prerender.json
{ "buildId": "…", "trailingSlash": false,
  "routes": [ { "route": "/", "status": "rendered", "router": "app", "path": "…" },
              { "route": "/x", "status": "skipped", "reason": "…" } ] }
```

It lands **beside `dist/server/index.js`** — the very file `tests/rendered-html.test.mjs:5` already
imports. **The measured caveat, stated because it changes the gate's build command:**
`cli.js:268-269` runs the prerender pass only `if (parsed.prerenderAll || resolvedNextConfig.output === "export")`,
so a plain `vinext build` **does not emit this file**. The gate therefore passes `--prerender-all`
on its own two builds. **That flag was not executed this session** — see the smoke item at the end of
§0.8, which now covers it too.

**What it asserts. Six assertions, and assertion 4 now runs in the opposite direction.**

1. **Both manifests exist and are non-empty.** `dist/server/vinext-prerender.json` parses and
   `routes.length > 0` for **both** builds. Without this, a build that emitted nothing passes
   everything downstream trivially. *(If either manifest is absent — because `--prerender-all` did
   not take on this project — the gate exits **1 with `MANIFEST_ABSENT`** and falls to §0.4a. It
   never silently degrades to a source scan.)*
2. **The release build is real.** `GET /` on the imported worker returns `200` and the body matches
   `/UNI–FLAGELLUM/`.
3. **The lab build is real.** `R_lab \ R_release` is **non-empty**, and **every** route in it
   returns `200` from the lab worker. You cannot satisfy this gate by never building the laboratory.
4. **THE ASSERTION, INVERTED — this is the one that closes the hole. It is SET EQUALITY, not
   containment.** **`R_release` === `PRODUCT_ROUTES`**, the frozen product route set committed at
   `experiments/product-routes.v1.json`, compared as sorted sets and reported as **two named
   differences**: `emitted_but_undeclared` and `declared_but_not_emitted`. **Either being non-empty
   is RED, and the message lists the routes.**
   - **`emitted_but_undeclared` is the hole this closes.** A laboratory page authored at *any* path
     — product or lab, `page.tsx` or `page.lab.tsx` — emits a route, that route is not in the frozen
     set, and the gate goes red naming it. The gate never asks *"is this file laboratory?"*, a
     question about source that a regex answers badly; it asks *"did the release emit a route nobody
     declared?"*, which is a question the **build** answers.
   - **`declared_but_not_emitted` is why this is equality and not `⊆`.** Under containment, adding a
     route to `PRODUCT_ROUTES` that does not exist would pass — so a builder could widen the frozen
     set *in advance*, land the leak in a later commit, and the gate would be green for both. **That
     is mutation X3, and containment does not catch it.** Equality does.
   > **The frozen set is not new machinery.** It is the idiom §7.3 **W12** already uses for
   > `experiments/compare-tolerance.v1.json` — *"`tolerance-is-frozen.test.mjs` refuses a loosened
   > budget against `git show HEAD~1:…`"*. Same shape, same enforcement: changing `PRODUCT_ROUTES`
   > is a visible reviewable edit **in the same commit as the route**, never a side effect and never
   > in advance.
5. **The laboratory contains the product.** **`PRODUCT_ROUTES` ⊆ `R_lab`** — every route the
   release serves is also served by the lab build, and each returns `200` from the lab worker.
   This is not true by construction and it fails for a real reason: the lab build sets
   `pageExtensions` to a **superset**, so if adding `lab.tsx` ever shadowed or displaced a product
   page, the map would be standing on a laboratory whose product wing no longer renders. *(An
   earlier version of this list had assertion 5 asserting `R_release ∩ (R_lab \ R_release) = ∅`,
   which is **true by the definition of set difference** and could never fail. It was a vacuous
   assertion inside the anti-vacuity gate, and it is replaced rather than annotated.)*
6. **Secondary, belt-and-braces:** the release bundle bytes contain none of `127.0.0.1:8102`,
   `:8103`, `:8096`, `:8100`. A scan over a **built artifact**, never over source, and explicitly
   secondary — assertion 4 is the criterion.

**Assertion 3 is what makes 4 mean something.** A gate that only checks a boundary in a laboratory
that was never built is satisfied by an empty directory.

**THE MUTATIONS THAT PROVE IT BITES.** `node scripts/verify-release-excludes-lab.mjs --mutate`,
following the `verify_shot.cjs --mutate` idiom this project already uses. **Three now, and the first
is the one the previous specification could not catch.**

| # | mutation | must trip |
|---|---|---|
| **X1** | **Write `app/(product)/math-workbench/page.tsx`** — a laboratory surface at a product path, byte-for-byte the mistake §4 had scheduled. The release emits `/math-workbench`; it is not in `PRODUCT_ROUTES`. | **assertion 4**, naming `/math-workbench` |
| **X2** | Write `app/(product)/lab-leak/page.tsx` re-exporting a component from `app/(lab)/` — someone reaches across the boundary for a component and drags the wing into the release. | **assertion 4** on `/lab-leak`, and **6** if it drags a host literal |
| **X3** | Add `"/math-workbench"` to `experiments/product-routes.v1.json` **without** the route existing. | **assertion 4** in reverse: a declared product route the release did not emit is a stale declaration and the gate names it |

Each mutation asserts GREEN → apply → **RED, and the message names the route** → revert → GREEN.
**If X1 comes back green, this gate is the same decoration it was before and the runner reports
`VACUOUS`, not `PASS`.**

### 0.4a The fallback, specified rather than assumed

**`--prerender-all` was not executed against this project this session.** If it fails — a dynamic
route with no `generateStaticParams`, a route needing request context — no manifest is written and
assertion 1 exits `MANIFEST_ABSENT`. **The fallback is still behavioural and is specified now, not
improvised later:** import `dist/server/index.js` from both builds and probe. The route list to probe
is `PRODUCT_ROUTES` ∪ the lab manifest's routes ∪ **every route reachable from `GET /` by following
`href` in the emitted HTML, transitively**. Assert every probed route outside `PRODUCT_ROUTES`
returns a status that is **not** `200` from the release worker, and `200` from the lab worker.
**This is strictly weaker** — it cannot see a route nothing links to — and the gate **prints that
limitation in its own output** rather than reporting a clean PASS.

**Honest limitation, stated in the gate's own output either way:** this proves no laboratory **route**
is *served* by the release worker. It does not prove no laboratory **byte** is present. Assertion 6
narrows that gap for the specific hosts that matter; it does not close it in general.

---

## 0.5 What `viewer/lab/`, TRACK, Gaia and HUD become

**Nothing is deleted. Nothing is rewritten. Not one line of the 5,326 changes.**

**`UNI.Minecraft/viewer/lab/` L0–L6 stays exactly what it already is: the gate and room renderer.**
It keeps its registered gates (`lab-l0`, `lab-l1`, `lab-l2-shot`, `lab-l3`, `lab-l4`, `lab-l5`,
`lab-l6` — and I confirmed `lab-l6` is registered and `l6.html` + `verify_lab_l6.cjs` are on disk).
It keeps `verify_shot.cjs --mutate` and the greyscale proof. It keeps port 8103. What it stops being
is **a candidate for the face of the project** — a role it was never suited for, because it has no
React, no build step, and, as I re-verified by running the search myself, **zero mathematics**: a
case-insensitive grep for `gravity|escape_velocity|nernst|ozone|flagell|torque|PMF|stator` across all
19 of its `.cjs` and `.html` files returns nothing.

**How the laboratory consumes it: over HTTP, and it needs no modification at all,** because it is
already API-first. I enumerated its handlers in `lab_server.cjs:120-364` — ten GET JSON endpoints
(`/api/identity`, `/api/lab`, `/api/lab/fixture`, `/api/lab/live`, `/api/lab/rooms`,
`/api/lab/portals`, `/api/lab/stations`, `/api/lab/desk`, `/api/lab/gauntlet`, `/api/lab/shot`),
`/healthz`, and `POST /api/lab/run`. The laboratory's compare and room views read these
**server-side**, inside `app/(lab)/`, through the single declared channel at
`app/(lab)/api/chip/route.lab.ts`.

**TRACK** keeps `/api/track`, `/api/identity`, `/api/arch` and `POST /api/comment`
(`track_server.cjs:407,485,512-513`) and remains the operator's persistent narrative surface.
**Gaia** (8096) and **HUD** (8100) likewise become read sources.

**The structural payoff:** because every one of these is consumed only from `app/(lab)/`, and
`app/(lab)/` is absent from the release route graph, **the release worker physically cannot contain
those hostnames.** The chip-observation channel is not kept out of the product by discipline. It is
kept out by the compiler, and assertion 4 checks the compiler did it.

> ### THE RE-PATHING RULE, stated once and applied throughout sections 3A, 4 and 5
>
> **A `.cjs` file under `UNI.Minecraft/viewer/` is a COMPUTATION or a GATE. It is never a rendering
> surface for a wing.** Where a later section names one — `desk.cjs`, `rooms.cjs`, `projection.cjs`,
> `resonance.cjs`, `gate_runner.cjs`, `coverage.cjs` — it is read by the laboratory over HTTP or as
> JSON, and the pixels are drawn in `app/(lab)/`. Where an earlier draft named
> `viewer/lab/wings/**` as the place a wing would be *built*, that path is **withdrawn**: wings are
> served by **the one manifest-driven route** `app/(lab)/lab/wing/[wing]/page.lab.tsx` at
> `/lab/wing/<wing>` (§0.9 decision 2), their panels sit beside it in
> `app/(lab)/lab/wing/[wing]/panels/<wing>.tsx`, and their offline kernels at
> `lib/kernel/mirrors/<wing>.js`. **`app/(lab)/lab/bench/…` is withdrawn with it** — it was a second
> route convention for the same thing. The rooms already standing on 8103 (`/lab`, `/lab/l1` …
> `/lab/l6`) keep their URLs and are linked from the laboratory as **a named instrument inside the
> building**. The laboratory's own rooms are named for what they are (`/lab/chalkboard`,
> `/lab/wing/flag`, `/lab/intake`), never `/lab/l1`-style, so nothing is called "the lab" twice.

---

## 0.6 The adverse finding this decision surfaced

**There is an accounts module sitting in the tree that gets promoted to the chip.**

`app/chatgpt-auth.ts` is 86 lines of ChatGPT authentication — `getChatGPTUser`,
`requireChatGPTUser`, a redirect to `/signin-with-chatgpt`, `/signout-with-chatgpt`, `/callback`, and
reads of the `oai-authenticated-user-email` and `oai-authenticated-user-full-name` request headers.
`CLAUDE.md:69-72` states the released product **"must contain no LLM inference, GPU computation,
WebGL, WebGPU, Three.js, analytics, accounts, or hidden network calls."** This is accounts.

**Two things keep it from being a live violation today, and I checked both rather than assuming
either.** A grep for `chatgpt-auth`, `getChatGPTUser`, `requireChatGPTUser` and `chatGPTSignInPath`
across every `.tsx`, `.ts` and `.mjs` outside `node_modules` returns **only its own five definition
lines** — nothing imports it, so it has no edge into the bundle. And `tests/walkthrough.test.mjs:114-122`
would not have caught it either way: that test reads **exactly three files** and joins them.
`chatgpt-auth.ts` is not one of them. **Neither is `uni-flagellum-lab.tsx`, the largest file in the
application at 880 lines.**

So the existing LLM/GPU/network test is already drawing the kernel/shell boundary the plan wants —
**around three named files instead of around a directory.** This decision replaces that three-file
allowlist with a wing boundary that a build enforces, and it puts `chatgpt-auth.ts` on the correct
side of it.

**This is the operator's call, and I am not making it quietly.** Moving the file to `app/(lab)/` is
the conservative move and what §0.3 specifies. Deleting it is the honest move, since nothing imports
it and the product forbids accounts. **I recommend moving it now and deleting it at the next
release, and I am asking rather than choosing.** (Recorded as row 15 of section 8.)

---

## 0.7 This is yours to overturn

**This decision is the operator's, not the agent's.** It sets where the laboratory lives, which
surface is the face of the project, and what a release is permitted to contain. That is
architecture, and architecture is principal-gated.

**Reverse it now — hours.** `git mv` eight files back, revert three lines of `next.config.ts`, revert
one path in `tests/walkthrough.test.mjs:116`, delete the gate and its registry entry. Nothing else in
either tree points at these paths; I established that with a repo-wide search, not by recollection.

**Reverse it after the wings are built — a full rewrite, not a port.** `viewer/lab/` has no React and
no build step; its `package.json` has no build script and its dependencies are `mineflayer`,
`prismarine-viewer` and `ws`. Every wing written as a React Server Component would have to be
re-authored as server-rendered `.cjs` string templates. That is sections 4 and 5 written twice. *(A
judgement, not a measurement — but the premise under it is measured.)*

**The point of no return is the first wing merged into `app/(lab)/`.** Before that, this is a
directory rename. After it, it is the shape of the project.

**If you say nothing, the plan proceeds on this decision.** Sections 3A, 4 and 5 are already written
against it, section 5's opening claim is corrected below, and the first thing built is the gate —
before any wing, so that the boundary exists before there is anything to leak.

**Two questions are genuinely yours, and I am stopping on them rather than picking:** whether
`chatgpt-auth.ts` is moved or deleted, and whether `/lab` on the new laboratory is the front door
with the 8103 rooms linked from inside it, or whether you want the rooms left standing alone.

---

## 0.8 What section 0 changes in the rest of the plan

- **§3A (THE SHELL)** — the map is `app/(lab)/lab/page.lab.tsx` at `/lab`, **not** `app/page.tsx`,
  because `/` stays the product. The FRAME lives in `app/(lab)/layout.lab.tsx`, **not** the root
  layout, because the root layout is shared with the product and lab chrome must never ship.
- **§4 (THE CHALKBOARD)** — its address is **`app/(lab)/lab/chalkboard/page.lab.tsx`**, its
  derivation renderer is **`app/(lab)/lab/proof/[id]/page.lab.tsx`**, and **every build item and
  every acceptance criterion inside §4, §5 and §7 has now been re-pathed to match** (§0.9 decision 3).
  The content of §4 stands; only its address changes — **and the previous draft wrote that same
  sentence and then never propagated it, which is what made the flagship gate vacuous.** The
  chalkboard is **laboratory**: it is served at `/lab/chalkboard` in the lab build and **is not in the
  release at all.**
- **§5 (THE WINGS)** — its opening claim is **false under this decision and is rewritten in place**
  (see §5's opening). Every wing's per-wing specification survives intact; only the host changes.
  Wings are served by **one manifest-driven route**, `app/(lab)/lab/wing/[wing]/page.lab.tsx` at
  `/lab/wing/<wing>` (§0.9 decision 2), with per-wing panels at
  `app/(lab)/lab/wing/[wing]/panels/<wing>.tsx`; offline kernels live at
  `lib/kernel/mirrors/<wing>.js`; `viewer/lab/` is the gate and data source they read from.
- **§2.11 (the declared observation channel)** — gains its enforcement. The channel is
  `app/(lab)/api/chip/route.lab.ts`, and `release-excludes-lab` is the check that it never ships.
- **§2.1 (the kernel/shell boundary as a path rule)** — becomes buildable. The path rule is
  `app/(product)/` vs `app/(lab)/`, enforced by the route graph rather than by a three-file
  allowlist in `tests/walkthrough.test.mjs:115`.
- **The first build item in the whole plan is now the gate**, not a wing. It must be built and its
  mutation must go red before `app/(lab)/` contains anything worth excluding. It is **W2a** in §7.1.
- **The second is THE SHELL, `W2b`** (§0.9 decision 1). Nothing that renders a room may precede it,
  because §3A.10 criterion 3 asserts the frame is on **every** lab route.

**And one build item before even that, because I read the mechanism but did not execute it:** run
`UNI_SURFACE=lab npm run build` against a single throwaway `app/(lab)/smoke/page.lab.tsx`, confirm it
serves at `/lab/smoke`, then run the release build and confirm it does not. I verified the
`pageExtensions` regex construction by reading `file-matcher.js:26-36`, and I verified the plumbing
carries the value from config through the CLI into the router — **but I did not run a build this
session.** The compound extension `lab.tsx` reaching the glob path (`buildExtensionGlob` at
`file-matcher.js:18-21` emits `page.{lab.tsx,tsx,…}`) is **reasoned, not observed.** That smoke test
is thirty minutes and it de-risks the entire section. **It is the single largest risk in §0.**
**And it now carries a second unexecuted item:** `vinext build --prerender-all` must emit
`dist/server/vinext-prerender.json` on this project. §0.4's assertion 1 depends on it, §0.4a is the
fallback if it does not, and **neither was run this session.**

---

## 0.9 FOUR CONTRADICTIONS, SETTLED — what was chosen, what was rejected, and why

**This document was convicted of carrying two designs at once and never noticing. It then did the
same thing four more times, one level down.** Each pair below is settled here, in one place, so that
no future reader has to re-derive the decision from the propagation. **The losing side is deleted
everywhere, not annotated.**

### Decision 1 — THE SHELL is a workstream, and it is **W2b**, and it is second

**Chosen:** §3A gets a real id, a real size, real dependencies and behavioural acceptance criteria in
the house format of §7.3. It is **W2b — THE SHELL**, it depends on **W2a only**, and it sits
**immediately after W2a and before every other workstream that renders anything.**
**Rejected:** leaving §3A as 587 lines of specification with no row in §7, which is how it appeared
in all of section 7 exactly once — as the bare token `3A` in W22's Depends-on column.
**Why:** §7 is titled THE WORK, ORDERED, and the front door was not in it. **The one sentence that
fixes the order: nothing that renders a room can precede the shell, because §3A.10 criterion 3
asserts the frame is on EVERY lab route, so any room built first fails that criterion the moment the
shell lands.** `W2b` follows the `W2a` convention §7.1b already established — no existing id moves.
Its only hard dependency is W2a, because §0.8 forbids any lab route before the release-exclusion gate
exists; the frame's NEEDS YOU and CASEBOOK counts come from W14 and W17 but are **not** dependencies,
because §3A.5 already specifies they render `—` when not computed.

### Decision 2 — ONE wing route: the manifest-driven `/lab/wing/<wing>`. `/lab/bench/…` is withdrawn

**Chosen:** `app/(lab)/lab/wing/[wing]/page.lab.tsx`, `generateStaticParams` driven by
`lib/shell/wings.js`. **A BENCH IS A KIND OF ROOM, not a parallel route family.**
**Rejected:** `app/(lab)/lab/bench/<wing>/page.lab.tsx`, one hand-authored static file per wing.
**Why:** *"a room cannot exist off the manifest"* is a real invariant a gate can check — §3A.10
criterion 6 walks the route files and asserts **set-equality** with the manifest — and a
hand-authored static route family defeats it by construction, because two conventions mean two
answers to *"what rooms exist?"* and the gate can only hold one of them. The dynamic route also
buys the wing frame for free: one `layout.lab.tsx` covers every wing, so W22's frame cannot be
omitted from a wing by forgetting. **What each W-wing workstream now builds is its panels, not its
route** — the route already exists, built once by W2b.

### Decision 3 — THE CHALKBOARD IS LABORATORY. Its address is `app/(lab)/lab/chalkboard/`

**Chosen:** §4 builds at `app/(lab)/lab/chalkboard/` and serves at `/lab/chalkboard` in the **lab
build only**. The derivation renderer moves with it, to `/lab/proof` and `/lab/proof/<id>`.
**Rejected:** `app/math-workbench/` — three sections named it (§4.4, §4.5, §4.8) and §7.3 W3 required
`/math-workbench` to serve six views, while §0.8 had written *"only its address changes"* and never
propagated it.
**Why:** the operator architecture says the laboratory is where you **work** the math. A plain
`page.tsx` at `app/math-workbench/` is, under §0.2, a **PRODUCT** route that ships to the chip — and
the old §0.4 gate derived its route list by scanning `app/(lab)/`, so it would have gone **GREEN,
all five assertions satisfied, while the entire chalkboard shipped.** That is the flagship gate of
this document made vacuous by a directory name. **Decision 4 fixes the gate; this decision fixes the
address; both were needed and neither alone is sufficient.**

> #### The live consequence, said plainly rather than left to be discovered
>
> **The chip today serves exactly `/math-workbench`, which this decision classifies as a LABORATORY
> surface. So the production deployment is serving the laboratory as if it were the product, and has
> been since 2026-07-20.**
>
> Measured this session: STALE `app/page.tsx` is 542 B, sha256
> `00c1e47ebc7786024d3efd6555843b05734cbfb76e7e08daa0799bec900fde3a`, and its whole body is
> `redirect("/math-workbench")` under a comment reading *"the flagellum living-science laboratory
> (UniFlagellumLab) is intentionally NOT served yet."* That sha256 is the **same value** §6.1 already
> records for the **chip's** `app/page.tsx`, so the chip is running that exact file. `/` on the
> production host does not serve the product — **it redirects into the laboratory**, and §9.2's
> measured `307 → /math-workbench → 200` is that redirect.
>
> **What the release must do about it, and it is not a code change:** the first release that crosses
> the Door (§6.3, W19) either (a) serves `app/(product)/page.tsx` at `/` and stops serving the
> chalkboard entirely — the chalkboard then lives only in the lab build and the §6.9 projection — or
> (b) declares the chip a **LAB deployment**, not a product deployment, and says so on the surface.
> **It may not do neither.** Under (a) the twelve worksheets stop being reachable on the chip, which
> is a real loss to a real user and is why this is his call, not the agent's. **Recorded as §8 row 6,
> which already holds the branch decision this now belongs to.**

### Decision 4 — the release-exclusion gate asserts on the EMITTED ROUTE MANIFEST, in reverse

**Chosen:** `verify-release-excludes-lab.mjs` reads `dist/server/vinext-prerender.json` from both
builds and asserts **`R_release` === a frozen `PRODUCT_ROUTES`**, as set equality with both
differences named — every route the release actually emitted must already be declared, **and every
route declared must actually be emitted**, so the frozen set cannot be widened in advance of the
leak it would excuse.
**Rejected:** deriving the lab route list from a source scan of `app/(lab)/**/page.lab.tsx` and
asserting each 404s.
**Why:** the scan can only ask about routes that already obey the rule, so it is blind to exactly the
failure it exists to catch. **Reversing the direction removes the blind spot**: the gate stops asking
*"is this file laboratory?"* — a question about source that a regex answers badly — and asks *"did
the release emit a route nobody declared?"*, which is a question the **build** answers. Mutation
**X1** in §0.4 writes a laboratory surface at a product path and the gate goes red naming the route;
under the old specification that same mutation passed. **The manifest was located on disk this
session** (`run-prerender.js:83,176-180`; shape at `prerender.js:789-816`); the measured caveat that
it is only written under `--prerender-all` or `output:"export"` (`cli.js:268-269`) is carried in
§0.4, and §0.4a specifies the fallback rather than leaving one to be improvised.

---

# 1. THE ARCHITECTURE, STATED ONCE

## In plain words

**The bench runs everything. Nothing that IS a release runs in the lab.**

Those two sentences sound like they fight. They do not, and here is why in one line:

> **A bench run is an instrument reading. A release is a thing that leaves.**

A wet lab absolutely runs experiments — that is what a bench *is*. Microscopes, centrifuges,
gels, chalkboards, printed worksheets, a teacher and a student. All of that executes in the
laboratory, all day, every day. What never happens in a wet lab is *shipping the sample to a
customer straight off the bench*. The sample leaves through a controlled door, gowned, logged,
accounted for — and what arrives at the other end is a *product*, not a bench.

So:

| | THE LAB (the bench) | THE CHIP (the runtime) |
|---|---|---|
| **purpose** | test, validate, observe, teach, explore | serve the release |
| **runs** | every experiment, every gate, every worksheet, every derivation | one artifact, deterministically |
| **surface** | chalkboard, sliders, printable paper, two-column compare | the product |
| **who is inside** | the operator, working | nobody; it is a machine |
| **what it emits** | *bench run records* — instrument readings | HTTP responses |
| **what it never emits** | a release | a verdict about science |

**"The UI and the runtime could never be the same."** They are two different artifacts of the
same mathematics. The kernel — `lib/kernel/**` — is the mathematics. The lab UI wraps it in a
chalkboard. The chip runtime wraps it in a server. Same equations, same seeds, same numbers;
two shells. That is exactly what makes COMPARE mode a scientific instrument rather than a
decoration: **if the two shells disagree about a number, one of them is wrong, and finding out
which is the whole point.**

## The door

A release leaves the lab through an airlock that already exists in code and has **never been
walked outside a unit test**: `UNI.Minecraft/lib/sp/control_plane/room.ex` (289 lines).

- three states, `green -> clean -> sterile` (`room.ex:47`), forward-only (`next_of/1` at `:226-228`,
  `next_of(:sterile) == nil`);
- every crossing needs **two keys from distinct parties and at least one of them an operator**
  (`:166-192`), and two agents are refused with the words *"two agents are two parties and no
  authority"* (`:186-190`);
- every crossing names a **receipt that must exist on disk** (`:205-209`) and whose sha256 is
  hashed into the ledger entry (`:241-254`);
- `Command.submit` is the only writer (`:284-287`);
- **there is no override function to call.** Not "an override is refused" — there is nothing to call.

The exit is `Room.exit/2` and it takes no keys (`:126-134`): the authority was spent on entry;
what governs the exit is *accounting for what leaves*. That is the transfer to the chip.

## The diagram

```
+=============================================================================+
|                        THE LABORATORY  --  THE BENCH                        |
|   Runs EVERYTHING: test, validation, observation, teaching, worksheets,     |
|   derivations, gates, ablations, falsifiers. The operator stands here.      |
|                                                                             |
|   +--------------------+   +--------------------+   +--------------------+  |
|   |   lib/kernel/**    |   |   lib/shell/**     |   |  viewer/lab L0..Ln |  |
|   |  THE MATHEMATICS   |   |  may reach out     |   |  rooms, desks,     |  |
|   |  pure: no network  |-->|  broker, compare,  |   |  chalkboard,       |  |
|   |  no clock, no RNG  |   |  divergence record |   |  worksheets, print |  |
|   +--------------------+   +--------------------+   +--------------------+  |
|            |                        |                        |             |
|            +---------->  BENCH RUN RECORD  <-----------------+             |
|                 an INSTRUMENT READING. never a release.                    |
|                 not_a_verdict: true      gate_row: null                    |
|                                                                             |
|         OFFLINE            ONLINE                COMPARE                    |
|         pure kernel        observe the chip      both, side by side         |
|         no network         running the same      A DIVERGENCE IS            |
|         (already gated)    mathematics           A FINDING                  |
+=============================================================================+
                                     |
                                     |  a CANDIDATE. not yet a release.
                                     v
        +===================================================================+
        |         THE AIRLOCK   SP.ControlPlane.Room  (289 lines)           |
        |                                                                   |
        |   green ---scan receipt---> clean ---execution receipt---> sterile|
        |                                                            |      |
        |                       exit: contamination + manifest  <----+      |
        |                                                                   |
        |   forward only . 2 keys, distinct parties, >=1 OPERATOR           |
        |   receipts must exist on disk, sha256 hashed into the ledger      |
        |   NO OVERRIDE FUNCTION EXISTS                                     |
        +===================================================================+
                                     |
                                     v
+=============================================================================+
|                            THE CHIP  --  THE RUNTIME                        |
|   /opt/uni/flagellum/{test,prod}/src   nginx :443 -> 127.0.0.1:8791         |
|   containers uni-flag-test / uni-flag-prod                                  |
|                                                                             |
|   NO bench. NO chalkboard. NO worksheets. NO compare. NO gate runner.       |
|   It serves the release and it observes itself, and nothing else.           |
+=============================================================================+
```

## RETRACTION — the offline clause was never in conflict, and I said it was

The first draft of this plan (`UNI-FLAGELLUM/docs/THE-LABORATORY-PLAN.md`) treated the plan of
record's **"NO SERVER, NO NETWORK"** clause as being in tension with a laboratory that observes
the chip, and asked the operator to co-sign a contract amendment (`THE-LABORATORY-PLAN.md:104-114`).

**That is retracted. There is no conflict, and no amendment is required to proceed.**

1. The clause **is** OFFLINE mode. It is not an obstacle to tri-mode; it is one third of it.
2. It is preserved **exactly** and, in this plan, made *stronger*, not weaker
   (workstream W2 below). Today it is asserted over 3 files of 9; after W2 it is asserted over
   `lib/kernel/**` and every `app/*.tsx`, with exactly one declared exception.
3. It is precisely what makes COMPARE meaningful. If the offline side could reach the network,
   an offline-vs-online agreement would prove nothing. The purity of one side is the control.
4. The contract's words are *"no ... analytics, accounts, or **hidden** network calls"*
   (`CLAUDE.md`). The obligation is entirely on the adjective. A single declared, manifested,
   GET-only, read-only observation channel with its truth class attached to every value is the
   opposite of hidden.

**And one correction to the first draft's supporting claim, measured:** it said *"chip
integration turns the suite red."* It does not. `tests/walkthrough.test.mjs:115` names exactly
three files — `biological-stage.tsx`, `guided-teacher.tsx`, `living-science-walkthrough.tsx` —
and `:119` asserts `doesNotMatch(source, /fetch\s*\(|XMLHttpRequest|WebSocket/i)` over those
three only. `app/uni-flagellum-lab.tsx` (880 lines, the component `app/page.tsx` actually
renders) is **not scanned**. A network call added there today would sail past a green suite.
That is not a reason to relax the clause. It is the reason W2 must land before any network code
in this plan, and it is why W2 is listed as a *hard dependency* and not a nicety.

## And a second retraction, from the same document

`THE-LABORATORY-PLAN.md:88-92` states *"The flagellum does not [run on the chip] ... There is no
deploy script, no quadlet unit, no ssh transport."*

**The second half is true. The conclusion is false.** Three lenses independently read the running
bytes off `/opt/uni/flagellum/prod/src/` through the uni-lab MCP. It is deployed. The correct
finding is *worse* than the one the draft recorded: **the deployment is real, it is public, and
it is reproducible by nobody.**

---

# 2. THE TRI-MODE INSTRUMENT

## In plain words

Three tabs on every equation, every experiment, every gate:

- **OFFLINE** — the pure kernel, in your browser or in node, deterministic, no network at all.
  You can do the whole lab on a plane.
- **ONLINE** — the same mathematics observed executing on the chip.
- **COMPARE** — both, side by side. **A divergence is a finding.** It is spoken first, it halts
  the run at the first differing value, and it writes a record you can hand to someone else.

This is the scientific heart of the laboratory. Everything else in this plan exists to feed it
or to render it.

## 2.1 The kernel/shell boundary — and why it is a path rule

Today `lib/` is eight flat files with no boundary
(`UNI-FLAGELLUM/lib/`: `observed-experiment.js` 500, `walkthrough.js` 472, `uni-motor.js` 420,
`cad.js` 144, `source-first-passage.js` 77, plus three `.d.ts`). No test asserts anything about
`lib/` and the network. A rule that cannot be checked by a script is not a rule.

```
lib/kernel/            PURE. May import ONLY lib/kernel/**. No node builtins. No sockets.
  uni-motor.js               git mv from lib/uni-motor.js          (420)
  walkthrough.js             git mv                                 (472)
  source-first-passage.js    git mv  -- fully pure today            (77)
  observed-experiment.js     git mv, node:crypto removed            (500)
  cad.js                     git mv                                 (144)
  duration-models.js         PORTED FROM THE STALE WORKTREE         (114)  <-- see W3
  hash.js                    NEW: pure sha256, spec already written at
                             docs/UNI-STACK-BUILDER-PLAN.md:288-295
  index.js                   NEW: the only re-export surface

lib/shell/             MAY reach the world. May import lib/kernel/**. Never imported BY it.
  chip-observer-client.js    NEW: the ONLY fetch( in the product
  compare.js                 NEW: the divergence engine
  bench-record.js            NEW: canonical serializer + f64 hex + the three digests
  bench-registry.js          NEW: the math registry (what can be run, and what computes it)
  divergence-record.js       NEW: schema + canonical encoder
  mode.js                    NEW: OFFLINE | ONLINE | COMPARE, no automatic transitions

lib/observation/       NEW. The declaration, not the code.
  channel.json               every endpoint the lab may ever read, and nothing else
```

### Measured purity, line by line

| module | lines | imports | network | fs | `Math.random` | clock |
|---|---|---|---|---|---|---|
| `lib/uni-motor.js` | 420 | **none** | none | none | none | **`:408` only** (`modelSnapshot`) |
| `lib/walkthrough.js` | 472 | **none** | none | none | none | `:385`, `:408`, both `input.x \|\| new Date()` |
| `lib/source-first-passage.js` | 77 | **none** | none | none | none | **none — fully pure** |
| `lib/observed-experiment.js` | 500 | `node:crypto` `:1` | none | none | none (seeded `:210`, `:331`) | none |
| `lib/cad.js` | 144 | none observed | none | none | none | none |

The kernel already takes its clock as an **injected parameter** on the hot path:
`observeWorld(world, controls, receivedAtMs)` (`lib/uni-motor.js:203`) and
`stepSyntheticSystem(system, controls, dtS, receivedAtMs)` (`:397`). Nothing reads a clock inside
`stepWorld`/`observeWorld`/`stepAgent`. The world's "noise" is not random at all —
`deterministicNoise(timeS, channel)` (`:128-130`) is a closed-form sine.
`observed-experiment.js` is seeded, not random: `seededRandom` (`:210`) keyed once from
`protocol.uncertainty.seed` (`:331`).

**So OFFLINE is 99% already built. It does not need writing. It needs FENCING.**

Two impurities to remove, both trivially:

- **A1** — `modelSnapshot(system, controls)` -> `modelSnapshot(system, controls, capturedAtIso)`.
  One caller: `app/uni-flagellum-lab.tsx:823`. Also `lib/uni-motor.d.ts:115`.
- **A2** — delete `node:crypto` from `observed-experiment.js:1`; `:498` becomes
  `report.runId = sha256Hex(JSON.stringify(report))` from `lib/kernel/hash.js`.
  **Acceptance is byte-exact:** re-running `npm run experiment:run` must reproduce
  `runId faa689defbf804948312388b3d26fe5f10b6d938780ca2e31f1fb48514486f6a` — the value in the
  committed report. If it does not, that is a *finding about runtime identity being an undeclared
  input*, not a licence to move on. See the C1 risk in §10.

## 2.2 The test that enforces it — and the test that proves the test bites

**NEW `tests/kernel/kernel-is-sealed.test.mjs`** — added to `npm test`. Reads every `.js` under
`lib/kernel/` recursively and asserts, per file:

1. `doesNotMatch(source, /fetch\s*\(|XMLHttpRequest|WebSocket|EventSource|navigator\.|BroadcastChannel|postMessage\s*\(/i)`
   — the surviving, *narrowed and widened* descendant of `tests/walkthrough.test.mjs:119`.
2. `doesNotMatch(source, /\bnew Date\b|Date\.now\s*\(|performance\.now\s*\(|Math\.random\s*\(/)`
   — the determinism half.
3. Every `import`/`from` specifier resolves inside `lib/kernel/`. Any `node:*`, any bare package,
   any `../shell/`, any `@/` -> fail, printing the offending specifier.
4. `doesNotMatch(source, /eval\s*\(|new Function|\bimport\s*\(/)`.
5. **Non-vacuity, asserted first:** `files.length >= 6` and
   `files.some(f => f.endsWith("uni-motor.js"))`. A guard that scans nothing passes everything.

**NEW `tests/kernel/kernel-is-sealed.mutation.test.mjs`** — copy `lib/kernel/` to a temp dir,
inject `const _ = fetch("http://x");` into the copy of `uni-motor.js`, run the same scanner
against the temp dir, assert it **FAILS**. A guard never seen to fail is a guard nobody should
trust. This repository learned that lesson this month in
`viewer/lab/desk.cjs` — its first version guarded on `typeof exit_code === "number"` and a
hand-typed `{exit_code: 0}` produced a clean PASS.

**EDIT `tests/walkthrough.test.mjs:114-122`** — not deleted, **re-aimed and widened**:

- the file list goes from three names to **every file the glob `app/*.tsx` matches, computed at run
  time and never transcribed.** Today that is **9 files / 2,234 lines** — the seven components
  (2,202 lines) plus two route shells. *(This bullet said "all seven" while naming a glob that
  matches nine. A criterion that hard-codes 7 goes red the day a shell is touched; one that reads
  the glob cannot.)*
- WebGL/WebGPU/three/LLM assertions (`:117-118`) unchanged, now over seven files;
- the network assertion becomes a **whole-tree census with a single-file allowlist**: exactly one
  file in `app/**` and `lib/**` may contain `fetch(`, and it is
  `lib/shell/chip-observer-client.js`;
- `:120-121` (`getContext("2d")`, `SpeechSynthesisUtterance`) unchanged.

**This is a strengthening, in the direction the clause already points. It is not the S5 contract
amendment the first draft asked for, and no work in this plan is blocked on a signature.**

## 2.3 The bench run record

### The one decision everything hangs on

A record must split **what was asked** from **who answered it**, or two engines can never be
compared. `SP.ControlPlane.Run` hashes `code_identity` and `env_identity` *into* `run_id`
(`UNI.Minecraft/lib/sp/control_plane/run.ex:52,77`) — correct for one engine, fatal for a
cross-engine diff, because the two engines then never share an id and there is no join key.

So the bench record carries **three** hashes:

- **`question_id`** = sha256 over `{math_id, math_version, inputs, seed, planned_n, stopping_rule}`.
  **Engine-free. This is the join key.**
- **`execution_id`** = sha256 over `{question_id, engine}`. Who answered.
- **`answer_digest`** = sha256 over the outputs' **raw IEEE-754 bits**. What the answer was.

### The float trap, closed before it is opened

**Measured this session:** Elixir `:erlang.float_to_binary(1.0, [:short])` emits `"1.0"`;
JavaScript `String(1.0)` emits `"1"`. `JSON.encode!(%{a: 1.0})` -> `{"a":1.0}`;
`JSON.stringify({a:1.0})` -> `{"a":1}`. And
`SP.ControlPlane.Ledger.canonical/1` serializes floats through exactly that function at
`lib/sp/control_plane/ledger.ex:199`.

**If the bench record reuses `canonical/1` unchanged for numbers, every cross-engine comparison
of a whole-valued float silently reports DIVERGENT and the instrument cries wolf on its first
run.** Therefore:

> **Every number in a bench record is carried as 16 lowercase hex characters of the big-endian
> float64 bits, and `answer_digest` hashes only those.** Elixir:
> `<<f::float-64>> |> Base.encode16(case: :lower)`. JavaScript: `DataView.setFloat64(0, v, false)`.
> A human-readable `decimal` field rides alongside and is **never hashed**.

The failing-first test for this (`tests/bench-record.test.mjs`) must exist and must fail against a
`JSON.stringify` implementation **before** the Elixir side is written.

### The shape — `uni.bench.run-record/1.0.0`

```jsonc
{
  "schema": "uni.bench.run-record/1.0.0",
  "record_id": "<sha256 of canonical(record minus record_id)>",

  "question": {
    "question_id": "<sha256 over canonical(question)  --  ENGINE-FREE JOIN KEY>",
    "math_id": "flagellum.agent.vfe",
    "math_version": "1.0.0",
    "equation": "F[q] = sum_s q(s)[ln q(s) - ln p(o,s)]",
    // :272 is `const vfe = posterior.reduce(` — the EXPRESSION, not the enclosing function
    // `bayesUpdateWithLikelihood` at :268. A field a gate will one day recompute must point at the
    // line the equation is on. (A previous revision cited :268.) Line numbers are measured against
    // `lib/uni-motor.js` as it stands today; §0.3 moves the file to `lib/kernel/`.
    "declared_in": "UNI-FLAGELLUM/lib/kernel/uni-motor.js:272",
    "constants": [
      { "name":"gamma", "f64":"4010000000000000", "decimal":"4",
        "unit":"dimensionless", "source":"undeclared magic number, audit NR-08",
        "evidence_class":"pending" }
    ],
    "inputs":  [ { "name":"o", "f64":"...", "decimal":"...", "unit":"dimensionless" } ],
    "seed": 20260717,
    "planned_n": 1,
    "stopping_rule": null
  },

  "engine": {
    "execution_id": "<sha256 over canonical({question_id, engine})>",
    "kind": "offline-kernel | on-chip | elixir-bench | offline-node",
    "runtime": "node v25.0.0",
    "v8": "<process.versions.v8, ALWAYS recorded -- see the C1 finding>",
    "entrypoint": "scripts/bench-run.mjs",
    "code_identity": {
      "repo": "UNI-FLAGELLUM",
      "git_commit": "4f6485e91d444bdbe35bb47e82ffe9d01ac5ec45",
      "git_dirty": false,
      "tree_digest": "<sha256 Merkle over source_set  --  COMPUTABLE WITH NO .git>",
      "source_set": [ { "path":"lib/kernel/uni-motor.js", "sha256":"852b38d1..." } ]
    },
    "env_identity": { "os":"win32", "arch":"x64", "tz":"UTC", "locale":"C" }
  },

  "execution": {
    "started_utc":"...", "started_unix_ns":0,
    "ended_utc":"...",   "ended_unix_ns":0,
    "wall_ms": 12.4, "exit_code": 0, "converged": true, "actual_n": 1,
    "status": "COMPLETE",
    "ran_in": "a clean git worktree at HEAD, removed afterwards",
    "run_token": "<minted inside run(), spent once  --  see 2.5>"
  },

  "answer": {
    "answer_digest": "<sha256 over canonical(outputs[].{name,f64,unit})  --  f64 ONLY>",
    "outputs": [
      { "name":"F", "f64":"...", "decimal":"0.4213...",
        "unit":"nat", "truth_class":"REDUCED_MODEL",
        "tolerance": { "kind":"ulp", "value":0 } }
    ],
    "artifacts": [ { "path":"...", "sha256":"..." } ]
  },

  "claim": {
    "truth_class": "REDUCED_MODEL",
    "not_a_verdict": "A bench run is an instrument reading. It is not a release and not a verdict about any scientific claim.",
    "gate_row": null
  }
}
```

- `status` reuses `SP.ControlPlane.Run.statuses/0` **verbatim** (`run.ex:56`):
  `NOT_RUN | PARTIAL_NOT_ESTABLISHED | STOPPED_BY_RULE | COMPLETE | OVERRUN | FAILED_RUN`.
- `not_a_verdict` copies the phrasing already used in control-plane ledger entry 32.
- **`tree_digest` is the git-free code identity.** Every existing staleness detector in the
  repository resolves a `.git` (`viewer/build_identity.cjs:51-60` walks up looking for it and
  `resolveGitDir` returns null if `statSync` throws), and **the chip deployment has none** —
  `os_file_list /opt/uni/flagellum/prod/src/.git` returns *"not a directory"*. A sha256 Merkle
  over `{path, sha256}` for a declared source set is computable in a checkout with no `.git`, in
  a tarball, and inside a container. `git_commit` is `null` on the chip and honestly says so.

**Where records land:** `UNI.Minecraft/evidence/bench/<question_id>/<execution_id>.json`, with the
bytes also into the existing content-addressed object store via `SP.ControlPlane.Store`.

## 2.4 The divergence record — the instrument

Two proposals converged from two lenses; they are merged here into one schema.
`uni.bench.diff/1.0.0`:

```jsonc
{
  "schema": "uni.bench.diff/1.0.0",
  "recorded_at_iso": "...",
  "question_id": "...",
  "subject_id": "AGENT_STEP",
  "left":  { "record_id":"...", "engine":"offline-kernel", "answer_digest":"...", "kernel_hashes":{...}, "v8":"14.1" },
  "right": { "record_id":"...", "engine":"on-chip",        "answer_digest":"...", "kernel_hashes":{...}, "v8":"14.1", "probe_at_iso":"...", "probe_age_ms":812 },

  "verdict": "IDENTICAL | AGREE_WITHIN_TOLERANCE | DIVERGENT | NOT_COMPARABLE | NOT_RUN",
  "tolerance_class": "BIT_IDENTICAL | ENGINE_ONLY | NOT_COMPARABLE",
  "tolerance_budget": 0,
  "tolerance_file_sha256": "<sha256 of experiments/compare-tolerance.v1.json>",

  "values_compared": 118000,
  "first_differing_path": "/tick/17/agent/efe/1",
  "left_value_e20": "4.21300000000000000000e-1",
  "right_value_e20": "4.21300000000000055511e-1",
  "ulp_distance": 1,

  "kind": null,              // "SOURCE_IDENTITY" when the two sides are different programs
  "finding": null,
  "why_not_comparable": null,
  "narrative": "..."
}
```

### The two load-bearing rules

**RULE 1 — the identity gate runs FIRST, before a single number is compared.**
`compareRun` compares `kernel_hashes` before arithmetic. Any mismatch -> the subject is
`NOT_COMPARABLE`, a record is written with `kind: "SOURCE_IDENTITY"`, **the UI shows the two
hashes side by side and refuses to draw the numbers.** Comparing numbers from two different
programs and calling the result agreement *or* disagreement is precisely the truth laundering
this instrument exists to prevent. It is the same refusal shape `Run.aggregate/2` already uses —
it refuses mismatched lengths *before* any mean (`run.ex:167`).

**On the fleet as measured today, this fires immediately and correctly.**
`uni-motor.js` is byte-identical on chip and in MAIN (`852b38d1...`), so `AGENT_STEP` and
`FIRST_PASSAGE` pass identity. `observed-experiment.js` is **not**: MAIN `b757971e...` (22 328 B)
vs chip `85a4a2e9...` (19 286 B), and the chip additionally carries `lib/duration-models.js`
which MAIN does not have at all. So `HELDOUT_ANALYSIS` fails identity on day one.

> **That is the acceptance criterion for this entire section: the first divergence COMPARE finds
> must be that one, on day one, without being told to look. If it produces anything else, the
> instrument is wrong, not the fleet.**

**RULE 2 — a DIVERGENT run halts at the first differing value and becomes a finding.**
Not a red dot. A dot is a summary. The page carries: the JSON pointer, both values printed to 20
significant figures via `toExponential(20)` (the technique already at
`tests/red/c1-cross-runtime-artifact-identity.test.mjs:111`), the ULP distance, the declared
budget it exceeded, both engine versions, both source hashes, and one button —
`Write divergence receipt`. This follows the precedent the plan of record already set at
`docs/UNI-STACK-BUILDER-PLAN.md:582`: *"on divergence, renders a `REPLAY MISMATCH` banner and
stops."*

**The page does not author the record.** It renders the exact bytes and a copy button. The
sentence for this already exists in this repository and is already correct — reuse it verbatim,
from `UNI.Minecraft/viewer/lab/desk.cjs:472-475`:

> *"THIS IS NOT WRITTEN AND THIS DESK CANNOT WRITE IT. S4. The line above is what would be
> appended ... appending it is authorship, and a rendering surface does not author verdicts."*

Records are appended to `experiments/results/divergences.ndjson` (append-only, in MAIN,
version-controlled, never edited). **A `NOT_COMPARABLE` verdict is recorded with the same weight
as a `DIVERGENT`. Silence is never a record.**

## 2.5 Tolerance — declared before the run, never chosen after seeing a diff

`experiments/compare-tolerance.v1.json`, authored by the **operator**, not by an agent. Three
classes, and the class is a claim about the *language*, not about the *result*:

| class | meaning | legitimate when | falsifier |
|---|---|---|---|
| `BIT_IDENTICAL` | zero ULP permitted | same source bytes, same engine major (browser V8 vs a same-major node) | any differing byte |
| `ENGINE_ONLY` | bit-identity per engine, a declared ULP budget across engines | different V8 majors, or any non-V8 engine | exceeding the budget |
| `NOT_COMPARABLE` | the two sides are not the same program | source hashes differ | n/a — arithmetic never runs |

The name `ENGINE_ONLY` is **not new**: `docs/UNI-STACK-BUILDER-PLAN.md:813` already coins it for
`stepWorld`'s `Math.exp`/`Math.sin`.

**The budget starts at the measured value, not a guess.** The project has already measured its own
cross-engine non-reproducibility and localised it to one operator on one line:
`tests/red/c1-cross-runtime-artifact-identity.test.mjs:13-22` records that at the fitted Weibull
parameters (shape 0.625088844276203, scale 0.6996038164387606), **418 of 4000 sampled evaluations
differ by 1 ULP between V8 12.4 and 14.1**, at
`lib/observed-experiment.js:178` — `(y / scale) ** shape`. `tests/red/README.md` records the two
report digests it produced: `a485fa5a...` (Node 25) vs `d1753d25...` (Node 22.13.1).
**This box runs Node v25.0.0 and `package.json` floors at 22.13.0.** The divergence C1 documents
is one `nvm use` away.

**Tightening a tolerance is a normal commit. Loosening one is refused by gate.**
`tests/compare/tolerance-is-frozen.test.mjs` asserts every numeric budget in the tolerance file is
`<=` the value at the previous commit of that file, read via
`git show HEAD~1:experiments/compare-tolerance.v1.json`. The CLAUDE.md law "never loosen a frozen
tolerance" gets a machine.

## 2.6 The three compare subjects, and why these three

| subject | kernel entry | trace compared | determinism class |
|---|---|---|---|
| `FIRST_PASSAGE` | `sourceMoments`, `sourceSurvival`, `sourceDensities` (`lib/kernel/source-first-passage.js`) | every returned scalar at a frozen grid of `(stateN, t)` | the only fully-pure module; cleanest possible signal |
| `AGENT_STEP` | `stepSyntheticSystem` (`lib/kernel/uni-motor.js:397`) | **every field of `{world, agent, observation, action}` at every one of N ticks** — ~60 numbers x N | this is "every bit exposed" |
| `HELDOUT_ANALYSIS` | `runObservedExperiment` (`lib/kernel/observed-experiment.js:292`) | `runId`, then the full report tree | already known to diverge cross-engine |

The trace is not a summary. For `AGENT_STEP` the comparison walks both trees key-by-key and
reports the **first differing path as a JSON pointer** — `/tick/17/agent/efe/1` — because "they
disagree" is not a finding and "they disagree at the RUN expected free energy on tick 17" is.

## 2.7 The determinism contract, and where it honestly stops

Every subject takes a **`RunSpec`**, canonically encoded and hashed, and nothing else:

```js
{ subjectId, seed, ticks, dtS, controls, receivedAtMsBase, kernelHashes }
```

- `seed` is the only entropy. There is no `Math.random` anywhere in `lib/`.
- **`receivedAtMsBase` is the clock, and it is an input.** Tick *n* uses
  `receivedAtMsBase + n * round(dtS * 1000)`. **Wall time is never an input to a compare run** —
  which is exactly why an offline run and a chip run can be compared at all.
- `kernelHashes` is part of the spec, so a run against different bytes is a **different run**, not
  a disagreeing one.
- `runSpecSha256 = sha256Hex(canonicalJson(runSpec))`. Two records with the same `runSpecSha256`
  and different verdicts is itself a finding.

**Three honest tiers:**

- **Tier 1 — YES.** Browser V8 vs local node V8 of the same major, over byte-identical
  `uni-motor.js` and `source-first-passage.js`. All arithmetic is `+ - * /`, `Math.sqrt`,
  `Math.log`, `Math.exp`, `Math.sin`, `Math.cos`; IEEE-754 pins the first four and `sqrt` exactly,
  and the transcendentals are the same V8 implementation on both sides. `BIT_IDENTICAL` is a
  legitimate demand here and must be **gated, not hoped**.
  *(Marked UNVERIFIED — reasoned from IEEE-754 and shared V8, no browser was driven. See §10.)*
- **Tier 2 — NO, and it is measured.** Across V8 majors or against any non-V8 engine, `**` /
  `Math.pow` is not reproducible; ECMA-262 permits it to be implementation-approximated. Valid
  comparison is `ENGINE_ONLY` with both engine versions in every record.
- **Tier 3 — NOT COMPARABLE, and it is where the fleet is today.** JavaScript vs Elixir over
  *different subjects* is not a comparison at all: `SP.Lab` (733 lines) computes planetary gravity,
  radiation, bioenergetics and solar energy — **not flagellar mathematics**. And within
  JavaScript, MAIN's `observed-experiment.js` and the chip's are different programs.
  `NOT_COMPARABLE` is the honest verdict and it is a *finding*, not an error state.

**NEW `tests/kernel/determinism-is-a-gate.test.mjs`** (in `npm test`): run `stepSyntheticSystem`
for 2000 ticks from a fixed `RunSpec`, twice in-process and again in a fresh child process;
assert `sha256Hex` of the canonical trace is identical across all three. **Mutation:** inject
`Math.random()` into a temp copy of the kernel, assert failure. CLAUDE.md already says
*"determinism is a gate, not a hope"*; today there is no such gate in `npm test`.

## 2.8 A bench run record is a new place to launder truth — and the fix already exists

`answer_digest` is computed by the same process that produced the answer. `viewer/lab/desk.cjs`
already solved this once: `run()` (`:489`) creates a throwaway `git worktree add -q --detach HEAD`
(`:504`), spawns the gate there under a timeout, removes and prunes (`:549-552`), and mints a
single-use `crypto.randomUUID` run token (`:580-585`) that the row-builder requires and deletes
(`:405-415`). It also refuses a gate file not present at HEAD rather than reporting a FAIL for a
question that could not be asked.

**The bench record must reuse that token, not invent a second scheme.** The hardest part of a
bench — running from the committed bytes, in isolation, with an unforgeable proof that a process
actually ran — is already built and already gated.

## 2.9 ONLINE: what is actually readable from the chip, and why a broker is mandatory

The uni-lab MCP is real, authenticated (`http://10.190.245.121:8080/mcp`, Bearer token,
registered **globally** in `C:/Users/mpolz/.claude.json`), and exposes seventeen read-only tools
that run with no approval; mutating tools pause for exactly one human co-sign.

**Measured behaviour, not recalled:**

- `os_file_read` returns **content plus its sha256** — exactly the primitive the identity gate
  needs, which is why the identity gate is buildable today with no chip-side change.
- `os_file_list` roots: `/opt/uni`, `/var/lib/uni`, `/etc/uni`, `/var/log/uni`, `/run`. The whole
  deployed tree is readable.
- `lab_call` proxies `127.0.0.1:8000`, which is **`uni-biological-builder`** — not the flagellum,
  not `SP.Lab`. Anyone designing "call the chip's maths" through `lab_call` is designing against
  the wrong service.
- `os_systemctl_status uni-flag-prod.service` -> **REFUSED**, *"unit not in allowlist"*. The read
  channel cannot see the one unit it most needs to watch. **Widening that allowlist is a chip
  security-posture change and is the operator's.** The design must render
  `REFUSED_BY_ALLOWLIST` and must **never** route around it via `os_exec`.

**A browser can reach none of it.** MCP is not an HTTP/CORS API a page may call. The one HTTPS
surface that answers — `https://workbench.uni-lab.solwright.com` — returned **no
`access-control-*` header** when probed with an `Origin`. So the broker is not a convenience:
without it there is no ONLINE mode at all.

### `scripts/chip-observer-broker.mjs` — NEW, dev-only, in `scripts/`, never in the bundle

- binds `127.0.0.1:8104` (measured free on this box; 8090/8096/8098/8099/8100/8102/8103 are the
  declared occupied range per `UNI.Minecraft/viewer/infra_registry.json`);
- refuses non-loopback `Host` and any method but `GET`, following **two separate fences in
  `UNI.Minecraft/viewer/lab/lab_server.cjs`, and a builder must copy both**: the **method fence at
  `:104-118`** (the one-member `POST_ALLOWED` set at `:107`, then `405` for anything that is not
  `GET`/`HEAD`) and the **Host pin at `:251-257`** (`const host = String(req.headers.host || "")…`
  tested against the four loopback names, `403` otherwise), added 2026-07-28 with its own comment at
  `:246` recording that its absence was the audit's unimplemented *probe C*. **On `lab_server.cjs`
  the Host pin sits inside the POST branch only. On the broker it must apply to EVERY route**,
  because every broker route reads a production host, and a header fence stops CSRF but not DNS
  rebinding. *(A previous revision cited `:104-123` for both; measured, that range contains the
  method fence and no Host check at all — a builder copying it would have silently omitted the
  rebinding defence, which is the half that matters for a broker.)* Both fences are *asked with real
  requests* by `verify_lab_l5.cjs` rather than read from source;
- **exact-match route allowlist, four routes, no parameter reaching a shell:**
  `/api/chip/identity` (filenames + sha256 of `/opt/uni/flagellum/prod/src/lib/**` plus
  `PROMOTE_STATUS`), `/api/chip/health`, `/api/chip/units` (returns
  `{"status":"REFUSED_BY_ALLOWLIST","unit":"..."}` verbatim — the refusal is *rendered*, never
  swallowed), `/api/chip/run/<subjectId>`;
- **zero mutating tools importable**, enforced by `tests/shell/broker-is-read-only.test.mjs`,
  which scans for every mutating tool name (`os_file_write`, `os_exec`, `os_systemctl_action`,
  `podman_run`, `podman_stop`, `podman_rm`, `podman_pull`, `podman_quadlet_apply`,
  `livepatch_apply`, `livepatch_revert`, `live_update_*`, `lab_evolve_run`, `lab_world_*`,
  `fleet_upgrade_*`) and asserts zero occurrences — with a **mutation** proving the scan fails
  when `os_exec` is inserted into a temp copy;
- every response carries its own provenance: `{ value, tool, probedAtIso, chipTimestamp,
  evidenceClass, auditId }`. The MCP envelope already supplies `evidence_class` and `audit_id`;
  the broker forwards them rather than flattening them into a bare number.

**`/api/chip/run/*` in v1 does NOT execute on the chip.** Executing a subject there requires a
process there; every path to that is a mutation, gated on one human co-sign. v1 returns
`{"status":"NOT_RUN","reason":"on-chip execution requires the operator's co-sign","command":"<the exact command that would run>"}`.
**v1 is complete and useful without it**, because v1 compares browser-vs-local-node (two genuinely
different V8s — a real test of the tolerance machinery) **plus** the chip *identity* comparison,
which needs no execution and which already finds the real divergence. v2 adds on-chip execution
behind the Room. That is the operator's call.

## 2.10 OFFLINE must be honest about not having a chip

The law, quoted from the file that actually contains it —
`UNI-FLAGELLUM/docs/control-plane/views.md:275`:

> **"No frame rate, glow, motion or particle may imply liveness. Liveness renders *only* from a
> real probe result — a frozen colony looks frozen while every process reports up."**

*(Correction, re-measured — and the previous version of this parenthesis misquoted the thing it was
correcting. `docs/THE-LABORATORY-PLAN.md:248` cites the rule at a **bare `views.md`**, with no path
prefix; `grep -n "views.md"` returns its four mentions, at `:89`, `:188`, `:248` and `:427`, and
**none of them carries the `UNI.Minecraft/viewer/` prefix a previous revision attributed to it.**
That prefix was invented, and the "does not exist" was true only of the invented path — though it
is separately true that `find . -name views.md` over `UNI.Minecraft` returns nothing. The bare
citation **does resolve**: `UNI-FLAGELLUM/docs/control-plane/views.md` exists, 16,597 B, and carries
the rule verbatim at `:275`, as does `docs/control-plane/ARCHITECTURE.md:274`. **The real defect is
smaller and still real: in a three-tree project a bare filename is a citation the reader has to
guess at, and the likeliest guess — the tree that owns the viewer — returns nothing. Cite the full
path.**)*

And the harder, earned corollary from the chip side —
`UNI.Minecraft/docs/receipts/hud_glance_honesty_2026-07-17.md` §4, gate
`colony-frozen-needs-dwell-not-one-sample` (PASS, `docs/GATES.md:103`): a single-sample liveness
verdict produced a permanent false FROZEN alarm on a healthy colony because the poll interval
equalled the event interval. **The fix was to dwell-gate on wall-clock-since-last-movement.**
And `undermined_signals_swept_2026-07-17.md` B4, gate `hud-freshness-honest`:
*"FALSIFIES: a 6-min-old number in a confident colour."*

`lib/shell/mode.js` — three states, **no automatic transitions**:

- **OFFLINE is the default and the boot state.** All 13 walkthrough steps, the synthetic world,
  the agent, the first-passage maths, the notebook, CSV/JSON export, and the twelve printable
  worksheets all work here. Nothing is greyed out. Nothing says "unavailable".
  **Offline is not degraded mode; it is the bench.**
- **ONLINE** is entered only by an explicit operator action, and only after a probe **succeeded**.
  It cannot be entered optimistically.
- **COMPARE** requires ONLINE plus a subject selection.

| probe state | what the page says | what it must never do |
|---|---|---|
| never probed | `CHIP . NOT PROBED — nothing has looked` | show a number; show a colour that reads healthy |
| probe failed | `CHIP . UNREACHABLE — <the actual error> . last looked 14 s ago` | fall back to a cached number, or to the offline number presented as the chip's |
| succeeded but stale | value **greyed and dated**: `stators 6.02 . last probe 4 m 12 s ago` | render it in a confident colour |

Staleness is dwell-gated per the colony receipt: stale at `> 3 x the measured probe interval`,
and the interval is **measured at request time from the last successful probe timestamp**, not
from a cadence counter that freezes when the poller dies — the exact B4 root cause.

**The rule that makes this non-negotiable:** an OFFLINE-computed value and a chip-observed value
are **never rendered in the same visual slot**. Two columns, two headers, always both present;
the chip column carries `NOT PROBED` / `UNREACHABLE` rather than collapsing. A number that can
silently change provenance is the failure mode; two columns make it structurally impossible.

The template already exists in this tree, in test form —
`tests/red/c1-cross-runtime-artifact-identity.test.mjs:81-85`:

```js
if (!ALT) {
  // Absence of a second runtime is NOT a pass. Skip loudly.
  t.skip("UNI_ALT_NODE not set -- a second Node runtime is required. NOT RUN, not passing.");
```

OFFLINE's contract is one sentence longer: **absence of the chip is NOT a comparison, NOT an
agreement, and NOT a failure of the science. It is `NOT_RUN`, said out loud, and the bench keeps
working.**

## 2.11 The observation channel is DECLARED, not merely coded

`UNI-FLAGELLUM/lib/observation/channel.json` — the manifest. Every endpoint the lab may read and
nothing else, each with `method: "GET"`, a `truth_class` drawn from the frozen `TRUTH_CLASSES` in
`lib/kernel/walkthrough.js:5`, and a `why`.

`lib/shell/chip-observer-client.js` — the **only** module permitted to contain `fetch(`. It
resolves every request against `channel.json`, refuses any id not present, refuses any method but
GET, attaches the endpoint's truth class to every value, and **never returns a bare value** —
always `{ endpointId, url, fetchedAt, truthClass, ok, body | refusal }`. A failure is a
first-class result, not an exception, so the UI can render "the chip did not answer" as data.

`tests/semantic/observation-channel-declared.semantic.test.mjs` — four static assertions, no
network: exactly one file in `app/**` + `lib/**` matches the network regex and it is the client;
every URL literal in the client appears in `channel.json`; every entry is GET with a legal truth
class; and `lib/kernel/**` contains zero network tokens and does not import `lib/observation/`.

## 2.12 Acceptance criteria for §2 (behavioural, not textual)

1. Injecting `fetch(` into a copy of any kernel file makes `kernel-is-sealed` FAIL; removing it
   makes it PASS. The whole-tree `fetch(` census returns exactly one file.
2. `benchRecord(q,e,x,a).question_id` is **unchanged** when `engine` changes.
3. `bench-record.test.mjs` FAILS against a `JSON.stringify` canonicaliser and PASSES against the
   f64-hex one, byte-compared to an Elixir golden.
4. `scripts/bench-run.mjs` run twice produces records differing **only** in `execution.*` timing;
   `question_id`, `execution_id` and `answer_digest` are identical.
5. Two records with different `question_id` produce `NOT_COMPARABLE` and **zero numeric
   comparisons execute** — asserted by a call counter, not by reading the verdict.
6. Perturbing one float's last mantissa bit in one engine's record flips the diff
   `IDENTICAL -> DIVERGENT`. Leaving a tolerance in swallows the mutation, which is the falsifier
   and must fail the gate.
7. Perturbing one literal in a copy of the kernel (`0.82 -> 0.820000000000001` in `bRun`,
   `lib/kernel/uni-motor.js:255`) makes `compareRun` return `DIVERGE` with `firstDifferingPath`
   naming an **`agent`** field, not a `world` field.
8. **The live one:** running COMPARE against the chip as it stands today produces a
   `NOT_COMPARABLE` record for `HELDOUT_ANALYSIS` naming `b757971e...` vs `85a4a2e9...`, and an
   `AGREE` for `AGENT_STEP`.
9. **The airplane test:** with every network interface down and the broker not running,
   `npm run build && node --test tests/rendered-html.test.mjs` passes, all 13 walkthrough steps
   render, the agent loop runs, and the worksheet print view renders. A cold boot matches
   `/NOT PROBED/` and does **not** match `/UNREACHABLE/`.

---

# 3. THE OPERATOR IS INSIDE

## In plain words

**Twenty-one things happen in this project every day and the operator can see three of them.**
The three he can see — voice lines, his own commentary, the plan — are the three somebody already
sat down and hand-wrote. The three that actually *change the world* — a gate run, a plan edit, an
intake — have no persistence at all. A gate run computes a full structured report and prints it to
a terminal, and then it is gone forever.

This section ends that.

## 3.1 The invisibility census — measured, twenty-one items, each one scheduled or not

**The census was the plan's answer to *"too much happens where I cannot see it"*, and fourteen of its
twenty-one rows had no build item anywhere in this document.** A census with no schedule is a list of
complaints. **The column on the right is the fix: every row now carries a workstream id or the literal
word `NOT_FIXED`.**

| # | What happens | Produced by | Where it lands | UI today | **fixed by** |
|---|---|---|---|---|---|
| 1 | **A full gate run** (28 registry entries, exit⇔verdict law, completeness check) | `viewer/gate_runner.cjs:64-116` | **NOWHERE.** `runGates()` returns a complete structured report; `main()` prints it and exits. Zero `fs.write` in the file | **NONE** | **W4** |
| 2 | **A single gate run** | the 28 gate files | stdout | **NONE** | **W4** |
| 3 | **A bench run from the lab** | `POST /api/lab/run` → `desk.run()` (`viewer/lab/lab_server.cjs:237`) | streamed to the socket, then gone — `desk.cjs` has zero writes | live stream only | **W4** |
| 4 | **Canonical gate-ledger rows** | nothing programmatic — S4, hand-edited | `evidence/gates.ndjson`, 206 rows / 109 unique | TRACK tally; L3 renders all rows | **NOT_FIXED** — S4, the operator's (§8 row 4) |
| 5 | **Control-plane ledger appends** (32 entries) | `SP.ControlPlane.Command` | `evidence/control_plane/ledger.ndjson` | **Gaia only**, raw projected bytes. **TRACK never reads it** | **NOT_FIXED** |
| 6 | **The anchor moving** | `SP.ControlPlane.Store` | `evidence/control_plane/anchor.json` (head `b90b7498…`, length 32) | Gaia signal only | **NOT_FIXED** |
| 7 | **Plan edits** — every status change of 43 steps | an agent's Edit tool. **No writer exists** | `evidence/remediation/phase9_plan.json` | current state only. **No diff, no author, no reason** | **NOT_FIXED** |
| 8 | **`mix test`** (139 `.exs` files, 1047 `test "` blocks) | a terminal | stdout | **NONE** | **W32** |
| 9 | **`node --test`** (MAIN, 17 files) | a terminal | stdout | **NONE** | **W32** |
| 10 | **Commits** (576 / 113) | git | `.git` | TRACK shows the last **6 subject lines per repo**. No body, no diff, no file list | **NOT_FIXED** |
| 11 | **Agent activity** — subagent runs, workflow runs, this very session | the harness | **NOWHERE in any repo** | **NONE** | **NOT_FIXED — and it is the worst row on this table. See below.** |
| 12 | **Receipts** — **136 files** under `UNI.Minecraft/docs/receipts/`; **zero in UNI-FLAGELLUM** | hand-written | files on disk | **NONE.** No index, no listing, no route | **W33** |
| 13 | **The airlock** `green→clean→sterile` | `lib/sp/control_plane/room.ex` | **never run outside its test files** | **NONE.** L4's "airlock" is `rooms.cjs`, a different object with zero references to `room.ex` | **W19** |
| 14 | **Gate-attempt classification** | `viewer/classify_gate_attempts.cjs` | `evidence/gate_attempts.ndjson` (1 header + 59 rows) | read by `rooms.cjs` (L4) only. Not on TRACK | **NOT_FIXED** |
| 15 | **Voice lines spoken** | ClaudeSpeak :5858 | that service's store | TRACK, last 25 | **NOT_FIXED — nothing to fix** |
| 16 | **TRACK comments** | `POST /api/comment` | `evidence/track_comments.ndjson`, **77 rows, every one `author: "claude"`** | TRACK. **The one thing that works end to end** | **NOT_FIXED — nothing to fix** |
| 17 | **Limitations** — 9 declared, generated, gate-enforced | `viewer/generate_limitations.cjs` | `UNI.Minecraft/docs/control-plane/LIMITATIONS.md` | **NONE.** TRACK's `/doc/` searches the *other* repo's control-plane dir | **NOT_FIXED** |
| 18 | **The resonance lattice** — 7 conjunctive layers, `--prove` | `viewer/resonance_meter.cjs` | stdout | **NONE**, and in no registry (deliberately) | **NOT_FIXED** *(the layer NAME is surfaced by §3A.9; the lattice itself gets no recorder)* |
| 19 | **Boot identity** — the commit + module set each process runs | `viewer/build_identity.cjs` | computed per request | served at `/api/identity`; **`track.html` renders it zero times** | **NOT_FIXED** |
| 20 | **Go-live token spend** | `viewer/golive_guard.cjs:61-63` | `viewer/.presence/token.json`, `.presence/spent.ndjson` | indirectly, via L4's `no_door` scan | **NOT_FIXED** |
| 21 | **Anything entering the lab** — equation, parameter, proof, dataset, module | agents and the operator | scattered into source, docs, `data/`, `experiments/` | **NONE** | **W18** |

**The arithmetic, so it cannot be softened.** Before this fix: **5** rows scheduled (1, 2, 3, 13, 21),
**2** already working (15, 16), **14** rows with no build item anywhere. After W32 and W33: **8**
scheduled, **13** carrying `NOT_FIXED`, of which two are the two that already work — so **eleven
things still happen where the operator cannot see them, and this plan says so on its own face rather
than leaving it to be discovered.**

**The shape of it:** the three things that change the world — a gate run, a plan edit, an intake —
are the three with no persistence. The things that are visible are the things somebody already sat
down and hand-wrote.

**And a second shape, which this table names rather than schedules.** Of the thirteen `NOT_FIXED`
rows, **five are argued** — 4 is S4 and the operator's, 11 is unfixable because the harness writes
nowhere in any repo, 15 has nothing to fix, 16 already works, 18 is deliberately out of every
registry. **The other eight — 5, 6, 7, 10, 14, 17, 19, 20 — carry the bare word and no reason, and
**six** of the eight are the same shape: a file that already exists, on disk, with no page that reads
it.** *(An earlier revision said seven and then named six files. Row 10 is the odd one: its artifact
is `.git`, not a file this list can `ls`, and its own UI cell says TRACK already renders the last
six subject lines per repo — so it is neither unread nor a render of a file. Corrected rather than
left, because a count inside a paragraph about bare `NOT_FIXED` rows is exactly where a reader
checks the arithmetic.)* Measured this session in `UNI.Minecraft`: `evidence/control_plane/ledger.ndjson` 50,377 B,
`evidence/control_plane/anchor.json` 126 B, `evidence/remediation/phase9_plan.json` 143,938 B,
`evidence/gate_attempts.ndjson` 24,713 B, `docs/control-plane/LIMITATIONS.md` 7,072 B,
`viewer/build_identity.cjs` 9,577 B. **Each is a render, not a build.** The eighth, row 20, is
different: `viewer/.presence/token.json` and `.presence/spent.ndjson` are **ABSENT** today, so there
is nothing to render until a token is minted. **Row 7 is the sharpest of the eight** — `CLAUDE.md`'s
own resume block makes `phase9_plan.json` the single source of truth for this entire phase, and this
plan records that its every edit is invisible and unattributed, then schedules nothing.
**Whether those seven renders are worth a workstream is a scope decision, not a measurement, and it
is parked at §10.4 rather than answered here.**

## 3.2 TRACK, characterised exactly

`viewer/track/track_server.cjs` (530 lines / 31,740 B) + `viewer/track/track.html` (384 lines), port 8102,
bound `0.0.0.0`, polling every 10 s (`track.html:383`), caching nothing. Fifteen sections
(`track.html:359-374`). It reads live, per request: `evidence/gates.ndjson` (`:167`),
`phase9_plan.json` (`:301`), `docs/control-plane/**` (`:186-218`, `:485-511`), Gaia `:8096`,
voice `:5858`, `git log -12` on both repos (`:220-230`), `track_comments.ndjson` (`:232`), TCP
probes on 6 ports (`:98-108`), and `fs.existsSync` on 13 Elixir module paths (`:112-126`). One
write: `POST /api/comment`, fenced by loopback peer (`:409`), loopback Host (`:423`) and
`x-uni-cc: 1` + JSON (`:432`); `author` defaults to `"claude"` (`:446`).

**One-sentence characterisation: TRACK is an excellent plan-and-architecture projector. It is not
an instrument panel and it is not a classroom. It shows what was decided and what was recorded by
hand; it shows nothing that ran.**

Zero mentions of `gate_attempts`, `gate_registry`, `gate_runner`, `mix test` or `LIMITATIONS` in
either file. Two defects worth fixing regardless of this plan:

- TRACK's own boot identity is the one thing on the page that would tell the operator TRACK is
  running stale bytes, and the page throws it away (computed `:275`, served `:513`, never drawn).
- `viewer/infra_registry.json` lists 21 services and contains **no `8102`, no `8103`, no `5858`**.
  The operator's three newest surfaces are not in the infrastructure registry.

## 3.3 Persist the run — the highest value-per-line change in this entire plan

**NEW `evidence/bench_runs.ndjson`.** One row per run, from both entry points:

```jsonc
{ "utc":"...", "gate":"lab-l5", "gate_row":"lab-l5-desk-shows-the-bytes",
  "commit":"1c7e69e", "boot_identity":{ },
  "exit":0, "verdict":"PASS", "law_ok":true, "ms":28104,
  "operator_prediction":"PASS", "predicted_before_run":true,
  "actor":"michael", "channel":"lab|runner", "output_sha256":"...",
  "output_path":"evidence/bench_output/<sha256>.txt" }
```

- **EDIT `viewer/gate_runner.cjs`** — `main()` gains `--record`, appending one row per result from
  the report object it **already builds** and already exports. Roughly nine lines.
- **EDIT `viewer/lab/lab_server.cjs`** — the `.then((observed) => {` block at **`:306`** (the file is
  383 lines, CRLF throughout; `:296` was wrong) appends the same row shape. It sits inside the
  streaming `/run` handler that strips `run_token` off the wire at `:310`.

**This is NOT `evidence/gates.ndjson` and must never be confused with it.** S4 stands; no verdict
is authored; the schema is deliberately different. Say so in the file's own header, the way
`viewer/gate_attempts.cjs:13-19` says it. A clause in the new gates asserts the two schemas share
no field names beyond `utc`.

**What a run history buys that the operator cannot have today:** *this gate went red on Tuesday and
green today, and here is the commit between them*; *your prediction was wrong six times out of
forty, and here are the six*; *this gate has never once been run*.

### W32 — a test run becomes a row

**`mix test` and `npm test` are the two commands this project lives by, and neither leaves a trace
anywhere.** Measured: MAIN's `npm test` is a single line in `package.json` running `node --test` over
**17** named files in **two invocations** (16 before `&& npm run build`, then
`tests/rendered-html.test.mjs` after it), with **no `--record` path and no runner script**. There is
**no `evidence/` directory in MAIN at all**.

- **NEW `UNI-FLAGELLUM/scripts/test-record.mjs`.** Reads the file list out of `package.json` **so it
  can never drift from `npm test`**, spawns `node --test`, parses the TAP summary, appends one row,
  and stores the full output content-addressed. **NEW npm script `"test:record"`. `npm test` is not
  touched**, so no existing gate moves.
- **NEW `UNI.Minecraft/viewer/record_test_run.cjs`.** Spawns `mix test`, parses its summary line,
  appends the same row shape. A `.cjs` wrapper **rather than a ninth mix task** (there are 8 in
  `lib/mix/tasks/`) because **it must not sit inside the thing it is measuring.**
- **NEW `evidence/test_runs.ndjson` in EACH tree** — including a new `UNI-FLAGELLUM/evidence/`
  directory. **Each tree records its own runs.** A test runner in one repository that writes into
  another repository is exactly the hidden cross-tree coupling §6.4 exists to kill; the viewer reads
  both and says which is which.

```jsonc
{ "schema":"uni.test.run/1.0.0", "utc":"...", "tree":"UNI-FLAGELLUM",
  "runner":"node --test", "invocation":"npm run test:record",
  "commit":"4f6485e", "dirty":false, "boot_identity":{ },
  "files":17, "tests":0, "pass":0, "fail":0, "skip":0, "todo":0,
  "wall_ms":0, "exit":0, "failing":[ {"file":"...","name":"..."} ],
  "output_sha256":"...", "output_path":"evidence/test_output/<sha256>.txt",
  "not_a_verdict":"A test run is an instrument reading. It is not a release and not a verdict about any scientific claim." }
```

Same rule as `bench_runs.ndjson`: **this is not `evidence/gates.ndjson`**, it says so in its own
header, and a clause asserts the two schemas share no field name but `utc`.

### W33 — the receipts get an index and a door

Measured: `UNI.Minecraft/docs/receipts/` holds **136 files** — 70 at top level (63 `.md`), **60**
under `control-plane/` (49 `.txt`, 9 `.md`, 2 `.json`), and 6 under `phase1_baseline_2026-06-25/`; by
extension across all: 72 `.md`, 57 `.txt`, 3 `.gz`, 2 `.json`, 1 `.log`, 1 `.png`.
**`UNI-FLAGELLUM` has no receipts directory at all** — its evidence lives under
`hierarchical-aif/reports/` and `docs/audit/` instead, **and the index must say that** rather than
silently index one tree and imply it is the whole project.

- **NEW `viewer/receipts.cjs`**, modelled line-for-line on `viewer/limitations.cjs` (148 lines,
  `module.exports = { scan, render, ROOTS, REPO, DOC }` at `:148`, `walk` `:49`, `scanFile` `:65`) —
  **the same shape, so a reader who can verify one can verify the other.** Per receipt: path, sha256,
  bytes, mtime, first `# ` heading, the gate id and the `PASS|FAIL|PARTIAL|PENDING` token if the file
  carries one, and whether any `gate_row` it names exists in `gate_registry.json`.
- **NEW route `/receipts` and `/receipts/<sha256>`** in `viewer/lab/lab_server.cjs`, added to the
  exact-`url.pathname` chain beside `/lab/l1` (`:356`) and `/lab/l5` (`:318`). **Read-only**; it
  renders a file, it never writes one. **It adds no second POST carve-out.**
- **NEW `viewer/verify_receipts_index.cjs`**, gate_row `receipts-index-cannot-drift`: regenerate and
  byte-compare; every indexed sha256 re-hashes on disk; **every `gate_row` a receipt claims either
  resolves in the registry or is listed as unresolved, by name** — because a receipt that cites a gate
  that does not exist is the fabricated-citation failure mode, and here it becomes a gate failure.

### Row 11 — `NOT_FIXED`, and that is the honest answer, not the easy one

**The agent harness emits nothing into either repository, and the two mechanisms that were built to
constrain an agent from inside a repository have never once run.**

What was searched, and what it returned:

- **Every `.ndjson` in `UNI.Minecraft`** — 16 files (`colony_minds` custody ×3,
  `control_plane/ledger`, `gates`, `gate_attempts`, `remediation` preludes ×3, `track_comments`, a
  red-producer camera run, `gaia/snapshots/index`, a `hud` fixture, three `viewer/runtime/door_*`
  logs). **None records an agent run, a subagent run, a workflow run, or a tool call.**
- **`evidence/track_comments.ndjson`** — 77 rows, keys `utc/author/target/text/kind`, and **every
  single row has `author: "claude"`.** It records what an agent chose to *say*. **It has never
  recorded what an agent *did*.**
- **`UNI-FLAGELLUM/hierarchical-aif/reports/FLOW-JOURNAL.jsonl`** — the one genuine agent-activity
  record in either tree: **37 rows, `F001` to `F036`, last timestamp `2026-07-22T23:30:00Z`**, scoped
  to the `hierarchical-aif/` namespace, written in prose by the agent about itself. **Six days stale,
  and mandated by `CLAUDE.md` — which means the mandate is already being missed and nothing detects
  that.**
- **`UNI.Minecraft/.claude/hooks/`** — exactly two files, `fe_touch_needs_verdict.py` and
  `no_percent_scoring.py`, **both git-tracked**. The first refuses a `git commit|push|merge|rebase`
  when a free-energy file is dirty without a merged-verdict receipt covering HEAD, and audits any
  bypass. **It is real, careful code with a CI mirror at
  `production/scripts/ci_fe_touch_check.sh`.**

**And here is the adverse result, said first and not softened: those two hooks are installed and
unwired, so neither has ever fired.** No settings file reachable from this box declares a `hooks`
block — the user settings carry only `permissions` and `skipDangerousModePermissionPrompt`; the
project-local settings carry only `permissions`; **neither repository contains a
`.claude/settings.json` at all.** The hook's own fallback write path, `logs/ship_gate_bypass.log`,
**does not exist** — consistent with never having run. *(A hooks block could exist in a settings file
on another machine or in a managed path not inspected this session.)*

**Why this plan does not answer row 11 with `evidence/agent_sessions.ndjson`.** An agent-written log
of agent activity is worth exactly what a `presence_evident` decision row is worth. **It is not
evidence of what an agent did; it is evidence of what an agent chose to record**, produced by the same
process whose honesty is the thing in question — **the single easiest laundering channel in the
repository: a surface that looks like oversight and is self-reported. Building it would make row 11
look fixed while making it worse.**

> **The agent harness writes nothing into any repository in this project. Every record of agent
> activity that exists — 77 comment rows, 37 flow-journal rows, every receipt, every commit message —
> was written by the agent about itself, after the fact, at its own discretion. There is no
> independent record of what any language model did in this codebase, and this plan does not create
> one, because a self-written one would be worse than none.**

**The one thing that would actually help is the operator's, not an agent's, and it is cheap:** wiring
the two hooks that already exist and are already tracked. That is a change to harness configuration
(§8 row 16). **The question to put to him, and nothing beyond it: shall the two tracked hooks in
`UNI.Minecraft/.claude/hooks/` be wired so that they run?** A wired `fe_touch_needs_verdict.py`
produces **the first record in this project written by something other than the agent it
constrains** — one bypass row at a time, from outside the agent's own account of itself.

## 3.4 THE INTAKE — everything is seen coming in

**The finding first: there are no git hooks. Anywhere.** Fourteen `.sample` files in
`UNI-FLAGELLUM/.git/hooks`, fourteen in `UNI.Minecraft/.git/hooks`, and the math-workbench worktree
shares the parent's empty hooks directory via its gitfile. No `core.hooksPath` override, no
`.githooks/` in either tree.

**And the hardest limit, stated before the design:**
`C:/Users/mpolz/Documents/UNI-Flagellum/.git` **does not exist**. The `CLAUDE.md` sitting there is
in no repository. **No hook this plan installs can ever see it.** The intake ledger cannot cover
it, and this plan does not pretend otherwise — it records it as intake row zero, class
`UNTRACKED_HAZARD`. Fixing it is a repository-layout decision and is the operator's.

### `evidence/intake.ndjson` — NEW, append-only, hash-chained

Same chain shape as `evidence/control_plane/ledger.ndjson` (`seq`, `prev_hash`, `hash`) so a reader
who can verify one can verify the other.

```jsonc
{ "schema_version": 1, "seq": 41, "utc": "...",
  "kind": "equation|parameter|proof|dataset|module|constant|schema|claim",
  "id": "eq.vfe.mean-field",
  "title": "Variational free energy, mean-field factorisation",
  "truth_class": "REDUCED_MODEL",
  "source_pin": { "kind":"doi|url|isbn|repo|derivation|operator_statement",
                  "ref":"10.1016/j.jmp.2017.09.004", "locator":"eq. 2.7, p. 4",
                  "retrieved_utc":"...", "sha256":"..." },
  "introduced_by": "claude", "channel": "hook|operator|agent",
  "landed_at": { "repo":"UNI.Minecraft", "path":"lib/sp/lab/physics.ex", "line":118, "blob":"..." },
  "commit": "1c7e69e",
  "units": "nats",
  "assumptions": ["mean-field factorisation over 3 hidden states"],
  "falsifier": "a computed F that disagrees with the independent oracle beyond 1e-9",
  "supersedes": [], "prev_hash": "...", "hash": "..." }
```

**Refusals (fail closed, each naming its own condition):** unknown `kind`; unknown `truth_class`;
missing `source_pin.ref`; `kind` in {equation, parameter, constant} with `units: null`; duplicate
`id` without `supersedes`; and — **the truth contract's first line made mechanical** —
`truth_class: OBSERVED` without a `source_pin.kind` of `doi|url|isbn` **and** a `sha256`.

**NEW `production/schemas/intake_row.schema.json`**, `additionalProperties: false`, a **sibling**
of `gate_row.schema.json`, not an extension. That schema is frozen and `additionalProperties:
false`, which is exactly why `gate_attempts` became a sidecar (`viewer/gate_attempts.cjs:13-19`).
Same precedent, same reasoning, **no contract amendment and no stop condition tripped.**

### The annotation and the shared parser

`// @intake <id>` blocks in the same grammar as `@limitation` (`viewer/limitations.cjs:46-47`
regex pair, `:65-85` block parser, `:108-146` renderer), so **one parser serves three registers**
(`@limitation`, `@intake`, `@teaches`). `viewer/intake.cjs` exports
`scan/validate/chain/verifyChain/rowsFor/render`, modelled line-for-line on `limitations.cjs` — a
module already gate-proven with 9 live annotations, 0 duplicates, 0 incomplete.

### The hooks (tracked, in `.githooks/`)

- **`pre-commit`** — refuses the commit if a staged file adds something that looks like an intake
  with no `@intake` block. The detector is narrow and named, not clever: a new exported const
  matching `/^(EQ|PARAM|CONST)_/`; a new `.json`/`.csv`/`.parquet` under `data/`, `experiments/`,
  `audits/`, `fixtures/`; a new module under `lib/sp/lab/`. **A refusal names the file, the line,
  and pastes the annotation skeleton.**
- **`post-commit`** — `node viewer/intake_record.cjs --commit HEAD` scans the commit's added lines
  for `@intake` blocks and appends rows.
- **`pre-push`** — refuses to push while `evidence/intake.ndjson` is dirty. This is what makes the
  post-commit append impossible to forget.

**Installation is one line and it is the operator's:**
`git -C <repo> config core.hooksPath .githooks`. It is set in `.git/config`, which is shared with
the worktree, so the stale math-workbench is covered with no second install.

**The honest cost, declared as a `@limitation` BEFORE the hook lands:** post-commit appending
leaves the tree dirty by exactly one file until the next commit. That conflicts with "both trees
clean" in the resume banner and with the rule that unknown working-tree changes are user-owned.
The alternative — staging rows in pre-commit — cannot name the commit the row describes. The dirty
file is chosen, the pre-push hook makes it un-forgettable, and the trade is **written down rather
than discovered.**

**The detector will both over-fire and under-fire, and under-firing cannot be fully closed:** an
equation typed into an existing function body will pass. The gate must state its detector's exact
scope, and the declared coverage claim must be about the ROUTE, never about attempts — exactly as
`gate_attempts.cjs` already words its own claim.

### The operator's own intake

`POST /api/intake/declare` on the lab server (second member of `POST_ALLOWED` at
`lab_server.cjs:107`), fenced identically to `/api/lab/run`: loopback Host plus `x-uni-cc: 1` plus
JSON plus an Origin check. Server-side it forces `channel: "operator"`,
`introduced_by: "michael"`, and stamps `presence: "presence_evident"` with F31's exact honesty
caveat. **Never the word "unforgeable."** This is how *"I am bringing this paper into the lab"*
becomes a row without touching a terminal.

### The gate — `viewer/verify_intake.cjs`, gate_row `intake-ledger-is-sealed`

Six clauses, each able to fail for its own reason:
1. every row validates against the schema;
2. `verifyChain()` holds — contiguous `seq`, every `prev_hash` correct;
3. every `landed_at.blob` exists (`git cat-file -e`);
4. **both directions** — every `@intake` annotation has a row, and every hook-channel row has an
   annotation. This is the completeness check `gate_runner.cjs` already models;
5. **the hook is installed and is the tracked one** — `core.hooksPath` reads `.githooks` and each
   hook's sha256 matches its committed blob. A quietly edited hook is a hook that is not there;
6. **M1 mutation** — the gate injects a row with truth class `OBSERVED` and a `source_pin.kind` of
   `derivation`, and requires its own refusal to fire.

### The Intake wing

**Re-pathed by §0.5:** the intake wing **renders at `app/(lab)/lab/intake/page.lab.tsx`**; the
computation that scans the ledger and classifies rows stays chip-side as `viewer/lab/intake_wing.cjs`
and is read over HTTP. Its L1 material vocabulary crosses **by value, not by file**.
**THE RECEIVING BAY** — recent arrivals as crates on
a loading dock, newest at the front, **material = truth class**, using L1's existing five materials
and the form-not-colour rule (`lab/fixtures/l1_materials.json`); a row whose `source_pin` is
missing renders as **fog** (F24/F25, already implemented and gate-tested). **THE MANIFEST WALL** —
every row, filterable, each printing its own reverification line, exactly as Gaia already does for
the control-plane ledger. **THE QUARANTINE SHELF** — rows failing clause 1 or 6: present, visible,
refused; not hidden, not deleted. **THE DECLARE DESK** — paste a DOI, pick a kind, pick a truth
class, type units, submit.

## 3.5 THE CLASSROOM — every gate teaches, and the teaching is generated

**The principle:** a gate must **declare its own teachable content at the line the gate lives on**,
and the classroom must be **generated** from those declarations. Hand-written teaching drifts in
exactly one direction — toward flattering the gate — which is the argument `limitations.cjs:6-10`
already makes and already proves with a byte-comparison gate.

**NEW `@teaches` annotation**, id equal to the registry entry's `gate_row`, fields:
`asks` (the question, one sentence) . `because` (why anyone should care) . `fails_if` (what would
make it red) . `method` (one of the plan's own M1-M8) . `bites_by` (the exact `path:line` where the
guard actually bites) . `licenses` (what a PASS entitles you to say) . `does_not` (what it says
nothing about).

**`licenses` / `does_not` is the pair that makes this teaching rather than advertising.** It is the
truth contract, per gate.

**NEW `viewer/teaches.cjs`** (sibling of `limitations.cjs`), **`viewer/generate_chalkboard.cjs`**
(writes `docs/control-plane/CHALKBOARD.md`; HALTs on a duplicate id or a block missing
`asks`/`because`/`fails_if`/`bites_by`, exactly as `generate_limitations.cjs:19-29` does), and
**`viewer/verify_chalkboard.cjs`** (gate_row `chalkboard-cannot-drift`):

1. regenerate and byte-compare;
2. every `gate_registry.json` entry has a `@teaches` block whose id equals its `gate_row`;
3. **every `bites_by` resolves to a real `path:line` that exists** — the anti-fabrication clause.
   A wrong line number in teaching material is precisely the failure the operator complains about;
   here it is a gate failure;
4. every `method` is one of M1-M8, read live from `phase9_plan.json`.

**Clause 2 lands RED today: 28 registered gates, 0 `@teaches` blocks.** That is correct and is
itself the finding. But a red gate that stays red for weeks trains the operator to ignore red — the
precise failure `room.ex`'s own docstring warns about. **So the gate reports a covered/total count
and goes RED only on a REGRESSION** until all 28 are authored, at which point clause 2 becomes
absolute. That is a deliberate softening of the *schedule*, not the *criterion*, stated here rather
than discovered later.

**Nothing mechanical catches wrong prose.** Clause 3 catches a wrong line number, not a wrong
sentence. That limit is printed in the chalkboard's own header. Concrete live example:
`viewer/lab/desk.cjs:668-672` asserts the `SEALED_BY_S10` branch *"is currently UNREACHABLE for
every registered gate"* — and one lens **executed** `canRun('hud')` today and got `SEALED_BY_S10`,
sealed by three PENDING rows through the `hud-*` glob. **A classroom generated from source comments
before that class of claim is audited would teach a falsehood on day one.**

## 3.6 THE DESK BECOMES A CLASSROOM — fold into L5, do not build a new room

`/lab/l5` already stands the operator in front of a gate and prints the exact ledger line, and
`desk.cjs`'s named refusal codes (`NOT_IN_REGISTRY`, `SEALED_BY_S10`, `NEEDS_THE_WORLD`,
`OUTSIDE_THE_REPO`, `NOT_AT_HEAD`, `REGISTRY_NOT_AT_HEAD`, `REGISTRY_DRIFTED`) already name *which*
condition failed in operator-readable prose. **That is 80% of a classroom.** What is missing is the
why-it-matters half and any persistence.

Standing at a station walks five panels:

1. **THE QUESTION** — `asks`, one sentence, largest type on the board.
2. **WHY ANYONE SHOULD CARE** — `because`.
3. **WHAT WOULD MAKE IT RED** — `fails_if`, plus a live link to the `bites_by` line.
4. **YOUR PREDICTION** — two buttons, PASS or FAIL, **before RUN exists**. This is the whole
   difference between a classroom and a log, and it is the project's own OBSERVE, PREDICT, ACT law
   applied to the operator instead of only to the agent.
5. **RUN IT** — the existing `POST /api/lab/run`, streaming; then the AFTER row beside the BEFORE
   row; then his prediction beside the result; then a row appended to `bench_runs.ndjson`.

**RUN is ABSENT — not greyed — until a prediction is recorded.** A refusal drawn as a disabled
control invites clicking; a refusal that is absent teaches the rule.

## 3.7 STEERING — the NEEDS YOU rail

**Sixteen-ish things are waiting on the operator right now and no surface says so.**
Measured: checkpoints A, B, C and AIR are `OPERATOR`; steps 5.5 and 6.4 are `OPERATOR`; 3.3 is
`BLOCKED`; 4.6 is `IN_PROGRESS`; stops are armed on steps 4.2 (S4), 5.5 (S5) and 6.4 (S6); there are
six `not_mine` entries. **The deduplicated union was NOT computed by any lens — the code must
compute it, and this plan must not state a number it did not run.** (See section 10.)

**NEW `evidence/operator_decisions.ndjson`**, append-only, hash-chained:

```jsonc
{ "schema_version":1, "seq":3, "utc":"...",
  "subject": { "kind":"checkpoint|step|stop|not_mine", "id":"B" },
  "question_verbatim":"he rules on my verify_host_tracking retraction",
  "he_saw": [ { "path":"docs/receipts/control-plane/phase9_1.3_green_2026-07-27.txt", "sha256":"..." } ],
  "proof_artifact":"A5",
  "verdict":"ACCEPT|REJECT|HOLD|NOT_MINE|NEEDS_MORE",
  "in_his_words":"the retraction stands",
  "actor":"michael", "presence":"presence_evident",
  "prev_hash":"...", "hash":"..." }
```

`question_verbatim` is **copied from the plan's `he_does`, never paraphrased.**
**HOLD is a real answer and must be as easy to give as ACCEPT.** A decision surface offering only
"approve" is a surface that manufactures approvals.

**The plan file stays hand-edited by an agent.** That boundary is deliberate and stops the UI
becoming a plan editor. What changes: a status may not move away from `OPERATOR` without citing a
decision-row `seq`.

**EDIT `viewer/track/track_server.cjs`** — `plan()` (`:300-339`) gains `needs_you`, computed from
the file it already parses, minus every subject already carrying a decision row.
**EDIT `viewer/track/track.html`** — a new section rendered **first**, above the plan (`:359`).
One card per item carrying, in this order: (1) **the one move, in his words, from `he_does`
verbatim**; (2) what he must look at, resolved to a real path with a sha256 and a link; (3) which
proof artifact this is, A1 to A6, so he knows whether he is recomputing a number, watching a guard
bite, reading a diff, or looking at two images; (4) three buttons — **ACCEPT . HOLD . NOT MINE** —
and a free-text box; (5) why it is his: the stop's `why` string, verbatim.

**Never a menu of options.** The flow has one next act; the rail shows it and asks for the co-sign.

**`POST /api/decision`** reuses the **already-exported, already-unit-tested** fence functions
`isLoopbackPeer`/`isLoopbackHost` (`track_server.cjs:48-57`, exported at `:530`). It forces
`actor: "michael"`, `channel: "track"`, and **never writes `phase9_plan.json` and never writes
`evidence/gates.ndjson`** — S4 and S5 stand untouched.

> **`viewer/track/track_server.cjs` (530 lines) states its write law TWICE, in TWO DIFFERENT
> SENTENCES, and both must be corrected in the same commit.** `:25` — *"The ONLY thing it writes is
> `evidence/track_comments.ndjson`"* — and `:11` — *"Every route here except POST /api/comment is a
> pure read. Nothing is actuated by looking."* They are **not the same string**, so a
> find-and-replace on one leaves the other standing and false. `:18` — *"this server owns
> NOTHING"* — is the third sentence in the same family. Otherwise the file becomes a file
> describing itself as it was, which is the exact defect `lab_server.cjs:12-23` records about itself.

**EDIT `viewer/verify_plan_consistency.cjs`** (already registered as `plan-consistency`), two new
clauses: (a) a status that moved off `OPERATOR` with no decision row is a decision an agent made on
his behalf, and fails; (b) `verifyChain()` over the decisions holds and every `he_saw[].sha256`
matches disk. Plus M1: injecting a status flip with no decision row must exit 1.

**Honesty caveat that rides on every render:** `presence_evident` means an agent inside the
operator's desktop session could forge a row. If any surface ever renders a decision row as *proof*
that Michael decided something, the ledger becomes a laundering channel. The caveat is inline, the
way F31's grants carry it.

## 3.8 THE AIRLOCK GETS A DOOR IN THE UI, AT LAST

`SP.ControlPlane.Room` has never run outside its test files. It is the *one place in the codebase*
that already models two-party authorisation with receipts hashed in and **no override function**,
and the operator has never seen it.

Add a fourth room to `/lab/l4` (`viewer/lab/rooms.cjs`, `l4.html`): `the-control-plane-airlock`,
rendering `Room.conditions/4` for a real candidate crossing **as a pure read** — which `room.ex:96-99`
already guarantees always answers. Green, clean, sterile, with each unmet condition printed in the
words `room.ex` already writes, and `no_door` where a key is missing.

**It draws the door and it cannot walk through it** — the rule `rooms.cjs:28-31` already states for
the go-live door and which applies identically here. This costs one read call and shows him a thing
he has never seen.

## 3.9 THE LLM CASEBOOK — generated from a corpus that already exists

**The denominator is confirmed: 689 commits across the two repositories** — 113 (MAIN) + 576
(CHIP-SIDE); the STALE worktree's 42 are excluded. **The numerator 278 is WITHDRAWN**: it reproduces
under no pattern anyone has stated, and it is the sum of two per-tree figures (201 + 77) produced by
a regex the draft never gave. Six patterns were run and none returned it (131, 192, 397, 505, 128,
379).

**So here is a stated pattern, and every number in this section uses it.** Commits whose **SUBJECT
LINE** matches, case-insensitively,
`fix|correct|retract|revert|repair|amend|withdraw|honest|false|wrong|stale|drift|defect|refute|undermine`:
**192 of 689** (MAIN 37/113, CHIP-SIDE 155/576), by `git log --pretty=%s | grep -Eci`. Widen the same
pattern to the full message body and it is **505 of 689**. **A count with no stated pattern is not a
measurement**, and this section is about self-correction, so it had better hold itself to that
first. The corpus is enormous and entirely unindexed.

| source | measured | holds |
|---|---|---|
| `docs/control-plane/FAILURE-MODES.md` | 187 lines | F1-F31 plus at least three in-document corrections, incl. `:171-185` *"CORRECTION — the F8 residual is NOT closed, and the paragraph above claiming it is has been false since at least 2026-07-26"* |
| `docs/audit/` | 3 files, 1189 lines + 12 evidence files | the ~55-defect self-audit |
| `hierarchical-aif/reports/` | 46 files | `CORRECTION-NOTICE-ISSUED.md`, `D5-HOLDOUT-MARK-CHANNEL-BURNED.md`, `D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md`, `D12-INCIDENT-CONTAINMENT-REPORT.md`, four `B4C*-CORRECTED-FULL-REPORT.md` |
| `hierarchical-aif/ledgers/` | 4 files | defect ledger, closure ledger, negatives-and-partials |
| `UNI.Minecraft/docs/receipts/` — **and only there**; MAIN and STALE have no such directory | **70 files + 2 subdirs at depth 1** (63 of the 70 are `.md`); **136 files / 72 `.md` recursively** | red/green receipt pairs, schema corrections |
| `phase9_plan.json` | 43 steps | **already a structured casebook** — see the key list below |
| inline source | throughout | `gate_runner.cjs:86-98`, `lab_server.cjs:12-23`, `desk.cjs:210-217`, `desk.cjs:280-284` |

The plan's own self-incriminating key vocabulary, measured as the union of step keys:
`RETRACTION_finding_B_was_wrong` . `my_test_was_wrong` . `defect_i_introduced` . `f10_caught_me` .
`it_caught_me_twice_more` . `my_own_test_fell_into_4_4s_trap` . `finding_corrected_2026_07_28` .
`counts_corrected_2026_07_28` . `status_correction` . `acceptance_NOT_met` .
`why_it_cannot_now_be_met` . `adverse` . `landed_red` . `a_measurement_is_not_a_verdict`.

**Three harvesters, one renderer, one anti-fabrication gate** — `viewer/casebook.cjs`:

- **H1, the plan harvester.** Walks `phase9_plan.json` over that **fixed key vocabulary**, not a
  regex over prose. **Produces at least 13 cases on the first run with no new authoring** — which
  is why the casebook starts non-empty.
- **H2, the source harvester.** A new `@mistake` annotation, same block grammar, placed at the line
  the mistake lived on (`what`, `who`, `cost`, `caught_by`, `fixed_in`, `lesson`). Retrofitting the
  inline cases above is about seven annotations. Worked example:
  *"a killed gate read as law-compliant because `exit=null` made `(exit === 0) === false` come out
  true"* — lesson: *"a question that was asked and not answered is not an answer of no."*
- **H3, the git harvester.** Reads a declared commit trailer `Self-correction: <one sentence>`,
  exactly as `Co-Authored-By:` is read. **No history carries this trailer today, so H3 returns ZERO
  and the casebook says so out loud.** An honest empty harvester beats a regex guessing at 689
  commit messages — and guessing is the exact failure mode this casebook documents.

`viewer/verify_casebook.cjs` (gate_row `casebook-cannot-drift`): regenerate and byte-compare; every
`proof.path` exists and `proof.line` is in range; **every `verbatim` quote is byte-present at
`proof.path:proof.line`** — a casebook about fabricated detail whose own citations were fabricated
would be the single most embarrassing artifact in the repository; and H1's key vocabulary is a
subset of the keys actually present in the plan, so a renamed plan key fails rather than silently
dropping a case.

**Class bands, derived from what the corpus actually shows, not invented:** *fabricated detail* .
*stale claim standing unchecked* . *a guard that passed vacuously* . *a count that was wrong* .
*scope creep past a stop* . *a retraction*.

**Seed case, class `fabricated detail`, and it happened inside this document.** A revision pass of
this plan wrote at its head that `modelSnapshot()`'s `new Date().toISOString()` was *"a **fourth**
ambient clock, beyond … the one at `uni-motor.js:408`."* It is the clock at `uni-motor.js:408`; the
agent double-counted one line against itself, almost certainly because `walkthrough.js` also carries
a clock at `:408`. It was presented as newly measured, it was never measured, and §2.1's purity
table and §9.2 had both already recorded the correct count of three. It was caught by an adversarial
re-derivation against disk, in the same document that specifies this casebook. **`who`: the revising
agent. `cost`: one false impurity in the head summary and one inherited "fifth impurity" in §4.10.
`caught_by`: hallucination audit, second pass. `lesson`: two files with the same line number are not
two findings — a citation you did not open is not a measurement.** It is retracted in full at §*FOUR
THINGS THE AGENT TOLD THE OPERATOR THAT WERE WRONG* and corrected in §4.10.

**The counter**, recomputed live, never cached, and **printing its own pattern beside its number**:
*"192 of 689 commits in this project carry correction language in their subject line"* — followed,
in the same element, by the regex it used and the field it ran over. A counter that shows a number
and hides its predicate is how 278 got into this document.

**The standing sentence**, at the top of the wing and on TRACK's header, rotating one case per
session: *this laboratory was built substantially by a language model, and this wall is what that
cost.*

## 3.10 What must NOT be built

- anything that writes `evidence/gates.ndjson` (**S4**);
- anything that edits `phase9_plan.json` programmatically;
- anything that mints a presence token (**F31 / S6**);
- **the word "unforgeable" anywhere in any new surface.**

## 3.11 Acceptance criteria for section 3

1. `node viewer/gate_runner.cjs --record` appends exactly one row per run gate and changes no other
   file. Running it twice produces two rows and a diffable history.
2. `git commit` of a new file under `data/` with no `@intake` block is **refused**, naming the file
   and pasting the skeleton.
3. `node viewer/verify_intake.cjs` exits 1 when (a) a row is edited in place, (b) a hook file is
   altered without committing, (c) the OBSERVED-with-derivation mutation is injected.
4. `curl` of `/api/intake/declare` from a non-loopback Host is refused 403.
5. Editing any `bites_by` line number by one makes `verify_chalkboard.cjs` exit 1.
6. At `/lab/l5`, RUN is **absent** until a prediction is recorded; recording one makes it appear and
   the resulting row carries `predicted_before_run: true`.
7. Pressing HOLD on the NEEDS YOU rail appends a row and the card moves to "answered — HOLD" with
   his words shown back to him. `verify_plan_consistency.cjs` exits 1 when a step's status is
   flipped off `OPERATOR` with no decision row.
8. `node viewer/generate_casebook.cjs` writes `LLM-CASEBOOK.md` with **at least 13 cases from the
   plan alone** on the first run; `verify_casebook.cjs` exits 1 when any `verbatim` string is
   altered by one character; H3 reports `0 cases (no commit carries the Self-correction trailer)`
   rather than guessing.
9. `/lab/l4` shows the green/clean/sterile airlock with its real unmet conditions and **no button
   that crosses it**.
10. `npm run test:record` twice yields two rows with identical `tests`/`pass` and differing
    `wall_ms`; **breaking one assertion still appends a row, with `fail >= 1` and `exit != 0`.**
11. `/receipts` lists **136** entries and **names UNI-FLAGELLUM's zero**. Changing one byte inside any
    indexed receipt makes `verify_receipts_index.cjs` exit 1.
12. The census renders on TRACK with its `fixed by` column live, and **the count of `NOT_FIXED` rows
    is computed from the table rather than typed** — so it cannot drift toward flattery.

---

# 3A. THE SHELL — THE LABORATORY AS A PLACE YOU ARE IN

> **Numbering note.** Additive, exactly like §0, so that no cross-reference anywhere else in this
> document moves. §4 is still THE CHALKBOARD; §5 is still THE WINGS.

> ### THIS SECTION IS WORKSTREAM **W2b**, AND IT IS SECOND IN §7.1
>
> **id:** `W2b — THE SHELL` · **first file:** `UNI-FLAGELLUM/lib/shell/wings.js` (new) ·
> **depends on:** `W2a` · **size:** **3–5d** · **trees:** MAIN ·
> **acceptance:** §7.3 W2b, which is §3A.10's ten criteria in the house format.
>
> **The previous draft specified this section in 587 lines and gave it no id, no size, no dependency
> row and no place in §7** — it appeared in all of section 7 exactly once, as the bare token `3A` in
> W22's Depends-on column. **Nothing else in the laboratory is reachable without it.** §0.9 decision 1
> records the correction. **Why it is second and not later: nothing that renders a room can precede
> it, because §3A.10 criterion 3 asserts the frame is on EVERY lab route, so any room built before the
> shell fails that criterion the moment the shell lands.** Why it is not *first*: §0.8 forbids any
> `app/(lab)/` route before W2a's release-exclusion gate exists and its mutation has gone red.

## In plain words

**Six gate verdicts in this repository say FAIL right now, they are committed, they are already
imported by a shipping React component, and not one of them is on screen when the application first
paints.**

Measured: `experiments/results/science-gates-report.json` — 14 gates, `generatedAt`
`2026-07-17T23:00:00Z`, `statusCounts {"PASS":4,"FAIL":3,"SOURCE_ONLY":1,"BLOCKED_EXTERNAL":5,
"NOT_ESTABLISHED":1}`, `overall: "PARTIAL_PARITY_ONLY"`, failures `G03_PUBLIC_ARTIFACT_PARITY`,
`G05_SYNTHETIC_RECOVERY`, `G06_HELDOUT_MECHANISTIC_PREDICTION`.
`experiments/results/cross-study-parity-report.json` — 16 gates, `executedAt`
`2026-07-17T20:30:00Z`, `{"PASS":8,"FAIL":3,"BLOCKED_EXTERNAL":3,"NOT_ESTABLISHED":2}`, failures
`X06_FINITE_LATTICE_COOPERATIVITY`, `X11_STRUCTURAL_CONSISTENCY`, `X16_FULL_BIOLOGICAL_PARITY`.
Both are imported at **line 1** of `app/science-gates-panel.tsx` and `app/cross-study-parity-panel.tsx`.
And `app/uni-flagellum-lab.tsx:466` initialises `panel` to `"loop"`, so **on arrival the tab that
would show them is not the tab you are on.**

That is the whole of this section in one fact. **The evidence is present, correct, honest and
unreachable.** Not because anyone hid it — because there is nowhere to stand from which the
laboratory is visible as a whole. There is one URL, no map, no room list, no way back, and no front
door.

This section builds the front door.

## 3A.0 The finding this section closes, and the re-run of it

The finding against the previous draft, verbatim:

> *"THE REQUIREMENT `a full interactive interface like a complete interactive video game, but real`
> IS NEVER QUOTED, NEVER NAMED AND NEVER DESIGNED AGAINST. Grepped case-insensitively for `game`
> across all 2919 lines: ZERO occurrences. There is no navigation model, no map, no traversal, no
> persistent place the operator occupies, no progression, no save state, no continuous feedback, no
> single entry point."*

**Re-run against the draft file — and the draft file must be named, because the obvious guess
inverts the result.** The subject is `scratchpad/LAB-PLAN-DRAFT.md`, the **2,918-line / 201,999 B**
working draft in this session's scratchpad — **not** `UNI-FLAGELLUM/docs/THE-LABORATORY-PLAN.md`,
the 436-line / 28,357 B first draft committed at `4f6485e`, against which the census FAILS
(`grep -ci game` = **1**, at `:20`, the R1 row quoting the operator's *"like a complete interactive
video game, but real"*; `grep -ci "home screen"` = **0**). Against `LAB-PLAN-DRAFT.md` it holds, and
every count below was re-run on it this session. `grep -ci`: `game` **0**, `lobby` **0**,
`navigation` **0**, `you are here` **0**, `progression` **0**, `save state` **0**, `home screen`
**1** — and that single occurrence calls the resonance lattice *"the honest headline number for the
operator's home screen"* **while never designing the screen.**

One correction to the finding, in its own spirit: **`wc -l` on the draft returned 2918, not 2919**,
and the file does end in a newline. Immaterial; recorded because this plan has already been convicted
once of sizing a file by counting its lines (§10.0 correction 2).

**And the same absence is measurable in the code, not only in the plan.** `grep -rn` for
`next/navigation|pushState|useRouter|next/link|<Link` across MAIN `app/` returns **exactly one hit**:
`app/chatgpt-auth.ts:2`, a `redirect` import in a non-route module. **MAIN's laboratory contains no
link, no router and no second route** — `find app -name page.tsx` returns `app/page.tsx` and nothing
else.

The stale worktree tried and produced the joke that proves the point:
`UNI-FLAGELLUM-math-workbench/app/math-workbench/scientific-math-workbench.tsx:273` renders
`<Link href="/" prefetch={false}>Return to laboratory</Link>` — and
`UNI-FLAGELLUM-math-workbench/app/page.tsx:9` is `redirect("/math-workbench")`. **The one door either
tree has ever had is a link to a redirect back to the room you are standing in.**

## 3A.1 What "like a video game, but real" means here — and the six things it forbids

It does **not** mean 3D, WebGL, Three.js or a physics toy. The product contract forbids all of them
(`CLAUDE.md:69-72`, quoted in full at §6.9.1).

**A scope trap that will otherwise be walked into.** `docs/control-plane/ARCHITECTURE.md:259` says:

> **Rendering constraint scope.** The flagellum *released product* forbids WebGL, GPU, Three.js,
> accounts and network. That fence is the flagellum's and still binds it. The **lab does not inherit
> it** — this platform already renders in THREE with shadows and ACES tone mapping.

That sentence is about the **SP.Lab control-plane platform** — a separate artifact on a separate
port — **and the document that says it lives at
`UNI-FLAGELLUM/docs/control-plane/ARCHITECTURE.md`, inside THIS repository, describing that other
artifact.** *(A previous revision said the file was in `UNI.Minecraft`. Measured:
`find . -name ARCHITECTURE.md -not -path '*/node_modules/*'` over `UNI.Minecraft` returns nothing;
the file exists only in MAIN. The one paragraph whose entire job is stopping a builder reading the
right document about the wrong lab was itself sending him to the wrong tree — which is a sharper
version of the same warning, not a weaker one.)* **The shell this section builds lives in `UNI-FLAGELLUM/app/(lab)/` — inside the
released product's repository and inside its build — so it inherits the fence in full.** Two things
are called "the lab" in these repositories and **they have opposite rendering rights.** A builder who
reads ARCHITECTURE.md §8 and reaches for `three` in `app/` has read the right document about the
wrong lab. This paragraph exists to stop that. *(§0.4's assertion 5 and §6.9.4's A1/A2 both bite if
it happens anyway.)*

So "like a video game, but real" means the six properties a good game has that a document does not,
and nothing about the rendering technology:

| | property | what it means here | what would violate it |
|---|---|---|---|
| **G1** | **One place you are in** | a single home screen listing every wing and every room that exists, with its state | seven ports and a bookmark folder |
| **G2** | **Movement costs one action** | every room has a URL and a link; never a typed address | `useState` tabs that the Back button escapes |
| **G3** | **Persistent state** | it remembers the room, the mode, the level, and what you were working on | losing your place on refresh |
| **G4** | **Continuous feedback** | a gate going red is visible from across the room, **without motion** | a pulsing dot that means "alive" |
| **G5** | **Real progression** | proven / pending / blocked / not-built, named per wing, never averaged | a percentage, a score, a streak, a badge |
| **G6** | **Everything reachable** | no hidden rooms, no dead ends, nothing that needs a terminal | a wing you can only see by reading source |

**G4 is the one that fights the contract, and the contract wins.** See §3A.8 — it is not a
compromise, it is the more interesting design.

## 3A.2 A continuously-running world already exists, and this plan never noticed

`app/uni-flagellum-lab.tsx` is 880 lines and it is **already a live world**, not a document.

- **The run loop.** `:486-525` (the `setInterval` body is `:488-523`). A `window.setInterval(..., 80)` (period at `:523`), `previous =
  performance.now()` at `:487`, `dt` clamped to `[0.01, 0.1]` at `:492`, short-circuiting on
  `if (!runningRef.current) return;` at `:494`, advancing either the live serial observation
  (`:498-506`) or `stepSyntheticSystem(...)` (`:508`; `:507` is the bare `} else {`), appending to a rolling 180-point history at
  `:512-522` (`slice(-179)` at `:513`, plus the new point = 180). **This ticks 12.5 times a second, today, in the shipping product.**
- **The Run/Pause control.** `:647-649` (`data-testid="run-toggle"` on `:647`; `:646` is the enclosing `<section className="command-bar">`), over
  `const [running, setRunning] = useState(true)` at `:461`, mirrored into `runningRef` at `:474` and
  `:484`. It defaults to **running**.
- **Seven `type="range"` sliders.** Four world causes — `:674` base ligand, `:678` gradient, `:682`
  mechanical load, `:686` ion-motive force — and three CAD parameters at `:817-819`. Two more world
  sliders are duplicated into the walkthrough at `living-science-walkthrough.tsx:300-301`.
- **Two canvases drawn from state** — the motor canvas at `:698-699` (`<canvas` opens `:698`,
  `ref={motorCanvasRef}` on `:699`) and the trace canvas at `:749`; refs declared `:476-477`; both
  redrawn by the effect at `:527-530`. *(A previous revision cited `:691-695` and `:526-529`.
  Measured: `:691` is a `<dl>` statistics row and `:695` is `</aside>` — no canvas in that range —
  and `:526` is blank while `:530` is the effect's dependency array.)*
- **A second animated surface.** `biological-stage.tsx:225-271` — `requestAnimationFrame` at `:265`,
  four cameras at `:261-264`, honouring `prefers-reduced-motion` at `:245`.
- **A seven-tab view switcher that is not navigation.** `type Panel` at `:25`, state at `:466`, the
  `<nav className="panel-tabs">` at `:737-743`. Seven rooms — loop, math, cad, observed, gates,
  cross, evidence — **none of which has a URL, a link, a Back button or a bookmark.**
- **The stale tree has a second, incompatible one.** `type View` at
  `scientific-math-workbench.tsx:59`, six values, state at `:214`, nav at `:285`. **Two in-component
  tab switchers, in two trees, with different vocabularies, neither writing the URL.**

**The honest read: the world is built and the building around it is not.** The plan has been treating
this application as a set of panels to add panels to. **It is a running instrument with thirteen
rooms and no corridor.**

Everything below is a corridor, a map and a frame. **No new physics, no new equations, no new
mathematics.** The most expensive line in this section is a `<Link>`.

## 3A.3 What exists to build on — and what is a different stack

The rule applied throughout: **an idea can cross a stack boundary; a `.cjs` file cannot.** This is
§0.5's re-pathing rule, seen from the other side.

| asset | measured | reusable in MAIN's React app? |
|---|---|---|
| `app/uni-flagellum-lab.tsx` (880) | React 19.2.6 / Next 16.2.6, TSX, in the product | **This IS the stack.** Everything in §3A.4-3A.7 is written against it. |
| `app/layout.tsx` (20) | `next/font/google` Geist + Geist_Mono, one `<body>{children}</body>` at `:17` | **Shared with the product (§0.3), so it does NOT get the frame.** The frame goes in `app/(lab)/layout.lab.tsx`. |
| `app/globals.css` (544) | 0 `@keyframes`, exactly 2 `transition:` (`:49` button hover, `:144` `.probability-track i` width), 2 `prefers-reduced-motion` blocks (`:389`, `:531`), 1 `@media print` (`:534`) | **Yes, and it already obeys the liveness rule nobody wrote down.** See §3A.8. |
| `viewer/lab/projection.cjs` (169) | CommonJS, Node builtins, reads `UNI.Minecraft/evidence/gates.ndjson`; `materialOf` at `:49-59`; 1 Hz diff-suppressed poll at `:147-166` | **Not as code.** **Yes as contract:** `materialOf`'s truth_class→material mapping and the diff-suppression argument at `:147-149` are ported **by value, not by file**. |
| `viewer/lab/l4.html` (320) | canvas 2D at `:83`, iso/unIso at `:98-103`, `wall()` `:119`, `drawDoor()` `:131` (three doors as three branches, deliberately not one branch with three colours), avatar `you` `:68` drawn `:209`, WASD `:234`, click-to-move `:236`, 5 s poll `:316` | **Different stack.** The iso projection is five lines of arithmetic; re-derive if ever wanted. **Do not port the avatar** — walking to a room costs many actions; G2 says one. The concourse stays chip-side. |
| `viewer/lab/l6.html` (169) | canvas `:44`, six pillars `:96`, a **dashed PENDING pillar** `:107-108` so a tired reader does not read mid-run as dead, a barred threshold `:122`, 2 s poll `:165`, and at `:12-13` *"There is no GO button here, and there never will be"* | **Different stack.** One idea crosses: **a threshold that has no button on it.** The map's DOOR tile is that idea. |
| `viewer/lab/rooms.cjs` (303) | `probePortals` `:277-301` (JSDoc `:274-276`) — loopback-only guard `:285-287`, GET only, 800 ms timeout, `not_probed` **never** rendered as `down` | **Not in the product.** **Yes in `scripts/`** — the working model for §2.9's dev-only broker, and its `not_probed` discipline is law in §3A.8. |
| `lab.html` (230), `l1.html` (255), `l3.html` (199), `l5.html` (289), `desk.cjs` (679), `lab_server.cjs` (383) | 19 files on `127.0.0.1:8103`, routed by exact `url.pathname` | **Different stack, and it stays.** MAIN's map reaches it as a **portal**, under §3A.8's liveness rules. |
| STALE `app/globals.css` (702) | 6 undeclared `var()` names, four of them `--cyan --failure --gold --void` | **A hazard on arrival, not today** (§4.5, now settled). The frame's truth-class legend declares its own tokens in MAIN and must not inherit the stale four. |

## 3A.4 THE MAP — one screen, every room, live state, two moves

**The map is `/lab`, served by `app/(lab)/lab/page.lab.tsx`.**

> **Reconciled with §0, and the reconciliation is a simplification.** An earlier draft of this
> section had `app/page.tsx` stop being the bench and become the map. **Under §0.2, `/` stays the
> product** — `app/(product)/page.tsx` still renders `<UniFlagellumLab/>` — and the laboratory front
> door is `/lab`. Two consequences, both good: **`tests/rendered-html.test.mjs` keeps all twelve of
> its assertions at `/`, unchanged and unweakened**; and the bench that ships is the bench that ships,
> while the map is lab-only and cannot leak into the release (§0.4 assertion 4).

### Files

| file | new / edit | what it is |
|---|---|---|
| `lib/shell/wings.js` | **NEW** | **THE MANIFEST.** The only enumeration of rooms that exists. Pure data, no imports, no `fetch`. |
| `lib/shell/wing-state.js` | **NEW** | Pure: manifest + snapshot → the tile model. No I/O. |
| `lib/shell/wing-state.snapshot.json` | **NEW, generated, committed** | The frozen reading. Carries `captured_at`, source hashes, per-wing counts. |
| `scripts/freeze-wing-state.mjs` | **NEW, dev-only, never bundled** | Builds the snapshot from the committed reports and, if the sibling checkout is present, the chip-side ledger. |
| `app/(lab)/lab/page.lab.tsx` | **NEW** | The map. Server component; renders tiles from `wing-state.js`. |
| `app/(lab)/lab/wing/[wing]/page.lab.tsx` | **NEW** | One dynamic route, `generateStaticParams` driven by the manifest, so a wing cannot exist without a room and a room cannot exist off the manifest. |
| `app/(lab)/lab/wing/[wing]/[room]/page.lab.tsx` | **NEW** | The second and last level. **There is no third.** |

### The manifest

```js
// lib/shell/wings.js — the only enumeration of rooms that exists.
export const WINGS = [
  { id:"flag",   title:"THE FLAGELLUM BENCH",  section:"5.1", built:true,
    rooms:[ {id:"loop", title:"the live loop"}, {id:"math", title:"the math"},
            {id:"cad",  title:"the physical analogue"}, {id:"observed", title:"the observed experiment"} ],
    state_from:["science-gates","observed-experiment"] },
  { id:"parity", title:"CROSS-STUDY PARITY",   section:"5.2", built:true,  rooms:[...], state_from:["cross-study"] },
  { id:"haif",   title:"HIERARCHICAL AIF",     section:"5.3", built:false, rooms:[], state_from:[] },
  { id:"planet", title:"THE PLANETARY BENCH",  section:"5.4", built:false, rooms:[], state_from:[] },
  { id:"colony", title:"THE COLONY BENCH",     section:"5.5", built:false, rooms:[], state_from:[] },
  { id:"genome", title:"DIGITAL DNA",          section:"5.6", built:false, rooms:[], state_from:[] },
  { id:"gate",   title:"THE GATE BENCH",       section:"5.7", built:false, rooms:[], state_from:[] },
];
export const STANDING = [
  { id:"chalkboard", title:"THE CHALKBOARD",   section:"4",    built:false },
  { id:"proof",      title:"THE DERIVATIONS",  section:"4.6",  built:false },
  { id:"stepper",    title:"THE STEPPER",      section:"4.10", built:false },
  { id:"compare",    title:"COMPARE",          section:"2",    built:false },
  { id:"intake",     title:"THE INTAKE",       section:"3.4",  built:false },
  { id:"casebook",   title:"THE LLM CASEBOOK", section:"3.9",  built:false },
  { id:"airlock",    title:"THE AIRLOCK",      section:"3.8",  built:false },
];
export const PORTALS = [
  { id:"track", title:"UNI TRACK — NEEDS YOU", url:"http://127.0.0.1:8102/", section:"3.7" },
  { id:"lab",   title:"THE CHIP-SIDE LAB",     url:"http://127.0.0.1:8103/", section:"3A.3" },
];
```

Wings from the §5.0 inventory, standing rooms from §§2/3/4, two portals. **The tile count is
`WINGS.length + STANDING.length + PORTALS.length`, computed at render, and it is deliberately not
written here as a number — the previous draft wrote "Fourteen tiles" one line after declaring that
the count "is a consequence of the manifest, never typed into a heading", and then §3A.10 transcribed
the fourteen a second time. Two rooms have since been added and one withdrawn, so both transcriptions
were already wrong.** §3A.10 criterion 1 asserts the rendered tile count **equals the manifest
length**, so a correct run cannot fail its own gate.

**`compare` and `proof` are in `STANDING` because §0.3 declares their routes and §3A.10 criterion 6
asserts set-equality between route files and the manifest** — a declared route absent from `STANDING`
turns the shell's own suite red. `classroom` is deliberately **not** here: §3.6 folds it into
`/lab/l5` chip-side, and its §0.3 row is withdrawn (§0.9 decision 2's table).

### Each tile carries exactly four things, and they are four different kinds of fact

1. **NAME and one line of what it computes.** Always.
2. **BUILT / NOT BUILT.** A fact about this repository, known from the manifest at build time. Always
   safe to render, never a probe.
3. **THE VERDICT MARK — a claim about the past, stamped with when.** `4 PASS · 3 FAIL · 5 BLOCKED ·
   1 SOURCE_ONLY · 1 NOT_ESTABLISHED — as recorded 2026-07-17T23:00:00Z`. **The timestamp is not
   optional and is not a tooltip.** A verdict with no capture time is a claim about now that nobody
   measured.
4. **THE LIVENESS DOT — a claim about right now.** Drawn **only** where a probe answered. In OFFLINE
   there is no probe, so **the element is absent from the DOM entirely** — not grey, not dimmed, not
   "unknown". See §3A.8.

**Points 3 and 4 are the design.** A gate verdict and a liveness dot are different kinds of claim and
**drawing them the same way is the laundering this whole plan exists to prevent.**

**Portal tiles are governed by a rule that already exists.** `ARCHITECTURE.md:279`: *"World portals
along one wall — look through to that world's own view, step through to work in it; **a portal never
re-derives its world's state and a down world renders dark.**"* So the TRACK and chip-side-lab tiles
show **that surface's own reported state or nothing at all** — never MAIN's guess about it. In
OFFLINE, with no probe, they carry the word `NOT WATCHED` and no dot, **and the link still works,
because a link is an offer to look, not a claim to have looked.**

### Where the state comes from — and the two-repository problem, stated

**Measured: MAIN contains no `.ndjson` file at all** and has no `evidence/` directory. The canonical
gate ledger `evidence/gates.ndjson` exists **only in `UNI.Minecraft`**. So **the map cannot read it
from inside the product, and must not pretend to.**

What MAIN *does* have, committed and already imported by shipping components:
`science-gates-report.json` (14 gates, `2026-07-17T23:00:00Z`, imported at
`science-gates-panel.tsx:1`); `cross-study-parity-report.json` (16 gates, `2026-07-17T20:30:00Z`,
runId `454bfc6c…`, imported at `cross-study-parity-panel.tsx:1`); `observed-experiment-report.json`
(runId `faa689de…`, imported at `observed-experiment-panel.tsx:1`).

**So the map reads exactly what the panels already read, and invents no second source of truth.**

`scripts/freeze-wing-state.mjs` merges those three into `lib/shell/wing-state.snapshot.json` and,
**if and only if** a sibling `UNI.Minecraft` checkout is passed on the command line, adds the
chip-side ledger counts with that ledger's `sha256` and the sibling's `git rev-parse HEAD`.
**If the sibling is absent, every chip-side wing is written `NOT_MEASURED` with the reason, and the
previous snapshot's numbers are never carried forward.** **A stale number silently re-emitted is
worse than an absent one** — the exact failure the CLAUDE.md banner was itself convicted of on
2026-07-28.

### Two moves, guaranteed structurally

`/lab` → `/lab/wing/flag` → `/lab/wing/flag/math`. **Two.** The route tree is two levels deep below
`/lab` and there is no third `page.lab.tsx`; §3A.10 criterion 2 makes adding one fail. A wing with no
rooms (`rooms: []`) is one move — the wing page *is* the room.

### NOT BUILT tiles are present, enterable, and say what is missing

`ARCHITECTURE.md:283` says *"**Refusal is the feature.** An action the evidence does not license is
**absent, not greyed** — a greyed control still teaches that the action exists."* That reads at first
as an argument for hiding unbuilt wings. **It is not, and the distinction matters.**

- **A room is not an action.** The operator's binding requirement is *"Every part and piece has to be
  in the user interface where the world can see it."* An inventory of what does not exist yet is a
  thing to see, **and hiding it makes the laboratory look finished.**
- **What is absent is any action inside it.** A NOT BUILT room has no RUN, no co-sign, no export. It
  has a name, the section of this plan that specifies it, the files that would build it, and one
  sentence saying what is missing. **Nothing is greyed, because nothing is drawn.**

So: **the tile is real, the room is real, the buttons are absent.** That satisfies both rules and
neither is bent.

## 3A.5 THE FRAME — what is on screen in every room, in every wing, always

**Name: THE FRAME.** Not "the rail" — §3.7 already owns that word for the NEEDS YOU decision list in
TRACK, and two things called the rail is how a vocabulary rots. The frame is the border of every
room; it carries the rail's **count**, not the rail.

**`app/(lab)/lab-frame.tsx`** — NEW. **`app/(lab)/layout.lab.tsx`** — NEW, and it wraps every lab
route in `<LabFrame>`. **NOT the root layout**, because §0.3 keeps `app/layout.tsx` shared with the
product and lab chrome must never ship. Because it is in the *lab* layout it cannot be omitted from a
lab room by forgetting, and §3A.10 criterion 3 makes removing it fail.

Six things, in this order, on one line at the top of every lab screen:

| slot | shows | where it comes from | when it is absent |
|---|---|---|---|
| **WHERE** | `LAB / W-FLAG / the math`, the lab word linking home | the route + `wings.js` | never |
| **MODE** | `OFFLINE` · `ONLINE` · `COMPARE` | `lib/shell/mode.js` (§2.1) | never |
| **LEVEL** | `play` · `lab` · `audit` — the disclosure ladder | the `detail` prop (§4.5) | never |
| **CHIP** | `NOT WATCHED` / `answered 14:22:07` / `no answer, 800 ms` | a real probe, or nothing | the *dot* is absent in OFFLINE; the *word* `NOT WATCHED` is not |
| **NEEDS YOU** | `3` — count only, links to TRACK | the §3.7 decision computation | shows `—` when not computed, **never `0`** |
| **CASEBOOK** | `13 recorded agent errors` — links to §3.9 | `generate_casebook.cjs` output count | shows `—` when not generated |

Plus, permanently, below the line and not dismissible:

- **THE TRUTH-CLASS LEGEND.** Five classes, five marks, in the operator's words at `play` and the
  formal names at `lab`+: OBSERVED · STRUCTURAL RECONSTRUCTION · REDUCED MODEL / DERIVED ·
  SIMULATED · UNKNOWN. Sourced from the material table at `ARCHITECTURE.md:267-271`. It is a legend,
  so it must be legible in the same glance as the thing it explains — that is why it is in the frame
  and not on a help page. `ARCHITECTURE.md:263` states the criterion it serves: *"A viewer must read
  epistemic status from a still screenshot with no text."* **The legend is the fallback for the case
  where the mark alone has not yet been learned; it is not a substitute for the mark.**
- **THE NOTEBOOK LINE — new copy, not a port.** The nearest existing string is *"Notebook is stored
  only in this browser."*, at `living-science-walkthrough.tsx:45` (the SSR fallback status) and
  `:203` (the `notebookStatus` initial state), buried in one panel. It states the **confinement**
  and not the **obligation**. The frame line adds the second half — *export it* — because §3A.7
  makes losing the notebook a real cost. **A previous revision quoted a sentence here and said it
  "already exists"; it exists nowhere in either tree (`grep -rn` over `app/ lib/ docs/ experiments/
  scripts/` exits 1), and a builder told to promote an existing string would have searched for it
  and not found it. Naming and exact wording are the operator's (§8).**

**MODE and LEVEL are global and they persist.** Changing either changes every room. That is the point
of a global switch: the operator sets his altitude once and the whole laboratory answers at that
altitude — *"the math at every level, approachable from kindergarten all the way up to a
150-year-old person."*

**The CASEBOOK count is in the frame deliberately.** The operator's binding requirement is that the
laboratory *"needs to continually call out and explain how risky and how dangerous the LLMs are, and
how many times you have made mistakes just in building this lab."* A number in the frame, on every
screen, costs one integer and satisfies "continually" without a nag. **It is a count of recorded,
receipted errors — never a general warning, never a disclaimer.**

## 3A.6 MOVEMENT — one action, never a typed URL

**Every room is a URL.** That single change buys the Back button, bookmarks, deep links, the browser's
own history, and shareable references in the ledger — all of which the `useState` tab strips at
`uni-flagellum-lab.tsx:737-742` and `scientific-math-workbench.tsx:285` throw away today.

- **Click** a tile on the map → that wing. Click a room in the wing → that room. **Two moves, ever.**
- **`next/link`** for every move. MAIN currently imports it **zero** times; the stale tree twice.
  `prefetch={false}` on portal links so **no request leaves without an action.**
- **Keyboard.** `Esc` or `m` → the map, from anywhere. On the map, `1`–`9` open the first nine tiles.
  Nothing else is bound, **and nothing is bound that is not also a visible control** — a keyboard
  shortcut that is the only way to reach something is a hidden room.
- **Back works**, because rooms are history entries. Today, pressing Back from the `evidence` tab
  leaves the application entirely.
- **No dead ends.** The frame's WHERE slot is a link home in every room including error and NOT BUILT
  rooms.
- **No hidden rooms.** §3A.10 criterion 6 walks `app/(lab)/**/page.lab.tsx` on disk and asserts
  set-equality with the manifest. Adding `app/(lab)/secret/page.lab.tsx` turns the suite red; so does
  a manifest entry with no route.

**Deliberately not built:** an avatar, a walk, a camera, a minimap, a fog of war, a transition
animation. `viewer/lab/l4.html:68,234,236` has a walking avatar and it is *correct there* — a spatial
exhibit on a different stack. Here it would turn a one-action move into a twenty-action move and
break G2 outright.

## 3A.7 MEMORY — what is remembered, where, and what happens when it is cleared

**The permission, verified and quoted verbatim, `docs/UNI-STACK-BUILDER-PLAN.md:695`:**

> **In browser.** `localStorage["uni.stack.workspace/1.0.0"]`, ≤ 2 MB, schema-versioned, oldest
> drafts evicted. No IndexedDB, no server, no network. A workspace that fails to parse or
> hash-verify is **refused with a message**, never silently reset. Export/import via `Blob` +
> `URL.createObjectURL`; `scripts/import-stack-export.mjs` re-canonicalises, recomputes every hash,
> and **fails on mismatch**.

**`localStorage` is not an account and not analytics.** It is a key on the operator's own machine that
leaves no trace anywhere else, sends nothing, and identifies nobody. `CLAUDE.md:69-72` is untouched.

**The discipline already exists in shipping code and must be copied, not reinvented.**
`living-science-walkthrough.tsx:36` declares `STORAGE_KEY`; `:44-55` reads it, validates it with
`validateLessonExport`, and on failure returns *"Saved notebook could not be restored; no data left
this browser."* — a **message, not a reset**, exactly as `:695` demands. Writes at `:224` and `:253`;
an export→re-import self-test at `:250-262`.

| key | holds | size | cleared by |
|---|---|---|---|
| `uni.flagellum.observer-notebook.v1` — **EXISTS** | the operator's own observations and drafts | as today | **never automatically, and never by the shell** |
| `uni.flagellum.shell.place/1.0.0` — **NEW** | where you were | ≤ 64 KB | a visible FORGET WHERE I WAS control in the frame |

```jsonc
{ "schema": "uni.flagellum.shell.place/1.0.0",
  "room": "/lab/wing/flag/math",
  "mode": "OFFLINE", "level": "lab",
  "recent": ["/lab/wing/flag/math", "/lab/chalkboard", "/lab/wing/parity"],
  "open": { "equation": "VFE" },
  "seen_snapshot": "<sha256 of wing-state.snapshot.json as of your last visit>",
  "written_at": "2026-07-29T09:14:02.113Z" }
```

> **The rule that keeps storage out of the evidence path.**
> **`localStorage` may hold navigation and the operator's own drafts. It may never hold a verdict, a
> probe result, a bench number, a hash of evidence, or anything with a truth class.**

**A cached `PASS` restored from a browser is a claim about the world with no capture time and no
provenance, presented as if it were read. That is truth laundering through a storage key.**
§3A.10 criterion 8 asserts the stored payload contains none of the verdict vocabulary and no
`sha256:` of evidence — `seen_snapshot` is the hash of the *snapshot file*, a fingerprint for change
detection, not a value anyone reads.

**What happens when storage is cleared.** You land on **the map**, in **OFFLINE**, at level **`lab`**.
Nothing that was evidence is lost, because no evidence was there. **The notebook is the one real loss,
and it is the operator's to prevent** — hence the permanent frame line and the existing
`exportJson`/`exportCsv` at `:247-248` (`:249` opens `validateRoundTrip`). FORGET WHERE I WAS touches the place key only, and says so on
the control. **`seen_snapshot` being absent is not "nothing changed"**: with no memory the frame says
*"first visit in this browser — nothing to compare against"*, never *"no change since your last
visit"*, because it does not know. **This is F26's discipline applied to change detection: absence of
a memory is not evidence of stability, exactly as absence of a probe is not evidence of health.** A
corrupt payload is **refused with a message and left in place**, never deleted; the operator can
export it. §3A.10 criterion 7 mutates this and it must bite.

## 3A.8 CONTINUOUS FEEDBACK — and the binding rule that forbids most of it

**The rule, verbatim, `docs/control-plane/ARCHITECTURE.md:274`:**

> No frame rate, glow, motion or particle may imply liveness. Liveness renders **only** from a real
> probe result. A frozen colony looks frozen while every process reports up.

And its second half at `:275`: *"Passing a gate renders the named behaviour and nothing more. **No
material, light or room in this lab can depict awareness, experience or life.**"*

**The same law, restated as F26**, `evidence/remediation/phase9_plan.json:567`: *"liveness is drawn
ONLY where a probe answered; not_probed draws NOTHING, and that silence is the point, because absence
of a probe is not evidence of health."*

**It is enforced in running code, three places, measured:** `viewer/lab/projection.cjs:113-115` sets
`node.liveness = "not_probed"` with the comment *"a projection of a ledger is not a probe of a
service, and drawing a liveness dot would say it was"*; `viewer/lab/rooms.cjs:274-276` — *"anything
not probed says `not_probed` — never `down`, because 'I did not look' and 'I looked and it was dark'
are different facts"*; and `lib/sp/control_plane/scene.ex:419-444`, whose `liveness/1` returns
`:not_probed` for `%{live: nil}` **and which records a hazard worth carrying: quoting §8.2's
prohibition verbatim in source trips a source-scan guard**, so `scene.ex:427-430` paraphrases it
deliberately. **Any test or comment added to `app/**` that quotes those words may hit the same
guard.**

### The violation is in the shipping product, and it is measured

`app/biological-stage.tsx:259` — `const phase = reducedMotion || !running ? 0.8 : (now - start) / 1000;`
— and `:265`, `if (!reducedMotion && running) frame = requestAnimationFrame(render);`.

**The biology animates if and only if a UI boolean is true.** Meanwhile
`app/uni-flagellum-lab.tsx:624-626` renders the header banner `EXPERT ENGINE · LIVE INSTRUMENT` from
`sourceMode === "serial"` — and `sourceMode` is set at `:549` on a successful
`port.open({ baudRate: 115200 })`, and cleared **only** by a thrown error (`:576`), a `done` on the
reader (`:557`), or the operator pressing Disconnect (`:578-591`). **An instrument that opens and then
stops sending frames leaves the banner reading LIVE INSTRUMENT and the flagellum turning.** That is a
frozen colony looking alive while a process reports up — **the exact sentence the contract forbids,
in the product, today.**

**The one honest instrument on the page already exists**: `receivedAge` at `:598`
(`clockMs - system.observation.receivedAtMs`), rendered at `:707` as `Observation age {receivedAge}
ms`. **It is a small span inside one panel while the false claim is a header banner.**

**The repair is small and behavioural.** The frame's CHIP slot renders from `receivedAge` against a
declared staleness budget, and the banner is demoted to the same source. **Motion is decoupled from
every liveness claim.** §3A.10 criterion 5.

### What MAY move

1. **The synthetic world's own state.** The loop at `:486-524` really is computing at 80 ms
   intervals, and its motion depicts *the model advancing*, not a chip being alive. It carries the
   `SIMULATED` truth chip at every level, per §4.5's always-present rule.
2. **A value that changed, changing.** `globals.css:144` — `.probability-track i { transition: width
   120ms linear; }`. **The bar moves because the number moved.**
3. **Anything the operator drives.** `globals.css:49` button hover. A slider. A page turn.
4. **All of it still yields to `prefers-reduced-motion`**, already honoured at
   `biological-stage.tsx:245,259,265` and `globals.css:389,531`.

**Measured, and worth saying out loud: MAIN's stylesheet already obeys this rule and nobody had
written it down.** `grep -c "@keyframes" app/globals.css` → **0**. `grep -n "transition:"` → exactly
two, both above. **No pulse, no glow, no breathing dot anywhere in the shipping stylesheet.** This
section is codifying an existing property, not imposing a new cost.

### What MAY NOT move

1. **Nothing may pulse, glow, breathe, tick or animate to mean up, connected, healthy, working, or
   alive.** No exceptions, no "just a subtle one".
2. **No spinner that spins while nothing is awaited.**
3. **No refresh cadence, frame rate, or counting-up "3s ago" may stand in for a probe.** A relative
   time that ticks is motion asserting freshness.
4. **No tile on the map may animate** — on load, on change, or on hover-in-a-way-that-means-state.
   Live state on the map is a mark and a timestamp.
5. **Nothing may depict awareness, experience or life** (`ARCHITECTURE.md:275`, F27).
6. **The map is diff-suppressed.** `projection.cjs:147-149`: *"A surface that re-sends an unchanged
   world once a second teaches its reader that motion means nothing, and then real motion goes
   unnoticed."* Rendered twice against an unchanged snapshot, **the map's DOM must be byte-identical.**
   §3A.10 criterion 4 is exactly that assertion, and it is the criterion that kills ticking clocks,
   pulsing tiles and relative times in one stroke.

### So how does a gate going red become visible from across the room?

**By text, colour and position — the three things a still screenshot carries.**

- The frame gains one **ALARM** slot, empty unless a wing's verdict set contains a `FAIL`. When
  non-empty it reads, at rest: `W-PARITY · 3 FAIL · as recorded 2026-07-17T20:30:00Z`. **It does not
  move, blink or animate.** It is red, it is at the top of every screen, and it is longer than
  everything beside it. **A still photograph of any room carries it.**
- **In OFFLINE it is always stamped with the capture time**, because OFFLINE has no fresh reading and
  a FAIL from twelve days ago must not read as a FAIL from now.
- **When the snapshot hash differs from `seen_snapshot`,** the frame adds one line: *"changed since
  you were last here: W-PARITY, W-FLAG."* **That is the world reacting, computed from a hash
  comparison, with no motion and no probe.**
- **It is never suppressed for being old, never collapsed into a count on a second screen, and never
  appended below the fold.** An adverse result carried honestly is the product working.

## 3A.9 PROGRESSION — real, not gamified

**Forbidden outright:** a percentage complete, a score, XP, a level number, a streak, a badge, a
progress bar over the whole laboratory, a green checkmark that survives a `FAIL` elsewhere, and **any
single number that averages a failing gate against passing ones.**

**The reason is scientific, not aesthetic.** `summary.overall` in both committed reports is
`"PARTIAL_PARITY_ONLY"` and `fullBiologicalParityAchieved: false`. Twelve PASS of thirty gates —
4 of 14 in `science-gates-report.json` plus 8 of 16 in `cross-study-parity-report.json` — would
"average" to a cheerful **40%**. **The correct rendering of `4 PASS · 3 FAIL · 5 BLOCKED_EXTERNAL ·
1 SOURCE_ONLY · 1 NOT_ESTABLISHED` is those five numbers, side by side, none of them merged.**

*(This paragraph said **60%** one revision ago. Twelve of thirty is 40. The argument for never
rendering a single percentage got its own percentage wrong, which is the strongest possible
illustration of it and the weakest possible way to have made it. Corrected, and left visible.)*

**What progression IS, on the map:**

1. **Per wing: the five counts, unmerged, with the capture time.**
2. **BUILT / NOT BUILT**, from the manifest — the honest shape of the laboratory as it is.
3. **BLOCKED is its own state and never counts as done or as failed.** `BLOCKED_EXTERNAL` appears 5
   times in the science report and 3 in the cross-study report. The tile says *blocked, and on what*.
4. **The first unsatisfied layer, named.** `viewer/resonance.cjs` (437) + `resonance_meter.cjs` (257)
   compute seven conjunctive layers and **name the first unsatisfied layer rather than averaging** —
   exactly the property a progression display needs and exactly the property a percentage destroys.
   They have no UI. Surfacing the layer *name* is nearly free. **Caveat, stated on the tile:** those
   scripts live in `UNI.Minecraft`, so the value reaches the map only through
   `scripts/freeze-wing-state.mjs` with the sibling present. **Absent, the tile says `NOT_MEASURED`,
   not a stale number.**

**Progression is a description of the evidence, not a reward. If the laboratory ever looks like it is
congratulating the operator, it has started lying to him.**

## 3A.10 Acceptance criteria for section 3A

### The operator's criterion — performable by him, no terminal, one pass

> Open the laboratory at `/lab`. Without typing a second address and without opening a terminal,
> reach every body of mathematics in **at most two clicks** from that first screen. In each room,
> without scrolling, read three things: **which MODE you are in, which LEVEL you are at, and whether
> the chip is being watched.** Then press one key and come back to the first screen — and press the
> browser's Back button and confirm it takes you back too.
>
> **It fails if:** any body of mathematics needs a typed address; any takes three moves; any room
> hides the mode, the level or the chip line; the Back button leaves the laboratory; a tile claims a
> wing is proven without showing when that was recorded; or anything on any screen pulses, glows or
> blinks.

### Behavioural criteria — each one runs, and its result changes when the thing changes

1. **Every manifest entry has a room, and the tile count is COMPUTED.** A test enumerates `WINGS`,
   `STANDING` and their `rooms[]`, renders each route through the same worker harness
   `tests/rendered-html.test.mjs:4-13` already uses, and asserts HTTP 200 plus the frame markers.
   **It then asserts the map renders exactly `WINGS.length + STANDING.length + PORTALS.length`
   tiles — the number is read from the manifest, never transcribed into the test**, so adding a room
   cannot fail this criterion. **Adding a wing to `lib/shell/wings.js` without creating its route
   turns the suite red.**
2. **Depth is two below `/lab`.** The same test asserts it. Adding a fourth path segment exits 1.
3. **The frame is on every lab route.** Render every manifest route and assert the server-rendered
   HTML contains the WHERE, MODE, LEVEL, CHIP, NEEDS YOU and CASEBOOK slots. **Deleting `<LabFrame>`
   from `app/(lab)/layout.lab.tsx` turns every one of them red at once** — which is why it lives in
   the lab layout.
4. **The map does not move.** Render the map twice, two seconds apart, against an unchanged snapshot;
   assert the two HTML strings are **byte-identical**. A ticking clock, a relative "3s ago", a pulsing
   tile or a random id all break byte-identity. **Mutation: add a `Date.now()`-derived string to any
   tile → exits 1.**
5. **`not_probed` draws nothing.** Render the map with the snapshot's `chip.probed_at` set to `null`
   and assert **no liveness element exists in the DOM at all** — not `hidden`, not `aria-disabled`,
   absent. **Mutation: emit a grey dot for `not_probed` → exits 1.** **This is the mutation that
   proves F26 bites in this codebase.**
6. **No hidden rooms.** Walk `app/(lab)/**/page.lab.tsx` on disk, map each to a route, assert
   set-equality with the manifest. Adding `app/(lab)/secret/page.lab.tsx` exits 1; so does a manifest
   entry with no file.
7. **A corrupt place-key is refused, not reset.** Write a valid payload, mount, assert you land in the
   recorded room/mode/level. Corrupt one byte, mount again, assert you land on the map **with a
   message** and that the corrupt value is **still present in storage**. **Mutation: make the loader
   `catch { removeItem() }` → exits 1**, because `UNI-STACK-BUILDER-PLAN.md:695` says refused with a
   message, never silently reset.
8. **Storage holds no evidence.** Visit every room, then assert the stored payload contains none of
   `PASS|FAIL|BLOCKED_EXTERNAL|NOT_ESTABLISHED|SOURCE_ONLY` and no evidence `sha256`. **Mutation:
   cache one verdict → exits 1.**
9. **The FAIL count on the front door is read, not typed.** Render the map and assert the FAIL count
   equals the count computed from the two committed reports — **today, 6** (3 + 3). Point
   `freeze-wing-state.mjs` at a **copy** with one `FAIL` edited to `PASS`, rebuild the snapshot,
   re-render: **the map must read 5.** **A number that does not move is a number somebody typed.**
10. **The snapshot never carries a number forward.** Run `freeze-wing-state.mjs` with no sibling
    checkout and assert every chip-side wing is `NOT_MEASURED` with a reason, and that no value from
    the previous snapshot survives. **Mutation: carry one count forward → exits 1.**

### What this section does NOT break, and why that is the §0 dividend

`tests/rendered-html.test.mjs` is 33 lines. Its `render()` at `:4-13` hardcodes
`new Request("http://localhost/")` at `:9`; the single test at `:15-33` asserts status 200 (`:17`),
the content type (`:18`), **twelve `assert.match` against the HTML at `:20-31`** — including
`/World process/i`, `/Markov boundary/i`, `/Connect real instrument/`, `/Physical UNI model/`,
`/Begin guided laboratory/`, `/OBSERVED REPLAY/` and `/mears-2014-run-tumble\.mp4/` — and one
`assert.doesNotMatch` at `:32`.

**Under §0.2 the bench stays at `/`, so all twelve assertions stay exactly where they are, untouched
and unweakened.** The file gains one thing: `render(path = "/")` takes a path argument, and a second
test asserts **`/lab` server-renders the map** — **every tile name in the manifest, iterated from the
manifest**, the six frame slots, the FAIL count and the capture timestamps. The existing
`assert.doesNotMatch` at `:32` applies to both. **The draft said "the fourteen tile names"; a
transcribed count in a criterion is a correct run's way of failing its own gate, and two rooms have
been added since it was written.**

**Nothing in `tests/rendered-html.test.mjs` is weakened or deleted.** An earlier draft of this section
moved the bench off `/` and turned that test red on purpose; §0 makes that unnecessary, which is the
cheapest possible outcome. **A plan that turned that test green by loosening a regex would be doing
the one thing this repository exists to forbid.**

---

# 4. THE CHALKBOARD

## In plain words

**Every equation in every surface of every tree is a string, and there are exactly sixty of them.**
Seventeen hard-coded in MAIN's `app/*.tsx`, eleven in the stale workbench's `modelCatalog`, and
thirty-two LaTeX display blocks in eight proof documents that nothing renders. Not one is connected
to the function that computes it, carries a unit the machine knows, or has a single step of
derivation behind it.

**CORRECTED — and the correction makes the argument stronger, not weaker.** The word `derivation`
occurs **243 times across 140 files in the three trees** (MAIN 111 / STALE 44 / CHIP-SIDE 88;
`--no-ignore-vcs` gives 251 / 146; code files only, exactly 50 — which is where an earlier "50"
came from, under an unstated filter). **And not one of them renders a derivation.**
`rg -c -i derivation` over `UNI-FLAGELLUM/app/` and `UNI-FLAGELLUM-math-workbench/app/` **exits 1 —
no match, in either Next.js tree.** In `UNI.Minecraft/viewer/` all twelve occurrences are the word
used to *forbid* something: Gaia's law that a projection is "not derivation" (`collectors.cjs:9`,
`gaia.cjs:7,49,238`, `gaia_lint.cjs:6`, `sig.cjs:11`), an AES key-derivation input
(`command_center.cjs:1734`), an IP-literal `re_derivation` field (`ip_fence.cjs:85-86`), a go-live
gate label (`infra.cjs:244`), and `desk.cjs:466`, which derives a verdict from an exit code (its
value spans `:467-468`). **The nearest thing to a rendered equation in the whole fleet is
`<pre>{selectedModel.equation}</pre>` at `app/math-workbench/scientific-math-workbench.tsx:340` —
one frozen string, no steps, no justification, no units check.**

This section turns those strings into a chalkboard you can work at.

## 4.1 The inventory

**MAIN — 17 display strings, all opaque text nodes**

| # | Where | Equation | Rendered at |
|---|---|---|---|
| 1-8 | `app/uni-flagellum-lab.tsx:73,80,87,94,101,108,115,122` | the `partDetails` record: ion free energy to torque work; the observation `o_t = sensor(world_t) + eps_t`; the prior log-odds; the evidence log-odds; the log-odds identity; `Q(pi) = softmax(-gamma G)`; the predicted-outcome marginal; `a_t in {RUN, TUMBLE}` | `:727` |
| 9 | `:784` | `q(s_t) = eta . p(o_t|s_t) . sum B_pi(s_t|s_t-1) q(s_t-1)` | inline |
| 10 | `:789` | `F[q] = sum q(s)[ln q(s) - ln p(o,s)] = KL[q||p(s|o)] - ln p(o)` | inline |
| 11 | `:794` | `Q(pi) = softmax(-gamma G); G = risk + ambiguity - information gain + effort` | inline |
| 12-16 | `app/cross-study-parity-panel.tsx:48-52` | DLT / ROTATION / LATTICE13 / GMC / RFT | `:103` |
| 17 | `app/observed-experiment-panel.tsx:101` | the `q(slow|T>t)` mixture posterior | inline |

Plus **13 `deeperMath` narration strings** in `lib/walkthrough.js` — one per step, prose with
equations embedded (`:123` *"mean speed is v=d/dt"*; `:141` *"F_body + sum F_flagella = 0"*).

**STALE — 11 catalog entries**, `app/math-workbench/scientific-math-workbench.tsx:80-191`:
WORLD, BOUNDARY, BAYES, VFE, EFE, DURATION, DLT, ROTATION, LATTICE, GMC, RFT. Each already carries
`id`, `name`, `truth`, `equation`, `input`, `output`, `source`, `plain` — **five of the fields a
disclosure ladder needs are already authored.** Rendered as a `<pre>` at `:340`.

**CHIP-SIDE — 32 LaTeX display blocks** across the 8 proof documents in `UNI.Minecraft/lab/proofs/`
(active_inference 4, bioenergetics 2, dgst 2, dimensional_analysis 7, limitations 4, ozone 5,
uv_filtering 5, water_escape 3), plus equations inside `@doc` strings in `lib/sp/lab/*.ex`
(e.g. `physics.ex:33`, `g = G.M/R^2`).

**And 21 LaTeX strings already written and already unrendered**, in
`UNI.Minecraft/lab/evidence/formula_ledger.json` — each with `latex`, `variables`,
`evidence_class`, `source`, `url`, `implemented_in`, `limitations`. **This is the single
highest-leverage unused asset in the three trees.**

**The binding today is prose.** `scientific-math-workbench.tsx:118` says
`source: "lib/uni-motor.js . bayesUpdateWithLikelihood"`. That function is real — and it is **not
exported**; `grep "^export function" lib/uni-motor.js` lists 17 and it is not among them. Same for
`policyTerms` and `transitionPrior`. **The string points at code no test can reach.**

## 4.2 `lib/math/` — the symbolic spine that does not exist anywhere

**Zero symbolic representation exists in any tree**: no KaTeX, no MathJax, no LaTeX renderer, no
expression AST, no unit type, no evaluator. `ls lib/math` and `ls lib/stack` in MAIN both fail.

New directory in MAIN: zero dependencies, pure, `node --test`-able. **It reuses the grammar, closed
function set and unit algebra the plan of record already froze and already had judged**
(`docs/UNI-STACK-BUILDER-PLAN.md:520-563`) rather than inventing a second vocabulary.

**`lib/math/units.js`** — unit multiset algebra. `mul`, `div`, `requireSame(a,b,ctx)`,
`requireDimensionless(u,fn)`, and the constants `NAT = {nat:1}` and `JOULE = {J:1}`.
**There is no conversion between nat and joule and this file exports none.**
`requireSame(NAT, JOULE)` throws with the plan's **already-authored** message (`plan:558`):
*"F is in nats; tau.dtheta is in joules; they cannot be added."* This turns the prose fence at
`app/uni-flagellum-lab.tsx:805-809` into a type.
**Acceptance:** nat plus J throws `UNIT_MISMATCH`; the module exports no function matching
`/convert|toJoules|toNats/`; a source scan asserts no `eval`, no `new Function`, no dynamic import.

**`lib/math/expr.js`** — the Term AST and a total, budgeted evaluator. Terms are **data, never a
parsed user string in v1**: `{k:"num"|"sym"|"op"|"fn", ...}`. The `fn` set is **verbatim** the
closed FUNC list at `plan:534-535`: `ln exp sqrt abs min max clamp sigmoid softplus tanh sum dot
entropy kl normalize softmax`. `evaluate(term, env, budget = 4096)` throws `UNBOUND_SYMBOL{name}`
rather than returning NaN, and `BUDGET_EXCEEDED` when the step counter trips.

**`lib/math/registry.js`** — `EQUATION_REGISTRY`, the single index. Each entry carries
`id`, `sockets[]`, `playTitle`, `labTitle`, `auditTitle`, `lhs{sym,of,unit}`, `rhs: Term`,
`unicode` (the EXISTING display string, retained verbatim), `latex`, `truthClass`, `species`,
`status` (`BUILT | NOT_BUILT | BLOCKED_EXTERNAL | DISPUTED`), `binding{module,fn,field}`,
`derivationId`, `proofPin{path,line,sha256}`, `falsifier`, `worksheetIds[]`.
**Falsifiers are lifted verbatim from the proof documents. Never paraphrase a falsifier.**

**`lib/math/render.js`** — three pure renderers, no DOM: `toUnicode(term)` (the display string,
*regenerated* rather than stored), `toChildWords(term)`, `toSteps(term)`.

### The test that makes this real — and it lands RED, by design

**`tests/math-registry.test.mjs`**: for every entry with a non-null `binding`, run the live system,
evaluate `rhs` from the same env, and assert agreement to `1e-12`.

**This test FAILS on EFE the day it lands, and that failure is the deliverable.**
`lib/uni-motor.js:318-321` computes `risk` as a cross-entropy; `:326` computes
`informationGain = entropy(qOutcome) - ambiguity`; `:328` is
`efe = risk + ambiguity - informationGain + effort`, which expands to
`KL[q(o)||C] + 2*ambiguity + effort` — **not** the displayed
`risk + ambiguity - informationGain + effort`. Today **nothing in the repository can detect that the
picture and the machine disagree.** This test is the first thing that can.

**Do not soften it. Land it red, carry `status: "DISPUTED"` with the audit id, and annotate
worksheet 5 rather than deleting it.** (The correction itself is workstream W1, earlier and
separately reviewed, because the equation is *live on the chip*.)

### v1 scope — six equations, not sixty

| id | binding | prerequisite |
|---|---|---|
| `BAYES` | `bayesUpdate` (already exported, `uni-motor.js:282`) | none |
| `LOGODDS` | already live at `uni-flagellum-lab.tsx:777` | none |
| `VFE` | `bayesUpdateWithLikelihood` | **export it** (additive) |
| `EFE` | `policyTerms` | **export it** — lands DISPUTED |
| `DLT_SURVIVAL` | `sourceSurvival` (`source-first-passage.js:43`, exported) | none |
| `DURATION_M0_M3` | `scoreDurationOnSeconds` | **BLOCKED — see 4.3** |

## 4.3 The blocker nobody wrote down

**`lib/duration-models.js` does not exist in MAIN.** It exists only in the stale worktree
(114 lines, 9 exports, plus a 16-line `.d.ts`). `scoreDurationOnSeconds` — the seconds-scale scorer
with the Jacobian term `jacobianLog = -ln(mu_N)` at `duration-models.js:96` — **does not exist in
MAIN at all.** MAIN's equivalents are **private**: `lib/observed-experiment.js:160`
`function logDensity` and `:176` `function survival`, neither exported.

**Six of the eleven workbench equations depend on it. Any plan that says "port the workbench to
MAIN" is blocked on this, and every earlier plan is silent about it.**
It is present on the chip (`/opt/uni/flagellum/prod/src/lib/duration-models.js`, 4346 B), which is
one more way of saying the chip is running a different program from MAIN.

Two additive options:
- **(a)** port `lib/duration-models.js` and `.d.ts` from STALE and refactor MAIN's
  `observed-experiment.js` (500 to ~420 lines) to import from it, matching STALE exactly. Larger
  diff; the two trees converge.
- **(b)** add `export` to `logDensity` and `survival` in MAIN and write a ~20-line
  `scoreDurationOnSeconds` wrapper. Smaller diff; the trees stay divergent.

**Recommendation: (a).** The STALE split is the already-reviewed shape, and convergence removes a
standing source of drift. **Whichever is chosen, MAIN then holds two copies of the same
mathematics, so the duplication itself must be gated:** a new `tests/duration-models.test.mjs`
asserting `scoreDurationOnSeconds(t, mu_N, models).logDensitySeconds` equals
`logDensity(name, t/mu_N, models) - ln(mu_N)` for all four models over a grid, and agreement with
`observed-experiment.js`'s internals to `1e-12`.

## 4.4 THE TWELVE WORKSHEETS — characterised exactly, then extended

**This is the ONE requirement in the operator's brief that already ships** — and it ships on the
wrong branch, is deployed on the chip, and **the worksheet VIEW is covered by one assertion about a
button label.**

`app/math-workbench/scientific-math-workbench.tsx:387-403`, guarded by `view === "worksheets"`.
Lines **`:390-401`** are twelve `[title, prompt]` tuples, one per line, inside an array literal that
opens `{[` at `:389` and closes `].map(...)` at `:402`: *1 Boundary inventory .
2 One Bayesian update . 3 Log-odds identity . 4 Variational free energy . 5 Expected free energy .
6 Normalize and score a dwell . 7 Survival posterior . 8 DLT competing risks . 9 Periodic lattice .
10 Evidence and claim . 11 B3 prediction audit . 12 Parity ladder.* Line `:402` maps each to an
`<article className="workbook-page">` with an eyebrow, an `<h3>`, a `<p>`, exactly **12 ruled
`<div className="workbook-line"/>`**, and a footer.

**The prompts are genuinely good.** They demand hand calculation with blanks, self-checks
(*"Check sum posterior = 1"*), and — worksheet 5 — **predict before revealing**:
*"Predict the selected action before checking the tool."*

**Printing:** `printWorkbook()` at `:251-254` switches the view then calls `window.print()` on the
next tick; invoked at `:274` and `:388`. CSS is 4 screen rules (`app/globals.css:680-683`;
`.workbook-page` min-height 9in, .45in padding, `break-after: page`; `.workbook-line` .45in with a
bottom border) and **5 print rules inside the second of the file's TWO `@media print` blocks**.
**Corrected, measured:** STALE's `app/globals.css` is 702 lines and has **two** `@media print`
blocks — the walkthrough block at `:534-544` (9 selector rules) and the workbook block at
`:696-702` (5: `.math-workbench-shell`, the hide list, `.workbook-pages`, `.workbook-page`,
`.workbook-line`). **Fourteen print rules in two blocks, and zero `@page` rules anywhere.** MAIN's
`globals.css` is 544 lines with **one** print block, at `:534`, and **no workbook rules at all** —
**which is the real gap: porting the worksheets to MAIN means porting `:696-702` too, or twelve
worksheets print as screen chrome.**

### Four measured defects

1. **No `@page` rule in either tree.** Page size and margin are browser defaults; the only margin
   is the .45in padding *inside* the page, which the print rule at `:700` does not remove.
2. **`Source commit ____` is a blank line.** A printed sheet carries **no machine-written
   provenance** — it cannot be re-derived, which breaks the reproduction-command clause on paper.
   Meanwhile **STALE** `app/math-workbench/page.tsx` (77 lines) **imports six provenance-bearing JSON reports
   at `:2-7`** — the observed report, the science-gates report, the cross-study parity report, the B3
   protocol, the B3 prediction and the D1 correction package — and passes none of it to the worksheet
   view. *(`:26-74` is a different thing: the single `observed={{…}}` prop object handed to
   `<ScientificMathWorkbench>`. Citing the prop block as the load point points a builder at the wrong
   48 lines.)*
3. **Ctrl+P from any other tab prints nothing** (`PHASE-E-WORKBENCH-AUDIT.md:420`, PRD-03), because
   `.workbook-pages` is only in the DOM when the view is selected.
4. **CORRECTED: the workbench MATHEMATICS is tested; the worksheet VIEW is not.** The earlier
   "zero test coverage" claim (`PHASE-E-WORKBENCH-AUDIT.md:232-241`, E-M05) is **false as stated**.
   `UNI-FLAGELLUM-math-workbench/tests/math-workbench.test.mjs` exists — 91 lines, 4,412 B,
   **5 `test(` blocks**, and it is **second in STALE's `npm test`**. It imports and executes the real
   `lib/duration-models.js` and `lib/source-first-passage.js`: the canonical seconds-scale scorer,
   the survival posterior, the DLT first-passage values and the closed-loop step model, and its
   fifth test asserts the workbench *binds* those calculators rather than defining shadow functions.
   **The claim narrows to the worksheet VIEW, where it holds and is worse than it sounds:** the only
   assertion touching the workbook anywhere in the tree is
   `assert.match(html, /Print complete workbook/)` at `tests/rendered-html.test.mjs:38` — **a button
   label.** `rg -n -i 'Boundary inventory|Parity ladder|workbook-page|length: 12|Paper workbook'
   tests/` **exits 1.** Nothing asserts that twelve worksheets exist, that any of them has a title,
   or that a single one renders. **Deleting all twelve tuples at `:390-401` leaves the suite green.**
   And **worksheet 5 asks for a value the tool does not produce** (E-M01).

### The build — extend, do not reinvent

**NEW `lib/worksheets/registry.js`** — the twelve tuples promoted to data, **prompts verbatim**,
each gaining `id`, `n`, `wing`, `equationIds[]` (resolving in `EQUATION_REGISTRY`), `lines: 12`
(the hard-coded 12 becomes data), `detail`, `truthClass`, `species`, `answerKey(env)` (**the same
binding as the screen**), and `falsifier`.

**NEW `app/(lab)/lab/chalkboard/worksheet.tsx`** — the `:402` mapper extracted as
`<Worksheet sheet={spec} provenance={p} detail={d}/>`. **Class names unchanged**
(`workbook-page`, `workbook-line`, `eyebrow`, `<footer>`) so `globals.css:680-683` and `:696-702`
need **zero edits**. That is the whole point of extending rather than rewriting.

**Edits, each minimal:** add `@page { size: letter; margin: 0.5in }` and, in the print block,
`.workbook-page { padding: 0 }`; stop hiding a rendered-but-screen-hidden `.workbook-pages` so
Ctrl+P works from every tab (closes PRD-03); pass `provenance={{commit, reportSha256, generatedAt}}`
from `app/(lab)/lab/chalkboard/page.lab.tsx` (the six JSON imports move with it from STALE's
`app/math-workbench/page.tsx:2-7`) so the footer's third field is machine-written; append the audit's disputed note to
worksheet 5 without deleting the prompt.

**NEW `tests/worksheets.test.mjs`** — closes E-M05: assert the **count first**
(`WORKSHEETS.filter(w => w.wing === "flagellum").length === 12`) so the gate cannot pass vacuously;
every `equationIds` entry resolves; every sheet renders a truth chip and a species label or an
explicit *not applicable*; server-render the worksheets view and assert **12 `workbook-page`
articles and 144 `workbook-line` divs**; the footer contains a **40-hex commit, not underscores**;
and a mutation — deleting one tuple must fail the count assertion.

**New wings, generated not hand-written.** `wing: "proofs"` sheets are emitted mechanically from
the eight proof documents (4.6): the Equations section as the header, the variables table as a
fill-in grid, the Worked Example with its numbers blanked, the Dimensional Check as a units-balance
exercise, and the Falsification Condition printed **verbatim** at the foot. Eight proofs, eight
sheets.

## 4.5 THE DISCLOSURE LADDER — one `detail` prop, identical DOM

The plan's claim, verified and quoted verbatim, `docs/UNI-STACK-BUILDER-PLAN.md:49`:

> **One product, three disclosure levels.** A single `detail: "play" | "lab" | "audit"` prop,
> identical DOM. **Correction to the lego-first design, per the truth-safety judge:** truth class,
> species label, NOT-BUILT status and unit suffix render at *every* level, in child words if
> necessary. Only symbols, hashes and the gate ledger are progressive.

And `:623`: *always present regardless of detail — truth chips, species labels, `NOT BUILT`
captions, unit suffixes on every scalar, em dashes for inert values, the `ABSENT` seam caption.
Progressive — Greek symbols and formal names (`lab`+); the equation pane (`lab`+); hashes,
`sourcePin` sha256, the gate ledger, prospectivity banner and UNIEXPR bricks (`audit` only).*
`:625`: *"A screenshot taken in any mode carries the truth class of every number on it."*
`:597`: inert values are an em dash, **never `0`**, at every level.
`:588`: play-mode truth chips read *"something we made up" / "something we measured" / "not built"*.

### Does `play | lab | audit` answer kindergarten-to-150? No. It answers half of it.

**The three-value prop was inherited whole from an older document and never checked against the
requirement it is supposed to satisfy.** The requirement is written down —
`docs/THE-LABORATORY-PLAN.md:22`, R3: *"Covers the math at every level — approachable from
kindergarten to a 150-year-old."* **That same file at `:213` already recorded this exact gap**
(*"`kindergarten` 0, `curriculum` 0, `lesson` 0, `classroom` 0, `educat*` 0, `150-year` 0"*), and the
draft dropped the finding: measured over it, `kindergarten` appeared **zero** times and neither
occurrence of `150` was about a person.

**Here is the map, stated plainly so nobody has to infer it again.**

`play` is for a person who cannot yet read a symbol — a five-year-old, **and equally** the visitor,
the funder, the journalist, the operator at hour three of a broadcast. It gives **quantities as
physical things**: counters, bar heights, boxes that grow and shrink, words of one or two syllables.
It gives **the whole truth apparatus anyway** — truth chip, species label, `NOT BUILT` status, unit
suffix, em dash for inert — in child words, because `plan:49` is not negotiable and **a child lied to
by omission is still lied to.**

`lab` is for a person who reads symbols and wants the quantity — the working scientist, the engineer,
the operator doing the work. Greek, formal names, the equation pane, the number with its unit.

`audit` is for a person who does not believe you — the reviewer, the adversary, the future agent, and
the operator when he is checking whether an agent lied. Hashes, `sourcePin` sha256, the gate row,
prospectivity, the binding to the exact function and line, the falsifier verbatim.

**And what does the 150-year-old get that the professor does not?** Nothing epistemic. He *is* the
professor — he sits at `audit` and has forgotten more than the professor knows. **What he needs is
not a fourth level, it is a second axis**, and neither this draft nor `UNI-STACK-BUILDER-PLAN.md` has
ever named it: **`density: "comfortable" | "compact"`**. Comfortable is 22 px minimum type, one
concept per printed page, 1.6 line height, contrast at WCAG AAA, no hover-only affordance, no timed
reveal, every control reachable by keyboard. Compact is what ships today. *(Those specific values are
chosen, not measured.)*

**`detail` and `density` are orthogonal** — a five-year-old wants `play`+`comfortable`, a reviewer on
a laptop wants `audit`+`compact`, and the 150-year-old wants `audit`+`comfortable`, **which the
current design cannot express at all.**

> **So: three levels answer the epistemic span and do not answer the sensory span. The honest
> statement is that the ladder is `detail × density` — six cells, one of which (`play`+`compact`) is
> REFUSED rather than rendered, because a child on a dense page is a child who stops.** This is a
> design correction, not a new requirement: it is what R3 already asked for.

**The claim is accurate and entirely unimplemented.** No `.tsx` in either tree declares a `detail`
prop; the closest shipping analogue is the two-state `deeper` boolean at
`app/guided-teacher.tsx:20,:80,:92`.

**Tension resolved, not papered over:** `:623` says the equation pane is `lab`+; `:49` says truth
class and units render at *every* level. **Resolution: at `play` the equation PANE — symbols, the
formal statement — is hidden; the equation's truth chip, unit chip and NOT_BUILT status are not,
because they attach to the VALUE, which is always shown.**

**NEW `app/(lab)/lab/chalkboard/equation-card.tsx`** — one component, one `detail` prop, identical DOM.
Every element exists at all three levels; only text content changes and three elements gain
`hidden`:

```
<article class="equation-card" data-detail={detail} data-equation="VFE">
  <header>  .eq-title   .truth-chip   .species-chip   .status-chip  </header>   ALWAYS
  <div class="eq-statement"  hidden={detail==="play"}>   ...   </div>
  <p   class="eq-plain">   one sentence   </p>                                  ALWAYS
  <div class="eq-value">   .eq-number (value or em dash)   .unit-chip   </div>  ALWAYS
  <div class="eq-bar" style="--h: ...">                                         ALWAYS
  <a   class="eq-derivation" hidden={detail==="play"}>   ...   </a>
  <div class="eq-pins"       hidden={detail!=="audit"}>  ...   </div>
</article>
```

**VFE at `play`** — *"How surprised was I?"* / `[something we made up] [no living thing] [built and
running]` / *"I had a guess about the world. Then I looked. This says how far off my guess was."* /
`0.42 surprise-units` and a bar with *"a bigger bar means I was more surprised"*.
Species is *"no living thing"*, because this quantity belongs to the model, not the bacterium —
**never blank**. The unit is *"surprise-units"*: a unit suffix in child words, as `:49` requires —
**not omitted**. If the equation is `NOT_BUILT`, the card reads *"we have not built this yet"* and
the value is an **em dash, never `0`**.

**VFE at `lab`** — *Variational free energy* / `[REDUCED MODEL] [species: not applicable] [BUILT]` /
`F[q] = sum_s q(s)[ln q(s) - ln p(o,s)] = KL[q || p(s|o)] - ln p(o) >= -ln p(o)` /
*"Measures model evidence. Not mechanical work. Not joules."* /
`F = 0.4213 nat`, `KL = 0.0000 nat`, `surprise = 0.4213 nat` / `-> Show the derivation (4 steps)`.
The plain sentence stays; it is not a play-only affordance.

**VFE at `audit`** — everything in `lab`, plus the binding
(`lib/uni-motor.js . bayesUpdateWithLikelihood -> .vfe`), the registry id, the derivation id with a
step count and a units verdict, the proof pin with `path:line` and sha256, the falsifier
**verbatim**, the gate row (today: *"no ledger row — 28 registered gates, 0 rows"*), and the
parity-test result.

**The EFE card at `audit` — because adverse results render too:**

```
[REDUCED MODEL] [species: not applicable] [DISPUTED]
G(pi) = risk + ambiguity - information gain + effort
!!  THE CODE DOES NOT COMPUTE THIS.
    G_code = KL[q(o)||C] + 2 . ambiguity + effort
    lib/uni-motor.js:328   .   audit E-M01
G = --   (the displayed equation and the running code disagree;
          this card shows no number until they are reconciled)
```

At `play` that same card reads: **"We are not sure this one is right yet, so we are not showing a
number."** Chips still present. Value still an em dash. **The child is told the truth in child
words.**

**NEW `tests/disclosure.test.mjs`** — render the same equation id at all three levels; assert the
**set of element tag+class paths is identical**, differing only in `hidden` attributes and text
content. Then at every level assert `.truth-chip`, `.species-chip`, `.status-chip` and `.unit-chip`
are present, and that no `.eq-number` for an inert equation contains `0`. This is the mechanical
form of `plan:625`.

**CSS constraint — and the dispute is now SETTLED by measurement, in MAIN's favour.**
**MAIN has no dead truth channel.** `UNI-FLAGELLUM/app/globals.css` is 544 lines, uses **18** `var()`
names and **declares 18**; the only two undeclared are `--font-geist-sans` and `--font-geist-mono`,
injected by `next/font` through `app/layout.tsx`. **The dead channel is STALE-only:**
`UNI-FLAGELLUM-math-workbench/app/globals.css` is 702 lines, uses 23 and declares 18, leaving
**`--cyan`, `--failure`, `--gold`, `--void`** plus the same two font vars. `plan:570` and
`docs/THE-LABORATORY-PLAN.md:127` both described the STALE file while citing MAIN.

So: every new `.equation-card`, `.derivation-*` and chip rule must use **only declared custom
properties**, and **the four colour tokens arrive in MAIN exactly when the workbench is ported,
which is W3.** Declare them in the same commit, and add `tests/globals-css-vars.test.mjs` — every
`var(--name)` reference a subset of every `--name:` declaration — which is **GREEN on MAIN today**
and **RED on the merged file until the four are declared.** That is the correct shape: a test that
is green now and goes red the moment the defect is imported.

### The ladder proved on one sheet — worksheet 2, the Bayesian update, at all three levels

**`detail` on a worksheet is a prop with no design behind it, and this closes that.** The twelve
prompts at `scientific-math-workbench.tsx:390-401` are adult, symbolic and demanding; the mapper at
`:402` gives every one of them the same twelve ruled lines. **There is no play-level prompt anywhere
in either tree.** Below is worksheet 2 authored at all three levels, ready to build.

**The underlying quantity is identical at all three levels and is named once:** the posterior after
one observation — `bayesUpdateWithLikelihood(prior, likelihood).posterior`, `lib/uni-motor.js:268-280`,
`.posterior` at `:271` — together with its normaliser, `evidence` at `:270`. **Every level computes
that.** Nothing is simplified into a different quantity; only the representation changes. **This is
the whole claim of the ladder and this sheet is where it is tested.**

#### `worksheet.bayes.play` — "Three boxes and a look"

> `[something we made up]` `[no living thing]` `[built and running]` — **counters out of 10**
>
> **Before you look.** Draw three boxes: **GOING DOWN**, **STAYING THE SAME**, **GOING UP**.
> Share your **10 counters** between them. Put more counters where you think it is.
> Write how many you put in each box: `___` `___` `___`
>
> **Now look.** The picture gives each box a helper number: **2**, **3**, **5**.
>
> **Multiply.** Counters × helper, one box at a time: `___` `___` `___`
>
> **Add them up.** That total is your **LOOK NUMBER**: `______`
>
> **Share again.** Colour in a bar of 10 squares for each box, giving each box the share it earned
> out of your LOOK NUMBER. **You will not land exactly on a square. That is fine — the machine does
> not round and you do. Write down how much you rounded by:** `______`
>
> **Which box grew? Which box shrank?** `____________________`
>
> *If the answer says **we have not built this yet**, every box is a dash — never a zero.*
>
> `lines: 0` (three drawn boxes, one 3×10 square grid, four blanks — **not** twelve ruled lines)

**What the play sheet must carry and why.** The 10 counters *are* the simplex, made of objects, so
"it has to add to ten" is **a fact of the desk and not a rule to memorise**. The helper numbers are
the normalised likelihood `[0.2, 0.3, 0.5]` with the decimal point removed. The LOOK NUMBER is
`100 × evidence`; **the ×100 is declared in the machine-written footer, never hidden.** **The rounding
box is the point:** *an approximation you write down is science; one you leave out is not.* A sheet
that quietly rounded would be teaching the exact failure the truth contract exists to stop.

#### `worksheet.bayes.lab` — the shipping prompt, **verbatim**, plus what the ladder adds

> **2 · One Bayesian update**
>
> *"Write q⁻=[___,___,___], likelihood=[___,___,___], joint=q⁻×likelihood=[___,___,___],
> evidence=Σjoint=___, posterior=joint/evidence=[___,___,___]. Check Σposterior=1."*
> — `scientific-math-workbench.tsx:391`, unchanged
>
> `[REDUCED MODEL]` `[species: not applicable]` `[BUILT]` — **q⁻, likelihood, posterior:
> dimensionless (each sums to 1) · evidence: dimensionless · surprise: nat**
>
> **Added by the ladder, not by rewriting the prompt:** a unit chip on every one of the five blanks,
> per `plan:49`; the binding printed under the prompt (`lib/uni-motor.js:268-280 → .posterior`); the
> self-check made two-sided (`Σposterior = 1` **and** `Σjoint = evidence`); one added line,
> `surprise = −ln(evidence) = ______ nat`, with the fence *"nats, not joules. There is no
> conversion."* — and `lines: 12`, unchanged, **so `globals.css:680-683` needs zero edits.**

#### `worksheet.bayes.audit` — everything in `lab`, plus what the machine actually did

> **Binding** `lib/uni-motor.js:268` `bayesUpdateWithLikelihood` → `.posterior` (`:271`), `.evidence`
> (`:270`), `.vfe` (`:272-276`), `.kl` (`:277`), `.surprise` (`:278`) · **Registry id** `BAYES` ·
> **derivation** 4 steps, units verdict `nat` · **proof pin**
> `lab/proofs/active_inference_bounds.md:<line>` + sha256 · **gate row** *"no ledger row — 28
> registered gates (25 `ci:true`), 0 rows in the canonical ledger"* · **bench** `question_id` +
> `answer_digest` of the run this sheet was printed from
>
> **A1 — the floor.** `:270` is `evidence = Math.max(EPSILON, Σjoint)` with `EPSILON = 1e-12`
> (`:14`). **Find a `q⁻` and a `likelihood` for which your hand calculation and the machine disagree,
> and state by how much.** hand `evidence = ______`, machine `evidence = ______`, difference
> `______`.
>
> **A2 — the identity that is true by construction, which is not the same as true.** `posterior` at
> `:271` is `joint/evidence`, and `kl` at `:277` is `klDivergence(posterior, normalize(joint))`.
> **Show that `kl` is identically zero, for every input, and therefore that `vfe` is identically
> `surprise`.** Then answer, in one sentence: *what would have to be different for `F = KL + surprise`
> to say anything at all?* `______________________________________________`
>
> **A3 — the falsifier, verbatim, printed at the foot and never paraphrased**, with a box for whether
> it fired and the minimum observed gap.
>
> `lines: 12` plus three bounded answer blocks.

**Same DOM at all three.** `<article class="workbook-page" data-detail="play|lab|audit">`, the same
`eyebrow`/`h3`/`p`/`footer`, the same `workbook-line` class. **Only text content and `hidden`
change** — `plan:623` applied to paper instead of to a card. The footer's third field is the
machine-written 40-hex commit from §4.4 at all three; the play footer additionally carries the `×100`
crosswalk, in the teacher's words, at the bottom of the page.

> **A2 is derived algebraically from reading `lib/uni-motor.js:270-278` and was NOT executed
> numerically. It must be run before the audit worksheet ships, because if it is wrong the exercise
> teaches a falsehood.**

### The chip-side rooms: `lab`-only in v1, and say so rather than implying otherwise

The rooms already standing on 8103 are **13 `.cjs` + 6 `.html`, plain server-rendered HTML, no React,
no build step**, routed by exact `url.pathname` equality in a 383-line server. **A React `detail` prop
cannot cross that boundary.**

**But the ladder is not a React feature.** It is `data-detail` on an element plus text substitution,
and a `.cjs` renderer emits that as easily as JSX does. So the honest split is:

- **The ladder's DATA is shared.** `playTitle`/`labTitle`/`auditTitle`, the child-words truth chips,
  the unit-in-child-words strings and the play/lab/audit prompt triples live in `lib/math/registry.js`
  and `lib/worksheets/registry.js` and are read by both surfaces as JSON.
- **The ladder's COMPONENT is not.** v1 declares the chip-side rooms **`lab`-only**, rendered at
  `detail="lab"` with a visible caption on every room index: *"This floor renders at lab level only.
  The play and audit levels exist in the laboratory and are not built here."*
- **Reason, stated so it is not mistaken for laziness:** hand-porting a three-level renderer into a
  second language is exactly how two surfaces drift, **and this project already carries a stale
  worktree as evidence.** When the shared data file exists and is gated, a `.cjs` renderer is a small
  job; before it exists, it is a duplicate.

### Acceptance — one label check, one non-label check, and the non-label one is NOT_ESTABLISHED

**AC-B1 (mechanical, and it only checks labels).** Render `worksheet.bayes` at all three levels: the
set of element tag+class paths is identical; `.truth-chip`, `.species-chip`, `.status-chip` and
`.unit-chip` are present at **all three**; no inert value renders `0`; the play sheet contains no
Greek character, no subscript and no word longer than eight characters; `data-detail` is present on
every `.workbook-page`. **This proves nothing whatsoever about whether a child can use the sheet.**

**AC-B2 — NON-LABEL, and `NOT_ESTABLISHED` until it is actually run with a person.**

> **Claim:** a person who cannot read algebra can complete `worksheet.bayes.play` unaided and, when
> shown the `lab` sheet immediately after, can point at the box on their own play sheet that
> corresponds to `posterior`.
>
> **Protocol:** five people, one at a time, no coaching, the sheet handed over with no verbal
> explanation beyond *"have a go."* Recorded per person: completed / did not complete; the
> correspondence question answered correctly / incorrectly / not attempted; the rounding box filled in
> or left blank; and **verbatim, the first question each person asked.**
>
> **Falsifier:** three or more of five fail to complete, **or** three or more cannot point at the
> posterior box. Either outcome **falsifies the play level and the sheet is redesigned rather than
> re-labelled.**
>
> **Status: `NOT_ESTABLISHED`. This has not been run with anybody.** It is not executable by an
> agent, by a test, or by a screenshot. **No green result from AC-B1, and no screenshot of a play
> sheet, may ever be reported, summarised or shown as evidence about a child.** The status stays
> `NOT_ESTABLISHED` until five recorded sessions exist with their verbatim first questions, and the
> adverse ones are reported alongside the rest, never instead of them.

## 4.6 THE DERIVATION AND PROOF RENDERER

**Eight finished proof documents, 501 lines / 41,451 B, in a stable seven-to-nine section schema, and
nothing renders them.** `UNI.Minecraft/lab/proofs/` — and **only** there; `ls UNI-FLAGELLUM/lab/proofs`
returns *No such file or directory*. The eight: `active_inference_bounds`,
`bioenergetics_proton_gradient`, `dgst_d_value_audit`, `dimensional_analysis`, `limitations`,
`ozone_photochemistry`, `uv_filtering`, `water_escape`. All eight share:

`# Title` -> `## Scope` -> `## Equations` -> `## Variables and units` ->
`## Worked example (with numbers)` -> `## Dimensional check` -> `## Evidence class per claim` ->
`## Falsification conditions` -> `## Outside this model (fence)`

8 of 8 have Scope, Worked example, Dimensional check, Falsification conditions and Outside this
model. **Heading wording varies — FOUR distinct spellings of the Equations heading, not five:**
`## Equations (preserved exactly)` in four files (`active_inference_bounds:7`,
`dgst_d_value_audit:7`, `uv_filtering:7`, `water_escape:7`), `## Equations (preserve exactly)` in
`bioenergetics_proton_gradient:7`, `## Equations, Units, and Checks` in `dimensional_analysis:7`,
and `## The governing equations (preserved exactly)` in `limitations:21`.

> **And the stronger finding, which the "five spellings" claim hid: the eighth file has NO equations
> heading at all.** `ozone_photochemistry.md`'s equations live under `## The four Chapman reactions`
> (`:7`). **Any parser keyed on the word "Equations" silently skips it** — which is exactly the
> vacuous-success failure `parse_proof.cjs`'s golden-test-per-file criterion (§7.3 W16) exists to
> catch, and it must be written so that skipping a file is a FAIL, not a pass with seven results.

32 LaTeX display blocks; 6 of 8 carry markdown variable tables; evidence classes are
**A/B/C/D/U/X**. *(Note on the count: all eight files lack a trailing newline, so `wc -l` totals 493
and an editor totals 501. §10.0's methodology note settles which this document uses.)*

### The Derivation shape — `lib/math/derivation.js`

Fields: `id`, `title`, `domain`, `scope` (verbatim),
`assumptions[{text, evidenceClass, why}]`, `claim{lhs: Term, rhs: Term, unit}`,
`steps[{n, from: Term, to: Term, rule, justification, unitsBefore: null, unitsAfter: null,
citation}]`, `dimensionalCheck{perTerm[], verdict}`, `worked{inputs, expected, unit, tolerance}`,
`evidenceClasses[]`, `falsifier` (verbatim), `outsideModel` (verbatim),
`sourcePin{path, sha256, headingLine}`. `rule` is one of
`DEFINITION | SUBSTITUTE | ALGEBRA | LIMIT | NUMERIC | CITED`.

> **`unitsBefore` and `unitsAfter` are `null` in the data and filled by `units.js` at render.**
> The document's own units claim is never trusted; the renderer recomputes it. A step whose computed
> units differ from its neighbours renders a red **UNIT BREAK** row.
> **The renderer carries its own falsifier.**

### The renderer

`app/(lab)/lab/proof/page.lab.tsx` (index, `/lab/proof`) plus
`app/(lab)/lab/proof/[id]/page.lab.tsx` (server, `/lab/proof/<id>`) plus
`app/(lab)/lab/proof/derivation-view.tsx` (client). **Re-pathed by §0.9 decision 3: the draft named
`app/proofs/page.tsx` and `app/proofs/[id]/page.tsx`, which under §0.2 are PRODUCT routes that ship
to the chip — the same defect as the chalkboard, in a section nobody had checked.** Both are ≤ 3 path
segments, so §3A.10 criterion 2's depth rule is unaffected. Reading order, top to bottom:

```
EQUATION      claim.lhs = claim.rhs      [unit chip] [truth chip] [domain chip]
ASSUMPTIONS   n rows:  text . evidence-class chip . why
STEPS         n rows:  from --> to
                       [rule chip]  justification
                       units: <computed-before>  ->  <computed-after>   OK | UNIT BREAK
DIMENSIONAL   per-term reduction table, verdict
WORKED        inputs -> expected, tolerance, and a RUN IT button
FALSIFIER     verbatim, in a bordered block
OUTSIDE       verbatim fence, never summarised, never collapsed by default
SOURCE PIN    path . line . sha256                      (audit level only)
```

### Conversion cost — the honest answer

**Cheap and automatable** — `UNI.Minecraft/lab/proofs/parse_proof.cjs`, roughly 200 lines,
deterministic, golden-tested per file: section split by a **normalised** regex, because heading
wording varies (**8/8**); `scope`, `falsifier` and `outsideModel` verbatim (**8/8**); the 32 display
blocks lifted as `latex` strings (**8/8**); variable tables (**6/8** — `active_inference_bounds` and
`dimensional_analysis` use bullets and inline text and need a second extractor or hand entry);
evidence-class bullets (**8/8** in substance, one heading alias to handle).

**Expensive and NOT automatable — say it plainly:**

- **LaTeX to `Term` AST.** The 32 blocks use `\underbrace`, `\mathbb{E}`, `\int`, `\tfrac`,
  `D_{\mathrm{KL}}` and `\;` spacing. Writing a parser for that subset is a real project and a regex
  does not do it. **v1 stores the LaTeX verbatim as a display field and hand-authors `Term` for the
  six v1 equations only.**
- **The `steps` array is the real cost, and 7 of 8 documents cannot be parsed into it at all.**
  The Worked Example sections are narrative paragraphs — `bioenergetics_proton_gradient.md:33-41` is
  three prose paragraphs, not an ordered list. **The single exception is
  `dimensional_analysis.md:9-38`**, already written as (equation, symbol list, `Check: ...`,
  `**PASS.**`) seven times over; that one converts **by parser**. The remaining seven need a human
  to segment prose into ordered steps and choose the `rule` for each. Rough size: **30 to 55
  hand-authored step objects.**

**So: the parser does the scaffolding — sections, equations, variables, evidence classes, falsifier,
fence — and a human writes only the `steps` array.** There is no clever way around it, and rushing
it produces steps that restate the equation with no justification, which is **worse than no
renderer**, because it has the appearance of a derivation and would launder an unjustified leap.

**Convert in this order:** `dimensional_analysis.md` (parses fully, and certifies all seven
load-bearing formulas) -> `active_inference_bounds.md` (the VFE/EFE proof, which directly backs the
v1 registry entries) -> the remaining six.

### The vocabulary collision — the operator's, not an agent's

**There are FOUR truth/evidence vocabularies in this project and no crosswalk file exists in any
tree:**

| vocabulary | members | declared at |
|---|---|---|
| MAIN truth classes | `OBSERVED`, `STRUCTURAL_RECONSTRUCTION`, `REDUCED_MODEL`, `UNI_PHYSICAL_ANALOGUE` | `lib/walkthrough.js:5`, `lib/walkthrough.d.ts:2` |
| chip scene classes | `OBSERVED`, `STRUCTURAL_RECONSTRUCTION`, `REDUCED_MODEL`, `DERIVED`, `SIMULATED`, `UNKNOWN` | `UNI.Minecraft/lib/sp/control_plane/scene.ex:40` |
| proof evidence classes | `A`, `B`, `C`, `D`, `U`, `X` | `lab/proofs/bioenergetics_proton_gradient.md:51-57` |
| gate-row evidence class | `A`, `B`, `C`, `Sec`, `pending` | `production/schemas/gate_row.schema.json` |

The first two intersect in three members. `UNI_PHYSICAL_ANALOGUE` has no chip representation;
`DERIVED`, `SIMULATED` and `UNKNOWN` have none in MAIN. **Any automatic mapping is truth laundering
under the closed-vocabulary clause.** The renderer must display **both, side by side, each labelled
with its origin document**, and the bench record must **REFUSE to carry a class outside the
intersection rather than silently coercing one.** Reconciliation is an operator decision (section 8).

### The domain fence

The eight proofs are about ozone photochemistry, planetary gravity, UV attenuation and water
escape — **NOT the flagellum**. Rendering them inside the flagellum lab risks implying they support
flagellar claims. They occupy a **separate wing with an explicit `domain` label on every card**, and
the derivation shape carries a `domain` field for exactly that reason.

## 4.7 THE SIX SOCKETS — SEE / THINK / EXPECT / WANT / SURE / DO

**They exist in ZERO code files in all three trees.** Every occurrence is prose, in
`docs/THE-LABORATORY-PLAN.md` and `docs/UNI-STACK-BUILDER-PLAN.md`. UNI.Minecraft has zero
occurrences of THINK and zero of WANT. The only specification is `plan:474-484` (the table) and
`:485-516` (a 24-brick palette grouped by socket).

**NEW `lib/math/sockets.js`.** A socket is a **typed hole with two labels and two questions.**
The type is identical; the sentence is not.

| socket | PortKind | unit | child reads | researcher reads |
|---|---|---|---|---|
| **SEE** | `Obs` | declared per channel | "What just happened?" | the timestamped observation record that crossed the Markov boundary, with truth class and source pin |
| **THINK** | `Simplex` | probability, sums to 1 | "What do I think is going on?" | the approximate posterior q(x) after this observation |
| **EXPECT** | `Matrix` | probability, columns sum to 1 | "If that were true, what would I see next?" | column-stochastic A and B, per policy |
| **WANT** | `Nats` | nat (log preference) | "What would I like to happen?" | unnormalised log preferences C, D, E, and the additive-constant convention |
| **SURE** | `Scalar` | dimensionless | "How much do I trust this?" | policy precision and the sensory precision schedule, and whether gamma is justified |
| **DO** | `Act` | one of a closed action set | "So what do I do?" | the policy posterior, its scoring rule, and whether the action was committed before the next observation |

Each entry also carries a `childWhy` and an `invariant`. Four invariants worth quoting, because they
are the teaching:

- **SEE** — *"Only the observation crosses inward. World truth never does."*
- **THINK** — *"q is the agent's belief. It is never displayed as the world's truth."*
- **WANT** — *"C is in nats. A Joules quantity cannot enter this socket. There is no conversion."*
- **SURE** — *"gamma = 4 is an undeclared magic number today (audit NR-08, `uni-motor.js:348`)."*

`kind` values are **verbatim** the `PortKind` union already declared at `plan:63-65`. The socket
module is the plan's table turned into the code the plan assumed existed.

**The sockets are also the index.** Re-index the existing eleven catalog entries onto the six:
`BOUNDARY -> SEE`; `BAYES, VFE -> THINK`; `DURATION, DLT, ROTATION, LATTICE, GMC, RFT -> EXPECT`;
`EFE -> DO`; and **`WORLD -> none (it is the world, not the agent — and saying so out loud is the
teaching)`**. That last row is the point: **not every equation belongs in a socket, and the ones
that do not are the world process.** The socket layout makes the Markov boundary a piece of
furniture.

**`tests/sockets.test.mjs`:** `SOCKETS.length === 6` and the array is frozen; for every socket the
`play` label contains no Greek character, no subscript and no word longer than 8 characters,
`formal` is non-empty, and `kind` is a member of the `PortKind` union; every registry entry's
`sockets` are members; and `equationsIn(s)` over all six covers the registry exactly once, except
entries explicitly marked `sockets: []` with a stated reason.

> **This is a mechanical legibility check on LABELS. It proves nothing about whether a child can use
> the artifact.** A green socket test must never be reported, screenshotted or summarised as
> evidence of child usability. That claim stays `NOT_ESTABLISHED` with its stated falsifier, because
> "five children aged 7-10" is not executable.

## 4.8 WORKING AN EQUATION — five verbs, end to end

**"Working" means five things, in order.** `app/(lab)/lab/chalkboard/work-the-equation.tsx`, mounted
inside `equation-card.tsx`: the full panel when `detail !== "play"`, a reduced form at `play`.

**1. SUBSTITUTE — the numbers are yours, not the demo's.** For VFE, a 3-simplex triangle where
`q = [falling, flat, rising]` is a **draggable point**; dragging re-normalises visibly, so
conservation is something you feel rather than a sentence you read. Three number inputs mirror the
drag for the researcher.

Every drag calls `freeEnergyAt(q, prior, logLik)` **and, in parallel**,
`evaluate(REG.VFE.rhs, {q, prior, logLik})` from `lib/math/expr.js`. **Both are shown.** If they
differ by more than `1e-12` the panel prints `REGISTRY DIVERGENCE` — the display and the machine
disagreeing, live, on screen.

*Prerequisite build item:* **export `freeEnergyAt(q, prior, logLik)` from `lib/uni-motor.js`.**
**It does not exist as code — `grep -rn "freeEnergyAt" app/ lib/` in MAIN exits 1.** The only four
occurrences anywhere in MAIN (excluding `node_modules/`) are specification text in
`docs/UNI-STACK-BUILDER-PLAN.md`: `:348` the signature, `:601` the teaching affordance, `:766` and
`:904` the gate. `:601` requires it be separate from the minimiser *precisely so the UI can evaluate
F at any user-supplied q.* Additive; no behaviour change to `stepAgent`.

> **The rule this sentence broke, stated once and applied throughout (§9.0).** A previous revision
> wrote *"`grep -rn "freeEnergyAt"` over MAIN returns zero"* and then cited `plan:601` in its very
> next clause — disproving itself in its own second half. **This repository documents almost every
> symbol it does not implement, so an unscoped "returns zero" is nearly always false.** Every
> absence claim in this document must name the directories searched. Where the claim is *"there is
> no implementation"*, the search is over `app/` and `lib/` only, and it says so.

**2. PREDICT-THEN-REVEAL.** Before the F bar is drawn: *"Before you look — how surprised do you
think this makes me?"*, with a number input and the unit chip already showing `nat`. On Reveal:

```
you said   0.60   nat
F          0.4213 nat
you were   0.179  nat high
```

**The guess writes into the EXISTING notebook.** `NotebookDraft` at `app/guided-teacher.tsx:6-13`
already has `prediction`, `observation`, `calculation`, `interpretation`, `alternativeExplanation`,
a confidence slider, a save path, JSON/CSV export, a round-trip self-test
(`living-science-walkthrough.tsx:326-334`) and a truth-class validator (`lib/walkthrough.js:439`).
**Do not build a second notebook.** Add one field, `equationId`, and reuse everything else. At
`play` the numeric guess becomes three faces and the reveal is a bar height next to a guess height —
same DOM, same record.

**3. STEP THE DERIVATION.** `-> Show the derivation (4 steps)` opens `/lab/proof/<id>` inline. Each
press of **NEXT STEP** reveals one row: `from -> to`, the rule chip, the justification, and the
**computed** units on both sides. The following row is `hidden`, not greyed — so the operator can
predict it. A *"guess the next line"* input sits above the hidden row; on reveal it says whether the
guessed **rule** matched (`ALGEBRA` vs `SUBSTITUTE`), which is teachable even when the algebra is
not typed correctly.

For VFE the four steps are: (1) `F[q] = sum q ln(q / p(o,s))` — DEFINITION — nat; (2) split the log,
`= sum q ln q - sum q ln p(o,s)` — ALGEBRA — nat; (3) factor `p(o,s) = p(s|o) p(o)` — SUBSTITUTE —
nat; (4) `= KL[q || p(s|o)] - ln p(o)` — DEFINITION (KL) — nat. Then the bound
`KL >= 0  =>  F >= -ln p(o)`, marked **CITED** to `active_inference_bounds.md:45`.

**4. BREAK IT — the falsifier is a button, not a paragraph.** Three buttons:

- *set q = the posterior* -> KL collapses to 0, the bound goes tight, `F = surprise`; the bar drops
  to a drawn floor line;
- *set q = degenerate* -> KL large, F far above the floor;
- *try to go below the floor* -> the panel prints, **verbatim from `active_inference_bounds.md:52`**:
  > *Observe F < -ln p(y|m) for any q -> the bound identity is **contradicted-by-test**.*

  and reports that across the sweep the minimum observed `F - (-ln p(o))` was `0.0000 nat`, never
  negative. **The falsifier ran. It did not fire. That is the result, and it is printed.**

**5. PRINT WHAT I JUST DID.** A **Print this as a worksheet** button emits a `WorksheetSpec` at
runtime whose prompt is the operator's **own** substituted values with the answers blanked, plus his
prediction, plus the four derivation steps with the justifications removed for him to write back in.
It routes through the **existing** print path (`printWorkbook`) and the **existing** CSS. The footer
carries the machine-written commit from 4.4.

**A working session becomes paper. That closes the loop the operator asked for.**

## 4.9 TRI-MODE ON THE SAME CARD

Three tabs on every equation card: **OFFLINE . ONLINE . COMPARE**, exactly as section 2 defines them.
OFFLINE is `evaluate(term, env)` in the browser — pure kernel, zero network, the clause at
`tests/walkthrough.test.mjs:119` extended (never relaxed) to the new files. ONLINE is the same
quantity observed through the broker. COMPARE renders both with the declared tolerance, and on
divergence renders a **FINDING** card carrying the equation id, both values, the tolerance, and both
code identities — and stating that it **cannot write this to the ledger**, in the words
`viewer/lab/desk.cjs:472-475` already uses.

**A divergence is a finding, and the bench that found it is not allowed to rule on it.** That is the
lab and the door doing their separate jobs.

## 4.10 THE STEPPER — watching one tick execute

**Address: `app/(lab)/lab/stepper/page.lab.tsx`** (§0.3). Workstream **W31**.

### The retraction that has to come first

**This plan let you step a *proof* and diff a *trace*, and never once designed a view where you watch
a *computation* execute.** Measured over the draft: `setInterval` appeared **zero** times, `Run/Pause`
and `run-toggle` **zero** times, and `single-step|stepper|scrubber|time scrub|pause-and-inspect|replay`
appeared **once** — quoting a `REPLAY MISMATCH` banner out of another document. §5.1 names a view
*"The loop, stepping"* and then specifies sliders, bars and a table. **A title is not a control.**

And the miss is worse than an omission, **because the thing already runs** (§3A.2): a
`window.setInterval` at `uni-flagellum-lab.tsx:488` firing every 80 ms, cleared at `:524`, gated at
`:494`, with a Run/Pause button at `:647-649` and four world sliders. The plan neither built on it nor
mentioned it. `docs/THE-LABORATORY-PLAN.md:23` R4 asks, in the operator's own words, to **"See the
math run."**

Worse still, **a step-control vocabulary was already frozen and this draft dropped that too**:
`docs/UNI-STACK-BUILDER-PLAN.md:617` specifies the transport bar as
`STEP · RUN ×[10|100|1000] · STOP · RESET · UNDO · seed field · stackHash[0..12] · detail switch
play | lab | audit`, and `:619` calls `UNDO` first-class at every level, judging its absence *"fatal
for the child path."* **The Stepper reuses that bar verbatim.** It introduces exactly one control the
plan of record does not have — `JUMP TO TICK n` — and says so out loud, because **a 900-tick tape you
can only walk one step at a time is a tape you never walk.**

### The measured reason this is a build and not a decoration

**A tick computes far more than it returns, so today there is nothing for a view to show.**

*World half* — `lib/uni-motor.js:139-198` declares 22 `const` bindings: one accumulator (`next`
`:141`), five fixed model parameters (`receptorTeams` `:158`, `kOffUm` `:159`, `kOnUm` `:160`,
`epsilonM` `:161`, `hill` `:191`), and **sixteen quantities computed every tick that nothing
returns** — `dt` `:140`, `run` `:143`, `speedUmS` `:145`, `spatialExponent` `:153`, `ligandTerm`
`:162`, `receptorFreeEnergy` `:163`, `receptorActivity` `:164`, `cheYTarget` `:172`, `loadFraction`
`:175`, `statorTarget` `:176`, `remodelingTauS` `:177`, `pmfFraction` `:184`, `stallTorque` `:185`,
`zeroLoadRpm` `:187`, `kdUm` `:190`, `switchWave` `:193`.

*Boundary* — `observeWorld` `:203-217` computes `noise` `:204` and `ligandObserved` `:205`; **neither
appears in the observation record.**

*Agent half* — and this is the load-bearing one:

| computed at | returns | `stepAgent` surfaces | **discarded** |
|---|---|---|---|
| `bayesUpdateWithLikelihood` `:268-280` | `posterior, likelihood, joint, evidence, vfe, kl, surprise` (7) | `posterior` `:367`, `likelihood` `:368`, `vfe` `:379`, `surprise` `:380` (4) | **`joint`, `evidence`, `kl`** |
| `policyTerms` `:309-330`, called twice (`:346` RUN, `:347` TUMBLE) | `qState, qOutcome, risk, ambiguity, informationGain, effort, efe` (7 per policy) | `efe` `:370`, `risk` `:371`, `ambiguity` `:372`, `informationGain` `:373`, as 2-element arrays (4) | **`qState`, `qOutcome`, `effort` — for both policies, six values** |
| `stepAgent` locals | — | `prior` as `priorAtUpdate` `:365`; three odds as logs `:381-383` | **`ligandRate` `:335`, `signedRate` `:350`, `stallTorque` `:352`** (a *second* `stallTorque`, the agent's estimate, sharing a name with the world's at `:185` — itself teachable) |

**Twelve agent-side quantities are computed at every tick and no surface in any tree can ever show
them, because `stepAgent` does not return them.** That is the finding, and it is why the Stepper's
first build item is **in the kernel, not the UI.**

### The determinism defect the Stepper exposes on contact

The synthetic kernel is **deterministic given `(system, controls, dt)`**: `deterministicNoise`
`:128-130` is a function of `world.timeS` alone, and `observeWorld` carries `receivedAtMs` into the
record at `:209` without ever computing with it. **All of the non-determinism is supplied by the
UI** — `dt` derived from `performance.now()` at `uni-flagellum-lab.tsx:487,489,492` and clamped to
`[0.01, 0.1]`, and `receivedAtMs` from `Date.now()` at `:490`.

**Consequence, stated before it is discovered: two runs of the current loop are never the same run,
and a tape recorded from it is not replayable.** So a `RunSpec` declares `dt` and `epoch0`, and the
Stepper computes `receivedAtMs = epoch0 + n·dt·1000`. **The Stepper never reads a wall clock.**

**These are UI-side clocks, and §2.1's kernel census does not cover them.** Measured this session
with `grep -rn "Date\.now()\|performance\.now()\|new Date()"`: `lib/` carries exactly **three**
ambient clocks — `uni-motor.js:408` (inside `modelSnapshot`, which is that same clock, not another
one), `walkthrough.js:385`, `walkthrough.js:408`. `app/` carries **seven more, across three files**:
`uni-flagellum-lab.tsx:487` and `:489` (`performance.now()`, feeding `dt` at `:492`), `:490`
(`Date.now()` → `epochNow`, which becomes `receivedAtMs` at the `stepSyntheticSystem(current,
controlsRef.current, dt, epochNow)` call on `:508`), `:566` (`Date.now()` on the serial path, into
`instrumentObservation`), `biological-stage.tsx:247` and `:268`, and
`living-science-walkthrough.tsx:41`. The four in the loop — `:487`, `:489`, `:490`, `:492` — are what
the Stepper displaces, and **they are what would have silently broken the first tape.**

### Build items — expose the existing loop's single-step path, never a second loop

**1. `lib/kernel/uni-motor.js` — additive traced exports.** `stepWorldTraced(world, action, controls,
dt)` and `stepAgentTraced(agent, observation, dt)` return `{ next, trace }`, where `next` is
**byte-identical to what `stepWorld`/`stepAgent` return today** and `trace` is a flat array of
`{ name, value, unit, stage, source }` carrying every quantity in the table above. `stepWorld` and
`stepAgent` become one-line wrappers that drop `trace`. **No existing caller changes and no existing
test moves.**

**2. `lib/kernel/f64.js` — NEW, ~20 lines.** `toF64Hex(v)` (`DataView.setFloat64(0, v, false)` → 16
lowercase hex) and `changed(a, b)`. **W7 consumes this rather than re-authoring it** — §7.2 item 7.

**3. `app/(product)/uni-flagellum-lab.tsx` — extract, do not duplicate.** The interval callback body
(`:496-511`) becomes a named `advance(spec, n)` declared beside `reset` (`:532-537`). The
`setInterval` at `:488` calls `advance`; so does `STEP`. **There is one advance path and the Stepper
is the same one the running world uses.** A test asserts there is exactly one `stepSyntheticSystem*`
call site in the file.

**4. `app/(lab)/lab/stepper/page.lab.tsx` — NEW.** It takes `{ spec, tape, detail }` and renders
**tick n** in two columns with the Markov boundary drawn between them — WORLD on the left, AGENT on
the right, the boundary carrying exactly the two things `observeWorld` lets across. Every quantity is
one cell: name, value, **unit chip**, truth chip, and `data-f64`. **Nothing is aggregated and nothing
is rounded away.** *(It is a lab route, not an eighth product tab: the product's seven-tab switcher
is untouched, and the Stepper cannot ship — §0.4.)*

**5. The transport bar**, verbatim from `plan:617`, plus one addition:
`STEP · RUN ×[10|100|1000] · STOP · RESET · UNDO · JUMP TO TICK n · seed · detail switch`.
**`UNDO` *is* BACK** — the plan already named it and naming it twice is how two surfaces drift.
**`STEP` is absent, not greyed, while the loop is running** — the same absent-not-disabled rule
`/lab/l5` uses (§3.6).

**6. The value-changed highlight compares f64 bits, never rendered decimals.** A cell carries
`data-changed="true"` when `toF64Hex(v_n) !== toF64Hex(v_{n-1})`. **A highlight that compares the
printed decimal teaches the operator that nothing moved when the fifteenth digit moved**, which is
precisely the lie the whole COMPARE instrument exists to prevent. Same rule, same helper, one tick
apart instead of one engine apart.

**7. The tape — replay for free.** `uni.bench.tick-tape/1.0.0`: the `RunSpec` (carrying the bench
record's own **`question_id`**, §2.3) plus one `TickTrace` per tick, every number as f64-hex with a
`decimal` field riding alongside and never hashed. A **900-tick ring buffer** is 72 s of history at
80 ms. Export and import are plain JSON; **a tape is diffable by the §2.4 divergence machinery with
no new comparison code at all.**

### What the Stepper must never do

**It may not display a quantity the kernel does not compute.** If a teaching-shaped intermediate is
missing, the fix is to compute it in the kernel and return it in the trace — **never to recompute it
in the view**, which would make the Stepper a second implementation and its agreement with the bench
a coincidence. v1 is **OFFLINE only**: pure kernel, no network, inside W2's sealed boundary, adding
zero rows to the observation channel.

### Acceptance — behavioural, and tied to a bench record

**AC-S1 (one step is one step).** With the loop paused, one press of `STEP` increases
`agent.observationCount` (`uni-motor.js:384`) by exactly 1 and `history.length` by exactly 1. While
the loop is running, `STEP` is **absent from the DOM**.

**AC-S2 — THE BENCH-RECORD CRITERION.** Hand-step a `RunSpec` to N=64 in the browser, then run the
**same** `RunSpec` headless through `scripts/bench-run.mjs` (W7). The two bench records must carry an
**identical `question_id` and an identical `answer_digest`**. **If the digests differ, the Stepper is
a second implementation and is deleted, not reconciled.**

**AC-S3 — the mutation that proves the highlight bites.** Perturb the last mantissa bit of
`bRun[0][0]` (`uni-motor.js:255`, `0.82`) in a scratch copy of the kernel and step the same `RunSpec`
to tick 1. The Stepper must mark `qState(RUN)` `data-changed="true"` **and** the `answer_digest` must
differ. **If the highlight does not fire on a last-bit change it is comparing decimals, and the test
fails.** *(If `normalize()` at `:265` absorbs the perturbation, the mutation target moves — the
criterion does not weaken.)*

**AC-S4 (UNDO is real).** `UNDO` from tick n renders cell values whose re-hashed f64 set equals the
tape's tick n−1 — asserted by re-hashing the **rendered** cells, not by reading the tape back.

**AC-S5 (replay).** Export the tape at tick 64, load it into a cold page whose loop was never started,
`JUMP TO TICK 40`, and every cell equals the live session's tick 40.

**AC-S6 (the twelve are actually on screen).** For each of `joint`, `evidence`, `kl`, `qState(RUN)`,
`qState(TUMBLE)`, `qOutcome(RUN)`, `qOutcome(TUMBLE)`, `effort(RUN)`, `effort(TUMBLE)`, `ligandRate`,
`signedRate`, `stallTorque(agent)`: read the cell's `data-f64`, recompute that quantity **from the
recorded tick inputs with an implementation that does not import `uni-motor.js`**, and require
agreement to `1e-12`. **Deleting one field from `stepAgentTraced` makes the cell absent and the test
fail.**

**AC-S7 (determinism, the honest one).** Two tapes from the same `RunSpec` are **byte-identical**.
Running the same spec through the *unmodified* `setInterval` path produces tapes that **differ**, and
that difference is **printed on screen as `WALL-CLOCK dt — NOT REPRODUCIBLE`** rather than hidden.

## 4.11 Acceptance criteria for section 4

1. Dragging the simplex changes F on screen, and `freeEnergyAt` and `evaluate(REG.VFE.rhs)` agree to
   `1e-12`. A deliberately mismatched registry entry produces a visible `REGISTRY DIVERGENCE`.
2. `tests/math-registry.test.mjs` **fails on EFE** on the tree as it stands, and passes on every
   other v1 entry.
3. `tests/math-units.test.mjs`: adding a nats term to a joules term throws `UNIT_MISMATCH` with the
   authored message; no export matches `/convert|toJoules|toNats/`; the no-eval source scan covers
   `lib/math/**` in the same change that creates it.
4. Server-rendering the worksheets view yields exactly 12 `workbook-page` articles and 144
   `workbook-line` divs, and the footer contains a 40-hex commit. Deleting one tuple fails the test.
5. Ctrl+P from **every** tab prints the workbook (PRD-03 closed).
6. `tests/disclosure.test.mjs`: identical tag+class paths at all three levels; the four chips present
   at all three; no inert `.eq-number` contains `0`.
7. Seeding a units mismatch into a derivation JSON makes the renderer draw `UNIT BREAK` — proving
   the units are computed, not copied.
8. The falsifier button reports a minimum gap and states whether the falsifier fired.
9. `tests/sockets.test.mjs` passes, and the report of it **never** appears in any summary as evidence
   about children.
10. One `STEP` advances exactly one tick; `STEP` is **absent** while the loop runs.
11. A 64-tick hand-stepped session and a headless `bench-run.mjs` of the same `RunSpec` produce the
    same `question_id` **and** the same `answer_digest`.
12. Flipping the last mantissa bit of `bRun[0][0]` lights the `qState(RUN)` changed-highlight and
    changes `answer_digest`; **a decimal-comparing highlight fails this.**
13. `worksheet.bayes` renders at `play`, `lab` and `audit` with identical tag+class paths, four chips
    at every level, and no inert `0`. **The play sheet's rounding box is present in the DOM.**
14. **AC-B2 reports `NOT_ESTABLISHED` in every surface that renders the play level, and the string
    `NOT_ESTABLISHED` is drawn on the sheet itself, not only in a report.**

---

# 5. THE WINGS — every body of mathematics in the repositories

## In plain words

**There are fourteen distinct bodies of mathematics across the three trees. Nine of them have no
user interface of any kind.** The building already exists — `UNI.Minecraft/viewer/lab/` on
`127.0.0.1:8103`, L0 to L6, six registered gates, roughly 5300 lines — and **it contains zero
mathematics**. A case-insensitive grep for `gravity|escape_velocity|nernst|ozone|flagell|torque|
PMF|stator` across every `.html` and `.cjs` in that directory returns nothing; the only `Math.*`
calls are isometric projection arithmetic. It is a building with no laboratory in it.

**CORRECTED BY §0, AND THIS PARAGRAPH USED TO SAY THE OPPOSITE.** It read: *"Each wing below is a
new floor in **that** building, served by **that** server, gated by **that** runner. Nothing in this
section proposes a second surface."* **That is false under the surface decision, and it was already
false against §4, which put the same catalog in MAIN's React app.** The plan carried two
architectures at once — the exact defect `viewer/verify_plan_consistency.cjs` was written to catch.

**Under §0.2, §0.5's re-pathing rule and §0.9 decision 2:** the wings are floors in the **laboratory
application**, served by **one manifest-driven route** — `app/(lab)/lab/wing/[wing]/page.lab.tsx` at
**`/lab/wing/<wing>`** — with their panels at **`app/(lab)/lab/wing/[wing]/panels/<wing>.tsx`** and
their offline kernels at **`lib/kernel/mirrors/<wing>.js`**. **A bench is a kind of room; there is no
`/lab/bench` route family, and the draft that carried both is corrected throughout.** A wing
workstream builds its **panels and its kernel**, never its route — the route is built once, by W2b. **`UNI.Minecraft/viewer/lab/` is the gate and room renderer they
read from** — over HTTP, through the single declared channel at `app/(lab)/api/chip/route.lab.ts`,
with no modification to any of its 5,326 lines. Every wing's per-wing specification below survives
intact; **only the host changes.** Where the text below names a `viewer/**.cjs` file, it is naming a
**computation or a gate**, never a rendering surface.

## 5.0 The master inventory

| # | Body | Where | Size | Tested | UI today | **Offline-capable** | Wing |
|---|---|---|---|---|---|---|---|
| 1 | Reduced flagellar world + AIF agent | `UNI-FLAGELLUM/lib/uni-motor.js` | 420 | yes (3 suites) | partial (loop, math panels) | **yes** | W-FLAG |
| 2 | Duration-model competition, held-out scoring | `lib/observed-experiment.js` | 500 | yes (5 suites) | read-only panel | **yes** | W-FLAG |
| 3 | DLT first-passage competing risks | `lib/source-first-passage.js` | 77 | yes (1 semantic) | **none in MAIN** | **yes** | W-FLAG |
| 4 | Seconds-scale duration scorer | `lib/duration-models.js` **STALE ONLY** | 114 | **yes — 5 tests** (see §4.4 defect 4) | STALE workbench only | **yes** | W-FLAG |
| 5 | Truth classes, walkthrough, lesson export | `lib/walkthrough.js` | 472 | yes | yes | **yes** | W-FLAG |
| 6 | Parametric CAD / mechanical Bayes | `lib/cad.js` | 144 | partial | yes (cad panel) | **yes** | W-FLAG |
| 7 | Cross-study parity: 5 physics bodies | `scripts/run-cross-study-parity.py` | 495 | yes + oracle | verdicts only | **report-only ‡** | W-PARITY |
| 8 | Science gates `G00_…`–`G13_…` | `scripts/run-science-gates.py` | 624 | yes | verdicts only | **report-only** | W-PARITY |
| 9 | Independent oracles ×4 | `scripts/independent-*.{mjs,py}`, `verify-ito-raw-archive.py` | 454 | n/a | **none** | **report-only ※** | W-PARITY |
| 10 | Semantic suite — mathematics about mathematics | `tests/semantic/` | **11 files, 3853** | is the test | **none** | **yes** | W-PARITY |
| 11 | H-AIF constrained motor stack | `hierarchical-aif/src/motor_stack_aif/` | **20 files, 3071** | 339 tests | **one static HTML** | **report-only** | W-HAIF |
| 12 | SP.Lab physics/chemistry/bioenergetics | `UNI.Minecraft/lib/sp/lab/` + `lab.ex` | 733 (+77) | 26 blocks, 5 files | **none served** | **report-only †W23** | W-PLANET |
| 13 | Chip-side discrete active inference | `UNI.Minecraft/lib/sp/brain/` | 46 files, 9420 | 1047 blocks | **none** | **report-only †W28** | W-COLONY |
| 14 | Digital DNA / genome / metabolism | `brain/genome.ex`, `genome.ex`, `metabolism.ex`, `homeostat.ex` | 745+228+120+159 | yes | **none** | **report-only †W26** | W-GENOME |

**What the offline column means, exactly.** *Can the operator, with no network and no server, get
this mathematics recomputed in front of him?*

- **yes** — it executes in the browser. JavaScript, no Python, no chip, no network.
- **report-only** — he can read a frozen number **with its provenance printed beside it**, and
  nothing computes. He is looking at a number someone else computed, on a machine that is not this
  one, at a time that is not now. **The wing must say so in those words.**
- **no** — neither. There is not even a report to read.

**†W__** — report-only **today**, becomes **yes** when the named workstream lands a gated JS mirror.
It is deliberately not written as "yes" in advance: nothing in rows 12–14 runs offline right now, and
the column states today's truth.

**‡** — one named exception inside row 7, and it must be badged differently from the rest of the
wing. **The 13-site lattice IS re-derivable offline**: 2¹³ = 8192 configurations enumerate in
JavaScript in milliseconds. That sub-panel is genuinely **yes**. Giving it the same badge as the
Python-generated verdicts around it would be the exact laundering this plan exists to prevent — and
so would giving the panels around it *its* badge.

**※** — 2 of the 4 oracles are Node and would port (`independent-science-check.mjs` 53 lines,
`independent-cross-study-check.mjs` 175); 2 are Python and would not. **But porting the first one
today would port a defect**: `independent-science-check.mjs:41` is an assertion true for every finite
double, and `:48`/`:52` emit the headline verdict as hardcoded string literals. It is rendered as a
**finding** until W1 corrects it, never as an oracle.

**And one row is `no`.** `cross-study:verify-raw` — the raw-source byte chain — is
`BLOCKED_EXTERNAL` because the 4.09 GB archive is absent. There is no computation **and no report**.
That is what `no` is for, and it is the only value in the inventory that means *"he cannot see this
at all, on a plane or off one."*

**Three corrections folded into the table above**, all measured: `tests/semantic/` is **11 files,
3,853 lines** (the earlier 10 / 3,653 came from a glob that missed two files lacking the
`.semantic.` infix); `motor_stack_aif/` is **20 files, 3,071 lines**, not "~3400"; and `npm test`
names **17** `.mjs` files, not 16.

Plus the world model — **1,569 lines, and only one of its four files is under `world/`**, measured
this session: `lib/sp/world/dynamics.ex` 337, `lib/sp/sim.ex` 558, `lib/sp/body.ex` 430,
`lib/sp/eval.ex` 244 — the
seven baseline adversaries, `lib/sp/determinism.ex` (113, SplitMix64, pure), the NumPy oracle
`uni/brain/active_inference.py` (280 + a 137-line test), the control plane
(**`lib/sp/control_plane/` = 17 `.ex` files / 3,439 lines** — 16 at the top level plus
`command/writ.ex` (26); the sibling `lib/sp/control_plane.ex` (44) sits **outside** the directory and
is counted only if the scope is "the SP.ControlPlane namespace" rather than "the directory"), the
resonance lattice (437 + 257), and the gate system itself.

---

## 5.1 W-FLAG — THE FLAGELLUM BENCH

**What it computes.** `uni-motor.js` is the only closed world-observation-inference-action loop in
any tree that runs in a browser with no server: an MWC receptor free energy and activity sigmoid
(`:158-165`), methylation adaptation (`:166`), CheY-P relaxation (`:172`), stator remodelling with
asymmetric time constants (`:175-182`), torque-speed (`:184-188`), Hill-6 CW bias with a
load-dependent Kd (`:190-192`); then column-stochastic B matrices for RUN and TUMBLE (`:254-263`),
a Gaussian likelihood over three gradient states (`:283-285`), exact categorical Bayes with `F[q]`,
KL and surprise (`:268-280`), and EFE with `Q(pi) = softmax(-4 G)` (`:309-330`).

`observed-experiment.js` adds Lanczos `logGamma` (`:32`), golden-section minimisation (`:52`),
mean-one Weibull / lognormal / two-timescale mixture (`:78-103`), a three-stage fit (coarse 50x81
grid, pattern search with halving steps, convergence at 1e-7) (`:105-158`), Abramowitz-Stegun `erf`
(`:168-174`), bisection inverse CDF (`:191-202`), the slow-component posterior `q(slow | T>y)`
(`:204-208`), a KS-uniform statistic (`:258`), and motor-clustered bootstrap intervals (`:210-222`).

`source-first-passage.js` is 77 lines and every function is a closed form worth a chalkboard:
`sourceCoefficients` (`:3`, a binomial convolution over c1,c2,c3, with a `codeN0Branch` flag that
**preserves a source-vs-code discrepancy rather than hiding it**), `r_j = k+(N) + N.sigma- +
j.(sigma+ - sigma-)` (`:38`), `S_N(t) = sum a_j e^(-r_j t)` (`:45`), competing densities (`:51-55`),
the censoring contract (`:59-65` — an uncensored event with no direction **throws**), and moments
(`:67-77`).

**Views.** (1) *The loop, stepping* — mount the kernel verbatim, sliders for base ligand / gradient
/ load / PMF, prior-likelihood-posterior as bars, four EFE columns as a table. **"Stepping" was a
title with no control behind it; §4.10 THE STEPPER is the control, and it is where this view's
single-step behaviour is specified.** (2) *Equation
library* — the eleven-model catalog. (3) *Dwell calculator* — needs item 4. (4) *DLT calculator* —
live, with the coefficient-sum check printed. (5) **The adverse wall** — lognormal `-3.01289`
beside mixture `-3.04976`, all three contrasts with their intervals drawn, and **the two that cross
zero drawn crossing zero**. (6) *Gate ledger* — 14 G-gates and 16 X-gates with criterion and
limitation, **exact-match status classes, never substring**.

**Derivations that get a chalkboard.** The MWC receptor free energy to the activity sigmoid; the
mean-one constraint `lambda_slow = (1-w)/(1 - w/lambda_fast)` and *why* mean-one; the Jacobian
`log f_seconds = log f_normalized - log mu_N`; `S_N(t)` from the binomial convolution; the censoring
contract; and `F[q] = KL + surprise` **with the KL identically zero here and why that is not a
virtue**.

**Worksheets.** The twelve at `scientific-math-workbench.tsx:390-401`, moved verbatim, plus the 13
`paper:` pencil-and-paper exercises already authored in `lib/walkthrough.js` — one per walkthrough
step, already worksheet-shaped.

**Bench run.** `npm test` (**17 named files across two `node --test` invocations**) -> `npm run
experiment:run` -> `experiment:verify` ->
`science:run` -> `science:verify` -> `cross-study:run` -> `cross-study:verify`.
**Acceptance:** the run emits a receipt naming every gate id and status; the frozen report hashes
are unchanged; the independent oracles agree within their declared tolerances.

**Tri-mode.** OFFLINE is native and already 99% built. ONLINE re-runs the Python engines through
the lab server's guarded POST. COMPARE diffs browser-computed values against report values **and**
against the independent oracles.

### The numbers this wing must render, and never soften

Frozen in `experiments/results/observed-experiment-report.json`:
cohort 129 source motors / 1349 source events; 80 train motors / 793 train events; 19 holdout
motors / 233 holdout events; eligible states 1-8; exclusions leftTruncated 129, rightCensored 109,
outOfRange 3. Fitted on training only: Weibull shape 0.62509 scale 0.69960; lognormal sigma 1.57831
mu -1.24553; mixture w 0.60664, lambda_fast 5.23987, lambda_slow 0.44486. `runId
faa689defbf804948312388b3d26fe5f10b6d938780ca2e31f1fb48514486f6a`, protocol
`UNI-FLAGELLUM-OBS-001`, seed 20260717, 2000 replicates.

**The adverse result, live in the frozen report — held-out mean log score, nats per event:**

| model | score | contrast | 95% interval |
|---|---|---|---|
| lognormal | **-3.01289** | — | — |
| mixture | -3.04976 | mixture vs lognormal `-0.03687` | `[-0.06803, +0.01482]` **crosses zero** |
| weibull | -3.09628 | mixture vs weibull `+0.04653` | `[-0.01797, +0.08496]` **crosses zero** |
| exponential | -3.25994 | mixture vs exponential `+0.21018` | `[0.06918, 0.32472]` excludes zero |

**Only one of the three contrasts excludes zero.** Any wing that renders these must draw the
intervals, not the point estimates.

DLT fitted mechanism, from `science-gates-report.json .fittedMechanism`: `k+(N)` for N=1..8 =
0.14632 / 0.21639 / 0.11959 / 0.13432 / 0.07628 / 0.03367 / 0.02193 / 0.01265 s^-1;
sigma+ 0.117381 s^-1; sigma- 0.00053834 s^-1; c1 0.462399; c2 0.00042127; c3 1.0723e-6.

---

## 5.2 W-PARITY — CROSS-STUDY, SCIENCE GATES, ORACLES AND THE SEMANTIC SUITE

**Five separate physics bodies live inside one 495-line Python file**,
`scripts/run-cross-study-parity.py`:

| body | functions | what it does |
|---|---|---|
| rotation-gated assembly | `weighted_fit:45`, `rotation_gate:50` (AIC at `:74`) | `b(w) = b0 + a+ max(w,0) + a- max(-w,0)` with an AIC comparison |
| torque-conditioned switching | `torque_response:110`, `mean_difference_test:90` | |
| **exact finite lattice** | `lattice_features:127`, `lattice_distribution:137`, `lattice_gate:145`, `occupancy_moments:172` | a periodic **13-site** ring enumerated over all **2^13 = 8192** configurations, `P(phi|J,mu) ~ exp[J sum phi_i phi_i+1 + mu sum phi_i]`. **This gate FAILS (X06)** because different summaries imply incompatible J |
| non-equilibrium GMC | `gmc_generator:218`, `gmc_reproduction:259`, `switching_direction:288`, `gmc_switching:307` | a rate generator over 175 coarse states with `Q_ij >= 0 (i != j)`, `sum_i Q_ij = 0`, `Q pi = 0` |
| RFT whole-cell propulsion | `propulsion_gate:325` | RMSE against a constant-mean baseline |

**Frozen verdicts.** `cross-study-parity-report.json` holds 16 gates X01-X16: **8 PASS, 3 FAIL**
(X06 finite-lattice, X11 structural, X16 full biological parity), **2 NOT_ESTABLISHED** (X10
parameter transfer, X12 AIF causal identity), **3 BLOCKED_EXTERNAL** (X13 live signal, X14 wet-lab
replication, X15 printed model). `summary.overall = "PARTIAL_PARITY_ONLY"`;
`fullBiologicalParityAchieved = false`; attributed studies 11; direct independent motor/cell lower
bound 409. `science-gates-report.json` holds 14 gates: **4 PASS** — `G00_SOURCE_IDENTITY`,
`G01_OBSERVATION_BOUNDARY`, `G02_FIRST_PASSAGE_MATH`, `G04_CENSORED_JOINT_LIKELIHOOD` — 3 FAIL
(`G03_PUBLIC_ARTIFACT_PARITY`, `G05_SYNTHETIC_RECOVERY`, `G06_HELDOUT_MECHANISTIC_PREDICTION`),
1 SOURCE_ONLY (`G07`), 1 NOT_ESTABLISHED (`G10`), and **5 BLOCKED_EXTERNAL** (`G08`, `G09`, `G11`,
`G12`, `G13`). **The file states this about itself:** `summary.statusCounts` carries the same tally
and `summary.computationalGatesPassed: 4` of `computationalGatesEvaluated: 7`, alongside
`overall: "PARTIAL_PARITY_ONLY"` and `proofClaim: "No universal, causal, or biological
Active-Inference identity was proved."` **An earlier draft of this plan reported 6 PASS and was
contradicted by the artifact it cited.**

**Views.** The 16+14 gate verdicts as they already render, **plus** the lattice actually drawn (13
sites, the enumerated distribution, and the incompatible-J finding made visible rather than reduced
to the word FAIL); the GMC generator's stationary condition checked on screen; the RFT residuals
against the baseline; and a **falsifier column** — every gate's criterion beside its limitation.

**Derivations.** Why 2^13 is enumerable and 2^26 is not. Why a fitted J is **not** resolved
molecular geometry — the report's own limitation string, verbatim. Why the AIC comparison in
`rotation_gate` is a model comparison and not evidence of mechanism.

**Worksheets.** (1) enumerate a 5-site ring by hand and compute Z; (2) verify `sum_i Q_ij = 0` for
a 3-state generator; (3) compute RMSE against a constant-mean baseline and say what "better than
constant" licenses; (4) read X06's two summaries and write down the J each implies.

**Bench run.** `npm run cross-study:run` then `cross-study:verify`; `science:run` then
`science:verify`; and the four independent oracles.
**Measured today: `science:verify` PASS (244 holdout intervals, mean log score
-3.8380834245644038); `cross-study:verify` PASS (`failures: []`, ito LOBO RMSE 0.8293641328245378,
lattice fitted SSE 0.04976772774792293, RFT RMSE 1.7274106879853608, 10 audit artifacts).**

### The two defects this wing must render rather than inherit

**E-B01 — a required gate reports PASS with zero evidence on disk.** `X01_SOURCE_INTEGRITY` reads
`status: "PASS"` while all 12 declared local artifacts are **present-on-disk 0** and all carry
`verified: true`. The criterion begins *"Every cached artifact matches its frozen SHA-256 and byte
size."* The guard at `tests/cross-study-parity.test.mjs:37` asserts the *claim*
(`assert.equal(artifact.verified, true)`) and `:45` short-circuits on `checkedArtifacts === 0` —
**the block is vacuous exactly when the evidence is gone.** `experiments/upstream-cache/` does not
exist. Direct violation of the never-report-a-pass clause.

**Section 4.5 of the audit — a required verification gate's headline verdict is a string literal.**
`scripts/independent-science-check.mjs:41` is
`assert.ok(Math.abs(moment.fractionPlus + (1 - moment.fractionPlus) - 1) < 1e-14)` — **true for
every finite double**. `:48` emits `status: "PASS"` and `:52` emits
`publicArtifactMismatchDetected: true` as **hardcoded literals inside the `console.log`.**
`science:verify` is a required gate.

**Both must be rendered on the wall as findings before either is fixed**, because a fixed defect
with no record is a defect that can come back.

### The semantic suite — mathematics about mathematics, with no face

`tests/semantic/`, **11 files, 3,853 lines, 174,486 B** — identical in MAIN and STALE. **Two of the
eleven drop the `.semantic.` infix** (`orientation-direction-and-score-sign.test.mjs` 562,
`prospectivity-provenance.test.mjs` 904), so **any glob on `*.semantic.test.mjs` silently loses
1,466 lines of coverage** — which is why this was measured as 10 files / 3,653 lines twice.
The eleven: prospectivity by commit graph (904),
orientation/direction/score-sign (562), train-holdout leakage (455), censoring exclusion (367),
D1 correction integrity (338), periodic-lattice topology (253), the world/agent/observation boundary
(242), density scale and dispersion (231), first-passage invariants (204), adverse-record
preservation (186), survival-posterior conditioning (111).

**Every one of these is a teachable invariant and not one is visible outside a terminal.** They are
the natural first content for the `@teaches` classroom: each already knows what it asks, and each
already knows what would falsify it.

### Tri-mode — and this wing does not get all three

**OFFLINE = `NOT_RUNNABLE_OFFLINE`, for the verdicts.** Every gate in this wing is produced by
Python. `package.json` says so in its own words: `science:run` is `python
scripts/run-science-gates.py` (624 lines) and `cross-study:run` is `python
scripts/run-cross-study-parity.py` (495). **Python does not run in a browser without a runtime the
product contract forbids**, and this plan will not smuggle one in. So OFFLINE here means the wing
renders the two frozen reports — `experiments/results/science-gates-report.json` (22,835 B, sha256
`d7a35acab4cfb2b4…`, runId `1361fae7…`, generatedAt `2026-07-17T23:00:00Z`) and
`experiments/results/cross-study-parity-report.json` (31,084 B, sha256 `bd3838c40b8d2563…`, runId
`454bfc6c…`) — with those provenance strings **printed on the face**, above a banner that says, in
the operator's own words: **NO COMPUTATION HAPPENED IN THIS BROWSER. You are reading a number
someone else computed, on a machine that is not this one, at a time that is not now.**

**With one exception, named and badged differently.** The 13-site lattice **is** re-derivable
offline: 2¹³ = 8192 configurations enumerate in JavaScript in milliseconds, so the wing computes `Z`
and the occupancy moments live and checks them against the frozen `lattice_distribution`. **That
panel carries the OFFLINE badge; every other panel in the wing carries NOT_RUNNABLE_OFFLINE, and the
gate fails if any panel carries the wrong one.**

**And two of the four oracles are JavaScript** — `independent-science-check.mjs` (53 lines) and
`independent-cross-study-check.mjs` (175) — so they *would* port. **They must not port yet.**
`independent-science-check.mjs:41` is an assertion true for every finite double and `:48`/`:52` emit
the headline verdict as hardcoded string literals. **Porting it offline would port the defect and
give it a face.** Until W1 corrects it, this wing renders it **as a finding, not as an oracle.**

**ONLINE — the guarded re-run.** Through `POST /api/lab/run`, the lab server's single carve-out
(`lab_server.cjs:107`, `POST_ALLOWED = new Set(["/api/lab/run"])`, refusal text at `:113-117`,
single-flight `runInFlight` at `:85`). **The wing does not get a second one.** It runs the registered
gate in a throwaway worktree at HEAD, one at a time, and **if Python is absent the run REFUSES with a
named reason** rather than falling back to the frozen numbers and pretending it ran.

**COMPARE — the frozen report against a fresh run, and this is the most valuable of the three.**
What it detects is **the report drifting from the code**: the file on disk saying one thing while the
program that produced it now says another. **That is not hypothetical here.** `mix sp.lab.validate`'s
committed capture at `UNI.Minecraft/lab/evidence/captures/lab_validate_report.txt` **disagrees with
`lib/sp/lab/validate.ex:160` today**, at exactly one of 24 labels, and nothing in either tree detects
it. COMPARE is the instrument that would have. A divergence is written as a **finding** to
`evidence/bench_runs.ndjson` (W4) with both runIds, and **is never resolved by preferring the fresh
number.** Naming it: **`REPORT_CODE_DRIFT`** — a distinct class from a numerical disagreement,
because its cause is a stale artifact rather than a wrong equation, and the repair is different.

---

## 5.3 W-HAIF — THE HIERARCHICAL ACTIVE-INFERENCE BENCH

**64 Python files, 67 markdown files, one JSONL, and exactly one static HTML page.** *(Full census:
also 17 `.sha256`, 16 `.pyc`, 13 `.json`, 12 `.txt`, 12 `.log`, 2 `.sh`, 2 `.gitignore`, 1 `TAG`.)*
The program is
documentation-dominant, and its gate state is prose.

`src/motor_stack_aif/`, 20 files: `compare.py` 747 (the B3/B4 harness), `d5_distribution_guard.py`
427, `numeric_provenance_guard.py` 340, `frozen_evidence_guard.py` 196, `claim_guard.py` 184,
`marks.py` 133, `hierarchy.py` 118, `events.py` 111, `score.py` 107, `hazard_survival.py` 100,
`bootstrap.py` 96, `baselines.py` 88, `free_energy.py` 66, `status.py` 65, `_bridge.py` 65,
`corrected_reasons.py` 63, `fit.py` 62, `resource.py` 59, `seeding.py` 44.
Tests: 32 files, 5329 lines, **339 `def test_` functions**.

**`hierarchy.py` is the most disciplined small model in the three trees.** Lmotor-5 population prior
(mu, tau) / Lmotor-4 per-motor latent integrated out by Gauss-Hermite / Lmotor-3 occupancy
normalisation / **Lmotor-2 NOT INSTANTIATED, with the reason in the docstring** / Lmotor-1 mean-one
Weibull. **TOTAL FREE PARAMETERS = 2.** Resolution floor cited as ~0.042 nats at 793 train events /
80 train motors / 19 holdout motors.

**`free_energy.py` carries its own fence in code.** `F = complexity - accuracy`, `gaussian_kl`,
`decompose()` keeping both terms named and unit-declared, and `surprise_from_exact_posterior()` —
which **records that the shipped runtime computes surprise and labels it F, with a KL term
identically zero.** Its docstring states there is deliberately **no** expected-free-energy function:
*"G requires policies over actions; this dataset has none. G-side is
DESIGN_ONLY_UNTIL_INTERVENTION_OR_TRANSFER, and the absence of the function is the fence."*

**That absence is itself a lab exhibit.** It is exactly the confusion the operator must be able to
see: two things called F, one of which has no KL.

**Views.** The Lmotor-5 to Lmotor-0 stack with **Lmotor-2 drawn as an empty slot with its reason
printed**; the two free parameters with the Gauss-Hermite nodes visible; the resolution floor
(~0.042 nats) drawn as a line every contrast is measured against; the nine frozen B3 competitors
M0-M8 (exponential, Weibull, lognormal, two-timescale, K3 mixture, gamma, semi-Markov
state-dependent, hierarchical-motor, empirical KDE) with their free-parameter counts; `H-AIF-G1` …
`H-AIF-G9` with
status and receipt path; **the D5 firewall drawn as a boundary with the burned holdout mark channel
greyed and labelled BURNED**; and the four measured defects — C11 cluster collapse (80 motors ->
46 groups, 42.5% cluster loss), the 17-29x resource overstatement, the PYTHONHASHSEED
nondeterminism, and the D6 impossible marks.

**Derivations.** `F = complexity - accuracy`. Why `surprise_from_exact_posterior` is a valid readout
and **not** evidence of minimisation. Why 2 free parameters and not 80. Why `hazard_survival.py` has
**no floor** — a non-finite log density HALTS rather than being clamped.

**Worksheets.** (1) compute the mean-one Weibull scale for three shapes; (2) the censored vs
uncensored log-density for one event; (3) count the free parameters of M0-M8 and **rank them before
seeing the scores**; (4) mark each P-level PASS / FAIL / NOT_ESTABLISHED / BLOCKED_EXTERNAL /
NOT_RUN and name the first unsatisfied one.

**Bench run.** `pytest hierarchical-aif/tests/` (339 tests) plus the frozen-evidence hash comparison
against `reports/frozen-evidence-baseline.sha256` (250 files). **Acceptance:** 0 frozen diffs,
claim clamp clean.

**BLOCKER, and it precedes any H-AIF view:** gates **`H-AIF-G1` … `H-AIF-G9` exist only as a markdown
table** at `hierarchical-aif/docs/H-AIF-GATES.md:9-17` — **those are the real ids; no gate in that
table is *identified* by the `G1..G9` short form, though the short form does occur in prose
elsewhere (§5.9)** — (G1 ESTABLISHED, G2 ISSUED, G3 COMPLETE, G4 COMPLETE, G5 IN PROGRESS,
G6 AUDIT COMPLETE/NOT YET SCORED, G7 NOT RUN, G8 NOT_LOCATED/NOT_ESTABLISHED, G9 ONGOING). The only
machine-readable trace is `reports/FLOW-JOURNAL.jsonl` (37 rows), which is a narrative journal, not
a gate-state file. **A parser over prose is a drift generator.** Create
`hierarchical-aif/ledgers/h-aif-gates.json` — **verified absent today; `hierarchical-aif/ledgers/`
exists and holds four `.md` files** (`DEFECT-CLOSURE-LEDGER`, `DEFECT-LEDGER`,
`GATE-TO-EXISTING-P-LADDER-MAP`, `NEGATIVES-AND-PARTIALS`), so this is a new file in a real
directory — with one record per gate keyed **`H-AIF-G1` … `H-AIF-G9`**, the ids actually used at
`hierarchical-aif/docs/H-AIF-GATES.md:9-17` (**not** the `G1..G9` short form, which is nowhere an
id), carrying `{id, title, maps_to_p_levels, status, receipt_paths, falsifier}`, plus a test asserting the
JSON and the markdown table agree — **the test fails if either drifts.**

### Tri-mode — and this wing gets the least of the three

**OFFLINE = `NOT_RUNNABLE_OFFLINE`, with no exception.** 20 Python modules, 3,071 lines in
`src/motor_stack_aif/`; 32 test files, 5,329 lines, 339 `def test_` functions. **None of it is
JavaScript and none of it should be mirrored.** `compare.py` alone is 747 lines, and mirroring a
B3/B4 scoring harness would create a second implementation of the scoring — **which is the one thing
a parity program must never have.** So OFFLINE here is: the wing renders `h-aif-gates.json` (the file
W30 creates), its nine records, the frozen-evidence baseline `reports/frozen-evidence-baseline.sha256`
(250 lines), and the four measured defects, and it states on its face: **NO PYTHON RAN. THIS IS A
RECORD OF A RUN, NOT A RUN.**

**The stack, the two free parameters, the ~0.042-nat resolution floor and the M0–M8 parameter counts
are drawn offline, because drawing is not computing** — and the wing says which is which, panel by
panel. **A diagram of a hierarchy is not the hierarchy.** That distinction is exactly what this wing
exists to teach, so it had better hold on the wing's own surface first.

**ONLINE — `pytest hierarchical-aif/tests/` (339 tests) through the same single guarded POST**, plus
recomputation of the 250-line frozen-evidence hash set. Acceptance is 0 frozen diffs — **and a
non-zero diff is not a failure of the run, it is a finding about the tree.** The wing must render it
that way, because the five `frozen-evidence-recheck-*.sha256` files sitting beside the baseline (each
byte-identical in size at 46,894) are a history of exactly this question being asked repeatedly.

**COMPARE — two comparisons, and the second one is the point.** First, the frozen `.sha256` baseline
against a fresh recomputation. Second, **`h-aif-gates.json` against the markdown table at
`hierarchical-aif/docs/H-AIF-GATES.md:9-17`** — which is the drift detector this program has never had. Today that
markdown table is the *only* gate state that exists. **So the JSON is authored once, by hand, and
from then on the two are held to each other and either one moving alone turns the test red.**

---

## 5.4 W-PLANET — THE PLANETARY BENCH (SP.Lab)

**733 lines of tested, unit-documented, zero-dependency Elixir with equations in the docstrings —
and no served UI anywhere.**

| module | lines | computes | constants |
|---|---|---|---|
| `physics.ex` | 75 | `g = GM/R^2` (`:39`), `g = GM/R^2` from GM (`:46`), `v_esc = sqrt(2GM/R)` (`:55`), the rival `g = k.P` (`:62`), `calibrate_k = g_ref/p_ref` (`:70`), `rel_error` (`:74`) | `G = 6.674e-11` (`:26`) |
| `planetary_data.ex` | 67 | 7 bodies with mass / radius / measured g / surface pressure (`:32-42`) | earth 5.972e24 kg, 6371 km, 9.82, 1.014 bar; moon 7.35e22, 1737, 1.62, 3.0e-15; mars 6.42e23, 3390, 3.73, 6.36e-3; venus 4.87e24, 6052, 8.87, 92.0; mercury 3.30e23, 2440, 3.70, 5.0e-15; jupiter 1.90e27, 69911, 25.92, **nil (no surface)**; titan 1.3452e23, 2574.76, 1.354, 1.467 |
| `radiation.ex` | 74 | `tau = sigma N` (`:52`), `T = e^-tau` (`:56`), shield `1 - e^-tau` (`:67`), `ozone_optical_depth_du` (`:73`) | `1 DU = 2.69e16` (`:28`), `sigma_O3 = 1.1e-17 cm^2` at ~255 nm (`:35`) |
| `bioenergetics.ex` | 121 | `nernst_slope_mv` using **ln(10) exactly, not 2.303** (`:63`); `Delta p = Delta psi - slope . Delta pH`, T default 298.15 (`:75`); `Delta G = n F Delta p` (`:87`); a 6-clause `cell_status/1` (`:95`) supporting `:aerobic` (needs `:o2`) and `:anaerobic` (`:sulfate`/`:nitrate`) **so oxygen-necessity cannot be smuggled in** | `F = 96485.0`, `R = 8.314` (`:29-30`); thresholds water_min 0.6, pmf_min 50.0 mV, radiation_max 1.0 (`:33-35`) |
| `solar_energy.ex` | 67 | `P_net = eta G A - eps sigma A (T^4 - Tenv^4) - h A (T - Tenv)` (`:56-65`) | `sigma = 5.670e-8`, `G_solar = 1361.0` (`:26-28`) |
| `model_compare.ex` | 104 | `S = 1.0 E - 0.5 C - 1.5 F - 1.0 U` with fixed public weights (`:28`); newton_card vs pressure_card (`:88-91`); default tolerance 0.02 | |
| `validate.ex` | 225 | **24 named cross-checks** (`:98-201`, inside the list literal `:97-206`) re-deriving every ledger/proof/dossier number from the code. **Not 23** — a naive `grep -c 'chk('` returns 25 because it counts the `defp chk/3` definition at `:217`; the harness itself prints `24 checks, 0 failed.` | |

`mix sp.lab.validate [--out PATH]` (`lib/mix/tasks/sp.lab.validate.ex`, 33 lines) exists, works,
and `Mix.raise()`s on any failed check. **This is already a bench run. It has a text face and no
visual one.**

**Views.** (1) *The seven bodies* — the table with Newtonian error and pressure-model error
**computed live, not typed**. (2) **Calibrate-on-Earth-then-fail** — one slider (which body you
calibrate on) and the failure count moves. *This is the single most teachable object in the three
trees.* (3) *Beer-Lambert* — a DU slider 0 to 600, tau and transmittance drawn, with the "zero
ozone -> T=1, shield=0" baseline as a fixed reference. (4) *Chemiosmosis* — Delta psi and Delta pH
sliders to Delta p to Delta G, and the six-clause viability rule **as six lamps**, with the
aerobic/anaerobic switch beside them so the operator can watch oxygen stop being necessary.
(5) *Solar balance* — a T slider, three terms stacked, and an `h -> 0` toggle that removes exactly
one bar and **cannot remove the T^4 one**. (6) *The cross-checks* with PASS/FAIL and detail — the
row count read from the loaded report, never typed (today it is 24).
(7) *Ledgers and proofs* — `formula_ledger.json` (21 records, LaTeX already written),
`claim_ledger.json` (18 records with `verify_with` and `falsify_with` side by side),
`source_ledger.json` (38), `parameter_ledger.json` (47), `falsification_ledger.json` (7),
`adversarial_reviews.json` (7), and the 8 proof documents.

**Derivations.** The dimensional check of `GM/R^2` to metres per second squared (already written in
`formula_ledger.json[0].limitations`); why pressure spans ~16.5 orders of magnitude while g spans a
factor of ~19; `tau = sigma N` and the Dobson conversion; the Nernst slope from `RT ln10 / F`; why a
vacuum removes the convective term and **cannot touch** the radiative one.

**Worksheets.** (1) compute g for all seven bodies by hand; (2) calibrate k on Earth and predict
Titan and Venus; (3) tau at 100 / 300 / 500 DU; (4) Delta p and Delta G for three parameter pairs;
(5) the collector balance at three temperatures with and without convection; (6) assign an evidence
class to each of the 18 claim-ledger rows and defend it.

**Bench run.** `mix sp.lab.validate --out lab/evidence/captures/lab_validate_report.txt` plus
`mix test test/sp/lab/ --seed 0`. **Acceptance — and the count must be COMPUTED, never a literal.**
The old criterion read *"23 of 23 checks PASS"* and **would have failed on a correct run**, because
there are 24. The replacement is W24's criterion in §7.3: the wing renders the check table by
iterating the report it loaded and prints `N checks, M failed` where `N` is the array length at
render time; any wing source containing `23` or `24` as a check-count literal fails the gate; and
the gate re-emits the report and byte-compares it to
`lab/evidence/captures/lab_validate_report.txt` — **which is RED on the current tree**, at exactly
one of 24 labels (source `validate.ex:160` reads `Nernst slope @298 K == 59.16 mV/pH (canonical,
dossier)`; capture index 13 reads `~=` and omits `canonical`). **A transcribed number that has
already drifted, sitting in the evidence directory, in the wing this plan builds first.**

**Tri-mode.** OFFLINE — a small JS mirror of the seven modules' pure functions at
**`lib/kernel/mirrors/splab.js`** (re-pathed by §0.5; the earlier `viewer/lab/wings/splab/kernel.js`
is **withdrawn**), **and the mirror is a gate**: it must reproduce the Elixir to a declared tolerance
or the wing refuses to render. **It refuses — it does not render stale numbers with a warning.**
ONLINE — a new `mix sp.lab.report` task emitting the same numbers as JSON, reached through the single
guarded `POST /api/lab/run`. COMPARE — the two side by side; **this is where a mirror drift becomes a
finding rather than a silent lie.** The mirror is its own workstream (**W23 MIRROR-SPLAB**), not a
line item inside the wing, because a mirror is a cross-engine parity problem and burying one inside a
wing is how a wing quietly becomes a multi-day numerical investigation.

**Two absences that must be closed in this wing's first change:**

- **`SP.Lab.Validate` has no test file**, and neither does `SP.Lab.PlanetaryData`. `test/sp/lab/`
  contains exactly five files: bioenergetics, model_compare, physics, radiation, solar_energy. The
  225-line harness whose entire purpose is to catch drift between code and ledgers **is itself
  unguarded**, and the 7-body reference table has nothing pinning its values to their cited sources.
- **`lab/ui/index.html` has SP.Lab's numbers typed in as literals** (Earth 0.03%, Moon 0.36%, Venus
  ~9,900%, Titan ~950%, tau ~= 89) and nothing checks them. Its own README calls it *"SPEC + STATIC
  VIEWER STUB (not a finished interface)"*. **Delete-or-drive:** either regenerate it from the JSON
  or remove it. Leaving it beside a live wing gives the repository a second stale surface. Its
  evidence-class pill styling (`.A/.B/.C/.D/.U/.X`) is already designed and should be reused.

---

## 5.5 W-COLONY — THE CHIP-SIDE ACTIVE-INFERENCE BENCH

**9420 lines across 46 files, pure-list categorical algebra, no Nx and no NIF — and the load-bearing
part is about 330 lines.**

| module | lines | computes |
|---|---|---|
| `brain/math.ex` | 107 | eps 1.0e-16, `softmax`, `entropy`, `col_entropies`, `matvec` (column-major), **`ln_matvec` — the `(ln B)s` convention, NOT `ln(B s)`, flagged bound-critical**, `row_log`, `digamma` via upward recurrence plus a Bernoulli series matching scipy to ~1e-9 |
| `brain/infer.ex` | 99 | `q(s) = softmax(forward_prior + sum_m gamma_m ln A[o_m,s])` with a delta-weighted contextual prior (`:26-41`); `vfe/2` at `:55-62`; **soft / virtual evidence** at `:93-98`, equal to the hard form at the one-hot limit |
| `brain/efe.ex` | 122 | `G(pi)` with epistemic `H(qo) - E_q[H(o|s)]` and pragmatic `qo . C`; `Q(pi) = softmax(ln E - gamma G - F_pi)`; a **gated** novelty term riding the epistemic channel (`:87-101`), zero by default so saved models stay byte-identical |
| `brain/novelty.ex` | 72 | the pymdp/SPM pA-novelty, explicitly **not** the digamma form, with a declared monotone decay to zero as counts grow — the no-smuggled-reward invariant |
| `brain/learn.ex` | 72 | Dirichlet accumulation of A and B; the moduledoc states **"there is NO reward"** |
| `brain/hierarchy2.ex` | 73 | DOWN is a prior, UP is evidence; tied to gate `gate.hierarchy2.composition` |
| `brain/precision.ex` | 104 | attention as precision optimisation |
| others | ~8800 | `factors.ex` 203, `model.ex` 129, `action_heads.ex` 110, `motor_control.ex` 104, `curriculum.ex` 177, `emotion.ex` 118, `awareness.ex` 88, `viability.ex` 34 |

**Supporting bodies.** `SP.Determinism` (113 lines, a pure splittable SplitMix64 in integer maths,
deliberately **not** `:rand`, threaded explicitly so the world is a pure function of its seed —
Validation Invariant 13). The NumPy oracle `uni/brain/active_inference.py` (280 lines) plus its
137-line test, which `math.ex` is kept **byte-comparable** to precisely to avoid BLAS
reduction-order nondeterminism. The world model — `world/dynamics.ex` 337 (conservative diffusion,
thermal relaxation, a reaction network, stochastic discharge, ecology; all pure), `sim.ex` 558
(hybrid time: microstep / decision tick / development tick), `body.ex` 430 (appendage and sensory
ladders), `eval.ex` 244 (ablation presets), `world/region.ex` 271, `world/actions.ex` 208,
`world/material.ex` 178, `world/law.ex` 114, `world/field.ex` 103. And seven baseline adversaries
(`lens.ex` 95, `leakage_probe.ex` 55, `infrastructure.ex` 49, `morphology_seeking.ex` 45,
`probe_first.ex` 42, `homeostatic.ex` 40, `random.ex` 29) — *"deliberately simple, deliberately kept
alive."* **A lab wing with no adversary is a demo.**

**Views.** A, B, C, D as heatmaps — **labelled column-major, because they are**; one tick unrolled
(forward prior, then likelihood, then posterior, with the vectors printed); `F` decomposed;
`G(pi)` per policy with epistemic and pragmatic split and **the novelty term shown as zero when
gated off**; Dirichlet counts growing with the novelty term decaying beside them; the hierarchy-2
down and up messages as two arrows with the actual matrices; and the seven baselines running beside
the agent.

**Derivations.** **Why `(ln B)s` is not `ln(B.s)`, with a worked 2x2 counterexample the operator can
do by hand** — this is the single most consequential convention in the engine and today it lives in
one docstring. `H(qo) - E_q[H(o|s)]` as expected information gain. `E[ln A] = psi(a) - psi(sum a)`
and why `learn.ex` uses the point update instead.

**Worksheets.** (1) one Bayes tick by hand for a 3-state, 2-modality model; (2) compute `G` for two
policies and **predict the choice before checking**; (3) the novelty term at counts 1 and 100, to
show the decay; (4) the hierarchy-2 up message by hand.

**Bench run.** `mix test test/sp/brain/` plus the NumPy oracle comparison.
**Acceptance: byte-identical policy posteriors between Elixir and NumPy on the oracle path.**

**Tri-mode.** OFFLINE — a JS mirror of `math.ex` (107) plus `infer.ex` (99) plus `efe.ex` (122) =
**exactly 328** of the 9,420 lines, at **`lib/kernel/mirrors/brain.js`** (§0.5); **the small part is
the load-bearing part.** ONLINE — a new `mix sp.brain.trace` task emitting one tick as JSON.
COMPARE — **three** implementations (JS mirror, Elixir, NumPy — `uni/brain/active_inference.py`,
280 lines), and **a divergence between any two is a finding.** The mirror is its own workstream
(**W28 MIRROR-BRAIN**) and must be green before this wing's OFFLINE tab is reachable (§7.2 item 5).

---

## 5.6 W-GENOME — THE DIGITAL DNA BENCH

**Three genome bodies, none rendered.** `SP.Brain.Genome` (745 lines) is a `%DNA{}` with a
**13-organ prerequisite graph** (`:22-38`), 12 scene states (`:42`), a modality table binding organ
to observation modality to hidden factor with sizes, `repair/1` by prerequisite closure plus
topological order, `mutate/2`, `recombine/3`, and expression into a runnable `Factors` model with
**A and B seeded UNINFORMATIVE** — no world knowledge in the genome. `SP.Genome` (228) is the
morphology growth plan with the same repair discipline. `SP.Producer.Genome` is 196.

`SP.Brain.Metabolism` (120) declares every rate as a named module attribute with a `rates/0`
accessor **"declared for the falsification ledger"**: upkeep 0.04, work 0.04, eat_refill 0.5,
satiety_decay 0.02, satiety_refill 0.4; a 4-bin discretisation; six costly actions.
`SP.Brain.Homeostat` (159) adds gut_refill 0.4, gut_empty 0.03, soma_heal 0.02, soma_damage 0.2,
nominal_tick 8.0 s, fatigue_spend 0.06, fatigue_recover 0.03, fatigue_tick 3.0 s, and a 6-bin graded
viability. Its moduledoc already carries the fence: *"energy and satiety are model variables, NEVER
felt states"* (`metabolism.ex:17`).

**Views.** The 13-organ prerequisite DAG drawn; a plan editor where **an invalid plan is
unreachable rather than rejected**, with `repair/1`'s closure and topological sort animated; the
modality table as the actual wiring diagram; metabolism and homeostat stores draining under a chosen
action sequence with every rate shown as the named attribute it is; **and the death condition as an
event, not a number.**

**Derivations.** Prerequisite closure, and why topological order makes every repaired genome
developable. Why a 4-bin discretisation of a continuous store is a modelling choice with
consequences.

**Worksheets.** (1) hand-repair three broken growth plans; (2) run 40 ticks of metabolism by hand
for a given action sequence and find the death tick; (3) for each store, name the *driver* that
drains it and show energy and gut dissociating.

**Bench run.** `mix test test/sp/brain/genome_test.exs test/sp/brain/metabolism_test.exs
test/sp/brain/homeostat_test.exs`. **Tri-mode:** OFFLINE fully — the repair algorithm and the store
dynamics port trivially, at **`lib/kernel/mirrors/genome.js`** (§0.5), **which is why W26 needs no
separate mirror workstream**; ONLINE for a live colony trace; COMPARE on the store trajectories.

---

## 5.7 W-GATE — THE GATE BENCH (mostly exists; three additions)

L3, L4, L5 and L6 already render the real 109 ledger gates on a floor, three distinguished
closed-states (`open` / `sealed_by_rule` / `no_door`, with `no_door` **computed** by scanning for a
minter rather than asserted), a desk that prints the exact gate-row bytes, and a gauntlet that walks
the whole lab in one run.

**Three additions, not a rebuild:**

1. **A coverage map** — 109 ledger names on one axis, 95 foreign identifiers on the other, and the
   empty intersection **drawn as empty**. See section 5.9.
2. **The 32-entry control-plane chain** with each `prev_hash -> hash` link drawn and verifiable in
   place.
3. **The Room as a walkable three-state corridor** with **`conditions/4` (`room.ex:93-96`)** read
   live — the first time that door is drawn. Read-only by construction.
   **There is ONE function, not two:** `@spec conditions(t(), atom(), map(), [Key.t()])` at `:93` and
   `def conditions(room, target, receipts \\ %{}, keys \\ [])` at `:94`; **two default arguments make
   `conditions/2` and `conditions/3` legal call forms of the same body.** `room.ex` contradicts
   itself the same way an earlier draft of this plan did — its own doc says `/2` at `:20` and `/4` at
   `:105`. **That inconsistency is in shipped source and is worth its own one-line fix.**

**Derivations.** What a hash chain proves (tamper-evidence) and what it does **not** (unforgeability,
with `independent_custodians: 0`). Why `theGap()` computes rather than asserts.

**Worksheet.** Author one gate row by hand for a named registered gate, in canonical property order,
and check it against what `desk.cjs` prints. **This worksheet is the operator's S4 path made
teachable.**

**Bench run.** `node viewer/gate_runner.cjs` plus `node viewer/lab/gauntlet.cjs`.
**Acceptance:** registry complete against filesystem discovery, and every registered gate reaching
a real verdict or a named refusal.

**Also surface the resonance lattice** (`viewer/resonance.cjs` 437 + `resonance_meter.cjs` 257):
seven conjunctive layers — L1 ROOT reproduces, L2 FLOW runs, L3 WILL bites, L4 HEART agrees, L5
VOICE matches, L6 SIGHT names the unseen, L7 CROWN licenses the claim — which **names the first
unsatisfied layer rather than averaging.** It is the single best "what does the whole thing actually
read right now" instrument in the repository, it has no UI, and it is in no registry (deliberately:
it recursed when registered as a gate). Surfacing it is nearly free and it is the honest headline
number for the operator's home screen — **which §3A.4 now designs, and §3A.9 constrains: the layer
NAME is surfaced, never a percentage.**

### Tri-mode — and this is the only wing where OFFLINE is unambiguously, fully true

**OFFLINE — yes.** Everything this wing renders is JSON and CommonJS already on disk:
`evidence/gates.ndjson` (206 rows, 109 unique names), `viewer/gate_registry.json` (28 entries), the
control-plane ledger, and `desk.cjs` (679 lines) which already **computes rather than asserts**.
`theGap()` runs in Node with no network, no Python and no chip. **The operator can take the entire
gate system on a plane today** — worth saying out loud, because it is the only body of which that is
currently true without a workstream first.

**ONLINE — `node viewer/gate_runner.cjs` and `node viewer/lab/gauntlet.cjs`** through the guarded
POST. The three `ci:false` entries — `hud`, `overlays`, `colony` — are **listed-not-run** and the
wing renders them as such, never as a fabricated pass. Measured: `canRun('overlays')` and
`canRun('colony')` both return `NEEDS_THE_WORLD`, and `canRun('hud')` returns `SEALED_BY_S10`.
**Three registry entries, two distinct refusals, and the wing prints the refusal it actually got.**

**COMPARE — the ledger as committed against the gates as they run now. This wing's COMPARE has
already found something**, and the finding is in `desk.cjs` itself — see §5.9.

---

## 5.8 NOT_RENDERED — and the reason for each

**Nothing in the repositories is unrepresented. What will not be rendered is listed here with a
reason, because an inventory that quietly omits things is the failure this plan exists to correct.**

> **ADVERSE — that sentence is false on its own page, and it is left standing rather than softened.**
> §5.0's fourteen-row table assigns every body a wing; its **trailing paragraph then names six bodies
> and assigns none of them a wing**: the Minecraft **world model** (`lib/sp/world/dynamics.ex` 337 +
> `lib/sp/sim.ex` 558 + `lib/sp/body.ex` 430 + `lib/sp/eval.ex` 244 = **1,569 lines**, all five sizes
> re-measured this session), the **seven baseline adversaries**, `lib/sp/determinism.ex` (113), the
> NumPy oracle `uni/brain/active_inference.py` (280), the **resonance lattice** (437 + 257), and the
> **control plane** (3,439). **None of the six appears in the twelve-row NOT_RENDERED table below
> either.** So they are in neither list, and the inventory the operator was promised is incomplete by
> exactly six bodies. **This matters beyond bookkeeping: the operator named "the Minecraft" as a thing
> the laboratory must show, and the world model is the Minecraft.** Assigning each of the six either a
> wing or a NOT_RENDERED reason is a scope decision, not a measurement, and it is **§10.4 item, open**
> — it is not silently closed here.

| Body | Size | Reason NOT_RENDERED |
|---|---|---|
| `viewer/command_center.cjs` | 2159 | Fleet operations surface, not science. Already has its own UI. Out of the laboratory's scope. |
| `viewer/studio_stage.cjs` | 581 | Broadcast staging. Not mathematics anyone must believe a scientific claim from. |
| `viewer/gaia/collectors.cjs` + `caps.cjs` + `sig.cjs` | **1380 + 424 + 294** | Already rendered by Gaia at `:8096`. The lab links to it; it does not re-draw it. **Except** the deploy-lag tripwire rule, which the bench-parity gate reuses directly. |
| `viewer/body.js` + `director.js` | 801 + 275 | Producer/broadcast body rendering. Different product. |
| `lab/film/render/*.js` | 8 files, ~1800 | SVG scene generation for the DGST film. It is illustration, not instrument. The DGST **D-value audit proof** IS rendered (W-PLANET); the film is not. |
| `lib/sp/producer/**`, broadcast, DNS, colony-cam, ERP, mail, meet, masterplan | large | Infrastructure. In `infra_registry.json`, out of the laboratory. |
| `runs/*.exs` (52 runners) + 4 `.py` analysers | — | Bench *invocations*, not bench *content*. They become entries in the bench-run registry, not wings. **Except `runs/pureworld_qa_gate.exs`, which is listed in section 6 as a blocker, because it still raises `@scaffold` at `:28` and the road to air runs through it.** |
| `app/chatgpt-auth.ts` | 86 | Dead code, unreachable (audit PRD-11), and it is an LLM auth path in a product whose contract forbids LLM inference. **It should be deleted, not rendered.** |
| `lab/purebody/*.cjs` | ~400 | Purity scanning of the Minecraft body. Real, but its output is a gate verdict already on the L3 floor. |
| `experiments/data/*.json` (20213 + 4638 lines) | — | Data, not mathematics. Rendered as *provenance* (hash, source pin, licence) in the intake wing, never as a table to scroll. |
| `hierarchical-aif/docs/NEXT-CYCLE-PLAN.html` | 551 | A static one-off. Superseded by the H-AIF wing; delete-or-drive, same rule as `lab/ui/index.html`. |
| The 5 SVGs in `docs/control-plane/generated/` | **568,487 B** | **RETRACTION — see §10.0 correction 2. They are not empty and never were**, and this row previously said they were. They hold 568,487 bytes of valid single-line PlantUML output (`structurizr-Bodies.svg` alone is 175,183 B). They report zero lines because they contain **no newline character**, and the draft sized them with a line count. Nothing here needs regenerating or deleting. They are NOT_RENDERED in the laboratory for the ordinary reason: they are architecture diagrams already served by Gaia and the control-plane docs, not mathematics. |

---

## 5.9 THE ZERO-INTERSECTION PROBLEM, STATED PRECISELY

**The banner says "25 registered gates, ZERO rows in the canonical ledger." The count is wrong and
the finding is far worse than stated.**

**Re-measured independently this session. It holds, and it holds more strongly than the first
statement of it.**

Measured:

- **`viewer/gate_registry.json` declares 28 gates** — 25 `ci:true`, 3 `ci:false` (`hud`, `overlays`,
  `colony`) — each with an `id` **and** a distinct `gate_row` pointer: **56 identifiers on the runner
  side, in 28 pairs.**
- **`evidence/gates.ndjson` holds 206 rows and 109 unique `name` values.** Over all rows: PASS 122,
  PENDING 69, PARTIAL 12, FAIL 3. Latest-per-name: **PASS 92, PARTIAL 4, PENDING 12, FAIL 1** —
  reproducing the banner's tally exactly.
- **The ledger is clean.** Validated against `production/schemas/gate_row.schema.json` (required:
  `schema_version`, `name`, `verdict`, `receipt_path`, `evidence_class`, `last_updated`;
  `additionalProperties: false`): **0 rows missing a required key, 0 rows carrying a disallowed key,
  and all 206 `receipt_path` values exist on disk.** The schema's own description states that every
  gate the project claims **MUST** be represented there, keyed to a real receipt.

| left set | size | exact intersection with the 109 ledger names |
|---|---|---|
| registry `.id` | 28 | **0** |
| registry `.gate_row` | 28 | **0** |
| science gates `G00_SOURCE_IDENTITY` … `G13_PHYSICAL_MODEL_VALIDATION` | 14 | **0** |
| cross-study `X01_SOURCE_INTEGRITY` … `X16_FULL_BIOLOGICAL_PARITY` | 16 | **0** |
| H-AIF `H-AIF-G1` … `H-AIF-G9` | 9 | **0** |
| **union of all four foreign id spaces** | **95** | **0** |

**Ninety-five gate identifiers across four independent id spaces. One hundred and nine names in the
canonical ledger. Exact intersection: zero.**

**Correction to how this table used to write the ids.** It previously tabulated `G00..G13`,
`X01..X16` and `G1..G9`. **No gate in either frozen report or in `H-AIF-GATES.md` is *identified* by
a short form.** The real ids carry their titles and were read out of `.gates[].id` in both frozen
reports (`G00_SOURCE_IDENTITY` … , 14 of them; `X01_SOURCE_INTEGRITY` … , 16 of them) and out of the
markdown table at `hierarchical-aif/docs/H-AIF-GATES.md:9-17`, whose ids are prefixed `H-AIF-`. The
intersection was re-measured **with the real id strings** — union 95, intersection 0, unchanged.

> **A correction to the correction, carried because this document has now been convicted three times
> of a false absence claim.** A previous revision wrote here that *"those short forms appear nowhere
> in either tree."* **RETRACTED — they occur, as display labels and in prose.** Measured this
> session: `app/science-gates-panel.tsx:84`, `:90` and `:96` render `G03 · PUBLIC ARTIFACT PARITY ·
> FAIL`, `G05 …`, `G06 …` inside `<span className="gate-id">`;
> `experiments/cross-study-preregistration.v1.json:139` and
> `experiments/results/cross-study-parity-report.json:735` both read *"X01 through X15 all pass
> without SOURCE_ONLY…"*; and on the chip side `lib/sp/brain/genome.ex:687` carries *"Rung-1 RED
> fields (Group G1)"* and `lib/sp/brain/mc.ex:152` carries *"(G5: keep moving)"*. **So a grep for a
> short form tests nothing.** What is true, and what the set operations below actually rest on, is
> that the short forms are never an id: the union and the intersection are computed over the full id
> strings. **The finding survives; the labels do not, and a table that names ids has to name the
> ones that exist.**

**Refinement — the one thing "zero" hides.** Two of the 28 `gate_row` values are **globs**:
`gaia → gaia-*` and `hud → hud-*`. By prefix they cover **34 of the 109 ledger names** (`gaia-*` 6,
`hud-*` 28). The other **26 `gate_row` values are exact strings and match zero ledger names.** So:

- **0 of 95 foreign identifiers is a ledger name.** Exactly as stated.
- **34 of 109 ledger names are nonetheless reachable from the registry — through two globs.**
- **75 of 109 are covered by nothing at all.**

**And this is why `desk.cjs:668-672` is measurably false.** It states that because the intersection
is empty, `canRun`'s `SEALED_BY_S10` branch is *"currently UNREACHABLE for every registered gate."*
**It was executed. `canRun('hud')` returns `allowed: false`, `code: "SEALED_BY_S10"`,
`sealed_by: ["hud-boot-persistent", "hud-integration-stage-0", "hud-renders-stale-as-stale"]`.**

The mechanism, precisely: **the seal fires when a registry entry's `gate_row` matches a ledger row
whose latest verdict is `PENDING`.** `hud-*` matches 28 ledger names — 25 PASS, 3 PENDING — so it
seals. `gaia-*` matches 6, all PASS, so `canRun('gaia')` returns `allowed: true`. The 26 exact
`gate_row` values match nothing, so they can never seal.

**The branch is reachable for exactly ONE of the 28 registered gates and unreachable for the other
twenty-seven** — 26 because their `gate_row` is absent from the ledger, and one (`gaia`) because its
glob's matches are all green. That is sharper and more useful than either the comment or the original
finding, and **it is the sort of thing a prose comment about a computed fact will always eventually
get wrong.** Same defect class as a transcribed check count (§5.4's Nernst label), different file,
same repair: **compute it.** W25 replaces the paragraph with a computed
`sealed_branch_reachable_for` field, which returns `["hud"]` on the current tree.

**And the problem is not integrity. The problem is that the canonical ledger has never been told the
science exists.** Its 109 names are broadcast, HUD, door, colony, producer and Gaia infrastructure
plus roughly sixteen brain RED gates. **Not one of the 109 matches `/lab|physic|ozone|gravit|
bioenerg|solar|radiat/i`. Not one names the flagellum.** `evidence/gate_attempts.ndjson` resolves
59 of 59 attempt rows into ledger names and 0 of 59 into registry ids — the sidecar sits entirely on
one side of the gap.

`desk.theGap()` measures **only** the runner registry against the ledger — 28 registered, 0 in the
ledger, 28 absent, 2 globs, 25 runnable here. **It is right about what it measures and it
under-measures the gap by 67 identifiers.** Extending it to the union of all four id spaces is W17;
rendering the result, and the 34/75 glob split, is W25.

**Authoring those rows remains S4 — the operator's.** Nothing in this plan proposes an agent write
them. What the wings do is make each one **printable**: the L5 desk already emits the exact canonical
bytes for a registered gate, and every wing above ends at the same place — a gate row the operator
can read, check and sign. **And this plan adds gates to that gap rather than closing it** —
`release-excludes-lab` (§0.4), `G-PROJ-01` (§6.9.4) and every wing verifier are new registered ids
with zero ledger rows. **A plan does not get to add gates and stay silent about the intersection.**

---

## 5.10 THE DEFECT THE NUL BYTE WAS HIDING

Chasing the reason `grep` treats `viewer/lab/l5.html` as binary turned up something nobody has
named, and it is exactly the class of bug a binary-flagged file protects: **the lab's streaming
protocol does not agree with itself.**

- `viewer/lab/l5.html:249` parses the run stream with
  `if (p.startsWith("\u0000RESULT ")) { tail = p.slice(8); continue; }` — a **NUL** sentinel. That
  single `0x00` byte, at offset 13457 on line 249, is the only NUL in all of `viewer/lab/`.
  *(Written above as a JavaScript escape, deliberately: **this plan file must not itself carry a raw
  NUL byte**, or every tool that reads it inherits the same blind spot.)*
- `viewer/lab/lab_server.cjs` emits the result line in three places — `:293`, `:311`, `:313` — and
  every one of them writes **`U+0020` (a space)** before `RESULT`. Scanned raw: **`lab_server.cjs`
  contains zero `0x00` bytes in the entire file.**
- **Nothing covers it.** `verify_lab_l5.cjs` drives the desk through `runInChild` (`:237-238`),
  in-process, and **never opens the HTTP stream** — so the L5 gate is green while the parser and the
  server disagree.

**Tooling consequence, which is its own hazard:** `grep -n` prints `Binary file viewer/lab/l5.html
matches` and **suppresses all output**; `rg -n` prints `binary file matches (found "\0" byte around
offset 13457)`. Both `grep -a` and `rg -a`/`--text` return normal output, and Node's
`fs.readFileSync` is unaffected. **Any audit that greps this tree without `-a` has a blind file and
does not know it.**

**Behavioural acceptance for the fix.** Name one convention in `lab_server.cjs`, make `l5.html`
match, then add to `verify_lab_l5.cjs` a case that starts the real server, issues a real `GET`
against the streaming run route, and asserts the client-side parse yields a non-empty `tail` object
with an `observed` key. **Mutation: flip the sentinel on one side only and assert the new case
FAILS.**

> **Static evidence only.** No server was started, no browser was driven, and the end-to-end symptom
> was **not observed**. The mismatch is established from the bytes on disk; that the RESULT block
> actually fails to render is UNVERIFIED and is carried in §10.

---

# 6. THE DOOR AND THE ROAD TO PRODUCTION

## In plain words

**"Into full production" is not a road from nothing. It is a road from an undeclared,
unreproducible production to a declared, reproducible, gated one.**

## 6.1 Deployment reality — MEASURED vs DECLARED

**MEASURED on uni-lab, 2026-07-29:**

| fact | value | how |
|---|---|---|
| host | `uni-lab`, up 13d 12:28 | `os_sysinfo` |
| LAN | **10.190.245.121** (eno4); wg0 10.13.13.1; tailscale0 100.100.188.48 | `os_sysinfo` |
| flagellum prod | `/opt/uni/flagellum/prod/src`, `PROMOTE_STATUS = PROMOTED` | `os_file_read` |
| flagellum test | `/opt/uni/flagellum/test/src` + `src.bak` + `src.tgz` (3,819,835 B), `BUILD_STATUS = REBUILD_DONE` | `os_file_read` |
| prod app identity | `app/page.tsx` sha256 `00c1e47e...` — **byte-identical to the STALE worktree's**, i.e. the `redirect("/math-workbench")` file | `os_file_read` + local hash |
| prod kernel identity | `lib/uni-motor.js` sha256 `852b38d1...` — **byte-identical to BOTH local trees** | `os_file_read` + local hash |
| prod analysis identity | `lib/observed-experiment.js` sha256 `85a4a2e9...` (19,286 B) = **STALE**, vs MAIN `b757971e...` (22,328 B) | both |
| extra file on chip | `lib/duration-models.js` (4346 B) — **does not exist in MAIN at all** | `os_file_list` |
| publication | `/etc/uni/uni-flag-workbench.conf` (sha256 `f8d99f48...`, added 2026-07-20): `workbench.uni-lab.solwright.com` and `workbench.uni-lab.local` on 443 -> `http://127.0.0.1:8791` | `os_file_read` |
| live response | `curl -k -I https://workbench.uni-lab.solwright.com/` -> `307`, `Server: nginx`, location `/math-workbench`; `/math-workbench` -> `200 text/html`; **no `access-control-*` header** with an `Origin` | curl from this box |
| containers | `uni-flag-prod`, `uni-flag-test`: `podman logs` rc 0; `/run/uni-flag-prod.cid` and `/run/uni-flag-test.cid` present (64 B each) | `podman_logs`, `os_file_list` |
| fleet MCP visibility | **NONE** — `uni-flag-prod.service`, `uni-flag-test.service`, `uni-flagellum.service` all refused: *"unit not in allowlist"* | `os_systemctl_status` x3 |
| branch divergence | chip build = `c23f686` on `feature/scientific-math-workbench` (2026-07-20 23:29). MAIN HEAD = `4f6485e` on `hierarchical-aif/motor-stack` (2026-07-28 23:12). **`git merge-base --is-ancestor c23f686 HEAD` returns NO.** 74 commits on MAIN not on the chip; **3 commits on the chip not on MAIN**; merge base `4fcba6ca` | git |
| `.git` in the deployed tree | **ABSENT** — `os_file_list /opt/uni/flagellum/prod/src/.git` -> *"not a directory"* | `os_file_list` |

**DECLARED and now falsified:**

- `views.md:92` declares the chip at `10.190.245.122`. Measured **.121**. And
  `infra_registry.json:3` (`_lan_dynamic_law`) documents this exact lease move on 2026-07-16 **and
  forbids hand-declared LAN literals** — while `views.md` carries one, in the same repository.
- `views.md:96` declares *"Flagellum project — Next.js :8790 :8791"*. **TRUE in substance**
  (prod is on 8791). `docs/THE-LABORATORY-PLAN.md:88-92` says the opposite. **THE-LABORATORY-PLAN
  is the wrong one.**
- `views.md:52` declares `gates.ndjson` at *"191 rows"*. Measured **206**.
- `views.md:43` declares the Lab View *"THREE.js on T1000. NOT BUILT."* `viewer/lab/` is roughly
  5300 lines with six gates — **and the contract forbids Three.js in the released product at all.**
  The declaration is stale *and* points at a forbidden dependency.
- `views.md:295,302` shows `Scene` as unbuilt. `lib/sp/control_plane/scene.ex` is 550 lines.

> **Rule for this plan: `infra_registry.json` is the model of record for the fleet; `views.md` is a
> stale projection of it and must be regenerated from measurement, never hand-edited.** The
> `_lan_dynamic_law` already says why.

## 6.2 What a release IS, concretely

`/opt/uni/flagellum/test/src.tgz` is 3,819,835 bytes and `PROMOTE_STATUS` is a file.
**The tarball is already the release unit.** So:

> **A release = `{ commit, tree_digest, tarball_sha256, bench_manifest_sha256 }`** — a git commit in
> MAIN, a git-free Merkle over the shipped source set, the sha256 of the tarball, and the sha256 of
> the frozen bench-question manifest it must satisfy.

Not a quadlet unit — the unit is infrastructure and outlives releases. Not a commit alone — the chip
has no `.git` and cannot check one.

**And note what the build actually is.** `package.json` scripts `dev`/`build`/`start` are
**`vinext`**, not `next`; `next.config.ts` is an empty object and decorative; the real build is
`vite.config.ts` composing `vinext()` + `sites()` + `cloudflare({...})` against `worker/index.ts`.
`tests/rendered-html.test.mjs` proves the serving contract by importing `../dist/server/index.js`
and calling `worker.fetch(...)` with an `ASSETS` binding. **"Production" here means a
Workers-shaped bundle in `dist/` run by a Node/worker runtime, not a static export.**

## 6.3 The pipeline — five stages, four gated crossings, on the real `room.ex`

**Every crossing is a real call into `SP.ControlPlane.Room`. No new state machine.**
Note the shape that already fits: `room.ex` has three states and `next_of(:sterile)` is `nil`
(`:226-228`). There is no fourth. **The chip transfer is therefore `Room.exit/2`, not a fourth
state** — and the module's own docstring (`:118-124`) says exactly why: *"a sterile room is sterile
because what leaves it is accounted for."*

### BENCH (ungated — everything runs here)

The worktree, `viewer/lab` on `:8103`, and the tri-mode UI. Experiments execute. Nothing here is a
release, nothing here is authoritative, nothing here is refused. **This is the wet bench.**

### BENCH -> GREEN — "a candidate exists"

Receipt: `UNI.Minecraft/evidence/release/<rel-id>/candidate.json` —
`{ commit, tree_digest, node_version, npm_version, package_lock_sha256, authored_at }`.
Written by `UNI-FLAGELLUM/scripts/release-candidate.mjs` (NEW). **No gate.** `Room.new/1` starts
`:green` by construction (`room.ex:62-66`, kebab-case enforced). Nothing is assumed about a green
room and nothing should be. Refuses: a non-kebab id -> `{:error, {:room_id_not_kebab_case, id}}`.

### GREEN -> CLEAN — `Room.enter(room, :clean, %{scan: path}, keys)`

Checked by `room.ex`, unmodified: `order_condition`; `keys_condition` (**at least 2 distinct
parties AND at least one `:operator` key**); `receipt_condition(:scan_receipt, ...)` — and the file
must be **on disk** at `Path.join(@repo, path)` (`:205-209`).

Receipt written by `scripts/release-scan.mjs` (NEW) -> `evidence/release/<rel-id>/scan.json`.
It runs the nine required-validation commands and records each **verbatim** as
`PASS | FAIL | BLOCKED | NOT_RUN`, **with the reason**. `cross-study:verify-raw` emits `BLOCKED`
with *"experiments/upstream-cache/ito-2021-raw-data.zip absent"*. `npm audit --omit=dev` emits its
advisory list. **A `BLOCKED` does not stop the crossing; a `FAIL` does.** The scan is a record;
`Room` is what refuses.

**Critical: the scan receipt must be generated from `gate_runner.cjs`'s structured `runGates()`
return value (exported at `:166`), NOT from its terminal output.** Redirecting stdout to a file is
not a receipt — it is not content-addressed, carries no code identity, and can be typed.

Keys: `Key.new!("michael", :operator, "<his spoken co-sign, quoted with a date>")` plus
`Key.new!("claude", :agent, "bench-diff:<diff_record_id>")` — **the agent's ref is the content
address of a cross-engine diff that passed, so an agent cannot mint a key without a real agreement
behind it.** Two agents produce the exact refusal at `room.ex:186-190`.

**Third key, recommended and absent today:** `Key.new!("uni-lab", :service, "<MCP audit_id>")`.
The MCP already returns a per-call `audit_id`. Binding the transport's own audit id into the
transition would make the Room and the approval queue **one** law rather than two, unjoined.

### CLEAN -> STERILE — `Room.enter(room, :sterile, %{execution: path}, keys)`

Receipt written by `scripts/release-execute.mjs` (NEW) ->
`evidence/release/<rel-id>/execution.json`. It runs `npm ci && npm run build` **twice into two
scratch directories** and records both `dist/` tree hashes. **Determinism is a gate, not a hope.**
If they differ, the file records `deterministic: false` with the first differing path and the
crossing is not attempted.

**And the execution receipt carries the science.** Alongside the build determinism it names
`evidence/bench/manifest/<tree_digest>.diff.json` — **the bench diff over the frozen question set,
offline-kernel vs on-chip, every entry `IDENTICAL` or `AGREE_WITHIN_TOLERANCE`. A single
`DIVERGENT` or `NOT_COMPARABLE` and the room refuses.** *This is the release-gating scientific
instrument, and it is the whole point of tri-mode.*

### STERILE -> CHIP — `Room.exit(room, %{contamination: p1, manifest: p2})`

`exit/2` is gated and **takes no keys** (`:126-134`): the two-key authority was spent on entry;
what governs the exit is accounting for what leaves.

`contamination.json`, written by `scripts/release-contamination.mjs` (NEW), sweeps the **built
bundle**, not the source:
- zero matches for `WebGL|WebGPU|navigator\.gpu|from ["']three|@react-three`;
- zero matches for `openai|anthropic|gemini|languageModel|chatCompletion`;
- zero analytics / beacon / account tokens;
- **every remaining URL literal resolves to an entry in `lib/observation/channel.json`** — this is
  where *"no hidden network calls"* becomes mechanical;
- **zero absolute Windows filesystem paths** (`[A-Za-z]:\Users\`). The Phase-E audit found the
  vinext font plugin emitting the build machine's username into an `@font-face src` at
  `dist/server/index.js:14546`. **That is a disclosure and it must fail the exit.**

`manifest.json`, written by `scripts/release-manifest.mjs` (NEW): sha256 and byte size of every file
that will land on the chip, plus the `dist_sha256` from `execution.json`.

**Then, and only then, the transfer.** And the landing check re-reads every shipped file through
`mcp__uni-lab__os_file_read` and re-hashes it against `manifest.json` — **exactly what was done by
hand this session to prove the running bytes.** Mismatch -> the promote does not happen and
`PROMOTE_STATUS` is not written.

### What refuses, and why a refusal teaches

`room.ex:216-217` unknown state; `:219` already there; `:222-224` out of order — **green to sterile
is impossible, there is no skip**; `:230-233` any unmet condition, **and the error carries the same
list a pure read would have given, so a refusal teaches**; `:205-209` a named receipt not on disk,
checked *before* `File.read!` at `:249` can raise; `:284-287` `Command.submit` is the only writer;
and **there is no override to call**, proven by `test/sp/control_plane/no_override_path_test.exs`.
`room.ex:271` records **every** key in `co_signers`, not just the ones that satisfied the condition —
a crossing whose authority is not on the record cannot be audited later.

## 6.4 A cross-repository coupling that must be decided, not discovered

**`room.ex` resolves receipt paths against `@repo = Path.expand("../../..", __DIR__)` — the
UNI.Minecraft root.** So flagellum release receipts must be written **into
`UNI.Minecraft/evidence/release/`**, not into the flagellum tree, or every `receipt_condition`
returns *"named but is not on disk."* This is a real coupling between two repositories and it must
be decided deliberately, before the first crossing, not discovered at it.

## 6.5 The artifacts that do not exist and must

| path | what |
|---|---|
| `UNI.Minecraft/lib/sp/control_plane/release.ex` | NEW, ~150 lines. Drives one Room through four crossings for a `<rel-id>`. Calls Room; contains **no policy of its own**. |
| `UNI.Minecraft/scripts/release_room.exs` | NEW. The CLI, following the `scripts/*.exs` convention. On refusal it **prints the condition list verbatim and stops**. |
| `UNI-FLAGELLUM/app/(lab)/lab/airlock/page.lab.tsx` + `UNI.Minecraft/viewer/lab/airlock.cjs` | NEW, **split by §0.5**: the `.cjs` is the read-only **computation** that calls `Room.conditions/4` and serves it as JSON; the `.lab.tsx` is the **airlock desk** that renders it as lit/unlit conditions with the `detail` string shown **as written**. Read-only both sides: it draws the door and cannot walk through it. |
| `UNI.Minecraft/viewer/verify_release_room.cjs` + registry entry | NEW gate. **AC:** two agent keys refused; a receipt named but not on disk refused; green-to-sterile refused; **the ledger byte-unchanged after every refusal.** |
| `UNI.Minecraft/deploy/uni-flagellum/{deploy.sh,rollback.sh,Containerfile}` | NEW. Modelled on the existing `deploy/uni-producer/deploy.sh` (which is itself real and **self-refusing** — it exits 1 unless an ack env var is set). **Makes the existing hand-built production reproducible.** |
| `UNI.Minecraft/production/containers/systemd/uni-flag-{prod,test}.container` | NEW quadlets, modelled on the six existing `uni-bcast-*.container` units. **None of the 8 `.container` files in UNI.Minecraft today is for the flagellum.** |
| `UNI-FLAGELLUM/scripts/release-{candidate,scan,execute,contamination,manifest}.mjs` | NEW x5. |
| `UNI-FLAGELLUM/.github/workflows/ci.yml` | NEW. **There is none.** Runs the nine required commands plus `release-scan.mjs` on every push. Model it on `UNI.Minecraft/.github/workflows/ci.yml` (four jobs), whose own comment records that CI had **never run** before Phase 9 step 1.3 because the branch filter never matched. |
| `UNI.Minecraft/viewer/verify_chip_tree_digest.cjs` + registry entry | NEW. Reads the chip tree over `os_file_read`, recomputes `tree_digest`, compares to the sterile receipt. **`ci: false`, `external_needs: "uni-lab MCP reachable"` — listed, not run, never a fabricated pass**, exactly as hud/overlays/colony are handled. |
| `UNI.Minecraft/viewer/build_identity.cjs` (EDIT, additive) | add `tree_digest` alongside `module_set_sha256`, computed over a declared source set so it survives having no `.git`. **AC:** `identity()` returns a non-null `tree_digest` in a directory with no `.git`, and `verify_build_identity.cjs` still passes unchanged. |
| `UNI.Minecraft/viewer/lab/verify_bench_parity.cjs` | NEW. The deploy-lag tripwire's shape applied to numbers. **AC (mutation):** change one float's last mantissa bit in the on-chip record and the gate goes RED; **leaving a tolerance in must swallow the mutation, which is the falsifier and must fail the gate.** |

## 6.6 The first crossing must record the past, not pretend it was empty

**Nothing in git records the live deployment.** The state of the chip is knowable only by querying
the chip. If the MCP is down, the token rotates, or the box is rebuilt, the fact that a flagellum
release exists is **unrecoverable from any repository**.

> **The very first `release_room.exs` run must RETROACTIVELY record the existing deployment as a
> ledger entry, with its measured hashes and its branch, BEFORE any new one is attempted** —
> otherwise the Door's first crossing pretends the chip was empty, and the first thing the new
> honest machinery does is tell a lie.

## 6.7 The blocking list for an honest production release

**A release claim today would be dishonest on six counts**, each with a named correction:

1. A required gate (`X01_SOURCE_INTEGRITY`) reports PASS with zero evidence on disk.
2. A shipped scientific equation is wrong **and is currently on the air**.
3. A passing test enforces a truth-contract violation on the surface MAIN serves —
   `lib/walkthrough.js:356-358` returns `"OBSERVED"` for mode `LIVE_INSTRUMENT` and
   `tests/walkthrough.test.mjs:41` pins it. **In the STALE branch this was unreachable because `/`
   redirected away; in MAIN, `app/page.tsx` renders `<UniFlagellumLab/>` with no redirect, so the
   mitigation is gone.**
4. A required verification gate's headline verdict is a hardcoded string literal.
5. `cross-study:verify-raw` is `BLOCKED_EXTERNAL` — 4.09 GB absent — so the raw-source byte chain is
   `EXTERNAL VALIDATION REQUIRED`.
6. Production dependencies now carry **3 HIGH** advisories, up from 0 eight days ago.

`fullBiologicalParityAchieved` remains `false` in the report and in the independent check.
**P0 is not clean.** Determinism is unproven for the release path (no double-build check exists),
the EFE algebra is wrong, and a gate reports PASS without evidence. **The first unsatisfied level is
P0, and no higher level can be claimed until items 1 and 2 close.**

## 6.8 And the road to air runs through the science

`colony_on_program` is blocked on `forage-pureworld-graduation`, whose runner
`runs/pureworld_qa_gate.exs` (91 lines) **still raises `@scaffold`** — the attribute is declared at
`:28` and the `raise """` is at **`:39`**, immediately after `check_prereqs()` at `:37` (`:40` is the
first line of the heredoc; an unrelated second `raise` sits at `:84`). The contract the future
implementation must honour is printed in the same heredoc. **`forage-pureworld-graduation` cannot
run, and the runner says so on purpose.**
**And no verdict has yet been authored about a real scientific claim.** Neither is fixed by this
plan; both are named so that no wing is mistaken for progress on them.

---

## 6.9 THE PUBLIC PROJECTION — where the world can see it

### In plain words

**He asked for a laboratory the world can see. This plan, as drafted, built one that exactly one
machine on earth can see — and it never told him it had made that choice.**

Every surface §2, §3 and §5 design binds `127.0.0.1`. Two of the plan's own acceptance criteria make
*refusing a non-loopback request* a PASS condition (§3.11 item 4, and **W9**). Nothing in the draft
argued for that. It was inherited from the chip viewer's fence and applied to everything, including
the parts of the laboratory that are not acts at all.

The fix is not to unfence the instrument. **The fix is to notice that a laboratory is two different
things, and that only one of them needs a fence.**

### 6.9.1 The tension, named precisely and fairly

The contract's product constraint is four lines long and reads, verbatim:

> The released product must remain CPU-only and must contain no LLM inference,
> GPU computation, WebGL, WebGPU, Three.js, analytics, accounts, or hidden network
> calls. Development agents may use their own tools, but those tools may not
> become undeclared runtime dependencies.
>
> — `UNI-FLAGELLUM/CLAUDE.md:69-72`

Now the part the draft got wrong, and it is decisive:

> **Neither contract file forbids publication. Neither contract file says "loopback".**
> A case-insensitive grep for `loopback|127.0.0.1|localhost|public|internet|expose` over **the two
> `CLAUDE.md` files that govern this product** returns **ten** hits — **five in
> `UNI-FLAGELLUM/CLAUDE.md`** (`:13` UNI TRACK `:8102`, `:41` the OBS WebSocket `:4455`, `:395` the
> voice transcript `:5858`, `:404` and `:412` UNI TRACK again) and **five in its untracked twin at
> `Documents/UNI-Flagellum/CLAUDE.md`** (`:13`, `:41`, `:234`, `:243`, `:251` — the same five
> sentences at different offsets). **All ten** are `127.0.0.1` references to the *agent's own
> operator surfaces*. **Zero** are product constraints, and `loopback`, `localhost`, `public`,
> `internet` and `expose` each return **0** in both files, measured this session.
>
> **The third copy is excluded, and naming it matters, because it inverts the result.**
> `UNI.Minecraft/CLAUDE.md` is the chip platform's contract, not the flagellum's; it carries
> `loopback` **6** times and `public` **12** times. **A reader who picks the wrong second file
> concludes the opposite of this paragraph.** *(A previous revision said "both `CLAUDE.md` files"
> while citing line numbers drawn only from the outer copy — and the banner it reproduces records
> that three copies exist.)*

So the loopback-only rule is **the plan's invention, not the contract's.** The draft imported a fence
from the chip viewer and then treated it as law. **That is the inversion, and this is where it gets
named.**

**Read the constraint again for what it actually says.** Every clause governs what the artifact
*does at runtime* — what it computes on, what it calls out to, what it collects, whom it identifies.
Not one clause governs *where the artifact is served from*. "No hidden network calls" is a property
of the bundle. A visitor fetching a static file is not a call the bundle makes. **Publishing a bundle
that makes zero network calls does not create a network call.** There is no conflict here at all —
the draft manufactured one by conflating *serving* with *calling*.

**Where loopback WAS the right answer, and why.** The contract forbids **accounts**. That removes the
ordinary way of proving a human is present for an act. What remains is network locality: if the
request came from `127.0.0.1`, someone is at this machine. That is exactly the guarantee class F31
already labels honestly — `presence_evident`, **not** unforgeable. So for every surface that
**mutates the laboratory's record**, loopback is correct and stays:

| surface | why it stays loopback |
|---|---|
| the bench run record (§2.3) | a RUN writes a row that later evidence rests on |
| the intake desk (§3.4) | declaring an intake changes what the project claims it observed |
| the NEEDS YOU decision rail (§3.7) | a HOLD is his signature |
| `POST /api/comment` on TRACK :8102 | append-only, but still append |
| the chip observer broker (§2.9) | it reads a production host |
| the airlock door (§3.8) | it crosses the Room |

**Where loopback is the wrong answer.** The equation cards, the derivations, the proofs, the twelve
worksheets, the casebook, the gate ledger, the frozen wing results, every truth chip and every
provenance pin — **these are statements, not acts.** They assert; they do not change anything. A
statement has no presence requirement, because reading it cannot alter the record. Fencing the
statement surface behind loopback does not protect the laboratory. **It only prevents anyone from
checking it.**

> #### The rule this subsection adds
>
> **ACTS ARE LOOPBACK. STATEMENTS ARE PUBLIC.**
>
> If a surface can change what the project claims, it binds `127.0.0.1` and it is co-signed.
> If a surface only shows what the project already claimed, it is exportable, and withholding it is
> not caution — **it is the project declining to be checked.**

### 6.9.2 Can this project even do a static export? — MEASURED, and the answer is yes

The draft never asked. The answer is more interesting than expected, because **MAIN does not build
with Next.js.**

| fact | value |
|---|---|
| build command | **`vinext build`**, not `next build` |
| the actual toolchain | `vinext@0.0.50` + `vite@8.0.13` + `@vitejs/plugin-rsc@0.5.26` + `@cloudflare/vite-plugin@1.37.1` |
| `next@16.2.6` | present as a **dependency**, but it does not drive the build |
| operative config | **`vite.config.ts`** — imports `./.openai/hosting.json` and wires `cloudflare({ main: "./worker/index.ts" })` |
| `next.config.ts` | 7 lines, an empty object, **no `output` key** *(§0 adds `pageExtensions` to it; that is the only other thing it will hold)* |
| **static export configured today** | **NO** |
| **static export SUPPORTED** | **YES** |

**Static export is available and the change is one line.** Measured in the installed package:
`config/next-config.js:284` reads `config.output ?? ""`; `:285` warns
`[vinext] Unknown output mode "…", ignoring` for anything but `export`/`standalone`; `:302` resolves
it. `cli.js:269` branches `if (parsed.prerenderAll || resolvedNextConfig.output === "export")`.
`build/static-export.js` exports `staticExportApp()` and `staticExportPages()`, both delegating to
`prerender.js` in `mode: "export"`.

**The one-line change** — applied **only in the projection build**, never to the lab build, because
the lab build is the Cloudflare Worker. That is why the projection gets its own script rather than a
flag:

```ts
const nextConfig: NextConfig = { output: "export", /* plus §0's pageExtensions */ };
```

> **CORRECTED BY §0.9 decision 3 — this paragraph said the opposite and it was the bug.** The draft
> built the projection with `UNI_SURFACE` **unset**, so every `app/(lab)/**/page.lab.tsx` was outside
> the route graph — **and then promised to publish the equation cards and the twelve worksheets,
> which are exactly what lives there.** The projection is built with **`UNI_SURFACE=lab`**, because
> **the projection is a build output OF the laboratory** (§6.9.3).
>
> **There are three build profiles, and conflating any two of them is how this went wrong:**
>
> | profile | `UNI_SURFACE` | `output` | what it is | its gate |
> |---|---|---|---|---|
> | **RELEASE** | unset | (worker) | what is promoted to the chip | `release-excludes-lab` (§0.4) |
> | **LAB** | `lab` | (worker) | the instrument the operator works in | the §3A/§5 suites |
> | **PROJECTION** | `lab` | `export` | the frozen static statement surface | `G-PROJ-01` (§6.9.4) |
>
> `release-excludes-lab` and `G-PROJ-01` are **not** two gates checking the same law — they check
> two different laws over two different artifacts. **The RELEASE must not serve a laboratory route.
> The PROJECTION must not contain an act, a server, an outbound channel or a loopback literal.**
> Reading them as one law is what produced a projection that deleted the thing it promised to
> publish.

#### Three hazards the exporter will NOT catch, measured

**1. The exporter only WARNS about server routes.** In `static-export.js`, `toStaticExportResult()`
pushes `API route ${r.route} skipped — API routes are not supported with output: 'export'` into
`result.warnings` — **never into `result.errors`.** A build with API routes still exits 0 and still
emits a bundle, silently missing them. **Any gate that trusts the exporter to refuse server routes is
vacuous.** §6.9.4's verifier therefore inspects the emitted bytes and never reads the exporter's
opinion.

**2. An accounts module is already sitting in `app/`.** `app/chatgpt-auth.ts` (2,404 B) — see §0.6,
which moves it to `app/(lab)/`. **It is dead today and it must stay dead.** Wiring it in would break
the contract's **"no accounts"** clause *and* make static export impossible in the same commit,
because `next/headers` is a request-time API. The verifier asserts on it directly (**A6**).

**3. Fonts reach the public internet at BUILD time.** `app/layout.tsx:2` imports `Geist` and
`Geist_Mono` from `next/font/google`. `node_modules/vinext/dist/plugins/fonts.js:278` fetches
`fonts.googleapis.com` and `:299` downloads each `fonts.gstatic.com` woff2, then **self-hosts** them:
`css = css.split(fontUrl).join(filePath.replaceAll("\\","/"))`. **Good news — the emitted bundle
carries no third-party URL.** Bad news — on a cold cache the build *requires* network and **throws
`GoogleFontsHttpError`** at `:280-282` if the fetch is not ok. So a cold offline projection build
**fails**, and a regression in that rewrite would silently put a Google URL in a public page.
**A4** covers it; §6.9.6 records the offline consequence.

### 6.9.3 THE STATIC PUBLIC PROJECTION — concretely

> **Naming note.** Every name below is a proposal. **Naming is his** (§8 row 13).

**The script:** `UNI-FLAGELLUM/scripts/build-public-projection.mjs` — new file, matching the existing
`scripts/independent-*.mjs` / `scripts/run-*.mjs` convention.
**It writes to:** `UNI-FLAGELLUM/dist/public-projection/` — a fresh directory, emptied on each run.
`dist` is already outside lint scope (`eslint . --ignore-pattern dist --ignore-pattern .next`) and is gitignored
(`/dist/` at `.gitignore:42`; `:44` is `/outputs/`), so the release artifact is built, never committed.

> **§0.9 decision 4 rewrote this. What the previous draft did, and why it could not work.** Step 2
> **deleted `app/(lab)/`** from the scratch tree, and the absent-list below confirmed it. Three rows
> later the IN-list promised the 11 equation cards, the 12 printable worksheets and five of six
> workbench views — **which under §0.2 and §0.9 decision 3 are the laboratory.** §6.9.5's criterion,
> *renders the walkthrough, all 11 equation cards and all 12 worksheets from `file://`*, was
> **unsatisfiable as written**: the generator deleted its own input.
>
> **The correction is a change of kind, not of detail. THE PROJECTION IS NOT A COPY OF A TREE WITH
> DELETIONS. IT IS A BUILD OUTPUT OF THE LABORATORY.** The generator **reads** the laboratory and
> **emits** static HTML in which every interactive and networked affordance is structurally absent
> **from the OUTPUT**. Deleting the source before reading it is the bug. Everything absent is now
> defined on the emitted bundle, which is also the only place `G-PROJ-01` has ever looked.

**What it does, in order:**

1. Refuses to run on a dirty tree, or records `--allow-dirty` in the manifest as `dirty: true`.
2. Copies MAIN to a scratch tree and overwrites `next.config.ts` with **both** `output: "export"`
   **and** §0's `pageExtensions`, then builds with **`UNI_SURFACE=lab`**. **`app/(lab)/` is READ, not
   deleted** — it is the thing being projected.
3. Deletes, from the scratch tree, only what can **emit an act, a server or an outbound channel**:
   `worker/`, `vite.config.ts`'s cloudflare plugin block, `app/(lab)/api/` (the whole route-handler
   directory, so the chip channel cannot be emitted), `app/(lab)/lab/intake/`,
   `app/(lab)/lab/airlock/`, `app/(lab)/lab/compare/`, `app/(lab)/chatgpt-auth.ts`, and the Web
   Serial block named in the absent-list below. **Statement rooms — the chalkboard, the proofs, the
   worksheets, the wings, the map, the casebook — are kept and rendered.**
4. Runs the export, then writes `PROJECTION.txt` and `projection.manifest.json`.
5. Runs `scripts/verify-public-projection.mjs` (§6.9.4) **against the emitted bundle** and **exits
   non-zero if it fails**, so a broken projection is never publishable.

> **The deletions in step 3 are an input convenience, not the guarantee.** The guarantee is A1–A8 in
> §6.9.4, every one of which reads emitted bytes. If a deletion is forgotten, the verifier fails; if
> a deletion is performed and something slips through anyway, the verifier still fails. **Nothing in
> this section is trusted because a directory was removed.**

#### What is IN it

| content | source | measured |
|---|---|---|
| the 13-step living-science walkthrough | `app/(product)/living-science-walkthrough.tsx` (337) | yes |
| the biological stage + CC BY 4.0 media | `app/(product)/biological-stage.tsx` (319), `public/media/` | yes |
| the science gates panel | `app/(product)/science-gates-panel.tsx` (130) | yes |
| the cross-study parity panel | `app/(product)/cross-study-parity-panel.tsx` (187) | yes |
| the observed-experiment panel | `app/(product)/observed-experiment-panel.tsx` (232) | yes |
| the guided teacher | `app/(product)/guided-teacher.tsx` (117) | yes |
| **the 11 equation cards** — `WORLD BOUNDARY BAYES VFE EFE DURATION DLT ROTATION LATTICE GMC RFT`, each `{name, truth, equation, input, output, source, plain}` | `app/(lab)/lab/chalkboard/` **in the LAB build**, ported by W3 from STALE `scientific-math-workbench.tsx:80-191` | yes — **11, not 12** |
| **the 12 printable worksheets**, 12 ruled lines each + `Name / session · Date · Source commit` footer | `lib/worksheets/registry.js` + `app/(lab)/lab/chalkboard/worksheet.tsx` (§4.4), from the same STALE tuples at `:390-401` | yes |
| five of the six workbench views — `flow`, `equations`, `evidence`, `planned`, `worksheets` | `/lab/chalkboard` in the LAB build; the sixth view is the act surface and is absent | yes |
| **the derivations** — `/lab/proof` and every `/lab/proof/<id>` | `app/(lab)/lab/proof/` (§4.6) | **NOT_PROJECTED in v1** — W16 has not landed |
| the frozen wing results — 11 evidence JSONs | `public/*.json` | yes |
| every truth chip, with its class | `truth-badge` markup exists in **exactly two components**, measured by `grep -n "truth-badge" app/` this session: `biological-stage.tsx:287,301,312,313,314,315` and `living-science-walkthrough.tsx:115,123,130,137,152,163,171,185,309`, styled by 9 rules in `app/globals.css`. **`uni-flagellum-lab.tsx` carries ZERO** — `grep` exits 1 over its 880 lines | yes, but see the adverse finding below |

> **ADVERSE, and it was hiding behind a wrong citation.** A previous revision of this row cited
> `uni-flagellum-lab.tsx:132,139,146` as truth-chip markup. **RETRACTED.** Those three lines are
> `status: "OBSERVED / MODELED"`, `status: "OBSERVED / INFERRED"` and `status: "OBSERVED"` — plain
> string fields inside a `partDetails` data object, rendered as unclassed text. **So the largest
> component in the product renders its truth status with no machine-readable truth class at all.**
> That is not a citation defect, it is a product defect, and it is why A5 below is scoped rather
> than global: A5 asserts over the two files that carry chips, and **giving the bench panel real
> chips is a W-FLAG build item, not something A5 may be weakened to accommodate.** Until the
> flagellum wing adds them, a bench screenshot cannot be read for epistemic status without reading
> text — which is precisely the Phase-7 clause this programme has already failed once.
| every provenance pin | `public/walkthrough-evidence-manifest.v1.json` | yes |
| the gate ledger | `UNI.Minecraft/evidence/gates.ndjson` | **NOT_PROJECTED in v1** |
| the 8 proof documents | `UNI.Minecraft/lab/proofs/` | **NOT_PROJECTED in v1** |
| the LLM casebook | `generate_casebook.cjs` output (§3.9) | **planned, does not exist yet** |

The three `NOT_PROJECTED` rows are **carried as visible placeholders in v1** and only enter the
bundle once §5 and §3.9 land. **A placeholder that says `NOT_PROJECTED` is honest; a missing section
is not.**

#### What is structurally ABSENT — deleted, not disabled

**Absent means the bytes are not in the bundle.** A disabled button is still an attack surface, still
a lie about what the page is, and still fails the verifier.

| absent | why |
|---|---|
| **every POST route and route handler** | a statement surface writes nothing. MAIN has **zero** API routes today (`find app -type d` returns only `app`), so v1 starts clean — but §3.4's intake desk and §2.3's bench record both add write routes to the LAB build, and A1/A2 assert their deletion rather than assuming it |
| **every act ROOM inside `app/(lab)/`** — `/lab/intake`, `/lab/airlock`, `/lab/compare`, and the whole of `app/(lab)/api/` | **Not the wing — the acts.** §0.9 decision 4: the projection is a build output *of* the laboratory, so deleting `app/(lab)/` would delete the cards and worksheets this bundle exists to publish. What is absent is every room that **writes**, plus the route-handler directory entirely, so no `route.*` file can be emitted. **A1 asserts zero route-handler chunks in the output, which is the guarantee; the deletion is only how the input is prepared.** |
| **the RUN control on every statement room that keeps one** | a wing may render its numbers; it may not offer to recompute them into a record. §3.11 already requires RUN be absent until a prediction is recorded, and a stranger cannot author a prediction |
| **the RUN control** | RUN produces a *bench run record*, and §3.11 already requires RUN be absent until a prediction is recorded. **A stranger cannot author a prediction into this laboratory's ledger** |
| **the intake desk, the NEEDS YOU rail, the chip observer broker, the airlock** | §3.4, §3.7, §2.9, §3.8 — all acts |
| **the entire Web Serial block** | it is *"The only inward crossing"* (`app/uni-flagellum-lab.tsx:81`). `connectSerial` `:539`, `navigator.serial` `:540`, `requestPort()` `:546`, `disconnectSerial` `:580`, `data-testid="connect-serial"` `:654` |
| **`chatgpt-auth.ts`** | accounts, forbidden at `CLAUDE.md:69-72` |
| **`worker/` and the cloudflare plugin** | a server |
| **every loopback literal** | including the *prose* one |

> **The measured trap.** `app/uni-flagellum-lab.tsx:542` is
> *"Web Serial is unavailable in this browser. Use Chromium over localhost or a secure origin."*
> That is the **only** `localhost`/`127.0.0.1` occurrence in all of `app/`, `lib/` and `scripts/`,
> and it is **prose, not an address**. **A naive `grep localhost` gate would fail on an English
> sentence and teach everyone to add an exception — which is how gates die.** The verifier matches
> **loopback URLs**, `https?://(127\.|localhost|0\.0\.0\.0|\[::1\])`, and additionally asserts the
> serial block is gone, so the prose string cannot survive anyway.

#### How a number carries its provenance

**The mechanism already exists and has the right shape** — it does not need inventing, only
extending. `public/walkthrough-evidence-manifest.v1.json` has keys
`[schema, frozenAt, claimFence, assets]`, and each asset carries:

```json
{ "id": "MEARS_2014_VIDEO_1",
  "path": "public/media/mears-2014-run-tumble.mp4",
  "bytes": 1634522,
  "sha256": "b5839132aec15ca099e9b99e6bd0f57fa26a720a97928e0a5f285eb5d9cd5050",
  "doi": "10.7554/eLife.01916.010",
  "license": "CC BY 4.0",
  "species": "Escherichia coli",
  "truthClass": "OBSERVED" }
```

**The rule for the projection:** every rendered number is wrapped in a pin element carrying
`data-pin-artifact`, `data-pin-sha256`, `data-pin-key`, `data-pin-truth`, `data-pin-species`, and
renders a visible pin the reader can click. Clicking shows the artifact path, the sha256, the JSON
key the number was read from, its truth class and its species label. **The artifacts themselves ship
in the bundle**, so the stranger's check is three commands, printed on the page:

```
sha256sum evidence/science-gates-report.json     # compare to the pin
node -e "…"                                      # read the same key
npm ci && npm run science:verify                 # rederive independently
```

This is the existing `math-workbench-provenance` footer (`scientific-math-workbench.tsx:405-409` —
*Executable sources* / *Frozen observations* + raw SHA-256 / *Independent reproduction*) promoted
from a page footer to a **per-number** obligation.

**A number with no pin does not render.** It is replaced by `UNPINNED` in the projection, and **A5**
fails the build. That is deliberate: **a projection that can show an unattributed number is a
projection that can launder one.**

#### How it says what it is

**Never presented as live.** Three mechanisms, all asserted by the verifier:

1. **A banner on every page**, first element in `<body>`, not dismissible:
   > **This is a frozen projection of a laboratory. It is not live. Nothing here is running.**
   > Commit `4f6485e9…` · projected `2026-07-29` · the live instrument is not published.
2. **`/PROJECTION.txt`** at the bundle root — plain text, readable with no browser, carrying
   `commit`, `tree_digest`, `built_at`, `dirty`, the absent-list, and the same sentence.
3. **`/projection.manifest.json`** — machine-readable: every emitted file with its sha256, the source
   commit, and the `NOT_PROJECTED` list, so the bundle can be diffed against itself.

### 6.9.4 THE GATE — `verify-public-projection.mjs`

**The verifier:** `UNI-FLAGELLUM/scripts/verify-public-projection.mjs` — new file.
**Registered as:** gate `G-PROJ-01`, `ci: true`, with a `gate_row` — **and therefore one more
registered id with zero rows in the canonical ledger, which §5.9 and §8 row 4 now say out loud.**

**It inspects the emitted bundle. It never reads the exporter's warnings and it never greps
`app/*.tsx`.** Source greps are textual; this plan's rule is behavioural.

| # | assertion | how it is checked |
|---|---|---|
| **A1** | **Zero server artifacts.** No `_worker.js`, no `worker/`, no `.server.js`, no route-handler chunk. Emitted extensions are a closed set: `.html .js .css .json .svg .mp4 .webp .woff2 .txt .ico` | walk the output, reject any path outside the set |
| **A2** | **Zero POST and zero outbound channels.** No `method:"POST"`, no `fetch(`, no `XMLHttpRequest`, no `new WebSocket`, no `EventSource`, no `navigator.serial`, no `requestPort` in any emitted `.js` or `.html` | scan emitted bytes |
| **A3** | **Zero loopback URLs.** `https?://(127\.|localhost|0\.0\.0\.0|\[::1\])` matches nothing | scan emitted bytes |
| **A4** | **Zero third-party hosts.** No `fonts.googleapis.com`, no `fonts.gstatic.com`, no host outside the bundle in any `src`/`href`/`url()` | parse emitted HTML + CSS |
| **A5** | **Every truth chip present, and every number pinned — scoped to the pages that carry chips.** For every emitted page **whose source component is one of the two that render `truth-badge`** (`biological-stage`, `living-science-walkthrough` — the list is derived by grepping the projection's own source, never transcribed), the set of `truthClass` values in the shipped manifest ⊆ the set of `truth-badge` classes rendered; every asset `id` appears in at least one page; **zero occurrences of `UNPINNED`** anywhere in the bundle. **A5 is deliberately NOT global**: `uni-flagellum-lab.tsx` renders zero chips today (see §6.9.3), so a global form would either fail on a correct bundle or be weakened until it passed. **A6 below is the one that makes that visible instead of hiding it.** | parse emitted HTML |
| **A6** | **The chip gap is reported, not silently tolerated.** The build prints, and the gate records, the count of emitted pages that carry `data-truth-class`-bearing markup and the count that carry none, **both computed from the bundle at build time**. The gate FAILS only if that second count *rises* against the recorded baseline. **Mutation: add one unclassed `status:` string to a projected component and the count rises and the gate goes red.** | run the build twice |
| **A6** | **No accounts.** `signin-with-chatgpt`, `signout-with-chatgpt`, `oai-authenticated-user` appear zero times | scan emitted bytes |
| **A7** | **Every pin recomputes.** Every `data-pin-sha256` equals `sha256(bundle bytes at data-pin-artifact)` | recompute against shipped files |
| **A8** | **It says what it is.** The banner sentence appears in **every** emitted `.html`; `/PROJECTION.txt` exists and its `commit` equals `git rev-parse HEAD` | read both |

**Exit 0 = publishable. Exit 1 = the bundle is not published, and the reason names the file.**

#### The mutations that prove it bites

`node scripts/verify-public-projection.mjs --mutate` applies each of these to a **copy** of the
bundle and asserts the verifier **exits 1** for each, naming the file. **If any mutation passes, the
gate is theatre and the runner reports `VACUOUS`, not `PASS`.**

| # | mutation | must trip |
|---|---|---|
| **M1** | inject `<script>fetch("/x")</script>` into one emitted `.html` | **A2** |
| **M2** | flip one byte in a shipped evidence JSON | **A7** |
| **M3** | delete one asset's `truth-badge` span from one page | **A5** |
| **M4** | **revert `next.config.ts` to `output: ""` and rebuild** — the exporter emits the Worker bundle and exits **0 with only warnings** | **A1** — *the sharp one, because it proves the gate does not trust the exporter* |
| **M5** | add `import { getChatGPTUser } from "./chatgpt-auth"` to a product page and rebuild | **A6**, and the prerender fails on `next/headers` |
| **M6** | break the font rewrite so `fonts.gstatic.com` survives into the CSS | **A4** |
| **M7** | strip the banner from one page | **A8** |
| **M8** | re-add the `connect-serial` button | **A2** (`navigator.serial`) |

**M4 and M5 are the two that matter.** M4 is the only one that catches the measured fact that
`static-export.js` files API routes under `warnings`, not `errors`. M5 is the only one that catches
the accounts module.

### 6.9.5 Acceptance criterion — behavioural

> **W23a.** `node scripts/build-public-projection.mjs` produces a bundle in `dist/public-projection/`
> and `verify-public-projection.mjs` exits **0** on it. Every mutation in §6.9.4's table makes it exit
> **1**, each naming the offending file — **the count is read from the table at run time, not
> transcribed here** — and **M4 exits 1 even though the export itself exited 0 with only warnings.**
>
> **The satisfiability clause, which is what §0.9 decision 4 repaired.** Opening `index.html` from
> `file://` with the machine's network interface **down** renders the walkthrough and reaches
> `/lab/chalkboard/index.html` **from a link on the page, not a typed address**, where it renders
> **every equation card in `EQUATION_REGISTRY` and every worksheet in `lib/worksheets/registry.js`**
> — counts read from those registries by the test, so porting a twelfth card cannot fail this
> criterion — and `window.print()` produces one `.workbook-page` per registry entry. The browser
> devtools network panel records **zero** requests to any host. **This is satisfiable because the
> generator now builds `UNI_SURFACE=lab`; under the previous draft it was not, because step 2 deleted
> `app/(lab)/` before the export ran.**
>
> Deleting `/PROJECTION.txt` fails the gate. Adding a number with no pin renders `UNPINNED` and fails
> the gate. **And one act-absence check that must be performed from the bundle, not from the
> generator's log:** `GET`-ing `/lab/intake`, `/lab/airlock`, `/lab/compare` and `/api/chip` inside
> the emitted tree finds **no file at all** — not a stub, not a 404 page authored for the purpose.

### 6.9.6 Three consequences this plan must carry, not hide

**1. The offline build is not yet offline.** `plugins/fonts.js:280-282` throws on a cold cache with
no network. Until the woff2 files are vendored into `public/`, *"build the projection on a plane"* is
**false**. Either vendor the fonts or drop `next/font/google` from `app/layout.tsx:2`. **The plan
records this as work, not as done.**

**2. This gate widens the gap §5.9 and §8 row 4 already name.** `G-PROJ-01` is one more registered
gate id with zero rows in `evidence/gates.ndjson`.

**3. The projection publishes the defect.** The promoted `lib/uni-motor.js` double-counts ambiguity
in the EFE. **The EFE equation card must carry that defect as a visible chip in the projection, not a
corrected equation.** A projection that quietly prints the fixed formula while the promoted binary
computes the broken one **is exactly the truth laundering the contract forbids.**

### 6.9.7 The second-order point, said plainly

**A public projection is the strongest honesty check this project can build, and it is stronger than
any gate in this document.**

Every gate here is written by the same people who wrote the code. Every verifier shares a repository,
a vocabulary and a set of assumptions with the thing it verifies. `verify-public-projection.mjs`
included. **That is a real limit and no amount of mutation testing removes it.**

A stranger has none of those. A stranger with the bundle can `sha256sum` the artifact, read the key,
run `npm run science:verify`, and get a different number than the page shows — **and they have no
reason on earth to be gentle about it. That is not a risk of publishing. That is the product.**

The project already knows this about itself. It has an off-box witness with
`independent_custodians: 0`. It has 28 registered gates and zero rows in the canonical ledger. It has
a promoted binary with a wrong equation. **Every one of those was found from inside, which means
every one of them could have been missed from inside.** Publishing is the only mechanism in this
entire plan that recruits a checker who does not share the project's blind spots.

And it is what he actually asked for: *"It needs to be completely exposed and fully visible. Every
part and piece has to be in the user interface where the world can see it."*

---

# 7. THE WORK, ORDERED

## THE FIRST SHIPPABLE INCREMENT, NAMED PRECISELY

> ### **L-1 — ONE TREE, ONE LAB, MODE OFFLINE.**
>
> MAIN serves the 13-step living-science walkthrough at `/` in **both** build profiles, and the
> six-view, twelve-worksheet chalkboard at **`/lab/chalkboard` in the LAB build**, reached in one
> click from the map at `/lab`. The expected free energy is corrected and the correction is declared
> beside the legacy value. The twelve worksheets print, on paper, with a machine-written commit in
> the footer, from **every** tab. The kernel is sealed and the seal is proven by a mutation. No
> network. No chip dependency. No new mathematics.
>
> **The operator can open it, work it, print it, and take it on a plane.**
>
> Delivered at the end of **W3**, which now stands on **W2a** and **W2b** — the boundary and the
> shell — because a room needs a building. Everything in it already exists; it has just never been in
> one tree, and one line of it is wrong.
>
> > **Changed by §0.9 decision 3, and the change is load-bearing rather than cosmetic.** The draft
> > put the workbench at `/math-workbench`, a **product** route that ships to the chip. The
> > chalkboard is where you *work* the mathematics, so it is laboratory, and **L-1 no longer puts a
> > single new route into the release.** What the release serves at the end of W3 is exactly what it
> > serves today: the walkthrough at `/`. **The instrument grew; the shipped surface did not** —
> > and `release-excludes-lab` is green precisely because of that.

## 7.1 The ordered table

| # | Workstream | Depends on | Size | Trees touched |
|---|---|---|---|---|
| **W0** | Speak the adverse results; retract the two false documents | — | hours | docs |
| **W1** | Correct the EFE, keep the legacy value, gate it with an independent oracle | W0 | hours to 1d | MAIN |
| **W2** | Kernel/shell boundary; sealed-kernel test + mutation; widen the offline clause | — | 1-2d | MAIN |
| **W3** | **ONE TREE** — port workbench, `duration-models`, CSS tokens, `statusClass`, worksheet tests, print fixes | W1, W2 | 1-2d | MAIN |
| **W4** | `gate_runner --record` + `evidence/bench_runs.ndjson` | — | hours | UNI.Minecraft |
| **W5** | `lib/math/{units,expr,sockets,registry,render}` + parity test (EFE lands DISPUTED) | W3 | 3-5d | MAIN |
| **W6** | Worksheets as data + `@page` + Ctrl+P + machine-written provenance | W3, W5 | 2d | MAIN |
| **W7** | Bench record: f64 canonical, three digests, failing-first float test, `bench-run.mjs` | W2 | 3-5d | MAIN |
| **W8** | Elixir bench: `lib/sp/lab/bench.ex`, `mix sp.bench.run`, cross-engine golden fixture | W7 | 3-5d | UNI.Minecraft |
| **W9** | Observation channel: `channel.json`, `chip-observer-client.js`, broker (identity route only), read-only gate | W2 | 2-3d | MAIN |
| **W10** | **COMPARE identity gate + divergence record** — the first real finding | W7, W9 | 2-3d | MAIN |
| **W11** | Mode machine, two-column render, dwell-gated liveness honesty | W9, W10 | 2-3d | MAIN |
| **W12** | Numeric compare, frozen tolerance file, mutation gates, `verify_bench_parity.cjs` | W10, W11 | 3-5d | both |
| **W13** | `@teaches` + chalkboard generator + gate (lands covered/total) | W4 | 3-5d | UNI.Minecraft |
| **W14** | NEEDS YOU rail + `operator_decisions.ndjson` + plan-consistency clauses | — | 3-5d | UNI.Minecraft |
| **W15** | Disclosure ladder `equation-card.tsx` + `work-the-equation.tsx` + `freeEnergyAt` | W5 | 5d | MAIN |
| **W16** | Proof parser + derivation renderer + 8 committed derivation JSONs | W5, W15 | 5-10d + hand authoring | both |
| **W17** | Casebook (H1/H2/H3) + gate; extend `theGap()` to all four id spaces | W4 | 3-5d | UNI.Minecraft |
| **W18** | Intake ledger, schema, annotation, hooks, gate, wing | W13 | 5d | both (**operator co-sign for `git config`**) |
| **W19** | **THE DOOR** — `release.ex`, `release_room.exs`, airlock desk, `verify_release_room.cjs`, retroactive record of the live deployment | W7, W12 | 5d | UNI.Minecraft |
| **W20** | Deploy artifacts: `deploy.sh`, `rollback.sh`, `Containerfile`, two quadlets, MAIN CI | W19 | 5d | both (**operator S2**) |
| **W21** | `tree_digest` (git-free identity) + `verify_chip_tree_digest.cjs` (`ci:false`) | W7 | 2d | UNI.Minecraft |

**Added by §0, and it comes before everything except W0:**

| # | Workstream | First file | Depends on | Size | Trees |
|---|---|---|---|---|---|
| **W2a** | **THE SURFACE BOUNDARY** — the `UNI_SURFACE` smoke test, the `app/(product)` / `app/(lab)` move, `pageExtensions`, `verify-release-excludes-lab.mjs` + its **three** mutations, `experiments/product-routes.v1.json`, the registry shim | `UNI-FLAGELLUM/scripts/verify-release-excludes-lab.mjs` **(new)** | W0 | 1-2d | both |
| **W2b** | **THE SHELL** (§3A) — `lib/shell/{wings,wing-state}.js`, the frozen snapshot + `freeze-wing-state.mjs`, `app/(lab)/layout.lab.tsx` + `lab-frame.tsx`, the map at `/lab`, the two manifest-driven levels below it, movement, the place key | `UNI-FLAGELLUM/lib/shell/wings.js` **(new)** | **W2a** | **3-5d** | MAIN |

**W2b is THE FRONT DOOR and it was missing from this table entirely** (§0.9 decision 1). **Nothing
that renders a room may precede it**, because §3A.10 criterion 3 asserts the frame is on every lab
route. Its 3–5d bracket is an estimate anchored to seven new files, ten behavioural criteria and five
mutations, in the same spirit as §7.1a's sizes — **no comparable work has been timed in these
repositories.**

### 7.1a The wings, ordered — W22 split into nine

*Replaces the single row `| **W22** | The wings: … | long tail |`, which hid roughly as much work as
W0 through W21 combined.* Six wings, one frame they all stand on, and **the two hand-written JS
mirrors lifted out as their own workstreams** — because a mirror is a cross-engine parity problem,
not rendering work.

| # | Workstream | First file | Depends on | Size | Trees |
|---|---|---|---|---|---|
| **W22** | **THE WING FRAME** — the tri-mode banner, the offline badge and the wing gate, wrapping **the one manifest-driven wing route W2b built** (§0.9 decision 2). W22 no longer creates routes. | `app/(lab)/lab/wing/[wing]/layout.lab.tsx` **(new)** | **W2a, W2b, W4** | **2-3d** | MAIN |
| **W23** | **MIRROR-SPLAB** — JS mirror of the 6 SP.Lab physics modules + the 24-check harness, with a frozen tolerance and a mutation gate | `lib/kernel/mirrors/splab.js` **(new)** | W22, W7 | **4-6d** | both |
| **W24** | **W-PLANET** — the planetary bench. First non-flagellum wing; proves the pattern on another body | `app/(lab)/lab/wing/[wing]/panels/planet.tsx` **(new)** | W23, W15 | **5-7d** | both |
| **W25** | **W-GATE** — coverage map, the control-plane chain, the Room corridor; `theGap()` extended | `viewer/lab/coverage.cjs` **(new, a computation)** + `app/(lab)/lab/wing/[wing]/panels/gate.tsx` **(new)**; edits `viewer/lab/desk.cjs:646-674` | W22, W17 | **3-5d** | both |
| **W26** | **W-GENOME** — the digital-DNA bench. Pure, ports cleanly, needs no mirror workstream | `lib/kernel/mirrors/genome.js` **(new)** | W22 | **4-6d** | both |
| **W27** | **W-PARITY** — cross-study, science gates, oracles, semantic suite. **Report-only offline** | `app/(lab)/lab/wing/[wing]/panels/parity.tsx` **(new)** | W22, W25 | **5-8d** | both |
| **W28** | **MIRROR-BRAIN** — JS mirror of `math`+`infer`+`efe` (**328** of 9,420 lines) with **three-way** parity JS / Elixir / NumPy | `lib/kernel/mirrors/brain.js` **(new)** | W22, W7 | **6-9d** | both |
| **W29** | **W-COLONY** — the chip-side active-inference bench | `app/(lab)/lab/wing/[wing]/panels/colony.tsx` **(new)** | W28 | **5-8d** | both |
| **W30** | **W-HAIF** — the hierarchical bench. **Report-only offline.** Opens by closing the gate-state blocker | `hierarchical-aif/ledgers/h-aif-gates.json` **(new)** | W22 | **4-6d** | MAIN |

**Total: 38–58 days.** That is what "long tail" was hiding. It is roughly as much work as W0 through
W21 combined, **and it should be visible as such before anybody commits to it.** *(Day sizes are
estimates anchored to measured line counts — 328 lines for the brain mirror, ~508 + a 225-line
harness for SP.Lab, 30 gate verdicts for W-PARITY. **No comparable work has been timed in these
repositories.**)*

**Every "(new)" is verified new.** `ls viewer/lab/wings` returns *No such file or directory*;
`ls hierarchical-aif/ledgers/h-aif-gates.json` the same. The three wings that previously named no
first file — **W-COLONY, W-GENOME, W-PARITY** — now name one each, and each is honestly new.

**Why this order.** **W-PLANET is early and it is the right call:** cheapest complete wing, not the
flagellum, and its bench run already exists with a committed capture to check against. If the wing
pattern does not work on SP.Lab it will not work anywhere, and we find that out on day nine instead
of day forty. **W-GATE at W25 rather than last**, because it is "mostly exists; three additions" and
it is the wing that teaches the operator to read a gate row — the S4 path he has to walk himself.
**The two mirrors are separated from their wings on purpose:** W23 must be green before W24's OFFLINE
tab is reachable, and W28 before W29's. If a mirror slips, the wing above it can still ship
report-only rather than slipping with it.

### 7.1b Three more recorders and the stepper

| # | Workstream | First file | Depends on | Size | Trees |
|---|---|---|---|---|---|
| **W31** | **THE STEPPER** — `stepWorldTraced`/`stepAgentTraced`, `lib/kernel/f64.js`, the `advance()` extraction, `app/(lab)/lab/stepper/page.lab.tsx`, the tick tape | `lib/kernel/f64.js` **(new)** | W2, W3, W2a | 3-5d | MAIN |
| **W32** | **Test-run recorder** — `scripts/test-record.mjs`, `viewer/record_test_run.cjs`, `evidence/test_runs.ndjson` in **each** tree | `UNI-FLAGELLUM/scripts/test-record.mjs` **(new)** | — | hours | both |
| **W33** | **Receipts index** — `viewer/receipts.cjs` + a read-only `/receipts` route + `receipts-index-cannot-drift` | `UNI.Minecraft/viewer/receipts.cjs` **(new)** | W4 | 1d | UNI.Minecraft |

> **Naming collision, resolved and recorded.** Two authors independently proposed W23/W24/W25. The
> wings block keeps them (it is larger and internally cross-linked through the offline column's
> †W23/†W26/†W28 markers); the stepper, test recorder and receipts index moved to **W31/W32/W33**.
> **No existing workstream id changed.** The public projection's criterion is **W23a** for the same
> reason.

## 7.2 The workstreams that must not be reordered

**Seven** hard dependencies, each because getting it wrong produces a green suite over a broken
claim:

1. **W2 before W9.** The offline clause covers 3 of 9 files today. Add a network module first and
   the first bench panel that talks to the chip passes a green suite.
2. **W10's identity gate before W12's numeric compare.** Build the numbers first and the
   instrument's first act is the lie it exists to prevent: showing the operator numbers from a
   different program and calling them the same lab.
3. **W7's failing-first float test before W8.** Write the Elixir side first and the shipped
   `canonical/1` float trap is baked into the schema.
4. **W1 before W5's registry.** The registry test is the *detector*; the EFE fix is the
   *correction*. Both are needed, but the correction to a live production equation cannot wait on a
   five-day symbolic-spine build.
5. **W23 and W28 before their wings — W24 and W29 respectively.** A mirror that renders before it is
   gated is a second implementation of the same physics with nothing comparing them, **which is worse
   than no offline mode at all.** Build the mirror as a *parity problem with a mutation gate*, prove
   the gate bites, and only then let a wing draw from it. **This is the same law as W10 before W12,
   applied to Elixir instead of Python.**
6. **W22 before every wing.** Six wings inventing six route conventions against a lab server whose
   entire POST surface is one exact pathname (`lab_server.cjs:107`,
   `POST_ALLOWED = new Set(["/api/lab/run"])`, with `verify_lab_l5.cjs` already asserting that set has
   exactly one member) is how the second carve-out gets added. Build the frame, register it, and let
   the L5 gate keep holding the line.
7. **`lib/kernel/f64.js` is written ONCE, by whichever of W31 and W7 lands first, and consumed by the
   other.** The Stepper's changed-highlight and the bench record's `answer_digest` must use one float
   canonicaliser, **or the instrument reports a change in one surface and no change in the other on
   the same bytes.** Build it twice and the first cross-engine diff argues with the first tick tape.

**And two that precede all seven, in this order:**

**W2a before any wing and before any lab route.** The release-exclusion gate must exist and its
mutation must go red **before `app/(lab)/` contains anything worth excluding** (§0.8).

**W2b before anything that renders a room — including W3.** §3A.10 criterion 3 asserts the frame is
on **every** lab route, so a room built before the shell fails that criterion the moment the shell
lands, and a room built before `lib/shell/wings.js` exists has no manifest entry, which fails
criterion 6 in the other direction. **This is the same law as W22-before-every-wing, applied one
level up:** build the frame, register it, then let rooms stand inside it. It also decides where the
chalkboard's route comes from — W3 authors `app/(lab)/lab/chalkboard/page.lab.tsx` **into an existing
lab layout**, never alongside a missing one.

## 7.3 Acceptance criteria — behavioural, per workstream

**W0.** The operator has heard, spoken and in this order: (a) the wrong EFE is live on the chip;
(b) the deployment cannot be rebuilt; (c) production dependency risk regressed 0 -> 3 HIGH. And
`docs/THE-LABORATORY-PLAN.md:88-92` and `docs/control-plane/workspace.dsl:42` are corrected in a
commit whose message names the retraction. `docs/control-plane/generated/` re-rendered via
`render.sh`. **The "five zero-byte SVGs" criterion is DELETED — it was an acceptance criterion for a
defect that does not exist (§10.0 correction 2).** It is replaced by a real one: an
artifact-presence check asserts `statSync(p).size > 0` for every file under
`docs/control-plane/generated/` — **a byte size, never a line count** — and its mutation truncates
one file to 0 bytes and asserts the check FAILS. **And `docs/THE-LABORATORY-PLAN.md` gains a
RETRACTED banner at its head naming this document as its replacement**, in the same commit.

**W1.** `lib/uni-motor.js` returns **both** `efeLegacy = risk + ambiguity - informationGain +
effort` (unchanged, preserved as the plan's `EFE_UNIMOTOR_LEGACY_V1`) and
`efe = risk - informationGain + effort`. `tests/semantic/efe-canonical-oracle.semantic.test.mjs`
computes `KL[q(o)||C] + ambiguity + effort` from the posterior **without importing `policyTerms`**
and asserts `=== agent.efe` to 1e-12 and `efeLegacy - efe === ambiguity` to 1e-12. **It must fail on
the current tree first.** `docs/SCIENCE.md:83`, the EFE equation card and worksheet 5 are updated in
the same commit. **Known consequence: the closed-loop trajectory changes; any pinned trajectory
fixture is regenerated and the regeneration is recorded.**

**W2.** Injecting `fetch(` into a copy of any kernel file makes `kernel-is-sealed` FAIL; removing it
makes it PASS. The whole-tree `fetch(` census returns exactly one file. `npm run experiment:run`
still reproduces `runId faa689de...` byte-for-byte after `node:crypto` is removed — **or the failure
is diagnosed as a runtime-identity finding, not papered over.**

**W3 — the first shippable increment.** `npm run build` succeeds and `/` serves the walkthrough **in
both profiles**. `UNI_SURFACE=lab` build: **`/lab/chalkboard` serves six views and prints twelve
worksheets**; release build: **`/lab/chalkboard` does not resolve, and `verify-release-excludes-lab`
stays GREEN** — the chalkboard is laboratory (§0.9 decision 3) and it is reached from the map, never
from a typed address. Server-rendering the worksheets view yields **one `workbook-page` article per
entry in `lib/worksheets/registry.js` and twelve `workbook-line` divs in each — counts read from the
registry, not transcribed** (today that is 12 and 144), and the footer contains a **40-hex commit**. **Ctrl+P prints the workbook from every tab.** `NOT_SUPPORTED` renders in the
failure colour, not green (`statusClass` exact-match on a frozen allow-list, fixed **before** any
status string becomes `NOT_SUPPORTED`). `tests/globals-css-vars.test.mjs` asserts every `var(--name)`
reference is a subset of every `--name:` declaration — **red on the merged CSS until the four tokens
are declared, then green.** `tests/duration-models.test.mjs` proves the two copies of the duration
mathematics agree to 1e-12. Do **not** port the STALE `app/page.tsx` redirect, and do **not** drag
the STALE `CLAUDE.md`/`README.md` across — copy by content, never by merge; **the STALE worktree is
dirty in SIX places, not four** — ` M CLAUDE.md`, ` M README.md`, ` M docs/LIVING-SCIENCE-WALKTHROUGH.md`,
`?? docs/MATH-WORKBENCH.md`, `?? docs/UNI-STACK-BUILDER-PLAN.md`, `?? docs/audit/PHASE-E-WORKBENCH-AUDIT.md`
— **all six user-owned**, and it must be read from, never written to. **And port
`app/globals.css:696-702`, the workbook print block, or the twelve worksheets print as screen
chrome.**

**W4.** `node viewer/gate_runner.cjs --record` appends exactly one row per run gate and changes no
other file. Two runs produce a diffable history. A clause asserts `bench_runs.ndjson` and
`gates.ndjson` share no field name but `utc`.

**W5.** `tests/math-registry.test.mjs` **fails on EFE** and passes on the other five v1 entries.
`requireSame(NAT, JOULE)` throws with the authored message. `evaluate` on an unbound symbol throws
rather than returning NaN, and the 4096 budget demonstrably bites. `tests/sockets.test.mjs` passes.
**The no-eval source scan is extended to `lib/math/**` in the same change that creates it** — the
existing prohibition is scoped to `lib/stack/**` and `app/stack-builder/**`, neither of which
exists, so a new directory without it is an unguarded hole in a rule already written down.

**W6.** Deleting one worksheet tuple fails the count assertion. The printed footer's third field is
a real commit, not underscores. `@page` is present and the print `.workbook-page` padding is zero.

**W7.** `benchRecord(q,e,x,a).question_id` is unchanged when `engine` changes. `bench-record.test.mjs`
FAILS against a `JSON.stringify` canonicaliser and PASSES against the f64-hex one. `bench-run.mjs`
run twice yields records differing **only** in `execution.*` timing. The run token is minted inside
`run()` and spent once — **reusing `desk.cjs:405-415,580-585`, not a second scheme.**

**W8.** Flipping one float's last mantissa bit in the JS-produced golden fixture fails
`test/sp/lab/bench_record_test.exs`. `SP.ControlPlane.Run` gains `question_id` **additively** —
`run_id` unchanged and all five existing `run_*` test files untouched
(`run_identity_determinism_test.exs` is the tripwire).

**W9.** `curl` from a non-loopback Host is refused. Deleting an entry from `channel.json` while a
call site still names it turns the semantic test red. Inserting `os_exec` into a temp copy of the
broker makes `broker-is-read-only.test.mjs` fail. `/api/chip/units` renders
`REFUSED_BY_ALLOWLIST` for the flagellum units **rather than routing around the refusal.**

**W10.** Two records with different `question_id` produce `NOT_COMPARABLE` and **zero numeric
comparisons execute**, asserted by a call counter. **And the live one: running COMPARE against the
chip as it stands produces a `NOT_COMPARABLE` divergence record for `HELDOUT_ANALYSIS` naming
`b757971e...` vs `85a4a2e9...`, and an `AGREE` for `AGENT_STEP`. If it produces anything else, the
instrument is wrong, not the fleet.**

**W11.** **The airplane test:** with every interface down and the broker not running, the build
passes, all 13 walkthrough steps render, the agent loop runs, and the worksheet print view renders.
A cold boot matches `/NOT PROBED/` and does not match `/UNREACHABLE/`. Feeding a probe result with
`ageMs = 360000` renders the stale class **with an age in the string**; removing the age from the
render fails the test. With the probe failing, the chip column's value is `null` and no offline value
appears in it; wiring the offline value into the chip column fails the test.

**W12.** Perturbing one float's last mantissa bit in the on-chip record flips the diff
`IDENTICAL -> DIVERGENT`. **Leaving a tolerance in swallows the mutation — that is the falsifier and
it must fail the gate.** `tolerance-is-frozen.test.mjs` refuses a loosened budget against
`git show HEAD~1:experiments/compare-tolerance.v1.json`.

**W13.** Editing any `bites_by` line number by one makes `verify_chalkboard.cjs` exit 1. The gate
reports `covered/total` and goes red only on a regression until all 28 are authored.

**W14.** Pressing HOLD appends a row and the card moves to "answered — HOLD" with his words shown
back. `verify_plan_consistency.cjs` exits 1 when a step's status is flipped off `OPERATOR` with no
decision row. **BOTH** of `track_server.cjs`'s self-descriptions — `:11` (*"every route except POST
/api/comment is a pure read"*) and `:25` (*"the ONLY thing it writes is
evidence/track_comments.ndjson"*) — are corrected **in the same commit** that adds the second write
route; a test asserts neither sentence survives. `:18` (*"this server owns NOTHING"*) is reviewed in
the same change.

**W15.** RUN is absent until a prediction is recorded. Dragging the simplex changes F, and a
deliberately mismatched registry entry shows `REGISTRY DIVERGENCE`. The falsifier button reports a
minimum gap and states whether the falsifier fired. Identical tag+class paths at all three detail
levels.

**W16.** `parse_proof.cjs` parses 8/8 for sections and `dimensional_analysis.md` fully to `steps`,
with a golden test per file. Seeding a units mismatch into a derivation JSON makes the renderer draw
`UNIT BREAK`. Every proof card carries its `domain` label. **Both evidence vocabularies render side
by side, labelled by origin; no mapping is performed.**

**W17.** `generate_casebook.cjs` produces at least 13 cases from the plan alone on the first run.
`verify_casebook.cjs` exits 1 when any `verbatim` string is altered by one character. H3 reports
`0 cases` rather than guessing. `theGap()` reports **95** foreign identifiers, not 28.

**W18.** `git commit` of a new file under `data/` with no `@intake` block is refused, naming the
file and pasting the skeleton. `verify_intake.cjs` exits 1 on an edited row, an altered hook, and
the OBSERVED-with-derivation mutation.

**W19.** With a missing execution receipt the room refuses at clean-to-sterile, **writes nothing,
and the ledger gains zero entries.** Two agent keys are refused with the module's own words. Green
to sterile is refused. **The ledger is byte-unchanged after every refusal.** And the first
successful run is the **retroactive record of the existing deployment**, not a new one.

**W20.** A deploy followed by a landing check that re-hashes every shipped file through the MCP
matches `manifest.json`; flipping one byte in `dist/` after `execution.json` is written makes
`Room.exit/2` refuse. **If it does not refuse, the pipeline is theatre.**

**W21.** `identity()` returns a non-null `tree_digest` in a directory with **no `.git`**, and
`verify_build_identity.cjs` still passes unchanged.

**W2a — THE SURFACE BOUNDARY.** `UNI_SURFACE=lab npm run build` against a throwaway
`app/(lab)/smoke/page.lab.tsx` serves it at `/lab/smoke`; the release build does not. Then
`vinext build --prerender-all` emits `dist/server/vinext-prerender.json` for **both** profiles — **if
it does not, the gate exits `MANIFEST_ABSENT` and §0.4a's link-walk fallback runs instead, and the
gate says which path it took in its own output.** `verify-release-excludes-lab.mjs` then passes all
six assertions of §0.4, and **all three mutations turn it RED, each naming a route**:
**X1** — writing `app/(product)/math-workbench/page.tsx`, a laboratory surface at a product path —
**is the one that matters**, because it is the mutation the previous specification passed. **If X1
comes back green the gate is decoration and the runner must report `VACUOUS`, not `PASS`.**
`experiments/product-routes.v1.json` is authored in this same commit and contains exactly the routes
`app/(product)/` emits today. All twelve assertions of `tests/rendered-html.test.mjs:20-31` still
pass at `/` unchanged, and `tests/walkthrough.test.mjs:116` is the only line edited.

**W2b — THE SHELL.** §3A.10's ten behavioural criteria, in full, are this workstream's acceptance.
The five that carry it, each with the mutation that proves it bites:

1. **Every manifest entry has a room, and the tile count is READ FROM THE MANIFEST.** Rendering
   `/lab` yields exactly `WINGS.length + STANDING.length + PORTALS.length` tiles. **Adding a wing to
   `lib/shell/wings.js` without creating its route turns the suite red; adding one *with* its route
   leaves this criterion green** — a correct run cannot fail its own gate, which the draft's
   transcribed "fourteen" could.
2. **The frame is on every lab route.** Render every manifest route; assert the WHERE, MODE, LEVEL,
   CHIP, NEEDS YOU and CASEBOOK slots are in the server-rendered HTML. **Mutation: delete
   `<LabFrame>` from `app/(lab)/layout.lab.tsx` → every one goes red at once.** *(This criterion is
   why W2b is second: any room built before it exists fails here the moment it lands.)*
3. **`not_probed` draws nothing.** With `chip.probed_at = null`, **no liveness element exists in the
   DOM at all** — not `hidden`, not `aria-disabled`, absent. **Mutation: emit a grey dot for
   `not_probed` → exits 1.** This is the mutation that proves F26 bites in this codebase.
4. **The FAIL count on the front door is read, not typed.** It equals the count computed from the two
   committed reports. Point `freeze-wing-state.mjs` at a **copy** with one `FAIL` edited to `PASS`,
   rebuild the snapshot, re-render: **the map must move by exactly one.** A number that does not move
   is a number somebody typed.
5. **No hidden rooms, and the withdrawn rows stay withdrawn.** Walk `app/(lab)/**/page.lab.tsx` on
   disk, map each to a route, assert set-equality with the manifest. Adding
   `app/(lab)/secret/page.lab.tsx` exits 1; so does a manifest entry with no file. **And the specific
   regression this pass exists to prevent: creating `app/(lab)/lab/bench/page.lab.tsx` or
   `app/(lab)/lab/classroom/page.lab.tsx` — the two rows §0.9 decision 2 withdrew — exits 1, because
   neither is in the manifest.**

Plus the operator's criterion at the head of §3A.10, performed by him, with no terminal: **reach
every body of mathematics in at most two clicks from `/lab`, read MODE, LEVEL and the chip line in
every room without scrolling, and come back with one key and with the browser's Back button.**

**W22 — THE WING FRAME.** With the frame serving, `GET /lab/wing/<id>` — **the one manifest-driven
route, built by W2b** — for a wing whose manifest declares `offline: report_only` renders the
**NOT_RUNNABLE_OFFLINE** banner and the OFFLINE tab is not clickable. Flip that one manifest field to `offline: full`, reload, and the banner changes and
the tab activates — **no other edit.** Delete a wing's manifest entry and the wings verifier FAILS
naming the orphaned route. `POST` to any wing route returns 405, and `verify_lab_l5.cjs`'s assertion
that `POST_ALLOWED` has exactly one member **still passes** — the wings add no second carve-out.
Registered in `viewer/gate_registry.json`, which the runner cross-checks against filesystem
discovery, so a gate file on disk and absent from the registry fails the run.

**W23 — MIRROR-SPLAB.** `mix sp.lab.report --out lab/evidence/captures/lab_report.json` (a new task
beside the existing 33-line `sp.lab.validate.ex`) and `lib/kernel/mirrors/splab.js` independently
produce all **24** check values. `verify_splab_mirror.cjs` compares them under a frozen tolerance file
and PASSES. **Then the mutation:** change `G` in the mirror from `6.674e-11` to `6.675e-11` and the
gate FAILS naming `g_surface` and the measured delta; revert and it PASSES. **And the fence:** while
that gate is RED the wing **refuses to render its OFFLINE tab at all** — it does not render stale
numbers with a warning, it refuses. **Ships with `test/sp/lab/validate_test.exs` and
`test/sp/lab/planetary_data_test.exs`, the two absences §5.4 names**, because the mirror is being
gated against a harness that nothing currently guards.

**W24 — W-PLANET.** The check table is rendered by iterating the loaded report; the header reads
`N checks, M failed` where **N is the array length at render time.** A test adds a twenty-fifth check
to `SP.Lab.Validate.build_checks/0` in a throwaway worktree — the wing renders 25 rows and the header
reads 25, **with no edit to any wing file.** Any wing source containing `23` or `24` as a check-count
literal fails the gate. Separately, the gate re-emits the report and byte-compares it to
`lab/evidence/captures/lab_validate_report.txt`: **it is RED on the current tree** at the Nernst
label (`validate.ex:160` vs capture index 13), **and it goes green when the capture is regenerated —
never by widening a tolerance.** And the teaching object: dragging the *calibrate-on* slider from
`earth` to `venus` changes the failure count on screen, and the number comes from `model_compare`
running, not from a table.

**W25 — W-GATE.** `theGap()` returns, all computed: `foreign_id_spaces: 4`, `foreign_ids: 95`,
`ledger_names: 109`, `exact_intersection: 0`, `glob_covered: 34`, `uncovered_ledger_names: 75`.
Adding a fabricated row to a **copy** of `gates.ndjson` whose `name` equals a registry `gate_row`
moves `exact_intersection` from 0 to 1. And **the prose at `desk.cjs:668-672` is replaced by a
computed field** — `sealed_branch_reachable_for` — which returns `["hud"]` on the current tree,
because `canRun('hud')` returns `SEALED_BY_S10` and `canRun('gaia')` does not.

**W26 — W-GENOME.** The plan editor makes an invalid plan **unreachable, not rejected**: a test
drives its reducer with a transition that would produce an organ without its prerequisite, and the
reducer returns the prior state rather than rendering an error. And: 40 metabolism ticks in the
browser for a fixed action sequence yield the same death tick as
`mix test test/sp/brain/metabolism_test.exs` computes for the same sequence; change `upkeep` from
`0.04` to `0.05` in the JS and the death tick moves **and the parity gate FAILS.**

**W27 — W-PARITY.** All 30 verdicts (14 G + 16 X) render from the two frozen reports.
**`X01_SOURCE_INTEGRITY` renders with its PASS struck through and finding E-B01 printed beside it,
driven by a computed check** — `declaredArtifacts > 0 && presentOnDisk === 0` — so if
`experiments/upstream-cache/` is ever populated the strike-through disappears with no edit. The
lattice: the wing enumerates 2¹³ = 8192 configurations in the browser and its computed `Z` matches
`lattice_distribution` in the frozen report to the declared tolerance; set the ring to 14 sites and
the enumeration doubles and the wing still agrees with an independently computed `Z`. **That
sub-panel carries an OFFLINE badge; every other panel carries NOT_RUNNABLE_OFFLINE, and the gate
fails if any panel carries the wrong one.**

**W28 — MIRROR-BRAIN.** **Three-way.** One fixed seed and one fixed model produce a policy posterior
from (a) `lib/kernel/mirrors/brain.js` in the browser, (b) `mix sp.brain.trace`, (c)
`python uni/brain/active_inference.py` (280 lines). The gate PASSES only when **all three** agree to
the frozen tolerance. **The mutation is the best one in the plan:** change `ln_matvec` in the mirror
from `(ln B)s` to `ln(B·s)` — the convention `math.ex` flags bound-critical and which today lives in
one docstring — and the gate FAILS **naming which of the three diverged and by how much.** Revert,
PASS. **A convention that consequential should be provable by breaking it, not by reading about it.**

**W29 — W-COLONY.** With the novelty term gated off the wing renders it as exactly `0` and the saved
model bytes are unchanged; toggling it on changes `G(π)` on screen **and** makes the byte-identity
check report a difference — **so the operator sees what the gate costs.** And one tick unrolled:
editing a single `A`-matrix cell in the browser changes the posterior, and applying the same edit to
`mix sp.brain.trace` changes its output the same way.

**W30 — W-HAIF.** **The blocker first.** `hierarchical-aif/ledgers/h-aif-gates.json` holds nine
records keyed `H-AIF-G1` … `H-AIF-G9` — **the ids actually used at
`hierarchical-aif/docs/H-AIF-GATES.md:9-17`** (verified on disk this session; `docs/H-AIF-GATES.md`
in MAIN does **not** exist, and a builder following the old citation gets ENOENT). **The acceptance
criterion below reads the ids out of the table at run time and never transcribes them, so the short
forms cannot be used by accident.** A new test parses the markdown table
and the JSON and FAILS if either drifts: edit G5's status in the markdown alone from `IN PROGRESS` to
`COMPLETE` and the test goes red. Then the wing: Lmotor-2 renders as an empty slot **with its reason
read from `hierarchy.py`'s docstring at render time**, so deleting that docstring changes what the
operator sees — **the fence cannot be quietly removed while the picture stays the same.**

**W31 — THE STEPPER.** See §4.10's AC-S1 … AC-S7. The two that carry it: **AC-S2**, a 64-tick
hand-stepped session and a headless `bench-run.mjs` of the same `RunSpec` produce the **same
`question_id` and the same `answer_digest`** — if they differ, the Stepper is a second implementation
and is **deleted, not reconciled**; and **AC-S3**, flipping the last mantissa bit of `bRun[0][0]`
lights the `qState(RUN)` changed-highlight and changes `answer_digest` — **a decimal-comparing
highlight fails this.**

**W32 — TEST-RUN RECORDER.** `npm run test:record` twice yields two rows with identical
`tests`/`pass` and differing `wall_ms`. **Break one assertion in a scratch copy: the row still
appends, with `fail >= 1` and `exit != 0`.** **A recorder that only records green runs is worse than
no recorder, and that is the falsifier.** Re-hashing `output_path` reproduces `output_sha256`.
`npm test` itself is **not touched**, so no existing gate moves.

**W33 — RECEIPTS INDEX.** Adding a file to `docs/receipts/` and not regenerating makes
`verify_receipts_index.cjs` exit 1. Changing one byte inside an indexed receipt makes it exit 1.
`/receipts` lists **136** entries and states *"UNI-FLAGELLUM: 0 receipts — its evidence is under
`hierarchical-aif/reports/` and `docs/audit/`"* rather than omitting the tree. **Every `gate_row` a
receipt claims either resolves in the registry or is listed as unresolved, by name** — because a
receipt that cites a gate that does not exist is the fabricated-citation failure mode, and here it
becomes a gate failure.

## 7.4 EVERY DECLARED ROUTE HAS EXACTLY ONE OWNER — reconciled against §0.3

**The second audit found that §0.3 declared ten routes and §7 scheduled only some of them.** This
table is the reconciliation. **It is not decoration: `viewer/verify_plan_consistency.cjs` already
exists to catch this document carrying two answers at once, and this table is the shape it can
check.** A route in §0.3 with no row here, or a row here naming a workstream absent from §7.1/§7.1a,
is a plan defect.

| route | file | owned by | scheduled in |
|---|---|---|---|
| `/lab` | `app/(lab)/lab/page.lab.tsx` | **W2b** | §7.1 |
| `/lab/wing/<wing>` | `app/(lab)/lab/wing/[wing]/page.lab.tsx` | **W2b** (route) · **W22** (frame) · one panel module per wing: **W24 W25 W26 W27 W29 W30** | §7.1, §7.1a |
| `/lab/wing/<wing>/<room>` | `app/(lab)/lab/wing/[wing]/[room]/page.lab.tsx` | **W2b** | §7.1 |
| `/lab/chalkboard` | `app/(lab)/lab/chalkboard/page.lab.tsx` | **W3** (route + port) · **W5 W6 W15** (contents) | §7.1 |
| `/lab/proof`, `/lab/proof/<id>` | `app/(lab)/lab/proof/{page,[id]/page}.lab.tsx` | **W16** | §7.1 |
| `/lab/stepper` | `app/(lab)/lab/stepper/page.lab.tsx` | **W31** | §7.1b |
| `/lab/compare` | `app/(lab)/lab/compare/page.lab.tsx` | **W11** | §7.1 |
| `/lab/intake` | `app/(lab)/lab/intake/page.lab.tsx` | **W18** | §7.1 |
| `/lab/casebook` | `app/(lab)/lab/casebook/page.lab.tsx` | **W17** | §7.1 |
| `/lab/airlock` | `app/(lab)/lab/airlock/page.lab.tsx` | **W19** | §7.1 |
| `/api/chip` | `app/(lab)/api/chip/route.lab.ts` | **W9** | §7.1 |
| *(layout)* | `app/(lab)/layout.lab.tsx`, `app/(lab)/lab-frame.tsx` | **W2b** | §7.1 |
| *(layout)* | `app/(lab)/lab/wing/[wing]/layout.lab.tsx` | **W22** | §7.1a |

**`NOT_SCHEDULED`, with reasons — neither is a gap, both were contradictions:**

| declared route | status | reason |
|---|---|---|
| `/lab/bench`, `/lab/bench/<wing>` | **WITHDRAWN** | A second route convention for the same wing. §0.9 decision 2. |
| `/lab/classroom` | **NOT_SCHEDULED** | §3.6: *"fold into L5, do not build a new room."* The classroom is `/lab/l5` on `127.0.0.1:8103`, linked as a portal. |
| `/math-workbench` | **WITHDRAWN as a MAIN route** | §0.9 decision 3 — it is the chalkboard and the chalkboard is laboratory. It survives only as the **address the chip serves today**, which §0.9 decision 3 records as the live consequence and §8 row 6 holds. |
| `/lab/l0` … `/lab/l6` | **EXTERNAL** | Chip-side, `127.0.0.1:8103`, already built and gated (`lab-l0` … `lab-l6`). Reached as portals under §3A.8's liveness rules; **not** re-implemented in MAIN. |

**Every route above is in the `(lab)` group. That is the point of §0.9 decision 3: after this pass
the plan schedules ZERO new product routes, so `app/(product)/` is exactly the eight files §0.3
moves and nothing else — which is the set `experiments/product-routes.v1.json` freezes and §0.4
assertion 4 enforces.**

---

# 8. WHAT IS THE OPERATOR'S, NOT THE AGENT'S

**Seventeen things. Every one of them is a decision, not a task. An agent that performs any of these
without his co-sign has substituted itself for him.**

| # | What | Why it is his | Stop |
|---|---|---|---|
| 1 | **The off-box witness key.** node2 accepts the writer's key; `independent_custodians: 0`. The anchor stands on git alone — tamper-evident, **not** unforgeable. | Removing that key is **the one repair an agent must not perform.** | **S1** |
| 2 | **The OBS WebSocket on `127.0.0.1:4455` has no authentication.** | A host security posture change. | **S2** |
| 3 | **Widening the chip's systemd allowlist** so `uni-flag-prod.service` and `uni-flag-test.service` are readable. | A chip security posture change. The design renders `REFUSED_BY_ALLOWLIST`; it must never route around it via `os_exec`. | **S2** |
| 4 | **Authoring rows in `evidence/gates.ndjson`.** 95 foreign gate identifiers, 109 ledger names, intersection zero — and this plan adds at least six more registered gates to that gap. | The ledger is the project's word. | **S4** |
| 5 | **Reconciling the four truth/evidence vocabularies** (MAIN's 4, the chip's 6, the proofs' A-X, the gate schema's A/B/C/Sec/pending). | Any automatic mapping is truth laundering. The bench record must REFUSE a class outside the intersection until he rules. | **S5** |
| 6 | **The three commits on `feature/scientific-math-workbench` that are not on MAIN** — and, **added by §0.9 decision 3, what the chip serves.** Any "promote MAIN to the chip" overwrites `c23f686` and with it the **only** twelve printable worksheets and the **only** six-view workbench that exist anywhere. **And the deployment as it stands serves a LABORATORY surface as product:** the chip's `app/page.tsx` is sha256 `00c1e47ebc778602…` — measured this session to be byte-identical to STALE's 542-byte `redirect("/math-workbench")` — so `/` does not serve the product at all, it redirects into the chalkboard, which §0.9 decision 3 classifies as laboratory. | Merge or explicitly abandon the branch; **and rule on the deployment: either the first release across the Door serves `app/(product)/page.tsx` at `/` and stops serving the chalkboard, or the chip is declared a LAB deployment and says so on its own surface. It may not do neither** — and option (a) costs a real user the twelve worksheets on the chip, which is why it is his. Both before any release crosses the Door. | — |
| 7 | **`git config core.hooksPath .githooks`** in both repositories. | A repository configuration change, adjacent to S5. Propose and co-sign; do not perform. | — |
| 8 | **The `next@16.2.12` decision.** The advertised fix for the 3 HIGH production advisories installs a version outside the declared range. | A release-scope decision, not a patch. | — |
| 9 | **Is the laboratory public — and if so, what exactly?** **Recommended answer: YES, publish the frozen static projection (§6.9), read-only, at a public address, with NO authentication — and take the live app down in the same act.** Today `workbench.uni-lab.solwright.com` answers `307` → `/math-workbench` → `200` with **no authentication**, serving a **live stale branch** (`c23f686`) whose promoted `lib/uni-motor.js` **double-counts ambiguity in the EFE**. **Correction to §9.1:** measured this session, that name resolves via the LAN DNS server (`Linksys00425`, `10.190.245.188`) to **`10.190.245.121`** — the chip's **private RFC1918** address. Plain `curl` from this box **failed** (exit 35, `CRYPT_E_NO_REVOCATION_CHECK`); only `--ssl-no-revoke` succeeded. **Whether it is reachable from outside the LAN is NOT ESTABLISHED.** The phrase *"over the public internet"* is **withdrawn**. **Why no authentication:** the contract forbids **accounts** (`CLAUDE.md:69-72`); a read-only static bundle has nothing to protect and nothing to mutate; and auth on a public science projection defeats its only purpose. **What he accepts by saying yes:** every number becomes checkable by strangers — **including the wrong ones**, specifically the EFE defect, `independent_custodians: 0`, and 28 registered gates with zero ledger rows, all of which the projection is **required** to display; and a permanent public URL becomes a permanent obligation to keep honest. **What stays private regardless:** every act surface in §6.9.1's table — the bench record, the intake desk, the decision rail, the broker, the airlock — all still `127.0.0.1`. | A disclosure decision and a security posture change, and the projection publishes the project's own adverse results under his name. | **S2** |
| 10 | **`experiments/compare-tolerance.v1.json`** — the tolerance class and budget per subject. | A tolerance chosen after seeing a diff is not a tolerance. Author it before the first compare run. | — |
| 11 | **Minting any presence token** (`viewer/.presence/token.json`). | F31: the guard is `presence_evident`, **not** unforgeable. | **S6** |
| 12 | **Tracking `C:/Users/mpolz/Documents/UNI-Flagellum/CLAUDE.md`**, which is in no git repository, so no hook, gate, diff or CI run can ever catch it drifting. | A repository-layout decision. This plan records it as a standing hazard; it does not fix it. | — |
| 13 | **Naming.** "L-1", "W-FLAG", "the bench run record", "the airlock desk" — every name in this document is a proposal. | Naming is his. | — |
| 14 | **Whether COMPARE mode ever executes on the chip (v2).** v1 is designed to be complete and useful without it. | Executing a subject on the chip is a mutation and needs his co-sign; going further and gating it behind the Room is his call. | — |
| 15 | **THE SURFACE DECISION ITSELF (§0), and the two questions inside it.** (a) Is `app/(product)` / `app/(lab)` in one MAIN application the laboratory? (b) Is `app/chatgpt-auth.ts` **moved** to `app/(lab)/` or **deleted**? — nothing imports it and the product forbids accounts, so deleting is the honest move and moving is the conservative one. **The agent recommends move now, delete at the next release, and is asking rather than choosing.** (c) Is `/lab` the front door with the 8103 rooms linked from inside it, or do the rooms stand alone? | Architecture is principal-gated. It sets which surface is the face of the project and what a release may contain. **Reversible in hours today; a rewrite of §4 and §5 after the first wing merges.** | — |
| 16 | **Wiring the two git-tracked hooks in `UNI.Minecraft/.claude/hooks/`** — `fe_touch_needs_verdict.py` and `no_percent_scoring.py` — **which are installed and unwired, so neither has ever fired.** No settings file reachable from this box declares a `hooks` block, and the hook's own fallback write path `logs/ship_gate_bypass.log` does not exist. | A change to harness configuration. **A wired `fe_touch_needs_verdict.py` produces the first record in this project written by something other than the agent it constrains.** See §3.1 row 11. | — |
| 17 | **The `UNI_SURFACE` / `cross-env` question on Windows.** `UNI_SURFACE=lab vinext build` is POSIX syntax and does not set the variable in PowerShell or cmd. | A dependency addition to `package.json` in the same commit as the boundary. Untested; flag rather than guess. | — |

**And one thing that is emphatically NOT his to be asked about again:** the offline clause amendment.
The first draft of this plan asked for it. **It is retracted (section 1). No work here is blocked on
that signature.**

---

# 9. MEASURED FACTS THIS PLAN RESTS ON

Every number below was produced by a command run during the measuring passes. Where two lenses
disagreed, the row says so and **§10.0 carries the settled correction; §10.1 carries only what is
still open.**

## 9.0 METHODOLOGY — stated once, and every count downstream inherits it

**LINES = (count of `0x0A` bytes) + (1 if the file is non-empty and its last byte is not `0x0A`).**
That is what an editor's gutter shows.

Three ways to get this wrong, **all three of which happened in this project**:

- **`wc -l` counts NEWLINE CHARACTERS, not lines.** A file with no trailing newline reports one
  fewer than it has. A file with **no newline at all reports 0 — even at 175 KB.** That single
  confusion is the entire source of the retracted "five empty SVGs" defect, and the entire source of
  the 501-vs-493 disagreement over `lab/proofs/` (all eight files lack a trailing newline, so `wc -l`
  loses exactly one per file).
- **`String.split("\n").length` OVER-counts by one** on any file that ends with a newline — the same
  error with the opposite sign. It reported `validate.ex` as 226 lines when it is 225.
- **NEVER size a file with a line count.** Use `statSync().size` / raw byte length. Byte size and
  line count answer different questions and one is not a proxy for the other.

**On absence claims:** every "does not exist" in this document names the search that establishes it
and its exit status. **Two of the three CRITICAL findings against the previous draft were false
absence claims.**

**Trees.** MAIN `.../UNI-FLAGELLUM` (HEAD `4f6485e`, clean, ahead 1), STALE
`.../UNI-FLAGELLUM-math-workbench` (HEAD `c23f686`, **six dirty entries**), CHIP-SIDE
`.../UNI.Minecraft`. **A fourth checkout exists at `C:/Users/mpolz/Documents/UNI.Architect/UNI-FLAGELLUM`
and is outside every count in this document** — worth knowing before anyone globs `Documents/**`.

## 9.1 The chip

| fact | evidence |
|---|---|
| `/opt/uni/flagellum/{prod,test}` exist; `PROMOTE_STATUS = PROMOTED`; `BUILD_STATUS = REBUILD_DONE`; `src.tgz` 3,819,835 B | `mcp__uni-lab__os_file_list` + `os_file_read` |
| prod `lib/uni-motor.js` sha256 `852b38d14e1de9e1baae9bda7c37fb2426911fb1b04b4f594d026373d4b50313` = **both local trees** | `os_file_read` + local sha256 |
| prod `app/page.tsx` sha256 `00c1e47ebc7786024d3efd6555843b05734cbfb76e7e08daa0799bec900fde3a` = **STALE**, the redirect file | same |
| prod `lib/observed-experiment.js` sha256 `85a4a2e96b348f5977bfc1b9045d2736ea2f7865b53f7eb830a8738476296169` (19,286 B) vs MAIN `b757971e1f207899ddac0b262241822552a06abc5272407b14b21fd98ddbe623` (22,328 B) | same |
| chip carries `lib/duration-models.js` (4346 B); **MAIN does not have the file at all** | `os_file_list`; `find` in MAIN returns zero |
| nginx vhost sha256 `f8d99f48f5279a7bd0992445c33ba01a702031d06368d6d333b636a3e768adb8`, added 2026-07-20, 443 -> `127.0.0.1:8791` | `os_file_read /etc/uni/uni-flag-workbench.conf` |
| `https://workbench.uni-lab.solwright.com/` -> `307` -> `/math-workbench` -> `200`; **no `access-control-*` header with an Origin** — **RE-MEASURED 2026-07-29: plain `curl` FAILS (exit 35, schannel `CRYPT_E_NO_REVOCATION_CHECK` 0x80092012); `--ssl-no-revoke` gives `307` -> `200` with `remote_ip` **10.190.245.121** (private RFC1918, resolved via LAN DNS `Linksys00425` at 10.190.245.188). **Public-internet reachability NOT ESTABLISHED**; the phrase "over the public internet" is withdrawn.** | `curl` / `curl --ssl-no-revoke -w "%{http_code} %{remote_ip}"` / `nslookup` from this box |
| chip probe 2026-07-29: hostname `uni-lab`, **up 13d 13:39**, load 7.62, 39 GiB RAM; `/opt/uni/flagellum/` holds exactly `test/` and `prod/`; `PROMOTE_STATUS` = `PROMOTED\n`, sha256 `537f3f73efdab7fa…`; `prod/src/` is a full Next.js tree | `os_sysinfo`, `os_file_list`, `os_file_read` |
| **SERVING is NOT ESTABLISHED.** `os_systemctl_status` refused `flagellum-prod.service` as outside the MCP allowlist (correct refusal, class `Sec`); `podman_ps` showed **no flagellum container** in a truncated tail | `os_systemctl_status`, `podman_ps` |
| `viewer/infra_registry.json` = **21 services, 4 boxes** (`uni-lab`, `thinker`, `node2`, `tab`); substring search FALSE for **all** of `8790`, `8791`, `flagellum`, `Flagellum`, `8102`, `8103`, `5858`, `8104`. **Stale with respect to the deployment, not evidence of its absence.** | node substring search |
| `uni-flag-prod.service` / `uni-flag-test.service` / `uni-flagellum.service` all **refused, not in allowlist** | `os_systemctl_status` x3 |
| chip LAN **10.190.245.121** (eno4), wg0 10.13.13.1, tailscale0 100.100.188.48, up 13d 12:28 | `os_sysinfo` |
| **`/opt/uni/flagellum/prod/src/.git` -> "not a directory"** | `os_file_list` |
| MCP fleet: `uni-lab` 10.13.13.1 (local), `uni-lab-79740c` 10.13.13.3, `uni-tab-arm-1` 10.13.13.5; instrument 2.6.0 | `limbs_list` |
| `lab_call` reaches **`uni-biological-builder`** on `127.0.0.1:8000` — not the flagellum, not SP.Lab | `lab_health` |

## 9.2 The trees

| fact | evidence |
|---|---|
| MAIN HEAD `4f6485e91d444bdbe35bb47e82ffe9d01ac5ec45`, branch `hierarchical-aif/motor-stack`, clean, ahead 1 | `git status -sb`, `git log -1` |
| STALE HEAD `c23f686b641ad74d3cfdc8c64295c4c437b47209`, branch `feature/scientific-math-workbench`, 2026-07-20 23:29 | same |
| **`git merge-base --is-ancestor c23f686 HEAD` -> NO**; 74 commits on MAIN not on the chip, 3 on the chip not on MAIN; merge base `4fcba6cad57c8df0bce3214fcaaf25b485d74281` | `git rev-list --count`, `git merge-base` |
| UNI.Minecraft HEAD `73553d8347f7770e415761ee56fe6468690519ce`, branch `gen2-runtime`, one modified file (`evidence/track_comments.ndjson`) | `git log -1`, `git status -sb` |
| MAIN 7 lab components = **2202** lines (uni-flagellum-lab 880, living-science-walkthrough 337, biological-stage 319, observed-experiment-panel 232, cross-study-parity-panel 187, science-gates-panel 130, guided-teacher 117); all `app/*.tsx` = 2234 (adds layout 20, page 12) | `wc -l app/*.tsx` |
| MAIN `lib/` = 8 files: observed-experiment 500, walkthrough 472, uni-motor 420, cad 144, walkthrough.d.ts 115, uni-motor.d.ts 115, source-first-passage 77, cad.d.ts 32 | `find lib -type f` + `wc -l` |
| `tests/walkthrough.test.mjs:115` names exactly **3 files**; `:119` is the network regex; `:41` pins `LIVE_INSTRUMENT -> OBSERVED` | file read |
| MAIN kernels: **zero** `Math.random`, **zero** network tokens; exactly three ambient clocks — `uni-motor.js:408`, `walkthrough.js:385`, `:408` | grep over `lib/*.js` |
| `lib/observed-experiment.js:1` `import crypto from "node:crypto"`, used once at `:498` | file read |
| seeded, not random: `seededRandom` `:210`, keyed from `protocol.uncertainty.seed` `:331` | file read |
| `experiments/results/audit-manifest.json` is CURRENT — all five recorded sha256 values recompute against disk today | node recompute |
| committed report: `runId faa689defbf804948312388b3d26fe5f10b6d938780ca2e31f1fb48514486f6a`, protocol `UNI-FLAGELLUM-OBS-001`, seed 20260717, 2000 replicates | node read |
| **MAIN has no `.github/`** — no CI of any kind | `ls .github` -> No such file or directory |
| **`experiments/upstream-cache/` does not exist**; `cross-study:verify-raw` BLOCKED | `ls` |
| MAIN runtime deps are exactly four: `drizzle-orm`, `next 16.2.6`, `react 19.2.6`, `react-dom 19.2.6`. **No charting library.** Every curve must be hand-drawn on a 2D canvas | `package.json` |
| `npm run lint` **PASS**, exit 0, zero diagnostics | `npx eslint .` run this session |
| `npm run science:verify` **PASS**, exit 0; holdoutIntervals 244; mean log score `-3.8380834245644038` | run this session |
| `npm run cross-study:verify` **PASS**, exit 0; `failures: []`; ito LOBO RMSE `0.8293641328245378`; lattice SSE `0.04976772774792293`; RFT RMSE `1.7274106879853608`; 10 audit artifacts | run this session |
| `npm audit --omit=dev --audit-level=moderate` -> **3 HIGH on three packages** — `next`, `postcss`, `sharp` — metadata `{high:3, total:3}`, all three `fixAvailable: next@16.2.12` (`isSemVerMajor:false`), exit 1 | run this session, `--json` |
| `npm audit` (all) -> **19: 1 low, 4 moderate, 14 high**, exit 1 | run this session |
| Phase-E recorded **0 production, 13 total, 8 high** on 2026-07-21 | `docs/audit/PHASE-E-WORKBENCH-AUDIT.md:36-37` |
| node v25.0.0, npm 11.6.2, python 3.12.10, Elixir 1.19.5 / OTP 28 (erts-16.3.1); `package.json` engines `node >=22.13.0` | version commands |
| **No git hooks anywhere** — 14 `.sample` files in each repo, no `core.hooksPath`, no `.githooks/` | `ls -la .git/hooks` |
| **`C:/Users/mpolz/Documents/UNI-Flagellum/.git` does not exist** | `ls -la` |

## 9.3 The gate system and the control plane

| fact | evidence |
|---|---|
| `viewer/gate_registry.json` = **28** gates, 25 `ci:true`, 3 `ci:false`; every entry has an `id` and a `gate_row` | node parse |
| registry complete against filesystem discovery: 28 discovered, 28 listed, 0 either way | `discoverGateFiles()` executed |
| `evidence/gates.ndjson` = **206 rows / 109 unique names**; all rows PASS 122, PENDING 69, PARTIAL 12, FAIL 3; latest-per-name PASS 92, PARTIAL 4, PENDING 12, FAIL 1 | node parse |
| **all 206 rows schema-conformant; all 206 `receipt_path` values exist on disk** | node check |
| **intersection of registry ids with ledger names = 0; of `gate_row` values = 0; of `G00_SOURCE_IDENTITY`…`G13_…` = 0; of `X01_SOURCE_INTEGRITY`…`X16_…` = 0; of `H-AIF-G1`…`H-AIF-G9` = 0. Union of 95 foreign ids: 0.** Re-measured with the **real** id strings read from `.gates[].id` and from `hierarchical-aif/docs/H-AIF-GATES.md:9-17`. **The short forms `G00..G13`/`X01..X16`/`G1..G9` are nowhere an *id*, but they DO occur as display labels and prose** — `app/science-gates-panel.tsx:84,90,96`, `experiments/cross-study-preregistration.v1.json:139`, `experiments/results/cross-study-parity-report.json:735`, `UNI.Minecraft/lib/sp/brain/genome.ex:687`, `.../mc.ex:152` — so a grep for a short form tests nothing (§5.9). **Refinement: 2 of the 28 `gate_row` values are globs covering 34 of the 109 ledger names by prefix; the other 26 are exact and match 0; 75 of 109 are covered by nothing.** | node set operations |
| **`canRun('hud')` EXECUTED → `SEALED_BY_S10`, `sealed_by: [hud-boot-persistent, hud-integration-stage-0, hud-renders-stale-as-stale]`; `canRun('gaia')` → `allowed: true`; `canRun('overlays')` and `canRun('colony')` → `NEEDS_THE_WORLD`.** So `desk.cjs:668-672`'s "UNREACHABLE for every registered gate" is **measurably false** — reachable for exactly 1 of 28. | node |
| `desk.theGap()` executed: 28 registered, 0 in the ledger, 28 absent, 2 globs, 25 runnable here | node |
| `evidence/gate_attempts.ndjson` = 1 header + 59 rows; 59/59 resolve into ledger names, **0/59 into registry ids** | node |
| `evidence/control_plane/ledger.ndjson` = **32 entries** (banner says 31); `anchor.json` head `b90b7498...`, length 32; last entry `4.6/L6` carries a `not_a_verdict` field | node parse |
| ledger transition vocabulary: `phase.executed` 20, `build.completed` 7, `account.ingested` 2, `evidence.superseded` 1, `record.corrected` 1, `proof.observed` 1. **Neither `room.entered` nor `room.exited` appears once.** | node tally |
| `phase9_plan.json` = 7 stages, **43 steps**: DONE 31, BLOCKED 1, IN_PROGRESS 1, PLANNED 8, OPERATOR 2; 10 stops, 6 not_mine, 8 proof methods, 6 proof artifacts, 7 status words | node walk |
| **`SP.ControlPlane.Room` has zero production callers** — only `room.ex` itself, one docstring line at `command.ex:19`, and test files | grep over `lib/ scripts/ runs/ test/` |
| **`SP.ControlPlane.Run` has zero production callers** likewise | grep |
| `gate_runner.cjs` writes **nothing** — only `readFileSync`/`readdirSync`/`existsSync`; verdicts exist only in the exit code and the terminal | file read |
| `viewer/infra_registry.json` = 21 services, containing **no 8102, no 8103, no 5858** | node |
| `viewer/lab/` contains **zero mathematics** — grep for `gravity|escape_velocity|nernst|ozone|flagell|torque|PMF|stator` over every `.html` and `.cjs` returns nothing | grep |
| **`runs/pureworld_qa_gate.exs` (91 lines) declares `@scaffold` at `:28` and raises at `:39`** (`:40` is the first heredoc line) | grep |
| UNI.Minecraft: 133 `.ex` files / 22,748 lines; `lib/sp/brain/` 46 files / 9420; `lib/sp/lab/` 733 across 7 modules (+ `lib/sp/lab.ex` 77); **`lib/sp/control_plane/` = 17 `.ex` files / 3,439 lines** (16 top-level + `command/writ.ex` 26; the sibling `lib/sp/control_plane.ex` 44 is outside the directory). **"3963" is withdrawn.** | `find` + line count |
| `test/sp/lab/` has **5** files and 26 `test "` blocks; **no `validate_test.exs`, no `planetary_data_test.exs`** | `ls` + grep |
| correction language, **with the pattern stated**: subject line matching `-Ei "fix\|correct\|retract\|revert\|repair\|amend\|withdraw\|honest\|false\|wrong\|stale\|drift\|defect\|refute\|undermine"` = **192 of 689** (MAIN 37/113, CHIP-SIDE 155/576); same pattern over the full message = 505 of 689. **The previously circulated "278 of 689" (201+77) reproduces under no pattern and is withdrawn.** | `git log --pretty=%s \| grep -Eci`, six variants run |
| `@limitation` machinery live: 9 limitations across 7 files, 0 duplicates, 0 incomplete, 9 with a proof field | `scan()` executed |
| **Measured cross-engine float divergence:** Elixir `:erlang.float_to_binary(1.0,[:short])` -> `"1.0"`; JS `String(1.0)` -> `"1"`. `Ledger.canonical/1` uses that function at `ledger.ex:199` | both run side by side |
| C1 RED test records 418 of 4000 `**` evaluations differing by 1 ULP between V8 12.4 and 14.1, at `observed-experiment.js:178`; report digests `a485fa5a...` (Node 25) vs `d1753d25...` (Node 22.13.1) | `tests/red/c1-...:13-22`, `tests/red/README.md` |

---

# 10. EXPLICITLY UNVERIFIED

**A plan that hides its own gaps is the failure it exists to correct.**

## 10.0 CORRECTIONS AGAINST DISK — settled by measurement, not left open

**Three claims in the previous draft were false, and the worst of them was manufactured by a line
count.** The five "zero-byte SVGs" are 568 KB of valid SVG. The word `derivation` appears 243 times,
not once. `science-gates-report.json` says 4 PASS, and it says so in its own summary field, **so the
draft's 6 contradicted the artifact it cited.** Everything else below is arithmetic, and on the
line-count disputes the critics were right nine times out of ten.

**Every count here uses the convention stated at §9.0.**

| # | claim as written | measured | corrected where |
|---|---|---|---|
| **1** | *"The word `derivation` appears **once** in all three trees and it describes an exit code"* | **243 occurrences in 140 files** (MAIN 111 / STALE 44 / CHIP-SIDE 88; `--no-ignore-vcs` 251/146; whole-word 151; **code files only, exactly 50**). **Zero in either `app/` tree** (`rg` exits 1). | §4 opening |
| **2** | **CRITICAL — RETRACTED.** *"5 zero-byte SVGs … They are empty files … regenerate or delete"* | **27,277 / 86,854 / 130,131 / 149,042 / 175,183 B = 568,487 B total.** Each begins `<svg xmlns=…>` and ends `</g></g></svg>`. Each contains **zero newline bytes**, which is why `wc -l` reports 0. **Nothing needed regenerating or deleting.** An engineer following the draft would have deleted 568 KB of real diagrams. | §5.8 row, §7.3 W0 |
| **3** | `science-gates-report.json`: **6 PASS** of 14 | **4 PASS.** `G00_SOURCE_IDENTITY`, `G01_OBSERVATION_BOUNDARY`, `G02_FIRST_PASSAGE_MATH`, `G04_CENSORED_JOINT_LIKELIHOOD`. Plus 3 FAIL, 1 SOURCE_ONLY, 1 NOT_ESTABLISHED, 5 BLOCKED_EXTERNAL. **`summary.statusCounts` in the file says the same**, alongside `computationalGatesPassed: 4` of 7. | §5.2, §3A |
| **4** | `tests/semantic/` = 10 files, 3,653 lines | **11 files, 3,853 lines, 174,486 B.** Two files drop the `.semantic.` infix, so a glob on `*.semantic.test.mjs` **silently loses 1,466 lines of coverage**. | §5.0, §5.2 |
| **5** | `lab_server.cjs` `.then((observed)` at `:296` | **`:306`.** File is 383 lines, CRLF throughout. | §3.3 |
| **6** | `validate.ex` = **23** checks | **24 invocations** (25 `chk(` tokens minus the `defp chk/3` at `:217`), at `:98`…`:201`. **The harness prints `24 checks, 0 failed.` itself.** The old acceptance criterion *"23 of 23 PASS"* **would have failed on a correct run.** | §5.4, §7.3 W24 |
| **7** | `lib/sp/control_plane/` = 17 modules / **3,963** lines | **17 `.ex` files / 3,439 lines** (16 top-level + `command/writ.ex` 26). The sibling `lib/sp/control_plane.ex` (44) is **outside** the directory. | §5.0, §9.3 |
| **8** | gaia: collectors 1320, caps 416, sig 264 | **1380 / 424 / 294.** Critic right on all three. | §5.8 |
| **9a** | `desk.cjs` — draft carried **624 AND 680** | **679 lines / 34,967 B.** The draft's own internal check was sound: `theGap()` at `:646`, `module.exports` to `:678`, so 624 was impossible. **Quote the 34,967-byte figure where size, not length, is the point.** | §5.7, §5.9 |
| **9b** | `l5.html` **260** lines; a NUL byte is claimed | **289 lines / 15,088 B, one NUL at offset 13457, on line 249.** Confirmed. `grep -n` prints `Binary file … matches` and **suppresses all output**; `grep -a`/`rg -a` do not. **And it hides a real defect — see §5.10.** | §5.10 |
| **10** | STALE `git status -sb` = **four** entries | **Six**, all user-owned. | §7.3 W3 |
| **11** | "**278 of 689**" self-correcting commits | **Denominator CONFIRMED** (113 + 576; STALE's 42 excluded). **Numerator WITHDRAWN** — reproduces under no stated pattern. Replaced by a **stated** one: subject-line match = **192 of 689**; full message = 505. | §3.9, §9.3 |
| **12** | STALE `globals.css` print-media rules = **6** | **Two `@media print` blocks** (`:534-544`, 9 rules; `:696-702`, 5 rules), **14 rules total, zero `@page`.** MAIN's has **one** block and **no workbook rules at all — which is the real gap.** | §4.4 |
| **13** | `hierarchical-aif` = **66** `.md` | **67** `.md`, 64 `.py`, 1 `.html`. | §5.3 |
| **14** | `room.ex` — `conditions/2` in one place, `conditions/4` in three | **One definition, three arities.** `@spec` `:93`, `def … \\ %{}, \\ []` `:94`. **`room.ex` contradicts itself the same way** — `:20` says `/2`, `:105` says `/4`. **That inconsistency is in shipped source.** | §5.7 |
| **15** | `page.tsx:26-74` "loads" the JSON | **Imports are `:2-7`.** `:26-74` is the `observed={{…}}` prop object. **Citing the prop block points a builder at the wrong 48 lines.** | §4.4 |
| **16** | twelve worksheet tuples at `:389-401` | **`:390-401`**; the literal opens at `:389` and maps at `:402`. | §4.4, §5.1 |
| **17** | MAIN `package.json` `test` enumerates **16** files | **17 paths in TWO `node --test` invocations.** Saying "16" or "17" unqualified is how this stayed disputed; **name both invocations.** | §5.0, §3.3 |
| **18** | `lab/proofs/` — five spellings of the Equations heading | **Four spellings**, and **the eighth file has NO equations heading at all** (`ozone_photochemistry.md` uses `## The four Chapman reactions`). **Any parser keyed on "Equations" silently skips it.** 8 files, 501 lines, CHIP-SIDE only. | §4.6 |
| **19** | `viewer/lab/` total = **5,436** | **5,326** across 19 files. Critic right. | §5 opening, §0.5 |
| **20** | "**zero test coverage** for the workbench maths" | **FALSE.** `tests/math-workbench.test.mjs` exists — 91 lines, **5 tests**, second in STALE's `npm test`, executing the real calculators. **The claim narrows to the worksheet VIEW, where it is worse than it sounded:** the only workbook assertion anywhere is a **button label**. Deleting all twelve tuples leaves the suite green. | §4.4 defect 4 |
| **21** | pureworld scaffold raise at `:40` | **`:39`.** `:40` is the first heredoc line. | §5.8, §6.8, §9.3 |
| **22** | `track_server.cjs` self-description at `:11` **and** `:25` | **Two DIFFERENT sentences, not two copies of one.** `:11` is *"every route except POST /api/comment is a pure read"*; `:25` is *"the ONLY thing it writes is …"*. **A find-and-replace on one leaves the other.** `:18` is a third in the same family. | §3.7, §7.3 W14 |
| **23** | MAIN `app/` — "seven" in one place, "nine" in another | **9 `.tsx`, 2,234 lines**; two are shells, so the seven components total **2,202**. **Both numbers are right and neither is safe unqualified.** The 773 figure (3 files) is correct. | §9.2, §0.3 |
| **24** | `docs/receipts/` — count and tree | **CHIP-SIDE only.** 70 files + 2 subdirs at depth 1 (63 `.md`); **136 files / 72 `.md` recursively.** `ls` errors in MAIN and STALE. | §3.1 row 12, §3.9 |

**Where the critics were right and the draft was wrong:** items 3, 4, 5, 6, 7, 8, 9a, 9b, 10, 13, 16,
19, 21, 23 — **fourteen of twenty-four. On raw line counts the critics beat the draft every single
time.**

**Where both were wrong:** item 12 (2 print blocks, not 6 and not 5 — though 5 is the rule count of
the second block, so that critic measured a real thing and mislabelled it) and item 7's *file* count.
**Where a critic was imprecise:** item 22 (two sentences, not two copies) and item 1 (**50** is
reproducible only under an unstated code-file filter; the honest total is 243).

> **The two line-count disputes were the same bug with opposite signs.** `wc -l` under-counts a file
> with no trailing newline; `split("\n").length` over-counts one with a newline. `lab/proofs/`
> (501 vs 493) is the first; `validate.ex` (225 vs 226) is the second. Both dissolve under §9.0's
> counter — **and the SVG CRITICAL is the first one taken to its limit: 175 KB, and the tool said
> zero.**

## 10.1 Where the lenses STILL disagree — mark, do not resolve

**Nine of the thirteen former disagreements were settled by measurement and moved to §10.0.** What
remains is what nobody has closed.

| # | Disagreement | State | How to resolve |
|---|---|---|---|
| **D7** | SP.Lab size — **733 lines, 7 modules** (`lib/sp/lab/`) vs **810 lines, 8 modules** (adds `lib/sp/lab.ex`, 77) | **NOT a disagreement about disk — a disagreement about scope.** Both are right about different things. | **State the scope wherever the number appears.** The same trap sits in item 7's control-plane count. |
| **D12** | Does the chip's whole tree match `c23f686`? | One lens proved byte-identity for **one file** plus structural identity of `package.json`; another matched byte sizes across `lib/` plus two hashes. **Neither walked the whole tree.** The 2026-07-29 chip probe added `PROMOTE_STATUS` and one more file hash — **it did not walk the tree either.** | **The "chip runs the STALE worktree" claim rests on a handful of files, not a Merkle — and that gap is itself the argument for W21's `tree_digest`.** OPEN. |
| **D14** | Whether `workbench.uni-lab.solwright.com` is reachable from **outside this LAN** | This box's DNS resolves it to `10.190.245.121`, a private RFC1918 address, **so no probe from here can settle it.** | A request from a host with **no route to `10.190.245.0/24`**. **That probe was not run and must not be assumed either way.** |
| **D15** | Whether a **process** is serving the promoted chip bytes | **DEPLOYED and PROMOTED are certain. SERVING is NOT ESTABLISHED.** `os_systemctl_status` correctly refused the unit name (allowlist, class `Sec`); `podman_ps` showed no flagellum container in a truncated tail. | Requires **§8 row 3** — widening the chip's systemd allowlist, which is **S2, his**. The design renders `REFUSED_BY_ALLOWLIST` and **must never route around it via `os_exec`.** |
| **D16** | Whether the "50 occurrences of `derivation`" and "64 occurrences" figures can be reproduced | **50 reproduces** under an unstated code-file filter. **64 reproduces under NOTHING tried** — eleven variants were run; the nearest is 62. | The author naming the tree scope, the glob, and whether the count is occurrences, matching lines, or files. |

## 10.2 Not run, by any lens, this session

**Nothing below was executed. Every claim about it is read from source, from a report, or from the
banner — and the banner has already been measured wrong in at least three places (25 vs 28 gates,
31 vs 32 ledger entries, 191 vs 206 rows).**

- **`npm ci`, `npm test`, `npm run build`, `npx tsc --noEmit`** — all NOT RUN. Each mutates
  (`node_modules`, `dist/`, `tsconfig.tsbuildinfo`, and `tsconfig.json` sets `"incremental": true`).
  The last recorded result is the Phase-E audit's, on a different branch, eight days ago.
- **`npm run cross-study:verify-raw`** — NOT RUN, and **BLOCKED regardless**:
  `experiments/upstream-cache/` does not exist and the 4.09 GB `ito-2021-raw-data.zip` is absent.
- **`mix test`** — NOT RUN. The banner's "1043 tests, 0 failures" is unverified. Static counts only:
  139 `.exs` files, 1047 `test "` blocks, 3 doctest directives.
- **`mix sp.lab.validate`** — NOT RUN, **and no Elixir ran at all this session.** The **24** checks
  are established from (a) 24 `chk(` call sites counted in `validate.ex:98-201` and (b) the committed
  capture at `lab/evidence/captures/lab_validate_report.txt`, which prints `24 checks, 0 failed.`
  **The claim that the task currently runs GREEN rests on a capture dated 2026-07-13, not on a run
  anyone performed — and that capture has already drifted from the source at one of its 24 labels.**
  W23's first act should be to run it and receipt the run.
- **NO BUILD WAS EXECUTED**, so `dist/` does not exist locally and the release artifact was never
  observed. **§0's `pageExtensions` exclusion is verified by READING vinext's source** —
  `file-matcher.js:26-36` regex construction, `next-config.js:286,303` normalization, `cli.js:285`
  and `index.js:789` plumbing — **not by running it.** Specifically UNVERIFIED: that the compound
  extension `lab.tsx` survives `buildExtensionGlob` (`file-matcher.js:18-21`) emitting
  `page.{lab.tsx,tsx,ts,jsx,js}` into `fs.promises.glob`, and that the `@cloudflare/vite-plugin`
  client build honours the same exclusion as the router. **§0.8's thirty-minute smoke test closes
  this, and it is the single largest risk in §0.**
- **`vinext`'s static export was never run on this app.** §6.9.2 verified the code path **exists and
  is reachable** (`cli.js:269` → `staticExportApp`). RSC components, `next/font`, and the `throw`
  guard at `math-workbench/page.tsx:18-22` could each fail prerender. **The first build is the test,
  and W23a is written so that it is.**
- **Whether the worker harness in `tests/rendered-html.test.mjs` resolves routes other than `/`
  after `vinext build`.** The harness was read (`:4-13`); no build was run. **§3A.10 criteria 1, 2, 3
  and 9 all depend on it.** If it does not, those criteria move to a Playwright/jsdom harness and
  §3A's cost rises — **verify this FIRST, before writing any route.**
- **Whether `next/link` client-side navigation preserves `<LabFrame>` without remounting it** (and
  therefore without losing MODE/LEVEL). Not tested; if it remounts, MODE and LEVEL must be lifted
  into a client context provider rather than read per-page.
- **§4.5's A2 exercise** — that `kl` is identically zero and `vfe` identically `surprise` in this
  code path — is **derived algebraically from reading `uni-motor.js:270-278` and was NOT executed
  numerically.** It must be run before the audit worksheet ships, **because if it is wrong the
  exercise teaches a falsehood.**
- **§4.10's AC-S2 and AC-S3 have never been executed.** Neither `scripts/bench-run.mjs` nor any bench
  record exists yet (W7), so AC-S2 is a **prediction, not a measurement**. AC-S3's specific mutation
  was reasoned from the code, not run.
- **The end-to-end symptom of §5.10's NUL-sentinel mismatch.** The static evidence is unambiguous;
  **no server was started, no browser was driven, and the RESULT block was never observed failing to
  render.**
- **`node viewer/gate_runner.cjs`** — NOT RUN (it spawns 25 child processes and boots the BEAM). The
  banner's "23/23 law-consistent, 21 PASS, 2 legitimately RED" is unverified **and is arithmetically
  inconsistent with the 28-entry registry that WAS measured.**
- **`node viewer/lab/gauntlet.cjs`** and the six lab gates — NOT RUN.
- **`viewer/resonance_meter.cjs`** — NOT RUN. Its header was read; no verdict was produced.
- **`pytest hierarchical-aif/tests/`** — NOT RUN. 339 `def test_` counted statically.
- **The control-plane hash chain was NOT recomputed.** First and last entries were read and the
  `prev_hash`/`hash` fields observed. "Chain verifies" is the banner's claim.
- **`evidence/gates.ndjson`'s file digest was NOT computed.** Row and unique counts were parsed;
  the banner's `964ea25cfe8666ca...` is unverified.
- **The 34 objects in `evidence/control_plane/objects/` were counted, not retrieved**, and no
  object's name was verified to equal its content hash.
- **The 250 files in `hierarchical-aif/reports/frozen-evidence-baseline.sha256` were NOT re-hashed.**
- **No server was started.** Whether TRACK (8102), Gaia (8096), HUD (8100) or the lab (8103) is
  listening right now is unverified. Only that 8104 has no listener on this box, and that
  `workbench.uni-lab.solwright.com` answered.

## 10.3 Asserted from reading, not from measurement

- **The EFE inflation magnitudes.** `G` inflated 60.7-62.5%; `G(RUN) - G(TUMBLE)` inflated 6.5x
  (0.030642 vs 0.004678); the policy posterior moving `[0.495322, 0.504678]` to
  `[0.469397, 0.530603]`. **These are read from `PHASE-E-WORKBENCH-AUDIT.md:150-158` and were NOT
  re-executed by any lens, in any session.** The **algebra** — that `efe` reduces to
  `KL(qOutcome ‖ preferences) + 2·ambiguity + effort`, and that the doubled term does **not** cancel
  between RUN and TUMBLE because `ambiguity` derives from each policy's **own** transition matrix —
  **was verified by direct reading of both the local file and the promoted file on the chip.**
  **The magnitudes were not. They remain UNVERIFIED and must not be quoted as measured.**
- **Whether `BIT_IDENTICAL` holds for browser V8 vs same-major node V8.** Reasoned from IEEE-754
  and shared V8 transcendentals. **No browser was driven.** If it is false, the tolerance file must
  be authored at `ENGINE_ONLY` from the start rather than tightened to `BIT_IDENTICAL` and quietly
  loosened — which `tolerance-is-frozen.test.mjs` would refuse anyway, so getting this wrong on day
  one is expensive.
- **Whether `build_identity.cjs` returns a null `boot_git_commit` on the chip.** The chip tree has
  no `.git` (measured) and the code path returning null on `statSync` failure was read (measured).
  **The conclusion is a code-reading inference; the module was not executed there.**
- **Whether the uni-flag containers are RUNNING.** `/run/*.cid` exist and `podman logs` returns rc 0
  for both names, and the vhost answered `200`. **No lens issued an HTTP request to `127.0.0.1:8791`
  directly, and the truncated `podman_ps` tail did not show either container.**
- **The quadlet unit names behind the two containers.** Inferred from the `/run/*.cid` convention
  every other unit on that box uses. `os_systemctl_status` refused all three guesses.
  **UNVERIFIED.**
- **Whether the chip serves the wrong EFE in its BUILT bundle.** `lib/uni-motor.js` on the chip was
  hashed (measured). **`dist/` was not.** So: the source it is built from carries the defect;
  whether the served JavaScript does was not established.
- **Whether `runId faa689de...` is reproducible on this box's Node v25.0.0.** The committed value
  was read. `npm run experiment:run` was not executed. **W2's acceptance criterion may fail for
  runtime-identity reasons rather than because the hash swap was wrong — that must be diagnosed as a
  finding, not papered over.**
- **Whether the workbench compiles against MAIN's tsconfig**, and whether MAIN's 544-line
  `globals.css` contains the `workbench-*` classes the component uses. STALE's is 702 lines — 158
  more — and the inference that the delta *is* the workbench styling is an inference, **not a diff**.
  *(What IS measured: MAIN uses 18 `var()` names and declares 18; STALE uses 23 and declares 18. The
  token sets were not diffed line by line.)*
- **`app/globals.css:680-683`** is cited twice as "the 4 screen rules" for the workbook. **The two
  `@media print` blocks were measured; the `:680-683` screen-rule citation was not.** STALE's file is
  702 lines so the range exists; its content is unchecked.
- **Whether the five SVGs in `docs/control-plane/generated/` are CURRENT with respect to
  `workspace.dsl`.** §10.0 correction 2 establishes they are **non-empty and valid**. It does **not**
  establish they are up to date — *"stale but non-empty"* remains possible and is a different,
  unmeasured claim from the one retracted.
- **Whether STALE `app/math-workbench/page.tsx`'s six imported JSON reports exist in MAIN at the same
  paths** — they must, because under §0.9 decision 3 those imports move to
  `app/(lab)/lab/chalkboard/page.lab.tsx` in MAIN. One lens said all six exist in MAIN (verified); another flagged it as unchecked.
  Re-verify before W3, because W6's provenance footer has a second blocker if they do not.
- **Whether `experiments/results/observed-experiment-report.json`'s `analysisCodeSha256` pin is
  stale** (audit E-M06 claims `b757971e...` against a current `85a4a2e9...`). NOT re-hashed.
- **The three commits on the chip's branch that are absent from MAIN.** The **count** was measured
  (`git rev-list --count HEAD..c23f686` = 3). **The commits were not read.** Whether they contain
  anything beyond the workbench is unknown — and item 6 of section 8 turns on it.
- **`lib/cad.js` purity.** One lens read it (144 lines, gear train, `theta = scale.ln(odds)`,
  falsifier at `:56`); another explicitly marked it unread. It appeared in **no** grep hit for
  network, `Math.random` or `node:crypto`, but it is imported by `app/uni-flagellum-lab.tsx:19` and
  deserves one direct read before it enters `lib/kernel/`.
- **Whether the port pairing 8790/8791 is right.** `:8791` was read from the vhost (measured) and
  `/run/uni-flag-test.cid` exists (measured). **No file naming 8790 was opened.** The pairing comes
  from architecture docs and memory.
- **Effort estimates.** "Roughly a day" for hand-authoring 32 Term objects; "30-55 step objects";
  "~200 lines" for `parse_proof.cjs`; **every size in §7.1, §7.1a and §7.1b, including the 38–58 day
  wings total.** **Nothing was timed, and no comparable work has ever been timed in these
  repositories.** These are judgement. So are the chosen sizes in §3A and §4.10: the 900-tick ring
  buffer, the ~20-line `f64.js`, the 22 px comfortable-density minimum and the WCAG AAA contrast
  target.
- **Whether reversing §0 after the wings are built really costs "a full rewrite of §4 and §5".**
  A judgement. **What IS measured is the premise:** `viewer/lab/` has no React (`grep -rli` returns
  nothing) and no build script (`viewer/package.json`), so React components cannot be ported there
  without re-authoring.
- **Whether the 13-site lattice enumeration actually reproduces the frozen `lattice_distribution`.**
  Only that 2¹³ = 8192 is trivially enumerable in JavaScript — which is what makes §5.0's `‡` badge
  *structurally* possible. **Whether the numbers agree is W27's job to establish, and it could
  falsify that badge.**
- **The exact NEEDS YOU count and CASEBOOK count §3A.5's frame will display.** §3.7 states the
  deduplicated union was never computed by any lens and must not be typed; §3.9 predicts "at least
  13" casebook cases. **Both frame slots therefore ship showing an em dash until their generators
  run — never a placeholder number.**
- **Whether the two `.claude` hooks have EVER run on any machine.** What is measured is that **no
  settings file reachable from this box declares a `hooks` block**, and that the fallback write path
  `logs/ship_gate_bypass.log` does not exist. A hooks block could exist on another machine or in a
  managed settings path not inspected.
- **Whether the chip promotion transport copies `app/` wholesale.** `/opt/uni/flagellum/prod/src/app/`
  was not enumerated, so the statement that `chatgpt-auth.ts` *"would be carried by any tree-level
  tarball promotion"* is **an inference from the transport method, not an observation of that file on
  the chip.**
- **Whether `experiments/results/*.json` in MAIN are byte-identical to the copies inside the chip's
  promoted `/opt/uni/flagellum/prod/src/`.** Not compared. **If they diverge, §3A.4's map numbers
  describe the lab's copy, not the chip's, and the tile must say so.**
- **Whether the resonance lattice's seven layer names (ROOT, FLOW, WILL, HEART, VOICE, SIGHT, CROWN)
  are exactly as written in `viewer/resonance.cjs`.** The two files' line counts were measured (437,
  257); **the layer names were taken from the draft, not from the source.**
- **`UNI_SURFACE` on Windows.** `UNI_SURFACE=lab vinext build` is POSIX syntax and **will not set the
  variable in PowerShell or cmd.** Whether `cross-env` or an equivalent is the right answer was **not
  tested** (§8 row 17).
- **Whether `dist/` is git-ignored in MAIN** was measured (`/dist/` at `.gitignore:42`), but **whether the
  projection output directory `dist/public-projection/` collides with anything else in `dist/`** was
  not.
- **Whether `experiments/upstream-cache/` does not exist** — carried forward from an earlier lens;
  the search was **not re-run** this session. §7.3 W27's E-B01 render turns on it.
- **The `f64` hex values in section 2's example JSON are illustrative placeholders written by hand.**
  Any implementation must derive them and **never copy them**.
- **The deduplicated NEEDS-YOU count.** Its four inputs are each measured; **the union was not
  computed by any lens.** The code must compute it. No number is stated here.

## 10.3a WHAT THE RECONCILIATION PASS COULD NOT SETTLE WITHOUT INVENTING DESIGN

**Four contradictions were settled and propagated (§0.9). Five things surfaced during that
propagation that are NOT settled, and each is written down here rather than decided quietly.**

1. **`vinext build --prerender-all` has never been run on this project.** §0.4 assertion 1 depends on
   `dist/server/vinext-prerender.json` existing. The file's writer, path and shape were all read on
   disk this session (`run-prerender.js:83,176-180`; `prerender.js:789-816`; the
   `prerenderAll || output==="export"` condition at `cli.js:268-269`) — **but no build was executed,
   here or in any earlier pass.** If the flag fails on a dynamic route, §0.4a's link-walk fallback
   runs and is **strictly weaker**: it cannot see a route nothing links to. **This is now the joint
   largest risk in §0 alongside the compound-extension question, and both are closed by the same
   thirty-minute smoke test.**
2. **`experiments/product-routes.v1.json` has no author yet.** §0.4 assertion 4 freezes the product
   route set, and W2a authors it. **Its initial contents are trivially derivable — `/` and nothing
   else, because MAIN's `app/` contains exactly one `page.tsx` (measured: 11 files, one of them
   `app/page.tsx`)** — but whether widening it is an operator co-sign or an ordinary reviewable edit
   is **not decided here.** §8 row 15 is where it would go if it is his.
3. **§3A.10 criterion 2's depth rule is ambiguous in its own words.** It says *"Depth is two below
   `/lab`… Adding a fourth path segment exits 1"*, while §3A.4's worked example `/lab/wing/flag/math`
   has four segments in total. Both readings are defensible; the routes this pass added
   (`/lab/proof/<id>`) are ≤ 3 segments and so are safe under **either**. **The criterion should be
   restated in counted segments before it is implemented, and this pass did not restate it, because
   choosing between the two readings changes what the test asserts.**
4. **Where a per-wing panel module lives is a re-path, and it is the one place this pass came closest
   to inventing.** §0.9 decision 2 removes the per-wing page file, so a wing's bespoke rendering needs
   an address; `app/(lab)/lab/wing/[wing]/panels/<wing>.tsx` is the flattest option that is provably
   unroutable (`file-matcher.js:35` — only `page` and `route` basenames are routes) and sits beside
   the route it serves. **It is a naming choice, it is §8 row 13's to overrule, and no mechanism
   depends on it.**
5. **The chalkboard's move has a cost nobody has priced.** Under §0.9 decision 3 the twelve worksheets
   are reachable only in the LAB build and the §6.9 projection. **The operator uses them on the chip
   today.** §8 row 6 now carries the decision; **what it does not carry is how long the chip serves
   the laboratory in the meantime, because that is a scheduling call and not the agent's.**

## 10.4 Not covered at all

- **No lens was dead.** All six returned measured facts. But three whole regions were touched only
  from the outside and carry no independent verification in this plan: `viewer/command_center.cjs`
  (2159 lines), `viewer/studio_stage.cjs` (581) and `viewer/gaia/collectors.cjs` (**1380**) were listed
  by name, size and header only.
- **`docs/UNI-STACK-BUILDER-PLAN.md` (1167 lines) was never read in full by any lens.** Roughly 900
  lines are unread. The quotes carried here (`:49`, `:288-295`, `:474-484`, `:520-563`, `:570`,
  `:582`, `:588`, `:597`, `:601`, `:623`, `:625`, `:806`, `:813`) are from passages that were opened.
  **There may be worksheet-adjacent or derivation-adjacent content in the unread remainder.**
  Separately measured: that plan names **90** source paths of which **16 exist and 74 are absent**,
  including all of `lib/stack/` (23 modules), `app/stack-builder/` (7 components), `tests/stack/`
  (13 tests), `experiments/stacks/` (5 fixtures) and four `scripts/*.mjs`. **90 is a lower bound**
  — the extraction matched only paths bearing a recognised extension under seven top-level
  directories.
- **`docs/audit/PHASE-E-WORKBENCH-AUDIT.md` (537 lines) was never read in full.** The findings cited
  here (E-B01, E-B02, E-M01, E-M02, E-M03, E-M05, E-M06, E-M07, E-M09, PRD-03, PRD-11, NR-08,
  TC-06/TSA-07, section 4.5) were each re-derived from source where the source was available.
  **The rest of the ~55 defects are carried on the audit's word.**
- **`docs/THE-LABORATORY-PLAN.md` (436 lines) was read only in parts**, per the instruction to
  distrust its section 2. This plan carries none of its conclusions. Three of its factual claims
  were checked and **all three were wrong**: the flagellum is on the chip; `globals.css` in MAIN is
  544 lines not 702; and chip integration does **not** turn the suite red.
- **No visual check of anything.** E-M02 predicts a visual failure that the audit itself never
  observed in a browser, and neither did any lens here.
- **No `mix test`, no `npm test`, no `pytest`, no gate runner, no server, no browser.**
  **Everything this plan says about what currently PASSES rests on four commands that WERE run —
  `eslint`, `science:verify`, `cross-study:verify`, and both `npm audit` invocations — and on
  nothing else.**

### 10.4a OPEN AFTER THE CORRECTION PASS OF 2026-07-29 — measured, unresolved, not silently dropped

**These four were raised by an adversarial audit, verified against disk this session, and NOT fixed,
because fixing each one means inventing a mechanism this pass is not authorised to invent. Each
carries the command that settles it.** They are open items, not accepted limitations.

| # | The contradiction, measured | What would settle it | Command that re-derives it |
|---|---|---|---|
| **O1** | **§4.5 names `density: comfortable\|compact` as the missing half of the kindergarten-to-150 requirement, and nothing builds it.** The `equation-card` DOM specified in §4.5 carries `data-detail` and **no density attribute at all**: the four `data-detail` occurrences in this document (§4.5's `<article class="equation-card" data-detail={detail} …>`, §4.6's `<article class="workbook-page" data-detail="play\|lab\|audit">`, and two more in §4.6) have **no `data-density` counterpart in any specified DOM** — the only mentions of density outside §4.5's design paragraph are this row and §10.3's parked 22 px value. The FRAME's LEVEL slot is three-valued, `tests/disclosure.test.mjs` asserts across **three levels, not six cells**, and W15's row names `equation-card.tsx`, `work-the-equation.tsx` and `freeEnergyAt` and never mentions density. The 22 px minimum is parked in §10.3 as *"asserted from reading, not from measurement."* **So half of R3 is designed and unscheduled.** | Either W15 takes `density` as a second attribute and `disclosure.test.mjs` asserts six cells with `play`+`compact` REFUSED, or §4.5 states plainly that density is deferred and R3 is half-answered. **The operator's call, because it changes W15's size.** | `grep -n "data-density\|density" LAB-PLAN-V2.md` |
| **O2** | **Six bodies are in neither §5.0's wing table nor §5.8's NOT_RENDERED list**, falsifying §5.8's opening sentence on its own page: the world model (1,569 lines), the seven baseline adversaries, `lib/sp/determinism.ex` (113), `uni/brain/active_inference.py` (280), the resonance lattice (437 + 257) and the control plane (3,439). All sizes re-measured this session. | Each of the six gets a wing **or** a NOT_RENDERED row with a reason. **Assigning a wing is scope; it is not a measurement.** | `wc -l lib/sp/world/dynamics.ex lib/sp/sim.ex lib/sp/body.ex lib/sp/eval.ex lib/sp/determinism.ex` in `UNI.Minecraft` |
| **O3** | **Eight of the thirteen `NOT_FIXED` census rows carry the bare word and no argument** (§3.1 rows 5, 6, 7, 10, 14, 17, 19, 20). Seven of the eight are one route each over a file that already exists on disk; the eighth (row 20) has no file to read yet. **Row 7 — plan edits, the single source of truth for this phase, invisible and unattributed — is the sharpest.** | Schedule the seven cheap renders as one workstream, or record for each why it stays dark. **Either is honest; a bare `NOT_FIXED` is not.** | `ls -l evidence/control_plane/ledger.ndjson evidence/control_plane/anchor.json evidence/remediation/phase9_plan.json evidence/gate_attempts.ndjson docs/control-plane/LIMITATIONS.md viewer/build_identity.cjs viewer/.presence/` in `UNI.Minecraft` |
| **O4** | **`uni-flagellum-lab.tsx` renders zero truth chips.** `grep -n "truth-badge" app/uni-flagellum-lab.tsx` **exits 1** across 880 lines; the file states truth as an unclassed `status:` string at `:132`, `:139`, `:146`. `truth-badge` exists only in `biological-stage.tsx` (6 lines) and `living-science-walkthrough.tsx` (9 lines). **The largest component in the product carries no machine-readable truth class**, which is why §6.9.4's A5 had to be scoped rather than global. | Add chips to the bench panel in W-FLAG, then widen A5. **A5 must not be weakened instead** — that is the failure this plan exists to prevent. | `grep -rn "truth-badge" app/` in MAIN |

**One thing this pass could NOT re-verify and therefore did not touch:** every claim sourced to
`os_file_list` / `os_exec` against the deployed chip at `/opt/uni/flagellum/prod/src/` — the
`duration-models.js` extra file (4,346 B), the `PROMOTE_STATUS`, the promoted-EFE defect. **They are
carried on the earlier session's measurement, not re-measured on 2026-07-29**, because the chip was
not probed this session. `find` over all three local trees confirms `duration-models.js` exists
**only** in the STALE worktree (`UNI-FLAGELLUM-math-workbench/lib/duration-models.js`) and in
**neither** MAIN nor `UNI.Minecraft` — which is consistent with the chip claim but does not test it.

### 10.4b OPEN AFTER THE THIRD-PASS CONSISTENCY VERIFICATION OF 2026-07-29

**§0.9's four decisions were each checked by grepping BOTH sides of the pair across this whole
document. Two of the four propagated completely; two did not, and the same defect class — two
designs carried at once — has now recurred at a THIRD level, inside the acceptance criteria and
inside the gate tables. Nine items below. None of them is fixed here, because fixing each one is
either a scheduling decision or a mechanism, and this pass is reconciliation only.**

**What DID propagate cleanly, stated because an absence claim needs its search named.** A
case-sensitive grep for `lab/bench`, `/bench/`, `bench/[` and `viewer/lab/wings` over the whole file
returns hits at `:354`, `:572`, `:576`, `:707`, `:711`, `:3750`, `:5516`, `:5652` and **every one of
them is a statement that the route family is withdrawn** — no W-wing workstream, no acceptance
criterion and no §0.3 row still builds at `/lab/bench`. **Decision 2's route convention is single.**
A grep for `chalkboard` returns 40 hits and **every path-bearing one reads
`app/(lab)/lab/chalkboard/`** (`:338 :648 :722 :2963 :2971 :3057 :3448 :4981 :4982 :5344 :5637`);
the surviving `math-workbench` hits are the STALE worktree, the chip's live address, mutation X1 and
the four rows that record the withdrawal. **Decision 3's address is single.**

| # | The contradiction, measured | What would settle it |
|---|---|---|
| **T1** | **§7.1's Depends-on column never learned about W2b.** The row at `:5219` still reads `W3 … | W1, W2`, while `:5201` says W3 *"now stands on **W2a** and **W2b**"* and `:5339` makes it law. The same column omits W2b from **every other room-rendering workstream**: W11 `:5227` (W9, W10), W16 `:5232` (W5, W15), W17 `:5233` (W4), W18 `:5234` (W13), W19 `:5235` (W7, W12), W31 `:5294` (W2, W3, W2a). **Only W22 `:5261` carries the edge.** The law is in prose in §7.2 and absent from the machine-readable table that `verify_plan_consistency.cjs` could hold. | Add `W2b` to the Depends-on cell of every workstream that renders a lab route, or state in §7.2 that the column is narrative and the ordering law lives only in prose. |
| **T2** | **`/lab/wing/flag` and its four rooms have no owner.** The manifest at `:2301-2304` declares wing `flag` with `built:true` and rooms `loop/math/cad/observed`; §5.1 `:3846-3854` specifies six views for it. §7.1a `:5255` says *"Six wings"* and schedules panels for planet `:5263`, gate `:5264`, genome `:5265`, parity `:5266`, colony `:5268`, haif `:5269`. §7.4's row at `:5635` names the panel owners as `W24 W25 W26 W27 W29 W30`. **W-FLAG is in none of them, and it is not in §7.4's `NOT_SCHEDULED` table either.** §10.4a O4 `:6121` then assigns work to it — *"Add chips to the bench panel in W-FLAG"* — as if it were a workstream. | Either W-FLAG gets a row in §7.1a with a first file, dependencies and a size, or §7.4 gains a `NOT_SCHEDULED` row saying the flagellum wing is deferred and `built:true` is wrong. |
| **T3** | **`built` is a hand-typed claim with no gate.** `flag` and `parity` are `built:true` at `:2301,:2305`; every §3A.10 criterion checks routes, tiles, frame slots and counts, and **none checks `built`**. A wing can render `BUILT` with no panel module in the tree. That is the *"a number that does not move is a number somebody typed"* law of criterion 9 `:2716`, violated one field over. | Either drop `built` and derive it, or add a criterion that ties `built:true` to a panel module existing. **Deriving it is a mechanism; it is not invented here.** |
| **T4** | **§6.9.4 has two assertions numbered A6** (`:5097` the chip-gap count, `:5098` no accounts), so its table holds **nine** assertions under **eight** ids. `:4966` calls the guarantee *"A1–A8"*; mutation **M5** at `:5116` says it must trip *"A6"* and **which A6 is undecidable from the text**. This is the document's own defect class reproduced inside the flagship honesty gate. | Renumber to A1–A9 and repoint M5. **A numbering fix, but it changes what the verifier asserts, so it is written down rather than performed.** |
| **T5** | **The public projection is a workstream with no row in THE WORK, ORDERED.** Its criterion is labelled **W23a** at `:5127`, and `W23a` appears **nowhere** in §7.1 `:5214-5237`, §7.1a `:5259-5269` or §7.1b `:5292-5296` — no first file, no Depends-on, no size, no trees. It ships two new scripts (`:4931`, `:5083`), a `ci:true` registered gate `G-PROJ-01` `:5084`, eight mutations `:5110-5119` and the font-vendoring work at `:5149-5152`. **This is §0.9 decision 1's defect — the front door missing from the table — recurring at a third level.** Its id also collides with the convention `:5298-5302` set: `W2a`/`W2b` mean *"part of W2"*, so `W23a` reads as part of **MIRROR-SPLAB**, which it is not. | Give it a row with dependencies (at minimum W2a, W2b, W3 and the font work) and a size, and an id that is not a suffix of an unrelated workstream. |
| **T6** | **The projection's own gate A3 fails on the projection's own map.** `:4960-4961` keeps *"the map"* in the emitted bundle; the map renders `PORTALS` `:2321-2324`, whose two entries are literally `http://127.0.0.1:8102/` and `http://127.0.0.1:8103/`, emitted as `href`s (`:2466` — *"`prefetch={false}` on portal links"*). **A3 at `:5094` asserts `https?://(127\.|localhost|0\.0\.0\.0|\[::1\])` matches nothing in the emitted bytes.** §6.9.5's criterion `:5128` requires the verifier to exit **0**. Nothing in §6.9.3's step-3 deletion list `:4956-4961` removes or rewrites the portal tiles. **So on a correct build the gate is RED, and the acceptance criterion is unsatisfiable for the second time — a different cause from the one §0.9 decision 4 repaired.** | Decide what the projection does with portal tiles: omit them, or render them as text with no `href`. **Both are mechanisms; neither is chosen here.** Related and unhandled: the map also renders tiles for `intake`, `airlock` and `compare`, whose route files §6.9.3 deletes, so the published map links to pages `:5144-5145` requires to be absent. |
| **T7** | **§3A.10 criteria 1 and 6 still assume one hand-authored file per wing — the design decision 2 rejected.** Criterion 1 `:2687-2688` says *"Adding a wing to `lib/shell/wings.js` without creating its route turns the suite red"*, and §7.3's W2b item 1 `:5499-5500` repeats it. **Under decision 2 the wing route is generated FROM the manifest** (`:2293`, `generateStaticParams`; `:709-710`), so adding a wing creates its route automatically and the stated mutation cannot go red. Criterion 6 `:2702-2704` walks `app/(lab)/**/page.lab.tsx` and asserts set-equality with the manifest — for the single `[wing]` file that expansion **is** the manifest, so the comparison is circular for wings. Both still bite for the seven `STANDING` rooms and for the withdrawn-row regression check `:5513-5518`, which is why the vacuity is easy to miss. | Restate criteria 1 and 6 in terms of what a dynamic route can actually falsify (a manifest wing whose panel module is missing; a static `page.lab.tsx` off the manifest). **That is a new assertion, so it is recorded, not written.** |
| **T8** | **`release-excludes-lab` is `ci:true` and cannot be green at the end of W2a.** Assertion 3 `:468-469` requires `R_lab \ R_release` to be **non-empty**. W2a's acceptance `:5481-5482` builds one throwaway `app/(lab)/smoke/page.lab.tsx` and then requires all six assertions to pass. **If the smoke page is deleted, assertion 3 fails and CI is red until W2b lands a lab route; if it is kept, §3A.10 criterion 6 `:2702` fails the moment W2b lands, because it is a route file with no manifest entry.** The plan says the gate is built first `:666-667` and never says which of the two states W2a ends in. | Decide whether the smoke route persists to W2b and is deleted there, or whether `release-excludes-lab` is knowingly RED between W2a and W2b and is registered `ci:false` until then. |
| **T9** | **Two answers to where the chip host is named.** §0.3 `:346` calls `app/(lab)/api/chip/route.lab.ts` *"the only file in either wing permitted to name a chip host or port"*, and §0.8 `:661-662` says *"the channel is"* that file. §2.11 `:1453-1466` says the endpoints live in `lib/observation/channel.json`, that `lib/shell/chip-observer-client.js` is *"the only module permitted to contain `fetch(`"*, and that a semantic test asserts **exactly one file in `app/**` + `lib/**`** matches the network regex. W9's row `:5225` lists all three artifacts and never says how they compose. **If `route.lab.ts` fetches the broker it breaks §2.11's one-file assertion; if it imports the client, §0.3's sentence is false.** | One sentence in §0.3 or §2.11 saying which file holds the URL and which holds the `fetch`. |

**And one thing this pass judged rather than measured, recorded because the judgement is contestable.**
**§0.4's gate can be GREEN while laboratory code ships**, and the reason is not the hole decision 4
closed. Assertion 4 `:470-483` is set-equality over **emitted routes**; a laboratory component
imported into an **existing** product page emits no new route, so `R_release` is unchanged and the
gate passes. Assertion 6 `:497-499` scans only for four loopback host literals, which a chalkboard
does not carry. **The three mutations `:510-512` all create or declare a route** — X2 chose the
variant the gate catches — so **no mutation exercises the import-into-an-existing-page case.** This
is **not** a hidden vacuity: §0.4a `:530-532` states the limitation in the gate's own words
(*"no laboratory **route** is served… It does not prove no laboratory **byte** is present"*). It is
recorded here because the consequence is sharper than the sentence sounds: **the whole chalkboard
could ship inside `/` with all six assertions satisfied.** A fourth mutation would settle it; adding
one is design, so it is named and not written.

**Minor, and listed so it is not lost.** §5.8's row at `:4393` states flatly that `chatgpt-auth.ts`
*"should be deleted, not rendered"*, while §0.3 `:322` schedules a move, §0.6 `:607-610` recommends
move-now-delete-later and §8 row 15 `:5685` holds the choice as the operator's. Three places, two
answers, and the flat one is in the section least likely to be read at decision time.
**And §3A.10 criterion 9 `:2713-2716` still transcribes its counts** (*"today, 6"*, *"the map must
read 5"*) while §7.3's W2b item 4 `:5509-5512` states the same criterion in computed form
(*"the map must move by exactly one"*). W2b's acceptance is *"§3A.10's ten behavioural criteria, in
full"* `:5494`, so both forms are in force and only one of them survives a change to the committed
reports.

*Measured this session: the file is 455,213 B and 6,156 lines before this subsection was appended;
its last byte is `0x0A`. Every line citation above was read this session in this file.*

---

### 10.4c OPEN AFTER THE FOURTH-PASS HALLUCINATION AUDIT OF 2026-07-29

**Every absence claim in this document was re-run against disk this session, scoped as the document
says it is scoped. They held.** So did §5.9's set operations (28 registry / 206 rows / 109 names /
34 glob-covered / 75 uncovered / intersection 0), §9.3's `canRun('hud') → SEALED_BY_S10` (executed),
§3.9's `192 of 689` and `505 of 689` (both re-derived with the stated pattern), §10.0 items 2, 4, 5,
6, 9a, 9b, 12, 13, 15, 17, 20 and 24, the `lab/proofs/` 501/41,451 split, and every vinext internal
except the one below. **Twelve citation defects were corrected in place by this pass** — they are
listed in the commit-free record below because a correction nobody can see is not a correction.

**Corrected in place, each verified by a numbered read this session:**

| what was written | what is on disk | where |
|---|---|---|
| `file-matcher.js:38` builds the app-router page regex — **twice** | `:38` is `const appDefaultRegex = createLeafPattern(["default"]);`. The page regex is `:35`. **The one paragraph whose whole job is proving, from source, that a non-`page` file can never be a route was pointing at the wrong line — and §10.3a item 4 repeated it.** | §0.3, §10.3a |
| page regex quoted as `` (^page|[\/]page)\.(?:<exts>)$ `` | the leaf pattern at `:33` interpolates `names`; for the page matcher `names` is `(page|route)`. **The quoted form silently drops `route`, which is the basename §6.9.4 A1 is about.** §0.3 already had it right, so the document held two spellings of one regex | §0.1 |
| `track_server.cjs` **531** lines | **530.** 31,740 B, 530 `0x0A`, last byte **is** `0x0A`, so §9.0's own counter gives 530 and `wc -l` agrees. 531 came from neither | §3.2 |
| `:497-505` serial branch · `:511-521` history · `:646-648` run toggle · `:737-742` nav · `:486-524` loop | `:498-506` · `:512-522` · `:647-649` · `:737-743` · `:486-525`. **All five off by one at one or both ends, in the same list where the previous pass precisely repaired `:507`→`:508`** | §3A.2 |
| `probePortals` `:276-300` | `:277-301`; the JSDoc is `:274-276` | §3A.3 |
| lint scope quoted as `eslint . --ignore-pattern dist` | `eslint . --ignore-pattern dist --ignore-pattern .next` | §6.9.3 |
| registry entry "matching the measured schema exactly (`{id, file, ci, gate_row, timeout_ms}`)" | `timeout_ms` is on **1 of 28**; `external_needs` on **3 of 28**; only four keys are universal | §0.4 |
| "**seven** of the eight are the same shape: a file that already exists" | **six** files are named, and row 10's artifact is `.git`, which its own UI cell says TRACK already renders in part | §3.1 |

**Not corrected, because correcting each one changes what a test asserts. Three contradictions,
measured, left standing:**

| # | The contradiction, measured | What would settle it |
|---|---|---|
| **U1** | **The `fetch(` census criterion fails on a correct implementation.** §2.2 and §2.11 scope it precisely — *"exactly one file in `app/**` and `lib/**`"* — but §2.12 criterion 1 and §7.3 **W2** both drop the scope and read *"The **whole-tree** `fetch(` census returns exactly one file."* Measured this session in MAIN, excluding `node_modules/`, `dist/`, `.next/`, `.git/`: **`fetch(` appears in three files** — `worker/index.ts` (which §0.1 `:248` cites approvingly for `handler.fetch`), `tests/rendered-html.test.mjs`, and `docs/UNI-STACK-BUILDER-PLAN.md`. In `app/` + `lib/` it appears in **zero**. **A builder who implements the criterion as written gets a red gate on a correct tree; one who implements §2.11 gets a green one.** | Delete the word *whole-tree* from both criteria and say `app/**` + `lib/**`, **or** keep the whole-tree scan and name its allowlist (`worker/`, `tests/`, `docs/`). **Either changes what the gate asserts, so it is recorded rather than performed.** |
| **U2** | **§3.11 criterion 11 transcribes a count into a gate.** *"`/receipts` lists **136** entries"* is correct today — re-measured: 136 files / 72 `.md` recursively under `UNI.Minecraft/docs/receipts/` — **and it goes red the first time anyone adds a receipt.** This document forbids exactly that shape twice in its own words: §2.2 *"A criterion that hard-codes 7 goes red the day a shell is touched; one that reads the glob cannot"*, and §3A.10's own note *"a transcribed count in a criterion is a correct run's way of failing its own gate."* Criterion 12, one line below, gets it right (*"computed from the table rather than typed"*). | Restate as *"`/receipts` lists one entry per file under `docs/receipts/`, counted at run time, and names UNI-FLAGELLUM's zero."* **A computed form is a different assertion, so it is written down here.** *(§10.4b's closing note records the same defect independently at §3A.10 criterion 9, which transcribes `6` and `5`.)* |
| **U3** | **Two absence claims name their directories but not their needle**, which §9.0's rule (*"every 'does not exist' in this document names the search that establishes it"*) does not survive. §3A.5's notebook line says a sentence *"exists nowhere in either tree (`grep -rn` over `app/ lib/ docs/ experiments/ scripts/` exits 1)"* **without quoting the sentence**, so no reader can re-run it; recovered from the previous draft it is *"Your notebook lives only in this browser. Export it."*, and with that needle the claim **holds** in both trees. §4.5's *"There is no play-level prompt anywhere in either tree"* names **no search at all** and no needle exists — it is a judgement about twelve prompts, not a measurement. | Quote the needle in §3A.5. In §4.5, restate as a judgement (*"none of the twelve prompts at `scientific-math-workbench.tsx:390-401` is authored below `lab` level"* — which **is** checkable by reading them) rather than as an absence. |

**And one hazard that is about this file, not about the repositories.** This document was being
written by another process **while this audit ran**: it was 455,213 B / 6,156 lines when the audit
opened, 466,170 B when §10.4b was read, and 467,168 B before this subsection was appended — three
different files in one session, growing by ~12 KB. **Every `:line` citation *into this document*
(§10.4b's table is built entirely from them) is therefore true only of the revision that wrote it,
and this file is tracked by no git repository, so nothing can ever diff it.** Citations *out* of this
document into the three trees are unaffected and were all re-verified. **The fix is not textual:
this plan belongs in a git repository before it accumulates one more self-referential line number.**
It is the same hazard `CLAUDE.md`'s own banner records about the untracked copy at
`Documents/UNI-Flagellum/CLAUDE.md`, one directory up.

---

## CLOSING NOTE

This document is a plan, not a claim. It contains no verdict about any scientific question, it
authors no gate row, and it crosses no door. The adverse results in its opening section are the
reason it exists, and they are the first thing anyone reading it should carry away.

**The single most important sentence in it: the defective expected free energy is the PROMOTED
artifact on the chip.** It was read this session, on the chip's own file, at
`/opt/uni/flagellum/prod/src/lib/uni-motor.js`, under a `PROMOTE_STATUS` that says `PROMOTED`.
DEPLOYED and PROMOTED are certain. **SERVING is not established, and this document does not claim
it.**

**Two things this revision retracted, and an engineer following the previous draft would have acted
on both:** five SVGs described as empty are 568 KB of valid diagrams, and a science report described
as 6 PASS says 4 in its own summary field. **Both were caught by re-measuring against disk, not by
review.** That is the argument for §6.9 in one line.

**One decision is now the operator's and the plan waits on nothing else: §0, the surface decision
(§8 row 15).** If he says nothing, the plan proceeds on it — sections 3A, 4 and 5 are already
written against it.

**Next act, if this plan is accepted: W0 — speak the adverse results, put a RETRACTED banner on
`docs/THE-LABORATORY-PLAN.md`, and correct the two false documents. Then W2a, the surface boundary
and its gate, before any wing exists to leak. Everything else waits behind those two.**
