# Fresh 工程 RST 精确导出设计

## 背景

旧的精确工作流依赖 `SYS.mechdb` 中已缓存的 `Face_Accel_Probe_*` 历史。用户指出 fresh `<case>_files` 删除了已生成结果，此时缓存不存在，旧流程会报 `cached histories missing probes`。纯 Python 直接读取 RST 节点并按传感器实体聚合不能稳定复现 Workbench ResultProbe，尤其 `Void.175.575` 与参考 CSV 存在量级差异。

## 目标

在不手动导入 RST 的前提下，由 HPC 终端自动生成 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV` 和 `<case>.zip`。精度路线必须沿用 Mechanical 自身的 ResultProbe scoping、插值、`SpatialResolution=Max` 与时间历史导出逻辑，避免非精确近似。

## 方案

新增 `mechanical-hpc-run` 命令。命令按照 HPC 目录契约检查 `.dat`、`.rst`、`.wbpj`、`SYS.mechdb`、`ds.dat`、`CAERep.xml`，随后生成 Workbench journal 和 Mechanical Python 脚本。Workbench batch 通过 `runwb2 -B -R run_workbench.wbjn` 打开 fresh 项目，Mechanical 脚本尝试把外部 RST 软链接为分析工作目录下的 `file.rst`，自动评估所有 `Face_Accel_Probe_*`，并逐个 `ExportToTextFile`。

Workbench 退出后，CPython 读取 700 个 probe 文本文件，按 RST 时间步重组为既有 CSV 格式，并使用原有打包逻辑生成 zip。

## 边界

本方案要求 HPC 安装或可加载 Ansys Workbench/Mechanical batch 启动器 `runwb2`。如果只有求解器或只有普通 Python，无法精确复现 Workbench ResultProbe。旧 `hpc-run` 保留，但只用于已经有缓存历史的项目。

## 验证

本机没有 Ansys Workbench，无法实跑 `runwb2`。已用单元测试覆盖路径契约、journal 生成、`runwb2` 查找、probe 文本解析、CSV 聚合和 CLI 参数。真实精度验证应在 HPC 上完成一次 `mechanical-hpc-run` 后，与手动导出的 `OriginData/<case>/FaceAccel_*.CSV` 比较。
