# animBot UI Clone for Autodesk Maya

100% 高保真复刻的 animBot 动画工具栏、曲线编辑器工具栏 (Graph Editor Toolbar) 与 Workspace 工作区/工具库定制管理器（基于 PySide6 / Maya WorkspaceControl）。

---

## 🌟 核心特性

1. **主工具栏与曲线编辑器工具栏 (Dual Toolbar Support)**：
   - 支持主工具栏 (`AnimBotMainToolbar`) 与曲线编辑器内嵌工具栏 (`AnimBotGraphEditorToolbar`)；
   - 在 Workspace 工作区窗口中可对两者分别进行独立的功能激活与排版定制。
2. **全量细分子功能与独立滑杆 (Fine-grained Sub-tools & Individual Sliders)**：
   - 每一个滑杆模式（Ease、Tweener、Buffer、Time Offsetter、Mirror 等）在工作区中均拥有独立的勾选条目与工具栏槽位；
   - 支持同时激活多个滑杆并列显示；
   - **动态防重**：当某滑杆已激活显示在工具栏时，其它滑杆右键切换菜单中该项将自动禁用，避免重复。
3. **精准 Maya 预设吸附 (`workspaceControl` Docking)**：
   - 完美对接 Maya `TimeSlider`（时间轴顶部/底部）、`Shelf`（工具架顶部/底部）、`StatusLine`（状态栏顶部/底部）及独立置顶悬浮；
   - 保持严格尺寸约束，按钮永不挤压。
4. **4 大排版模式 (Left, Center, Right, Single Row)**：
   - 支持左对齐、居中对齐、右对齐与单行模式一键切换。
5. **模块原子自动换行 (Group-Atomic Wrap)**：
   - 换行以模块为原子单位，同一个模块内部按钮永不被拆分拆断。
6. **单行模式超宽拖拽滑动 (Drag Panning & Wheel)**：
   - 鼠标左键/中键拖拽平滑滑动（抓手手势）与鼠标滚轮横向滚动。
7. **弹簧回弹滑块 (`AnimBotSlider`)**：
   - 拖拽平滑调节，松开自动平滑回弹至 0.0。
8. **全套按钮右键快捷菜单 (`AnimBotContextMenuBuilder`)**：
   - 40+ 个核心按钮均支持右键专属预设菜单。

---

## 🚀 启动与使用方式

在 Maya 的 Python 脚本编辑器（Script Editor）中运行：

```python
import sys
if r"d:\jiaoben\jiaoben2026\Google" not in sys.path:
    sys.path.insert(0, r"d:\jiaoben\jiaoben2026\Google")

import animbot_copy

# 1. 启动主工具栏
toolbar = animbot_copy.launch()

# 2. 嵌入曲线编辑器工具栏 (Graph Editor Toolbar)
animbot_copy.attach_to_graph_editor()

# 3. 打开 Workspace 工作区定制窗口
toolbar.open_workspace_editor()

# 4. 切换显示 / 隐藏
animbot_copy.toggle()

# 5. 关闭
animbot_copy.close()
```
