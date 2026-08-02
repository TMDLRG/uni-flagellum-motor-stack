# Data specification

**Status, 2026-07-26: §1, §3 and §5 are BUILT, §1 has been corrected once, and §1 now PERSISTS** (`UNI.Minecraft` through `e6a0529` — `lib/sp/control_plane/`, 211 tests). **§2 (receipt) and §4 (scene node) remain DESIGN**, owned by phases 5 and 7.
Cross-referenced to the one schema that already exists and is enforced: `production/schemas/gate_row.schema.json` in `UNI.Minecraft`, guarded by `test/gate_registry_integrity_test.exs`.

**Three things this spec did not anticipate**, one of which is that the spec itself was wrong, recorded here so the next reader inherits them rather than rediscovering them:

- **The ledger's invariants do not cover tail truncation.** §1 lists "deleting any entry fails `verify/1`". That is true for the middle and false for the end: a prefix of a valid chain is a valid chain. `SP.ControlPlane.Store` now persists the anchor beside the ledger, so a reload that has lost its tail fails to attest — caught **in practice** against loss, corruption and accident. **Not** against a tamperer who owns the store directory and rewrites both; a test performs that attack and asserts it succeeds. Phase 5 item 5.1.
- **The gate row's own canonical ledger violated §3 in twelve places** — `pre_registration_path: null`, forbidden by `"type": "string"`. Remedied 2026-07-25 by eleven superseding rows; the twelve originals remain, because the file is append-only. See [`phases/PHASE-2-RESULTS.md`](phases/PHASE-2-RESULTS.md) §4.1.
- **§1's own `prior` rule was wrong**, and shipped enforced. See the correction note under §1.

Everything here must be expressible in **stdlib `JSON`** — the root app takes no hex dependency ([ADR-0006](decisions/ADR-0006-sp-controlplane-naming-and-placement.md)).

---

## 1. Ledger entry — `SP.ControlPlane.Ledger`

Append-only. Hash-chained. An entry is **never edited**; a correction is a new entry.

| field | type | req | meaning |
|-|-|-|-|
| `seq` | integer ≥ 1 | ✔ | position in the chain, contiguous, never reused |
| `utc` | ISO-8601 string | ✔ | human-readable instant |
| `unix_ns` | integer | ✔ | monotonic-ish precision; both are required, neither substitutes |
| `actor` | string | ✔ | who acted — a person, an agent, a service |
| `role` | string | ✔ | the authority under which they acted |
| `transition` | string | ✔ | what changed, in the controlled vocabulary |
| `prior` | object \| null | ✔ | state before; `null` for **any creation event**, at any `seq` |
| `resulting` | object | ✔ | state after |
| `authorization` | object | ✔ | `{kind, granted_by, ref}` — how this was permitted. **Optional `co_signers`**: an array of `{holder, kind, ref}`, added 2026-07-26 for airlocks, which need two parties. |
| `evidence` | array of `{path, sha256}` | ✔ | may be empty, may not be absent |
| `prev_hash` | 64-hex \| null | ✔ | `null` only for `seq = 1` |
| `hash` | 64-hex | ✔ | `sha256` over the canonical serialization of every field above |

**Invariants (each is a Phase 2 red test):** `hash` recomputes from content · `prev_hash` equals the previous entry's `hash` · editing any past entry fails `verify/1` · deleting any entry **from the middle** fails `verify/1` · `seq` is contiguous from 1.

> **EXTENDED 2026-07-26, Phase 6.** `authorization` gained an optional `co_signers` array. Phase 6 item 6.0 found that this row gave `authorization` a **single** `granted_by` while an airlock (F20) needs **two keys** — the entry had nowhere to put the second. The extension is **additive**: the seven entries already in the Control Plane ledger carry no `co_signers`, need none, and still verify, which a test asserts. When present, each co-signer must be a distinct party and none may be the actor — the same rule as the two-party check. This is the **second** correction to §1.

> **CORRECTED 2026-07-25, Phase 3.** This row originally read *"`null` only for `seq = 1`"*, and `Ledger` enforced it. **Both were wrong.** Registering a new gate as the fifth ledger entry genuinely has no prior state — the rule confused *the ledger's* first entry with *this subject's* first entry. It survived Phase 2 because nothing tested it; a rule with no test is a comment that happens to run. Supplying the right `prior` is the authoring module's job; chain integrity is the ledger's. See [`phases/PHASE-3-RESULTS.md`](phases/PHASE-3-RESULTS.md) §2.

## 2. Receipt — what makes a claim reproducible

| field | type | req | meaning |
|-|-|-|-|
| `receipt_id` | string | ✔ | stable id, referenced from the gate row |
| `decision_id` | string | ✔ | the decision this receipt establishes |
| `commit` | 40-hex | ✔ | the commit the claim was established at |
| `artifacts` | array of `{path, sha256, bytes}` | ✔ | content-addressed; must exist on disk |
| `logs` | array of paths | ✔ | may be empty |
| `reproduce_cmd` | string | ✔ | the exact command that regenerates the result |
| `env` | object | ✔ | code identity, runtime versions, platform, seeds |

**Invariant:** `receipt_path` in a gate row must resolve to a file on disk. This is **already enforced** by `test/gate_registry_integrity_test.exs` — extend it, do not duplicate it.

## 3. Gate row — already specified, already enforced

Do **not** redefine it. `production/schemas/gate_row.schema.json`, JSON Schema 2020-12, `additionalProperties: false`.

Required: `schema_version` (const 1) · `name` (kebab-case) · `verdict` (`PASS|PARTIAL|FAIL|WITHHELD|PENDING`) · `receipt_path` (must exist) · `evidence_class` (`A|B|C|Sec|pending`) · `last_updated` (date).
Optional: `phase` · `pass_condition` · `falsifies_condition` · `pre_registration_path` · `supersedes` · `notes`.

`SP.ControlPlane.GateRow` validates against this **in hand-written Elixir with stdlib `JSON`** — there is no schema library and there will not be one.

## 4. Scene node — the lab view's contract

Every node the renderer receives:

| field | type | req | meaning |
|-|-|-|-|
| `id` | string | ✔ | stable locator |
| `truth_class` | enum | ✔ | `OBSERVED · STRUCTURAL_RECONSTRUCTION · REDUCED_MODEL · DERIVED · SIMULATED · UNKNOWN` |
| `receipt_ref` | string \| null | ✔ | `null` is permitted and **renders as fog** |
| `evidence_class` | `A\|B\|C\|Sec\|pending` | ✔ | carried from the source, never invented |
| `captured_at` | ISO-8601 | ✔ | when this was true |
| `live` | `{up: true\|false\|null}` | ✖ | present only for a real probe result |

**The binding rule:** a node **missing `truth_class` or `receipt_ref` renders as fog**. That is not an error path — it is the honest depiction of an unbacked assertion. The renderer selects its material *from* `truth_class`; there is no style flag.

## 5. Drift comparison — `SP.ControlPlane.Drift`

| field | type | req |
|-|-|-|
| `a` | `{locator, raw, kind}` | ✔ |
| `b` | `{locator, raw, kind}` | ✔ |
| `relation` | `declared_vs_observed \| absent \| snapshot_vs_live \| self` | ✔ |
| `equal` | boolean | ✔ |

**The Phase 1 lesson, encoded:** construction **refuses** when `a.kind != b.kind`. A prose line may not be compared to a command's output. Four of Gaia's five slice-1 drifts do exactly that and can never converge; this type cannot be built that way.
