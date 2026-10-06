from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys

def _get_this_dir():
    if hasattr(sys, '_animo_tools_path') and sys._animo_tools_path:
        return sys._animo_tools_path
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        pass
    try:
        import maya.cmds as cmds
        maya_scripts_dir = cmds.internalVar(userScriptDir=True)
        global_scripts_dir = os.path.normpath(os.path.join(maya_scripts_dir, "..", "..", "scripts"))
        return os.path.join(global_scripts_dir, "Animo_Data", "Animo_Tools_Editor", "animo_tools")
    except:
        return ""

_this_dir = _get_this_dir()
if _this_dir and _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)


def _purge_stale_modules(base_dir):
    if not os.path.isdir(base_dir):
        return
    
    self_name = os.path.splitext(os.path.basename(__file__))[0]
    module_names = set()
    
    for filename in os.listdir(base_dir):
        if filename.endswith('.py'):
            module_names.add(filename[:-3])
        elif filename.endswith('.pyc'):
            base_name = filename[:-4]
            prefix, marker, suffix = base_name.rpartition('_py')
            if marker and suffix.isdigit():
                base_name = prefix
            module_names.add(base_name)
    
    module_names.discard(self_name)
    
    normalized_base_dir = os.path.normcase(os.path.normpath(base_dir))
    
    for module_name in module_names:
        cached_module = sys.modules.get(module_name)
        if cached_module is None:
            continue
        
        cached_file = getattr(cached_module, '__file__', None)
        if not cached_file:
            continue
        
        cached_dir = os.path.normcase(os.path.normpath(os.path.dirname(cached_file)))
        if cached_dir != normalized_base_dir:
            continue
        
        del sys.modules[module_name]


if _this_dir:
    _purge_stale_modules(_this_dir)

import dialog_main as dialog_main
AnimoToolsDialog = dialog_main.AnimoToolsDialog

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore

animo_dialog = None


def _close_existing_animo_tools_windows():
    try:
        get_maya_main_window = compat.get_maya_main_window
        main_win = get_maya_main_window()
    except Exception:
        return
    
    if main_win is None:
        return
    
    for child in main_win.children():
        try:
            if child.objectName() != "AnimoToolsEditorUIWindow":
                continue
            child.close()
            child.setParent(None)
            child.deleteLater()
        except (AttributeError, RuntimeError):
            continue


def show_animo_tools():
    global animo_dialog
    
    app = QtWidgets.QApplication.instance()
    if app:
        app.setOverrideCursor(QtCore.Qt.WaitCursor)
    
    try:
        try:
            animo_dialog.close()
            animo_dialog.deleteLater()
        except Exception:
            pass
        
        _close_existing_animo_tools_windows()
        
        if app:
            app.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
            app.processEvents()
        
        animo_dialog = AnimoToolsDialog()
        animo_dialog.show()
        
        return animo_dialog
    finally:
        if app:
            app.restoreOverrideCursor()


if __name__ == "__main__":
    show_animo_tools()
