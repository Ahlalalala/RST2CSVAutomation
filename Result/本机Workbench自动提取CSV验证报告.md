# 本机 Workbench 自动提取 CSV 验证报告

## 验证环境

- 工作空间：`D:/Developing_WCL/RST2CSV`
- Workbench：`D:/Program Files/ANSYS Inc R2/v252/Framework/bin/Win64/RunWB2.exe`
- Workbench 版本：2025 R2
- 验证工况：`Void.85.210`
- Workbench 工程：`E:/WCL/AnsysTunnel/Void.85.210.wbpj`
- Workbench files：`E:/WCL/AnsysTunnel/Void.85.210_files`
- RST：`E:/WCL/AnsysTunnel/RSTVoidBatch/Void.85.210.rst`
- 输出目录：`E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210`

## 验证命令

先执行 dry-run，确认本机路径和批处理脚本生成正确：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.85.210 --dry-run
```

实际端到端运行：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli local-run Void.85.210 --mechanical-timeout-seconds 14400
```

验证命令：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli validate Void.85.210 --output-root E:/WCL/AnsysTunnel/AutoCSVResult
```

## 输出文件

```text
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_A.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_B.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_C.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_D.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_E.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_F.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210/FaceAccel_G.CSV
E:/WCL/AnsysTunnel/AutoCSVResult/Void.85.210.zip
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

## 数值验证

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

## 逐字节验证

与 `D:/Developing_WCL/RST2CSV/OriginData/Void.85.210/FaceAccel_*.CSV` 对比，7 个输出文件 MD5 完全一致：

| 文件 | 逐字节一致 | MD5 |
|---|---:|---|
| FaceAccel_A.CSV | 是 | `e6df7ca9b4a639b4c7190037a2d46200` |
| FaceAccel_B.CSV | 是 | `928348fc775d1988b4a8c7a22d90ccf8` |
| FaceAccel_C.CSV | 是 | `71afbd39d7a1beff8c11dc992f9ad56f` |
| FaceAccel_D.CSV | 是 | `fbd0719fb8c82fa3375ae0eba6142c4a` |
| FaceAccel_E.CSV | 是 | `e1ca3eede4e3556bd9a8206b3de334b9` |
| FaceAccel_F.CSV | 是 | `8823407b7c7a8b2a694c017019698d23` |
| FaceAccel_G.CSV | 是 | `c5b578271b9678d947c732323d972620` |

## 结论

本机 `local-run` 工作流已达到目标：基于本机 Workbench 工程、`<case>_files` 和未手动载入的 `.rst` 文件，自动生成的 7 个 CSV 与测试数据逐字节一致，数值误差为 0。

本次实测耗时约 5 分钟；考虑不同工况、磁盘状态和 Workbench 启动状态差异，手册仍建议为单次完整测试预留 40-60 分钟。
