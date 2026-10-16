"""Reviewed ADV 6.640 animator entrypoints, not an arbitrary MEL dispatcher."""


def operation(label, proc, binding='ui', mode='api', window=None, selection=0,
              effect='scene', requirements='', **extra):
    return dict(label=label, proc=proc, binding=binding, execution_mode=mode,
                window=window, selection_min=selection, effect=effect,
                requirements=requirements, verification='static_review', **extra)


OPERATIONS = {
    'pose_copy': operation('Pose / Copy', 'asCopyToClipBoard', 'ui_zero', effect='clipboard_file'),
    'pose_paste': operation('Pose / Paste', 'asPasteFromClipBoard', 'ui_zero', requirements='ADV 姿态剪贴板文件'),
    'pose_reset': operation('Pose / Reset', 'asGoToBuildPose', requirements='buildPose.udAttr'),
    'pose_tpose': operation('Pose / Tpose', 'asGoToTPose', requirements='buildPose 与 ADV 双臂 Tpose 关节'),
    'mirror': operation('Pose / Mirror', 'asMirror', 'mirror'),
    'mirror_options': operation('Pose / Mirror Options', 'asMirrorOptions', 'mirror', 'interactive_ui', 'asMirrorOptions', effect='ui'),
    'animation_copy': operation('Anim / Copy', 'asCopyToClipBoard', 'ui_one', effect='clipboard_file', requirements='无目标动画层；复制全部原生曲线，不裁剪时间'),
    'animation_paste': operation('Anim / Paste', 'asPasteFromClipBoard', 'ui_one', requirements='ADV 动画剪贴板文件；无目标动画层'),
    'animation_clean': operation('Anim / Clean', 'asDeleteStaticChannels', mode='interactive_dialog', requirements='原生确认对话框；删除整个 ControlSet 的静态曲线'),
    'bake_options': operation('Anim / Bake', 'asAnimBake', mode='interactive_ui', window='asAnimBake', effect='ui'),
    'switch_fkik': operation('Anim / SwitchFKIK', 'asAutoSwitchFKIK', 'none', selection=1, requirements='选中 FKIK 控制器或相关肢体控制器'),
    'switch_pivot': operation('Anim / SwitchPivot', 'asAutoSwitchPivot', 'none', selection=2, exact_selection=2, requirements='目标、带 Extra 父节点的控制器，顺序重要'),
    'pivot_control': operation('Anim / PivotControl', 'asPivotControl', 'none', selection=1, requirements='旋转/缩放 pivot 无已有输入连接'),
    'quick_ik': operation('Anim / QuickIK', 'asQuickIK', 'none', selection=2, exact_selection=2, requirements='同一关节链的起止控制器'),
    'humanik_options': operation('Anim / HumanIK', 'asHumanIKUI', mode='interactive_ui', window='asHumanIK', effect='ui'),
    'mocap_matcher': operation('Anim / MoCapMatcher', 'asMoCapMatcherUI', mode='interactive_ui', window='asMappingUI', effect='ui', requirements='执行匹配需要源动捕骨架和匹配模板'),
    'mocap_library': operation('Anim / MoCapLibrary', 'asMoCapLibraryUI', mode='interactive_ui', window='asMoCapLibraryUI', effect='ui', requirements='Y-up；具体素材可能需要另行下载'),
    'arkit_options': operation('Anim / Connect ARKit', 'asConnectARKitUI', mode='interactive_ui', window='asConnectARKitUI', effect='ui', requirements='连接时需要 ARKit blendShape 和 ADV Face 控制器'),
    'connect_mocapx': operation('Anim / Connect MocapX', 'asConnectMocapX', requirements='根命名空间；MocapX 数据属性与 ADV Face 控制器；设备流未验证'),
    'metahuman_options': operation('Anim / MetaHumanAnimator', 'asMetaHumanAnimatorUI', mode='interactive_ui', window='asMetaHumanAnimatorUI', effect='ui', requirements='连接时需要 MetaHumanAnimator FBX 数据'),
    'video_mocap_options': operation('Anim / VideoMoCap', 'asVideoMoCapUI', mode='interactive_ui', window='asVideoMoCapUI', effect='ui', requirements='Windows；追踪需 asVideoMoCap 外部组件及视频'),
    'lipsync_options': operation('Anim / Auto lipsync', 'asAutoLipSyncUI', mode='interactive_ui', window='asAutoLipSyncUI', effect='ui', requirements='处理需 Montreal Forced Aligner、音频与文本'),
    'audio2face_options': operation('Anim / Audio2Face', 'asAudio2FaceUI', mode='interactive_ui', window='asAudio2FaceUI', effect='ui', requirements='连接时需要 Audio2Face blendShape 数据'),
    'deformable_options': operation('Anim / Deformable', 'asDeformableUI', mode='interactive_ui', window='asDeformableUI', effect='ui'),
    'time_echo_options': operation('Anim / TimeEcho', 'asTimeEchoUI', mode='interactive_ui', window='asTimeEchoUI', effect='ui'),
    'dynamics_add': operation('Dynamics / Add Standard', 'asDynAdd', selection=2, requirements='同链 FK 控制器与对应变形关节'),
    'dynamics_add_hair': operation('Dynamics / Add HairSystem', 'asDynAddHairSystem', selection=2, requirements='同链 FK 控制器；Maya nHair'),
    'dynamics_remove': operation('Dynamics / Remove', 'asDynRemove', selection=1, requirements='已添加 ADV dynamics 的 FK 控制器'),
    'dynamics_initial_state': operation('Dynamics / Set Initial State', 'asDynSetInitialState', requirements='作用于全场景动力学系统，并非仅目标角色'),
    'dynamics_playback': operation('Dynamics / Interactive Playback', 'asDynSetInteractivePlayback', mode='interactive_playback', effect='playback'),
    'dynamics_bake': operation('Dynamics / Bake', 'asDynBake', mode='interactive_dialog', requirements='全场景 Dynamics 组；原生确认对话框'),
    'parent_constraint': operation('Parent / Add parent constraint', 'asParentAdd', 'ui_zero', selection=2, requirements='父对象在前、子控制器最后'),
    'parent_constraint_extra': operation('Parent / Add parent constraint Extra', 'asParentAdd', 'ui_one', selection=2, requirements='子控制器需要 Extra 父节点'),
    'walk_designer': operation('Tools / WalkDesigner', 'asWalkDesigner', 'none', 'interactive_ui', 'asWalkDesigner', effect='ui_and_temporary_scene_nodes'),
    'animation_tester': operation('Tools / AnimationTester', 'asAnimationTesterUI', 'none', 'interactive_ui', 'asAnimationTester', effect='ui', requirements='部分内部按钮只面向无命名空间绑定测试，生产动画勿直接点 Apply'),
    'align_fk_to_ik': operation('FK/IK / Align FK to IK pose', 'asAlignFK2IK', 'limb', requirements='limb，例如 Arm_L；对齐 FK 到 IK 姿态，不切换'),
    'align_ik_to_fk': operation('FK/IK / Align IK to FK pose', 'asAlignIK2FK', 'limb', requirements='limb；对齐 IK 到 FK 姿态，不切换'),
    'switch_fk_to_ik': operation('FK/IK / Switch FK to IK', 'asSwitchFK2IK', 'limb', requirements='limb，例如 Arm_L'),
    'switch_ik_to_fk': operation('FK/IK / Switch IK to FK', 'asSwitchIK2FK', 'limb', requirements='limb，例如 Arm_L'),
    'bake_fk_to_ik': operation('Bake / FK to IK', 'asAnimBakeFKIK', 'bake_one', requirements='limb；无目标动画层'),
    'bake_ik_to_fk': operation('Bake / IK to FK', 'asAnimBakeFKIK', 'bake_zero', requirements='limb；无目标动画层'),
    'bake_extra_to_controls': operation('Bake / ExtraControls to Controls', 'asAnimBakeExtra', requirements='匹配的 Extra 控制器；原生会替换整条曲线，范围外键不保证保留'),
    'bake_controls_to_extra': operation('Bake / Controls to ExtraControls', 'asAnimBakeToExtra', requirements='匹配的 Extra 控制器；移动整条动画曲线，不按时间裁剪'),
    'bake_quick_ik': operation('Bake / QuickIK to FKControls', 'asAnimBakeQuickIK', requirements='已建立 QuickIK；烘焙后移除 QuickIK'),
    'key': operation('Selector / Key', 'asKey', 'nodes', selection=1),
    'linear_key': operation('Selector / Linear Key', 'asLinearKey', 'nodes', selection=1),
}

RANGE_OPERATIONS = {'bake_fk_to_ik', 'bake_ik_to_fk', 'bake_extra_to_controls', 'bake_quick_ik'}

# Record actual evidence without treating UI dispatch as completed animation work.
from pathlib import Path
import json
_evidence_file = Path(__file__).with_name('verification.json')
if _evidence_file.is_file():
    for _name, _record in json.loads(_evidence_file.read_text(encoding='utf-8')).get('operations', {}).items():
        if _name in OPERATIONS:
            OPERATIONS[_name]['verification'] = _record['scope']
for _name in ('pose_paste', 'animation_paste'):
    OPERATIONS[_name]['undo'] = 'native reference removal clears Maya Undo history; explicit opt-in required'
