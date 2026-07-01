import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from rst2csv.rst_reader import MissingRstReaderDependency, PyMapdlRstReader, build_result_sets


class RstReaderTests(unittest.TestCase):
    def test_missing_dependency_has_actionable_message(self):
        with patch.dict(sys.modules, {"ansys.mapdl.reader": None}):
            with self.assertRaises(MissingRstReaderDependency) as ctx:
                PyMapdlRstReader(Path("missing.rst"))

        self.assertIn("ansys-mapdl-reader", str(ctx.exception))

    def test_reader_wraps_pyansys_acceleration_api(self):
        fake_result = types.SimpleNamespace(
            time_values=[0.1, 2.0],
            nodal_acceleration=lambda rnum: (
                [101, 102],
                [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
            ),
        )
        fake_module = types.SimpleNamespace(read_binary=lambda path: fake_result)

        with patch.dict(sys.modules, {"ansys.mapdl.reader": fake_module}):
            reader = PyMapdlRstReader(Path("case.rst"))

        self.assertEqual(reader.result_sets, [(1, 0.1), (1, 2.0)])
        self.assertEqual(reader.acceleration_for_nodes(0, (102,)), {102: (4.0, 5.0, 6.0)})

    def test_build_result_sets_uses_step_split_time(self):
        self.assertEqual(
            build_result_sets([0.1, 2.0, 2.0001, 2.05], step_split_time=2.0),
            [(1, 0.1), (1, 2.0), (2, 2.0001), (2, 2.05)],
        )


if __name__ == "__main__":
    unittest.main()
