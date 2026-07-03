import tempfile
import unittest
import zipfile
from pathlib import Path

from rst2csv.hpc_paths import HpcCasePaths


class HpcPathsTests(unittest.TestCase):
    def test_hpc_case_paths_follow_remote_directory_contract(self):
        paths = HpcCasePaths.from_base_and_case(Path("/base"), "Void.112.510")

        self.assertEqual(paths.dat_path, Path("/base/Void.112.510.dat"))
        self.assertEqual(paths.rst_path, Path("/base/TaskDir_Void.112.510/Void.112.510.rst"))
        self.assertEqual(
            paths.mechdb_path,
            Path("/base/RST2CSVFiles/Void.112.510_files/dp0/global/MECH/SYS.mechdb"),
        )
        self.assertEqual(paths.dsdat_path, Path("/base/RST2CSVFiles/Void.112.510_files/dp0/SYS/MECH/ds.dat"))
        self.assertEqual(paths.caerep_path, Path("/base/RST2CSVFiles/Void.112.510_files/dp0/SYS/MECH/CAERep.xml"))
        self.assertEqual(paths.output_dir, Path("/base/CSVResult/Void.112.510"))
        self.assertEqual(paths.zip_path, Path("/base/CSVResult/Void.112.510.zip"))

    def test_missing_inputs_lists_required_hpc_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = HpcCasePaths.from_base_and_case(Path(tmp), "Void.112.510")
            paths.rst_path.parent.mkdir(parents=True)
            paths.rst_path.write_bytes(b"placeholder")

            missing = paths.missing_inputs()

        self.assertEqual(
            missing,
            [
                paths.dat_path,
                paths.mechdb_path,
                paths.dsdat_path,
                paths.caerep_path,
            ],
        )

    def test_require_inputs_raises_file_not_found_with_missing_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = HpcCasePaths.from_base_and_case(Path(tmp), "Void.112.510")

            with self.assertRaises(FileNotFoundError) as context:
                paths.require_inputs()

        self.assertEqual(Path(context.exception.filename), paths.dat_path)

    def test_zip_output_dir_packages_face_csvs_under_case_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = HpcCasePaths.from_base_and_case(Path(tmp), "Void.112.510")
            paths.output_dir.mkdir(parents=True)
            (paths.output_dir / "FaceAccel_A.CSV").write_text("a", encoding="gb2312")
            (paths.output_dir / "FaceAccel_G.CSV").write_text("g", encoding="gb2312")
            (paths.output_dir / "notes.txt").write_text("skip", encoding="utf-8")

            zip_path = paths.zip_output_dir()

            with zipfile.ZipFile(zip_path) as archive:
                names = sorted(archive.namelist())

        self.assertEqual(zip_path, paths.zip_path)
        self.assertEqual(
            names,
            [
                "Void.112.510/FaceAccel_A.CSV",
                "Void.112.510/FaceAccel_G.CSV",
            ],
        )


if __name__ == "__main__":
    unittest.main()
