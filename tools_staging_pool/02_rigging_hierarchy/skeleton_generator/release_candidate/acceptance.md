# Maya 直验（not_run）

1. 保存备份场景，打开 launch_candidate.py 的 show_ui，核查后缀、选择结果、预检/生成按钮。dry_run 不改变节点、属性、时间、选择、namespace/autokey 或 Undo。
2. 选择两级旋转 joint 与其下 locator，生成并比较全部世界 TR、层级、radius/drawStyle、单位 scale；未选择的 joint 子孙不生成。一次 Undo 删除整批新骨架，原对象完全保留。
3. 只选祖先与隔着未选父节点的后代，应生成两个世界根；不要误认为补齐了缺失链。namespace 与重名目标检查正确，select_result=False 恢复旧选择。
4. 引用/锁定源、负缩放/非均匀缩放/复杂 jointOrient 的生产 rig 用备份逐项比较世界姿态，记录实际兼容范围。新 posed 骨架没有原动画/skin/bindPose 的声明应明确。
5. 目标冲突、实例、别名重复、组件/空选区拒绝，Script Editor 无致命错误。其它目标 Maya 版本复验。
6. 满意后写真实 passed/tool_id/candidate_sha256/maya_version/accepted_by/date 验收 JSON，运行 plans/staging_run/promote_candidate.py --candidate 本目录 --apply --acceptance 验收记录；当前只允许晋级预览。
