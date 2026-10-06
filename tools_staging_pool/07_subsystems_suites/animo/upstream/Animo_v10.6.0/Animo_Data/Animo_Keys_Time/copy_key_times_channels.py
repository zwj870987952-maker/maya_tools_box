import maya.cmds as cmds
import maya.mel as mel
import json
import os
import tempfile

def get_temp_path():
    return tempfile.gettempdir()

def get_selected_channelbox_attrs():
    try:
        channel_box = mel.eval('$tmp=$gChannelBoxName')

        main_selected = cmds.channelBox(channel_box, q=True, selectedMainAttributes=True) or []
        shape_selected = cmds.channelBox(channel_box, q=True, selectedShapeAttributes=True) or []
        output_selected = cmds.channelBox(channel_box, q=True, selectedOutputAttributes=True) or []
        history_selected = cmds.channelBox(channel_box, q=True, selectedHistoryAttributes=True) or []

        return list(set(main_selected + shape_selected + output_selected + history_selected))
    except:
        return []

def get_all_keyable_attrs(obj):
    try:
        all_attrs = cmds.listAttr(obj, keyable=True, visible=True, unlocked=True) or []
        return all_attrs
    except:
        return []

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

def copy_key_times_channels():
    try:
        cmds.undoInfo(openChunk=True)
        
        selected = cmds.ls(sl=True)
        if not selected:
            cmds.warning("No objects selected.")
            return

        result = {}

        for obj in selected:
            attrs = get_selected_channelbox_attrs()
            if not attrs:
                attrs = get_all_keyable_attrs(obj)

            if not attrs:
                continue

            obj_data = {}
            for attr in attrs:
                full_attr = "{0}.{1}".format(obj, attr)
                if cmds.objExists(full_attr):
                    key_times = cmds.keyframe(full_attr, q=True, timeChange=True)
                    if key_times:
                        obj_data[attr] = key_times

            if obj_data:
                result[obj] = obj_data

        if not result:
            cmds.warning("No keyed attributes found on selected objects.")
            return

        desktop_path = get_temp_path()
        json_filename = "maya_key_timing.json"
        json_path = os.path.join(desktop_path, json_filename)

        with open(json_path, "w") as f:
            json.dump(result, f, indent=4)

        show_feedback_message("Copied Key Time")
        
    except:
        pass
    finally:
        cmds.undoInfo(closeChunk=True)

copy_key_times_channels()
