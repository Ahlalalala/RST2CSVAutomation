# 无缓存 RST 自动提取 CSV 验证报告

## 验证环境

- 工作空间：`D:\Developing_WCL\RST2CSV`
- 本机 Workbench：`D:\Program Files\ANSYS Inc R2\v252\Framework\bin\Win64\RunWB2.exe`
- Workbench 版本：2025 R2
- 验证工况：`Void.85.210`
- RST 文件：`E:\WCL\AnsysTunnel\RSTVoidBatch\Void.85.210.rst`
- fresh 工程来源：`OriginData/RST2CSVFiles/Void.85.210.wbpj` 和 `OriginData/RST2CSVFiles/Void.85.210_files`
- 隔离验证目录：`LocalWorkbenchVerifyFresh/`

## 验证步骤

1. 从 `OriginData/RST2CSVFiles` 重新复制 fresh Workbench 工程到 `LocalWorkbenchVerifyFresh/RST2CSVFiles/`。
2. 在 `LocalWorkbenchVerifyFresh/TaskDir_Void.85.210/` 中建立 `Void.85.210.rst` 软链接，未移动原始 293GB RST。
3. 验证 fresh `SYS.mechdb` 中探针历史数为 0。
4. 运行：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli mechanical-hpc-run Void.85.210 `
  --base-dir (Resolve-Path 'LocalWorkbenchVerifyFresh').Path `
  --runwb2 'D:\Program Files\ANSYS Inc R2\v252\Framework\bin\Win64\RunWB2.exe' `
  --mechanical-timeout-seconds 14400
```

5. Workbench 自动生成 `file.rst` 链接，评价 700 个 `Face_Accel_Probe_*`，保存后 `SYS.mechdb` 从 46,211,288 字节增至 69,546,296 字节。
6. Python 从更新后的 `SYS.mechdb` 读取 700 个高精度历史并生成 7 个 CSV 与 zip。

## 输出检查

生成文件：

```text
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_A.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_B.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_C.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_D.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_E.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_F.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210/FaceAccel_G.CSV
LocalWorkbenchVerifyFresh/CSVResult/Void.85.210.zip
```

压缩包内部包含：

```text
Void.85.210/FaceAccel_A.CSV
Void.85.210/FaceAccel_B.CSV
Void.85.210/FaceAccel_C.CSV
Void.85.210/FaceAccel_D.CSV
Void.85.210/FaceAccel_E.CSV
Void.85.210/FaceAccel_F.CSV
Void.85.210/FaceAccel_G.CSV
```

## 精度结论

与 `OriginData/Void.85.210/FaceAccel_*.CSV` 逐字节比较，7 个文件全部完全一致：

| 文件 | 逐字节一致 | MD5 |
|---|---:|---|
| FaceAccel_A.CSV | 是 | `e6df7ca9b4a639b4c7190037a2d46200` |
| FaceAccel_B.CSV | 是 | `928348fc775d1988b4a8c7a22d90ccf8` |
| FaceAccel_C.CSV | 是 | `71afbd39d7a1beff8c11dc992f9ad56f` |
| FaceAccel_D.CSV | 是 | `fbd0719fb8c82fa3375ae0eba6142c4a` |
| FaceAccel_E.CSV | 是 | `e1ca3eede4e3556bd9a8206b3de334b9` |
| FaceAccel_F.CSV | 是 | `8823407b7c7a8b2a694c017019698d23` |
| FaceAccel_G.CSV | 是 | `c5b578271b9678d947c732323d972620` |

验证器输出：

```text
FaceAccel_A.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_B.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_C.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_D.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_E.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_F.CSV: probe_max_abs_error=0, all_max_abs_error=0
FaceAccel_G.CSV: probe_max_abs_error=0, all_max_abs_error=0
```

结论：当前 `mechanical-hpc-run` 工作流已满足“完全一致”要求。它不是读取旧缓存，也不是低精度文本导出；验证从 0 个探针缓存的 fresh `SYS.mechdb` 开始，最终 CSV 与目标 CSV 逐字节一致。
