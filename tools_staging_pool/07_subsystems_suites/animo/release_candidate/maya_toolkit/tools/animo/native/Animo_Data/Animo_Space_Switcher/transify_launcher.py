## Created by Ehsan Bayat, 2025
# Transfer animation from Maya to another Maya

# Transify v1.9

import json
import os
import glob
from maya import cmds
from maya import mel
import maya.OpenMayaUI as omui
import sys

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

try:
    max = builtins.max 
    min = builtins.min 
except:
    pass

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance


class AnimationCopyPasteJson:
    
    def __init__(self):
        self.documents_path = self.get_documents_path()




    def get_documents_path(self):
        if sys.platform.startswith("win"):
            try:
                from ctypes import windll, wintypes, create_unicode_buffer
                CSIDL_PERSONAL = 5
                SHGFP_TYPE_CURRENT = 0
                buf = create_unicode_buffer(wintypes.MAX_PATH)
                windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
                docs_dir = buf.value
            except Exception:
                docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents")

        anim_tools_folder = os.path.join(docs_dir, "animTools", "animationData")
        if not os.path.exists(anim_tools_folder):
            os.makedirs(anim_tools_folder)
        return anim_tools_folder

    def check_objects_in_animation_layers(self, objects_to_check):
        animLayers = cmds.ls(type='animLayer')
        root_layer = cmds.animLayer(q=True, root=True)
        if root_layer and root_layer in animLayers:
            animLayers.remove(root_layer)
        
        if not animLayers:
            return False
        
        objects_in_layers = []
        all_affected_layers = set()
        
        for animLyr in animLayers:
            attrs = cmds.animLayer(animLyr, q=True, attribute=True)
            if attrs:
                for attr in attrs:
                    obj_from_attr = attr.split('.')[0]
                    
                    for checked_obj in objects_to_check:
                        checked_short = checked_obj.split('|')[-1]
                        attr_short = obj_from_attr.split('|')[-1]
                        
                        if checked_short == attr_short:
                            if checked_obj not in objects_in_layers:
                                objects_in_layers.append(checked_obj)
                            all_affected_layers.add(animLyr)
                            break
        
        if not objects_in_layers:
            return False
        
        cmds.waitCursor(state=False)
        
        result = cmds.confirmDialog(
            title='Animation Layer Detected',
            message='The selected controls are part of an animation layer, you need to merge the layers first.',
            button=['Cancel', 'Merge'],
            defaultButton='Merge',
            cancelButton='Cancel',
            dismissString='Cancel',
            backgroundColor=[0.15, 0.15, 0.15]
        )
        
        if result == 'Merge':
            self.bake_all_objects_from_layers(objects_in_layers, list(all_affected_layers))
            return False
        else:
            return True
    
    def bake_all_objects_from_layers(self, objects_to_bake, affected_layers):
        cmds.undoInfo(openChunk=True)
        
        try:
            allAnimLayers = cmds.ls(type="animLayer")
            root_layer = cmds.animLayer(q=True, root=True)
            if root_layer and root_layer in allAnimLayers:
                allAnimLayers.remove(root_layer)
            
            original_mute_states = {}
            for layer in allAnimLayers:
                original_mute_states[layer] = cmds.animLayer(layer, q=True, mute=True)
            
            for layer in allAnimLayers:
                if layer not in affected_layers:
                    cmds.animLayer(layer, edit=True, mute=True)
            
            for layer in affected_layers:
                cmds.animLayer(layer, edit=True, mute=False)
            
            cmds.refresh(suspend=True)
            cmds.evaluationManager(mode="off")
            
            try:
                min_time = cmds.playbackOptions(q=True, animationStartTime=True)
                max_time = cmds.playbackOptions(q=True, animationEndTime=True)

                cmds.bakeResults(objects_to_bake, sm=True, pok=True, t=(min_time, max_time))
                
                for layer in affected_layers:
                    if cmds.objExists(layer):
                        layer_attrs = cmds.animLayer(layer, q=True, attribute=True)
                        if layer_attrs:
                            for attr in layer_attrs:
                                obj_from_attr = attr.split('.')[0]
                                obj_short = obj_from_attr.split('|')[-1]
                                
                                for obj in objects_to_bake:
                                    obj_check_short = obj.split('|')[-1]
                                    if obj_short == obj_check_short:
                                        try:
                                            cmds.animLayer(layer, edit=True, removeAttribute=attr)
                                        except:
                                            pass
                                        break
               
                for layer in allAnimLayers:
                    if layer not in affected_layers and cmds.objExists(layer):
                        cmds.animLayer(layer, edit=True, mute=original_mute_states[layer])
                
                layers_to_delete = []
                for layer in allAnimLayers:
                    if cmds.objExists(layer):
                        attrs = cmds.animLayer(layer, q=True, attribute=True)
                        if not attrs:
                            layers_to_delete.append(layer)
                
                if layers_to_delete:
                    cmds.delete(layers_to_delete)
                
            except Exception:
                pass
            finally:
                cmds.refresh(suspend=False)
                cmds.evaluationManager(mode="parallel")
        
        finally:
            cmds.undoInfo(closeChunk=True)



    
    
    def get_anim_curves(self, force_graph_editor=False):
        anim_curves = cmds.keyframe(query=True, name=True, selected=True)
        visible_panels = cmds.getPanel(visiblePanels=True)
        graph_editor = "graphEditor1" in visible_panels
        get_from = "graphEditor"
        
        if not anim_curves or not graph_editor and not force_graph_editor:
            get_from = "timeline"
            try:
                playback_slider = mel.eval('$temp=$gPlayBackSlider')
                anim_curves = cmds.timeControl(playback_slider, query=True, animCurveNames=True)
            except:
                sel = cmds.ls(selection=True)
                if sel:
                    anim_curves = cmds.keyframe(sel, query=True, name=True)
                else:
                    anim_curves = []
        
        return [anim_curves, get_from]
    
    def get_timeline_range(self, float_val=True):
        try:
            playback_slider = mel.eval('$temp=$gPlayBackSlider')
            range_val = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            if float_val:
                range_val[1] -= 0.0001
            return range_val
        except:
            start = cmds.playbackOptions(query=True, minTime=True)
            end = cmds.playbackOptions(query=True, maxTime=True)
            if float_val:
                end -= 0.0001
            return [start, end]
    
    def get_objects_and_attributes(self, anim_curves):
        if not anim_curves:
            return [[], []]
        
        objects = []
        attributes = []
        
        for node in anim_curves:
            if not cmds.objExists(node):
                objects.append(None)
                attributes.append(None)
                continue
            
            try:
                connections = cmds.listConnections("{}.output".format(node.split('.')[0]), 
                                                 source=False, destination=True, 
                                                 plugs=True, skipConversionNodes=True)
                if connections:
                    target = connections[0]
                    obj = target.split(".")[0]
                    attr = target.split(".")[-1]
                    objects.append(obj)
                    attributes.append(attr)
                else:
                    objects.append(None)
                    attributes.append(None)
            except:
                objects.append(None)
                attributes.append(None)
        
        return [objects, attributes]
    
    def get_keys_in_range(self, anim_curves, get_from, range_all=None):
        if not anim_curves:
            return []
        
        keys_sel = []
        
        if get_from == "graphEditor":
            for node in anim_curves:
                selected_keys = cmds.keyframe(node, selected=True, query=True, timeChange=True)
                keys_sel.append(selected_keys if selected_keys else [])
        else:
            if range_all is None:
                timeline_range = self.get_timeline_range()
            else:
                timeline_range = None
            
            for node in anim_curves:
                if not cmds.objExists(node):
                    keys_sel.append([])
                    continue
                
                all_keys = cmds.keyframe(node, query=True, timeChange=True)
                if not all_keys:
                    keys_sel.append([])
                    continue
                
                if range_all or not timeline_range:
                    keys_sel.append(all_keys)
                else:
                    range_keys = [key for key in all_keys 
                                if timeline_range[0] <= key < timeline_range[1]]
                    keys_sel.append(range_keys)
        
        return keys_sel
    
    def get_all_animatable_attributes(self, objects):
        all_obj_attrs = []
        
        common_attrs = [
            'translateX', 'translateY', 'translateZ',
            'rotateX', 'rotateY', 'rotateZ',
            'scaleX', 'scaleY', 'scaleZ',
            'visibility'
        ]
        
        for obj in objects:
            if not cmds.objExists(obj):
                continue
                
            obj_attrs = []
            
            for attr in common_attrs:
                full_attr = "{}.{}".format(obj, attr)
                if cmds.objExists(full_attr) and cmds.getAttr(full_attr, keyable=True):
                    obj_attrs.append(full_attr)
            
            try:
                keyable_attrs = cmds.listAttr(obj, keyable=True) or []
                for attr in keyable_attrs:
                    if attr not in common_attrs:
                        full_attr = "{}.{}".format(obj, attr)
                        if cmds.objExists(full_attr):
                            obj_attrs.append(full_attr)
            except:
                pass
            
            all_obj_attrs.extend(obj_attrs)
        
        return all_obj_attrs
    
    def copy_animation(self, range_mode="selected"):
        cmds.waitCursor(state=True)
        
        try:
            if range_mode == "all":
                selected_objects = cmds.ls(selection=True)
                if not selected_objects:
                    cmds.warning("No objects selected. Please select controls to copy all their animation.")
                    return None
                
                all_obj_attrs = self.get_all_animatable_attributes(selected_objects)
                
                if not all_obj_attrs:
                    cmds.warning("No animatable attributes found on selected objects.")
                    return None
                
                anim_data = self.get_anim_data_from_attributes(all_obj_attrs, range_all=True)
            else:
                anim_data = self.get_anim_data()
            
            return anim_data
            
        finally:
            cmds.waitCursor(state=False)
    
    def get_anim_data_from_attributes(self, obj_attrs, range_all=False):
        if not obj_attrs:
            cmds.warning("No object attributes found.")
            return None
        
        current_time = cmds.currentTime(query=True)
        
        anim_data = {
            "objects": [],
            "animData": []
        }
        
        objects_added = set()
        
        
        for obj_attr in obj_attrs:
            if not cmds.objExists(obj_attr):
                continue
            
            obj_name = obj_attr.split('.')[0]
            attr_name = obj_attr.split('.')[-1]
            
            if obj_name not in objects_added:
                anim_data["objects"].append(obj_name)
                objects_added.add(obj_name)
            
            anim_curves = cmds.keyframe(obj_attr, query=True, name=True)
            
            if anim_curves and len(anim_curves) > 0:
                curve = anim_curves[0]
                
                try:
                    weighted = cmds.keyTangent(curve, query=True, weightedTangents=True)
                    if weighted:
                        weighted = weighted[0]
                    else:
                        weighted = False
                        
                    infinity = cmds.setInfinity(obj_attr, query=True, 
                                              preInfinite=True, postInfinite=True)
                except:
                    weighted = False
                    infinity = ["constant", "constant"]
                
                curve_data = {
                    "objAttr": obj_attr,
                    "curveData": [weighted, infinity],
                    "keyframeData": [],
                    "tangentData": []
                }
                
                try:
                    if range_all:
                        time_change = cmds.keyframe(curve, query=True, timeChange=True)
                        value_change = cmds.keyframe(curve, query=True, valueChange=True)
                        breakdowns = cmds.keyframe(curve, query=True, breakdown=True)
                        
                        in_tangent_type = cmds.keyTangent(curve, query=True, inTangentType=True)
                        out_tangent_type = cmds.keyTangent(curve, query=True, outTangentType=True)
                        ix = cmds.keyTangent(curve, query=True, ix=True)
                        iy = cmds.keyTangent(curve, query=True, iy=True)
                        ox = cmds.keyTangent(curve, query=True, ox=True)
                        oy = cmds.keyTangent(curve, query=True, oy=True)
                        lock = cmds.keyTangent(curve, query=True, lock=True)
                        weight_lock = cmds.keyTangent(curve, query=True, weightLock=True)
                        
                        for j, key_time in enumerate(time_change):
                            breakdown = (key_time in breakdowns) if breakdowns else False
                            
                            keyframe = [time_change[j], value_change[j], breakdown]
                            tangent = [
                                in_tangent_type[j], out_tangent_type[j],
                                ix[j], iy[j], ox[j], oy[j],
                                lock[j], weight_lock[j]
                            ]
                            
                            curve_data["keyframeData"].append(keyframe)
                            curve_data["tangentData"].append(tangent)
                    
                except Exception as e:
                    continue
                
                anim_data["animData"].append(curve_data)
                
            else:
                try:
                    current_value = cmds.getAttr(obj_attr)
                    
                    curve_data = {
                        "objAttr": obj_attr,
                        "curveData": [False, ["constant", "constant"]],
                        "keyframeData": [[current_time, current_value, False]],
                        "tangentData": [["auto", "auto", 0, 0, 0, 0, False, False]]
                    }
                    
                    anim_data["animData"].append(curve_data)
                    
                except Exception as e:
                    continue
        
        return anim_data
    
    def get_anim_data(self, anim_curves=None, range_all=False):
        if anim_curves is None:
            get_curves = self.get_anim_curves(True)
            anim_curves = get_curves[0]
            get_from = get_curves[1]
        else:
            get_from = None
        
        if not anim_curves:
            cmds.warning("No animation curves found.")
            return None
        
        if get_from is None:
            keys_sel = self.get_keys_in_range(anim_curves, "timeline", range_all=True)
        else:
            keys_sel = self.get_keys_in_range(anim_curves, get_from)
        
        if not keys_sel or all(not keys for keys in keys_sel):
            cmds.warning("No keys found to copy.")
            return None
        
        objs_attrs = self.get_objects_and_attributes(anim_curves)
        objects = objs_attrs[0]
        attributes = objs_attrs[1]
        
        anim_data = {
            "objects": objects,
            "animData": []
        }
        
        
        for i, curve in enumerate(anim_curves):
            if objects[i] is None or not keys_sel[i]:
                continue
            
            obj_attr = "{}.{}".format(objects[i], attributes[i])
            
            try:
                weighted = cmds.keyTangent(curve, query=True, weightedTangents=True)
                if weighted:
                    weighted = weighted[0]
                else:
                    weighted = False
                    
                infinity = cmds.setInfinity(obj_attr, query=True, 
                                          preInfinite=True, postInfinite=True)
            except:
                weighted = False
                infinity = ["constant", "constant"]
            
            curve_data = {
                "objAttr": obj_attr,
                "curveData": [weighted, infinity],
                "keyframeData": [],
                "tangentData": []
            }
            
            time_range = (keys_sel[i][0], keys_sel[i][-1])
            
            try:
                time_change = cmds.keyframe(curve, query=True, time=time_range, timeChange=True)
                value_change = cmds.keyframe(curve, query=True, time=time_range, valueChange=True)
                breakdowns = cmds.keyframe(curve, query=True, time=time_range, breakdown=True)
                
                in_tangent_type = cmds.keyTangent(curve, query=True, time=time_range, inTangentType=True)
                out_tangent_type = cmds.keyTangent(curve, query=True, time=time_range, outTangentType=True)
                ix = cmds.keyTangent(curve, query=True, time=time_range, ix=True)
                iy = cmds.keyTangent(curve, query=True, time=time_range, iy=True)
                ox = cmds.keyTangent(curve, query=True, time=time_range, ox=True)
                oy = cmds.keyTangent(curve, query=True, time=time_range, oy=True)
                lock = cmds.keyTangent(curve, query=True, time=time_range, lock=True)
                weight_lock = cmds.keyTangent(curve, query=True, time=time_range, weightLock=True)
                
                for j, key_time in enumerate(keys_sel[i]):
                    if key_time in time_change:
                        idx = time_change.index(key_time)
                        breakdown = (key_time in breakdowns) if breakdowns else False
                        
                        keyframe = [time_change[idx], value_change[idx], breakdown]
                        tangent = [
                            in_tangent_type[idx], out_tangent_type[idx],
                            ix[idx], iy[idx], ox[idx], oy[idx],
                            lock[idx], weight_lock[idx]
                        ]
                        
                        curve_data["keyframeData"].append(keyframe)
                        curve_data["tangentData"].append(tangent)
                
            except Exception as e:
                continue
            
            anim_data["animData"].append(curve_data)
        
        return anim_data
    
    def save_to_json(self, anim_data, filename=None):
        if not anim_data:
            cmds.warning("No animation data to save.")
            return None
        
        if not filename:
            import time
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                base_name = ".".join(scene_name.split(".")[:-1])
            else:
                base_name = "untitled_scene"
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = "{}_animation_{}.json".format(base_name, timestamp)
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.documents_path, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(anim_data, f, indent=2)
            
            return filepath
            
        except Exception as e:
            error_msg = "Failed to save animation data: {}".format(e)
            cmds.confirmDialog(title="Error", 
                             message=error_msg,
                             button=["OK"])
            return None
    
    def copy_all_animation_to_json(self):
        cmds.waitCursor(state=True)
        
        try:
            selected_objects = cmds.ls(selection=True)
            if not selected_objects:
                cmds.warning("No objects selected. Please select controls to copy all their animation.")
                return None
            
            cmds.waitCursor(state=False)
            if self.check_objects_in_animation_layers(selected_objects):
                return None
            cmds.waitCursor(state=True)
            
            temp_keyed_objects = []
            
            all_anim_curves = []
            for obj in selected_objects:
                curves = cmds.keyframe(obj, query=True, name=True)
                if curves:
                    all_anim_curves.extend(curves)
                else:
                    try:
                        cmds.undoInfo(openChunk=True)
                        cmds.setKeyframe(obj)
                        temp_keyed_objects.append(obj)
                        curves = cmds.keyframe(obj, query=True, name=True)
                        if curves:
                            all_anim_curves.extend(curves)
                        cmds.undoInfo(closeChunk=True)
                    except Exception:
                        cmds.undoInfo(closeChunk=True)
                        pass
            
            if not all_anim_curves:
                cmds.warning("No animation curves found on selected objects.")
                for obj in temp_keyed_objects:
                    try:
                        cmds.undo()
                    except Exception:
                        pass
                return None
            
            anim_data = self.get_anim_data(anim_curves=all_anim_curves, range_all=True)
            
            for obj in temp_keyed_objects:
                try:
                    cmds.undo()
                except Exception:
                    pass
            
            if anim_data:
                return self.save_to_json(anim_data)
            return None
            
        finally:
            cmds.waitCursor(state=False)
    
    def copy_selected_animation_to_json(self):
        anim_data = self.copy_animation(range_mode="selected")
        if anim_data:
            return self.save_to_json(anim_data)
        return None
    
    
    def get_latest_json_file(self):
        pattern = os.path.join(self.documents_path, "*_animation_*.json")
        json_files = glob.glob(pattern)
        
        if not json_files:
            return None
        
        json_files.sort(key=os.path.getmtime, reverse=True)
        return json_files[0]
    
    def get_all_json_files(self):
        pattern = os.path.join(self.documents_path, "*_animation_*.json")
        json_files = glob.glob(pattern)
        
        if not json_files:
            return []
        
        json_files.sort(key=os.path.getmtime, reverse=True)
        return json_files
    
    def load_animation_data(self, filepath):
        try:
            with open(filepath, 'r') as f:
                anim_data = json.load(f)
            
            return anim_data
            
        except Exception as e:
            error_msg = "Failed to load animation data: {}".format(e)
            cmds.confirmDialog(title="Error", 
                             message=error_msg,
                             button=["OK"])
            return None
    
    def create_dummy_key(self, objects):
        if not objects:
            return
        
        valid_objects = [obj for obj in objects if obj and cmds.objExists(obj)]
        if valid_objects:
            cmds.setKeyframe(valid_objects, time=(-50000, -50000), insert=False)
    
    def delete_dummy_key(self, objects):
        if not objects:
            return
        
        valid_objects = [obj for obj in objects if obj and cmds.objExists(obj)]
        if valid_objects:
            cmds.cutKey(valid_objects, time=(-50000, -50000), clear=True)
    
    def get_all_namespaces(self):
        remove_list = ["UI", "shared"]
        try:
            namespaces = list(set(cmds.namespaceInfo(listOnlyNamespaces=True)) - set(remove_list))
            namespaces.insert(0, "")
            if namespaces:
                namespaces.sort()
            return namespaces
        except:
            return [""]
    
    def remap_namespace_in_data(self, anim_data, source_namespace, target_namespace):
        if not anim_data or 'animData' not in anim_data:
            return anim_data
        
        import copy
        remapped_data = copy.deepcopy(anim_data)
        
        if source_namespace is None:
            source_namespace = self.detect_source_namespace(anim_data)
        
        source_ns = source_namespace + ":" if source_namespace else ""
        target_ns = target_namespace + ":" if target_namespace else ""
        
        if source_ns == target_ns:
            return remapped_data
        
        
        remapped_count = 0
        for anim_item in remapped_data['animData']:
            if 'objAttr' in anim_item and anim_item['objAttr']:
                obj_attr = anim_item['objAttr']
                original_obj_attr = obj_attr
                
                if obj_attr.startswith(source_ns):
                    new_obj_attr = obj_attr.replace(source_ns, target_ns, 1)
                    anim_item['objAttr'] = new_obj_attr
                    remapped_count += 1
                elif not source_ns and target_ns:
                    anim_item['objAttr'] = target_ns + obj_attr
                    remapped_count += 1
        
        return remapped_data
    
    def detect_multiple_namespaces_from_selection(self, selected_objects):
        if not selected_objects:
            return []
        
        namespaces = set()
        
        for obj in selected_objects:
            obj_short = obj.split('|')[-1]
            if ":" in obj_short:
                namespace = obj_short.split(":")[0]
                namespaces.add(namespace)
            else:
                namespaces.add("")
        
        return list(namespaces)
    
    def select_objects_from_json(self):
        latest_file = self.get_latest_json_file()
        if not latest_file:
            cmds.warning("No animation JSON files found.")
            return
        
        self.select_objects_from_json_file(latest_file)
    
    def select_objects_from_json_file(self, filepath):
        if not filepath:
            cmds.warning("No file specified.")
            return
        
        anim_data = self.load_animation_data(filepath)
        if not anim_data or 'animData' not in anim_data:
            cmds.warning("Invalid animation data.")
            return
        
        json_objects = []
        for anim_item in anim_data['animData']:
            if 'objAttr' in anim_item and anim_item['objAttr']:
                obj_name = anim_item['objAttr'].split('.')[0]
                if obj_name not in json_objects:
                    json_objects.append(obj_name)
        
        if not json_objects:
            cmds.warning("No objects found in JSON file.")
            return
        
        selected_objects = cmds.ls(selection=True)
        has_selection = bool(selected_objects)
        
        objects_to_select = []
        
        if not has_selection:
            objects_to_select = json_objects
            
        else:
            target_namespaces = self.detect_multiple_namespaces_from_selection(selected_objects)
            
            if target_namespaces:
                source_ns = self.detect_source_namespace(anim_data)
                
                for target_ns_item in target_namespaces:
                    if target_ns_item != source_ns:
                        remapped_data = self.remap_namespace_in_data(anim_data, source_ns, target_ns_item)
                        
                        for anim_item in remapped_data['animData']:
                            if 'objAttr' in anim_item and anim_item['objAttr']:
                                obj_name = anim_item['objAttr'].split('.')[0]
                                if obj_name not in objects_to_select:
                                    objects_to_select.append(obj_name)
                    else:
                        for obj_name in json_objects:
                            if obj_name not in objects_to_select:
                                objects_to_select.append(obj_name)
            else:
                objects_to_select = json_objects
        
        
        existing_objects = []
        for obj in objects_to_select:
            if cmds.objExists(obj):
                existing_objects.append(obj)
            else:
                obj_short = obj.split('|')[-1]
                matching = cmds.ls(obj_short, long=True)
                if matching:
                    existing_objects.extend(matching)
        
        if existing_objects:
            cmds.select(existing_objects, replace=True)
        else:
            cmds.warning("No matching objects found in scene.")

    
    def apply_animation_to_multiple_namespaces(self, paste_in_place, only_selected, source_namespaces, target_namespaces, filepath=None):
        cmds.undoInfo(openChunk=True)
        
        try:
            success_count = 0
            
            if filepath:
                anim_data = self.load_animation_data(filepath)
            else:
                latest_file = self.get_latest_json_file()
                if latest_file:
                    anim_data = self.load_animation_data(latest_file)
                else:
                    anim_data = None
            
            if not anim_data:
                return False
            
            for target_ns in target_namespaces:
                
                result = self.apply_animation_data(
                    anim_data,
                    paste_in_place=paste_in_place,
                    only_selected_nodes=only_selected,
                    target_namespace=target_ns,
                    skip_undo_chunk=True
                )
                
                if result:
                    success_count += 1
            
            return success_count > 0
            
        finally:
            cmds.undoInfo(closeChunk=True)
    
    def detect_most_common_namespace_from_selection(self, selected_objects):
        if not selected_objects:
            return ""
        
        namespace_counts = {}
        
        for obj in selected_objects:
            if ":" in obj:
                namespace = obj.split(":")[0]
                namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
            else:
                namespace_counts[""] = namespace_counts.get("", 0) + 1
        
        if namespace_counts:
            most_common = max(namespace_counts, key=namespace_counts.get)
            return most_common
        
        return ""
    
    def detect_source_namespace(self, anim_data):

        try:
            max = builtins.max 
            min = builtins.min 
        except:
            pass
        if not anim_data or 'animData' not in anim_data:
            return ""
        
        namespace_counts = {}
        
        for anim_item in anim_data['animData']:
            if 'objAttr' in anim_item and anim_item['objAttr']:
                obj_attr = anim_item['objAttr']
                if ":" in obj_attr:
                    namespace = obj_attr.split(":")[0]
                    namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
                else:
                    namespace_counts[""] = namespace_counts.get("", 0) + 1
        
        if namespace_counts:
            most_common = max(namespace_counts, key=namespace_counts.get)
            return most_common
        
        return ""
    
    def apply_animation_data(self, anim_data, paste_in_place=True, only_selected_nodes=False, target_namespace=None, skip_undo_chunk=False):
        if not anim_data or 'animData' not in anim_data:
            cmds.warning("Invalid animation data.")
            return False
        
        if not skip_undo_chunk:
            cmds.undoInfo(openChunk=True)
        
        try:
            if target_namespace is not None:
                source_namespace = self.detect_source_namespace(anim_data)
                anim_data = self.remap_namespace_in_data(anim_data, source_namespace, target_namespace)
            
            if only_selected_nodes:
                selected_objects = cmds.ls(selection=True)
                if not selected_objects:
                    cmds.warning("No objects selected for paste operation.")
                    return False
                
                filtered_anim_data = []
                for anim_item in anim_data['animData']:
                    obj_attr = anim_item['objAttr']
                    if obj_attr:
                        obj_name = obj_attr.split('.')[0]
                        if self.is_object_or_transform_selected(obj_name, selected_objects) and self.attribute_exists_and_keyable(obj_attr):
                            filtered_anim_data.append(anim_item)
                
                if not filtered_anim_data:
                    cmds.warning("None of the selected objects have matching animation data in the JSON file.")
                    return False
                
                anim_data['animData'] = filtered_anim_data
                objects = selected_objects
                
            else:
                objects = []
                for item in anim_data['animData']:
                    if item['objAttr']:
                        obj_name = item['objAttr'].split('.')[0]
                        if cmds.objExists(obj_name) and obj_name not in objects:
                            objects.append(obj_name)
                
                if objects:
                    cmds.select(objects)
            
            if not objects:
                cmds.warning("No valid objects to apply animation to.")
                return False
            
            cmds.refresh(suspend=True)
            
            first_key = None
            if paste_in_place:
                curr_key = cmds.currentTime(query=True)
                all_keys = []
                
                for anim_item in anim_data['animData']:
                    for keyframe in anim_item['keyframeData']:
                        all_keys.append(keyframe[0])
                
                if all_keys:
                    first_key = min(all_keys)
                    time_offset = curr_key - first_key
                else:
                    time_offset = 0
            else:
                time_offset = 0
            
            existing_obj_attrs = []
            for anim_item in anim_data['animData']:
                obj_attr = anim_item['objAttr']
                if self.attribute_exists_and_keyable(obj_attr):
                    existing_obj_attrs.append(obj_attr)
            
            if not existing_obj_attrs:
                cmds.warning("No matching object attributes found in scene.")
                cmds.refresh(suspend=False)
                return False
            
            
            self.create_dummy_key(existing_obj_attrs)
            
            if paste_in_place and first_key is not None:
                cut_in = curr_key
                cut_out = curr_key + (max(all_keys) - first_key)
                cmds.cutKey(existing_obj_attrs, time=(cut_in, cut_out), clear=True)
            else:
                cmds.cutKey(existing_obj_attrs, time=(-49999, 50000), clear=True)
            
            
            applied_count = 0
            for anim_item in anim_data['animData']:
                obj_attr = anim_item['objAttr']
                
                if not self.attribute_exists_and_keyable(obj_attr):
                    continue
                
                curve_data = anim_item['curveData']
                weighted = curve_data[0] if len(curve_data) > 0 else False
                infinity = curve_data[1] if len(curve_data) > 1 else ["constant", "constant"]
                
                keyframe_data = anim_item['keyframeData']
                tangent_data = anim_item['tangentData']
                
                for i, keyframe in enumerate(keyframe_data):
                    if i >= len(tangent_data):
                        continue
                    
                    time_change = keyframe[0] + time_offset
                    value_change = keyframe[1]
                    breakdown = keyframe[2] if len(keyframe) > 2 else False
                    
                    tangent = tangent_data[i]
                    if len(tangent) >= 8:
                        in_tangent_type = tangent[0]
                        out_tangent_type = tangent[1]
                        ix = tangent[2]
                        iy = tangent[3]
                        ox = tangent[4]
                        oy = tangent[5]
                        lock = tangent[6]
                        weight_lock = tangent[7]
                    else:
                        in_tangent_type = "auto"
                        out_tangent_type = "auto"
                        ix = iy = ox = oy = 0
                        lock = weight_lock = False
                    
                    time_tuple = (time_change, time_change)
                    
                    try:
                        cmds.setKeyframe(obj_attr, time=time_tuple, value=value_change)
                        
                        if i == 0:
                            if weighted is not None:
                                cmds.keyTangent(obj_attr, weightedTangents=weighted)
                            if infinity:
                                cmds.setInfinity(obj_attr, edit=True, 
                                               preInfinite=infinity[0], 
                                               postInfinite=infinity[1])
                        
                        if breakdown:
                            cmds.keyframe(obj_attr, edit=True, time=time_tuple, breakdown=True)
                        
                        cmds.keyTangent(obj_attr, time=time_tuple, 
                                       ix=ix, iy=iy, ox=ox, oy=oy, lock=lock)
                        
                        if weighted and weight_lock is not None:
                            cmds.keyTangent(obj_attr, time=time_tuple, weightLock=weight_lock)
                        
                        cmds.keyTangent(obj_attr, time=time_tuple, 
                                       inTangentType=in_tangent_type, 
                                       outTangentType=out_tangent_type)
                    
                    except Exception as e:
                        continue
                
                applied_count += 1
            
            self.delete_dummy_key(existing_obj_attrs)
            cmds.refresh(suspend=False)
            
            return True
            
        except Exception as e:
            return False
            
        finally:
            if not skip_undo_chunk:
                cmds.undoInfo(closeChunk=True)

    def attribute_exists_and_keyable(self, obj_attr):
        if not obj_attr or '.' not in obj_attr:
            return False
        
        if cmds.objExists(obj_attr):
            try:
                return cmds.getAttr(obj_attr, keyable=True) is not False
            except:
                try:
                    cmds.getAttr(obj_attr)
                    return True
                except:
                    return False
        
        obj_name = obj_attr.split('.')[0]
        attr_name = obj_attr.split('.')[-1]
        
        if not cmds.objExists(obj_name):
            return False
        
        try:
            cmds.getAttr(obj_attr)
            return True
        except:
            pass
        
        try:
            all_attrs = cmds.listAttr(obj_name) or []
            if attr_name in all_attrs:
                return True
        except:
            pass
        
        return False

    def is_object_or_transform_selected(self, obj_name, selected_objects):
        if obj_name in selected_objects:
            return True
        
        try:
            if cmds.objectType(obj_name) != 'transform':
                parents = cmds.listRelatives(obj_name, parent=True, type='transform')
                if parents and parents[0] in selected_objects:
                    return True
        except:
            pass
        
        for sel_obj in selected_objects:
            try:
                if cmds.objExists(sel_obj):
                    relatives = cmds.listRelatives(sel_obj, allDescendents=True) or []
                    if obj_name in relatives:
                        return True
                    relatives = cmds.listRelatives(obj_name, allDescendents=True) or []
                    if sel_obj in relatives:
                        return True
            except:
                continue
        
        return False
    
    def paste_latest_animation(self, paste_in_place=True, only_selected=False, target_namespace=None, skip_undo_chunk=False):
        latest_file = self.get_latest_json_file()
        
        if not latest_file:
            cmds.warning("No animation JSON files found in Documents folder.")
            return False
        
        anim_data = self.load_animation_data(latest_file)
        if anim_data:
            return self.apply_animation_data(anim_data, paste_in_place, only_selected, target_namespace, skip_undo_chunk)
        
        return False
    
    def paste_from_file(self, filepath, paste_in_place=True, only_selected=False, target_namespace=None, skip_undo_chunk=False):
        anim_data = self.load_animation_data(filepath)
        if anim_data:
            return self.apply_animation_data(anim_data, paste_in_place, only_selected, target_namespace, skip_undo_chunk)
        
        return False

    def copy_pose_to_json(self):
        cmds.waitCursor(state=True)
        
        try:
            selected_objects = cmds.ls(selection=True, long=True)
            if not selected_objects:
                cmds.warning("No objects selected. Please select controls to copy their pose.")
                return None
            
            current_time = cmds.currentTime(query=True)
            pose_data = {}
            anim_data_list = []
            
            for obj in selected_objects:
                short_name = obj.split('|')[-1]
                pose_data[short_name] = {}
                
                attrs = cmds.listAttr(obj, keyable=True, unlocked=True)
                if not attrs:
                    continue
                
                for attr in attrs:
                    full_attr = obj + '.' + attr
                    try:
                        value = cmds.getAttr(full_attr)
                        pose_data[short_name][attr] = value
                        
                        anim_data_list.append({
                            "objAttr": short_name + '.' + attr,
                            "curveData": [False, ["constant", "constant"]],
                            "keyframeData": [[current_time, value, False]],
                            "tangentData": [["auto", "auto", 0, 0, 0, 0, False, False]]
                        })
                    except:
                        continue
            
            if not pose_data or all(not attrs for attrs in pose_data.values()):
                cmds.warning("No keyable attributes found on selected objects.")
                return None
            
            import time
            scene_name = cmds.file(query=True, sceneName=True, shortName=True)
            if scene_name:
                base_name = ".".join(scene_name.split(".")[:-1])
            else:
                base_name = "untitled_scene"
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = "{}_animation_{}.json".format(base_name, timestamp)
            filepath = os.path.join(self.documents_path, filename)
            
            save_data = {
                "pose": pose_data,
                "animData": anim_data_list
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_data, f, indent=4)
            
            return filepath
            
        finally:
            cmds.waitCursor(state=False)
    
    def paste_pose_from_json(self, filepath=None, target_namespace=None, selected_objects=None):
        cmds.waitCursor(state=True)
        
        try:
            if not filepath:
                json_files = glob.glob(os.path.join(self.documents_path, "*_animation_*.json"))
                pose_files = glob.glob(os.path.join(self.documents_path, "pose_*.json"))
                all_files = json_files + pose_files
                
                if not all_files:
                    cmds.warning("No pose or animation files found.")
                    return
                
                all_files.sort(key=os.path.getmtime, reverse=True)
                filepath = all_files[0]
            
            if not os.path.exists(filepath):
                cmds.warning("File not found: {}".format(filepath))
                return
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            if not data:
                cmds.warning("No pose data found in file.")
                return
            
            if "pose" in data:
                pose_data = data["pose"]
            else:
                pose_data = data
            
            cmds.undoInfo(openChunk=True)
            
            try:
                all_objects = cmds.ls(long=True) if not selected_objects else None
                
                for obj_name, attrs in pose_data.items():
                    if target_namespace is not None:
                        if target_namespace:
                            target_obj = target_namespace + ":" + obj_name.split(':')[-1]
                        else:
                            target_obj = obj_name.split(':')[-1]
                    else:
                        target_obj = obj_name
                    
                    if selected_objects:
                        target_obj_full = None
                        target_short = target_obj.split(':')[-1]
                        
                        for sel_obj in selected_objects:
                            sel_short = sel_obj.split('|')[-1]
                            if sel_short == target_obj or sel_short.split(':')[-1] == target_short:
                                if cmds.objExists(sel_obj):
                                    target_obj_full = sel_obj
                                    break
                        
                        if not target_obj_full:
                            continue
                    else:
                        if cmds.objExists(target_obj):
                            target_obj_full = target_obj
                        else:
                            matching = cmds.ls(target_obj, long=True)
                            if matching:
                                target_obj_full = matching[0]
                            else:
                                target_short = target_obj.split(':')[-1]
                                matching_objects = [obj for obj in all_objects if obj.split('|')[-1].split(':')[-1] == target_short]
                                
                                if not matching_objects:
                                    continue
                                
                                best_match = None
                                for match in matching_objects:
                                    match_short = match.split('|')[-1]
                                    if match_short == target_obj:
                                        best_match = match
                                        break
                                
                                if not best_match:
                                    best_match = matching_objects[0]
                                
                                target_obj_full = best_match
                    
                    for attr_name, value in attrs.items():
                        full_attr = target_obj_full + '.' + attr_name
                        
                        if not cmds.objExists(full_attr):
                            continue
                        
                        if cmds.getAttr(full_attr, lock=True):
                            continue
                        
                        try:
                            cmds.setAttr(full_attr, value)
                        except:
                            continue
            
            finally:
                cmds.undoInfo(closeChunk=True)
                
        finally:
            cmds.waitCursor(state=False)
    
    def get_latest_pose_file(self):
        json_files = glob.glob(os.path.join(self.documents_path, "*_animation_*.json"))
        pose_files = glob.glob(os.path.join(self.documents_path, "pose_*.json"))
        all_files = json_files + pose_files
        
        if not all_files:
            return None
        
        latest_file = max(all_files, key=os.path.getmtime)
        return latest_file


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class ModernAnimationCopyPasteUI(QtWidgets.QDialog):
    
    option_var_name = "ModernAnimCopyPasteUI_lastPos"
    
    def __init__(self, parent=get_maya_main_window()):
        super(ModernAnimationCopyPasteUI, self).__init__(parent)
        
        self.dpi_scale = self.get_dpi_scale()
        
        if sys.platform == "darwin":
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.Window |
                QtCore.Qt.WindowStaysOnTopHint
            )
        else:
            self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint |
                QtCore.Qt.Window
            )
        
        base_width = 280
        base_height = 380
        self.setFixedSize(int(base_width * self.dpi_scale), int(base_height * self.dpi_scale))
        self.setWindowOpacity(0.0)
        
        self.tool = AnimationCopyPasteJson()
        self.maya_main_window = get_maya_main_window()
        self.old_pos = None
        self.selected_file = None
        
        self.build_ui()
        self.apply_dark_theme()
        self.update_file_info()
        
        if cmds.optionVar(exists=self.option_var_name):
            pos_str = cmds.optionVar(q=self.option_var_name)
            try:
                x, y = map(int, pos_str.split(","))
                self.move(x, y)
            except:
                pass
        
        self.fade_to(0.9)
    
    def get_dpi_scale(self):
        """Get DPI scale factor for high-DPI displays"""
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            if screen:
                dpi = screen.logicalDotsPerInch()
                scale = dpi / 96.0
                if scale > 1.5:
                    return 1.5
                elif scale > 1.25:
                    return 1.3
                elif scale > 1.0:
                    return 1.15
            return 1.0
        except:
            return 1.0
    
    def closeEvent(self, event):
        pos = self.pos()
        pos_str = "{},{}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        super(ModernAnimationCopyPasteUI, self).closeEvent(event)
    
    def has_selection(self):
        return bool(cmds.ls(selection=True))
    
    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(
            int(8 * self.dpi_scale), 
            int(6 * self.dpi_scale), 
            int(8 * self.dpi_scale), 
            int(6 * self.dpi_scale)
        )
        layout.setSpacing(int(5 * self.dpi_scale))
        
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(int(5 * self.dpi_scale))
        
        title_label = QtWidgets.QLabel("")
        title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        font_size = int(10 * self.dpi_scale)
        title_label.setStyleSheet("font-weight: bold; font-size: {}pt; color: #E0E0E0;".format(font_size))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.exit_btn = QtWidgets.QPushButton("")
        btn_size = int(18 * self.dpi_scale)
        self.exit_btn.setFixedSize(btn_size, btn_size)
        exit_font_size = int(11 * self.dpi_scale)
        border_radius = int(3 * self.dpi_scale)
        self.exit_btn.setStyleSheet("""
            QPushButton {{
                background: #e74c3c;
                border: none;
                color: #fff;
                font-size: {}px;
                font-weight: bold;
                border-radius: {}px;
            }}
            QPushButton:hover {{ background: #c0392b; }}
        """.format(exit_font_size, border_radius))
        self.exit_btn.clicked.connect(self.close)
        header_layout.addWidget(self.exit_btn)
        
        layout.addLayout(header_layout)
        
        copy_label = QtWidgets.QLabel("COPY ANIM")
        label_font_size = int(10 * self.dpi_scale)
        margin_top = int(3 * self.dpi_scale)
        margin_bottom = int(1 * self.dpi_scale)
        copy_label.setStyleSheet("font-size: {}pt; color: #FF7F32; font-weight: bold; margin-top: {}px; margin-bottom: {}px;".format(label_font_size, margin_top, margin_bottom))
        layout.addWidget(copy_label)
        
        copy_layout = QtWidgets.QHBoxLayout()
        copy_layout.setSpacing(int(5 * self.dpi_scale))
        
        self.copy_selected_btn = QtWidgets.QPushButton("Copy Selected Curves")
        btn_height = int(22 * self.dpi_scale)
        self.copy_selected_btn.setFixedHeight(btn_height)
        self.copy_selected_btn.clicked.connect(self.copy_selected_animation)
        self.copy_selected_btn.setObjectName("copyButton")
        
        self.copy_all_btn = QtWidgets.QPushButton("Copy All Animation")
        self.copy_all_btn.setFixedHeight(btn_height)
        self.copy_all_btn.clicked.connect(self.copy_all_animation)
        self.copy_all_btn.setObjectName("copyAllButton")
        self.copy_all_btn.setToolTip("Copy all animation from selected controls")
        
        copy_layout.addWidget(self.copy_all_btn)
        copy_layout.addWidget(self.copy_selected_btn)
        layout.addLayout(copy_layout)
        
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        sep_margin = int(5 * self.dpi_scale)
        separator.setStyleSheet("color: #555555; background-color: #555555; border: none; height: 1px; margin: {}px 0px;".format(sep_margin))
        layout.addWidget(separator)
        
        self.file_info_label = QtWidgets.QLabel("No files found")
        info_font_size = int(7 * self.dpi_scale)
        info_margin = int(2 * self.dpi_scale)
        self.file_info_label.setStyleSheet("font-size: {}pt; color: #AAAAAA; font-style: italic; margin-bottom: {}px;".format(info_font_size, info_margin))
        self.file_info_label.setWordWrap(True)
        layout.addWidget(self.file_info_label)
        
        paste_label = QtWidgets.QLabel("PASTE ANIM")
        paste_margin = int(1 * self.dpi_scale)
        paste_label.setStyleSheet("font-size: {}pt; color: #FF7F32; font-weight: bold; margin-bottom: {}px;".format(label_font_size, paste_margin))
        layout.addWidget(paste_label)
        
        self.select_objects_btn = QtWidgets.QPushButton("Select Objects From Selection")
        self.select_objects_btn.setFixedHeight(btn_height)
        self.select_objects_btn.clicked.connect(self.select_objects_from_json)
        self.select_objects_btn.setObjectName("selectButton")
        layout.addWidget(self.select_objects_btn)
        
        ns_layout = QtWidgets.QHBoxLayout()
        ns_margin_top = int(2 * self.dpi_scale)
        ns_margin_bottom = int(3 * self.dpi_scale)
        ns_layout.setContentsMargins(0, ns_margin_top, 0, ns_margin_bottom)
        ns_layout.setSpacing(int(5 * self.dpi_scale))
        
        ns_label = QtWidgets.QLabel("Namespace:")
        ns_label_width = int(60 * self.dpi_scale)
        ns_label.setFixedWidth(ns_label_width)
        ns_font_size = int(8 * self.dpi_scale)
        ns_label.setStyleSheet("font-size: {}pt; color: #CCCCCC;".format(ns_font_size))
        
        self.namespace_combo = QtWidgets.QComboBox()
        combo_height = int(19 * self.dpi_scale)
        self.namespace_combo.setFixedHeight(combo_height)
        self.update_namespace_list()
        
        ns_layout.addWidget(ns_label)
        ns_layout.addWidget(self.namespace_combo)
        layout.addLayout(ns_layout)
        
        main_buttons_layout = QtWidgets.QHBoxLayout()
        main_buttons_layout.setSpacing(int(5 * self.dpi_scale))
        
        self.insert_btn = QtWidgets.QPushButton("Insert Animation")
        main_btn_height = int(26 * self.dpi_scale)
        self.insert_btn.setFixedHeight(main_btn_height)
        self.insert_btn.clicked.connect(lambda: self.paste_animation(True, self.has_selection()))
        self.insert_btn.setObjectName("insertButton")

        self.replace_btn = QtWidgets.QPushButton("Replace Animation")
        self.replace_btn.setFixedHeight(main_btn_height)
        self.replace_btn.clicked.connect(lambda: self.paste_animation(False, self.has_selection()))
        self.replace_btn.setObjectName("replaceButton")
        
        main_buttons_layout.addWidget(self.replace_btn)
        main_buttons_layout.addWidget(self.insert_btn)
        layout.addLayout(main_buttons_layout)
        
        self.browse_btn = QtWidgets.QPushButton("Browse Files...")
        browse_height = int(20 * self.dpi_scale)
        self.browse_btn.setFixedHeight(browse_height)
        self.browse_btn.clicked.connect(self.browse_files)
        self.browse_btn.setObjectName("browseButton")
        layout.addWidget(self.browse_btn)
        
        pose_layout = QtWidgets.QHBoxLayout()
        pose_layout.setSpacing(int(5 * self.dpi_scale))
        
        self.copy_pose_btn = QtWidgets.QPushButton("Copy Pose")
        self.copy_pose_btn.setFixedHeight(btn_height)
        self.copy_pose_btn.clicked.connect(self.copy_pose)
        self.copy_pose_btn.setObjectName("copyPoseButton")
        
        self.paste_pose_btn = QtWidgets.QPushButton("Paste Pose")
        self.paste_pose_btn.setFixedHeight(btn_height)
        self.paste_pose_btn.clicked.connect(self.paste_pose)
        self.paste_pose_btn.setObjectName("pastePoseButton")
        
        pose_layout.addWidget(self.copy_pose_btn)
        pose_layout.addWidget(self.paste_pose_btn)
        layout.addLayout(pose_layout)
        
        self.status_label = QtWidgets.QLabel("")
        self.status_label.setStyleSheet("font-size: 7pt; color: #888888; margin-top: 1px;")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
    
    def apply_dark_theme(self):
        label_font = int(8 * self.dpi_scale)
        button_font = int(8 * self.dpi_scale)
        combo_font = int(8 * self.dpi_scale)
        border_radius = int(3 * self.dpi_scale)
        combo_border_radius = int(2 * self.dpi_scale)
        padding_v = int(4 * self.dpi_scale)
        padding_h = int(8 * self.dpi_scale)
        combo_padding_v = int(2 * self.dpi_scale)
        combo_padding_h = int(6 * self.dpi_scale)
        dropdown_width = int(16 * self.dpi_scale)
        arrow_size = int(3 * self.dpi_scale)
        arrow_margin = int(4 * self.dpi_scale)
        
        self.setStyleSheet("""
            QDialog {{ 
                background-color: #2E2E2E; 
                color: #E0E0E0; 
            }}
            QLabel {{ 
                color: #CCCCCC; 
                font-size: {label_font}pt; 
            }}
            QPushButton {{
                background-color: #3C3C3C;
                color: #E0E0E0;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
                font-size: {button_font}pt;
                padding: {padding_v}px {padding_h}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #4A4A4A;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
            QPushButton#copyButton {{
                background-color: #4A90E2;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#copyButton:hover {{ 
                background-color: #6BA6F2; 
            }}
            QPushButton#copyButton:pressed {{ 
                background-color: #3A7BC8; 
            }}
            QPushButton#copyAllButton {{
                background-color: #8E44AD;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#copyAllButton:hover {{ 
                background-color: #A569BD; 
            }}
            QPushButton#copyAllButton:pressed {{ 
                background-color: #7D3C98; 
            }}
            QPushButton#insertButton {{
                background-color: #FF7F32;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#insertButton:hover {{ 
                background-color: #FFA055; 
            }}
            QPushButton#insertButton:pressed {{ 
                background-color: #CC6626; 
            }}
            QPushButton#replaceButton {{
                background-color: #E74C3C;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#replaceButton:hover {{ 
                background-color: #F1687D; 
            }}
            QPushButton#replaceButton:pressed {{ 
                background-color: #C0392B; 
            }}
            QPushButton#browseButton {{
                background-color: #5A5A5A;
                border: 1px solid #666666;
                color: #E0E0E0;
                font-weight: 500;
            }}
            QPushButton#browseButton:hover {{
                background-color: #6A6A6A;
            }}
            QPushButton#selectButton {{
                background-color: #27AE60;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#selectButton:hover {{ 
                background-color: #2ECC71; 
            }}
            QPushButton#selectButton:pressed {{ 
                background-color: #229954; 
            }}
            QPushButton#copyPoseButton {{
                background-color: #16A085;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#copyPoseButton:hover {{ 
                background-color: #1ABC9C; 
            }}
            QPushButton#copyPoseButton:pressed {{ 
                background-color: #138F7A; 
            }}
            QPushButton#pastePoseButton {{
                background-color: #D35400;
                border: none;
                color: white;
                font-weight: bold;
            }}
            QPushButton#pastePoseButton:hover {{ 
                background-color: #E67E22; 
            }}
            QPushButton#pastePoseButton:pressed {{ 
                background-color: #BA4A00; 
            }}
            QComboBox {{
                background-color: #3C3C3C;
                border: 1px solid #555555;
                border-radius: {combo_border_radius}px;
                color: #E0E0E0;
                font-size: {combo_font}pt;
                padding: {combo_padding_v}px {combo_padding_h}px;
            }}
            QComboBox:hover {{
                background-color: #4A4A4A;
            }}
            QComboBox::drop-down {{
                border: none;
                width: {dropdown_width}px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: {arrow_size}px solid transparent;
                border-right: {arrow_size}px solid transparent;
                border-top: {arrow_size}px solid #CCCCCC;
                margin-right: {arrow_margin}px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #3C3C3C;
                border: 1px solid #555555;
                color: #E0E0E0;
                selection-background-color: #FF7F32;
            }}
        """.format(
            label_font=label_font,
            button_font=button_font,
            combo_font=combo_font,
            border_radius=border_radius,
            combo_border_radius=combo_border_radius,
            padding_v=padding_v,
            padding_h=padding_h,
            combo_padding_v=combo_padding_v,
            combo_padding_h=combo_padding_h,
            dropdown_width=dropdown_width,
            arrow_size=arrow_size,
            arrow_margin=arrow_margin
        ))
    
    def fade_to(self, target_opacity):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        self.anim.start()
    
    def enterEvent(self, event):
        self.fade_to(1)
        super(ModernAnimationCopyPasteUI, self).enterEvent(event)

    def leaveEvent(self, event):
        self.fade_to(0.5)
        super(ModernAnimationCopyPasteUI, self).leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()
        elif event.button() == QtCore.Qt.RightButton:
            self.show_context_menu(event.globalPos())
    
    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.old_pos = None
    
    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2E2E2E;
                border: 1px solid #555555;
                border-radius: 4px;
                color: #E0E0E0;
                font-size: 8pt;
            }
            QMenu::item {
                padding: 6px 12px;
                border-radius: 2px;
                margin: 1px;
            }
            QMenu::item:selected {
                background-color: #FF7F32;
                color: white;
            }
        """)
        
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_ui)
        
        if self.selected_file:
            clear_action = menu.addAction("Use Latest File")
            clear_action.triggered.connect(self.clear_selected_file)
        
        menu.addSeparator()
        
        exit_action = menu.addAction("Close")
        action = menu.exec_(pos)
        if action == exit_action:
            self.close()
    
    def clear_selected_file(self):
        self.selected_file = None
        self.update_file_info()
    
    def refresh_ui(self):
        self.update_file_info()
        self.update_namespace_list()
    
    def update_namespace_list(self):
        self.namespace_combo.clear()
        namespaces = self.tool.get_all_namespaces()
        
        for ns in namespaces:
            display_name = "<root>" if ns == "" else ns
            self.namespace_combo.addItem(display_name, ns)
    
    def update_file_info(self):
        if self.selected_file:
            filename = os.path.basename(self.selected_file)
            if len(filename) > 28:
                filename = filename[:25] + "..."
            
            try:
                import time
                mod_time = os.path.getmtime(self.selected_file)
                date_str = time.strftime("%m/%d %H:%M", time.localtime(mod_time))
                self.file_info_label.setText("Selected: {}\n{}".format(filename, date_str))
            except:
                self.file_info_label.setText("Selected: {}".format(filename))
        else:
            latest_file = self.tool.get_latest_json_file()
            
            if latest_file:
                filename = os.path.basename(latest_file)
                if len(filename) > 32:
                    filename = filename[:29] + "..."
                
                try:
                    import time
                    mod_time = os.path.getmtime(latest_file)
                    date_str = time.strftime("%m/%d %H:%M", time.localtime(mod_time))
                    self.file_info_label.setText("Latest: {}\n{}".format(filename, date_str))
                except:
                    self.file_info_label.setText("Latest: {}".format(filename))
            else:
                self.file_info_label.setText("No animation files found")
        
        files = self.tool.get_all_json_files()
        file_count = len(files)
        status_text = "Files in folder: {}".format(file_count)
        if self.selected_file:
            status_text += " | Using selected file"
        self.status_label.setText(status_text)
    
    def get_target_namespace(self):
        index = self.namespace_combo.currentIndex()
        if index >= 0:
            return self.namespace_combo.itemData(index)
        return None
    
    def copy_selected_animation(self):
        self.show_button_feedback(self.copy_selected_btn)
        
        cmds.waitCursor(state=True)
        try:
            result = self.tool.copy_selected_animation_to_json()
            if result:
                self.selected_file = None
                self.update_file_info()
        finally:
            cmds.waitCursor(state=False)
    
    def copy_all_animation(self):
        self.show_button_feedback(self.copy_all_btn)
        
        cmds.waitCursor(state=True)
        try:
            result = self.tool.copy_all_animation_to_json()
            if result:
                self.selected_file = None
                self.update_file_info()
        finally:
            cmds.waitCursor(state=False)
    
    def copy_pose(self):
        self.show_button_feedback(self.copy_pose_btn)
        cmds.waitCursor(state=True)
        try:
            filepath = self.tool.copy_pose_to_json()
            if filepath:
                self.update_file_info()
        finally:
            cmds.waitCursor(state=False)
    
    def paste_pose(self):
        self.show_button_feedback(self.paste_pose_btn)
        target_ns = self.get_target_namespace()
        selected_objects = cmds.ls(selection=True)
        
        if selected_objects and (target_ns == "" or target_ns is None):
            target_namespaces = self.detect_multiple_namespaces_from_selection(selected_objects)
            
            if self.selected_file:
                anim_data = self.tool.load_animation_data(self.selected_file)
            else:
                latest_file = self.tool.get_latest_pose_file()
                if latest_file:
                    anim_data = self.tool.load_animation_data(latest_file)
                else:
                    anim_data = None
            
            if anim_data and target_namespaces:
                source_ns = self.tool.detect_source_namespace(anim_data)
                target_ns_from_selection = target_namespaces[0] if target_namespaces else ""
                
                if source_ns != target_ns_from_selection:
                    target_ns = target_ns_from_selection
                else:
                    target_ns = None
        
        cmds.waitCursor(state=True)
        try:
            if self.selected_file and "pose_" in os.path.basename(self.selected_file):
                self.tool.paste_pose_from_json(self.selected_file, target_namespace=target_ns, selected_objects=selected_objects)
            else:
                self.tool.paste_pose_from_json(target_namespace=target_ns, selected_objects=selected_objects)
        finally:
            cmds.waitCursor(state=False)
    
    def detect_multiple_namespaces_from_selection(self, selected_objects):
        if not selected_objects:
            return []
        
        namespaces = set()
        
        for obj in selected_objects:
            obj_short = obj.split('|')[-1]
            if ":" in obj_short:
                namespace = obj_short.split(":")[0]
                namespaces.add(namespace)
            else:
                namespaces.add("")
        
        return list(namespaces)
    
    def apply_animation_to_multiple_namespaces(self, paste_in_place, only_selected, source_namespaces, target_namespaces, filepath=None):
        return self.tool.apply_animation_to_multiple_namespaces(
            paste_in_place, only_selected, source_namespaces, target_namespaces, filepath
        )
    
    def select_objects_from_json(self):
        if self.selected_file:
            self.tool.select_objects_from_json_file(self.selected_file)
        else:
            self.tool.select_objects_from_json()
    
    def paste_animation(self, paste_in_place, only_selected):
        if paste_in_place and not only_selected:
            self.show_button_feedback(self.insert_btn)
        elif not paste_in_place and not only_selected:
            self.show_button_feedback(self.replace_btn)
        elif paste_in_place and only_selected:
            self.show_button_feedback(self.insert_btn)
        else:
            self.show_button_feedback(self.replace_btn)
        
        target_ns = self.get_target_namespace()
        
        cmds.waitCursor(state=True)
        try:
            if only_selected:
                selected_objects = cmds.ls(selection=True)
                if not selected_objects:
                    cmds.warning("No objects selected for paste operation.")
                    return
                
                target_namespaces = self.detect_multiple_namespaces_from_selection(selected_objects)
                
                if len(target_namespaces) > 1:
                    
                    if self.selected_file:
                        anim_data = self.tool.load_animation_data(self.selected_file)
                        filepath = self.selected_file
                    else:
                        latest_file = self.tool.get_latest_json_file()
                        if latest_file:
                            anim_data = self.tool.load_animation_data(latest_file)
                            filepath = latest_file
                        else:
                            anim_data = None
                            filepath = None
                    
                    if anim_data:
                        source_ns = self.tool.detect_source_namespace(anim_data)
                        self.apply_animation_to_multiple_namespaces(
                            paste_in_place, True, source_ns, target_namespaces, filepath
                        )
                    return
                else:
                    target_ns_from_selection = target_namespaces[0] if target_namespaces else ""
                    
                    if self.selected_file:
                        anim_data = self.tool.load_animation_data(self.selected_file)
                    else:
                        latest_file = self.tool.get_latest_json_file()
                        if latest_file:
                            anim_data = self.tool.load_animation_data(latest_file)
                        else:
                            anim_data = None
                    
                    if anim_data:
                        source_ns = self.tool.detect_source_namespace(anim_data)
                        
                        if source_ns != target_ns_from_selection:
                            target_ns = target_ns_from_selection
                        else:
                            target_ns = None
            else:
                if target_ns == "":
                    target_ns = None
            
            if self.selected_file:
                self.tool.paste_from_file(
                    self.selected_file,
                    paste_in_place=paste_in_place,
                    only_selected=only_selected,
                    target_namespace=target_ns
                )
            else:
                self.tool.paste_latest_animation(
                    paste_in_place=paste_in_place,
                    only_selected=only_selected,
                    target_namespace=target_ns
                )
                
        finally:
            cmds.waitCursor(state=False)

            
    
    def browse_files(self):
        json_files = self.tool.get_all_json_files()
        
        if not json_files:
            cmds.confirmDialog(
                title="No Files Found",
                message="No animation JSON files found in Documents folder.",
                button=["OK"]
            )
            return
        
        result = cmds.fileDialog2(
            fileMode=1,
            caption="Select Animation File",
            fileFilter="JSON Files (*.json)",
            startingDirectory=self.tool.documents_path
        )
        
        if result:
            self.selected_file = result[0]
            self.update_file_info()
    
    def show_button_feedback(self, button):
        original_style = button.styleSheet()
        
        if "FF7F32" in original_style:
            feedback_style = original_style.replace("#FF7F32", "#FFA055")
        elif "E74C3C" in original_style:
            feedback_style = original_style.replace("#E74C3C", "#F1687D")
        elif "4A90E2" in original_style:
            feedback_style = original_style.replace("#4A90E2", "#6BA6F2")
        elif "8E44AD" in original_style:
            feedback_style = original_style.replace("#8E44AD", "#A569BD")
        elif "27AE60" in original_style:
            feedback_style = original_style.replace("#27AE60", "#2ECC71")
        elif "16A085" in original_style:
            feedback_style = original_style.replace("#16A085", "#1ABC9C")
        elif "D35400" in original_style:
            feedback_style = original_style.replace("#D35400", "#E67E22")
        else:
            feedback_style = original_style.replace("#3C3C3C", "#4A4A4A")
        
        button.setStyleSheet(feedback_style)
        QtCore.QTimer.singleShot(150, lambda: button.setStyleSheet(original_style))


def show_modern_animation_copy_paste_ui():
    global modern_anim_ui
    try:
        modern_anim_ui.close()
        modern_anim_ui.deleteLater()
    except:
        pass
    
    modern_anim_ui = ModernAnimationCopyPasteUI()
    modern_anim_ui.show()


def create_complete_animation_ui():
    show_modern_animation_copy_paste_ui()

def create_animation_paste_ui():
    show_modern_animation_copy_paste_ui()

def create_animation_copy_ui():
    show_modern_animation_copy_paste_ui()

def copy_selected_animation_to_json():
    tool = AnimationCopyPasteJson()
    return tool.copy_selected_animation_to_json()

def copy_all_animation_to_json(self):
    cmds.waitCursor(state=True)
    
    try:
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("No objects selected. Please select controls to copy all their animation.")
            return None
        
        all_anim_curves = []
        for obj in selected_objects:
            curves = cmds.keyframe(obj, query=True, name=True)
            if curves:
                all_anim_curves.extend(curves)
        
        if not all_anim_curves:
            cmds.warning("No animation curves found on selected objects.")
            return None
        
        anim_data = self.get_anim_data(anim_curves=all_anim_curves, range_all=True)
        if anim_data:
            return self.save_to_json(anim_data)
        return None
        
    finally:
        cmds.waitCursor(state=False)

def paste_latest_animation_in_place():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=False)

def paste_latest_animation_original():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=False, only_selected=False)

def paste_to_selected_only():
    tool = AnimationCopyPasteJson()
    return tool.paste_latest_animation(paste_in_place=True, only_selected=True)

if __name__ == "__main__":
    show_modern_animation_copy_paste_ui()
else:
    show_modern_animation_copy_paste_ui()