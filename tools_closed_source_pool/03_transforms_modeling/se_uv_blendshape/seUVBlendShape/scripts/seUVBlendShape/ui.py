'''
This is a UI module for the seUVBlendShape plugin which provides
visual tools to make working with the deformer easier.

This is Qt Window and uses PySide which comes with Maya.

>>> import seUVBlendShape
>>> seUVBlendShape.launchEditor()
'''
from __future__ import absolute_import
import functools
import sys
if sys.version_info > (3,):
    long = int

from maya import OpenMayaUI, cmds, mel
from .Qt import QtWidgets, QtCore, QtGui

_pyside2 = int(cmds.about(qtVersion=True).split('.')[0]) == 5
# # update importing for version 5 of Qt
if _pyside2:
    from shiboken2 import wrapInstance
else:
    from shiboken import wrapInstance

from . import core

def launchEditor():
    '''
    Launch a new editor for the seUVBlendShape deformer.

    :returns: new editor instance.
    :rtype: QtWidgets.QMainWindow
    '''
    core.loadPlugin()

    mayaWindowPtr = OpenMayaUI.MQtUtil.mainWindow()

    mayaWindowWidget = wrapInstance(long(mayaWindowPtr), QtWidgets.QWidget)

    editor = SEUVBlendShapeMainWindow(mayaWindowWidget)
    editor.show()
    return editor

class SEUVBlendShapeMainWindow(QtWidgets.QMainWindow):
    '''
    Main window for the seUVBlendShape Editor. You can use the :py:func:`launchEditor`
    function to easily launch a new editor window.
    '''

    def __init__(self, parent=None):
        super(SEUVBlendShapeMainWindow, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle('seUVBlendShape Editor')

        self._activeDeformer = None

        self._setupUI()

        self.refreshDeformerList()

        self.resize(425, 450)

    def _setupUI(self):
        '''Setup the window'''
        self._createToolBar()
        self._createCentralWidgets()

    def _createCentralWidgets(self):
        '''Create the central widgets'''        
        # central widget
        centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(centralWidget)

        mainLayout = QtWidgets.QVBoxLayout(centralWidget)

        # deformer list
        deformerLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(deformerLayout)

        deformerLabel = QtWidgets.QLabel('Deformer:', self)
        deformerLayout.addWidget(deformerLabel)

        self.deformerComboBox = QtWidgets.QComboBox(self)
        self.deformerComboBox.setMinimumWidth(100)
        self.deformerComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.deformerComboBox.currentIndexChanged['QString'].connect(self.loadDeformer)
        deformerLayout.addWidget(self.deformerComboBox)

        refreshBtn = QtWidgets.QPushButton('Refresh', self)
        refreshBtn.clicked.connect(self.refreshDeformerList)
        deformerLayout.addWidget(refreshBtn)

        selectBtn = QtWidgets.QPushButton('Select', self)
        selectBtn.clicked.connect(self.selectDeformer)
        deformerLayout.addWidget(selectBtn)

        deleteBtn = QtWidgets.QPushButton('Delete', self)
        deleteBtn.clicked.connect(self.deleteDeformer)
        deformerLayout.addWidget(deleteBtn)

        deformerLayout.addStretch(0)

        # target list
        targetAttributeSplitter = QtWidgets.QSplitter(self)
        self.targetListWidget = QtWidgets.QListWidget(targetAttributeSplitter)
        self.targetListWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.targetListWidget.itemSelectionChanged.connect(self._onTargetSelectionChange)
        targetAttributeSplitter.addWidget(self.targetListWidget)

        self.targetAttributeWidget = QtWidgets.QWidget(targetAttributeSplitter)
        #targetAttributeSplitter.addWidget(self.targetAttributeWidget)
        targetAttributeLayout = QtWidgets.QVBoxLayout(self.targetAttributeWidget)
        targetAttributeLayout.setContentsMargins(0,0,0,0)
        
        # UV Sets attribute
        uvSetsGroupBox = QtWidgets.QGroupBox('UV Sets', self.targetAttributeWidget)
        uvSetsLayout = QtWidgets.QVBoxLayout(uvSetsGroupBox)
        uvSetsLayout.setAlignment(QtCore.Qt.AlignTop)

        baseUVLabel = QtWidgets.QLabel('Base UV Set:', uvSetsGroupBox)
        uvSetsLayout.addWidget(baseUVLabel)

        self.baseUVCombBox = QtWidgets.QComboBox(uvSetsGroupBox)
        uvSetsLayout.addWidget(self.baseUVCombBox)

        targetUVLabel = QtWidgets.QLabel('Target UV Set:', uvSetsGroupBox)
        uvSetsLayout.addWidget(targetUVLabel)

        self.targetUVCombBox = QtWidgets.QComboBox(uvSetsGroupBox)
        uvSetsLayout.addWidget(self.targetUVCombBox)

        self.rebindBtn = QtWidgets.QPushButton('Rebind', uvSetsGroupBox)
        self.rebindBtn.clicked.connect(self._updateUVSet)
        uvSetsLayout.addWidget(self.rebindBtn)

        targetAttributeLayout.addWidget(uvSetsGroupBox)

        # Delta scale attributes
        deltaScaleGroupBox = QtWidgets.QGroupBox('Delta Scale', self.targetAttributeWidget)
        deltaScaleFormLayout = QtWidgets.QFormLayout(deltaScaleGroupBox)

        maxFloat = sys.float_info.max

        self.deltaScaleXSpin = QtWidgets.QDoubleSpinBox(deltaScaleGroupBox)
        self.deltaScaleXSpin.setSingleStep(0.1)
        self.deltaScaleXSpin.setRange(-maxFloat, maxFloat)
        self.deltaScaleXSpin.setValue(1.0)
        self.deltaScaleXSpin.setDecimals(4)
        self.deltaScaleXSpin.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.Fixed)
        self.deltaScaleXSpin.valueChanged.connect(functools.partial(self._setDeltaScale, 'X'))
        deltaScaleFormLayout.addRow('X:', self.deltaScaleXSpin)

        self.deltaScaleYSpin = QtWidgets.QDoubleSpinBox(deltaScaleGroupBox)
        self.deltaScaleYSpin.setSingleStep(0.1)
        self.deltaScaleYSpin.setRange(-maxFloat, maxFloat)
        self.deltaScaleYSpin.setValue(1.0)
        self.deltaScaleYSpin.setDecimals(4)
        self.deltaScaleYSpin.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.Fixed)
        self.deltaScaleYSpin.valueChanged.connect(functools.partial(self._setDeltaScale, 'Y'))
        deltaScaleFormLayout.addRow('Y:', self.deltaScaleYSpin)

        self.deltaScaleZSpin = QtWidgets.QDoubleSpinBox(deltaScaleGroupBox)
        self.deltaScaleZSpin.setSingleStep(0.1)
        self.deltaScaleZSpin.setRange(-maxFloat, maxFloat)
        self.deltaScaleZSpin.setValue(1.0)
        self.deltaScaleZSpin.setDecimals(4)
        self.deltaScaleZSpin.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.Fixed)
        self.deltaScaleZSpin.valueChanged.connect(functools.partial(self._setDeltaScale, 'Z'))
        deltaScaleFormLayout.addRow('Z:', self.deltaScaleZSpin)

        targetAttributeLayout.addWidget(deltaScaleGroupBox)
        targetAttributeLayout.addStretch()
        self.targetAttributeWidget.setEnabled(False)

        mainLayout.addWidget(targetAttributeSplitter)

    def _createToolBar(self):
        '''Create the toolbar and buttons'''
        # tool bar and buttons
        toolBar = QtWidgets.QToolBar('ToolBar', self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, toolBar)

        action = toolBar.addAction('Create')
        action.triggered.connect(self.createNewDeformer)

        action = toolBar.addAction('Add Target')
        action.triggered.connect(self.addSelectedTargets)

        action = toolBar.addAction('Remove Target')
        action.triggered.connect(self.removeSelectedTargets)

        action = toolBar.addAction('Rebind Target')
        action.triggered.connect(self.rebindSelectedTargets)

        paintWeightsBtn = QtWidgets.QToolButton(toolBar)
        paintWeightsBtn.setText('Paint Weights')
        paintWeightsBtn.setToolTip('Paint weights on selected target. If you click' \
                                   ' and hold, you can choose to paint deformer and delta weights.')
        paintWeightsBtn.clicked.connect(self.paintSelectedTargetWeights)
        toolBar.addWidget(paintWeightsBtn)

        paintMenu = QtWidgets.QMenu(paintWeightsBtn)
        paintTargetWeightsAction = paintMenu.addAction('Target Weights')
        paintTargetWeightsAction.triggered.connect(self.paintSelectedTargetWeights)
        paintDeformerWeightsAction = paintMenu.addAction('Deformer Weights')
        paintDeformerWeightsAction.triggered.connect(self.paintDeformerWeights)
        paintDeltaWeightsAction = paintMenu.addAction('Delta Weights')
        paintDeltaWeightsAction.triggered.connect(self.paintDeltaWeights)
        paintWeightsBtn.setMenu(paintMenu)
        

    def createNewDeformer(self):
        '''Create a new seUVBlendShape deformer on selected mesh.'''
        # check it's a poly mesh
        selection = cmds.ls(sl=True, l=True)
        if not selection or len(selection) > 1:
            QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'Please select a single polygon mesh only.')
            return

        selected = selection[0]
        if cmds.nodeType(selected) == 'transform':
            shape = cmds.listRelatives(selected, f=True, type='shape')
            if not shape:
                QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'Selection does not have a shape under it.')
                return
            selected = shape[0]

        if cmds.nodeType(selected) != 'mesh':
            QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'Selection is not a polygon mesh.')
            return

        value, ok = QtWidgets.QInputDialog.getText(self, 'Enter Deformer Name',
            'Please enter the name of the new deformer:')
        
        if ok:
            deformer = cmds.deformer(selected, type='seUVBlendShape', n=value)[0]
            
            self.deformerComboBox.blockSignals(True)
            self.deformerComboBox.addItem(deformer)
            self.deformerComboBox.setCurrentIndex(self.deformerComboBox.count()-1)
            self.deformerComboBox.blockSignals(False)
            self.loadDeformer(deformer)

    def selectDeformer(self):
        '''Select the currently loaded deformer in the scene.'''
        currentDeformer = self.deformerComboBox.currentText()
        if currentDeformer:
            cmds.select(currentDeformer, r=True)

    def deleteDeformer(self):
        '''Delete the currently loaded deformer in the scene'''
        currentDeformer = self.deformerComboBox.currentText()
        if currentDeformer:
            cmds.delete(currentDeformer)
            self.refreshDeformerList()

    def loadDeformer(self, deformer):
        '''
        Load the given deformer into the UI. Normally this is called when
        the user has selected a deformer from the combo box or refreshes.

        :param deformer: name of seUVBlendShape deformer.
        :type deformer: str
        '''
        self.targetListWidget.clear()

        # add all the targets to the list
        targetNames = core.getTargetNames(deformer)
        for tn in targetNames:
            item = QtWidgets.QListWidgetItem(tn)
            item.setSizeHint(QtCore.QSize(item.sizeHint().width(), 20))
            self.targetListWidget.addItem(item)

    def refreshDeformerList(self):
        '''
        Refresh the deformer combo box with all seUVBlendShape deformers
        in the scene. If the current deformer is still in the scene,
        it will be reloaded. Otherwise the first deformer will be loaded.
        '''
        deformers = cmds.ls(type='seUVBlendShape')
        
        # store curent deformer to restore it after refreshing list
        currentDeformer = self.deformerComboBox.currentText()

        self.deformerComboBox.blockSignals(True)
        self.deformerComboBox.clear()

        if not deformers:
            self.deformerComboBox.blockSignals(False)
            self.targetListWidget.clear()
            return

        self.deformerComboBox.addItems(sorted(deformers))

        # try to restore the current  deformer if possible
        if currentDeformer:
            index = self.deformerComboBox.findText(currentDeformer)
            if index > -1:
                self.deformerComboBox.setCurrentIndex(index)
            else:
                currentDeformer = self.deformerComboBox.currentText()
        else:
            currentDeformer = self.deformerComboBox.currentText()

        self.deformerComboBox.blockSignals(False)

        self.loadDeformer(currentDeformer)

    def addSelectedTargets(self):
        '''
        Add selected meshes as targets to the current deformer.
        A popup box will allow you to specify options.
        '''
        currentDeformer = self.deformerComboBox.currentText()
        if not currentDeformer:
            return

        selection = cmds.ls(sl=True, l=True)
        if not selection:
            QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'Please select a polygon mesh.')
            return

        # filter out non-polyon objects
        invalidObjects = []
        for sel in selection:
            if cmds.nodeType(sel) == 'transform':
                shape = cmds.listRelatives(sel, f=True, type='shape')
                if not shape:
                    invalidObjects.append(sel)
                    continue
                sel = shape[0]

            if cmds.nodeType(sel) != 'mesh':
                invalidObjects.append(sel)

        if invalidObjects:
            QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'The following objects are not polygon meshes:\n' \
                '%s' % '\n'.join(invalidObjects))
            return

        baseMesh = cmds.deformer(currentDeformer, q=True, g=True)
        if not baseMesh:
            QtWidgets.QMessageBox.critical(self, 'Deformer Error',
                'Unable to get the base mesh from deformer.')
            return

        addTargetsDialog = AddTargetsDialog(self)
        addTargetsDialog.addTargets(baseMesh[0], *selection)

        if addTargetsDialog.exec_():
            for t in selection:
                baseUVSet = addTargetsDialog.getBaseUVSet(t)
                targetUVSet = addTargetsDialog.getTargetUVSet(t)
                tolerance = addTargetsDialog.getTargetTolerance(t)

                try:
                    core.addTarget(currentDeformer, t, baseUVSet=baseUVSet,
                        targetUVSet=targetUVSet, tolerance=tolerance)
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, 'Error Adding Target',
                        'Unable to add target to deformer:\n\n%s' % e)
                    raise

            self.loadDeformer(currentDeformer)

        addTargetsDialog.deleteLater()

    def removeSelectedTargets(self):
        '''Remove the selected targets in the list from the deformer.'''
        selectedTargets = self.targetListWidget.selectedItems()
        if not selectedTargets:
            return

        currentDeformer = self.deformerComboBox.currentText()
        for item in selectedTargets:
            core.removeTarget(currentDeformer, item.text())

        self.loadDeformer(currentDeformer)

    def paintSelectedTargetWeights(self):
        '''Activate target weight painting'''
        selection = self.targetListWidget.selectedItems()
        if not selection:
            return

        if len(selection) > 1:
            QtWidgets.QMessageBox.critical(self, 'Invalid Selection',
                'Select a single target to paint weights.')
            return

        targetName = selection[0].text()
        currentDeformer = self.deformerComboBox.currentText()
        core.paintTargetWeights(currentDeformer, targetName)

    def paintDeformerWeights(self):
        '''Activate deformer weight painting'''
        currentDeformer = self.deformerComboBox.currentText()
        if not currentDeformer:
            return

        core.paintDeformerWeights(currentDeformer)

    def paintDeltaWeights(self):
        '''Activate delta weight painting'''
        currentDeformer = self.deformerComboBox.currentText()
        if not currentDeformer:
            return

        core.paintDeltaWeights(currentDeformer)

    def rebindSelectedTargets(self):
        '''Rebind the selected targets.'''
        selection = self.targetListWidget.selectedItems()
        if not selection:
            return

        tolerance, ok = QtWidgets.QInputDialog.getDouble(self, 'Enter Tolerance',
                        'Enter the tolerance to use for rebinding:', 0.01,
                        0.0, sys.float_info.max, 4)

        if ok:
            currentDeformer = self.deformerComboBox.currentText()
            for sel in selection:
                core.rebind(currentDeformer, sel.text(), tolerance)

    def _onTargetSelectionChange(self):
        '''
        Called when there is a selection change in the target list
        '''
        # clear the target attribute widgets
        self.baseUVCombBox.clear()
        self.targetUVCombBox.clear()

        selection = self.targetListWidget.selectedItems()
        if len(selection) == 1:
            # this only works with a single target selection
            self.targetAttributeWidget.setEnabled(True)

            currentDeformer = self.deformerComboBox.currentText()
            baseMesh = cmds.deformer(currentDeformer, q=True, g=True)
            if not baseMesh:
                QtWidgets.QMessageBox.critical(self, 'Deformer Error',
                    'Unable to get the base mesh from deformer.')
                self.rebindBtn.setEnabled(False)
                return
            
            targetName = selection[0].text()
            targetMesh = core.getTargetMesh(currentDeformer, targetName)

            if not targetMesh:
                # the mesh is not connected, can't do anything
                self.rebindBtn.setEnabled(False)
                return

            baseUVSets = cmds.polyUVSet(baseMesh, q=True, auv=True)
            targetUVSets = cmds.polyUVSet(targetMesh, q=True, auv=True)

            self.baseUVCombBox.addItems(baseUVSets)
            self.targetUVCombBox.addItems(targetUVSets)

            # select UV sets that is bound on this deformer
            boundBaseUVSet = core.getBaseUVSet(currentDeformer, targetName)
            boundTargetUVSet = core.getTargetUVSet(currentDeformer, targetName)

            # get the indexes for the bound UV sets and error if they do not exist
            try:
                baseUVSetIndex = baseUVSets.index(boundBaseUVSet)
            except ValueError:
                QtWidgets.QMessageBox.critical(self, 'UV Error',
                    'Bound base UV set missing: %s' % boundBaseUVSet)
                self.rebindBtn.setEnabled(False)
                return

            try:
                targetUVSetIndex = targetUVSets.index(boundTargetUVSet)
            except ValueError:
                QtWidgets.QMessageBox.critical(self, 'UV Error',
                    'Bound target UV set missing: %s' % boundTargetUVSet)
                self.rebindBtn.setEnabled(False)
                return

            self.baseUVCombBox.setCurrentIndex(baseUVSetIndex)
            self.targetUVCombBox.setCurrentIndex(targetUVSetIndex)

            targetIndex = core.getTargetIndexFromName(currentDeformer, targetName)
            deltaScale = cmds.getAttr('%s.inputTarget[0].inputTargetGroup[%i].targetDeltaScale' %
                                    (currentDeformer, targetIndex))[0]

            self.deltaScaleXSpin.setValue(deltaScale[0])
            self.deltaScaleYSpin.setValue(deltaScale[1])
            self.deltaScaleZSpin.setValue(deltaScale[2])

        else:
            self._resetTargetAttributes()
            self.targetAttributeWidget.setEnabled(False)
            
    def _resetTargetAttributes(self):
        self.deltaScaleXSpin.blockSignals(True)
        self.deltaScaleYSpin.blockSignals(True)
        self.deltaScaleZSpin.blockSignals(True)

        self.deltaScaleXSpin.setValue(1.0)
        self.deltaScaleYSpin.setValue(1.0)
        self.deltaScaleZSpin.setValue(1.0)

        self.deltaScaleXSpin.blockSignals(False)
        self.deltaScaleYSpin.blockSignals(False)
        self.deltaScaleZSpin.blockSignals(False)

        self.baseUVCombBox.clear()
        self.targetUVCombBox.clear()

    def _setDeltaScale(self, axis, value):
        '''
        Called when the delta scale spin boxes change value
        '''
        currentDeformer = self.deformerComboBox.currentText()
        selection = self.targetListWidget.selectedItems()
        targetName = selection[0].text()
        targetIndex = core.getTargetIndexFromName(currentDeformer, targetName)

        deltaScaleAttr = '%s.inputTarget[0].inputTargetGroup[%i].' \
                        'targetDeltaScale%s' % (currentDeformer, targetIndex, axis)
        cmds.undoInfo(state=False)
        cmds.setAttr(deltaScaleAttr, value)
        cmds.undoInfo(state=True)

    def _updateUVSet(self):
        '''
        Called when the user clicks the rebind button on the target attribute
        section
        '''
        tolerance, ok = QtWidgets.QInputDialog.getDouble(self, 'Enter Tolerance',
                        'Enter the tolerance to use for rebinding:', 0.01,
                        0.0, sys.float_info.max, 4)

        if ok:
            selection = self.targetListWidget.selectedItems()
            currentDeformer = self.deformerComboBox.currentText()
            baseUVSet = self.baseUVCombBox.currentText()
            targetUVSet = self.targetUVCombBox.currentText()

            core.changeUVSet(currentDeformer, selection[0].text(),
                                    baseUVSet, targetUVSet, tolerance)

class AddTargetsDialog(QtWidgets.QDialog):
    '''
    A dialog box for setting specific options for adding targets to a
    seUVBlendShape deformer.
    '''

    def __init__(self, parent=None):
        super(AddTargetsDialog, self).__init__(parent)
        self.setWindowTitle('Add Targets')

        layout = QtWidgets.QVBoxLayout(self)

        instructions = QtWidgets.QLabel('For each target, select the base and ' \
                        'target UV set and the bind tolerance.', self)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        scrollArea = QtWidgets.QScrollArea(self)
        scrollArea.setWidgetResizable(True)
        scrollArea.setFrameStyle(QtWidgets.QFrame.NoFrame)
        layout.addWidget(scrollArea)

        self.scrollWidget = QtWidgets.QWidget(scrollArea)
        scrollArea.setWidget(self.scrollWidget)
        self.scrollLayout = QtWidgets.QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setContentsMargins(0,0,0,0)

        dialogButtonBox = QtWidgets.QDialogButtonBox(
                            QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel,
                            QtCore.Qt.Horizontal, self)
        dialogButtonBox.accepted.connect(self.accept)
        dialogButtonBox.rejected.connect(self.reject)
        layout.addWidget(dialogButtonBox)

        # storage for the base and target uv set widgets per target
        self._baseUVSetWidgets = {}
        self._targetUVSetWidgets = {}
        self._targetToleranceWidgets = {}

    def addTargets(self, baseMesh, *targetMeshes):
        '''
        Add targets to the dialog

        :param baseMesh: name of the base mesh on the seUVBlendShape deformer.
        :param baseMesh: str
        :param targetMeshes: target meshes that will be added the the deformer.
        :param targetMeshes: str
        '''
        baseMeshUVSets = cmds.polyUVSet(baseMesh, q=True, auv=True)

        for t in targetMeshes:
            targetGroupBox = QtWidgets.QGroupBox(t, self.scrollWidget)
            formLayout = QtWidgets.QFormLayout(targetGroupBox)

            baseUVSetComboBox = QtWidgets.QComboBox(targetGroupBox)
            baseUVSetComboBox.addItems(baseMeshUVSets)
            formLayout.addRow('Base UV Set:', baseUVSetComboBox)
            self._baseUVSetWidgets[t] = baseUVSetComboBox

            targetUVSets = cmds.polyUVSet(t, q=True, auv=True)
            targetUVSetComboBox = QtWidgets.QComboBox(targetGroupBox)
            targetUVSetComboBox.addItems(targetUVSets)
            formLayout.addRow('Target UV Set:', targetUVSetComboBox)
            self._targetUVSetWidgets[t] = targetUVSetComboBox

            toleranceDoubleSB = QtWidgets.QDoubleSpinBox(targetGroupBox)
            toleranceDoubleSB.setMinimum(0.0)
            toleranceDoubleSB.setSingleStep(0.01)
            toleranceDoubleSB.setValue(0.01)
            toleranceDoubleSB.setDecimals(3)
            formLayout.addRow('Tolerance:', toleranceDoubleSB)
            self._targetToleranceWidgets[t] = toleranceDoubleSB

            self.scrollLayout.addWidget(targetGroupBox)

    def getBaseUVSet(self, target):
        '''
        Return the user selected base UV set for the given target.

        :param target: name of target to get the base UV set for.
        :type target: str
        '''
        try:
            return self._baseUVSetWidgets[target].currentText()
        except KeyError:
            raise ValueError('No target found with name: %s' % target)

    def getTargetUVSet(self, target):
        '''
        Return the user selected target UV set for the given target.

        :param target: name of target to get the target UV set for.
        :type target: str
        '''
        try:
            return self._targetUVSetWidgets[target].currentText()
        except KeyError:
            raise ValueError('No target found with name: %s' % target)

    def getTargetTolerance(self, target):
        '''
        Return the user defined tolerance value for the given target

        :param target: name of target to get the tolerance for.
        :type target: str
        '''
        try:
            return self._targetToleranceWidgets[target].value()
        except KeyError:
            raise ValueError('No target found with name: %s' % target)