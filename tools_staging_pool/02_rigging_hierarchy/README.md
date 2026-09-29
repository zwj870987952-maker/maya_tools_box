# 绑定、骨骼与层级管理 (Rigging & Hierarchy)

> 当前分类共收纳 **14** 个纯明文开源的工具与脚本。所有代码均已解耦并开放，可直接阅读、调试或封装转正。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 |
| :--- | :--- | :--- | :--- |
| 1 | **OverRig 角色二级动力学绑定装配系统 v9.0** | [base_overrig_v9_0](base_overrig_v9_0/base_OverRig_scripts_V9_0/base_OverRig_scripts.mel) | 完整用户手册、图标与骨骼模板，高级副级动力学约束系统 |
| 2 | **按顺序批量蒙皮/绑定与代理生成** | [batch_skin_bind](batch_skin_bind/批量绑骨头.py) | 按选择顺序将成组模型与骨骼链自动执行标准蒙皮绑定，支持快速骨骼碰撞代理生成。 |
| 3 | **bb_Tools 绑定与控制器综合工具集** | [bb_tools](bb_tools/bb_ctrlTool.mel) | 包含属性批量控制、毛囊生成、控制器造型库与蒙皮权重清单 |
| 4 | **场景约束综合管理与重建工具** | [constraint_manager_v6](constraint_manager_v6/约束管理v6.py) | 约束全生命周期管理。支持将场景约束拓扑导出为 JSON、一键批量静音/恢复、安全删除与无损重建（含偏移保持）。 |
| 5 | **DAG节点层级关系分析器** | [hierarchy_analyzer](hierarchy_analyzer/maya_hierarchy_analysis.py) | 深度分析场景选中节点的完整父子继承链、DAG 绝对路径及依赖节点关系，结构化输出层级树。 |
| 6 | **骨骼朝向与轴向优化神器 (Joint Optimal Pro v4.1)** | [joint_optimal_pro_v4_1](joint_optimal_pro_v4_1/Joint_Optimal_Pro.mel) | 专业纠正骨骼旋转轴 (Rotate Axis) 与关节定向 (Joint Orient)，带完整 PDF 说明 |
| 7 | **RdM Tools 自动化角色绑定与装配套件 v2 (中文版)** | [rdm_tools_v2](rdm_tools_v2/RdMToolsV2/__init__.py) | 解压中文版源码与 UI，过滤教程视频，全自动手臂、腿部、头部装配与蒙皮工具 |
| 8 | **高级层级与空间切换工具 (Relationship Tools v19)** | [relationship_tools_v19](relationship_tools_v19/Relationship Tools_v19.py) | 历经 19 次迭代的核心层级/约束工具。支持父子/世界空间切换、约束烘焙、层级安全断开与重连、主从关系维护。 |
| 9 | **reParent Pro 高级层级重构与父子切换器 v1.5.1** | [reparent_pro_v1_5_1](reparent_pro_v1_5_1/reParent_Pro_v1.5.1.mel) | 无损维持当前位移旋转情况下动态重构 DAG 父子从属关系 |
| 10 | **批量取消骨骼分段比例补偿 (Segment Scale Fix)** | [segment_scale_fix](segment_scale_fix/批量取消骨骼分段比例补偿.py) | 一键递归遍历骨骼链关闭 segmentScaleCompensate 属性（游戏引擎骨骼缩放动画的关键避坑点，防止导入 UE/Unity 缩放异常）。 |
| 11 | **选区顺序生成骨骼链** | [skeleton_generator](skeleton_generator/选区生成骨骼链.py) | 根据当前选中的多个物体/Locator 的世界坐标顺序，自动创建定向对齐的 Joint 骨骼链。 |
| 12 | **SkinInfo v1.92 权重导入导出与 SuperConnect 约束管理器** | [skin_info_and_super_connect](skin_info_and_super_connect/skinInfo_V1.92.mel) | 淘汰旧版 1.7/1.8/1.91，打包最新的 skinInfo_V1.92 与 Super_Connect 约束链接器 |
| 13 | **SkinMagic 蒙皮权重平滑与魔法笔刷** | [skin_magic](skin_magic/SkinMagic.py) | 图形化蒙皮权重调节器，快速分配、镜像与就近吸附顶点权重 |
| 14 | **骨骼蒙皮权重转移工具** | [skin_weight_transfer](skin_weight_transfer/骨骼权重转移.py) | 提取源骨骼链的 SkinCluster 蒙皮权重，按骨骼命名或就近空间拓扑快速转移至新骨骼链。 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.framework.base_tool.BaseMayaTool`；
2. **标准化输出**：执行入口统一为 `run(dry_run=False, **kwargs) -> ToolResult`；
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用；
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用；
5. **双向反哺下沉**：通用几何、矩阵或 DAG 算法下沉沉淀到 `maya_toolkit.core` 公共库中。
