"""Bridge to the frozen B3/B4 runners.

Loads the committed audit runners as modules WITHOUT importing them as packages and
WITHOUT writing bytecode next to the frozen artifacts. Nothing here modifies frozen
evidence; the runners are read-only inputs to the hierarchical-aif work.

audits/phase-c/** and audits/phase-d/** are frozen and are never touched by this module.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

REPO_ROOT = Path(__file__).resolve().parents[3]
B3_RUNNER = REPO_ROOT / "audits" / "phase-b" / "b3-model-competition-runner.py"
B4_RUNNER = REPO_ROOT / "audits" / "phase-b" / "b4-identifiability-robustness-runner.py"
B3_RESULT = REPO_ROOT / "audits" / "phase-b" / "b3-model-competition-result.json"
B4_RESULT = REPO_ROOT / "audits" / "phase-b" / "b4-identifiability-robustness-result.v1.json"

_b3 = None
_b4 = None


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def b3():
    global _b3
    if _b3 is None:
        _b3 = _load("b3lib", B3_RUNNER)
    return _b3


def b4():
    global _b4
    if _b4 is None:
        _b4 = _load("b4lib", B4_RUNNER)
    return _b4


def b3_result() -> dict:
    return json.loads(B3_RESULT.read_text(encoding="utf-8"))


def b4_result() -> dict:
    return json.loads(B4_RESULT.read_text(encoding="utf-8"))


def frozen_cohort(states=tuple(range(1, 9)), name="frozen"):
    """Rebuild the derived_eligible_1_to_8 cohort exactly as the B4 runner does."""
    lib = b3()
    fresh = []
    for e in lib.load_events():
        e2 = dict(e)
        e2["partition"] = "holdout" if lib.sha256_mod5(e2["motorId"]) == 0 else "train"
        fresh.append(e2)
    return lib.Cohort(name, tuple(states), fresh)
