from __future__ import print_function, division, absolute_import

from spacify_core import QtWidgets
from dpi_scale import dpi


def create_xform_tab(parent):
    tab = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(tab)
    layout.setContentsMargins(0, dpi(11), 0, 0)
    layout.setSpacing(dpi(6))
    
    # ============ GROUP 1: Copy/Paste XForm ============
    
    # Copy XForm row
    copy_row = QtWidgets.QWidget()
    copy_row_layout = QtWidgets.QHBoxLayout(copy_row)
    copy_row_layout.setContentsMargins(0, 0, 0, 0)
    copy_row_layout.setSpacing(dpi(6))
    
    parent.copy_xform_btn = QtWidgets.QPushButton("Copy XForm")
    parent.copy_xform_btn.setMinimumHeight(dpi(35))
    parent.copy_xform_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A3D;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #4D3A4D; }
        QPushButton:pressed { background-color: #2D1A2D; }
    """)
    parent.copy_xform_btn.clicked.connect(parent.execute_copy_xform)
    copy_row_layout.addWidget(parent.copy_xform_btn)
    
    parent.copy_xform_range_btn = QtWidgets.QPushButton("Copy XForm\nRange")
    parent.copy_xform_range_btn.setMinimumHeight(dpi(35))
    parent.copy_xform_range_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A3D;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 7pt;
            font-weight: 700;
            line-height: 1.1;
        }
        QPushButton:hover { background-color: #4D3A4D; }
        QPushButton:pressed { background-color: #2D1A2D; }
    """)
    parent.copy_xform_range_btn.clicked.connect(parent.execute_copy_xform_range)
    copy_row_layout.addWidget(parent.copy_xform_range_btn)
    
    layout.addWidget(copy_row)
    
    # Paste XForm button
    parent.paste_xform_btn = QtWidgets.QPushButton("Paste XForm")
    parent.paste_xform_btn.setMinimumHeight(dpi(38))
    parent.paste_xform_btn.setStyleSheet("""
        QPushButton {
            background-color: #8B4789;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #9B5799; }
        QPushButton:pressed { background-color: #7B3779; }
    """)
    parent.paste_xform_btn.clicked.connect(parent.execute_paste_xform)
    layout.addWidget(parent.paste_xform_btn)
    
    # ============ SEPARATOR between Group 1 and 2 ============
    layout.addSpacing(dpi(12))
    separator1 = QtWidgets.QFrame()
    separator1.setFrameShape(QtWidgets.QFrame.HLine)
    separator1.setStyleSheet("background-color: #4D3A4D; max-height: 1px; margin: 0px;")
    layout.addWidget(separator1)
    layout.addSpacing(dpi(12))
    
    # ============ GROUP 2: Copy/Paste XForm Relationship ============
    
    # Copy XForm Relationship button
    parent.copy_xform_relationship_btn = QtWidgets.QPushButton("Copy XForm Relationship")
    parent.copy_xform_relationship_btn.setMinimumHeight(dpi(38))
    parent.copy_xform_relationship_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A3D;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #4D3A4D; }
        QPushButton:pressed { background-color: #2D1A2D; }
    """)
    parent.copy_xform_relationship_btn.clicked.connect(parent.execute_copy_xform_relationship)
    layout.addWidget(parent.copy_xform_relationship_btn)
    
    layout.addSpacing(dpi(6))
    
    # Paste XForm Relationship row
    paste_rel_row = QtWidgets.QWidget()
    paste_rel_row_layout = QtWidgets.QHBoxLayout(paste_rel_row)
    paste_rel_row_layout.setContentsMargins(0, 0, 0, 0)
    paste_rel_row_layout.setSpacing(dpi(6))
    
    parent.paste_relationship_btn = QtWidgets.QPushButton("Paste")
    parent.paste_relationship_btn.setMinimumHeight(dpi(38))
    parent.paste_relationship_btn.setStyleSheet("""
        QPushButton {
            background-color: #8B4789;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #9B5799; }
        QPushButton:pressed { background-color: #7B3779; }
    """)
    parent.paste_relationship_btn.clicked.connect(parent.execute_paste_xform_relationship)
    paste_rel_row_layout.addWidget(parent.paste_relationship_btn)
    
    parent.bake_relationship_btn = QtWidgets.QPushButton("Bake")
    parent.bake_relationship_btn.setMinimumHeight(dpi(38))
    parent.bake_relationship_btn.setStyleSheet("""
        QPushButton {
            background-color: #8B4789;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #9B5799; }
        QPushButton:pressed { background-color: #7B3779; }
    """)
    parent.bake_relationship_btn.clicked.connect(parent.execute_bake_xform_relationship)
    paste_rel_row_layout.addWidget(parent.bake_relationship_btn)
    
    layout.addWidget(paste_rel_row)
    
    # ============ SEPARATOR between Group 2 and 3 ============
    layout.addSpacing(dpi(12))
    separator2 = QtWidgets.QFrame()
    separator2.setFrameShape(QtWidgets.QFrame.HLine)
    separator2.setStyleSheet("background-color: #4D3A4D; max-height: 1px; margin: 0px;")
    layout.addWidget(separator2)
    layout.addSpacing(dpi(12))
    
    # ============ GROUP 3: Align ============
    
    # Align row
    align_row = QtWidgets.QWidget()
    align_row_layout = QtWidgets.QHBoxLayout(align_row)
    align_row_layout.setContentsMargins(0, 0, 0, 0)
    align_row_layout.setSpacing(dpi(6))
    
    parent.align_translate_btn = QtWidgets.QPushButton("Align\n(Translate)")
    parent.align_translate_btn.setMinimumHeight(dpi(38))
    parent.align_translate_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A47;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 7pt;
            font-weight: 700;
            line-height: 1.1;
        }
        QPushButton:hover { background-color: #4D3A57; }
        QPushButton:pressed { background-color: #2D1A37; }
    """)
    parent.align_translate_btn.clicked.connect(parent.execute_align_translate)
    align_row_layout.addWidget(parent.align_translate_btn)
    
    parent.align_rotate_btn = QtWidgets.QPushButton("Align\n(Rotate)")
    parent.align_rotate_btn.setMinimumHeight(dpi(38))
    parent.align_rotate_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A47;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 7pt;
            font-weight: 700;
            line-height: 1.1;
        }
        QPushButton:hover { background-color: #4D3A57; }
        QPushButton:pressed { background-color: #2D1A37; }
    """)
    parent.align_rotate_btn.clicked.connect(parent.execute_align_rotate)
    align_row_layout.addWidget(parent.align_rotate_btn)
    
    layout.addWidget(align_row)
    
    layout.addSpacing(dpi(6))
    
    # Align button
    parent.align_btn = QtWidgets.QPushButton("Align")
    parent.align_btn.setMinimumHeight(dpi(38))
    parent.align_btn.setStyleSheet("""
        QPushButton {
            background-color: #8B72A5;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #9B82B5; }
        QPushButton:pressed { background-color: #7B6295; }
    """)
    parent.align_btn.clicked.connect(parent.execute_align)
    layout.addWidget(parent.align_btn)
    
    # Separator within Align group
    layout.addSpacing(dpi(8))
    separator3 = QtWidgets.QFrame()
    separator3.setFrameShape(QtWidgets.QFrame.HLine)
    separator3.setStyleSheet("background-color: #4D3A4D; max-height: 1px; margin: 0px;")
    layout.addWidget(separator3)
    layout.addSpacing(dpi(8))
    
    # Align Range row
    align_range_row = QtWidgets.QWidget()
    align_range_row_layout = QtWidgets.QHBoxLayout(align_range_row)
    align_range_row_layout.setContentsMargins(0, 0, 0, 0)
    align_range_row_layout.setSpacing(dpi(6))
    
    parent.align_range_translate_btn = QtWidgets.QPushButton("Align (Range)\n(Translate)")
    parent.align_range_translate_btn.setMinimumHeight(dpi(38))
    parent.align_range_translate_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A47;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 7pt;
            font-weight: 700;
            line-height: 1.1;
        }
        QPushButton:hover { background-color: #4D3A57; }
        QPushButton:pressed { background-color: #2D1A37; }
    """)
    parent.align_range_translate_btn.clicked.connect(parent.execute_align_range_translate)
    align_range_row_layout.addWidget(parent.align_range_translate_btn)
    
    parent.align_range_rotate_btn = QtWidgets.QPushButton("Align (Range)\n(Rotate)")
    parent.align_range_rotate_btn.setMinimumHeight(dpi(38))
    parent.align_range_rotate_btn.setStyleSheet("""
        QPushButton {
            background-color: #3D2A47;
            border: none;
            color: white;
            border-radius: 5px;
            font-size: 7pt;
            font-weight: 700;
            line-height: 1.1;
        }
        QPushButton:hover { background-color: #4D3A57; }
        QPushButton:pressed { background-color: #2D1A37; }
    """)
    parent.align_range_rotate_btn.clicked.connect(parent.execute_align_range_rotate)
    align_range_row_layout.addWidget(parent.align_range_rotate_btn)
    
    layout.addWidget(align_range_row)
    
    layout.addSpacing(dpi(6))
    
    # Align Range button
    parent.align_range_btn = QtWidgets.QPushButton("Align (Range)")
    parent.align_range_btn.setMinimumHeight(dpi(38))
    parent.align_range_btn.setStyleSheet("""
        QPushButton {
            background-color: #8B72A5;
            border: none;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 8pt;
            font-weight: 700;
        }
        QPushButton:hover { background-color: #9B82B5; }
        QPushButton:pressed { background-color: #7B6295; }
    """)
    parent.align_range_btn.clicked.connect(parent.execute_align_range)
    layout.addWidget(parent.align_range_btn)
    
    layout.addStretch()
    return tab
