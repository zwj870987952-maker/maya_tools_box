import maya.cmds as cmds
import maya.mel as mel
import math

try:
    import builtins
except ImportError:
    import __builtin__ as builtins


def create_cube():
    curve = cmds.curve(d=1, p=[
        (1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1),
        (1, -1, 1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, -1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1),
        (-1, 1, 1), (-1, -1, 1), (1, -1, 1)
    ], k=list(range(16)))
    return curve


def create_plus():
    curve = cmds.curve(d=1, p=[
        (-1, 0, -2), (1, 0, -2), (1, 0, -1), (2, 0, -1),
        (2, 0, 1), (1, 0, 1), (1, 0, 2), (-1, 0, 2),
        (-1, 0, 1), (-2, 0, 1), (-2, 0, -1), (-1, 0, -1),
        (-1, 0, -2)
    ])
    return curve


def create_simple_circle():
    points = []
    for i in range(48):
        angle = (i / 48.0) * 2 * math.pi
        points.append((math.cos(angle) * 1.5, 0, math.sin(angle) * 1.5))
    points.append(points[0])
    curve = cmds.curve(d=1, p=points)
    return curve


def create_circle():
    radius = 1.5
    segments = 16

    def make_circle(axis):
        points = []
        for i in range(segments):
            angle = (i / float(segments)) * 2 * math.pi
            if axis == 'xy':
                points.append((math.cos(angle) * radius, math.sin(angle) * radius, 0))
            elif axis == 'xz':
                points.append((math.cos(angle) * radius, 0, math.sin(angle) * radius))
            elif axis == 'yz':
                points.append((0, math.cos(angle) * radius, math.sin(angle) * radius))
        points.append(points[0])
        return cmds.curve(d=1, p=points)

    xy = make_circle('xy')
    xz = make_circle('xz')
    yz = make_circle('yz')

    main_curve = xy
    for curve in [xz, yz]:
        shapes = cmds.listRelatives(curve, shapes=True, fullPath=True)
        for s in shapes:
            cmds.parent(s, main_curve, shape=True, relative=True)
        cmds.delete(curve)

    return main_curve


def create_diamond():
    curve = cmds.curve(d=1, p=[
        (0, 1, 0), (-1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0),
        (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 1, 0), (0, 0, -1),
        (-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, -1, 0),
        (0, 0, 1)
    ], k=list(range(16)))
    return curve


def create_locator():
    curve = cmds.curve(d=1, p=[
        (0.0, 2.0, 0.0), (0.0, -2.0, 0.0), (0.0, 0.0, 0.0),
        (0.0, 0.0, -2.0), (0.0, 0.0, 2.0), (0.0, 0.0, 0.0),
        (2.0, 0.0, 0.0), (-2.0, 0.0, 0.0)
    ])
    return curve


def get_control_scale_info(obj):
    scale_x = cmds.getAttr(obj + ".scaleX")
    scale_y = cmds.getAttr(obj + ".scaleY")
    scale_z = cmds.getAttr(obj + ".scaleZ")
    return builtins.max(scale_x, scale_y, scale_z)


def lock_and_hide_channels(obj):
    for channel in ['visibility']:
        attr = obj + "." + channel
        if cmds.objExists(attr):
            try:
                cmds.setAttr(attr, lock=True, keyable=False, channelBox=False)
            except:
                pass


def is_symmetric_shape(shape_suffix):
    symmetric_shapes = ["_simpleCircleShape", "_circleShape", "_diamondShape"]
    return shape_suffix in symmetric_shapes


def _gather_cvs_for_shapes(shape_nodes):
    cvs = []
    for s in shape_nodes or []:
        c = cmds.ls(s + ".cv[*]", fl=True) or cmds.ls(s + ".cv[*][*]", fl=True) or []
        if c:
            cvs.extend(c)
    return cvs


def _bbox_from_cvs_object_space(cvs):
    if not cvs:
        return None
    min_v = [float('inf')] * 3
    max_v = [float('-inf')] * 3
    for cv in cvs:
        try:
            pos = cmds.xform(cv, q=True, t=True, os=True)
        except:
            pos = cmds.xform(cv, q=True, t=True, ws=True)
        for i in range(3):
            if pos[i] < min_v[i]:
                min_v[i] = pos[i]
            if pos[i] > max_v[i]:
                max_v[i] = pos[i]
    return min_v, max_v


def show_nurbs_curves_in_all_viewports():
    all_panels = cmds.getPanel(type='modelPanel')
    for panel in all_panels:
        if cmds.modelPanel(panel, query=True, exists=True):
            editor = cmds.modelPanel(panel, query=True, modelEditor=True)
            cmds.modelEditor(editor, edit=True, nurbsCurves=True)
            cmds.modelEditor(panel, edit=True, controllers=True)


def turn_off_selection_highlighting():
    panels = cmds.getPanel(type='modelPanel')
    for panel in panels:
        cmds.modelEditor(panel, e=True, sel=False)


def turn_on_selection_highlighting():
    panels = cmds.getPanel(type='modelPanel')
    for panel in panels:
        cmds.modelEditor(panel, e=True, sel=True)


def make_nurbs_curve_thicker(line_width_increase=1.0):
    selected = cmds.ls(selection=True, type="transform")
    for ctrl in selected:
        shapes = cmds.listRelatives(ctrl, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.objectType(shape) == "nurbsCurve":
                width = cmds.getAttr(shape + ".lineWidth") if cmds.attributeQuery("lineWidth", node=shape, exists=True) else 1.0
                try:
                    cmds.setAttr(shape + ".lineWidth", width + line_width_increase)
                except:
                    pass
    cmds.select(selected, r=True)
    return selected


def set_always_draw_on_top_for_controls():
    selection = cmds.ls(selection=True) or []
    
    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in shapes:
            pass


def cv_selected():
    selection = cmds.ls(selection=True, flatten=True)
    cv_items = [item for item in selection if '.cv[' in item]
    
    if cv_items:
        shapes = set(cv.split('.')[0] for cv in cv_items)
        cmds.select(list(shapes), replace=True)


def is_only_curves_and_locators_selected(selection=None):
    if selection is None:
        selection = cmds.ls(selection=True, long=True)
    elif isinstance(selection, str):
        selection = [selection]
    selection = cmds.ls(selection, long=True) or []
    if not selection:
        return False
    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.objectType(shape) not in ["nurbsCurve", "locator"]:
                return False
    return True


def changeCtrlShape(sel):
    old_shapes = cmds.listRelatives(sel, shapes=True, fullPath=True)
    if not old_shapes:
        cmds.warning("No shapes found under " + str(sel))
        return None

    old_cvs = _gather_cvs_for_shapes(old_shapes)
    old_bbox_local = _bbox_from_cvs_object_space(old_cvs)

    if old_bbox_local:
        old_min_local, old_max_local = old_bbox_local
        old_size = [
            old_max_local[0] - old_min_local[0],
            old_max_local[1] - old_min_local[1],
            old_max_local[2] - old_min_local[2]
        ]
    else:
        old_bb_world = cmds.exactWorldBoundingBox(old_shapes)
        ctrl_scale = get_control_scale_info(sel) or 1.0
        old_size = [
            (old_bb_world[3] - old_bb_world[0]) / ctrl_scale,
            (old_bb_world[4] - old_bb_world[1]) / ctrl_scale,
            (old_bb_world[5] - old_bb_world[2]) / ctrl_scale
        ]

    shape_map = {
        "_cubeShape": (create_plus, "_plusShape"),
        "_plusShape": (create_simple_circle, "_simpleCircleShape"),
        "_simpleCircleShape": (create_circle, "_circleShape"),
        "_circleShape": (create_diamond, "_diamondShape"),
        "_diamondShape": (create_locator, "_locatorShape"),
        "_locatorShape": (create_cube, "_cubeShape"),
    }

    short_name = sel.split('|')[-1]
    creator = create_locator
    new_suffix_for_rename = "_locatorShape"
    matched_suffix = None

    for suffix, (creator_fn, new_suffix) in shape_map.items():
        if suffix in short_name:
            creator = creator_fn
            new_suffix_for_rename = new_suffix
            matched_suffix = suffix
            break

    if matched_suffix == "_cubeShape":
        cube_compensation_factor = 1.0 / 0.65
        old_size = [size * cube_compensation_factor for size in old_size]

    new_transform = creator()

    new_shape_nodes = cmds.listRelatives(new_transform, shapes=True, fullPath=True) or []
    new_cvs = _gather_cvs_for_shapes(new_shape_nodes)
    new_bbox_local = _bbox_from_cvs_object_space(new_cvs)

    if new_bbox_local and new_cvs:
        new_min_local, new_max_local = new_bbox_local
        new_size = [
            new_max_local[0] - new_min_local[0],
            new_max_local[1] - new_min_local[1],
            new_max_local[2] - new_min_local[2]
        ]
        
        if is_symmetric_shape(new_suffix_for_rename):
            max_old_size = builtins.max(old_size)
            max_new_size = builtins.max(new_size)
            uniform_scale = max_old_size / max_new_size if max_new_size != 0 else 1.0
            scale_factors = [uniform_scale, uniform_scale, uniform_scale]
        else:
            scale_factors = [
                (old_size[0] / new_size[0]) if new_size[0] != 0 else 1.0,
                (old_size[1] / new_size[1]) if new_size[1] != 0 else 1.0,
                (old_size[2] / new_size[2]) if new_size[2] != 0 else 1.0
            ]
        
        if new_suffix_for_rename == "_cubeShape" and matched_suffix != "_cubeShape":
            cube_scale_factor = 0.65
            scale_factors = [sf * cube_scale_factor for sf in scale_factors]
        
        pivot = [
            (new_min_local[0] + new_max_local[0]) / 2.0,
            (new_min_local[1] + new_max_local[1]) / 2.0,
            (new_min_local[2] + new_max_local[2]) / 2.0
        ]
        
        for cv in new_cvs:
            pos = cmds.xform(cv, q=True, t=True, os=True)
            new_pos = [
                pivot[0] + (pos[0] - pivot[0]) * scale_factors[0],
                pivot[1] + (pos[1] - pivot[1]) * scale_factors[1],
                pivot[2] + (pos[2] - pivot[2]) * scale_factors[2]
            ]
            cmds.xform(cv, os=True, t=new_pos)

    if old_shapes:
        try:
            cmds.delete(old_shapes)
        except:
            pass

    new_shapes_after_scale = cmds.listRelatives(new_transform, shapes=True, fullPath=True) or []
    if new_shapes_after_scale:
        for new_shape in new_shapes_after_scale:
            try:
                cmds.parent(new_shape, sel, r=True, s=True)
            except:
                pass

    try:
        cmds.delete(new_transform)
    except:
        pass

    short_name = sel.split('|')[-1]
    base_name = short_name
    if matched_suffix and matched_suffix in short_name:
        idx = short_name.rfind(matched_suffix)
        if idx != -1:
            base_name = short_name[:idx]

    new_short_name = base_name + new_suffix_for_rename

    try:
        renamed_obj = cmds.rename(sel, new_short_name)
    except:
        renamed_obj = sel

    lock_and_hide_channels(renamed_obj)

    try:
        cmds.select(renamed_obj, r=True)
    except:
        pass

    return renamed_obj


def changeShapeForEachCtrl():
    selections = cmds.ls(sl=True, long=True, type='transform')
    new_selections = []
    
    for sel in selections:
        new_sel = changeCtrlShape(sel)
        
        try:
            cmds.setAttr(new_sel + ".displayHandle", 1)
        except:
            pass
        
        if new_sel:
            new_selections.append(new_sel)
        else:
            new_selections.append(sel)
    
    cmds.select(new_selections, r=True)


def changeShape():
    sel = cmds.ls(sl=True)
    if not sel:
        return
    
    for obj in sel:
        try:
            if cmds.referenceQuery(obj, isNodeReferenced=True):
                cmds.warning("Skipping referenced object: " + str(obj))
                return
        except:
            pass
    
    changeShapeForEachCtrl()


def change_selected_shape():
    try:
        cv_selected()
    except:
        pass

    sel = cmds.ls(sl=True, type='transform')
    curve_loc_list = [s for s in sel if is_only_curves_and_locators_selected(s)]
    
    if not curve_loc_list:
        cmds.warning("No curves or locators selected.")
        return
    
    cmds.select(curve_loc_list, r=True)
    changeShape()
    set_always_draw_on_top_for_controls()
    make_nurbs_curve_thicker(line_width_increase=3.0)
    show_nurbs_curves_in_all_viewports()