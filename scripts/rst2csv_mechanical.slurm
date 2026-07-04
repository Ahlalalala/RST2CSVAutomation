#!/bin/bash

#SBATCH -p AMD_9654
#SBATCH -J RST2CSV
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 1
#SBATCH -o rst2csv_%j.out
#SBATCH -e rst2csv_%j.err
#SBATCH --no-requeue

# Edit this block when the HPC layout changes.
BASE_DIR="/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop"
SOURCE_DIR="${BASE_DIR}/RST2CSVAutomation"
CONDA_SH="/opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh"
CONDA_ENV="py310"
INTEL_SETVARS="/home/software/intel/oneapi/2022.1/setvars.sh"
ANSYS_SETENV="/home/software/ansys/2025R2/setenv.sh"
RUNWB2_PATH="${RST2CSV_RUNWB2:-/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2}"
MECHANICAL_TIMEOUT_SECONDS="86400"

CASE_NAME="$1"
if [ -z "${CASE_NAME}" ]; then
  echo "Usage: sbatch rst2csv_mechanical.slurm Void.112.510" >&2
  exit 2
fi

# Keep the case name for this workflow, but do not pass it into sourced
# environment scripts such as Intel oneAPI setvars.sh.
set --

source "${CONDA_SH}"
conda activate "${CONDA_ENV}"
PYTHON_BIN="$(command -v python)"

source "${INTEL_SETVARS}"
source "${ANSYS_SETENV}"

cd "${SOURCE_DIR}"
export PYTHONPATH="${SOURCE_DIR}/src"
export RST2CSV_RUNWB2="${RUNWB2_PATH}"

"${PYTHON_BIN}" -m rst2csv.cli mechanical-hpc-run "${CASE_NAME}" \
  --base-dir "${BASE_DIR}" \
  --runwb2 "${RUNWB2_PATH}" \
  --mechanical-timeout-seconds "${MECHANICAL_TIMEOUT_SECONDS}"
