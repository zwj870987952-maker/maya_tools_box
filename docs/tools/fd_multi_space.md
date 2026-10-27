# FD Multi Space 候选知识说明

工具 ID `fd_multi_space`，领域 `animation`。原作者 Filippo Dattola，2023，All Rights Reserved；RTF 说明要求商业使用、修改和再分发取得作者许可。本候选仅整理用户已有副本供私有本地检查，不公开发布，不对授权状态作推断。原 3 个 Python 文件与 RTF 共 4 个资源按字节和 SHA256 保留在包内 `upstream`；原 GUI 的主窗口/两种三步流程完整对应候选 UI，原顶层自动弹窗和依赖 Maya scripts 全局 import 取消。

## 用途与两种算法

在控制器上新增 keyable double 自定义属性（min=0,max=1,default=0），该属性连接 driver 对控制器父级的 parentConstraint 权重。

- `local` 对本地 driven 调用原 `group(driven)` 和 `xform(centerPivots=True)`，插入空间组，再 `parentConstraint(driver,group,maintainOffset=True)`。
- `reference` 使用 driven 既有父级，不插组；`parentConstraint(driver,parent,maintainOffset=True)`。它也可处理普通本地父级。“reference/open file”是原模式名称，工具不会打开、保存、导出或切换 Maya 场景。

多次为同一 driven 添加不同属性/driver 时，复用本候选已记录空间组和自有约束，通过 Maya parentConstraint 编辑添加新 target，保留 maintainOffset。属性接到目标 UUID 对应的 weightAlias；不再用原 `listAttr[-1]` 猜测属性，不使用 `force=True`。全部权重为 0 的静止行为与 Maya 原 constraint 求值有关；不是自动匹配姿势或无跳变切换算法。多个非零权重会由原 parentConstraint 归一化混合，不创建互斥/切换表达式。

## 接口、输入和输出

调用 `MultiSpaceTool.run(dry_run=False, **arguments)` 返回 `ToolResult`。

| 参数 | 作用 |
| --- | --- |
| `action` | `records` 查询来源；`open_ui` 两种完整窗口；`create` 一次执行全部三步；`prepare` 第一阶段；`add_driver` 第二阶段；`connect` 第三阶段 |
| `mode` | `local/reference`，阶段二/三从来源记录恢复实际模式 |
| `driven`, `driver` | 明确唯一 transform/joint 名称或绝对 DAG 路径，不接受组件、通配符；API不会靠当前选择猜对象 |
| `attribute` | 合法尚不存在的自定义属性名称，默认 space，阶段二/三从记录恢复 |
| `record_id` | prepare 输出的本地来源 network UUID，保存重载或重命名后可恢复下一阶段 |
| `allow_reference_edits` | 默认 false；引用 control/parent 只在 reference 模式且本次显式 true 时允许 addAttr/连接/约束引起的 reference edits；local始终拒绝引用重父级 |

结果含 `record_id`、`phase` (1/2/3)、`driven/parent/driver/constraint/group`、模式和属性。来源使用私有 Owner network/message 和辅助 Owner 标记；对于引用节点，比较 UUID 同时加入 referenceNode UUID，避免同一文件加载为引用后与原场景节点 UUID 重复。消息用于实际对象定位；本地来源记录 UUID不因重命名变化。阶段一/二半成品可以用相同 record_id 继续，不重复加属性/target。

## 只读预检与场景影响

`validate`/`dry_run` 不创建节点/属性/UI，不修改选择、时间、Undo、AutoKey。拒绝属性重名、锁定/未经允许的引用编辑、实例 transform、同 driver 重复、driver处于受约束层级下造成循环、已存在的外部父级驱动/约束、不属于本候选的同名空间组，以及被改动的自有 target、权重连接、父级和辅助来源。此预检较保守，约束/动画层/复杂混合图不保证兼容，不覆盖旧制作图。

`create` 的全部三步为一个标准 Undo chunk；GUI 的每个原三步按钮各为一个 chunk。失败不自动回滚局部改动，先 Undo 再检查；半成品仅在相应完整阶段成功时可继续。local改变DAG层级、group pivot、可能改变控制器的局部变换/动画求值；reference操作既有父级，可能影响该父级下所有控制器/子树。因此在备份场景对比动画，再使用生产 rig。引用 edits 不等于只读操作，默认拒绝，允许后需真人核验引用保存/重载。选择按对象身份恢复，时间/namespace/AutoKey finally恢复，Undo全程开启。

候选不提供自动清理/删除属性与组，避免制作图被误删；创建后用 Maya Undo/Redo恢复。若已经保存并进行了后续动画编辑，应在备份中检查完整来源/连接后人工移除，不能假设删除 network 就等于撤销工具。原文件不会被改写，无外部文件业务写入。面板创建不归场景 Undo。

## 示例与组合

```python
tool.run(dry_run=True, action='create', mode='local', driven='rig:hand_CTL', driver='world_CTL', attribute='worldSpace')
result = tool.run(action='create', mode='reference', driven='rig:hand_CTL', driver='world_CTL', attribute='worldSpace', allow_reference_edits=True)
first = tool.run(action='prepare', mode='local', driven='hand_CTL', attribute='followChest')
tool.run(action='add_driver', record_id=first.data['record_id'], driver='chest_CTL')
tool.run(action='connect', record_id=first.data['record_id'])
```

输入为控制器/driver/权重名称，输出为可动画的空间属性和完整 provenance，可接关键帧工具给新空间属性打键；创建后检查世界姿势后再镜像/烘焙。这里只说明数据衔接，未承诺跨工具组合实测。只复用现有 BaseMayaTool/ToolResult/Undo，不改生产 core、注册或正式目录。

## 检查与晋级

普通 Python 验证资源字节/两模式目录、Schema/延迟导入；Maya 2025 隔离 mayapy 验证本地权重数值/双target共享约束、三步保存重载/改名/后加属性明确alias、真实文件引用编辑与UUID冲突、读预检/循环/锁/外部驱动保护、Undo/Redo与故障finally。实际GUI、生产rig、不同旋转顺序/父级非均匀scale、复杂引用/动画控制器待真人验收。源声明 Maya2018/Python2兼容未经复验，候选以当前框架支持环境为准。

`promotion.json` 包含完整目标代码/资源/知识/测试和 `ALL_TOOL_CLASSES` 注册与面板动作；真人按 acceptance.md 验收前不能迁入正式库。
