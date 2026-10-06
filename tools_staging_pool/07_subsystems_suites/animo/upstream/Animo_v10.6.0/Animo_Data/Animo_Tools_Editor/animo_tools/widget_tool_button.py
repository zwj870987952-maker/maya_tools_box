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

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size
class ToolButton(QtWidgets.QWidget):
    clicked = QtCore.Signal()
    delete_requested = QtCore.Signal()
    rename_requested = QtCore.Signal()
    clear_tools_requested = QtCore.Signal()
    tool_dropped = QtCore.Signal(object, object)
    category_dropped = QtCore.Signal(object, object, object)
    
    def __init__(self, icon_name, label, icon_color, bg_color="#3A3A3A", 
                 icon_manager=None, can_delete=False, parent=None):
        super(ToolButton, self).__init__(parent)
        self.icon_name = icon_name
        self.label_text = label
        self.icon_color = icon_color
        self.bg_color = bg_color
        self.is_selected = False
        self.icon_manager = icon_manager
        self.can_delete = can_delete
        self._drag_hover = False
        self._drag_start_pos = None
        self._is_hovered = False
        self._is_pressed = False
        self.setFixedHeight(scale_size(45))
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAcceptDrops(self.can_delete)
        self.setMouseTracking(True)
        
        if self.icon_manager:
            self.icon_pixmap = self.icon_manager.create_pixmap(icon_name, scale_size(24))
        else:
            self.icon_pixmap = None
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        if self._drag_hover:
            bg_color = QtGui.QColor("#5A7A9A")
        elif self.is_selected:
            bg_color = QtGui.QColor("#4A5F7F")
        elif self._is_pressed:
            bg_color = QtGui.QColor(self.bg_color).darker(115)
        elif self._is_hovered:
            bg_color = QtGui.QColor(self.bg_color).lighter(130)
        else:
            bg_color = QtGui.QColor(self.bg_color)
        
        painter.fillRect(self.rect(), bg_color)
        
        icon_rect = QtCore.QRect(scale_size(8), scale_size(8), scale_size(30), scale_size(30))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(self.icon_color)))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(icon_rect, scale_size(3), scale_size(3))
        
        if self.icon_pixmap and not self.icon_pixmap.isNull():
            icon_x = icon_rect.x() + (icon_rect.width() - self.icon_pixmap.width()) // 2
            icon_y = icon_rect.y() + (icon_rect.height() - self.icon_pixmap.height()) // 2
            painter.drawPixmap(icon_x, icon_y, self.icon_pixmap)
        
        painter.setPen(QtGui.QColor("#CCCCCC"))
        font = painter.font()
        font.setPixelSize(scale_font_size(12))
        font.setWeight(QtGui.QFont.DemiBold)
        painter.setFont(font)
        text_offset = scale_size(45)
        text_rect = QtCore.QRect(text_offset, 0, self.width() - text_offset, self.height())
        painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, self.label_text)
    
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super(ToolButton, self).enterEvent(event)
    
    def leaveEvent(self, event):
        self._is_hovered = False
        self._is_pressed = False
        self.update()
        super(ToolButton, self).leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self._drag_start_pos = None
            if self.can_delete:
                self.show_context_menu(event.pos())
        elif event.button() == QtCore.Qt.LeftButton:
            self._drag_start_pos = event.pos()
            self._is_pressed = True
            self.update()
        else:
            self._drag_start_pos = None
        super(ToolButton, self).mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.can_delete and self._drag_start_pos is not None:
            distance = (event.pos() - self._drag_start_pos).manhattanLength()
            if distance >= QtWidgets.QApplication.startDragDistance():
                self._start_drag()
                return
        super(ToolButton, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self._drag_start_pos is not None:
            self.clicked.emit()
        self._drag_start_pos = None
        self._is_pressed = False
        self.update()
        super(ToolButton, self).mouseReleaseEvent(event)
    
    def _start_drag(self):
        self._drag_start_pos = None
        self._is_pressed = False
        self.update()
        
        payload = {
            'category_name': self.label_text
        }
        
        mime_data = QtCore.QMimeData()
        mime_data.setData('application/x-animo-category', QtCore.QByteArray(json.dumps(payload).encode('utf-8')))
        
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(QtCore.QPoint(pixmap.width() // 4, pixmap.height() // 2))
        
        drag.exec_(QtCore.Qt.MoveAction)
    
    def mouseDoubleClickEvent(self, event):
        self._drag_start_pos = None
        if self.can_delete:
            self.rename_requested.emit()
    
    def dragEnterEvent(self, event):
        mime_data = event.mimeData()
        if self.can_delete and (mime_data.hasFormat('application/x-animo-tool') or mime_data.hasFormat('application/x-animo-category')):
            self._drag_hover = True
            self.update()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        mime_data = event.mimeData()
        if self.can_delete and (mime_data.hasFormat('application/x-animo-tool') or mime_data.hasFormat('application/x-animo-category')):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        self._drag_hover = False
        self.update()
    
    def dropEvent(self, event):
        self._drag_hover = False
        self.update()
        
        mime_data = event.mimeData()
        
        if self.can_delete and mime_data.hasFormat('application/x-animo-category'):
            raw_bytes = bytes(mime_data.data('application/x-animo-category'))
            try:
                payload = json.loads(raw_bytes.decode('utf-8'))
            except Exception:
                event.ignore()
                return
            
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            
            insert_after = event.pos().y() > (self.height() // 2)
            self.category_dropped.emit(payload, self, insert_after)
            return
        
        if self.can_delete and mime_data.hasFormat('application/x-animo-tool'):
            raw_bytes = bytes(mime_data.data('application/x-animo-tool'))
            try:
                payload = json.loads(raw_bytes.decode('utf-8'))
            except Exception:
                event.ignore()
                return
            
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            self.tool_dropped.emit(payload, self)
            return
        
        event.ignore()
    
    def show_context_menu(self, pos):
        parent_dialog = self.window()
        if hasattr(parent_dialog, 'close_all_tooltips'):
            parent_dialog.close_all_tooltips()
        
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
        
        change_icon_action = menu.addAction("Change Icon")
        change_color_action = menu.addAction("Change Color")
        menu.addSeparator()
        rename_action = menu.addAction("Rename")
        menu.addSeparator()
        clear_tools_action = menu.addAction("Clear All Tools From This Category")
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == delete_action:
            self.delete_requested.emit()
        elif action == rename_action:
            self.rename_requested.emit()
        elif action == clear_tools_action:
            self.clear_tools_requested.emit()
        elif action == change_icon_action:
            self.change_icon()
        elif action == change_color_action:
            self.change_color()
    
    def setSelected(self, selected):
        self.is_selected = selected
        self.update()
    
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
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #2B2B2B; }")
        
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
            icons_layout.addWidget(btn, i // 6, i % 6)
        
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
                file_path, self.icon_manager.sanitize_icon_key(self.label_text) + "_icon"
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
                self.icon_pixmap = self.icon_manager.create_pixmap(new_icon, scale_size(24))
                self.update()
                
                parent_widget = self.parent()
                while parent_widget:
                    if hasattr(parent_widget, 'save_data'):
                        parent_widget.save_data()
                        break
                    parent_widget = parent_widget.parent()
    
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
                self.update()
                
                parent_widget = self.parent()
                while parent_widget:
                    if hasattr(parent_widget, 'save_data'):
                        parent_widget.save_data()
                        break
                    parent_widget = parent_widget.parent()
