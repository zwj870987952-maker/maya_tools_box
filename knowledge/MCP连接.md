---
type: integration-guide
---

# Obsidian MCP 连接

本项目目录可作为 Obsidian Vault。本机 `.obsidian/` 中安装了 Local REST API with MCP 插件，项目级 `.codex/config.toml` 保存本机 MCP 地址和令牌。Obsidian 载入并启用插件后，连接才会生效。插件和访问凭据都由 Git 忽略，不进入云备份。换机时按 [[OBSIDIAN_SETUP|新电脑安装指引]] 重新配置。

## 首次启用

1. 在 Obsidian 中把整个 `maya_tools_box` 文件夹打开为 Vault。
2. 在该 Vault 的“设置 → 第三方插件”中关闭受限模式，并启用 **Local REST API with MCP**。
3. 插件运行后，重启 Codex，使新增 MCP 工具进入工具列表。

该连接只监听 `127.0.0.1:27123`，要求访问令牌。知识库的实时生成仍由 `knowledge/启动实时同步.ps1` 负责；MCP 用于让 AI 查询当前笔记、搜索、读取反向链接和编辑人工笔记。

## 知识编辑约定

- `knowledge/_generated/` 是自动生成的页面，不直接通过 MCP 编辑。
- 人工记录写在 `knowledge/` 的其他位置或 `docs/tools/`。
- 已通过 Maya 验证的跨工具流程写入 `knowledge/relations.json`，然后重新生成知识页。

配置脚本：[configure_obsidian_mcp.py](../scripts/configure_obsidian_mcp.py)。插件说明：[Local REST API with MCP](https://community.obsidian.md/plugins/obsidian-local-rest-api)。
