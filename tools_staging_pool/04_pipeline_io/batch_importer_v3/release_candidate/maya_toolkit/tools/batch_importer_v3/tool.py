"""Bounded batch file import/reference and exact whole-reference removal."""
import hashlib
import json
import math
from pathlib import Path
import re
from maya_toolkit.framework import BaseMayaTool,ToolResult

EXTENSIONS={'.ma':None,'.mb':None,'.fbx':'fbxmaya','.obj':'objExport','.abc':'AbcImport'}


def file_hash(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): digest.update(chunk)
    return digest.hexdigest()


def normalize(values):
    p=dict(action='inspect',items=None,objects=None,reference_nodes=None)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','import','reference','remove_reference'): raise ValueError('Invalid action')
    if p['action']=='remove_reference':
        if p['items'] is not None or (p['objects'] is not None and p['reference_nodes'] is not None): raise ValueError('Remove selects objects OR exact reference_nodes, not file items')
        for key in ('objects','reference_nodes'):
            if p[key] is not None and (not isinstance(p[key],list) or not p[key] or any(not isinstance(n,str) or not n or any(c in n for c in '*?\n\r') for n in p[key]) or len(set(p[key]))!=len(p[key])): raise ValueError('Unique exact removal scope required')
    else:
        if p['objects'] is not None or p['reference_nodes'] is not None: raise ValueError('Removal-only scope')
        if not isinstance(p['items'],list) or not p['items']: raise ValueError('Nonempty file items required')
        total=0
        for row in p['items']:
            if not isinstance(row,dict) or set(row)-{'path','count','namespace'} or 'path' not in row: raise ValueError('Each item needs path/count/namespace only')
            if not isinstance(row['path'],str) or not Path(row['path']).is_absolute() or Path(row['path']).suffix.lower() not in EXTENSIONS: raise ValueError('Supported absolute file path required')
            count=row.get('count',1)
            if type(count) is not int or not 1<=count<=9999: raise ValueError('Count must be 1..9999 integer')
            if 'namespace' in row and (not isinstance(row['namespace'],str) or not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',row['namespace'])): raise ValueError('Simple namespace required')
            total+=count
        if total>10000: raise ValueError('Batch exceeds 10000 instances')
    return p


def namespace_base(path):
    name=re.sub('[^A-Za-z0-9_]','_',Path(path).stem)
    return name if name and not name[0].isdigit() else 'file_'+name


def references(p):
    from maya import cmds
    nodes=p['reference_nodes']
    if nodes is None:
        objects=p['objects'] if p['objects'] is not None else (cmds.ls(selection=True,long=True) or [])
        if not objects: raise ValueError('Select referenced objects or provide exact reference nodes')
        nodes=[]
        for obj in objects:
            names=cmds.ls(obj,long=True) or []
            if len(names)!=1 or not cmds.referenceQuery(names[0],isNodeReferenced=True): raise ValueError('Every target must belong to a reference: '+obj)
            node=cmds.referenceQuery(names[0],referenceNode=True)
            if node not in nodes: nodes.append(node)
    rows=[]
    for name in nodes:
        matches=cmds.ls(name,type='reference') or []
        if len(matches)!=1 or matches[0]=='sharedReferenceNode': raise ValueError('Exact file reference required')
        node=matches[0]
        if cmds.referenceQuery(node,parent=True,referenceNode=True): raise ValueError('Nested reference removal unsupported; explicitly select a top-level file reference')
        if cmds.referenceQuery(node,child=True,referenceNode=True): raise ValueError('Reference contains nested child references; automatic whole-reference restoration unsupported')
        if cmds.referenceQuery(node,editStrings=True): raise ValueError('Edited reference cannot be restored faithfully; remove edits explicitly or use original Maya reference workflow')
        # Native Maya locks reference metadata nodes by default. File removal is
        # the supported operation and does not need unlocking that metadata.
        path=cmds.referenceQuery(node,filename=True,withoutCopyNumber=True)
        if not Path(path).is_file(): raise ValueError('Reference source unavailable for Undo restore')
        namespace=cmds.referenceQuery(node,namespace=True).lstrip(':')
        if ':' in namespace: raise ValueError('Nested namespace reference unsupported')
        loaded=cmds.referenceQuery(node,isLoaded=True)
        rows.append({'reference_node':node,'uuid':cmds.ls(node,uuid=True)[0],'path':path,'sha256':file_hash(path),'namespace':namespace,
                     'loaded':loaded,'node_locked':bool(cmds.lockNode(node,query=True,lock=True)[0]),'nodes':(cmds.referenceQuery(node,nodes=True,dagPath=True) or []) if loaded else []})
    return rows


def plan(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Maya Undo must be enabled')
    if p['action']=='remove_reference': return {'references':references(p),'whole_file_reference_removal':True}
    tasks=[]; names=set()
    for item in p['items']:
        path=Path(item['path']).resolve()
        if not path.is_file(): raise ValueError('Missing input file: '+str(path))
        base=item.get('namespace',namespace_base(path)); digest=file_hash(path)
        for index in range(item.get('count',1)):
            namespace=base if index==0 else base+str(index)
            if namespace in names or cmds.namespace(exists=':'+namespace): raise ValueError('Namespace collision; choose explicit unique base: '+namespace)
            names.add(namespace); tasks.append({'path':str(path),'namespace':namespace,'sha256':digest,'plugin':EXTENSIONS[path.suffix.lower()]})
    return {'tasks':tasks,'count':len(tasks),'whole_file_reference_removal':False}


def identities():
    from maya import cmds
    return {cmds.ls(n,uuid=True)[0] for n in cmds.ls(long=True) or []}


def create_reference(row,restore=False):
    from maya import cmds
    if not Path(row['path']).is_file() or file_hash(row['path'])!=row['sha256']: raise RuntimeError('Reference source changed/unavailable; cannot restore exact source')
    namespace=':'+row['namespace']
    if cmds.namespace(exists=namespace):
        if cmds.namespaceInfo(namespace,listOnlyDependencyNodes=True): raise RuntimeError('Reference namespace contains foreign nodes')
        cmds.namespace(removeNamespace=namespace)
    previous=set(cmds.ls(type='reference') or [])
    cmds.file(row['path'],reference=True,namespace=row['namespace'],mergeNamespacesOnClash=False,executeScriptNodes=False,deferReference=not row.get('loaded',True))
    added=set(cmds.ls(type='reference') or [])-previous
    top=[n for n in added if n!='sharedReferenceNode' and not cmds.referenceQuery(n,parent=True,referenceNode=True)]
    if len(top)!=1: raise RuntimeError('Expected one top-level reference')
    node=top[0]
    if restore and node!=row['reference_node']:
        if cmds.objExists(row['reference_node']): raise RuntimeError('Old reference node name occupied')
        # Only the newly created RN is unlocked, never an existing user RN.
        cmds.lockNode(node,lock=False)
        node=cmds.rename(node,row['reference_node'])
    if restore: cmds.lockNode(node,lock=row.get('node_locked',True))
    return {'reference_node':node,'uuid':cmds.ls(node,uuid=True)[0],'path':row['path'],'sha256':row['sha256'],'namespace':row['namespace'],'loaded':row.get('loaded',True),'node_locked':bool(cmds.lockNode(node,query=True,lock=True)[0])}


def native_operation(p,scope):
    from maya import cmds
    selected=cmds.ls(selection=True,long=True) or []; current=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
    namespace=cmds.namespaceInfo(currentNamespace=True,absoluteName=True); before=identities(); outputs=[]
    try:
        cmds.namespace(setNamespace=':')
        if auto: cmds.autoKeyframe(state=False)
        if p['action']=='remove_reference':
            for row in scope['references']: cmds.file(referenceNode=row['reference_node'],removeReference=True)
            return {'references':scope['references'],'removed':True}
        for task in scope['tasks']:
            if task['plugin'] and not cmds.pluginInfo(task['plugin'],query=True,loaded=True): cmds.loadPlugin(task['plugin'],quiet=True)
            if p['action']=='reference': outputs.append(create_reference(task))
            else:
                old=identities()
                cmds.file(task['path'],i=True,namespace=task['namespace'],mergeNamespacesOnClash=False,executeScriptNodes=False,removeDuplicateNetworks=False)
                outputs.append({'path':task['path'],'namespace':task['namespace'],'created_uuids':sorted(identities()-old)})
        return {'imports':outputs,'created_uuids':sorted(identities()-before),'namespaces':[r['namespace'] for r in outputs],'mode':p['action']}
    except Exception:
        if p['action']=='import':
            nodes=[n for identity in identities()-before for n in cmds.ls(identity,long=True) or []]
            if nodes: cmds.delete(nodes)
        elif p['action']=='reference':
            for row in reversed(outputs):
                if cmds.objExists(row['reference_node']): cmds.file(referenceNode=row['reference_node'],removeReference=True)
        raise
    finally:
        cmds.namespace(setNamespace=namespace if cmds.namespace(exists=namespace) else ':')
        if cmds.currentTime(query=True)!=current: cmds.currentTime(current)
        valid=[n for n in selected if cmds.objExists(n)]
        if (cmds.ls(selection=True,long=True) or [])!=valid: cmds.select(valid,replace=True) if valid else cmds.select(clear=True)
        if cmds.autoKeyframe(query=True,state=True)!=auto: cmds.autoKeyframe(state=auto)


def execute_operation(p):
    from maya import cmds
    path=Path(__file__).with_name('batch_file_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbBatchFileOperation' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path: raise ValueError('Another package owns batch command; restart Maya')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    result=cmds.mtbBatchFileOperation(json.dumps(p))
    if isinstance(result,list) and len(result)==1: result=result[0]
    return json.loads(result)


class BatchImporterV3Tool(BaseMayaTool):
    tool_id='batch_importer_v3'; tool_name='批量导入与引用 V3'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Repeated .ma/.mb/.fbx/.obj/.abc import/reference with exact planned namespaces, recursive file UI, and whole-reference removal preflight.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','import','reference','remove_reference'],'default':'inspect'},
        'items':{'type':'array','minItems':1,'items':{'type':'object','additionalProperties':False,'required':['path'],'properties':{'path':{'type':'string'},'count':{'type':'integer','minimum':1,'maximum':9999,'default':1},'namespace':{'type':'string','pattern':'^[A-Za-z_][A-Za-z0-9_]*$'}}}},
        'objects':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},'reference_nodes':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True}}}

    def validate(self,**values):
        try: return ToolResult.ok(message='All batch rows preflight passed',data=plan(normalize(values)))
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**values):
        p=normalize(values)
        if p['action']=='inspect': return ToolResult.ok(message='Batch inspected',data=plan(p))
        return ToolResult.ok(message='Batch file operation completed',data=execute_operation(p))

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui()
