# Local Workbench RST2CSV Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Windows local Workbench workflow that exports exact `FaceAccel_A.CSV` to `FaceAccel_G.CSV` from `E:/WCL/AnsysTunnel` projects and `RSTVoidBatch` RST files into `E:/WCL/AnsysTunnel/AutoCSVResult`.

**Architecture:** Reuse the existing fresh Workbench batch engine and exact `SYS.mechdb` cache reader. Add a small local path resolver, central default paths, a `local-run` CLI entry, and a Chinese user manual. Keep HPC/VNC code intact.

**Tech Stack:** Python standard library, existing `rst2csv` modules, Workbench 2025 R2 `RunWB2.exe`, `unittest`, PowerShell verification commands.

---

### Task 1: Add Local Path Resolver

**Files:**
- Create: `src/rst2csv/local_paths.py`
- Modify: `src/rst2csv/config.py`
- Test: `tests/test_local_paths.py`

- [ ] **Step 1: Write failing path tests**

Add `tests/test_local_paths.py`:

```python
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
        self.assertEqual(paths.mechdb_path, Path("E:/WCL/AnsysTunnel/Void.112.510_files/dp0/global/MECH/SYS.mechdb"))
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
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_local_paths -v
```

Expected: FAIL or ERROR because `rst2csv.local_paths` does not exist.

- [ ] **Step 3: Add config defaults**

Modify `src/rst2csv/config.py` near the existing editable path block:

```python
LOCAL_WORKBENCH_ROOT = Path("E:/WCL/AnsysTunnel")
LOCAL_RST_ROOT = Path("E:/WCL/AnsysTunnel/RSTVoidBatch")
LOCAL_OUTPUT_ROOT = Path("E:/WCL/AnsysTunnel/AutoCSVResult")
LOCAL_RUNWB2_PATH = Path("D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe")
```

- [ ] **Step 4: Implement `LocalCasePaths`**

Create `src/rst2csv/local_paths.py` with a dataclass mirroring the needed fields from `HpcCasePaths`, but using local root paths and no `TaskDir_` convention.

- [ ] **Step 5: Run test to verify it passes**

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_local_paths -v
```

Expected: 3 tests OK.

### Task 2: Add Shared Fresh Workbench Runner And `local-run`

**Files:**
- Modify: `src/rst2csv/cli.py`
- Modify: `tests/test_cli_exact.py`

- [ ] **Step 1: Write failing CLI tests**

Add assertions to `tests/test_cli_exact.py`:

```python
    def test_local_run_defaults_to_windows_roots(self):
        parser = build_parser()

        args = parser.parse_args(["local-run", "Void.112.510"])

        self.assertEqual(args.workbench_root, config.LOCAL_WORKBENCH_ROOT)
        self.assertEqual(args.rst_root, config.LOCAL_RST_ROOT)
        self.assertEqual(args.output_root, config.LOCAL_OUTPUT_ROOT)
        self.assertEqual(args.runwb2, config.LOCAL_RUNWB2_PATH)

    def test_local_run_accepts_multiple_cases_and_overrides(self):
        parser = build_parser()

        args = parser.parse_args([
            "local-run",
            "Void.40.245",
            "Void.67.675",
            "--workbench-root",
            "D:/wb",
            "--rst-root",
            "D:/rst",
            "--output-root",
            "D:/out",
            "--runwb2",
            "D:/ansys/RunWB2.exe",
        ])

        self.assertEqual(args.cases, ["Void.40.245", "Void.67.675"])
        self.assertEqual(args.workbench_root, Path("D:/wb"))
        self.assertEqual(args.rst_root, Path("D:/rst"))
        self.assertEqual(args.output_root, Path("D:/out"))
        self.assertEqual(args.runwb2, Path("D:/ansys/RunWB2.exe"))
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_cli_exact -v
```

Expected: FAIL because `local-run` is not registered.

- [ ] **Step 3: Refactor shared fresh runner**

In `src/rst2csv/cli.py`, extract the body after path creation from `mechanical_hpc_run_command` into `_run_fresh_workbench_case(...)`, accepting path object, case name, runwb2 path, timeout, component, system, and dry-run flag.

- [ ] **Step 4: Register `local-run`**

In `build_parser()`, add:

```python
local_parser = subparsers.add_parser(
    "local-run",
    help="Run exact local Windows Workbench/RST export and create a case zip package.",
)
local_parser.add_argument("cases", nargs="+", help="Case names such as Void.112.510.")
local_parser.add_argument("--workbench-root", type=Path, default=config.LOCAL_WORKBENCH_ROOT)
local_parser.add_argument("--rst-root", type=Path, default=config.LOCAL_RST_ROOT)
local_parser.add_argument("--output-root", type=Path, default=config.LOCAL_OUTPUT_ROOT)
local_parser.add_argument("--runwb2", type=Path, default=config.LOCAL_RUNWB2_PATH)
local_parser.add_argument("--mechanical-timeout-seconds", type=int, default=config.HPC_MECHANICAL_STATUS_TIMEOUT_SECONDS)
local_parser.add_argument("--dry-run", action="store_true")
local_parser.add_argument("--design-point", default=config.HPC_DESIGN_POINT)
local_parser.add_argument("--system", default=config.HPC_SYSTEM)
local_parser.add_argument("--component", default=config.HPC_WORKBENCH_COMPONENT)
local_parser.set_defaults(func=local_run_command)
```

- [ ] **Step 5: Implement `local_run_command`**

For each case, build `LocalCasePaths.from_roots(...)`, require inputs, and call the shared fresh runner. Print the output directory and zip path per case.

- [ ] **Step 6: Run CLI tests**

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_cli_exact -v
```

Expected: OK.

### Task 3: Add Chinese Local Manual

**Files:**
- Create: `Result/本机Workbench自动提取CSV工作流手册.md`

- [ ] **Step 1: Write manual**

Create a Chinese manual containing:

```text
1. 适用目标：本机 Workbench 2025 R2，输入位于 E:/WCL/AnsysTunnel。
2. 输入目录约定：<case>.wbpj、<case>_files、RSTVoidBatch/<case>.rst。
3. 输出目录：AutoCSVResult/<case>/FaceAccel_*.CSV 和 AutoCSVResult/<case>.zip。
4. 单工况命令：python -m rst2csv.cli local-run Void.112.510。
5. 批量命令：python -m rst2csv.cli local-run Void.40.245 Void.67.675 Void.112.510。
6. 如何修改默认路径：config.py 和命令行参数。
7. 中断和重跑：先确认无 RunWB2.exe、AnsysFW.exe、ansyswbu.exe 残留进程。
8. 日志位置：AutoCSVResult/<case>/_mechanical_batch。
9. 验证方法：Void.85.210 与 OriginData 比较，预留 40-60 分钟。
```

- [ ] **Step 2: Review manual for command accuracy**

Run:

```powershell
Select-String -Path "Result/本机Workbench自动提取CSV工作流手册.md" -Pattern "local-run|AutoCSVResult|RunWB2"
```

Expected: the documented commands and paths appear.

### Task 4: Full Verification

**Files:**
- Modify if needed: `Result/本机Workbench自动提取CSV工作流手册.md`
- Create or modify if needed: `Result/本机Workbench自动提取CSV验证报告.md`

- [ ] **Step 1: Run full unit tests**

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

Expected: all tests OK.

- [ ] **Step 2: Run local dry-run**

Run:

```powershell
$env:PYTHONPATH='src'
$case = 'Void.85.210'
$wbRoot = (Resolve-Path -LiteralPath "LocalWorkbenchVerifyFresh/TruthTest_$case").Path
$outRoot = Join-Path $wbRoot 'AutoCSVResult'
python -m rst2csv.cli local-run $case `
  --workbench-root $wbRoot `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root $outRoot `
  --dry-run
```

Expected: generated Workbench journal and Mechanical script under `LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/_mechanical_batch/`.

- [ ] **Step 3: Run local end-to-end verification**

Before running, copy the fresh source project from `OriginData/RST2CSVFiles` to an ignored isolated directory and confirm cached histories are 0. Then run only when ready to reserve 40-60 minutes:

```powershell
$env:PYTHONPATH='src'
$case = 'Void.85.210'
$wbRoot = (Resolve-Path -LiteralPath "LocalWorkbenchVerifyFresh/TruthTest_$case").Path
$outRoot = Join-Path $wbRoot 'AutoCSVResult'
python -m rst2csv.cli local-run $case `
  --workbench-root $wbRoot `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root $outRoot `
  --runwb2 "D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe" `
  --mechanical-timeout-seconds 14400
```

Expected: 7 CSV files and `LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210.zip`; cached histories increase from 0 to 700.

- [ ] **Step 4: Compare against reference CSVs**

Run:

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli validate Void.85.210 --output-root LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult
```

Expected: every face reports `probe_max_abs_error=0` and `all_max_abs_error=0`.

- [ ] **Step 5: Commit implementation**

Run:

```powershell
git add src/rst2csv/config.py src/rst2csv/local_paths.py src/rst2csv/cli.py tests/test_local_paths.py tests/test_cli_exact.py "Result/本机Workbench自动提取CSV工作流手册.md" "Result/本机Workbench自动提取CSV验证报告.md"
git commit -m "feat: add local workbench rst2csv workflow"
```
