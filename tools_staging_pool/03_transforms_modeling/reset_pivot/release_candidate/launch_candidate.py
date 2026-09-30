# -*- coding: utf-8 -*-
"""Load the candidate package without registering it in the production registry."""
from __future__ import absolute_import, division, print_function

import os
import sys


def load_tool():
    root = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.abspath(os.path.join(root, "..", "..", "..", ".."))
    if repo not in sys.path:
        sys.path.insert(0, repo)
    package_dir = os.path.join(root, "maya_toolkit", "tools", "reset_pivot")
    name = "staging_reset_pivot_candidate"
    for module_name in list(sys.modules):
        if module_name == name or module_name.startswith(name + "."):
            del sys.modules[module_name]
    if sys.version_info[0] >= 3:
        import importlib.util
        spec = importlib.util.spec_from_file_location(name, os.path.join(package_dir, "__init__.py"), submodule_search_locations=[package_dir])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    else:
        import imp
        module = imp.load_module(name, None, package_dir, ("", "", imp.PKG_DIRECTORY))
    return module.ResetPivotTool()


if __name__ == "__main__":
    load_tool().show_ui()
