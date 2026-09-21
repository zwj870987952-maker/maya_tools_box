# coding=utf-8
import os
import maya.cmds as cmds
import shutil
from PySide2 import QtWidgets, QtCore, QtGui
import shiboken2
import maya.OpenMayaUI as omui

# 保存所有文件夹路径的列表
folder_paths = []

def clear_maya_file(path):
    u"""删除所有未知节点与插件，删除多余script节点"""
    try:
        path = path.replace('\\', '/')
        folder_path = path.rsplit('/', 1)[0]
        file_name = path.rsplit('/', 1)[-1].rsplit('.', 1)[0]
        backup_folder = folder_path + '/history'
        new_file = backup_folder + '/' + file_name + '_backup.ma'
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        shutil.copyfile(path, new_file)
        results = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as file_obj:
            need_write = True
            for line in file_obj.readlines():
                if line.startswith('createNode') or line.startswith('select'):
                    need_write = True
                    if line.startswith('createNode script'):
                        if not line.startswith('createNode script -n "sceneConfigurationScriptNode"'):
                            need_write = False
                if line.startswith('requires maya'):
                    results.append(line)
                    need_write = False
                if line.startswith('currentUnit'):
                    need_write = True
                if need_write:
                    results.append(line)
        with open(path, "w", encoding='utf-8', errors='ignore') as file_obj:
            file_obj.writelines(results)
        return [True, new_file]
    except PermissionError as e:
        error_message = f"权限错误: 无法访问文件 {path}。请检查文件权限和是否被其他程序占用。"
        cmds.warning(error_message)
        print(error_message)
        return [False, path]

def list_maya_file(dir_path):
    all_file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if file.endswith('.ma'):
                all_file_list.append(os.path.join(root, file))
    return all_file_list

def start_clean(*arg):
    if not folder_paths:
        feedback_label.setText(u'请拖拽文件夹路径到上方区域')
    else:
        maya_file_list = []
        for folder_path in folder_paths:
            maya_file_list.extend(list_maya_file(folder_path))
        
        if maya_file_list:
            progress_dialog = QtWidgets.QProgressDialog("正在清理文件...", "取消", 0, len(maya_file_list))
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.setMinimumDuration(0)
            feedback_label.setText(u'开始清理maya文件')
            for i, each_file in enumerate(maya_file_list):
                if progress_dialog.wasCanceled():
                    feedback_label.setText(u'操作已取消')
                    break
                clear_maya_file(each_file)
                progress_dialog.setValue(i + 1)
            else:
                feedback_label.setText(u'全部清理完毕并且备份完毕')
            progress_dialog.close()
        else:
            feedback_label.setText(u'没有找到任何 .ma 文件')

class DragDropWidget(QtWidgets.QWidget):
    def __init__(self):
        super(DragDropWidget, self).__init__()
        self.setAcceptDrops(True)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.text_label = QtWidgets.QLabel('请拖拽文件夹路径到此区域 (支持多个文件夹)', self)
        self.text_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.text_label)
        self.folder_list_widget = QtWidgets.QListWidget(self)
        self.layout.addWidget(self.folder_list_widget)
        self.feedback_label = QtWidgets.QLabel('_(:з」∠)_', self)
        self.layout.addWidget(self.feedback_label)
        global feedback_label
        feedback_label = self.feedback_label

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    folder_paths.append(path)
                    self.folder_list_widget.addItem(path)
            event.acceptProposedAction()

    def clear(self):
        self.folder_list_widget.clear()
        global folder_paths
        folder_paths = []

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class MayaFileCleanUI(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MayaFileCleanUI, self).__init__(parent)
        self.setWindowTitle('maya文件清理魔改版')
        self.setGeometry(300, 300, 400, 300)
        self.central_widget = DragDropWidget()
        self.setCentralWidget(self.central_widget)
        self.start_button = QtWidgets.QPushButton('开始清理', self)
        self.start_button.clicked.connect(start_clean)
        self.central_widget.layout.addWidget(self.start_button)
        self.clear_button = QtWidgets.QPushButton('清除路径', self)
        self.clear_button.clicked.connect(self.central_widget.clear)
        self.central_widget.layout.addWidget(self.clear_button)

def show_ui():
    global maya_file_clean_ui
    try:
        maya_file_clean_ui.close() # 关闭之前打开的窗口
    except:
        pass
    maya_file_clean_ui = MayaFileCleanUI(maya_main_window())
    maya_file_clean_ui.show()

show_ui()