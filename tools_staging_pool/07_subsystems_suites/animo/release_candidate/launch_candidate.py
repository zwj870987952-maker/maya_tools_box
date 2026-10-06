"""Explicit staging loader. Does not register or execute Animo on import."""
import importlib.util
from pathlib import Path
import sys


def load_tool(register_for_session=False):
    project = Path(__file__).resolve().parents[4]
    if str(project) not in sys.path:
        sys.path.insert(0, str(project))
    import maya_toolkit.tools
    from maya_toolkit.framework import ToolRegistry
    name = 'maya_toolkit.tools.animo_candidate'
    path = Path(__file__).parent / 'maya_toolkit/tools/animo/__init__.py'
    module = sys.modules.get(name)
    if module is not None:
        if Path(module.__file__).resolve() != path.resolve():
            raise RuntimeError('另一候选目录已加载，请重启 Maya')
    else:
        spec = importlib.util.spec_from_file_location(name, path, submodule_search_locations=[str(path.parent)])
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            for key in list(sys.modules):
                if key == name or key.startswith(name + '.'):
                    sys.modules.pop(key, None)
            raise
    tool = module.AnimoTool()
    if register_for_session:
        existing = ToolRegistry.get(tool.tool_id)
        if existing is not None and existing.__class__ is not tool.__class__:
            raise RuntimeError('同名正式/其他候选工具已注册，拒绝覆盖')
        ToolRegistry.register(tool)
    return tool


def show_ui():
    return load_tool().show_ui()


if __name__ == '__main__':
    show_ui()
