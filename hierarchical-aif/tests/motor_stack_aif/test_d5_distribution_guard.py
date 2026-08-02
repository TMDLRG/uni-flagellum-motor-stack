"""D12 — the distribution guard must catch what D5 missed: held-out mark leaks in prose.

WHY THIS EXISTS
---------------
The external D5 safety review found real event-level identifiers and record-shaped mark tuples
surviving in distributable reports, protocols, ledgers and a test fixture, after the review's own
scan (scoped to JSON/JSONL/Markdown) missed a `.py` fixture entirely (`KNOWN_BAD` in
`test_nextstate_range_check.py`). `numeric_provenance_guard` checks number PROVENANCE, not identity
leakage, and `claim_guard` checks forbidden WORDING, not data values. Neither is the right tool.
This guard is a THIRD, separate responsibility: does a shipped artifact contain a real event id, a
motor id tied to the mark defect, or a reconstructable held-out record tuple.

D5: this module and its tests use only SYNTHETIC identifiers of the same shape as the real leak
(`99-99-99-9999:9999`, motor `99-99-99-9999`) — never the real event/motor ids. No held-out data is
read to build or test this guard.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import d5_distribution_guard as guard  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]

# Synthetic examples matching the REAL leak's shape (date-coded motor id : 4-digit event seq).
# These are not real identifiers; they exist only to exercise the detector.
SYNTHETIC_EVENT_ID = "99-99-99-9999:0001"
SYNTHETIC_MOTOR_ID = "99-99-99-9999"


def test_detects_event_id_pattern_in_prose():
    text = "Two events record an impossible mark: `%s` (stateN=0, nextStateN=-1)." % SYNTHETIC_EVENT_ID
    hits = guard.scan_text(text, source="synthetic.md")
    assert any(h["kind"] == "EVENT_ID" for h in hits)


def test_detects_motor_id_only_when_colocated_with_mark_context():
    with_context = "The 2 breaks are holdout, both from motor `%s`, tied to the mark defect." % SYNTHETIC_MOTOR_ID
    hits = guard.scan_text(with_context, source="synthetic.md")
    assert any(h["kind"] == "MOTOR_ID_MARK_CONTEXT" for h in hits)

    bare = "Motor `%s` contributed 12 training events overall." % SYNTHETIC_MOTOR_ID
    hits_bare = guard.scan_text(bare, source="synthetic.md")
    assert not any(h["kind"] == "MOTOR_ID_MARK_CONTEXT" for h in hits_bare)


def test_detects_record_shaped_tuple_with_holdout_label():
    text = "stateN=0 nextStateN=-1 jump=-1 direction=\"off\" partition=holdout"
    hits = guard.scan_text(text, source="synthetic.md")
    assert any(h["kind"] == "RECORD_SHAPED_TUPLE" for h in hits)


def test_distinguishes_schema_prose_from_value_bearing_record():
    schema = "Fields: `stateN` (integer), `nextStateN` (integer or null), `jump` (integer), `direction` (\"on\"/\"off\")."
    hits = guard.scan_text(schema, source="synthetic.md")
    assert not any(h["kind"] == "RECORD_SHAPED_TUPLE" for h in hits)


def test_permits_synthetic_fixture_with_explicit_marker():
    text = "SYNTHETIC_FIXTURE: `%s` (stateN=0, nextStateN=-1, jump=-1, direction=\"off\")" % SYNTHETIC_EVENT_ID
    hits = guard.scan_text(text, source="synthetic.md")
    assert hits == []


def test_structurally_parses_json_string_values_not_only_keys():
    doc = {"note": "affected event %s in holdout" % SYNTHETIC_EVENT_ID, "eventId": "unrelated"}
    hits = guard.scan_json(doc, source="synthetic.json")
    assert any(h["kind"] == "EVENT_ID" for h in hits)


def test_inspects_or_rejects_nested_archives(tmp_path):
    inner = tmp_path / "inner.zip"
    with zipfile.ZipFile(inner, "w") as zf:
        zf.writestr("leaked.md", "event `%s` leaked" % SYNTHETIC_EVENT_ID)
    outer = tmp_path / "outer.zip"
    with zipfile.ZipFile(outer, "w") as zf:
        zf.write(inner, arcname="inner.zip")

    report = guard.scan_archive(outer)
    assert report["nestedArchivesInspected"] >= 1 or report["nestedArchivesRejected"] >= 1
    if report["nestedArchivesInspected"] >= 1:
        assert any(h["kind"] == "EVENT_ID" for h in report["findings"])


def test_fails_on_pre_redaction_example_and_mutation_variants():
    variants = [
        "`%s` (`stateN=0 -> nextStateN=-1`, `jump=-1`)" % SYNTHETIC_EVENT_ID,
        "%s: stateN=0, nextStateN=-1, jump=-1, direction=off, partition=holdout" % SYNTHETIC_EVENT_ID,
        "the pair %s and %s" % (SYNTHETIC_EVENT_ID, "99-99-99-9999:0002"),
    ]
    for v in variants:
        hits = guard.scan_text(v, source="synthetic.md")
        assert hits, "mutation variant not detected: %r" % v


def test_emits_machine_readable_report_naming_every_artifact_and_exception(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("No identifiers here.", encoding="utf-8")
    leaky = tmp_path / "leaky.md"
    leaky.write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    synth = tmp_path / "synth.md"
    synth.write_text("SYNTHETIC_FIXTURE: `%s`" % SYNTHETIC_EVENT_ID, encoding="utf-8")

    report = guard.scan_paths([tmp_path])
    assert report["artifactsInspected"] >= 3
    names = {f["file"] for f in report["findings"]}
    assert str(leaky).replace("\\", "/") in names
    assert str(clean).replace("\\", "/") not in names
    assert str(synth).replace("\\", "/") not in names
    assert report["exceptionsGranted"] and report["exceptionsGranted"][0]["reason"] == "SYNTHETIC_FIXTURE marker"


def test_release_falsifier_fails_closed_when_any_finding_survives(tmp_path):
    leaky = tmp_path / "leaky.md"
    leaky.write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    report = guard.scan_paths([tmp_path])
    assert guard.release_verdict(report) == "FAIL"


def test_release_falsifier_passes_when_nothing_survives(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("Nothing sensitive here.", encoding="utf-8")
    report = guard.scan_paths([tmp_path])
    assert guard.release_verdict(report) == "PASS"


def test_html_generated_reports_are_scanned(tmp_path):
    page = tmp_path / "page.html"
    page.write_text("<p>event <code>%s</code> leaked</p>" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    report = guard.scan_paths([tmp_path])
    assert any(h["kind"] == "EVENT_ID" for h in report["findings"])
    assert report["unscanned"] == []


def test_sha256_manifest_files_are_scanned(tmp_path):
    m = tmp_path / "MANIFEST.sha256"
    m.write_text("abc123  path/to/file\ndeadbeef  event %s note\n" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    report = guard.scan_paths([tmp_path])
    assert report["unscanned"] == []
    assert any(h["kind"] == "EVENT_ID" for h in report["findings"])


def test_unknown_suffix_is_reported_unscanned_not_assumed_clean(tmp_path):
    weird = tmp_path / "data.parquet"
    weird.write_bytes(b"binary-ish content")
    report = guard.scan_paths([tmp_path])
    assert any(u["file"].endswith("data.parquet") for u in report["unscanned"])


def test_known_binary_suffix_is_silently_skipped(tmp_path):
    img = tmp_path / "figure.png"
    img.write_bytes(b"\x89PNG\r\n")
    report = guard.scan_paths([tmp_path])
    assert report["unscanned"] == []


@pytest.mark.skipif(
    not (REPO_ROOT / "hierarchical-aif" / "reports" / "D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md").exists(),
    reason="repo layout not present")
def test_named_d12_surfaces_are_clean_after_redaction():
    """Regression gate: once D12 redaction lands, these four named surfaces must stay clean."""
    surfaces = [
        REPO_ROOT / "hierarchical-aif" / "reports" / "D6-INGEST-NEXTSTATE-RANGE-CHECK-DEFECT.md",
        REPO_ROOT / "hierarchical-aif" / "protocols" / "MARK-PROCESS-TRANSFER-RESCUE-PROTOCOL.md",
        REPO_ROOT / "hierarchical-aif" / "ledgers" / "HIERARCHICAL-AIF-DEFECT-LEDGER.md",
    ]
    report = guard.scan_paths(surfaces)
    assert report["findings"] == [], "D12 surface still carries a detectable leak: %r" % report["findings"]


# ==============================================================================================
# Phase 9 step 3.1 — F29 and F30. THE REFUSALS THAT DO NOT EXIST.
#
# MUST FAIL BEFORE THE CODE EXISTS, for this reason:
#   `release_verdict` has only two words, so "we could not look" is indistinguishable from
#   "we looked and found nothing", and both come out as PASS.
#
#   F29 | an archive cannot be opened            | report UNVERIFIED | it is treated as clean
#   F30 | files in a distribution are unscanned  | fail closed       | release_verdict returns
#                                                                      PASS with unscanned files
#
# Both are violated LIVE. `scan_archive` already writes the right words into a `note` string —
# "archive could not be opened - treated as UNVERIFIED, not clean" — and then `scan_paths` takes
# only `sub["findings"]` and throws the note away, so a distribution containing an archive nobody
# could open returns PASS. `scan_paths` has collected `unscanned` since the day it was written,
# with a docstring saying "a skipped file is NOT a clean file... a caller can fail on it", and
# `release_verdict` has never once looked at it.
#
# THE PRE-REGISTERED FALSIFIER, from phase9_plan.json step 3.1, is "a caller treats UNVERIFIED as
# truthy" — and `main()` does exactly that today: `return 1 if verdict == "FAIL" else 0`. A third
# word is worth nothing if the exit code still has two.
# ==============================================================================================


def _broken_zip(tmp_path, name="broken.zip"):
    """A file that claims to be a zip and is not. The point is that it CANNOT be opened."""
    p = tmp_path / name
    p.write_bytes(b"PK\x03\x04 this is not a real archive")
    return p


def test_f29_an_archive_that_cannot_be_opened_is_UNVERIFIED_not_clean(tmp_path):
    _broken_zip(tmp_path)
    report = guard.scan_paths([tmp_path])
    assert report["findings"] == [], "nothing can be found in an archive nobody opened"
    assert guard.release_verdict(report) == "UNVERIFIED"


def test_f29_the_archive_nobody_could_open_is_NAMED_not_merely_counted(tmp_path):
    _broken_zip(tmp_path)
    report = guard.scan_paths([tmp_path])
    assert any(u["file"].endswith("broken.zip") for u in report["unopenable"]), (
        "a coverage gap that cannot be located is not actionable: %r" % report.get("unopenable"))


def test_f29_an_unopenable_archive_NESTED_inside_a_good_one_still_reaches_the_verdict(tmp_path):
    inner = _broken_zip(tmp_path, "inner.zip")
    outer = tmp_path / "outer.zip"
    with zipfile.ZipFile(outer, "w") as zf:
        zf.write(inner, arcname="inner.zip")
    inner.unlink()

    report = guard.scan_paths([tmp_path])
    assert guard.release_verdict(report) == "UNVERIFIED", (
        "a gap one level down is still a gap: %r" % report)


def test_f30_unscanned_files_make_the_verdict_UNVERIFIED_never_PASS(tmp_path):
    (tmp_path / "data.parquet").write_bytes(b"binary-ish content")
    report = guard.scan_paths([tmp_path])
    assert report["unscanned"], "precondition: the file is recorded as unscanned"
    assert guard.release_verdict(report) == "UNVERIFIED"


def test_a_finding_still_OUTRANKS_a_coverage_gap(tmp_path):
    """FAIL beats UNVERIFIED. 'We looked and found something' is worse than 'we could not look'."""
    (tmp_path / "leaky.md").write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    _broken_zip(tmp_path)
    assert guard.release_verdict(guard.scan_paths([tmp_path])) == "FAIL"


def test_NEGATIVE_CONTROL_looked_everywhere_and_found_nothing_is_still_PASS(tmp_path):
    """UNVERIFIED must not become the new default. A guard that never says PASS gets ignored."""
    (tmp_path / "clean.md").write_text("Nothing sensitive here.", encoding="utf-8")
    (tmp_path / "figure.png").write_bytes(b"\x89PNG\r\n")  # known binary: skipped, not a gap
    report = guard.scan_paths([tmp_path])
    assert report["unscanned"] == [] and report["unopenable"] == []
    assert guard.release_verdict(report) == "PASS"


def test_THE_FALSIFIER_no_caller_may_treat_UNVERIFIED_AS_TRUTHY(tmp_path):
    """The pre-registered falsifier for step 3.1, tested on the guard's own CLI.

    `main()` is the guard's only shipped caller and its exit code is what CI reads. A third
    verdict word that still exits 0 has changed a report and refused nothing.
    """
    _broken_zip(tmp_path)
    assert guard.main([str(tmp_path)]) != 0


def test_the_cli_exits_zero_ONLY_on_PASS(tmp_path):
    clean = tmp_path / "clean"
    clean.mkdir()
    (clean / "ok.md").write_text("Nothing sensitive here.", encoding="utf-8")
    assert guard.main([str(clean)]) == 0

    leaky = tmp_path / "leaky"
    leaky.mkdir()
    (leaky / "bad.md").write_text("event `%s` leaked" % SYNTHETIC_EVENT_ID, encoding="utf-8")
    assert guard.main([str(leaky)]) != 0

    gap = tmp_path / "gap"
    gap.mkdir()
    _broken_zip(gap)
    assert guard.main([str(gap)]) != 0


def test_the_report_says_WHY_it_is_unverified_in_words_a_human_reads(tmp_path):
    """A verdict a reader cannot act on is a verdict they will learn to ignore."""
    _broken_zip(tmp_path)
    (tmp_path / "data.parquet").write_bytes(b"x")
    report = guard.scan_paths([tmp_path])
    why = guard.unverified_because(report)
    assert any("broken.zip" in w for w in why)
    assert any("data.parquet" in w for w in why)
