"""
QT MODERN

MIT License

Copyright (c) 2017 Gerard Marull-Paretas <gerardmarull@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .. import Qt
#from qtpy.QtGui import Qt.QtGui.QPalette, Qt.QtGui.QColor

# Constant to reference default themes
DEFAULT_DARK_PALETTE = 'Dark'
DEFAULT_LIGHT_PALETTE = 'Light'


def dark(app):
    """
    Apply dark theme to the Qt application instance.

    Args:
        app (QApplication): QApplication instance.
    """

    dark_palette = Qt.QtGui.QPalette()

    # base
    dark_palette.setColor(Qt.QtGui.QPalette.WindowText, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.Button, Qt.QtGui.QColor(53, 53, 53))
    dark_palette.setColor(Qt.QtGui.QPalette.Light, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.Midlight, Qt.QtGui.QColor(90, 90, 90))
    dark_palette.setColor(Qt.QtGui.QPalette.Dark, Qt.QtGui.QColor(35, 35, 35))
    dark_palette.setColor(Qt.QtGui.QPalette.Text, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.BrightText, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.ButtonText, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.Base, Qt.QtGui.QColor(42, 42, 42))
    dark_palette.setColor(Qt.QtGui.QPalette.Window, Qt.QtGui.QColor(53, 53, 53))
    dark_palette.setColor(Qt.QtGui.QPalette.Shadow, Qt.QtGui.QColor(20, 20, 20))
    dark_palette.setColor(Qt.QtGui.QPalette.Highlight, Qt.QtGui.QColor(42, 130, 218))
    dark_palette.setColor(Qt.QtGui.QPalette.HighlightedText, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.Link, Qt.QtGui.QColor(56, 252, 196))
    dark_palette.setColor(Qt.QtGui.QPalette.AlternateBase, Qt.QtGui.QColor(66, 66, 66))
    dark_palette.setColor(Qt.QtGui.QPalette.ToolTipBase, Qt.QtGui.QColor(53, 53, 53))
    dark_palette.setColor(Qt.QtGui.QPalette.ToolTipText, Qt.QtGui.QColor(180, 180, 180))
    dark_palette.setColor(Qt.QtGui.QPalette.LinkVisited, Qt.QtGui.QColor(80, 80, 80))

    # disabled
    dark_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.WindowText,
                         Qt.QtGui.QColor(127, 127, 127))
    dark_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.Text,
                         Qt.QtGui.QColor(127, 127, 127))
    dark_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.ButtonText,
                         Qt.QtGui.QColor(127, 127, 127))
    dark_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.Highlight,
                         Qt.QtGui.QColor(80, 80, 80))
    dark_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.HighlightedText,
                         Qt.QtGui.QColor(127, 127, 127))

    app.style().unpolish(app)
    app.setPalette(dark_palette)

    app.setStyle('Fusion')


def light(app):
    """
    Apply light theme to the Qt application instance.

    Args:
        app (QApplication): QApplication instance.
    """

    light_palette = Qt.QtGui.QPalette()

    # base
    light_palette.setColor(Qt.QtGui.QPalette.WindowText, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.Button, Qt.QtGui.QColor(240, 240, 240))
    light_palette.setColor(Qt.QtGui.QPalette.Light, Qt.QtGui.QColor(180, 180, 180))
    light_palette.setColor(Qt.QtGui.QPalette.Midlight, Qt.QtGui.QColor(200, 200, 200))
    light_palette.setColor(Qt.QtGui.QPalette.Dark, Qt.QtGui.QColor(225, 225, 225))
    light_palette.setColor(Qt.QtGui.QPalette.Text, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.BrightText, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.ButtonText, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.Base, Qt.QtGui.QColor(237, 237, 237))
    light_palette.setColor(Qt.QtGui.QPalette.Window, Qt.QtGui.QColor(240, 240, 240))
    light_palette.setColor(Qt.QtGui.QPalette.Shadow, Qt.QtGui.QColor(20, 20, 20))
    light_palette.setColor(Qt.QtGui.QPalette.Highlight, Qt.QtGui.QColor(76, 163, 224))
    light_palette.setColor(Qt.QtGui.QPalette.HighlightedText, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.Link, Qt.QtGui.QColor(0, 162, 232))
    light_palette.setColor(Qt.QtGui.QPalette.AlternateBase, Qt.QtGui.QColor(225, 225, 225))
    light_palette.setColor(Qt.QtGui.QPalette.ToolTipBase, Qt.QtGui.QColor(240, 240, 240))
    light_palette.setColor(Qt.QtGui.QPalette.ToolTipText, Qt.QtGui.QColor(0, 0, 0))
    light_palette.setColor(Qt.QtGui.QPalette.LinkVisited, Qt.QtGui.QColor(222, 222, 222))

    # disabled
    light_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.WindowText,
                          Qt.QtGui.QColor(115, 115, 115))
    light_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.Text,
                          Qt.QtGui.QColor(115, 115, 115))
    light_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.ButtonText,
                          Qt.QtGui.QColor(115, 115, 115))
    light_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.Highlight,
                          Qt.QtGui.QColor(190, 190, 190))
    light_palette.setColor(Qt.QtGui.QPalette.Disabled, Qt.QtGui.QPalette.HighlightedText,
                          Qt.QtGui.QColor(115, 115, 115))

    app.style().unpolish(app)
    app.setPalette(light_palette)

    app.setStyle('Fusion')
