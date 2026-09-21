"""
Custom styled menus for animBot logo and context menus.
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle

class AnimBotMenu(QtWidgets.QMenu):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(f"""
        QMenu {{
            background-color: {AnimBotColors.BG_DARK};
            color: {AnimBotColors.TEXT_MAIN};
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 4px;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 12px;
        }}
        QMenu::item {{
            padding: 6px 24px 6px 28px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: #484848;
            color: #FFFFFF;
        }}
        QMenu::separator {{
            height: 1px;
            background: #3A3A3A;
            margin: 4px 8px;
        }}
        """)
