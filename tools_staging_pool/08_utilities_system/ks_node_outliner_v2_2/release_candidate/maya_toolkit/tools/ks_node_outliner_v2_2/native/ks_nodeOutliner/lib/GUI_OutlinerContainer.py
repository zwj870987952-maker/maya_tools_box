from __future__ import absolute_import
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore,QtGui,QtWidgets
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import Signal

from functools import partial

from ks_nodeOutliner.lib import libCommon, config

from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_lib,native_outliner
libMaya=native_lib();outlinerWidget=native_outliner()


class OutlinerContainer(QtWidgets.QWidget):
    def __init__(self, parent=None, outlinerName=None, **kwargs):
        super(OutlinerContainer, self).__init__(parent=parent)
        self.outlinerName = outlinerName
        self.setObjectName('%s_containerWidget' %(self.outlinerName))
        self.CONFIG = config.configuration()

        self.buildUI()

        self.activeFilterName = None
        self.selectionOverride = False


    def getOutlinerName(self):
        return self.outlinerName

    def buildUI(self):
        self.rootLayout = QtWidgets.QVBoxLayout(self)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName('%s_containerLayout' %(self.outlinerName))

        self.setLayout(self.rootLayout)

        self.commandLine_layout = QtWidgets.QHBoxLayout()
        self.commandLine_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.commandLine_layout.setContentsMargins(0, 0, 0, 0)
        self.commandLine_layout.setSpacing(0)
        self.rootLayout.addLayout(self.commandLine_layout)


        self.label_filterName = QtWidgets.QToolButton()
        self.label_filterName.setAutoRaise(False)
        self.label_filterName.setMaximumWidth(150)
        self.label_filterName.setMinimumWidth(90)
        self.label_filterName.setFocusPolicy(QtCore.Qt.NoFocus)
        self.label_filterName.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.label_filterName.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.label_filterName.setStyleSheet('''QToolButton:menu-indicator{image:none;}
            QToolButton:hover{background:none;border:none;}''')
        self.commandLine_layout.addWidget(self.label_filterName)

        self.menu_filterList = QtWidgets.QMenu(self)
        self.label_filterName.setMenu(self.menu_filterList)


        self.btn_scriptFilter = btn = libCommon.makeIconBtn(iconPath=':/CN_refresh.png', statusTip='Refresh ScriptFilter', iconFallBackLetter="R", command=self.scriptFilter_refresh, iconSize=20)
        self.commandLine_layout.addWidget(btn)
        # btn.setStyleSheet('''QToolButton:hover{background:none;border:none;}''')

        self.btn_scriptFilter_spacer = spacer = QtWidgets.QWidget()
        spacer.setFixedWidth(20)
        spacer.setVisible(False)
        self.commandLine_layout.addWidget(spacer)


        self.btn_resetFilter = btn = libCommon.makeIconBtn(iconPath=':/nodeGrapherClose.png', statusTip='Remove Filter', iconFallBackLetter="X", command=self.setFilter_noFilter, iconSize=20)
        self.commandLine_layout.addWidget(btn)


        self.searchField = ks_searchField()
        self.searchField.setMinimumWidth(100)
        self.searchField.setPlaceholderText('Search...')
        self.commandLine_layout.addWidget(self.searchField)
        self.searchField.searchUpdate.connect(lambda text, inverted: self.setFilter_byName(text, inverted=inverted))


        self.btn_selectionFilter_local = btn = libCommon.makeIconBtn(iconPath=':/aselect.png', statusTip='Local Selection Filter - Affects only one outliner, overriding the Global Selection Filter. Right-Click for options.', iconFallBackLetter="S", iconSize=20)
        btn.setCheckable(True)
        self.btn_selectionFilter_local.clicked.connect(lambda: self.selectionFilter_local_toggle(active=self.btn_selectionFilter_local.isChecked()))
        self.commandLine_layout.addWidget(btn)

        self.btn_selectionFilter_local.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.btn_selectionFilter_local.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.btn_selectionFilter_local.customContextMenuRequested.connect(self.contextMenu_localSelectionFilter)

        self.menu_selectionFilter_local = menu = QtWidgets.QMenu(self)

        self.ma_sf_inclHierarchy = action = QtWidgets.QAction('Include Hierarchy', menu, checkable=True)
        # action.setIcon(libCommon.getIconObject(':/selectByHierarchy.png'))
        action.setChecked(True)
        menu.addAction(action)

        self.ma_sf_includeShaders = action = QtWidgets.QAction('Include Shading Network', menu, checkable=True)
        # action.setIcon(libCommon.getIconObject(':/out_shadingEngine.png'))
        action.setChecked(True)
        menu.addAction(action)

        self.ma_sf_includeInputs = action = QtWidgets.QAction('Include Input Connections', menu, checkable=True)
        # action.setIcon(libCommon.getIconObject(':/input.png'))
        action.setChecked(True)
        menu.addAction(action)


        self.outlinerWidget = outlinerWidget.outlinerWidget(outlinerName=self.outlinerName)
        self.outlinerWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.outlinerWidget.setParent(self)
        self.rootLayout.addWidget(self.outlinerWidget)


    def contextMenu_localSelectionFilter(self, point):
        self.menu_selectionFilter_local.exec(self.btn_selectionFilter_local.mapToGlobal(point))


    def setFilterName(self, filterName):
        self.label_filterName.setText(filterName)
        self.label_filterName.setStatusTip('Active Filter - %s' %(filterName))

    def populate_filterList(self, filterList):
        self.menu_filterList.clear()
        for filterName in filterList:
            self.menu_filterList.addAction(filterName, partial(self.setFilter_byPreset, filterName))



    def setFilter_byName(self, string, inverted):
        self.outlinerWidget.filter_searchFilter(string, inverted=inverted)


    def setFilter_noFilter(self):
        self.setFilterName(" ")
        self.searchField.resetField(emitSignal=False)
        self.outlinerWidget.filter_searchFilter('', inverted=False, updateFilter=False)
        self.scriptFilter_toggle(False)

        self.outlinerWidget.filter_clear()

    def setFilter_bySelectedNodeTypes(self):
        nodeTypes = libMaya.nodeTypesFromSelection()
        if not nodeTypes:
            return

        filterName = '/'.join(nodeTypes)
        self.setFilterName(filterName)
        self.scriptFilter_toggle(False)

        if self.searchField.fromPreset is True:
            self.searchField.resetField(emitSignal=False)

        self.outlinerWidget.filter_byNodeType(nodeTypes)

    def setFilter_customOutput(self, nodeList, ignoreHierarchy=False):
        self.setFilterName("Custom Output")
        self.outlinerWidget.filter_customOutput(nodeList, ignoreHierarchy=ignoreHierarchy)
        self.scriptFilter_toggle(False)

    def setFilter_byPreset(self, filterName):
        filterNode = self.CONFIG.getFilterNode(filterName)
        if not filterNode:
            self.setFilter_noFilter()
            return

        self.setFilterName(filterName)

        filterText = filterNode.getData('searchString')
        searchInvert = filterNode.getData('searchInvert')
        if filterText:
            self.searchField.setText(filterText, fromPreset=True)
            self.searchField.invertSearch_setToggle(searchInvert, emitSignal=False)
            self.outlinerWidget.filter_searchFilter(filterText, inverted=searchInvert, updateFilter=False)
        else:
            if self.searchField.fromPreset is True:
                ### Prevents user-inputs from being erased when applying filters without searchFilter.
                self.searchField.setText('', fromPreset=True)
                self.searchField.invertSearch_setToggle(False, emitSignal=False)
                self.outlinerWidget.filter_searchFilter('', inverted=False, updateFilter=False)


        if filterNode.getData('updateSelectionFilter'):
            self.selectionOverride = True
            inclHierachy = filterNode.getData('sf_getHierarchy')
            inclShaders = filterNode.getData('sf_getShadingNetwork')
            inclInputs = filterNode.getData('sf_getInputConnections')
            self.selectionFilter_local_activate(inclHierarchy=inclHierachy, inclShaders=inclShaders, inclInputs=inclInputs)

        else:
            if self.selectionOverride:
                self.selectionOverride = False
                self.selectionFilter_local_deactivate()


        if filterNode.getData('scriptFilter'):
            self.scriptFilter_toggle(True)
        else:
            self.scriptFilter_toggle(False)

        # outlinerAttributes = {}
        # outlinerAttributes['showShapes'] = filterNode.getData('showShapes')
        # # outlinerAttributes['ignoreDagHierarchy'] = filterNode.getData('ignoreDagHierarchy')
        # outlinerAttributes['expandObjects'] = filterNode.getData('expandObjects')
        # outlinerAttributes['showDagOnly'] = False

        self.outlinerWidget.assignFilter(filterNode)
        self.outlinerWidget.filter_updateActive()

    def selectionFilter_local_toggle(self, active=None):
        if active == True:
            self.selectionFilter_local_activate()
        else:
            self.selectionFilter_local_deactivate()
        return

    def selectionFilter_local_activate(self, rootSelection=None, inclHierarchy=None, inclShaders=None, inclInputs=None):
        if not rootSelection:
            rootSelection = libMaya.getSelection(fullPath=False)
        if not rootSelection:
            libMaya.warning('Nothing selected. Local Selection Filter is not activated.')
            self.btn_selectionFilter_local.setChecked(False)
            return

        if not inclHierarchy:
            inclHierarchy = self.ma_sf_inclHierarchy.isChecked()
        if not inclShaders:
            inclShaders = self.ma_sf_includeShaders.isChecked()
        if not inclInputs:
            inclInputs = self.ma_sf_includeInputs.isChecked()

        self.outlinerWidget.selectionFilter_reset(local=True)
        self.outlinerWidget.selectionFilter_add(nodeList=rootSelection, local=True, inclHierarchy=inclHierarchy, inclShaders=inclShaders, inclInputs=inclInputs)

        self.btn_selectionFilter_local.setChecked(True)
        self.outlinerWidget.filter_updateActive()


    def selectionFilter_local_deactivate(self):
        self.btn_selectionFilter_local.setChecked(False)
        self.outlinerWidget.selectionFilter_reset(local=True)
        self.outlinerWidget.filter_updateActive()


    def scriptFilter_toggle(self, state):
        if state == True:
            self.btn_scriptFilter.setVisible(True)
            self.btn_scriptFilter_spacer.setVisible(False)
        else:
            self.btn_scriptFilter.setVisible(False)
            self.btn_scriptFilter_spacer.setVisible(True)
        return


    def scriptFilter_refresh(self):
        if self.selectionOverride == True:
            self.selectionFilter_local_activate()
        self.outlinerWidget.filter_updateActive()


    def slowMode_activate(self):
        self.outlinerWidget.slowMode_toggle(True)
        self.searchField.slowMode_toggle(True)


    def slowMode_deactivate(self):
        self.outlinerWidget.slowMode_toggle(False)
        self.searchField.slowMode_toggle(False)
        self.outlinerWidget.filter_updateActive()

    def diagnoseBtn(self):
        self.outlinerWidget.querySelectionLock()




class ks_searchField(QtWidgets.QLineEdit):
    searchUpdate = Signal(str, bool)

    def __init__(self,parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.setTextMargins(20,0,20,0)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(2,0,2,0)

        self.setStyleSheet("""
            .QToolButton:hover{color:white;}
            .QToolButton:disabled{color:#7c7c7c;}
            .QToolButton{color:#C6C6C6; background:transparent; border:None}
            """)

        self.btn_toggleInvert = QtWidgets.QToolButton(self)
        self.btn_toggleInvert.setText('>')
        self.btn_toggleInvert.setFont(QtGui.QFont("Times", 14))
        self.btn_toggleInvert.setMaximumHeight(15)
        self.btn_toggleInvert.setMaximumWidth(15)
        self.btn_toggleInvert.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_toggleInvert.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btn_toggleInvert.setStyleSheet("background: transparent; border: none;")
        self.btn_toggleInvert.setStatusTip('Invert text-filter.')
        self.btn_toggleInvert.clicked.connect(self.invertSearch_toggle)
        layout.addWidget(self.btn_toggleInvert, 0, QtCore.Qt.AlignLeft)

        self.btn_clearField = libCommon.makeIconBtn(iconPath=':/hotkeyFieldClear.png', iconFallBackLetter="x", command=False, iconSize=14)
        self.btn_clearField.setFont(QtGui.QFont("Times", 12))
        self.btn_clearField.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_clearField.setFocusPolicy(QtCore.Qt.NoFocus)
        self.btn_clearField.setStyleSheet("background: transparent; border: none;")
        self.btn_clearField.clicked.connect(self.resetField)

        self.textEdited.connect(lambda text: self.textUpdated(text=text, forceUpdate=False, editingFinished=False))
        self.editingFinished.connect(lambda: self.textUpdated(text=self.text(), forceUpdate=True, editingFinished=True))
        layout.addWidget(self.btn_clearField, 1, QtCore.Qt.AlignRight)

        self.clearField_toggleVisiblity(False)
        self.inverted = False
        self.fromPreset = False
        self.slowMode = False
        self.lastSearch = None


    def textUpdated(self, text, forceUpdate=False, editingFinished=False):
        self.clearField_toggleVisiblity(text)

        if self.slowMode is True:
            if editingFinished is False and forceUpdate is False:
                return
        elif self.slowMode is False and editingFinished is True:
            return

        if forceUpdate:
            self.searchUpdate.emit(text, self.inverted)
            self.lastSearch == text
            return

        if self.lastSearch == text:
            return

        self.lastSearch == text
        self.searchUpdate.emit(text, self.inverted)



    def slowMode_toggle(self, state):
        self.slowMode = state

    def setText(self, text, fromPreset=False):
        self.fromPreset = fromPreset
        self.blockSignals(True)
        super(ks_searchField, self).setText(text)
        self.blockSignals(False)
        self.clearField_toggleVisiblity(text)

    def invertSearch_toggle(self):
        if self.inverted is True:
            self.invertSearch_setToggle(False, emitSignal=True)
        else:
            self.invertSearch_setToggle(True, emitSignal=True)

    def invertSearch_setToggle(self, toggle, emitSignal=True):
        if toggle:
            self.inverted = True
            self.btn_toggleInvert.setText('<')
            self.btn_toggleInvert.setStyleSheet("color:#b27070;")
        else:
            self.inverted = False
            self.btn_toggleInvert.setText('>')
            self.btn_toggleInvert.setStyleSheet("color:#7c7c7c;")

        if emitSignal:
            self.textUpdated(text=self.text(), forceUpdate=True)

    def clearField_toggleVisiblity(self, active):
        if active:
            self.btn_clearField.setVisible(True)
            self.btn_toggleInvert.setEnabled(True)
        else:
            self.btn_clearField.setVisible(False)
            self.btn_toggleInvert.setEnabled(False)

    def resetField(self, emitSignal=True):
        self.setText('', fromPreset=False)
        self.invertSearch_setToggle(False, emitSignal=False)
        if emitSignal:
            self.textUpdated(text='', forceUpdate=True)





if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    outlinerGUI = OutlinerContainer(outlinerName='outlinerA')
    outlinerGUI.resize(300,350)

    filterList = outlinerGUI.CONFIG.getFilterNames()
    outlinerGUI.show()
    outlinerGUI.populate_filterList(filterList)
    app.exec()
