import hashlib
import json
import math
from pathlib import Path
from maya import cmds
from maya.api import OpenMaya as om

PKG = Path(__file__).resolve().parent


def supported(node):
    return cmds.nodeType(node)=='joint' or (cmds.nodeType(node)=='transform' and bool(cmds.listRelatives(node,shapes=True,type='locator',noIntermediate=True)))


def plan(p):
    c = json.loads((PKG/'catalog.json').read_text(encoding='utf8'))
    if hashlib.sha256((PKG/'vendor'/(c['source']+'.original')).read_bytes()).hexdigest()!=c['sha256']:
        raise ValueError('Original source missing/changed')
    if p['action']=='inspect':
        return {'catalog':c,'scene_write':False,'file_write':False,'gui_acceptance':'not_run'}
    if not cmds.undoInfo(query=True,state=True):
        raise ValueError('Enable Undo before skeleton creation')
    explicit = 'objects' in p
    values = p.get('objects',cmds.ls(selection=True,long=True) or [])
    objects = []
    for value in values:
        found = cmds.ls(value,long=True) or []
        if len(found)!=1 or '.' in value:
            raise ValueError('Unique whole input required: '+value)
        n = found[0]
        if not supported(n):
            if explicit:
                raise ValueError('Joint/locator transform required: '+value)
            continue
        sl = om.MSelectionList()
        sl.add(n)
        if len(om.MDagPath.getAllPathsTo(sl.getDependNode(0)))!=1:
            raise ValueError('True DAG instances unsupported for hierarchy mapping')
        if n in objects:
            raise ValueError('Duplicate object aliases')
        objects.append(n)
    if not objects or len(objects)>10000:
        raise ValueError('Select 1..10000 joints/locator transforms')
    # Preserve original joint-first/locator-second root order and immediate edges.
    objects = [n for n in objects if cmds.nodeType(n)=='joint']+[n for n in objects if cmds.nodeType(n)!='joint']
    parents = {n:(cmds.listRelatives(n,parent=True,fullPath=True) or [None])[0] for n in objects}
    roots = [n for n in objects if parents[n] not in objects]
    order = []
    pending = list(reversed(roots))
    while pending:
        node = pending.pop()
        order.append(node)
        children = [n for n in cmds.listRelatives(node,children=True,fullPath=True) or [] if n in parents]
        pending.extend(reversed(children))
    rows = []
    targets = set()
    for node in order:
        name = node.rsplit('|',1)[-1]+p['suffix']
        if name in targets or cmds.objExists(':'+name):
            raise ValueError('Result joint name collision: '+name)
        targets.add(name)
        translation = cmds.xform(node,query=True,worldSpace=True,translation=True)
        rotation = cmds.xform(node,query=True,worldSpace=True,rotation=True)
        if any(not math.isfinite(v) for v in translation+rotation):
            raise ValueError('Nonfinite input world pose')
        rows.append({'source':node,'source_uuid':cmds.ls(node,uuid=True)[0],'name':name,'parent_source':parents[node] if parents[node] in parents else None,'world_translation':translation,'world_rotation':rotation,'radius':cmds.getAttr(node+'.radius') if cmds.nodeType(node)=='joint' else None,'draw_style':cmds.getAttr(node+'.drawStyle') if cmds.nodeType(node)=='joint' else None})
    return {'objects':objects,'roots':roots,'rows':rows,'scene_write':True,'file_write':False,'scale_copied':False,'hierarchy_expanded':False,'gui_acceptance':'not_run'}


def execute(p):
    result = plan(p)
    if p['action']=='inspect':
        return result
    selected = [cmds.ls(n,uuid=True)[0] for n in cmds.ls(selection=True,long=True) or []]
    namespace = cmds.namespaceInfo(currentNamespace=True)
    autokey = cmds.autoKeyframe(query=True,state=True)
    mapping = {}
    complete = False
    try:
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        for row in result['rows']:
            parent = mapping.get(row['parent_source'])
            cmds.select(parent,replace=True) if parent else cmds.select(clear=True)
            joint = cmds.joint(name=':'+row['name'])
            mapping[row['source']] = cmds.ls(joint,long=True)[0]
        for row in result['rows']:
            joint = mapping[row['source']]
            cmds.matchTransform(joint,row['source'],position=True,rotation=True,scale=False)
            if row['radius'] is not None:
                cmds.setAttr(joint+'.radius',row['radius'])
                cmds.setAttr(joint+'.drawStyle',row['draw_style'])
        complete = True
        result['mapping'] = mapping
        result['created_uuids'] = [cmds.ls(n,uuid=True)[0] for n in mapping.values()]
        return result
    finally:
        cmds.namespace(setNamespace=namespace)
        cmds.autoKeyframe(state=autokey)
        if complete and p['select_result']:
            cmds.select(list(mapping.values()),replace=True)
        else:
            found = [cmds.ls(n,long=True)[0] for n in selected if cmds.ls(n,long=True)]
            cmds.select(found,replace=True) if found else cmds.select(clear=True)
