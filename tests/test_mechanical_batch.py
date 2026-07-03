import os
import tempfile
import unittest
from pathlib import Path

from rst2csv.mechanical_batch import (
    MechanicalBatchConfig,
    build_mechanical_export_script,
    build_workbench_journal,
    find_runwb2,
)


class MechanicalBatchTests(unittest.TestCase):
    def _batch_config(self) -> MechanicalBatchConfig:
        return MechanicalBatchConfig(
            case="Void.112.510",
            project_path=Path("/base/RST2CSVFiles/Void.112.510.wbpj"),
            rst_path=Path("/base/TaskDir_Void.112.510/Void.112.510.rst"),
            output_dir=Path("/base/CSVResult/Void.112.510"),
            status_path=Path("/base/CSVResult/Void.112.510/_mechanical_batch/mechanical_status.txt"),
            mechanical_script_path=Path("/base/CSVResult/Void.112.510/_mechanical_batch/export_probes.py"),
            workbench_system="SYS",
            workbench_component="Model",
        )

    def test_build_workbench_journal_targets_project_and_mechanical_script(self):
        config = self._batch_config()

        journal = build_workbench_journal(config)

        self.assertIn("/base/RST2CSVFiles/Void.112.510.wbpj", journal)
        self.assertIn("/base/CSVResult/Void.112.510/_mechanical_batch/export_probes.py", journal)
        self.assertIn("GetSystem(Name=SYSTEM_NAME)", journal)
        self.assertIn("SendCommand(Language=\"Python\"", journal)

    def test_mechanical_script_populates_mechdb_cache_instead_of_text_export(self):
        script = build_mechanical_export_script(self._batch_config())

        self.assertIn("solution.EvaluateAllResults()", script)
        self.assertIn("probe.RetrieveResult()", script)
        self.assertIn("empty_probes = _empty_probes(probes)", script)
        self.assertIn("for probe in empty_probes:", script)
        self.assertNotIn("for probe in probes:\n        try:\n            probe.EvaluateAllResults()", script)
        self.assertIn("Cached histories", script)
        self.assertNotIn("ExportToTextFile", script)
        self.assertNotIn("SequenceTotalVector", script)

    def test_mechanical_script_fails_if_result_link_is_not_created(self):
        script = build_mechanical_export_script(self._batch_config())

        self.assertIn('path.replace("/", "\\\\")', script)
        self.assertIn('["cmd", "/c", "mklink"', script)
        self.assertIn('["ln", "-s"', script)
        self.assertIn("Result link was not created", script)

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


if __name__ == "__main__":
    unittest.main()
