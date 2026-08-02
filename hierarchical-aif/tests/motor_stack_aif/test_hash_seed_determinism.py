"""D3 reproducer — seeds must be identical across processes.

RED BEFORE FIX: `legacy_seed` uses `hash(str)`, which CPython randomizes per process.
GREEN AFTER FIX: `stable_seed` is SHA-256 derived and process-invariant.
"""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "hierarchical-aif" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from motor_stack_aif import seeding  # noqa: E402

GENERATORS = ["WEIBULL_GAMMA_BLEND", "THREE_TIMESCALE", "PER_MOTOR_HETEROGENEOUS_WEIBULL"]


def _run_in_subprocess(expr: str, hashseed: str) -> str:
    code = (
        "import sys; sys.path.insert(0, r'%s');\n"
        "from motor_stack_aif import seeding;\n"
        "print(%s)" % (str(SRC), expr)
    )
    out = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True,
        env={"PYTHONHASHSEED": hashseed, "PATH": "", "SYSTEMROOT": "C:\\Windows"},
    )
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def test_stable_seed_is_identical_across_processes_and_hashseeds():
    expr = ("seeding.stable_seed(cell_id='B4C02', base_seed=20260802, replicate_index=7,"
            " protocol_version='PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1',"
            " cohort_id='derived_eligible_1_to_8')")
    results = {_run_in_subprocess(expr, hs) for hs in ("0", "1", "12345", "random")}
    assert len(results) == 1, (
        "stable_seed must not vary with PYTHONHASHSEED or process; got %r" % results
    )


def test_stable_seed_is_deterministic_in_process():
    kw = dict(cell_id="B4C01", base_seed=20260801, replicate_index=3,
              protocol_version="V1", cohort_id="c")
    assert seeding.stable_seed(**kw) == seeding.stable_seed(**kw)


def test_stable_seed_separates_distinct_inputs():
    base = dict(cell_id="B4C01", base_seed=20260801, replicate_index=0,
                protocol_version="V1", cohort_id="c")
    seeds = set()
    for gen_idx in range(len(GENERATORS)):
        for rep in range(5):
            kw = dict(base)
            kw["replicate_index"] = rep
            kw["cell_id"] = "B4C01::%s" % GENERATORS[gen_idx]
            seeds.add(seeding.stable_seed(**kw))
    assert len(seeds) == len(GENERATORS) * 5, "distinct protocol inputs must give distinct seeds"


def test_legacy_seed_demonstrates_the_defect():
    """Pin D3: the committed seeding varies across processes."""
    expr = "seeding.legacy_seed(20260802, 0, 'WEIBULL_GAMMA_BLEND')"
    results = {_run_in_subprocess(expr, hs) for hs in ("0", "1", "12345")}
    assert len(results) > 1, (
        "expected legacy hash() seeding to vary across PYTHONHASHSEED values (D3); got %r"
        % results
    )
