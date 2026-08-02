# The fqdn seam — what is actually true, and the complete solution

**Date:** 2026-07-26 · **Status:** DETERMINED, partially executed · **Occasioned by:** `drift.fqdn_cjs`
**Asked:** *"Doc is wrong? address your uncertain and determine the full and complete solution that will be honest and true and measured"*

This is not a recommendation between two options. It is the measured state and the
end condition. Every number here was produced by a command that can be re-run.

---

## 1. The answer: both are wrong, and the code carries the weight

### The doc is wrong in three separate ways — none of them "the filename"

**A false pointer.** `CLAUDE.md:94` names `viewer/fqdn.cjs` as the single seam for
the repo's strongest law. Verified: `git log --all --diff-filter=A --name-only --
'*fqdn.cjs'` returns only `viewer/hud/fqdn.cjs` @ `ac02bb9`, 2026-07-14. **It has
never existed on any ref.** That file's own line 1 reads *"the helper CLAUDE.md
declares but never existed until now."*

**A superseded scope claim the doc already corrects.** `:93` says *"Every host is a
`<name>.uni-lab.local` DNS name"*. `:108`, fourteen lines later, describes a
two-seam design where `host_resolve.cjs` returns a live **address** for consumers
that cannot use a name. Those are different architectures. `:93-94` entered at
`61765a8` on 2026-07-13; `host_resolve.cjs` was created at `ceacf97` on 2026-07-16
in response to the DHCP-lease incident. **The document contains its own correction
and never back-propagated it.**

**A self-contradiction.** `:95` sanctions static IPs at `infra.cjs:312` and `:23`.
Both hold `10.190.245.121` — the chip's LAN DHCP lease, which `:97` declares *"NOT
DECLARABLE AT ALL (binding)"*. The doc sanctions at `:95` what it forbids at `:97`,
with no recorded reason.

### The code is the larger defect

| measured | value |
|-|-|
| IPv4 literals in code files | **12–16 across 9 files** |
| of those, **dead addresses served live** | **4** (`discovery.cjs:22,23,24`, `overlay_server.cjs:38`) — now fixed |
| `${name}.${zone}` composition sites in `.cjs` | **5**, with **4 distinct failure behaviours** |
| hand-written name sets outside JS | **3** (`infra_registry.json` probe.host ×6, `hub.html:168-173`, `install_lan_cert.ps1:24-30`) |
| production consumers of `viewer/hud/fqdn.cjs` | **0** — `require(.*fqdn` returns 2 hits, both its own test |
| files covered by the only IP-literal fence | **17 of 472 (3.6%)** — `viewer/hud/**`, the subtree with zero production traffic |
| does that fence run in CI? | **No.** `.github/workflows/ci.yml` is Elixir-only and never invokes node |
| mesh `10.13.13.x` / overlay `100.x` literals | **0 across all 472 files** |

**The deciding measurement.** `GET :8090/api/door/state` returns twelve doors. Two
are live-resolved IPs, six are loopback literals, four are null. **Not one href is
`<name>.uni-lab.local`.** The running product emits no FQDNs at all — deliberately,
and gated: `chip-address-tracking` (PASS) exists to prove consumers follow a
*live-resolved* address, and it names `host_resolve.cjs` as "the one seam". It never
mentions `viewer/fqdn.cjs`.

The law works perfectly on the planes that never move and is broken on the plane
that does.

### Therefore both easy moves are wrong

Editing `CLAUDE.md` to describe the status quo would launder 12–16 real violations
and four live dead links into "as designed", **deleting the only artifact currently
telling the truth**. Creating `viewer/fqdn.cjs` would satisfy a grep by writing a
**sixth** composition site with zero consumers on day one — exactly as the fifth has
today — in service of the one file whose subject is a prohibition on convenience
shortcuts.

**The doc correction comes last, after the code it describes is true. That ordering
is the entire ethical content of this answer.**

---

## 2. The law, restated so it is both true and enforceable

> **No address with a shelf life may be recorded anywhere that cannot notice it expired.**

That is what the prohibition is *for*, and it is the version that survives
measurement. *"Use a name"* is one mechanism serving it. *"Resolve a name to an
address at the moment of use, with provenance"* is the other, and it exists because
the first is not available to every consumer class. The law keeps its force; it
stops over-claiming its mechanism.

## 3. Two seams, not one

`viewer/fqdn.cjs` and `viewer/host_resolve.cjs` are **different products, not
duplicates.** Consolidating them would be the wrong answer:

| | name seam | address seam |
|-|-|-|
| returns | `http://colony.uni-lab.local:4000` | `http://10.190.245.121:4000/` |
| shape | sync, pure, no I/O | async, live `getaddrinfo`, 30s TTL cache |
| on unknown name | throws | degrades, `via:"none"` + honest detail |
| provenance | none needed | `via` + ISO timestamp |
| reads `ips[]` | never | yes — the stable-plane fallback |
| lifetime | **permanent** | **narrow, expiring at the `.local` → `.internal` flip** |

The correct relation is a **dependency**, not a merge: `host_resolve.fqdnOf()`
becomes a delegation to the name seam. One *composition* function; two *resolution*
seams. Merging would drag the retiring layer's lifetime onto the permanent one.

**The measured cost of the duplication is not tidiness — it is that four code paths
disagree on failure.** `hud/fqdn.cjs:34` throws; `host_resolve.cjs:54` would emit
`name.undefined`; `gaia_server.cjs:51,53` and `replica_ledger_probe.cjs:43` silently
substitute a hardcoded `"uni-lab.local"`. So the seam needs a non-throwing
`fqdnSafe(name)` alongside `fqdn(name)` — consolidating onto a throwing-only helper
would make Gaia crash where she presently answers, converting a designed tolerance
into an outage.

**Done means:** requirers `0 → ≥5`, inline composition sites `5 → 0`.

## 4. The steps

| # | step | state |
|-|-|-|
| 1 | Adjudicate the resolver split — does CEF resolve `.local`? `host_resolve.cjs:20-27` and `studio_channels.ps1:56-58` make opposed claims, both dated 2026-07-15 | **OPEN** — needs the operator at a browser |
| 2 | Resolver negative control in `verify_host_tracking.cjs` | **OPEN** |
| 3 | **Replace the four dead `.122` literals with live resolution** | **DONE** — `ca35408` |
| 4 | Promote the IP fence repo-wide (472 files), allowlist bootstrap literals in `evidence/bootstrap_literals.json`, wire into CI. **Land it RED** — the failure list is the work queue | **OPEN** — highest value |
| 5 | `git mv viewer/hud/fqdn.cjs viewer/fqdn.cjs` (a **move**, not a new write) + add `fqdnSafe` | **OPEN** |
| 6 | Convert all 5 composition sites to require the seam; delete the two hardcoded zone fallbacks | **OPEN** |
| 7 | Retire the 3 hand-written name sets outside JS | **OPEN** |
| 8 | Fix 3 registry rows declaring unreachable `10.13.13.1` as `ips[0]` | **OPEN** |
| 9 | De-scope the anti-circularity check so non-chip literals must be justified | **OPEN** |
| 10 | Read the DHCP reservation table for THINKER and node2 | **OPEN** — needs host access |
| 11 | Register bootstrap literals with re-derivation path and expiry | **OPEN** |
| 12 | **Correct `CLAUDE.md:93-97` — last** | **OPEN, and deliberately last** |

## 5. Two findings no measurement was looking for

**The LAN resolver hijacks unqualified names.** `nslookup colony.uni-lab.local`
returns AWS registrar-parking addresses because the router (`Linksys00425`,
`10.190.245.188`) appends a `[redacted: client-identifier]` search suffix. Negative control:
`thisnamedoesnotexist99.uni-lab.local` gets the **same positive answer**. The
`getaddrinfo` path is clean — the nonsense name correctly yields `ENOTFOUND`. So
`host_resolve.cjs:57-59`'s choice of `dns.lookup` over `dns.resolve4` is
**measurably load-bearing, not stylistic** — and `infra_registry.json` declares
`10.190.245.188` as `resolver.upstreams[0]`: **the registry declares as an upstream
the resolver doing the hijacking.**

Independently corroborated during this session: `ping node2` resolved to
`node2.[redacted: client-identifier] [76.223.54.146]`.

**Three registry rows declare an unreachable stable fallback.** `dns`, `masterplan`
and `mcp` list `10.13.13.1` as `ips[0]`, and `declaredStable()` returns exactly
`ips[0]`. From THINKER: `ping 10.13.13.1` = 100% loss. THINKER is not a mesh peer —
the registry says so itself in `music`'s `_ips_note`. Found and fixed for `music` on
2026-07-16 and **not propagated**, exactly as with `.122`.

## 6. Adverse, and not buried

`music.uni-lab.local` does not resolve — `ENOTFOUND`, confirmed on the
`getaddrinfo` path. The `chip-names-resolve-via-dns` gate is **RED at exit 1 today**
for that reason, independent of everything above.

## 7. What stays open

Steps 1, 2, 4–12. Step 1 needs a human at a browser; step 10 needs the DHCP server.
**This determination is complete; the work is not**, and the distinction is the
point. One measurement was returned wrong by an agent and corrected on verification
(`caps.cjs`/`collectors.cjs`/`gaia.cjs` were reported as `require`-ing the helper;
they contain the *string* inside the drift collector's own text). Every figure above
was re-verified directly before being written here.
