import maya.cmds as cmds
import time

_last_frame_time = 0

def smart_go_to_next_frame():
    global _last_frame_time
    current_time = time.time()
    time_since_last = current_time - _last_frame_time
    _last_frame_time = current_time
    
    current_frame = cmds.currentTime(query=True)
    
    if time_since_last > 0.15:
        cmds.currentTime(current_frame + 1, edit=True, update=True)
    else:
        cmds.currentTime(current_frame + 1, edit=True, update=False)

smart_go_to_next_frame()
