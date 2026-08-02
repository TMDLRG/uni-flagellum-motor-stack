"""Build the D5-safe successor archive and round-trip verify it (D12 step 4).

Pipeline (per the M25 authorization):
  1. build from a named anchor commit (default HEAD)
  2. stage a CURATED allowlist (leak-bearing files are excluded, not included-then-hoped-clean)
  3. scan the staged tree with d5_distribution_guard  -> must be 0 findings, 0 unscanned
  4. generate the manifest (sha256 per file)
  5. create the archive (deterministic zip)
  6. unpack it into a clean directory
  7. rescan the unpacked archive  -> must be 0 findings
  8. recompute every manifest entry from the unpacked tree  -> must match staged
  9. confirm no .git blobs, *.bundle, or *.patch were reintroduced
 10. include the withdrawal notice + D12 report (they are inside the staged reports/ tree) plus a
     SANITIZED ANCESTRY RECEIPT (commit metadata only, no blob history) and a supersede README

The guard's release_verdict() is the single authority on the verdict, and since Phase 9 step 3.1
it has THREE words, not two: FAIL (a finding survived), UNVERIFIED (the guard could not look
everywhere), PASS (it looked everywhere it covers and found nothing). This script has always
required PASS and nothing else, and separately re-checked `unscanned` at step 3 — which is to say
its author already knew the two-word verdict was inadequate and compensated locally rather than
fixing the guard. That local compensation is now redundant and is kept anyway: a build that
fail-closes twice is not worse than one that fail-closes once.

This script reads only git metadata and the redacted working tree; it reproduces no held-out value.
Deterministic: git archive pins file contents to the anchor commit; the zip uses a fixed timestamp
and sorted order, so the package sha256 is stable across rebuilds from the same anchor.
"""
from __future__ import annotations

import hashlib
import io
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "hierarchical-aif" / "src"
sys.path.insert(0, str(SRC))
from motor_stack_aif import d5_distribution_guard as guard  # noqa: E402

# ---- curated allowlist: the closure NARRATIVE + the guards. Everything carrying held-out identity
# is EXCLUDED by omission (raw/served datasets, per-motor result JSONs, frozen audits, and the
# identifier-bearing regression fixture). The guard proves the omission worked.
INCLUDES = [
    "CLAUDE.md",
    "hierarchical-aif/README.md",
    "hierarchical-aif/docs",
    "hierarchical-aif/ledgers",
    "hierarchical-aif/protocols",
    "hierarchical-aif/reports",
    "hierarchical-aif/src/motor_stack_aif/claim_guard.py",
    "hierarchical-aif/src/motor_stack_aif/numeric_provenance_guard.py",
    "hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py",
    "hierarchical-aif/tests/motor_stack_aif/test_d5_distribution_guard.py",
]
# Documented, deliberate exclusions (recorded in the README so a recipient knows what is NOT here).
DOCUMENTED_EXCLUSIONS = [
    ("hierarchical-aif/tests/motor_stack_aif/test_nextstate_range_check.py",
     "functional D6 regression fixture pins real event identifiers; excluded from distribution, "
     "not redacted (would make the test vacuous)"),
    ("hierarchical-aif/results/**",
     "per-motor result artifacts carry holdout motor ids / mark tuples; referenced by hash in the "
     "reports instead"),
    ("audits/**", "frozen historical evidence carrying the motor id; referenced by hash"),
    ("experiments/**, public/wadhwa-2022-derived-events.json",
     "raw and served held-out event-level datasets"),
    (".git, *.bundle, *.patch",
     "no git history/blobs/bundles: the withdrawn material lives in history and must not ride along"),
]
FORBIDDEN_IN_PACKAGE = (".bundle", ".patch")
FORBIDDEN_NAMES = (".git",)

WITHDRAWN_ARCHIVE = "UNI-FLAGELLUM-haif-closure-e21747c.zip"
WITHDRAWN_SHA256 = "7b28f0d6f338cb2fa077d3a84fe9688c44a67cb813e513f27a1a0348113d41b2"
ANCESTRY_COMMITS = ["e21747c", "da89a41", "HEAD"]
FIXED_ZIP_DT = (1980, 1, 1, 0, 0, 0)   # deterministic zip entry timestamp


def sh(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args],
                          check=True, capture_output=True, text=True).stdout


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def stage(anchor: str, staging: Path) -> None:
    """Extract the allowlist from the anchor commit into a clean staging dir."""
    if staging.exists():
        import shutil
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    tar_bytes = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "archive", "--format=tar", anchor, "--", *INCLUDES],
        check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tf:
        try:
            tf.extractall(staging, filter="data")   # py3.12 safe extraction
        except TypeError:
            tf.extractall(staging)


def write_ancestry_receipt(staging: Path, anchor_full: str) -> None:
    lines = [
        "# Sanitized Git Ancestry Receipt",
        "",
        "**Class:** `GIT_ANCESTRY_RECEIPT_PROVIDED; FULL_HISTORY_RECONSTRUCTION_NOT_INCLUDED`",
        "",
        "Full blob history is **deliberately excluded** from this package: commits at and before",
        "`e21747c` contain the withdrawn, unredacted held-out mark identifiers (defect D12). Shipping",
        "a git bundle or `.git` directory would carry those blobs and recreate the exposure inside a",
        "package that is supposed to be D5-safe. This receipt therefore provides commit *metadata and",
        "file name-status only* — never a diff, never blob contents.",
        "",
        "## Commit chain (metadata, no patch)",
        "",
        "```text",
        sh("show", "--no-patch", "--format=raw", *[c for c in ANCESTRY_COMMITS]).strip(),
        "```",
        "",
        "## Path name-status for the D12 anchor (names + status letters only, no content)",
        "",
        "```text",
        sh("show", "--no-patch", "--format=%H %s", "HEAD").strip(),
        sh("diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD").strip(),
        "```",
        "",
        "## Exact commands used to build this package",
        "",
        "```bash",
        "git archive --format=tar <anchor> -- \\",
        *["  %s \\" % i for i in INCLUDES],
        "  | tar -x -C <staging>",
        "python hierarchical-aif/scripts/build_d5_safe_successor_archive.py",
        "```",
        "",
        "**Anchor commit:** `%s`" % anchor_full,
        "",
        "Verify this receipt's own integrity against the package manifest (`MANIFEST-SHA256.txt`).",
    ]
    (staging / "ANCESTRY-RECEIPT.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_readme(staging: Path, anchor_short: str, archive_name: str) -> None:
    excl = "\n".join("- `%s` — %s" % (p, why) for p, why in DOCUMENTED_EXCLUSIONS)
    text = f"""# UNI-FLAGELLUM H-AIF closure evidence — D5-SAFE successor package

**Anchor commit:** `{anchor_short}` · **Package:** `{archive_name}`
**Class:** D5-safe curated closure-evidence package.

## This package SUPERSEDES but does NOT erase a withdrawn one

It supersedes `{WITHDRAWN_ARCHIVE}`
(sha256 `{WITHDRAWN_SHA256}`), which is **`WITHDRAWN_D5_UNSAFE`**: that archive carried real
event-level held-out mark identifiers. Withdrawing it does not recall copies already distributed —
that residual is permanent (incident state `NEGATIVE`). See
`hierarchical-aif/reports/D12-INCIDENT-CONTAINMENT-REPORT.md`.

## What is IN this package

The human-readable closure **narrative** and the mechanical **guards** only:
CLAUDE.md; hierarchical-aif/{{README, docs, ledgers, protocols, reports}}; the three guards
(claim_guard, numeric_provenance_guard, d5_distribution_guard) and the d5 guard's synthetic-only
test. Every file was scanned by `d5_distribution_guard` at both staging and post-unpack (round-trip):
**0 findings, 0 unscanned.**

## What is deliberately NOT in this package (and why)

{excl}

Because the per-motor result artifacts and frozen audits are excluded, the reports cite their frozen
results **by sha256 hash** rather than shipping the identifier-bearing JSON. A recipient verifies the
narrative's internal consistency and reproduces the guards; the excluded artifacts are available only
through a D5-firewalled channel.

## Verify this package yourself

```bash
# 1. per-file integrity
sha256sum -c MANIFEST-SHA256.txt        # (paths relative to this package root)
# 2. re-run the distribution guard over the whole package — must print 0 findings
python hierarchical-aif/src/motor_stack_aif/d5_distribution_guard.py .
```

The package sha256 is recorded separately in
`hierarchical-aif/reports/D12-SUCCESSOR-ARCHIVE-RECEIPT.md` in the repository (not inside this
package, which cannot contain its own hash).
"""
    (staging / "README-D5-SAFE-SUCCESSOR.md").write_text(text, encoding="utf-8", newline="\n")


def manifest_over(root: Path, exclude_names=("MANIFEST-SHA256.txt",)) -> list:
    rows = []
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()
        if p.name in exclude_names:
            continue
        rows.append((sha256_file(p), rel))
    return rows


def assert_no_forbidden(root: Path) -> None:
    for p in root.rglob("*"):
        if p.name in FORBIDDEN_NAMES or (p.is_dir() and p.name == ".git"):
            raise SystemExit("FORBIDDEN in package: %s" % p)
        if p.suffix.lower() in FORBIDDEN_IN_PACKAGE:
            raise SystemExit("FORBIDDEN in package: %s" % p)


def build_zip(staging: Path, archive: Path) -> None:
    files = sorted(p for p in staging.rglob("*") if p.is_file())
    if archive.exists():
        archive.unlink()
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in files:
            zi = zipfile.ZipInfo(p.relative_to(staging).as_posix(), date_time=FIXED_ZIP_DT)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            zf.writestr(zi, p.read_bytes())


def scan_or_die(root: Path, label: str) -> dict:
    report = guard.scan_paths([root])
    verdict = guard.release_verdict(report)
    print("  [%s] artifacts=%d findings=%d unscanned=%d verdict=%s"
          % (label, report["artifactsInspected"], len(report["findings"]),
             len(report.get("unscanned", [])), verdict))
    if verdict != "PASS":
        for f in report["findings"]:
            print("    FINDING", f["kind"], f["file"])
        raise SystemExit("FAIL-CLOSED at %s: guard verdict %s" % (label, verdict))
    if report.get("unscanned"):
        for u in report["unscanned"]:
            print("    UNSCANNED", u["file"], u["suffix"])
        raise SystemExit("FAIL-CLOSED at %s: %d unscanned files (coverage gap)"
                         % (label, len(report["unscanned"])))
    return report


def main() -> int:
    anchor = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    anchor_full = sh("rev-parse", anchor).strip()
    anchor_short = anchor_full[:7]
    archive_name = "UNI-FLAGELLUM-haif-closure-%s-D5SAFE.zip" % anchor_short
    archive = REPO_ROOT.parent / archive_name

    scratch = Path(__file__).resolve().parents[0] / "_d5safe_build"
    staging = scratch / "staging"
    unpacked = scratch / "unpacked"

    print("D12 successor-archive build")
    print("  anchor:", anchor_full)
    print("  archive:", archive)

    # 2. stage the allowlist
    stage(anchor_full, staging)
    write_ancestry_receipt(staging, anchor_full)
    write_readme(staging, anchor_short, archive_name)
    staged_manifest = manifest_over(staging)
    (staging / "MANIFEST-SHA256.txt").write_text(
        "\n".join("%s  %s" % (h, rel) for h, rel in staged_manifest) + "\n",
        encoding="utf-8", newline="\n")

    # 3. scan staged tree (fail-closed)
    print("staging scan:")
    staged_report = scan_or_die(staging, "staged")
    assert_no_forbidden(staging)

    # 4-5. build the archive
    build_zip(staging, archive)
    pkg_sha = sha256_file(archive)

    # 6. unpack
    if unpacked.exists():
        import shutil
        shutil.rmtree(unpacked)
    unpacked.mkdir(parents=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(unpacked)

    # 7. rescan unpacked (fail-closed)
    print("round-trip (unpacked) scan:")
    unpacked_report = scan_or_die(unpacked, "unpacked")
    assert_no_forbidden(unpacked)

    # 8. recompute manifest from unpacked, compare
    unpacked_manifest = manifest_over(unpacked)
    if unpacked_manifest != staged_manifest:
        print("  MANIFEST MISMATCH staged vs unpacked")
        s, u = dict((r, h) for h, r in staged_manifest), dict((r, h) for h, r in unpacked_manifest)
        for rel in sorted(set(s) | set(u)):
            if s.get(rel) != u.get(rel):
                print("    DIFF", rel, s.get(rel), "!=", u.get(rel))
        raise SystemExit("FAIL: round-trip manifest mismatch")

    verdict = "PASS"
    print("ROUND-TRIP VERDICT:", verdict)
    print("  package sha256:", pkg_sha)
    print("  files:", len(staged_manifest))

    # 15. write receipts into the repo (critical info lives in-repo)
    reports = REPO_ROOT / "hierarchical-aif" / "reports"
    (reports / "D12-SUCCESSOR-ARCHIVE-MANIFEST-SHA256.txt").write_text(
        "\n".join("%s  %s" % (h, rel) for h, rel in staged_manifest) + "\n",
        encoding="utf-8", newline="\n")

    receipt = [
        "# D12 Successor-Archive — Build & Round-Trip Receipt",
        "",
        "**Remediation gate:** `PASS` (this receipt) — the successor archive survived staging and",
        "round-trip scans. **Incident state stays `NEGATIVE` permanently** (see D12 report); a PASS",
        "here means the *forward* package is D5-safe, not that the prior distribution was recalled.",
        "",
        "| field | value |",
        "|-|-|",
        "| anchor commit | `%s` |" % anchor_full,
        "| package name | `%s` |" % archive_name,
        "| package location | repository parent dir (beside the withdrawn archive) |",
        "| **package sha256** | `%s` |" % pkg_sha,
        "| files in package | %d |" % len(staged_manifest),
        "| staged scan | %d artifacts, %d findings, %d unscanned, verdict PASS |"
        % (staged_report["artifactsInspected"], len(staged_report["findings"]),
           len(staged_report.get("unscanned", []))),
        "| round-trip scan | %d artifacts, %d findings, %d unscanned, verdict PASS |"
        % (unpacked_report["artifactsInspected"], len(unpacked_report["findings"]),
           len(unpacked_report.get("unscanned", []))),
        "| round-trip manifest | staged == unpacked (byte-identical per-file sha256) |",
        "| forbidden content | no `.git`, no `*.bundle`, no `*.patch` |",
        "| supersedes (withdrawn) | `%s` sha256 `%s` `WITHDRAWN_D5_UNSAFE` |"
        % (WITHDRAWN_ARCHIVE, WITHDRAWN_SHA256),
        "| ancestry | `GIT_ANCESTRY_RECEIPT_PROVIDED; FULL_HISTORY_RECONSTRUCTION_NOT_INCLUDED` |",
        "| transmission | principal-gated — build is authorized, sending is not |",
        "",
        "Per-file manifest: `hierarchical-aif/reports/D12-SUCCESSOR-ARCHIVE-MANIFEST-SHA256.txt`.",
        "Rebuild: `python hierarchical-aif/scripts/build_d5_safe_successor_archive.py %s`" % anchor_short,
        "",
        "The build is deterministic (git archive pins contents to the anchor; the zip uses a fixed",
        "timestamp and sorted order), so re-running from the same anchor reproduces the package sha256.",
    ]
    (reports / "D12-SUCCESSOR-ARCHIVE-RECEIPT.md").write_text(
        "\n".join(receipt) + "\n", encoding="utf-8", newline="\n")
    print("wrote receipts to hierarchical-aif/reports/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
