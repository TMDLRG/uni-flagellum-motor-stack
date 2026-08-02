#!/usr/bin/env bash
# Launch the CORRECTED B4C01 full-N run (D3 stable-seed fix).
#
#   bash hierarchical-aif/scripts/launch_B4C01_corrected_full.sh [N_SIM]
#
# Default: N_SIM=200 per generator (the FROZEN value) x 5 generators = 1000 simulations.
#
# Writes, all under hierarchical-aif/results/motor_stack_aif/ :
#   B4C01_CORRECTED_FULL_RESULT.json     the result (written by the harness on completion)
#   B4C01_CORRECTED_FULL_STDOUT.log
#   B4C01_CORRECTED_FULL_STDERR.log
#   B4C01_CORRECTED_FULL_COMMAND.txt
#   B4C01_CORRECTED_FULL_ENV.txt
#   B4C01_CORRECTED_FULL_PROGRESS.json   crash-recovery checkpoint, NOT a result
#
# REFUSES to overwrite an existing RESULT.json. Never touches audits/**.
#
# The prediction record was COMMITTED (28ce738) before this cell had ever run at any N.
set -euo pipefail

N_SIM="${1:-200}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RESULT_DIR="${REPO_ROOT}/hierarchical-aif/results/motor_stack_aif"
RUNNER="${REPO_ROOT}/hierarchical-aif/scripts/run_c01_corrected_full.py"
PREDICTION="${REPO_ROOT}/hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md"

BASE="B4C01_CORRECTED_FULL"
RESULT="${RESULT_DIR}/${BASE}_RESULT.json"
STDOUT_LOG="${RESULT_DIR}/${BASE}_STDOUT.log"
STDERR_LOG="${RESULT_DIR}/${BASE}_STDERR.log"
COMMAND_TXT="${RESULT_DIR}/${BASE}_COMMAND.txt"
ENV_TXT="${RESULT_DIR}/${BASE}_ENV.txt"

PY="${PYTHON:-python}"
mkdir -p "${RESULT_DIR}"

# ---- refuse to clobber an existing result ---------------------------------------------------
if [ -e "${RESULT}" ]; then
  echo "REFUSING TO RUN: ${RESULT} already exists." >&2
  echo "A corrected B4C01 result is recorded evidence and is never overwritten in place." >&2
  exit 3
fi

# ---- the prediction record must exist AND be COMMITTED before the run -----------------------
if [ ! -e "${PREDICTION}" ]; then
  echo "REFUSING TO RUN: prediction record missing: ${PREDICTION}" >&2
  exit 4
fi
if ! git -C "${REPO_ROOT}" ls-files --error-unmatch "hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md" >/dev/null 2>&1; then
  echo "REFUSING TO RUN: the prediction record is NOT COMMITTED." >&2
  echo "Per CLAUDE.md a prediction is prospective only if committed before its observation," >&2
  echo "and per defect D9 that ordering is decided by the commit graph, not by prose." >&2
  echo "Commit it first, then launch." >&2
  exit 7
fi
if [ ! -e "${RUNNER}" ]; then
  echo "REFUSING TO RUN: harness missing: ${RUNNER}" >&2
  exit 5
fi

START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo '<not-a-git-repo>')"
BRANCH="$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '<unknown>')"
PRED_COMMIT="$(git -C "${REPO_ROOT}" log --diff-filter=A --format='%H %cI' -- hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md | tail -1)"

PY_VER="$(${PY} -c 'import platform;print(platform.python_version())')"
NUMPY_VER="$(${PY} -c 'import numpy;print(numpy.__version__)' 2>/dev/null || echo '<missing>')"
SCIPY_VER="$(${PY} -c 'import scipy;print(scipy.__version__)' 2>/dev/null || echo '<missing>')"
PLATFORM="$(${PY} -c 'import platform;print(platform.platform())')"
CPUS="$(${PY} -c 'import os;print(os.cpu_count())')"
SHA () { ${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1"; }
RUNNER_SHA="$(SHA "${REPO_ROOT}/audits/phase-b/b4-identifiability-robustness-runner.py")"
HARNESS_SHA="$(SHA "${RUNNER}")"
PREDICTION_SHA="$(SHA "${PREDICTION}")"

CMD="${PY} ${RUNNER} ${N_SIM} ${RESULT}"
printf '%s\n' "${CMD}" > "${COMMAND_TXT}"

cat > "${ENV_TXT}" <<EOF
started_utc=${START_UTC}
HEAD=${HEAD_SHA}
branch=${BRANCH}
cell=B4C01_SYNTHETIC_PARAMETER_RECOVERY
harness=hierarchical-aif/scripts/run_c01_corrected_full.py (sha256 ${HARNESS_SHA})
frozen_runner_consumed=audits/phase-b/b4-identifiability-robustness-runner.py (FROZEN, UNMODIFIED, READ-ONLY, sha256 ${RUNNER_SHA})
predictionRecord=hierarchical-aif/protocols/B4C01-CORRECTED-FULL-PREDICTION.md (sha256 ${PREDICTION_SHA})
predictionRecordIntroducedBy=${PRED_COMMIT}
prospectivity=prediction record was COMMITTED while B4C01 had never run at any N (frozen artifact: status=NOT_RUN, actual_N=0)
correctionApplied=D3_HASH_SEED_NONDETERMINISM (stable_seed replaces hash(gen) % 100000)
correctionNotApplied=D1 - C01 does not use the motor-cluster bootstrap
onlyChangeFromCommittedCell=seed derivation; '+ sim' term, seed_base, generators, tolerances, self-win threshold, model set and verdict rule unchanged
n_sim_per_generator=${N_SIM}
generators=M0_EXPONENTIAL,M1_WEIBULL,M2_LOGNORMAL,M3_TWO_TIMESCALE,M5_GAMMA
seed_base=20260801
skippedModels=M4_MIXTURE_K3,M7_HIERARCHICAL_MOTOR,M8_EMPIRICAL_KDE (skipped BY CONSTRUCTION in the frozen cell)
python=${PY_VER}
numpy=${NUMPY_VER}
scipy=${SCIPY_VER}
platform=${PLATFORM}
cpu_count=${CPUS}
PYTHONHASHSEED=${PYTHONHASHSEED:-<unset>}
note=stable_seed makes this run independent of PYTHONHASHSEED (D3 fix)
note=PROGRESS.json is a crash-recovery checkpoint and is NOT a result
EOF

echo "=== B4C01 CORRECTED FULL RUN ==="
echo "n_sim=${N_SIM} per generator x 5 generators"
echo "HEAD=${HEAD_SHA}  branch=${BRANCH}"
echo "prediction record committed by: ${PRED_COMMIT}"
echo "result -> ${RESULT}"

cd "${REPO_ROOT}"
set +e
${PY} "${RUNNER}" "${N_SIM}" "${RESULT}" > "${STDOUT_LOG}" 2> "${STDERR_LOG}"
RC=$?
set -e

{
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "exit_code=${RC}"
} >> "${ENV_TXT}"

if [ ${RC} -ne 0 ]; then
  echo "RUN FAILED with exit code ${RC}. See ${STDERR_LOG}" >&2
  echo "A failed run is a reportable outcome. Do NOT read PROGRESS.json as a result." >&2
  exit ${RC}
fi

if [ -e "${RESULT}" ]; then
  RESULT_SHA="$(SHA "${RESULT}")"
  echo "result_sha256=${RESULT_SHA}" >> "${ENV_TXT}"
  echo "WROTE ${RESULT}"
  echo "sha256=${RESULT_SHA}"
else
  echo "RUN reported success but no result file was written: ${RESULT}" >&2
  exit 6
fi

tail -n 8 "${STDOUT_LOG}"
