"""Full preference/drop/dialog feature controls; explicit session activation."""
owned_window=None;views=[]
NAME='MTB_SmartAssistant';TAG='maya_toolkit.smart_assistant'
def _call(fn,*args,**kwargs):
    from maya import cmds
    try:return fn(*args,**kwargs)
    except Exception as e:cmds.warning(str(e))
def launch():
    from ... import SmartAssistantTool
    return SmartAssistantTool().run(action='enable')
def show_main_window():
    global owned_window
    from maya import cmds
    from ... import session
    from .config import prefs_manager
    from .dragdrop import dragdrop_handler
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    if cmds.window(NAME,exists=True):
        if owned_window!=NAME or cmds.window(NAME,query=True,docTag=True)!=TAG:raise RuntimeError('Foreign window name collision')
        cmds.showWindow(NAME);return NAME
    window=cmds.window(NAME,title='Maya Smart Assistant',widthHeight=(330,270),docTag=TAG);owned_window=window
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='原五项 optionVar；启用监听和路径补丁为会话行为')
    cmds.button(label='导出当前首选项（新 JSON）',command=lambda *_:_call(prefs_manager.export_prefs))
    cmds.button(label='加载并应用首选项',command=lambda *_:_call(prefs_manager.apply_prefs))
    cmds.button(label='恢复本会话应用前首选项',command=lambda *_:_call(session.restore_prefs))
    cmds.button(label='开启拖拽监听',command=lambda *_:_call(dragdrop_handler.start_dragdrop_monitor))
    cmds.button(label='停止拖拽监听',command=lambda *_:_call(dragdrop_handler.stop_dragdrop_monitor))
    cmds.button(label='启用 Python 文件对话框当前场景路径',command=lambda *_:_call(session.patch_dialog))
    cmds.button(label='恢复文件对话框',command=lambda *_:_call(session.restore_dialog))
    cmds.button(label='关闭界面',command=lambda *_:close_ui())
    cmds.showWindow(window);return window
def close_ui():
    global owned_window
    from maya import cmds
    if owned_window and cmds.window(owned_window,exists=True):
        if cmds.window(owned_window,query=True,docTag=True)!=TAG:raise RuntimeError('Window ownership changed')
        cmds.deleteUI(owned_window,window=True)
    owned_window=None
def camera_view(camera):
    from maya import cmds
    window=cmds.window(title='Smart Assistant sequence camera')
    pane=cmds.paneLayout(parent=window);panel=cmds.modelPanel(parent=pane,camera=camera)
    cmds.modelEditor(panel,edit=True,allObjects=False,imagePlane=True,grid=False)
    views.append(window);cmds.showWindow(window);return window
