import maya.cmds as cmds
import json
import os
import tempfile

copied_key_times = []

def get_temp_path():
    return tempfile.gettempdir()

def show_feedback_message(message):
    try:
        cmds.inViewMessage(
            amg=message,
            pos='botCenter',
            fade=True,
            fadeStayTime=1500,
            fadeOutTime=500
        )
    except:
        pass

def copy_key_times_pose_to_pose():
    try:
        cmds.undoInfo(openChunk=True)
        
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            return
        
        Min = int(cmds.playbackOptions(q=True, min=True))
        Max = int(cmds.playbackOptions(q=True, max=True))
        
        allKeys = cmds.keyframe(sel, q=True, t=(Min, Max))
        
        if allKeys:
            key_times = list(set(allKeys))
            key_times.sort()
        else:
            key_times = []
        
        desktop_path = get_temp_path()
        json_filename = "esn_key_times.json"
        json_path = os.path.join(desktop_path, json_filename)
        
        json_data = {
            "key_times": key_times,
            "playback_range": [Min, Max],
            "source_objects": sel,
            "has_keys": len(key_times) > 0
        }
        
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
        
        global copied_key_times
        copied_key_times = key_times
        
        show_feedback_message("Copied Key Time")
                
    except:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)

copy_key_times_pose_to_pose()
