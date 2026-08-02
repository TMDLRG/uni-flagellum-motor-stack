"""Corrected cell reasons, grounded in measured runtime.

These SUPERSEDE the reason strings recorded in
`audits/phase-b/b4-identifiability-robustness-result.v1.json` for reporting purposes only.
The frozen artifact is NOT edited; it remains the historical record. See D2 and D4 in
`hierarchical-aif/ledgers/HIERARCHICAL-AIF-DEFECT-LEDGER.md`.

Measured on the frozen cohort, 2026-07-21 (Python 3.12.10, numpy 2.3.5, scipy 1.16.3):
    fit_simple_models  32.0 s
    fit_m6             20.1 s   -> C01/C02 per-simulation 52.1 s
    _fit_m4_reduced     3.8 s
    _fit_m7_reduced    36.2 s
"""
from __future__ import annotations

PROTOCOL_VERSION = "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1"

MEASURED_SECONDS = {
    "fit_simple_models": 32.0,
    "fit_m6": 20.1,
    "c01_c02_per_sim": 52.1,
    "_fit_m4_reduced": 3.8,
    "_fit_m7_reduced": 36.2,
}

C01_REASON = (
    "B4C01 fits the simple competitors (M0, M1, M2, M3, M5) plus M6 on each synthetic dataset; "
    "it explicitly skips M4/M8 and the hierarchical model, so the cost driver is the simple "
    "model set, not a full 9-model competition. Measured per-simulation cost on the frozen "
    "cohort is 52.1 s, so frozen N_sim=200 x 5 generators = 1000 simulations projects to "
    "approximately 14.5 h. The previously recorded 250-400 h figure was overstated by roughly "
    "17-28x and attributed the cost to a model set this cell does not fit."
)

C02_REASON = (
    "B4C02 fits the simple competitors plus M6 on each misspecified-world dataset; M4/M7/M8 are "
    "skipped. Measured per-simulation cost is 52.1 s, so frozen N_sim=200 x 3 generators = 600 "
    "simulations projects to approximately 8.7 h. The previously recorded 150-250 h figure was "
    "overstated by roughly 17-29x. This is the HIGH-risk misspecified-world discriminator and it "
    "is feasible at full frozen N."
)

C10_REASON = (
    "B4C10 runs a training-motor bootstrap refitting M4 under a reduced DE budget. Measured cost "
    "is 3.8 s per replicate, so frozen N_boot=2000 projects to approximately 2.1 h. The cell was "
    "previously executed at 100 of 2000 replicates and labelled resourceBoundPartial; at the "
    "measured cost it is feasible at full frozen N and should not have been partial."
)

C11_REASON = (
    "B4C11 U4 runs a training-motor bootstrap refitting M7. Measured cost is 36.2 s per "
    "replicate, so frozen N_boot=2000 projects to approximately 20.1 h. The cell was previously "
    "executed at 30 of 2000 replicates. Independently of cost, the previous run used a bootstrap "
    "that collapsed duplicate motor draws by motorId (D1), so its U4 verdict is withdrawn and a "
    "corrected full-N rerun is required."
)

BY_CELL = {
    "B4C01": C01_REASON,
    "B4C02": C02_REASON,
    "B4C10": C10_REASON,
    "B4C11": C11_REASON,
}
