# ADR-0009 — Gaia is the authoritative projection; the Control Plane is the author

- **Status:** PROPOSED — NOT ADOPTED. This document is not in force.
- **Date:** 2026-08-01
- **Deciders:** Michael (operator — ruled **RECONCILE, no repeal**, aloud, 2026-08-01), Veritas, Custos
- **Subject on `/decide`:** `not_mine[6]` in `evidence/remediation/phase9_plan.json`
- **Amends:** nothing. It reconciles a seed-prompt sentence with [ADR-0001](ADR-0001-four-bodies.md),
  [ADR-0002](ADR-0002-gaia-projects-never-computes.md) and `ARCHITECTURE.md` §1.2 — all three of which
  stand unchanged. **Adoption is `S5`, a contract amendment, and is the operator's alone.**

## Context

Two governing documents say opposite things about the same word.

A seed-prompt document declares:

> Gaia is the sole authoritative platform source.

`ARCHITECTURE.md` §1.2 (`ARCHITECTURE.md:21`) declares:

> **Not Gaia.** Gaia may never act or author a verdict (§3.3). A Gaia-centred control plane is
> structurally impossible, not merely undesirable.

Read as written, one of the two must be repealed. The operator ruled on 2026-08-01 that **neither
is** — because they are not statements about the same thing. The word *source* was carrying three
jobs at once, and collapsing distinct things into one word is the exact failure this architecture
exists to prevent ([ADR-0001](ADR-0001-four-bodies.md),
[ADR-0006](ADR-0006-sp-controlplane-naming-and-placement.md)).

**The three jobs are already three separate artifacts. Only the word was shared:**

| role | body | artifact | authors a verdict? |
|-|-|-|-|
| **AUTHOR** | `SP.ControlPlane`, and nothing else | `lib/sp/control_plane.ex` | **yes — only this body** |
| **RECORD** | the append-only ledgers | `evidence/control_plane/ledger.ndjson` + `evidence/gates.ndjson` | no — it *holds* what was authored |
| **PROJECTION** | Gaia, and Gaia alone | `viewer/gaia/**` | **never** |

None of this is new. `SP.ControlPlane`'s own moduledoc calls it *"the body that runs the lab, authors
every verdict, and is the only writer of the evidence record"*. `docs/GAIA.md:87` says Gaia *"NEVER
summarizes, represents, editorializes, scores, ranks, narrates, or authors a verdict"*, and
`gaia_lint.cjs` fails the build on any breach of it. [ADR-0002](ADR-0002-gaia-projects-never-computes.md)
already rules that the Control Plane authors and Gaia projects verbatim. What was missing was the one
sentence that says the seed prompt is talking about the third row of that table and nothing else.

**The seed prompt is not a committed artifact, and that is part of why this lasted.** Measured
2026-08-01: `grep` for the sentence *"sole authoritative platform source"* across both
`UNI.Minecraft` and `UNI-Flagellum` returns **no match**. A declaration that lives in no tracked file
cannot drift under a gate, cannot be diffed, and cannot be corrected by anything except a reader
noticing — which is the same class of defect as the untracked `CLAUDE.md` copy that carried a stale
`NEXT ACT:` for a day because no instrument could reach it.

## Decision

**Gaia's authority is real, exclusive, and confined to one role. The seed prompt gets a qualifier, not a repeal:**

Gaia is the sole authoritative PROJECTION of platform state. It is not, and can never be, an AUTHOR of it. The seed prompt's 'Gaia is the sole authoritative platform source' is true of the projection role and false of the authoring role; this ADR supplies the qualifier. ARCHITECTURE.md section 1.2 stands unamended and is a statement about authorship.

Three consequences follow directly, and each names its artifact:

1. **AUTHOR is `SP.ControlPlane` and nothing else** (`lib/sp/control_plane.ex`). No surface, no
   agent, no viewer and no projection may author a verdict. A verdict that did not come from that
   body did not come from the platform.
2. **RECORD is the ledgers** — `evidence/control_plane/ledger.ndjson` and `evidence/gates.ndjson`.
   They are append-only and hash-chained. They store; they do not decide.
3. **PROJECTION is Gaia and Gaia alone** (`viewer/gaia/**`). *Sole* is the operative word and it cuts
   both ways: no second surface may claim to be an authoritative view of platform state, and Gaia
   may not summarise, score, rank, roll up, reconcile, or author what it shows. Where the record and
   a document disagree, Gaia emits a drift signal carrying both byte-sets verbatim and **the Control
   Plane resolves it** ([ADR-0002](ADR-0002-gaia-projects-never-computes.md), decisions 3 and 4).

## Consequences

- `ARCHITECTURE.md` §1.2 is **not edited**. It was correct before this ADR and is correct after it.
  This document narrows a loose word in the seed prompt; it does not soften a precise one in the
  architecture.
- Gaia is *promoted* on the only axis where it can honestly be promoted. "Sole authoritative
  projection" is a stronger claim than Gaia held before, and it is one Gaia can actually keep: a
  surface that shows platform state without Gaia's provenance triple is not authoritative even on the
  occasions when it happens to be right.
- The word **authoritative**, applied to Gaia, is now role-qualified by contract. Any future document
  that writes "Gaia is authoritative" without saying *projection* is wrong on its face, and this ADR
  is the citation for saying so.
- **The one place the split is not clean is retained rather than hidden.** `docs/GAIA.md:281` and
  `:349` grant Gaia exactly **one** sanctioned append to `evidence/gates.ndjson`, at DD-completion —
  a row about Gaia's own gate. That is the PROJECTION writing to the RECORD. It is bounded, declared
  and fenced, but it is a genuine exception to the table above, and this ADR does not dissolve it. If
  the operator wants it closed, closing it means the Control Plane authors Gaia's row like every
  other, and Gaia writes nowhere outside `viewer/gaia/**`.
- The seed prompt should be committed, or the sentence should be retired from it. An uncommitted
  governing sentence is unreachable by every instrument this project has built.

## Alternatives considered

1. **Repeal the seed-prompt sentence.** Rejected by the operator — the ruling was RECONCILE, no
   repeal — and also wrong on the merits. The sentence carries a real claim that nothing else states:
   there is exactly **one** authoritative projection. Deleting it loses that.
2. **Amend `ARCHITECTURE.md` §1.2 to soften "structurally impossible".** Rejected. §1.2 is the
   load-bearing sentence and it is true: Gaia may never act, so a Gaia-centred control plane is not a
   design choice anyone could make. Weakening a correct statement so that a loose one becomes true is
   precisely the "apparent harmony" the truth contract forbids.
3. **Let both stand and let readers infer the qualifier.** Rejected — this is what was already
   happening. It produced a live contradiction between two governing documents that survived until
   somebody read them side by side. An inferred qualifier is not a qualifier.
4. **Introduce a fourth role called "source", distinct from all three.** Rejected: *source* is the
   ambiguous word. Naming a role after it entrenches the ambiguity instead of resolving it. The
   platform already has the precise thing that word was reaching for — a per-signal provenance
   locator — and a locator is a field, not a body.

## Falsifier

**Any verdict that reaches the record without passing through `SP.ControlPlane`, and any verdict that
Gaia itself derived.** Three observations falsify this ADR, and each names the instrument that fires
on it:

1. **Gaia authors.** Any Gaia-emitted count, percent, score, rank, rollup or verdict that Gaia itself
   derived, rather than carried verbatim from its source. `viewer/gaia/gaia_lint.cjs` fails the build
   on exactly this (registered gate `gaia-lint`, `gate_row: gaia-no-summarization`), and its negative
   control `viewer/gaia/verify_lint_bites.cjs` (gate `lint-bites`) runs the lint against
   `viewer/gaia/fixtures/summarizing_seat_fixture.json` and **fails if the lint passes it** — so the
   falsifier is itself proved to bite.
2. **Gaia writes outside its own tree.** Any write by `viewer/gaia/**` to anything other than
   `viewer/gaia/**`, `docs/GAIA.md`, and the single sanctioned gate row. `gaia-read-only-fence` is
   the check; if it cannot see a given write path, the fence is the defect and the seat waits.
3. **Gaia resolves a disagreement instead of reporting it.** A projected value that is the reconciled
   result of two disagreeing sources, rather than a drift signal carrying both verbatim, falsifies
   the PROJECTION role directly.

**And the falsifier this ADR cannot currently satisfy, stated first-class because it is the real
one: the record does not name its author.** `production/schemas/gate_row.schema.json` requires
`schema_version`, `name`, `verdict`, `receipt_path`, `evidence_class`, `last_updated`, sets
`additionalProperties: false`, and has **no author field of any kind**. All 207 rows in
`evidence/gates.ndjson` are therefore anonymous. The AUTHOR role is asserted by this document and
fenced inside Gaia's own code; it is **not verifiable from the RECORD** — which is the one place it
would have to be verifiable for the three-role split to be more than prose. Until such a field
exists, *"`SP.ControlPlane` authored this"* is an unfalsifiable statement about every row in the
ledger, and adopting this ADR obliges the field that makes its own central claim checkable.
