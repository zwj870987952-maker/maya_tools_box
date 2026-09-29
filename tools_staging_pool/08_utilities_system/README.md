# 系统辅助与环境管理 (Utilities & System)

> 当前分类共收纳 **7** 个纯明文开源的工具与脚本。所有代码均已解耦并开放，可直接阅读、调试或封装转正。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 |
| :--- | :--- | :--- | :--- |
| 1 | **吸附式悬浮快捷工具栏** | [floating_toolbar](floating_toolbar/floating_toolbar.py) | 基于 PySide2 的悬浮工具条，可自动吸附在 Maya 视口边缘，支持拖拽 Shelf 命令或自定义按钮生成轻量操作浮窗。 |
| 2 | **KS NodeOutliner 节点分类大纲增强管理器 v2.2.0** | [ks_node_outliner_v2_2](ks_node_outliner_v2_2/ks_nodeOutliner/ksNodeOutliner.py) | 解压 KS_NodeOutliner-2.2.0.zip，按节点类型过滤与大纲容器聚合展示 |
| 3 | **KS SaveTimer 智能工程自动保存与版本递增 (原版+汉化版)** | [ks_save_timer_v1_3_0](ks_save_timer_v1_3_0/KS_SaveTimer.py) | 包含原版与汉化版完整代码与手册，定期提醒与多重备份 |
| 4 | **Maya 进程与端口查找器 (MayaFinder)** | [maya_process_finder](maya_process_finder/maya_process_finder.py) | Windows 独立桌面 GUI。自动探测枚举本机所有运行中的 Maya 进程 PID、占用端口（Command Port），排查卡死与多开。 |
| 5 | **Maya-Tabs 视口多工程标签页切换扩展 v1.3a** | [maya_tabs_v1_3a](maya_tabs_v1_3a/plug-ins/Maya-Tabs.py) | 解压 Maya-Tabs_v1.3a.zip，在视口顶部呈现类似浏览器标签的多场景快速切换条 |
| 6 | **Maya 视口智能文件拖拽重载扩展** | [perform_file_drop_action](perform_file_drop_action/performFileDropAction.mel) | 重载 performFileDropAction.mel，支持拖拽自动识别格式与智能弹窗处理 |
| 7 | **Maya 跨版本工具架管理器 (2018-2026)** | [shelf_manager](shelf_manager/shelf_manager.py) | 集中管理 Maya 2018~2026 各版本的 Shelf 工具架配置，区分中英文路径，支持跨版本复制、同步与备份。 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.framework.base_tool.BaseMayaTool`；
2. **标准化输出**：执行入口统一为 `run(dry_run=False, **kwargs) -> ToolResult`；
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用；
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用；
5. **双向反哺下沉**：通用几何、矩阵或 DAG 算法下沉沉淀到 `maya_toolkit.core` 公共库中。
