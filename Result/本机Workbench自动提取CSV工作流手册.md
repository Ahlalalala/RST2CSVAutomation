# 本机 Workbench 自动提取 CSV 工作流手册

本手册用于 Windows 本机环境：基于 `E:/WCL/AnsysTunnel` 下的 Workbench 工程和 `E:/WCL/AnsysTunnel/RSTVoidBatch` 下的未载入 `.rst` 文件，自动生成与手工测试数据格式一致的 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`。

该流程使用 Workbench/Mechanical 生成高精度 `SYS.mechdb` 探针历史缓存，再由 Python 读取缓存写出 CSV。不要把它理解为低精度文本导出。

## 1. 默认目录

以 `Void.112.510` 为例，输入应为：

```text
E:/WCL/AnsysTunnel/Void.112.510.wbpj
E:/WCL/AnsysTunnel/Void.112.510_files/
E:/WCL/AnsysTunnel/RSTVoidBatch/Void.112.510.rst
```

`Void.112.510_files` 内需要保留：

```text
dp0/global/MECH/SYS.mechdb
dp0/SYS/MECH/ds.dat
dp0/SYS/MECH/CAERep.xml
```

默认 Workbench 启动器：

```text
D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe
```

默认输出目录：

```text
E:/WCL/AnsysTunnel/AutoCSVResult/
```

成功后输出：

```text
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510/FaceAccel_A.CSV
...
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510/FaceAccel_G.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.112.510.zip
```

## 2. 单工况运行

在项目源码目录打开 PowerShell：

```powershell
cd D:/Developing_WCL/RST2CSV
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.112.510
```

## 3. 批量运行

多个工况直接写在同一条命令后面：

```powershell
cd D:/Developing_WCL/RST2CSV
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.40.245 Void.67.675 Void.112.510
```

脚本会按顺序逐个运行，不会并行启动多个 Workbench。这样更稳，也避免多个 Mechanical 同时写工程文件。

## 4. 临时覆盖路径

如果目录变化，可在命令中覆盖：

```powershell
python -m rst2csv.cli local-run Void.112.510 `
  --workbench-root E:/WCL/AnsysTunnel `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root E:/WCL/AnsysTunnel/AutoCSVResult `
  --runwb2 "D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe"
```

如果长期修改默认路径，编辑：

```text
src/rst2csv/config.py
```

重点配置：

```python
LOCAL_WORKBENCH_ROOT = Path("E:/WCL/AnsysTunnel")
LOCAL_RST_ROOT = Path("E:/WCL/AnsysTunnel/RSTVoidBatch")
LOCAL_OUTPUT_ROOT = Path("E:/WCL/AnsysTunnel/AutoCSVResult")
LOCAL_RUNWB2_PATH = Path("D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe")
```

## 5. 日志位置

每个工况的 Workbench 批处理文件和日志位于：

```text
E:/WCL/AnsysTunnel/AutoCSVResult/<case>/_mechanical_batch/
```

常用文件：

```text
run_workbench.wbjn
export_probes_mechanical.py
workbench_stdout.log
workbench_stderr.log
mechanical_status.txt
```

`mechanical_status.txt` 首行为 `OK` 表示 Mechanical 已成功生成探针历史缓存；首行为 `ERROR` 时，后续内容是 Mechanical Python 的错误堆栈。

## 6. 中断和重跑

如果运行中断，先确认没有残留进程，再重跑同一工况。PowerShell 中可检查：

```powershell
Get-Process | Where-Object {
  $_.ProcessName -match 'RunWB2|AnsysFW|ansyswbu|AnsysWBU|mono'
}
```

如果确认要清理残留进程，可在任务管理器中结束对应 Workbench/Mechanical 进程，或谨慎使用：

```powershell
Get-Process | Where-Object {
  $_.ProcessName -match 'RunWB2|AnsysFW|ansyswbu|AnsysWBU'
} | Stop-Process
```

不要在同一个工况仍运行时再次启动同一工况；否则可能同时写同一个 `<case>_files`。

## 7. 验证 0 误差

本机端到端验证建议使用已有参考数据 `Void.85.210`。注意：如果 `E:/WCL/AnsysTunnel/<case>_files` 已经完成过 RST 载入，它只能验证读取和导出链路，不能证明 fresh 工程自动载入性能。

真实 fresh 验证应先从仓库内的未载入工程复制一份隔离副本：

```powershell
cd D:/Developing_WCL/RST2CSV
$case = 'Void.85.210'
$destRoot = Join-Path (Get-Location) "LocalWorkbenchVerifyFresh/TruthTest_$case"
New-Item -ItemType Directory -Force -Path $destRoot | Out-Null
Copy-Item -LiteralPath "OriginData/RST2CSVFiles/$case.wbpj" -Destination (Join-Path $destRoot "$case.wbpj")
Copy-Item -LiteralPath "OriginData/RST2CSVFiles/${case}_files" -Destination (Join-Path $destRoot "${case}_files") -Recurse
```

然后对这份隔离副本运行：

```powershell
cd D:/Developing_WCL/RST2CSV
$case = 'Void.85.210'
$wbRoot = (Resolve-Path -LiteralPath "LocalWorkbenchVerifyFresh/TruthTest_$case").Path
$outRoot = Join-Path $wbRoot 'AutoCSVResult'
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run $case `
  --workbench-root $wbRoot `
  --rst-root E:/WCL/AnsysTunnel/RSTVoidBatch `
  --output-root $outRoot `
  --runwb2 "D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe" `
  --mechanical-timeout-seconds 14400
```

完成后验证：

```powershell
python -m rst2csv.cli validate Void.85.210 --output-root LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult
```

目标输出中每个文件应为：

```text
probe_max_abs_error=0
all_max_abs_error=0
```

如果需要先检查命令和脚本生成，不真正启动 Workbench，可运行：

```powershell
python -m rst2csv.cli local-run Void.85.210 --dry-run
```

本次已完成的验证记录见：

```text
Result/本机Workbench自动提取CSV验证报告.md
```

该验证使用 `OriginData/RST2CSVFiles` 的 fresh 副本，运行前缓存历史数为 0，运行后为 700，耗时约 34 分 57 秒，7 个 CSV 与参考数据逐字节一致。

## 8. 注意事项

- 运行 Workbench 后，对应 `<case>_files/dp0/global/MECH/SYS.mechdb` 会被 Workbench 保存更新，这是生成高精度 CSV 所需步骤。
- `.rst` 文件不会被移动或复制。
- 输出 CSV 和 zip 只写入 `AutoCSVResult`。
- 不要使用旧的低精度文本导出流程作为最终结果来源。
