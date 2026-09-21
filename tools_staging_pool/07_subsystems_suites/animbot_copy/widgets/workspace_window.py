"""
animBot Workspace Window & Tool Library Editor.
Multi-column visual workspace manager with separate settings for:
1. Main Toolbar (时间轴顶部/底部, 工具架, 视口, 状态栏, 悬浮)
2. Graph Editor Toolbar (图形编辑器顶部, 在图形编辑器菜单下, 图形编辑器底部)
Independent alignments, tool selection, and robust Maya window persistence (Maya-level stay on top).
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle
from ..core.icons import AnimBotIconProvider
from ..core.workspace_manager import WORKSPACE_MGR

_WORKSPACE_WINDOW_INSTANCE = None

def get_maya_main_window():
    """Retrieve Maya's main QMainWindow instance."""
    app = QtWidgets.QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QtWidgets.QMainWindow) and "Maya" in widget.windowTitle():
            return widget
    return None

class WorkspaceWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        # Parent directly to Maya's main window so it stays on top within Maya ONLY (not global Windows level)
        maya_win = get_maya_main_window()
        super().__init__(parent=maya_win or parent)
        self.setObjectName("animBotWorkspaceWindow")
        self.setWindowTitle("Workspace")
        self.resize(1300, 720)
        # Maya-level top window without global Windows WindowStaysOnTopHint
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowCloseButtonHint)
        
        self.active_toolbar_type = "main" # "main" or "graph_editor"
        self.selected_color_key = "orange"
        self.selected_module_key = "tangents"
        
        self.setStyleSheet(f"""
        QDialog {{
            background-color: {AnimBotColors.BG_DARK};
            color: {AnimBotColors.TEXT_MAIN};
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 13px;
        }}
        QListWidget {{
            background-color: #242424;
            border: 1px solid #363636;
            border-radius: 4px;
            color: #D0D0D0;
            padding: 4px;
            outline: none;
        }}
        QListWidget::item {{
            padding: 4px 8px;
            border-radius: 3px;
            min-height: 24px;
            margin: 1px 0px;
        }}
        QListWidget::item:hover {{
            background-color: #383838;
            color: #FFFFFF;
        }}
        QListWidget::item:selected {{
            background-color: #3F729B;
            color: #FFFFFF;
        }}
        QHeaderView::section {{
            background-color: transparent;
            color: #888888;
            font-weight: bold;
            font-size: 12px;
            padding: 4px;
            border: none;
        }}
        QPushButton {{
            background-color: #383838;
            border: 1px solid #484848;
            border-radius: 4px;
            color: #E0E0E0;
            padding: 8px 16px;
            font-size: 12px;
        }}
        QPushButton:hover {{
            background-color: #484848;
            border: 1px solid #606060;
            color: #FFFFFF;
        }}
        QPushButton:pressed {{
            background-color: #2A2A2A;
        }}
        QLabel {{
            color: #999999;
            font-size: 12px;
            font-weight: bold;
        }}
        QCheckBox {{
            color: #E0E0E0;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 1px solid #555555;
            background: #2C2C2C;
        }}
        QCheckBox::indicator:checked {{
            background: #4A90E2;
            border: 1px solid #70B0FF;
        }}
        """)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)
        
        self._build_header()
        self._build_columns()
        self._build_footer()
        
        self._load_presets()
        self._load_toolbar_specific_ui()
        self._load_color_groups()
        self._select_default_items()
        
        # Connect live updates from workspace manager (e.g. right-click slider mode changes)
        WORKSPACE_MGR.toolToggled.connect(self._on_external_tool_toggled)
        WORKSPACE_MGR.workspaceChanged.connect(self._on_external_workspace_changed)

    def _on_external_tool_toggled(self, tool_id, active, toolbar_type):
        if toolbar_type == self.active_toolbar_type:
            for i in range(self.list_items.count()):
                it = self.list_items.item(i)
                if it.data(QtCore.Qt.UserRole) == tool_id:
                    self.list_items.blockSignals(True)
                    it.setCheckState(QtCore.Qt.Checked if active else QtCore.Qt.Unchecked)
                    self.list_items.blockSignals(False)
                    break

    def _on_external_workspace_changed(self, toolbar_type):
        if toolbar_type == self.active_toolbar_type and self.selected_color_key and self.selected_module_key:
            self._load_items_for_module(self.selected_color_key, self.selected_module_key)

    def _build_header(self):
        header_layout = QtWidgets.QHBoxLayout()
        
        lbl_logo = QtWidgets.QLabel(self)
        lbl_logo.setPixmap(AnimBotIconProvider.get_icon("logo", size=QtCore.QSize(24, 24)).pixmap(24, 24))
        
        lbl_title = QtWidgets.QLabel("Workspace", self)
        lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFFFFF;")
        
        header_layout.addWidget(lbl_logo)
        header_layout.addWidget(lbl_title)
        header_layout.addStretch(1)
        
        btn_help = QtWidgets.QToolButton(self)
        btn_help.setText("?")
        btn_help.setStyleSheet("color: #888888; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        header_layout.addWidget(btn_help)
        
        self.main_layout.addLayout(header_layout)

    def _build_columns(self):
        self.cols_layout = QtWidgets.QHBoxLayout()
        self.cols_layout.setSpacing(8)
        
        # Col 1: Workspace Presets
        col1 = self._create_col("Workspace", width=140)
        self.list_presets = QtWidgets.QListWidget(self)
        self.list_presets.setSpacing(2)
        self.list_presets.itemClicked.connect(self._on_preset_clicked)
        col1.layout().addWidget(self.list_presets)
        self.cols_layout.addWidget(col1)

        # Col 2: 工具栏 (Toolbars)
        col2 = self._create_col("工具栏", width=150)
        self.list_toolbars = QtWidgets.QListWidget(self)
        self.list_toolbars.setSpacing(2)
        for name in ["主工具栏", "Graph Editor Toolbar"]:
            it = QtWidgets.QListWidgetItem(name)
            it.setSizeHint(QtCore.QSize(0, 28))
            self.list_toolbars.addItem(it)
        self.list_toolbars.setCurrentRow(0)
        self.list_toolbars.itemClicked.connect(self._on_toolbar_changed)
        col2.layout().addWidget(self.list_toolbars)
        self.cols_layout.addWidget(col2)

        # Col 3: 位置 (Location)
        col3 = self._create_col("位置", width=140)
        self.list_locations = QtWidgets.QListWidget(self)
        self.list_locations.setSpacing(2)
        self.list_locations.itemClicked.connect(self._on_location_clicked)
        col3.layout().addWidget(self.list_locations)
        self.cols_layout.addWidget(col3)

        # Col 4: 对齐 (Alignment)
        col4 = self._create_col("对齐", width=110)
        self.list_alignments = QtWidgets.QListWidget(self)
        self.list_alignments.setSpacing(2)
        self.list_alignments.itemClicked.connect(self._on_alignment_clicked)
        col4.layout().addWidget(self.list_alignments)
        self.cols_layout.addWidget(col4)

        # Col 5: 颜色组 (Color Group)
        col5 = self._create_col("颜色组", width=130)
        self.list_colors = QtWidgets.QListWidget(self)
        self.list_colors.setSpacing(2)
        self.list_colors.itemClicked.connect(self._on_color_clicked)
        col5.layout().addWidget(self.list_colors)
        self.cols_layout.addWidget(col5)

        # Col 6: 工具模块 (Tools in Selected Group)
        col6 = self._create_col("工具", width=160)
        self.list_modules = QtWidgets.QListWidget(self)
        self.list_modules.setSpacing(2)
        self.list_modules.itemClicked.connect(self._on_module_clicked)
        col6.layout().addWidget(self.list_modules)
        self.cols_layout.addWidget(col6)

        # Col 7: 按钮明细 (Sub-tool items with toggle checkboxes)
        self.col7 = self._create_col("功能明细 (激活显示在工具栏)", width=270)
        self.list_items = QtWidgets.QListWidget(self)
        self.list_items.setSpacing(2)
        self.list_items.itemChanged.connect(self._on_item_toggled)
        self.col7.layout().addWidget(self.list_items)
        self.cols_layout.addWidget(self.col7)

        self.main_layout.addLayout(self.cols_layout)

    def _create_col(self, title, width=120):
        w = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        lbl = QtWidgets.QLabel(title, w)
        layout.addWidget(lbl)
        w.setMinimumWidth(width)
        return w

    def _build_footer(self):
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setSpacing(10)
        
        btn_new = QtWidgets.QPushButton("+ 新建工作区", self)
        btn_new.clicked.connect(self._on_new_workspace)
        
        btn_restore = QtWidgets.QPushButton("↺ Restore Defaults (恢复默认)", self)
        btn_restore.clicked.connect(self._on_restore_defaults)
        
        btn_import = QtWidgets.QPushButton("↓ 导入工作区", self)
        btn_export = QtWidgets.QPushButton("↑ 导出工作区", self)
        
        btn_close = QtWidgets.QPushButton("✕ 关闭", self)
        btn_close.clicked.connect(self.close)
        
        footer_layout.addWidget(btn_new)
        footer_layout.addWidget(btn_restore)
        footer_layout.addWidget(btn_import)
        footer_layout.addWidget(btn_export)
        footer_layout.addStretch(1)
        footer_layout.addWidget(btn_close)
        
        self.main_layout.addLayout(footer_layout)

    def _load_presets(self):
        self.list_presets.clear()
        for p in WORKSPACE_MGR.PRESETS.keys():
            item = QtWidgets.QListWidgetItem(p)
            item.setSizeHint(QtCore.QSize(0, 28))
            self.list_presets.addItem(item)
            if p == WORKSPACE_MGR.current_preset:
                item.setSelected(True)
                self.list_presets.setCurrentItem(item)

    def _load_toolbar_specific_ui(self):
        """Update Col 3 (Locations) & Col 4 (Alignments) based on active toolbar type."""
        # 1. Locations
        self.list_locations.blockSignals(True)
        self.list_locations.clear()
        
        locations = (
            WORKSPACE_MGR.MAIN_LOCATIONS 
            if self.active_toolbar_type == "main" 
            else WORKSPACE_MGR.GRAPH_EDITOR_LOCATIONS
        )
        cur_loc = WORKSPACE_MGR.get_location(self.active_toolbar_type)
        
        for loc in locations:
            item = QtWidgets.QListWidgetItem(loc)
            item.setSizeHint(QtCore.QSize(0, 28))
            self.list_locations.addItem(item)
            if loc == cur_loc:
                item.setSelected(True)
                self.list_locations.setCurrentItem(item)
        self.list_locations.blockSignals(False)

        # 2. Alignments
        self.list_alignments.blockSignals(True)
        self.list_alignments.clear()
        for align_name in ["左对齐", "右对齐", "居中对齐", "单行"]:
            item = QtWidgets.QListWidgetItem(align_name)
            item.setSizeHint(QtCore.QSize(0, 28))
            self.list_alignments.addItem(item)
            
        is_single = WORKSPACE_MGR.get_single_row(self.active_toolbar_type)
        cur_align = WORKSPACE_MGR.get_alignment(self.active_toolbar_type)
        
        target_txt = "单行" if is_single else ("左对齐" if cur_align == "left" else ("右对齐" if cur_align == "right" else "居中对齐"))
        for i in range(self.list_alignments.count()):
            it = self.list_alignments.item(i)
            if it.text() == target_txt:
                it.setSelected(True)
                self.list_alignments.setCurrentItem(it)
                break
        self.list_alignments.blockSignals(False)

    def _load_color_groups(self):
        self.list_colors.clear()
        for key, info in WORKSPACE_MGR.MAIN_TOOL_LIBRARY.items():
            item = QtWidgets.QListWidgetItem(info["display_name"])
            item.setData(QtCore.Qt.UserRole, key)
            item.setSizeHint(QtCore.QSize(0, 28))
            
            pix = QtGui.QPixmap(14, 14)
            pix.fill(QtGui.QColor(info["color"]))
            item.setIcon(QtGui.QIcon(pix))
            
            self.list_colors.addItem(item)

    def _select_default_items(self):
        for i in range(self.list_colors.count()):
            item = self.list_colors.item(i)
            if item.data(QtCore.Qt.UserRole) == "orange":
                self.list_colors.setCurrentItem(item)
                self._load_modules_for_color("orange")
                break

    def _on_toolbar_changed(self, item):
        txt = item.text()
        if "Graph" in txt:
            self.active_toolbar_type = "graph_editor"
            try:
                from ..ui.graph_editor_toolbar import attach_to_graph_editor
                attach_to_graph_editor()
            except Exception:
                pass
        else:
            self.active_toolbar_type = "main"
            
        self._load_toolbar_specific_ui()
        if self.selected_color_key and self.selected_module_key:
            self._load_items_for_module(self.selected_color_key, self.selected_module_key)

    def _on_alignment_clicked(self, item):
        txt = item.text()
        if "左" in txt:
            WORKSPACE_MGR.set_alignment(self.active_toolbar_type, "left")
            WORKSPACE_MGR.set_single_row(self.active_toolbar_type, False)
        elif "右" in txt:
            WORKSPACE_MGR.set_alignment(self.active_toolbar_type, "right")
            WORKSPACE_MGR.set_single_row(self.active_toolbar_type, False)
        elif "居中" in txt:
            WORKSPACE_MGR.set_alignment(self.active_toolbar_type, "center")
            WORKSPACE_MGR.set_single_row(self.active_toolbar_type, False)
        elif "单行" in txt:
            WORKSPACE_MGR.set_single_row(self.active_toolbar_type, True)

    def _on_location_clicked(self, item):
        loc = item.text()
        WORKSPACE_MGR.set_location(self.active_toolbar_type, loc)
        
        if self.active_toolbar_type == "main":
            from ..ui.workspace_control import dock_to_location
            dock_to_location(loc)
        else:
            from ..ui.graph_editor_toolbar import dock_graph_editor_toolbar
            dock_graph_editor_toolbar(loc)
            
        # Ensure WorkspaceWindow remains focused and never disappears
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_color_clicked(self, item):
        color_key = item.data(QtCore.Qt.UserRole)
        self.selected_color_key = color_key
        self._load_modules_for_color(color_key)

    def _load_modules_for_color(self, color_key):
        self.list_modules.clear()
        self.list_items.clear()
        
        cat_info = WORKSPACE_MGR.MAIN_TOOL_LIBRARY.get(color_key, {})
        modules = cat_info.get("modules", {})
        
        first_mod = None
        for mod_key, mod_info in modules.items():
            item = QtWidgets.QListWidgetItem(mod_info["label"])
            item.setData(QtCore.Qt.UserRole, mod_key)
            item.setSizeHint(QtCore.QSize(0, 28))
            self.list_modules.addItem(item)
            if not first_mod:
                first_mod = item
                
        if first_mod:
            self.list_modules.setCurrentItem(first_mod)
            self._load_items_for_module(color_key, first_mod.data(QtCore.Qt.UserRole))

    def _on_module_clicked(self, item):
        mod_key = item.data(QtCore.Qt.UserRole)
        self.selected_module_key = mod_key
        self._load_items_for_module(self.selected_color_key, mod_key)

    def _load_items_for_module(self, color_key, mod_key):
        self.list_items.blockSignals(True)
        self.list_items.clear()
        
        cat_info = WORKSPACE_MGR.MAIN_TOOL_LIBRARY.get(color_key, {})
        mod_info = cat_info.get("modules", {}).get(mod_key, {})
        tools = mod_info.get("tools", [])
        
        for tool_meta in tools:
            tool_id = tool_meta["id"]
            label = tool_meta["label"]
            icon_name = tool_meta.get("icon", tool_id)
            
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.UserRole, tool_id)
            item.setSizeHint(QtCore.QSize(0, 28))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            
            is_active = WORKSPACE_MGR.is_tool_active(tool_id, self.active_toolbar_type)
            item.setCheckState(QtCore.Qt.Checked if is_active else QtCore.Qt.Unchecked)
            
            icon = AnimBotIconProvider.get_icon(icon_name, color_key)
            item.setIcon(icon)
            
            self.list_items.addItem(item)
            
        self.list_items.blockSignals(False)

    def _on_item_toggled(self, item):
        tool_id = item.data(QtCore.Qt.UserRole)
        is_checked = (item.checkState() == QtCore.Qt.Checked)
        WORKSPACE_MGR.set_tool_active(tool_id, is_checked, self.active_toolbar_type)

    def _on_preset_clicked(self, item):
        preset_name = item.text()
        WORKSPACE_MGR.apply_preset(preset_name)
        self._load_toolbar_specific_ui()
        if self.selected_color_key and self.selected_module_key:
            self._load_items_for_module(self.selected_color_key, self.selected_module_key)

    def _on_restore_defaults(self):
        WORKSPACE_MGR.apply_preset("Classic *")
        self._load_presets()
        self._load_toolbar_specific_ui()
        if self.selected_color_key and self.selected_module_key:
            self._load_items_for_module(self.selected_color_key, self.selected_module_key)

    def _on_new_workspace(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "新建工作区", "请输入工作区名称:")
        if ok and name:
            WORKSPACE_MGR.PRESETS[name] = {
                "main": {
                    "active_tools": list(WORKSPACE_MGR.toolbar_configs["main"]["active_tools"]),
                    "location": WORKSPACE_MGR.get_location("main"),
                    "alignment": WORKSPACE_MGR.get_alignment("main"),
                    "single_row": WORKSPACE_MGR.get_single_row("main"),
                },
                "graph_editor": {
                    "active_tools": list(WORKSPACE_MGR.toolbar_configs["graph_editor"]["active_tools"]),
                    "location": WORKSPACE_MGR.get_location("graph_editor"),
                    "alignment": WORKSPACE_MGR.get_alignment("graph_editor"),
                    "single_row": WORKSPACE_MGR.get_single_row("graph_editor"),
                }
            }
            WORKSPACE_MGR.current_preset = name
            self._load_presets()

def show_workspace_window():
    global _WORKSPACE_WINDOW_INSTANCE
    if _WORKSPACE_WINDOW_INSTANCE is None:
        _WORKSPACE_WINDOW_INSTANCE = WorkspaceWindow()
    _WORKSPACE_WINDOW_INSTANCE.show()
    _WORKSPACE_WINDOW_INSTANCE.raise_()
    _WORKSPACE_WINDOW_INSTANCE.activateWindow()
    return _WORKSPACE_WINDOW_INSTANCE
