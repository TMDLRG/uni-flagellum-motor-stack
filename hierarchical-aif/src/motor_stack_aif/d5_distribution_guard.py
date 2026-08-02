"""D12 — the distribution guard: no shipped artifact may carry a real held-out mark identity.

WHY THIS EXISTS (separate responsibility from the other two guards)
---------------------------------------------------------------------
`claim_guard.py` clamps forbidden WORDING. `numeric_provenance_guard.py` clamps declared numeric
PROVENANCE. Neither checks for LEAKED IDENTITY: a real event id, a real motor id tied to the D6
mark defect, or a reconstructable held-out record tuple, surviving in a document a reviewer or the
public will read. The external D5 safety review found exactly that — in prose reports, a protocol,
a defect ledger, and (crucially) a `.py` test fixture the review's own JSON/JSONL/Markdown-scoped
scan could not see. This guard closes that scope gap and is the mechanical gate for D12 release.

WHAT IT DETECTS
----------------
  EVENT_ID                 - the real event-id shape: `DD-DD-DD-DDDD:DDDD` (motor-date-time:seq).
  MOTOR_ID_MARK_CONTEXT     - the motor-id shape `DD-DD-DD-DDDD` appearing within MARK_CONTEXT_WINDOW
                              characters of a mark-defect context word (holdout, mark, nextStateN,
                              impossible, defect, burned, quarantine...). A bare motor id with no
                              such context does NOT fire - motor ids appear throughout legitimate,
                              non-sensitive text.
  RECORD_SHAPED_TUPLE       - >=2 of {stateN, nextStateN, jump, direction} co-occurring with a
                              holdout/partition label in the same line, WITH an assigned value
                              (`stateN=0`, `stateN: 0`) - never a bare field name in a schema
                              listing (see SCHEMA_PROSE below).

WHAT IT DELIBERATELY DOES NOT FIRE ON
--------------------------------------
  SCHEMA_PROSE   - a field-name listing with no assigned value ("`stateN` (integer)") is
                   declaration, not a record. Distinguished by requiring `=` or `: <value>` after
                   the field name before a tuple counts as value-bearing.
  SYNTHETIC_FIXTURE - a line explicitly marked `SYNTHETIC_FIXTURE` is exempt and named in the
                   `exceptionsGranted` list of the report, never silently dropped.

SCOPE
-----
Structurally parses `.json` / `.jsonl` (walks every string VALUE, not just keys). Textually scans
`.md`, `.txt`, `.py`, log and manifest files. Inspects nested `.zip` archives one level by
extracting to a temp dir and recursing; an archive member that cannot be read as text/JSON is
reported under `nestedArchivesRejected`, never silently treated as clean.

RELEASE FALSIFIER — THREE WORDS, NOT TWO (F29/F30, Phase 9 step 3.1)
--------------------------------------------------------------------
`release_verdict(report)` returns:

    FAIL        a finding survived. Something was found. Outranks everything below.
    UNVERIFIED  the guard COULD NOT LOOK everywhere — an archive would not open, a member
                could not be read, or a file's suffix is neither in-scope nor known-binary.
    PASS        the guard looked everywhere it claims to cover, and found nothing.

It returned only FAIL and PASS until 2026-07-27, and that was a live violation of two declared
refusals, F29 and F30 in `docs/control-plane/FAILURE-MODES.md`:

    F29 | an archive cannot be opened           | report UNVERIFIED | it is treated as clean
    F30 | files in a distribution are unscanned | fail closed       | PASS with unscanned files

The words were already written and simply had no consumer. `scan_archive` returned a `note`
reading "archive could not be opened - treated as UNVERIFIED, not clean", and `scan_paths` took
`sub["findings"]` and dropped the note on the floor. `scan_paths` has collected `unscanned` since
it was written, with a docstring promising "a skipped file is NOT a clean file... a caller can
fail on it", and the verdict function never looked at it. **We could not look** and **we looked
and found nothing** are different states, and they were reported with the same word.

A third word is worth nothing if the exit code still has two, so `main()` now exits 0 ONLY on
PASS. `unverified_because(report)` names every gap in words a human can act on: a coverage gap
nobody can locate is a coverage gap nobody will close.

This function remains the only place the verdict is computed, so it cannot drift from the
detectors above.

D5: this module reads only file STRUCTURE and TEXT to run pattern detection. It contains no real
held-out identifiers; its own tests use synthetic examples of the same shape.
"""
from __future__ import annotations

import json
import re
import tempfile
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

EVENT_ID_RE = re.compile(r"\b\d{2}-\d{2}-\d{2}-\d{4}:\d{4}\b")
MOTOR_ID_RE = re.compile(r"\b\d{2}-\d{2}-\d{2}-\d{4}\b")

MARK_CONTEXT_WORDS = (
    "holdout", "mark", "marks", "nextstate", "next_state", "impossible", "defect",
    "burned", "quarantine", "d5", "d6", "reflecting-boundary", "stator count",
)
MARK_CONTEXT_WINDOW = 160  # characters of surrounding text searched for a context word

TUPLE_FIELDS = ("staten", "nextstaten", "jump", "direction")
HOLDOUT_LABELS = ("holdout", "partition=holdout", "partition: holdout", "partition\": \"holdout")
# a field counts as VALUE-BEARING only if followed by `=` or `:` and then a value (not just "(type)")
VALUE_BEARING_RE = re.compile(
    r"\b(staten|nextstaten|jump|direction)\b\s*[:=]\s*[\"']?-?\w", re.IGNORECASE)

SYNTHETIC_MARKER = "SYNTHETIC_FIXTURE"

TEXT_SUFFIXES = {".md", ".txt", ".py", ".log", ".yaml", ".yml", ".ini", ".cfg",
                 ".html", ".htm", ".csv", ".tsv", ".mjs", ".js", ".ts", ".sha256", ".sha", ".sums"}
JSON_SUFFIXES = {".json", ".jsonl"}
# Suffixes we KNOW are non-textual and intentionally do not scan. Anything not in
# TEXT_SUFFIXES | JSON_SUFFIXES | KNOWN_BINARY_SUFFIXES is reported as UNSCANNED so coverage is
# never silent (a skipped file is not a clean file).
KNOWN_BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".mov", ".pdf",
                         ".zip", ".gz", ".tar", ".woff", ".woff2", ".ico", ".pyc"}


def _has_mark_context(text: str, span_start: int, span_end: int) -> bool:
    window = text[max(0, span_start - MARK_CONTEXT_WINDOW): span_end + MARK_CONTEXT_WINDOW].lower()
    return any(w in window for w in MARK_CONTEXT_WORDS)


def _is_record_shaped(line: str) -> bool:
    lowered = line.lower()
    value_bearing_fields = {m.group(1).lower() for m in VALUE_BEARING_RE.finditer(line)}
    if len(value_bearing_fields) < 2:
        return False
    has_holdout_label = any(lbl in lowered for lbl in HOLDOUT_LABELS) or "partition" in lowered and "holdout" in lowered
    return has_holdout_label


def scan_text(text: str, source: str) -> list:
    """Scan raw text (one file's contents, or one JSON string value) for leak patterns."""
    if SYNTHETIC_MARKER in text:
        return []
    findings = []

    for m in EVENT_ID_RE.finditer(text):
        findings.append({"kind": "EVENT_ID", "file": source, "match": "<REDACTED event-level identifier>"})

    for m in MOTOR_ID_RE.finditer(text):
        if EVENT_ID_RE.match(text, m.start()):
            continue  # already counted as part of a full event id
        if _has_mark_context(text, m.start(), m.end()):
            findings.append({"kind": "MOTOR_ID_MARK_CONTEXT", "file": source,
                              "match": "<REDACTED motor identifier>"})

    for line in text.splitlines():
        if _is_record_shaped(line):
            findings.append({"kind": "RECORD_SHAPED_TUPLE", "file": source,
                              "match": "<REDACTED record-shaped mark tuple>"})

    return findings


def scan_json(node, source: str, _path: str = "") -> list:
    """Structurally parse JSON/JSONL: walk every string VALUE, not just keys."""
    findings = []
    if isinstance(node, dict):
        for k, v in node.items():
            findings.extend(scan_json(v, source, _path + "." + str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            findings.extend(scan_json(v, source, "%s[%d]" % (_path, i)))
    elif isinstance(node, str):
        findings.extend(scan_text(node, source))
    return findings


def _scan_json_file(path: Path) -> list:
    text = path.read_text(encoding="utf-8", errors="replace")
    source = str(path).replace("\\", "/")
    findings = []
    if path.suffix == ".jsonl":
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                doc = json.loads(line)
            except Exception:
                findings.extend(scan_text(line, source))
                continue
            findings.extend(scan_json(doc, source))
    else:
        try:
            doc = json.loads(text)
        except Exception:
            findings.extend(scan_text(text, source))
        else:
            findings.extend(scan_json(doc, source))
    return findings


def scan_file(path: Path) -> list:
    source = str(path).replace("\\", "/")
    if SYNTHETIC_MARKER and path.suffix in TEXT_SUFFIXES:
        text = path.read_text(encoding="utf-8", errors="replace")
        if SYNTHETIC_MARKER in text:
            return []
    if path.suffix in JSON_SUFFIXES:
        return _scan_json_file(path)
    if path.suffix in TEXT_SUFFIXES:
        text = path.read_text(encoding="utf-8", errors="replace")
        return scan_text(text, source)
    return []  # binary / out-of-scope suffix: not scanned, not claimed clean


def scan_archive(path: Path, _depth: int = 0) -> dict:
    """Inspect a zip archive: structurally scan every member; recurse one level into nested zips."""
    findings = []
    inspected, rejected = 0, 0
    nested_inspected, nested_rejected = 0, 0
    unopenable = []
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        try:
            with zipfile.ZipFile(path) as zf:
                zf.extractall(tdp)
        except Exception as exc:
            # F29. This branch has always said the right words; until Phase 9 step 3.1 nothing
            # upstream read them, so an archive nobody could open reached the verdict as PASS.
            # `unopenable` is a LIST OF NAMES, not a count: a coverage gap nobody can locate is
            # a coverage gap nobody will close.
            return {"artifact": str(path), "findings": [], "artifactsInspected": 0,
                    "nestedArchivesInspected": 0, "nestedArchivesRejected": 1,
                    "membersRejected": 0, "exceptionsGranted": [], "opened": False,
                    "unopenable": [{"file": str(path).replace("\\", "/"),
                                    "why": type(exc).__name__}],
                    "note": "archive could not be opened - treated as UNVERIFIED, not clean"}
        for p in sorted(tdp.rglob("*")):
            if p.is_dir():
                continue
            # A member's name inside a temp dir is meaningless to a reader. Name it the way a
            # human would look for it: <archive>::<path inside the archive>.
            member = "%s::%s" % (str(path).replace("\\", "/"),
                                 p.relative_to(tdp).as_posix())
            if p.suffix == ".zip":
                if _depth >= 1:
                    # Not "could not", but "did not" — and a gap is a gap either way. Recorded
                    # rather than counted, so the reader knows WHICH archive went uninspected.
                    nested_rejected += 1
                    unopenable.append({"file": member, "why": "depth_limit"})
                    continue
                sub = scan_archive(p, _depth=_depth + 1)
                findings.extend(sub["findings"])
                nested_inspected += 1
                nested_inspected += sub.get("nestedArchivesInspected", 0)
                nested_rejected += sub.get("nestedArchivesRejected", 0)
                for u in sub.get("unopenable", []):
                    unopenable.append({"file": member if u["file"].endswith(p.name)
                                       else "%s::%s" % (member, u["file"]),
                                       "why": u.get("why", "unopenable")})
                continue
            try:
                findings.extend(scan_file(p))
                inspected += 1
            except Exception as exc:
                rejected += 1
                unopenable.append({"file": member, "why": type(exc).__name__})
    return {
        "artifact": str(path),
        "findings": findings,
        "artifactsInspected": inspected,
        "nestedArchivesInspected": nested_inspected,
        "nestedArchivesRejected": nested_rejected,
        "membersRejected": rejected,
        "unopenable": unopenable,
        "opened": True,
        "exceptionsGranted": [],
    }


def scan_paths(paths) -> dict:
    """Scan a staged tree (list of files/dirs). Returns the machine-readable report.

    `unscanned` names every file whose suffix is neither in-scope nor a known binary — a skipped
    file is NOT a clean file, so coverage is made explicit and a caller can fail on it.
    """
    findings = []
    inspected = 0
    exceptions = []
    unscanned = []
    unopenable = []
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(root.rglob("*"))
        for p in files:
            if p.is_dir():
                continue
            if p.suffix == ".zip":
                sub = scan_archive(p)
                findings.extend(sub["findings"])
                # F29. This line is the repair: the archive's own account of what it could NOT
                # look at used to stop here, one function short of the verdict.
                unopenable.extend(sub.get("unopenable", []))
                # `inspected += 1` used to run BEFORE this call, so an archive that would not
                # open was counted as inspected — the artifact count itself claimed "we looked"
                # about the one file nobody could look at. Found by the independent method
                # (test_d5_coverage_conservation.py), which noticed it landing in two buckets
                # at once, and not by the direct F29 tests, which never asked about the count.
                if sub.get("opened", True):
                    inspected += 1
                continue
            if p.suffix in TEXT_SUFFIXES:
                text = p.read_text(encoding="utf-8", errors="replace")
                if SYNTHETIC_MARKER in text:
                    inspected += 1
                    exceptions.append({"file": str(p).replace("\\", "/"),
                                        "reason": "SYNTHETIC_FIXTURE marker"})
                    continue
            if p.suffix in TEXT_SUFFIXES or p.suffix in JSON_SUFFIXES:
                inspected += 1
                findings.extend(scan_file(p))
            elif p.suffix.lower() in KNOWN_BINARY_SUFFIXES:
                continue  # known non-textual; intentionally not scanned
            else:
                unscanned.append({"file": str(p).replace("\\", "/"), "suffix": p.suffix})
    return {
        "artifactsInspected": inspected,
        "findings": findings,
        "exceptionsGranted": exceptions,
        "unscanned": unscanned,
        "unopenable": unopenable,
    }


def unverified_because(report: dict) -> list:
    """Every reason this report cannot claim coverage, in words a reader can act on.

    Empty when the guard looked everywhere it claims to cover. Naming the gap is the whole
    point: a coverage gap nobody can locate is a coverage gap nobody will close.
    """
    why = []
    for u in report.get("unopenable") or []:
        why.append("could not open %s (%s)" % (u["file"], u.get("why", "unopenable")))
    for u in report.get("unscanned") or []:
        why.append("did not scan %s (suffix %r is neither in-scope nor known-binary)"
                   % (u["file"], u.get("suffix", "")))
    n = report.get("nestedArchivesRejected") or 0
    if n and not report.get("unopenable"):
        why.append("%d nested archive(s) rejected" % n)
    return why


def release_verdict(report: dict) -> str:
    """The only place the release verdict is computed. Three words, and the order matters.

    FAIL        a finding survived — we looked and found something.
    UNVERIFIED  we could not look everywhere (F29 an archive would not open; F30 a file's
                suffix is neither in-scope nor known-binary).
    PASS        we looked everywhere we claim to cover, and found nothing.

    FAIL outranks UNVERIFIED deliberately: "found something" is a worse state than "could not
    look", and a real finding must never be downgraded to a coverage caveat. Before Phase 9
    step 3.1 there were two words, so "could not look" and "looked and found nothing" both
    came out as PASS — a live violation of F29 and F30.
    """
    if report.get("findings"):
        return "FAIL"
    if unverified_because(report):
        return "UNVERIFIED"
    return "PASS"


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="d5_distribution_guard",
        description="D12 guard: no shipped artifact may carry a real event id, motor id tied to "
                    "the mark defect, or an event-level held-out mark tuple.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--report", default=None)
    args = ap.parse_args(argv)

    present = [p for p in args.paths if Path(p).exists()]
    if not present:
        print("D5 DISTRIBUTION GUARD: nothing scanned - every path was missing.")
        return 2

    report = scan_paths(present)
    verdict = release_verdict(report)

    lines = ["# D5 Distribution Guard Report", "",
             "**Defect:** D12 - no shipped artifact may carry a real event id, an associated real "
             "motor id, or an event-level held-out mark tuple.", "",
             "Scanned: %s" % ", ".join(present), "",
             "Artifacts inspected: %d" % report["artifactsInspected"], ""]

    if report["exceptionsGranted"]:
        lines += ["## Exceptions granted (%d)" % len(report["exceptionsGranted"]), "",
                  "| file | reason |", "|-|-|"]
        for e in report["exceptionsGranted"]:
            lines.append("| `%s` | %s |" % (e["file"], e["reason"]))
        lines.append("")

    if report["findings"]:
        lines += ["## FINDINGS (%d) - RELEASE FAILS" % len(report["findings"]), "",
                  "| kind | file |", "|-|-|"]
        for f in report["findings"]:
            lines.append("| `%s` | `%s` |" % (f["kind"], f["file"]))
            print("FAIL %s  kind=%s  %s" % (f["file"], f["kind"], f["match"]))
    else:
        lines += ["## FINDINGS: 0", "", "No real event id, motor id, or held-out mark tuple detected.", ""]

    # F29/F30. The coverage gaps get their own section, ABOVE the verdict, because "0 findings"
    # read on its own is exactly the sentence this whole step exists to stop being misread.
    gaps = unverified_because(report)
    if gaps:
        lines += ["## COVERAGE GAPS (%d) - RELEASE IS UNVERIFIED, NOT CLEAN" % len(gaps), "",
                  "`0 findings` above means only that nothing was found in what WAS looked at.", ""]
        for g in gaps:
            lines.append("- %s" % g)
            print("UNVERIFIED %s" % g)
        lines.append("")

    lines += ["", "## Verdict: `%s`" % verdict, ""]

    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print("wrote %s" % rp)

    print("D5 DISTRIBUTION GUARD: %d artifact(s) inspected, %d finding(s), %d coverage gap(s), "
          "verdict %s." % (report["artifactsInspected"], len(report["findings"]), len(gaps), verdict))

    # THE PRE-REGISTERED FALSIFIER for Phase 9 step 3.1 is "a caller treats UNVERIFIED as truthy",
    # and this line used to be it: `return 1 if verdict == "FAIL" else 0` exited 0 on UNVERIFIED.
    # A third verdict word that still exits 0 has changed a report and refused nothing. Exit 0 is
    # now reserved for PASS and nothing else.
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
