"""Claim guard — mechanical clamp on forbidden claim language.

Scans hierarchical-aif documents for claims the current evidence does not license. A phrase is a
VIOLATION unless it appears in a NEGATED or QUOTED-AS-FORBIDDEN context (these documents must be
able to say "we do NOT claim biological parity" and to list forbidden wording verbatim).

This guard is mechanical and therefore dumb. It cannot judge whether a claim is warranted; it only
catches known-bad phrasing. Passing the guard is necessary, not sufficient.
"""
from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN = [
    "biological parity achieved",
    "full parity achieved",
    "achieved full parity",
    "parity achieved",
    "active inference demonstrated",
    "demonstrated active inference",
    "flagellum solved",
    "motor solved",
    "full flagellum motor working exactly",
    "general intelligence",
    "awareness achieved",
    "consciousness achieved",
    "human stack validated",
    "g proves motor agency",
    "proves motor agency",
    "m2 is the uni model",
    "mark process prospectively validated",
    "prospectively validated on wadhwa",
    "c11 diagnostic proves",
    "diagnostic proves u4",
    "digital life",
    "we have full biological parity",
]

# A hit inside one of these contexts is allowed: the document is denying or cataloguing the phrase.
NEGATION_CUES = [
    "no ", "not ", "never", "cannot", "can not", "forbidden", "must not", "may not",
    "unless", "would be", "does not", "do not", "don't", "isn't", "is not", "without",
    "prohibited", "disallow", "refus", "withdraw", "avoid", "rather than", "instead of",
    "no longer", "denied", "reject", "disclaim", "hazard", "would produce", "category error",
    "overclaim", "illegitimate", "invalid", "wrong", "error", "misread", "must be labelled",
]

# Use/mention: a forbidden phrase wrapped in quotation marks is being NAMED, not asserted.
# These documents must be able to catalogue the wording they prohibit. This is the standard
# use/mention distinction. It is deliberately permissive - a determined author could evade the
# guard by quoting a claim, which is why the guard is documented as necessary, not sufficient.
QUOTE_CHARS = '"“”‘’\''

ALLOWED_REPLACEMENTS = [
    "target hypothesis", "candidate model", "corrected full run", "not established",
    "retrospective/exploratory", "transfer required", "intervention required",
    "mechanism discriminator pending", "CI-bound verdict", "old claim withdrawn",
    "defect preserved",
]

WINDOW = 180  # chars of left-context inspected for a negation cue


def scan_text(text: str, source: str = "<text>") -> list[dict]:
    violations = []
    low = text.lower()
    for phrase in FORBIDDEN:
        for m in re.finditer(re.escape(phrase), low):
            line_no = text.count("\n", 0, m.start()) + 1
            line_start = low.rfind("\n", 0, m.start()) + 1
            line_end = low.find("\n", m.end())
            line = low[line_start:line_end if line_end != -1 else len(low)]
            # Negation must be on the SAME LINE as the phrase. A cross-line window let an
            # unrelated "forbidden" on a preceding line mask a real claim on the next one -
            # caught by test_quoting_does_not_defeat_a_bare_claim_on_another_line.
            left = low[line_start:m.start()][-WINDOW:]
            negated = any(cue in left for cue in NEGATION_CUES)
            # a line that is itself a forbidden-wording catalogue entry
            catalogued = "forbidden" in line or "allowed_wording" in line
            # use/mention: phrase immediately wrapped in quotation marks
            before = text[m.start() - 1] if m.start() > 0 else ""
            after = text[m.end()] if m.end() < len(text) else ""
            quoted = before in QUOTE_CHARS and after in QUOTE_CHARS
            if negated or catalogued or quoted:
                continue
            violations.append({
                "source": source,
                "line": line_no,
                "phrase": phrase,
                "context": text[max(0, m.start() - 90):m.end() + 90].replace("\n", " "),
            })
    return violations


def scan_paths(paths, patterns=("*.md", "*.json", "*.jsonl")) -> list[dict]:
    out = []
    for root in paths:
        root = Path(root)
        if root.is_file():
            files = [root]
        else:
            files = [p for pat in patterns for p in root.rglob(pat)]
        for p in files:
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            out.extend(scan_text(text, source=str(p)))
    return out


def main(argv=None) -> int:
    """CLI entry point. Exit 0 = clean, 1 = violations found, 2 = nothing scanned.

    The package directory is hyphenated (`hierarchical-aif/`), so it is NOT importable as
    `hierarchical-aif.src...`. Invoke by file path instead:

        python hierarchical-aif/src/motor_stack_aif/claim_guard.py \\
            hierarchical-aif/reports hierarchical-aif/docs \\
            hierarchical-aif/ledgers hierarchical-aif/protocols

    Exiting non-zero on a violation is what lets this be wired into a gate. Passing is
    NECESSARY, NOT SUFFICIENT: this guard checks WORDING only. It cannot judge whether a claim
    is supported by evidence, and a determined author can evade it by quoting. It is a clamp on
    known-bad phrasing, not a substitute for the truth contract.
    """
    import argparse

    ap = argparse.ArgumentParser(
        prog="claim_guard",
        description="Mechanical clamp on forbidden claim wording in hierarchical-aif documents.")
    ap.add_argument("paths", nargs="+", help="files or directories to scan")
    ap.add_argument("--report", default=None,
                    help="also write a markdown report to this path")
    args = ap.parse_args(argv)

    missing = [p for p in args.paths if not Path(p).exists()]
    for p in missing:
        print("MISSING PATH: %s" % p)
    scanned = [p for p in args.paths if Path(p).exists()]
    if not scanned:
        print("CLAIM GUARD: nothing scanned — every path was missing.")
        return 2

    violations = scan_paths(scanned)

    lines = ["# Claim Guard Report", ""]
    lines.append("Scanned: %s" % ", ".join(scanned))
    if missing:
        lines.append("")
        lines.append("**Missing paths (not scanned):** %s" % ", ".join(missing))
    lines.append("")
    if violations:
        lines.append("## VIOLATIONS: %d" % len(violations))
        lines.append("")
        lines.append("| source | line | phrase | context |")
        lines.append("|-|-|-|-|")
        for v in violations:
            ctx = v["context"].replace("|", "\\|")[:160]
            lines.append("| `%s` | %d | `%s` | %s |"
                         % (v["source"], v["line"], v["phrase"], ctx))
            print("VIOLATION %s:%d  %r" % (v["source"], v["line"], v["phrase"]))
    else:
        lines.append("## VIOLATIONS: 0 — CLEAN")
        lines.append("")
        lines.append("No forbidden claim wording found in the scanned paths.")
    lines.append("")
    lines.append("**Passing this guard is necessary, not sufficient.** It checks wording only; "
                 "it never checks whether evidence supports a claim.")
    lines.append("")

    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text("\n".join(lines), encoding="utf-8", newline="\n")
        print("wrote %s" % rp)

    print("CLAIM GUARD: %d violation(s) across %d path(s)." % (len(violations), len(scanned)))
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
