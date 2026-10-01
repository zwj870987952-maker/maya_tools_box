# Maya 人工验收（not_run）

1. 打开备份场景，通过 launch_candidate.py 的 load_tool()/show_ui() 打开完整窗口；核查所有模式开关、Go、Cancel、Advanced/Help、清除全部 TR 键确认选项。未勾选时涉及清键操作必须拒绝。
2. 简单带键控制器做 default 和 Pin，比较首尾帧、中间帧世界姿态，确认范围外键按原清除行为移除；Undo 一步恢复全部原键和控制器。修改 locator 应正确驱动控制器。
3. 手动 pivot：manual_start 后移动 locator，再 Go，检查偏移；另开一组 Cancel，只删除自有 locator。relative 最后选参照、Freeze 第一项主控，核对全时域运动及 Undo。
4. 备份真实 FK 三控制器 limb，分别测试 IK/Local、Pole 移动、约束、尺寸和显示；共线/零长/缺父节点拒绝。锁定/已有约束/动画层输入应被保护。未知 rig 兼容问题记录具体 Maya 错误，不视为验收通过。
5. final bake_delete 比较控制器世界运动，检查辅助清理且外部对象保留，Undo 恢复整个会话。最终 bake override layer 检查结果动画层保留、静音/solo 行为与 Undo。
6. 创建相似原工具后缀对象、TempLocator、foreign 自有前缀对象、辅助组外部子节点、篡改 session 集合：前两者保留，后三者预检应拒绝；dry_run 不新增 MEL/UI/节点、不清键、不改变选区/时间/首选项。
7. 独立 Maya 会话及其它目标版本复验。全部满意后写真实人工验收 JSON（passed、tool_id、candidate_sha256、maya_version、accepted_by、date），再用 plans/staging_run/promote_candidate.py --candidate 本目录 --apply --acceptance 验收文件 晋级；当前只允许预览，不执行迁入正式库。
