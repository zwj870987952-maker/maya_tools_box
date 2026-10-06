from __future__ import print_function, division, absolute_import

import os
import sys

def get_script_path():
    """Get the path to this script's directory."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(script_dir):
            return script_dir
    except:
        pass
    return None


script_dir = get_script_path()
if script_dir and script_dir not in sys.path:
    sys.path.insert(0, script_dir)


# Import and show UI
from attributes_space_switcher_ui import show_ui

show_ui()
