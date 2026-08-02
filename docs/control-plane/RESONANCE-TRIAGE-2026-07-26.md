# Resonance triage — 2026-07-26

**Measured, not recalled.** Every line below was produced by a command run today
against the live system. Where I could not measure something, it says so.

Resonance is `CLAUDE.md`'s seven-point consistency condition. This walks each break,
names the file and line, and says what it takes to close it — and who can close it.

**Headline: seventeen breaks. Two are live defects serving wrong answers right now.
One is a security property that was lost today. Three are mine, made today.**

---

## R1 · Source observation and provenance

### 1.1 — THE WITNESS IS COMPROMISED · **severity: highest** · not closable by me

`viewer/gaia/witness.json`, captured 2026-07-26T17:05:09Z:

```
offbox:node2   port_open=true   writer_reachable=TRUE   qualifies_as_witness=false
```

Identified directly rather than inferred — `ssh uni@10.190.245.149 hostname` returns
`uni-lab-79740c`, machine-id `1eeab8064da94079`, holding both `10.190.245.149` and
`10.13.13.3`. **It is node2, and the writer's key works on it.**

node2 was the custodian for exactly one reason: the writer could not write there.
That is gone. The anchor now stands on **git alone — tamper-evident, not
unforgeable.**

Within one session this signal read `corroborated` (03:48) → `blocked_unreachable`
(14:51) → `compromised` (17:05). The vocabulary added in item 7.10 held all three
apart, and `witness.json`'s own `claim_note` predicted it: *"adding the writer's key
to that box would end it silently, which is why it is re-measured on every capture."*
It was not silent.

**To restore:** remove the writer's key from node2's `authorized_keys`, then
re-measure. **Not mine to do** — and note this is the one repair I must not perform,
because a witness I can configure is not a witness.

**Consequence: item 7.7 has lost its premise.** *"An anchor the writer could place
alone would not be a witness"* — I could place it alone right now. 7.7 is blocked on
the key, not on a co-sign.

### 1.2 — The LAN resolver hijacks unqualified names · not closable by me

`nslookup thisnamedoesnotexist99.uni-lab.local` returns AWS registrar-parking
addresses; the router (`Linksys00425`, `10.190.245.188`) appends a `[redacted: client-identifier]`
search suffix. Independently corroborated today: `ping node2` resolved to
`node2.[redacted: client-identifier] [76.223.54.146]`.

`viewer/infra_registry.json` declares `10.190.245.188` as `resolver.upstreams[0]` —
**the registry declares as an upstream the resolver doing the hijacking.**

The `getaddrinfo` path is clean (nonsense name → `ENOTFOUND`), which makes
`viewer/host_resolve.cjs:57-59`'s choice of `dns.lookup` over `dns.resolve4`
**load-bearing, not stylistic.**

**To restore:** a negative-control assertion in `viewer/verify_host_tracking.cjs`, and
an operator decision about the router's search suffix.

---

## R2 · Declared variables, units, assumptions

### 2.1 — `CLAUDE.md:93-97` is false three ways · mine to draft, yours to rule

Fully worked in [`FQDN-SEAM-DETERMINATION.md`](FQDN-SEAM-DETERMINATION.md). In short:
`:94` names `viewer/fqdn.cjs`, which **has never existed on any ref**; `:93`'s scope
claim is corrected by `:108` fourteen lines later and never back-propagated; `:95`
sanctions the exact literal `:97` calls *"NOT DECLARABLE AT ALL (binding)"*.

**Deliberately last** — step 12 of 12. Correcting the doc first would launder the
code violations below into "as designed".

### 2.2 — `infra_registry.json:5` says the resolver is planned; it has run for 14 days

`"kind": "dnsmasq (planned)"`. Live: `dns.uni-lab.local` state `tracking`, dnsmasq
answering since 2026-07-12 (receipt `production/docs/receipts/dns_phase0_4_2026-07-12.md`).
Same object, `"mdns_foundation": "avahi serves uni-lab.local today"` is false —
`production/dns/README.md` says mDNS cannot answer the unicast queries that were
answered.

### 2.3 — Three registry rows declare an unreachable stable fallback

`dns`, `masterplan`, `mcp` list `10.13.13.1` as `ips[0]`, and
`host_resolve.declaredStable()` returns exactly `ips[0]`. From THINKER `ping
10.13.13.1` is 100% loss — THINKER is not a mesh peer, which the registry says
itself in `music`'s `_ips_note`. Found and fixed for `music` on 2026-07-16 and
**never propagated** — the same non-propagation as `.122`.

### 2.4 — `music.uni-lab.local` does not resolve · **adverse, standing**

`ENOTFOUND` on the clean path. `chip-names-resolve-via-dns` is **RED at exit 1
today**, independent of everything else here.

---

## R3 · Implementation and deterministic runtime state

### 3.1 — TWO LIVE USES OF A DEAD ADDRESS · **mine to fix, no ruling needed**

`10.190.245.122` died on 2026-07-16 when the chip's lease moved to `.121`.
Walked every one of the 33 IP literals in code. Ten carry `.122`; **eight are
comments recording a past fix and are correct. Two are live:**

| file:line | line | why it matters |
|-|-|-|
| `viewer/diag_dns.ps1:9` | `$chip = "10.190.245.122"; $ctrl = ...` | **the DNS diagnostic points at the dead host.** A diagnostic that tests the wrong address is worse than none — it will report DNS broken when it is fine |
| `viewer/launch_channels.ps1:18` | `Launch 'https://10.190.245.122/glass/' 'ch_glass'` | opens a browser window at a dead host every studio launch |

### 3.2 — Two comments contradict the code beside them

| file:line | comment says | code does |
|-|-|-|
| `viewer/infra.cjs:304` | *"Query the chip's dnsmasq DIRECTLY (10.190.245.122)"* | `:312` `setServers(["10.190.245.121"])` |
| `viewer/apply_nrpt.ps1:14` | *"routes ... to 10.190.245.122"* | `:32` default `"10.190.245.121"` |

The code is right and the prose is stale. This is resonance point 2 against point 3
in its purest form, and it is how `.122` survived: a reader checking the comment
concludes the system is wrong, or trusts the comment and repeats the dead address.

### 3.3 — The IP fence covers 3.6% of its jurisdiction and CI never runs it

`viewer/hud/tests/hud_no_ip_test.cjs` scopes to `viewer/hud/**` — 17 of 472 files,
the one subtree with zero production traffic — and is invoked only from
`viewer/hud/package.json:10`. `.github/workflows/ci.yml` is Elixir-only and never
calls node.

**A law with no detector over 96.4% of its jurisdiction is enforced by memory, and
memory is what let `.122` rot in four places for ten days.**

**Design note the fence must respect, discovered by measurement:** a blanket scan
would flag `viewer/discovery.cjs:27` and `viewer/overlay_server.cjs:38` — **my own
comments from today documenting the removal.** Use versus mention, for the fifth time
in this programme. The fence must distinguish a literal in code from a literal in
prose recording its death, or it convicts the fix.

---

## R4 · Prospective prediction and later observation

### 4.1 — Five drift comparisons cannot converge in any repository state

Accepted as [ADR-0002 Amendment 1](decisions/ADR-0002-gaia-projects-never-computes.md).
Measured live: `fqdn_cjs` compares a prose line to a filename; `gate_row_schema_path`
a prose fragment to a path; `resolver_planned` a 17-byte label to a 21-row JSON array;
`self_caps_doc_vs_served` a CAPS blob to 54 KB of markdown; the three
`replica_ledger` signals compare an LF-hashed digest to a CRLF-hashed one — **equal
is unreachable even at zero lag.**

The two well-formed comparisons — `control_plane_anchor_git` and
`git_dirty_vs_clean` — both went `equal: true` today when the world became correct.
That contrast is the proof.

**To restore:** the collector repairs, each with a mutation proving it still bites
(Amendment 1, Decision 8). Co-signed; not yet executed.

### 4.2 — The replica lag needs its own never-converging signal

`drift.deploy_ref_behind_head.<build>`, relation `lag`, not `equal`. Today the three
replica signals conflate *"a deployment is behind"* (normal, deliberate, from an
immutable pushed ref) with *"a deployed ledger was edited in place"* (the only thing
worth alarming on). Splitting them makes the second the only tamper tripwire on a
deployed ledger anywhere on the platform.

---

## R5 · UI truth badge and label

### 5.1 — `docs/GAIA.md` is stale in eleven places · mine to fix

Seven manifest rows and four prose claims, including two that are severity items
rather than typos: `:222` documents a probe path that `caps.cjs:218` records as
**already corrected on 2026-07-16**, and `:227` narrates a resource the registry
declares `roadmap` as slice **live (colony)**. Signal count reads 85; live is 330.
Seat list omits `organic-operator` and `control-plane` and carries a `relay` seat
that does not exist.

`docs/GAIA.md:11`, `:190` and `caps.cjs:12` claim the table is machine-rendered.
`gaia.cjs:222`'s `toMarkdown()` exists but nothing writes that path.

### 5.2 — The Gaia process served an 8-signal seat from a 10-signal file · **CLOSED today**

Restarted 2026-07-26T17:0xZ. 319 → 330 signals. An entire **`control-plane` seat of
9 signals had never been served** — seven ledger entries, the anchor, the witness
capture. For Phases 3–7 the Control Plane was invisible in Gaia while it was being
built.

---

## R6 · Gate criterion, result, uncertainty, limitation

### 6.1 — Three phase plans claim they were never executed · mine to fix

`PHASE-1.md`, `PHASE-2.md`, `PHASE-4.md` all read `PRE-REGISTERED, NOT EXECUTED`
while their `-RESULTS.md` files exist and read `EXECUTED`. Only 3, 5 and 6 were ever
flipped. UNI TRACK reads these live and reports them faithfully.

### 6.2 — `PHASE-7-RESULTS.md` and `PHASE-8.md` do not exist

`PHASE-7.md` §7: *"Phase 7 is complete only when `PHASE-8.md` exists, is committed,
and is pre-registered in this same form."* Items 7.0–7.6, 7.9 and 7.10 are green;
7.7 is blocked (§1.1), 7.8 stands, 7.11 is in progress.

### 6.3 — Not a break, checked and cleared

The ledger tally reads `PASS 122 / PARTIAL 12 / PENDING 69 / FAIL 3` over **206
rows** and `92 / 4 / 12 / 1` over **109 unique gates**. Those are the same ledger
counted two ways — all rows versus latest-per-gate honouring `supersedes`. **No
drift.** Recorded because it looks like a discrepancy and is not.

---

## R7 · Report, reproduction command, artifact hash

### 7.1 — A committed receipt was not reproducible from its own commit · **CLOSED today**

`phase7_item76_green_2026-07-26.txt` at `98a76a0` carried a warning line only an
**uncommitted** file could emit. Closed by `9de87b4`; recorded in
`phase7_item76_receipt_correction_2026-07-26.md`; the receipt itself was **not
edited**. Standing procedure now records `git status --short` inside every receipt.

### 7.2 — `mix format --check-formatted` fails repo-wide on `lib/sp/brain/language.ex`

Item 7.8, standing since Phase 3. Carried, not buried — the reformat must be its own
commit on its own terms.

---

## What closes what

**Mine, no ruling needed** — §3.1 (2 live dead-address uses), §3.2 (2 stale
comments), §5.1 (GAIA.md), §6.1 (3 phase statuses), §6.2 (results + Phase 8),
§2.2/§2.3 (registry declarations).

**Mine, co-signed, not yet executed** — §4.1 and §4.2 (collector repairs under
Amendment 1, each with a bite-proving mutation), §3.3 (the repo-wide fence, landed
red, with the use-versus-mention rule above).

**Not mine** — §1.1 the writer's key on node2, and with it item 7.7. §1.2's router
suffix. §2.4 is a real host that does not exist.

**Ordering, and it is doing work:** the code corrections come before the document
corrections, everywhere. Editing a document to match a broken world closes the only
signal telling the truth. That ordering is why `CLAUDE.md:93-97` is step 12 of 12 and
not step 1.
