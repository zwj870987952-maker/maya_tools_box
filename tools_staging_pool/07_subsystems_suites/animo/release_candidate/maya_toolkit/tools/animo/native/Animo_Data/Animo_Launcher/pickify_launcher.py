## Created by Ehsan Bayat, 2026
# Quick selection set for animators that allows them to select a set of controls with one hotkey.

# Pickify Plus

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import json
import maya.OpenMayaUI as omui
import platform
try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtGui import QGuiApplication
    from shiboken6 import wrapInstance
    PYSIDE_VERSION = 6
except ImportError:
    try:
        from PySide2 import QtWidgets, QtGui, QtCore
        from PySide2.QtGui import QGuiApplication
        from shiboken2 import wrapInstance
        PYSIDE_VERSION = 2
    except ImportError:
        from PySide import QtGui, QtCore
        from PySide import QtGui as QtWidgets
        from shiboken import wrapInstance
        PYSIDE_VERSION = 1
        QGuiApplication = QtGui.QApplication

try:
    import __builtin__ as builtins
except ImportError:
    import builtins

try:
    max = builtins.max 
    min = builtins.min
    sum = builtins.sum
    abs = builtins.abs
    len = builtins.len
    int = builtins.int
    str = builtins.str
    set = builtins.set
    range = builtins.range
    list = builtins.list
    dict = builtins.dict
except:
    pass



def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except:
        return 2022

def get_event_pos(event):
    """Get position from event in a Qt version compatible way"""
    try:
        if hasattr(event, 'position'):
            return event.position().toPoint()
    except:
        pass
    return event.pos()

def get_event_global_pos(event):
    """Get global position from event as QPoint in a Qt version compatible way"""
    try:
        if hasattr(event, 'globalPosition'):
            return event.globalPosition().toPoint()
    except:
        pass
    return event.globalPos()

def exec_menu(menu, pos):
    """Execute menu in a Qt version compatible way"""
    # In Python 2.7, 'exec' is a keyword, so we use getattr
    if hasattr(menu, 'exec'):
        exec_method = getattr(menu, 'exec')
        return exec_method(pos)
    else:
        return menu.exec_(pos)

def get_dpi_scale():
    base_scale = 1.0

    try:
        if PYSIDE_VERSION == 6:
            screen = QGuiApplication.primaryScreen()
            if screen:
                base_scale = screen.logicalDotsPerInch() / 96.0
        else:
            app = QtWidgets.QApplication.instance()
            if app:
                desktop = app.desktop()
                if desktop:
                    screen = desktop.screen()
                    if screen:
                        base_scale = screen.logicalDpiX() / 96.0
    except Exception:
        base_scale = 1.0

    return max(1.0, min(base_scale, 3.0))

        
def get_manual_scale_override():
    if cmds.optionVar(exists="esnPickifyScale"):
        scale = cmds.optionVar(q="esnPickifyScale")
        return max(0.5, min(scale, 3.0))
    return None

def scale_font_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())

def scale_size(size):
    manual_override = get_manual_scale_override()
    if manual_override:
        return int(size * manual_override)
    return int(size * get_dpi_scale())

def get_context_menu_style():
    font_size = scale_font_size(12)
    padding = scale_size(7)
    margin = scale_size(1)
    border_radius = scale_size(4)
    item_radius = scale_size(3)
    
    return """
        QMenu {{
            background-color: #333;
            color: #eee;
            border: 1px solid #555;
            border-radius: {0}px;
            padding: {1}px;
            font-size: {2}px;
        }}
        QMenu::item {{
            background-color: transparent;
            padding: {3}px {4}px;
            border-radius: {5}px;
            margin: {6}px;
        }}
        QMenu::item:selected {{
            background-color: #f39c12;
            color: #222;
            font-weight: bold;
        }}
        QMenu::separator {{
            height: 1px;
            background-color: #555;
            margin: {1}px {7}px;
        }}
    """.format(border_radius, scale_size(4), font_size, padding, scale_size(14), item_radius, margin, scale_size(8))

def is_macos():
    import platform
    return platform.system() == 'Darwin'    

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def get_esn_network_node():
    node = "esnSelectionSets"
    if not cmds.objExists(node):
        current_selection = cmds.ls(selection=True)
        node = cmds.createNode("network", name=node)
        cmds.addAttr(node, longName="selectionSets", dataType="string")
        cmds.addAttr(node, longName="setMetadata", dataType="string")
        
        # Make node persistent - prevent Maya from deleting it
        cmds.setAttr("{0}.isHistoricallyInteresting".format(node), 1)
        cmds.lockNode(node, lock=False)  # Ensure it's unlocked for editing
        
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
    return node

def save_esn_sets(data):
    node = get_esn_network_node()
    json_data = json.dumps(data)
    cmds.setAttr("{0}.selectionSets".format(node), json_data, type="string")

def load_esn_sets():
    node = get_esn_network_node()
    if cmds.objExists("{0}.selectionSets".format(node)):
        try:
            raw = cmds.getAttr("{0}.selectionSets".format(node))
            return json.loads(raw) if raw else {}
        except Exception:
            return {}
    return {}

def save_set_metadata(metadata):
    node = get_esn_network_node()
    json_data = json.dumps(metadata)
    cmds.setAttr("{0}.setMetadata".format(node), json_data, type="string")

def load_set_metadata():
    node = get_esn_network_node()
    if cmds.objExists("{0}.setMetadata".format(node)):
        try:
            raw = cmds.getAttr("{0}.setMetadata".format(node))
            return json.loads(raw) if raw else {}
        except Exception:
            return {}
    return {}


def get_groups_network_node():
    node = "esnSelectionGroups"
    if not cmds.objExists(node):
        current_selection = cmds.ls(selection=True)
        node = cmds.createNode("network", name=node)
        cmds.addAttr(node, longName="groups", dataType="string")
        cmds.addAttr(node, longName="currentGroup", dataType="string")
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
    return node

def save_groups_data(groups_data):
    node = get_groups_network_node()
    json_data = json.dumps(groups_data)
    cmds.setAttr("{0}.groups".format(node), json_data, type="string")

def load_groups_data():
    node = get_groups_network_node()
    if cmds.objExists("{0}.groups".format(node)):
        try:
            raw = cmds.getAttr("{0}.groups".format(node))
            return json.loads(raw) if raw else {'groups': ['Default'], 'current_group': 'Default'}
        except Exception:
            return {'groups': ['Default'], 'current_group': 'Default'}
    return {'groups': ['Default'], 'current_group': 'Default'}

def get_group_network_node(group_name):
    safe_name = "".join(c for c in group_name if c.isalnum() or c in ('_', '-')).strip().replace(' ', '_')
    node = "esnGroup_{0}".format(safe_name)
    if not cmds.objExists(node):
        current_selection = cmds.ls(selection=True)
        node = cmds.createNode("network", name=node)
        cmds.addAttr(node, longName="selectionSets", dataType="string")
        cmds.addAttr(node, longName="setMetadata", dataType="string")
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
    return node

def get_pickify_ui_size_network_node():
    node = "esnPickifyUISize"
    if not cmds.objExists(node):
        current_selection = cmds.ls(selection=True)
        node = cmds.createNode("network", name=node)
        cmds.addAttr(node, longName="horizontalWidth", attributeType="long")
        cmds.addAttr(node, longName="horizontalHeight", attributeType="long")
        if current_selection:
            cmds.select(current_selection, replace=True)
        else:
            cmds.select(clear=True)
    return node

def save_horizontal_ui_size(width, height):
    node = get_pickify_ui_size_network_node()
    cmds.setAttr("{0}.horizontalWidth".format(node), int(width))
    cmds.setAttr("{0}.horizontalHeight".format(node), int(height))

def load_horizontal_ui_size():
    node = "esnPickifyUISize"
    if cmds.objExists(node) and cmds.objExists("{0}.horizontalWidth".format(node)) and cmds.objExists("{0}.horizontalHeight".format(node)):
        try:
            width = cmds.getAttr("{0}.horizontalWidth".format(node))
            height = cmds.getAttr("{0}.horizontalHeight".format(node))
            if width and height:
                return (width, height)
        except Exception:
            return None
    return None

def save_group_sets(data, group_name):
    node = get_group_network_node(group_name)
    json_data = json.dumps(data)
    cmds.setAttr("{0}.selectionSets".format(node), json_data, type="string")
    sync_all_sets_to_main_network_node()

def migrate_old_sets_to_default_group():
    """Migrate sets from old esnSelectionSets node to new Default group structure."""
    old_node = "esnSelectionSets"
    
    # Check if old node exists
    if not cmds.objExists(old_node):
        return False
    
    # Check if migration has already been done
    if cmds.objExists("{0}.migrationComplete".format(old_node)):
        try:
            migrated = cmds.getAttr("{0}.migrationComplete".format(old_node))
            if migrated:
                return False  # Already migrated, don't do it again
        except:
            pass
    
    # Try to load old sets
    if not cmds.objExists("{0}.selectionSets".format(old_node)):
        return False
    
    try:
        raw = cmds.getAttr("{0}.selectionSets".format(old_node))
        old_sets = json.loads(raw) if raw else {}
    except Exception:
        return False
    
    # If no old sets, nothing to migrate
    if not old_sets:
        return False
    
    # Load old metadata if it exists
    old_metadata = {}
    if cmds.objExists("{0}.setMetadata".format(old_node)):
        try:
            raw_meta = cmds.getAttr("{0}.setMetadata".format(old_node))
            old_metadata = json.loads(raw_meta) if raw_meta else {}
        except Exception:
            pass
    
    # Load current Default group data
    default_data = load_group_sets("Default")
    default_metadata = load_group_metadata("Default")
    
    # Merge old sets into Default group (don't overwrite existing)
    migrated_count = 0
    for set_name, set_contents in old_sets.items():
        if set_name not in default_data:
            default_data[set_name] = set_contents
            migrated_count += 1
            
            # Also migrate metadata if exists
            if set_name in old_metadata:
                default_metadata[set_name] = old_metadata[set_name]
    
    # Save merged data if anything was migrated
    if migrated_count > 0:
        save_group_sets(default_data, "Default")
        save_group_metadata(default_metadata, "Default")
        
        # Mark migration as complete to prevent re-running
        if not cmds.objExists("{0}.migrationComplete".format(old_node)):
            cmds.addAttr(old_node, longName="migrationComplete", attributeType="bool")
        cmds.setAttr("{0}.migrationComplete".format(old_node), True)
        
        cmds.warning("Migrated {0} set(s) from old Pickify version to Default group.".format(migrated_count))
        return True
    
    return False

def sync_all_sets_to_main_network_node():
    """Sync all sets from all groups to the main esnSelectionSets network node for hotkey compatibility."""
    groups_data = load_groups_data()
    all_groups = groups_data.get('groups', ['Default'])
    
    combined_sets = {}
    disabled_sets = []
    
    for group in all_groups:
        group_sets = load_group_sets(group)
        group_metadata = load_group_metadata(group)
        
        # Only add sets that are NOT disabled for hotkeys
        for set_name, set_objects in group_sets.items():
            # Check if hotkey is disabled in metadata
            is_disabled = False
            if set_name in group_metadata and isinstance(group_metadata[set_name], dict):
                is_disabled = group_metadata[set_name].get("hotkey_disabled", False)
            
            # Only add if not disabled
            if not is_disabled:
                combined_sets[set_name] = set_objects
            else:
                disabled_sets.append(set_name)
    
    main_node = get_esn_network_node()
    json_data = json.dumps(combined_sets)
    cmds.setAttr("{0}.selectionSets".format(main_node), json_data, type="string")


# Global variable to track the persistent sync job
_pickify_persistent_sync_job = None

def start_persistent_sync_job():
    """Start a persistent scriptJob that keeps the network node synced even when UI is closed."""
    global _pickify_persistent_sync_job
    
    # Kill existing job if any
    if _pickify_persistent_sync_job:
        try:
            if cmds.scriptJob(exists=_pickify_persistent_sync_job):
                cmds.scriptJob(kill=_pickify_persistent_sync_job, force=True)
        except:
            pass
    
    # Create new persistent job
    try:
        # This job will run on every scene open/new and keep the network node synced
        _pickify_persistent_sync_job = cmds.scriptJob(
            event=["SceneOpened", sync_all_sets_to_main_network_node],
            permanent=True  # This keeps it alive even when UI closes!
        )
    except Exception as e:
        pass


def load_group_sets(group_name):
    node = get_group_network_node(group_name)
    if cmds.objExists("{0}.selectionSets".format(node)):
        try:
            raw = cmds.getAttr("{0}.selectionSets".format(node))
            return json.loads(raw) if raw else {}
        except Exception:
            return {}
    return {}

def save_group_metadata(metadata, group_name):
    node = get_group_network_node(group_name)
    json_data = json.dumps(metadata)
    cmds.setAttr("{0}.setMetadata".format(node), json_data, type="string")

def load_group_metadata(group_name):
    node = get_group_network_node(group_name)
    if cmds.objExists("{0}.setMetadata".format(node)):
        try:
            raw = cmds.getAttr("{0}.setMetadata".format(node))
            return json.loads(raw) if raw else {}
        except Exception:
            return {}
    return {}

def save_window_position(pos):
    cmds.optionVar(iv=("esnSetsWinX", pos.x()))
    cmds.optionVar(iv=("esnSetsWinY", pos.y()))

def load_window_position():
    if cmds.optionVar(exists="esnSetsWinX") and cmds.optionVar(exists="esnSetsWinY"):
        x = cmds.optionVar(q="esnSetsWinX")
        y = cmds.optionVar(q="esnSetsWinY")
        return QtCore.QPoint(x, y)
    return None

def get_user_home_dir():
    """Resolve the user's home directory in a way that stays consistent
    across Maya/Python versions on Windows.

    os.path.expanduser("~") has been observed to behave inconsistently
    between Maya's bundled Python 2.7 (Maya 2022) and Python 3 (Maya 2023+)
    on Windows, in some environments resolving to the Documents folder
    itself rather than the user's home folder. This prefers the Windows
    USERPROFILE environment variable directly, with HOMEDRIVE/HOMEPATH and
    expanduser("~") as fallbacks, and guards against a resolved path that
    already ends in "Documents" so a "Documents/Documents" doubling can't
    happen even if the underlying resolution misbehaves again.
    """
    home = None
    if platform.system() == "Windows":
        home = os.environ.get("USERPROFILE")
        if not home:
            home_drive = os.environ.get("HOMEDRIVE", "")
            home_path = os.environ.get("HOMEPATH", "")
            if home_drive and home_path:
                home = home_drive + home_path
    if not home:
        home = os.path.expanduser("~")
    home = os.path.normpath(home)
    if os.path.basename(home).lower() == "documents":
        home = os.path.dirname(home)
    return home

def get_pickify_ui_settings_path():
    maya_docs_dir = os.path.join(get_user_home_dir(), "Documents", "maya")
    if not os.path.isdir(maya_docs_dir):
        try:
            os.makedirs(maya_docs_dir)
        except Exception:
            pass
    return os.path.join(maya_docs_dir, "pickify_ui_settings.json")

def load_pickify_ui_settings():
    settings_path = get_pickify_ui_settings_path()
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_pickify_ui_settings(settings_data):
    settings_path = get_pickify_ui_settings_path()
    try:
        with open(settings_path, "w") as f:
            json.dump(settings_data, f, indent=2)
    except Exception:
        pass

def get_ui_mode():
    settings_data = load_pickify_ui_settings()
    return settings_data.get("ui_mode", "horizontal")

def set_ui_mode(mode):
    settings_data = load_pickify_ui_settings()
    settings_data["ui_mode"] = mode
    save_pickify_ui_settings(settings_data)

def get_selected_namespaces():
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        return []
    
    namespaces = set()
    for obj in selection:
        if ":" in obj:
            ns = obj.split("|")[-1].rsplit(":", 1)[0]
            namespaces.add(ns)
        else:
            namespaces.add("")
    
    return list(namespaces)

def get_namespace_from_object(obj):
    short_name = obj.split("|")[-1]
    if ":" in short_name:
        return short_name.rsplit(":", 1)[0]
    return ""

def find_all_nurbs_curves_in_namespace(namespace):
    all_transforms = cmds.ls(type='transform', long=True)
    nurbs_curves = []
    
    for transform in all_transforms:
        obj_namespace = get_namespace_from_object(transform)
        
        if obj_namespace == namespace:
            shapes = cmds.listRelatives(transform, shapes=True, fullPath=True)
            if shapes:
                for shape in shapes:
                    if cmds.nodeType(shape) == 'nurbsCurve':
                        nurbs_curves.append(transform)
                        break
    
    return nurbs_curves

def select_all_ctrls():
    cmds.waitCursor(state=True)
    
    try:
        original_selection = cmds.ls(selection=True, long=True)
        
        if not original_selection:
            cmds.warning("Please select at least one object")
            return
        
        selected_namespaces = get_selected_namespaces()
        
        all_curves = []
        for ns in selected_namespaces:
            curves_in_ns = find_all_nurbs_curves_in_namespace(ns)
            all_curves.extend(curves_in_ns)
        
        if all_curves:
            cmds.select(all_curves, replace=True)
            cmds.select(original_selection, add=True)
        else:
            cmds.warning("No NURBS curves found in the selected namespace(s)")
    
    finally:
        cmds.waitCursor(state=False)





class CustomInputDialog(QtWidgets.QDialog):
    def __init__(self, title, label, initial_text="", parent=None):
        super(CustomInputDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.result_text = None
        
        font_size = scale_font_size(12)
        line_edit_font_size = scale_font_size(13)
        button_font_size = scale_font_size(11)
        padding = scale_size(6)
        border_radius = scale_size(4)
        button_padding = scale_size(4)
        button_min_width = scale_size(50)
        button_max_height = scale_size(22)
        
        self.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
                border: 1px solid #555;
                border-radius: {0}px;
            }}
            QLabel {{
                color: #eee;
                font-size: {1}px;
                padding: {2}px;
            }}
        """.format(scale_size(8), font_size, scale_size(5)))
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(scale_size(0))
        main_layout.setContentsMargins(scale_size(10), scale_size(1), scale_size(10), scale_size(12))
        
        label_widget = QtWidgets.QLabel(label)
        label_widget.setStyleSheet("padding: 0px; margin: 0px;")
        label_widget.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(label_widget)
        
        main_layout.addSpacing(scale_size(2))
        
        self.line_edit = QtWidgets.QLineEdit(initial_text)
        self.line_edit.setStyleSheet("""
            QLineEdit {{
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: {0}px;
                padding: {1}px;
                font-size: {2}px;
                min-height: {3}px;
            }}
            QLineEdit:hover {{
                border-color: #f39c12;
            }}
            QLineEdit:focus {{
                border-color: #f39c12;
                background-color: #3a3a3a;
            }}
        """.format(border_radius, padding, line_edit_font_size, scale_size(17)))
        self.line_edit.selectAll()
        main_layout.addWidget(self.line_edit)
        
        main_layout.addSpacing(scale_size(12))
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(scale_size(4))
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {{
                background-color: #555;
                color: #eee;
                border: none;
                border-radius: {0}px;
                padding: {1}px {2}px;
                font-size: {3}px;
                font-weight: 600;
                min-width: {4}px;
                max-height: {5}px;
            }}
            QPushButton:hover {{
                background-color: #666;
            }}
            QPushButton:pressed {{
                background-color: #444;
            }}
        """.format(border_radius, button_padding, scale_size(8), button_font_size, button_min_width, button_max_height))
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {{
                background-color: #f39c12;
                color: #222;
                border: none;
                border-radius: {0}px;
                padding: {1}px {2}px;
                font-size: {3}px;
                font-weight: 600;
                min-width: {4}px;
                max-height: {5}px;
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
            QPushButton:pressed {{
                background-color: #d35400;
            }}
        """.format(border_radius, button_padding, scale_size(8), button_font_size, button_min_width, button_max_height))
        ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(ok_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.setFixedSize(scale_size(300), scale_size(120))
        
    def accept(self):
        self.result_text = self.line_edit.text()
        super(CustomInputDialog, self).accept()
        
    def get_text(self):
        return self.result_text
    
    def showEvent(self, event):
        super(CustomInputDialog, self).showEvent(event)
        self.line_edit.setFocus()
        self.line_edit.selectAll()

class TransferSetDialog(QtWidgets.QDialog):
    def __init__(self, current_group, all_groups, parent=None):
        super(TransferSetDialog, self).__init__(parent)
        self.setWindowTitle("Transfer to Group")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        if is_macos():
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.selected_group = None
        self.current_group = current_group
        
        font_size = scale_font_size(12)
        button_font_size = scale_font_size(11)
        padding = scale_size(6)
        border_radius = scale_size(4)
        button_padding = scale_size(4)
        button_min_width = scale_size(50)
        button_max_height = scale_size(22)
        list_item_height = scale_size(25)
        
        self.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
                border: 1px solid #555;
                border-radius: {0}px;
            }}
            QLabel {{
                color: #eee;
                font-size: {1}px;
                padding: {2}px;
            }}
        """.format(scale_size(8), font_size, scale_size(5)))
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(scale_size(8))
        main_layout.setContentsMargins(scale_size(10), scale_size(10), scale_size(10), scale_size(10))
        
        label = QtWidgets.QLabel("Select destination group:")
        main_layout.addWidget(label)
        
        self.groups_list = GroupRightClickListWidget()
        self.groups_list.set_dropped.connect(self.on_set_dropped)
        self.groups_list.setStyleSheet("""
            QListWidget {{
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                font-size: {0}px;
                border-radius: {1}px;
            }}
            QListWidget::item {{
                padding: {2}px;
                min-height: {3}px;
            }}
            QListWidget::item:hover {{
                background-color: #4a4a4a;
            }}
            QListWidget::item:selected {{
                background-color: #f39c12;
                color: #222;
            }}
        """.format(font_size, border_radius, padding, list_item_height))
        
        for group in all_groups:
            if group != current_group:
                self.groups_list.addItem(group)
        
        main_layout.addWidget(self.groups_list)
        
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(scale_size(4))
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {{
                background-color: #555;
                color: #eee;
                border: none;
                border-radius: {0}px;
                padding: {1}px {2}px;
                font-size: {3}px;
                font-weight: 600;
                min-width: {4}px;
                max-height: {5}px;
            }}
            QPushButton:hover {{
                background-color: #666;
            }}
            QPushButton:pressed {{
                background-color: #444;
            }}
        """.format(border_radius, button_padding, scale_size(8), button_font_size, button_min_width, button_max_height))
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        transfer_btn = QtWidgets.QPushButton("Transfer")
        transfer_btn.setStyleSheet("""
            QPushButton {{
                background-color: #f39c12;
                color: #222;
                border: none;
                border-radius: {0}px;
                padding: {1}px {2}px;
                font-size: {3}px;
                font-weight: 600;
                min-width: {4}px;
                max-height: {5}px;
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
            QPushButton:pressed {{
                background-color: #d35400;
            }}
        """.format(border_radius, button_padding, scale_size(8), button_font_size, button_min_width, button_max_height))
        transfer_btn.setCursor(QtCore.Qt.PointingHandCursor)
        transfer_btn.clicked.connect(self.accept)
        transfer_btn.setDefault(True)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(transfer_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.setFixedSize(scale_size(250), scale_size(300))
        
    def accept(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_group = current_item.text()
            super(TransferSetDialog, self).accept()
        
    def get_selected_group(self):
        return self.selected_group

class GroupSetsDialog(QtWidgets.QDialog):
    group_switched = QtCore.Signal(str)
    set_transfer_requested = QtCore.Signal(str, str)  # (set_name, target_group)
    
    def __init__(self, parent=None, current_group=None):
        super(GroupSetsDialog, self).__init__(parent)
        self.current_group = current_group or "Default"
        self.setWindowTitle("Groups")
        
        maya_version = get_maya_version()
        if maya_version >= 2020:
            self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        else:
            self.setStyleSheet("QDialog { background-color: rgb(34, 34, 34); }")
        
        if is_macos():
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        base_width = scale_size(120)
        base_height = scale_size(280)
        self.setFixedSize(base_width, base_height)
        
        # Setup opacity animations for fade effect
        self.setWindowOpacity(0.0)  # Start invisible
        
        # Fade in animation on startup
        self.fade_in_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_anim.setDuration(400)
        self.fade_in_anim.setStartValue(0.0)
        self.fade_in_anim.setEndValue(1.0)
        self.fade_in_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        # Fade animation for mouse enter/leave
        self.fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        
        self.setMouseTracking(True)
        
        
        self.setup_ui()
        self.load_groups()
        self.fade_in_anim.start()  # Start fade-in
        self._drag_pos = None
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = get_event_global_pos(event) - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton and self._drag_pos is not None:
            self.move(get_event_global_pos(event) - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        
    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QtWidgets.QWidget()
        border_radius = scale_size(12)
        self.container.setStyleSheet("""
            QWidget {{
                background-color: rgba(38, 38, 38, 245);
                border-radius: {0}px;
                border: 1px solid rgba(68, 68, 68, 180);
            }}
        """.format(border_radius))
        
        margin = scale_size(8)
        spacing = scale_size(4)
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(margin, margin, margin, margin)
        container_layout.setSpacing(spacing)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(spacing)
        
        header_layout.addStretch()

        exit_size = scale_size(16)
        exit_font_size = scale_font_size(12)
        
        self.exit_btn = QtWidgets.QPushButton("X")
        self.exit_btn.setFixedSize(exit_size, exit_size)
        self.exit_btn.setStyleSheet("""
            QPushButton {{
                background: rgba(243, 156, 18, 200);
                border: none;
                color: #fff;
                font-size: {0}px;
                font-weight: bold;
                border-radius: 3px;
            }}
            QPushButton:hover {{ background: rgba(243, 156, 18, 255); }}
        """.format(exit_font_size))
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setCursor(QtCore.Qt.PointingHandCursor)
        header_layout.addWidget(self.exit_btn)

        container_layout.addLayout(header_layout)

        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(scale_size(3))
        
        button_height = scale_size(20)
        button_font_size = scale_font_size(9)
        button_radius = scale_size(4)
        
        self.new_btn = QtWidgets.QPushButton("NEW GROUP")
        self.new_btn.setFixedHeight(button_height)
        self.new_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.new_btn.setStyleSheet("""
            QPushButton {{
                background: rgba(166, 124, 22, 220);
                border: 1px solid rgba(138, 102, 18, 220);
                border-radius: {0}px;
                color: #fff;
                font-size: {1}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background: rgba(200, 149, 26, 240);
            }}
            QPushButton:pressed {{ background: rgba(212, 161, 38, 255); }}
        """.format(button_radius, button_font_size))
        self.new_btn.clicked.connect(self.on_new_group)
        button_layout.addWidget(self.new_btn)
        
        container_layout.addLayout(button_layout)
        
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_margin = scale_size(4)
        separator.setStyleSheet("""
            QFrame {{
                color: rgba(102, 102, 102, 120);
                background-color: rgba(102, 102, 102, 120);
                margin: {0}px 0px;
            }}
        """.format(separator_margin))
        container_layout.addWidget(separator)

        list_height = scale_size(200)
        list_font_size = scale_font_size(12)
        item_radius = scale_size(4)
        item_padding = scale_size(4)
        item_margin = scale_size(3)
        item_height = scale_size(14)
        
        self.groups_list = GroupRightClickListWidget()
        self.groups_list.setFixedHeight(list_height)
        self.groups_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.groups_list.setStyleSheet("""
            QListWidget {{
                background: transparent;
                border: none;
                color: #f39c12;
                font-size: {0}px;
                font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
                font-weight: 600;
                letter-spacing: 0.5px;
                outline: none;
            }}
            QListWidget::item {{
                border: 1px solid rgba(102, 102, 102, 100);
                border-radius: {1}px;
                padding: {2}px 6px;
                margin: {3}px;
                min-height: {4}px;
                color: #f39c12;
                text-align: center;
            }}
            QListWidget::item:hover {{
                border-color: #f39c12;
                font-weight: 700;
                color: #f39c12;
            }}
            QListWidget::item:selected {{
                background: rgba(243, 156, 18, 180);
                border-color: #f39c12;
                color: #fff;
                font-weight: 700;
            }}
        """.format(list_font_size, item_radius, item_padding, item_margin, item_height))
        
        self.groups_list.itemDoubleClicked.connect(self.on_rename_group)
        self.groups_list.rename_requested.connect(self.on_rename_group)
        self.groups_list.delete_requested.connect(self.on_delete_group)
        self.groups_list.switch_requested.connect(self.on_switch_group_from_menu)
        self.groups_list.switch_no_close_requested.connect(self.on_switch_group_no_close_from_list)
        self.groups_list.set_dropped.connect(self.on_set_dropped)  # Connect drop handler!
        
        container_layout.addWidget(self.groups_list)
        
        go_to_button_layout = QtWidgets.QHBoxLayout()
        go_to_button_layout.setSpacing(scale_size(3))
        
        self.go_to_btn = QtWidgets.QPushButton("Switch")
        self.go_to_btn.setFixedHeight(button_height)
        self.go_to_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.go_to_btn.setStyleSheet("""
            QPushButton {{
                background: rgba(166, 124, 22, 220);
                border: 1px solid rgba(138, 102, 18, 220);
                border-radius: {0}px;
                color: #fff;
                font-size: {1}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background: rgba(200, 149, 26, 240);
            }}
            QPushButton:pressed {{ background: rgba(212, 161, 38, 255); }}
        """.format(button_radius, button_font_size))
        self.go_to_btn.clicked.connect(self.on_switch_to_selected_group)
        go_to_button_layout.addWidget(self.go_to_btn)
        
        container_layout.addLayout(go_to_button_layout)
        
        main_layout.addWidget(self.container)
        
    def load_groups(self):
        self.groups_list.clear()
        groups_data = load_groups_data()
        groups = groups_data.get('groups', ['Default'])
        
        for group in groups:
            item = QtWidgets.QListWidgetItem(group)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            if group == self.current_group:
                item.setBackground(QtGui.QColor("#f39c12"))
                item.setForeground(QtGui.QColor("#fff"))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            self.groups_list.addItem(item)
            
    def on_new_group(self):
        dialog = CustomInputDialog("New Group", "Enter group name:", "", self)
        ok = dialog.exec_() == QtWidgets.QDialog.Accepted
        text = dialog.get_text() if ok else ""
        
        if ok and text:
            groups_data = load_groups_data()
            groups = groups_data.get('groups', ['Default'])
            
            if text in groups:
                cmds.warning("A group with this name already exists.")
                return
                
            groups.append(text)
            groups_data['groups'] = groups
            save_groups_data(groups_data)
            
            self.load_groups()
            
    def on_rename_group(self):
        current_item = self.groups_list.currentItem()
        if not current_item:
            return
            
        old_name = current_item.text()
        
        dialog = CustomInputDialog("Rename Group", "Enter new name:", old_name, self)
        ok = dialog.exec_() == QtWidgets.QDialog.Accepted
        text = dialog.get_text() if ok else old_name
        
        if ok and text and text != old_name:
            groups_data = load_groups_data()
            groups = groups_data.get('groups', ['Default'])
            
            if text in groups:
                cmds.warning("A group with this name already exists.")
                return
                
            idx = groups.index(old_name)
            groups[idx] = text
            
            if groups_data.get('current_group') == old_name:
                groups_data['current_group'] = text
                self.current_group = text
            
            groups_data['groups'] = groups
            save_groups_data(groups_data)
            
            old_node = get_group_network_node(old_name)
            new_node = get_group_network_node(text)
            if cmds.objExists(old_node) and old_node != new_node:
                try:
                    if cmds.objExists("{0}.selectionSets".format(old_node)):
                        data = cmds.getAttr("{0}.selectionSets".format(old_node))
                        cmds.setAttr("{0}.selectionSets".format(new_node), data, type="string")
                    if cmds.objExists("{0}.setMetadata".format(old_node)):
                        metadata = cmds.getAttr("{0}.setMetadata".format(old_node))
                        cmds.setAttr("{0}.setMetadata".format(new_node), metadata, type="string")
                    cmds.delete(old_node)
                except:
                    pass
            
            self.load_groups()
            
    def on_delete_group(self):
        current_item = self.groups_list.currentItem()
        if not current_item:
            return
            
        group_name = current_item.text()
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Confirm Delete")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setFixedSize(scale_size(280), scale_size(120))
        font_size = scale_font_size(12)
        button_font_size = scale_font_size(11)
        button_height = scale_size(30)
        border_radius = scale_size(4)
        padding = scale_size(5)
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
            }}
            QLabel {{
                color: #eee;
                font-size: {0}px;
                padding: {1}px;
            }}
        """.format(font_size, scale_size(10)))
        
        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Delete group '{0}'?".format(group_name))
        label.setWordWrap(True)
        layout.addWidget(label)
        
        button_layout = QtWidgets.QHBoxLayout()
        
        yes_btn = QtWidgets.QPushButton("Yes")
        yes_btn.setFixedHeight(button_height)
        yes_btn.setStyleSheet("""
            QPushButton {{
                background: #e74c3c;
                border: none;
                color: #fff;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #c0392b;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        yes_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        no_btn = QtWidgets.QPushButton("No")
        no_btn.setFixedHeight(button_height)
        no_btn.setStyleSheet("""
            QPushButton {{
                background: #555;
                border: none;
                color: #eee;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #666;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        no_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        layout.addLayout(button_layout)
        
        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            groups_data = load_groups_data()
            groups = groups_data.get('groups', ['Default'])
            
            if group_name in groups:
                groups.remove(group_name)
                
            if groups_data.get('current_group') == group_name:
                groups_data['current_group'] = 'Default'
                self.current_group = 'Default'
                
            groups_data['groups'] = groups
            save_groups_data(groups_data)
            
            group_node = get_group_network_node(group_name)
            if cmds.objExists(group_node):
                try:
                    cmds.delete(group_node)
                except:
                    pass
            
            self.load_groups()
    
    def on_switch_group_from_menu(self):
        current_item = self.groups_list.currentItem()
        if current_item:
            self.on_switch_group(current_item)
    
    def on_switch_group_no_close(self, item):
        if not item:
            return
            
        group_name = item.text()
        
        groups_data = load_groups_data()
        groups_data['current_group'] = group_name
        save_groups_data(groups_data)
        
        self.current_group = group_name
        self.group_switched.emit(group_name)
        self.load_groups()
        # Don't close! That's the whole point of "no_close"
    
    def on_switch_group_no_close_from_list(self):
        """Called when double-clicking a group - switch without closing"""
        current_item = self.groups_list.currentItem()
        if current_item:
            self.on_switch_group_no_close(current_item)
    
    def on_switch_to_selected_group(self):
        selected_items = self.groups_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        group_name = item.text()
        
        groups_data = load_groups_data()
        groups_data['current_group'] = group_name
        save_groups_data(groups_data)
        
        self.current_group = group_name
        self.group_switched.emit(group_name)
        self.load_groups()
    
    def on_switch_group(self, item):
        if not item:
            return
            
        group_name = item.text()
        
        groups_data = load_groups_data()
        groups_data['current_group'] = group_name
        save_groups_data(groups_data)
        
        self.group_switched.emit(group_name)
        self.close()
    
    def on_set_dropped(self, set_name, target_group):
        """Handle set drop - emit signal to parent"""
        if target_group == self.current_group:
            cmds.warning("Set '{0}' is already in group '{1}'.".format(set_name, target_group))
            return
        
        self.set_transfer_requested.emit(set_name, target_group)
        cmds.inViewMessage(amg="'{0}' moved to '{1}'".format(set_name, target_group), pos='midCenter', fade=True)

    
    def enterEvent(self, event):
        """Mouse entered - fade to full opacity"""
        if hasattr(self, 'fade_anim'):
            self.fade_anim.stop()
            self.fade_anim.setDuration(120)
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.start()
        super(GroupSetsDialog, self).enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse left - fade to subtle transparency"""
        if hasattr(self, 'fade_anim'):
            self.fade_anim.stop()
            self.fade_anim.setDuration(500)
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(0.70)
            self.fade_anim.start()
        super(GroupSetsDialog, self).leaveEvent(event)

class GroupRightClickListWidget(QtWidgets.QListWidget):
    rename_requested = QtCore.Signal()
    delete_requested = QtCore.Signal()
    switch_requested = QtCore.Signal()
    switch_no_close_requested = QtCore.Signal()  # For double-click
    set_dropped = QtCore.Signal(str, str)  # (set_name, target_group)
    
    def __init__(self, parent=None):
        super(GroupRightClickListWidget, self).__init__(parent)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to switch to group without closing"""
        item = self.itemAt(get_event_pos(event))
        if item:
            self.switch_no_close_requested.emit()
        else:
            super(GroupRightClickListWidget, self).mouseDoubleClickEvent(event)
        
    def mousePressEvent(self, event):
        item = self.itemAt(get_event_pos(event))
        if item is None:
            event.ignore()
        else:
            super(GroupRightClickListWidget, self).mousePressEvent(event)

    def contextMenuEvent(self, event):
        item = self.itemAt(get_event_pos(event))
        if not item:
            return
            
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(get_context_menu_style())
        
        switch_action = menu.addAction("Switch to Group")
        rename_action = menu.addAction("Rename")
        delete_action = menu.addAction("Delete")
        
        action = exec_menu(menu, self.mapToGlobal(get_event_pos(event)))
        
        if action == switch_action:
            self.switch_requested.emit()
        elif action == rename_action:
            self.rename_requested.emit()
        elif action == delete_action:
            self.delete_requested.emit()
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            set_name = event.mimeData().text()
            item = self.itemAt(get_event_pos(event))
            
            if item:
                target_group = item.text()
                self.set_dropped.emit(set_name, target_group)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()


class MinimalEsnSelectionTool(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
            super(MinimalEsnSelectionTool, self).__init__(parent)
            self.setObjectName("PickifyUIWindow")
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
            
            if is_macos():
                self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            
            maya_version = get_maya_version()
            if maya_version >= 2020:
                self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            else:
                self.setStyleSheet("QDialog { background-color: rgb(34, 34, 34); }")
            
            width = scale_size(120)
            self.setMinimumSize(width, scale_size(100))
            
            # Flag to prevent selection on double-click
            self.double_click_pending = False
            
            # Migrate old sets from previous Pickify version
            migrate_old_sets_to_default_group()
            
            groups_data = load_groups_data()
            self.current_group = groups_data.get('current_group', 'Default')
            
            self.ui_mode = get_ui_mode()
            
            self.data = load_group_sets(self.current_group)
            self.metadata = load_group_metadata(self.current_group)
            
            # Migrate colors to new dark gray (#303030)
            old_gray = "#95a5a6"
            new_gray = "#303030"
            migrated = False
            
            # Update all sets to have the new dark gray color
            for set_name in self.data.keys():
                # Initialize metadata for set if doesn't exist
                if set_name not in self.metadata:
                    self.metadata[set_name] = {}
                
                # If no color or old gray color, set to new dark gray
                if "color" not in self.metadata[set_name]:
                    self.metadata[set_name]["color"] = new_gray
                    migrated = True
                elif self.metadata[set_name]["color"] == old_gray:
                    self.metadata[set_name]["color"] = new_gray
                    migrated = True
            
            # Save if any changes were made
            if migrated:
                save_group_metadata(self.metadata, self.current_group)
            
            # Ensure set_order exists and contains all sets (fix for old scenes)
            if "set_order" not in self.metadata:
                self.metadata["set_order"] = []
            
            # Add any missing sets to set_order (preserves existing order)
            for set_name in self.data.keys():
                if set_name not in self.metadata["set_order"]:
                    self.metadata["set_order"].append(set_name)
            
            # Remove any sets from set_order that no longer exist
            self.metadata["set_order"] = [s for s in self.metadata["set_order"] if s in self.data]
            
            # Save the fixed set_order
            if "set_order" in self.metadata:
                save_group_metadata(self.metadata, self.current_group)
            
            
            # Sync all sets to main network node for hotkey compatibility
            sync_all_sets_to_main_network_node()
            
            self._drag_pos = None
            self._resize_edge = None
            self._resize_start_geo = None
            self._resize_start_pos = None
            self.selection_job = None
            self.new_scene_job = None
            self.scene_opened_job = None
            
            if self.ui_mode == "horizontal":
                self.setup_ui_horizontal()
                self.setMinimumSize(scale_size(90), scale_size(50))
            else:
                self.setup_ui()
            self.refresh_list()
            if self.ui_mode == "horizontal":
                saved_size = load_horizontal_ui_size()
                if saved_size and self.list_widget.count() > 0:
                    self.resize(saved_size[0], saved_size[1])
                else:
                    self.fit_horizontal_to_content()
            self.restore_position()
            self.update_selection_count()
            
            # Setup opacity animations using windowOpacity (compatible with Maya 2026)
            self.setWindowOpacity(0.0)  # Start invisible
            
            # Fade in animation on startup
            self.fade_in_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
            self.fade_in_anim.setDuration(400)  # 400ms fade in
            self.fade_in_anim.setStartValue(0.0)  # Start invisible
            self.fade_in_anim.setEndValue(1.0)  # Full opacity
            self.fade_in_anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            
            # Fade out/in animation for mouse leave/enter
            self.fade_anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
            self.fade_anim.setDuration(300)  # 300ms smooth fade
            self.fade_anim.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
            
            # Track mouse for fade effect
            self.setMouseTracking(True)
            self.is_mouse_over = True
            
            # Start fade-in animation
            self.fade_in_anim.start()
            
            self.start_selection_job()
            self.start_new_scene_job()
            
            # Start persistent sync job that works even when UI is closed
            start_persistent_sync_job()

    def start_new_scene_job(self):
        if self.new_scene_job:
            cmds.scriptJob(kill=self.new_scene_job, force=True)
        
        try:
            self.new_scene_job = cmds.scriptJob(event=["NewSceneOpened", self.reload_scene_data])
            self.scene_opened_job = cmds.scriptJob(event=["SceneOpened", self.reload_scene_data])
        except Exception:
            pass
    
    def reload_scene_data(self):
        groups_data = load_groups_data()
        self.current_group = groups_data.get('current_group', 'Default')
        self.data = load_group_sets(self.current_group)
        self.metadata = load_group_metadata(self.current_group)
        
        # Sync all sets to main network node for hotkey compatibility
        sync_all_sets_to_main_network_node()
        
        self.refresh_list()
        self.update_selection_count()
        self.highlight_matching_sets()
    
    def start_selection_job(self):
        if self.selection_job:
            cmds.scriptJob(kill=self.selection_job, force=True)
        
        try:
            self.selection_job = cmds.scriptJob(event=["SelectionChanged", self.on_selection_changed])
        except Exception:
            self.selection_timer = QtCore.QTimer()
            self.selection_timer.timeout.connect(self.on_selection_changed)
            self.selection_timer.start(100)
    
    def on_selection_changed(self):
        self.update_selection_count()
        self.highlight_matching_sets()
        
        selected = cmds.ls(selection=True, long=True)
        
        # Always check if we should clear button selection
        selected_items = self.list_widget.selectedItems()
        
        if not selected:
            # No Maya selection - clear any selected buttons
            if selected_items:
                self.list_widget.clearSelection()
                self.list_widget.viewport().update()
        elif selected_items:
            # Maya has selection AND button is selected
            # Check if they match
            should_clear = True
            
            for selected_item in selected_items:
                set_name = selected_item.text()
                if set_name in self.data:
                    # Get set objects
                    set_objects = [obj for obj in self.data[set_name] if cmds.objExists(obj)]
                    
                    # Convert to long names for comparison
                    set_long = set()
                    for obj in set_objects:
                        try:
                            long_names = cmds.ls(obj, long=True)
                            if long_names:
                                set_long.add(long_names[0])
                        except:
                            pass
                    
                    # Compare with Maya selection
                    maya_long = set(selected)
                    
                    # If they match, don't clear
                    if maya_long == set_long:
                        should_clear = False
                        break
            
            # Clear button if selection doesn't match
            if should_clear:
                self.list_widget.clearSelection()
                self.list_widget.viewport().update()
    
    def highlight_matching_sets(self):
        """
        Clean highlighting logic:
        - Get current Maya selection
        - For each set, check if it matches
        - Update highlighting accordingly
        - Only refresh if something changed (preserve hover)
        """
        # Get current Maya selection (both long and short names for comparison)
        maya_selection_long = set(cmds.ls(selection=True, long=True) or [])
        maya_selection_short = set(cmds.ls(selection=True) or [])
        
        # Track which sets match
        matches = {}  # set_name: "full_match" or "partial_match" or None
        
        # Check each set against Maya selection
        for set_name, set_objects in self.data.items():
            # Get valid objects from this set
            valid_set_objects = [obj for obj in set_objects if cmds.objExists(obj)]
            if not valid_set_objects:
                matches[set_name] = None
                continue
            
            # Convert set objects to long names for comparison
            set_long = set()
            for obj in valid_set_objects:
                try:
                    long_name = cmds.ls(obj, long=True)
                    if long_name:
                        set_long.add(long_name[0])
                except:
                    pass
            
            if not set_long:
                matches[set_name] = None
                continue
            
            # Check for matches
            if maya_selection_long == set_long:
                # Exact match - all objects in set are selected, nothing else
                matches[set_name] = "full_match"
            elif set_long.intersection(maya_selection_long):
                # Partial match - some objects from set are selected
                matches[set_name] = "partial_match"
            else:
                # No match
                matches[set_name] = None
        
        # Update items and track if anything changed
        something_changed = False
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_name = item.text()
            
            # Get the match type for this set
            old_match_type = item.data(QtCore.Qt.UserRole)
            new_match_type = matches.get(item_name, None)
            
            # Only update if changed
            if old_match_type != new_match_type:
                item.setData(QtCore.Qt.UserRole, new_match_type)
                something_changed = True
        
        # Only force refresh if something actually changed
        # This preserves hover state when selection doesn't affect any sets
        if something_changed:
            self.list_widget.viewport().update()



    def stop_selection_job(self):
        try:
            if self.selection_job:
                cmds.scriptJob(kill=self.selection_job, force=True)
                self.selection_job = None
        except Exception:
            pass
        
        try:
            if self.new_scene_job:
                cmds.scriptJob(kill=self.new_scene_job, force=True)
                self.new_scene_job = None
        except Exception:
            pass
        
        try:
            if self.scene_opened_job:
                cmds.scriptJob(kill=self.scene_opened_job, force=True)
                self.scene_opened_job = None
        except Exception:
            pass
        
        if hasattr(self, 'selection_timer'):
            self.selection_timer.stop()

    def restore_position(self):
        saved_pos = load_window_position()
        if saved_pos:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen().geometry()
            else:
                screen = QtWidgets.QApplication.desktop().screenGeometry()
            
            window_width = scale_size(120)
            window_height = scale_size(350)
            
            if (saved_pos.x() >= 0 and saved_pos.y() >= 0 and 
                saved_pos.x() < screen.width() - window_width and 
                saved_pos.y() < screen.height() - window_height):
                self.move(saved_pos)

    def update_selection_count(self):
        try:
            selected = cmds.ls(selection=True)
            count = len(selected) if selected else 0
            self.selection_count.setText(str(count))
            
            font_size = scale_font_size(9)
            
            if count == 0:
                color = "#555"
                text_color = "#888"
            elif count <= 20:
                color = "#27ae60"
                text_color = "#fff"
            elif count <= 50:
                color = "#f39c12"
                text_color = "#222"
            else:
                color = "#e74c3c"
                text_color = "#fff"
                
            self.selection_count.setStyleSheet("""
                QLabel {{
                    background-color: {0};
                    color: {1};
                    border-radius: 3px;
                    font-size: {2}px;
                    font-weight: 600;
                }}
            """.format(color, text_color, font_size))
        except Exception:
            self.selection_count.setText("?")

    def closeEvent(self, event):
        self.stop_selection_job()
        save_window_position(self.pos())
        if self.ui_mode == "horizontal":
            save_horizontal_ui_size(self.width(), self.height())
        event.accept()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QtWidgets.QWidget()
        border_radius = scale_size(12)
        self.container.setStyleSheet("""
            QWidget {{
                background-color: rgba(34, 34, 34, 240);
                border-radius: {0}px;
                border: 1px solid rgba(68, 68, 68, 180);
            }}
        """.format(border_radius))
        
        margin = scale_size(8)
        spacing = scale_size(4)
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(margin, margin, margin, margin)
        container_layout.setSpacing(spacing)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(spacing)
        
        count_size = scale_size(20)
        count_height = scale_size(16)
        font_size = scale_font_size(9)
        
        self.selection_count = QtWidgets.QLabel("0")
        self.selection_count.setFixedSize(count_size, count_height)
        self.selection_count.setAlignment(QtCore.Qt.AlignCenter)
        self.selection_count.setStyleSheet("""
            QLabel {{
                background-color: #555;
                color: #888;
                border-radius: 3px;
                font-size: {0}px;
                font-weight: 600;
            }}
        """.format(font_size))
        header_layout.addWidget(self.selection_count)
        
        header_layout.addStretch()

        exit_size = scale_size(16)
        exit_font_size = scale_font_size(12)
        
        self.exit_btn = QtWidgets.QPushButton("X")
        self.exit_btn.setFixedSize(exit_size, exit_size)
        self.exit_btn.setStyleSheet("""
            QPushButton {{
                background: rgba(243, 156, 18, 200);
                border: none;
                color: #fff;
                font-size: {0}px;
                font-weight: bold;
                border-radius: 3px;
            }}
            QPushButton:hover {{ background: rgba(243, 156, 18, 255); }}
        """.format(exit_font_size))
        self.exit_btn.clicked.connect(self.close)
        header_layout.addWidget(self.exit_btn)

        container_layout.addLayout(header_layout)

        button_layout = QtWidgets.QVBoxLayout()
        button_layout.setSpacing(scale_size(3))
        
        button_height = scale_size(20)
        button_font_size = scale_font_size(9)
        button_radius = scale_size(4)
        
        self.add_btn = QtWidgets.QPushButton("CREATE SET")
        self.add_btn.setFixedHeight(button_height)
        self.add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {{
                background: rgba(180, 135, 25, 230);
                border: 1px solid rgba(150, 112, 20, 230);
                border-radius: {0}px;
                color: #fff;
                font-size: {1}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ 
                background: rgba(200, 149, 26, 245);
            }}
            QPushButton:pressed {{ 
                background: rgba(212, 161, 38, 255);
            }}
        """.format(button_radius, button_font_size))
        self.add_btn.clicked.connect(self.create_set)
        button_layout.addWidget(self.add_btn)
        
        container_layout.addLayout(button_layout)
        
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_margin = scale_size(4)
        separator.setStyleSheet("""
            QFrame {{
                color: rgba(102, 102, 102, 120);
                background-color: rgba(102, 102, 102, 120);
                margin: {0}px 0px;
            }}
        """.format(separator_margin))
        container_layout.addWidget(separator)

        list_height = scale_size(250)
        list_font_size = scale_font_size(12)
        item_radius = scale_size(4)
        item_padding = scale_size(4)
        item_margin = scale_size(3)
        item_height = scale_size(18)
        
        self.list_widget = EsnRightClickListWidget()
        self.list_widget.setFixedHeight(list_height)
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Need selection for drag
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)  # Allow external drag
        self.list_widget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.list_widget.setItemDelegate(ColorItemDelegate())
        self.list_widget.setMouseTracking(True)  # Enable mouse tracking for hover
        self.list_widget.viewport().setMouseTracking(True)  # Also on viewport
        self.list_widget.setFocusPolicy(QtCore.Qt.NoFocus)  # Disable focus rectangle
        self.list_widget.current_group = self.current_group  # Store current group for dragging
        self.list_widget.current_ui_mode = self.ui_mode
        self.list_widget.model().rowsMoved.connect(self.save_order)
        self.list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_widget.setStyleSheet("""
            QListWidget {{
                background: transparent;
                border: none;
                color: #eee;
                font-size: {0}px;
                font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
                font-weight: normal;
                letter-spacing: 0.5px;
                outline: none;
                show-decoration-selected: 0;
            }}
            QListWidget::item {{
                border: none;
                background: rgba(55, 55, 55, 255);
                border-radius: 3px;
                padding: {2}px 6px;
                margin: 1px;
                min-height: {4}px;
                outline: none;
            }}
            QListWidget::item:hover {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:active {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:!active {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:focus {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(80, 80, 80, 80);
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(100, 100, 100, 120);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """.format(list_font_size, item_radius, item_padding, item_margin, item_height))
        self.list_widget.itemClicked.connect(self.handle_item_click)
        self.list_widget.itemDoubleClicked.connect(self.rename_set)
        
        self.list_widget.delete_requested.connect(self.delete_multiple_sets)
        self.list_widget.add_selection_requested.connect(self.add_to_set)
        self.list_widget.remove_selection_requested.connect(self.remove_from_set)
        self.list_widget.update_contents_requested.connect(self.update_set_contents)
        self.list_widget.clear_all_requested.connect(self.clear_all_sets)
        self.list_widget.export_requested.connect(self.export_sets)
        self.list_widget.select_requested.connect(self.select_add_to_maya)
        self.list_widget.remove_select_requested.connect(self.remove_select_from_maya)
        self.list_widget.import_requested.connect(self.import_sets)
        self.list_widget.change_namespace_all_requested.connect(self.change_namespace_all_sets)
        self.list_widget.group_sets_requested.connect(self.open_group_sets_dialog)
        self.list_widget.auto_select_all_ctrls_requested.connect(self.auto_select_all_ctrls)
        self.list_widget.create_all_set_requested.connect(self.create_all_set)
        self.list_widget.disable_hotkey_requested.connect(self.disable_hotkey_for_set)
        self.list_widget.enable_hotkey_requested.connect(self.enable_hotkey_for_set)
        self.list_widget.rename_requested.connect(self.rename_set)
        self.list_widget.toggle_ui_mode_requested.connect(self.on_toggle_ui_mode)
        
        container_layout.addWidget(self.list_widget)
        main_layout.addWidget(self.container)

    def setup_ui_horizontal(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)

        self.container = QtWidgets.QWidget()
        border_radius = scale_size(10)
        self.container.setStyleSheet("""
            QWidget {{
                background-color: #222222;
                border-radius: {0}px;
                border: none;
            }}
        """.format(border_radius))
        main_layout.addWidget(self.container)

        margin = scale_size(6)
        vmargin = scale_size(5)
        spacing = scale_size(3)
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(margin, vmargin, margin, vmargin)
        container_layout.setSpacing(spacing)
        container_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setSpacing(scale_size(4))

        add_width = scale_size(22)
        add_height = scale_size(16)
        add_font_size = scale_font_size(11)

        self.add_btn = QtWidgets.QPushButton("+")
        self.add_btn.setFixedSize(add_width, add_height)
        self.add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_btn.setStyleSheet("""
            QPushButton {{
                background: #b48719;
                border: none;
                border-radius: 3px;
                color: #fff;
                font-size: {0}px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background: #c8951a; }}
            QPushButton:pressed {{ background: #d4a126; }}
        """.format(add_font_size))
        self.add_btn.clicked.connect(self.create_set)
        header_layout.addWidget(self.add_btn)

        count_size = scale_size(20)
        count_height = scale_size(14)
        font_size = scale_font_size(8)

        self.selection_count = QtWidgets.QLabel("0")
        self.selection_count.setFixedSize(count_size, count_height)
        self.selection_count.setAlignment(QtCore.Qt.AlignCenter)
        self.selection_count.setStyleSheet("""
            QLabel {{
                background-color: #555;
                color: #888;
                border-radius: 3px;
                font-size: {0}px;
                font-weight: 600;
            }}
        """.format(font_size))
        header_layout.addWidget(self.selection_count)

        header_layout.addStretch()

        exit_size = scale_size(14)
        exit_font_size = scale_font_size(9)

        self.exit_btn = QtWidgets.QPushButton("X")
        self.exit_btn.setFixedSize(exit_size, exit_size)
        self.exit_btn.setStyleSheet("""
            QPushButton {{
                background: #f39c12;
                border: none;
                color: #fff;
                font-size: {0}px;
                font-weight: bold;
                border-radius: 3px;
            }}
            QPushButton:hover {{ background: #ffab2e; }}
        """.format(exit_font_size))
        self.exit_btn.clicked.connect(self.close)
        header_layout.addWidget(self.exit_btn)

        container_layout.addLayout(header_layout)

        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(scale_size(5))

        list_font_size = scale_font_size(12)
        item_radius = scale_size(4)
        item_padding_v = scale_size(6)
        item_padding_h = scale_size(14)

        self.list_widget = EsnRightClickListWidget()
        self.list_widget.setViewMode(QtWidgets.QListWidget.ListMode)
        self.list_widget.setFlow(QtWidgets.QListWidget.LeftToRight)
        self.list_widget.setWrapping(True)
        self.list_widget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setSpacing(scale_size(2))
        self.list_widget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # Need selection for drag
        self.list_widget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)  # Allow external drag
        self.list_widget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.list_widget.setItemDelegate(ColorItemDelegate())
        self.list_widget.setMouseTracking(True)  # Enable mouse tracking for hover
        self.list_widget.viewport().setMouseTracking(True)  # Also on viewport
        self.list_widget.setFocusPolicy(QtCore.Qt.NoFocus)  # Disable focus rectangle
        self.list_widget.current_group = self.current_group  # Store current group for dragging
        self.list_widget.current_ui_mode = self.ui_mode
        self.list_widget.model().rowsMoved.connect(self.save_order)
        self.list_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.list_widget.setStyleSheet("""
            QListWidget {{
                background: transparent;
                border: none;
                color: #eee;
                font-size: {0}px;
                font-family: "Segoe UI", "San Francisco", "Helvetica Neue", Arial, sans-serif;
                font-weight: normal;
                letter-spacing: 0.5px;
                outline: none;
                show-decoration-selected: 0;
            }}
            QListWidget::item {{
                border: none;
                background: rgba(55, 55, 55, 255);
                border-radius: {1}px;
                padding: {2}px {3}px;
                margin: 2px;
                outline: none;
            }}
            QListWidget::item:hover {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:active {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:selected:!active {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item:focus {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 4px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(80, 80, 80, 80);
                border-radius: 2px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(100, 100, 100, 120);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """.format(list_font_size, item_radius, item_padding_v, item_padding_h))
        self.list_widget.itemClicked.connect(self.handle_item_click)
        self.list_widget.itemDoubleClicked.connect(self.rename_set)
        
        self.list_widget.delete_requested.connect(self.delete_multiple_sets)
        self.list_widget.add_selection_requested.connect(self.add_to_set)
        self.list_widget.remove_selection_requested.connect(self.remove_from_set)
        self.list_widget.update_contents_requested.connect(self.update_set_contents)
        self.list_widget.clear_all_requested.connect(self.clear_all_sets)
        self.list_widget.export_requested.connect(self.export_sets)
        self.list_widget.select_requested.connect(self.select_add_to_maya)
        self.list_widget.remove_select_requested.connect(self.remove_select_from_maya)
        self.list_widget.import_requested.connect(self.import_sets)
        self.list_widget.change_namespace_all_requested.connect(self.change_namespace_all_sets)
        self.list_widget.group_sets_requested.connect(self.open_group_sets_dialog)
        self.list_widget.auto_select_all_ctrls_requested.connect(self.auto_select_all_ctrls)
        self.list_widget.create_all_set_requested.connect(self.create_all_set)
        self.list_widget.disable_hotkey_requested.connect(self.disable_hotkey_for_set)
        self.list_widget.enable_hotkey_requested.connect(self.enable_hotkey_for_set)
        self.list_widget.rename_requested.connect(self.rename_set)
        self.list_widget.toggle_ui_mode_requested.connect(self.on_toggle_ui_mode)

        content_layout.addWidget(self.list_widget, 1)

        container_layout.addLayout(content_layout, 1)

        self.resize(self.minimumWidth(), self.minimumHeight())

    def refresh_list(self):
        self.list_widget.clear()
        
        set_order = []
        if "set_order" in self.metadata:
            set_order = self.metadata["set_order"]
        
        ordered_keys = []
        for name in set_order:
            if name in self.data:
                ordered_keys.append(name)
        
        for name in self.data.keys():
            if name not in ordered_keys:
                ordered_keys.append(name)
        
        for name in ordered_keys:
            item = QtWidgets.QListWidgetItem(name)
            if name in self.metadata and "color" in self.metadata[name]:
                color_hex = self.metadata[name]["color"]
                item.setData(QtCore.Qt.UserRole + 1, color_hex)
            self.list_widget.addItem(item)
        
        self.adjust_width_to_content() if self.ui_mode != "horizontal" else self.adjust_size_horizontal()
        self.highlight_matching_sets()
    
    def adjust_size_horizontal(self):
        """In horizontal mode the window is freely resizable by the user, so
        we intentionally do not force a fixed size here on every refresh."""
        pass

    def is_last_item_visible_horizontal(self):
        """Check whether the most recently added set is fully visible within
        the current window size, without changing anything."""
        if self.list_widget.count() == 0:
            return True
        self.list_widget.doItemsLayout()
        last_index = self.list_widget.model().index(self.list_widget.count() - 1, 0)
        last_rect = self.list_widget.visualRect(last_index)
        viewport_rect = self.list_widget.viewport().rect()
        if last_rect.width() <= 0 or last_rect.height() <= 0:
            return False
        if last_rect.right() > viewport_rect.width():
            return False
        if last_rect.bottom() > viewport_rect.height():
            return False
        return True

    def grow_horizontal_to_show_all(self):
        """Grow (never shrink, never change width) the window height so all
        sets are visible, preserving whatever row layout the user has already
        resized into. Used when a newly created set overflows the view."""
        if self.list_widget.count() == 0:
            return
        self.list_widget.doItemsLayout()
        last_index = self.list_widget.model().index(self.list_widget.count() - 1, 0)
        last_rect = self.list_widget.visualRect(last_index)
        spacing = self.list_widget.spacing()
        needed_list_height = last_rect.y() + last_rect.height() + spacing

        current_list_height = self.list_widget.height()
        if needed_list_height <= current_list_height:
            return

        extra_height_needed = needed_list_height - current_list_height
        new_height = self.height() + extra_height_needed
        new_height = max(new_height, self.minimumHeight())
        self.resize(self.width(), new_height)

    def fit_horizontal_to_content(self):
        """Shrink/grow the horizontal window once to exactly fit the current
        sets, with no leftover empty space. Called only right after the UI is
        (re)built, not on every refresh, so manual resizing afterward sticks.
        Measures Qt's own rendered item layout rather than estimating pixel
        sizes, so it matches exactly regardless of font/padding/letter-spacing."""
        if self.list_widget.count() == 0:
            empty_width = max(self.minimumWidth(), scale_size(240))
            empty_height = max(self.minimumHeight(), scale_size(60))
            self.resize(empty_width, empty_height)
            return

        container_margin_h = scale_size(6) * 2
        container_margin_v = scale_size(5) * 2
        header_height = scale_size(16) + scale_size(3)
        spacing = self.list_widget.spacing()

        screen_geo = None
        try:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen()
                if screen:
                    screen_geo = screen.geometry()
            else:
                app = QtWidgets.QApplication.instance()
                if app:
                    desktop = app.desktop()
                    if desktop:
                        screen_geo = desktop.screenGeometry()
        except Exception:
            screen_geo = None

        if screen_geo:
            max_row_width = int(screen_geo.width() * 0.6)
        else:
            max_row_width = scale_size(900)

        last_row = self.list_widget.count() - 1
        last_index = self.list_widget.model().index(last_row, 0)

        prev_min = self.list_widget.minimumWidth()
        prev_max = self.list_widget.maximumWidth()

        huge_width = scale_size(6000)
        self.list_widget.setFixedWidth(huge_width)
        self.list_widget.doItemsLayout()

        last_rect = self.list_widget.visualRect(last_index)
        single_row_width = last_rect.x() + last_rect.width() + spacing
        single_row_height = last_rect.height() + (spacing * 2)

        if single_row_width + container_margin_h <= max_row_width:
            final_width = single_row_width + container_margin_h
            final_height = header_height + single_row_height + container_margin_v
        else:
            final_width = max_row_width
            self.list_widget.setFixedWidth(final_width - container_margin_h)
            self.list_widget.doItemsLayout()
            last_rect = self.list_widget.visualRect(last_index)
            total_height = last_rect.y() + last_rect.height() + spacing
            final_height = header_height + total_height + container_margin_v

        self.list_widget.setMinimumWidth(prev_min)
        self.list_widget.setMaximumWidth(prev_max)

        final_width = max(final_width, self.minimumWidth())
        final_height = max(final_height, self.minimumHeight())

        self.resize(final_width, final_height)
        self.list_widget.doItemsLayout()

    def adjust_width_to_content(self):
        """Adjust window width and height to fit content."""
        item_count = self.list_widget.count()
        
        # Fixed heights for components
        button_height = scale_size(32)  # CREATE SET button
        header_height = scale_size(32)  # Header with X button and margins
        separator_height = scale_size(4)  # Separator line
        list_area_height = scale_size(250)  # Fixed list area (doesn't grow!)
        bottom_padding = scale_size(12)  # Bottom margin
        
        # Total height is FIXED - doesn't change with items
        total_height = header_height + button_height + separator_height + list_area_height + bottom_padding
        self.setFixedHeight(total_height)
        
        # Adjust width
        if item_count == 0:
            self.setFixedWidth(scale_size(120))
            return
        
        # Calculate the width needed for the longest text
        font_metrics = QtGui.QFontMetrics(self.list_widget.font())
        max_width = 0
        
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            # Use horizontalAdvance for PySide6, fallback to width for PySide2
            if hasattr(font_metrics, 'horizontalAdvance'):
                text_width = font_metrics.horizontalAdvance(item.text())
            else:
                text_width = font_metrics.width(item.text())
            if text_width > max_width:
                max_width = text_width
        
        # Add padding for margins, borders, and scrollbar
        padding = scale_size(60)  # Account for margins, padding, and vertical scrollbar
        needed_width = max_width + padding
        
        # Set minimum and cap maximum width
        min_width = scale_size(120)
        max_allowed_width = scale_size(250)
        
        final_width = max(min_width, min(needed_width, max_allowed_width))
        
        self.setFixedWidth(final_width)

    def save_order(self):
        order = []
        for i in range(self.list_widget.count()):
            order.append(self.list_widget.item(i).text())
        self.metadata["set_order"] = order
        save_group_metadata(self.metadata, self.current_group)

    def handle_item_click(self, item):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        set_name = item.text()

        if set_name not in self.data:
            return

        set_objects = [obj for obj in self.data[set_name] if cmds.objExists(obj)]
        if not set_objects:
            cmds.warning("No valid objects found in set: {0}".format(set_name))
            return

        if modifiers == QtCore.Qt.ShiftModifier:
            cmds.select(set_objects, add=True)

        elif modifiers == QtCore.Qt.ControlModifier:
            current_selection = cmds.ls(selection=True, long=True) or []
            new_selection = [obj for obj in current_selection if obj not in set_objects]
            if new_selection:
                cmds.select(new_selection, replace=True)
            else:
                cmds.select(clear=True)

        else:
            cmds.select(set_objects, replace=True)

        # Clear the list widget selection so orange highlight comes from match_type only
        # This prevents the button from staying "selected" in the list widget
        QtCore.QTimer.singleShot(50, self.list_widget.clearSelection)
        
        cmds.setFocus("MayaWindow")

    def create_set(self):
            sel = cmds.ls(selection=True, long=True)
            if not sel:
                cmds.warning("Nothing selected to create set with.")
                return

            sel_set = set(sel)
            for existing_set_name, existing_set_objects in self.data.items():
                if set(existing_set_objects) == sel_set:
                    dialog = QtWidgets.QDialog(self)
                    dialog.setWindowTitle("Duplicate Set")
                    dialog.setWindowModality(QtCore.Qt.ApplicationModal)
                    dialog.setFixedSize(scale_size(320), scale_size(120))
                    
                    font_size = scale_font_size(12)
                    button_font_size = scale_font_size(11)
                    button_height = scale_size(30)
                    border_radius = scale_size(4)
                    
                    dialog.setStyleSheet("""
                        QDialog {{
                            background-color: #222;
                            color: #eee;
                        }}
                        QLabel {{
                            color: #eee;
                            font-size: {0}px;
                            padding: {1}px;
                        }}
                    """.format(font_size, scale_size(10)))

                    layout = QtWidgets.QVBoxLayout(dialog)
                    label = QtWidgets.QLabel("You already have a set with these contents.")
                    label.setWordWrap(True)
                    layout.addWidget(label)

                    button_layout = QtWidgets.QHBoxLayout()
                    
                    ok_btn = QtWidgets.QPushButton("OK")
                    ok_btn.setFixedHeight(button_height)
                    ok_btn.setStyleSheet("""
                        QPushButton {{
                            background: #f39c12;
                            border: none;
                            color: #222;
                            font-size: {0}px;
                            border-radius: {1}px;
                            font-weight: 600;
                            padding: {2}px {3}px;
                        }}
                        QPushButton:hover {{
                            background: #e67e22;
                        }}
                        QPushButton:pressed {{
                            background: #d35400;
                        }}
                    """.format(button_font_size, border_radius, scale_size(5), scale_size(15)))
                    ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    
                    button_layout.addWidget(ok_btn)
                    layout.addLayout(button_layout)

                    ok_btn.clicked.connect(dialog.accept)
                    dialog.exec_()
                    return

            base_name = "set"
            index = 1
            while "{0}_{1}".format(base_name, index) in self.data:
                index += 1
            name = "{0}_{1}".format(base_name, index)

            self.data[name] = sel
            
            # Set default color for new sets
            if name not in self.metadata:
                self.metadata[name] = {}
            self.metadata[name]["color"] = "#303030"
            
            # Add new set to the TOP of set_order (index 0)
            if "set_order" not in self.metadata:
                self.metadata["set_order"] = []
            if name not in self.metadata["set_order"]:
                self.metadata["set_order"].insert(0, name)  # Insert at beginning!
            
            save_group_sets(self.data, self.current_group)
            save_group_metadata(self.metadata, self.current_group)
            self.refresh_list()
            if self.ui_mode == "horizontal" and not self.is_last_item_visible_horizontal():
                self.grow_horizontal_to_show_all()
            
            QtCore.QTimer.singleShot(0, self.highlight_matching_sets)
            
            self.list_widget.clearSelection()
            cmds.setFocus("MayaWindow")

    def create_all_set(self):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected to create All Controls set with.")
            return
        
        self.data["All_Ctrls"] = sel
        
        # Set default dark grey color for ALL_Ctrls
        if "All_Ctrls" not in self.metadata:
            self.metadata["All_Ctrls"] = {}
        self.metadata["All_Ctrls"]["color"] = "#373737"  # Dark grey like normal sets
        
        # Add All_Ctrls to the TOP of set_order
        if "set_order" not in self.metadata:
            self.metadata["set_order"] = []
        if "All_Ctrls" not in self.metadata["set_order"]:
            self.metadata["set_order"].insert(0, "All_Ctrls")
        
        save_group_sets(self.data, self.current_group)
        save_group_metadata(self.metadata, self.current_group)
        self.refresh_list()
        if self.ui_mode == "horizontal" and not self.is_last_item_visible_horizontal():
            self.grow_horizontal_to_show_all()
        
        self.list_widget.clearSelection()
        cmds.setFocus("MayaWindow")

    def rename_set(self, item):
        original_name = item.text()
        
        # For ALL_Ctrls, allow color change but lock the name
        is_all_ctrls = (original_name == "All_Ctrls")
        
        current_color = None
        if original_name in self.metadata and "color" in self.metadata[original_name]:
            current_color = self.metadata[original_name]["color"]
        
        dialog = ColorRenameDialog(original_name, current_color, self)
        
        # If it's ALL_Ctrls, disable the name field
        if is_all_ctrls:
            dialog.line_edit.setText("All_Ctrls (Cannot change name)")
            dialog.line_edit.setEnabled(False)
            dialog.line_edit.setStyleSheet("""
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #888;
                    border: 1px solid #444;
                    border-radius: 3px;
                    padding: 4px;
                    font-size: 13px;
                }
            """)
        
        result = dialog.exec_()
        
        if result == QtWidgets.QDialog.Accepted:
            new_name = dialog.get_name().strip()
            selected_color = dialog.get_color()
            
            if not new_name:
                new_name = original_name
            
            # Only allow renaming if it's not ALL_Ctrls
            if new_name != original_name and not is_all_ctrls:
                if new_name in self.data:
                    cmds.warning("A set with this name already exists.")
                    return
                
                self.data[new_name] = self.data.pop(original_name)
                
                if original_name in self.metadata:
                    self.metadata[new_name] = self.metadata.pop(original_name)
                else:
                    self.metadata[new_name] = {}
                
                # Update set_order to preserve position
                if "set_order" in self.metadata and original_name in self.metadata["set_order"]:
                    index = self.metadata["set_order"].index(original_name)
                    self.metadata["set_order"][index] = new_name
                
                save_group_sets(self.data, self.current_group)
            
            # Always allow color change (even for ALL_Ctrls)
            final_name = new_name if not is_all_ctrls else original_name
            
            if selected_color:
                if final_name not in self.metadata:
                    self.metadata[final_name] = {}
                self.metadata[final_name]["color"] = selected_color
            elif final_name in self.metadata and "color" in self.metadata[final_name]:
                del self.metadata[final_name]["color"]
            
            save_group_metadata(self.metadata, self.current_group)
            self.refresh_list()

    def delete_multiple_sets(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        
        set_names = [item.text() for item in selected_items]
        
        if len(set_names) == 1:
            message = "Delete selection set '{0}'?".format(set_names[0])
            title = "Delete Set"
        else:
            message = "Delete {0} selection sets?".format(len(set_names))
            title = "Delete Multiple Sets"
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setFixedSize(scale_size(320), scale_size(120))
        
        font_size = scale_font_size(12)
        button_font_size = scale_font_size(11)
        button_height = scale_size(30)
        border_radius = scale_size(4)
        padding = scale_size(5)
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
            }}
            QLabel {{
                color: #eee;
                font-size: {0}px;
                padding: {1}px;
            }}
        """.format(font_size, scale_size(10)))

        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel(message)
        label.setWordWrap(True)
        layout.addWidget(label)

        button_layout = QtWidgets.QHBoxLayout()
        
        yes_btn = QtWidgets.QPushButton("Yes")
        yes_btn.setFixedHeight(button_height)
        yes_btn.setStyleSheet("""
            QPushButton {{
                background: #e74c3c;
                border: none;
                color: #fff;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #c0392b;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        yes_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        no_btn = QtWidgets.QPushButton("No")
        no_btn.setFixedHeight(button_height)
        no_btn.setStyleSheet("""
            QPushButton {{
                background: #555;
                border: none;
                color: #eee;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #666;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        no_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        layout.addLayout(button_layout)

        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            for name in set_names:
                self.data.pop(name, None)
                self.metadata.pop(name, None)
            save_group_sets(self.data, self.current_group)
            save_group_metadata(self.metadata, self.current_group)
            self.refresh_list()

    def add_to_set(self, name):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected to add.")
            return
        
        if name in self.data:
            current_set = self.data[name]
            updated_set = list(set(current_set + sel))
            self.data[name] = updated_set
            save_group_sets(self.data, self.current_group)
            self.refresh_list()

    def remove_from_set(self, name):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected to remove.")
            return
        
        if name in self.data:
            current_set = self.data[name]
            updated_set = [obj for obj in current_set if obj not in sel]
            self.data[name] = updated_set
            save_group_sets(self.data, self.current_group)
            self.refresh_list()

    def update_set_contents(self, name):
        sel = cmds.ls(selection=True, long=True)
        if not sel:
            cmds.warning("Nothing selected to update the set with.")
            return
        
        self.data[name] = sel
        save_group_sets(self.data, self.current_group)
        self.refresh_list()

    def select_add_to_maya(self, name):
        if name in self.data:
            existing_objects = [obj for obj in self.data[name] if cmds.objExists(obj)]
            if existing_objects:
                cmds.select(existing_objects, add=True)

    def remove_select_from_maya(self, name):
        if name in self.data:
            current_selection = cmds.ls(selection=True, long=True)
            if not current_selection:
                cmds.warning("Nothing currently selected to remove from.")
                return
            
            set_objects = [obj for obj in self.data[name] if cmds.objExists(obj)]
            new_selection = [obj for obj in current_selection if obj not in set_objects]
            
            if new_selection != current_selection:
                if new_selection:
                    cmds.select(new_selection, replace=True)
                else:
                    cmds.select(clear=True)

    def clear_all_sets(self):
        if not self.data:
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Clear All Sets")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setFixedSize(scale_size(280), scale_size(120))
        
        font_size = scale_font_size(12)
        button_font_size = scale_font_size(11)
        button_height = scale_size(30)
        border_radius = scale_size(4)
        padding = scale_size(5)
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
            }}
            QLabel {{
                color: #eee;
                font-size: {0}px;
                padding: {1}px;
            }}
        """.format(font_size, scale_size(10)))

        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Are you sure you want to delete ALL selection sets?")
        label.setWordWrap(True)
        layout.addWidget(label)

        button_layout = QtWidgets.QHBoxLayout()
        
        yes_btn = QtWidgets.QPushButton("Yes")
        yes_btn.setFixedHeight(button_height)
        yes_btn.setStyleSheet("""
            QPushButton {{
                background: #e74c3c;
                border: none;
                color: #fff;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #c0392b;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        yes_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        no_btn = QtWidgets.QPushButton("No")
        no_btn.setFixedHeight(button_height)
        no_btn.setStyleSheet("""
            QPushButton {{
                background: #555;
                border: none;
                color: #eee;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #666;
            }}
        """.format(button_font_size, border_radius, padding, scale_size(15)))
        no_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        button_layout.addWidget(yes_btn)
        button_layout.addWidget(no_btn)
        layout.addLayout(button_layout)

        yes_btn.clicked.connect(dialog.accept)
        no_btn.clicked.connect(dialog.reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Clear in-memory data
            self.data.clear()
            self.metadata.clear()
            
            # Delete all group network nodes
            groups_data = load_groups_data()
            all_groups = groups_data.get('groups', ['Default'])
            for group in all_groups:
                safe_name = "".join(c for c in group if c.isalnum() or c in ('_', '-')).strip().replace(' ', '_')
                group_node = "esnGroup_{0}".format(safe_name)
                if cmds.objExists(group_node):
                    cmds.delete(group_node)
            
            # Also delete the main esnSelectionSets node if it exists
            if cmds.objExists("esnSelectionSets"):
                cmds.delete("esnSelectionSets")
            
            # Refresh the UI
            self.refresh_list()
            cmds.warning("All sets and network nodes have been cleared from the scene.")

    def export_sets(self):
        if not self.data:
            cmds.warning("No sets to export.")
            return
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Selection Sets", "", "JSON Files (*.json)")
        if path:
            try:
                export_data = {"sets": self.data, "metadata": self.metadata}
                with open(path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                cmds.inViewMessage(amg="Selection sets exported.", pos='midCenter', fade=True)
            except Exception as e:
                cmds.warning("Failed to export selection sets:\n{0}".format(e))

    def import_sets(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Selection Sets", "", "JSON Files (*.json)")
        if path and os.path.isfile(path):
            try:
                with open(path, 'r') as f:
                    imported_data = json.load(f)
                
                if isinstance(imported_data, dict):
                    if "sets" in imported_data and "metadata" in imported_data:
                        sets_to_import = imported_data["sets"]
                        metadata_to_import = imported_data.get("metadata", {})
                    else:
                        sets_to_import = imported_data
                        metadata_to_import = {}
                    
                    for k, v in sets_to_import.items():
                        new_key = k
                        idx = 1
                        while new_key in self.data:
                            new_key = "{0}_{1}".format(k, idx)
                            idx += 1
                        self.data[new_key] = v
                        
                        if k in metadata_to_import:
                            self.metadata[new_key] = metadata_to_import[k]
                    
                    save_group_sets(self.data, self.current_group)
                    save_group_metadata(self.metadata, self.current_group)
                    
                    # Sync to apply hotkey states from imported metadata
                    sync_all_sets_to_main_network_node()
                    
                    self.refresh_list()
                    cmds.inViewMessage(amg="Selection sets imported.", pos='midCenter', fade=True)
                else:
                    cmds.warning("Invalid file format: expected a dictionary of sets.")
            except Exception as e:
                cmds.warning("Failed to import selection sets:\n{0}".format(e))

    def change_namespace_all_sets(self):
        if not self.data:
            cmds.warning("No sets to change namespace for.")
            return

        all_objs = cmds.ls(long=True)
        namespaces = sorted(set([obj.rsplit(":", 1)[0] for obj in all_objs if ":" in obj]))
        namespaces = [ns for ns in namespaces if cmds.namespace(exists=ns)]

        if not namespaces:
            cmds.warning("No namespaces found in the scene.")
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Change Namespace")
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setFixedSize(scale_size(300), scale_size(140))
        
        font_size = scale_font_size(12)
        combo_font_size = scale_font_size(11)
        button_font_size = scale_font_size(11)
        button_height = scale_size(30)
        border_radius = scale_size(4)
        combo_padding = scale_size(5)
        combo_min_height = scale_size(20)
        
        dialog.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
            }}
            QLabel {{
                color: #eee;
                font-size: {0}px;
                padding: {1}px;
            }}
            QComboBox {{
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: {2}px;
                padding: {3}px;
                font-size: {4}px;
                min-height: {5}px;
            }}
            QComboBox:hover {{
                border-color: #f39c12;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: {1}px solid transparent;
                border-right: {1}px solid transparent;
                border-top: {1}px solid #eee;
                margin-right: {1}px;
            }}
        """.format(font_size, scale_size(5), border_radius, combo_padding, combo_font_size, combo_min_height))

        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel("Select new namespace to apply to ALL sets:")
        combo = QtWidgets.QComboBox()
        combo.addItems(namespaces)
        layout.addWidget(label)
        layout.addWidget(combo)

        button_layout = QtWidgets.QHBoxLayout()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedHeight(button_height)
        ok_btn.setStyleSheet("""
            QPushButton {{
                background: #f39c12;
                border: none;
                color: #222;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #e67e22;
            }}
            QPushButton:pressed {{
                background: #d35400;
            }}
        """.format(button_font_size, border_radius, scale_size(5), scale_size(15)))
        ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedHeight(button_height)
        cancel_btn.setStyleSheet("""
            QPushButton {{
                background: #555;
                border: none;
                color: #eee;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
            }}
            QPushButton:hover {{
                background: #666;
            }}
            QPushButton:pressed {{
                background: #444;
            }}
        """.format(button_font_size, border_radius, scale_size(5), scale_size(15)))
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return

        new_namespace = combo.currentText().strip()
        updated_sets_count = 0
        
        for set_name, set_objects in self.data.items():
            updated_objects = []
            for obj in set_objects:
                obj_name = obj.split("|")[-1]
                
                if ":" in obj_name:
                    short_name = obj_name.split(":")[-1]
                    new_obj_name = "{0}:{1}".format(new_namespace, short_name)
                    
                    potential_matches = cmds.ls(new_obj_name, long=True)
                    if potential_matches:
                        updated_objects.append(potential_matches[0])
                else:
                    updated_objects.append(obj)
            
            if updated_objects != set_objects:
                self.data[set_name] = updated_objects
                updated_sets_count += 1

        if updated_sets_count > 0:
            save_group_sets(self.data, self.current_group)
            self.refresh_list()
            self.highlight_matching_sets()
            cmds.inViewMessage(amg="Namespace changed for {0} sets".format(updated_sets_count), pos='topCenter', fade=True)
        else:
            cmds.warning("No matching objects with new namespace found in any sets.")

    def auto_select_all_ctrls(self):
        selected = cmds.ls(selection=True)
        if not selected:
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Auto Select All Ctrls")
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.setFixedSize(scale_size(280), scale_size(120))
            
            font_size = scale_font_size(12)
            button_font_size = scale_font_size(11)
            button_height = scale_size(30)
            border_radius = scale_size(4)
            
            dialog.setStyleSheet("""
                QDialog {{
                    background-color: #222;
                    color: #eee;
                }}
                QLabel {{
                    color: #eee;
                    font-size: {0}px;
                    padding: {1}px;
                }}
            """.format(font_size, scale_size(10)))

            layout = QtWidgets.QVBoxLayout(dialog)
            label = QtWidgets.QLabel("Please select at least one control first.")
            label.setWordWrap(True)
            layout.addWidget(label)

            button_layout = QtWidgets.QHBoxLayout()
            
            ok_btn = QtWidgets.QPushButton("OK")
            ok_btn.setFixedHeight(button_height)
            ok_btn.setStyleSheet("""
                QPushButton {{
                    background: #f39c12;
                    border: none;
                    color: #222;
                    font-size: {0}px;
                    border-radius: {1}px;
                    font-weight: 600;
                    padding: {2}px {3}px;
                }}
                QPushButton:hover {{
                    background: #e67e22;
                }}
            """.format(button_font_size, border_radius, scale_size(5), scale_size(15)))
            ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            button_layout.addWidget(ok_btn)
            layout.addLayout(button_layout)

            ok_btn.clicked.connect(dialog.accept)
            dialog.exec_()
            return
        
        select_all_ctrls()



    def disable_hotkey_for_set(self, set_name):
        # Save hotkey disabled state to metadata
        if set_name not in self.metadata:
            self.metadata[set_name] = {}
        self.metadata[set_name]["hotkey_disabled"] = True
        save_group_metadata(self.metadata, self.current_group)
        
        # Re-sync to apply the change (this will exclude disabled sets)
        sync_all_sets_to_main_network_node()
        
        cmds.inViewMessage(amg="Set '{0}' disabled from hotkey".format(set_name), pos='midCenter', fade=True)

    def enable_hotkey_for_set(self, set_name):
        if set_name not in self.data:
            cmds.warning("Set '{0}' not found in current group.".format(set_name))
            return
        
        # Remove hotkey disabled state from metadata
        if set_name in self.metadata and "hotkey_disabled" in self.metadata[set_name]:
            del self.metadata[set_name]["hotkey_disabled"]
            save_group_metadata(self.metadata, self.current_group)
        
        # Re-sync to apply the change (this will include newly enabled sets)
        sync_all_sets_to_main_network_node()
        
        cmds.inViewMessage(amg="Set '{0}' enabled for hotkey".format(set_name), pos='midCenter', fade=True)

    def open_group_sets_dialog(self):
        if hasattr(self, 'group_sets_dialog') and self.group_sets_dialog and self.group_sets_dialog.isVisible():
            self.group_sets_dialog.raise_()
            self.group_sets_dialog.activateWindow()
            return
        
        self.group_sets_dialog = GroupSetsDialog(self, self.current_group)
        self.group_sets_dialog.group_switched.connect(self.on_group_switched)
        self.group_sets_dialog.set_transfer_requested.connect(self.on_drag_drop_transfer)
        
        # Position Group Manager next to main window
        main_geometry = self.geometry()
        dialog_width = self.group_sets_dialog.width()
        
        # Position to the right of main window
        new_x = main_geometry.x() + main_geometry.width() + scale_size(10)
        new_y = main_geometry.y()
        
        self.group_sets_dialog.move(new_x, new_y)
        self.group_sets_dialog.show()
    
    def on_group_switched(self, group_name):
        self.current_group = group_name
        self.data = load_group_sets(self.current_group)
        self.metadata = load_group_metadata(self.current_group)
        self.refresh_list()
        self.update_selection_count()
        self.highlight_matching_sets()
    
    def on_drag_drop_transfer(self, set_name, target_group):
        """Handle set transfer from drag-drop"""
        if set_name not in self.data:
            cmds.warning("Set '{0}' not found in current group.".format(set_name))
            return
        
        target_data = load_group_sets(target_group)
        target_data[set_name] = self.data[set_name]
        save_group_sets(target_data, target_group)
        
        target_metadata = load_group_metadata(target_group)
        if set_name in self.metadata:
            target_metadata[set_name] = self.metadata[set_name]
            save_group_metadata(target_metadata, target_group)
        
        del self.data[set_name]
        save_group_sets(self.data, self.current_group)
        
        if set_name in self.metadata:
            del self.metadata[set_name]
            save_group_metadata(self.metadata, self.current_group)
        
        sync_all_sets_to_main_network_node()
        self.refresh_list()

    RESIZE_MARGIN = 10
    CORNER_MARGIN = 20

    def get_edges(self, pos):
        rect = self.rect()
        edge_margin = self.RESIZE_MARGIN
        corner_margin = self.CORNER_MARGIN
        x = pos.x()
        y = pos.y()
        w = rect.width()
        h = rect.height()

        near_left = x <= corner_margin
        near_right = x >= w - corner_margin
        near_bottom = y >= h - corner_margin

        if near_left and near_bottom:
            return True, False, False, True
        if near_right and near_bottom:
            return False, False, True, True

        left = x <= edge_margin
        right = x >= w - edge_margin
        bottom = y >= h - edge_margin
        top = False
        return left, top, right, bottom

    def update_cursor(self, pos):
        left, top, right, bottom = self.get_edges(pos)
        if (left and top) or (right and bottom):
            self.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif (right and top) or (left and bottom):
            self.setCursor(QtCore.Qt.SizeBDiagCursor)
        elif left or right:
            self.setCursor(QtCore.Qt.SizeHorCursor)
        elif top or bottom:
            self.setCursor(QtCore.Qt.SizeVerCursor)
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)

    def eventFilter(self, obj, event):
        if self.ui_mode == "horizontal" and event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
            pos_in_dialog = obj.mapTo(self, event.pos())
            left, top, right, bottom = self.get_edges(pos_in_dialog)
            if left or top or right or bottom:
                self._resize_edge = (left, top, right, bottom)
                self._resize_start_geo = QtCore.QRect(self.geometry())
                self._resize_start_pos = get_event_global_pos(event)
                self.grabMouse()
                return True
        return QtWidgets.QDialog.eventFilter(self, obj, event)

    def mousePressEvent(self, event):
        if self.ui_mode == "horizontal":
            if event.button() == QtCore.Qt.LeftButton:
                left, top, right, bottom = self.get_edges(event.pos())
                if left or top or right or bottom:
                    self._resize_edge = (left, top, right, bottom)
                    self._resize_start_geo = QtCore.QRect(self.geometry())
                    self._resize_start_pos = get_event_global_pos(event)
                else:
                    self._resize_edge = None
                    self._drag_pos = get_event_global_pos(event) - self.frameGeometry().topLeft()
                self.grabMouse()
                event.accept()
            else:
                QtWidgets.QDialog.mousePressEvent(self, event)
            return
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_pos = get_event_global_pos(event) - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.ui_mode == "horizontal":
            if self._resize_edge is not None and event.buttons() == QtCore.Qt.LeftButton:
                left, top, right, bottom = self._resize_edge
                delta = get_event_global_pos(event) - self._resize_start_pos
                geo = QtCore.QRect(self._resize_start_geo)
                min_w = self.minimumWidth()
                min_h = self.minimumHeight()

                if left:
                    new_left = geo.left() + delta.x()
                    if geo.right() - new_left + 1 >= min_w:
                        geo.setLeft(new_left)
                if right:
                    geo.setWidth(max(geo.width() + delta.x(), min_w))
                if top:
                    new_top = geo.top() + delta.y()
                    if geo.bottom() - new_top + 1 >= min_h:
                        geo.setTop(new_top)
                if bottom:
                    geo.setHeight(max(geo.height() + delta.y(), min_h))

                self.setGeometry(geo)
                event.accept()
            elif self._drag_pos is not None and event.buttons() == QtCore.Qt.LeftButton:
                self.move(get_event_global_pos(event) - self._drag_pos)
                event.accept()
            else:
                self.update_cursor(event.pos())
            return
        if self._drag_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.move(get_event_global_pos(event) - self._drag_pos)

    def mouseReleaseEvent(self, event):
        if self.ui_mode == "horizontal":
            if event.button() == QtCore.Qt.LeftButton:
                self._drag_pos = None
                self._resize_edge = None
                self.releaseMouse()
                self.setCursor(QtCore.Qt.ArrowCursor)
                event.accept()
            else:
                QtWidgets.QDialog.mouseReleaseEvent(self, event)
            return
        QtWidgets.QDialog.mouseReleaseEvent(self, event)

    def on_toggle_ui_mode(self):
        new_mode = "vertical" if self.ui_mode == "horizontal" else "horizontal"
        set_ui_mode(new_mode)
        self.close()
        esn_pickify()

    def contextMenuEvent(self, event):
        if self.ui_mode == "horizontal":
            self.list_widget.show_empty_area_context_menu(get_event_global_pos(event))
            event.accept()
            return
        QtWidgets.QDialog.contextMenuEvent(self, event)

    def enterEvent(self, event):
        """Mouse entered - fade to full opacity FAST"""
        self.is_mouse_over = True
        if hasattr(self, 'fade_anim'):
            self.fade_anim.stop()
            self.fade_anim.setDuration(120)  # Fast and smooth fade-in: 120ms
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(1.0)  # Full opacity
            self.fade_anim.start()
        super(MinimalEsnSelectionTool, self).enterEvent(event)
    
    def leaveEvent(self, event):
        """Mouse left - fade to subtle transparency SLOWLY"""
        self.is_mouse_over = False
        if hasattr(self, 'fade_anim'):
            self.fade_anim.stop()
            self.fade_anim.setDuration(500)  # Slower, smoother fade-out: 500ms
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(0.70)  # 70% opacity
            self.fade_anim.start()
        super(MinimalEsnSelectionTool, self).leaveEvent(event)
    
class ColorRenameDialog(QtWidgets.QDialog):
    def __init__(self, current_name, current_color=None, parent=None):
        super(ColorRenameDialog, self).__init__(parent)
        self.setWindowTitle("Rename Set")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        self.selected_color = current_color
        self.setup_ui(current_name)
    
    def setup_ui(self, current_name):
        font_size = scale_font_size(12)
        line_edit_font_size = scale_font_size(13)
        button_font_size = scale_font_size(11)
        padding = scale_size(6)
        border_radius = scale_size(4)
        button_padding = scale_size(4)
        button_min_width = scale_size(50)
        button_max_height = scale_size(22)
        color_button_size = scale_size(24)
        
        self.setStyleSheet("""
            QDialog {{
                background-color: #222;
                color: #eee;
                border: 1px solid #555;
                border-radius: {0}px;
            }}
            QLabel {{
                color: #eee;
                font-size: {1}px;
                padding: {2}px;
            }}
        """.format(scale_size(8), font_size, scale_size(5)))
        
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setSpacing(scale_size(0))
        main_layout.setContentsMargins(scale_size(10), scale_size(1), scale_size(10), scale_size(12))
        
        label = QtWidgets.QLabel("New Name:")
        label.setStyleSheet("padding: 0px; margin: 0px;")
        label.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(label)
        
        main_layout.addSpacing(scale_size(2))
        
        self.line_edit = QtWidgets.QLineEdit(current_name)
        self.line_edit.setStyleSheet("""
            QLineEdit {{
                background-color: #333;
                color: #eee;
                border: 1px solid #555;
                border-radius: {0}px;
                padding: {1}px;
                font-size: {2}px;
                min-height: {3}px;
            }}
            QLineEdit:hover {{
                border-color: #f39c12;
            }}
            QLineEdit:focus {{
                border-color: #f39c12;
                background-color: #3a3a3a;
            }}
        """.format(border_radius, padding, line_edit_font_size, scale_size(17)))
        self.line_edit.selectAll()
        main_layout.addWidget(self.line_edit)
        
        # Connect Enter key to accept dialog
        self.line_edit.returnPressed.connect(self.accept)
        
        main_layout.addSpacing(scale_size(12))
        
        colors_layout = QtWidgets.QGridLayout()
        colors_layout.setSpacing(scale_size(4))
        
        self.color_data = [
            ("#303030", "Gray"),
            ("#e74c3c", "Red"),
            ("#e67e22", "Orange"),
            ("#f39c12", "Yellow"),
            ("#f1c40f", "Light Yellow"),
            ("#2ecc71", "Green"),
            ("#1abc9c", "Turquoise"),
            ("#3498db", "Blue"),
            ("#9b59b6", "Purple"),
            ("#e91e63", "Pink"),
            ("#95a5a6", "Light Gray"),
            ("#34495e", "Dark Blue")
        ]
        
        self.color_buttons = []
        row = 0
        col = 0
        for color_hex, color_name in self.color_data:
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(color_button_size, color_button_size)
            btn.setProperty("color_value", color_hex)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            def make_color_handler(color):
                def handler():
                    self.select_color(color)
                return handler
            
            btn.clicked.connect(make_color_handler(color_hex))
            
            border_style = "3px solid #fff" if self.selected_color == color_hex else "1px solid #444"
            btn.setStyleSheet("""
                QPushButton {{
                    background-color: {0};
                    border: {1};
                    border-radius: {2}px;
                }}
                QPushButton:hover {{
                    border: 2px solid #f39c12;
                }}
            """.format(color_hex, border_style, scale_size(3)))
            
            self.color_buttons.append(btn)
            colors_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 6:
                col = 0
                row += 1
        
        main_layout.addLayout(colors_layout)
        
        main_layout.addSpacing(scale_size(14))
        
        button_layout = QtWidgets.QHBoxLayout()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedHeight(button_max_height)
        ok_btn.setStyleSheet("""
            QPushButton {{
                background: #f39c12;
                border: 1px solid #e67e22;
                color: #222;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
                min-width: {4}px;
            }}
            QPushButton:hover {{
                background: #e67e22;
            }}
        """.format(button_font_size, border_radius, button_padding, scale_size(12), button_min_width))
        ok_btn.setCursor(QtCore.Qt.PointingHandCursor)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedHeight(button_max_height)
        cancel_btn.setStyleSheet("""
            QPushButton {{
                background: #555;
                border: 1px solid #666;
                color: #eee;
                font-size: {0}px;
                border-radius: {1}px;
                font-weight: 600;
                padding: {2}px {3}px;
                min-width: {4}px;
            }}
            QPushButton:hover {{
                background: #666;
            }}
        """.format(button_font_size, border_radius, button_padding, scale_size(12), button_min_width))
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addSpacing(scale_size(8))
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
        dialog_width = scale_size(280)
        dialog_height = scale_size(185)
        self.setFixedSize(dialog_width, dialog_height)
    
    def select_color(self, color_hex):
        self.selected_color = str(color_hex)
        
        for btn in self.color_buttons:
            btn_color = str(btn.property("color_value"))
            border_style = "3px solid #fff" if btn_color == str(color_hex) else "1px solid #444"
            btn.setStyleSheet("""
                QPushButton {{
                    background-color: {0};
                    border: {1};
                    border-radius: {2}px;
                }}
                QPushButton:hover {{
                    border: 2px solid #f39c12;
                }}
            """.format(btn_color, border_style, scale_size(3)))
    
    def get_name(self):
        return self.line_edit.text().strip()
    
    def get_color(self):
        return self.selected_color
    
    def showEvent(self, event):
        super(ColorRenameDialog, self).showEvent(event)
        self.line_edit.setFocus()
        self.line_edit.selectAll()

class ColorItemDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        # Override to strip focus and selection BEFORE Qt touches anything
        super(ColorItemDelegate, self).initStyleOption(option, index)
        option.state &= ~QtWidgets.QStyle.State_HasFocus
        option.state &= ~QtWidgets.QStyle.State_Selected
    
    def paint(self, painter, option, index):
        # Remove focus and selection states to prevent Qt decoration
        option.state &= ~QtWidgets.QStyle.State_HasFocus
        option.state &= ~QtWidgets.QStyle.State_Selected
        
        color_hex = index.data(QtCore.Qt.UserRole + 1)
        match_type = index.data(QtCore.Qt.UserRole)
        
        painter.save()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # FIRST: Fill entire rect to cover any Qt default drawing
        painter.fillRect(option.rect, QtGui.QColor(34, 34, 34))
        
        # Subtle margin for separation
        margin = 1
        rect = QtCore.QRectF(option.rect).adjusted(margin, margin, -margin, -margin)
        radius = 3  # Rounded corners
        
        if color_hex:
            color = QtGui.QColor(color_hex)
            color.setAlpha(120)
            # Subtle rounded corners
            path = QtGui.QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            painter.fillPath(path, color)
            
            brightness = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
            text_color = QtGui.QColor("#bbb")
        else:
            default_color = QtGui.QColor(55, 55, 55)
            # Subtle rounded corners
            path = QtGui.QPainterPath()
            path.addRoundedRect(rect, radius, radius)
            painter.fillPath(path, default_color)
            text_color = QtGui.QColor("#bbb")
        
        # Draw borders for states
        is_hovering = option.state & QtWidgets.QStyle.State_MouseOver
        is_selected = option.state & QtWidgets.QStyle.State_Selected
        
        # Draw match states first (base layer)
        if match_type == "full_match":
            # Full match - VERY VIBRANT FILL, no border
            overlay_path = QtGui.QPainterPath()
            overlay_path.addRoundedRect(rect, radius, radius)
            painter.fillPath(overlay_path, QtGui.QColor(243, 156, 18, 150))  # Very vibrant!
            # NO BORDER for full match!
        elif match_type == "partial_match":
            # Partial match - subtle orange border (more transparent)
            painter.setPen(QtGui.QPen(QtGui.QColor(243, 156, 18, 120), 1))
            painter.drawRoundedRect(rect, radius, radius)
        # Note: is_selected state intentionally not drawn
        # Selection happens via click action, not visual highlight
        
        # ALWAYS draw hover on top (even over matches!)
        if is_hovering and not is_selected:
            # Add extra orange glow on hover
            overlay_path = QtGui.QPainterPath()
            overlay_path.addRoundedRect(rect, radius, radius)
            # Add brighter overlay to make hover visible even over matches
            painter.fillPath(overlay_path, QtGui.QColor(243, 156, 18, 40))
            # Draw brighter border for hover
            painter.setPen(QtGui.QPen(QtGui.QColor(243, 156, 18, 200), 2))
            painter.drawRoundedRect(rect, radius, radius)
        
        # Text rendering - no margins
        text_rect = option.rect.adjusted(scale_size(6), 0, -scale_size(6), 0)
        
        # Change text color to super white on full match
        if match_type == "full_match":
            text_color = QtGui.QColor("#fff")  # Super white!
        
        painter.setPen(text_color)
        font = option.font
        if match_type == "full_match":
            font.setWeight(QtGui.QFont.Bold)
        elif option.state & QtWidgets.QStyle.State_Selected:
            font.setWeight(QtGui.QFont.Bold)
        elif option.state & QtWidgets.QStyle.State_MouseOver:
            font.setWeight(QtGui.QFont.DemiBold)
        painter.setFont(font)
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter, index.data(QtCore.Qt.DisplayRole))
        
        painter.restore()

class EsnRightClickListWidget(QtWidgets.QListWidget):
    delete_requested = QtCore.Signal()
    add_selection_requested = QtCore.Signal(str)
    remove_selection_requested = QtCore.Signal(str)
    update_contents_requested = QtCore.Signal(str)
    clear_all_requested = QtCore.Signal()
    export_requested = QtCore.Signal()
    import_requested = QtCore.Signal()
    select_requested = QtCore.Signal(str)
    remove_select_requested = QtCore.Signal(str)
    change_namespace_all_requested = QtCore.Signal()
    auto_select_all_ctrls_requested = QtCore.Signal()
    create_all_set_requested = QtCore.Signal()
    group_sets_requested = QtCore.Signal()
    disable_hotkey_requested = QtCore.Signal(str)
    enable_hotkey_requested = QtCore.Signal(str)
    rename_requested = QtCore.Signal(object)  # Pass the item to rename
    toggle_ui_mode_requested = QtCore.Signal()

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if item is None:
            event.ignore()
        else:
            super(EsnRightClickListWidget, self).mousePressEvent(event)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            
            # Store the item text for external drops (Group Manager)
            set_name = item.text()
            mime_data.setText(set_name)
            
            # Store source group info
            if hasattr(self, 'current_group'):
                mime_data.setData("application/x-pickify-source-group", self.current_group.encode('utf-8'))
            
            # Also store the internal model data for reordering within this list
            model_data = self.model().mimeData([self.indexFromItem(item)])
            if model_data:
                for format in model_data.formats():
                    mime_data.setData(format, model_data.data(format))
            
            drag.setMimeData(mime_data)
            drag.exec_(QtCore.Qt.MoveAction)

    def contextMenuEvent(self, event):
        item = self.itemAt(event.pos())
        menu = QtWidgets.QMenu(self)
        
        menu.setStyleSheet(get_context_menu_style())
        
        if item:
            original_name = item.text()
            
            add_action = menu.addAction("Add to Set")
            remove_action = menu.addAction("Remove from Set")
            update_action = menu.addAction("Update Set")
            rename_action = menu.addAction("Rename")
            menu.addSeparator()
            
            delete_action = menu.addAction("Delete")
            menu.addSeparator()
            
            create_all_action = menu.addAction("Create All Ctrls Set")
            auto_select_all_action = menu.addAction("Auto Select All Ctrls")
            change_namespace_all_action = menu.addAction("Change Namespace")
            menu.addSeparator()
            
            group_sets_action = menu.addAction("= Group Manager =")
            menu.addSeparator()
            
            export_action = menu.addAction("Export Sets")
            import_action = menu.addAction("Import Sets")
            clear_action = menu.addAction("Clear All Sets")
            menu.addSeparator()
            
            enable_hotkey_action = menu.addAction("Enable Hotkey")
            disable_hotkey_action = menu.addAction("Disable Hotkey")
            menu.addSeparator()
            
            mode_label = "Vertical Mode" if getattr(self, "current_ui_mode", "vertical") == "horizontal" else "Horizontal Mode"
            toggle_mode_action = menu.addAction(mode_label)
            
            action = menu.exec_(self.mapToGlobal(event.pos()))
            
            if action == update_action:
                self.update_contents_requested.emit(original_name)
            elif action == rename_action:
                self.rename_requested.emit(item)
            elif action == add_action:
                self.add_selection_requested.emit(original_name)
            elif action == remove_action:
                self.remove_selection_requested.emit(original_name)
            elif action == delete_action:
                self.delete_requested.emit()
            elif action == create_all_action:
                self.create_all_set_requested.emit()
            elif action == auto_select_all_action:
                self.auto_select_all_ctrls_requested.emit()
            elif action == change_namespace_all_action:
                self.change_namespace_all_requested.emit()
            elif action == group_sets_action:
                self.group_sets_requested.emit()
            elif action == export_action:
                self.export_requested.emit()
            elif action == import_action:
                self.import_requested.emit()
            elif action == clear_action:
                self.clear_all_requested.emit()
            elif action == enable_hotkey_action:
                self.enable_hotkey_requested.emit(original_name)
            elif action == disable_hotkey_action:
                self.disable_hotkey_requested.emit(original_name)
            elif action == toggle_mode_action:
                self.toggle_ui_mode_requested.emit()
        else:
            self.show_empty_area_context_menu(self.mapToGlobal(event.pos()))

    def show_empty_area_context_menu(self, global_pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(get_context_menu_style())

        create_all_action = menu.addAction("Create All Ctrls Set")
        auto_select_all_action = menu.addAction("Auto Select All Ctrls")
        change_namespace_all_action = menu.addAction("Change Namespace")
        menu.addSeparator()
        
        group_sets_action = menu.addAction("= Group Manager =")
        menu.addSeparator()
        
        export_action = menu.addAction("Export Sets")
        import_action = menu.addAction("Import Sets")
        clear_action = menu.addAction("Clear All Sets")
        menu.addSeparator()
        
        mode_label = "Vertical Mode" if getattr(self, "current_ui_mode", "vertical") == "horizontal" else "Horizontal Mode"
        toggle_mode_action = menu.addAction(mode_label)
        
        action = menu.exec_(global_pos)
        
        if action == create_all_action:
            self.create_all_set_requested.emit()
        elif action == auto_select_all_action:
            self.auto_select_all_ctrls_requested.emit()
        elif action == change_namespace_all_action:
            self.change_namespace_all_requested.emit()
        elif action == group_sets_action:
            self.group_sets_requested.emit()
        elif action == export_action:
            self.export_requested.emit()
        elif action == import_action:
            self.import_requested.emit()
        elif action == clear_action:
            self.clear_all_requested.emit()
        elif action == toggle_mode_action:
            self.toggle_ui_mode_requested.emit()

def _close_existing_pickify_windows():
    try:
        main_win = get_maya_main_window()
    except Exception:
        return
    
    if main_win is None:
        return
    
    for child in main_win.children():
        try:
            if child.objectName() != "PickifyUIWindow":
                continue
            child.close()
            child.setParent(None)
            child.deleteLater()
        except (AttributeError, RuntimeError):
            continue

def esn_pickify():
    global _minimal_esn_tool_win
    QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
    try:
        try:
            _minimal_esn_tool_win.close()
            _minimal_esn_tool_win.deleteLater()
        except Exception:
            pass
        
        _close_existing_pickify_windows()
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
            app.processEvents()
        
        _minimal_esn_tool_win = MinimalEsnSelectionTool()
        _minimal_esn_tool_win.show()
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()

def ui():
    esn_pickify()

def createEsnNetworkSet():
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        cmds.warning("Nothing selected to create set with.")
        return
    
    sets_data = load_esn_sets()
    
    sel_set = set(sel)
    for existing_set_name, existing_set_objects in sets_data.items():
        if set(existing_set_objects) == sel_set:
            cmds.warning("You already have a set with these contents.")
            return
    
    base_name = "set"
    index = 1
    while "{0}_{1}".format(base_name, index) in sets_data:
        index += 1
    set_name = "{0}_{1}".format(base_name, index)
    
    sets_data[set_name] = sel
    save_esn_sets(sets_data)

def createEsnAllNetworkSet():
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        cmds.warning("Nothing selected to create All Controls set with.")
        return
    
    sets_data = load_esn_sets()
    sets_data["All_Ctrls"] = sel
    save_esn_sets(sets_data)

def esnSelectNetworkSets():
    sel = cmds.ls(sl=True, long=True)
    sets_data = load_esn_sets()
    
    if not sel:    
        if "All_Ctrls" in sets_data:
            all_objects = sets_data["All_Ctrls"]
            existing_objects = [obj for obj in all_objects if cmds.objExists(obj)]
            if existing_objects:
                cmds.select(existing_objects)
        return
    
    selections = cmds.ls(sl=True, long=True)
    matching_sets = []
    
    for set_name, set_objects in sets_data.items():
        if "All_Ctrls" not in set_name and "esn_set" in set_name:
            for selected_obj in selections:
                if selected_obj in set_objects:
                    matching_sets.append(set_name)
                    break
    
    if matching_sets:
        all_set_objects = []
        for set_name in matching_sets:
            all_set_objects.extend(sets_data[set_name])
        
        unique_objects = list(set(all_set_objects))
        existing_objects = [obj for obj in unique_objects if cmds.objExists(obj)]
        
        if existing_objects:
            cmds.select(existing_objects)

def quickSelectionUI():
    if cmds.window('Quick_Selection', exists=True):
        cmds.deleteUI('Quick_Selection')
        
    myWin = cmds.window('Quick_Selection', mxb=False)
    cmds.showWindow(myWin)
    cmds.window('Quick_Selection', e=True, width=10, height=10, s=1, tlb=True)
    
    cmds.columnLayout(adjustableColumn=True)
    cmds.frameLayout( label='Quick Selection', labelAlign='center', collapsable=True, cl=False, bgc=[0.200,0.200,0.200])
        
    cmds.button('Get', bgc=[1, 0.75, 0.4], command='esnGetSelections()')
    cmds.button('Select', bgc=[1, 0.45, 0.354], command='esnQuickSelectItems()')

def esnGetSelections():
    documentsPath = os.path.expanduser('~')
    sel = cmds.ls(sl=True)
    if sel:
        f = open(documentsPath + "/OBJECT_LIST.txt", "w")
        for s in sel:
            f.write(s + "\n")
        f.close()
        cmds.inViewMessage(amg='Selections Stored', pos='midCenter', fade=True)

def esnQuickSelectItems():
    documentsPath = os.path.expanduser('~')
    selections = cmds.ls(sl=True)
    
    namespaceList = []
    for sel in selections:
        selNamespace = sel.split(":")[0]
        if selNamespace not in namespaceList:
            namespaceList.append(selNamespace)
    
    if selections:
        with open(documentsPath + "/OBJECT_LIST.txt") as f:
            lines = f.readlines()
        
        objList = []    
        for line in lines:
            obj = line.split(",")
            objList.append(obj)
        
        controlsNoNamespace = []    
        for obj in objList:
            obj = obj[0].replace("\n", "")
            obj = obj.split(":")[-1]    
            controlsNoNamespace.append(obj) 
            
        selectTheseItems = []
        for n in namespaceList:
            for item in controlsNoNamespace:
                obj = n + ":" + item
                selectTheseItems.append(obj)
                
        cmds.select(cl=True)
        for i in selectTheseItems:
            try:
                cmds.select(i, add=True)
            except:
                pass
    else:
        with open(documentsPath + "/OBJECT_LIST.txt") as f:
            lines = f.readlines()
        
        objList = []    
        for line in lines:
            obj = line.split(",")
            objList.append(obj)
        
        selectTheseitems = []    
        for obj in objList:
            obj = obj[0].replace("\n", "")  
            selectTheseitems.append(obj) 
        
        cmds.select(cl=True)
        try:
            cmds.select(selectTheseitems)
        except:
            pass

esn_pickify()