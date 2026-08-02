# ADR-0002 — Verdicts are authored by the Control Plane and projected by Gaia, never computed by Gaia

- **Status:** Accepted
- **Date:** 2026-07-25
- **Deciders:** Michael, Veritas, Custos

## Context

Gate status in the flagellum repository is hand-written prose in nine files, and it has drifted. `H-AIF-G7` is recorded `NOT RUN` at `hierarchical-aif/docs/H-AIF-GATES.md:15` and `EXECUTED — NOT_ESTABLISHED` at `hierarchical-aif/ledgers/HIERARCHICAL-AIF-GATE-TO-EXISTING-P-LADDER-MAP.md:53`. G5 and G6 disagree likewise.

The obvious fix — have one component compute gate status from receipts so it cannot drift — was proposed in an earlier draft of this architecture, assigned to Gaia.

**That proposal violates GAIA LAW.** From `docs/GAIA.md §1`: *"Gaia shows ONLY direct signals with provenance. It NEVER summarizes, represents, editorializes, scores, ranks, narrates, or authors a verdict."* §6(b) makes `count`, `sum`, `avg`, `percent`, `score`, `rank`, `total`, `ratio` and any Gaia-authored verdict a **build defect** caught mechanically by `gaia_lint.cjs`. §9: *"derived-by-Gaia = FORBIDDEN."*

The proposal would have been rejected by the system's own linter.

## Decision

1. The **Control Plane authors** every verdict and writes a receipt.
2. **Gaia projects** both the authored verdict and its receipt **verbatim**, with a provenance triple, adding nothing.
3. When a document and a receipt disagree, **Gaia emits a drift signal** — `{a, b, relation, equal}` with both byte-sets carried verbatim, no severity, no diff-percent, no judgment.
4. **The Control Plane resolves the drift.** Gaia reports it and never resolves it.

A source's *own* computed verdict carried verbatim is projection, not derivation, and is allowed — a gate row's `PASS|PARTIAL|FAIL|WITHHELD|PENDING` travels with its source as locator.

## Consequences

**Positive.** Gaia stays lint-clean and keeps its value as an independent witness. Drift becomes visible rather than silently reconciled — `docs/GAIA.md §9` names doc-vs-code drift as something Gaia *must* surface. Every receipt Gaia projects must be shaped so no field requires Gaia to compute anything, which forces the Control Plane to emit complete records.

**Negative.** Drift is surfaced but not auto-fixed; a human decision is required to reconcile. This is intentional — an auto-reconcile is exactly the "apparent harmony" the truth contract forbids.

## Alternatives considered

**Gaia computes the authoritative gate register.** Rejected: forbidden by GAIA LAW, and mechanically rejected by `gaia_lint.cjs`. Would also destroy Gaia's independence — a witness that computes the thing it reports is no longer checking anything.

**A tenth prose file holding the "real" status.** Rejected: that is the disease, not the cure.

**Auto-reconcile the stale document to match the receipt.** Rejected: silently rewriting a disagreement is the failure mode the drift signal exists to prevent.

## Falsifier

Any Gaia-emitted count, percent, rank, rollup or verdict that Gaia itself derived. `gaia_lint.cjs` must fail the build on a summarizing fixture **before** any new Gaia seat is added — that red test is a required step in the build sequence.

---

# Amendment 1 — both sides of a drift signal must be the same kind and the same normalization

- **Status:** Accepted
- **Date:** 2026-07-26
- **Deciders:** Michael (co-sign), Veritas, Custos
- **Occasioned by:** *"address all drift"* — and the discovery that most of it could not be addressed, because most of it could not converge.

## Context

Decision 3 above says a drift signal carries `{a, b, relation, equal}` with both byte-sets verbatim. It never said what `a` and `b` must **be**. They turn out, in practice, to be different kinds of thing — and a signal comparing a sentence to a filename cannot reach `equal: true` in **any** state of the repository. It is not measuring drift. It is reporting a category error, forever, in the vocabulary of a measurement.

Measured live at `127.0.0.1:8096/api/gaia`, 2026-07-26T16:05Z, ten drift signals:

| signal | side `a` | side `b` | can it ever be equal? |
|-|-|-|-|
| `drift.fqdn_cjs` | a prose line from `CLAUDE.md` | a filename, or `""` | **no** — prose vs path |
| `drift.gate_row_schema_path` | a prose line fragment | `production/schemas/gate_row.schema.json` | **no** — prose vs path |
| `drift.resolver_planned` | `"dnsmasq (planned)"`, 17 bytes | a JSON array of 21 live tracking rows | **no** — label vs array |
| `drift.self_caps_doc_vs_served` | a CAPS JSON blob | the whole of `GAIA.md`, 54 KB of markdown | **no** — JSON vs a document |
| `drift.replica_ledger.*` (×3) | `sha256` of mixed-EOL working-tree bytes | `sha256` of all-CRLF bytes after `git archive \| tar -x` | **no** — same type, different normalization |
| `drift.control_plane_anchor_git` | anchor object | anchor object | **yes — and it is `equal: true` today** |
| `drift.git_dirty_vs_clean` | `""` | `git status --short` output | **yes — and it is `equal: true` today** |

**That table is the whole argument.** The two well-formed comparisons converged the moment the world became correct. The five malformed ones stayed red through a day of real corrections — a served schema pointer fixed, a resolver confirmed live, a working tree cleaned — and would have stayed red had every one of those corrections been perfect. The replica family is the sharpest case: even at **zero lag** the digests differ, because canonical is hashed from mixed-EOL working-tree bytes while the chip receives all-CRLF. Same 206 rows, same content, different digest.

The cost is not the red pixel. It is that **an inequality nobody can act on stops being read.** `drift.git_dirty_vs_clean` had been unequal for days, was filed as an accepted oscillation, and was therefore pointing — unread — at a committed receipt that its own commit could not reproduce (`docs/receipts/control-plane/phase7_item76_receipt_correction_2026-07-26.md`). A permanently-unequal signal is indistinguishable from a broken one, and both get ignored.

## Decision

**5. Both sides of a drift signal MUST be the same kind and the same normalization.**

A comparison is well-formed only if `equal: true` is *reachable* — that is, only if some achievable state of the world makes the two byte-sets identical. Path against path. Object against object. Digest against digest **computed the same way**. Never prose against a path, never a label against an array, never a document against a JSON blob.

**6. A signal whose inequality is structural is not a drift signal.** Where two things legitimately differ forever — a deployment lagging its source, an anchor awaiting a co-sign that has not happened — that fact belongs in a signal with its **own relation** (`lag`, `absent`) whose `equal` is not the reading anyone acts on, and it must be **classified, dated and signed** rather than left to look like an unresolved fault.

**7. Extracting a locator from a document is capture, not judgment.** Pulling the cited *path* out of a prose line, so it can be compared against a path, is the same class of operation as `grepFirst`, which already runs a regex to find the line at all. `equal` stays a mechanical byte-compare. No severity, no verdict, no diff-percentage, no ranking. **GAIA LAW holds**: Gaia is still projecting what a source says, only now projecting the part of it that is comparable.

## Consequences

**Positive.** A red drift signal becomes actionable again, which is the only reason to have one. The distinction between *"this is wrong"* and *"these are different things"* stops being invisible. And the corrections already made today become **visible as progress** — `drift.gate_row_schema_path`'s side `b` moved from `""` to the real schema path when the pointers were fixed, and the malformed comparison could not express that.

**Negative.** Repairing a comparison changes what the platform **measures**, and a changed measurement can be a way to make a problem disappear. That is why this required a co-sign and why Decision 8 exists.

**8. Every repaired comparison must be proved to still bite** — point its declared side at a bad value and watch `equal` go `false` — and the before/after signal state must be captured on both sides of the change. A comparison repaired without that proof is indistinguishable from a comparison loosened.

## Alternatives considered

**Leave them and record all five as permanently unequal.** Rejected — it is what was already done, informally, in Phase 1, and it is how `drift.git_dirty_vs_clean` stopped being read while pointing at a live defect. `STRUCTURAL` must mean *"unequal by construction **and** both sides independently verified true, on this date, by this command"*. It must never mean *"unequal, stop looking"*.

**Add a tolerance so near-matches count as equal.** Rejected, and it is the most dangerous option on the list. For the replica family a tolerance would swallow the in-place-edit case — the *only* thing that family is for — in order to hide a lag that is deliberate and documented.

**Delete the malformed signals.** Rejected, and already mechanically prevented: `verify_gaia.cjs:513-518` requires the hints `fqdn`, `gate_row`, `resolver`, `git`, `self` to exist. The ledger was armed against silent removal before this amendment was written.

**Normalize line endings so the replica digests match.** Rejected as a fix *for this*: it would change how the canonical ledger is stored in order to satisfy a comparison, which is the tail wagging the dog. The comparison is what is wrong.

## Falsifier

A drift signal is added or retained whose `a` and `b` are of different kinds, or of the same kind under different normalization, such that no achievable state of the world yields `equal: true` — **and** which is not declared structural under Decision 6 with a relation that says so. Also falsified if a comparison is repaired without a mutation showing it still bites (Decision 8).
