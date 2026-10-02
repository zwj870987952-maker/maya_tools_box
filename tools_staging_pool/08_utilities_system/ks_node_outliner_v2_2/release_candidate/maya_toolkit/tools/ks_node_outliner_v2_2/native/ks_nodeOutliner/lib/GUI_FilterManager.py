# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import QtCore,QtGui,QtWidgets
from maya_toolkit.tools.ks_node_outliner_v2_2.qt_compat import Signal as pyqtSignal

import ks_nodeOutliner
from ks_nodeOutliner.lib import config, libCommon


from maya_toolkit.tools.ks_node_outliner_v2_2.session import native_lib
libMaya=native_lib()

_helpText_ = '''
<h1>Editing Filters</h1>
<b>Filter Icon</b><br>
Icon-paths starting with :/ are relative and will use either internal Maya icons, or use your own custom icons from the plugin's ICON folder.

<h2>Base Filter</h2>
<b>Internal Maya Filter</b><br>
Filters built into Maya, grouping node-types by categories. Custom nodetypes from render-plugins are usually included in these filters.<br>
<br>
<b>Filter by node types</b><br>
Specify what node-types to filter manually.

<h2>Selection Filter</h2>
Enables and updates Local Selection Filter with current selection when filter is activated.<br>
Local Selection Filter takes priority over any Global Selection Filter which may be active.<br>
This can be useful when used with more complex script filters, to avoid processing unecessary amount of nodes.<br>
<br>
A Selection Filter can optionally include nodes related to the "root" selection, such as all hierarchy children, shading networks, and input connections.<br>
This allows you to only select the root group of an asset, and get all nodes related to that asset.<br>
<br>
- When a Selection Filter is activated, the outliner will no longer automatically update.

<h2>Script Filter</h2>
Filter using custom python code.<br>
It will filter nodes based on the result from Base Filter and Selection Filter if active.<br>
<br>
<b>Use at your own risk, do not run code you don't trust!</b><br>
<br>
- When a Script Filter is activated, the outliner will no longer automatically update.<br>
- Naming conflicts may cause identically named nodes to display, despite only one node passing the filter.<br>
<br>

<b>Module Name</b><br>
Points to a module accessible through PythonPath.<br>
Module paths beginning with . are relative to the scriptFilter-directory found in the KS_NodeOutliner's plugin folder.<br>
<br>
<b>Function Name</b><br>
The name of the filter function inside the specified module.<br>
<br>
<b>Arguments</b><br>
Optional arguments can be provided to make filters more flexible.<br>
Multiple arguments are separated by , without spaces.<br>
Arguments containing only numbers will be automatically converted to intergers, otherwise all arguments are strings.<br>



<h2>Search Filter</h2>
Default input into the search field, if you want to filter by object names.

<h2>Outliner Display</h2>
<b>Ignore Hierarchy</b> will display all nodes as a flat list. Show Shapes will be enabled, as parent transforms are also ignored.<br>
<b>Auto-Expand Hierarchy</b> will expand all hierarchy.<br>


<h1>Making Script Filters</h1>
<b>Node Input</b><br>
The first argument passed to the script filter is always a list of nodes passing the Base Filter and/or Selection Filter. If those filters are inactive, the list will be empty.<br>
<br>
<b>Node Output</b><br>
Return any list of nodes to display them in the outliner.<br>
Full-path/Long names are not supported. All nodes returned from the script filter will automatically be converted to short names.
This may cause naming conflcits, and nodes with identical names may display despite not passing any filters.<br>
<br>
When testing a script filter using the Preview-button in the Filter Manager, the module will be automatically reloaded to use the latest code.<br>

<h3>Example Script Filter:</h3>
<pre>def ks_attrMatch(*args):
    nodeOutput = []
    nodeInput = args[0]
    attr = args[1]
    value = args[2]

    for node in nodeInput:
        if cmds.getAttr(node+'.'+attr) == value:
            nodeOutput.append(node)
    return nodeOutput</pre>

'''



class GUI_FilterManager(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(GUI_FilterManager, self).__init__(parent)
        self.setWindowTitle("KS_NodeOutliner - Filter Manager")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.rootLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self.rootLayout)

        self.CONFIG = config.configuration()
        self.CONFIG.snapshotData()

        self.activeFilterPreset = None

        self.buildUI()
        self.setMaximumSize(self.rootLayout.sizeHint())
        self._populate_allfilterPresetList()


        self.CONFIG.guiRefresh.connect(self._refreshLists)



    def show(self):
        super(GUI_FilterManager, self).show()
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def reject(self):
        self.CONFIG.restoreData()
        super(GUI_FilterManager, self).reject()
        # self.deleteLater()

    def saveConfig(self):
        self.CONFIG.setFilterListOrder(self.filtersMasterListWidget.exportList())
        self.filterMasterList_mainWidget.setFocus()
        self.CONFIG.saveData()
        self.accept()
        # self.deleteLater()




    def buildUI(self):
        #----- CONFIGURATION WIDGETS -----#

        self.edit_layout = QtWidgets.QHBoxLayout()
        self.rootLayout.addLayout(self.edit_layout)

        self.buildUI_filterMasterList(self.edit_layout)

        self.tabWidget = QtWidgets.QTabWidget()
        self.edit_layout.addWidget(self.tabWidget)


        self.filterEdit_widget = GUI_EditFilter(self)
        self.tabWidget.addTab(self.filterEdit_widget, "Edit Filter")

        self.menuPresetEdit_widget = GUI_editMenuPreset(self)
        self.tabWidget.addTab(self.menuPresetEdit_widget, "Menu Presets")


        self.helpTextView = QtWidgets.QTextEdit()
        self.helpTextView.setReadOnly(True)
        self.helpTextView.setText(_helpText_)

        self.helpTextView_document = self.helpTextView.document()
        self.tabWidget.addTab(self.helpTextView, "Help")

        #-------------------- COMMAND BUTTONS --------------------------------#

        self.commands_layout = QtWidgets.QHBoxLayout()
        self.commands_layout.setAlignment(QtCore.Qt.AlignRight)
        self.rootLayout.addLayout(self.commands_layout)

        spacerItem = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.commands_layout.addItem(spacerItem)

        btn = QtWidgets.QPushButton('Cancel')
        self.commands_layout.addWidget(btn)
        btn.clicked.connect(self.reject)

        btn = QtWidgets.QPushButton('Save')
        self.commands_layout.addWidget(btn)
        btn.clicked.connect(self.saveConfig)



    # ------------------------------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------------------------------ #
    # ----------------------------------------MASTER FILTER LIST ------------------------------------------- #
    # ------------------------------------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------------------------------------ #



    def buildUI_filterMasterList(self, parent):
        self.filterMasterList_mainWidget = QtWidgets.QWidget()
        self.filterMasterList_mainWidget.setFixedWidth(150)

        self.filterMasterList_mainLayout = QtWidgets.QGridLayout()
        self.filterMasterList_mainLayout.setContentsMargins(1,1,1,1)
        self.filterMasterList_mainLayout.setSpacing(2)
        self.filterMasterList_mainWidget.setLayout(self.filterMasterList_mainLayout)
        parent.addWidget(self.filterMasterList_mainWidget)

        label = QtWidgets.QLabel('All Filters:')
        self.filterMasterList_mainLayout.addWidget(label,0,0,1,1)

        self.filtersMasterListWidget = listWidget_allFilters(self)
        # self.filtersMasterListWidget.setFixedWidth(200)
        self.filtersMasterListWidget.setStatusTip('Double click to edit preset.')
        self.filterMasterList_mainLayout.addWidget(self.filtersMasterListWidget,1,0,1,-1)

        self.filtersMasterListWidget.itemDoubleClicked.connect(lambda item:self.filterEdit_widget.openFilter(item.text()))
        self.filtersMasterListWidget.itemsDeleted.connect(lambda deletedFilters:self.filterPresets_delete(deletedFilters))

        cmdLayout = QtWidgets.QHBoxLayout()
        cmdLayout.setAlignment(QtCore.Qt.AlignLeft)
        cmdLayout.setSpacing(2)
        cmdLayout.setContentsMargins(0,0,0,0)
        self.filterMasterList_mainLayout.addLayout(cmdLayout,2,0,1,-1)


        btn = libCommon.makeIconBtn(iconPath=':/addClip_100.png', statusTip='Create New Filter Preset', iconFallBackLetter='+', iconSize=18)
        btn.clicked.connect(self.filterPresets_addNew)
        cmdLayout.addWidget(btn)

        btn = libCommon.makeIconBtn(iconPath=':/UVTkDuplicateSet.png',statusTip='Duplicate Filter', iconFallBackLetter='D', iconSize=18)
        btn.clicked.connect(self.filterPresets_duplicate)
        cmdLayout.addWidget(btn)


        btn = libCommon.makeIconBtn(iconPath=':/deleteGeneric.png', statusTip='Delete Selected Filter Presets', iconFallBackLetter='-', iconSize=18)
        btn.clicked.connect(self.filterPresets_delete)
        cmdLayout.addWidget(btn)

        spacer = QtWidgets.QSpacerItem(18,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        cmdLayout.addItem(spacer)

        # btn = libCommon.makeIconBtn(iconPath=':/teImport.svg', statusTip='Import from presetFile', iconFallBackLetter='I', iconSize=18)
        btn = libCommon.makeIconBtn(iconPath=':/fileOpen.png', statusTip='Import filters', iconFallBackLetter='I', iconSize=18)
        btn.clicked.connect(self.filterPresets_importFromFile)
        cmdLayout.addWidget(btn)

        # btn = libCommon.makeIconBtn(iconPath=':/save.png', statusTip='Export To PresetFile', iconFallBackLetter='E', iconSize=18)
        btn = libCommon.makeIconBtn(iconPath=':/fileSave.png', statusTip='Export selected filters', iconFallBackLetter='E', iconSize=18)
        btn.clicked.connect(self.filterPresets_exportToFile)
        cmdLayout.addWidget(btn)


    def _refreshLists(self):
        self._populate_allfilterPresetList()
        self.menuPresetEdit_widget.refresh()


    def _populate_allfilterPresetList(self):
        self.filtersMasterListWidget.clear()
        allFilters = self.CONFIG.getFilterNames()
        sortOrder = self.CONFIG.getFilterListOrder()
        filterList = [x for x in sortOrder if x in allFilters]
        filterList += [x for x in allFilters if x not in filterList]

        for filterName in filterList:
            item = QtWidgets.QListWidgetItem(filterName)
            filterNode = self.CONFIG.getFilterNode(filterName)
            iconPath = filterNode.getData('icon')
            libCommon.setIcon_listItem(item, iconPath)
            self.filtersMasterListWidget.addItem(item)


        self.filterEdit_widget.openFilter(filterList[0])


    def filterPresets_addNew(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Add new filter preset:', 'Filter name:')
        if ok: newFilterName = text
        else: return

        node = self.CONFIG.filter_addNew(newFilterName)
        filterName = node.getFilterName()
        iconPath = node.getData("icon")

        item = QtWidgets.QListWidgetItem(filterName)
        libCommon.setIcon_listItem(item, iconPath)
        self.filtersMasterListWidget.addItem(item)


    def filterPresets_delete(self, filterList=None):
        if not filterList:
            filterList = self.filtersMasterListWidget.getSelectedItems()

        for filterName in filterList:
            self.CONFIG.filter_delete(filterName)

        if self.filterEdit_widget.activeFilter in filterList:
            self.filterEdit_widget.openFilter(self.CONFIG.getFilterNames()[0])

        self._refreshLists()


    def filterPresets_duplicate(self):
        selection = self.filtersMasterListWidget.getSelectedItems()
        for filterName in selection:
            filterNode = self.CONFIG.filter_duplicate(filterName)


    def filterPresets_importFromFile(self):
        options = QtWidgets.QFileDialog.Options()
        filePaths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Import Filters from File", ks_nodeOutliner._ROOTDIR_,"Json Files (*.json)", options=options)
        if not filePaths:
            return

        self.CONFIG.importFromFile(filePaths[0])
        self.filtersMasterListWidget.clear()
        self._populate_allfilterPresetList()


    def filterPresets_exportToFile(self):
        filePath, ok = QtWidgets.QFileDialog.getSaveFileName(self, 'Export Filters to File', ks_nodeOutliner._ROOTDIR_, '*.json')
        if not ok:
            return

        if not filePath.endswith('.json'):
            filePath += '.json'

        filterList = self.filtersMasterListWidget.getSelectedItems()
        self.CONFIG.exportToFile(filePath, filterList)





# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# -------------------------------------------- FILTER EDIT --------------------------------------------- #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #






class GUI_EditFilter(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super(GUI_EditFilter, self).__init__(parent=parent, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        self.setStyleSheet('''#groupbox_boldTitle {font-weight:bold;font-size:10pt;}''')

        self.CONFIG = config.configuration()

        self.activeFilter = None
        self.activeFilterNode = None
        self.filterData = None

        self.inputWidgets_blockToggle = []
        self.buildUI()

    def buildUI(self):
        # self.rootLayout = QtWidgets.QVBoxLayout(self)
        # self.setLayout(self.rootLayout)

        gridLayout = QtWidgets.QGridLayout()
        gridLayout.setContentsMargins(5, 5, 5, 5)
        gridLayout.setSpacing(8)
        # self.rootLayout.addLayout(gridLayout)
        self.setLayout(gridLayout)

        ## ------------FILTER NAME & ICON  -------------- ##


        self.filterIcon_iconPreview = label = QtWidgets.QLabel()
        self.iconPixmap = QtGui.QPixmap()
        label.setFixedSize(25,25)
        label.setScaledContents(True)
        gridLayout.addWidget(self.filterIcon_iconPreview, 0, 0)

        self.filterName_label = label = QtWidgets.QLabel('Filter')
        font = label.font()
        font.setPointSize(16)
        label.setFont(font)
        gridLayout.addWidget(self.filterName_label,0,1)




        iconConfigLayout = QtWidgets.QHBoxLayout()
        iconConfigLayout.setAlignment(QtCore.Qt.AlignBottom)
        iconConfigLayout.setSpacing(2)
        # gridLayout.addLayout(iconConfigLayout,1,0,1,-1)
        gridLayout.addLayout(iconConfigLayout,0,2,1,-1)


        spacer = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        iconConfigLayout.addItem(spacer)

        # btn = QtWidgets.QPushButton("Rename")
        # btn.setFixedWidth(60)
        btn = libCommon.makeIconBtn(iconPath=':/renamePreset_100.png', statusTip='Rename Filter', iconFallBackLetter='Rename', iconSize=32)
        icon = libCommon.getIconObject(':/renamePreset_100.png')
        btn.setIcon(icon)
        iconConfigLayout.addWidget(btn)
        btn.clicked.connect(self.renameFilter)

        spacer = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        iconConfigLayout.addItem(spacer)

        label = QtWidgets.QLabel('Icon:')
        iconConfigLayout.addWidget(label)

        self.filterIcon_editField = lineEdit = QtWidgets.QLineEdit()
        lineEdit.setFixedWidth(120)
        iconConfigLayout.addWidget(lineEdit)


        btn = libCommon.makeIconBtn(iconPath=':/browseFolder.png', statusTip='Browse for custom icon', iconFallBackLetter='...', iconSize=22)
        btn.clicked.connect(self.browseIcons_explorer)
        iconConfigLayout.addWidget(btn)


        btn = libCommon.makeIconBtn(iconPath=':/teContentBrowser.png', statusTip='Browse Maya Built-In icons', iconFallBackLetter='MB', iconSize=22)
        iconConfigLayout.addWidget(btn)
        btn.clicked.connect(self.browseMayaIcons)

        self.filterIcon_editField.editingFinished.connect(lambda: self.iconUpdated(iconPath=self.filterIcon_editField.text()))


        # label = QtWidgets.QLabel('Description:')
        # gridLayout.addWidget(label, 1, 0)

        # lineEdit = QtWidgets.QLineEdit()
        # gridLayout.addWidget(lineEdit, 1, 0, 1, -1)
#         lineEdit.setPlaceholderText('Description')

        ## ----------------------------------------
        ## ------------BASE FILTER  -------------- ##
        ## ---------------------------------------

        self.baseFilter_groupBox = groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle('Base Filter')
        groupBox.setObjectName('groupbox_boldTitle')
        groupBox.setCheckable(True)
        groupBox.setChecked(True)
        gridLayout.addWidget(groupBox,2,0,1,-1)

        groupBoxLayout = QtWidgets.QVBoxLayout()
        groupBoxLayout.setContentsMargins(4,4,4,4)
        groupBoxLayout.setSpacing(2)
        groupBox.setLayout(groupBoxLayout)

        self.baseFilter_groupBox.toggled.connect(lambda state: self.updateFilterData(dataKey='baseFilter', dataValue=state))
        self.inputWidgets_blockToggle.append(self.baseFilter_groupBox)


        self.baseFilterType_radioGroupParent = ks_radioGroup_noWidget()
        self.baseFilterType_radioGroupParent.stateChanged.connect(lambda value: self.updateFilterData(dataKey='baseFilterType', dataValue=value))
        self.inputWidgets_blockToggle.append(self.baseFilterType_radioGroupParent)


        hboxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.addLayout(hboxLayout)
        radioBtn = QtWidgets.QRadioButton('Internal Maya filter:')
        radioBtn.setFixedWidth(130)
        self.baseFilterType_radioGroupParent.addRadioBtn(radioBtn, radioName='internalFilter')
        hboxLayout.addWidget(radioBtn)

        self.nodeFilterPresetMenu_menu = combobox = QtWidgets.QComboBox(self)
        combobox.addItems(libMaya.maya_getBuiltInFilters())
        self.nodeFilterPresetMenu_menu.currentTextChanged.connect(lambda text: self.updateFilterData(dataKey='internalFilter', dataValue=text))
        hboxLayout.addWidget(self.nodeFilterPresetMenu_menu)

        self.baseFilterType_radioGroupParent.addSubWidgets(radioName='internalFilter', widgets=self.nodeFilterPresetMenu_menu)
        self.inputWidgets_blockToggle.append(self.nodeFilterPresetMenu_menu)

        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignTop)
        btnLayout.setSpacing(1)
        btnLayout.setContentsMargins(1,1,1,1)
        groupBoxLayout.addLayout(btnLayout)

        radioBtn = QtWidgets.QRadioButton('Filter by node types:')
        radioBtn.setFixedWidth(130)
        self.baseFilterType_radioGroupParent.addRadioBtn(radioBtn, radioName='nodeTypes')
        btnLayout.addWidget(radioBtn)

        self.nodeTypes_widget = baseListWidget()
        self.nodeTypes_widget.setFixedHeight(23)
        self.nodeTypes_widget.setFlow(QtWidgets.QListWidget.LeftToRight)
        self.nodeTypes_widget.setWrapping(True)
        self.nodeTypes_widget.setClipboardGroup('nodeTypes')
        self.nodeTypes_widget.modified.connect(lambda: self.updateFilterData(dataKey='nodeTypes', dataValue=self.nodeTypes_widget.exportList()))
        btnLayout.addWidget(self.nodeTypes_widget)
        self.inputWidgets_blockToggle.append(self.nodeTypes_widget)



        btnA = libCommon.makeIconBtn(iconPath=':/addClip_100.png', statusTip='Add node-filters based on text input', command=self.nodeTypes_addByName, iconFallBackLetter='A', iconSize=23)
        btnLayout.addWidget(btnA)

        btnB = libCommon.makeIconBtn(iconPath=':/selectByObject.png', statusTip='Add node-filters based on object selection', command=self.nodeTypes_addFromMayaSelection, iconFallBackLetter='S', iconSize=23)
        btnLayout.addWidget(btnB)

        self.baseFilterType_radioGroupParent.addSubWidgets(radioName='nodeTypes', widgets=[self.nodeTypes_widget, btnA, btnB])




        # ## ------------SELECTION FILTER OPTIONS  -------------- ##
        self.selectionFilter_groupBox = groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle('Selection Filter')
        groupBox.setObjectName('groupbox_boldTitle')
        groupBox.setCheckable(True)
        groupBox.setChecked(False)
        gridLayout.addWidget(groupBox,3,0,1,-1)
        self.selectionFilter_groupBox.toggled.connect(lambda state: self.updateFilterData(dataKey='updateSelectionFilter', dataValue=state))
        self.inputWidgets_blockToggle.append(self.selectionFilter_groupBox)


        groupBoxLayout = QtWidgets.QVBoxLayout()
        groupBoxLayout.setAlignment(QtCore.Qt.AlignLeft)
        groupBoxLayout.setContentsMargins(4,4,4,4)
        groupBoxLayout.setSpacing(4)
        groupBox.setLayout(groupBoxLayout)

        hboxLayout = QtWidgets.QHBoxLayout()
        hboxLayout.setAlignment(QtCore.Qt.AlignLeft)
        hboxLayout.setContentsMargins(0,0,0,0)
        hboxLayout.setSpacing(0)
        groupBoxLayout.addLayout(hboxLayout)

        self.checkBtn_sf_hierarchy = iconButton = libCommon.makeIconBtn(iconPath=':/selectByHierarchy.png', statusTip='Get Hierarchy', iconFallBackLetter="H", command=None, iconSize=22)
        iconButton.setCheckable(True)
        iconButton.setChecked(True)
        iconButton.toggled.connect(lambda state: self.updateFilterData(dataKey='sf_getHierarchy', dataValue=state))
        hboxLayout.addWidget(iconButton)
        self.inputWidgets_blockToggle.append(self.checkBtn_sf_hierarchy)

        label = QtWidgets.QLabel('Include Hierarchy')
        hboxLayout.addWidget(label)
        spacerItem = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        hboxLayout.addItem(spacerItem)

        self.checkBtn_sf_shaders = iconButton = libCommon.makeIconBtn(iconPath=':/out_shadingEngine.png', statusTip='Get Shading Network', iconFallBackLetter="S", command=None, iconSize=22)
        iconButton.setCheckable(True)
        iconButton.setChecked(True)
        iconButton.toggled.connect(lambda state: self.updateFilterData(dataKey='sf_getShadingNetwork', dataValue=state))
        hboxLayout.addWidget(iconButton)
        self.inputWidgets_blockToggle.append(self.checkBtn_sf_shaders)

        label = QtWidgets.QLabel('Include Shading Network')
        hboxLayout.addWidget(label)

        spacerItem = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        hboxLayout.addItem(spacerItem)

        self.checkBtn_sf_inputs = iconButton = libCommon.makeIconBtn(iconPath=':/input.png', statusTip='Get Input Connections', iconFallBackLetter="In", command=None, iconSize=22)
        iconButton.setCheckable(True)
        iconButton.setChecked(True)
        iconButton.toggled.connect(lambda state: self.updateFilterData(dataKey='sf_getInputConnections', dataValue=state))
        hboxLayout.addWidget(iconButton)
        self.inputWidgets_blockToggle.append(self.checkBtn_sf_inputs)

        label = QtWidgets.QLabel('Include Input Connections')
        hboxLayout.addWidget(label)


        hboxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.addLayout(hboxLayout)

        font = QtGui.QFont()
        font.setPointSize(7)

        label = QtWidgets.QLabel("Enables and updates Local Selection Filter when filter is activated.")
        label.setFont(font)
        hboxLayout.addWidget(label)


        # ## ------------SCRIPT FILTER OPTIONS  -------------- ##

        self.scriptFilter_groupBox = groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle('Script Filter')
        groupBox.setObjectName('groupbox_boldTitle')
        groupBox.setCheckable(True)

        groupBoxLayout = QtWidgets.QGridLayout()
        groupBoxLayout.setSpacing(4)
        groupBoxLayout.setContentsMargins(4,4,4,4)
        groupBox.setLayout(groupBoxLayout)
        gridLayout.addWidget(groupBox,4,0,1,-1)

        self.scriptFilter_groupBox.toggled.connect(lambda state: self.updateFilterData(dataKey='scriptFilter', dataValue=state))
        self.inputWidgets_blockToggle.append(self.scriptFilter_groupBox)

        hboxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.addLayout(hboxLayout, 0,0,1,-1)

        self.sf_moduleName_lineEdit = lineEdit = QtWidgets.QLineEdit()
        lineEdit.setPlaceholderText('.moduleName')

        hboxLayout.addWidget(lineEdit)
        self.sf_moduleName_lineEdit.editingFinished.connect(lambda: self.updateFilterData(dataKey='scriptModule', dataValue=self.sf_moduleName_lineEdit.text()))
        self.inputWidgets_blockToggle.append(self.sf_moduleName_lineEdit)

        self.sf_functionName_lineEdit = lineEdit = QtWidgets.QLineEdit()
        lineEdit.setPlaceholderText('functionName')

        hboxLayout.addWidget(lineEdit)
        self.sf_functionName_lineEdit.editingFinished.connect(lambda: self.updateFilterData(dataKey='scriptFunction', dataValue=self.sf_functionName_lineEdit.text()))
        self.inputWidgets_blockToggle.append(self.sf_functionName_lineEdit)

        self.sf_args_lineEdit = lineEdit = QtWidgets.QLineEdit()
        lineEdit.setPlaceholderText('arg1,arg2')
        hboxLayout.addWidget(lineEdit)
        self.sf_args_lineEdit.editingFinished.connect(lambda: self.updateFilterData(dataKey='scriptArgs', dataValue=self.sf_args_lineEdit.text()))
        self.inputWidgets_blockToggle.append(self.sf_args_lineEdit)


        vboxLayout = QtWidgets.QVBoxLayout()
        groupBoxLayout.addLayout(vboxLayout, 2,0,1,-1)

        font = QtGui.QFont()
        font.setPointSize(7)

        label = QtWidgets.QLabel("Modules paths beginning with . are relative to the plugin's scriptFilter-directory.")
        label.setFont(font)
        vboxLayout.addWidget(label)
        # label = QtWidgets.QLabel("Optional string-arguments are separated by , without spaces.<br>Number-only arguments are automatically converted to integers.")
        # label.setFont(font)
        # vboxLayout.addWidget(label)



        # ## ------------SEARCH FILTER OPTIONS  -------------- ##
        self.filterSearch_groupBox = groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle('Search Filter')
        groupBox.setObjectName('groupbox_boldTitle')
        groupBoxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.setSpacing(4)
        groupBoxLayout.setContentsMargins(4,4,4,4)
        groupBox.setLayout(groupBoxLayout)

        gridLayout.addWidget(groupBox,6,0,1,-1)

        self.searchFilter_textField = lineEdit = QtWidgets.QLineEdit()
        lineEdit.setFixedWidth(150)
        groupBoxLayout.addWidget(self.searchFilter_textField)
        self.searchFilter_textField.editingFinished.connect(lambda: self.updateFilterData(dataKey='searchString', dataValue=self.searchFilter_textField.text()))
        self.inputWidgets_blockToggle.append(self.searchFilter_textField)

        self.searchFilter_invert_checkbox = QtWidgets.QCheckBox('Invert Search')
        groupBoxLayout.addWidget(self.searchFilter_invert_checkbox)
        self.searchFilter_invert_checkbox.toggled.connect(lambda state: self.updateFilterData(dataKey='searchInvert', dataValue=state))
        self.inputWidgets_blockToggle.append(self.searchFilter_invert_checkbox)



        # ## ------------OUTLINER BEHAVIOR OPTIONS  -------------- ##
        groupBox = QtWidgets.QGroupBox()
        groupBox.setTitle('Outliner Display')
        groupBox.setObjectName('groupbox_boldTitle')
        groupBoxLayout = QtWidgets.QHBoxLayout()
        groupBoxLayout.setAlignment(QtCore.Qt.AlignLeft)
        # groupBoxLayout.setSpacing(4)
        groupBoxLayout.setContentsMargins(4,4,4,4)
        groupBox.setLayout(groupBoxLayout)

        gridLayout.addWidget(groupBox,8,0,1,-1)


        self.checkbox_ignoreHierarchy = checkBox = QtWidgets.QCheckBox('Ignore Hierarchy')
        checkBox.setStatusTip('Ignore DAG Hierarchy and display as flat list.')
        groupBoxLayout.addWidget(checkBox)
        checkBox.toggled.connect(lambda state: self.updateFilterData(dataKey='ignoreHierarchy', dataValue=state))
        self.inputWidgets_blockToggle.append(self.checkbox_ignoreHierarchy)

        self.checkbox_autoExpand =checkBox = QtWidgets.QCheckBox('Auto-Expand Hierarchy')
        checkBox.setStatusTip('All hierarchy auto-expanded.')
        groupBoxLayout.addWidget(checkBox)
        checkBox.toggled.connect(lambda state: self.updateFilterData(dataKey='expandObjects', dataValue=state))
        self.inputWidgets_blockToggle.append(self.checkbox_autoExpand)

        self.checkbox_showShapeNodes =checkBox = QtWidgets.QCheckBox('Show Shape Nodes')
        groupBoxLayout.addWidget(checkBox)
        checkBox.toggled.connect(lambda state: self.updateFilterData(dataKey='showShapes', dataValue=state))
        self.inputWidgets_blockToggle.append(self.checkbox_showShapeNodes)


        # ## ------------HELP TEXT  -------------- ##


        helpTextLayout = QtWidgets.QHBoxLayout()
        helpTextLayout.setAlignment(QtCore.Qt.AlignLeft)
        helpTextLayout.setSpacing(2)
        helpTextLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.addLayout(helpTextLayout, 9, 0, 1, -1)


        font = QtGui.QFont()
        font.setPointSize(7)

        helpText = 'Double-click a filter in the All Filters list to edit it.<br>The Preview-button will apply the filter currently edited without saving it.'
        label = QtWidgets.QLabel(helpText)
        label.setFont(font)
        helpTextLayout.addWidget(label)
        # gridLayout.addWidget(label,9,0,1,-1)

        spacer = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        helpTextLayout.addItem(spacer)

        icon = libCommon.getIconObject(':/outliner.png')
        btn = QtWidgets.QPushButton('Preview Filter')
        btn.setDefault(True)
        btn.setIcon(icon)
        helpTextLayout.addWidget(btn)
        btn.clicked.connect(self.previewFilter)



    def openFilter(self, filterName):
        self.activeFilterName = filterName
        self.activeFilterNode = self.CONFIG.getFilterNode(filterName)

        # self.filterData = self.CONFIG.getFilterData(filterName)

        for widget in self.inputWidgets_blockToggle:
            widget.blockSignals(True)


        self.filterName_label.setText(self.activeFilterName)


        iconPath = self.activeFilterNode.getData('icon')
        self.filterIcon_editField.setText(iconPath)
        iconObject = libCommon.getIconObject(iconPath)
        self.iconPixmap = iconObject.pixmap(QtCore.QSize(25,25))
        self.filterIcon_iconPreview.setPixmap(self.iconPixmap)

        self.baseFilter_groupBox.setChecked(self.activeFilterNode.getData('baseFilter'))
        self.baseFilterType_radioGroupParent.setChecked_byName(self.activeFilterNode.getData('baseFilterType'))
        self.nodeFilterPresetMenu_menu.setCurrentText(self.activeFilterNode.getData('internalFilter'))
        self.nodeTypes_widget.clear()
        self.nodeTypes_widget.addItems(self.activeFilterNode.getData('nodeTypes'))


        self.selectionFilter_groupBox.setChecked(self.activeFilterNode.getData('selectionFilter'))
        self.checkBtn_sf_hierarchy.setChecked(self.activeFilterNode.getData('sf_getHierarchy'))
        self.checkBtn_sf_shaders.setChecked(self.activeFilterNode.getData('sf_getShadingNetwork'))
        self.checkBtn_sf_inputs.setChecked(self.activeFilterNode.getData('sf_getInputConnections'))

        self.scriptFilter_groupBox.setChecked(self.activeFilterNode.getData('scriptFilter'))
        self.sf_moduleName_lineEdit.setText(self.activeFilterNode.getData('scriptModule'))
        self.sf_functionName_lineEdit.setText(self.activeFilterNode.getData('scriptFunction'))
        self.sf_args_lineEdit.setText(self.activeFilterNode.getData('scriptArgs'))

        self.searchFilter_textField.setText(self.activeFilterNode.getData('searchString'))
        self.searchFilter_invert_checkbox.setChecked(self.activeFilterNode.getData('searchInvert'))

        self.checkbox_ignoreHierarchy.setChecked(self.activeFilterNode.getData('ignoreHierarchy'))
        self.checkbox_autoExpand.setChecked(self.activeFilterNode.getData('expandObjects'))
        self.checkbox_showShapeNodes.setChecked(self.activeFilterNode.getData('showShapes'))

        for widget in self.inputWidgets_blockToggle:
            widget.blockSignals(False)



    def renameFilter(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'Rename Filter:', 'New filter name:', QtWidgets.QLineEdit.Normal, self.activeFilterName)
        if ok:
            newName = text
        else:
            return

        if newName == self.activeFilterName:
            return

        newName = self.CONFIG.filter_rename(self.activeFilterName, newName)
        self.openFilter(newName)


    def previewFilter(self):
        activeFilter = self.activeFilterName
        outliner = self.parent().parent().parent().parent().getOutlinerTarget()

        filterNode = self.CONFIG.getFilterNode(activeFilter)

        scriptFilter = filterNode.getData('scriptFilter')
        moduleName = filterNode.getData("scriptModule")
        if scriptFilter and moduleName:
            _ = libCommon.getModule(moduleName, reloadModule=True)

        # outliner.setFilter_byPreset(filterNode)
        outliner.setFilter_byPreset(activeFilter)
        output = outliner.outlinerWidget.queryFilter()
        if output:
            print('Preview Filter result:', len(output), libMaya.nodeList_makeShortNames(output))


    def iconUpdated(self, iconPath):
        self.updateFilterData(dataKey='icon', dataValue=iconPath)

        iconObject = libCommon.getIconObject(iconPath)
        self.iconPixmap = iconObject.pixmap(QtCore.QSize(25,25))
        self.filterIcon_iconPreview.setPixmap(self.iconPixmap)

    def browseMayaIcons(self):
        iconPath = libMaya.openIconBrowser()
        if not iconPath:
            return
        iconPath = ':/%s'%(iconPath)
        self.filterIcon_editField.setText(iconPath)
        self.iconUpdated(iconPath)


    def browseIcons_explorer(self):
        options = QtWidgets.QFileDialog.Options()
        fileFilter = "Images (*.png *.jpg *.svg)"
        filePaths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Choose icon image", ks_nodeOutliner._ICON_DIR_, fileFilter, options=options)
        if not filePaths:
            return
        iconPath = filePaths[0]
        if ks_nodeOutliner._ICON_DIR_ in iconPath:
            iconPath = iconPath.replace(ks_nodeOutliner._ICON_DIR_, ':/')
        self.filterIcon_editField.setText(iconPath)
        self.iconUpdated(iconPath)


    def updateFilterData(self, dataKey=None, dataValue=None):
        if not self.activeFilterNode:
            return
        self.activeFilterNode.setData(dataKey, dataValue)


    def nodeTypes_addFromMayaSelection(self):
        nodeTypes = libMaya.nodeTypesFromSelection()
        self.nodeTypes_widget.importList(nodeTypes)


    def nodeTypes_addByName(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "Add List Items", "Write items separated by commas", QtWidgets.QLineEdit.Normal, "")
        if not text:
            return None
        text = text.replace(' ', '')
        itemList = text.split(',')
        self.nodeTypes_widget.importList(itemList)







# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ----------------------------------------MENU PRESET EDIT --------------------------------------------- #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #








class GUI_editMenuPreset(QtWidgets.QWidget):
    def __init__(self, parent=None, **kwargs):
        super(GUI_editMenuPreset, self).__init__(parent=parent, **kwargs)

        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)

        self.CONFIG = config.configuration()

        self.activePreset = None
        self.presetData = None


        self.buildUI()

        self._populate_menuPresetsMenu()

    def buildUI(self):
        menuPresets_rootLayout = QtWidgets.QGridLayout()
        menuPresets_rootLayout.setContentsMargins(5, 5, 5, 5)
        menuPresets_rootLayout.setSpacing(5)
        menuPresets_rootLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.setLayout(menuPresets_rootLayout)


        hboxLayout = QtWidgets.QHBoxLayout()
        hboxLayout.setSpacing(2)
        hboxLayout.setContentsMargins(0, 0, 0, 0)
        hboxLayout.setAlignment(QtCore.Qt.AlignLeft)
        menuPresets_rootLayout.addLayout(hboxLayout, 0, 0, 1, -1)


        self.menuPresets_combobox = combobox = QtWidgets.QComboBox()
        combobox.setFixedHeight(30)
        combobox.setFixedWidth(200)
        font = combobox.font()
        # font.setBold(True)
        font.setPointSize(12)
        combobox.setFont(font)
        hboxLayout.addWidget(self.menuPresets_combobox)
        self.menuPresets_combobox.currentTextChanged.connect(lambda presetName: self.openMenuPreset(presetName))


        btn = libCommon.makeIconBtn(iconPath=':/addClip_100.png', statusTip='Create New Menu-Preset', iconFallBackLetter='+', iconSize=30)
        btn.clicked.connect(self.menuPreset_addNew)
        hboxLayout.addWidget(btn)


        btn = libCommon.makeIconBtn(iconPath=':/deleteGeneric.png', statusTip='Delete Current Menu-Preset', iconFallBackLetter='-', iconSize=30)
        btn.clicked.connect(self.menuPreset_delete)
        hboxLayout.addWidget(btn)

        spacerItem = QtWidgets.QSpacerItem(10,10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        hboxLayout.addItem(spacerItem)



        #
        # ----- Filter Menus --------#
        #

        vboxLayout = QtWidgets.QVBoxLayout()
        vboxLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        menuPresets_rootLayout.addLayout(vboxLayout, 1, 0, 1, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        label = QtWidgets.QLabel('Icon Menu')
        self.iconMenu_listWidget = listWidget = listWidget_menuPresetList(self)
        listWidget.setClipboardGroup('filterList')
        listWidget.setFixedWidth(120)
        self.iconMenu_listWidget.setListName("iconMenu")
        self.iconMenu_listWidget.modified.connect(lambda:self.menuPreset_updateList(self.iconMenu_listWidget, "iconMenu"))

        vboxLayout.addWidget(label)
        vboxLayout.addWidget(listWidget)


        vboxLayout = QtWidgets.QVBoxLayout()
        vboxLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        menuPresets_rootLayout.addLayout(vboxLayout, 1, 1, 1, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        label = QtWidgets.QLabel('Outliner Menu')
        self.outlinerMenu_listWidget = listWidget = listWidget_menuPresetList(self)
        listWidget.setClipboardGroup('filterList')
        listWidget.setFixedWidth(120)
        self.outlinerMenu_listWidget.setListName("outlinerMenu")
        self.outlinerMenu_listWidget.modified.connect(lambda:self.menuPreset_updateList(self.outlinerMenu_listWidget, "outlinerMenu"))

        vboxLayout.addWidget(label)
        vboxLayout.addWidget(listWidget)


        # ----- Defaults Menu --------#
        vboxLayout = QtWidgets.QVBoxLayout()
        vboxLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        menuPresets_rootLayout.addLayout(vboxLayout, 1, 2, 1, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        label = QtWidgets.QLabel('Default Filter #1')
        vboxLayout.addWidget(label)
        self.defaultFilterA_listWidget = listWidget_singleItem(self)
        self.defaultFilterA_listWidget.setClipboardGroup('filterList')
        self.defaultFilterA_listWidget.setListName("defaultFilter_nodeOutlinerA")
        vboxLayout.addWidget(self.defaultFilterA_listWidget)
        self.defaultFilterA_listWidget.modified.connect(lambda:self.menuPreset_updateList(self.defaultFilterA_listWidget, "defaultFilter_nodeOutlinerA"))

        label = QtWidgets.QLabel('Default Filter #2')
        vboxLayout.addWidget(label)
        self.defaultFilterB_listWidget = listWidget_singleItem(self)
        self.defaultFilterB_listWidget.setClipboardGroup('filterList')
        self.defaultFilterB_listWidget.setListName("defaultFilter_nodeOutlinerB")
        vboxLayout.addWidget(self.defaultFilterB_listWidget)
        self.defaultFilterB_listWidget.modified.connect(lambda:self.menuPreset_updateList(self.defaultFilterB_listWidget, "defaultFilter_nodeOutlinerB"))

        # spacerItem = QtWidgets.QSpacerItem(10,50, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        # defaults_layout.addItem(spacerItem)



        helpTextLayout = QtWidgets.QHBoxLayout()
        helpTextLayout.setSpacing(2)
        helpTextLayout.setContentsMargins(0, 0, 0, 0)
        helpTextLayout.setAlignment(QtCore.Qt.AlignLeft)
        menuPresets_rootLayout.addLayout(helpTextLayout, 2, 0, 1, -1)


        font = QtGui.QFont()
        font.setPointSize(7)

        helpText = 'Drag and Drop from the All Filters list into the menu-lists.<br>Copy, Paste and Remove is available in right-click menu. '
        label = QtWidgets.QLabel(helpText)
        label.setFont(font)
        helpTextLayout.addWidget(label)


    def _populate_menuPresetsMenu(self):
        self.menuPresets_combobox.blockSignals(True)
        self.menuPresets_combobox.clear()
        self.menuPresets_combobox.addItems(sorted(self.CONFIG.getMenuPresetNames()))
        self.menuPresets_combobox.setCurrentIndex(0)
        self.menuPresets_combobox.blockSignals(False)
        self.openMenuPreset(self.menuPresets_combobox.currentText())


    def menuPreset_addNew(self):
        presetName, confirmState = QtWidgets.QInputDialog.getText(self, 'Add new menu preset:', 'Preset Name:', QtWidgets.QLineEdit.Normal, '')
        if not confirmState:
            return
        # presetName, confirmState = QtWidgets.QInputDialog.getText('Add new menu preset:', 'Preset Name:', QtWidgets.QLineEdit.Normal, '')
        # if not confirmState:
        #     return

        presetName = self.CONFIG.menuPreset_addNew(presetName)
        self.menuPresets_combobox.addItems([presetName])
        # self._populate_menuPresetsMenu()

    def menuPreset_delete(self):
        currentPreset = self.menuPresets_combobox.currentText()
        self.CONFIG.menuPreset_delete(currentPreset)
        self._populate_menuPresetsMenu()

    def openMenuPreset(self, presetName):
        self.activePreset = presetName
        self.presetData = self.CONFIG.menuPreset_getDict(presetName)

        listWidgets = [self.outlinerMenu_listWidget, self.iconMenu_listWidget, self.defaultFilterA_listWidget, self.defaultFilterB_listWidget]
        # print 'Opening presetName:', presetName
        for listWidget in listWidgets:
            listWidget.blockSignals(True)
            listWidget.clear()
            listName = listWidget.getListName()
            # print 'Opening listName:', listName
            filterList = self.CONFIG.menuPreset_getList(presetName, listName)
            for filterName in filterList:
                item = QtWidgets.QListWidgetItem(filterName)
                filterNode = self.CONFIG.getFilterNode(filterName)
                libCommon.setIcon_listItem(item, filterNode.getData('icon'))
                listWidget.addItem(item)

            listWidget.blockSignals(False)

    def refresh(self):
        self.openMenuPreset(self.activePreset)

    def menuPreset_updateList(self, listWidget, listName):
        if self.activePreset is None:
            return

        self.CONFIG.menuPreset_setList(self.activePreset, listName, listWidget.exportList())





# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #
# ---------------------------------------- MISC -------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------ #


class baseListWidget(QtWidgets.QListWidget):
    modified = pyqtSignal()
    itemsDeleted = pyqtSignal(list)
    _CLIPBOARD_ = {}

    def __init__(self, parent=None):
        super(baseListWidget, self).__init__(parent=parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setAcceptDrops(True)
        # self.iconsEnabled = True

        self.listName = None
        self.clipboardGroup = 'defaultClipboard'


        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.ContextMenuEvent)
        self.build_contextMenu()

    def getListName(self):
        return self.listName

    def setListName(self, listName):
        self.listName = listName

    def getSelectedItems(self):
        itemNames = []
        for item in self.selectedItems():
            itemNames.append(item.text())

        return itemNames

    # def importListDict(self, listDict):
    #     for filterName, index in sorted(listDict.iteritems(), key=lambda (k,v): (v,k)):
    #         item = QtWidgets.QListWidgetItem(filterName)
    #         self.addItem(item)

    # def exportListDict(self):
    #     listDict = {}
    #     for index in range(self.count()):
    #         itemName = self.item(index).text()
    #         listDict[itemName] = index
    #     return listDict


    def importList(self, itemList):
        existingItems = [str(self.item(i).text()) for i in range(self.count())]
        newItems = list(set(itemList) - set(existingItems))
        self.addItems(newItems)
        self.modified.emit()

    def exportList(self):
        listItems = [str(self.item(i).text()) for i in range(self.count())]
        return listItems

    def getClipboard(cls, clipboardGroup):
        return cls._CLIPBOARD_.get(clipboardGroup, [])

    def setClipboard(cls, clipboardGroup, content):
        cls._CLIPBOARD_[clipboardGroup] = content

    def setClipboardGroup(self, clipboardGroup):
        self.clipboardGroup = clipboardGroup

    def copyToClipboard(self):
        dataList = self.getSelectedItems()
        self.setClipboard(self.clipboardGroup, dataList)

    def pasteFromClipboard(self):
        clipboardData = self.getClipboard(self.clipboardGroup)
        self.importList(clipboardData)
        self.modified.emit()

    def dropEvent(self, event):
        sourceWidget = event.source()

        if self == sourceWidget:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(baseListWidget, self).dropEvent(event)
        else:
            event.setDropAction(QtCore.Qt.CopyAction)
            super(baseListWidget, self).dropEvent(event)
            self.cleanupDuplicates()

        self.modified.emit()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_selection()


    def delete_selection(self):
        deletedItems = []
        for item in self.selectedItems():
            deletedItems.append(item.text())
            self.takeItem(self.row(item))

        self.modified.emit()
        self.itemsDeleted.emit(deletedItems)

    def delete_byNames(self, names):
        if not type(names) == list:
            names = [names]
        for itemText in names:
            item = self.findItems(itemText, QtCore.Qt.MatchExactly)
            if item:
                self.takeItem(self.row(item))
        self.modified.emit()

    def cleanupDuplicates(self):
        indexRange = list(range(self.count()))
        self.blockSignals(True)
        for i in reversed(indexRange):
            item = self.item(i)
            if not item:
                continue
            itemText = item.text()
            if itemText == '':
                self.takeItem(self.row(item))
            if item.font().bold():
                self.takeItem(self.row(item))
            if len(self.findItems(itemText, QtCore.Qt.MatchExactly)) > 1:
                self.takeItem(self.row(item))

        self.blockSignals(False)




    def build_contextMenu(self):
        self.contextMenu = QtWidgets.QMenu(self)

        self.contextMenu.addAction("Copy", self.copyToClipboard)
        self.contextMenu.addAction("Paste", self.pasteFromClipboard)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction("Remove", self.delete_selection)


    def ContextMenuEvent(self, pos):
        self.contextMenu.exec(self.mapToGlobal(pos))



class listWidget_menuPresetList(baseListWidget):
    def __init__(self, parent=None):
        super(listWidget_menuPresetList, self).__init__(parent=parent)

        self.listName = None
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)


    def dropEvent(self, event):
        sourceWidget = event.source()

        if self == sourceWidget:
            event.setDropAction(QtCore.Qt.MoveAction)
            super(listWidget_menuPresetList, self).dropEvent(event)
        else:
            event.setDropAction(QtCore.Qt.CopyAction)
            super(listWidget_menuPresetList, self).dropEvent(event)
            # self.cleanupDuplicates()


class listWidget_allFilters(baseListWidget):

    def __init__(self, parent=None):
        super(listWidget_allFilters, self).__init__(parent=parent)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        sourceWidget = event.source()
        if self == sourceWidget:
            event.setDropAction(QtCore.Qt.MoveAction)
        else:
            event.setDropAction(QtCore.Qt.IgnoreAction)
        super(listWidget_allFilters, self).dragEnterEvent(event)


    def dropEvent(self, event):
        # Drop event is set to Internal Move when moving objects internally.
        # After every drop-event it resets back to DragDrop mode, so that it will not remove items
        # from list when dropped into other lists.
        sourceWidget = event.source()
        if self == sourceWidget:
            self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
            super(listWidget_allFilters, self).dropEvent(event)
        else:
            event.setDropAction(QtCore.Qt.IgnoreAction)
            event.ignore()


    def build_contextMenu(self):
        self.contextMenu = QtWidgets.QMenu(self)

        self.contextMenu.addSeparator()
        self.contextMenu.addAction("Delete", self.delete_selection)



class listWidget_singleItem(baseListWidget):
    def __init__(self, parent=None):
        super(listWidget_singleItem, self).__init__(parent)
        self.setMaximumHeight(22)
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setAcceptDrops(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.setDropIndicatorShown(False)

        self.listName = None

    def importList(self, itemList):
        self.clear()
        self.addItem(itemList[0])

    def dropEvent(self, event):
        self.clear()
        event.setDropAction(QtCore.Qt.CopyAction)

        item = self.item(0)

        itemCount = self.count()
        if itemCount > 1:
            for i in reversed(list(range(1, itemCount))):
                item = self.item(i)
                self.takeItem(self.row(item))

        super(listWidget_singleItem, self).dropEvent(event)
        # self.modified.emit()




class ks_radioGroup_noWidget(QtCore.QObject):
    stateChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super(ks_radioGroup_noWidget, self).__init__(parent)
        self.radioDict = {}

    def addRadioBtn(self, widget, radioName):
        self.radioDict[radioName] = {'widget':widget, 'subWidgets':[]}
        widget.clicked.connect(lambda: self.emitSignal(radioName))
        widget.toggled.connect(lambda state: self.widgetToggled(radioName, state))

    def addSubWidgets(self, radioName, widgets=[]):
        if not type(widgets) == list:
            widgets = [widgets]

        parentWidget = self.radioDict[radioName].get('widget')
        checked = parentWidget.isChecked()
        for widget in widgets:
            self.radioDict[radioName]['subWidgets'].append(widget)
            if not checked:
                widget.setEnabled(False)

    def setChecked_byName(self, radioName):
        if not radioName:
            return
        widget = self.radioDict[radioName].get('widget')
        widget.setChecked(True)

    def widgetToggled(self, radioName, state):
        for widget in self.radioDict[radioName].get('subWidgets'):
            widget.setEnabled(state)

    def emitSignal(self, radioName):
        self.stateChanged.emit(radioName)





if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    outlinerGUI = GUI_FilterManager()
    outlinerGUI.show()
    app.exec()
