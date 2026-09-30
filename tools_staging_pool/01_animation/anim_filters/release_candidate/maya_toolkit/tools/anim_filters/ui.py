# -*- coding: utf-8 -*-
# UI adaptation of animFilters, Copyright 2018 Michal Mach; GPL-2.0-or-later.
from __future__ import absolute_import, division, print_function

import os
from functools import partial
from maya_toolkit.core import get_maya_main_window
from .operations import commands
from .preview import PreviewSession

_controllers = []


def checked(value):
    return value if isinstance(value, bool) else str(value).lower() in ("1", "true", "yes", "on")


def show(tool, parent=None, settings=None):
    try:
        from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools
    except ImportError:
        from PySide2 import QtCore, QtGui, QtWidgets, QtUiTools
    if QtWidgets.QApplication.instance() is None:
        raise RuntimeError("Open this UI in a Maya GUI session")
    for previous in list(_controllers):
        if not previous.closed:
            previous.window.close()
            if not previous.closed:
                return previous.window
    _controllers[:] = []
    root = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(root, "upstream", "scripts", "animFilters", "animFilters.ui")
    source = QtCore.QFile(path)
    if not source.open(QtCore.QIODevice.ReadOnly):
        raise IOError("Cannot read UI resource: " + path)
    try:
        window = QtUiTools.QUiLoader().load(source, parent or get_maya_main_window())
    finally:
        source.close()
    if window is None:
        raise RuntimeError("Qt failed to load animFilters.ui")
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
    window.setWindowIcon(QtGui.QIcon(os.path.join(root, "upstream", "icons", "animFilters.png")))

    class Controller(QtCore.QObject):
        def __init__(self):
            super(Controller, self).__init__(window)
            self.window = window
            self.closed = False
            self.preview = PreviewSession(tool, commands())
            self.settings = settings if settings is not None else QtCore.QSettings("MayaAnimFilters", "animFilters")
            self.controls = {}
            names = ("thresholdSlider", "thresholdSpinBox", "multiSlider", "multiSpinBox", "medianSlider", "medianSpinBox", "butterSampleFreqSlider", "butterSampleFreqSpinBox", "butterCutoffFreqSlider", "butterCutoffFreqSpinBox", "butterOrderSlider", "butterOrderSpinBox", "previewButton", "cancelButton", "applyButton", "resetButton", "bufferCurvesCheckBox", "tabWidget")
            for name in names:
                control = window.findChild(QtCore.QObject, name)
                if control is None:
                    raise RuntimeError("Missing upstream UI control: " + name)
                self.controls[name] = control
            self.controls["bufferCurvesCheckBox"].setChecked(checked(self.settings.value("bufferCurves", True)))
            self.controls["bufferCurvesCheckBox"].stateChanged.connect(self.save_buffer_setting)
            for slider, spin, multiplier in (("thresholdSlider", "thresholdSpinBox", 1000.0), ("multiSlider", "multiSpinBox", 1.0), ("medianSlider", "medianSpinBox", 1.0), ("butterSampleFreqSlider", "butterSampleFreqSpinBox", 1.0), ("butterCutoffFreqSlider", "butterCutoffFreqSpinBox", 100.0), ("butterOrderSlider", "butterOrderSpinBox", 1.0)):
                self.controls[slider].valueChanged.connect(partial(self.slider_changed, spin, multiplier))
                self.controls[spin].valueChanged.connect(partial(self.spin_changed, slider, multiplier))
            self.controls["previewButton"].clicked.connect(self.start)
            self.controls["cancelButton"].clicked.connect(self.cancel)
            self.controls["applyButton"].clicked.connect(self.apply)
            self.controls["resetButton"].clicked.connect(self.reset_values)
            window.installEventFilter(self)
            window.destroyed.connect(self.destroyed_window)
            self.switch_state()

        def destroyed_window(self, *unused):
            self.closed = True

        def save_buffer_setting(self, *unused):
            self.settings.setValue("bufferCurves", self.controls["bufferCurvesCheckBox"].isChecked())

        def sync(self, name, value):
            control = self.controls[name]
            old = control.blockSignals(True)
            try:
                control.setValue(value)
            finally:
                control.blockSignals(old)

        def slider_changed(self, name, multiplier, value):
            control = self.controls[name]
            converted = value / multiplier
            self.sync(name, int(converted) if isinstance(control, QtWidgets.QSpinBox) else converted)
            if self.preview.active:
                self.refresh()

        def spin_changed(self, name, multiplier, value):
            self.sync(name, int(value * multiplier))
            if self.preview.active:
                self.refresh()

        def arguments(self):
            c = self.controls
            result = {"mode": ("adaptive", "butterworth", "median")[c["tabWidget"].currentIndex()], "tolerance": c["thresholdSpinBox"].value() * c["multiSpinBox"].value(), "window_size": c["medianSpinBox"].value(), "sample_frequency": c["butterSampleFreqSpinBox"].value(), "cutoff": c["butterCutoffFreqSpinBox"].value(), "order": c["butterOrderSpinBox"].value()}
            if self.preview.arguments:
                for name in ("anim_curves", "time_range"):
                    result[name] = self.preview.arguments[name]
            return result

        def report(self, result):
            if result is not None:
                print(result.to_json())
                if not result.success:
                    commands().warning(result.message)
            self.switch_state()

        def switch_state(self):
            active = self.preview.active
            for name, enabled in (("previewButton", not active), ("cancelButton", active), ("applyButton", active)):
                self.controls[name].setEnabled(enabled)
            tab = self.controls["tabWidget"]
            for index in range(tab.count()):
                tab.setTabEnabled(index, not active or index == tab.currentIndex())
            window.statusBar().showMessage("Live preview; Cancel/close restores it. Undo stays enabled." if active else "")

        def start(self, *unused):
            try:
                self.report(self.preview.update(self.arguments(), buffer=self.controls["bufferCurvesCheckBox"].isChecked()))
            except Exception as error:
                commands().warning(str(error))
                self.switch_state()

        def refresh(self):
            try:
                self.report(self.preview.update(self.arguments()))
            except Exception as error:
                commands().warning(str(error))
                self.switch_state()

        def cancel(self, *unused):
            try:
                self.preview.cancel()
                self.preview.arguments = None
            except Exception as error:
                commands().warning(str(error))
            self.switch_state()

        def apply(self, *unused):
            if self.preview.result is not None and not self.preview.result.success:
                commands().warning("Cannot apply a failed preview; Cancel it first")
                return
            self.report(self.preview.apply())

        def reset_values(self, *unused):
            index = self.controls["tabWidget"].currentIndex()
            defaults = (("multiSpinBox", 0.5), ("thresholdSpinBox", 0.5)) if index == 0 else (("butterSampleFreqSpinBox", 30), ("butterCutoffFreqSpinBox", 7), ("butterOrderSpinBox", 5)) if index == 1 else (("medianSpinBox", 35),)
            for name, value in defaults:
                self.controls[name].setValue(value)

        def eventFilter(self, watched, event):
            if watched is window and event.type() == QtCore.QEvent.Close:
                try:
                    self.preview.cancel()
                except Exception as error:
                    commands().warning(str(error))
                    event.ignore()
                    return True
                self.closed = True
            return super(Controller, self).eventFilter(watched, event)

    controller = Controller()
    _controllers.append(controller)
    window.show()
    return window
