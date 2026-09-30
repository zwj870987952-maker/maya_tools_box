# BRS Smooth Mocap 候选

`brs_smooth_mocap` / `animation` / `SmoothMocapTool`。prepared_unverified；真实 GUI/制作动捕资产 not_run。保留原 valueAverage AST（只增加入口 guard）、三邻点快照后提交、strength-1 循环、locator 驱动与六 TR 回烘。原 BRSSmoothMocap.py 完整字节归档，BRS Locator Transfer 来源原件/完整适配后端随包固定拷贝，Owner、组/guide/locator 名独立，不依赖待整理池或用户 scripts 目录。无独立再分发授权，仅本地私有准备。

原脚本导入时按 MAYA_APP_DIR/scripts 找 BRSLocTransfer.py 并 exec，依赖其 UI 选项、建窗，再对当前 root 弹 Yes/No 并执行；候选移除全部导入执行、scripts 读取、远程exec、自动场景写入与关外部窗口。GUI 改为明确参数窗口及执行确认，不提前平滑场景。

## API 与参数

候选加载见 acceptance.md。未来验收晋级后可 `maya_toolkit.execute_tool('brs_smooth_mocap', arguments, dry_run=True)`；当前正式库未注册。沿用 BaseMayaTool/ToolResult/UndoChunk，复用完整固定私有 locator 后端，不改正式 core/工具。backend 是随本候选的固定版本，不自动读取另一个候选或正式 LocatorTransfer 更新。

| 参数 | 默认 | 作用 |
|---|---|---|
| action | inventory | inventory/open_ui/smooth_mocap/smooth_keys |
| root_joint | 空 | Mocap 明确 joint；空取当前首选对象，必须 joint |
| strength | 3，整数1..100 | 仅 Mocap：实际平均轮数 strength-1；1 仍复制/回烘但0轮平均 |
| curves | [] | smooth_keys 明确 animCurveTA/TL/TU；空读取所选关键帧所属曲线 |
| selected_only | true | smooth_keys 只处理所选时间键；false 处理明确曲线全键 |
| annotation | true | Mocap 临时 locator 原 Annotation 选项 |
| bake_all | false | locator 生成时原稀疏键/完整整数帧选项 |
| in_timeline | false | locator 生成范围是否使用 round(playback min/max) |

smooth_keys 始终一轮，对应原 BRSSmoothKeys；strength 不控制此动作。Mocap 后端 Position/Rotation/Constraint 明确启用，两种位姿都要由 locator 驱动才能平滑回写。原隐式窗口选项改为显式参数。

## 平滑算法与行为边界

对每条曲线的指定有序时间键，先查询前/当前/后三个键的值并快照 `(prev+current+next)/3`，然后全部提交。序列首/末键不改；不是逐个写完再读邻居，不按时间间隔加权，不保证切线/高频细节/脚部接触保留。只选不连续的三个键时，它们也作为相邻序列；选少于三键的曲线跳过。Mocap 默认3对应两次平滑，非三次。

Mocap 读取 root 下 joint 后代再 root，保持原后代顺序；修复叶 joint 的 listRelatives None 和原包含非 joint 对象的层级采集。仅六 TR 拥有两个以上不同时间键的 joint 参与复制/回烘，零/一时间键 joint 返回 skipped_joints，避免原 locator 名列表引用根本没创建的对象。没有可处理 joint 时只读预检失败。

原 BRS 后端复制世界运动到临时 locator，按原稀疏/dense/timeline/breakdown 规则留键；private UUID+message 对应目标，标准通道预检拒绝引用、锁、外部驱动/约束或不安全旧 helper。locator 六 TR 曲线全部进行 strength-1 轮平均，再按 locator 全时间集合回烘六 TR。

回烘保留原 sampleBy=1、disableImplicitControl=True、preserveOutsideKeys=True、sparseAnimCurveBake=False、Python round 边界和 filterCurve。最终 joint 键可以变密，breakdown/切线/小数边界会受原 bake 行为影响；没有最终稀疏删键/snapKey 步骤（原 Mocap 也是直接 bakeKey，而非 LocatorTransfer apply）。in_timeline 可能使临时 locator 范围扩展，进而改变最终回烘范围。

区别于原直接删 locator 的残留问题，成功回烘后先按 Owner 脱离并删除本次目标约束，再安全删除临时 locator/annotation/shapes，保护空 joint，不 blanket 删除外部约束。Maya 自动生成的 blend/旧曲线载体可能保留，返回 retained_blend_nodes，不强行清空所有辅助节点。

## 预检、状态与输出

normalize 严格验证 bool/int/名字/重复/非有限等类型；strength 新增上限100防止误传无限工作量。smooth_keys 限制时间输入 TA/TL/TU，拒绝 time warp/非时间曲线，拒绝曲线及直接下游引用/锁；复杂间接混合/layer需制作资产复验。无三个键可处理时不写。

validate/dry_run 只查询 root/层级/通道、时间键与 eligibility，不选择键/对象、不加载 scripts、不创建 helper、不修改 Undo。标准执行一个 UndoChunk，finally 恢复时间、存活组件选择、refresh suspend、GUI OGS pause、仍存在曲线原所选键索引和两个内部 guard。没有外部文件/联网/cycleCheck/evaluation 修改。若键数量/索引被 bake 改写，恢复所选键只按原仍有效索引，不能保证相同时间语义；GUI需验收。

失败不自动回滚，可能已有 owned locators/约束/部分曲线，查看 ToolResult/Script Editor 后 Undo 或修候选；不要将失败保存成制作资产。无原全局 mainProgressBar 依赖。

inventory 返回来源/完整随包后端哈希；open_ui 返回 window。执行返回 action、passes、processed_curves、source_key_times、joints、skipped_joints、remaining_private_locators、retained_blend_nodes 和 warnings。Mocap 的 processed_curves/source_key_times 指临时曲线，成功清理后这些名字可能已不存在；用于审计，不作为后续对象输入。真正后续输入是 joints 的烘焙动画。

可选副本流程：Graph Editor 明确键 → smooth_keys → 比较端点/细节；或 root joint 动捕副本 → dry_run → smooth_mocap → 比较世界运动/接触/旋转曲线 → 人工决定是否进入导出。没有保证与其他候选或正式工具的生产组合已验证。

## 检查与晋级

普通 Python3项：全部原件/随包文件哈希、原平均算法 AST 一致、Schema/严格参数/无 Maya inventory。Maya2025 隔离6项：实际所选键/快照平均/端点/Undo，真实 locator→两轮平均→joint回烘（中值6变2/3）与owned清理，叶根/静态后代/strength=1，无副作用预检/锁/GUI拒绝，以及故障状态/两个guard恢复。临时正式布局/注册预览不改正式库。

实际 GUI/Graph Editor 部分所选键、非默认单位/小数帧、jointOrient/复杂骨骼/动画层/大角度Euler与真实动捕质量未验收。真人当前哈希记录通过后才可按 promotion.json 完整复制代码/依赖/文档/测试并注册；之前留在 tools_staging_pool。
