"""Import canonical candidate without touching the production registry."""
import importlib.util
from pathlib import Path
import sys


def load_tool():
    root = Path(__file__).resolve().parents[4]
    sys.path.insert(0, str(root))
    import maya_toolkit.tools
    name = 'maya_toolkit.tools.back2origin_v05_gaiv3'
    path = Path(__file__).parent / 'maya_toolkit/tools/back2origin_v05_gaiv3/__init__.py'
    if name in sys.modules:
        if Path(sys.modules[name].__file__).resolve() != path.resolve():
            raise RuntimeError('另一个路径的 Back2Origin 已加载，请重启或明确卸载后再测试')
        module = sys.modules[name]
    else:
        spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=[str(path.parent)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return module.Back2OriginTool()
