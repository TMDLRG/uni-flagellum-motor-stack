#!/usr/bin/env bash
# Launch the CORRECTED B4C11 full-N run (D1 cluster-bootstrap fix).
#
#   bash hierarchical-aif/scripts/launch_B4C11_corrected_full.sh [N_BOOT] [N_PAIRED]
#
# Defaults: N_BOOT=2000 (the FROZEN value), N_PAIRED=25 (legacy-vs-corrected diagnostic subset).
#
# Writes, all under hierarchical-aif/results/motor_stack_aif/ :
#   B4C11_CORRECTED_FULL_RESULT.json     the result (written by the harness on completion)
#   B4C11_CORRECTED_FULL_STDOUT.log
#   B4C11_CORRECTED_FULL_STDERR.log
#   B4C11_CORRECTED_FULL_COMMAND.txt
#   B4C11_CORRECTED_FULL_ENV.txt
#   B4C11_CORRECTED_FULL_PROGRESS.json   crash-recovery checkpoint, NOT a result
#
# REFUSES to overwrite an existing RESULT.json. Never touches audits/**.
#
# Prediction record (must exist and be committed BEFORE this runs):
#   hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md
set -euo pipefail

N_BOOT="${1:-2000}"
N_PAIRED="${2:-25}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
RESULT_DIR="${REPO_ROOT}/hierarchical-aif/results/motor_stack_aif"
RUNNER="${REPO_ROOT}/hierarchical-aif/scripts/run_c11_corrected_full.py"
PREDICTION="${REPO_ROOT}/hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md"

BASE="B4C11_CORRECTED_FULL"
RESULT="${RESULT_DIR}/${BASE}_RESULT.json"
STDOUT_LOG="${RESULT_DIR}/${BASE}_STDOUT.log"
STDERR_LOG="${RESULT_DIR}/${BASE}_STDERR.log"
COMMAND_TXT="${RESULT_DIR}/${BASE}_COMMAND.txt"
ENV_TXT="${RESULT_DIR}/${BASE}_ENV.txt"

PY="${PYTHON:-python}"

mkdir -p "${RESULT_DIR}"

# ---- refuse to clobber an existing result -------------------------------------------------
if [ -e "${RESULT}" ]; then
  echo "REFUSING TO RUN: ${RESULT} already exists." >&2
  echo "A corrected B4C11 result is recorded evidence and is never overwritten in place." >&2
  echo "sha256: $(${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${RESULT}" 2>/dev/null || echo '<unavailable>')" >&2
  echo "Move or rename it deliberately if a re-run is genuinely intended." >&2
  exit 3
fi

# ---- the prediction record must exist BEFORE the run --------------------------------------
if [ ! -e "${PREDICTION}" ]; then
  echo "REFUSING TO RUN: prediction record missing: ${PREDICTION}" >&2
  echo "A prospective prediction must be committed before the run that tests it." >&2
  exit 4
fi

if [ ! -e "${RUNNER}" ]; then
  echo "REFUSING TO RUN: harness missing: ${RUNNER}" >&2
  exit 5
fi

START_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HEAD_SHA="$(git -C "${REPO_ROOT}" rev-parse HEAD 2>/dev/null || echo '<not-a-git-repo>')"
BRANCH="$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo '<unknown>')"

PY_VER="$(${PY} -c 'import platform;print(platform.python_version())')"
NUMPY_VER="$(${PY} -c 'import numpy;print(numpy.__version__)' 2>/dev/null || echo '<missing>')"
SCIPY_VER="$(${PY} -c 'import scipy;print(scipy.__version__)' 2>/dev/null || echo '<missing>')"
PLATFORM="$(${PY} -c 'import platform;print(platform.platform())')"
CPUS="$(${PY} -c 'import os;print(os.cpu_count())')"
RUNNER_SHA="$(${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${REPO_ROOT}/audits/phase-b/b4-identifiability-robustness-runner.py")"
HARNESS_SHA="$(${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${RUNNER}")"
PREDICTION_SHA="$(${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${PREDICTION}")"

# SINGLE SOURCE OF TRUTH for the result path: the harness is given ${RESULT} itself, the same
# variable the overwrite-refusal check and the post-run existence check use. Never a second,
# independently-written relative path - that can silently write evidence somewhere the checks
# are not looking.
CMD="${PY} ${RUNNER} ${N_BOOT} ${RESULT} --paired ${N_PAIRED}"

cat > "${COMMAND_TXT}" <<EOF
${CMD}
EOF

cat > "${ENV_TXT}" <<EOF
started_utc=${START_UTC}
HEAD=${HEAD_SHA}
branch=${BRANCH}
cell=B4C11_M7_STRUCTURAL_IDENTIFIABILITY
harness=hierarchical-aif/scripts/run_c11_corrected_full.py (sha256 ${HARNESS_SHA})
frozen_runner_consumed=audits/phase-b/b4-identifiability-robustness-runner.py (FROZEN, UNMODIFIED, READ-ONLY, sha256 ${RUNNER_SHA})
predictionRecord=hierarchical-aif/protocols/B4C11-CORRECTED-FULL-PREDICTION.md (sha256 ${PREDICTION_SHA})
correctionApplied=D1_C11_CLUSTER_COLLAPSE (bootstrap train_by_motor: one group per DRAW, not per motorId)
correctionNotApplied=D3 - C11 seeding is arithmetic (seed_base + b), no hash(); stable_seed deliberately NOT substituted
onlyChangeFromRecordedRun=bootstrap cohort GROUPING + replicate count 30 -> ${N_BOOT} (frozen N = 2000)
n_boot=${N_BOOT}
n_paired_legacy_comparison=${N_PAIRED}
seed_base=20260717
python=${PY_VER}
numpy=${NUMPY_VER}
scipy=${SCIPY_VER}
platform=${PLATFORM}
cpu_count=${CPUS}
PYTHONHASHSEED=${PYTHONHASHSEED:-<unset>}
note=C11 U4 does not use hash(); PYTHONHASHSEED is irrelevant to this run's determinism
note=U1/U2/U3 are CARRIED_FORWARD_FROM_FROZEN_ARTIFACT, not recomputed (see prediction record section 5)
note=PROGRESS.json is a crash-recovery checkpoint and is NOT a result
EOF

echo "=== B4C11 CORRECTED FULL RUN ==="
echo "n_boot=${N_BOOT}  n_paired=${N_PAIRED}"
echo "HEAD=${HEAD_SHA}  branch=${BRANCH}"
echo "result -> ${RESULT}"
echo "cmd    -> ${CMD}"
echo "Projected runtime is recorded in the prediction record section 11. This is a long run."

cd "${REPO_ROOT}"
set +e
${PY} "${RUNNER}" \
  "${N_BOOT}" \
  "${RESULT}" \
  --paired "${N_PAIRED}" \
  > "${STDOUT_LOG}" 2> "${STDERR_LOG}"
RC=$?
set -e

END_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
{
  echo "ended_utc=${END_UTC}"
  echo "exit_code=${RC}"
} >> "${ENV_TXT}"

if [ ${RC} -ne 0 ]; then
  echo "RUN FAILED with exit code ${RC}. See ${STDERR_LOG}" >&2
  echo "A failed run is a reportable outcome. Do NOT read PROGRESS.json as a result." >&2
  exit ${RC}
fi

if [ -e "${RESULT}" ]; then
  RESULT_SHA="$(${PY} -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "${RESULT}")"
  echo "result_sha256=${RESULT_SHA}" >> "${ENV_TXT}"
  echo "WROTE ${RESULT}"
  echo "sha256=${RESULT_SHA}"
else
  echo "RUN reported success but no result file was written: ${RESULT}" >&2
  exit 6
fi

tail -n 6 "${STDOUT_LOG}"
