# Views

Rendered from the model in [`workspace.dsl`](workspace.dsl). These Mermaid sources render natively in GitHub, GitLab and most markdown viewers with **no build step**. Edit the text; the picture follows.

If you change a view here, change [`workspace.dsl`](workspace.dsl) too — the DSL is the model of record and these are its projections.

---

## 1. Context — who uses the platform

```mermaid
C4Context
title UNI Platform — system context

Person(michael, "Michael", "Regenerative architect and organic operator. Inside every body. Types go-live personally.")
Person(reviewer, "External reviewer", "Receives evidence packages. Never has write access.")
Person(audience, "Audience", "Public viewers of the science broadcast.")

System(platform, "UNI Platform", "Digital-life research colony plus the broadcast platform that puts it on air.")
System_Ext(streams, "Streaming platforms", "YouTube, Twitch, up to 20 endpoints.")

Rel(michael, platform, "Enters, operates, authors verdicts, stops runs")
Rel(reviewer, platform, "Receives evidence packages")
Rel(platform, streams, "One RTMP stream, fanned out")
Rel(audience, streams, "Watches")
```

---

## 2. Bodies — the container view

Four bodies. None may be collapsed into another. See [ADR-0001](decisions/ADR-0001-four-bodies.md).

```mermaid
C4Container
title UNI Platform — the four bodies and the stacks they govern

Person(michael, "Michael", "Organic operator")

System_Boundary(platform, "UNI Platform") {
  Container(door, "The Door", "launcher.cjs :8090", "BUILT. Admission, release, keys, journey. LAW: a polled read never spawns anything.")
  Container(cp, "The Control Plane", "SP.ControlPlane, root zero-dep app", "PARTLY BUILT. Ledger, GateRow, Command, Drift landed 2026-07-25. Registry, Verdict, Run, Pair, Room, Scene NOT BUILT. No verdict authored yet. THIS IS THE LAB.")
  Container(lab, "The Lab View", "THREE.js on T1000", "NOT BUILT. The immersive room: floor, rooms, airlocks, portals.")
  Container(gaia, "Gaia", "gaia_server.cjs :8096", "BUILT. Projects signals with provenance. LAW: never scores, ranks or authors a verdict.")
  Container(hud, "The HUD", "WPF + JSON :8100", "BUILT. Sees and carries. LAW: never fabricates; unknown renders SYNCING.")

  Container(colony, "Colony world", "Elixir lib/sp + paper.jar :25565", "BUILT. The subject of the science.")
  Container(look, "Overlooker", "LiveView + world.js", "BUILT. The colony's own god-view and blanket monitor.")
  Container(cc, "Colony control center", "command_center.cjs :8098", "BUILT. Vision mixer for one world.")
  Container(enc, "Encoder", "OBS + MediaMTX :1935", "BUILT. One render, one encode.")

  ContainerDb(gates, "Gate ledger", "gates.ndjson", "Append-only. 191 rows. Never edited.")
  ContainerDb(rcpt, "Receipt store", "files + sha256", "Content-addressed. Reproduces each claim.")
  Container(appr, "Approval queue", "uni-approvald", "One human approve or deny per mutating call.")
}

Rel(michael, door, "Crosses once")
Rel(michael, lab, "Works inside, authors, stops")
Rel(michael, hud, "Carries")
Rel(michael, appr, "Co-signs")

Rel(door, cp, "Admits and releases")
Rel(cp, lab, "Compact scene per tick")
Rel(lab, cp, "Explicit verbs only")
Rel(cp, gates, "Appends a row")
Rel(cp, rcpt, "Writes a receipt")
Rel(cp, appr, "Requests co-sign")
Rel(cp, colony, "Starts and stops paired runs")

Rel(gaia, gates, "Projects verbatim")
Rel(gaia, rcpt, "Projects with sha256")
Rel(gaia, door, "Projects register and journey")
Rel(gaia, cp, "Projects the ledger, read-only")

Rel(hud, gaia, "Reads signals")
Rel(lab, look, "Looks through, never reimplements")
Rel(colony, look, "Observer frame per tick")
Rel(cc, enc, "Cuts and takes")
Rel(enc, gates, "")
```

**The one-way rule.** Every arrow into Gaia is a projection. There is no arrow out of Gaia that actuates anything — that is the G-PA fence, enforced by construction: the HTTP surface has no mutating route and no MCP tool is effectful.

---

## 3. Deployment — which body runs where

```mermaid
C4Deployment
title Fleet — deployment of the four bodies

Deployment_Node(chip, "The chip — uni-lab", "10.190.245.122, rootless. Zero broadcast.") {
  Container(colony, "Colony world", "Minecraft + Phoenix FEP brain", "The colony, always. Never on THINKER.")
  Container(look, "Overlooker", "LiveView + world.js", "")
  Container(appr, "Approval queue", "uni-approvald", "")
  Container(flag, "Flagellum project", "Next.js :8790 :8791", "CPU-only build")
  ContainerDb(gates, "Gate ledger", "gates.ndjson", "")
}

Deployment_Node(thinker, "THINKER", "10.190.245.196, NVIDIA T1000. Portable. Captures the colony; hosts none of it.") {
  Container(door, "The Door", ":8090", "")
  Container(gaia, "Gaia", ":8096", "")
  Container(hud, "The HUD", ":8100", "")
  Container(cp, "The Control Plane", "PARTLY BUILT", "")
  Container(lab, "The Lab View", "NOT BUILT", "")
  Container(enc, "Encoder", "OBS + MediaMTX", "")
}

Deployment_Node(node2, "node2 — uni-lab-79740c", "Mesh 10.13.13.3. Fan-out only, no encode, no colony.") {
  Container(relay, "Fan-out relay", "uni-bcast-relay", "")
}

Rel(colony, enc, "Captured over the LAN")
Rel(enc, relay, "One RTMP stream")
```

---

## 4. The evidence spine

Steps 1–6 have no home today. Steps 7–9 already work.

```mermaid
flowchart LR
  A["1 register the gate<br/>before the run<br/>falsifier named"] --> B["2 paired run<br/>exactly one variable<br/>or the result is VOID"]
  B --> C["3 observe<br/>continuous time-series<br/>RCON is the authority"]
  C --> D["4 adversarial review<br/>three perspectives<br/>two of them hostile"]
  D --> E["5 author the verdict<br/>PASS PARTIAL FAIL WITHHELD<br/>never a percent"]
  E --> F["6 write the receipt<br/>commit, artifact, log"]
  F --> G["7 append the row<br/>gates.ndjson<br/>never edited"]
  G --> H["8 Gaia projects it<br/>verbatim plus sha256<br/>decides nothing"]
  H --> I["9 HUD and lab show it<br/>drift shown as two<br/>objects that do not align"]

  subgraph NOHOME ["Control Plane — steps 1-6 still have no home (Registry and Verdict are Phase 3)"]
    A
    B
    C
    D
    E
    F
  end
  subgraph WORKS ["Already works"]
    G
    H
    I
  end
```

---

## 5. Gate lifecycle

```mermaid
stateDiagram-v2
  [*] --> REGISTERED: register before the run, with falsifier
  REGISTERED --> PENDING: awaiting its run
  PENDING --> ADJUDICATED: run complete, verdict authored
  ADJUDICATED --> [*]: row appended, never edited

  state ADJUDICATED {
    [*] --> PASS
    [*] --> PARTIAL: names exactly which sub-claim holds
    [*] --> FAIL
    [*] --> WITHHELD
  }

  note right of REGISTERED
    A verdict without a pre-registered
    gate is refused. Prospectivity is
    decided by the commit graph, never
    by prose.
  end note
```

A gate may be **lowered** on receipts. That is the gate working, not a failure.

---

## 6. Run lifecycle

```mermaid
stateDiagram-v2
  [*] --> DESIGNED
  DESIGNED --> READY: protocol frozen, gate registered
  READY --> RUNNING: explicit operator verb
  RUNNING --> COMPLETE: all planned N reached
  RUNNING --> FAILED_RUN: crash or halt
  RUNNING --> VOID: more than one variable differed
  COMPLETE --> [*]
  FAILED_RUN --> [*]: inspectable, never a scientific negative
  VOID --> [*]: unclaimable, re-run cleanly

  note right of COMPLETE
    actual_n = 0            -> NOT_RUN
    0 < actual_n < planned  -> PARTIAL_NOT_ESTABLISHED
    actual_n > planned      -> OVERRUN, flagged, never silent
  end note
```

---

## 7. Rooms and airlocks

```mermaid
stateDiagram-v2
  [*] --> Outside
  Outside --> Green: open, no key
  Green --> Clean: two keys
  Clean --> Sterile: two keys plus a passing scan
  Sterile --> Outside: contamination check and manifest recompute
  Clean --> Green: two keys
  Sterile --> Clean: two keys

  note right of Sterile
    No receipt, no entry.
    The door stays shut and
    names the missing receipt.
    There is no override path.
  end note
```

---

## 8. Authoring a verdict — sequence

```mermaid
sequenceDiagram
  actor M as Michael
  participant L as Lab view
  participant CP as Control Plane
  participant AP as Approval queue
  participant GL as Gate ledger
  participant G as Gaia
  participant H as HUD

  M->>L: enter the room, inspect the run
  L->>CP: GET /api/cp/state (pure read, spawns nothing)
  CP-->>L: scene, each node carrying truth_class and receipt_ref
  M->>L: author verdict (explicit verb)
  L->>CP: POST /api/cp/verdict/author
  CP->>CP: refuse if no pre-registered gate
  CP->>CP: refuse if more than one variable differed
  CP->>AP: request human co-sign
  AP-->>M: approve or deny
  M-->>AP: co-sign (never own change)
  AP-->>CP: granted
  CP->>GL: append row (never edit)
  CP->>CP: write receipt (commit, artifact, log)
  G->>GL: project row verbatim
  G->>H: signal with provenance
  H-->>M: shows the verdict as recorded
  Note over G: Gaia carries the verdict.<br/>It never authored one.
```

---

## 9. Rendering the truth class

The lab view chooses a **material from the truth class**, not from a style flag. A viewer must read epistemic status from a still screenshot with no text.

```mermaid
flowchart TD
  N["scene node"] --> Q{"has truth_class<br/>and receipt_ref?"}
  Q -->|no| FOG["FOG<br/>walkable, not actionable"]
  Q -->|yes| T{"truth_class"}
  T -->|OBSERVED| O["lit, solid, full shadow<br/>nothing else may look like this"]
  T -->|STRUCTURAL_RECONSTRUCTION| S["solid but visibly rebuilt<br/>seams shown, not smoothed"]
  T -->|REDUCED_MODEL / DERIVED| D["translucent<br/>you see through a calculation"]
  T -->|SIMULATED| R["visibly staged<br/>green-room light follows it"]
  T -->|UNKNOWN / UNVERIFIED| FOG
```

Two rules that stop the room from lying:

1. No frame rate, glow, motion or particle may imply liveness. Liveness renders **only** from a real probe result — a frozen colony looks frozen while every process reports up.
2. Passing a gate renders the named behaviour and nothing more. No material, light or room in this lab can depict awareness, experience or life.

---

## 10. Component view — inside the Control Plane

Rendered from the model: [`generated/structurizr-ControlPlaneComponents.svg`](generated/structurizr-ControlPlaneComponents.svg).

```mermaid
flowchart TB
  subgraph CP["The Control Plane — phases 2 through 6 are BUILT; only the scene is not"]
    REG["Registry · phase 3 · BUILT<br/>registration is the FIRST entry naming the gate"]
    VER["Verdict · phase 3 · BUILT<br/>PASS PARTIAL FAIL WITHHELD PENDING"]
    ANC["Anchor · phase 3 · BUILT<br/>the head a chain cannot hold about itself"]
    STO[("Store · phase 4 · BUILT<br/>append-only, the only module that writes")]
    RUN["Run · phase 4 · BUILT<br/>identity is not the record"]
    PAIR["Pair · phase 4 · BUILT<br/>one differing variable, or VOID"]
    WIT["Witness · phase 5 · BUILT<br/>node2 refuses the writer's key"]
    ROOM["Room + Key · phase 6 · BUILT<br/>two parties, receipts on disk, no override"]
    SCENE["Scene · phase 7<br/>every node carries truth_class"]
    DRIFT["Drift · phase 2 · BUILT<br/>refuses cross-type AT CONSTRUCTION"]
    CMD["Command · phase 2 · BUILT<br/>THE ONLY WRITER"]
    LED[("Ledger · phase 2 · BUILT<br/>append-only, hash-chained")]
    ROW["GateRow · phase 2 · BUILT<br/>validates against the schema"]
  end
  classDef built fill:#e8f4ef,stroke:#0f6e56,stroke-width:2px;
  class DRIFT,CMD,LED,ROW,REG,VER,ANC,STO,RUN,PAIR,WIT,ROOM built;
  REG --> CMD
  VER --> CMD
  RUN --> PAIR
  RUN --> CMD
  ROOM --> CMD
  CMD --> LED
  CMD --> ROW
  DRIFT --> LED
  SCENE --> LED
  ANC --> LED
  STO --> LED
  RUN --> PAIR
  WIT --> STO
```

Everything funnels through `Command`. If a write reaches the ledger without passing it, [ADR-0001](decisions/ADR-0001-four-bodies.md) has been violated.

The twelve green components landed across five phases — Phase 2 at `75e2fc4`, Phase 3 at `8ff5591`, Phase 4 at `e6a0529`, Phase 5 at `915bfbb`, Phase 6 at `d524ad1` — 286 tests in total. `Command` is fenced by a runtime writ type-gate **and** a static scan proving no other module in `lib/` reaches the writer — both mutation-tested, because a static scan cannot fail before its subject exists.

---

## 11. Sequence — a claim becomes evidence

The spine, end to end. Steps 7–9 already work. Of steps 1–6, **registration, the ledger append, the row build and verdict authorship now exist**; running paired, observing and adversarial review do not. This is what building the rest means.

```mermaid
sequenceDiagram
  actor M as Michael
  participant REG as Registry
  participant RUN as Run
  participant PAIR as Pair
  participant VER as Verdict
  participant CMD as Command
  participant LED as Ledger
  participant AP as Approval queue
  participant G as Gaia

  M->>REG: register gate (pass_condition, falsifies_condition)
  REG->>CMD: record registration
  CMD->>LED: append (never edit)
  Note over REG,LED: A verdict with no registered gate is REFUSED.<br/>Prospectivity is decided by the commit graph, not prose.

  M->>RUN: start paired run
  RUN->>PAIR: how many variables differ?
  alt exactly one
    PAIR-->>RUN: ok
  else two or more
    PAIR-->>RUN: VOID — unclaimable, re-run cleanly
  end
  RUN->>CMD: record run identity (code, env, seeds, unix_ns)

  M->>VER: author PASS / PARTIAL / FAIL / WITHHELD
  VER->>VER: refuse a percent score
  VER->>VER: refuse a PARTIAL that does not name its holding sub-claim
  VER->>AP: request the human co-sign
  AP-->>M: approve or deny
  M-->>AP: co-sign (never one's own change)
  VER->>CMD: author
  CMD->>LED: append row + receipt
  G->>LED: project the row VERBATIM
  Note over G: Gaia carries the verdict.<br/>It never authored one.
```

---

## 12. Sequence — the Door admits and releases

```mermaid
sequenceDiagram
  actor M as Michael
  participant D as /door page
  participant L as launcher.cjs :8090
  participant DL as door_lifecycle.cjs
  participant S as the studio

  M->>D: click (a deliberate act)
  D->>L: POST /api/door/open {door:all}
  L->>DL: verb(all, open)
  DL->>DL: append ledger entry (actor, method, prediction)
  DL->>S: bring up, guarded by an OS mutex
  Note over D,S: LAW — a polled READ never spawns anything.<br/>Three independent breakers; any one alone stops a storm.

  D->>L: GET /api/door/journey (pure read, every 3s)
  L-->>D: studio_ready → feature_test → go_live → run_of_show → off_air
  Note over L: The journey OBSERVES. It never actuates.<br/>go_live is typed by hand — no agent can ever do it.
```

---

## 13. Sequence — an airlock, two keys

```mermaid
sequenceDiagram
  actor M as Michael
  participant R as Room
  participant K as Key
  participant CMD as Command
  participant LED as Ledger

  M->>R: request entry to sterile
  R->>K: two keys present, in scope, unexpired?
  alt keys satisfied
    R->>R: execution receipt present?
    alt receipt present
      R->>CMD: record the transition
      CMD->>LED: append
      R-->>M: opened
    else no receipt
      R-->>M: REFUSED — names the missing receipt
    end
  else keys missing
    R-->>M: REFUSED — names which key
  end
  Note over R: There is no override path.<br/>The refusal IS the feature.
```

---

## 14. Sequence — emergency stop, mid-run

```mermaid
sequenceDiagram
  actor M as Michael
  participant L as Lab view
  participant CMD as Command
  participant RUN as Run
  participant LED as Ledger

  M->>L: STOP (reachable from anywhere on the floor)
  L->>CMD: stop {run_id, reason}
  CMD->>RUN: halt
  RUN->>LED: append FAILED_RUN with the reason
  Note over RUN,LED: FAILED_RUN is INSPECTABLE and is NEVER<br/>a scientific negative. Partial output is kept, labelled.
  CMD-->>M: stopped
  Note over M,CMD: Stop is never blocked and never queued behind an approval.
```

---

## 15. Sequence — a drift is surfaced, and who resolves it

```mermaid
sequenceDiagram
  participant G as Gaia
  participant A as side A (live)
  participant B as side B (capture)
  participant M as Michael / Control Plane

  G->>A: read
  G->>B: read
  G->>G: equal = (a.raw === b.raw)   %% a pure byte compare
  G-->>M: drift signal {a, b, relation, equal} — both byte-sets verbatim
  Note over G: Gaia adds NO severity, NO diff-percent, NO judgment.<br/>It reports the disagreement and never resolves it.
  M->>M: decide — is A wrong, or B?
  M->>M: fix the SOURCE, never the comparison
  Note over M: If a drift will not clear, the source is wrong.<br/>Four of the original five CANNOT clear: they compare<br/>unlike kinds. Never edit the collector to force convergence.
```
