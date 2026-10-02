"""Cancel-preserving dispatch for every supplied supported drop file."""
from pathlib import Path
from ..dialogs import choose_action_dialog,namespace_dialog
from . import camera_imageplane
from ... import operations
def handle_drop(paths):
    from maya import cmds
    if not paths:return None
    if len(paths)==1 and Path(paths[0]).is_dir():return camera_imageplane.create_camera_with_sequence(paths[0])
    action=choose_action_dialog.ask_action()
    if action is None:return None
    namespace=''
    if action=='reference':
        namespace=namespace_dialog.get_namespace()
        if namespace is None:return None
    confirm=False
    if action=='open':
        confirm=cmds.confirmDialog(title='打开替换当前场景',message='打开不能通过 Undo 撤回。先保存当前场景，使用备份文件验收。',button=['打开','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')=='打开'
        if not confirm:return None
    plan=operations.plan_files(paths,action,namespace,confirm)
    return operations.execute_files(plan)
