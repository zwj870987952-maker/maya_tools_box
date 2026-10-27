from maya_toolkit.core.ui_base import QtCore, QtGui, QtWidgets, Qt, get_maya_main_window
from .files import default_data_root
from . import bridge
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os, webbrowser
from functools import partial
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken2 import wrapInstance
globals().update({name: getattr(module, name) for module in (QtWidgets, QtGui, QtCore) for name in dir(module) if name.startswith('Q')})

class CgShake(QMainWindow):

    def __init__(self, parent=None):
        if parent is None:
            parent = get_maya_main_window()
        super(CgShake, self).__init__(parent)
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.path = self.path.replace('\\', '/')
        self.imagePath = self.path + '/images/'
        self.cachePath = str(default_data_root() / 'cache') + '/'
        self.presetsPath = str(default_data_root() / 'presets') + '/'
        self.setUI()
        self.setWidgetStyleSheet()
        self.populatePresets()
        self.attemptPluginLoad()

    def attemptPluginLoad(self):
        from .files import plugin_loaded
        if not plugin_loaded():
            cmds.warning('Cache/Restore requires manually loaded animImportExport; opening/apply do not load it.')

    def convertPathToPySideObject(self, name):
        ptr = omui.MQtUtil.findControl(name)
        if ptr is None:
            ptr = omui.MQtUtil.findLayout(name)
        if ptr is None:
            ptr = omui.MQtUtil.findMenuItem(name)
        if ptr is not None:
            return wrapInstance(int(ptr), QWidget)
        else:
            return

    def setUI(self):
        self.setWindowTitle('CgShake 1.5')
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu(QIcon('%s/icon.png' % self.imagePath), '')
        fileMenu = self.menubar.addMenu('Presets')
        fileMenu.addAction('Save', self.savePreset)
        fileMenu = self.menubar.addMenu('Help')
        fileMenu.addAction('Check Documentation', self.checkDocumentation)
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(mainLayout)
        self.presetComboBox = QComboBox()
        self.presetComboBox.currentTextChanged.connect(self.loadPreset)
        self.frameRangeGroupBox = QGroupBox('Settings')
        self.frameRangeGroupBox.setMaximumHeight(130)
        self.frameRangeGroupBox.setMinimumHeight(130)
        frameGridLayout = QGridLayout()
        self.frameRangeGroupBox.setLayout(frameGridLayout)
        byFrameLabel = QLabel('Frame')
        self.byFrameSpinBox = QSpinBox()
        self.byFrameSpinBox.setMinimum(1)
        self.byFrameSpinBox.setValue(1)
        amountLabel = QLabel('Amount')
        txAmountLabel = QLabel('Tx')
        self.txAmountSpinBox = QDoubleSpinBox()
        self.txAmountSpinBox.setValue(5.0)
        tyAmountLabel = QLabel('Ty')
        self.tyAmountSpinBox = QDoubleSpinBox()
        self.tyAmountSpinBox.setValue(5.0)
        tzAmountLabel = QLabel('Tz')
        self.tzAmountSpinBox = QDoubleSpinBox()
        self.tzAmountSpinBox.setValue(5.0)
        rxAmountLabel = QLabel('Rx')
        self.rxAmountSpinBox = QDoubleSpinBox()
        self.rxAmountSpinBox.setValue(5.0)
        ryAmountLabel = QLabel('Ry')
        self.ryAmountSpinBox = QDoubleSpinBox()
        self.ryAmountSpinBox.setValue(5.0)
        rzAmountLabel = QLabel('Rz')
        self.rzAmountSpinBox = QDoubleSpinBox()
        self.rzAmountSpinBox.setValue(5.0)
        self.cacheButton = QPushButton('Cache')
        self.restoreButton = QPushButton('Restore')
        self.cacheButton.setToolTip('Cache the current anim layer of the selected object.')
        self.restoreButton.setToolTip('Restore cache if it exists.')
        self.cacheButton.clicked.connect(self.cacheObject)
        self.restoreButton.clicked.connect(self.restoreCache)
        frameGridLayout.addWidget(byFrameLabel, 0, 0)
        frameGridLayout.addWidget(self.byFrameSpinBox, 0, 1)
        frameGridLayout.addWidget(self.cacheButton, 0, 3)
        frameGridLayout.addWidget(self.restoreButton, 0, 5)
        frameGridLayout.addWidget(amountLabel, 1, 0)
        frameGridLayout.addWidget(txAmountLabel, 2, 0)
        frameGridLayout.addWidget(self.txAmountSpinBox, 2, 1)
        frameGridLayout.addWidget(tyAmountLabel, 2, 2)
        frameGridLayout.addWidget(self.tyAmountSpinBox, 2, 3)
        frameGridLayout.addWidget(tzAmountLabel, 2, 4)
        frameGridLayout.addWidget(self.tzAmountSpinBox, 2, 5)
        frameGridLayout.addWidget(rxAmountLabel, 3, 0)
        frameGridLayout.addWidget(self.rxAmountSpinBox, 3, 1)
        frameGridLayout.addWidget(ryAmountLabel, 3, 2)
        frameGridLayout.addWidget(self.ryAmountSpinBox, 3, 3)
        frameGridLayout.addWidget(rzAmountLabel, 3, 4)
        frameGridLayout.addWidget(self.rzAmountSpinBox, 3, 5)
        self.range_ctr = cmds.gradientControlNoAttr('mtbCGShakeFalloffCurve', h=90)
        cmds.gradientControlNoAttr(self.range_ctr, e=True, optionVar='mtbCGShakeFalloffCurveOptionVar')
        self.mayaQTObj = self.convertPathToPySideObject(self.range_ctr)
        self.curvesGroupBox = QGroupBox('Curves')
        curvesLayout = QHBoxLayout()
        curvesLayout.setContentsMargins(0, 0, 0, 0)
        self.curvesGroupBox.setLayout(curvesLayout)
        curvesLayout.addWidget(self.mayaQTObj)
        mainLayout.addWidget(self.presetComboBox)
        mainLayout.addWidget(self.frameRangeGroupBox)
        mainLayout.addWidget(self.curvesGroupBox)
        applyWidget = QWidget()
        applyWidget.setMaximumHeight(30)
        applyLayout = QHBoxLayout()
        applyLayout.setAlignment(Qt.AlignRight)
        applyLayout.setContentsMargins(0, 0, 0, 0)
        applyLayout.setSpacing(0)
        applyWidget.setLayout(applyLayout)
        self.overwriteCheckBox = QCheckBox('Overwrite')
        self.overwriteCheckBox.clicked.connect(self.overwriteWarning)
        self.useCacheCheckBox = QCheckBox('Use cache')
        self.applyButton = QPushButton('Apply to first selected object')
        self.applyButton.setMinimumHeight(24)
        applyLayout.addWidget(self.useCacheCheckBox)
        applyLayout.addWidget(self.overwriteCheckBox)
        applyLayout.addWidget(self.applyButton)
        mainLayout.addWidget(applyWidget)
        self.applyButton.clicked.connect(partial(self.applyShake))
        cmds.gradientControlNoAttr(self.range_ctr, e=True, asString='0,1,3,1,0,3')

    def savePreset(self, *_):
        return bridge.save_preset(self)

    def loadPreset(self, preset):
        return bridge.load_preset(self, preset)

    def populatePresets(self):
        self.presetComboBox.blockSignals(True)
        self.presetComboBox.clear()
        self.presetComboBox.addItem('Default')
        if os.path.isdir(self.presetsPath):
            for name in sorted(os.listdir(self.presetsPath)):
                if name.endswith('.cgsk'):
                    self.presetComboBox.addItem(name)
        self.presetComboBox.blockSignals(False)

    def checkDocumentation(self):
        webbrowser.open('https://trikingo.com/cgshake-documentation/')

    def overwriteWarning(self, *_):
        if self.overwriteCheckBox.isChecked():
            QMessageBox.warning(self, 'Overwrite', 'Deletes object animation keys without a frame restriction; layer scope must be checked on a copy. Scene Undo cannot remove cache/preset files.')

    def clearAnimationLayer(self):
        return bridge.clear(self)

    def applyShake(self, *_):
        return bridge.apply(self)

    def setWidgetStyleSheet(self):
        self.setStyleSheet('QMainWindow {background-color: #3F3D36 ; background-image: url(' + self.imagePath + 'romboBack.png); border-image: url(' + self.imagePath + 'vignetteFrame.png)}')
        self.frameRangeGroupBox.setStyleSheet('QFrame{background-color: None;} QGroupBox { background-color: rgba(90, 90, 90, 40%); padding-top:5px; border: 1px solid #131213; border-radius: 6px; margin-top: 0.5em;} QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;} QGroupBox::indicator {width: 0px; height: 0px;} .QPushButton{background-color: #403C44; border-radius:2px; border: 1px solid #171619;} .QPushButton:hover{background-color: #615A67; } .QPushButton:pressed{background-color: #2C292F; } QComboBox {background-color: #2E414A; border-radius:2px; border: 1px solid #25482D;} ')
        self.curvesGroupBox.setStyleSheet('QFrame{background-color: None;} QGroupBox { background-color: rgba(90, 90, 90, 40%); padding-top:5px; border: 1px solid #131213; border-radius: 6px; margin-top: 0.5em;} QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;} QGroupBox::indicator {width: 0px; height: 0px;} .QPushButton{background-color: #403C44; border-radius:2px; border: 1px solid #171619;} .QPushButton:hover{background-color: #615A67; } .QPushButton:pressed{background-color: #2C292F; } QComboBox {background-color: #2E414A; border-radius:2px; border: 1px solid #25482D;} ')
        self.mayaQTObj.setStyleSheet(' QWidget {margin:0px; background-color: rgba(50,40,40, 0%);}')
        self.applyButton.setStyleSheet('.QPushButton { padding:4px; background-color: #3B5735; border-radius:6px; border: 1px solid #233120;} .QPushButton:hover{background-color: #627B5E; } .QPushButton:pressed{background-color: #233120;}')
        self.cacheButton.setStyleSheet('.QPushButton { padding:4px; background-color: #3B5735; border-radius:6px; border: 1px solid #233120;} .QPushButton:hover{background-color: #627B5E; } .QPushButton:pressed{background-color: #233120;}')
        self.restoreButton.setStyleSheet('.QPushButton { padding:4px; background-color: #605D4D; border-radius:6px; border: 1px solid #2E2D25;} .QPushButton:hover{background-color: #777562;} .QPushButton:pressed{background-color: #48463B;}')
        self.menubar.setStyleSheet('QMenuBar {background: #262520;}')
        self.presetComboBox.setStyleSheet('QComboBox {background-color: #605D4D; border-radius:2px; border: 1px solid #111; padding:2px;}')

    def cacheObject(self, *_):
        return bridge.cache(self)

    def restoreCache(self, *_):
        return bridge.restore(self)

    def closeEvent(self, event):
        if cmds.control(self.range_ctr, exists=True):
            cmds.deleteUI(self.range_ctr)
        super(CgShake, self).closeEvent(event)
