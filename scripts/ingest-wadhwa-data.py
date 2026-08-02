#!/usr/bin/env python3
"""Extract auditable stator dwell events from the Wadhwa et al. raw MATLAB data.

This script performs ingestion only. It does not fit a model or inspect an
experimental outcome. The expected source identity and extraction boundary are
frozen in experiments/preregistration.v1.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import scipy.io


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "experiments" / "preregistration.v1.json"
DEFAULT_OUTPUT = ROOT / "experiments" / "data" / "wadhwa-2022-events.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def partition_for(name: str) -> tuple[str, int]:
    remainder = int(hashlib.sha256(name.encode("utf-8")).hexdigest(), 16) % 5
    return ("holdout" if remainder == 0 else "train", remainder)


def exact_integer(value: float, motor: str, sample_index: int) -> int:
    rounded = round(float(value))
    if not math.isfinite(float(value)) or abs(float(value) - rounded) > 1e-9:
        raise ValueError(f"{motor}: non-integer stator value at sample {sample_index}: {value}")
    return int(rounded)


def runs(states: list[int], times: np.ndarray) -> list[dict]:
    output: list[dict] = []
    start = 0
    for index in range(1, len(states)):
        if states[index] != states[start]:
            output.append(
                {
                    "state": states[start],
                    "startIndex": start,
                    "endIndex": index - 1,
                    "startS": float(times[start]),
                    "eventS": float(times[index]),
                    "durationS": float(times[index] - times[start]),
                    "nextState": states[index],
                    "censored": False,
                }
            )
            start = index
    dt = float(np.median(np.diff(times)))
    output.append(
        {
            "state": states[start],
            "startIndex": start,
            "endIndex": len(states) - 1,
            "startS": float(times[start]),
            "eventS": None,
            "durationS": float(times[-1] + dt - times[start]),
            "nextState": None,
            "censored": True,
        }
    )
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_mat", type=Path, help="Path to data/remodeling_data.mat")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    source = protocol["source"]
    raw_path = args.raw_mat.resolve()
    raw_sha = sha256_file(raw_path)
    if raw_sha.lower() != source["rawSha256"].lower():
        raise ValueError(f"Raw SHA-256 mismatch: expected {source['rawSha256']}, observed {raw_sha}")

    records = scipy.io.loadmat(raw_path, squeeze_me=True, struct_as_record=False)["stoich"]
    start_index = int(protocol["extraction"]["analysisStartIndex"])
    events: list[dict] = []
    motors: list[dict] = []
    exclusions = {
        "leftTruncatedDwells": 0,
        "rightCensoredDwells": 0,
        "outOfRangeDwells": 0,
        "zeroOrNegativeDurationDwells": 0,
    }

    for record in records:
        name = str(record.name)
        full_time = np.asarray(record.t, dtype=float).reshape(-1)
        full_stators = np.asarray(record.stators, dtype=float).reshape(-1)
        if len(full_time) != len(full_stators) or len(full_time) <= start_index + 2:
            raise ValueError(f"{name}: invalid or too-short trace")
        if not np.all(np.isfinite(full_time)) or not np.all(np.isfinite(full_stators)):
            raise ValueError(f"{name}: non-finite source samples")
        if not np.all(np.diff(full_time) > 0):
            raise ValueError(f"{name}: timestamps are not strictly increasing")
        dt = float(np.median(np.diff(full_time)))
        if abs(dt - 0.02) > 1e-6:
            raise ValueError(f"{name}: expected 0.02 s sampling, observed {dt}")

        time = full_time[start_index:]
        stators = [exact_integer(v, name, start_index + i) for i, v in enumerate(full_stators[start_index:])]
        motor_runs = runs(stators, time)
        partition, remainder = partition_for(name)
        motors.append(
            {
                "motorId": name,
                "partition": partition,
                "splitRemainder": remainder,
                "sourceSamples": len(full_time),
                "analysisSamples": len(time),
                "sampleIntervalS": dt,
                "nominalElectrorotationSpeed": int(record.speed),
                "runCount": len(motor_runs),
            }
        )

        for run_index, dwell in enumerate(motor_runs):
            if run_index == 0:
                exclusions["leftTruncatedDwells"] += 1
                continue
            if dwell["censored"]:
                exclusions["rightCensoredDwells"] += 1
            if dwell["state"] < 0 or dwell["state"] > 11:
                exclusions["outOfRangeDwells"] += 1
                continue
            if dwell["durationS"] <= 0:
                exclusions["zeroOrNegativeDurationDwells"] += 1
                continue
            next_state = dwell["nextState"]
            events.append(
                {
                    "eventId": f"{name}:{run_index:04d}",
                    "motorId": name,
                    "partition": partition,
                    "splitRemainder": remainder,
                    "stateN": dwell["state"],
                    "enteredAtS": round(dwell["startS"], 9),
                    "durationS": round(dwell["durationS"], 9),
                    "eventAtS": None if dwell["eventS"] is None else round(dwell["eventS"], 9),
                    "nextStateN": next_state,
                    "direction": None if next_state is None else ("on" if next_state > dwell["state"] else "off"),
                    "jump": None if next_state is None else next_state - dwell["state"],
                    "rightCensored": bool(dwell["censored"]),
                }
            )

    motor_ids = {m["motorId"] for m in motors}
    train_ids = {m["motorId"] for m in motors if m["partition"] == "train"}
    holdout_ids = {m["motorId"] for m in motors if m["partition"] == "holdout"}
    if train_ids & holdout_ids:
        raise AssertionError("Motor-level partition leakage detected")
    if len(motor_ids) != len(motors):
        raise AssertionError("Duplicate motor identifier detected")

    artifact = {
        "schema": "uni.flagellum.observed-events/1.0.0",
        "protocolId": protocol["protocolId"],
        "source": {
            **source,
            "resolvedRawPath": source["rawPath"],
            "observedRawSha256": raw_sha,
        },
        "ingestion": {
            "script": "scripts/ingest-wadhwa-data.py",
            "numpyVersion": np.__version__,
            "scipyVersion": scipy.__version__,
            "analysisStartIndex": start_index,
            "motorCount": len(motors),
            "trainMotorCount": len(train_ids),
            "holdoutMotorCount": len(holdout_ids),
            "eventCount": len(events),
            "uncensoredEventCount": sum(not e["rightCensored"] for e in events),
            "exclusions": exclusions,
        },
        "motors": motors,
        "events": events,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(artifact["ingestion"], indent=2))


if __name__ == "__main__":
    main()
