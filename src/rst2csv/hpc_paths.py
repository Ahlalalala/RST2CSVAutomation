"""Linux/HPC path helpers for exact Workbench probe CSV export."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


@dataclass(frozen=True)
class HpcCasePaths:
    case: str
    base_dir: Path
    dat_path: Path
    rst_path: Path
    mechdb_path: Path
    dsdat_path: Path
    caerep_path: Path
    output_dir: Path
    zip_path: Path

    @classmethod
    def from_base_and_case(cls, base_dir: str | Path, case: str) -> "HpcCasePaths":
        base = Path(base_dir)
        files_root = base / "RST2CSV" / f"{case}_files"
        return cls(
            case=case,
            base_dir=base,
            dat_path=base / f"{case}.dat",
            rst_path=base / f"TaskDir_{case}" / f"{case}.rst",
            mechdb_path=files_root / "dp0" / "global" / "MECH" / "SYS.mechdb",
            dsdat_path=files_root / "dp0" / "SYS" / "MECH" / "ds.dat",
            caerep_path=files_root / "dp0" / "SYS" / "MECH" / "CAERep.xml",
            output_dir=base / "CSVResult" / case,
            zip_path=base / "CSVResult" / f"{case}.zip",
        )

    def missing_inputs(self) -> list[Path]:
        required = [
            self.dat_path,
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
