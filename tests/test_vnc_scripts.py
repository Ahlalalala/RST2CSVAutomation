import unittest
import re
from pathlib import Path


class VncScriptTests(unittest.TestCase):
    def test_in_vnc_script_runs_mechanical_export_without_nested_sbatch(self):
        script = Path("scripts/rst2csv_in_current_vnc.sh")

        text = script.read_text(encoding="utf-8")

        self.assertIn('-m rst2csv.cli mechanical-hpc-run', text)
        self.assertIn('DISPLAY', text)
        self.assertNotIn('sbatch', text)

    def test_in_vnc_script_does_not_pass_cases_to_environment_scripts(self):
        script = Path("scripts/rst2csv_in_current_vnc.sh")

        text = script.read_text(encoding="utf-8")

        self.assertIn('CASE_NAMES=("$@")', text)
        self.assertIn("set --", text)
        self.assertIn('for CASE_NAME in "${CASE_NAMES[@]}"; do', text)
        self.assertIsNotNone(
            re.search(r'CASE_NAMES=\("\$@"\).*?\nset --.*?source "\$\{INTEL_SETVARS\}"', text, re.S)
        )

    def test_in_vnc_script_allows_unset_variables_inside_vendor_env_scripts(self):
        script = Path("scripts/rst2csv_in_current_vnc.sh")

        text = script.read_text(encoding="utf-8")

        env_block_match = re.search(r"set \+u(.*?)set -u", text, re.S)
        self.assertIsNotNone(env_block_match)
        env_block = env_block_match.group(1)
        self.assertIn('source "${CONDA_SH}"', env_block)
        self.assertIn('source "${INTEL_SETVARS}"', env_block)
        self.assertIn('source "${ANSYS_SETENV}"', env_block)


if __name__ == "__main__":
    unittest.main()
