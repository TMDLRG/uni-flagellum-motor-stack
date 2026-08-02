"""D5 firewall — the held-out mark channel is not readable by accident, and the scoring path
cannot read it at all.

The D5 defect was NOT "someone wrote a bad model". It was "a read-only task with no declared split
boundary read ``nextStateN``/``jump`` on the holdout partition and permanently destroyed its
prospective status". Reading held-out data is irreversible; read-only is not consequence-free.

Two independent guards are asserted here:

  RUNTIME  — ``load_events`` refuses to hand back holdout mark fields in ANY mark mode unless the
             caller writes down the acknowledgement that the result is
             RETROSPECTIVE_EXPLORATORY_ON_THIS_DATASET. ``duration_only`` never returns them at
             all, even when the holdout partition is requested explicitly.
  SOURCE   — the duration scoring path (score / hierarchy / fit / hazard_survival, and compare if
             it exists) contains no reference to ``nextStateN`` / ``jump`` / ``direction``. A
             runtime guard can be bypassed by a module that reads the raw dict directly; the
             source scan is what closes that hole.

Coverage note (audit): ``test_fside_motor_stack.py`` covers the refusal, the acknowledged path,
the train-only path, and duration-only masking for ``states=1..8``. The MARK_QUARANTINE mode, the
explicit ``partition='holdout'`` duration-only case, the error message content, and the whole
SOURCE guard were not covered. The closure ledger lists this filename against D5; until now the
file did not exist.

This file itself reads no mark VALUE. It asserts on types, exceptions, and source text.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import events  # noqa: E402

PKG_DIR = SRC / "motor_stack_aif"

# Modules that make up the duration-only held-out scoring path. `compare.py` is included when it
# exists so a later comparison harness inherits the same fence.
SCORING_PATH = ["score.py", "compare.py", "hierarchy.py", "fit.py", "hazard_survival.py",
                "baselines.py", "bootstrap.py"]

RAW_MARK_KEYS = {"nextStateN", "direction", "jump"}
ATTR_MARK_NAMES = {"next_state_n", "direction", "jump"}
GETTERS = {"get", "pop", "setdefault"}


def mark_reads(source: str, label: str = "<src>"):
    """AST scan for an actual READ of the mark channel.

    USE vs MENTION. A plain string literal naming a mark field is a MENTION: ``compare.py``
    legitimately declares ``_FORBIDDEN_EVENT_FIELDS = ("nextStateN", "direction", "jump")`` as its
    own guard list, and several modules name the channel in prose to say they do not touch it.
    Banning the substring would punish the modules that document the fence most carefully. What is
    banned is a construct that would actually pull a value out:

        e["nextStateN"]            subscript with a mark key
        raw.get("jump")            dict getter with a mark key
        event.next_state_n         attribute access on a typed record
        next_state_n               a bare local bound to the channel
    """
    tree = ast.parse(source, filename=label)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant) \
                and node.slice.value in RAW_MARK_KEYS:
            hits.append((node.lineno, "subscript %r" % node.slice.value))
        elif isinstance(node, ast.Attribute) and node.attr in ATTR_MARK_NAMES:
            hits.append((node.lineno, "attribute .%s" % node.attr))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in GETTERS and node.args \
                and isinstance(node.args[0], ast.Constant) \
                and node.args[0].value in RAW_MARK_KEYS:
            hits.append((node.lineno, "%s(%r)" % (node.func.attr, node.args[0].value)))
        elif isinstance(node, ast.Name) and node.id in ("next_state_n", "nextStateN"):
            hits.append((node.lineno, "name %s" % node.id))
    return hits


# ---------------------------------------------------------------- runtime guard
@pytest.mark.parametrize("mode", [events.MARK_RETROSPECTIVE, events.MARK_QUARANTINE])
def test_every_mark_mode_refuses_holdout_without_acknowledgement(mode):
    with pytest.raises(events.HoldoutMarkAccessError):
        events.load_events(mode=mode, states=range(1, 9))


@pytest.mark.parametrize("mode", [events.MARK_RETROSPECTIVE, events.MARK_QUARANTINE])
def test_every_mark_mode_refuses_an_explicit_holdout_partition(mode):
    with pytest.raises(events.HoldoutMarkAccessError):
        events.load_events(mode=mode, states=range(1, 9), partition="holdout")


def test_the_refusal_message_records_the_irreversibility():
    with pytest.raises(events.HoldoutMarkAccessError) as exc:
        events.load_events(mode=events.MARK_RETROSPECTIVE)
    msg = str(exc.value)
    assert "RETROSPECTIVE_EXPLORATORY_ON_" in msg
    assert "never be PROSPECTIVE" in msg or "can never be" in msg
    assert "duration_only" in msg, "the message must name the safe path"


@pytest.mark.parametrize("mode", [events.MARK_RETROSPECTIVE, events.MARK_QUARANTINE])
def test_train_partition_mark_access_is_permitted(mode):
    ev = events.load_events(mode=mode, states=range(1, 9), partition="train")
    assert ev
    assert all(e.partition == "train" for e in ev)
    assert not any(e.is_holdout for e in ev)


def test_duration_only_masks_marks_even_when_holdout_is_requested_explicitly():
    """The strongest form of the guard: asking for the holdout partition by name still yields no
    mark field, so there is no accidental route to the burned channel."""
    ev = events.load_events(mode=events.DURATION_ONLY, partition="holdout")
    assert ev and all(e.is_holdout for e in ev)
    assert all(e.next_state_n is None and e.jump is None and e.direction is None for e in ev)
    assert not any(e.has_mark for e in ev)


def test_duration_only_is_the_default_mode():
    """If the default were a mark mode, an unqualified call would spend the channel."""
    import inspect
    default = inspect.signature(events.load_events).parameters["mode"].default
    assert default == events.DURATION_ONLY


def test_the_acknowledgement_flag_is_keyword_only():
    """It must not be possible to acknowledge D5 by positional accident."""
    import inspect
    p = inspect.signature(events.load_events).parameters["acknowledge_retrospective_holdout_marks"]
    assert p.kind is inspect.Parameter.KEYWORD_ONLY
    assert p.default is False


def test_an_unknown_mode_is_refused_rather_than_defaulting():
    with pytest.raises(ValueError):
        events.load_events(mode="marks_please")


# ---------------------------------------------------------------- source guard
@pytest.mark.parametrize("fname", SCORING_PATH)
def test_the_duration_scoring_path_never_reads_the_mark_channel(fname):
    p = PKG_DIR / fname
    if not p.exists():
        pytest.skip("%s does not exist in this tree" % fname)
    hits = mark_reads(p.read_text(encoding="utf-8"), fname)
    assert not hits, "mark-channel READ in the duration scoring path %s: %r" % (fname, hits)


def test_the_scoring_path_files_actually_exist():
    """NON-VACUITY guard #1: if every file were missing, the scan above would skip silently."""
    present = [f for f in SCORING_PATH if (PKG_DIR / f).exists()]
    assert len(present) >= 6, "expected the scoring path to be present, found %r" % present


@pytest.mark.parametrize("offending", [
    'y = e["nextStateN"]',
    "ns = raw.get('nextStateN')",
    "d = event.jump",
    "if event.direction == 'CW':\n    pass",
    "next_state_n = 3",
    "vals = [row['jump'] for row in rows]",
])
def test_the_mark_read_detector_catches_every_read_form(offending):
    """NON-VACUITY guard #2a: each realistic way of pulling the channel out must be detected."""
    assert mark_reads(offending), offending


@pytest.mark.parametrize("innocent", [
    '# duration-only: this module never touches mark fields (nextStateN/jump/direction)',
    '_FORBIDDEN_EVENT_FIELDS = ("nextStateN", "direction", "jump")',
    '"""Never read nextStateN or jump on the holdout partition."""',
    'note = "nothing about the MARK process (nextStateN/direction/jump) - not read here"',
    "y = e['durationS']",
    "jumps_in_logic = 0",
])
def test_the_mark_read_detector_permits_mention_without_use(innocent):
    """NON-VACUITY guard #2b: USE vs MENTION. Declaring the channel's name in a guard list or a
    disclaimer is not a read, and must not be punished — otherwise the modules that document the
    fence most explicitly would be the ones that fail."""
    assert not mark_reads(innocent), innocent


def test_only_the_declared_gate_modules_read_the_mark_channel():
    """Any module that READS a mark field must be one of the declared mark-handling modules.
    A new file quietly reading `nextStateN` is exactly the D5 failure mode repeating."""
    allowed = {"events.py", "marks.py"}
    offenders = {}
    for p in sorted(PKG_DIR.glob("*.py")):
        if p.name in allowed:
            continue
        hits = mark_reads(p.read_text(encoding="utf-8"), p.name)
        if hits:
            offenders[p.name] = hits
    assert not offenders, (
        "mark-channel reads outside the declared gate modules %r: %r" % (allowed, offenders))


def test_the_declared_gate_modules_really_are_where_the_reads_live():
    """NON-VACUITY guard #3: if NO module read the channel, the scan above would be trivially
    satisfied. The gate modules must actually contain reads, so the exclusion is meaningful."""
    for name in ("events.py", "marks.py"):
        assert mark_reads((PKG_DIR / name).read_text(encoding="utf-8"), name), name
