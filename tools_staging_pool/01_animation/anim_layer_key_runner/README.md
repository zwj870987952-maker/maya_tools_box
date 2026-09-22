# 动画层逐关键帧命令执行器 (Anim Layer Keyframe Command Runner)

## 📌 工具简介

在角色动画制作与骨骼绑定中，动画师经常使用**动画层 (Animation Layer)** 进行分层 K 帧或次级微调。当需要在关键帧处进行姿态匹配（如 **Advanced Skeleton 的 IK/FK 无缝切换匹配 `asAutoSwitchFKIK`**）或批量属性操作时，如果逐帧烘焙，会破坏原始动画曲线的手动关键帧结构；而如果手工跳转每一帧点击切换，效率极其低下。

本工具可以**精准识别选中控制器/物体在特定动画层（或当前高亮激活层）上的专属关键帧**，并在每个有关键帧的时间点自动跳转时间轴并触发指定的 MEL 或 Python 命令。

---

## ✨ 核心特性

1. **精准动画层过滤**：
   - **自动识别 (Auto)**：自动读取 Maya 动画层面板中当前选中的层级；
   - **基础层 (BaseAnimation)**：专门针对底层基础动画帧执行；
   - **自定义层 (AnimLayer)**：通过属性插头 (`findCurveForPlug`) 与下游依赖历史拓扑双重判定，仅提取该层上的曲线关键帧；
   - **全层合并 (All Layers)**：一键聚合所有层级关键帧。
2. **高精度关键帧去重与排序**：
   - 自动合并控制器各通道（平移、旋转等）的重复关键帧；
   - 带有浮点数容差判定，完美支持带有小数帧（Sub-frame）的高精度动画。
3. **双引擎与预设支持**：
   - 支持一键执行 **MEL 命令/过程** 或 **Python 脚本/表达式**；
   - 内置 Advanced Skeleton `asAutoSwitchFKIK`、`setKeyframe` 等高频预设。
4. **安全与撤销 (Undo Support)**：
   - 包含完整的原子级 `UndoChunk`，在 Maya 中按下 `Ctrl+Z` 可一键瞬间撤销所有关键帧上产生的变更。
   - 提供 **🔍 预检 (Dry Run)** 按钮，执行前可先预览关键帧数量与具体时间列表，避免误操作。

---

## 🚀 Maya 中一键启动方式

### 方式一：Python 快捷命令（打开交互式 UI 界面）
在 Maya **Script Editor (脚本编辑器)** 的 **Python** 选项卡中粘贴并运行：

```python
import sys
tool_path = r"d:\Users\zhongweijie\Documents\GitHub\maya_tools_box\tools_staging_pool\01_animation\anim_layer_key_runner"
if tool_path not in sys.path:
    sys.path.insert(0, tool_path)

import anim_layer_key_runner
anim_layer_key_runner.show_ui()
```

### 方式二：Python 无界面直接调用 (Headless / Pipeline 模式)
在自定义 Shelf 工具架按钮或动画脚本中直接调用：

```python
import anim_layer_key_runner as alkr

# 对选中的物体，在当前动画层的每个关键帧上自动运行 asAutoSwitchFKIK
alkr.run_command_on_keyframes(
    command="asAutoSwitchFKIK",
    layer="auto",               # "auto" 自动检测当前高亮层，或传入具体层名如 "Layer_Arm"
    language="mel",             # "mel" 或 "python"
    only_in_playback=True,      # 仅在时间滑块播放范围内执行
    dry_run=False               # 设为 True 可先预检关键帧数量
)
```

### 方式三：MEL 纯脚本运行（适合直接拖入 MEL 选项卡或 Shelf）
打开本目录下的 `anim_layer_key_runner.mel`，直接在 Maya **MEL** 选项卡中运行即可：

```mel
source "d:/Users/zhongweijie/Documents/GitHub/maya_tools_box/tools_staging_pool/01_animation/anim_layer_key_runner/anim_layer_key_runner.mel";
```

---

## ❓ 常见问题排查 (Troubleshooting)

1. **报错 `# 错误: invalid character '（' (U+FF08)`**：
   - **原因**：把 MEL 脚本粘贴到了 Python 选项卡中。
   - **解决**：在 Maya 脚本编辑器中点击新建或切换到 **MEL** 标签页再运行；或者使用上述提供的 **Python 版启动代码**。
2. **提示“未检测到当前选中的动画层”**：
   - **解决**：请在 Maya 右下角/侧边的 **Animation Layer Editor** 中用鼠标左键**点击高亮选中**你要处理的动画层；或者在界面下拉菜单中直接选择具体层名。
