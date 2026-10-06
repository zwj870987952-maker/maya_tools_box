import maya.cmds as cmds

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


def smart_bake(objects, start_time=None, end_time=None, attributes=None, source_objects=None):
    """
    Bake animation on objects.
    If source_objects provided with Only Keys mode:
    - Constraint already exists with maintain offset
    - We just need to go to each key time and set a key on the constrained object
    - Use dgeval to force constraint evaluation without unsuspending refresh
    """
    only_keys = SPACIFY_STATE.get("only_keys", False)
    
    if not objects:
        return
    
    if isinstance(objects, str):
        objects = [objects]
    
    if not only_keys:
        # Normal bake - every frame
        if start_time is None:
            start_time = cmds.playbackOptions(q=True, ast=True)
        if end_time is None:
            end_time = cmds.playbackOptions(q=True, aet=True)
        
        if attributes:
            cmds.bakeResults(objects, sm=True, pok=True, t=(start_time, end_time), at=attributes)
        else:
            cmds.bakeResults(objects, sm=True, t=(start_time, end_time))
    else:
        # Only Keys mode - get keyframe times from source objects
        key_source = source_objects if source_objects else objects
        if isinstance(key_source, str):
            key_source = [key_source]
        
        key_times = get_all_keyframe_times(key_source)
        
        if not key_times:
            if start_time is None:
                start_time = cmds.playbackOptions(q=True, ast=True)
            if end_time is None:
                end_time = cmds.playbackOptions(q=True, aet=True)
            key_times = [start_time, end_time]
        
        current_time = cmds.currentTime(q=True)
        
        # Go to each key time and set a key on the objects
        # Use dgeval to force constraint evaluation without unsuspending refresh
        for t in key_times:
            cmds.currentTime(t, update=True)
            for obj in objects:
                if cmds.objExists(obj):
                    # Force constraint evaluation using dgeval
                    cmds.dgeval(obj + '.translate', obj + '.rotate')
                    # Make sure blendParent is on if it exists
                    if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                        try:
                            cmds.setAttr(obj + '.blendParent1', 1)
                        except:
                            pass
                    # Set keyframe - this captures the constraint-driven position
                    cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
        
        cmds.currentTime(current_time)


def add_to_esn_ctrls_set(items):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for item in items:
        if not cmds.sets(item, isMember=set_name):
            cmds.sets(item, add=set_name)


def encode_long_name(long_name):
    return long_name.replace('|', '_PIPE_')


def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')


def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group


def get_bounding_box_size(obj):
    try:
        bbox = cmds.exactWorldBoundingBox(obj)
        width = bbox[3] - bbox[0]
        height = bbox[4] - bbox[1]
        depth = bbox[5] - bbox[2]
        max_size = max(width, height, depth)
        return max_size if max_size > 0 else 1.0
    except:
        return 1.0


def smartConstraint(ctrl=None, object=None):
    if ctrl is None or object is None:
        return
        
    transAttr = None
    rotAttr = None
    scaleAttr = None
    translate = True
    rotate = True
    scale = False
    maintainOffset = True

    if translate:
        transAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='translate*')     
    if rotate:
        rotAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='rotate*')      
    if scale:
        scaleAttr = cmds.listAttr(object, keyable=True, unlocked=True, string='scale*')     

    rotSkip = []
    transSkip = []

    for axis in ['x','y','z']:
        if transAttr and not 'translate'+axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate'+axis.upper() in rotAttr:
            rotSkip.append(axis)

    if not transSkip:
        transSkip = 'none'
    if not rotSkip:
        rotSkip = 'none'

    constraints = []
    if rotAttr and transAttr and rotSkip == 'none' and transSkip == 'none':
        constraints.append(cmds.parentConstraint(ctrl, object, maintainOffset=maintainOffset))
    else:
        if transAttr:
            constraints.append(cmds.pointConstraint(ctrl, object, skip=transSkip, maintainOffset=maintainOffset))
        if rotAttr:
            constraints.append(cmds.orientConstraint(ctrl, object, skip=rotSkip, maintainOffset=maintainOffset))


def create_locator_with_settings(name, bbox_size=1.0):
    loc = cmds.spaceLocator(n=name)[0]
    cmds.setAttr(loc + ".overrideEnabled", 1)
    cmds.setAttr(loc + ".overrideColor", 18)   
    cmds.setAttr(loc + '.useOutlinerColor', True)
    cmds.setAttr(loc + ".outlinerColor", .8, .3, .5)
    
    locator_scale = bbox_size * 0.5
    if locator_scale <= 0.0001 or locator_scale > 100000.0:
        locator_scale = 1.0
    cmds.setAttr(loc + ".localScaleX", locator_scale)
    cmds.setAttr(loc + ".localScaleY", locator_scale)
    cmds.setAttr(loc + ".localScaleZ", locator_scale)
    
    return loc


def get_active_model_panel():
    panel = cmds.getPanel(withFocus=True)
    if panel and "modelPanel" in panel:
        return panel
    all_panels = cmds.getPanel(type="modelPanel")
    if all_panels:
        return all_panels[0]
    return None


def create_pivot_locators():
    sel = cmds.ls(sl=True, long=True)
    
    if not sel:
        return create_single_locator()
    
    # Use all selected objects - don't filter out locators
    return create_locators_for_selection(sel)


def create_single_locator():
    spacify_group = get_or_create_spacify_group()
    loc_name = "esn_ctrl_1"
    loc = create_locator_with_settings(loc_name)
    cmds.parent(loc, spacify_group)
    cmds.select(loc)
    # Return empty data since there's no object to constrain
    return [], [], {}, []


def create_locators_for_selection(sel):
    spacify_group = get_or_create_spacify_group()
    locators = []
    object_map = {}
    original_selection = list(sel)
    
    for s in sel:
        encoded_name = encode_long_name(s)
        loc_name = encoded_name + "_esn_ctrl"
        
        bbox_size = get_bounding_box_size(s)
        loc = create_locator_with_settings(loc_name, bbox_size)
        locators.append(loc)
        
        cmds.matchTransform(loc, s, pos=True, rot=True)
        cmds.parent(loc, spacify_group)
        
        object_map[loc] = s
        
    cmds.select(locators)
    return locators, locators, object_map, original_selection


def bake_and_constrain(locators, groups, object_map, original_selection, current_time):
    if not locators:
        return
        
    cmds.currentTime(current_time)
    con_list = []
    min_time = cmds.playbackOptions(q=True, ast=True)
    max_time = cmds.playbackOptions(q=True, aet=True)
    
    # Create constraints from original objects to locators (with maintain offset)
    for loc in locators:
        obj = object_map.get(loc)
        if obj and cmds.objExists(obj):
            con = cmds.parentConstraint(obj, loc, mo=True)[0]
            con_list.append(con)
    
    refresh_suspended = False
    eval_mode_changed = False
    original_eval_mode = None
    
    try:
        cmds.refresh(suspend=True)
        refresh_suspended = True
        original_eval_mode = cmds.evaluationManager(query=True, mode=True)
        cmds.evaluationManager(mode="off")
        eval_mode_changed = True
        
        if locators:
            # Get source objects for keyframe timing
            source_objs = [object_map.get(loc) for loc in locators if object_map.get(loc)]
            # Bake - goes to each key time and sets key on constrained locators
            smart_bake(locators, min_time, max_time, source_objects=source_objs)
        
        # Delete the constraints after baking
        if con_list:
            cmds.delete(con_list)
        
        add_to_esn_ctrls_set(groups)
        
    finally:
        if refresh_suspended:
            try:
                cmds.refresh(suspend=False)
            except:
                pass
        
        if eval_mode_changed and original_eval_mode:
            try:
                cmds.evaluationManager(mode=original_eval_mode[0])
            except:
                pass
    
    # Now constrain objects back to locators
    for loc in locators:
        obj = object_map.get(loc)
        if obj and cmds.objExists(obj):
            smartConstraint(loc, obj)
    
    cmds.filterCurve(locators)
    cmds.selectKey(locators, cl=True)
    
    cmds.select(locators)


# Global storage
GLOBAL_LOCATORS = []
GLOBAL_GROUPS = []
GLOBAL_OBJECT_MAP = {}
GLOBAL_ORIGINAL_SELECTION = []
GLOBAL_CURRENT_TIME = 0


def bake_callback():
    global GLOBAL_LOCATORS, GLOBAL_GROUPS, GLOBAL_OBJECT_MAP, GLOBAL_ORIGINAL_SELECTION, GLOBAL_CURRENT_TIME
    # Only bake if we have both locators and objects to constrain
    if GLOBAL_LOCATORS and GLOBAL_OBJECT_MAP:
        bake_and_constrain(GLOBAL_LOCATORS, GLOBAL_GROUPS, GLOBAL_OBJECT_MAP, GLOBAL_ORIGINAL_SELECTION, GLOBAL_CURRENT_TIME)
        if GLOBAL_LOCATORS:
            cmds.select(GLOBAL_LOCATORS)


def btl_main():
    """Main function called by UI"""
    global GLOBAL_LOCATORS, GLOBAL_GROUPS, GLOBAL_OBJECT_MAP, GLOBAL_ORIGINAL_SELECTION, GLOBAL_CURRENT_TIME
    
    GLOBAL_CURRENT_TIME = cmds.currentTime(q=True)
    GLOBAL_LOCATORS, GLOBAL_GROUPS, GLOBAL_OBJECT_MAP, GLOBAL_ORIGINAL_SELECTION = create_pivot_locators()
    
    panel = get_active_model_panel()
    if panel:
        cmds.modelEditor(panel, e=True, locators=True)
    
    # Only register callback if we have locators AND objects to constrain
    if GLOBAL_LOCATORS and GLOBAL_OBJECT_MAP:
        cmds.scriptJob(runOnce=True, killWithScene=True, event=["SelectionChanged", bake_callback])