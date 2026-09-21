import os
from ..dialogs import choose_action_dialog, namespace_dialog
from . import camera_imageplane
from ..utils import path_utils
import maya.cmds as cmds

def handle_drop(paths):
    if not paths:
        return
    path = paths[0]
    if os.path.isdir(path):
        # 判断是否为图片序列文件夹
        if path_utils.is_image_sequence_folder(path):
            camera_imageplane.create_camera_with_sequence(path)
        else:
            cmds.confirmDialog(title='提示', message='暂不支持该文件夹拖拽', button=['OK'])
        return
    ext = os.path.splitext(path)[-1].lower()
    if ext in ['.ma', '.mb', '.fbx', '.obj', '.abc']:
        action = choose_action_dialog.ask_action()
        if action == 'open':
            cmds.file(path, o=True, f=True)
        elif action == 'import':
            cmds.file(path, i=True, ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, options="v=0;", pr=True)
        elif action == 'reference':
            ns = namespace_dialog.get_namespace()
            cmds.file(path, reference=True, namespace=ns)
    else:
        cmds.confirmDialog(title='提示', message='暂不支持该文件类型拖拽', button=['OK']) 