from pathlib import Path
import os
import uuid
import json
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

PROPS={'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'hide_original':{'type':'boolean','default':True}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(kwargs); p.setdefault('hide_original',True)
    if type(p['hide_original']) is not bool: raise ValueError('hide_original requires bool')
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(set(p['objects']))!=len(p['objects'])): raise ValueError('Unique nonempty object names required')
    return p


def plan(p):
    from maya import cmds
    from maya.api import OpenMaya as om
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    values=p.get('objects') or cmds.ls(selection=True,long=True) or []
    if not values: raise ValueError('Select explicit gpuCache shapes or parents')
    shapes=[]; selected_ids=set()
    for value in values:
        if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Unique explicit whole node required')
        matches=cmds.ls(value,long=True) or []
        if len(matches)!=1: raise ValueError('Missing/ambiguous target: '+value)
        uid=cmds.ls(matches[0],uuid=True)[0]
        if uid in selected_ids: raise ValueError('Aliased duplicate objects')
        selected_ids.add(uid)
        if cmds.nodeType(matches[0])=='gpuCache': found=matches
        elif cmds.objectType(matches[0],isAType='transform'): found=cmds.ls(matches[0],dag=True,leaf=True,shapes=True,long=True,type='gpuCache') or []
        else: raise ValueError('Expected gpuCache shape or transform')
        shapes.extend(found)
    if not shapes: raise ValueError('No gpuCache leaf shapes found in explicit scope')
    if len(set(shapes))!=len(shapes): raise ValueError('Overlapping parent/shape scopes contain duplicate cache')
    try: loaded=cmds.pluginInfo('AbcImport',query=True,loaded=True)
    except RuntimeError: loaded=False
    if not loaded: raise ValueError('AbcImport must already be loaded explicitly; preflight does not load plugins')
    tasks=[]
    for shape in shapes:
        parents=cmds.listRelatives(shape,parent=True,fullPath=True) or []
        if len(parents)!=1: raise ValueError('gpuCache requires unique parent')
        parent=parents[0]
        for node in (shape,parent):
            selection=om.MSelectionList(); selection.add(node); obj=selection.getDependNode(0)
            if len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('True DAG instance unsupported')
            if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True) or []): raise ValueError('Referenced/locked cache or parent')
        if p['hide_original'] and (cmds.getAttr(shape+'.visibility',lock=True) or cmds.listConnections(shape+'.visibility',source=True,destination=False)): raise ValueError('Original cache visibility locked or driven')
        raw=cmds.getAttr(shape+'.cacheFileName')
        path=Path(os.path.expandvars(raw)).expanduser()
        if not path.is_absolute(): path=Path(cmds.workspace(query=True,rootDirectory=True))/path
        path=path.resolve()
        if path.suffix.lower()!='.abc' or not path.is_file(): raise ValueError('Cache file missing/not .abc: '+str(path))
        tasks.append({'shape':shape,'parent':parent,'shape_uuid':cmds.ls(shape,uuid=True)[0],'parent_uuid':cmds.ls(parent,uuid=True)[0],'path':str(path),'original_visibility':cmds.getAttr(shape+'.visibility'),'bytes':path.stat().st_size})
    return {'tasks':tasks,'hide_original':p['hide_original'],'scope':'Import entire Alembic file once per gpuCache as original; cacheGeomPath not used','external_file_write':False,'native_import_undo':'Requires actual importer check; native command may differ by Maya version','gui_acceptance':'not_run'}


def ids():
    from maya import cmds
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True)}


def execute_native(p,validated_scope=None):
    from maya import cmds
    scope=validated_scope if validated_scope is not None else plan(p)
    before=ids(); selection=cmds.ls(selection=True,long=True) or []
    time=cmds.currentTime(query=True); ns=cmds.namespaceInfo(currentNamespace=True); auto=cmds.autoKeyframe(query=True,state=True)
    results=[]; holders=[]
    try:
        cmds.autoKeyframe(state=False); cmds.namespace(setNamespace=':')
        for task in scope['tasks']:
            prefix='mtbGpuImport_'+uuid.uuid4().hex[:12]
            cmds.namespace(add=prefix); cmds.namespace(setNamespace=prefix)
            holder=cmds.group(empty=True,name='importHolder'); holders.append(cmds.ls(holder,uuid=True)[0])
            holder=(cmds.ls(holder,long=True) or [None])[0]
            old=ids()
            cmds.AbcImport(task['path'],mode='import',reparent=holder)
            new=ids()-old
            children=cmds.listRelatives(holder,children=True,fullPath=True) or []
            if not children: raise RuntimeError('Alembic contained no importable DAG objects')
            parent=(cmds.ls(task['parent_uuid'],long=True) or [None])[0]
            if not parent: raise RuntimeError('Cache parent disappeared during native import')
            roots=cmds.parent(children,parent,relative=True)
            cmds.delete(holder); holders.pop(); cmds.namespace(setNamespace=':')
            results.append({'cache':task['shape'],'path':task['path'],'namespace':prefix,'roots':cmds.ls(roots,long=True),'imported_uuids':sorted(new)})
        if p['hide_original']:
            for task in scope['tasks']:
                shape=(cmds.ls(task['shape_uuid'],long=True) or [None])[0]
                if not shape: raise RuntimeError('Original gpuCache disappeared')
                cmds.setAttr(shape+'.visibility',0)
        return {'imports':results,'created_uuids':sorted(ids()-before),'hidden_original':p['hide_original'],'external_file_write':False,'gui_acceptance':'not_run'}
    except Exception:
        # Delete only actual nodes created in this invocation; no suffix/glob
        # cleanup. Native importer failure may still require checking the scene.
        created=ids()-before
        names=[n for uid in created for n in cmds.ls(uid,long=True) or []]
        if names: cmds.delete(names)
        if p['hide_original']:
            for task in scope['tasks']:
                values=cmds.ls(task['shape_uuid'],long=True) or []
                if values: cmds.setAttr(values[0]+'.visibility',task['original_visibility'])
        raise
    finally:
        cmds.namespace(setNamespace=ns); cmds.autoKeyframe(state=auto); cmds.currentTime(time,edit=True)
        valid=[n for n in selection if cmds.objExists(n)]
        cmds.select(valid,replace=True) if valid else cmds.select(clear=True)


def execute_plan(p):
    from maya import cmds
    scope=plan(p)
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    path=Path(__file__).with_name('gpu_cache_undo_command.py').resolve()
    # Explicit execution loads only the self-contained candidate Undo command.
    # validate/dry_run never import/register plugins. Other command ownership
    # is rejected rather than taking over an already loaded candidate.
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbGpuCacheConvert' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path:
                raise RuntimeError('Another candidate owns mtbGpuCacheConvert; use fresh Maya session')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    value=cmds.mtbGpuCacheConvert(json.dumps(p))
    if isinstance(value,list) and len(value)==1: value=value[0]
    return json.loads(value)


class GpuCacheToMeshTool(BaseMayaTool):
    tool_id='gpu_cache_to_mesh'; tool_name='GPU缓存转实体'
    category='modeling_surfacing'; version='1.0-candidate.1'
    description='将所选gpuCache实际Alembic全文件导入原父级，可隐藏原cache；全部路径/实例/引用/锁预检，私有namespace导入与Undo。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs): return ToolResult.ok(data=execute_plan(normalize(kwargs)))

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        win='mtbGpuCacheToMesh'
        if cmds.window(win,exists=True): cmds.deleteUI(win)
        cmds.window(win,title=self.tool_name,widthHeight=(450,160)); cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='导入所选GPU缓存的完整Alembic文件到原父级')
        hide=cmds.checkBox(label='隐藏原GPU cache shape',value=True)
        def call(dry):
            result=self.run(hide_original=cmds.checkBox(hide,query=True,value=True),dry_run=dry)
            print(result.to_dict())
            if not result.success: cmds.warning(result.message)
        cmds.button(label='预检当前选择',command=lambda *_:call(True)); cmds.button(label='导入实体',command=lambda *_:call(False)); cmds.showWindow(win)
        return win
