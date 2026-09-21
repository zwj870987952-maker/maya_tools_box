"""
Custom tool button widget matching animBot's flat, rounded, responsive aesthetic.
"""

from PySide6 import QtWidgets, QtCore, QtGui
from ..core.theme import AnimBotColors, AnimBotStyle
from ..core.icons import AnimBotIconProvider

class AnimBotButton(QtWidgets.QToolButton):
    """
    AnimBot style tool button with group-colored hover outline,
    right-click context menu, and clean tooltips.
    """
    rightClicked = QtCore.Signal(QtCore.QPoint)
    middleClicked = QtCore.Signal()

    def __init__(self, icon_name=None, tooltip=None, accent_color=AnimBotColors.WHITE, color_category="white", parent=None):
        super().__init__(parent)
        self.accent_color = accent_color
        self.color_category = color_category
        self.icon_name = icon_name
        self.custom_menu = None
        
        self.setFixedSize(AnimBotStyle.BTN_SIZE, AnimBotStyle.BTN_SIZE)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setAutoRaise(True)
        self.setIconSize(QtCore.QSize(22, 22))
        
        if tooltip:
            self.setToolTip(tooltip)
            
        if icon_name:
            self.set_anim_icon(icon_name, color_category)
            
        self.update_style()

    def set_anim_icon(self, name, category=None):
        if category:
            self.color_category = category
        icon = AnimBotIconProvider.get_icon(name, self.color_category, tint_color=None)
        self.setIcon(icon)

    def set_accent_color(self, color):
        self.accent_color = color
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: {AnimBotStyle.BTN_RADIUS}px;
            margin: 0px;
            padding: 0px;
        }}
        QToolButton:hover {{
            background-color: {AnimBotColors.BG_BUTTON_HOVER};
            border: 1px solid {self.accent_color};
        }}
        QToolButton:pressed {{
            background-color: {self.accent_color};
            border: 1px solid {AnimBotColors.BORDER_DARK};
        }}
        QToolButton:checked {{
            background-color: {self.accent_color};
            border: 1px solid {AnimBotColors.BORDER_DARK};
        }}
        """)

    def set_context_menu(self, menu):
        self.custom_menu = menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _show_context_menu(self, pos):
        if self.custom_menu:
            self.custom_menu.exec_(self.mapToGlobal(pos))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            self.rightClicked.emit(event.pos())
            if self.custom_menu:
                self.custom_menu.exec_(self.mapToGlobal(event.pos()))
                return
        elif event.button() == QtCore.Qt.MiddleButton:
            self.middleClicked.emit()
        super().mousePressEvent(event)
