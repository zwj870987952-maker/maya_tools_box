"""Full original 1.1.0 stagger sampling with explicit curve scope."""
import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs)-{'objects','start','end','amount'}:
        raise ValueError('Unknown arguments')
    p=dict(kwargs)
    for name in ('start','end'):
        if type(p.get(name)) is not int:
            raise ValueError(name+' must be an integer')
    if p['end']-p['start']<3 or p['end']-p['start']>200000:
        raise ValueError('Range needs at least four inclusive frames and at most 200001')
    amount=p.setdefault('amount',3.1)
    if type(amount) not in (float,int) or not math.isfinite(amount) or not 2.2<=amount<=4:
        raise ValueError('Amount must be within original slider range 2.2..4')
    if 'objects' in p and (not isinstance(p['objects'],list) or not p['objects'] or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))):
        raise ValueError('Objects must be nonempty unique whole node names')
    return p


def preflight(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Undo before modifying animation')
    names=p.get('objects',cmds.ls(selection=True,long=True) or [])
    if not names:
        raise ValueError('Select animated transforms or supply objects/curves')
    objects=[]
    for name in names:
        matches=cmds.ls(name,long=True) or []
        if len(matches)!=1 or '.' in name:
            raise ValueError('Expected unambiguous whole node: '+name)
        objects.append(matches[0])
    if len(objects)!=len(set(objects)):
        raise ValueError('Duplicate aliases identify same node')
    allowed={cmds.ls(n,uuid=True)[0] for n in objects}
    curves=[]
    for node in objects:
        if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True)):
            raise ValueError('Referenced/locked input: '+node)
        if cmds.nodeType(node).startswith('animCurve'):
            candidates=[node]
        elif cmds.objectType(node,isAType='transform'):
            # keyframe -query -animation objects is rejected in Maya 2025.
            # Direct graph discovery also avoids global selected-key scope.
            incoming=cmds.listConnections(node,source=True,destination=False) or []
            if any(cmds.nodeType(n).startswith('animBlend') or cmds.nodeType(n) in ('pairBlend','unitConversion') for n in incoming):
                raise ValueError('Animation-layer/conversion/constraint graph requires separate acceptance')
            candidates=cmds.listConnections(node,source=True,destination=False,type='animCurve') or []
        else:
            raise ValueError('Expected transform/joint or time animation curve')
        for curve in candidates:
            if curve not in curves:
                curves.append(curve)
    if not curves:
        raise ValueError('No animation curves exist on supplied objects')
    results=[]
    for curve in curves:
        if cmds.nodeType(curve) not in ('animCurveTA','animCurveTL','animCurveTT','animCurveTU'):
            raise ValueError('Driven-key curve is not a time curve: '+curve)
        if cmds.referenceQuery(curve,isNodeReferenced=True) or any(cmds.lockNode(curve,query=True,lock=True)):
            raise ValueError('Curve is referenced/locked')
        inputs=cmds.listConnections(curve+'.input',source=True,destination=False,plugs=True) or []
        if len(inputs)>1 or (inputs and (cmds.nodeType(inputs[0].split('.')[0])!='time' or inputs[0].split('.')[-1] not in ('outTime','unwarpedTime'))):
            raise ValueError('Time-warped or unsupported curve input')
        destinations=cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True) or []
        for plug in destinations:
            target=plug.split('.')[0]
            if cmds.nodeType(target).startswith('animBlend') or cmds.nodeType(target) in ('pairBlend','unitConversion'):
                raise ValueError('Animation-layer/conversion/constraint graph requires separate acceptance')
            if cmds.ls(curve,uuid=True)[0] not in allowed and cmds.ls(target,uuid=True)[0] not in allowed:
                raise ValueError('Curve also drives an object outside requested scope')
            if cmds.referenceQuery(target,isNodeReferenced=True) or any(cmds.lockNode(target,query=True,lock=True)) or cmds.getAttr(plug,lock=True):
                raise ValueError('Locked/referenced curve destination')
        results.append({'curve':curve,'key_count':cmds.keyframe(curve,query=True,keyframeCount=True),'destinations':destinations})
    return {'objects':objects,'curves':results,'start':p['start'],'end':p['end'],'amount':p['amount'],'effect':'Boundary insertion and full original stagger sample writes; existing interior keys retained','gui_acceptance':'not_run'}


def stagger_curve(curve,start,end,amount):
    """Every sampling branch and boundary write from original stagger_it."""
    from maya import cmds
    cmds.setKeyframe(curve,time=start,insert=True)
    cmds.setKeyframe(curve,time=end,insert=True)
    values=cmds.keyframe(curve,query=True,time=(start,end),valueChange=True)
    first_value=cmds.keyframe(curve,query=True,valueChange=True)[0]
    key_values=[]
    if not all(item==first_value for item in values):
        for frame in range(start,end,2):
            if frame<end-3:
                key_values.append(cmds.keyframe(curve,query=True,eval=True,time=(frame+amount,frame+amount))[0])
                key_values.append(cmds.keyframe(curve,query=True,eval=True,time=(frame+2,frame+2))[0])
        if (end-start)&1==1:
            key_values.append(cmds.keyframe(curve,query=True,eval=True,time=(end-.5,end-.5))[0])
        cmds.setKeyframe(curve,time=end-1,insert=True)
        for frame,value in enumerate(key_values,start=1):
            cmds.setKeyframe(curve,time=start+frame,value=value)
    return {'curve':curve,'samples':key_values,'written_times':[start+i for i in range(1,len(key_values)+1)]}


class StaggerGuiTool(BaseMayaTool):
    tool_id='stagger_gui'
    tool_name='Stagger 1.1.0'
    category='animation'
    version='1.1.0-candidate.1'
    description='Original animation stagger resampling: boundary keys, alternating offset/normal samples, odd-range final sample and easing boundary. Existing interior keys retained.'
    parameters_schema={'type':'object','properties':{'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True,'minItems':1},'start':{'type':'integer'},'end':{'type':'integer'},'amount':{'type':'number','minimum':2.2,'maximum':4,'default':3.1}},'required':['start','end'],'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            return ToolResult.ok(message='Stagger read-only preflight',data=preflight(normalize(**kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        p=normalize(**kwargs)
        plan=preflight(p)
        changed=[]
        try:
            for row in plan['curves']:
                changed.append(stagger_curve(row['curve'],p['start'],p['end'],p['amount']))
        except Exception as exc:
            return ToolResult.fail(message='Stagger failed; Undo the whole operation: '+str(exc),errors=[str(exc)],data={'completed_curves':changed})
        return ToolResult.ok(message='Stagger animation written',data={'results':changed,'gui_acceptance':'not_run'})

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True):
            raise RuntimeError('Stagger GUI requires interactive Maya')
        from .ui import win
        return win()
