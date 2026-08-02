# Phase A Audit Package

Append-only machine-readable record of the Phase A independent audit of
`9c3a644e4b57e8ac27f925dcec84222463063aa1`.

**Nothing in this package is a fix.** No production source file was modified in
Phase A. This directory records what was observed, under what identities, with
what predictions committed beforehand.

## Contents

| File | Contents |
|---|---|
| `phase-a-findings.md` | Narrative findings, corrections, and the STOP CONDITION |
| `package-manifest.json` | SHA-256 and byte count of every artifact below |
| `environment-matrix.json` | The four Node×npm cells and the provisioned runtime's provenance |
| `command-ledger.json` | Every command executed, with exit status |
| `source-integrity-manifest.json` | Independent verification of all 12 Tier-1 artifacts |
| `node-runtime-divergence.json` | Cross-runtime `runId` divergence evidence (CRITICAL) |
| `x01-empty-vs-full-cache.json` | Proof that X01 is invariant to the evidence it claims to verify |
| `crlf-mutation-result.json` | The CRLF corruption chain and each instrument's behaviour |
| `dependency-audit.json` | Production and development risk, reported separately |
| `wadhwa-raw-derived-verification.json` | Raw `.mat` → derived chain, and the three motor counts |
| `ito-archive-verification.json` | 4.09 GB archive verification and its MD5-only limitation |
| `phase-a-gate-ledger.json` | Every named gate with its actually-observed status |

### Addenda (added after the initial package; append-only)

| File | Contents |
|---|---|
| `c1-localization-addendum.json` | C1 divergence localized to `Math.pow`; retracts an earlier audit conclusion |
| `c2f-cache-state-matrix.json` | C2f empty / partial / corrupted / substituted cache states, executed |
| `x02-experimental-unit-contract.json` | X02A / X02B / X02S contract resolving the experimental-unit stop condition |
| `evidence-integrity-notes.json` | Decisions about the audit's own evidence bytes and digests |

## Deliberately excluded

Large binaries are **not** committed. Only identities, manifests, commands,
environments and results are preserved.

- The 4,085,227,742-byte Ito archive — identified by DOI, byte count, MD5, and a
  SHA-256 computed by this audit.
- The 75,001,736-byte Tier-1 source cache — identified by URL, byte count and
  SHA-256 per artifact.
- The 17,868,673-byte Wadhwa raw `.mat` — identified by repository, commit, path
  and SHA-256.

Every excluded artifact is retrievable from the URLs recorded in the manifests.

## Verifying this package

```bash
# every artifact's digest, recomputed
python - <<'PY'
import hashlib, json, pathlib
d = pathlib.Path("audits/phase-a")
man = json.loads((d / "package-manifest.json").read_text(encoding="utf-8"))
for a in man["artifacts"]:
    obs = hashlib.sha256((d / a["name"]).read_bytes()).hexdigest()
    print(("OK  " if obs == a["sha256"] else "FAIL"), a["name"])
PY
```

`package-manifest.json` is excluded from its own manifest, as it cannot contain
its own digest.

## Reading conventions

- `prediction` was recorded **before** execution; `observed` is the outcome.
  Where the two disagree the prediction is marked **REFUTED** and retained.
- `uncertainty`, `limitation` and `alternativeExplanation` are present on every
  artifact and are load-bearing, not boilerplate.
- `independentlyReproduced` states whether a second, non-repository oracle
  confirmed the result. Several say `false`. See `phase-a-findings.md` §5 for
  the full independence statement — notably, the cross-runtime divergence
  harness **does** import the implementation under test, by design, and is not
  claimed to be an independent oracle.
- No timestamps are recorded. This package must be byte-reproducible; ordering is
  established by git history.

## Relationship to `docs/audit/`

`docs/audit/PHASE-A-FINDINGS.md` was the earlier human-readable prose record.
It is retained unmodified as part of the append-only history. Where the two
disagree, **this package supersedes it** — specifically:

- the claim that `git status` reports a clean tree (retracted, §1.1);
- the claim that the 99-motor cohort does not exist (retracted, §1.6).
