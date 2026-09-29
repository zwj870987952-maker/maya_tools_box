# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from PySide2 import QtCore, QtGui, QtWidgets

_OUTLINERS_ = {}

def getOutlinerOutput(outlinerName):
    outliner = _OUTLINERS_[outlinerName]
    return outliner.getOutlinerOutput()


##
## @brief      It is super important that all parents of this widget have specific and unique object names assigned. Or else Maya throws a hissyfit when re-parenting outliners.
##
class outlinerWidget(QtWidgets.QWidget):
    selectionFilter_global = []

    def __init__(self, parent=None, outlinerName=None, **kwargs):
        super(outlinerWidget, self).__init__(parent=parent, **kwargs)
        self.setObjectName('%s_wrapperWidget' %(outlinerName))
        self.setStyleSheet("background:#666666;")
        self.outlinerName = outlinerName

        self.rootLayout = QtWidgets.QVBoxLayout(self)
        self.rootLayout.setContentsMargins(0, 0, 0, 0)
        self.rootLayout.setSpacing(0)
        self.rootLayout.setObjectName('%s_wrapperLayout' %(outlinerName))
        self.rootLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.setLayout(self.rootLayout)

        self.slowModeActive = False
        self.selectionFilterActive = False

        self.textLayout = QtWidgets.QVBoxLayout()

        self.textLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.rootLayout.addLayout(self.textLayout)

        self.txt_filterName = QtWidgets.QLabel('FilterName')
        self.txt_filterName.setAlignment(QtCore.Qt.AlignCenter)
        self.textLayout.addWidget(self.txt_filterName)

        self.txt_searchQuery = QtWidgets.QLabel('SearchQuery')
        self.txt_searchQuery.setAlignment(QtCore.Qt.AlignCenter)
        self.textLayout.addWidget(self.txt_searchQuery)

        self.txt_searchQuery_toggle = QtWidgets.QLabel('Search Include')
        self.txt_searchQuery_toggle.setAlignment(QtCore.Qt.AlignCenter)
        self.textLayout.addWidget(self.txt_searchQuery_toggle)

        self.setFocusPolicy(QtCore.Qt.ClickFocus)



        self.txt_customOutput = QtWidgets.QLabel('')
        self.txt_customOutput.setAlignment(QtCore.Qt.AlignCenter)
        self.txt_customOutput.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.textLayout.addWidget(self.txt_customOutput)

        self.setMouseTracking(True)
        self.hotkey_revealSelected = QtWidgets.QShortcut(QtGui.QKeySequence("F"), self)
        self.hotkey_revealSelected.setEnabled(False)
        self.hotkey_revealSelected.activated.connect(self.revealSelected)

        self.filterGarbage = []

        self.itemFilter_default = "itemFilter_default"
        self.itemFilter_searchString = "itemFilter_searchString"
        self.itemFilter_nodeType = "itemFilter_nodeType"
        self.itemFilter_intersect = "itemFilter_intersect"

        self.activeBaseFilter = self.itemFilter_default
        self.activeAttributes = {}
        self.selectionFilter_local = []

        ### SCRIPT FILTER SETUP
        ### Make Mel-procedure used for scriptFilter
        _OUTLINERS_[outlinerName] = self
        self.OUTLINER_OUTPUT = []
        self.itemFilter_customOutput = "ks_getOutlinerCustomOutput_%s" %(outlinerName)

    def getOutlinerCustomOutput(self):
        return self.OUTLINER_OUTPUT

    def setOutlinerCustomOutput(self, nodeList):
        self.OUTLINER_OUTPUT = nodeList
        print('Setting Outliner output:', self.outlinerName)


    def revealSelected(self):
        print('Hotkey - Reveal Selected!')
        print(self.objectName())

    def enterEvent(self, event):
        self.hotkey_revealSelected.setEnabled(True)

    def leaveEvent(self, event):
        self.hotkey_revealSelected.setEnabled(False)



    def setFilter_byName_invertToggle(self, toggle):
        if toggle == True:
            self.txt_searchQuery_toggle.setText("Search Exclude")
        else:
            self.txt_searchQuery_toggle.setText("Search Include")

    def clearFilter(self):
        self.txt_filterName.setText('FilterName')
        self.txt_searchQuery.setText('SearchQuery')
        self.txt_searchQuery_toggle.setText('Search Include')
        self.txt_customOutput.setText('')


    def deleteFilterGarbage(self):
        for filterName in self.filterGarbage:
            self.filterGarbage.remove(filterName)


    def filter_searchFilter(self, string, inverted, updateFilter=True):
        self.searchFilterString = string
        searchString = '*%s*' %(string)
        self.txt_searchQuery.setText(searchString)
        if inverted is True:
            self.txt_searchQuery_toggle.setText('Search Exclude')
        else:
            self.txt_searchQuery_toggle.setText('Search Include')

        if updateFilter:
            self.filter_updateActive(customOutputRefresh=False)


    def filter_byNodeType(self, nodeTypes):
        filterData = {'baseFilter': 'nodeTypes', 'nodeTypes': nodeTypes}
        outlinerAttributes = {'ignoreDagHierarchy': False, 'expandObjects': False, 'showDagOnly': False}
        self.assignFilter(filterData=filterData, attributes=outlinerAttributes)
        # self.filter_updateActive()

    def filter_clear(self):
        filterData = {'baseFilter': None}
        outlinerAttributes = {'ignoreDagHierarchy': False, 'expandObjects': False, 'showDagOnly': True}
        self.assignFilter(filterData=filterData, attributes=outlinerAttributes)
        self.filter_updateActive()



    def selectionFilter(self, state, update=True, reset=False):
        if state == True:
            # self.selectionFilterActive = True
            self.selectionFilter_add()
            print('Activating selection filter!')
        else:
            # self.selectionFilterActive = False
            self.selectionLockList = []
            print('Reset selection filter!')

        if update:
            self.filter_updateActive()

    def selectionFilter_add(self, nodeList, local=False, inclHierarchy=False, inclShaders=False, inclInputs=False):
        selection = ['C1', 'D1']
        if local:
            self.selectionFilter_local_add(selection)
        else:
            self.selectionFilter_global_add(selection)

    def selectionFilter_remove(self, local=False):
        # selection = cmds.ls(selection, long=True)
        selection = ['C1']
        if local:
            self.selectionFilter_local_remove(selection)
        else:
            self.selectionFilter_global_remove(selection)
        # self.selectionLockList = list(set(self.selectionLockList) - set(selection))

    def selectionFilter_reset(self, local=False):
        self.selectionLockList = []
        if local:
            self.selectionFilter_local_reset()
        else:
            self.selectionFilter_global_reset()

    def selectionFilter_get(self, local=False):
        if local:
            return self.selectionFilter_local_get()
        else:
            return self.selectionFilter_global_get()

    def selectionFilter_global_add(cls, nodeList):
        cls.selectionFilter_global = list(set(cls.selectionFilter_global) | set(nodeList))
        print('Updating Global Selection Filter:', len(cls.selectionFilter_global), cls.selectionFilter_global)

    def selectionFilter_global_remove(cls, nodeList):
        cls.selectionFilter_global = list(set(cls.selectionFilter_global) - set(nodeList))

    def selectionFilter_global_reset(cls):
        cls.selectionFilter_global = []

    def selectionFilter_global_get(cls):
        return cls.selectionFilter_global

    def selectionFilter_local_add(self, nodeList):
        self.selectionFilter_local = list(set(self.selectionFilter_local) | set(nodeList))
        print('Updating Local Selection Filter:', len(self.selectionFilter_local), self.selectionFilter_local)

    def selectionFilter_local_remove(self, nodeList):
        self.selectionFilter_local = list(set(self.selectionFilter_local) - set(nodeList))

    def selectionFilter_local_reset(self):
        self.selectionFilter_local = []

    def selectionFilter_local_get(self):
        return self.selectionFilter_local


    def selectionFilter_check(self):
        if self.selectionFilter_local_get() or self.selectionFilter_global_get():
            self.selectionFilterActive = True
        else:
            self.selectionFilterActive = False
        return self.selectionFilterActive


    def assignFilter(self, filterNode, attributes):
        print('RUNNING - ASSIGN FILTER')
        self.deleteFilterGarbage()

        self.activeAttributes = attributes

        baseFilter = None

        baseFilterAttr = filterNode.getData('baseFilter')
        if baseFilterAttr == 'internalFilter':
            baseFilter = filterNode.getData('internalFilter')
        elif baseFilterAttr == 'nodeTypes':
            baseFilter = ', '.join(filterNode.getData('nodeTypes'))
        if baseFilter:
            self.activeBaseFilter = baseFilter
        else:
            self.activeBaseFilter = self.itemFilter_default


        if filterNode.getData("scriptFilter"):
            self.activeScriptCode = filterNode.getData("scriptCode")
        else:
            self.activeScriptCode = None

        return


    def filter_updateActive(self, customOutputRefresh=False):
        print('RUNNING - UPDATE ACTIVE FILTER')
        if self.slowModeActive:
            if self.activeScriptCode or self.selectionFilter_check():
                pass
                print('Slow-Mode active, but found script or selection filter')
            else:
                # self.filter_clear()
                print('Slow-Mode active, filters will not be activated without a Selection Filter or Script Filter')
                return

        self.itemFilter_intersect = self.activeBaseFilter + '<br>+<br>' + self.itemFilter_searchString
        activeFilter = self.itemFilter_intersect

        self.txt_filterName.setText(activeFilter)
        print(activeFilter)


    def customOutput_get(self):
        print('Getting outliner output:', len(self.OUTLINER_OUTPUT), self.OUTLINER_OUTPUT)
        return self.OUTLINER_OUTPUT

    def customOutput_set(self, nodeList):
        # nodeList = cmds.ls(nodeList, long=True)
        self.OUTLINER_OUTPUT = nodeList

    def customOutput_update(self):
        print('RUNNING - UPDATE CUSTOM OUTPUT')
        nodeOutput = []

        if self.activeScriptCode:
            nodeOutput = self.scriptFilter_runCode(self.activeScriptCode, nodeInput=nodeOutput)
            print('UpdateCustomOutput - 3', len(nodeOutput), nodeOutput)

        self.setOutlinerCustomOutput(nodeOutput)


    def scriptFilter_runCode(self, scriptCode, nodeInput):
        print('RUNNING - SCRIPTFILTER')
        nodeOutput = ['A1', 'B1']
        return nodeOutput


    def slowMode_toggle(self, state):
        self.slowModeActive = state

    def slowMode_activate(self):
        self.slowModeActive = True

    def slowMode_deactivate(self):
        self.slowModeActive = False

    def slowMode_validCheck(self):
        if self.slowModeActive:
            if self.activeScriptCode or self.selectionFilterActive:
                return True
            else:
                return False
        return True

    def printOutliner(self):
        pass

    def querySelectionLock(self):
        selectionFilterOutput_global = self.selectionFilter_get(local=False)
        print('Selection Filter Query - Global:', len(selectionFilterOutput_global), selectionFilterOutput_global)

        selectionFilterOutput_local = self.selectionFilter_get(local=True)
        print('Selection Filter Query - Local:', len(selectionFilterOutput_local), selectionFilterOutput_local)

        print('Selection Filter Check:', self.selectionFilter_check())
        print('Active ScriptCode:', self.activeScriptCode)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    outlinerGUI = outlinerWidget(outlinerName='dummyoutliner')
    outlinerGUI.resize(600,350)

    outlinerGUI.show()
    app.exec_()
