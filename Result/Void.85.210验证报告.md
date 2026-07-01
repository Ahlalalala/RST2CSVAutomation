# 精确工作流验证报告

## 验证命令

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli check
python -m unittest discover -s tests -v
python -m rst2csv.cli run
```

## 工作流范围

主代码现在只保留精确工作流：

- `python -m rst2csv.cli export <case>`
- `python -m rst2csv.cli validate <case>`
- `python -m rst2csv.cli run`

旧的非精确 RST 节点聚合/校准代码、测试和旧输出已经移动到：

```text
NonExactWorkflow_ToDelete/
```

## 单元测试

当前保留测试全部面向精确工作流：

- CSV 表头和 Workbench 数值格式；
- CLI 精确命令和集中配置；
- RST 时间步读取；
- `SYS.mechdb` chunked zlib 解压和探针历史提取；
- CSV 验证器。

## 真实数据验证结果

输出目录：

```text
GeneratedExact/
```

对比基准：

```text
Backup/OriginData/
```

三组工况全部结构一致：

- 每个工况 7 个 `FaceAccel_*.CSV`
- 每个文件 977 行，含 1 行表头和 976 行结果
- 每个文件 103 列
- 表头与手工 Workbench CSV 一致

探针列最大误差：

| 工况 | Face A | Face B | Face C | Face D | Face E | Face F | Face G |
|---|---:|---:|---:|---:|---:|---:|---:|
| Void.13.375 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 |
| Void.85.210 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 |
| Void.175.575 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 | 1e-05 |

探针列 RMSE 均小于 `3e-07`。

全部数值列最大误差为 `5e-05` 到 `5.74121e-05`，主要来自时间列/显示格式舍入；结论以加速度探针列误差为准。
