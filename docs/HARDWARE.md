# Live instrument and physical UNI model

## Serial measurement contract

The laboratory reads UTF-8, newline-delimited JSON at 115200 baud. Each complete
line is validated before crossing the Markov boundary.

Required fields:

```json
{
  "t_ms": 1250,
  "ligand_uM": 1.12,
  "motor_rpm": 6430,
  "rotation": "CCW",
  "load_pNnm": 700,
  "pmf_mV": 150
}
```

Optional fields are `cheyp_uM`, `stators`, `receptor_activity`,
`prior_angle_deg`, and `evidence_angle_deg`. Unknown fields are retained only in
the raw-frame display and have no model authority.

The browser attaches `receivedAtMs` independently from device time. A frame
with missing, non-finite or invalid rotation fields is rejected and displayed
as rejected evidence.

## Physical mathematical model

The model has eight labeled parts:

1. external WORLD-ROTOR;
2. inward SIGNAL-CAM;
3. PRIOR-GEAR;
4. EVIDENCE-GEAR;
5. POSTERIOR-DIFFERENTIAL;
6. POLICY-GEAR;
7. PREDICTION-GEAR;
8. outward ACTION-CLUTCH.

A literal boundary plate has only two apertures: observation inward and action
outward. There is no direct shaft from the world rotor to the internal belief
gears.

## Classroom measurement

Rotary encoders or magnetic angle sensors can be mounted in the declared bores.
The microcontroller maps encoder angles to prior and evidence log-odds, emits a
serial observation, and receives no hidden world state from the browser.

The initial mechanical identity is:

```
theta_posterior = theta_prior + theta_likelihood
```

The screen computes the exact Bayesian identity and shows encoder error,
backlash and calibration residual. The v1 printed differential is an
educational mechanism and requires physical validation before it can be called
a mechanical calculator.

## Fabrication gates

1. Print a bore/shaft/gear tolerance coupon.
2. Measure actual dimensions with calipers.
3. Record fit, backlash and printer/material settings.
4. Regenerate with corrected clearance; never sand away evidence silently.
5. Print each gear separately and confirm free rotation.
6. Assemble the boundary and verify that no undeclared crossing exists.
7. Install encoders and calibrate zero, direction and angle scale.
8. Compare physical and on-screen log-odds across the full safe travel.
9. Preserve the calibration dataset and declare the valid uncertainty band.
10. Use adult supervision for small parts, electronics and rotating mechanisms.

The OpenSCAD file is a conversion-ready parametric starting point. It is not a
certified consumer product or a promise of successful printing on every
machine.

