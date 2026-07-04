# Linux/HPC 终端自动提取操作手册

本手册是 HPC 上运行 RST2CSV 的总入口。当前有两个命令：

```bash
python -m rst2csv.cli mechanical-hpc-run <case>
python -m rst2csv.cli hpc-run <case>
```

选择规则：

- fresh 工程，也就是 `<case>_files` 中没有已生成结果、`SYS.mechdb` 里还没有探针历史缓存时，必须使用 `mechanical-hpc-run`。
- 已经手工导入 RST 并保存过 Workbench 结果缓存的旧工程，才可以使用 `hpc-run`。

后续批量脱空工况应使用 `mechanical-hpc-run`。详细步骤见：

```text
Result/无缓存RST自动提取CSV工作流手册.md
```

## 1. 基础目录

默认基础路径：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

以 `Void.112.510` 为例，应准备：

```text
Desktop/
|-- Void.112.510.dat
|-- TaskDir_Void.112.510/
|   `-- Void.112.510.rst
|-- RST2CSVFiles/
|   |-- Void.112.510.wbpj
|   `-- Void.112.510_files/
|       `-- dp0/
|           |-- global/MECH/SYS.mechdb
|           `-- SYS/MECH/
|               |-- ds.dat
|               `-- CAERep.xml
`-- RST2CSVAutomation/
    |-- src/
    |-- scripts/
    `-- ...
```

源码压缩包解压后，应让 `src/` 和 `scripts/` 直接位于：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

## 2. 环境

服务人员已配置的 Python 3.10 Slurm 环境可参考：

```bash
source /opt/phadcloud/lustre/software/conda/miniforge/etc/profile.d/conda.sh
conda activate py310
```

Ansys 2025R2 环境可参考：

```bash
source /home/software/intel/oneapi/2022.1/setvars.sh
source /home/software/ansys/2025R2/setenv.sh
```

Workbench batch 启动器默认写为：

```bash
/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2
```

如路径不同，先查找：

```bash
find /home/software/ansys/2025R2 -name runwb2 2>/dev/null
```

## 3. 推荐提交方式

进入源码目录：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

复制模板：

```bash
cp scripts/rst2csv_mechanical.slurm python1.slurm
```

检查 `python1.slurm` 顶部配置，重点是：

```bash
BASE_DIR="/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop"
SOURCE_DIR="${BASE_DIR}/RST2CSVAutomation"
CONDA_ENV="py310"
RUNWB2_PATH="${RST2CSV_RUNWB2:-/home/software/ansys/2025R2/ansys_inc/v252/Framework/bin/Linux64/runwb2}"
```

提交 fresh 工程自动提取：

```bash
sbatch python1.slurm Void.112.510
```

输出目录：

```text
CSVResult/Void.112.510/FaceAccel_A.CSV
...
CSVResult/Void.112.510/FaceAccel_G.CSV
CSVResult/Void.112.510.zip
```

下载时选择：

```text
CSVResult/Void.112.510.zip
```

## 4. 常见错误

### cached histories missing probes

说明使用了旧的缓存读取命令 `hpc-run`，但当前工程没有缓存。fresh 工程改用：

```bash
python -m rst2csv.cli mechanical-hpc-run Void.112.510
```

### Python3 is disabled on login nodes

不要在登录节点创建 venv 或直接运行 Python 计算任务。使用 Slurm 提交，让脚本在计算节点中激活 `py310`。

### 找不到 runwb2

检查 `RUNWB2_PATH` 是否正确。也可临时设置：

```bash
export RST2CSV_RUNWB2=/实际路径/runwb2
```

### Cannot open X display

错误形如：

```text
Cannot open X display "(not specified)".
Fatal error: Unable to start the Mechanical editor.
```

说明计算节点没有图形显示环境。Mechanical batch 仍需要 X display。新版 `scripts/rst2csv_mechanical.slurm` 会自动查找并启动 `Xvfb` 虚拟显示。

如果仍然报错，先检查：

```bash
which Xvfb
```

如果没有输出，需要联系 HPC 服务人员安装或加载 `Xvfb`。也可以在脚本顶部手动指定：

```bash
XVFB_BIN="/usr/bin/Xvfb"
```

### 状态文件报错

查看：

```text
CSVResult/<case>/_mechanical_batch/mechanical_status.txt
CSVResult/<case>/_mechanical_batch/workbench_stdout.log
CSVResult/<case>/_mechanical_batch/workbench_stderr.log
```

## 5. 已验证结论

本机 Workbench 2025R2 已使用 `Void.85.210` 从 0 缓存 fresh 工程完成端到端验证，生成的 7 个 CSV 与 `OriginData/Void.85.210/FaceAccel_*.CSV` 逐字节一致，验证器误差全部为 0。
