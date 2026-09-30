# 动画复制与自动对齐候选

`copy_animation` / `animation` / `CopyAnimationTool` / revised-adapter-1.0。prepared_unverified，真实 Qt GUI not_run。原修复优化版单文件完整字节归档；六通道采样/数值算法AST只增加guard，其余一致。原 CustomListWidgetItem、Delegate、ListWidget、EditDialog、完整 AutoAlignUI 的彩色圆点、右键模式、拖拽、录入/列表编辑、配置UI保留；场景/文件按钮改标准API，另加“清理候选辅助节点”。用户自有脚本未附独立license，本地准备不发布。

原文件的Maya2020–2025/Python2标题与兼容辅助保留用于追溯，不是本候选已验证版本声明；本候选和当前框架按Python3准备，只在Maya2025隔离执行，真实旧版本/Qt/Python2不宣称通过。复用框架BaseMayaTool/ToolResult/UndoChunk，不改正式core。

## API与配置

候选加载见acceptance.md。真人验收晋级后才可 `maya_toolkit.execute_tool('copy_animation', arguments, dry_run)`；当前正式库没有注册。

| 参数 | 默认 | 用途 |
|---|---|---|
| action | inventory | inventory/open_ui/create_locators/execute/cleanup/save_config/load_config |
| pairs | [] | source、target、可选modes的有序数组；非文件/GUI/inventory需明确pair |
| modes.translate/rotate/scale | frame | frame/constraint/numeric/none |
| modes.other | none | numeric/none，只处理源keyable userDefined标量且目标同名属性存在 |
| start/end | null | execute取int(playback min/max)，API显式参数必须整数；闭区间 |
| file_path | 空 | save/load_config绝对.json路径 |
| overwrite_file | false | 配置覆盖需显式true，GUI文件已有询问 |

示例pair：`{"source":"|src","target":"|dst","modes":{"translate":"frame","rotate":"numeric","scale":"none","other":"none"}}`。每项缺失modes按原默认补齐。拒绝未知/无效模式、组件/通配符/歧义、源目标相同、同批重复写入目标；源可作为只读引用，目标引用/锁定拒绝，创建helper也要求目标非引用/非锁。通道锁/外部驱动拒绝，本pair自己的约束和辅助混合可在模式切换时处理；复杂层/rig不保证适用。

load/save配置保持原列表格式 `[{"text":"源对象 , 目标对象","modes":{...}}]`，读取整份严格校验后才替换UI。纯配置动作不要求节点此时存在，不执行任意代码。原列表编辑先clear再复用旧QListWidgetItem会访问已删除C++对象，候选先保存modes再新建条目，按原行索引复用模式，不复用旧wrapper。

## 四种原行为

- frame：逐整数帧检查源对应TRS组任一轴是否有该帧精确时间键；有键才按target locator世界位姿matchTransform目标，并给整个translate/rotate/scale组打键。源只有小数帧键时不会自动在邻近整数采样，不是每帧烘焙。
- locator：创建源/目标locators，match当前源与目标TRS，源locator入组、目标locator作为其子物体；源locator由原parentConstraint+scaleConstraint maintainOffset跟随源。目标locator保留创建时目标相对源的初始偏移，不是直接复制源世界TRS。执行复用已有locator，强制“生成/更新”才按当前姿态重建。
- constraint：translate/rotate/scale分别原point/orient/scaleConstraint，maintainOffset=True，约束持续存在；再次执行先删本pair自己的旧目标约束，再按当前模式重建。不是bake后自动删约束。
- numeric：每个整数帧查询源局部标量属性，给目标同名可settable属性setKeyframe；TRS三个轴或other keyable userDefined。缺目标属性、非数值、非标量、不可settable按原跳过，非标量产生warning；不是创建新属性。源/目标父级空间不同时数值复制不会保留世界轨迹。
- none：该通道不写。默认other不复制；多pair按传入顺序处理，源若也是前一pair目标，读取可能包含前一步结果，复杂依赖/cycle需另行验证。

原算法里的逐帧写入失败warning收集到ToolResult.errors并返回失败，不能把所有失败都吞掉后称“完成”；允许的非标量跳过仍作为warning。部分已写入不会自动回滚，应检查后Undo。

## 持久记录与清理

每pair一个Owner/Role/token network，保存source/target UUID+message、两helper UUID、follow/目标constraints UUID。重命名/保存/Undo后按UUID重建关系，拒绝message/约束输入改接、外部消费者、其他pair或外部后代；UUID查询必须唯一，不猜第一项。helper创建阶段及时保存已建立的资源记录，失败仍可按记录检查或Undo。

固定group与四集合用mtbCA私有名；已有外部同名节点拒绝，不接管。集合从全部存活owned记录汇总，不仅当前UI条目；UI清空只清列表，不删scene helpers。constraint先脱离目标再删除，保护空transform。source locator对子target locator的删除只在同token后代/消费者检查通过后进行。Maya自动生成的owned auxiliary/pairBlend可能保留旧动画，返回retained_auxiliary，不强行全删。

cleanup有pairs时清这些已记录pair；pairs=[]时清全部本候选记录，包括目标已消失的残留，不按外部对象名清理。清理目标约束会取消持续驱动，不把驱动效果自动bake；需要动画保留请先人工烘焙。只删owned constraints/helpers/network和空owned group，四owned集合更新为空保留。若有外部添加后代/连接，应拒绝并人工检查；不要绕过token校验。

标准场景调用一个UndoChunk，finally恢复时间/存活组件选择和关闭guard，不改播放范围/refresh/evaluation或外部文件。validate/dry_run只查询pair/通道/owned记录与配置路径，不创建set/helper、导入Qt或写文件。配置用自己的临时文件后替换、显式覆盖，JSON/目录写入不能由Maya Undo撤回。

## 输出、组合和验证

inventory返回来源SHA/原类/六算法与UI变动。open_ui返回window。场景执行返回pairs（source/target/record_uuid/target_locator/constraint_uuids）、warnings/errors、retained_auxiliary；cleanup返回cleaned_records。save返回file_path，load返回pairs及路径。helper/约束UUID可用于审计，不是已转正外部API；用户只通过标准工具动作操作。

可在副本录入pairs→选择模式→dry_run→create_locators/execute→编辑helper或对照曲线→按需cleanup。frame与numeric的键密度/空间不同，混用前明确通道用途。UI条目选择决定处理选中项，没选中处理全列表；清空列表后cleanup按全owned记录。没有跨其他工具生产组合的实测证据。

普通Python3项通过：原件SHA/六算法AST一致/完整五原UI类与edit修复、严格参数/配置/Schema/无Maya inventory、文件预检无建目录。Maya2025隔离9项通过：真实frame键门控/相对偏移/Undo，numeric逐帧/custom scalar，持续maintainOffset/重复约束/安全清空目标，frame→constraint→numeric切换，dry_run/外部group/后代拒绝，UUID重命名/保存重载，同叶名两pair批量约束/清理，配置覆盖/加载、故障返回失败/guard与Undo。

没有创建真实Qt，没有验收圆点/右键/拖拽/列表编辑/文件对话框；nonuniform scale、复杂父级/jointOrient/动画层、制作rig、小数键和旧Maya/Python仍待真人。完整知识/两测试/资源/注册与晋级清单预制，当前哈希真人通过后才迁正式库。
