# Red tests — C1, C2, C3

**These tests are EXPECTED TO FAIL at `9c3a644e`.** They encode three assurance
defects found by the Phase A audit. They are not part of `npm test` and must not
be added to it until the corresponding defect is corrected.

A red test that passes here means either the defect was fixed (good) or the test
was weakened (forbidden by `CLAUDE.md:33-35`).

## Running

```bash
# C1 requires a second Node runtime with a different V8 major.
UNI_ALT_NODE=/path/to/other/node node --test tests/red/c1-cross-runtime-artifact-identity.test.mjs
node --test tests/red/c2-source-byte-gate.test.mjs
node --test tests/red/c3-raw-byte-identity.test.mjs
```

## Status at `9c3a644e`

| Test | Result | Fails because |
|---|---|---|
| C1 | **FAIL** | report SHA-256 differs across engines: `a485fa5a…` (Node 25) vs `d1753d25…` (Node 22.13.1) |
| C1a | **FAIL** | `Math.pow` digests differ across V8 12.4 / 14.1 |
| C2a | **FAIL** | no `NOT_RUN` status exists; vocabulary is `[PASS, FAIL, NOT_ESTABLISHED, BLOCKED_EXTERNAL]` |
| C2b | **FAIL** | no validator constrains status strings |
| C2c | **FAIL** | X01 evidence lacks `artifactsHashed` / `bytesHashed` |
| C2d | **FAIL** | X01 is `PASS` while 12 of 12 declared artifacts are absent |
| C2e | **FAIL** | the gate result derives from frozen `verified: true` literals |
| C2f × 4 | **SKIP** | cache-state matrix — `NOT RUN`, requires isolated worktree runs |
| C3a | **FAIL** | the two hash-pinned files carry different `eol` attributes |
| C3b | **FAIL** | one logical artifact has two on-disk identities |
| C3c | **FAIL** | hash-pinned evidence is still subject to eol filtering |
| C3d | **PASS** | see below — a genuine negative result |
| C3e | **FAIL** | regeneration changes the mirror; `git diff --numstat` reports nothing |

## C3d passes, and that matters

`C3d` verifies raw bytes across `core.autocrlf` `true`, `false` and `input`.
**It passes.** All three settings materialize
`experiments/data/wadhwa-2022-events.json` at 508,103 bytes and
`public/wadhwa-2022-derived-events.json` at 487,890 bytes, identically.

Explicit `.gitattributes` `eol` settings override `core.autocrlf`, so the
repository **is** correctly protected against platform variation. This is a
point in the repository's favour and it narrows the defect:

- **Not** a cross-platform portability bug.
- **Is** an intra-repository inconsistency: two paths carrying identical content
  are assigned different `eol` attributes, and `run-observed-experiments.mjs:35`
  copies raw bytes between them.

The correction is correspondingly narrower than "mark everything `-text`":

1. the generator must emit canonical LF rather than copying platform bytes
   (the pattern already exists at `scripts/run-science-gates.py:590`); and
2. the two paths must agree on their `eol` attribute, or both be `-text`.

## C1 cannot be fixed by raising the engines floor

Root cause: V8's `Math.pow` (and the equivalent `**` operator) is not
bit-reproducible across versions. At the fitted Weibull parameters
(`shape 0.625088844276203`, `scale 0.6996038164387606`), **418 of 4000** sampled
evaluations differ by 1 ULP between V8 12.4 and V8 14.1. `**` and `Math.pow`
agree *within* each runtime (0 of 4000), so the operator choice is irrelevant.

`lib/observed-experiment.js:178` evaluates `(y / scale) ** shape`, so Weibull
survival and log-scores inherit the difference, which propagates into the paired
advantage mean, the bootstrap interval, and finally `runId`.

**ECMA-262 permits `Math.pow` to be implementation-approximated.** Bit-identical
cross-engine results are therefore not guaranteed by the language. Pinning a
minimum Node version would work only by accident until the next V8 change, and
would not make the determinism claim true. Of the two remediation models the
directive posed, **Model A** — artifact identity includes runtime identity, so
exact replay is promised only inside a declared runtime — is the scientifically
correct contract. **Model B** (canonicalize precision before hashing) remains
viable but requires first proving that the chosen precision cannot move any
gate, ranking, interval crossing or conclusion. That proof has not been done.

Only 7 of 644 report fields diverge, and the 33 fitted parameters are
bit-identical, so the divergence enters **after** the fit, not inside it.
