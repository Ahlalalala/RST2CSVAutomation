#!/bin/bash
set -euo pipefail

# Edit this block when the HPC layout changes.
BASE_DIR="/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop"
SOURCE_DIR="${BASE_DIR}/RST2CSVAutomation"
CONDA_SH="/opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh"
CONDA_ENV="py310"
INTEL_SETVARS="/home/software/intel/oneapi/2022.1/setvars.sh"
ANSYS_SETENV="/home/software/ansys/2025R2/setenv.sh"
RUNWB2_PATH="${RST2CSV_RUNWB2:-/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2}"
MECHANICAL_TIMEOUT_SECONDS="86400"
XAUTHORITY_PATH="${RST2CSV_XAUTHORITY:-${HOME}/.Xauthority}"

if [ "$#" -lt 1 ]; then
  echo "Usage: bash scripts/rst2csv_in_current_vnc.sh Void.40.245 [Void.67.675 ...]" >&2
  exit 2
fi

CASE_NAMES=("$@")
# Keep case names for this workflow, but do not pass them into sourced
# environment scripts such as Intel oneAPI setvars.sh.
set --

if [ -z "${DISPLAY:-}" ]; then
  LATEST_VNC_LOG="$(ls -t "${HOME}"/.vnc/*.log 2>/dev/null | head -n 1 || true)"
  if [ -n "${LATEST_VNC_LOG}" ]; then
    export DISPLAY="$(basename "${LATEST_VNC_LOG}" .log)"
  fi
fi

if [ -z "${DISPLAY:-}" ]; then
  echo "ERROR: DISPLAY is empty. Run this script from a terminal inside the VNC desktop." >&2
  exit 2
fi

if [ -f "${XAUTHORITY_PATH}" ]; then
  export XAUTHORITY="${XAUTHORITY_PATH}"
fi

DISPLAY_HOST="${DISPLAY%%:*}"
CURRENT_HOST_FULL="$(hostname -f 2>/dev/null || hostname)"
CURRENT_HOST_SHORT="$(hostname -s 2>/dev/null || hostname)"
if [ -n "${DISPLAY_HOST}" ] && [ "${DISPLAY_HOST}" != "${DISPLAY}" ] \
  && [ "${DISPLAY_HOST}" != "localhost" ] \
  && [ "${DISPLAY_HOST}" != "${CURRENT_HOST_FULL}" ] \
  && [ "${DISPLAY_HOST}" != "${CURRENT_HOST_SHORT}" ]; then
  echo "WARNING: DISPLAY host is ${DISPLAY_HOST}, current host is ${CURRENT_HOST_FULL}." >&2
  echo "Run this script inside the VNC desktop terminal, or inside an allocation on the same node." >&2
fi

if command -v xdpyinfo >/dev/null 2>&1; then
  if ! xdpyinfo -display "${DISPLAY}" >/dev/null 2>&1; then
    echo "ERROR: DISPLAY=${DISPLAY} is not reachable from current host ${CURRENT_HOST_FULL}." >&2
    echo "Run inside the VNC desktop terminal, or ask HPC support for a node-local display." >&2
    exit 2
  fi
fi

set +u
source "${CONDA_SH}"
conda activate "${CONDA_ENV}"
PYTHON_BIN="$(command -v python)"

source "${INTEL_SETVARS}"
source "${ANSYS_SETENV}"
set -u

cd "${SOURCE_DIR}"
export PYTHONPATH="${SOURCE_DIR}/src"
export RST2CSV_RUNWB2="${RUNWB2_PATH}"

echo "Using host=${CURRENT_HOST_FULL}"
echo "Using DISPLAY=${DISPLAY}"
if [ -n "${XAUTHORITY:-}" ]; then
  echo "Using XAUTHORITY=${XAUTHORITY}"
fi

for CASE_NAME in "${CASE_NAMES[@]}"; do
  echo "=== RST2CSV mechanical export: ${CASE_NAME} ==="
  "${PYTHON_BIN}" -m rst2csv.cli mechanical-hpc-run "${CASE_NAME}" \
    --base-dir "${BASE_DIR}" \
    --runwb2 "${RUNWB2_PATH}" \
    --mechanical-timeout-seconds "${MECHANICAL_TIMEOUT_SECONDS}"
done
