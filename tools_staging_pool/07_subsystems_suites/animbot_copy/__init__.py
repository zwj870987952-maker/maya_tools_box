# animBot UI Clone for Autodesk Maya
import os
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
if PACKAGE_DIR not in sys.path:
    sys.path.insert(0, PACKAGE_DIR)

from .core.workspace_manager import WORKSPACE_MGR
from .launch import launch, close, toggle
from .ui.workspace_control import dock_to_location
from .ui.graph_editor_toolbar import attach_to_graph_editor

__all__ = ["launch", "close", "toggle", "dock_to_location", "attach_to_graph_editor", "WORKSPACE_MGR"]
