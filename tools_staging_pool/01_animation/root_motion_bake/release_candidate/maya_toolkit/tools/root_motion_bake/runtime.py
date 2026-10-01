"""Original full workflow with whole-batch preflight and self-owned temporaries."""
from contextlib import contextmanager
import math
import re
import uuid

_session=None
_window=None


def require_scope():
    if _session is None:
        raise RuntimeError('Root Motion scene writers require the checked scope')


def resolve(name):
    import maya.cmds as cmds
    nodes=cmds.ls(name,long=True) or []
    if len(nodes)!=1 or '.' in name or 'transform' not in (cmds.nodeType(nodes[0],inherited=True) or []):
        raise ValueError('Unique transform/joint required: '+name)
    return nodes[0]


def identities(names):
    import maya.cmds as cmds
    return {cmds.ls(n,uuid=True)[0] for n in names if cmds.objExists(n)}


def safe_layer_name(root):
    require_scope()
    leaf=root.rsplit('|',1)[-1].replace(':','_')
    return 'mtkRootMotion_'+re.sub('[^A-Za-z0-9_]','_',leaf)+'_'+uuid.uuid4().hex[:12]+'_offsetLayer'


class NativeCommands:
    def __getattr__(self,name):
        from maya import cmds
        original=getattr(cmds,name)
        def call(*args,**kwargs):
            writes=name in ('pointConstraint','orientConstraint','bakeResults','setKeyframe','delete') or name in ('xform','animLayer') and not (kwargs.get('q') or kwargs.get('query'))
            if writes:
                require_scope()
            if name=='setKeyframe' and _session and _session.get('current_layer'):
                kwargs.setdefault('animLayer',_session['current_layer'])
            if name=='delete':
                nodes=args[0] if isinstance(args[0],(list,tuple)) else [args[0]]
                if not identities(nodes).issubset(_session['temporary']):
                    raise RuntimeError('Refusing to delete nodes not created by this workflow')
            result=original(*args,**kwargs)
            if name in ('pointConstraint','orientConstraint') and not (kwargs.get('q') or kwargs.get('query')):
                _session['temporary'].update(identities(result))
            if name=='animLayer' and not (kwargs.get('q') or kwargs.get('query') or kwargs.get('e') or kwargs.get('edit')):
                _session['layers'].append(result)
                _session['current_layer']=result
            return result
        return call


native_cmds=NativeCommands()


def discover():
    from maya import cmds
    buckets={}
    for n in cmds.ls(type='transform',long=True) or []:
        leaf=n.rsplit('|',1)[-1]
        ns,_,name=leaf.rpartition(':')
        text=name.lower()
        role='center' if 'rootx_m' in text else 'ring' if 'main' in text else 'root' if 'root' in text else None
        if role:
            buckets.setdefault(ns,{'root':[],'center':[],'ring':[]})[role].append(n)
    groups=[]
    ambiguous=[]
    for ns,b in sorted(buckets.items()):
        if any(len(v)>1 for v in b.values()):
            ambiguous.append({'namespace':ns,'matches':b})
        elif b['root'] and b['center']:
            groups.append({'root':b['root'][0],'center':b['center'][0],'ring':b['ring'][0] if b['ring'] else None})
    return {'groups':groups,'ambiguous':ambiguous}


def time_range(o):
    from maya import cmds,mel
    if o['start'] is not None:
        result=(o['start'],o['end'])
    elif o['time_range']=='timeline':
        result=(cmds.playbackOptions(q=True,minTime=True),cmds.playbackOptions(q=True,maxTime=True))
    elif o['time_range']=='animation':
        result=(cmds.playbackOptions(q=True,animationStartTime=True),cmds.playbackOptions(q=True,animationEndTime=True))
    else:
        if cmds.about(batch=True):
            raise ValueError('Selected time range needs interactive Maya or explicit start/end')
        slider=mel.eval('$mtkRootMotionTimeSlider=$gPlayBackSlider')
        if not cmds.timeControl(slider,q=True,rangeVisible=True):
            raise ValueError('No highlighted time range')
        a,b=cmds.timeControl(slider,q=True,rangeArray=True)
        result=(a,b-1)
    if not all(math.isfinite(v) for v in result) or not 0<result[1]-result[0]<=10000:
        raise ValueError('Nonempty bounded time range required, <=10000 frames')
    return list(result)


def prepare(o):
    from maya import cmds
    if o['action'] in ('inspect','discover'):
        return discover()
    if o['action'] in ('open_ui','close_ui'):
        if o['action']=='open_ui' and cmds.about(batch=True):
            raise ValueError('UI requires interactive Maya')
        return {'action':o['action']}
    if not o['translate_axes'] and not o['rotate_axes']:
        raise ValueError('At least one constraint axis required')
    info=discover() if o['groups'] is None else {'groups':o['groups'],'ambiguous':[]}
    if info['ambiguous'] and o['groups'] is None:
        raise ValueError('Ambiguous automatic groups; supply explicit groups')
    if not info['groups']:
        raise ValueError('No complete root/center group')
    groups=[]
    all_roots=[]
    for g in info['groups']:
        root,center=resolve(g['root']),resolve(g['center'])
        ring=resolve(g['ring']) if g.get('ring') else None
        if len(set([root,center]+([ring] if ring else [])))!=2+bool(ring):
            raise ValueError('Root/center/ring must be different')
        if root in all_roots or any(root.startswith(r+'|') or r.startswith(root+'|') for r in all_roots):
            raise ValueError('Batch roots must be unique without ancestry overlap')
        if ring and ring.startswith(root+'|'):
            raise ValueError('Ring cannot be below root: original relative arithmetic would feed back')
        if center.startswith(root+'|') and not o['snapshot_center']:
            raise ValueError('Center below root needs a snapshot to avoid constraint cycles')
        all_roots.append(root)
        if cmds.referenceQuery(root,isNodeReferenced=True) or any(cmds.lockNode(root,q=True,lock=True) or []):
            raise ValueError('Root is referenced or locked')
        attrs=cmds.listAttr(root,keyable=True,scalar=True) or []
        for attr in attrs:
            plug=root+'.'+attr
            if cmds.getAttr(plug,lock=True):
                raise ValueError('Original all-channel bake would touch locked '+plug)
            for src in cmds.listConnections(plug,s=True,d=False,plugs=True) or []:
                driver=src.split('.')[0]
                if not cmds.nodeType(driver).startswith('animCurveT') or cmds.referenceQuery(driver,isNodeReferenced=True) or any(cmds.lockNode(driver,q=True,lock=True) or []):
                    raise ValueError('Root has noneditable driver/layer/constraint: '+plug)
                consumers=cmds.listConnections(driver+'.output',s=False,d=True,plugs=True) or []
                if any(resolve(x.split('.')[0])!=root for x in consumers):
                    raise ValueError('Root animation curve has another consumer')
        for prefix,axes in (('translate',o['translate_axes']),('rotate',o['rotate_axes'])):
            for axis in axes:
                if prefix+axis.upper() not in attrs:
                    raise ValueError('Constraint channel must be keyable')
        if ring:
            for attr in ('translateX','translateY','translateZ','rotateX','rotateY','rotateZ'):
                if attr not in attrs:
                    raise ValueError('Ring step writes all translation/rotation channels')
        matrix=cmds.xform(root,q=True,worldSpace=True,matrix=True)
        if any(not math.isfinite(v) for v in matrix):
            raise ValueError('Nonfinite root transform')
        groups.append({'root':root,'center':center,'ring':ring,'baked_attributes':attrs})
    return {'groups':groups,'range':time_range(o),'snapshot_center':o['snapshot_center'],'warnings':['Original bake touches all keyable root attributes and preserveOutsideKeys=False','Original ring-relative position/rotation is world translation/Euler subtraction, not matrix-relative transform','No external files written; one Undo restores scene changes']}


@contextmanager
def scope():
    global _session
    from maya import cmds
    if _session is not None:
        raise RuntimeError('Root Motion scope already running')
    old=(cmds.ls(sl=True,long=True) or [],cmds.currentTime(q=True),cmds.autoKeyframe(q=True,state=True),cmds.namespaceInfo(currentNamespace=True,absoluteName=True))
    layers={l:{a:cmds.animLayer(l,q=True,**{a:True}) for a in ('selected','preferred','lock','mute','solo')} for l in cmds.ls(type='animLayer') or []}
    _session={'temporary':set(),'layers':[],'current_layer':None}
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        for l in layers:
            cmds.animLayer(l,e=True,selected=False,preferred=False)
        yield _session
    finally:
        session=_session
        try:
            # Names may be changed by Maya; UUID ownership determines cleanup.
            owned=[n for n in cmds.ls(long=True) or [] if cmds.ls(n,uuid=True)[0] in session['temporary']]
            for n in sorted(owned,key=lambda s:s.count('|'),reverse=True):
                if cmds.objExists(n):
                    descendants=cmds.listRelatives(n,allDescendents=True,fullPath=True) or [] if cmds.objectType(n,isAType='dagNode') else []
                    if not identities(descendants).issubset(session['temporary']):
                        raise RuntimeError('Temporary object has external descendants; use Undo')
                    cmds.delete(n)
        finally:
            try:
                for l in session['layers']:
                    if cmds.objExists(l):
                        cmds.animLayer(l,e=True,selected=False,preferred=False)
                for l,flags in layers.items():
                    if cmds.objExists(l):
                        cmds.animLayer(l,e=True,**flags)
                cmds.currentTime(old[1])
                cmds.namespace(setNamespace=old[3])
                cmds.autoKeyframe(state=old[2])
                live=[n for n in old[0] if cmds.objExists(n)]
                cmds.select(live,replace=True) if live else cmds.select(clear=True)
            finally:
                _session=None


def center_snapshot(center,a,b):
    from maya import cmds
    require_scope()
    helper=cmds.spaceLocator(name='mtkRootMotion_center_'+uuid.uuid4().hex[:12])[0]
    _session['temporary'].update(identities([helper]+(cmds.listRelatives(helper,shapes=True,fullPath=True) or [])))
    samples=sorted(set([a,b]+[a+i for i in range(int(math.floor(b-a))+1)]))
    # Capture all source poses before any root is changed, including source pivots.
    for t in samples:
        cmds.currentTime(t)
        matrix=cmds.xform(center,q=True,worldSpace=True,matrix=True)
        cmds.xform(helper,worldSpace=True,matrix=matrix)
        pivot=cmds.xform(center,q=True,worldSpace=True,rotatePivot=True)
        cmds.setAttr(helper+'.scale',1,1,1)
        cmds.setAttr(helper+'.shear',0,0,0)
        cmds.xform(helper,worldSpace=True,translation=pivot)
        cmds.setKeyframe(helper,at=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ'],time=t,inTangentType='linear',outTangentType='linear')
    return helper


def relative_on_layer(worker,root,ring,relative_pos,relative_rot):
    """Run original world/Euler arithmetic on an unconnected duplicate, then key the layer.

The original two xform calls on a driven root lose evaluated translation before
setKeyframe. The duplicate lets Maya solve the same pivots/parent/rotate order
without changing that arithmetic or guessing Euler/matrix conversion.
"""
    from maya import cmds
    require_scope()
    layer=_session['current_layer']
    if not layer:
        raise RuntimeError('No offset layer for relative transform')
    clone=cmds.duplicate(root,parentOnly=True,inputConnections=False,name='mtkRootMotion_local_'+uuid.uuid4().hex[:12])[0]
    _session['temporary'].update(identities([clone]))
    worker.original_set_relative_transform(clone,ring,relative_pos,relative_rot)
    values={a:cmds.getAttr(clone+'.'+a) for a in ('translateX','translateY','translateZ','rotateX','rotateY','rotateZ')}
    for a,v in values.items():
        cmds.setKeyframe(root+'.'+a,time=cmds.currentTime(q=True),value=v,animLayer=layer)
    cmds.delete(clone)


def execute(o,plan):
    global _window
    from maya import cmds
    if o['action'] in ('inspect','discover'):
        return plan
    if o['action']=='open_ui':
        from .native import ConstraintBakeTool
        _window=ConstraintBakeTool()
        return {'window':_window.window_name}
    if o['action']=='close_ui':
        if cmds.window('mtkRootMotionBakeCandidateWindow',exists=True):
            cmds.deleteUI('mtkRootMotionBakeCandidateWindow',window=True)
        _window=None
        return {'closed':True}
    from .native import ConstraintBakeTool
    worker=ConstraintBakeTool.__new__(ConstraintBakeTool)
    with scope() as session:
        a,b=plan['range']
        centers={g['center']:center_snapshot(g['center'],a,b) for g in plan['groups']} if o['snapshot_center'] else {}
        for g in plan['groups']:
            session['current_layer']=None
            cmds.currentTime(a)
            worker.process_single_group(g['root'],centers.get(g['center'],g['center']),g['ring'],o['translate_axes'],o['rotate_axes'],o['maintain_offset'],a,b)
        output={'groups':plan['groups'],'range':plan['range'],'layers':list(session['layers']),'warnings':plan['warnings']}
    return output
