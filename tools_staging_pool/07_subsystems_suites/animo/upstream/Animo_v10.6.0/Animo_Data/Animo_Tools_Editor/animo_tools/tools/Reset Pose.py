import maya.cmds as cmds
import maya.mel as mel
import json
import os

def resetSpecialChannels():
    
    selected = cmds.ls(selection=True, long=True)  # Ensure it's selecting the right objects
    selected_channels = cmds.channelBox('mainChannelBox', q=True, sma=True)  # Get selected channels
    
    if not selected:
        pass
    else:
        for sel in selected:
            if selected_channels:  # If channels are selected in the channel box
                for attr in selected_channels:
                    try:
                        # Check if the attribute exists on the object
                        if cmds.attributeQuery(attr, node=sel, exists=True):
                            # Attempt to retrieve the default value
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
            
            else:  # If no channels are selected, reset all animatable attributes
                # Get all attributes of the object that are keyable (animatable)
                animatable_attrs = cmds.listAttr(sel, k=True)  # 'k=True' ensures it fetches keyable attributes
                if animatable_attrs:
                    for attr in animatable_attrs:
                        try:
                            # Check if the attribute exists on the object
                            if cmds.attributeQuery(attr, node=sel, exists=True):
                                # Attempt to retrieve the default value
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


# Define the path to the JSON file
documentsPath = os.path.expanduser('~')  # This gives you the path to the user's home directory
user = documentsPath.split("/Documents")[0]  # This removes the "Documents" part
json_file_path = os.path.join(user, 'Documents', 'animTools', 'channelbox_attributes.json')

def is_graph_editor_active():
    """Check if the graph editor window is active using the same method as your reference"""
    try:
        gw = "graphEditor1Window"
        if cmds.window(gw, exists=True) and cmds.window(gw, q=True, visible=True):
            return True
        return False
    except:
        return False

def get_selected_time_range():
    """Get the selected time range from the playback slider"""
    try:
        playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
        timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
        if timeRange and len(timeRange) >= 2:
            StartRange = int(timeRange[0])
            EndRange = int(timeRange[1] - 1)
            # Only return range if it's more than a single frame
            if EndRange > StartRange:
                return StartRange, EndRange
    except:
        pass
    return None, None

def get_selected_graph_editor_keys():
    """Get selected keys from the graph editor with their time values"""
    selected_curves = cmds.keyframe(q=True, selected=True, name=True)
    if not selected_curves:
        return []
    
    selected_keys_data = []
    
    for curve in selected_curves:
        try:
            # Get the attribute name from the curve
            connections = cmds.listConnections(curve + '.output', p=True)
            if connections:
                attr_full = connections[0]
                obj, attr = attr_full.split('.', 1)
                
                # Get selected key times for this curve
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
    # Show wait cursor only once at the beginning
    cmds.waitCursor(state=True)
    
    try:
        # Check if the directory exists, create it if it doesn't
        json_dir = os.path.dirname(json_file)
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        
        # Check if the JSON file exists, create it if it doesn't
        if not os.path.exists(json_file):
            # Create an empty JSON file
            with open(json_file, 'w') as file:
                json.dump({}, file, indent=4)

        # Open and load the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Get the selected objects in the scene
        selected_objects = cmds.ls(selection=True)
        
        # Check for selected keys in graph editor
        selected_keys_data = get_selected_graph_editor_keys()
        
        # Check if graph editor is active/focused
        graph_editor_active = is_graph_editor_active()
        
        # Check for selected time range
        start_range, end_range = get_selected_time_range()
        
        # Check if specific channels are selected in the channel box
        selected_channels = cmds.channelBox('mainChannelBox', q=True, sma=True)
        
        # Priority 1: If we have graph editor key selection AND graph editor is active
        if selected_keys_data and graph_editor_active:
            for key_data in selected_keys_data:
                obj = key_data['object']
                attr = key_data['attribute']
                time_val = key_data['time']
                
                # Get the long name for the attribute
                try:
                    long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                except:
                    long_name = attr
                
                # First check if we have this attribute in JSON data
                json_value = None
                if obj in data:
                    if attr in data[obj]:
                        json_value = data[obj][attr]
                    elif long_name in data[obj]:
                        json_value = data[obj][long_name]
                
                if json_value is not None:
                    # Set the keyframe to the JSON value at the specific time
                    try:
                        if cmds.attributeQuery(attr, node=obj, exists=True):
                            cmds.setKeyframe(f"{obj}.{attr}", time=time_val, value=json_value)
                    except Exception as e:
                        continue
                else:
                    # Fall back to default value
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
            return  # Exit early since we processed graph editor key selection
        
        # Priority 2: If we have a time range selected, reset keys in that range
        elif start_range is not None and end_range is not None:
            if not selected_objects:
                cmds.error("No objects selected. Please select the objects you want to reset.")
            
            for obj in selected_objects:
                if selected_channels:  # If channels are selected in the channel box
                    # Process selected channels only
                    for attr in selected_channels:
                        try:
                            long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                        except:
                            long_name = attr
                        
                        # Get keys in the time range for this attribute
                        keys_in_range = cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_range, end_range), timeChange=True)
                        if keys_in_range:
                            # Get reset value
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
                            
                            # Set all keys in range to reset value
                            for key_time in keys_in_range:
                                try:
                                    cmds.setKeyframe(f"{obj}.{attr}", time=key_time, value=reset_value)
                                except:
                                    continue
                else:
                    # No channels selected, process all keyable attributes
                    animatable_attrs = cmds.listAttr(obj, k=True)
                    if animatable_attrs:
                        for attr in animatable_attrs:
                            try:
                                # Get keys in the time range for this attribute
                                keys_in_range = cmds.keyframe(f"{obj}.{attr}", q=True, time=(start_range, end_range), timeChange=True)
                                if keys_in_range:
                                    # Get reset value
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
                                    
                                    # Set all keys in range to reset value
                                    for key_time in keys_in_range:
                                        try:
                                            cmds.setKeyframe(f"{obj}.{attr}", time=key_time, value=reset_value)
                                        except:
                                            continue
                            except:
                                continue
            return  # Exit early since we processed time range selection
        
        if not selected_objects:
            cmds.error("No objects selected. Please select the objects you want to reset.")
        
        # Iterate over the selected objects
        for obj in selected_objects:
            if selected_channels:  # If channels are selected in the channel box
                # Process selected channels only
                for attr in selected_channels:
                    # Get the long name for the attribute (in case it's a short name like 'tx' -> 'translateX')
                    try:
                        long_name = cmds.attributeQuery(attr, node=obj, longName=True)
                    except:
                        long_name = attr  # If query fails, use the original name
                    
                    # First check if we have this attribute in JSON data (try both short and long names)
                    json_value = None
                    if obj in data:
                        if attr in data[obj]:
                            json_value = data[obj][attr]
                        elif long_name in data[obj]:
                            json_value = data[obj][long_name]
                    
                    if json_value is not None:
                        # Use JSON value
                        try:
                            full_attr = f"{obj}.{attr}"
                            if cmds.attributeQuery(attr, node=obj, exists=True):
                                cmds.setAttr(full_attr, json_value)
                        except Exception as e:
                            continue
                    else:
                        # Fall back to default behavior (same logic as resetSpecialChannels)
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
            
            else:  # No channels selected
                if obj in data:
                    # Reset all attributes from JSON
                    attributes = data[obj]
                    for attr, value in attributes.items():
                        try:
                            full_attr = f"{obj}.{attr}"
                            if cmds.attributeQuery(attr, node=obj, exists=True):
                                cmds.setAttr(full_attr, value)
                        except Exception as e:
                            continue
                else:
                    # Object not in JSON, reset all keyable attributes to defaults
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
        # Always hide wait cursor at the end
        cmds.waitCursor(state=False)


# Call the function to reset attributes
reset_channelbox_attributes(json_file_path)