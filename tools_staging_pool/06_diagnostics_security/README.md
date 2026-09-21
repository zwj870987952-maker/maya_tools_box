# 06. 场景体检、安全杀毒与快照 (Diagnostics & Security)

> 涵盖针对 Maya 知名蠕虫脚本病毒的专杀与免疫疫苗、场景未知残留垃圾节点清理 (HM Cleaner) 以及突破原生限制的场景撤销存档点系统。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Maya 场景病毒专杀与免疫疫苗** | [scene_virus_cleaner](scene_virus_cleaner/文件病毒清理魔改版.py) | 专门查杀与清除 Maya 常见恶意脚本蠕虫病毒（如 vaccine.py, fuckVirus, breed_gene），清除恶意 scriptJob 与节点，防止工程交叉感染。 | P1 - 核心高频 |
| 2 | **场景未知与垃圾节点清理 (HM Cleaner)** | [clean_junk_nodes](clean_junk_nodes/HM_清理垃圾节点.py) | 深度清除场景中残留的 unknown 节点、失效插件声明与无引用垃圾数据，减小文件体积、解决无法保存问题。 | P1 - 核心高频 |
| 3 | **场景快照记录点与撤销恢复系统 (Undo Checkpoint)** | [undo_checkpoint](undo_checkpoint/maya_undo_checkpoint.py) | 突破 Maya 原生撤销限制。可随时为场景创建快照存档点（Checkpoint），一键快速恢复或清空，带专用工具架按钮。 | P1 - 核心高频 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
