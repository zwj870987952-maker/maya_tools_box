"""Load the candidate canonical package without changing the production registry."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    candidate = Path(__file__).resolve().parent
    repo = next(parent for parent in candidate.parents if (parent / 'maya_toolkit/framework/base_tool.py').is_file())
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    import maya_toolkit.tools as parent
    name = 'maya_toolkit.tools.animirror_v2_0'
    package = candidate / 'maya_toolkit/tools/animirror_v2_0'
    if name in sys.modules:
        module = sys.modules[name]
        if Path(module.__file__).resolve().parent != package.resolve():
            raise RuntimeError('其他位置的 AniMirror 适配包已加载，请先关闭窗口并重启 Maya')
        return module.AnimirrorV2Tool()
    spec = importlib.util.spec_from_file_location(name, package / '__init__.py', submodule_search_locations=[str(package)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    setattr(parent, 'animirror_v2_0', module)
    return module.AnimirrorV2Tool()


if __name__ == '__main__':
    load_tool().show_ui()
