# 约束管理 v6 真实 Maya 验收（not_run）

在真实交互 Maya 的新场景和绑定备份中测试。用 importlib 加载此目录 `launch_candidate.py`，调用 `show_ui()`；记录版本、Script Editor 报错、每个核心按钮与实际 Undo 结果。

1. 面板全部布局、显示模式、刷新/添加/清空、分隔/颜色、右键、双击、tooltip 和已有列表正常，Maya 2025 Qt6 与所需旧 Maya Qt5 分别测试。
2. 用 namespace、名称含 W、重名不同长 DAG、三 target 及删除过中间 target 的约束验证 alias/index/target 顺序。0/(1)0/1、自定义值、打键与不打键、已有动画曲线/共享/锁/驱动拒绝均符合预期，不误改用户浮点属性。
3. 对真实动画+skip+offset+自定义属性+插值的 parent/point/orient/scale/aim 约束测试断开/恢复：原 UUID 与输入动画保留，新驱动不得被覆盖。场景 Undo 后快照要重新校验，不凭 UI 标记操作已变化的场景。
4. 原 child 真正驱动每个原 target 的反向运动符合要求；原节点保留不丢动画，恢复只删除本次逆向节点。有关联 DAG、已有 target 动画或外部驱动必须在改动前拒绝，不自动拆驱动。若需要烘焙反向，另行定义需求，不把此按钮当动画转移器。
5. 重建后新 UUID 与实际名称、完整 targets/offset/skip/interp/custom/原输入曲线与场景运动一致，列表重建映射准确；一次 Undo 恢复原节点。删除、移除具体目标与保持偏移按选择范围作用，至少保留一个目标。
6. 静止位置和修改轴只作用原 child，包含该 child 所有原菜单会修改的约束，不修改 driver；检查原 Maya 菜单结果和 Undo。高级约束类型/多约束/复杂连接单独逐项记录，隔离测试不代表这些全部通过。
7. 新名称保存 locator 彩色列表、长 DAG 含 `|`、旧分隔格式导入、JSON 加载均正确，既有名称保护不丢资料。列表信息失效时要提示/重新选择，不映射到无关新对象。
8. 完整辅助四按钮与快照新 JSON 导出/载入在临时目录测试；既有文件拒绝覆盖，同场景 UUID 匹配才能恢复，恶意节点/连接/逆向 UUID 文件不能重连或删除无关对象。外部文件不是 Maya Undo 数据。
9. 真实 GUI、业务结果和实际需要的组合均满意后，制作 `tool_id=constraint_manager_v6`、`passed=true`、Maya版本/验收人/时间与最新 `candidate_sha256` 的 acceptance JSON。执行 `promote_candidate.py --candidate <本目录> --acceptance <json>` 预览；确认通过再附 `--apply` 安放代码、资源、知识、目标测试和注册，正式面板复验。

当前只完成候选和隔离验证；不提前转正。
