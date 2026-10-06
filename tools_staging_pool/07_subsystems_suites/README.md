# 大型专业独立子系统与完整套件 (Subsystems & Suites)

> 当前分类共收纳 **7** 个纯明文开源的工具与脚本。所有代码均已解耦并开放，可直接阅读、调试或封装转正。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 |
| :--- | :--- | :--- | :--- |
| 1 | **animBot 完整 UI 与工具克隆套件** | [animbot_copy](animbot_copy/launch.py) | 完整复刻知名动画插件 animBot 的 UI 与工具库：包含 Graph Editor 曲线编辑器嵌入式工具栏、弹性回弹多段滑块、工作区管理。 |
| 2 | **GETOOLS 动力学与次级动作套件 (含 Overlappy / CenterOfMass)** | [getools_overlappy](getools_overlappy/GeneralWindow.py) | 包含两大神器：1. Overlappy 一键自动生成物理次级重叠惯性动作；2. CenterOfMass 角色实时重心质心解算。 |
| 3 | **Malcolm341 Maya 高级实用脚本合集 (MegaPack 2023)** | [malcolm341_mega_pack](malcolm341_mega_pack/install.mel) | 汇集了大量影视游戏一线制作加速脚本与架上工具 |
| 4 | **Maya 节点式蓝图自动化工具箱 (Blueprint Toolbox 完整工程)** | [maya_blueprint_toolbox](maya_blueprint_toolbox/main.py) | 基于 Qt 的可视化节点连线画布与执行引擎。支持像虚幻蓝图一样连线驱动 Maya 操作，内置动画、属性、约束等通用 API 包装。 |
| 5 | **Maya 视口智能拖拽与对话框拦截助手** | [smart_assistant](smart_assistant/main.py) | 视口拖拽与文件对话框拦截：将图片序列拖入视口自动生成摄像机与 ImagePlane；拖入 FBX/MA 自动弹窗提示导入/引用规则。 |
| 6 | **Studio Library 世界空间扩展增强包 (PlusPatch)** | [studiolibrary_patch](studiolibrary_patch/studiolibrary_wanimation/__init__.py) | 在原生 Studio Library 基础上增加了世界坐标动画抓取与跨角色粘贴 (WAnimation)、世界坐标姿态对齐 (WPose) 与中文汉化。 |
| 7 | **TheKeyMachine 动画师综合套件 (完整汉化增强版)** | [the_key_machine](the_key_machine/core/toolbar.py) | 关键帧微调工具：包含曲线平滑、切线权重批量调整、反向动画、自定义曲线图编辑器与一键汉化补丁。 |

## 经作者授权发布的待整理候选

此类条目不计入上述 7 项开源工具数量，尚未通过真实 Maya 直验。

| 工具 | 候选入口 | 整理范围与状态 |
| --- | --- | --- |
| Animo V10.6.0 | [launch_candidate.py](animo/release_candidate/launch_candidate.py) | 55 类、553 个入口；统一 API、Schema、静态分析及人工检验面板；20 项离线测试通过，待用户检验。按用户确认的作者授权同步原始/候选源码和素材，见 [授权记录](animo/AUTHOR_PERMISSION.md) 与 [说明](animo/release_candidate/README.md)。 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.framework.base_tool.BaseMayaTool`；
2. **标准化输出**：执行入口统一为 `run(dry_run=False, **kwargs) -> ToolResult`；
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用；
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用；
5. **双向反哺下沉**：通用几何、矩阵或 DAG 算法下沉沉淀到 `maya_toolkit.core` 公共库中。
