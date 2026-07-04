# 本机 Workbench 自动提取 CSV 真实 fresh 验证报告

## 1. 验证目的

本次验证专门纠正一个关键问题：`E:/WCL/AnsysTunnel` 下的 `<case>_files` 已经完成过 RST 载入，不能代表“未载入 RST 的 fresh 工程”性能。

因此本次真实验证不使用 `E:/WCL/AnsysTunnel/Void.85.210_files`，而是从：

```text
D:/Developing_WCL/RST2CSV/OriginData/RST2CSVFiles/
```

复制 fresh Workbench 工程到工作区隔离目录，再运行本机 `local-run`。

## 2. 验证环境

- 工作空间：`D:/Developing_WCL/RST2CSV`
- Workbench：`D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe`
- Workbench 版本：2025 R2
- 验证工况：`Void.85.210`
- fresh 工程源：
  - `OriginData/RST2CSVFiles/Void.85.210.wbpj`
  - `OriginData/RST2CSVFiles/Void.85.210_files`
- 隔离工作副本：
  - `LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/Void.85.210.wbpj`
  - `LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/Void.85.210_files`
- RST：
  - `E:/WCL/AnsysTunnel/RSTVoidBatch/Void.85.210.rst`
- 输出：
  - `LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210`

## 3. fresh 状态确认

运行前读取隔离副本中的：

```text
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/Void.85.210_files/dp0/global/MECH/SYS.mechdb
```

检测结果：

```text
result_sets= 976
cached_probe_histories= 0
first_probe_keys= []
```

这说明本次输入确实是未生成探针历史缓存的 fresh 工程。

## 4. 运行命令

```powershell
$case = 'Void.85.210'
$wbRoot = (Resolve-Path -LiteralPath "LocalWorkbenchVerifyFresh\TruthTest_$case").Path
$outRoot = Join-Path $wbRoot 'AutoCSVResult'
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run $case `
  --workbench-root $wbRoot `
  --rst-root 'E:/WCL/AnsysTunnel/RSTVoidBatch' `
  --output-root $outRoot `
  --runwb2 'D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe' `
  --mechanical-timeout-seconds 14400
```

运行输出：

```text
Void.85.210: generated Workbench journal: D:\Developing_WCL\RST2CSV\LocalWorkbenchVerifyFresh\TruthTest_Void.85.210\AutoCSVResult\Void.85.210\_mechanical_batch\run_workbench.wbjn
Void.85.210: generated Mechanical script: D:\Developing_WCL\RST2CSV\LocalWorkbenchVerifyFresh\TruthTest_Void.85.210\AutoCSVResult\Void.85.210\_mechanical_batch\export_probes_mechanical.py
Void.85.210: exported 7 exact cached Mechanical files to D:\Developing_WCL\RST2CSV\LocalWorkbenchVerifyFresh\TruthTest_Void.85.210\AutoCSVResult\Void.85.210
Void.85.210: packaged D:\Developing_WCL\RST2CSV\LocalWorkbenchVerifyFresh\TruthTest_Void.85.210\AutoCSVResult\Void.85.210.zip
elapsed_seconds=2097.082
elapsed_hhmmss=00:34:57.0817820
```

真实 fresh 运行耗时约 **34 分 57 秒**。

## 5. 运行后缓存确认

运行后再次读取隔离副本 `SYS.mechdb`：

```text
result_sets= 976
cached_probe_histories= 700
first_probe_keys= [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
```

这说明 Workbench/Mechanical 已从 RST 自动生成 700 个探针历史缓存。

## 6. 输出文件

```text
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_A.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_B.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_C.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_D.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_E.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_F.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210/FaceAccel_G.CSV
LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult/Void.85.210.zip
```

压缩包内部结构：

```text
Void.85.210/FaceAccel_A.CSV
Void.85.210/FaceAccel_B.CSV
Void.85.210/FaceAccel_C.CSV
Void.85.210/FaceAccel_D.CSV
Void.85.210/FaceAccel_E.CSV
Void.85.210/FaceAccel_F.CSV
Void.85.210/FaceAccel_G.CSV
```

## 7. 数值验证

验证命令：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli validate Void.85.210 `
  --output-root LocalWorkbenchVerifyFresh/TruthTest_Void.85.210/AutoCSVResult
```

验证器输出：

```text
Void.85.210/FaceAccel_A.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_B.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_C.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_D.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_E.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_F.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
Void.85.210/FaceAccel_G.CSV: OK, probe_max_abs_error=0, probe_rmse=0, all_max_abs_error=0, all_rmse=0, numeric_cells=100528
```

## 8. 逐字节验证

与 `OriginData/Void.85.210/FaceAccel_*.CSV` 对比，7 个文件逐字节一致：

| 文件 | 逐字节一致 | MD5 |
|---|---:|---|
| FaceAccel_A.CSV | 是 | `e6df7ca9b4a639b4c7190037a2d46200` |
| FaceAccel_B.CSV | 是 | `928348fc775d1988b4a8c7a22d90ccf8` |
| FaceAccel_C.CSV | 是 | `71afbd39d7a1beff8c11dc992f9ad56f` |
| FaceAccel_D.CSV | 是 | `fbd0719fb8c82fa3375ae0eba6142c4a` |
| FaceAccel_E.CSV | 是 | `e1ca3eede4e3556bd9a8206b3de334b9` |
| FaceAccel_F.CSV | 是 | `8823407b7c7a8b2a694c017019698d23` |
| FaceAccel_G.CSV | 是 | `c5b578271b9678d947c732323d972620` |

## 9. 结论

本机 `local-run` 工作流已经通过真实 fresh 工程验证：

- 初始 `SYS.mechdb` 中探针历史缓存数为 0。
- Workbench/Mechanical 自动载入 RST 并生成 700 个探针历史缓存。
- Python 自动导出 7 个 CSV 和 zip。
- 7 个 CSV 与目标测试数据逐字节一致，数值误差为 0。
- `Void.85.210` 本次真实 fresh 运行耗时约 34 分 57 秒。

因此，手册中建议为单次完整 fresh 测试预留 40-60 分钟是合理的。
