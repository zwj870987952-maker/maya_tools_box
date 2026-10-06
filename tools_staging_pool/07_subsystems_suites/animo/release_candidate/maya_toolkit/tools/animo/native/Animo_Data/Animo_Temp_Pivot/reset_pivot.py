import maya.cmds as cmds
import maya.api.OpenMaya as om
import os
import json


def get_prefs_path():
    if os.name == 'nt':
        docs = os.path.join(os.environ['USERPROFILE'], "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    else:
        docs = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Prefs")
    if not os.path.exists(docs):
        os.makedirs(docs)
    return os.path.join(docs, "temp_pivot.json")


def load_offsets():
    path = get_prefs_path()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"single_offsets": {}, "multi_offsets": []}


def save_offsets(data):
    path = get_prefs_path()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def reset_pivot():
    """Reset stored pivot offset for selected objects to default (object center/last selected)"""
    
    pivot_null = "Animo_Pivot"
    pivot_set = "Animo_Pivot_objects"
    
    # Check if pivot tool is active
    if cmds.objExists(pivot_null) and cmds.objExists(pivot_set):
        sel = cmds.sets(pivot_set, q=True) or []
    else:
        sel = cmds.ls(selection=True)
    
    if not sel:
        cmds.warning("Nothing selected")
        return
    
    data = load_offsets()
    
    if len(sel) == 1:
        obj = sel[0]
        # Single object - reset to identity (pivot at object center)
        identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        data["single_offsets"][obj] = identity
        
        # If pivot tool active, snap pivot point to object center
        if cmds.objExists(pivot_null):
            pos = cmds.xform(obj, q=True, ws=True, rp=True)
            cmds.xform(pivot_null, ws=True, piv=pos)
        
        print(f"Reset pivot offset for '{obj}' to object center")
    else:
        # Multi selection - reset to last selected object position
        sel_sorted = sorted(sel)
        last_obj = sel[-1]
        
        offsets = {}
        last_obj_mtx = om.MMatrix(cmds.xform(last_obj, q=True, ws=True, matrix=True))
        
        for obj in sel:
            obj_mtx = om.MMatrix(cmds.xform(obj, q=True, ws=True, matrix=True))
            # Offset from this object to last selected (pivot will be at last selected)
            offset_mtx = last_obj_mtx * obj_mtx.inverse()
            offsets[obj] = list(offset_mtx)
        
        # Find and update existing group or add new
        found = False
        for group in data["multi_offsets"]:
            if sorted(group["objects"]) == sel_sorted:
                group["offsets"] = offsets
                found = True
                break
        
        if not found:
            data["multi_offsets"].append({"objects": list(sel), "offsets": offsets})
        
        # If pivot tool active, snap pivot point to last selected object
        if cmds.objExists(pivot_null):
            pos = cmds.xform(last_obj, q=True, ws=True, rp=True)
            cmds.xform(pivot_null, ws=True, piv=pos)
        
        print(f"Reset pivot offset for {len(sel)} objects to last selected '{last_obj}'")
    
    save_offsets(data)


reset_pivot()