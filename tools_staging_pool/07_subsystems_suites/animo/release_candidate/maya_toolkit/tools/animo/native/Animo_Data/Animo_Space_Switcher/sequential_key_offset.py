from __future__ import print_function, division, absolute_import

from maya import cmds

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass


def get_infinity_settings(obj, attr):
    """Query pre and post infinity settings for an attribute."""
    try:
        pre = cmds.setInfinity(obj + "." + attr, query=True, preInfinite=True)
        post = cmds.setInfinity(obj + "." + attr, query=True, postInfinite=True)
        return pre[0] if pre else "constant", post[0] if post else "constant"
    except:
        return "constant", "constant"


def set_infinity_settings(obj, attr, pre, post):
    """Restore pre and post infinity settings for an attribute."""
    try:
        cmds.setInfinity(obj + "." + attr, preInfinite=pre, postInfinite=post)
    except:
        pass


def apply_offset(offset):
    selection = cmds.ls(selection=True)
    
    if not selection:
        cmds.warning("Select objects first.")
        return
    
    selected_keyframes = cmds.keyframe(query=True, selected=True)
    
    count = 0
    num_objs = len(selection)
    
    if selected_keyframes:
        key_selection_map = {}
        for obj in selection:
            obj_attrs = cmds.listAttr(obj, keyable=True) or []
            for attr in obj_attrs:
                try:
                    times = cmds.keyframe(obj, attribute=attr, query=True, selected=True)
                    if times:
                        if (obj, attr) not in key_selection_map:
                            key_selection_map[(obj, attr)] = []
                        key_selection_map[(obj, attr)].extend(times)
                except:
                    pass
        
        i = 0
        for key_pair in key_selection_map:
            obj, attr = key_pair
            times = key_selection_map[key_pair]
            unique_times = sorted(set(times))
            obj_offset = offset * i if num_objs > 1 else offset
            values = cmds.keyframe(obj, attribute=attr, time=(min(unique_times), max(unique_times)), query=True, valueChange=True)
            
            # Store infinity settings before cutting
            pre_inf, post_inf = get_infinity_settings(obj, attr)
            
            cmds.cutKey(obj, attribute=attr, time=(min(unique_times), max(unique_times)))
            new_times = [t + obj_offset for t in unique_times]
            for idx in range(len(new_times)):
                cmds.setKeyframe(obj, attribute=attr, time=new_times[idx], value=values[idx])
            
            # Restore infinity settings
            set_infinity_settings(obj, attr, pre_inf, post_inf)
            
            for t in new_times:
                cmds.selectKey(obj, attribute=attr, time=(t, t), add=True)
            
            count += 1
            i += 1
    
    else:
        channel_box = "mainChannelBox"
        selected_attrs = cmds.channelBox(channel_box, query=True, sma=True)
        if not selected_attrs:
            selected_attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        
        for i in range(len(selection)):
            obj = selection[i]
            obj_offset = offset * i if num_objs > 1 else offset
            for attr in selected_attrs:
                if not cmds.objExists(obj + "." + attr):
                    continue
                if cmds.keyframe(obj, attribute=attr, query=True, keyframeCount=True):
                    times = cmds.keyframe(obj, attribute=attr, query=True)
                    values = cmds.keyframe(obj, attribute=attr, query=True, valueChange=True)
                    
                    # Store infinity settings before cutting
                    pre_inf, post_inf = get_infinity_settings(obj, attr)
                    
                    cmds.cutKey(obj, attribute=attr, time=(min(times), max(times)))
                    for idx in range(len(times)):
                        cmds.setKeyframe(obj, attribute=attr, time=times[idx] + obj_offset, value=values[idx])
                    
                    # Restore infinity settings
                    set_infinity_settings(obj, attr, pre_inf, post_inf)
                    
                    count += 1
    
    return count
