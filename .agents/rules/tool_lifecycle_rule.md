---
trigger: always_on
description: 新工具生命周期与准入规则：新工具必须先进入待整理库，在已打开的Maya中直接执行实测通过后，方可封装转正。
---

# 新工具生命周期与准入规则 (Tool Lifecycle & Staging Rule)

## 核心原则
1. **待整理库优先**：所有新制作、新收集的工具必须首先放入 `tools_staging_pool/` 对应的分类目录下，不得直接写入 `maya_toolkit/tools/` 生产目录。
2. **轻量直验测试**：在新工具试制阶段，直接在正在运行的 Maya 实例中检查界面、核心操作、选择结果与报错，无需提前编写繁重的抽象自动化测试。可使用 Script Editor；如使用外部 Maya 连接，应先确认连接可用且指向目标实例。窗口打开不等于业务功能验证通过。
3. **准入与封装转正**：真实 Maya 实测通过后，按 [AGENTS.md](../../AGENTS.md) 的准入流程和 [DEVELOPMENT_SPEC.md](../../DEVELOPMENT_SPEC.md) 的当前接口契约封装、补齐说明及回归测试，并挂载统一面板。参数描述使用 `parameters_schema`，不另行定义旧接口要求。
