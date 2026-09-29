# 在新电脑上安装 Obsidian 项目知识库

本指南以 Windows 为例，把这份仓库恢复成当前使用的状态：**项目目录就是 Obsidian Vault**，知识页随代码更新，Codex 可以通过 Obsidian MCP 读取笔记。换机不需要复制旧电脑的 Vault 设置或访问令牌。

## 1. 获取项目并打开 Vault

1. 安装 [Obsidian 桌面版](https://obsidian.md/download) 和 Codex。安装 Git，或用 GitHub Desktop 下载本仓库。
2. 把仓库克隆到新电脑的任意位置。命令行示例：

   ```powershell
   git clone https://github.com/zwj870987952-maker/maya_tools_box.git
   cd maya_tools_box
   ```

3. 在 Obsidian 的 Vault 选择界面选择**打开本地文件夹作为仓库**，选中整个 `maya_tools_box` 文件夹，不要只选 `knowledge/`。
4. 打开 `knowledge/00-首页.md`，确认能看到知识库总览、工具与模块链接。如果第一次下载后缺少 `knowledge/_generated/`，第 3 步的脚本会生成。

## 2. 在这个 Vault 安装插件

在 Obsidian 的**设置 → 第三方插件**中允许社区插件，点**浏览**，搜索 **Local REST API with MCP**（插件 ID：`obsidian-local-rest-api`），安装并启用。插件内置 MCP 服务，无需再安装独立的 Obsidian MCP 服务器。插件的 [项目说明](https://github.com/coddingtonbear/obsidian-local-rest-api) 和 [Obsidian 插件页面](https://community.obsidian.md/plugins/obsidian-local-rest-api) 可用于核对名称。

安装完成后，**退出 Obsidian**，再执行下一步。这样安装脚本写入的插件设置不会被仍在运行的 Obsidian 覆盖。

## 3. 生成这台电脑的配置并启动同步

在仓库根目录打开 PowerShell，运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_obsidian_vault.ps1
```

脚本会检查插件文件，寻找 Python 3.7+（优先使用 Codex 附带的 Python，也支持系统 Python 和 Maya 的 `mayapy`），随后：

- 为本机插件生成或沿用 API 令牌，设置仅监听 `127.0.0.1:27123` 的 HTTP MCP 服务；
- 写入本仓库的 `.codex/config.toml`，让 Codex 只在这个项目连接 Obsidian；
- 生成 `knowledge/_generated/` 并启动后台变更监视。

`.obsidian/`、`.codex/config.toml` 和监视进程的运行文件不会提交到 Git。换另一台电脑时，在那台电脑重复本指南即可。脚本可重复运行；已有令牌和监视进程会保留。如果脚本提示已有 Obsidian MCP 配置不同，先查看 `.codex/config.toml`，不要覆盖其中其他配置。

## 4. 验证连接

1. 重新打开 Obsidian 的同一个 `maya_tools_box` Vault，确认 **Local REST API with MCP** 已启用。
2. 在仓库根目录运行：

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_obsidian_vault.ps1 -Check
   ```

   成功时会显示 `Obsidian MCP connected`、工具数量，以及首页可读取。检查脚本不会打印令牌。
3. 在 Codex 中打开并信任这个项目；如果已经开着 Codex，重新打开项目或启动新会话。让 Codex **通过 Obsidian MCP 读取 `knowledge/00-首页.md`**，确认工具已加载。项目级配置只在受信任的项目中生效。

## 日常使用与排查

- 开机后需要同步时，再运行第 3 步的命令；重复运行不会创建第二个监视进程。仅想重建一次知识页，可运行 `scripts/sync_obsidian_knowledge.py`。
- 如果检查提示连接失败，先确认 Obsidian 仍在运行、打开的是**同一份仓库**、插件已启用。再看插件设置里的 HTTP 服务状态及端口 `27123`；其他 Vault 不应占用同一端口。
- 如果第 4 步检查成功但 Codex 没有 Obsidian 工具，确认 Codex 打开的是这个项目并已信任它，然后重新打开会话。检查项目根目录的 `.codex/config.toml` 是否存在。
- 如果知识页不更新，重新运行第 3 步；监视日志在 `knowledge/.knowledge_runtime/`。
- `knowledge/_generated/` 是生成内容，实际知识和经过 Maya 验证的组合流程请写在 `docs/tools/` 或 `knowledge/` 的人工笔记中。参见 [MCP 连接与编辑约定](knowledge/MCP连接.md)。

macOS/Linux 上也可以安装相同的插件，关闭 Obsidian 后用 Python 3.7+ 运行 `python3 scripts/configure_obsidian_mcp.py`，再运行 `python3 scripts/sync_obsidian_knowledge.py --watch`。Windows 的 PowerShell 启动脚本不适用于这些系统；如需常驻监视，请用当地系统的进程管理方式启动该 Python 命令。
