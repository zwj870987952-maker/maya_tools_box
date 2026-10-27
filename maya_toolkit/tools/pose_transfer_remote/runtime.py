"""Persist original locator workflow as an undoable, UUID-resolved scene session."""
from contextlib import contextmanager
import json
import math
import re
import uuid
from maya import cmds
import maya.api.OpenMaya as om
from maya_toolkit.framework.models import ToolResult

ACTIVE = None
ATTRIBUTE = 'mayaToolkitPoseTransferSession'
WARNINGS = ['真人GUI/生产rig/pivot/引用编辑待验；只按ROOT平移，不自动跨模型重映射。', '完整world matrix会写控制器T/R/S/shear，执行前备份。', '助手与network metadata留场景，cleanup仅删自有助手。']


def require_scope():
    if ACTIVE is None:
        raise ValueError('Use PoseTransferRemoteTool.run; native writes need checked scope')


def uid(n):
    return cmds.ls(n, uuid=True)[0]


def nodes():
    result = {}
    it = om.MItDependencyNodes()
    while not it.isDone():
        obj = it.thisNode()
        fn = om.MFnDependencyNode(obj)
        if obj.hasFn(om.MFn.kDagNode):
            path = om.MDagPath.getAPathTo(obj)
            parts = []
            while path.length():
                parts.append(om.MFnDependencyNode(path.node()).absoluteName())
                path.pop()
            name = '|' + '|'.join(reversed(parts))
        else:
            name = fn.absoluteName()
        result.setdefault(fn.uuid().asString(), []).append(name)
        it.next()
    return result


def resolve(identity):
    found = nodes().get(identity, [])
    if len(found) != 1:
        raise ValueError('Missing/duplicate UUID node: ' + str(identity))
    return found[0]


def whole(n, kind='transform'):
    found = cmds.ls(n, long=True) or []
    if len(found) != 1 or '.' in found[0] or cmds.nodeType(found[0]) != kind:
        raise ValueError('Expected one whole ' + kind + ': ' + str(n))
    n = resolve(uid(found[0]))
    if len(cmds.ls(n, long=True, allPaths=True) or []) != 1:
        raise ValueError('Instanced destination unsupported')
    return n


def matrix(n):
    values = cmds.xform(n, q=True, ws=True, matrix=True)
    if len(values) != 16 or any(not math.isfinite(v) or abs(v) > 1e12 for v in values):
        raise ValueError('Nonfinite/excessive world matrix')
    return values


def mutable(n, refs=False, all_channels=True):
    if any(cmds.lockNode(n, q=True, lock=True) or []) or (cmds.referenceQuery(n, isNodeReferenced=True) and not refs):
        raise ValueError('Locked/referenced write node refused: ' + n)
    attrs = ('tx','ty','tz','rx','ry','rz','sx','sy','sz','shearXY','shearXZ','shearYZ') if all_channels else ('tx','ty','tz')
    for attr in attrs:
        compound = 'translate' if attr.startswith('t') else 'rotate' if attr.startswith('r') else 'scale' if attr.startswith('s') and not attr.startswith('shear') else 'shear'
        if cmds.getAttr(n+'.'+attr, lock=True) or cmds.listConnections(n+'.'+attr,s=True,d=False) or cmds.listConnections(n+'.'+compound,s=True,d=False):
            raise ValueError('Locked/keyed/driven destination channel: ' + n+'.'+attr)


def session():
    found = []
    for n in cmds.ls(type='network') or []:
        if cmds.attributeQuery(ATTRIBUTE, node=n, exists=True) and not cmds.referenceQuery(n, isNodeReferenced=True):
            raw = cmds.getAttr(n+'.'+ATTRIBUTE)
            if not isinstance(raw,str) or len(raw) > 4000000:
                raise ValueError('Malformed session metadata')
            data = json.loads(raw)
            if not re.fullmatch('[a-f0-9]{32}', data.get('id','')) or data.get('version') != 1 or not isinstance(data.get('pairs'),list) or len(data['pairs']) > 1000:
                raise ValueError('Invalid session identity/shape')
            marker = resolve(uid(n))
            if marker != ':mtkPoseTransfer_' + data['id'] + '_session':
                raise ValueError('Marker provenance changed')
            data['marker'] = marker
            if data.get('complete') and (not isinstance(data.get('original_root_pos'),list) or len(data['original_root_pos'])!=3 or any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e12 for v in data['original_root_pos'])):
                raise ValueError('Invalid captured root position')
            found.append(data)
    if len(found)>1:
        raise ValueError('Multiple local pose sessions refused')
    return found[0] if found else None


def helper_name(ctrl, index):
    require_scope()
    return ':mtkPoseTransfer_' + ACTIVE['id'] + '_' + uid(ctrl).replace('-','') + '_' + str(index)


def owned(s):
    return {identity for pair in s['pairs'] for identity in [pair['locator']] + pair.get('shapes',[])}


def alive_locs(s):
    current=nodes()
    return [current[p['locator']][0] for p in s['pairs'] if len(current.get(p['locator'],[]))==1]


def check_delete(names, identities):
    for n in names:
        if uid(n) not in identities:
            raise ValueError('Refuse deleting foreign helper')
        mutable(n)
        for child in cmds.listRelatives(n, allDescendents=True, fullPath=True) or []:
            if uid(child) not in identities:
                raise ValueError('Helper has an external child')
        for out in cmds.listConnections(n,s=False,d=True) or []:
            if uid(out) not in identities:
                raise ValueError('Helper drives an external user')


def checked_delete(n):
    require_scope()
    found = [resolve(uid(x)) for x in (n if isinstance(n,list) else [n])]
    identities = set(ACTIVE.get('owned',[]))
    check_delete(found,identities)
    cmds.delete(found)


def detect(root, control_set=None):
    from .native import PoseTransfer
    obj = PoseTransfer()
    results = []
    if control_set is None:
        leaf=root.rsplit('|',1)[-1]
        namespace=leaf.rsplit(':',1)[0] if ':' in leaf else ''
        candidate=(namespace or ':')+(':' if namespace else '')+'ControlSet'
        if cmds.objExists(candidate):
            control_set=candidate
    if control_set:
        control_set = whole(control_set,'objectSet')
        for n in cmds.sets(control_set,q=True) or []:
            try:
                n = whole(n)
            except ValueError:
                continue
            if n == root or n.startswith(root+'|'):
                results.append(n)
    for n in cmds.listRelatives(root,allDescendents=True,type='transform',fullPath=True) or []:
        n = whole(n)
        if obj.is_controller(n):
            results.append(n)
    return sorted(set(results+[root]),key=lambda n:(n.count('|'),n))


def prepare(o):
    p = dict(action=o['action'],warnings=WARNINGS[:])
    s = session()
    if o['action'] in ('open_ui','close_ui','inspect'):
        if o['action']=='open_ui' and cmds.about(batch=True):
            raise ValueError('Interactive Maya UI required')
        p.update(session=s,selection=cmds.ls(sl=True,long=True) or [])
        return p
    if s and o['action']!='detect':
        if any(cmds.lockNode(s['marker'],q=True,lock=True) or []) or cmds.getAttr(s['marker']+'.'+ATTRIBUTE,lock=True) or cmds.listConnections(s['marker']+'.'+ATTRIBUTE,s=True,d=False):
            raise ValueError('Session metadata is locked/driven')
        if o['action']=='cleanup' and cmds.listConnections(s['marker'],s=False,d=True):
            raise ValueError('Session marker feeds an external user')
    if o['action'] in ('detect','capture'):
        root = whole(o['root'])
        controls = [whole(n) for n in o['controllers']] if o['controllers'] is not None else detect(root,o['control_set'])
        controls = sorted(set(controls),key=lambda n:(n.count('|'),n))
        if len(controls)>1000:
            raise ValueError('Controller budget exceeded')
        for n in controls:
            matrix(n)
        p.update(root=root,controllers=controls)
        if s and o['action']=='capture':
            check_delete(alive_locs(s),owned(s))
    else:
        if s is None:
            if o['action']=='cleanup':
                return p
            raise ValueError('Capture a pose first')
        if o['action'] in ('shift','apply') and not s.get('complete'):
            raise ValueError('Incomplete capture; recapture or cleanup first')
        if o['action']=='cleanup':
            p.update(session=s,root=None,controllers=[],locators=alive_locs(s))
        else:
            p.update(session=s,root=resolve(s['root']),controllers=[resolve(pair['controller']) for pair in s['pairs']],locators=[resolve(pair['locator']) for pair in s['pairs']])
        if o['root'] and uid(whole(o['root'])) != s['root']:
            raise ValueError('Root differs from captured UUID')
        for n in p['locators']:
            matrix(n)
            mutable(n,all_channels=o['action']!='shift')
        if o['action']=='apply':
            for pair,n,loc in zip(s['pairs'],p['controllers'],p['locators']):
                mutable(n,o['allow_reference_edits'])
                attr = cmds.getAttr(loc+'.original_controller')
                if attr not in (pair['original_path'],n):
                    raise ValueError('Locator controller identity was manually changed')
        if o['action']=='cleanup':
            check_delete(p['locators'],owned(s))
    if o['action']!='detect' and not cmds.undoInfo(q=True,state=True):
        raise ValueError('Enable Undo before scene writes')
    if o['allow_reference_edits']:
        p['warnings'].append('显式允许引用控制器matrix写入的引用编辑；保存场景会保留。')
    return p


@contextmanager
def scope(s):
    global ACTIVE
    if ACTIVE is not None:
        raise ValueError('Reentrant write refused')
    state = dict(selection=cmds.ls(sl=True,long=True) or [],time=cmds.currentTime(q=True),auto=cmds.autoKeyframe(q=True,state=True),ns=':'+cmds.namespaceInfo(currentNamespace=True).lstrip(':'),relative=cmds.namespace(q=True,relativeNames=True))
    ACTIVE = dict(id=s['id'],owned=list(owned(s)))
    try:
        cmds.namespace(relativeNames=False)
        cmds.namespace(set=':')
        cmds.autoKeyframe(state=False)
        yield
    finally:
        ACTIVE = None
        errors=[]
        for fn in (lambda:cmds.namespace(relativeNames=False),lambda:cmds.namespace(set=state['ns']),lambda:cmds.namespace(relativeNames=state['relative']),lambda:cmds.autoKeyframe(state=state['auto']),lambda:cmds.currentTime(state['time']),lambda:cmds.select([n for n in state['selection'] if cmds.objExists(n)],r=True) if state['selection'] else cmds.select(clear=True)):
            try:
                fn()
            except Exception as e:
                errors.append(str(e))
        if errors:
            raise RuntimeError('Context restore failed: '+'; '.join(errors))


def save(s):
    cmds.setAttr(s['marker']+'.'+ATTRIBUTE,json.dumps({k:v for k,v in s.items() if k!='marker'},ensure_ascii=True),type='string')


def execute(o,p):
    from .native import PoseTransfer,create_pose_transfer_ui
    action=o['action']
    if action in ('inspect','detect'):
        return ToolResult.ok(data=p,warnings=p['warnings'])
    if action=='open_ui':
        create_pose_transfer_ui()
        return ToolResult.ok(data=p,warnings=p['warnings'])
    if action=='close_ui':
        if cmds.window('mtkPoseTransferCandidateWindow',exists=True):
            cmds.deleteUI('mtkPoseTransferCandidateWindow',window=True)
        return ToolResult.ok(data=p,warnings=p['warnings'])
    s=session()
    if action=='cleanup' and s is None:
        return ToolResult.ok('没有候选会话需要清理',data=p,warnings=p['warnings'])
    if s is None:
        identity=uuid.uuid4().hex
        marker=cmds.createNode('network',name=':mtkPoseTransfer_'+identity+'_session',skipSelect=True)
        cmds.addAttr(marker,ln=ATTRIBUTE,dt='string')
        s=dict(id=identity,version=1,marker=':mtkPoseTransfer_'+identity+'_session',root=uid(p['root']),pairs=[],original_root_pos=None,complete=False)
        save(s)
    obj=PoseTransfer()
    with scope(s):
        obj.root_controller=p['root']
        obj.controllers=p['controllers'] if action=='capture' else p.get('controllers',[])
        obj.locators=alive_locs(s) if action in ('capture','cleanup') else [resolve(pair['locator']) for pair in s['pairs']]
        obj.original_root_pos=s['original_root_pos']
        if action=='capture':
            obj.cleanup_locators()
            s.update(root=uid(p['root']),pairs=[],complete=False)
            ok=False
            try:
                ok=bool(obj.create_locators_and_record_pose())
            finally:
                s['pairs']=[dict(locator=uid(loc),controller=uid(ctrl),original_path=ctrl,shapes=[uid(n) for n in cmds.listRelatives(loc,allDescendents=True,fullPath=True) or []]) for loc,ctrl in zip(obj.locators,obj.controllers) if cmds.objExists(loc)]
                s['original_root_pos']=obj.original_root_pos
                s['complete']=ok and len(s['pairs'])==len(obj.controllers)
                save(s)
        elif action=='shift':
            obj.move_locators_to_new_root_position()
            s['original_root_pos']=obj.original_root_pos
            save(s)
        elif action=='apply':
            for loc,ctrl in zip(obj.locators,obj.controllers):
                cmds.setAttr(loc+'.original_controller',ctrl,type='string')
            obj.apply_pose_from_locators()
            for pair,ctrl in zip(s['pairs'],obj.controllers):
                pair['original_path']=ctrl
            save(s)
        else:
            obj.cleanup_locators()
            cmds.delete(s['marker'])
        p.update(session_id=s['id'],locators=[resolve(pair['locator']) for pair in s['pairs']] if action!='cleanup' else [])
    return ToolResult.ok('Pose Transfer操作完成',data=p,warnings=p['warnings'])
