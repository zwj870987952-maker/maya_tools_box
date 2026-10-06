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


def smart_bake(objects, start_time=None, end_time=None, attributes=None, source_objects=None):
    """
    Bake animation on objects.
    If source_objects provided with Only Keys mode:
    - Constraints should already exist with maintain offset
    - We just go to each key time and set a key on the constrained objects
    """
    only_keys = SPACIFY_STATE.get("only_keys", False)
    
    if not objects:
        return
    
    if isinstance(objects, str):
        objects = [objects]
    
    if not only_keys:
        if start_time is None:
            start_time = cmds.playbackOptions(q=True, ast=True)
        if end_time is None:
            end_time = cmds.playbackOptions(q=True, aet=True)
        
        if attributes:
            cmds.bakeResults(objects, sm=True, pok=True, t=(start_time, end_time), at=attributes)
        else:
            cmds.bakeResults(objects, sm=True, t=(start_time, end_time), pok=True)
    else:
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
        
        cmds.refresh(suspend=False)
        
        try:
            for t in key_times:
                cmds.currentTime(t, update=True)
                cmds.refresh(force=True)
                for obj in objects:
                    if cmds.objExists(obj):
                        if cmds.attributeQuery('blendParent1', node=obj, exists=True):
                            try:
                                cmds.setAttr(obj + '.blendParent1', 1)
                            except:
                                pass
                        cmds.setKeyframe(obj, at=['tx','ty','tz','rx','ry','rz'], t=t)
        finally:
            cmds.refresh(suspend=True)
            cmds.currentTime(current_time)


def add_to_esn_ctrls_set(locators):
    set_name = "esn_ctrls_set"
    if not cmds.objExists(set_name):
        cmds.sets(name=set_name, empty=True)
    for loc in locators:
        if not cmds.sets(loc, isMember=set_name):
            cmds.sets(loc, add=set_name)


def get_next_camera_space_set_name():
    base_name = "spacify_camera_space"
    counter = 1
    while True:
        set_name = "{0}_{1:02d}".format(base_name, counter)
        if not cmds.objExists(set_name):
            return set_name
        counter += 1

def encode_long_name(long_name):
    return long_name.replace('|', '_PIPE_')

def decode_long_name(encoded_name):
    return encoded_name.replace('_PIPE_', '|')

def get_or_create_network_node():
    network_node = "cameraSpaceCtrls_network"
    if not cmds.objExists(network_node):
        network_node = cmds.createNode("network", name=network_node)
        if not cmds.attributeQuery("savedCamera", node=network_node, exists=True):
            cmds.addAttr(network_node, longName="savedCamera", dataType="string")
    return network_node

def save_camera_to_network(camera):
    network_node = get_or_create_network_node()
    cmds.setAttr(network_node + ".savedCamera", camera, type="string")

def load_camera_from_network():
    network_node = "cameraSpaceCtrls_network"
    if cmds.objExists(network_node):
        if cmds.attributeQuery("savedCamera", node=network_node, exists=True):
            camera = cmds.getAttr(network_node + ".savedCamera")
            if camera and cmds.objExists(camera):
                return camera
    return None

def get_bounding_box_size(obj):
    bbox = cmds.exactWorldBoundingBox(obj)
    width = bbox[3] - bbox[0]
    height = bbox[4] - bbox[1]
    depth = bbox[5] - bbox[2]
    raw_size = max(width, height, depth)
    
    scale = cmds.xform(obj, query=True, worldSpace=True, scale=True)
    avg_scale = (abs(scale[0]) + abs(scale[1]) + abs(scale[2])) / 3.0
    if avg_scale > 0.0001:
        return raw_size / avg_scale
    return raw_size

def set_locator_size(locator, source_object):
    bbox_size = get_bounding_box_size(source_object) * 0.6
    locator_shape = cmds.listRelatives(locator, shapes=True)[0]
    cmds.setAttr(locator_shape + ".localScaleX", bbox_size)
    cmds.setAttr(locator_shape + ".localScaleY", bbox_size)
    cmds.setAttr(locator_shape + ".localScaleZ", bbox_size)

def get_or_create_spacify_group():
    spacify_group = "SPACIFY"
    if not cmds.objExists(spacify_group):
        spacify_group = cmds.group(empty=True, name=spacify_group)
        cmds.setAttr(spacify_group + '.useOutlinerColor', True)
        cmds.setAttr(spacify_group + ".outlinerColor", 1, 0.65, 0.3)
    return spacify_group

def get_or_create_camera_space_group():
    spacify_group = get_or_create_spacify_group()
    camera_space_group = "CAMERA_SPACE"
    if not cmds.objExists(camera_space_group):
        camera_space_group = cmds.group(empty=True, name=camera_space_group)
        cmds.setAttr(camera_space_group + '.useOutlinerColor', True)
        cmds.setAttr(camera_space_group + ".outlinerColor", 0.3, 0.65, 1)
        cmds.parent(camera_space_group, spacify_group)
    return camera_space_group

def smartConstraint(ctrl=None, object=None):
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

    for axis in ['x', 'y', 'z']:
        if transAttr and not 'translate' + axis.upper() in transAttr:
            transSkip.append(axis)
        if rotAttr and not 'rotate' + axis.upper() in rotAttr:
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

def create_camera_space_ctrls(camera):
    if not camera or not cmds.objExists(camera):
        cmds.warning("Please assign a valid camera first.")
        return

    sel = cmds.ls(sl=True, long=True)

    if len(sel) < 1:
        cmds.warning("Please select at least one object to create camera space controls.")
        return

    # Check if selected objects include the camera
    camera_short = camera.split('|')[-1]
    for s in sel:
        s_short = s.split('|')[-1]
        if s == camera or s_short == camera_short:
            cmds.confirmDialog(
                title='Invalid Selection',
                message='Cannot create camera space controls on the camera itself.\nPlease select different objects.',
                button=['OK'],
                defaultButton='OK',
                backgroundColor=[0.15, 0.15, 0.15]
            )
            return

    locList = []
    conList = []
    grpList = []
    objectMap = {}
    camera_space_group = None
    camera_space_set = None
    original_eval_mode = "parallel"
    
    try:
        original_eval_mode = cmds.evaluationManager(query=True, mode=True)[0]
        cmds.evaluationManager(mode="off")
        cmds.refresh(suspend=True)

        # Create a unique set for this camera space setup
        set_name = get_next_camera_space_set_name()
        camera_space_set = cmds.sets(name=set_name, empty=True)
        
        # Add original objects to the set
        for s in sel:
            cmds.sets(s, add=camera_space_set)

        camera_space_group = get_or_create_camera_space_group()

        for s in sel:
            encoded_name = encode_long_name(s)
            loc_name = encoded_name + "_cam_ctrl"

            loc = cmds.spaceLocator(n=loc_name)[0]
            cmds.setAttr(loc + ".overrideEnabled", 1)
            cmds.setAttr(loc + ".overrideColor", 17)
            cmds.setAttr(loc + '.useOutlinerColor', True)
            cmds.setAttr(loc + ".outlinerColor", 0.3, 0.7, 1)

            set_locator_size(loc, s)

            locList.append(loc)
            cmds.sets(loc, add=camera_space_set)

            cmds.setAttr(loc + ".sx", lock=True)
            cmds.setAttr(loc + ".sy", lock=True)
            cmds.setAttr(loc + ".sz", lock=True)

            grp = cmds.group(n=encoded_name + "_cam_ctrl_grp")
            grpList.append(grp)
            cmds.setAttr(grp + '.useOutlinerColor', True)
            cmds.setAttr(grp + ".outlinerColor", 0.5, 0.7, 1)
            cmds.sets(grp, add=camera_space_set)

            cmds.matchTransform(loc, s, pos=True)
            cmds.matchTransform(loc, s, rot=True)
            con = cmds.parentConstraint(s, loc, mo=False)[0]
            conList.append(con)
            cmds.parentConstraint(camera, grp, mo=False)

            cmds.parent(grp, camera_space_group)

            objectMap[loc] = s

        min_time = cmds.playbackOptions(q=True, ast=True)
        max_time = cmds.playbackOptions(q=True, aet=True)
        smart_bake(locList, min_time, max_time, source_objects=sel)
        add_to_esn_ctrls_set(grpList)
        cmds.delete(conList)
        conList = []  # Clear so cleanup doesn't try to delete again

        for loc in locList:
            obj = objectMap[loc]
            smartConstraint(loc, obj)

        cmds.select(locList)
        
    except Exception as e:
        # Cleanup on error
        cmds.warning("Error creating camera space controls: " + str(e))
        
        # Delete any constraints we created
        for con in conList:
            if cmds.objExists(con):
                try:
                    cmds.delete(con)
                except:
                    pass
        
        # Delete any groups we created
        for grp in grpList:
            if cmds.objExists(grp):
                try:
                    cmds.delete(grp)
                except:
                    pass
        
        # Delete any locators we created
        for loc in locList:
            if cmds.objExists(loc):
                try:
                    cmds.delete(loc)
                except:
                    pass
        
        # Delete the set we created
        if camera_space_set and cmds.objExists(camera_space_set):
            try:
                cmds.delete(camera_space_set)
            except:
                pass
                    
    finally:
        cmds.refresh(suspend=False)
        cmds.evaluationManager(mode=original_eval_mode)

class CameraSpaceCtrlsUI(object):
    def __init__(self):
        self.window_name = "cameraSpaceCtrlsWindow"
        self.camera = None

    def create(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        self.window_name = cmds.window(self.window_name, title="Camera Space Ctrls", widthHeight=(350, 120), sizeable=False)

        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAttach=('both', 10))

        cmds.separator(height=10, style='none')

        cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 180, 60), adjustableColumn=2, columnAttach=[(1, 'left', 0), (2, 'both', 5), (3, 'right', 0)])
        cmds.text(label="Camera:", align='left')
        self.camera_text_field = cmds.textField(editable=False, backgroundColor=(0.2, 0.2, 0.2))
        cmds.button(label="Assign", command=self.assign_camera)
        cmds.setParent('..')

        saved_camera = load_camera_from_network()
        if saved_camera:
            self.camera = saved_camera
            short_name = saved_camera.split('|')[-1]
            cmds.textField(self.camera_text_field, edit=True, text=short_name)

        cmds.separator(height=15, style='none')

        cmds.button(label="Create Camera Space Ctrls", height=35, backgroundColor=(0.3, 0.5, 0.7), command=self.create_ctrls)

        cmds.separator(height=10, style='none')

        cmds.showWindow(self.window_name)

    def assign_camera(self, *args):
        sel = cmds.ls(sl=True, long=True)

        if len(sel) != 1:
            cmds.warning("Please select exactly one camera.")
            return

        selected = sel[0]

        if cmds.nodeType(selected) == 'transform':
            shapes = cmds.listRelatives(selected, shapes=True, fullPath=True)
            if shapes and cmds.nodeType(shapes[0]) == 'camera':
                self.camera = selected
                short_name = selected.split('|')[-1]
                cmds.textField(self.camera_text_field, edit=True, text=short_name)
                save_camera_to_network(selected)
                return
        elif cmds.nodeType(selected) == 'camera':
            parent = cmds.listRelatives(selected, parent=True, fullPath=True)
            if parent:
                self.camera = parent[0]
                short_name = parent[0].split('|')[-1]
                cmds.textField(self.camera_text_field, edit=True, text=short_name)
                save_camera_to_network(parent[0])
                return

        cmds.warning("Selected object is not a camera.")

    def create_ctrls(self, *args):
        if not self.camera:
            cmds.warning("Please assign a camera first.")
            cmds.confirmDialog(
                title='Camera Required',
                message='Please assign a camera first.',
                button=['OK'],
                defaultButton='OK',
                backgroundColor=[0.15, 0.15, 0.15]
            )
            return

        create_camera_space_ctrls(self.camera)

def show_ui():
    ui = CameraSpaceCtrlsUI()
    ui.create()