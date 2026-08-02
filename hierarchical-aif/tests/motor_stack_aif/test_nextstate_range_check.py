"""D6 regression — impossible nextStateN must never be silently accepted.

The committed dataset contains 2 events with nextStateN = -1 (physically impossible stator count),
because scripts/ingest-wadhwa-data.py range-checks dwell["state"] but writes next_state through
unchecked. The dataset is FROZEN historical evidence and is NOT edited.

These tests pin the defect and require any future mark-model preparation to handle it explicitly:
reject, quarantine with status, or retain under a documented raw-data-defect label - never drop
silently.

Split boundary: NO_DATA_ACCESS_NEEDED beyond the two already-identified events, whose mark channel
was already burned by D5. These tests compute no new held-out statistic.
"""
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import _bridge, marks  # noqa: E402

PHYSICAL_MIN_STATORS = 0
PHYSICAL_MAX_STATORS = 11
KNOWN_BAD = {"19-01-31-1329:0004", "19-01-31-1329:0011"}


@pytest.fixture(scope="module")
def events():
    import json
    p = _bridge.REPO_ROOT / "experiments" / "data" / "wadhwa-2022-events.json"
    return json.loads(p.read_text(encoding="utf-8"))["events"]


def test_the_known_defect_is_still_present_and_unedited(events):
    """The frozen dataset must NOT be silently repaired. This asserts the defect persists."""
    bad = {e["eventId"] for e in events
           if e.get("nextStateN") is not None and e["nextStateN"] < PHYSICAL_MIN_STATORS}
    assert bad == KNOWN_BAD, (
        "expected exactly the 2 known out-of-range marks (dataset must not be edited); got %r" % bad
    )


def test_detector_flags_impossible_nextstate(events):
    flagged = marks.flag_impossible_marks(
        events, min_state=PHYSICAL_MIN_STATORS, max_state=PHYSICAL_MAX_STATORS)
    assert {f["eventId"] for f in flagged} == KNOWN_BAD
    for f in flagged:
        assert f["reason"] == "NEXT_STATE_BELOW_PHYSICAL_MINIMUM"


def test_preparation_refuses_silent_drop(events):
    """Default policy must REFUSE rather than quietly discard impossible marks."""
    with pytest.raises(marks.ImpossibleMarkError):
        marks.prepare_mark_dataset(events, policy="strict")


def test_quarantine_policy_preserves_and_labels(events):
    kept, quarantined = marks.prepare_mark_dataset(events, policy="quarantine")
    assert {e["eventId"] for e in quarantined} == KNOWN_BAD
    assert all("quarantineReason" in e for e in quarantined)
    assert KNOWN_BAD.isdisjoint({e["eventId"] for e in kept})
    # nothing is lost: every event is accounted for in exactly one bucket
    assert len(kept) + len(quarantined) == len(events)


def test_documented_defect_policy_retains_with_label(events):
    kept, quarantined = marks.prepare_mark_dataset(events, policy="retain_labelled")
    assert quarantined == []
    labelled = [e for e in kept if e.get("rawDataDefect")]
    assert {e["eventId"] for e in labelled} == KNOWN_BAD


def test_unknown_policy_is_rejected(events):
    with pytest.raises(ValueError):
        marks.prepare_mark_dataset(events, policy="ignore")


def test_closed_chain_assumption_is_refused(events):
    """15-17% of marks leave {1..8}: a closed-chain model over that set must be refused."""
    with pytest.raises(marks.OpenMarkAlphabetError):
        marks.assert_closed_alphabet(events, states=tuple(range(1, 9)), partition="train")
