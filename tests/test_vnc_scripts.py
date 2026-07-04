import unittest
from pathlib import Path


class VncScriptTests(unittest.TestCase):
    def test_in_vnc_script_runs_mechanical_export_without_nested_sbatch(self):
        script = Path("scripts/rst2csv_in_current_vnc.sh")

        text = script.read_text(encoding="utf-8")

        self.assertIn('-m rst2csv.cli mechanical-hpc-run', text)
        self.assertIn('DISPLAY', text)
        self.assertNotIn('sbatch', text)


if __name__ == "__main__":
    unittest.main()
