"""Original Maya preference-aware reset without selection-dependent commands."""
import math


def preference(cmds,name):
    key='resetTransformations'+name
    if not cmds.optionVar(exists=key):
        return True
    value=cmds.optionVar(query=key)
    if type(value) not in (int,bool) or value not in (0,1):
        raise ValueError('Reset Transformations preference must be 0 or 1: '+key)
    return bool(value)


def preflight(p):
    from maya import cmds
    from maya.api import OpenMaya as om
    name=p['camera']
    if any(c in name for c in ('*','?',';','"','\n','\r','.')):
        raise ValueError('Expected a whole unique camera name')
    matches=cmds.ls(name,long=True) or []
    if len(matches)!=1:
        raise ValueError('Camera missing or ambiguous')
    camera=matches[0]
    if cmds.nodeType(camera)=='camera':
        camera=(cmds.listRelatives(camera,parent=True,fullPath=True) or [None])[0]
    if not camera or cmds.nodeType(camera)!='transform':
        raise ValueError('Expected a camera transform or shape')
    shapes=cmds.listRelatives(camera,shapes=True,noIntermediate=True,fullPath=True) or []
    if len(shapes)!=1 or cmds.nodeType(shapes[0])!='camera' or cmds.getAttr(shapes[0]+'.orthographic'):
        raise ValueError('Expected exactly one perspective camera shape')
    if cmds.listRelatives(camera,children=True,type='transform',fullPath=True):
        raise ValueError('Camera has a child transform rig; reset is unsupported')
    selection=om.MSelectionList()
    selection.add(camera)
    if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1:
        raise ValueError('Instanced camera transforms unsupported')
    rotate=p['reset_rotation'] if 'reset_rotation' in p else preference(cmds,'Rotate')
    scale=p['reset_scale'] if 'reset_scale' in p else preference(cmds,'Scale')
    translate=preference(cmds,'Translate')
    channels=['translate'+a for a in 'XYZ']+(['rotate'+a for a in 'XYZ'] if rotate else [])+(['scale'+a for a in 'XYZ'] if scale else [])
    if cmds.referenceQuery(camera,isNodeReferenced=True) or any(cmds.lockNode(camera,query=True,lock=True) or []):
        raise ValueError('Referenced/locked camera target')
    for attr in channels:
        plug=camera+'.'+attr
        if not cmds.getAttr(plug,settable=True) or cmds.listConnections(plug,source=True,destination=False,plugs=True):
            raise ValueError('Camera reset channel locked/keyed/driven: '+plug)
        if not math.isfinite(cmds.getAttr(plug)):
            raise ValueError('Nonfinite camera transform')
    return {'action':p['action'],'camera':camera,'shape':shapes[0],'reset_translation':translate,'reset_rotation':rotate,'reset_scale':scale,'translation_after':[1,1,1],'preserve_selection':p['preserve_selection'],'channels':channels,'before':{n:cmds.getAttr(camera+'.'+n)[0] for n in ('translate','rotate','scale')},'impacts':'Only camera local transform; original selects camera. No file/shape/viewport changes; one Undo.'}


def execute(p):
    from maya import cmds
    plan=preflight(p)
    if p['action']=='inspect':
        return plan
    before_selection=cmds.ls(selection=True,long=True) or []
    auto=cmds.autoKeyframe(query=True,state=True)
    try:
        cmds.autoKeyframe(state=False)
        cmds.makeIdentity(plan['camera'],apply=False,translate=plan['reset_translation'],rotate=plan['reset_rotation'],scale=plan['reset_scale'])
        cmds.setAttr(plan['camera']+'.translate',1,1,1,type='double3')
        cmds.select(before_selection if p['preserve_selection'] else [plan['camera']],replace=True)
    finally:
        cmds.autoKeyframe(state=auto)
    plan['after']={n:cmds.getAttr(plan['camera']+'.'+n)[0] for n in ('translate','rotate','scale')}
    return plan
