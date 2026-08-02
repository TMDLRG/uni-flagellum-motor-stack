"""D11 — the numeric provenance guard must catch the two values that actually got through.

The bar this file has to clear is specific, and it is the bar the defect set:

  * `0.043` — a Monte-Carlo SE quoted where `power_atlas.json` records `0.03952847075210474`.
    An invented figure: it appears nowhere in any artifact.
  * `0.0790` — a mean CI half-width quoted where the artifact records `0.07996917206325926`.
    NOT invented: it is the recorded M3 percentile half-width `0.0789979` **transplanted from a
    different table in the same document**.

The second is the reason a naive checker is useless here. "Does this number appear somewhere in
some artifact?" returns **True** for `0.0790` — it is a real recorded value, just of something
else. Provenance has to be about the POINTER, not the digits. These tests prove the guard makes
that distinction, and prove it on a real artifact rather than a toy.

D5: reads a result artifact and synthetic in-memory markdown. No data channel is touched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import numeric_provenance_guard as npg  # noqa: E402

ATLAS = REPO / "hierarchical-aif/results/motor_stack_aif/power_atlas.json"

# The two D11 values, with the pointer each one *claimed* to be.
FABRICATED_SE = "0.043"
RECORDED_SE = 0.03952847075210474
SE_POINTER = "power_atlas.json#cells.0.resolveRateMonteCarloSE"      # placeholder, fixed in fixture

TRANSPLANTED_HW = "0.0790"
RECORDED_HW = 0.07996917206325926
HW_POINTER = "power_atlas.json#d10Counterfactual.meanCIHalfWidthNats"


@pytest.fixture(scope="module")
def artifacts():
    if not ATLAS.exists():
        pytest.skip("power_atlas.json not present in this working tree")
    return npg.load_artifacts()


@pytest.fixture(scope="module")
def se_pointer(artifacts):
    """Locate the worst cross-check cell's index so the pointer is real, not assumed."""
    cells = artifacts["power_atlas.json"]["cells"]
    idx = max(range(len(cells)),
              key=lambda i: abs(cells[i]["resolveRate"] - cells[i]["analyticResolveRate"]))
    assert abs(cells[idx]["resolveRateMonteCarloSE"] - RECORDED_SE) < 1e-15, (
        "the worst cell's recorded MC SE changed: %r" % cells[idx]["resolveRateMonteCarloSE"])
    return "power_atlas.json#cells.%d.resolveRateMonteCarloSE" % idx


def _scan(tmp_path, body, artifacts):
    p = tmp_path / "probe.md"
    p.write_text(body, encoding="utf-8", newline="\n")
    return npg.scan_file(p, artifacts)


# ---------------------------------------------------------------- the two real D11 values
def test_the_invented_monte_carlo_se_is_caught(tmp_path, artifacts, se_pointer):
    body = ("<!-- prov: %s = %s -->\n\nworst cell MC SE %s\n"
            % (FABRICATED_SE, se_pointer, FABRICATED_SE))
    f = [x for x in _scan(tmp_path, body, artifacts) if x["number"] == FABRICATED_SE]
    assert f, "the guard did not see the number at all"
    assert f[0]["status"] == "ANCHORED_MISMATCH", f[0]
    assert f[0]["passed"] is False
    assert "0.0395" in f[0]["detail"] or "%r" % RECORDED_SE in f[0]["detail"], f[0]["detail"]


def test_the_transplanted_half_width_is_caught_and_named(tmp_path, artifacts):
    """The harder case: a REAL recorded value, pointed at the wrong field."""
    body = ("<!-- prov: %s = %s -->\n\nD10 counterfactual half-width %s\n"
            % (TRANSPLANTED_HW, HW_POINTER, TRANSPLANTED_HW))
    f = [x for x in _scan(tmp_path, body, artifacts) if x["number"] == TRANSPLANTED_HW]
    assert f, "the guard did not see the number at all"
    assert f[0]["status"] == "ANCHORED_MISMATCH", f[0]
    assert f[0]["passed"] is False


def test_a_naive_does_it_appear_anywhere_check_would_have_PASSED_the_transplant(artifacts):
    """NON-VACUITY / root cause. This is why the pointer matters and the digits do not.

    If this ever fails, the transplanted value has stopped being a real recorded quantity and the
    test above would no longer be exercising the hard case.
    """
    hits = npg.find_transplant_source(artifacts, TRANSPLANTED_HW)
    assert hits, (
        "0.0790 no longer matches any recorded field, so it would now look like a plain "
        "invention and the hard transplant case would be untested")


def test_the_correct_values_pass(tmp_path, artifacts, se_pointer):
    """NON-VACUITY: the guard must not simply fail everything."""
    body = ("<!-- prov: 0.0800 = %s -->\n<!-- prov: 0.0395 = %s -->\n\n"
            "half-width 0.0800 and MC SE 0.0395\n" % (HW_POINTER, se_pointer))
    got = {x["number"]: x for x in _scan(tmp_path, body, artifacts)}
    for n in ("0.0800", "0.0395"):
        assert got[n]["status"] == "ANCHORED_OK", got[n]
        assert got[n]["passed"] is True


# ---------------------------------------------------------------- mechanism
def test_display_precision_is_the_comparison_rule(artifacts):
    assert npg.matches_at_display_precision("0.0800", RECORDED_HW)
    assert not npg.matches_at_display_precision("0.0790", RECORDED_HW)
    assert npg.matches_at_display_precision("0.07996917206325926", RECORDED_HW)
    # scientific notation compares relatively
    assert npg.matches_at_display_precision("2.507e-07", 2.506984e-07)


def test_markers_and_unanchored_are_classified_not_failed(tmp_path, artifacts):
    body = ("floor 0.04207043063262626 DESIGN_ONLY\n"
            "torque 12.3456 NOT-MEASURED\n"
            "some derived 0.12345 with no anchor\n")
    got = _scan(tmp_path, body, artifacts)
    st = {x["number"]: x["status"] for x in got}
    assert st["0.04207043063262626"] == "MARKED"
    assert st["12.3456"] == "MARKED"
    assert st["0.12345"] == "UNANCHORED"
    assert all(x["passed"] for x in got), "markers and unanchored numbers must not fail"


def test_an_unresolvable_pointer_fails(tmp_path, artifacts):
    body = "<!-- prov: 0.1234 = power_atlas.json#no.such.path -->\n\nvalue 0.1234\n"
    f = [x for x in _scan(tmp_path, body, artifacts) if x["number"] == "0.1234"]
    assert f[0]["status"] == "ANCHORED_UNRESOLVABLE"
    assert f[0]["passed"] is False


def test_guard_runs_over_the_real_namespace_without_error():
    """Smoke: the guard must survive the actual document set."""
    findings = npg.scan_paths([REPO / "hierarchical-aif" / "reports"])
    assert findings, "no decimals found across the reports directory - the scan is not working"
    s = npg.summarise(findings)
    assert s["total"] == len(findings)
    assert isinstance(s["byStatus"], dict)


def test_d11_records_the_guard_and_its_scope():
    ledger = (REPO / "hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md"
              ).read_text(encoding="utf-8")
    assert "D11_FABRICATED_NUMBERS_IN_GENERATED_REPORTS" in ledger
    assert "numeric_provenance_guard" in ledger, (
        "D11 must name the guard once it exists, or the ledger under-reports its own repair")
