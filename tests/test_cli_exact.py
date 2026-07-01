import unittest
from pathlib import Path

from rst2csv import config
from rst2csv.cli import build_parser


class ExactCliTests(unittest.TestCase):
    def test_default_paths_are_centralized_in_config(self):
        self.assertEqual(config.BACKUP_ROOT, Path("Backup"))
        self.assertEqual(config.RST_ROOT, Path("E:/WCL/AnsysTunnel/RSTVoidBatch"))
        self.assertEqual(config.OUTPUT_ROOT, Path("GeneratedExact"))
        self.assertEqual(config.MECHDB_FILE_NAME, "SYS.mechdb")

    def test_cli_only_exposes_exact_workflow_commands(self):
        parser = build_parser()
        subparsers_action = next(action for action in parser._actions if action.dest == "command")

        self.assertEqual(set(subparsers_action.choices), {"check", "export", "validate", "run"})

    def test_export_defaults_to_exact_output_root(self):
        parser = build_parser()
        args = parser.parse_args(["export", "Void.85.210"])

        self.assertEqual(args.output_root, config.OUTPUT_ROOT)


if __name__ == "__main__":
    unittest.main()
