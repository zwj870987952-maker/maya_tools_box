import maya.cmds as cmds
import json
import os
import tempfile

def get_temp_path():
    return tempfile.gettempdir()

def paste_key_times_channels():
    try:
        desktop_path = get_temp_path()
        json_filename = "maya_key_timing.json"
        json_path = os.path.join(desktop_path, json_filename)
        
        if not os.path.exists(json_path):
            cmds.warning("JSON file not found. Please use Smart Copy first.")
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        if not data:
            cmds.warning("JSON is empty or invalid.")
            return

        selected = cmds.ls(sl=True)
        if not selected:
            cmds.warning("Please select at least one object.")
            return

        time_start = cmds.playbackOptions(q=True, min=True)
        time_end = cmds.playbackOptions(q=True, max=True)
        timeline_min = float(time_start)
        timeline_max = float(time_end)

        ref_obj = next(iter(data))

        for obj in selected:
            obj_key_data = data.get(obj, data[ref_obj])

            for attr, ref_times in obj_key_data.items():
                full_attr = "{0}.{1}".format(obj, attr)
                if not cmds.objExists(full_attr):
                    continue

                filtered_ref_times = [t for t in ref_times if timeline_min <= t <= timeline_max]
                ref_set = set(filtered_ref_times)

                actual_times = cmds.keyframe(full_attr, q=True, timeChange=True)
                actual_set = set(actual_times) if actual_times else set()

                to_add = [t for t in sorted(ref_set - actual_set) if timeline_min <= t <= timeline_max]
                to_remove = [t for t in sorted(actual_set - ref_set) if timeline_min <= t <= timeline_max]

                for t in to_add:
                    cmds.setKeyframe(full_attr, time=t, insert=True)
                for t in to_remove:
                    cmds.cutKey(full_attr, time=(t, t), option="keys")
        
    except:
        pass

paste_key_times_channels()
