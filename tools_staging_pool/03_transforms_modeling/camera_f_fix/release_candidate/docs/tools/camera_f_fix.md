# 按 F 相机重置候选

`prepared_unverified`，真实 Maya 视口/F 键效果及 GUI 尚未验收，仅留待整理池。原 MEL 全字节和SHA保留，不自动source。原文件没有作者/许可说明，不推断发布权。

原行为完整保留：选 `persp`，Reset Transformations，再将**局部** translate 设 `(1,1,1)`。Reset Transformations 的旋转/缩放选项来自 Maya 用户偏好。读取本机 Maya2025 `performResetTransformations.mel` 确认其底层是 `makeIdentity -apply false -t/-r/-s`；候选使用相同命令、只读解析偏好，未拷贝 Autodesk 专有脚本。未设偏好默认 True。候选不修改 cameraShape、焦距、裁切、centerOfInterest 或视口；不能保证所有“按 F 出错”由这些变换引起。

`CameraFFixTool` 继承Base、ToolResult、Schema、Undo Chunk；category=`modeling_surfacing`。`action='reset'` 默认执行，`inspect` 返回计划。参数 `camera='persp'`（可为唯一 perspective transform/shape）、`reset_rotation` / `reset_scale`（布尔；省略用当前Maya偏好）、`preserve_selection=False`（原选中相机；True保留调用前选择）。每次预检返回目标shape、原TRS、解析后选项、固定平移、影响通道；只读，不改选择/时间/偏好/Undo/节点。拒绝空/歧义/非camera/正交/实例、引用/锁/关键帧/驱动通道、camera含child transform rig。父层级保留，重置为局部变换，不承诺世界姿态。

```python
tool = load_tool()  # 候选根目录 launch_candidate.py
plan = tool.run(dry_run=True)
if plan.success:
    print(tool.run().to_dict())
```

输出含目标、before/after TRS和影响说明。恢复AutoKey，不写文件，单次Undo恢复变换和原选择。小型UI提供相机字段、保留选择、预检与执行。晋级清单已包含完整代码、文档、测试、注册和面板接入；验收后调用统一 `maya_toolkit.execute_tool('camera_f_fix', args, dry_run=True)`。

复用框架现有协议/Undo。core没有相同camera偏好重置业务；其它整姿工具不等价，不改core。可在确认视图异常来源后重置，再手动选对象按F验收；与其它工具没有已验证组合。原脚本选择相机是默认保留的副作用，GUI可选保留选择是显式扩展。

2组离线检查（原字节/MEL内容/协议/参数）；3组隔离Maya2025（原MEL实际结果等价、全部偏好启闭与覆盖、选择/AutoKey、只读/单Undo、锁/关键帧/正交/rig子节点/实例/GUIbatch拒绝）。真实 GUI 和生产相机/父层级/非默认偏好跨版本仍not_run。
