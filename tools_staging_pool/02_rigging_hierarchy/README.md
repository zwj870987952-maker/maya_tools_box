# 02. 绑定、骨骼与层级管理 (Rigging & Hierarchy)

> 涵盖历经多次迭代的高级层级与空间切换工具 (Relationship Tools)、约束全生命周期管理、骨骼蒙皮权重转移、游戏引擎分段比例补偿修复等。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **高级层级与空间切换工具 (Relationship Tools v19)** | [relationship_tools_v19](relationship_tools_v19/Relationship Tools_v19.py) | 历经 19 次迭代的核心层级/约束工具。支持父子/世界空间切换、约束烘焙、层级安全断开与重连、主从关系维护。 | P1 - 核心高频 |
| 2 | **场景约束综合管理与重建工具** | [constraint_manager_v6](constraint_manager_v6/约束管理v6.py) | 约束全生命周期管理。支持将场景约束拓扑导出为 JSON、一键批量静音/恢复、安全删除与无损重建（含偏移保持）。 | P1 - 核心高频 |
| 3 | **骨骼蒙皮权重转移工具** | [skin_weight_transfer](skin_weight_transfer/骨骼权重转移.py) | 提取源骨骼链的 SkinCluster 蒙皮权重，按骨骼命名或就近空间拓扑快速转移至新骨骼链。 | P1 - 核心高频 |
| 4 | **批量取消骨骼分段比例补偿 (Segment Scale Fix)** | [segment_scale_fix](segment_scale_fix/批量取消骨骼分段比例补偿.py) | 一键递归遍历骨骼链关闭 segmentScaleCompensate 属性（游戏引擎骨骼缩放动画的关键避坑点，防止导入 UE/Unity 缩放异常）。 | P1 - 核心高频 |
| 5 | **选区顺序生成骨骼链** | [skeleton_generator](skeleton_generator/选区生成骨骼链.py) | 根据当前选中的多个物体/Locator 的世界坐标顺序，自动创建定向对齐的 Joint 骨骼链。 | P1 - 核心高频 |
| 6 | **DAG节点层级关系分析器** | [hierarchy_analyzer](hierarchy_analyzer/maya_hierarchy_analysis.py) | 深度分析场景选中节点的完整父子继承链、DAG 绝对路径及依赖节点关系，结构化输出层级树。 | P2 - 进阶扩展 |
| 7 | **按顺序批量蒙皮/绑定与代理生成** | [batch_skin_bind](batch_skin_bind/批量绑骨头.py) | 按选择顺序将成组模型与骨骼链自动执行标准蒙皮绑定，支持快速骨骼碰撞代理生成。 | P2 - 进阶扩展 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
