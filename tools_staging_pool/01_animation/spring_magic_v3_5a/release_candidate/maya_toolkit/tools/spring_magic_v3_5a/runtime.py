"""Read-only planning and UUID-scoped access to the complete PyMel engine."""
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import uuid

MARK='springMagicCandidateState'
OWNER='springMagicCandidateOwner'
ACTIVE=None


def cmds_module():
    from maya import cmds
    return cmds


def identity(node):
    return cmds_module().ls(str(node),uuid=True)[0]


def snapshot():
    return {identity(n) for n in cmds_module().ls(long=True) or []}


def resolve(uid):
    names=cmds_module().ls(uid,long=True) or []
    return names[0] if names else None


def pymel_available():
    try:
        spec=importlib.util.find_spec('pymel')
        return bool(spec and spec.submodule_search_locations and any((Path(p)/'core/__init__.py').is_file() for p in spec.submodule_search_locations))
    except (ModuleNotFoundError,ValueError):
        return False


def require_pymel():
    if not pymel_available():
        raise RuntimeError('Compatible PyMel is required by the complete Spring Magic engine; absent in this Maya. No dependency was installed and no engine substitute is used.')


def integrity():
    package=Path(__file__).parent
    catalog=json.loads((package/'catalog.json').read_text(encoding='utf-8'))
    for row in catalog['files']:
        if hashlib.sha256((package/row['archive']).read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Original archive changed: '+row['path'])
    for relative,digest in catalog.get('runtime_sha256',{}).items():
        if hashlib.sha256((package/relative).read_bytes()).hexdigest()!=digest:
            raise ValueError('Private engine/resource changed: '+relative)
    return len(catalog['files'])


def node_list(names):
    c=cmds_module()
    out=[]
    for name in names:
        matches=c.ls(name,long=True) or []
        if len(matches)!=1 or '.' in name:
            raise ValueError('Expected one whole node: '+name)
        out.append(matches[0])
    if len(out)!=len(set(out)):
        raise ValueError('Duplicate aliases identify the same node')
    return out


def editable(node):
    c=cmds_module()
    if c.referenceQuery(node,isNodeReferenced=True) or any(c.lockNode(node,query=True,lock=True)):
        raise ValueError('Referenced/locked node: '+node)
    if c.objectType(node,isAType='dagNode') and len(c.ls(node,allPaths=True,long=True) or [])>1:
        raise ValueError('Instanced node: '+node)


def writable_transforms(nodes,channels=True):
    c=cmds_module()
    for node in nodes:
        if not c.objectType(node,isAType='transform'):
            raise ValueError('Expected transform or joint: '+node)
        editable(node)
        if not channels:
            continue
        for attr in c.listAttr(node,keyable=True) or []:
            plug=node+'.'+attr
            if c.getAttr(plug,lock=True):
                raise ValueError('Locked keyable channel: '+plug)
            for driver in c.listConnections(plug,source=True,destination=False) or []:
                kind=c.nodeType(driver)
                if not kind.startswith('animCurve'):
                    raise ValueError('Driven channel needs a clean rig/proxy: '+plug+' <- '+kind)
                editable(driver)
                destinations=c.listConnections(driver,source=False,destination=True,plugs=True) or []
                allowed={identity(n) for n in nodes}
                if any(identity(d.split('.')[0]) not in allowed for d in destinations):
                    raise ValueError('Shared animation driver: '+driver)


def find_session(name=None):
    c=cmds_module()
    sessions=[n for n in c.ls(type='network') or [] if c.attributeQuery(MARK,node=n,exists=True)]
    if name:
        selected=node_list([name])[0]
        if selected not in node_list(sessions):
            raise ValueError('Not a Spring Magic candidate session')
        return selected
    if len(sessions)>1:
        raise ValueError('Multiple sessions: pass an explicit session')
    return sessions[0] if sessions else None


def read_state(session):
    return json.loads(cmds_module().getAttr(session+'.'+MARK)) if session else None


def save_state(session,state):
    cmds_module().setAttr(session+'.'+MARK,json.dumps(state,sort_keys=True),type='string')


def owned_names(state,ids=None):
    c=cmds_module()
    names=[]
    for uid in (state['owned'] if ids is None else ids):
        node=resolve(uid)
        if node:
            if not c.attributeQuery(OWNER,node=node,exists=True) or c.getAttr(node+'.'+OWNER)!=state['id']:
                raise ValueError('Lost ownership marker: '+node)
            names.append(node)
    return names


def deletion_guard(nodes,state,allowed_inputs=()):
    c=cmds_module()
    allowed=set(state['owned'])
    permitted=allowed|set(allowed_inputs)
    for node in nodes:
        if identity(node) not in allowed:
            raise ValueError('Refusing to delete an unowned node: '+node)
        editable(node)
        dependents=(c.listRelatives(node,allDescendents=True,fullPath=True) or [])+(c.listConnections(node,source=False,destination=True) or [])
        for dependent in dependents:
            if identity(dependent) not in permitted and c.nodeType(dependent) not in ('shadingEngine',):
                raise ValueError('Foreign dependent would be affected by cleanup: '+dependent)


def frame_range(p):
    c=cmds_module()
    start=p.get('start',int(c.playbackOptions(query=True,minTime=True)))
    end=p.get('end',int(c.playbackOptions(query=True,maxTime=True)))
    if end<=start or (end-start)*p.get('subdivision',1)>200000:
        raise ValueError('Empty/reversed range or more than 200000 substeps')
    return start,end


def preflight(p):
    c=cmds_module()
    count=integrity()
    session=find_session(p.get('session'))
    state=read_state(session)
    owned=owned_names(state) if state else []
    info={'action':p['action'],'session':session,'pymel_available':pymel_available(),'source_files':count,'owned_nodes':owned,'gui_acceptance':'not_run'}
    if p['action']=='status':
        info['previous_operation_failed']=bool(state and state.get('failed'))
        return info
    require_pymel()
    if not c.undoInfo(query=True,state=True):
        raise ValueError('Enable Maya Undo before running Spring Magic scene operations')
    if state and state.get('failed'):
        raise ValueError('Previous operation failed: Undo it before continuing')
    nodes=node_list(p.get('objects',c.ls(selection=True,long=True) or []))
    action=p['action']
    if action not in ('clear_collision','add_plane','add_wind','add_capsule') and not nodes:
        raise ValueError('Select or supply transforms')
    writable_transforms(nodes,channels=action in ('compute','bind_controls','paste_pose','straight','bind_pose'))
    info['objects']=nodes
    if action in ('compute','bake_controls'):
        info['range']=frame_range(p)
    if action=='compute':
        if any(len(c.ls(n.rsplit('|',1)[-1],long=True) or [])!=1 for n in nodes):
            raise ValueError('Original engine requires unique short transform names')
        selected=set(nodes)
        edges=[]
        for child in nodes:
            parents=c.listRelatives(child,parent=True,fullPath=True) or []
            if parents and parents[0] in selected and c.listRelatives(parents[0],parent=True):
                edges.append((parents[0],child))
                position=c.getAttr(child+'.translate')[0]
                if position[0]<=0 or abs(position[1])>0.001 or abs(position[2])>0.001:
                    raise ValueError('Spring requires child along positive local X: '+child)
        if not edges:
            raise ValueError('Select at least a parented two-transform chain; unparented root is the original driver')
        if any(sum(1 for a,b in edges if a==parent)>1 for parent,child in edges):
            raise ValueError('Branching selections are ambiguous in the original ordered-chain algorithm')
        info['processed_edges']=edges
        info['key_cleanup']='All keyable channels on processed parent/child in range' if not p['pose_match'] else 'Pose-match samples source before solving'
        if p['collision'] and state:
            for capsule in owned_names(state,state['capsules']):
                children=c.listRelatives(capsule,children=True,type='transform',fullPath=True) or []
                if len(children)<2 or c.getAttr(capsule+'.scaleZ')<=0:
                    raise ValueError('Invalid capsule endpoints/radius')
                a=c.xform(children[0],query=True,worldSpace=True,translation=True)
                b=c.xform(children[1],query=True,worldSpace=True,translation=True)
                if sum((x-y)**2 for x,y in zip(a,b))<1e-12:
                    raise ValueError('Degenerate capsule axis')
            for plane in owned_names(state,state['planes']):
                shapes=c.listRelatives(plane,shapes=True,fullPath=True) or []
                if len(shapes)!=1 or c.nodeType(shapes[0])!='mesh' or c.polyEvaluate(plane,vertex=True)!=4:
                    raise ValueError('Original plane math requires the unmodified four-vertex plane')
                mat=c.xform(plane,query=True,worldSpace=True,matrix=True)
                if abs(sum(v*v for v in mat[4:7])-1)>1e-5:
                    raise ValueError('Original plane equations require unit world Y; remove inherited scale')
    if action=='add_capsule':
        for node in nodes:
            children=c.listRelatives(node,children=True,fullPath=True) or []
            if children:
                child=children[0]
                if not c.objectType(child,isAType='transform') or c.getAttr(child+'.translateX')<=0:
                    raise ValueError('Capsule placement requires first child transform along positive local X')
    if action=='bind_controls':
        if len(nodes)<2:
            raise ValueError('Bind needs at least two ordered controls')
        if state and state.get('bindings'):
            raise ValueError('Bake existing bindings before creating another chain in this session')
    if action in ('remove_capsule','clear_collision','add_plane') and state:
        ids=list(state['planes']) if action=='add_plane' else list(state['capsules'])+list(state['planes'])
        deletion_guard(owned_names(state,ids),state)
    if action=='bake_controls':
        if not state or any(identity(n) not in state.get('bindings',{}) for n in nodes):
            raise ValueError('Select only owned controller proxies with recorded UUID bindings')
        ctrls=[resolve(state['bindings'][identity(n)]) for n in nodes]
        if any(n is None for n in ctrls):
            raise ValueError('Bound control disappeared')
        writable_transforms(ctrls,channels=False)
        for n in ctrls:
            for attr in ('tx','ty','tz','rx','ry','rz'):
                if c.getAttr(n+'.'+attr,lock=True):
                    raise ValueError('Locked controller channel')
        # Original bake deletes proxy chains: require the full recorded chain.
        if set(map(identity,nodes))!=set(state['bindings']):
            raise ValueError('Select the complete recorded proxy chain to bake')
        deletion_guard(nodes,state,state['bindings'].values())
    if action=='straight' and any(c.nodeType(n)!='joint' for n in nodes):
        raise ValueError('Straight applies only to selected joints')
    info['warnings']=['PyMel engine execution and real Maya UI still require acceptance','Cancellation/failure may leave partial animation; Undo the operation']
    return info


def new_session():
    c=cmds_module()
    token=uuid.uuid4().hex
    node=c.createNode('network',name='springMagicCandidateSession')
    c.addAttr(node,longName=MARK,dataType='string')
    state={'id':token,'owned':[],'capsules':[],'planes':[],'winds':[],'bindings':{},'pose':{},'failed':False}
    save_state(node,state)
    return node,state


def record_new(state,before):
    c=cmds_module()
    for uid in snapshot()-before:
        node=resolve(uid)
        if c.attributeQuery(MARK,node=node,exists=True):
            continue
        if not c.attributeQuery(OWNER,node=node,exists=True):
            c.addAttr(node,longName=OWNER,dataType='string')
        c.setAttr(node+'.'+OWNER,state['id'],type='string')
        if uid not in state['owned']:
            state['owned'].append(uid)


def capsules(all_nodes):
    if ACTIVE is None:
        raise RuntimeError('Engine requires candidate operation scope')
    from .native import core
    names=owned_names(ACTIVE,ACTIVE['capsules'])
    if not all_nodes:
        selected={identity(n) for n in cmds_module().ls(selection=True,long=True) or []}
        names=[n for n in names if identity(n) in selected]
    return [core.pm.PyNode(n) for n in names]


def collision_plane():
    from .native import core
    names=owned_names(ACTIVE,ACTIVE['planes'])
    return core.pm.PyNode(names[0]) if names else None


def wind_source():
    from .native import core
    names=owned_names(ACTIVE,ACTIVE['winds'])
    return core.pm.PyNode(names[0]) if names else None


def clear_bind(start,end):
    from .native import core
    c=cmds_module()
    proxies=c.ls(selection=True,long=True) or []
    controls=[resolve(ACTIVE['bindings'][identity(n)]) for n in proxies]
    core.pm.bakeResults(*[core.pm.PyNode(n) for n in controls],t=(start,end))
    # The controller constraint is a recorded owned dependency of the proxy.
    constraints=[]
    for n in proxies:
        for x in c.listConnections(n,source=False,destination=True,type='parentConstraint') or []:
            if identity(x) in ACTIVE['owned']:
                constraints.append(x)
    if constraints:
        c.delete(list(set(constraints)))
    c.delete(proxies)
    ACTIVE['bindings']={}


@contextlib.contextmanager
def environment(nodes):
    c=cmds_module()
    selection=[identity(n) for n in c.ls(selection=True,long=True) or []]
    frame=c.currentTime(query=True)
    autokey=c.autoKeyframe(query=True,state=True)
    namespace=c.namespaceInfo(currentNamespace=True,absoluteName=True)
    try:
        c.autoKeyframe(state=False)
        c.select(nodes,replace=True) if nodes else c.select(clear=True)
        yield
    finally:
        c.currentTime(frame,edit=True)
        c.autoKeyframe(state=autokey)
        c.namespace(setNamespace=namespace)
        live=[resolve(u) for u in selection if resolve(u)]
        c.select(live,replace=True) if live else c.select(clear=True)


def cleanup_compute(core,state):
    c=cmds_module()
    temporary=[]
    for data in core._active_data:
        for attr in ('aim_constraint','child_proxy'):
            obj=getattr(data,attr,None)
            if obj is not None and c.objExists(str(obj)):
                temporary.append(str(obj))
    for attr in ('cur_position_locator','prev_position_locator','prev_grand_child_position_locator'):
        obj=getattr(core.SpringData,attr,None)
        if obj is not None and c.objExists(str(obj)):
            temporary.append(str(obj))
        setattr(core.SpringData,attr,None)
    core._active_data.clear()
    for node in temporary:
        if c.objExists(node):
            if identity(node) not in state['owned']:
                raise ValueError('Unowned compute helper')
            c.delete(node)


def execute(p):
    global ACTIVE
    c=cmds_module()
    plan=preflight(p)
    from .native import core
    session=find_session(p.get('session'))
    session,state=(session,read_state(session)) if session else new_session()
    before=snapshot()
    input_ids=list(map(identity,plan['objects']))
    action=p['action']
    # The full original geometry/math operates in private per-session name space.
    core.kWindObjectName='spring_wind_'+state['id']
    core.kSpringProxySuffix='_SpringProxy_'+state['id']
    core.kCollisionPlaneSuffix='_SpringColPlane_'+state['id']
    core.kCapsuleNameSuffix='_collision_capsule_'+state['id']
    core.kNullSuffix='_SpringNull_'+uuid.uuid4().hex
    ACTIVE=state
    try:
        with environment(plan['objects']):
            if action=='compute':
                spring=core.Spring(1-p['spring'],1-p['twist'],p['tension'],p['extend'],p['inertia'])
                settings=core.SpringMagic(*plan['range'],p['subdivision'] if p['collision'] else 1.0,p['loop'],p['pose_match'],p['collision'],p['fast_move'],p['clear_subframes'])
                core.startCompute(spring,settings)
                if core.SpringMagicMaya.isInterrupted():
                    raise RuntimeError('Cancelled; Undo partial animation')
            elif action=='add_capsule':
                core.addCapsuleBody()
            elif action=='add_plane':
                # UUID lookup remains valid after user renames the owned plane.
                old=owned_names(state,state['planes'])
                if old:
                    c.delete(old)
                state['planes']=[]
                core.createCollisionPlane()
            elif action=='add_wind':
                if owned_names(state,state['winds']):
                    raise ValueError('One wind source per session; edit the existing wind attributes')
                core.addWindObj()
            elif action in ('remove_capsule','clear_collision'):
                chosen=list(state['capsules']) if action=='clear_collision' else [u for u in input_ids if u in state['capsules']]
                # Original removeBody also removes the collision plane.
                names=owned_names(state,chosen+state['planes'])
                deletion_guard(names,state)
                if names:
                    c.delete(names)
                state['capsules']=[u for u in state['capsules'] if u not in chosen]
                state['planes']=[]
            elif action=='bind_controls':
                core.bindControls(p['linked_chains'])
            elif action=='bake_controls':
                core.clearBind(*plan['range'])
            elif action=='copy_pose':
                state['pose']={u:[c.getAttr(resolve(u)+'.translate')[0],c.getAttr(resolve(u)+'.rotate')[0]] for u in input_ids}
            elif action=='paste_pose':
                for uid in input_ids:
                    if uid in state['pose']:
                        c.setAttr(resolve(uid)+'.translate',*state['pose'][uid][0])
                        c.setAttr(resolve(uid)+'.rotate',*state['pose'][uid][1])
            elif action=='straight':
                for node in plan['objects']:
                    c.setAttr(node+'.rotate',0,0,0)
            elif action=='bind_pose':
                core.bindPose()
            record_new(state,before)
            added=owned_names(state,list(snapshot()-before-set([identity(session)])))
            for node in added:
                if c.objectType(node,isAType='transform'):
                    short=node.rsplit('|',1)[-1]
                    if 'ylinder' in short and core.kCapsuleNameSuffix in short:
                        state['capsules'].append(identity(node))
                    if core.kCollisionPlaneSuffix in short:
                        state['planes'].append(identity(node))
                    if short==core.kWindObjectName:
                        state['winds'].append(identity(node))
            if action=='bind_controls':
                for node in added:
                    if c.nodeType(node)=='parentConstraint':
                        proxies=c.listConnections(node+'.target',source=True,destination=False,type='joint') or []
                        targets=c.listConnections(node,source=False,destination=True,type='transform') or []
                        for proxy in proxies:
                            for target in targets:
                                if identity(target) in input_ids:
                                    state['bindings'][identity(proxy)]=identity(target)
                if set(state['bindings'].values())!=set(input_ids):
                    raise RuntimeError('Could not identify all native controller bindings')
            if action=='compute':
                cleanup_compute(core,state)
    except Exception:
        state['failed']=True
        record_new(state,before)
        if action=='compute':
            cleanup_compute(core,state)
        save_state(session,state)
        raise
    finally:
        ACTIVE=None
    state['owned']=[u for u in state['owned'] if resolve(u)]
    for role in ('capsules','planes','winds'):
        state[role]=[u for u in state[role] if resolve(u)]
    save_state(session,state)
    return {'action':action,'session':session,'owned_nodes':owned_names(state),'bindings':state['bindings'],'gui_acceptance':'not_run','original_engine':'complete 3.5a PyMel implementation'}
