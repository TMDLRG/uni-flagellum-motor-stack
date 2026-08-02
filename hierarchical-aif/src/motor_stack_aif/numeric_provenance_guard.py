"""D11 — numeric provenance guard: a decimal in a report must say where it came from.

WHY THIS EXISTS
---------------
`claim_guard.py` clamps forbidden WORDING. It cannot check a number. Defect D11 proved the gap:
two figures reached a report with no traceable source, and the harder of the two was
`0.0790` — not an invention but the **recorded M3 percentile half-width `0.0789979` transplanted
from a different table in the same document**. Real, precise, locally plausible, and invisible to
a wording guard.

Note what that means for a naive checker: "does this number appear somewhere in some artifact?"
would have **passed** the transplanted value, because it does appear — under a different field.
Provenance is therefore about the POINTER, not about the digits.

THE CONTRACT THIS ENFORCES
--------------------------
Every decimal that looks like a scientific quantity must be one of:

  1. ANCHORED        — carries an explicit source pointer, and the pointed-at value matches.
  2. RECOMPUTED      — produced by a named script with saved inputs (declared via a `prov:` anchor
                       whose source is a script path rather than a JSON pointer).
  3. DESIGN_ONLY     — an introduced design threshold, evidential for nothing.
  4. NOT_COMPUTED    — explicitly absent.
  5. NOT_MEASURED    — explicitly unmeasurable here.

Anything else is `UNANCHORED`: reported, and not by itself a failure, because a report may
legitimately quote counts, dates, section numbers and derived arithmetic. Making unanchored
numbers fail globally would produce thousands of findings and would be ignored — a guard that is
ignored protects nothing.

**What DOES fail is `ANCHORED_MISMATCH`**: a number that declares a source and does not match it.
That is the actionable, low-noise, non-bypassable case, and it is exactly the D11 class.

ANCHOR SYNTAX (an HTML comment, so it is invisible in rendered markdown)

    <!-- prov: 0.0800 = power_atlas.json#d10Counterfactual.meanCIHalfWidthNats -->
    <!-- prov: 3.4326923382675303 = F_SIDE_MOTOR_STACK_SCORING_RESULT.json#motorEqualNLPD.F_MOTOR_STACK -->
    <!-- prov: 0.042 = DESIGN_ONLY -->
    <!-- prov: 61.42 = scripts/run_c01_corrected_full.py RECOMPUTED -->

Comparison is at the **declared display precision**: `0.0800` matches `0.07996917206325926`
because it rounds there; `0.0790` does not. That is the whole mechanism.

TRANSPLANT DIAGNOSIS
--------------------
On a mismatch the guard searches every loaded artifact for a field whose value *does* round to the
quoted number and names it. That converts "this number is wrong" into "this number is the value of
<other field>" — which is how the D11 defect was actually diagnosed by hand.

SCOPE, STATED HONESTLY
----------------------
This does not make numeric provenance decidable in general. It makes *declared* provenance
checkable, and it makes the known defect a mechanical regression. The general control remains an
adversarial reader briefed to trace every number.

D5: reads markdown and result artifacts only. No data channel is touched.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = REPO_ROOT / "hierarchical-aif" / "results" / "motor_stack_aif"
AUDITS_DIR = REPO_ROOT / "audits" / "phase-b"

try:                                    # package import
    from . import status as _status
except ImportError:                     # direct script invocation: `python .../numeric_provenance_guard.py`
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from motor_stack_aif import status as _status

# Document status markers. Where a marker is ALSO a CI verdict, it is imported from `status`
# rather than re-declared: `status.py` owns the verdict vocabulary, and an AST scan
# (`test_verdict_strings_are_defined_in_exactly_one_module`) enforces single ownership so that no
# other module can emit a verdict without having seen an interval. That check fired on an earlier
# draft of this file, correctly — a literal is a literal regardless of the author's intent.
MARKERS = ("DESIGN_ONLY", "NOT_COMPUTED", "NOT_MEASURED", "NOT-MEASURED",
           "NOT_APPLICABLE_DIFFERENT_UNITS", "NOT_SATISFIED",
           _status.NOT_RUN, _status.NOT_ESTABLISHED)

# A decimal that looks like a scientific quantity: >=3 decimal places, or scientific notation.
# Plain integers, dates, small counts and 1-2dp figures are out of scope by design.
NUMBER_RE = re.compile(r"(?<![\w.])(-?\d+\.\d{3,}(?:[eE][-+]?\d+)?|-?\d+(?:\.\d+)?[eE][-+]?\d+)(?![\w])")

ANCHOR_RE = re.compile(
    r"<!--\s*prov:\s*(?P<num>-?[\d.]+(?:[eE][-+]?\d+)?)\s*=\s*(?P<src>[^>]*?)\s*-->")


class Finding(dict):
    """number / file / line / claimedSource / status / pass."""


def load_artifacts() -> dict:
    """Load every result artifact the reports could legitimately cite."""
    out = {}
    for d in (RESULTS_DIR, AUDITS_DIR):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.json")):
            try:
                out[p.name] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
    return out


def resolve_pointer(artifacts: dict, source: str):
    """Resolve `file.json#dotted.path`. Returns (value, error)."""
    if "#" not in source:
        return None, "source is not a JSON pointer"
    fname, path = source.split("#", 1)
    fname = fname.strip()
    if fname not in artifacts:
        return None, "artifact %r not loaded" % fname
    node = artifacts[fname]
    for part in path.strip().split("."):
        if not part:
            continue
        if isinstance(node, dict):
            if part not in node:
                return None, "path element %r not found" % part
            node = node[part]
        elif isinstance(node, list):
            try:
                node = node[int(part)]
            except (ValueError, IndexError):
                return None, "list index %r invalid" % part
        else:
            return None, "cannot descend into %r at %r" % (type(node).__name__, part)
    if not isinstance(node, (int, float)):
        return None, "resolved value is %r, not numeric" % type(node).__name__
    return float(node), None


def _decimals(num_str: str) -> int:
    s = num_str.lower()
    if "e" in s:
        return -1                      # scientific notation: compare relatively
    return len(s.split(".")[1]) if "." in s else 0


def matches_at_display_precision(quoted: str, actual: float) -> bool:
    """`0.0800` matches 0.07996917206325926; `0.0790` does not. That is the mechanism."""
    d = _decimals(quoted)
    q = float(quoted)
    if d < 0:
        return abs(q - actual) <= max(abs(actual), abs(q)) * 1e-3
    return ("%.*f" % (d, actual)) == ("%.*f" % (d, q))


def find_transplant_source(artifacts: dict, quoted: str, exclude_path: str = "") -> list:
    """On a mismatch, name any field whose value DOES round to the quoted number.

    This is the D11 diagnosis made mechanical: it turns 'wrong' into 'this is <other field>'.
    """
    hits = []

    def walk(node, fname, path):
        if len(hits) >= 6:
            return
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, fname, path + "." + k if path else k)
        elif isinstance(node, list):
            for i, v in enumerate(node[:50]):
                walk(v, fname, "%s.%d" % (path, i))
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            full = "%s#%s" % (fname, path)
            if full == exclude_path:
                return
            if matches_at_display_precision(quoted, float(node)):
                hits.append({"path": full, "value": node})

    for fname, doc in artifacts.items():
        walk(doc, fname, "")
    return hits


def scan_file(path: Path, artifacts: dict) -> list:
    """Return a Finding per in-scope decimal in `path`."""
    findings = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # anchors declared anywhere in the file, keyed by the literal number string
    anchors = {}
    for m in ANCHOR_RE.finditer(text):
        anchors[m.group("num")] = m.group("src").strip()

    for i, line in enumerate(lines, start=1):
        if line.lstrip().startswith("<!--"):
            continue
        marked = any(mk in line for mk in MARKERS)
        for m in NUMBER_RE.finditer(line):
            raw = m.group(1)
            f = Finding(number=raw, file=str(path).replace("\\", "/"), line=i,
                        claimedSource=None, status=None, passed=True, detail="")
            src = anchors.get(raw)
            if src:
                f["claimedSource"] = src
                if src.upper() in ("DESIGN_ONLY", "NOT_COMPUTED", "NOT_MEASURED"):
                    f["status"] = src.upper()
                elif "RECOMPUTED" in src.upper():
                    f["status"] = "RECOMPUTED"
                    f["detail"] = "declared recomputation: %s" % src
                elif "#" in src:
                    actual, err = resolve_pointer(artifacts, src)
                    if err:
                        f["status"] = "ANCHORED_UNRESOLVABLE"
                        f["passed"] = False
                        f["detail"] = err
                    elif matches_at_display_precision(raw, actual):
                        f["status"] = "ANCHORED_OK"
                        f["detail"] = "matches %r at display precision" % actual
                    else:
                        f["status"] = "ANCHORED_MISMATCH"
                        f["passed"] = False
                        tp = find_transplant_source(artifacts, raw, exclude_path=src)
                        f["detail"] = ("declared source holds %r, which does not round to %s"
                                       % (actual, raw))
                        if tp:
                            f["detail"] += (" | TRANSPLANT SUSPECT: this value matches %s"
                                            % ", ".join("%s=%r" % (h["path"], h["value"])
                                                        for h in tp[:3]))
                else:
                    f["status"] = "ANCHORED_FREEFORM"
                    f["detail"] = "source is not a resolvable pointer: %s" % src
            elif marked:
                f["status"] = "MARKED"
                f["detail"] = "line carries an explicit status marker"
            else:
                f["status"] = "UNANCHORED"
                f["detail"] = "no source pointer declared"
            findings.append(f)
    return findings


def scan_paths(paths) -> list:
    artifacts = load_artifacts()
    out = []
    for root in paths:
        root = Path(root)
        files = [root] if root.is_file() else sorted(root.rglob("*.md"))
        for p in files:
            out.extend(scan_file(p, artifacts))
    return out


def summarise(findings: list) -> dict:
    tally = {}
    for f in findings:
        tally[f["status"]] = tally.get(f["status"], 0) + 1
    return {"total": len(findings), "byStatus": tally,
            "failures": [f for f in findings if not f["passed"]]}


def main(argv=None) -> int:
    """CLI. Exit 0 = no anchored mismatches, 1 = at least one, 2 = nothing scanned."""
    import argparse
    ap = argparse.ArgumentParser(
        prog="numeric_provenance_guard",
        description="D11 guard: a declared numeric source must match the artifact it points at.")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--report", default=None)
    ap.add_argument("--show-unanchored", action="store_true",
                    help="list UNANCHORED numbers too (informational, never a failure)")
    args = ap.parse_args(argv)

    present = [p for p in args.paths if Path(p).exists()]
    if not present:
        print("NUMERIC PROVENANCE GUARD: nothing scanned - every path was missing.")
        return 2

    findings = scan_paths(present)
    s = summarise(findings)

    lines = ["# Numeric Provenance Guard Report", "",
             "**Defect:** D11 - a wording guard cannot check a number. This checks *declared* "
             "provenance.", "",
             "Scanned: %s" % ", ".join(present), "",
             "| status | meaning | count |", "|-|-|-|"]
    meaning = {
        "ANCHORED_OK": "declares a source pointer and matches it at display precision",
        "ANCHORED_MISMATCH": "**declares a source and does NOT match it - FAILS**",
        "ANCHORED_UNRESOLVABLE": "**declares a pointer that cannot be resolved - FAILS**",
        "ANCHORED_FREEFORM": "declares a non-pointer source (not machine-checkable)",
        "RECOMPUTED": "declared as recomputed by a named script",
        "DESIGN_ONLY": "introduced design threshold, evidential for nothing",
        "NOT_COMPUTED": "explicitly absent", "NOT_MEASURED": "explicitly unmeasurable here",
        "MARKED": "line carries an explicit status marker",
        "UNANCHORED": "no source declared (reported, not a failure - see scope note)",
    }
    for k, v in sorted(s["byStatus"].items(), key=lambda kv: -kv[1]):
        lines.append("| `%s` | %s | %d |" % (k, meaning.get(k, ""), v))
    lines += ["", "**Total in-scope decimals: %d**" % s["total"], ""]

    if s["failures"]:
        lines += ["## FAILURES (%d)" % len(s["failures"]), "",
                  "| number | file | line | claimed source | status | detail |", "|-|-|-|-|-|-|"]
        for f in s["failures"]:
            lines.append("| `%s` | `%s` | %d | `%s` | `%s` | %s |"
                         % (f["number"], f["file"], f["line"], f["claimedSource"],
                            f["status"], f["detail"].replace("|", "\\|")))
            print("FAIL %s:%d  %s  %s" % (f["file"], f["line"], f["number"], f["detail"]))
    else:
        lines += ["## FAILURES: 0", "",
                  "No number declares a source it does not match.", ""]

    if args.show_unanchored:
        un = [f for f in findings if f["status"] == "UNANCHORED"]
        lines += ["", "## UNANCHORED (informational, %d)" % len(un), "",
                  "| number | file | line |", "|-|-|-|"]
        for f in un[:400]:
            lines.append("| `%s` | `%s` | %d |" % (f["number"], f["file"], f["line"]))

    lines += ["", "## Scope, stated honestly", "",
              "This guard makes **declared** provenance checkable; it does not make numeric "
              "provenance decidable in general. `UNANCHORED` is reported and does **not** fail, "
              "because reports legitimately carry counts, dates and derived arithmetic, and a "
              "guard that fires on everything is a guard nobody reads. The failing class is "
              "`ANCHORED_MISMATCH` - a number that names a source and contradicts it, which is "
              "exactly the D11 defect. The general control remains an adversarial reader briefed "
              "to trace every number.", ""]

    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print("wrote %s" % rp)

    print("NUMERIC PROVENANCE GUARD: %d in-scope decimals, %d failure(s)."
          % (s["total"], len(s["failures"])))
    return 1 if s["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
