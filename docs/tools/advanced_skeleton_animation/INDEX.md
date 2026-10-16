# ADV 动画逐入口目录

状态：已转正，2026-10-16，Maya 2024 / ADV 6.640。46个入口有实测记录；14个仅验证窗口，MocapX 为模拟输入驱动验证。animRescue 加载时场景操作仍被拦截。

说明与调用见 [主文档](../advanced_skeleton_animation.md)。

| operation | 原生入口 | 执行方式 | 已检查范围 | 前提/影响 |
| --- | --- | --- | --- | --- |
| pose_copy | asCopyToClipBoard | api | maya_fixture_effect_checked | 见主文档通用前提 |
| pose_paste | asPasteFromClipBoard | api | maya_fixture_effect_checked | ADV 姿态剪贴板文件 |
| pose_reset | asGoToBuildPose | api | maya_call_and_undo_checked | buildPose.udAttr |
| pose_tpose | asGoToTPose | api | maya_call_and_undo_checked | buildPose 与 ADV 双臂 Tpose 关节 |
| mirror | asMirror | api | maya_call_and_undo_checked | 见主文档通用前提 |
| mirror_options | asMirrorOptions | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| animation_copy | asCopyToClipBoard | api | maya_fixture_effect_checked | 无目标动画层；复制全部原生曲线，不裁剪时间 |
| animation_paste | asPasteFromClipBoard | api | maya_fixture_effect_checked | ADV 动画剪贴板文件；无目标动画层 |
| animation_clean | asDeleteStaticChannels | interactive_dialog | maya_dialog_effect_and_undo_checked | 原生确认对话框；删除整个 ControlSet 的静态曲线 |
| bake_options | asAnimBake | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| switch_fkik | asAutoSwitchFKIK | api | maya_call_and_undo_checked | 选中 FKIK 控制器或相关肢体控制器 |
| switch_pivot | asAutoSwitchPivot | api | maya_fixture_effect_checked | 目标、带 Extra 父节点的控制器，顺序重要 |
| pivot_control | asPivotControl | api | maya_fixture_effect_checked | 旋转/缩放 pivot 无已有输入连接 |
| quick_ik | asQuickIK | api | maya_system_checked | 同一关节链的起止控制器 |
| humanik_options | asHumanIKUI | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| mocap_matcher | asMoCapMatcherUI | interactive_ui | maya_ui_open_checked | 执行匹配需要源动捕骨架和匹配模板 |
| mocap_library | asMoCapLibraryUI | interactive_ui | maya_ui_open_checked | Y-up；具体素材可能需要另行下载 |
| arkit_options | asConnectARKitUI | interactive_ui | maya_ui_open_checked | 连接时需要 ARKit blendShape 和 ADV Face 控制器 |
| connect_mocapx | asConnectMocapX | api | maya_fixture_wiring_and_undo_checked | 根命名空间；MocapX 数据属性与 ADV Face 控制器；设备流未验证 |
| metahuman_options | asMetaHumanAnimatorUI | interactive_ui | maya_ui_open_checked | 连接时需要 MetaHumanAnimator FBX 数据 |
| video_mocap_options | asVideoMoCapUI | interactive_ui | maya_ui_open_checked | Windows；追踪需 asVideoMoCap 外部组件及视频 |
| lipsync_options | asAutoLipSyncUI | interactive_ui | maya_ui_open_checked | 处理需 Montreal Forced Aligner、音频与文本 |
| audio2face_options | asAudio2FaceUI | interactive_ui | maya_ui_open_checked | 连接时需要 Audio2Face blendShape 数据 |
| deformable_options | asDeformableUI | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| time_echo_options | asTimeEchoUI | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| dynamics_add | asDynAdd | api | maya_system_checked | 同链 FK 控制器与对应变形关节 |
| dynamics_add_hair | asDynAddHairSystem | api | maya_system_checked | 同链 FK 控制器；Maya nHair |
| dynamics_remove | asDynRemove | api | maya_system_checked | 已添加 ADV dynamics 的 FK 控制器 |
| dynamics_initial_state | asDynSetInitialState | api | maya_system_checked | 作用于全场景动力学系统，并非仅目标角色 |
| dynamics_playback | asDynSetInteractivePlayback | interactive_playback | maya_playback_start_stop_checked | 见主文档通用前提 |
| dynamics_bake | asDynBake | interactive_dialog | maya_dialog_effect_and_undo_checked | 全场景 Dynamics 组；原生确认对话框 |
| parent_constraint | asParentAdd | api | maya_fixture_effect_checked | 父对象在前、子控制器最后 |
| parent_constraint_extra | asParentAdd | api | maya_fixture_effect_checked | 子控制器需要 Extra 父节点 |
| walk_designer | asWalkDesigner | interactive_ui | maya_ui_open_checked | 见主文档通用前提 |
| animation_tester | asAnimationTesterUI | interactive_ui | maya_ui_open_checked | 部分内部按钮只面向无命名空间绑定测试，生产动画勿直接点 Apply |
| align_fk_to_ik | asAlignFK2IK | api | maya_call_and_undo_checked | limb，例如 Arm_L；对齐 FK 到 IK 姿态，不切换 |
| align_ik_to_fk | asAlignIK2FK | api | maya_call_and_undo_checked | limb；对齐 IK 到 FK 姿态，不切换 |
| switch_fk_to_ik | asSwitchFK2IK | api | maya_call_and_undo_checked | limb，例如 Arm_L |
| switch_ik_to_fk | asSwitchIK2FK | api | maya_call_and_undo_checked | limb，例如 Arm_L |
| bake_fk_to_ik | asAnimBakeFKIK | api | maya_system_checked | limb；无目标动画层 |
| bake_ik_to_fk | asAnimBakeFKIK | api | maya_system_checked | limb；无目标动画层 |
| bake_extra_to_controls | asAnimBakeExtra | api | maya_fixture_effect_checked | 匹配的 Extra 控制器；原生会替换整条曲线，范围外键不保证保留 |
| bake_controls_to_extra | asAnimBakeToExtra | api | maya_fixture_effect_checked | 匹配的 Extra 控制器；移动整条动画曲线，不按时间裁剪 |
| bake_quick_ik | asAnimBakeQuickIK | api | maya_system_checked | 已建立 QuickIK；烘焙后移除 QuickIK |
| key | asKey | api | maya_fixture_effect_checked | 见主文档通用前提 |
| linear_key | asLinearKey | api | maya_fixture_effect_checked | 见主文档通用前提 |
