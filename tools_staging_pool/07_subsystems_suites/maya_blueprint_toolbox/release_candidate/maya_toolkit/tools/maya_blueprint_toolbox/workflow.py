"""Strict graph structure and read-only preflight of currently resolvable operations."""
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
