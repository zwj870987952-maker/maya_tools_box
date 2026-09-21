"""
Theme and styling definitions for animBot clone.
Provides exact animBot color palettes, stylesheets, and geometry constants.
"""

from PySide6 import QtGui, QtCore

class AnimBotColors:
    # Group Accents
    GREEN = "#84F296"      # Nudge, Bake, Key Slider (Ease)
    YELLOW = "#F2E66C"     # Tween Slider
    ORANGE = "#F2A785"     # Tangents, Tangent Slider
    PURPLE = "#D9D0F2"     # Select Sets, Selection tools
    PINK = "#F2C3ED"       # Align objects, Mirror, Space Switcher
    RED = "#FF6B6B"        # Bookmarks, Motion Trail, Suspend
    TURQUOISE = "#9DECF2"  # Temp Controls, Temp Pivot, Master Spline
    BLUE = "#C1E2F2"       # Extra tools, Channel box, Graph Editor
    WHITE = "#E6E6E6"      # General, Main Menu, Search
    
    # UI Dark Neutrals
    BG_DARK = "#282828"
    BG_PANEL = "#333333"
    BG_TOOLBAR = "#383838"
    BG_SLIDER_GROOVE = "#3C3C3C"
    BG_BUTTON = "#484848"
    BG_BUTTON_HOVER = "#585858"
    BG_BUTTON_PRESSED = "#2C2C2C"
    
    # Text
    TEXT_MAIN = "#DCDCDC"
    TEXT_MUTED = "#8C8C8C"
    TEXT_DARK = "#202020"
    
    # Borders
    BORDER_DARK = "#222222"
    BORDER_LIGHT = "#505050"


class AnimBotStyle:
    # Standard sizes
    BTN_SIZE = 30
    BTN_RADIUS = 5
    SLIDER_HEIGHT = 30
    SLIDER_RADIUS = 6
    GROUP_MARGIN = 2
    GROUP_SPACING = 1
    
    @staticmethod
    def get_button_stylesheet(accent_color=AnimBotColors.WHITE, is_checkable=False):
        return f"""
        QToolButton, QPushButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: {AnimBotStyle.BTN_RADIUS}px;
            color: {AnimBotColors.TEXT_MAIN};
            padding: 0px;
            margin: 0px;
        }}
        QToolButton:hover, QPushButton:hover {{
            background-color: {AnimBotColors.BG_BUTTON_HOVER};
            border: 1px solid {accent_color};
        }}
        QToolButton:pressed, QPushButton:pressed {{
            background-color: {accent_color};
            border: 1px solid {AnimBotColors.BORDER_DARK};
            color: {AnimBotColors.TEXT_DARK};
        }}
        QToolButton:checked, QPushButton:checked {{
            background-color: {accent_color};
            border: 1px solid {AnimBotColors.BORDER_DARK};
            color: {AnimBotColors.TEXT_DARK};
        }}
        QToolButton:disabled, QPushButton:disabled {{
            background-color: transparent;
            color: {AnimBotColors.TEXT_MUTED};
            border: none;
        }}
        """

    @staticmethod
    def get_spinbox_stylesheet(accent_color=AnimBotColors.GREEN):
        return f"""
        QSpinBox, QDoubleSpinBox {{
            background-color: {AnimBotColors.BG_DARK};
            color: {AnimBotColors.TEXT_MAIN};
            border: 1px solid #383838;
            border-radius: 5px;
            padding: 2px 4px;
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 11px;
            font-weight: bold;
            selection-background-color: {accent_color};
            selection-color: {AnimBotColors.TEXT_DARK};
        }}
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border: 1px solid {accent_color};
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {accent_color};
            background-color: #202020;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width: 0px;
            height: 0px;
            border: none;
        }}
        """

    @staticmethod
    def get_toolbar_stylesheet():
        return f"""
        #AnimBotMainToolbar {{
            background-color: {AnimBotColors.BG_TOOLBAR};
            border: none;
        }}
        QToolTip {{
            background-color: #242424;
            color: #E0E0E0;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
            font-family: 'Segoe UI', 'Arial', sans-serif;
        }}
        QMenu {{
            background-color: {AnimBotColors.BG_DARK};
            color: {AnimBotColors.TEXT_MAIN};
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 5px 20px 5px 25px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: #4A4A4A;
            color: #FFFFFF;
        }}
        QMenu::separator {{
            height: 1px;
            background: #444444;
            margin: 4px 8px;
        }}
        """
