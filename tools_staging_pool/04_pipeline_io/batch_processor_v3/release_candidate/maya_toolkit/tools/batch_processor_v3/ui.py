"""Original full Qt file/script lists, sort/modes and controls; writes use API."""
import html as _html
from pathlib import Path
from .tool import BatchProcessorV3Tool
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
            if all((file_path.endswith(('.ma', '.mb', '.fbx')) for file_path in file_paths)):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super(MyListWidget, self).dragEnterEvent(event)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        open_action = menu.addAction('Open')
        delete_action = menu.addAction('Delete')
        menu.addSeparator()
        sort_menu = menu.addMenu('Sort')
        sort_name_action = sort_menu.addAction('By Name')
        sort_date_action = sort_menu.addAction('By Date')
        sort_size_action = sort_menu.addAction('By Size')
        menu.addSeparator()
        clear_action = menu.addAction('Clear List')
        open_action.triggered.connect(self.open_selected_files)
        delete_action.triggered.connect(self.delete_selected_files)
        sort_name_action.triggered.connect(lambda: self.sort_items('name'))
        sort_date_action.triggered.connect(lambda: self.sort_items('date'))
        sort_size_action.triggered.connect(lambda: self.sort_items('size'))
        clear_action.triggered.connect(self.clear)
        menu.exec_(self.mapToGlobal(position))

    def delete_selected_files(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))

    def sort_items(self, sort_type):
        items = [(self.item(i).text(), self.item(i).isSelected()) for i in range(self.count())]
        if sort_type == 'name':
            items.sort(key=lambda x: natural_sort_key(os.path.basename(x[0])))
        elif sort_type == 'date':
            items.sort(key=lambda x: os.path.getmtime(x[0]))
        elif sort_type == 'size':
            items.sort(key=lambda x: os.path.getsize(x[0]))
        self.clear()
        for file_path, is_selected in items:
            item = QtWidgets.QListWidgetItem(file_path)
            item.setSelected(is_selected)
            self.addItem(item)

class ScriptListWidget(DraggableListWidget):

    def __init__(self, parent=None):
        super(ScriptListWidget, self).__init__(parent)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [_get_file_path(url) for url in event.mimeData().urls()]
            if all((file_path.endswith(('.py', '.mel')) for file_path in file_paths)):
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            super(ScriptListWidget, self).dragEnterEvent(event)

    def show_context_menu(self, position):
        menu = QtWidgets.QMenu()
        delete_action = menu.addAction('Delete')
        menu.addSeparator()
        clear_action = menu.addAction('Clear List')
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
        self.setWindowTitle('Maya File Manager')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self.setGeometry(300, 300, 620, 560)
        self.execute_all_mode = True
        self.build_ui()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.path_field = QtWidgets.QLineEdit(self)
        self.path_field.setPlaceholderText('备份/保存路径（留空则使用源文件所在目录）')
        layout.addWidget(self.path_field)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical, self)
        self.file_list_widget = MyListWidget(splitter)
        self.file_list_widget.setToolTip('拖入 Maya 文件 (.ma .mb .fbx)')
        self.script_list_widget = ScriptListWidget(splitter)
        self.script_list_widget.setToolTip('拖入脚本文件 (.py .mel)')
        splitter.setSizes([300, 100])
        layout.addWidget(splitter)
        main_button_layout = QtWidgets.QHBoxLayout()
        left_button_layout = QtWidgets.QVBoxLayout()
        self.save_button = QtWidgets.QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_button_clicked)
        left_button_layout.addWidget(self.save_button)
        left_button_layout.addStretch()
        right_button_layout = QtWidgets.QVBoxLayout()
        self.auto_execute_button = QtWidgets.QPushButton('Auto Execute', self)
        self.auto_execute_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.auto_execute_button.customContextMenuRequested.connect(self.show_auto_execute_button_menu)
        self.auto_execute_button.clicked.connect(self.auto_execute)
        right_button_layout.addWidget(self.auto_execute_button)
        self.save_backup_checkbox = QtWidgets.QCheckBox('Save Backup', self)
        self.save_backup_checkbox.setToolTip('执行脚本前备份原始文件 -> BF_Backup/')
        right_button_layout.addWidget(self.save_backup_checkbox)
        self.save_after_checkbox = QtWidgets.QCheckBox('Save After', self)
        self.save_after_checkbox.setToolTip('执行脚本后另存处理结果 -> backup/')
        right_button_layout.addWidget(self.save_after_checkbox)
        self.overwrite_save_checkbox = QtWidgets.QCheckBox('Overwrite Save', self)
        self.overwrite_save_checkbox.setToolTip('执行脚本后覆盖原始文件（不可恢复，建议同时勾选 Save Backup）')
        self.overwrite_save_checkbox.stateChanged.connect(self.on_overwrite_save_changed)
        right_button_layout.addWidget(self.overwrite_save_checkbox)
        main_button_layout.addLayout(left_button_layout)
        main_button_layout.addLayout(right_button_layout)
        layout.addLayout(main_button_layout)
        log_label = QtWidgets.QLabel('执行日志：', self)
        layout.addWidget(log_label)
        self.log_text = QtWidgets.QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(130)
        self.log_text.setStyleSheet('background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas, monospace; font-size: 11px;')
        self.log_text.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.log_text.customContextMenuRequested.connect(self.show_log_context_menu)
        layout.addWidget(self.log_text)
        self.setLayout(layout)

    def log(self, message, level='INFO'):
        timestamp = time.strftime('%H:%M:%S')
        color_map = {'INFO': '#d4d4d4', 'OK': '#6a9955', 'WARN': '#dcdcaa', 'ERROR': '#f44747', 'SKIP': '#569cd6'}
        color = color_map.get(level, '#d4d4d4')
        html = '<span style="color:{}">[{}] [{}] {}</span>'.format(color, timestamp, level, _html.escape(str(message)))
        self.log_text.append(html)
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())
        QtWidgets.QApplication.processEvents()

    def show_auto_execute_button_menu(self, position):
        menu = QtWidgets.QMenu()
        label = 'Switch to Execute Selected' if self.execute_all_mode else 'Switch to Execute All'
        switch_action = menu.addAction(label)
        switch_action.triggered.connect(self.switch_execute_mode)
        menu.exec_(self.auto_execute_button.mapToGlobal(position))

    def switch_execute_mode(self):
        self.execute_all_mode = not self.execute_all_mode
        self.auto_execute_button.setText('Auto Execute' if self.execute_all_mode else 'Execute Selected')

    def show_log_context_menu(self, position):
        menu = QtWidgets.QMenu()
        clear_action = menu.addAction('Clear Log')
        clear_action.triggered.connect(self.log_text.clear)
        menu.exec_(self.log_text.mapToGlobal(position))

    def clear_list(self):
        self.file_list_widget.clear()
        self.script_list_widget.clear()

def open_file(path):
    if cmds.file(query=True,modified=True):
        cmds.warning('当前场景有未保存修改，请先保存。'); return
    if not Path(path).is_file(): cmds.warning('文件不存在：'+path); return
    try: cmds.file(path,open=True,force=False,executeScriptNodes=False,prompt=False)
    except Exception as exc: cmds.warning(str(exc))

def open_selected(self):
    items=self.selectedItems()
    if len(items)!=1: cmds.warning('请只选择一个文件打开。'); return
    open_file(items[0].text())

def open_double(self,event):
    item=self.itemAt(event.pos())
    if item: open_file(item.text())

MyListWidget.open_selected_files=open_selected
MyListWidget.mouseDoubleClickEvent=open_double
OriginalFileManager=MayaFileManager

class MayaFileManager(OriginalFileManager):
    def build_ui(self):
        super().build_ui()
        self.execution_mode=QtWidgets.QComboBox(self)
        self.execution_mode.addItem('隔离 mayapy（默认，保留当前场景）','isolated')
        self.execution_mode.addItem('当前 Maya（只允许干净已保存场景）','interactive')
        self.error_policy=QtWidgets.QComboBox(self)
        self.error_policy.addItem('出错跳过当前文件','skip_file'); self.error_policy.addItem('出错停止批次','stop_batch')
        self.cleanup_checkbox=QtWidgets.QCheckBox('保存前删除 unknown 节点（默认关闭）',self)
        for w in (self.execution_mode,self.error_policy,self.cleanup_checkbox): self.layout().insertWidget(1,w)
        self.overwrite_save_checkbox.setToolTip('覆盖 .ma/.mb；强制原始字节备份，文件写入不能 Maya Undo')
        self.setWindowTitle('Maya File Manager — 隔离批处理候选')
        self.busy=False

    def closeEvent(self,event):
        if self.busy: event.ignore()
        else: super().closeEvent(event)

    def on_overwrite_save_changed(self,state):
        if self.overwrite_save_checkbox.isChecked(): self.save_backup_checkbox.setChecked(True)

    def controls(self,enabled):
        self.busy=not enabled
        for w in (self.save_button,self.auto_execute_button,self.file_list_widget,self.script_list_widget,self.path_field,
                  self.save_backup_checkbox,self.save_after_checkbox,self.overwrite_save_checkbox,self.execution_mode,self.error_policy,self.cleanup_checkbox): w.setEnabled(enabled)

    def report(self,result):
        for row in (result.data or {}).get('scenes',[]):
            self.log(row['source']+': '+row['message'],'OK' if row['success'] else 'ERROR')
            for script in row.get('scripts',[]): self.log(script['path']+': '+('OK' if script['success'] else script.get('message','failed')),'OK' if script['success'] else 'ERROR')
            if row.get('backup'): self.log('原始字节备份：'+row['backup'])
            for output in row.get('outputs',[]): self.log('已保存：'+output['path'])
        self.log(result.message,'OK' if result.success else 'ERROR')
        return result

    def save_button_clicked(self):
        if self.busy: return
        if self.path_field.text().strip(): return self.save_as_ma()
        return self.save_in_current_path()

    def save_as_ma(self):
        source=cmds.file(query=True,sceneName=True); directory=self.path_field.text().strip()
        if not source or not Path(directory).is_dir(): self.log('需要已保存场景和有效保存目录','ERROR'); return
        target=str(Path(directory)/(Path(source).stem+'.ma'))
        self.controls(False)
        try: return self.report(BatchProcessorV3Tool().run(action='save_current',output=target,remove_unknown=self.cleanup_checkbox.isChecked()))
        finally: self.controls(True)

    def save_in_current_path(self):
        self.controls(False)
        try: return self.report(BatchProcessorV3Tool().run(action='save_current',overwrite=True,remove_unknown=self.cleanup_checkbox.isChecked()))
        finally: self.controls(True)

    def auto_execute(self):
        if self.busy: return
        files=[self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count()) if self.execute_all_mode or self.file_list_widget.item(i).isSelected()]
        scripts=[self.script_list_widget.item(i).text() for i in range(self.script_list_widget.count())]
        if not files: self.log('文件列表为空或没有选中的文件','ERROR'); return
        params=dict(action='process',files=files,scripts=scripts,base_dir=self.path_field.text().strip() or None,
                    save_backup=self.save_backup_checkbox.isChecked(),save_after=self.save_after_checkbox.isChecked(),overwrite=self.overwrite_save_checkbox.isChecked(),
                    remove_unknown=self.cleanup_checkbox.isChecked(),execution_mode=self.execution_mode.currentData(),error_policy=self.error_policy.currentData())
        progress=QtWidgets.QProgressDialog('正在处理文件','取消',0,len(files),self)
        progress.setWindowModality(QtCore.Qt.WindowModal); progress.setMinimumDuration(0); progress.setAutoClose(False)
        tool=BatchProcessorV3Tool()
        def update(index,total,message):
            progress.setValue(index); progress.setLabelText(message); QtWidgets.QApplication.processEvents()
        tool.progress=update; tool.cancelled=progress.wasCanceled
        self.controls(False); self.log('开始批处理；脚本可操作外部文件，取消不会回滚已完成输出。')
        try: return self.report(tool.run(**params))
        finally: progress.close(); self.controls(True)

_file_manager_instance=None
def show_maya_file_manager():
    global _file_manager_instance
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    try:
        if _file_manager_instance is not None:
            _file_manager_instance.show(); _file_manager_instance.raise_(); return _file_manager_instance
    except RuntimeError: _file_manager_instance=None
    _file_manager_instance=MayaFileManager(); _file_manager_instance.show(); return _file_manager_instance
