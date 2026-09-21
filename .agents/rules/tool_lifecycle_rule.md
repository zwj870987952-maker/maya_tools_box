---
trigger: always_on
description: 新工具生命周期与准入规则：新工具必须先进入待整理库，在已打开的Maya中直接执行实测通过后，方可封装转正。
---

# 新工具生命周期与准入规则 (Tool Lifecycle & Staging Rule)

## 核心原则
1. **待整理库优先**：所有新制作、新收集的工具必须首先放入 `tools_staging_pool/` 对应的分类目录下，不得直接写入 `maya_toolkit/tools/` 生产目录。
2. **轻量直验测试**：在新工具试制阶段，测试方式统一为**直接在正在运行的 Maya 实例中执行打开界面或运行功能**（通过 Maya 脚本编辑器或 Maya MCP 接口），无需编写繁重的抽象自动化测试用例。
3. **准入与封装转正**：只有在真实 Maya 中实测通过、确认功能完好且无明显报错后，才由代理或开发者按照 `BaseMayaTool` + `ToolResult` + `get_schema()` + `dry_run` 规范正式封装迁移至 `maya_toolkit/tools/`，并挂载到统一启动器面板 `maya_toolkit.show_ui()`。
