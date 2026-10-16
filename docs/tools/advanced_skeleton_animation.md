# ADV 动画 API：本机原生内核

## 当前状态

**已于 2026-10-16 转正**，tool_id=`advanced_skeleton_animation`，版本1.0.0，已注册到统一 API 与面板。46个固定入口直接调用本机原版 MEL，不改动 ADV 源文件或重写算法。

46个入口均有真实 Maya 2024 / ADV 6.640 验证记录。其中14个交互窗口只验证打开与关闭，MocapX 只验证模拟数据节点到面部控制器的原生连接，不能视为设备采集或所有窗口内部业务流程通过。具体范围见 [逐入口目录](advanced_skeleton_animation/INDEX.md)。

本轮在另一已打开的空 Maya 实例中临时卸载 animRescue 后验收；未修改恢复后的 Dance 工作场景。动画清理确认/取消/撤销、MocapX 四类驱动数值与撤销、交互播放启动/推进/停止、五帧动力学烘焙与撤销均通过。测试和后续空闲期间未再次崩溃；这不等于解决了上次崩溃的根因。

2026-10-15 18:23 崩溃日志显示 `animRescue_2024x64.mll`（MGTools）在空闲回调中调用 `MFnDependencyNode::name`，随后访问异常。此调用栈提示回调与节点生命周期问题，**尚未隔离出根因，不能直接断言由某一 ADV 功能导致**。API 检测到 animRescue 已加载时拒绝新的场景操作；只读取目录/状态及无场景写入的窗口入口仍可使用。不会自动卸载插件或关闭用户的自动恢复功能。

## 内核发现规则

共享实现：`maya_toolkit/core/advanced_skeleton.py`。现有正式 Mirror API 与动画工具共用此逻辑。

1. 每次未提供 source_path 时，从本机已知安装目录发现版本，按源文件头的版本号选择最新安装，避免根据文件夹名字误判。
2. 搜索范围：`ADVANCED_SKELETON_PATH`（路径分隔符分隔）、Maya script path、用户 scripts 目录、已配置路径和已加载来源的相邻版本，以及常见盘符下 `TOOLS/adv_rig`、`Tools/AdvancedSkeleton`。最多向下两层，不扫描整块硬盘。
3. 发现结果缓存60秒；`discover(refresh=True)` 强制刷新。候选文件存在性检查和文件内容缓存按修改时间/大小失效。
4. 显式 `source_path` 覆盖自动选择。旧 Mirror configure 路径用于增加发现线索，不再永久锁定旧版本。
5. 检查完整资源目录与所需原生过程；新版缺入口时明确报错，不静默回退旧版。仅6.640在本次实测，新版自动选中不代表已验证兼容。
6. 项目本地 vendor 副本排除 Git；外部安装优先于副本。本机发现18个外部6.x安装，最新为6.640，另有项目备用副本。

```python
from maya_toolkit.core import advanced_skeleton
print(advanced_skeleton.resolve())
print(advanced_skeleton.discover(refresh=True))
```

其他安装位置可设置 `ADVANCED_SKELETON_PATH`，或使用 `discover(extra_roots=[r"D:/MyMayaTools"], refresh=True)` 查找。API 执行时要使用返回的 source_path；一次性的 extra_roots 不会自动写入持久配置。

## 正式调用方法

通过 `maya_toolkit.show_ui()` 打开统一面板，在动画分类中选择“ADV 动画工具”。也可直接调用：

```python
import maya_toolkit
catalog = maya_toolkit.execute_tool("advanced_skeleton_animation", {"operation": "catalog"})
print(catalog.to_dict())
args = {"operation": "switch_fk_to_ik", "namespace": "character:", "limb": "Arm_L"}
preview = maya_toolkit.execute_tool("advanced_skeleton_animation", args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool("advanced_skeleton_animation", args)
    print(result.to_dict())
```

时间范围只用于 `bake_fk_to_ik`、`bake_ik_to_fk`、`bake_extra_to_controls`、`bake_quick_ik`，整数帧含首尾，最多5001帧。它临时设置播放范围再恢复；原生 Extra 烘焙会替换整条曲线，**不承诺范围外关键帧保留**。`bake_controls_to_extra` 移动整条曲线，不能传 time_range。

## 参数契约

| 参数 | 语义 |
| --- | --- |
| operation | 固定目录 ID，默认 catalog；status 读取本次进程里的交互作业状态 |
| namespace | 明确角色；省略从选择或唯一 ControlSet 识别 |
| nodes | 有序 transform/joint 列表，省略使用当前选择；Parent 的子控制器必须最后 |
| limb | 只用于显式 FK/IK 入口，例如 Arm_L、Leg_R、Spine_M |
| time_range | 仅上述四种烘焙入口，默认原生播放范围 |
| control_set | ControlSet 或 FaceControlSet；Mirror 目前只支持已验证的 ControlSet |
| source_path | 省略或空字符串自动寻找本机最新安装 |
| accept_undo_history_loss | 粘贴必须明确为 True；默认为 False |

预检检查参数、版本与过程存在性、GUI/停止播放/Undo、修饰键、角色/节点选择、必要肢体/Extra/QuickIK、目标动画层、部分外部依赖以及已观察到的 animRescue 冲突。不会 source MEL、写文件或修改场景。它不是对全部原生内部条件的完整模拟，尤其不保证外部动捕文件的字段匹配。

## 执行与返回

返回框架 ToolResult；success 只表示分派或原生调用返回，应再看 data.state、execution_mode、verification 和实际场景效果。

- `api`：执行原生过程，state=`native_call_returned`。ADV 很多过程没有业务返回值，故 completed_effect 为 null；需检查目标曲线、混合属性或生成节点。
- `interactive_ui`：打开原生窗口，state=`ui_open`、completed_effect=false。下载、连接、Apply、Bake 等内部按钮仍需用户操作，未封装为无人值守批处理。
- `interactive_dialog`：原生 Clean/Dynamics Bake 有确认对话框，返回 awaiting_native_dialog、job_id。作业通过 Maya idle 调用，重新核对角色身份；status 可查失败或 native_dialog_returned。原版不给确认/取消结果，所以不能把 dialog_returned 当作业务成功。该路径已验证确认、取消和撤销；返回值仍不自动判定用户是否确认。
- `interactive_playback`：原生交互播放，返回 playback_started；已验证播放状态、帧推进和 `maya.cmds.play(state=False)` 停止。调用影响全局播放，不以普通场景 Undo 保证停止。

原生窗口的隐藏角色上下文随窗口关闭清理。时间、选择、AutoKey 和临时播放范围在同步执行后恢复；原生窗口按钮后续执行不在这次调用的 Undo Chunk 内。

## 场景和文件影响

普通场景操作由 BaseMayaTool 使用 UndoChunk；异常不会自动回滚。实际验证了姿态操作、三帧 FK/IK 烘焙和 QuickIK/Dynamics 的撤销恢复；不外推到所有第三方插件组合。

**原生 pose_paste / animation_paste 使用临时文件引用，移除引用会清空 Maya Undo 历史。** 本轮测试确认过这个影响，因此必须显式 opt-in；不要在尚需撤销的工作场景中试用。Copy 覆盖 ADV 用户临时目录里的 ClipBoard0.ma / ClipBoard1.ma；文件操作不受 Undo 保护。测试已备份并恢复这些剪贴板文件，且显式删除测试命名空间。

Dynamics 初始状态和 Bake 的原生范围涉及全场景动力学，不能误认为仅 namespace 内。QuickIK/Dynamics/Parent 会增删节点、约束、属性或连接。原版可能使用全局临时名称，包装只检查了部分已知冲突。新 API 不自动保存文件、不自动下载依赖、不自动关闭其他插件。

## 限制与相关工具

正式 `advanced_skeleton_mirror` 仍提供已验证的专用 Mirror API；新版发现逻辑已接入。本工具不自动清理命名空间、不自动执行曲线修复或 FBX 导出。与 `fix_rotation_winding`、`export_sets_to_fbx` 的组合需要按其输入条件另验。

MocapX 当前仅支持根命名空间。原生6.640过程直接引用无命名空间的曲线名，因此预检拒绝带命名空间角色、重复连接、缺失数据/面部属性、锁定或已有输入的目标；不自行改写供应方连接算法。真实 MocapX 插件/设备流仍需对应环境验收。

验证证据：正式包内 `verification.json` 保存逐项范围及历史崩溃记录；待整理目录保留原始实现、`verify_remaining.py` 和 `verification_remaining_20261016.json`。本轮首个动力学测试夹具缺少变形关节父节点，原生执行失败后已撤销；补齐夹具后通过，并加入必要父节点预检。不得把夹具修正误记为供应方算法修复。

功能组合已验证：原生 Dynamics Add → Dynamics Bake → Undo（五帧测试链）。其他跨工具组合仍需单独验收。所有源文件默认从本机最新完整 ADV 安装读取；本次实测版本为6.640。

转正后复验：统一注册共8个工具；面板显示46项，实际点击预检与 Key 按钮成功。统一 API 的 dry_run 未改变曲线；正式 Clean、MocapX 连接与撤销再次通过。46个离线回归测试通过。测试实例已清空并恢复 animRescue；工作实例仅打开面板及执行只读预检，场景写入仍由插件冲突保护拦截。
