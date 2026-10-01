"""One scene per child process; never opens source scenes in caller's Maya."""
import json
import importlib.util
from pathlib import Path
import sys
import traceback


def main():
    config=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
    sys.path.insert(0,config['runtime_root'])
    import maya.standalone
    maya.standalone.initialize(name='python')
    from maya import cmds
    try:
        cmds.file(config['scene'],open=True,force=True,executeScriptNodes=False,loadReferenceDepth='all',prompt=False)
        import maya_toolkit.tools
        package=Path(__file__).resolve().parent
        spec=importlib.util.spec_from_file_location('maya_toolkit.tools.abc_batch_exporter',package/'__init__.py',submodule_search_locations=[str(package)])
        module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
        result=module.ABCBatchExporterTool().run(**config['arguments']).to_dict()
    except Exception as exc: result={'success':False,'message':str(exc),'errors':[traceback.format_exc()]}
    Path(config['result']).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    # Process exit closes readers; no user plug-ins or caller scenes are unloaded.
    return 0 if result['success'] else 1


if __name__=='__main__': raise SystemExit(main())
