from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import maya.mel as mel
import math

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max
    min = builtins.min
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
    float = builtins.float
    isinstance = builtins.isinstance
    round = builtins.round
    sorted = builtins.sorted
except:
    pass

STATE = {
    "attrMenu": None,
    "valMenu": None,
    "refreshBtn": None,
    "applyBtn": None,
    "currentFrameCheckbox": None,
    "roLabel": None,
}

rotate_order_dict = {
    0: "xyz",
    1: "yzx",
    2: "zxy",
    3: "xzy",
    4: "yxz",
    5: "zyx"
}


def initialize_ui_state(attr_combo, value_combo, refresh_btn, apply_btn, current_frame_check, ro_label):
    STATE["attrMenu"] = attr_combo
    STATE["valMenu"] = value_combo
    STATE["refreshBtn"] = refresh_btn
    STATE["applyBtn"] = apply_btn
    STATE["currentFrameCheckbox"] = current_frame_check
    STATE["roLabel"] = ro_label
    refresh_ui(attr_combo, value_combo, refresh_btn, apply_btn, current_frame_check, ro_label)


def smart_constraint(ctrl=None, obj=None):
    trans_attr = None
    rot_attr = None
    maintain_offset = False

    trans_attr = cmds.listAttr(obj, keyable=True, unlocked=True, string='translate*')
    rot_attr = cmds.listAttr(obj, keyable=True, unlocked=True, string='rotate*')

    rot_skip = []
    trans_skip = []

    for axis in ['x', 'y', 'z']:
        if trans_attr and not 'translate' + axis.upper() in trans_attr:
            trans_skip.append(axis)
        if rot_attr and not 'rotate' + axis.upper() in rot_attr:
            rot_skip.append(axis)

    if not trans_skip:
        trans_skip = 'none'
    if not rot_skip:
        rot_skip = 'none'

    constraints = []
    if rot_attr and trans_attr and rot_skip == 'none' and trans_skip == 'none':
        constraints.extend(cmds.parentConstraint(ctrl, obj, maintainOffset=maintain_offset))
    else:
        if trans_attr:
            constraints.extend(cmds.pointConstraint(ctrl, obj, skip=trans_skip, maintainOffset=maintain_offset))
        if rot_attr:
            constraints.extend(cmds.orientConstraint(ctrl, obj, skip=rot_skip, maintainOffset=maintain_offset))

    return constraints


def gimbal_risk(degrees):
    return abs(math.sin(math.radians(degrees))) * 100


def get_best_ro_simple(obj):
    if not cmds.objExists(obj + ".rotateOrder"):
        return None
    
    try:
        rx = cmds.getAttr(obj + ".rotateX")
        ry = cmds.getAttr(obj + ".rotateY")
        rz = cmds.getAttr(obj + ".rotateZ")
    except:
        return None
    
    rx = abs(rx)
    ry = abs(ry)
    rz = abs(rz)
    
    rotations = [("x", rx), ("y", ry), ("z", rz)]
    sorted_rots = sorted(rotations, key=lambda x: x[1], reverse=True)
    
    largest = sorted_rots[0][0]
    smallest = sorted_rots[2][0]
    middle = sorted_rots[1][0]
    
    best_order = largest + smallest + middle
    
    order_to_index = {"xyz": 0, "yzx": 1, "zxy": 2, "xzy": 3, "yxz": 4, "zyx": 5}
    
    return order_to_index.get(best_order, 0)


def change_rotate_order_preserve(obj, ro_index_or_str):
    if isinstance(ro_index_or_str, int):
        ro_str = rotate_order_dict[ro_index_or_str]
    else:
        ro_str = ro_index_or_str
    mel.eval('xform -roo "{0}" -preserve true "{1}";'.format(ro_str, obj))


def evaluate_best_ro_with_preserve(obj):
    if not cmds.objExists(obj + ".rotateOrder"):
        return None, None

    original_time = cmds.currentTime(q=True)
    original_autokey = cmds.autoKeyframe(q=True, state=True)
    cmds.autoKeyframe(state=False)

    try:
        original_ro = cmds.getAttr(obj + ".rotateOrder")
        best_ro, best_risk = None, float("inf")

        for ro in rotate_order_dict.keys():
            change_rotate_order_preserve(obj, ro)
            ro_str = rotate_order_dict[ro]
            mid = ro_str[1].upper()
            attr = obj + ".rotate" + mid
            if not cmds.objExists(attr):
                continue
            try:
                val = cmds.getAttr(attr)
            except Exception:
                continue

            risk = gimbal_risk(val)
            if risk < best_risk:
                best_risk = risk
                best_ro = ro

        change_rotate_order_preserve(obj, original_ro)
        return best_ro, best_risk
    finally:
        cmds.autoKeyframe(state=original_autokey)
        cmds.currentTime(original_time)


def change_ro_enhanced(ro_str, *args):
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("Please select at least one object.")
        return

    valid_objects = []
    for obj in sel:
        if cmds.objExists(obj + ".rotateOrder"):
            valid_objects.append(obj)

    if not valid_objects:
        cmds.warning("No valid objects with rotateOrder attribute found in selection.")
        return

    CT = cmds.currentTime(q=True)
    processed_objects = []
    temp_locators = []

    em_prev = None
    try:
        em_prev = cmds.evaluationManager(q=True, mode=True)
        cmds.evaluationManager(mode="off")
    except Exception:
        pass
    try:
        cmds.refresh(suspend=True)
    except Exception:
        pass

    try:
        for obj in valid_objects:
            try:
                keys = cmds.keyframe(obj, q=True, at=("rx", "ry", "rz"))

                if keys:
                    keys = list(set(keys))
                    keys.sort()

                    tempLoc = cmds.spaceLocator(n="roo_tempLoc_{0}".format(obj.split(":")[-1].split("|")[-1]))[0]
                    temp_locators.append(tempLoc)

                    for key in keys:
                        cmds.currentTime(key)
                        cmds.matchTransform(tempLoc, obj, rot=True)
                        cmds.setKeyframe(tempLoc, at=("rx", "ry", "rz"))

                    try:
                        cmds.cutKey(obj + ".ro")
                    except Exception:
                        pass
                    cmds.xform(obj, roo=ro_str, preserve=True)

                    for key in keys:
                        cmds.currentTime(key)
                        cmds.matchTransform(obj, tempLoc, rot=True)
                        cmds.setKeyframe(obj, at=("rx", "ry", "rz"))

                    processed_objects.append(obj)
                else:
                    try:
                        cmds.cutKey(obj + ".ro")
                    except Exception:
                        pass
                    change_rotate_order_preserve(obj, ro_str)
                    processed_objects.append(obj)

            except Exception:
                continue

        for tempLoc in temp_locators:
            if cmds.objExists(tempLoc):
                cmds.delete(tempLoc)

        if processed_objects:
            cmds.select(processed_objects, r=True)
        cmds.currentTime(CT)

        try:
            cmds.filterCurve()
            cmds.selectKey(cl=True)
        except Exception:
            pass

    finally:
        try:
            cmds.refresh(suspend=False)
        except Exception:
            pass

        try:
            cmds.evaluationManager(mode="parallel")
        except Exception:
            pass

    if processed_objects:
        object_count = len(processed_objects)
        if object_count == 1:
            message = 'Set to {0}'.format(ro_str.upper())
        else:
            message = 'Set {0} object(s) to {1}'.format(object_count, ro_str.upper())
        cmds.optionVar(intValue=("inViewMessageEnable", 10))
        cmds.inViewMessage(amg=message, pos='botCenter', dragKill=True, fadeOutTime=4.0, fade=True)


def set_each_object_to_best_ro(*args):
    sel = cmds.ls(selection=True, type="transform")
    if not sel:
        cmds.warning("Please select at least one transform object.")
        return

    valid_objects = []
    for obj in sel:
        if cmds.objExists(obj + ".rotateOrder"):
            valid_objects.append(obj)

    if not valid_objects:
        cmds.warning("No valid objects with rotateOrder attribute found in selection.")
        return

    processed_objects = []
    for obj in valid_objects:
        try:
            best_ro, _ = evaluate_best_ro_with_preserve(obj)
            if best_ro is not None:
                best_ro_str = rotate_order_dict[best_ro]
                cmds.select(obj, r=True)
                change_ro_enhanced(best_ro_str)
                processed_objects.append(obj)
        except Exception:
            continue

    if processed_objects:
        cmds.select(processed_objects, r=True)
        object_count = len(processed_objects)
        if object_count == 1:
            message = 'Set to Best RO'
        else:
            message = 'Set {0} object(s) to Best RO'.format(object_count)
        cmds.optionVar(intValue=("inViewMessageEnable", 10))
        cmds.inViewMessage(amg=message, pos='botCenter', dragKill=True, fadeOutTime=4.0, fade=True)


def _get_all_selected_transforms():
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        return []
    return sel


def _get_timeline_range():
    start = cmds.playbackOptions(q=True, min=True)
    end = cmds.playbackOptions(q=True, max=True)
    return int(start), int(end)


def _get_common_enum_attrs(objects):
    if not objects:
        return []

    common_attrs = None

    for obj in objects:
        try:
            ud_attrs = cmds.listAttr(obj, userDefined=True) or []
            keyable_attrs = cmds.listAttr(obj, keyable=True) or []
            cb_attrs = cmds.listAttr(obj, channelBox=True) or []
            
            all_attrs = list(set(ud_attrs + keyable_attrs + cb_attrs))
            
            valid_attrs = []
            for attr in all_attrs:
                try:
                    full_attr = "{0}.{1}".format(obj, attr)
                    if not cmds.objExists(full_attr):
                        continue
                    
                    attr_type = cmds.getAttr(full_attr, type=True)
                    
                    if attr_type == "enum":
                        valid_attrs.append(attr)
                    elif attr_type in ["double", "float", "long", "short"]:
                        if attr in ["translateX", "translateY", "translateZ",
                                   "rotateX", "rotateY", "rotateZ",
                                   "scaleX", "scaleY", "scaleZ",
                                   "visibility", "rotateOrder"]:
                            continue
                        
                        has_min = cmds.attributeQuery(attr, node=obj, minExists=True)
                        has_max = cmds.attributeQuery(attr, node=obj, maxExists=True)
                        
                        if has_min and has_max:
                            valid_attrs.append(attr)
                        elif attr.lower() in ["global", "local", "world", "follow", "space", 
                                              "parent", "orient", "point", "aim", "ik", "fk",
                                              "ikfk", "ik_fk", "stretch", "bendy", "twist"]:
                            valid_attrs.append(attr)
                            
                except Exception:
                    continue

            if common_attrs is None:
                common_attrs = set(valid_attrs)
            else:
                common_attrs = common_attrs.intersection(set(valid_attrs))

        except Exception:
            continue

    if common_attrs is None:
        return []

    return sorted(list(common_attrs))


def refresh_ui(*args):
    attr_combo = STATE["attrMenu"]
    value_combo = STATE["valMenu"]
    
    if attr_combo is None or value_combo is None:
        return

    objects = _get_all_selected_transforms()
    
    if not objects:
        attr_combo.clear()
        attr_combo.addItem("No Attributes")
        value_combo.clear()
        value_combo.addItem("No Values")
        return

    common_attrs = _get_common_enum_attrs(objects)

    attr_combo.clear()
    if not common_attrs:
        attr_combo.addItem("No Attributes")
    else:
        for attr in common_attrs:
            attr_combo.addItem(attr)

    update_value_menu(attr_combo)


def update_value_menu(attr_combo=None):
    if attr_combo is None:
        attr_combo = STATE["attrMenu"]
    value_combo = STATE["valMenu"]
    
    if attr_combo is None or value_combo is None:
        return

    value_combo.clear()

    attr = attr_combo.currentText()

    if not attr or attr == "No Attributes":
        value_combo.addItem("No Values")
        return

    objects = _get_all_selected_transforms()
    if not objects:
        value_combo.addItem("No Values")
        return

    obj = objects[0]
    full_attr = "{0}.{1}".format(obj, attr)

    if not cmds.objExists(full_attr):
        value_combo.addItem("No Values")
        return

    attr_type = cmds.getAttr(full_attr, type=True)
    
    if attr_type == "enum":
        try:
            enum_list = cmds.attributeQuery(attr, node=obj, listEnum=True)
            if enum_list:
                values = enum_list[0].split(":")
            else:
                values = []
        except Exception:
            values = []

        if not values:
            value_combo.addItem("No Values")
            return

        for val in values:
            value_combo.addItem(val)

        try:
            current_val = cmds.getAttr(full_attr)
            if current_val is not None:
                if isinstance(current_val, (int, float)):
                    current_idx = int(current_val)
                    if 0 <= current_idx < len(values):
                        value_combo.setCurrentIndex(current_idx)
        except:
            pass
    
    elif attr_type in ["double", "float", "long", "short"]:
        try:
            has_min = cmds.attributeQuery(attr, node=obj, minExists=True)
            has_max = cmds.attributeQuery(attr, node=obj, maxExists=True)
            
            if has_min and has_max:
                min_val = cmds.attributeQuery(attr, node=obj, minimum=True)[0]
                max_val = cmds.attributeQuery(attr, node=obj, maximum=True)[0]
            else:
                min_val = 0
                max_val = 10
            
            min_val = int(min_val)
            max_val = int(max_val)
            
            for i in range(min_val, max_val + 1):
                value_combo.addItem(str(i))
            
            try:
                current_val = cmds.getAttr(full_attr)
                if current_val is not None:
                    current_idx = int(round(current_val)) - min_val
                    if 0 <= current_idx < value_combo.count():
                        value_combo.setCurrentIndex(current_idx)
            except:
                pass
                
        except Exception:
            value_combo.addItem("0")
            value_combo.addItem("1")
    else:
        value_combo.addItem("No Values")


def delete_blend_parent_attr():
    sel = cmds.ls(sl=True)
    if not sel:
        return

    constraint_keywords = [
        "blendParent",
        "blendPoint",
        "blendOrient",
        "blend_",
        "orientConstraint",
        "pointConstraint",
        "parentConstraint",
        "scaleConstraint",
        "aimConstraint",
        "poleVectorConstraint",
        "geometryConstraint",
        "normalConstraint",
        "tangentConstraint"
    ]

    for obj in sel:
        try:
            user_attrs = cmds.listAttr(obj, userDefined=True) or []
            for attr in user_attrs:
                attr_lower = attr.lower()
                for keyword in constraint_keywords:
                    if keyword.lower() in attr_lower:
                        full_attr = "{0}.{1}".format(obj, attr)
                        try:
                            if cmds.objExists(full_attr):
                                cmds.deleteAttr(full_attr)
                        except Exception:
                            pass
                        break
        except Exception:
            pass


def apply_change(attr_combo, value_combo, current_frame_check):
    objects = _get_all_selected_transforms()
    if not objects:
        return

    if attr_combo is None or value_combo is None:
        return

    attr = attr_combo.currentText()
    val = value_combo.currentText()

    if not attr or not val or attr == "No Attributes" or val == "No Values":
        return

    only_current = False
    if current_frame_check is not None:
        only_current = current_frame_check.isChecked()

    if only_current:
        _apply_change_current_frame(objects, attr, val)
    else:
        _apply_change_full_range(objects, attr, val)


def _apply_change_current_frame(objects, attr, val):
    current_frame = int(cmds.currentTime(q=True))
    start_frame = current_frame
    end_frame = current_frame

    em_prev = None
    try:
        em_prev = cmds.evaluationManager(q=True, mode=True)
        cmds.evaluationManager(mode="off")
    except Exception:
        pass
    try:
        cmds.refresh(suspend=True)
    except Exception:
        pass

    try:
        processed_objects = []

        for obj in objects:
            full_attr = "{0}.{1}".format(obj, attr)
            if not cmds.objExists(full_attr):
                continue

            temp_locator = None
            try:
                temp_locator = cmds.spaceLocator(name="temp_bake_loc")[0]

                try:
                    prev_key = cmds.findKeyframe(obj, which="previous", time=(current_frame, current_frame))
                    if prev_key >= current_frame:
                        prev_key = None
                except Exception:
                    prev_key = None

                try:
                    next_key = cmds.findKeyframe(obj, which="next", time=(current_frame, current_frame))
                    if next_key <= current_frame:
                        next_key = None
                except Exception:
                    next_key = None

                if prev_key is not None:
                    try:
                        prev_val = cmds.getAttr(full_attr, time=prev_key)
                        cmds.setKeyframe(full_attr, time=int(round(prev_key)), value=prev_val, insertBlend=False)
                    except Exception:
                        pass

                if next_key is not None:
                    try:
                        next_val = cmds.getAttr(full_attr, time=next_key)
                        cmds.setKeyframe(full_attr, time=int(round(next_key)), value=next_val, insertBlend=False)
                    except Exception:
                        pass

                constraints_list = smart_constraint(ctrl=obj, obj=temp_locator)
                if not constraints_list:
                    constraints_list = []

                cmds.bakeResults(temp_locator, t=(start_frame, end_frame), at=["translate", "rotate"], simulation=True, smart=True)

                for con in constraints_list:
                    if cmds.objExists(con):
                        cmds.delete(con)

                try:
                    if cmds.attributeQuery(attr, node=obj, enum=True):
                        enum_list = cmds.attributeQuery(attr, node=obj, listEnum=True)[0].split(":")
                        idx = enum_list.index(val)
                        cmds.setAttr(full_attr, idx)
                    else:
                        try:
                            fval = float(val)
                        except Exception:
                            fval = cmds.getAttr(full_attr)
                        cmds.setAttr(full_attr, fval)
                except Exception:
                    if temp_locator and cmds.objExists(temp_locator):
                        cmds.delete(temp_locator)
                    continue

                cmds.cutKey(full_attr, t=(start_frame, end_frame))

                constraints_list2 = smart_constraint(ctrl=temp_locator, obj=obj)
                if not constraints_list2:
                    constraints_list2 = []

                cmds.bakeResults(obj, t=(start_frame, end_frame), at=["translate", "rotate"], simulation=True, smart=True)

                for con in constraints_list2:
                    if cmds.objExists(con):
                        cmds.delete(con)
                if temp_locator and cmds.objExists(temp_locator):
                    cmds.delete(temp_locator)

                try:
                    if cmds.attributeQuery(attr, node=obj, enum=True):
                        enum_list = cmds.attributeQuery(attr, node=obj, listEnum=True)[0].split(":")
                        idx = enum_list.index(val)
                        cmds.setKeyframe(full_attr, time=int(current_frame), value=idx, insertBlend=False)
                    else:
                        try:
                            fval = float(val)
                        except Exception:
                            fval = cmds.getAttr(full_attr)
                        cmds.setKeyframe(full_attr, time=int(current_frame), value=fval, insertBlend=False)
                    cmds.keyframe(full_attr, edit=True, time=(current_frame, current_frame), timeChange=int(current_frame))
                except Exception:
                    pass

                processed_objects.append(obj)

            except Exception:
                if temp_locator and cmds.objExists(temp_locator):
                    try:
                        cmds.delete(temp_locator)
                    except:
                        pass
                continue

        if processed_objects:
            cmds.select(processed_objects, r=True)

        delete_blend_parent_attr()

        try:
            cmds.keyTangent(ott="auto", itt="auto")
        except Exception:
            pass

        delete_blend_parent_attr()

    finally:
        try:
            if em_prev:
                cmds.evaluationManager(mode=em_prev)
        except Exception:
            pass
        try:
            cmds.evaluationManager(mode="parallel")
            cmds.refresh(suspend=False)
        except Exception:
            pass

        delete_blend_parent_attr()


def _apply_change_full_range(objects, attr, val):
    start_frame, end_frame = _get_timeline_range()

    actual_start = None
    actual_end = None
    for obj in objects:
        try:
            keys = cmds.keyframe(obj, q=True, timeChange=True)
            if keys:
                obj_start = min(keys)
                obj_end = max(keys)
                if actual_start is None or obj_start < actual_start:
                    actual_start = obj_start
                if actual_end is None or obj_end > actual_end:
                    actual_end = obj_end
        except:
            pass

    if actual_start is not None and actual_end is not None:
        start_frame = int(actual_start)
        end_frame = int(actual_end)

    em_prev = None
    try:
        em_prev = cmds.evaluationManager(q=True, mode=True)
        cmds.evaluationManager(mode="off")
    except Exception:
        pass
    try:
        cmds.refresh(suspend=True)
    except Exception:
        pass

    try:
        processed_objects = []

        for obj in objects:
            full_attr = "{0}.{1}".format(obj, attr)
            if not cmds.objExists(full_attr):
                continue

            temp_locator = None
            try:
                temp_locator = cmds.spaceLocator(name="temp_bake_loc")[0]

                constraints_list = smart_constraint(ctrl=obj, obj=temp_locator)
                if not constraints_list:
                    constraints_list = []

                cmds.bakeResults(temp_locator, t=(start_frame, end_frame), at=["translate", "rotate"], simulation=True, smart=True)

                for con in constraints_list:
                    if cmds.objExists(con):
                        cmds.delete(con)

                try:
                    if cmds.attributeQuery(attr, node=obj, enum=True):
                        enum_list = cmds.attributeQuery(attr, node=obj, listEnum=True)[0].split(":")
                        idx = enum_list.index(val)
                        cmds.setKeyframe(full_attr, time=start_frame, value=idx, insertBlend=False)
                        cmds.setKeyframe(full_attr, time=end_frame, value=idx, insertBlend=False)
                    else:
                        try:
                            fval = float(val)
                        except Exception:
                            fval = cmds.getAttr(full_attr)
                        cmds.setKeyframe(full_attr, time=start_frame, value=fval, insertBlend=False)
                        cmds.setKeyframe(full_attr, time=end_frame, value=fval, insertBlend=False)
                except Exception:
                    if temp_locator and cmds.objExists(temp_locator):
                        cmds.delete(temp_locator)
                    continue

                try:
                    cmds.cutKey(full_attr)
                except Exception:
                    pass

                try:
                    if cmds.attributeQuery(attr, node=obj, enum=True):
                        enum_list = cmds.attributeQuery(attr, node=obj, listEnum=True)[0].split(":")
                        idx = enum_list.index(val)
                        cmds.setAttr(full_attr, idx)
                    else:
                        try:
                            fval = float(val)
                        except Exception:
                            fval = cmds.getAttr(full_attr)
                        cmds.setAttr(full_attr, fval)
                except Exception:
                    pass

                constraints_list2 = smart_constraint(ctrl=temp_locator, obj=obj)
                if not constraints_list2:
                    constraints_list2 = []

                cmds.bakeResults(obj, t=(start_frame, end_frame), at=["translate", "rotate"], simulation=True, smart=True)

                for con in constraints_list2:
                    if cmds.objExists(con):
                        cmds.delete(con)
                if temp_locator and cmds.objExists(temp_locator):
                    cmds.delete(temp_locator)

                processed_objects.append(obj)

            except Exception:
                if temp_locator and cmds.objExists(temp_locator):
                    try:
                        cmds.delete(temp_locator)
                    except:
                        pass
                continue

        if processed_objects:
            cmds.select(processed_objects, r=True)

        delete_blend_parent_attr()

        try:
            cmds.keyTangent(ott="auto", itt="auto")
        except Exception:
            pass

        delete_blend_parent_attr()

    finally:
        try:
            if em_prev:
                cmds.evaluationManager(mode=em_prev)
        except Exception:
            pass
        try:
            cmds.evaluationManager(mode="parallel")
            cmds.refresh(suspend=False)
        except Exception:
            pass

        delete_blend_parent_attr()
