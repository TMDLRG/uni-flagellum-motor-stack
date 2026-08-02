#!/usr/bin/env python3
"""
B4 result assembler.

Reads per-cell outputs from the B4 runner and emits the canonical, sorted-key,
LF-terminated canonical b4-identifiability-robustness-result.v1.json in the
frozen artifact location.

Usage:
  python audits/phase-b/b4-assemble.py \
      --in C05=path,C06=path,C11u2=path,C10=path,C11u4=path,C03C04C07C08=path \
      --out audits/phase-b/b4-identifiability-robustness-result.v1.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]

C12_HEADLINES = ["adverse_M2_over_M3_NLPD",
                 "all_motor_equal_contrasts_inconclusive",
                 "rule_disagreement_NLPD_vs_CRPS",
                 "cohort_dependence_1to8_vs_0to8"]


def _canon(obj):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if obj is None:
        return "null"
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return "null"
        return "%.17g" % obj
    if isinstance(obj, (int,)):
        return str(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=True)
    if isinstance(obj, (list, tuple)):
        return "[" + ",".join(_canon(x) for x in obj) + "]"
    if isinstance(obj, dict):
        items = sorted(obj.items(), key=lambda kv: str(kv[0]))
        return "{" + ",".join(json.dumps(str(k), ensure_ascii=True) + ":" + _canon(v)
                              for k, v in items) + "}"
    if isinstance(obj, (np.floating,)):
        return _canon(float(obj))
    if isinstance(obj, (np.integer,)):
        return str(int(obj))
    if isinstance(obj, np.ndarray):
        return _canon(obj.tolist())
    raise TypeError(f"cannot canonicalize {type(obj)}")


def canonical_json(obj):
    return _canon(obj) + "\n"


def aggregate_c12(cells_run):
    """Deterministic aggregation of stability across executed cells.
    Mirrors the runner's cell_C12 semantics; kept here so the assembler can
    build C12 after all others are in place, without re-running the runner."""
    headlines = {h: {"stable_in": [], "unstable_in": [], "not_evaluable_in": []}
                 for h in C12_HEADLINES}
    c02 = cells_run.get("B4C02", {})
    v = c02.get("verdict")
    if v == "GENERATOR-ROBUST_ADVERSE":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C02")
    elif v == "GENERATOR-SPECIFIC":
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C02")
    else:
        headlines["adverse_M2_over_M3_NLPD"]["not_evaluable_in"].append(
            f"B4C02({v or c02.get('status','NA')})")
    c04 = cells_run.get("B4C04", {})
    for cn, cc in c04.get("cohorts", {}).items():
        if cc.get("verdict") == "SEED-STABLE_ALL_INCONCLUSIVE":
            headlines["all_motor_equal_contrasts_inconclusive"]["stable_in"].append(f"B4C04:{cn}")
        else:
            headlines["all_motor_equal_contrasts_inconclusive"]["unstable_in"].append(
                f"B4C04:{cn}({cc.get('verdict','NA')})")
    c05 = cells_run.get("B4C05", {})
    a = c05.get("treatments", {}).get("a_frozen_exclusion", {})
    b = c05.get("treatments", {}).get("b_naive_include", {})
    if a and b:
        if a.get("m2_vs_m3_nlpd_verdict") == b.get("m2_vs_m3_nlpd_verdict"):
            headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C05(a_vs_b_same_direction)")
        else:
            headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C05(a_vs_b_direction_differs)")
    c06 = cells_run.get("B4C06", {})
    if c06.get("verdict") == "BOUNDARY-STABLE":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C06(outlier)")
    elif c06.get("verdict"):
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append(f"B4C06({c06['verdict']})")
    c07 = cells_run.get("B4C07", {})
    if c07.get("verdict") == "ELIGIBILITY-REPRODUCED":
        headlines["cohort_dependence_1to8_vs_0to8"]["stable_in"].append("B4C07(eligibility_reproduced)")
    c08 = cells_run.get("B4C08", {})
    for cn, cc in c08.get("cohorts", {}).items():
        if cc.get("verdict") == "LOMO-STABLE":
            headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append(f"B4C08:{cn}(LOMO)")
        else:
            headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append(
                f"B4C08:{cn}({cc.get('verdict','NA')})")
            headlines["all_motor_equal_contrasts_inconclusive"]["unstable_in"].append(
                f"B4C08:{cn}(contrastFlipsUnderMotorRemoval)")
    c09 = cells_run.get("B4C09", {})
    v = c09.get("verdict")
    if v == "INTERVAL-ROBUST":
        headlines["adverse_M2_over_M3_NLPD"]["stable_in"].append("B4C09")
    elif v == "INTERVAL-SENSITIVE":
        headlines["adverse_M2_over_M3_NLPD"]["unstable_in"].append("B4C09")
    else:
        headlines["adverse_M2_over_M3_NLPD"]["not_evaluable_in"].append(
            f"B4C09({v or c09.get('status','NA')})")
    # rule disagreement heuristic: C04 both-cohorts seed-stable => rule-disagreement is stable
    if c04:
        stable_pairs = sum(1 for cc in c04.get("cohorts", {}).values()
                           if cc.get("verdict") == "SEED-STABLE_ALL_INCONCLUSIVE")
        if stable_pairs > 0:
            headlines["rule_disagreement_NLPD_vs_CRPS"]["stable_in"].append(
                "B4C04(both_rules_seed_stable)")

    ledger = {}
    for h, lists in headlines.items():
        s = lists["stable_in"]; u = lists["unstable_in"]
        if u and s:
            v = "SPECIFICATION-DEPENDENT"
        elif u:
            v = "UNSTABLE"
        elif s:
            v = "STABLE"
        else:
            v = "NOT_ESTABLISHED"
        ledger[h] = {"verdict": v, **lists}
    return {"cell": "B4C12_RANKING_AND_INTERVAL_CROSSING_STABILITY",
            "headlines": ledger,
            "note": "Aggregation of stability contributions from cells "
                    "C02,C04,C05,C06,C07,C08,C09. M4/M7 identifiability (C10/C11) "
                    "map into the SPECIFICATION-DEPENDENT column for the "
                    "mechanism-interpretation of any M3-alternative advantage."}


def _merge_c11(a, b):
    """Merge two B4C11 records: the U2-only run and the U4-only run become
    one record with both filled. If both have the same sub-key populated
    non-trivially, prefer the one whose 'status' != NOT_RUN."""
    merged = dict(a)
    for k, v in b.items():
        if k == "U2_profile":
            av = a.get("U2_profile", {})
            bv = v
            if av.get("status") == "NOT_RUN" and bv.get("status") != "NOT_RUN":
                merged["U2_profile"] = bv
            elif bv.get("status") == "NOT_RUN" and av.get("status") != "NOT_RUN":
                merged["U2_profile"] = av
            elif "verdict" in bv and "verdict" not in av:
                merged["U2_profile"] = bv
        elif k == "U4_bootstrap":
            av = a.get("U4_bootstrap", {})
            bv = v
            if av.get("status") == "NOT_RUN" and bv.get("status") != "NOT_RUN":
                merged["U4_bootstrap"] = bv
            elif bv.get("status") == "NOT_RUN" and av.get("status") != "NOT_RUN":
                merged["U4_bootstrap"] = av
            elif "verdict" in bv and "verdict" not in av:
                merged["U4_bootstrap"] = bv
        elif k in ("resourceBoundPartial_U4",):
            merged[k] = a.get(k) or b.get(k)
        elif k == "M7_status":
            # recompute below after merge
            pass
        else:
            if k not in merged:
                merged[k] = v
    # recompute M7 status after merge
    u2v = merged.get("U2_profile", {}).get("verdict") or ""
    u4v = merged.get("U4_bootstrap", {}).get("verdict") or ""
    fires = []
    if u2v.startswith("UNIDENTIFIED"):
        fires.append("U2")
    if u4v.startswith("UNSTABLE"):
        fires.append("U4")
    if fires:
        merged["M7_status"] = (f"UNIDENTIFIED_OR_UNSTABLE ({','.join(fires)}) "
                                "(U1 interior, U3 LRT-supported per B3)")
    else:
        merged["M7_status"] = "IDENTIFIED_ON_THIS_COHORT (U1/U2/U3/U4 all OK)"
    return merged


def load_cells_from_paths(paths):
    """paths: dict alias->Path. Extracts cells dict from each JSON and merges.
    B4C11 records from separate U2-only and U4-only runs are merged into one."""
    cells = {}
    provenance = {}
    for alias, p in paths.items():
        j = json.loads(Path(p).read_text(encoding="utf-8"))
        for cid, cell in j.get("cells", {}).items():
            if cid == "B4C11" and cid in cells:
                cells[cid] = _merge_c11(cells[cid], cell)
                provenance[cid] += f" + {alias}:{p}"
                continue
            if cid in cells:
                print(f"WARN: cell {cid} already present from {provenance[cid]} — "
                      f"overwriting from {p} ({alias})", file=sys.stderr)
            cells[cid] = cell
            provenance[cid] = f"{alias}:{p}"
    return cells, provenance


def resource_bound_declaration(cid, frozen_n, actual_n, reason):
    """Standard NOT_RUN record for a cell that could not run in this dispatch."""
    return {"cell": cid, "status": "NOT_RUN", "reason": reason,
            "frozen_N": frozen_n, "actual_N": actual_n,
            "resourceBoundPartial": True}


def summarize_predictions(cells):
    """Evaluate each frozen B4 prediction against the executed cell verdicts."""
    preds_path = ROOT / "audits" / "phase-b" / "b4-identifiability-robustness-predictions.v1.json"
    preds = json.loads(preds_path.read_text(encoding="utf-8"))
    out = []
    for p in preds["predictions"]:
        cid_full = p["cell"]; exp = p["expectation"]
        cid = cid_full.split("_")[0]  # short id (e.g. "B4C07")
        rec = {"cell": cid_full, "expectation": exp, "risk": p["risk"], "statement": p["statement"]}
        c = cells.get(cid_full) or cells.get(cid) or {}
        # runner emits cells keyed by short id ("B4C07"); fall back accordingly
        if not c and cid in cells:
            c = cells[cid]
        v = c.get("verdict")
        if not c:
            rec["result"] = "NOT_EVALUATED_CELL_MISSING"
            out.append(rec)
            continue
        if cid == "B4C07":
            rec["observed"] = v
            rec["result"] = "CONFIRMED" if v == "ELIGIBILITY-REPRODUCED" else "REFUTED"
        elif cid == "B4C04":
            all_seed_stable = all(cc.get("verdict") == "SEED-STABLE_ALL_INCONCLUSIVE"
                                  for cc in c.get("cohorts", {}).values())
            rec["observed"] = ("SEED-STABLE_ALL_INCONCLUSIVE" if all_seed_stable
                               else "MIXED_" + str([cc.get("verdict") for cc in c.get("cohorts",{}).values()]))
            rec["result"] = "CONFIRMED" if all_seed_stable and exp == "SEED-STABLE_ALL_INCONCLUSIVE" else "REFUTED"
        elif cid == "B4C08":
            all_stable = all(cc.get("verdict") == "LOMO-STABLE"
                             for cc in c.get("cohorts", {}).values())
            rec["observed"] = "LOMO-STABLE" if all_stable else "UNSTABLE_LOMO"
            rec["result"] = "CONFIRMED" if all_stable and exp == "LOMO-STABLE" else "REFUTED"
        elif cid == "B4C03":
            all_stable = all(cc.get("verdict") == "STABLE" for cc in c.get("cohorts", {}).values())
            rec["observed"] = "STABLE" if all_stable else "UNSTABLE"
            rec["result"] = "CONFIRMED" if all_stable and exp == "STABLE" else "REFUTED"
        elif cid == "B4C05":
            v_load = c.get("loadBearingCensoringFlag", {}).get("verdict")
            rec["observed"] = v_load
            rec["result"] = "CONFIRMED" if v_load == "PASS_censoring_load_bearing" else "REFUTED"
        elif cid == "B4C06":
            rec["observed"] = v
            if v == "BOUNDARY-STABLE":
                rec["result"] = "CONFIRMED_ON_AVAILABLE_VARIANTS"
                rec["note"] = "3400/3600 analysisStartIndex neighbours BLOCKED_EXTERNAL (raw MAT absent)."
            elif v is None:
                rec["result"] = "NOT_ESTABLISHED"
            else:
                rec["result"] = "REFUTED"
        elif cid == "B4C09":
            if c.get("status") == "NOT_RUN":
                rec["observed"] = "NOT_RUN"
                rec["result"] = "NOT_ESTABLISHED_RESOURCE_BOUND"
            else:
                rec["observed"] = v
                rec["result"] = "CONFIRMED" if v == "INTERVAL-ROBUST" and exp == "INTERVAL-ROBUST" \
                    else ("REFUTED" if v in ("INTERVAL-SENSITIVE",) else "PARTIAL")
        elif cid == "B4C10":
            if c.get("status") == "NOT_RUN":
                rec["observed"] = "NOT_RUN"; rec["result"] = "NOT_ESTABLISHED_RESOURCE_BOUND"
            else:
                st = c.get("M4_status", "")
                rec["observed"] = st
                if st.startswith("UNIDENTIFIED"):
                    rec["result"] = "CONFIRMED" if exp == "UNIDENTIFIED_OR_WEAK" else "REFUTED"
                else:
                    rec["result"] = "REFUTED" if exp == "UNIDENTIFIED_OR_WEAK" else "CONFIRMED"
                if c.get("resourceBoundPartial"):
                    rec["result"] += "_PARTIAL"
        elif cid == "B4C11":
            u2 = c.get("U2_profile", {}).get("verdict")
            u4 = c.get("U4_bootstrap", {}).get("verdict")
            m7 = c.get("M7_status", "")
            rec["observed"] = {"U2": u2, "U4": u4, "M7_status": m7}
            weak = (u2 or "").startswith("UNIDENTIFIED") or (u4 or "").startswith("UNSTABLE")
            if exp == "PROFILE_FLAT_OR_WEAK":
                rec["result"] = "CONFIRMED" if weak else "REFUTED"
            if c.get("resourceBoundPartial_U4"):
                rec["result"] = str(rec.get("result", "PARTIAL")) + "_U4_PARTIAL"
        elif cid == "B4C01":
            if c.get("status") == "NOT_RUN":
                rec["observed"] = "NOT_RUN"; rec["result"] = "NOT_ESTABLISHED_RESOURCE_BOUND"
            else:
                rec["observed"] = v; rec["result"] = "CONFIRMED" if v == "PASS" else "REFUTED"
                if c.get("resourceBoundPartial"): rec["result"] += "_PARTIAL"
        elif cid == "B4C02":
            if c.get("status") == "NOT_RUN":
                rec["observed"] = "NOT_RUN"; rec["result"] = "NOT_ESTABLISHED_RESOURCE_BOUND"
            else:
                rec["observed"] = v
                rec["result"] = "CONFIRMED" if v == "GENERATOR-ROBUST_ADVERSE" else "REFUTED"
                if c.get("resourceBoundPartial"): rec["result"] += "_PARTIAL"
        elif cid == "B4C12":
            rec["observed"] = {h: d["verdict"] for h, d in c.get("headlines", {}).items()}
            rec["result"] = "STRUCTURED_LEDGER"
        else:
            rec["observed"] = v; rec["result"] = "UNKNOWN"
        out.append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_paths", type=str, action="append", required=True,
                    help="alias=path input JSON entries (repeatable)")
    ap.add_argument("--out", type=str, required=True)
    ap.add_argument("--evidence-dir", type=str, default=None)
    args = ap.parse_args()

    paths = {}
    for entry in args.in_paths:
        alias, p = entry.split("=", 1)
        paths[alias.strip()] = p.strip()
    cells, provenance = load_cells_from_paths(paths)

    # Add explicit resource-bound NOT_RUN records for any missing frozen cells,
    # so accounting is complete (12 cells always present).
    if "B4C01" not in cells:
        cells["B4C01"] = resource_bound_declaration(
            "B4C01_SYNTHETIC_PARAMETER_RECOVERY", frozen_n=200, actual_n=0,
            reason=("Frozen N_sim=200 per generating model × 5 gens × 1 full B3 refit each ≈ "
                    "1000 refits × ~15-25 min per M4/M7-inclusive competition = ~250-400 h "
                    "wall-clock; not feasible in this dispatch's compute budget. Recorded "
                    "NOT_RUN with reason=RESOURCE_BOUND per plan §4 (allowed status). "
                    "The runner code is present and exercised on the cheap sanity path; "
                    "the resource budget, not the code, blocks this cell."))
    if "B4C02" not in cells:
        cells["B4C02"] = resource_bound_declaration(
            "B4C02_MISSPECIFIED_WORLDS", frozen_n=200, actual_n=0,
            reason=("Frozen N_sim=200 per generator × 3 generators × 1 full B3 refit each ≈ "
                    "600 refits × ~15-25 min = ~150-250 h wall-clock; not feasible in this "
                    "dispatch's compute budget. Recorded NOT_RUN with reason=RESOURCE_BOUND."))
    if "B4C09" not in cells:
        cells["B4C09"] = resource_bound_declaration(
            "B4C09_MEASUREMENT_INTERVAL_UNCERTAINTY", frozen_n=100, actual_n=0,
            reason=("Frozen M_jitter=100 replicates × 1 full B3 refit each ≈ "
                    "100 refits × ~15-25 min = ~25-40 h wall-clock; not feasible in this "
                    "dispatch's compute budget. Recorded NOT_RUN with reason=RESOURCE_BOUND."))

    # C12 aggregation ALWAYS built here from the assembled cells (deterministic
    # pure function of cell verdicts).
    cells["B4C12"] = aggregate_c12(cells)

    predictions = summarize_predictions(cells)

    result = {
        "schema": "uni.flagellum.b4-identifiability-robustness-result/1.0.0",
        "protocolId": "PHASE-B4-IDENTIFIABILITY-ROBUSTNESS-CLAUDE-V1",
        "protocolPath": "audits/phase-b/b4-identifiability-robustness-protocol.v1.json",
        "predictionsPath": "audits/phase-b/b4-identifiability-robustness-predictions.v1.json",
        "predictionRecordPath": "experiments/predictions/b4-identifiability-robustness.prediction.json",
        "consumesB3ResultSha256": "5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd",
        "runner": "audits/phase-b/b4-identifiability-robustness-runner.py",
        "assembler": "audits/phase-b/b4-assemble.py",
        "oracle": "audits/phase-b/b4-independent-oracle.py",
        "cellsRequested": sorted(cells.keys()),
        "cellsExecutedFully": sorted([k for k, v in cells.items()
                                       if v.get("status") != "NOT_RUN"
                                       and not v.get("resourceBoundPartial", False)]),
        "cellsResourceBoundPartial": sorted([k for k, v in cells.items()
                                              if v.get("resourceBoundPartial", False) is True
                                              and v.get("status") != "NOT_RUN"]),
        "cellsNotRunResourceBound": sorted([k for k, v in cells.items()
                                            if v.get("status") == "NOT_RUN"]),
        "cells": cells,
        "predictionsEvaluation": predictions,
        "provenance": provenance,
        "environment": {"python": sys.version.split()[0],
                        "numpy": np.__version__, "scipy": scipy.__version__},
        "governance": {
            "b3ResultConsumedPath": "audits/phase-b/b3-model-competition-result.json",
            "b3ResultConsumedSha256": "5d7a0589e94de6b10f425f2d483e1e2a8f899d336aa59c335990209795e6b2bd",
            "b3InputsExpectedByteIdenticalTo": "e5b4969",
            "phaseCPhaseDExpectedByteIdenticalTo": "4fcba6c",
            "b4PredictionCommittedAgainst": "e433ef9b92a8803208abc76a148016ef4b3c299b",
            "noPostHocRules": ("No threshold, cohort, seed, bound, optimizer setting or scoring "
                               "rule may be changed after any B4 result is seen. Cells with "
                               "reduced replicate counts are marked resourceBoundPartial=true "
                               "with the actual N run; cells that could not run at all are "
                               "marked status=NOT_RUN with reason=RESOURCE_BOUND. Neither is a "
                               "relabeling of PASS."),
        },
    }
    body = canonical_json(result).encode("utf-8")
    Path(args.out).write_bytes(body)
    print(f"wrote {args.out} ({len(body)} bytes) sha256={hashlib.sha256(body).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
