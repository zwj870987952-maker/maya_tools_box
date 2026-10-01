# Copyright 2024 Philippe Ratté
# Local candidate adaptation; restrictive EULA retained in upstream/LICENSE.txt.
import sys
import os
import maya.OpenMayaUI as omui
from ..runtime import mc
import maya.mel as mel
import json
pyside_version = '2'
try:
    from PySide6 import QtWidgets as qt_w
    from PySide6 import QtCore as qt_c
    from PySide6 import QtGui as qt_g
    from shiboken6 import wrapInstance
    pyside_version = '6'
except ImportError:
    from PySide2 import QtWidgets as qt_w
    from PySide2 import QtCore as qt_c
    from PySide2 import QtGui as qt_g
    from shiboken2 import wrapInstance
    pyside_version = '2'
from pathlib import Path
from .packages import overlap_package as over_p
from .. import ui_bridge as bridge
script_path = str(Path(__file__).resolve().parent)
default_options_path = os.path.join(script_path, 'default.json')
icon_path = os.path.join(script_path, 'icons')
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

class overslapper_UI(MayaQWidgetBaseMixin, qt_w.QWidget):
    """    UI Class """
    WIN_NAME = 'mtkOverslapperCandidate'
    TITLE = 'mtkOverslapperCandidate'

    def __init__(self, *args, **kwargs):
        super(overslapper_UI, self).__init__(*args, **kwargs)
        screen = self.screen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        pixel_ratio = screen.devicePixelRatio()
        self.width_scale = screen_width / 1920
        self.height_scale = screen_height / 1080
        self.setWindowTitle('OverSlapper 1.0.3')
        self.width_value = int(285 * self.width_scale)
        self.setMinimumWidth(self.width_value)
        self.current_main_axis = 0
        self.axes = ['x+', 'x-', 'y+', 'y-', 'z+', 'z-']
        self.z_axis = ['x+', 'x-', 'y+', 'y-']
        self.x_axis = ['y+', 'y-', 'z+', 'z-']
        self.y_axis = ['x+', 'x-', 'z+', 'z-']
        self.z_axis = ['x+', 'x-', 'y+', 'y-']
        self.overlap_button_text = 'overlap'
        self.custom_var = 'mtkOverslapperCandidateGradient'
        mc.optionVar(rm=self.custom_var)
        mc.optionVar(sva=[self.custom_var, '1,0,3'])
        mc.optionVar(sva=[self.custom_var, '0,1,3'])
        self.int_validator = qt_g.QIntValidator()
        self.float_validator = qt_g.QDoubleValidator()
        self.float_validator_0_1 = qt_g.QDoubleValidator()
        self.float_validator_0_1.setRange(0.0, 1.0, -1)
        self.offset_temp_val = '0.0'
        self.timeline_height_value = 0
        self.parent_height_value = 0
        self.distance_height_value = 0
        self.start_height = int(305 * self.height_scale)
        self.error_height = 0
        self.axes_height = 0
        self.overshoot_height = 0
        self.wind_height = 0
        self.create_widgets()
        self.create_layout()
        self.connect_ui()
        self.set_tooltips()
        if os.path.exists(default_options_path):
            self.preset_file = default_options_path
            try:
                self.import_ui_data(True, True, True, True, True, True, True, True)
            except:
                self.error_ui('corrupt_default', '')
        else:
            self.error_ui('missing_default', '')

    def create_layout(self):
        main_layout = qt_w.QVBoxLayout(self)
        base_setting_layout = qt_w.QHBoxLayout()
        base_setting_layout.addWidget(self.menubar)
        self.create_v_separator(base_setting_layout)
        base_setting_layout.addWidget(self.axes_spacer)
        base_setting_layout.addWidget(self.axis_x_checkbox, 0)
        base_setting_layout.addWidget(self.axis_y_checkbox, 0)
        base_setting_layout.addWidget(self.axis_z_checkbox, 0)
        self.create_v_separator(base_setting_layout)
        self.overlap_type_palette = self.create_palette(base_setting_layout, 255, 255, 0)
        base_setting_layout.addWidget(self.overlap_type)
        translation_layout = qt_w.QHBoxLayout()
        self.translation_palette = self.create_palette(translation_layout, 0, 255, 255)
        self.translation_palette.setVisible(False)
        translation_layout.addWidget(self.translation_strength_label)
        translation_layout.addWidget(self.translation_strength_slider)
        translation_layout.addWidget(self.translation_strength_value)
        axes_layout = qt_w.QHBoxLayout()
        self.axes_palette = self.create_palette(axes_layout, 255, 255, 0)
        axes_layout.addWidget(self.main_axis_label)
        axes_layout.addWidget(self.main_axis_combo_box)
        axes_layout.addWidget(self.up_axis_label)
        axes_layout.addWidget(self.up_axis_combo_box)
        distance_layout = qt_w.QHBoxLayout()
        self.distance_palette = self.create_palette(distance_layout, 255, 255, 0)
        self.distance_palette.setVisible(False)
        distance_layout.addWidget(self.distance_label)
        distance_layout.addWidget(self.distance_value)
        distance_layout.addWidget(self.distance_button)
        timeline_layout = qt_w.QHBoxLayout()
        self.create_palette(timeline_layout, 0, 255, 0)
        timeline_layout.addWidget(self.timeline_combo_box, alignment=qt_c.Qt.AlignLeft)
        timeline_layout.addWidget(self.timeline_start)
        timeline_layout.addWidget(self.timeline_end)
        strength_layout = qt_w.QHBoxLayout()
        self.create_palette(strength_layout, 0, 255, 0)
        strength_layout.addWidget(self.strength_label)
        strength_layout.addWidget(self.strength_slider)
        strength_layout.addWidget(self.strength_value)
        stiffness_layout_1 = qt_w.QHBoxLayout()
        self.stiffness_palette = self.create_palette(stiffness_layout_1, 0, 255, 0)
        stiffness_layout_1.addWidget(self.stiffness_label)
        stiffness_layout_1.addWidget(self.stiffness_slider)
        stiffness_layout_1.addWidget(self.stiffness_value)
        falloff_layout = qt_w.QVBoxLayout()
        self.falloff_layout_h_1 = qt_w.QHBoxLayout()
        falloff_layout_v_1 = qt_w.QVBoxLayout()
        falloff_layout_h_2 = qt_w.QHBoxLayout()
        falloff_layout_h_3 = qt_w.QHBoxLayout()
        falloff_layout_h_4 = qt_w.QHBoxLayout()
        falloff_layout_v_1.addWidget(self.one_widget)
        falloff_layout_v_1.addWidget(self.zero_widget)
        self.stiffness_complex_palette_1 = self.create_palette(self.falloff_layout_h_1, 167, 255, 105)
        self.stiffness_complex_palette_1.setVisible(False)
        self.falloff_layout_h_1.addWidget(self.falloff_widget)
        self.falloff_layout_h_1.addLayout(falloff_layout_v_1)
        falloff_layout_h_2.addWidget(self.spacer_widget)
        falloff_layout_h_2.addWidget(self.start_widget)
        falloff_layout_h_2.addWidget(self.end_widget)
        self.stiffness_complex_palette_2 = self.create_palette(falloff_layout_h_3, 167, 255, 105)
        self.stiffness_complex_palette_2.setVisible(False)
        falloff_layout_h_3.addWidget(self.selected_position_label)
        falloff_layout_h_3.addWidget(self.selected_position)
        falloff_layout_h_3.addWidget(self.selected_value_label)
        falloff_layout_h_3.addWidget(self.selected_value)
        self.stiffness_complex_palette_3 = self.create_palette(falloff_layout_h_4, 167, 255, 105)
        self.stiffness_complex_palette_3.setVisible(False)
        falloff_layout_h_4.addWidget(self.interpolation_label)
        falloff_layout_h_4.addWidget(self.interpolation_combo_box)
        falloff_layout.addLayout(self.falloff_layout_h_1)
        falloff_layout.addLayout(falloff_layout_h_2)
        self.stiffness_separator = self.create_separator(falloff_layout)
        self.stiffness_separator.setVisible(False)
        falloff_layout.addLayout(falloff_layout_h_3)
        falloff_layout.addLayout(falloff_layout_h_4)
        overshoot_v_layout = qt_w.QVBoxLayout()
        overshoot_h_layout_1 = qt_w.QHBoxLayout()
        overshoot_h_layout_2 = qt_w.QHBoxLayout()
        overshoot_h_layout_3 = qt_w.QHBoxLayout()
        overshoot_v_layout.addLayout(overshoot_h_layout_1)
        self.overshoot_separator_1 = self.create_separator(overshoot_v_layout)
        overshoot_v_layout.addLayout(overshoot_h_layout_2)
        self.overshoot_separator_1.setVisible(False)
        self.overshoot_separator_2 = self.create_separator(overshoot_v_layout)
        overshoot_v_layout.addLayout(overshoot_h_layout_3)
        self.overshoot_separator_2.setVisible(False)
        self.overshoot_palette_1 = self.create_palette(overshoot_h_layout_1, 255, 105, 255)
        self.overshoot_palette_1.setVisible(False)
        overshoot_h_layout_1.addWidget(self.overshoot_strength_label)
        overshoot_h_layout_1.addWidget(self.overshoot_strength_slider)
        overshoot_h_layout_1.addWidget(self.overshoot_strength_value)
        self.overshoot_palette_2 = self.create_palette(overshoot_h_layout_2, 255, 105, 255)
        self.overshoot_palette_2.setVisible(False)
        overshoot_h_layout_2.addWidget(self.overshoot_frequency_lablel)
        overshoot_h_layout_2.addWidget(self.overshoot_frequency_slider)
        overshoot_h_layout_2.addWidget(self.overshoot_frequency_value)
        wind_v_layout = qt_w.QVBoxLayout()
        wind_h_layout = qt_w.QHBoxLayout()
        self.wind_palette = self.create_palette(wind_h_layout, 162, 255, 255)
        self.wind_palette.setVisible(False)
        wind_h_layout.addWidget(self.wind_strength_label)
        wind_h_layout.addWidget(self.wind_strength_slider)
        wind_h_layout.addWidget(self.wind_strength_value)
        wind_v_layout.addLayout(wind_h_layout)
        self.wind_separator = self.create_separator(wind_v_layout)
        self.wind_separator.setVisible(False)
        parent_layout = qt_w.QHBoxLayout()
        parent_layout.addWidget(self.parent_result)
        parent_layout.addWidget(self.parent_button)
        selection_type_layout = qt_w.QHBoxLayout()
        self.create_palette(selection_type_layout, 0, 255, 0)
        selection_type_layout.addWidget(self.selection_label)
        selection_type_layout.addWidget(self.selection_combo_box)
        animation_type_layout = qt_w.QHBoxLayout()
        self.create_palette(animation_type_layout, 0, 255, 0)
        animation_type_layout.addWidget(self.animation_label)
        animation_type_layout.addWidget(self.animation_combo_box)
        main_layout.addLayout(base_setting_layout)
        self.timeline_separator = self.create_separator(main_layout)
        main_layout.addLayout(timeline_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(translation_layout)
        main_layout.addLayout(axes_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(distance_layout)
        self.distance_separator = self.create_separator(main_layout)
        self.distance_separator.setVisible(False)
        main_layout.addLayout(strength_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(stiffness_layout_1)
        main_layout.addLayout(falloff_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(overshoot_v_layout)
        main_layout.addLayout(wind_v_layout)
        main_layout.addLayout(selection_type_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(animation_type_layout)
        self.create_separator(main_layout)
        main_layout.addLayout(parent_layout)
        self.parent_separator = self.create_separator(main_layout)
        self.parent_separator.setVisible(False)
        main_layout.addWidget(self.basic_button)
        main_layout.addWidget(self.error_label, alignment=qt_c.Qt.AlignHCenter)
        main_layout.addWidget(self.progress_bar, alignment=qt_c.Qt.AlignHCenter)

    def create_widgets(self):
        self.menubar = qt_w.QMenuBar()
        self.icon = qt_g.QIcon('{}\\gearIcon.png'.format(icon_path))
        self.layers_menu = qt_w.QMenu('Anim layers options')
        self.overshoot_menu = qt_w.QMenu('Overshoot options')
        self.simulation_menu = qt_w.QMenu('Simulation options')
        self.other_menu = qt_w.QMenu('Bonus options')
        self.presets_menu = qt_w.QMenu('Presets options')
        self.options_menu = self.menubar.addMenu(self.icon, '')
        if pyside_version == '2':
            self.parent_option = qt_w.QAction('Remove parent influence', self)
        elif pyside_version == '6':
            self.parent_option = qt_g.QAction('Remove parent influence', self)
        self.parent_option.setCheckable(True)
        if pyside_version == '2':
            self.stiffness_option = qt_w.QAction('Complex stiffness', self)
        elif pyside_version == '6':
            self.stiffness_option = qt_g.QAction('Complex stiffness', self)
        self.stiffness_option.setCheckable(True)
        if pyside_version == '2':
            self.axes_option = qt_w.QAction('Customize axes ', self)
        elif pyside_version == '6':
            self.axes_option = qt_g.QAction('Customize axes ', self)
        self.axes_option.setCheckable(True)
        if pyside_version == '2':
            self.rotation_translation_option = qt_w.QAction('Rotation overlap ignore its own translation', self)
        elif pyside_version == '6':
            self.rotation_translation_option = qt_g.QAction('Rotation overlap ignore its own translation', self)
        self.rotation_translation_option.setCheckable(True)
        self.rotation_translation_option.setChecked(True)
        if pyside_version == '2':
            self.default_distance_option = qt_w.QAction('Default distance for rotation', self)
        elif pyside_version == '6':
            self.default_distance_option = qt_g.QAction('Default distance for rotation', self)
        self.default_distance_option.setCheckable(True)
        if pyside_version == '2':
            self.default_distance_only_option = qt_w.QAction('Use only the default distance', self)
        elif pyside_version == '6':
            self.default_distance_only_option = qt_g.QAction('Use only the default distance', self)
        self.default_distance_only_option.setCheckable(True)
        if pyside_version == '2':
            self.cycle_option = qt_w.QAction('Cycle animation', self)
        elif pyside_version == '6':
            self.cycle_option = qt_g.QAction('Cycle animation', self)
        self.cycle_option.setCheckable(True)
        if pyside_version == '2':
            self.wind_option = qt_w.QAction('Wind', self)
        elif pyside_version == '6':
            self.wind_option = qt_g.QAction('Wind', self)
        self.wind_option.setCheckable(True)
        if pyside_version == '2':
            self.wind_absolute_option = qt_w.QAction('Wind is absolute in translation', self)
        elif pyside_version == '6':
            self.wind_absolute_option = qt_g.QAction('Wind is absolute in translation', self)
        self.wind_absolute_option.setCheckable(True)
        if pyside_version == '2':
            self.wind_control_option = qt_w.QAction('Create a wind control', self)
        elif pyside_version == '6':
            self.wind_control_option = qt_g.QAction('Create a wind control', self)
        self.wind_control_option.setCheckable(False)
        if pyside_version == '2':
            self.wind_select_option = qt_w.QAction('Select all winds controls', self)
        elif pyside_version == '6':
            self.wind_select_option = qt_g.QAction('Select all winds controls', self)
        self.wind_select_option.setCheckable(False)
        if pyside_version == '2':
            self.wind_off_option = qt_w.QAction('Turn all winds controls off', self)
        elif pyside_version == '6':
            self.wind_off_option = qt_g.QAction('Turn all winds controls off', self)
        self.wind_off_option.setCheckable(False)
        if pyside_version == '2':
            self.wind_on_option = qt_w.QAction('Turn all winds controls on', self)
        elif pyside_version == '6':
            self.wind_on_option = qt_g.QAction('Turn all winds controls on', self)
        self.wind_on_option.setCheckable(False)
        if pyside_version == '2':
            self.overshoot_option = qt_w.QAction('Overshoot', self)
        elif pyside_version == '6':
            self.overshoot_option = qt_g.QAction('Overshoot', self)
        self.overshoot_option.setCheckable(True)
        if pyside_version == '2':
            self.overshoot_first_option = qt_w.QAction('Overshoot only the first controller', self)
        elif pyside_version == '6':
            self.overshoot_first_option = qt_g.QAction('Overshoot only the first controller', self)
        self.overshoot_first_option.setCheckable(True)
        if pyside_version == '2':
            self.overshoot_between_option = qt_w.QAction('Overshoot in between', self)
        elif pyside_version == '6':
            self.overshoot_between_option = qt_g.QAction('Overshoot in between', self)
        self.overshoot_between_option.setCheckable(True)
        self.overshoot_between_option.setChecked(True)
        if pyside_version == '2':
            self.overshoot_end_option = qt_w.QAction('Overshoot at the end', self)
        elif pyside_version == '6':
            self.overshoot_end_option = qt_g.QAction('Overshoot at the end', self)
        self.overshoot_end_option.setCheckable(True)
        self.overshoot_end_option.setChecked(True)
        if pyside_version == '2':
            self.create_layer_option = qt_w.QAction('Bake to a new anim layer', self)
        elif pyside_version == '6':
            self.create_layer_option = qt_g.QAction('Bake to a new anim layer', self)
        self.create_layer_option.setCheckable(True)
        if pyside_version == '2':
            self.add_to_layer_option = qt_w.QAction('Bake to selected anim layer', self)
        elif pyside_version == '6':
            self.add_to_layer_option = qt_g.QAction('Bake to selected anim layer', self)
        self.add_to_layer_option.setCheckable(True)
        if pyside_version == '2':
            self.additive_layer = qt_w.QAction('Additive anim layer mode', self)
        elif pyside_version == '6':
            self.additive_layer = qt_g.QAction('Additive anim layer mode', self)
        self.additive_layer.setCheckable(True)
        self.additive_layer.setChecked(True)
        if pyside_version == '2':
            self.override_layer = qt_w.QAction('Override anim layer mode', self)
        elif pyside_version == '6':
            self.override_layer = qt_g.QAction('Override anim layer mode', self)
        self.override_layer.setCheckable(True)
        if pyside_version == '2':
            self.export_option = qt_w.QAction('Export a preset', self)
        elif pyside_version == '6':
            self.export_option = qt_g.QAction('Export a preset', self)
        self.export_option.setCheckable(False)
        if pyside_version == '2':
            self.import_option = qt_w.QAction('Import a preset', self)
        elif pyside_version == '6':
            self.import_option = qt_g.QAction('Import a preset', self)
        self.import_option.setCheckable(False)
        if pyside_version == '2':
            self.partial_import_option = qt_w.QAction('Partial import a preset', self)
        elif pyside_version == '6':
            self.partial_import_option = qt_g.QAction('Partial import a preset', self)
        self.partial_import_option.setCheckable(False)
        self.layers_menu.addAction(self.add_to_layer_option)
        self.layers_menu.addAction(self.create_layer_option)
        self.layers_menu.addAction(self.additive_layer)
        self.layers_menu.addAction(self.override_layer)
        self.overshoot_menu.addAction(self.overshoot_option)
        self.overshoot_menu.addAction(self.overshoot_first_option)
        self.overshoot_menu.addAction(self.overshoot_between_option)
        self.overshoot_menu.addAction(self.overshoot_end_option)
        self.simulation_menu.addAction(self.wind_option)
        self.simulation_menu.addAction(self.wind_absolute_option)
        self.simulation_menu.addAction(self.wind_control_option)
        self.simulation_menu.addAction(self.wind_select_option)
        self.simulation_menu.addAction(self.wind_off_option)
        self.simulation_menu.addAction(self.wind_on_option)
        self.other_menu.addAction(self.axes_option)
        self.other_menu.addAction(self.stiffness_option)
        self.other_menu.addAction(self.parent_option)
        self.other_menu.addAction(self.rotation_translation_option)
        self.other_menu.addAction(self.default_distance_option)
        self.other_menu.addAction(self.default_distance_only_option)
        self.other_menu.addAction(self.cycle_option)
        self.presets_menu.addAction(self.export_option)
        self.presets_menu.addAction(self.import_option)
        self.presets_menu.addAction(self.partial_import_option)
        self.options_menu.addMenu(self.layers_menu)
        self.options_menu.addMenu(self.overshoot_menu)
        self.options_menu.addMenu(self.simulation_menu)
        self.options_menu.addMenu(self.other_menu)
        self.options_menu.addMenu(self.presets_menu)
        self.overlap_type_label = qt_w.QLabel('mode:')
        self.overlap_type = qt_w.QComboBox()
        self.overlap_type.addItem('rotation')
        self.overlap_type.addItem('translation')
        self.overlap_type.setMaximumWidth(int(85 * self.width_scale))
        self.translation_strength_label = qt_w.QLabel('frame lag:')
        self.translation_strength_label.setVisible(False)
        self.translation_strength_label.setMaximumHeight(int(15 * self.height_scale))
        self.translation_strength_slider = qt_w.QSlider()
        self.translation_strength_slider.setValue(100)
        self.translation_strength_slider.setMinimum(1)
        self.translation_strength_slider.setMaximum(1000)
        self.translation_strength_slider.setOrientation(qt_c.Qt.Horizontal)
        self.translation_strength_slider.setVisible(False)
        self.translation_strength_slider.setMaximumHeight(int(15 * self.height_scale))
        self.translation_strength_value = qt_w.QLineEdit('1')
        self.translation_strength_value.setValidator(self.float_validator)
        self.translation_strength_value.setFixedWidth(int(30 * self.width_scale))
        self.translation_strength_value.setVisible(False)
        self.basic_button = qt_w.QPushButton(self.overlap_button_text, self)
        self.axes_spacer = qt_w.QLabel()
        self.axes_spacer.setMinimumWidth(int(120 * self.width_scale))
        self.axis_x_checkbox = qt_w.QCheckBox('X')
        self.axis_x_checkbox.setMaximumWidth(int(30 * self.width_scale))
        self.axis_x_checkbox.setVisible(False)
        self.axis_x_checkbox.setChecked(True)
        self.axis_x_checkbox.setStyleSheet('color:red; font: bold')
        self.axis_y_checkbox = qt_w.QCheckBox('Y')
        self.axis_y_checkbox.setMaximumWidth(int(30 * self.width_scale))
        self.axis_y_checkbox.setVisible(False)
        self.axis_y_checkbox.setChecked(True)
        self.axis_y_checkbox.setStyleSheet('color:lime; font: bold')
        self.axis_z_checkbox = qt_w.QCheckBox('Z')
        self.axis_z_checkbox.setMaximumWidth(int(30 * self.width_scale))
        self.axis_z_checkbox.setVisible(False)
        self.axis_z_checkbox.setChecked(True)
        self.axis_z_checkbox.setStyleSheet('color:blue; font: bold')
        self.main_axis_label = qt_w.QLabel('aim axis:')
        self.main_axis_combo_box = qt_w.QComboBox()
        for axes in self.axes:
            self.main_axis_combo_box.addItem(axes)
        self.color_swap('x', self.main_axis_combo_box)
        self.up_axis_label = qt_w.QLabel('up axis:')
        self.up_axis_combo_box = qt_w.QComboBox()
        for axes in self.x_axis:
            self.up_axis_combo_box.addItem(axes)
        self.color_swap('y', self.up_axis_combo_box)
        self.distance_label = qt_w.QLabel('Default control distance:')
        self.distance_label.setVisible(False)
        self.distance_value = qt_w.QLineEdit('1')
        self.distance_value.setValidator(self.float_validator)
        self.distance_value.setVisible(False)
        self.distance_button = qt_w.QPushButton('get')
        self.distance_button.setVisible(False)
        self.timeline_combo_box = qt_w.QComboBox()
        self.timeline_combo_box.addItem('Time range:')
        self.timeline_combo_box.addItem('Current timeline:')
        self.timeline_combo_box.addItem('Select time range:')
        font_metrics = self.timeline_combo_box.fontMetrics()
        if pyside_version == '2':
            text_width = font_metrics.width(self.timeline_combo_box.currentText()) + 30 * self.width_scale
            self.timeline_combo_box.setFixedWidth(int(text_width))
        elif pyside_version == '6':
            text_width = font_metrics.horizontalAdvance(self.timeline_combo_box.currentText()) + 30 * self.width_scale
            self.timeline_combo_box.setFixedWidth(int(text_width))
        self.timeline_start = qt_w.QLineEdit('start')
        self.timeline_start.setValidator(self.int_validator)
        self.timeline_end = qt_w.QLineEdit('end')
        self.timeline_end.setValidator(self.int_validator)
        self.strength_label = qt_w.QLabel('strength')
        self.strength_slider = qt_w.QSlider()
        self.strength_slider.setValue(100)
        self.strength_slider.setMinimum(-100)
        self.strength_slider.setMaximum(1000)
        self.strength_slider.setOrientation(qt_c.Qt.Horizontal)
        self.strength_value = qt_w.QLineEdit('1.0')
        self.strength_value.setValidator(self.float_validator)
        self.strength_value.setFixedWidth(int(30 * self.width_scale))
        self.stiffness_label = qt_w.QLabel('stiffness')
        self.stiffness_slider = qt_w.QSlider()
        self.stiffness_slider.setValue(50)
        self.stiffness_slider.setMinimum(0)
        self.stiffness_slider.setMaximum(100)
        self.stiffness_slider.setOrientation(qt_c.Qt.Horizontal)
        self.stiffness_value = qt_w.QLineEdit('0.5')
        self.stiffness_value.setValidator(self.float_validator)
        self.stiffness_value.setFixedWidth(int(30 * self.width_scale))
        self.zero_widget = qt_w.QLabel('bendy')
        self.zero_widget.setAlignment(qt_c.Qt.AlignCenter)
        self.zero_widget.setVisible(False)
        self.one_widget = qt_w.QLabel('stiff')
        self.one_widget.setAlignment(qt_c.Qt.AlignTop)
        self.one_widget.setVisible(False)
        self.start_widget = qt_w.QLabel('selection start')
        self.start_widget.setAlignment(qt_c.Qt.AlignLeft)
        self.start_widget.setVisible(False)
        self.spacer_widget = qt_w.QLabel('')
        self.spacer_widget.setVisible(False)
        self.spacer_widget.setMaximumWidth(int(38 * self.width_scale))
        self.end_widget = qt_w.QLabel('selection end')
        self.end_widget.setAlignment(qt_c.Qt.AlignRight)
        self.end_widget.setVisible(False)
        self.selected_position_label = qt_w.QLabel('position:')
        self.selected_position_label.setVisible(False)
        self.selected_position = qt_w.QLineEdit('0.0')
        self.selected_position.setValidator(self.float_validator_0_1)
        self.selected_position.setVisible(False)
        self.selected_value_label = qt_w.QLabel('value:')
        self.selected_value_label.setVisible(False)
        self.selected_value = qt_w.QLineEdit('1.0')
        self.selected_value.setValidator(self.float_validator_0_1)
        self.selected_value.setVisible(False)
        interps = ['None', 'Linear', 'Smooth', 'Spline']
        self.interpolation_label = qt_w.QLabel('interpolation:')
        self.interpolation_label.setVisible(False)
        self.interpolation_combo_box = qt_w.QComboBox()
        for interp in interps:
            self.interpolation_combo_box.addItem(interp)
        self.interpolation_combo_box.setCurrentIndex(2)
        self.interpolation_combo_box.setVisible(False)
        falloff_layout = self.create_falloff_curve_layout()
        self.falloff_widget = self.get_maya_layout_widget(falloff_layout)
        self.falloff_widget.setVisible(False)
        self.selection_label = qt_w.QLabel('order type:')
        self.selection_combo_box = qt_w.QComboBox()
        selection_types = ['selection', 'name', 'split by name']
        for sel_type in selection_types:
            self.selection_combo_box.addItem(sel_type)
        self.overshoot_strength_label = qt_w.QLabel('overshoot strength')
        self.overshoot_strength_label.setVisible(False)
        self.overshoot_strength_slider = qt_w.QSlider()
        self.overshoot_strength_slider.setValue(100)
        self.overshoot_strength_slider.setMinimum(1)
        self.overshoot_strength_slider.setMaximum(1000)
        self.overshoot_strength_slider.setOrientation(qt_c.Qt.Horizontal)
        self.overshoot_strength_slider.setVisible(False)
        self.overshoot_strength_value = qt_w.QLineEdit('1')
        self.overshoot_strength_value.setValidator(self.float_validator)
        self.overshoot_strength_value.setFixedWidth(int(30 * self.width_scale))
        self.overshoot_strength_value.setVisible(False)
        self.overshoot_frequency_lablel = qt_w.QLabel('oscillation number')
        self.overshoot_frequency_lablel.setVisible(False)
        self.overshoot_frequency_slider = qt_w.QSlider()
        self.overshoot_frequency_slider.setValue(3)
        self.overshoot_frequency_slider.setMinimum(1)
        self.overshoot_frequency_slider.setMaximum(20)
        self.overshoot_frequency_slider.setOrientation(qt_c.Qt.Horizontal)
        self.overshoot_frequency_slider.setVisible(False)
        self.overshoot_frequency_value = qt_w.QLineEdit('3')
        self.overshoot_frequency_value.setValidator(self.float_validator)
        self.overshoot_frequency_value.setFixedWidth(int(30 * self.width_scale))
        self.overshoot_frequency_value.setVisible(False)
        self.wind_strength_label = qt_w.QLabel('wind strength')
        self.wind_strength_label.setVisible(False)
        self.wind_strength_slider = qt_w.QSlider()
        self.wind_strength_slider.setValue(100)
        self.wind_strength_slider.setMinimum(1)
        self.wind_strength_slider.setMaximum(1000)
        self.wind_strength_slider.setOrientation(qt_c.Qt.Horizontal)
        self.wind_strength_slider.setVisible(False)
        self.wind_strength_value = qt_w.QLineEdit('1')
        self.wind_strength_value.setValidator(self.float_validator)
        self.wind_strength_value.setFixedWidth(int(30 * self.width_scale))
        self.wind_strength_value.setVisible(False)
        self.animation_label = qt_w.QLabel('keying type:')
        self.animation_combo_box = qt_w.QComboBox()
        animation_types = ['replacer', 'additive', 'delete all']
        for anim_type in animation_types:
            self.animation_combo_box.addItem(anim_type)
        self.parent_result = qt_w.QLineEdit('select a parent ')
        self.parent_result.setVisible(False)
        self.parent_result.setMaximumHeight(int(20 * self.height_scale))
        self.parent_button = qt_w.QPushButton('get')
        self.parent_button.setVisible(False)
        self.parent_button.setMaximumHeight(int(20 * self.height_scale))
        self.wind_button = qt_w.QPushButton('Create a wind control')
        self.error_label = qt_w.QLabel('')
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet('color:red')
        self.progress_bar = qt_w.QProgressBar()
        self.progress_bar.setMinimumWidth(int(260 * self.width_scale))
        self.progress_bar.setMinimum(0)
        self.progress_bar.setVisible(False)

    def set_tooltips(self):
        self.overshoot_menu.setToolTip('<b>Overshoot:</b> will activate the option to add overshoot to your overlap.\n<br><br> \n<b>Overshoot first controller:</b> will only apply the overshoot on the first\n control in the selection or the split. Best used for rotational overshoot.\n<br><br> \n<b>Overshoot in between:</b> will make the overshoot in between the animation\n in zones where the animation is stable.\n<br><br> \n<b>Overshoot at the end:</b> will make the overshoot happen at the end\n of the animation\n')
        self.layers_menu.setToolTip('<b>Bake to selected anim layer:</b> will bake the overlap on the currently selected layer\n<br>If you have no selected layers it will not bake to a layer\n<br>If you have 2 or more selected it will use the one the top most one.\n<br><br> \n<b>Bake to a new anim layer:</b> will create a new anim layer and bake the overlap on it.\n<br><br>\n<b>Additive layer:</b> will set the created layer to the additive mode when creating it.\n<br><br>\n<b>Override layer:</b> will set the created layer to the override mode when creating it. ')
        self.simulation_menu.setToolTip('<b>Wind:</b> will activate the wind simulation in the scene.\n<br>Make sure you have at least one wind control active in your scene\n<br><br>\n<b>Wind is absolute in translation:</b> will let you push a control\nin the world with the winds.\n<br><br>\n<b>Create wind control:</b> will create a custom wind control in the scene.\n<br>Make sure to use this button to create them and dont duplicate them or they\nwill not display properly.\n<br>Renaming them is fine it will not cause any issue.\n<br><br>\n<b>Select all wind controls:</b> will select all wind controls in the scene.\n<br><br>\n<b>Turn all wind controls off:</b> will turn off all wind controls in the scene.\n<br><br>\n<b>Turn all wind controls on:</b> will turn on all wind controls in the scene')
        self.other_menu.setToolTip('<b>Customize axes:</b> will let you choose on what axes the overlap will be applied\n<br><br>\n<b>Complex stiffness:</b> will change the stiffnes from a slider to a graph from\nthe start of your selection to the end of it\n<br><br>\n<b>Remove parent influence:</b> will let you select a transform in the scene and\n remove its transformation from the overlap calculation. \n<br><br>\n<b>Rotation overlap ignore its own translation:</b> using this option will make it\nso that when you create a rotational overlap it will not calculate it own translation\nanimation. Best to turn off in cases like of an ik that was translated and now that\ntranslation drive its own rotation.\n<br><br>\n<b>Default distance for rotation:</b> this option unlock a slider to set the default\ndistance between controls. The tool will normally look to the next control in \nyour selection for the distance and if you only choose one control it will look\nat the distance between the its parent or its child to find a distance. If the tool\ncannot find a distance it will set it to 1 by default but for larger rig its \nbetter to set the proper size or the rotation will be way too strong for the motion.\n<br><br>\n<b>Use only the default distance:</b> this option will make it so that the tool will\nonly use the default distance that you set previously for all rotation overlap\n<br><br>\n<b>Cycle animation</b>: This option will make it so that your overlap will loop in\nthe timerange that you have set. Make sure that the first frame and last frame have\nthe same position for perfect results')
        self.presets_menu.setToolTip('<b>Export a preset:</b> will let you export a preset of the current tool settings\n<br><br>\n<b>Import a preset:</b> will let you import a selected preset of the tool settings\n<br><br>\n<b>Partial Import a preset:</b> will let you choose wich options to import \nfrom a selected preset of the tool settings')
        self.axis_x_checkbox.setToolTip('Unchecking this will remove the x axis of the overlap')
        self.axis_y_checkbox.setToolTip('Unchecking this will remove the y axis of the overlap')
        self.axis_z_checkbox.setToolTip('Unchecking this will remove the z axis of the overlap')
        self.overlap_type.setToolTip('This will determine which overlap mode will be used')
        self.timeline_combo_box.setToolTip('This is your time range input the start and the end that you want')
        self.timeline_start.setToolTip('Start of the time range')
        self.timeline_end.setToolTip('End of the time range')
        self.main_axis_label.setToolTip('Please select what is the aim axis \nThe aim axis is the axis that points to your next controller ')
        self.main_axis_combo_box.setToolTip('Please select what is the aim axis \nThe aim axis is the axis that points to your next controller ')
        self.up_axis_label.setToolTip('Please select what is the up axis \nExample if you were to have y+ as your aim axis and your motion is mainly \n parallel the x axis you would set the up axis to either z+ or z-')
        self.up_axis_combo_box.setToolTip('Please select what is the up axis \nExample if you were to have y+ as your aim axis and your motion is mainly \n parallel the x axis you would set the up axis to either z+ or z-')
        self.translation_strength_label.setToolTip('This value will change how many frame the translation will lag behind')
        self.translation_strength_slider.setToolTip('This value will change how many frame the translation will lag behind')
        self.translation_strength_value.setToolTip('This value will change how many frame the translation will lag behind')
        self.strength_label.setToolTip('This value will change by how much the value will be multiplied\nafter the main calculation \nIf you set it to -1 it will inverse your overlap')
        self.strength_slider.setToolTip('This value will change by how much the value will be multiplied\nafter the main calculation\nIf you set it to -1 it will inverse your overlap')
        self.stiffness_value.setToolTip('This value will change by how much the value will be multiplied\nafter the main calculation\nIf you set it to -1 it will inverse your overlap')
        self.stiffness_label.setToolTip('This value will change the stiffness of the overlap.\n0 will be soft as overcooked pasta and 1 will hard as stone')
        self.stiffness_slider.setToolTip('This value will change the stiffness of the overlap.\n0 will be soft as overcooked pasta and 1 will hard as stone')
        self.stiffness_value.setToolTip('This value will change the stiffness of the overlap.\n0 will be soft as overcooked pasta and 1 will hard as stone')
        self.selected_position_label.setToolTip('This value will determine the position of the point across the selection')
        self.selected_position.setToolTip('This value will determine the position of the point across the selection')
        self.selected_value_label.setToolTip('This value will determine the stiffness of the selection at that point')
        self.selected_value.setToolTip('This value will determine the stiffness of the selection at that point')
        self.interpolation_label.setToolTip('This will determine the interpolation between\nthe current point and the next one')
        self.interpolation_combo_box.setToolTip('This will determine the interpolation between\nthe current point and the next one')
        self.overshoot_strength_slider.setToolTip('This will multiply the strength of the overshoot at the end of the anim')
        self.overshoot_strength_value.setToolTip('This will multiply the strength of the overshoot at the end of the anim')
        self.overshoot_frequency_slider.setToolTip('This will the frequency of the overshoot at the end of the anim')
        self.overshoot_frequency_value.setToolTip('This will the frequency of the overshoot at the end of the anim')
        self.wind_strength_slider.setToolTip('This will multiply the value for all the winds')
        self.wind_strength_value.setToolTip('This will multiply the value for all the winds')
        self.selection_combo_box.setToolTip('<b>Selection:</b> will just be the order in which you selected your controls\n<br><br>\n<b>Name:</b> will order your selection by \n<br><br>\n<b>Split by name:</b> will split controllers in group by their name\n<br>\nExtremely useful if you are using complex stiffness\n<br>\nExample [banana_1,banana_2], [apple_1,apple_2]\n<br>\n<b>!!WARNING!!</b>will only split if you have numbers in your names')
        self.animation_combo_box.setToolTip('<b></b>This will determine how the keys are created\n<br>\nAnd if you are in a layer it will only affect that layer\n<br><br>\n<b>Replacer:</b> will replace the keys in time range you have selected\n<br><br>\n<b>Add:</b> will add key to the time range you have selected and keep the offset\n<br><br>\n<b>Delete:</b> all will delete all key for that controller ')
        self.parent_result.setToolTip('This parent transforms will be removed from the calculation of the overlap')
        self.parent_button.setToolTip('Press this button while having the parent that you want to remove selected')
        self.basic_button.setToolTip('Press this button and the overlap will be created')

    def create_separator(self, target_layout):
        separator = qt_w.QFrame()
        separator.setFrameShape(qt_w.QFrame.HLine)
        separator.setFixedHeight(1)
        target_layout.addWidget(separator)
        return separator

    def create_palette(self, target_layout, r, g, b):
        separator = qt_w.QFrame()
        separator.setFrameShape(qt_w.QFrame.VLine)
        separator.setLineWidth(int(10 * self.width_scale))
        separator.setStyleSheet('background-color: rgb({}, {}, {})'.format(r, g, b))
        target_layout.addWidget(separator)
        return separator

    def create_v_separator(self, target_layout):
        separator = qt_w.QFrame()
        separator.setFrameShape(qt_w.QFrame.VLine)
        separator.setFixedWidth(1)
        target_layout.addWidget(separator)
        return separator

    def connect_ui(self):
        self.main_axis_combo_box.currentIndexChanged.connect(self.main_axis_changed)
        self.up_axis_combo_box.currentIndexChanged.connect(self.up_axis_changed)
        self.stiffness_slider.valueChanged.connect(self.stiffness_changed)
        self.stiffness_value.textEdited.connect(self.stiffness_value_changed)
        self.translation_strength_slider.valueChanged.connect(self.translation_strength_changed)
        self.translation_strength_value.textEdited.connect(self.translation_strength_value_changed)
        self.strength_slider.valueChanged.connect(self.strength_changed)
        self.strength_value.textEdited.connect(self.strength_value_changed)
        self.overshoot_strength_slider.valueChanged.connect(self.overshoot_strength_changed)
        self.overshoot_strength_value.textEdited.connect(self.overshoot_strength_value_changed)
        self.overshoot_frequency_slider.valueChanged.connect(self.overshoot_frequency_changed)
        self.overshoot_frequency_value.textEdited.connect(self.overshoot_frequency_value_changed)
        self.wind_strength_slider.valueChanged.connect(self.wind_strength_changed)
        self.wind_strength_value.textEdited.connect(self.wind_value_changed)
        self.basic_button.clicked.connect(self.overlap)
        self.distance_button.clicked.connect(self.get_distances)
        self.selected_position.textChanged.connect(self.position_changed)
        self.selected_value.textChanged.connect(self.value_changed)
        self.interpolation_combo_box.currentIndexChanged.connect(self.interp_changed)
        self.overlap_type.currentIndexChanged.connect(self.stiffness_type_changed)
        self.timeline_combo_box.currentIndexChanged.connect(self.timeline_type_changed)
        self.parent_option.triggered.connect(self.parent_checked)
        self.stiffness_option.triggered.connect(self.stiffness_type_changed)
        self.axes_option.triggered.connect(self.select_axes_changed)
        self.default_distance_option.triggered.connect(self.default_distance_checked)
        self.overshoot_option.triggered.connect(self.overshoot_checked)
        self.overshoot_end_option.triggered.connect(self.overshoot_end_checked)
        self.overshoot_between_option.triggered.connect(self.overshoot_between_checked)
        self.wind_option.triggered.connect(self.wind_checked)
        self.wind_control_option.triggered.connect(self.create_wind_control)
        self.wind_select_option.triggered.connect(self.select_wind_controls)
        self.wind_off_option.triggered.connect(self.wind_controls_off)
        self.wind_on_option.triggered.connect(self.wind_controls_on)
        self.add_to_layer_option.triggered.connect(self.add_layer_option_checked)
        self.create_layer_option.triggered.connect(self.create_layer_option_checked)
        self.additive_layer.triggered.connect(self.additive_checked)
        self.override_layer.triggered.connect(self.override_checked)
        self.export_option.triggered.connect(self.write_ui_data)
        self.partial_import_option.triggered.connect(self.partial_import_overlap_preset)
        self.import_option.triggered.connect(self.import_overlap_preset)
        self.parent_button.clicked.connect(self.get_parent)

    def wind_checked(self):
        wind_validator = self.wind_option.isChecked()
        if wind_validator:
            self.wind_height = int(30 * self.height_scale)
            self.wind_palette.setVisible(True)
            self.wind_strength_label.setVisible(True)
            self.wind_strength_slider.setVisible(True)
            self.wind_strength_value.setVisible(True)
            self.wind_separator.setVisible(True)
            if self.overlap_button_text == 'overlap':
                self.overlap_button_text = 'overlap and simulate wind'
                self.basic_button.setText(self.overlap_button_text)
            elif self.overlap_button_text == 'overlap and overshoot':
                self.overlap_button_text = 'overlap, overshoot and simulate wind'
                self.basic_button.setText(self.overlap_button_text)
            self.stiffness_type_changed()
        else:
            self.wind_height = 0
            self.wind_palette.setVisible(False)
            self.wind_strength_label.setVisible(False)
            self.wind_strength_slider.setVisible(False)
            self.wind_strength_value.setVisible(False)
            self.wind_separator.setVisible(False)
            if self.overlap_button_text == 'overlap and simulate wind':
                self.overlap_button_text = 'overlap'
                self.basic_button.setText(self.overlap_button_text)
            elif self.overlap_button_text == 'overlap, overshoot and simulate wind':
                self.overlap_button_text = 'overlap and overshoot'
                self.basic_button.setText(self.overlap_button_text)
            self.stiffness_type_changed()

    def overshoot_checked(self):
        overshoot_check = self.overshoot_option.isChecked()
        if overshoot_check:
            self.overshoot_palette_1.setVisible(True)
            self.overshoot_palette_2.setVisible(True)
            self.overshoot_separator_1.setVisible(True)
            self.overshoot_separator_2.setVisible(True)
            self.overshoot_strength_label.setVisible(True)
            self.overshoot_strength_slider.setVisible(True)
            self.overshoot_strength_value.setVisible(True)
            self.overshoot_frequency_lablel.setVisible(True)
            self.overshoot_frequency_slider.setVisible(True)
            self.overshoot_frequency_value.setVisible(True)
            self.overshoot_height = int(70 * self.height_scale)
            self.stiffness_type_changed()
            if self.overlap_button_text == 'overlap':
                self.overlap_button_text = 'overlap and overshoot'
                self.basic_button.setText(self.overlap_button_text)
            elif self.overlap_button_text == 'overlap and simulate wind':
                self.overlap_button_text = 'overlap, overshoot and simulate wind'
                self.basic_button.setText(self.overlap_button_text)
        else:
            self.overshoot_palette_1.setVisible(False)
            self.overshoot_palette_2.setVisible(False)
            self.overshoot_separator_1.setVisible(False)
            self.overshoot_separator_2.setVisible(False)
            self.overshoot_strength_label.setVisible(False)
            self.overshoot_strength_slider.setVisible(False)
            self.overshoot_strength_value.setVisible(False)
            self.overshoot_frequency_lablel.setVisible(False)
            self.overshoot_frequency_slider.setVisible(False)
            self.overshoot_frequency_value.setVisible(False)
            if self.overlap_button_text == 'overlap and overshoot':
                self.overlap_button_text = 'overlap'
                self.basic_button.setText(self.overlap_button_text)
            elif self.overlap_button_text == 'overlap, overshoot and simulate wind':
                self.overlap_button_text = 'overlap and simulate wind'
                self.basic_button.setText(self.overlap_button_text)
            self.overshoot_height = 0
            self.stiffness_type_changed()

    def overshoot_end_checked(self):
        overshoot_end_check = self.overshoot_end_option.isChecked()
        overshoot_between_check = self.overshoot_between_option.isChecked()
        if not overshoot_end_check and (not overshoot_between_check):
            self.overshoot_between_option.setChecked(True)

    def overshoot_between_checked(self):
        overshoot_end_check = self.overshoot_end_option.isChecked()
        overshoot_between_check = self.overshoot_between_option.isChecked()
        if not overshoot_end_check and (not overshoot_between_check):
            self.overshoot_end_option.setChecked(True)

    def override_checked(self):
        override_check = self.override_layer.isChecked()
        if override_check:
            self.additive_layer.setChecked(False)
        else:
            self.additive_layer.setChecked(True)

    def additive_checked(self):
        override_check = self.additive_layer.isChecked()
        if override_check:
            self.override_layer.setChecked(False)
        else:
            self.override_layer.setChecked(True)

    def parent_checked(self):
        check = self.parent_option.isChecked()
        if check:
            self.parent_result.setVisible(True)
            self.parent_button.setVisible(True)
            self.parent_separator.setVisible(True)
            self.parent_height_value = int(45 * self.height_scale)
            self.stiffness_type_changed()
        else:
            self.parent_result.setVisible(False)
            self.parent_button.setVisible(False)
            self.parent_separator.setVisible(False)
            self.parent_height_value = 0
            self.stiffness_type_changed()

    def default_distance_checked(self):
        rotation_check = self.overlap_type.currentIndex()
        check = self.default_distance_option.isChecked()
        if rotation_check == 0:
            if check:
                self.distance_palette.setVisible(True)
                self.distance_label.setVisible(True)
                self.distance_value.setVisible(True)
                self.distance_button.setVisible(True)
                self.distance_separator.setVisible(True)
                self.distance_height_value = 45
                self.stiffness_type_changed()
            else:
                self.distance_palette.setVisible(False)
                self.distance_label.setVisible(False)
                self.distance_value.setVisible(False)
                self.distance_button.setVisible(False)
                self.distance_separator.setVisible(False)
                self.distance_height_value = 0
                self.stiffness_type_changed()

    def add_layer_option_checked(self):
        current_check = self.add_to_layer_option.isChecked()
        if current_check == 0:
            pass
        else:
            self.create_layer_option.setChecked(False)

    def create_layer_option_checked(self):
        current_check = self.create_layer_option.isChecked()
        if current_check == 0:
            pass
        else:
            self.add_to_layer_option.setChecked(False)

    def select_axes_changed(self):
        current_id = self.axes_option.isChecked()
        if current_id == False:
            self.axes_spacer.setVisible(True)
            self.axis_x_checkbox.setVisible(False)
            self.axis_y_checkbox.setVisible(False)
            self.axis_z_checkbox.setVisible(False)
            self.axes_height = 0
        elif current_id == True:
            self.axes_spacer.setVisible(False)
            self.axis_x_checkbox.setVisible(True)
            self.axis_y_checkbox.setVisible(True)
            self.axis_z_checkbox.setVisible(True)
            self.axes_height = 0
        self.stiffness_type_changed()

    def stiffness_type_changed(self):
        current_id = self.stiffness_option.isChecked()
        size = self.start_height - self.timeline_height_value + self.parent_height_value + self.error_height + self.axes_height + self.wind_height + self.overshoot_height + self.distance_height_value
        if current_id == 0:
            self.stiffness_complex_palette_1.setVisible(False)
            self.stiffness_complex_palette_2.setVisible(False)
            self.stiffness_complex_palette_3.setVisible(False)
            self.zero_widget.setVisible(False)
            self.one_widget.setVisible(False)
            self.start_widget.setVisible(False)
            self.spacer_widget.setVisible(False)
            self.end_widget.setVisible(False)
            self.selected_position_label.setVisible(False)
            self.selected_position.setVisible(False)
            self.selected_value_label.setVisible(False)
            self.selected_value.setVisible(False)
            self.interpolation_label.setVisible(False)
            self.interpolation_combo_box.setVisible(False)
            try:
                self.falloff_widget.setVisible(False)
                self.falloff_widget.setVisible(False)
            except RuntimeError:
                pass
            self.stiffness_separator.setVisible(False)
            self.stiffness_palette.setVisible(True)
            self.stiffness_label.setVisible(True)
            self.stiffness_slider.setVisible(True)
            self.stiffness_value.setVisible(True)
            self.overlap_changed(size)
        elif current_id == 1:
            try:
                self.falloff_widget.setVisible(True)
            except RuntimeError:
                falloff_layout = self.create_falloff_curve_layout()
                self.falloff_widget = self.get_maya_layout_widget(falloff_layout)
                self.falloff_layout_h_1.addWidget(self.falloff_widget)
            self.stiffness_complex_palette_1.setVisible(True)
            self.stiffness_complex_palette_2.setVisible(True)
            self.stiffness_complex_palette_3.setVisible(True)
            self.zero_widget.setVisible(True)
            self.one_widget.setVisible(True)
            self.start_widget.setVisible(True)
            self.spacer_widget.setVisible(True)
            self.end_widget.setVisible(True)
            self.selected_position_label.setVisible(True)
            self.selected_position.setVisible(True)
            self.selected_value_label.setVisible(True)
            self.selected_value.setVisible(True)
            self.interpolation_label.setVisible(True)
            self.interpolation_combo_box.setVisible(True)
            self.stiffness_separator.setVisible(True)
            self.stiffness_palette.setVisible(False)
            self.stiffness_label.setVisible(False)
            self.stiffness_slider.setVisible(False)
            self.stiffness_value.setVisible(False)
            size = size + 165
            self.overlap_changed(size)

    def overlap_changed(self, size):
        current_id = self.overlap_type.currentIndex()
        distance_check = self.default_distance_option.isChecked()
        if current_id == 0:
            self.overlap_type_palette.setStyleSheet('background-color: rgb({}, {}, {})'.format(255, 255, 0))
            self.translation_palette.setVisible(False)
            self.translation_strength_label.setVisible(False)
            self.translation_strength_slider.setVisible(False)
            self.translation_strength_value.setVisible(False)
            if distance_check:
                self.distance_palette.setVisible(True)
                self.distance_label.setVisible(True)
                self.distance_value.setVisible(True)
                self.distance_button.setVisible(True)
                self.distance_separator.setVisible(True)
                if self.distance_height_value == 0:
                    self.distance_height_value = int(45 * self.height_scale)
                    size = size + self.distance_height_value
            else:
                self.distance_palette.setVisible(False)
                self.distance_label.setVisible(False)
                self.distance_value.setVisible(False)
                self.distance_button.setVisible(False)
                self.distance_separator.setVisible(False)
                if self.distance_height_value == 45:
                    self.distance_height_value = 0
                    size = int(size - 45 * self.height_scale)
            self.axes_palette.setVisible(True)
            self.main_axis_label.setVisible(True)
            self.main_axis_combo_box.setVisible(True)
            self.up_axis_combo_box.setVisible(True)
            self.up_axis_label.setVisible(True)
            self.resize(self.width_value, size)
        elif current_id == 1:
            self.overlap_type_palette.setStyleSheet('background-color: rgb({}, {}, {})'.format(0, 255, 255))
            self.translation_palette.setVisible(True)
            self.translation_strength_label.setVisible(True)
            self.translation_strength_slider.setVisible(True)
            self.translation_strength_value.setVisible(True)
            self.distance_palette.setVisible(False)
            self.distance_label.setVisible(False)
            self.distance_value.setVisible(False)
            self.distance_button.setVisible(False)
            self.distance_separator.setVisible(False)
            self.distance_height_value = 0
            self.axes_palette.setVisible(False)
            self.main_axis_label.setVisible(False)
            self.main_axis_combo_box.setVisible(False)
            self.up_axis_combo_box.setVisible(False)
            self.up_axis_label.setVisible(False)
            self.resize(self.width_value, size)

    def get_distances(self):
        distance = over_p.get_distance_between_object()
        self.distance_value.setText(str(distance))

    def timeline_type_changed(self):
        current_time_type = self.timeline_combo_box.currentIndex()
        if current_time_type == 0:
            self.timeline_start.setVisible(True)
            self.timeline_end.setVisible(True)
            font_metrics = self.timeline_combo_box.fontMetrics()
            if pyside_version == '2':
                text_width = font_metrics.width(self.timeline_combo_box.currentText()) + 30 * self.width_scale
                self.timeline_combo_box.setFixedWidth(int(text_width))
            elif pyside_version == '6':
                text_width = font_metrics.horizontalAdvance(self.timeline_combo_box.currentText()) + 30 * self.width_scale
                self.timeline_combo_box.setFixedWidth(int(text_width))
            self.stiffness_type_changed()
        else:
            font_metrics = self.timeline_combo_box.fontMetrics()
            if pyside_version == '2':
                text_width = font_metrics.width(self.timeline_combo_box.currentText()) + 30 * self.width_scale
                self.timeline_combo_box.setFixedWidth(int(text_width))
            elif pyside_version == '6':
                text_width = font_metrics.horizontalAdvance(self.timeline_combo_box.currentText()) + 30 * self.width_scale
                self.timeline_combo_box.setFixedWidth(int(text_width))
            self.timeline_start.setVisible(False)
            self.timeline_end.setVisible(False)
            self.stiffness_type_changed()

    def point_changed(self):
        current_key = mc.gradientControlNoAttr(self.falloff_curve, q=True, ck=True)
        test = mc.gradientControlNoAttr(self.falloff_curve, q=True, asString=True)
        points_range = test.split(',')
        size = int(len(points_range) / 3)
        points = []
        for x in range(size):
            if x == current_key:
                val = int(x) * 3
                self.selected_position.setText(points_range[val + 1])
                self.selected_value.setText(points_range[val])
                self.interpolation_combo_box.setCurrentIndex(int(points_range[val + 2]))

    def position_changed(self):
        current_val = mc.gradientControlNoAttr(self.falloff_curve, q=True, asString=True)
        current_val_split = current_val.split(',')
        current_key = mc.gradientControlNoAttr(self.falloff_curve, q=True, ck=True)
        current_pos = current_val_split[current_key * 3 + 1]
        if current_pos == self.selected_position.text():
            return
        current_val_split[current_key * 3 + 1] = self.selected_position.text()
        result = ''
        for x, val in enumerate(current_val_split):
            if x == 0:
                result = '{}'.format(val)
            else:
                result = '{},{}'.format(result, val)
        mc.gradientControlNoAttr(self.falloff_curve, e=True, asString=result)

    def value_changed(self):
        current_val = mc.gradientControlNoAttr(self.falloff_curve, q=True, asString=True)
        current_val_split = current_val.split(',')
        current_key = mc.gradientControlNoAttr(self.falloff_curve, q=True, ck=True)
        current_pos = current_val_split[current_key * 3]
        if current_pos == self.selected_value.text():
            return
        current_val_split[current_key * 3] = self.selected_value.text()
        result = ''
        for x, val in enumerate(current_val_split):
            if x == 0:
                result = '{}'.format(val)
            else:
                result = '{},{}'.format(result, val)
        mc.gradientControlNoAttr(self.falloff_curve, e=True, asString=result)

    def interp_changed(self):
        current_val = mc.gradientControlNoAttr(self.falloff_curve, q=True, asString=True)
        current_val_split = current_val.split(',')
        current_key = mc.gradientControlNoAttr(self.falloff_curve, q=True, ck=True)
        current_pos = current_val_split[current_key * 3 + 2]
        if current_pos == self.interpolation_combo_box.currentIndex():
            return
        current_val_split[current_key * 3 + 2] = self.interpolation_combo_box.currentIndex()
        result = ''
        for x, val in enumerate(current_val_split):
            if x == 0:
                result = '{}'.format(val)
            else:
                result = '{},{}'.format(result, val)
        mc.gradientControlNoAttr(self.falloff_curve, e=True, asString=result)

    def wind_strength_changed(self):
        val = self.wind_strength_slider.value()
        val = str(float(val) * 0.01)[0:4]
        self.wind_strength_value.setText(val)

    def wind_value_changed(self):
        try:
            val = self.wind_strength_value.text()
            val = int(float(val) / 0.01)
            old = self.wind_strength_slider.blockSignals(True)
            try:
                self.wind_strength_slider.setValue(val)
            finally:
                self.wind_strength_slider.blockSignals(old)
        except ValueError:
            pass

    def stiffness_changed(self):
        val = self.stiffness_slider.value()
        val = str(float(val) * 0.01)[0:4]
        self.stiffness_value.setText(val)

    def stiffness_value_changed(self):
        try:
            val = self.stiffness_value.text()
            val = int(float(val) / 0.01)
            old = self.stiffness_slider.blockSignals(True)
            try:
                self.stiffness_slider.setValue(val)
            finally:
                self.stiffness_slider.blockSignals(old)
        except ValueError:
            pass

    def translation_strength_changed(self):
        val = self.translation_strength_slider.value()
        val = str(float(val) * 0.01)[0:4]
        self.translation_strength_value.setText(val)

    def translation_strength_value_changed(self):
        try:
            val = self.translation_strength_value.text()
            val = int(float(val) / 0.01)
            old = self.translation_strength_slider.blockSignals(True)
            try:
                self.translation_strength_slider.setValue(val)
            finally:
                self.translation_strength_slider.blockSignals(old)
        except ValueError:
            pass

    def strength_changed(self):
        val = self.strength_slider.value()
        val = str(float(val) / 100)
        self.strength_value.setText(val)

    def strength_value_changed(self):
        try:
            val = self.strength_value.text()
            val = int(float(val) * 100)
            old = self.strength_slider.blockSignals(True)
            try:
                self.strength_slider.setValue(val)
            finally:
                self.strength_slider.blockSignals(old)
        except ValueError:
            pass

    def overshoot_strength_changed(self):
        val = self.overshoot_strength_slider.value()
        val = str(float(val) / 100)
        self.overshoot_strength_value.setText(val)

    def overshoot_strength_value_changed(self):
        try:
            val = self.overshoot_strength_value.text()
            val = int(float(val) * 100)
            old = self.overshoot_strength_slider.blockSignals(True)
            try:
                self.overshoot_strength_slider.setValue(val)
            finally:
                self.overshoot_strength_slider.blockSignals(old)
        except ValueError:
            pass

    def overshoot_frequency_changed(self):
        val = self.overshoot_frequency_slider.value()
        val = str(val)
        self.overshoot_frequency_value.setText(val)

    def overshoot_frequency_value_changed(self):
        try:
            val = self.overshoot_frequency_value.text()
            val = int(val)
            old = self.overshoot_frequency_slider.blockSignals(True)
            try:
                self.overshoot_frequency_slider.setValue(val)
            finally:
                self.overshoot_frequency_slider.blockSignals(old)
        except ValueError:
            pass

    def up_axis_changed(self):
        current_id = self.up_axis_combo_box.currentText()
        try:
            self.color_swap(str(current_id[0]), self.up_axis_combo_box)
        except:
            pass

    def main_axis_changed(self):
        current_id = self.main_axis_combo_box.currentIndex()
        if current_id == 0 or current_id == 1:
            self.color_swap('x', self.main_axis_combo_box)
            self.color_swap('y', self.up_axis_combo_box)
            for temp in range(4):
                self.up_axis_combo_box.removeItem(0)
            for axis in self.x_axis:
                self.up_axis_combo_box.addItem(axis)
        if current_id == 2 or current_id == 3:
            self.color_swap('y', self.main_axis_combo_box)
            self.color_swap('x', self.up_axis_combo_box)
            for temp in range(4):
                self.up_axis_combo_box.removeItem(0)
            for axis in self.y_axis:
                self.up_axis_combo_box.addItem(axis)
        if current_id == 4 or current_id == 5:
            self.color_swap('z', self.main_axis_combo_box)
            self.color_swap('x', self.up_axis_combo_box)
            for temp in range(4):
                self.up_axis_combo_box.removeItem(0)
            for axis in self.z_axis:
                self.up_axis_combo_box.addItem(axis)

    def color_swap(self, axis, target):
        if axis == 'x':
            target.setStyleSheet('color:red; font:bold')
        if axis == 'y':
            target.setStyleSheet('color:lime; font:bold')
        if axis == 'z':
            target.setStyleSheet('color:blue; font:bold')

    def create_falloff_curve_layout(self):
        if mc.window('mtkOverslapperCandidateGradientWindow', exists=True):
            mc.deleteUI('mtkOverslapperCandidateGradientWindow', window=True)
        window = mc.window('mtkOverslapperCandidateGradientWindow')
        layout = mc.columnLayout()
        self.falloff_curve = mc.gradientControlNoAttr(w=220, h=110, p=layout, ov=self.custom_var, dc=lambda *args: self.point_changed())
        return layout

    def get_maya_layout_widget(self, layout_name):
        layout_ptr = omui.MQtUtil.findLayout(layout_name)
        layout_widget = wrapInstance(int(layout_ptr), qt_w.QWidget)
        layout_widget.setAttribute(qt_c.Qt.WA_AcceptTouchEvents)
        return layout_widget

    def create_wind_control(self):
        return bridge.action(self, 'create_wind')

    def select_wind_controls(self):
        return bridge.action(self, 'select_winds')

    def wind_controls_off(self):
        return bridge.action(self, 'set_winds', enabled=False)

    def wind_controls_on(self):
        return bridge.action(self, 'set_winds', enabled=True)

    def import_overlap_preset(self):
        try:
            file_dialog = qt_w.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, 'Import Preset', script_path, 'JSON Files (*.json)')
            if file_path:
                self.preset_file = file_path
                self.import_ui_data(True, True, True, True, True, True, True, True)
        except Exception as error:
            return bridge.import_error(self, error)

    def partial_import_overlap_preset(self):
        try:
            file_dialog = qt_w.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, 'Import Preset', script_path, 'JSON Files (*.json)')
            if file_path:
                self.preset_file = file_path
                partial_import_ui = partialImportDialog(self)
                partial_import_ui.data_sent.connect(self.import_ui_data)
                partial_import_ui.exec()
        except Exception as error:
            return bridge.import_error(self, error)

    def import_ui_data(self, overlap_type, base_overlap, order_key, complex_attribute, anim_layers, overshoot, wind, bonus):
        try:
            ui_data = bridge.read_preset(self.preset_file)
            if overlap_type:
                self.overlap_type.setCurrentIndex(ui_data['overlap_type'])
            if base_overlap:
                self.timeline_combo_box.setCurrentIndex(ui_data['base_overlap']['time_type'])
                self.timeline_start.setText(ui_data['base_overlap']['start_time'])
                self.timeline_end.setText(ui_data['base_overlap']['end_time'])
                self.main_axis_combo_box.setCurrentIndex(ui_data['base_overlap']['main_axis'])
                self.up_axis_combo_box.setCurrentIndex(ui_data['base_overlap']['up_axis'])
                self.strength_value.setText(ui_data['base_overlap']['strength'])
                self.stiffness_value.setText(ui_data['base_overlap']['stifness'])
                self.translation_strength_value_changed()
                self.strength_value_changed()
                self.stiffness_value_changed()
            if order_key:
                self.selection_combo_box.setCurrentIndex(ui_data['order_key_type']['order'])
                self.animation_combo_box.setCurrentIndex(ui_data['order_key_type']['key_type'])
            if complex_attribute:
                self.stiffness_option.setChecked(ui_data['complex_stiffness']['option'])
                vals = ''
                mc.optionVar(rm=self.custom_var)
                for x, curve_point in enumerate(ui_data['complex_stiffness']['curve']):
                    curve_point = str(curve_point)
                    mc.optionVar(sva=[self.custom_var, '{}'.format(curve_point)])
                    if x == 0:
                        vals = '{}'.format(curve_point)
                    else:
                        vals = '{},{}'.format(vals, curve_point)
                mc.gradientControlNoAttr(self.falloff_curve, e=True, asString=vals)
                self.stiffness_type_changed()
            if anim_layers:
                self.add_to_layer_option.setChecked(ui_data['anim_layers']['bake_selected'])
                self.create_layer_option.setChecked(ui_data['anim_layers']['bake_new'])
                self.additive_layer.setChecked(ui_data['anim_layers']['additive'])
                self.override_layer.setChecked(ui_data['anim_layers']['override'])
            if overshoot:
                self.overshoot_option.setChecked(ui_data['overshoot']['option'])
                self.overshoot_first_option.setChecked(ui_data['overshoot']['first'])
                self.overshoot_between_option.setChecked(ui_data['overshoot']['between'])
                self.overshoot_end_option.setChecked(ui_data['overshoot']['end'])
                self.overshoot_strength_value.setText(ui_data['overshoot']['strength'])
                self.overshoot_frequency_value.setText(ui_data['overshoot']['frequency'])
                self.overshoot_checked()
                self.overshoot_strength_value_changed()
                self.overshoot_frequency_value_changed()
            if wind:
                self.wind_option.setChecked(ui_data['wind']['option'])
                self.wind_absolute_option.setChecked(ui_data['wind']['absolute'])
                self.wind_checked()
                self.wind_value_changed()
            if bonus:
                self.axes_option.setChecked(ui_data['bonus']['axis_option'])
                self.axis_x_checkbox.setChecked(ui_data['bonus']['x_axis'])
                self.axis_y_checkbox.setChecked(ui_data['bonus']['y_axis'])
                self.axis_z_checkbox.setChecked(ui_data['bonus']['z_axis'])
                self.parent_option.setChecked(ui_data['bonus']['remove_option'])
                self.parent_result.setText(ui_data['bonus']['parent'])
                self.rotation_translation_option.setChecked(ui_data['bonus']['ignore'])
                self.default_distance_option.setChecked(ui_data['bonus']['distance_option'])
                self.default_distance_only_option.setChecked(ui_data['bonus']['distance_only'])
                self.distance_value.setText(ui_data['bonus']['distance'])
                if 'cycle' in ui_data['bonus']:
                    self.cycle_option.setChecked(ui_data['bonus']['cycle'])
                else:
                    self.cycle_option.setChecked(False)
                self.parent_checked()
                self.select_axes_changed()
                self.stiffness_changed()
            if base_overlap:
                self.translation_strength_value.setText(ui_data['base_overlap'].get('frame_lag', '1.0'))
                self.translation_strength_value_changed()
            if wind:
                self.wind_strength_value.setText(ui_data['wind'].get('strength', '1.0'))
                self.wind_value_changed()
        except Exception as error:
            return bridge.import_error(self, error)

    def write_ui_data(self):
        ui_data = {}
        ui_data['overlap_type'] = self.overlap_type.currentIndex()
        ui_data['base_overlap'] = {}
        ui_data['base_overlap']['time_type'] = self.timeline_combo_box.currentIndex()
        ui_data['base_overlap']['start_time'] = self.timeline_start.text()
        ui_data['base_overlap']['end_time'] = self.timeline_end.text()
        ui_data['base_overlap']['main_axis'] = self.main_axis_combo_box.currentIndex()
        ui_data['base_overlap']['up_axis'] = self.up_axis_combo_box.currentIndex()
        ui_data['base_overlap']['strength'] = self.strength_value.text()
        ui_data['base_overlap']['stifness'] = self.stiffness_value.text()
        ui_data['order_key_type'] = {}
        ui_data['order_key_type']['order'] = self.selection_combo_box.currentIndex()
        ui_data['order_key_type']['key_type'] = self.animation_combo_box.currentIndex()
        ui_data['complex_stiffness'] = {}
        ui_data['complex_stiffness']['option'] = self.stiffness_option.isChecked()
        ui_data['complex_stiffness']['curve'] = mc.optionVar(q=self.custom_var)
        ui_data['anim_layers'] = {}
        ui_data['anim_layers']['bake_selected'] = self.add_to_layer_option.isChecked()
        ui_data['anim_layers']['bake_new'] = self.create_layer_option.isChecked()
        ui_data['anim_layers']['additive'] = self.additive_layer.isChecked()
        ui_data['anim_layers']['override'] = self.override_layer.isChecked()
        ui_data['overshoot'] = {}
        ui_data['overshoot']['option'] = self.overshoot_option.isChecked()
        ui_data['overshoot']['first'] = self.overshoot_first_option.isChecked()
        ui_data['overshoot']['between'] = self.overshoot_between_option.isChecked()
        ui_data['overshoot']['end'] = self.overshoot_end_option.isChecked()
        ui_data['overshoot']['strength'] = self.overshoot_strength_value.text()
        ui_data['overshoot']['frequency'] = self.overshoot_frequency_value.text()
        ui_data['wind'] = {}
        ui_data['wind']['option'] = self.wind_option.isChecked()
        ui_data['wind']['absolute'] = self.wind_absolute_option.isChecked()
        ui_data['bonus'] = {}
        ui_data['bonus']['axis_option'] = self.axes_option.isChecked()
        ui_data['bonus']['x_axis'] = self.axis_x_checkbox.isChecked()
        ui_data['bonus']['y_axis'] = self.axis_y_checkbox.isChecked()
        ui_data['bonus']['z_axis'] = self.axis_z_checkbox.isChecked()
        ui_data['bonus']['remove_option'] = self.parent_option.isChecked()
        ui_data['bonus']['parent'] = self.parent_result.text()
        ui_data['bonus']['ignore'] = self.rotation_translation_option.isChecked()
        ui_data['bonus']['distance_option'] = self.default_distance_option.isChecked()
        ui_data['bonus']['distance_only'] = self.default_distance_only_option.isChecked()
        ui_data['bonus']['distance'] = self.distance_value.text()
        ui_data['bonus']['cycle'] = self.cycle_option.isChecked()
        ui_data['base_overlap']['frame_lag'] = self.translation_strength_value.text()
        ui_data['wind']['strength'] = self.wind_strength_value.text()
        return bridge.write_preset(self, ui_data)

    def error_ui(self, error_type, extra):
        self.error_height = int(30 * self.height_scale)
        self.stiffness_type_changed()
        self.error_label.setStyleSheet('color:red')
        self.error_label.setMinimumWidth(200)
        if error_type == 'startTime':
            text = 'Please input a value in the start of the time range'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'endTime':
            text = 'Please input a value in the end of the time range'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'end<start':
            text = 'The end value cant be smaller than the start value'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'end=start':
            text = 'The start value cant be equal to the end value'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'noSelection':
            text = 'you need to select something'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'falseParent':
            text = 'Please select a valid parent'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'axesOff':
            text = 'Please have at least one axis checked'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'stiffness>1':
            text = 'The stiffness cannot be more than 1'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'stiffness<0':
            text = 'The stiffness cannot be smaller than 0'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'overshoot_0':
            text = 'The overshoot strength cannot be 0'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'frequency_small':
            text = 'The frequency cannot be less than 1'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'overshoot_range_small':
            text = 'The overshoot range cannot be smaller than 1'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'no_wind':
            text = 'You need to have a wind control \nin your scene to have wind'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'wind_off':
            text = 'You need to have one of your \n wind control wind attribute ON'
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'corrupt_default':
            text = ' Your default.json ui preset is broken \n please create a new one with the Export preset '
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'missing_default':
            text = ' Your default.json ui preset is missing \n please create a new one with the Export preset '
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        elif error_type == 'toolDones':
            self.error_label.setStyleSheet('color:lime')
            text = 'Overlap was excuted in {} seconds'.format(extra)
            self.error_label.setText(text)
            self.error_label.setVisible(True)
        font_metrics = self.error_label.fontMetrics()
        if pyside_version == '2':
            text_width = font_metrics.width(self.error_label.text()) * self.width_scale
            self.error_label.setFixedWidth(int(text_width))
        elif pyside_version == '6':
            text_width = font_metrics.horizontalAdvance(self.error_label.text()) * self.width_scale
            self.error_label.setFixedWidth(int(text_width))

    def get_parent(self):
        sel = mc.ls(sl=True, long=True)
        if sel:
            self.parent_result.setText(sel[0])

    def overlap(self):
        return bridge.overlap(self)

    def progress_bar_update(self, value):
        self.progress_bar.setValue(value)

    def closeEvent(self, event):
        bridge.cleanup(self)
        return super().closeEvent(event)

class partialImportDialog(MayaQWidgetBaseMixin, qt_w.QDialog):
    data_sent = qt_c.Signal(bool, bool, bool, bool, bool, bool, bool, bool)

    def __init__(self, parent=None):
        super(partialImportDialog, self).__init__(parent)
        screen = self.screen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()
        pixel_ratio = screen.devicePixelRatio()
        width_scale = screen_width / 1920
        height_scale = screen_height / 1080
        self.setWindowTitle('Partial import')
        self.resize(int(250 * width_scale), int(330 * height_scale))
        layout = qt_w.QVBoxLayout()
        self.setLayout(layout)
        self.import_label = qt_w.QLabel('Choose which attributes you want to import')
        self.overlap_type_checkbox = qt_w.QCheckBox('Overlap type')
        self.base_overlap_checkbox = qt_w.QCheckBox('Base overlap attributes')
        self.order_key_type_checkbox = qt_w.QCheckBox('Selection order & key type')
        self.complex_attribute_checkbox = qt_w.QCheckBox('Complex stiffness attributes')
        self.anim_layers_checkbox = qt_w.QCheckBox('Anim layers options')
        self.overshoot_checkbox = qt_w.QCheckBox('Overshoot attributes and options')
        self.wind_checkbox = qt_w.QCheckBox('Wind attribute and options')
        self.bonus_checkbox = qt_w.QCheckBox('Bonus options')
        self.button = qt_w.QPushButton('Partial import')
        layout.addWidget(self.import_label)
        self.create_separator(layout)
        layout.addWidget(self.overlap_type_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.base_overlap_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.order_key_type_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.complex_attribute_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.anim_layers_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.overshoot_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.wind_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.bonus_checkbox)
        self.create_separator(layout)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.partial_import)
        self.set_tool_tips()

    def set_tool_tips(self):
        self.overlap_type_checkbox.setToolTip('Contains the overlap type option')
        self.base_overlap_checkbox.setToolTip('Contain the following options:<b>\n<br>Time range type\n<br>Start time\n<br>End time\n<br>Rotation overlap main axis\n<br>Rotation overlap up axis\n<br>Overlap strength\n<br>Overlap stiffness ')
        self.order_key_type_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Order type\n<br>Keying type')
        self.complex_attribute_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Complex stifness option\n<br>Complex stifness curve')
        self.anim_layers_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Bake on selected layer\n<br>Bake on new layer\n<br>Additive type anim layer\n<br>Override type anim layer')
        self.overshoot_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Overshoot option\n<br>Overshoot first control only\n<br>Overshoot in between\n<br>Overshoot at the end')
        self.wind_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Wind option\n<br>Wind is absolute in translation')
        self.bonus_checkbox.setToolTip('<b></b>Contain the following options:<b>\n<br>Axes option and which are selected\n<br>Remove parent option\n<br>Remove parent selected transform name\n<br>Rotation ignore its own translation option\n<br>Default distance for rotation\n<br>Use only the default distance\n<br>Cycle animation')

    def create_separator(self, target_layout):
        separator = qt_w.QFrame()
        separator.setFrameShape(qt_w.QFrame.HLine)
        separator.setFixedHeight(1)
        target_layout.addWidget(separator)
        return separator

    def partial_import(self):
        overlap_type = self.overlap_type_checkbox.isChecked()
        base = self.base_overlap_checkbox.isChecked()
        order_key = self.order_key_type_checkbox.isChecked()
        complex_attribute = self.complex_attribute_checkbox.isChecked()
        anim_layers = self.anim_layers_checkbox.isChecked()
        overshoot = self.overshoot_checkbox.isChecked()
        wind = self.wind_checkbox.isChecked()
        bonus = self.bonus_checkbox.isChecked()
        self.data_sent.emit(overlap_type, base, order_key, complex_attribute, anim_layers, overshoot, wind, bonus)
        self.accept()
