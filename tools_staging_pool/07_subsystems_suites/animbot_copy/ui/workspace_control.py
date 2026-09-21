"""
Workspace Control Manager for embedding animBot toolbar into Maya's dockable UI.
Supports:
1. Native Maya WorkspaceControl docking (Timeline, Shelf, Viewport, Status Line).
2. Tabless clean docking (hides Maya's workspaceControl QTabBar tab bar).
3. Dynamic relocation via cmds.workspaceControl(edit=True, ...).
4. Maya-level stay-on-top floating mode (does not block external Windows apps).
"""

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore, QtGui
import shiboken6
from .main_toolbar import AnimBotMainToolbar

CONTROL_NAME = "animBotCopyWorkspaceControl"
_WINDOW_INSTANCE = None
_TOOLBAR_INSTANCE = None

def get_maya_main_window():
    """Retrieve Maya's main QMainWindow instance."""
    app = QtWidgets.QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QtWidgets.QMainWindow) and "Maya" in widget.windowTitle():
            return widget
    return None

def hide_workspace_control_tab(parent_widget):
    """Hide Maya's workspaceControl QTabBar tab bar and unlock height constraints."""
    p = parent_widget
    for _ in range(6):
        if not p:
            break
        p.setMaximumHeight(16777215)
        p.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        if isinstance(p, QtWidgets.QTabWidget):
            tab_bar = p.tabBar()
            if tab_bar:
                tab_bar.hide()
                tab_bar.setFixedHeight(0)
                tab_bar.setVisible(False)
            p.setStyleSheet("""
                QTabWidget::pane { border: 0px; margin: 0px; padding: 0px; }
                QTabBar { height: 0px; max-height: 0px; }
                QTabBar::tab { height: 0px; max-height: 0px; visibility: hidden; }
            """)
        p = p.parentWidget()

def create_workspace_control(dock_area="top", float_state=False, dock_target=None):
    """
    Create or raise Maya WorkspaceControl containing AnimBotMainToolbar.
    """
    global _TOOLBAR_INSTANCE
    
    if cmds.workspaceControl(CONTROL_NAME, exists=True):
        cmds.deleteUI(CONTROL_NAME, control=True)
    
    kwargs = {
        "label": "",
        "retain": False,
        "floating": float_state,
        "initialWidth": 1920,
        "initialHeight": 54,
        "widthProperty": "free",
        "heightProperty": "free",
    }
    
    if dock_target and cmds.workspaceControl(dock_target[0], exists=True):
        kwargs["dockToControl"] = dock_target
    elif not float_state:
        kwargs["dockToMainWindow"] = (dock_area, False)
        
    cmds.workspaceControl(CONTROL_NAME, **kwargs)
    
    ptr = omui.MQtUtil.findControl(CONTROL_NAME)
    if ptr:
        parent_widget = shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
        layout = parent_widget.layout()
        if not layout:
            layout = QtWidgets.QVBoxLayout(parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
        _TOOLBAR_INSTANCE = AnimBotMainToolbar(parent_widget)
        layout.addWidget(_TOOLBAR_INSTANCE)
        
        # Hide tab bar & unlock height when docked
        hide_workspace_control_tab(parent_widget)
        
        parent_widget.show()
        return _TOOLBAR_INSTANCE
    else:
        return create_floating_window()

def create_floating_window():
    """Create a resizable floating toolbar dialog that stays on top of Maya (Maya level)."""
    global _WINDOW_INSTANCE, _TOOLBAR_INSTANCE
    close_workspace_control()
    
    main_win = get_maya_main_window()
    _WINDOW_INSTANCE = QtWidgets.QDialog(main_win)
    _WINDOW_INSTANCE.setObjectName(CONTROL_NAME)
    _WINDOW_INSTANCE.setWindowTitle("animBot")
    
    # Stay on top of Maya only (no global Windows WindowStaysOnTopHint)
    _WINDOW_INSTANCE.setWindowFlags(
        QtCore.Qt.Tool | 
        QtCore.Qt.CustomizeWindowHint | 
        QtCore.Qt.WindowTitleHint | 
        QtCore.Qt.WindowCloseButtonHint | 
        QtCore.Qt.WindowMinMaxButtonsHint
    )
    
    layout = QtWidgets.QVBoxLayout(_WINDOW_INSTANCE)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    
    _TOOLBAR_INSTANCE = AnimBotMainToolbar(_WINDOW_INSTANCE)
    layout.addWidget(_TOOLBAR_INSTANCE)
    
    size_grip = QtWidgets.QSizeGrip(_WINDOW_INSTANCE)
    layout.addWidget(size_grip, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
    
    _WINDOW_INSTANCE.resize(1920, 54)
    _WINDOW_INSTANCE.show()
    _WINDOW_INSTANCE.raise_()
    _WINDOW_INSTANCE.activateWindow()
    return _TOOLBAR_INSTANCE

def dock_to_location(location_name):
    """
    Dock toolbar to specified location in Maya or float in real time.
    Options: '时间轴顶部', '时间轴底部', '工具架顶部', '工具架底部', '状态栏顶部', '状态栏底部', '视口顶部', '视口底部', '悬浮'
    """
    global _TOOLBAR_INSTANCE
    
    dock_target = None
    if "时间轴顶部" in location_name:
        dock_target = ["TimeSlider", "top"]
    elif "时间轴底部" in location_name:
        dock_target = ["TimeSlider", "bottom"]
    elif "工具架顶部" in location_name:
        dock_target = ["Shelf", "top"]
    elif "工具架底部" in location_name:
        dock_target = ["Shelf", "bottom"]
    elif "状态栏顶部" in location_name:
        dock_target = ["StatusLine", "top"]
    elif "状态栏底部" in location_name:
        dock_target = ["StatusLine", "bottom"]
    elif "视口顶部" in location_name:
        dock_target = ["TimeSlider", "top"]
    elif "视口底部" in location_name:
        dock_target = ["TimeSlider", "bottom"]
        
    is_floating = ("悬浮" in location_name or "Floating" in location_name)

    if cmds.workspaceControl(CONTROL_NAME, exists=True):
        try:
            if is_floating:
                cmds.workspaceControl(CONTROL_NAME, edit=True, floating=True)
            elif dock_target and cmds.workspaceControl(dock_target[0], exists=True):
                cmds.workspaceControl(CONTROL_NAME, edit=True, dockToControl=dock_target)
            else:
                cmds.workspaceControl(CONTROL_NAME, edit=True, dockToMainWindow=["top", False])
            cmds.workspaceControl(CONTROL_NAME, edit=True, restore=True)
            
            ptr = omui.MQtUtil.findControl(CONTROL_NAME)
            if ptr:
                parent_widget = shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
                hide_workspace_control_tab(parent_widget)
                
            if _TOOLBAR_INSTANCE:
                _TOOLBAR_INSTANCE.relayout_groups()
            return _TOOLBAR_INSTANCE
        except Exception:
            pass

    return create_workspace_control(
        dock_area="bottom" if "底部" in location_name else "top",
        float_state=is_floating,
        dock_target=dock_target
    )

def close_workspace_control():
    """Close and clean up animBot UI."""
    global _WINDOW_INSTANCE, _TOOLBAR_INSTANCE
    if cmds.workspaceControl(CONTROL_NAME, exists=True):
        try:
            cmds.deleteUI(CONTROL_NAME, control=True)
        except Exception:
            pass
            
    if _WINDOW_INSTANCE:
        try:
            _WINDOW_INSTANCE.close()
            _WINDOW_INSTANCE.deleteLater()
        except Exception:
            pass
        _WINDOW_INSTANCE = None
        
    _TOOLBAR_INSTANCE = None
    
    app = QtWidgets.QApplication.instance()
    if app:
        for w in app.allWidgets():
            if w.objectName() == CONTROL_NAME:
                try:
                    w.close()
                    w.deleteLater()
                except Exception:
                    pass
