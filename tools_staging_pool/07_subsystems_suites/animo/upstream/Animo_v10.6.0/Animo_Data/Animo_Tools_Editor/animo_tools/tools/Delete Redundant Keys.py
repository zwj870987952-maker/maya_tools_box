import maya.cmds as cmds
import maya.mel as mel

def get_target_curves(sel):
    graph_curves = cmds.keyframe(query=True, name=True, selected=True)
    if graph_curves:
        return graph_curves
    
    return cmds.keyframe(sel, query=True, name=True)

def delete_redundant_keys():
    sel = cmds.ls(selection=True)
    if not sel:
        return
    
    cmds.waitCursor(state=True)
    
    try:
        anim_curves = get_target_curves(sel)
        if not anim_curves:
            cmds.waitCursor(state=False)
            return
        
        keys_deleted = 0
        
        for curve in anim_curves:
            if not cmds.objExists(curve):
                continue
            
            key_values = cmds.keyframe(curve, query=True, valueChange=True)
            key_times = cmds.keyframe(curve, query=True, timeChange=True)
            
            if not key_values or not key_times:
                continue
            
            if len(key_values) == 1:
                continue
            
            indices_to_delete = []
            
            for i in range(1, len(key_values) - 1):
                prev_val = key_values[i - 1]
                curr_val = key_values[i]
                next_val = key_values[i + 1]
                
                if abs(prev_val - curr_val) < 0.0001 and abs(curr_val - next_val) < 0.0001:
                    indices_to_delete.append(i)
            
            for idx in reversed(indices_to_delete):
                cmds.cutKey(curve, index=(idx, idx), clear=True)
                keys_deleted += 1
    
    finally:
        cmds.waitCursor(state=False)

delete_redundant_keys()