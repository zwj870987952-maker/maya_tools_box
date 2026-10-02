import importlib
from pathlib import Path
import sys

def load_tool():
    root = str(Path(__file__).resolve().parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    return importlib.import_module('engine_toolkit.tools.maya_process_finder')

def run(dry_run=True, **kwargs):
    return load_tool().run(dry_run=dry_run, **kwargs)

def show_ui():
    return load_tool().show_ui()
