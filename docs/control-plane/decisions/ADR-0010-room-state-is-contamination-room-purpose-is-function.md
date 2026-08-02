# ADR-0010 — Room state is contamination; room purpose is function

- **Status:** PROPOSED — NOT ADOPTED. This document is not in force.
- **Date:** 2026-08-01
- **Deciders:** Michael (operator), Veritas, Custos
- **Subject on `/decide`:** `not_mine[8]` in `evidence/remediation/phase9_plan.json`

## Context

The founding specification asked the control plane to be, in the operator's own words, *"the
operating room … the laboratory … the airlock system … the green room … the clean room, and the
sterile room."*

Five of those six exist and are enforced. `SP.ControlPlane.Room` (`lib/sp/control_plane/room.ex:47`)
declares `@states [:green, :clean, :sterile]` as a strict ladder, with a two-key airlock condition
(`keys_condition/1` — at least two distinct parties, at least one of them an operator) and receipt
plus contamination gates on the sterile crossings. Five tests encode that ladder.

Two are missing: **operating room** and **laboratory**. The obvious move is to add them to `@states`.
That move is wrong, and the reason is worth writing down rather than rediscovering.

**They are not the same kind of thing.** `green → clean → sterile` is a **contamination** axis: what
has been *proved* about a space, in order, each step paid for with keys and receipts. "Operating
room" and "laboratory" are **function** labels: what *happens* in a space. The two axes are
orthogonal, and a single enum cannot carry both:

- *A sterile operating room* would need two values at once, which the enum cannot express.
- Or `:operating_room` would **replace** `:sterile`, and the room would silently stop carrying the
  only fact the ladder exists to carry.

**The function is already held, twice, and better.** ADR-0003 rules that the Control Plane **is** the
lab — laboratory is the body's *identity*, not a state it enters. And `viewer/lab/rooms.cjs` already
models named functional rooms (`the-gate-floor`, `the-pending-gates`, `the-airlock-to-air`) with a
**three-valued door** — `open` / `sealed_by_rule` / `no_door` — which is strictly more informative
about *why* you cannot enter than a fourth state would be.

**And a fourth state is not cheap.** Each state in the ladder carries its own ordering rule, its own
entry conditions, its own receipt kind and its own refusal messages. A fourth without all of those is
decoration; a fourth with all of them invents a contamination step nobody can define.

## Decision

**Do not add a room state. Add a `purpose` field that gates nothing.**

`SP.ControlPlane.Room` gains `@purposes [:floor, :laboratory, :operating_room, :airlock]` and a
`purpose` field defaulting to `:floor`, set at `Room.new/2` and recorded on **both sides** of every
crossing (`prior` and `resulting`). The operator gets the vocabulary he asked for. The contamination
axis stays uncorrupted.

**The field is inert by construction, and a test keeps it that way.**
`test/sp/control_plane/room_purpose_never_gates_test.exs` is a **source scan** over the functions that
decide a crossing — `conditions`, `enter`, `order_condition`, `keys_condition`, `receipt_conditions`,
`all_met`, `in_order`, `not_already`, `known_state`, `next_of` — and fails if any of them so much as
mentions `purpose`. It is a source scan and not a behavioural test on purpose: a behavioural test can
only prove the field does not gate the cases someone thought to write.

It carries its own **negative control**: the same scan logic is run over a copy with `purpose`
injected into `keys_condition/1`, and must catch it. A scan that has only ever been run against a
clean file has proved nothing about itself.

Also asserted: a **state may not be used as a purpose** (`Room.new("x", :sterile)` is refused), two
rooms differing only in purpose face byte-identical conditions, and every room still starts `green`
whatever it is called — naming a room `:operating_room` proves nothing about it.

## Consequences

- The specification's vocabulary is honoured without weakening the ladder.
- A room's function is now in the evidence record, where a reader can see what a space was *for* as
  well as what was proved about it.
- `purpose` can never become a second, undeclared authorization axis — which is the real risk, since
  a label is settable by anyone who can name a room, while a state must be *earned* through keys and
  receipts.
- "Operating room" as a **state** is now a closed question. If a future reader wants it, they must
  first define its contamination meaning and its receipt, and argue with this document.

## Alternatives considered

1. **Add `:operating_room` and `:laboratory` to `@states`.** Rejected: makes an illegal state
   expressible, or drops the contamination fact. See Context.
2. **A second enum, `room_kind`, gating its own conditions.** Rejected: that is exactly the
   undeclared second authorization axis this ADR exists to prevent.
3. **Nothing — document that green/clean/sterile plus ADR-0003 already satisfy the intent.** Rejected
   as the weaker option: the operator asked for the words, the words cost one inert field, and
   refusing them without offering anything reads as a refusal of the request rather than of the
   design.

## Falsifier

**Any transition condition whose result depends on `purpose`.** Concretely: two rooms identical
except for their purpose that receive different `conditions/4` output, or different `enter/4`
refusals. `room_purpose_never_gates_test.exs` fires on exactly this, and its negative control proves
it can.

A second falsifier: a room whose recorded `prior.purpose` and `resulting.purpose` disagree within one
crossing. Purpose is carried, not changed, by a threshold.
