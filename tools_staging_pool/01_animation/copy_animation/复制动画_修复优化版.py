# -*- coding: utf-8 -*-
"""Maya 2020–2025 通用动画复制/对齐工具。

兼容环境：
- Maya 2020–2022：Python 2.7 / PySide2
- Maya 2022–2024：Python 3 / PySide2
- Maya 2025：Python 3 / PySide6

用法：
1. 依次选择源对象和目标对象，点击“录入”。
2. 点击列表项左侧的彩色圆点，或使用右键菜单设置各通道模式。
3. “帧对齐”会自动创建辅助定位器；也可以提前点击“生成/更新定位器”。
4. 点击“开始复制/对齐”。
"""

from __future__ import unicode_literals

import maya.OpenMayaUI as omui
import maya.cmds as cmds

import io
import json
import re
import sys


try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from shiboken6 import wrapInstance
    USING_QT6 = True
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance
    USING_QT6 = False


try:
    TEXT_TYPE = unicode
except NameError:
    TEXT_TYPE = str


if USING_QT6:
    QT_STATE_SELECTED = QtWidgets.QStyle.StateFlag.State_Selected
    QT_NO_PEN = QtCore.Qt.PenStyle.NoPen
    QT_ALIGN_VCENTER = QtCore.Qt.AlignmentFlag.AlignVCenter
    QT_ALIGN_LEFT = QtCore.Qt.AlignmentFlag.AlignLeft
    QT_EXTENDED_SELECTION = (
        QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
    )
    QT_INTERNAL_MOVE = QtWidgets.QAbstractItemView.DragDropMode.InternalMove
    QT_DIALOG_OK = QtWidgets.QDialogButtonBox.StandardButton.Ok
    QT_DIALOG_CANCEL = QtWidgets.QDialogButtonBox.StandardButton.Cancel
    QT_DELETE_ON_CLOSE = QtCore.Qt.WidgetAttribute.WA_DeleteOnClose
    QT_CUSTOM_CONTEXT_MENU = QtCore.Qt.ContextMenuPolicy.CustomContextMenu
    QT_DIALOG_ACCEPTED = QtWidgets.QDialog.DialogCode.Accepted
    QT_WINDOW = QtCore.Qt.WindowType.Window
else:
    QT_STATE_SELECTED = QtWidgets.QStyle.State_Selected
    QT_NO_PEN = QtCore.Qt.NoPen
    QT_ALIGN_VCENTER = QtCore.Qt.AlignVCenter
    QT_ALIGN_LEFT = QtCore.Qt.AlignLeft
    QT_EXTENDED_SELECTION = QtWidgets.QAbstractItemView.ExtendedSelection
    QT_INTERNAL_MOVE = QtWidgets.QAbstractItemView.InternalMove
    QT_DIALOG_OK = QtWidgets.QDialogButtonBox.Ok
    QT_DIALOG_CANCEL = QtWidgets.QDialogButtonBox.Cancel
    QT_DELETE_ON_CLOSE = QtCore.Qt.WA_DeleteOnClose
    QT_CUSTOM_CONTEXT_MENU = QtCore.Qt.CustomContextMenu
    QT_DIALOG_ACCEPTED = QtWidgets.QDialog.Accepted
    QT_WINDOW = QtCore.Qt.Window


WINDOW_OBJECT_NAME = "copyAnimationAutoAlignWindow"
LOCATOR_GROUP_NAME = "CopyAnimation_Locators_GRP"
SOURCE_SET_NAME = "CopyAnimation_Source_SET"
TARGET_SET_NAME = "CopyAnimation_Target_SET"
LOCATOR_SET_NAME = "CopyAnimation_Locator_SET"
CONSTRAINT_SET_NAME = "CopyAnimation_Constraint_SET"

CHANNELS = ("translate", "rotate", "scale", "other")
TRANSFORM_CHANNELS = ("translate", "rotate", "scale")
ALL_MODES = ("frame", "constraint", "numeric", "none")
OTHER_MODES = ("numeric", "none")

MODE_COLORS = {
    "frame": QtGui.QColor("#E85D5D"),
    "constraint": QtGui.QColor("#52B788"),
    "numeric": QtGui.QColor("#F4D35E"),
    "none": QtGui.QColor("#777777"),
}

MODE_LABELS = {
    "frame": "帧对齐",
    "constraint": "约束",
    "numeric": "仅数值",
    "none": "无",
}

CHANNEL_LABELS = {
    "translate": "位移",
    "rotate": "旋转",
    "scale": "缩放",
    "other": "其他属性",
}


def _qt_exec(widget, *args):
    """Call Qt's exec/exec_ method in both PySide2 and PySide6."""
    method = getattr(widget, "exec", None)
    if method is None:
        method = getattr(widget, "exec_")
    return method(*args)


def _pointer_value(pointer):
    if sys.version_info[0] < 3:
        return long(pointer)
    return int(pointer)


def _warning(message):
    cmds.warning("[动画复制工具] {}".format(message))


def _object_exists(node):
    return bool(node and cmds.objExists(node))


def _long_name(node):
    matches = cmds.ls(node, long=True) or []
    return matches[0] if matches else node


def _safe_node_token(node):
    short_name = node.rsplit("|", 1)[-1].replace(":", "_")
    token = re.sub(r"[^0-9A-Za-z_]+", "_", short_name).strip("_")
    return token or "Object"


def _parse_pair(text):
    if " , " not in text:
        raise ValueError("列表项必须使用“源对象 , 目标对象”的格式")
    source, target = [part.strip() for part in text.split(" , ", 1)]
    if not source or not target:
        raise ValueError("源对象或目标对象为空")
    return source, target


def _set_members(set_name, members):
    members = [node for node in members if _object_exists(node)]
    if cmds.objExists(set_name):
        if cmds.nodeType(set_name) != "objectSet":
            _warning("无法更新集合 {}：同名节点不是 objectSet。".format(set_name))
            return
        cmds.sets(clear=set_name)
        if members:
            cmds.sets(members, add=set_name)
    elif members:
        cmds.sets(members, name=set_name)


class UndoChunk(object):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        cmds.undoInfo(openChunk=True, chunkName=self.name)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        cmds.undoInfo(closeChunk=True)
        return False


class CustomListWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, text, parent=None):
        super(CustomListWidgetItem, self).__init__(text, parent)
        self.modes = {
            "translate": "frame",
            "rotate": "frame",
            "scale": "frame",
            "other": "none",
        }
        self.locator_data = {}
        self.constraint_nodes = []

    def set_mode(self, channel, mode):
        available_modes = OTHER_MODES if channel == "other" else ALL_MODES
        if channel not in CHANNELS or mode not in available_modes:
            raise ValueError("无效模式：{} / {}".format(channel, mode))
        self.modes[channel] = mode

    def toggle_mode(self, channel):
        available_modes = OTHER_MODES if channel == "other" else ALL_MODES
        current_mode = self.modes.get(channel, available_modes[0])
        try:
            next_index = (available_modes.index(current_mode) + 1) % len(available_modes)
        except ValueError:
            next_index = 0
        self.set_mode(channel, available_modes[next_index])


class CustomItemDelegate(QtWidgets.QStyledItemDelegate):
    FLAG_SIZE = 11
    FLAG_SPACING = 6
    LEFT_MARGIN = 7

    def paint(self, painter, option, index):
        item = self.parent().itemFromIndex(index)
        if not isinstance(item, CustomListWidgetItem):
            super(CustomItemDelegate, self).paint(painter, option, index)
            return

        painter.save()
        if option.state & QT_STATE_SELECTED:
            painter.fillRect(option.rect, QtGui.QColor("#505053"))

        center_y = option.rect.top() + option.rect.height() // 2
        for index_value, channel in enumerate(CHANNELS):
            mode = item.modes.get(channel, "none")
            flag_rect = self._flag_rect(option.rect, center_y, index_value)
            painter.setPen(QT_NO_PEN)
            painter.setBrush(MODE_COLORS.get(mode, MODE_COLORS["none"]))
            painter.drawEllipse(flag_rect)

        flags_width = len(CHANNELS) * self.FLAG_SIZE
        flags_width += (len(CHANNELS) - 1) * self.FLAG_SPACING
        text_left = self.LEFT_MARGIN + flags_width + 12
        painter.setPen(QtGui.QColor("#FFFFFF"))
        painter.drawText(
            option.rect.adjusted(text_left, 0, -5, 0),
            QT_ALIGN_VCENTER | QT_ALIGN_LEFT,
            item.text(),
        )
        painter.restore()

    def _flag_rect(self, row_rect, center_y, index_value):
        left = row_rect.left() + self.LEFT_MARGIN
        left += index_value * (self.FLAG_SIZE + self.FLAG_SPACING)
        top = center_y - self.FLAG_SIZE // 2
        return QtCore.QRect(left, top, self.FLAG_SIZE, self.FLAG_SIZE)

    def channel_at_position(self, item, position):
        row_rect = self.parent().visualItemRect(item)
        center_y = row_rect.top() + row_rect.height() // 2
        for index_value, channel in enumerate(CHANNELS):
            if self._flag_rect(row_rect, center_y, index_value).contains(position):
                return channel
        return None


class CustomListWidget(QtWidgets.QListWidget):
    modesChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.setItemDelegate(CustomItemDelegate(self))
        self.setSelectionMode(QT_EXTENDED_SELECTION)
        self.setDragDropMode(QT_INTERNAL_MOVE)
        self.setAlternatingRowColors(True)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, CustomListWidgetItem):
            channel = self.itemDelegate().channel_at_position(item, event.pos())
            if channel:
                if not item.isSelected():
                    self.clearSelection()
                    item.setSelected(True)
                    self.setCurrentItem(item)
                for selected_item in self.selectedItems():
                    if isinstance(selected_item, CustomListWidgetItem):
                        selected_item.toggle_mode(channel)
                self.viewport().update()
                self.modesChanged.emit()
                return
        super(CustomListWidget, self).mousePressEvent(event)


class EditDialog(QtWidgets.QDialog):
    def __init__(self, items_text, parent=None):
        super(EditDialog, self).__init__(parent)
        self.setWindowTitle("编辑对象列表")
        self.resize(520, 340)

        layout = QtWidgets.QVBoxLayout(self)
        description = QtWidgets.QLabel("每行格式：源对象 , 目标对象")
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setPlainText(items_text)
        button_box = QtWidgets.QDialogButtonBox(
            QT_DIALOG_OK | QT_DIALOG_CANCEL
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(description)
        layout.addWidget(self.text_edit)
        layout.addWidget(button_box)

    def edited_text(self):
        return self.text_edit.toPlainText()


class AutoAlignUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AutoAlignUI, self).__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle("动画复制与自动对齐（Maya 2020–2025）")
        self.resize(540, 620)
        self.setAttribute(QT_DELETE_ON_CLOSE, True)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2D2D30;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #3E3E42;
                border: 1px solid #55555A;
                padding: 6px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505053;
            }
            QPushButton:pressed {
                background-color: #252526;
            }
            QListWidget {
                background-color: #363638;
                border: 1px solid #55555A;
                alternate-background-color: #323234;
            }
            QListWidget::item {
                min-height: 24px;
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #505053;
            }
            QLabel#hintLabel {
                color: #B8B8B8;
            }
            """
        )

        main_layout = QtWidgets.QVBoxLayout(self)

        input_layout = QtWidgets.QHBoxLayout()
        self.input_button = QtWidgets.QPushButton("录入所选对象")
        self.clear_button = QtWidgets.QPushButton("清空列表")
        self.edit_button = QtWidgets.QPushButton("编辑列表")
        input_layout.addWidget(self.input_button)
        input_layout.addWidget(self.clear_button)
        input_layout.addWidget(self.edit_button)

        save_load_layout = QtWidgets.QHBoxLayout()
        self.save_button = QtWidgets.QPushButton("保存配置")
        self.load_button = QtWidgets.QPushButton("读取配置")
        save_load_layout.addWidget(self.save_button)
        save_load_layout.addWidget(self.load_button)

        self.record_list = CustomListWidget(self)
        self.record_list.setContextMenuPolicy(QT_CUSTOM_CONTEXT_MENU)

        hint_label = QtWidgets.QLabel(
            "圆点顺序：位移 / 旋转 / 缩放 / 其他　"
            "红=帧对齐　绿=约束　黄=仅数值　灰=无"
        )
        hint_label.setObjectName("hintLabel")
        hint_label.setWordWrap(True)

        self.create_locators_button = QtWidgets.QPushButton("生成/更新定位器")
        self.execute_button = QtWidgets.QPushButton("开始复制/对齐")
        self.execute_button.setMinimumHeight(34)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(save_load_layout)
        main_layout.addWidget(hint_label)
        main_layout.addWidget(self.record_list, 1)
        main_layout.addWidget(self.create_locators_button)
        main_layout.addWidget(self.execute_button)

    def _connect_signals(self):
        self.input_button.clicked.connect(self.add_selection)
        self.clear_button.clicked.connect(self.clear_list)
        self.edit_button.clicked.connect(self.edit_list)
        self.save_button.clicked.connect(self.save_data)
        self.load_button.clicked.connect(self.load_data)
        self.create_locators_button.clicked.connect(self.create_locators_for_all)
        self.execute_button.clicked.connect(self.execute_alignment)
        self.record_list.itemDoubleClicked.connect(self.select_objects)
        self.record_list.customContextMenuRequested.connect(self.show_context_menu)

    def _items(self):
        return [
            self.record_list.item(index)
            for index in range(self.record_list.count())
        ]

    def _items_to_process(self):
        selected_items = self.record_list.selectedItems()
        return selected_items if selected_items else self._items()

    def add_selection(self):
        selected_objects = cmds.ls(selection=True, long=True) or []
        if len(selected_objects) != 2:
            cmds.confirmDialog(
                title="选择错误",
                message="请依次选择一个源对象和一个目标对象。",
                button=["确定"],
            )
            return

        source, target = selected_objects
        if source == target:
            cmds.confirmDialog(
                title="选择错误",
                message="源对象和目标对象不能相同。",
                button=["确定"],
            )
            return

        pair_text = "{} , {}".format(source, target)
        for item in self._items():
            if item.text() == pair_text:
                self.record_list.setCurrentItem(item)
                item.setSelected(True)
                _warning("该对象组合已经在列表中。")
                return

        self.record_list.addItem(CustomListWidgetItem(pair_text))

    def clear_list(self):
        self.record_list.clear()

    def edit_list(self):
        items_text = "\n".join(item.text() for item in self._items())
        dialog = EditDialog(items_text, self)
        if _qt_exec(dialog) != QT_DIALOG_ACCEPTED:
            return

        new_lines = [
            line.strip()
            for line in dialog.edited_text().splitlines()
            if line.strip()
        ]
        old_items = self._items()

        for index, line in enumerate(new_lines):
            try:
                _parse_pair(line)
            except ValueError as error:
                cmds.confirmDialog(
                    title="格式错误",
                    message="第 {} 行：{}".format(index + 1, error),
                    button=["确定"],
                )
                return

        self.record_list.clear()
        for index, line in enumerate(new_lines):
            if index < len(old_items):
                item = old_items[index]
                item.setText(line)
            else:
                item = CustomListWidgetItem(line)
            self.record_list.addItem(item)

    def _ensure_locator_group(self):
        if cmds.objExists(LOCATOR_GROUP_NAME):
            if cmds.nodeType(LOCATOR_GROUP_NAME) == "transform":
                return _long_name(LOCATOR_GROUP_NAME)
            raise RuntimeError("同名节点 {} 不是 transform。".format(LOCATOR_GROUP_NAME))
        return cmds.group(empty=True, world=True, name=LOCATOR_GROUP_NAME)

    def _delete_item_locators(self, item):
        locator_data = item.locator_data or {}
        follow_constraints = locator_data.get("follow_constraints", [])
        follow_constraints = [
            node for node in follow_constraints if _object_exists(node)
        ]
        if follow_constraints:
            cmds.delete(follow_constraints)
        source_locator = locator_data.get("source_locator")
        if _object_exists(source_locator):
            cmds.delete(source_locator)
        item.locator_data = {}

    def _create_locators_for_item(self, item, force_rebuild=False):
        source, target = _parse_pair(item.text())
        if not _object_exists(source):
            raise RuntimeError("源对象不存在：{}".format(source))
        if not _object_exists(target):
            raise RuntimeError("目标对象不存在：{}".format(target))

        existing = item.locator_data or {}
        source_locator = existing.get("source_locator")
        target_locator = existing.get("target_locator")
        if (
            not force_rebuild
            and existing.get("source") == source
            and existing.get("target") == target
            and _object_exists(source_locator)
            and _object_exists(target_locator)
        ):
            return source_locator, target_locator

        self._delete_item_locators(item)
        locator_group = self._ensure_locator_group()
        source_token = _safe_node_token(source)
        target_token = _safe_node_token(target)

        source_locator = cmds.spaceLocator(
            name="{}_CopyAnim_Source_LOC".format(source_token)
        )[0]
        target_locator = cmds.spaceLocator(
            name="{}_CopyAnim_Target_LOC".format(target_token)
        )[0]

        try:
            cmds.matchTransform(source_locator, source, pos=True, rot=True, scl=True)
            cmds.matchTransform(target_locator, target, pos=True, rot=True, scl=True)
            source_locator = cmds.parent(source_locator, locator_group)[0]
            target_locator = cmds.parent(target_locator, source_locator)[0]
            follow_constraints = cmds.parentConstraint(
                source, source_locator, maintainOffset=True
            ) or []
            follow_constraints.extend(
                cmds.scaleConstraint(
                    source, source_locator, maintainOffset=True
                ) or []
            )

            source_locator = _long_name(source_locator)
            target_locator = _long_name(target_locator)
            item.locator_data = {
                "source": source,
                "target": target,
                "source_locator": source_locator,
                "target_locator": target_locator,
                "follow_constraints": follow_constraints,
            }
            return source_locator, target_locator
        except Exception:
            if _object_exists(source_locator):
                cmds.delete(source_locator)
            elif _object_exists(target_locator):
                cmds.delete(target_locator)
            item.locator_data = {}
            raise

    def create_locators_for_all(self):
        items = self._items_to_process()
        if not items:
            _warning("列表为空。")
            return

        source_objects = []
        target_objects = []
        locator_nodes = []
        errors = []

        with UndoChunk("CopyAnimationCreateLocators"):
            for item in items:
                try:
                    source, target = _parse_pair(item.text())
                    source_locator, target_locator = self._create_locators_for_item(
                        item, force_rebuild=True
                    )
                    source_objects.append(source)
                    target_objects.append(target)
                    locator_nodes.extend([source_locator, target_locator])
                except Exception as error:
                    errors.append("{}：{}".format(item.text(), error))

            _set_members(SOURCE_SET_NAME, source_objects)
            _set_members(TARGET_SET_NAME, target_objects)
            _set_members(LOCATOR_SET_NAME, locator_nodes)

        if errors:
            _warning("部分定位器创建失败：\n{}".format("\n".join(errors)))
        else:
            _warning("已为 {} 组对象生成或更新定位器。".format(len(items)))

    def _delete_item_constraints(self, item):
        existing = [
            node for node in item.constraint_nodes if _object_exists(node)
        ]
        if existing:
            cmds.delete(existing)
        item.constraint_nodes = []

    def _create_channel_constraints(self, item, source, target):
        self._delete_item_constraints(item)
        constraint_nodes = []

        constraint_specs = (
            ("translate", cmds.pointConstraint),
            ("rotate", cmds.orientConstraint),
            ("scale", cmds.scaleConstraint),
        )
        for channel, command in constraint_specs:
            if item.modes.get(channel) != "constraint":
                continue
            try:
                nodes = command(source, target, maintainOffset=True) or []
                constraint_nodes.extend(nodes)
            except Exception as error:
                _warning("{} 的{}约束创建失败：{}".format(
                    target, CHANNEL_LABELS[channel], error
                ))

        item.constraint_nodes = constraint_nodes
        return constraint_nodes

    def execute_alignment(self):
        items = self._items_to_process()
        if not items:
            _warning("列表为空。")
            return

        start_time = int(cmds.playbackOptions(query=True, min=True))
        end_time = int(cmds.playbackOptions(query=True, max=True))
        original_time = cmds.currentTime(query=True)
        original_selection = cmds.ls(selection=True, long=True) or []
        constraint_nodes = []
        errors = []
        completed_count = 0

        with UndoChunk("CopyAnimationExecute"):
            try:
                for item in items:
                    try:
                        source, target = _parse_pair(item.text())
                        if not _object_exists(source):
                            raise RuntimeError("源对象不存在：{}".format(source))
                        if not _object_exists(target):
                            raise RuntimeError("目标对象不存在：{}".format(target))

                        constraint_nodes.extend(
                            self._create_channel_constraints(item, source, target)
                        )

                        needs_sampling = any(
                            item.modes.get(channel) in ("frame", "numeric")
                            for channel in CHANNELS
                        )
                        if needs_sampling:
                            target_locator = None
                            if any(
                                item.modes.get(channel) == "frame"
                                for channel in TRANSFORM_CHANNELS
                            ):
                                _, target_locator = self._create_locators_for_item(
                                    item, force_rebuild=False
                                )
                            self.apply_channel_modes(
                                source,
                                target,
                                target_locator,
                                item.modes,
                                start_time,
                                end_time,
                            )
                        completed_count += 1
                    except Exception as error:
                        errors.append("{}：{}".format(item.text(), error))
            finally:
                cmds.currentTime(original_time, edit=True)
                if original_selection:
                    existing_selection = [
                        node for node in original_selection if _object_exists(node)
                    ]
                    if existing_selection:
                        cmds.select(existing_selection, replace=True)
                    else:
                        cmds.select(clear=True)
                else:
                    cmds.select(clear=True)

            _set_members(CONSTRAINT_SET_NAME, constraint_nodes)

        if errors:
            _warning(
                "完成 {} 组，失败 {} 组：\n{}".format(
                    completed_count, len(errors), "\n".join(errors)
                )
            )
        else:
            _warning("动画复制/对齐完成，共处理 {} 组对象。".format(completed_count))

    def _attribute_has_key(self, node, attribute, frame):
        plug = "{}.{}".format(node, attribute)
        if not cmds.objExists(plug):
            return False
        return bool(
            cmds.keyframe(
                plug,
                query=True,
                time=(frame, frame),
                keyframeCount=True,
            )
        )

    def _channel_has_key(self, node, channel, frame):
        attributes = [
            "{}{}".format(channel, axis)
            for axis in ("X", "Y", "Z")
        ]
        return any(
            self._attribute_has_key(node, attribute, frame)
            for attribute in attributes
        )

    def _match_and_key(self, target, target_locator, channel, frame):
        if not _object_exists(target_locator):
            raise RuntimeError("辅助定位器不存在，请重新生成定位器。")

        cmds.currentTime(frame, edit=True)
        match_flags = {
            "translate": {"pos": True},
            "rotate": {"rot": True},
            "scale": {"scl": True},
        }
        cmds.matchTransform(target, target_locator, **match_flags[channel])
        cmds.setKeyframe(target, attribute=channel, time=frame)

    def apply_channel_modes(
        self,
        source,
        target,
        target_locator,
        modes,
        start_time,
        end_time,
    ):
        for frame in range(start_time, end_time + 1):
            for channel in TRANSFORM_CHANNELS:
                mode = modes.get(channel, "none")
                if mode == "frame":
                    if self._channel_has_key(source, channel, frame):
                        try:
                            self._match_and_key(
                                target, target_locator, channel, frame
                            )
                        except Exception as error:
                            _warning(
                                "{} 在第 {} 帧的{}对齐失败：{}".format(
                                    target,
                                    frame,
                                    CHANNEL_LABELS[channel],
                                    error,
                                )
                            )
                elif mode == "numeric":
                    self.copy_numeric_values(
                        source, target, channel, frame
                    )

            if modes.get("other") == "numeric":
                self.copy_numeric_values(source, target, "other", frame)

    def _numeric_attributes(self, node, channel):
        if channel == "other":
            attributes = cmds.listAttr(
                node, keyable=True, userDefined=True
            ) or []
        else:
            attributes = [
                "{}{}".format(channel, axis)
                for axis in ("X", "Y", "Z")
            ]
        return attributes

    def copy_numeric_values(self, source, target, channel, frame):
        for attribute in self._numeric_attributes(source, channel):
            source_plug = "{}.{}".format(source, attribute)
            target_plug = "{}.{}".format(target, attribute)

            if not cmds.objExists(target_plug):
                continue

            try:
                if not cmds.getAttr(target_plug, settable=True):
                    continue
                value = cmds.getAttr(source_plug, time=frame)
                if isinstance(value, (list, tuple)):
                    if len(value) == 1 and isinstance(value[0], (list, tuple)):
                        value = value[0]
                    if len(value) != 1:
                        _warning(
                            "跳过非标量属性 {}。".format(source_plug)
                        )
                        continue
                    value = value[0]
                if not isinstance(value, (int, float, bool)):
                    continue
                cmds.setKeyframe(
                    target,
                    time=frame,
                    attribute=attribute,
                    value=value,
                )
            except Exception as error:
                _warning(
                    "{} 在第 {} 帧复制失败：{}".format(
                        target_plug, frame, error
                    )
                )

    def save_data(self):
        file_path = cmds.fileDialog2(
            dialogStyle=2,
            fileMode=0,
            caption="保存动画复制配置",
            fileFilter="JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return

        items_data = []
        for item in self._items():
            items_data.append({
                "text": item.text(),
                "modes": dict(item.modes),
            })

        try:
            with io.open(file_path[0], "w", encoding="utf-8") as file_object:
                json.dump(
                    items_data,
                    file_object,
                    ensure_ascii=False,
                    indent=4,
                )
            cmds.confirmDialog(
                title="成功",
                message="配置已保存。",
                button=["确定"],
            )
        except Exception as error:
            cmds.confirmDialog(
                title="保存失败",
                message=TEXT_TYPE(error),
                button=["确定"],
            )

    def load_data(self):
        file_path = cmds.fileDialog2(
            dialogStyle=2,
            fileMode=1,
            caption="读取动画复制配置",
            fileFilter="JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return

        try:
            with io.open(
                file_path[0], "r", encoding="utf-8-sig"
            ) as file_object:
                items_data = json.load(file_object)
            if not isinstance(items_data, list):
                raise ValueError("配置根节点必须是列表。")

            loaded_items = []
            for index, item_data in enumerate(items_data):
                if not isinstance(item_data, dict):
                    raise ValueError("第 {} 项不是对象。".format(index + 1))
                text = item_data.get("text", "").strip()
                _parse_pair(text)
                item = CustomListWidgetItem(text)

                saved_modes = item_data.get("modes", {})
                if isinstance(saved_modes, dict):
                    for channel in CHANNELS:
                        mode = saved_modes.get(channel)
                        available = OTHER_MODES if channel == "other" else ALL_MODES
                        if mode in available:
                            item.modes[channel] = mode
                loaded_items.append(item)

            self.record_list.clear()
            for item in loaded_items:
                self.record_list.addItem(item)
            self.record_list.viewport().update()
            cmds.confirmDialog(
                title="成功",
                message="配置已读取。",
                button=["确定"],
            )
        except Exception as error:
            cmds.confirmDialog(
                title="读取失败",
                message=TEXT_TYPE(error),
                button=["确定"],
            )

    def _set_selected_items_mode(self, channel, mode):
        selected_items = self.record_list.selectedItems()
        if not selected_items:
            item = self.record_list.itemAt(
                self.record_list.mapFromGlobal(QtGui.QCursor.pos())
            )
            if item:
                selected_items = [item]

        for item in selected_items:
            if isinstance(item, CustomListWidgetItem):
                item.set_mode(channel, mode)
        self.record_list.viewport().update()

    def show_context_menu(self, position):
        clicked_item = self.record_list.itemAt(position)
        if clicked_item and not clicked_item.isSelected():
            self.record_list.clearSelection()
            clicked_item.setSelected(True)
            self.record_list.setCurrentItem(clicked_item)

        selected_items = self.record_list.selectedItems()
        if not selected_items:
            return

        menu = QtWidgets.QMenu(self)
        action_map = {}
        for channel in CHANNELS:
            channel_menu = menu.addMenu(CHANNEL_LABELS[channel])
            modes = OTHER_MODES if channel == "other" else ALL_MODES
            for mode in modes:
                action = channel_menu.addAction(MODE_LABELS[mode])
                action_map[action] = (channel, mode)

        menu.addSeparator()
        delete_action = menu.addAction("从列表删除")
        selected_action = _qt_exec(
            menu,
            self.record_list.viewport().mapToGlobal(position)
        )

        if selected_action in action_map:
            channel, mode = action_map[selected_action]
            self._set_selected_items_mode(channel, mode)
        elif selected_action == delete_action:
            for item in list(selected_items):
                self.record_list.takeItem(self.record_list.row(item))

    def select_objects(self, item):
        try:
            source, target = _parse_pair(item.text())
        except ValueError as error:
            _warning(TEXT_TYPE(error))
            return

        existing = [node for node in (source, target) if _object_exists(node)]
        missing = [node for node in (source, target) if not _object_exists(node)]
        if existing:
            cmds.select(existing, replace=True)
        if missing:
            _warning("以下对象不存在：{}".format(", ".join(missing)))


def maya_main_window():
    main_window_pointer = omui.MQtUtil.mainWindow()
    if not main_window_pointer:
        return None
    return wrapInstance(
        _pointer_value(main_window_pointer), QtWidgets.QWidget
    )


def show_window():
    global copy_animation_window

    try:
        copy_animation_window.close()
        copy_animation_window.deleteLater()
    except (NameError, RuntimeError, AttributeError):
        pass

    copy_animation_window = AutoAlignUI(parent=maya_main_window())
    copy_animation_window.setWindowFlags(QT_WINDOW)
    copy_animation_window.show()
    copy_animation_window.raise_()
    copy_animation_window.activateWindow()
    return copy_animation_window


if __name__ == "__main__":
    show_window()
