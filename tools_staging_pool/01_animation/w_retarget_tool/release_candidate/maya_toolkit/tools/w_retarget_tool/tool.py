import os
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

CHANNELS = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']


def normalize(**kwargs):
    if set(kwargs) - {'action', 'pairs', 'start_frame', 'end_frame', 'exports', 'up_axis', 'ascii', 'fbx_version', 'bake'}:
        raise ValueError('Unknown arguments')
    p = dict(action='copy', start_frame=0, end_frame=20, up_axis='y', ascii=False, fbx_version='FBX202000', bake=True)
    p.update(kwargs)
    if p['action'] not in ('copy', 'export') or p['up_axis'] not in ('y', 'z') or p['fbx_version'] not in ('FBX202000', 'FBX201900', 'FBX201800') or any(type(p[k]) is not bool for k in ('ascii', 'bake')):
        raise ValueError('Invalid action/FBX options')
    if any(type(p[k]) is not int or abs(p[k]) > 1000000 for k in ('start_frame', 'end_frame')) or not 0 < p['end_frame'] - p['start_frame'] <= 10000:
        raise ValueError('Integer positive exclusive-end interval, at most 10000 frames required')
    if p['action'] == 'copy':
        if 'exports' in p or not isinstance(p.get('pairs'), list) or not 1 <= len(p['pairs']) <= 100 or any(not isinstance(x, dict) or set(x) != {'source', 'target'} or any(not isinstance(v, str) or not v for v in x.values()) for x in p['pairs']):
            raise ValueError('copy requires bounded source/target pairs only')
    elif 'pairs' in p or not isinstance(p.get('exports'), list) or not 1 <= len(p['exports']) <= 100:
        raise ValueError('export requires explicit nodes/path jobs only')
    return p


def resolve(value):
    from maya import cmds
    found = cmds.ls(value, long=True) or []
    if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('Unique whole transform required: ' + value)
    # The complete legacy matrices explicitly use instance[0].
    if len(cmds.ls(found[0], long=True, allPaths=True) or []) != 1:
        raise ValueError('Instanced transforms are unsupported by original matrix[0] algorithm')
    return found[0]


def output_path(value):
    if not isinstance(value, str) or any(c in value for c in ('\n', '\r', '"')):
        raise ValueError('Explicit FBX output path required')
    path = Path(value)
    if not path.is_absolute() or path.suffix.lower() != '.fbx' or any(p in ('.', '..') for p in value.replace('\\', '/').split('/')) or not path.parent.is_dir():
        raise ValueError('Absolute .fbx path with existing parent required')
    for node in [path] + list(path.parents):
        if (node.exists() or node.is_symlink()) and (node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0) & 0x400):
            raise ValueError('Symlink/junction output rejected')
    if path.exists():
        raise ValueError('FBX output already exists; never overwrite')
    return path.resolve()


def preflight(p):
    from maya import cmds
    plan = {'action': p['action'], 'start_frame': p['start_frame'], 'end_frame_exclusive': p['end_frame'], 'sample_count': p['end_frame'] - p['start_frame'], 'gui_acceptance': 'not_run'}
    if p['action'] == 'copy':
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('Enable Undo before retargeting')
        pairs = [{'source': resolve(x['source']), 'target': resolve(x['target'])} for x in p['pairs']]
        sources = {x['source'] for x in pairs}
        targets = [x['target'] for x in pairs]
        if len(set(targets)) != len(targets) or sources & set(targets) or any(s.startswith(t + '|') for s in sources for t in targets):
            raise ValueError('Distinct targets and independent sources required; no retarget dependency cycles')
        for target in targets:
            if cmds.referenceQuery(target, isNodeReferenced=True) or any(cmds.lockNode(target, query=True, lock=True)):
                raise ValueError('Target is locked/referenced')
            for attr in CHANNELS:
                plug = target + '.' + attr
                if cmds.getAttr(plug, lock=True) or not cmds.getAttr(plug, keyable=True):
                    raise ValueError('All nine original channels must be unlocked/keyable: ' + plug)
                incoming = cmds.listConnections(plug, source=True, destination=False) or []
                for curve in incoming:
                    if cmds.nodeType(curve) not in ('animCurveTA', 'animCurveTL', 'animCurveTU') or cmds.referenceQuery(curve, isNodeReferenced=True) or any(cmds.lockNode(curve, query=True, lock=True)):
                        raise ValueError('Unsupported target driver/layer/reference/lock')
                    outputs = cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
                    if len(outputs) != 1:
                        raise ValueError('Shared target animation curve')
        plan.update(pairs=pairs, channels=CHANNELS, scale_effect='Original parentConstraint proxy typically keys scale=1; does not retarget source scale', algorithm='full original pose-offset parentConstraint + multMatrix/decomposeMatrix sampling')
    else:
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            raise ValueError('Load the Maya FBX plugin explicitly before export; dry-run never loads it')
        jobs, seen = [], set()
        for item in p['exports']:
            if not isinstance(item, dict) or set(item) != {'nodes', 'path'} or not isinstance(item['nodes'], list) or not item['nodes']:
                raise ValueError('Each export requires explicit nodes and path')
            nodes = [resolve(n) for n in item['nodes']]
            if len(set(nodes)) != len(nodes):
                raise ValueError('Duplicate export node aliases')
            path = output_path(item['path'])
            if str(path).casefold() in seen:
                raise ValueError('Duplicate export output path')
            seen.add(str(path).casefold())
            jobs.append({'nodes': nodes, 'path': str(path)})
        plan.update(exports=jobs, file_effect='Creates new FBX files only; scene Undo cannot remove exports')
    return plan


class WRetargetTool(BaseMayaTool):
    tool_id = 'w_retarget_tool'
    tool_name = 'W Retarget Tool 1.0'
    category = 'animation'
    version = '1.0.0-candidate.1'
    description = 'Complete original pose-offset matrix retargeting for independent source/target pairs, four-row UI and explicit non-overwriting FBX export. Preserves original exclusive end and nine-channel/scale behavior; temporary helpers are owned and cleaned.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['copy', 'export'], 'default': 'copy'}, 'pairs': {'type': 'array', 'minItems': 1, 'maxItems': 100, 'items': {'type': 'object', 'properties': {'source': {'type': 'string'}, 'target': {'type': 'string'}}, 'required': ['source', 'target'], 'additionalProperties': False}}, 'start_frame': {'type': 'integer', 'default': 0}, 'end_frame': {'type': 'integer', 'description': 'Exclusive end, matching original range(start,end)', 'default': 20}, 'exports': {'type': 'array', 'minItems': 1, 'maxItems': 100, 'items': {'type': 'object', 'properties': {'nodes': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'uniqueItems': True}, 'path': {'type': 'string'}}, 'required': ['nodes', 'path'], 'additionalProperties': False}}, 'up_axis': {'type': 'string', 'enum': ['y', 'z'], 'default': 'y'}, 'ascii': {'type': 'boolean', 'default': False}, 'fbx_version': {'type': 'string', 'enum': ['FBX202000', 'FBX201900', 'FBX201800'], 'default': 'FBX202000'}, 'bake': {'type': 'boolean', 'default': True}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='Read-only full retarget/export preflight', data=preflight(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        p = normalize(**kwargs)
        plan = preflight(p)
        if p['action'] == 'copy':
            from .runtime import retarget
            data = retarget(plan)
        else:
            from .exporter import export
            data = export(plan, p)
        return ToolResult.ok(message='W Retarget operation complete', data=data, warnings=['Original exclusive end and scale=1 effect preserved', 'FBX files/settings and GUI state are separate from scene Undo', 'Production rigs and GUI acceptance still not_run'])

    def show_ui(self, parent=None):
        from maya import cmds
        if cmds.about(batch=True):
            raise RuntimeError('Interactive Maya required')
        from .ui import show_ui
        return show_ui(self)
