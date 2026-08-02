# H-AIF-G1 — Repo and Frozen-Evidence Integrity

**Gate:** H-AIF-G1 · **Executed:** 2026-07-21T16:39:52Z · **Maps to existing ladder:** `P0` computational integrity
**Status:** `ESTABLISHED`

> **Provenance note.** This work was originally requested as Phase-C closure work, but was
> namespaced under `hierarchical-aif/` to avoid collision with frozen `audits/phase-c/` evidence.
> The frozen Phase-C audits remain read-only source evidence.

---

## 1. Live repository identity

| item | value |
|-|-|
| local HEAD | `17a2f0e18c09c762ab1cefe854c0d68698803eac` |
| **remote HEAD** (`git ls-remote origin refs/heads/phase-2/b3-model-competition`) | `17a2f0e18c09c762ab1cefe854c0d68698803eac` |
| match | **YES — local == remote** |
| origin | `https://github.com/TMDLRG/UNI-FLAGELLUM.git` |
| review branch | `phase-2/b3-model-competition` (0 ahead / 0 behind) |
| work branch | `hierarchical-aif/motor-stack` (created from HEAD) |
| working tree | `git status --porcelain` → **0 lines** (pristine, including untracked) |
| commit object | `git cat-file -e HEAD^{commit}` → OK |
| author/date | Michael, 2026-07-21T00:52:48-05:00, "audit(phase-b): B4 identifiability & robustness result + PROSPECTIVE flip" |

This closes the reviewer's G1 objection that the earlier proofs were "a text dump, not a live
repository." `git ls-remote` performs a network call to GitHub and returns the remote ref
directly; it is not served from the local object cache.

## 2. Anchor ancestry — verified against the REMOTE branch

Every anchor is confirmed an ancestor of `origin/phase-2/b3-model-competition`, not merely of a
local ref:

| anchor | role | on remote branch |
|-|-|-|
| `e5b4969bd1af85cedc9d8b5b9d1d728bda7e906a` | B3 prediction-only | ✅ |
| `693feadefbfc495308e3d6b38ac21bc15b8c421c` | B4 prediction-only | ✅ |
| `e433ef9b92a8803208abc76a148016ef4b3c299b` | B4 `madeAgainstCommit` | ✅ |
| `4fcba6cad57c8df0bce3214fcaaf25b485d74281` | Phase-1 accepted anchor | ✅ |
| `17a2f0e18c09c762ab1cefe854c0d68698803eac` | B4 result | ✅ |

Strict-ancestry checks (`git merge-base --is-ancestor`, exit 0):
- `e433ef9b…` → `17a2f0e1…` — **strict ancestor**, 5 commits between
- `693fead…` → `17a2f0e1…` — **strict ancestor**, 4 commits between
- `e5b4969…` → B3 result commit — **strict ancestor**

The B4 prediction-only commit `693fead` changed exactly four files (protocol, predictions,
manifest, prediction record) and **contains no result file**.

## 3. Frozen evidence integrity

`audits/phase-c/**` and `audits/phase-d/**` are **read-only historical evidence.**

| check | result |
|-|-|
| `git diff 4fcba6cad57c8df0bce3214fcaaf25b485d74281 HEAD -- audits/phase-c` | **empty** → byte-identical |
| `git diff 4fcba6cad57c8df0bce3214fcaaf25b485d74281 HEAD -- audits/phase-d` | **empty** → byte-identical |
| frozen files hashed | **250** (`audits/phase-c` 64 + `audits/phase-d` 186) |
| baseline manifest | `hierarchical-aif/reports/frozen-evidence-baseline.sha256` |

Any future diff against that manifest is a contract violation. The manifest was recorded
**before** any hierarchical-aif work began.

## 4. Namespace separation

`hierarchical-aif/` did not exist prior to this gate, so the new work is trivially separate from
frozen evidence. Initial file list: `hierarchical-aif/reports/hierarchical-aif-file-list.initial.txt`.

Directory contract in force:

```text
audits/phase-c/          frozen evidence, read-only
audits/phase-d/          frozen evidence, read-only
hierarchical-aif/docs/       new model audit and gate docs
hierarchical-aif/src/        new isolated implementation
hierarchical-aif/tests/      new tests
hierarchical-aif/results/    new run outputs
hierarchical-aif/ledgers/    new ledger patches
hierarchical-aif/reports/    run reports
hierarchical-aif/protocols/  prospective protocols and predictions
hierarchical-aif/scripts/    helper scripts
```

No work is created under `phase-c/`, `docs/phase-c/`, `tests/phase-c/`, or `results/phase-c/`.

## 5. Supporting integrity checks re-run at this gate

Re-verified at HEAD on 2026-07-21 (all from the submitted package, all still passing):

| check | result |
|-|-|
| `python audits/phase-b/b3-preflight.py` | **46/46** |
| `python audits/phase-b/b3-independent-oracle.py` | **44/44** |
| `python audits/phase-b/b4-independent-oracle.py` | **43/43** |
| B4 assembler determinism (2 runs, committed aliases) | both `f361e4dc…1807f3`, byte-identical to committed |
| `package-manifest.json` re-hash | **43/43** match, 0 missing, 0 mismatch |
| LF-only on 14 new/modified B4 files | **0** CR bytes |
| plan §7 baseline | all green except the two permitted non-passes (`cross-study:verify-raw` `BLOCKED_EXTERNAL`; `npm audit` dev-only) |

**These integrity receipts are unaffected by defects D1–D4.** D1–D4 concern the *scientific
interpretation* of specific B4 cells and the *credibility of recorded resource claims* — not the
packaging, hashing, determinism, or provenance machinery, which independently verify clean.

## 6. Verdict

```text
H-AIF-G1 = ESTABLISHED
maps to: P0 computational integrity
```

Preconditions for proceeding to H-AIF-G2 are met: the live repo state is proven, frozen evidence
is proven unmodified and hash-baselined, and the new namespace is proven separate.

**No P-level above P0 is moved by this gate.**
