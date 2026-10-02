"""Complete native node canvas and guarded workflow/API candidate."""
import ast,json,shutil,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/07_subsystems_suites/maya_blueprint_toolbox'
RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/maya_blueprint_toolbox';NATIVE=PKG/'native'
for src in UNIT.rglob('*'):
    if not src.is_file() or 'release_candidate' in src.relative_to(UNIT).parts or '__pycache__' in src.parts or src.name=='.gitattributes':continue
    dst=NATIVE/src.relative_to(UNIT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
put(NATIVE/'__init__.py','''"""Full native package; Qt is only imported on explicit UI launch."""
def show():
    from .main import show
    return show()
''')
def edit(rel,before,after):
    p=NATIVE/rel;s=p.read_text(encoding='utf8');assert before in s,(rel,before[:80]);put(p,s.replace(before,after))
edit('main.py','WINDOW_OBJECT_NAME = "MayaBlueprintToolboxWindow"','WINDOW_OBJECT_NAME = "MTB_MayaBlueprintToolboxWindow"')
edit('main.py','    global _window_instance\n','''    global _window_instance
    from maya import cmds
    if cmds.about(batch=True) or QtWidgets.QApplication.instance() is None:
        raise RuntimeError("Real Maya GUI with existing QApplication required")
    app=QtWidgets.QApplication.instance()
    if QtCore.QThread.currentThread()!=app.thread():raise RuntimeError("Maya main thread required")
''')
put(NATIVE/'maya_api/common.py',r'''"""Native wrapper compatibility using existing toolkit Undo context."""
from maya_toolkit.core.context import UndoChunkContext
class MayaApiError(RuntimeError):pass
def maya_modules(include_mel=False):
    try:
        from maya import cmds
        if include_mel:
            from maya import mel
            return cmds,mel
        return cmds
    except ImportError:raise MayaApiError('This operation requires Maya')
class UndoChunk(UndoChunkContext):
    def __init__(self,name=None):super().__init__(name or 'Blueprint Operation')
    def __enter__(self):
        if not maya_modules().undoInfo(query=True,state=True):raise MayaApiError('Enable Undo before scene operations')
        return super().__enter__()
''')
edit('maya_api/scene_nodes.py','''    found_nodes = [node for node in (nodes or []) if cmds.objExists(node)]
    if not found_nodes:
        raise MayaApiError("No existing {0} found.".format(label))
    return found_nodes''','''    if not nodes:raise MayaApiError("No input "+label)
    found_nodes=[]
    for node in nodes:
        matches=cmds.ls(str(node),long=True) or []
        if len(matches)!=1 or not cmds.objExists(matches[0]):raise MayaApiError("Missing/ambiguous "+str(node))
        if matches[0] not in found_nodes:found_nodes.append(matches[0])
    return found_nodes''')
edit('maya_api/attributes.py','''    changed_attrs = []

    with UndoChunk("Blueprint Set Attribute"):
''','''    changed_attrs = []
    from ...workflow import writable_attrs
    writable_attrs([node+"."+attribute for node in source_nodes])
    with UndoChunk("Blueprint Set Attribute"):
''')
edit('maya_api/attributes.py','''    with UndoChunk("Blueprint Set Attribute Ref"):
        for attr_ref in refs:
            converted_value = _convert_value_for_attr(attr_ref, value, value_type)''','''    from ...workflow import writable_attrs
    writable_attrs([r.full_attr for r in refs])
    converted_values=[_convert_value_for_attr(r,value,value_type) for r in refs]
    with UndoChunk("Blueprint Set Attribute Ref"):
        for attr_ref,converted_value in zip(refs,converted_values):''')
edit('maya_api/attributes.py','''    current_time = float(cmds.currentTime(query=True))
    changed_attrs = []''','''    from ...workflow import writable_attrs
    writable_attrs([r.full_attr for r in target_refs])
    for frame in frame_data.frames:
        for ref in target_refs:
            sample=_sample_for_attr_ref(_samples_for_frame(frame_data,frame),ref,frame_data,target_nodes)
            if sample is None or ref.attr not in (sample.get("values") or {}):raise MayaApiError("Missing frame/channel sample")
    current_time = float(cmds.currentTime(query=True))
    changed_attrs = []''')
# Correct a definite original bug: world samples were pasted as local scalar
# attributes. Delegate world conversion to Maya xform; key the local channels
# coupled by parent transforms, and preflight every affected axis first.
p=NATIVE/'maya_api/attributes.py';s=p.read_text(encoding='utf8');a=s.index('def _set_transform_frame_data_attr_refs(');b=s.index('\n\ndef _samples_for_frame(',a)
s=s[:a]+r'''def _set_transform_frame_data_attr_refs(attr_refs,frame_data):
    import math
    from ...workflow import writable_attrs,writable_nodes
    from .animation import normalize_channel
    cmds=maya_modules();refs=_existing_attr_refs(attr_refs)
    channels=set(frame_data.paste_channels or frame_data.recorded_channels or [])
    refs=[r for r in refs if normalize_channel(r.attr) in channels]
    if not refs:raise MayaApiError("No matching paste channels")
    target_nodes=_unique_target_nodes(refs)
    if len(target_nodes)!=len(frame_data.source_nodes):raise MayaApiError("Source/target lists must match 1-to-1")
    writable_nodes(target_nodes)
    if any(not cmds.objectType(n,isAType='transform') for n in target_nodes):raise MayaApiError("Transform targets required")
    requested={n:{normalize_channel(r.attr) for r in refs if r.node==n} for n in target_nodes}
    affected={n:[] for n in target_nodes}
    for n in target_nodes:
        for group in ('translate','rotate'):
            if any(group+a in requested[n] for a in 'XYZ'):affected[n].extend(group+a for a in 'XYZ')
        affected[n].extend('scale'+a for a in 'XYZ' if 'scale'+a in requested[n])
    writable_attrs([n+'.'+c for n in target_nodes for c in affected[n]])
    samples={}
    for frame in frame_data.frames:
        if not math.isfinite(float(frame)):raise MayaApiError("Non-finite sample time")
        for n in target_nodes:
            source=frame_data.source_nodes[target_nodes.index(n)]
            rows=[r for r in frame_data.samples if r.get('node')==source and float(r.get('frame'))==float(frame)]
            if len(rows)!=1:raise MayaApiError("Missing/duplicate frame sample")
            values=rows[0].get('values') or {}
            if any(c not in values or type(values[c]) not in (int,float) or not math.isfinite(values[c]) for c in requested[n]):raise MayaApiError("Missing/non-finite channel sample")
            samples[(n,float(frame))]=values
    current_time=cmds.currentTime(query=True)
    keyed=[]
    with UndoChunk('Blueprint World Frame Paste'):
        try:
            for frame in frame_data.frames:
                cmds.currentTime(frame)
                for n in target_nodes:
                    values=samples[(n,float(frame))]
                    for group,flag in (('translate','translation'),('rotate','rotation')):
                        if any(group+a in requested[n] for a in 'XYZ'):
                            vector=cmds.xform(n,query=True,worldSpace=True,**{flag:True})
                            for i,a in enumerate('XYZ'):
                                if group+a in requested[n]:vector[i]=values[group+a]
                            cmds.xform(n,worldSpace=True,**{flag:vector})
                    for a in 'XYZ':
                        if 'scale'+a in requested[n]:cmds.setAttr(n+'.scale'+a,values['scale'+a])
                    for c in affected[n]:
                        plug=n+'.'+c;cmds.setKeyframe(plug,time=frame);keyed.append(plug)
        finally:cmds.currentTime(current_time)
    return _unique_text_items(keyed)
'''+s[b:];put(p,s)
# All rename/group/delete native calls get the same complete local input check,
# including calls through the UI's native executor.
for method in ('rename_nodes','group_nodes','delete_nodes'):
    p=NATIVE/'maya_api/scene_nodes.py';s=p.read_text(encoding='utf8');tree=ast.parse(s)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==method)
    lines=s.splitlines();body='\n'.join(lines[fn.lineno-1:fn.end_lineno])
    old='    source_nodes = existing_nodes(nodes)';assert old in body
    body=body.replace(old,old+'\n    from ...workflow import writable_nodes\n    writable_nodes(source_nodes, refuse_hierarchy_overlap=True)')
    lines[fn.lineno-1:fn.end_lineno]=body.splitlines();put(p,'\n'.join(lines))
edit('maya_api/constraints.py','''    command = _constraint_command(cmds, constraint_type)
    created_constraints = []''','''    command = _constraint_command(cmds, constraint_type)
    from ...workflow import validate_constraint
    validate_constraint(constraint_type,driver_nodes,driven_nodes,weight)
    created_constraints = []''')
edit('maya_api/io.py','kwargs = {"returnNewNodes": True}','kwargs = {"returnNewNodes": True, "executeScriptNodes": False}')
edit('maya_api/io.py','''    resolved_path = os.path.normpath(file_path)
    if not os.path.exists(resolved_path):''','''    if not os.path.isabs(file_path):raise MayaApiError("Absolute source path required")
    resolved_path = os.path.normpath(file_path)
    if not os.path.isfile(resolved_path):''')
put(NATIVE/'maya_api/export.py',r'''"""Full FBX operation with explicit file protection and temporary globals."""
import json
import math
from .common import MayaApiError,maya_modules
from .scene_nodes import existing_nodes
from ...file_io import output_path,backup_file
def export_fbx(nodes,target_path,bake_animation=False,frame_start=1.,frame_end=120.,overwrite_existing=False):
    cmds,mel=maya_modules(include_mel=True)
    nodes=existing_nodes(nodes)
    p=output_path(target_path,overwrite_existing)
    if p.suffix.lower()!='.fbx':raise MayaApiError('FBX extension required')
    start,end=float(frame_start),float(frame_end)
    if not math.isfinite(start) or not math.isfinite(end) or end<start:raise MayaApiError('Invalid FBX frame bounds')
    if p.exists():backup_file(p)
    if not cmds.pluginInfo('fbxmaya',query=True,loaded=True):cmds.loadPlugin('fbxmaya')
    flags=('FBXExportBakeComplexAnimation','FBXExportBakeComplexStart','FBXExportBakeComplexEnd')
    previous={f:mel.eval(f+' -q') for f in flags}
    selection=cmds.ls(selection=True,long=True) or []
    try:
        mel.eval('FBXExportBakeComplexAnimation -v '+str(bool(bake_animation)).lower())
        if bake_animation:
            mel.eval('FBXExportBakeComplexStart -v '+str(start));mel.eval('FBXExportBakeComplexEnd -v '+str(end))
        cmds.select(nodes,replace=True)
        mel.eval('FBXExport -f '+json.dumps(p.as_posix(),ensure_ascii=False)+' -s')
    finally:
        for f,value in previous.items():mel.eval(f+' -v '+(str(value).lower() if isinstance(value,bool) else str(value)))
        cmds.select([n for n in selection if cmds.objExists(n)],replace=True)
    if not p.is_file():raise MayaApiError('Native export produced no file')
    return str(p)
''')
edit('maya_api/animation.py','import tempfile','import tempfile\nimport math\nimport uuid')
p=NATIVE/'maya_api/animation.py';s=p.read_text(encoding='utf8');a=s.index('def save_frame_data_json(');b=s.index('\n\ndef normalize_frames(',a)
s=s[:a]+'''def save_frame_data_json(frame_data, json_path=""):
    from ...file_io import write_json
    if not json_path:json_path=os.path.join(tempfile.gettempdir(),"mtb_blueprint_frame_"+uuid.uuid4().hex+".json")
    return write_json(json_path,frame_data.to_dict())
'''+s[b:];put(p,s)
edit('maya_api/animation.py','''    start_int = int(round(start))
    end_int = int(round(end))''','''    if not math.isfinite(start) or not math.isfinite(end) or abs(end-start)>10000 or end<start:raise MayaApiError("Invalid/excessive frame range")
    start_int = int(round(start))
    end_int = int(round(end))''')
edit('core/executor.py','''    def execute(self, workflow_data, status_callback=None):
''','''    def execute(self, workflow_data, status_callback=None):
        from ...workflow import execute_graph
        return execute_graph(workflow_data,status_callback=status_callback,executor=self)

    def _execute_impl(self, workflow_data, status_callback=None):
''')
# File I/O goes through one guarded implementation in both API and full UI.
edit('ui/canvas.py','''        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=2, sort_keys=True, ensure_ascii=False)''','''        from ...file_io import write_json
        from ...workflow import normalize_graph
        try:write_json(file_path,normalize_graph(data,require_inputs=False))
        except Exception as error:
            self.status_label.setText(str(error));return''')
edit('ui/canvas.py','''        with open(file_path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        self.scene.load_workflow(data)''','''        from ...file_io import read_json
        from ...workflow import normalize_graph
        try:data=normalize_graph(read_json(file_path),require_inputs=False)
        except Exception as error:
            self.status_label.setText(str(error));return
        self.scene.load_workflow(data)''')
edit('ui/canvas.py','''        issues = self.scene.validate_workflow()
        if issues:''','''        issues = self.scene.validate_workflow()
        from ...workflow import plan_graph
        try:plan_graph(self.scene.serialize())
        except Exception as error:issues.append(str(error))
        if issues:''')
put(PKG/'file_io.py',r'''"""Bounded literal JSON reads, exclusive writes and explicit overwrite backups."""
from pathlib import Path
import hashlib,json,shutil,uuid
MAX=8*1024*1024
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or p.is_symlink():raise ValueError('Absolute non-symlink path required')
    return p
def output_path(value,overwrite=False):
    if type(overwrite) is not bool:raise ValueError('overwrite_existing must be boolean')
    p=path(value)
    if not p.parent.is_dir():raise ValueError('Parent must already exist')
    if p.exists() and (not overwrite or not p.is_file()):raise ValueError('Existing output preserved; explicitly choose overwrite_existing with backup')
    return p
def backup_file(p):
    if p.stat().st_size>128*1024*1024:raise ValueError('Backup limit 128 MiB')
    dst=p.with_name(p.name+'.mtb_backup_'+uuid.uuid4().hex)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    with p.open('rb') as source,dst.open('xb') as target:shutil.copyfileobj(source,target)
    if hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError('Backup verification failed')
    return {'path':str(dst),'sha256':digest}
def write_json(value,data,overwrite=False):
    p=output_path(value,overwrite);raw=json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2).encode('utf8')
    if len(raw)>MAX:raise ValueError('JSON exceeds 8 MiB')
    if p.exists():backup_file(p)
    if overwrite:
        temp=p.with_name(p.name+'.mtb_write_'+uuid.uuid4().hex)
        try:
            with temp.open('xb') as f:f.write(raw)
            temp.replace(p)
        finally:
            if temp.exists():temp.unlink()
    else:
        with p.open('xb') as f:f.write(raw)
    return str(p)
def read_json(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>MAX:raise ValueError('JSON absent or exceeds 8 MiB')
    def pairs(rows):
        result={}
        for key,item in rows:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=item
        return result
    def bad(value):raise ValueError('Non-finite JSON constant')
    return json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs,parse_constant=bad)
''')
put(PKG/'workflow.py',r'''"""Strict graph structure and read-only preflight of currently resolvable operations."""
import copy,json,math,re
from .native.core.node_specs import default_node_specs
from .native.core.types import port_types_compatible
from .file_io import output_path,path
MUTATIONS={'maya.selection.select_nodes','maya.nodes.rename','maya.nodes.group','maya.nodes.delete','maya.attributes.set',
           'maya.constraints.parent','maya.constraints.point','maya.constraints.orient','maya.constraints.scale','maya.io.import_file','maya.io.export_fbx','maya.animation.copy_frame'}
busy=False

def specs():return default_node_specs()
def normalize_graph(data,require_inputs=True):
    try:
        raw=json.dumps(data,allow_nan=False)
        if len(raw.encode('utf8'))>8*1024*1024:raise ValueError('Graph exceeds 8 MiB')
        data=json.loads(raw)
    except (TypeError,RecursionError):raise ValueError('Workflow must be literal JSON')
    if not isinstance(data,dict) or set(data)-{'version','nodes','connections'}:raise ValueError('Workflow keys must be version/nodes/connections')
    if data.get('version',1)!=1 or type(data.get('version',1)) is not int:raise ValueError('Workflow version must be 1')
    nodes=data.get('nodes');links=data.get('connections',[])
    if not isinstance(nodes,list) or len(nodes)>1000 or not isinstance(links,list) or len(links)>10000:raise ValueError('Graph limits: 1000 nodes, 10000 links')
    node_specs=specs();by_id={}
    for n in nodes:
        if not isinstance(n,dict) or set(n)-{'id','type','title','position','parameters'}:raise ValueError('Invalid node structure')
        identifier=n.get('id')
        if not isinstance(identifier,str) or not identifier or len(identifier)>256 or identifier in by_id:raise ValueError('Missing/duplicate node id')
        spec=node_specs.get(n.get('type'))
        if spec is None:raise ValueError('Unknown node type')
        values=n.get('parameters',{})
        if not isinstance(values,dict) or set(values)-{p.name for p in spec.parameters}:raise ValueError('Unknown node parameter')
        values={**copy.deepcopy(spec.default_parameters()),**values}
        for p in spec.parameters:
            value=values[p.name]
            if p.param_type=='bool' and type(value) is not bool:raise ValueError(identifier+'.'+p.name+' must be boolean')
            if p.param_type=='number' and (type(value) not in (int,float) or not math.isfinite(value)):raise ValueError('Finite number required')
            if p.param_type in ('text','path','choice') and not isinstance(value,str):raise ValueError('String parameter required')
            if p.param_type=='choice' and value not in p.choices:raise ValueError('Unknown choice')
            if p.param_type in ('node_list','attribute_item_list') and not (isinstance(value,str) or isinstance(value,list) and all(isinstance(x,str) and x for x in value)):raise ValueError('Name list required')
            if require_inputs and p.required and value in ('',None,[]):raise ValueError(identifier+'.'+p.name+' is required')
        if 'position' in n and (not isinstance(n['position'],list) or len(n['position'])!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in n['position'])):raise ValueError('Finite canvas position required')
        n['parameters']=values;by_id[identifier]=n
    linked=set();dependencies={identifier:set() for identifier in by_id}
    for c in links:
        if not isinstance(c,dict) or set(c)!=set(('source_node','source_port','target_node','target_port')):raise ValueError('Invalid connection structure')
        source,target=c['source_node'],c['target_node']
        if source not in by_id or target not in by_id or source==target:raise ValueError('Missing node/self connection')
        so=next((p for p in node_specs[by_id[source]['type']].outputs if p.name==c['source_port']),None)
        ti=next((p for p in node_specs[by_id[target]['type']].inputs if p.name==c['target_port']),None)
        if so is None or ti is None or not port_types_compatible(so.port_type,ti.port_type):raise ValueError('Unknown/incompatible connection port')
        key=(target,ti.name)
        if key in linked:raise ValueError('Multiple sources for one input')
        linked.add(key);dependencies[target].add(source)
    if require_inputs:
        for n in nodes:
            for p in node_specs[n['type']].inputs:
                if p.required and (n['id'],p.name) not in linked:raise ValueError(n['id']+'.'+p.name+' input required')
            if n['type']=='maya.attributes.make_ref':
                items=n['parameters']['attribute_items'];items=items if isinstance(items,list) else re.split('[,;\n]',items)
                if any('.' not in x for x in items if x.strip()) and (n['id'],'nodes') not in linked:raise ValueError('Attribute names need nodes input')
    remaining={k:set(v) for k,v in dependencies.items()}
    while remaining:
        ready=[k for k,v in remaining.items() if not v]
        if not ready:raise ValueError('Graph cycle')
        for k in ready:remaining.pop(k)
        for v in remaining.values():v.difference_update(ready)
    return {'version':1,'nodes':nodes,'connections':links}

def scoped_graph(data,targets=None):
    if targets is None:return data
    if not isinstance(targets,list) or not targets or any(not isinstance(x,str) for x in targets) or len(set(targets))!=len(targets):raise ValueError('Unique nonempty target ids required')
    known={n['id'] for n in data['nodes']}
    if not set(targets)<=known:raise ValueError('Unknown target node id')
    include=set(targets)
    while True:
        extra={c['source_node'] for c in data['connections'] if c['target_node'] in include}
        if extra<=include:break
        include.update(extra)
    return {**data,'nodes':[n for n in data['nodes'] if n['id'] in include],
            'connections':[c for c in data['connections'] if c['source_node'] in include and c['target_node'] in include]}

def writable_nodes(nodes,refuse_hierarchy_overlap=False):
    from maya import cmds
    if not nodes:raise ValueError('Nonempty node list required')
    for n in nodes:
        if not cmds.objExists(n) or '.' in n or '*' in n or '?' in n:raise ValueError('Explicit existing scene nodes required')
        if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True)) or n in (cmds.ls(defaultNodes=True,long=True) or []):raise ValueError('Referenced/locked/default node refused: '+n)
    if refuse_hierarchy_overlap:
        paths=[(cmds.ls(n,long=True) or [n])[0] for n in nodes]
        if any(a!=b and b.startswith(a+'|') for a in paths for b in paths):raise ValueError('Ancestor/descendant mixed batch refused')
        for n in nodes:
            for child in cmds.listRelatives(n,allDescendents=True,fullPath=True) or []:
                if cmds.referenceQuery(child,isNodeReferenced=True) or any(cmds.lockNode(child,query=True,lock=True)):raise ValueError('Protected descendant refused: '+child)

def writable_attrs(attrs):
    from maya import cmds
    for plug in attrs:
        if not cmds.objExists(plug) or not cmds.getAttr(plug,settable=True) or cmds.getAttr(plug,lock=True):raise ValueError('Missing/locked/connected plug: '+plug)
        writable_nodes([plug.split('.')[0]])

def validate_constraint(kind,drivers,driven,weight):
    from maya import cmds
    if not math.isfinite(float(weight)) or float(weight)<=0:raise ValueError('Positive finite weight required')
    if not drivers or not driven or set(drivers)&set(driven):raise ValueError('Nonempty disjoint drivers/driven required')
    if any(not cmds.objectType(n,isAType='transform') for n in drivers+driven):raise ValueError('Constraint requires transforms')
    writable_nodes(driven)
    axes={'parent':['translate','rotate'],'point':['translate'],'orient':['rotate'],'scale':['scale']}[kind]
    writable_attrs([n+'.'+attribute+a for n in driven for attribute in axes for a in 'XYZ'])

def _check_operation(n,inputs,connected):
    from .native.maya_api import attributes,scene_nodes
    kind=n['type'];p=n['parameters'];nodes=inputs.get('nodes') or []
    if kind in ('maya.nodes.rename','maya.nodes.group','maya.nodes.delete'):
        nodes=scene_nodes.existing_nodes(nodes);writable_nodes(nodes,True)
        if kind=='maya.nodes.rename':
            from maya import cmds
            base=p['base_name']
            if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',base):raise ValueError('Simple rename base required')
            if p['padding']<0 or p['padding']>12 or p['start_index']!=int(p['start_index']):raise ValueError('Invalid rename index/padding')
            destinations=[base+'_'+str(int(p['start_index'])+i).zfill(int(p['padding'])) for i in range(len(nodes))]
            if any(cmds.objExists(x) for x in destinations):raise ValueError('Rename destination collision')
        if kind=='maya.nodes.group':
            from maya import cmds
            if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*',p['group_name']) or cmds.objExists(p['group_name']):raise ValueError('Group name invalid/already exists')
    elif kind=='maya.selection.select_nodes':scene_nodes.existing_nodes(nodes)
    elif kind=='maya.attributes.set':
        refs=attributes._existing_attr_refs(inputs.get('attrs'));writable_attrs([r.full_attr for r in refs])
        value=inputs.get('value')
        if hasattr(value,'samples'):return
        for ref in refs:
            converted=attributes._convert_value_for_attr(ref,value,p.get('value_type','auto'))
            if isinstance(converted,float) and not math.isfinite(converted):raise ValueError('Non-finite attribute value')
    elif kind.startswith('maya.constraints.'):
        validate_constraint(kind.rsplit('.',1)[-1],scene_nodes.existing_nodes(inputs.get('drivers')),scene_nodes.existing_nodes(inputs.get('driven')),p['weight'])
    elif kind=='maya.io.export_fbx':
        scene_nodes.existing_nodes(nodes);out=output_path(inputs.get('target_path'),p['overwrite_existing'])
        if out.suffix.lower()!='.fbx' or p['frame_end']<p['frame_start']:raise ValueError('Invalid FBX extension/frame bounds')
    elif kind=='maya.io.import_file':
        source=path(inputs.get('file_path'))
        if not source.is_file():raise ValueError('Import source absent')
    elif kind=='maya.animation.copy_frame':
        scene_nodes.existing_nodes(nodes)
        from .native.maya_api.animation import normalize_frames
        frames=normalize_frames(inputs.get('frames'))
        if len(frames)>10001 or any(not math.isfinite(x) for x in frames):raise ValueError('Invalid/excessive frames')
        if not connected.get('frame_data') and p.get('json_path'):output_path(p['json_path'])

def plan_graph(data,targets=None,resolve_scene=False):
    data=normalize_graph(data,require_inputs=False)
    data=normalize_graph(scoped_graph(data,targets))
    effects=[{'id':n['id'],'type':n['type'],'scene_or_file_effect':True} for n in data['nodes'] if n['type'] in MUTATIONS]
    plan={'workflow':data,'node_count':len(data['nodes']),'effects':effects,'deferred_nodes':[],
          'preflight':'Structural/type/parameter validation; current data checked read-only where resolvable; future mutation-dependent values checked before each operation'}
    if resolve_scene:
        from .native.core.executor import WorkflowExecutor
        executor=WorkflowExecutor(specs());by_id={n['id']:n for n in data['nodes']};results={};deferred=set()
        for identifier in executor._topological_order(by_id,data['connections']):
            n=by_id[identifier];sources={c['source_node'] for c in data['connections'] if c['target_node']==identifier}
            if sources&deferred:deferred.add(identifier);continue
            inputs=executor._collect_inputs(identifier,data['connections'],results)
            connected=executor._connected_outputs(identifier,data['connections'])
            if n['type'] in MUTATIONS:_check_operation(n,inputs,connected);deferred.add(identifier)
            else:results[identifier]=executor._execute_node(n,inputs,connected)
        plan['deferred_nodes']=sorted(deferred)
    return plan

def execute_graph(data,targets=None,status_callback=None,executor=None):
    global busy
    if busy:raise RuntimeError('Another blueprint graph is executing')
    data=plan_graph(data,targets,resolve_scene=True)['workflow']
    from .native.core.executor import WorkflowExecutor
    from .native.maya_api.common import UndoChunk
    executor=executor or WorkflowExecutor(specs())
    original=executor._execute_node
    def guarded(n,inputs,connected=None):
        if n['type'] in MUTATIONS:_check_operation(n,inputs,connected or {})
        return original(n,inputs,connected)
    executor._execute_node=guarded;busy=True
    try:
        with UndoChunk('Blueprint Complete Workflow'):return executor._execute_impl(data,status_callback=status_callback)
    finally:executor._execute_node=original;busy=False

def serializable(value):
    if hasattr(value,'to_dict'):return serializable(value.to_dict())
    if isinstance(value,dict):return {str(k):serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serializable(v) for v in value]
    if value is None or isinstance(value,(str,int,float,bool)):return value
    return str(value)
''')
put(PKG/'__init__.py',r'''"""Full 45-node graph suite, headless API and original Chinese canvas."""
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from . import workflow,file_io
class MayaBlueprintToolboxTool(BaseMayaTool):
    tool_id='maya_blueprint_toolbox';tool_name='Maya 蓝图工具盒';category='pipeline_io';version='1.0.0'
    description='45种原生类型节点与完整中文蓝图画布；结构/连线/当前可解析操作预检、统一图执行和JSON持久化'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','show_ui','close_ui','validate_workflow','execute_workflow','read_workflow','save_workflow'],'default':'inspect'},
        'workflow':{'type':'object','description':'version1，nodes/parameters与connections typed graph'},
        'target_node_ids':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},
        'path':{'type':'string','description':'绝对JSON路径，parent已存在'},
        'overwrite_existing':{'type':'boolean','default':False}},'required':[]}
    def _plan(self,kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameter')
        action=kwargs.get('action','inspect');overwrite=kwargs.get('overwrite_existing',False)
        if action not in self.parameters_schema['properties']['action']['enum'] or type(overwrite) is not bool:raise ValueError('Invalid action/boolean')
        if action=='inspect':return {'action':action}
        if action in ('show_ui','close_ui'):
            from maya import cmds
            if cmds.about(batch=True):raise ValueError('Real Maya GUI required')
            return {'action':action}
        if action=='read_workflow':
            return {'action':action,'workflow':workflow.normalize_graph(file_io.read_json(kwargs.get('path')),require_inputs=False)}
        graph=kwargs.get('workflow')
        if action=='save_workflow':
            graph=workflow.normalize_graph(graph,require_inputs=False)
            return {'action':action,'workflow':graph,'path':str(file_io.output_path(kwargs.get('path'),overwrite))}
        plan=workflow.plan_graph(graph,kwargs.get('target_node_ids'),resolve_scene=True)
        if plan['effects']:
            from maya import cmds
            if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo before graph operations')
        return {'action':action,**plan}
    def validate(self,**kwargs):
        try:return ToolResult.ok('Blueprint plan',data=self._plan(kwargs),dry_run=True)
        except Exception as error:return ToolResult.fail(str(error),errors=[str(error)])
    def execute(self,**kwargs):
        p=self._plan(kwargs);action=p['action']
        if action=='inspect':return ToolResult.ok('45 native nodes',data={'node_specs':[s.to_dict() for s in workflow.specs().values()],'gui_acceptance':'not_run'})
        if action=='show_ui':
            from .native import show
            window=show();return ToolResult.ok('Blueprint canvas opened',data={'object_name':window.objectName()})
        if action=='close_ui':
            from .native import main
            if main._window_instance is not None:
                try:main._window_instance.close();main._window_instance.deleteLater()
                except RuntimeError:pass
                main._window_instance=None
            return ToolResult.ok('Owned blueprint window closed')
        if action=='save_workflow':return ToolResult.ok('Workflow saved',data={'path':file_io.write_json(p['path'],p['workflow'],kwargs.get('overwrite_existing',False))})
        if action in ('read_workflow','validate_workflow'):return ToolResult.ok('Workflow plan',data=p)
        result=workflow.execute_graph(p['workflow'])
        return ToolResult.ok('Workflow completed',data={'results':workflow.serializable(result),'node_count':p['node_count']})
    def run(self,dry_run=False,**kwargs):
        if type(dry_run) is not bool:return ToolResult.fail('dry_run must be boolean')
        try:
            result=self.validate(**kwargs)
            if result.success and not dry_run:result=self.execute(**kwargs)
        except Exception as error:result=ToolResult.fail(str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=dry_run;return result
    def show_ui(self,parent=None):return self.run(action='show_ui')
''')
put(RC/'tests/test_maya_blueprint_toolbox.py',r'''import copy,importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.maya_blueprint_toolbox import MayaBlueprintToolboxTool
    tool=MayaBlueprintToolboxTool()
from maya_toolkit.tools.maya_blueprint_toolbox import workflow,file_io
def graph():return {'version':1,'nodes':[{'id':'n','type':'constant.number','parameters':{'value':7}},{'id':'p','type':'debug.print_result','parameters':{}}],
    'connections':[{'source_node':'n','source_port':'value','target_node':'p','target_port':'input'}]}
class Checks(unittest.TestCase):
    def test_native_complete_and_strict_graph(self):
        result=tool.run();self.assertTrue(result.success);self.assertEqual(len(result.data['node_specs']),45)
        self.assertNotIn('PySide6',sys.modules)
        data=graph();normalized=workflow.normalize_graph(data);self.assertNotIn('label',data['nodes'][1]['parameters'])
        bad=copy.deepcopy(data);bad['nodes'].append(copy.deepcopy(bad['nodes'][0]))
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['connections'].append(copy.deepcopy(bad['connections'][0]))
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['nodes'][0]['parameters']['value']=True
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        bad=copy.deepcopy(data);bad['connections'][0]['source_port']='wrong'
        with self.assertRaises(ValueError):workflow.normalize_graph(bad)
        with self.assertRaises(ValueError):workflow.scoped_graph(normalized,['missing'])
        self.assertEqual(len(workflow.scoped_graph(normalized,['p'])['nodes']),2)
    def test_graph_persistence_exact_backup(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'graph.json'
            dry=tool.run(action='save_workflow',workflow=graph(),path=str(p),dry_run=True)
            self.assertTrue(dry.success,dry.message);self.assertFalse(p.exists())
            result=tool.run(action='save_workflow',workflow=graph(),path=str(p));self.assertTrue(result.success,result.message)
            before=p.read_bytes();self.assertFalse(tool.run(action='save_workflow',workflow=graph(),path=str(p)).success);self.assertEqual(p.read_bytes(),before)
            self.assertTrue(tool.run(action='save_workflow',workflow=graph(),path=str(p),overwrite_existing=True).success)
            self.assertEqual(next(Path(td).glob('*.mtb_backup_*')).read_bytes(),before)
            self.assertTrue(tool.run(action='read_workflow',path=str(p)).success)
            p.write_text('{"a":1,"a":2}',encoding='utf8')
            with self.assertRaises(ValueError):file_io.read_json(str(p))
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_maya_blueprint_toolbox_maya.py',r'''import copy,importlib.util,os,sys,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.maya_blueprint_toolbox import workflow
def connect(source,port,target,input):return {'source_node':source,'source_port':port,'target_node':target,'target_port':input}
def attribute_graph(names):return {'version':1,'nodes':[{'id':'names','type':'maya.nodes.node_names','parameters':{'names':names}},
    {'id':'refs','type':'maya.attributes.make_ref','parameters':{'attribute_items':['translateX']}},
    {'id':'value','type':'constant.number','parameters':{'value':8}}, {'id':'set','type':'maya.attributes.set','parameters':{}}],
    'connections':[connect('names','nodes','refs','nodes'),connect('refs','attrs','set','attrs'),connect('value','value','set','value')]}
class MayaChecks(unittest.TestCase):
    def setUp(self):cmds.file(new=True,force=True);cmds.undoInfo(state=True)
    def test_graph_dry_complete_and_one_undo(self):
        a=cmds.createNode('transform',name='a');b=cmds.createNode('transform',name='b');cmds.setAttr(a+'.tx',2);cmds.setAttr(b+'.tx',3);cmds.select(a)
        graph=attribute_graph([a,b]);before=set(cmds.ls());selection=cmds.ls(selection=True);time=cmds.currentTime(query=True)
        result=tool.run(action='execute_workflow',workflow=graph,dry_run=True);self.assertTrue(result.success,result.message)
        self.assertEqual(cmds.getAttr(a+'.tx'),2);self.assertEqual(cmds.ls(selection=True),selection);self.assertEqual(set(cmds.ls()),before)
        result=tool.run(action='execute_workflow',workflow=graph);self.assertTrue(result.success,result.message)
        self.assertEqual(cmds.getAttr(a+'.tx'),8);self.assertEqual(cmds.getAttr(b+'.tx'),8)
        cmds.undo();self.assertEqual(cmds.getAttr(a+'.tx'),2);self.assertEqual(cmds.getAttr(b+'.tx'),3)
        self.assertEqual(cmds.currentTime(query=True),time)
        cmds.setAttr(b+'.tx',lock=True);result=tool.run(action='execute_workflow',workflow=graph);self.assertFalse(result.success);self.assertEqual(cmds.getAttr(a+'.tx'),2)
        cmds.setAttr(b+'.tx',lock=False)
        self.assertFalse(tool.run(action='execute_workflow',workflow=attribute_graph([a,'missing'])).success);self.assertEqual(cmds.getAttr(a+'.tx'),2)
        self.assertFalse(tool.run(action='show_ui',dry_run=True).success)
    def test_native_sample_and_guarded_file_json(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.maya_api import animation
        cube=cmds.polyCube()[0];cmds.setAttr(cube+'.tx',7);cmds.currentTime(12)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'sample.json';data=animation.copy_frame([cube],[1,2],save_json=True,json_path=str(p))
            self.assertEqual(cmds.currentTime(query=True),12);self.assertEqual(data.samples[0]['values']['translateX'],7)
            before=p.read_bytes()
            with self.assertRaises(ValueError):animation.copy_frame([cube],[1],save_json=True,json_path=str(p))
            self.assertEqual(p.read_bytes(),before)
            with self.assertRaises(Exception):animation.normalize_frames({'start':0,'end':100000})
    def test_native_example_data_transform(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.core.executor import WorkflowExecutor
        from maya_toolkit.tools.maya_blueprint_toolbox.file_io import read_json
        graph=read_json(str(rc/'maya_toolkit/tools/maya_blueprint_toolbox/native/examples/workflows/data_transform_test.json'))
        results=WorkflowExecutor(workflow.specs()).execute(graph)
        self.assertEqual(results['filter_by_name_1']['matched_nodes'],['pCube1','pCube2'])
    def test_copy_world_paste_parented_rotation_and_one_undo(self):
        from maya_toolkit.tools.maya_blueprint_toolbox.native.maya_api import animation,attributes
        from maya_toolkit.tools.maya_blueprint_toolbox.native.core.types import AttrRef
        source=cmds.createNode('transform',name='source');parent=cmds.createNode('transform',name='targetParent')
        target=cmds.createNode('transform',name='target',parent=parent)
        cmds.setAttr(parent+'.tx',10);cmds.setAttr(parent+'.ry',90);cmds.setAttr(parent+'.sx',2);cmds.setAttr(target+'.rotateOrder',3)
        cmds.setAttr(source+'.tx',7);cmds.setAttr(source+'.ty',3);cmds.setAttr(source+'.rx',15);cmds.setAttr(source+'.ry',25)
        cmds.currentTime(12)
        data=animation.copy_frame([source],[1,2],save_json=False)
        refs=[AttrRef(target,c) for c in animation.TRANSLATE_CHANNELS+animation.ROTATE_CHANNELS]
        before=cmds.xform(target,query=True,worldSpace=True,matrix=True)
        result=attributes.set_attribute_refs(refs,data)
        self.assertEqual(len(result),6);self.assertEqual(cmds.currentTime(query=True),12)
        cmds.undo();self.assertEqual(cmds.xform(target,query=True,worldSpace=True,matrix=True),before)
        cmds.redo()
        for frame in (1,2):
            cmds.currentTime(frame)
            self.assertAlmostEqual(cmds.xform(target,query=True,worldSpace=True,translation=True)[0],7)
            self.assertAlmostEqual(cmds.xform(target,query=True,worldSpace=True,translation=True)[1],3)
            actual=cmds.xform(target,query=True,worldSpace=True,rotation=True)
            for x,y in zip(actual,[15,25,0]):self.assertAlmostEqual(x,y,places=5)
        # Exact one Undo is asserted immediately after the operation, before
        # test-only time scrubbing adds its own native Undo entries.
        cmds.currentTime(12);redo_state=cmds.xform(target,query=True,worldSpace=True,matrix=True)
        cmds.setAttr(target+'.tz',lock=True)
        with self.assertRaises(ValueError):attributes.set_attribute_refs(refs,data)
        self.assertEqual(cmds.xform(target,query=True,worldSpace=True,matrix=True),redo_state)
if __name__=='__main__':
    result=unittest.main(exit=False).result;maya.standalone.uninitialize();sys.exit(0 if result.wasSuccessful() else 1)
''')
put(RC/'tests/test_maya_blueprint_toolbox_qt.py',r'''"""Offscreen native Qt canvas without Maya initialization; not GUI acceptance."""
import importlib.util,os,sys,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable process only')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_bp',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtWidgets,QtCore
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.maya_blueprint_toolbox.native.main import BlueprintToolboxWindow
from maya_toolkit.tools.maya_blueprint_toolbox.file_io import read_json
class QtChecks(unittest.TestCase):
    def test_whole_canvas_all_node_specs_and_example(self):
        window=BlueprintToolboxWindow();canvas=window.canvas_widget
        self.assertEqual(len(canvas.node_specs),45)
        for kind in canvas.node_specs:canvas.scene.add_node_type(kind)
        self.assertGreaterEqual(len(canvas.scene.nodes_by_id),45)
        example=read_json(str(rc/'maya_toolkit/tools/maya_blueprint_toolbox/native/examples/workflows/data_transform_test.json'))
        canvas.scene.load_workflow(example)
        serialized=canvas.scene.serialize();self.assertEqual(len(serialized['nodes']),len(example['nodes']))
        self.assertEqual(len(serialized['connections']),len(example['connections']))
        self.assertEqual(canvas.scene.validate_workflow(),[])
        window.close();window.deleteLater();app.sendPostedEvents(None,QtCore.QEvent.DeferredDelete);app.processEvents()
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/maya_blueprint_toolbox.md','''# Maya 蓝图工具盒：完整45节点候选

用户自有29原文件/全部中文文档/两示例完整SHA归档，17Python模块（以catalog/source_review实际数量为准）完整native运行树、45节点规格与全canvas保留。不扩展原规划的条件/循环/JSON帧数据加载或新Maya节点；所有原实现功能、类型颜色、拖连线/搜索/属性编辑/选中上游子图/多次运行/JSON/结果状态保留。native.core是套件自有数据层，现有正式maya_toolkit.core不改；native Undo共享正式UndoChunkContext。无外部临时路径、无Qt启动import依赖，Qt5/6完整兼容入口保留，自有MTB窗与主线程/已有QApplication/真实GUI检查。

统一API actions inspect/show_ui/close_ui/validate_workflow/execute_workflow/read_workflow/save_workflow，Base/Schema/ToolResult；默认inspect只列45spec，执行实例化Qt为显式show_ui。workflow为version1/nodes/connections，每node含id/type/parameters/可选title+position；target_node_ids仅该节点+全部上游，完整Graph先结构检查，选中子图才必连校验。有限8MiB/1000nodes/10000links，重复id/未知节点/参数/端口/多个来源/不兼容类型/环/严格bool/非有限数字/必填参数拒绝，不静默跳过非法图。save/load可保存合法结构的未连接草稿，不以加载即执行；读取重复JSON键/非有限常量/大文件拒绝。

```python
from maya_toolkit.tools.maya_blueprint_toolbox import MayaBlueprintToolboxTool
t=MayaBlueprintToolboxTool()
t.run() # all specs
t.show_ui()
saved=t.run(action='read_workflow',path=r'C:/temp/workflow.json')
graph=saved.data['workflow']
t.run(action='execute_workflow',workflow=graph,dry_run=True)
t.run(action='execute_workflow',workflow=graph)
```

dry/validate不运行修改节点、不改时间/选择/场景/文件、不编译UI：纯结构检查+当前可解析的只读节点求值，当前目标全表缺失/歧义/锁/reference/default节点/plug连接等检查。涉及前序写入才有的输出列deferred_nodes，真实执行每个操作前再次全表校验；此范围不能假称能预测全部未来节点名和运行状态。全graph scene操作同一个UndoChunk；拒绝重入，失败可能留可Undo的已完成步骤，文件/导入reference/插件不能保证scene Undo完全恢复。多次UI运行各自一group，状态回调保持原运行/完成/失败/跳过。

原静默丢失missing nodes改全表报错；rename/group/delete拒绝锁/reference/default、锁或引用后代及混祖孙批次，rename/group碰撞拒绝；属性设置全部converted value/属性settable先检，CopyFrame数据全部sample先检再写。约束驱动/受驱不同且transform，全部受驱轴可写，权重正有限。复制帧原世界位移/欧拉+相对scale取样/列表1:1保持，采样恢复currentTime，frame range上限10000。修正原世界样本按local scalar setAttr的确定问题：世界位移/欧拉交由Maya xform转换到目标父级空间与rotateOrder；部分世界轴粘贴保留其他世界轴，并预检/打键全部耦合local XYZ轴。scale仍为原相对local scale，不伪称世界scale。所有样本/目标/受影响轴在首写前全检，锁任一耦合轴拒绝。带父级旋转+缩放+不同rotateOrder的隔离fixture证明世界位移/角度与一次Undo/Redo；jointOrient/负scale/shear/复杂constraint rig尚未实测，需真实备份场景验收。

JSON save/new CopyFrame默认独占新文件与已有parent；空CopyFrame路径改系统temp唯一UUID而非固定覆盖，UI保存已存在名拒绝，API明确overwrite_existing才允许备份后原子替换JSON。FBX输出绝对路径/parent/后缀/全部目标/有限帧范围；overwrite_existing明确True保存同目录精确备份后导出，不默认覆盖，插件只真实export加载，finally恢复选择及三项修改的Bake flag。导入source绝对file、MA scriptNodes=False（不能保证其他插件/复杂reference不执行代码）。backup/输出文件/插件加载不由Maya Undo回滚，使用独占临时目录避免检查与写之间竞态。

可组合：节点类型与typed ports、复制帧TransformFrameData、AttrRef/AttrPacket/data lists、导出FILE_RESULT可串联本套45节点。返回results统一序列化到ToolResult；不存在的计划节点不会伪造。其他工具配合以实际输入输出和用户验收为准，未声明跨套件实测组合。

非Maya结构/JSON检查、隔离mayapy图写属性/一次Undo/坏最后锁目标/缺失目标/世界采样与parent-space转换/采样恢复时间/防覆盖/原data-transform示例，以及单独无Maya初始化Qt离屏全canvas/all45类型/示例加载可检查；这些不是已打开Maya的真实UI/生产rig/FBX/reference/跨版本验收。完整代码/资源/专项doc/tests与面板注册晋级已预制，真实验收not_run，仍留staging。
''')
put(RC/'acceptance.md','''# 蓝图工具盒真实Maya验收 not_run

1. 已打开真实Maya中show_ui，全中文45节点/颜色/搜索/右键分类/拖动/端口连线类型/平移缩放/Delete/属性面板/选中上游子图/次数/状态/print/关闭重开，与原版窗隔离。离屏Qt不替代此步骤。
2. 检查重复id/坏最后节点/未知type/参数/端口/双来源/环/必连/strict bool/非有限值在首次场景写前拒绝。dry nodes/选择/currentTime/dirty/Undo队列/文件一致；未来写入输出deferred如实显示，不谎称全图静态预知。一次Undo/Redo整个执行图；异常后当前已完成输出和可Undo部分准确记录。
3. 备份场景逐测全部Maya节点：attr/锁/reference/connected/重命名碰撞/祖孙混批/组/删/4约束；关系遍历/materials/skin/blend/deformer/时间/range/channelBox；非空1:1copy→paste/key。重点父级旋转/缩放/负scale/shear/jointOrient/不同rotateOrder：世界样本使用xform转目标parent space，部分世界轴粘贴时local XYZ耦合打键与锁预检，不将普通带父fixture通过当成全生产rig验证。
4. 两原示例、draft JSON save/load/坏图加载不清空旧图、新名保存/重复名拒绝/显式overwrite精确SHA备份/无路径CopyFrame唯一temp文件；输出前parent须存在，dry不mkdir。FBX插件加载/选择与3项Bake flag恢复/新输出/overwrite明确备份/范围/失败恢复；MA import/reference不执行scriptNodes但插件仍需可信。复杂文件/引用不能假称Undo完全恢复。
5. Qt5/6、Maya2020+原目标与本Maya2025 GUI逐验；文档原规划的尚无节点不认为已实现。candidate_sha256/maya_version/accepted_by/date/passed=true后用promotion一次晋级。
''')
review=[]
for p in sorted(NATIVE.rglob('*.py')):
    t=ast.parse(p.read_bytes());review.append({'path':p.relative_to(NATIVE).as_posix(),'functions':[n.name for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))]})
put(PKG/'source_review.json',json.dumps(review,ensure_ascii=False,indent=2))
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','07_subsystems_suites/maya_blueprint_toolbox','--class-name','MayaBlueprintToolboxTool',
                '--summary','Complete Chinese 45-node blueprint canvas, typed bounded graph/API, read-only resolvable preflight, shared Undo and protected workflow/animation/file IO',
                '--dependencies','Maya cmds/MEL','Bundled complete native canvas and PySide6/PySide2','FBX plugin only for export node',
                '--limitations','Real Maya canvas, all production graph nodes, complex rig world paste, FBX/reference and cross-version acceptance not_run'],check=True)
