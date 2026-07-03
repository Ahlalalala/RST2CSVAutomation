"""Linux/HPC path helpers for exact Workbench probe CSV export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from . import config


@dataclass(frozen=True)
class HpcCasePaths:
    case: str
    base_dir: Path
    design_point: str
    system: str
    dat_path: Path
    rst_path: Path
    mechdb_path: Path
    dsdat_path: Path
    caerep_path: Path
    project_path: Path
    output_dir: Path
    zip_path: Path
    batch_dir: Path
    probe_text_dir: Path
    mechanical_script_path: Path
    workbench_journal_path: Path
    mechanical_status_path: Path

    @classmethod
    def from_base_and_case(
        cls,
        base_dir: str | Path,
        case: str,
        design_point: str = config.HPC_DESIGN_POINT,
        system: str = config.HPC_SYSTEM,
    ) -> "HpcCasePaths":
        base = Path(base_dir)
        files_root = base / config.HPC_WORKBENCH_FILES_DIR_NAME / f"{case}_files"
        return cls(
            case=case,
            base_dir=base,
            design_point=design_point,
            system=system,
            dat_path=base / f"{case}.dat",
            rst_path=base / f"TaskDir_{case}" / f"{case}.rst",
            mechdb_path=files_root / design_point / "global" / "MECH" / f"{system}.mechdb",
            dsdat_path=files_root / design_point / system / "MECH" / "ds.dat",
            caerep_path=files_root / design_point / system / "MECH" / "CAERep.xml",
            project_path=base / config.HPC_WORKBENCH_FILES_DIR_NAME / f"{case}.wbpj",
            output_dir=base / config.HPC_CSV_RESULT_DIR_NAME / case,
            zip_path=base / config.HPC_CSV_RESULT_DIR_NAME / f"{case}.zip",
            batch_dir=base / config.HPC_CSV_RESULT_DIR_NAME / case / "_mechanical_batch",
            probe_text_dir=base / config.HPC_CSV_RESULT_DIR_NAME / case / "_mechanical_batch" / "probe_txt",
            mechanical_script_path=(
                base
                / config.HPC_CSV_RESULT_DIR_NAME
                / case
                / "_mechanical_batch"
                / "export_probes_mechanical.py"
            ),
            workbench_journal_path=(
                base
                / config.HPC_CSV_RESULT_DIR_NAME
                / case
                / "_mechanical_batch"
                / "run_workbench.wbjn"
            ),
            mechanical_status_path=(
                base
                / config.HPC_CSV_RESULT_DIR_NAME
                / case
                / "_mechanical_batch"
                / "mechanical_status.txt"
            ),
        )

    def missing_inputs(self) -> list[Path]:
        required = [
            self.dat_path,
            self.rst_path,
            self.mechdb_path,
            self.dsdat_path,
            self.caerep_path,
            self.project_path,
        ]
        return [path for path in required if not path.exists()]

    def require_inputs(self) -> None:
        missing = self.missing_inputs()
        if missing:
            raise FileNotFoundError(2, "No such file or directory", str(missing[0]))

    def zip_output_dir(self) -> Path:
        self.zip_path.parent.mkdir(parents=True, exist_ok=True)
        face_csvs = sorted(self.output_dir.glob("FaceAccel_*.CSV"))
        with ZipFile(self.zip_path, "w", compression=ZIP_DEFLATED) as archive:
            for csv_path in face_csvs:
                archive.write(csv_path, arcname=f"{self.case}/{csv_path.name}")
        return self.zip_path
