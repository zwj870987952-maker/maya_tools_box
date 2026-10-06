from __future__ import division
from __future__ import absolute_import

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import json
import os
import sys
import uuid
import platform
import math
import subprocess
import time

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
    int = builtins.int
    str = builtins.str
    range = builtins.range
except Exception:
    pass


def get_maya_version():
    try:
        version_string = cmds.about(version=True)
        for part in version_string.split():
            if part.isdigit() and len(part) == 4:
                return int(part)
        return 2022
    except Exception:
        return 2022


def is_macos():
    return platform.system() == "Darwin"


BASE_DPI = 96.0
_scale_factor = None
_cursor_position = None


def get_scale_factor():
    global _scale_factor, _cursor_position
    
    try:
        current_cursor = QtGui.QCursor.pos()
        if _cursor_position is not None and _scale_factor is not None:
            if abs(current_cursor.x() - _cursor_position.x()) < 100 and \
               abs(current_cursor.y() - _cursor_position.y()) < 100:
                return _scale_factor
        _cursor_position = current_cursor
    except Exception:
        if _scale_factor is not None:
            return _scale_factor
    
    try:
        app = QtWidgets.QApplication.instance()
        raw_scale = 1.0
        
        if app:
            screen = None
            
            if PYSIDE_VERSION == 6:
                screen = app.screenAt(current_cursor)
                if not screen:
                    screen = QGuiApplication.primaryScreen()
            else:
                if hasattr(app, 'screenAt'):
                    screen = app.screenAt(current_cursor)
                if not screen and hasattr(app, 'primaryScreen'):
                    screen = app.primaryScreen()
            
            if screen:
                raw_scale = screen.logicalDotsPerInch() / BASE_DPI
            else:
                desktop = app.desktop() if hasattr(app, 'desktop') else None
                if desktop:
                    raw_scale = desktop.logicalDpiX() / BASE_DPI
        
        _scale_factor = max(1.0, min(raw_scale, 3.0))
            
    except Exception:
        _scale_factor = 1.0
    
    return _scale_factor


def reset_scale_factor():
    global _scale_factor, _cursor_position
    _scale_factor = None
    _cursor_position = None


def dpi(value):
    return int(value * get_scale_factor())


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info[0] >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def save_window_position(pos):
    pos_str = "{0},{1}".format(pos.x(), pos.y())
    cmds.optionVar(stringValue=('CamBookmarkUI_WindowPos', pos_str))


def load_window_position():
    if cmds.optionVar(exists='CamBookmarkUI_WindowPos'):
        try:
            pos_str = cmds.optionVar(q='CamBookmarkUI_WindowPos')
            x, y = pos_str.split(',')
            return QtCore.QPoint(int(x), int(y))
        except Exception:
            pass
    return None


def show_feedback_message(message):
    try:
        cmds.inViewMessage(
            amg=message,
            pos='midCenter',
            fade=True,
            fadeStayTime=1500,
            fadeOutTime=500
        )
    except Exception:
        pass


PLAYBLAST_PATH_ATTR = 'playblastPath'
PLAYBLAST_FILENAME_ATTR = 'playblastFilename'

OPT_GEOMETRY = 'camBookmarkMgr_geometry'
OPT_NURBS_CURVES = 'camBookmarkMgr_nurbsCurves'
OPT_LOCATORS = 'camBookmarkMgr_locators'
OPT_IMAGE_PLANES = 'camBookmarkMgr_imagePlanes'
OPT_LIGHTS = 'camBookmarkMgr_lights'
OPT_GRID = 'camBookmarkMgr_grid'
OPT_SHADOWS = 'camBookmarkMgr_shadows'
OPT_ACTIVE_TAB = 'camBookmarkMgr_activeTab'
OPT_RESOLUTION_SOURCE = 'camBookmarkMgr_resolutionSource'
OPT_TRACKED_CAMERAS = 'camBookmarkMgr_trackedCameras'


def short_display_name(name):
    if name and '|' in name:
        return name.split('|')[-1]
    return name


def resolve_camera_transform_names(cam_shape):
    parents = cmds.listRelatives(cam_shape, parent=True, fullPath=True) or []
    resolved = []
    for full_path in parents:
        short_name = full_path.split('|')[-1]
        try:
            matches = cmds.ls(short_name) or []
        except Exception:
            matches = []
        if len(matches) == 1:
            resolved.append(short_name)
        else:
            resolved.append(full_path)
    return resolved


def resolve_ambiguous_transform_name(name):
    if not cmds.objExists(name):
        return None
    
    try:
        matches = cmds.ls(name, long=True) or []
    except Exception:
        matches = []
    
    if len(matches) <= 1:
        return name
    
    for full_path in matches:
        try:
            shapes = cmds.listRelatives(full_path, shapes=True, fullPath=True, type='camera') or []
        except Exception:
            shapes = []
        if shapes:
            return full_path
    
    return name


def load_tracked_cameras():
    """Load tracked cameras from optionVar."""
    if cmds.optionVar(exists=OPT_TRACKED_CAMERAS):
        cam_string = cmds.optionVar(query=OPT_TRACKED_CAMERAS)
        if cam_string:
            cameras = cam_string.split(',')
            valid = []
            for c in cameras:
                try:
                    if c and cmds.objExists(c):
                        valid.append(c)
                except Exception:
                    continue
            return valid
    return []


def save_tracked_cameras(cameras):
    """Save tracked cameras to optionVar."""
    cam_string = ','.join(cameras) if cameras else ''
    cmds.optionVar(stringValue=(OPT_TRACKED_CAMERAS, cam_string))


def ensure_playblast_attrs(node):
    if not cmds.attributeQuery(PLAYBLAST_PATH_ATTR, node=node, exists=True):
        cmds.addAttr(node, longName=PLAYBLAST_PATH_ATTR, dataType='string')
    if not cmds.attributeQuery(PLAYBLAST_FILENAME_ATTR, node=node, exists=True):
        cmds.addAttr(node, longName=PLAYBLAST_FILENAME_ATTR, dataType='string')


def get_playblast_path(node):
    if cmds.attributeQuery(PLAYBLAST_PATH_ATTR, node=node, exists=True):
        path = cmds.getAttr('{0}.{1}'.format(node, PLAYBLAST_PATH_ATTR))
        return path if path else ''
    return ''


def get_playblast_filename(node):
    if cmds.attributeQuery(PLAYBLAST_FILENAME_ATTR, node=node, exists=True):
        filename = cmds.getAttr('{0}.{1}'.format(node, PLAYBLAST_FILENAME_ATTR))
        return filename if filename else ''
    return ''


def set_playblast_path(node, path):
    ensure_playblast_attrs(node)
    cmds.setAttr('{0}.{1}'.format(node, PLAYBLAST_PATH_ATTR), path, type='string')


def set_playblast_filename(node, filename):
    ensure_playblast_attrs(node)
    cmds.setAttr('{0}.{1}'.format(node, PLAYBLAST_FILENAME_ATTR), filename, type='string')


def load_option(option_var, default=False):
    if cmds.optionVar(exists=option_var):
        val = cmds.optionVar(query=option_var)
        # If default is int, return int; otherwise return bool
        if isinstance(default, int) and not isinstance(default, bool):
            return int(val)
        return bool(val)
    return default


def save_option(option_var, value):
    cmds.optionVar(intValue=(option_var, int(value)))


def apply_bookmark_to_camera(bookmark, camera):
    if cmds.nodeType(camera) != 'transform':
        parents = cmds.listRelatives(camera, parent=True)
        camera = parents[0] if parents else None
        if not camera:
            return
    
    try:
        cmds.cameraView(bookmark, edit=True, camera=camera, setCamera=True)
        return
    except Exception:
        pass
    
    if cmds.nodeType(camera) == 'transform':
        cam_shapes = cmds.listRelatives(camera, shapes=True, type='camera')
        if not cam_shapes:
            return
    
    def safe_get(node, attr, default):
        if cmds.attributeQuery(attr, node=node, exists=True):
            val = cmds.getAttr('{0}.{1}'.format(node, attr))
            return val[0] if isinstance(val, list) else val
        return default
    
    try:
        eye = safe_get(bookmark, 'eye', None)
        coi = safe_get(bookmark, 'centerOfInterest', None)
        if not eye or not coi:
            return
        
        cmds.setAttr('{0}.translate'.format(camera), eye[0], eye[1], eye[2])
        
        dx, dy, dz = coi[0] - eye[0], coi[1] - eye[1], coi[2] - eye[2]
        dist_xz = math.sqrt(dx*dx + dz*dz)
        
        if dist_xz > 0.0001:
            rot_y = math.degrees(math.atan2(dx, dz)) + 180
            rot_x = -math.degrees(math.atan2(dy, dist_xz))
        else:
            rot_y = 0
            rot_x = -90 if dy > 0 else 90
        
        cmds.setAttr('{0}.rotate'.format(camera), rot_x, rot_y, 0)
    except Exception:
        pass


def get_camera_bookmarks():
    bookmarks = []
    for cv in cmds.ls(type='cameraView') or []:
        data = {'name': cv}
        for attr in ['eye', 'centerOfInterest', 'up', 'tumblePivot']:
            if cmds.attributeQuery(attr, node=cv, exists=True):
                data[attr] = cmds.getAttr('{0}.{1}'.format(cv, attr))[0]
        for attr in ['focalLength', 'horizontalAperture', 'verticalAperture', 'orthographicWidth', 'orthographic']:
            if cmds.attributeQuery(attr, node=cv, exists=True):
                data[attr] = cmds.getAttr('{0}.{1}'.format(cv, attr))
        data['playblastPath'] = get_playblast_path(cv)
        data['playblastFilename'] = get_playblast_filename(cv)
        connections = cmds.listConnections(cv, type='camera')
        if connections:
            data['associatedCamera'] = connections[0]
        bookmarks.append(data)
    return bookmarks


class AddCameraDialog(QtWidgets.QDialog):
    cameras_added = QtCore.Signal(list)
    
    def __init__(self, parent=None):
        super(AddCameraDialog, self).__init__(parent)
        
        self.drag_position = QtCore.QPoint()
        
        self.setWindowTitle("Add Cameras")
        self.setFixedSize(dpi(300), dpi(350))
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui()
        self.populate_cameras()
    
    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("addCamContainer")
        container.setStyleSheet("""
            QWidget#addCamContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, dpi(12))
        container_layout.setSpacing(dpi(8))
        
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(dpi(36))
        title_bar.setStyleSheet("background: transparent;")
        title_row = QtWidgets.QHBoxLayout(title_bar)
        title_row.setContentsMargins(dpi(12), dpi(8), dpi(8), dpi(4))
        
        title_label = QtWidgets.QLabel("Add Cameras")
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), 0, dpi(12), 0)
        content_layout.setSpacing(dpi(8))
        
        persp_label = QtWidgets.QLabel("Perspective Cameras")
        persp_label.setStyleSheet("color: #aaa; font-size: 8pt; font-weight: bold; background: transparent;")
        content_layout.addWidget(persp_label)
        
        self.persp_list = QtWidgets.QListWidget()
        self.persp_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.persp_list.setFixedHeight(dpi(90))
        self.persp_list.setStyleSheet(self.get_list_style())
        content_layout.addWidget(self.persp_list)
        
        ortho_label = QtWidgets.QLabel("Orthographic Cameras")
        ortho_label.setStyleSheet("color: #aaa; font-size: 8pt; font-weight: bold; background: transparent; margin-top: 4px;")
        content_layout.addWidget(ortho_label)
        
        self.ortho_list = QtWidgets.QListWidget()
        self.ortho_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ortho_list.setFixedHeight(dpi(90))
        self.ortho_list.setStyleSheet(self.get_list_style())
        content_layout.addWidget(self.ortho_list)
        
        content_layout.addStretch()
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(8))
        
        add_selected_btn = QtWidgets.QPushButton("ADD SELECTED")
        add_selected_btn.setFixedHeight(dpi(28))
        add_selected_btn.setCursor(QtCore.Qt.PointingHandCursor)
        add_selected_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(179, 119, 0, 220);
                border: 1px solid rgba(153, 102, 0, 200);
                color: #fff;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(217, 145, 0, 220);
            }
        """)
        add_selected_btn.clicked.connect(self.add_selected)
        btn_layout.addWidget(add_selected_btn)
        
        add_all_btn = QtWidgets.QPushButton("ADD ALL")
        add_all_btn.setFixedHeight(dpi(28))
        add_all_btn.setCursor(QtCore.Qt.PointingHandCursor)
        add_all_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(243, 156, 18, 200);
                border-color: #f39c12;
                color: #222;
            }
        """)
        add_all_btn.clicked.connect(self.add_all)
        btn_layout.addWidget(add_all_btn)
        
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content_widget)
        
        main_layout.addWidget(container)
    
    def get_list_style(self):
        return """
            QListWidget {
                background-color: rgba(42, 42, 42, 180);
                border: 1px solid rgba(68, 68, 68, 120);
                border-radius: 4px;
                color: #eee;
                font-size: 9pt;
                padding: 2px;
                outline: none;
            }
            QListWidget::item {
                padding: 4px;
                border-radius: 3px;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: rgba(243, 156, 18, 200);
                color: #222;
            }
            QListWidget::item:selected {
                background-color: rgba(180, 120, 18, 200);
                color: #fff;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 100);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """
    
    def populate_cameras(self):
        self.persp_list.clear()
        self.ortho_list.clear()
        
        all_cams = cmds.ls(type='camera', long=True) or []
        skip_cams = ['perspShape']
        
        for cam_shape in sorted(all_cams):
            if cam_shape.split('|')[-1] in skip_cams:
                continue
            
            try:
                cam_transforms = resolve_camera_transform_names(cam_shape)
                if not cam_transforms:
                    continue
                
                for cam_transform in cam_transforms:
                    is_ortho = cmds.getAttr('{0}.orthographic'.format(cam_shape))
                    
                    if is_ortho:
                        self.ortho_list.addItem(cam_transform)
                    else:
                        self.persp_list.addItem(cam_transform)
            except Exception:
                continue
    
    def add_selected(self):
        cameras = []
        
        for item in self.persp_list.selectedItems():
            cameras.append(item.text())
        
        for item in self.ortho_list.selectedItems():
            cameras.append(item.text())
        
        if cameras:
            self.cameras_added.emit(cameras)
            self.accept()
    
    def add_all(self):
        cameras = []
        
        for i in range(self.persp_list.count()):
            cameras.append(self.persp_list.item(i).text())
        
        for i in range(self.ortho_list.count()):
            cameras.append(self.ortho_list.item(i).text())
        
        if cameras:
            self.cameras_added.emit(cameras)
            self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class ExportDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, has_cameras=False, has_bookmarks=False, has_cam_selection=False, has_bm_selection=False):
        super(ExportDialog, self).__init__(parent)
        
        self.has_cameras = has_cameras
        self.has_bookmarks = has_bookmarks
        self.has_cam_selection = has_cam_selection
        self.has_bm_selection = has_bm_selection
        self.export_type = None
        self.export_selected = False
        self.drag_position = QtCore.QPoint()
        
        self.setWindowTitle("Export")
        self.setFixedSize(dpi(260), dpi(200))
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("exportContainer")
        container.setStyleSheet("""
            QWidget#exportContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, dpi(12))
        container_layout.setSpacing(dpi(10))
        
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(dpi(36))
        title_bar.setStyleSheet("background: transparent;")
        title_row = QtWidgets.QHBoxLayout(title_bar)
        title_row.setContentsMargins(dpi(12), dpi(8), dpi(8), dpi(4))
        
        title_label = QtWidgets.QLabel("Export")
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), 0, dpi(12), 0)
        content_layout.setSpacing(dpi(10))
        
        btn_style = """
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(243, 156, 18, 200);
                border-color: #f39c12;
                color: #222;
            }
            QPushButton:disabled {
                background-color: rgba(40, 40, 40, 150);
                color: #555;
                border-color: rgba(60, 60, 60, 100);
            }
        """
        
        self.cam_btn = QtWidgets.QPushButton("Cameras (.ma)")
        self.cam_btn.setFixedHeight(dpi(32))
        self.cam_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.cam_btn.setStyleSheet(btn_style)
        self.cam_btn.setEnabled(self.has_cameras)
        self.cam_btn.clicked.connect(lambda checked=False: self.do_export("cameras"))
        content_layout.addWidget(self.cam_btn)
        
        self.bm_btn = QtWidgets.QPushButton("Bookmarks (.json)")
        self.bm_btn.setFixedHeight(dpi(32))
        self.bm_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.bm_btn.setStyleSheet(btn_style)
        self.bm_btn.setEnabled(self.has_bookmarks)
        self.bm_btn.clicked.connect(lambda checked=False: self.do_export("bookmarks"))
        content_layout.addWidget(self.bm_btn)
        
        content_layout.addStretch()
        
        self.selected_chk = QtWidgets.QCheckBox("Export Selected Only")
        self.selected_chk.setStyleSheet("""
            QCheckBox {
                color: #ccc;
                font-size: 8pt;
                background: transparent;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid #555;
                background-color: rgba(42, 42, 42, 180);
            }
            QCheckBox::indicator:checked {
                background-color: #f39c12;
                border-color: #e67e22;
            }
            QCheckBox::indicator:hover {
                border-color: #f39c12;
            }
        """)
        has_any_selection = self.has_cam_selection or self.has_bm_selection
        self.selected_chk.setEnabled(has_any_selection)
        content_layout.addWidget(self.selected_chk)
        
        container_layout.addWidget(content_widget)
        main_layout.addWidget(container)
    
    def do_export(self, export_type):
        self.export_type = export_type
        self.export_selected = self.selected_chk.isChecked()
        self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class ImportDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        super(ImportDialog, self).__init__(parent)
        
        self.import_type = None
        self.drag_position = QtCore.QPoint()
        
        self.setWindowTitle("Import")
        self.setFixedSize(dpi(260), dpi(160))
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("importContainer")
        container.setStyleSheet("""
            QWidget#importContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(12))
        container_layout.setSpacing(dpi(10))
        
        title_row = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel("Import")
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addLayout(title_row)
        
        btn_style = """
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(243, 156, 18, 200);
                border-color: #f39c12;
                color: #222;
            }
        """
        
        cam_btn = QtWidgets.QPushButton("Cameras (.ma)")
        cam_btn.setFixedHeight(dpi(32))
        cam_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cam_btn.setStyleSheet(btn_style)
        cam_btn.clicked.connect(lambda checked=False: self.do_import("cameras"))
        container_layout.addWidget(cam_btn)
        
        bm_btn = QtWidgets.QPushButton("Bookmarks (.json)")
        bm_btn.setFixedHeight(dpi(32))
        bm_btn.setCursor(QtCore.Qt.PointingHandCursor)
        bm_btn.setStyleSheet(btn_style)
        bm_btn.clicked.connect(lambda checked=False: self.do_import("bookmarks"))
        container_layout.addWidget(bm_btn)
        
        container_layout.addStretch()
        
        main_layout.addWidget(container)
    
    def do_import(self, import_type):
        self.import_type = import_type
        self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()


class StyledMessageBox(QtWidgets.QDialog):
    
    def __init__(self, parent=None, title="Message", message="", buttons=None):
        super(StyledMessageBox, self).__init__(parent)
        
        self.drag_position = QtCore.QPoint()
        self.result_button = None
        
        if buttons is None:
            buttons = ["OK"]
        self.button_list = buttons
        
        self.setWindowTitle(title)
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui(title, message, buttons)
        self.adjustSize()
        min_width = dpi(260)
        if self.width() < min_width:
            self.setFixedWidth(min_width)
    
    def setup_ui(self, title, message, buttons):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("msgContainer")
        container.setStyleSheet("""
            QWidget#msgContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, dpi(12))
        container_layout.setSpacing(dpi(12))
        
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(dpi(36))
        title_bar.setStyleSheet("background: transparent;")
        title_row = QtWidgets.QHBoxLayout(title_bar)
        title_row.setContentsMargins(dpi(12), dpi(8), dpi(8), dpi(4))
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), 0, dpi(12), 0)
        content_layout.setSpacing(dpi(12))
        
        msg_label = QtWidgets.QLabel(message)
        msg_label.setStyleSheet("color: #ccc; font-size: 9pt; background: transparent;")
        msg_label.setWordWrap(True)
        msg_label.setMinimumWidth(dpi(200))
        content_layout.addWidget(msg_label)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(8))
        btn_layout.addStretch()
        
        btn_style_primary = """
            QPushButton {
                background-color: rgba(179, 119, 0, 220);
                border: none;
                color: #fff;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(217, 145, 0, 220);
            }
        """
        
        btn_style_secondary = """
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """
        
        for i, btn_text in enumerate(buttons):
            btn = QtWidgets.QPushButton(btn_text)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setFixedHeight(dpi(28))
            if i == 0:
                btn.setStyleSheet(btn_style_primary)
            else:
                btn.setStyleSheet(btn_style_secondary)
            btn.clicked.connect(lambda checked=False, t=btn_text: self.button_clicked(t))
            btn_layout.addWidget(btn)
        
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content_widget)
        main_layout.addWidget(container)
    
    def button_clicked(self, text):
        self.result_button = text
        self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    @staticmethod
    def show_message(parent, title, message, buttons=None):
        if buttons is None:
            buttons = ["OK"]
        dialog = StyledMessageBox(parent, title, message, buttons)
        dialog.exec_()
        return dialog.result_button


class StyledInputDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, title="Input", message="", text="", buttons=None):
        super(StyledInputDialog, self).__init__(parent)
        
        self.drag_position = QtCore.QPoint()
        self.result_button = None
        self.input_text = text
        
        if buttons is None:
            buttons = ["OK", "Cancel"]
        self.button_list = buttons
        
        self.setWindowTitle(title)
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui(title, message, text, buttons)
        self.setFixedSize(dpi(300), self.sizeHint().height())
    
    def setup_ui(self, title, message, text, buttons):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("inputContainer")
        container.setStyleSheet("""
            QWidget#inputContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, dpi(12))
        container_layout.setSpacing(dpi(10))
        
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(dpi(36))
        title_bar.setStyleSheet("background: transparent;")
        title_row = QtWidgets.QHBoxLayout(title_bar)
        title_row.setContentsMargins(dpi(12), dpi(8), dpi(8), dpi(4))
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), 0, dpi(12), 0)
        content_layout.setSpacing(dpi(10))
        
        if message:
            msg_label = QtWidgets.QLabel(message)
            msg_label.setStyleSheet("color: #ccc; font-size: 9pt; background: transparent;")
            msg_label.setWordWrap(True)
            content_layout.addWidget(msg_label)
        
        self.text_input = QtWidgets.QLineEdit(text)
        self.text_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(42, 42, 42, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                border-radius: 4px;
                color: #eee;
                font-size: 9pt;
                padding: 6px 8px;
            }
            QLineEdit:focus {
                border-color: #f39c12;
            }
        """)
        self.text_input.setFixedHeight(dpi(28))
        self.text_input.returnPressed.connect(lambda: self.button_clicked(buttons[0]))
        content_layout.addWidget(self.text_input)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(8))
        btn_layout.addStretch()
        
        btn_style_primary = """
            QPushButton {
                background-color: rgba(179, 119, 0, 220);
                border: none;
                color: #fff;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(217, 145, 0, 220);
            }
        """
        
        btn_style_secondary = """
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """
        
        for i, btn_text in enumerate(buttons):
            btn = QtWidgets.QPushButton(btn_text)
            btn.setCursor(QtCore.Qt.PointingHandCursor)
            btn.setFixedHeight(dpi(28))
            if i == 0:
                btn.setStyleSheet(btn_style_primary)
            else:
                btn.setStyleSheet(btn_style_secondary)
            btn.clicked.connect(lambda checked=False, t=btn_text: self.button_clicked(t))
            btn_layout.addWidget(btn)
        
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content_widget)
        main_layout.addWidget(container)
    
    def button_clicked(self, text):
        self.result_button = text
        self.input_text = self.text_input.text()
        self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    @staticmethod
    def get_text(parent, title, message, text="", buttons=None):
        if buttons is None:
            buttons = ["OK", "Cancel"]
        dialog = StyledInputDialog(parent, title, message, text, buttons)
        dialog.exec_()
        return dialog.result_button, dialog.input_text


class StyledListDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, title="Select", message="", items=None):
        super(StyledListDialog, self).__init__(parent)
        
        self.drag_position = QtCore.QPoint()
        self.selected_item = None
        self.selected_index = -1
        
        if items is None:
            items = []
        
        self.setWindowTitle(title)
        window_flags = QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setup_ui(title, message, items)
        self.setFixedSize(dpi(320), dpi(280))
    
    def setup_ui(self, title, message, items):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QtWidgets.QWidget()
        container.setObjectName("listContainer")
        container.setStyleSheet("""
            QWidget#listContainer {
                background-color: rgba(26, 26, 26, 250);
                border-radius: 8px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, dpi(12))
        container_layout.setSpacing(dpi(10))
        
        title_bar = QtWidgets.QWidget()
        title_bar.setFixedHeight(dpi(36))
        title_bar.setStyleSheet("background: transparent;")
        title_row = QtWidgets.QHBoxLayout(title_bar)
        title_row.setContentsMargins(dpi(12), dpi(8), dpi(8), dpi(4))
        
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: #eee; font-size: 11pt; font-weight: bold; background: transparent;")
        title_row.addWidget(title_label)
        title_row.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #f39c12;
            }
        """)
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), 0, dpi(12), 0)
        content_layout.setSpacing(dpi(10))
        
        if message:
            msg_label = QtWidgets.QLabel(message)
            msg_label.setStyleSheet("color: #ccc; font-size: 9pt; background: transparent;")
            msg_label.setWordWrap(True)
            content_layout.addWidget(msg_label)
        
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: rgba(42, 42, 42, 180);
                border: 1px solid rgba(68, 68, 68, 120);
                border-radius: 4px;
                color: #eee;
                font-size: 9pt;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: rgba(243, 156, 18, 200);
                color: #222;
            }
            QListWidget::item:selected {
                background-color: rgba(180, 120, 18, 200);
                color: #fff;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 100);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self.item_double_clicked)
        for item in items:
            self.list_widget.addItem(item)
        if items:
            self.list_widget.setCurrentRow(0)
        content_layout.addWidget(self.list_widget)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(dpi(8))
        btn_layout.addStretch()
        
        btn_style_primary = """
            QPushButton {
                background-color: rgba(179, 119, 0, 220);
                border: none;
                color: #fff;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(217, 145, 0, 220);
            }
        """
        
        btn_style_secondary = """
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 9pt;
                font-weight: bold;
                padding: 6px 16px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """
        
        select_btn = QtWidgets.QPushButton("Select")
        select_btn.setCursor(QtCore.Qt.PointingHandCursor)
        select_btn.setFixedHeight(dpi(28))
        select_btn.setStyleSheet(btn_style_primary)
        select_btn.clicked.connect(self.do_select)
        btn_layout.addWidget(select_btn)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setCursor(QtCore.Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(dpi(28))
        cancel_btn.setStyleSheet(btn_style_secondary)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        content_layout.addLayout(btn_layout)
        container_layout.addWidget(content_widget)
        main_layout.addWidget(container)
    
    def item_double_clicked(self, item):
        self.do_select()
    
    def do_select(self):
        current = self.list_widget.currentItem()
        if current:
            self.selected_item = current.text()
            self.selected_index = self.list_widget.currentRow()
            self.accept()
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    @staticmethod
    def get_item(parent, title, message, items):
        dialog = StyledListDialog(parent, title, message, items)
        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return dialog.selected_index, dialog.selected_item
        return -1, None


class CameraBookmarkUI(QtWidgets.QDialog):
    
    def __init__(self, parent=get_maya_main_window()):
        super(CameraBookmarkUI, self).__init__(parent)
        
        self.setObjectName("CameraBookmarkUIWindow")
        self.setWindowTitle("Fast Playblaster")
        
        window_flags = QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint
        if is_macos():
            window_flags |= QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(window_flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.dragging = False
        self.drag_position = QtCore.QPoint()
        self.script_jobs = []
        try:
            self.tracked_cameras = load_tracked_cameras()
        except Exception:
            self.tracked_cameras = []
        
        self.setup_ui()
        self.restore_window_position()
        
        self._safe_call(self._auto_add_scene_cameras)
        self._safe_call(self.refresh_bookmark_list)
        self._safe_call(self.refresh_camera_list)
        self._safe_call(self.restore_tab)
        
        self.setup_script_jobs()
    
    def _safe_call(self, func):
        try:
            func()
        except Exception:
            pass
    
    def setup_script_jobs(self):
        self.script_jobs = []
        self._last_cams = set()
        self._last_bookmarks = set()
        
        self.script_jobs.append(cmds.scriptJob(event=['SceneOpened', self.on_scene_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['NewSceneOpened', self.on_scene_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['PostSceneRead', self.on_scene_changed], protected=True))
        
        self.script_jobs.append(cmds.scriptJob(event=['DagObjectCreated', self.on_dag_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['NameChanged', self.on_dag_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['Undo', self.on_dag_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['Redo', self.on_dag_changed], protected=True))
        self.script_jobs.append(cmds.scriptJob(event=['SelectionChanged', self.on_selection_changed], protected=True))
        
        try:
            self.script_jobs.append(cmds.scriptJob(event=['deleteAll', self.on_dag_changed], protected=True))
        except Exception:
            pass
    
    def kill_script_jobs(self):
        for job_id in self.script_jobs:
            try:
                if cmds.scriptJob(exists=job_id):
                    cmds.scriptJob(kill=job_id, force=True)
            except Exception:
                pass
        self.script_jobs = []
    
    def on_scene_changed(self):
        try:
            self.refresh_camera_list()
            self.refresh_bookmark_list()
        except Exception:
            pass
    
    def on_dag_changed(self):
        try:
            cmds.evalDeferred(self.deferred_refresh, lowestPriority=True)
        except Exception:
            pass
    
    def on_selection_changed(self):
        try:
            cmds.evalDeferred(self.check_for_deletions, lowestPriority=True)
        except Exception:
            pass
    
    def deferred_refresh(self):
        try:
            self.refresh_camera_list()
            self.refresh_bookmark_list()
        except Exception:
            pass
    
    def check_for_deletions(self):
        try:
            current_cams = set(cmds.ls(type='camera') or [])
            current_bookmarks = set(cmds.ls(type='cameraView') or [])
            
            needs_refresh = False
            
            if current_cams != self._last_cams:
                self._last_cams = current_cams
                needs_refresh = True
            
            if current_bookmarks != self._last_bookmarks:
                self._last_bookmarks = current_bookmarks
                needs_refresh = True
            
            if needs_refresh:
                self.refresh_camera_list()
                self.refresh_bookmark_list()
        except Exception:
            pass
    
    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.container = QtWidgets.QWidget()
        self.container.setObjectName("mainContainer")
        self.container.setStyleSheet("""
            QWidget#mainContainer {
                background-color: rgba(26, 26, 26, 245);
                border-radius: 12px;
                border: 1px solid rgba(68, 68, 68, 180);
            }
        """)
        
        container_layout = QtWidgets.QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        title_bar = self.create_title_bar()
        container_layout.addWidget(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background: transparent; border: none;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(dpi(12), dpi(10), dpi(12), dpi(8))
        content_layout.setSpacing(dpi(1))
        
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background: transparent;
                border: none;
            }
            QTabWidget::pane {
                border: none;
                background-color: transparent;
            }
            QTabBar {
                qproperty-drawBase: 0;
            }
            QTabBar::tab {
                background-color: rgba(50, 50, 50, 200);
                color: #aaa;
                border: none;
                border-radius: 5px;
                padding: 6px 16px;
                margin-right: 4px;
                font-size: 8pt;
                font-weight: 600;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: rgba(180, 120, 18, 220);
                color: #fff;
            }
            QTabBar::tab:hover:!selected {
                background-color: rgba(80, 80, 80, 200);
                color: #fff;
            }
        """)
        
        self.cameras_tab = self.create_cameras_tab()
        self.bookmarks_tab = self.create_bookmarks_tab()
        
        self.tab_widget.addTab(self.cameras_tab, "CAMERAS")
        self.tab_widget.addTab(self.bookmarks_tab, "BOOKMARKS")
        self.tab_widget.currentChanged.connect(self.save_tab)
        self.tab_widget.setFixedHeight(dpi(310))
        
        content_layout.addWidget(self.tab_widget)
        
        options_widget = self.create_options_section()
        content_layout.addWidget(options_widget)
        
        export_widget = self.create_export_section()
        content_layout.addWidget(export_widget)
        
        spacer = QtWidgets.QSpacerItem(0, dpi(12), QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        content_layout.addItem(spacer)
        
        container_layout.addWidget(content_widget)
        main_layout.addWidget(self.container)
        
        self.setFixedSize(dpi(340), dpi(620))
    
    def create_title_bar(self):
        title_bar = QtWidgets.QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(dpi(42))
        title_bar.setStyleSheet("""
            QWidget#titleBar {
                background-color: rgba(35, 35, 35, 220);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid rgba(68, 68, 68, 150);
            }
        """)
        
        title_layout = QtWidgets.QHBoxLayout(title_bar)
        title_layout.setContentsMargins(dpi(12), 0, dpi(8), 0)
        title_layout.setSpacing(0)
        
        title_label = QtWidgets.QLabel("Fast Playblaster")
        title_label.setStyleSheet("""
            QLabel {
                color: #eee;
                font-size: 10pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        close_btn = QtWidgets.QPushButton("x")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(dpi(28), dpi(28))
        close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton#closeBtn {
                background-color: transparent;
                border: none;
                color: #888;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton#closeBtn:hover {
                background-color: #f39c12;
                color: #222;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        return title_bar
    
    def create_cameras_tab(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, dpi(10), 0, 0)
        layout.setSpacing(dpi(6))
        
        self.camera_list_container = QtWidgets.QWidget()
        self.camera_list_container.setFixedHeight(dpi(185))
        container_layout = QtWidgets.QVBoxLayout(self.camera_list_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.camera_list = QtWidgets.QListWidget()
        self.camera_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.camera_list.itemDoubleClicked.connect(self.activate_camera)
        self.camera_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.camera_list.customContextMenuRequested.connect(self.show_camera_context_menu)
        self.camera_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(42, 42, 42, 180);
                border: 1px solid rgba(68, 68, 68, 120);
                border-radius: 4px;
                color: #eee;
                font-size: 9pt;
                font-weight: bold;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid transparent;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: rgba(243, 156, 18, 200);
                color: #222;
                border-color: #f39c12;
            }
            QListWidget::item:selected {
                background-color: rgba(180, 120, 18, 200);
                color: #fff;
                border-color: #e67e22;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 100);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        container_layout.addWidget(self.camera_list)
        
        self.add_camera_btn = QtWidgets.QPushButton("+ ADD CAMERA")
        self.add_camera_btn.setFixedHeight(dpi(185))
        self.add_camera_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.add_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(42, 42, 42, 180);
                border: 1px dashed rgba(100, 100, 100, 150);
                border-radius: 4px;
                color: #888;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 200);
                border-color: #f39c12;
                color: #f39c12;
            }
        """)
        self.add_camera_btn.clicked.connect(self.show_add_camera_dialog)
        container_layout.addWidget(self.add_camera_btn)
        
        self.update_camera_list_visibility()
        
        layout.addWidget(self.camera_list_container)
        
        btn_container = QtWidgets.QWidget()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(dpi(4))
        
        self.cam_rename_btn = self.create_secondary_button("RENAME")
        self.cam_rename_btn.clicked.connect(self.rename_camera)
        btn_layout.addWidget(self.cam_rename_btn)
        
        self.cam_reload_btn = self.create_secondary_button("RELOAD")
        self.cam_reload_btn.clicked.connect(self.reload_camera_list)
        btn_layout.addWidget(self.cam_reload_btn)
        
        layout.addWidget(btn_container)
        
        self.playblast_cam_btn = self.create_primary_button("PLAYBLAST CAMERAS")
        self.playblast_cam_btn.clicked.connect(self.playblast_cameras)
        layout.addWidget(self.playblast_cam_btn)
        
        layout.addStretch()
        
        return widget
    
    def update_camera_list_visibility(self):
        has_items = self.camera_list.count() > 0
        self.camera_list.setVisible(has_items)
        self.add_camera_btn.setVisible(not has_items)
    
    def show_add_camera_dialog(self):
        dialog = AddCameraDialog(self)
        dialog.cameras_added.connect(self.on_cameras_added)
        dialog.exec_()
    
    def create_bookmarks_tab(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, dpi(10), 0, 0)
        layout.setSpacing(dpi(6))
        
        self.bookmark_list = QtWidgets.QListWidget()
        self.bookmark_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.bookmark_list.itemDoubleClicked.connect(self.activate_bookmark)
        self.bookmark_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.bookmark_list.customContextMenuRequested.connect(self.show_bookmark_context_menu)
        self.bookmark_list.setFixedHeight(dpi(185))
        self.bookmark_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(42, 42, 42, 180);
                border: 1px solid rgba(68, 68, 68, 120);
                border-radius: 4px;
                color: #eee;
                font-size: 9pt;
                font-weight: bold;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
                border: 1px solid transparent;
                margin: 1px;
            }
            QListWidget::item:hover {
                background-color: rgba(243, 156, 18, 200);
                color: #222;
                border-color: #f39c12;
            }
            QListWidget::item:selected {
                background-color: rgba(180, 120, 18, 200);
                color: #fff;
                border-color: #e67e22;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 60);
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(255, 255, 255, 100);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        layout.addWidget(self.bookmark_list)
        
        btn_container = QtWidgets.QWidget()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(dpi(4))
        
        self.bm_rename_btn = self.create_secondary_button("RENAME")
        self.bm_rename_btn.clicked.connect(self.rename_bookmark)
        btn_layout.addWidget(self.bm_rename_btn)
        
        self.bm_reload_btn = self.create_secondary_button("RELOAD")
        self.bm_reload_btn.clicked.connect(self.refresh_bookmark_list)
        btn_layout.addWidget(self.bm_reload_btn)
        
        layout.addWidget(btn_container)
        
        self.playblast_bm_btn = self.create_primary_button("PLAYBLAST BOOKMARKS")
        self.playblast_bm_btn.clicked.connect(self.playblast_bookmarks)
        layout.addWidget(self.playblast_bm_btn)
        
        layout.addStretch()
        
        return widget
    
    def create_options_section(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, dpi(6), 0, 0)
        layout.setSpacing(dpi(5))
        
        header = QtWidgets.QLabel("Playblast Options")
        header.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: bold;
                color: #eee;
                background: transparent;
            }
        """)
        layout.addWidget(header)
        
        options_container = QtWidgets.QWidget()
        options_container.setObjectName("optionsContainer")
        options_container.setStyleSheet("""
            QWidget#optionsContainer {
                background-color: rgba(42, 42, 42, 180);
                border: 1px solid rgba(68, 68, 68, 120);
                border-radius: 4px;
            }
        """)
        
        options_layout = QtWidgets.QVBoxLayout(options_container)
        options_layout.setContentsMargins(dpi(10), dpi(8), dpi(10), dpi(8))
        options_layout.setSpacing(dpi(16))
        
        # Resolution dropdown row
        res_row = QtWidgets.QHBoxLayout()
        res_row.setSpacing(dpi(8))
        
        res_label = QtWidgets.QLabel("Resolution:")
        res_label.setStyleSheet("color: #ccc; font-size: 8pt; background: transparent;")
        res_row.addWidget(res_label)
        
        self.resolution_combo = QtWidgets.QComboBox()
        self.resolution_combo.addItem("From Render Settings")
        self.resolution_combo.addItem("From Window")
        self.resolution_combo.setCurrentIndex(load_option(OPT_RESOLUTION_SOURCE, 0))
        self.resolution_combo.currentIndexChanged.connect(lambda idx: save_option(OPT_RESOLUTION_SOURCE, idx))
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                border-radius: 4px;
                color: #ddd;
                font-size: 8pt;
                padding: 4px 8px;
                min-width: 140px;
            }
            QComboBox:hover {
                border-color: #f39c12;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #aaa;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(45, 45, 45, 250);
                border: 1px solid rgba(80, 80, 80, 150);
                selection-background-color: rgba(243, 156, 18, 200);
                selection-color: #222;
                color: #ddd;
                outline: none;
            }
        """)
        res_row.addWidget(self.resolution_combo)
        res_row.addStretch()
        
        options_layout.addLayout(res_row)
        
        # Checkbox columns
        checkbox_row = QtWidgets.QHBoxLayout()
        checkbox_row.setSpacing(dpi(10))
        
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(dpi(6))
        
        self.chk_geometry = self.create_checkbox("Geometry", load_option(OPT_GEOMETRY, True))
        self.chk_geometry.stateChanged.connect(lambda: save_option(OPT_GEOMETRY, self.chk_geometry.isChecked()))
        left_col.addWidget(self.chk_geometry)
        
        self.chk_nurbs_curves = self.create_checkbox("NURBS Curves", load_option(OPT_NURBS_CURVES, False))
        self.chk_nurbs_curves.stateChanged.connect(lambda: save_option(OPT_NURBS_CURVES, self.chk_nurbs_curves.isChecked()))
        left_col.addWidget(self.chk_nurbs_curves)
        
        self.chk_grid = self.create_checkbox("Grid", load_option(OPT_GRID, False))
        self.chk_grid.stateChanged.connect(lambda: save_option(OPT_GRID, self.chk_grid.isChecked()))
        left_col.addWidget(self.chk_grid)
        
        self.chk_shadows = self.create_checkbox("Shadows", load_option(OPT_SHADOWS, False))
        self.chk_shadows.stateChanged.connect(lambda: save_option(OPT_SHADOWS, self.chk_shadows.isChecked()))
        left_col.addWidget(self.chk_shadows)
        
        checkbox_row.addLayout(left_col)
        
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(dpi(6))
        
        self.chk_locators = self.create_checkbox("Locators", load_option(OPT_LOCATORS, False))
        self.chk_locators.stateChanged.connect(lambda: save_option(OPT_LOCATORS, self.chk_locators.isChecked()))
        right_col.addWidget(self.chk_locators)
        
        self.chk_image_planes = self.create_checkbox("Image Planes", load_option(OPT_IMAGE_PLANES, False))
        self.chk_image_planes.stateChanged.connect(lambda: save_option(OPT_IMAGE_PLANES, self.chk_image_planes.isChecked()))
        right_col.addWidget(self.chk_image_planes)
        
        self.chk_lights = self.create_checkbox("Scene Lights", load_option(OPT_LIGHTS, False))
        self.chk_lights.stateChanged.connect(lambda: save_option(OPT_LIGHTS, self.chk_lights.isChecked()))
        right_col.addWidget(self.chk_lights)
        
        checkbox_row.addLayout(right_col)
        
        options_layout.addLayout(checkbox_row)
        
        layout.addWidget(options_container)
        
        return widget
    
    def create_export_section(self):
        widget = QtWidgets.QWidget()
        widget.setStyleSheet("background: transparent; border: none;")
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, dpi(12), 0, dpi(6))
        layout.setSpacing(dpi(5))
        
        header = QtWidgets.QLabel("Export / Import")
        header.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                font-weight: bold;
                color: #eee;
                background: transparent;
            }
        """)
        layout.addWidget(header)
        
        btn_container = QtWidgets.QWidget()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QtWidgets.QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(dpi(5))
        
        self.export_btn = self.create_primary_button("EXPORT")
        self.export_btn.clicked.connect(self.show_export_dialog)
        btn_layout.addWidget(self.export_btn)
        
        self.import_btn = self.create_primary_button("IMPORT")
        self.import_btn.clicked.connect(self.show_import_dialog)
        btn_layout.addWidget(self.import_btn)
        
        layout.addWidget(btn_container)
        
        return widget
    
    def create_primary_button(self, text):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(dpi(32))
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(179, 119, 0, 220);
                border: 1px solid rgba(153, 102, 0, 200);
                color: #fff;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(217, 145, 0, 220);
            }
            QPushButton:pressed {
                background-color: rgba(230, 158, 0, 220);
            }
        """)
        return btn
    
    def create_secondary_button(self, text):
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(dpi(30))
        btn.setCursor(QtCore.Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: 1px solid rgba(80, 80, 80, 150);
                color: #ddd;
                border-radius: 4px;
                font-size: 7pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(243, 156, 18, 200);
                border-color: #f39c12;
                color: #222;
            }
            QPushButton:pressed {
                background-color: rgba(230, 145, 10, 200);
            }
        """)
        return btn
    
    def create_checkbox(self, text, checked=False):
        chk = QtWidgets.QCheckBox(text)
        chk.setChecked(checked)
        chk.setCursor(QtCore.Qt.PointingHandCursor)
        chk.setStyleSheet("""
            QCheckBox {
                color: #ccc;
                font-size: 8pt;
                spacing: 5px;
                background: transparent;
            }
            QCheckBox::indicator {
                width: 13px;
                height: 13px;
                border-radius: 3px;
                border: 1px solid #666;
                background-color: rgba(30, 30, 30, 200);
            }
            QCheckBox::indicator:checked {
                background-color: #f39c12;
                border-color: #e67e22;
            }
            QCheckBox::indicator:hover {
                border-color: #f39c12;
            }
        """)
        return chk
    
    def create_context_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(42, 42, 42, 245);
                color: #eee;
                border: 1px solid rgba(68, 68, 68, 180);
                border-radius: 4px;
                padding: 4px;
                font-size: 9pt;
                font-weight: bold;
            }
            QMenu::item {
                padding: 5px 16px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #f39c12;
                color: #222;
            }
            QMenu::separator {
                height: 1px;
                background-color: rgba(85, 85, 85, 150);
                margin: 4px 8px;
            }
        """)
        return menu
    
    def show_camera_context_menu(self, pos):
        item = self.camera_list.itemAt(pos)
        if item:
            item.setSelected(True)
            self.camera_list.setCurrentItem(item)
        menu = self.create_context_menu()
        menu.addAction("Look Through", self.activate_camera)
        menu.addSeparator()
        menu.addAction("Where to Save...", self.set_camera_output)
        menu.addAction("Open Output Directory", self.open_selected_camera_dir)
        menu.exec_(self.camera_list.mapToGlobal(pos))
    
    def _auto_add_scene_cameras(self):
        all_cams = cmds.ls(type='camera', long=True) or []
        skip_cams = ['perspShape']
        added = []
        
        for cam_shape in sorted(all_cams):
            if cam_shape.split('|')[-1] in skip_cams:
                continue
            
            try:
                cam_transforms = resolve_camera_transform_names(cam_shape)
                for cam_transform in cam_transforms:
                    if cam_transform not in self.tracked_cameras and cmds.objExists(cam_transform):
                        self.tracked_cameras.append(cam_transform)
                        added.append(cam_transform)
            except Exception:
                continue
        
        if added:
            save_tracked_cameras(self.tracked_cameras)
        
        return added
    
    def reload_camera_list(self):
        added = self._auto_add_scene_cameras()
        
        self.refresh_camera_list()
        
        if added:
            show_feedback_message('Added {0} new camera(s)'.format(len(added)))
        else:
            show_feedback_message('Camera list reloaded')
        
        self.clear_focus()
    
    def show_bookmark_context_menu(self, pos):
        item = self.bookmark_list.itemAt(pos)
        if item:
            item.setSelected(True)
            self.bookmark_list.setCurrentItem(item)
        menu = self.create_context_menu()
        menu.addAction("Activate", self.activate_bookmark)
        menu.addAction("Update from View", self.update_bookmark_from_view)
        menu.addSeparator()
        menu.addAction("Where to Save...", self.set_bookmark_output)
        menu.addAction("Open Output Directory", self.open_selected_bookmark_dir)
        menu.addSeparator()
        menu.addAction("Delete", self.delete_bookmark)
        menu.exec_(self.bookmark_list.mapToGlobal(pos))
    
    def restore_window_position(self):
        saved_pos = load_window_position()
        if saved_pos:
            if PYSIDE_VERSION == 6:
                screen = QGuiApplication.primaryScreen().geometry()
            else:
                screen = QtWidgets.QApplication.desktop().screenGeometry()
            
            window_width = self.width()
            window_height = self.height()
            
            if (saved_pos.x() >= 0 and saved_pos.y() >= 0 and
                saved_pos.x() < screen.width() - window_width and
                saved_pos.y() < screen.height() - window_height):
                self.move(saved_pos)
    
    def save_tab(self):
        cmds.optionVar(intValue=(OPT_ACTIVE_TAB, self.tab_widget.currentIndex() + 1))
    
    def restore_tab(self):
        if cmds.optionVar(exists=OPT_ACTIVE_TAB):
            tab_index = cmds.optionVar(query=OPT_ACTIVE_TAB) - 1
            if 0 <= tab_index < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(tab_index)
    
    def closeEvent(self, event):
        self.kill_script_jobs()
        save_window_position(self.pos())
        QtWidgets.QDialog.closeEvent(self, event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            title_bar_height = dpi(36)
            if event.pos().y() <= title_bar_height:
                self.dragging = True
                if hasattr(event, 'globalPosition'):
                    self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                else:
                    self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == QtCore.Qt.LeftButton:
            if hasattr(event, 'globalPosition'):
                self.move(event.globalPosition().toPoint() - self.drag_position)
            else:
                self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def clear_focus(self):
        try:
            cmds.setFocus("MayaWindow")
        except Exception:
            pass
    
    def refresh_camera_list(self):
        self.camera_list.clear()
        
        valid_cameras = []
        for cam in self.tracked_cameras:
            try:
                resolved = resolve_ambiguous_transform_name(cam)
                if resolved and resolved not in valid_cameras:
                    valid_cameras.append(resolved)
            except Exception:
                continue
        
        if valid_cameras != self.tracked_cameras:
            self.tracked_cameras = valid_cameras
            save_tracked_cameras(self.tracked_cameras)
        else:
            self.tracked_cameras = valid_cameras
        
        for cam_transform in sorted(self.tracked_cameras):
            try:
                short_name = cam_transform.split('|')[-1] if '|' in cam_transform else cam_transform
                path = get_playblast_path(cam_transform)
                filename = get_playblast_filename(cam_transform)
                if path and filename:
                    display = '{0}  ->  {1}'.format(short_name, filename)
                else:
                    display = short_name
                item = QtWidgets.QListWidgetItem(display)
                item.setData(QtCore.Qt.UserRole, cam_transform)
                self.camera_list.addItem(item)
            except Exception:
                item = QtWidgets.QListWidgetItem(cam_transform)
                item.setData(QtCore.Qt.UserRole, cam_transform)
                self.camera_list.addItem(item)
        
        self.update_camera_list_visibility()
        self.clear_focus()
    
    def on_cameras_added(self, cameras):
        for cam in cameras:
            if cam not in self.tracked_cameras and cmds.objExists(cam):
                self.tracked_cameras.append(cam)
        save_tracked_cameras(self.tracked_cameras)
        self.refresh_camera_list()
    
    def refresh_bookmark_list(self):
        self.bookmark_list.clear()
        camera_views = cmds.ls(type='cameraView') or []
        for cv in sorted(camera_views):
            try:
                short_name = cv.split('|')[-1] if '|' in cv else cv
                path = get_playblast_path(cv)
                filename = get_playblast_filename(cv)
                if path and filename:
                    display = '{0}  ->  {1}'.format(short_name, filename)
                else:
                    display = short_name
                item = QtWidgets.QListWidgetItem(display)
                item.setData(QtCore.Qt.UserRole, cv)
                self.bookmark_list.addItem(item)
            except Exception:
                item = QtWidgets.QListWidgetItem(cv)
                item.setData(QtCore.Qt.UserRole, cv)
                self.bookmark_list.addItem(item)
        self.clear_focus()
    
    def get_selected_cameras(self):
        selected = self.camera_list.selectedItems()
        if selected:
            cameras = []
            for s in selected:
                data = s.data(QtCore.Qt.UserRole)
                if data:
                    cameras.append(data)
                    continue
                text = s.text()
                if '  ->  ' in text:
                    cameras.append(text.split('  ->  ')[0].strip())
                elif ' -> ' in text:
                    cameras.append(text.split(' -> ')[0].strip())
                else:
                    cameras.append(text.strip())
            return cameras
        return []
    
    def get_selected_camera(self):
        items = self.get_selected_cameras()
        return items[0] if items else None
    
    def get_selected_bookmarks(self):
        selected = self.bookmark_list.selectedItems()
        if selected:
            bookmarks = []
            for s in selected:
                data = s.data(QtCore.Qt.UserRole)
                if data:
                    bookmarks.append(data)
                    continue
                text = s.text()
                if '  ->  ' in text:
                    bookmarks.append(text.split('  ->  ')[0].strip())
                elif ' -> ' in text:
                    bookmarks.append(text.split(' -> ')[0].strip())
                else:
                    bookmarks.append(text.strip())
            return bookmarks
        return []
    
    def get_selected_bookmark(self):
        items = self.get_selected_bookmarks()
        return items[0] if items else None
    
    def activate_camera(self):
        selected = self.get_selected_camera()
        if not selected or not cmds.objExists(selected):
            return
        
        cmds.setFocus("MayaWindow")
        
        active_panel = cmds.getPanel(withFocus=True)
        if not active_panel or cmds.getPanel(typeOf=active_panel) != 'modelPanel':
            visible_panels = cmds.getPanel(visiblePanels=True) or []
            for p in visible_panels:
                if cmds.getPanel(typeOf=p) == 'modelPanel':
                    active_panel = p
                    break
        
        if active_panel and cmds.getPanel(typeOf=active_panel) == 'modelPanel':
            cmds.lookThru(active_panel, selected)
            show_feedback_message('Looking through "{0}"'.format(short_display_name(selected)))
        self.clear_focus()
    
    def activate_bookmark(self):
        selected = self.get_selected_bookmark()
        if not selected or not cmds.objExists(selected):
            return
        
        cmds.setFocus("MayaWindow")
        
        active_panel = cmds.getPanel(withFocus=True)
        if not active_panel or cmds.getPanel(typeOf=active_panel) != 'modelPanel':
            visible_panels = cmds.getPanel(visiblePanels=True) or []
            for p in visible_panels:
                if cmds.getPanel(typeOf=p) == 'modelPanel':
                    active_panel = p
                    break
        
        if active_panel and cmds.getPanel(typeOf=active_panel) == 'modelPanel':
            camera = cmds.modelPanel(active_panel, query=True, camera=True)
        else:
            camera = 'persp'
        
        if cmds.nodeType(camera) != 'transform':
            parents = cmds.listRelatives(camera, parent=True)
            camera = parents[0] if parents else 'persp'
        
        try:
            cmds.cameraView(selected, edit=True, camera=camera, setCamera=True)
            show_feedback_message('Activated bookmark "{0}"'.format(short_display_name(selected)))
        except Exception:
            apply_bookmark_to_camera(selected, camera)
        self.clear_focus()
    
    def delete_bookmark(self):
        selected = self.get_selected_bookmarks()
        if not selected:
            return
        
        result = StyledMessageBox.show_message(
            self,
            'Delete',
            'Delete {0} bookmark(s)?'.format(len(selected)),
            ['Delete', 'Cancel']
        )
        
        if result == 'Delete':
            for bm in selected:
                if cmds.objExists(bm):
                    cmds.delete(bm)
            self.refresh_bookmark_list()
        self.clear_focus()
    
    def rename_bookmark(self):
        selected = self.get_selected_bookmarks()
        selected = [b for b in selected if cmds.objExists(b)]
        if not selected:
            return
        
        if len(selected) == 1:
            default_text = selected[0]
            message = 'New name:'
        else:
            default_text = ''
            message = 'New base name for {0} bookmarks:'.format(len(selected))
        
        result, new_name = StyledInputDialog.get_text(
            self,
            'Rename Bookmark',
            message,
            default_text,
            ['Rename', 'Cancel']
        )
        
        if result != 'Rename':
            self.clear_focus()
            return
        
        new_name = new_name.strip()
        if not new_name:
            self.clear_focus()
            return
        
        if len(selected) == 1:
            old_name = selected[0]
            if new_name != old_name and not cmds.objExists(new_name):
                cmds.rename(old_name, new_name)
        else:
            suffix = 1
            for old_name in selected:
                candidate = '{0}_{1:02d}'.format(new_name, suffix)
                while cmds.objExists(candidate) and candidate != old_name:
                    suffix += 1
                    candidate = '{0}_{1:02d}'.format(new_name, suffix)
                
                if candidate != old_name:
                    cmds.rename(old_name, candidate)
                
                suffix += 1
        
        self.refresh_bookmark_list()
        self.clear_focus()
    
    def rename_camera(self):
        selected = self.get_selected_cameras()
        selected = [c for c in selected if cmds.objExists(c)]
        if not selected:
            return
        
        if len(selected) == 1:
            default_text = selected[0]
            message = 'New name:'
        else:
            default_text = ''
            message = 'New base name for {0} cameras:'.format(len(selected))
        
        result, new_name = StyledInputDialog.get_text(
            self,
            'Rename Camera',
            message,
            default_text,
            ['Rename', 'Cancel']
        )
        
        if result != 'Rename':
            self.clear_focus()
            return
        
        new_name = new_name.strip()
        if not new_name:
            self.clear_focus()
            return
        
        if len(selected) == 1:
            old_name = selected[0]
            if new_name != old_name and not cmds.objExists(new_name):
                actual_name = cmds.rename(old_name, new_name)
                if old_name in self.tracked_cameras:
                    idx = self.tracked_cameras.index(old_name)
                    self.tracked_cameras[idx] = actual_name
                    save_tracked_cameras(self.tracked_cameras)
        else:
            suffix = 1
            for old_name in selected:
                candidate = '{0:02d}_{1}'.format(suffix, new_name)
                while cmds.objExists(candidate) and candidate != old_name:
                    suffix += 1
                    candidate = '{0:02d}_{1}'.format(suffix, new_name)
                
                if candidate != old_name:
                    actual_name = cmds.rename(old_name, candidate)
                    if old_name in self.tracked_cameras:
                        idx = self.tracked_cameras.index(old_name)
                        self.tracked_cameras[idx] = actual_name
                
                suffix += 1
            
            save_tracked_cameras(self.tracked_cameras)
        
        self.refresh_camera_list()
        self.clear_focus()
    
    def set_camera_output(self):
        selected = self.get_selected_cameras()
        if not selected:
            return
        
        # Filter to existing cameras
        selected = [c for c in selected if cmds.objExists(c)]
        if not selected:
            return
        
        # Get starting directory from first selected item
        current_path = get_playblast_path(selected[0])
        if not current_path:
            scene_path = cmds.file(query=True, sceneName=True)
            current_path = os.path.dirname(scene_path) if scene_path else cmds.workspace(query=True, rootDirectory=True)
        
        if len(selected) == 1:
            # Single selection - use file dialog
            result = cmds.fileDialog2(
                fileFilter='Movie (*.mov *.avi);;All Files (*.*)',
                dialogStyle=2,
                fileMode=0,
                caption='Set Output for "{0}"'.format(selected[0]),
                startingDirectory=current_path
            )
            
            if result:
                directory = os.path.dirname(result[0])
                filename = os.path.splitext(os.path.basename(result[0]))[0]
                set_playblast_path(selected[0], directory)
                set_playblast_filename(selected[0], filename)
        else:
            # Multiple selection - use folder dialog, use camera names as filenames
            result = cmds.fileDialog2(
                dialogStyle=2,
                fileMode=3,
                caption='Set Output Directory for {0} Cameras'.format(len(selected)),
                startingDirectory=current_path
            )
            
            if result:
                directory = result[0]
                for cam in selected:
                    set_playblast_path(cam, directory)
                    set_playblast_filename(cam, cam)
        
        self.refresh_camera_list()
        self.clear_focus()
    
    def set_bookmark_output(self):
        selected = self.get_selected_bookmarks()
        if not selected:
            return
        
        # Filter to existing bookmarks
        selected = [b for b in selected if cmds.objExists(b)]
        if not selected:
            return
        
        # Get starting directory from first selected item
        current_path = get_playblast_path(selected[0])
        if not current_path:
            scene_path = cmds.file(query=True, sceneName=True)
            current_path = os.path.dirname(scene_path) if scene_path else cmds.workspace(query=True, rootDirectory=True)
        
        if len(selected) == 1:
            # Single selection - use file dialog
            result = cmds.fileDialog2(
                fileFilter='Movie (*.mov *.avi);;All Files (*.*)',
                dialogStyle=2,
                fileMode=0,
                caption='Set Output for "{0}"'.format(selected[0]),
                startingDirectory=current_path
            )
            
            if result:
                directory = os.path.dirname(result[0])
                filename = os.path.splitext(os.path.basename(result[0]))[0]
                set_playblast_path(selected[0], directory)
                set_playblast_filename(selected[0], filename)
        else:
            # Multiple selection - use folder dialog, use bookmark names as filenames
            result = cmds.fileDialog2(
                dialogStyle=2,
                fileMode=3,
                caption='Set Output Directory for {0} Bookmarks'.format(len(selected)),
                startingDirectory=current_path
            )
            
            if result:
                directory = result[0]
                for bm in selected:
                    set_playblast_path(bm, directory)
                    set_playblast_filename(bm, bm)
        
        self.refresh_bookmark_list()
        self.clear_focus()
    
    def update_bookmark_from_view(self):
        selected = self.get_selected_bookmark()
        if not selected or not cmds.objExists(selected):
            cmds.warning('No bookmark selected.')
            return
        
        all_cams = cmds.ls(type='camera', long=True) or []
        cam_transforms = []
        for cam_shape in all_cams:
            try:
                cam_transforms.extend(resolve_camera_transform_names(cam_shape))
            except Exception:
                continue
        
        cam_transforms = sorted(set(cam_transforms))
        
        if not cam_transforms:
            cmds.warning('No cameras found.')
            return
        
        dialog_name = 'updateBookmarkDialog'
        if cmds.window(dialog_name, exists=True):
            cmds.deleteUI(dialog_name)
        
        self._update_dialog_bookmark = selected
        self._update_dialog_cameras = cam_transforms
        
        dialog = cmds.window(dialog_name, title='Update Bookmark', widthHeight=(280, 140), sizeable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8, columnAttach=('both', 15))
        
        cmds.separator(height=10, style='none')
        cmds.text(label='Update "{0}" from camera:'.format(selected), align='left')
        
        self._update_cam_menu = cmds.optionMenu()
        for cam in cam_transforms:
            cmds.menuItem(label=cam)
        
        if 'persp' in cam_transforms:
            cmds.optionMenu(self._update_cam_menu, edit=True, value='persp')
        
        cmds.separator(height=5, style='none')
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(120, 120), columnAttach2=['both', 'both'], columnOffset2=[5, 5])
        cmds.button(label='Update', command=self._execute_update_bookmark, backgroundColor=(0.7, 0.5, 0.1))
        cmds.button(label='Cancel', command=lambda x: cmds.deleteUI(dialog_name))
        cmds.setParent('..')
        
        cmds.separator(height=10, style='none')
        
        cmds.showWindow(dialog)
        self.clear_focus()
    
    def _execute_update_bookmark(self, *args):
        bookmark = self._update_dialog_bookmark
        selected_cam = cmds.optionMenu(self._update_cam_menu, query=True, value=True)
        
        cam_shapes = cmds.listRelatives(selected_cam, shapes=True, type='camera')
        if not cam_shapes:
            cmds.warning('No camera shape found for {0}'.format(selected_cam))
            cmds.deleteUI('updateBookmarkDialog')
            return
        
        cam_shape = cam_shapes[0]
        
        try:
            import maya.api.OpenMaya as om
            
            eye = cmds.xform(selected_cam, query=True, worldSpace=True, translation=True)
            coi_distance = cmds.getAttr('{0}.centerOfInterest'.format(cam_shape))
            
            sel = om.MSelectionList()
            sel.add(selected_cam)
            dag_path = sel.getDagPath(0)
            world_matrix = dag_path.inclusiveMatrix()
            
            local_coi = om.MPoint(0, 0, -coi_distance)
            world_coi = local_coi * world_matrix
            coi = [world_coi.x, world_coi.y, world_coi.z]
            
            local_up = om.MVector(0, 1, 0)
            world_up = local_up * world_matrix
            up = [world_up.x, world_up.y, world_up.z]
            
            cmds.setAttr('{0}.eye'.format(bookmark), eye[0], eye[1], eye[2])
            cmds.setAttr('{0}.centerOfInterest'.format(bookmark), coi[0], coi[1], coi[2])
            cmds.setAttr('{0}.up'.format(bookmark), up[0], up[1], up[2])
            
            if cmds.attributeQuery('focalLength', node=bookmark, exists=True):
                cmds.setAttr('{0}.focalLength'.format(bookmark), cmds.getAttr('{0}.focalLength'.format(cam_shape)))
            
            show_feedback_message('Updated bookmark "{0}"'.format(short_display_name(bookmark)))
            
        except Exception as e:
            cmds.warning('Failed to update bookmark: {0}'.format(str(e)))
        
        cmds.deleteUI('updateBookmarkDialog')
        self.clear_focus()
    
    def playblast_cameras(self):
        selected = self.get_selected_cameras()
        if not selected:
            cmds.warning('No cameras selected.')
            return
        self._do_playblast(selected, is_camera=True)
        self.clear_focus()
    
    def playblast_bookmarks(self):
        selected = self.get_selected_bookmarks()
        if not selected:
            cmds.warning('No bookmarks selected.')
            return
        self._do_playblast(selected, is_camera=False)
        self.clear_focus()
    
    def open_selected_camera_dir(self):
        selected = self.get_selected_camera()
        if not selected:
            cmds.warning('No camera selected for open dir')
            return
        self._open_item_dir(selected)
        self.clear_focus()
    
    def open_selected_bookmark_dir(self):
        selected = self.get_selected_bookmark()
        if not selected:
            cmds.warning('No bookmark selected for open dir')
            return
        self._open_item_dir(selected)
        self.clear_focus()
    
    def _open_item_dir(self, item):
        if not item:
            cmds.warning('No item provided to open directory')
            return
            
        if not cmds.objExists(item):
            StyledMessageBox.show_message(
                self,
                'Error',
                'Node does not exist: {0}'.format(item),
                ['OK']
            )
            return
        
        path = get_playblast_path(item)
        
        if not path or not path.strip():
            StyledMessageBox.show_message(
                self,
                'No Path Set',
                'No playblast output path set for:\n{0}'.format(item),
                ['OK']
            )
            return
        
        path = path.strip()
        
        if os.path.exists(path):
            if is_macos():
                subprocess.Popen(['open', path])
            else:
                # Use os.startfile on Windows - more reliable
                if hasattr(os, 'startfile'):
                    os.startfile(path)
                else:
                    subprocess.Popen(['explorer', path])
        else:
            StyledMessageBox.show_message(
                self,
                'Directory Not Found',
                'Directory does not exist:\n{0}'.format(path),
                ['OK']
            )
    
    def _prompt_missing_outputs(self, missing, is_camera):
        current_path = get_playblast_path(missing[0])
        if not current_path:
            scene_path = cmds.file(query=True, sceneName=True)
            current_path = os.path.dirname(scene_path) if scene_path else cmds.workspace(query=True, rootDirectory=True)
        
        if len(missing) == 1:
            result = cmds.fileDialog2(
                fileFilter='Movie (*.mov *.avi);;All Files (*.*)',
                dialogStyle=2,
                fileMode=0,
                caption='Set Output for "{0}"'.format(missing[0]),
                startingDirectory=current_path
            )
            
            if not result:
                return None
            
            directory = os.path.dirname(result[0])
            filename = os.path.splitext(os.path.basename(result[0]))[0]
            set_playblast_path(missing[0], directory)
            set_playblast_filename(missing[0], filename)
        else:
            result = cmds.fileDialog2(
                dialogStyle=2,
                fileMode=3,
                caption='Set Output Directory for {0} Item(s)'.format(len(missing)),
                startingDirectory=current_path
            )
            
            if not result:
                return None
            
            directory = result[0]
            for name in missing:
                set_playblast_path(name, directory)
                set_playblast_filename(name, name)
        
        if is_camera:
            self.refresh_camera_list()
        else:
            self.refresh_bookmark_list()
        
        return directory
    
    def _apply_existing_output_to_missing(self, items, missing, is_camera):
        source_path = None
        for item in items:
            if item not in missing:
                candidate = get_playblast_path(item)
                if candidate:
                    source_path = candidate
                    break
        
        if not source_path:
            return self._prompt_missing_outputs(missing, is_camera)
        
        for name in missing:
            set_playblast_path(name, source_path)
            set_playblast_filename(name, name)
        
        if is_camera:
            self.refresh_camera_list()
        else:
            self.refresh_bookmark_list()
        
        return source_path
    
    def _get_all_tracked_names(self, is_camera):
        if is_camera:
            return list(self.tracked_cameras)
        return cmds.ls(type='cameraView') or []
    
    def _propagate_output_to_unset(self, directory, exclude, is_camera):
        all_names = self._get_all_tracked_names(is_camera)
        changed = False
        
        for name in all_names:
            if name in exclude:
                continue
            if not cmds.objExists(name):
                continue
            if get_playblast_path(name) and get_playblast_filename(name):
                continue
            
            set_playblast_path(name, directory)
            set_playblast_filename(name, name)
            changed = True
        
        if changed:
            if is_camera:
                self.refresh_camera_list()
            else:
                self.refresh_bookmark_list()
    
    def _do_playblast(self, items, is_camera=False):
        missing = [i for i in items if not get_playblast_path(i) or not get_playblast_filename(i)]
        if missing:
            if len(missing) < len(items):
                output_directory = self._apply_existing_output_to_missing(items, missing, is_camera)
            else:
                output_directory = self._prompt_missing_outputs(missing, is_camera)
            
            if not output_directory:
                return
            
            self._propagate_output_to_unset(output_directory, items, is_camera)
        
        result = StyledMessageBox.show_message(
            self,
            'Playblast',
            'Playblast {0} item(s)?\nExisting files will be replaced.'.format(len(items)),
            ['Playblast', 'Cancel']
        )
        if result != 'Playblast':
            return
        
        cmds.setFocus("MayaWindow")
        
        start_frame = int(cmds.playbackOptions(query=True, min=True))
        end_frame = int(cmds.playbackOptions(query=True, max=True))
        
        # Get resolution based on dropdown selection
        use_window_size = self.resolution_combo.currentIndex() == 1
        
        if use_window_size:
            # Get resolution from active viewport
            active_panel = cmds.getPanel(withFocus=True)
            if not active_panel or cmds.getPanel(typeOf=active_panel) != 'modelPanel':
                visible_panels = cmds.getPanel(visiblePanels=True) or []
                for p in visible_panels:
                    if cmds.getPanel(typeOf=p) == 'modelPanel':
                        active_panel = p
                        break
            
            if active_panel and cmds.getPanel(typeOf=active_panel) == 'modelPanel':
                # Get the model editor control
                editor = cmds.modelPanel(active_panel, query=True, modelEditor=True)
                # Get viewport dimensions
                width = cmds.control(active_panel, query=True, width=True)
                height = cmds.control(active_panel, query=True, height=True)
                if not width or not height:
                    width = 1920
                    height = 1080
            else:
                width = 1920
                height = 1080
        else:
            # Get resolution from render settings
            width = int(cmds.getAttr('defaultResolution.width'))
            height = int(cmds.getAttr('defaultResolution.height'))
        
        show_geo = self.chk_geometry.isChecked()
        show_curves = self.chk_nurbs_curves.isChecked()
        show_loc = self.chk_locators.isChecked()
        show_img = self.chk_image_planes.isChecked()
        show_lights = self.chk_lights.isChecked()
        show_grid = self.chk_grid.isChecked()
        show_shadows = self.chk_shadows.isChecked()
        
        success = 0
        errors = []
        
        for item in items:
            if not cmds.objExists(item):
                errors.append('{0}: Node does not exist'.format(item))
                continue
            
            path = get_playblast_path(item)
            filename = get_playblast_filename(item)
            
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
            except Exception as e:
                errors.append('{0}: Cannot create directory - {1}'.format(item, str(e)))
                continue
            
            uid = str(uuid.uuid4())[:8]
            win_name = 'pb_win_{0}'.format(uid)
            panel_name = 'pb_panel_{0}'.format(uid)
            temp_cam = None
            restore_data = None
            cam_to_use = None
            
            try:
                if is_camera:
                    cam_to_use = item
                    temp_cam = None
                    restore_data = None
                else:
                    # Find the camera this bookmark is connected to
                    temp_cam = None
                    connections = cmds.listConnections('{0}.message'.format(item), type='camera') or []
                    
                    if connections:
                        cam_shape = connections[0]
                        cam_transforms = resolve_camera_transform_names(cam_shape)
                        if cam_transforms:
                            cam_to_use = cam_transforms[0]
                        else:
                            cam_to_use = cam_shape
                        
                        # Store current camera state to restore later
                        restore_data = {
                            'translate': cmds.getAttr('{0}.translate'.format(cam_to_use))[0],
                            'rotate': cmds.getAttr('{0}.rotate'.format(cam_to_use))[0],
                            'focalLength': cmds.getAttr('{0}.focalLength'.format(cam_shape)),
                            'centerOfInterest': cmds.getAttr('{0}.centerOfInterest'.format(cam_shape)),
                        }
                        
                        # Apply the bookmark to the camera
                        cmds.cameraView(item, edit=True, camera=cam_to_use, setCamera=True)
                        
                        # Force Maya to update
                        cmds.dgdirty(allPlugs=True)
                        cmds.refresh(force=True)
                        QtWidgets.QApplication.processEvents()
                        time.sleep(0.2)
                        cmds.refresh(force=True)
                    else:
                        # No connected camera, create temp and set manually
                        temp_cam = cmds.camera(name='pb_cam_{0}'.format(uid))[0]
                        temp_cam_shape = cmds.listRelatives(temp_cam, shapes=True, type='camera')[0]
                        restore_data = None
                        
                        # Read bookmark attributes directly
                        if cmds.attributeQuery('eye', node=item, exists=True):
                            eye = cmds.getAttr('{0}.eye'.format(item))[0]
                            cmds.setAttr('{0}.translateX'.format(temp_cam), eye[0])
                            cmds.setAttr('{0}.translateY'.format(temp_cam), eye[1])
                            cmds.setAttr('{0}.translateZ'.format(temp_cam), eye[2])
                        
                        if cmds.attributeQuery('centerOfInterest', node=item, exists=True):
                            coi = cmds.getAttr('{0}.centerOfInterest'.format(item))[0]
                            eye = cmds.getAttr('{0}.eye'.format(item))[0]
                            
                            dx = coi[0] - eye[0]
                            dy = coi[1] - eye[1]
                            dz = coi[2] - eye[2]
                            
                            dist_xz = math.sqrt(dx*dx + dz*dz)
                            if dist_xz > 0.0001:
                                rot_y = math.degrees(math.atan2(dx, dz)) + 180
                                rot_x = -math.degrees(math.atan2(dy, dist_xz))
                            else:
                                rot_y = 0
                                rot_x = -90 if dy > 0 else 90
                            
                            cmds.setAttr('{0}.rotateX'.format(temp_cam), rot_x)
                            cmds.setAttr('{0}.rotateY'.format(temp_cam), rot_y)
                            cmds.setAttr('{0}.rotateZ'.format(temp_cam), 0)
                        
                        if cmds.attributeQuery('focalLength', node=item, exists=True):
                            fl = cmds.getAttr('{0}.focalLength'.format(item))
                            if fl:
                                cmds.setAttr('{0}.focalLength'.format(temp_cam_shape), fl)
                        
                        cam_to_use = temp_cam
                
                # Create playblast window
                cmds.window(win_name, widthHeight=(width, height))
                cmds.paneLayout()
                panel = cmds.modelPanel(panel_name, camera=cam_to_use)
                editor = cmds.modelPanel(panel, query=True, modelEditor=True)
                
                cmds.modelEditor(editor, edit=True,
                    allObjects=False,
                    displayAppearance='smoothShaded',
                    displayTextures=True
                )
                cmds.modelEditor(editor, edit=True,
                    polymeshes=show_geo,
                    subdivSurfaces=show_geo,
                    nurbsSurfaces=show_geo,
                    nurbsCurves=show_curves,
                    locators=show_loc,
                    imagePlane=show_img,
                    grid=show_grid,
                    shadows=show_shadows,
                    displayLights='all' if show_lights else 'default'
                )
                
                cmds.showWindow(win_name)
                
                # Force the panel to look through the camera
                cmds.lookThru(panel, cam_to_use)
                
                cmds.setFocus(win_name)
                cmds.refresh(force=True)
                
                # Give Maya time to update the viewport
                QtWidgets.QApplication.processEvents()
                time.sleep(0.2)
                cmds.refresh(force=True)
                QtWidgets.QApplication.processEvents()
                
                full_path = os.path.join(path, filename).replace('\\', '/')
                
                playblast_success = False
                
                # Make absolutely sure the panel is using our camera
                cmds.modelPanel(panel, edit=True, camera=cam_to_use)
                cmds.lookThru(panel, cam_to_use)
                cmds.refresh(force=True)
                
                if is_macos():
                    try:
                        cmds.playblast(
                            filename=full_path,
                            format='avfoundation',
                            startTime=start_frame,
                            endTime=end_frame,
                            widthHeight=(width, height),
                            percent=100,
                            quality=100,
                            showOrnaments=False,
                            viewer=False,
                            offScreen=False,
                            forceOverwrite=True,
                            fp=4,
                            editorPanelName=panel
                        )
                        playblast_success = True
                    except Exception:
                        pass
                
                if not playblast_success:
                    try:
                        cmds.playblast(
                            filename=full_path,
                            format='qt',
                            compression='H.264',
                            startTime=start_frame,
                            endTime=end_frame,
                            widthHeight=(width, height),
                            percent=100,
                            quality=100,
                            showOrnaments=False,
                            viewer=False,
                            offScreen=False,
                            forceOverwrite=True,
                            fp=4,
                            editorPanelName=panel
                        )
                        playblast_success = True
                    except Exception:
                        pass
                
                if not playblast_success:
                    try:
                        cmds.playblast(
                            filename=full_path,
                            format='avi',
                            startTime=start_frame,
                            endTime=end_frame,
                            widthHeight=(width, height),
                            percent=100,
                            quality=100,
                            showOrnaments=False,
                            viewer=False,
                            offScreen=False,
                            forceOverwrite=True,
                            fp=4,
                            editorPanelName=panel
                        )
                        playblast_success = True
                    except Exception:
                        pass
                
                if not playblast_success:
                    cmds.playblast(
                        filename=full_path,
                        format='image',
                        startTime=start_frame,
                        endTime=end_frame,
                        widthHeight=(width, height),
                        percent=100,
                        quality=100,
                        showOrnaments=False,
                        viewer=False,
                        offScreen=False,
                        forceOverwrite=True,
                        fp=4,
                        editorPanelName=panel
                    )
                    playblast_success = True
                
                success += 1
                
            except Exception as e:
                errors.append('{0}: {1}'.format(item, str(e)))
            finally:
                try:
                    if cmds.window(win_name, exists=True):
                        cmds.deleteUI(win_name, window=True)
                    if temp_cam and cmds.objExists(temp_cam):
                        cmds.delete(temp_cam)
                    # Restore original camera state if we modified it
                    if not is_camera and restore_data and cmds.objExists(cam_to_use):
                        t = restore_data['translate']
                        r = restore_data['rotate']
                        cmds.setAttr('{0}.translate'.format(cam_to_use), t[0], t[1], t[2])
                        cmds.setAttr('{0}.rotate'.format(cam_to_use), r[0], r[1], r[2])
                        cam_shapes = cmds.listRelatives(cam_to_use, shapes=True, type='camera') or []
                        if cam_shapes:
                            cmds.setAttr('{0}.focalLength'.format(cam_shapes[0]), restore_data['focalLength'])
                            cmds.setAttr('{0}.centerOfInterest'.format(cam_shapes[0]), restore_data['centerOfInterest'])
                except Exception:
                    pass
        
        if errors:
            error_msg = 'Playblasted {0} of {1} item(s).\n\nErrors:\n'.format(success, len(items))
            error_msg += '\n'.join(errors[:5])
            if len(errors) > 5:
                error_msg += '\n... and {0} more errors'.format(len(errors) - 5)
            
            StyledMessageBox.show_message(
                self,
                'Playblast Errors',
                error_msg,
                ['OK']
            )
    
    def show_export_dialog(self):
        has_cameras = len(self.tracked_cameras) > 0
        has_bookmarks = self.bookmark_list.count() > 0
        has_cam_selection = len(self.get_selected_cameras()) > 0
        has_bm_selection = len(self.get_selected_bookmarks()) > 0
        
        if not has_cameras and not has_bookmarks:
            StyledMessageBox.show_message(
                self,
                'Export',
                'Nothing to export.',
                ['OK']
            )
            return
        
        dialog = ExportDialog(
            self,
            has_cameras=has_cameras,
            has_bookmarks=has_bookmarks,
            has_cam_selection=has_cam_selection,
            has_bm_selection=has_bm_selection
        )
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if dialog.export_type == "cameras":
                self.export_cameras(dialog.export_selected)
            elif dialog.export_type == "bookmarks":
                self.export_bookmarks(dialog.export_selected)
    
    def show_import_dialog(self):
        dialog = ImportDialog(self)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if dialog.import_type == "cameras":
                self.import_cameras()
            elif dialog.import_type == "bookmarks":
                self.import_bookmarks()
    
    def export_cameras(self, selected_only=False):
        if selected_only:
            cameras = self.get_selected_cameras()
        else:
            cameras = self.tracked_cameras[:]
        
        valid_cameras = [c for c in cameras if cmds.objExists(c)]
        if not valid_cameras:
            cmds.warning('No cameras to export.')
            return
        
        result = cmds.fileDialog2(
            fileFilter='Maya ASCII (*.ma)',
            dialogStyle=2,
            fileMode=0,
            caption='Export Cameras'
        )
        if not result:
            return
        
        file_path = result[0]
        if not file_path.lower().endswith('.ma'):
            file_path += '.ma'
        
        current_selection = cmds.ls(selection=True) or []
        
        try:
            cmds.select(valid_cameras, replace=True)
            
            prev_prompt = cmds.file(query=True, prompt=True)
            cmds.file(prompt=False)
            cmds.file(file_path, force=True, options="", typ="mayaAscii", exportSelected=True)
            
        except Exception as e:
            cmds.warning('Export failed: {0}'.format(str(e)))
        finally:
            try:
                cmds.file(prompt=prev_prompt)
            except Exception:
                pass
            
            if current_selection:
                try:
                    cmds.select(current_selection, replace=True)
                except Exception:
                    cmds.select(clear=True)
            else:
                cmds.select(clear=True)
        
        self.clear_focus()
    
    def import_cameras(self):
        result = cmds.fileDialog2(
            fileFilter='Maya ASCII (*.ma);;Maya Binary (*.mb)',
            dialogStyle=2,
            fileMode=1,
            caption='Import Cameras'
        )
        if not result:
            return
        
        file_path = result[0]
        
        cameras_before = set(cmds.ls(type='camera', long=True) or [])
        
        try:
            file_type = "mayaAscii" if file_path.lower().endswith('.ma') else "mayaBinary"
            cmds.file(
                file_path,
                i=True,
                type=file_type,
                ignoreVersion=True,
                ra=True,
                mergeNamespacesOnClash=False,
                namespace=":",
                options="",
                pr=True
            )
            
            cameras_after = set(cmds.ls(type='camera', long=True) or [])
            new_cam_shapes = cameras_after - cameras_before
            
            new_cameras = []
            for cam_shape in new_cam_shapes:
                try:
                    new_cameras.extend(resolve_camera_transform_names(cam_shape))
                except Exception:
                    continue
            
            for cam in new_cameras:
                if cam not in self.tracked_cameras:
                    self.tracked_cameras.append(cam)
            
            if new_cameras:
                save_tracked_cameras(self.tracked_cameras)
            
            self.refresh_camera_list()
            
            StyledMessageBox.show_message(
                self,
                'Imported',
                'Imported {0} camera(s).'.format(len(new_cameras)),
                ['OK']
            )
        except Exception as e:
            cmds.warning('Import failed: {0}'.format(str(e)))
        
        self.clear_focus()
    
    def export_bookmarks(self, selected_only=False):
        if selected_only:
            bookmark_names = self.get_selected_bookmarks()
            bookmarks = []
            for bm in get_camera_bookmarks():
                if bm.get('name') in bookmark_names:
                    bookmarks.append(bm)
        else:
            bookmarks = get_camera_bookmarks()
        
        if not bookmarks:
            cmds.warning('No bookmarks to export.')
            return
        
        result = cmds.fileDialog2(
            fileFilter='JSON (*.json)',
            dialogStyle=2,
            fileMode=0,
            caption='Export Bookmarks'
        )
        if not result:
            return
        
        file_path = result[0]
        if not file_path.lower().endswith('.json'):
            file_path += '.json'
        
        with open(file_path, 'w') as f:
            json.dump({'version': '1.0', 'bookmarks': bookmarks}, f, indent=2)
        
        self.clear_focus()
    
    def import_bookmarks(self):
        result = cmds.fileDialog2(
            fileFilter='JSON (*.json)',
            dialogStyle=2,
            fileMode=1,
            caption='Import Bookmarks'
        )
        if not result:
            return
        
        with open(result[0], 'r') as f:
            data = json.load(f)
        
        bookmarks = data.get('bookmarks', [])
        if not bookmarks:
            cmds.warning('No bookmarks in file.')
            return
        
        count = 0
        for bm in bookmarks:
            try:
                name = bm.get('name', 'importedBookmark')
                new_name = name
                i = 1
                while cmds.objExists(new_name):
                    new_name = '{0}_{1}'.format(name, i)
                    i += 1
                
                target_cam = bm.get('associatedCamera', 'perspShape')
                if not cmds.objExists(target_cam):
                    target_cam = 'perspShape'
                if cmds.nodeType(target_cam) != 'camera':
                    shapes = cmds.listRelatives(target_cam, shapes=True, type='camera')
                    target_cam = shapes[0] if shapes else 'perspShape'
                
                cv = cmds.createNode('cameraView', name=new_name)
                existing = cmds.listConnections('{0}.bookmarks'.format(target_cam), source=True, destination=False) or []
                cmds.connectAttr('{0}.message'.format(cv), '{0}.bookmarks[{1}]'.format(target_cam, len(existing)))
                
                for attr in ['eye', 'centerOfInterest', 'up', 'tumblePivot']:
                    if attr in bm:
                        cmds.setAttr('{0}.{1}'.format(cv, attr), *bm[attr])
                
                for attr in ['focalLength', 'horizontalAperture', 'verticalAperture', 'orthographicWidth', 'orthographic']:
                    if attr in bm and cmds.attributeQuery(attr, node=cv, exists=True):
                        cmds.setAttr('{0}.{1}'.format(cv, attr), bm[attr])
                
                if bm.get('playblastPath'):
                    set_playblast_path(cv, bm['playblastPath'])
                if bm.get('playblastFilename'):
                    set_playblast_filename(cv, bm['playblastFilename'])
                
                count += 1
            except Exception:
                pass
        
        StyledMessageBox.show_message(self, 'Imported', 'Imported {0} bookmark(s).'.format(count), ['OK'])
        self.refresh_bookmark_list()
        self.clear_focus()


camera_bookmark_ui_instance = None


def create_camera_bookmark_ui():
    global camera_bookmark_ui_instance
    
    if camera_bookmark_ui_instance is not None:
        try:
            camera_bookmark_ui_instance.kill_script_jobs()
            camera_bookmark_ui_instance.close()
            camera_bookmark_ui_instance.deleteLater()
        except Exception:
            pass
        camera_bookmark_ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "CameraBookmarkUIWindow":
                if hasattr(child, 'kill_script_jobs'):
                    child.kill_script_jobs()
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    reset_scale_factor()
    
    try:
        camera_bookmark_ui_instance = CameraBookmarkUI()
        camera_bookmark_ui_instance.show()
    except Exception as e:
        cmds.warning('Fast Playblaster failed to open: {0}'.format(e))
        camera_bookmark_ui_instance = None
    return camera_bookmark_ui_instance


def ui():
    return create_camera_bookmark_ui()


create_camera_bookmark_ui()