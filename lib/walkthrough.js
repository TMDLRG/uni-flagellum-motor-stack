export const WALKTHROUGH_SCHEMA = "uni.flagellum.walkthrough/0.3.0";
export const LESSON_EXPORT_SCHEMA = "uni.flagellum.lesson-export/1.0.0";
export const WALKTHROUGH_MANIFEST_ID = "UNI-FLAGELLUM-LIVING-SCIENCE-v0.3.0";
export const RUNTIME_MODES = ["OBSERVED_REPLAY", "SYNTHETIC_WORLD", "LIVE_INSTRUMENT"];
export const TRUTH_CLASSES = ["OBSERVED", "STRUCTURAL_RECONSTRUCTION", "REDUCED_MODEL", "UNI_PHYSICAL_ANALOGUE"];

export const EVIDENCE_ASSETS = [
  {
    id: "MEARS_2014_VIDEO_1",
    kind: "video",
    evidenceType: "observed",
    sourceClass: "OBSERVED",
    species: "Escherichia coli",
    scale: "whole cell and fluorescent flagella",
    citation: "Mears et al., eLife 3:e01916 (2014), Video 1",
    doi: "10.7554/eLife.01916.010",
    href: "https://doi.org/10.7554/eLife.01916.010",
    localPath: "/media/mears-2014-run-tumble.mp4",
    sha256: "b5839132aec15ca099e9b99e6bd0f57fa26a720a97928e0a5f285eb5d9cd5050",
    license: "CC BY 4.0",
    permittedClaim: "Directly shows fluorescently labelled E. coli flagella bundling during a run, separating during a tumble, and rebundling.",
  },
  {
    id: "SINGH_2024_VIDEO_4",
    kind: "video",
    evidenceType: "reconstruction",
    sourceClass: "STRUCTURAL_RECONSTRUCTION",
    species: "Salmonella enterica serovar Typhimurium",
    scale: "MS-ring, C-ring and MotA/B",
    citation: "Singh et al., Nature Microbiology 9, 1271-1281 (2024), Supplementary Video 4",
    doi: "10.1038/s41564-024-01674-1",
    href: "https://www.nature.com/articles/s41564-024-01674-1",
    localPath: "/media/singh-2024-switching.mp4",
    sha256: "d8cff0a3536a7dd9fbf2acc5b34c815cfdf2588b83725de7f8fe04a72fd5f6e9",
    license: "CC BY 4.0",
    permittedClaim: "CryoEM-constrained visualization of CCW and CW C-ring poses and a proposed MotA/B-dependent switching mechanism.",
  },
  {
    id: "PDB_7E82",
    kind: "structure",
    evidenceType: "reconstruction",
    sourceClass: "STRUCTURAL_RECONSTRUCTION",
    species: "Salmonella enterica",
    scale: "basal body, rod and partial hook",
    citation: "PDB 7E82; Tan et al., Cell 184, 2665-2679.e19 (2021)",
    doi: "10.2210/pdb7E82/pdb",
    href: "https://www.rcsb.org/structure/7E82",
    localPath: "/data/structures/7e82.cif.gz",
    sha256: "c143331497d819b2be42b7892db80a577312ad8b4fbc50111d58e263597e8afc",
    license: "CC0 1.0",
    permittedClaim: "Constrains the labelled arrangement of rod, hook and basal-body components; it is not an E. coli whole-cell observation.",
  },
  {
    id: "PDB_6YSL",
    kind: "structure",
    evidenceType: "reconstruction",
    sourceClass: "STRUCTURAL_RECONSTRUCTION",
    species: "Bacillus subtilis",
    scale: "MotA5MotB2 stator complex",
    citation: "PDB 6YSL; Deme et al., Nature Microbiology 5, 1553-1564 (2020)",
    doi: "10.2210/pdb6YSL/pdb",
    href: "https://www.rcsb.org/structure/6YSL",
    localPath: "/data/structures/6ysl.cif.gz",
    sha256: "74386247ed1dd7a9f2d02e8b1805bea4c39b9b148ffc9c06766e92b26778c221",
    license: "CC0 1.0",
    permittedClaim: "Constrains the A5B2 stator architecture; homologous geometry is not silently presented as an E. coli measurement.",
  },
  {
    id: "WADHWA_2022_EVENTS",
    kind: "dataset",
    evidenceType: "derived",
    sourceClass: "OBSERVED",
    species: "Escherichia coli",
    scale: "single-motor stator-remodelling events",
    citation: "Wadhwa et al., Nature Communications 13, 5327 (2022)",
    doi: "10.1038/s41467-022-33075-5",
    href: "https://doi.org/10.1038/s41467-022-33075-5",
    localPath: "/wadhwa-2022-derived-events.json",
    sha256: "d119ca603621900aa4a076b110a1f43c6f01482ce891be2812634f71f597e353",
    rawSourceSha256: "c14de12cc11df8af2ab87f1ec94629eebc249c0e1475c24f850f5a28ddd1ea22",
    license: "source repository and paper terms",
    permittedClaim: "Provides motor-identified stator occupancy dwell events; it does not directly measure ligand, CheY-P or whole-cell swimming.",
  },
];

const common = {
  completion: "Make a prediction, record an observation, and state one limitation before continuing.",
};

export const WALKTHROUGH_STEPS = [
  {
    ...common,
    id: "S00_TRUTH_CONTRACT", index: 0, title: "Truth before beauty", camera: "cell", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "Separate observed media, structural reconstruction, reduced model and physical analogue before making any claim.",
    activity: "Classify each visible layer by how it was produced.",
    paper: "Draw four boxes labelled observed, reconstruction, model and analogue; put every claim in exactly one box.",
    narration: {
      what: "Two views are shown together: a recorded fluorescent cell and a separately labelled reconstruction.",
      why: "At nanometre scale, no single camera records the entire motor, bacterium and inference process at once.",
      evidence: "The observed film has a DOI, licence and frozen SHA-256. The reconstruction cites the structures that constrain it.",
      couldMean: "Agreement across views can support a mechanistic explanation.",
      doesNotEstablish: "A lifelike animation is not a new biological observation and cannot prove Active Inference identity.",
      test: "Ask whether every visible object has a provenance badge and whether species are kept separate.",
      reproduce: "Open the cited DOI, compare the same timestamps, and verify the downloaded media hash.",
      deeperMath: "Evidence class is metadata, not a probability. It constrains which likelihood and causal claims are admissible.",
    },
    evidenceIds: ["MEARS_2014_VIDEO_1", "SINGH_2024_VIDEO_4", "PDB_7E82", "PDB_6YSL"], gateIds: ["X01_SOURCE_INTEGRITY", "X11_STRUCTURAL_CONSISTENCY"],
  },
  {
    ...common,
    id: "S01_WATCH_LIFE_MOVE", index: 1, title: "Watch life move", camera: "cell", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "A fluorescent E. coli cell runs, loses its flagellar bundle, tumbles, and resumes running.",
    activity: "Before the transition, predict the first timestamp at which the bundle breaks.",
    paper: "Mark RUN and TUMBLE intervals on a 0-15 s line and calculate each interval duration.",
    narration: {
      what: "Multiple helical flagella form a bundle during a run. Direction changes disrupt the bundle and reorient the cell.",
      why: "A rotating helical bundle pushes fluid at very low Reynolds number; switching changes bundle geometry.",
      evidence: "The left film is an actual fluorescent experiment recorded at high frame rate and replayed slowly.",
      couldMean: "Coordinated switching makes whole-cell navigation robust to multiple motors.",
      doesNotEstablish: "The film does not reveal ion flow, molecular contacts or an internal probabilistic representation.",
      test: "Blind the timestamp, have two observers label run/tumble transitions, then compare inter-rater agreement.",
      reproduce: "Download Video 1 from DOI 10.7554/eLife.01916.010 and inspect the 2.4-3.4 s transition described by the authors.",
      deeperMath: "For displacement d over elapsed time dt, mean speed is v=d/dt; uncertainty must include scale-bar and frame-timing error.",
    },
    evidenceIds: ["MEARS_2014_VIDEO_1"], gateIds: ["X09_WHOLE_CELL_PROPULSION"],
  },
  {
    ...common,
    id: "S02_RECONSTRUCT_CELL", index: 2, title: "Reconstruct the swimming cell", camera: "cell", runtimeMode: "SYNTHETIC_WORLD",
    liveExperience: "A deterministic cell reconstruction moves through a ligand field while its trajectory and scale remain visible.",
    activity: "Compare the reconstruction with the observed film and list one match and one mismatch.",
    paper: "If a cell travels 12 micrometres in 0.60 seconds, calculate 20 micrometres per second.",
    narration: {
      what: "The right view is generated by declared equations, not recorded by a microscope.",
      why: "A reconstruction lets us intervene on load, PMF and policy while preserving a visible causal boundary.",
      evidence: "Its values come from the transparent CPU world process and are labelled synthetic.",
      couldMean: "A model that predicts held-out trajectories may capture useful constraints on propulsion.",
      doesNotEstablish: "Visual similarity alone is not parameter recovery or causal validation.",
      test: "Freeze parameters, predict a held-out trajectory, and compare RFT error against a constant-speed baseline.",
      reproduce: "Use the scale bar, two positions and two timestamps; compute speed without software.",
      deeperMath: "RFT closes force and torque balance: F_body + sum F_flagella = 0 and T_body + sum T_flagella = 0.",
    },
    evidenceIds: ["MEARS_2014_VIDEO_1"], gateIds: ["X09_WHOLE_CELL_PROPULSION"],
  },
  {
    ...common,
    id: "S03_ENTER_MOTOR", index: 3, title: "Enter the motor", camera: "motor", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "The view crosses the cell envelope through filament, hook, rod, bushings, MS-ring, C-ring and stators.",
    activity: "Trace torque transmission from MotA/B to FliG, FliF, rod, hook and filament.",
    paper: "Draw the envelope as three layers, then add the L-, P-, MS- and C-rings in order.",
    narration: {
      what: "A membrane motor turns a rod, flexible hook and long helical filament.",
      why: "Stators anchored around the rotor convert ion motive force into torque while bushings support the rod.",
      evidence: "The cutaway is constrained by Salmonella basal-body structure 7E82 and homologous MotA5MotB2 structure 6YSL.",
      couldMean: "Symmetry mismatch and compliant contacts may help continuous rotation and switching.",
      doesNotEstablish: "The composite is not one experimentally imaged E. coli motor; species and evidence scopes remain explicit.",
      test: "Compare every labelled part with the deposited structures and list unsupported geometry as uncertainty.",
      reproduce: "Download the two mmCIF records, verify their hashes, and make a labelled side-view sketch.",
      deeperMath: "The rotor is tens of nanometres across while the filament is micrometres long; the display changes scale and never claims one uniform magnification.",
    },
    evidenceIds: ["SINGH_2024_VIDEO_4", "PDB_7E82", "PDB_6YSL"], gateIds: ["X11_STRUCTURAL_CONSISTENCY"],
  },
  {
    ...common,
    id: "S04_IONS_TO_TORQUE", index: 4, title: "Turn ions into torque", camera: "motor", runtimeMode: "SYNTHETIC_WORLD",
    liveExperience: "Ion pulses cross MotA/B channels as stator engagement, load, rotor speed and torque update.",
    activity: "Change PMF or load, predict the speed direction, then compare with the model response.",
    paper: "For 700 pN nm through one revolution, compute W=tau*2pi = 4.398e-18 J, about 1.06e3 kBT at 300 K.",
    narration: {
      what: "Electrochemical potential drives conformational cycling in stators and transfers torque to the rotor.",
      why: "Changing load and motive force changes the mechanical operating point and stator recruitment.",
      evidence: "Observed torque-speed and stator-remodelling studies constrain trends; the live curve is a reduced model.",
      couldMean: "Mechanosensitive recruitment helps preserve torque across loads.",
      doesNotEstablish: "Thermodynamic work in joules is not variational free energy in nats.",
      test: "Measure speed under calibrated loads and PMF values, then predict new conditions without refitting.",
      reproduce: "Multiply torque in N m by angle in radians; divide by kBT only after converting units.",
      deeperMath: "W=tau*delta-theta. At 300 K, kBT is approximately 4.142e-21 J.",
    },
    evidenceIds: ["PDB_6YSL"], gateIds: ["X03_ROTATION_GATED_ASSEMBLY", "X05_TORQUE_SWITCHING_RESPONSE"],
  },
  {
    ...common,
    id: "S05_SWITCH_DIRECTION", index: 5, title: "Switch direction and behaviour", camera: "bundle", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "C-ring pose, CW/CCW labels and flagellar bundle state change together without claiming the pose was optically observed.",
    activity: "Predict whether one CW-switching flagellum will preserve or break a three-flagellum bundle.",
    paper: "With independent CW bias 0.10 for three flagella, calculate P(all CCW)=(1-0.10)^3=0.729.",
    narration: {
      what: "CCW rotation supports the normal bundled waveform; CW transitions can create semi-coiled or curly forms and a tumble.",
      why: "CheY-associated switching changes C-ring conformation and the mechanical state of each filament.",
      evidence: "Observed fluorescence shows the bundle transition; cryoEM constrains distinct C-ring poses.",
      couldMean: "Correlations among motors can make behaviour differ from independent-switch predictions.",
      doesNotEstablish: "A reconstruction of CheY binding is not a direct movie of every molecule acting in vivo.",
      test: "Compare measured tumble bias with the independent veto-model prediction across flagellar counts.",
      reproduce: "Use flagellar number N and CW bias CB to calculate the simple independent probability (1-CB)^N.",
      deeperMath: "The independence calculation is a null model; deviations motivate, but do not uniquely identify, coupling.",
    },
    evidenceIds: ["MEARS_2014_VIDEO_1", "SINGH_2024_VIDEO_4"], gateIds: ["X04_STATOR_CHEY_COUPLING", "X05_TORQUE_SWITCHING_RESPONSE"],
  },
  {
    ...common,
    id: "S06_MARKOV_BOUNDARY", index: 6, title: "Establish the boundary", camera: "inference", runtimeMode: "SYNTHETIC_WORLD",
    liveExperience: "World state remains outside; only an observation enters and only a bounded action leaves.",
    activity: "Decide which displayed quantities are sensed and which remain hidden world truth.",
    paper: "Write o_t=sensor(world_t)+epsilon and a_t in {RUN,TUMBLE}; do not copy trueGradient into o_t.",
    narration: {
      what: "The Markov boundary separates external causes from the model's beliefs.",
      why: "Without this separation, the agent could cheat by reading the answer it is supposed to infer.",
      evidence: "Automated tests reject observations containing hidden true-gradient labels.",
      couldMean: "A lawful signal/action separation is necessary for a credible inference experiment.",
      doesNotEstablish: "A software boundary does not prove that the biological cell uses the same represented states.",
      test: "Remove hidden fields, replay the same observation stream and check that predictions remain reproducible.",
      reproduce: "On paper, list world variables, observed variables, beliefs and actions in four columns.",
      deeperMath: "The observation likelihood p(o|s) links hidden state hypotheses to sensory data without revealing s.",
    },
    evidenceIds: ["WADHWA_2022_EVENTS"], gateIds: ["G01_OBSERVATION_BOUNDARY", "X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY"],
  },
  {
    ...common,
    id: "S07_UPDATE_BELIEF", index: 7, title: "Update belief in public", camera: "inference", runtimeMode: "SYNTHETIC_WORLD",
    liveExperience: "Prior, likelihood and posterior probabilities update beside their exact log-odds identity.",
    activity: "Record whether you expect ligand to rise before revealing the next observation.",
    paper: "Prior odds 2 multiplied by likelihood ratio 3 gives posterior odds 6, or conditional probability 6/7=0.857.",
    narration: {
      what: "The prior is committed before the signal; the likelihood scores the signal under each hypothesis; normalization produces the posterior.",
      why: "Separating these quantities exposes where an inference came from.",
      evidence: "The categorical update and log-odds identity are tested to machine precision.",
      couldMean: "If calibrated, posterior changes quantify evidence relative to declared alternatives.",
      doesNotEstablish: "A correct Bayesian calculation does not show that biology literally contains these variables.",
      test: "Use held-out signals and calibration curves; compare predicted probabilities with observed frequencies.",
      reproduce: "Multiply prior odds by the likelihood ratio, then convert odds O to probability O/(1+O).",
      deeperMath: "q(s|o)=eta p(o|s)q-(s), and ln Opost=ln Oprior+ln LR.",
    },
    evidenceIds: ["WADHWA_2022_EVENTS"], gateIds: ["G02_FIRST_PASSAGE_MATH", "X12_ACTIVE_INFERENCE_CAUSAL_IDENTITY"],
  },
  {
    ...common,
    id: "S08_PREDICT_CONFRONT", index: 8, title: "Predict, then confront", camera: "inference", runtimeMode: "SYNTHETIC_WORLD",
    liveExperience: "A prediction is frozen before the next signal arrives; observation and residual are then revealed.",
    activity: "State the residual sign before the observation is uncovered.",
    paper: "For observed 1.003 uM and predicted 1.023 uM, calculate residual=-0.020 uM.",
    narration: {
      what: "Prediction and observation occupy separate timestamped records.",
      why: "A prediction created after seeing the data is not a prospective test.",
      evidence: "The trace retains every prediction, observation, source and residual.",
      couldMean: "Systematic residuals identify missing dynamics or biased sensors.",
      doesNotEstablish: "A small residual in one synthetic run is not biological validation.",
      test: "Freeze parameters, score an untouched motor or laboratory, and retain adverse comparisons.",
      reproduce: "Subtract prediction from observation and retain the sign and units.",
      deeperMath: "Surprise is -ln p(o|m); a residual becomes surprise only through a declared likelihood and noise scale.",
    },
    evidenceIds: ["WADHWA_2022_EVENTS"], gateIds: ["G06_HELDOUT_MECHANISTIC_PREDICTION", "X10_CROSS_STUDY_PARAMETER_TRANSFER"],
  },
  {
    ...common,
    id: "S09_REAL_MOTOR_DATA", index: 9, title: "Test recorded motors", camera: "motor", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "A deterministic sequence of motor-identified Wadhwa holdout events replays with unmeasured fields explicitly absent.",
    activity: "Choose a model before revealing the held-out log scores.",
    paper: "If one model assigns probability 0.25 and another 0.10, log-score advantage is ln(0.25)-ln(0.10)=0.916 nat.",
    narration: {
      what: "The replay contains measured stator occupancy, event duration, direction and censoring—not invented ligand or speed.",
      why: "Motor-level holdout prevents events from the same motor leaking across fit and test sets.",
      evidence: "Nineteen untouched motors and 233 holdout events were scored after fitting only training motors.",
      couldMean: "Non-memoryless timing supports hidden-timescale structure within this protocol.",
      doesNotEstablish: "The UNI mixture did not beat every flexible alternative; lognormal scored slightly better.",
      test: "Repeat on an independent laboratory with parameters frozen before access.",
      reproduce: "For each event, compute log predicted density or log survival if censored, then average by event and bootstrap by motor.",
      deeperMath: "Right-censored dwells contribute ln S(t), never an invented transition direction.",
    },
    evidenceIds: ["WADHWA_2022_EVENTS"], gateIds: ["G04_CENSORED_JOINT_LIKELIHOOD", "G06_HELDOUT_MECHANISTIC_PREDICTION"],
  },
  {
    ...common,
    id: "S10_CROSS_STUDY", index: 10, title: "Test across studies", camera: "motor", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "Ito, Antani, GMC, RFT and structural results enter through assay-specific observation operators.",
    activity: "Separate biological units from repeated time samples before reading any sample-size claim.",
    paper: "For observed [1,2] and predicted [1.2,1.8], calculate RMSE=sqrt((0.04+0.04)/2)=0.20.",
    narration: {
      what: "Each study observes a different scale, so no single parameter table is silently treated as universal.",
      why: "Cross-scale parity requires compatible observation operators, units and independent replication.",
      evidence: "The corpus contains eleven attributed studies and a conservative lower bound of 409 independent motors or cells.",
      couldMean: "Several constrained modules reproduce their attributed observations.",
      doesNotEstablish: "Cross-laboratory parameter transfer and full structural consistency remain unestablished.",
      test: "Freeze all transferable parameters and predict a commensurate external dataset from another laboratory.",
      reproduce: "Recalculate one slope, effect size or RMSE from the downloadable source table and compare hashes.",
      deeperMath: "Assay-specific likelihoods must remain separate unless a hierarchical generative model explicitly links them.",
    },
    evidenceIds: ["SINGH_2024_VIDEO_4", "PDB_7E82", "PDB_6YSL", "WADHWA_2022_EVENTS"], gateIds: ["X02_CORPUS_BREADTH", "X10_CROSS_STUDY_PARAMETER_TRANSFER", "X11_STRUCTURAL_CONSISTENCY"],
  },
  {
    ...common,
    id: "S11_KEEP_FALSIFIER", index: 11, title: "Keep the falsifier", camera: "inference", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "Three incompatible interaction estimates for the same 13-site lattice remain visible beside the failed gate.",
    activity: "Explain why choosing the estimate closest to expectation would be invalid.",
    paper: "Compute AIC=2k+n ln(SSE/n) for J=0 and fitted J using the supplied n and SSE; retain the lower-AIC model.",
    narration: {
      what: "Full-distribution, weighted and moment summaries imply very different cooperative coupling J.",
      why: "A parameter that changes with the summary statistic is not a stable biological constant under this model.",
      evidence: "The full-distribution fit gives J about 0.211 while moment fits are near 1.1; cooperativity is not AIC-favoured.",
      couldMean: "The observable, lattice likelihood, equilibrium assumption or mapping from load class may be incomplete.",
      doesNotEstablish: "Failure of this lattice does not prove no biological cooperativity exists.",
      test: "Acquire direct occupancy distributions under matched conditions and preregister the observation model.",
      reproduce: "Fit both J=0 and free-J versions to the same full distribution, then compare residuals and AIC.",
      deeperMath: "Identifiability requires that distinct parameter values induce distinguishable distributions under the measured observable.",
    },
    evidenceIds: ["WADHWA_2022_EVENTS"], gateIds: ["X06_FINITE_LATTICE_COOPERATIVITY", "X16_FULL_BIOLOGICAL_PARITY"],
  },
  {
    ...common,
    id: "S12_REPRODUCE_CONTINUE", index: 12, title: "Reproduce and continue", camera: "inference", runtimeMode: "OBSERVED_REPLAY",
    liveExperience: "The complete gate ledger, observer notebook, source hashes, CAD analogue and unresolved physical experiments are assembled.",
    activity: "Write the strongest warranted conclusion, one alternative explanation and the next discriminating test.",
    paper: "Select one artifact, compute its SHA-256, rerun its documented command and compare the resulting gate status.",
    narration: {
      what: "Eight cross-study gates pass, three fail, two are not established and three require external physical work.",
      why: "A living scientific model must preserve failures and specify what observation could change it.",
      evidence: "Reports, protocols, source identities, code and audits are downloadable and cryptographically bound.",
      couldMean: "The current model is a reproducible partial account with concrete next experiments.",
      doesNotEstablish: "It is not full biological parity, an independently replicated wet-lab result or a validated printed instrument.",
      test: "Run calibrated live signals, independent wet-lab replication, cross-lab transfer and fabricated-model validation.",
      reproduce: "Clone the repository, install dependencies, run the science commands and compare the committed hashes and status ledger.",
      deeperMath: "The assurance cycle is DONE -> VERIFY -> PROVE -> RUN; a failed or external gate cannot be converted to PASS by narration.",
    },
    evidenceIds: ["MEARS_2014_VIDEO_1", "SINGH_2024_VIDEO_4", "PDB_7E82", "PDB_6YSL", "WADHWA_2022_EVENTS"], gateIds: ["X13_LIVE_SIGNAL_CHAIN", "X14_INDEPENDENT_WET_LAB_REPLICATION", "X15_PRINTED_MODEL_VALIDATION", "X16_FULL_BIOLOGICAL_PARITY"],
  },
];

export const REPLAY_FRAMES = [
  ["18-02-06-1505:0001", "18-02-06-1505", 6, 391.91, 5.00, 396.91, 7, "on", 1],
  ["18-02-06-1505:0002", "18-02-06-1505", 7, 396.91, 6.00, 402.91, 6, "off", -1],
  ["18-02-06-1505:0003", "18-02-06-1505", 6, 402.91, 0.86, 403.77, 7, "on", 1],
  ["18-02-06-1505:0004", "18-02-06-1505", 7, 403.77, 3.30, 407.07, 10, "on", 3],
  ["18-02-07-1612:0001", "18-02-07-1612", 2, 421.23, 2.94, 424.17, 3, "on", 1],
  ["18-02-07-1612:0002", "18-02-07-1612", 3, 424.17, 2.74, 426.91, 6, "on", 3],
  ["18-02-07-1612:0003", "18-02-07-1612", 6, 426.91, 4.74, 431.65, 7, "on", 1],
  ["18-02-07-1612:0004", "18-02-07-1612", 7, 431.65, 5.76, 437.41, 6, "off", -1],
  ["18-02-07-1612:0005", "18-02-07-1612", 6, 437.41, 0.88, 438.29, 7, "on", 1],
  ["18-02-07-1612:0006", "18-02-07-1612", 7, 438.29, 6.94, 445.23, 9, "on", 2],
  ["18-02-16-1628:0003", "18-02-16-1628", 1, 413.54, 7.08, 420.62, 4, "on", 3],
  ["18-02-16-1628:0004", "18-02-16-1628", 4, 420.62, 23.18, 443.80, 7, "on", 3],
].map(([eventId, motorId, stateN, enteredAtS, durationS, eventAtS, nextStateN, direction, jump]) => ({
  sourceId: "WADHWA_2022_EVENTS",
  eventId,
  motorId,
  partition: "holdout",
  experimentalTimeS: enteredAtS,
  measured: { stateN, durationS, eventAtS, nextStateN, direction, jump, rightCensored: false },
  missingFields: ["ligandUm", "motorSpeedRpm", "rotation", "loadPnNm", "pmfMv", "cheYpUm"],
  citation: "10.1038/s41467-022-33075-5",
}));

export function getReplayFrame(index) {
  const normalized = ((Number(index) || 0) % REPLAY_FRAMES.length + REPLAY_FRAMES.length) % REPLAY_FRAMES.length;
  return REPLAY_FRAMES[normalized];
}

export function truthClassForMode(mode) {
  if (mode === "OBSERVED_REPLAY" || mode === "LIVE_INSTRUMENT") return "OBSERVED";
  return "REDUCED_MODEL";
}

export function paperExampleResults() {
  const kbt300 = 1.380649e-23 * 300;
  const workJ = 700e-21 * Math.PI * 2;
  return {
    cellSpeedUmS: 12 / 0.6,
    revolutionWorkJ: workJ,
    revolutionWorkKbt: workJ / kbt300,
    allCcwProbability: (1 - 0.1) ** 3,
    posteriorOdds: 2 * 3,
    posteriorConditionalProbability: 6 / 7,
    residualUm: 1.003 - 1.023,
    logScoreAdvantageNat: Math.log(0.25) - Math.log(0.10),
    rmse: Math.sqrt(((1 - 1.2) ** 2 + (2 - 1.8) ** 2) / 2),
  };
}

export function createObserverRecord(input) {
  const step = WALKTHROUGH_STEPS.find((candidate) => candidate.id === input.stepId);
  if (!step) throw new Error(`Unknown walkthrough step: ${input.stepId}`);
  if (!RUNTIME_MODES.includes(input.runtimeMode)) throw new Error(`Unknown runtime mode: ${input.runtimeMode}`);
  return {
    schema: "uni.flagellum.observer-record/1.0.0",
    sessionId: String(input.sessionId),
    stepId: step.id,
    recordedAt: input.recordedAt || new Date().toISOString(),
    runtimeMode: input.runtimeMode,
    truthClass: truthClassForMode(input.runtimeMode),
    inputState: input.inputState || {},
    prediction: String(input.prediction || ""),
    observation: String(input.observation || ""),
    calculation: String(input.calculation || ""),
    interpretation: String(input.interpretation || ""),
    alternativeExplanation: String(input.alternativeExplanation || ""),
    confidence: Math.max(0, Math.min(100, Number(input.confidence) || 0)),
    evidenceIds: [...step.evidenceIds],
    gateIds: [...step.gateIds],
    applicationCommit: input.applicationCommit || "WORKTREE",
    modelRunId: input.modelRunId || null,
    datasetHashes: input.datasetHashes || {},
  };
}

export function createLessonExport(records, metadata = {}) {
  return {
    schema: LESSON_EXPORT_SCHEMA,
    walkthroughSchema: WALKTHROUGH_SCHEMA,
    manifestId: WALKTHROUGH_MANIFEST_ID,
    exportedAt: metadata.exportedAt || new Date().toISOString(),
    applicationCommit: metadata.applicationCommit || "WORKTREE",
    modelRunId: metadata.modelRunId || null,
    gateStatusCounts: metadata.gateStatusCounts || {},
    evidenceHashes: Object.fromEntries(EVIDENCE_ASSETS.filter((asset) => asset.sha256).map((asset) => [asset.id, asset.sha256])),
    steps: WALKTHROUGH_STEPS.map(({ id, index, title, evidenceIds, gateIds }) => ({ id, index, title, evidenceIds, gateIds })),
    records: records.map((record) => ({ ...record })),
    reproduction: [
      "npm ci",
      "npm test",
      "npm run science:verify",
      "npm run cross-study:verify",
    ],
  };
}

export function validateLessonExport(value) {
  const errors = [];
  if (!value || typeof value !== "object") return { valid: false, errors: ["Export must be an object."] };
  if (value.schema !== LESSON_EXPORT_SCHEMA) errors.push("Lesson export schema mismatch.");
  if (value.walkthroughSchema !== WALKTHROUGH_SCHEMA) errors.push("Walkthrough schema mismatch.");
  if (value.manifestId !== WALKTHROUGH_MANIFEST_ID) errors.push("Walkthrough manifest mismatch.");
  if (!Array.isArray(value.steps) || value.steps.length !== WALKTHROUGH_STEPS.length || value.steps.some((step, index) => step.id !== WALKTHROUGH_STEPS[index].id || step.index !== index)) errors.push("Walkthrough step manifest mismatch.");
  const expectedHashes = Object.fromEntries(EVIDENCE_ASSETS.filter((asset) => asset.sha256).map((asset) => [asset.id, asset.sha256]));
  if (!value.evidenceHashes || Object.entries(expectedHashes).some(([id, hash]) => value.evidenceHashes[id] !== hash)) errors.push("Evidence hash manifest mismatch.");
  if (!Array.isArray(value.records)) errors.push("Records must be an array.");
  else {
    for (const record of value.records) {
      const step = WALKTHROUGH_STEPS.find((candidate) => candidate.id === record.stepId);
      if (!step) errors.push(`Unknown record step ${record.stepId}.`);
      if (!RUNTIME_MODES.includes(record.runtimeMode)) errors.push(`Unknown record runtime mode ${record.runtimeMode}.`);
      if (record.truthClass !== truthClassForMode(record.runtimeMode)) errors.push(`Truth class mismatch for ${record.stepId}.`);
      if (!record.sessionId || !record.recordedAt || !record.applicationCommit) errors.push(`Incomplete audit identity for ${record.stepId}.`);
      if (step && JSON.stringify(record.evidenceIds) !== JSON.stringify(step.evidenceIds)) errors.push(`Evidence trace mismatch for ${record.stepId}.`);
      if (step && JSON.stringify(record.gateIds) !== JSON.stringify(step.gateIds)) errors.push(`Gate trace mismatch for ${record.stepId}.`);
      if (!record.datasetHashes || Object.entries(expectedHashes).some(([id, hash]) => record.datasetHashes[id] !== hash)) errors.push(`Dataset hash trace mismatch for ${record.stepId}.`);
    }
  }
  return { valid: errors.length === 0, errors };
}

function csvCell(value) {
  const text = String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

export function recordsToCsv(records) {
  const columns = ["sessionId", "stepId", "recordedAt", "runtimeMode", "truthClass", "prediction", "observation", "calculation", "interpretation", "alternativeExplanation", "confidence"];
  return [columns.join(","), ...records.map((record) => columns.map((column) => csvCell(record[column])).join(","))].join("\n") + "\n";
}

export function validateWalkthrough() {
  const errors = [];
  const assetIds = new Set(EVIDENCE_ASSETS.map((asset) => asset.id));
  if (WALKTHROUGH_STEPS.length !== 13) errors.push("Walkthrough must contain exactly 13 ordered steps.");
  WALKTHROUGH_STEPS.forEach((step, index) => {
    if (step.index !== index) errors.push(`Non-contiguous step index at ${step.id}.`);
    if (step.evidenceIds.some((id) => !assetIds.has(id))) errors.push(`Unknown evidence reference in ${step.id}.`);
    if (!RUNTIME_MODES.includes(step.runtimeMode)) errors.push(`Unknown runtime mode in ${step.id}.`);
  });
  const structuralSpecies = new Set(EVIDENCE_ASSETS.filter((asset) => asset.kind === "structure").map((asset) => asset.species));
  if (structuralSpecies.size < 2) errors.push("Structural evidence must retain cross-species labels.");
  if (EVIDENCE_ASSETS.some((asset) => asset.sourceClass === "OBSERVED" && asset.kind === "structure")) errors.push("Deposited structures cannot be labelled direct whole-cell observations.");
  return { valid: errors.length === 0, errors };
}
