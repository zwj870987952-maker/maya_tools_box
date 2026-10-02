import importlib.util
import json
from pathlib import Path
import sys
import traceback
def main():
    data=json.loads(Path(sys.argv[1]).read_text(encoding='utf8')); sys.path.insert(0,data['runtime_root'])
    import maya.standalone
    maya.standalone.initialize(name='python')
    from maya import cmds
    cmds.undoInfo(state=True)
    import maya_toolkit.tools
    package=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('maya_toolkit.tools.replace_references',package/'__init__.py',submodule_search_locations=[str(package)])
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    try: result=module.process_one(data['parameters'],data['task'],data['rules'])
    except Exception as exc: result={'source':data['task']['source'],'success':False,'message':str(exc),'traceback':traceback.format_exc()}
    Path(data['result']).write_text(json.dumps(result,ensure_ascii=False),encoding='utf8'); return 0 if result['success'] else 1
if __name__=='__main__': raise SystemExit(main())
