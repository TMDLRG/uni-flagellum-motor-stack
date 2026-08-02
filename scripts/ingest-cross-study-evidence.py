#!/usr/bin/env python3
"""Build the cross-study flagellar-motor evidence corpus on CPU only.

The script is deliberately an ingestion boundary, not a model fitter. It
verifies immutable upstream bytes, reads cached primary-study workbooks and
MAT files, records independence units, and emits a compact JSON corpus. Large
time series are summarized per motor; source byte hashes retain the route back
to every original sample.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZipFile

import numpy as np
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "experiments" / "upstream-cache"
OUTPUT = ROOT / "experiments" / "data" / "cross-study-motor-evidence.json"
PUBLIC = ROOT / "public" / "cross-study-motor-evidence.json"

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


LOCAL_ARTIFACTS = [
    {
        "id": "ITO_2021_SOURCE_WORKBOOK",
        "file": "ito-2021-source-data.xlsx",
        "bytes": 11896413,
        "sha256": "33687c50a5636817889612d59d7e902b876391997bf7f6013574f8fa2bce944a",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-021-23516-y/MediaObjects/41467_2021_23516_MOESM2_ESM.xlsx",
        "tier": "A",
    },
    {
        "id": "ANTANI_2021_SOURCE_WORKBOOK",
        "file": "antani-2021-source-data.xlsx",
        "bytes": 45271,
        "sha256": "bee5497182be4e7b6c2f1a3bd75a24407ab965512e8652bfe9a6337ffb297abd",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-021-25774-2/MediaObjects/41467_2021_25774_MOESM5_ESM.xlsx",
        "tier": "A",
    },
    {
        "id": "LISEVICH_2025_SOURCE_ARCHIVE",
        "file": "lisevich-2025-source-data.zip",
        "bytes": 45274919,
        "sha256": "7e30c791be8136cc4520e7f897d2ca10d7f88cd2558447dfbe36b393eb641afd",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-56980-x/MediaObjects/41467_2025_56980_MOESM7_ESM.zip",
        "tier": "A",
    },
    {
        "id": "LISEVICH_2025_SUPPLEMENTARY_DATA_1",
        "file": "lisevich-2025-supp-data-1.xlsx",
        "bytes": 13690,
        "sha256": "87186cdc9221ed4249231b82306250f1abe7ab66c7de905d7a88682cc9a03ce8",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-56980-x/MediaObjects/41467_2025_56980_MOESM2_ESM.xlsx",
        "tier": "B",
    },
    {
        "id": "LISEVICH_2025_SUPPLEMENTARY_DATA_2",
        "file": "lisevich-2025-supp-data-2.xlsx",
        "bytes": 14102,
        "sha256": "3d62f6a53876d1fc5c17dfdc05c42c263b7984d1f130cfc05df7ae819cbf1d78",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-56980-x/MediaObjects/41467_2025_56980_MOESM3_ESM.xlsx",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_SOURCE_DATA",
        "file": "mattingly-2026-fig2-source-data.zip",
        "bytes": 15731056,
        "sha256": "6c9c7145ef8aa9485365d863ecd573e0fd4a664d61a2c46929a7a772ce8522cf",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM7_ESM.zip",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_CODE_FIG2",
        "file": "mattingly-2026-supp-code-2.zip",
        "bytes": 402957,
        "sha256": "ccb4ce3c3052110e1ebc345dbb7e4078da04f172efd7191918053f7d1bbaa653",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM2_ESM.zip",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_CODE_FIG3",
        "file": "mattingly-2026-supp-code-3.zip",
        "bytes": 439682,
        "sha256": "16f9ea44aa6ac79e59ae89225b6645c1fe23117bfeb24d1ea6749bf9ba63418a",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM3_ESM.zip",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_CODE_FIG4",
        "file": "mattingly-2026-supp-code-4.zip",
        "bytes": 372370,
        "sha256": "a3ddbaec26b9b5767fdd438f79d7dcea81d5c2f59a83bac804446a8d1cc76dc2",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM4_ESM.zip",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_CODE_FIG5",
        "file": "mattingly-2026-supp-code-5.zip",
        "bytes": 409379,
        "sha256": "b01ea374aec04dd77849181cc56a2c2663fcbe100e5f0f2b16e78e4ec4c7d53a",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM5_ESM.zip",
        "tier": "B",
    },
    {
        "id": "MATTINGLY_2026_CODE_FIG6",
        "file": "mattingly-2026-supp-code-6.zip",
        "bytes": 376804,
        "sha256": "127a3e7688ae33fdf8be1b85d47dd50faf958db5b871e860eeba6913d034fd63",
        "url": "https://static-content.springer.com/esm/art%3A10.1038%2Fs41567-025-03105-2/MediaObjects/41567_2025_3105_MOESM6_ESM.zip",
        "tier": "B",
    },
    {
        "id": "PEREZ_CARRASCO_2022_MODEL_CODE",
        "file": "perez-carrasco-2022-code.zip",
        "bytes": 25093,
        "sha256": "23bded7d444f8c684a7aca95dae7fc9bd06bc07a9c95b42ccb58e213f0543561",
        "url": "https://zenodo.org/records/5784548/files/2piruben/BFM_multistate-v1.0.0.zip?download=1",
        "tier": "B",
    },
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_number(value: Any) -> float | None:
    if isinstance(value, (int, float, np.integer, np.floating)):
        number = float(value)
        return number if math.isfinite(number) else None
    return None


def numbers(values: Iterable[Any]) -> list[float]:
    return [number for value in values if (number := finite_number(value)) is not None]


def summary(values: Iterable[Any]) -> dict[str, float | int | None]:
    clean = numbers(values)
    if not clean:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    return {
        "n": len(clean),
        "mean": float(statistics.fmean(clean)),
        "sd": float(statistics.stdev(clean)) if len(clean) > 1 else 0.0,
        "min": float(min(clean)),
        "max": float(max(clean)),
    }


def column_index(cell_ref: str) -> int:
    match = re.match(r"[A-Z]+", cell_ref)
    if not match:
        raise ValueError(f"Invalid XLSX cell reference {cell_ref}")
    result = 0
    for char in match.group(0):
        result = result * 26 + ord(char) - 64
    return result - 1


def read_xlsx(path: Path, selected: set[str]) -> dict[str, list[dict[int, Any]]]:
    """Read selected XLSX sheets with only Python standard-library XML/ZIP APIs."""
    result: dict[str, list[dict[int, Any]]] = {}
    with ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{{{MAIN_NS}}}si"):
                shared.append("".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t")))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {node.attrib["Id"]: node.attrib["Target"] for node in relationships}
        sheets = workbook.find(f"{{{MAIN_NS}}}sheets")
        if sheets is None:
            raise ValueError(f"No sheets in {path}")

        for sheet in sheets:
            name = sheet.attrib["name"]
            if name not in selected:
                continue
            relation_id = sheet.attrib[f"{{{REL_NS}}}id"]
            target = targets[relation_id].lstrip("/")
            if not target.startswith("xl/"):
                target = f"xl/{target}"
            root = ET.fromstring(archive.read(target))
            parsed_rows: list[dict[int, Any]] = []
            for row in root.findall(f".//{{{MAIN_NS}}}row"):
                parsed: dict[int, Any] = {}
                for cell in row.findall(f"{{{MAIN_NS}}}c"):
                    index = column_index(cell.attrib["r"])
                    kind = cell.attrib.get("t")
                    raw = cell.find(f"{{{MAIN_NS}}}v")
                    if kind == "inlineStr":
                        value: Any = "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
                    elif raw is None:
                        value = None
                    elif kind == "s":
                        value = shared[int(raw.text or 0)]
                    elif kind in {"str", "e"}:
                        value = raw.text
                    else:
                        try:
                            value = float(raw.text or "nan")
                        except ValueError:
                            value = raw.text
                    parsed[index] = value
                parsed_rows.append(parsed)
            result[name] = parsed_rows
    missing = selected - result.keys()
    if missing:
        raise ValueError(f"Missing sheets in {path.name}: {sorted(missing)}")
    return result


def verify_artifacts() -> list[dict[str, Any]]:
    verified = []
    for declared in LOCAL_ARTIFACTS:
        path = CACHE / declared["file"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing upstream artifact {path}")
        actual_size = path.stat().st_size
        actual_hash = sha256(path)
        if actual_size != declared["bytes"] or actual_hash != declared["sha256"]:
            raise ValueError(
                f"Integrity failure for {path.name}: {actual_size}/{actual_hash}, "
                f"expected {declared['bytes']}/{declared['sha256']}"
            )
        if path.suffix.lower() in {".zip", ".xlsx"}:
            with ZipFile(path) as archive:
                bad = archive.testzip()
                if bad is not None:
                    raise ValueError(f"CRC failure in {path.name}: {bad}")
        verified.append({**declared, "cachePath": path.relative_to(ROOT).as_posix(), "verified": True})
    return verified


def ingest_ito() -> dict[str, Any]:
    raw_verification_path = ROOT / "experiments" / "results" / "ito-raw-archive-verification.json"
    raw_verification_bytes = raw_verification_path.read_bytes()
    (ROOT / "public" / "ito-raw-archive-verification.json").write_bytes(raw_verification_bytes)
    raw_verification = json.loads(raw_verification_bytes)
    if raw_verification["status"] != "PASS":
        raise ValueError("Ito raw archive verification did not pass")
    workbook = read_xlsx(
        CACHE / "ito-2021-source-data.xlsx",
        {"Figure 2d", "Figure S3", "Figure S5b", "Figure S8a,d,g", "Figure S8b,e,h", "Figure S8c,f,i"},
    )
    s3 = workbook["Figure S3"]
    motor_names = {index: str(value) for index, value in s3[2].items() if 2 <= index <= 41 and value}
    motor_summaries = []
    for offset, rotation_column in enumerate(sorted(motor_names)):
        motor_id = motor_names[rotation_column]
        stator_column = 44 + 2 * offset
        mean_speed_column = stator_column + 1
        rotation = numbers(row.get(rotation_column) for row in s3[4:])
        occupancy = numbers(row.get(stator_column) for row in s3[4:])
        fitted_speed = numbers(row.get(mean_speed_column) for row in s3[4:])
        motor_summaries.append(
            {
                "motorId": motor_id,
                "rotationHz": summary(rotation),
                "statorOccupancy": summary(occupancy),
                "stepMeanSpeedHz": summary(fitted_speed),
                "traceRows": max(len(rotation), len(occupancy)),
            }
        )

    def rate_bins(sheet_name: str, width_hz: int) -> list[dict[str, Any]]:
        output = []
        for row in workbook[sheet_name][3:]:
            left = finite_number(row.get(1))
            right = finite_number(row.get(2))
            speed = finite_number(row.get(3))
            n_zero = finite_number(row.get(5))
            n_plus = finite_number(row.get(6))
            probability = finite_number(row.get(7))
            probability_se = finite_number(row.get(8))
            binding = finite_number(row.get(9))
            binding_se = finite_number(row.get(10))
            if left is None or right is None or speed is None:
                continue
            output.append(
                {
                    "binWidthHz": width_hz,
                    "leftHz": left,
                    "rightHz": right,
                    "meanSpeedHz": speed,
                    "nZero": n_zero,
                    "nPlus": n_plus,
                    "assemblyProbability": probability,
                    "assemblyProbabilitySe": probability_se,
                    "bindingRatePerSecond": binding,
                    "bindingRateSe": binding_se,
                }
            )
        return output

    def dwell(sheet_name: str) -> list[dict[str, float]]:
        rows = workbook[sheet_name]
        states = numbers(rows[1].get(index) for index in sorted(rows[1]) if index >= 2)
        means = numbers(rows[2].get(index) for index in sorted(rows[2]) if index >= 2)
        errors = numbers(rows[3].get(index) for index in sorted(rows[3]) if index >= 2)
        return [
            {"stateN": int(state), "meanDwellSeconds": mean, "standardErrorSeconds": error}
            for state, mean, error in zip(states, means, errors, strict=True)
        ]

    return {
        "studyId": "ITO_2021",
        "doi": "10.1038/s41467-021-23516-y",
        "organism": "Escherichia coli",
        "tier": "A",
        "unitOfIndependence": "motor/cell",
        "motorCount": len(motor_summaries),
        "rawWorkbookRows": len(s3) - 4,
        "rotationSampleCount": sum(item["rotationHz"]["n"] for item in motor_summaries),
        "statorSampleCount": sum(item["statorOccupancy"]["n"] for item in motor_summaries),
        "motors": motor_summaries,
        "rotationBindingBins": {
            "5Hz": rate_bins("Figure S8a,d,g", 5),
            "10Hz": rate_bins("Figure S8b,e,h", 10),
            "20Hz": rate_bins("Figure S8c,f,i", 20),
        },
        "dwellMeans": {"main": dwell("Figure 2d"), "splitCheck": dwell("Figure S5b")},
        "declaredRawArchive": {
            "doi": "10.6084/m9.figshare.14371232.v2",
            "url": "https://ndownloader.figshare.com/files/27453833",
            "bytes": 4085227742,
            "md5": "d42879e66142ff7190f256f4276db111",
            "license": "CC BY 4.0",
            "contents": "All manuscript rotation-rate traces",
            "cachePath": raw_verification["artifact"]["cachePath"],
            "verificationReportPath": raw_verification_path.relative_to(ROOT).as_posix(),
            "cacheVerification": raw_verification,
        },
    }


def ingest_antani() -> dict[str, Any]:
    sheets = read_xlsx(
        CACHE / "antani-2021-source-data.xlsx",
        {
            "Fig1c_CheYp_empty_vector_vs_Mot",
            "Fig1d_FliM",
            "Fig1e_rotator_stalled",
            "Fig2_speed_CWbias_Nst_groups",
            "Fig4a_adaptation_to_load",
            "Fig4b_CWbias_vs_load",
            "Supplementary Fig 1",
        },
    )

    def two_groups(sheet: str, start: int) -> dict[str, list[float]]:
        rows = sheets[sheet][start:]
        return {"groupA": numbers(row.get(1) for row in rows), "groupB": numbers(row.get(2) for row in rows)}

    torque_rows = []
    for row in sheets["Fig4b_CWbias_vs_load"][2:]:
        values = [finite_number(row.get(index)) for index in range(4)]
        if all(value is not None for value in values):
            torque_rows.append(
                {
                    "torquePnNm": values[0],
                    "kCwToCcwPerSecond": values[1],
                    "kCcwToCwPerSecond": values[2],
                    "cwBias": values[3],
                }
            )

    speed_rows = sheets["Fig2_speed_CWbias_Nst_groups"]
    speeds = {
        "low": numbers(row.get(1) for row in speed_rows[2:]),
        "medium": numbers(row.get(2) for row in speed_rows[2:]),
        "high": numbers(row.get(3) for row in speed_rows[2:]),
    }
    bias_rows = sheets["Supplementary Fig 1"]
    biases = {
        "low": numbers(row.get(1) for row in bias_rows[2:]),
        "medium": numbers(row.get(2) for row in bias_rows[2:]),
        "high": numbers(row.get(3) for row in bias_rows[2:]),
    }
    adaptation_rows = sheets["Fig4a_adaptation_to_load"]
    dynamic = []
    for row in adaptation_rows[3:]:
        time = finite_number(row.get(4))
        bias = finite_number(row.get(5))
        if time is not None and bias is not None:
            dynamic.append({"timeSeconds": time, "meanCwBias": bias})

    chey = two_groups("Fig1c_CheYp_empty_vector_vs_Mot", 2)
    flim = two_groups("Fig1d_FliM", 2)
    rotation_control = two_groups("Fig1e_rotator_stalled", 2)
    return {
        "studyId": "ANTANI_2021",
        "doi": "10.1038/s41467-021-25774-2",
        "organism": "Escherichia coli",
        "tier": "A",
        "unitOfIndependence": "motor/cell",
        "directIndependentUnitLowerBound": len(chey["groupA"]) + len(chey["groupB"]),
        "cheYFluorescence": {"emptyVector": chey["groupA"], "motAB": chey["groupB"]},
        "fliMControl": {"control": flim["groupA"], "deltaMotAB": flim["groupB"]},
        "rotationControl": {"rotating": rotation_control["groupA"], "stalled": rotation_control["groupB"]},
        "statorClassSpeedHz": speeds,
        "statorClassCwBias": biases,
        "torqueSwitching": torque_rows,
        "dynamicLoadAdaptation": dynamic,
    }


def ingest_lisevich() -> dict[str, Any]:
    figure2 = read_xlsx(CACHE / "lisevich-2025-source-data" / "Fig.2.xlsx", {"Figure 2b", "Figure 2c", "Figure 2d", "Figure 2e"})
    flagella_count = []
    for row in figure2["Figure 2b"][1:]:
        values = [row.get(index) for index in range(5)]
        if finite_number(values[3]) is not None:
            flagella_count.append(
                {
                    "strain": values[0],
                    "expressionMean": finite_number(values[1]),
                    "expressionSd": finite_number(values[2]),
                    "flagellaMean": finite_number(values[3]),
                    "flagellaSd": finite_number(values[4]),
                }
            )
    rotation = []
    for row in figure2["Figure 2d"][1:]:
        if finite_number(row.get(1)) is not None:
            rotation.append(
                {
                    "strain": row.get(0),
                    "flagellaCount": finite_number(row.get(1)),
                    "filamentRotationHz": finite_number(row.get(2)),
                    "motorRotationHz": finite_number(row.get(3)),
                    "bodyRotationHz": finite_number(row.get(4)),
                }
            )
    experimental_speed = []
    model_speed = []
    for row in figure2["Figure 2e"][2:]:
        if finite_number(row.get(1)) is not None and finite_number(row.get(2)) is not None:
            experimental_speed.append(
                {"strain": row.get(0), "flagellaCount": finite_number(row.get(1)), "speedUmPerSecond": finite_number(row.get(2))}
            )
        if finite_number(row.get(5)) is not None and finite_number(row.get(6)) is not None:
            model_speed.append(
                {"flagellaCount": int(finite_number(row.get(5)) or 0), "meanSpeedUmPerSecond": finite_number(row.get(6)), "sdSpeedUmPerSecond": finite_number(row.get(7))}
            )
    return {
        "studyId": "LISEVICH_2025",
        "doi": "10.1038/s41467-025-56980-x",
        "organism": "Escherichia coli K-12 and natural isolates",
        "tier": "A",
        "unitOfIndependence": "cell, filament, or biological replicate as declared per assay",
        "directIndependentUnitLowerBound": 106,
        "declaredCounts": {"flagellaCountCells": 106, "flagellaLengthFilaments": [35, 46, 47], "biologicalReplicates": 3},
        "flagellaCounts": flagella_count,
        "rotationRates": rotation,
        "experimentalCellSpeeds": experimental_speed,
        "rftSourcePredictions": model_speed,
    }


def as_list(value: Any) -> list[float]:
    return [float(item) for item in np.asarray(value, dtype=float).reshape(-1)]


def ingest_mattingly() -> dict[str, Any]:
    base = CACHE / "mattingly-2026-fig2-source-data" / "Mattingly_Tu_Source_Data_1"
    fig2 = loadmat(base / "Fig2" / "Fig2B_data.mat", squeeze_me=True)
    p_ne = np.asarray(fig2["P_NeNu"], dtype=float).sum(axis=0)
    source_model = loadmat(base / "Fig5" / "Fig5AB_data.mat", squeeze_me=True)
    yuan = loadmat(base / "Fig5" / "Fig5AB_switching_rates_vs_load_data_Yuan2009.mat", squeeze_me=True)
    bai = loadmat(base / "Fig5" / "Fig5C_switching_rates_vs_CWbias_data_Bai2010.mat", squeeze_me=True)
    zhu = loadmat(base / "Fig4" / "Fig4_Zhu_2024_PRE_data.mat", squeeze_me=True)

    yuan_rows = []
    for index in range(len(yuan["Omega_CW_data"])):
        yuan_rows.append(
            {
                "speedCwHz": float(yuan["Omega_CW_data"][index]),
                "speedCcwHz": float(yuan["Omega_CCW_data"][index]),
                "kCwToCcw": float(yuan["kCW_data"][index]),
                "kCwToCcwLower": float(yuan["kCW_lower"][index]),
                "kCwToCcwUpper": float(yuan["kCW_upper"][index]),
                "kCcwToCw": float(yuan["kCCW_data"][index]),
                "kCcwToCwLower": float(yuan["kCCW_lower"][index]),
                "kCcwToCwUpper": float(yuan["kCCW_upper"][index]),
            }
        )
    bai_rows = [
        {
            "cwBias": float(bai["CWbias"][index]),
            "meanCcwIntervalSeconds": float(bai["T_CCW"][index]),
            "ccwIntervalSe": float(bai["T_CCW_se"][index]),
            "meanCwIntervalSeconds": float(bai["T_CW"][index]),
            "cwIntervalSe": float(bai["T_CW_se"][index]),
        }
        for index in range(len(bai["CWbias"]))
    ]
    zhu_rows = [
        {
            "cellIndex": int(zhu["cellInds"][index]),
            "condition": int(zhu["conditions"][index]),
            "cwBias": float(zhu["CWData"][index]),
            "cwBiasSe": float(zhu["CWData_se"][index]),
            "inferredCheYpUm": float(zhu["Yp_fit"][index]),
        }
        for index in range(len(zhu["CWData"]))
    ]
    return {
        "studyId": "MATTINGLY_TU_2026",
        "doi": "10.1038/s41567-025-03105-2",
        "tier": "B/C",
        "modelCode": {
            "repository": "https://github.com/hhmattingly/GMC_motor_Gillespie",
            "commit": "c3bb92455804fe26e7b99b22c18c2d786be0db71",
            "parameters": {"N": 30, "M": 6, "gamma": 3.5, "beta": 0, "J": 0, "F": 0, "k0": 1},
        },
        "fig2PublishedEngagedMarginal": as_list(p_ne),
        "sourceSwitchingPrediction": {
            "speedHz": [300 * value for value in as_list(source_model["Omegas"])],
            "kCwToCcw": as_list(source_model["kCW"]),
            "kCcwToCw": as_list(source_model["kCCW"]),
        },
        "yuan2009DigitizedSwitching": yuan_rows,
        "bai2010DigitizedIntervals": bai_rows,
        "zhu2024PairedCells": zhu_rows,
        "sourceSimulationScale": {
            "gamma0Transitions": 82308,
            "gamma0DimensionlessDuration": 2500.01718,
            "gamma3_5Transitions": 2582155,
            "gamma3_5DimensionlessDuration": 42453.9359,
        },
    }


def published_aggregate_evidence() -> dict[str, Any]:
    return {
        "francoOnate2025": {
            "studyId": "FRANCO_ONATE_2025",
            "doi": "10.1038/s41598-025-14570-3",
            "tier": "C/D",
            "warning": "Reanalysis of earlier traces. Only aggregate distributions are available here; the paper states that J is an upper estimate and that intercellular variability was assumed insignificant.",
            "ringSize": 13,
            "probabilityByBead": {
                "300nm": [0.12, 0.09, 0.11, 0.15, 0.15, 0.22, 0.13, 0.033, 0, 0, 0, 0, 0, 0],
                "500nm": [0.005, 0.005, 0, 0.01, 0.05, 0.04, 0.17, 0.29, 0.13, 0.13, 0.05, 0.04, 0.06, 0.03],
                "1300nm": [0.01, 0, 0, 0, 0, 0, 0, 0.002, 0.12, 0.14, 0.28, 0.25, 0.18, 0.02],
            },
            "meanAndSdRows": [
                {"condition": "300nm-1", "meanRelativeOccupancy": 0.29, "meanSe": 0.03, "sdRelativeOccupancy": 0.17, "sdSe": 0.02},
                {"condition": "300nm-2", "meanRelativeOccupancy": 0.355, "meanSe": 0.006, "sdRelativeOccupancy": 0.153, "sdSe": 0.011},
                {"condition": "300nm-3", "meanRelativeOccupancy": 0.41, "meanSe": 0.02, "sdRelativeOccupancy": 0.15, "sdSe": 0.02},
                {"condition": "300nm-glycerol", "meanRelativeOccupancy": 0.461, "meanSe": 0.005, "sdRelativeOccupancy": 0.175, "sdSe": 0.007},
                {"condition": "500nm-1", "meanRelativeOccupancy": 0.56, "meanSe": 0.02, "sdRelativeOccupancy": 0.18, "sdSe": 0.02},
                {"condition": "500nm-2", "meanRelativeOccupancy": 0.592, "meanSe": 0.011, "sdRelativeOccupancy": 0.21, "sdSe": 0.02},
                {"condition": "500nm-3", "meanRelativeOccupancy": 0.67, "meanSe": 0.02, "sdRelativeOccupancy": 0.18, "sdSe": 0.04},
                {"condition": "500nm-glycerol", "meanRelativeOccupancy": 0.705, "meanSe": 0.005, "sdRelativeOccupancy": 0.158, "sdSe": 0.005},
                {"condition": "1300nm-1", "meanRelativeOccupancy": 0.74, "meanSe": 0.03, "sdRelativeOccupancy": 0.13, "sdSe": 0.02},
                {"condition": "1300nm-2", "meanRelativeOccupancy": 0.80, "meanSe": 0.03, "sdRelativeOccupancy": 0.153, "sdSe": 0.012},
                {"condition": "1300nm-3", "meanRelativeOccupancy": 0.828, "meanSe": 0.006, "sdRelativeOccupancy": 0.18, "sdSe": 0.04},
                {"condition": "1300nm-4", "meanRelativeOccupancy": 0.826, "meanSe": 0.011, "sdRelativeOccupancy": 0.161, "sdSe": 0.009}
            ],
            "sourceTable": "https://www.nature.com/articles/s41598-025-14570-3/tables/2",
        },
        "nord2017": {
            "studyId": "NORD_2017",
            "doi": "10.1073/pnas.1716007114",
            "tier": "D",
            "beadConditions": [
                {"label": "gamma1300", "beadNm": 1364, "dragPnNmS": 11.4, "recruitedAtStallMean": -0.3, "recruitedAtStallSd": 1.1},
                {"label": "gamma500g", "beadNm": 543, "dragPnNmS": 1.67, "recruitedAtStallMean": 1.0, "recruitedAtStallSd": 1.3},
                {"label": "gamma500", "beadNm": 543, "dragPnNmS": 0.77, "recruitedAtStallMean": 1.7, "recruitedAtStallSd": 1.1},
                {"label": "gamma300g", "beadNm": 302, "dragPnNmS": 0.39, "recruitedAtStallMean": 2.0, "recruitedAtStallSd": 1.4},
                {"label": "gamma300", "beadNm": 302, "dragPnNmS": 0.21, "recruitedAtStallMean": 2.3, "recruitedAtStallSd": 1.8},
            ],
            "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5724282/",
        },
        "perezCarrasco2022": {
            "studyId": "PEREZ_CARRASCO_2022",
            "doi": "10.1126/sciadv.abm0535",
            "tier": "B/D",
            "conditions": {"beadDiametersNm": [300, 500, 1300], "sameMotorAssays": ["steady", "release-from-stall", "resurrection"]},
            "availableArtifact": "Model-comparison code only; raw traces are not present in the archived ZIP.",
            "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC8942351/",
        },
    }


def main() -> None:
    verified = verify_artifacts()
    wadhwa = json.loads((ROOT / "experiments" / "data" / "wadhwa-2022-events.json").read_text("utf-8"))
    wadhwa_motors = len({event["motorId"] for event in wadhwa["events"]})
    ito = ingest_ito()
    antani = ingest_antani()
    lisevich = ingest_lisevich()
    mattingly = ingest_mattingly()
    aggregates = published_aggregate_evidence()
    direct_lower_bound = wadhwa_motors + ito["motorCount"] + antani["directIndependentUnitLowerBound"] + lisevich["directIndependentUnitLowerBound"]

    corpus = {
        "schema": "uni.flagellum.cross-study-evidence/1.0.0",
        "protocolId": "UNI-FLAGELLUM-XSTUDY-001",
        "generatedBy": "scripts/ingest-cross-study-evidence.py",
        "compute": "CPU_ONLY_NO_LLM_NO_GPU",
        "sourceIntegrity": {
            "localArtifacts": verified,
            "wadhwaDerivedEventsSha256": sha256(ROOT / "experiments" / "data" / "wadhwa-2022-events.json"),
            "itoRawArchive": ito["declaredRawArchive"],
        },
        "breadth": {
            "directPrimaryArtifactFamilies": ["WADHWA_2022", "ITO_2021", "ANTANI_2021", "LISEVICH_2025"],
            "attributedStudies": [
                "WADHWA_2022", "ITO_2021", "ANTANI_2021", "LISEVICH_2025", "NORD_2017",
                "PEREZ_CARRASCO_2022", "YUAN_2009", "BAI_2010", "ZHU_2024", "MATTINGLY_TU_2026", "FRANCO_ONATE_2025"
            ],
            "observationScales": ["event/dwell", "single motor", "motor ensemble", "cell propulsion", "population/strain"],
            "directIndependentMotorCellLowerBound": direct_lower_bound,
            "lowerBoundDerivation": {"Wadhwa2022": wadhwa_motors, "Ito2021": ito["motorCount"], "Antani2021": antani["directIndependentUnitLowerBound"], "Lisevich2025": lisevich["directIndependentUnitLowerBound"]},
            "warning": "A lower bound is used to avoid double-counting motors/cells across multiple assays within a study. Time points and transition events are never counted as independent biological units.",
        },
        "studies": {
            "wadhwa2022": {
                "studyId": "WADHWA_2022",
                "doi": "10.1038/s41467-022-33075-5",
                "tier": "A",
                "motorCount": wadhwa_motors,
                "eventCount": len(wadhwa["events"]),
                "dataPath": "experiments/data/wadhwa-2022-events.json",
            },
            "ito2021": ito,
            "antani2021": antani,
            "lisevich2025": lisevich,
            "mattingly2026": mattingly,
            **aggregates,
        },
        "claimFences": [
            "Source-paper predictions are source reproductions, not independent validation.",
            "Published aggregate tables cannot identify motor-to-motor heterogeneity.",
            "No cross-assay parameter is shared unless units and observation operators are commensurate.",
            "No result in this corpus establishes biological Active Inference identity.",
            "The world process, biological mechanism, measurement channel, and inference model remain separate objects.",
        ],
    }
    encoded = json.dumps(corpus, indent=2, sort_keys=True, allow_nan=False) + "\n"
    OUTPUT.write_text(encoded, encoding="utf-8", newline="\n")
    PUBLIC.write_text(encoded, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(OUTPUT), "bytes": OUTPUT.stat().st_size, "sha256": sha256(OUTPUT), "directIndependentLowerBound": direct_lower_bound}))


if __name__ == "__main__":
    main()
