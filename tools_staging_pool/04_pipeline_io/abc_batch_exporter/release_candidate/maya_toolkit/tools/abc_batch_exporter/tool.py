"""Native Alembic export and isolated scene-folder batch; no autorun."""
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
from maya_toolkit.framework import BaseMayaTool, ToolResult

FLAGS={'uv_write':'-uvWrite','world_space':'-worldSpace','write_uv_sets':'-writeUVSets','write_face_sets':'-writeFaceSets','write_visibility':'-writeVisibility','strip_namespaces':'-stripNamespaces','write_color_sets':'-writeColorSets'}


def number(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and abs(v)<1e9


def normalize(values):
    p=dict(action='inspect',objects=None,set_name=None,output=None,folder=None,output_dir=None,start=None,end=None,step=1.,options={},timeout=180)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','export','batch','materials'): raise ValueError('Invalid action')
    if p['objects'] is not None and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n or any(c in n for c in '*?"\n\r') for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))): raise ValueError('Unique safe DAG objects required')
    if p['set_name'] is not None and (not isinstance(p['set_name'],str) or not p['set_name'] or any(c in p['set_name'] for c in '*?.|"\n\r')): raise ValueError('Exact set name required')
    if p['objects'] is not None and p['set_name'] is not None: raise ValueError('Choose objects or set')
    if (p['start'] is None)!=(p['end'] is None) or (p['start'] is not None and (not number(p['start']) or not number(p['end']) or p['end']<p['start'])): raise ValueError('Invalid range')
    if not number(p['step']) or p['step']<=0: raise ValueError('Step must be positive finite')
    if type(p['timeout']) is not int or not 10<=p['timeout']<=3600: raise ValueError('Timeout 10..3600 seconds')
    if not isinstance(p['options'],dict) or set(p['options'])-set(FLAGS) or any(type(v) is not bool for v in p['options'].values()): raise ValueError('Invalid boolean export options')
    defaults={k:k not in ('strip_namespaces','write_color_sets') for k in FLAGS}
    if p['action']=='batch': defaults['write_color_sets']=True
    p['options']=dict(defaults,**p['options'])
    for key in ('output','folder','output_dir'):
        if p[key] is not None and (not isinstance(p[key],str) or not Path(p[key]).is_absolute() or any(c in p[key] for c in '"\n\r\x00')): raise ValueError('Safe absolute paths required')
    if p['action']=='batch':
        if p['folder'] is None or p['output_dir'] is None or p['objects'] is not None or p['output'] is not None: raise ValueError('Batch requires folder/output_dir, uses per-scene named set')
        if p['set_name'] is None: p['set_name']='abc_export'
    elif p['folder'] is not None or p['output_dir'] is not None: raise ValueError('Folder options only apply to batch')
    if p['action']=='export' and (p['output'] is None or Path(p['output']).suffix.lower()!='.abc'): raise ValueError('Explicit .abc output required')
    if p['action']=='materials' and any(k in values for k in ('output','start','end','step','options','timeout')): raise ValueError('Materials action only takes scene scope')
    return p


def quote(value):
    value=str(value).replace('\\','/')
    if any(c in value for c in '"\n\r\x00'): raise ValueError('Unsafe Alembic job token')
    return '"'+value+'"'


def roots(objects=None,set_name=None):
    from maya import cmds
    if set_name is not None:
        if not cmds.objExists(set_name) or cmds.nodeType(set_name)!='objectSet': raise ValueError('Missing named objectSet: '+set_name)
        names=cmds.sets(set_name,query=True) or []
    else: names=objects if objects is not None else (cmds.ls(selection=True,long=True) or [])
    if not names: raise ValueError('No members/objects; no fallback to unrelated selection')
    result=[]
    for name in names:
        if '.' in name or any(c in name for c in '*?"\n\r'): raise ValueError('Components/unsafe names unsupported')
        matches=cmds.ls(name,long=True) or []
        if len(matches)!=1: raise ValueError('Ambiguous/deleted member: '+name)
        n=matches[0]; kind=cmds.nodeType(n)
        if kind=='mesh': meshes=[n]
        elif kind in ('transform','joint'): meshes=cmds.listRelatives(n,allDescendents=True,type='mesh',fullPath=True) or []
        else: raise ValueError('Only mesh hierarchy supported: '+n)
        live=[shape for shape in meshes if not cmds.getAttr(shape+'.intermediateObject')]
        if not live: raise ValueError('No live mesh in member: '+n)
        for shape in live:
            owner=cmds.listRelatives(shape,parent=True,fullPath=True)[0]
            # Leaf owners prevent exporting unexpected cameras, rig subtrees or nested child meshes.
            if cmds.listRelatives(owner,children=True,type='transform',fullPath=True): raise ValueError('Mesh owner has child transforms; choose leaf mesh hierarchy')
            if owner not in result: result.append(owner)
    return result


def no_collision(nodes):
    from maya import cmds
    seen=set()
    for root in nodes:
        for node in [root]+(cmds.listRelatives(root,allDescendents=True,fullPath=True) or []):
            relative=node[len(root):].split('|')
            stripped=root.rsplit('|',1)[-1].rsplit(':',1)[-1]+'|'+ '|'.join(part.rsplit(':',1)[-1] for part in relative if part)
            if stripped in seen: raise ValueError('Namespace stripping causes DAG name collision')
            seen.add(stripped)


def unused_output(path):
    p=Path(path)
    if p.suffix.lower()!='.abc' or not p.parent.is_dir() or p.exists() or p.is_symlink(): raise ValueError('Output requires existing directory and unused .abc file: '+str(p))
    return p


def scene_plan(p):
    from maya import cmds
    nodes=roots(p['objects'],p['set_name'])
    if p['options']['strip_namespaces']: no_collision(nodes)
    start=cmds.playbackOptions(query=True,min=True) if p['start'] is None else p['start']
    end=cmds.playbackOptions(query=True,max=True) if p['end'] is None else p['end']
    if (end-start)/p['step']>99999: raise ValueError('Excessive sample count')
    if p['output'] is not None: unused_output(p['output'])
    return {'roots':nodes,'start':start,'end':end,'step':p['step'],'options':p['options'],'output':p['output']}


def make_job(data,output):
    tokens=['-frameRange',str(data['start']),str(data['end']),'-step',str(data['step'])]
    tokens += [flag for name,flag in FLAGS.items() if data['options'][name]]
    for n in data['roots']: tokens+=['-root',quote(n)]
    return ' '.join(tokens+['-file',quote(output)])


def mayapy():
    from maya import cmds
    location=Path(os.environ.get('MAYA_LOCATION',Path(cmds.about(environmentFile=True)).parent))
    executable=location/'bin'/('mayapy.exe' if os.name=='nt' else 'mayapy')
    if not executable.is_file():
        executable=Path(sys.executable).with_name('mayapy.exe' if os.name=='nt' else 'mayapy')
    if not executable.is_file(): raise ValueError('Maya mayapy executable unavailable')
    return executable


def batch_plan(p):
    folder=Path(p['folder']); output=Path(p['output_dir'])
    if not folder.is_dir() or not output.is_dir(): raise ValueError('Input/output directories must exist')
    files=sorted(f.resolve() for f in folder.iterdir() if f.is_file() and f.suffix.lower() in ('.ma','.mb'))
    if not 1<=len(files)<=1000: raise ValueError('Batch needs 1..1000 scene files')
    destinations=[str(unused_output(output/(f.stem+'.abc'))) for f in files]
    if len(set(n.casefold() for n in destinations))!=len(files): raise ValueError('Scene names collide at output, including .ma/.mb same stem')
    executable=mayapy()
    return {'scenes':[str(f) for f in files],'outputs':destinations,'mayapy':str(executable),'set_name':p['set_name'],'scene_contents_checked':False}


def export(data):
    from maya import cmds
    output=unused_output(data['output']); current=cmds.currentTime(query=True); selected=cmds.ls(selection=True,long=True) or []
    auto=cmds.autoKeyframe(query=True,state=True)
    try:
        if not cmds.pluginInfo('AbcExport',query=True,loaded=True): cmds.loadPlugin('AbcExport',quiet=True)
        if auto: cmds.autoKeyframe(state=False)
        with tempfile.TemporaryDirectory(prefix='mtb_abc_',dir=str(output.parent)) as directory:
            generated=Path(directory)/'export.abc'; cmds.AbcExport(j=make_job(data,generated),verbose=True)
            if not generated.is_file() or generated.stat().st_size<=0: raise RuntimeError('AbcExport produced no cache')
            # Exclusive create defeats races and never overwrites a pre-existing cache.
            owned=False
            try:
                with output.open('xb') as writer:
                    owned=True
                    with generated.open('rb') as reader: shutil.copyfileobj(reader,writer)
                    writer.flush(); os.fsync(writer.fileno())
            except Exception:
                if owned: output.unlink(missing_ok=True)
                raise
    finally:
        if cmds.currentTime(query=True)!=current: cmds.currentTime(current)
        if (cmds.ls(selection=True,long=True) or [])!=selected: cmds.select(selected,replace=True) if selected else cmds.select(clear=True)
        if cmds.autoKeyframe(query=True,state=True)!=auto: cmds.autoKeyframe(state=auto)
    return {'output':str(output),'bytes':output.stat().st_size,'roots':data['roots'],'start':data['start'],'end':data['end'],'step':data['step']}


class ABCBatchExporterTool(BaseMayaTool):
    tool_id='abc_batch_exporter'; tool_name='ABC模型与选择集批量导出'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Export native Alembic mesh roots, create separate Lambert materials, or process scene-folder abc_export sets in isolated mayapy workers.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','export','batch','materials'],'default':'inspect'},
        'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True,'minItems':1},'set_name':{'type':'string'},
        'output':{'type':'string','description':'Absolute unused .abc path'},'folder':{'type':'string'},'output_dir':{'type':'string'},
        'start':{'type':'number'},'end':{'type':'number'},'step':{'type':'number','exclusiveMinimum':0,'default':1},
        'timeout':{'type':'integer','minimum':10,'maximum':3600,'default':180},
        'options':{'type':'object','additionalProperties':False,'properties':{k:{'type':'boolean','default':k not in ('strip_namespaces','write_color_sets')} for k in FLAGS}}}}

    def validate(self,**values):
        try:
            p=normalize(values)
            if p['action']=='batch': data=batch_plan(p)
            elif p['action']=='materials':
                from maya import cmds
                from maya.api import OpenMaya as om
                nodes=roots(p['objects'],p['set_name'])
                for node in nodes:
                    for item in [node]+(cmds.listRelatives(node,shapes=True,fullPath=True) or []):
                        selected=om.MSelectionList(); selected.add(item)
                        if cmds.referenceQuery(item,isNodeReferenced=True) or any(cmds.lockNode(item,query=True,lock=True)) or len(om.MDagPath.getAllPathsTo(selected.getDagPath(0).node()))!=1: raise ValueError('Material assignment reference/lock/instance rejected')
                data={'roots':nodes}
            else: data=scene_plan(p)
            return ToolResult.ok(message='Alembic preflight passed',data=data,warnings=['Files/plugin loading are external effects; not scene Undoable'] if p['action'] in ('export','batch') else [])
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**values):
        from maya import cmds
        import maya_toolkit
        p=normalize(values)
        if p['action']=='inspect': return ToolResult.ok(message='Mesh roots inspected',data=scene_plan(p))
        if p['action']=='export': return ToolResult.ok(message='Alembic cache exported',data=export(scene_plan(p)))
        if p['action']=='materials':
            nodes=self.validate(**values).data['roots']; selected=cmds.ls(selection=True,long=True) or []; rows=[]
            try:
                for node in nodes:
                    shader=cmds.shadingNode('lambert',asShader=True); sg=cmds.sets(renderable=True,noSurfaceShader=True,empty=True,name=shader+'SG')
                    cmds.connectAttr(shader+'.outColor',sg+'.surfaceShader'); color=[random.random() for _ in range(3)]
                    cmds.setAttr(shader+'.color',*color,type='double3'); cmds.sets(node,edit=True,forceElement=sg)
                    rows.append({'node':node,'shader':shader,'shading_group':sg,'color':color})
            finally:
                if (cmds.ls(selection=True,long=True) or [])!=selected: cmds.select(selected,replace=True) if selected else cmds.select(clear=True)
            return ToolResult.ok(message='Separate Lambert materials assigned',data={'materials':rows})
        planned=batch_plan(p); results=[]
        with tempfile.TemporaryDirectory(prefix='mtb_abc_batch_') as directory:
            for index,(scene,output) in enumerate(zip(planned['scenes'],planned['outputs'])):
                config=Path(directory)/('config'+str(index)+'.json'); result=Path(directory)/('result'+str(index)+'.json')
                config.write_text(json.dumps({'scene':scene,'result':str(result),'runtime_root':str(Path(maya_toolkit.__file__).resolve().parent.parent),'arguments':{'action':'export','set_name':p['set_name'],'output':output,'start':p['start'],'end':p['end'],'step':p['step'],'options':p['options']}}),encoding='utf8')
                command=[planned['mayapy'],str(Path(__file__).with_name('worker.py')),str(config)]
                try:
                    process=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=p['timeout'],env=dict(os.environ,PYTHONIOENCODING='utf-8'),creationflags=0x08000000 if os.name=='nt' else 0)
                    evidence=json.loads(result.read_text(encoding='utf8')) if result.is_file() else {'success':False,'message':process.stdout.decode('utf8',errors='replace')[-3000:]}
                    evidence.update(scene=scene,returncode=process.returncode); evidence['success']=bool(evidence.get('success')) and process.returncode==0
                except subprocess.TimeoutExpired: evidence={'scene':scene,'success':False,'message':'Isolated worker timed out; inspect unused/partial external output before retry'}
                results.append(evidence)
        data={'scenes':results,'outputs':[r['data']['output'] for r in results if r.get('success')],'current_scene_preserved':True}
        failed=[r['scene'] for r in results if not r.get('success')]
        if failed: return ToolResult.fail(message='Some scene exports failed; successful external caches retained',data=data,errors=failed)
        return ToolResult.ok(message='All isolated scene exports completed',data=data)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya UI required')
        from .ui import show_ui
        return show_ui()
