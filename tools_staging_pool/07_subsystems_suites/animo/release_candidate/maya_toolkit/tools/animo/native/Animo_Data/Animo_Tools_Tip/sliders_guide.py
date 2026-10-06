"""
Animo Sliders Guide
A reference dialog listing every slider in Animo, what it's called, and what it does.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import compat
QtWidgets = compat.QtWidgets
QtCore = compat.QtCore
QtGui = compat.QtGui

import dpi_utils
scale_size = dpi_utils.scale_size
scale_font_size = dpi_utils.scale_font_size


SLIDER_GUIDE_DATA = [
    {
        "abbr": "TW",
        "name": "Tween Machine",
        "description": "Easily create breakdowns between your poses. Slide to blend toward the previous or next keyframe.",
        "color": (225, 175, 45),
    },
    {
        "abbr": "BN",
        "name": "Blend to Neighbor",
        "description": "Blend your current pose or selected keys toward neighboring keyframes to fine-tune spacing and favor a nearby pose.",
        "color": (220, 140, 60),
    },
    {
        "abbr": "SL",
        "name": "Scale from Left",
        "description": "Scale your selected keys using the key to the left as the pivot point.",
        "color": (100, 180, 220),
    },
    {
        "abbr": "BW",
        "name": "Blend to World",
        "description": "Blend your selected object toward its neighboring keys in world space. Drag right to blend toward the next key, left to blend toward the previous one.",
        "color": (180, 120, 200),
    },
    {
        "abbr": "EA",
        "name": "Ease",
        "description": "Ease your pose in or out, softening the timing around the current keyframe. Shortcut: Ctrl+TW.",
        "color": (92, 184, 214),
    },
    {
        "abbr": "BE",
        "name": "Blend to Ease",
        "description": "Smooth out the timing around your selected keys by blending them toward the neighboring keys. Drag right for an ease in, left for an ease out.",
        "color": (100, 192, 218),
    },
    {
        "abbr": "SR",
        "name": "Scale from Right",
        "description": "Scale your selected keys using the key to the right as the pivot point. Shortcut: Shift+SL.",
        "color": (113, 167, 214),
    },
    {
        "abbr": "SA",
        "name": "Scale from Average",
        "description": "Scale your selected keys using the average of the curve as the pivot point. Shortcut: Ctrl+SL.",
        "color": (131, 158, 216),
    },
    {
        "abbr": "SD",
        "name": "Scale from Default",
        "description": "Scale your selected keys using the attribute's default value as the pivot point. Drag right to exaggerate away from default, left to flatten back toward it.",
        "color": (145, 161, 224),
    },
    {
        "abbr": "BD",
        "name": "Blend to Default",
        "description": "Blend your selected keys toward the attribute's default value. Drag right toward default, left to push away from it.",
        "color": (157, 164, 231),
    },
    {
        "abbr": "TO",
        "name": "Time Offset",
        "description": "Offsets the animation without offsetting the timing. The more keys you have selected, the better the result.",
        "color": (150, 135, 222),
    },
    {
        "abbr": "TS",
        "name": "Time Offset Stagger",
        "description": "Offsets the animation like Time Offset, but staggers the amount based on the order you selected your objects. The first object selected offsets the most, with each object selected after it offsetting progressively less.",
        "color": (163, 133, 226),
    },
    {
        "abbr": "NW",
        "name": "Noise / Wave",
        "description": "Add a smooth wave to your selected keys by dragging right, or randomized noise by dragging left.",
        "color": (178, 140, 227),
    },
    {
        "abbr": "CN",
        "name": "Connect to Neighbour",
        "description": "Connect multiple animation curves to a single selected keyframe without breaking their original motion.",
        "color": (205, 147, 230),
    },
    {
        "abbr": "PP",
        "name": "Push / Pull",
        "description": "Push or pull your selected keys relative to a straight line between their neighbors. Left aligns them linearly, right pushes them further out.",
        "color": (84, 206, 212),
    },
    {
        "abbr": "SH",
        "name": "Smooth | Harsh",
        "description": "Smooth your selected keys toward their neighbors by dragging right or push them further apart for a harsher, snappier feel by dragging left.",
        "color": (212, 144, 228),
    },
    {
        "abbr": "SB",
        "name": "Simplify | Bake",
        "description": "Clean up your curves by dragging left to remove extra keys while keeping the shape or drag right to bake in more keys for denser control.",
        "color": (218, 142, 226),
    },
    {
        "abbr": "BI",
        "name": "Blend to Infinity",
        "description": "Extend the motion of your selected keys past their neighbors, as if the animation kept going. Drag right to project forward, left to project backward.",
        "color": (224, 140, 224),
    },
    {
        "abbr": "BM",
        "name": "Blend to Mirror",
        "description": "Blend your pose toward its mirrored side. Drag right to move toward the mirror, left to push away from it. Make sure you've snapshotted your rig's default pose first.",
        "color": (230, 138, 205),
    },
]


_guide_dialog = None


class _SlidersGuideDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(_SlidersGuideDialog, self).__init__(parent)
        self.setWindowTitle("Animo Sliders Guide")
        self.setMinimumWidth(scale_size(480))
        self.setMinimumHeight(scale_size(420))
        self.setStyleSheet('''
            QDialog { background-color: #2e2e2e; }
            QScrollArea { border: none; background-color: #2e2e2e; }
            QScrollArea > QWidget > QWidget { background-color: #2e2e2e; }
            QLabel { color: #ddd; }
        ''')

        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(scale_size(14), scale_size(14), scale_size(14), scale_size(14))
        outer_layout.setSpacing(scale_size(10))

        header = QtWidgets.QLabel("Every slider in Animo, and what it does.")
        header_font = header.font()
        header_font.setPixelSize(scale_font_size(13))
        header.setFont(header_font)
        header.setStyleSheet("color: #999;")
        outer_layout.addWidget(header)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, scale_size(8), 0)
        content_layout.setSpacing(scale_size(4))

        for entry in SLIDER_GUIDE_DATA:
            content_layout.addWidget(self._buildRow(entry))

        content_layout.addStretch(1)
        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area, 1)

        close_row = QtWidgets.QHBoxLayout()
        close_row.addStretch(1)
        close_button = QtWidgets.QPushButton("Close")
        close_button.setStyleSheet('''
            QPushButton { background-color: #444; color: #ddd; border: 1px solid #555; border-radius: 3px; padding: 5px 18px; }
            QPushButton:hover { background-color: #555; }
        ''')
        close_button.clicked.connect(self.close)
        close_row.addWidget(close_button)
        outer_layout.addLayout(close_row)

    def _buildRow(self, entry):
        row = QtWidgets.QWidget()
        row.setStyleSheet('''
            QWidget#sliderGuideRow { background-color: #383838; border-radius: 4px; }
            QWidget#sliderGuideRow:hover { background-color: #404040; }
        ''')
        row.setObjectName("sliderGuideRow")

        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(scale_size(10), scale_size(8), scale_size(10), scale_size(8))
        row_layout.setSpacing(scale_size(12))

        r, g, b = entry["color"]
        badge = QtWidgets.QLabel(entry["abbr"])
        badge.setAlignment(QtCore.Qt.AlignCenter)
        badge.setFixedSize(scale_size(46), scale_size(28))
        badge_font = badge.font()
        badge_font.setBold(True)
        badge_font.setPixelSize(scale_font_size(12))
        badge.setFont(badge_font)
        badge.setStyleSheet(
            "background-color: rgb({0},{1},{2}); color: #1c1c1c; border-radius: 5px;".format(r, g, b)
        )
        row_layout.addWidget(badge, 0, QtCore.Qt.AlignTop)

        text_col = QtWidgets.QVBoxLayout()
        text_col.setSpacing(scale_size(2))

        name_label = QtWidgets.QLabel(entry["name"])
        name_font = name_label.font()
        name_font.setBold(True)
        name_font.setPixelSize(scale_font_size(13))
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #f0f0f0;")
        text_col.addWidget(name_label)

        desc_label = QtWidgets.QLabel(entry["description"])
        desc_label.setWordWrap(True)
        desc_font = desc_label.font()
        desc_font.setPixelSize(scale_font_size(12))
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #aaa;")
        text_col.addWidget(desc_label)

        row_layout.addLayout(text_col, 1)

        return row


def show_sliders_guide(parent=None):
    global _guide_dialog
    try:
        if _guide_dialog is not None:
            _guide_dialog.close()
            _guide_dialog.deleteLater()
    except:
        pass
    _guide_dialog = _SlidersGuideDialog(parent)
    _guide_dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
    _guide_dialog.show()
    _guide_dialog.raise_()
    _guide_dialog.activateWindow()
    return _guide_dialog