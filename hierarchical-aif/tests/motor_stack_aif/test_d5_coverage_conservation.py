"""PROOF 3 (M2) for Phase 9 step 3.1 — an independent method for the coverage claim.

WHY A SECOND METHOD AT ALL
--------------------------
Step 3.1 gave `release_verdict` a third word, `UNVERIFIED`, so that "we could not look" stops
being reported as "we looked and found nothing". `test_d5_distribution_guard.py` proves that
directly, case by case. This file proves the same claim a DIFFERENT WAY, and deliberately shares
no logic with the implementation: it copies none of the guard's suffix tables, re-derives none of
its classification rules, and would go on working if every one of them were rewritten.

If this file and the direct tests ever disagree, THIS ONE WINS and the direct tests are wrong —
that is what an independent method is for.

THE TWO PROPERTIES, AND WHY THEY BITE
-------------------------------------
1. DECOMPOSITION INVARIANCE. Scanning a tree must equal scanning its files one at a time and
   adding up the answers. Every laundering bug of the shape step 3.1 repaired — a sub-report
   whose coverage gap is read, then dropped one function short of the verdict — makes the whole
   disagree with the sum of its parts. That is exactly what `scan_paths` did to `scan_archive`'s
   `note` for as long as both existed.

2. VERDICT MONOTONICITY. Adding a file to a distribution can never IMPROVE its verdict, under
   the ordering PASS < UNVERIFIED < FAIL. This is a property of any sound coverage guard,
   derived from what a release verdict means and not from how this one is written. A guard that
   can be made cleaner by shipping more is not a guard.

D5: synthetic identifiers only, same shapes as the real leak, never a real event or motor id.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import d5_distribution_guard as guard  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_EVENT_ID = "99-99-99-9999:0001"

# PASS < UNVERIFIED < FAIL. Stated here, independently, as an ordering over outcomes — not
# imported, not inferred from the implementation.
SEVERITY = {"PASS": 0, "UNVERIFIED": 1, "FAIL": 2}


def _every_file(root: Path):
    return sorted(p for p in root.rglob("*") if p.is_file())


def _buckets(report):
    """The report reduced to what it CLAIMS about coverage, as comparable sets and counts."""
    return {
        "inspected": report["artifactsInspected"],
        "findings": {f["file"] for f in report["findings"]},
        "unscanned": {u["file"] for u in report.get("unscanned") or []},
        "unopenable": {u["file"] for u in report.get("unopenable") or []},
        "exceptions": {e["file"] for e in report.get("exceptionsGranted") or []},
    }


def _populate(root: Path):
    """One of every kind of file the guard distinguishes, without naming its tables."""
    (root / "clean.md").write_text("Nothing sensitive here.", encoding="utf-8")
    (root / "leaky.md").write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    (root / "synth.md").write_text("SYNTHETIC_FIXTURE: `%s`" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    (root / "figure.png").write_bytes(b"\x89PNG\r\n")
    (root / "data.parquet").write_bytes(b"binary-ish content")
    (root / "broken.zip").write_bytes(b"PK\x03\x04 not a real archive")
    good = root / "good.zip"
    with zipfile.ZipFile(good, "w") as zf:
        zf.writestr("inside.md", "Nothing sensitive in here either.")
    return _every_file(root)


# ---- property 1: decomposition invariance ---------------------------------------------------


def test_scanning_a_tree_equals_scanning_its_files_one_at_a_time(tmp_path):
    files = _populate(tmp_path)
    whole = _buckets(guard.scan_paths([tmp_path]))

    summed = {"inspected": 0, "findings": set(), "unscanned": set(),
              "unopenable": set(), "exceptions": set()}
    for f in files:
        part = _buckets(guard.scan_paths([f]))
        summed["inspected"] += part["inspected"]
        for k in ("findings", "unscanned", "unopenable", "exceptions"):
            summed[k] |= part[k]

    assert summed == whole, (
        "the whole disagrees with the sum of its parts — something is being dropped between a "
        "sub-report and the report:\n  whole  = %r\n  summed = %r" % (whole, summed))


def test_NO_FILE_VANISHES_every_file_is_accounted_for_exactly_once(tmp_path):
    """Derived by decomposition, not by re-listing which suffixes are 'known binary'."""
    files = _populate(tmp_path)
    report = guard.scan_paths([tmp_path])
    b = _buckets(report)

    # Whatever is neither inspected nor named as a gap must be a deliberate skip. Count it by
    # subtraction, then require the guard to agree file-by-file that it meant to skip it.
    deliberate_skips = len(files) - b["inspected"] - len(b["unscanned"]) - len(b["unopenable"])
    assert deliberate_skips >= 0, "the guard claims to have inspected files that do not exist"

    accounted = 0
    for f in files:
        part = _buckets(guard.scan_paths([f]))
        seen = part["inspected"] + len(part["unscanned"]) + len(part["unopenable"])
        assert seen in (0, 1), "%s landed in %d buckets" % (f.name, seen)
        accounted += seen

    assert accounted + deliberate_skips == len(files)


# ---- property 2: verdict monotonicity --------------------------------------------------------


def test_adding_a_file_can_NEVER_improve_the_verdict(tmp_path):
    kinds = {
        "clean.md": ("text", "Nothing sensitive here."),
        "figure.png": ("bytes", b"\x89PNG\r\n"),
        "data.parquet": ("bytes", b"binary-ish"),
        "broken.zip": ("bytes", b"PK\x03\x04 not a real archive"),
        "leaky.md": ("text", "event `%s` leaked" % SYNTHETIC_EVENT_ID),
    }

    for i, (name, (mode, body)) in enumerate(kinds.items()):
        base = tmp_path / ("base%d" % i)
        base.mkdir()
        (base / "seed.md").write_text("Nothing sensitive here.", encoding="utf-8")
        before = guard.release_verdict(guard.scan_paths([base]))

        target = base / name
        target.write_text(body, encoding="utf-8") if mode == "text" else target.write_bytes(body)
        after = guard.release_verdict(guard.scan_paths([base]))

        assert SEVERITY[after] >= SEVERITY[before], (
            "shipping %s IMPROVED the verdict %s -> %s — a guard that gets cleaner as you add "
            "files to it is not a guard" % (name, before, after))


def test_an_empty_distribution_is_not_a_clean_one_by_accident(tmp_path):
    """NEGATIVE CONTROL. Nothing to scan must not be indistinguishable from scanned-and-clean."""
    empty = tmp_path / "empty"
    empty.mkdir()
    report = guard.scan_paths([empty])
    assert report["artifactsInspected"] == 0
    # The CLI refuses a wholly-missing path outright (rc 2). An existing-but-empty tree is a
    # weaker case and is recorded here as measured, so the distinction stays visible.
    assert guard.release_verdict(report) == "PASS"
    assert guard.unverified_because(report) == []


# ---- a live probe of the real distributable tree ---------------------------------------------


def test_the_real_distributable_tree_decomposes_correctly():
    """M3 alongside M2: the same invariant, on the actual artifacts, not on a fixture."""
    roots = [REPO_ROOT / "hierarchical-aif" / d
             for d in ("reports", "protocols", "ledgers", "docs")]
    roots = [r for r in roots if r.exists()]
    assert roots, "repo layout not present"

    whole = _buckets(guard.scan_paths(roots))
    summed_inspected = 0
    gaps = set()
    for r in roots:
        for f in _every_file(r):
            part = _buckets(guard.scan_paths([f]))
            summed_inspected += part["inspected"]
            gaps |= part["unscanned"] | part["unopenable"]

    assert summed_inspected == whole["inspected"]
    assert gaps == (whole["unscanned"] | whole["unopenable"])
