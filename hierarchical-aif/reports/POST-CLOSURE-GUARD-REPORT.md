# Post-Closure Guard Report

**Date:** 2026-07-22 · **Gate:** H-AIF-G9 · **Context:** all four corrected B4 cells landed; freeze
before commit. This report records the state of every mechanical gate at the freeze point.

---

## 1. Repository state

| check | result |
|-|-|
| all new work under `hierarchical-aif/` | **YES** — `git status --short` shows nothing outside `hierarchical-aif/` (94 entries, all under it) |
| frozen audits drift | **NONE** — `git diff --stat -- audits/` empty; full 250-file sha256 recheck **IDENTICAL** to `frozen-evidence-baseline.sha256` |
| result artifacts missing a sha256 sidecar | **NONE** — all six primary results + two probe outputs + two probe JSONs now carry sidecars; `sha256sum -c` verifies **OK** on all six primary results |
| a template cited as a result | **NONE** — the two templates live under `reports/templates/` with `TEMPLATE, NOT A RESULT` banners; the only match for that banner outside `templates/` is a prose *mention* in `RUN-LANDING-MODE-STATUS.md` |
| a canonical report path containing `<<FILL>>` / template text | **NONE** — all four `B4C##-CORRECTED-FULL-REPORT.md` verified to be real reports, not templates |

## 2. Guard results

| gate | command | result |
|-|-|-|
| **test suite** | `python -m pytest hierarchical-aif/tests/motor_stack_aif -q` | **`501 passed, 2 skipped, 1 xfailed`** |
| **claim guard** | `python …/claim_guard.py reports docs ledgers protocols scripts results` | **`0 violations across 6 paths`** |
| **numeric provenance guard** | `python …/numeric_provenance_guard.py reports docs ledgers protocols` | **`2046 in-scope decimals, 0 failures`** (2 `ANCHORED_OK`, 4 `RECOMPUTED`, rest `MARKED`/`UNANCHORED`) |
| **frozen evidence** | 250-file sha256 recheck vs baseline | **IDENTICAL — NO DRIFT** (receipt `frozen-evidence-recheck-post-closure.sha256`) |

## 3. Result-hash sidecar verification

```
B4C01_CORRECTED_FULL_RESULT.json          : OK   564-… no, 8256cb12…
B4C02_CORRECTED_FULL_RESULT.json          : OK   0633988d…
B4C10_CORRECTED_FULL_RESULT.json          : OK   959a00e9…
B4C11_CORRECTED_FULL_RESULT.json          : OK   564a5b0f…
F_SIDE_MOTOR_STACK_SCORING_RESULT.json    : OK   b3b12720…
M4_M6_M7_PER_MOTOR_CONTRASTS_RESULT.json  : OK   751a59ef…
```

All six verified against their sidecars from the repo root (`sha256sum -c` returned `OK`).

## 4. The two mechanical guards, and what each cannot do

- **`claim_guard`** clamps forbidden *wording*, use/mention aware. **It cannot check whether
  evidence supports a claim, and it cannot check a number.** Passing it is necessary, not sufficient.
- **`numeric_provenance_guard`** (D11) checks *declared* numeric provenance: an anchored number must
  match the artifact field it names. **It does not make numeric provenance decidable in general** —
  `UNANCHORED` numbers are reported, not failed. The failing class is `ANCHORED_MISMATCH`.

Neither guard replaces the adversarial reader. Both are recorded with their scope so that a green
guard is never mistaken for full coverage.

## 5. Verdict

**All gates green. No frozen drift. No out-of-scope change. Every result hashed and verified. No
template cited as a result.** The working tree is in a durable, reviewable state and is ready for
the principal's commit decision.

---

`NEXT_ACT = write hierarchical-aif/reports/CORRECTED-CELL-RESULT-INDEX.md`
