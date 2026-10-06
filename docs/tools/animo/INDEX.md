# Animo 功能与代码目录

> 待整理候选，所有入口均未通过 Maya 人工检验。原始源码保留在本机。

540 个库入口 + 13 个套件补充入口；573 条原显示记录按文件路径去重。

每个操作使用固定 operation ID；当前选择、通道、时间范围和原生配置由 Maya 上下文提供。

| 分类 | 中文用途 | 入口数 | 详细索引 |
| --- | --- | ---: | --- |
| Align | 对齐 | 6 | [对齐](categories/align.md) |
| Animation Layers | 动画层 | 11 | [动画层](categories/animation_layers.md) |
| Blend to Default | 混合至默认值 | 16 | [混合至默认值](categories/blend_to_default.md) |
| Blend to Ease | 混合至缓动 | 12 | [混合至缓动](categories/blend_to_ease.md) |
| Blend to Infinity | 混合至 Infinity | 12 | [混合至 Infinity](categories/blend_to_infinity.md) |
| Blend to Mirror | 混合至镜像 | 12 | [混合至镜像](categories/blend_to_mirror.md) |
| Blend to Neighbors | 混合至邻帧 | 16 | [混合至邻帧](categories/blend_to_neighbors.md) |
| Blend to World | 混合至世界空间 | 16 | [混合至世界空间](categories/blend_to_world.md) |
| Channel Box | 通道面板 | 1 | [通道面板](categories/channel_box.md) |
| Color Keys | 关键帧颜色 | 3 | [关键帧颜色](categories/color_keys.md) |
| Connect To Neighbor | 衔接邻帧 | 12 | [衔接邻帧](categories/connect_to_neighbor.md) |
| Constraints | 约束 | 4 | [约束](categories/constraints.md) |
| Copy Animation | 跨场景动画传递 | 5 | [跨场景动画传递](categories/copy_animation.md) |
| Copy Pose | 姿态传递 | 3 | [姿态传递](categories/copy_pose.md) |
| Ease | 缓入缓出 | 16 | [缓入缓出](categories/ease.md) |
| Fast Bake | 快速烘焙 | 7 | [快速烘焙](categories/fast_bake.md) |
| Global Offset | 全局偏移 | 1 | [全局偏移](categories/global_offset.md) |
| Graph Editor | 曲线编辑器 | 10 | [曲线编辑器](categories/graph_editor.md) |
| Keys | 关键帧操作 | 12 | [关键帧操作](categories/keys.md) |
| Keys Time | 关键帧时间传递 | 9 | [关键帧时间传递](categories/keys_time.md) |
| Locator | 定位器与父级 | 8 | [定位器与父级](categories/locator.md) |
| Manipulator | 操纵器 | 3 | [操纵器](categories/manipulator.md) |
| Mirror | 姿态与动画镜像 | 4 | [姿态与动画镜像](categories/mirror.md) |
| Nudge Keys | 关键帧微移 | 11 | [关键帧微移](categories/nudge_keys.md) |
| Offset Keys | 关键帧偏移 | 9 | [关键帧偏移](categories/offset_keys.md) |
| Physics | 物理辅助 | 1 | [物理辅助](categories/physics.md) |
| Pickify (Selection Sets) | 选择集 | 1 | [选择集](categories/pickify_selection_sets.md) |
| Push and Pull | 推拉幅度 | 16 | [推拉幅度](categories/push_and_pull.md) |
| Recommended | 推荐工具 | 1 | [推荐工具](categories/recommended.md) |
| Reset Pose | 姿态复位 | 5 | [姿态复位](categories/reset_pose.md) |
| Rotate Order | 旋转顺序 | 6 | [旋转顺序](categories/rotate_order.md) |
| Scale Average | 围绕均值缩放 | 16 | [围绕均值缩放](categories/scale_average.md) |
| Scale Left | 围绕左侧缩放 | 16 | [围绕左侧缩放](categories/scale_left.md) |
| Scale Right | 围绕右侧缩放 | 16 | [围绕右侧缩放](categories/scale_right.md) |
| Scale from Average | 从均值缩放 | 16 | [从均值缩放](categories/scale_from_average.md) |
| Scale from Default | 从默认值缩放 | 16 | [从默认值缩放](categories/scale_from_default.md) |
| Scale from Left | 从左侧缩放 | 16 | [从左侧缩放](categories/scale_from_left.md) |
| Scale from Right | 从右侧缩放 | 16 | [从右侧缩放](categories/scale_from_right.md) |
| Selection | 选择管理 | 9 | [选择管理](categories/selection.md) |
| Simplify - Bake | 简化与烘焙 | 12 | [简化与烘焙](categories/simplify_minus_bake.md) |
| Smooth - Harsh | 平滑与强化 | 12 | [平滑与强化](categories/smooth_minus_harsh.md) |
| Spacify | 临时空间切换 | 11 | [临时空间切换](categories/spacify.md) |
| Suite UI | 完整套件入口 | 13 | [完整套件入口](categories/suite_ui.md) |
| Tangents | 切线 | 9 | [切线](categories/tangents.md) |
| Temp Pivot | 临时轴心 | 2 | [临时轴心](categories/temp_pivot.md) |
| Time Offset | 时间偏移 | 16 | [时间偏移](categories/time_offset.md) |
| Time Offset Stagger | 错开时间 | 16 | [错开时间](categories/time_offset_stagger.md) |
| Tracify (Track Arcs) | 运动弧线 | 4 | [运动弧线](categories/tracify_track_arcs.md) |
| Tween | 补间 | 17 | [补间](categories/tween.md) |
| Tweenify (Sliders Quick Pop Up) | 滑块弹出面板 | 1 | [滑块弹出面板](categories/tweenify_sliders_quick_pop_up.md) |
| Twosify | 风格化动画 | 4 | [风格化动画](categories/twosify.md) |
| Viewport Display | 视口显示 | 41 | [视口显示](categories/viewport_display.md) |
| Wave and Noise | 波形与噪声 | 16 | [波形与噪声](categories/wave_and_noise.md) |
| Xform Relationships | 相对变换关系 | 3 | [相对变换关系](categories/xform_relationships.md) |
| Xform World | 世界变换 | 6 | [世界变换](categories/xform_world.md) |
