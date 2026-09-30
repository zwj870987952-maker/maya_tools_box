from . import ui as bridge
from .algorithms import calculate_ik_positions, calculate_other_positions, calculate_root_world_positions, zero_out_root_control, reapply_ik_positions, reapply_other_positions, reapply_root_world_positions, optimize_keyframes
import maya.cmds as cmds
import os
import shutil
import webbrowser
import re
CONTROLLER_KEYWORDS = {'root_control': ['RootX_M'], 'ik_controls': ['IKLeg_R', 'IKLeg_L'], 'pv_controls': ['PoleLeg_R', 'PoleLeg_L'], 'other_controls': [], 'global_control': ['Main']}

def auto_identify_controllers(*_callback_args):
    return bridge.identify()

def fill_controller_fields(*_callback_args):
    return bridge.fill(None)

def fill_by_namespace(namespace):
    return bridge.fill(namespace)

def refresh_namespaces_menu(*_callback_args):
    object_menu = 'mtbB2O_objectMenu'
    items = cmds.menu(object_menu, q=True, itemArray=True) or []
    for item in items:
        if item != 'mtbB2O_refreshNamespacesItem':
            try:
                cmds.deleteUI(item)
            except:
                pass
    _, namespaces = auto_identify_controllers()
    cmds.menuItem(parent=object_menu, divider=True, dividerLabel='Namespaces')
    for ns in sorted(namespaces):
        label = 'Root Namespace' if ns == '' else ns
        import functools
        command_func = functools.partial(fill_by_namespace, ns)
        cmds.menuItem(parent=object_menu, label=label, command=lambda x, func=command_func: func())
    if len(namespaces) == 1 and '' in namespaces:
        cmds.menuItem(parent=object_menu, label='No matching namespaces found', enable=False)

def save_script_to_maya_default(*_callback_args):
    raise RuntimeError('候选不自动安装或复制脚本；请使用晋级清单')

def show_about(*_callback_args):
    cmds.confirmDialog(title='About Back2Origin', message='Back2Origin is a tool designed to help game animators convert forward-moving animations into root motion for seamless integration into game engines like Unity and Unreal.\n\nKey Features:\n- Dynamic root motion conversion\n- Frame-by-frame recalculation of IK and pole vector controls\n- Customizable bake options for game engine compatibility\n- Designed for fast and efficient workflows.\n\nFor questions or suggestions, contact via email: jk529079@gmail.com with the title [Query].', button=['OK'])

def show_contact(*_callback_args):
    cmds.confirmDialog(title='Contact', message='For inquiries, contact:\nEmail: jk529079@gmail.com', button=['OK'])

def open_gumroad_page(url):
    webbrowser.open(url)

def select_root_control(*_callback_args):
    selection = cmds.ls(selection=True)
    if len(selection) == 1:
        cmds.textFieldButtonGrp('mtbB2O_rootControlField', e=True, text=selection[0])
    else:
        cmds.warning('Please select exactly one root control.')

def select_ik_controls(*_callback_args):
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('mtbB2O_ikControlsField', e=True, text=', '.join(selection))
    else:
        cmds.warning('Please select one or more IK controls.')

def select_pv_controls(*_callback_args):
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('mtbB2O_pvControlsField', e=True, text=', '.join(selection))
    else:
        cmds.warning('Please select one or more Pole Vector controls.')

def select_other_controls(*_callback_args):
    selection = cmds.ls(selection=True)
    if len(selection) > 0:
        cmds.textFieldButtonGrp('mtbB2O_otherControlsField', e=True, text=', '.join(selection))
    else:
        cmds.warning('Please select one or more Other controls.')

def select_global_control(*_callback_args):
    selection = cmds.ls(selection=True)
    if len(selection) == 1:
        cmds.textFieldButtonGrp('mtbB2O_globalControlField', e=True, text=selection[0])
    else:
        cmds.warning('Please select exactly one global control.')

def clear_root_control(*_callback_args):
    cmds.textFieldButtonGrp('mtbB2O_rootControlField', e=True, text='')

def clear_ik_controls(*_callback_args):
    cmds.textFieldButtonGrp('mtbB2O_ikControlsField', e=True, text='')

def clear_pv_controls(*_callback_args):
    cmds.textFieldButtonGrp('mtbB2O_pvControlsField', e=True, text='')

def clear_other_controls(*_callback_args):
    cmds.textFieldButtonGrp('mtbB2O_otherControlsField', e=True, text='')

def clear_global_control(*_callback_args):
    cmds.textFieldButtonGrp('mtbB2O_globalControlField', e=True, text='')

def clear_all(*_callback_args):
    clear_root_control()
    clear_ik_controls()
    clear_pv_controls()
    clear_other_controls()
    clear_global_control()
    cmds.checkBoxGrp('mtbB2O_channelCheckBoxGrp', e=True, value1=False, value2=False)
    cmds.warning('Selections cleared!')

def toggle_start_end_frames(*_callback_args):
    bake_from_timeslider = cmds.checkBox('mtbB2O_bakeFromTimesliderCheckBox', q=True, value=True)
    cmds.intFieldGrp('mtbB2O_startFrameField', e=True, enable=not bake_from_timeslider)
    cmds.intFieldGrp('mtbB2O_endFrameField', e=True, enable=not bake_from_timeslider)

def run_root_motion_conversion(*_callback_args):
    return bridge.dispatch('convert')

def return_to_root(*_callback_args):
    return bridge.dispatch('reverse')

def show_root_help(*_callback_args):
    cmds.confirmDialog(title='Root Control Help', message='Select the main control responsible for root motion.', button=['OK'])

def show_ik_help(*_callback_args):
    cmds.confirmDialog(title='IK Controls Help', message='Select one or more IK controls that are part of the rig.', button=['OK'])

def show_pv_help(*_callback_args):
    cmds.confirmDialog(title='Pole Vector Controls Help', message='Select the pole vector controls corresponding to the IK handles.', button=['OK'])

def show_other_help(*_callback_args):
    cmds.confirmDialog(title='Other Controls Help', message='Select any additional controls like props or other rig elements.\n\nReminder: \nIf you wish the other controls to move along with the root control, ensure they are parented to an object or group constrained to the root control after the conversion.', button=['OK'])

def show_global_help(*_callback_args):
    cmds.confirmDialog(title='Global Control Help', message='Select the control that manages the global position of the character.', button=['OK'])

def show_back2origin_ui(*_callback_args):
    if cmds.window('mtbB2O_back2OriginWindow', exists=True):
        cmds.deleteUI('mtbB2O_back2OriginWindow', window=True)
    window = cmds.window('mtbB2O_back2OriginWindow', title='Back2Origin - v0.5(Beta)', widthHeight=(500, 600))
    cmds.columnLayout(adjustableColumn=True)
    menu_bar = cmds.menuBarLayout()
    cmds.menu(label='Edit')
    cmds.menuItem(label='Clear All', command=lambda *_: clear_all())
    cmds.menuItem(label='Auto-Identify Controllers', command=lambda x: fill_controller_fields())
    object_menu = cmds.menu('mtbB2O_objectMenu', label='Object', parent=menu_bar)
    cmds.menuItem('mtbB2O_refreshNamespacesItem', label='Refresh Scene', command=lambda x: refresh_namespaces_menu())
    cmds.menu(label='Help')
    cmds.menuItem(label='About', command=lambda *_: show_about())
    cmds.menuItem(label='Contact', command=lambda *_: show_contact())
    cmds.menuItem(label='Gumroad Page', command=lambda _: cmds.launch(web='https://jk529079.gumroad.com/'))
    cmds.separator(height=20, style='none')
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp('mtbB2O_rootControlField', label='Root Control     ', buttonLabel='Select', bc=select_root_control)
    cmds.button(label='Clear', command=lambda x: clear_root_control())
    cmds.button(label='?', command=lambda x: show_root_help())
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp('mtbB2O_ikControlsField', label='IK Controls     ', buttonLabel='Select', bc=select_ik_controls)
    cmds.button(label='Clear', command=lambda x: clear_ik_controls())
    cmds.button(label='?', command=lambda x: show_ik_help())
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp('mtbB2O_pvControlsField', label='Pole Vector Controls     ', buttonLabel='Select', bc=select_pv_controls)
    cmds.button(label='Clear', command=lambda x: clear_pv_controls())
    cmds.button(label='?', command=lambda x: show_pv_help())
    cmds.setParent('..')
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp('mtbB2O_otherControlsField', label='Other Controls     ', buttonLabel='Select', bc=select_other_controls)
    cmds.button(label='Clear', command=lambda x: clear_other_controls())
    cmds.button(label='?', command=lambda x: show_other_help())
    cmds.setParent('..')
    cmds.separator(height=20, style='in')
    cmds.frameLayout(label='Bake Options', collapsable=True, collapse=False)
    cmds.rowLayout(numberOfColumns=5)
    cmds.textFieldButtonGrp('mtbB2O_globalControlField', label='Global Control    ', buttonLabel='Select', bc=select_global_control)
    cmds.button(label='Clear', command=lambda x: clear_global_control())
    cmds.button(label='?', command=lambda x: show_global_help())
    cmds.setParent('..')
    form = cmds.formLayout()
    channel_checkboxes = cmds.checkBoxGrp('mtbB2O_channelCheckBoxGrp', numberOfCheckBoxes=2, label='Channel    ', labelArray2=['X', 'Z'], valueArray2=[0, 1])
    bake_from_timeslider_label = cmds.text(label='Bake from Timeslider')
    bake_from_timeslider_checkbox = cmds.checkBox('mtbB2O_bakeFromTimesliderCheckBox', label='', value=False, cc=lambda x: toggle_start_end_frames())
    cmds.formLayout(form, edit=True, attachForm=[(channel_checkboxes, 'top', 0), (channel_checkboxes, 'left', 10), (bake_from_timeslider_label, 'left', 25), (bake_from_timeslider_checkbox, 'left', 153)], attachControl=[(bake_from_timeslider_label, 'top', 10, channel_checkboxes), (bake_from_timeslider_checkbox, 'top', 10, channel_checkboxes)])
    cmds.setParent('..')
    cmds.intFieldGrp('mtbB2O_startFrameField', label='Start Frame', value1=cmds.playbackOptions(q=True, min=True), enable=True)
    cmds.intFieldGrp('mtbB2O_endFrameField', label='End Frame', value1=cmds.playbackOptions(q=True, max=True), enable=True)
    cmds.intFieldGrp('mtbB2O_frameStepField', label='Frame Step', value1=1)
    cmds.setParent('..')
    cmds.separator(height=20, style='in')
    cmds.button(label='Convert to Root Motion', command=lambda x: run_root_motion_conversion(), height=50, width=350, bgc=[0, 0.5, 0.5])
    cmds.separator(height=10, style='none')
    cmds.button(label='Return Global Motion to Root', command=lambda x: return_to_root(), height=40, width=350, bgc=[0.5, 0, 0.5])
    cmds.separator(height=10, style='none')
    cmds.text(label='Developed by: Jeremy Wang', align='center')
    cmds.text(label='Version 0.5 (Beta)', align='center')
    fill_controller_fields()
    refresh_namespaces_menu()
    cmds.showWindow(window)
