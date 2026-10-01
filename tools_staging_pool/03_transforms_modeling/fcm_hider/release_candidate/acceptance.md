# FCM Hider 真实 Maya 验收

1. 备份测试rig，initialize/open_ui创建私有mtbFCM系统，原紧凑窗口全部身体/Extra按钮和右键菜单、Edit扩展、图标/文字帮助/联系页正常；不运行原shelf安装器。先dry确认无节点/成员/visibility/时间/选区/Undo/文件变化，碰撞旧同名节点拒绝。
2. 对象/shape/mesh faces分别加入9组，Body/Extra shape_mode边界正确，添加即hide、show/toggle/全show/hide正常。空set不意外全场景隐藏，原“最后一面”不会被修改。成员所在transform父子影响符合实际场景；一Undo恢复membership/visibility/面隐藏数据，不用单测代替真实视口。
3. remove/clear/clear_body/clear_extra显示并清空对应范围，cleanup只删拥有的set/settings，不删对象、其它set、默认隐藏数据。settings新增child/节点给外部消费者后，“Remove All”应预检拒绝。引用/锁/实例/坏拓扑/失效membership拒绝，不部分修改。
4. 原Mirror从右Arm/Leg到左，12命名变体和局部X对称face分别实测；非对称和多候选拒绝，容差/角色左右轴记录。镜像只加成员，确认各组随后hide/show响应，原global reflection mode不应改变。
5. Lock Selection、Unlock成员／可见mesh、Template Line、object/component/curve切换、poly颜色、Grow/Shrink、Check All循环与Isolate式循环全部验收。无关网格、部分覆盖的displayLayer保持；“Select Set”保留新选择。选择mask/color等GUI状态按说明人工恢复，核对进度取消和Script Editor。
6. 新临时JSON导出／导入9组，已有文件拒绝。修改membership后import替换成员并显示旧内容，不假称导入还原隐藏状态；再hide验收。旧.py/malformed JSON明确拒绝，绝不执行外部文件。外部文件不Undo，scene导入单Undo还原原membership。
7. 记录Maya/Qt/场景单位/版本、未验证问题和满意结果。全部实测通过才执行promotion注册面板；当前prepared_unverified，全包留待整理池，不运行Obsidian同步。
