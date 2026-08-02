/*
UNI-FLAGELLUM physical mathematical model
Schema: uni.flagellum.educational-cad/1.0.0

NOT A BACTERIAL MOTOR CAD MODEL.
This assembly embodies the UNI priors -> evidence -> posterior -> policy ->
prediction calculation and keeps the external world on the other side of a
literal Markov-boundary plate.
*/

$fn = 72;
clearance = 0.280;

module spur_gear(teeth=24, mod=2, thickness=6, bore=5.2, label_text="GEAR") {
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
      text(label_text,size=max(2,mod*1.8),halign="center",valign="center");
}

module markov_boundary() {
  difference() {
    translate([-10,-100,-2]) cube([12,200,12]);
    translate([-11,-68,-3]) cube([14,46,14]); // observation aperture
    translate([-11,22,-3]) cube([14,46,14]);  // action aperture
  }
  translate([-4,88,10])
    rotate([90,0,90]) linear_extrude(height=0.8)
      text("WORLD | OBSERVATION > UNI | ACTION >",size=4,halign="center");
}

module base_plate() {
  difference() {
    translate([-155,-120,-5]) cube([405,240,5]);
    // mounting holes
    for (x=[-143,238]) for (y=[-108,108])
      translate([x,y,-6]) cylinder(h=7,r=2.2);
  }
}

color("Gainsboro") base_plate();
color("Orange") markov_boundary();

// WORLD-ROTOR: world process; physically outside the UNI enclosure
translate([-95.000, 0.000, 0])
  spur_gear(teeth=48, mod=2.000, thickness=6.000, bore=6.200, label_text="WORLD-ROTOR");

// SIGNAL-CAM: timestamped observation crossing inward
translate([-10.000, -45.000, 0])
  spur_gear(teeth=16, mod=2.000, thickness=6.000, bore=6.200, label_text="SIGNAL-CAM");

// PRIOR-GEAR: ln prior odds
translate([50.000, -70.000, 0])
  spur_gear(teeth=32, mod=2.000, thickness=6.000, bore=6.200, label_text="PRIOR-GEAR");

// EVIDENCE-GEAR: ln likelihood ratio
translate([50.000, 70.000, 0])
  spur_gear(teeth=32, mod=2.000, thickness=6.000, bore=6.200, label_text="EVIDENCE-GEAR");

// POSTERIOR-DIFFERENTIAL: ln posterior odds = ln prior odds + ln likelihood ratio
translate([130.000, 0.000, 0])
  spur_gear(teeth=48, mod=2.000, thickness=6.000, bore=6.200, label_text="POSTERIOR-DIFFERENTIAL");

// POLICY-GEAR: softmax of negative expected free energy
translate([210.000, -50.000, 0])
  spur_gear(teeth=24, mod=2.000, thickness=6.000, bore=6.200, label_text="POLICY-GEAR");

// PREDICTION-GEAR: predicted observation sent to Verum display
translate([210.000, 50.000, 0])
  spur_gear(teeth=24, mod=2.000, thickness=6.000, bore=6.200, label_text="PREDICTION-GEAR");

// ACTION-CLUTCH: RUN or TUMBLE action crossing outward
translate([-10.000, 45.000, 0])
  spur_gear(teeth=20, mod=2.000, thickness=6.000, bore=5.200, label_text="ACTION-CLUTCH");

// Print parts individually by commenting out the assembly above and invoking
// spur_gear with the chosen manifest values. Validate clearances before use.
