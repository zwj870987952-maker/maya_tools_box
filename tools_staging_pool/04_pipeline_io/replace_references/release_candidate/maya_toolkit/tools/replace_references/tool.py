"""Current-scene exact reference replacement and isolated saved batch outputs."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from maya_toolkit.framework import BaseMayaTool,ToolResult

def file_hash(path):
    sha=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): sha.update(chunk)
    return sha.hexdigest()
def path(value):
    if not isinstance(value,str) or not Path(value).is_absolute() or Path(value).suffix.lower() not in ('.ma','.mb') or not Path(value).is_file(): raise ValueError('Existing absolute .ma/.mb path required')
    return str(Path(value).resolve())
def exact_list(value):
    if not isinstance(value,list) or not value or any(not isinstance(n,str) or not n or any(c in n for c in '*?\n\r') for n in value) or len(set(value))!=len(value): raise ValueError('Unique exact node/UUID list required')
def normalize(values):
    p=dict(action='inspect',reference_nodes=None,objects=None,new_file=None,rename_namespace=True,files=None,rules=None,output_dir=None,timeout=180)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','replace','batch_inspect','batch'): raise ValueError('Invalid action')
    if type(p['rename_namespace']) is not bool or type(p['timeout']) is not int or not 10<=p['timeout']<=3600: raise ValueError('Boolean rename and timeout10..3600 required')
    if p['action'] in ('batch','batch_inspect'):
        if p['reference_nodes'] is not None or p['objects'] is not None or p['new_file'] is not None: raise ValueError('Batch uses files/rules only')
        if not isinstance(p['files'],list) or not 1<=len(p['files'])<=1000: raise ValueError('1..1000 scene files required')
        p['files']=[path(v) for v in p['files']]
        if len({v.casefold() for v in p['files']})!=len(p['files']): raise ValueError('Duplicate source file')
        if not isinstance(p['rules'],list) or not p['rules'] or len(p['rules'])>1000: raise ValueError('Nonempty replacement rules required')
        rows=[]
        for row in p['rules']:
            if not isinstance(row,dict) or set(row)!={'source_contains','target'} or not isinstance(row['source_contains'],str) or not row['source_contains']: raise ValueError('Rule requires nonempty literal source_contains and target')
            rows.append({'source_contains':row['source_contains'],'target':path(row['target'])})
        p['rules']=rows
        if not isinstance(p['output_dir'],str) or not Path(p['output_dir']).is_absolute() or not Path(p['output_dir']).is_dir(): raise ValueError('Existing absolute batch output directory required')
    else:
        if p['files'] is not None or p['rules'] is not None or p['output_dir'] is not None: raise ValueError('Current scene uses references/new_file only')
        if p['reference_nodes'] is not None and p['objects'] is not None: raise ValueError('Exact reference nodes OR objects')
        for key in ('reference_nodes','objects'):
            if p[key] is not None: exact_list(p[key])
        p['new_file']=path(p['new_file'])
    return p

def references(p):
    from maya import cmds
    from .reference_ops import references as eligible
    nodes=p['reference_nodes']
    if nodes is None:
        nodes=[]
        objects=p['objects'] if p['objects'] is not None else cmds.ls(selection=True,long=True) or []
        if not objects: raise ValueError('Select referenced objects/reference nodes')
        for obj in objects:
            names=cmds.ls(obj,long=True) or []
            if len(names)!=1 or '.' in names[0]: raise ValueError('Exact referenced scene node required')
            if cmds.nodeType(names[0])=='reference': node=names[0]
            elif cmds.referenceQuery(names[0],isNodeReferenced=True): node=cmds.referenceQuery(names[0],referenceNode=True)
            else: raise ValueError('Non-reference target: '+obj)
            if node not in nodes: nodes.append(node)
    return eligible({'reference_nodes':nodes})

def current_plan(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Maya Undo')
    rows=references(p); target_hash=file_hash(p['new_file']); reserved=set()
    base=re.sub('[^A-Za-z0-9_]','_',Path(p['new_file']).stem)
    if not base or base[0].isdigit(): base='asset_'+base
    for row in rows:
        desired=row['namespace']
        if p['rename_namespace']:
            for node in cmds.namespaceInfo(':'+row['namespace'],listOnlyDependencyNodes=True,recurse=True) or []:
                if not cmds.referenceQuery(node,isNodeReferenced=True) or cmds.referenceQuery(node,referenceNode=True)!=row['reference_node']: raise ValueError('Namespace contains local/other-reference nodes; rename would move unrelated nodes')
            desired=base; index=1
            while desired in reserved or (cmds.namespace(exists=':'+desired) and desired!=row['namespace']): desired=base+str(index); index+=1
        reserved.add(desired); row.update(new_file=p['new_file'],new_sha256=target_hash,new_namespace=desired)
    return {'references':rows,'whole_file_reference_replacement':True,'namespace_rename':p['rename_namespace']}

def matching_mayapy():
    location=os.environ.get('MAYA_LOCATION'); exe=Path(location)/'bin/mayapy.exe' if location and os.name=='nt' else Path(sys.executable).with_name('mayapy.exe' if os.name=='nt' else 'mayapy')
    if not exe.is_file(): raise ValueError('Matching mayapy unavailable')
    return str(exe)

def batch_plan(p):
    rows=[]; used=set()
    for source in p['files']:
        src=Path(source); identity=hashlib.sha256(str(src).casefold().encode('utf8')).hexdigest()[:8]
        target=Path(p['output_dir'])/(src.stem+'__'+identity+src.suffix)
        if target.exists() or target.is_symlink() or str(target).casefold() in used: raise ValueError('Batch output exists/collides: '+str(target))
        used.add(str(target).casefold()); rows.append({'source':source,'sha256':file_hash(source),'output':str(target)})
    rules=[dict(row,sha256=file_hash(row['target'])) for row in p['rules']]
    return {'tasks':rows,'rules':rules,'mayapy':matching_mayapy(),'scope':'child validates actual matched references after opening each source','caller_scene_preserved':True}

def plan(p): return batch_plan(p) if p['action'] in ('batch','batch_inspect') else current_plan(p)

def load_row(row,direction):
    from maya import cmds
    names=cmds.ls(row['uuid'],type='reference') or []
    if len(names)!=1: raise RuntimeError('Reference identity missing/replaced')
    node=names[0]; source=row['path'] if direction=='old' else row['new_file']; expected=row['sha256'] if direction=='old' else row['new_sha256']; namespace=row['namespace'] if direction=='old' else row['new_namespace']
    if file_hash(source)!=expected: raise RuntimeError('Reference source changed/unavailable')
    cmds.file(source,loadReference=node,loadReferenceDepth='all' if row['loaded'] else 'none',executeScriptNodes=False,prompt=False)
    current=cmds.referenceQuery(node,namespace=True).lstrip(':')
    if current!=namespace:
        reference_file=cmds.referenceQuery(node,filename=True)  # Keep copy number for repeated files.
        cmds.file(reference_file,edit=True,namespace=namespace)
    if not row['loaded'] and cmds.referenceQuery(node,isLoaded=True): cmds.file(unloadReference=node)

def operation(p):
    from maya import cmds
    plugin_path=Path(__file__).with_name('replace_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbReplaceReferences' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=plugin_path: raise ValueError('Other package owns replace command; restart Maya')
            break
    else: cmds.loadPlugin(str(plugin_path),quiet=True)
    value=cmds.mtbReplaceReferences(json.dumps(p)); return json.loads(value[0] if isinstance(value,list) else value)

def save_output(target):
    from maya import cmds
    import shutil
    target=Path(target); target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mtb_replaced_',dir=str(target.parent)) as directory:
        generated=Path(directory)/('scene'+target.suffix); cmds.file(rename=str(generated)); cmds.file(save=True,type='mayaBinary' if target.suffix.lower()=='.mb' else 'mayaAscii',force=True)
        owned=False
        try:
            with target.open('xb') as writer:
                owned=True
                with generated.open('rb') as reader: shutil.copyfileobj(reader,writer)
                writer.flush(); os.fsync(writer.fileno())
        except Exception:
            if owned: target.unlink(missing_ok=True)
            raise
    return {'path':str(target),'bytes':target.stat().st_size}

def process_one(p,task,rules):
    from maya import cmds
    if file_hash(task['source'])!=task['sha256']: raise RuntimeError('Batch source changed since preflight')
    for rule in rules:
        if file_hash(rule['target'])!=rule['sha256']: raise RuntimeError('Rule target changed since preflight')
    cmds.file(task['source'],open=True,force=True,executeScriptNodes=False,prompt=False)
    operations=[]
    for node in cmds.ls(type='reference') or []:
        if node=='sharedReferenceNode': continue
        source=cmds.referenceQuery(node,filename=True,withoutCopyNumber=True)
        matches=[rule for rule in rules if rule['source_contains'] in source]
        if len(matches)>1: raise ValueError('Reference matches multiple rules; ambiguous replacement: '+source)
        if matches:
            parameters=normalize({'action':'replace','reference_nodes':[node],'new_file':matches[0]['target'],'rename_namespace':p['rename_namespace']})
            operations.append((parameters,current_plan(parameters)))
    # Full child-scene preflight occurs before its first replacement.
    reserved=set()
    if p['rename_namespace']:
        for _,scope in operations:
            for row in scope['references']:
                base=re.sub('[^A-Za-z0-9_]','_',Path(row['new_file']).stem)
                if not base or base[0].isdigit(): base='asset_'+base
                desired=base; index=1
                while desired in reserved or (cmds.namespace(exists=':'+desired) and desired!=row['namespace']): desired=base+str(index); index+=1
                row['new_namespace']=desired; reserved.add(desired)
    namespaces=[r['new_namespace'] for _,scope in operations for r in scope['references']]
    if len(set(namespaces))!=len(namespaces): raise ValueError('Batch namespace targets collide; use rename_namespace=False or disambiguated assets')
    for _,scope in operations:
        for row in scope['references']: load_row(row,'new')
    output=save_output(task['output'])
    return {'source':task['source'],'replaced':sum(len(scope['references']) for _,scope in operations),'output':output,'success':True}

def batch(p,data):
    import maya_toolkit
    results=[]
    with tempfile.TemporaryDirectory(prefix='mtb_reference_batch_') as directory:
        for index,task in enumerate(data['tasks']):
            config=Path(directory)/('job'+str(index)+'.json'); output=Path(directory)/('result'+str(index)+'.json')
            config.write_text(json.dumps({'parameters':p,'task':task,'rules':data['rules'],'result':str(output),'runtime_root':str(Path(maya_toolkit.__file__).resolve().parent.parent)}),encoding='utf8')
            try:
                run=subprocess.run([data['mayapy'],str(Path(__file__).with_name('worker.py')),str(config)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=p['timeout'],env=dict(os.environ,PYTHONIOENCODING='utf-8'),creationflags=0x08000000 if os.name=='nt' else 0)
                row=json.loads(output.read_text(encoding='utf8')) if output.is_file() else {'source':task['source'],'success':False,'message':run.stdout.decode('utf8',errors='replace')[-3000:]}
                row['success']=bool(row.get('success')) and run.returncode==0
            except subprocess.TimeoutExpired: row={'source':task['source'],'success':False,'message':'Worker timed out; own temporary or completed output may remain'}
            results.append(row)
    return results

class ReplaceReferencesTool(BaseMayaTool):
    tool_id='replace_references'; tool_name='引用替换与批量场景替换'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Whole-file selected reference replacement, exact namespace rename and native Undo; isolated per-scene batch with literal rules and exclusive new outputs.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','replace','batch_inspect','batch'],'default':'inspect'},'reference_nodes':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},'objects':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},'new_file':{'type':'string'},'rename_namespace':{'type':'boolean','default':True},'files':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':1000},'rules':{'type':'array','minItems':1,'items':{'type':'object','additionalProperties':False,'required':['source_contains','target'],'properties':{'source_contains':{'type':'string','minLength':1},'target':{'type':'string'}}}},'output_dir':{'type':'string'},'timeout':{'type':'integer','minimum':10,'maximum':3600,'default':180}}}
    def validate(self,**values):
        try: return ToolResult.ok(message='Reference replacement preflight passed',data=plan(normalize(values)))
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])
    def execute(self,**values):
        p=normalize(values); data=plan(p)
        if p['action']=='replace': data=operation(p)
        elif p['action']=='batch':
            rows=batch(p,data); data={'scenes':rows,'caller_scene_preserved':True,'processed':len(rows)}
            if any(not row['success'] for row in rows): return ToolResult.fail(message='Batch contains failed scenes; successful new outputs retained',data=data,errors=[r.get('message','failed') for r in rows if not r['success']])
        return ToolResult.ok(message='Reference '+p['action']+' completed',data=data)
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui()
