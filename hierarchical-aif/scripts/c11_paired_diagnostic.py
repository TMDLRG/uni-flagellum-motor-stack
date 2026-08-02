"""PAIRED DIAGNOSTIC (NOT the corrected C11 result).

Runs a small number of C11 U4 bootstrap replicates under the LEGACY (defective) and CORRECTED
cluster-bootstrap semantics on identical draws, to measure whether D1 has a material effect on
tau. This is a diagnostic at tiny N, NOT the frozen N=2000 run. It licenses no verdict.
"""
import json, sys, time
from pathlib import Path
import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
from motor_stack_aif import _bridge, bootstrap  # noqa: E402

N_REP = int(sys.argv[1]) if len(sys.argv) > 1 else 5
SEED_BASE = 20260717

b3 = _bridge.b3(); b4 = _bridge.b4()
coh = _bridge.frozen_cohort()
res = _bridge.b3_result()
m7rec = res["cohorts"]["derived_eligible_1_to_8"]["fitted"]["M7_HIERARCHICAL_MOTOR"]
k_hat = m7rec["kTau"]["k"]; tau_hat = m7rec["kTau"]["tau"]

rows = []
t0 = time.time()
for b in range(N_REP):
    rng = np.random.default_rng(SEED_BASE + b)
    sampled = bootstrap.draw_motors(coh.train_motors, rng)  # identical draws for both arms
    out = {"replicate": b, "n_draws": len(sampled), "n_distinct": len(set(sampled))}
    for arm, builder in (("legacy_defective", bootstrap.build_bootstrap_cohort_LEGACY_DEFECTIVE),
                         ("corrected", bootstrap.build_bootstrap_cohort)):
        try:
            coh_b = builder(coh, sampled, name="c11_%s_%d" % (arm, b))
            fit = b4._fit_m7_reduced(coh_b, k_full=k_hat, tau_full=tau_hat)
            out[arm] = {"groups": len(coh_b.train_by_motor),
                        "tau": None if fit is None else float(fit["tau"]),
                        "k": None if fit is None else float(fit["k"])}
        except Exception as ex:
            out[arm] = {"error": "%s: %s" % (type(ex).__name__, ex)}
    rows.append(out)
    print(json.dumps(out), flush=True)

def taus(arm):
    return [r[arm]["tau"] for r in rows if isinstance(r.get(arm), dict) and r[arm].get("tau") is not None]

summary = {
    "DISCLAIMER": "DIAGNOSTIC ONLY at N=%d. NOT the frozen N=2000 corrected C11 result. Licenses no verdict." % N_REP,
    "n_replicates": N_REP, "seed_base": SEED_BASE,
    "legacy_groups": [r["legacy_defective"].get("groups") for r in rows if isinstance(r.get("legacy_defective"), dict)],
    "corrected_groups": [r["corrected"].get("groups") for r in rows if isinstance(r.get("corrected"), dict)],
    "legacy_tau": taus("legacy_defective"),
    "corrected_tau": taus("corrected"),
    "runtime_s": time.time() - t0,
}
for arm in ("legacy_tau", "corrected_tau"):
    v = summary[arm]
    if v:
        summary[arm + "_median"] = float(np.median(v))
        summary[arm + "_min"] = float(np.min(v)); summary[arm + "_max"] = float(np.max(v))
summary["rows"] = rows
out_p = Path(__file__).resolve().parents[1] / "results" / "motor_stack_aif" / "C11-PAIRED-DIAGNOSTIC.json"
out_p.write_text(json.dumps(summary, indent=1, sort_keys=True), encoding="utf-8")
print("\nWROTE", out_p)
print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=1))
