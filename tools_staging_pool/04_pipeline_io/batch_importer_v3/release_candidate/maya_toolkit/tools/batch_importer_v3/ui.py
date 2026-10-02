"""Complete original Qt UI; no module-level window creation."""
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
try:
    from PySide6 import QtWidgets,QtGui,QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets,QtGui,QtCore
    from shiboken2 import wrapInstance
from .tool import BatchImporterV3Tool,namespace_base
count_spinbox=None

def ui_items():
    return [{'path':list_widget.item(i).text(),'count':count_layout.itemAt(i).widget().value(),
             'namespace':name_layout.itemAt(i).widget().text()} for i in range(list_widget.count())]

def report(result):
    print(result.to_dict())
    if not result.success: cmds.warning(result.message)
    return result

def import_references(): return report(BatchImporterV3Tool().run(action='reference',items=ui_items()))
def import_all_items(): return report(BatchImporterV3Tool().run(action='import',items=ui_items()))
def remove_referenced_objects(): return report(BatchImporterV3Tool().run(action='remove_reference'))

def maya_main_window():
    """
    Get Maya's main window as a QtWidgets.QMainWindow instance
    :return: QtWidgets.QMainWindow instance of Maya's main window
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def add_watermark():
    watermark_label = QtWidgets.QLabel("<font size='4' color='gray'>by ZWJ</font>")
    watermark_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
    layout.addWidget(watermark_label)

def delete_item():
    selected_items = list_widget.selectedItems()
    for item in selected_items:
        row = list_widget.row(item)
        list_widget.takeItem(row)
        name_widget = name_layout.itemAt(row).widget()
        count_widget = count_layout.itemAt(row).widget()
        name_layout.removeWidget(name_widget)
        count_layout.removeWidget(count_widget)
        name_widget.deleteLater()
        count_widget.deleteLater()

def add_file():
    global count_spinbox
    default_filter = 'All Supported Files (*.ma *.mb *.fbx *.obj *.abc);;Maya Files (*.ma *.mb);;FBX Files (*.fbx);;OBJ Files (*.obj);;Alembic Files (*.abc);;All Files (*.*)'
    result = cmds.fileDialog2(dialogStyle=2, fileMode=4, caption='Select Files', fileFilter=default_filter)
    if result:
        files = result
        for file in files:
            valid_extensions = ['.ma', '.mb', '.fbx', '.obj', '.abc']
            if not any((file.lower().endswith(ext) for ext in valid_extensions)):
                continue
            list_widget.addItem(file)
            file_name = namespace_base(file)
            if file_name in import_count:
                count = import_count[file_name]
            else:
                count = 1
            name_widget = QtWidgets.QLineEdit(file_name)
            name_widget.setReadOnly(False)
            name_widget.setAlignment(QtCore.Qt.AlignCenter)
            name_widget.setFixedHeight(30)
            name_layout.addWidget(name_widget)
            count_spinbox = QtWidgets.QSpinBox()
            count_spinbox.setRange(1, 9999)
            count_spinbox.setValue(count)
            count_spinbox.setAlignment(QtCore.Qt.AlignCenter)
            count_spinbox.setFixedHeight(30)
            count_layout.addWidget(count_spinbox)

def add_folder_files():
    global count_spinbox
    default_filter = 'All Supported Files (*.ma *.mb *.fbx *.obj *.abc);;Maya Files (*.ma *.mb);;FBX Files (*.fbx);;OBJ Files (*.obj);;Alembic Files (*.abc);;All Files (*.*)'
    chosen = cmds.fileDialog2(dialogStyle=3, fileMode=3, caption='Select Folder', fileFilter=default_filter)
    folder = chosen[0] if chosen else None
    if folder:
        for root, dirs, files in os.walk(folder):
            for file in files:
                file_path = os.path.join(root, file)
                valid_extensions = ['.ma', '.mb', '.fbx', '.obj', '.abc']
                if not any((file.lower().endswith(ext) for ext in valid_extensions)):
                    continue
                list_widget.addItem(file_path)
                file_name = namespace_base(file_path)
                if file_name in import_count:
                    count = import_count[file_name]
                else:
                    count = 1
                name_widget = QtWidgets.QLineEdit(file_name)
                name_widget.setReadOnly(False)
                name_widget.setAlignment(QtCore.Qt.AlignCenter)
                name_widget.setFixedHeight(30)
                name_layout.addWidget(name_widget)
                count_spinbox = QtWidgets.QSpinBox()
                count_spinbox.setRange(1, 9999)
                count_spinbox.setValue(count)
                count_spinbox.setAlignment(QtCore.Qt.AlignCenter)
                count_spinbox.setFixedHeight(30)
                count_layout.addWidget(count_spinbox)

def show_ui():
    global add_file_button, add_folder_button, central_widget, count_layout, delete_button, hlayout1, hlayout2, hlayout3, hlayout4, hlayout5, import_all_button, import_button, import_count, layout, list_widget, maya_window, name_layout, remove_referenced_button, window
    maya_window = maya_main_window()
    window = QtWidgets.QMainWindow(maya_window)
    window.setWindowTitle('Import Object — namespace可编辑 / Del Ref删除整份引用')
    window.resize(500, 300)
    layout = QtWidgets.QVBoxLayout()
    hlayout1 = QtWidgets.QHBoxLayout()
    add_file_button = QtWidgets.QPushButton('Add Files')
    add_file_button.clicked.connect(add_file)
    hlayout1.addWidget(add_file_button)
    add_folder_button = QtWidgets.QPushButton('Add Folder')
    add_folder_button.clicked.connect(add_folder_files)
    hlayout1.addWidget(add_folder_button)
    hlayout2 = QtWidgets.QHBoxLayout()
    import_button = QtWidgets.QPushButton('References')
    import_button.clicked.connect(import_references)
    hlayout2.addWidget(import_button)
    import_all_button = QtWidgets.QPushButton('Import')
    import_all_button.clicked.connect(import_all_items)
    hlayout2.addWidget(import_all_button)
    delete_button = QtWidgets.QPushButton('Delete')
    delete_button.clicked.connect(delete_item)
    delete_button.setStyleSheet('background-color: red')
    hlayout2.addWidget(delete_button)
    remove_referenced_button = QtWidgets.QPushButton('Del Ref')
    remove_referenced_button.clicked.connect(remove_referenced_objects)
    hlayout2.addWidget(remove_referenced_button)
    hlayout5 = QtWidgets.QHBoxLayout()
    hlayout4 = QtWidgets.QHBoxLayout()
    name_layout = QtWidgets.QVBoxLayout()
    name_layout.setSpacing(0)
    count_layout = QtWidgets.QVBoxLayout()
    count_layout.setSpacing(0)
    hlayout4.addLayout(name_layout)
    hlayout4.addLayout(count_layout)
    layout.addLayout(hlayout1)
    layout.addLayout(hlayout2)
    layout.addLayout(hlayout4)
    layout.addLayout(hlayout5)
    hlayout5.setAlignment(QtCore.Qt.AlignTop)
    hlayout3 = QtWidgets.QHBoxLayout()
    list_widget = QtWidgets.QListWidget()
    list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    hlayout3.addWidget(list_widget)
    layout.addLayout(hlayout3)
    import_count = {}
    central_widget = QtWidgets.QWidget()
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)
    add_watermark()
    window.show()
    window.raise_()
    window.activateWindow()
    window.setFocus()
    return window
