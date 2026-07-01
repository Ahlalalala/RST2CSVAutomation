"""Read cached Workbench Result Probe histories from Mechanical `.mechdb` files."""

from __future__ import annotations

import csv
import math
from pathlib import Path
import re
import struct
import zlib

from .csv_format import csv_header_for_face, format_probe_value, format_time_value, probe_numbers_for_face


SIMULATION_OBJECT_DATASET = "Simulation Object Storage/Simulation Object (-)"
PROBE_VALUE_OFFSET_BASE = 8158
PROBE_NAME_RE = re.compile(rb"(?:[ -~]\x00){2,}")


class MissingMechdbCacheDependency(RuntimeError):
    """Raised when HDF5 support is not available."""


def load_probe_histories_from_mechdb(
    mechdb_path: str | Path,
    result_count: int,
) -> dict[int, tuple[float, ...]]:
    """Load cached probe time histories from a backed-up Mechanical `.mechdb` file."""
    try:
        import h5py
    except Exception as exc:  # pragma: no cover - exact import error varies by install
        raise MissingMechdbCacheDependency(
            "Missing HDF5 dependency. Install h5py, for example: python -m pip install h5py"
        ) from exc

    path = Path(mechdb_path)
    with h5py.File(path, "r") as h5file:
        dataset = h5file[SIMULATION_OBJECT_DATASET]
        raw = bytes(dataset[:])
        used_size = _attribute_int(dataset.attrs.get("UsedSize"), len(raw))
        simulation_stream = decompress_chunked_zlib_stream(raw[:used_size])

    return extract_probe_histories_from_simulation_stream(simulation_stream, result_count)


def decompress_chunked_zlib_stream(stream: bytes) -> bytes:
    """Decompress Workbench streams stored as repeated `<uint32 length><zlib bytes>` chunks."""
    position = 0
    chunks: list[bytes] = []
    while position + 4 <= len(stream):
        compressed_size = struct.unpack_from("<I", stream, position)[0]
        if compressed_size <= 0 or position + 4 + compressed_size > len(stream):
            break
        start = position + 4
        chunks.append(zlib.decompress(stream[start : start + compressed_size]))
        position = start + compressed_size
    return b"".join(chunks)


def extract_probe_histories_from_simulation_stream(
    simulation_stream: bytes,
    result_count: int,
) -> dict[int, tuple[float, ...]]:
    """Extract `Face_Accel_Probe_N` cached double arrays from a decompressed stream."""
    histories: dict[int, tuple[float, ...]] = {}
    byte_count = result_count * 8
    for match in PROBE_NAME_RE.finditer(simulation_stream):
        try:
            name = match.group().decode("utf-16le")
        except UnicodeDecodeError:
            continue
        if not name.startswith("Face_Accel_Probe_"):
            continue
        probe_number = int(name.rsplit("_", 1)[1])
        offset = match.start() + _probe_value_offset(probe_number)
        if offset + byte_count > len(simulation_stream):
            continue
        values = struct.unpack_from(f"<{result_count}d", simulation_stream, offset)
        if all(math.isfinite(value) for value in values):
            histories[probe_number] = tuple(float(value) for value in values)
    return histories


def export_cached_probe_csvs(
    histories: dict[int, tuple[float, ...]],
    result_sets: list[tuple[int, float]],
    output_dir: str | Path,
    faces: tuple[str, ...] = ("A", "B", "C", "D", "E", "F", "G"),
) -> list[Path]:
    """Write Workbench-shaped FaceAccel CSVs from cached probe histories."""
    result_count = len(result_sets)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for face in faces:
        probes = probe_numbers_for_face(face)
        missing = [probe for probe in probes if probe not in histories]
        if missing:
            raise ValueError(f"cached histories missing probes for Face {face}: {missing[:5]}")
        for probe in probes:
            if len(histories[probe]) != result_count:
                raise ValueError(
                    f"probe {probe} has {len(histories[probe])} cached values, "
                    f"expected {result_count}"
                )

        path = output_path / f"FaceAccel_{face}.CSV"
        with path.open("w", encoding="gb2312", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(csv_header_for_face(face))
            for row_index, (step, time_value) in enumerate(result_sets, start=1):
                writer.writerow(
                    [str(row_index), str(step), format_time_value(time_value)]
                    + [format_probe_value(histories[probe][row_index - 1]) for probe in probes]
                )
        written.append(path)
    return written


def _probe_value_offset(probe_number: int) -> int:
    return PROBE_VALUE_OFFSET_BASE + 2 * (len(str(probe_number)) - 1)


def _attribute_int(value, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except Exception:
        try:
            return int(value[0])
        except Exception:
            return default
