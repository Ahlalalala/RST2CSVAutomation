# Linux/HPC 端 RST2CSV 自动提取设计

## 目标

让用户在远程 HPC 的 Linux 终端中，针对一个工况名直接运行命令，自动完成：

1. 定位 `.rst`；
2. 定位 Workbench 工程目录中的 `SYS.mechdb`、`ds.dat`、`CAERep.xml`；
3. 导出 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`；
4. 在 `CSVResult/<case>/` 中保存 CSV；
5. 额外生成 `CSVResult/<case>.zip`，便于只下载一个压缩包。

## 目录约定

以 `Void.112.510` 为例：

```text
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/
├── Void.112.510.dat
├── TaskDir_Void.112.510/
│   └── Void.112.510.rst
├── RST2CSVFiles/
│   └── Void.112.510_files/
│       └── dp0/
│           ├── global/MECH/SYS.mechdb
│           └── SYS/MECH/ds.dat
│           └── SYS/MECH/CAERep.xml
└── CSVResult/
    ├── Void.112.510/
    │   ├── FaceAccel_A.CSV
    │   └── ...
    └── Void.112.510.zip
```

## 命令设计

新增 Linux/HPC 一键命令：

```bash
python -m rst2csv.cli hpc-run Void.112.510
```

默认基础目录：

```text
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

也允许用户临时指定基础目录，用于本地测试或 HPC 路径变化：

```bash
python -m rst2csv.cli hpc-run Void.112.510 --base-dir /path/to/Desktop
```

## 架构

新增 `src/rst2csv/hpc_paths.py`，负责：

- 根据基础目录和工况名推导 `.rst`、`SYS.mechdb`、`ds.dat`、`CAERep.xml`；
- 创建 `CSVResult/<case>/`；
- 生成 `CSVResult/<case>.zip`；
- 在执行前检查必需文件是否存在。

现有 `mechdb_cache.py`、`rst_reader.py`、`csv_format.py` 不改变核心算法。`cli.py` 只新增 `hpc-run`，调用新的路径解析模块和已有精确导出函数。

## 错误处理

如果缺少必需文件，命令应明确指出缺失路径，例如：

```text
ERROR: missing file: /.../RST2CSVFiles/Void.112.510_files/dp0/global/MECH/SYS.mechdb
```

如果 `CSVResult/<case>.zip` 已存在，重新运行时覆盖压缩包。

## 测试策略

单元测试覆盖：

- HPC 路径推导；
- 缺失文件检查；
- zip 打包时只包含 `FaceAccel_*.CSV`，且压缩包顶层目录名为工况名；
- CLI `hpc-run` 默认基础目录和可覆盖基础目录。

本地模拟验证：

- 用临时目录构造 `TaskDir_<case>`、`RST2CSVFiles/<case>_files` 和 `CSVResult`；
- 由于真实 `.rst`/`.mechdb` 较大，单元测试不读取真实文件，只验证路径和打包行为；
- 真实数据验证仍用已有三工况 Windows/本地路径运行 `python -m rst2csv.cli run`，确认原工作流未被破坏。
