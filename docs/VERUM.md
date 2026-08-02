# Verum truth surface contract

Every changing value carries these meanings:

- **WORLD TRUTH** — available only inside the synthetic world visualization;
- **OBSERVED** — crossed the declared sensor boundary with a timestamp;
- **PRIOR** — belief before the current observation;
- **LIKELIHOOD** — evidence probability under each modeled hidden state;
- **POSTERIOR** — updated belief, never world truth;
- **PREDICTED** — committed forecast for comparison with a later observation;
- **RESIDUAL** — observed minus predicted with units;
- **ACTION** — bounded outward command;
- **MODELED** — equation or parameter choice, not an observation;
- **SOURCE** — primary evidence that constrains a biological statement;
- **FENCE** — what the evidence does not establish.

The UI must never upgrade one class into another. Instrument mode hides no
missing fields: an absent CheY-P or stator measurement is rendered as “not
observed,” not filled from synthetic truth.
