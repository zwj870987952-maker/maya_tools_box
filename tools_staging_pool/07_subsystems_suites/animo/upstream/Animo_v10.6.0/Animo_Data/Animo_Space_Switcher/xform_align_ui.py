from __future__ import print_function, division, absolute_import

import os
import sys
import platform
import maya.cmds as cmds

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui

spacify_dir = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts", "Animo_Data", "Animo_Space_Switcher")
if spacify_dir not in sys.path:
    sys.path.insert(0, spacify_dir)

from dpi_scale import (
    dpi, 
    reset_scale_factor, 
    get_screen_for_widget, 
    get_scale_factor_for_screen, 
    set_scale_factor,
    get_scale_factor
)

try:
    reload
except NameError:
    from importlib import reload


def _get_icons_dir():
    app_dir = cmds.internalVar(userAppDir=True)
    path = os.path.join(app_dir, "prefs", "icons")
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except Exception:
            pass
    return path


def _draw_icon_png(path, text, bg_color="#8B4789"):
    size = 64
    img = QtGui.QImage(size, size, QtGui.QImage.Format_ARGB32)
    img.fill(QtCore.Qt.transparent)

    painter = QtGui.QPainter(img)
    painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing, True)

    qcolor = QtGui.QColor(bg_color)
    painter.setBrush(qcolor)
    painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60), 2))
    rect = QtCore.QRectF(2, 2, size - 4, size - 4)
    painter.drawRoundedRect(rect, 10, 10)

    painter.setPen(QtCore.Qt.white)
    font = QtGui.QFont()
    font.setBold(True)
    font.setPointSize(16 if len(text) <= 2 else 12)
    painter.setFont(font)
    painter.drawText(QtCore.QRect(0, 0, size, size), QtCore.Qt.AlignCenter, text)
    painter.end()

    img.save(path, "PNG")


def _ensure_xform_icon(icon_text):
    icons_folder = _get_icons_dir()
    icon_name = "xform_{0}.png".format(icon_text.replace(" ", "_"))
    icon_path = os.path.join(icons_folder, icon_name)
    if not os.path.isfile(icon_path):
        _draw_icon_png(icon_path, icon_text)
    return icon_path


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class XformAlignUI(QtWidgets.QDialog):
    option_var_name = "XformAlignUI_lastPos"
    bake_keys_option_var = "XformAlignUI_bakeKeys"
    
    BASE_WIDTH = 282
    
    SHELF_COMMANDS = {
        "Copy XForm": ("xfCopy", "XC", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_copy; reload(xform_copy)"),
        "Copy XForm\nRange": ("xfCopyRng", "XCR", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_copy_range; reload(xform_copy_range)"),
        "Paste XForm": ("xfPaste", "XP", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_paste; reload(xform_paste)"),
        "Paste XForm Range": ("xfPasteRng", "XPR", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_paste_range; reload(xform_paste_range)"),
        "Copy XForm Relationship": ("xfRelCopy", "RC", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_relationship_copy; reload(xform_relationship_copy)"),
        "Paste Relationship": ("xfRelPaste", "RP", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_relationship_paste; reload(xform_relationship_paste)"),
        "Paste Range Relationship": ("xfRelPasteRng", "RPR", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport xform_relationship_bake; reload(xform_relationship_bake)"),
        "Align\n(Translate)": ("xfAlignT", "AT", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport align_objects_translate; reload(align_objects_translate); align_objects_translate.align_translate()"),
        "Align\n(Rotate)": ("xfAlignR", "AR", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport align_objects_rotate; reload(align_objects_rotate); align_objects_rotate.align_rotate()"),
        "Align": ("xfAlign", "A", "try:\n    reload\nexcept NameError:\n    from importlib import reload\nimport align_objects; reload(align_objects); align_objects.align()"),
    }

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(XformAlignUI, self).__init__(parent)
        self.setObjectName("XformAlignUIWindow")
        
        if platform.system() == 'Darwin':
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Window)
        
        self.setWindowOpacity(0.0)
        self.old_pos = None
        
        self._built_with_scale = get_scale_factor()
        self._current_screen = None
        self._screen_check_timer = QtCore.QTimer()
        self._screen_check_timer.setSingleShot(True)
        self._screen_check_timer.timeout.connect(self._check_screen_change)
        self._is_reopening = False
        
        self.build_ui()
        self.apply_theme()
        
        self.setFixedWidth(dpi(self.BASE_WIDTH))
        self.adjustSize()
        
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        if cmds.optionVar(exists=self.option_var_name):
            pos_str = cmds.optionVar(q=self.option_var_name)
            try:
                x, y = [int(v) for v in pos_str.split(",")]
                self.move(x, y)
            except Exception:
                pass
        
        self.fade_to(0.87)
        self.apply_rounded_corners()
        
        QtCore.QTimer.singleShot(100, self._store_initial_screen)

    def closeEvent(self, event):
        pos = self.pos()
        pos_str = "{0},{1}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        super(XformAlignUI, self).closeEvent(event)

    def build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(dpi(12), dpi(12), dpi(12), dpi(18))
        main_layout.setSpacing(0)

        title_bar = QtWidgets.QHBoxLayout()
        title_bar.setSpacing(dpi(9))
        
        title_bar.addStretch()
        
        title_label = QtWidgets.QLabel("XFORM - ALIGN")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 10pt;
                font-weight: 700;
                letter-spacing: 1px;
            }
        """)
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        close_btn = QtWidgets.QPushButton("✕")
        close_btn.setFixedSize(dpi(24), dpi(24))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #8B4789;
            }
        """)
        close_btn.clicked.connect(self.close)
        title_bar.addWidget(close_btn)
        
        main_layout.addLayout(title_bar)
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, dpi(18), 0, 0)
        content_layout.setSpacing(dpi(6))
        
        self._build_content(content_layout)
        
        main_layout.addWidget(content_widget)

    def _build_content(self, layout):
        
        bake_keys_row = QtWidgets.QWidget()
        bake_keys_layout = QtWidgets.QHBoxLayout(bake_keys_row)
        bake_keys_layout.setContentsMargins(0, 0, 0, 0)
        bake_keys_layout.setSpacing(dpi(6))
        
        self.bake_keys_checkbox = QtWidgets.QCheckBox("Bake Only Keys")
        self.bake_keys_checkbox.setStyleSheet("""
            QCheckBox {
                color: #AAAAAA;
                font-size: 8pt;
                font-weight: 600;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 3px;
                border: 1px solid #555555;
                background-color: #2A2A2A;
            }
            QCheckBox::indicator:checked {
                background-color: #8B4789;
                border: 1px solid #8B4789;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #8B4789;
            }
        """)
        
        if cmds.optionVar(exists=self.bake_keys_option_var):
            self.bake_keys_checkbox.setChecked(cmds.optionVar(q=self.bake_keys_option_var))
        else:
            self.bake_keys_checkbox.setChecked(True)
        
        self.bake_keys_checkbox.stateChanged.connect(self._on_bake_keys_changed)
        
        bake_keys_layout.addWidget(self.bake_keys_checkbox)
        bake_keys_layout.addStretch()
        
        layout.addWidget(bake_keys_row)
        layout.addSpacing(dpi(6))
        
        copy_row = QtWidgets.QWidget()
        copy_row_layout = QtWidgets.QHBoxLayout(copy_row)
        copy_row_layout.setContentsMargins(0, 0, 0, 0)
        copy_row_layout.setSpacing(dpi(6))
        
        self.copy_xform_btn = self._create_purple_button("Copy XForm", self.execute_copy_xform)
        copy_row_layout.addWidget(self.copy_xform_btn)
        
        self.copy_xform_range_btn = self._create_purple_button("Copy XForm\nRange", self.execute_copy_xform_range, small_font=True)
        copy_row_layout.addWidget(self.copy_xform_range_btn)
        
        layout.addWidget(copy_row)
        
        paste_xform_row = QtWidgets.QWidget()
        paste_xform_row_layout = QtWidgets.QHBoxLayout(paste_xform_row)
        paste_xform_row_layout.setContentsMargins(0, 0, 0, 0)
        paste_xform_row_layout.setSpacing(dpi(6))
        
        self.paste_xform_btn = self._create_purple_accent_button("Paste", self.execute_paste_xform, shelf_name="Paste XForm")
        paste_xform_row_layout.addWidget(self.paste_xform_btn)
        
        self.paste_xform_range_btn = self._create_purple_accent_button("Paste Range", self.execute_paste_xform_range, shelf_name="Paste XForm Range")
        paste_xform_row_layout.addWidget(self.paste_xform_range_btn)
        
        layout.addWidget(paste_xform_row)
        
        layout.addSpacing(dpi(12))
        separator1 = QtWidgets.QFrame()
        separator1.setFrameShape(QtWidgets.QFrame.HLine)
        separator1.setStyleSheet("background-color: #4D3A4D; max-height: 1px; margin: 0px;")
        layout.addWidget(separator1)
        layout.addSpacing(dpi(12))
        
        self.copy_xform_relationship_btn = self._create_purple_button("Copy XForm Relationship", self.execute_copy_xform_relationship)
        layout.addWidget(self.copy_xform_relationship_btn)
        
        layout.addSpacing(dpi(6))
        
        paste_rel_row = QtWidgets.QWidget()
        paste_rel_row_layout = QtWidgets.QHBoxLayout(paste_rel_row)
        paste_rel_row_layout.setContentsMargins(0, 0, 0, 0)
        paste_rel_row_layout.setSpacing(dpi(6))
        
        self.paste_relationship_btn = self._create_purple_accent_button("Paste", self.execute_paste_xform_relationship, shelf_name="Paste Relationship")
        paste_rel_row_layout.addWidget(self.paste_relationship_btn)
        
        self.paste_range_relationship_btn = self._create_purple_accent_button("Paste Range", self.execute_paste_range_xform_relationship, shelf_name="Paste Range Relationship")
        paste_rel_row_layout.addWidget(self.paste_range_relationship_btn)
        
        layout.addWidget(paste_rel_row)
        
        layout.addSpacing(dpi(12))
        separator2 = QtWidgets.QFrame()
        separator2.setFrameShape(QtWidgets.QFrame.HLine)
        separator2.setStyleSheet("background-color: #4D3A4D; max-height: 1px; margin: 0px;")
        layout.addWidget(separator2)
        layout.addSpacing(dpi(12))
        
        align_row = QtWidgets.QWidget()
        align_row_layout = QtWidgets.QHBoxLayout(align_row)
        align_row_layout.setContentsMargins(0, 0, 0, 0)
        align_row_layout.setSpacing(dpi(6))
        
        self.align_translate_btn = self._create_purple_dark_button("Align\n(Translate)", self.execute_align_translate)
        align_row_layout.addWidget(self.align_translate_btn)
        
        self.align_rotate_btn = self._create_purple_dark_button("Align\n(Rotate)", self.execute_align_rotate)
        align_row_layout.addWidget(self.align_rotate_btn)
        
        layout.addWidget(align_row)
        
        layout.addSpacing(dpi(6))
        
        self.align_btn = self._create_purple_light_button("Align", self.execute_align)
        layout.addWidget(self.align_btn)
        
        layout.addStretch()

    def _on_bake_keys_changed(self, state):
        cmds.optionVar(iv=(self.bake_keys_option_var, 1 if state else 0))

    def _create_purple_button(self, text, callback, small_font=False, shelf_name=None):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(dpi(35))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        font_size = "7pt" if small_font else "8pt"
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #3D2A3D;
                border: none;
                color: white;
                border-radius: 5px;
                font-size: {0};
                font-weight: 700;
                line-height: 1.1;
            }}
            QPushButton:hover {{ background-color: #4D3A4D; }}
            QPushButton:pressed {{ background-color: #2D1A2D; }}
        """.format(font_size))
        if callback:
            btn.clicked.connect(callback)
        self._setup_button_context_menu(btn, shelf_name or text)
        return btn

    def _create_purple_accent_button(self, text, callback, shelf_name=None):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(dpi(38))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #8B4789;
                border: none;
                color: white;
                padding: {0}px {1}px;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #9B5799; }}
            QPushButton:pressed {{ background-color: #7B3779; }}
        """.format(dpi(5), dpi(10)))
        if callback:
            btn.clicked.connect(callback)
        self._setup_button_context_menu(btn, shelf_name or text)
        return btn

    def _create_purple_dark_button(self, text, callback, shelf_name=None):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(dpi(38))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3D2A47;
                border: none;
                color: white;
                border-radius: 5px;
                font-size: 7pt;
                font-weight: 700;
                line-height: 1.1;
            }
            QPushButton:hover { background-color: #4D3A57; }
            QPushButton:pressed { background-color: #2D1A37; }
        """)
        if callback:
            btn.clicked.connect(callback)
        self._setup_button_context_menu(btn, shelf_name or text)
        return btn

    def _create_purple_light_button(self, text, callback, shelf_name=None):
        btn = QtWidgets.QPushButton(text)
        btn.setMinimumHeight(dpi(38))
        btn.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        btn.setStyleSheet("""
            QPushButton {{
                background-color: #8B72A5;
                border: none;
                color: white;
                padding: {0}px {1}px;
                border-radius: 5px;
                font-size: 8pt;
                font-weight: 700;
            }}
            QPushButton:hover {{ background-color: #9B82B5; }}
            QPushButton:pressed {{ background-color: #7B6295; }}
        """.format(dpi(5), dpi(10)))
        if callback:
            btn.clicked.connect(callback)
        self._setup_button_context_menu(btn, shelf_name or text)
        return btn

    def _clear_focus(self):
        self.setFocus()

    def _setup_button_context_menu(self, btn, button_name):
        btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        btn.customContextMenuRequested.connect(lambda pos, b=btn, n=button_name: self._show_button_context_menu(b, n, pos))

    def _show_button_context_menu(self, btn, button_name, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #8B4789;
            }
        """)
        
        add_to_shelf_action = menu.addAction("Add to Shelf")
        add_to_shelf_action.triggered.connect(lambda: self._add_to_shelf(button_name))
        
        menu.exec_(btn.mapToGlobal(pos))

    def _add_to_shelf(self, button_name):
        if button_name not in self.SHELF_COMMANDS:
            cmds.warning("No shelf command defined for: {0}".format(button_name))
            return
        
        shelf_name, icon_text, command = self.SHELF_COMMANDS[button_name]
        
        icon_path = _ensure_xform_icon(icon_text)
        
        current_shelf = cmds.tabLayout("ShelfLayout", query=True, selectTab=True)
        
        cmds.shelfButton(
            parent=current_shelf,
            label=shelf_name,
            command=command,
            sourceType="python",
            image=icon_path,
            annotation=button_name.replace("\n", " ")
        )
        
        cmds.inViewMessage(
            amg='<span style="color:#4ca6e6;">Added to shelf: {0}</span>'.format(shelf_name),
            pos='botCenter',
            fade=True
        )

    def execute_copy_xform(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_copy
            reload(xform_copy)
        except Exception as e:
            cmds.warning("Error copying xform: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_copy_xform_range(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_copy_range
            reload(xform_copy_range)
        except Exception as e:
            cmds.warning("Error copying xform range: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_paste_xform(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_paste
            reload(xform_paste)
        except Exception as e:
            cmds.warning("Error pasting xform: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_paste_xform_range(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_paste_range
            reload(xform_paste_range)
        except Exception as e:
            cmds.warning("Error pasting xform range: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_copy_xform_relationship(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_relationship_copy
            reload(xform_relationship_copy)
        except Exception as e:
            cmds.warning("Error copying xform relationship: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_paste_xform_relationship(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_relationship_paste
            reload(xform_relationship_paste)
        except Exception as e:
            cmds.warning("Error pasting xform relationship: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_paste_range_xform_relationship(self):
        cmds.undoInfo(openChunk=True)
        try:
            import xform_relationship_bake
            reload(xform_relationship_bake)
        except Exception as e:
            cmds.warning("Error pasting xform relationship range: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_align_translate(self):
        cmds.undoInfo(openChunk=True)
        try:
            import align_objects_translate
            reload(align_objects_translate)
            align_objects_translate.align_translate()
        except Exception as e:
            cmds.warning("Error aligning translate: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_align_rotate(self):
        cmds.undoInfo(openChunk=True)
        try:
            import align_objects_rotate
            reload(align_objects_rotate)
            align_objects_rotate.align_rotate()
        except Exception as e:
            cmds.warning("Error aligning rotate: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def execute_align(self):
        cmds.undoInfo(openChunk=True)
        try:
            import align_objects
            reload(align_objects)
            align_objects.align()
        except Exception as e:
            cmds.warning("Error aligning: {0}".format(str(e)))
        finally:
            cmds.undoInfo(closeChunk=True)
            self._clear_focus()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self._screen_check_timer.start(200)

    def _store_initial_screen(self):
        screen = get_screen_for_widget(self)
        if screen:
            self._current_screen = screen.name()

    def _check_screen_change(self):
        if self._is_reopening:
            return
        
        import time
        current_time = time.time()
        last_reopen = getattr(self, '_last_reopen_time', 0)
        if current_time - last_reopen < 2.0:
            return
        
        new_screen = get_screen_for_widget(self)
        if not new_screen:
            return
        
        new_screen_name = new_screen.name()
        new_scale = get_scale_factor_for_screen(new_screen)
        
        if self._current_screen is None:
            self._current_screen = new_screen_name
            return
        
        if new_screen_name == self._current_screen:
            return
        
        if abs(self._built_with_scale - new_scale) > 0.01:
            self._last_reopen_time = current_time
            self._reopen_for_new_screen(new_screen)
        else:
            self._current_screen = new_screen_name

    def _reopen_for_new_screen(self, new_screen):
        self._is_reopening = True
        
        pos = self.pos()
        pos_str = "{0},{1}".format(pos.x(), pos.y())
        cmds.optionVar(sv=(self.option_var_name, pos_str))
        
        new_scale = get_scale_factor_for_screen(new_screen)
        reset_scale_factor()
        set_scale_factor(new_scale)
        
        self.close()
        
        cmds.evalDeferred(reopen_xform_align_ui)

    def apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
            }
        """)

    def apply_rounded_corners(self):
        path = QtGui.QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect()), 12, 12)
        region = QtGui.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2A2A2A;
                color: white;
                border: 1px solid #3A3A3A;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #8B4789;
            }
        """)
        
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        
        menu.exec_(self.mapToGlobal(pos))

    def fade_to(self, target_opacity, duration=300, easing=None):
        self.anim = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(duration)
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(target_opacity)
        if easing is None:
            self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        else:
            self.anim.setEasingCurve(easing)
        self.anim.start()

    def enterEvent(self, event):
        self.fade_to(0.87, 50, QtCore.QEasingCurve.OutQuad)
        super(XformAlignUI, self).enterEvent(event)

    def leaveEvent(self, event):
        self.fade_to(0.55, 300)
        super(XformAlignUI, self).leaveEvent(event)


def reopen_xform_align_ui():
    show_ui()


_ui_instance = None


def show_ui():
    global _ui_instance
    
    if _ui_instance is not None:
        try:
            _ui_instance.close()
            _ui_instance.deleteLater()
        except Exception:
            pass
        _ui_instance = None
    
    maya_main = get_maya_main_window()
    for child in maya_main.children():
        try:
            if child.objectName() == "XformAlignUIWindow":
                child.close()
                child.deleteLater()
        except (AttributeError, RuntimeError):
            continue
    
    _ui_instance = XformAlignUI()
    _ui_instance.show()
    return _ui_instance


if __name__ == "__main__":
    show_ui()