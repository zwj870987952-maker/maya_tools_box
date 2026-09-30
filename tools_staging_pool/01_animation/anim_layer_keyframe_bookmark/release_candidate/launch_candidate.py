# -*- coding: utf-8 -*-
"""Load the staged class without modifying the production registry."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    candidate = Path(__file__).resolve().parent
    repo = next(parent for parent in candidate.parents if (parent / "maya_toolkit/framework/base_tool.py").is_file())
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    name = "staging_anim_layer_keyframe_bookmark_candidate"
    for module in list(sys.modules):
        if module == name or module.startswith(name + "."):
            del sys.modules[module]
    package = candidate / "maya_toolkit/tools/anim_layer_keyframe_bookmark"
    spec = importlib.util.spec_from_file_location(name, package / "__init__.py", submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module.AnimLayerKeyframeBookmarkTool()


if __name__ == "__main__":
    load_tool().show_ui()
