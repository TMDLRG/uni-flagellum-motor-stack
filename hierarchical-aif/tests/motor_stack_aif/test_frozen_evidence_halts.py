"""Phase 9 step 3.2 — F28: frozen evidence hashes drift, and everything halts.

MUST FAIL BEFORE THE CODE EXISTS, for this reason:
  there is NO checker. `hierarchical-aif/reports/frozen-evidence-baseline.sha256` pins 250 files
  under `audits/phase-c/**` and `audits/phase-d/**`, and nothing in this repository ever compares
  them. A human running `sha256sum -c` by hand is not a refusal; it is a habit.

    F28 | frozen evidence hashes drift | STOP_FROZEN_EVIDENCE_DRIFT, halt everything
        | falsifier: work continues past a drift

TWO DIRECTIONS, AND ONLY ONE OF THEM IS FREE
--------------------------------------------
`sha256sum -c` catches a CHANGED file and a MISSING one. It cannot catch an ADDED one: a new file
dropped into the frozen tree is invisible to a manifest that never names it. Frozen means frozen
in both directions, so the guard derives the frozen roots from the baseline itself and requires
that nothing lives under them that the baseline does not name.

THE PRE-REGISTERED FALSIFIER FOR THIS STEP IS ABOUT THE PROOF, NOT THE CODE
---------------------------------------------------------------------------
phase9_plan.json step 3.2 names it: **"the real frozen tree is mutated."** Proving a drift guard
bites means causing a drift, and the one place a drift must never be caused is the tree under
test. `audits/**` is S3 — "any write to a frozen artifact" is a STOP. So EVERY mutation here runs
on a `shutil.copytree` copy in a temp directory, and the last test in this file re-verifies the
real tree afterwards, so the falsifier is not merely avoided but actively checked.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import frozen_evidence_guard as fez  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
BASELINE = REPO_ROOT / "hierarchical-aif" / "reports" / "frozen-evidence-baseline.sha256"


def _copy_frozen_world(tmp_path):
    """A disposable copy of the frozen tree and its baseline. The real one is never touched."""
    root = tmp_path / "repo"
    root.mkdir()
    for r in fez.frozen_roots(BASELINE):
        shutil.copytree(REPO_ROOT / r, root / r)
    baseline = tmp_path / "baseline.sha256"
    shutil.copyfile(BASELINE, baseline)
    return baseline, root


# ---- the real tree, read only ----------------------------------------------------------------


def test_the_real_frozen_tree_verifies_against_its_own_baseline():
    report = fez.verify(BASELINE, REPO_ROOT)
    assert report["checked"] == 250
    assert report["ok"], fez.account(report)


def test_the_frozen_roots_are_derived_from_the_baseline_not_configured_separately():
    """A guard whose scope is configured elsewhere can be narrowed by editing the elsewhere."""
    roots = fez.frozen_roots(BASELINE)
    assert roots == ["audits/phase-c", "audits/phase-d"]
    for r in roots:
        assert (REPO_ROOT / r).is_dir()


# ---- M1 mutation, ON A COPY, one route per test ------------------------------------------------


def test_MUTATION_a_changed_byte_is_caught(tmp_path):
    baseline, root = _copy_frozen_world(tmp_path)
    victim = next(p for p in (root / "audits" / "phase-c").rglob("*") if p.is_file())
    victim.write_bytes(victim.read_bytes() + b"\n")

    report = fez.verify(baseline, root)
    assert not report["ok"]
    assert any(victim.name in c["file"] for c in report["changed"])


def test_MUTATION_a_deleted_file_is_caught(tmp_path):
    baseline, root = _copy_frozen_world(tmp_path)
    victim = next(p for p in (root / "audits" / "phase-d").rglob("*") if p.is_file())
    name = victim.name
    victim.unlink()

    report = fez.verify(baseline, root)
    assert not report["ok"]
    assert any(name in m for m in report["missing"])


def test_MUTATION_an_ADDED_file_is_caught_which_sha256sum_c_alone_cannot_do(tmp_path):
    """The direction a manifest check misses for free. Frozen means frozen both ways."""
    baseline, root = _copy_frozen_world(tmp_path)
    (root / "audits" / "phase-c" / "helpful-addition.md").write_text("just a note", encoding="utf-8")

    report = fez.verify(baseline, root)
    assert not report["ok"]
    assert any("helpful-addition.md" in u for u in report["unlisted"])


def test_MUTATION_a_drifted_tree_HALTS_rather_than_returning_a_value(tmp_path):
    baseline, root = _copy_frozen_world(tmp_path)
    victim = next(p for p in (root / "audits" / "phase-c").rglob("*") if p.is_file())
    victim.write_bytes(b"replaced")

    with pytest.raises(fez.FrozenEvidenceDrift) as exc:
        fez.halt_if_drifted(baseline, root)
    assert fez.STOP in str(exc.value)
    assert victim.name in str(exc.value), "a halt that does not name the file is not actionable"


def test_NEGATIVE_CONTROL_an_untouched_copy_verifies_and_does_not_halt(tmp_path):
    """A guard that fires on a faithful copy would be untrustworthy in the other direction."""
    baseline, root = _copy_frozen_world(tmp_path)
    assert fez.verify(baseline, root)["ok"]
    fez.halt_if_drifted(baseline, root)  # must not raise


# ---- the wiring: work must not CONTINUE past a drift -------------------------------------------


def test_the_test_session_ITSELF_refuses_to_run_past_a_drift(monkeypatch):
    """F28 says 'halt everything', so the suite is the thing that has to stop.

    The detection is proved above on copies. This proves the WIRING: given a drifted report,
    the session hook exits rather than letting the run continue.
    """
    conftest = pytest.importorskip("conftest")
    monkeypatch.setattr(fez, "verify", lambda *_a, **_k: {
        "ok": False, "checked": 250,
        "changed": [{"file": "audits/phase-c/x.json", "baseline": "a" * 64, "actual": "b" * 64}],
        "missing": [], "unlisted": [],
    })
    with pytest.raises(pytest.exit.Exception) as exc:
        conftest.pytest_sessionstart(session=None)
    assert fez.STOP in str(exc.value) and "audits/phase-c/x.json" in str(exc.value)


def test_the_halt_message_survives_a_PARTIAL_report_rather_than_raising(monkeypatch):
    """A reporter that raises while explaining a drift turns a legible stop into a stack trace."""
    partial = {"ok": False, "checked": 250, "changed": [{"file": "audits/phase-c/x.json"}]}
    text = fez.account(partial)
    assert fez.STOP in text and "audits/phase-c/x.json" in text


def test_the_session_hook_is_wired_to_the_REAL_baseline_not_a_parameter():
    """A halt pointed at a tree of its own choosing halts nothing."""
    source = (REPO_ROOT / "hierarchical-aif" / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "frozen-evidence-baseline.sha256" in source
    assert "pytest_sessionstart" in source


# ---- THE PRE-REGISTERED FALSIFIER, checked rather than assumed ---------------------------------


def test_THE_FALSIFIER_the_real_frozen_tree_was_never_mutated_by_any_of_the_above():
    """Runs last by name and by intent. Every mutation above ran on a copy; prove it."""
    report = fez.verify(BASELINE, REPO_ROOT)
    assert report["ok"] and report["checked"] == 250, (
        "THE FALSIFIER FIRED: proving the drift guard bites has drifted the real frozen tree. "
        + fez.account(report))
