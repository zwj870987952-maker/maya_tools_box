# BRS Locator Transfer 真人验收

prepared_unverified，GUI not_run。只用真实 Maya 备份场景；关闭原窗口，不运行原 BRSLocTransfer.py（它含远程 exec 入口）。

```python
import runpy
candidate = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\brs_loc_transfer\release_candidate\launch_candidate.py')
tool = candidate['load_tool']()
tool.show_ui()
```

1. 原布局/折叠/四按钮/选项/状态文本开关重开正常，不下载执行远程代码，cycleCheck 不改变。
2. 两个以上 TR 时间键的控制器 create，Annotation/Constraint 开关、稀疏/dense/breakdown、timeline范围正确；零/一时间键被跳过。dry_run 比较场景/选择/时间/Undo/refresh 无变化，普通一次 Undo 撤回整个创建。
3. 编辑 locator 动画，再 Apply 验证真实控制器运动/曲线、外键保留、locator/owned约束/空组清理、空控制器存活及 Undo。观察 retained blend 节点是否携带旧曲线，不要求全部删除。
4. Position-only/Rotation-only：原 apply 仍删/烘焙六TR，验收未选通道变化，不按 Align 推断保护。测试小数帧、round半帧、范围外键最终 snapKey 和切线，不在生产动画上首次运行。
5. Create Guide，移动/旋转 guide，Apply Redirection，比较 group transform、locator世界轨迹和最终controller运动。隔离平移发现 group.tx=10但locator worldX仍0；这项必须确认是否符合目的，不能用“代码无异常”判定整体重定向满意。若需改变算法，先修候选再验收。
6. 改名目标/locator/group，保存重载后对应关系正确；外部同名group/guide、外部子对象/输出连接/message改接/外部约束应拒绝。含额外动画属性的回写拒绝，使用仅六TR副本。
7. 约束开关、引用源只读(constrain=False)、节点/通道锁、复杂动画层/blend、多个对象/同叶名与生产rig独立测试。故障检查选择/时间/refresh/OGS/锁/guard恢复，部分已写入用Undo撤回。

记录实际Maya版本、日期、验收人和逐项结果（guide世界轨迹单列）；发现问题修候选后重验。通过才建立真实记录：

```json
{"tool_id":"brs_loc_transfer","passed":true,"maya_version":"实际版本","date":"实际日期","accepted_by":"验收人","candidate_sha256":"当前只读晋级预览哈希"}
```

plans/staging_run/promote_candidate.py --candidate <候选绝对路径> 先预览当前哈希/目标清单；真人记录匹配才能 --acceptance <记录> --apply。真人通过之前保持待整理库，不迁正式库。
