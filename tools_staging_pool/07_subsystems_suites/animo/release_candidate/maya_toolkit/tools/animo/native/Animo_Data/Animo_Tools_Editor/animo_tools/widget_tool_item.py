from __future__ import absolute_import, division, print_function, unicode_literals

import json
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

import maya.cmds as cmds

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import widget_hotkey_input as widget_hotkey_input
HotkeyLineEdit = widget_hotkey_input.HotkeyLineEdit

import animo_hotkeys as animo_hotkeys

tooltip_widget = compat.load_own_module(__file__, 'tooltip_widget.py', 'animo_tools_editor_tooltip_widget')
AnimoTooltip = tooltip_widget.AnimoTooltip

import tooltip_data as tooltip_data
get_tooltip_data = tooltip_data.get_tooltip_data

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size

import animo_data as animo_data

class ToolItem(QtWidgets.QWidget):
    delete_requested = QtCore.Signal()
    
    def __init__(self, icon_name, icon_color, label, script_data=None, 
                 icon_manager=None, is_custom=False, parent=None):
        super(ToolItem, self).__init__(parent)
        self.icon_name = icon_name
        self.icon_color = icon_color
        self.label_text = label
        self.script_data = script_data or {}
        self.icon_manager = icon_manager
        self.is_custom = is_custom
        self.tool_entry = self.script_data.get('_tool_entry')
        self.setFixedHeight(scale_size(36))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setMouseTracking(True)
        self.setAcceptDrops(self.is_custom)
        
        self._drag_start_pos = None
        self._is_hovered = False
        self._is_pressed = False
        
        self._hover_timer = QtCore.QTimer(self)
        self._hover_timer.setSingleShot(True)
        self._hover_timer.timeout.connect(self._show_tooltip_at_cursor)
        self._hover_delay = 500
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(scale_size(10), scale_size(5), scale_size(10), scale_size(5))
        layout.setSpacing(scale_size(10))
        
        icon_box_size = scale_size(20)
        icon_size = scale_size(16)
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(icon_box_size, icon_box_size)
        self.icon_label.setStyleSheet("background-color: {0}; border-radius: {1}px;".format(icon_color, scale_size(2)))
        
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(icon_name, icon_size)
            if icon_pixmap and not icon_pixmap.isNull():
                self.icon_label.setPixmap(icon_pixmap)
                self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        layout.addWidget(self.icon_label)
        
        self.text_label = QtWidgets.QLabel(label)
        self.text_label.setStyleSheet("color: #DDDDDD; font-size: {0}px;".format(scale_font_size(11)))
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        if self.is_custom:
            self.edit_btn = QtWidgets.QPushButton("Edit")
            self.edit_btn.setFixedWidth(scale_size(80))
            self.edit_btn.setStyleSheet("""
                QPushButton {{
                    background-color: #3A3A3A;
                    color: #FFFFFF;
                    border: none;
                    border-radius: {border_radius}px;
                    padding: {pad_v}px {pad_h}px;
                    font-size: {font_size}px;
                }}
                QPushButton:hover {{
                    background-color: #444444;
                }}
                QPushButton:pressed {{
                    background-color: #2A2A2A;
                }}
            """.format(
                border_radius=scale_size(3),
                pad_v=scale_size(5),
                pad_h=scale_size(10),
                font_size=scale_font_size(11)
            ))
            self.edit_btn.clicked.connect(self.edit_script)
            layout.addWidget(self.edit_btn)
        
        self.tooltip_btn = QtWidgets.QPushButton("Tool Tips")
        self.tooltip_btn.setFixedWidth(scale_size(70))
        self.tooltip_btn.setStyleSheet("""
            QPushButton {{
                background-color: #3A3A3A;
                color: #AAAAAA;
                border: none;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #444444;
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(8),
            font_size=scale_font_size(10)
        ))
        self.tooltip_btn.clicked.connect(self.show_tooltip)
        layout.addWidget(self.tooltip_btn)
        
        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setFixedWidth(scale_size(120))
        self.hotkey_input.setStyleSheet(self._hotkey_input_style("default"))
        self.hotkey_input.hotkey_captured.connect(self.assign_hotkey)
        self.hotkey_input.hotkey_cleared.connect(self.clear_hotkey)
        layout.addWidget(self.hotkey_input)
        
        self.shelf_btn = QtWidgets.QPushButton("+ Add to Shelf")
        self.shelf_btn.setFixedWidth(scale_size(120))
        self.shelf_btn.setStyleSheet("""
            QPushButton {{
                background-color: #3A3A3A;
                color: #FFFFFF;
                border: none;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #444444;
            }}
            QPushButton:pressed {{
                background-color: #2A2A2A;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(10),
            font_size=scale_font_size(11)
        ))
        self.shelf_btn.clicked.connect(self.add_to_shelf)
        layout.addWidget(self.shelf_btn)
    
    def _update_background(self):
        if self._is_pressed:
            self.setStyleSheet("background-color: #2A2A2A; border-radius: {0}px;".format(scale_size(3)))
        elif self._is_hovered:
            self.setStyleSheet("background-color: #3A3A3A; border-radius: {0}px;".format(scale_size(3)))
        else:
            self.setStyleSheet("")
    
    def enterEvent(self, event):
        self._hover_timer.start(self._hover_delay)
        self._is_hovered = True
        self._update_background()
        super(ToolItem, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self._hover_timer.stop()
        self._is_hovered = False
        self._is_pressed = False
        self._update_background()
        
        if hasattr(self, '_active_tooltip') and self._active_tooltip is not None:
            try:
                if self._active_tooltip.isVisible():
                    self._active_tooltip._check_mouse_distance()
            except RuntimeError:
                self._active_tooltip = None
        
        super(ToolItem, self).leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._hover_timer.stop()
            self._close_all_tooltips_in_parent()
            child = self.childAt(event.pos())
            if child is None or child in (self.icon_label, self.text_label):
                self._drag_start_pos = event.pos()
                self._is_pressed = True
                self._update_background()
            else:
                self._drag_start_pos = None
        super(ToolItem, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.is_custom and self._drag_start_pos is not None:
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance >= QtWidgets.QApplication.startDragDistance():
                self._start_drag()
                return
        super(ToolItem, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self._drag_start_pos is not None:
            self.run_script()
        self._drag_start_pos = None
        self._is_pressed = False
        self._update_background()
        super(ToolItem, self).mouseReleaseEvent(event)
    
    def _start_drag(self):
        self._drag_start_pos = None
        self._is_pressed = False
        self._update_background()
        self._hover_timer.stop()
        self._close_all_tooltips_in_parent()
        
        payload = {
            'category': self.script_data.get('category', ''),
            'tool_name': self.label_text
        }
        
        mime_data = QtCore.QMimeData()
        mime_data.setData('application/x-animo-tool', QtCore.QByteArray(json.dumps(payload).encode('utf-8')))
        
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() // 4, pixmap.height() // 2))
        
        drag.exec_(QtCore.Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        if self.is_custom and event.mimeData().hasFormat('application/x-animo-tool'):
            self.setStyleSheet("background-color: #2F4A63;")
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        if self.is_custom and event.mimeData().hasFormat('application/x-animo-tool'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self._update_background()
    
    def dropEvent(self, event):
        self._update_background()
        
        if not self.is_custom or not event.mimeData().hasFormat('application/x-animo-tool'):
            event.ignore()
            return
        
        raw_bytes = bytes(event.mimeData().data('application/x-animo-tool'))
        try:
            payload = json.loads(raw_bytes.decode('utf-8'))
        except Exception:
            event.ignore()
            return
        
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        
        insert_after = event.pos().y() > (self.height() // 2)
        
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'move_tool_to_position') and self.tool_entry is not None:
            parent_dialog.move_tool_to_position(payload, self.tool_entry, insert_after)
    
    def _close_all_tooltips_in_parent(self):
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'close_all_tooltips'):
            parent_dialog.close_all_tooltips()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.run_script()
    
    def _ensure_saved_to_library(self):
        if not self.is_custom or self.tool_entry is None:
            return
        
        category_name = self.script_data.get('category', '')
        if not category_name:
            return
        
        existing_path = self.tool_entry.get('file_path')
        if existing_path:
            return
        
        new_file_path = animo_data.ensure_category_tool_file(category_name, self.tool_entry)
        
        if new_file_path != existing_path:
            self.tool_entry['file_path'] = new_file_path
            self.script_data['file_path'] = new_file_path
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def run_script(self):
        self._ensure_saved_to_library()
        
        try:
            import maya.cmds as cmds
            import maya.mel as mel
            import os
            import marshal
            import re
            
            script_file = self.script_data.get('script_file', '')
            script_name = os.path.splitext(script_file)[0] if script_file else "AnimoTool"
            
            cmds.undoInfo(openChunk=True, chunkName=script_name)
            
            try:
                if script_file:
                    tools_dir = os.path.join(_this_dir, 'tools')
                    script_path = os.path.join(tools_dir, script_file)
                    
                    exec_globals = {
                        '__builtins__': __builtins__,
                        '__name__': '__main__',
                        'cmds': cmds,
                        'mel': mel,
                    }
                    
                    if os.path.exists(script_path):
                        if tools_dir not in sys.path:
                            sys.path.insert(0, tools_dir)
                        
                        exec_globals['__file__'] = script_path
                        
                        with open(script_path, 'r') as f:
                            script_content = f.read()
                        
                        exec(script_content, exec_globals)
                    else:
                        pyc_path = self._find_pyc_for_maya_version(tools_dir, script_name)
                        
                        if pyc_path and os.path.exists(pyc_path):
                            if tools_dir not in sys.path:
                                sys.path.insert(0, tools_dir)
                            
                            exec_globals['__file__'] = pyc_path
                            
                            with open(pyc_path, 'rb') as f:
                                f.read(16)
                                code = marshal.load(f)
                            
                            exec(code, exec_globals)
                        else:
                            cmds.warning("Script file not found: {0}".format(script_path))
                else:
                    command = self.script_data.get('command', '')
                    if command:
                        exec_globals = {
                            '__builtins__': __builtins__,
                            'cmds': cmds,
                            'mel': mel,
                        }
                        
                        exec(command, exec_globals)
            finally:
                cmds.undoInfo(closeChunk=True)
                self._set_maya_focus()
                
        except Exception as e:
            try:
                cmds.undoInfo(closeChunk=True)
            except:
                pass
            cmds.warning("Error running script: {0}".format(str(e)))
    
    def _find_pyc_for_maya_version(self, tools_dir, script_name):
        import maya.cmds as cmds
        import os
        import re
        
        maya_version = int(cmds.about(version=True)[:4])
        
        versioned_pyc = "{0}_py{1}.pyc".format(script_name, maya_version)
        versioned_path = os.path.join(tools_dir, versioned_pyc)
        if os.path.exists(versioned_path):
            return versioned_path
        
        pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\d{4})\.pyc$', re.IGNORECASE)
        available_versions = []
        
        if os.path.exists(tools_dir):
            for filename in os.listdir(tools_dir):
                match = pattern.match(filename)
                if match:
                    file_version = int(match.group(1))
                    available_versions.append((file_version, filename))
        
        if available_versions:
            available_versions.sort(key=lambda x: x[0], reverse=True)
            
            for file_version, filename in available_versions:
                if file_version <= maya_version:
                    return os.path.join(tools_dir, filename)
            
            oldest_version, oldest_file = available_versions[-1]
            return os.path.join(tools_dir, oldest_file)
        
        generic_pyc = script_name + '.pyc'
        generic_path = os.path.join(tools_dir, generic_pyc)
        if os.path.exists(generic_path):
            return generic_path
        
        return None
    
    def _set_maya_focus(self):
        try:
            import animo_compat as compat
            maya_window = compat.get_maya_main_window()
            if maya_window:
                maya_window.activateWindow()
                maya_window.setFocus()
        except:
            pass
    
    def contextMenuEvent(self, event):
        if not self.is_custom:
            return
        
        self._close_all_tooltips_in_parent()
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {{
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: 1px solid #555555;
                padding: {menu_pad}px;
            }}
            QMenu::item {{
                padding: {item_pad_v}px {item_pad_h}px;
            }}
            QMenu::item:selected {{
                background-color: #4A4A4A;
            }}
        """.format(
            menu_pad=scale_size(5),
            item_pad_v=scale_size(5),
            item_pad_h=scale_size(20)
        ))
        
        run_action = menu.addAction("Run")
        menu.addSeparator()
        copy_code_action = menu.addAction("Copy Code")
        open_file_directory_action = menu.addAction("Open File Directory")
        rename_action = menu.addAction("Edit")
        duplicate_action = menu.addAction("Duplicate")
        duplicate_instance_action = menu.addAction("Duplicate Instance")
        menu.addSeparator()
        icon_action = menu.addAction("Change Icon")
        color_action = menu.addAction("Change Color")
        tooltip_action = menu.addAction("Edit Tooltip")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(event.globalPos())
        
        if action == run_action:
            self.run_script()
        elif action == icon_action:
            self.change_icon()
        elif action == color_action:
            self.change_color()
        elif action == tooltip_action:
            self.edit_tooltip()
        elif action == rename_action:
            self.rename_tool()
        elif action == duplicate_action:
            self.duplicate_tool()
        elif action == duplicate_instance_action:
            self.duplicate_tool_instance()
        elif action == copy_code_action:
            self.copy_code()
        elif action == open_file_directory_action:
            self.open_file_directory()
        elif action == delete_action:
            self.delete_tool()
    
    def open_file_directory(self):
        file_path = self.tool_entry.get('file_path') if self.tool_entry else None
        if not file_path or not os.path.exists(file_path):
            return
        
        folder_path = os.path.dirname(file_path)
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder_path))
    
    def copy_code(self):
        script_type = self.script_data.get('script_type', 'Python')
        raw_script = animo_data.extract_raw_script(self.script_data.get('command', ''), script_type)
        
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(raw_script)
    
    def change_icon(self):
        if not self.icon_manager:
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Icon")
        dialog.setFixedSize(scale_size(520), scale_size(400))
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #CCCCCC;
            }
            QPushButton {
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                border-color: #6A6A6A;
            }
            QPushButton:checked {
                background-color: #5A8AB5;
                border-color: #7AAAD5;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(scale_size(20), scale_size(20), scale_size(20), scale_size(20))
        
        label = QtWidgets.QLabel("Select an icon:")
        label.setStyleSheet("font-size: {0}px; margin-bottom: {1}px;".format(scale_size(12), scale_size(10)))
        layout.addWidget(label)
        
        browse_btn = QtWidgets.QPushButton("Browse for Icon...")
        browse_btn.setStyleSheet("padding: {0}px {1}px; text-align: center;".format(scale_size(6), scale_size(10)))
        layout.addWidget(browse_btn)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        icons_widget = QtWidgets.QWidget()
        icons_layout = QtWidgets.QGridLayout(icons_widget)
        icons_layout.setSpacing(scale_size(10))
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        available_icons = self.icon_manager.get_available_icons()
        
        for i, icon_name in enumerate(available_icons):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(scale_size(60), scale_size(60))
            btn.setCheckable(True)
            btn.setProperty('icon_name', icon_name)
            
            pixmap = self.icon_manager.create_pixmap(icon_name, scale_size(32))
            if not pixmap.isNull():
                btn.setIcon(QtGui.QIcon(pixmap))
                btn.setIconSize(QtCore.QSize(scale_size(32), scale_size(32)))
            
            if icon_name == self.icon_name:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            icons_layout.addWidget(btn, i // 5, i % 5)
        
        scroll.setWidget(icons_widget)
        layout.addWidget(scroll)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedSize(scale_size(70), scale_size(28))
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(scale_size(70), scale_size(28))
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        dialog._browsed_icon = None
        
        def _browse_for_icon():
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                dialog,
                "Choose Icon Image",
                "",
                "Image Files (*.svg *.png *.jpg *.jpeg *.bmp *.gif *.ico *.tif *.tiff *.webp *.xpm *.ppm *.pgm *.pbm);;All Files (*)"
            )
            
            if not file_path:
                return
            
            imported_icon = self.icon_manager.import_custom_icon(
                file_path, self.icon_manager.sanitize_icon_key(self.label_text) + "_script_icon"
            )
            if imported_icon:
                dialog._browsed_icon = imported_icon
                dialog.accept()
            else:
                error_box = QtWidgets.QMessageBox(dialog)
                error_box.setWindowTitle("Import Failed")
                error_box.setText("That file couldn't be used as an icon.")
                error_box.setIcon(QtWidgets.QMessageBox.Warning)
                error_box.exec_()
        
        browse_btn.clicked.connect(_browse_for_icon)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            new_icon = dialog._browsed_icon
            if new_icon is None:
                checked_btn = button_group.checkedButton()
                if checked_btn:
                    new_icon = checked_btn.property('icon_name')
            
            if new_icon:
                self.icon_name = new_icon
                
                if self.icon_manager:
                    icon_pixmap = self.icon_manager.create_pixmap(new_icon, scale_size(16))
                    if icon_pixmap and not icon_pixmap.isNull():
                        self.icon_label.setPixmap(icon_pixmap)
                
                self.update()
                
                if self.tool_entry is not None:
                    self.tool_entry['icon'] = new_icon
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
    
    def change_color(self):
        if not self.icon_manager:
            return
        
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Color")
        dialog.setFixedSize(scale_size(490), scale_size(300))
        dialog.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
            }
            QLabel {
                color: #CCCCCC;
            }
            QPushButton {
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                border-color: #6A6A6A;
            }
            QPushButton:checked {
                border: 3px solid #FFFFFF;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(scale_size(20), scale_size(20), scale_size(20), scale_size(20))
        
        label = QtWidgets.QLabel("Select a color:")
        label.setStyleSheet("font-size: {0}px; margin-bottom: {1}px;".format(scale_size(12), scale_size(10)))
        layout.addWidget(label)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        colors_widget = QtWidgets.QWidget()
        colors_layout = QtWidgets.QGridLayout(colors_widget)
        colors_layout.setSpacing(scale_size(10))
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        for i, (color_hex, color_name) in enumerate(self.icon_manager.available_colors):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(scale_size(80), scale_size(40))
            btn.setCheckable(True)
            btn.setProperty('color_hex', color_hex)
            btn.setStyleSheet("background-color: {0};".format(color_hex))
            
            if color_hex == self.icon_color:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            colors_layout.addWidget(btn, i // 4, i % 4)
        
        scroll.setWidget(colors_widget)
        layout.addWidget(scroll)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setFixedSize(scale_size(70), scale_size(28))
        ok_btn.setStyleSheet("background-color: #4A4A4A; color: #CCCCCC;")
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(scale_size(70), scale_size(28))
        cancel_btn.setStyleSheet("background-color: #4A4A4A; color: #CCCCCC;")
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            checked_btn = button_group.checkedButton()
            if checked_btn:
                new_color = checked_btn.property('color_hex')
                self.icon_color = new_color
                self.icon_label.setStyleSheet("background-color: {0}; border-radius: 2px;".format(new_color))
                self.update()
                
                if self.tool_entry is not None:
                    self.tool_entry['color'] = new_color
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
    
    def _sync_tool_entry_and_file(self, tool_data):
        if self.tool_entry is None:
            return
        
        self.tool_entry['name'] = self.label_text
        self.tool_entry['description'] = self.script_data.get('description', '')
        self.tool_entry['script_type'] = self.script_data.get('script_type', 'Python')
        self.tool_entry['script'] = self.script_data.get('command', '')
        
        parent_dialog = self.window()
        
        category_name = self.script_data.get('category', '')
        file_is_shared = False
        if hasattr(parent_dialog, 'is_file_shared_by_other_entry'):
            file_is_shared = parent_dialog.is_file_shared_by_other_entry(self.tool_entry.get('file_path'), self.tool_entry)
        
        if category_name:
            animo_data.move_category_tool_assets(self.tool_entry, category_name, allow_move=not file_is_shared)
            self.script_data['file_path'] = self.tool_entry.get('file_path')
        
        if file_is_shared and hasattr(parent_dialog, 'sync_shared_file_siblings'):
            parent_dialog.sync_shared_file_siblings(self.tool_entry)
    
    def _sync_custom_icon_rename(self, old_label, new_label):
        if not self.icon_manager or old_label == new_label:
            return
        
        old_icon_key = self.icon_manager.sanitize_icon_key(old_label) + "_script_icon"
        new_icon_key = self.icon_manager.sanitize_icon_key(new_label) + "_script_icon"
        
        if self.icon_name != old_icon_key or old_icon_key == new_icon_key:
            return
        
        renamed_icon = self.icon_manager.rename_custom_icon(old_icon_key, new_icon_key)
        self.icon_name = renamed_icon
        
        icon_pixmap = self.icon_manager.create_pixmap(renamed_icon, scale_size(16))
        if icon_pixmap and not icon_pixmap.isNull():
            self.icon_label.setPixmap(icon_pixmap)
    
    def rename_tool(self):
        from animo_dialogs import ScriptEditorDialog
        
        parent_dialog = self.window()
        shared_with_names = []
        if self.tool_entry is not None and hasattr(parent_dialog, 'get_shared_sibling_entries'):
            shared_with_names = [entry.get('name', 'Unnamed') for entry in parent_dialog.get_shared_sibling_entries(self.tool_entry)]
        
        dialog = ScriptEditorDialog(self, edit_mode=True, shared_with_names=shared_with_names)
        dialog.setWindowTitle("Edit Tool")
        
        dialog.name_input.setText(self.label_text)
        dialog.description_input.setText(self.script_data.get('description', ''))
        current_script_type = self.script_data.get('script_type', 'Python')
        dialog.script_editor.setPlainText(animo_data.extract_raw_script(self.script_data.get('command', ''), current_script_type))
        dialog.script_type_combo.setCurrentText(current_script_type)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            
            self.script_data['command'] = animo_data.wrap_script_for_command(tool_data['script_type'], tool_data['script'])
            self.script_data['description'] = tool_data['description']
            self.script_data['script_type'] = tool_data['script_type']
            
            if tool_data['name'] != self.label_text:
                old_label = self.label_text
                self.label_text = tool_data['name']
                self.text_label.setText(tool_data['name'])
                self._sync_custom_icon_rename(old_label, self.label_text)
            
            self._sync_tool_entry_and_file(tool_data)
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def delete_tool(self):
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Delete Tool")
        msg_box.setText("Are you sure you want to delete '{0}'?".format(self.label_text))
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        
        msg_box.setStyleSheet(self._confirm_box_style())
        
        for button in msg_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        reply = msg_box.exec_()
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        parent_dialog = self.window()
        
        if self.tool_entry is None or not hasattr(parent_dialog, 'custom_categories'):
            self.deleteLater()
            return
        
        file_is_shared = False
        if hasattr(parent_dialog, 'is_file_shared_by_other_entry'):
            file_is_shared = parent_dialog.is_file_shared_by_other_entry(self.tool_entry.get('file_path'), self.tool_entry)
        
        for category in parent_dialog.custom_categories:
            tools_data = category.get('tools_data', [])
            if self.tool_entry in tools_data:
                tools_data.remove(self.tool_entry)
                break
        
        if not file_is_shared:
            file_path = self.tool_entry.get('file_path')
            if file_path:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                
                sidecar_path = os.path.splitext(file_path)[0] + '.tooltip.json'
                if os.path.exists(sidecar_path):
                    try:
                        os.remove(sidecar_path)
                    except Exception:
                        pass
            
            gif_path = self.tool_entry.get('tooltip_gif_path')
            if gif_path and os.path.exists(gif_path):
                try:
                    os.remove(gif_path)
                except Exception:
                    pass
        
        self.deleteLater()
        
        if hasattr(parent_dialog, 'save_data'):
            parent_dialog.save_data()
    
    def duplicate_tool(self):
        if self.tool_entry is None:
            return
        
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'duplicate_tool_entry'):
            parent_dialog.duplicate_tool_entry(self.tool_entry)
    
    def duplicate_tool_instance(self):
        if self.tool_entry is None:
            return
        
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'duplicate_tool_entry_instance'):
            parent_dialog.duplicate_tool_entry_instance(self.tool_entry)
    
    def edit_tooltip(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Edit Tooltip")
        dialog.setFixedSize(scale_size(420), scale_size(430))
        dialog.setStyleSheet("""
            QDialog {{
                background-color: #2B2B2B;
            }}
            QLabel {{
                color: #CCCCCC;
                font-size: {font_size}px;
            }}
            QLineEdit, QTextEdit, QSpinBox {{
                background-color: #3A3A3A;
                color: #DDDDDD;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
                padding: {input_padding}px;
                font-size: {font_size}px;
            }}
            QPushButton {{
                background-color: #4A4A4A;
                color: #CCCCCC;
                border: none;
                border-radius: {border_radius}px;
                padding: {btn_padding_v}px {btn_padding_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
            QPushButton#okButton {{
                background-color: #B8B8B8;
                color: #2B2B2B;
                font-weight: bold;
            }}
            QPushButton#okButton:hover {{
                background-color: #C8C8C8;
            }}
        """.format(
            font_size=scale_font_size(11),
            border_radius=scale_size(3),
            input_padding=scale_size(5),
            btn_padding_v=scale_size(6),
            btn_padding_h=scale_size(15)
        ))
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(scale_size(15), scale_size(15), scale_size(15), scale_size(15))
        layout.setSpacing(scale_size(10))
        
        title_label = QtWidgets.QLabel("Tooltip Title:")
        layout.addWidget(title_label)
        
        title_input = QtWidgets.QLineEdit()
        current_title = self.tool_entry.get('tooltip_title', '') if self.tool_entry else ''
        title_input.setText(current_title or self.label_text)
        layout.addWidget(title_input)
        
        desc_label = QtWidgets.QLabel("Tooltip Description:")
        layout.addWidget(desc_label)
        
        desc_input = QtWidgets.QTextEdit()
        current_description = self.tool_entry.get('tooltip_description', '') if self.tool_entry else ''
        desc_input.setPlainText(current_description)
        layout.addWidget(desc_input)
        
        gif_section_label = QtWidgets.QLabel("Tooltip GIF (shown below the text):")
        layout.addWidget(gif_section_label)
        
        gif_row_layout = QtWidgets.QHBoxLayout()
        
        current_gif_path = self.tool_entry.get('tooltip_gif_path', '') if self.tool_entry else ''
        gif_status_label = QtWidgets.QLabel(os.path.basename(current_gif_path) if current_gif_path else "No GIF added")
        gif_status_label.setStyleSheet("color: #888888; font-size: {0}px;".format(scale_font_size(11)))
        gif_row_layout.addWidget(gif_status_label)
        
        gif_row_layout.addStretch()
        
        add_gif_btn = QtWidgets.QPushButton("Add GIF...")
        add_gif_btn.setFixedWidth(scale_size(90))
        gif_row_layout.addWidget(add_gif_btn)
        
        remove_gif_btn = QtWidgets.QPushButton("Remove")
        remove_gif_btn.setFixedWidth(scale_size(70))
        remove_gif_btn.setVisible(bool(current_gif_path))
        gif_row_layout.addWidget(remove_gif_btn)
        
        layout.addLayout(gif_row_layout)
        
        gif_size_row_layout = QtWidgets.QHBoxLayout()
        
        gif_size_label = QtWidgets.QLabel("GIF Width:")
        gif_size_row_layout.addWidget(gif_size_label)
        
        gif_size_input = QtWidgets.QSpinBox()
        gif_size_input.setRange(40, 800)
        gif_size_input.setSingleStep(10)
        gif_size_input.setSuffix(" px")
        current_gif_width = self.tool_entry.get('tooltip_gif_width') if self.tool_entry else None
        gif_size_input.setValue(current_gif_width if current_gif_width else 260)
        gif_size_row_layout.addWidget(gif_size_input)
        
        gif_size_row_layout.addStretch()
        layout.addLayout(gif_size_row_layout)
        
        gif_selection = {'source_path': None, 'changed': False}
        
        def choose_gif():
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                dialog,
                "Choose GIF",
                "",
                "GIF Files (*.gif)"
            )
            if file_path:
                gif_selection['source_path'] = file_path
                gif_selection['changed'] = True
                gif_status_label.setText(os.path.basename(file_path))
                remove_gif_btn.setVisible(True)
        
        def remove_gif():
            gif_selection['source_path'] = None
            gif_selection['changed'] = True
            gif_status_label.setText("No GIF added")
            remove_gif_btn.setVisible(False)
        
        add_gif_btn.clicked.connect(choose_gif)
        remove_gif_btn.clicked.connect(remove_gif)
        
        layout.addStretch()
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("Save")
        ok_btn.setObjectName("okButton")
        ok_btn.setFixedSize(scale_size(80), scale_size(28))
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(scale_size(80), scale_size(28))
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tooltip_title = title_input.text().strip()
            tooltip_description = desc_input.toPlainText()
            
            if self.tool_entry is not None:
                self.tool_entry['tooltip_title'] = tooltip_title
                self.tool_entry['tooltip_description'] = tooltip_description
                self.tool_entry['tooltip_gif_width'] = gif_size_input.value()
                
                if gif_selection['changed']:
                    old_gif_path = self.tool_entry.get('tooltip_gif_path', '')
                    
                    if gif_selection['source_path']:
                        tool_file_path = self.tool_entry.get('file_path', '')
                        new_gif_path = None
                        if tool_file_path:
                            new_gif_path = animo_data.save_tool_gif_next_to_script(
                                tool_file_path,
                                self.tool_entry.get('name', self.label_text),
                                gif_selection['source_path']
                            )
                        if not new_gif_path:
                            category_name = self.script_data.get('category', '')
                            if category_name:
                                new_gif_path = animo_data.save_category_tool_gif(
                                    category_name,
                                    self.tool_entry.get('name', self.label_text),
                                    gif_selection['source_path']
                                )
                        self.tool_entry['tooltip_gif_path'] = new_gif_path or ''
                    else:
                        if old_gif_path and os.path.exists(old_gif_path):
                            try:
                                os.remove(old_gif_path)
                            except Exception:
                                pass
                        self.tool_entry['tooltip_gif_path'] = ''
                
                self._save_tooltip_sidecar()
                
                parent_dialog = self.window()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
    
    def _save_tooltip_sidecar(self):
        if self.tool_entry is None:
            return
        animo_data.save_tooltip_sidecar(self.tool_entry)
    
    def add_to_shelf(self):
        try:
            import os
            
            current_shelf = cmds.tabLayout("ShelfLayout", query=True, selectTab=True)
            
            icon_path = ""
            if self.icon_manager:
                icon_path = self.icon_manager.get_icon_path(self.icon_name)
            
            script_file = self.script_data.get('script_file', '')
            
            if script_file:
                animo_tools_dir = _this_dir
                tools_dir = os.path.join(animo_tools_dir, 'tools')
                script_name = os.path.splitext(script_file)[0]
                
                shelf_command = '''import sys
import os
import re
import marshal
import maya.cmds as cmds

def get_maya_version():
    return int(cmds.about(version=True)[:4])

def find_script(tools_dir, script_name):
    maya_version = get_maya_version()
    py_path = os.path.join(tools_dir, script_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    versioned_pyc = os.path.join(tools_dir, script_name + "_py" + str(maya_version) + ".pyc")
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\\d{{4}})\\.pyc$', re.IGNORECASE)
    available = []
    if os.path.exists(tools_dir):
        for f in os.listdir(tools_dir):
            m = pattern.match(f)
            if m:
                available.append((int(m.group(1)), f))
    if available:
        available.sort(reverse=True)
        for v, f in available:
            if v <= maya_version:
                return os.path.join(tools_dir, f), "pyc"
        return os.path.join(tools_dir, available[-1][1]), "pyc"
    generic = os.path.join(tools_dir, script_name + ".pyc")
    if os.path.exists(generic):
        return generic, "pyc"
    return None, None

tools_dir = r"{0}"
script_name = "{1}"
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
path, ftype = find_script(tools_dir, script_name)
if path:
    if ftype == "py":
        with open(path, 'r') as f:
            exec(f.read())
    else:
        with open(path, 'rb') as f:
            f.read(16)
            exec(marshal.load(f))
else:
    cmds.warning("Script not found: " + script_name)
'''.format(tools_dir, script_name)
            else:
                shelf_command = self.script_data.get('command', 'print("Execute: {0}")'.format(self.label_text))
            
            cmds.shelfButton(
                parent=current_shelf,
                image=icon_path if icon_path else "pythonFamily.png",
                command=shelf_command,
                annotation=self.label_text,
                label=self.label_text,
                imageOverlayLabel=self.label_text[:3].upper(),
                sourceType="python"
            )
        except Exception as e:
            import traceback
            print("Error adding to shelf: {0}".format(str(e)))
            traceback.print_exc()
    
    def _confirm_box_style(self):
        return """
            QMessageBox {{
                background-color: #2B2B2B;
            }}
            QMessageBox QLabel {{
                color: #CCCCCC;
                font-size: {font_size}px;
            }}
            QPushButton {{
                background-color: #4A4A4A;
                color: #CCCCCC;
                border: 1px solid #5E5E5E;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #5A7A9A;
                border: 1px solid #7A9AB5;
                color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #4A6A85;
            }}
        """.format(
            font_size=scale_font_size(11),
            border_radius=scale_size(3),
            pad_v=scale_size(6),
            pad_h=scale_size(14)
        )
    
    def _hotkey_input_style(self, state="default"):
        colors = {
            "default": ("#3A3A3A", "#AAAAAA", "#555555"),
            "success": ("#3A5A3A", "#AAFFAA", "#5A8A5A"),
            "error": ("#5A3A3A", "#FFAAAA", "#8A5A5A"),
        }
        bg, fg, border = colors.get(state, colors["default"])
        
        return """
            QLineEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QLineEdit:focus {{
                border: 1px solid #6A6A6A;
                color: #DDDDDD;
            }}
        """.format(
            bg=bg, fg=fg, border=border,
            border_radius=scale_size(3),
            pad_v=scale_size(5),
            pad_h=scale_size(8),
            font_size=scale_font_size(10)
        )
    
    def assign_hotkey(self):
        hotkey_text = self.hotkey_input.text().strip()
        if not hotkey_text:
            return
        
        confirm_box = QtWidgets.QMessageBox(self)
        confirm_box.setWindowTitle("Apply Hotkey")
        confirm_box.setText("Assign \"{0}\" as the hotkey for \"{1}\"?".format(hotkey_text, self.label_text))
        confirm_box.setIcon(QtWidgets.QMessageBox.Question)
        confirm_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirm_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
        confirm_box.setStyleSheet(self._confirm_box_style())
        
        for button in confirm_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        if confirm_box.exec_() != QtWidgets.QMessageBox.Yes:
            return
        
        self._apply_hotkey_now()
    
    def clear_hotkey(self):
        old_hotkey = ''
        if self.tool_entry is not None:
            old_hotkey = self.tool_entry.get('hotkey', '')
        
        if old_hotkey:
            try:
                animo_hotkeys.remove_hotkey(old_hotkey)
            except Exception:
                pass
        
        if self.tool_entry is not None:
            self.tool_entry['hotkey'] = ''
        
        self.hotkey_input.setStyleSheet(self._hotkey_input_style("default"))
        
        parent_dialog = self.window()
        if self.tool_entry is not None and hasattr(parent_dialog, 'save_hotkeys_to_data'):
            parent_dialog.save_hotkeys_to_data()
        if hasattr(parent_dialog, 'save_data'):
            parent_dialog.save_data()
    
    def _apply_hotkey_now(self):
        hotkey_text = self.hotkey_input.text().strip()
        if not hotkey_text:
            return
        
        try:
            import os
            
            script_file = self.script_data.get('script_file', '')
            
            if script_file:
                animo_tools_dir = _this_dir
                tools_dir = os.path.join(animo_tools_dir, 'tools')
                script_name = os.path.splitext(script_file)[0]
                
                command = '''import sys
import os
import re
import marshal
import maya.cmds as cmds

def get_maya_version():
    return int(cmds.about(version=True)[:4])

def find_script(tools_dir, script_name):
    maya_version = get_maya_version()
    py_path = os.path.join(tools_dir, script_name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    versioned_pyc = os.path.join(tools_dir, script_name + "_py" + str(maya_version) + ".pyc")
    if os.path.exists(versioned_pyc):
        return versioned_pyc, "pyc"
    pattern = re.compile(r'^' + re.escape(script_name) + r'_py(\\d{{4}})\\.pyc$', re.IGNORECASE)
    available = []
    if os.path.exists(tools_dir):
        for f in os.listdir(tools_dir):
            m = pattern.match(f)
            if m:
                available.append((int(m.group(1)), f))
    if available:
        available.sort(reverse=True)
        for v, f in available:
            if v <= maya_version:
                return os.path.join(tools_dir, f), "pyc"
        return os.path.join(tools_dir, available[-1][1]), "pyc"
    generic = os.path.join(tools_dir, script_name + ".pyc")
    if os.path.exists(generic):
        return generic, "pyc"
    return None, None

tools_dir = r"{0}"
script_name = "{1}"
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)
path, ftype = find_script(tools_dir, script_name)
if path:
    if ftype == "py":
        with open(path, 'r') as f:
            exec(f.read())
    else:
        with open(path, 'rb') as f:
            f.read(16)
            exec(marshal.load(f))
else:
    cmds.warning("Script not found: " + script_name)
'''.format(tools_dir, script_name)
                language = "python"
            else:
                command = self.script_data.get('command', 'print("Execute: {0}")'.format(self.label_text))
                script_type = self.script_data.get('script_type', 'Python')
                language = "python" if script_type == "Python" else "mel"
            
            success, message = animo_hotkeys.assign_hotkey(command, hotkey_text, self.label_text, language)
            
            if success:
                self.hotkey_input.setStyleSheet(self._hotkey_input_style("success"))
                
                if self.tool_entry is not None:
                    self.tool_entry['hotkey'] = hotkey_text
                
                parent_dialog = self.window()
                if self.tool_entry is not None and hasattr(parent_dialog, 'clear_duplicate_hotkey'):
                    parent_dialog.clear_duplicate_hotkey(hotkey_text, self.tool_entry)
                if hasattr(parent_dialog, 'save_hotkeys_to_data'):
                    parent_dialog.save_hotkeys_to_data()
                if hasattr(parent_dialog, 'save_data'):
                    parent_dialog.save_data()
            else:
                self.hotkey_input.setStyleSheet(self._hotkey_input_style("error"))
            
        except Exception:
            self.hotkey_input.setStyleSheet(self._hotkey_input_style("error"))
    
    def edit_script(self):
        from animo_dialogs import ScriptEditorDialog
        
        parent_dialog = self.window()
        shared_with_names = []
        if self.tool_entry is not None and hasattr(parent_dialog, 'get_shared_sibling_entries'):
            shared_with_names = [entry.get('name', 'Unnamed') for entry in parent_dialog.get_shared_sibling_entries(self.tool_entry)]
        
        dialog = ScriptEditorDialog(
            self, 
            edit_mode=True, 
            icon_manager=self.icon_manager,
            current_icon=self.icon_name,
            current_color=self.icon_color,
            shared_with_names=shared_with_names
        )
        
        dialog.name_input.setText(self.label_text)
        dialog.description_input.setText(self.script_data.get('description', ''))
        
        command = self.script_data.get('command', '')
        script_type = self.script_data.get('script_type', 'Python')
        
        dialog.script_editor.setPlainText(animo_data.extract_raw_script(command, script_type))
        dialog.script_type_combo.setCurrentText(script_type)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            tool_data = dialog.get_tool_data()
            
            self.script_data['command'] = animo_data.wrap_script_for_command(tool_data['script_type'], tool_data['script'])
            self.script_data['description'] = tool_data['description']
            self.script_data['script_type'] = tool_data['script_type']
            
            if 'icon' in tool_data and tool_data['icon'] != self.icon_name:
                self.icon_name = tool_data['icon']
                if self.icon_manager:
                    icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, scale_size(16))
                    if icon_pixmap and not icon_pixmap.isNull():
                        self.icon_label.setPixmap(icon_pixmap)
            
            if 'color' in tool_data and tool_data['color'] != self.icon_color:
                self.icon_color = tool_data['color']
                self.icon_label.setStyleSheet("background-color: {0}; border-radius: 2px;".format(self.icon_color))
            
            if tool_data['name'] != self.label_text:
                old_label = self.label_text
                self.label_text = tool_data['name']
                self.text_label.setText(tool_data['name'])
                self._sync_custom_icon_rename(old_label, self.label_text)
            
            self._sync_tool_entry_and_file(tool_data)
            
            parent_dialog = self.window()
            if hasattr(parent_dialog, 'save_data'):
                parent_dialog.save_data()
    
    def _get_effective_tooltip_data(self):
        if self.is_custom and self.tool_entry is not None:
            title = self.tool_entry.get('tooltip_title') or self.label_text
            description = self.tool_entry.get('tooltip_description', '')
            return {
                'title': title,
                'description': description,
                'info_lines': [],
                'shortcut': ''
            }
        return get_tooltip_data(self.label_text)
    
    def _resolve_gif_path(self):
        if self.is_custom and self.tool_entry is not None:
            gif_path = self.tool_entry.get('tooltip_gif_path', '')
            if gif_path and os.path.exists(gif_path):
                return gif_path
            return ""
        
        script_file = self.script_data.get('script_file', '')
        if script_file:
            animo_tools_dir = _this_dir
            gifs_dir = os.path.join(animo_tools_dir, 'gifs')
            gif_name = os.path.splitext(script_file)[0] + '.gif'
            potential_gif_path = os.path.join(gifs_dir, gif_name)
            if os.path.exists(potential_gif_path):
                return potential_gif_path
        
        return ""
    
    def _resolve_gif_width(self):
        if self.is_custom and self.tool_entry is not None:
            width = self.tool_entry.get('tooltip_gif_width')
            if width:
                return width
        return None
    
    def show_tooltip(self):
        if hasattr(self, '_active_tooltip') and self._active_tooltip is not None:
            try:
                if self._active_tooltip.isVisible():
                    self._active_tooltip.hide_tooltip()
                    self._active_tooltip = None
                    return
                else:
                    self._active_tooltip = None
            except RuntimeError:
                self._active_tooltip = None
        
        tooltip_data = self._get_effective_tooltip_data()
        
        icon_pixmap = None
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, scale_size(28))
        
        hotkey_text = self.hotkey_input.text().strip()
        shortcut = tooltip_data.get("shortcut", "")
        if hotkey_text:
            shortcut = hotkey_text
        
        gif_path = self._resolve_gif_path()
        
        tooltip = AnimoTooltip()
        tooltip.set_trigger_button(self.tooltip_btn)
        tooltip.set_content(
            title=tooltip_data.get("title", self.label_text),
            description=tooltip_data.get("description", ""),
            info_lines=tooltip_data.get("info_lines", []),
            shortcut=shortcut,
            icon_pixmap=icon_pixmap,
            gif_path=gif_path,
            gif_width=self._resolve_gif_width()
        )
        tooltip.show_at_widget(self.tooltip_btn)
        self._active_tooltip = tooltip
    
    def _show_tooltip_at_cursor(self):
        self._close_all_tooltips_in_parent()
        
        tooltip_data = self._get_effective_tooltip_data()
        
        icon_pixmap = None
        if self.icon_manager:
            icon_pixmap = self.icon_manager.create_pixmap(self.icon_name, scale_size(28))
        
        hotkey_text = self.hotkey_input.text().strip()
        shortcut = tooltip_data.get("shortcut", "")
        if hotkey_text:
            shortcut = hotkey_text
        
        gif_path = self._resolve_gif_path()
        
        tooltip = AnimoTooltip()
        tooltip.set_trigger_button(self.tooltip_btn)
        tooltip.set_source_widget(self)
        tooltip.set_content(
            title=tooltip_data.get("title", self.label_text),
            description=tooltip_data.get("description", ""),
            info_lines=tooltip_data.get("info_lines", []),
            shortcut=shortcut,
            icon_pixmap=icon_pixmap,
            gif_path=gif_path,
            gif_width=self._resolve_gif_width()
        )
        tooltip.show_at_cursor()
        self._active_tooltip = tooltip