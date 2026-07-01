import csv
import tempfile
import unittest
from pathlib import Path

from rst2csv.validator import compare_csv_files, validate_case


def write_csv(path, rows):
    with Path(path).open("w", encoding="gb2312", newline="") as stream:
        csv.writer(stream).writerows(rows)


class ValidatorTests(unittest.TestCase):
    def test_compare_csv_files_reports_numeric_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref = Path(tmp) / "ref.csv"
            gen = Path(tmp) / "gen.csv"
            rows = [
                ["", "步骤", "时间 [s]", "[A] Face_Accel_Probe_1  (总体) [m/s?]"],
                ["1", "1", "0.1", "1.0"],
                ["2", "2", "2.0", "3.0"],
            ]
            write_csv(ref, rows)
            write_csv(
                gen,
                [
                    rows[0],
                    ["1", "1", "0.1", "1.5"],
                    ["2", "2", "2.0", "2.5"],
                ],
            )

            result = compare_csv_files(ref, gen)

        self.assertTrue(result.structure_matches)
        self.assertEqual(result.numeric_cells, 8)
        self.assertAlmostEqual(result.max_abs_error, 0.5)
        self.assertAlmostEqual(result.rmse, 0.25)
        self.assertEqual(result.probe_numeric_cells, 2)
        self.assertAlmostEqual(result.probe_max_abs_error, 0.5)
        self.assertAlmostEqual(result.probe_rmse, 0.5)

    def test_validate_case_compares_face_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            ref_dir = Path(tmp) / "ref"
            gen_dir = Path(tmp) / "gen"
            ref_dir.mkdir()
            gen_dir.mkdir()
            rows = [["", "步骤", "时间 [s]", "probe"], ["1", "1", "0.1", "0"]]
            write_csv(ref_dir / "FaceAccel_A.CSV", rows)
            write_csv(gen_dir / "FaceAccel_A.CSV", rows)

            results = validate_case(ref_dir, gen_dir, faces=("A",))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].file_name, "FaceAccel_A.CSV")
        self.assertTrue(results[0].structure_matches)
        self.assertEqual(results[0].max_abs_error, 0.0)


if __name__ == "__main__":
    unittest.main()
