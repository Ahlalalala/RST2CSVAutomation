import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

from rst2csv.mechanical_batch import (
    MechanicalBatchConfig,
    build_mechanical_export_script,
    build_workbench_journal,
    find_runwb2,
    run_workbench_batch,
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

    def test_run_workbench_batch_streams_logs_while_process_is_running(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            journal = tmp_path / "fake_workbench.py"
            journal.write_text(
                "import sys, time\n"
                "print('stdout before sleep', flush=True)\n"
                "print('stderr before sleep', file=sys.stderr, flush=True)\n"
                "time.sleep(3)\n",
                encoding="utf-8",
            )
            log_dir = tmp_path / "logs"
            result: dict[str, object] = {}

            def run_batch() -> None:
                result["completed"] = run_workbench_batch(sys.executable, journal, log_dir)

            thread = threading.Thread(target=run_batch)
            thread.start()
            try:
                stdout_log = log_dir / "workbench_stdout.log"
                stderr_log = log_dir / "workbench_stderr.log"
                deadline = time.monotonic() + 5
                while time.monotonic() < deadline:
                    stdout_text = stdout_log.read_text(encoding="utf-8") if stdout_log.exists() else ""
                    stderr_text = stderr_log.read_text(encoding="utf-8") if stderr_log.exists() else ""
                    if "stdout before sleep" in stdout_text and "stderr before sleep" in stderr_text:
                        break
                    time.sleep(0.05)

                self.assertIn("stdout before sleep", stdout_log.read_text(encoding="utf-8"))
                self.assertIn("stderr before sleep", stderr_log.read_text(encoding="utf-8"))
                self.assertTrue(thread.is_alive())
            finally:
                thread.join(timeout=5)
            self.assertIn("completed", result)


if __name__ == "__main__":
    unittest.main()
