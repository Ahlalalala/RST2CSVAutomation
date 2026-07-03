# Fresh Mechanical Batch RST2CSV 实施计划

**目标：** 支持 fresh Workbench 工程在 HPC 终端自动挂载 RST、生成高精度 `SYS.mechdb` 缓存、导出 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV` 并打包。

**架构：** Python CLI 负责路径检查、脚本生成、`runwb2` 调用、状态等待、`SYS.mechdb` 高精度解析、CSV 写出和 zip 打包；Workbench/Mechanical 只负责按原工程探针定义评价结果并保存缓存。

## Task 1: 路径与 CLI

涉及文件：

- `src/rst2csv/config.py`
- `src/rst2csv/hpc_paths.py`
- `src/rst2csv/cli.py`
- `tests/test_cli_exact.py`
- `tests/test_hpc_paths.py`

状态：

- [x] 增加 `RST2CSVFiles`、`CSVResult`、`RST2CSV_RUNWB2`、Workbench component、Mechanical 状态超时等集中配置。
- [x] 增加 `.wbpj`、batch 目录、状态文件路径。
- [x] 新增 `mechanical-hpc-run` 命令和 `--mechanical-timeout-seconds` 参数。
- [x] 删除旧状态文件并等待本次 `mechanical_status.txt`，避免 Workbench 后台执行时误读旧结果。

## Task 2: Mechanical Batch

涉及文件：

- `src/rst2csv/mechanical_batch.py`
- `tests/test_mechanical_batch.py`

状态：

- [x] 生成 Workbench journal。
- [x] 生成 Mechanical Python 脚本。
- [x] 脚本稳健创建 `file.rst` 软链接，Windows 尝试 `mklink`，Linux 尝试 `ln -s`。
- [x] 不再使用低精度 `ExportToTextFile` 或 `SequenceTotalVector`。
- [x] 调用 `solution.EvaluateAllResults()` 和 `probe.RetrieveResult()` 生成 `SYS.mechdb` 缓存。
- [x] 缓存为空时写入 `ERROR` 状态并终止。

## Task 3: HPC 使用文件

涉及文件：

- `scripts/rst2csv_mechanical.slurm`
- `Result/无缓存RST自动提取CSV工作流手册.md`

状态：

- [x] Slurm 模板按已实测 HPC 环境加载 `py310`、Intel oneAPI 和 Ansys 2025R2。
- [x] 模板显式传入 `runwb2` 路径。
- [x] 手册说明源码上传位置、`RST2CSVFiles`、RST、`.dat`、输出路径、依赖安装、3 个关键文件选择和常见错误。

## Task 4: 验证

状态：

- [x] 用 TDD 覆盖“不得使用低精度文本导出”和“RST 链接失败必须报错”。
- [x] 运行全部单元测试。
- [x] 使用本机 Workbench 2025R2 对 `Void.85.210` 做端到端验证。
- [x] 更新验证报告。
