from __future__ import print_function, division, absolute_import

from spacify_core import QtWidgets, QtCore
from dpi_scale import dpi


def create_button(text, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(28))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    button.setStyleSheet("""
        QPushButton {{
            background-color: #1565C0;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #1976D2; }}
        QPushButton:pressed {{ background-color: #0D47A1; }}
    """.format(dpi(6), dpi(12)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_red_button(text, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(28))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    button.setStyleSheet("""
        QPushButton {{
            background-color: #C94A47;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #D95A57; }}
        QPushButton:pressed {{ background-color: #B93A37; }}
    """.format(dpi(6), dpi(12)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_yellow_button(text, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(28))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    button.setStyleSheet("""
        QPushButton {{
            background-color: #B8A547;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: #C8B557; }}
        QPushButton:pressed {{ background-color: #A89537; }}
    """.format(dpi(6), dpi(12)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_gradient_button(text, colors, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(28))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    main_color, hover_color, pressed_color = colors
    button.setStyleSheet("""
        QPushButton {{
            background-color: {0};
            border: none;
            color: white;
            padding: {3}px {4}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        QPushButton:hover {{ background-color: {1}; }}
        QPushButton:pressed {{ background-color: {2}; }}
    """.format(main_color, hover_color, pressed_color, dpi(6), dpi(12)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_compact_gradient_button(text, colors, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(22))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    main_color, hover_color, pressed_color = colors
    button.setStyleSheet("""
        QPushButton {{
            background-color: {0};
            border: none;
            color: white;
            padding: {3}px {4}px;
            border-radius: 4px;
            font-size: 7pt;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        QPushButton:hover {{ background-color: {1}; }}
        QPushButton:pressed {{ background-color: {2}; }}
    """.format(main_color, hover_color, pressed_color, dpi(4), dpi(8)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_compact_button(text, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(22))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    button.setStyleSheet("""
        QPushButton {{
            background-color: #1565C0;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 4px;
            font-size: 7pt;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}
        QPushButton:hover {{ background-color: #1976D2; }}
        QPushButton:pressed {{ background-color: #0D47A1; }}
    """.format(dpi(4), dpi(8)))
    if callback:
        button.clicked.connect(callback)
    return button


def create_small_button(text, callback):
    button = QtWidgets.QPushButton(text)
    button.setMinimumHeight(dpi(28))
    button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
    button.setStyleSheet("""
        QPushButton {{
            background-color: #2A2A2A;
            border: none;
            color: white;
            padding: {0}px {1}px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }}
        QPushButton:hover {{ background-color: #353535; }}
        QPushButton:pressed {{ background-color: #1F1F1F; }}
    """.format(dpi(6), dpi(12)))
    if callback:
        button.clicked.connect(callback)
    return button
