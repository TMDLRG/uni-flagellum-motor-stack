# Next session brief — deepen the architecture, then resume Phase 2

**This is prep work, not Phase 2.** Phase 2 stays pre-registered and untouched until this completes.
Read [`RESUME.md`](RESUME.md) first for state, then this.

---

## Standing rules for this session (read before acting)

- **Speak.** Use `mcp__claude-voice__speak` on findings, decisions, phase edges, completion, blockage. Adverse results are spoken **first**, never appended at the end. Confirmed working: Piper, local, `en_GB-jenny_dioco-medium`.
- **Converse. Do not dump.** One thing at a time. Lead with the outcome in the first sentence. If a long status block is forming, it belongs in TRACK, not in chat.
- **Ask, do not assume.** Naming, scope and contract changes are the operator's. Speak the question and stop.
- **Ground before claiming.** Four times this project I reported a replica as canonical or a doc as truth. Verify against the live source and name it.
- **Live read only.** Nothing in TRACK may be cached or hand-transcribed. If a value cannot be read live, it renders as unknown — never as a guess.

## What exists now

| thing | where |
|-|-|
| C4 model of record | `workspace.dsl` — 15 containers, 31 relationships, 4 views |
| Rendered views | `generated/*.svg` + `*.png`, via `render.sh` (structurizr-cli + PlantUML, both installed) |
| Mermaid projections | `views.md` — 9 views, render with no tooling |
| Architecture prose | `ARCHITECTURE.md` — 15 sections |
| Decisions | `decisions/ADR-0001..0007`, each with a falsifier |
| Phases | `phases/PHASE-1.md`, `PHASE-1-RESULTS.md`, `PHASE-2.md` |
| Live surface | **UNI TRACK `:8102`** — `viewer/track/` in `UNI.Minecraft`; serves `/arch/*` and `/api/arch` |

## Task 1 — Audit the architecture for accuracy

Cross-check every claim in `ARCHITECTURE.md`, `workspace.dsl` and `views.md` against the **running system**, not against each other. For each: confirmed, corrected, or `NOT_VERIFIED` with the reason.

Known to check: port and process claims for all four bodies; the seat list and signal population in Gaia (live, not `GAIA.md`); the ledger tally (canonical only — the chip replicas are stale by design); the Door's verbs and journey states; the `ui/` contract as amended; every `SP.*` module name actually present in `lib/sp/`.

**Falsifier:** any statement in the architecture that cannot be traced to a live read or a named file:line.

## Task 2 — Add the missing specification

Currently absent and needed before the Control Plane is built:

- **Sequence diagrams** (Mermaid, into `views.md`, and mirrored in the DSL where it can carry them): register a gate → run paired → observe → review → author verdict → write receipt → append row → Gaia projects; the Door's admission and release; a room/airlock transition with two keys; an emergency stop mid-run; a drift surfacing and its resolution.
- **Component view** — the C4 level below Container, for `SP.ControlPlane` internals.
- **Data specification** — the ledger entry shape, the receipt shape, and the scene-node contract, each with field types and required/optional, cross-referenced to `gate_row.schema.json`.
- **Failure-mode spec** — every refusal in `ARCHITECTURE.md §10` as a testable statement.
- **The `SP.Producer` disambiguation line** (ADR-0006) — not yet written.

## Task 3 — Drill-down and cross-linking in TRACK

- Every element in the diagram links to its definition — a body to its `ARCHITECTURE.md` section, a Control Plane part to its phase item, a gate to its receipt.
- ADRs cross-link to the elements they govern, and elements back to their ADRs.
- Render the markdown docs **in** the page rather than serving raw text.
- Surface each falsifier next to the thing it would falsify.
- Make `/api/arch` carry the model's parsed elements and relationships so the page can show the graph, not just the pictures.

**Constraint:** TRACK owns nothing and caches nothing. Every addition is a live read from the real file, carrying that file's path.

## Task 4 — Re-render and verify

```bash
bash docs/control-plane/render.sh                      # validate + export + render, all 4 views
cd ~/Documents/UNI.Minecraft
node viewer/gaia/verify_gaia.cjs                       # expect 12 PASS, 8 drift signals
node viewer/gaia/gaia_lint.cjs                         # expect 0 violations
node viewer/gaia/replica_ledger_probe.cjs              # re-capture replica digests
curl -s http://127.0.0.1:8102/api/arch                 # index resolves
```

**Do not** add a hex dependency, edit `mc_test.exs` (user-owned), write to `evidence/gates.ndjson`, or move a P-level.

## Exit condition

This brief is complete when the architecture audit is recorded, the missing specs exist, TRACK drills down and cross-links, and every view re-renders clean. **Then, and only then, resume [`phases/PHASE-2.md`](phases/PHASE-2.md) exactly as pre-registered.**

Per `ORCHESTRATE-RULES.md §1`, record the result and name the next act. Phase 2 ends by writing `PHASE-3.md`.
