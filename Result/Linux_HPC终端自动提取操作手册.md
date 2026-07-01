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

进入基础路径：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop
```

如果代码已经上传到 `RST2CSVAutomation/`，进入代码目录：

```bash
cd RST2CSVAutomation
```

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

## 4. 单个工况自动提取

以 `Void.112.510` 为例：

```bash
cd /opt/phadcloud/lustre/home/phadcloud01z417972/Desktop/RST2CSVAutomation
source .venv/bin/activate
export PYTHONPATH=src
python -m rst2csv.cli hpc-run Void.112.510
```

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
