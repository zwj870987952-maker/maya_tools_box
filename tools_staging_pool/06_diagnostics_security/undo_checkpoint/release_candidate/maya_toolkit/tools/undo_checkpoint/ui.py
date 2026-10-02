"""Original complete Qt table/name/create/restore/latest/double-click/clear panel."""
from maya import cmds
import maya.OpenMayaUI as omui
try:
    from PySide6 import QtWidgets,QtCore,QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets,QtCore,QtGui
    from shiboken2 import wrapInstance
from .manager import manager as _GLOBAL_MANAGER
_CURRENT_UI_INSTANCE=None
def get_maya_main_window():
    """获取 Maya 主窗口的 QWidget 指针"""
    ptr = omui.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapInstance(int(ptr), QtWidgets.QWidget)
    return None

class UndoCheckpointUI(QtWidgets.QDialog):
    WINDOW_TITLE = "Maya 场景记录点与撤销恢复工具"
    WINDOW_NAME = "MayaUndoCheckpointWindow"

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(UndoCheckpointUI, self).__init__(parent)

        self.manager = _GLOBAL_MANAGER
        self.setObjectName(self.WINDOW_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(460, 420)
        self.resize(500, 480)

        # 确保独立窗口
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)

        self.setup_ui()
        self.apply_styles()
        self.refresh_table()

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # 1. 顶部标题与提示
        header_layout = QtWidgets.QHBoxLayout()
        icon_label = QtWidgets.QLabel("📍")
        icon_label.setStyleSheet("font-size: 22px;")

        title_box = QtWidgets.QVBoxLayout()
        title_label = QtWidgets.QLabel("Maya 操作记录点管理器")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF;")
        sub_label = QtWidgets.QLabel("在任意步骤生成记录点，随时一键批量 Undo 回退")
        sub_label.setStyleSheet("font-size: 11px; color: #A0A0A0;")
        title_box.addWidget(title_label)
        title_box.addWidget(sub_label)

        header_layout.addWidget(icon_label)
        header_layout.addLayout(title_box)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # 2. 生成记录点控制区
        create_group = QtWidgets.QGroupBox("创建记录点")
        create_layout = QtWidgets.QHBoxLayout(create_group)
        create_layout.setContentsMargins(8, 8, 8, 8)
        create_layout.setSpacing(6)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("输入记录点名称 (留空使用默认时间)...")
        self.name_edit.returnPressed.connect(self.on_create_checkpoint)

        self.create_btn = QtWidgets.QPushButton("➕ 生成记录点")
        self.create_btn.setFixedHeight(30)
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D68C4;
                color: #FFFFFF;
                font-weight: bold;
                border-radius: 4px;
                padding: 4px 12px;
            }
            QPushButton:hover { background-color: #3A7DE8; }
            QPushButton:pressed { background-color: #1E4E96; }
        """)
        self.create_btn.clicked.connect(self.on_create_checkpoint)

        create_layout.addWidget(self.name_edit)
        create_layout.addWidget(self.create_btn)
        main_layout.addWidget(create_group)

        # 3. 记录点列表表格
        table_group = QtWidgets.QGroupBox("历史记录点列表")
        table_layout = QtWidgets.QVBoxLayout(table_group)
        table_layout.setContentsMargins(8, 8, 8, 8)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["记录点名称", "创建时间", "状态"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.on_table_double_clicked)
        table_layout.addWidget(self.table)

        main_layout.addWidget(table_group)

        # 4. 恢复与操作按钮区
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(8)

        self.restore_btn = QtWidgets.QPushButton("⏪ 恢复到所选记录点")
        self.restore_btn.setFixedHeight(34)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A9D57;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #34BD69; }
            QPushButton:pressed { background-color: #1E7540; }
        """)
        self.restore_btn.clicked.connect(self.on_restore_selected)

        self.restore_latest_btn = QtWidgets.QPushButton("⏮️ 恢复到最新记录点")
        self.restore_latest_btn.setFixedHeight(34)
        self.restore_latest_btn.setStyleSheet("""
            QPushButton {
                background-color: #D97724;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #F08B32; }
            QPushButton:pressed { background-color: #AA5813; }
        """)
        self.restore_latest_btn.clicked.connect(self.on_restore_latest)

        self.clear_btn = QtWidgets.QPushButton("🗑️ 清空列表")
        self.clear_btn.setFixedHeight(34)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A4A4A;
                color: #DDDDDD;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #5A5A5A; }
            QPushButton:pressed { background-color: #333333; }
        """)
        self.clear_btn.clicked.connect(self.on_clear)

        btn_layout.addWidget(self.restore_btn)
        btn_layout.addWidget(self.restore_latest_btn)
        btn_layout.addWidget(self.clear_btn)
        main_layout.addLayout(btn_layout)

        # 5. 底部状态栏
        self.status_label = QtWidgets.QLabel("就绪。点击上方按钮生成记录点。")
        self.status_label.setStyleSheet("color: #8E8E8E; font-size: 11px;")
        main_layout.addWidget(self.status_label)

    def apply_styles(self):
        """深色系 Maya 风格样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2B2B;
                color: #E0E0E0;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QGroupBox {
                border: 1px solid #3E3E3E;
                border-radius: 4px;
                margin-top: 10px;
                font-weight: bold;
                color: #C8C8C8;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 4px;
            }
            QLineEdit {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border: 1px solid #444444;
                border-radius: 3px;
                padding: 4px 8px;
            }
            QLineEdit:focus {
                border: 1px solid #5285D1;
            }
            QTableWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                gridline-color: #333333;
                border: 1px solid #3E3E3E;
                border-radius: 3px;
                selection-background-color: #2D68C4;
                selection-color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                color: #BBBBBB;
                padding: 4px;
                border: 1px solid #3E3E3E;
                font-weight: bold;
            }
        """)

    def refresh_table(self):
        """刷新记录点表格"""
        self.table.setRowCount(0)
        for row, cp in enumerate(self.manager.checkpoints):
            self.table.insertRow(row)

            # 名字
            name_item = QtWidgets.QTableWidgetItem(cp.name)
            name_item.setData(QtCore.Qt.UserRole, cp.id)
            self.table.setItem(row, 0, name_item)

            # 时间
            time_item = QtWidgets.QTableWidgetItem(cp.time_str)
            time_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.table.setItem(row, 1, time_item)

            # 状态
            status_item = QtWidgets.QTableWidgetItem(cp.status)
            status_item.setTextAlignment(QtCore.Qt.AlignCenter)
            if "有效" in cp.status:
                status_item.setForeground(QtGui.QColor("#4EC9B0"))
            elif "已回退" in cp.status:
                status_item.setForeground(QtGui.QColor("#CE9178"))
            else:
                status_item.setForeground(QtGui.QColor("#808080"))
            self.table.setItem(row, 2, status_item)

        # 默认高亮最后一行
        if self.manager.checkpoints:
            last_row = len(self.manager.checkpoints) - 1
            self.table.selectRow(last_row)

    def on_create_checkpoint(self):
        """点击生成记录点"""
        name = self.name_edit.text()
        item = self.manager.create_checkpoint(name)
        if item:
            self.name_edit.clear()
            self.refresh_table()
            self.status_label.setText("✅ 已生成记录点 [{}] ({})".format(item.name, item.time_str))

            # Maya 视口提示
            try:
                cmds.inViewMessage(
                    amg="<hl>已生成记录点:</hl> {}".format(item.name),
                    pos='topCenter',
                    fade=True,
                    fst=2000
                )
            except Exception:
                pass

    def on_restore_selected(self):
        """恢复到选中的记录点"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QtWidgets.QMessageBox.information(self, "提示", "请先在列表中选择要回退的记录点。")
            return

        row = selected_rows[0].row()
        item_name = self.table.item(row, 0).text()
        cp_id = self.table.item(row, 0).data(QtCore.Qt.UserRole)

        reply = QtWidgets.QMessageBox.question(
            self,
            "确认恢复记录点",
            "确定要通过 Undo 回退到记录点 [{}] 吗？\n该记录点之后的所有操作都将被撤销。".format(item_name),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        success, count, msg = self.manager.restore_to_checkpoint(cp_id)
        self.refresh_table()

        if success:
            self.status_label.setText("⏪ " + msg)
            try:
                cmds.inViewMessage(
                    amg="<hl>已回退至记录点:</hl> {} (撤销了 {} 步)".format(item_name, count),
                    pos='topCenter',
                    fade=True,
                    fst=2500
                )
            except Exception:
                pass
        else:
            self.status_label.setText("❌ " + msg)
            QtWidgets.QMessageBox.warning(self, "回退警告", msg)

    def on_restore_latest(self):
        """恢复到最新的记录点"""
        active_cp = self.manager.get_latest_active_checkpoint()
        if not active_cp:
            QtWidgets.QMessageBox.information(self, "提示", "当前没有有效的记录点。")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "确认恢复最新记录点",
            "确定要回退到最新记录点 [{}] 吗？".format(active_cp.name),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.Yes
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        success, count, msg = self.manager.restore_to_checkpoint(active_cp.id)
        self.refresh_table()

        if success:
            self.status_label.setText("⏪ " + msg)
            try:
                cmds.inViewMessage(
                    amg="<hl>已回退至记录点:</hl> {} (撤销了 {} 步)".format(active_cp.name, count),
                    pos='topCenter',
                    fade=True,
                    fst=2500
                )
            except Exception:
                pass
        else:
            self.status_label.setText("❌ " + msg)
            QtWidgets.QMessageBox.warning(self, "回退警告", msg)

    def on_table_double_clicked(self, item):
        """双击表格行直接触发恢复"""
        self.on_restore_selected()

    def on_clear(self):
        """清空列表"""
        if not self.manager.checkpoints:
            return
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有记录点列表吗？（这不会影响场景中的已有对象）",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.manager.clear()
            self.refresh_table()
            self.status_label.setText("已清空记录点列表。")

def show():
    """打开或激活 UI 窗口"""
    global _CURRENT_UI_INSTANCE

    # 尝试关闭已打开的旧窗口
    if _CURRENT_UI_INSTANCE is not None:
        try:
            _CURRENT_UI_INSTANCE.close()
            _CURRENT_UI_INSTANCE.deleteLater()
        except Exception:
            pass

    if cmds.about(batch=True):
        raise RuntimeError("Interactive Maya required")

    # 创建并展示新窗口
    _CURRENT_UI_INSTANCE = UndoCheckpointUI()
    _CURRENT_UI_INSTANCE.show()
    return _CURRENT_UI_INSTANCE
