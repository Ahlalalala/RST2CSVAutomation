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
RUNWB2_PATH="${RST2CSV_RUNWB2:-}"

CASE_NAME="$1"
if [ -z "${CASE_NAME}" ]; then
  echo "Usage: sbatch rst2csv_mechanical.slurm Void.112.510" >&2
  exit 2
fi

source "${CONDA_SH}"
conda activate "${CONDA_ENV}"

cd "${SOURCE_DIR}"
export PYTHONPATH="${SOURCE_DIR}/src"
if [ -n "${RUNWB2_PATH}" ]; then
  export RST2CSV_RUNWB2="${RUNWB2_PATH}"
fi

python -m rst2csv.cli mechanical-hpc-run "${CASE_NAME}" --base-dir "${BASE_DIR}"
