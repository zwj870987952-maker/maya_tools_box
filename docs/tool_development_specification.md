# 工具开发规范入口

本文件原为 v2.0 规范，所述接口和目录结构已有变化。当前唯一的开发契约见项目根目录的 [DEVELOPMENT_SPEC.md](../DEVELOPMENT_SPEC.md)。

请按该规范使用 BaseMayaTool 的 validate(**kwargs)、execute(**kwargs)、run(dry_run=False, **kwargs) 与 parameters_schema。工具说明使用 [知识卡模板](tools/_tool_knowledge_template.md)。

个人旧脚本和新原型先进入 tools_staging_pool/，经真实 Maya 直验后再转正。转正时补齐 API、知识说明、回归测试和面板入口。
