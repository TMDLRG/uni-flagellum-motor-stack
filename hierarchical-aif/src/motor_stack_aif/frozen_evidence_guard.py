"""F28 — frozen evidence hashes drift, and everything halts.

    F28 | frozen evidence hashes drift | STOP_FROZEN_EVIDENCE_DRIFT, halt everything
        | falsifier: work continues past a drift

WHY THIS EXISTS (Phase 9 step 3.2)
----------------------------------
`hierarchical-aif/reports/frozen-evidence-baseline.sha256` has pinned 250 files under
`audits/phase-c/**` and `audits/phase-d/**` since 2026-07-21, and until now NOTHING IN THIS
REPOSITORY EVER COMPARED THEM. `CLAUDE.md` states that any diff against that baseline is "a
contract violation and a hard stop" — a sentence with no mechanism behind it. A human who
remembers to run `sha256sum -c` is a habit, not a refusal, and habits are exactly what a frozen
evidence baseline exists to stop relying on.

BOTH DIRECTIONS, BECAUSE ONLY ONE OF THEM IS FREE
--------------------------------------------------
`sha256sum -c` catches a CHANGED file and a MISSING one. It cannot catch an ADDED one: a file
dropped into the frozen tree is invisible to a manifest that never names it, and "the manifest
verifies" reads exactly the same either way. Frozen means frozen in both directions, so `verify`
also walks the frozen roots and refuses anything living there that the baseline does not name.

The frozen roots are DERIVED FROM THE BASELINE ITSELF, never configured separately. A guard whose
scope lives in a second file can be narrowed by editing the second file, and the narrowing looks
like configuration rather than like removing a guard.

WHAT "HALT EVERYTHING" MEANS HERE, STATED PLAINLY
-------------------------------------------------
`halt_if_drifted` raises; it never returns a value a caller can mistake for success. It is wired
into `hierarchical-aif/tests/conftest.py` at `pytest_sessionstart`, so a drifted tree stops the
whole test session before a single test runs — the suite is the thing that must not continue.
That is the strongest honest reading of "halt everything" within this repository's reach, and it
is claimed as no more than that: it does not stop a process that never imports this module.

D5: reads file BYTES to hash them. It parses no field, interprets no value, and reads nothing
held out.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

STOP = "STOP_FROZEN_EVIDENCE_DRIFT"


class FrozenEvidenceDrift(RuntimeError):
    """Raised instead of returning. A drift that can be assigned to a variable can be ignored."""


def _repo_root() -> Path:
    # src/motor_stack_aif/ -> src/ -> hierarchical-aif/ -> repo root
    return Path(__file__).resolve().parents[3]


def default_paths():
    """The real baseline and the real root. Hardcoded so a caller cannot aim the guard elsewhere."""
    root = _repo_root()
    return root / "hierarchical-aif" / "reports" / "frozen-evidence-baseline.sha256", root


def parse_baseline(baseline_path) -> list:
    """`sha256sum` manifest format: `<sha256> *<path>` (binary mode) or `<sha256>  <path>`."""
    entries = []
    for raw in Path(baseline_path).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        sha, _, rest = line.partition(" ")
        rel = rest.lstrip(" *").replace("\\", "/")
        if sha and rel:
            entries.append((sha.lower(), rel))
    return entries


def frozen_roots(baseline_path) -> list:
    """The directories this baseline claims to freeze, read out of the baseline itself.

    Two path components deep (`audits/phase-c`), which is how this baseline is written. Derived
    rather than configured: see the module docstring.
    """
    roots = set()
    for _sha, rel in parse_baseline(baseline_path):
        parts = Path(rel).parts
        if len(parts) >= 2:
            roots.add("/".join(parts[:2]))
    return sorted(roots)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(baseline_path, root) -> dict:
    """Compare the frozen tree under `root` with `baseline_path`. A read; it changes nothing.

    Returns `changed` / `missing` / `unlisted`, all as NAMES rather than counts — a drift nobody
    can locate is a drift nobody can rule on.
    """
    root = Path(root)
    entries = parse_baseline(baseline_path)
    listed = {rel for _sha, rel in entries}

    changed, missing = [], []
    for sha, rel in entries:
        p = root / rel
        if not p.is_file():
            missing.append(rel)
            continue
        actual = _sha256(p)
        if actual != sha:
            changed.append({"file": rel, "baseline": sha, "actual": actual})

    unlisted = []
    for r in frozen_roots(baseline_path):
        base = root / r
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*")):
            if p.is_file() and p.relative_to(root).as_posix() not in listed:
                unlisted.append(p.relative_to(root).as_posix())

    return {
        "ok": not (changed or missing or unlisted),
        "checked": len(entries),
        "changed": changed,
        "missing": missing,
        "unlisted": unlisted,
    }


def account(report: dict) -> str:
    """The drift, in words, with every affected path named."""
    if report.get("ok"):
        return "frozen evidence intact: %d file(s) verified" % report["checked"]

    # Every lookup here is defensive, and that is not fussiness: this function runs at the worst
    # possible moment, and a reporter that raises while explaining a drift has converted a
    # legible stop into a stack trace. Plain ASCII for the same reason it is defensive — this
    # prints to a console, and a reader deciphering mojibake in a halt message is being shown
    # nothing. (Both learned here: the first version raised KeyError on a partial report.)
    lines = ["%s - %d file(s) checked" % (STOP, report.get("checked", 0))]
    for c in report.get("changed") or []:
        lines.append("  CHANGED  %s\n             baseline %s\n             actual   %s"
                     % (c.get("file", "?"), c.get("baseline", "?"), c.get("actual", "?")))
    for m in report.get("missing") or []:
        lines.append("  MISSING  %s" % m)
    for u in report.get("unlisted") or []:
        lines.append("  UNLISTED %s  (added to a frozen tree; a manifest check alone cannot see this)"
                     % u)
    lines += [
        "",
        "Frozen evidence is historical: it is not edited, corrected or regenerated. If a change",
        "here is deliberate, that is a decision about the evidence record and belongs to the",
        "operator, not to whatever process just tripped this.",
    ]
    return "\n".join(lines)


def halt_if_drifted(baseline_path=None, root=None) -> dict:
    """Verify, and RAISE on any drift. Returns the report only when the tree is intact."""
    if baseline_path is None or root is None:
        baseline_path, root = default_paths()
    report = verify(baseline_path, root)
    if not report["ok"]:
        raise FrozenEvidenceDrift(account(report))
    return report


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        prog="frozen_evidence_guard",
        description="F28: refuse to continue when frozen evidence has drifted.")
    default_baseline, default_root = default_paths()
    ap.add_argument("--baseline", default=str(default_baseline))
    ap.add_argument("--root", default=str(default_root))
    args = ap.parse_args(argv)

    report = verify(args.baseline, args.root)
    print(account(report))
    print("")
    print("EXPECTED OUTPUT: `frozen evidence intact: 250 file(s) verified`, and exit 0.")
    print("")
    print("RECOMPUTE THE NUMBER YOURSELF, with an instrument that shares nothing with this one:")
    print("    sha256sum -c %s | grep -c ': OK$'" % args.baseline)
    print("  It must print 250. If the two disagree, TRUST sha256sum and not this program.")
    print("  (sha256sum cannot see an ADDED file, which is why this program also walks the tree;")
    print("   so this side may legitimately refuse where sha256sum is content, never the reverse.)")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
