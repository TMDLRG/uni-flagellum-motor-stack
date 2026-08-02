"""S9 SWEEP — every hash pin in this repository, checked against its own commit.

    python hierarchical-aif/scripts/s9_sweep.py            report
    python hierarchical-aif/scripts/s9_sweep.py --json     machine-readable

READ-ONLY. It computes and compares. It repairs nothing, because every repair here is either
S9 (a receipt that cannot be reproduced from its own commit) or S3 (a write to a frozen
artifact), and both are the operator's.

WHY THIS EXISTS
---------------
S9 is a stop condition: *"a receipt cannot be reproduced from its own commit."* It was found and
ruled in `UNI.Minecraft` on 2026-07-27 — a Phase 7 receipt had been pinned against the CRLF form
its file happened to carry in a Windows working tree, while git stored the LF form. The pin was of
bytes git had never held, so the receipt verified on exactly one machine.

THE SAME SWEEP WAS NEVER RUN HERE. This repository declares `* text=auto eol=lf` in
`.gitattributes`, so every checkout on every platform produces LF — and any pin taken from a CRLF
working copy is therefore permanently unreachable from the commit. That is not a hypothetical: an
adversarial audit found three of them among the *scientific result* artifacts.

THE THREE STATES, AND WHY THEY ARE DIFFERENT
--------------------------------------------
    REPRODUCIBLE  the committed blob hashes to the pin. Anyone, anywhere, can check it.
    S9            the WORKING COPY matches the pin and the COMMITTED BLOB does not. The evidence
                  is real and the pin is of a form git has never stored: verifiable on one machine
                  and nowhere else. This is the stop condition, exactly.
    DRIFTED       NEITHER matches. The artifact changed after the pin was written and nobody
                  re-issued it. Worse than S9, because there is no machine on which it holds.
    MISSING       the pinned path is not there at all.

Collapsing S9 and DRIFTED would be the mistake. S9 is a RECORDING fault — the right bytes, hashed
in the wrong form — and the repair is to re-record. DRIFTED is an EVIDENCE fault: something moved
and the record did not follow. They need different decisions from different people.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# A sidecar line is `<sha256> [*]<path>` — the sha256sum manifest format, binary or text mode.
SIDECAR_LINE = re.compile(r"^([0-9a-f]{64})\s+\*?(.+?)\s*$")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "_build", "deps", ".venv"}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blobs_at_head(rels: list[str]) -> dict[str, bytes | None]:
    """Every blob in ONE process, via `git cat-file --batch`.

    THE FIRST VERSION SPAWNED `git show` ONCE PER PIN. Measured: 46 ms per spawn on Windows,
    times 1513 pins, is SEVENTY SECONDS OF PURE PROCESS LAUNCH before a single character reached
    the screen. The operator ran it and reported it hung. It was not hung; it was SILENT, which
    from the outside is the same thing — and it is the second time in one day I shipped a tool
    that is indistinguishable from a hang.

    `git cat-file --batch` takes refs on stdin and streams a header line then the raw bytes for
    each. One process for the whole repository, and the seventy seconds become a fraction of one.
    """
    proc = subprocess.Popen(
        ["git", "-C", str(REPO), "cat-file", "--batch"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    payload = "".join("HEAD:" + r + "\n" for r in rels).encode("utf-8")
    out, _ = proc.communicate(payload)

    result: dict[str, bytes | None] = {}
    pos = 0
    for rel in rels:
        nl = out.find(b"\n", pos)
        if nl < 0:
            result[rel] = None
            continue
        header = out[pos:nl].decode("utf-8", "replace")
        pos = nl + 1
        parts = header.rsplit(" ", 2)
        # "<path> missing" for anything not in the tree at HEAD.
        if len(parts) != 3 or not parts[2].isdigit():
            result[rel] = None
            continue
        size = int(parts[2])
        result[rel] = out[pos:pos + size]
        pos += size + 1  # the trailing newline cat-file adds after the payload
    return result


def sidecars():
    """Every `.sha256` manifest in the tree, and the pins inside it."""
    for p in REPO.rglob("*.sha256"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        base = p.parent
        for raw in text.splitlines():
            m = SIDECAR_LINE.match(raw.strip())
            if not m:
                continue
            digest, rel = m.group(1).lower(), m.group(2).replace("\\", "/")
            # A manifest names paths relative to itself, or to the repo root. Try both, and say
            # which one resolved rather than guessing silently.
            for cand in (base / rel, REPO / rel):
                if cand.exists():
                    yield {
                        "pin": digest,
                        "path": cand.resolve().relative_to(REPO).as_posix(),
                        "declared_in": p.resolve().relative_to(REPO).as_posix(),
                    }
                    break
            else:
                yield {"pin": digest, "path": rel, "declared_in": p.resolve().relative_to(REPO).as_posix()}


def classify(entry, blob, disk=None):
    """`disk` is injectable ONLY so a test can construct the S9 shape deterministically.

    Without it, the S9 mutation could not be built at all on this tree: every candidate fixture
    has identical disk and blob bytes, so the constructed pin matched neither and the test either
    skipped or passed on DRIFTED — a test named "the S9 shape specifically is caught" that never
    saw an S9. A mutation that cannot be constructed is a mutation nobody has run.
    """
    abs_path = REPO / entry["path"]
    if disk is None:
        disk = abs_path.read_bytes() if abs_path.is_file() else None

    disk_sha = sha256(disk) if disk is not None else None
    blob_sha = sha256(blob) if blob is not None else None

    if disk is None and blob is None:
        state = "MISSING"
    elif blob_sha == entry["pin"]:
        state = "REPRODUCIBLE"
    elif disk_sha == entry["pin"]:
        state = "S9"
    else:
        state = "DRIFTED"

    # For S9 specifically: is it the line-ending class? Naming the CAUSE is what lets a reader
    # decide whether it is a recording fault or something worse.
    cause = None
    if state == "S9" and disk is not None and blob is not None:
        if disk.replace(b"\r\n", b"\n") == blob.replace(b"\r\n", b"\n"):
            cause = f"line endings only ({disk.count(bytes([13]))} CR on disk, {blob.count(bytes([13]))} in the blob) - IDENTICAL TEXT"
        else:
            cause = "content differs, not only line endings — the working copy is genuinely ahead of or behind the commit"

    return {**entry, "state": state, "disk": disk_sha, "blob": blob_sha, "cause": cause}


def main() -> int:
    # SPEAK WHILE WORKING. Every line below appears as it happens, because a tool that shows
    # nothing for a minute has already been reported as hung once.
    print()
    print("  S9 SWEEP - reading manifests...", flush=True)
    entries = list(sidecars())
    print(f"  {len(entries)} pins across {len({e['declared_in'] for e in entries})} manifest(s)", flush=True)

    print("  fetching every committed blob in ONE git process...", end="", flush=True)
    t0 = time.time()
    blobs = blobs_at_head([e["path"] for e in entries])
    print(f" {time.time() - t0:.1f}s", flush=True)

    print("  hashing and comparing...", end="", flush=True)
    t1 = time.time()
    rows = [classify(e, blobs.get(e["path"])) for e in entries]
    print(f" {time.time() - t1:.1f}s", flush=True)
    by = {}
    for r in rows:
        by.setdefault(r["state"], []).append(r)

    if "--json" in sys.argv:
        print(json.dumps({"total": len(rows), "counts": {k: len(v) for k, v in by.items()}, "pins": rows}, indent=1))
        return 0

    print()
    print("  " + "-" * 92)
    for state in ("REPRODUCIBLE", "S9", "DRIFTED", "MISSING"):
        n = len(by.get(state, []))
        print(f"    {str(n).rjust(5)}  {state}")
    print()

    for state, blurb in (
        ("S9", "PINNED AGAINST A FORM GIT HAS NEVER STORED. The working copy matches; the commit\n"
               "        does not. Verifiable on this machine and NOWHERE ELSE. This is the stop condition."),
        ("DRIFTED", "NEITHER the working copy NOR the commit matches the pin. Something moved and the\n"
                    "        record did not follow — there is no machine on which this holds."),
        ("MISSING", "the pinned path is not present at all."),
    ):
        items = by.get(state, [])
        if not items:
            continue
        print(f"  {state} ({len(items)})")
        print(f"        {blurb}")
        print()
        for r in items:
            print(f"    {r['path']}")
            print(f"        pinned {r['pin'][:16]}  disk {(r['disk'] or 'absent')[:16]}  blob {(r['blob'] or 'absent')[:16]}")
            print(f"        declared in {r['declared_in']}")
            if r["cause"]:
                print(f"        cause: {r['cause']}")
            print()

    s9 = len(by.get("S9", []))
    drift = len(by.get("DRIFTED", []))
    print("  " + "-" * 92)
    if s9 or drift:
        print(f"  {s9} S9 / {drift} DRIFTED. NOTHING HERE IS REPAIRED BY THIS SCRIPT.")
        print("  An S9 repair re-records the pin against the reproducible form; a DRIFTED pin needs")
        print("  someone to decide whether the artifact or the record is wrong. Both are the")
        print("  operator's: S9 is a stop condition and these are frozen artifacts (S3).")
    else:
        print("  Every pin reproduces from its own commit.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
