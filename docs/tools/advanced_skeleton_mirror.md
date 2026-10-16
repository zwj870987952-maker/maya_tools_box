# ADV 原生 Mirror

工具 ID：`advanced_skeleton_mirror`；分类：animation；版本：1.1.0。

直接调用本机 AdvancedSkeleton 原版 `asMirror`，不创建配对表、不自写轴向或矩阵镜像算法。适用于 ADV 角色及其 ControlSet。用户明确选择的入口是 **Mirror**。默认自动寻找本机最新 ADV 安装，目前选中6.640；共享发现规则见 [ADV 动画 API](advanced_skeleton_animation.md)。项目另有排除 Git 的本地备用副本，原版不随 Git 分发。

## 快速使用

在 Maya 中执行（仓库需在 Python 路径中）：

```python
import maya_toolkit
maya_toolkit.show_ui()  # 动画分类 → ADV 原生 Mirror
```

或直接打开专用界面：

```python
from maya_toolkit.tools.advanced_skeleton_mirror import AdvancedSkeletonMirrorTool
AdvancedSkeletonMirrorTool().show_ui()
```

API 默认处理当前姿态，优先从选择或唯一 ControlSet 识别角色：

```python
import maya_toolkit
args = {"action": "mirror", "namespace": "SK_CH_HM_Woman_01:"}
preview = maya_toolkit.execute_tool("advanced_skeleton_mirror", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("advanced_skeleton_mirror", args)
    print(result.to_dict())
```

非标准安装位置可添加路径线索；要锁定某一版本，应逐次传 `source_path`：

```python
from maya_toolkit.tools.advanced_skeleton_mirror import runtime
runtime.configure(r"E:/TOOLS/adv_rig/AdvancedSkeleton.6.640/AdvancedSkeleton.mel")
```

## 参数与前提

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| action | mirror | 当前姿态；open_options 打开原生选项；mirror_animation 为逐帧扩展 |
| namespace | 自动识别 | 多角色时指定，允许末尾冒号 |
| source_path | 自动发现本机最新安装 | 显式路径覆盖自动选择；不自动下载 |
| side | swap | swap / left_to_right / right_to_left |
| axis | X | X / Y / Z |
| space | main | main / world / root（RootX_M） |
| time_range | 播放范围 | 仅动画扩展，两个整数帧、含首尾、最多5001帧 |

要求 Maya GUI、停止播放、Undo 开启、有效 ControlSet、无 flipGroup 名称冲突，执行时松开 Ctrl+Shift。预检读取源文件、参数、角色和层状态，不 source MEL、不修改场景或偏好。版本门槛为6.x，但仅 **Maya 2024 + ADV 6.640** 已实测。

## 操作影响和限制

- `mirror` 遵循原生姿态行为和当前 AutoKey 状态，作用于整个 ControlSet。ADV 原生略过的控制器（如其特定 Aim 情形）不额外补算。
- `open_options` 调用原生 `asMirrorOptions`。窗口内按钮由 ADV 自己管理；其选项设置会保留。隐藏的角色上下文随窗口关闭清理。
- `mirror_animation` 是自写的时间采样及设键封装，每帧镜像仍完全调用原生 Mirror。它不是 ADV 原生的整段动画命令。目标控制器参与动画层时拒绝执行，不会自动合并层。
- 动画扩展先快照输入，逐帧调用 Mirror，再对有变化的可写标量通道烘焙整数帧键；连续通道线性切线，离散通道阶梯切线。范围外原有键值保留，必要时在前后各一帧插入守卫键，边界间的插值可能改变；不保证子帧形状完全保持，不额外进行 Euler 展开。
- API 场景改动由框架合并为一次 Undo；异常不会自动回滚，失败后需撤销该操作。当前时间、选择与 AutoKey 在调用后恢复。加载 MEL、配置路径和窗口偏好不属于场景 Undo。
- 不保存或覆盖 Maya 文件。当前含动画层的 Dance 场景只验证了原生姿态；未运行整段动画扩展。

## 输出和组合

统一返回 `ToolResult`。预检 data 含 action、namespace、source_path、native_version、native_entrypoint、side、axis、space、time_range、control_count、animation_layers。
执行额外返回 state；姿态/动画包含 native_seconds、custom_mapping=false、changed_channels（姿态为 null）；选项窗口包含 window。失败见 errors，execution_time 是包括预检的总耗时。

可在人工检查曲线后调用 `fix_rotation_winding`，或按导出工具的选择集条件调用 `export_sets_to_fbx`；这些衔接尚未联合实测，不能默认自动执行。无需 clean_namespaces；ADV 的命名空间是角色识别信息。

## 实测与演进

1.1.0：用户要求所有 ADV 调用默认寻找本机最新版。内核发现下沉到 core，保留 source_path 显式覆盖；发现器离线回归与真实 Maya 只读检查通过。新动画套件的 animRescue 崩溃记录详见其专项文档，不能将早期 Mirror 成功外推为整套动画功能稳定。

2026-10-15，在已打开 Maya 2024 中完成：

1. Dance 角色（174个控制器）：原生 Mirror 调用1.6304秒，原生部分1.5704秒；Undo 后抽查6个主要控制器世界矩阵最大差0。此耗时仅为一次姿态镜像。
2. 专用 UI 和原生选项窗口打开成功；原生窗口关闭后临时上下文清理。Dance 的 AnimLayer1 在动画预检中被正确拒绝。
3. 无层的简化 ADV 命名测试角色：1–3帧逐帧调用成功，4个通道改变，约0.1449秒；范围外0、4帧原键值保持；dry_run 前后曲线一致。测试创建的节点和动画均已撤销。此测试不代表复杂角色完整动画已验收。
4. 转正后通过统一 API 再测：同一真实角色原生姿态调用1.1971秒（原生部分1.1389秒），一次 Undo 后上述矩阵误差0；正式 UI 打开成功。32项 Python 回归测试全部通过。

候选先位于 `tools_staging_pool/01_animation/advanced_skeleton_mirror_session/native_tool/`，真实 Maya 验证后移入正式库；候选保留为历史快照，`launch_native.py` 已转调正式工具。旧 `session_runner.py` 与修改版5.740 MEL仅作早期实验记录，不由正式工具调用。后续维护只修改正式目录。
