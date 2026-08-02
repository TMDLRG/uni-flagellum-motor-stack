"""CI-bound verdicts only. A point estimate is never a verdict.

Three properties:

  1. An interval that CONTAINS the threshold is NOT_ESTABLISHED — in both directions, at both
     exact boundaries, and for a degenerate interval sitting exactly on the threshold.
  2. A point estimate cannot produce a verdict: ``verdict_from_ci`` refuses ``None`` bounds, and
     an AST scan shows the verdict strings exist in exactly one module, so no other code path can
     synthesise one.
  3. "Underpowered" is not "equivalent". A large point-estimate gap with a wide interval is still
     NOT_ESTABLISHED, and a tiny gap with a narrow interval can be RESOLVED. The two are decided
     by the interval, never by the size of the effect.

Coverage note (audit): ``test_not_run_partial_resource_semantics.py`` covers one crossing case and
the ``None``-bound refusal. The boundary cases, the non-zero threshold, the inverted-interval
halt, the AST single-source scan, and the "big gap is still not established" case were not
covered.

D5 declaration: no data is loaded; these are properties of the decision rule.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import numpy as np
import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import score, status  # noqa: E402

PKG_DIR = SRC / "motor_stack_aif"
VERDICTS = {status.NOT_ESTABLISHED, status.RESOLVED_ABOVE, status.RESOLVED_BELOW}


# ---------------------------------------------------------------- 1. containment
@pytest.mark.parametrize("lo,hi", [
    (-1.0, 1.0),      # straddles from both sides
    (-5.0, 0.001),    # mostly below, brushes above
    (-0.001, 5.0),    # mostly above, brushes below
    (0.0, 1.0),       # lower bound EXACTLY on the threshold
    (-1.0, 0.0),      # upper bound EXACTLY on the threshold
    (0.0, 0.0),       # degenerate interval exactly on the threshold
])
def test_interval_containing_the_threshold_is_not_established(lo, hi):
    assert status.verdict_from_ci(lo, hi, threshold=0.0) == status.NOT_ESTABLISHED


@pytest.mark.parametrize("lo,hi,expect", [
    (0.001, 5.0, status.RESOLVED_ABOVE),
    (1e-15, 1e-14, status.RESOLVED_ABOVE),
    (-5.0, -0.001, status.RESOLVED_BELOW),
    (-1e-14, -1e-15, status.RESOLVED_BELOW),
])
def test_interval_excluding_the_threshold_resolves_in_the_right_direction(lo, hi, expect):
    assert status.verdict_from_ci(lo, hi, threshold=0.0) == expect


@pytest.mark.parametrize("threshold", [-2.5, 0.0, 0.042, 7.0])
def test_the_rule_is_the_same_at_a_non_zero_threshold(threshold):
    """The B3 resolution floor is ~0.042 nats, so a non-zero threshold is a real use case."""
    assert status.verdict_from_ci(threshold - 1.0, threshold + 1.0,
                                  threshold=threshold) == status.NOT_ESTABLISHED
    assert status.verdict_from_ci(threshold + 0.1, threshold + 1.0,
                                  threshold=threshold) == status.RESOLVED_ABOVE
    assert status.verdict_from_ci(threshold - 1.0, threshold - 0.1,
                                  threshold=threshold) == status.RESOLVED_BELOW


def test_an_inverted_interval_halts_rather_than_being_reordered():
    """Silently sorting the bounds would let a sign error pass as a verdict."""
    with pytest.raises(ValueError):
        status.verdict_from_ci(1.0, -1.0, threshold=0.0)


# ---------------------------------------------------------------- 2. no point-estimate path
@pytest.mark.parametrize("lo,hi", [(None, None), (None, 1.0), (0.0, None)])
def test_a_missing_bound_refuses_to_produce_a_verdict(lo, hi):
    with pytest.raises(ValueError):
        status.verdict_from_ci(lo, hi, threshold=0.0)


def test_verdict_strings_are_defined_in_exactly_one_module():
    """AST SCAN. If a verdict literal appeared elsewhere, some other code path could emit a
    verdict without ever seeing an interval."""
    offenders = []
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name == "status.py":
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"), filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in VERDICTS:
                    offenders.append("%s:%d: %r" % (p.name, node.lineno, node.value))
    assert not offenders, "verdict literal outside status.py:\n  " + "\n  ".join(offenders)


def test_the_ast_scan_is_not_vacuous():
    """NON-VACUITY: the scan must fire on a planted literal, and must have parsed real files."""
    planted = ast.parse('verdict = "RESOLVED_ABOVE"\n')
    found = [n.value for n in ast.walk(planted)
             if isinstance(n, ast.Constant) and n.value in VERDICTS]
    assert found == ["RESOLVED_ABOVE"]
    assert len(list(PKG_DIR.glob("*.py"))) >= 10


def test_contrast_with_ci_routes_its_verdict_through_the_interval_rule():
    """The reported verdict must be exactly what the reported interval implies — not a separately
    computed judgement that could drift from the interval printed beside it."""
    rng = np.random.default_rng(5)
    a = rng.normal(3.0, 0.5, 19)
    for shift_sd in (0.0, 0.05, 0.4):
        b = a + rng.normal(0.02, shift_sd, 19)
        out = score.contrast_with_ci(a, b, n_rep=800)
        lo, hi = out["interval"]
        assert out["verdict"] == status.verdict_from_ci(lo, hi, threshold=0.0)
        assert out["verdict"] in VERDICTS


def test_contrast_output_carries_an_interval_alongside_every_verdict():
    a = np.array([3.0, 3.1, 2.9, 3.2, 3.05])
    out = score.contrast_with_ci(a, a + 0.01, n_rep=400)
    for required in ("interval", "intervalType", "nRep", "seed", "resamplingUnit", "verdict"):
        assert required in out, required
    assert out["interval"][0] <= out["interval"][1]


# ---------------------------------------------------------------- 3. underpowered != equivalent
def test_a_large_point_estimate_gap_with_a_wide_interval_is_still_not_established():
    """THE anti-pattern this rule exists to stop: reading a big-looking mean difference as a
    result. With 19 motors and high between-motor variance the interval owns the verdict."""
    rng = np.random.default_rng(1)
    a = rng.normal(3.0, 0.4, 19)
    b = a + rng.normal(0.5, 3.0, 19)          # large mean shift, much larger spread
    out = score.contrast_with_ci(a, b, n_rep=3000)
    assert abs(out["pointEstimate"]) > 0.2, out["pointEstimate"]
    assert out["verdict"] == status.NOT_ESTABLISHED, out
    assert out["interval"][0] < 0.0 < out["interval"][1]


def test_not_established_is_not_reported_as_equivalence():
    """Vocabulary guard, on NAMES and on VALUES.

    'Underpowered' is not 'equivalent'. With 19 holdout motors most contrasts are inconclusive, so
    the single most damaging edit available is to rename the inconclusive outcome into an
    equivalence claim. Both the constant's NAME and its emitted VALUE are pinned, because renaming
    only the value would slip past a name-only check and change every report.
    """
    banned = ("EQUIVALENT", "NO_DIFFERENCE", "SAME", "NULL_CONFIRMED", "ACCEPTED_NULL",
              "NO_EFFECT")

    names = {n for n in dir(status) if n.isupper()}
    for b in banned:
        assert b not in names

    # the VALUES the module can emit
    assert status.NOT_ESTABLISHED == "NOT_ESTABLISHED"
    assert status.RESOLVED_ABOVE == "RESOLVED_ABOVE"
    assert status.RESOLVED_BELOW == "RESOLVED_BELOW"
    emitted = {status.verdict_from_ci(lo, hi, threshold=0.0)
               for lo, hi in [(-1.0, 1.0), (0.0, 0.0), (0.1, 1.0), (-1.0, -0.1)]}
    assert emitted == {"NOT_ESTABLISHED", "RESOLVED_ABOVE", "RESOLVED_BELOW"}
    for v in emitted:
        for b in banned:
            assert b not in v
    assert set(VERDICTS) == {"NOT_ESTABLISHED", "RESOLVED_ABOVE", "RESOLVED_BELOW"}


def test_a_partial_run_cannot_be_upgraded_to_a_refutation_by_a_point_estimate():
    """Cross-check with the run-status vocabulary: 30 of 2000 replicates (the D1/D2 case) is
    PARTIAL, whatever the numbers looked like."""
    assert status.classify_run(30, 2000) == status.PARTIAL
    assert status.may_claim_refutation(30, 2000) is False
    assert status.may_claim_refutation(2000, 2000) is True
