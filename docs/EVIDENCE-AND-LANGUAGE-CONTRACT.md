# The evidence and language contract

Binding on every signal, citation and surface in the Blanket Builder and the signal inventory.
Set by the operator 2026-08-20. Enforced mechanically by `viewer/verify_signal_inventory.cjs`.

---

## 1. The language contract — why we never write "fact"

> **"science is never done and we never say FACT, we say confirmed observation, and standing
> durable measure with observed evidence."** — the operator, 2026-08-20

This is not decoration. A word like *fact* closes a question that the scientific method holds
open by design; it invites a reader to stop checking. The purpose of these surfaces is the
opposite — to make checking easy, and to restore rather than degrade a reader's grip on how
knowing actually works.

**Permitted vocabulary**

| say this | for |
|---|---|
| **confirmed observation** | something measured, reported, and reproduced or independently corroborated |
| **standing durable measure with observed evidence** | a quantity that has held up across studies/conditions and carries its evidence |
| **reported measurement** | a single source's number, not yet corroborated here |
| **stated mechanism** | what a source asserts happens, in the source's own terms |
| **proposal / interpretation** | a model or reading offered by authors, not a measurement |
| **contested** | sources disagree; both sides carried |
| **not established here** | we have not shown it; the honest null |
| **not measured in this estate** | explicitly absent evidence |

**Forbidden on these surfaces:** `fact`, `proven`, `proves`, `definitive`, `settled science`,
`obviously`, `certainly`, `undeniable`, `the truth is`. The gate greps for these.

**Hedging is preserved, never stripped.** If a source writes "may", "is thought to",
"we propose", those words survive into our quote and into our summary. Removing an author's
hedge is a form of fabrication.

---

## 2. The provenance contract — click-through to the original, every time

The operator's requirement:

> **"If we cite, link to the quote, link the quote to the source, make the source a copy in our
> repo and UI and the source copy MUST fully link to the original source."**

Every signal therefore carries a **four-link chain**, and the UI renders all four:

```
CLAIM  ──▶  VERBATIM QUOTE  ──▶  LOCAL SOURCE COPY  ──▶  ORIGINAL (DOI / publisher URL)
 what we      <=40 words,          mirrored in-repo        the thing itself, so a
 assert       with a locator       where licence allows    reader verifies us
```

**Required fields per signal** (schema `uni.flagellum.signal-inventory/1.0.0`):

- `verbatimQuote` + `quoteLocator` — the exact words, and where in the document they sit
- `apaReference` — **full APA 7**, the citation style a journal, a paper and a non-fiction
  science book all carry
- `doi` / `stableUrl` — the persistent identifier
- `urlFetched` + `retrievedOn` — what was actually retrieved, and when
- `localCopy` — path to the mirrored source in this repo, or `null` with the reason
- `licence` — as stated by the source page
- `fetchStatus` — `FETCHED_AND_READ` · `ABSTRACT_ONLY` · `PAYWALLED` · `FETCH_FAILED`
- `sourceType` — `PEER_REVIEWED` · `REVIEW` · `TEXTBOOK` · `PREPRINT` · `DATABASE` ·
  `PROFESSIONAL_BODY` · `BLOG_OR_POPULAR` · `FRINGE_OR_CONTESTED`

### Mirroring rule — copy what we may, link what we may not

- **Open licence (CC-BY, CC0, public domain, PMC open subset):** mirror the **full text** into
  `docs/sources/` and record the licence. The local copy header links back to the original.
- **All rights reserved / paywalled:** we mirror **only** the metadata and the short quotes we
  rely on (fair dealing for criticism and review), and the entry is marked
  `localCopy: null, reason: "licence does not permit mirroring"`. We never pretend to hold what
  we do not hold.
- Every mirrored file carries a provenance header: source URL, DOI, retrieval date, licence,
  sha256 of the retrieved bytes.

### OPEN GAP, recorded 2026-08-21 — mirroring is NOT yet done

**`localCopy` is populated on ZERO of the 159 signals.** The operator's requirement — *"make the
source a copy in our repo and UI and the source copy MUST fully link to the original source"* — is
**NOT yet satisfied**. The fetch fleet returned metadata and quotes but did not mirror full texts.

Worse, and corrected the moment it was found: the Blanket Builder drawer was rendering
*"not mirrored — licence does not permit"* as a **fallback** on every unmirrored row. That asserted a
licence ruling nobody had made, on 159 rows. It now reads *"NOT MIRRORED — mirroring has not yet been
attempted for this row"*, which is the truth. The one-line lesson: **a fallback string is a claim.**

To close the gap: for each row whose `openAccess` states an open licence (CC-BY, CC0, PMC open
subset), retrieve and mirror the full text into `docs/sources/` with a provenance header, and set
`localCopy`. For the rest, set `localCopy: null` **with the licence text that was actually read**,
not an assumed one.

### The anti-fabrication rule

**A signal may only exist if a source was actually retrieved and read.** Not remembered, not
inferred, not "well-known". An entry with no verbatim quote is not an entry. A failed fetch is
recorded as a failed fetch — an honest negative row is worth more than a confident guess.

**Never guess** a DOI, year, volume, or page. Absent → `null` plus
`"not stated on the fetched page"`.

---

## 3. What we claim, and how we say we are testing it

Every signal and every blanket in the builder answers five questions on its face, because a
claim without these is an assertion, not science:

1. **What we claim** — stated in permitted vocabulary, at the strength the evidence licenses.
2. **Why we claim it** — the quote, the citation, the click-through.
3. **How we are testing it** — the gate, the run, the artifact; or honestly, `NOT YET TESTED`.
4. **Controls** — the negative control, the null model, the comparison that could have come out
   the other way. A claim with no control is labelled `NO CONTROL — reported only`.
5. **Adversarial check** — who tried to break it, and what survived. Includes contradicting
   sources, which are carried side by side and **never reconciled by us**.

---

## 4. Contradictions are evidence, not noise

Where two sources disagree, **both are shown, both are cited, neither is silently dropped**, and
the disagreement is labelled `CONTESTED`. Resolving a contradiction requires new evidence, not
an editorial decision. (This estate already carries live examples: Ito-vs-Wadhwa dwell direction;
the Johnson/Singh attribution conflict.)

Fringe and edge material is welcome **and labelled** `FRINGE_OR_CONTESTED`, and never appears
without the mainstream response beside it. Excluding contested work hides the argument; printing
it unlabelled misrepresents its standing. We do neither.

---

## 5. Why this exists

> *"we have no pride, no ego, no hubris, we are the EFE curiosity turnt up and eager to share
> with the world how to EFE and stay grounded and produce durable science that others can use to
> further their observational learning."* — the operator

A published failure is worth the same as a published success, because both let someone else move.
The provenance chain exists so that a stranger can check us without asking us — and find us
honest, or find us wrong, on the evidence.
