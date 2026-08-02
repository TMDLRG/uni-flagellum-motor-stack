# D12 Successor-Archive — Build & Round-Trip Receipt

**Remediation gate:** `PASS` (this receipt) — the successor archive survived staging and
round-trip scans. **Incident state stays `NEGATIVE` permanently** (see D12 report); a PASS
here means the *forward* package is D5-safe, not that the prior distribution was recalled.

| field | value |
|-|-|
| anchor commit | `8b93cf048e0760000b49ad1b7f6e371abcea1679` |
| package name | `UNI-FLAGELLUM-haif-closure-8b93cf0-D5SAFE.zip` |
| package location | repository parent dir (beside the withdrawn archive) |
| **package sha256** | `386f0e46018865a973c35e81cd3480c5fc8684cc74d1f46e979a09eafa51c6d2` |
| files in package | 82 |
| staged scan | 83 artifacts, 0 findings, 0 unscanned, verdict PASS |
| round-trip scan | 83 artifacts, 0 findings, 0 unscanned, verdict PASS |
| round-trip manifest | staged == unpacked (byte-identical per-file sha256) |
| forbidden content | no `.git`, no `*.bundle`, no `*.patch` |
| supersedes (withdrawn) | `UNI-FLAGELLUM-haif-closure-e21747c.zip` sha256 `7b28f0d6f338cb2fa077d3a84fe9688c44a67cb813e513f27a1a0348113d41b2` `WITHDRAWN_D5_UNSAFE` |
| ancestry | `GIT_ANCESTRY_RECEIPT_PROVIDED; FULL_HISTORY_RECONSTRUCTION_NOT_INCLUDED` |
| transmission | principal-gated — build is authorized, sending is not |

Per-file manifest: `hierarchical-aif/reports/D12-SUCCESSOR-ARCHIVE-MANIFEST-SHA256.txt`.
Rebuild: `python hierarchical-aif/scripts/build_d5_safe_successor_archive.py 8b93cf0`

The build is deterministic (git archive pins contents to the anchor; the zip uses a fixed
timestamp and sorted order), so re-running from the same anchor reproduces the package sha256.
