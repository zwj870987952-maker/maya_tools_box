# 取消选择高亮 v2

id `no_highlight_v2`，域 `modeling_surfacing`。原完整单文件/SHA 保留 upstream；完整 Start/Stop、活动 panel、面选择模式、选择变化时 shape override 和小窗口功能重构为受保护 session，继承标准 BaseMayaTool。导入只声明，不开 UI/加回调。真实 GUI/modelEditor 与生产 Maya 事件交互 not_run。

原功能关闭活动视图 selection highlight，切面组件模式，对第一选中对象的直接 shape 设置 overrideEnabled=True/overrideShading=False。候选支持第一 transform 或直接 shape/shape 组件，忽略 intermediate，保留原第一对象作用域，不处理全部选择。原每次选择先恢复然后同一对象不再应用的问题修复；空选择恢复当前对象。形状原 override 两值与原 panel highlight、object/component mode 和 facet mask 均记录，Stop 准确还原，不使用原强制(0,1)/object模式。

API `run(action='start', panel='modelPanel4', dry_run=True)`，panel 仅 Start 可选，默认焦点/活动/第一个 native modelPanel。`start` 激活单例会话并处理当前已有选择；`refresh` 跟随当前选择；`stop` 移除六个 API 回调并恢复全部跟踪 shape 原值、panel 和选择模式；`status` 默认只读输出 active/panel/callbacks/faulted/last_error/selection_events/last_stop_recoverable。`recover` 用本 Maya 进程保存的最近已停止会话记录恢复 override，适用于 Undo Stop 后，不重新装回调。一个会话仅一个 panel，第二次 Start 拒绝。

原值按 shape UUID 留到停止，支持重命名，删除的 shape 不重建；实例、引用、锁、属性驱动/不存在、外部 override 改为原值及本工具值之外均全表拒绝。只恢复记录对象，不重置用户其它显示颜色或未选节点；不自动解锁或断连接。validate/dry_run 不改视图、选择模式、callback、override 或 Undo。数据结果均为基础类型，Start/Status 返回会话状态，Refresh 返回当前/跟踪 UUID，Stop/Recover 返回恢复行。

场景属性写通过标准 UndoChunk，选择不主动修改、时间/AutoKey 不改；modelEditor、选择模式和 Python callback 生命周期不是可由 Maya Undo 自动恢复的事务。Undo/Redo 事件暂停跟随，faulted 会话先 Stop 再 Start。Stop 的属性改动被 Undo 后会重新出现 override，但 callback 不复活，使用显式 recover；不对 Undo/Redo 自动写场景。最近停止记录仅留当前进程，重启不能用于恢复，因此保存场景前请 Stop 并核对原值。回调正常注册/清理属于会话资源管理，不宣称 scene Undo 完整恢复会话。

关闭窗口通过 closeCommand 和一次 uiDeleted job 停止；若属性状态使 Stop 被拒绝，窗口关闭会分离回调并保留 faulted 会话供用户解除具体问题后 API Stop，不留下后台持续改图。BeforeNew/BeforeOpen/MayaExiting 移除回调/恢复视图及选择模式并清会话，不写即将替换的旧场景；未 Stop 的旧场景若此前保存了 override，另需用户用备份恢复，不能把新场景当旧 UUID。实际删除窗口/换场景/多窗口事件順序需 GUI 验收。异常属性/viewport 写失败可能部分生效，按记录/Undo 本次属性改动复查，不静默吞错。

完整窗口包含 panel 字段、Start/Stop、预检、最近停止记录恢复；原 HighlightTool 方法名 create_ui/get_active_panel/toggle_tool/start_tool/stop_tool/setup_tool/selection_changed/close_tool 保留对应入口，`launch_candidate.show_ui()` 显式打开。无外部文件/用户配置写入，无 shelf 安装。

复用框架 Undo/结果，不改 core。FCM Hider 也改 display override，需先 Stop 本工具再使用它，避免交叉恢复覆盖；isolate_selected 仅改 transform visibility，在 Stop 后组合更容易追溯。组合尚无生产实测。原作者/发行授权未推断。

验证：离线 SHA/Schema/严格输入；隔离 Maya2025 使用真实 DAG/属性/UUID/Undo、六个真实 MEvent/MScene callback 注册清理、实际 Undo 与 BeforeNew 事件、手动调用实际 selection_changed 回调方法。standalone 原生 selectMode 查询 object/component 均 False，不虚构选择模式通过；整个 viewport/selection-mode adapter 替换。native batch/GUI 拒绝；实际 GUI SelectionChanged 递送、modelEditor/选择模式及mask恢复、uiDeleted job 与真实关闭、保存重开、其它版本仍 not_run，不把 fixture panel 当真实验收。回调也直接检查 MGlobal.isUndoing/isRedoing，避免 Undo/Redo 期间 selection 递送加入场景写入。
