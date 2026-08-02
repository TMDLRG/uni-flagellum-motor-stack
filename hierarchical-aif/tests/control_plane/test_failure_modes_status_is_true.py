"""Phase 9 step 3.4 — the FAILURE-MODES.md status line, and the NEGATIVE CONTROL on correcting it.

The step's own falsifier, pre-registered in `phase9_plan.json`:

    correcting it earlier launders the F28-F31 gap into 'as designed'

That is a falsifier about the CORRECTION, not about the code. A status line is the one place in
this repository where overclaiming costs nothing at the moment of writing and everything later, so
the correction needs a guard that fires when the document starts flattering the work.

M6, NEGATIVE CONTROL: these are cases that must NOT fire — the document must go on saying the
unflattering things. Every assertion here fails if the doc gets tidier than the truth:

  * F31 must still be described as UNFINISHED, with go-live CLOSED rather than guarded;
  * the claim level must still read `presence_evident` and still say NOT unforgeable;
  * the unauthenticated OBS WebSocket must still be named, because it is the limit that matters;
  * F24-F27 must still read DESIGN, because nothing in stage 3 touched them;
  * and the F8 residual must still be recorded as VOID.

This test does not check that F28-F30 work. That is what their own tests are for, and asserting it
here from a document would be circular.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DOC = REPO_ROOT / "docs" / "control-plane" / "FAILURE-MODES.md"


def text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_the_document_exists_and_the_check_cannot_pass_by_not_running():
    assert DOC.is_file(), "FAILURE-MODES.md is missing; a doc check with nothing to read is not a pass"
    assert "| F31 |" in text(), "the refusal table has lost F31; this guard would be vacuous"


def test_F31_is_still_described_as_UNFINISHED_and_go_live_as_CLOSED():
    t = text()
    assert re.search(r"F31 IS NOT FINISHED", t), (
        "the status no longer says F31 is unfinished — that is the falsifier for step 3.4, "
        "laundering the gap into 'as designed'")
    assert "mint" in t and re.search(r"is not minted by anything|does NOT exist", t), (
        "the missing human-presence mint is no longer named; a guard nothing can open is not a "
        "guarded door and the document has to keep saying so")
    assert re.search(r"go-live is closed rather than guarded|shut door rather than a guarded one", t, re.I)


def test_the_claim_level_is_still_stated_and_still_says_NOT_unforgeable():
    t = text()
    assert "presence_evident" in t
    assert re.search(r"NOT unforgeable", t), (
        "the claim level has been quietly promoted; a guard trusted further than it can carry is "
        "worse than none")


def test_the_unauthenticated_actuator_is_still_named():
    """The limit that actually matters. A document that drops it is claiming the box is bound."""
    t = text()
    assert "4455" in t, "the OBS WebSocket port is no longer named"
    assert re.search(r"no authentication", t, re.I)
    assert re.search(r"does not bind the box", t, re.I), (
        "F31's boundary — it binds this codebase's paths to air, not the box — has been dropped")


def test_F24_to_F27_still_read_DESIGN_because_nothing_touched_them():
    t = text()
    assert re.search(r"F24[–\-]F27 remain \*\*DESIGN\*\*|F24[–\-]F27 remain DESIGN", t), (
        "F24-F27 are no longer marked DESIGN. Stage 3 did not touch them, so anything else is a "
        "claim nobody earned")


def test_the_F8_residual_is_recorded_as_VOID_not_as_closed():
    """Phase 5 claimed to close it via a second custodian that does not qualify. It is void."""
    t = text()
    assert "is therefore VOID" in t, (
        "Phase 5's closure of the F8 residual is no longer recorded as VOID")
    assert "store_anchor_in_practice_test.exs:145" in t, (
        "the VOID no longer names the test it voids, so a reader cannot check it")
    assert "independent_custodians: 0" in t, (
        "the measured fact behind the VOID has been dropped; a correction without its measurement "
        "is an opinion")
    assert re.search(r"tamper-evident, not unforgeable", t, re.I)


def test_the_correction_LEAVES_the_superseded_paragraph_standing():
    """A record of what was believed is part of the record, exactly as in the ledger."""
    t = text()
    assert "refuses every credential the writer holds" in t, (
        "the now-false Phase 5 paragraph was DELETED rather than corrected. The ledger's rule "
        "applies to documents too: a correction is an addition, and what was believed at the "
        "time stays visible")
    # Anchor on the CORRECTION's own words, not on the bare token "VOID" — that appears earlier in
    # the F12 paragraph ("two differences are VOID and unclaimable"), a different use entirely, and
    # the first version of this assertion matched it and failed for the wrong reason.
    assert t.index("refuses every credential the writer holds") < t.index("is therefore VOID"), (
        "the correction must come AFTER the claim it corrects — this section is 'most recent last'")
