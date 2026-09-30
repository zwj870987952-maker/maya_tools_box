# BRS Locator Transfer 候选

`brs_loc_transfer` / `animation` / `LocatorTransferTool` / 1.09-adapter。状态 prepared_unverified，真实 GUI not_run。原作者 Burasate Uttha (DEX3D)，原单文件完整字节归档，未附独立 license，仅本地私有整理。十七原函数均有候选对应入口，增加显式 build_ui；六算法 helper 的 AST 除 guard 外一致，完整创建/回写/guide 流程循环保留。原 UI 四按钮、选项、折叠布局和配色保留。

原文件导入时创建 UI，showWindow 时尝试联网下载并 exec 远程 support.py，关闭 cycleCheck、重置视口。候选取消导入执行/远程执行/cycleCheck 改动；不安装、不下载、不写外部文件。只通过标准 API 操作，原始入口归档用于审阅，不应 source/runpy 它。

## 调用和参数

候选加载见 acceptance.md。验收晋级后才能 `maya_toolkit.execute_tool('brs_loc_transfer', arguments, dry_run)`；当前正式库没有注册。复用 BaseMayaTool/ToolResult/UndoChunk，面板靠注册合并，不新增 core。原通用 snap/bake 只作为本候选私有实现，不未经直验改正式共享库。

| 参数 | 默认 | 含义 |
|---|---|---|
| action | inventory | inventory/open_ui/create/apply/create_guide/redirect |
| objects | [] | create/apply 明确 transform/joint 数组，空读取选择；guide/redirect 从 owned group 推导 |
| annotation | true | 创建时保留原 annotation；false 不创建 |
| constrain | true | create 完成后用 locator 的 point/orient constraint 驱动控制器 |
| bake_all | false | false 保留原时间键集合；true 保留每整数帧 bake 并把新增键标 breakdown |
| in_timeline | false | 仅 create：true 使用 round(playback min/max)，false 使用 round(原键min/max) |
| translate | true | Position 约束开关 |
| rotate | true | Rotation 约束开关 |

参数必须真实 bool，拒绝未知、重复、组件、通配符和歧义。create 原来仅处理 TR 六通道拥有多个不同时间键的对象，零/一时间键跳过并返回 skipped；全跳过不创建空组。初次 group 用输入对象位置 pointConstraint 对齐，rotateOrder=3，TRS 锁定。定位器最初始终复制六 TR，不因 Align 少选而仅复制部分通道。

create 的 constrain=False 可只读复制引用控制器动画；开启约束则目标引用/节点或写入通道锁定/外部驱动拒绝。apply 拒绝引用、六 TR 锁定/外部驱动/外部约束。Maya 自动生成的本候选 blend 允许，复杂混合和制作 rig 仍需人工复验。原 keepKeyframe/snapKey 未限制通道，会影响额外动画属性；候选对含额外动画属性的 apply 明确拒绝，请使用仅六 TR 的副本，不静默改写这些键。

## 原动画算法与重要边界

- getAllKeyframe 合并 tx/ty/tz/rx/ry/rz 的全部时间键；breakdown None 修为 []。
- bakeResults 保留原 sampleBy=1、disableImplicitControl=True、preserveOutsideKeys=True、sparseAnimCurveBake=False、六 TR，随后 filterCurve。边界用 Python round，半帧遵循原舍入，而非保证保留小数关键帧。
- bake_all=False 将原时间 round 成集合，在区间 `[min,max)` 删掉非集合整数键，恢复 breakdown；true 把新整数键加到 breakdown。范围外键保留，但小数键/切线/密度不能保证与原曲线完全相同。
- apply 先在 locator 键 min/max 范围 cut 掉目标六 TR 的旧键，清理自己的约束，按 Position/Rotation 创建约束，然后仍 bake 全部六 TR。即使只选 Position，旋转旧键仍可能被删/重建；Align 不是通道删除/烘焙掩码。最后原 snapKey 对选中对象执行 timeMultiple=1.0，包含范围外动画键的时间取整风险。
- guide 流程保留：选组内 locators → 缓存世界动画到不入组的临时 locators，强制约束 → group snap 到 guide → bake 回原 locators → 删除 guide → 锁回 TRS。**隔离简单平移观察 group.tx 从0变10，但第1帧 locator worldX 仍0；不能声称它把整体动画平移了10。** 这是原顺序的世界动画保留行为，未擅自修改算法；真实重定向意图需人工验收，若不满意修候选再验。

## 所有权、Undo 与状态

group/guide/locator/shapes/annotation/创建的约束与 auxiliary 节点带 Owner/Role。locator 有目标 UUID 和 message，场景保存/Undo 后可重建对应关系；目标/定位器/组重命名依然可回写。固定同名外部对象拒绝，自己的 locator 可以安全替换；Maya 返回实际唯一名并在 parent 后更新路径，不按原拼接名字误认同名对象。

删除仅作用于 owned locator/guide/空组和 owned constraints。外部后代/输出消费者、目标 message 被改接拒绝；约束先脱离控制器再删，保护空 transform。原 blanket deleteConstraint 和静默异常吞掉替换为 owned 检查/明确错误。Maya 新 blend/pairBlend 节点可能保留承载旧动画，returned retained_blend_nodes 供观察，不强行全删。

validate/dry_run 只查询，返回 eligibility 等计划，不导入原 legacy 或开窗/写场景。执行使用标准 UndoChunk，finally 恢复时间、组件选择、refresh suspend、GUI OGS pause 和既有 group 锁；原 resetViewport 改为无全局重置。失败不自动回滚部分已创建定位器/键，检查并 Undo。没有文件输出/联网/evaluation 或 cycleCheck 改动。GUI 状态文本保留，省去全局 mainProgressBar 依赖，不声称 headless 创建了真实界面。

## 输出、组合和验证

inventory 返回原函数、SHA 和变动审计；open_ui 返回 window。动作返回 action、created_nodes、locators、group、guide、skipped、retained_blend_nodes、warnings。角色列表反映当前场景中本候选辅助对象，可包括其他已创建批次。结果不代表真人 GUI/制作 rig 验收。

推荐副本流程：create → 编辑 locator 动画/位置 → apply → 检查原控制器曲线和 Undo。create_guide/redirect 为独立待验的原流程，不作为已验证整体重定向推荐。调用共享框架并可在人工确认后接其他导出/动画工具，但没有验证跨工具生产组合。

普通 Python 三项通过：完整来源/十七对应函数/导入无执行且无远程exec；六 helper AST 保留；严格参数/Schema/无 Maya inventory。Maya2025 隔离八项通过：稀疏/dense/timeline/breakdown/annotation/跳过，真实编辑后回写/约束清理/Undo，只读与外部对象保护，重命名/保存重载 UUID，完整 guide 流程及上述 world observation，故障状态恢复，额外动画/外部约束/message 改接拒绝。

原 GUI、视口反馈、复杂层/blend/引用控制器读复制、旋转大角度、小数帧/切线、Position-only 和真正重定向制作结果仍需人工。完整代码/原资源/两测试/文档/注册已列 promotion.json；真实当前哈希验收通过才能迁正式库。
