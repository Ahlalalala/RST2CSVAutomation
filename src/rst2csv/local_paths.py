"""Windows local path helpers for exact Workbench probe CSV export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from . import config


@dataclass(frozen=True)
class LocalCasePaths:
    case: str
    workbench_root: Path
    rst_root: Path
    output_root: Path
    design_point: str
    system: str
    files_root: Path
    rst_path: Path
    mechdb_path: Path
    dsdat_path: Path
    caerep_path: Path
    project_path: Path
    output_dir: Path
    zip_path: Path
    batch_dir: Path
    mechanical_script_path: Path
    workbench_journal_path: Path
    mechanical_status_path: Path

    @classmethod
    def from_roots(
        cls,
        workbench_root: str | Path,
        rst_root: str | Path,
        output_root: str | Path,
        case: str,
        design_point: str = config.HPC_DESIGN_POINT,
        system: str = config.HPC_SYSTEM,
    ) -> "LocalCasePaths":
        workbench = Path(workbench_root)
        rst = Path(rst_root)
        output = Path(output_root)
        files_root = workbench / f"{case}_files"
        batch_dir = output / case / "_mechanical_batch"
        return cls(
            case=case,
            workbench_root=workbench,
            rst_root=rst,
            output_root=output,
            design_point=design_point,
            system=system,
            files_root=files_root,
            rst_path=rst / f"{case}.rst",
            mechdb_path=files_root / design_point / "global" / "MECH" / f"{system}.mechdb",
            dsdat_path=files_root / design_point / system / "MECH" / "ds.dat",
            caerep_path=files_root / design_point / system / "MECH" / "CAERep.xml",
            project_path=workbench / f"{case}.wbpj",
            output_dir=output / case,
            zip_path=output / f"{case}.zip",
            batch_dir=batch_dir,
            mechanical_script_path=batch_dir / "export_probes_mechanical.py",
            workbench_journal_path=batch_dir / "run_workbench.wbjn",
            mechanical_status_path=batch_dir / "mechanical_status.txt",
        )

    def missing_inputs(self) -> list[Path]:
        required = [
            self.project_path,
            self.rst_path,
            self.mechdb_path,
            self.dsdat_path,
            self.caerep_path,
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
