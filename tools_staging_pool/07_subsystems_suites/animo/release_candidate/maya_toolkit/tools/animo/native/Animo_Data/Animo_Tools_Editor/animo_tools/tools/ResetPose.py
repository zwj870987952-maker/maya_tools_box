import maya.cmds as cmds
import maya.mel as mel
import json
import os

def resetSpecialChannels():
    
    selected = cmds.ls(selection=True, long=True)
    selected_channels = cmds.channelBox('mainChannelBox', q=True, sma=True)
    
    if not selected:
        pass
    else:
        for sel in selected:
            if selected_channels:
                for attr in selected_channels:
                    try:
                        if cmds.attributeQuery(attr, node=sel, exists=True):
                            try:
                                default_value = cmds.attributeQuery(attr, ld=True, n=sel)
                                if default_value:
                                    cmds.setAttr(f"{sel}.{attr}", default_value[0])
                                else:
                                    cmds.setAttr(f"{sel}.{attr}", 0)
                            except:
                                cmds.setAttr(f"{sel}.{attr}", 0)
                    except Exception as e:
                        continue
            
            else:
                animatable_attrs = cmds.listAttr(sel, k=True)
                if animatable_attrs:
                    for attr in animatable_attrs:
                        try:
                            if cmds.attributeQuery(attr, node=sel, exists=True):
                                try:
                                    default_value = cmds.attributeQuery(attr, ld=True, n=sel)
                                    if default_value:
                                        cmds.setAttr(f"{sel}.{attr}", default_value[0])
                                    else:
                                        cmds.setAttr(f"{sel}.{attr}", 0)
                                except:
                                    cmds.setAttr(f"{sel}.{attr}", 0)
                        except Exception as e:
                            continue


documentsPath = os.path.expanduser('~')
user = documentsPath.split("/Documents")[0]
json_file_path = os.path.join(user, 'Documents', 'animTools', 'channelbox_attributes.json')

def is_graph_editor_active():
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
        return False
    except:
        return False

def get_selected_time_range():
    try:
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        if timeRange and len(timeRange) >= 2:
            StartRange = int(timeRange[0])
            EndRange = int(timeRange[1] - 1)
            if EndRange > StartRange:
                return StartRange, EndRange
    except:
        pass
    return None, None

def get_selected_graph_editor_keys():
    selected_curves = cmds.keyframe(q=True, selected=True, name=True)
    if not selected_curves:
        return []
    
    selected_keys_data = []
    
    for curve in selected_curves:
        try:
            connections = cmds.listConnections(curve + '.output', p=True)
            if connections:
                attr_full = connections[0]
                obj, attr = attr_full.split('.', 1)
                
                selected_times = cmds.keyframe(curve, q=True, selected=True, timeChange=True)
                if selected_times:
                    for time_val in selected_times:
                        selected_keys_data.append({
                            'object': obj,
                            'attribute': attr,
                            'time': time_val,
                            'curve': curve
                        })
        except:
            continue
    
    return selected_keys_data

def reset_channelbox_attributes(json_file):
    cmds.waitCursor(state=True)
    
    try:
        json_dir = os.path.dirname(json_file)
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        
        if not os.path.exists(json_file):
            with open(json_file, 'w') as file:
                json.dump({}, file, indent=4)

        with open(json_file, 'r') as file:
            data = json.load(file)

        selected_objects = cmds.ls(selection=True)
        
        selected_keys_data = get_selected_graph_editor_keys()
        
        graph_editor_active = is_graph_editor_active()
        
        start_range, end_range = get_selected_time_range()
        
        selected_channels = cmds.channelBox('mainChannelBox', q=True, sma=True)
        
        if selected_keys_data and graph_editor_active:
            for key_data in selected_keys_data:
                obj = key_data['object']
                attr = key_data['attribute']
                time_val = key_data['time']
                
                try:
                    long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                except:
                    long_name = attr
                
                json_value = None
                if obj in data:
                    if attr in data[obj]:
                        json_value = data[obj][attr]
                    elif long_name in data[obj]:
                        json_value = data[obj][long_name]
                
                if json_value is not None:
                    try:
                        if cmds.attributeQuery(attr, node=obj, exists=True):
                            cmds.setKeyframe(f"{obj}.{attr}", time=time_val, value=json_value)
                    except Exception as e:
                        continue
                else:
                    try:
                        if cmds.attributeQuery(attr, node=obj, exists=True):
                            try:
                                default_value = cmds.attributeQuery(attr, ld=True, n=obj)
                                if default_value:
                                    cmds.setKeyframe(f"{obj}.{attr}", time=time_val, value=default_value[0])
                                else:
                                    cmds.setKeyframe(f"{obj}.{attr}", time=time_val, value=0)
                            except:
                                cmds.setKeyframe(f"{obj}.{attr}", time=time_val, value=0)
                    except Exception as e:
                        continue
            return
        
        elif start_range is not None and end_range is not None:
            if not selected_objects:
                cmds.error("No objects selected. Please select the objects you want to reset.")
            
            for obj in selected_objects:
                if selected_channels:
                    for attr in selected_channels:
                        try:
                            long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                        except:
                            long_name = attr
                        
                        keys_in_range = cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_range, end_range), timeChange=True)
                        if keys_in_range:
                            json_value = None
                            if obj in data:
                                if attr in data[obj]:
                                    json_value = data[obj][attr]
                                elif long_name in data[obj]:
                                    json_value = data[obj][long_name]
                            
                            if json_value is not None:
                                reset_value = json_value
                            else:
                                try:
                                    default_value = cmds.attributeQuery(attr, ld=True, n=obj)
                                    reset_value = default_value[0] if default_value else 0
                                except:
                                    reset_value = 0
                            
                            for key_time in keys_in_range:
                                try:
                                    cmds.setKeyframe(f"{obj}.{attr}", time=key_time, value=reset_value)
                                except:
                                    continue
                else:
                    animatable_attrs = cmds.listAttr(obj, k=True)
                    if animatable_attrs:
                        for attr in animatable_attrs:
                            try:
                                keys_in_range = cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_range, end_range), timeChange=True)
                                if keys_in_range:
                                    json_value = None
                                    if obj in data:
                                        if attr in data[obj]:
                                            json_value = data[obj][attr]
                                    
                                    if json_value is not None:
                                        reset_value = json_value
                                    else:
                                        try:
                                            default_value = cmds.attributeQuery(attr, ld=True, n=obj)
                                            reset_value = default_value[0] if default_value else 0
                                        except:
                                            reset_value = 0
                                    
                                    for key_time in keys_in_range:
                                        try:
                                            cmds.setKeyframe(f"{obj}.{attr}", time=key_time, value=reset_value)
                                        except:
                                            continue
                            except:
                                continue
            return
        
        if not selected_objects:
            cmds.error("No objects selected. Please select the objects you want to reset.")
        
        for obj in selected_objects:
            if selected_channels:
                for attr in selected_channels:
                    try:
                        long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                    except:
                        long_name = attr
                    
                    json_value = None
                    if obj in data:
                        if attr in data[obj]:
                            json_value = data[obj][attr]
                        elif long_name in data[obj]:
                            json_value = data[obj][long_name]
                    
                    if json_value is not None:
                        try:
                            full_attr = f"{obj}.{attr}"
                            if cmds.attributeQuery(attr, node=obj, exists=True):
                                cmds.setAttr(full_attr, json_value)
                        except Exception as e:
                            continue
                    else:
                        try:
                            if cmds.attributeQuery(attr, node=obj, exists=True):
                                try:
                                    default_value = cmds.attributeQuery(attr, ld=True, n=obj)
                                    if default_value:
                                        cmds.setAttr(f"{obj}.{attr}", default_value[0])
                                    else:
                                        cmds.setAttr(f"{obj}.{attr}", 0)
                                except:
                                    cmds.setAttr(f"{obj}.{attr}", 0)
                        except Exception as e:
                            continue
            
            else:
                if obj in data:
                    attributes = data[obj]
                    for attr, value in attributes.items():
                        try:
                            full_attr = f"{obj}.{attr}"
                            if cmds.attributeQuery(attr, node=obj, exists=True):
                                cmds.setAttr(full_attr, value)
                        except Exception as e:
                            continue
                else:
                    animatable_attrs = cmds.listAttr(obj, k=True)
                    if animatable_attrs:
                        for attr in animatable_attrs:
                            try:
                                if cmds.attributeQuery(attr, node=obj, exists=True):
                                    try:
                                        default_value = cmds.attributeQuery(attr, ld=True, n=obj)
                                        if default_value:
                                            cmds.setAttr(f"{obj}.{attr}", default_value[0])
                                        else:
                                            cmds.setAttr(f"{obj}.{attr}", 0)
                                    except:
                                        cmds.setAttr(f"{obj}.{attr}", 0)
                            except Exception as e:
                                continue
    
    finally:
        cmds.waitCursor(state=False)


reset_channelbox_attributes(json_file_path)