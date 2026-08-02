"""D7 — the published `width` field is the PERCENTILE companion width, never the BCa width.

The closure ledger recorded this test as a delivered receipt for D7, but the file did not exist
(found 2026-07-22 during active-flow supervision, logged as D8_LEDGER_CLAIMED_UNDELIVERED_TESTS).
This is the test the ledger promised.

WHAT D7 IS, PRECISELY
---------------------
In the frozen B3 artifact every contrast entry carries four interval fields (`bca`, `percentile`,
`bonferroni99375`, `intervalUsed`) and one scalar `width`. `intervalUsed` is the BCa interval and
is what every verdict is computed from. `width`, however, equals the width of the *percentile
companion* in 48 of 48 entries and the BCa width in 0 of 48.

So D7 is a REPORTING defect, not a verdict defect:
  - no verdict changes, because verdicts read `intervalUsed` (BCa);
  - but any resolution/power argument built on `width` used the wrong interval. Track D's
    "0.064 nats" resolution floor came from this field; the corrected floor is ~0.042 nats.

These tests PIN the defect on the frozen artifact rather than repairing it. The frozen artifact is
read-only historical evidence and is deliberately NOT edited. If one of these assertions ever
starts failing, the frozen evidence has been mutated — which is a hard stop, not a test to update.

NON-CIRCULARITY
---------------
Every expected quantity here is recomputed from the recorded interval endpoints by this file's own
arithmetic. Nothing is imported from the code that produced the artifact, and no expected value is
read from a field that the artifact also derives.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
B3_RESULT = REPO_ROOT / "audits" / "phase-b" / "b3-model-competition-result.json"

# Endpoints are stored as full-precision float64 JSON, so a recomputed difference of two stored
# endpoints is exact to within one ULP of the subtraction. 1e-12 is ~4 orders of magnitude looser
# than that on values of order 1e-1, and ~10 orders tighter than the 0.0247 divergence being
# distinguished. It cannot confuse the two hypotheses.
EXACT = 1e-12


def _entries():
    """Yield (cohort, rule, modelId, entry) for every recorded contrast."""
    doc = json.loads(B3_RESULT.read_text(encoding="utf-8"))
    for cohort, cv in doc["cohorts"].items():
        for rule, rv in cv["contrasts"].items():
            for model_id, entry in rv.items():
                yield cohort, rule, model_id, entry


@pytest.fixture(scope="module")
def entries():
    rows = list(_entries())
    assert rows, "no contrast entries found — frozen artifact missing or restructured"
    return rows


def test_frozen_artifact_is_present_and_has_the_expected_48_contrasts(entries):
    """2 cohorts x 3 scoring rules x 8 non-reference models = 48. Pins the denominator."""
    assert len(entries) == 48, (
        "expected 48 contrast entries (2 cohorts x 3 rules x 8 models); got %d. The frozen "
        "artifact has changed shape — investigate before touching this test." % len(entries))


def test_published_width_is_the_percentile_width_in_every_entry(entries):
    """THE DEFECT. `width` tracks the percentile companion, in 48/48 entries."""
    mismatches = []
    for cohort, rule, model_id, e in entries:
        pct_width = e["percentile"][1] - e["percentile"][0]
        if not math.isclose(e["width"], pct_width, rel_tol=0.0, abs_tol=EXACT):
            mismatches.append((cohort, rule, model_id, e["width"], pct_width))
    assert not mismatches, "width did not equal the percentile width in: %r" % (mismatches,)


def test_published_width_is_never_the_bca_width(entries):
    """The complement of the above — this is what makes the defect a defect and not a coincidence.

    If BCa and percentile widths happened to be equal everywhere, the previous test would pass
    vacuously. They are not equal: see the divergence test below.
    """
    matches_bca = []
    for cohort, rule, model_id, e in entries:
        bca_width = e["bca"][1] - e["bca"][0]
        if math.isclose(e["width"], bca_width, rel_tol=0.0, abs_tol=EXACT):
            matches_bca.append((cohort, rule, model_id))
    assert not matches_bca, (
        "width equalled the BCa width in %d entries: %r. D7 asserts this never happens; if the "
        "frozen artifact now says otherwise it has been mutated." % (len(matches_bca), matches_bca))


def test_the_two_widths_actually_diverge_so_the_defect_is_material(entries):
    """Guards the two tests above against vacuity, and pins the recorded divergence magnitude."""
    divergences = [abs((e["bca"][1] - e["bca"][0]) - (e["percentile"][1] - e["percentile"][0]))
                   for _, _, _, e in entries]
    max_div = max(divergences)
    assert max_div > 1e-6, (
        "BCa and percentile widths are identical everywhere (max divergence %g), so the width "
        "provenance tests above would be vacuous." % max_div)
    # Recorded in the defect ledger as 0.0247 nats. Pinned to 3 decimal places so a genuine
    # artifact change trips it while float formatting does not.
    assert math.isclose(max_div, 0.024688739601508747, rel_tol=0.0, abs_tol=1e-9), (
        "max BCa-vs-percentile width divergence changed: %r" % max_div)


def test_verdicts_are_driven_by_intervalUsed_which_is_the_bca_interval(entries):
    """Why D7 moves no verdict: every decision reads `intervalUsed`, and that IS the BCa interval.

    This is the test that bounds the blast radius. Without it, "D7 affects no verdict" would be an
    assertion rather than a receipt.
    """
    for cohort, rule, model_id, e in entries:
        if e.get("bcaUndefined"):
            continue
        assert e["intervalUsed"] == e["bca"], (
            "%s/%s/%s: intervalUsed is not the BCa interval; D7's 'no verdict is affected' "
            "conclusion would not hold" % (cohort, rule, model_id))


def test_verdict_matches_the_interval_actually_used(entries):
    """An interval containing 0 must read INCONCLUSIVE — never 'no difference', never equivalence."""
    for cohort, rule, model_id, e in entries:
        lo, hi = e["intervalUsed"]
        contains_zero = lo <= 0.0 <= hi
        verdict = e["verdict"]
        if contains_zero:
            assert verdict == "INCONCLUSIVE", (
                "%s/%s/%s: interval [%r, %r] contains 0 but verdict is %r. An interval crossing "
                "the threshold is INCONCLUSIVE; underpowered is not equivalence."
                % (cohort, rule, model_id, lo, hi, verdict))
        else:
            assert verdict != "INCONCLUSIVE", (
                "%s/%s/%s: interval [%r, %r] excludes 0 but verdict is INCONCLUSIVE"
                % (cohort, rule, model_id, lo, hi))
        assert e["beatsM3"] == (lo > 0.0), (
            "%s/%s/%s: beatsM3=%r contradicts the interval [%r, %r] under the recorded convention "
            "contrast = S(M3) - S(M), where an interval entirely above 0 means the challenger wins"
            % (cohort, rule, model_id, e["beatsM3"], lo, hi))


def test_corrected_resolution_floor_is_derived_from_the_bca_interval_not_the_width_field():
    """The superseded 0.064-nat floor came from `width`; the corrected ~0.042 comes from BCa.

    Recomputes the narrowest motor-equal half-width from the BCa endpoints and checks it against
    the corrected figure of record. This is the number every power/resolution statement must use.
    """
    doc = json.loads(B3_RESULT.read_text(encoding="utf-8"))
    contrasts = doc["cohorts"]["derived_eligible_1_to_8"]["contrasts"]["NLPD_motor_equal"]
    half_widths = {mid: (e["bca"][1] - e["bca"][0]) / 2.0 for mid, e in contrasts.items()}
    narrowest_model = min(half_widths, key=half_widths.get)
    narrowest = half_widths[narrowest_model]

    assert narrowest_model == "M4_MIXTURE_K3", (
        "narrowest motor-equal contrast is %r, not M4_MIXTURE_K3. The corrected record names "
        "M4_MIXTURE_K3 (the superseded claim named M2, which is 3rd of 8)." % narrowest_model)
    assert 0.040 <= narrowest <= 0.044, (
        "corrected resolution floor (BCa half-width) is %r; the record states ~0.042 nats. The "
        "superseded 0.064 figure came from the percentile `width` field (D7)." % narrowest)

    # And the defective route must NOT reproduce it — otherwise D7 would have been harmless.
    width_route = min(e["width"] for e in contrasts.values()) / 2.0
    assert not math.isclose(width_route, narrowest, rel_tol=0.0, abs_tol=1e-9), (
        "the `width`-derived floor equals the BCa-derived floor, so D7 would have had no effect "
        "on any resolution argument — contradicting the ledger")


def test_new_hierarchical_aif_intervals_label_which_interval_a_width_belongs_to():
    """Forward guard: the D7 remedy is that NEW reports must say which interval a width is.

    `score.contrast_with_ci` is the only new-code path that emits a `width`, so it must carry an
    explicit interval label. This is what stops D7 from recurring in the new namespace.
    """
    import sys
    src = REPO_ROOT / "hierarchical-aif" / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from motor_stack_aif import score

    per_motor_ref = [1.0, 1.2, 0.9, 1.4, 1.1, 1.3, 0.95, 1.25]
    per_motor_challenger = [0.8, 1.0, 0.7, 1.2, 0.9, 1.1, 0.75, 1.05]
    out = score.contrast_with_ci(per_motor_ref, per_motor_challenger, n_rep=200, seed=20260717)

    assert "intervalType" in out, "a reported width must be accompanied by its interval type (D7)"
    assert out["intervalType"] == "percentile"
    # The emitted width must be the width of the emitted interval — the exact identity D7 broke.
    assert math.isclose(out["width"], out["interval"][1] - out["interval"][0],
                        rel_tol=0.0, abs_tol=1e-12), (
        "width does not equal the width of the interval reported alongside it — this is precisely "
        "the D7 defect reappearing in new code")
    assert "D7" in out.get("note", ""), "the D7 provenance note must travel with the interval"
