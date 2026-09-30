# 真人Maya验收：Lock to World

状态not_run。当前只有离线与隔离mayapy检查，候选留待整理池。使用有权使用的本地备份，不执行原import插件/启动脚本。

1. launch_candidate.py load_tool().show_ui()打开Start/End/Lock窗口，按钮时间更新、缩放布局与Script Editor无Fatal/Error。整数帧区间，子帧按钮值应明确拒绝。
2. 六轴可写degree/cm控制器，动画父级与六种rotateOrder，指定停留start..end。逐帧比较世界位置/方向和区间前后轨迹，检查范围外插值变化。
3. 非零静态rotatePivot的冻结控制器、多对象、已有动画和无键本地对象分别测试；复杂scale/shear/负scale与真实脚底/IK膝部表现需要单独记录。冻结分支单位scale，不保存scale动画。
4. channelBox选择TR短名/长名、仅tx或仅旋转、空选择默认六轴；确认未选旋转曲线/锁通道不变，部分轴不承诺完整世界锁。选scale/非TR应拒绝。
5. 锁选中通道、动画pivot/外部驱动/层/约束/共享或引用曲线、额外rotateAxis/pivotTranslate/offsetParentMatrix应拒绝。真实引用控制器必须明确允许且写通道符合保护。
6. 一次Undo恢复本次键；AutoKey/时间/选择/namespace保持，无mtbLock_*助手残留。故障显示真正错误，先Undo恢复；插件状态/UI不由场景Undo恢复。
7. 记录Maya版本、fixture、视窗效果/截图/报错与是否满意；确认后才执行预制promotion.json，不能将mayapy通过当真人直验。
