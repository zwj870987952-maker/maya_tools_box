'''TB Animation Tools is a toolset for animators

*******************************************************************************
    License and Copyright
    Copyright 2020-Tom Bailey
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    send issues/ requests to brimblashman@gmail.com
    visit https://tbanimtools.blogspot.com/ for "more info"

    usage


*******************************************************************************
'''
# Modified staging installer, 2026-10-01: Qt6/Python3 compatibility,
# fixed offline ZIP, no overwrite, explicit registration/startup separation.
# Original copyright Tom Bailey 2020; original LGPL v3-or-later notice retained
# in upstream/tbAnimToolsInstaller.py.original. Full suite GPL LICENSE included.
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omUI
qt_major = int(cmds.about(qtVersion=True).split('.')[0])
if qt_major >= 6:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from shiboken6 import wrapInstance
elif qt_major >= 5:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from shiboken2 import wrapInstance
else:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

styleSheet = '''
QLabel
{
    font-weight: bold; font-size: 18px;
}
QPushButton
{
    color: #b1b1b1;
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
    border-width: 1px;
    border-color: #1e1e1e;
    border-style: solid;
    border-radius: 6;
    padding: 3px;
    font-size: 12px;
    padding-left: 5px;
    padding-right: 5px;
}

QPushButton:pressed
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
}

QPushButton:hover
{
    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
}
'''

class tbAnimToolsInstaller(QDialog):
    oldPos = None

    def __init__(self, parent=None):
        if cmds.about(batch=True):
            raise RuntimeError('Open the installer only in interactive Maya')
        if parent is None:
            pointer = omUI.MQtUtil.mainWindow()
            if not pointer:
                raise RuntimeError('Maya main window is unavailable')
            parent = wrapInstance(int(pointer), QWidget)
        super(tbAnimToolsInstaller, self).__init__(parent=parent)
        from .tool import TBAnimToolsTool
        self.adapter = TBAnimToolsTool()
        self.datUrl = 'https://api.github.com/repos/tb-animator/tbAnimTools'
        self.master_url = 'https://raw.githubusercontent.com/tb-animator/tbtools/master/'
        self.latestZip = 'bundled fixed snapshot; network disabled'
        self.realPath = os.path.realpath(__file__)
        self.basename = os.path.basename(__file__)
        self.base_dir = os.path.normpath(os.path.dirname(__file__))
        self.subFolder = 'tbAnimTools'
        self.defaultInstallPath = os.path.join(self.base_dir, self.subFolder)
        self.versionDataFile = None
        self.dateFormat = '%Y-%m-%dT%H:%M'
        self.uiDateFormat = '%Y-%m-%d'
        self.timeFormat = '%H:%M'

        self.installPath = None
        # self.stylesheet = .getStyleSheet()
        # self.setStyleSheet(self.stylesheet)

        self.setWindowTitle("HELLO!")
        self.setWindowOpacity(1.0)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.windowFlags()
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.setFixedSize(660, 290)
        self.mainLayout = QVBoxLayout()
        self.layout = QVBoxLayout()

        self.titleText = QLabel('tbAnimTools · pinned offline installer')
        self.titleText.setStyleSheet(styleSheet)
        self.titleText.setAlignment(Qt.AlignCenter)
        self.infoText = QLabel('Tom Bailey · LGPL notice / upstream GPL LICENSE · no warranty\nChoose a NEW directory. Activation changes Maya settings and commands.')
        self.installButton = QPushButton('1. Install complete files (no activation)')
        self.installButton.setStyleSheet(styleSheet)
        self.installButton.clicked.connect(self.installTools)

        self.filePathLayout = QHBoxLayout()
        self.pathLabel = QLabel('Install to ::')
        self.pathLineEdit = QLineEdit(self.defaultInstallPath)
        self.cle_action_pick = self.pathLineEdit.addAction(QIcon(":/folder-open.png"),
                                                              QLineEdit.TrailingPosition)
        self.cle_action_pick.setToolTip(
            'Pick destination folder to install tbAnimTools to')
        self.cle_action_pick.triggered.connect(self.pickInstallFolder)
        self.filePathLayout.addWidget(self.pathLabel)
        self.filePathLayout.addWidget(self.pathLineEdit)
        # self.infoText.setStyleSheet(self.stylesheet)

        self.mainLayout.addWidget(self.titleText)
        self.mainLayout.addLayout(self.layout)
        self.layout.addWidget(self.infoText)

        self.layout.addLayout(self.filePathLayout)
        self.layout.addWidget(self.installButton)

        self.registerButton = QPushButton('2. Register module (new tbAnimTools.mod only)')
        self.launchButton = QPushButton('3. Launch original suite in this Maya session')
        self.registerButton.clicked.connect(lambda: self.activate('register_module'))
        self.launchButton.clicked.connect(lambda: self.activate('launch_native'))
        self.layout.addWidget(self.registerButton)
        self.layout.addWidget(self.launchButton)
        self.setLayout(self.mainLayout)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        lineColor = QColor(68, 68, 68, 128)

        # qp.setCompositionMode(qp.CompositionMode_Clear)
        qp.setCompositionMode(qp.CompositionMode_Source)
        qp.setRenderHint(QPainter.Antialiasing)

        qp.setPen(QPen(QBrush(lineColor), 2))
        grad = QLinearGradient(200, 0, 200, 32)
        grad.setColorAt(0, QColor("#323232"))
        grad.setColorAt(0.1, QColor("#373737"))
        grad.setColorAt(1, QColor("#323232"))
        qp.setBrush(QBrush(grad))
        qp.drawRoundedRect(self.rect(), 16, 16)
        qp.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        return super(tbAnimToolsInstaller, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        self.oldPos = (event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos())

    def mouseMoveEvent(self, event):
        if not self.oldPos:
            return
        delta = QPoint((event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos()) - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = (event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos())

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def createVersionFile(self):
            # The unchanged upstream version/config files must stay unchanged.
            # Our separate receipt already records exact commit and file hashes.
            from .files import RECEIPT
            self.versionDataFile = os.path.join(self.installPath, RECEIPT)
            if not os.path.isfile(self.versionDataFile):
                raise RuntimeError('Installation receipt is missing')

    def pickInstallFolder(self):
        self.installPath = cmds.fileDialog2(caption='tbAnimTools :: Choose installation directory',
                                          fileFilter='',
                                          dialogStyle=1,
                                          fileMode=3)
        if not self.installPath:
            return
        self.installPath = os.path.join(self.installPath[0], self.subFolder)
        self.pathLineEdit.setText(self.installPath)

    def installTools(self):
            self.installPath = self.pathLineEdit.text()
            if self.download_project_files():
                self.createVersionFile()
                self.infoText.setText('Complete files installed. Module registration and suite startup are separate buttons.')

    def download_project_files(self):
            result = self.adapter.run(action='install_files', destination=self.installPath)
            if not result.success:
                QMessageBox.warning(self, 'Install failed', result.message)
                return False
            return True

    def installModule(self):
            return self.activate('register_module')

    def activate(self, action):
        self.installPath = self.pathLineEdit.text()
        message = ('Activation writes a new module file and disables automatic upstream updates. '
                   'Native startup may write preferences, runtime commands, menus, plugin state and hotkeys. '
                   'Maya Undo cannot revert these changes. Back up your Maya profile first. Continue?')
        if QMessageBox.question(self, 'Explicit suite activation', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return False
        result = self.adapter.run(action=action, destination=self.installPath, acknowledge_external_effects=True)
        if not result.success:
            QMessageBox.warning(self, 'Activation failed', result.message)
            return False
        self.infoText.setText(result.message + '\nVerify deferred startup in Script Editor.')
        return True

_WINDOW = None

def show_ui(parent=None):
    global _WINDOW
    if _WINDOW is not None:
        try:
            _WINDOW.close()
        except RuntimeError:
            pass
    _WINDOW = tbAnimToolsInstaller(parent)
    _WINDOW.show()
    return _WINDOW

def onMayaDroppedPythonFile(*args):
    return show_ui()
