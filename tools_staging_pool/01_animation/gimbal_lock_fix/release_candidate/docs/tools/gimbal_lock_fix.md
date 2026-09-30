# 四元数动画旋转修复候选

工具 ID `gimbal_lock_fix`，领域 animation；用户提供的 `maya_animation_gimbal_fix.py` 头部作者 Claude，未附独立许可。原文件按字节保留，完整 8 个算法方法和原生界面保留在 native.py，所有适配差异在 gimbal_lock_fix_changes.diff；不将来源信息推定为公开分发许可。

## 用途与实际算法

原检测按三轴关键帧时间并集采样 Euler rotation，转换为对应 rotateOrder 的四元数，以相邻关键帧最短旋转夹角/帧间隔是否超过阈值定位连续问题区间。这是角速度提示，不是奇异性检测：真实快速动作也会被标记，360°整圈端点的最短夹角可能为0，不能据此断定没有问题。

原修复在所选范围内的已有关键帧取四元数，密度大于1时只在相邻键时间间隔>1帧的区间增加SLERP样本，然后转回Euler、覆写/新增三轴key，将整条曲线（包括范围外）的in/out切线改为spline。密度1不增加帧内采样，只重新表达现有键旋转；不改变rotateOrder、不选择最佳旋转顺序、不做Euler连续性展开、不保留任意圈数，也不能保证去除全部万向锁/插值跳变。必须在备份中比较视窗结果。原 preserve_keys/create_new_curves/frame_rate/smooth_factor 属性未用于算法；不宣称实现这些功能，原UI未连线的保留键复选框显示说明并禁用。

## 接口与场景范围

`GimbalFixTool.run(dry_run=False, **arguments) -> ToolResult`。`action=detect/fix/open_ui`，`objects=[]` 使用当前选择，明确对象为唯一transform/joint，`threshold=45` 为有限正数（度/当前帧单位），`start/end=null` 使用每对象各自关键帧范围，`samples_per_frame=1..100` 整数；预计样本超过200000拒绝。范围两端不自动补键，必须包含已有关键帧。输出 `results` 含对象、检测 `problem_ranges/rotation_order` 或修复 `fixed/sample_count/curves`。

只支持degree单位、固定rotateOrder、三轴各自已有直接animCurveTA。动画层、约束、表达式/单位转换输入、缺轴曲线、animated rotateOrder等会明确拒绝，不接管或强行补驱动。检测可只读引用/锁定对象，修复拒绝引用/锁定对象与曲线、锁定通道和共享/外部曲线输出。validate/dry_run仅读取参数、连接、键时间和范围，不导入原UI、改时间/选择/键/Undo/偏好或打开窗口。检测按 getAttr(time=...) 的只读时间上下文采样，不切换当前帧。

修复通过框架Undo chunk和原UI标准调用桥执行；private _apply 写入要求活跃的已验证曲线范围，不能绕过入口补接图。AutoKey临时关闭后finally恢复，选择/时间保持。失败不自动回滚局部key，先Undo再检查。没有外部文件业务写入。原UI保留对象选择、检测/问题区间回填、三个范围单选、自定义区间、密度、帮助；原“整个动画”实为min/max播放范围，原“时间滑块”实为animationStart/End，现准确标注，API null则按真正键范围。UI创建不归场景Undo。

## 明确修复与演进

- quaternion→Euler 原先在asEulerRotation后只改order字段，会改变非XYZ的方向；改为reorderIt重表达同一旋转，六种rotateOrder关键帧矩阵等价已在隔离Maya验证。
- Maya API1 MQuaternion没有原调用的angleShortestPath；用 `2*acos(clamp(abs(dot/(norm1*norm2))))` 实现最短夹角，避免归一化误差越界。
- SLERP先复制第二个四元数，负点积符号翻转不再污染缓存；其余最短路径/近共线分支、原采样规则与公式完整保留。
- 只读采样替换原currentTime循环；未使用的fallback旋转曲线类型由TL修为TA，但当前安全准入要求已有三轴，补接图分支不执行。
- 完整UI回调经标准API/Undo，取消顶层自动窗口；准确说明范围/未实现选项/效果边界。

## 示例与组合

```python
tool.run(dry_run=True, action='fix', objects=['rig:control'], start=1, end=24, samples_per_frame=2)
report = tool.run(action='detect', objects=['rig:control'], threshold=45)
tool.run(action='fix', objects=['rig:control'], start=1, end=24, samples_per_frame=2)
```

输入为已烘焙三轴旋转曲线，输出为检测区间或改写曲线，可在备份上接烘焙/平滑/导出。若上游来自约束/动画层，需先经用户验证的烘焙步骤得到直接曲线；这里不宣称跨工具组合已实测。复用现有BaseMayaTool/ToolResult/Undo；生产core/正式库/注册不改。

## 验证与晋级

普通Python验证资源/完整native方法/UI/Schema/延迟Maya导入；Maya2025隔离mayapy覆盖六种order矩阵等价/Undo、只读检测与dry-run、真实角速度区间、子帧密度/范围/标准原UI业务桥、SLERP缓存符号不变、共享/锁/animated-order/角度单位保护、部分写失败与finally/Undo。没有实际打开GUI，也未验证生产动画效果、jointOrient/rotateAxis/非均匀父级scale/所有版本。候选 prepared_unverified，按acceptance.md真人验收后才可执行预制promotion.json的完整搬迁/注册/面板晋级。
