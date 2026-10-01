from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ATTRS=['translate','rotate','scale']+[kind+axis for kind in ('translate','rotate','scale') for axis in 'XYZ']
PROPS={'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'restore_locks':{'type':'boolean','default':False}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(restore_locks=False); p.update(kwargs)
    if type(p['restore_locks']) is not bool: raise ValueError('Boolean lock restoration required')
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))): raise ValueError('Nonempty unique objects required')
    return p


def node(value):
    from maya import cmds
    from maya.api import OpenMaya as om
    if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Explicit whole DAG node required')
    matches=cmds.ls(value,long=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous node')
    n=matches[0]; selection=om.MSelectionList(); selection.add(n); obj=selection.getDependNode(0)
    if not obj.hasFn(om.MFn.kDagNode) or len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('Non-instanced DAG required')
    if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Referenced/locked affected node')
    return n,cmds.ls(n,uuid=True)[0]


def plan(p):
    from maya import cmds
    from maya.api import OpenMaya as om
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    values=p.get('objects') or cmds.ls(selection=True,long=True) or []
    if not values: raise ValueError('Select at least one transform/joint')
    roots=[]; ids=set(); affected=set()
    for value in values:
        n,uid=node(value)
        if cmds.nodeType(n) not in ('transform','joint'): raise ValueError('Transform/joint roots required')
        if uid in ids: raise ValueError('Duplicate root alias')
        ids.add(uid); roots.append(n); affected.add(n); affected.update(cmds.listRelatives(n,allDescendents=True,fullPath=True) or [])
    if any(a!=b and b.startswith(a+'|') for a in roots for b in roots): raise ValueError('Overlapping root hierarchy unsupported')
    geometries=[]; history=set()
    for value in sorted(affected):
        n,uid=node(value); kind=cmds.nodeType(n)
        if kind in ('transform','joint'):
            matrix=cmds.xform(n,query=True,worldSpace=True,matrix=True)
            if abs(om.MMatrix(matrix).det3x3())<1e-12: raise ValueError('Degenerate affected transform')
            for attr in ATTRS:
                if cmds.listConnections(n+'.'+attr,source=True,destination=False): raise ValueError('Affected transform channel driven/animated: '+n+'.'+attr)
                if n not in roots and cmds.getAttr(n+'.'+attr,lock=True): raise ValueError('Locked descendant transform channel')
            if kind=='joint' and (cmds.getAttr(n+'.jointOrient',lock=True) or cmds.listConnections(n+'.jointOrient',source=True,destination=False)): raise ValueError('Affected jointOrient locked/driven')
            if cmds.objExists(n+'.offsetParentMatrix'):
                m=cmds.getAttr(n+'.offsetParentMatrix')
                if any(abs(v-(1.0 if i in (0,5,10,15) else 0.0))>1e-10 for i,v in enumerate(m)): raise ValueError('Nonidentity affected offsetParentMatrix')
        elif kind in ('mesh','nurbsCurve','nurbsSurface'):
            if cmds.getAttr(n+'.intermediateObject'): raise ValueError('Intermediate/deformed geometry unsupported')
            input_attr='inMesh' if kind=='mesh' else 'create'
            if cmds.getAttr(n+'.'+input_attr,lock=True): raise ValueError('Locked geometry input')
            upstream=cmds.listConnections(n+'.'+input_attr,source=True,destination=False) or []
            graph=set(upstream)
            for start in upstream: graph.update(cmds.listHistory(start,pruneDagObjects=True) or [])
            for h in graph:
                if cmds.nodeType(h) not in ('makeNurbCircle','makeNurbSphere','transformGeometry','rebuildCurve','reverseCurve','rebuildSurface','reverseSurface') and not cmds.nodeType(h).startswith('poly'): raise ValueError('Only static exclusive construction geometry supported')
                if cmds.referenceQuery(h,isNodeReferenced=True) or any(cmds.lockNode(h,query=True,lock=True) or []): raise ValueError('Construction node referenced/locked')
                history.add(h)
            for attr in (('outMesh','worldMesh') if kind=='mesh' else ('local','worldSpace')):
                if cmds.listConnections(n+'.'+attr,source=False,destination=True): raise ValueError('Affected geometry has external consumer')
            geometries.append({'node':n,'uuid':uid,'type':kind})
        else: raise ValueError('Affected camera/light/other node unsupported: '+kind)
    owned=affected|history
    for h in history:
        for consumer in cmds.listConnections(h,source=False,destination=True) or []:
            n=(cmds.ls(consumer,long=True) or [consumer])[0]
            if n not in owned: raise ValueError('Shared construction node affects outside hierarchy')
    return {'roots':[{'node':n,'uuid':cmds.ls(n,uuid=True)[0],'locks':{a:bool(cmds.getAttr(n+'.'+a,lock=True)) for a in ATTRS}} for n in roots],'geometries':geometries,'affected_nodes':sorted(affected),'construction_nodes':sorted(history),'restore_locks':p['restore_locks']}


class UnlockFreezeTool(BaseMayaTool):
    tool_id='unlock_freeze'; tool_name='解锁并冻结变换'; category='modeling_surfacing'; version='1.0-candidate.1'
    description='完整原九TRS属性解锁与makeIdentity apply全TRS冻结；精确根/全部受影响后代/独占静态geometry预检，单Undo/选择恢复，可选恢复原锁。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        data=plan(normalize(kwargs)); selection=cmds.ls(selection=True,long=True) or []; auto=cmds.autoKeyframe(query=True,state=True)
        try:
            cmds.autoKeyframe(state=False)
            for row in data['roots']:
                n=row['node']
                for attr in ATTRS: cmds.setAttr(n+'.'+attr,lock=False)
                cmds.makeIdentity(n,apply=True,translate=True,rotate=True,scale=True)
                if data['restore_locks']:
                    for attr in ATTRS[3:]: cmds.setAttr(n+'.'+attr,lock=row['locks'][attr])
                    for attr in ATTRS[:3]: cmds.setAttr(n+'.'+attr,lock=row['locks'][attr])
            return ToolResult.ok(data=data)
        finally:
            cmds.autoKeyframe(state=auto)
            valid=[n for n in selection if cmds.objExists(n)]; cmds.select(valid,replace=True) if valid else cmds.select(clear=True)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        win='mtbUnlockFreezeWindow'
        if cmds.window(win,exists=True): cmds.deleteUI(win)
        cmds.window(win,title=self.tool_name); cmds.columnLayout(adjustableColumn=True)
        choice=cmds.checkBox(label='冻结后恢复原属性锁（默认保持解锁）',value=False)
        def call(dry):
            r=self.run(dry_run=dry,restore_locks=cmds.checkBox(choice,query=True,value=True)); print(r.to_dict())
            if not r.success: cmds.warning(r.message)
        cmds.button(label='预检选择及全部受影响后代',command=lambda *_:call(True)); cmds.button(label='解锁并冻结TRS',command=lambda *_:call(False))
        cmds.showWindow(win); return win


def unlock_and_freeze_transforms(**kwargs): return UnlockFreezeTool().run(**kwargs)
