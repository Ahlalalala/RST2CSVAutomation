# 无缓存 RST 自动提取 CSV 工作流手册

本手册对应新命令：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510
```

它不再读取已经导入 Workbench 后才会产生的 probe 历史缓存，也不再使用纯 RST 节点近似算法。新流程会在 HPC 终端中调用 Workbench/Mechanical batch：自动打开 fresh 工程、挂接 RST、让 Mechanical 自己评估原有 700 个 `Face_Accel_Probe_*`，再聚合为 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV` 并打包。

## 1. 为什么旧错误会出现

旧命令 `hpc-run` 读取的是 `SYS.mechdb` 里已经缓存好的 Workbench probe 历史。fresh 的 `<case>_files` 删除了已生成结果，因此 `SYS.mechdb` 中没有这些历史，报错：

```text
ERROR: cached histories missing probes for Face A: [1, 2, 3, 4, 5]
```

这不是 `dp0/global/MECH/SYS.mechdb`、`dp0/SYS/MECH/ds.dat`、`dp0/SYS/MECH/CAERep.xml` 选错了，而是使用了旧缓存流程。fresh 工程必须使用 `mechanical-hpc-run`。

## 2. HPC 文件目录

以 `Void.112.510` 为例，基础路径固定为：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

需要放置：

```text
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/
├── Void.112.510.dat
├── TaskDir_Void.112.510/
│   └── Void.112.510.rst
├── RST2CSVFiles/
│   ├── Void.112.510.wbpj
│   └── Void.112.510_files/
│       └── dp0/
│           ├── global/MECH/SYS.mechdb
│           └── SYS/MECH/
│               ├── CAERep.xml
│               └── ds.dat
└── RST2CSVAutomation/
    ├── src/
    ├── scripts/
    └── ...
```

源码压缩包 `RST2CSVAutomation_codex-linux-hpc-workflow_source.zip` 解压后，应该让 `src/`、`scripts/`、`tests/` 等目录直接位于：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

不要解成 `RST2CSVAutomation/RST2CSVAutomation/src` 这种双层目录。

## 3. 环境要求

Python 侧仍需 `ansys-mapdl-reader` 用于读取 RST 的时间步信息：

```bash
python -m pip install ansys-mapdl-reader
```

如果计算节点不能联网，把依赖 wheel 上传到某个目录后离线安装：

```bash
python -m pip install --no-index --find-links /path/to/wheels ansys-mapdl-reader
```

精确导出侧必须能调用 Workbench/Mechanical 的 batch 启动器 `runwb2`。如果命令行找不到它，请联系 HPC 服务人员提供 Ansys Workbench/Mechanical 模块，并确认实际路径，例如：

```bash
find /opt -name runwb2 2>/dev/null
```

找到后设置：

```bash
export RST2CSV_RUNWB2=/path/to/runwb2
```

## 4. 推荐 Slurm 用法

可以直接使用仓库中的模板：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
cp scripts/rst2csv_mechanical.slurm python1.slurm
```

打开 `python1.slurm`，只在文件开头集中修改这些配置：

```bash
BASE_DIR="/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop"
SOURCE_DIR="${BASE_DIR}/RST2CSVAutomation"
CONDA_SH="/opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh"
CONDA_ENV="py310"
RUNWB2_PATH="${RST2CSV_RUNWB2:-}"
```

如果 `runwb2` 没有加入环境变量，把最后一行改成实际路径，例如：

```bash
RUNWB2_PATH="/opt/ansys_inc/v252/Framework/bin/Linux64/runwb2"
```

提交：

```bash
sbatch python1.slurm Void.112.510
```

不要在登录节点直接执行 `python -m venv`。该集群提示 `Python3 is disabled on login nodes` 时，说明 Python 任务应通过 Slurm 在计算节点运行。

## 5. 先做 dry-run 检查

提交正式任务前，可以在计算节点或允许 Python 的交互节点上检查路径并生成 batch 脚本：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
export PYTHONPATH=src
python -m rst2csv.cli mechanical-hpc-run Void.112.510 \
  --base-dir /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop \
  --dry-run
```

成功后会在：

```text
CSVResult/Void.112.510/_mechanical_batch/
```

生成：

```text
run_workbench.wbjn
export_probes_mechanical.py
```

这一步不会运行 Workbench，也不会读取巨大 RST。

## 6. 输出文件

正式运行成功后输出：

```text
CSVResult/
├── Void.112.510/
│   ├── FaceAccel_A.CSV
│   ├── FaceAccel_B.CSV
│   ├── FaceAccel_C.CSV
│   ├── FaceAccel_D.CSV
│   ├── FaceAccel_E.CSV
│   ├── FaceAccel_F.CSV
│   └── FaceAccel_G.CSV
└── Void.112.510.zip
```

下载时选择：

```text
CSVResult/Void.112.510.zip
```

## 7. 常见问题

如果仍然出现 `cached histories missing probes`，说明运行的是旧命令 `hpc-run`。fresh 工程必须运行：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510
```

如果提示找不到 `runwb2`，设置：

```bash
export RST2CSV_RUNWB2=/path/to/runwb2
```

或在 `python1.slurm` 顶部填写 `RUNWB2_PATH`。

如果 Mechanical 状态文件报错，查看：

```text
CSVResult/<case>/_mechanical_batch/mechanical_status.txt
CSVResult/<case>/_mechanical_batch/workbench_stdout.log
CSVResult/<case>/_mechanical_batch/workbench_stderr.log
```

如果 Workbench journal 提示找不到 `Model` cell，可以临时改用：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510 --component Setup
```

但常规 Mechanical 工程应优先使用默认的 `Model`。

如果 `dp0/SYS/MECH/file.rst` 已存在且是旧结果，请先备份或删除。新脚本会优先使用已有 `file.rst`，没有时才尝试把 `TaskDir_<case>/<case>.rst` 软链接过去。

## 8. 仍保留的旧命令

`hpc-run` 只适用于已经手动导入并缓存 probe 历史的 Workbench 工程，用于回归验证或旧数据复现。后续真实批量 fresh 工况不要使用它。

## 9. 当前验证情况

本地没有安装 Workbench/Mechanical，因此无法直接实跑 `runwb2`。已经完成的验证包括：

```text
python -m unittest discover -s tests -v
```

结果：30 个单元测试全部通过。

同时用 `Void.85.210` 的已有缓存历史模拟 Mechanical 单探针文本导出，再走新 parser/聚合器生成 CSV，与 `OriginData/Void.85.210` 对比：

```text
FaceAccel_A.CSV  probe_max_abs_error=1e-05  probe_rmse=2.70569e-07
FaceAccel_B.CSV  probe_max_abs_error=1e-05  probe_rmse=2.27132e-07
FaceAccel_C.CSV  probe_max_abs_error=1e-05  probe_rmse=2.1329e-07
FaceAccel_D.CSV  probe_max_abs_error=1e-05  probe_rmse=1.70314e-07
FaceAccel_E.CSV  probe_max_abs_error=1e-05  probe_rmse=1.76287e-07
FaceAccel_F.CSV  probe_max_abs_error=1e-05  probe_rmse=1.43937e-07
FaceAccel_G.CSV  probe_max_abs_error=1e-05  probe_rmse=1.29115e-07
```

也就是说，Mechanical 成功导出 700 个单探针文本后，Python 后处理不会引入额外精度损失。最终端到端精度需要在 HPC 上完成一次 `mechanical-hpc-run` 后再与手动导出 CSV 对比确认。
