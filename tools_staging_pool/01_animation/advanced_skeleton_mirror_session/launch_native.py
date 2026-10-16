"""Run this file to open the native-Mirror adapter; no scene edits on import."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    here = Path(__file__).resolve().parent
    root = next(p for p in here.parents if (p / 'maya_toolkit/framework/base_tool.py').is_file())
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from maya_toolkit.tools.advanced_skeleton_mirror import AdvancedSkeletonMirrorTool
    return AdvancedSkeletonMirrorTool()


if __name__ == '__main__':
    load_tool().show_ui()
