"""Assemble EVERY available held-out contrast into one materiality map.

WHY THIS EXISTS
---------------
D10: the frozen CI-bound rule has NO minimum-effect-size guard. A paired motor-cluster
bootstrap resamples MOTORS, so it resolves a difference of ANY magnitude provided its sign is
consistent across motors. M7 exposed it (2.507e-07 nats "RESOLVED_ABOVE"). The repair was ADDED
INTERPRETATION, never re-thresholding. That interpretation currently exists on only 3 of the 57
contrasts in the repository. This script applies the SAME rule - imported in spirit, transcribed
verbatim from `scripts/recompute_m4_m6_m7_per_motor.py` lines 222-258 - across every contrast the
repository holds, so the reader can see at a glance which "wins" are material and which are
consistent numerical dust.

IT COMPUTES NO NEW SCIENCE. It re-reads frozen artifacts, re-derives interval widths by
subtraction, and attaches a reading. No refit, no bootstrap, no data load, no holdout access.

HONESTY FENCES ENFORCED IN CODE
-------------------------------
1. BCa intervals exist ONLY for the 48 frozen B3 contrasts. The 6 F-side and 3 M4/M6/M7
   contrasts are PERCENTILE-ONLY: their BCaWidth is emitted as the literal string
   "NOT_COMPUTED". This script never computes, estimates or imputes a BCa for them.
2. The 0.042-nat resolution floor is an NLPD-NATS quantity. B3 also scores CRPS_normalized and
   CRPS_seconds, which are NOT nats. For those the floor, the ratio, the reading and the
   win-flag are emitted as "NOT_APPLICABLE_DIFFERENT_UNITS". Transferring a nats floor onto a
   CRPS scale would be exactly the units error the contract forbids.
3. Frozen verdicts are copied VERBATIM. Nothing here alters, upgrades or downgrades one.
4. The floor itself was derived on cohort `derived_eligible_1_to_8`. Rows from cohort
   `primary_states_0_to_8` carry `floorTransferCaveat = true`.

D5: no event data is loaded. `nextStateN`/`direction`/`jump` are never touched.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RESULTS = HERE.parent / "results" / "motor_stack_aif"

B3_RESULT = REPO / "audits" / "phase-b" / "b3-model-competition-result.json"
FSIDE_RESULT = RESULTS / "F_SIDE_MOTOR_STACK_SCORING_RESULT.json"
M467_RESULT = RESULTS / "M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json"
OUT = RESULTS / "materiality_map_all_contrasts.json"

# ---------------------------------------------------------------------------------------------
# The floor. HEURISTIC, NOT a pre-specified equivalence margin. It is the BCa HALF-width of the
# narrowest frozen B3 contrast (M4_MIXTURE_K3, NLPD_motor_equal, derived_eligible_1_to_8):
#   BCa width 0.08414086126525253 -> half 0.04207043063262626, rounded to 0.042 in
#   `recompute_m4_m6_m7_per_motor.py` and in the F-side result's `resolution.halfWidthFloorNats`.
# The superseded 0.064 figure came from the mislabelled `width` field (D7).
# ---------------------------------------------------------------------------------------------
RESOLUTION_FLOOR_NATS = 0.042
FLOOR_SOURCE_CONTRAST = ("derived_eligible_1_to_8", "NLPD_motor_equal", "M4_MIXTURE_K3")

NA_UNITS = "NOT_APPLICABLE_DIFFERENT_UNITS"
NOT_COMPUTED = "NOT_COMPUTED"

NATS_RULES = {"NLPD_motor_equal"}
CRPS_RULES = {"CRPS_normalized", "CRPS_seconds"}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def classify(point, lo, hi):
    """VERBATIM port of the D10 guard in scripts/recompute_m4_m6_m7_per_motor.py (lines 227-242).

    inside_floor  -> SCIENTIFICALLY_NULL   (whole interval inside +/- floor)
    point<floor   -> SUB_FLOOR_EFFECT      (point estimate below floor, interval reaches outside)
    otherwise     -> MATERIAL
    """
    inside_floor = max(abs(lo), abs(hi)) < RESOLUTION_FLOOR_NATS
    point_below_floor = abs(point) < RESOLUTION_FLOOR_NATS
    if inside_floor:
        return "SCIENTIFICALLY_NULL", (
            "the ENTIRE interval lies inside +/-%.3f nats, the corrected motor-equal resolution "
            "floor, so no scientifically material difference exists in either direction"
            % RESOLUTION_FLOOR_NATS)
    if point_below_floor:
        return "SUB_FLOOR_EFFECT", (
            "the point estimate %.3e nats is below the %.3f-nat resolution floor; any CI-bound "
            "resolution here rests on CONSISTENCY of sign across motors, not on effect magnitude"
            % (point, RESOLUTION_FLOOR_NATS))
    return "MATERIAL", "the point estimate exceeds the resolution floor"


def row(**kw):
    return kw


def main():
    b3 = json.loads(B3_RESULT.read_text(encoding="utf-8"))
    fside = json.loads(FSIDE_RESULT.read_text(encoding="utf-8"))
    m467 = json.loads(M467_RESULT.read_text(encoding="utf-8"))

    rows = []
    d7_width_matches = {"percentile": 0, "bca": 0, "neither": 0}
    interval_used_is = {"bca": 0, "percentile": 0, "unmatched": 0}

    # ------------------------------------------------------------------ 1. 48 frozen B3
    for cohort, cv in b3["cohorts"].items():
        n_motors = len(cv["holdoutMotors"])
        for rule, rv in cv["contrasts"].items():
            for model, c in rv.items():
                bca = c["bca"]
                pct = c["percentile"]
                used = c["intervalUsed"]
                bca_w = None if bca is None else float(bca[1] - bca[0])
                pct_w = float(pct[1] - pct[0])
                if bca is not None and used == bca:
                    used_name = "bca"
                elif used == pct:
                    used_name = "percentile"
                else:
                    used_name = "unmatched"
                interval_used_is[used_name] += 1

                pub_w = c["width"]
                if abs(pub_w - pct_w) <= 1e-15:
                    d7_width_matches["percentile"] += 1
                elif bca_w is not None and abs(pub_w - bca_w) <= 1e-15:
                    d7_width_matches["bca"] += 1
                else:
                    d7_width_matches["neither"] += 1

                point = float(c["pointEstimate"])
                lo, hi = float(used[0]), float(used[1])
                if rule in NATS_RULES:
                    reading, why = classify(point, lo, hi)
                    floor = RESOLUTION_FLOOR_NATS
                    ratio = abs(point) / RESOLUTION_FLOOR_NATS
                    win = (c["verdict"] in ("RESOLVED_ABOVE", "CHALLENGER_BETTER")
) and reading == "MATERIAL"  # D10: the win flag is decided by the INTERVAL verdict and the
        # materiality reading ONLY. `beatsM3` is a frozen boolean kept as reported
        # provenance; allowing it to set the flag would bypass the interval entirely.
                    units = "nats/event (motor-equal NLPD, SECONDS scale)"
                else:
                    reading = NA_UNITS
                    why = ("the 0.042-nat floor is an NLPD-nats quantity; CRPS is not measured "
                           "in nats, so neither the floor nor any ratio to it transfers")
                    floor = NA_UNITS
                    ratio = NA_UNITS
                    win = NA_UNITS
                    units = ("CRPS seconds" if rule == "CRPS_seconds"
                             else "CRPS on normalised y (dimensionless)")

                rows.append(row(
                    contrastId="B3|%s|%s|%s" % (cohort, rule, model),
                    source="FROZEN_B3",
                    sourceArtifact="audits/phase-b/b3-model-competition-result.json",
                    cohort=cohort,
                    rule=rule,
                    units=units,
                    reference=b3["referenceModel"],
                    challenger=model,
                    signConvention=("contrast = S(reference) - S(challenger); entirely above 0 "
                                    "=> challenger better; entirely below 0 => reference better; "
                                    "contains 0 => NOT_ESTABLISHED"),
                    nHoldoutMotors=n_motors,
                    frozenVerdict=c["verdict"],
                    effectSize=point,
                    intervalUsed=used_name,
                    intervalUsedValues=[lo, hi],
                    BCaWidth=bca_w if bca_w is not None else NOT_COMPUTED,
                    percentileWidth=pct_w,
                    publishedWidthField=pub_w,
                    resolutionFloor=floor,
                    effectToFloorRatio=ratio,
                    scientificReading=reading,
                    scientificReadingWhy=why,
                    reportableAsAWin=win,
                    frozenBeatsM3=c["beatsM3"],
                    frozenUnderpowered=c["underpowered"],
                    floorTransferCaveat=(rule in NATS_RULES
                                         and cohort != FLOOR_SOURCE_CONTRAST[0]),
                ))

    # ------------------------------------------------------------------ 2. 6 F-side
    for model, c in fside["contrasts"].items():
        point = float(c["pointEstimate"])
        lo, hi = float(c["interval"][0]), float(c["interval"][1])
        reading, why = classify(point, lo, hi)
        rows.append(row(
            contrastId="FSIDE|derived_eligible_1_to_8|NLPD_motor_equal|%s" % model,
            source="F_SIDE_SCORING",
            sourceArtifact=("hierarchical-aif/results/motor_stack_aif/"
                            "F_SIDE_MOTOR_STACK_SCORING_RESULT.json"),
            cohort="derived_eligible_1_to_8",
            rule="NLPD_motor_equal",
            units="nats/event (motor-equal NLPD, SECONDS scale)",
            reference=model,
            challenger="F_MOTOR_STACK",
            signConvention=("contrast = S(reference) - S(challenger); entirely above 0 => "
                            "challenger (F_MOTOR_STACK) better"),
            nHoldoutMotors=len(fside["motorOrder"]),
            frozenVerdict=c["verdict"],
            effectSize=point,
            intervalUsed="percentile",
            intervalUsedValues=[lo, hi],
            BCaWidth=NOT_COMPUTED,
            percentileWidth=float(hi - lo),
            publishedWidthField=c["width"],
            resolutionFloor=RESOLUTION_FLOOR_NATS,
            effectToFloorRatio=abs(point) / RESOLUTION_FLOOR_NATS,
            scientificReading=reading,
            scientificReadingWhy=why,
            reportableAsAWin=(c["verdict"] == "RESOLVED_ABOVE" and reading == "MATERIAL"),
            frozenBeatsM3=NOT_COMPUTED,
            frozenUnderpowered=NOT_COMPUTED,
            floorTransferCaveat=False,
            prospectivity="NOT_SATISFIED (D9)",
        ))

    # ------------------------------------------------------------------ 3. 3 M4/M6/M7
    for model, c in m467["contrasts"].items():
        point = float(c["pointEstimate"])
        lo, hi = float(c["interval"][0]), float(c["interval"][1])
        reading, why = classify(point, lo, hi)
        if reading != c["scientificReading"]["classification"]:
            raise SystemExit(
                "ABORT: re-derived reading %r disagrees with the recorded reading %r for %s. The "
                "rule was supposed to be identical." % (
                    reading, c["scientificReading"]["classification"], model))
        rows.append(row(
            contrastId="M4M6M7|derived_eligible_1_to_8|NLPD_motor_equal|%s" % model,
            source="M4_M6_M7_POST_HOC",
            sourceArtifact=("hierarchical-aif/results/motor_stack_aif/"
                            "M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json"),
            cohort="derived_eligible_1_to_8",
            rule="NLPD_motor_equal",
            units="nats/event (motor-equal NLPD, SECONDS scale)",
            reference=model,
            challenger="F_MOTOR_STACK",
            signConvention=("contrast = S(reference) - S(challenger); entirely above 0 => "
                            "challenger (F_MOTOR_STACK) better"),
            nHoldoutMotors=m467["nHoldoutMotors"],
            frozenVerdict=c["verdict"],
            effectSize=point,
            intervalUsed="percentile",
            intervalUsedValues=[lo, hi],
            BCaWidth=NOT_COMPUTED,
            percentileWidth=float(hi - lo),
            publishedWidthField=c["width"],
            resolutionFloor=RESOLUTION_FLOOR_NATS,
            effectToFloorRatio=abs(point) / RESOLUTION_FLOOR_NATS,
            scientificReading=reading,
            scientificReadingWhy=why,
            reportableAsAWin=bool(c["reportableAsAWin"]),
            frozenBeatsM3=NOT_COMPUTED,
            frozenUnderpowered=NOT_COMPUTED,
            floorTransferCaveat=False,
            prospectivity="NOT_SATISFIED - POST_HOC_EXPLORATORY (D9)",
        ))

    # ------------------------------------------------------------------ tallies
    nats_rows = [r for r in rows if r["rule"] in NATS_RULES]
    crps_rows = [r for r in rows if r["rule"] in CRPS_RULES]
    tally = {}
    for r in nats_rows:
        tally[r["scientificReading"]] = tally.get(r["scientificReading"], 0) + 1
    verdicts = {}
    for r in rows:
        verdicts[r["frozenVerdict"]] = verdicts.get(r["frozenVerdict"], 0) + 1

    resolved_labels = {"RESOLVED_ABOVE", "RESOLVED_BELOW", "CHALLENGER_BETTER",
                       "REFERENCE_BETTER"}
    d10_class = [r["contrastId"] for r in nats_rows
                 if r["frozenVerdict"] in resolved_labels
                 and r["scientificReading"] != "MATERIAL"]
    underpowered = [r["contrastId"] for r in rows if r["frozenUnderpowered"] is True]
    material_wins = [r["contrastId"] for r in nats_rows if r["reportableAsAWin"] is True]

    out = {
        "schema": "MATERIALITY-MAP-ALL-CONTRASTS/1",
        "status": "BUILDER_SUPPORT_PROBE - INTERPRETATION LAYER ONLY",
        "claimBoundary": (
            "This artifact computes NO new science. It re-reads frozen results and attaches the "
            "D10 minimum-effect-size reading. It moves no P-level, alters no frozen verdict and "
            "creates no claim. Duration-only. No holdout mark channel touched."),
        "channel": "DURATION_ONLY - nextStateN/direction/jump never requested (D5)",
        "resolutionFloor": {
            "valueNats": RESOLUTION_FLOOR_NATS,
            "isA": "HALF-width, in nats/event",
            "derivation": (
                "BCa HALF-width of the narrowest frozen B3 contrast: cohort %s, rule %s, model "
                "%s. BCa width 0.08414086126525253 -> half 0.04207043063262626, used as 0.042."
                % FLOOR_SOURCE_CONTRAST),
            "status": ("HEURISTIC. It is NOT a pre-specified equivalence margin, was NOT "
                       "registered before any result, and no verdict in this repository was ever "
                       "decided by it. It describes what the assay can RESOLVE, not what the "
                       "bootstrap will CALL."),
            "supersedes": ("0.064, which came from the mislabelled `width` field - see D7"),
            "unitsFence": ("NLPD nats only. CRPS_normalized and CRPS_seconds rows carry "
                           "resolutionFloor/effectToFloorRatio/scientificReading/"
                           "reportableAsAWin = %s." % NA_UNITS),
            "cohortProvenance": ("derived on cohort %s; rows from primary_states_0_to_8 are "
                                 "flagged floorTransferCaveat=true" % FLOOR_SOURCE_CONTRAST[0]),
        },
        "bcaAvailability": {
            "frozenB3": "bca AND percentile both recorded for all 48 contrasts",
            "fSide": ("PERCENTILE ONLY - the F-side harness computed no BCa. BCaWidth is "
                      "%s for all 6. Not computed, not estimated, not imputed." % NOT_COMPUTED),
            "m4m6m7": ("PERCENTILE ONLY - same harness, same seed. BCaWidth is %s for all 3."
                       % NOT_COMPUTED),
        },
        "counts": {
            "totalContrasts": len(rows),
            "frozenB3": len([r for r in rows if r["source"] == "FROZEN_B3"]),
            "fSide": len([r for r in rows if r["source"] == "F_SIDE_SCORING"]),
            "m4m6m7": len([r for r in rows if r["source"] == "M4_M6_M7_POST_HOC"]),
            "natsRows": len(nats_rows),
            "crpsRowsFloorNotApplicable": len(crps_rows),
        },
        "scientificReadingTallyNatsRowsOnly": tally,
        "frozenVerdictTallyAllRows": verdicts,
        "materialWinsNatsRows": material_wins,
        "d10ClassResolvedButNotMaterial": d10_class,
        "frozenUnderpoweredFlags": underpowered,
        "d7Recheck": {
            "publishedWidthFieldEquals": d7_width_matches,
            "intervalUsedMatches": interval_used_is,
            "note": ("recomputed by subtraction from the frozen `bca`/`percentile` arrays; "
                     "confirms D7 independently of the ledger text"),
        },
        "assayNote": (
            "A large count of sub-floor and inconclusive contrasts is a statement about the "
            "ASSAY, not about the models. 19 holdout motors is the binding limit. An interval "
            "containing 0 is NOT_ESTABLISHED - never 'no difference', never 'equivalent'. "
            "Underpowered is not equivalence. Replicates were not and must not be increased "
            "after seeing a width."),
        "inputs": {
            "b3ResultSha256": sha256_file(B3_RESULT),
            "fSideResultSha256": sha256_file(FSIDE_RESULT),
            "m4m6m7ResultSha256": sha256_file(M467_RESULT),
        },
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "contrasts": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(out, indent=1, sort_keys=True) + "\n"
    OUT.write_text(body, encoding="utf-8", newline="\n")
    print("rows=%d  nats=%d  crps=%d" % (len(rows), len(nats_rows), len(crps_rows)))
    print("readingTally(nats only)=%r" % (tally,))
    print("frozenVerdictTally(all)=%r" % (verdicts,))
    print("materialWins=%r" % (material_wins,))
    print("d10Class(resolved but not material)=%r" % (d10_class,))
    print("underpowered=%d %r" % (len(underpowered), underpowered))
    print("d7 widthField matches=%r  intervalUsed=%r" % (d7_width_matches, interval_used_is))
    print("WROTE %s" % OUT)
    print("sha256=%s" % hashlib.sha256(body.encode("utf-8")).hexdigest())


if __name__ == "__main__":
    main()
