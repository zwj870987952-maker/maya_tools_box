##修改日志##

##PS:已知打开MGTools的自动保存之后会导致工具运行结束之后maya崩溃，可先关闭自动保存再使用##

##1.添加执行日志记录##
##2.批量执行脚本选项细化，添加脚本执行前另存，脚本执行后另存，脚本执行后覆盖当前文件保存##
##3.文件列表和脚本列表框高度修改##
##4.保存按钮修改为识别路径输入框判断是直接覆盖保存还是另存##
##5.兼容maya2025##


import os
import sys
import re
import codecs
import time
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel

try:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def _get_file_path(url):
    return os.path.normpath(url.toLocalFile())

def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]

def read_file_with_fallback(file_path):
    try:
        with codecs.open(file_path, 'r', 'utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with codecs.open(file_path, 'r') as f:
            return f.read()

def execute_script(script_path, *args):
    script_namespace = {}
    script_code = read_file_with_fallback(script_path)
    if script_path.endswith(".py"):
        exec(script_code, script_namespace)
    elif script_path.endswith(".mel"):
        mel.eval(script_code)

def remove_unknown_nodes():
    unknown_nodes = cmds.ls(type='unknown')
    if unknown_nodes:
        cmds.delete(unknown_nodes)

class DraggableListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(DraggableListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DraggableListWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DraggableListWidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [_get_file_path(url) for url in event.mimeData().urls()]
            self.add_files_in_order(file_paths)
            event.acceptProposedAction()
        else:
            super(DraggableListWidget, self).dropEvent(event)

    def add_files_in_order(self, file_paths):
        for file_path in file_paths:
            self.addItem(file_path)

    def show_context_menu(self, position):
        pass

class MyListWidget(DraggableListWidget):
    def __init__(self, parent=None):
        super(MyListWidget, self).__init__(parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [_get_file_path(url) for url in event.mimeData().urls()]
            if all(file_path.endswith((".ma", ".mb", ".fbx")) for file_path in file_paths):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super(MyListWidget, self).dragEnterEvent(event)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        open_action   = menu.addAction("Open")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        sort_menu        = menu.addMenu("Sort")
        sort_name_action = sort_menu.addAction("By Name")
        sort_date_action = sort_menu.addAction("By Date")
        sort_size_action = sort_menu.addAction("By Size")
        menu.addSeparator()
        clear_action = menu.addAction("Clear List")

        open_action.triggered.connect(self.open_selected_files)
        delete_action.triggered.connect(self.delete_selected_files)
        sort_name_action.triggered.connect(lambda: self.sort_items("name"))
        sort_date_action.triggered.connect(lambda: self.sort_items("date"))
        sort_size_action.triggered.connect(lambda: self.sort_items("size"))
        clear_action.triggered.connect(self.clear)

        menu.exec_(self.mapToGlobal(position))

    def open_selected_files(self):
        for item in self.selectedItems():
            file_path = item.text()
            if os.path.exists(file_path):
                if file_path.endswith((".ma", ".mb", ".fbx")):
                    cmds.file(file_path, open=True, force=True)

    def delete_selected_files(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

    def sort_items(self, sort_type):
        items = [(self.item(i).text(), self.item(i).isSelected()) for i in range(self.count())]
        if sort_type == "name":
            items.sort(key=lambda x: natural_sort_key(os.path.basename(x[0])))
        elif sort_type == "date":
            items.sort(key=lambda x: os.path.getmtime(x[0]))
        elif sort_type == "size":
            items.sort(key=lambda x: os.path.getsize(x[0]))
        self.clear()
        for file_path, is_selected in items:
            item = QtWidgets.QListWidgetItem(file_path)
            item.setSelected(is_selected)
            self.addItem(item)

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            file_path = item.text()
            if os.path.exists(file_path):
                if file_path.endswith((".ma", ".mb", ".fbx")):
                    cmds.file(file_path, open=True, force=True)

class ScriptListWidget(DraggableListWidget):
    def __init__(self, parent=None):
        super(ScriptListWidget, self).__init__(parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [_get_file_path(url) for url in event.mimeData().urls()]
            if all(file_path.endswith((".py", ".mel")) for file_path in file_paths):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super(ScriptListWidget, self).dragEnterEvent(event)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        clear_action  = menu.addAction("Clear List")
        delete_action.triggered.connect(self.delete_selected_scripts)
        clear_action.triggered.connect(self.clear)
        menu.exec_(self.mapToGlobal(position))

    def delete_selected_scripts(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

class MayaFileManager(QtWidgets.QDialog):
    def __init__(self, parent=None):
        if parent is None:
            parent = maya_main_window()
        super(MayaFileManager, self).__init__(parent)
        self.setWindowTitle("Maya File Manager")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setGeometry(300, 300, 620, 560)
        self.execute_all_mode = True
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.path_field = QtWidgets.QLineEdit(self)
        self.path_field.setPlaceholderText("备份/保存路径（留空则使用源文件所在目录）")
        layout.addWidget(self.path_field)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        self.file_list_widget = MyListWidget(splitter)
        self.file_list_widget.setToolTip("拖入 Maya 文件 (.ma .mb .fbx)")
        self.script_list_widget = ScriptListWidget(splitter)
        self.script_list_widget.setToolTip("拖入脚本文件 (.py .mel)")
        splitter.setSizes([300, 100])
        layout.addWidget(splitter)

        # 主横向布局：左侧按钮列 + 右侧 Auto Execute 列（含保存选项）
        main_button_layout = QtWidgets.QHBoxLayout()

        # 左侧：Save
        left_button_layout = QtWidgets.QVBoxLayout()
        self.save_button = QtWidgets.QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_button_clicked)
        left_button_layout.addWidget(self.save_button)
        left_button_layout.addStretch()

        # 右侧：Auto Execute 按钮 + 三个保存选项
        right_button_layout = QtWidgets.QVBoxLayout()
        self.auto_execute_button = QtWidgets.QPushButton("Auto Execute", self)
        self.auto_execute_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.auto_execute_button.customContextMenuRequested.connect(self.show_auto_execute_button_menu)
        self.auto_execute_button.clicked.connect(self.auto_execute)
        right_button_layout.addWidget(self.auto_execute_button)

        self.save_backup_checkbox = QtWidgets.QCheckBox("Save Backup", self)
        self.save_backup_checkbox.setToolTip("执行脚本前备份原始文件 -> BF_Backup/")
        right_button_layout.addWidget(self.save_backup_checkbox)

        self.save_after_checkbox = QtWidgets.QCheckBox("Save After", self)
        self.save_after_checkbox.setToolTip("执行脚本后另存处理结果 -> backup/")
        right_button_layout.addWidget(self.save_after_checkbox)

        self.overwrite_save_checkbox = QtWidgets.QCheckBox("Overwrite Save", self)
        self.overwrite_save_checkbox.setToolTip("执行脚本后覆盖原始文件（不可恢复，建议同时勾选 Save Backup）")
        self.overwrite_save_checkbox.stateChanged.connect(self.on_overwrite_save_changed)
        right_button_layout.addWidget(self.overwrite_save_checkbox)

        main_button_layout.addLayout(left_button_layout)
        main_button_layout.addLayout(right_button_layout)
        layout.addLayout(main_button_layout)

        log_label = QtWidgets.QLabel("执行日志：", self)
        layout.addWidget(log_label)

        self.log_text = QtWidgets.QPlainTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(130)
        self.log_text.setStyleSheet(
            "background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 11px;"
        )
        self.log_text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.log_text.customContextMenuRequested.connect(self.show_log_context_menu)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        color_map = {
            "INFO":  "#d4d4d4",
            "OK":    "#6a9955",
            "WARN":  "#dcdcaa",
            "ERROR": "#f44747",
            "SKIP":  "#569cd6"
        }
        color = color_map.get(level, "#d4d4d4")
        html = '<span style="color:{}">[{}] [{}] {}</span>'.format(color, timestamp, level, message)
        self.log_text.appendHtml(html)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()

    def save_button_clicked(self):
        save_path = self.path_field.text().strip()
        if save_path and os.path.isdir(save_path):
            self.save_as_ma()
        else:
            self.save_in_current_path()

    def save_as_ma(self):
        save_path = self.path_field.text()
        if not save_path or not os.path.isdir(save_path):
            QtWidgets.QMessageBox.warning(self, "警告", "路径无效，请检查路径输入框。")
            return
        current_scene_name = cmds.file(query=True, sceneName=True, shortName=True)
        if not current_scene_name:
            QtWidgets.QMessageBox.warning(self, "警告", "当前没有打开的场景。")
            return
        base_name = os.path.splitext(current_scene_name)[0] + ".ma"
        full_path = os.path.join(save_path, base_name)
        remove_unknown_nodes()
        cmds.file(rename=full_path)
        cmds.file(save=True, type='mayaAscii')

    def save_in_current_path(self):
        current_scene_path = cmds.file(query=True, sceneName=True)
        if not current_scene_path:
            QtWidgets.QMessageBox.warning(self, "警告", "当前没有打开的场景。")
            return
        remove_unknown_nodes()
        cmds.file(save=True, type='mayaAscii')

    def show_auto_execute_button_menu(self, position):
        menu = QtWidgets.QMenu()
        label = "Switch to Execute Selected" if self.execute_all_mode else "Switch to Execute All"
        switch_action = menu.addAction(label)
        switch_action.triggered.connect(self.switch_execute_mode)
        menu.exec_(self.auto_execute_button.mapToGlobal(position))

    def switch_execute_mode(self):
        self.execute_all_mode = not self.execute_all_mode
        self.auto_execute_button.setText("Auto Execute" if self.execute_all_mode else "Execute Selected")

    def on_overwrite_save_changed(self, state):
        if int(state) == 2:
            reply = QtWidgets.QMessageBox.warning(
                self,
                "警告",
                "你已勾选「Overwrite Save」\n\n"
                "执行后将直接覆盖原始文件，此操作不可恢复！\n"
                "建议同时勾选「Save Backup」以保留原始备份。\n\n"
                "是否继续保持勾选？",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.No:
                self.overwrite_save_checkbox.setChecked(False)

    def show_log_context_menu(self, position):
        menu = QtWidgets.QMenu()
        clear_action = menu.addAction("Clear Log")
        clear_action.triggered.connect(self.log_text.clear)
        menu.exec_(self.log_text.mapToGlobal(position))

    def clear_list(self):
        self.file_list_widget.clear()
        self.script_list_widget.clear()

    def auto_execute(self):
        start_time = time.time()

        save_backup    = self.save_backup_checkbox.isChecked()
        save_after     = self.save_after_checkbox.isChecked()
        overwrite_save = self.overwrite_save_checkbox.isChecked()
        script_paths   = [self.script_list_widget.item(i).text() for i in range(self.script_list_widget.count())]

        if self.execute_all_mode:
            file_paths = [self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count())]
        else:
            file_paths = [item.text() for item in self.file_list_widget.selectedItems()]

        total = len(file_paths)
        if total == 0:
            QtWidgets.QMessageBox.warning(self, "警告", "文件列表为空，请先添加 Maya 文件。")
            return

        progress = QtWidgets.QProgressDialog("正在处理文件...", "取消", 0, total, self)
        progress.setWindowTitle("Auto Execute")
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        success_count = 0
        skip_count    = 0
        error_count   = 0

        self.log("开始批量处理，共 {} 个文件".format(total), "INFO")

        for idx, file_path in enumerate(file_paths):
            if progress.wasCanceled():
                self.log("用户取消了操作", "WARN")
                break

            file_name = os.path.basename(file_path)
            progress.setLabelText("正在处理 ({}/{})：{}".format(idx + 1, total, file_name))
            progress.setValue(idx)
            QtWidgets.QApplication.processEvents()

            if not os.path.exists(file_path):
                self.log("文件不存在，已跳过：{}".format(file_path), "WARN")
                skip_count += 1
                continue

            self.log("打开文件：{}".format(file_name), "INFO")
            cmds.file(file_path, open=True, force=True)

            # 执行脚本前备份原始文件（仅勾选 Save Backup 时执行）
            if save_backup:
                base_dir = self.path_field.text() if self.path_field.text() else os.path.dirname(file_path)
                backup_dir = os.path.join(base_dir, "BF_Backup")
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                cmds.file(rename=backup_path)
                cmds.file(save=True, type='mayaAscii')
                cmds.file(rename=file_path)
                self.log("  原始文件已备份至：{}".format(backup_path), "OK")

            # 执行脚本
            script_failed = False
            for script_path in script_paths:
                try:
                    execute_script(script_path)
                    self.log("  脚本执行成功：{}".format(os.path.basename(script_path)), "OK")
                except Exception as e:
                    error_msg = str(e)
                    self.log("  脚本执行失败：{} -> {}".format(os.path.basename(script_path), error_msg), "ERROR")
                    reply = QtWidgets.QMessageBox.question(
                        self,
                        "脚本执行出错",
                        "文件：{}\n脚本：{}\n\n错误：{}\n\n是否跳过该文件继续处理后续文件？".format(
                            file_name, os.path.basename(script_path), error_msg
                        ),
                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                        QtWidgets.QMessageBox.Yes
                    )
                    if reply == QtWidgets.QMessageBox.Yes:
                        self.log("  已跳过：{}".format(file_name), "SKIP")
                        skip_count += 1
                        script_failed = True
                        break
                    else:
                        progress.setValue(total)
                        elapsed = time.time() - start_time
                        self.log("========================================", "INFO")
                        self.log("用户终止了所有操作", "ERROR")
                        self.log("  成功：{}  跳过：{}  失败：{}  耗时：{:.2f}s".format(
                            success_count, skip_count, error_count, elapsed), "INFO")
                        self.log("========================================", "INFO")
                        return

            if script_failed:
                error_count += 1
                continue

            # 执行脚本后另存处理结果（仅勾选 Save After 时执行）
            if save_after:
                base_dir = self.path_field.text() if self.path_field.text() else os.path.dirname(file_path)
                after_dir = os.path.join(base_dir, "backup")
                os.makedirs(after_dir, exist_ok=True)
                after_path = os.path.join(after_dir, os.path.basename(file_path))
                remove_unknown_nodes()
                cmds.file(rename=after_path)
                cmds.file(save=True, type='mayaAscii')
                cmds.file(rename=file_path)
                self.log("  处理结果已另存至：{}".format(after_path), "OK")

            # 覆盖保存原始文件（仅勾选 Overwrite Save 时执行）
            if overwrite_save:
                remove_unknown_nodes()
                cmds.file(save=True, type='mayaAscii')
                self.log("  已覆盖保存：{}".format(file_name), "OK")

            # 未勾选任何保存选项
            if not save_backup and not save_after and not overwrite_save:
                self.log("  未勾选保存选项，跳过保存：{}".format(file_name), "SKIP")

            success_count += 1
            self.log("完成：{}".format(file_name), "OK")

        progress.setValue(total)
        elapsed_time = time.time() - start_time
        self.log("========================================", "INFO")
        self.log("批量处理完成！", "OK")
        self.log("  成功：{}  跳过：{}  失败：{}  耗时：{:.2f}s".format(
            success_count, skip_count, error_count, elapsed_time), "INFO")
        self.log("========================================", "INFO")

_file_manager_instance = None

def show_maya_file_manager():
    global _file_manager_instance
    try:
        if _file_manager_instance is not None:
            _file_manager_instance.show()
            _file_manager_instance.raise_()
            return
    except RuntimeError:
        _file_manager_instance = None
    _file_manager_instance = MayaFileManager()
    _file_manager_instance.show()

if __name__ == '__main__':
    show_maya_file_manager()
