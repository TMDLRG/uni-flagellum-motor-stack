"""PROOF 4 (A2) for Phase 9 step 3.1 — a command that fails on demand, so you watch the guard bite.

    python hierarchical-aif/scripts/prove_unverified_bites.py

It builds three throwaway distributions in a temp directory, runs the real guard's real CLI on
each, and prints what it EXPECTED beside what it OBSERVED. It exits 0 only if all three agree,
so you do not have to read the output to know the answer — but the output is there so you can.

WHAT YOU ARE WATCHING
---------------------
Before Phase 9 step 3.1 the middle case printed PASS and exited 0. An archive nobody could open
was reported with the same word as an archive that was opened and found clean. That was a live
violation of two declared refusals:

    F29 | an archive cannot be opened           | report UNVERIFIED | it is treated as clean
    F30 | files in a distribution are unscanned | fail closed       | PASS with unscanned files

Nothing here is a fixture of the guard's own making: the broken archive really is a file that is
not a zip, and the guard really does try to open it and really does fail.

D5: synthetic identifiers only, of the same shape as the real leak. No held-out data is read.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import d5_distribution_guard as guard  # noqa: E402

SYNTHETIC_EVENT_ID = "99-99-99-9999:0001"

CASES = [
    ("we looked everywhere and found nothing",
     lambda d: (d / "notes.md").write_text("Nothing sensitive here.", encoding="utf-8"),
     "PASS", 0),
    ("WE COULD NOT LOOK - an archive that will not open",
     lambda d: (d / "delivery.zip").write_bytes(b"PK\x03\x04 truncated, unreadable"),
     "UNVERIFIED", 1),
    ("we looked and found something",
     lambda d: (d / "leak.md").write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID,
                                          encoding="utf-8"),
     "FAIL", 1),
]


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="prove-unverified-"))
    rows, ok = [], True
    try:
        for i, (label, build, want_verdict, want_rc) in enumerate(CASES):
            d = tmp / ("case%d" % i)
            d.mkdir()
            (d / "always-present.md").write_text("Nothing sensitive here.", encoding="utf-8")
            build(d)

            verdict = guard.release_verdict(guard.scan_paths([d]))
            rc = guard.main([str(d)])
            good = (verdict, rc) == (want_verdict, want_rc)
            ok = ok and good
            rows.append((good, label, want_verdict, want_rc, verdict, rc))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # Plain ASCII on purpose: this prints to a Windows console, where an em-dash arrives as a
    # replacement character and the operator is left reading mojibake in his own proof.
    print("\n" + "=" * 78)
    print("PROVING F29/F30 - the guard needs THREE words, and the exit code needs three too")
    print("=" * 78)
    for good, label, wv, wrc, gv, grc in rows:
        print("  %-4s %-48s" % ("ok" if good else "FAIL", label))
        print("       expected %-11s rc %d" % (wv, wrc))
        print("       observed %-11s rc %d" % (gv, grc))
    print("-" * 78)
    print("EXPECTED OUTPUT: three 'ok' lines, and this command exits 0.")
    print("A middle case reading PASS / rc 0 is F29 and F30 violated - that is what it did before.")
    print("RESULT: %s\n" % ("all three bite as declared" if ok else "THE GUARD DID NOT BITE"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
