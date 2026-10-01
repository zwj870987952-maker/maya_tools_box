# Maya 直验（not_run）

1. 在已保存备份的真实 Maya 场景，从 launch_candidate.py 打开界面，选关节后预检，确认列表范围不展开层级，混合选择只处理 joint。
2. 父关节缩放为 2 的简单关节链，关闭选中子关节的 segmentScaleCompensate，比较世界矩阵/骨架显示及蒙皮；未选择关节保持原值。一次 Undo 恢复完整外观和属性。
3. 用生产 rig/动画做同样比较，不把可预期的比例变化称为“自动修复”。检查锁定/连接驱动/引用/实例/空选择拒绝，重复执行无额外写入。
4. dry_run 不改变选择/时间/Undo 队列/属性。其它目标 Maya 版本复验，Script Editor 无致命错误。
5. 满意后记录真实人工 acceptance JSON（passed、tool_id、candidate_sha256、maya_version、accepted_by、date），交给 plans/staging_run/promote_candidate.py --candidate 本目录 --apply --acceptance 记录文件；当前只预览。
