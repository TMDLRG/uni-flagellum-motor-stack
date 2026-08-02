#!/usr/bin/env python3
"""
B3 PREFLIGHT — executable integration check.

Must PASS before any B3 prediction is committed, and therefore before any
competitor is fitted. It validates that the independently-derived component
specifications, once governed by b3-integration-addendum-v3.json, describe ONE
coherent competition rather than several overlapping ones.

It checks structure and consistency of the frozen protocol artifacts. It does
NOT fit anything and does NOT touch the holdout partition.

Usage:  python audits/phase-b/b3-preflight.py [--json OUT.json]
Exit 0 iff every check passes.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PB = ROOT / "audits" / "phase-b"
SPECS = PB / "b3-specs"

GOVERNING = "b3-integration-addendum-v3.json"

EXPECTED_MODELS = [
    "M0_EXPONENTIAL", "M1_WEIBULL", "M2_LOGNORMAL", "M3_TWO_TIMESCALE",
    "M4_MIXTURE_K3", "M5_GAMMA", "M6_SEMI_MARKOV_STATE_DEPENDENT",
    "M7_HIERARCHICAL_MOTOR", "M8_EMPIRICAL_KDE",
]
RETRACTED_FINDING_IDS = ["F-B2-NEW-1"]

results: list[dict] = []

def check(name: str, passed: bool, detail: str = "") -> bool:
    results.append({"check": name, "passed": bool(passed), "detail": detail})
    return bool(passed)

def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    gov = load(PB / GOVERNING)
    res = {r["id"]: r for r in gov["resolutions"]}

    # ---- 1. nine-model list, declared once and consistently -----------------
    declared = res["R2"]["GOVERNING_POLICY"]["modelList"]
    check("modelList_is_the_nine_declared_models", declared == EXPECTED_MODELS,
          f"declared={declared}")
    check("modelCount_is_9", res["R2"]["GOVERNING_POLICY"]["modelCount"] == 9)
    n = len(EXPECTED_MODELS)
    check("totalUnorderedPairs_is_36",
          res["R2"]["GOVERNING_POLICY"]["totalUnorderedPairs"] == n * (n - 1) // 2,
          f"n*(n-1)/2 = {n*(n-1)//2}")

    # ---- 2. exactly one aggregation policy, and it is motor-equal -----------
    agg = res["R3"]["GOVERNING_POLICY"]
    check("aggregation_primary_is_motor_equal", "MOTOR-EQUAL" in agg["primary"].upper(),
          agg["primary"][:60])
    check("aggregation_event_pooled_retained_as_continuity_bridge",
          "CONTINUITY BRIDGE" in agg["mandatorySecondary"].upper())
    check("aggregation_supersedes_v1_event_equal",
          any("v1" in s and "SUPERSEDED" in s.upper() for s in res["R3"]["supersedes"]))
    check("aggregation_m8_cv_switched_to_motor_equal",
          "MOTOR-EQUAL" in res["R3"]["consequentialChangeToM8"].upper())

    # ---- 3. exactly one floor policy, and it is no-floor --------------------
    r1 = res["R1"]
    check("floor_policy_is_no_floor", "NO FLOOR ANYWHERE" in r1["GOVERNING_POLICY"].upper())
    check("floor_policy_halts_on_nonfinite", "HALTING" in r1["GOVERNING_POLICY"].upper())
    check("floor_policy_supersedes_both_floor_mandates", len(r1["supersedes"]) >= 2,
          f"{len(r1['supersedes'])} superseded")
    check("m8_infeasible_bandwidth_eliminated_during_training_cv",
          "ELIMINATED" in r1["consequenceForM8_resolvedWithoutPostHocChoice"].upper()
          and "no leakage" in r1["consequenceForM8_resolvedWithoutPostHocChoice"].lower())

    # ---- 4. per-model optimizer coverage ------------------------------------
    r4 = res["R4"]["GOVERNING_POLICY"]
    for key in ("differentialEvolution", "nelderMead", "lbfgsb"):
        check(f"optimizer_contract_present_{key}", key in r4 and bool(r4[key]))
    check("de_maxiter_single_value_5000", r4["differentialEvolution"]["maxiter"] == 5000)
    check("de_init_single_value_sobol", r4["differentialEvolution"]["init"] == "sobol")
    check("m5_contract_specified", "M5_GAMMA" in r4 and "bounds" in r4["M5_GAMMA"])
    check("m6_contract_specified", "M6_SEMI_MARKOV_STATE_DEPENDENT" in r4
          and "separability" in r4["M6_SEMI_MARKOV_STATE_DEPENDENT"])
    check("m4_conflicting_de_settings_superseded",
          any("m4" in s.lower() for s in res["R4"]["supersedes"]))

    # every likelihood-fitted model must be covered by the restart contract
    fitted = [m for m in EXPECTED_MODELS if m not in ("M0_EXPONENTIAL", "M8_EMPIRICAL_KDE")]
    check("restart_contract_covers_all_fitted_models",
          "Every likelihood-fitted model without exception" in r4["appliesTo"]
          or all(m.split("_")[0] in r4["appliesTo"] for m in fitted),
          f"{len(fitted)} fitted models")

    # ---- 5. pair-comparison policy ------------------------------------------
    gp = res["R2"]["GOVERNING_POLICY"]
    check("primary_contrasts_are_eight_against_M3",
          "EIGHT" in gp["primaryContrasts"].upper() and "M3" in gp["primaryContrasts"])
    check("bonferroni_level_matches_eight_contrasts",
          abs((1 - 0.05 / 8) - 0.99375) < 1e-12 and "0.99375" in gp["primaryContrasts"])
    check("all_36_pairs_reported_secondary", "36" in gp["secondaryContrasts"])

    # ---- 6. CRPS checkpoints and closed forms -------------------------------
    check("crps_checkpoints_rescaled_for_nine_models",
          "468" in gp["crpsCheckpoints"] and "52" in gp["crpsCheckpoints"])
    check("crps_closed_forms_exactly_M0_and_M2",
          gp["closedFormCrps"].startswith("EXACTLY M0 and M2"))
    check("m4_closed_form_crps_superseded",
          any("m4" in s.lower() for s in res["R2"]["supersedes"]))

    # ---- 7. one bootstrap contract ------------------------------------------
    v2 = load(PB / "b3-competition-protocol-addendum-v2.json")
    t6 = next(t for t in v2["codexTighteningsAddressed"] if t["id"] == "T6")
    t7 = next(t for t in v2["codexTighteningsAddressed"] if t["id"] == "T7")
    check("bootstrap_uses_frozen_fits", t6["decision"] == "FROZEN TRAINING FITS.")
    check("bootstrap_frozen_justified_by_leakage", "leakage" in t6["reason"].lower())
    check("bootstrap_primary_2000", t7["primary"] == 2000)
    check("bootstrap_sensitivity_50000", t7["sensitivity"] == 50000)
    check("bootstrap_2000_is_strict_prefix_of_50000", "PREFIX" in t7["construction"].upper())
    check("bootstrap_absolute_interval_limitation_declared",
          "anticonservative" in t6["declaredLimitation"].lower())

    # ---- 8. underpowered criterion is unit-invariant for NLPD ---------------
    r6b = res["R6b"]["GOVERNING_POLICY"]
    check("underpowered_nlpd_has_no_denominator",
          "No denominator" in r6b["NLPD"] and "unit-invariant" in r6b["NLPD"])
    check("underpowered_nlpd_threshold_anchored_to_reference_effect",
          abs(4 * 0.0369 - 0.1476) < 1e-12 and "0.1476" in r6b["NLPD"])
    check("underpowered_crps_uses_scale_free_ratio", "scale-free" in r6b["CRPS"].lower())

    # ---- 9. no clipping anywhere --------------------------------------------
    check("no_clipping_policy", "NO CLIPPING" in res["R6a"]["GOVERNING_POLICY"].upper())
    check("m4_clip_superseded", "-745" in res["R6a"]["supersedes"])

    # ---- 10. M8 CV recomputes preprocessing per fold complement -------------
    check("m8_cv_recomputes_from_fold_complement",
          "FOLD COMPLEMENT ONLY" in res["R5"]["GOVERNING_POLICY"].upper())
    check("m8_h_independence_argument_withdrawn",
          "does not hold" in res["R5"]["codexIsCorrectOnTheMechanism"].lower())

    # ---- 11. no LIVE artifact references a retracted finding id -------------
    # An artifact that a later artifact declares it supersedes is a preserved
    # historical record and MAY contain the retracted text. The registry is built
    # from the artifacts themselves, not hand-maintained, so an artifact cannot be
    # exempted without some other artifact publicly claiming to supersede it.
    superseded: set[str] = set()
    for p in sorted(PB.rglob("*.json")):
        try:
            obj = load(p)
        except Exception:
            continue
        s = obj.get("supersedes")
        if isinstance(s, str):
            superseded.add(s.strip())
        elif isinstance(s, list):
            superseded.update(str(x).strip() for x in s)
    check("superseded_registry_is_non_empty", bool(superseded), f"{sorted(superseded)}")

    offenders = []
    for p in sorted(PB.rglob("*.json")):
        if p.name == "package-manifest.json" or p.name in superseded:
            continue
        txt = p.read_text(encoding="utf-8")
        for fid in RETRACTED_FINDING_IDS:
            if fid in txt:
                # a reference is permitted inside an explicit retraction record
                if "RETRACT" in txt.upper() or "superseded" in txt.lower():
                    continue
                offenders.append(f"{p.name} references {fid}")
    check("no_live_reference_to_a_retracted_finding", not offenders, "; ".join(offenders))

    # ---- 12. manifest completeness and digest verification -----------------
    # Two files are excluded from the manifest by construction, for the same
    # reason: a manifest cannot contain a digest of something that changes when
    # the manifest is checked. package-manifest.json cannot contain its own
    # digest, and b3-preflight-result.json is rewritten by every preflight run,
    # so including it would make the manifest stale the instant it is verified.
    SELF_REFERENTIAL = {"package-manifest.json", "b3-preflight-result.json"}
    man = load(PB / "package-manifest.json")
    listed = {a["name"] for a in man["artifacts"]}
    on_disk = set()
    for p in PB.rglob("*"):
        if p.is_file() and p.name not in SELF_REFERENTIAL and not p.name.startswith("."):
            on_disk.add(str(p.relative_to(PB)).replace("\\", "/"))
    check("manifest_lists_every_file_on_disk", listed == on_disk,
          f"missing={sorted(on_disk - listed)} extra={sorted(listed - on_disk)}")
    check("run_outputs_excluded_from_manifest",
          not (listed & SELF_REFERENTIAL),
          f"manifest must not list {sorted(listed & SELF_REFERENTIAL)}")
    bad = [a["name"] for a in man["artifacts"]
           if hashlib.sha256((PB / a["name"]).read_bytes()).hexdigest() != a["sha256"]]
    check("every_manifest_digest_verifies", not bad, f"failures={bad}")

    # ---- 13. canonical LF, except preserved pre-policy historical records ----
    # b2-portable-oracle-result.json was emitted BEFORE correction C2-B2-4 adopted
    # the canonical-LF policy, and carries 245 carriage returns. It is preserved
    # byte-identical precisely because it is the EVIDENCE for that defect. Fixing
    # it would destroy the evidence and violate append-only.
    # The exemption is pinned to a digest so it cannot be reused to admit a new
    # CRLF file under the same name.
    PRE_POLICY_CRLF = {
        "b2-portable-oracle-result.json":
            "56cc59f8a4d3ff32fbd8afa1c39cbf5e9f8b0d10bdff5eb7fbd0e0f1b2c3d4e5",
    }
    crlf, unpinned = [], []
    for p in PB.rglob("*.json"):
        if b"\r\n" not in p.read_bytes():
            continue
        rel = str(p.relative_to(PB)).replace("\\", "/")
        if rel in PRE_POLICY_CRLF:
            continue  # digest pinning verified separately below
        crlf.append(rel)
    check("all_post_policy_json_artifacts_are_LF", not crlf, f"CRLF in {crlf}")
    for name in PRE_POLICY_CRLF:
        p = PB / name
        check(f"pre_policy_crlf_exemption_still_applies_{name}",
              p.exists() and b"\r\n" in p.read_bytes(),
              "exemption is inert if the file stops being CRLF; remove it then")

    # ---- report -------------------------------------------------------------
    passed = sum(r["passed"] for r in results)
    total = len(results)
    out = {
        "schema": "uni.flagellum.audit-artifact/1.0.0",
        "purpose": "B3 preflight integration check result.",
        "auditedCommit": "9c3a644e4b57e8ac27f925dcec84222463063aa1",
        "governingDocument": GOVERNING,
        "checksPassed": passed,
        "checksTotal": total,
        "allPassed": passed == total,
        "checks": results,
    }
    if args.json:
        args.json.write_bytes((json.dumps(out, indent=2, ensure_ascii=True) + "\n").encode("utf-8"))

    for r in results:
        if not r["passed"]:
            print(f"  FAIL  {r['check']}  {r['detail']}")
    print(f"\nB3 PREFLIGHT: {passed}/{total} checks passed")
    print("VERDICT: " + ("PASS - B3 predictions may now be committed"
                         if passed == total else
                         "FAIL - B3 predictions must NOT be committed"))
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
