# 精确导出 Workbench 探针 CSV 工作流说明

## 现在保留的工作流

当前主代码只保留精确工作流：从 `.rst` 读取时间步，从 Workbench/Mechanical 的 `SYS.mechdb` 读取已缓存的 `Face_Accel_Probe_N` 探针历史曲线，然后生成 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`。

旧的非精确 RST 节点聚合/校准工作流已经移出主代码，集中放在：

```text
NonExactWorkflow_ToDelete/
```

该目录可作为历史参考；正式使用时不要调用里面的内容。

## 路径集中配置

后续如果目录变化，优先改这个文件开头的配置区：

```text
src/rst2csv/config.py
```

当前默认配置：

```python
BACKUP_ROOT = Path("Backup")
RST_ROOT = Path("E:/WCL/AnsysTunnel/RSTVoidBatch")
OUTPUT_ROOT = Path("GeneratedExact")
```

## 命令

检查依赖：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli check
```

精确导出单个工况：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli export Void.85.210
```

精确导出并验证全部已备份工况：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli run
```

仅验证已有输出：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli validate
```

Linux/HPC 远程终端一键提取：

```bash
export PYTHONPATH=src
python -m rst2csv.cli hpc-run Void.112.510
```

HPC 详细步骤见：

```text
Result/Linux_HPC终端自动提取操作手册.md
```

输出文件位于：

```text
GeneratedExact/<case>/FaceAccel_A.CSV
...
GeneratedExact/<case>/FaceAccel_G.CSV
```

## 新工况手动准备方法

用户平时常见的顶层 `<case>.dat` 只是求解输入文件，不包含 Workbench 探针缓存，不能单独用于精确导出。精确导出还需要同名 Workbench 工程目录 `<case>_files` 里的三个文件。

以 `Void.85.210` 为例，如果工程在：

```text
E:\WCL\AnsysTunnel\Void.85.210.wbpj
```

对应工程目录通常是：

```text
E:\WCL\AnsysTunnel\Void.85.210_files\
```

需要复制这三个文件到工作区：

| 需要的文件 | Workbench 工程中的来源 | 复制到工作区 |
|---|---|---|
| `SYS.mechdb` | `<case>_files\dp0\global\MECH\SYS.mechdb` | `Backup\Workbench\<case>\SYS.mechdb` |
| `ds.dat` | `<case>_files\dp0\SYS\MECH\ds.dat` | `Backup\Workbench\<case>\ds.dat` |
| `CAERep.xml` | `<case>_files\dp0\SYS\MECH\CAERep.xml` | `Backup\Workbench\<case>\CAERep.xml` |

其中 `SYS.mechdb` 是精确导出的必需文件；`ds.dat` 和 `CAERep.xml` 用于留档、核查和后续排查。

单个工况复制示例：

```powershell
$case = "Void.85.210"
$projectRoot = "E:\WCL\AnsysTunnel"
$backupRoot = "D:\Developing_WCL\RST2CSV\Backup\Workbench"

New-Item -ItemType Directory -Force -Path "$backupRoot\$case" | Out-Null
Copy-Item -LiteralPath "$projectRoot\${case}_files\dp0\global\MECH\SYS.mechdb" -Destination "$backupRoot\$case\SYS.mechdb" -Force
Copy-Item -LiteralPath "$projectRoot\${case}_files\dp0\SYS\MECH\ds.dat" -Destination "$backupRoot\$case\ds.dat" -Force
Copy-Item -LiteralPath "$projectRoot\${case}_files\dp0\SYS\MECH\CAERep.xml" -Destination "$backupRoot\$case\CAERep.xml" -Force
```

如果 `SYS.mechdb` 缺失或导出值不是最新结果，请在 Workbench 中打开对应 `.wbpj`，进入 Mechanical，确认 Solution/Result Probe 已经评估完成并保存工程，然后再复制。

## RST 文件放置

大型 `.rst` 不需要复制到工作区。默认只读位置是：

```text
E:/WCL/AnsysTunnel/RSTVoidBatch/<case>.rst
```

如果 RST 目录变化，修改：

```text
src/rst2csv/config.py
```

或在命令中临时指定：

```powershell
python -m rst2csv.cli run --rst-root E:\Other\RSTFolder
```

## 新工况完整流程

1. 确认 RST 存在：

```text
E:/WCL/AnsysTunnel/RSTVoidBatch/<case>.rst
```

2. 从 Workbench `<case>_files` 目录复制 `SYS.mechdb`、`ds.dat`、`CAERep.xml` 到：

```text
Backup/Workbench/<case>/
```

3. 如果要验证新工况，也把人工导出的参考 CSV 放到：

```text
Backup/OriginData/<case>/
```

4. 运行：

```powershell
$env:PYTHONPATH='src'
python -m rst2csv.cli export <case>
```

5. 若有参考 CSV，运行：

```powershell
python -m rst2csv.cli validate <case>
```

## 当前验证结论

三组已有工况已验证：

- `Void.13.375`
- `Void.85.210`
- `Void.175.575`

结果：

- 结构全部一致；
- 700 个加速度探针列最大误差为 `1e-05`；
- 探针列 RMSE 均小于 `3e-07`。
