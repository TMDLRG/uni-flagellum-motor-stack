# UNI hierarchical stack builder - implementation plan

## 0. Scope statement (read first)

**What this builder is.** A general, CPU-only, deterministic construction and falsification instrument for hierarchical discrete active-inference models. A *stack* is an ordered set of levels `ell = 0..L`; each level owns a categorical hidden state `x_ell`, an outcome `o_ell`, policies `pi_ell`, and the parameter block `{A, B, C, D, E, gamma, Pi}`. The engine minimises a per-level variational free energy `F` bottom-up, scores expected free energy `G` and acts top-down, and passes typed messages across each seam. The flagellar-motor loop that already exists in `lib/uni-motor.js` becomes the first fully-instantiated level (`L0`), migrated by wrapping, not rewriting. The instrument is usable by a child through a typed-brick interface and by a researcher through the same artifact at a higher disclosure level.

**What this builder is not.**

- It is **not** a claim that the L0–L12 human ladder exists. Exactly one level is built. Levels L1–L12 ship as **NOT_BUILT**: no parameters, no sockets, no numbers, no contribution to any total. Adding them to a stack must leave the built levels' trace hash bit-identical.
- It is **not** a general active-inference solver. Policies are **single-step** in v1 (`G` is scored over one transition). Multi-step policy trees are explicitly out of scope and are named as an open question.
- It does **not** define a hierarchical joint `p(x_0..x_L, o)`. Downward messages modulate a child's *parameters*; they are not a generative prior over the child's state. Consequently **cross-level aggregation of `F` is forbidden by the engine** — there is no `sumF` across levels, because there is no quantity such a sum would bound.
- It does **not** establish prospectivity in the browser. The browser may emit `TIMING_UNVERIFIED` or `PENDING` only. `PROSPECTIVE` is minted exclusively by the existing git-DAG oracle in `tests/semantic/prospectivity-provenance.test.mjs`.
- It carries **no usability evidence**. The child path is a hypothesis with a stated falsifier, recorded `NOT_ESTABLISHED` in the gate ledger.
- It changes no existing science. `lib/uni-motor.js`, `lib/duration-models.js`, `lib/source-first-passage.js` are not edited in Phases 1–9. The 11 catalog entries migrate under a byte-equality gate.

**Verification status of this document.** The design body below was produced by a design-and-judge pass that executed no test, gate or build; all PASS/FAIL statuses it cites are read from committed report JSON, not from a fresh run, and anything the designers could not corroborate is marked NOT VERIFIED inline.

Four load-bearing premises were subsequently **confirmed by direct execution** during the Phase-E audit (see [docs/audit/PHASE-E-WORKBENCH-AUDIT.md](audit/PHASE-E-WORKBENCH-AUDIT.md)) and may be relied on:

| Premise | Status | Evidence |
|---|---|---|
| `--cyan`, `--gold`, `--void`, `--failure` are used but never declared in `app/globals.css` | **CONFIRMED** | 21 `var()` references; zero `--name:` declarations; `:root` declares 16 other tokens |
| `transitionPrior` and `policyTerms` are module-private in `lib/uni-motor.js` | **CONFIRMED** | absent from the module's `export` list |
| The shipped `G` is `KL + 2·ambiguity + effort`, not `KL + ambiguity + effort` (`lib/uni-motor.js:328`) | **CONFIRMED** | independent rederivation; on the real model `G` is inflated 60.7–62.5 %, and `G(RUN) − G(TUMBLE)` is inflated 6.5× (0.030642 → 0.004678), so the error **changes action selection** |
| `X01_SOURCE_INTEGRITY` renders `PASS` with 0 of 12 declared artifacts present on disk | **CONFIRMED** | `experiments/upstream-cache/` does not exist; all 12 `verified` fields are frozen `true` literals |

The third premise has a direct consequence for **Phase 2 acceptance criterion 4** and for the `EFE_UNIMOTOR_LEGACY_V1` brick: the legacy brick must be registered as a **deliberately preserved non-canonical form** with its discrepancy printed on the card, not as an alternative convention. `EFE_RISK_AMBIGUITY` is the canonical brick. Migration parity for the legacy brick must be asserted against the *current* shipped output so that correcting `lib/uni-motor.js:328` is a visible, gated, separately-reviewed change rather than a silent drift.

---

## 1. Architecture

Four layers, strictly one-directional in dependency.

```
  app/stack-builder/*.tsx        presentation only; no arithmetic, no RNG, no accumulator
        |  reads frozen StackState records
  lib/stack/scheduler.js         ticks, phases, mailbox, trace hashing
        |
  lib/stack/level.js  bus.js  experiment.js  scoring.js
        |
  lib/stack/{numeric,hash,rng,truth,ports,expr,bricks}.js    pure kernel, zero deps
```

Governing decisions, each traceable to a judged flaw:

1. **Kernel first, but demoable at Phase 4.** Correctness lives where numbers are made and is falsified by `node --test` before pixels exist. To avoid four invisible phases, Phase 4 ships a headless ASCII CLI that prints the ladder with live `F`/`G`.
2. **The type system is the truth contract.** Ports carry `{kind, dim, unit, truthClass}`. `Nats` and `Joules` are distinct kinds with distinct geometry and **no conversion function anywhere**. Truth-class is never a settable field; it is a join over inputs, and `OBSERVED` has exactly one mint point.
3. **One product, three disclosure levels.** A single `detail: "play" | "lab" | "audit"` prop, identical DOM. **Correction to the lego-first design, per the truth-safety judge:** truth class, species label, NOT-BUILT status and unit suffix render at *every* level, in child words if necessary. Only symbols, hashes and the gate ledger are progressive.
4. **Run is a method on the Experiment for scored results; `tick` is a method on the Stack for exploration.** This repairs the science-first flaw where a child's only reachable verdict was `INCONCLUSIVE`. Exploration is free, reversible and immediate; only *scored* results require the falsification apparatus.
5. **Prospectivity is delegated, never minted locally.** The holdout is unreachable before sealing (a throwing Proxy); the seal is a content hash; the ordering witness is git.

---

## 2. Data model

All artifacts are JSON, LF-only, key-sorted on write, and content-addressed by SHA-256 over the canonical serialisation with the hash field itself removed. Numbers use plain `number[]` (dims ≤ 32), deep-freezable, matching house style.

### 2.1 Port type

```ts
// lib/stack/types.d.ts
export type PortKind =
  | "Simplex" | "Matrix" | "MatrixStack" | "Scalar" | "Obs" | "Act"
  | "Nats" | "Joules" | "MsgUp" | "MsgDown" | "Inert";
export type PortShape =
  | "round" | "cross" | "cross-stack" | "square" | "hex" | "tri"
  | "round-notch" | "square-notch" | "up" | "down" | "none";
export type TruthClass =
  | "OBSERVED" | "MODELED" | "DERIVED" | "INFERRED"
  | "FROZEN_PREDICTION" | "NOT_BUILT";

export interface PortType {
  kind: PortKind;
  shape: PortShape;               // derived, frozen per kind
  dim: number | null;
  unit: string;                   // "prob" | "nat" | "J" | "s" | "uM" | "rpm" | "pN.nm" | "1"
  constraint: "column-stochastic" | "probability" | "nonneg" | "positive" | null;
  truthClass: TruthClass;
}
```

Truth-class ordering, weakest first: `NOT_BUILT < FROZEN_PREDICTION < INFERRED < DERIVED < MODELED < OBSERVED`. `joinTruth(...)` returns the **weakest** input class. There is exactly one rule; the science-first design carried two contradictory ones and this resolves it: *any* operation over inputs returns the weakest input class, so `ln(o)` for `OBSERVED o` is `OBSERVED`, and the moment a `MODELED` parameter participates the result is `MODELED`. Provenance narrowing ("derived from observation") is expressed by `sourceBinding`, not by demoting the class.

### 2.2 Level

```jsonc
{
  "schema": "uni.stack.level/1.0.0",
  "id": "L0.motor",
  "index": 0,                       // ell; MUST equal array position for role LEVEL
  "role": "LEVEL",                  // "LEVEL" | "WORLD" | "ANALYSIS"
  "title": "Flagellar motor switch",
  "playTitle": "The tiny motor",
  "built": true,
  "truthClass": "MODELED",          // computed = weakest over seated bricks; not user-settable
  "tauTicks": 1,                    // integer >= 1
  "eventTrigger": null,             // null | { "kind": "XI_EXCEEDS", "threshold": 2.5 }
  "stateLabels": ["falling", "flat", "rising"],
  "obsLabels":   ["falling", "flat", "rising"],
  "policyLabels": ["RUN", "TUMBLE"],
  "sockets": {
    "SEE":    { "brickId": "OBS_WORLD_SENSOR",      "params": {}, "enabled": true },
    "THINK":  { "brickId": "BAYES_CATEGORICAL",     "params": {}, "enabled": true },
    "EXPECT": { "brickId": "GENERATIVE_AB",         "params": { "A": [[/*3x3*/]], "B": [[[/*2x3x3*/]]] }, "enabled": true },
    "WANT":   { "brickId": "PREFERENCE_CDE",        "params": { "C": [-2.81,-1.43,-0.36], "D": [0.15,0.35,0.50], "E": [0.5,0.5] }, "enabled": true },
    "SURE":   { "brickId": "PRECISION_FIXED",       "params": { "gamma": 4, "Pi": [1,1,1] }, "enabled": true },
    "DO":     { "brickId": "EFE_UNIMOTOR_LEGACY_V1","params": { "effort": [0.02,0.07] }, "enabled": true }
  },
  "upMap":   { "mode": "PRIMITIVE", "primitive": "up_q_eps_pi_F" },
  "downMap": { "mode": "PRIMITIVE", "primitive": "down_C_from_parent_q" },
  "parentId": null,
  "childIds": [],
  "sourceBinding": {
    "kind": "NONE",                 // "NONE" | "FROZEN_REPORT" | "SOURCE_PINNED"
    "path": null, "sha256": null, "field": null, "protocolId": null, "citation": null
  },
  "domain": { "species": null, "scale": "single motor",
              "validity": "TENTATIVE" },
  "refutation": {
    "authored": false,
    "falsifier": "Held-out mean log score does not exceed the coin-flip adversary beyond its 95% paired interval.",
    "againstArm": "ADVERSARY_COIN_FLIP",
    "threshold": { "metric": "logScoreNatsPerEvent", "direction": "GREATER", "value": 0 }
  },
  "notes": "",
  "contentHash": "sha256:..."
}
```

Validator rules with named error codes:

| Code | Rule |
|---|---|
| `LEVEL_INDEX_MISMATCH` | `levels[i].index !== i` for `role: "LEVEL"` |
| `NOT_BUILT_CARRIES_NUMBERS` | `built:false` and any socket non-null or any numeric param present |
| `NOT_BUILT_TRUTHCLASS` | `built:false` and `truthClass !== "NOT_BUILT"` |
| `OBSERVED_WITHOUT_SOURCE_PIN` | `truthClass === "OBSERVED"` and `sourceBinding.kind !== "SOURCE_PINNED"` or `citation === null` |
| `NOT_COLUMN_STOCHASTIC` | any column of `A` or of any `B[pi]` off simplex by > 1e-12 |
| `DIM_MISMATCH` | any param shape disagreeing with `stateLabels`/`obsLabels`/`policyLabels` |
| `GAMMA_NONPOSITIVE`, `PRECISION_NONPOSITIVE`, `TAU_NOT_POSITIVE_INTEGER` | as named |
| `MISSING_REQUIRED_SOCKET` | `built:true` with a null required socket |

Note the single `EXPECT` socket carries **both** `A` and `B` as one `GENERATIVE_AB` brick. This repairs the lego-first schema flaw where `A` and `B` were separate bricks competing for one socket.

### 2.3 Stack

```jsonc
{
  "schema": "uni.stack.stack/1.0.0",
  "stackId": "S_MOTOR_V1",
  "title": "One motor deciding",
  "playTitle": "The swimming bacterium",
  "levels": [ /* Level[], index-ascending; role ANALYSIS last */ ],
  "seams": [
    { "lowerId": "L0.motor", "upperId": "L1.dwell",
      "upPrimitive": "up_q_eps_pi_F",
      "downPrimitive": "down_C_from_parent_q" }
  ],
  "worldBinding": { "kind": "SYNTHETIC_WORLD", "module": "lib/uni-motor.js", "symbol": "stepWorld" },
  "observationBinding": {
    "module": "lib/uni-motor.js", "symbol": "observeWorld",
    "permittedFields": ["ligandUm","receptorActivity","motorSpeedRpm","rotation","loadPnNm","pmfMv"]
  },
  "seed": 20260721,
  "dtS": 0.05,
  "replayGuarantee": "ENGINE_ONLY",  // "FULL" for FROZEN_EVIDENCE stacks
  "parents": ["sha256:..."],
  "createdAtUtc": "2026-07-21T09:00:00Z",   // EXCLUDED from stackHash
  "authorNote": "",                          // EXCLUDED from stackHash
  "stackHash": "sha256:..."
}
```

`seams` is **per-seam**, not one global coupling pair — this repairs the lego-first dimensional impossibility where a single `{up, down}` had to type-check against heterogeneous levels.

`permittedFields` is the machine-readable Markov boundary; the runtime deletes every other key and freezes the record, so `trueGradient`, `stators`, `methylation` can never reach an agent.

### 2.4 Messages — the exact seam contract

```ts
export interface UpPayload {          // ell -> ell+1
  q: number[];            // approximate posterior over x_ell, simplex
  eps: number[];          // o - A q, outcome-space residual, unit "prob"
  Pi: number[];           // sensory precision actually in force, positive
  xi: number[];           // Pi .* eps
  F: number;              // unit "nat"; per-level only, never summed across levels
  complexity: number;     // KL[q||prior], nat
  accuracy: number;       // E_q[ln p(o|x)], nat
  uncertainty: number;    // H[q], nat
  viability: number | null; // [0,1] or null when no homeostatic brick is seated
}
export interface DownPayload {        // ell+1 -> ell
  C: number[] | null;     // log preferences, nat, unnormalised
  D: number[] | null;
  E: number[] | null;
  gamma: number | null;
  Pi: number[] | null;
  APrior: number[][] | null;
  BPrior: number[][][] | null;
  gate: number[] | null;  // inhibition in [0,1] per state
}
export interface Message {
  schema: "uni.stack.message/1.0.0";
  direction: "UP" | "DOWN";
  fromLevelId: string; toLevelId: string;
  fromIndex: number; toIndex: number;
  postedTick: number; deliverTick: number;   // ALWAYS postedTick + 1
  kind: "PAYLOAD" | "ABSENT";
  payload: UpPayload | DownPayload | null;   // null iff kind === "ABSENT"
  truthClass: TruthClass;
  receipt: { producedBy: string; nodeHash: string; payloadHash: string };
}
```

Three hard rules, each with a mutation cell:

1. `direction === "UP"` requires `fromIndex < toIndex`; `direction === "DOWN"` requires `fromIndex > toIndex`. `post()` throws `MESSAGE_DIRECTION_VIOLATION` otherwise.
2. `deliverTick === postedTick + 1` in **both** directions. The one-tick latch is what makes level iteration order provably irrelevant. It is a **declared modelling choice** and is rendered in the level card's MATH pane: *"messages arrive one tick later; this level is responding to what its neighbour saw last tick."*
3. **Down-message persistence.** `runState.effective[ell]` holds the last received `DownPayload` and **persists until replaced**. This repairs the science-first flaw where a `tau=8` child discarded its parent's message on 7 of 8 ticks. Node `parameters` are never mutated in place, so a saved stack always replays identically.

`eps` and `xi` are **declared honestly** as predictive-coding diagnostics with no variational status in a categorical model. They are carried in the up-payload because they are the most legible seam quantity, and the level card labels them `diagnostic, not part of F`. This is a preserved disagreement with the pure variational formulation, not a silent import.

### 2.5 Run, Variant, Experiment

```jsonc
// experiments/results/stack/<runId>.run.json
{
  "schema": "uni.stack.run/1.0.0",
  "runId": "sha256:...",              // sha256(stackHash + "|" + seed + "|" + ticks + "|" + armId)
  "stackHash": "sha256:...", "seed": 20260721, "ticks": 2000,
  "engineVersion": "1.0.0", "nodeVersion": "v25.x", "replayGuarantee": "ENGINE_ONLY",
  "partial": false,                    // true if any stepLevel() was used -> unscorable
  "prospectivity": "TIMING_UNVERIFIED", // browser may ONLY emit this or "PENDING"
  "sealHash": "sha256:...",
  "perLevel": [
    { "index": 0, "levelId": "L0.motor", "inert": false,
      "firedTicks": [0,1,2], "F": [0.431,0.402], "G": [[2.71,2.93]] }
  ],
  "notRunLevels": [ { "index": 6, "levelId": "L6.perception", "reason": "NOT_BUILT" } ],
  "traceHash": "sha256:...",
  "adverseFindings": []               // append-only; never shortened
}
```

```jsonc
// experiments/stacks/<slug>/variants/<variantId>.json
{
  "schema": "uni.stack.variant/1.0.0",
  "variantId": "v_random_action", "label": "Just guess",
  "role": "TREATMENT" | "CONTROL" | "ABLATION" | "ADVERSARY" | "NEGATIVE_CONTROL" | "CHEATING_CONTROL" | "BASELINE_PARENT",
  "parentHash": "sha256:...", "childHash": "sha256:...",
  "ops": [ { "op": "set", "path": "/levels/0/sockets/DO/brickId", "value": "ACTION_RANDOM" } ]
}
```

`path` is a restricted pointer: `/levels/<i>/sockets/<SOCKET>/params/<paramId>`, `/levels/<i>/sockets/<SOCKET>/brickId`, `/levels/<i>/sockets/<SOCKET>/enabled`, `/levels/<i>/tauTicks`, `/seed`. Anything else — notably `/__proto__`, `/constructor`, `/levels/<i>/truthClass` — is rejected by `applyOps` with `ILLEGAL_OP_PATH`. **Truth class is not reachable by any op.**

```jsonc
// experiments/designs/<EXP_ID>.experiment.json
{
  "schema": "uni.stack.experiment/1.0.0",
  "experimentId": "E_MOTOR_POLICY_ABLATION_V1",
  "question": "Does expected-free-energy policy selection beat a coin flip on held-out dwell prediction?",
  "prereg": {
    "claim": "...", "falsifier": "...", "authored": true,
    "primaryRule": "meanHeldoutLogScoreNatsPerEvent",
    "secondaryRule": "CRPS",
    "decisionThreshold": { "direction": "GREATER", "value": 0, "onInterval": "LOWER_95" },
    "stoppingRule": "fixed 2000 ticks; no peeking; no re-seeding",
    "committedAgainstCommit": null
  },
  "arms": [ /* {armId, role, variantId} */ ],
  "holdout": { "source": "experiments/results/observed-experiment-report.json",
               "partition": "holdout", "unitField": "motorId" },
  "seeds": [1,2,3,4,5,6,7,8,9,10],
  "variantOf": null,
  "contentHash": "sha256:..."
}
```

---

## 3. Engine API

All files pure ESM, no dependencies, `.d.ts` sibling for each, house style of `lib/source-first-passage.js`.

### `lib/stack/hash.js`
```js
export function canonicalJson(value): string       // keys sorted, LF, toPrecision(17), -0 -> 0, throws on NaN/Infinity
export function sha256Hex(bytesOrString): string   // hand-written, synchronous, Node === browser
export function contentHash(value): string         // "sha256:" + sha256Hex(canonicalJson(stripHash(value)))
```

**Differential gate, per the truth-safety judge:** every truth guarantee in this design reduces to this one function, so `tests/stack/hash-differential.test.mjs` compares `sha256Hex` against `node:crypto` over 20 000 seeded random byte strings of length 0–4096 (covering the 55/56/64-byte padding boundaries), not merely NIST fixed vectors.

### `lib/stack/numeric.js`
```js
export const EPSILON = 1e-12;
export function normalize(v): number[]
export function softmax(v): number[]
export function entropy(p): number
export function klDivergence(p, q): number
export function crossEntropy(p, logQ): number
export function matVec(M, v): number[]
export function isColumnStochastic(M, tol = 1e-12): boolean
```
These **re-export or delegate to** `lib/uni-motor.js`'s already-tested `normalize` (:20), `softmax` (:26), `entropy` (:31), `klDivergence` (:38) wherever semantics match, so the kernel cannot drift from the pinned implementations.

**Removed from the design:** the hand-rolled `fp.js` (`exp`/`ln` minimax polynomial). Two judges independently flagged it: it costs 2–3 days, adds a new numerical-correctness surface whose failure silently corrupts every `F` and `G`, and buys a cross-engine claim that is void anyway because `lib/uni-motor.js:139-198` uses `Math.exp`/`Math.sin`. The replay guarantee is scoped to **a pinned Node version and engine build**, declared in `Run.replayGuarantee` and printed in the UI. This is a deliberate downgrade of a claim, recorded here as such.

### `lib/stack/rng.js`
```js
export function u32(seed, streamId, counter): number         // splitmix32 over (seed ^ hash32(streamId)) + counter
export function unitFloat(seed, streamId, counter): number
export function sampleCategorical(p, seed, streamId, counter): number
```
Counter-based and stateless: a pure function of its arguments, never of call order. This is what makes the scheduler-permutation determinism test a real falsifier rather than a tautology.

### `lib/stack/truth.js`
```js
export const TRUTH_ORDER = ["NOT_BUILT","FROZEN_PREDICTION","INFERRED","DERIVED","MODELED","OBSERVED"];
export function joinTruth(...classes): TruthClass            // returns the WEAKEST
export function bindObserved(value, sourceBinding, resolver): { value, truthClass: "OBSERVED", sourceBinding }
export function isObservedMintable(sourceBinding): boolean
```
`bindObserved` is the **only** mint point for `OBSERVED`. It requires:
- `sha256Hex(canonicalJson(value)) === sourceBinding.sha256`;
- `sourceBinding.citation !== null`;
- `resolver.classify(sourceBinding.path) === "FROZEN_REPORT_DIR"`.

`resolver` is injected: under Node it is a filesystem resolver rooted at `experiments/results/`; **in the browser it is a manifest resolver** over `SOURCE_PIN_MANIFEST`, a build-time-generated frozen allowlist of `{path, sha256, field}` triples emitted by `lib/stack/source-pins.js`. This closes the kernel-first hole where the directory constraint had no browser meaning. A pin absent from the manifest throws `SOURCE_PIN_NOT_IN_MANIFEST`.

No exported function anywhere in `lib/stack/` accepts a `truthClass` argument for computed state. That absence is itself gated.

### `lib/stack/ports.js`
```js
export function canConnect(plug: PortType, socket: PortType): { ok: boolean, code?: string, childMessage?: string }
export function portsRegistry(): PortType[]                  // enumerable, for the exhaustive gate
```
Four checks: `kind` equal; `dim` equal; `unit` equal; `joinTruth(plug, socket)` must not *raise* the socket's class. Codes: `KIND_MISMATCH`, `DIM_MISMATCH`, `UNIT_MISMATCH`, `TRUTH_UPGRADE_REFUSED`, `LEVEL_ORDER`, `CYCLE`.

**The anti-cast gate is not a name grep** (the lego-first version was defeatable by renaming). It is exhaustive over the brick registry: for every registered brick and every (input, output) pair, assert no signature maps a `Joules`-kinded input to a `Nats`-kinded output or vice versa. Adding a brick with such a signature turns the gate red regardless of what it is called.

### `lib/stack/level.js`
```js
export function validateLevel(spec): Violation[]
export function freeEnergyAt(q, prior, logLikelihood): { F, complexity, accuracy }
export function fPass(spec, prevLevelState, observation, effectiveDown, ctx): FResult
export function gPass(spec, qNow, effectiveDown, ctx): GResult
```

**F pass.**
```
prior      = (tick === 0) ? D : matVec(B[pi*], q_prev)
logLik[x]  = SUM_o  obsWeight[o] * ln A[o][x]          // obsWeight = the observed outcome vector
q*         ∝ prior .* exp(logLik)                       // exact categorical minimiser
F          = KL[q* || prior] - E_{q*}[logLik]           // = complexity - accuracy, nats
oPred      = A q* ;  eps = obsWeight - oPred ;  xi = Pi .* eps
```

**Correction to kernel-first, per the mathematical-correctness judge:** `Pi` is **removed from the likelihood**. Raising `A` to the power `Pi` produces an unnormalised tempered pseudo-likelihood, so the reported `F` would no longer bound `-ln p(o)` and the identity test would be circular. In v1, `Pi` is carried in the up-message, used to weight `xi` for display and for the `up` map, and used by `PRECISION_GATED_SENSE` (a SEE-socket brick that mixes the observation toward uniform *before* it enters the likelihood, which is a normalised and declarable operation). `Pi` does not enter `F`. This is stated in the level card's MATH pane.

**G pass.**
```
per policy pi:
  qX   = matVec(B[pi], q*)
  qO   = matVec(A, qX)
  risk      = crossEntropy(qO, C) - entropy(qO)          // = KL[qO || softmax(C)]
  ambiguity = SUM_x qX[x] * entropy(A[:,x])
  G(pi)     = risk + ambiguity                            // gScoring "RISK_AMBIGUITY"
  G(pi)     = risk + 2*ambiguity + effort[pi]             // gScoring "UNIMOTOR_LEGACY_V1"
qPi = softmax(ln E - gamma * G)
```

Both scorings ship as named constants. `UNIMOTOR_LEGACY_V1` reproduces `lib/uni-motor.js:318-328`, where `informationGain = entropy(qOutcome) - ambiguity` is subtracted from a form already containing `ambiguity`, giving `KL + 2*ambiguity + effort`. It is the **default for the migrated L0** and is pinned bit-for-bit. A gate asserts the two scorings **differ**. The level card shows a chip: `G scoring: UNIMOTOR_LEGACY_V1 — ambiguity weight 2 (lib/uni-motor.js:326-328)`. Migrating the default is a separate, prospectively-predicted change, not a side effect of building this.

`horizon` does **not** appear in the schema. Single-step policies are the declared v1 semantics; there is no field implying a depth the engine does not implement.

### `lib/stack/bus.js`
```js
export function post(bus, message): Message[]        // throws MESSAGE_DIRECTION_VIOLATION
export function deliver(bus, tick): { up: Record<string, Message>, down: Record<string, Message> }
export function absentMessage(direction, fromId, toId, tick, reason): Message
```

### `lib/stack/scheduler.js`
```js
export function createRunState(stack, { seed, ticks }): RunState
export function activeLevels(stack, runState, tick): number[]
export function tick(runState, stack, env): RunState          // returns a NEW frozen state
export function runTicks(runState, stack, env, n): RunState
export function stepLevel(runState, stack, levelId): RunState // sets runState.partial = true
export function resetRun(stack, seed): RunState
export function traceHash(runState): string
export function replay(run): { ok: boolean, traceHash: string }
```

**Tick semantics, exactly:**

1. `env.world = worldBinding.step(world, lastAction, controls, dtS)` — only when a `WORLD` node exists.
2. `o_0 = observationBinding.observe(...)`; keys outside `permittedFields` deleted; record `Object.freeze`d.
3. `L = activeLevels(...)`, computed against `tick` **before** any pass runs. A level is active iff `built === true` **and** (`tick % tauTicks === 0` **or** its `eventTrigger` fired last tick).
4. **F phase**, ascending `ell` over `L`: `fPass(spec, prev, obs, runState.effective[ell], ctx)`; then `post(up)` with `deliverTick = tick + 1`.
5. **G phase**, descending `ell` over `L`: `gPass(...)`; then `post(down)` with `deliverTick = tick + 1`; record `runState.actions[ell]`.
6. Mailbox swap: messages with `deliverTick === tick + 1` become readable next tick. `runState.effective[ell]` is **updated only when a down-message arrives**, and otherwise persists.
7. `runState.tick += 1`; every returned state and every nested array is frozen.

**Order independence.** Because all reads are from the previous tick's mailbox and the RNG is counter-keyed, permuting the iteration order over active levels cannot change `traceHash`. This is gated with 20 seeded permutations.

**Run controls, one function each — the UI has no other way to advance state:**

| Control | Call | Scorable? |
|---|---|---|
| Step (one tick) | `tick(...)` | yes |
| Step this level | `stepLevel(..., levelId)` | **no** — sets `partial: true` |
| Run 10 / 100 / 1000 | `runTicks(..., n)` | yes |
| Run one level for N of its own periods | `runTicks` on a *derived stack* with other `tauTicks` set to `Infinity` — a real stack with its own hash, never a hidden mode | yes |
| Reset | `resetRun(stack, seed)` — regenerated, not restored, which is itself a determinism check | n/a |
| Run all arms | `runExperiment(...)` | the only path producing a verdict |

`scoreRun` throws `PARTIAL_RUN_CANNOT_BE_SCORED` on any run with `partial: true`. Hand-stepping is exploration and can never become evidence.

**NOT-BUILT participation.** A `built:false` level is never in `activeLevels`, has all-null parameters by validation, and emits `{kind:"ABSENT"}` in both directions. A built level whose seam input arrives `ABSENT` enters status `STARVED`: **all numeric fields null**, `absentReason: "UPSTREAM_ABSENT:<id>"`, and it does **not** fall back to its own `D`. This repairs the lego-first behaviour where a level downstream of a hole still published `F = 0.4213 nat`. Every reducer throws `NULL_COERCION_REFUSED` on a null. There is no `sumF` across levels at all (see §0).

### `lib/stack/experiment.js`, `lib/stack/scoring.js`
```js
// experiment.js
export function validateExperiment(exp): Violation[]     // refuses missing CONTROL / ADVERSARY / NEGATIVE_CONTROL / CHEATING_CONTROL
export function sealExperiment(exp, holdoutHandle): SealedExperiment
export function runExperiment(sealed, env): RunRecord
export function makeHoldoutProxy(evidence): Proxy        // every get throws HOLDOUT_SEALED until sealed
export function applyOps(stack, ops): Stack              // restricted pointer whitelist
export function verifyVariant(parent, variant): { ok, reason }

// scoring.js
export function logScore(prediction, outcome, scaleSeconds): number   // nats/event; requires Jacobian
export function crps(survivalFn, outcome, grid): number
export function pairedDelta(armA, armB, unitIds, { resamples, seed }): { mean, interval95, nUnits }
export function assertUnitIsNotFrame(unitField): void     // throws UNIT_IS_FRAME on /frame|tick|time|index|row/i
export function recoverParameters(stack, trueParams, seeds): RecoveryReport
export function verdict(prereg, primary, secondary, recovery, refutation): Verdict
```

`verdict()` emits **both** rules plus a first-class `rulesAgree`; the UI may print the word "better" only when they agree. It downgrades to `INCONCLUSIVE` with an explicit reason on: `PARAMETER_NOT_RECOVERABLE` (95% coverage < 0.80), `REFUTATION_NOT_AUTHORED`, `PARTIAL_RUN`, `CHEATING_CONTROL_DID_NOT_WIN`.

---

## 4. Math authoring

Three mechanisms. **No `eval`, no `new Function`, no dynamic `import()`, no string `setTimeout`** — enforced by a source scan over `lib/stack/**` in the test suite.

### 4.1 Typed parameter forms (default; the only way `A/B/C/D/E/gamma/Pi` are edited)

Editing is **projection-based**, so an invalid state is unreachable rather than merely rejected:

```js
// lib/stack/edit.js
export function setSimplexEntry(vector, index, value): number[]   // redistributes remainder proportionally
export function setColumn(matrix, colIndex, vector): number[][]   // per-column simplex projection
export function clampParam(spec, value): number | number[]
```

- `Simplex(k)` — k draggable bars; every drag re-normalises visibly. A child sees conservation happen.
- `Matrix(k,k,COLUMN)` — one column per source state; column header reads *"if it was FALLING, where does it go next?"*
- `MatrixStack` — one grid per policy with a policy selector.
- `C` — nats, unnormalised **log** preferences, edited through a 5-notch want-o-meter mapping to `[-4,-2,0,2,4]`. Log-preference `C` is invariant to an additive constant under `KL[qO||softmax(C)]`, so the migrated `C = ln normalize([0.06,0.24,0.70])` from `lib/uni-motor.js:317` is exact.
- `gamma`, `Pi` — positive log-scale sliders with unit chips.

### 4.2 LEGO primitives (the brick palette)

Each brick is a named pure function with a declared port signature, a `playName`, a `playSentence`, an `equationPlain`, a `truthClass` and a pinning test. `lib/stack/brick-registry.js` exports `BRICK_REGISTRY`; a stack naming an unregistered brick fails validation with `UNKNOWN_BRICK`.

**Six sockets, printed on every baseplate, identical from L0 to L12:**

| Play label | Socket | Formal content |
|---|---|---|
| WHAT I SEE | `SEE` | `o` |
| WHAT I THINK | `THINK` | `q(x)` |
| WHAT I EXPECT | `EXPECT` | `A`, `B` |
| WHAT I WANT | `WANT` | `C`, `D`, `E` |
| HOW SURE | `SURE` | `gamma`, `Pi` |
| WHAT I DO | `DO` | `pi`, `a` |

**v1 palette (24 bricks):**

```
SEE     OBS_WORLD_SENSOR ("Look at the world")        wraps observeWorld
        OBS_INSTRUMENT_FRAME ("Read the machine")     wraps instrumentObservation
        OBS_FROM_UP_MESSAGE ("Listen to below")       o_{ell+1} = g_up(...)
        OBS_REPLAY_FROZEN ("A real thing we measured") requires SourcePin; OBSERVED collar
        PRECISION_GATED_SENSE ("Squint")              mixes o toward uniform by Pi, normalised
        OBS_ORACLE_CHEAT ("Peek at the answer")       CHEATING_CONTROL only; permanently badged

THINK   BAYES_CATEGORICAL ("Weigh the guesses")       exact categorical minimiser
        HOLD_BELIEF ("Never change your mind")        identity; ablation
        POSTERIOR_FROZEN ("Decide once, forever")     adversary

EXPECT  GENERATIVE_AB ("Because / Then")              A and B together
        DURATION_M0_EXPONENTIAL .. M3_MIXTURE         wrap lib/duration-models.js
        FIRSTPASSAGE_DLT                              wraps lib/source-first-passage.js

WANT    PREFERENCE_CDE ("What I want / Start / Habit")
        PREFERENCE_FROM_DOWN ("Do what I'm told")

SURE    PRECISION_FIXED ("Sure")
        PRECISION_FROM_DOWN ("Be as sure as I'm told")

DO      EFE_RISK_AMBIGUITY ("Pick the best")          G = risk + ambiguity
        EFE_UNIMOTOR_LEGACY_V1 ("Pick the best, old way")
        ACTION_ARGMAX / ACTION_SAMPLE
        ACTION_RANDOM ("Just guess")                  adversary
        ACTION_NONE ("Do nothing")                    ablation

COUPLE  up_q_eps_pi_F, down_C_from_parent_q, down_precision_gate   (registry primitives, each with a written equation and a test)
```

Coupling maps are a **closed registry with published equations**, not free expressions. `up_q_eps_pi_F` is the identity packing of `{q, eps, Pi, xi, F, complexity, accuracy, uncertainty, viability}`. `down_C_from_parent_q(qParent, mapMatrix)` yields `C_child = ln(M qParent + eps)`, a declared normalised log-preference — the output is **type-checked as a `Nats` vector of the child's `obsDim`**, so a coupling cannot deliver a non-distribution into a child's `F` pass.

### 4.3 UNIEXPR (audit mode only, never in `play`)

A restricted expression grammar for scalar shaping of `gamma` schedules, `Pi` schedules and coupling scalars. **It is never used for `F` or `G`, which are compiled primitives.**

```
program := binding (";" binding)* [";"]
binding := ident "=" expr
expr    := term (("+"|"-") term)*
term    := unary (("*"|"/") unary)*
unary   := ["-"] power
power   := atom ["^" unary]                  // right-assoc; exponent must be dimensionless
atom    := NUMBER | IDENT | call | index | "(" expr ")"
call    := FUNC "(" [expr ("," expr)*] ")"
index   := IDENT "[" NUMBER "]"
FUNC    := ln | exp | sqrt | abs | min | max | clamp | sigmoid | softplus | tanh
         | sum | dot | entropy | kl | normalize | softmax
IDENT   := [A-Za-z_][A-Za-z0-9_]{0,31}       // must be a key of the injected scope
NUMBER  := digit+ ["." digit+] [("e"|"E") ["+"|"-"] digit+]
```

Scope, per level and explicit: `q, o, oPred, eps, xi, F, G, qPi, gamma, tau, t, nX, nO, nPi`, the level's declared scalar params, and `childQ, childF, childEps`. Any other identifier is a parse error with `{line, column, token}`.

No assignment beyond a declared output name, no strings, no property access, no comparison, no control flow, no loops, no user functions, no `random`, no `now`.

Character class whitelisted **before** the parser sees anything: `[A-Za-z0-9_+\-*/^(),.\[\] ;=\n]`. Everything else is a tokenizer rejection.

Budgets, enforced by `parse` and by an explicit interpreter step counter: ≤ 512 source chars, ≤ 256 AST nodes, ≤ 24 depth, ≤ 64 identifiers, ≤ 4096 interpreter steps. Exceeding any throws `UXL_BUDGET_EXCEEDED`.

```js
// lib/stack/expr.js
export function tokenize(src): Token[]
export function parse(src, scope): { ast, astSha256, nodes, depth }
export function typecheck(ast, scope): { kind, unit, truthClass, errors }
export function evaluate(ast, env, budget = 4096): number | number[]
export function compileMap(src, scope): UxlMap
export function applyMap(map, env): Record<string, number|number[]>
```

**Unit algebra.** `+ - min max clamp` require identical units. `*` concatenates, `/` cancels over a canonical multiset. `ln exp sigmoid softplus tanh softmax normalize ^` require `unit === "1"`. `entropy` and `kl` require a probability-constrained input and return `"nat"`. Adding a `Nats` to a `Joules` is `UNIT_MISMATCH`, reported as *"F is in nats; tau·dθ is in joules; they cannot be added."*

**Two guards that are acceptance criteria, not risk-register prose:**
1. **Tamper detection.** A saved `UxlMap` stores `{source, ast, astSha256}`. `loadStack` **re-parses the source**, recomputes the hash, and refuses on `UXL_AST_MISMATCH`. A hand-edited AST in JSON cannot bypass the parser.
2. **Non-finite refusal.** `applyMap` runs every output through a finiteness and declared-range check. A non-finite or out-of-range output marks the *receiving* level `STARVED` with `absentReason: "UXL_NON_FINITE"` and propagates nulls — never a NaN into a parent's `F`.

---

## 5. Visual specification

Route `app/stack-builder/page.tsx` (server; loads frozen reports and the source-pin manifest exactly as `app/math-workbench/page.tsx:15-77` does) plus `app/stack-builder/stack-builder.tsx` (client). The math workbench gains **one** nav entry in the array at `app/math-workbench/scientific-math-workbench.tsx:256-259` linking here; the 412-line component is otherwise untouched until Phase 6.

**CSS precondition (verified defect).** `app/globals.css` consumes `var(--cyan)`, `var(--gold)`, `var(--failure)`, `var(--void)` at lines 577-579, 586, 606, 609, 612, 626-628, 640-641, 649, 653-656, 664-666, and none of the four is declared; `:root` at lines 4-21 defines only `--ink --muted --quiet --ground --ground-2 --panel --panel-strong --line --line-strong --signal --signal-dark --prediction --belief --evidence --danger --good`. **All new builder CSS uses only the declared sixteen.** The four undefined properties are fixed in a separate bounded change with its own test (Phase 0.5, §10) and are not a dependency of this plan.

### 5.1 Layout

Three columns ≥ 1200 px, stacked below, matching the existing breakpoints at `app/globals.css:684-692`.

**Left rail `.stack-shelf` (18 rem).** Five starter towers as chunky tiles: *The swimming bacterium* (2 levels, runnable), *One motor deciding* (1 level), *Guess the weather* (1 level, no biology), *Two levels talking*, and — **not on the child shelf** — *The ladder we have not built*, reachable only from the audit-mode header. Below: the palette, grouped by socket colour, each brick drawn with its studs. Bricks that cannot seat anywhere currently empty are 35% opacity and **not draggable**; in `play` mode, `NOT_BUILT` bricks (the Python-only nodes) are hidden entirely rather than draggable-then-dead.

**Centre `.stack-tower`.** The tower, **L0 at the bottom**, scrolling upward, so the eye reads bottom-up in the direction the F pass runs.

**Right rail `.stack-inspector` (26 rem).** Four tabs: NUMBERS, MATH, MESSAGES, SOURCE.

**Bottom `.stack-timeline` (9 rem).** One horizontal lane per level, x = tick; a firing is a 3 px mark, an event-triggered firing a taller mark in `var(--danger)`. A scrubber sets `viewTick`; the ladder re-renders from `run.history[viewTick]` as a **pure array index with zero recomputation**. Beyond a 512-tick ring buffer the scrubber recomputes from `(stack, seed)` and, on divergence, renders a `REPLAY MISMATCH` banner and stops — a determinism assertion that runs in production.

### 5.2 The level card, component by component

`app/stack-builder/level-card.tsx`. What a card shows, at every `detail` level:

**Header row.** `ℓ` badge in mono; title (`playTitle` in play); **truth chip** — rendered at *every* detail level, using child words in play (`something we made up` / `something we measured` / `not built`); species label when non-null; clock chip `τ=4 · next t=12`; activity dot flashing on ticks where the level was ACTIVE.

**Left gutter (3 rem) — the clock lane.** A vertical column of tick pips at `tauTicks` spacing, current pip lit in `var(--signal)`. A `τ=4` level visibly blinks a quarter as often as L0. Asynchrony becomes legible with no text.

**Body — six sockets in a row.** Empty socket: dashed outline with its `playLabel`. Seated brick: solid tile, studs drawn on the top edge, a 4 px truth-class collar (`OBSERVED` = `var(--good)` plus a drawn keyhole; `MODELED` = `var(--belief)`; `DERIVED` = `var(--signal)`; `INFERRED` = `var(--evidence)`; `FROZEN_PREDICTION` = `var(--prediction)`; `NOT_BUILT` = `var(--quiet)`, hatched).

**Right gutter (10 rem) — live readouts, monospace, always with a unit suffix.**
- `play`: bar heights and words only, e.g. a surprise bar plus `I was a bit surprised`, and the action word `RUN`.
- `lab` / `audit`: `F = 0.4213 nat`, `complexity = 0.912 nat`, `accuracy = 0.481 nat`, `|ξ| = 1.08`, `G(π*) = 2.71 nat`, `a = RUN`.
- **Inert or starved:** every value is an em dash `—`, never `0`, at every detail level.

**Expanded body.** Left column: `ProbabilityRow` (reusing the existing component pattern at `scientific-math-workbench.tsx:203-211`) for `prior`, `likelihood`, `q(x)`, `oPred`, `o`, `q(π)`; `ε` and `ξ` as signed bars (negative left in `var(--danger)`, positive right in `var(--signal)`) labelled *diagnostic, not part of F*. Right column: the F/G table in the shape of the existing table at `scientific-math-workbench.tsx:331` — columns `Policy | risk | ambiguity | G | q(π)` — with the footer `F = complexity − accuracy = 0.912 − 0.481 = 0.431 nat`.

**The free-energy handle (the single best teaching affordance in the design).** In the expanded card, `q(x)` is draggable on a 3-simplex triangle. `freeEnergyAt(q, prior, logLik)` is exported separately from the minimiser precisely so the UI can evaluate `F` at any user-supplied `q`. Dragging `q` off the minimum makes an `F` bar visibly rise; releasing snaps back to `q*`. In `play` the number is hidden and only the bar height shows. **A child physically feels that `q*` sits at the bottom of a bowl.**

**INERT card.** Grey, hatched, **no sockets at all** — nothing can be dragged into it at any zoom — and one sentence: `NOT BUILT — nothing is computed here.` A `STARVED` card reads `WAITING — L1.dwell sent nothing.`

### 5.3 The seam

`app/stack-builder/seam.tsx`, 3.5 rem between cards, two CSS-only arrows (no canvas, no WebGL).

- **UP**, left half, `var(--evidence)`: `F=0.431 nat · ‖ξ‖=1.08 · Π̄=1.40`. Stroke width `clamp(2px, 2px + 6px*tanh(|ξ|/scale), 8px)`.
- **DOWN**, right half, `var(--prediction)`: `γ=4.00 · C̄=−0.51 nat · gate=1.00`.
- In `play`, the same arrows carry words: *"I tell the level above what I noticed"* / *"It tells me what to want"* — with the truth chip still present.
- **ABSENT:** a dashed grey outline captioned `NO MESSAGE — LEVEL NOT BUILT`. Never a thin-but-present numeric arrow.
- Hover shows `postedTick → deliverTick` and the receipt hash prefix, making the one-tick latch visible rather than mysterious.

### 5.4 Transport bar (sticky)

`⏭ STEP` · `▶ RUN ×[10|100|1000]` · `⏹` · `⟲ RESET` · `↶ UNDO` · seed field · `stackHash[0..12]` (click to copy) · detail switch `play | lab | audit`.

`UNDO` is a first-class control at every detail level. Its absence in the science-first design was judged fatal for the child path: an 8-year-old's learning mode is undo.

### 5.5 Progressive disclosure — the exact contract

One `detail` prop, identical DOM. What is **always** present regardless of detail: truth chips, species labels, `NOT BUILT` captions, unit suffixes on every scalar, em dashes for inert values, the `ABSENT` seam caption. What is progressive: Greek symbols and formal names (`lab`+); the equation pane (`lab`+); hashes, `sourcePin` sha256, the gate ledger, prospectivity banner, and UNIEXPR bricks (`audit` only).

A screenshot taken in **any** mode carries the truth class of every number on it. This is gated by `tests/rendered-html.test.mjs`.

---

## 6. The LEGO / child path

### 6.1 Studs are types

Seven shapes; the shape **is** the type. Round = a bag of chances (`Simplex`); square = one number (`Scalar`, with the unit written on it); hexagon = something I saw (`Obs`); triangle = something I do (`Act`); cross = a change table (`Matrix`, column-stochastic); **round-with-a-notch = surprise money (`Nats`); square-with-a-notch = real work (`Joules`)**. The last pair is the CLAUDE.md thermodynamic/informational separation rendered as plastic: a Joules stud physically cannot enter an `F` socket, and there is no conversion function in the library.

Seam connectors are keyed opposite: up-studs exist only on plate tops, down-tubes only on plate bottoms. Direction inversion is not a mistake a child can make.

### 6.2 Snapping and the four-tier refusal ladder

There are **no modal dialogs and no error codes on screen in `play`**.

1. **Prevention.** Sockets that cannot accept a dragged brick do nothing at all — no red, no highlight. Legal sockets glow `var(--signal)` with a 6 px magnet radius. Unusable bricks are dimmed and undraggable.
2. **Snap-back.** A bad drop tweens home in 160 ms with a 3° shake. Zero words.
3. **The hover chip.** 600 ms on a socket draws the shape it wants; on an incompatible brick, draws the two shapes with a slash. Text layer, six sentences total:
   - *"These pieces are different sizes. The blue piece makes 3 numbers; the yellow piece wants 5."*
   - *"This piece measures surprise. That hole measures energy. They are not the same kind of thing."*
   - *"That's a Want piece. This hole is for a Because piece."*
   - *"This is something we made up. That hole only takes something we actually measured."*
   - *"Up-pipes only go up. Turn it around."*
   - *"This level is not built yet, so nothing can come out of it."*
   Each carries a **show me** link that highlights the exact stud pair.
4. **The grey run button.** A tower with an empty required socket reads `▶ needs 1 more piece`; clicking scrolls to the socket and pulses it three times. The tower never runs half-built and never zero-fills.

Every drag has a keyboard equivalent (select brick, Enter on a lit socket). There is no force-connect anywhere.

### 6.3 The first three clicks

1. Click the shelf tile **The swimming bacterium**. A two-plate tower appears, fully built, valid, `▶ STEP` pulsing.
2. Click **▶ STEP**. Bars move; the seam arrow thickens; `WHAT I DO` flips `RUN`/`TUMBLE`. One step, one visible consequence.
3. Drag **Just guess** (`ACTION_RANDOM`) onto `WHAT I DO`, replacing **Pick the best**. Press `▶ RUN ×100`. The bacterium stops climbing the gradient.

The child has run an adversarial baseline and watched it lose, in three clicks, with `UNDO` available throughout. This is exploration — it produces a trajectory, not a verdict.

### 6.4 From play to a scored claim

When the child (or researcher) clicks **Make it count**, the experiment apparatus appears: the tower's `CONTROL`, `ADVERSARY` and `NEGATIVE_CONTROL` arms are auto-generated, the refutation card is pre-filled from the brick's default with `authored: false`, and the seal button appears. The result is real and reported — but a defaulted falsifier caps the verdict at `INCONCLUSIVE` with the reason shown in plain words: *"You did not say what would show you were wrong, so this counts as a look, not a finding."* Authoring the falsifier lifts the cap.

`refutation.authored` is a self-report and defends against laziness, not intent. That limitation is printed on the record.

### 6.5 Verdict sentences

- Win: *"Your model beat the coin flip by 0.42 (somewhere between 0.31 and 0.53). That is a real win."*
- Loss: *"Your model did NOT beat the coin flip. That is a real answer too — write down why you thought it would."*
- Inconclusive: *"We could not tell. The interval crosses zero, so this is not established."*

The losing sentence is not removable and its content is appended to `adverseFindings[]`.

---

## 7. Version control and variants

**Content addressing.** `stackHash = "sha256:" + sha256Hex(canonicalJson(stack))` over everything except `stackHash`, `createdAtUtc` and `authorNote`, so mathematically identical stacks hash identically. `parents[]` records lineage. `runId = sha256(stackHash + "|" + seed + "|" + ticks + "|" + armId)`.

**On disk (git is the version-control system; nothing is reinvented):**
```
experiments/stacks/<slug>/stack.json
experiments/stacks/<slug>/variants/<variantId>.json      a PATCH, never a copy
experiments/stacks/<slug>/lineage.json                   append-only
experiments/results/stack/<runId>.run.json
experiments/designs/<EXP_ID>.experiment.json
experiments/predictions/<EXP_ID>.prediction.json
```

`npm run stack:canon` rewrites every artifact canonically so a one-parameter change is a one-line git diff. `npm run stack:verify` (`scripts/verify-stacks.mjs`) walks the tree and asserts: every `stackHash` recomputes; every variant's `applyOps(parent, ops)` reproduces `childHash`; every run's `stackHash` exists; every `adverseFindings[]` array is a superset of its previous committed value.

**In browser.** `localStorage["uni.stack.workspace/1.0.0"]`, ≤ 2 MB, schema-versioned, oldest drafts evicted. No IndexedDB, no server, no network. A workspace that fails to parse or hash-verify is **refused with a message**, never silently reset. Export/import via `Blob` + `URL.createObjectURL` with repo-relative filenames plus an `APPLY.txt`; `scripts/import-stack-export.mjs` re-canonicalises, recomputes every hash, and **fails on mismatch**.

**Variants are patches.** `role` is one of the seven listed in §2.5. `verifyVariant` mismatch marks the variant `BROKEN LINEAGE` in `var(--danger)` and `runExperiment` refuses it: you cannot run a model whose ancestry does not reproduce.

**Diff.** `lib/stack/diff.js`:
```js
export function diffStacks(a, b): {
  levels: Array<{op:"add"|"remove", levelId, index}>,
  params: Array<{levelId, socket, path, from, to, delta, columnSumsStillValid}>,
  structure: Array<{levelId, path, from, to}>,
  uxl: Array<{levelId, mapName, fromSha256, toSha256, fromSource, toSource}>,
  truthAffecting: Array<{levelId, kind:"truthClass"|"built"|"sourceBinding", from, to, requiresSourceBinding}>
}
```
`truthAffecting` is a **separate top-level field**, rendered in a loud `var(--danger)` band above everything else, captioned `TRUTH-AFFECTING CHANGE`. Any move toward `OBSERVED` additionally displays the sha256 that must verify.

**Lineage view.** A text-first DAG: indented rows `hash[0..12] · role · authorNote · Δ3 params, Δ1 level`, tinted by last verdict — green SUPPORTED, red CONTRADICTED, grey INCONCLUSIVE, hatched NOT_RUN. **A CONTRADICTED tip is never pruned**; the graph is the record of what failed.

---

## 8. Experiment apparatus

### 8.1 Arms (closed enum; `validateExperiment` refuses an incomplete set)

| Role | Requirement | Content |
|---|---|---|
| `TREATMENT` | ≥ 1 | the stack under test |
| `CONTROL` | ≥ 1 | same stack, different seed |
| `ABLATION` | auto-generatable per level | one brick disabled or one parameter pinned neutral; recorded as an explicit `ops[]`, never described in prose. Standard set: `gamma→0`, `Pi→1`, seam removed, `C` flat, `B→identity` |
| `ADVERSARY` | ≥ 1 | `ACTION_RANDOM`, `POSTERIOR_FROZEN`, constant predictor, persistence baseline, KDE ceiling (training-only flexible model) |
| `NEGATIVE_CONTROL` | ≥ 1 | outcome labels permuted **within each unit** at a declared RNG stream; expected paired advantage ≈ 0 |
| `CHEATING_CONTROL` | **mandatory** | `OBS_ORACLE_CHEAT`; **must win by a wide margin** or the score function cannot detect leakage and no other arm is interpretable |
| `BASELINE_PARENT` | auto for variants | the parent stack |

`runExperiment` refuses to emit a result without a `CHEATING_CONTROL` arm, and `verdict()` returns `INCONCLUSIVE / CHEATING_CONTROL_DID_NOT_WIN` if it fails to win.

### 8.2 Scoring

Primary: mean held-out log predictive density, **nats per event, on the seconds scale**. Secondary: CRPS. Both always computed; `rulesAgree` first-class; the word "better" only when they agree — lifted from `audits/phase-b/b3-competition-protocol.v1.json`.

The `-log(stateMeanDurationS)` Jacobian is mandatory for any normalised-duration density, exactly as `lib/duration-models.js:96` does it; a density declared on a normalised scale without a declared Jacobian throws `MISSING_JACOBIAN`.

Uncertainty: **paired cluster bootstrap over the declared experimental unit** (`motorId`), resampling `nUnits` unit ids with replacement, never rows. `assertUnitIsNotFrame` throws `UNIT_IS_FRAME` when the unit field matches `/frame|tick|time|index|row/i` or when its cardinality equals the row count. Deltas are always `TREATMENT − namedArm`; the UI never shows an absolute score without at least one delta beside it.

### 8.3 Parameter recovery

`recoverParameters(stack, trueParams, seeds)` simulates from a known θ at declared seeds, refits with the stack's own fitter over the declared bounded box, and reports per-parameter bias, RMSE and 95% interval coverage. A level with coverage < 0.80 is stamped `UNIDENTIFIABLE` on its card in `var(--danger)`, and `verdict()` downgrades to `INCONCLUSIVE / PARAMETER_NOT_RECOVERABLE`. Identifiability is a precondition for interpreting any comparison, and this is the gate that enforces it.

### 8.4 Prospectivity — three locks plus a delegated witness

1. **Unreachability.** `env.holdout` is a `Proxy` whose every `get` throws `HOLDOUT_SEALED` until `sealExperiment` has been called. The answer is not hidden in the UI; it is unreachable from the computation.
2. **Prior-run refusal.** `sealExperiment(exp, existingReceipts)` throws `ALREADY_RUN` if any run record exists for that `baselineStackHash`. This closes the see-then-freeze loop: you cannot pre-register a stack you have already run.
3. **Seal integrity.** The run stores `sealHash = sha256(canonicalJson(prereg))`. A one-character post-hoc prereg edit yields `SEAL_MISMATCH`.
4. **The witness is git, not the browser.** `runExperiment` in the browser stamps `prospectivity: "TIMING_UNVERIFIED"` — **there is no code path by which the browser emits `PROSPECTIVE`.** The builder writes `experiments/predictions/<EXP_ID>.prediction.json` in the exact shape validated by `tests/semantic/prospectivity-provenance.test.mjs` (`recordId`, `claim`, `falsifier`, `madeAgainstCommit` 40-hex, `predictionPath`, `resultPaths`, `prospectivity`), initialised `PENDING`. The user commits the prediction alone, runs, then commits the result; the existing gate measures `PROSPECTIVE` from `git merge-base --is-ancestor`. A single squashed commit measures `SAME_COMMIT` and is forced to `TIMING_UNVERIFIED`, and an environment without git degrades to `NOT_RUN`. We reuse that adversarially-tested oracle rather than mint a second, weaker one.

### 8.5 Ledger integration

Builder gates append to `experiments/results/stack-gates-report.json` using the **existing gate-record shape** consumed at `app/math-workbench/page.tsx:36-42` (`{id, title, status, criterion, limitation}`) and the existing status vocabulary `PASS / FAIL / NOT_ESTABLISHED / BLOCKED_EXTERNAL / NOT_RUN`, so they render in the Measured-evidence tab with zero new UI code. `tests/semantic/adverse-record-preservation.semantic.test.mjs` is extended to cover `experiments/results/stack/*.run.json`, so a `CONTRADICTED` verdict cannot be deleted in a later commit. Post-hoc defects are recorded as `audits/phase-e/<ID>-correction-package.v1.json` in the D1 schema; the run record is never edited and gains only a `supersededBy` pointer.

---

## 9. Test and mutation-gate list

House style throughout: header comment naming the frozen property and the target corruptions, `node:test` + `node:assert/strict`, hand-calculable fixtures, assertion messages naming the *scientific* consequence. All files appended to the explicit list in `package.json:9`.

### 9.1 Correctness gates (`tests/stack/`)

| File | Asserts |
|---|---|
| `hash-differential.test.mjs` | `sha256Hex` matches `node:crypto` over 20 000 seeded random inputs 0–4096 bytes incl. the 55/56/64-byte boundaries; `canonicalJson` stable under key reordering; throws on NaN/Infinity |
| `numeric-invariants.test.mjs` | `normalize` sums to 1 ± 1e-15; `softmax` additive-constant invariant; `entropy ≤ ln n` with equality only at uniform; `kl(p,p) === 0` and `kl ≥ 0` over 10⁴ pairs |
| `level-algebra.test.mjs` | **the load-bearing gate.** Over 10⁴ seeded `(prior, logLik)`: (a) closed-form `q*` equals 200-step gradient-free minimisation of `freeEnergyAt` to 1e-9; (b) `F(q*) ≤ F(q)` for 100 perturbations each, every time; (c) `F === complexity − accuracy` exactly; (d) `F === kl(q*, exactPosterior) − ln evidence` with the first term ≤ 1e-12 — **and `exactPosterior` is computed independently in the test file from `prior .* exp(logLik)`, not imported from the kernel**, so the oracle is not circular; (e) `G === risk + ambiguity` and `risk === crossEntropy(qO,C) − entropy(qO)`; (f) `qPi` is a simplex and `argmin G === argmax qPi` at uniform `E` |
| `scheduler-determinism.test.mjs` | three runs from one seed give identical `traceHash`; `replay(run)` reproduces it; 20 seeded permutations of active-level order leave `traceHash` unchanged; seed+1 changes it; 1000 ticks over 3 levels complete under 200 ms |
| `bus-routing.test.mjs` | every message satisfies the direction/index ordering and `deliverTick === postedTick + 1`; every receipt recomputes |
| `expr-grammar.test.mjs` | frozen 60-row accept/reject table incl. `constructor`, `a.b`, `this`, `process.exit(1)`, `import("x")`, `while(1)1`, backticks, `__proto__`, `a=>a`, `${x}`, `0x41`, a 600-char source, a 40-deep nest, unknown FUNC, out-of-scope IDENT; budgets throw; `astSha256` stable across parse→serialise→parse; `UXL_AST_MISMATCH` on a hand-edited AST; **applyMap on a NaN-producing map yields STARVED, not NaN**; source scan of `lib/stack/**` finds zero `eval`, `new Function`, dynamic `import(`, `Math.random`, `Date.now`, `performance.now`, `fetch`, `WebGL`, `WebGPU` |
| `unit-algebra.test.mjs` | `nat + J` throws `UNIT_MISMATCH`; `exp(J)` throws; `ln(uM)` throws; `entropy(q)` returns `"nat"`; a Joules-valued expression cannot seat in an `F` socket |
| `ports-connect.test.mjs` | frozen kind×kind connectivity matrix; **exhaustive registry scan asserting no brick signature maps a Joules input to a Nats output or the reverse** (not a name grep); every refusal code returns a child message |
| `stack-hash-stability.test.mjs` | key reordering, float reformatting, and `createdAtUtc`/`authorNote` changes leave `stackHash` unchanged; any parameter change alters it |
| `scoring.test.mjs` | log score against a hand-computed exponential; CRPS against a closed form; interval width shrinks as `1/√nUnits`; `MISSING_JACOBIAN` throws |
| `migration-parity.test.mjs` | `S_MOTOR_V1` over 500 ticks reproduces `stepAgent`/`stepSyntheticSystem` on posterior, likelihood, risk, ambiguity, efe, policyPosterior, vfe, surprise **to ≤ 1e-12** (a tolerance, not `deepEqual` — decomposition reassociates floating-point operations) |

### 9.2 Semantic / mutation gates (`tests/semantic/`)

| File | Kills |
|---|---|
| `stack-truth-lattice.semantic.test.mjs` | **M-LAUNDER.** Frozen 6×6 `joinTruth` table; `joinTruth("MODELED","OBSERVED") === "MODELED"`; `bindObserved` throws on sha256 mismatch, on a missing citation, and on a pin absent from `SOURCE_PIN_MANIFEST`; **no exported function in `lib/stack/` accepts a `truthClass` argument for computed state**; `applyOps` rejects any path touching `truthClass` |
| `stack-message-direction.semantic.test.mjs` | **M-DIR.** `post` throws on mis-ordered indices; swapping `up`/`down` primitives changes `traceHash` (an inversion that changed nothing would mean the hierarchy is decorative); changing `C` at L1 leaves every L0 field at the same tick bit-identical; changing `ε` at L0 leaves L1's `o` unchanged until `tick+1` |
| `stack-level-identity.semantic.test.mjs` | **M-SWAP.** `levels[i].index !== i` throws; exchanging two level indices changes `traceHash` and perturbs at least one `F` series by > 1e-9 |
| `notbuilt-inertness.semantic.test.mjs` | **M-ZERO.** Every INERT field is `null` (`assert.strictEqual(x, null)`, which `0` fails); reducers throw `NULL_COERCION_REFUSED`; a level downstream of an ABSENT seam is `STARVED` with all-null numerics and **does not fall back to its own D**; `built:false → true` without parameters fails validation; **adding a 12-level inert ladder leaves L0's `traceHash` bit-identical to the 1-level stack's** |
| `stack-unit-separation.semantic.test.mjs` | **M-UNIT.** `τ·Δθ` is stamped `"J"` and cannot reach a `"nat"` socket; no exported function converts between them |
| `stack-seal-integrity.semantic.test.mjs` | **M-SEAL.** Holdout `get` throws before seal; `sealExperiment` throws `ALREADY_RUN` when a receipt exists; a one-char prereg edit yields `SEAL_MISMATCH`; a partial run throws `PARTIAL_RUN_CANNOT_BE_SCORED`; the browser path never emits `PROSPECTIVE` |
| `stack-experiment-completeness.semantic.test.mjs` | **M-CTRL.** Missing `CONTROL`/`ADVERSARY`/`NEGATIVE_CONTROL`/`CHEATING_CONTROL` is unsavable; the `CHEATING_CONTROL` must win or the verdict downgrades; the `NEGATIVE_CONTROL` paired interval covers 0 |
| `stack-pseudoreplication.semantic.test.mjs` | **M-REPL.** The bootstrap draws exactly `nUnits` ids; duplicating every event within each unit does not shrink the CI by > 5%; 8 motors × 500 frames gives the same interval as 8 motor aggregates; `unitField: "frameIndex"` throws |
| `uni-motor-parity.semantic.test.mjs` | **M-DRIFT.** `UNIMOTOR_LEGACY_V1` reproduces `stepAgent` to 1e-12; `RISK_AMBIGUITY` and `UNIMOTOR_LEGACY_V1` are asserted to **differ**, documenting `lib/uni-motor.js:326-328` rather than hiding it |
| `ladder-not-built.semantic.test.mjs` | Every `HUMAN_LADDER` entry with `index ≥ 1` has `built:false`, `truthClass:"NOT_BUILT"`, no sockets, and `openQuestion:true` on L12 |
| `stack-lineage-integrity.semantic.test.mjs` | `verifyVariant` rejects an edited `ops[]`; `applyOps` throws on `/__proto__`, `/constructor`, `/levels/0/truthClass` |

### 9.3 Render gate (`tests/rendered-html.test.mjs`, extended)

Existing assertions unchanged. Added: `GET /stack-builder` returns 200; the human-ladder route renders `NOT BUILT` for every unbuilt level; **no rendered element carries an `OBSERVED` chip while `data-truth` is not `OBSERVED`**; every rendered scalar carries a unit suffix or an em dash; no inert level renders a numeric `0` for `F`, `G`, `γ` or `Π`; a `play`-mode render still contains a truth chip for every level.

### 9.4 Mutation battery

`audits/phase-e/e1-stack-mutation-patch-set.v1.json` (18 frozen mutations: M-LAUNDER ×3, M-SWAP ×2, M-DIR ×2, M-SEAL ×2, M-CTRL ×2, M-SCORE ×3, M-UNIT ×1, M-REPL ×1, M-ZERO ×1, M-ADVERSE ×1), executed by `audits/phase-e/tools/run-stack-mutation-replay.mjs` in the scratch directory, never the worktree.

**Acceptance criterion, adopted from the science-first design because it is the only proposed defence against a vacuous gate:** each mutation must be `DETECTED_SEMANTIC` with `attributionSatisfied: true` — naming the assertion that caught it. `DETECTED_BY_HASH_ONLY` (a diagnostic that merely reports a changed artifact hash) **counts as UNCAUGHT**. Any survivor is recorded as an `OPEN COVERAGE HOLE` in the ledger and in `docs/STACK-BUILDER.md`, never patched away silently. Phase C caught 0/10; this battery exists to make that unrepeatable.

---

## 10. Migration

**Rule: wrap, never edit.** `lib/uni-motor.js`, `lib/duration-models.js`, `lib/source-first-passage.js`, `lib/observed-experiment.js`, `lib/walkthrough.js`, `lib/cad.js` are byte-identical to HEAD `c23f686` through Phase 9. All 103 tests keep passing because the modules they test are untouched.

**The private-symbol constraint (verified).** `transitionPrior` (`lib/uni-motor.js:251`) and `policyTerms` (`lib/uni-motor.js:309`) are **module-private**. Two of the three competing designs proposed binding to them directly; that is unbuildable without editing the module, which would widen the surface pinned at `tests/semantic/world-agent-observation-boundary.semantic.test.mjs:134-138` (`stepAgent.length === 3`). Resolution:

- **v1 adapters do not call them.** `lib/stack/adapters/uni-motor-level.js` builds a `LevelSpec` from the literals in that file — `A` from `outcomeLikelihood` (:303-307, transposed to `A[o][x]` and column-normalised), `B.RUN`/`B.TUMBLE` from `bRun`/`bTumble` (:254-263), `C = ln normalize([0.06,0.24,0.70])` (:317), `D = [0.15,0.35,0.50]` (:91), `E` uniform, `gamma = 4` (from the literal `-4` at :348), `effort = [0.02,0.07]` (:327), `gScoring: "UNIMOTOR_LEGACY_V1"`, `tau: 1`, labels from `GRADIENT_STATES`/`OUTCOME_STATES`/`POLICY_NAMES` (:10-12) — and the parity is proven against the **exported** `stepAgent` to 1e-12.
- Exporting the two private functions is deferred to its own bounded, separately-gated phase (out of scope here) with its own prediction record.

**The world is a node, not a level.** `role: "WORLD"`, wrapping `stepWorld`/`observeWorld` unchanged. The Markov boundary is the frozen nine-key set already protected by `tests/semantic/world-agent-observation-boundary.semantic.test.mjs:41-51`, so the existing gate protects the builder for free. `stepWorld` uses `Math.exp`/`Math.sin` and is outside the bit-identical guarantee; such stacks record `replayGuarantee: "ENGINE_ONLY"`, declared in the run artifact and shown in the UI.

**The 11 catalog entries.** They move verbatim from `app/math-workbench/scientific-math-workbench.tsx:80-191` into `lib/stack/catalog-nodes.js` as `CATALOG_NODES`, each keeping its exact `id/name/truth/equation/input/output/source/plain` strings and gaining `socket`, `ports`, `truthClass`, `built`, `role`, `sourceBinding`. The `.tsx` then does:

```js
import { CATALOG_NODES, toLegacyCatalog } from "@/lib/stack/catalog-nodes.js";
const modelCatalog = toLegacyCatalog(CATALOG_NODES);
```

`toLegacyCatalog` projects exactly the 8 legacy keys in the original order. **The acceptance criterion is byte equality** — `JSON.stringify(toLegacyCatalog(CATALOG_NODES))` equals a frozen literal captured *before* the move — with `tests/math-workbench.test.mjs` and `tests/rendered-html.test.mjs` unmodified. This makes the migration provably a no-op.

Assignments:

| Catalog id | Role / socket | Truth | JS-executable? |
|---|---|---|---|
| `WORLD` | WORLD node | MODELED | yes (`stepWorld`) |
| `BOUNDARY` | SEE, L0 | DERIVED | yes (`observeWorld`) |
| `BAYES`, `VFE` | THINK, L0 | DERIVED | yes (via `stepAgent`) |
| `EFE` | DO, L0 | DERIVED | yes (via `stepAgent`) |
| `DURATION` | EXPECT, ANALYSIS | **OBSERVED**, source-pinned to `experiments/results/observed-experiment-report.json` + `protocolId` + DOI | yes |
| `DLT` | EXPECT, ANALYSIS | DERIVED, pinned to the science-gates report | yes (evaluation only; fitting is Python) |
| `ROTATION` (X03) | ANALYSIS | DERIVED | **no — `NOT_BUILT` in JS** |
| `LATTICE` (X06) | ANALYSIS | MODELED, `validity: "UNIDENTIFIABLE"`, carries `MODEL FAILED IDENTIFICATION GATE` | **no** |
| `GMC` (X07/X08) | ANALYSIS | MODELED (source reproduction, not experimental truth) | **no** |
| `RFT` (X09) | ANALYSIS | DERIVED | **no** |

The four Python-only entries ship with `implId: null`, `built: false`, hatched grey, captioned `NOT BUILT IN THE BROWSER — result comes from scripts/run-cross-study-parity.py`. **In `play` mode they are hidden from the palette entirely** (per the child-usability judge: a draggable brick that produces a dead run button contradicts prevention-first refusal). In `lab`/`audit` they are visible and undraggable.

**The nine B3 competitors.** Any competitor list must distinguish **NOT IMPLEMENTED** from **NOT RUN**: `M4_MIXTURE_K3`, `M5_GAMMA`, `M6_SEMI_MARKOV`, `M7_HIERARCHICAL`, `M8_EMPIRICAL_KDE` exist only in frozen JSON specs and have no implementation in any language. The builder shows 4 implemented + 5 not implemented, never 9 pending.

**The human ladder.** `lib/stack/ladder.js` exports `HUMAN_LADDER`: L1 cellular … L11 offline replay, all `built:false`, `truthClass:"NOT_BUILT"`, no sockets, each carrying a `whatWouldItTakeToBuild` string; L12 additionally `openQuestion:true`, `claimed:false`, `claimForbidden: "This level is not built, not partially built, and no result from this repository bears on it."` **The ladder is not on the child shelf** and is reachable only from audit mode, with a standing banner: *"One level is built. The other twelve are names, not models."* This is a presentational mitigation of a presentational risk and is recorded as such (§13).

---

## 11. Phased delivery plan

Ten phases. Every phase is independently shippable, independently testable, and reversible by reverting its own commit. Phases 1–5 touch no existing file; Phase 6 is the first that edits `scientific-math-workbench.tsx`, under a byte-equality gate.

---

### Phase 0.5 — CSS custom-property repair (prerequisite, not part of the builder)

**Deliverable.** Declare `--cyan`, `--gold`, `--failure`, `--void` in `:root` (and any dark-scheme block) of `app/globals.css`, or replace their 15 use sites with declared properties.

**Files changed.** `app/globals.css`; `tests/globals-css-vars.test.mjs` (new).

**Acceptance criterion.** A test parses `app/globals.css`, extracts every `var(--name)` reference, extracts every `--name:` declaration, and asserts the reference set is a subset of the declaration set. Currently red for four names.

**Falsifier.** If the four properties turn out to be intentionally inherited from a parent document, the test is wrong and must instead assert an explicit allowlist of externally-supplied properties — recorded, not deleted.

**Test that must fail first.** `tests/globals-css-vars.test.mjs` on the unmodified `app/globals.css`.

**Rollback.** `git revert` the single commit. No builder code depends on it: all builder CSS uses only the sixteen declared properties.

**Effort.** Half a day. This is a separate bounded change with its own prediction record; it is listed here because every design that reuses `.workbench-status` chips inherits the defect.

---

### Phase 1 — Canonical hashing and the truth lattice (one sitting)

**Deliverable.** `canonicalJson`, `sha256Hex`, `contentHash`, `TRUTH_ORDER`, `joinTruth`. Nothing else. No stack concepts, no runtime, no UI.

**Files created.** `lib/stack/hash.js`, `lib/stack/hash.d.ts`, `lib/stack/truth.js`, `lib/stack/truth.d.ts`, `tests/stack/hash-differential.test.mjs`, `tests/semantic/stack-truth-lattice.semantic.test.mjs` (lattice portion only).
**Files changed.** `package.json` (append two files to the `test` list).

**Acceptance criterion.**
1. `sha256Hex` agrees with `node:crypto` on 20 000 seeded random inputs of length 0–4096, explicitly including lengths 55, 56, 63, 64, 65, 119, 120.
2. `canonicalJson` is byte-stable under key insertion order; throws on `NaN`/`Infinity`; renders `-0` as `0`.
3. `contentHash` of a fixture equals a hand-pinned literal.
4. The 6×6 `joinTruth` table equals a frozen literal and always returns the weakest input.
5. `npm test` passes with the 103 existing tests' behaviour unchanged.

**Falsifier.** If `sha256Hex` disagrees with `node:crypto` on any input, every downstream truth guarantee — OBSERVED binding, seal integrity, lineage verification, AST tamper detection, trace replay — is void, because all of them reduce to this function. Stop and fix before any other phase.

**Test that must fail first.** `tests/stack/hash-differential.test.mjs` against an empty `lib/stack/hash.js` (module-not-found, then wrong-digest as the implementation lands).

**Rollback.** Revert the commit; delete `lib/stack/`; remove two lines from `package.json`. No existing file's behaviour was touched.

**Effort.** 1 day.

---

### Phase 2 — Ports, level validation, F and G

**Deliverable.** `lib/stack/types.d.ts`, `numeric.js`, `ports.js`, `level.js`. A single level computes correctly with no stack, no bus, no scheduler, no UI.

**Files created.** `lib/stack/types.d.ts`, `lib/stack/numeric.js(.d.ts)`, `lib/stack/ports.js(.d.ts)`, `lib/stack/level.js(.d.ts)`, `tests/stack/numeric-invariants.test.mjs`, `tests/stack/level-algebra.test.mjs`, `tests/stack/ports-connect.test.mjs`, `tests/semantic/stack-unit-separation.semantic.test.mjs`.
**Files changed.** `package.json`.

**Acceptance criterion.**
1. `F(q*) ≤ F(q)` for every one of 10⁶ perturbations across 10⁴ seeded cases.
2. Closed-form `q*` equals a 200-step gradient-free minimisation of `freeEnergyAt` to 1e-9.
3. `F === complexity − accuracy` exactly; the `F = KL − ln p(o)` identity holds against an **independently computed** posterior in the test file.
4. `G === risk + ambiguity` under `RISK_AMBIGUITY`; `risk === crossEntropy(qO,C) − entropy(qO)`.
5. The exhaustive registry scan finds no Joules→Nats or Nats→Joules signature.
6. `validateLevel` returns each named violation code on its targeted fixture.

**Falsifier.** If any perturbed `q` yields `F` below `F(q*)`, the closed form is not the variational minimiser and the entire F pass is wrong. If the identity test can only be made to pass by importing the kernel's own posterior as the oracle, the test is circular and must be rewritten before the phase closes.

**Test that must fail first.** `tests/stack/level-algebra.test.mjs` clause (b), written against a deliberately non-normalised `q*`.

**Rollback.** Revert; Phase 1 stands alone and is unaffected.

**Effort.** 3–4 days.

---

### Phase 3 — Bus, scheduler, inertness, bit-identical replay

**Deliverable.** `rng.js`, `bus.js`, `scheduler.js`, `stack.js`, `ladder.js`. A 3-level stack runs 1000 ticks headless; a 12-level inert ladder provably changes nothing.

**Files created.** `lib/stack/rng.js(.d.ts)`, `bus.js(.d.ts)`, `scheduler.js(.d.ts)`, `stack.js(.d.ts)`, `ladder.js(.d.ts)`, `tests/stack/scheduler-determinism.test.mjs`, `tests/stack/bus-routing.test.mjs`, `tests/semantic/stack-message-direction.semantic.test.mjs`, `tests/semantic/stack-level-identity.semantic.test.mjs`, `tests/semantic/notbuilt-inertness.semantic.test.mjs`, `tests/semantic/ladder-not-built.semantic.test.mjs`.
**Files changed.** `package.json`.

**Acceptance criterion.**
1. Three runs from one seed produce identical `traceHash`; `replay(run)` reproduces it; 20 seeded permutations of active-level order leave it unchanged.
2. Every message satisfies the direction/index rule and `deliverTick === postedTick + 1`.
3. Exchanging two level indices changes `traceHash`.
4. **Adding a 12-level inert ladder leaves the built level's `traceHash` bit-identical to the 1-level stack's.**
5. Every INERT field is `null`; reducers throw `NULL_COERCION_REFUSED`; a STARVED level does not fall back to its own `D`.
6. A `tau=8` child still holds its parent's last `DownPayload` on intervening ticks.
7. 1000 ticks over 3 levels complete under 200 ms.

**Falsifier.** If permuting iteration order changes `traceHash`, the one-tick latch is not isolating the phases and order independence is false — the scheduler must then declare a fixed canonical order as a gated semantic requirement rather than claim commutativity. If adding inert levels perturbs the built level's hash by one bit, inert levels are not inert and are silently participating; that is the worst failure mode in this product and the phase must not ship.

**Test that must fail first.** `tests/semantic/notbuilt-inertness.semantic.test.mjs`, written against a scheduler that returns `0` for an inert `F` (`assert.strictEqual(x, null)` fails on `0`).

**Rollback.** Revert; Phases 1–2 stand.

**Effort.** 4–5 days.

---

### Phase 4 — Migration adapters, motor stack, headless CLI (first demoable artifact)

**Deliverable.** `adapters/uni-motor-level.js`, `duration-level.js`, `first-passage-level.js`; `experiments/stacks/motor-loop/stack.json`; `scripts/run-stack.mjs` printing an ASCII ladder with live `F`/`G`.

**Files created.** `lib/stack/adapters/*.js`, `lib/stack/brick-registry.js(.d.ts)`, `lib/stack/edit.js(.d.ts)`, `experiments/stacks/motor-loop/stack.json`, `scripts/run-stack.mjs`, `tests/stack/migration-parity.test.mjs`, `tests/semantic/uni-motor-parity.semantic.test.mjs`.
**Files changed.** `package.json` (tests + a `stack:run` script).

**Acceptance criterion.**
1. `UNIMOTOR_LEGACY_V1` reproduces `stepAgent`'s posterior, likelihood, risk, ambiguity, efe, policyPosterior, vfe and surprise over 500 steps **to ≤ 1e-12** (tolerance, not exact equality — decomposition reassociates float ops).
2. `RISK_AMBIGUITY` and `UNIMOTOR_LEGACY_V1` are asserted to **differ**.
3. `lib/uni-motor.js`, `lib/duration-models.js`, `lib/source-first-passage.js` are byte-identical to HEAD `c23f686`.
4. All 103 existing tests pass unmodified.
5. `node scripts/run-stack.mjs experiments/stacks/motor-loop/stack.json --ticks 50` prints a ladder with per-level `F`, `G`, action and clock lane.

**Falsifier.** If parity cannot be reached at 1e-12 without editing `lib/uni-motor.js`, the general level is not a superset of the existing agent. Report the exact divergent term and stop; do not adjust either side to agree.

**Test that must fail first.** `tests/semantic/uni-motor-parity.semantic.test.mjs` against an adapter using `RISK_AMBIGUITY` (it must fail, proving the parity test can see the ambiguity-weight difference).

**Rollback.** Revert; the CLI and adapters are additive.

**Effort.** 3–4 days.

---

### Phase 5 — UNIEXPR, typed editing, bricks, unit algebra

**Deliverable.** `expr.js` (tokenizer, parser, typechecker, interpreter, budgets, AST-hash tamper detection, non-finite refusal); simplex-projection editors; the 24-brick registry with `canConnect`.

**Files created.** `lib/stack/expr.js(.d.ts)`, `lib/stack/bricks.js(.d.ts)`, `tests/stack/expr-grammar.test.mjs`, `tests/stack/unit-algebra.test.mjs`, `tests/stack/edit-projection.test.mjs`.
**Files changed.** `lib/stack/brick-registry.js`, `package.json`.

**Acceptance criterion.**
1. The frozen 60-row accept/reject table passes; all 12 hostile sources throw `ExprError` at the correct index.
2. Budgets throw `UXL_BUDGET_EXCEEDED`; unknown identifiers/functions throw with `{line, column}`.
3. `astSha256` is stable across parse→serialise→parse; a hand-edited AST yields `UXL_AST_MISMATCH`.
4. **`applyMap` on a NaN- or out-of-range-producing map marks the receiving level `STARVED` with `absentReason: "UXL_NON_FINITE"` and propagates nulls.** (Acceptance criterion, not a risk note.)
5. Source scan of `lib/stack/**` finds zero `eval`, `new Function`, `Function(`, dynamic `import(`, `Math.random`, `Date.now`, `fetch`.
6. `setSimplexEntry` leaves the vector on the simplex over 10⁵ random edits.
7. `canConnect` refuses every truth upgrade and returns one of the six child messages per code.

**Falsifier.** If any legal UNIEXPR program can exceed 4096 interpreter steps, reference a name outside the injected scope, or reach a host object, the authoring mechanism is an injection vector and must be replaced by pure block composition with no expression language at all.

**Test that must fail first.** `tests/stack/expr-grammar.test.mjs` clause 4, written against an `applyMap` with no finiteness check (a NaN reaches the parent's `F`).

**Rollback.** Revert; UNIEXPR is audit-only and no shipped stack depends on it. The typed forms in `edit.js` would need to move to Phase 6 if `expr.js` is dropped.

**Effort.** 5–6 days.

---

### Phase 6 — Catalog migration and the read-only tower UI

**Deliverable.** `catalog-nodes.js` + `toLegacyCatalog`; the `/stack-builder` route rendering a running tower: level cards, seams with live numerals, clock lanes, timeline, scrubber, inspector, transport bar, `detail` switch. No editing yet.

**Files created.** `lib/stack/catalog-nodes.js(.d.ts)`, `lib/stack/source-pins.js`, `app/stack-builder/page.tsx`, `stack-builder.tsx`, `level-card.tsx`, `seam.tsx`, `clock-lane.tsx`, `timeline.tsx`, `inspector.tsx`, `experiments/stacks/human-ladder/stack.json`.
**Files changed.** `app/math-workbench/scientific-math-workbench.tsx` (catalog import + one nav entry), `app/globals.css` (new `.stack-*` section appended; **no existing selector modified**), `tests/rendered-html.test.mjs`, `package.json`.

**Acceptance criterion.**
1. `JSON.stringify(toLegacyCatalog(CATALOG_NODES))` equals the frozen literal captured pre-migration; `tests/math-workbench.test.mjs` and the existing `tests/rendered-html.test.mjs` assertions are **unmodified and green**.
2. `GET /stack-builder` returns 200 and server-renders the tower.
3. The human-ladder route renders unbuilt levels with `NOT BUILT`, no sockets, and the L12 `OPEN QUESTION` caption.
4. **No inert level renders a numeric `0` for `F`, `G`, `γ` or `Π` anywhere in the HTML — only em dashes.**
5. Every rendered scalar carries a unit suffix or an em dash; every level carries a truth chip **in `play` mode too**.
6. New CSS references only the sixteen declared custom properties.
7. A source scan of `app/stack-builder/**` finds no `Math.random`, no `Date.now`, and no arithmetic on `q`/`F`/`G` beyond formatting.

**Falsifier.** If any displayed number cannot be traced to a field of a `StackState` produced by the engine, the UI has started computing science and the kernel-first contract is broken — delete the computation and move it into `lib/stack/`. If a `play`-mode render omits any truth chip, the disclosure mechanism is laundering by default and the phase must not ship.

**Test that must fail first.** The extended `tests/rendered-html.test.mjs` assertion "no inert level renders `0`", written against a first-cut card that formats `null` as `0`.

**Rollback.** Revert. The two edits to `scientific-math-workbench.tsx` are a one-line import swap and a one-entry nav append; reverting restores the inline literal exactly, and the byte-equality gate guarantees no behavioural difference either way.

**Note on the bundle-purity check.** The lego-first design's `grep dist/ for fetch(` is not implementable — the framework runtime contains `fetch`. The gate here is narrower and executable: scan **only** files under `app/stack-builder/` and `lib/stack/` for `WebGLRenderingContext`, `WebGPU`, `three`, `navigator.sendBeacon`, `XMLHttpRequest`, `fetch(`. Bundle-level purity remains an open question (§12).

**Effort.** 7–9 days. *This is the largest phase; if it must be split, ship the level card + seam + timeline first and the inspector second.*

---

### Phase 7 — Drag, snap, refusal, parameter forms, the three-click path

**Deliverable.** The brick tray, shape-based snapping with the four-tier refusal ladder, keyboard equivalents, typed parameter forms, the `F`-handle simplex drag, `UNDO`, and the starter shelf.

**Files created.** `app/stack-builder/palette.tsx`, `brick.tsx`, `param-form.tsx`, `simplex-handle.tsx`, `experiments/stacks/weather/stack.json`, `experiments/stacks/two-levels/stack.json`, `tests/stack/canconnect-messages.test.mjs`.
**Files changed.** `app/stack-builder/stack-builder.tsx`, `level-card.tsx`, `app/globals.css`.

**Acceptance criterion (executable parts only).**
1. `canConnect` returns exactly one of the six child sentences for each refusal code, asserted against a frozen table — **no schema error code appears in any returned `childMessage`**.
2. A stack with an empty required socket cannot run and the button text names the missing count.
3. An uploaded/pasted stack with an illegal connection is still rejected by `validateStack`, proving refusal is not UI-only.
4. `setSimplexEntry` and `setColumn` never emit an off-simplex vector.
5. A source scan finds no force-connect or override path in the component tree.
6. `UNDO` restores the previous `stackHash` exactly.

**Acceptance criterion (non-executable, declared as such).** The three-click path — shelf tile → STEP → swap in *Just guess* → RUN ×100 → visibly worse trajectory. **This is a manual observation, not a gate.** It is recorded in the ledger as `NOT_ESTABLISHED` until at least five children aged 7–10 complete it unaided. `node --test` cannot verify it and this plan does not pretend otherwise.

**Falsifier.** If any socket accepts a mismatched stud through any route — keyboard, paste, uploaded JSON — the geometric-impossibility claim is false. If five observed children cannot reach a running two-level stack in three clicks without help, the LEGO hypothesis is refuted and the interaction must be redesigned; record the refutation, do not restate the claim.

**Test that must fail first.** `tests/stack/canconnect-messages.test.mjs` against a `canConnect` returning bare codes rather than child sentences.

**Rollback.** Revert; Phase 6's read-only tower remains fully functional and shippable.

**Effort.** 6–8 days.

---

### Phase 8 — Variants, lineage, diff, on-disk format, git handshake

**Deliverable.** `variants.js`, `diff.js`, the diff and lineage views, export/import, `stack:canon`, `stack:verify`, `stack:import`, and prediction-record emission in the existing validated shape.

**Files created.** `lib/stack/variants.js(.d.ts)`, `lib/stack/diff.js(.d.ts)`, `app/stack-builder/diff-view.tsx`, `lineage-view.tsx`, `scripts/stack-canon.mjs`, `scripts/verify-stacks.mjs`, `scripts/import-stack-export.mjs`, `experiments/stacks/motor-loop/lineage.json`, `tests/stack/stack-hash-stability.test.mjs`, `tests/semantic/stack-lineage-integrity.semantic.test.mjs`.
**Files changed.** `package.json`.

**Acceptance criterion.**
1. `applyOps(parent, ops)` reproduces the recorded `childHash` for every shipped variant; a tampered `ops` yields `BROKEN LINEAGE` and `runExperiment` refuses it.
2. `applyOps` throws `ILLEGAL_OP_PATH` on `/__proto__`, `/constructor`, `/levels/0/truthClass`, and any path outside the whitelist.
3. `diffStacks` reports `truthAffecting` as a separate top-level field; the view renders it above everything else.
4. `stack:verify` passes on the committed tree and fails when one digit of one `stack.json` is edited.
5. An emitted prediction record satisfies every schema assertion in `tests/semantic/prospectivity-provenance.test.mjs`.
6. `adverseFindings[]` in any run record is a superset of its previous committed value.

**Falsifier.** If a stack whose ancestry does not reproduce can still be run or scored, the version-control claim is cosmetic. If the browser ever writes `prospectivity: "PROSPECTIVE"`, the prospectivity design is broken and the emitter must be removed before anything else lands.

**Test that must fail first.** `tests/semantic/stack-lineage-integrity.semantic.test.mjs` against an `applyOps` with no path whitelist (`/__proto__` succeeds).

**Rollback.** Revert; the builder loses versioning and reverts to a single-stack tool. `experiments/stacks/` artifacts remain readable.

**Effort.** 4–5 days.

---

### Phase 9 — Experiments: arms, seal, scoring, prospectivity, verdicts

**Deliverable.** `experiment.js`, `scoring.js`, `adversaries.js`; the Compare view with sealed-outcome chrome; the first real experiment `E_MOTOR_POLICY_ABLATION_V1`.

**Files created.** `lib/stack/experiment.js(.d.ts)`, `lib/stack/scoring.js(.d.ts)`, `lib/stack/adversaries.js`, `app/stack-builder/compare-view.tsx`, `experiments/designs/E_MOTOR_POLICY_ABLATION_V1.experiment.json`, `experiments/predictions/E_MOTOR_POLICY_ABLATION_V1.prediction.json`, `tests/stack/scoring.test.mjs`, `tests/semantic/stack-seal-integrity.semantic.test.mjs`, `tests/semantic/stack-experiment-completeness.semantic.test.mjs`, `tests/semantic/stack-pseudoreplication.semantic.test.mjs`.
**Files changed.** `tests/semantic/adverse-record-preservation.semantic.test.mjs`, `package.json`.

**Acceptance criterion.**
1. Holdout access before seal throws `HOLDOUT_SEALED`; `sealExperiment` throws `ALREADY_RUN` when a receipt exists for that baseline; a one-char prereg edit yields `SEAL_MISMATCH`.
2. A partial (hand-stepped) run throws `PARTIAL_RUN_CANNOT_BE_SCORED`.
3. An arm list missing `CONTROL`, `ADVERSARY`, `NEGATIVE_CONTROL` or `CHEATING_CONTROL` is unsavable.
4. **The `CHEATING_CONTROL` arm wins by a wide margin**; the `NEGATIVE_CONTROL` paired interval covers 0.
5. The bootstrap resamples exactly `nUnits` ids; duplicating events within units does not shrink the CI by > 5%; `unitField: "frameIndex"` throws.
6. `verdict()` emits both rules plus `rulesAgree`, and downgrades on `PARAMETER_NOT_RECOVERABLE`, `REFUTATION_NOT_AUTHORED`, `PARTIAL_RUN`, `CHEATING_CONTROL_DID_NOT_WIN`.
7. The browser path stamps `TIMING_UNVERIFIED`, never `PROSPECTIVE`.

**Falsifier.** If the `CHEATING_CONTROL` arm does not win by a wide margin, the score function cannot detect leakage and **no comparison result from this builder is interpretable** — halt and mark the comparison gate `BLOCKED` rather than publishing arm rankings.

**Test that must fail first.** `tests/semantic/stack-seal-integrity.semantic.test.mjs`, written against a holdout passed as a plain object (the pre-seal read succeeds).

**Rollback.** Revert; the builder reverts to exploration-only. No scored artifact would exist to orphan.

**Effort.** 5–7 days.

---

### Phase 10 — Mutation battery and gate-ledger integration

**Deliverable.** The 18-mutation frozen patch set with per-cell predicted classifications, the replay runner, the executed ledger, `stack-gates-report.json`, and `docs/STACK-BUILDER.md`.

**Files created.** `audits/phase-e/e1-stack-mutation-patch-set.v1.json`, `e1-stack-mutation-predictions.v1.json`, `tools/run-stack-mutation-replay.mjs`, `e1-stack-mutation-ledger.json`, `experiments/results/stack-gates-report.json`, `experiments/predictions/e1-stack-mutation.prediction.json`, `docs/STACK-BUILDER.md`.
**Files changed.** `package.json`, `README.md` (the README currently does not mention the math workbench at all; this adds both).

**Acceptance criterion.**
1. The patch set and its predicted classifications are committed **strictly before** the ledger, in separate commits, so the existing prospectivity gate measures `PROSPECTIVE`.
2. ≥ 16 of 18 mutations are `DETECTED_SEMANTIC` with `attributionSatisfied: true` and **zero** `DETECTED_BY_HASH_ONLY`.
3. Every survivor is recorded as an `OPEN COVERAGE HOLE` with its own falsification analysis in the ledger **and** in `docs/STACK-BUILDER.md`.
4. `stack-gates-report.json` uses the existing status vocabulary and renders in the Measured-evidence tab with **no new UI code**.
5. `docs/STACK-BUILDER.md` states the declared limitations: single-step policies; no hierarchical joint and therefore no cross-level `F` aggregation; `Pi` outside the likelihood; the one-tick message lag; `replayGuarantee: ENGINE_ONLY` for world-driven stacks; the child path `NOT_ESTABLISHED`; four Python-only modules `NOT_BUILT`; five B3 competitors `NOT IMPLEMENTED`.

**Falsifier.** If any truth-laundering, level-swap, direction-inversion, seal-bypass, control-deletion or scoring-sign mutation survives — or is detected only by a changed artifact hash — the truth-contract claims of this builder are unproven, and it ships only with the coverage hole stated in the docs and the gate ledger. If the prediction and the ledger land in one commit, the existing gate forces `TIMING_UNVERIFIED` and the phase's own prospectivity claim fails; that is the correct outcome and must not be worked around.

**Test that must fail first.** The replay runner against a deliberately weakened `joinTruth` (M-LAUNDER-1); the run must classify it `DETECTED_SEMANTIC` with the naming assertion attributed.

**Rollback.** Revert; the audit artifacts are additive and the builder is unaffected.

**Effort.** 5–7 days.

---

**Total: roughly 45–60 working days.** Phases 1–4 (≈12 days) deliver a headless, tested, demoable engine. Phase 6 (≈8 days) delivers the first screen. Phases 8–9 are **not optional polish**: shipping the builder without versioning, controls and sealing yields an instrument that can edit models but cannot version, compare or pre-register them — scientifically worse than the current workbench.

---

## 12. Open questions requiring the user's decision

1. **Multi-step policies.** v1 scores `G` over a single transition. Extending to a policy tree of depth `H` changes the schema (`policies` become sequences), the `G` recursion, and the UI. Do you want depth in scope, and at what `H`? Until you decide, the word "policy" in this builder means "one action".

2. **The hierarchical joint.** Downward messages modulate parameters; they are not a generative prior `p(x_ell | x_{ell+1})`. Consequently there is no legitimate stack-total free energy. Do you want (a) to keep parameter modulation and permanently ban cross-level `F` aggregation (current plan), or (b) to specify a real hierarchical joint, at which point `F_total` becomes meaningful and the whole engine changes shape?

3. **Precision in the likelihood.** I removed `Pi` from the `F` pass because a tempered `A^Pi` is unnormalised and breaks the `F` identity. The alternatives are: keep it out (current plan); introduce an explicitly normalised tempered likelihood with a declared temperature parameter and a modified identity; or model precision as a first-class latent with its own update. Which?

4. **Exporting `transitionPrior` and `policyTerms`.** The v1 adapter copies their literals and proves parity through `stepAgent`. Exporting them would let a builder read and edit `A`/`B` directly against the live kernel rather than a copy, but widens the module surface pinned at `tests/semantic/world-agent-observation-boundary.semantic.test.mjs:134-138`. Do you authorise that as a separate gated change?

5. **Rendering the human ladder at all.** Every mitigation proposed across all three designs is presentational (hatching, captions, `openQuestion` flags, audit-only access). A screenshot of a thirteen-storey tower with one storey lit is a claim about feasibility and ordering that nothing in this repository supports. Option: do not render unbuilt levels as a contiguous ordered ladder — show the one built level plus an **unordered, unnumbered list of named open problems**, so the tower shape cannot be photographed as a roadmap. Which do you want?

6. **Child usability evidence.** The three-click path is a hypothesis with no gate. Do you authorise an observational study (five children aged 7–10, first-run path unaided, timed, with a pre-registered falsifier), or does the child path ship permanently marked `NOT_ESTABLISHED`?

7. **Porting the Python-only modules.** X03 rotation-gated binding, X06 the 8192-state lattice, X07 the 175-state GMC generator, X09 RFT propulsion are Python+SciPy. JS oracles already exist for parts of X03, X06, X08, X09 in `scripts/independent-cross-study-check.mjs`. Porting them to the browser is a substantial separate project needing its own numerical-parity gate. Ship them permanently `NOT_BUILT` in the browser (current plan), or schedule the port?

8. **Bundle-level purity gate.** Phase 6 scans only builder source, because the framework runtime legitimately contains `fetch`. A true bundle-purity assertion needs a mechanism to exclude framework code from the scan. Do you want that mechanism specified and built, or is source-level scanning sufficient?

9. **Where the builder lives.** `app/page.tsx` currently redirects `/` to `/math-workbench`. The builder is proposed at `/stack-builder` with a nav link. Should it instead be a 7th tab inside the existing component, or eventually become the landing route?

10. **UNIEXPR at all.** It is audit-only, budgeted, totalised and tamper-checked — but it remains the only user-input-to-execution path in the product and the only place a parser bug becomes a determinism or injection hazard. The alternative is pure block composition with a slightly larger coupling-primitive registry and no expression language. Keep it, or cut it?

---

## 13. What we are NOT claiming

- **We are not claiming the L0–L12 human ladder has been built.** One level is built. L1–L12 are names with no parameters, no sockets, no numbers, no contribution to any total. A screenshot of the ladder is not evidence of progress and the builder must never present it as such.
- **We are not claiming biological parity.** `X16_FULL_BIOLOGICAL_PARITY` is a conjunction over all gates and is currently FALSE. That is a hard ceiling, not a score.
- **We are not claiming general active inference.** Policies are single-step. There is no policy tree, no temporal depth, no accumulated `G` over a horizon.
- **We are not claiming a hierarchical generative model.** No `p(x_ell | x_{ell+1})` is written down. Per-level `F` bounds a per-level surprise and nothing more. Any "total free energy of the stack" would bound nothing, which is why the engine will not compute one.
- **We are not claiming cross-engine bit-identical replay.** The hand-rolled transcendental library was cut. Replay is guaranteed on a pinned Node version and engine build; world-driven stacks are `replayGuarantee: ENGINE_ONLY` because `lib/uni-motor.js:139-198` uses `Math.exp`/`Math.sin`.
- **We are not claiming that `eps` and `xi` are variational quantities.** They are predictive-coding diagnostics carried across seams because they are legible; they have no status in the categorical `F`, and the card says so.
- **We are not claiming the builder can establish prospectivity.** The browser emits `TIMING_UNVERIFIED` or `PENDING` only. Even the git-DAG witness is defeatable by a squash, a rebase, or a hand-edited file; it is an honesty scaffold against accident and self-deception, not a cryptographic commitment. It degrades to `NOT_RUN` where git is unavailable.
- **We are not claiming a child can use this.** No usability evidence exists in this repository and this plan produces none. The three-click path, the shape vocabulary and the refusal ladder are design hypotheses recorded `NOT_ESTABLISHED` with a stated falsifier.
- **We are not claiming the mutation battery covers the space.** Eighteen named corruptions over a space of 24 bricks × 6 sockets × N levels is not exhaustive. Property-based generation of random valid stacks is an acknowledged gap, not delivered.
- **We are not claiming the four Python-only modules run in the browser.** X03, X06, X07/X08, X09 ship `NOT_BUILT`; their results come from `scripts/run-cross-study-parity.py`.
- **We are not claiming nine model competitors exist.** Five of the nine B3 densities have no implementation in any language. The builder shows **NOT IMPLEMENTED**, distinct from **NOT RUN**.
- **We are not repairing the existing adverse results.** M2 lognormal beats M3 on held-out point score. `G03_PUBLIC_ARTIFACT_PARITY` is FAIL and `scripts/independent-science-check.mjs:41` *asserts* the mismatch exceeds 0.5 relative error, so "fixing" it breaks the gate. The X06 lattice `J` disagrees between full-distribution and moment fits. Phase-C blind mutations were detected 0/10. X10 and X12 are `NOT_ESTABLISHED`; X13–X15 and G07–G09, G11–G13 are `SOURCE_ONLY` or `BLOCKED_EXTERNAL`. All of these survive into the builder unchanged and visible.
- **We are not claiming this document is verified by execution.** No test, gate, build or script was run in producing it. Every repository fact cited is read from source and committed reports, and the two acted-upon findings (private `transitionPrior`/`policyTerms`; undeclared CSS custom properties) are corroborated by two independent judges but were not confirmed by me directly.