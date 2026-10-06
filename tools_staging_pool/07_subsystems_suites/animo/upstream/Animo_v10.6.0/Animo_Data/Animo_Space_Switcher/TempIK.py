from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import maya.cmds as cmds
import sys

try:
    from spacify_core import SPACIFY_STATE
except:
    SPACIFY_STATE = {"only_keys": False}


def get_all_keyframe_times(objects):
    all_keys = set()
    for obj in objects:
        if cmds.objExists(obj):
            keys = cmds.keyframe(obj, q=True) or []
            for k in keys:
                all_keys.add(k)
    return sorted(list(all_keys))


def smart_bake_ik(objects, start_time, end_time, source_objects=None):
    """
    Bake animation on objects.
    If source_objects provided with Only Keys mode:
    - Constraints should already exist with maintain offset
    - We just go to each key time and set a key on the constrained objects
    - Use dgeval to force constraint evaluation without unsuspending refresh
    """
    only_keys = SPACIFY_STATE.get("only_keys", False)
    
    if not objects:
        return
    
    if isinstance(objects, str):
        objects = [objects]
    
    if not only_keys:
        cmds.bakeResults(objects, time=(start_time, end_time),
                         simulation=False, preserveOutsideKeys=True)
    else:
        key_source = source_objects if source_objects else objects
        if isinstance(key_source, str):
            key_source = [key_source]
        
        key_times = get_all_keyframe_times(key_source)
        
        if not key_times:
            key_times = [start_time, end_time]
        
        ct = cmds.currentTime(q=True)
        
        for t in key_times:
            cmds.currentTime(t, update=True)
            for obj in objects:
                if cmds.objExists(obj):
                    cmds.dgeval(obj + '.translate', obj + '.rotate')
                    if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                        try:
                            cmds.setAttr(obj + '.blendParent1', 1)
                        except:
                            pass
                    cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
        
        cmds.currentTime(ct)


def display_selection_warning():
    cmds.confirmDialog(
        title='Selection Error',
        message='Please ensure you have 3 controls selected in order:\n\n1. Top Control\n2. Mid Control\n3. Bottom Control',
        button=['OK'],
        defaultButton='OK',
        backgroundColor=[0.15, 0.15, 0.15]
    )


def display_error_dialog(message):
    cmds.confirmDialog(
        title='Error',
        message=message,
        button=['OK'],
        defaultButton='OK',
        icon='critical',
        backgroundColor=[0.2, 0.1, 0.1]
    )


def query_eval_mode():
    try:
        return cmds.evaluationManager(query=True, mode=True)[0]
    except:
        return 'off'


def change_eval_mode(mode):
    try:
        current_mode = query_eval_mode()
        if current_mode != mode:
            cmds.evaluationManager(mode=mode)
        return current_mode
    except:
        return 'off'


def revert_eval_mode(original_mode):
    try:
        change_eval_mode(original_mode)
    except:
        pass


def find_or_make_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group


def get_unique_name(base_name):
    if not cmds.objExists(base_name):
        return base_name
    
    counter = 1
    candidate = "{0}{1}".format(base_name, counter)
    while cmds.objExists(candidate):
        counter += 1
        candidate = "{0}{1}".format(base_name, counter)
    
    return candidate


def get_next_set_name():
    base_name = "spacify_temp_ik"
    counter = 1
    while True:
        set_name = "{0}_{1:02d}".format(base_name, counter)
        if not cmds.objExists(set_name):
            return set_name
        counter += 1


def remove_existing_spacify_sets(objects):
    sets_to_delete = []
    for obj in objects:
        if cmds.objExists(obj):
            try:
                obj_sets = cmds.listSets(object=obj) or []
                for obj_set in obj_sets:
                    if obj_set.startswith("spacify_temp_ik_"):
                        if obj_set not in sets_to_delete:
                            sets_to_delete.append(obj_set)
            except:
                pass
    
    for set_name in sets_to_delete:
        try:
            if cmds.objExists(set_name):
                cmds.delete(set_name)
        except:
            pass


def calculate_locator_scale(control_object, scale_multiplier=1.0):
    try:
        obj_bbox = cmds.exactWorldBoundingBox(control_object)
        obj_size = max([
            obj_bbox[3] - obj_bbox[0],
            obj_bbox[4] - obj_bbox[1],
            obj_bbox[5] - obj_bbox[2]
        ]) * 0.4 * scale_multiplier
        
        current_unit = cmds.currentUnit(query=True, linear=True)
        scale_factor = obj_size
        
        unit_multipliers = {
            'mm': 10.0, 'cm': 1.0, 'm': 0.1,
            'in': 2.54, 'ft': 0.3048, 'yd': 0.0914
        }
        
        if current_unit in unit_multipliers:
            scale_factor *= unit_multipliers[current_unit]
        
        if scale_factor <= 0.0001 or scale_factor > 100000.0:
            scale_factor = 1.0
        
        return scale_factor
    except:
        return 1.0


def apply_locator_scale(locator, scale_factor):
    try:
        loc_shape = cmds.listRelatives(locator, shapes=True)
        if loc_shape:
            cmds.setAttr("{0}.localScaleX".format(loc_shape[0]), scale_factor)
            cmds.setAttr("{0}.localScaleY".format(loc_shape[0]), scale_factor)
            cmds.setAttr("{0}.localScaleZ".format(loc_shape[0]), scale_factor)
    except:
        pass


def set_locator_color_red(locator):
    try:
        loc_shape = cmds.listRelatives(locator, shapes=True)
        if loc_shape:
            cmds.setAttr("{0}.overrideEnabled".format(loc_shape[0]), 1)
            cmds.setAttr("{0}.overrideRGBColors".format(loc_shape[0]), 1)
            cmds.setAttr("{0}.overrideColorRGB".format(loc_shape[0]), 1, 0, 0)
    except:
        pass


def calculate_pole_vector_position(top_pos, mid_pos, bot_pos, offset_distance):
    try:
        import math
        
        def magnitude(v):
            return math.sqrt(sum(x * x for x in v))
        
        def normalize(v):
            mag = magnitude(v)
            if mag < 0.0001:
                return [0, 0, 0]
            return [x / mag for x in v]
        
        def subtract(v1, v2):
            return [v1[i] - v2[i] for i in range(3)]
        
        def add(v1, v2):
            return [v1[i] + v2[i] for i in range(3)]
        
        def scale(v, s):
            return [v[i] * s for i in range(3)]
        
        def dot_product(v1, v2):
            return sum(v1[i] * v2[i] for i in range(3))
        
        top_to_bot = subtract(bot_pos, top_pos)
        top_to_mid = subtract(mid_pos, top_pos)
        
        top_to_bot_normalized = normalize(top_to_bot)
        
        projection_length = dot_product(top_to_mid, top_to_bot_normalized)
        projection_point = add(top_pos, scale(top_to_bot_normalized, projection_length))
        
        bend_direction = subtract(mid_pos, projection_point)
        bend_direction_normalized = normalize(bend_direction)
        
        if magnitude(bend_direction) < 0.0001:
            bend_direction_normalized = [0, 0, 1]
        
        pv_position = [
            mid_pos[0] + bend_direction_normalized[0] * offset_distance,
            mid_pos[1] + bend_direction_normalized[1] * offset_distance,
            mid_pos[2] + bend_direction_normalized[2] * offset_distance
        ]
        
        return pv_position, bend_direction_normalized
    except:
        return [mid_pos[0], mid_pos[1], mid_pos[2] + offset_distance], [0, 0, 1]


def execute_ik_conversion():
    original_eval_mode = None
    created_nodes = []
    original_time = None
    ik_system_grp = None
    temp_set = None
    undo_chunk_open = False
    only_keys_mode = SPACIFY_STATE.get("only_keys", False)
    
    try:
        original_time = cmds.currentTime(query=True)
        
        objects = cmds.ls(orderedSelection=True, long=False)
        
        if len(objects) < 3 or len(objects) > 4:
            display_selection_warning()
            return
        
        for obj in objects:
            if not cmds.objExists(obj):
                display_error_dialog('Selected object "{0}" does not exist.'.format(obj))
                return
        
        cmds.undoInfo(openChunk=True)
        undo_chunk_open = True
        
        remove_existing_spacify_sets(objects)
        
        set_name = get_next_set_name()
        temp_set = cmds.sets(name=set_name, empty=True)
        
        for obj in objects:
            cmds.sets(obj, add=temp_set)
        
        original_eval_mode = change_eval_mode('off')
        cmds.refresh(suspend=True)
        
        if len(objects) == 4:
            ik_parent = objects[0]
            ik_top = objects[1]
            ik_mid = objects[2]
            ik_bot = objects[3]
        elif len(objects) == 3:
            ik_top = objects[0]
            ik_mid = objects[1]
            ik_bot = objects[2]
            
            parent_list = cmds.listRelatives(ik_top, parent=True, type='transform')
            if parent_list:
                ik_parent = parent_list[0]
            else:
                ik_parent = None
        
        spacify_group = find_or_make_spacify_group()
        ik_system_grp = cmds.group(name=get_unique_name(ik_top + '_spacify_ik_system'), empty=True)
        ik_system_grp = cmds.parent(ik_system_grp, spacify_group)[0]
        created_nodes.append(ik_system_grp)
        
        cmds.select(clear=True)
        startTime = int(cmds.playbackOptions(q=True, ast=True))
        endTime = int(cmds.playbackOptions(q=True, aet=True))
        
        cmds.currentTime(startTime)
        
        ik_jnt_top = cmds.joint(name=get_unique_name(ik_top + '_spacify_ik_jnt'))
        created_nodes.append(ik_jnt_top)
        cmds.matchTransform(ik_jnt_top, ik_top, position=True, rotation=True)
        cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        
        ik_jnt_mid = cmds.joint(name=get_unique_name(ik_mid + '_spacify_ik_jnt'))
        created_nodes.append(ik_jnt_mid)
        cmds.matchTransform(ik_jnt_mid, ik_mid, position=True, rotation=True)
        cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        
        ik_jnt_bot = cmds.joint(name=get_unique_name(ik_bot + '_spacify_ik_jnt'))
        created_nodes.append(ik_jnt_bot)
        cmds.matchTransform(ik_jnt_bot, ik_bot, position=True, rotation=True)
        cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        
        try:
            bot_child = cmds.listRelatives(ik_bot, children=True, type='transform')
            if bot_child:
                cmds.select(ik_jnt_bot)
                ik_jnt_end = cmds.joint(name=get_unique_name(ik_bot + '_end_spacify_ik_jnt'))
                created_nodes.append(ik_jnt_end)
                cmds.matchTransform(ik_jnt_end, bot_child[0], position=True, rotation=True)
                cmds.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
        except:
            pass
        
        ik_handle = cmds.ikHandle(startJoint=ik_jnt_top, endEffector=ik_jnt_bot, solver='ikRPsolver', name=get_unique_name(ik_top + '_spacify_ikHandle'))[0]
        created_nodes.append(ik_handle)
        
        top_length = cmds.getAttr(ik_jnt_mid + '.translateX')
        mid_length = cmds.getAttr(ik_jnt_bot + '.translateX')
        
        total_length = abs(top_length) + abs(mid_length)
        
        loc_top = cmds.spaceLocator(name=get_unique_name(ik_top + '_spacify_loc'))
        created_nodes.append(loc_top[0])
        loc_top_grp = cmds.group(loc_top, name=get_unique_name(ik_top + '_spacify_loc_grp'))
        created_nodes.append(loc_top_grp)
        cmds.sets(loc_top, add=temp_set)
        cmds.sets(loc_top_grp, add=temp_set)
        
        top_scale = calculate_locator_scale(ik_top, scale_multiplier=1.0)
        apply_locator_scale(loc_top[0], top_scale)
        set_locator_color_red(loc_top[0])
        
        if ik_parent:
            try:
                cmds.parentConstraint(ik_parent, loc_top_grp)
            except:
                pass
        
        pv_mid = cmds.spaceLocator(name=get_unique_name(ik_mid + '_spacify_loc'))
        created_nodes.append(pv_mid[0])
        pv_mid_grp = cmds.group(pv_mid, name=get_unique_name(ik_mid + '_spacify_loc_grp'))
        created_nodes.append(pv_mid_grp)
        cmds.sets(pv_mid, add=temp_set)
        cmds.sets(pv_mid_grp, add=temp_set)
        
        mid_scale = calculate_locator_scale(ik_mid, scale_multiplier=0.7)
        apply_locator_scale(pv_mid[0], mid_scale)
        set_locator_color_red(pv_mid[0])
        
        loc_bot = cmds.spaceLocator(name=get_unique_name(ik_bot + '_spacify_loc'))
        created_nodes.append(loc_bot[0])
        cmds.sets(loc_bot, add=temp_set)
        
        bot_scale = calculate_locator_scale(ik_bot, scale_multiplier=2.5)
        apply_locator_scale(loc_bot[0], bot_scale)
        set_locator_color_red(loc_bot[0])
        
        cmds.parent(ik_jnt_top, ik_system_grp)
        cmds.hide(ik_jnt_top)
        cmds.parent(ik_handle, ik_system_grp)
        cmds.hide(ik_handle)
        cmds.parent(loc_top_grp, ik_system_grp)
        cmds.parent(pv_mid_grp, ik_system_grp)
        cmds.parent(loc_bot, ik_system_grp)
        
        constraintList = []
        constraint = cmds.parentConstraint(ik_top, loc_top, mo=False)
        constraintList.append(constraint)
        
        smart_bake_ik(loc_top, startTime, endTime, source_objects=objects)
        
        only_keys_mode = SPACIFY_STATE.get("only_keys", False)
        if only_keys_mode:
            key_times = get_all_keyframe_times(objects)
            if not key_times:
                key_times = list(range(int(startTime), int(endTime) + 1))
            for t in key_times:
                cmds.currentTime(t, update=True)
                cmds.dgeval(ik_bot + '.translate', ik_bot + '.rotate')
                cmds.matchTransform(loc_bot, ik_bot, position=True, rotation=True)
                cmds.setKeyframe(loc_bot, at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        else:
            for f in range(int(startTime), int(endTime) + 1):
                cmds.currentTime(f, update=True)
                cmds.matchTransform(loc_bot, ik_bot, position=True, rotation=True)
                cmds.setKeyframe(loc_bot, at=['tx', 'ty', 'tz', 'rx', 'ry', 'rz'])
        
        for c in constraintList:
            try:
                cmds.delete(c)
            except:
                pass
        
        cmds.currentTime(startTime)
        
        top_pos = cmds.xform(ik_jnt_top, query=True, worldSpace=True, translation=True)
        mid_pos = cmds.xform(ik_jnt_mid, query=True, worldSpace=True, translation=True)
        bot_pos = cmds.xform(ik_jnt_bot, query=True, worldSpace=True, translation=True)
        
        offset_distance = total_length * 1.5
        pv_start_position, pv_direction = calculate_pole_vector_position(top_pos, mid_pos, bot_pos, offset_distance)
        
        cmds.xform(pv_mid_grp, worldSpace=True, translation=pv_start_position)
        
        temp_pv_constraint = cmds.poleVectorConstraint(pv_mid, ik_handle)[0]
        
        try:
            mid_bbox = cmds.exactWorldBoundingBox(ik_mid)
            mid_ctrl_size = max([
                mid_bbox[3] - mid_bbox[0],
                mid_bbox[4] - mid_bbox[1],
                mid_bbox[5] - mid_bbox[2]
            ])
        except:
            mid_ctrl_size = 1.0
        
        elbow_offset_distance = abs(top_length) * 0.5 + (mid_ctrl_size * 2.0)
        
        cmds.xform(pv_mid_grp, worldSpace=True, translation=[
            mid_pos[0] + pv_direction[0] * elbow_offset_distance,
            mid_pos[1] + pv_direction[1] * elbow_offset_distance,
            mid_pos[2] + pv_direction[2] * elbow_offset_distance
        ])
        
        try:
            cmds.delete(temp_pv_constraint)
        except:
            pass
        
        temp_pv_constraint = cmds.poleVectorConstraint(pv_mid, ik_handle)[0]
        
        constraint = cmds.parentConstraint(ik_mid, pv_mid_grp, mo=True)
        constraintList = [constraint]
        
        smart_bake_ik(pv_mid_grp, startTime, endTime, source_objects=objects)
        
        for c in constraintList:
            try:
                cmds.delete(c)
            except:
                pass
        
        cmds.cutKey(pv_mid, attribute=['rx', 'ry', 'rz'], clear=True)
        cmds.matchTransform(pv_mid, ik_mid, rotation=True)
        for attr in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
            try:
                cmds.setAttr(pv_mid[0] + attr, lock=True)
            except:
                pass
        
        cmds.poleVectorConstraint(pv_mid, ik_handle)
        cmds.hide(loc_top)
        
        cmds.pointConstraint(loc_top, ik_jnt_top)
        cmds.pointConstraint(loc_bot, ik_handle)
        cmds.orientConstraint(loc_bot, ik_jnt_bot)
        
        def lockedAttrsSkip(node):
            lockedPos, lockedRot = [], []
            try:
                lockedAttr = cmds.listAttr(node, locked=True, scalar=True) or []
                for attribute in lockedAttr:
                    if attribute.startswith('translate'):
                        lockedPos.append(attribute[9:].lower())
                    elif attribute.startswith('rotate'):
                        lockedRot.append(attribute[6:].lower())
            except:
                pass
            return lockedPos, lockedRot
        
        lp, lr = lockedAttrsSkip(ik_top)
        cmds.parentConstraint(ik_jnt_top, ik_top, skipTranslate=lp, skipRotate=lr, maintainOffset=True)
        
        lp, lr = lockedAttrsSkip(ik_mid)
        cmds.parentConstraint(ik_jnt_mid, ik_mid, skipTranslate=lp, skipRotate=lr, maintainOffset=True)
        
        lp, lr = lockedAttrsSkip(ik_bot)
        cmds.parentConstraint(ik_jnt_bot, ik_bot, skipTranslate=lp, skipRotate=lr, maintainOffset=False)
        
        try:
            cmds.select(loc_bot)
            cmds.filterCurve()
        except:
            pass
        
    except Exception as e:
        error_message = 'An error occurred during IK conversion:\n\n{0}'.format(str(e))
        display_error_dialog(error_message)
        
        if undo_chunk_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except:
                pass
            undo_chunk_open = False
            
            try:
                cmds.undo()
            except:
                pass
        
        for node in reversed(created_nodes):
            if node and cmds.objExists(node):
                try:
                    cmds.delete(node)
                except:
                    pass
        
        if ik_system_grp and cmds.objExists(ik_system_grp):
            try:
                cmds.delete(ik_system_grp)
            except:
                pass
        
        if temp_set and cmds.objExists(temp_set):
            try:
                cmds.delete(temp_set)
            except:
                pass
    
    finally:
        if undo_chunk_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except:
                pass
        
        try:
            cmds.refresh(suspend=False)
        except:
            pass
        
        if original_eval_mode is not None:
            try:
                revert_eval_mode(original_eval_mode)
            except:
                pass
        
        if original_time is not None:
            try:
                cmds.currentTime(original_time)
            except:
                pass


def btl_main():
    execute_ik_conversion()


if __name__ == "__main__":
    btl_main()