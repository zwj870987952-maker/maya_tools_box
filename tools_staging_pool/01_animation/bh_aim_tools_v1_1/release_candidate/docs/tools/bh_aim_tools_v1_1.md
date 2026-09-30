# bh_aimTools v1.1 候选知识说明

通过独立 Aim Locator 编辑控制器朝向：创建定位器、放到合适位置、按现有关键帧或每帧附着、建立 Aim、编辑定位器动画、烘焙回控制器。完整原16过程和窗口保留，另加一个参数读取过程。英文 MEL、中文版本、图标和 ReadMe 四个文件按字节归档。

原 ReadMe 是购买工具的使用说明，明确要求不要分享；本候选只作本地整理，不声称再分发授权，不发布原资源或改编代码。实际窗口/生产绑定尚未验收，候选不迁入正式库。

## 接口与流程

BhAimTool 继承 BaseMayaTool，tool_id=bh_aim_tools_v1_1，category=animation，version=1.1.1-adapter；validate/execute 实现真实契约，run 输出 ToolResult 并使用现有 core/framework Undo。Schema 由 to_openai_tool/to_mcp_tool 导出，晋级后通过 maya_toolkit.execute_tool 调度。

| 参数 | 含义 |
|---|---|
| action | inventory（默认）、open_ui、create、attach、aim、bake、clear |
| objects | 明确对象名数组，默认空使用选择；create 输入控制器，其余场景动作输入本候选定位器；支持多对象，拒绝重复/歧义/组件/通配符 |
| keys_only | attach/bake 使用，默认 true；附着按控制器的键时间，烘焙按定位器的键时间（含小数帧）。false 使用播放范围整数帧逐帧 |
| delete_rotation_keys | 默认 false，仅 keys_only bake 可设 true；会删除控制器**所有时段**原 rx/ry/rz 键，随后只在定位器范围内键时间重建 |
| start / end | 同时提供整数，start≤end；省略使用播放范围整数边界。执行临时采用该范围，结束恢复原四个播放范围值 |

create 创建白色定位器，ctrl message 指向原控制器；成功后选择全部新定位器，便于移动和下一步。原件多对象创建只选最后一项，候选显式选择全部结果。attach 使用原保持偏移 parentConstraint，按源键时间/逐帧打定位器键，删除自己的临时约束并 filterCurve。aim 用原局部距离启发式选择轴、原 maintainOffset/worldUpObject 参数创建 Aim 和锁定 UpVLocator。该启发式的比较顺序保留，不作为任意坐标/骨架的“最大轴”通用保证。

bake 按原 SetKeyRotate、pairBlend 路由及 filterCurve 烘焙旋转，然后删除定位器、其辅助层级及本候选约束；成功后选择控制器。keys_only 的旧旋转键删除已改为显式参数，业务不弹对话框；原窗口仍在调用前给 Yes/No 选择，默认 No。clear 额外提供安全放弃定位器网络的接口，不烘焙，不删除控制器既有曲线。

inventory 返回来源/资源哈希、过程和变更目录；open_ui 返回原生窗口名与来源，只在实际 GUI 可用。场景结果包含 action、range、items，每项 locator_uuid、仍存在的 locator/controller 及 retained_blend_nodes；warnings 提示保留的 Maya blend 节点。原算法可能留下 pairBlend/控制器混合属性，候选不自动删除仍承载原曲线的节点，不把它们误认作无用垃圾。

## 无副作用预检与保护

validate/dry_run 不 source、建节点、加载窗口、改变选择/时间/范围、评估或缓存。已建立 Aim 不允许重复 Aim 或重新 attach。定位器必须携带本候选 UUID/所有权记录，ctrl message 必须仍连接记录控制器；原工具定位器不自动接管。keys_only attach 检查控制器键，keys_only bake 在任何删旧键之前检查定位器键。aim 拒绝与控制器位置完全重合的定位器。

涉及写入的控制器/定位器拒绝引用或节点锁定、相应通道锁定、外部约束/表达式/动画层/混合驱动；原 animCurve 允许，当前候选拥有的驱动允许。原指南建议编辑定位器动画；若建立 Aim 后给控制器新增键，Maya 可能在候选调用外创建新的 pairBlend，此时保护会拒绝操作，应 Undo 或在副本明确处理，不自动接管该节点。

UUID 元数据附在定位器，保存/Undo/重命名后仍可找到控制器与辅助节点；节点类型、Owner/token 和 UUID 共同校验，名字替身不能冒充拥有的节点。外部后代或新增外部输出消费连接会拒绝清理。attach 只删除本候选临时 parentConstraint；bake/clear 删除前先脱离控制器下本候选约束再删除，避免空控制器连带删除。临时 root locator 返回 Maya 实际生成名，防止与已有 _ROOTLOCATOR 撞名时删错；生成名称只用 DAG 叶名，保留 ctrl message 的长路径配对。

每次场景调用由 UndoChunk 分组。执行 finally 恢复当前时间、刷新暂停、评估模式、cache evaluator 开关、四个范围值和仍存在的选择；create/bake 成功选择其结果，其他动作恢复输入。不复制脚本、安装 Shelf、写外部文件。错误不会自动回滚；可能已部分修改，用户应 Maya Undo。已有记录的动作在异常时捕获拥有的部分节点、标 failed，允许 clear/Undo；create 若在完整创建/建立记录前失败，应 Undo，不声称所有残留都已可清理。

## 示例和衔接

```python
result = tool.run(action='create', objects=['head_CTRL'])
locator = result.data['items'][0]['locator']
# 在 Maya 中将 locator 移到目标位置后：
tool.run(action='attach', objects=[locator], keys_only=False, start=1, end=120)
tool.run(action='aim', objects=[locator])
tool.run(action='bake', objects=[locator], keys_only=False, start=1, end=120)
```

可使用 Maya motion trail 或定位器动画层调整目标，再烘焙控制器旋转，之后用滤波/导出工具处理曲线；生产场景中的动画层、复杂 pairBlend、引用绑定和跨工具组合尚未验证。不要将已有外部网络视为候选可安全删除的辅助节点。

## 完整性、验证与晋级

原所有过程/UI 保留，去除唯一顶层开窗，私有名称避免原 globals 冲突；四按钮走标准 API。明确改动有参数替代 checkbox/确认、actual unique 临时名、完整 all-frames pairBlend 变量声明、所有权清理和 runtime finally。逐行差异见 bh_aim_changes.diff；中文版本原样归档，运行入口使用英文原算法/UI。

普通 Python四项和 Maya2025隔离九项检查通过：完整17过程实际 source/来源/内部保护、创建和 Undo、两种附着、实际 Aim/旋转烘焙/单次 Undo、显式全时段旧键删除、外部后代/改接/约束拒绝、无副作用与故障恢复、长路径和临时名冲突、批量同叶控制器与场景重载。未创建 GUI，真实 rig、其他 Maya/平台、原轴选择、实际 motion trail/动画层和复杂 pairBlend 行为待真人。

首次旧键 fixture 在 Aim 后新增控制器键，生成外部 pairBlend，被预检正确拒绝；改为 Aim 前已有旧键，再在候选动作内捕获 Maya 新 pairBlend。批量同叶名 fixture 首次使用创建返回的歧义短名，两输入误指同一节点；改为确定长路径后通过。未把首次失败记作通过。

promotion.json 预制完整包、资源、专项说明和两个测试到正式目录，并合并 BhAimTool 导入/ALL_TOOL_CLASSES/__all__；临时正式布局验证不改当前正式库。真人流程见 acceptance.md，匹配当前候选哈希的真实验收记录后才可晋级。Git 属性关闭原资源和候选的文本换行转换，保持校验字节。
