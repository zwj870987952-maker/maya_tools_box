# 隔离选中物体

完整原脚本四入口与说明归档于包内 upstream，原字节和 SHA 不变。候选继承 BaseMayaTool，保留隔离、恢复和原生 cmds 小窗口；原函数名提供兼容入口，不自动启动。id `isolate_selected`，域 `modeling_surfacing`。候选留待整理池，真实 Maya GUI 验收 not_run。

原脚本把所有子节点包含直接 shape 隐藏，可能连选中父对象自身也看不到；恢复把全场景 transform 设可见，且遗漏已隐藏 shape。候选只隐藏选中节点下未选中的子 transform，保留直接 shape 和选中后代的所有祖先路径；原本隐藏的选中对象/祖先不强制显示。仅恢复本次真正从可见改为隐藏的节点，保持无关对象和本来隐藏的子对象。

API `run(action='isolate', objects=['|root'], panel='modelPanel4', dry_run=True)`；省略 objects 使用当前整节点选择；shape 可以直接选择，组件、歧义名、重复别名、DAG 实例拒绝。`inspect` 返回只读计划。`restore` 省略 receipt 按 panel 找唯一记录，或明确 `receipt='mtbIsolateReceipt_...'`。panel 留空优先焦点 modelPanel，否则第一视图；batch 没有 native modelPanel，拒绝，避免静默改场景。

输出隔离为 ToolResult.data 的 receipt、panel、hidden UUID/原值；恢复返回恢复行。network receipt 的 marker 和严格 JSON snapshot 与场景一起保存，UUID 支持重命名和重新打开。原 modelPanel 名在新会话不存在时以 `receipt` 加新的 `panel` 覆盖恢复；之前面板组件集合通过节点 UUID 加组件后缀还原。拓扑、删除、驱动、锁、引用、实例或 receipt 损坏/外部连接让全表预检失败。隔离后手动改了本次 hidden 节点 visibility 也拒绝，避免覆盖新意图；撤销该手改或明确修正后再恢复。

场景影响是指定后代 visibility、一个私有唯一 network snapshot、目标视图 isolate 集合；不改全场景显示、不清其他工具节点、不写外部文件。选择和 AutoKey 在 finally 恢复，时间不变。validate/dry_run 只读；run 的场景写入在框架 UndoChunk 内。隔离 Undo 恢复可见性并删 receipt，恢复 Undo 重新创建 receipt 并回隔离时可见性；真实视图 isolateSelect/集合的 Undo 与 GUI callback 必须人工检验，隔离测试中的 panel adapter 不是原生视口验证。意外 viewport 命令失败可能留下本次记录/部分状态，应先 Undo 本次调用并检查视口；不自动 Undo 用户之前历史。空 isolate 集合、保存后换 panel、多视图、生产 rig 与其他 Maya 版本均待验收。

完整 UI 提供 panel 字段、预检、只显示选中物体和恢复本次隔离。兼容 `isolate_selected_only`/`restore_visibility` 返回标准 ToolResult，`create_isolate_ui`/`main` 显式打开窗口。临时独立加载 launch_candidate.load_tool()/show_ui()；真实验收通过后由 promotion.json 和预制晋级脚本注册到面板，无需改业务。

core 没有具有此恢复语义的 viewport receipt；复用框架 Undo 和标准结果，不修改 core。FCM Hider 管理成员组，只有确认其成员 visibility 不与本记录交叉时才可衔接；GPU Cache to Mesh 的 hideCache 会改变恢复条件，先恢复本工具再转换。此组合只是输入影响分析，尚无生产 Maya 组合实测。原作者/许可依据随原说明归档，不推断公开发行授权。

离线测试核对全归档 SHA、Schema 和损坏 snapshot。隔离 Maya2025 实际 DAG/visibility/UUID/network/Undo 测试仅替换四个 modelPanel adapter：保留直接 shape/选中后代祖先、原隐形子及无关对象、dry 无变、重命名恢复、两操作 Undo/Redo、全表锁/损坏/外部可见性变化/实例拒绝。native choose 与 GUI 在 batch 正确拒绝；真实 GUI 与视口验收不计为通过。
