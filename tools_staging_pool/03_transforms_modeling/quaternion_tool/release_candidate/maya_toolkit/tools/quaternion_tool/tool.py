import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS={'from_euler':{'euler'},'from_axis_angle':{'axis','angle'},'from_components':{'quaternion'},'from_to':{'from_direction','to_direction'},'rotate_vector':{'quaternion','vector'},'to_euler':{'quaternion'},'slerp':{'quaternion','second','t'},'multiply':{'quaternion','second'},'inverse':{'quaternion'},'normalize':{'quaternion'},'apply':{'quaternion','objects'}}
DEFAULTS={'euler':[0,0,0],'axis':[0,1,0],'angle':0,'quaternion':[0,0,0,1],'from_direction':[1,0,0],'to_direction':[0,1,0],'vector':[1,0,0],'second':[0,0,0,1],'t':.5}
PROPS={'action':{'type':'string','enum':list(ACTIONS),'default':'from_euler'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True}}
for key,value in DEFAULTS.items():
    PROPS[key]={'type':'array','items':{'type':'number'},'minItems':len(value),'maxItems':len(value),'default':value} if isinstance(value,list) else {'type':'number','default':value}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(action='from_euler'); p.update(kwargs)
    if not isinstance(p['action'],str) or p['action'] not in ACTIONS: raise ValueError('Unknown action')
    if set(p)-{'action'}-ACTIONS[p['action']]: raise ValueError('Argument does not apply to action')
    for key in ACTIONS[p['action']]-{'objects'}:
        p.setdefault(key,DEFAULTS[key]); value=p[key]
        if isinstance(DEFAULTS[key],list):
            if not isinstance(value,list) or len(value)!=len(DEFAULTS[key]): raise ValueError('Exact numeric vector length required: '+key)
            numbers=value
        else: numbers=[value]
        if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e12 for v in numbers): raise ValueError('Finite numeric values within 1e12 required: '+key)
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))): raise ValueError('Unique explicit objects required')
    return p


def calculate(p):
    from .native import Quaternion
    action=p['action']; q=Quaternion(p.get('quaternion',[0,0,0,1]))
    if action=='from_euler': q=Quaternion.FromEuler(p['euler'])
    elif action=='from_axis_angle': q=Quaternion.FromAxisAngle(p['axis'],p['angle'])
    elif action=='from_to': q=Quaternion.FromToRotation(p['from_direction'],p['to_direction'])
    elif action=='multiply': q=q*Quaternion(p['second'])
    elif action=='inverse': q=q.Inversed()
    elif action=='normalize': q=q.Normalized()
    elif action=='slerp': q=Quaternion.Slerp(q,Quaternion(p['second']),p['t'])
    data={'quaternion':q.xyzw(),'euler_degrees':q.Euler(),'convention':'supplied XYZ quaternion multiplication and RotateDirection convention'}
    if action=='rotate_vector':
        vector=q.RotateDirection(p['vector']); data['rotated_vector']=[vector.x,vector.y,vector.z]
    if any(not math.isfinite(v) for values in (data['quaternion'],data['euler_degrees'],data.get('rotated_vector',[])) for v in values): raise ValueError('Calculated nonfinite rotation')
    return data


def targets(values):
    from maya import cmds
    from maya.api import OpenMaya as om
    rows=[]; ids=set()
    for value in values:
        if any(c in value for c in ('*','?','.',';','"','\n','\r','\\')): raise ValueError('Explicit whole transform required')
        matches=cmds.ls(value,long=True) or []
        if len(matches)!=1: raise ValueError('Missing/ambiguous target')
        n=matches[0]; uid=cmds.ls(n,uuid=True)[0]
        if uid in ids: raise ValueError('Duplicate target alias')
        ids.add(uid)
        if cmds.nodeType(n)!='transform' or cmds.getAttr(n+'.rotateOrder')!=0: raise ValueError('Plain XYZ transform required; joints/other rotate orders unsupported')
        selection=om.MSelectionList(); selection.add(n)
        if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1: raise ValueError('Instanced target unsupported')
        if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Referenced/locked target')
        if any(abs(v)>1e-10 for v in cmds.getAttr(n+'.rotateAxis')[0]): raise ValueError('Nonzero rotateAxis unsupported')
        for axis in 'XYZ':
            plug=n+'.rotate'+axis
            if cmds.getAttr(plug,lock=True) or cmds.listConnections(plug,source=True,destination=False): raise ValueError('Locked/driven rotation')
        if cmds.objExists(n+'.offsetParentMatrix'):
            matrix=cmds.getAttr(n+'.offsetParentMatrix')
            if any(abs(v-(1.0 if i in (0,5,10,15) else 0.0))>1e-10 for i,v in enumerate(matrix)): raise ValueError('Nonidentity offsetParentMatrix unsupported')
        rows.append({'node':n,'uuid':uid})
    if not rows: raise ValueError('Select transforms to apply quaternion')
    return rows


def plan(p):
    data=calculate(p)
    if p['action']=='apply':
        from maya import cmds
        if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
        data['targets']=targets(p.get('objects') or cmds.ls(selection=True,long=True) or [])
    return data


class QuaternionMathTool(BaseMayaTool):
    tool_id='quaternion_tool'; tool_name='Maya四元数工具'; category='modeling_surfacing'; version='1.0-candidate.1'
    description='完整原四元数数学类和创建/向量旋转/欧拉/应用UI；十一计算与XYZ变换应用API，严格角度制和只读预检，场景应用一次Undo。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from maya import cmds
        p=normalize(kwargs); data=plan(p)
        if p['action']=='apply':
            auto=cmds.autoKeyframe(query=True,state=True)
            try:
                cmds.autoKeyframe(state=False)
                for row in data['targets']: cmds.rotate(*[str(v)+'deg' for v in data['euler_degrees']],row['node'],absolute=True)
            finally: cmds.autoKeyframe(state=auto)
        return ToolResult.ok(data=data)

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import QuaternionCandidateUI
        return QuaternionCandidateUI(self)
