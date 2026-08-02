"""Deterministic seed derivation.

D3_HASH_SEED_NONDETERMINISM
---------------------------
The committed B4 runner seeds C01/C02 with `seed_base + sim + hash(gen) % 100000`, where `gen`
is a generator-name STRING. CPython randomizes `str` hashing per process unless PYTHONHASHSEED
is pinned, so the same command produces different synthetic data on every invocation. Measured
across three consecutive processes for the same two strings:
    14565/95125, 59809/55025, 89866/26054

Any C01/C02 result produced that way would be unreproducible byte-for-byte and could never
satisfy the protocol's own determinism discipline. The defect is latent only because neither
cell has ever been executed.

`stable_seed` replaces it with a SHA-256-derived integer that depends only on declared protocol
inputs, so the same inputs give the same seed in every process regardless of PYTHONHASHSEED.
"""
from __future__ import annotations

import hashlib

SEED_SPACE = 2 ** 32


def legacy_seed(seed_base: int, sim: int, gen: str) -> int:
    """The committed (defective) seeding. Retained ONLY to demonstrate the defect in tests."""
    return seed_base + sim + hash(gen) % 100000


def stable_seed(*, cell_id: str, base_seed: int, replicate_index: int,
                protocol_version: str, cohort_id: str = "") -> int:
    """Process-stable seed derived from declared protocol inputs.

    Property: same inputs -> same integer in any process, any PYTHONHASHSEED, any platform.
    """
    material = "|".join([
        str(cell_id),
        str(base_seed),
        str(replicate_index),
        str(protocol_version),
        str(cohort_id),
    ])
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % SEED_SPACE
