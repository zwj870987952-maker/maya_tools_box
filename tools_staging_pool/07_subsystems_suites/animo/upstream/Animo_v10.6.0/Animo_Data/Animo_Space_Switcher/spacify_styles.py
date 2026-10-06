from __future__ import print_function, division, absolute_import

from dpi_scale import dpi


def get_tab_style(selected, tab_index=None):
    padding_v = dpi(4)
    padding_h = dpi(8)
    
    # Tab 0: Spaces - Blue
    # Tab 1: Offset - Teal Blue
    
    if tab_index == 1:
        # Offset tab - Teal blue
        if selected:
            return """
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: #1E88A8;
                    border-bottom: 2px solid #1E88A8;
                    font-size: 9pt;
                    font-weight: 700;
                    padding: {0}px {1}px;
                }}
                QPushButton:hover {{
                    color: #2898B8;
                }}
            """.format(padding_v, padding_h)
        else:
            return """
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: #888888;
                    border-bottom: 2px solid transparent;
                    font-size: 9pt;
                    font-weight: 700;
                    padding: {0}px {1}px;
                }}
                QPushButton:hover {{
                    color: #1E88A8;
                }}
            """.format(padding_v, padding_h)
    
    # Default / Tab 0: Spaces - Blue
    if selected:
        return """
            QPushButton {{
                background-color: transparent;
                border: none;
                color: #1565C0;
                border-bottom: 2px solid #1565C0;
                font-size: 9pt;
                font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{
                color: #1976D2;
            }}
        """.format(padding_v, padding_h)
    else:
        return """
            QPushButton {{
                background-color: transparent;
                border: none;
                color: #888888;
                border-bottom: 2px solid transparent;
                font-size: 9pt;
                font-weight: 700;
                padding: {0}px {1}px;
            }}
            QPushButton:hover {{
                color: #CCCCCC;
            }}
        """.format(padding_v, padding_h)
