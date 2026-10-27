# -*- coding: utf-8 -*-
"""
业务工具层：自动注册内置工具到统一工具注册中心 (ToolRegistry)
"""
from __future__ import absolute_import, division, print_function

from ..framework.registry import ToolRegistry

from .namespace_clean import NamespaceCleanTool
from .euler_winding import EulerWindingTool
from .weights_copy import WeightsCopyTool
from .fbx_export import FBXExportTool
from .material_transfer import MaterialTransferTool
from .fbx_diff import FBXDiffSyncTool
from .advanced_skeleton_mirror import AdvancedSkeletonMirrorTool
from .advanced_skeleton_animation import AdvancedSkeletonAnimationTool
from .stagger_offset import StaggerOffsetTool
from .stagger_gui import StaggerGuiTool
from .bh_wave_it import WaveItTool
from .bh_local_nudge import LocalNudgeTool
from .keyframe_overlap import KeyframeOverlapTool
from .back2origin_v05_gaiv3 import Back2OriginTool
from .animirror_v2_0 import AnimirrorV2Tool
from .gimbal_lock_fix import GimbalFixTool
from .anim_filters import AnimFiltersTool
from .tweener_v1_0_2 import TweenerTool
from .root_motion_bake import RootMotionBakeTool
from .copy_animation import CopyAnimationTool
from .shift_animation_v3_2 import ShiftAnimationTool
from .overslapper import OverslapperTool
from .spring_magic_v3_5a import SpringMagicTool
from .cg_shake_py3 import CgShakeTool
from .directional_cycle_tool_v1_1 import DirectionalCycleTool
from .retime_tools import RetimeToolsTool
from .dof_control_v1_0 import DofControlTool
from .eblabs_screenspace import ScreenSpaceTool
from .eblabs_whiskey import WhiskeyTool
from .anim_layer_bookmark_trimmer import AnimLayerBookmarkTrimmerTool
from .anim_layer_keyframe_bookmark import AnimLayerKeyframeBookmarkTool
from .anim_layer_key_runner import AnimLayerKeyRunnerTool
from .anim_layer_v4_0 import AnimLayerSuiteTool
from .anim_mirror_helper_v1_1 import AnimMirrorHelperTool
from .anim_polish_premium_v1_23 import AnimPolishTool
from .animation_retarget import AnimationRetargetTool
from .bh_aim_tools_v1_1 import BhAimTool
from .bh_speedlines import SpeedLinesTool
from .brs_loc_transfer import LocatorTransferTool
from .brs_smooth_mocap import SmoothMocapTool
from .fd_multi_space import MultiSpaceTool
from .ik_fk_switch import IKFKTool
from .jop_retarget_anim import JopRetargetTool
from .kf_animrig_ikfk import KFAnimRigTool
from .lock_to_world import LockToWorldTool
from .keyframe_reduction import KeyframeReductionTool
from .timeline_marker import TimelineMarkerTool
from .mov_playblast import MovPlayblastTool
from .physics_tools import PhysicsToolsTool
from .pose_matcher import PoseMatcherTool
from .pose_transfer_remote import PoseTransferRemoteTool
from .shape_animation_tool import ShapeAnimationTool
from .sword_anim_polishing_tool_v4 import SwordAnimPolishTool
from .tb_anim_tools import TBAnimToolsTool
from .timeline_enhanced import TimelineEnhancedTool
from .velocity_calculator import VelocityCalculatorTool
from .w_retarget_tool import WRetargetTool

# 统一自动注册内置工具
ALL_TOOL_CLASSES = [
    NamespaceCleanTool,
    EulerWindingTool,
    WeightsCopyTool,
    FBXExportTool,
    MaterialTransferTool,
    FBXDiffSyncTool,
    AdvancedSkeletonMirrorTool,
    AdvancedSkeletonAnimationTool,
    StaggerOffsetTool,
    StaggerGuiTool,
    WaveItTool,
    LocalNudgeTool,
    KeyframeOverlapTool,
    Back2OriginTool,
    AnimirrorV2Tool,
    GimbalFixTool,
    AnimFiltersTool,
    TweenerTool,
    RootMotionBakeTool,
    CopyAnimationTool,
    ShiftAnimationTool,
    OverslapperTool,
    SpringMagicTool,
    CgShakeTool,
    DirectionalCycleTool,
    RetimeToolsTool,
    DofControlTool,
    ScreenSpaceTool,
    WhiskeyTool,
    AnimLayerBookmarkTrimmerTool,
    AnimLayerKeyframeBookmarkTool,
    AnimLayerKeyRunnerTool,
    AnimLayerSuiteTool,
    AnimMirrorHelperTool,
    AnimPolishTool,
    AnimationRetargetTool,
    BhAimTool,
    SpeedLinesTool,
    LocatorTransferTool,
    SmoothMocapTool,
    MultiSpaceTool,
    IKFKTool,
    JopRetargetTool,
    KFAnimRigTool,
    LockToWorldTool,
    KeyframeReductionTool,
    TimelineMarkerTool,
    MovPlayblastTool,
    PhysicsToolsTool,
    PoseMatcherTool,
    PoseTransferRemoteTool,
    ShapeAnimationTool,
    SwordAnimPolishTool,
    TBAnimToolsTool,
    TimelineEnhancedTool,
    VelocityCalculatorTool,
    WRetargetTool,
]


def register_all_builtin_tools():
    """注册所有内置工具"""
    registered = []
    for cls in ALL_TOOL_CLASSES:
        tool_instance = ToolRegistry.register(cls)
        registered.append(tool_instance)
    return registered


# 导入时自动完成注册
register_all_builtin_tools()

__all__ = [
    "NamespaceCleanTool",
    "EulerWindingTool",
    "WeightsCopyTool",
    "FBXExportTool",
    "MaterialTransferTool",
    "FBXDiffSyncTool",
    "AdvancedSkeletonMirrorTool",
    "AdvancedSkeletonAnimationTool",
    "StaggerOffsetTool",
    "StaggerGuiTool",
    "WaveItTool",
    "LocalNudgeTool",
    "KeyframeOverlapTool",
    "Back2OriginTool",
    "AnimirrorV2Tool",
    "GimbalFixTool",
    "AnimFiltersTool",
    "TweenerTool",
    "RootMotionBakeTool",
    "CopyAnimationTool",
    "ShiftAnimationTool",
    "OverslapperTool",
    "SpringMagicTool",
    "CgShakeTool",
    "DirectionalCycleTool",
    "RetimeToolsTool",
    "DofControlTool",
    "ScreenSpaceTool",
    "WhiskeyTool",
    "AnimLayerBookmarkTrimmerTool",
    "AnimLayerKeyframeBookmarkTool",
    "AnimLayerKeyRunnerTool",
    "AnimLayerSuiteTool",
    "AnimMirrorHelperTool",
    "AnimPolishTool",
    "AnimationRetargetTool",
    "BhAimTool",
    "SpeedLinesTool",
    "LocatorTransferTool",
    "SmoothMocapTool",
    "MultiSpaceTool",
    "IKFKTool",
    "JopRetargetTool",
    "KFAnimRigTool",
    "LockToWorldTool",
    "KeyframeReductionTool",
    "TimelineMarkerTool",
    "MovPlayblastTool",
    "PhysicsToolsTool",
    "PoseMatcherTool",
    "PoseTransferRemoteTool",
    "ShapeAnimationTool",
    "SwordAnimPolishTool",
    "TBAnimToolsTool",
    "TimelineEnhancedTool",
    "VelocityCalculatorTool",
    "WRetargetTool",
    "register_all_builtin_tools",
]
