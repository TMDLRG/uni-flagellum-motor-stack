"""D9 — a document may not assert prospectivity that the commit graph does not support.

`CLAUDE.md`:
    "A prediction is prospective only if it was committed before its observation."
    "Prospectivity is decided by the commit graph, not by prose. Flip a prediction record
     PENDING -> PROSPECTIVE only in the result commit, after the prediction commit is a proven
     strict ancestor of the result's introduction."

The failure this guards against is subtle and already happened (D9): a report asserted
"**Prediction record (committed before execution)**" as a bare fact. It was not. The prediction
record entered the repository 2 h 33 min AFTER the run it predicts had finished. No number was
wrong; the epistemic GRADE attached to the numbers was.

Two things are checked here, and the second is the one with teeth:

  1. WORDING — no hierarchical-aif document asserts "committed before execution" (or labels a
     result PROSPECTIVE) without an adjacent negation or qualification.
  2. COMMIT GRAPH — the actual ancestry test, run against git, for the prediction/result pairs
     produced this session. This pins the known-NOT_SATISFIED state so that a future edit which
     quietly re-asserts prospectivity goes red.

WHY THE MECHANICAL ANCESTRY TEST IS NOT SUFFICIENT ON ITS OWN
-------------------------------------------------------------
For B4C10 the prediction and the result were introduced by the SAME commit (`b9b5670`), so
strict-ancestor status is structurally unattainable there — a commit cannot be its own strict
ancestor. But for a pair where the result is still uncommitted, committing the prediction NOW
would make it a strict ancestor of the result's later introduction, satisfying a naive ancestry
check while still failing the substantive requirement, because the prediction would have been
committed after the observation already existed on disk. So `prospectivity_verdict` below compares
the prediction's COMMIT TIME against the result's OBSERVATION TIME (its mtime), not merely against
ancestry. Ancestry is necessary, not sufficient.

D5 declaration: no data is loaded; this reads governance documents and git metadata.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
HAIF = REPO / "hierarchical-aif"

SCAN_DIRS = ["reports", "protocols", "docs", "ledgers"]

# An assertion of prospectivity. Matched case-insensitively.
# Regexes, not literals: the original D9 wording was caught, but a near-miss phrasing
# ("committed BEFORE this run") slipped past a literal list. Allow a short filler between
# "committed before" and the noun.
PROSPECTIVITY_ASSERTIONS = [
    r"committed\s+(?:before|prior\s+to)\s+(?:\w+\s+){0,2}(?:execution|run|the\s+run|observation)",
]

# Cues that the surrounding line is DENYING, qualifying, or cataloguing the assertion rather than
# making it. Same-line only, deliberately: a qualification three lines away does not travel with a
# quoted sentence, and that is exactly how the D9 wording slipped through.
QUALIFIER_CUES = [
    "not ", "never", "no ", "cannot", "can not", "must", "would", "unless", "rather than",
    "instead of", "forbidden", "may not", "does not", "is not", "was not", "were not",
    "not_satisfied", "not_established", "not_verified", "withdrawn", "falsif", "wrongly",
    "asserted", "claimed", "earlier draft", "replace", "d9", "quarantin", "only if",
]


def _git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=False).stdout.strip()


def _is_tracked(rel: str) -> bool:
    r = subprocess.run(["git", "-C", str(REPO), "ls-files", "--error-unmatch", rel],
                       capture_output=True, text=True, check=False)
    return r.returncode == 0


def _introducing_commit_iso(rel: str):
    """UTC ISO time of the commit that introduced `rel`, or None if untracked/uncommitted."""
    if not _is_tracked(rel):
        return None
    out = _git("log", "--diff-filter=A", "--format=%cI", "--", rel)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return lines[-1] if lines else None


def prospectivity_verdict(prediction_rel: str, observation_epoch: float | None):
    """SATISFIED only if the prediction was COMMITTED strictly before the observation existed.

    observation_epoch: mtime of the result artifact, or None if the result does not exist yet.
    """
    committed = _introducing_commit_iso(prediction_rel)
    if committed is None:
        return "NOT_SATISFIED_PREDICTION_NOT_COMMITTED"
    if observation_epoch is None:
        return "PENDING_NO_OBSERVATION_YET"
    import datetime as _dt
    ct = _dt.datetime.fromisoformat(committed).timestamp()
    return "SATISFIED" if ct < observation_epoch else "NOT_SATISFIED_COMMITTED_AFTER_OBSERVATION"


def _docs():
    out = []
    for d in SCAN_DIRS:
        root = HAIF / d
        if root.exists():
            out.extend(sorted(root.rglob("*.md")))
    return out


# ---------------------------------------------------------------- 1. wording
def test_there_are_documents_to_scan():
    """NON-VACUITY: the wording tests below are worthless if the scan finds nothing."""
    docs = _docs()
    assert len(docs) >= 10, "expected a substantial document set, found %d" % len(docs)


@pytest.mark.parametrize("doc", _docs(), ids=lambda p: p.name)
def test_no_document_asserts_prospectivity_without_qualification(doc):
    text = doc.read_text(encoding="utf-8", errors="replace")
    offenders = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        low = line.lower()
        for phrase in PROSPECTIVITY_ASSERTIONS:
            if re.search(phrase, low) and not any(cue in low for cue in QUALIFIER_CUES):
                offenders.append((line_no, phrase, line.strip()[:150]))
    assert not offenders, (
        "%s asserts prospectivity with no same-line qualification: %r\n"
        "Per CLAUDE.md prospectivity is decided by the commit graph, not by prose (D9)."
        % (doc.name, offenders))


def test_the_wording_scanner_actually_catches_a_bare_assertion():
    """NON-VACUITY: a test that cannot fail is not evidence."""
    bare = "**Prediction record (committed before execution):** foo.md"
    low = bare.lower()
    hit = any(re.search(p, low) for p in PROSPECTIVITY_ASSERTIONS)
    qualified = any(cue in low for cue in QUALIFIER_CUES)
    assert hit and not qualified, "the scanner would not have caught the original D9 wording"

    fixed = ("**Prediction record (WRITTEN before execution; NOT committed before execution "
             "— prospectivity NOT_SATISFIED):** foo.md")
    assert any(cue in fixed.lower() for cue in QUALIFIER_CUES), (
        "the corrected wording is not recognised as qualified")

    # REGRESSION: a literal-substring scanner missed this phrasing and it reached a report.
    near_miss = "**Prediction record (committed BEFORE this run):** foo.md"
    assert any(re.search(p, near_miss.lower()) for p in PROSPECTIVITY_ASSERTIONS), (
        "the scanner must catch 'committed BEFORE this run', which a literal list missed")


# ---------------------------------------------------------------- 2. the commit graph itself
def test_git_is_available_so_the_ancestry_checks_below_are_real():
    """NON-VACUITY guard: if git were missing every ancestry test would silently pass."""
    assert _git("rev-parse", "--is-inside-work-tree") == "true", "not a git work tree"
    assert _git("rev-parse", "HEAD"), "no HEAD"


def test_b4c10_prospectivity_is_not_satisfied_and_is_pinned_as_such():
    """PINS THE D9 FINDING. B4C10's prediction record was committed AFTER the run finished.

    If this ever starts returning SATISFIED, either history was rewritten or the artifact was
    replaced — both of which must be investigated, not accepted.
    """
    pred = "hierarchical-aif/protocols/B4C10-CORRECTED-FULL-PREDICTION.md"
    result = REPO / "hierarchical-aif/results/motor_stack_aif/B4C10_CORRECTED_FULL_RESULT.json"
    assert _is_tracked(pred), "the B4C10 prediction record is expected to be tracked"
    assert result.exists(), "the B4C10 result is expected to exist on disk"

    verdict = prospectivity_verdict(pred, result.stat().st_mtime)
    assert verdict == "NOT_SATISFIED_COMMITTED_AFTER_OBSERVATION", (
        "B4C10 prospectivity verdict changed to %r. D9 records that the prediction record entered "
        "the repo at 2026-07-21T22:44:31Z while the result existed from ~20:11:51Z. This result "
        "may never be labelled PROSPECTIVE." % verdict)


@pytest.mark.parametrize("pred_rel", [
    "hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md",
    "hierarchical-aif/protocols/F-SIDE-MOTOR-STACK-SCORING-PREDICTION.md",
])
def test_uncommitted_prediction_records_cannot_support_a_prospective_label(pred_rel):
    """These were written before their runs but never committed, so prospectivity fails at step 1.

    This test does NOT demand they be committed — committing them now would not make them
    prospective. It demands only that nothing claims prospectivity while they are uncommitted.
    """
    if _is_tracked(pred_rel):
        pytest.skip("%s is now tracked; re-grade its prospectivity deliberately, per D9" % pred_rel)
    assert prospectivity_verdict(pred_rel, 0.0) == "NOT_SATISFIED_PREDICTION_NOT_COMMITTED"


def test_b4c11_prediction_was_committed_before_its_observation():
    """B4C11 is the cell where the D9 window was still open, and it was taken.

    The prediction record was committed in `897c8ab` at 2026-07-22T03:23:14Z, while the run
    (PID 26756, launched 2026-07-22T01:40:03Z) was at 210/2000 replicates and NO result file
    existed. This test pins that ordering permanently:

      - before the result lands  -> PENDING_NO_OBSERVATION_YET
      - after  the result lands  -> SATISFIED (the commit strictly precedes the observation)

    It must NEVER return NOT_SATISFIED_COMMITTED_AFTER_OBSERVATION. If it ever does, either the
    result file was back-dated or history was rewritten - both are hard stops, not test updates.

    Contrast B4C10, where prediction and result share one commit and prospectivity is
    structurally unattainable. That contrast is the whole point of D9.
    """
    pred = "hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md"
    result = REPO / "hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_RESULT.json"

    assert _is_tracked(pred), (
        "the B4C11 prediction record must remain committed; uncommitting it would destroy the "
        "only prospective cell in this batch")

    committed = _introducing_commit_iso(pred)
    assert committed is not None

    # The prediction must NOT share a commit with its result - the B4C10 failure mode.
    if _is_tracked("hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_RESULT.json"):
        pred_commit = _git("log", "--diff-filter=A", "--format=%H", "--", pred).splitlines()[-1]
        res_commit = _git("log", "--diff-filter=A", "--format=%H", "--",
                          "hierarchical-aif/results/motor_stack_aif/"
                          "B4C11_CORRECTED_FULL_RESULT.json").splitlines()[-1]
        assert pred_commit != res_commit, (
            "B4C11 prediction and result were introduced by the SAME commit - the exact B4C10 "
            "failure mode (D9). Strict ancestry is then structurally unattainable.")

    verdict = prospectivity_verdict(pred, result.stat().st_mtime if result.exists() else None)
    assert verdict in ("PENDING_NO_OBSERVATION_YET", "SATISFIED"), (
        "B4C11 prospectivity verdict is %r. It was committed before its observation existed; "
        "anything else means the artifact or the history changed." % verdict)


def test_b4c01_prediction_was_committed_before_any_observation():
    """B4C01 is the cleanest prospective cell in the batch: committed with ZERO observations.

    Unlike B4C02 (committed mid-run) and B4C11 (committed at 210/2000 replicates), B4C01 had
    never been executed at any N when its prediction record was committed in `28ce738` — the
    frozen artifact records status=NOT_RUN, actual_N=0, and no result, checkpoint, or smoke-test
    artifact for this cell existed anywhere.

    This test pins that and keeps pinning it:
      - before the result lands -> PENDING_NO_OBSERVATION_YET
      - after  it lands         -> SATISFIED
    It must NEVER read NOT_SATISFIED_*. If it does, either the record was uncommitted or an
    observation predates the commit — both are hard stops, not test updates.
    """
    pred = "hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md"
    result = REPO / "hierarchical-aif/results/motor_stack_aif/B4C01_CORRECTED_FULL_RESULT.json"

    assert _is_tracked(pred), (
        "the B4C01 prediction record must remain committed; uncommitting it would destroy the "
        "cleanest prospective standing in the batch")

    # It must not share a commit with its result - the B4C10 failure mode (D9).
    res_rel = "hierarchical-aif/results/motor_stack_aif/B4C01_CORRECTED_FULL_RESULT.json"
    if _is_tracked(res_rel):
        pred_commit = _git("log", "--diff-filter=A", "--format=%H", "--", pred).splitlines()[-1]
        res_commit = _git("log", "--diff-filter=A", "--format=%H", "--", res_rel).splitlines()[-1]
        assert pred_commit != res_commit, (
            "B4C01 prediction and result were introduced by the SAME commit - the B4C10 failure "
            "mode. Strict ancestry is then structurally unattainable (D9).")

    verdict = prospectivity_verdict(pred, result.stat().st_mtime if result.exists() else None)
    assert verdict in ("PENDING_NO_OBSERVATION_YET", "SATISFIED"), (
        "B4C01 prospectivity verdict is %r; it was committed before any observation existed."
        % verdict)


def test_d9_is_recorded_in_the_closure_ledger_as_not_retroactively_repairable():
    """The defect must stay routed and must not quietly acquire a repaired status."""
    ledger = (HAIF / "ledgers" / "HIERARCHICAL-AIF-DEFECT-CLOSURE-LEDGER.md").read_text(
        encoding="utf-8")
    assert "D9_PROSPECTIVITY_NOT_ESTABLISHED_BY_COMMIT_GRAPH" in ledger
    assert "NOT_RETROACTIVELY_REPAIRABLE" in ledger.upper(), (
        "D9 must remain marked as not retroactively repairable; a rerun cannot fix a label")
    # The mitigating receipt must stay visible AND stay labelled as weaker than a commit.
    assert "5d0a1170" in ledger, (
        "the B4C11 launch-time prediction sha256 receipt should remain recorded")


def test_the_b4c11_launcher_recorded_the_prediction_hash_before_the_run():
    """The one genuine mitigating receipt: the C11 ENV pins the prediction's bytes at launch.

    Weaker than a commit because it is self-attested by the same process that ran the cell - but
    it is real, and it must not silently disappear.
    """
    env = REPO / "hierarchical-aif/results/motor_stack_aif/B4C11_CORRECTED_FULL_ENV.txt"
    if not env.exists():
        pytest.skip("B4C11 has not been launched in this working tree")
    text = env.read_text(encoding="utf-8", errors="replace")
    assert "predictionRecord=" in text
    assert "started_utc=" in text
    m = re.search(r"predictionRecord=.*?sha256\s+([0-9a-f]{64})", text)
    assert m, "the C11 ENV must record the prediction record's sha256"
