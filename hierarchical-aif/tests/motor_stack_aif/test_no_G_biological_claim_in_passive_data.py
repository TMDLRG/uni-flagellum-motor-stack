"""The G-side fence: no expected free energy, no policies, no action set — and the RECORDED
REASON is STRUCTURAL, not sample-size-limited.

Coverage note (audit): ``test_fside_motor_stack.py::test_no_expected_free_energy_function_exists``
checks four banned attribute names on the ``free_energy`` MODULE only. This file extends that to
(a) every module in the package, (b) a source-level scan so a G-side symbol cannot be introduced
in any file, and (c) the recorded reason itself — because the dangerous failure mode is not
"someone adds an EFE function", it is "someone re-labels the absence as an underpowering that
more data would fix". More data would not fix it. The dataset is passive; the action set is
empty. That is structural.

Distinction being protected: the F-side objective is a fitting objective over recorded
observations. G-side biological policy selection would be a claim that the MOTOR selects actions
to minimise expected free energy. Nothing in a passive dwell-time dataset can test that.
"""
from __future__ import annotations

import ast
import dataclasses
import importlib
import pkgutil
import re
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
REPO = Path(__file__).resolve().parents[3]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import motor_stack_aif  # noqa: E402
from motor_stack_aif import events, free_energy  # noqa: E402

PKG_DIR = SRC / "motor_stack_aif"

# Identifier-shaped G-side symbols. Deliberately identifier-shaped, not prose words: the ruling
# document must remain free to DISCUSS policies and G in prose (use vs mention). What is banned
# is a callable/attribute that would let a G quantity actually be computed and reported.
BANNED_IDENTIFIERS = (
    "expected_free_energy",
    "expected_fe",
    "policy_posterior",
    "policy_prior",
    "select_policy",
    "policy_selection",
    "epistemic_value",
    "pragmatic_value",
    "instrumental_value",
    "action_set",
    "action_space",
    "G_motor",
    "g_motor",
)
BANNED_RE = re.compile("|".join(re.escape(t) for t in BANNED_IDENTIFIERS))

# Action-like observation fields. Their absence is what makes the action set empty.
ACTION_FIELD_TOKENS = ("action", "intervention", "perturbation", "stimulus", "control_input")


def _package_sources():
    return sorted(PKG_DIR.glob("*.py"))


def g_side_identifiers(source: str, label: str = "<src>"):
    """AST scan for a G-side IDENTIFIER — a name that could actually compute or return a G value.

    USE vs MENTION, exactly as ``claim_guard`` treats claim wording. Prose and string literals may
    say ``expected_free_energy does not exist and must not`` — that sentence is the fence being
    documented, and banning the substring would fail the modules that state the boundary most
    clearly. What is banned is a binding: a def, a class, an attribute, a parameter, an import, or
    a variable by that name.
    """
    tree = ast.parse(source, filename=label)
    hits = []

    def flag(name, node):
        if name and BANNED_RE.search(name):
            hits.append((getattr(node, "lineno", 0), name))

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            flag(node.name, node)
        elif isinstance(node, ast.Name):
            flag(node.id, node)
        elif isinstance(node, ast.Attribute):
            flag(node.attr, node)
        elif isinstance(node, ast.arg):
            flag(node.arg, node)
        elif isinstance(node, ast.keyword):
            flag(node.arg, node)
        elif isinstance(node, ast.alias):
            flag(node.name, node)
            flag(node.asname, node)
    return hits


def _all_modules():
    mods = []
    for m in pkgutil.iter_modules([str(PKG_DIR)]):
        mods.append(importlib.import_module("motor_stack_aif." + m.name))
    return mods


# ---------------------------------------------------------------- source-level fence
def test_no_G_side_identifier_appears_anywhere_in_the_package_source():
    hits = {}
    for p in _package_sources():
        found = g_side_identifiers(p.read_text(encoding="utf-8"), p.name)
        if found:
            hits[p.name] = found
    assert not hits, "G-side identifiers bound in a passive-data package: %r" % hits


@pytest.mark.parametrize("planted", [
    "def expected_free_energy(policies):\n    return 0.0\n",
    "G_motor = 1.0\n",
    "from elsewhere import policy_posterior\n",
    "value = agent.epistemic_value\n",
    "run(action_set=[1, 2])\n",
])
def test_the_identifier_scanner_fires_on_a_planted_G_symbol(planted):
    """NON-VACUITY. Each way of introducing a G quantity must be detected."""
    assert g_side_identifiers(planted), planted


@pytest.mark.parametrize("mention", [
    '"""There is deliberately NO expected-free-energy function in this module."""',
    'note = "no G-side policy claim; expected_free_energy does not exist and must not"',
    "# G_motor is DESIGN_ONLY_UNTIL_INTERVENTION\n",
])
def test_the_identifier_scanner_permits_mention_without_use(mention):
    """USE vs MENTION. Documenting the fence is not breaching it."""
    assert not g_side_identifiers(mention), mention


def test_the_scanner_saw_a_real_package():
    assert len(_package_sources()) >= 10, "scanner scanned suspiciously few files"


def test_no_module_in_the_package_exposes_a_G_side_attribute():
    bad = []
    for mod in _all_modules():
        for name in dir(mod):
            if BANNED_RE.search(name):
                bad.append("%s.%s" % (mod.__name__, name))
    assert not bad, bad


def test_the_package_namespace_itself_is_clean():
    for name in BANNED_IDENTIFIERS:
        assert not hasattr(motor_stack_aif, name)
        assert not hasattr(free_energy, name)


# ---------------------------------------------------------------- the action set is empty
def test_the_observation_schema_declares_no_action_field():
    """STRUCTURAL evidence, not an opinion: an ObservedEvent records a dwell, its state, and its
    censoring. There is no field an agent could have acted on, so no policy can be defined."""
    fields = {f.name for f in dataclasses.fields(events.ObservedEvent)}
    for tok in ACTION_FIELD_TOKENS:
        assert not any(tok in f for f in fields), "%r-like field present: %r" % (tok, fields)
    assert fields == {"event_id", "motor_id", "partition", "state_n", "duration_s",
                      "right_censored", "next_state_n", "direction", "jump", "meta"}


def test_no_package_source_reads_an_action_channel():
    hits = []
    for p in _package_sources():
        text = p.read_text(encoding="utf-8")
        for tok in ("\"action\"", "'action'", "\"intervention\"", "'intervention'",
                    "\"perturbation\"", "'perturbation'"):
            if tok in text:
                hits.append("%s: %s" % (p.name, tok))
    assert not hits, hits


# ---------------------------------------------------------------- the recorded reason
def _ruling_text():
    p = REPO / "hierarchical-aif" / "docs" / "MOTOR-STACK-AIF-SCOPE-RULING.md"
    assert p.exists(), "the scope ruling that records the reason is missing: %s" % p
    return p.read_text(encoding="utf-8")


def test_the_recorded_reason_is_structural_not_sample_size_limited():
    """This is the assertion that stops the fence being re-labelled. 'We lack power' invites
    'collect more dwell times'. 'The action set is empty' does not."""
    text = _ruling_text().lower()
    assert "structural, not sample-size-limited" in text
    assert "the action set is empty" in text


def test_the_governing_contract_records_the_same_structural_reason():
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8").lower()
    assert "the action set is empty, which is structural, not sample-size-limited" in text


def test_the_G_side_classification_is_design_only_until_intervention():
    text = _ruling_text()
    assert "DESIGN_ONLY_UNTIL_INTERVENTION" in text


def test_the_F_side_module_states_why_G_is_absent():
    # whitespace-normalised: the reason must survive a reflow of the docstring
    doc = " ".join((free_energy.__doc__ or "").split())
    assert "NO expected-free-energy function" in doc
    assert "this dataset has none" in doc
    assert "absence of the function is the fence" in doc


@pytest.mark.parametrize("phrase", [
    "underpowered",
    "not enough data",
    "insufficient sample",
    "more motors would",
])
def test_the_reason_is_not_attributed_to_sample_size(phrase):
    """NEGATIVE CONTROL on the wording: if the ruling ever explains G's absence by sample size,
    the structural fence has been quietly converted into a fixable shortfall."""
    ruling = _ruling_text().lower()
    idx = ruling.find(phrase)
    if idx == -1:
        return
    window = ruling[max(0, idx - 300): idx + 300]
    assert "structural" in window, (
        "%r appears near the G-side reason without the structural qualifier" % phrase)
