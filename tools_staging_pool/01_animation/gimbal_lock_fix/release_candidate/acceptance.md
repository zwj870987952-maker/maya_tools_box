# 万向锁修复真人验收

当前 `not_run`，只在备份动画上测试。mayapy矩阵/业务通过不等于视觉效果通过。

1. Script Editor用下方代码打开完整原生窗口，检查对象选择、检测、三个范围模式、自定义时间、采样密度/帮助正常，无Error/Fatal Traceback。
2. 六种rotateOrder分别比较修复前后关键帧世界姿势；通过备份/Undo逐帧检查中间姿势、插值、动画速度和长转圈。检测是最短角速度而非必然万向锁，不能保证消除全部问题。
3. 验证density1/2/更高、非整数key、键间距≤1与>1、范围边界不含键/只含一个键、范围外切线也变spline的原行为；看Graph Editor与视窗。
4. 验证锁定/引用对象、共享输出、层/约束、缺轴曲线、animated rotateOrder及非degree单位明确拒绝修复，引用/锁定只读检测按条件可用；不要期待覆盖制作图。
5. joint/rotateAxis、不同parent/scale、制作rig逐项复验；检测不改变选择/时间/key/Undo队列，修复按标准Undo/Redo，AutoKey恢复。故障后先Undo并检查局部曲线。原“保留键”选项未实现，UI已禁用并说明。
6. 记录Maya/Python/OS、旋转顺序、测试动画、结果/错误/满意度；真实通过前不迁入正式库、不执行promotion apply。

```python
import runpy
tool = runpy.run_path(r'E:\GitHub\maya_tools_box\tools_staging_pool\01_animation\gimbal_lock_fix\release_candidate\launch_candidate.py')['load_tool']()
tool.show_ui()
```
