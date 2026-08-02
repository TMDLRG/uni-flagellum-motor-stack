"""D11 — numbers quoted in generated reports must trace to the artifact they claim to quote.

WHAT HAPPENED
-------------
Two numbers in `reports/POWER-ATLAS-MOTOR-EQUAL-SCORING.md` could not be traced to any artifact:

  * a Monte-Carlo SE quoted as `0.043` for the worst cross-check cell, where `power_atlas.json`
    records `0.03952847075210474`;
  * a D10-counterfactual mean CI half-width quoted as `0.0790`, where the artifact records
    `0.07996917206325926`.

The second is the instructive one. `0.0790` is not a rounding of anything in that row — it is the
**recorded M3 percentile half-width `0.0789979` transplanted from a different table in the same
document**. A transplanted neighbouring number is the hardest fabrication class to catch by eye:
real, precise, and locally plausible.

Both survived the authoring agent's own `claim_guard.py` run, because **that guard checks WORDING
and never numeric provenance**. This file is the narrow mechanical control that the wording guard
cannot be: it pins the specific values so the fabrications cannot silently reappear, and it pins
the label collision found in the same sweep.

SCOPE — STATED HONESTLY
-----------------------
This does **not** solve numeric provenance in general. Generic provenance is not decidable by a
test: a report may legitimately quote a derived quantity, a rounded value, or a number from
another artifact. The general control is the adversarial verification lane with an explicit
trace-every-number brief. What this file does is make the KNOWN defect a regression, and encode
the pattern that caught it — compare the printed figure against the recorded field it names.

D5 declaration: no data is loaded; this reads a result artifact and a markdown report.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
ATLAS_JSON = REPO / "hierarchical-aif/results/motor_stack_aif/power_atlas.json"
ATLAS_MD = REPO / "hierarchical-aif/reports/POWER-ATLAS-MOTOR-EQUAL-SCORING.md"


@pytest.fixture(scope="module")
def atlas():
    if not ATLAS_JSON.exists():
        pytest.skip("power_atlas.json not present in this working tree")
    return json.loads(ATLAS_JSON.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def report():
    if not ATLAS_MD.exists():
        pytest.skip("power atlas report not present in this working tree")
    return ATLAS_MD.read_text(encoding="utf-8")


# ---------------------------------------------------------------- the two fabricated values
def test_worst_cell_monte_carlo_se_is_the_recorded_value_not_the_fabricated_one(atlas, report):
    """The worst cross-check cell's MC SE must be quoted from the artifact."""
    cells = atlas["cells"]
    worst = max(cells, key=lambda c: abs(c["resolveRate"] - c["analyticResolveRate"]))
    recorded = worst["resolveRateMonteCarloSE"]

    # the recorded value must appear in the report
    assert repr(recorded) in report or ("%.17g" % recorded) in report, (
        "the report does not quote the recorded resolveRateMonteCarloSE %r for the worst "
        "cross-check cell" % recorded)

    # and the fabricated one must not
    assert "MC SE 0.043" not in report, (
        "the fabricated 'MC SE 0.043' has reappeared; the artifact records %r" % recorded)


def test_d10_counterfactual_half_width_is_the_recorded_value_not_the_transplanted_one(atlas, report):
    """`0.0790` was the M3 percentile half-width transplanted from another table. Pin it out."""
    recorded = atlas["d10Counterfactual"]["meanCIHalfWidthNats"]
    assert abs(recorded - 0.07996917206325926) < 1e-15, (
        "the recorded D10-counterfactual half-width changed: %r" % recorded)

    row = [ln for ln in report.splitlines() if "D10 counterfactual" in ln]
    assert row, "the D10 counterfactual row vanished from the report"
    line = row[0]

    assert "0.0790" not in line, (
        "the transplanted value 0.0790 has reappeared in the D10 counterfactual row. The artifact "
        "records %r; 0.0790 is the RECORDED M3 percentile half-width 0.0789979 from a different "
        "table in the same document." % recorded)
    assert "0.0800" in line, (
        "the D10 counterfactual row no longer quotes the recorded half-width to 4 dp (0.0800 from "
        "%r)" % recorded)


def test_the_quoted_max_and_mean_divergence_reproduce_from_the_cells(atlas, report):
    """NON-VACUITY: two figures in the same sentence WERE correct — the test must not flag them."""
    cells = atlas["cells"]
    divs = [abs(c["resolveRate"] - c["analyticResolveRate"]) for c in cells]
    assert "%.4f" % max(divs) == "0.0876", "max divergence changed: %r" % max(divs)
    assert "%.4f" % (sum(divs) / len(divs)) == "0.0169", "mean divergence changed"
    assert "0.0876" in report and "0.0169" in report, (
        "the correctly-quoted divergence figures are missing; this test would then be checking "
        "nothing")


# ---------------------------------------------------------------- ladder label collision
def test_atlas_predictions_do_not_collide_with_the_frozen_parity_ladder(report):
    """The atlas numbered its own predictions P1..P4 while using P0..P8 in the ladder sense.

    Inside one document that is a genuine ambiguity: a reader meeting `| P4 | ... | **HELD** |`
    could take it for a statement about `P4` transfer, which no probe may touch.
    """
    for bad in ("| P1 |", "| P2 |", "| P3 |", "| P4 |"):
        assert bad not in report, (
            "atlas prediction row %r collides with the frozen P0..P8 ladder used elsewhere in the "
            "same document; predictions are labelled A1..A4" % bad)
    for good in ("| A1 |", "| A2 |", "| A3 |", "| A4 |"):
        assert good in report, "atlas prediction row %r missing" % good


def test_the_report_still_uses_the_ladder_sense_correctly(report):
    """NON-VACUITY guard on the rename: the genuine ladder references must survive untouched."""
    assert "`P4` transfer" in report, (
        "the rename appears to have clobbered a genuine parity-ladder reference")


# ---------------------------------------------------------------- the defect is on the record
def test_d11_is_recorded_and_states_the_limit_of_the_wording_guard():
    ledger = (REPO / "hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md").read_text(
        encoding="utf-8")
    assert "D11_FABRICATED_NUMBERS_IN_GENERATED_REPORTS" in ledger
    low = ledger.lower()
    assert "numeric provenance" in low, (
        "D11 must state that numeric provenance is not decidable by a wording guard, so the limit "
        "of claim_guard.py is not mistaken for coverage")
    assert "0.03952847075210474" in ledger and "0.07996917206325926" in ledger, (
        "D11 must carry both recorded values so the fabrications stay traceable")
