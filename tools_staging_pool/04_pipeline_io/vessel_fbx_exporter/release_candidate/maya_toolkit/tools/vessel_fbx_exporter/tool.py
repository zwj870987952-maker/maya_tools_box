"""Vessel set pipeline runs on an isolated snapshot, never the caller scene."""
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from maya_toolkit.framework import BaseMayaTool,ToolResult
TRS=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
RESET=[0,0,0,-90,0,0,1,1,1]

def normalize(values):
    p=dict(action='inspect',output_dir=None,keyword=None,start=None,end=None,bake_joints=True,bake_export_sets=False,reset_transforms=True,import_references=True,remove_namespaces=True,rename_root=True,reference_results=False,save_prepared_scene=False,ascii=True,embedded_textures=True,reset_values=RESET,timeout=300)
    if set(values)-set(p): raise ValueError('Unknown parameters')
    p.update(values)
    if p['action'] not in ('inspect','process'): raise ValueError('Invalid action')
    for key in ('bake_joints','bake_export_sets','reset_transforms','import_references','remove_namespaces','rename_root','reference_results','save_prepared_scene','ascii','embedded_textures'):
        if type(p[key]) is not bool: raise ValueError('Pipeline options must be bool')
    for key in ('start','end'):
        if p[key] is not None and (type(p[key]) not in (int,float) or not math.isfinite(p[key])): raise ValueError('Finite frame range required')
    if p['output_dir'] is not None and (not isinstance(p['output_dir'],str) or not Path(p['output_dir']).is_absolute()): raise ValueError('Absolute output directory required')
    if p['keyword'] is not None and (not isinstance(p['keyword'],str) or not p['keyword'] or any(c in p['keyword'] for c in '/\\<>:"|?*\n\r')): raise ValueError('Portable nonempty keyword required')
    if not isinstance(p['reset_values'],list) or len(p['reset_values'])!=9 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p['reset_values']): raise ValueError('Nine finite TRS reset values required')
    if type(p['timeout']) is not int or not 10<=p['timeout']<=3600: raise ValueError('Timeout10..3600 required')
    return p

def resolve(node):
    from maya import cmds
    names=cmds.ls(node,long=True) or []
    if len(names)!=1 or '.' in names[0] or not cmds.objectType(names[0],isAType='transform'): raise ValueError('Set members must be exact transform/joint nodes: '+node)
    return names[0]

def members(node,visited=None):
    from maya import cmds
    visited=set() if visited is None else set(visited)
    if node in visited: raise ValueError('Cyclic nested set')
    visited.add(node); result=[]
    for member in cmds.sets(node,query=True) or []:
        if cmds.nodeType(member)=='objectSet': result.extend(members(member,visited))
        else: result.append(resolve(member))
    return sorted(set(result))

def sets_scope():
    from maya import cmds
    types={'export':'_FBXExport','joints':'All_joints','reset':'Reset_Trans'}; scope={}
    for key,marker in types.items():
        scope[key]=[{'set':n,'uuid':cmds.ls(n,uuid=True)[0],'members':members(n)} for n in sorted(cmds.ls(type='objectSet') or []) if marker in n]
    return scope

def plan(p):
    from maya import cmds
    from .fbx_io import safe_name
    scope=sets_scope(); rows=[r for r in scope['export'] if r['members']]
    if not rows: raise ValueError('No nonempty _FBXExport sets')
    scene=cmds.file(query=True,sceneName=True); name=Path(scene).stem if scene else 'untitled'
    keyword=p['keyword'] if p['keyword'] is not None else name
    safe_name(keyword)
    directory=Path(p['output_dir']) if p['output_dir'] else Path(scene).parent/'FBXExport'
    if not scene and p['output_dir'] is None: raise ValueError('Unsaved caller requires explicit output_dir')
    if directory.exists() and not directory.is_dir(): raise ValueError('Output path is not a directory')
    parent=directory
    while not parent.exists(): parent=parent.parent
    if not parent.is_dir(): raise ValueError('Output ancestor not directory')
    start=p['start'] if p['start'] is not None else cmds.playbackOptions(query=True,minTime=True); end=p['end'] if p['end'] is not None else cmds.playbackOptions(query=True,maxTime=True)
    if end<start or end-start>100000: raise ValueError('Ordered bounded frame range required')
    outputs=[]; used=set()
    for row in rows:
        filename=row['set'].replace('_FBXExport','').replace('AAA',keyword).replace(':','_')+'.fbx'; safe_name(filename); path=directory/filename
        if path.exists() or path.is_symlink() or str(path.resolve()).casefold() in used: raise ValueError('Output exists/collides: '+str(path))
        used.add(str(path.resolve()).casefold()); outputs.append(dict(row,output=str(path)))
    prepared=directory/(safe_name(keyword)+'_prepared.ma') if p['save_prepared_scene'] else None
    if prepared is not None and (prepared.exists() or prepared.is_symlink()): raise ValueError('Prepared scene output exists')
    refs=[]
    for rn in cmds.ls(type='reference') or []:
        if rn=='sharedReferenceNode': continue
        source=cmds.referenceQuery(rn,filename=True,withoutCopyNumber=True)
        if p['import_references'] and (not Path(source).is_file() or not cmds.referenceQuery(rn,isLoaded=True)): raise ValueError('All imported references must be loaded and source-readable: '+rn)
        refs.append({'node':rn,'source':source,'loaded':cmds.referenceQuery(rn,isLoaded=True)})
    for category in ('joints','reset','export'):
        enabled=p[{'joints':'bake_joints','reset':'reset_transforms','export':'bake_export_sets'}[category]]
        if not enabled: continue
        for row in scope[category]:
            for node in row['members']:
                if cmds.lockNode(node,query=True,lock=True)[0]: raise ValueError('Locked pipeline set member: '+node)
                if cmds.referenceQuery(node,isNodeReferenced=True) and not p['import_references']: raise ValueError('Reference set member requires private import before modification')
                for attr in TRS if category=='reset' else cmds.listAttr(node,keyable=True,multi=True) or []:
                    plug=node+'.'+attr
                    if cmds.getAttr(plug,lock=True): raise ValueError('Locked member attribute: '+plug)
                    if category=='reset':
                        drivers=cmds.listConnections(plug,source=True,destination=False) or []
                        if any(not cmds.nodeType(n).startswith('animCurve') for n in drivers): raise ValueError('Reset has non-animation driver: '+plug)
    return {'scope':scope,'outputs':outputs,'references':refs,'range':[start,end],'keyword':keyword,'output_dir':str(directory),'prepared_scene':str(prepared) if prepared else None,
            'caller_scene_preserved':True,'pipeline_scope':'entire private scene snapshot; all references imported when enabled','reset_cuts_all_keys_on_members':p['reset_transforms']}

def shape_ids():
    from maya import cmds
    return set(cmds.ls(long=True) or [])

def node_from_uuid(identity):
    from maya import cmds
    names=cmds.ls(identity,long=True) or []
    if len(names)!=1: raise RuntimeError('Set identity changed during private preparation')
    return names[0]

def pipeline(p,data):
    from maya import cmds
    from .fbx_io import export,DEFAULTS
    from .scene_io import save_output
    events=[]
    # Import first in this private scene so baking/reset do not leave reference
    # edits which are then discarded. Caller references are never imported.
    if p['import_references']:
        while True:
            refs=[r for r in cmds.ls(type='reference') or [] if r!='sharedReferenceNode']
            if not refs: break
            tops=[r for r in refs if not cmds.referenceQuery(r,parent=True,referenceNode=True)]
            if not tops: raise RuntimeError('Unresolved nested reference tree')
            for rn in tops: cmds.file(referenceNode=rn,importReference=True)
        events.append('All private references imported')
    scope=sets_scope()
    if p['bake_joints']:
        for row in scope['joints']:
            if row['members']: cmds.bakeResults(row['members'],t=tuple(data['range']),simulation=True,sampleBy=1,sparseAnimCurveBake=False,removeBakedAttributeFromLayer=False,bakeOnOverrideLayer=False,preserveOutsideKeys=True,minimizeRotation=True)
        events.append('All_joints sets baked')
    if p['bake_export_sets']:
        for row in scope['export']:
            if row['members']: cmds.bakeResults(row['members'],t=tuple(data['range']),simulation=True)
        events.append('_FBXExport set member animations baked')
    if p['reset_transforms']:
        cmds.currentTime(data['range'][0])
        for node in sorted({n for row in scope['reset'] for n in row['members']}):
            cmds.cutKey(node,clear=True)
            for attr,value in zip(TRS,p['reset_values']): cmds.setAttr(node+'.'+attr,value)
            cmds.setKeyframe(node,time=data['range'][0])
        events.append('Reset_Trans all keys cleared, TRS reset and first-frame key set')
    # Bind output names to set UUID after reference import, before namespace merge.
    current_exports=[r for r in scope['export'] if r['members']]
    if len(current_exports)!=len(data['outputs']): raise RuntimeError('Export set scope changed during reference import')
    output_rows=[]
    for original in data['outputs']:
        matches=[r for r in current_exports if r['set']==original['set']]
        if len(matches)!=1: raise RuntimeError('Original export set disappeared during reference import')
        output_rows.append(dict(matches[0],output=original['output']))
    if p['remove_namespaces']:
        namespaces={r['set'].rpartition(':')[0] for r in output_rows if ':' in r['set']}
        namespaces.update(n.rsplit('|',1)[-1].rpartition(':')[0] for r in output_rows for n in r['members'] if ':' in n.rsplit('|',1)[-1])
        for namespace in sorted(namespaces,key=lambda n:n.count(':'),reverse=True):
            if cmds.namespace(exists=':'+namespace): cmds.namespace(removeNamespace=':'+namespace,mergeNamespaceWithRoot=True)
        events.append('Export set/member namespaces merged to root in private scene')
    Path(data['output_dir']).mkdir(parents=True,exist_ok=True); outputs=[]
    opts=dict(DEFAULTS,ascii=p['ascii'],embedded_textures=p['embedded_textures'],blend_shapes=True,include_children=True)
    for row in output_rows:
        set_name=node_from_uuid(row['uuid']); targets=members(set_name)
        outputs.extend(export({'tasks':[{'objects':targets,'start':data['range'][0],'end':data['range'][1],'output':row['output']}],'options':opts}))
        if p['rename_root'] and cmds.objExists(':root'):
            roots=cmds.ls('root*',type='transform') or []; numbers=[int(m.group(1)) for name in roots if (m:=re.search(r'_(\d+)$',name))]
            cmds.rename(':root','root_'+str(max(numbers,default=0)+1).zfill(3)); events.append('Private root renamed after export')
        if p['reference_results']:
            namespace=re.sub('[^A-Za-z0-9_]','_',Path(row['output']).stem)
            if not namespace or namespace[0].isdigit(): namespace='export_'+namespace
            if cmds.namespace(exists=':'+namespace): raise ValueError('Reference result namespace occupied')
            cmds.file(row['output'],reference=True,namespace=namespace,mergeNamespacesOnClash=False,executeScriptNodes=False)
            cmds.select(cmds.namespaceInfo(':'+namespace,listOnlyDependencyNodes=True,dagPath=True) or [],replace=True)
            events.append('Generated FBX referenced in private scene')
    prepared=save_output(data['prepared_scene']) if data['prepared_scene'] else None
    return {'success':True,'outputs':outputs,'prepared_scene':prepared,'events':events,'caller_scene_preserved':True}

def matching_mayapy():
    location=os.environ.get('MAYA_LOCATION'); exe=Path(location)/'bin'/('mayapy.exe' if os.name=='nt' else 'mayapy') if location else Path(sys.executable).with_name('mayapy.exe' if os.name=='nt' else 'mayapy')
    if not exe.is_file(): raise ValueError('Matching mayapy unavailable')
    return str(exe)

def process(p,data):
    from maya import cmds
    import maya_toolkit
    with tempfile.TemporaryDirectory(prefix='mtb_vessel_') as directory:
        root=Path(directory); scene=root/'snapshot.ma'; config=root/'job.json'; output=root/'result.json'
        # exportAll captures even an untitled dirty scene without renaming or
        # saving its source, nor changing the caller's Undo queue.
        cmds.file(str(scene),exportAll=True,type='mayaAscii',preserveReferences=True,force=True,options='v=0;')
        config.write_text(json.dumps({'parameters':p,'plan':data,'scene':str(scene),'workspace':cmds.workspace(query=True,rootDirectory=True),'result':str(output),'runtime_root':str(Path(maya_toolkit.__file__).resolve().parent.parent)}),encoding='utf8')
        try: run=subprocess.run([matching_mayapy(),str(Path(__file__).with_name('worker.py')),str(config)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=p['timeout'],env=dict(os.environ,PYTHONIOENCODING='utf-8',MAYA_APP_DIR=str(root/'maya_app')),creationflags=0x08000000 if os.name=='nt' else 0)
        except subprocess.TimeoutExpired: return ToolResult.fail(message='Vessel worker timed out; completed external outputs may remain',errors=['timeout'])
        result=json.loads(output.read_text(encoding='utf8')) if output.is_file() else {'success':False,'message':run.stdout.decode('utf8',errors='replace')[-3000:]}
        if not result['success'] or run.returncode!=0: return ToolResult.fail(message=result.get('message','Vessel worker failed'),data=result,errors=[result.get('traceback','worker failed')])
        return ToolResult.ok(message='Vessel snapshot pipeline completed; external outputs retained',data=result)

class VesselFbxExporterTool(BaseMayaTool):
    tool_id='vessel_fbx_exporter'; tool_name='舰船选择集自动FBX导出'; category='pipeline_io'; version='1.0.0-candidate1'
    description='Original All_joints/Reset_Trans/reference import/namespace merge/root rename/FBX set pipeline, applied only to a private isolated current-scene snapshot.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','process'],'default':'inspect'},'output_dir':{'type':'string'},'keyword':{'type':'string'},'start':{'type':'number'},'end':{'type':'number'},**{k:{'type':'boolean','default':v} for k,v in {'bake_joints':True,'bake_export_sets':False,'reset_transforms':True,'import_references':True,'remove_namespaces':True,'rename_root':True,'reference_results':False,'save_prepared_scene':False,'ascii':True,'embedded_textures':True}.items()},'reset_values':{'type':'array','items':{'type':'number'},'minItems':9,'maxItems':9,'default':RESET},'timeout':{'type':'integer','minimum':10,'maximum':3600,'default':300}}}
    def validate(self,**values):
        try:
            p=normalize(values); data=plan(p); data['mayapy']=matching_mayapy()
            return ToolResult.ok(message='Vessel pipeline scope inspected',data=data,warnings=['Private snapshot pipeline imports all references and clears all keys on Reset_Trans members; files/logs not Maya Undoable'])
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])
    def execute(self,**values):
        p=normalize(values); data=plan(p)
        if p['action']=='inspect': return ToolResult.ok(message='Vessel scene sets inspected',data=data)
        return process(p,data)
    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui()
