// Semantic gate: the finite occupancy lattice is a PERIODIC thirteen-site ring.
//
// Frozen protocol: audits/phase-d/d1-semantic-remediation-protocol.v1.json
//   property D1P10_PERIODIC_LATTICE_TOPOLOGY.
//
// The X06 gate fits an exact finite-lattice occupancy model to published
// Franco-Onate 2025 stator occupancy distributions at three bead sizes. The lattice
// is a 13-site periodic ring: adjacency counts all THIRTEEN nearest-neighbour bonds,
// including the bond joining site 13 back to site 1. Replacing the ring with an open
// chain silently deletes one of thirteen bonds, changing the partition function, the
// fitted cooperativity J, and the structural interpretation, while the model continues
// to be described as a periodic motor ring.
//
// Oracle independence: this file is a pure JavaScript reimplementation of the DECLARED
// statistical-mechanics model. It never executes, imports or parses
// scripts/run-cross-study-parity.py. It consumes only the source-pinned observed
// distributions and the artifact's OWN reported parameters, and it recomputes the
// goodness of fit itself.
//
// Not satisfied by hash: this gate deliberately does NOT read the audit artifact's
// recorded sha256 of the Python runner. A regenerating mutant rewrites that digest with
// its own value, so a digest check would be self-healing and would degrade to hash
// identity rather than semantic correctness.
//
// Coverage provenance, stated honestly: scripts/independent-cross-study-check.mjs
// already performs an equivalent periodic recomputation. It runs under
// npm run cross-study:verify, a command OUTSIDE the semantic gate, which is why the
// Phase-C battery did not classify this corruption as detected. For this property D1 is
// primarily SUITE MEMBERSHIP MIGRATION plus a new anti-vacuity discrimination control.
//
// Target corruptions:
//   D1X10 periodic ring replaced by an open chain
//   D1A10 ring kept but coupled to NEXT-nearest neighbours, preserving both
//         periodicity and bond count

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..", "..");

const RING_SITES = 13;
const BEAD_LABELS = ["300nm", "500nm", "1300nm"];
const SSE_TOLERANCE = 1e-10;
// The periodic and open-chain fits must be separated by far more than this, otherwise
// the gate has no discriminating power and must say so rather than pass quietly.
const DISCRIMINATION_MARGIN = 1e-6;

const report = JSON.parse(
  fs.readFileSync(path.join(root, "experiments", "results", "cross-study-parity-report.json"), "utf8"),
);
const evidenceCorpus = JSON.parse(
  fs.readFileSync(path.join(root, "experiments", "data", "cross-study-motor-evidence.json"), "utf8"),
);

const gate = report.gates.find((entry) => entry.id === "X06_FINITE_LATTICE_COOPERATIVITY");

/**
 * Enumerate all 2^13 occupancy configurations.
 * neighbourOffset = 1 with wraparound is the DECLARED periodic nearest-neighbour ring.
 */
function latticeFeatures({ periodic, neighbourOffset = 1 }) {
  const size = 1 << RING_SITES;
  const count = new Float64Array(size);
  const adjacent = new Float64Array(size);
  for (let encoded = 0; encoded < size; encoded += 1) {
    let occupied = 0;
    let bonds = 0;
    for (let site = 0; site < RING_SITES; site += 1) occupied += (encoded >> site) & 1;
    const lastSite = periodic ? RING_SITES : RING_SITES - neighbourOffset;
    for (let site = 0; site < lastSite; site += 1) {
      const here = (encoded >> site) & 1;
      const there = (encoded >> ((site + neighbourOffset) % RING_SITES)) & 1;
      bonds += here * there;
    }
    count[encoded] = occupied;
    adjacent[encoded] = bonds;
  }
  return { count, adjacent };
}

/** Grand-canonical occupancy distribution P(n) for n = 0..13. */
function latticeDistribution(jValue, mu, features) {
  const { count, adjacent } = features;
  const size = count.length;
  const logWeight = new Float64Array(size);
  let peak = -Infinity;
  for (let s = 0; s < size; s += 1) {
    logWeight[s] = jValue * adjacent[s] + mu * count[s];
    if (logWeight[s] > peak) peak = logWeight[s];
  }
  const bins = new Float64Array(RING_SITES + 1);
  let partition = 0;
  for (let s = 0; s < size; s += 1) {
    const weight = Math.exp(logWeight[s] - peak);
    partition += weight;
    bins[count[s]] += weight;
  }
  return Array.from(bins, (value) => value / partition);
}

const observedDistributions = BEAD_LABELS.map((label) => {
  const raw = evidenceCorpus.studies.francoOnate2025.probabilityByBead[label];
  const total = raw.reduce((sum, value) => sum + value, 0);
  return raw.map((value) => value / total);
});

function sumSquaredResiduals(features) {
  let sse = 0;
  BEAD_LABELS.forEach((label, index) => {
    const predicted = latticeDistribution(gate.evidence.J, gate.evidence.muByBead[label], features);
    for (let occupancy = 0; occupancy <= RING_SITES; occupancy += 1) {
      const residual = predicted[occupancy] - observedDistributions[index][occupancy];
      sse += residual * residual;
    }
  });
  return sse;
}

const periodicFeatures = latticeFeatures({ periodic: true });
const openChainFeatures = latticeFeatures({ periodic: false });
const nextNearestFeatures = latticeFeatures({ periodic: true, neighbourOffset: 2 });

/**
 * A corruption that PRESERVES periodicity, ring size and nearest-neighbour coupling,
 * and breaks only the translational symmetry, by double counting a single bond.
 * Used as the discrimination control the next-nearest-neighbour ring cannot provide.
 */
function doubleCountedBondFeatures() {
  const { count, adjacent } = latticeFeatures({ periodic: true });
  const doubled = Float64Array.from(adjacent);
  for (let encoded = 0; encoded < doubled.length; encoded += 1) {
    doubled[encoded] += ((encoded >> 0) & 1) * ((encoded >> 1) & 1);
  }
  return { count, adjacent: doubled };
}
const doubleCountedFeatures = doubleCountedBondFeatures();

test("D1P10 periodic thirteen-site lattice retains its wraparound bond", () => {
  assert.ok(gate, "The X06_FINITE_LATTICE_COOPERATIVITY gate is missing from the cross-study parity report.");
  assert.equal(
    gate.evidence.observations,
    3 * (RING_SITES + 1),
    "The finite-lattice residual vector no longer has three bead conditions times fourteen occupancy bins.",
  );

  const reported = gate.evidence.sse;
  const periodicSse = sumSquaredResiduals(periodicFeatures);

  assert.ok(
    Math.abs(periodicSse - reported) < SSE_TOLERANCE,
    "The reported finite-lattice fit is not consistent with a PERIODIC thirteen-site ring at its own reported " +
      `parameters. Independently recomputed periodic sum of squared residuals ${periodicSse}, reported ${reported}, ` +
      `absolute difference ${Math.abs(periodicSse - reported)}. The lattice adjacency must include the wraparound ` +
      "bond joining site 13 to site 1; an open chain or a next-nearest-neighbour ring changes the partition " +
      "function and the fitted cooperativity while the model is still described as a periodic motor ring.",
  );
});

test("D1P10 periodic and open-chain lattice topologies are genuinely discriminated at the reported fit", () => {
  // Anti-vacuity control. If the two topologies produced nearly identical predictions
  // at the reported parameters, the check above would pass for a reason unrelated to
  // the wraparound bond. This also fires if a corruption drives the fitted J toward
  // zero, where the adjacency term vanishes and the topologies coincide.
  const periodicSse = sumSquaredResiduals(periodicFeatures);
  const openChainSse = sumSquaredResiduals(openChainFeatures);
  const doubleCountedSse = sumSquaredResiduals(doubleCountedFeatures);

  assert.ok(
    Math.abs(periodicSse - openChainSse) > DISCRIMINATION_MARGIN,
    "The periodic ring and the open chain are not discriminated at the reported lattice parameters " +
      `(difference ${Math.abs(periodicSse - openChainSse)}). Either the fitted cooperativity J has collapsed toward ` +
      "zero, where the wraparound bond carries no weight, or the finite-lattice gate has lost its power to " +
      "distinguish ring topology from open chain. In neither case may this gate be reported as passing.",
  );
  assert.ok(
    Math.abs(periodicSse - doubleCountedSse) > DISCRIMINATION_MARGIN,
    "A periodic thirteen-site ring with one nearest-neighbour bond double counted is not discriminated from the " +
      `declared ring (difference ${Math.abs(periodicSse - doubleCountedSse)}). The gate must be sensitive to the ` +
      "adjacency WEIGHTING, not merely to the presence of a wraparound.",
  );
});

test("D1P10 the lattice gate cannot detect a bond-offset relabelling, because on a prime ring it is an isomorphism", () => {
  // DECLARED LIMITATION, proven rather than assumed.
  //
  // Thirteen is prime, so for any offset k in 1..12 the map site -> k*site mod 13 is a
  // bijection carrying the offset-k cycle onto the offset-1 cycle. Occupancy count is
  // preserved by a site permutation, so the joint multiset of (count, adjacency) over
  // all 8192 configurations is IDENTICAL and the occupancy distribution is unchanged.
  //
  // A "next-nearest-neighbour ring" is therefore NOT a corruption of this model. It is
  // the same model under relabelling, and no observable can distinguish it. This gate
  // records that limit explicitly instead of pretending to cover it.
  const periodicSse = sumSquaredResiduals(periodicFeatures);
  const nextNearestSse = sumSquaredResiduals(nextNearestFeatures);

  assert.ok(
    Math.abs(periodicSse - nextNearestSse) < SSE_TOLERANCE,
    "A next-nearest-neighbour ring is expected to be INDISTINGUISHABLE from the nearest-neighbour ring on a " +
      `thirteen-site (prime) lattice, but the recomputed fits differ by ${Math.abs(periodicSse - nextNearestSse)}. ` +
      "Either the ring size is no longer prime or the adjacency enumeration is no longer a pure cycle, both of " +
      "which change the declared finite-lattice structure.",
  );
});

test("D1P10 lattice adjacency oracle counts the wraparound bond on hand-calculable configurations", () => {
  // Guards the oracle itself. A weakened oracle would silently disarm the gate above.
  const endsOnly = (1 << 0) | (1 << (RING_SITES - 1));
  const fullyOccupied = (1 << RING_SITES) - 1;
  let alternating = 0;
  for (let site = 0; site < RING_SITES; site += 2) alternating |= 1 << site;

  assert.equal(
    periodicFeatures.adjacent[endsOnly],
    1,
    "On a periodic thirteen-site ring the configuration occupying only site 1 and site 13 has exactly one " +
      "adjacent occupied pair, formed by the wraparound bond. The oracle reported otherwise.",
  );
  assert.equal(
    openChainFeatures.adjacent[endsOnly],
    0,
    "On an open chain the configuration occupying only the two end sites has zero adjacent occupied pairs. " +
      "This is the discriminating configuration between ring and open chain.",
  );
  assert.equal(
    periodicFeatures.adjacent[fullyOccupied],
    RING_SITES,
    "A fully occupied periodic ring has thirteen adjacent occupied pairs, one per bond.",
  );
  assert.equal(
    openChainFeatures.adjacent[fullyOccupied],
    RING_SITES - 1,
    "A fully occupied open chain has twelve adjacent occupied pairs.",
  );
  // Thirteen is ODD, so a maximal alternating pattern cannot close: sites 1 and 13 are
  // both occupied and are joined by the wraparound bond. This is a second independent
  // discriminating configuration between the ring and the open chain.
  assert.equal(
    periodicFeatures.adjacent[alternating],
    1,
    "On an ODD thirteen-site ring a maximal alternating occupancy pattern must contain exactly one adjacent " +
      "occupied pair, because the first and last occupied sites meet across the wraparound bond. The oracle " +
      "reported otherwise, which means the wraparound bond is missing.",
  );
  assert.equal(
    openChainFeatures.adjacent[alternating],
    0,
    "On an open chain the same alternating occupancy pattern has zero adjacent occupied pairs.",
  );
});
