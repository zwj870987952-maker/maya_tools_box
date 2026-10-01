"""World pose clipboard and hierarchy-first repeated restore, without autorun."""
import copy
import json
import math
from pathlib import Path
import uuid
from maya_toolkit.framework import BaseMayaTool, ToolResult

_CLIPBOARD=None
IDENTITY=[1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.,0.,0.,0.,0.,1.]


def finite(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and abs(value)<=1e12


def normalize(values):
    defaults=dict(action='inspect',objects=None,snapshot=None,path=None,channels='both',start=None,end=None,
                  only_keyframes=False,max_attempts=10,full_check_attempts=5)
    if set(values)-set(defaults): raise ValueError('Unknown parameters')
    p=dict(defaults,**values)
    if p['action'] not in ('inspect','copy','paste','save','load'): raise ValueError('Invalid action')
    if p['channels'] not in ('both','translate','rotate'): raise ValueError('Invalid channel group')
    for key in ('max_attempts','full_check_attempts'):
        if type(p[key]) is not int or not 1<=p[key]<=50: raise ValueError('Attempt counts must be integers 1..50')
    if type(p['only_keyframes']) is not bool: raise ValueError('only_keyframes must be bool')
    if p['objects'] is not None and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(x,str) or not x or '*' in x or '.' in x for x in p['objects']) or len(set(p['objects']))!=len(p['objects'])): raise ValueError('Unique whole objects required')
    if (p['start'] is None)!=(p['end'] is None): raise ValueError('Supply both inclusive range bounds')
    if p['start'] is not None and (not finite(p['start']) or not finite(p['end']) or p['end']<p['start'] or p['end']-p['start']>9999): raise ValueError('Invalid or excessive range')
    if p['snapshot'] is not None: check_snapshot(p['snapshot'])
    if p['action'] in ('save','load'):
        if not isinstance(p['path'],str) or not Path(p['path']).is_absolute() or Path(p['path']).suffix.lower()!='.json': raise ValueError('Absolute JSON path required')
    elif p['path'] is not None: raise ValueError('Only explicit save/load accesses files')
    if p['action']!='paste' and any(k in values for k in ('channels','start','end','only_keyframes','max_attempts','full_check_attempts')): raise ValueError('Paste options only apply to paste')
    if p['action'] in ('save','load') and p['objects'] is not None: raise ValueError('File actions do not select scene objects')
    if p['action'] in ('copy','inspect','load') and p['snapshot'] is not None: raise ValueError('Snapshot only applies to paste/save')
    return p


def check_snapshot(s):
    if not isinstance(s,dict) or set(s)!=set(('version','linear_unit','angle_unit','rows')) or type(s['version']) is not int or s['version']!=1: raise ValueError('Invalid snapshot format')
    if s['linear_unit'] not in ('mm','cm','m','km','in','ft','yd','mi') or s['angle_unit'] not in ('deg','rad'): raise ValueError('Invalid snapshot units')
    if not isinstance(s['rows'],list) or not 1<=len(s['rows'])<=10000: raise ValueError('Invalid snapshot rows')
    seen=set()
    for row in s['rows']:
        if not isinstance(row,dict) or set(row)!=set(('uuid','path','pos','rot','rotate_order')): raise ValueError('Invalid row fields')
        if not isinstance(row['uuid'],str) or not row['uuid'] or row['uuid'] in seen or not isinstance(row['path'],str) or not row['path'].startswith('|'): raise ValueError('Invalid or duplicate identity')
        seen.add(row['uuid'])
        try: uuid.UUID(row['uuid'])
        except (ValueError,AttributeError): raise ValueError('Real UUID required; names/patterns are not identities')
        if type(row['rotate_order']) is not int or not 0<=row['rotate_order']<=5: raise ValueError('Invalid rotation order')
        for key in ('pos','rot'):
            if not isinstance(row[key],list) or len(row[key])!=3 or not all(finite(v) for v in row[key]): raise ValueError('Invalid pose values')
    return copy.deepcopy(s)


def resolve(name):
    from maya import cmds
    from maya.api import OpenMaya as om
    matches=cmds.ls(name,long=True) or []
    if len(matches)!=1 or '.' in matches[0] or cmds.nodeType(matches[0]) not in ('transform','joint'): raise ValueError('Unique transform/joint required: '+name)
    node=matches[0]; selected=om.MSelectionList(); selected.add(node)
    if len(om.MDagPath.getAllPathsTo(selected.getDagPath(0).node()))!=1: raise ValueError('Instanced DAG rejected: '+node)
    return node


def capture(objects=None):
    from maya import cmds
    targets=objects if objects is not None else (cmds.ls(selection=True,long=True) or [])
    if not targets: raise ValueError('Select objects to copy/inspect')
    rows=[]; seen=set()
    for name in targets:
        node=resolve(name); identity=cmds.ls(node,uuid=True)[0]
        if identity in seen: raise ValueError('Alias duplicates')
        seen.add(identity)
        rows.append(dict(uuid=identity,path=node,pos=cmds.xform(node,query=True,worldSpace=True,translation=True),rot=cmds.xform(node,query=True,worldSpace=True,rotation=True),rotate_order=cmds.getAttr(node+'.rotateOrder')))
    return check_snapshot(dict(version=1,linear_unit=cmds.currentUnit(query=True,linear=True),angle_unit=cmds.currentUnit(query=True,angle=True),rows=rows))


def snapshot(p):
    value=p['snapshot'] if p['snapshot'] is not None else _CLIPBOARD
    if value is None: raise ValueError('No snapshot; copy or load first, or pass snapshot')
    return check_snapshot(value)


def attributes(channels):
    return [group+axis for group in (('translate','rotate') if channels=='both' else (channels,)) for axis in 'XYZ']


def writable(node,attrs,frames):
    from maya import cmds
    if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True)): raise ValueError('Reference/node lock rejected: '+node)
    if cmds.getAttr(node+'.offsetParentMatrix')!=IDENTITY: raise ValueError('offsetParentMatrix unsupported')
    for group in set(a[:-1] for a in attrs):
        if cmds.getAttr(node+'.'+group,lock=True) or cmds.listConnections(node+'.'+group,source=True,destination=False,plugs=True,skipConversionNodes=False):
            # Parent compound connections includes child curves; child checks below decide.
            if cmds.getAttr(node+'.'+group,lock=True): raise ValueError('Compound locked')
            direct=cmds.connectionInfo(node+'.'+group,isExactDestination=True)
            if direct: raise ValueError('Compound driver unsupported')
    for attr in attrs:
        plug=node+'.'+attr
        if cmds.getAttr(plug,lock=True) or not cmds.getAttr(plug,keyable=True): raise ValueError('Locked/nonkeyable channel: '+plug)
        incoming=cmds.listConnections(plug,source=True,destination=False,plugs=True,skipConversionNodes=False) or []
        if incoming:
            if len(incoming)!=1: raise ValueError('Multiple drivers')
            curve=incoming[0].split('.')[0]
            expected='animCurveTL' if attr.startswith('translate') else 'animCurveTA'
            if cmds.nodeType(curve)!=expected or cmds.referenceQuery(curve,isNodeReferenced=True) or any(cmds.lockNode(curve,query=True,lock=True)) or cmds.getAttr(curve+'.ktv',lock=True): raise ValueError('Only owned editable direct time curves supported')
            consumers=cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True) or []
            if len(consumers)!=1 or resolve(consumers[0].split('.')[0])!=node or consumers[0].split('.')[-1]!=attr: raise ValueError('Shared curve rejected')
            sources=cmds.listConnections(curve+'.input',source=True,destination=False,plugs=True) or []
            if sources not in ([],['time1.outTime'],['time1.unwarpedTime']): raise ValueError('Nonstandard animation time rejected: '+str(sources))
    # Future evaluated matrices are read without time changes; reject unsupported sheared/mirrored chains.
    chain=[node]; parent=cmds.listRelatives(node,parent=True,fullPath=True)
    while parent:
        chain.append(parent[0]); parent=cmds.listRelatives(parent[0],parent=True,fullPath=True)
    for frame in frames:
        for ancestor in chain:
            if any(abs(v)>1e-9 for v in cmds.getAttr(ancestor+'.shear',time=frame)[0]) or any(v<=1e-9 for v in cmds.getAttr(ancestor+'.scale',time=frame)[0]): raise ValueError('Shear/reflection/zero scale unsupported')


def plan(p):
    from maya import cmds
    s=snapshot(p)
    if s['linear_unit']!=cmds.currentUnit(query=True,linear=True) or s['angle_unit']!=cmds.currentUnit(query=True,angle=True): raise ValueError('Snapshot and current scene units differ; use matching units')
    rows=[]; selected=p['objects'] if p['objects'] is not None else (cmds.ls(selection=True,long=True) or [])
    chosen=None
    if selected:
        chosen=[cmds.ls(resolve(n),uuid=True)[0] for n in selected]
        if len(chosen)!=len(set(chosen)): raise ValueError('Alias duplicates')
        if set(chosen)-set(r['uuid'] for r in s['rows']): raise ValueError('Selected targets were not copied')
    for row in s['rows']:
        if chosen is not None and row['uuid'] not in chosen: continue
        matches=cmds.ls(row['uuid'],long=True) or []
        if not matches:
            if chosen is not None: raise ValueError('Copied target deleted')
            continue
        node=resolve(row['uuid'])
        if cmds.getAttr(node+'.rotateOrder')!=row['rotate_order']: raise ValueError('Rotation order changed since copy')
        rows.append(dict(row,node=node))
    if not rows: raise ValueError('No copied live targets')
    rows.sort(key=lambda r:r['node'].count('|'))
    attrs=attributes(p['channels']); current=cmds.currentTime(query=True)
    warnings=[]
    if p['start'] is None: frames=[current]
    elif p['only_keyframes']:
        frames=sorted({t for r in rows for a in attrs for t in (cmds.keyframe(r['node'],attribute=a,query=True,timeChange=True) or []) if p['start']<=t<=p['end']})
        if not frames: frames=[current]; warnings.append('No keys in chosen channels/range; original current-frame fallback applies')
    else:
        if int(p['start'])!=p['start'] or int(p['end'])!=p['end']: raise ValueError('All-frame range requires integer bounds; keyed-only range supports fractional keys')
        frames=list(range(int(p['start']),int(p['end'])+1))
    if len(frames)*len(rows)>100000: raise ValueError('Excessive evaluation workload')
    for row in rows: writable(row['node'],attrs,frames)
    return s,rows,attrs,frames,warnings


def residual(row,channels,rotation_check=True):
    from maya import cmds
    failed=[]
    if channels!='rotate':
        actual=cmds.xform(row['node'],query=True,worldSpace=True,translation=True)
        if any(abs(a-b)>=.01 for a,b in zip(actual,row['pos'])): failed.append('translate')
    if channels!='translate' and rotation_check:
        actual=cmds.xform(row['node'],query=True,worldSpace=True,rotation=True)
        period=360. if cmds.currentUnit(query=True,angle=True)=='deg' else math.tau
        tolerance=.01 if period==360 else math.radians(.01)
        if any(abs((a-b+period/2)%period-period/2)>=tolerance for a,b in zip(actual,row['rot'])): failed.append('rotate')
    return failed


class WorldTransformV4Tool(BaseMayaTool):
    tool_id='world_transform_v4'; tool_name='世界坐标复制还原 V4'; category='modeling_surfacing'; version='1.0.0-candidate1'
    description='Copy one world pose; restore copied live UUID objects hierarchy-first and key requested translation/rotation groups.'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','copy','paste','save','load'],'default':'inspect'},
        'objects':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True},
        'snapshot':{'type':'object','description':'Versioned UUID pose returned by copy; exact fields validated by API'},
        'path':{'type':'string','description':'Absolute JSON path; save exclusively creates, load only reads'},
        'channels':{'type':'string','enum':['both','translate','rotate'],'default':'both'},
        'start':{'type':'number'},'end':{'type':'number','description':'Inclusive range end'},
        'only_keyframes':{'type':'boolean','default':False},
        'max_attempts':{'type':'integer','minimum':1,'maximum':50,'default':10},
        'full_check_attempts':{'type':'integer','minimum':1,'maximum':50,'default':5}}}

    def validate(self,**values):
        try:
            p=normalize(values)
            if p['action'] in ('copy','inspect'): data={'snapshot':capture(p['objects'])}
            elif p['action']=='paste':
                s,rows,attrs,frames,warnings=plan(p)
                return ToolResult.ok(message='World pose paste preflight passed',data={'objects':[r['node'] for r in rows],'attributes':attrs,'frames':frames},warnings=warnings)
            elif p['action']=='save':
                data={'snapshot':snapshot(p),'path':p['path']}; path=Path(p['path'])
                if path.exists() or path.is_symlink() or not path.parent.is_dir(): raise ValueError('Save requires existing directory and unused file name')
            else:
                path=Path(p['path'])
                if not path.is_file() or path.is_symlink() or path.stat().st_size>8*1024*1024: raise ValueError('Load requires regular bounded JSON file')
                data={'snapshot':check_snapshot(json.loads(path.read_text(encoding='utf8'))),'path':p['path']}
            return ToolResult.ok(message='Preflight passed',data=data)
        except Exception as exc: return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**values):
        global _CLIPBOARD
        from maya import cmds
        p=normalize(values)
        if p['action'] in ('copy','inspect'):
            s=capture(p['objects'])
            if p['action']=='copy': _CLIPBOARD=copy.deepcopy(s)
            return ToolResult.ok(message='World pose captured' if p['action']=='copy' else 'World pose inspected',data={'snapshot':s})
        if p['action']=='save':
            s=snapshot(p)
            with Path(p['path']).open('x',encoding='utf8') as stream: json.dump(s,stream,ensure_ascii=False,indent=2)
            return ToolResult.ok(message='Snapshot saved; external file is not Maya Undoable',data={'path':p['path'],'snapshot':s})
        if p['action']=='load':
            s=check_snapshot(json.loads(Path(p['path']).read_text(encoding='utf8'))); _CLIPBOARD=copy.deepcopy(s)
            return ToolResult.ok(message='Snapshot loaded to memory',data={'snapshot':s})
        s,rows,attrs,frames,warnings=plan(p); current=cmds.currentTime(query=True); auto=cmds.autoKeyframe(query=True,state=True)
        completed=[]; window=False; cancelled=False
        try:
            if auto: cmds.autoKeyframe(state=False)
            if len(frames)>1 and not cmds.about(batch=True):
                cmds.progressWindow(title='处理世界坐标',progress=0,maxValue=len(frames),isInterruptable=True); window=True
            for index,frame in enumerate(frames):
                if window and cmds.progressWindow(query=True,isCancelled=True): cancelled=True; break
                cmds.currentTime(frame)
                for attempt in range(p['max_attempts']):
                    for row in rows:
                        if p['channels']!='rotate': cmds.xform(row['node'],worldSpace=True,translation=row['pos'])
                        if p['channels']!='translate': cmds.xform(row['node'],worldSpace=True,rotation=row['rot'])
                    full=attempt<p['full_check_attempts'] or attempt+1==p['max_attempts']
                    failed={r['node']:residual(r,p['channels'],full) for r in rows}
                    failed={n:bad for n,bad in failed.items() if bad}
                    # Every reported success includes a complete final rotation check.
                    if not failed:
                        failed={r['node']:residual(r,p['channels']) for r in rows}
                        failed={n:bad for n,bad in failed.items() if bad}
                        if not failed: break
                    if attempt+1==p['max_attempts']: raise RuntimeError('World restore did not converge at '+str(frame)+': '+str(failed))
                for row in rows: cmds.setKeyframe(row['node'],attribute=attrs,time=frame)
                completed.append(frame)
                if window: cmds.progressWindow(edit=True,progress=index+1,status='Frame '+str(frame))
        finally:
            if window: cmds.progressWindow(endProgress=True)
            cmds.currentTime(current)
            if auto: cmds.autoKeyframe(state=True)
        data={'objects':[r['node'] for r in rows],'attributes':attrs,'frames':completed,'cancelled':cancelled}
        if cancelled: return ToolResult.fail(message='Cancelled; completed frames remain in one Undo chunk',data=data,errors=['CANCELLED'],warnings=warnings)
        return ToolResult.ok(message='World pose restored and keyed on '+str(len(completed))+' frames',data=data,warnings=warnings)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya UI required')
        from .ui import show_world_transform_ui
        return show_world_transform_ui()


def copy_world_transform(): return WorldTransformV4Tool().run(action='copy')
def paste_world_transform(**values): return WorldTransformV4Tool().run(action='paste',**values)
def show_world_transform_ui(): return WorldTransformV4Tool().show_ui()
