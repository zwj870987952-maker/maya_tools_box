# -*- coding: utf-8 -*-
from .runtime import ui_cmds as cmds
import maya.mel as mel
import os
import json
import decimal
import colorsys
from functools import partial
from functools import wraps
from collections import OrderedDict
from operator import itemgetter
import traceback
import copy

from . import qt_compat as Qt

'''
- retro compatible
- resize the upper window including the retime
'''

'''
todo:
* File, import/export
* Progress bars
* Hide display
* connect custom attribute
* disable add/remove when no retime selected
'''
# compatibility
# https://python-future.org/_modules/future/utils.html
# https://python-future.org/compatible_idioms.html
def iteritems(obj, **kwargs):
    """Use this only if compatibility with Python versions before 2.7 is
    required. Otherwise, prefer viewitems().
    """
    func = getattr(obj, "iteritems", None)
    if not func:
        func = obj.items
    return func(**kwargs)

class Window(Qt.QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        parent = QTHelpers.get_main_window()

        '''
        set parent
        '''
        super(Window, self).__init__(parent)

        '''
        set title
        '''
        windowTitle = u'eblabs Retime Tools 【帝都儿汉化】'
        self.setObjectName('mtkRetimeCandidateWindow')
        self.setWindowTitle(windowTitle)

        '''
        set window flags
        '''
        '''
        self.setWindowFlags(
            Qt.QtCore.Qt.Window |
            Qt.QtCore.Qt.CustomizeWindowHint |
            Qt.QtCore.Qt.WindowTitleHint |
            Qt.QtCore.Qt.WindowCloseButtonHint
            )
        '''
        self.setWindowFlags(

            Qt.QtCore.Qt.CustomizeWindowHint |
            Qt.QtCore.Qt.WindowTitleHint |
            Qt.QtCore.Qt.WindowCloseButtonHint |
            Qt.QtCore.Qt.Tool
            )

        '''
        main layout for Document
        '''
        self.main_layout = VBoxLayout(self)
        self.main_layout.setObjectName('main_layout')
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

    def display(self):


        '''
        deffered add document
        '''
        self.main_document = Document(self)
        self.main_layout.addWidget(self.main_document)

        '''
        set size
        '''
        self.resize(800, 700)
        self.show()

class RetimeStates(object):
    Enable = 1
    Disable = 2
    Reset = 3
    Invert = 4
    Disconnect = 5
    Delete = 6

    @classmethod
    def get_state_for_string(cls, value):
        '''
        lookup table
        '''
        state_lookup = {}
        state_lookup[u'启用'] = RetimeStates.Enable
        state_lookup[u'禁用'] = RetimeStates.Disable
        state_lookup[u'重置'] = RetimeStates.Reset
        state_lookup[u'反向'] = RetimeStates.Invert
        state_lookup[u'断开连接'] = RetimeStates.Disconnect
        state_lookup[u'删除'] = RetimeStates.Delete

        '''
        return with fallback
        '''
        return state_lookup.get(value, RetimeStates.Enable)

    @classmethod
    def get_state_for_int(cls, value):
        '''
        lookup table
        '''
        state_lookup = {}
        state_lookup[1] = RetimeStates.Enable
        state_lookup[2] = RetimeStates.Disable
        state_lookup[3] = RetimeStates.Reset
        state_lookup[4] = RetimeStates.Invert
        state_lookup[5] = RetimeStates.Disconnect
        state_lookup[6] = RetimeStates.Delete

        '''
        return with fallback
        '''
        return state_lookup.get(value, 1)

    @classmethod
    def get_string_for_int(cls, value):
        '''
        lookup table
        '''
        state_lookup = {}
        state_lookup[1] = u'启用'
        state_lookup[2] = u'禁用'
        state_lookup[3] = u'重置'
        state_lookup[4] = u'反向'
        state_lookup[5] = u'断开连接'
        state_lookup[6] = u'删除'

        '''
        return with fallback
        '''
        return state_lookup.get(value, 1)

class Document(Qt.QtWidgets.QWidget):
    '''
    Display Packages and Information
    '''

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)
        '''
        main layout
        '''
        self.main_layout = GridLayout(self)
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop | Qt.QtCore.Qt.AlignLeft)

        '''
        menu bar
        '''
        self.main_menu_bar = Qt.QtWidgets.QMenuBar(self)
        self.main_layout.addWidget(self.main_menu_bar, 0, 0, 1, 2)
        self.main_layout.setAlignment(self.main_menu_bar, Qt.QtCore.Qt.AlignLeft)

        '''
        build menus
        '''
        self.add_user_menu_items(self.main_menu_bar)

        # sides
        left_side = GridWidget(self)
        right_side = GridWidget(self)
        self.main_layout.addWidget(left_side, 1, 0, 1, 1)
        self.main_layout.addWidget(right_side, 1, 1, 1, 1)

        #
        splitter = Qt.QtWidgets.QSplitter(left_side)
        splitter.setMinimumSize(Qt.QtCore.QSize(0, 0))
        splitter.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        splitter.setOrientation(Qt.QtCore.Qt.Vertical)
        left_side.main_layout.addWidget(splitter, 0, 0, 1, 1)

        '''
        timewarp list
        '''
        self.retime_control_widget = ControlersWidget(left_side)
        self.retime_connections_list = ConnectionsWidget(left_side)
        self.retime_actions_list = ActionsWidget(right_side)

        self.retime_control_widget.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        self.retime_connections_list.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        self.retime_actions_list.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)

        #self.retime_control_widget.setFixedHeight(200)
        right_side.setFixedWidth(300)

        splitter.addWidget(self.retime_control_widget)
        splitter.addWidget(self.retime_connections_list)
        #left_side.main_layout.addWidget(self.retime_control_widget, 1, 0, 1, 1)
        #left_side.main_layout.addWidget(self.retime_connections_list, 2, 0, 1, 1)
        right_side.main_layout.addWidget(self.retime_actions_list, 1, 1, 2, 1)

        '''
        update elements
        '''
        self.retime_control_widget.update()

        self.setup_signals()

    def setup_signals(self):
        '''
        retime controllers
        '''
        self.retime_actions_list.scene_change.connect(self.retime_control_widget.update)

        '''
        connections
        '''
        self.retime_control_widget.selection_change.connect(self.retime_connections_list.on_data_change)
        self.retime_actions_list.scene_change.connect(self.retime_connections_list.update)
        self.retime_control_widget.valid_selection_change.connect(self.retime_connections_list.set_valid)

        '''
        actions
        '''
        self.retime_control_widget.selection_change.connect(self.retime_actions_list.on_data_change)
        self.retime_control_widget.valid_selection_change.connect(self.retime_actions_list.set_valid)

    def add_user_menu_items(self, menu):
        '''
        main menu, User
        '''
        main_menu = menu.addMenu(u"文件")

        '''
        items
        '''
        #sub_menu = main_menu.addMenu('Import/Export')
        item = main_menu.addAction(u'导入重定时')
        item.triggered.connect(self.import_retime)
        item.setEnabled(False)
        item = main_menu.addAction(u'导出重定时')
        item.triggered.connect(self.export_retime)
        item.setEnabled(False)
        item = main_menu.addAction(u'更新重定时曲线')
        item.triggered.connect(self.update_old_retime_curves)
        item.setEnabled(True)

    def import_retime(self):
        print(267, 'import_retime')

    def export_retime(self):
        print(270, 'export_retime')

    def update_old_retime_curves(self):
        CoreFunctions.update_old_retime_curves()

class LayoutWidget(object):

    def __init__(self, *args, **kwargs):
        super(LayoutWidget, self).__init__(*args, **kwargs)
        '''
        '''
        self.internal_data = False

        '''
        main layout
        '''
        self.main_layout = GridLayout(self)
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop | Qt.QtCore.Qt.AlignLeft)

        '''
        layout
        '''
        self.do_layout()

    def set_data(self, data):
        self.internal_data = data
        self.on_set_data()

    def get_data(self):
        return self.internal_data

    def do_layout(self):
        '''
        virtual override
        '''

    def update(self):
        '''
        virtual override
        '''

    def on_selection_change(self):
        '''
        virtual override
        '''

    def on_set_data(self):
        '''
        virtual override
        '''


class ActionsWidget(LayoutWidget, Qt.QtWidgets.QWidget):
    scene_change = Qt.QtCore.Signal()
    valid_selection_change = Qt.QtCore.Signal(bool)

    def __init__(self, *args, **kwargs):
        super(ActionsWidget, self).__init__(*args, **kwargs)

    def do_layout(self):
        '''
        elemetns
        '''
        self.main_list = ScrollableLayoutWidget(self)
        self.main_layout.addWidget(self.main_list, 0, 0, 1, 1)

        '''
        configure buttons
        '''
        d = OrderedDict()

        '''
        Main Group
        '''
        d[u'主体'] = OrderedDict()

        '''
        Create New Retime
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = False
        kwargs['button_label'] = u'创 建 新 的 重 定 时 控 制 器'
        kwargs['button_confirm_required'] = False
        kwargs['button_okay_command'] = self.create_new_retime_controller
        kwargs['button_message'] = ''
        kwargs['button_checkbox_message'] = ''
        kwargs['button_is_valid_checking'] = False
        d[u'主体'][u'创 建 新 的 重 定 时 控 制 器'] =  kwargs

        '''
        Bake Group
        '''
        d[u'烘焙'] = OrderedDict()

        '''
        Bake Retime
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = False
        kwargs['button_label'] = u'烘 焙 重 定 时'
        kwargs['button_confirm_required'] = True
        kwargs['button_okay_command'] = self.action_bake
        kwargs['button_message'] = 'Bake Retime?'
        kwargs['button_checkbox_message'] = ''
        kwargs['display_message'] = False
        kwargs['display_checkbox'] = False
        kwargs['button_is_valid_checking'] = True
        d[u'烘焙'][u'烘 焙 重 定 时'] = kwargs

        '''
        Shuffle Keys
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = False
        kwargs['button_label'] = u'重 新 排 列 关 键 帧'
        kwargs['button_confirm_required'] = True
        kwargs['button_okay_command'] =  self.action_shuffle
        kwargs['button_message'] = u'重 新 排 列 关 键 帧 选 项'
        kwargs['button_checkbox_message'] = u'清理小数帧？'
        kwargs['button_checkbox_initial_state'] = True
        kwargs['display_message'] = True
        kwargs['display_checkbox'] = True
        kwargs['button_is_valid_checking'] = True
        d[u'烘焙'][u'重 新 排 列 关 键 帧'] = kwargs

        '''
        Tools
        '''
        d[u'工具'] = OrderedDict()

        '''
        Shuffle Keys
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = False
        kwargs['button_label'] = u'清 理 小 数 帧'
        kwargs['button_confirm_required'] = False
        kwargs['button_okay_command'] =  CoreFunctions.cleanSubframeKeys
        kwargs['button_message'] = ''
        kwargs['button_checkbox_message'] = ''
        kwargs['button_is_valid_checking'] = False
        d[u'工具'][u'清 理 小 数 帧'] = kwargs

        '''
        build buttons
        '''
        for section in d.keys():
            '''
            create sections
            '''
            section_widget = CollapsableWidget(self.main_list)
            section_widget.set_section_label(section)
            self.main_list.add_widget(section_widget)

            for action, kwargs in iteritems(d[section]):

                '''
                set parent
                '''
                kwargs['parent'] = section_widget

                '''
                create widget
                '''
                w = ConfirmButton(**kwargs)

                '''
                valid checking callback
                '''
                self.valid_selection_change.connect(partial(self.set_valid_item, w))

                '''
                add to ui
                '''
                section_widget.add_widget(w)

        '''
        update valid
        '''
        self.set_valid(False)

    def set_valid(self, state):
        self.valid_selection_change.emit(state)

    def set_valid_item(self, widget, state):
        widget.set_valid(state)

    def action_clean_subframes(self, *args, **kwargs):
        '''
        * get curve
        * clean
        '''
        CoreFunctions.cleanSubframeKeys()

    def action_bake(self, *args, **kwargs):
        '''
        * bake
        * refresh
        '''
        retime_controller = self.get_data()
        if not retime_controller:
            return False

        CoreFunctions.bake_retime_controller(retime_controller)

        '''
        signal update event
        '''
        self.scene_change.emit()

    def action_shuffle(self, *args, **kwargs):
        '''
        * bake
        * disconnect
        * refresh
        '''

        '''
        check
        '''
        retime_controller = self.get_data()
        if not retime_controller:
            return False

        '''
        get state
        '''
        state = False
        if args:
            state = args[0]
        #print(448, 'state', state)

        '''
        undo chunck
        '''

        '''
        shuffle
        '''
        animCurves = False
        if state:
            animCurves = CoreFunctions.getCurvesAttachedToRetime(retime_controller)
        ShuffleKeys.process(retime_controller)
        CoreFunctions.completely_disconnect_retime(retime_controller)

        '''
        clean subframe keys
        '''
        if state and animCurves:
            CoreFunctions.cleanSubframeKeys(curve_nodes=animCurves)

        '''
        undo chunck
        '''

        '''
        signal update event
        '''
        self.scene_change.emit()

    def on_data_change(self, retime_curve, *args, **kwargs):
        '''
        on selection change, this sets the internal data for the widget and then triggers a UI update
        '''

        '''
        store data
        '''
        self.set_data(retime_curve)

    def create_new_retime_controller(self, *args, **kwargs):
        '''
        preserve selections
        '''
        selection = cmds.ls(sl=True)

        '''
        create new retime
        '''
        CoreFunctions.create_new_retime_controller()

        '''
        signal update event
        '''
        self.scene_change.emit()

        '''
        reselect
        '''
        cmds.select(selection, replace=True)


class ConnectionsWidget(LayoutWidget, Qt.QtWidgets.QWidget):
    valid_selection_change = Qt.QtCore.Signal(bool)

    def __init__(self, *args, **kwargs):
        super(ConnectionsWidget, self).__init__(*args, **kwargs)

    def do_layout(self):
        '''
        elemetns
        '''
        self.main_list = DictTree() # ListWidget(self)

        '''
        add button
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = self
        kwargs['button_label'] = u'添加对象'
        kwargs['button_okay_command'] = self.on_click_add_objects
        kwargs['button_is_valid_checking'] = True
        kwargs['button_confirm_required'] = False
        add_button = ConfirmButton(**kwargs)
        self.valid_selection_change.connect(partial(self.set_valid_item, add_button))

        '''
        remove button
        '''
        kwargs = ConfirmButton.get_kwarg_template()
        kwargs['parent'] = self
        kwargs['button_label'] = u'移除对象'
        kwargs['button_confirm_required'] = True
        kwargs['button_okay_command'] = self.on_click_remove_objects
        kwargs['button_is_valid_checking'] = True
        subtract_button = ConfirmButton(**kwargs)
        self.valid_selection_change.connect(partial(self.set_valid_item, subtract_button))

        '''
        expanding
        '''
        for w in [self.main_list, add_button, subtract_button]:
            w.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding,Qt.QtWidgets.QSizePolicy.Expanding)

        '''
        sizing
        '''
        for w in [add_button, subtract_button]:
            w.setFixedHeight(40)

        '''
        layout
        '''
        self.main_layout.addWidget(self.main_list, 1, 0, 1, 2)
        self.main_layout.addWidget(add_button, 0, 0, 1, 1)
        self.main_layout.addWidget(subtract_button, 0, 1, 1, 1)

        '''
        commands
        '''
        self.main_list.items_clicked.connect(self.on_click_item)
        #add_button.clicked.connect(self.on_click_add_objects)
        #subtract_button.clicked.connect(self.on_click_remove_objects)

        '''
        update valid
        '''
        self.set_valid(False)

    def on_click_item(self):
        '''
        '''
        selected_items = self.main_list.selectedItems()
        maya_nodes = self.main_list.get_top_parents(selected_items)
        CoreFunctions.select_maya_nodes(maya_nodes)

    def on_click_remove_objects(self, *args, **kwargs):
        '''
        get some data
        '''
        selected_items = self.main_list.selectedItems()
        connections = self.main_list.get_end_children(selected_items)

        '''
        '''
        retime_controller = self.get_data()
        CoreFunctions.disconnect_curve(retime_controller, connections)

        '''
        update UI
        '''
        self.update()


    def on_click_add_objects(self, *args, **kwargs):
        '''
        get some data
        '''
        retime_curve = self.get_data()
        if not retime_curve:
            return False

        '''
        undo chunck
        '''

        '''
        launch add function
        '''
        CoreFunctions.addCurvesToTimewarp(retime_curve)

        #

        '''
        update UI
        '''
        self.update()

    def on_data_change(self, retime_curve, *args, **kwargs):
        '''
        on selection change, this sets the internal data for the widget and then triggers a UI update
        '''

        '''
        store data
        '''
        self.set_data(retime_curve)

    def on_set_data(self):
        '''
        post data update
        '''
        self.update()

    def update(self):
        '''

        clear
        '''
        self.main_list.clear()

        connections_data = CoreFunctions.get_hierarchical_connection_info_from_retime(self.get_data())
        if not connections_data:
            return False
        #print( json.dumps(connections_data, sort_keys=True, indent=4))

        '''
        check this out about creating a tree view from dict
        '''
        self.main_list.set_dict_data(connections_data)
        #https://stackoverflow.com/questions/21805047/qtreewidget-to-mirror-python-dictionary

    def set_valid(self, state):
        self.valid_selection_change.emit(state)

    def set_valid_item(self, widget, state):
        widget.set_valid(state)

class ControlersWidget(LayoutWidget, Qt.QtWidgets.QWidget):
    selection_change = Qt.QtCore.Signal(str)
    valid_selection_change = Qt.QtCore.Signal(bool)

    def __init__(self, *args, **kwargs):
        super(ControlersWidget, self).__init__(*args, **kwargs)

    def do_layout(self):
        '''
        elemetns
        '''
        self.main_list = ListWidget(self)
        #self.new_button = Qt.QtWidgets.QPushButton('Create New Retime', self)

        #self.new_button.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)

        #self.main_layout.setColumnStretch(0, 1)
        #self.new_button.setFixedWidth(200)

        self.main_layout.addWidget(self.main_list, 0, 0, 1, 1)
        #self.main_layout.addWidget(self.new_button, 0, 1, 1, 1)

        self.main_list.itemSelectionChanged.connect(self.on_item_selection_change)
        self.main_list.itemPressed.connect(self.on_selection_change)

    def on_item_selection_change(self, *args, **kwargs):
        '''

        '''
        selection = self.main_list.selectedItems()
        if selection:
            valid_selection = True
            '''
            selected item
            '''
            item_data = selection[0].data(Qt.QtCore.Qt.UserRole)
            if not item_data:
                valid_selection = False
        else:
            valid_selection = False

        '''
        emit
        '''
        self.valid_selection_change.emit(valid_selection)

    def clear_items(self):
        '''
        clear
        '''
        self.main_list.clear()

        '''
        indicate change
        '''
        self.on_item_selection_change('on_clear')

    def update(self):
        '''
        clear
        '''
        self.clear_items()

        '''
        get list of retime curves
        '''
        retime_curves = CoreFunctions.get_retime_curves_in_scene()
        if not retime_curves:
            return False

        '''
        todo, also get state
        '''

        '''
        add retime curves to list
        '''
        for s in retime_curves:
            '''
            data
            '''
            data = {}
            data['name'] = s
            data['state'] = u'启用'  # todo, set actual state

            '''
            widget
            '''
            widget = ControllersWidgetItem()
            widget.set_data(data)
            widget.select_clicked.connect(partial(self.on_clicked_select, s))
            widget.selection_change.connect(self.on_selection_change)


            '''
            item
            '''
            item = Qt.QtWidgets.QListWidgetItem(self.main_list)
            # item.setText('{0} [{1}]'.format(data['name'], data['state']))
            item.setData(Qt.QtCore.Qt.UserRole, data)
            item.setSizeHint(Qt.QtCore.QSize(0, 40))

            self.main_list.addItem(item)
            self.main_list.setItemWidget(item, widget)

    def on_clicked_select(self, *args, **kwargs):
        if not args:
            return False
        retime_controller = args[0]
        success = CoreFunctions.select_maya_nodes(retime_controller)
        if not success:
            self.update()

    def on_selection_change(self, *args, **kwargs):
        '''

        '''
        selection = self.main_list.selectedItems()
        if not selection:
            return False
        '''
        selected item
        '''
        item_data = selection[0].data(Qt.QtCore.Qt.UserRole)
        if not item_data:
            return False

        '''
        check that it exists
        '''
        node_name = item_data['name']
        if not CoreFunctions.object_exists(node_name):
            self.update()

        '''
        emit signal
        '''
        self.selection_change.emit(node_name)


class ControllersWidgetItem(LayoutWidget, Qt.QtWidgets.QWidget):
    select_clicked = Qt.QtCore.Signal(str)
    selection_change = Qt.QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(ControllersWidgetItem, self).__init__(*args, **kwargs)

        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignVCenter | Qt.QtCore.Qt.AlignLeft)

    def do_layout(self):
        self.main_layout.setSpacing(2)
        self.main_layout.setContentsMargins(3, 0, 3, 0)

        # retime curve name
        self.main_label = EditableLabelWidget(self) #Qt.QtWidgets.QLabel(self)
        self.main_label.setFixedHeight(30)
        self.main_label.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addWidget(self.main_label, 0, 0, 1, 1)
        self.main_label.on_text_edit.connect(self.on_rename_curve)

        # state box
        self.state_combobox = ColoredComboBox(self)
        self.state_combobox.setFixedHeight(30)
        self.state_combobox.setSizePolicy(Qt.QtWidgets.QSizePolicy.Minimum, Qt.QtWidgets.QSizePolicy.Expanding)
        self.main_layout.addWidget(self.state_combobox, 0, 1, 1, 1)
        try:
            self.state_combobox.textActivated['QString'].connect(self.on_state_change)
        except:
            self.state_combobox.activated['QString'].connect(self.on_state_change)
        #https://doc.qt.io/qt-5/qcombobox-obsolete.html
        # todo

        #Select button
        #color = [0.847, .263, .145] # red
        color = [.8, .8, .8] # whitey grey
        self.select_button = ColoredButton(u'选择', parent=self, color=color, borderRadius=0)
        self.select_button.setFixedHeight(30)
        #self.delete_button.setFixedSize(Qt.QtCore.QSize(30,30))
        self.select_button.setSizePolicy(Qt.QtWidgets.QSizePolicy.Minimum, Qt.QtWidgets.QSizePolicy.Expanding)
        self.select_button.clicked.connect(self.on_select_clicked)
        self.main_layout.addWidget(self.select_button, 0, 2, 1, 1)

        #sizing
        self.main_layout.setColumnStretch(0, 1)
        #self.main_layout.setColumnStretch(1, 30)
        #self.main_layout.setColumnStretch(2, 20)

    @classmethod
    def split_namespace(cls, object_name):
        '''
        namespace
        getting rid of path separaters |
        splitting by namespace separators, removing the object name, then rejoining
        '''
        namespace = ':'.join(object_name.split('|')[-1].split(':')[:-1])

        '''
        object name
        '''
        object_name = object_name.split(':')[-1]

        return [namespace, object_name]

    def on_rename_curve(self, new_name, *args, **kwargs):


        # get current curve name
        data = self.get_data()
        controller_name = data.get('name', False)
        if not controller_name:
            #print(892, 'if not controller_name:')
            return

        #
        root_name = controller_name.split('|')[-1] # remove from any heirarchy
        namespace, object_name = self.split_namespace(root_name)

        # strip junk from new name
        new_name = new_name.split('|')[-1].split(':')[-1]

        # change if different
        if new_name == object_name:
            #print(892, 'new_name == object_name')
            self.on_set_data()
            return

        # rename
        separator= ''
        if namespace:
            separator = ':'
        new_object_name = '{0}{1}{2}'.format(namespace, separator, new_name)

        # do the rename
        result_name = controller_name
        try:
            result_name = cmds.rename(controller_name, new_object_name)
            result_name = cmds.ls(result_name, long=True) [0]
        except Exception as e:
            print('Rename Unsuccessful: ', Exception, e)
            pass

        #update display
        self.internal_data['name'] = result_name
        self.on_set_data()
        #print(879, 'on_rename_curve', result_name)

        # trigger a refresh
        self.select_clicked.emit(result_name)

    def on_select_clicked(self):
        value = self.get_data().get('name', 'NOT SET')
        self.select_clicked.emit(value)

    def on_state_change(self, state_string):
        '''
        data
        '''
        data = self.get_data()
        retime_controller = data.get('name', False)
        previous_state = CoreFunctions.get_retime_controller_status(retime_controller)
        new_state = RetimeStates.get_state_for_string(state_string)

        '''
        set
        '''
        return_state = CoreFunctions.set_retime_controller_state(retime_controller, new_state)

        '''
        deletion event
        '''
        if new_state in [RetimeStates.Delete, RetimeStates.Disconnect]:
            self.selection_change.emit()

        '''
        internal combo
        '''
        self.update_comboBox()
        #print(276, 'on_modify_state', state_string)

    def on_set_data(self):
        '''
        update widget with new data
        '''
        data = self.get_data()

        '''
        retime curve name
        '''
        retime_controller = data.get('name', 'NOT SET')
        data['text'] = retime_controller
        #print(913, 'setting data',retime_controller )
        self.main_label.update_data(data)

        '''
        update combobox
        '''
        self.update_comboBox()

    def update_comboBox(self, current_state_override = False):
        '''
        get data
        '''
        data = self.get_data()
        retime_controller = data.get('name', 'NOT SET')

        '''
        combo box
        '''
        optional_values = [u'重置', u'启用', u'禁用', u'反向', u'断开连接', u'删除']
        kwargs = {}
        current_state = False
        if current_state_override:
            current_state = current_state_override
        else:
            current_state = CoreFunctions.get_retime_controller_status(retime_controller)
        current_state_str = RetimeStates.get_string_for_int(current_state)
        kwargs['setCurrentItem'] = current_state_str
        kwargs['sortItems'] = False
        kwargs['reverseSortOrder'] = False
        QTHelpers.populateComboBox(self.state_combobox, optional_values, **kwargs)


class CoreFunctions():

    @classmethod
    def get_retime_curves_in_scene(cls):
        nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
        if not nurbs_curves:
            return False
        transforms = cmds.listRelatives(nurbs_curves, allParents=True, type='transform', fullPath=True)
        transforms = list(set(transforms))
        retime_curves = []
        for t in transforms:
            if cmds.attributeQuery('retimeState', node=t, exists=True):
                retime_curves.append(t)
        retime_curves = sorted(retime_curves)
        return retime_curves

    @classmethod
    def object_exists(cls, maya_node):
        return cmds.objExists(maya_node)

    @classmethod
    def getAttrFromObject(cls, objectVar):
        attrs = cmds.listAttr(objectVar, scalar=True, keyable=True, scalarAndArray=False)
        returnAttrs = []
        if attrs:
            for a in attrs:
                if '.' not in a:
                    returnAttrs.append(a)
        return returnAttrs

    @classmethod
    def isStringListInString(cls, stringListVar, stringVar):
        for s in stringListVar:
            if s.lower() in stringVar.lower():
                return True
        return False

    @classmethod
    def getConnectedNodes(cls, nodesVar):

        # whitelist
        stringList = ['animcurveT', 'character', 'blend', 'onstrain']
        newNodes = []
        connectionQuery = cmds.listConnections(nodesVar, destination=False, source=True)

        if connectionQuery:
            for c in connectionQuery:
                nodeType = cmds.objectType(c)
                if cls.isStringListInString(stringList, nodeType):
                    # print '>>', nodeType, c
                    if c not in newNodes:
                        newNodes.append(c)

        newNodes = list(set(newNodes) - set(nodesVar))

        # also query new results
        if newNodes:
            newNodes = cls.getConnectedNodes(newNodes)

        # combine
        nodesVar = list(set(nodesVar) | set(newNodes))

        #
        return nodesVar

    @classmethod
    def getCurvesFromNodes(cls, nodes):
        curves = []
        for n in nodes:
            curves_query = cls.get_all_related_curves_for_object(n)
            if curves_query:
                curves += curves_query
        return list(set(curves))

    @classmethod
    def get_all_related_curves_for_object(cls, node, depth = 2):
        anim_curves = [curve for curve in cmds.listHistory(node, pruneDagObjects=False, leaf=False, levels=depth) if cmds.nodeType(curve, inherited=True)[0] == 'animCurve']
        if not anim_curves:
            anim_curves = []
        return anim_curves

    @classmethod
    def getActiveTimewarp(cls):
        try:
            timewarpNode = cmds.textScrollList("eb_labs_tw_controlList", q=True, si=True)
            timewarpNode = timewarpNode[0].split(' ')[0]
            if cmds.objExists(timewarpNode):
                return timewarpNode
        except Exception as e:
            # print  Exception, e
            pass
        return False

    @classmethod
    def getSelected(cls):
        '''
        get current selection
        '''
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            return []
        '''
        find connected shapes
        '''
        shapes = cmds.listRelatives(selection, fullPath=True, shapes=True)

        '''
        fallback if no shapes
        '''
        if not shapes:
            return selection

        '''
        return combined shapes + selection
        '''
        return selection + shapes

    @classmethod
    def addCurvesToTimewarp(cls, retime_curve):
        #
        selection = cls.getSelected()
        #imewarp = cls.getActiveTimewarp()
        timewarpAnimCurves = cls.getCurvesFromNodes([retime_curve])
        if not retime_curve or not selection:
            return False

        # get anim curves
        animCurves = cls.getCurvesFromNodes(selection)
        animCurves = list(set(animCurves) - set(timewarpAnimCurves))

        # connect
        for a in animCurves:
            outPlug = '{0}.{1}'.format(retime_curve, 'timeWarp')
            inPlug = '{0}.{1}'.format(a, 'input')

            # connect if not already connected
            if not cmds.isConnected(outPlug, inPlug):
                cmds.connectAttr(outPlug, inPlug, force=True)

    @classmethod
    def getCurvesAttachedToRetime(cls, retimeObject):
        if not cmds.objExists(retimeObject):
            return False
        '''
        get connections to retime attribute
        '''
        connections = cmds.listConnections('{0}.{1}'.format(retimeObject, 'timeWarp'), source=False, type='animCurve')
        return connections

    @classmethod
    def getAllConnectionsToRetime(cls, retimeObject):
        if not cmds.objExists(retimeObject):
            return False
        '''
        get connections to retime attribute
        '''
        connections = cmds.listConnections('{0}.{1}'.format(retimeObject, 'timeWarp'), source=False)
        return connections

    @classmethod
    def getAttributeFromCurve(cls, curve_node):
        if not cmds.objExists(curve_node):
            return False

        '''
        handle character sets
        '''
        connections = cmds.listConnections(curve_node)
        curve_type = cmds.objectType(connections[0])

        if curve_type == 'character':
            '''
            get character set attribute
            '''
            characterSetPlug = cmds.listConnections(curve_node, plugs=True )
            objectAttribute = cmds.listConnections(characterSetPlug[0], plugs=True, source=False)
            return objectAttribute[0]
        else:
            objectAttribute = cmds.listConnections(curve_node, source=False, destination=True, plugs=True)
            return objectAttribute[0]

    @classmethod
    def get_hierarchical_connection_info_from_retime(cls, retimeObject):
        '''
        data
        '''
        data = {}

        '''
        start getting info
        '''
        connections = cls.getCurvesAttachedToRetime(retimeObject)
        if not connections:
            return data

        '''
        '''
        for c in connections:
            '''
            get attr object.attribute
            '''
            attr = cls.getAttributeFromCurve(c)
            if not attr:
                continue

            buffer = attr.split('.')
            if buffer[0] not in data.keys():
                data[buffer[0]] = {}
            data[buffer[0]][buffer[1]] = c

        '''
        '''
        return data

    @classmethod
    def print_curve_points(cls, close_shape = True):
        '''
        points = []
        points.append([0.194834031727,0.580902610367])
        points.append([0.194834031727,0.648078016865])
        points.append([0.805165968273,0.648078016865])
        points.append([0.805165968273,0.580902610367])
        points.append([0.194834031727,0.580902610367])
        '''

        selection = cmds.ls(sl=True)

        '''
        grouping header
        '''
        print('\n\n## Points Group Header:')
        print('points_group = []')

        '''
        itterate shapes
        '''
        for nurbs_curve in selection:
            '''
            print header
            '''
            print('## Shape: {0}'.format(nurbs_curve))
            print( 'points = []')

            '''
            print points
            '''

            cv_count = cmds.getAttr('{0}.spans'.format(nurbs_curve))
            for n in range(cv_count):
                cv = '{0}.cv[{1}]'.format(nurbs_curve, n)
                pos = cmds.xform(cv, query=True, t=True, worldSpace=True)
                print( 'points.append([{0},{1},{2}])'.format(pos[0], pos[1], pos[2]))

            '''
            close shape
            '''
            #if close_shape:
            cv = '{0}.cv[{1}]'.format(nurbs_curve, 0)
            pos = cmds.xform(cv,  query=True, t=True, worldSpace=True)
            print('points.append([{0},{1},{2}])'.format(pos[0], pos[1], pos[2]))
            print('points_group.append(points)\n\n')

    @classmethod
    def get_controller_shape_node(cls):
        points_group = []
        ## Shape: small_circle_top_left
        points = []
        points.append([-0.208226537704, 0.719860601425, 0.0536088585854])
        points.append([-0.191773462296, 0.719860601425, 0.0536088585854])
        points.append([-0.180139374733, 0.708226537704, 0.0536088585854])
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([-0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([-0.208226537704, 0.680139398575, 0.0536088585854])
        points.append([-0.219860625267, 0.691773462296, 0.0536088585854])
        points.append([-0.219860625267, 0.708226537704, 0.0536088585854])
        points.append([-0.208226537704, 0.719860601425, 0.0536088585854])
        points_group.append(points)

        ## Shape: small_circle_top_right
        points = []
        points.append([0.180139374733, 0.708226537704, 0.0536088585854])
        points.append([0.191773462296, 0.719860601425, 0.0536088585854])
        points.append([0.208226537704, 0.719860601425, 0.0536088585854])
        points.append([0.219860625267, 0.708226537704, 0.0536088585854])
        points.append([0.219860625267, 0.691773462296, 0.0536088585854])
        points.append([0.208226537704, 0.680139398575, 0.0536088585854])
        points.append([0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([0.180139374733, 0.708226537704, 0.0536088585854])
        points_group.append(points)

        ## Shape: small_circle_bot_center
        points = []
        points.append([0.0198606207967, 0.191773462296, 0.0536088585854])
        points.append([0.00822653770447, 0.180139374733, 0.0536088585854])
        points.append([-0.00822653919458, 0.180139374733, 0.0536088585854])
        points.append([-0.0198606193066, 0.191773462296, 0.0536088585854])
        points.append([-0.0198606207967, 0.208226537704, 0.0536088585854])
        points.append([-0.00822653770447, 0.219860601425, 0.0536088585854])
        points.append([0.00822653919458, 0.219860601425, 0.0536088585854])
        points.append([0.0198606222868, 0.208226537704, 0.0536088585854])
        points.append([0.0198606207967, 0.191773462296, 0.0536088585854])
        points_group.append(points)

        ## Shape: small_circle_center_center
        points = []
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.019860625267, 0.508226537704, 0.0536088585854])
        points.append([0.0198606207967, 0.491773462296, 0.0536088585854])
        points.append([0.00822653770447, 0.480139398575, 0.0536088585854])
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points.append([-0.0198606193066, 0.491773462296, 0.0536088585854])
        points.append([-0.0198606193066, 0.508226537704, 0.0536088585854])
        points.append([-0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points_group.append(points)

        ## Shape: wire_top_left
        points = []
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([-0.156861448288, 0.6684237957, 0.0639001250267])
        points.append([-0.116200792789, 0.627763128281, 0.0704486727715])
        points.append([-0.075540137291, 0.587102460861, 0.0704486727715])
        points.append([-0.034879475832, 0.546441793442, 0.0639001250267])
        points.append([-0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([-0.0198606207967, 0.508226537704, 0.0536088585854])
        points.append([-0.0464418232441, 0.53487944603, 0.0639001250267])
        points.append([-0.0871024847031, 0.575540113449, 0.0704486727715])
        points.append([-0.127763140202, 0.616200780869, 0.0704486727715])
        points.append([-0.1684237957, 0.656861448288, 0.0639001250267])
        points.append([-0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points_group.append(points)

        ## Shape: wire_top_right
        points = []
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.034879475832, 0.546441793442, 0.0639001250267])
        points.append([0.075540137291, 0.587102460861, 0.0704486727715])
        points.append([0.116200792789, 0.627763128281, 0.0704486727715])
        points.append([0.156861448288, 0.6684237957, 0.0639001250267])
        points.append([0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([0.1684237957, 0.656861448288, 0.0639001250267])
        points.append([0.127763152122, 0.616200780869, 0.0704486727715])
        points.append([0.0871024847031, 0.575540113449, 0.0704486727715])
        points.append([0.0464418232441, 0.53487944603, 0.0639001250267])
        points.append([0.019860625267, 0.508226537704, 0.0536088585854])
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points_group.append(points)

        ## Shape: wire_bot_center
        points = []
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points.append([-0.00817581340671, 0.442497158051, 0.0639001250267])
        points.append([-0.00817581638694, 0.384994292259, 0.0704486727715])
        points.append([-0.00817581638694, 0.327491426468, 0.0704486727715])
        points.append([-0.00817581340671, 0.269988584518, 0.0639001250267])
        points.append([-0.00822653770447, 0.219860601425, 0.0536088585854])
        points.append([0.00822653919458, 0.219860601425, 0.0536088585854])
        points.append([0.00817581415176, 0.269988584518, 0.0639001250267])
        points.append([0.00817581191659, 0.327491426468, 0.0704486727715])
        points.append([0.00817581191659, 0.384994292259, 0.0704486727715])
        points.append([0.00817581415176, 0.442497158051, 0.0639001250267])
        points.append([0.00822653770447, 0.480139398575, 0.0536088585854])
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points_group.append(points)

        ## Shape: large_circle_top_left
        points = []
        points.append([-0.230901694298, 0.795105648041, 0.05])
        points.append([-0.169098293781, 0.795105648041, 0.05])
        points.append([-0.119098305702, 0.758778524399, 0.05])
        points.append([-0.0999999880791, 0.7, 0.05])
        points.append([-0.119098293781, 0.641221475601, 0.05])
        points.append([-0.169098305702, 0.604894351959, 0.05])
        points.append([-0.23090171814, 0.604894351959, 0.05])
        points.append([-0.28090171814, 0.641221475601, 0.05])
        points.append([-0.3, 0.7, 0.05])
        points.append([-0.28090171814, 0.758778524399, 0.05])
        points.append([-0.230901694298, 0.795105648041, 0.05])
        points_group.append(points)

        ## Shape: large_circle_top_right
        points = []
        points.append([0.119098293781, 0.758778524399, 0.05])
        points.append([0.169098305702, 0.795105648041, 0.05])
        points.append([0.230901694298, 0.795105648041, 0.05])
        points.append([0.280901694298, 0.758778524399, 0.05])
        points.append([0.3, 0.7, 0.05])
        points.append([0.28090171814, 0.641221475601, 0.05])
        points.append([0.230901694298, 0.604894351959, 0.05])
        points.append([0.16909828186, 0.604894351959, 0.05])
        points.append([0.11909828186, 0.641221475601, 0.05])
        points.append([0.0999999880791, 0.7, 0.05])
        points.append([0.119098293781, 0.758778524399, 0.05])
        points_group.append(points)

        ## Shape: large_circle_bot_center
        points = []
        points.append([0.0309017032385, 0.295105648041, 0.05])
        points.append([-0.030901697278, 0.295105648041, 0.05])
        points.append([-0.0809017062187, 0.258778524399, 0.05])
        points.append([-0.100000011921, 0.2, 0.05])
        points.append([-0.0809017181396, 0.141221475601, 0.05])
        points.append([-0.0309017151594, 0.104894340038, 0.05])
        points.append([0.0309016942978, 0.104894328117, 0.05])
        points.append([0.0809017062187, 0.141221451759, 0.05])
        points.append([0.100000011921, 0.199999988079, 0.05])
        points.append([0.0809017002583, 0.258778524399, 0.05])
        points.append([0.0309017032385, 0.295105648041, 0.05])
        points_group.append(points)

        ## Shape: frame
        points = []
        points.append([-0.32800719738, 1.0, 0.05])
        points.append([-0.364003610611, 0.990354824066, 0.05])
        points.append([-0.390354800224, 0.964003562927, 0.05])
        points.append([-0.4, 0.928007221222, 0.05])
        points.append([-0.4, 0.0719928264618, 0.05])
        points.append([-0.390354800224, 0.035996389389, 0.05])
        points.append([-0.364003610611, 0.00964517593384, 0.05])
        points.append([-0.32800719738, 0.0, 0.05])
        points.append([0.32800719738, 0.0, 0.05])
        points.append([0.364003610611, 0.00964517593384, 0.05])
        points.append([0.390354800224, 0.035996389389, 0.05])
        points.append([0.4, 0.0719928264618, 0.05])
        points.append([0.4, 0.928007221222, 0.05])
        points.append([0.390354800224, 0.964003562927, 0.05])
        points.append([0.364003610611, 0.990354824066, 0.05])
        points.append([0.32800719738, 1.0, 0.05])
        points.append([-0.32800719738, 1.0, 0.05])
        points.append([-0.32800719142, 1.0, -0.0500000007451])
        points.append([-0.364003610611, 0.990354824066, -0.05])
        points.append([-0.364003610611, 0.990354824066, 0.05])
        points.append([-0.364003610611, 0.990354824066, -0.05])
        points.append([-0.390354800224, 0.964003562927, -0.05])
        points.append([-0.390354800224, 0.964003562927, 0.05])
        points.append([-0.390354800224, 0.964003562927, -0.05])
        points.append([-0.4, 0.928007221222, -0.05])
        points.append([-0.4, 0.928007221222, 0.05])
        points.append([-0.4, 0.928007221222, -0.05])
        points.append([-0.4, 0.0719928264618, -0.05])
        points.append([-0.4, 0.0719928264618, 0.05])
        points.append([-0.4, 0.0719928264618, -0.05])
        points.append([-0.390354800224, 0.035996389389, -0.05])
        points.append([-0.390354800224, 0.035996389389, 0.05])
        points.append([-0.390354800224, 0.035996389389, -0.05])
        points.append([-0.364003610611, 0.00964517593384, -0.05])
        points.append([-0.364003610611, 0.00964517593384, 0.05])
        points.append([-0.364003610611, 0.00964517593384, -0.05])
        points.append([-0.32800719738, 0.0, -0.05])
        points.append([-0.32800719738, 0.0, 0.05])
        points.append([-0.32800719738, 0.0, -0.05])
        points.append([0.32800719738, 0.0, -0.05])
        points.append([0.32800719738, 0.0, 0.05])
        points.append([0.32800719738, 0.0, -0.05])
        points.append([0.364003610611, 0.00964517593384, -0.05])
        points.append([0.364003610611, 0.00964517593384, 0.05])
        points.append([0.364003610611, 0.00964517593384, -0.05])
        points.append([0.390354800224, 0.035996389389, -0.05])
        points.append([0.390354800224, 0.035996389389, 0.05])
        points.append([0.390354800224, 0.035996389389, -0.05])
        points.append([0.4, 0.0719928264618, -0.05])
        points.append([0.4, 0.0719928264618, 0.05])
        points.append([0.4, 0.0719928264618, -0.05])
        points.append([0.4, 0.928007221222, -0.05])
        points.append([0.4, 0.928007221222, 0.05])
        points.append([0.4, 0.928007221222, -0.05])
        points.append([0.390354800224, 0.964003562927, -0.05])
        points.append([0.390354800224, 0.964003562927, 0.05])
        points.append([0.390354800224, 0.964003562927, -0.05])
        points.append([0.364003610611, 0.990354824066, -0.05])
        points.append([0.364003610611, 0.990354824066, 0.05])
        points.append([0.364003610611, 0.990354824066, -0.05])
        points.append([0.32800719738, 1.0, -0.05])
        points.append([0.32800719738, 1.0, 0.05])
        points.append([0.32800719738, 1.0, -0.05])
        points.append([-0.32800719142, 1.0, -0.0500000007451])
        points.append([-0.32800719738, 1.0, 0.05])
        points_group.append(points)

        '''
        create curve objects
        '''
        node_list = []
        for points in points_group:
            temp_curve = cmds.curve(degree=1, p=points)
            node_list.append(temp_curve)

        '''
        combine
        '''
        main_node = node_list.pop()
        for n in node_list:
            '''
            get shape
            '''
            shape_node = cmds.listRelatives(n, shapes=True)
            if shape_node:
                shape_node = shape_node[0]

                '''
                hide shapes
                '''
                cmds.setAttr('{0}.{1}'.format(shape_node, 'isHistoricallyInteresting'), 0)
                cmds.setAttr('{0}.{1}'.format(shape_node, 'hiddenInOutliner'), True)

                '''
                reparent shape
                '''
                cmds.parent(shape_node, main_node, shape=True, addObject=True)
                cmds.delete(n)

        '''
        rename main node
        '''
        combined_node = cmds.rename(main_node, 'retime_controller')

        '''
        set color
        '''
        cmds.setAttr('{0}.{1}'.format(combined_node, 'overrideEnabled'), 1)
        cmds.setAttr('{0}.{1}'.format(combined_node, 'overrideColor'), 17)

        '''
        return
        '''
        return combined_node

    @classmethod
    def create_new_retime_controller(cls, retime_controller='retime_controller'):
        '''
        undo chunck
        '''

        cls.create_new_retime_controller_exec(retime_controller=retime_controller)

        '''
        undo chunck
        '''

    @classmethod
    def create_new_retime_controller_exec(cls, retime_controller ='retime_controller'):
        '''
        - create curve shape
        - add attributes
        - reset based on selection
        '''
        #curvePoints = cls.get_controller_shape_points()
        #retime_controller = cmds.curve(degree=1, p=curvePoints, n=retime_controller)
        retime_controller = cls.get_controller_shape_node()

        '''
        add attributes
        '''
        cmds.addAttr(retime_controller, longName='timeWarp', attributeType='time')
        #cmds.addAttr(retime_controller, longName='shuffleData', attributeType='double')
        cmds.addAttr(retime_controller, longName='store', dataType='string')
        cmds.addAttr(retime_controller, longName='timeWarp_offline', attributeType='time')
        states_enum = [ \
            'Enable=1', \
            'Disable=2', \
            'Reset=3', \
            'Invert=4', \
            'Disconnect=5',
            'Delete=6']
        cmds.addAttr(retime_controller, ln='retimeState', at='enum', enumName=(':'.join(states_enum)))

        '''
        keyable and channelbox
        '''
        for a in ['timeWarp']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, channelBox=True)
            cmds.setAttr(attribute, edit=True, keyable=True)

        '''
        non-keyable
        '''
        for a in ['timeWarp_offline', 'retimeState']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, keyable=False)

        '''
        misc attributes
        '''
        for a in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, keyable=False)
            cmds.setAttr(attribute, edit=True, channelBox=True)

        '''
        non-channelbox
        '''
        for a in ['timeWarp_offline', 'store', 'retimeState']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, channelBox=False)

        '''
        reset anim
        '''
        cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)

    @classmethod
    def set_retime_controller_state(cls, retime_controller, new_state):
        if not retime_controller or not new_state:
            return False

        '''
        do nothing
        '''
        previous_state = cls.get_retime_controller_status(retime_controller)
        if previous_state == new_state:
            return new_state

        '''
        change to a default state temporarily
        * disconnect time
        * copy offline back timeWarp
        '''

        attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        online_key_count = cmds.keyframe(attr, query=True, keyframeCount =True)
        attr = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        offline_key_count = cmds.keyframe(attr, query=True, keyframeCount =True)
        time_node = cmds.ls(type='time')[0]

        time_attr = '{0}.{1}'.format(time_node, 'outTime')
        attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        if cmds.isConnected(time_attr, attr):
            cmds.disconnectAttr (time_attr, attr)
        if offline_key_count>0:
            attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
            cmds.cutKey(attribute, option='keys')
            attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
            cmds.pasteKey(attribute, option='replace')
            '''
            update online keycount
            '''
            online_key_count = cmds.keyframe(attr, query=True, keyframeCount=True)

        '''
        fix empty
        '''
        if online_key_count == 0:
            cls.reset_retime(retime_controller)

        '''
        states
        '''
        if new_state == RetimeStates.Reset:
            '''
            reset
            '''
            cls.reset_retime(retime_controller)

            '''
            set state to enable
            '''
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
            return RetimeStates.Enable

        elif new_state == RetimeStates.Disable:
            try:
                '''
                cut/paste to offline
                '''
                attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
                cmds.cutKey(attribute, option='keys')
                attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
                cmds.pasteKey(attribute, option='replace')

                '''
                connect to time
                '''
                time_nodes = cmds.ls(type='time')
                time_attr = '{0}.{1}'.format(time_nodes[0], 'outTime')
                retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
                cmds.connectAttr(time_attr,retime_attr, force=True)

                '''
                set state to disable
                '''
                cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Disable)
                return RetimeStates.Disable

            except Exception as e:
                print(1280, 'RetimeStates.Enable', Exception, e)
                cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)

        elif new_state == RetimeStates.Enable:
            try:
                # '''
                # disconnect to time
                # '''
                # time_nodes = cmds.ls(type='time')
                # time_attr = '{0}.{1}'.format(time_nodes[0], 'outTime')
                # retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
                # if cmds.isConnected(time_attr, retime_attr):
                #     cmds.disconnectAttr(time_attr,retime_attr)
                #
                # '''
                # cut/paste to online
                # '''
                # attr = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
                # offline_key_count = cmds.keyframe(attr, query=True, keyframeCount=True)
                # print(1634, 'offline_key_count', offline_key_count, attr)
                # if offline_key_count > 0:
                #     attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
                #     cmds.cutKey(attribute, option='curve')
                #     attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
                #     cmds.pasteKey(attribute, option='replace')

                '''
                set state to Enable
                '''
                cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
                return RetimeStates.Enable
            except Exception as e:
                print(1270, 'RetimeStates.Enable', Exception, e)
                print (traceback.format_exc())
                cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)

        elif new_state == RetimeStates.Delete:
            cls.delete_retime(retime_controller)
            return RetimeStates.Delete

        elif new_state == RetimeStates.Disconnect:
            '''
            disconnect
            '''
            cls.completely_disconnect_retime(retime_controller)

            '''
            set state to enable
            '''
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
            return RetimeStates.Enable

        elif new_state == RetimeStates.Invert:
            '''
            invert
            * copy to offline
            * rekey back to online inverted
            '''
            cls.invert_retime(retime_controller)

            '''
            set state to enable
            '''
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Invert)
            return RetimeStates.Enable

    @classmethod
    def reset_retime(cls, retime_controller):
        '''
        set start and end keys
        '''
        start_time = cmds.playbackOptions(query=True, animationStartTime=True)
        end_time = cmds.playbackOptions(query=True, animationEndTime=True)
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        cmds.cutKey(attribute)
        cmds.setKeyframe(attribute, time=start_time, value=start_time, inTangentType='linear', outTangentType='linear')
        cmds.setKeyframe(attribute, time=end_time, value=end_time, inTangentType='linear', outTangentType='linear')

        '''
        clear offline
        '''
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        cmds.cutKey(attribute, option='keys')

    @classmethod
    def invert_retime(cls, retime_controller):
        '''
        * copy main curve to offline
        * invert keys back to main curve
        '''

        '''
        get info
        '''
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        start_frame = int(cmds.findKeyframe(attribute, which='first'))
        end_frame = int(cmds.findKeyframe(attribute, which='last'))
        duration = end_frame - start_frame
        if duration <= 1:
            return False

        '''
        cut/paste to offline
        '''
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        cmds.cutKey(attribute, option='keys')
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        cmds.pasteKey(attribute, option='replace')

        '''
        copy/invert
        '''
        source_attr = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        target_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for t in range(start_frame, end_frame):
            value = cmds.getAttr(source_attr, time=t)
            cmds.setKeyframe(target_attr, value=t, time=value, inTangentType='spline', outTangentType='spline')

    @classmethod
    def completely_disconnect_retime(cls, retime_controller):
        '''
        get connected curves
        '''
        connections = cls.getAllConnectionsToRetime(retime_controller)
        if not connections:
            return False

        '''
        disconnect
        '''
        retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for c in connections:
            curve_attr = '{0}.{1}'.format(c, 'input')
            if cmds.isConnected(retime_attr, curve_attr):
                cmds.disconnectAttr(retime_attr, curve_attr)

    @classmethod
    def disconnect_curve(cls, retime_controller, connections):
        if not cmds.objExists(retime_controller):
            return False
        '''
        disconnect
        '''
        retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for c in connections:
            curve_attr = '{0}.{1}'.format(c, 'input')
            if cmds.isConnected(retime_attr, curve_attr):
                cmds.disconnectAttr(retime_attr, curve_attr)

    @classmethod
    def delete_retime(cls, retime_controller):
        cmds.delete(retime_controller)

    @classmethod
    def select_maya_nodes(cls, nodes):
        if not nodes:
            return False
        if type(nodes) != type([]):
            nodes = [nodes]
        existing_nodes = []
        for n in nodes:
            if cls.object_exists(n):
                existing_nodes.append(n)
        if not existing_nodes:
            return False

        '''
        select
        '''
        cmds.select(existing_nodes, replace=True)
        return True

    @classmethod
    def get_retime_controller_status(cls, retime_controller):
        if not cmds.objExists(retime_controller):
            return RetimeStates.Delete

        '''
        check the attr
        '''
        attr = '{0}.{1}'.format(retime_controller, 'retimeState')
        state_query = cmds.getAttr(attr)

        '''
        lookup table
        '''
        state_lookup = {}
        state_lookup[1] = RetimeStates.Enable
        state_lookup[2] = RetimeStates.Disable
        state_lookup[3] = RetimeStates.Reset
        state_lookup[4] = RetimeStates.Invert
        state_lookup[5] = RetimeStates.Disconnect
        state_lookup[6] = RetimeStates.Delete

        '''
        return with fallback
        '''
        return state_lookup.get(state_query, 1)

    @classmethod
    def bake_retime_controller(cls, retime_controller):
        '''
        get all connected plugs, object.attr
        '''
        connections = cls.getCurvesAttachedToRetime( retime_controller)
        all_plugs = cls.get_plugs_for_anim_curves(connections)

        '''
        get stats
        '''
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        start_frame = int(cmds.findKeyframe(attribute, which='first'))
        end_frame = int(cmds.findKeyframe(attribute, which='last'))
        time_range = (start_frame, end_frame)

        '''
        bake
        '''
        cmds.bakeResults(all_plugs, simulation=True, time=time_range, sampleBy=1, disableImplicitControl=True, preserveOutsideKeys=False, sparseAnimCurveBake=False,  shape=True)

    @classmethod
    def get_plugs_for_anim_curves(cls, anim_curves):
        if not anim_curves:
            return []
        all_plugs = []
        for c in anim_curves:
            if cmds.objExists(c):
                plugs = cmds.listConnections(anim_curves, plugs=True, source=False, destination=True)

                all_plugs += plugs
        '''
        clean
        '''
        all_plugs = list(set(all_plugs))
        return all_plugs

    @classmethod
    def cleanSubframeKeys(cls, *args, **kwargs):
        '''
        pull args
        '''
        curve_nodes = kwargs.get('curve_nodes', False)

        '''
        get selections
        '''
        if not curve_nodes:
            selection = cmds.ls(sl=True)
            checkShapes = cmds.listRelatives(selection, shapes=True, fullPath=True)
            if checkShapes:
                selection += checkShapes
            selection = list(set(selection))

            curve_nodes = cls.getCurvesFromNodes(selection)
        #print(1642, 'curveNodes', curveNodes)
        #curveNodes = cls.getCurvesAttachedToRetime(retime_controller)
        if curve_nodes:
            for curveNode in curve_nodes:
                timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                # if there are keys:
                if timesValues:

                    # breakdown lists
                    times = []
                    values = []
                    wholeTimes = set()
                    subframeTimes = set()
                    for t, v in timesValues:
                        times.append(t)
                        wholeTimes.add(int(float(t) + 0.5))
                        values.append(v)
                        if not float(t).is_integer():
                            subframeTimes.add(t)

                    # diff a list of times that need keyframes set
                    newTimes = list(wholeTimes - set(times))
                    for t in newTimes:
                        cmds.setKeyframe(curveNode, insert=True, time=tuple([t, t]))

                    # remove subframe keys
                    for t in subframeTimes:
                        cmds.cutKey(curveNode, time=tuple([t, t]))

    @classmethod
    def find_old_retime_curves(cls, *args, **kwargs):
        #
        nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
        if not nurbs_curves:
            return False
        transforms = cmds.listRelatives(nurbs_curves, allParents=True, type='transform', fullPath=True)
        transforms = list(set(transforms))

        old_retime_curves = []
        for t in transforms:
            # old retime curve has this
            has_shuffle_data_attr = cmds.objExists('{0}.{1}'.format(t , 'shuffleData'))
            has_offline_attr = cmds.objExists('{0}.{1}'.format(t, 'timeWarp_offline'))
            if has_shuffle_data_attr and has_offline_attr:
                if t not in old_retime_curves:
                    old_retime_curves.append(t)
        return old_retime_curves

    @classmethod
    def update_old_retime_curves(cls, *args, **kwargs):
        ''''''
        # find old retime curves
        old_retime_curves = cls.find_old_retime_curves()
        if not old_retime_curves:
            return

        def update():
            for c in old_retime_curves:
                cls.update_old_retime_curve(c)

        #
        kwargs = {}
        kwargs['parentWidget'] = QTHelpers.get_main_window()
        kwargs['titleText'] = 'Update Retime Curves?'
        message = []
        message.append('It looks like there are some outdated retime curves in your scene, would you like to update?\n')
        message += old_retime_curves
        message.append('\n')
        message.append('Make sure to back up your scene before proceeding!')
        kwargs['messageText'] = '\n'.join(message)
        kwargs['successCallback'] = update
        QTHelpers.getYesNoFromUser(**kwargs)

        # if they exist, ask the user if they want to update

        # do update

    @classmethod
    def update_old_retime_curve(cls, retime_controller):
        print('Updating ', retime_controller)
        try:
            # add state enum
            states_enum = [ \
                'Enable=1', \
                'Disable=2', \
                'Reset=3', \
                'Invert=4', \
                'Disconnect=5',
                'Delete=6']
            cmds.addAttr(retime_controller, ln='retimeState', at='enum', enumName=(':'.join(states_enum)))

            # check enabled state
            state = RetimeStates.Enable
            keyframe_count = cmds.keyframe('{0}.{1}'.format(retime_controller, 'timeWarp_offline'), query=True, time=(), keyframeCount=True)
            if keyframe_count>0:
                # offline, means retime animation temporarily placed on offline slot
                state = RetimeStates.Disable
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), state)

            # remove old attribute
            cmds.deleteAttr('{0}.{1}'.format(retime_controller, 'shuffleData'))
        except Exception as e:
            print('Error', 'update_old_retime_curve', Exception, e)

class ShuffleKeys(object):


    @classmethod
    def process(cls, retimeObject):
        '''
        build retime helpers
        '''
        curveNodes = cmds.findKeyframe(retimeObject, curve=True, at='timeWarp')
        if not curveNodes:
            return False
        curve = curveNodes[0]
        retime_lookup = RetimeLookup(curve)

        '''
        find connected anim curves
        '''
        animCurves = CoreFunctions.getCurvesAttachedToRetime(retimeObject)
        if not animCurves:
            return False

        '''
        iterate curves
        '''
        for curve in animCurves:
            '''
            get key times
            '''
            timesValues = cmds.getAttr('{0}.{1}'.format(curve, 'keyTimeValue[:]'))
            if not timesValues:
                continue

            '''
            create temp curve
            '''
            nodeType = cmds.nodeType(curve)
            tmpCurve = cmds.createNode(nodeType, name='{0}_tempCurve'.format(curve))

            '''
            check infinities
            '''
            pre_infinity = cmds.setInfinity( attribute = curve, query=True, preInfinite=True)
            post_infinity = cmds.setInfinity( attribute = curve, query=True, postInfinite=True)

            '''
            copy keys into temp curve
            '''
            for t, v in timesValues:
                '''
                copy
                '''
                cmds.copyKey(curve, time=(t, t), option='keys')

                '''
                remap time
                '''
                #print(1778, t)
                lookup_info = retime_lookup.getSingleKeyTimeLookup(t)
                #print(1780, lookup_info)
                for i, data in enumerate(lookup_info):
                    rt, slope_multiplier = data

                    #remappedTime = Intersections.getSingleKeyTimeLookup(retimeObject, t)
                    if not rt:
                        continue

                    '''
                    paste key
                    '''
                    #for rt in remappedTime:
                    cmds.pasteKey(tmpCurve, time=(rt, rt), option='insert')

                    '''
                    apply slope
                    '''
                    out_tangent_type = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, outTangentType=True)[0]
                    if out_tangent_type != 'step':
                        in_tangent_angle = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, inAngle=True)[0]
                        in_tangent_weight = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, inWeight=True)[0]
                        out_tangent_angle = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, outAngle=True)[0]
                        out_tangent_weight = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True,  outWeight=True)[0]

                        in_tangent_x = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, ix=True)[0]
                        in_tangent_y = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, iy=True)[0]
                        out_tangent_x = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, ox=True)[0]
                        out_tangent_y = cmds.keyTangent( tmpCurve, time=(rt,rt), query=True, oy=True)[0]

                        in_tangent_angle *= slope_multiplier
                        out_tangent_angle *= slope_multiplier

                        #in_tangent_x *= slope_multiplier
                        in_tangent_y *= slope_multiplier

                        #cmds.keyTangent( tmpCurve, edit=True, absolute = True, time=(rt,rt), inAngle=in_tangent_angle, inWeight=in_tangent_weight)
                        #cmds.keyTangent( tmpCurve, edit=True, absolute = True, time=(rt,rt), outAngle=in_tangent_angle, outWeight=out_tangent_weight)
                        cmds.keyTangent( tmpCurve, edit=True, absolute = True, time=(rt,rt), ix=in_tangent_x)
                        cmds.keyTangent( tmpCurve, edit=True, absolute = True, time=(rt,rt), iy=in_tangent_y)

            '''
            replace curve
            '''
            try:
                cmds.cutKey(tmpCurve, option='curve')
                cmds.pasteKey(curve, option='replaceCompletely')
            except Exception as e:
                print(1969, Exception, e)
                print('Skipping:', curve)

            '''
            set infinity
            '''
            cmds.setInfinity( attribute = curve, preInfinite=pre_infinity)
            cmds.setInfinity( attribute = curve, postInfinite=post_infinity)

            '''
            remove temp curve
            '''
            cmds.delete(tmpCurve)



class RetimeLookup(object):

    def __init__(self, retime_animCurve):

        '''
        properties
        '''
        self.retime_animCurve = retime_animCurve

        '''
        sections
        '''
        self.sections = self.getSections(self.retime_animCurve)

        '''
        value time lookup
        '''
        self.value_time_lookup = self.create_value_time_lookup(self.sections)
        self.value_time_cache = {}
        #print(1823, '#self.value_time_lookup#')
        #print(json.dumps(self.value_time_lookup, indent=4))

    @classmethod
    def getDirection(cls, itemIndex, prevValue, currValue, nextValue):

        direction = 0
        if itemIndex == 0:
            '''
            first
            '''
            if nextValue > currValue:
                direction = 1
            elif nextValue < currValue:
                direction = -1
            else:
                direction = 0

        else:
            '''
            any other position
            '''
            if currValue > prevValue:
                direction = 1
            elif currValue < prevValue:
                direction = -1
            else:
                direction = 0
        '''
        '''
        return direction

    @classmethod
    def drange(cls, x, y, jump):
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    @classmethod
    def getKeyTimes(cls, curve):
        timesValues = cmds.getAttr('{0}.{1}'.format(curve, 'keyTimeValue[:]'))
        # if there are keys:
        times = []
        values = []
        if timesValues:
            # breakdown lists
            wholeTimes = set()
            subframeTimes = set()
            for t, v in timesValues:
                times.append(t)
                wholeTimes.add(int(float(t) + 0.5))
                values.append(v)
        return times



    @classmethod
    def getSections(cls, curve):
        '''
        get keytimes needed for sampling retime curve
        '''
        keyframeTimes = cls.getKeyTimes(curve)
        firstFrame = int(min(keyframeTimes))
        lastFrame = int(max(keyframeTimes))
        sampleStep = 0.1
        allKeyframeTimes = sorted(list(set(list(cls.drange(firstFrame, lastFrame+sampleStep, sampleStep)) + keyframeTimes)))

        '''
        simultaniously group by direction
        '''
        currentValue = None
        previousDirection = None
        direction = None
        newSection = True

        section = {}
        sections = []
        for i, t in enumerate(allKeyframeTimes):

            '''
            check directions
            '''
            previousValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=allKeyframeTimes[max(i - 1, 0)])
            currentValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=allKeyframeTimes[i])
            nextValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'),
                                     time=allKeyframeTimes[min(i + 1, len(allKeyframeTimes) - 1)])
            direction = cls.getDirection(i, previousValue, currentValue, nextValue)
            if newSection:
                previousDirection = direction
                newSection = False

            '''
            new direction
            '''
            if direction != previousDirection:
                '''
                indicate starting new section
                '''
                newSection = True

                '''
                create new section
                '''
                if section:
                    sections.append(section)
                section = {}

            '''
            add info to section
            '''
            section[t] = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=t)

            '''
            cache
            '''
            previousDirection = direction

        '''
        add last section
        '''
        sections.append(section)

        return sections

    @classmethod
    def create_value_time_lookup(cls, sections):
        '''
        section/value int/[value float = time]
        '''
        data = OrderedDict()

        '''
        construct lookup
        '''
        for i, section in enumerate(sections):
            '''
            section grouping
            '''
            if i not in data.keys():
                data[i] = OrderedDict()

            for k, v in iteritems(section):
                '''
                value int grouping
                adding neighbouring values in each section for overlap
                '''
                for offset in [-1, 0, 1]:
                    value_int = int(v + offset)
                    if value_int not in data[i].keys():
                        data[i][value_int] = []

                    '''
                    adding values
                    '''
                    data[i][value_int].append([v, k])

        '''
        return
        '''
        return data

    @classmethod
    def get_nearest_pair_index(cls, pairs, target_value, sort = False):
        # https://stackoverflow.com/questions/9706041/finding-index-of-an-item-closest-to-the-value-in-a-list-thats-not-entirely-sort
        if sort:
            pairs = sorted(pairs, key=itemgetter(1))
        return min(enumerate(pairs), key=lambda x: abs(x[1][0] - target_value))

    @classmethod
    def float_lerp(cls, a, b, f):
        return (a * (1.0 - f)) + (b * f)

    @classmethod
    def slope(cls, x1, y1, x2, y2):
        diff = (x2 - x1)
        if diff == 0:
            return 1
        return (y2 - y1) / diff

    @classmethod
    def clamp(cls, n, minn, maxn):
        return max(min(maxn, n), minn)

    @classmethod
    def get_slope_between_pairs(cls, pairs, index_a, index_b):
        '''
        clamp indexes
        '''
        index_a = cls.clamp(index_a, 0, len(pairs)-1)
        index_b = cls.clamp(index_b, 0, len(pairs)-1)

        '''
        if the index are the same, spread them out by a step
        end check as well
        '''
        if index_a == index_b:
            if index_a == 0:
                index_b += 1
            else:
                index_a -= 1

        '''

        '''
        try:
            slope = cls.slope(pairs[index_a][0], pairs[index_a][1], pairs[index_b][0], pairs[index_b][1])
        except Exception as e:
            slope = 1
            print(2248, 'Slope Calculate Fail', Exception, e)
            print('index_a', index_a)
            print('index_b', index_b)
            print('pairs', pairs)

        return slope

    def getSingleKeyTimeLookup(self, target_time):
        '''
        get nearest 2 t/v pairs from data
        '''

        if target_time not in self.value_time_cache.keys():
            #print(2266, 'target_time', target_time)
            '''
            if not already cached, do brute force lookup
            '''
            lookup_times = []
            for section, int_groups in iteritems(self.value_time_lookup):
                value_int = int(target_time)
                if value_int in int_groups.keys():
                    '''
                    matching pair
                    '''
                    pairs = int_groups[value_int]

                    '''
                    lerp lookup
                    '''
                    pairs = sorted(pairs, key=itemgetter(0))
                    nearest_index, nearest_pair = self.get_nearest_pair_index(pairs, target_time)
                    #print(2284, 'nearest index and pair', nearest_index, nearest_pair)
                    #print(2285, 'total number of pairs', len(pairs))
                    #print(2285, 'pairs', pairs)

                    '''
                    where? under, equal, over than matching value
                    '''
                    if target_time == nearest_pair[0]:
                        '''
                        found a match, onto next section
                        '''
                        slope = self.get_slope_between_pairs(pairs, nearest_index, nearest_index+1)
                        lookup_times.append((nearest_pair[1], 1.0/slope))
                        continue
                    elif nearest_pair[0] > target_time:
                        min_index = nearest_index
                        max_index = nearest_index + 1
                    else:
                        min_index = nearest_index
                        max_index = nearest_index - 1

                    '''
                    clamp if only one set of pairs in list
                    '''
                    max_index = min(len(pairs)-1, max_index)
                    #print(2302, 'neighboring indexes', min_index, max_index)

                    '''
                    get lerp ratio and apply to value
                    '''
                    diff = 0
                    try:
                        diff = (pairs[max_index][0] - pairs[min_index][0])
                    except Exception as e:
                        pass
                        #print(Exception, e)
                        #print(2308, 'neighboring indexes', min_index, max_index, pairs)
                    if diff == 0:
                        '''
                        both min and max are the same, just pick one
                        '''
                        ratio = False
                        lerp_value = pairs[min_index][1]
                    else:
                        ratio = (target_time - pairs[min_index][0]) / (pairs[max_index][0] - pairs[min_index][0])
                        lerp_value = self.float_lerp(pairs[min_index][1], pairs[min_index][1], ratio)
                    #print(2094,ratio, ':',  '({0} - {1}) / ({2} - {3})'.format(target_time,pairs[min_index][0],pairs[max_index][0],pairs[min_index][0]  ))
                    '''
                    slope
                    '''
                    slope = self.get_slope_between_pairs(pairs, min_index, max_index)

                    '''
                    store data
                    '''
                    lookup_times.append((lerp_value, 1.0/slope))


            '''
            store results to cache
            '''
            self.value_time_cache[target_time] = lookup_times

        '''
        final return
        '''
        return self.value_time_cache[target_time]


class Color(object):

    def __init__(self, rgba):
        self.set_rgba(rgba)

    def get_rgba(self):
        return self.rgba

    def set_rgba(self, rgba):
        '''
        validate, should include alpha
        '''
        rgba += [1.0] * (4 - len(rgba))

        '''
        set
        '''
        self.rgba = rgba

    def r(self):
        return self.rgba[0]
    def g(self):
        return self.rgba[1]
    def b(self):
        return self.rgba[2]
    def a(self):
        return self.rgba[3]

    def r_int(self):
        return self.float_to_int(self.r())
    def g_int(self):
        return self.float_to_int(self.g())
    def b_int(self):
        return self.float_to_int(self.b())
    def a_int(self):
        return self.float_to_int(self.a())

    def multiply_hsva(self, m_rgba):
        '''
        get hsva
        '''
        hsva = self.float_rgba_to_hsva(self.rgba)

        '''
        multiply by values
        '''
        m_hsva = []
        for i, v in enumerate(hsva):
            m_hsva.append(hsva[i] * m_rgba[i])

        '''
        back to rgb
        '''
        rgba = self.float_hsva_to_rgba(m_hsva)

        '''
        return copy
        '''
        return Color(rgba)

    def lighten_hsva(self, m_rgba):
        '''
        get hsva
        '''
        hsva = self.float_rgba_to_hsva(self.rgba)

        '''
        multiply by values
        '''
        m_hsva = []
        for i, v in enumerate(hsva):
            m_hsva.append(self.lerp(hsva[i], 1, m_rgba[i]))

        '''
        back to rgb
        '''
        rgba = self.float_hsva_to_rgba(m_hsva)

        '''
        return copy
        '''
        return Color(rgba)

    def get_average_intensity(self):
        #https://www.tutorialspoint.com/dip/grayscale_to_rgb_conversion.htm
        intensity = (0.3 * self.r()) + (0.59 * self.g()) + (0.11 * self.b())
        return intensity

    def get_int_rgba(self):
        return [self.r_int(), self.g_int(), self.b_int(), self.a_int()]

    def get_int_rgba_string(self):
        '''
        helper for qt stylesheets
        '''
        return 'rgb({0},{1},{2},{3})'.format(*self.get_int_rgba())

    @classmethod
    def lerp(cls, a, b, f):
        #https://stackoverflow.com/questions/4353525/floating-point-linear-interpolation
        return (a * (1.0 - f)) + (b * f)

    @classmethod
    def float_to_int(cls, f):
        return int(f * 255)

    @classmethod
    def float_rgba_to_hsva(cls, rgba):
        h, s, v = colorsys.rgb_to_hsv(*rgba[:3])
        a = rgba[3]
        return [h, s, v, a]

    @classmethod
    def float_hsva_to_rgba(cls, hsva):
        r, g, b = colorsys.hsv_to_rgb(*hsva[:3])
        a = hsva[3]
        return [r, g, b, a]


class Utilities():

    @classmethod
    def ebLabs_retimeTools_createRetimefromAscii(cls, **kwargs):
        #
        curveNode = ''
        if 'curveNode' in kwargs:
            # confirm node actually exists
            if cmds.objExists(curveNode):
                curveNode = kwargs.pop('curveNode')
        #
        curveName = ''
        if 'curveName' in kwargs:
            # confirm node actually exists
            if cmds.objExists(curveName):
                curveName = kwargs.pop('curveName')

        # load file and set basic data
        filters = 'All Files (*)'
        fileName = cmds.fileDialog2(fileFilter=filters, fileMode=1, dialogStyle=2)
        if fileName and type(fileName) == list:
            fileName = fileName[0]
        # fileName = cmds.fileDialog().encode('ascii')
        if not len(fileName):
            return ''
        #
        shortName = os.path.splitext(os.path.basename(fileName))[0]

        #
        f = open(fileName, 'r')
        if not f:
            cmds.warning('importASCIICurve', 'Unable to open "%s".' % fileName)
            return
        else:
            # create timewarp node
            timeWarpNode = mel.eval('ebLabs_createTimeWarpController($name=\"' + shortName + '_' + '\");')

            # clear off any previous animation
            attribute = (timeWarpNode + '.timeWarp')
            cmds.cutKey(attribute)

            # apply anim to node
            frameVals = []
            counter = 1
            for line in f:
                # set variables
                value = False
                frame = False

                # for two column data
                if ' ' in line:
                    line = line.strip()
                    buffer = line.split(' ')
                    buffer = list(filter(None, buffer))
                    print(59, 'buffer', type(buffer), buffer)
                    frame = float(buffer[0])
                    value = float(buffer[1])

                # for single column data
                else:
                    value = float(line)
                    frame = counter

                # counter
                counter += 1

                # set keys
                cmds.setKeyframe(attribute, t=frame, value=value)

            # save meta data
            attr = 'pathToAscii'
            value = fileName
            cmds.addAttr(timeWarpNode, ln=attr, dt='string')
            cmds.setAttr((timeWarpNode + '.' + attr), value, e=True, type='string')

            # save short name
            attr = 'shortName'
            value = shortName
            cmds.addAttr(timeWarpNode, ln=attr, dt='string')
            cmds.setAttr((timeWarpNode + '.' + attr), value, e=True, type='string')

    @classmethod
    def ebLabs_retimeTools_createRetimefromJson(cls, **kwargs):
        #
        curveNode = ''
        if 'curveNode' in kwargs:
            # confirm node actually exists
            if cmds.objExists(curveNode):
                curveNode = kwargs.pop('curveNode')
        #
        curveName = ''
        if 'curveName' in kwargs:
            # confirm node actually exists
            if cmds.objExists(curveName):
                curveName = kwargs.pop('curveName')

        # load file and set basic data
        filters = 'All Files (*)'
        fileName = cmds.fileDialog2(fileFilter=filters, fileMode=1, dialogStyle=2)
        if fileName and type(fileName) == list:
            fileName = fileName[0]
        # fileName = cmds.fileDialog().encode('ascii')
        if not fileName or not len(fileName):
            return ''
        #
        shortName = os.path.splitext(os.path.basename(fileName))[0]

        #
        data = cls.loadDataFromFile(fileName)

        if data:
            # create timewarp node
            timeWarpNode = mel.eval('ebLabs_createTimeWarpController($name=\"' + shortName + '_' + '\");')

            # clear off any previous animation
            attribute = (timeWarpNode + '.timeWarp')
            cmds.cutKey(attribute)

            # apply anim to node
            for frame, value in iteritems(data):
                # set keys
                cmds.setKeyframe(attribute, t=frame, value=value)

            # save meta data
            attr = 'pathToAscii'
            value = fileName
            cmds.addAttr(timeWarpNode, ln=attr, dt='string')
            cmds.setAttr((timeWarpNode + '.' + attr), value, e=True, type='string')

            # save short name
            attr = 'shortName'
            value = shortName
            cmds.addAttr(timeWarpNode, ln=attr, dt='string')
            cmds.setAttr((timeWarpNode + '.' + attr), value, e=True, type='string')

    @classmethod
    def loadDataFromFile(cls, filename, *args, **kwargs):
        data = None
        try:
            filePath = open(filename, 'r')
            data = json.loads(filePath.read())
            filePath.close()
        except:
            pass
        return data


class QTHelpers():

    @classmethod
    def populateComboBox(cls, combo_box, combo_items, **kwargs):
        reverseSortOrder = kwargs.get('reverseSortOrder', False)
        showBlank = kwargs.get('showBlank', False)
        setCurrentItem = kwargs.get('setCurrentItem', False)
        sortItems = kwargs.get('sortItems', False)

        '''
        signal blcokign
        '''
        combo_box.blockSignals(True)

        '''
        clear
        '''
        combo_box.clear()

        '''
        iterate items
        '''
        if combo_items:

            '''
            sorting
            '''
            if sortItems:
                combo_items = sorted(list(set(combo_items)), reverse=reverseSortOrder)

            '''
            first blank
            '''
            if showBlank:
                items = [''] + combo_items
            '''
            add items
            '''
            reference_index = 0
            for i, combo_item in enumerate(combo_items):
                item = Qt.QtGui.QStandardItem(str(combo_item))
                '''
                color
                '''
                if setCurrentItem:
                    if combo_item == setCurrentItem:
                        set_color = Color([0.208, 0.480, 0.751, 1])
                        item.setForeground(Qt.QtGui.QColor(*set_color.get_int_rgba()))
                        reference_index = i
                combo_box.model().appendRow(item)

            '''
            set current item
            '''
            combo_box.setCurrentIndex(reference_index)
        '''
        signal blcokign
        '''
        combo_box.blockSignals(False)

    @classmethod
    def get_key_modifiers(cls):
        QModifiers = Qt.QtWidgets.QApplication.keyboardModifiers()
        modifiers = []
        if (QModifiers & Qt.QtCore.Qt.ShiftModifier) == Qt.QtCore.Qt.ShiftModifier:
            modifiers.append('shift')
        if (QModifiers & Qt.QtCore.Qt.ControlModifier) == Qt.QtCore.Qt.ControlModifier:
            modifiers.append('control')
        if (QModifiers & Qt.QtCore.Qt.AltModifier) == Qt.QtCore.Qt.AltModifier:
            modifiers.append('alt')
        return modifiers

    @classmethod
    def getStringFromUser(cls, parentWidget=False, titleText='Input Dialog', labelText='Input Below',
                          successCallback=False):
        '''
        ask the user to provide a string
        '''
        # get input from user
        returnText, okState = Qt.QtWidgets.QInputDialog.getText(parentWidget, titleText, labelText)
        if okState and returnText:
            '''
            run callback
            '''
            try:
                if successCallback:
                    successCallback(returnText)
            except:
                pass

    @classmethod
    def getYesNoFromUser(cls, parentWidget=False, titleText='Title Text', messageText='Message Text',
                         successCallback=False):
        '''
        ask the user to click yes or no
        '''
        reply = Qt.QtWidgets.QMessageBox.question(parentWidget, titleText, messageText,
                                                  Qt.QtWidgets.QMessageBox.No | Qt.QtWidgets.QMessageBox.Yes,
                                                  Qt.QtWidgets.QMessageBox.No)
        if reply == Qt.QtWidgets.QMessageBox.Yes:
            '''
            run callback
            '''
            try:
                if successCallback:
                    successCallback()
            except:
                pass

    @classmethod
    def get_files_from_user(cls, parent_widget=False, file_types='Archive (*.zip)', title='window title',
                            target_folder=False, allow_multiples=True):
        '''
        setup parent
        '''
        if not parent_widget:
            parent_widget = cls.get_main_window()
        '''
        target folder
        '''
        if not target_folder:
            target_folder = Qt.QtCore.QDir.currentPath()

        '''
        get filepath from user
        '''
        filepaths = []
        if allow_multiples:
            filepaths = Qt.QtWidgets.QFileDialog.getOpenFileNames(parent_widget, title, target_folder, file_types)
        else:
            filepaths = Qt.QtWidgets.QFileDialog.getOpenFileName(parent_widget, title, target_folder, file_types)
            if filepaths:
                filepaths = [filepaths]

        '''
        remove filepath list from tupple
        (['filepathA.txt', 'filepathB.txt'], u'Text Files (*.txt)'))
        '''
        if filepaths:
            filepaths = filepaths[0]
        '''
        return
        '''
        return filepaths

    @classmethod
    def get_folder_from_user(cls, parent_widget=False, title='window title', target_folder=False):
        '''
        setup parent
        '''
        if not parent_widget:
            parent_widget = cls.get_main_window()
        '''
        target folder
        '''
        if not target_folder:
            target_folder = Qt.QtCore.QDir.currentPath()

        '''
        get filepath from user
        '''
        filepath = Qt.QtWidgets.QFileDialog.getExistingDirectory(None, title, target_folder,
                                                                 Qt.QtWidgets.QFileDialog.ShowDirsOnly)
        '''
        return
        '''
        return filepath

    @classmethod
    def get_main_window(cls):
        main_window = None
        try:
            '''
            debugging, attempting to use Open Maya, rather than QT
            '''
            import maya.OpenMayaUI as omui
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            # mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), Qt.QtWidgets.QWidget)
            mayaMainWindow = Qt._wrapinstance(int(mayaMainWindowPtr), base=Qt.QtWidgets.QWidget)
            main_window = mayaMainWindow
        except:
            try:
                """Return Maya's main window"""
                for obj in Qt.QtWidgets.QApplication.topLevelWidgets():
                    if obj.objectName() == 'MayaWindow':
                        main_window = obj
                        break
            except:
                pass

        #
        return main_window


class MessageQueryDialog(Qt.QtWidgets.QDialog):

    def __init__(self, *args, **kwargs):
        '''
        pull args
        '''
        parent = kwargs.get('parent', False)
        self.title = kwargs.get('title', 'Title')
        self.message = kwargs.get('message', 'Message')
        #self.bool_message = kwargs.get('bool_message', 'Bool Message')
        #self.bool_initial_state = kwargs.get('bool_initial_state', True)
        self.ok_callback = kwargs.get('ok_callback', False)
        self.cancel_callback = kwargs.get('cancel_callback', False)

        # init
        super(MessageQueryDialog, self).__init__(parent)

        # window setup
        self.setWindowTitle(self.title)
        self.setVisible(True)  # without this, there are focus problems!!
        self.setObjectName(self.title)
        self.resize(300, 200)
        self.setModal(True)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window |
            Qt.QtCore.Qt.CustomizeWindowHint |
            Qt.QtCore.Qt.WindowTitleHint |
            Qt.QtCore.Qt.WindowCloseButtonHint |
            Qt.QtCore.Qt.WindowStaysOnTopHint
        )

        '''
        '''
        self.do_layout()

    def do_layout(self):
        '''
        main layout
        '''
        self.main_layout = GridLayout(self)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop | Qt.QtCore.Qt.AlignHCenter)

        '''
        elements
        '''
        self.message_label = Qt.QtWidgets.QLabel(self.message, self)
        self.okay_button = Qt.QtWidgets.QPushButton(u'确认', self)
        self.cancel_button = Qt.QtWidgets.QPushButton(u'取消', self)

        '''
        '''
        for w in [self.okay_button, self.cancel_button]:
            w.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
            w.setFixedHeight(30)

        '''

        '''
        #self.checkbox.setChecked(self.bool_initial_state)
        self.okay_button.clicked.connect(self.on_click_okay)
        self.cancel_button.clicked.connect(self.on_click_cancel)

        '''
        layout
        '''
        self.main_layout.addWidget(self.message_label, 0, 0, 1, 2, Qt.QtCore.Qt.AlignCenter)
        #self.main_layout.addWidget(self.checkbox, 1, 0, 1, 2, Qt.QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.okay_button, 1, 1, 1, 1)
        self.main_layout.addWidget(self.cancel_button, 1, 0, 1, 1)

    def on_click_okay(self):
        '''
        run callback, then close
        '''
        #state = self.checkbox.isChecked()
        if self.ok_callback:
            try:
                self.ok_callback()
            except Exception as e:
                print(2913, Exception, e)
        self.close()

    def on_click_cancel(self):
        '''
        run callback, then close
        '''
        #state = self.checkbox.isChecked()
        if self.cancel_callback:
            try:
                self.cancel_callback()
            except Exception as e:
                print(2959, Exception, e)
        self.close()

    def closeEvent(self, event):
        '''
        close
        '''
        return super(MessageQueryDialog, self).closeEvent(event)
        # return Qt.QtWidgets.QDialog.closeEvent(self, event)

class BoolQueryDialog(Qt.QtWidgets.QDialog):
    __instance__ = None

    def __init__(self, *args, **kwargs):
        '''
        pull args
        '''
        parent = kwargs.get('parent', False)
        self.title = kwargs.get('title', 'Title')
        self.message = kwargs.get('message', 'Message')
        self.bool_message = kwargs.get('bool_message', 'Bool Message')
        self.bool_initial_state = kwargs.get('bool_initial_state', True)
        self.ok_callback = kwargs.get('ok_callback', False)
        self.cancel_callback = kwargs.get('cancel_callback', False)

        # init
        super(BoolQueryDialog, self).__init__(parent)

        # window setup
        self.setWindowTitle(self.title)
        self.setVisible(True)  # without this, there are focus problems!!
        self.setObjectName(self.title)
        self.resize(300, 200)
        self.setModal(True)

        self.setWindowFlags(
            Qt.QtCore.Qt.Window |
            Qt.QtCore.Qt.CustomizeWindowHint |
            Qt.QtCore.Qt.WindowTitleHint |
            Qt.QtCore.Qt.WindowCloseButtonHint |
            Qt.QtCore.Qt.WindowStaysOnTopHint
        )

        '''
        '''
        self.do_layout()

    def do_layout(self):
        '''
        main layout
        '''
        self.main_layout = GridLayout(self)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop | Qt.QtCore.Qt.AlignHCenter)

        '''
        elements
        '''
        self.checkbox = Qt.QtWidgets.QCheckBox(self.bool_message, self)
        self.message_label = Qt.QtWidgets.QLabel(self.message, self)
        self.okay_button = Qt.QtWidgets.QPushButton(u'确认', self)
        self.cancel_button = Qt.QtWidgets.QPushButton(u'取消', self)

        '''
        '''
        for w in [self.okay_button, self.cancel_button]:
            w.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
            w.setFixedHeight(30)

        '''

        '''
        self.checkbox.setChecked(self.bool_initial_state)
        self.okay_button.clicked.connect(self.on_click_okay)
        self.cancel_button.clicked.connect(self.on_click_cancel)

        '''
        layout
        '''
        self.main_layout.addWidget(self.message_label, 0,0,1,2, Qt.QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.checkbox, 1, 0, 1, 2, Qt.QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.okay_button, 2, 1, 1, 1)
        self.main_layout.addWidget(self.cancel_button, 2, 0, 1, 1)

    def on_click_okay(self):
        '''
        run callback, then close
        '''
        state = self.checkbox.isChecked()
        if self.ok_callback:
            try:
                self.ok_callback(state)
            except Exception as e:
                print(2913, Exception, e)
        self.close()

    def on_click_cancel(self):
        '''
        run callback, then close
        '''
        state = self.checkbox.isChecked()
        if self.cancel_callback:
            try:
                self.cancel_callback(state)
            except Exception as e:
                print(2959, Exception, e)
        self.close()

    def closeEvent(self, event):
        '''
        close
        '''
        return super(BoolQueryDialog, self).closeEvent(event)
        # return Qt.QtWidgets.QDialog.closeEvent(self, event)




class VBoxLayout(Qt.QtWidgets.QVBoxLayout):

    def __init__(self, *args, **kwargs):
        #
        super(VBoxLayout, self).__init__(*args, **kwargs)

        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class GridWidget(Qt.QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        #
        super(GridWidget, self).__init__(*args, **kwargs)
        #
        self.setContentsMargins(0, 0, 0, 0)

        #
        self.main_layout = GridLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)

class GridLayout(Qt.QtWidgets.QGridLayout):

    def __init__(self, *args, **kwargs):
        #
        super(GridLayout, self).__init__(*args, **kwargs)

        self.setSpacing(2)
        self.setContentsMargins(3, 3, 3, 3)


class StackedLayout(Qt.QtWidgets.QStackedLayout):

    def __init__(self, *args, **kwargs):
        #
        super(StackedLayout, self).__init__(*args, **kwargs)

        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)


class ListWidget(Qt.QtWidgets.QListWidget):

    def __init__(self, *args, **kwargs):
        #
        super(ListWidget, self).__init__(*args, **kwargs)

        style = '''
        QListWidget::item
        {
            background: rgb(0,0,0,0);
        }
        QListWidget::item:selected
        {
            background: rgb(255,255,255,100);
        }
        '''
        self.setStyleSheet(style)


class ColoredButton(Qt.QtWidgets.QPushButton):
    def __init__(self, label, parent=False, color=[.4, .4, .4, 1], borderRadius=False, *args,
                 **kwargs):
        #
        super(ColoredButton, self).__init__(label, parent=parent, *args, **kwargs)

        # initial state
        self.color = Color(color)
        self.borderRadius = borderRadius

        # set initial colors
        self.updateButtonColors()

    def updateButtonColors(self):

        '''
        dynamically calculate high contrast text color
        '''
        averageColor = self.color.get_average_intensity()
        textColor = Color([1,1,1,1])
        if averageColor > 0.5:
            textColor.set_rgba([0,0,0,1])

        '''
        stylesheet
        '''
        styleSheet = ''

        '''
        regular
        '''
        bg_color = self.color.get_int_rgba_string()
        text_color = textColor.get_int_rgba_string()
        styleSheet += 'QPushButton{{background-color: {0};;color: {1};;}}'.format(bg_color, text_color)

        '''
        disabled
        '''
        backgroundColor = Color([0.5,0.5,0.5,1]).get_int_rgba_string()
        textColorModified = Color([0.2,0.2,0.2,1]).get_int_rgba_string()
        styleSheet += 'QPushButton:disabled   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                              textColorModified)

        '''
        pressed
        '''
        # modify darker
        backgroundColor = self.color.multiply_hsva([1, 1, .75, 1]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QPushButton:pressed   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                             textColorModified)

        '''
        focus
        '''
        backgroundColor = self.color.multiply_hsva([1, 1, .75, 1]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QPushButton:focus   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                           textColorModified)

        '''
        hover
        '''
        # modify brighter
        backgroundColor = self.color.lighten_hsva([0, 0.1, 0.5, 0]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QPushButton:hover   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                           textColorModified)

        '''
        assign stylesheet
        '''
        self.setStyleSheet(styleSheet)


class ColoredComboBox(Qt.QtWidgets.QComboBox):
    def __init__(self, *args, **kwargs):
        #
        super(ColoredComboBox, self).__init__(*args, **kwargs)

        # initial state
        self.color = Color([0.208, 0.480, 0.751, 1])
        self.borderRadius = 5
        self.height = 20
        self.command = None

        # set initial colors
        self.updateButtonColors()

    def wheelEvent(self, *args, **kwargs):
        return None

    def on_click(self):

        # run commands
        if self.command:
            self.command()

    def setCommand(self, command=False):
        if command:
            self.command = command

    def updateButtonColors(self):
        '''
        dynamically calculate high contrast text color
        '''
        averageColor = self.color.get_average_intensity()
        textColor = Color([1,1,1,1])
        if averageColor > 0.5:
            textColor = textColor.set_rgba([0,0,0,1])

        '''
        stylesheet
        '''
        styleSheet = ''

        '''
        regular
        '''
        bg_color = self.color.get_int_rgba_string()
        text_color = textColor.get_int_rgba_string()
        styleSheet += 'QComboBox{{background-color: {0};;color: {1};;}}'.format(bg_color, text_color)

        '''
        disabled
        '''
        backgroundColor = Color([0.5, 0.5, 0.5, 1]).get_int_rgba_string()
        textColorModified = Color([0.2, 0.2, 0.2, 1]).get_int_rgba_string()
        styleSheet += 'QComboBox:disabled   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                              textColorModified)

        '''
        pressed
        '''
        '''
        # modify darker
        backgroundColor = self.color.multiply_hsva([1, 1, .75, 1]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QComboBox:pressed   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                             textColorModified)
        '''

        '''
        focus
        '''
        backgroundColor = self.color.lighten_hsva([0, 0.5, 0.5, 0]).get_int_rgba_string()#self.color.multiply_hsva([1, 1, .75, 1]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QComboBox:focus   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                           textColorModified)

        '''
        hover
        '''
        # modify brighter
        backgroundColor = self.color.lighten_hsva([0, 0.5, 0.5, 0]).get_int_rgba_string()
        textColorModified = textColor.get_int_rgba_string()
        styleSheet += 'QComboBox:hover   {{background-color: {0};;color: {1};;}}'.format(backgroundColor,
                                                                                           textColorModified)

        '''
        assign stylesheet
        '''
        self.setStyleSheet(styleSheet)

class CollapsableWidget(Qt.QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        #
        super(CollapsableWidget, self).__init__(*args, **kwargs)

        '''
        attributes
        '''
        self.expand_state = True

        '''
        create container laayout
        '''
        containerLayout = Qt.QtWidgets.QGridLayout(self)
        containerLayout.setSpacing(0)
        containerLayout.setContentsMargins(0,0,0,0)
        '''
        elements
        '''
        self.expand_button = Qt.QtWidgets.QToolButton(self) #Qt.QtWidgets.QPushButton('', self)
        self.expand_button.setText('Section Label')
        self.expand_button.setToolButtonStyle(Qt.QtCore.Qt.ToolButtonTextBesideIcon)
        self.expand_button.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Preferred)
        self.expand_button.clicked.connect(self.on_click)

        self.main_widget = Qt.QtWidgets.QWidget(self)
        self.main_layout = Qt.QtWidgets.QVBoxLayout(self.main_widget)
        self.main_layout.setSpacing(3)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop)
        self.setLayout(self.main_layout)

        containerLayout.addWidget(self.expand_button, 0, 0, 1, 1)
        containerLayout.addWidget(self.main_widget, 1, 0, 1, 1)

        '''
        set initial state
        '''
        self.set_expand_state(True)

    def set_expand_state(self, state_var):
        '''
        store
        '''
        self.expand_state = state_var

        '''
        updates
        '''
        self.update_UI_state_change()

    def get_expand_state(self):
        return self.expand_state

    def set_section_label(self, string_var):
        self.expand_button.setText(string_var)

    def add_widget(self, w):
        self.main_layout.addWidget(w)


    def update_UI_state_change(self):
        '''
        arrow
        '''
        if self.get_expand_state():
            self.expand_button.setArrowType(Qt.QtCore.Qt.DownArrow)
        else:
            self.expand_button.setArrowType(Qt.QtCore.Qt.RightArrow)

    def on_click(self):
        '''
        update state
        '''
        self.set_expand_state(not self.get_expand_state())

        '''
        toggle visibilty of section
        '''
        self.main_widget.setVisible(self.get_expand_state())
        print('expand state:', self.get_expand_state())


class ScrollableLayoutWidget(Qt.QtWidgets.QScrollArea):

    def __init__(self, parent):
        super(ScrollableLayoutWidget, self).__init__(parent)

        '''
        contents area
        '''
        self.main_widget = Qt.QtWidgets.QWidget(self)
        self.main_layout = Qt.QtWidgets.QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(Qt.QtCore.Qt.AlignTop)
        self.main_layout.setSpacing(5)
        self.main_widget.setLayout(self.main_layout)

        '''
        scrollable area
        '''
        self.setFocusPolicy(Qt.QtCore.Qt.NoFocus)
        self.setWidgetResizable(True)
        self.setWidget(self.main_widget)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(Qt.QtWidgets.QFrame.NoFrame)

    def add_widget(self, widget):
        self.main_layout.addWidget(widget)


class DictTree(Qt.QtWidgets.QTreeWidget):
    items_clicked = Qt.QtCore.Signal()

    def __init__(self):
        super(DictTree, self).__init__()
        '''
        settings
        '''
        self.setHeaderHidden(True)
        self.setSelectionMode(Qt.QtWidgets.QAbstractItemView.ExtendedSelection)

    def mouseReleaseEvent(self, event):
        '''
        just for left clicks
        '''
        if event.button() == Qt.QtCore.Qt.LeftButton:
            self.on_click()


        '''
        let other QT stuff go on
        '''
        Qt.QtWidgets.QTreeView.mouseReleaseEvent(self, event)

    def on_click(self):
        '''
        emit items clicked event only
        '''
        self.items_clicked.emit()

        '''
        testing
        '''
        selected_items = self.selectedItems()
        child_items = self.get_end_children(selected_items)
        parent_items = self.get_top_parents(selected_items)
        #print(2218, len(parent_items), parent_items)

    def get_top_parents(self, items):
        if not items:
            return []

        '''
        initial list
        '''
        parent_items = []

        '''
        itterate items
        '''
        for item in items:
            parent = item
            '''
            get top parent
            '''
            while parent.parent():
                parent = parent.parent()
            parent_items.append(parent.text(0))

        '''
        cleanup
        '''
        parent_items = list(set(parent_items))

        return parent_items

    def get_end_children(self, items):
        if not items:
            return []

        '''
        initial list
        '''
        child_items = []

        '''
        recursive function
        '''
        def get_child_data_values(item_var):
            if not item_var:
                return
            if item_var.childCount():
                for i in range(item_var.childCount()):
                    child_item = item_var.child(i)
                    get_child_data_values(child_item)
            else:
                child_items.append(item_var.text(0))

        '''
        run it
        '''
        for item in items:
            get_child_data_values(item)
        child_items = list(set(child_items))

        '''
        return results
        '''
        return child_items

    def new_item(self, parent, text, val=None):
        child = Qt.QtWidgets.QTreeWidgetItem([text])
        self.fill_item(child, val)
        parent.addChild(child)
        child.setExpanded(False)

    def fill_item(self, item, value):
        if value is None:
            return
        elif isinstance(value, dict):
            for key, val in sorted(value.items()):
                self.new_item(item, str(key), val)
        elif isinstance(value, (list, tuple)):
            for val in value:
                text = (str(val) if not isinstance(val, (dict, list, tuple))
                        else '[%s]' % type(val).__name__)
                self.new_item(item, text, val)
        else:
            self.new_item(item, str(value))

    def set_dict_data(self, value):
        self.clear()
        self.fill_item(self.invisibleRootItem(), value)



class ConfirmButton(Qt.QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        '''
        store data
        '''
        self.internal_data = kwargs
        parent = self.get_data('parent', False)

        '''
        extra info
        '''
        has_extra_info = False
        display_message = self.get_data('display_message', False)
        display_checkbox = self.get_data('display_checkbox', False)
        if display_message or display_checkbox:
            has_extra_info = True
        self.set_data('has_extra_info', has_extra_info)

        '''
        super init
        '''
        super(ConfirmButton, self).__init__(parent)

        '''
        attributes
        '''
        self.expand_state = True

        '''
        create container laayout
        '''
        self.main_layout = Qt.QtWidgets.QGridLayout(self)
        self.main_layout.setSpacing(5)
        self.main_layout.setContentsMargins(0,0,0,0)

        '''
        elements
        '''
        button_label = self.get_data('button_label', 'Button Label')
        self.main_button = Qt.QtWidgets.QPushButton(button_label, self)
        self.main_button.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Preferred)

        self.okay_button = Qt.QtWidgets.QPushButton(u'确认', self)
        self.cancel_button = Qt.QtWidgets.QPushButton(u'取消', self)
        for w in [self.okay_button, self.cancel_button]:
            w.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Preferred)

        '''
        '''
        self.main_button.clicked.connect(self.on_click_main_button)
        self.okay_button.clicked.connect(self.on_click_okay_button)
        self.cancel_button.clicked.connect(partial(self.set_expand_state, False))

        '''
        extra info
        '''
        self.expand_widget = Qt.QtWidgets.QWidget(self)
        self.expand_layout = Qt.QtWidgets.QVBoxLayout(self.expand_widget)
        self.expand_layout.setSpacing(3)
        self.expand_layout.setContentsMargins(0, 0, 0, 0)

        self.expand_layout.setAlignment(Qt.QtCore.Qt.AlignTop)
        self.expand_widget.setLayout(self.expand_layout)

        button_message = self.get_data('button_message', 'Button Message')
        self.info_message = Qt.QtWidgets.QLabel(button_message, self.expand_widget )
        button_checkbox_message = self.get_data('button_checkbox_message', 'Checkbox Message')
        self.info_checkbox = Qt.QtWidgets.QCheckBox(button_checkbox_message, self.expand_widget)
        self.expand_layout.addWidget(self.info_message)
        self.expand_layout.addWidget(self.info_checkbox)

        self.info_message.setVisible(display_message)
        self.info_checkbox.setVisible(display_checkbox)
        button_checkbox_initial_state = self.get_data('self.button_checkbox_initial_state', True)
        self.set_checked_state(button_checkbox_initial_state)

        '''
        layout
        '''
        self.main_layout.addWidget(self.main_button, 0, 0, 1, 2)
        self.main_layout.addWidget(self.okay_button, 0, 1, 1, 1)
        self.main_layout.addWidget(self.cancel_button, 0, 0, 1, 1)
        self.main_layout.addWidget(self.expand_widget, 1, 0, 1, 2)

        '''
        set initial state
        '''
        self.set_expand_state(False)

    def get_data(self, key, default):
        return self.internal_data.get(key, default)

    def set_data(self, key, value):
        self.internal_data[key] = value

    @classmethod
    def get_kwarg_template(cls):
        kwargs = {}

        kwargs['parent'] = False

        kwargs['button_okay_command'] = False

        kwargs['button_label'] = 'Button Label'
        kwargs['button_message'] = 'Button Message Here?'
        kwargs['button_checkbox_message'] = 'Checkbox Label'
        kwargs['button_checkbox_initial_state'] = True

        kwargs['button_confirm_required'] = False
        kwargs['display_message'] = False
        kwargs['display_checkbox'] = False
        kwargs['button_is_valid_checking'] = False

        return kwargs

    def on_click_main_button(self):
        button_confirm_required = self.get_data('button_confirm_required', False)
        if button_confirm_required:
            self.set_expand_state(True)
        else:
            self.run_command()

    def on_click_okay_button(self):
        self.run_command()
        self.set_expand_state(False)

    def set_checked_state(self, state_var):
        '''
        '''
        lookup = {}
        lookup[True] = Qt.QtCore.Qt.Checked
        lookup[False] = Qt.QtCore.Qt.Unchecked
        self.info_checkbox.setCheckState(lookup.get(state_var, 'False'))

    def get_checked_state(self,):
        return self.info_checkbox.isChecked()

    def set_expand_state(self, state_var):
        '''
        store
        '''
        self.expand_state = state_var

        '''
        updates
        '''
        self.update_UI_state_change()

    def run_command(self):
        try:
            checkbox_state = self.info_checkbox.isChecked()
            command = self.get_data('button_okay_command', False)
            if command:
                command(checkbox_state)
        except Exception as e:
            print(3684, Exception, e)
            print (traceback.format_exc())

    def set_valid(self, state):
        button_is_valid_checking = self.get_data('button_is_valid_checking', False)
        #print(3805, 'set_valid', button_is_valid_checking)
        if button_is_valid_checking:
            self.setEnabled(state)

    def get_expand_state(self):
        return self.expand_state

    def update_UI_state_change(self):
        '''
        set display
        '''
        self.main_button.setVisible(not self.get_expand_state())

        self.okay_button.setVisible(self.get_expand_state())
        self.cancel_button.setVisible(self.get_expand_state())

        '''
        toggle if feature being used
        '''
        expand_widget_state = self.get_data('has_extra_info', False)
        if expand_widget_state:
            expand_widget_state = self.get_expand_state()
        self.expand_widget.setVisible(expand_widget_state)


class SimpleDataHandler(object):

    def __init__(self, *args, **kwargs):
        #
        self.data = kwargs.pop('data', {})

        #
        super(SimpleDataHandler, self).__init__(*args, **kwargs)


    @classmethod
    def get_template_data(cls):
        data = {}

        # color
        data['background'] = []

        #
        return copy.deepcopy(data)

    def get_data_key(self, key, default_value):
        if not self.data:
            self.data = self.get_template_data()
        return self.data.get(key, default_value)

    def get_all_data(self):
        if not self.data:
            self.data = self.get_template_data()
        return self.data

    def set_data_key(self, key, value):
        self.data[key] = value

    def update_data(self, data):
        #
        self.data.update(data)

        #
        self.on_data_change()

    def modify_data(self):
        '''modify any data that is automatic/dynamic'''

    def on_data_change(self):
        # update visuals
        self.on_redraw_pre()

        # do the redraw
        self.on_redraw()

    def on_pallete_change(self):
        # update visuals
        self.on_redraw_pre()

        # do the redraw
        self.on_redraw()

    def on_redraw_pre(self):
        # modify data
        self.modify_data()

    def on_redraw(self):
        '''over write, do visual updating here'''
        data = self.get_all_data()

        # do stuff

class EditableLabelWidget(SimpleDataHandler, Qt.QtWidgets.QWidget):
    on_text_edit = Qt.QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(EditableLabelWidget, self).__init__(*args, **kwargs)

        # config
        self.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)

        # layout
        self.main_layout = Qt.QtWidgets.QStackedLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # edit
        data = EditableTextField.get_template_data()
        self.edit_widget = EditableTextField(self, data = data)
        self.main_layout.addWidget(self.edit_widget)

        # display
        data = EditableLabel.get_template_data()
        self.display_widget = EditableLabel(self, data = data)
        self.main_layout.addWidget(self.display_widget)

        # connections
        Utils.doubleClickable(self.display_widget).connect(self.set_editible)
        self.edit_widget.on_text_editing.connect(self.on_edit_action)
        self.edit_widget.on_text_edit_finish.connect(self.on_edit_finished_action)
        self.edit_widget.on_text_edit_cancel.connect(self.on_edit_cancelled_action)

        #
        self.on_data_change()

    def modify_data(self):
        '''modify any data that is automatic/dynamic'''

    def on_redraw(self):
        #
        data = self.get_all_data()

        #
        is_edit_mode = self.get_data_key('is_edit_mode', False)
        self.toggle_editor(is_edit_mode)

        # set label text
        display_text = data['text']
        self.display_widget.setText(display_text)

    def on_edit_action(self, *args, **kwargs):
        ''''''
        #print(3759, 'on_edit_action', args, kwargs)
        # no need to do anything here

    def on_edit_finished_action(self, *args, **kwargs):
        ''''''
        # store new string

        text_string = self.edit_widget.get_data_key('text', 'new text')
        self.set_data_key('text', text_string)
        #print(3784, 'self.edit_widget.data', self.edit_widget.data)
        #print(3788, 'on_edit_finished_action', text_string, args, kwargs)

        # update label
        data = {}
        data['text'] = text_string
        self.display_widget.update_data(data)

        # toggle
        self.toggle_editor(False)

        # emit
        self.on_text_edit.emit(text_string)

    def on_edit_cancelled_action(self, *args, **kwargs):
        ''''''
        #print(3759, 'on_edit_cancelled_action', args, kwargs)

        # dont save anything, just toggle back
        self.toggle_editor(False)

    def set_editible(self):
        # set editor text
        data = {}
        display_text = self.get_data_key('text', 'display text')
        display_text = display_text.split('|')[-1].split(':')[-1]# simplify when editing
        data['text'] = display_text

        self.edit_widget.update_data(data)

        # enable editing
        self.toggle_editor(True)

    def toggle_editor(self, is_edit_mode):
        # settings have changed
        # = self.get_data_key('is_edit_mode', False)
        #if is_edit_mode != current_is_edit_mode or True:

        if is_edit_mode:
            self.main_layout.setCurrentIndex(0)
            self.edit_widget.blockSignals(True)
            self.edit_widget.setFocus()
            self.edit_widget.selectAll()
            self.edit_widget.blockSignals(False)
        else:
            self.main_layout.setCurrentIndex(1)
            #self.clearFocus()

        # update stored value
        self.set_data_key('is_edit_mode', False)

    @classmethod
    def get_template_data(cls):
        data = {}

        # color
        data['background'] = []
        data['text'] = 'test text'
        data['is_edit_mode'] = False

        #
        return copy.deepcopy(data)

class EditableLabel(SimpleDataHandler, Qt.QtWidgets.QLabel):
    on_double_clicked = Qt.QtCore.Signal()
    on_click = Qt.QtCore.Signal()

    def __init__(self, *args, **kwargs):
        super(EditableLabel, self).__init__(*args, **kwargs)


        #
        self.on_data_change()

    def on_redraw(self):
        #
        data = self.get_all_data()

        # text
        display_text = data['text']
        self.setText(display_text)

    @classmethod
    def get_template_data(cls):
        data = {}

        # color
        data['background'] = []
        data['text'] = 'test text'

        #
        return copy.deepcopy(data)

class EditableTextField(SimpleDataHandler, Qt.QtWidgets.QLineEdit):
    on_text_editing = Qt.QtCore.Signal(str)
    on_text_edit_finish = Qt.QtCore.Signal(str)
    on_text_edit_cancel = Qt.QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super(EditableTextField, self).__init__(*args, **kwargs)

        #properties
        self.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        # self.setAlignment(Qt.QtCore.Qt.AlignCenter)
        # self.color = [0.2,0.2,0.2,1]
        self.editNotesBuffer = self.get_data_key('text', 'not set') #textVar

        # set display text
        self.setDisplayText(self.editNotesBuffer)

        #
        self.installEventFilter(self)

        # connections
        self.textChanged.connect(self.editNote)
        self.editingFinished.connect(self.editing_finished)

        #
        self.on_data_change()

    @classmethod
    def get_template_data(cls):
        data = {}

        # color
        data['background'] = []
        data['text'] = 'test text'

        #
        return copy.deepcopy(data)

    def on_redraw(self):
        #
        data = self.get_all_data()

        #
        display_text = data['text']


        #
        self.setDisplayText(display_text)

    def eventFilter(self, obj, event):
        if not obj.isWidgetType():
            return False
        # vents
        # eventType = event.type()
        # button = False
        if isinstance(event, Qt.QtGui.QMouseEvent):
            if event.modifiers() != Qt.QtCore.Qt.NoModifier:
                return False
            # button = event.button()

        # escape
        if event.type() == Qt.QtCore.QEvent.KeyPress:
            if event.key() == Qt.QtCore.Qt.Key_Escape:
                if self.cancelEdit:
                    self.cancelEdit()
                return True

        # consume all
        return False  # super(EditableTextField, self).eventFilter(obj, event)

    def editNote(self, *args, **kwargs):
        '''
        get new text
        '''
        stringVar = ''
        if args:
            stringVar = args[0]

        self.on_text_editing.emit(stringVar)

    def setDisplayText(self, text):
        self.setText(text)
        self.setToolTip(text)

    def editing_finished(self):

        '''
        clear focus
        '''
        self.blockSignals(True)
        self.clearFocus()
        self.blockSignals(False)

        # store
        stringVar = self.text()
        self.editNotesBuffer = stringVar
        self.set_data_key('text', stringVar)

        #print(3960, 'editing_finished', stringVar, self.data)

        #callback if changed
        self.on_text_edit_finish.emit(stringVar)

    def cancelEdit(self):
        '''
        reset to buffer
        '''
        self.setText(self.editNotesBuffer)

        '''
        '''
        self.on_text_edit_cancel.emit(self.editNotesBuffer)
        # if self.onTextEditCancelCommand:
        #    self.onTextEditCancelCommand(self.editNotesBuffer)


class Utils():

    @classmethod
    def doubleClickable(cls, widget):
        class Filter(Qt.QtCore.QObject):
            clicked = Qt.QtCore.Signal()

            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == Qt.QtCore.QEvent.MouseButtonDblClick:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            return True
                return False

        f = Filter(widget)
        widget.installEventFilter(f)
        return f.clicked










from .ui_bridge import install
install(globals())
