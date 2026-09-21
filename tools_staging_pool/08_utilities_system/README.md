# 08. 系统辅助与环境管理 (Utilities & System)

> 涵盖 Windows 独立桌面 Maya 进程/端口侦查器 (MayaFinder)、跨版本 (2018-2026) 工具架管理器以及吸附式悬浮快捷工具栏。

## 工具清单与导向

| 序号 | 工具名称 | 对应目录与入口 | 核心功能简述 | 建议重构优先级 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | **Maya 进程与端口查找器 (MayaFinder)** | [maya_process_finder](maya_process_finder/maya_process_finder.py) | Windows 独立桌面 GUI。自动探测枚举本机所有运行中的 Maya 进程 PID、占用端口（Command Port），排查卡死与多开。 | P1 - 核心高频 |
| 2 | **Maya 跨版本工具架管理器 (2018-2026)** | [shelf_manager](shelf_manager/shelf_manager.py) | 集中管理 Maya 2018~2026 各版本的 Shelf 工具架配置，区分中英文路径，支持跨版本复制、同步与备份。 | P1 - 核心高频 |
| 3 | **吸附式悬浮快捷工具栏** | [floating_toolbar](floating_toolbar/floating_toolbar.py) | 基于 PySide2 的悬浮工具条，可自动吸附在 Maya 视口边缘，支持拖拽 Shelf 命令或自定义按钮生成轻量操作浮窗。 | P1 - 核心高频 |

## 整合至 `maya_toolkit` 的规范要求
当您挑选本目录中的工具进行正式重构时，请遵循以下规范：
1. **继承基类**：所有工具类需继承自 `maya_toolkit.core.base_tool.BaseMayaTool`。
2. **标准化输出**：执行入口统一为 `run(**kwargs) -> ToolResult`，支持 `success`, `data`, `message`, `errors` 结构。
3. **大模型 Schema 支持**：通过 `get_schema()` 提供入参类型说明与默认值，支持 Agent 自动读取调用。
4. **安全试运行**：必须支持 `dry_run=True` 预检模式，在执行破坏性/批量操作前不产生实际副作用。
