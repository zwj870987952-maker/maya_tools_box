# ADV 动画工具：已转正

2026-10-16 已迁入 `maya_toolkit/tools/advanced_skeleton_animation/`，注册 `advanced_skeleton_animation`，可从 `maya_toolkit.show_ui()` 使用。默认发现本机最新 ADV 安装。

本目录保留待整理实现、原始直验脚本和证据，供追溯。`launch.py` 转发正式工具；旧测试脚本只适用于隔离的测试实例，不要在工作场景直接执行。

46个入口有 Maya 记录；14个只验窗口，MocapX 只验根命名空间的模拟数据驱动。animRescue 冲突保护、粘贴清空撤销历史等边界见 `docs/tools/advanced_skeleton_animation.md`。
