############0910增加批量去除参考文件，增加文件夹添加，添加水印
############1002批量去除参考bug修复，优化导入文件类型，文件夹导入加上子文件夹


import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtGui, QtCore
from shiboken2 import wrapInstance

count_spinbox = None  # 声明 count_spinbox 为全局变量

def maya_main_window():
    """
    Get Maya's main window as a QtWidgets.QMainWindow instance
    :return: QtWidgets.QMainWindow instance of Maya's main window
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def add_watermark():
    # 创建水印标签
    watermark_label = QtWidgets.QLabel("<font size='4' color='gray'>by ZWJ</font>")
    watermark_label.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
    
    # 将水印标签添加到窗口
    layout.addWidget(watermark_label)



def import_references():
    file_list = [list_widget.item(i).text() for i in range(list_widget.count())]

    for i, file in enumerate(file_list):
        count_spinbox = count_layout.itemAt(i).widget()
        file_name = os.path.basename(file).split(".")[0]  # 获取文件名
        count = count_spinbox.value()  # 获取次数框中的次数

        for j in range(count):  # 根据次数循环导入文件
            if j == 0:
                namespace = file_name
            else:
                namespace = "{}{}".format(file_name, j)
            cmds.file(file, reference=True, namespace=namespace)

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
    global count_spinbox  # 声明使用全局变量 count_spinbox
    # 设置默认文件筛选器
    default_filter = "All Supported Files (*.ma *.mb *.fbx *.obj *.abc);;Maya Files (*.ma *.mb);;FBX Files (*.fbx);;OBJ Files (*.obj);;Alembic Files (*.abc);;All Files (*.*)"
    result = cmds.fileDialog2(dialogStyle=2, fileMode=4, caption="Select Files", fileFilter=default_filter)
    if result:
        files = result
        for file in files:
            # 检查文件扩展名是否在允许的范围内
            valid_extensions = ['.ma', '.mb', '.fbx', '.obj', '.abc']
            if not any(file.lower().endswith(ext) for ext in valid_extensions):
                continue  # 忽略不支持的文件类型
            list_widget.addItem(file)
            file_name = os.path.basename(file).split(".")[0]
            if file_name in import_count:
                count = import_count[file_name]
            else:
                count = 1

            name_widget = QtWidgets.QLineEdit(file_name)
            name_widget.setReadOnly(True)
            name_widget.setAlignment(QtCore.Qt.AlignCenter)
            name_widget.setFixedHeight(30)  # 设置次数框高度为30
            name_layout.addWidget(name_widget)

            count_spinbox = QtWidgets.QSpinBox()  # 将 count_spinbox 变为全局变量
            count_spinbox.setRange(1, 9999)  # 设置数值范围
            count_spinbox.setValue(count)
            count_spinbox.setAlignment(QtCore.Qt.AlignCenter)
            count_spinbox.setFixedHeight(30)  # 设置次数框高度为30
            count_layout.addWidget(count_spinbox)

#######添加文件夹           
def add_folder_files():
    global count_spinbox
    # 设置默认文件筛选器，包含所有支持的文件类型
    default_filter = "All Supported Files (*.ma *.mb *.fbx *.obj *.abc);;Maya Files (*.ma *.mb);;FBX Files (*.fbx);;OBJ Files (*.obj);;Alembic Files (*.abc);;All Files (*.*)"
    folder = cmds.fileDialog2(dialogStyle=3, fileMode=3, caption="Select Folder", fileFilter=default_filter)[0]
    if folder:
        for root, dirs, files in os.walk(folder):
            for file in files:
                # 获取文件的绝对路径
                file_path = os.path.join(root, file)
                # 检查文件扩展名是否在允许的范围内
                valid_extensions = ['.ma', '.mb', '.fbx', '.obj', '.abc']
                if not any(file.lower().endswith(ext) for ext in valid_extensions):
                    continue  # 忽略不支持的文件类型
                list_widget.addItem(file_path)
                file_name = os.path.basename(file_path).split(".")[0]
                if file_name in import_count:
                    count = import_count[file_name]
                else:
                    count = 1

                name_widget = QtWidgets.QLineEdit(file_name)
                name_widget.setReadOnly(True)
                name_widget.setAlignment(QtCore.Qt.AlignCenter)
                name_widget.setFixedHeight(30)
                name_layout.addWidget(name_widget)

                count_spinbox = QtWidgets.QSpinBox()
                count_spinbox.setRange(1, 9999)
                count_spinbox.setValue(count)
                count_spinbox.setAlignment(QtCore.Qt.AlignCenter)
                count_spinbox.setFixedHeight(30)
                count_layout.addWidget(count_spinbox)


def import_all_items():
    file_list = [list_widget.item(i).text() for i in range(list_widget.count())]
    
    for i, file in enumerate(file_list):
        count_spinbox = count_layout.itemAt(i).widget()
        file_name = os.path.basename(file).split(".")[0]  # 获取文件名
        count = count_spinbox.value()  # 获取次数框中的次数
        
        for j in range(count):  # 根据次数循环导入文件
            if j == 0:
                namespace = file_name
            else:
                namespace = "{}{}".format(file_name, j)
            cmds.file(file, i=True, namespace=namespace, force=True)
            
######增加批量去除参考文件功能
def remove_referenced_objects():
    # 获取当前选择的物体
    selected_objects = cmds.ls(selection=True)
    
    # 遍历选择的物体
    for obj in selected_objects:
        try:
            # 检查是否是引用物体
            if cmds.referenceQuery(obj, isNodeReferenced=True):
                # 解除引用
                ref_node = cmds.referenceQuery(obj, referenceNode=True)
                cmds.file(rfn=ref_node, removeReference=True)
                print("已删除引用物体:", obj)
        except RuntimeError:
            # 如果物体找不到，则捕获异常并继续下一个物体
            continue

# 获取Maya的主窗口
maya_window = maya_main_window()

# 创建窗口
window = QtWidgets.QMainWindow(maya_window)
window.setWindowTitle("Import Object")
window.resize(500, 300)

# 创建布局
layout = QtWidgets.QVBoxLayout()

# 创建第一行布局
hlayout1 = QtWidgets.QHBoxLayout()
add_file_button = QtWidgets.QPushButton("Add Files")
add_file_button.clicked.connect(add_file)
hlayout1.addWidget(add_file_button)
add_folder_button = QtWidgets.QPushButton("Add Folder")
add_folder_button.clicked.connect(add_folder_files)
hlayout1.addWidget(add_folder_button)

# 创建第二行布局
hlayout2 = QtWidgets.QHBoxLayout()
import_button = QtWidgets.QPushButton("References")
import_button.clicked.connect(import_references)
hlayout2.addWidget(import_button)
import_all_button = QtWidgets.QPushButton("Import")
import_all_button.clicked.connect(import_all_items)
hlayout2.addWidget(import_all_button)
delete_button = QtWidgets.QPushButton("Delete")
delete_button.clicked.connect(delete_item)
delete_button.setStyleSheet("background-color: red")
hlayout2.addWidget(delete_button)

# 添加一个按钮到第二行布局，功能为remove_referenced_objects
remove_referenced_button = QtWidgets.QPushButton("Del Ref")  # 将按钮文本改为"Del Ref"
remove_referenced_button.clicked.connect(remove_referenced_objects)
hlayout2.addWidget(remove_referenced_button)



# 创建第五行布局
hlayout5 = QtWidgets.QHBoxLayout()

# 创建第四行布局
hlayout4 = QtWidgets.QHBoxLayout()
name_layout = QtWidgets.QVBoxLayout()
name_layout.setSpacing(0)

count_layout = QtWidgets.QVBoxLayout()
count_layout.setSpacing(0)

hlayout4.addLayout(name_layout)
hlayout4.addLayout(count_layout)

# 添加布局到主布局
layout.addLayout(hlayout1)
layout.addLayout(hlayout2)
layout.addLayout(hlayout4)  # Add the fourth layout (hlayout4) to the main layout
layout.addLayout(hlayout5)

# 设置文本框和次数框在垂直方向上顶部对齐
hlayout5.setAlignment(QtCore.Qt.AlignTop)

# 创建第三行布局
hlayout3 = QtWidgets.QHBoxLayout()
list_widget = QtWidgets.QListWidget()
list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
hlayout3.addWidget(list_widget)

layout.addLayout(hlayout3)  # Move the third layout (hlayout3) below all other layouts

# 创建一个字典来保存每个物体的导入次数
import_count = {}

# 将布局设置到窗口中
central_widget = QtWidgets.QWidget()
central_widget.setLayout(layout)
window.setCentralWidget(central_widget)

# 添加水印
add_watermark()


# 显示窗口
window.show()

# 运行主循环
window.raise_()
window.activateWindow()
window.setFocus()