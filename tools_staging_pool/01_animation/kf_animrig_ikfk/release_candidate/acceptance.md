# 真人Maya验收：KF AnimRig IK/FK

状态not_run；只有完整MEL编译与临时引用手臂fixture检查。需要用户已有权使用的原KF Auto Rig备份，不安装/下载/发布第三方资源。

1. 用launch_candidate.py load_tool().show_ui()打开原匹配窗口/说明，核对Instructions、两匹配按钮、右键两bake与Adv Spline菜单，没有Error/Fatal；显式引用编辑确认取消应无写入。
2. 引用原作者rig，选namespace:CTRL_*_Hand，手动按原说明确认源姿态/显示模式，两方向左右臂分别测试。比较世界手位置/朝向、Pole、stretch、右侧rotateAxis=-180补偿；工具不会切pinner/IKFK。
3. 原普通脚与狗腿两方向、toe/roll/heel等重置、第二pole/independentIK/匹配空组和长度属性分别核验。若原FK通道锁定，候选会严格拒绝，不自动解锁。
4. 原高级样条选*_Pinner测试两方向，记录jointNum/CV数量/open与closed曲线、cluster位置、allRot/allLength/scale重置效果。当前只有MEL编译，无这些资产实跑记录。
5. 备份区间烘焙：原需要已有键，候选改为逐帧显式键所有预检目标属性。确认目标键数量、范围外键、间帧运动和pinner需手工设置这一行为可接受。
6. 一次Undo恢复单次匹配或整段bake；AutoKey/时间/选择/namespace恢复；助手清理且不删已有同名group，不额外残留约束/blend影响rig。失败先Undo再修候选；有自动blend残留记录具体节点。
7. 验证缺依赖、引用/锁曲线、外部约束/层/共享曲线、不同reference node应拒绝。记录版本/场景/截图/报错和是否满意；只有用户确认才执行预制晋级。隔离fixture不替代真人验收。
