import hashlib
import json
import math
import os
from pathlib import Path
from maya import cmds
from . import engine

PKG = Path(__file__).resolve().parent
MARKS = {'mark', 'mark_foot', 'mark_animation'}
WRITES = {'one_step', 'more_step', 'align'}


def path_check(value, output=False):
    path = Path(value)
    if not path.is_absolute() or path.suffix.lower() != '.json' or not path.parent.is_dir():
        raise ValueError('Explicit absolute JSON path with existing parent required')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in [path] + list(path.parents)):
        raise ValueError('File links/junctions rejected')
    if output and os.path.lexists(path):
        raise ValueError('Existing export file protected')
    if not output and (not path.is_file() or path.stat().st_size > 5000000):
        raise ValueError('Existing bounded pose JSON required')
    return path


def pose_input(path):
    data = json.loads(path_check(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or set(data) != {'tool_id', 'poses'} or data['tool_id'] != 'relationship_tools_v19' or not isinstance(data['poses'], dict) or not 1 <= len(data['poses']) <= 1000:
        raise ValueError('Invalid pose cache document')
    for uuid, pose in data['poses'].items():
        found = cmds.ls(uuid, long=True) or []
        if len(found) != 1 or engine.identifier(found[0]) != uuid:
            raise ValueError('Pose UUID is not a unique current scene object')
        engine.nodes(found)
        if not isinstance(pose, dict) or set(pose) != {'pos', 'rot', 'short_name'} or not isinstance(pose['short_name'], str):
            raise ValueError('Invalid pose fields')
        for key in ('pos', 'rot'):
            if not isinstance(pose[key], list) or len(pose[key]) != 3 or any(type(n) not in (int, float) or not math.isfinite(n) or abs(n) > 1000000000 for n in pose[key]):
                raise ValueError('Three finite pose coordinates required')
    return data['poses']


def preflight(p):
    c = json.loads((PKG / 'catalog.json').read_text(encoding='utf-8'))
    if hashlib.sha256((PKG / 'vendor/Relationship Tools_v19.py.original').read_bytes()).hexdigest() != c['sha256']:
        raise ValueError('Original source fingerprint changed')
    action = p['action']
    if action == 'inspect':
        return {'source': c, 'owned_marks': engine.owned(), 'marked_objects': engine.mark_map(), 'copied_objects': engine.pose_cache(), 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    plan = dict(p)
    if action in ('more_step', 'mark_animation') and plan['frame_range'] is None:
        plan['frame_range'] = [int(cmds.playbackOptions(query=True, minTime=True)), int(cmds.playbackOptions(query=True, maxTime=True)) + 1]
        if not 0 < plan['frame_range'][1] - plan['frame_range'][0] <= 10000:
            raise ValueError('Playback range exceeds bounded work interval')
    selected = p.get('objects', cmds.ls(selection=True, long=True) or [])
    if action in ('delete_marks', 'export_pose', 'import_pose'):
        selected = []
    if action in ('one_step', 'more_step') and not selected:
        selected = list(engine.pose_cache() if p['world_coords'] else engine.mark_map())
    resolved = engine.nodes(selected)
    if action in MARKS | WRITES | {'copy_world'} and not resolved:
        raise ValueError('Nonempty object scope required')
    if action in ('mark', 'mark_animation', 'align') and len(resolved) < 2:
        raise ValueError('At least two ordered objects required; last is parent/target')
    if action in MARKS | {'delete_marks'}:
        removable = engine.cleanup_plan()
        plan['delete_owned_nodes'] = removable
    if action in MARKS:
        delete_ids = {engine.identifier(n) for n in plan['delete_owned_nodes']}
        names = [n.rsplit('|', 1)[-1] + '_locatorTag' for n in (resolved if action == 'mark_foot' else resolved[:-1])]
        names.append('foot_locatorPar' if action == 'mark_foot' else resolved[-1].rsplit('|', 1)[-1] + '_locatorPar')
        if len(names) != len(set(names)):
            raise ValueError('Original-style mark names collide')
        for name in names:
            existing = cmds.ls(name, long=True) or []
            if any(engine.identifier(n) not in delete_ids for n in existing):
                raise ValueError('Foreign mark-like name protected: ' + name)
        if any(engine.identifier(n) in delete_ids for n in resolved):
            raise ValueError('Owned locator cannot be source of replacement mark')
    targets = resolved[:-1] if action == 'align' else resolved
    if action in WRITES:
        engine.nodes(targets, writable=True, channels=engine.channels(p))
        if action == 'align' and any(resolved[-1].startswith(n + '|') for n in targets):
            raise ValueError('Align target below written ancestor would move during alignment')
        if action in ('one_step', 'more_step'):
            mapping = engine.pose_cache() if p['world_coords'] else engine.mark_map()
            if any(n not in mapping for n in resolved):
                raise ValueError('Every target must have an owned tag or copied UUID pose')
            if not p['world_coords']:
                for target in resolved:
                    parents = cmds.listRelatives(mapping[target], parent=True, fullPath=True) or []
                    for parent in parents:
                        driving = cmds.listConnections(parent + '.' + engine.SOURCE, source=True, destination=False) or [] if cmds.objExists(parent + '.' + engine.SOURCE) else []
                        if driving:
                            source = engine.nodes(driving)[0]
                            if source == target or source.startswith(target + '|'):
                                raise ValueError('Written target would move its own mark driving parent')
    chosen = engine.frames(plan, resolved) if action in WRITES | {'mark_animation'} else []
    if len(chosen) * max(1, len(targets)) > 200000:
        raise ValueError('Frame/object work budget exceeded')
    if action == 'export_pose':
        if not engine.CACHE:
            raise ValueError('Copy a pose before export')
        path_check(p['file_path'], output=True)
    if action == 'import_pose':
        plan['imported_poses'] = pose_input(p['file_path'])
    plan.update({'objects': resolved, 'targets': targets, 'frames': chosen, 'scene_write': action in MARKS | WRITES | {'delete_marks'}, 'file_write': action == 'export_pose', 'gui_acceptance': 'not_run'})
    if plan['scene_write'] and not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before scene mutations')
    return plan


def uuids():
    return {engine.identifier(n) for n in cmds.ls(long=True) or []}


def snapshot():
    return {'time': cmds.currentTime(query=True), 'selection': [engine.identifier(n) for n in cmds.ls(selection=True, long=True) or []], 'namespace': cmds.namespaceInfo(currentNamespace=True), 'autokey': cmds.autoKeyframe(query=True, state=True), 'track': cmds.selectPref(query=True, trackSelectionOrder=True), 'evaluation': cmds.evaluationManager(query=True, mode=True)[0], 'refresh': cmds.refresh(query=True, suspend=True)}


def restore(state, advance=False):
    cmds.namespace(setNamespace=state['namespace'])
    cmds.autoKeyframe(state=state['autokey'])
    cmds.currentTime(state['time'] + (1 if advance else 0))
    selected = [found[0] for uuid in state['selection'] for found in [cmds.ls(uuid, long=True) or []] if len(found) == 1]
    cmds.select(selected, replace=True) if selected else cmds.select(clear=True)
    cmds.selectPref(trackSelectionOrder=state['track'])
    cmds.refresh(suspend=state['refresh'])
    cmds.evaluationManager(mode=state['evaluation'])


def execute(p):
    plan = preflight(p)
    action = p['action']
    if action == 'inspect':
        return plan
    if action == 'export_pose':
        path = path_check(p['file_path'], output=True)
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            json.dump({'tool_id': 'relationship_tools_v19', 'poses': engine.CACHE}, stream, ensure_ascii=False, indent=2)
        return plan
    if action == 'import_pose':
        engine.CACHE.clear()
        engine.CACHE.update(plan['imported_poses'])
        return plan
    state = snapshot()
    before = uuids()
    plan['_original_time'] = state['time']
    worker = engine.SafeRelationship(plan)
    succeeded = False
    try:
        cmds.namespace(setNamespace=':')
        cmds.autoKeyframe(state=False)
        cmds.selectPref(trackSelectionOrder=True)
        cmds.select(plan['objects'], replace=True) if plan['objects'] else cmds.select(clear=True)
        method = {'mark': 'mark_action', 'mark_foot': 'mark_foot_action', 'mark_animation': 'mark_ani_action', 'copy_world': 'copy_world_transform', 'one_step': 'one_step_action', 'more_step': 'more_step_action', 'align': 'align_objects_action', 'delete_marks': 'delete_marks_action'}[action]
        getattr(worker, method)()
        created = sorted(uuids() - before)
        if action in MARKS:
            for uuid in created:
                node = cmds.ls(uuid, long=True)[0]
                if not cmds.objExists(node + '.' + engine.OWNER):
                    engine.mark_metadata(node)
        succeeded = True
        return dict(plan, created_node_uuids=created, created_layer=worker.created_layer, copied_objects=engine.pose_cache(), owned_marks=engine.owned(), native_result_selection=cmds.ls(selection=True, long=True) or [])
    finally:
        restore(state, succeeded and p['advance'] and action in ('one_step', 'more_step'))
