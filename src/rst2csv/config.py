"""User-editable default paths for the exact RST/Mechanical CSV workflow."""

from __future__ import annotations

from pathlib import Path


# Edit this block when project folders change.
BACKUP_ROOT = Path("Backup")
RST_ROOT = Path("E:/WCL/AnsysTunnel/RSTVoidBatch")
OUTPUT_ROOT = Path("GeneratedExact")
HPC_BASE_DIR = Path("/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop")
HPC_WORKBENCH_FILES_DIR_NAME = "RST2CSVFiles"
HPC_CSV_RESULT_DIR_NAME = "CSVResult"
HPC_RUNWB2_ENV_VAR = "RST2CSV_RUNWB2"
HPC_WORKBENCH_COMPONENT = "Model"
HPC_DESIGN_POINT = "dp0"
HPC_SYSTEM = "SYS"
HPC_MECHANICAL_STATUS_TIMEOUT_SECONDS = 24 * 60 * 60

ORIGIN_DATA_DIR_NAME = "OriginData"
WORKBENCH_DIR_NAME = "Workbench"
MECHDB_FILE_NAME = "SYS.mechdb"
