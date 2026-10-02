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
    cmds.undoInfo(state=True); cmds.workspace(data['workspace'],openWorkspace=True); cmds.file(data['scene'],open=True,force=True,executeScriptNodes=False,prompt=False)
    import maya_toolkit.tools
    package=Path(__file__).resolve().parent; spec=importlib.util.spec_from_file_location('maya_toolkit.tools.vessel_fbx_exporter',package/'__init__.py',submodule_search_locations=[str(package)])
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    try: result=module.pipeline(data['parameters'],data['plan'])
    except Exception as exc: result={'success':False,'message':str(exc),'traceback':traceback.format_exc(),'completed_external_outputs_may_remain':True}
    Path(data['result']).write_text(json.dumps(result,ensure_ascii=False),encoding='utf8'); return 0 if result['success'] else 1
if __name__=='__main__': raise SystemExit(main())
