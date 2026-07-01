# Linux/HPC RST2CSV 迁移实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标:** 新增 Linux/HPC 终端一键导出命令 `hpc-run`，按指定目录约定自动定位输入文件、导出 CSV 并生成 zip。

**架构:** 新增 `hpc_paths.py` 负责 Linux/HPC 路径解析、文件检查和 zip 打包；`cli.py` 只负责接收命令参数并调用现有精确导出核心。保持 Windows/本地精确工作流不变。

**技术栈:** Python 标准库 `pathlib`、`zipfile`、`argparse`；现有 `ansys-mapdl-reader` 和 `h5py`。

---

### 任务 1：HPC 路径解析和打包工具

**文件:**
- 创建: `src/rst2csv/hpc_paths.py`
- 创建: `tests/test_hpc_paths.py`

- [ ] **步骤 1：写失败测试**

测试内容：

```python
def test_hpc_case_paths_follow_remote_directory_contract():
    paths = HpcCasePaths.from_base_and_case(Path("/base"), "Void.112.510")
    assert paths.dat_path == Path("/base/Void.112.510.dat")
    assert paths.rst_path == Path("/base/TaskDir_Void.112.510/Void.112.510.rst")
    assert paths.mechdb_path == Path("/base/RST2CSV/Void.112.510_files/dp0/global/MECH/SYS.mechdb")
    assert paths.dsdat_path == Path("/base/RST2CSV/Void.112.510_files/dp0/SYS/MECH/ds.dat")
    assert paths.caerep_path == Path("/base/RST2CSV/Void.112.510_files/dp0/SYS/MECH/CAERep.xml")
    assert paths.output_dir == Path("/base/CSVResult/Void.112.510")
    assert paths.zip_path == Path("/base/CSVResult/Void.112.510.zip")
```

- [ ] **步骤 2：运行测试确认失败**

运行：

```bash
PYTHONPATH=src python -m unittest tests.test_hpc_paths -v
```

期望：因为 `rst2csv.hpc_paths` 不存在而失败。

- [ ] **步骤 3：实现最小路径解析**

创建 `HpcCasePaths` dataclass，提供 `from_base_and_case()`。

- [ ] **步骤 4：实现文件检查和 zip 打包测试**

测试 `require_inputs()` 能列出缺失文件，测试 `zip_output_dir()` 生成 `<case>.zip` 且 zip 内文件路径为 `<case>/FaceAccel_A.CSV`。

- [ ] **步骤 5：实现文件检查和 zip 打包**

使用 `zipfile.ZipFile(..., "w", ZIP_DEFLATED)`，只打包 `FaceAccel_*.CSV`。

### 任务 2：CLI 增加 hpc-run

**文件:**
- 修改: `src/rst2csv/cli.py`
- 修改: `src/rst2csv/config.py`
- 修改: `tests/test_cli_exact.py`

- [ ] **步骤 1：写失败测试**

测试 `build_parser().parse_args(["hpc-run", "Void.112.510"])` 默认 `base_dir` 等于 Linux 基础路径。

- [ ] **步骤 2：运行测试确认失败**

运行：

```bash
PYTHONPATH=src python -m unittest tests.test_cli_exact -v
```

期望：`hpc-run` 命令不存在。

- [ ] **步骤 3：实现 CLI 参数**

在 `config.py` 增加：

```python
HPC_BASE_DIR = Path("/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop")
```

在 `cli.py` 增加 `hpc-run` 子命令，参数：

```text
hpc-run <case> [--base-dir PATH]
```

- [ ] **步骤 4：实现 hpc-run 执行**

调用 `HpcCasePaths.from_base_and_case()`，检查文件，读取 RST 时间步，读取 `SYS.mechdb`，导出 CSV，再打包 zip。

### 任务 3：中文 HPC 操作手册

**文件:**
- 创建: `Result/Linux_HPC终端自动提取操作手册.md`
- 修改: `Result/RST直接导出CSV工作流说明.md`

- [ ] **步骤 1：撰写手册**

手册必须包含：

- 上传目录结构；
- 如何确认 `Void.112.510_files` 放在基础路径的 `RST2CSV/` 下；
- 如何安装依赖；
- 如何运行 `hpc-run`；
- 如何下载 `CSVResult/Void.112.510.zip`；
- 常见错误排查。

- [ ] **步骤 2：更新主说明**

在主说明中增加 Linux/HPC 入口，链接到单独手册。

### 任务 4：验证和发布

**文件:**
- 修改: `pyproject.toml` 如有需要
- GitHub remote: `https://github.com/Ahlalalala/RST2CSVAutomation.git`

- [ ] **步骤 1：运行测试**

```bash
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m rst2csv.cli run Void.85.210
```

- [ ] **步骤 2：本地提交**

```bash
git add src tests Result docs pyproject.toml
git commit -m "feat: add linux hpc workflow"
```

- [ ] **步骤 3：尝试推送**

```bash
git remote add origin https://github.com/Ahlalalala/RST2CSVAutomation.git
git push -u origin codex/linux-hpc-workflow
```

如果因认证失败不能推送，保留本地分支和提交，并在最终说明中写清楚。
