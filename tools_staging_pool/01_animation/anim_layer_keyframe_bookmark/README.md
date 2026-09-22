# 动画层关键帧区间书签生成器 (Anim Layer Keyframe Bookmark Generator)

## 📌 工具简介
在制作复杂角色动作、打击感停顿 (Hitstop)、节奏卡点或多层动画叠加微调时，动画师往往需要清晰直观地观察两两关键帧之间的跨度与停顿间歇。

本工具可以**自动提取所选控制器/物体在当前动画层级（Anim Layer）上的关键帧**，并在**相邻关键帧之间（区间）自动创建时间滑块书签 (Time Slider Bookmarks)**。同时采用**相邻色彩互斥机制**，交替变换颜色，让时间轴上的节奏分段一目了然！

---

## ✨ 核心特性

1. **智能动画层识别**：
   - **自动检测 (Auto)**：智能识别当前在 Maya 动画层面板中选中的层级；
   - **基础动画层 (BaseAnimation)**：精准提取 Base 层的底层关键帧；
   - **自定义层 (AnimLayer)**：通过 DAG 历史追溯，仅提取当前层上驱动所选物体的曲线关键帧；
   - **所有层合并 (All Layers)**：一键聚合所有层级关键帧。
2. **相邻颜色绝对互斥**：
   - 内置 4 套精心校准的专业色板：
     - **经典双色交替**（晴空蓝 / 珊瑚暖红，时间轴极易区分）；
     - **彩虹六色轮转**（海蓝 / 暖橙 / 薄荷绿 / 洋红 / 琥珀金 / 罗兰紫）；
     - **马卡龙柔和色**（低饱和明亮柔和，长时间审帧不疲劳）；
     - **赛博霓虹**（高饱和高辨识度荧光色）。
   - 数学保证任何两个相邻书签颜色绝对不重复。
3. **安全与撤销支持**：
   - 完整的原子级 `UndoChunk`，在 Maya 中按 `Ctrl+Z` 可一键瞬间撤销所有创建的书签。
   - 提供“生成前清空旧书签”选项，告别反复调试时图层堆积残留。
4. **轻量高效**：
   - 纯底层节点快速生成，避免传统命令在批量创建时频繁触发时间轴指针跳跃带来的卡顿。

---

## 🚀 Maya 中一键启动方式

### 方式一：Python 快捷命令（打开 UI 界面）
在 Maya **Script Editor (脚本编辑器)** 的 Python 选项卡中粘贴并运行：

```python
import sys
tool_path = r"d:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_keyframe_bookmark"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

import anim_layer_keyframe_bookmark
anim_layer_keyframe_bookmark.show_ui()
```

### 方式二：无界面单行脚本直接调用 (Headless / Pipeline 模式)
可在动画师自定义按键或动画标记管线中直接调用：

```python
import anim_layer_keyframe_bookmark as alb

# 对选中的物体，在当前动画层上按双色交替生成书签
alb.generate_keyframe_bookmarks(
    layer="auto",
    palette_name="dual",
    prefix="BM",
    clear_existing=True
)
```

---

## 📖 交互界面说明

| 控件区域 | 说明 |
| :--- | :--- |
| **选择层级 (Layer)** | 下拉菜单列出当前场景全部动画层，提供 `[自动识别当前高亮层]`、`[所有动画层合并]` 与各个具体层，支持点击 **🔄 刷新** 同步场景最新层级变化。 |
| **色彩方案 (Palette)** | 切换双色交替、彩虹轮转、马卡龙粉彩或霓虹色系。 |
| **命名前缀 (Prefix)** | 书签节点名称前缀，生成的书签形如 `{prefix}_{start}_{stop}`。 |
| **清空已有书签** | 勾选后在生成新书签前自动清空场景旧书签。 |
| **🔍 检查当前关键帧** | 快速检查当前选中物体在目标层上的关键帧数量与前 8 帧数值，方便预检。 |
| **🧹 清空所有书签** | 一键清理时间滑块上的所有书签。 |
