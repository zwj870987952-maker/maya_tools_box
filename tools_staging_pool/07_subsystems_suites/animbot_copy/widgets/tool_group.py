"""
Tool Group container widget matching animBot's clean modular layout without underlines.
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle

class AnimBotToolGroup(QtWidgets.QWidget):
    """
    Container for a group of related animBot tools with compact layout and no underlines.
    """
    def __init__(self, group_name="", accent_color=AnimBotColors.WHITE, parent=None):
        super().__init__(parent)
        self.group_name = group_name
        self.accent_color = accent_color
        self.is_collapsed = False
        
        # Horizontal layout directly for compact and clean alignment
        self.content_layout = QtWidgets.QHBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(1)

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)

    def add_spacing(self, size=2):
        self.content_layout.addSpacing(size)

    def set_collapsed(self, collapsed):
        self.is_collapsed = collapsed
        for i in range(1, self.content_layout.count()):
            item = self.content_layout.itemAt(i)
            if item.widget():
                item.widget().setVisible(not collapsed)

    def toggle_collapsed(self):
        self.set_collapsed(not self.is_collapsed)
