# 动画层逐关键帧命令执行器

工具 ID：`anim_layer_key_runner`；类别 Animation；候选版本 1.1.0。
保留同名单元的自有原始 Python、MEL 和 README 于运行包 `upstream/`。原源文件未提供第三方许可证；本轮不新增第三方许可声明。原 MEL 文件在 source 后会自动执行快捷命令，仅作可追溯存档，不作为候选入口自动运行。

## 用途和条件

把指定对象在一个动画层（或所有层）上的关键帧时间作为调度表，每帧选中这些对象、切换当前时间、执行用户提供的 MEL/Python 命令。适合按已有键点进行匹配或属性处理，不逐帧烘焙。

依赖 Maya 的 cmds/mel、Python 3 和现有框架/core，无其他通用 Python 包依赖。`asAutoSwitchFKIK` 预设另外依赖用户场景中的 Advanced Skeleton 安装、过程与角色设置；候选不附带该第三方工具。本轮仅运行临时场景中的无害命令，没有测试 Advanced Skeleton 或真实角色。

框架的 `run(dry_run=True)` **不执行命令**，只查对象、层与帧，Python 命令只编译检查语法；MEL 语法/过程存在性不通过 eval 预检。预检成功不代表命令运行成功、依赖齐全或副作用可撤销。

## 参数

| 参数 | 默认 | 作用 |
| --- | --- | --- |
| objects | null | 当前选择；也接受唯一节点名或非空节点名数组。拒绝歧义名和组件，去重 |
| command | asAutoSwitchFKIK | 明确的 MEL 命令或 Python 代码；不得为空 |
| layer | auto | 当前激活层优先、无高亮时基础层；BaseAnimation、All 或具体层名 |
| language | mel | mel 或 python，区分大小写 |
| only_in_playback | true | 只取播放 minTime~maxTime 内键时间 |
| continue_on_error | true | 某帧失败仍继续；false 在首个帧失败后停止 |
| max_frames | 10000 | 帧数上限，整数 [1,100000]，超过时预检拒绝 |

JSON Schema 导出与真实参数检查一致，拒绝未知参数、错误类型、无效层与非有限帧时间；运行前需已启用 Maya Undo。引用和锁定节点可作为只读调度目标，命令对它们的写入是否允许由 Maya 和命令自身决定，调度预检不会假称所有写入都可行。锁定动画层也不阻止查询其时间点。

## 调度、命令环境和结果

通过对象可动画属性的 `findCurveForPlug` 获取一个层的确切曲线，将 Maya 返回的单字符串统一转列表。无动画层节点时基础层只查询直接 animCurve 连接；有其他层时绝不借跨层回退混入基础层。All 逐层合并，限时间驱动 animCurveTA/TL/TU/TT。不再用宽泛的下游历史匹配，以免把无关对象或动画层权重曲线算入目标。

沿用原规则，将帧时间四舍五入至 4 位小数，升序去重，相邻保留帧间隔须 >0.001。非常接近的子帧会合并，不适合要求更高精度的调度。空动画返回成功、count=0，不执行命令。执行使用预先确定的帧表，过程中新增/删除关键帧不改变当前帧表。

每帧命令执行前重新选中目标、设置当前时间。目标用 UUID 在后续帧重查，因此命令重命名对象仍可继续；删除目标会在后续帧报告无法解析。命令可能在当前帧自行改变选择或时间，这些变化属于命令行为。

Python 代码可使用 `cmds`、`mel`、`sys`、`f`/`frame`（当前调度帧）、`objects`（该帧目标长名列表）、`frames`（调度表副本）、`layer`/`resolved_layer`、`command`/`language`。同次调用共用一个命名空间，用户变量可跨帧保存；副本列表的修改不改变调度器帧表/目标 UUID。该命名空间并非原脚本全部模块私有变量的镜像，依赖原私有 helper 的代码应改为显式 import。

MEL 通过 `mel.eval(command)` 执行，使用当时的 Maya 时间和选择。`layer` **只决定在哪些帧执行**；不切换 preferred/selected 层，不保证命令写入该层。匹配/打键命令须自行指定目标层或依赖用户已设置的动画层状态。

外部通过 `run(dry_run=False, **kwargs)` 或转正后的 `maya_toolkit.execute_tool`，返回 ToolResult。预检 data 含 objects/layer/curves/frames/count；执行含 total、count、completed_frames、errors。每个 errors 条目包含失败 frame/error 或恢复失败的 stage/error。count 是完成命令的帧数，不是已修改键数；总失败为 success=false，已完成帧仍可能留有修改。

## 影响和撤销

所有命令以正常 Maya 进程权限执行，工具不提供脚本沙箱，不分析或限制代码内容。自定义代码可能写外部文件、导出、发网络请求、重载场景、加载插件、修改选择或禁用 Undo。此类影响不由本工具撤回，也不能由 dry_run 保证安全。只对了解作用的命令使用正式执行，导出等测试使用临时目录并自行检查覆盖策略。

框架 UndoChunk 包含逐帧场景操作和恢复操作；普通 Maya 可撤销命令一次 Undo 可撤回整批。本轮隔离测试验证了 setKeyframe/setAttr/delete/rename 的典型场景，并不覆盖任意命令。失败不会自动回滚，默认继续其他帧；使用 continue_on_error=false 可停止后续帧。

finally 恢复原时间与仍存活的原选择，节点选择按 UUID 支持改名；组件按原字符串尽力恢复。命令删除节点、替换场景或修改拓扑时无法保证完整恢复。无帧时不打开额外内部 chunk、不切时间、不改选择；基础框架仍会进入自身执行包装。工具自身没有文件输出。

## 示例与入口

转正后可用：

```python
import maya_toolkit
args = dict(objects=['ctrl_root'], layer='Walk', only_in_playback=True,
            language='python', command="cmds.setKeyframe(objects, attribute='translateX', time=f)",
            continue_on_error=False, max_frames=500)
preview = maya_toolkit.execute_tool('anim_layer_key_runner', args, dry_run=True)
if preview.success:
    result = maya_toolkit.execute_tool('anim_layer_key_runner', args)
```

候选阶段使用 launch_candidate.py 的 load_tool()，不写正式注册表。窗口保留层刷新、全层、播放范围、语言切换、预设和命令输入；执行/预检经过统一框架。预检也检查输入框当前命令；原空命令预检不再作为例外。

转正后的 MEL 入口 `maya_toolkit/tools/anim_layer_key_runner/launch_ui.mel` 只定义 `mayaToolkitAnimLayerKeyRunnerUI()`，source 不执行调度或创建窗口，显式调用该过程才打开标准 Python UI。原纯 MEL 调度器完整保存在 upstream，未修补其自动执行/异常时可能漏关 undoChunk 的逻辑，不建议当作候选标准入口。

## 复用与组合

复用 BaseMayaTool、ToolResult、框架 UndoChunk；层帧查询保留在工具包，未新增公共 core。与 anim_layer_bookmark_trimmer 共享动画层查询用途，但一个查询调度时间，一个直接修剪/优化键，通道过滤语义不同，不能直接互换。可将本工具预检 frames 用于后续人工选择关键帧和其他工具的时间区间；Advanced Skeleton FK/IK 预设需单独角色验收，没有已实测的跨工具组合承诺。

## 演进与验证

相较原 Python：修复单曲线字符串返回与基础层跨层兜底；帧表保持原精度/容差；拆出原生 UI；增加参数/上限预检、Python 语法检查、逐帧结构化错误、停止选项、UUID 改名解析；实际恢复原时间和原选择（原脚本记录时间但未恢复，且最终改为目标选择）。原 Python/MEL/README 原样存档，原 MEL 默认 source 自动执行改为新的显式启动桥。

普通 Python tests 检查 Schema、无执行编译、层查询、容差、输入、原档与 UI/MEL 入口。Maya 2025 专用隔离 tests 检查无写入预检、MEL/Python 实行、帧失败/停止、层隔离和全层、播放范围/上限/空动画、改名/删除、原时间/选择及单步 Undo。真人 GUI、动画层面板、真实角色/Advanced Skeleton 和其他版本仍待 acceptance.md 验收。
