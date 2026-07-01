"""Adapters for reading nodal acceleration from ANSYS RST files."""

from __future__ import annotations

import importlib
from pathlib import Path


class MissingRstReaderDependency(RuntimeError):
    """Raised when no supported RST reader dependency is installed."""


class PyMapdlRstReader:
    """Read nodal acceleration using `ansys-mapdl-reader`."""

    def __init__(self, rst_path: str | Path, step_split_time: float = 2.0):
        self.rst_path = Path(rst_path)
        try:
            mapdl_reader = importlib.import_module("ansys.mapdl.reader")
        except Exception as exc:  # pragma: no cover - exact import error varies by install
            raise MissingRstReaderDependency(
                "Missing RST reader dependency. Install ansys-mapdl-reader, for example: "
                "python -m pip install ansys-mapdl-reader"
            ) from exc

        self._result = mapdl_reader.read_binary(str(self.rst_path))
        self.result_sets = build_result_sets(self._result.time_values, step_split_time=step_split_time)

    def acceleration_for_nodes(
        self,
        result_index: int,
        node_ids: tuple[int, ...],
    ) -> dict[int, tuple[float, float, float]]:
        node_numbers, accelerations = self._result.nodal_acceleration(result_index)
        wanted = set(node_ids)
        values: dict[int, tuple[float, float, float]] = {}
        for node_number, vector in zip(node_numbers, accelerations):
            node = int(node_number)
            if node in wanted:
                values[node] = (float(vector[0]), float(vector[1]), float(vector[2]))
        return values


def build_result_sets(time_values, step_split_time: float = 2.0) -> list[tuple[int, float]]:
    result_sets: list[tuple[int, float]] = []
    previous_time: float | None = None
    step = 1
    for raw_time in time_values:
        time_value = float(raw_time)
        if previous_time is not None and time_value < previous_time:
            step += 1
        elif previous_time is not None and previous_time <= step_split_time < time_value:
            step = 2
        result_sets.append((step, time_value))
        previous_time = time_value
    return result_sets
