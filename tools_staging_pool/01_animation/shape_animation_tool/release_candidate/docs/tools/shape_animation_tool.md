# Shape Animation Tool 修型动画候选

状态：`prepared_unverified`，真人 Maya GUI 验收 `not_run`。本目录镜像未来正式布局，仍留在待整理池。不得因 mayapy 通过便直接晋级。

用途：在动画的不同帧建立逐帧修型；一层使用原始成对 blendShape 目标，一个目标是禁用本层后采样的基准，一个目标是当前形状。正目标动画权重驱动 `multDoubleLinear.input1`，`input2=-1`，输出驱动负基准权重，得到修型差值。新关键帧会在本层既有曲线上置零，并在新正目标曲线上为既有帧置零、当前帧置一。保留原版的插值及 weightedTangents 开/关处理，不替换成简化单目标或全网格逐帧缓存。

来源：原包关于窗口记载作者 Pavel Korolyov，汉化帝都儿，画笔 Brave Rabbit Studio；原包附商业购买地址，没有独立再分发许可证。仅作本地自有工具整理，不发布第三方源码。六套完整分发各含六个 Python 文件，另有启动代码、购买地址和安装使用说明 Word，共 39 个原文件，按原字节归档于 `upstream/`；Python 原件扩展名为 `.py.original`，避免误执行。清单记录每个 SHA256。

主运行端使用 2022 Python3 汉化版完整 34 个类方法和全量生成界面。六套 main 的方法集合一致；旧版仅有 NoneType、注释等 Python 兼容差异，英文版另有主页链接和界面文字差异。保留完整英文及旧版原分发供追溯，不冒称已测试其旧环境。`native.py` 留存所有原方法定义；`ui_bridge.py` 将每个实际场景操作绑定到完整、受检查的 `runtime.Engine`。原 API1 视口射线求交和最近可见网格拾取仍完整运行，PyMel 仅有的 `PyNode.isIntermediate/isVisible/select` 使用实际 Maya cmds 替换，不需要安装 PyMel。

## 接口与输入

`ShapeAnimationTool` 继承 `BaseMayaTool`；正常用 `run(dry_run=False, **kwargs)` 或未来注册后的 `maya_toolkit.execute_tool`。`parameters_schema` 可导出 OpenAI/MCP。`validate` 和 `dry_run` 只读取节点、拓扑、曲线及元数据；不建会话、不改时间、选择、Undo 队列、不加载插件、不打开窗口。

| action | 输入及行为 |
| --- | --- |
| `status` | 默认操作，返回会话、全部层及待完成雕刻；不写场景 |
| `add_mesh` | `mesh` 为唯一整网格/transform，省略时必须恰好选一个；创建新层，可在同一网格加多层 |
| `set_key` | `layer_id`，可给有限 `frame`；已有该帧则不重复建目标；采样、成对目标和完整动画权重图 |
| `begin_sculpt` | 层及可选帧；必要时先建 key，创建可编辑网格，将其 worldMesh 连接到正目标；持久待完成状态 |
| `end_sculpt` | 按记录的网格 UUID 完成雕刻；删除自己的编辑网格时 Maya 将目标几何保存在 blendShape 中；恢复原 LOD 可见性、选择和工具上下文 |
| `reset_shape` | 仅在待完成雕刻中使用；禁用本层取基准，通过原完整临时 blendShape→权重一→仅烘焙自己的编辑网格历史→清理基准的流程复位 |
| `delete_key` | 可选帧；逐对重连自己的临时目标并 remove target，删除自己的负权重与曲线，再移除该帧其他曲线 keys；没有该帧则无操作 |
| `delete_all_keys` | 同样的完整成对删除流程；保留空层的 blendShape，可继续建 key |
| `set_enabled` | 必须给布尔 `enabled`，修改本层 envelope；原网格其他层保持 |
| `step_key` | 必须给 `direction=prev/next`；按实际曲线关键帧跳转，到边界停留；时间变化属于操作结果 |
| `remove_mesh` / `remove_all` | 删除指定/全部层拥有的 blendShape 和驱动，保留原网格及外部同名节点；全部层预检后才开始删除 |
| `inspect_legacy` | 默认读 `legacy_node=sat`；只读受限读取旧 pickle，检查旧层及成对权重图，不接管 |
| `adopt_legacy` | 备份场景后显式给 `accept_legacy_ownership=True`；仅允许空候选会话接管独占旧 deformer/曲线/mult，旧网络不改、不删除；启用负权重支持；不隐式迁移 |

有多个候选 network 必须显式指定 `session`（UUID 或唯一网络名）。`layer_id` 是 `add_mesh` 返回的持久 id；省略时使用当前层。返回 `ToolResult`，`data` 含 session UUID、节点名、全部层记录、配对 key 的帧/权重索引/曲线与乘法器 UUID，以及 `editing`（网格 UUID、原帧、原 LOD、选择与上下文）。未知、不适用参数或 NaN/布尔 frame 明确拒绝。

网格必须为非实例化、非引用、可写的单可见 mesh transform，无子 transform；不改变 skin、其他层等上游变形器。记录顶点数与完整面连接拓扑 SHA；更改原网格或编辑网格拓扑会拒绝后续写入。禁止锁定、外部重接、共享目标/权重/曲线驱动、非时间曲线和未知目标。支持整层曲线一起 retime，只读解析各曲线的单个 unit key 得到真实帧；任意不一致帧、非零/一 keys 或手工未登记目标需要先 Undo 恢复，不能猜测要删除哪个目标。切线编辑允许，插值可能过冲，需真人观察。

## 使用示例

在 Maya 备份场景中通过候选 `launch_candidate.py` 加载。正式示例在验收晋级后为：

```python
from maya_toolkit.tools.shape_animation_tool import ShapeAnimationTool
tool = ShapeAnimationTool()
added = tool.run(action='add_mesh', mesh='|rig|body_GEO').data
args = dict(session=added['session'], layer_id=added['added_layer'])
tool.run(dry_run=True, action='set_key', frame=1, **args)
tool.run(action='set_key', frame=1, **args)
editing = tool.run(action='begin_sculpt', frame=10, **args)
# 在真实 Maya 中雕刻 editing.data['editing']['sculpt'] 对应的网格。
tool.run(action='end_sculpt', **args)
tool.show_ui()
```

完整原窗口保留 Add/Pick/Remove、多层清单及 envelope 勾选、Key/前后帧/Del key/Edit、Artisan、ShapesBrush、Vertex、Reset、删除全部层/keys、画笔属性、主页和 About。Qt6 使用 PySide6/shiboken6，Qt5 使用 PySide2/shiboken2；不创建 QApplication，独立 mayapy 明确拒绝呼出 UI。构造器不再在 import 的默认参数中包装主窗口指针。接口加载完全不导入 Maya/Qt，`run` 沿用框架的 Maya 初始化行为。

## 状态、影响及行为修复

会话为独立随机命名的 network，JSON 数据可随 `.ma` 保存重开；deformer、权重驱动和暂存网格都有所属会话 UUID/角色。不依赖 `sat`、`shape_1`、`shape_1_mult` 等全局名称；实际形状路径通过 DAG 查询，不拼 `transform+'Shape'`，嵌套命名空间/重命名/同名对象不误认。创建/删除不会覆盖其他工具的数据。不同层可独立启停、删除；负基准保证采样上游形状后添加差值，父变换与缩放的基本案例已在隔离 Maya 验证。

每个场景写入 API 调用一个 UndoChunk；雕刻期间的手工笔刷/顶点编辑是其各自 Maya Undo 操作，开始、完成、Reset 是分开的调用。成功结束删除的是自己的暂存网格并保留目标数据。失败会清理已追踪临时副本并恢复临时 envelope、时间、选择、namespace、autoKey；不会自动 Undo 已写目标/曲线。发生中途异常要读 Script Editor 并 Undo 该调用后重试。暂存网格若新增外来子节点或历史，拒绝删除并保留供用户处理，避免误删。

开始雕刻保留其目标帧与编辑选择；`step_key` 保留跳转时间。其他常规写入恢复操作前时间/选择；完成雕刻恢复开始时选择和工具。场景写入本身不导出或覆盖任何文件；API 不消费额度、不安装依赖、不加载额外插件。离线保存重开检查只写测试临时目录。

旧源 UI 的 Edit 菜单只 setChecked、不调用 clicked；时间回调仅切按钮状态而未一致完成编辑。候选修复为 Edit 菜单直接调同一个完整操作；时间回调只读同步，换帧提示待完成状态，由 Edit、API `end_sculpt` 或关闭窗口明确完成，Undo/时间事件不会隐式写场景。原全局 timeline press/release 回调不再覆盖；使用窗口自己的 timeChanged scriptJob，关闭时清理该 job 和独有拾取 context。

原 pickle 在 Python3 把字节 repr 当字符串直接 loads 会失败；现会话用 JSON，旧 pickle 只支持普通字面值容器，拒绝 GLOBAL/REDUCE 所需类加载和持久引用。接管是明确用户选择，拒绝旧工具仍在编辑、共享驱动或无法识别的图；接管后继续使用候选，不再同时使用旧 SAT 修改同一层。

SHAPESBrush.mll 与 `SHAPESBrush` MEL 未随原包提供，不自动下载或加载。仅已安装、已加载且 MEL 可用时启用对应按钮；缺少时仍保留 Artisan/Vertex/Reset 全流程。原开发 helper `compileUI` 需要未提供的 `.ui`/pysideuic；现成生成窗口已完整交付，helper 明确失败而不覆盖安装中的代码。原 Word 指出首次激活笔刷需多次点击，此环境问题仍待真人核查。

## 复用、组合与验证

直接复用正式 `BaseMayaTool`、`ToolResult` 和框架 Undo；现有 core/正式工具没有同类成对修型/雕刻引擎。UUID 所属及临时几何与目标对管理属于此套件的业务，本轮不改 core。可先由动画工具准备时间和上游动画，再添加修型层；输出 mesh 继续由常规导出流程使用。与其他工具在同一 mesh 的变形器顺序、皮肤及层权重需真实备份场景验收，不把静态相邻依赖称为已验证组合。

检查：2 项普通 Python 契约/全资源指纹检查；8 项隔离 Maya2025 mayapy，覆盖 dry/import、完整几何修型与关键帧/Undo、Reset/删除/外来同名保留、UUID 重命名/共享驱动拒绝、失败恢复、旧场景接管、父变换/缩放与曲线 retime、两层及待完成雕刻保存重开；未来临时正式布局导入/注册/面板入口检查。GUI/真实笔刷/视口拾取/production skin、参考体/所有旋转轴和旧 Maya 版本均未验收。

真人步骤见候选根目录 `acceptance.md`。逐项实测通过后，用预制 `promotion.json` 和 `plans/staging_run/promote_candidate.py` 搬完整目标代码/原资源、文档、测试并插入 `ALL_TOOL_CLASSES`；本轮只检查预览和临时未来布局，不修改正式库。
