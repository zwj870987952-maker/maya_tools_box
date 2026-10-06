from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.mel as mel
import os
import sys

MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40
BAKE_KEYS_OPTION_VAR = "XformAlignUI_bakeKeys"


def is_bake_keys_enabled():
    if cmds.optionVar(exists=BAKE_KEYS_OPTION_VAR):
        return cmds.optionVar(q=BAKE_KEYS_OPTION_VAR) == 1
    return True


def load_mark_frame():
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.path.join(cmds.internalVar(userAppDir=True), "scripts", "Animo_Data", "Animo_Space_Switcher")
    
    if folder not in sys.path:
        sys.path.insert(0, folder)
    
    try:
        import mark_frame
        return mark_frame
    except ImportError:
        return None


def get_timeline_range():
    playback_slider = mel.eval('$tmp = $gPlayBackSlider')
    range_array = cmds.timeControl(playback_slider, query=True, rangeArray=True)
    start = int(range_array[0])
    end = int(range_array[1]) - 1
    if end > start:
        return start, end
    return None


def align_rotate():
    sel = cmds.ls(sl=True)
    
    if len(sel) < 2:
        cmds.inViewMessage(amg='<span style="color:#f58b3a;">Select at least 2 objects</span>', pos="botCenter", fade=True)
        return
    
    target = sel[-1]
    sources = sel[:-1]
    
    timeline_range = get_timeline_range()
    
    if timeline_range:
        align_range_rotate(sources, target, timeline_range[0], timeline_range[1])
    else:
        marker = load_mark_frame()
        if marker:
            marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
        
        cmds.matchTransform(sources, target, pos=False, rot=True)
        for src in sources:
            cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])


def align_range_rotate(sources, target, start_frame, end_frame):
    current_time = cmds.currentTime(query=True)
    
    bake_keys_mode = is_bake_keys_enabled()
    
    if bake_keys_mode:
        keys = cmds.keyframe(target, query=True, time=(start_frame, end_frame))
        frames_to_process = sorted(set([int(k) for k in keys])) if keys else None
    else:
        frames_to_process = list(range(start_frame, end_frame + 1))
    
    if not frames_to_process:
        marker = load_mark_frame()
        if marker:
            marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
        
        cmds.matchTransform(sources, target, pos=False, rot=True)
        for src in sources:
            cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])
        return
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(frames_to_process[0], frames_to_process[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.undoInfo(openChunk=True, chunkName="Align Range Rotate")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for frame in frames_to_process:
            cmds.currentTime(frame)
            cmds.matchTransform(sources, target, pos=False, rot=True)
            for src in sources:
                cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])
    finally:
        try:
            cmds.currentTime(current_time)
        except:
            pass
        try:
            cmds.refresh(suspend=False)
        except:
            pass
        try:
            if original_eval_mode:
                cmds.evaluationManager(mode=original_eval_mode[0])
        except:
            pass
        try:
            cmds.undoInfo(closeChunk=True)
        except:
            pass
