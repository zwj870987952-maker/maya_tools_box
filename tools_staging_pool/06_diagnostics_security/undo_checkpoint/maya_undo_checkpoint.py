# -*- coding: utf-8 -*-
"""
Maya Undo Checkpoint Tool (Maya 场景记录点与撤销恢复工具)
=====================================================
功能：
1. 在 Maya 操作流中生成一个“记录点 (Checkpoint)”。
2. 用户在场景中进行任意建模、变换、属性修改等操作。
3. 点击“恢复记录”后，工具会自动批量执行 Maya Undo，精确回退到该记录点的场景状态。

兼容性：Maya 2020 ~ 2026+ (PySide2 / PySide6, Python 2 / Python 3)
"""

from __future__ import print_function, absolute_import
import sys
import os
import time
import uuid

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui

# -----------------------------------------------------------------------------
# Qt 兼容层 (PySide2 / PySide6)
# -----------------------------------------------------------------------------
try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
    IS_PYSIDE6 = True
except ImportError:
    try:
        from PySide2 import QtWidgets, QtCore, QtGui
        from shiboken2 import wrapInstance
        IS_PYSIDE6 = False
    except ImportError:
        from PySide import QtWidgets, QtCore, QtGui
        from shiboken import wrapInstance
        IS_PYSIDE6 = False


# -----------------------------------------------------------------------------
# MPxCommand: Undo Checkpoint Marker
# -----------------------------------------------------------------------------
PLUGIN_CMD_NAME = "mayaUndoCheckpointMarker"

class CheckpointState(object):
    """全局状态追踪器，用于捕获 Undo 触发的标记"""
    last_undone_id = None
    undone_history = set()


def maya_useNewAPI():
    pass


class MayaUndoCheckpointMarkerCmd(om.MPxCommand):
    """
    用于插入 Maya Undo 队列的标记命令。
    当 Maya Undo 栈回退到此命令时，会触发 undoIt() 并通知管理器。
    """
    kIdFlag = "-id"
    kIdFlagLong = "-identifier"
    kNameFlag = "-n"
    kNameFlagLong = "-name"

    def __init__(self):
        super(MayaUndoCheckpointMarkerCmd, self).__init__()
        self.identifier = ""
        self.name = ""

    def doIt(self, args):
        try:
            argData = om.MArgDatabase(self.syntax(), args)
            if argData.isFlagSet(self.kIdFlag):
                self.identifier = argData.flagArgumentString(self.kIdFlag, 0)
            else:
                self.identifier = str(uuid.uuid4())

            if argData.isFlagSet(self.kNameFlag):
                self.name = argData.flagArgumentString(self.kNameFlag, 0)
            else:
                self.name = "Checkpoint"
        except Exception as e:
            om.MGlobal.displayError("[UndoCheckpoint] 参数解析失败: {}".format(e))

    def redoIt(self):
        pass

    def undoIt(self):
        # 当此标记被 Maya Undo 时调用
        CheckpointState.last_undone_id = self.identifier
        CheckpointState.undone_history.add(self.identifier)

    def isUndoable(self):
        return True

    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def syntaxCreator(cls):
        syntax = om.MSyntax()
        syntax.addFlag(cls.kIdFlag, cls.kIdFlagLong, om.MSyntax.kString)
        syntax.addFlag(cls.kNameFlag, cls.kNameFlagLong, om.MSyntax.kString)
        return syntax


def register_checkpoint_command():
    """注册 Maya 自定义 Undo 标记命令"""
    if hasattr(cmds, PLUGIN_CMD_NAME):
        return True

    import tempfile
    plugin_code = '''# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om
import sys

kPluginCmdName = "{cmd_name}"

def maya_useNewAPI():
    pass

class MayaUndoCheckpointMarkerCmd(om.MPxCommand):
    kIdFlag = "-id"
    kIdFlagLong = "-identifier"
    kNameFlag = "-n"
    kNameFlagLong = "-name"

    def __init__(self):
        super(MayaUndoCheckpointMarkerCmd, self).__init__()
        self.identifier = ""
        self.name = ""

    def doIt(self, args):
        try:
            argData = om.MArgDatabase(self.syntax(), args)
            if argData.isFlagSet(self.kIdFlag):
                self.identifier = argData.flagArgumentString(self.kIdFlag, 0)
            if argData.isFlagSet(self.kNameFlag):
                self.name = argData.flagArgumentString(self.kNameFlag, 0)
        except Exception:
            pass

    def redoIt(self):
        pass

    def undoIt(self):
        try:
            import maya_undo_checkpoint
            maya_undo_checkpoint.CheckpointState.last_undone_id = self.identifier
            maya_undo_checkpoint.CheckpointState.undone_history.add(self.identifier)
        except Exception:
            pass

    def isUndoable(self):
        return True

    @classmethod
    def creator(cls):
        return cls()

    @classmethod
    def syntaxCreator(cls):
        syntax = om.MSyntax()
        syntax.addFlag(cls.kIdFlag, cls.kIdFlagLong, om.MSyntax.kString)
        syntax.addFlag(cls.kNameFlag, cls.kNameFlagLong, om.MSyntax.kString)
        return syntax

def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin, "UndoCheckpoint", "1.0", "Any")
    try:
        pluginFn.registerCommand(kPluginCmdName, MayaUndoCheckpointMarkerCmd.creator, MayaUndoCheckpointMarkerCmd.syntaxCreator)
    except Exception as e:
        sys.stderr.write("Failed to register command: %s\\n" % e)
        raise

def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(kPluginCmdName)
    except Exception as e:
        sys.stderr.write("Failed to deregister command: %s\\n" % e)
        raise
'''.format(cmd_name=PLUGIN_CMD_NAME)

    temp_dir = tempfile.gettempdir()
    plugin_path = os.path.join(temp_dir, "maya_undo_marker_plugin.py").replace("\\", "/")
    with open(plugin_path, "w") as f:
        f.write(plugin_code)

    if not cmds.pluginInfo(plugin_path, q=True, loaded=True):
        cmds.loadPlugin(plugin_path)
    return True


# -----------------------------------------------------------------------------
# 记录点管理器 (Checkpoint Manager)
# -----------------------------------------------------------------------------
class CheckpointItem(object):
    def __init__(self, cp_id, name, created_time=None):
        self.id = cp_id
        self.name = name
        self.time_str = created_time or time.strftime("%H:%M:%S", time.localtime())
        self.status = "有效 (Active)"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "time": self.time_str,
            "status": self.status
        }


class CheckpointManager(object):
    def __init__(self):
        self.checkpoints = []  # List of CheckpointItem (最新在最后)

    def create_checkpoint(self, name=None, overwrite=False):
        """
        在 Maya 中生成一个记录点
        :param name: 记录点名称
        :param overwrite: 是否覆盖已有记录点（清空之前的记录点，仅保留此最新唯一记录点）
        """
        register_checkpoint_command()

        if not cmds.undoInfo(q=True, state=True):
            cmds.warning("Maya 的 Undo 功能当前处于关闭状态，请先开启 Undo！")
            return None

        if overwrite:
            # 清理旧记录
            self.checkpoints = []
            CheckpointState.last_undone_id = None
            CheckpointState.undone_history.clear()

        cp_id = "cp_" + uuid.uuid4().hex[:8]
        if not name or not name.strip():
            name = "唯一记录点" if overwrite else "记录点_{}".format(time.strftime("%H%M%S"))
        else:
            name = name.strip()

        # 调用自定义命令，将标记压入 Maya Undo 队列
        mel_cmd = '{} -id "{}" -name "{}";'.format(PLUGIN_CMD_NAME, cp_id, name)
        mel.eval(mel_cmd)

        item = CheckpointItem(cp_id, name)
        self.checkpoints.append(item)
        return item

    def get_latest_active_checkpoint(self):
        """获取当前最新的有效记录点"""
        for cp in reversed(self.checkpoints):
            if "有效" in cp.status and cp.id not in CheckpointState.undone_history:
                return cp
        return None

    def restore_to_checkpoint(self, target_id=None, max_steps=5000):
        """
        批量 Undo 回退到指定的记录点（若不指定 target_id 则回退到最新有效记录点）
        :param target_id: 目标记录点的 ID，留空则自动选取最新有效记录点
        :param max_steps: 最大撤销步数保护，防止死循环
        :return: (bool success, int undid_steps, str message)
        """
        if not cmds.undoInfo(q=True, state=True):
            return False, 0, "Undo 功能已被禁用。"

        if not target_id:
            latest = self.get_latest_active_checkpoint()
            if not latest:
                return False, 0, "当前没有可恢复的有效记录点。"
            target_id = latest.id

        # 重置当前状态
        CheckpointState.last_undone_id = None
        undone_count = 0
        target_reached = False

        # 检查 target_id 是否已被撤销过
        if target_id in CheckpointState.undone_history:
            return False, 0, "该记录点在之前的操作中已被撤销或失效。"

        # 暂停视口刷新以加速批量 Undo
        cmds.refresh(suspend=True)

        try:
            while undone_count < max_steps:
                # 检查 Undo 队列是否已空
                if cmds.undoInfo(q=True, undoQueueEmpty=True):
                    break

                # 执行一步 Undo
                cmds.undo()
                undone_count += 1

                # 检查是否撤销到了目标记录点
                if CheckpointState.last_undone_id == target_id:
                    target_reached = True
                    break

        except Exception as e:
            cmds.refresh(suspend=False)
            return False, undone_count, "撤销过程中发生异常: {}".format(e)

        finally:
            cmds.refresh(suspend=False)
            cmds.refresh()

        if target_reached:
            # 更新记录点状态
            reached_idx = -1
            for idx, cp in enumerate(self.checkpoints):
                if cp.id == target_id:
                    cp.status = "已回退至此"
                    reached_idx = idx
                elif reached_idx != -1:
                    # 在目标点之后的记录点都已失效
                    cp.status = "已失效 (Undone)"

            msg = "成功回退 {} 步操作，回到记录点 [{}]！".format(
                undone_count,
                self.get_checkpoint_name(target_id)
            )
            return True, undone_count, msg
        else:
            return False, undone_count, "已撤销 {} 步，但未找到目标记录点（可能已超出撤销栈上限）。".format(undone_count)

    def get_checkpoint_name(self, cp_id):
        for cp in self.checkpoints:
            if cp.id == cp_id:
                return cp.name
        return cp_id

    def clear(self):
        self.checkpoints = []
        CheckpointState.last_undone_id = None
        CheckpointState.undone_history.clear()


# 全局单例管理器
_GLOBAL_MANAGER = CheckpointManager()


# -----------------------------------------------------------------------------
# 独立脚本调用的 API 接口 (供 3 个独立脚本调用)
# -----------------------------------------------------------------------------
def notify_ui_refresh():
    """如果 UI 窗口处于打开状态，同步刷新表格"""
    global _CURRENT_UI_INSTANCE
    if _CURRENT_UI_INSTANCE is not None:
        try:
            _CURRENT_UI_INSTANCE.refresh_table()
        except Exception:
            pass


def create_checkpoint_standalone(name="唯一记录点", overwrite=True):
    """
    独立执行：生成记录点（默认覆盖已有记录点）
    """
    item = _GLOBAL_MANAGER.create_checkpoint(name=name, overwrite=overwrite)
    notify_ui_refresh()

    if item:
        msg = "已生成记录点: {} ({})".format(item.name, item.time_str)
        if overwrite:
            msg += " [已覆盖历史记录]"
        try:
            cmds.inViewMessage(
                amg="<hl color='00FF7F'>【记录点】</hl> {}".format(msg),
                pos='topCenter',
                fade=True,
                fst=2000
            )
        except Exception:
            pass
        print("[UndoCheckpoint] " + msg)
        return True
    return False


def restore_checkpoint_standalone():
    """
    独立执行：恢复到最新记录点
    """
    success, count, msg = _GLOBAL_MANAGER.restore_to_checkpoint()
    notify_ui_refresh()

    if success:
        try:
            cmds.inViewMessage(
                amg="<hl color='00E5FF'>【恢复成功】</hl> {}".format(msg),
                pos='topCenter',
                fade=True,
                fst=2500
            )
        except Exception:
            pass
        print("[UndoCheckpoint] " + msg)
        return True
    else:
        try:
            cmds.inViewMessage(
                amg="<hl color='FF5555'>【恢复失败】</hl> {}".format(msg),
                pos='topCenter',
                fade=True,
                fst=2500
            )
        except Exception:
            pass
        cmds.warning("[UndoCheckpoint] " + msg)
        return False


def clear_checkpoint_standalone():
    """
    独立执行：清空所有记录点
    """
    _GLOBAL_MANAGER.clear()
    notify_ui_refresh()

    msg = "所有记录点已清空。"
    try:
        cmds.inViewMessage(
            amg="<hl color='FFA500'>【记录点】</hl> {}".format(msg),
            pos='topCenter',
            fade=True,
            fst=2000
        )
    except Exception:
        pass
    print("[UndoCheckpoint] " + msg)
    return True


# -----------------------------------------------------------------------------
# PySide GUI 界面
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# 启动入口函数
# -----------------------------------------------------------------------------
_CURRENT_UI_INSTANCE = None

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

    # 注册命令
    register_checkpoint_command()

    # 创建并展示新窗口
    _CURRENT_UI_INSTANCE = UndoCheckpointUI()
    _CURRENT_UI_INSTANCE.show()
    return _CURRENT_UI_INSTANCE


if __name__ == "__main__":
    show()
