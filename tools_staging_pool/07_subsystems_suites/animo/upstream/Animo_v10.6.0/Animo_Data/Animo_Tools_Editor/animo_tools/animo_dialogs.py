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

import animo_compat as compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
class ScriptEditorDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None, edit_mode=False, icon_manager=None, current_icon='recommended', current_color='#5A8AB5', shared_with_names=None):
        super(ScriptEditorDialog, self).__init__(parent)
        
        self.edit_mode = edit_mode
        self.icon_manager = icon_manager
        self.selected_icon = current_icon
        self.selected_color = current_color
        self.shared_with_names = shared_with_names or []
        title = "Edit Script" if edit_mode else "Create New Tool"
        self.setWindowTitle(title)
        extra_height = scale_size(50) if self.shared_with_names else 0
        self.setFixedSize(scale_size(600), scale_size(500) + extra_height)
        self.setStyleSheet("""
            QDialog {{
                background-color: #2B2B2B;
            }}
            QLabel {{
                color: #CCCCCC;
            }}
            QLineEdit, QTextEdit {{
                background-color: #3A3A3A;
                color: #DDDDDD;
                border: 1px solid #555555;
                border-radius: {border_radius}px;
                padding: {input_padding}px;
            }}
            QPushButton {{
                background-color: #4A4A4A;
                color: #CCCCCC;
                border: none;
                border-radius: {border_radius}px;
                padding: {btn_padding_v}px {btn_padding_h}px;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """.format(
            border_radius=scale_size(3),
            input_padding=scale_size(5),
            btn_padding_v=scale_size(8),
            btn_padding_h=scale_size(15)
        ))
        
        self.create_widgets()
        self.create_layouts()
    
    def create_widgets(self):
        if self.shared_with_names:
            if len(self.shared_with_names) == 1:
                banner_text = "This is a shared instance of \"{0}\". Editing the code here updates it everywhere.".format(self.shared_with_names[0])
            else:
                banner_text = "This is a shared instance of: {0}. Editing the code here updates it everywhere.".format(", ".join('"{0}"'.format(n) for n in self.shared_with_names))
            
            self.shared_banner_label = QtWidgets.QLabel(banner_text)
            self.shared_banner_label.setWordWrap(True)
            self.shared_banner_label.setStyleSheet("""
                QLabel {{
                    background-color: #4A3A1A;
                    color: #E0B060;
                    border: 1px solid #6A5528;
                    border-radius: {border_radius}px;
                    padding: {padding}px;
                }}
            """.format(
                border_radius=scale_size(3),
                padding=scale_size(8)
            ))
        
        self.name_label = QtWidgets.QLabel("Tool Name:")
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Enter tool name...")
        
        self.description_label = QtWidgets.QLabel("Description:")
        self.description_input = QtWidgets.QLineEdit()
        self.description_input.setPlaceholderText("Enter description...")
        
        if self.edit_mode and self.icon_manager:
            self.icon_color_label = QtWidgets.QLabel("Icon & Color:")
            
            self.change_icon_btn = QtWidgets.QPushButton("Change Icon")
            self.change_icon_btn.clicked.connect(self.change_icon)
            self.change_icon_btn.setFixedWidth(scale_size(120))
            
            self.change_color_btn = QtWidgets.QPushButton("Change Color")
            self.change_color_btn.clicked.connect(self.change_color)
            self.change_color_btn.setFixedWidth(scale_size(120))
        
        self.script_label = QtWidgets.QLabel("Script:")
        self.script_editor = QtWidgets.QTextEdit()
        self.script_editor.setPlaceholderText("Enter your Python or MEL script here...")
        
        self.script_type_label = QtWidgets.QLabel("Script Type:")
        self.script_type_combo = QtWidgets.QComboBox()
        self.script_type_combo.addItems(["Python", "MEL"])
        self.script_type_combo.setStyleSheet("""
            QComboBox {{
                background-color: #3A3A3A;
                color: #DDDDDD;
                border: 1px solid #555555;
                padding: {0}px;
            }}
        """.format(scale_size(5)))
        
        save_text = "Update Script" if self.edit_mode else "Save Tool"
        self.save_btn = QtWidgets.QPushButton(save_text)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #B8B8B8;
                color: #2B2B2B;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C8C8C8;
            }
        """)
        
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
    
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(scale_size(20), scale_size(20), scale_size(20), scale_size(20))
        main_layout.setSpacing(scale_size(15))
        
        if self.shared_with_names:
            main_layout.addWidget(self.shared_banner_label)
        
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.name_input)
        
        main_layout.addWidget(self.description_label)
        main_layout.addWidget(self.description_input)
        
        if self.edit_mode and self.icon_manager:
            main_layout.addWidget(self.icon_color_label)
            icon_color_layout = QtWidgets.QHBoxLayout()
            icon_color_layout.addWidget(self.change_icon_btn)
            icon_color_layout.addWidget(self.change_color_btn)
            icon_color_layout.addStretch()
            main_layout.addLayout(icon_color_layout)
        
        main_layout.addWidget(self.script_type_label)
        main_layout.addWidget(self.script_type_combo)
        
        main_layout.addWidget(self.script_label)
        main_layout.addWidget(self.script_editor)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(btn_layout)
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def get_tool_data(self):
        return {
            'name': self.name_input.text(),
            'description': self.description_input.text(),
            'script': self.script_editor.toPlainText(),
            'script_type': self.script_type_combo.currentText(),
            'icon': self.selected_icon,
            'color': self.selected_color
        }
    
    def change_icon(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Icon")
        dialog.setFixedSize(scale_size(520), scale_size(400))
        dialog.setStyleSheet("""
            QDialog { background-color: #2B2B2B; }
            QLabel { color: #CCCCCC; }
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
            
            if icon_name == self.selected_icon:
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
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            checked_btn = button_group.checkedButton()
            if checked_btn:
                self.selected_icon = checked_btn.property('icon_name')
    
    def change_color(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Choose Color")
        dialog.setFixedSize(scale_size(490), scale_size(300))
        dialog.setStyleSheet("""
            QDialog { background-color: #2B2B2B; }
            QLabel { color: #CCCCCC; }
            QPushButton {
                border: 2px solid #555555;
                border-radius: 5px;
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
        
        colors_widget = QtWidgets.QWidget()
        colors_layout = QtWidgets.QGridLayout(colors_widget)
        colors_layout.setSpacing(scale_size(10))
        
        button_group = QtWidgets.QButtonGroup(dialog)
        
        for i, (color_hex, color_name) in enumerate(self.icon_manager.available_colors):
            btn = QtWidgets.QPushButton()
            btn.setFixedSize(scale_size(60), scale_size(60))
            btn.setCheckable(True)
            btn.setProperty('color_hex', color_hex)
            btn.setStyleSheet("background-color: {0};".format(color_hex))
            
            if color_hex == self.selected_color:
                btn.setChecked(True)
            
            button_group.addButton(btn)
            colors_layout.addWidget(btn, i // 6, i % 6)
        
        layout.addWidget(colors_widget)
        
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
                self.selected_color = checked_btn.property('color_hex')
