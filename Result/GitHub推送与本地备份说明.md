# GitHub 推送与本地备份说明

## 1. 本次分支

本地仓库已创建并完成 Linux/HPC 迁移工作，当前开发分支为：

```bash
codex/linux-hpc-workflow
```

本地 Git 身份已设置为：

```bash
user.name=1438618299
user.email=1438618299@qq.com
```

## 2. 远端推送情况

目标远端仓库为：

```bash
https://github.com/Ahlalalala/RST2CSVAutomation.git
```

已经执行：

```bash
git remote add origin https://github.com/Ahlalalala/RST2CSVAutomation.git
git push -u origin codex/linux-hpc-workflow
```

但当前环境访问 GitHub HTTPS 时连接被重置，报错为：

```text
fatal: unable to access 'https://github.com/Ahlalalala/RST2CSVAutomation.git/': Recv failure: Connection was reset
```

随后用 `git ls-remote` 探测远端以及用 `http.version=HTTP/1.1` 重试推送，仍为同样的连接重置错误。本机也未安装 `gh` 命令，因此无法使用 GitHub CLI 作为兜底推送方式。

## 3. 本地备份

由于远端推送未成功，已在工作目录下生成本地备份目录：

```bash
LocalBackup/
```

其中建议保留两个文件：

```text
RST2CSVAutomation_codex-linux-hpc-workflow.bundle
RST2CSVAutomation_codex-linux-hpc-workflow_source.zip
```

`bundle` 文件包含完整 Git 历史和分支，可在另一台能访问 GitHub 的机器上恢复仓库并继续推送；`source.zip` 是当前提交的源码快照，便于直接上传或查看。

## 4. 在另一台机器恢复并推送

如果使用 `bundle` 恢复：

```bash
git clone RST2CSVAutomation_codex-linux-hpc-workflow.bundle RST2CSVAutomation
cd RST2CSVAutomation
git checkout codex/linux-hpc-workflow
git remote add origin https://github.com/Ahlalalala/RST2CSVAutomation.git
git push -u origin codex/linux-hpc-workflow
```

如果远端已经存在 `origin`，则改用：

```bash
git remote set-url origin https://github.com/Ahlalalala/RST2CSVAutomation.git
git push -u origin codex/linux-hpc-workflow
```

## 5. 本次验证

已经完成以下验证：

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
python -m rst2csv.cli run Void.85.210
python -m rst2csv.cli hpc-run Void.85.210 --base-dir <临时HPC模拟目录>
```

验证结果：

- 单元测试共 22 项，全部通过；
- `Void.85.210` 本地精确工作流导出 7 个 `FaceAccel_*.CSV`，并通过已有目标 CSV 校验；
- HPC 模拟目录工作流成功生成 7 个 CSV，并生成包含 7 个 CSV 的同名 zip 压缩包；
- 临时 HPC 模拟目录已在验证后删除。
