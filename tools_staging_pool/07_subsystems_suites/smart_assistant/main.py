import maya.cmds as cmds
from .config import prefs_manager
from .dragdrop import dragdrop_handler
from .file_dialog_patch import patch_file_dialog

def launch():
    """
    工具主入口，初始化各模块，注册事件监听和UI。
    """
    # 应用首选项
    prefs_manager.apply_prefs()
    # 启动拖拽监听
    dragdrop_handler.start_dragdrop_monitor()
    # 劫持文件对话框
    patch_file_dialog.patch_file_dialog()
    # 弹出主UI窗口
    show_main_window()

def show_main_window():
    if cmds.window('msa_main_window', exists=True):
        cmds.deleteUI('msa_main_window')
    window = cmds.window('msa_main_window', title='Maya Smart Assistant', widthHeight=(300, 120))
    cmds.columnLayout(adjustableColumn=True)
    cmds.button(label='导出当前首选项', command=lambda *_: prefs_manager.export_prefs())
    cmds.button(label='应用首选项', command=lambda *_: prefs_manager.apply_prefs())
    cmds.button(label='关闭', command=lambda *_: cmds.deleteUI(window, window=True))
    cmds.showWindow(window) 