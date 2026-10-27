# Shift Animation v3.2 候选知识说明

状态：`prepared_unverified`，真实 Maya GUI 和完整动画移动、AUTOPATH、圆形行走、Root Motion 验收 `not_run`。不迁正式库。

来源为 Pavel Barnev 的完整 Shift Animation v3.2 分发：3268 行 MEL，130 处 global proc 声明、129 个唯一过程（一个原生重复声明未改），完整原窗口、拖放安装器、英文/俄文说明、商业许可证与 BMP 图标，共六个原文件。`vendor/` 原字节保留，`catalog.json` 逐项 SHA256 对账；不改原算法、过程名、授权文字或安装器，不移除声明，不解密/反编译。独立编写的 `runtime.py/tool.py/ui.py` 负责外围参数检查、调用、状态保存和环境恢复，原文件不依赖待整理池路径。

原 License.txt 要求商业使用购买，禁止再分发、修改及移除所有权声明；整理限于本地候选，不购买、不发布第三方软件。原安装器和 guide 中的拖放文件名有差异，候选提供独立加载入口，保留原文件原样供追溯，不执行原拖放安装器或改用户 Shelf。

## 原算法与适用条件

MATCH 从非 Base 动画层的键值区间分析有层/无层的逐帧动作，完整复制层、采样定位器、约束、分配移动差值、逐帧重新置 key、清理临时组并 Euler filter。保留 source 的整数帧区间与固定步进、全部 T/R 通道及原回写层语义。说明将其称为 acceleration analysis；实际数值 helper 使用相邻关键值变化的绝对量作分配比例，并逐样本累计起末偏移，不是换成新的二阶差分算法。移动曲线 `[0,1,3]` 的独立实际计算，绝对起末偏移 `[0,6]` 返回 `[0,2,6]`；零运动原 fallback 返回 `[2,4,6]`，这一特殊首样本行为也保留。

AUTOPATH/手工路径从动画层构造原 base/second 曲线，平坦化可选轴；包括 LockCurveLength、曲线投射、逐 CV 控制器及重排、pathAnimation/uValue 逐帧采样、近点/矩阵节点、原缓动及 vertical independent、完整约束/层烘焙和临时系统清理。手工修改原 editable curve 后 `apply_path`；圆形行走保留原 fake curve、Bend_Control、Bend 曲率连接及完整 circle bake；Root Motion 保留 root/pelvis、冻结其它层成员、约束与逐帧采样、关键帧简化/Euler filter 和 override 结果层。没有用只采样点/简单 bake 冒充完整算法。

适合原 guide 所述 mocap 脚步调整、平移与转向；多次 shift/rotate 原作者建议分开处理。对象应为本地可写非实例化整控制器，输入非 Base 层含至少两帧 key。MATCH 拒绝小数键区间（原算法强制整数）；CV 数不能令原 int step 为零。`flat` 依 source upAxis 处理；播放/高亮/层键范围按原脚本实取，不假设所有操作范围相同。真实 production 约束、空间切换、层权重和脚滑效果仍须人工观察，离线检查不作效果保证。

## 统一 API

`ShiftAnimationTool` 继承 `BaseMayaTool`，使用框架 `run(dry_run, **kwargs)`、`ToolResult`、UndoChunk 与 OpenAI/MCP Schema；正式晋级后也可由注册表 `execute_tool` 调度。

| action | 参数和完整调用 |
| --- | --- |
| `status` | 默认，只读候选会话、owned UUID、pending、失败和原 MEL globals 的已存数据 |
| `analyze_curve` | `curve` 为有 key 的 time animCurve，有限 `start_value/end_value` 默认 0/1，`relative` 默认 true；原数值 helper，只读返回数组 |
| `match` | `layer` 或恰好一个已选非 Base 层；完整原 MATCH，输出 match_result 类新层 |
| `extract` | `layer` 和可选 `objects`，省略对象时按当前完整选择；原 layerEditorExtractObjectsSingleAnimLayer |
| `create_path` | 输入层，`curve_object` 可空自动检测，`cv_count=5`、`flat=True`；完整原 base/second 曲线留在场景供编辑 |
| `auto_path` | 上述参数加 `easing=10`、`vertical_independent=True`；create→完整 path compute/bake/clean 全流程 |
| `apply_path` | 会话中已有自己创建的 pending path；缓动/vertical 参数同上；按原完整流程烘焙到新结果层 |
| `create_circle` / `apply_circle` | 原 circle 固定 CV/flat 模式及 Bend 控制器流程；可指定 curve_object；apply 使用原 0 easing/vertical 模式 |
| `root_motion` | `layer/main/pelvis`（不同对象，main 在层内），`rotate=False/flat=True`；完整 Root Motion 计算 |
| `lock_curve` / `unlock_curve` | 一个整 NURBS 曲线，`objects` 或当前选择；原 Lock/Unlock 流程，拒绝会删除外来副形状/历史的输入 |
| `project_curve` | 两个整曲线按顺序，第一条投射到第二条；原重建/投射算法。未建立 path 时外围用参考曲线提供 source 的最终选择上下文，不伪造目标几何 |
| `curve_controls` | 一个整曲线；原逐 CV 控制器及完整 blindDataTemplate 网络；同曲线已有系统先拒绝；pending path 时只能控制自己的 editable curve |
| `arrange_controls` | 选择本会话某系统的一个控制器，按完整原算法重排 |
| `delete_controls` | 按选中曲线/控制器连接的唯一 owned 元数据删除对应系统、保留曲线；仅一个系统且无选择时可自动定位。多个不同曲线系统分别工作，不误删其他系统 |
| `euler_filter` | `objects` 或完整选中控制器；原 Euler filter，注意其临时 null frame/key 行为 |
| `refresh_viewport` | 原 VP 对应恢复，保留主动取消刷新暂停/恢复时间滑块可见的结果；不重写动画 |

`session` 可给唯一 network 名或 UUID；多个会话必须明确指定。未知/不适用参数、bool CV、负 easing、重复对象、非法名字/引用/锁定/实例、缺失层/keys、已有非动画控制器驱动及层曲线共享到范围外对象均预检拒绝。

**原路径应用和 Root Motion 的清理会删除参与控制器的全部 userDefined 属性**，不仅删除 `blendPoint999wb`。默认 `allow_attribute_cleanup=False`；有其它属性（如 IK_FK）时预检列出确切对象/属性并拒绝，备份并确认影响后才显式传 true，独立候选界面也有明确的许可勾选。不能因为属性属于 rig 设置而偷偷跳过原步骤并声称原算法完整。拒绝的预检本身不删任何属性。

返回 `data` 包含 vendor_result、实际清理属性清单、会话 UUID、owned 节点 UUID、全局变量快照/身份映射、待应用 path/circle、失败操作等。原动画层的 mute/selected/preferred 变化在成功后保留，因为输入层静音和结果层选择属于原输出算法；失败恢复原层状态。不要在结果层已生成后又擅自恢复输入层 mute 导致叠加两次。

## 示例、界面与操作影响

验收晋级后示例：

```python
from maya_toolkit.tools.shift_animation_v3_2 import ShiftAnimationTool
tool=ShiftAnimationTool()
tool.run(dry_run=True,action='match',layer='shiftInput')
result=tool.run(action='match',layer='shiftInput')
path=tool.run(action='create_path',layer='turnInput',curve_object='root_CTRL',cv_count=5)
# 选中/修改原 editable curve，必要时用 curve_controls/lock_curve 等完整原工具。
tool.run(action='apply_path',session=path.data['session'],easing=10)
tool.show_ui()
```

候选 `show_ui` 为独立完整前端，保留原 MATCH/Extract、路径全部参数和工具、Root Motion、Circle、Euler、VP 功能，通过统一 API 执行，另有会话字段、仅预检和属性清理许可。没有修改原 UI 文件或替换原按钮的运行时代码。`show_original_ui()` 为备份场景中的显式原版对照入口，调用原全量窗口，原回调保留原行为及保护限制；它不经过外围预检/Undo/恢复，不能同时打开两个前端，也不据此宣称原按钮已符合标准契约。

载入工具类时不导入 Maya、不 source MEL、不呼出窗口或安装 Shelf。validate/dry 不 source/声明 MEL globals、不建立会话、不改场景、时间、选择、Undo 或 prefs。执行才核对资源并 source 全量 MEL；若已加载不同版本同名过程则拒绝覆盖，要求重启 Maya。原所有 MEL 名字/globals 原样保留，不能和原版/其他版本并发操作。

原 Maya 动画层/时间滑块的 UI 过程是 MATCH/路径/Root Motion 的实际依赖；batch mayapy 明确返回 unavailable，绝不替换 getSelectedAnimLayer、假造 layer editor 或静默执行缩水算法。独立数值 helper 和实际曲线控制网络可在隔离 mayapy 运行。

每次场景写操作一个 UndoChunk；保留完整原 Scene writes、约束、层、烘焙、History/属性删除影响。异常不自动 Undo 或盲删所有新节点；记录新 UUID 及失败标记，恢复 namespace、time、selection（构造曲线/控制器时成功保留原选中输出）、autoKey、linear unit、evaluation mode、刷新暂停、时间滑块、trackSelectionOrder、三项 anim optionVars、Cached Playback preference。失败后预检拒绝再写，用户读 Script Editor 并 Undo 失败调用后续作，原临时 helper 不会误当外来对象删除。偏好/视口状态不依赖 Maya Undo 撤回；外部恢复失败也记录并明确报错。

会话 network 记录 JSON、created UUID 和 MEL globals 的对象身份；每次执行根据自己的已存状态重新提供原 MEL 上下文，避免 Undo/重命名后沿用过时 Python/MEL 缓存。仅核准自己的 pending helper 无外来子节点和曲线系统无外来连接才调用原删除逻辑。原文件安装器、外部邮件/网页、不在 API 自动执行范围；普通 API 无文件写入/导出/覆盖。本轮不做 Obsidian 同步。

## 复用、验证与晋级

复用正式 BaseMayaTool/ToolResult/Undo。core 的刷新 context 只处理基本 suspend，不覆盖此原套件的时间滑块、缓存、optionVars、单位等状态，因此外围集中恢复这些 source 明确触碰的设置；不改 core。原数值算法和通用 MEL helper 都属于授权原套件，完整调用，不复制重写后假称可下沉共享。可先准备 mocap/修正层，再 MATCH，或在一个层平移、另一层转向；生产工具组合和脚滑效果待验收。

非 GUI 检查：2 项 Python 契约/六文件与130声明指纹；5 项隔离 Maya2025 检查包含129过程完整编译、不改场景、原运动/零运动分配、层 dry 与原属性清理/共享曲线拒绝、两套完整 curve control/delete/Undo/Redo、故障后环境恢复和失败网络 Undo。未来临时正式布局的导入/注册/面板入口检查通过。完整 MATCH/动画路径/Bend/Root Motion 和界面参数/缓存/脚滑需要真实 Maya，不把数值 helper 通过写成整体效果已验证。

逐项真人步骤见 `acceptance.md`。真实备份场景验收通过后按 `promotion.json` 和预制 `plans/staging_run/promote_candidate.py` 一次搬全量代码/许可/图标/说明、知识文档和测试并插入 ALL_TOOL_CLASSES，面板由注册表发现；本轮只预览并在临时未来布局测试，不 apply。
