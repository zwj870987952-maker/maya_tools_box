import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

try:
    from PySide6 import QtWidgets, QtGui, QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from shiboken2 import wrapInstance

all_model_panels = cmds.getPanel(type="modelPanel")

for Panel in all_model_panels:
    if Panel and cmds.getPanel(typeOf=Panel) == "modelPanel":
        nurbsC = cmds.modelEditor(Panel, q=1, nurbsCurves=1)
        if nurbsC == True:
            cmds.modelEditor(Panel, e=True, allObjects=False)
            cmds.modelEditor(Panel, e=True, polymeshes=True)
            cmds.modelEditor(Panel, e=True, nurbsSurfaces=True)
            cmds.modelEditor(Panel, e=True, subdivSurfaces=True)
        else:
            cmds.modelEditor(Panel, e=True, allObjects=False)
            cmds.modelEditor(Panel, e=True, polymeshes=True)
            cmds.modelEditor(Panel, e=True, nurbsSurfaces=True)
            cmds.modelEditor(Panel, e=True, nurbsCurves=1)
            cmds.modelEditor(Panel, e=True, subdivSurfaces=True)
            cmds.modelEditor(Panel, e=True, manipulators=True)
            cmds.modelEditor(Panel, e=True, textures=True)  
            cmds.modelEditor(Panel, e=True, motionTrails=True)	
            mel.eval("modelEditor -e -controllers true {0}" .format(Panel))

show_copied_key_time()



def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QMainWindow)

class CopiedKeyTimeUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(CopiedKeyTimeUI, self).__init__(parent or get_maya_main_window())

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.95)

        self.setFixedSize(300, 220)

        self.setStyleSheet("""
            QWidget {
                background-color: rgba(12, 15, 20, 165);
                border: 1px solid rgba(100, 255, 150, 80);
                border-radius: 14px;
            }
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', 'Helvetica Neue', sans-serif;
                font-size: 22px;
                font-weight: 800;
                letter-spacing: 1px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton {
                background: none;
                border: none;
                color: #888;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #ff5555;
            }
        """)

        self.create_ui()
        self.installEventFilter(self)
        self.show()

    def create_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        label = QtWidgets.QLabel("Animation Mode")

        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addStretch()

        layout.addLayout(top_layout)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()

    def fade_out_and_close(self, delay=1200):
        QtCore.QTimer.singleShot(delay, self._fade_out)

    def _fade_out(self):
        self.animation = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(900)
        self.animation.setStartValue(0.95)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

def show_copied_key_time():
    ui = CopiedKeyTimeUI()
    ui.fade_out_and_close()