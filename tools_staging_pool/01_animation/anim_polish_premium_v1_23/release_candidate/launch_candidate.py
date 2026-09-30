"""Load a staged canonical package without production registration or sys.path vendor aliases."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    candidate = Path(__file__).resolve().parent
    repo = next(p for p in candidate.parents if (p/'maya_toolkit/framework/base_tool.py').is_file())
    if str(repo) not in sys.path:
        sys.path.insert(0,str(repo))
    import maya_toolkit.tools as parent
    name = 'maya_toolkit.tools.anim_polish_premium_v1_23'
    package = candidate/'maya_toolkit/tools/anim_polish_premium_v1_23'
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve()!=package/'__init__.py':
            raise RuntimeError('A different AnimPolish adapter is already loaded; use a fresh Maya session')
        return module.AnimPolishTool()
    spec = importlib.util.spec_from_file_location(name,package/'__init__.py',submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    setattr(parent,'anim_polish_premium_v1_23',module)
    spec.loader.exec_module(module)
    return module.AnimPolishTool()


if __name__=='__main__':
    load_tool().show_ui()
