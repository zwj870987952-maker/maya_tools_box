# bh_aimTools 真人验收

当前 prepared_unverified，GUI not_run。在实际 Maya 的备份场景操作，关闭原工具窗口。保留购买许可和原 ReadMe，不分享本候选及原资源。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\bh_aim_tools_v1_1\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 开窗、关闭、重开，四按钮和两个 KeysOnly 响应正常；不创建 Shelf、不复制 scripts 文件。观察 Script Editor 致命异常。
2. 选择一个无外部旋转驱动的控制器，先 create dry_run，比较节点/键/选择/时间/范围/Undo/评估/缓存，无写入。实际 Create 后白色定位器及 ctrl message 指向控制器，选择定位器；批量创建应选择全部结果。一次 Undo 撤回。
3. 把定位器移离控制器。KeysOnly Attach 使用控制器范围内已有键（含小数帧）；关闭则每整数帧附着。无源键应提示，而非留下半条曲线。观察保持偏移和 filterCurve。
4. Aim 后控制器朝向定位器，出现锁定 UpVLocator；验证 X/Y/Z 相对位置、twist 和原轴启发式，在非零旋转/父级/真实头眼rig副本上观察。重复 Aim 或 Aim 后再次 Attach 应拒绝。
5. 编辑定位器动画，用 motion trails/定位器层逐项观察；烘焙 KeysOnly 与每帧两模式，检查控制器旋转曲线、视觉朝向和一次 Undo 恢复约束/定位器。烘焙后空控制器应仍存在。
6. KeysOnly Bake 的删除确认选 No 时保持旧键；选 Yes 会删除**所有时段**旧旋转键，不仅播放范围。检查范围外键确实按该选择变化。没有定位器键时应先拒绝，不能删旧键后才失败。
7. 在 Aim 前已有旋转动画时验证 Maya pairBlend 路由；检查返回 retained_blend_nodes 和混合属性，不将保留节点当无影响垃圾。在 Aim 后直接给控制器新增键可能产生外部 pairBlend，候选应拒绝自动接管；记录真实rig效果。
8. 重命名控制器/定位器、两个rig同叶名/命名空间、场景保存重开，UUID/message 配对应保持；预先创建同名 _ROOTLOCATOR 应保留。外部后代、改接 ctrl、外部约束/消费连接应拒绝危险清理。
9. 锁定/引用写目标、外部驱动、缺失/歧义/重复对象、倒置范围应失败；按工具说明使用 clear 放弃网络，已有曲线保持。发生部分执行异常先检查，再 Maya Undo；不能把 finally 恢复 runtime 状态当自动回滚。
10. 检查时间、选择、播放范围、刷新、evaluation/cache 状态恢复；真实 Maya 和生产绑定结果满意后，记录版本、日期、验收人及逐项结果。

真实通过后建立当前记录（占位字段不能当实测证据）：

```json
{"tool_id":"bh_aim_tools_v1_1","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

先运行 plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 获取预览；匹配真实记录后才执行 --acceptance <记录> --apply。文件、说明、测试及当前注册表同时晋级，不再要求开发业务。真实验收前不迁入正式库。
