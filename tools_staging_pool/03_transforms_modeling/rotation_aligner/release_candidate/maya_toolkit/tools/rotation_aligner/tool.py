import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

AXES=['+X','-X','+Y','-Y','+Z','-Z']
DEFAULTS=dict(full_alignment=False,rotate_axes={'x':True,'y':True,'z':True},source_axis='+Y',target_axis='+Y',time_mode='timeline',custom_start=1,custom_end=1,bake_all_frames=True,per_frame_iters=5,time_next_frame=False)
PAIR_KEYS={'source','target','source_child','target_child'}
PROPS={'pairs':{'type':'array','items':{'type':'object','properties':{k:{'type':'string'} for k in PAIR_KEYS},'required':['source','target'],'additionalProperties':False}}}
for key,value in DEFAULTS.items():
    PROPS[key]={'type':'object','properties':{a:{'type':'boolean'} for a in 'xyz'},'required':list('xyz'),'additionalProperties':False,'default':value} if key=='rotate_axes' else {'type':'boolean' if type(value) is bool else 'integer' if type(value) is int else 'string','default':value}
for key in ('source_axis','target_axis'): PROPS[key]['enum']=AXES
PROPS['time_mode']['enum']=['single','custom','timeline']; PROPS['per_frame_iters'].update(minimum=1,maximum=100)


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(DEFAULTS); p.update(kwargs)
    for key,value in DEFAULTS.items():
        if type(p[key]) is not type(value): raise ValueError('Invalid type: '+key)
    if set(p['rotate_axes'])!=set('xyz') or any(type(v) is not bool for v in p['rotate_axes'].values()): raise ValueError('Exact boolean x/y/z mask required')
    if not any(p['rotate_axes'].values()): raise ValueError('At least one rotate axis required')
    if p['source_axis'] not in AXES or p['target_axis'] not in AXES or p['time_mode'] not in PROPS['time_mode']['enum']: raise ValueError('Unknown signed axis/time mode')
    if not 1<=p['per_frame_iters']<=100: raise ValueError('Iterations must be 1..100')
    if p['time_next_frame'] and p['time_mode']!='single': raise ValueError('Next-frame applies only to single mode')
    if 'pairs' in p:
        if not isinstance(p['pairs'],list) or not p['pairs']: raise ValueError('Nonempty pair rows required')
        for row in p['pairs']:
            if not isinstance(row,dict) or not {'source','target'}<=set(row) or set(row)-PAIR_KEYS or any(not isinstance(n,str) or not n for n in row.values()): raise ValueError('Explicit pair fields required')
    return p


def resolve(value):
    from maya import cmds
    from maya.api import OpenMaya as om
    if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Exact whole transform/joint required')
    matches=cmds.ls(value,long=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous node: '+value)
    n=matches[0]
    if cmds.nodeType(n) not in ('transform','joint'): raise ValueError('Transform/joint required')
    selection=om.MSelectionList(); selection.add(n)
    if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1: raise ValueError('Instanced DAG unsupported')
    return n,cmds.ls(n,uuid=True)[0]


def valid_matrix(n):
    from maya import cmds
    matrix=cmds.xform(n,query=True,worldSpace=True,matrix=True)
    if any(not math.isfinite(v) for v in matrix): raise ValueError('Nonfinite world matrix')
    vectors=[matrix[i:i+3] for i in (0,4,8)]
    norms=[math.sqrt(sum(v*v for v in row)) for row in vectors]
    if min(norms)<1e-9: raise ValueError('Degenerate scale')
    for i,j in ((0,1),(0,2),(1,2)):
        if abs(sum(a*b for a,b in zip(vectors[i],vectors[j]))/(norms[i]*norms[j]))>1e-6: raise ValueError('Sheared world orientation unsupported')
    from maya.api import OpenMaya as om
    if om.MMatrix(matrix).det3x3()<=0: raise ValueError('Reflected world orientation unsupported')


def writable(n,p):
    from maya import cmds
    if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Writable source referenced/locked')
    valid_matrix(n)
    if cmds.objExists(n+'.offsetParentMatrix'):
        matrix=cmds.getAttr(n+'.offsetParentMatrix')
        if any(abs(v-(1.0 if i in (0,5,10,15) else 0.0))>1e-10 for i,v in enumerate(matrix)): raise ValueError('Writable source offsetParentMatrix must be identity')
    mask={axis:False for axis in 'xyz'}
    for axis,enabled in p['rotate_axes'].items():
        plug=n+'.rotate'+axis.upper()
        if not enabled or cmds.getAttr(plug,lock=True): continue
        connections=cmds.listConnections(plug,source=True,destination=False,plugs=True) or []
        for upstream in connections:
            curve=upstream.rsplit('.',1)[0]
            if p['time_mode']=='single' or not cmds.nodeType(curve).startswith('animCurve') or cmds.nodeType(curve)!='animCurveTA': raise ValueError('Single animated source/constraint/layer/driver unsupported')
            if cmds.referenceQuery(curve,isNodeReferenced=True) or any(cmds.lockNode(curve,query=True,lock=True) or []) or cmds.getAttr(curve+'.ktv',lock=True): raise ValueError('Animation curve referenced/locked')
            consumers=cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True) or []
            if len(consumers)!=1 or cmds.ls(consumers[0].rsplit('.',1)[0],uuid=True)!=cmds.ls(n,uuid=True): raise ValueError('Shared animation curve unsupported')
        mask[axis]=True
    if not any(mask.values()): raise ValueError('No unlocked requested source rotation axes')
    return mask


def frames(p,target):
    from maya import cmds
    if p['time_mode']=='single': return [float(cmds.currentTime(query=True))]
    start,end=(p['custom_start'],p['custom_end']) if p['time_mode']=='custom' else (cmds.playbackOptions(query=True,minTime=True),cmds.playbackOptions(query=True,maxTime=True))
    start,end=sorted((start,end))
    if p['bake_all_frames']:
        if end-start>10000: raise ValueError('Frame range exceeds 10000')
        if start!=int(start) or end!=int(end): raise ValueError('All-frame bake bounds must be whole frames')
        return list(range(int(start),int(end)+1))
    return sorted(set(cmds.keyframe(target,query=True,time=(start,end),timeChange=True) or []))


def plan(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    raw=p.get('pairs')
    if raw is None:
        selected=cmds.ls(selection=True,long=True) or []
        if len(selected)==2: raw=[dict(source=selected[0],target=selected[1])]
        elif len(selected)==4: raw=[dict(source=selected[0],source_child=selected[1],target=selected[2],target_child=selected[3])]
        else: raise ValueError('Provide pair rows or select 2/4 objects; original 6-object up inputs were unused and are unsupported')
    rows=[]; ids=set()
    for row in raw:
        nodes={key:resolve(value)[0] for key,value in row.items()}; source,uid=resolve(nodes['source']); target,tuid=resolve(nodes['target'])
        if uid==tuid or uid in ids: raise ValueError('Self alignment or duplicate writable source')
        ids.add(uid); mask=writable(source,p); valid_matrix(target)
        for key in ('source_child','target_child'):
            if key in nodes:
                parent=nodes['source'] if key=='source_child' else nodes['target']
                if not nodes[key].startswith(parent+'|'): raise ValueError('Fallback child must be a descendant of its corresponding object')
        rows.append(dict(nodes,source_uuid=uid,target_uuid=tuid,rotate_axes=mask,frames=frames(p,target)))
    if not any(row['frames'] for row in rows): raise ValueError('No reference keys in selected range')
    if sum(len(row['frames']) for row in rows)*p['per_frame_iters']>100000: raise ValueError('Too many frame iterations')
    return {'parameters':p,'rows':rows,'range_writes_keys':p['time_mode']!='single','source_is_modified':True}


class ScopedCommands:
    def __init__(self,row,p):
        from maya import cmds
        self.real=cmds; self.row=row; self.p=p; self.errors=[]; self.writes=0
        self.rad=cmds.currentUnit(query=True,angle=True)=='rad'

    def __getattr__(self,name):
        if name not in ('xform','getAttr','attributeQuery','objectType','listRelatives','warning'): raise RuntimeError('Native command outside supported read/write set: '+name)
        return getattr(self.real,name)

    def getAttr(self,plug,**kwargs):
        value=self.real.getAttr(plug,**kwargs)
        if self.rad and not kwargs and plug.rsplit('.',1)[-1] in ('rotate','rotateAxis','jointOrient'):
            return [tuple(math.degrees(v) for v in value[0])]
        if self.rad and not kwargs and plug.rsplit('.',1)[-1] in ('rotateX','rotateY','rotateZ'): return math.degrees(value)
        return value

    def setAttr(self,plug,value,**kwargs):
        try:
            node_name,attr=plug.rsplit('.',1)
            if node_name!=self.row['source'] or attr not in ('rotateX','rotateY','rotateZ') or not self.row['rotate_axes'][attr[-1].lower()] or kwargs or not math.isfinite(value): raise ValueError('Native write outside validated rotation scope')
            actual=math.radians(value) if self.rad else value
            if self.p['time_mode']=='single': self.real.setAttr(plug,actual)
            else: self.real.setKeyframe(node_name,attribute=attr,time=self.real.currentTime(query=True),value=actual)
            self.writes+=1
        except Exception as e: self.errors.append(str(e)); raise


class RotationAlignerTool(BaseMayaTool):
    tool_id='rotation_aligner'; tool_name='旋转对齐工具'; category='modeling_surfacing'; version='1.0-candidate.1'
    description='完整原单轴/完全两步对齐与旋转限制/多对/范围迭代UI；旋转源对象到参考目标，完整原矩阵逻辑，真实范围关键帧写入/Undo/预检。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        from . import native
        p=normalize(kwargs); data=plan(p); current=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True); original_cmds=native.cmds; succeeded=False
        try:
            cmds.autoKeyframe(state=False)
            for row in data['rows']:
                settings=dict(p,rotate_axes=row['rotate_axes']); proxy=ScopedCommands(row,p); native.cmds=proxy
                for frame in row['frames']:
                    cmds.currentTime(frame,edit=True); valid_matrix(row['source']); valid_matrix(row['target'])
                    for _ in range(p['per_frame_iters']):
                        fn=native.align_object_to_target_full if p['full_alignment'] else native.align_object_to_target
                        if not fn(row['source'],row['target'],row.get('source_child'),row.get('target_child'),settings=settings): raise ValueError('Native alignment reported failure')
                        if proxy.errors: raise RuntimeError('; '.join(proxy.errors))
                row['channel_writes']=proxy.writes
            succeeded=True; return ToolResult.ok(data=data)
        finally:
            native.cmds=original_cmds; cmds.autoKeyframe(state=auto)
            cmds.currentTime(current+1 if succeeded and p['time_mode']=='single' and p['time_next_frame'] else current,edit=True)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import bind
        return bind(self)
