# Claim-Guard Report

**Gate:** H-AIF-G9 · **Run:** 2026-07-21 · **Scanner:** `src/motor_stack_aif/claim_guard.py`

Mechanical clamp on forbidden claim language. A phrase counts as a violation unless it appears in
a negated context or inside a forbidden-wording catalogue.

## Scope

| directory | files scanned | violations |
|-|-|-|
| `hierarchical-aif/reports/` | 11 | **0** |
| `hierarchical-aif/docs/` | 1 | **0** |
| `hierarchical-aif/ledgers/` | 2 | **0** |
| `hierarchical-aif/protocols/` | 2 | **0** |
| `hierarchical-aif/src/` | 8 | **0** |
| `hierarchical-aif/tests/` | 7 | **0** |
| `hierarchical-aif/scripts/` | 2 | **0** |
| **total** | **33** | **0** |

### Excluded, with reason

| file | reason |
|-|-|
| `src/motor_stack_aif/claim_guard.py` | Holds the phrase list as its `FORBIDDEN` data. Self-scanning a dictionary is a definitional false positive. |
| `tests/.../test_claim_guard_forbidden_phrases.py` | Uses the phrases as fixtures to prove the guard fires. |
| `reports/CLAIM-GUARD-REPORT.md` | This file. A report that quotes offending phrases would flag itself, and a FAIL listing would then re-flag on the next run. |

These exclusions are recorded so they are auditable rather than silent. Two self-reference
artifacts were observed while building this guard: an unfiltered scan reported 19 hits (all inside
the guard's own dictionary and fixtures), and a first FAIL report that quoted its findings verbatim
then re-flagged them on the next pass, reporting 124. Both are scanner self-reference, not claims.

## Result: `PASS`

No forbidden claim language in any substantive hierarchical-aif artifact.

22 phrases are clamped.

## Limits

- **Semantic equivalents are not caught.** A document could assert parity in novel wording and pass.
- The negation heuristic inspects 180 characters of left context; a distant negation may be missed,
  and an unrelated nearby negation could mask a real violation.
- The guard checks **wording only**, never whether the evidence supports a claim. Passing is
  necessary, not sufficient; that judgement stays with the reviewer.
