"""Command-line interface for the RST to CSV workflow."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import time

from . import config
from .mechdb_cache import (
    MissingMechdbCacheDependency,
    export_cached_probe_csvs,
    load_probe_histories_from_mechdb,
)
from .hpc_paths import HpcCasePaths
from .mechanical_batch import (
    MechanicalBatchConfig,
    find_runwb2,
    run_workbench_batch,
    write_mechanical_batch_files,
)
from .rst_reader import MissingRstReaderDependency, PyMapdlRstReader
from .validator import validate_case


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except MissingRstReaderDependency as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except MissingMechdbCacheDependency as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"ERROR: missing file: {exc.filename}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export exact Workbench-compatible FaceAccel CSV files.")
    parser.add_argument("--backup-root", type=Path, default=config.BACKUP_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser(
        "export",
        help="Export exact CSVs from cached Workbench probe histories in backed-up SYS.mechdb.",
    )
    export_parser.add_argument("cases", nargs="*", help="Case names such as Void.85.210.")
    export_parser.add_argument("--rst-root", type=Path, default=config.RST_ROOT)
    export_parser.add_argument("--output-root", type=Path, default=config.OUTPUT_ROOT)
    export_parser.set_defaults(func=export_command)

    validate_parser = subparsers.add_parser("validate", help="Validate generated CSVs against backed-up references.")
    validate_parser.add_argument("cases", nargs="*", help="Case names such as Void.85.210.")
    validate_parser.add_argument("--output-root", type=Path, default=config.OUTPUT_ROOT)
    validate_parser.set_defaults(func=validate_command)

    run_parser = subparsers.add_parser("run", help="Export exact cached probe CSVs then validate cases.")
    run_parser.add_argument("cases", nargs="*", help="Case names such as Void.85.210.")
    run_parser.add_argument("--rst-root", type=Path, default=config.RST_ROOT)
    run_parser.add_argument("--output-root", type=Path, default=config.OUTPUT_ROOT)
    run_parser.set_defaults(func=run_command)

    hpc_parser = subparsers.add_parser(
        "hpc-run",
        help="Run exact export on Linux/HPC directory layout and create a case zip package.",
    )
    hpc_parser.add_argument("case", help="Case name such as Void.112.510.")
    hpc_parser.add_argument("--base-dir", type=Path, default=config.HPC_BASE_DIR)
    hpc_parser.add_argument(
        "--design-point",
        default=config.HPC_DESIGN_POINT,
        help="Workbench design point directory, default: dp0.",
    )
    hpc_parser.add_argument(
        "--system",
        default=config.HPC_SYSTEM,
        help="Workbench system directory/name, default: SYS.",
    )
    hpc_parser.set_defaults(func=hpc_run_command)

    mechanical_hpc_parser = subparsers.add_parser(
        "mechanical-hpc-run",
        help="Run fresh-project exact export through Workbench/Mechanical batch, then create a case zip package.",
    )
    mechanical_hpc_parser.add_argument("case", help="Case name such as Void.112.510.")
    mechanical_hpc_parser.add_argument("--base-dir", type=Path, default=config.HPC_BASE_DIR)
    mechanical_hpc_parser.add_argument("--runwb2", type=Path, default=None, help="Path to Workbench runwb2.")
    mechanical_hpc_parser.add_argument(
        "--mechanical-timeout-seconds",
        type=int,
        default=config.HPC_MECHANICAL_STATUS_TIMEOUT_SECONDS,
        help="Maximum seconds to wait for Mechanical status after launching Workbench.",
    )
    mechanical_hpc_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only generate Workbench/Mechanical batch scripts; do not run Workbench.",
    )
    mechanical_hpc_parser.add_argument(
        "--design-point",
        default=config.HPC_DESIGN_POINT,
        help="Workbench design point directory, default: dp0.",
    )
    mechanical_hpc_parser.add_argument(
        "--system",
        default=config.HPC_SYSTEM,
        help="Workbench system directory/name, default: SYS.",
    )
    mechanical_hpc_parser.add_argument(
        "--component",
        default=config.HPC_WORKBENCH_COMPONENT,
        help="Workbench Mechanical container, default: Setup.",
    )
    mechanical_hpc_parser.set_defaults(func=mechanical_hpc_run_command)

    check_parser = subparsers.add_parser("check", help="Check optional runtime dependencies.")
    check_parser.set_defaults(func=check_command)

    return parser


def export_command(args) -> int:
    for case in _cases(args.backup_root, args.cases):
        written = _export_exact_case(
            case=case,
            rst_path=args.rst_root / f"{case}.rst",
            mechdb_path=_mechdb_path(args.backup_root, case),
            output_dir=args.output_root / case,
        )
        print(f"{case}: exported {len(written)} exact cached files to {args.output_root / case}")
    return 0


def hpc_run_command(args) -> int:
    paths = HpcCasePaths.from_base_and_case(
        args.base_dir,
        args.case,
        design_point=args.design_point,
        system=args.system,
    )
    paths.require_inputs()
    written = _export_exact_case(
        case=args.case,
        rst_path=paths.rst_path,
        mechdb_path=paths.mechdb_path,
        output_dir=paths.output_dir,
    )
    zip_path = paths.zip_output_dir()
    print(f"{args.case}: exported {len(written)} exact cached files to {paths.output_dir}")
    print(f"{args.case}: packaged {zip_path}")
    return 0


def mechanical_hpc_run_command(args) -> int:
    paths = HpcCasePaths.from_base_and_case(
        args.base_dir,
        args.case,
        design_point=args.design_point,
        system=args.system,
    )
    paths.require_inputs()
    batch_config = MechanicalBatchConfig(
        case=args.case,
        project_path=paths.project_path,
        rst_path=paths.rst_path,
        output_dir=paths.output_dir,
        status_path=paths.mechanical_status_path,
        mechanical_script_path=paths.mechanical_script_path,
        workbench_system=args.system,
        workbench_component=args.component,
    )
    write_mechanical_batch_files(batch_config, paths.workbench_journal_path)
    print(f"{args.case}: generated Workbench journal: {paths.workbench_journal_path}")
    print(f"{args.case}: generated Mechanical script: {paths.mechanical_script_path}")
    if args.dry_run:
        if args.runwb2:
            print(f"{args.case}: dry run command: {args.runwb2} -B -R {paths.workbench_journal_path}")
        else:
            print(f"{args.case}: dry run complete; set {config.HPC_RUNWB2_ENV_VAR} or pass --runwb2 before running.")
        return 0

    runwb2_path = find_runwb2(args.runwb2)
    _remove_stale_status(paths.mechanical_status_path)
    run_workbench_batch(runwb2_path, paths.workbench_journal_path, paths.batch_dir)
    _wait_for_mechanical_status(paths.mechanical_status_path, args.mechanical_timeout_seconds)
    _require_mechanical_status_ok(paths.mechanical_status_path)
    written = _export_exact_case(
        case=args.case,
        rst_path=paths.rst_path,
        mechdb_path=paths.mechdb_path,
        output_dir=paths.output_dir,
    )
    zip_path = paths.zip_output_dir()
    print(f"{args.case}: exported {len(written)} exact cached Mechanical files to {paths.output_dir}")
    print(f"{args.case}: packaged {zip_path}")
    return 0


def _export_exact_case(
    case: str,
    rst_path: Path,
    mechdb_path: Path,
    output_dir: Path,
) -> list[Path]:
    reader = PyMapdlRstReader(rst_path)
    histories = load_probe_histories_from_mechdb(
        mechdb_path,
        result_count=len(reader.result_sets),
    )
    return export_cached_probe_csvs(histories, reader.result_sets, output_dir)


def _require_mechanical_status_ok(status_path: Path) -> None:
    if not status_path.exists():
        raise RuntimeError(f"Mechanical batch did not write status file: {status_path}")
    text = status_path.read_text(encoding="utf-8", errors="replace")
    first_line = text.splitlines()[0] if text.splitlines() else ""
    if first_line.strip() != "OK":
        raise RuntimeError(f"Mechanical batch failed; see {status_path}: {text[:500]}")


def _remove_stale_status(status_path: Path) -> None:
    try:
        status_path.unlink()
    except FileNotFoundError:
        pass


def _wait_for_mechanical_status(status_path: Path, timeout_seconds: int) -> None:
    deadline = time.monotonic() + max(1, timeout_seconds)
    while time.monotonic() < deadline:
        if status_path.exists():
            return
        time.sleep(5)
    raise TimeoutError(f"Mechanical batch did not write status file within {timeout_seconds} seconds: {status_path}")


def validate_command(args) -> int:
    all_ok = True
    for case in _cases(args.backup_root, args.cases):
        reference_dir = args.backup_root / config.ORIGIN_DATA_DIR_NAME / case
        generated_dir = args.output_root / case
        results = validate_case(reference_dir, generated_dir)
        for result in results:
            status = "OK" if result.structure_matches else "STRUCTURE_MISMATCH"
            print(
                f"{case}/{result.file_name}: {status}, "
                f"probe_max_abs_error={result.probe_max_abs_error:.6g}, "
                f"probe_rmse={result.probe_rmse:.6g}, "
                f"all_max_abs_error={result.max_abs_error:.6g}, all_rmse={result.rmse:.6g}, "
                f"numeric_cells={result.numeric_cells}"
            )
            all_ok = all_ok and result.structure_matches
    return 0 if all_ok else 1


def run_command(args) -> int:
    export_status = export_command(args)
    if export_status != 0:
        return export_status
    return validate_command(args)


def check_command(_args) -> int:
    status = 0
    try:
        PyMapdlRstReader.__init__
        import importlib

        importlib.import_module("ansys.mapdl.reader")
    except Exception:
        print("ansys-mapdl-reader: missing")
        print("Install with: python -m pip install ansys-mapdl-reader")
        status = 2
    else:
        print("ansys-mapdl-reader: available")

    try:
        import importlib

        importlib.import_module("h5py")
    except Exception:
        print("h5py: missing")
        print("Install with: python -m pip install h5py")
        status = 2
    else:
        print("h5py: available")
    return status


def _cases(backup_root: Path, requested: list[str]) -> list[str]:
    if requested:
        return requested
    origin_root = backup_root / config.ORIGIN_DATA_DIR_NAME
    return sorted(path.name for path in origin_root.iterdir() if path.is_dir())


def _mechdb_path(backup_root: Path, case: str) -> Path:
    return backup_root / config.WORKBENCH_DIR_NAME / case / config.MECHDB_FILE_NAME


if __name__ == "__main__":
    raise SystemExit(main())
