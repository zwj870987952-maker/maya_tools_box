"""Load only this candidate; production registry remains unchanged."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    root = Path(__file__).resolve().parent
    repo = next(parent for parent in root.parents if (parent / 'maya_toolkit/framework/base_tool.py').is_file())
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    name = 'staging_animation_retarget_candidate'
    # Keep a displayed Qt window's module alive; users close/restart Maya after edits.
    if name in sys.modules:
        return sys.modules[name].AnimationRetargetTool()
    package = root / 'maya_toolkit/tools/animation_retarget'
    spec = importlib.util.spec_from_file_location(name, package / '__init__.py', submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module.AnimationRetargetTool()


if __name__ == '__main__':
    load_tool().show_ui()
