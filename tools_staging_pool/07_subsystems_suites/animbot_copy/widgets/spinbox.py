"""
Custom dark rounded spinboxes matching animBot's numeric inputs.
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle

class AnimBotDoubleSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, value=1.000, decimals=3, step=0.1, min_val=-9999.0, max_val=9999.0, accent_color=AnimBotColors.GREEN, parent=None):
        super().__init__(parent)
        self.setDecimals(decimals)
        self.setSingleStep(step)
        self.setRange(min_val, max_val)
        self.setValue(value)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(58, AnimBotStyle.BTN_SIZE)
        self.setStyleSheet(AnimBotStyle.get_spinbox_stylesheet(accent_color))
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setCursor(QtCore.Qt.IBeamCursor)


class AnimBotSpinBox(QtWidgets.QSpinBox):
    def __init__(self, value=1, step=1, min_val=-9999, max_val=9999, accent_color=AnimBotColors.GREEN, parent=None):
        super().__init__(parent)
        self.setSingleStep(step)
        self.setRange(min_val, max_val)
        self.setValue(value)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setFixedSize(46, AnimBotStyle.BTN_SIZE)
        self.setStyleSheet(AnimBotStyle.get_spinbox_stylesheet(accent_color))
        self.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.setCursor(QtCore.Qt.IBeamCursor)
