from __future__ import print_function, division, absolute_import

import maya.cmds as cmds
import os
import sys
from spacify_core import SPACIFY_STATE, reload

def get_maya_version():
    return int(cmds.about(version=True))

MAYA_VERSION = get_maya_version()

def get_script_dir():
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except:
        return None

SCRIPT_DIR = get_script_dir()

def import_action_module(module_name):
    """Import action module with version support"""
    
    # Clear cached modules
    if module_name in sys.modules:
        del sys.modules[module_name]
    versioned_name = "{0}_py{1}".format(module_name, MAYA_VERSION)
    if versioned_name in sys.modules:
        del sys.modules[versioned_name]
    
    if SCRIPT_DIR:
        # Check for .py file first
        py_path = os.path.join(SCRIPT_DIR, module_name + ".py")
        if os.path.exists(py_path):
            module = __import__(module_name)
            return module
        
        # Check for version-specific .pyc
        pyc_versioned_path = os.path.join(SCRIPT_DIR, versioned_name + ".pyc")
        if os.path.exists(pyc_versioned_path):
            module = __import__(versioned_name)
            sys.modules[module_name] = module
            return module
    
    # Fallback to normal import
    return __import__(module_name)


def clear_focus():
    try:
        cmds.setFocus("MayaWindow")
    except Exception:
        pass


def execute_world():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        WorldSpace = import_action_module("WorldSpace")
        WorldSpace.btl_main()
    except Exception as e:
        cmds.warning("Error executing World Space: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()
        clear_focus()


def execute_new_pivot():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        NewPivot = import_action_module("NewPivot")
        NewPivot.btl_main()
    except Exception as e:
        cmds.warning("Error executing New Pivot: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_relative():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least two objects.")
            return
        
        RelativeSpace = import_action_module("RelativeSpace")
        RelativeSpace.create_relative_space_ctrls()
    except Exception as e:
        cmds.warning("Error executing Relative Space: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_group():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        GroupCtrl = import_action_module("GroupCtrl")
        GroupCtrl.btl_main()
    except Exception as e:
        cmds.warning("Error executing Group: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_aim():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        AimSpace = import_action_module("AimSpace")
        AimSpace.btl_main()
    except Exception as e:
        cmds.warning("Error executing Aim Space: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_fk():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        FKChain = import_action_module("FKChain")
        FKChain.btl_main()
    except Exception as e:
        cmds.warning("Error executing FK Chain: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_world_orient():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        WorldOrient = import_action_module("WorldOrient")
        WorldOrient.orient_main()
    except Exception as e:
        cmds.warning("Error executing World Orient: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_temp_ik():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        TempIK = import_action_module("TempIK")
        TempIK.btl_main()
    except Exception as e:
        cmds.warning("Error executing Temp IK: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def assign_camera(camera_field):
    cmds.undoInfo(openChunk=True)
    try:
        CameraSpace = import_action_module("CameraSpace")
        
        sel = cmds.ls(sl=True, long=True)
        
        if len(sel) != 1:
            cmds.warning("Please select exactly one camera.")
            return
        
        selected = sel[0]
        camera = None
        
        if cmds.nodeType(selected) == 'transform':
            shapes = cmds.listRelatives(selected, shapes=True, fullPath=True)
            if shapes and cmds.nodeType(shapes[0]) == 'camera':
                camera = selected
        elif cmds.nodeType(selected) == 'camera':
            parent = cmds.listRelatives(selected, parent=True, fullPath=True)
            if parent:
                camera = parent[0]
        
        if camera:
            SPACIFY_STATE["camera"] = camera
            short_name = camera.split('|')[-1]
            camera_field.setText(short_name)
            CameraSpace.save_camera_to_network(camera)
        else:
            cmds.warning("Selected object is not a camera.")
    except Exception as e:
        cmds.warning("Error assigning camera: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def create_camera_space():
    cmds.undoInfo(openChunk=True)
    try:
        CameraSpace = import_action_module("CameraSpace")
        
        camera = SPACIFY_STATE.get("camera")
        if not camera:
            cmds.warning("Please assign a camera first.")
            cmds.confirmDialog(
                title='Camera Required',
                message='Please assign a camera first.',
                button=['OK'],
                defaultButton='OK',
                backgroundColor=[0.15, 0.15, 0.15]
            )
            return
        CameraSpace.create_camera_space_ctrls(camera)
    except Exception as e:
        cmds.warning("Error creating camera space: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def set_offset_value(value):
    SPACIFY_STATE["offset_value"] = value
    cmds.optionVar(intValue=('shiftKeysToolOffset', value))


def apply_shift():
    cmds.undoInfo(openChunk=True)
    try:
        ShiftSceneKeys = import_action_module("ShiftSceneKeys")
        
        offset_value = SPACIFY_STATE.get("offset_value", 1000)
        ShiftSceneKeys.apply_shift_with_value(offset_value)
    except Exception as e:
        cmds.warning("Error applying shift: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_sequential_offset(offset_value):
    cmds.undoInfo(openChunk=True, chunkName="Sequential Key Offset")
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        import sequential_key_offset
        reload(sequential_key_offset)
        sequential_key_offset.apply_offset(offset_value)
    except Exception as e:
        cmds.warning("Error applying sequential offset: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def clean_and_bake_wrapper():
    cmds.undoInfo(openChunk=True, chunkName="Clean and Bake")
    try:
        CleanAndBake = import_action_module("CleanAndBake")
        
        CleanAndBake.clean_and_bake()
    except Exception as e:
        cmds.warning("Error in clean and bake: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def pick_color(color_button):
    from spacify_core import QtWidgets
    
    color = QtWidgets.QColorDialog.getColor()
    if color.isValid():
        color_button.setStyleSheet("background-color: {0}; border-radius: 5px;".format(color.name()))
        rgb = (color.redF(), color.greenF(), color.blueF())
        apply_color_to_objects(rgb)


def hue_changed(value, color_button):
    from spacify_core import QtGui
    ControlsColor = import_action_module("ControlsColor")
    
    rgb = ControlsColor.hsv_to_rgb(value, 1.0, 1.0)
    color = QtGui.QColor.fromRgbF(rgb[0], rgb[1], rgb[2])
    color_button.setStyleSheet("background-color: {0}; border-radius: 5px;".format(color.name()))
    apply_color_to_objects(rgb)


def apply_color_to_objects(rgb):
    ControlsColor = import_action_module("ControlsColor")
    
    cmds.undoInfo(openChunk=True)
    try:
        ControlsColor.apply_color_to_controls(rgb)
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


SCALE_STATE = {
    "pushClick": False,
    "openChunk": False,
    "storedObjects": [],
    "storedCVPositions": {},
    "lastValue": 1.0,
}


def get_esn_ctrls():
    selection = []
    set_name = "esn_ctrls_set"
    
    if cmds.objExists(set_name):
        try:
            set_members = cmds.sets(set_name, query=True)
            if set_members:
                for member in set_members:
                    if cmds.objExists(member):
                        obj_type = cmds.objectType(member)
                        if obj_type == 'transform':
                            selection.append(member)
        except:
            pass
    
    if not selection:
        all_objects = cmds.ls(long=True)
        for obj in all_objects:
            try:
                if cmds.objectType(obj) == 'transform':
                    full_path = obj
                    if '_esn_ctrl' in full_path or '_PIPE_' in full_path:
                        selection.append(obj)
            except:
                continue
    
    return selection


def scale_changed(value, scale_label):
    scale_label.setText("{0}%".format(value))
    
    normalized = (value - 100) / 100.0
    curve_power = 2.0
    if normalized >= 0:
        tValue = 1.0 + (normalized ** curve_power)
    else:
        tValue = 1.0 - (abs(normalized) ** curve_power)
    
    if not SCALE_STATE["pushClick"]:
        SCALE_STATE["pushClick"] = True
        
        if not SCALE_STATE["openChunk"]:
            cmds.undoInfo(openChunk=True)
            SCALE_STATE["openChunk"] = True
        
        selection = cmds.ls(selection=True, long=True)
        
        if not selection:
            selection = get_esn_ctrls()
        
        if not selection:
            return
        
        SCALE_STATE["storedObjects"] = []
        SCALE_STATE["storedCVPositions"] = {}
        
        for obj in selection:
            if not cmds.objExists(obj):
                continue
            
            try:
                obj_type = cmds.objectType(obj)
            except:
                continue
            
            if obj_type != 'transform':
                continue
            
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
            if not shapes:
                continue
            
            curveShapes = []
            locatorShape = None
            
            for shape in shapes:
                try:
                    nodeType = cmds.nodeType(shape)
                    if nodeType == 'nurbsCurve':
                        curveShapes.append(shape)
                    elif nodeType == 'locator':
                        locatorShape = shape
                except:
                    continue
            
            if curveShapes:
                try:
                    curveCVs = {}
                    for curveShape in curveShapes:
                        cvNames = cmds.ls(curveShape + '.cv[*]', flatten=True) or []
                        if cvNames:
                            curveCVs[curveShape] = cvNames
                    
                    if curveCVs:
                        SCALE_STATE["storedCVPositions"][obj] = curveCVs
                        SCALE_STATE["storedObjects"].append(('curve', obj))
                except:
                    continue
                    
            elif locatorShape:
                try:
                    SCALE_STATE["storedObjects"].append(('locator', locatorShape))
                except:
                    continue
        
        SCALE_STATE["lastValue"] = 1.0
    
    if tValue == 0:
        tValue = 0.0000001
    
    if SCALE_STATE["pushClick"] and SCALE_STATE["lastValue"] != 0:
        scaleValue = (1.0 / SCALE_STATE["lastValue"]) * tValue
    else:
        scaleValue = tValue
    
    for objType, obj in SCALE_STATE["storedObjects"]:
        if not cmds.objExists(obj):
            continue
        
        if objType == 'locator':
            try:
                currentScaleX = cmds.getAttr(obj + '.localScaleX')
                currentScaleY = cmds.getAttr(obj + '.localScaleY')
                currentScaleZ = cmds.getAttr(obj + '.localScaleZ')
                cmds.setAttr(obj + '.localScaleX', currentScaleX * scaleValue)
                cmds.setAttr(obj + '.localScaleY', currentScaleY * scaleValue)
                cmds.setAttr(obj + '.localScaleZ', currentScaleZ * scaleValue)
            except:
                continue
        
        elif objType == 'curve':
            if obj in SCALE_STATE["storedCVPositions"]:
                curveCVs = SCALE_STATE["storedCVPositions"][obj]
                
                try:
                    pivot = cmds.xform(obj, query=True, rotatePivot=True, worldSpace=True)
                except:
                    pivot = [0, 0, 0]
                
                for curveShape, cvNames in curveCVs.items():
                    for cvName in cvNames:
                        try:
                            currentPos = cmds.xform(cvName, 
                                                   query=True, translation=True, worldSpace=True)
                            
                            deltaX = currentPos[0] - pivot[0]
                            deltaY = currentPos[1] - pivot[1]
                            deltaZ = currentPos[2] - pivot[2]
                            
                            newX = pivot[0] + deltaX * scaleValue
                            newY = pivot[1] + deltaY * scaleValue
                            newZ = pivot[2] + deltaZ * scaleValue
                            
                            cmds.xform(cvName, 
                                      translation=(newX, newY, newZ), worldSpace=True)
                        except:
                            continue
    
    SCALE_STATE["lastValue"] = tValue


def scale_released(scale_slider, scale_label):
    if SCALE_STATE["openChunk"]:
        cmds.undoInfo(closeChunk=True)
        SCALE_STATE["openChunk"] = False
    
    SCALE_STATE["pushClick"] = False
    SCALE_STATE["storedObjects"] = []
    SCALE_STATE["storedCVPositions"] = {}
    SCALE_STATE["lastValue"] = 1.0
    
    scale_slider.blockSignals(True)
    scale_slider.setValue(100)
    scale_slider.blockSignals(False)
    scale_label.setText("100%")
    
    clear_focus()


def set_scale_preset(value, scale_slider, scale_label):
    SCALE_STATE["pushClick"] = False
    
    if not SCALE_STATE["openChunk"]:
        cmds.undoInfo(openChunk=True)
        SCALE_STATE["openChunk"] = True
    
    scale_slider.blockSignals(True)
    scale_slider.setValue(value)
    scale_slider.blockSignals(False)
    scale_changed(value, scale_label)
    scale_released(scale_slider, scale_label)


# ============== XFORM FUNCTIONS ==============

def execute_copy_xform():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        import xform_copy
        reload(xform_copy)
        xform_copy.copy_xform_data()
    except Exception as e:
        cmds.warning("Error copying xform: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_copy_xform_range():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        import xform_copy_range
        reload(xform_copy_range)
        xform_copy_range.copy_xform_range()
    except Exception as e:
        cmds.warning("Error copying xform range: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_paste_xform():
    cmds.undoInfo(openChunk=True)
    try:
        import xform_paste
        reload(xform_paste)
        xform_paste.paste_transforms()
    except Exception as e:
        cmds.warning("Error pasting xform: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_copy_xform_relationship():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.warning("Please select at least one object.")
            return
        
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import xform_relationship_copy
        reload(xform_relationship_copy)
        xform_relationship_copy.copy_offset()
    except Exception as e:
        cmds.warning("Error copying xform relationship: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_paste_xform_relationship():
    cmds.undoInfo(openChunk=True)
    try:
        import xform_relationship_paste
        reload(xform_relationship_paste)
        xform_relationship_paste.paste_offset_current_frame()
    except Exception as e:
        cmds.warning("Error pasting xform relationship: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_bake_xform_relationship():
    cmds.undoInfo(openChunk=True)
    try:
        import xform_relationship_bake
        reload(xform_relationship_bake)
        xform_relationship_bake.paste_offset_bake()
    except Exception as e:
        cmds.warning("Error baking xform relationship: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


# ============== ALIGN FUNCTIONS ==============

def execute_align_translate():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects_translate
        reload(align_objects_translate)
        align_objects_translate.align_translate()
    except Exception as e:
        cmds.warning("Error aligning translate: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_align_rotate():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects_rotate
        reload(align_objects_rotate)
        align_objects_rotate.align_rotate()
    except Exception as e:
        cmds.warning("Error aligning rotate: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_align():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects
        reload(align_objects)
        align_objects.align()
    except Exception as e:
        cmds.warning("Error aligning: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_align_range_translate():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects_range_translate
        reload(align_objects_range_translate)
        align_objects_range_translate.align_range_translate()
    except Exception as e:
        cmds.warning("Error aligning range translate: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_align_range_rotate():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects_range_rotate
        reload(align_objects_range_rotate)
        align_objects_range_rotate.align_range_rotate()
    except Exception as e:
        cmds.warning("Error aligning range rotate: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()


def execute_align_range():
    cmds.undoInfo(openChunk=True)
    try:
        sel = cmds.ls(sl=True)
        if len(sel) < 2:
            cmds.warning("Please select at least 2 objects.")
            return
        
        import align_objects_range
        reload(align_objects_range)
        align_objects_range.align_range()
    except Exception as e:
        cmds.warning("Error aligning range: {0}".format(str(e)))
    finally:
        cmds.undoInfo(closeChunk=True)
        clear_focus()