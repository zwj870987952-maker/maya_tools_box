from PySide2 import QtGui,QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel
import pymel.core as pm

#QT WIndow!

Title = 'NAME HERE'
Folder = 'FOLDER'
UI_File = 'UI_NAME.ui'
ResourcesPath =  Folder + '/Resources/'

def maya_main_window():
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class UIName(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(UIName, self).__init__(parent)

        self.setWindowTitle(Title)
        self.setFixedSize(682,590)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        
        UIPath  = cmds.internalVar(usd = True) + Folder + '/'
        f = QtCore.QFile(UIPath + UI_File)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        
        self.ui.layout().setContentsMargins(3, 3, 3, 3)          
      
        imagePath  = cmds.internalVar(usd = True) + ResourcesPath
        #self.ui.ButtonName.setIcon(QtGui.QIcon(imagePath+'Locator.png'))

    def create_connections(self):

        def Demo(self):
            print 'This is a DemoFunc'
        
        #self.ui.ButtonName.clicked.connect(self.Demo)
        #self.ui.ButtonName.clicked.connect(lambda: print 'this is lambda')
        
                
if __name__ == "__main__":

    try:
        UIName_ui.close() # pylint: disable=E0601
        UIName_ui.deleteLater()
    except:
        pass
    UIName_ui = UIName()
    UIName_ui.show()



'''
Stylesheets:

https://renderdemartes.com/2019/10/09/qt-stylesheet-ref/


BackgroundImage in create layout

#from PySide2.QtWidgets import QLabel, QMainWindow, QApplication, QWidget, QVBoxLayout
#from PySide2.QtGui import QPixmap

        self.setWindowTitle(Title)
        self.setFixedSize(485,565)


        #imagePath  = cmds.internalVar(usd = True) + ResourcesPath
        
        #label = QLabel(self)
        #pixmap = QPixmap(imagePath+'Background.png')
        #label.setPixmap(pixmap)
        #self.resize(pixmap.width(), pixmap.height())

        self.init_ui()

        

'''