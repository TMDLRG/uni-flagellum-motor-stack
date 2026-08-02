"""Claim-guard tests: the clamp must fire on bare claims and stay silent on negated ones."""
import sys
from pathlib import Path
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from motor_stack_aif import claim_guard  # noqa: E402

HAIF = Path(__file__).resolve().parents[2]


def test_bare_forbidden_claim_is_caught():
    v = claim_guard.scan_text("The system has achieved full parity with nature.", "t")
    assert v, "a bare parity claim must be flagged"


def test_negated_claim_is_allowed():
    assert not claim_guard.scan_text(
        "No full parity achieved claim is licensed by this evidence.", "t")
    assert not claim_guard.scan_text(
        "This does not mean active inference demonstrated.", "t")


def test_forbidden_wording_catalogue_is_allowed():
    assert not claim_guard.scan_text(
        "**Forbidden:** biological parity achieved | active inference demonstrated", "t")


def test_m2_promotion_is_caught():
    assert claim_guard.scan_text("Therefore M2 is the UNI model.", "t")


def test_diagnostic_overclaim_is_caught():
    assert claim_guard.scan_text("The C11 diagnostic proves U4 was wrong.", "t")


@pytest.mark.parametrize("sub", ["reports", "docs", "ledgers", "protocols"])
def test_hierarchical_aif_documents_are_clean(sub):
    d = HAIF / sub
    if not d.exists():
        pytest.skip("%s not present" % sub)
    violations = claim_guard.scan_paths([d])
    assert not violations, "claim-guard violations:\n" + "\n".join(
        "  %s:%s  %r  ...%s..." % (v["source"], v["line"], v["phrase"], v["context"])
        for v in violations)


def test_quoted_phrase_is_a_mention_not_a_use():
    """Documents must be able to NAME the wording they prohibit (use/mention)."""
    assert not claim_guard.scan_text(
        'This is the reading that would produce "G proves motor agency".', "t")
    assert not claim_guard.scan_text(
        "Do not write 'biological parity achieved' in any report.", "t")


def test_quoting_does_not_defeat_a_bare_claim_on_another_line():
    """A real claim elsewhere must still be caught even if a quoted mention exists."""
    txt = ('We list "biological parity achieved" as forbidden.\n'
           'Our system has achieved full parity with the organism.')
    assert claim_guard.scan_text(txt, "t")
