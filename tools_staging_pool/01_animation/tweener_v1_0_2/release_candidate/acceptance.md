# Tweener 真实 Maya 验收（not_run）

1. 备份场景、optionVars与用户配置，加载 launch_candidate.py 的 load_tool；选临时动画control，dry_run检查无键/值/插键/时间/选中/Undo/plugin/UI改变。
2. 完整UI五种mode、normal/special ticks、overshoot/live、九fraction预设/饼图、右键显示状态/偏好、DPI/Qt5/6/dock restore逐项检查，Script Editor无Fatal。选择不同scene/Graph Editor/DopeSheet/ChannelBox/Time Slider范围，对照原行为。
3. 测相邻键、未插当前帧、连续/非连续多key、weighted tangent/角度/默认值。五种模式和overshoot输出符合目标，Undo/Redo一次恢复所有API键/值；端点外/共享/锁引用/锁层/不支持driver拒绝。
4. 开启live press/drag/release，整gesture只有一次Undo；关闭、切模式、取消/错误、改选择/对象重命名或删除时不得留下无Undo预览。关闭后没有遗留idle callback、Undo状态始终保持开启。鼠标context/无拖动release/换工具finalize正确，不全局注册热键。
5. 所选最佳动画层/BaseAnimation fallback与多层/selected/locked/mute/solo/嵌套层/动画层默认值/不同旋转组合检查。普通隔离检查只覆盖简单选中层，不能代替生产rig。
6. keyhammer临时多curve并集闭区间、外部选键隔离、取消/失败回滚和progress finally检查；tick色场景Undo实际限制单独记录。若显式建立Shelf，图标与完整候选show_ui命令正确。
7. 记录真实版本与未通过项，在候选修复重验，不运行旧网络/删目录安装器。晋级清单自带完整plugin/resources/docs/tests/注册动作；通过全部人工验收后才apply，晋级后重启避免已加载候选路径冲突。
