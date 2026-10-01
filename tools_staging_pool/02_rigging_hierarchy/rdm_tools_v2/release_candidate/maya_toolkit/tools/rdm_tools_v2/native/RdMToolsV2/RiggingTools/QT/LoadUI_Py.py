from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtGui, QtCore
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtUiTools
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtWidgets
from maya_toolkit.tools.rdm_tools_v2.qt_compat import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel
Title = 'NAME HERE'
Folder = 'FOLDER'
UI_File = 'UI_NAME.ui'

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class UIName(QtWidgets.QDialog):

    def __init__(self, parent=None):
        if parent is None:
            parent = maya_main_window()
        super(UIName, self).__init__(parent)
        self.setWindowTitle(Title)
        self.setFixedSize(682, 590)
        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        UIPath = bundled_scripts_dir(usd=True) + Folder + '/'
        f = QtCore.QFile(UIPath + UI_File)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)
        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(3, 3, 3, 3)
        imagePath = bundled_scripts_dir(usd=True) + ResourcesPath

    def create_connections(self):

        def Demo(self):
            print('This is a DemoFunc')
"\nStylesheets:\n\nhttps://renderdemartes.com/2019/10/09/qt-stylesheet-ref/\n\n\nBackgroundImage in create layout\n\n#from PySide2.QtWidgets import QLabel, QMainWindow, QApplication, QWidget, QVBoxLayout\n#from PySide2.QtGui import QPixmap\n\n        self.setWindowTitle(Title)\n        self.setFixedSize(485,565)\n\n\n        #imagePath  = cmds.internalVar(usd = True) + ResourcesPath\n        \n        #label = QLabel(self)\n        #pixmap = QPixmap(imagePath+'Background.png')\n        #label.setPixmap(pixmap)\n        #self.resize(pixmap.width(), pixmap.height())\n\n        self.init_ui()\n\n        \n\n"


def run_script():
    exec(compile("Title = 'NAME HERE'\nFolder = 'FOLDER'\nUI_File = 'UI_NAME.ui'\nResourcesPath = Folder + '/Resources/'\ntry:\n    UIName_ui.close()\n    UIName_ui.deleteLater()\nexcept:\n    pass\nUIName_ui = UIName()\nUIName_ui.show()", __file__, "exec"), globals())
