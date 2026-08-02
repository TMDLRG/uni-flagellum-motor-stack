"""S9 AS A GATE — every hash pin in this repository must reproduce from its own commit.

Operator-authorised 2026-07-27: "wire the sweep in as a gate."

WHY THIS IS A TEST AND NOT A HABIT
-----------------------------------
The sweep found four faults the day it was first run — three S9 and one drifted — and every one
of them had been sitting in the tree for weeks with nothing looking. The same shape as F28 before
step 3.2: a rule stated in prose, a manifest on disk, and no mechanism between them. A human who
remembers to run `s9_sweep.py` is a habit, and a habit is exactly what a hash pin exists to stop
relying on.

WHAT IT REFUSES, AND WHY THE TWO ARE SEPARATE
----------------------------------------------
    S9       the working copy matches the pin and THE COMMIT DOES NOT. Verifiable on one machine
             and nowhere else. A stop condition by name: "a receipt cannot be reproduced from its
             own commit."
    DRIFTED  NEITHER matches. The artifact moved and the record did not follow. There is no
             machine on which it holds.

They fail separately because they need different decisions from different people. An S9 repair
re-records the pin against the reproducible form and changes no evidence; a DRIFTED pin means
someone must decide whether the artifact or the record is wrong. Collapsing them into one red
would hide the second inside the first.

SCOPE, STATED RATHER THAN IMPLIED
----------------------------------
F28's guard is hardcoded to `frozen-evidence-baseline.sha256` and covers 250 pins. This covers all
1513, which is every `.sha256` manifest entry in the repository — including the 1263 that had no
guard of any kind until the sweep existed.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SWEEP = REPO / "hierarchical-aif" / "scripts" / "s9_sweep.py"


def _load():
    """Import the sweep from scripts/, which is not a package."""
    spec = importlib.util.spec_from_file_location("s9_sweep", SWEEP)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["s9_sweep"] = mod
    spec.loader.exec_module(mod)
    return mod


s9 = _load()


@pytest.fixture(scope="module")
def swept():
    """One sweep for the whole module. ~5s: 1513 pins, one `git cat-file --batch`."""
    entries = list(s9.sidecars())
    blobs = s9.blobs_at_head([e["path"] for e in entries])
    rows = [s9.classify(e, blobs.get(e["path"])) for e in entries]
    by: dict[str, list] = {}
    for r in rows:
        by.setdefault(r["state"], []).append(r)
    return {"rows": rows, "by": by}


def _names(items):
    return "\n  ".join(f"{r['path']}  (pinned {r['pin'][:16]}, declared in {r['declared_in']})" for r in items)


# ---- the check cannot pass by not running ------------------------------------------------------


def test_the_sweep_finds_pins_at_all(swept):
    """A gate over an empty set is a gate that passes because it looked at nothing."""
    assert len(swept["rows"]) > 1000, (
        "only %d pins found — the manifests moved, or the scan is broken, and either way this "
        "gate is not checking what it claims" % len(swept["rows"]))


# ---- the two refusals, separately ---------------------------------------------------------------


def test_NO_PIN_IS_S9(swept):
    """S9: a receipt that cannot be reproduced from its own commit."""
    bad = swept["by"].get("S9", [])
    assert bad == [], (
        "%d pin(s) match the WORKING COPY and not the COMMIT. They verify on this machine and "
        "nowhere else — S9, word for word:\n  %s\n\n"
        "An S9 repair re-records the pin against the reproducible form. It changes no evidence, "
        "but it is a stop condition and the decision is the operator's." % (len(bad), _names(bad)))


def test_NO_PIN_HAS_DRIFTED(swept):
    """Worse than S9: neither the working copy nor the commit matches."""
    bad = swept["by"].get("DRIFTED", [])
    assert bad == [], (
        "%d pin(s) match NEITHER the working copy NOR the commit. There is no machine on which "
        "these hold:\n  %s\n\n"
        "This is not a recording fault. Something moved and the record did not follow, and "
        "someone has to decide which of the two is wrong." % (len(bad), _names(bad)))


def test_NO_PINNED_PATH_IS_MISSING(swept):
    bad = swept["by"].get("MISSING", [])
    assert bad == [], "%d pinned path(s) are not present at all:\n  %s" % (len(bad), _names(bad))


# ---- MUTATION: the classifier must bite, or every green above is vacuous -------------------------


def test_MUTATION_a_pin_that_names_the_wrong_hash_is_caught():
    """A guard nobody has shown can fail is decoration."""
    real = "hierarchical-aif/reports/frozen-evidence-baseline.sha256"
    forged = s9.classify(
        {"pin": "0" * 64, "path": real, "declared_in": "synthetic"},
        s9.blobs_at_head([real])[real],
    )
    assert forged["state"] == "DRIFTED", (
        "a pin naming a hash nothing has ever had was classified %s — the classifier does not "
        "bite, and every passing check above means nothing" % forged["state"])


def test_MUTATION_the_S9_shape_specifically_is_caught(tmp_path):
    """The exact shape: working copy matches, commit does not.

    Constructed rather than found, because by design there is now no real instance left to point
    at — the four were repaired. A mutation that can only run while the bug exists disappears the
    moment the bug is fixed, which is precisely when it starts being needed.
    """
    real = "hierarchical-aif/reports/frozen-evidence-baseline.sha256"
    blob = s9.blobs_at_head([real])[real]
    # The CRLF form of a file whose committed form is LF - the S9 shape exactly.
    crlf = blob.replace(b"\n", b"\r\n")

    # The disk bytes are INJECTED, because on this tree every candidate fixture has identical disk
    # and blob bytes — so without injection the constructed pin matches neither and the test passes
    # on DRIFTED, never having seen an S9 at all. It was doing exactly that before this fix.
    got = s9.classify({"pin": s9.sha256(crlf), "path": real, "declared_in": "synthetic"},
                      blob, disk=crlf)
    assert got["state"] == "S9", (
        "a pin matching the working copy and NOT the commit was classified %s — the exact shape "
        "of the stop condition is not being caught" % got["state"])


def test_NEGATIVE_CONTROL_a_correct_pin_reads_REPRODUCIBLE():
    """Without this, every refusal above is satisfiable by a classifier that refuses everything."""
    real = "hierarchical-aif/reports/frozen-evidence-baseline.sha256"
    blob = s9.blobs_at_head([real])[real]
    good = s9.classify({"pin": s9.sha256(blob), "path": real, "declared_in": "synthetic"}, blob)
    assert good["state"] == "REPRODUCIBLE"


def test_a_MISSING_path_is_its_own_state_not_a_pass():
    """A pinned path that is not there must not read REPRODUCIBLE by having nothing to compare."""
    got = s9.classify({"pin": "0" * 64, "path": "no/such/file.json", "declared_in": "synthetic"}, None)
    assert got["state"] == "MISSING"


def test_the_S9_verdict_NAMES_ITS_CAUSE():
    """A refusal a reader cannot act on is a refusal they learn to ignore.

    S9 has two very different causes — line endings, which is a recording fault and repairable by
    re-recording, and genuinely divergent content, which is not. The classifier says which.
    """
    real = "hierarchical-aif/reports/frozen-evidence-baseline.sha256"
    blob = s9.blobs_at_head([real])[real]
    crlf = blob.replace(b"\n", b"\r\n")
    got = s9.classify({"pin": s9.sha256(crlf), "path": real, "declared_in": "synthetic"},
                      blob, disk=crlf)
    assert got["state"] == "S9"
    assert got["cause"] and "IDENTICAL TEXT" in got["cause"], (
        "an S9 finding must say whether the text is the same — that is the difference between a "
        "pin to re-record and evidence to investigate: %r" % got["cause"])
