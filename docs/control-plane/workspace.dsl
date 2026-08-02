workspace "UNI Platform" "Digital-life research colony plus the live broadcast platform that puts it on air. C4 model of record." {

    !identifiers hierarchical

    model {
        michael = person "Michael" "Regenerative architect and organic operator. Present inside every body, not a dashboard recipient. Types go-live personally." "Operator"
        reviewer = person "External reviewer" "Independent scientific or release reviewer. Receives evidence packages; never has write access." "External"
        audience = person "Audience" "Public viewers of the science broadcast." "External"

        platform = softwareSystem "UNI Platform" "The four bodies, the colony, the studio and the evidence spine." {

            door = container "The Door" "Admission, release, key custody and the journey. LAW: a polled read never spawns anything; every actuation is a deliberate click or an explicit verb." "Node.js / launcher.cjs :8090" "Built"
            controlPlane = container "The Control Plane" "Runs the science and authors every verdict, across every project. THIS IS THE LAB. Phase 2 landed Ledger, GateRow, Command and Drift; Registry, Verdict, Run, Pair, Room and Scene are not built." "Elixir / SP.ControlPlane, root zero-dep app" "PartlyBuilt" {
                cpCommand  = component "Command" "The ONLY writer. Records actor, role, utc, unix_ns, prior, transition, authorization, evidence, resulting, hash. Inherits the Door's law: a read never actuates." "Elixir, phase 2" "Built"
                cpLedger   = component "Ledger" "Append-only, hash-chained via prev_hash. verify/1 walks the chain; tampering any past entry fails it. History is extended, never edited." "Elixir, phase 2" "Built"
                cpGateRow  = component "GateRow" "Builds and validates a row against gate_row.schema.json in hand-written Elixir with stdlib JSON. supersedes chains a revision without mutating what it supersedes." "Elixir, phase 2" "Built"
                cpRegistry = component "Registry" "Registers a gate BEFORE its run, with pass_condition, falsifies_condition and pre_registration_path. Refuses a verdict with no registered gate." "Elixir, phase 3" "Built"
                cpVerdict  = component "Verdict" "Authors PASS|PARTIAL|FAIL|WITHHELD|PENDING only. Refuses a percent score and a PARTIAL that does not name its holding sub-claim." "Elixir, phase 3" "Built"
                cpAnchor   = component "Anchor" "Holds the expected head and length OUTSIDE the chain. A hash chain cannot detect truncation from its own tail; a prefix of a valid chain is a valid chain." "Elixir, phase 3" "Built"
                cpStore    = component "Store" "Durable append-only persistence. Until it exists the Control Plane cannot record its own mutations and nothing holds an anchor across a restart." "Elixir, phase 4" "Built"
                cpRun      = component "Run" "Immutable run identity: code identity, env identity, inputs, params, seeds, start/end in unix_ns and UTC, exit code, output hashes." "Elixir, phase 4" "Built"
                cpPair     = component "Pair" "Enforces exactly one differing variable between arms. Two differences mark the run VOID and unclaimable." "Elixir, phase 4" "Built"
                cpDrift    = component "Drift" "Like-for-like comparison only. Refuses a cross-type comparison AT CONSTRUCTION, so the Phase 1 defect cannot recur." "Elixir, phase 2" "Built"
                cpWitness  = component "Witness" "An anchor the ledger's writer cannot reach. A local anchor cannot outrank a local writer: a tamperer who owns the store directory can truncate the ledger and rewrite its anchor to match." "Elixir, phase 5" "Built"
                cpRoom     = component "Room + Key" "green to clean to sterile, two keys per airlock. A failed condition names the missing receipt. No override path." "Elixir, phase 6" "Built"
                cpScene    = component "Scene" "Pure function of state. Every node carries truth_class, receipt_ref, evidence_class, captured_at. A node missing them renders as fog." "Elixir, phase 7" "NotBuilt"
            }
            labView = container "The Lab View" "The immersive rendered room the operator works inside. Proposes commands; never writes. Rooms, airlocks, world portals, Gaia overhead." "Phoenix LiveView + THREE.js on T1000" "NotBuilt"
            gaia = container "Gaia" "World-visibility organ. 308 live signals, 0 provenance-incomplete, 5 drift signals. LAW: never summarizes, scores, ranks, narrates, authors a verdict, or acts outward." "Node.js / gaia_server.cjs :8096 + read-only MCP" "Built"
            hud = container "The HUD" "What the operator sees and carries. LAW: never fabricates a state; unknown renders SYNCING." "WPF widget + JSON service :8100" "Built"

            colony = container "Colony world" "Minecraft world plus the Phoenix FEP brain and body.js bots. The subject of the science." "Elixir / lib/sp + paper.jar :25565" "Built"
            overlooker = container "Overlooker" "The colony's own omniscient per-tick god-view with a Markov-blanket monitor that re-derives per tick that the agent received only the opaque observation." "Phoenix LiveView + world.js THREE" "Built"
            commandCenter = container "Colony control center" "Live-television vision mixer for the colony: preview, take, cut, cue, projector, overlay, fanout, golive, offair." "Node.js / command_center.cjs :8098" "Built"
            cameras = container "Cameras and compositor" "Director follow-cam, prismarine colony cam, overlay server and the single-page broadcast composite." "Node.js + Chrome :3020 :8099" "Built"
            encoder = container "Encoder" "One render and one encode on the T1000, out as a single RTMP stream." "OBS + MediaMTX :1935" "Built"
            relay = container "Fan-out relay" "Tees one incoming stream to many endpoints. No encode, no colony." "Podman / uni-bcast-relay" "Built"

            gatesLedger = container "Gate ledger" "Append-only record of every registered gate and its verdict. 206 rows, 109 unique, 1 FAIL." "NDJSON / evidence/gates.ndjson" "Store"
            receipts = container "Receipt store" "Content-addressed artifacts, commit ids and logs that reproduce each claim." "Filesystem + sha256" "Store"
            approvals = container "Approval queue" "One human approve or deny per mutating call." "systemd / uni-approvald" "Built"
            flagellum = container "Flagellum project" "Bacterial flagellar-motor science. Separate repo, CPU-only build, no WebGL or network." "Next.js on Cloudflare Worker :8790 :8791" "Built"
        }

        broadcastTargets = softwareSystem "Streaming platforms" "YouTube, Twitch and up to twenty endpoints." "External"

        michael -> platform.door "Crosses once, on the way in"
        michael -> platform.labView "Works inside. Authors verdicts. Stops runs."
        michael -> platform.hud "Carries"
        michael -> platform.commandCenter "Types go-live by hand (G-PA)"
        michael -> platform.approvals "Co-signs each mutating call"
        reviewer -> platform.receipts "Receives evidence packages"
        audience -> broadcastTargets "Watches"

        platform.controlPlane.cpCommand -> platform.controlPlane.cpLedger "Appends one entry per mutation"
        platform.controlPlane.cpCommand -> platform.controlPlane.cpGateRow "Builds and validates a row"
        platform.controlPlane.cpRegistry -> platform.controlPlane.cpCommand "Registers a gate before its run"
        platform.controlPlane.cpVerdict -> platform.controlPlane.cpCommand "Authors a verdict"
        platform.controlPlane.cpRun -> platform.controlPlane.cpPair "Checks exactly one variable differs"
        platform.controlPlane.cpRun -> platform.controlPlane.cpCommand "Records run identity"
        platform.controlPlane.cpRoom -> platform.controlPlane.cpCommand "Records an airlock transition"
        platform.controlPlane.cpScene -> platform.controlPlane.cpLedger "Reads state to build the scene"
        platform.controlPlane.cpDrift -> platform.controlPlane.cpLedger "Compares like with like"
        platform.controlPlane.cpAnchor -> platform.controlPlane.cpLedger "Attests the head the chain cannot hold"
        platform.controlPlane.cpStore -> platform.controlPlane.cpLedger "Persists and reloads, append-only"
        platform.controlPlane.cpRun -> platform.controlPlane.cpPair "Offers an arm for pairing"
        platform.controlPlane.cpWitness -> platform.controlPlane.cpStore "Holds the anchor out of the writer's reach"
        platform.gaia -> platform.controlPlane.cpStore "Projects the Control Plane ledger VERBATIM (seat control-plane)"
        platform.door -> platform.controlPlane "Admits and releases"
        platform.controlPlane -> platform.labView "Pushes a compact scene per tick"
        platform.labView -> platform.controlPlane "Explicit verbs only. No hover or poll actuates."
        platform.controlPlane -> platform.gatesLedger "Appends a gate row. Never edits."
        platform.controlPlane -> platform.receipts "Writes a receipt per decision"
        platform.controlPlane -> platform.approvals "Requests the human co-sign"
        platform.controlPlane -> platform.colony "Starts and stops paired runs"
        platform.controlPlane -> platform.flagellum "Runs gates and guards"

        platform.gaia -> platform.gatesLedger "Projects rows verbatim"
        platform.gaia -> platform.receipts "Projects artifacts with sha256"
        platform.gaia -> platform.door "Projects register and journey"
        platform.gaia -> platform.controlPlane "Projects the ledger. Read-only."
        platform.gaia -> platform.colony "Probes and projects. Never actuates."

        platform.hud -> platform.gaia "Reads signals"
        platform.hud -> platform.door "Reads state"
        platform.hud -> platform.controlPlane "Reads run state"
        platform.labView -> platform.gaia "Renders signals overhead. Cannot act on them."
        platform.labView -> platform.overlooker "Looks through the colony portal. Never reimplements it."

        platform.colony -> platform.overlooker "Emits an observer frame each tick"
        platform.colony -> platform.cameras "Is captured over the LAN"
        platform.cameras -> platform.encoder "Feeds one composite"
        platform.commandCenter -> platform.encoder "Switches scenes, cuts, takes"
        platform.encoder -> platform.relay "One RTMP stream"
        platform.relay -> broadcastTargets "Fans out"

        prod = deploymentEnvironment "Fleet" {
            chip = deploymentNode "The chip - uni-lab" "10.190.245.122, rootless. The colony, always. Zero broadcast." "UNI-OS" {
                containerInstance platform.colony
                containerInstance platform.overlooker
                containerInstance platform.approvals
                containerInstance platform.flagellum
                containerInstance platform.gatesLedger
                containerInstance platform.receipts
            }
            thinker = deploymentNode "THINKER" "10.190.245.196, NVIDIA T1000. Portable studio. Captures the colony; hosts none of it." "Windows 11" {
                containerInstance platform.door
                containerInstance platform.gaia
                containerInstance platform.hud
                containerInstance platform.controlPlane
                containerInstance platform.labView
                containerInstance platform.cameras
                containerInstance platform.commandCenter
                containerInstance platform.encoder
            }
            node2 = deploymentNode "node2 - uni-lab-79740c" "Mesh 10.13.13.3. Fan-out only." "UNI-OS" {
                containerInstance platform.relay
            }
        }
    }

    views {
        systemContext platform "Context" "Who uses the platform and what it talks to." {
            include *
            autolayout lr
        }

        container platform "Bodies" "The four bodies, the colony stack and the evidence stores." {
            include *
            autolayout tb
        }

        container platform "EvidenceSpine" "Only the path a claim travels to become evidence." {
            include michael platform.controlPlane platform.gatesLedger platform.receipts platform.gaia platform.hud platform.labView platform.approvals
            autolayout lr
        }

        component platform.controlPlane "ControlPlaneComponents" "Inside the Control Plane: what gets built, and in which phase." {
            include *
            autolayout tb
        }

        deployment platform "Fleet" "FleetDeployment" "Which body runs on which machine." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                shape person
                background "#534ab7"
                color "#ffffff"
            }
            element "Operator" {
                background "#3c3489"
                color "#ffffff"
            }
            element "External" {
                background "#8a6a1a"
                color "#ffffff"
            }
            element "Container" {
                shape roundedbox
                background "#f7f8fa"
                color "#16181d"
            }
            element "Built" {
                background "#e8f4ef"
                stroke "#0f6e56"
                color "#16181d"
            }
            element "PartlyBuilt" {
                background "#fdf8e8"
                stroke "#9a7b12"
                color "#16181d"
            }
            element "NotBuilt" {
                background "#fdf1ee"
                stroke "#b4442f"
                color "#16181d"
                border dashed
            }
            element "Store" {
                shape cylinder
                background "#eef0fb"
                stroke "#534ab7"
            }
            element "Software System" {
                background "#1d2026"
                color "#ffffff"
            }
        }
    }
}
