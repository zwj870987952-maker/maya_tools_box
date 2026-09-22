# 动画层书签关键帧修剪与曲线优化器 (Anim Layer Bookmark Keyframe Trimmer & Curve Optimizer)

## 📌 工具简介

在角色动画与镜头制作流程中，动画师常使用 Maya 的 **Time Slider Bookmark (时间滑块书签)** 划分不同的动作片段或时间区间（例如：书签 1 为 `1-59` 帧，书签 2 为 `68-100` 帧）。

本工具提供两大核心功能与三种灵活的作用范围：
1. **✂️ 关键帧修剪 (Trim Keyframes)**：
   - 只保留目标书签起始位置与结束位置处的关键帧（如 `1, 59, 68, 100` 帧）；
   - 将其余所有非端点关键帧安全删除。
2. **🎛️ 书签区间动画曲线优化 (Curve Optimization)**：
   - **端点绝对锁定**：各个书签的起始帧与结束帧（端点帧）作为姿态锚点，算法确保其时间点和数值 100% 保持不变；
   - **区间内部优化**：在每个书签的内部关键帧区间，提供：
     - **区间多帧缓入缓出 (Multi-key Ease In/Out)**：内部所有多个关键帧按 Smootherstep S 曲线整体缓动重塑（$S(u)=6u^5-15u^4+10u^3$），端点绝对锚定不变！
     - **圆滑曲线 (Smooth Curves)**：基于非均匀时间倒数加权高斯平滑滤波，消除高频抖动噪点；
     - **简化曲线 (Simplify Curves)**：开区间自适应容差冗余抽稀，剔除曲率微小和共线的冗余关键帧；
     - **端点缓入缓出 (Ease In/Out)**：起始帧出切线水平缓出，结束帧入切线水平缓入，手柄权重按力度伸展；
     - **平滑切线 (Tangents)** 与 **综合优化 (Smart Optimize)**；
   - **力度调节滑动杆 (Strength Slider 0~100%)**：实时调节缓动混合比率、平滑加权比率与简化容差阈值；
   - **权重偏置滑动杆 (Weight Bias Slider 0.0~1.0，默认 0.5 居中)**：自由控制缓动重心分布——偏向起点（0.0，起步长滞留/缓出加重）、中间（0.5，对称缓入缓出）或偏向终点（1.0，起步迅速/终点平缓缓入加重）。
3. **🔖 三重书签作用范围 (Bookmark Scope)**：
   - **全部 (All)**：全场景所有书签；
   - **时间轴范围内 (Playback Range)**：仅在有效播放范围 (`minTime ~ maxTime`) 内的书签；
   - **光标框选或所在时间轴 (Selected / Cursor)**：优先匹配时间滑块鼠标高亮框选区域，若无框选则自动锁定当前光标时间指针所在的书签。
   - **局部安全隔离**：在局部模式下，操作被严格限制在目标书签范围内，范围外的任何关键帧 100% 保持不动！

---

## ✨ 核心特性

1. **端点帧绝对锚定与姿态锁定**：
   - 算法内置双重边界保护机制，各个书签的端点值无论在多帧缓动、平滑还是简化时绝无任何漂移，确保区间起止姿态精准对齐。
2. **丰富的曲线优化算法**：
   - **区间多帧缓入缓出 (Multi-key Ease S-Curve)**：利用 Ken Perlin 五次 Smootherstep 多项式，对书签区间内部的任意多个关键帧计算归一化时间，实现整段动作的优雅平滑加减速过渡，起止端点导数为 0、数值恒定；
   - **圆滑曲线 (Smooth Curves)**：基于非均匀时间倒数加权高斯平滑滤波，消除高频抖动噪点，过渡更自然柔顺；
   - **简化曲线 (Simplify Curves)**：开区间自适应容差冗余抽稀，剔除曲率微小和共线的冗余关键帧；
   - **端点缓入缓出 (Ease In/Out)**：起始帧出切线水平缓出，结束帧入切线水平缓入，手柄权重按力度伸展；
   - **平滑切线 (Smooth Tangents)**：自动重设为柔顺 Spline 切线；
   - **综合优化 (Smart Optimize)**：一键完成平滑去噪、自适应抽稀与多帧缓动协同处理。
3. **专属动画层曲线隔离**：
   - **自动识别 (Auto)**：动态获取 Maya 动画层面板中当前激活选中的层；
   - **分层安全**：通过 `findCurveForPlug` 与下游历史拓扑依赖双重判定，仅对属于该层的专属曲线进行操作，完全隔离其他动画层。
4. **安全与撤销 (Undo & Dry Run)**：
   - **Ctrl+Z 一键撤销**：所有操作均封装在单一原子级 `UndoChunk` 中；
   - **预检分析 (Dry Run)**：执行前可点击预检，先确认检测到的端点、已存在帧以及受影响的优化关键帧数量。
5. **双重运行模式**：
   - 原生 Maya 深色交互界面（内置滑动条与范围切换）；
   - 简洁的 Python API，支持一键集成到 Shelf 工具架、快捷键或 Pipeline 自动化脚本。

---

## 🚀 启动与使用指南

### 方式一：在 Maya 中打开图形界面 (GUI)

在 Maya 的 **Script Editor (脚本编辑器)** 的 **Python** 选项卡中粘贴并运行：

```python
import sys
tool_path = r"d:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_bookmark_trimmer"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

import anim_layer_bookmark_trimmer
anim_layer_bookmark_trimmer.show_ui()
```

#### 界面操作步骤：
1. 在场景中**选中需要处理的物体或控制器**；
2. 在下拉菜单中选择**书签作用范围 (Scope)**：
   - `全部 (All)` / `时间轴范围内 (Playback Range)` / `光标框选或者所在的时间轴 (Selected / Cursor)`；
3. **进行曲线优化**：
   - 在“优化模式”下拉菜单中选择（如：`圆滑曲线`、`区间多帧缓入缓出`、`端点缓入缓出` 或 `综合优化`）；
   - 拖动“优化力度”滑动杆调整力度比率 (0.0 ~ 1.0)；
   - 拖动“权重分布”滑动杆调整重心倾向 (0.0=偏向起点 | 0.5=居中默认 | 1.0=偏向终点)；
   - 点击 **🔍 预检曲线优化 (Dry Run)** 查看预览，或点击 **✨ 执行曲线优化 (Optimize)** 立即应用。
4. **进行关键帧修剪**：
   - 点击下方 **✂️ 执行关键帧修剪 (Trim)** 即可仅保留所选书签端点帧，清理中间非端点帧（范围外关键帧 100% 保护不受影响）。

---

### 方式二：无界面直接调用 (Headless / Python API)

#### 1. 书签区间动画曲线优化
```python
import anim_layer_bookmark_trimmer as trimmer

# A. 区间多帧缓入缓出 (支持权重偏置: bias=0.2 偏向起点，0.5 居中对称，0.8 偏向终点)
result = trimmer.optimize_layer_curves_by_bookmarks(
    objects=None,
    layer="auto",
    scope="selected",            # 可选: 'all', 'playback', 'selected'
    mode="multikey_ease",       # 模式: 'multikey_ease', 'ease', 'smooth', 'simplify', 'smart'
    strength=1.0,               # 力度 0.0 ~ 1.0
    bias=0.2,                   # 权重偏置: 0.0(偏向起点) ~ 0.5(居中默认) ~ 1.0(偏向终点)
    dry_run=False
)
print(result["message"])

# B. 对当前光标所在的书签应用端点切线缓入缓出，力度 0.8
result = trimmer.optimize_layer_curves_by_bookmarks(
    objects=None,
    layer="auto",
    scope="selected",
    mode="ease",
    strength=0.8,
    bias=0.5,
    dry_run=False
)
print(result["message"])

# C. 在时间轴播放范围内执行综合优化 (平滑 + 抽稀 + 多帧缓动 + 缓入缓出)
result = trimmer.optimize_layer_curves_by_bookmarks(
    objects=None,
    layer="auto",
    scope="playback",
    mode="smart",
    strength=0.7,
    bias=0.5,
    ease_bounds=True,
    dry_run=False
)
print(result["message"])
```

#### 2. 纯端点关键帧修剪
```python
import anim_layer_bookmark_trimmer as trimmer

# 仅修剪当前光标所在的书签（范围外帧完全不受影响）
result = trimmer.trim_layer_keyframes_by_bookmarks(
    objects=None,
    layer="auto",
    scope="selected",
    ensure_keys_at_bounds=True,
    dry_run=False
)
print(result["message"])
```

---

## ❓ 常见问题排查与诊断机制 (Troubleshooting & Diagnostics)

### 1. 作用对象机制 (Selection Scope)
- **严格遵循当前选中对象**：工具**只对您在视口或大纲 (Outliner) 中选中的物体/控制器生效**。如果未选中任何物体，工具会弹出拦截提示并中止，绝不会擅自修改场景中未选中的对象。

### 2. 为什么有些选中的物体/控制器没有改变曲线？
工具在执行优化与修剪时，会在最上方的反馈窗口中输出精准的原因诊断：
1. **在该动画层上无动画曲线**：
   - 选中的物体在当前目标层（或激活层）上没有关键帧（例如：关键帧打在 BaseAnimation 或其他层，而当前工具选定的是 Layer1）。
2. **书签区间内关键帧少于 3 个**：
   - 物体在当前书签区间内仅有 1 个或 2 个端点关键帧，没有中间帧。因为工具严格执行**“端点绝对锚定锁定”**机制，起止端点姿态绝不改动，在没有内部中间帧的情况下无需且无法重塑曲线。
3. **起止端点数值完全相同 (水平直线)**：
   - 书签起点与终点的数值相等（$\Delta v = 0$）。在水平直线上应用 S 曲线缓动，所有帧的数值变形量为 0，故数值保持不变。
4. **选中了组节点而非控制器**：
   - 用户选中了物体的父级群组或空节点，而关键帧实际打在子级控制器或骨骼上。请确保直接选中带关键帧的具体控制器。

### 3. 通道聚焦与显示隐藏 (visibility) 绝对排除机制
- **🎯 默认聚焦位移与旋转**：
  - 工具默认开启 **位移 (Translate X/Y/Z)** 与 **旋转 (Rotate X/Y/Z)**，支持可选勾选 **缩放 (Scale X/Y/Z)** 或 **其他连续浮点属性**。
- **🛡️ 永久安全排除 visibility (显示隐藏)**：
  - 显示隐藏属性为布尔离散型开关 (0 或 1)，切线通常为阶梯式 (`step`)。工具内置绝对安全白名单/黑名单机制，**绝对不触碰、不平滑、不重塑任何显示隐藏动画曲线**，彻底避免误改可见性！
- **⚡ Channel Box (通道栏) 智能联动**：
  - 若在 Maya 右侧 Channel Box 中高亮点击了具体通道（如只高亮了 `translateY` 或 `rotateZ`），工具将**智能优先仅对该通道执行优化**，满足动画师精细微调单个轴向的需求；未高亮时自动应用选定的位移与旋转通道。

### 4. 最上方反馈窗口与诊断报告 (Top-pinned Diagnostics)
- **位置最上方**：反馈窗口调整至目标层与书签设置下方、优化与修剪操作按钮的正上方，第一时间即可看到结果。
- **置顶刷新 (Prepend)**：每次点击预检或执行按钮后，最新的诊断报告都会直接显示在最上面第 1 行，光标与滚动条自动定位到最顶部，无需向下拉动滚动条。
- **详尽报告结构**：
  - `🎯 作用通道`：明确显示当前生效的通道规则（如 `[位移, 旋转] (已安全排除显示隐藏)` 或 `通道栏高亮优先: [translateY]`）；
  - `✅【已成功优化的对象与属性】`：逐一列出被修改的物体与插头（如 `RootX_M.rotateY`）、书签区间、帧数变化以及关键帧数值的前后对比；
  - `⚠️【未修改/跳过的对象与属性及原因诊断】`：逐一分析未被修改的具体物体、具体属性及其根本原因。

