import tempfile
import unittest
import zipfile
from pathlib import Path

from rst2csv.local_paths import LocalCasePaths


class LocalPathsTests(unittest.TestCase):
    def test_local_case_paths_follow_windows_directory_contract(self):
        paths = LocalCasePaths.from_roots(
            workbench_root=Path("E:/WCL/AnsysTunnel"),
            rst_root=Path("E:/WCL/AnsysTunnel/RSTVoidBatch"),
            output_root=Path("E:/WCL/AnsysTunnel/AutoCSVResult"),
            case="Void.112.510",
        )

        self.assertEqual(paths.project_path, Path("E:/WCL/AnsysTunnel/Void.112.510.wbpj"))
        self.assertEqual(paths.files_root, Path("E:/WCL/AnsysTunnel/Void.112.510_files"))
        self.assertEqual(paths.rst_path, Path("E:/WCL/AnsysTunnel/RSTVoidBatch/Void.112.510.rst"))
        self.assertEqual(
            paths.mechdb_path,
            Path("E:/WCL/AnsysTunnel/Void.112.510_files/dp0/global/MECH/SYS.mechdb"),
        )
        self.assertEqual(paths.dsdat_path, Path("E:/WCL/AnsysTunnel/Void.112.510_files/dp0/SYS/MECH/ds.dat"))
        self.assertEqual(paths.caerep_path, Path("E:/WCL/AnsysTunnel/Void.112.510_files/dp0/SYS/MECH/CAERep.xml"))
        self.assertEqual(paths.output_dir, Path("E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510"))
        self.assertEqual(paths.zip_path, Path("E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510.zip"))

    def test_missing_inputs_lists_required_local_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = LocalCasePaths.from_roots(root, root / "RSTVoidBatch", root / "AutoCSVResult", "Void.112.510")
            paths.rst_path.parent.mkdir(parents=True)
            paths.rst_path.write_bytes(b"rst")

            missing = paths.missing_inputs()

        self.assertEqual(
            missing,
            [
                paths.project_path,
                paths.mechdb_path,
                paths.dsdat_path,
                paths.caerep_path,
            ],
        )

    def test_zip_output_dir_packages_face_csvs_under_case_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = LocalCasePaths.from_roots(root, root / "RSTVoidBatch", root / "AutoCSVResult", "Void.112.510")
            paths.output_dir.mkdir(parents=True)
            (paths.output_dir / "FaceAccel_A.CSV").write_text("a", encoding="gb2312")
            (paths.output_dir / "FaceAccel_G.CSV").write_text("g", encoding="gb2312")
            (paths.output_dir / "notes.txt").write_text("skip", encoding="utf-8")

            zip_path = paths.zip_output_dir()

            with zipfile.ZipFile(zip_path) as archive:
                names = sorted(archive.namelist())

        self.assertEqual(zip_path, paths.zip_path)
        self.assertEqual(names, ["Void.112.510/FaceAccel_A.CSV", "Void.112.510/FaceAccel_G.CSV"])


if __name__ == "__main__":
    unittest.main()
