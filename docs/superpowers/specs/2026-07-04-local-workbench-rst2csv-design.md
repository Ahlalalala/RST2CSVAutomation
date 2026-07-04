# 本机 Workbench RST 自动提取 CSV 工作流设计

## 目标

在 Windows 本机恢复并固化一套可复用工作流：基于 `E:/WCL/AnsysTunnel` 下的 Workbench 工程文件、同名 `<case>_files` 目录，以及 `E:/WCL/AnsysTunnel/RSTVoidBatch` 下未手动载入的 `.rst` 文件，自动生成与既有测试数据格式一致、误差为 0 的 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`。

默认输出目录为：

```text
E:/WCL/AnsysTunnel/AutoCSVResult/
```

每个工况输出到独立子目录：

```text
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510/FaceAccel_A.CSV
...
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510/FaceAccel_G.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510.zip
```

## 输入约定

以 `Void.112.510` 为例，默认输入为：

```text
E:/WCL/AnsysTunnel/Void.112.510.wbpj
E:/WCL/AnsysTunnel/Void.112.510_files/
E:/WCL/AnsysTunnel/RSTVoidBatch/Void.112.510.rst
```

`<case>_files` 内仍按 Workbench 默认结构读取：

```text
<case>_files/dp0/global/MECH/SYS.mechdb
<case>_files/dp0/SYS/MECH/ds.dat
<case>_files/dp0/SYS/MECH/CAERep.xml
```

默认 Workbench 入口为：

```text
D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe
```

这些路径需要集中放在代码靠近开头的位置，便于后续手动修改。

## 推荐命令

新增本机专用命令：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.112.510
```

批量运行：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.40.245 Void.67.675 Void.112.510
```

可覆盖默认路径：

```powershell
python -m rst2csv.cli local-run Void.112.510 `
  --workbench-root E:/WCL/AnsysTunnel `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root E:/WCL/AnsysTunnel/AutoCSVResult `
  --runwb2 "D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe"
```

## 工作流

本机工作流复用已经验证的 fresh Workbench 批处理链路：

1. 检查 `.wbpj`、`<case>_files`、`.rst`、`SYS.mechdb`、`ds.dat`、`CAERep.xml` 是否存在。
2. 生成 Workbench journal 和 Mechanical Python 脚本到输出目录的 `_mechanical_batch/`。
3. 调用 `RunWB2.exe -B -R <journal>` 打开 Workbench 工程。
4. Mechanical 脚本把同名 `.rst` 作为 `file.rst` 链接或挂载到 Mechanical 工作目录。
5. Mechanical 评价已有的 700 个 `Face_Accel_Probe_*`，保存高精度历史缓存到 `SYS.mechdb`。
6. Python 读取更新后的 `SYS.mechdb` double 缓存，生成 7 个 Workbench 格式 CSV。
7. 将 7 个 CSV 打包为 `<case>.zip`，压缩包内保留 `<case>/FaceAccel_*.CSV` 结构。

该流程不使用低精度文本导出，不使用 `SequenceTotalVector(i)` 作为最终数据源。

## 架构改动

新增 `src/rst2csv/local_paths.py`，负责本机路径约定：

- `workbench_root`：默认 `E:/WCL/AnsysTunnel`
- `rst_root`：默认 `E:/WCL/AnsysTunnel/RSTVoidBatch`
- `output_root`：默认 `E:/WCL/AnsysTunnel/AutoCSVResult`
- `project_path`：`<workbench_root>/<case>.wbpj`
- `files_root`：`<workbench_root>/<case>_files`
- `rst_path`：`<rst_root>/<case>.rst`
- `output_dir`：`<output_root>/<case>`
- `zip_path`：`<output_root>/<case>.zip`

修改 `src/rst2csv/config.py` 增加本机默认路径配置。

修改 `src/rst2csv/cli.py` 增加 `local-run` 子命令。为避免复制现有 `mechanical-hpc-run` 的主体逻辑，将提取出一个共享的 fresh Workbench 执行函数，供 `mechanical-hpc-run` 和 `local-run` 使用。

既有 `mechdb_cache.py`、`csv_format.py`、`rst_reader.py` 的核心算法不改动。

## 错误处理

缺少输入文件时，命令应明确报出第一个缺失路径。

Workbench 批处理失败时，保留：

```text
<output_root>/<case>/_mechanical_batch/workbench_stdout.log
<output_root>/<case>/_mechanical_batch/workbench_stderr.log
<output_root>/<case>/_mechanical_batch/mechanical_status.txt
```

如果 `mechanical_status.txt` 首行为 `ERROR`，提示用户查看该文件中的 Mechanical Python 堆栈。

如果中断重跑，手册说明应提醒用户先确认没有残留 `RunWB2.exe`、`AnsysFW.exe`、`ansyswbu.exe` 等进程，再重新运行同一工况。

## 验证策略

单元测试覆盖：

- 本机路径解析是否符合 `E:/WCL/AnsysTunnel` 目录约定。
- `local-run` CLI 默认参数与覆盖参数。
- 本机输出打包结构是否为 `<case>/FaceAccel_*.CSV`。
- `mechanical-hpc-run` 既有行为不受影响。

端到端验证使用本机 Workbench 2025 R2 和 `Void.85.210`。由于 `E:/WCL/AnsysTunnel` 下现有 `<case>_files` 可能已经完成过 RST 载入，真实 fresh 验证必须先从 `OriginData/RST2CSVFiles` 复制一份未载入工程到工作目录隔离副本，例如：

```text
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/
|-- Void.85.210.wbpj
`-- Void.85.210_files/
```

并先确认隔离副本中的 `SYS.mechdb` 缓存历史数为 0。随后运行：

```powershell
$env:PYTHONPATH='src'
$case = 'Void.85.210'
$wbRoot = (Resolve-Path -LiteralPath "LocalWorkbenchVerifyFresh/TruthTest_$case").Path
$outRoot = Join-Path $wbRoot 'AutoCSVResult'
python -m rst2csv.cli local-run Void.85.210 `
  --workbench-root $wbRoot `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root $outRoot `
  --runwb2 "D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe" `
  --mechanical-timeout-seconds 14400
```

全套端到端验证单次应预留 40-60 分钟。验证完成后，将隔离副本 `AutoCSVResult/Void.85.210/FaceAccel_*.CSV` 与 `OriginData/Void.85.210/FaceAccel_*.CSV` 比较，目标为 7 个文件逐字节一致，验证器显示 `probe_max_abs_error=0` 和 `all_max_abs_error=0`。

## 手册

新增中文手册：

```text
Result/本机Workbench自动提取CSV工作流手册.md
```

手册包含：

- 目录如何放置。
- 单工况与批量命令。
- 如何修改默认路径。
- 如何处理中断、重跑和 Workbench 残留进程。
- 如何查看日志。
- 如何用 `Void.85.210` 做 0 误差验证。

## 不做的事

本设计不再扩展 HPC/VNC 自动运行方案。

本设计不移动或删除 `E:/WCL/AnsysTunnel` 下已有工程、`<case>_files` 或 `.rst` 文件。Workbench 保存工程时会更新对应 `<case>_files` 内的 `SYS.mechdb` 缓存，这是生成高精度 CSV 所需的 Workbench 行为。
