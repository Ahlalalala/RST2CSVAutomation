# 无缓存 RST 自动提取 CSV 工作流手册

本手册对应 fresh Workbench 工程的自动提取命令：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510
```

这里的 fresh 工程指 `<case>_files` 中已经删除求解后生成结果，`SYS.mechdb` 里还没有 `Face_Accel_Probe_*` 历史缓存。旧命令 `hpc-run` 只能读取已经缓存好的 `SYS.mechdb`，遇到 fresh 工程会报：

```text
ERROR: cached histories missing probes for Face A: [1, 2, 3, 4, 5]
```

新的 `mechanical-hpc-run` 会自动调用 Workbench/Mechanical：打开 `.wbpj`，把 `TaskDir_<case>/<case>.rst` 挂到 Mechanical 分析工作目录，评价 700 个已有探针并保存工程。保存后的 `SYS.mechdb` 会产生与手工导出同源的高精度历史缓存，Python 再读取该缓存生成 `FaceAccel_A.CSV` 到 `FaceAccel_G.CSV`，最后打包为 `<case>.zip`。

## 1. 目录放置

以 `Void.112.510` 为例，基础路径为：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

目录应为：

```text
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/
|-- Void.112.510.dat
|-- TaskDir_Void.112.510/
|   `-- Void.112.510.rst
|-- RST2CSVFiles/
|   |-- Void.112.510.wbpj
|   `-- Void.112.510_files/
|       `-- dp0/
|           |-- global/MECH/SYS.mechdb
|           `-- SYS/MECH/
|               |-- CAERep.xml
|               `-- ds.dat
`-- RST2CSVAutomation/
    |-- src/
    |-- scripts/
    |-- tests/
    `-- ...
```

源码压缩包 `RST2CSVAutomation_codex-linux-hpc-workflow_source.zip` 解压后，应把压缩包里的内容放到：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

判断是否放对：执行下面命令后，应该能看到 `src`、`scripts`、`tests` 等目录直接位于 `RST2CSVAutomation` 下。

```bash
ls /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

不要形成 `RST2CSVAutomation/RST2CSVAutomation/src` 这种双层目录。

## 2. 三个关键文件如何确定

用户通常只接触 `.dat`，但本流程还需要 Workbench 工程中的三个小文件：

```text
dp0/global/MECH/SYS.mechdb
dp0/SYS/MECH/ds.dat
dp0/SYS/MECH/CAERep.xml
```

如果 `<case>_files` 已经删除多余分析模块，三者应当唯一。若不唯一，优先按以下顺序确认：

1. 使用与待提取 `.dat` 同名的 `<case>.wbpj` 旁边的 `<case>_files`。
2. 选择同一个设计点，默认是 `dp0`。
3. 选择同一个系统，默认是 `SYS`。
4. 在仍然不唯一时，选择更新时间最新且路径位于 `dp0/global/MECH` 或 `dp0/SYS/MECH` 的文件。

检查命令：

```bash
BASE=/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
CASE=Void.112.510

find "$BASE/RST2CSVFiles/${CASE}_files" -name SYS.mechdb -o -name ds.dat -o -name CAERep.xml
```

## 3. 环境要求

Python 侧需要：

```text
python 3.10
h5py
ansys-mapdl-reader
```

如果登录节点提示：

```text
Python3 is disabled on login nodes -m venv .venv
```

不要在登录节点创建虚拟环境。应使用服务人员配置好的 Slurm 环境，在计算节点中运行。当前已知可用环境为：

```bash
source /opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh
conda activate py310
```

Workbench/Mechanical 侧需要 Ansys 2025R2。已知 HPC 求解脚本使用：

```bash
source /home/software/intel/oneapi/2022.1/setvars.sh
source /home/software/ansys/2025R2/setenv.sh
```

本工作流需要的是 Workbench batch 启动器 `runwb2`，默认路径写为：

```bash
/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2
```

如果实际路径不同，用下面命令查找后修改 Slurm 脚本顶部的 `RUNWB2_PATH`：

```bash
find /home/software/ansys/2025R2 -name runwb2 2>/dev/null
```

本机 Windows 验证使用的 Workbench 路径是：

```text
D:\Program Files\ANSYS Inc R2\v252\Framework\bin\Win64\RunWB2.exe
```

## 4. 依赖安装

如果计算节点可以联网：

```bash
python -m pip install h5py ansys-mapdl-reader
```

如果不能联网，可以在本机或可联网 Linux 机器下载 wheel，再上传到 HPC 指定目录，例如：

```bash
mkdir -p /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVDeps
```

安装时使用：

```bash
python -m pip install --no-index \
  --find-links /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVDeps \
  h5py ansys-mapdl-reader
```

检查：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
export PYTHONPATH=src
python -m rst2csv.cli check
```

## 5. 推荐 Slurm 用法

复制模板：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
cp scripts/rst2csv_mechanical.slurm python1.slurm
```

只需集中检查 `python1.slurm` 文件开头这些配置：

```bash
BASE_DIR="/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop"
SOURCE_DIR="${BASE_DIR}/RST2CSVAutomation"
CONDA_SH="/opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh"
CONDA_ENV="py310"
INTEL_SETVARS="/home/software/intel/oneapi/2022.1/setvars.sh"
ANSYS_SETENV="/home/software/ansys/2025R2/setenv.sh"
RUNWB2_PATH="${RST2CSV_RUNWB2:-/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2}"
MECHANICAL_TIMEOUT_SECONDS="86400"
```

提交：

```bash
sbatch python1.slurm Void.112.510
```

如果单个工况很慢，可把 `MECHANICAL_TIMEOUT_SECONDS` 调大，例如 172800 表示 48 小时。

## 6. dry-run 检查

dry-run 只生成 Workbench journal 和 Mechanical 脚本，不真正运行 Workbench，也不会读取巨大 RST：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
export PYTHONPATH=src
python -m rst2csv.cli mechanical-hpc-run Void.112.510 \
  --base-dir /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop \
  --runwb2 /home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2 \
  --dry-run
```

成功后会生成：

```text
CSVResult/Void.112.510/_mechanical_batch/run_workbench.wbjn
CSVResult/Void.112.510/_mechanical_batch/export_probes_mechanical.py
```

## 7. 正式输出

正式运行成功后：

```text
CSVResult/
|-- Void.112.510/
|   |-- FaceAccel_A.CSV
|   |-- FaceAccel_B.CSV
|   |-- FaceAccel_C.CSV
|   |-- FaceAccel_D.CSV
|   |-- FaceAccel_E.CSV
|   |-- FaceAccel_F.CSV
|   `-- FaceAccel_G.CSV
`-- Void.112.510.zip
```

下载时直接选择：

```text
CSVResult/Void.112.510.zip
```

压缩包内部会保留一层 `Void.112.510/` 文件夹，便于区分不同工况。

## 8. 常见错误

### cached histories missing probes

说明使用了旧命令 `hpc-run`，或 Mechanical 没有成功评价并保存 fresh 工程。fresh 工程必须使用：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510
```

### 找不到 runwb2

检查 `RUNWB2_PATH` 是否正确：

```bash
ls -lh /home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2
```

也可以临时指定：

```bash
export RST2CSV_RUNWB2=/实际路径/runwb2
```

### Result link was not created

脚本会尝试把：

```text
TaskDir_<case>/<case>.rst
```

软链接为 Mechanical 工作目录下的：

```text
RST2CSVFiles/<case>_files/dp0/SYS/MECH/file.rst
```

Linux 上通常由 `ln -s` 完成。如果报 `Result link was not created`，检查目标目录权限、RST 路径是否存在，以及 `file.rst` 是否已被旧文件占用。

### Workbench 找不到 Model

默认组件名是 `Model`。如果工程单元名称不同，可试：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510 --component Setup
```

### 状态和日志在哪里

```text
CSVResult/<case>/_mechanical_batch/mechanical_status.txt
CSVResult/<case>/_mechanical_batch/workbench_stdout.log
CSVResult/<case>/_mechanical_batch/workbench_stderr.log
```

如果 `mechanical_status.txt` 第一行是 `OK`，说明 Workbench 已完成缓存生成；如果第一行是 `ERROR`，后面会有 Mechanical Python 的详细错误堆栈。

## 9. 精度说明

不要使用 Mechanical 的 `SequenceTotalVector(i)` 或文本导出作为最终数据源；该接口返回的是显示精度，可能把 `2.873846761e-05` 显示为 `2.9e-05`。本工作流只让 Mechanical 生成高精度 `SYS.mechdb` 缓存，然后由 Python 读取缓存中的 double 数组并按 Workbench CSV 格式写出。

本机验证中，`Void.85.210` 的第 1 个探针第 40 行缓存值为：

```text
2.8738467613742973e-05
```

格式化后对应手工 CSV 中的：

```text
2.87E-05
```

因此最终 CSV 的精度与已验证的缓存精确工作流一致，而不是低精度文本导出。

## 10. 已完成的本机验证

已在本机 Workbench 2025R2 上用 `Void.85.210` 做端到端验证：

1. 从 `OriginData/RST2CSVFiles/Void.85.210_files` 复制 fresh 工程到隔离目录。
2. 验证初始 `SYS.mechdb` 中探针历史数为 0。
3. 运行 `mechanical-hpc-run`，由 Workbench 自动挂载 RST、评价 700 个探针并保存缓存。
4. 自动生成 7 个 CSV 和 `Void.85.210.zip`。
5. 与 `OriginData/Void.85.210/FaceAccel_*.CSV` 逐字节比对。

结果：`FaceAccel_A.CSV` 到 `FaceAccel_G.CSV` 全部逐字节一致，验证器显示 `probe_max_abs_error=0`、`all_max_abs_error=0`。

详细记录见：

```text
Result/无缓存RST自动提取CSV验证报告.md
```
