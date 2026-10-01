import hashlib
import json
from pathlib import Path
from maya import cmds
from maya.api import OpenMaya as om

PKG = Path(__file__).resolve().parent


def plan(p):
    catalog = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
    for row in catalog['files']:
        if hashlib.sha256((PKG / 'vendor' / row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Missing/changed original asset')
    if p['action'] == 'inspect':
        return {'catalog': catalog, 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before writes')
    values = p.get('objects', cmds.ls(selection=True, type='joint', long=True) or [])
    if not values:
        raise ValueError('Please select at least one joint.')
    objects = []
    changes = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or cmds.nodeType(found[0]) != 'joint':
            raise ValueError('Unique whole joint required: ' + value)
        node = found[0]
        if node in objects:
            raise ValueError('Duplicate object aliases')
        sl = om.MSelectionList()
        sl.add(node)
        if len(om.MDagPath.getAllPathsTo(sl.getDependNode(0))) != 1:
            raise ValueError('Instanced joint would affect other DAG paths')
        plug = node + '.segmentScaleCompensate'
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)) or cmds.getAttr(plug, lock=True) or cmds.listConnections(plug, source=True, destination=False):
            raise ValueError('Referenced/locked/driven compensation: ' + node)
        objects.append(node)
        if cmds.getAttr(plug):
            changes.append({'joint': node, 'uuid': cmds.ls(node, uuid=True)[0], 'before': True, 'after': False})
    return {'objects': objects, 'changes': changes, 'unchanged_count': len(objects) - len(changes), 'scene_write': bool(changes), 'file_write': False, 'hierarchy_expanded': False, 'gui_acceptance': 'not_run'}


def apply(p):
    for row in p['changes']:
        cmds.setAttr(row['joint'] + '.segmentScaleCompensate', False)
