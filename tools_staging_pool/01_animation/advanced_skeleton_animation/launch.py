"""Compatibility launcher for the promoted tool."""
from pathlib import Path
import sys


def load_tool():
    root = next(p for p in Path(__file__).resolve().parents if (p/'maya_toolkit').is_dir())
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from maya_toolkit.framework import ToolRegistry
    return ToolRegistry.get('advanced_skeleton_animation')


if __name__ == '__main__':
    load_tool().show_ui()
