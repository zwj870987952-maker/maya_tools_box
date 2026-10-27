from __future__ import absolute_import
from __future__ import print_function
from six.moves import range
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2 import QtUiTools
    from shiboken2 import wrapInstance
    from PySide2 import __version__
except ImportError:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide import QtUiTools
    from shiboken import wrapInstance
    from PySide import __version__
    from shiboken import wrapInstance

import webbrowser, maya.OpenMayaUI as omui, maya.OpenMaya as om, maya.cmds as cmds
from functools import partial
import os, json
mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)

class CgShake(QMainWindow):

    def __init__(self, parent=mayaMainWindow):
        super(CgShake, self).__init__(parent)
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.path = self.path.replace('\\', '/')
        self.imagePath = self.path + '/images/'
        self.cachePath = self.path + '/cache/'
        self.presetsPath = self.path + '/presets/'
        self.setUI()
        self.setWidgetStyleSheet()
        self.populatePresets()
        self.attemptPluginLoad()

    def attemptPluginLoad(self):
        try:
            if not cmds.pluginInfo('animImportExport.mll', q=True, l=True):
                cmds.loadPlugin('animImportExport.mll')
        except:
            cmds.warning('Could not load animImportExport.mll plugin! Please try to load it manually through the Plugin Manager...')

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
        self.byFrameSpinBox.setValue(1.0)
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
        self.range_ctr = cmds.gradientControlNoAttr('shakeFalloffCurve', h=90)
        cmds.gradientControlNoAttr(self.range_ctr, e=True, optionVar='shakeFalloffCurveOptionVar')
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
        self.applyButton = QPushButton('Apply to selected object(s)')
        self.applyButton.setMinimumHeight(24)
        applyLayout.addWidget(self.useCacheCheckBox)
        applyLayout.addWidget(self.overwriteCheckBox)
        applyLayout.addWidget(self.applyButton)
        mainLayout.addWidget(applyWidget)
        self.applyButton.clicked.connect(partial(self.applyShake))
        cmds.gradientControlNoAttr(self.range_ctr, e=True, asString='0,1,3,1,0,3')

    def savePreset(self):
        text, okPressed = QInputDialog.getText(self, 'Preset Name', 'Enter name (Please no spaces)', QLineEdit.Normal, 'Preset1')
        if okPressed and text != '':
            values = cmds.gradientControlNoAttr(self.range_ctr, query=True, asString=True)
            presetDict = {}
            presetDict['Frame'] = self.byFrameSpinBox.value()
            presetDict['TX'] = self.txAmountSpinBox.value()
            presetDict['TY'] = self.tyAmountSpinBox.value()
            presetDict['TZ'] = self.tzAmountSpinBox.value()
            presetDict['RX'] = self.rxAmountSpinBox.value()
            presetDict['RY'] = self.ryAmountSpinBox.value()
            presetDict['RZ'] = self.rzAmountSpinBox.value()
            presetDict['Points'] = values
            filename = self.presetsPath + text + '.cgsk'
            if filename:
                with open(filename, 'w') as (json_data):
                    json.dump(presetDict, json_data, indent=4, sort_keys=True)
        self.populatePresets()

    def loadPreset(self, preset):
        if preset == 'Default':
            self.byFrameSpinBox.setValue(1)
            self.txAmountSpinBox.setValue(5)
            self.tyAmountSpinBox.setValue(5)
            self.tzAmountSpinBox.setValue(5)
            self.rxAmountSpinBox.setValue(5)
            self.ryAmountSpinBox.setValue(5)
            self.rzAmountSpinBox.setValue(5)
            cmds.gradientControlNoAttr(self.range_ctr, e=True, asString='0,1,3,1,0,3')
        else:
            filename = self.presetsPath + preset
            if filename:
                with open(filename, 'r') as (json_version_data):
                    presetDict = json.load(json_version_data)
                    self.byFrameSpinBox.setValue(presetDict['Frame'])
                    self.txAmountSpinBox.setValue(presetDict['TX'])
                    self.tyAmountSpinBox.setValue(presetDict['TY'])
                    self.tzAmountSpinBox.setValue(presetDict['TZ'])
                    self.rxAmountSpinBox.setValue(presetDict['RX'])
                    self.ryAmountSpinBox.setValue(presetDict['RY'])
                    self.rzAmountSpinBox.setValue(presetDict['RZ'])
                    cmds.gradientControlNoAttr(self.range_ctr, e=True, asString=presetDict['Points'])

    def populatePresets(self):
        self.presetComboBox.clear()
        self.presetComboBox.addItem('Default')
        presets = os.listdir(self.presetsPath)
        self.presetComboBox.blockSignals(True)
        for preset in presets:
            print(preset)
            self.presetComboBox.addItem(preset)

        self.presetComboBox.blockSignals(False)

    def checkDocumentation(self):
        webbrowser.open('https://trikingo.com/cgshake-documentation/')

    def overwriteWarning(self):
        if self.overwriteCheckBox.isChecked() == True:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText('Please ensure you are not in your Base Animation layer.\r\nThis option will remove any key from your selected object within the active layer.\r\nIf you are not sure about this, create a new animation layer now!')
            msg.setWindowTitle('Important!')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def clearAnimationLayer(self):
        getSelection = cmds.ls(selection=True)
        if getSelection:
            cmds.cutKey(getSelection[0], clear=True)

    def applyShake(self):
        if self.overwriteCheckBox.isChecked() == True:
            self.clearAnimationLayer()
        allow = True
        import random
        getSelection = cmds.ls(selection=True)
        txValues = []
        tyValues = []
        tzValues = []
        rxValues = []
        ryValues = []
        rzValues = []
        if getSelection:
            if self.useCacheCheckBox.isChecked() == True:
                if cmds.attributeQuery('cache', node=getSelection[0], exists=True):
                    self.restoreCache()
                else:
                    buttonReply = QMessageBox.question(self, 'No cache exists', 'No cache was found!\r\nTo use the cache feature, please select an object and press the\r\nCache button in the settings area.\r\n\r\nDo you still want to continue?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if buttonReply == QMessageBox.Yes:
                        allow = True
                    else:
                        allow = False
            if allow == True:
                cmds.undoInfo(openChunk=True)
                startFrame = cmds.playbackOptions(q=True, min=True)
                endFrame = cmds.playbackOptions(q=True, max=True) + 1.0
                byFrame = self.byFrameSpinBox.value()
                for frame in range(int(startFrame), int(endFrame), byFrame):
                    txValues.append(cmds.getAttr(getSelection[0] + '.tx', time=frame))
                    tyValues.append(cmds.getAttr(getSelection[0] + '.ty', time=frame))
                    tzValues.append(cmds.getAttr(getSelection[0] + '.tz', time=frame))
                    rxValues.append(cmds.getAttr(getSelection[0] + '.rx', time=frame))
                    ryValues.append(cmds.getAttr(getSelection[0] + '.ry', time=frame))
                    rzValues.append(cmds.getAttr(getSelection[0] + '.rz', time=frame))

                counter = 0
                for frame in range(int(startFrame), int(endFrame), byFrame):
                    normValue = (frame - startFrame) / (endFrame - startFrame) * 1.0
                    value = cmds.gradientControlNoAttr(self.range_ctr, q=True, valueAtPoint=normValue)
                    getTx = txValues[counter] + value * random.uniform(0, self.txAmountSpinBox.value())
                    getTy = tyValues[counter] + value * random.uniform(0, self.tyAmountSpinBox.value())
                    getTz = tzValues[counter] + value * random.uniform(0, self.tzAmountSpinBox.value())
                    getRx = rxValues[counter] + value * random.uniform(0, self.rxAmountSpinBox.value())
                    getRy = ryValues[counter] + value * random.uniform(0, self.ryAmountSpinBox.value())
                    getRz = rzValues[counter] + value * random.uniform(0, self.rzAmountSpinBox.value())
                    cmds.currentTime(frame)
                    cmds.setAttr(getSelection[0] + '.rx', getRx)
                    cmds.setAttr(getSelection[0] + '.ry', getRy)
                    cmds.setAttr(getSelection[0] + '.rz', getRz)
                    cmds.setAttr(getSelection[0] + '.translate', getTx, getTy, getTz, type='double3')
                    keyableAttributes = []
                    if self.txAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('tx')
                    if self.tyAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('ty')
                    if self.tzAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('tz')
                    if self.rxAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('rx')
                    if self.ryAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('ry')
                    if self.rzAmountSpinBox.value() != 0.0:
                        keyableAttributes.append('rz')
                    cmds.setKeyframe(getSelection[0], at=keyableAttributes)
                    counter += 1

                cmds.undoInfo(closeChunk=True)

    def setWidgetStyleSheet(self):
        self.setStyleSheet('QMainWindow {background-color: #3F3D36 ; background-image: url(' + self.imagePath + 'romboBack.png); border-image: url(' + self.imagePath + 'vignetteFrame)}')
        self.frameRangeGroupBox.setStyleSheet('QFrame{background-color: None;} QGroupBox { background-color: rgba(90, 90, 90, 40%); padding-top:5px; border: 1px solid #131213; border-radius: 6px; margin-top: 0.5em;} QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;} QGroupBox::indicator {width: 0px; height: 0px;} .QPushButton{background-color: #403C44; border-radius:2px; border: 1px solid #171619;} .QPushButton:hover{background-color: #615A67; } .QPushButton:pressed{background-color: #2C292F; } QComboBox {background-color: #2E414A; border-radius:2px; border: 1px solid #25482D;} ')
        self.curvesGroupBox.setStyleSheet('QFrame{background-color: None;} QGroupBox { background-color: rgba(90, 90, 90, 40%); padding-top:5px; border: 1px solid #131213; border-radius: 6px; margin-top: 0.5em;} QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;} QGroupBox::indicator {width: 0px; height: 0px;} .QPushButton{background-color: #403C44; border-radius:2px; border: 1px solid #171619;} .QPushButton:hover{background-color: #615A67; } .QPushButton:pressed{background-color: #2C292F; } QComboBox {background-color: #2E414A; border-radius:2px; border: 1px solid #25482D;} ')
        self.mayaQTObj.setStyleSheet(' QWidget {margin:0px; background-color: rgba(50,40,40, 0%);}')
        self.applyButton.setStyleSheet('.QPushButton { padding:4px; background-color: #3B5735; border-radius:6px; border: 1px solid #233120;} .QPushButton:hover{background-color: #627B5E; } .QPushButton:pressed{background-color: #233120;}')
        self.cacheButton.setStyleSheet('.QPushButton { padding:4px; background-color: #3B5735; border-radius:6px; border: 1px solid #233120;} .QPushButton:hover{background-color: #627B5E; } .QPushButton:pressed{background-color: #233120;}')
        self.restoreButton.setStyleSheet('.QPushButton { padding:4px; background-color: #605D4D; border-radius:6px; border: 1px solid #2E2D25;} .QPushButton:hover{background-color: #777562;} .QPushButton:pressed{background-color: #48463B;}')
        self.menubar.setStyleSheet('QMenuBar {background: #262520;}')
        self.presetComboBox.setStyleSheet('QComboBox {background-color: #605D4D; border-radius:2px; border: 1px solid #111; padding:2px;}')

    def cacheObject(self):
        getSelection = cmds.ls(selection=True)
        if getSelection:
            if cmds.attributeQuery('cache', node=getSelection[0], exists=True):
                print('Attribute already exists!')
            else:
                cmds.addAttr(getSelection[0], ln='cache', dataType='string')
            cmds.file('%stempCache.anim' % self.cachePath, force=True, options='precision=17;intValue=17;nodeNames=1;verboseUnits=0;whichRange=1;range=1:120;options=keys;hierarchy=none;controlPoints=0;shapes=1;helpPictures=0;useChannelBox=0;copyKeyCmd=-animation objects -option keys -hierarchy none -controlPoints 0 -shape 1 ', type='animExport', pr=True, es=True)
            cmds.setAttr(getSelection[0] + '.cache', '%stempCache.anim' % self.cachePath, type='string')
            cmds.warning('Cache was successfully generated!')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Cache successfull!')
            msg.setWindowTitle('Success!')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def restoreCache(self):
        getSelection = cmds.ls(selection=True)
        if getSelection:
            if cmds.attributeQuery('cache', node=getSelection[0], exists=True):
                getCache = cmds.getAttr('%s.cache' % getSelection[0])
                self.clearAnimationLayer()
                cmds.file(getCache, i=True, type='animImport', ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, options='targetTime=4;copies=1;option=replace;pictures=0;connect=0;', pr=True, importTimeRange='combine')
                cmds.select(getSelection[0])
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText('No cache found!')
                msg.setWindowTitle('Important!')
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()


def run():
    CgShake().show()