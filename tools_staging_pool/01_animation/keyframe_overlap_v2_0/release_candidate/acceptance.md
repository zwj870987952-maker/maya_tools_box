# 真人Maya验收：KF Overlap v2

状态not_run；当前只有隔离mayapy/离线检查，全部候选留待整理池。仅当前有权使用的原用户机器、本地备份、隔离动力学场景测试。

1. 用launch_candidate.py load_tool().show_ui()打开完整窗口/dock。核对Rotation/Position、六mode、Invert、三滑块/数值框、Smooth、Create/Bake响应与Script Editor错误。不能执行原安装器或原support下载代码。
2. 带shape本地可写控制器，degree/cm、停止播放。为10..40等非零区间建立明显位置/旋转动画，分别试六mode和dynamic/offset/smooth参数，核对真实粒子延迟、方向、间帧效果；不要仅确认窗口打开。
3. Create留下owner/定位器图，调整红animate定位器的直接本地不共享曲线；选整组原控制器Bake或用record_id。比较视窗/曲线，检查范围外键删除与优化误差是否可接受，记录复杂scale/rig及其他动力学缓存表现。
4. 在场景放kfo_user_data和同类原名称节点，确认不被接管/删除。测试控制器/helper改名、保存重载后继续Bake；外部后代/输出/驱动、锁、引用、共享曲线或已有约束应拒绝。失败半成品先Undo。
5. Create一次Undo恢复/Redo可用；Bake一次Undo恢复编辑图。故障之后AutoKey/时间/选择/namespace/evaluation/refresh恢复；无自有约束/pairBlend或定位器残留影响目标，场景外动力学缓存需另行检查。
6. Save/Load/Rename/Delete预设在本窗口会话有效，重名拒绝，重开窗口/重启丢失；没有原cfg/APPDATA/preset持久写入。确认用户接受此变化。
7. 记录版本、fixture、结果/截图/报错与是否满意；只有用户明确通过才执行预制promotion.json晋级。不能将隔离mayapy通过当作真人直验。
