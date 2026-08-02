#!/usr/bin/env python3
"""Verify the separately cached 4.09 GB Ito 2021 raw-trace archive.

This deliberately does not run inside the normal test suite. It is the
repeatable, CPU-only deep verification command for the large external tier.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "experiments" / "upstream-cache" / "ito-2021-raw-data.zip"
OUTPUT = ROOT / "experiments" / "results" / "ito-raw-archive-verification.json"
PUBLIC_OUTPUT = ROOT / "public" / "ito-raw-archive-verification.json"
EXPECTED_BYTES = 4_085_227_742
EXPECTED_MD5 = "d42879e66142ff7190f256f4276db111"


def md5(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    if not ARCHIVE.is_file():
        raise SystemExit(f"Missing external cache: {ARCHIVE}")

    observed_bytes = ARCHIVE.stat().st_size
    observed_md5 = md5(ARCHIVE)
    with ZipFile(ARCHIVE) as archive:
        entries = archive.infolist()
        crc_failure = archive.testzip()
        uncompressed_bytes = sum(entry.file_size for entry in entries)
        compressed_bytes = sum(entry.compress_size for entry in entries)

    passed = observed_bytes == EXPECTED_BYTES and observed_md5 == EXPECTED_MD5 and crc_failure is None
    result = {
        "schema": "uni.flagellum.large-source-verification/1.0.0",
        "studyId": "ITO_2021",
        "artifact": {
            "cachePath": ARCHIVE.relative_to(ROOT).as_posix(),
            "doi": "10.6084/m9.figshare.14371232.v2",
            "downloadUrl": "https://ndownloader.figshare.com/files/27453833",
            "license": "CC BY 4.0",
            "declaredContents": "All manuscript rotation-rate traces",
        },
        "method": {
            "byteCount": True,
            "streamingMd5": True,
            "zipCentralDirectory": True,
            "everyMemberCrc": True,
            "normalTestSuiteRehashesArchive": False,
        },
        "expected": {"bytes": EXPECTED_BYTES, "md5": EXPECTED_MD5},
        "observed": {
            "bytes": observed_bytes,
            "md5": observed_md5,
            "zipEntryCount": len(entries),
            "zipCompressedMemberBytes": compressed_bytes,
            "zipUncompressedMemberBytes": uncompressed_bytes,
            "zipCrcFailure": crc_failure,
        },
        "verifiedAt": "2026-07-17T21:00:00Z",
        "status": "PASS" if passed else "FAIL",
        "claimFence": "This establishes archive identity and integrity, not correctness of every measurement or biological parity.",
    }
    serialized = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    encoded = serialized.encode("utf-8")
    OUTPUT.write_bytes(encoded)
    PUBLIC_OUTPUT.write_bytes(encoded)
    print(json.dumps({"output": str(OUTPUT), "status": result["status"], **result["observed"]}, allow_nan=False))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
