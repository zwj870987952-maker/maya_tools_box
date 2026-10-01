import math
import re
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

PROPS={'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'pairs':{'type':'array','items':{'type':'object','properties':{'source':{'type':'string'},'target':{'type':'string'}},'required':['source','target'],'additionalProperties':False}},'left':{'type':'string','default':'_L'},'right':{'type':'string','default':'_R'},'include_hierarchy':{'type':'boolean','default':False},'plane':{'type':'string','enum':['XY','YZ','XZ'],'default':'XY'},'mode':{'type':'string','enum':['orientation','behavior','copy'],'default':'orientation'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(left='_L',right='_R',include_hierarchy=False,plane='XY',mode='orientation'); p.update(kwargs)
    if type(p['include_hierarchy']) is not bool: raise ValueError('Boolean hierarchy required')
    for key in ('left','right'):
        if not isinstance(p[key],str) or not re.fullmatch(r'[A-Za-z0-9_]+',p[key]): raise ValueError('Naming tokens must be nonempty letters/digits/underscores')
    if p['left'] in p['right'] or p['right'] in p['left']: raise ValueError('Distinct nonoverlapping naming tokens required')
    if p['plane'] not in PROPS['plane']['enum'] or p['mode'] not in PROPS['mode']['enum']: raise ValueError('Unknown plane/mode')
    if 'objects' in p:
        if not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects'])): raise ValueError('Unique explicit objects required')
    if 'pairs' in p:
        if 'objects' in p or p['include_hierarchy'] or not isinstance(p['pairs'],list) or not p['pairs']: raise ValueError('Explicit pairs exclude objects and hierarchy expansion')
        for row in p['pairs']:
            if not isinstance(row,dict) or set(row)!={'source','target'} or any(not isinstance(n,str) or not n for n in row.values()): raise ValueError('Exact source/target strings required')
    return p


def opposite(name,left,right):
    # Keep namespace spelling; only basename naming tokens indicate side.
    namespace,separator,base=name.rpartition(':')
    if not separator: base=name
    if left in base and right in base: raise ValueError('Name contains both side tokens')
    if left in base: mirrored=base.replace(left,right)
    elif right in base: mirrored=base.replace(right,left)
    else: return None
    return namespace+':'+mirrored if separator else mirrored


def mirrored_values(position,world_rotation,scale,local_rotation,plane,mode):
    position=list(position); position[{'XY':2,'YZ':0,'XZ':1}[plane]]*=-1
    x,y,z=world_rotation
    if mode=='copy': rotation=list(local_rotation)
    elif mode=='orientation': rotation={'XY':[-x,-y,z],'YZ':[-x,y,-z],'XZ':[x,-y,-z]}[plane]
    else: rotation={'XY':[-x+180,-y,z+180],'YZ':[-x,-y+180,z+180],'XZ':[x+180,-y+180,-z]}[plane]
    return {'translation':position,'rotation':rotation,'scale':list(scale),'rotation_space':'object' if mode=='copy' else 'world'}


def resolve(value,write=False):
    from maya import cmds
    from maya.api import OpenMaya as om
    if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Exact transform node required')
    matches=cmds.ls(value,long=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous transform: '+value)
    n=matches[0]
    if cmds.nodeType(n)!='transform': raise ValueError('Plain transform required; joints/shapes unsupported')
    selection=om.MSelectionList(); selection.add(n)
    if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1: raise ValueError('Instanced transform unsupported')
    if write:
        if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Target is referenced/locked')
        for attr in ('translate','rotate','scale'):
            for axis in 'XYZ':
                plug=n+'.'+attr+axis
                if cmds.getAttr(plug,lock=True) or cmds.listConnections(plug,source=True,destination=False): raise ValueError('Target channel locked/driven: '+plug)
        if any(abs(v)>1e-10 for v in cmds.getAttr(n+'.shear')[0]): raise ValueError('Target shear unsupported')
        if min(cmds.getAttr(n+'.scale')[0])<=0: raise ValueError('Target local scale must be positive')
        if cmds.objExists(n+'.offsetParentMatrix'):
            matrix=cmds.getAttr(n+'.offsetParentMatrix')
            if any(abs(v-(1.0 if i in (0,5,10,15) else 0.0))>1e-10 for i,v in enumerate(matrix)): raise ValueError('Target offsetParentMatrix must be identity')
        parent=cmds.listRelatives(n,parent=True,fullPath=True) or []
        while parent:
            scale=cmds.getAttr(parent[0]+'.scale')[0]; shear=cmds.getAttr(parent[0]+'.shear')[0]
            if min(scale)<=0 or max(scale)-min(scale)>1e-10 or any(abs(v)>1e-10 for v in shear): raise ValueError('Target parent chain must have positive uniform scale and no shear')
            parent=cmds.listRelatives(parent[0],parent=True,fullPath=True) or []
    return n,cmds.ls(n,uuid=True)[0]


def auto_target(source,p):
    from maya import cmds
    leaf=opposite(source.split('|')[-1],p['left'],p['right'])
    if not leaf: return None
    parts=[opposite(part,p['left'],p['right']) or part for part in source.split('|') if part]
    expected='|'+'|'.join(parts)
    if cmds.objExists(expected): return resolve(expected,True)[0]
    return resolve(leaf,True)[0]


def plan(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    skipped=[]; rows=[]
    if 'pairs' in p: raw=p['pairs']
    else:
        sources=[]; ids=set()
        for value in p.get('objects') or cmds.ls(selection=True,long=True) or []:
            source,uid=resolve(value)
            if uid in ids: raise ValueError('Duplicate source alias')
            ids.add(uid); sources.append(source)
        if not sources: raise ValueError('Select at least one transform')
        if p['include_hierarchy']:
            for root in list(sources):
                for value in cmds.listRelatives(root,allDescendents=True,fullPath=True,type='transform') or []:
                    source,uid=resolve(value)
                    if uid not in ids: ids.add(uid); sources.append(source)
        raw=[]
        for source in sources:
            target=auto_target(source,p)
            if target: raw.append({'source':source,'target':target})
            else: skipped.append({'source':source,'reason':'No side token'})
    seen=set()
    for row in raw:
        source,suid=resolve(row['source']); target,tuid=resolve(row['target'],True)
        if suid==tuid or tuid in seen: raise ValueError('Self mirror or duplicate target')
        seen.add(tuid)
        data=mirrored_values(cmds.xform(source,query=True,worldSpace=True,translation=True),cmds.xform(source,query=True,worldSpace=True,rotation=True),cmds.xform(source,query=True,worldSpace=True,scale=True),cmds.xform(source,query=True,objectSpace=True,rotation=True),p['plane'],p['mode'])
        if any(not math.isfinite(v) for key in ('translation','rotation','scale') for v in data[key]) or min(data['scale'])<=0: raise ValueError('Finite positive source world scale required')
        rows.append(dict(source=source,target=target,source_uuid=suid,target_uuid=tuid,values=data))
    if not rows: raise ValueError('No mirror pairs found')
    planned={row['target']:row['values'] for row in rows}
    for row in rows:
        parent=cmds.listRelatives(row['target'],parent=True,fullPath=True) or []
        while parent:
            if parent[0] in planned:
                scale=planned[parent[0]]['scale']
                if max(scale)-min(scale)>1e-10: raise ValueError('Planned ancestor scale would invalidate child world transforms')
            parent=cmds.listRelatives(parent[0],parent=True,fullPath=True) or []
    rows.sort(key=lambda row:row['target'].count('|'))
    return dict(parameters=p,rows=rows,skipped=skipped,source_values_sampled_before_writes=True)


class MirrorTransformTool(BaseMayaTool):
    tool_id='mirror_tool'; tool_name='变换镜像工具'; category='modeling_surfacing'; version='1.0-candidate.1'
    description='完整原三平面/控制普通复制三模式与层级UI；精确配对，全表预检及预采样，世界位置缩放和原Euler公式镜像，一次Undo。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        data=plan(normalize(kwargs)); auto=cmds.autoKeyframe(query=True,state=True)
        try:
            cmds.autoKeyframe(state=False)
            for row in data['rows']:
                n=row['target']; value=row['values']
                cmds.xform(n,worldSpace=True,translation=value['translation'])
                if value['rotation_space']=='object':
                    cmds.xform(n,worldSpace=True,scale=value['scale']); cmds.xform(n,objectSpace=True,rotation=value['rotation'])
                else:
                    cmds.xform(n,worldSpace=True,rotation=value['rotation']); cmds.xform(n,worldSpace=True,scale=value['scale'])
            return ToolResult.ok(data=data)
        finally: cmds.autoKeyframe(state=auto)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import MirrorCandidateUI
        return MirrorCandidateUI(self)
