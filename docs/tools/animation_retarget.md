# 动画重定向（animation_retarget）候选说明

本工具源于用户自有 `动画重定向.py`，原文件按字节完整保留在 `upstream/`，不是公开许可第三方套件。候选包镜像正式目录，界面和业务已经适配，仍须在真实 Maya 中逐项验收后晋级。导入包不会创建界面、修改场景或注册到正式工具库。

## 用途与完整能力

给定源对象和目标对象配对列表，按每对的四种通道模式传递动画。原界面的录入、清空、文本编辑、拖动排序、双击选对象、彩色圆点循环模式、右键批量改模式和删除全部保留；对位、默认/智能烘焙、保存/读取 JSON、从场景信息加载、应用姿态均接入标准 API。新增“只读预检”按钮。Qt 组件和 Maya 主窗口使用现有 `maya_toolkit.core.ui_base`，支持 PySide2/PySide6 的导入与菜单适配；GUI 行为需实测，未在 mayapy 创建窗口。

## 调用与参数

继承 `BaseMayaTool`，`tool_id=animation_retarget`，领域 `animation`，版本 `1.0.0`。实现 `validate/execute`；通过 `run(dry_run=...)` 调用，输出 `ToolResult`，Schema 可由 `to_openai_tool/to_mcp_tool` 导出。晋级后亦可用 `maya_toolkit.execute_tool`。

| 参数 | 说明 |
|---|---|
| action | align（默认）、numeric_copy、bake、load_scene、restore_pose、save_config、load_config |
| pairs | 数组，每项 source/target/modes；兼容旧 text="源 , 目标"。空数组仅适用于配置、加载场景和恢复所有记录 |
| modes.translate/rotate/scale | constraint（默认）、numeric、none |
| modes.other | numeric、none（默认），不能设 constraint |
| start/end | 同时提供有限数字，start≤end；省略时使用播放范围的整数边界，保留原脚本行为 |
| smart | 布尔，默认 false，仅 bake 使用；true 采用原脚本 smart bakeResults 参数 |
| path | save/load_config 的包外绝对 .json 文件路径；保存只创建新文件，不覆盖 |

`align` 创建保持偏移的 point/orient/scale 约束（不是吸附到源位置），在添加约束之前保存源与目标姿态，然后执行 numeric 模式的关键帧复制。`numeric_copy` 可独立复制，不创建姿态记录或约束。所有 numeric 操作使用所选源对象关键帧时间的并集，范围内每个源帧均采样所有 numeric 配对；无源关键帧就不写目标关键帧。支持小数帧。TRS 各轴逐一复制；other 只复制源自定义可关键帧的数值标量与复合数值子通道，目标必须已有对应属性，不自动建属性。字符串、缺失或不适合关键帧的属性返回 warnings。

`bake` 仍像原脚本一样烘焙目标所有可烘焙属性，none 模式不会限制烘焙通道。默认调用 simulation=True；智能调用原 smart 参数，无原脚本 `cmds.mel` 的错误后备调用。烘焙成功后只删除记录为本候选所有且仍连接原目标的约束；旧 Constraint_SelectionSet 及其他工具约束不删除。信息节点继续保留以供加载和恢复。

`load_scene` 返回配对及模式，只读。`restore_pose` 空 pairs 恢复所有信息记录，提供 pairs 只恢复所选记录；源与目标均恢复。锁定、驱动、不匹配类型或不可恢复属性在 skipped/warnings 中列出，不声称完全恢复。新姿态是类型化 JSON，支持数值、字符串、数值向量和矩阵；连接/message、数组等特殊属性不存储。旧 Rematch 字符串序列化只作有限兼容，含逗号/冒号的字符串或复杂类型无法完整恢复。

save/load_config 保存旧格式列表 JSON，保留 modes，兼容 UTF-8 BOM，载入严格检查结构；文件参数不要求场景对象存在，可在别的场景先加载配置。保存前和写入时均保护文件碰撞。写入/读取错误返回失败；新文件若写入中失败可能残留部分内容，需检查后另存。文件写入不能由 Maya Undo 撤回。

## 检查与影响

validate 与 dry_run 只查询场景、文件及配置，不创建节点、关键帧、约束、不执行 Qt、不更改选择和时间。拒绝不明确名称、组件/通配符、自配对、重复目标、调用中的循环配对、祖先/后代约束、锁定目标通道和已有非 animCurve 驱动；约束引用目标需先转副本。Undo 必须打开。预检不是对所有约束网络的全面循环求解器，仍须在副本观察复杂绑定的效果。

每次写场景调用由框架分组 Undo。执行恢复调用前的时间与选择，即使中途异常；不设置评估模式、不暂停刷新。框架不在失败时自动回滚，报错可能留下已执行部分，用户应按一次 Undo 撤回整次场景修改。读取/配置操作也沿用标准 run 的 Undo 包装，但外部文件不属于场景 Undo。

新 metadata 是带所有权标记的 network 节点，不占用或改写原 Rematch 组。源/目标/约束都按 UUID 追踪，重命名后仍能找到，删除后同名替身不会冒充原约束；UUID 缺失或损坏的记录会拒绝继续，需要在副本修复/删除明确属于本工具的记录。约束同时校验本候选所有权、pair_id 和输出目标；重接后的约束拒绝自动删除。旧 Rematch 记录只读，不自动转换或删除旧约束。没有共享全局约束集合。已存在候选约束时禁止再次 align 同目标，先 bake/Undo。

输入为 transform/joint 节点、已有匹配属性及源动画；输出包含 constraints/info_nodes、frames/keyed、targets/deleted_owned_constraints、pairs、restored/skipped 和 warnings，随 action 不同。场景影响有约束、network、关键帧、动画曲线和恢复属性；文件影响仅用户明确给出的新 JSON 配置。

## 示例与组合

```python
tool.run(action='align', pairs=[{'source': 'source_CTRL', 'target': 'target_CTRL',
    'modes': {'translate': 'constraint', 'rotate': 'numeric', 'scale': 'none', 'other': 'numeric'}}])
tool.run(action='bake', pairs=[{'source': 'source_CTRL', 'target': 'target_CTRL'}], start=1, end=120, smart=False)
tool.run(action='restore_pose', pairs=[], dry_run=True)
```

先用场景管理/命名工具准备明确的对象，再用此工具复制或烘焙，之后可用动画滤波工具处理目标曲线。此处是接口上的衔接说明，未验证跨工具真实 GUI 组合。不能把 mirror/layer 的结果直接当成已验证的重定向输入；需核对目标连接、层及时间范围。

## 演进、验证与晋级

原实现 PySide2 固定导入、UI 内直接写场景、Rematch 属性名拼接 DAG/命名空间、姿态逗号/冒号序列化、默认烘焙删除全局约束集合；候选拆分完整业务与 UI、复用 core Qt/Undo，使用 UUID 所有权与类型化姿态、只删除选中目标的本候选约束、时间/选择 finally 恢复、严格预检、文件不覆盖。源帧并集、maintainOffset、模式默认值和 bake 参数保留；姿态快照提前、other 复合属性正确拆子通道、保存不覆盖、烘焙不删除旧集合属于明确行为修正。

tests/test_animation_retarget.py 是普通 Python 检查，tests/test_animation_retarget_maya.py 只允许隔离 runner，使用一次性 Maya 场景测试实际约束、关键帧、默认/智能烘焙、Undo、UUID、JSON 姿态和旧信息兼容。没有把 GUI 或复杂真实绑定视为通过。最终结果见 manifest 和 animation_retarget_mayapy.json。源码校验值和 UI 完整能力目录在 catalog.json，UI 逐行变化附 diff。

promotion.json 预制整个包、原文件、说明及两个测试文件到正式目标路径，以及 AnimationRetargetTool 导入/ALL_TOOL_CLASSES/__all__ 注册；面板按注册表读取，无需另写面板业务。晋级脚本合并当前注册表并要求当前候选哈希和真人验收记录。人工验收步骤见候选根 acceptance.md。
