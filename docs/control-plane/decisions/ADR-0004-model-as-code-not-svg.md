# ADR-0004 — Architecture is model-as-code; hand-authored SVG is not an architecture format

- **Status:** Accepted (supersedes the SVG diagrams committed in `0587c3b`)
- **Date:** 2026-07-25
- **Deciders:** Michael, Veritas, Custos

## Context

The first attempt at documenting this architecture committed two hand-authored SVG files with absolute `x`/`y` coordinates on every element — 508 lines of positioned rectangles and text.

The operator's objection, verbatim: *"how the fuck are we going to collaborate over SVG files… now it is just a picture."*

The objection is correct and the failure is concrete:

- **Not editable.** Moving one box requires recomputing the coordinates of every neighbour and every connecting path by hand.
- **Not diffable.** A layout change and a semantic change look identical in `git diff`. A reviewer cannot see that a relationship was added.
- **Not readable by the author.** Coordinates do not carry meaning; the file cannot be reasoned about after it is written, only re-rendered.
- **No single source of truth.** Two SVGs sharing the same subject drift independently, with nothing to detect it — the same disease [ADR-0002](ADR-0002-gaia-projects-never-computes.md) exists to prevent.
- **Not a model.** There are no typed elements or relationships, so nothing can be validated, queried, or projected into a second view.

## Decision

Architecture is maintained as **text that models, not text that draws**:

1. **[`workspace.dsl`](../workspace.dsl) — Structurizr DSL, the model of record.** One C4 model with typed people, containers, relationships and deployment nodes; multiple views derived from it. Industry-standard C4, tool-supported, reviewable line by line.
2. **[`views.md`](../views.md) — Mermaid, the zero-tooling projection.** Renders natively in GitHub, GitLab and most markdown viewers with no build step. Text in, picture out.
3. **`decisions/ADR-*.md` — the reasoning.** MADR format. Every consequential choice gets its context, decision, consequences, alternatives and falsifier.
4. **[`ARCHITECTURE.md`](../ARCHITECTURE.md) — the prose** that the model cannot carry: contracts, invariants, failure modes, acceptance criteria.

The hand-authored SVGs are **deleted**, not left beside the model. Two sources of truth is the problem being fixed.

## Consequences

**Positive.** Every element and relationship is a reviewable line. A pull request shows *"added relationship Control Plane → Approval queue"*, not a coordinate delta. One model yields several views without redrawing. Both a human and an agent can read the model back and reason over it. Layout is the renderer's job, which is what renderers are for.

**Negative.** Structurizr rendering needs tooling (`structurizr-cli`, Java, or the free web renderer) that is **not currently installed** — recorded as an open item. Mitigated by Mermaid, which needs nothing. Mermaid's C4 support is less complete than Structurizr's, so the two views may not be pixel-identical; the DSL is authoritative where they differ.

**Neutral.** Contributors need to know C4's four levels and Mermaid basics. Both are widely documented and standard practice.

## Alternatives considered

**Keep the SVGs, add a model alongside.** Rejected: two sources of truth that drift, with no mechanism to detect it.

**PlantUML.** Viable and text-based, but needs a render step everywhere and has no first-class deployment or C4 element typing without an extension library.

**Mermaid alone, no DSL.** Simpler, and it was tempting. Rejected because Mermaid views are independent drawings — the same relationship must be repeated in each diagram, so views drift from one another. The DSL holds one model that the views project.

**Diagrams-as-code in a general language (Python `diagrams`, D2).** Rejected: adds a runtime dependency to read the architecture, and D2 is not C4-native.

## Falsifier

If a relationship exists in a rendered view but not in `workspace.dsl`, or a view is edited without the model, this decision has been violated. If anyone hand-positions a diagram element again, it has been violated.

## Addendum — toolchain installed 2026-07-25, and one honest limitation

The tooling gap this ADR recorded as open is now closed. Installed user-local; nothing system-wide was changed:

| tool | version | why |
|-|-|-|
| Temurin JDK 17 | 17.0.19 | structurizr-cli ships class file 61.0; the system JDK 11 (55.0) cannot load it |
| structurizr-cli | 2025.11.09 | validates the DSL and exports every view from the one model |
| PlantUML | 1.2026.6 | renders the exported C4-PlantUML to SVG and PNG |
| graphviz | 14.1.0 | already present; PlantUML's layout engine |

Reproduce with [`render.sh`](../render.sh): validate, export to C4-PlantUML **and** Mermaid, render to SVG **and** PNG.

Two real errors were caught by `validate` that a hand-drawn diagram could never have surfaced:
`deployment` takes *environment* then *key*, and the key rejected a description used in its place;
and element styles require one property per line. **This is the argument for the format, made by the format.**

**Limitation — element styles do not survive the PlantUML export.** The `Built` / `NotBuilt` /
`Store` styling in `workspace.dsl` renders in the Structurizr renderer (web or Lite), but
C4-PlantUML applies its own theme, so every container in `generated/*.png` appears in the same
blue. **The built-versus-not-built distinction is therefore carried in the element descriptions
and in `ARCHITECTURE.md`, never by colour alone.** Do not read the rendered PNGs as a statement
about what is built. This is recorded rather than worked around, because a reader who infers
"all blue means all built" would be badly misled.
