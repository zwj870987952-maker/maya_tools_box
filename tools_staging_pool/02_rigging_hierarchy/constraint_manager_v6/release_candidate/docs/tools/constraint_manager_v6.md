# 约束管理 v6 候选

`tool_id=constraint_manager_v6`，类 `ConstraintManagerTool`，分类 `rigging`。两份自有原型 `约束管理v6.py`（1681 行）和 `重建约束.py`（201 行）原始字节归档到 `vendor/*.original`，SHA256 与原声明表见 `catalog.json`。完整四个 UI 类、全部原方法及辅助脚本八个函数保留为候选代码镜像；无原 `__main__` / 顶层启动。面板实际使用 `ui.py` 的完整原界面子类与安全回调，不使用旧辅助脚本固定 `%TEMP%/constraint_info.json` 的隐式覆盖读写。

继承 `BaseMayaTool`、完整 Schema、`validate/execute`、继承 `run` 返回 `ToolResult`、`show_ui` 与单次晋级文件/注册清单已备齐。没有修改正式库或注册表。真实 Maya GUI 验收 **not_run**。

## 保留的功能与修正

完整界面保留刷新/添加/清空、约束节点/权重模式、0/(1)0/1/自定义权重、是否打键、颜色、条目分组、保存/加载列表、右键移除目标（含保持偏移）、设置静止位置、修改约束轴、约束对象/目标/节点选择、双击、工具提示、断开/恢复/反向/重建。Maya 2025 使用 PySide6/shiboken6，旧 Maya 可使用 PySide2/shiboken2；仅 `show_ui` 时导入 Qt 并创建 Widget，batch 明确拒绝界面，不自行建 QApplication。

原权重查找将 userDefined float/double 当权重、按名称中 `W` 拆驱动对象，并将 targets 转成 set。候选用实际 `targetList`、`weightAliasList`、物理 target indices 及 `.targetParentMatrix` 连接对应目标，保持顺序和 namespace；不会误写用户浮点属性，支持名称含 W 和长 DAG。原 UI 从这些真实数据建立列表，选择与 tooltip 的原业务继续使用。

原 `setAttr` 后不带值的 setKeyframe 对已有动画可能取旧曲线值。候选打键直接用 `setKeyframe(value=...)`；不打键模式拒绝覆盖已有驱动，普通独占 time animCurve 可明确写键，驱动/共享/锁定/时间扭曲曲线受保护。权重三模式与自定义值保持原意。

原断开通过删除节点，只存当前权重，恢复无法还原动画、skip、offset 或自定义属性。候选只断开原节点的约束输出，保留原 UUID、输入连接、全部动画和设置，再恢复精确 UUID/属性端点；新驱动出现时拒绝强制覆盖。Python 会话快照可另行导出/导入，不把它当 Maya Undo 数据。

原反向两分支仍然用 target 驱动原 child。候选真正将原被约束物体作为 source，分别驱动每个原 target，先断开原输出避免双向环；原节点保留，恢复时仅删除带本次 owner UUID 标识的逆向节点，再接回原输出。只支持原 parent/point/orient/scale/aim 反向类型；有关联 DAG、已有受影响动画/驱动、offsetParentMatrix 驱动、相关依赖环或锁定节点时，在任何改动前拒绝。原方向动画保留，逆向节点以当前姿态和显式 `maintain_offset` 创建，原动画不是自动转移到逆向关系的烘焙。

重建通过 duplicate 原约束及 inputConnections，在删除旧节点前保留输入动画、所有 target 及偏移、skip 输出连接、自定义属性、插值等完整状态，连接全部原输出后再删除旧节点。返回实际新名和 UUID，原 UUID 会改变；一条 Undo 恢复原节点。既有输入动画曲线不复制或删除。原 UI 列表同步实际重建结果，不按字符串猜创建名。

场景列表使用 locator `.notes` 的 JSON，避免长 DAG 中 `|` 与旧分隔符冲突，保留颜色和权重信息，能读取旧列表格式。新列表名称不能覆写既有场景数据；需保存新版本时用新名称。列表只是呈现信息，不把失效名字自动映射到其他对象。完整原辅助四按钮另有显式 cmds 面板，增加快照路径选择；回调为 callable，不再依赖 Script Editor 的全局函数字符串。

## 接口

| 参数 | 含义 |
| --- | --- |
| `action` | inspect、weights、disconnect、restore、reverse、rebuild、delete、remove_target、rest、axis、save_list、export_snapshot、import_snapshot |
| `objects` / `constraints` | 明确有序完整节点；约束优先，否则由对象或当前选择发现相关约束。拒绝组件、通配符、重名和实例；写节点/目的通道锁与引用全批预检 |
| `selected_weights` / `all_weights` | 真实 target alias 或物理 weight plug。`selected_one` 的全部列表明确作为写范围，选中项 1、其他项 0；其他模式只写选中项 |
| `mode` / `value` / `keyframe` | zero、one、selected_one、custom；有限自定义权重，默认打键 |
| `maintain_offset` | 反向和移除目标保持偏移选项，默认 true；原轴功能恢复全部轴并使用该偏移选项 |
| `list_name` / `items` | 新场景 locator 列表名称，普通文字/颜色/节点/权重的数据行 |
| `path` | 快照 JSON 显式路径；新文件拒绝覆盖，限制大小与结构，不执行内容 |

`inspect` 返回约束类型、UUID、真实 child、按原顺序的 targets/alias/index/当前权重、输出与全部输出连接。非写 API 输出包含预检数据；操作输出包括变更权重、断开记录、逆向节点 UUID、重建原/新名和 UUID、列表 locator 或文件路径。Schema 由框架导出 OpenAI/MCP，不接受任意 Python/MEL。

```python
tool.run(dry_run=True, action="inspect", objects=["rig:driven"])
tool.run(action="weights", selected_weights=["rig:driven_parentConstraint1.driverW0"],
         mode="custom", value=0.5, keyframe=True)
tool.run(action="disconnect", constraints=["rig:driven_parentConstraint1"])
tool.run(action="restore", constraints=["rig:driven_parentConstraint1"])
tool.run(action="rebuild", constraints=["rig:driven_parentConstraint1"])
tool.show_ui()
```

例中别名只是说明：先从 inspect 取得实际 alias，不手写猜测。

## 作用、条件与复用

预检/dry-run 不修改 scene、selection、time、Undo、MEL、UI、快照或文件。API 写操作用 Base 的 UndoChunk，全批预检后才执行；finally 恢复时间、选择 UUID、AutoKey 和 namespace。部分异常不自动 rollback，检查现场后执行一次 Undo。Python 快照不参与 Undo，恢复始终重新检查原 UUID、目标顺序和当前连接，不信任失效会话状态。

快照恢复只接受原 constrained 直接通道，或仍连接原 child 同通道的 pairBlend；不允许导入 JSON 任意接线，也不按名字删除其他约束。所有逆向删除节点必须携带匹配 owner UUID。外部快照保存使用独占新文件，不覆盖别人的临时 JSON，不能用 Maya Undo 撤回；没有文件自动写入或后台快照任务。

原静止位置/轴操作保留 Maya 原生 MEL 菜单行为，且仅交互 Maya 中执行。读取本机 Autodesk 菜单脚本后纠正了把 `maintain_offset` 误传为 version 的问题；轴操作只选 child，避免原代码连 driver 也修改；菜单会处理同 child 的全部约束，需明确包含这些约束。未冒充 batch 菜单实测。高级几何/法线/切线/极向量/pointOnPoly 类型及生产 rig 的特殊连接需逐项 GUI 验收。

复用正式框架和 `core.context.UndoChunkContext`，未重复建立调度/Undo 系统。输出 UUID、目标列表、真实权重可供用户明确选择的后续绑定/层级工具消费；跨工具自动组合未实测。

## 检查与验收

普通 Python 检查两源散列、全部 UI 类/方法与辅助八函数完整性、无原自动入口、参数/列表格式。隔离 Maya 2025 实际检查 namespace+名称含 W 的目标顺序、三权重模式/自定义值和真实曲线 value、单次 Undo、断开/恢复保留 UUID/偏移/键及新驱动拒绝、每个目标的真正逆向/运动/恢复、完整重建/输入曲线/自定义属性/插值、精确移除目标、JSON 彩色列表、快照导出/导入及拒绝覆盖。另有正式布局注册/Schema/分类/面板检查。

真实 GUI 全部功能、颜色切换/长名保存往返/双击/tooltip、反向多约束复杂图、各约束类型、Maya 多版本、原静止位置和轴菜单 **not_run**。见 `acceptance.md`，验收通过前不迁入正式库。
