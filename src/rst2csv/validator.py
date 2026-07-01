"""Validation helpers for generated FaceAccel CSV files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import math
from pathlib import Path


@dataclass(frozen=True)
class CsvComparison:
    file_name: str
    structure_matches: bool
    row_count_reference: int
    row_count_generated: int
    column_count_reference: int
    column_count_generated: int
    numeric_cells: int
    max_abs_error: float
    rmse: float
    probe_numeric_cells: int
    probe_max_abs_error: float
    probe_rmse: float
    message: str


def compare_csv_files(reference_path: str | Path, generated_path: str | Path) -> CsvComparison:
    reference_path = Path(reference_path)
    generated_path = Path(generated_path)
    reference_rows = _read_csv(reference_path)
    generated_rows = _read_csv(generated_path)

    ref_cols = len(reference_rows[0]) if reference_rows else 0
    gen_cols = len(generated_rows[0]) if generated_rows else 0
    structure_matches = (
        len(reference_rows) == len(generated_rows)
        and ref_cols == gen_cols
        and bool(reference_rows)
        and reference_rows[0] == generated_rows[0]
    )

    errors: list[float] = []
    probe_errors: list[float] = []
    for ref_row, gen_row in zip(reference_rows[1:], generated_rows[1:]):
        for column_index, (ref_cell, gen_cell) in enumerate(zip(ref_row, gen_row)):
            try:
                ref_value = float(ref_cell)
                gen_value = float(gen_cell)
            except ValueError:
                continue
            if not (math.isfinite(ref_value) and math.isfinite(gen_value)):
                continue
            error = gen_value - ref_value
            errors.append(error)
            if column_index >= 3:
                probe_errors.append(error)

    max_abs_error = max((abs(value) for value in errors), default=math.nan)
    rmse = math.sqrt(sum(value * value for value in errors) / len(errors)) if errors else math.nan
    probe_max_abs_error = max((abs(value) for value in probe_errors), default=math.nan)
    probe_rmse = (
        math.sqrt(sum(value * value for value in probe_errors) / len(probe_errors))
        if probe_errors
        else math.nan
    )
    message = "ok" if structure_matches else "row count, column count, or header mismatch"

    return CsvComparison(
        file_name=generated_path.name,
        structure_matches=structure_matches,
        row_count_reference=len(reference_rows),
        row_count_generated=len(generated_rows),
        column_count_reference=ref_cols,
        column_count_generated=gen_cols,
        numeric_cells=len(errors),
        max_abs_error=max_abs_error,
        rmse=rmse,
        probe_numeric_cells=len(probe_errors),
        probe_max_abs_error=probe_max_abs_error,
        probe_rmse=probe_rmse,
        message=message,
    )


def validate_case(
    reference_dir: str | Path,
    generated_dir: str | Path,
    faces: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "G"),
) -> list[CsvComparison]:
    reference_dir = Path(reference_dir)
    generated_dir = Path(generated_dir)
    return [
        compare_csv_files(reference_dir / f"FaceAccel_{face}.CSV", generated_dir / f"FaceAccel_{face}.CSV")
        for face in faces
    ]


def _read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="gb2312", newline="") as stream:
        return list(csv.reader(stream))
