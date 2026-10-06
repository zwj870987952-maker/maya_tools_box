from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os
import shutil
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
get_maya_main_window = compat.get_maya_main_window

import animo_icons as animo_icons
IconManager = animo_icons.IconManager

import animo_widgets as animo_widgets
ToolButton = animo_widgets.ToolButton
ToolItem = animo_widgets.ToolItem

import animo_dialogs as animo_dialogs
ScriptEditorDialog = animo_dialogs.ScriptEditorDialog

import animo_data as animo_data

import animo_hotkeys as animo_hotkeys

import tool_defaults as tool_defaults
RECOMMENDED_TOOLS = tool_defaults.RECOMMENDED_TOOLS

import tool_icon_picker as tool_icon_picker
pick_icon_for_tool = tool_icon_picker.pick_icon_for_tool
pick_color_for_tool = tool_icon_picker.pick_color_for_tool
pick_color_for_index = tool_icon_picker.pick_color_for_index

import tooltip_data as tooltip_data

import styles as styles

import dpi_utils as dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size


class _StayOpenMenu(QtWidgets.QMenu):
    
    item_picked = QtCore.Signal(object)
    
    def mouseReleaseEvent(self, event):
        action = self.activeAction()
        if action is not None and action.isEnabled() and action.data() is not None:
            self.item_picked.emit(action.data())
            return
        super(_StayOpenMenu, self).mouseReleaseEvent(event)


class AnimoToolsDialog(QtWidgets.QDialog):
    
    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(AnimoToolsDialog, self).__init__(parent)
        
        self.setWindowTitle("Animo Tools Editor")
        self.setObjectName("AnimoToolsEditorUIWindow")
        self.setFixedSize(scale_size(1150), scale_size(800))
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        if compat.IS_MAC:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        
        self.icon_manager = IconManager()
        self.custom_tools = []
        self.custom_categories = []
        
        self.setStyleSheet(styles.MAIN_DIALOG_STYLE)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.load_data()
        self.select_default_category()
        
        self.scroll_area.viewport().installEventFilter(self)
        self.tools_widget.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() in (QtCore.Qt.LeftButton, QtCore.Qt.RightButton):
                self.close_all_tooltips()
        return super(AnimoToolsDialog, self).eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        if event.button() in (QtCore.Qt.LeftButton, QtCore.Qt.RightButton):
            self.close_all_tooltips()
        super(AnimoToolsDialog, self).mousePressEvent(event)
    
    def close_all_tooltips(self):
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                tool_item = item.widget()
                if hasattr(tool_item, '_active_tooltip') and tool_item._active_tooltip is not None:
                    try:
                        if tool_item._active_tooltip.isVisible():
                            tool_item._active_tooltip.hide_tooltip()
                    except RuntimeError:
                        pass
                    tool_item._active_tooltip = None
    
    def create_widgets(self):
        self.header_title = QtWidgets.QLabel("Animo Tools Editor")
        self.header_title.setStyleSheet("color: #CCCCCC; font-size: {0}px; font-weight: bold;".format(scale_font_size(18)))
        
        self.refresh_btn = QtWidgets.QPushButton("Refresh Contents")
        self.refresh_btn.setStyleSheet("""
            QPushButton {{
                background-color: #3A3A3A;
                color: #CCCCCC;
                border: none;
                border-radius: {border_radius}px;
                padding: {pad_v}px {pad_h}px;
                font-size: {font_size}px;
            }}
            QPushButton:hover {{
                background-color: #454545;
            }}
            QPushButton:pressed {{
                background-color: #2F2F2F;
            }}
        """.format(
            border_radius=scale_size(3),
            pad_v=scale_size(6),
            pad_h=scale_size(12),
            font_size=scale_font_size(11)
        ))
        
        self.tools_label = QtWidgets.QLabel("Categories")
        self.tools_label.setStyleSheet("color: #888888; font-size: {0}px; padding: {1}px;".format(scale_font_size(10), scale_size(5)))
        
        self.create_category_btn = QtWidgets.QPushButton("+ New Category")
        self.create_category_btn.setStyleSheet(styles.CREATE_CATEGORY_BTN_STYLE)
        
        self.category_search_bar = QtWidgets.QLineEdit()
        self.category_search_bar.setPlaceholderText("Search categories...")
        self.category_search_bar.setStyleSheet(styles.SEARCH_BAR_STYLE)
        
        self.categories_scroll_area = QtWidgets.QScrollArea()
        self.categories_scroll_area.setWidgetResizable(True)
        self.categories_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.categories_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.categories_scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #2A2A2A; }")
        
        self.categories_widget = QtWidgets.QWidget()
        self.categories_widget.setStyleSheet("background-color: #2A2A2A;")
        self.categories_layout = QtWidgets.QVBoxLayout(self.categories_widget)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)
        self.categories_layout.setSpacing(2)
        self.categories_layout.addStretch()
        
        self.categories_scroll_area.setWidget(self.categories_widget)
        
        self.tools_title = QtWidgets.QLabel("Animo Tools")
        self.tools_title.setStyleSheet("color: #888888; font-size: {0}px; padding: {1}px;".format(scale_font_size(11), scale_size(10)))
        
        self.add_instance_btn = QtWidgets.QPushButton("+ Add Tool")
        self.add_instance_btn.setToolTip("Add a tool from another category as a shared instance")
        self.add_instance_btn.setFixedHeight(scale_size(26))
        self.add_instance_btn.setMinimumWidth(scale_size(100))
        self.add_instance_btn.setStyleSheet(styles.ADD_INSTANCE_BTN_STYLE)
        self.add_instance_btn.setCursor(QtCore.Qt.PointingHandCursor)
        
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search tools...")
        self.search_bar.setStyleSheet(styles.SEARCH_BAR_STYLE)
        
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.tools_widget = QtWidgets.QWidget()
        self.tools_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tools_layout = QtWidgets.QVBoxLayout(self.tools_widget)
        self.tools_layout.setContentsMargins(0, 0, 0, 0)
        self.tools_layout.setSpacing(2)
        
        self.scroll_area.setWidget(self.tools_widget)
        
        self.import_btn = QtWidgets.QPushButton("Import Scripts")
        self.reset_default_btn = QtWidgets.QPushButton("Reset to Default Settings")
        self.reset_default_btn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.import_hotkeys_btn = QtWidgets.QPushButton("Import Hotkeys")
        self.export_hotkeys_btn = QtWidgets.QPushButton("Export Hotkeys")
        self.clear_hotkeys_btn = QtWidgets.QPushButton("Clear All Hotkeys")
        self.apply_btn = QtWidgets.QPushButton("Apply Hotkeys")
        self.apply_btn.setStyleSheet(styles.APPLY_BTN_STYLE)
        self.close_bottom_btn = QtWidgets.QPushButton("Close")
        self.close_bottom_btn.setStyleSheet(styles.CLOSE_BTN_STYLE)
    
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet("background-color: #2A2A2A;")
        header_widget.setFixedHeight(scale_size(50))
        header_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.header_widget = header_widget
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(scale_size(15), scale_size(10), scale_size(15), scale_size(10))
        
        header_layout.addWidget(self.header_title)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        
        main_layout.addWidget(header_widget)
        
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        left_panel = QtWidgets.QWidget()
        left_panel.setStyleSheet("background-color: #2A2A2A;")
        left_panel.setFixedWidth(scale_size(250))
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, scale_size(10), 0, 0)
        left_layout.setSpacing(0)
        
        left_layout.addWidget(self.tools_label)
        left_layout.addWidget(self.create_category_btn)
        left_layout.addWidget(self.category_search_bar)
        left_layout.addWidget(self.categories_scroll_area)
        
        content_layout.addWidget(left_panel)
        
        right_panel = QtWidgets.QWidget()
        right_panel.setStyleSheet("background-color: #2B2B2B;")
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        title_row = QtWidgets.QHBoxLayout()
        title_row.setContentsMargins(scale_size(10), scale_size(2), scale_size(22), scale_size(4))
        title_row.addWidget(self.tools_title)
        title_row.addStretch()
        title_row.addWidget(self.add_instance_btn, 0, QtCore.Qt.AlignTop)
        right_layout.addLayout(title_row)
        right_layout.addWidget(self.search_bar)
        right_layout.addWidget(self.scroll_area)
        
        content_layout.addWidget(right_panel)
        
        main_layout.addLayout(content_layout)
        
        bottom_widget = QtWidgets.QWidget()
        bottom_widget.setStyleSheet("background-color: #353535;")
        bottom_widget.setFixedHeight(scale_size(60))
        bottom_layout = QtWidgets.QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(scale_size(15), scale_size(10), scale_size(15), scale_size(10))
        bottom_layout.setSpacing(scale_size(10))
        
        bottom_layout.addWidget(self.import_btn)
        bottom_layout.addWidget(self.reset_default_btn)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.import_hotkeys_btn)
        bottom_layout.addWidget(self.export_hotkeys_btn)
        bottom_layout.addWidget(self.clear_hotkeys_btn)
        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.close_bottom_btn)
        
        main_layout.addWidget(bottom_widget)
    
    def create_connections(self):
        self.close_bottom_btn.clicked.connect(self.close)
        self.import_btn.clicked.connect(self.import_scripts)
        self.reset_default_btn.clicked.connect(self.reset_to_default_settings)
        self.reset_default_btn.customContextMenuRequested.connect(self.show_reset_default_context_menu)
        self.tools_widget.customContextMenuRequested.connect(self.show_add_instance_browser_menu)
        self.add_instance_btn.clicked.connect(self.show_add_instance_browser_menu_from_button)
        self.header_widget.customContextMenuRequested.connect(self.show_add_instance_browser_menu_from_header)
        self.create_category_btn.clicked.connect(self.create_new_category)
        self.refresh_btn.clicked.connect(self.refresh_contents)
        self.search_bar.textChanged.connect(self.filter_tools)
        self.category_search_bar.textChanged.connect(self.filter_categories)
        self.apply_btn.clicked.connect(self.apply_all_hotkeys)
        self.import_hotkeys_btn.clicked.connect(self.import_hotkeys)
        self.export_hotkeys_btn.clicked.connect(self.export_hotkeys)
        self.clear_hotkeys_btn.clicked.connect(self.clear_all_hotkeys)
    
    def select_default_category(self):
        if self.custom_categories:
            first_category = self.custom_categories[0]
            self.on_tool_selected(first_category['button'])
        else:
            self.tools_title.setText("")
            while self.tools_layout.count():
                item = self.tools_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.tools_layout.addStretch()
    
    def on_tool_selected(self, selected_btn):
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            for category in self.custom_categories:
                category['button'].setSelected(category['button'] == selected_btn)
            
            for category in self.custom_categories:
                if category['button'] == selected_btn:
                    self.tools_title.setText(category['name'])
                    self.load_category_tools(category)
                    break
        finally:
            if app:
                app.restoreOverrideCursor()
    
    def load_category_tools(self, category):
        while self.tools_layout.count():
            item = self.tools_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for tool_data in category.get('tools_data', []):
            item = ToolItem(
                tool_data.get('icon', 'smart_key'),
                tool_data.get('color', '#7A8A9A'),
                tool_data['name'],
                {
                    'command': tool_data.get('script', ''),
                    'description': tool_data.get('description', ''),
                    'script_type': tool_data.get('script_type', 'Python'),
                    'category': category['name'],
                    'file_path': tool_data.get('file_path'),
                    '_tool_entry': tool_data
                },
                icon_manager=self.icon_manager,
                is_custom=True
            )
            
            saved_hotkey = tool_data.get('hotkey', '')
            if saved_hotkey:
                item.hotkey_input.setText(saved_hotkey)
            
            self.tools_layout.addWidget(item)
        
        self.tools_layout.addStretch()
        self.load_hotkeys_from_data()
    
    def import_scripts(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Import Scripts", 
            "", 
            "Script Files (*.py *.mel);;Python Files (*.py);;MEL Files (*.mel);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    script_content = f.read()
                
                script_type = "Python" if file_path.endswith('.py') else "MEL"
                script_name = os.path.basename(file_path).replace('.py', '').replace('.mel', '')
                
                tool_data = {
                    'name': script_name,
                    'description': 'Imported {0} script'.format(script_type),
                    'script': script_content,
                    'script_type': script_type
                }
                
                self.add_custom_tool(tool_data)
            except Exception:
                pass
    
    def add_custom_tool(self, tool_data):
        icon_name = pick_icon_for_tool(tool_data['name'])
        color = pick_color_for_tool(tool_data['name'])
        
        script_command = animo_data.wrap_script_for_command(tool_data['script_type'], tool_data['script'])
        
        tool_entry = {
            'name': tool_data['name'],
            'icon': icon_name,
            'color': color,
            'script': script_command,
            'description': tool_data.get('description', ''),
            'script_type': tool_data['script_type']
        }
        
        added_to_category = False
        for category in self.custom_categories:
            if category['button'].is_selected:
                if 'tools_data' not in category:
                    category['tools_data'] = []
                
                color = pick_color_for_index(len(category['tools_data']))
                icon_name = tool_entry['icon']
                tool_entry['color'] = color
                
                saved_path = animo_data.save_category_tool_file(
                    category['name'],
                    tool_data['name'],
                    tool_data['script'],
                    tool_data['script_type']
                )
                tool_entry['file_path'] = saved_path
                
                category['tools_data'].append(tool_entry)
                
                item = ToolItem(
                    icon_name, 
                    color, 
                    tool_data['name'], 
                    {
                        'command': script_command,
                        'description': tool_data.get('description', ''),
                        'script_type': tool_data['script_type'],
                        'category': category['name'],
                        'file_path': saved_path,
                        '_tool_entry': tool_entry
                    },
                    icon_manager=self.icon_manager,
                    is_custom=True
                )
                self.tools_layout.insertWidget(self.tools_layout.count() - 1, item)
                added_to_category = True
                break
        
        if not added_to_category:
            self.custom_tools.append(tool_data)
            item = ToolItem(
                icon_name, 
                color, 
                tool_data['name'], 
                {'command': script_command, 'description': tool_data.get('description', ''), 'script_type': tool_data['script_type']},
                icon_manager=self.icon_manager,
                is_custom=True
            )
            self.tools_layout.insertWidget(self.tools_layout.count() - 1, item)
        
        self.save_data()
    
    def is_file_shared_by_other_entry(self, file_path, exclude_entry):
        if not file_path:
            return False
        
        normalized_target = os.path.normcase(os.path.normpath(file_path))
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                if entry is exclude_entry:
                    continue
                
                other_path = entry.get('file_path')
                if not other_path:
                    continue
                
                if os.path.normcase(os.path.normpath(other_path)) == normalized_target:
                    return True
        
        return False
    
    def get_shared_sibling_entries(self, tool_entry):
        file_path = tool_entry.get('file_path') if tool_entry else None
        if not file_path:
            return []
        
        normalized_target = os.path.normcase(os.path.normpath(file_path))
        siblings = []
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                if entry is tool_entry:
                    continue
                
                other_path = entry.get('file_path')
                if not other_path:
                    continue
                
                if os.path.normcase(os.path.normpath(other_path)) == normalized_target:
                    siblings.append(entry)
        
        return siblings
    
    def sync_shared_file_siblings(self, tool_entry):
        siblings = self.get_shared_sibling_entries(tool_entry)
        if not siblings:
            return
        
        new_script = tool_entry.get('script', '')
        new_script_type = tool_entry.get('script_type', 'Python')
        
        sibling_set = set(id(entry) for entry in siblings)
        
        for sibling_entry in siblings:
            sibling_entry['script'] = new_script
            sibling_entry['script_type'] = new_script_type
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if not item or not item.widget():
                continue
            widget = item.widget()
            if not isinstance(widget, ToolItem):
                continue
            if widget.tool_entry is None:
                continue
            if id(widget.tool_entry) in sibling_set:
                widget.script_data['command'] = new_script
                widget.script_data['script_type'] = new_script_type
    
    def move_tool_to_category(self, payload, destination_btn):
        dest_category = None
        for category in self.custom_categories:
            if category['button'] == destination_btn:
                dest_category = category
                break
        
        if dest_category is None:
            return
        
        source_category_name = payload.get('category', '')
        tool_name = payload.get('tool_name', '')
        
        if dest_category['name'] == source_category_name:
            return
        
        source_category = None
        for category in self.custom_categories:
            if category['name'] == source_category_name:
                source_category = category
                break
        
        if source_category is None:
            return
        
        tool_entry = None
        for entry in source_category.get('tools_data', []):
            if entry.get('name') == tool_name:
                tool_entry = entry
                break
        
        if tool_entry is None:
            return
        
        source_category['tools_data'].remove(tool_entry)
        
        file_is_shared = self.is_file_shared_by_other_entry(tool_entry.get('file_path'), tool_entry)
        animo_data.move_category_tool_assets(tool_entry, dest_category['name'], allow_move=not file_is_shared)
        
        if 'tools_data' not in dest_category:
            dest_category['tools_data'] = []
        dest_category['tools_data'].append(tool_entry)
        
        if source_category['button'].is_selected:
            self.load_category_tools(source_category)
        
        if dest_category['button'].is_selected:
            self.load_category_tools(dest_category)
        
        self.save_data()
    
    def move_tool_to_position(self, payload, target_entry, insert_after=False):
        source_category_name = payload.get('category', '')
        tool_name = payload.get('tool_name', '')
        
        source_category = None
        source_entry = None
        for category in self.custom_categories:
            if category['name'] != source_category_name:
                continue
            for entry in category.get('tools_data', []):
                if entry.get('name') == tool_name:
                    source_category = category
                    source_entry = entry
                    break
            if source_entry is not None:
                break
        
        if source_entry is None or source_entry is target_entry:
            return
        
        target_category = None
        for category in self.custom_categories:
            if target_entry in category.get('tools_data', []):
                target_category = category
                break
        
        if target_category is None:
            return
        
        source_category['tools_data'].remove(source_entry)
        
        if source_category is not target_category:
            file_is_shared = self.is_file_shared_by_other_entry(source_entry.get('file_path'), source_entry)
            animo_data.move_category_tool_assets(source_entry, target_category['name'], allow_move=not file_is_shared)
        
        target_list = target_category['tools_data']
        insert_index = target_list.index(target_entry)
        if insert_after:
            insert_index += 1
        target_list.insert(insert_index, source_entry)
        
        self.save_data()
        
        refreshed_names = set()
        for category in (source_category, target_category):
            if category['name'] not in refreshed_names and category['button'].is_selected:
                self.load_category_tools(category)
                refreshed_names.add(category['name'])
    
    def duplicate_tool_entry(self, tool_entry):
        category = None
        for cat in self.custom_categories:
            if tool_entry in cat.get('tools_data', []):
                category = cat
                break
        
        if category is None:
            return
        
        existing_names = set(entry.get('name', '') for entry in category['tools_data'])
        base_name = tool_entry.get('name', 'Tool') + " Copy"
        new_name = base_name
        counter = 2
        while new_name in existing_names:
            new_name = "{0} {1}".format(base_name, counter)
            counter += 1
        
        script_type = tool_entry.get('script_type', 'Python')
        new_entry = {
            'name': new_name,
            'icon': tool_entry.get('icon', 'gear'),
            'color': tool_entry.get('color', '#7A8A9A'),
            'script': tool_entry.get('script', ''),
            'description': tool_entry.get('description', ''),
            'script_type': script_type,
            'tooltip_title': tool_entry.get('tooltip_title', ''),
            'tooltip_description': tool_entry.get('tooltip_description', ''),
            'tooltip_gif_width': tool_entry.get('tooltip_gif_width')
        }
        
        raw_script = animo_data.extract_raw_script(new_entry['script'], script_type)
        new_entry['file_path'] = animo_data.save_category_tool_file(
            category['name'],
            new_name,
            raw_script,
            script_type
        )
        
        old_gif_path = tool_entry.get('tooltip_gif_path')
        if old_gif_path and os.path.exists(old_gif_path):
            new_entry['tooltip_gif_path'] = animo_data.save_category_tool_gif(
                category['name'],
                new_name,
                old_gif_path
            ) or ''
        else:
            new_entry['tooltip_gif_path'] = ''
        
        animo_data.save_tooltip_sidecar(new_entry)
        
        tools_data = category['tools_data']
        insert_index = tools_data.index(tool_entry) + 1
        tools_data.insert(insert_index, new_entry)
        
        self.save_data()
        
        if category['button'].is_selected:
            self.load_category_tools(category)
    
    def duplicate_tool_entry_instance(self, tool_entry):
        category = None
        for cat in self.custom_categories:
            if tool_entry in cat.get('tools_data', []):
                category = cat
                break
        
        if category is None:
            return
        
        existing_names = set(entry.get('name', '') for entry in category['tools_data'])
        base_name = tool_entry.get('name', 'Tool') + " Copy"
        new_name = base_name
        counter = 2
        while new_name in existing_names:
            new_name = "{0} {1}".format(base_name, counter)
            counter += 1
        
        new_entry = {
            'name': new_name,
            'icon': tool_entry.get('icon', 'gear'),
            'color': tool_entry.get('color', '#7A8A9A'),
            'script': tool_entry.get('script', ''),
            'description': tool_entry.get('description', ''),
            'script_type': tool_entry.get('script_type', 'Python'),
            'tooltip_title': tool_entry.get('tooltip_title', ''),
            'tooltip_description': tool_entry.get('tooltip_description', ''),
            'tooltip_gif_width': tool_entry.get('tooltip_gif_width'),
            'file_path': tool_entry.get('file_path'),
            'tooltip_gif_path': tool_entry.get('tooltip_gif_path', '')
        }
        
        tools_data = category['tools_data']
        insert_index = tools_data.index(tool_entry) + 1
        tools_data.insert(insert_index, new_entry)
        
        self.save_data()
        
        if category['button'].is_selected:
            self.load_category_tools(category)
    
    def _build_add_instance_browser_menu(self):
        current_category = None
        for category in self.custom_categories:
            if category['button'].is_selected:
                current_category = category
                break
        
        if current_category is None:
            return None
        
        menu_style = """
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
        )
        
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(menu_style)
        
        import_action = menu.addAction("Import Scripts")
        import_action.triggered.connect(self.import_scripts)
        menu.addSeparator()
        
        export_library_action = menu.addAction("Export Tool Library...")
        export_library_action.triggered.connect(self.export_tool_library)
        import_library_action = menu.addAction("Import Tool Library...")
        import_library_action.triggered.connect(self.import_tool_library)
        menu.addSeparator()
        
        for category in self.custom_categories:
            tools_data = category.get('tools_data', [])
            if not tools_data:
                continue
            
            submenu = _StayOpenMenu(category['name'], menu)
            submenu.setStyleSheet(menu_style)
            submenu.item_picked.connect(lambda entry: self._add_tool_instance_from_browser(entry, current_category))
            
            for tool_entry in tools_data:
                action = submenu.addAction(tool_entry.get('name', 'Unnamed'))
                action.setData(tool_entry)
            
            menu.addMenu(submenu)
        
        return menu
    
    def show_add_instance_browser_menu(self, pos):
        menu = self._build_add_instance_browser_menu()
        if menu is None:
            return
        
        menu.exec_(self.tools_widget.mapToGlobal(pos))
    
    def show_add_instance_browser_menu_from_header(self, pos):
        menu = self._build_add_instance_browser_menu()
        if menu is None:
            return
        
        menu.exec_(self.header_widget.mapToGlobal(pos))
    
    def show_add_instance_browser_menu_from_button(self):
        menu = self._build_add_instance_browser_menu()
        if menu is None:
            return
        
        button_pos = self.add_instance_btn.mapToGlobal(QtCore.QPoint(0, self.add_instance_btn.height()))
        menu.exec_(button_pos)
    
    def _add_tool_instance_from_browser(self, tool_entry, target_category):
        if 'tools_data' not in target_category:
            target_category['tools_data'] = []
        
        existing_names = set(entry.get('name', '') for entry in target_category['tools_data'])
        base_name = tool_entry.get('name', 'Tool')
        new_name = base_name
        counter = 2
        while new_name in existing_names:
            new_name = "{0} {1}".format(base_name, counter)
            counter += 1
        
        new_entry = {
            'name': new_name,
            'icon': tool_entry.get('icon', 'gear'),
            'color': tool_entry.get('color', '#7A8A9A'),
            'script': tool_entry.get('script', ''),
            'description': tool_entry.get('description', ''),
            'script_type': tool_entry.get('script_type', 'Python'),
            'tooltip_title': tool_entry.get('tooltip_title', ''),
            'tooltip_description': tool_entry.get('tooltip_description', ''),
            'tooltip_gif_width': tool_entry.get('tooltip_gif_width'),
            'file_path': tool_entry.get('file_path'),
            'tooltip_gif_path': tool_entry.get('tooltip_gif_path', '')
        }
        
        target_category['tools_data'].append(new_entry)
        
        self.save_data()
        
        if target_category['button'].is_selected:
            self.load_category_tools(target_category)
        
        try:
            cmds.inViewMessage(
                amg='<hl>{0}</hl> added to <hl>{1}</hl>'.format(new_name, target_category['name']),
                pos='midCenter',
                fade=True
            )
        except Exception:
            pass
    
    def show_reset_default_context_menu(self, pos):
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
        
        save_default_action = menu.addAction("Save as Default")
        
        action = menu.exec_(self.reset_default_btn.mapToGlobal(pos))
        
        if action == save_default_action:
            self.save_as_default_settings()
    
    def _build_settings_snapshot(self):
        custom_categories = []
        
        for category in self.custom_categories:
            custom_categories.append({
                'name': category['name'],
                'icon': category['button'].icon_name,
                'color': category['button'].icon_color,
                'tools_data': category.get('tools_data', [])
            })
        
        return {
            'custom_tools': self.custom_tools,
            'custom_categories': custom_categories
        }
    
    def save_as_default_settings(self):
        snapshot = self._build_settings_snapshot()
        success = animo_data.save_default_settings(snapshot)
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Save as Default")
        
        if success:
            msg_box.setText("Current categories, tools, order, and appearance have been saved as the default settings.")
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
        else:
            msg_box.setText("Failed to save default settings.")
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in msg_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        msg_box.exec_()
    
    def reset_to_default_settings(self):
        default_data = animo_data.load_default_settings()
        
        if default_data is None:
            info_box = QtWidgets.QMessageBox(self)
            info_box.setWindowTitle("Reset to Default")
            info_box.setText("No default settings have been saved yet.\nRight-click this button and choose \"Save as Default\" first.")
            info_box.setIcon(QtWidgets.QMessageBox.Information)
            info_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            info_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in info_box.buttons():
                button.setMinimumSize(scale_size(70), scale_size(28))
            
            info_box.exec_()
            return
        
        confirm_box = QtWidgets.QMessageBox(self)
        confirm_box.setWindowTitle("Reset to Default")
        confirm_box.setText("Are you sure you want to reset to the default settings?\nThis will replace your current categories, tools, order, and appearance.")
        confirm_box.setIcon(QtWidgets.QMessageBox.Question)
        confirm_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirm_box.setDefaultButton(QtWidgets.QMessageBox.No)
        confirm_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in confirm_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        if confirm_box.exec_() != QtWidgets.QMessageBox.Yes:
            return
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            self._apply_settings_snapshot(default_data)
        finally:
            if app:
                app.restoreOverrideCursor()
    
    def _apply_settings_snapshot(self, data):
        for category in list(self.custom_categories):
            category['button'].setParent(None)
            category['button'].deleteLater()
        self.custom_categories = []
        
        self.custom_tools = data.get('custom_tools', [])
        
        for category_data in data.get('custom_categories', []):
            category_name = category_data.get('name', 'Unnamed')
            
            self._add_category_widget(
                category_name,
                icon=category_data.get('icon', 'recommended'),
                color=category_data.get('color', '#4A4A4A'),
                tools_data=category_data.get('tools_data', [])
            )
            
            animo_data.get_category_folder_path(category_name, create=True)
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                file_path = animo_data.ensure_category_tool_file(category['name'], entry)
                entry['file_path'] = file_path
        
        self.save_data()
        self.select_default_category()
    
    def _add_category_widget(self, category_name, icon="recommended", color="#4A4A4A", tools_data=None):
        new_category_btn = ToolButton(
            icon,
            category_name,
            color,
            "#3A3A3A",
            icon_manager=self.icon_manager,
            can_delete=True
        )
        
        new_category_btn.clicked.connect(lambda btn=new_category_btn: self.on_tool_selected(btn))
        new_category_btn.delete_requested.connect(lambda btn=new_category_btn: self.delete_category(btn))
        new_category_btn.rename_requested.connect(lambda btn=new_category_btn: self.rename_category(btn))
        new_category_btn.clear_tools_requested.connect(lambda btn=new_category_btn: self.clear_all_tools_from_category(btn))
        new_category_btn.tool_dropped.connect(self.move_tool_to_category)
        new_category_btn.category_dropped.connect(self.move_category_to_position)
        
        category = {
            'name': category_name,
            'button': new_category_btn,
            'tools_data': tools_data if tools_data is not None else []
        }
        
        self.custom_categories.append(category)
        self._refresh_category_widget_order()
        
        return category
    
    def _refresh_category_widget_order(self):
        while self.categories_layout.count():
            self.categories_layout.takeAt(0)
        
        for category in self.custom_categories:
            self.categories_layout.addWidget(category['button'])
        
        self.categories_layout.addStretch()
    
    def _apply_category_row_shading(self):
        shades = ["#2A2A2A", "#272727"]
        
        for index, category in enumerate(self.custom_categories):
            new_bg = shades[index % len(shades)]
            category['button'].bg_color = new_bg
            category['button'].update()
    
    def move_category_to_position(self, payload, target_btn, insert_after=False):
        source_name = payload.get('category_name', '')
        
        source_category = None
        for category in self.custom_categories:
            if category['name'] == source_name:
                source_category = category
                break
        
        if source_category is None:
            return
        
        target_category = None
        for category in self.custom_categories:
            if category['button'] == target_btn:
                target_category = category
                break
        
        if target_category is None or target_category is source_category:
            return
        
        self.custom_categories.remove(source_category)
        insert_index = self.custom_categories.index(target_category)
        if insert_after:
            insert_index += 1
        self.custom_categories.insert(insert_index, source_category)
        
        self._refresh_category_widget_order()
        self._apply_category_row_shading()
        self.save_data()
    
    def create_new_category(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("New Category")
        dialog.setFixedSize(scale_size(280), scale_size(130))
        dialog.setStyleSheet(styles.CATEGORY_DIALOG_STYLE)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(scale_size(15), scale_size(15), scale_size(15), scale_size(15))
        layout.setSpacing(scale_size(12))
        
        label = QtWidgets.QLabel("Enter category name:")
        layout.addWidget(label)
        
        line_edit = QtWidgets.QLineEdit()
        line_edit.setPlaceholderText("Category name...")
        line_edit.returnPressed.connect(dialog.accept)
        layout.addWidget(line_edit)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setObjectName("okButton")
        ok_btn.setFixedSize(scale_size(70), scale_size(28))
        ok_btn.clicked.connect(dialog.accept)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedSize(scale_size(70), scale_size(28))
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        line_edit.setFocus()
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            category_name = line_edit.text()
            
            if category_name:
                self._add_category_widget(category_name)
                animo_data.get_category_folder_path(category_name, create=True)
                self._apply_category_row_shading()
                self.save_data()
    
    def filter_tools(self, text):
        text = text.lower()
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    should_show = text in widget.label_text.lower()
                    widget.setVisible(should_show)
    
    def filter_categories(self, text):
        text = text.lower()
        
        for category in self.custom_categories:
            should_show = text in category['name'].lower()
            category['button'].setVisible(should_show)
    
    def delete_category(self, category_btn):
        for i, category in enumerate(self.custom_categories):
            if category['button'] == category_btn:
                msg_box = QtWidgets.QMessageBox(self)
                msg_box.setWindowTitle("Delete Category")
                msg_box.setText("Are you sure you want to delete '{0}'? This will also delete its folder on disk.".format(category['name']))
                msg_box.setIcon(QtWidgets.QMessageBox.Question)
                msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
                msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
                
                for button in msg_box.buttons():
                    button.setMinimumSize(scale_size(70), scale_size(28))
                
                reply = msg_box.exec_()
                
                if reply == QtWidgets.QMessageBox.Yes:
                    category_btn.deleteLater()
                    self.custom_categories.pop(i)
                    
                    animo_data.delete_category_folder(category['name'])
                    
                    if category_btn.is_selected:
                        self.select_default_category()
                    
                    self._apply_category_row_shading()
                    self.save_data()
                break
    
    def clear_all_tools_from_category(self, category_btn):
        target_category = None
        for category in self.custom_categories:
            if category['button'] == category_btn:
                target_category = category
                break
        
        if target_category is None:
            return
        
        tools_data = target_category.get('tools_data', [])
        if not tools_data:
            return
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Clear All Tools")
        msg_box.setText("Are you sure you want to remove all tools from '{0}'? This cannot be undone.".format(target_category['name']))
        msg_box.setIcon(QtWidgets.QMessageBox.Question)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        msg_box.setDefaultButton(QtWidgets.QMessageBox.No)
        msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in msg_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        reply = msg_box.exec_()
        
        if reply != QtWidgets.QMessageBox.Yes:
            return
        
        for entry in list(tools_data):
            file_is_shared = self.is_file_shared_by_other_entry(entry.get('file_path'), entry)
            
            if not file_is_shared:
                file_path = entry.get('file_path')
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
                
                gif_path = entry.get('tooltip_gif_path')
                if gif_path and os.path.exists(gif_path):
                    try:
                        os.remove(gif_path)
                    except Exception:
                        pass
        
        target_category['tools_data'] = []
        
        if category_btn.is_selected:
            self.load_category_tools(target_category)
        
        self.save_data()
    
    def rename_category(self, category_btn):
        for category in self.custom_categories:
            if category['button'] == category_btn:
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Rename Category")
                dialog.setFixedSize(scale_size(280), scale_size(130))
                dialog.setStyleSheet(styles.CATEGORY_DIALOG_STYLE)
                
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setContentsMargins(scale_size(15), scale_size(15), scale_size(15), scale_size(15))
                layout.setSpacing(scale_size(12))
                
                label = QtWidgets.QLabel("Enter new category name:")
                layout.addWidget(label)
                
                line_edit = QtWidgets.QLineEdit()
                line_edit.setText(category['name'])
                line_edit.selectAll()
                line_edit.returnPressed.connect(dialog.accept)
                layout.addWidget(line_edit)
                
                btn_layout = QtWidgets.QHBoxLayout()
                btn_layout.addStretch()
                
                ok_btn = QtWidgets.QPushButton("OK")
                ok_btn.setObjectName("okButton")
                ok_btn.setFixedSize(scale_size(70), scale_size(28))
                ok_btn.clicked.connect(dialog.accept)
                
                cancel_btn = QtWidgets.QPushButton("Cancel")
                cancel_btn.setFixedSize(scale_size(70), scale_size(28))
                cancel_btn.clicked.connect(dialog.reject)
                
                btn_layout.addWidget(ok_btn)
                btn_layout.addWidget(cancel_btn)
                layout.addLayout(btn_layout)
                
                line_edit.setFocus()
                
                if dialog.exec_() == QtWidgets.QDialog.Accepted:
                    new_name = line_edit.text()
                    if new_name:
                        old_name = category['name']
                        animo_data.rename_category_folder(old_name, new_name)
                        
                        category['name'] = new_name
                        category_btn.label_text = new_name
                        
                        old_icon_key = self.icon_manager.sanitize_icon_key(old_name) + "_icon"
                        new_icon_key = self.icon_manager.sanitize_icon_key(new_name) + "_icon"
                        if category_btn.icon_name == old_icon_key and old_icon_key != new_icon_key:
                            renamed_icon = self.icon_manager.rename_custom_icon(old_icon_key, new_icon_key)
                            category_btn.icon_name = renamed_icon
                            category_btn.icon_pixmap = self.icon_manager.create_pixmap(renamed_icon, 24)
                        
                        category_btn.update()
                        
                        if category_btn.is_selected:
                            self.tools_title.setText(new_name)
                        
                        self.save_data()
                break
    
    def save_data(self):
        data = {
            'custom_tools': self.custom_tools,
            'custom_categories': []
        }
        
        category_order = []
        tools_order = {}
        category_appearance = {}
        tools_appearance = {}
        
        for category in self.custom_categories:
            category_data = {
                'name': category['name'],
                'icon': category['button'].icon_name,
                'color': category['button'].icon_color,
                'tools_data': []
            }
            
            if 'tools_data' in category:
                category_data['tools_data'] = category['tools_data']
            
            data['custom_categories'].append(category_data)
            
            category_order.append(category['name'])
            tools_order[category['name']] = [entry.get('name', '') for entry in category.get('tools_data', [])]
            
            category_appearance[category['name']] = {
                'icon': category['button'].icon_name,
                'color': category['button'].icon_color
            }
            
            tools_appearance[category['name']] = {
                entry.get('name', ''): {
                    'icon': entry.get('icon', ''),
                    'color': entry.get('color', '')
                }
                for entry in category.get('tools_data', [])
            }
        
        animo_data.save_tools_data(data)
        animo_data.save_library_order(category_order, tools_order, category_appearance, tools_appearance)
    
    def load_data(self):
        data = animo_data.load_tools_data()
        
        self.custom_tools = data.get('custom_tools', [])
        
        category_list = data.get('custom_categories', [])
        category_list = [
            category_data for category_data in category_list
            if category_data.get('name', '').strip().lower() != 'icons'
        ]
        needs_migration = False
        
        if needs_migration:
            self._migrate_recommended_tools_to_library()
        
        for category_data in category_list:
            icon = category_data.get('icon', 'recommended')
            color = category_data.get('color', '#4A4A4A')
            
            self._add_category_widget(
                category_data['name'],
                icon=icon,
                color=color,
                tools_data=category_data.get('tools_data', [])
            )
        
        if needs_migration:
            self.save_data()
        
        self.sync_tools_library()
        self._sync_tools_from_disk()
        self._apply_saved_library_order()
        self._apply_category_row_shading()
        self.load_hotkeys_from_data()
        self.save_data()
    
    def _apply_saved_library_order(self):
        order_data = animo_data.load_library_order()
        category_order = order_data.get('category_order', [])
        tools_order = order_data.get('tools_order', {})
        category_appearance = order_data.get('category_appearance', {})
        tools_appearance = order_data.get('tools_appearance', {})
        
        if category_order:
            ordered = []
            remaining = list(self.custom_categories)
            
            for name in category_order:
                for category in remaining:
                    if category['name'] == name:
                        ordered.append(category)
                        remaining.remove(category)
                        break
            
            ordered.extend(remaining)
            self.custom_categories = ordered
        
        for category in self.custom_categories:
            saved_tool_names = tools_order.get(category['name'])
            if saved_tool_names:
                remaining_tools = list(category.get('tools_data', []))
                ordered_tools = []
                
                for tool_name in saved_tool_names:
                    for entry in remaining_tools:
                        if entry.get('name', '') == tool_name:
                            ordered_tools.append(entry)
                            remaining_tools.remove(entry)
                            break
                
                ordered_tools.extend(remaining_tools)
                category['tools_data'] = ordered_tools
            
            appearance = category_appearance.get(category['name'])
            if appearance:
                btn = category['button']
                new_icon = appearance.get('icon')
                new_color = appearance.get('color')
                
                if new_icon and (new_icon != btn.icon_name or new_color != btn.icon_color):
                    if new_icon != btn.icon_name:
                        btn.icon_name = new_icon
                    if new_color:
                        btn.icon_color = new_color
                    btn.icon_pixmap = self.icon_manager.create_pixmap(new_icon, 24)
                    btn.update()
            
            category_tool_appearance = tools_appearance.get(category['name'], {})
            if category_tool_appearance:
                for entry in category.get('tools_data', []):
                    tool_appearance = category_tool_appearance.get(entry.get('name', ''))
                    if tool_appearance:
                        if tool_appearance.get('icon'):
                            entry['icon'] = tool_appearance['icon']
                        if tool_appearance.get('color'):
                            entry['color'] = tool_appearance['color']
        
        self._refresh_category_widget_order()
    
    def _migrate_recommended_tools_to_library(self):
        tools_source_dir = os.path.join(_this_dir, tool_defaults.TOOLS_FOLDER)
        gifs_source_dir = os.path.join(_this_dir, 'gifs')
        
        migrated_tools = []
        
        for icon_name, color, label, script_data in RECOMMENDED_TOOLS:
            script_file = script_data.get('script_file', '')
            if not script_file:
                continue
            
            script_path = os.path.join(tools_source_dir, script_file)
            
            try:
                with open(script_path, 'r') as f:
                    script_content = f.read()
            except Exception:
                continue
            
            tooltip = tooltip_data.get_tooltip_data(label)
            
            tool_entry = {
                'name': label,
                'icon': icon_name,
                'color': color,
                'script': script_content,
                'description': tooltip.get('description', ''),
                'script_type': 'Python',
                'tooltip_title': tooltip.get('title', label),
                'tooltip_description': tooltip.get('description', '')
            }
            
            tool_entry['file_path'] = animo_data.save_category_tool_file(
                'Animo Tools', label, script_content, 'Python'
            )
            
            gif_name = os.path.splitext(script_file)[0] + '.gif'
            source_gif_path = os.path.join(gifs_source_dir, gif_name)
            if os.path.exists(source_gif_path):
                tool_entry['tooltip_gif_path'] = animo_data.save_category_tool_gif(
                    'Animo Tools', label, source_gif_path
                ) or ''
            else:
                tool_entry['tooltip_gif_path'] = ''
            
            animo_data.save_tooltip_sidecar(tool_entry)
            
            migrated_tools.append(tool_entry)
        
        self._add_category_widget('Animo Tools', icon='recommended', color='#5A8AB5', tools_data=migrated_tools)
    
    def sync_tools_library(self):
        changed = False
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                file_path = entry.get('file_path')
                if file_path and os.path.exists(file_path):
                    continue
                
                reconstructed_path = animo_data.resolve_path_relative_to_tools_library(file_path)
                if reconstructed_path:
                    entry['file_path'] = reconstructed_path
                    changed = True
        
        for category in self.custom_categories:
            tools_data = category.get('tools_data', [])
            if not tools_data:
                continue
            
            by_name = {}
            for entry in tools_data:
                by_name.setdefault(entry.get('name'), []).append(entry)
            
            entries_to_remove = set()
            
            for name, entries in by_name.items():
                if len(entries) < 2:
                    continue
                
                valid_entries = [e for e in entries if e.get('file_path') and os.path.exists(e.get('file_path'))]
                valid_ids = set(id(e) for e in valid_entries)
                broken_entries = [e for e in entries if id(e) not in valid_ids]
                
                if not valid_entries or not broken_entries:
                    continue
                
                valid_path = valid_entries[0].get('file_path')
                
                keeper = None
                for e in broken_entries:
                    if e.get('description') != 'Found in tools_library':
                        keeper = e
                        break
                if keeper is None:
                    keeper = broken_entries[0]
                
                keeper['file_path'] = valid_path
                if not keeper.get('tooltip_gif_path'):
                    for e in valid_entries:
                        if e.get('tooltip_gif_path'):
                            keeper['tooltip_gif_path'] = e.get('tooltip_gif_path')
                            break
                
                for e in entries:
                    if e is keeper:
                        continue
                    entries_to_remove.add(id(e))
            
            if entries_to_remove:
                category['tools_data'] = [e for e in tools_data if id(e) not in entries_to_remove]
                changed = True
        
        tracked_paths = set()
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                file_path = entry.get('file_path')
                if file_path:
                    tracked_paths.add(os.path.normcase(os.path.normpath(file_path)))
        
        scanned_folders = animo_data.scan_tools_library()
        
        for folder_name, file_paths in scanned_folders.items():
            category = None
            for existing in self.custom_categories:
                if animo_data.sanitize_name(existing['name']) == folder_name:
                    category = existing
                    break
            
            if category is None:
                category = self._add_category_widget(folder_name)
                changed = True
            
            if 'tools_data' not in category:
                category['tools_data'] = []
            
            for file_path in file_paths:
                normalized_path = os.path.normcase(os.path.normpath(file_path))
                if normalized_path in tracked_paths:
                    continue
                
                tool_name = os.path.splitext(os.path.basename(file_path))[0]
                
                repaired_entry = None
                for existing_entry in category['tools_data']:
                    if existing_entry.get('name') != tool_name:
                        continue
                    existing_path = existing_entry.get('file_path')
                    if existing_path and os.path.exists(existing_path):
                        continue
                    repaired_entry = existing_entry
                    break
                
                if repaired_entry is not None:
                    repaired_entry['file_path'] = file_path
                    tracked_paths.add(normalized_path)
                    changed = True
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        script_content = f.read()
                except Exception:
                    continue
                
                extension = os.path.splitext(file_path)[1].lower()
                script_type = "MEL" if extension == ".mel" else "Python"
                tool_name = os.path.splitext(os.path.basename(file_path))[0]
                
                tool_entry = {
                    'name': tool_name,
                    'icon': pick_icon_for_tool(tool_name),
                    'color': pick_color_for_index(len(category['tools_data'])),
                    'script': animo_data.wrap_script_for_command(script_type, script_content),
                    'description': 'Found in tools_library',
                    'script_type': script_type,
                    'file_path': file_path
                }
                
                sidecar_path = os.path.splitext(file_path)[0] + '.tooltip.json'
                if os.path.exists(sidecar_path):
                    try:
                        with open(sidecar_path, 'r') as f:
                            sidecar_data = json.load(f)
                        tool_entry['tooltip_title'] = sidecar_data.get('title', '')
                        tool_entry['tooltip_description'] = sidecar_data.get('description', '')
                        sidecar_gif_width = sidecar_data.get('gif_width')
                        if sidecar_gif_width:
                            tool_entry['tooltip_gif_width'] = sidecar_gif_width
                    except Exception:
                        pass
                
                resolved_gif_path = animo_data.resolve_gif_path_from_sidecar(file_path)
                if resolved_gif_path:
                    tool_entry['tooltip_gif_path'] = resolved_gif_path
                
                category['tools_data'].append(tool_entry)
                tracked_paths.add(normalized_path)
                changed = True
        
        if changed:
            self.save_data()
    
    def export_tool_library(self):
        self.save_data()
        
        default_path = os.path.join(os.path.expanduser("~"), "AnimoToolsLibrary_Export.zip")
        dest_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Tool Library", default_path, "Zip Files (*.zip)"
        )
        
        if not dest_path:
            return
        
        if not dest_path.lower().endswith('.zip'):
            dest_path += '.zip'
        
        try:
            animo_data.export_tool_library_zip(dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Failed", "Could not export the tool library:\n{0}".format(str(e)))
            return
        
        try:
            cmds.inViewMessage(amg='Tool library exported successfully', pos='midCenter', fade=True)
        except Exception:
            pass
    
    def import_tool_library(self):
        source_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Tool Library", "", "Zip Files (*.zip)"
        )
        
        if not source_path:
            return
        
        try:
            temp_dir = animo_data.extract_tool_library_zip(source_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Import Failed", "Could not read the selected file:\n{0}".format(str(e)))
            return
        
        imported_json_path = os.path.join(temp_dir, "animo_tools.json")
        if not os.path.exists(imported_json_path):
            QtWidgets.QMessageBox.warning(self, "Import Failed", "This doesn't look like a Tool Library export.")
            return
        
        try:
            with open(imported_json_path, 'r') as f:
                imported_data = json.load(f)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Import Failed", "Could not read the exported data:\n{0}".format(str(e)))
            return
        
        imported_tools_library = os.path.join(temp_dir, "tools_library")
        
        added_categories = 0
        added_tools = 0
        skipped_tools = 0
        
        for imported_category in imported_data.get('custom_categories', []):
            cat_name = imported_category.get('name', '')
            if not cat_name:
                continue
            
            local_category = None
            for category in self.custom_categories:
                if category['name'] == cat_name:
                    local_category = category
                    break
            
            if local_category is None:
                local_category = self._add_category_widget(
                    cat_name,
                    icon=imported_category.get('icon', 'recommended'),
                    color=imported_category.get('color', '#4A4A4A'),
                    tools_data=[]
                )
                animo_data.get_category_folder_path(cat_name, create=True)
                added_categories += 1
            
            local_names = set(entry.get('name', '') for entry in local_category.get('tools_data', []))
            target_folder = animo_data.get_category_folder_path(cat_name, create=True)
            
            for imported_tool in imported_category.get('tools_data', []):
                tool_name = imported_tool.get('name', '')
                if not tool_name:
                    continue
                
                if tool_name in local_names:
                    skipped_tools += 1
                    continue
                
                new_entry = dict(imported_tool)
                
                script_type = new_entry.get('script_type', 'Python')
                extension = ".mel" if script_type == "MEL" else ".py"
                desired_filename = animo_data.sanitize_name(tool_name) + extension
                
                new_file_path = animo_data.copy_imported_tool_asset(
                    imported_tools_library,
                    imported_tool.get('file_path', ''),
                    target_folder,
                    desired_filename
                )
                
                if not new_file_path:
                    new_file_path = animo_data.save_category_tool_file(
                        cat_name, tool_name, new_entry.get('script', ''), script_type
                    )
                
                new_entry['file_path'] = new_file_path
                
                old_gif = imported_tool.get('tooltip_gif_path', '')
                if old_gif:
                    gif_filename = animo_data.sanitize_name(tool_name) + ".tooltip.gif"
                    new_gif_path = animo_data.copy_imported_tool_asset(
                        imported_tools_library, old_gif, target_folder, gif_filename
                    )
                    new_entry['tooltip_gif_path'] = new_gif_path
                
                old_sidecar_rel = imported_tool.get('file_path', '')
                if old_sidecar_rel:
                    sidecar_rel = os.path.splitext(old_sidecar_rel)[0] + '.tooltip.json'
                    sidecar_filename = os.path.splitext(desired_filename)[0] + '.tooltip.json'
                    animo_data.copy_imported_tool_asset(
                        imported_tools_library, sidecar_rel, target_folder, sidecar_filename
                    )
                
                local_category['tools_data'].append(new_entry)
                local_names.add(tool_name)
                added_tools += 1
        
        imported_hotkeys_path = os.path.join(temp_dir, "animo_hotkeys.json")
        if os.path.exists(imported_hotkeys_path):
            try:
                with open(imported_hotkeys_path, 'r') as f:
                    imported_hotkeys = json.load(f)
                local_hotkeys = animo_data.load_hotkeys_data()
                hotkeys_changed = False
                for name, hotkey_text in imported_hotkeys.items():
                    if name not in local_hotkeys:
                        local_hotkeys[name] = hotkey_text
                        hotkeys_changed = True
                if hotkeys_changed:
                    animo_data.save_hotkeys_data(local_hotkeys)
            except Exception:
                pass
        
        imported_custom_icons = os.path.join(temp_dir, "icons", "custom")
        if os.path.isdir(imported_custom_icons):
            local_custom_icons = os.path.join(animo_data.get_animo_data_path(), "icons", "custom")
            try:
                if not os.path.isdir(local_custom_icons):
                    os.makedirs(local_custom_icons)
                for filename in os.listdir(imported_custom_icons):
                    target_icon_path = os.path.join(local_custom_icons, filename)
                    if not os.path.exists(target_icon_path):
                        shutil.copyfile(os.path.join(imported_custom_icons, filename), target_icon_path)
            except Exception:
                pass
        
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
        
        self._apply_category_row_shading()
        self.save_data()
        
        selected_category = None
        for category in self.custom_categories:
            if category['button'].is_selected:
                selected_category = category
                break
        if selected_category is not None:
            self.load_category_tools(selected_category)
        
        summary = "Import complete.\n\n{0} new categor{1} added\n{2} new tool{3} added\n{4} already existed and {5} kept unchanged".format(
            added_categories, "y" if added_categories == 1 else "ies",
            added_tools, "" if added_tools == 1 else "s",
            skipped_tools, "was" if skipped_tools == 1 else "were"
        )
        QtWidgets.QMessageBox.information(self, "Import Tool Library", summary)
    
    def refresh_contents(self):
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            self._refresh_contents_impl()
        finally:
            if app:
                app.restoreOverrideCursor()
    
    def _refresh_contents_impl(self):
        self.sync_tools_library()
        
        removed_categories = []
        for category in self.custom_categories:
            folder_path = animo_data.get_category_folder_path(category['name'], create=False)
            if not os.path.isdir(folder_path):
                removed_categories.append(category)
        
        for category in removed_categories:
            was_selected = category['button'].is_selected
            category['button'].setParent(None)
            category['button'].deleteLater()
            self.custom_categories.remove(category)
            if was_selected:
                self.select_default_category()
        
        self._sync_tools_from_disk()
        
        self._apply_saved_library_order()
        self._apply_category_row_shading()
        self.save_data()
        
        selected_category = None
        for category in self.custom_categories:
            if category['button'].is_selected:
                selected_category = category
                break
        
        if selected_category is not None:
            self.load_category_tools(selected_category)
    
    def _sync_tools_from_disk(self):
        for category in self.custom_categories:
            removed_entries = []
            
            for entry in category.get('tools_data', []):
                file_path = entry.get('file_path')
                
                if not file_path:
                    new_file_path = animo_data.ensure_category_tool_file(category['name'], entry)
                    entry['file_path'] = new_file_path
                    continue
                
                if not os.path.exists(file_path):
                    removed_entries.append(entry)
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        disk_content = f.read()
                except Exception:
                    continue
                
                script_type = entry.get('script_type', 'Python')
                wrapped_content = animo_data.wrap_script_for_command(script_type, disk_content)
                
                if wrapped_content != entry.get('script', ''):
                    entry['script'] = wrapped_content
                
                sidecar_path = os.path.splitext(file_path)[0] + '.tooltip.json'
                sidecar_exists = os.path.exists(sidecar_path)
                if sidecar_exists:
                    try:
                        with open(sidecar_path, 'r') as f:
                            sidecar_data = json.load(f)
                        entry['tooltip_title'] = sidecar_data.get('title', entry.get('tooltip_title', ''))
                        entry['tooltip_description'] = sidecar_data.get('description', entry.get('tooltip_description', ''))
                        sidecar_gif_width = sidecar_data.get('gif_width')
                        if sidecar_gif_width:
                            entry['tooltip_gif_width'] = sidecar_gif_width
                    except Exception:
                        pass
                
                current_gif_path = entry.get('tooltip_gif_path')
                if current_gif_path and os.path.exists(current_gif_path):
                    pass
                elif current_gif_path or sidecar_exists:
                    resolved_gif_path = animo_data.resolve_gif_path_from_sidecar(file_path)
                    if resolved_gif_path:
                        entry['tooltip_gif_path'] = resolved_gif_path
            
            for entry in removed_entries:
                category['tools_data'].remove(entry)
                
                gif_path = entry.get('tooltip_gif_path')
                if gif_path and os.path.exists(gif_path):
                    try:
                        os.remove(gif_path)
                    except Exception:
                        pass
    
    def save_hotkeys_to_data(self):
        hotkeys_dict = {}
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                hotkey_text = entry.get('hotkey', '')
                if hotkey_text:
                    hotkeys_dict[entry.get('name', '')] = hotkey_text
        
        animo_data.save_hotkeys_data(hotkeys_dict)
    
    def load_hotkeys_from_data(self):
        hotkeys_dict = animo_data.load_hotkeys_data()
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    if widget.hotkey_input.text().strip():
                        continue
                    if widget.label_text in hotkeys_dict:
                        hotkey_text = hotkeys_dict[widget.label_text]
                        widget.hotkey_input.setText(hotkey_text)
                        if widget.tool_entry is not None:
                            widget.tool_entry['hotkey'] = hotkey_text
    
    def _register_hotkey_for_entry(self, entry):
        hotkey_text = entry.get('hotkey', '')
        if not hotkey_text:
            return None
        
        tool_name = entry.get('name', '')
        command = entry.get('script', 'print("Execute: {0}")'.format(tool_name))
        script_type = entry.get('script_type', 'Python')
        language = "python" if script_type == "Python" else "mel"
        
        try:
            success, message = animo_hotkeys.assign_hotkey(command, hotkey_text, tool_name, language)
        except Exception:
            success = False
        
        return success
    
    def clear_duplicate_hotkey(self, hotkey_text, keep_entry):
        if not hotkey_text:
            return
        
        visible_widgets_by_entry_id = {}
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem) and widget.tool_entry is not None:
                    visible_widgets_by_entry_id[id(widget.tool_entry)] = widget
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                if entry is keep_entry:
                    continue
                if entry.get('hotkey', '') == hotkey_text:
                    entry['hotkey'] = ''
                    
                    widget = visible_widgets_by_entry_id.get(id(entry))
                    if widget is not None:
                        widget.hotkey_input.clear()
                        widget.hotkey_input.hotkey = ''
                        widget.hotkey_input.setStyleSheet(widget._hotkey_input_style("default"))
    
    def _apply_all_hotkeys_silent(self):
        applied_count = 0
        failed_count = 0
        
        visible_widgets_by_name = {}
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    visible_widgets_by_name[widget.label_text] = widget
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                hotkey_text = entry.get('hotkey', '')
                if not hotkey_text:
                    continue
                
                success = self._register_hotkey_for_entry(entry)
                
                if success:
                    applied_count += 1
                    self.clear_duplicate_hotkey(hotkey_text, entry)
                else:
                    failed_count += 1
                
                widget = visible_widgets_by_name.get(entry.get('name', ''))
                if widget is not None and widget.tool_entry is entry:
                    widget.hotkey_input.setStyleSheet(widget._hotkey_input_style("success" if success else "error"))
        
        self.save_hotkeys_to_data()
        
        return applied_count, failed_count
    
    def clear_all_hotkeys(self):
        has_any_hotkey = any(
            entry.get('hotkey', '')
            for category in self.custom_categories
            for entry in category.get('tools_data', [])
        )
        
        if not has_any_hotkey:
            info_box = QtWidgets.QMessageBox(self)
            info_box.setWindowTitle("Clear All Hotkeys")
            info_box.setText("There are no hotkeys assigned to clear.")
            info_box.setIcon(QtWidgets.QMessageBox.Information)
            info_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            info_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in info_box.buttons():
                button.setMinimumSize(scale_size(70), scale_size(28))
            
            info_box.exec_()
            return
        
        confirm_box = QtWidgets.QMessageBox(self)
        confirm_box.setWindowTitle("Clear All Hotkeys")
        confirm_box.setText("Are you sure you want to clear all hotkeys?\nThis removes them from every category and un-assigns them in Maya.")
        confirm_box.setIcon(QtWidgets.QMessageBox.Question)
        confirm_box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirm_box.setDefaultButton(QtWidgets.QMessageBox.No)
        confirm_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in confirm_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        if confirm_box.exec_() != QtWidgets.QMessageBox.Yes:
            return
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            cleared_count = self._clear_all_hotkeys_silent()
            self.save_data()
        finally:
            if app:
                app.restoreOverrideCursor()
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Clear All Hotkeys")
        msg_box.setText("Cleared {0} hotkey(s).".format(cleared_count))
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in msg_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        msg_box.exec_()
    
    def _clear_all_hotkeys_silent(self):
        cleared_count = 0
        
        visible_widgets_by_name = {}
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    visible_widgets_by_name[widget.label_text] = widget
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                hotkey_text = entry.get('hotkey', '')
                if not hotkey_text:
                    continue
                
                try:
                    animo_hotkeys.remove_hotkey(hotkey_text)
                except Exception:
                    pass
                
                entry['hotkey'] = ''
                cleared_count += 1
                
                widget = visible_widgets_by_name.get(entry.get('name', ''))
                if widget is not None and widget.tool_entry is entry:
                    widget.hotkey_input.clear()
                    widget.hotkey_input.hotkey = ''
                    widget.hotkey_input.setStyleSheet(widget._hotkey_input_style("default"))
        
        self.save_hotkeys_to_data()
        
        return cleared_count
    
    def apply_all_hotkeys(self):
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            applied_count, failed_count = self._apply_all_hotkeys_silent()
        finally:
            if app:
                app.restoreOverrideCursor()
        
        if applied_count > 0 or failed_count > 0:
            msg = "Applied {0} hotkey(s)".format(applied_count)
            if failed_count > 0:
                msg += "\nFailed: {0}".format(failed_count)
            
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Apply Hotkeys")
            msg_box.setText(msg)
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in msg_box.buttons():
                button.setMinimumSize(scale_size(70), scale_size(28))
            
            msg_box.exec_()
    
    def export_hotkeys(self):
        hotkeys_data = {}
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                hotkey_text = entry.get('hotkey', '')
                if hotkey_text:
                    hotkeys_data[entry.get('name', '')] = hotkey_text
        
        if not hotkeys_data:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Export Hotkeys")
            msg_box.setText("There are no hotkeys assigned yet, so there's nothing to export.")
            msg_box.setIcon(QtWidgets.QMessageBox.Information)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in msg_box.buttons():
                button.setMinimumSize(scale_size(70), scale_size(28))
            
            msg_box.exec_()
            return
        
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Hotkeys",
            "animo_hotkeys.json",
            "JSON Files (*.json)"
        )
        
        if file_path:
            animo_data.export_hotkeys(file_path, hotkeys_data)
    
    def import_hotkeys(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import Hotkeys",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        hotkeys_data = animo_data.import_hotkeys(file_path)
        
        if not hotkeys_data:
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("Import Hotkeys")
            msg_box.setText("That file couldn't be read as a hotkeys export.")
            msg_box.setIcon(QtWidgets.QMessageBox.Warning)
            msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
            
            for button in msg_box.buttons():
                button.setMinimumSize(scale_size(70), scale_size(28))
            
            msg_box.exec_()
            return
        
        imported_count = 0
        
        for category in self.custom_categories:
            for entry in category.get('tools_data', []):
                tool_name = entry.get('name', '')
                if tool_name in hotkeys_data:
                    entry['hotkey'] = hotkeys_data[tool_name]
                    imported_count += 1
        
        for i in range(self.tools_layout.count()):
            item = self.tools_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, ToolItem):
                    if widget.label_text in hotkeys_data:
                        widget.hotkey_input.setText(hotkeys_data[widget.label_text])
        
        app = QtWidgets.QApplication.instance()
        if app:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        try:
            applied_count, failed_count = self._apply_all_hotkeys_silent()
            self.save_data()
        finally:
            if app:
                app.restoreOverrideCursor()
        
        msg = "Imported {0} hotkey(s) and applied {1} of them in Maya.".format(imported_count, applied_count)
        if failed_count > 0:
            msg += "\nFailed to apply: {0}".format(failed_count)
        
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle("Import Hotkeys")
        msg_box.setText(msg)
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.setStyleSheet(styles.MESSAGE_BOX_STYLE)
        
        for button in msg_box.buttons():
            button.setMinimumSize(scale_size(70), scale_size(28))
        
        msg_box.exec_()
    
    def closeEvent(self, event):
        self.save_data()
        event.accept()
