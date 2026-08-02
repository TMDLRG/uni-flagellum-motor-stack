/** Parametric educational UNI model export. This is not a bacterial motor CAD file. */

export const CAD_SCHEMA = "uni.flagellum.educational-cad/1.0.0";

export function createCadManifest(options = {}) {
  const moduleMm = Number(options.moduleMm ?? 2.0);
  const thicknessMm = Number(options.thicknessMm ?? 6.0);
  const clearanceMm = Number(options.clearanceMm ?? 0.28);
  const shaftMm = Number(options.shaftMm ?? 5.2);
  const encoderShaftMm = Number(options.encoderShaftMm ?? 6.2);
  const parts = [
    { id: "WORLD-ROTOR", label: "external world rotor", teeth: 48, role: "world process; physically outside the UNI enclosure", x: -95, y: 0, encoder: true },
    { id: "SIGNAL-CAM", label: "observed signal cam", teeth: 16, role: "timestamped observation crossing inward", x: -10, y: -45, encoder: true },
    { id: "PRIOR-GEAR", label: "prior log-odds dial", teeth: 32, role: "ln prior odds", x: 50, y: -70, encoder: true },
    { id: "EVIDENCE-GEAR", label: "likelihood-ratio dial", teeth: 32, role: "ln likelihood ratio", x: 50, y: 70, encoder: true },
    { id: "POSTERIOR-DIFFERENTIAL", label: "posterior differential", teeth: 48, role: "ln posterior odds = ln prior odds + ln likelihood ratio", x: 130, y: 0, encoder: true },
    { id: "POLICY-GEAR", label: "policy selector", teeth: 24, role: "softmax of negative expected free energy", x: 210, y: -50, encoder: true },
    { id: "PREDICTION-GEAR", label: "prediction output", teeth: 24, role: "predicted observation sent to Verum display", x: 210, y: 50, encoder: true },
    { id: "ACTION-CLUTCH", label: "bounded action clutch", teeth: 20, role: "RUN or TUMBLE action crossing outward", x: -10, y: 45, encoder: false },
  ].map((part) => ({
    ...part,
    moduleMm,
    pitchDiameterMm: part.teeth * moduleMm,
    outerDiameterMm: (part.teeth + 2) * moduleMm,
    thicknessMm,
    boreMm: part.encoder ? encoderShaftMm : shaftMm,
    clearanceMm,
    material: "PLA or PETG; classroom prototype only",
  }));

  return {
    schema: CAD_SCHEMA,
    identity: "UNI-FLAGELLUM physical mathematical model",
    explicitNonClaim: "This printable mechanism represents the UNI generative model and Markov boundary. It is not a scale model, structural model, or functional replica of a bacterial flagellar motor.",
    units: "millimetres",
    printProfile: {
      nozzleMm: 0.4,
      layerHeightMm: 0.2,
      walls: 3,
      infillPercent: 20,
      fitNote: "Print the tolerance coupon first. Increase clearance for printers that over-extrude.",
    },
    electronicsInterface: {
      controller: "Any local microcontroller that emits newline-delimited JSON at 115200 baud",
      encoders: "Rotary encoder or magnetic angle sensor on WORLD-ROTOR, SIGNAL-CAM, PRIOR-GEAR, EVIDENCE-GEAR, POSTERIOR-DIFFERENTIAL, POLICY-GEAR, and PREDICTION-GEAR",
      protocol: {
        required: ["t_ms", "ligand_uM", "motor_rpm", "rotation", "load_pNnm", "pmf_mV"],
        optional: ["cheyp_uM", "stators", "receptor_activity", "prior_angle_deg", "evidence_angle_deg"],
        example: { t_ms: 1250, ligand_uM: 1.12, motor_rpm: 6430, rotation: "CCW", load_pNnm: 700, pmf_mV: 150, cheyp_uM: 3.4, stators: 5 },
      },
    },
    mathematicalTransmission: {
      encoding: "theta = scale * ln(odds)",
      identity: "theta_posterior = theta_prior + theta_likelihood",
      physicalImplementation: "The v1 print exposes encoder-ready input gears and a visible posterior differential. The screen is authoritative for calculation; mechanical ratio and backlash are calibration observations, not hidden corrections.",
      falsifier: "If encoder angles plus declared calibration cannot reproduce posterior log-odds within the printed tolerance band, the physical-model claim fails until corrected.",
    },
    parts,
    assembly: [
      "Print one tolerance coupon and verify shaft and gear clearances.",
      "Print gears flat; deburr tooth flanks without changing tooth count.",
      "Mount WORLD-ROTOR on the world side of the boundary plate.",
      "Mount SIGNAL-CAM through the observation aperture; it must not directly drive internal belief gears.",
      "Mount PRIOR-GEAR and EVIDENCE-GEAR as independent encoder inputs.",
      "Mount POSTERIOR-DIFFERENTIAL, POLICY-GEAR, and PREDICTION-GEAR inside the UNI side.",
      "Mount ACTION-CLUTCH through the action aperture; no other mechanical crossing is permitted.",
      "Calibrate every encoder with the exported zero marks before accepting measurements.",
    ],
  };
}

function number(value) {
  return Number(value).toFixed(3);
}

export function openScadFromManifest(manifest) {
  const partDefinitions = manifest.parts
    .map(
      (part) => `// ${part.id}: ${part.role}\ntranslate([${number(part.x)}, ${number(part.y)}, 0])\n  spur_gear(teeth=${part.teeth}, mod=${number(part.moduleMm)}, thickness=${number(part.thicknessMm)}, bore=${number(part.boreMm)}, label_text=\"${part.id}\");`,
    )
    .join("\n\n");

  return `/*
UNI-FLAGELLUM physical mathematical model
Schema: ${manifest.schema}

NOT A BACTERIAL MOTOR CAD MODEL.
This assembly embodies the UNI priors -> evidence -> posterior -> policy ->
prediction calculation and keeps the external world on the other side of a
literal Markov-boundary plate.
*/

$fn = 72;
clearance = ${number(manifest.parts[0].clearanceMm)};

module spur_gear(teeth=24, mod=2, thickness=6, bore=5.2, label_text=\"GEAR\") {
  pitch_r = teeth * mod / 2;
  root_r = max(3, pitch_r - 1.25 * mod);
  tooth_depth = 2.25 * mod;
  tooth_arc = 2 * PI * pitch_r / teeth * 0.48;
  difference() {
    union() {
      cylinder(h=thickness, r=root_r);
      for (i=[0:teeth-1])
        rotate([0,0,i*360/teeth])
          translate([root_r + tooth_depth/2,0,thickness/2])
            cube([tooth_depth,tooth_arc,thickness],center=true);
    }
    translate([0,0,-0.5]) cylinder(h=thickness+1,r=bore/2 + clearance);
  }
  translate([0,0,thickness])
    linear_extrude(height=0.6)
      text(label_text,size=max(2,mod*1.8),halign=\"center\",valign=\"center\");
}

module markov_boundary() {
  difference() {
    translate([-10,-100,-2]) cube([12,200,12]);
    translate([-11,-68,-3]) cube([14,46,14]); // observation aperture
    translate([-11,22,-3]) cube([14,46,14]);  // action aperture
  }
  translate([-4,88,10])
    rotate([90,0,90]) linear_extrude(height=0.8)
      text(\"WORLD | OBSERVATION > UNI | ACTION >\",size=4,halign=\"center\");
}

module base_plate() {
  difference() {
    translate([-155,-120,-5]) cube([405,240,5]);
    // mounting holes
    for (x=[-143,238]) for (y=[-108,108])
      translate([x,y,-6]) cylinder(h=7,r=2.2);
  }
}

color(\"Gainsboro\") base_plate();
color(\"Orange\") markov_boundary();

${partDefinitions}

// Print parts individually by commenting out the assembly above and invoking
// spur_gear with the chosen manifest values. Validate clearances before use.
`;
}
