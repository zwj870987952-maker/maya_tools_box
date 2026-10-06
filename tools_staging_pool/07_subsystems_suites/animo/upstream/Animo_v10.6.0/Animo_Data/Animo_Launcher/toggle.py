import sys
import os
import stat
import maya.cmds as cmds
import maya.mel as mel
import shutil


ENABLE_USERSETUP = False


def _close_stale_animo_windows():
    try:
        import maya.OpenMayaUI as _mui
        try:
            from PySide2 import QtWidgets as _QW
            from shiboken2 import wrapInstance as _wi
        except ImportError:
            from PySide6 import QtWidgets as _QW
            from shiboken6 import wrapInstance as _wi
        main_ptr = _mui.MQtUtil.mainWindow()
        if not main_ptr:
            return
        main_win = _wi(int(main_ptr), _QW.QMainWindow)
    except (ImportError, AttributeError, RuntimeError):
        return

    for child in main_win.children():
        try:
            name = child.objectName()
        except (AttributeError, RuntimeError):
            continue
        if name.endswith("UIWindow"):
            try:
                child.close()
                child.setParent(None)
                child.deleteLater()
            except (AttributeError, RuntimeError):
                continue


def _clear_readonly_and_retry(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass


def _safe_remove_pycache(pycache_path):
    try:
        shutil.rmtree(pycache_path, onerror=_clear_readonly_and_retry)
    except Exception:
        pass

    if not os.path.isdir(pycache_path):
        return

    for root, dirs, files in os.walk(pycache_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                os.chmod(file_path, stat.S_IWRITE)
                os.remove(file_path)
            except Exception:
                pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                os.rmdir(dir_path)
            except Exception:
                pass

    try:
        os.rmdir(pycache_path)
    except Exception:
        pass


def _stop_previous_graph_editor_row():
    for mod_name, mod_obj in list(sys.modules.items()):
        if mod_obj is not None and mod_name.endswith("graphSliderMod"):
            try:
                if hasattr(mod_obj, "stop_auto_attach_script_job"):
                    mod_obj.stop_auto_attach_script_job()
            except:
                pass
            try:
                if hasattr(mod_obj, "remove_row"):
                    mod_obj.remove_row()
            except:
                pass


version_script_dir = cmds.internalVar(userScriptDir=True)
script_dir = os.path.normpath(os.path.join(version_script_dir, "..", "..", "scripts"))
animo_data_path = os.path.join(script_dir, "Animo_Data")

if ENABLE_USERSETUP:
    try:
        cmds.optionVar(intValue=("SafeModeExecUserSetupScript", 1))
    except:
        pass

if os.path.exists(animo_data_path):
    for subfolder in ["Animo_UI", "Animo_Launcher"]:
        pycache = os.path.join(animo_data_path, subfolder, "__pycache__")
        if os.path.exists(pycache):
            _safe_remove_pycache(pycache)

animo_visible = False
qt_toolbar_visible = False
existing_qt_toolbars = []

if cmds.workspaceControl('animo', exists=True):
    animo_visible = cmds.workspaceControl('animo', query=True, visible=True)

try:
    import maya.OpenMayaUI as mui
    try:
        from PySide2 import QtWidgets, QtCore
        from shiboken2 import wrapInstance, isValid
    except ImportError:
        from PySide6 import QtWidgets, QtCore
        from shiboken6 import wrapInstance, isValid

    maya_main_ptr = mui.MQtUtil.mainWindow()
    if maya_main_ptr:
        maya_main = wrapInstance(int(maya_main_ptr), QtWidgets.QMainWindow)
        for candidate in maya_main.findChildren(QtWidgets.QWidget, "animo_qt_toolbar"):
            try:
                if isValid(candidate):
                    existing_qt_toolbars.append(candidate)
                    if candidate.isVisible():
                        qt_toolbar_visible = True
            except:
                pass
except:
    pass

if animo_visible or qt_toolbar_visible:
    if cmds.workspaceControl('animo', exists=True):
        cmds.workspaceControl('animo', edit=True, visible=False)

    for tb_widget in existing_qt_toolbars:
        try:
            tb_widget.hide()
            tb_widget.setParent(None)
            tb_widget.deleteLater()
        except:
            pass

else:
    if cmds.workspaceControl('animo', exists=True):
        try:
            cmds.deleteUI('animo', control=True)
        except:
            pass

    for tb_widget in existing_qt_toolbars:
        try:
            tb_widget.hide()
            tb_widget.setParent(None)
            tb_widget.deleteLater()
        except:
            pass

    _stop_previous_graph_editor_row()
    _close_stale_animo_windows()

    mods_to_delete = [mod for mod in list(sys.modules.keys())
                      if 'Animo' in mod or 'animo' in mod or 'styleMod' in mod or 'barMod' in mod
                      or mod in ('tooltip_manager', 'tooltip_widget', 'tooltip_data', 'compat')]
    for mod in mods_to_delete:
        del sys.modules[mod]

    sys.path = [p for p in sys.path if 'Animo' not in p and 'animo' not in p]

    if os.path.exists(animo_data_path):
        animo_launcher_dir = os.path.join(animo_data_path, "Animo_Launcher")
        for p in [script_dir, animo_data_path, animo_launcher_dir]:
            if p not in sys.path:
                sys.path.insert(0, p)

    if os.path.exists(animo_data_path):
        import importlib.util
        launcher_file = os.path.join(animo_data_path, "Animo_Launcher", "Animo_Launcher.py")
        spec = importlib.util.spec_from_file_location("Animo_Launcher_Module", launcher_file)
        launcher_module = importlib.util.module_from_spec(spec)
        sys.modules["Animo_Launcher_Module"] = launcher_module
        spec.loader.exec_module(launcher_module)

        def _ensure_animo_started():
            try:
                mod = sys.modules.get("Animo_Launcher_Module")
                if mod is None:
                    return
                tb_obj = getattr(mod, 'tb', None)
                if tb_obj is None:
                    return
                needs_build = True
                try:
                    import maya.OpenMayaUI as _mui
                    try:
                        from PySide2 import QtWidgets as _QW
                        from shiboken2 import wrapInstance as _wi, isValid as _iv
                    except ImportError:
                        from PySide6 import QtWidgets as _QW
                        from shiboken6 import wrapInstance as _wi, isValid as _iv
                    main_ptr = _mui.MQtUtil.mainWindow()
                    if main_ptr:
                        main_win = _wi(int(main_ptr), _QW.QMainWindow)
                        for w in main_win.findChildren(_QW.QWidget, "animo_qt_toolbar"):
                            try:
                                if _iv(w) and w.isVisible():
                                    needs_build = False
                                    break
                            except:
                                pass
                except:
                    pass
                if needs_build:
                    tb_obj.startUI()
            except:
                pass

        try:
            from PySide2.QtCore import QTimer
        except ImportError:
            from PySide6.QtCore import QTimer
        QTimer.singleShot(500, _ensure_animo_started)