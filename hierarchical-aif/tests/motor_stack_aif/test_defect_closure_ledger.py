"""The defect CLOSURE ledger must stay routed, scoped, and consistent with the test suite.

A defect ledger rots in three ways, none of which any other test would notice:

  UNROUTED   — a defect is recorded but never assigned a closure route, so "we know about it"
               silently substitutes for "we did something about it".
  UNSCOPED   — a defect's impact is written as a global retreat ("P6 is weaker") instead of a
               scoped one ("P6 for C11 U4 is withdrawn; P6 for duration-only B3/B4 is
               unchanged"). Unscoped weakening is banned by the operating contract.
  DESYNCED   — the per-defect status and the closure-summary table drift apart, or the ledger
               claims a test file that does not exist.

This file parses the ledger and asserts all three cannot happen without a red test.

D5 declaration: no data is loaded; this reads a governance document.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
LEDGER = REPO / "hierarchical-aif" / "ledgers" / "HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md"
TESTS_DIR = REPO / "hierarchical-aif" / "tests" / "motor_stack_aif"

REQUIRED_DEFECTS = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12"]

REQUIRED_FIELDS = (
    "affected_lane",
    "unaffected_lanes",
    "defect_summary",
    "repair_or_quarantine_action",
    "test_added",
    "rerun_required",
    "gate_impact",
    "existing_P_level_impact",
    "closure_status",
    "next_action",
    "blocking_or_nonblocking",
)

# Allowed closure-route FAMILIES. A status must begin with one of these stems, so every defect is
# routed into repair, quarantine, rerun, or falsification and none is left merely "recorded".
# `QUARANTINE` is used as the stem rather than `QUARANTINED` because it is a prefix of both; the
# ledger currently mixes `QUARANTINED_...` (D5) and `QUARANTINE_...` (D6). That inconsistency is
# recorded as a finding, not silently normalised, and both route to the same family.
CLOSURE_FAMILIES = ("CLOSED", "CLOSING", "QUARANTINE", "OPEN", "FALSIFIED_AND_RETIRED")

DECLARED_LANES = {"LANE A", "LANE B", "LANE C", "LANE D", "LANE E", "LANE F"}

# Tokens that make an impact statement SCOPED rather than a blanket retreat. Matched
# case-insensitively. Each names a boundary: which thing, or which things are untouched.
SCOPE_TOKENS = ("only", " for ", "unchanged", "untouched", "no other",
                "no scientific level moves", "limited", "provenance")


def _parse_ledger(text: str) -> dict:
    """Return {defect_id: {field: value}} for every `## D<n>_...` section."""
    out: dict[str, dict[str, str]] = {}
    current = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(D\d+)_", line.strip())
        if m:
            current = m.group(1)
            out[current] = {"_heading": line.strip()[3:]}
            continue
        if line.strip().startswith("## "):
            current = None
            continue
        if current is None:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")] \
            if line.strip().startswith("|") else None
        if not cells or len(cells) != 2:
            continue
        key, value = cells
        if key in REQUIRED_FIELDS:
            out[current][key] = value
    return out


def _parse_closure_summary(text: str) -> dict:
    """Return {defect_id: family} from the closure-summary table at the foot of the ledger."""
    tail = text.split("## Closure summary", 1)
    if len(tail) != 2:
        return {}
    out = {}
    for line in tail[1].splitlines():
        s = line.strip()
        if not s.startswith("|") or s.startswith("|-"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 2:
            continue
        status_cell, defects_cell = cells
        fam = re.search(r"`([A-Z_]+)`", status_cell)
        if not fam:
            continue
        for d in re.findall(r"\bD\d+\b", defects_cell):
            out[d] = fam.group(1)
    return out


@pytest.fixture(scope="module")
def text():
    assert LEDGER.exists(), "closure ledger missing: %s" % LEDGER
    return LEDGER.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ledger(text):
    return _parse_ledger(text)


# ---------------------------------------------------------------- the parser works at all
def test_the_parser_finds_the_expected_number_of_defect_sections(ledger):
    """NON-VACUITY. Every assertion below is parametrised over what the parser found; if the
    parser silently found nothing, they would all pass trivially."""
    assert len(ledger) == len(REQUIRED_DEFECTS), sorted(ledger)


def test_the_parser_fails_loudly_on_a_gutted_ledger(text):
    """NON-VACUITY. A ledger with a section removed and a status blanked must be detectable."""
    mutated = re.sub(r"^## D3_HASH_SEED_NONDETERMINISM$.*?(?=^## D4_)", "", text,
                     flags=re.S | re.M)
    assert "D3" not in _parse_ledger(mutated)

    blanked = text.replace("| closure_status | `QUARANTINED_RETROSPECTIVE_ONLY` |",
                           "| closure_status |  |")
    assert _parse_ledger(blanked)["D5"]["closure_status"] == ""


# ---------------------------------------------------------------- presence and routing
@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_defect_is_present(did, ledger):
    assert did in ledger, "defect %s is missing from the closure ledger" % did


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_defect_carries_every_required_field(did, ledger):
    entry = ledger[did]
    missing = [f for f in REQUIRED_FIELDS if not entry.get(f, "").strip()]
    assert not missing, "%s is missing/blank: %r" % (did, missing)


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_closure_status_is_drawn_from_the_allowed_vocabulary(did, ledger):
    raw = ledger[did]["closure_status"].strip().strip("`*")
    assert raw.startswith(CLOSURE_FAMILIES), (
        "%s closure_status %r is not routed into any of %r" % (did, raw, CLOSURE_FAMILIES))


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_no_defect_is_left_unrouted(did, ledger):
    """A defect is only a completed FLOW result once it names an action AND a next action."""
    entry = ledger[did]
    action = entry["repair_or_quarantine_action"]
    assert re.search(r"REPAIRED|CLOSED|QUARANTIN|CLOSING|RERUN|FALSIFIED|POLICY BUILT",
                     action, re.I), "%s action is not a routing decision: %r" % (did, action)
    assert entry["next_action"].strip().lower() not in {"", "none", "n/a", "tbd"}


# ---------------------------------------------------------------- scoping (anti-unscoped-weakening)
@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_defect_names_the_lanes_it_does_not_touch(did, ledger):
    un = ledger[did]["unaffected_lanes"]
    assert un.strip().lower() not in {"", "none", "n/a", "-"}, (
        "%s names no unaffected lane; that is an unscoped weakening statement" % did)
    assert len(un) > 20, "%s unaffected_lanes is too thin to be a real scope: %r" % (did, un)


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_defect_names_an_affected_lane_from_the_declared_vocabulary(did, ledger):
    aff = ledger[did]["affected_lane"]
    assert any(lane in aff for lane in DECLARED_LANES), (
        "%s affected_lane %r names no declared lane" % (did, aff))


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_P_level_impact_is_scoped(did, ledger):
    """The banned formulation is the unscoped one. An impact statement must say WHICH claim moves
    or WHICH lanes are untouched."""
    impact = ledger[did]["existing_P_level_impact"].lower()
    assert any(tok in impact for tok in SCOPE_TOKENS), (
        "%s existing_P_level_impact is unscoped: %r" % (did, impact))


def test_the_scoped_P_level_statements_section_survives(text):
    """These sentences are the replacement for the banned unscoped wording; losing them would
    reopen the door to 'P6 is weaker'."""
    assert "`P6` for C11 U4" in text
    assert "`P6` for duration-only B3/B4" in text
    assert "unchanged" in text


# ---------------------------------------------------------------- summary consistency
def test_the_closure_summary_covers_every_defect(text):
    summary = _parse_closure_summary(text)
    assert set(summary) == set(REQUIRED_DEFECTS), sorted(summary)


# D7 HISTORY — why this list is plain again.
# This parametrisation previously carried D7 as a STRICT xfail, because the ledger told two
# stories about it: the D7 section recorded `OPEN_UNTIL_WIDTH_FIELDS_CORRECTED_IN_NEW_REPORTS`
# (family OPEN) while the closure-summary table listed D7 under `CLOSING`. That disagreement was
# held visible here rather than papered over by editing the ledger.
#
# It was reconciled on 2026-07-22 by the ledger owner, on a SUBSTANTIVE change of state rather
# than a relabel: the forward guard now exists and is mutation-tested (a reported `width` must
# equal the width of the interval reported alongside it, and must carry `intervalType`), and the
# corrected ~0.042-nat resolution floor is now asserted against the frozen BCa endpoints. The
# section reads `CLOSING_BY_FORWARD_GUARD_AND_CORRECTED_FLOOR`, which is family CLOSING and
# agrees with the summary. The strict xfail therefore XPASSed and D7 returns to the plain list.
# The reconciliation itself is recorded in the ledger's `status_reconciliation` row, so the
# disagreement remains auditable rather than erased.
@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_the_summary_family_matches_the_per_defect_closure_status(did, text, ledger):
    """DESYNC GUARD. Changing a per-defect status without updating the summary (or the reverse)
    is how a ledger starts telling two different stories."""
    summary = _parse_closure_summary(text)
    raw = ledger[did]["closure_status"].strip().strip("`*")
    fam_status = next(f for f in CLOSURE_FAMILIES if raw.startswith(f))
    fam_summary = next(f for f in CLOSURE_FAMILIES if summary[did].startswith(f))
    assert fam_status == fam_summary, (
        "%s: section says %r (family %s) but the summary says %r (family %s)"
        % (did, raw, fam_status, summary[did], fam_summary))


# ---------------------------------------------------------------- claimed tests must exist
def _claimed_test_files(entry):
    return re.findall(r"`([A-Za-z0-9_./-]+\.py)`", entry["test_added"])


@pytest.mark.parametrize("did", REQUIRED_DEFECTS)
def test_every_test_file_the_ledger_claims_actually_exists(did, ledger):
    claimed = _claimed_test_files(ledger[did])
    assert claimed, "%s claims no test file" % did
    missing = [f for f in claimed if not (TESTS_DIR / Path(f).name).exists()]
    assert not missing, "%s claims test files that do not exist: %r" % (did, missing)


def test_the_claimed_test_file_scan_is_not_vacuous(ledger):
    """NON-VACUITY: the extractor must actually pull filenames out of the ledger."""
    all_claimed = {f for did in ledger for f in _claimed_test_files(ledger[did])}
    assert len(all_claimed) >= 6, sorted(all_claimed)
    assert "test_hash_seed_determinism.py" in all_claimed


# ---------------------------------------------------------------- individual routing facts
def test_D1_is_closed_by_rerun_and_stays_scoped_to_C11_U4(ledger):
    """D1's corrected C11 run landed. The scoped statement must survive closure: C11 U4 is the
    only lane it ever touched, and B3 (LANE A) was never touched. Closure must not generalise
    into a claim about anything beyond C11 U4."""
    e = ledger["D1"]
    assert e["closure_status"].strip("`") == "CLOSED_BY_CORRECTED_RERUN"
    assert "C11 U4" in e["blocking_or_nonblocking"]
    assert "LANE A" in e["unaffected_lanes"]
    # closing D1 re-established P6 for C11 U4 ON THE CORRECTED RUN ONLY - never the withdrawn artifact
    imp = e["existing_P_level_impact"].lower()
    assert "corrected run only" in imp and "withdrawn" in imp, (
        "D1 closure must state that P6 for C11 U4 is re-established on the corrected run ONLY and "
        "the submitted artifact stays withdrawn: %r" % e["existing_P_level_impact"])


def test_D5_is_quarantined_and_leaves_the_duration_lane_intact(ledger):
    e = ledger["D5"]
    assert e["closure_status"].strip("`").startswith("QUARANTIN")
    assert "LANE A" in e["unaffected_lanes"] and "duration-only" in e["unaffected_lanes"]
    assert "LANE D" in e["unaffected_lanes"]


def test_D5_is_not_claimed_repairable_by_rerun(ledger):
    """Reading held-out data is irreversible; a rerun cannot undo it. If this field ever said
    YES, the irreversibility would have been quietly denied."""
    assert "Not repairable by rerun" in ledger["D5"]["rerun_required"]
