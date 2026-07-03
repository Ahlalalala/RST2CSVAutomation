# Linux/HPC 终端自动提取操作手册

## 1. 适用场景

本手册用于在远程 HPC 的 Linux 终端中，把 ANSYS/Workbench 工况结果自动导出为：

```text
FaceAccel_A.CSV
FaceAccel_B.CSV
FaceAccel_C.CSV
FaceAccel_D.CSV
FaceAccel_E.CSV
FaceAccel_F.CSV
FaceAccel_G.CSV
```

并额外生成一个同名 zip 压缩包，便于在网页或文件管理器中只下载一个文件。

## 2. 目录约定

HPC 基础路径固定为：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

下面以工况 `Void.112.510` 为例。

### 2.1 基础路径中的文件

基础路径下通常有输入 `.dat`：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/Void.112.510.dat
```

注意：这个 `.dat` 只是求解输入文件，不能替代 `SYS.mechdb`。精确导出必须使用 Workbench/Mechanical 工程中的 `SYS.mechdb`。

### 2.2 RST 结果文件

RST 应放在：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/TaskDir_Void.112.510/Void.112.510.rst
```

### 2.3 Workbench 工程文件

把包含 `dp0` 的 Workbench 工程目录上传到基础路径下的 `RST2CSV/`：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/
```

程序会自动读取：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/global/MECH/SYS.mechdb
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/SYS/MECH/ds.dat
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/SYS/MECH/CAERep.xml
```

其中：

- `SYS.mechdb`：精确导出必需，保存 Mechanical 已缓存的 Result Probe 曲线；
- `ds.dat`：留档和核查用；
- `CAERep.xml`：留档和核查用。

## 3. 首次部署

### 3.1 上传并解压源码

进入基础路径：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

如果使用本地备份中的源码压缩包：

```text
RST2CSVAutomation_codex-linux-hpc-workflow_source.zip
```

应把这个压缩包的内容解压到基础路径下的 `RST2CSVAutomation/` 目录中。推荐命令为：

```bash
mkdir -p RST2CSVAutomation
unzip RST2CSVAutomation_codex-linux-hpc-workflow_source.zip -d RST2CSVAutomation
cd RST2CSVAutomation
```

解压后，`RST2CSVAutomation/` 里面应直接能看到：

```text
pyproject.toml
src/
scripts/
Result/
```

也就是说，代码目录应是：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
```

不要形成下面这种多套一层的目录：

```text
RST2CSVAutomation/RST2CSVAutomation_codex-linux-hpc-workflow_source/pyproject.toml
```

如果已经多套了一层，就进入内层目录运行命令，或把内层文件移动到 `RST2CSVAutomation/` 下。

如果代码已经通过 Git 或其他方式上传到 `RST2CSVAutomation/`，进入代码目录即可：

```bash
cd RST2CSVAutomation
```

### 3.2 登录节点禁用 Python 时怎么办

如果创建虚拟环境时提示：

```text
Python3 is disabled on login nodes -m venv .venv
```

意思是 HPC 不允许在登录节点运行 Python。此时不要在登录节点继续执行 `python3 -m venv .venv`，需要先进入计算节点，或把初始化和提取命令写成作业提交到计算节点。

如果平台支持交互计算节点，先申请一个交互 shell。不同 HPC 的命令可能不同，常见 Slurm 示例为：

```bash
srun --pty -N 1 -n 1 --mem=8G -t 02:00:00 bash
```

有些平台使用：

```bash
salloc -N 1 -n 1 --mem=8G -t 02:00:00
```

或需要在网页端/平台端点击“交互式作业”“终端”“计算节点 Shell”。进入计算节点后，再执行后面的虚拟环境创建和运行命令。

如果平台不提供交互计算节点，则把命令写成作业脚本提交。以 Slurm 为例，可创建：

```bash
cat > run_rst2csv.sh <<'EOF'
#!/bin/bash
#SBATCH -J rst2csv
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --mem=8G
#SBATCH -t 02:00:00

cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation

# 如果平台使用 module 管理 Python，可按实际版本修改或取消下一行注释。
# module load python/3.10

if [ ! -d .venv ]; then
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install ansys-mapdl-reader h5py
else
  source .venv/bin/activate
fi

export PYTHONPATH=src
python -m rst2csv.cli check
python -m rst2csv.cli hpc-run Void.112.510
EOF
```

然后提交：

```bash
sbatch run_rst2csv.sh
```

如果 HPC 不是 Slurm，请把 `#SBATCH` 和 `sbatch` 换成平台对应的作业系统命令。关键原则不变：Python 环境创建、依赖安装和 CSV 提取都要在允许运行 Python 的计算节点上完成。

### 3.3 创建 Python 环境并安装依赖

建议创建 Python 虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
python -m pip install ansys-mapdl-reader h5py
```

检查依赖：

```bash
export PYTHONPATH=src
python -m rst2csv.cli check
```

看到下面两行即可：

```text
ansys-mapdl-reader: available
h5py: available
```

如果计算节点需要先加载 Python 模块，可在创建虚拟环境前执行类似命令：

```bash
module avail python
module load python/3.10
```

具体模块名称以 HPC 平台显示结果为准。

## 4. 单个工况自动提取

以 `Void.112.510` 为例：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
source .venv/bin/activate
export PYTHONPATH=src
python -m rst2csv.cli hpc-run Void.112.510
```

如果登录节点禁用 Python，这几行也应在计算节点交互 shell 中执行，或放入作业脚本中提交执行。

程序会自动：

1. 读取 `/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/TaskDir_Void.112.510/Void.112.510.rst`；
2. 读取 `/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/global/MECH/SYS.mechdb`；
3. 创建输出目录；
4. 写出 7 个 CSV；
5. 创建 zip 压缩包。

## 5. 输出位置

CSV 输出目录：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/CSVResult/Void.112.510/
```

其中包含：

```bash
FaceAccel_A.CSV
FaceAccel_B.CSV
FaceAccel_C.CSV
FaceAccel_D.CSV
FaceAccel_E.CSV
FaceAccel_F.CSV
FaceAccel_G.CSV
```

压缩包位置：

```bash
/opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/CSVResult/Void.112.510.zip
```

下载时优先下载这个 zip。

## 6. 路径不是默认值时

如果基础路径不是默认路径，可以显式指定：

```bash
python -m rst2csv.cli hpc-run Void.112.510 --base-dir /your/base/Desktop
```

## 7. 常见错误

### 7.1 提示缺少 `.rst`

错误示例：

```text
ERROR: missing file: /.../TaskDir_Void.112.510/Void.112.510.rst
```

检查：

```bash
ls /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/TaskDir_Void.112.510/
```

确认里面有：

```text
Void.112.510.rst
```

### 7.2 提示缺少 `SYS.mechdb`

错误示例：

```text
ERROR: missing file: /.../RST2CSV/Void.112.510_files/dp0/global/MECH/SYS.mechdb
```

说明上传的 Workbench 工程目录不完整，或目录层级放错。应检查：

```bash
ls /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/global/MECH/
```

必须能看到：

```text
SYS.mechdb
```

如果没有，需要从本地 Workbench 工程目录重新上传完整的 `Void.112.510_files`。

### 7.3 提示缺少 `ds.dat` 或 `CAERep.xml`

这两个文件位于：

```bash
Void.112.510_files/dp0/SYS/MECH/
```

检查：

```bash
ls /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSV/Void.112.510_files/dp0/SYS/MECH/
```

必须能看到：

```text
ds.dat
CAERep.xml
```

### 7.4 依赖导入失败

如果 `check` 显示缺少依赖，重新安装：

```bash
python -m pip install ansys-mapdl-reader h5py
```

如果 HPC 不能联网，需要提前在有网络的机器下载 whl 包，再上传到 HPC 安装。

如果在登录节点执行安装命令时出现 `Python3 is disabled on login nodes`，说明命令位置不对。应先进入计算节点，或把安装命令放到作业脚本中运行。

### 7.5 输出 zip 没有生成

确认命令完整运行，没有中途报错。也可以检查输出目录：

```bash
ls /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/CSVResult/
```

应能看到：

```text
Void.112.510
Void.112.510.zip
```

## 8. 批量运行建议

多个工况可以用 shell 循环：

```bash
for case in Void.112.510 Void.85.210 Void.175.575
do
  python -m rst2csv.cli hpc-run "$case"
done
```

每个工况都会生成自己的 CSV 文件夹和 zip 压缩包。
