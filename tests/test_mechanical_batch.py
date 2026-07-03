import csv
import os
import tempfile
import unittest
from pathlib import Path

from rst2csv.mechanical_batch import (
    MechanicalBatchConfig,
    build_workbench_journal,
    combine_probe_text_exports,
    find_runwb2,
    parse_probe_export_text,
)


class MechanicalBatchTests(unittest.TestCase):
    def test_build_workbench_journal_targets_project_and_mechanical_script(self):
        config = MechanicalBatchConfig(
            case="Void.112.510",
            project_path=Path("/base/RST2CSVFiles/Void.112.510.wbpj"),
            rst_path=Path("/base/TaskDir_Void.112.510/Void.112.510.rst"),
            output_dir=Path("/base/CSVResult/Void.112.510"),
            probe_text_dir=Path("/base/CSVResult/Void.112.510/_mechanical_batch/probe_txt"),
            status_path=Path("/base/CSVResult/Void.112.510/_mechanical_batch/mechanical_status.txt"),
            mechanical_script_path=Path("/base/CSVResult/Void.112.510/_mechanical_batch/export_probes.py"),
            workbench_system="SYS",
            workbench_component="Model",
        )

        journal = build_workbench_journal(config)

        self.assertIn("/base/RST2CSVFiles/Void.112.510.wbpj", journal)
        self.assertIn("/base/CSVResult/Void.112.510/_mechanical_batch/export_probes.py", journal)
        self.assertIn("GetSystem(Name=SYSTEM_NAME)", journal)
        self.assertIn("SendCommand(Language=\"Python\"", journal)

    def test_find_runwb2_prefers_explicit_path_then_environment(self):
        with tempfile.TemporaryDirectory() as tmp:
            explicit = Path(tmp) / "runwb2"
            explicit.write_text("#!/bin/sh\n", encoding="utf-8")

            self.assertEqual(find_runwb2(explicit, env={}), explicit)

            env_path = Path(tmp) / "env_runwb2"
            env_path.write_text("#!/bin/sh\n", encoding="utf-8")
            self.assertEqual(
                find_runwb2(None, env={"RST2CSV_RUNWB2": str(env_path), "PATH": ""}),
                env_path,
            )

    def test_parse_probe_export_text_matches_known_times(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Face_Accel_Probe_1.txt"
            path.write_text(
                "Time [s]\tTotal [m/s^2]\n"
                "0.1\t0\n"
                "2.0001\t2.8738467188650472e-05\n"
                "2.0004490970593576\t4.435465051531779e-05\n",
                encoding="utf-8",
            )

            history = parse_probe_export_text(
                path,
                result_sets=[
                    (1, 0.1),
                    (2, 2.0001),
                    (2, 2.0004490970593576),
                ],
            )

        self.assertEqual(history, (0.0, 2.8738467188650472e-05, 4.435465051531779e-05))

    def test_parse_probe_export_text_falls_back_to_last_numeric_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Face_Accel_Probe_1.txt"
            path.write_text(
                "row time total\n"
                "1 0.1 0\n"
                "2 2.0001 1.25E-04\n",
                encoding="utf-8",
            )

            history = parse_probe_export_text(path, result_sets=[(1, 0.1), (2, 2.0001)])

        self.assertEqual(history, (0.0, 1.25e-04))

    def test_combine_probe_text_exports_writes_face_csv(self):
        result_sets = [(1, 0.1), (2, 2.0001)]
        with tempfile.TemporaryDirectory() as tmp:
            probe_dir = Path(tmp) / "probe_txt"
            probe_dir.mkdir()
            for probe in list(range(1, 51)) + list(range(101, 151)):
                (probe_dir / f"Face_Accel_Probe_{probe}.txt").write_text(
                    "time,total\n0.1,0\n2.0001,{}\n".format(probe / 1000),
                    encoding="utf-8",
                )

            output_dir = Path(tmp) / "csv"
            written = combine_probe_text_exports(probe_dir, result_sets, output_dir, faces=("A",))

            with written[0].open("r", encoding="gb2312", newline="") as stream:
                rows = list(csv.reader(stream))

        self.assertEqual(written[0].name, "FaceAccel_A.CSV")
        self.assertEqual(rows[1][3], "0")
        self.assertEqual(rows[2][3], "1.00E-03")


if __name__ == "__main__":
    unittest.main()
