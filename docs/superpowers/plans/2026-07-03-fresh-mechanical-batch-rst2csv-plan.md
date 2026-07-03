# Fresh Mechanical Batch RST2CSV Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 fresh Workbench 工程的 Mechanical batch 精确导出命令。

**Architecture:** Python CLI 负责路径检查、脚本生成、`runwb2` 调用、probe 文本解析、CSV 聚合和 zip 打包；Workbench/Mechanical batch 负责真正评估 ResultProbe。

**Tech Stack:** Python `unittest`、Workbench journal、Mechanical Python、现有 `ansys-mapdl-reader` 时间步读取和 CSV 格式化代码。

---

### Task 1: 路径与 CLI

**Files:**
- Modify: `src/rst2csv/config.py`
- Modify: `src/rst2csv/hpc_paths.py`
- Modify: `src/rst2csv/cli.py`
- Test: `tests/test_cli_exact.py`
- Test: `tests/test_hpc_paths.py`

- [x] 添加 `CSVResult`、`RST2CSV_RUNWB2`、Workbench component 默认配置。
- [x] 在 HPC 路径对象中加入 `.wbpj`、batch 目录、probe 文本目录和状态文件。
- [x] 新增 `mechanical-hpc-run` 参数。

### Task 2: Mechanical Batch 边界

**Files:**
- Create: `src/rst2csv/mechanical_batch.py`
- Test: `tests/test_mechanical_batch.py`

- [x] 写失败测试覆盖 journal 生成、`runwb2` 查找、probe 文本解析、CSV 聚合。
- [x] 实现 Workbench journal 和 Mechanical Python 脚本生成。
- [x] 实现 `runwb2 -B -R` 调用与日志保存。
- [x] 实现 700 个 probe 文本聚合为目标 CSV。

### Task 3: HPC 使用文档

**Files:**
- Create: `scripts/rst2csv_mechanical.slurm`
- Create: `Result/无缓存RST自动提取CSV工作流手册.md`

- [x] 提供 Slurm 模板，配置集中在文件开头。
- [x] 说明源码、`RST2CSVFiles`、RST、`.dat` 和输出路径。
- [x] 说明 `runwb2` 必需性、dry-run、正式提交和常见错误。
