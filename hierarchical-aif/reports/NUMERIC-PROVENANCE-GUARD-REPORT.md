# Numeric Provenance Guard Report

**Defect:** D11 - a wording guard cannot check a number. This checks *declared* provenance.

Scanned: hierarchical-aif/reports, hierarchical-aif/docs, hierarchical-aif/ledgers, hierarchical-aif/protocols

| status | meaning | count |
|-|-|-|
| `UNANCHORED` | no source declared (reported, not a failure - see scope note) | 1929 |
| `MARKED` | line carries an explicit status marker | 132 |
| `RECOMPUTED` | declared as recomputed by a named script | 4 |
| `ANCHORED_OK` | declares a source pointer and matches it at display precision | 2 |

**Total in-scope decimals: 2067**

## FAILURES: 0

No number declares a source it does not match.


## Scope, stated honestly

This guard makes **declared** provenance checkable; it does not make numeric provenance decidable in general. `UNANCHORED` is reported and does **not** fail, because reports legitimately carry counts, dates and derived arithmetic, and a guard that fires on everything is a guard nobody reads. The failing class is `ANCHORED_MISMATCH` - a number that names a source and contradicts it, which is exactly the D11 defect. The general control remains an adversarial reader briefed to trace every number.
