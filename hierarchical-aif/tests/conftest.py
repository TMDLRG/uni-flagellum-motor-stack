"""F28's wiring — the test session refuses to start on a drifted frozen tree.

    F28 | frozen evidence hashes drift | STOP_FROZEN_EVIDENCE_DRIFT, halt everything
        | falsifier: WORK CONTINUES PAST A DRIFT

The falsifier is about CONTINUING, so the halt has to sit where continuing happens. This runs at
`pytest_sessionstart`, before a single test is collected: if `audits/phase-c/**` or
`audits/phase-d/**` no longer match `hierarchical-aif/reports/frozen-evidence-baseline.sha256`,
the whole session exits and says which files and how.

The paths are HARDCODED to the real baseline, deliberately. A halt that can be aimed at a tree of
its own choosing halts nothing, and an environment variable that relocates it is an off switch
with a polite name. Detection is proved against disposable copies in
`tests/motor_stack_aif/test_frozen_evidence_halts.py`; this file is proved to be wired to the
real one by reading its own source.

Cost, stated rather than discovered later: a deliberate re-freeze of the evidence record makes
this suite refuse to run until the baseline is regenerated. That is the intended behaviour of a
hard stop, and regenerating the baseline is a decision about the evidence record — the operator's,
not an agent's.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import frozen_evidence_guard  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "hierarchical-aif" / "reports" / "frozen-evidence-baseline.sha256"


def pytest_sessionstart(session):  # noqa: ARG001 - pytest hook signature
    if not BASELINE.is_file():
        pytest.exit("%s — the frozen-evidence baseline itself is missing: %s\n"
                    "A guard whose manifest can be deleted is a guard that can be deleted."
                    % (frozen_evidence_guard.STOP, BASELINE), returncode=3)

    report = frozen_evidence_guard.verify(BASELINE, REPO_ROOT)
    if not report["ok"]:
        pytest.exit("\n" + frozen_evidence_guard.account(report), returncode=3)
