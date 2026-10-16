---
trigger: always_on
description: 项目可持续演进与开源工具吸纳规则：支持外部开源工具吸纳与双向技术互哺升级。
---

# 项目可持续演进与开源工具吸纳规则 (Continuous Evolution & Open Source Ingestion)

## 核心原则
1. **统一规范适配**：工具转正遵循 [当前开发契约](../../DEVELOPMENT_SPEC.md)：继承 `BaseMayaTool`，使用 `parameters_schema` 描述参数，通过 `run()` 返回 `ToolResult`。完整接口与 Schema 导出方式以该文档为准，本规则不维护另一套契约。
2. **双向技术择优互哺 (Bidirectional Upgrade)**：
   - 先比较已有 `core` 与引入工具的适用条件、行为和复用价值，再决定复用或提取公共能力。
   - 性能优势须有相同条件下的测量依据，不预设 OpenMaya、MEL 或 `cmds` 的优劣；不得为了统一架构而未经直验改变旧工具行为。算法替换与接口变化记录在专项说明中，并按 [准入规则](../../AGENTS.md) 验证。
3. **开源礼仪与版权保留**：在引入外部开源工具时，务必保留原工具的作者署名、开源许可证及出处链接，并在 `README.md` 或迁移记录中明确致谢。
