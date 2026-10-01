# Pose Transfer 真人Maya验收（未运行）

在备份rig/临时场景使用launch_candidate.py load_tool/open_ui，不执行原文件自动入口。

1. 原1..5自动/手动/记录/移动/应用/清理按钮全部可见，窗口不盖掉原版，默认Allow reference edits关闭；重开候选可读取scene session，Script Editor无致命错误。
2. 一个ROOT与层级控制器，部分含同leaf不同namespace，capture dry_run不造节点/改选择/AutoKey/时间/ns/Undo；detect仅ROOT范围，namespace ControlSet有别rig成员时不能混入。
3. capture，用户ROOT仅平移，再shift/apply；检查所有world位置/旋转/scale/shear与locator，父先子后；重复shift不漂移，再动ROOT后按新delta移动，一次Undo/Redo包括metadata。
4. ROOT rotation/scale改变不作相应姿态空间变换，不能宣称跨模型自动retarget；生产pivot/nonuniform scale/shear/rotateOrder/OPM用备份场景核验全matrix效果。已有动画/driver/constraint/层/锁应拒绝apply。
5. 手选controllers包含ROOT外对象时仅该明确范围参与；先在scene选好再点手动确认；root修改/rename、controller rename、scene.ma/.mb保存重开/Undo后能重读UUID，不按旧名字写错对象。
6. cleanup只删session helpers/marker，目标控制器不变，Undo/Redo恢复助手和session；外部child/shape/output拒绝，控制器已删、部分helper缺失仍可清剩余owned helper。marker被锁/接consumer时拒绝。
7. 第二helper或apply中途错误：partial capture不能shift/apply，context finally恢复，Undo可恢复；recapture只换原owned helper，不删同名用户locator。坏metadata/重复marker明确拒绝。
8. 引用控制器capture只读允许；默认apply拒绝。只有在备份引用场景显式勾选允许edit，再核对实际ref edits/全matrix和保存影响，锁/driver仍必须拒绝。

记录Maya/Python版本、rig/pivot/scale/ref条件、各按钮/scene结果与错误。5组隔离检查不是上述真人验收，满意后才按promotion.json晋级；无独立license仅本地不发布。
