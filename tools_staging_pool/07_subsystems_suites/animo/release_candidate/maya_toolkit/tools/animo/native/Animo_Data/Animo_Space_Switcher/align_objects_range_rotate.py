from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import os
import sys

MARK_COLOR = "#4ca6e6"
MARK_OPACITY = 0.40


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


def align_range_rotate():
    sel = cmds.ls(sl=True)
    
    if len(sel) < 2:
        cmds.inViewMessage(amg='<span style="color:#f58b3a;">Select at least 2 objects</span>', pos="botCenter", fade=True)
        return
    
    target = sel[-1]
    sources = sel[:-1]
    current_time = cmds.currentTime(query=True)
    
    min_time = int(cmds.playbackOptions(query=True, min=True))
    max_time = int(cmds.playbackOptions(query=True, max=True))
    
    keys = cmds.keyframe(target, query=True, time=(min_time, max_time))
    
    if not keys:
        marker = load_mark_frame()
        if marker:
            marker.mark_current_frame(auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
        
        cmds.matchTransform(sources, target, pos=False, rot=True)
        for src in sources:
            cmds.setKeyframe(src, attribute=["tx", "ty", "tz", "rx", "ry", "rz"])
        return
    
    keys = sorted(set([int(k) for k in keys]))
    
    marker = load_mark_frame()
    if marker:
        marker.mark_range(keys[0], keys[-1], auto_fade=True, color=MARK_COLOR, opacity=MARK_OPACITY)
    
    original_eval_mode = cmds.evaluationManager(query=True, mode=True)
    cmds.undoInfo(openChunk=True, chunkName="Align Range Rotate")
    cmds.evaluationManager(mode="off")
    cmds.refresh(suspend=True)
    
    try:
        for key in keys:
            cmds.currentTime(key)
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
