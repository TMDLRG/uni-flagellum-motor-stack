# Architecture audit — claims checked against the running system

**Executed 2026-07-25.** Method: every factual claim in `ARCHITECTURE.md`, `workspace.dsl` and `views.md` checked against a **live read**, never against another document. Per [`NEXT-SESSION-BRIEF.md`](NEXT-SESSION-BRIEF.md) Task 1.

**Falsifier for this audit:** any statement in the architecture that cannot be traced to a live read or a named `file:line`.

---

## Result: one error class, three sites. Everything else confirmed.

| claim | architecture said | live | verdict |
|-|-|-|-|
| Gaia signal population | **305** | **308** | **CORRECTED** — 2 sites in `ARCHITECTURE.md`, 1 in `workspace.dsl` |
| Gaia drift signals | 8 | 8 | confirmed |
| Gaia provenance-incomplete | 0 | 0 | confirmed |
| Gaia seats | incl. `organic-operator`, excl. `relay` | matches | confirmed |
| ledger rows / unique | 195 / 109 | 195 / 109 | confirmed |
| ledger tally | 92 PASS · 4 PARTIAL · 1 FAIL · 12 PENDING | identical | confirmed |
| Door port + verbs | `:8090`, open/close/state/journey | identical in `launcher.cjs` | confirmed |
| Door journey states | 5, `studio_ready`→`off_air` | identical in `door_journey.cjs` | confirmed |
| body ports up | 8090, 8096, 8100 | all UP by socket connect | confirmed |
| Control Plane | NOT BUILT | `lib/sp/control_plane` absent | confirmed |

> **Superseded 2026-07-25, later the same day.** The Control Plane row above was true when this audit ran and is left as the record. Phase 2 landed `Ledger`, `GateRow`, `Command` and `Drift`; the body is now **PARTLY BUILT**. See [`phases/PHASE-2-RESULTS.md`](phases/PHASE-2-RESULTS.md). The `mix test` count quoted below (554) likewise predates the 61 tests Phase 2 added; live is 615.

| `ui/` contract | amended, reads-only + submit | `ui/mix.exs:26-42` | confirmed |
| `SP.*` modules | as listed | `lib/sp/*.ex` matches | confirmed |

### The one error, and its cause

`305 signals` was correct when written. I then added three `drift.replica_ledger.*` signals, updated the **drift count** to 8, and left the **total** at 305. A stale number I created myself, in the same session, hours apart.

This is the fourth instance of the same failure mode in this project: **a number recorded once and not re-read.** The first three are in [`RESUME.md`](RESUME.md). The pattern is not carelessness about any single fact — it is treating a written number as evidence. It is exactly what [ADR-0002](decisions/ADR-0002-gaia-projects-never-computes.md) exists to prevent, applied to my own prose rather than to a gate.

**Mitigation now in place:** UNI TRACK reads all of these live on every request and caches none of them. A number in prose that disagrees with TRACK is wrong by construction, and TRACK is the thing on screen.

## Not verified, and why

| item | status | reason |
|-|-|-|
| HUD internals (`:8100`) | `NOT_VERIFIED` | loopback-only by design; the socket answers but the JSON surface was not read this pass |
| Colony UI (`:4000`) | **DOWN** — confirmed | the colony is deliberately down for a generative-model rebuild |
| chip replica ledgers | confirmed DIFFERS ×3 | expected: they are older deployments, and nothing on them is absent from canonical |

## Verification run

`verify_gaia` **12 PASS / 0 FAIL** · `gaia_lint` **0 violations** · `mix compile --warnings-as-errors` clean · `mix test` **554 tests, 4 doctests, 0 failures** · `mix.exs` **unchanged** · `mc_test.exs` **untouched** (user-owned) · `replica_ledger_probe` re-captured 3 replicas · all 5 C4 views re-rendered from the model.
