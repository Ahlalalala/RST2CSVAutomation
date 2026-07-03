#!/bin/bash

#SBATCH -p AMD_9654
#SBATCH -J RST2CSV
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 32
#SBATCH -o rst2csv_%j.out
#SBATCH -e rst2csv_%j.err
#SBATCH --no-requeue

set -euo pipefail

source /opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh
conda activate py310

BASE=/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
CASE=Void.112.510
DESIGN_POINT=dp0
SYSTEM=SYS

CODE_DIR="$BASE/RST2CSVAutomation"
DEPS_DIR="$BASE/RST2CSVDeps/python"
WHEELHOUSE="$BASE/RST2CSVDeps/wheelhouse"

cd "$CODE_DIR"

echo "Python executable: $(which python)"
python --version

mkdir -p "$DEPS_DIR"

if ! PYTHONPATH="$CODE_DIR/src:$DEPS_DIR" python -m rst2csv.cli check; then
  if [ -d "$WHEELHOUSE" ]; then
    python -m pip install --upgrade --target "$DEPS_DIR" --no-index --find-links "$WHEELHOUSE" -r requirements-hpc.txt
  else
    python -m pip install --upgrade --target "$DEPS_DIR" -r requirements-hpc.txt
  fi
fi

export PYTHONPATH="$CODE_DIR/src:$DEPS_DIR"
python -m rst2csv.cli check
python -m rst2csv.cli hpc-run "$CASE" --base-dir "$BASE" --design-point "$DESIGN_POINT" --system "$SYSTEM"
