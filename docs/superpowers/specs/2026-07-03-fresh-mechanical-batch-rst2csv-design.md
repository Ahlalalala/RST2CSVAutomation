# Fresh 工程 RST 精确导出设计

## 背景

旧的精确工作流读取 `SYS.mechdb` 中已经缓存的 `Face_Accel_Probe_*` 历史。fresh `<case>_files` 删除了求解后生成数据，因此缓存不存在，旧命令会报 `cached histories missing probes`。

直接用 Python 从 RST 节点结果近似聚合不能稳定复现 Workbench ResultProbe。Mechanical 内部 `SequenceTotalVector(i)` 也只返回显示精度，不适合作为最终 CSV 数据源。

## 目标

在不手动打开 Workbench、不手动导入 RST 的前提下，由 HPC 终端自动生成：

- `CSVResult/<case>/FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`
- `CSVResult/<case>.zip`

精度必须沿用现有已验证的 `SYS.mechdb` double 缓存解析路径。

## 方案

新增 `mechanical-hpc-run` 命令：

1. 检查 `.dat`、`.rst`、`.wbpj`、`SYS.mechdb`、`ds.dat`、`CAERep.xml` 是否按 HPC 目录契约存在。
2. 生成 Workbench journal 和 Mechanical Python 脚本。
3. 调用 `runwb2 -B -R run_workbench.wbjn` 打开 fresh 工程。
4. Mechanical 脚本把外部 RST 软链接为分析工作目录下的 `file.rst`。
5. Mechanical 调用 `solution.EvaluateAllResults()` 并逐个 `RetrieveResult()`，使 700 个探针历史写入 `SYS.mechdb`。
6. Workbench 保存工程后，Python 读取更新后的 `SYS.mechdb`，使用原有 `load_probe_histories_from_mechdb` 和 `export_cached_probe_csvs` 生成目标 CSV。
7. 打包 `<case>.zip`。

## 边界

该方案要求 HPC 可加载 Ansys Workbench/Mechanical 2025R2 的 `runwb2`。只有 MAPDL 求解器或普通 Python 不足以精确复现 Workbench ResultProbe。

旧命令 `hpc-run` 保留，仅用于已经完成手工导入并缓存探针历史的工程。

## 验证重点

- 单元测试覆盖 journal 生成、`runwb2` 查找、RST 链接失败处理、CLI 参数和 HPC 路径契约。
- 本地 Workbench 2025R2 验证 `Void.85.210` 可由 fresh 工程生成 700 个高精度缓存历史。
- 端到端输出必须与 `OriginData/Void.85.210/FaceAccel_*.CSV` 进行结构和数值比对。
