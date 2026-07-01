"""Workbench-compatible FaceAccel CSV formatting helpers."""

from __future__ import annotations

FACE_ORDER = ("A", "B", "C", "D", "E", "F", "G")


def excel_column_name(index: int) -> str:
    """Return the Workbench-style probe column label for a 1-based index."""
    if index < 1:
        raise ValueError("column index must be 1 or greater")

    prefix_count, remainder = divmod(index - 1, 26)
    return ("A" * prefix_count) + chr(ord("A") + remainder)


def probe_numbers_for_face(face: str) -> list[int]:
    """Return the 100 output probe numbers for one tunnel face row."""
    face = face.upper()
    if face not in FACE_ORDER:
        raise ValueError(f"unknown face {face!r}; expected one of {FACE_ORDER}")

    face_index = FACE_ORDER.index(face)
    left_start = face_index * 200 + 1
    right_start = face_index * 200 + 101
    return list(range(left_start, left_start + 50)) + list(range(right_start, right_start + 50))


def csv_header_for_face(face: str) -> list[str]:
    """Build the exact header used by the manual Workbench CSV export."""
    headers = ["", "步骤", "时间 [s]"]
    for column_index, probe_number in enumerate(probe_numbers_for_face(face), start=1):
        excel_column = excel_column_name(column_index)
        headers.append(f"[{excel_column}] Face_Accel_Probe_{probe_number}  (总体) [m/s?]")
    return headers


def format_probe_value(value: float) -> str:
    """Format probe values close to Mechanical's CSV table display."""
    if value == 0:
        return "0"
    if abs(value) < 0.1:
        if abs(value) >= 0.01:
            value += 5e-7 if value > 0 else -5e-7
        return f"{value:.2E}"
    return f"{value:.5g}"


def format_time_value(value: float) -> str:
    """Format step time without losing precision."""
    return f"{value:.15g}"
