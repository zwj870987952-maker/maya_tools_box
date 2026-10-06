import maya.cmds as cmds
import json
import os
import tempfile

copied_key_times = []

def get_temp_path():
    return tempfile.gettempdir()

def frame_matches(frame, keys_list, tol=0.0001):
    for k in keys_list:
        if abs(k - frame) < tol:
            return True
    return False

def clear_object_keys(objects):
    for obj in objects:
        try:
            cmds.cutKey(obj, clear=True)
        except:
            pass

def paste_key_times_pose_to_pose():
    global copied_key_times
    json_data = None
    try:
        cmds.undoInfo(openChunk=True)
        
        desktop_path = get_temp_path()
        json_filename = "esn_key_times.json"
        json_path = os.path.join(desktop_path, json_filename)
        
        hasSourceKeys = True
        
        if not os.path.exists(json_path):
            allKeys = copied_key_times[:]
            if not allKeys:
                cmds.warning("No key times found. Please use Copy button first.")
                return
        else:
            try:
                with open(json_path, "r") as f:
                    json_data = json.load(f)
                
                allKeys = json_data.get("key_times", [])
                hasSourceKeys = json_data.get("has_keys", len(allKeys) > 0)
                
                if not allKeys and hasSourceKeys:
                    cmds.warning("No key times found in JSON file. Please use Copy button first.")
                    return
                    
            except:
                allKeys = copied_key_times[:]
                if not allKeys:
                    cmds.warning("No fallback key times available.")
                    return
        
        sel = cmds.ls(sl=True)
        if len(sel) == 0:
            return

        objects = cmds.ls(sl=1)

        if not allKeys:
            cmds.waitCursor(state=True)
            clear_object_keys(objects)
            cmds.waitCursor(state=False)
            return

        CT = cmds.currentTime(q=1)

        if json_data:
            stored_range = json_data.get("playback_range", [int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))])
        else:
            stored_range = [int(cmds.playbackOptions(q=True, min=True)), int(cmds.playbackOptions(q=True, max=True))]
        Min = stored_range[0]
        Max = stored_range[1]

        cmds.waitCursor(state=True)
        
        objWithNoKeys = []
        for obj in objects:
            keyframes = cmds.keyframe(obj, q=1)
            if keyframes is None:
                objWithNoKeys.append(obj)

        if objWithNoKeys:
            for obj in objWithNoKeys:
                cmds.setKeyframe(obj, t=allKeys[0])

        for key in allKeys:
            cmds.setKeyframe(objects, i=True, t=key)

        for obj in objects:
            objFrames = cmds.keyframe(obj, q=1, t=(Min, Max))
            if not objFrames:
                continue
            uniqueFrames = []
            for objFrame in objFrames:
                if objFrame not in uniqueFrames:
                    uniqueFrames.append(objFrame)
            for frame in uniqueFrames:
                if not frame_matches(frame, allKeys):
                    cmds.cutKey(obj, t=(frame, frame))

        cmds.currentTime(CT)
        cmds.waitCursor(state=False)
        
    except:
        cmds.waitCursor(state=False)
    finally:
        cmds.undoInfo(closeChunk=True)

paste_key_times_pose_to_pose()