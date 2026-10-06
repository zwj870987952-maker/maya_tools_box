from maya import cmds
import maya.mel as mel
import sys

def get_evaluation_mode():
    return cmds.evaluationManager(query=True, mode=True)[0]

def set_evaluation_mode(mode):
    current_mode = get_evaluation_mode()
    if current_mode != mode:
        cmds.evaluationManager(mode=mode)
    return current_mode

def restore_evaluation_mode(original_mode):
    set_evaluation_mode(original_mode)

def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')

def get_short_name(long_name):
    return long_name.split('|')[-1]

def is_in_spacify_ik_set(obj):
    try:
        obj_sets = cmds.listSets(object=obj) or []
        for obj_set in obj_sets:
            if obj_set.startswith("spacify_temp_ik_"):
                return True
    except:
        pass
    return False

def is_in_relative_space_set(obj):
    try:
        obj_sets = cmds.listSets(object=obj) or []
        for obj_set in obj_sets:
            if obj_set == "relative_space_01":
                return True
    except:
        pass
    return False

def is_in_fk_chain_set(obj):
    try:
        obj_sets = cmds.listSets(object=obj) or []
        for obj_set in obj_sets:
            if obj_set == "esn_fk_set":
                return True
    except:
        pass
    return False


def is_in_camera_space_set(obj):
    try:
        obj_sets = cmds.listSets(object=obj) or []
        for obj_set in obj_sets:
            if obj_set.startswith("spacify_camera_space_"):
                return True
    except:
        pass
    return False


def partition_selection_by_sets(sel):
    ik_objs = []
    relative_objs = []
    fk_objs = []
    camera_space_objs = []
    other_objs = []
    
    for obj in sel:
        if is_in_spacify_ik_set(obj):
            ik_objs.append(obj)
        elif is_in_relative_space_set(obj):
            relative_objs.append(obj)
        elif is_in_fk_chain_set(obj):
            fk_objs.append(obj)
        elif is_in_camera_space_set(obj):
            camera_space_objs.append(obj)
        else:
            other_objs.append(obj)
    
    return ik_objs, relative_objs, fk_objs, camera_space_objs, other_objs

def find_relative_space_sets_from_selection(sel):
    relative_space_sets = set()
    for obj in sel:
        if cmds.objExists(obj):
            try:
                obj_sets = cmds.listSets(object=obj) or []
                for obj_set in obj_sets:
                    if obj_set == "relative_space_01":
                        relative_space_sets.add(obj_set)
            except:
                pass
    return list(relative_space_sets)

def get_objects_from_relative_space_set(set_name):
    try:
        set_members = cmds.sets(set_name, query=True) or []
        valid_members = []
        for member in set_members:
            if cmds.objExists(member):
                valid_members.append(member)
        return valid_members
    except:
        return []

def find_constrained_objects_from_relative_space_group(grp):
    constrained_objects = []
    descendants = cmds.listRelatives(grp, allDescendents=True, fullPath=True, type='transform') or []
    
    for desc in descendants:
        short_name = get_short_name(desc)
        if "_esn_ctrl" in short_name and cmds.objectType(desc, isType='transform'):
            constrained = find_constrained_objects(desc)
            if constrained:
                constrained_objects.extend(constrained)
    
    return constrained_objects

def find_spacify_ik_sets_from_selection(sel):
    spacify_sets = set()
    for obj in sel:
        if cmds.objExists(obj):
            try:
                obj_sets = cmds.listSets(object=obj) or []
                for obj_set in obj_sets:
                    if obj_set.startswith("spacify_temp_ik_"):
                        spacify_sets.add(obj_set)
            except:
                pass
    return list(spacify_sets)


def find_camera_space_sets_from_selection(sel):
    camera_space_sets = set()
    for obj in sel:
        if cmds.objExists(obj):
            try:
                obj_sets = cmds.listSets(object=obj) or []
                for obj_set in obj_sets:
                    if obj_set.startswith("spacify_camera_space_"):
                        camera_space_sets.add(obj_set)
            except:
                pass
    return list(camera_space_sets)


def get_objects_from_camera_space_set(set_name):
    """Get locators and original objects from a camera space set"""
    try:
        set_members = cmds.sets(set_name, query=True) or []
        locators = []
        original_objects = []
        groups = []
        
        for member in set_members:
            if cmds.objExists(member):
                short_name = member.split('|')[-1]
                if "_cam_ctrl_grp" in short_name:
                    groups.append(member)
                elif "_cam_ctrl" in short_name:
                    locators.append(member)
                else:
                    original_objects.append(member)
        
        return locators, original_objects, groups
    except:
        return [], [], []

def find_all_spacify_ik_sets():
    all_sets = cmds.ls(type='objectSet')
    spacify_sets = []
    for obj_set in all_sets:
        if obj_set.startswith("spacify_temp_ik_"):
            spacify_sets.append(obj_set)
    return spacify_sets

def get_objects_from_spacify_set(set_name):
    try:
        set_members = cmds.sets(set_name, query=True) or []
        valid_members = []
        for member in set_members:
            if cmds.objExists(member):
                valid_members.append(member)
        return valid_members
    except:
        return []


def get_original_objects_from_spacify_ik_set(set_name):
    """
    Get original objects from a spacify_temp_ik set.
    Original objects are those WITHOUT _spacify_ in their name.
    """
    try:
        set_members = cmds.sets(set_name, query=True) or []
        original_objects = []
        for member in set_members:
            if cmds.objExists(member):
                short_name = member.split('|')[-1]
                # Original objects don't have _spacify_ in their name
                if "_spacify_" not in short_name:
                    original_objects.append(member)
        return original_objects
    except:
        return []

def find_ik_system_group_from_controls(controls):
    ik_groups = set()
    for ctrl in controls:
        if cmds.objExists(ctrl):
            short_name = get_short_name(ctrl)
            base_name = short_name.split('_spacify_loc')[0]
            ik_group_name = base_name + '_spacify_ik_system'
            
            all_groups = cmds.ls(ik_group_name, long=True)
            for grp in all_groups:
                ik_groups.add(grp)
    
    return list(ik_groups)

def find_constrained_objects(control_long_name):
    constrained_objects = set()
    constraint_types = ['parentConstraint', 'pointConstraint', 'orientConstraint', 
                       'scaleConstraint', 'aimConstraint', 'poleVectorConstraint']
    
    connections = cmds.listConnections(control_long_name, destination=True, plugs=False, connections=False) or []
    
    for conn in connections:
        if cmds.nodeType(conn) in constraint_types:
            parent = cmds.listRelatives(conn, parent=True, type='transform', fullPath=True)
            if parent and parent[0] != control_long_name:
                constrained_objects.add(parent[0])
    
    all_constraints = cmds.ls(type=constraint_types, long=True)
    
    for constraint in all_constraints:
        try:
            constraint_type = cmds.nodeType(constraint)
            targets = None
            
            if constraint_type == 'parentConstraint':
                targets = cmds.parentConstraint(constraint, query=True, targetList=True)
            elif constraint_type == 'pointConstraint':
                targets = cmds.pointConstraint(constraint, query=True, targetList=True)
            elif constraint_type == 'orientConstraint':
                targets = cmds.orientConstraint(constraint, query=True, targetList=True)
            elif constraint_type == 'scaleConstraint':
                targets = cmds.scaleConstraint(constraint, query=True, targetList=True)
            elif constraint_type == 'aimConstraint':
                targets = cmds.aimConstraint(constraint, query=True, targetList=True)
            elif constraint_type == 'poleVectorConstraint':
                targets = cmds.poleVectorConstraint(constraint, query=True, targetList=True)
            
            if targets:
                target_long_names = cmds.ls(targets, long=True)
                if control_long_name in target_long_names:
                    parent = cmds.listRelatives(constraint, parent=True, type='transform', fullPath=True)
                    if parent and parent[0] != control_long_name:
                        constrained_objects.add(parent[0])
                        
        except RuntimeError:
            continue
    
    return list(constrained_objects)

def get_connected_esn_ctrl(obj_long_name):
    all_constraints = cmds.listRelatives(obj_long_name, type='constraint', fullPath=True) or []
    
    parent_cons = cmds.listConnections(obj_long_name, type='parentConstraint', source=True, destination=False) or []
    point_cons = cmds.listConnections(obj_long_name, type='pointConstraint', source=True, destination=False) or []
    orient_cons = cmds.listConnections(obj_long_name, type='orientConstraint', source=True, destination=False) or []
    
    for cons in parent_cons:
        cons_long = cmds.ls(cons, long=True)
        if cons_long:
            all_constraints.extend(cons_long)
    
    for cons in point_cons:
        cons_long = cmds.ls(cons, long=True)
        if cons_long:
            all_constraints.extend(cons_long)
    
    for cons in orient_cons:
        cons_long = cmds.ls(cons, long=True)
        if cons_long:
            all_constraints.extend(cons_long)
    
    if not all_constraints:
        return None
    
    for constraint in all_constraints:
        all_connections = cmds.listConnections(constraint, source=True, destination=False) or []
        
        for conn in all_connections:
            conn_long = cmds.ls(conn, long=True)
            if conn_long:
                for conn_path in conn_long:
                    base_name = conn_path.split('|')[-1]
                    if "_esn_ctrl" in base_name and cmds.objectType(conn_path) == 'transform':
                        return conn_path
    
    return None

def get_object_from_ctrl(ctrl_long_name):
    base_name = ctrl_long_name.split('|')[-1]
    if "_esn_fk_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_fk_ctrl")[0]
        return decode_long_name(encoded_obj)
    elif "_esn_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_ctrl")[0]
        return decode_long_name(encoded_obj)
    return None

def get_object_from_ctrl_smart(ctrl_long_name):
    base_name = ctrl_long_name.split('|')[-1]
    
    if "_esn_fk_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_fk_ctrl")[0]
        obj_name = decode_long_name(encoded_obj)
        if cmds.objExists(obj_name):
            return obj_name
    elif "_esn_ctrl" in base_name:
        encoded_obj = base_name.split("_esn_ctrl")[0]
        obj_name = decode_long_name(encoded_obj)
        if cmds.objExists(obj_name):
            return obj_name
    
    constrained = find_constrained_objects(ctrl_long_name)
    if constrained:
        return constrained[0]
    
    return None

def get_aim_related_locators(ctrl_long_name):
    base_name = ctrl_long_name.split('|')[-1]
    related = []
    
    if "_esn_ctrl_Aim" in base_name:
        encoded_obj = base_name.split("_esn_ctrl_Aim")[0]
        side_name = encoded_obj + "_esn_ctrl_Side"
        side_locators = cmds.ls(side_name, long=True)
        if side_locators:
            related.extend(side_locators)
    
    if "_esn_ctrl_Side" in base_name:
        encoded_obj = base_name.split("_esn_ctrl_Side")[0]
        aim_name = encoded_obj + "_esn_ctrl_Aim"
        aim_locators = cmds.ls(aim_name, long=True)
        if aim_locators:
            related.extend(aim_locators)
    
    return related

def find_esn_grp_from_selection(sel):
    grp_list = []
    for s in sel:
        current = s
        while current:
            short_name = get_short_name(current)
            if short_name.startswith("esn_GRP"):
                if current not in grp_list:
                    grp_list.append(current)
                break
            parent = cmds.listRelatives(current, parent=True, fullPath=True)
            if parent:
                current = parent[0]
            else:
                break
    return grp_list

def get_all_ctrls_in_grp(grp_node):
    all_ctrls = []
    descendants = cmds.listRelatives(grp_node, allDescendents=True, fullPath=True, type='transform') or []
    
    for desc in descendants:
        short_name = get_short_name(desc)
        if "_esn_ctrl" in short_name:
            all_ctrls.append(desc)
    
    return all_ctrls

def clean_empty_spacify_group():
    if cmds.objExists("SPACIFY"):
        children = cmds.listRelatives("SPACIFY", children=True, fullPath=True)
        if not children:
            cmds.delete("SPACIFY")

def remove_objects_from_animation_layers(objects):
    anim_layers = cmds.ls(type='animLayer')
    if not anim_layers:
        return
    
    for obj in objects:
        if not cmds.objExists(obj):
            continue
        for layer in anim_layers:
            try:
                if cmds.animLayer(layer, query=True, exists=True):
                    affected_objs = cmds.animLayer(layer, query=True, affectedLayers=True) or []
                    if obj in affected_objs:
                        cmds.animLayer(layer, edit=True, removeObject=obj)
            except:
                pass

def remove_parent_groups(locators):
    groups_to_remove = []
    for loc in locators:
        if cmds.objExists(loc):
            parent = cmds.listRelatives(loc, parent=True, fullPath=True)
            if parent:
                parent_short = get_short_name(parent[0])
                if "_esn_ctrl_grp" in parent_short:
                    if parent[0] not in groups_to_remove:
                        groups_to_remove.append(parent[0])
    return groups_to_remove

def clean_ik_setup_single_frame(spacify_sets):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for spacify_set in spacify_sets:
        # Get original objects (the ones we need to bake)
        original_objects = get_original_objects_from_spacify_ik_set(spacify_set)
        all_objects_to_bake.extend(original_objects)
        
        # Get all members to find ik_system groups
        all_members = get_objects_from_spacify_set(spacify_set)
        ik_groups = find_ik_system_group_from_controls(all_members)
        all_groups_to_delete.extend(ik_groups)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            min_time = cmds.playbackOptions(q=True, ast=True)
            max_time = cmds.playbackOptions(q=True, aet=True)
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(min_time, max_time))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for spacify_set in spacify_sets:
                if cmds.objExists(spacify_set):
                    cmds.delete(spacify_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)

def clean_ik_setup_frame_range(spacify_sets, StartRange, EndRange):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for spacify_set in spacify_sets:
        # Get original objects (the ones we need to bake)
        original_objects = get_original_objects_from_spacify_ik_set(spacify_set)
        all_objects_to_bake.extend(original_objects)
        
        # Get all members to find ik_system groups
        all_members = get_objects_from_spacify_set(spacify_set)
        ik_groups = find_ik_system_group_from_controls(all_members)
        all_groups_to_delete.extend(ik_groups)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(StartRange, EndRange))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for spacify_set in spacify_sets:
                if cmds.objExists(spacify_set):
                    cmds.delete(spacify_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)

def clean_relative_space_single_frame(relative_space_sets):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for rel_set in relative_space_sets:
        groups = get_objects_from_relative_space_set(rel_set)
        
        for grp in groups:
            constrained = find_constrained_objects_from_relative_space_group(grp)
            if constrained:
                all_objects_to_bake.extend(constrained)
            all_groups_to_delete.append(grp)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            min_time = cmds.playbackOptions(q=True, ast=True)
            max_time = cmds.playbackOptions(q=True, aet=True)
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(min_time, max_time))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for rel_set in relative_space_sets:
                if cmds.objExists(rel_set):
                    cmds.delete(rel_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)

def clean_relative_space_frame_range(relative_space_sets, StartRange, EndRange):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for rel_set in relative_space_sets:
        groups = get_objects_from_relative_space_set(rel_set)
        
        for grp in groups:
            constrained = find_constrained_objects_from_relative_space_group(grp)
            if constrained:
                all_objects_to_bake.extend(constrained)
            all_groups_to_delete.append(grp)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(StartRange, EndRange))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for rel_set in relative_space_sets:
                if cmds.objExists(rel_set):
                    cmds.delete(rel_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)


def get_original_objects_from_camera_space_set(set_name):
    """
    Get original objects from a spacify_camera_space set.
    Original objects are those WITHOUT _cam_ctrl in their name.
    """
    try:
        set_members = cmds.sets(set_name, query=True) or []
        original_objects = []
        for member in set_members:
            if cmds.objExists(member):
                short_name = member.split('|')[-1]
                # Original objects don't have _cam_ctrl in their name
                if "_cam_ctrl" not in short_name:
                    original_objects.append(member)
        return original_objects
    except:
        return []


def get_camera_space_groups_to_delete(set_name):
    """Get all camera space groups and locators to delete"""
    try:
        set_members = cmds.sets(set_name, query=True) or []
        groups_and_locators = []
        for member in set_members:
            if cmds.objExists(member):
                short_name = member.split('|')[-1]
                if "_cam_ctrl_grp" in short_name:
                    groups_and_locators.append(member)
        return groups_and_locators
    except:
        return []


def clean_camera_space_single_frame(camera_space_sets):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for cam_set in camera_space_sets:
        # Get original objects (the ones we need to bake)
        original_objects = get_original_objects_from_camera_space_set(cam_set)
        all_objects_to_bake.extend(original_objects)
        
        # Get groups to delete
        groups = get_camera_space_groups_to_delete(cam_set)
        all_groups_to_delete.extend(groups)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            min_time = cmds.playbackOptions(q=True, ast=True)
            max_time = cmds.playbackOptions(q=True, aet=True)
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(min_time, max_time))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for cam_set in camera_space_sets:
                if cmds.objExists(cam_set):
                    cmds.delete(cam_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)


def clean_camera_space_frame_range(camera_space_sets, StartRange, EndRange):
    ct = cmds.currentTime(q=True)
    all_objects_to_bake = []
    all_groups_to_delete = []
    
    for cam_set in camera_space_sets:
        # Get original objects (the ones we need to bake)
        original_objects = get_original_objects_from_camera_space_set(cam_set)
        all_objects_to_bake.extend(original_objects)
        
        # Get groups to delete
        groups = get_camera_space_groups_to_delete(cam_set)
        all_groups_to_delete.extend(groups)
    
    if all_objects_to_bake:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            cmds.bakeResults(all_objects_to_bake, sm=True, pok=True, t=(StartRange, EndRange))
            cmds.currentTime(ct)
            
            for grp in all_groups_to_delete:
                if cmds.objExists(grp):
                    cmds.delete(grp)
            
            for cam_set in camera_space_sets:
                if cmds.objExists(cam_set):
                    cmds.delete(cam_set)
            
            existing_objs = [obj for obj in all_objects_to_bake if cmds.objExists(obj)]
            if existing_objs:
                cmds.select(existing_objs, replace=True)
            
            remove_objects_from_animation_layers(all_objects_to_bake)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)


def is_temp_control_object(obj):
    """Check if an object is actually a temp control created by our scripts"""
    if not cmds.objExists(obj):
        return False
    
    base_name = obj.split('|')[-1]
    
    # Check for temp control naming patterns
    if "_esn_ctrl" in base_name or "_esn_fk_ctrl" in base_name:
        return True
    
    if "_spacify_loc" in base_name:
        return True
    
    if "_cam_ctrl" in base_name:
        return True
    
    if base_name.endswith("_esn_ctrl_grp"):
        return True
    
    if base_name.endswith("_spacify_loc_grp"):
        return True
    
    if base_name.endswith("_cam_ctrl_grp"):
        return True
    
    # Check if object is in any temp control sets
    try:
        obj_sets = cmds.listSets(object=obj) or []
        for obj_set in obj_sets:
            if obj_set.startswith("spacify_temp_ik_") or obj_set.startswith("spacify_camera_space_") or obj_set == "relative_space_01" or obj_set == "esn_ctrls_set" or obj_set == "esn_fk_set":
                return True
    except:
        pass
    
    # Check if it's a parent of a temp control
    if base_name.endswith("_esn_ctrl_grp") or base_name.endswith("_spacify_loc_grp") or base_name.endswith("_cam_ctrl_grp"):
        return True
    
    return False

def clean_single_frame_for_selection(sel):
    ct = cmds.currentTime(q=True)
    
    # Filter selection to only include temp controls
    valid_temp_ctrls = [s for s in sel if is_temp_control_object(s)]
    
    if not valid_temp_ctrls:
        return []
    
    objList = []
    locList = []
    grp_nodes_to_delete = []
    
    esn_grps = find_esn_grp_from_selection(valid_temp_ctrls)
    
    if esn_grps:
        for grp in esn_grps:
            all_ctrls = get_all_ctrls_in_grp(grp)
            
            for ctrl in all_ctrls:
                constrained = find_constrained_objects(ctrl)
                if constrained:
                    for obj in constrained:
                        if obj not in objList:
                            objList.append(obj)
                    locList.append(ctrl)
            
            grp_nodes_to_delete.append(grp)
        
        if objList:
            original_eval_mode = set_evaluation_mode("off")
            cmds.refresh(suspend=True)
            
            try:
                min_time = cmds.playbackOptions(q=True, ast=True)
                max_time = cmds.playbackOptions(q=True, aet=True)
                cmds.bakeResults(objList, sm=True, pok=True, t=(min_time, max_time))
                cmds.currentTime(ct)
                
                for grp in grp_nodes_to_delete:
                    if cmds.objExists(grp):
                        cmds.delete(grp)
                
                remove_objects_from_animation_layers(objList)
            finally:
                cmds.refresh(suspend=False)
                restore_evaluation_mode(original_eval_mode)
            return objList
    
    aimLocatorsList = []
    for s in valid_temp_ctrls:
        related = get_aim_related_locators(s)
        aimLocatorsList.extend(related)
    
    objList = []
    locList = []
    for s in valid_temp_ctrls:
        base_name = s.split('|')[-1]
        if "_esn_ctrl" in base_name or "_spacify_loc" in base_name:
            obj_long = get_object_from_ctrl_smart(s)
            if obj_long and cmds.objExists(obj_long):
                objList.append(obj_long)
                locList.append(s)
        else:
            connected_ctrl = get_connected_esn_ctrl(s)
            if connected_ctrl:
                objList.append(s)
                locList.append(connected_ctrl)
                related = get_aim_related_locators(connected_ctrl)
                aimLocatorsList.extend(related)
            else:
                constrained = find_constrained_objects(s)
                if constrained:
                    for const_obj in constrained:
                        if const_obj not in objList:
                            objList.append(const_obj)
                            locList.append(s)
    
    if objList and locList:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            min_time = cmds.playbackOptions(q=True, ast=True)
            max_time = cmds.playbackOptions(q=True, aet=True)
            cmds.bakeResults(objList, sm=True, pok=True, t=(min_time, max_time))
            cmds.currentTime(ct)
            
            groups_to_remove = remove_parent_groups(locList)
            
            cmds.delete(locList)
            try:
                cmds.filterCurve()
            except:
                pass
            try:
                cmds.selectKey(cl=True)
            except:
                pass
            
            for group in groups_to_remove:
                if cmds.objExists(group):
                    cmds.delete(group)
            
            if aimLocatorsList:
                existing_aim_locs = [loc for loc in aimLocatorsList if cmds.objExists(loc)]
                if existing_aim_locs:
                    cmds.delete(existing_aim_locs)
            
            remove_objects_from_animation_layers(objList)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)
    
    return objList

def clean_frame_range_for_selection(sel, StartRange, EndRange):
    ct = cmds.currentTime(q=True)
    
    # Filter selection to only include temp controls
    valid_temp_ctrls = [s for s in sel if is_temp_control_object(s)]
    
    if not valid_temp_ctrls:
        return []
    
    objList = []
    locList = []
    grp_nodes_to_delete = []
    
    esn_grps = find_esn_grp_from_selection(valid_temp_ctrls)
    
    if esn_grps:
        for grp in esn_grps:
            all_ctrls = get_all_ctrls_in_grp(grp)
            
            for ctrl in all_ctrls:
                constrained = find_constrained_objects(ctrl)
                if constrained:
                    for obj in constrained:
                        if obj not in objList:
                            objList.append(obj)
                    locList.append(ctrl)
            
            grp_nodes_to_delete.append(grp)
        
        if objList:
            original_eval_mode = set_evaluation_mode("off")
            cmds.refresh(suspend=True)
            
            try:
                cmds.bakeResults(objList, sm=True, pok=True, t=(StartRange, EndRange))
                cmds.currentTime(ct)
                
                for grp in grp_nodes_to_delete:
                    if cmds.objExists(grp):
                        cmds.delete(grp)
                
                remove_objects_from_animation_layers(objList)
            finally:
                cmds.refresh(suspend=False)
                restore_evaluation_mode(original_eval_mode)
            return objList
    
    aimLocatorsList = []
    for s in valid_temp_ctrls:
        related = get_aim_related_locators(s)
        aimLocatorsList.extend(related)
    
    objList = []
    locList = []
    for s in valid_temp_ctrls:
        base_name = s.split('|')[-1]
        if "_esn_ctrl" in base_name or "_spacify_loc" in base_name:
            obj_long = get_object_from_ctrl_smart(s)
            if obj_long and cmds.objExists(obj_long):
                objList.append(obj_long)
                locList.append(s)
        else:
            connected_ctrl = get_connected_esn_ctrl(s)
            if connected_ctrl:
                objList.append(s)
                locList.append(connected_ctrl)
                related = get_aim_related_locators(connected_ctrl)
                aimLocatorsList.extend(related)
            else:
                constrained = find_constrained_objects(s)
                if constrained:
                    for const_obj in constrained:
                        if const_obj not in objList:
                            objList.append(const_obj)
                            locList.append(s)
    
    if objList and locList:
        original_eval_mode = set_evaluation_mode("off")
        cmds.refresh(suspend=True)
        
        try:
            cmds.bakeResults(objList, sm=True, pok=True, t=(StartRange, EndRange))
            cmds.currentTime(ct)
            
            groups_to_remove = remove_parent_groups(locList)
            
            cmds.delete(locList)
            try:
                cmds.filterCurve()
            except:
                pass
            try:
                cmds.selectKey(cl=True)
            except:
                pass
            
            for group in groups_to_remove:
                if cmds.objExists(group):
                    cmds.delete(group)
            
            if aimLocatorsList:
                existing_aim_locs = [loc for loc in aimLocatorsList if cmds.objExists(loc)]
                if existing_aim_locs:
                    cmds.delete(existing_aim_locs)
            
            remove_objects_from_animation_layers(objList)
        finally:
            cmds.refresh(suspend=False)
            restore_evaluation_mode(original_eval_mode)
    
    return objList

def clean_fk_chain_single_frame(fk_ctrls):
    ct = cmds.currentTime(q=True)
    objList = []
    fk_hierarchy_roots = []
    
    for fk_ctrl in fk_ctrls:
        base_name = fk_ctrl.split('|')[-1]
        if "_esn_fk_ctrl" in base_name:
            parent = cmds.listRelatives(fk_ctrl, parent=True, fullPath=True)
            if parent:
                parent_base = parent[0].split('|')[-1]
                if "_esn_fk_ctrl" not in parent_base:
                    if fk_ctrl not in fk_hierarchy_roots:
                        fk_hierarchy_roots.append(fk_ctrl)
            else:
                if fk_ctrl not in fk_hierarchy_roots:
                    fk_hierarchy_roots.append(fk_ctrl)
    
    for root_ctrl in fk_hierarchy_roots:
        descendants = cmds.listRelatives(root_ctrl, allDescendents=True, fullPath=True, type='transform') or []
        all_fk_ctrls = [root_ctrl] + [d for d in descendants if "_esn_fk_ctrl" in d.split('|')[-1]]
        
        for ctrl in all_fk_ctrls:
            constrained = find_constrained_objects(ctrl)
            if constrained:
                for obj in constrained:
                    if obj not in objList:
                        objList.append(obj)
        
        if objList:
            original_eval_mode = set_evaluation_mode("off")
            try:
                cmds.refresh(suspend=True)
                min_time = cmds.playbackOptions(q=True, ast=True)
                max_time = cmds.playbackOptions(q=True, aet=True)
                cmds.bakeResults(objList, sm=True, pok=True, t=(min_time, max_time))
                cmds.currentTime(ct)
                
                cmds.delete(root_ctrl)
                
                if cmds.objExists("esn_fk_set"):
                    try:
                        cmds.delete("esn_fk_set")
                    except:
                        pass
                
                remove_objects_from_animation_layers(objList)
            finally:
                cmds.refresh(suspend=False)
                restore_evaluation_mode(original_eval_mode)
    
    return objList

def clean_fk_chain_frame_range(fk_ctrls, StartRange, EndRange):
    ct = cmds.currentTime(q=True)
    objList = []
    fk_hierarchy_roots = []
    
    for fk_ctrl in fk_ctrls:
        base_name = fk_ctrl.split('|')[-1]
        if "_esn_fk_ctrl" in base_name:
            parent = cmds.listRelatives(fk_ctrl, parent=True, fullPath=True)
            if parent:
                parent_base = parent[0].split('|')[-1]
                if "_esn_fk_ctrl" not in parent_base:
                    if fk_ctrl not in fk_hierarchy_roots:
                        fk_hierarchy_roots.append(fk_ctrl)
            else:
                if fk_ctrl not in fk_hierarchy_roots:
                    fk_hierarchy_roots.append(fk_ctrl)
    
    for root_ctrl in fk_hierarchy_roots:
        descendants = cmds.listRelatives(root_ctrl, allDescendents=True, fullPath=True, type='transform') or []
        all_fk_ctrls = [root_ctrl] + [d for d in descendants if "_esn_fk_ctrl" in d.split('|')[-1]]
        
        for ctrl in all_fk_ctrls:
            constrained = find_constrained_objects(ctrl)
            if constrained:
                for obj in constrained:
                    if obj not in objList:
                        objList.append(obj)
        
        if objList:
            original_eval_mode = set_evaluation_mode("off")
            try:
                cmds.refresh(suspend=True)
                cmds.bakeResults(objList, sm=True, pok=True, t=(StartRange, EndRange))
                cmds.currentTime(ct)
                
                cmds.delete(root_ctrl)
                
                if cmds.objExists("esn_fk_set"):
                    try:
                        cmds.delete("esn_fk_set")
                    except:
                        pass
                
                remove_objects_from_animation_layers(objList)
            finally:
                cmds.refresh(suspend=False)
                restore_evaluation_mode(original_eval_mode)
    
    return objList

def clean_and_bake():
    sel = cmds.ls(sl=True, long=True)
    
    if len(sel) == 0:
        cmds.inViewMessage(amg='Please select a temp control to bake.', pos='midCenter', fade=True)
        return
    
    ik_objs, relative_objs, fk_objs, camera_space_objs, other_objs = partition_selection_by_sets(sel)
    
    playBackSlider = mel.eval('$animBot_playBackSliderPython=$gPlayBackSlider')
    timeRange = cmds.timeControl(playBackSlider, query=True, rangeArray=True)
    StartRange = int(timeRange[0])
    EndRange = int(timeRange[1] - 1)
    
    all_baked_objects = []
    
    if ik_objs:
        spacify_sets = find_spacify_ik_sets_from_selection(ik_objs)
        if spacify_sets:
            ik_baked_objs = []
            for spacify_set in spacify_sets:
                # Get original objects directly from the set
                original_objects = get_original_objects_from_spacify_ik_set(spacify_set)
                ik_baked_objs.extend(original_objects)
            
            if (EndRange - StartRange) == 0:
                clean_ik_setup_single_frame(spacify_sets)
            else:
                clean_ik_setup_frame_range(spacify_sets, StartRange, EndRange)
            
            all_baked_objects.extend(ik_baked_objs)
    
    if relative_objs:
        relative_space_sets = find_relative_space_sets_from_selection(relative_objs)
        if relative_space_sets:
            rel_baked_objs = []
            for rel_set in relative_space_sets:
                groups = get_objects_from_relative_space_set(rel_set)
                for grp in groups:
                    constrained = find_constrained_objects_from_relative_space_group(grp)
                    if constrained:
                        rel_baked_objs.extend(constrained)
            
            if (EndRange - StartRange) == 0:
                clean_relative_space_single_frame(relative_space_sets)
            else:
                clean_relative_space_frame_range(relative_space_sets, StartRange, EndRange)
            
            all_baked_objects.extend(rel_baked_objs)
    
    if fk_objs:
        fk_baked_objs = []
        for fk_ctrl in fk_objs:
            constrained = find_constrained_objects(fk_ctrl)
            if constrained:
                fk_baked_objs.extend(constrained)
        
        if (EndRange - StartRange) == 0:
            fk_result = clean_fk_chain_single_frame(fk_objs)
            if fk_result:
                all_baked_objects.extend(fk_result)
        else:
            fk_result = clean_fk_chain_frame_range(fk_objs, StartRange, EndRange)
            if fk_result:
                all_baked_objects.extend(fk_result)
    
    if camera_space_objs:
        camera_space_sets = find_camera_space_sets_from_selection(camera_space_objs)
        if camera_space_sets:
            cam_baked_objs = []
            for cam_set in camera_space_sets:
                original_objects = get_original_objects_from_camera_space_set(cam_set)
                cam_baked_objs.extend(original_objects)
            
            if (EndRange - StartRange) == 0:
                clean_camera_space_single_frame(camera_space_sets)
            else:
                clean_camera_space_frame_range(camera_space_sets, StartRange, EndRange)
            
            all_baked_objects.extend(cam_baked_objs)
    
    if other_objs:
        if (EndRange - StartRange) == 0:
            other_baked = clean_single_frame_for_selection(other_objs)
            if other_baked:
                all_baked_objects.extend(other_baked)
        else:
            other_baked = clean_frame_range_for_selection(other_objs, StartRange, EndRange)
            if other_baked:
                all_baked_objects.extend(other_baked)
    
    clean_empty_spacify_group()
    
    if all_baked_objects:
        existing_objs = [obj for obj in all_baked_objects if cmds.objExists(obj)]
        if existing_objs:
            cmds.select(existing_objs, replace=True)

