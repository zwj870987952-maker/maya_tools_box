import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs)-{'objects','offset','mode','update_selection'}:
        raise ValueError('Unknown arguments')
    p={'offset':5.0,'mode':'batch','update_selection':False}
    p.update(kwargs)
    if type(p['offset']) not in (int,float) or not math.isfinite(p['offset']) or not -1000<=p['offset']<=1000:
        raise ValueError('Offset must be finite within -1000..1000')
    if p['mode'] not in ('once','batch') or type(p['update_selection']) is not bool:
        raise ValueError('Mode must be once/batch, update_selection must be boolean')
    if 'objects' in p and (not isinstance(p['objects'],list) or len(p['objects'])<2 or any(not isinstance(n,str) or not n for n in p['objects']) or len(p['objects'])!=len(set(p['objects']))):
        raise ValueError('Supply at least two unique ordered whole transforms')
    return p


def offsets(count,offset,mode):
    return [0]+[offset*(i if mode=='batch' else 1) for i in range(1,count)]


def preflight(p):
    from maya import cmds
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Undo before moving animation')
    names=p.get('objects',cmds.ls(selection=True,long=True) or [])
    if len(names)<2:
        raise ValueError('Select at least two ordered transforms')
    objects=[]
    for name in names:
        found=cmds.ls(name,long=True) or []
        if len(found)!=1 or '.' in name or not cmds.objectType(found[0],isAType='transform'):
            raise ValueError('Expected unique whole transform: '+name)
        if found[0] in objects:
            raise ValueError('Duplicate aliases identify one node')
        objects.append(found[0])
    shifts=offsets(len(objects),p['offset'],p['mode'])
    allowed={cmds.ls(n,uuid=True)[0]:shift for n,shift in zip(objects,shifts)}
    curve_shifts={}
    owners={}
    for node,shift in zip(objects,shifts):
        if not shift:
            continue
        if cmds.referenceQuery(node,isNodeReferenced=True) or any(cmds.lockNode(node,query=True,lock=True)):
            raise ValueError('Referenced/locked transform: '+node)
        incoming=cmds.listConnections(node,source=True,destination=False) or []
        if any(cmds.nodeType(x).startswith('animBlend') or cmds.nodeType(x) in ('pairBlend','unitConversion') for x in incoming):
            raise ValueError('Animation-layer/conversion graph is unsupported')
        for curve in cmds.listConnections(node,source=True,destination=False,type='animCurve') or []:
            if cmds.nodeType(curve) not in ('animCurveTA','animCurveTL','animCurveTT','animCurveTU'):
                raise ValueError('Driven-key input is not frame animation')
            if curve in curve_shifts and curve_shifts[curve]!=shift:
                raise ValueError('Shared curve has conflicting per-object offsets')
            if cmds.referenceQuery(curve,isNodeReferenced=True) or any(cmds.lockNode(curve,query=True,lock=True)):
                raise ValueError('Referenced/locked curve')
            inputs=cmds.listConnections(curve+'.input',source=True,destination=False,plugs=True) or []
            if len(inputs)>1 or (inputs and (cmds.nodeType(inputs[0].split('.')[0])!='time' or inputs[0].split('.')[-1] not in ('outTime','unwarpedTime'))):
                raise ValueError('Unsupported time warp')
            for plug in cmds.listConnections(curve+'.output',source=False,destination=True,plugs=True) or []:
                target=plug.split('.')[0]
                uid=cmds.ls(target,uuid=True)[0]
                if uid not in allowed or allowed[uid]!=shift:
                    raise ValueError('Shared curve would move a stationary/out-of-scope/differently shifted target')
                if cmds.referenceQuery(target,isNodeReferenced=True) or any(cmds.lockNode(target,query=True,lock=True)) or cmds.getAttr(plug,lock=True):
                    raise ValueError('Locked/referenced output')
            curve_shifts[curve]=shift
            owners.setdefault(curve,[]).append(node)
    return {'objects':objects,'offsets':shifts,'curves':[{'curve':c,'offset':v,'owners':owners[c],'key_count':cmds.keyframe(c,query=True,keyframeCount=True)} for c,v in curve_shifts.items()],'mode':p['mode'],'selection_after':objects[1:] if p['mode']=='once' else objects[-1:],'gui_acceptance':'not_run'}


class StaggerOffsetTool(BaseMayaTool):
    tool_id='stagger_offset'
    tool_name='减选关键帧偏移'
    category='animation'
    version='1.0.0-candidate.1'
    description='Ordered selection offset: once moves all except first by offset; batch gives offsets 0,offset,2*offset,... . Moves every existing key with dense-key collision protection.'
    parameters_schema={'type':'object','properties':{'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True,'minItems':2},'offset':{'type':'number','minimum':-1000,'maximum':1000,'default':5},'mode':{'type':'string','enum':['once','batch'],'default':'batch'},'update_selection':{'type':'boolean','default':False}},'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            return ToolResult.ok(message='Read-only ordered offset preflight',data=preflight(normalize(**kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from maya import cmds
        p=normalize(**kwargs)
        plan=preflight(p)
        changed=[]
        try:
            for row in plan['curves']:
                # Translate the entire curve simultaneously; per-time writes
                # collide with neighboring dense keys and may shift twice.
                cmds.keyframe(row['curve'],edit=True,time=(':',),relative=True,timeChange=row['offset'],option='over')
                changed.append(row)
            if p['update_selection']:
                cmds.select(plan['selection_after'],replace=True)
                cmds.selectKey(plan['selection_after'],replace=True)
        except Exception as exc:
            return ToolResult.fail(message='Offset failed; Undo the operation: '+str(exc),errors=[str(exc)],data={'completed_curves':changed})
        return ToolResult.ok(message='Ordered animation offset complete',data={'objects':plan['objects'],'offsets':plan['offsets'],'curves':changed,'selection_changed':p['update_selection'],'gui_acceptance':'not_run'})

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()
