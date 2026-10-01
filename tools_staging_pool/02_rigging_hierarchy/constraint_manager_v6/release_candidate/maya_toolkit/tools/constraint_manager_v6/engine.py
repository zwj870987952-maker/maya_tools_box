"""Operate on actual target aliases and UUID connection endpoints, never guessed names."""
import hashlib
import json
from pathlib import Path
import re
from maya import cmds, mel

PKG = Path(__file__).resolve().parent
TYPES = ('parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint', 'aimConstraint', 'geometryConstraint', 'normalConstraint', 'tangentConstraint', 'poleVectorConstraint', 'pointOnPolyConstraint')
REVERSE_TYPES = TYPES[:5]
_snapshots = {}


def resources():
    c = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
    for row in c['files']:
        p = PKG/row['archive']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Missing/changed original source '+row['path'])


def node(value, editable=False):
    if not isinstance(value, str) or not value or any(x in value for x in ('*', '?', '[', ']', ';', '`', '"', '\n', '\r')) or '.' in value:
        raise ValueError('Literal whole node or UUID required')
    found = cmds.ls(value, long=True) or []
    if len(found) != 1:
        raise ValueError('Unique existing node required '+value)
    out = found[0]
    if len(cmds.ls(out, allPaths=True, long=True) or []) != 1:
        raise ValueError('Instanced nodes rejected')
    if editable and (cmds.referenceQuery(out, isNodeReferenced=True) or any(cmds.lockNode(out, query=True, lock=True))):
        raise ValueError('Referenced/locked node '+out)
    return out


def identity(value):
    return cmds.ls(value, uuid=True)[0]


def endpoint(plug):
    n, attr = plug.split('.', 1)
    n = node(n)
    return {'uuid': identity(n), 'attribute': attr}


def plug(data):
    if not isinstance(data, dict) or set(data) != {'uuid', 'attribute'} or not isinstance(data['attribute'], str) or not re.fullmatch(r'[A-Za-z_]\w*(?:\[\d+\])?(?:\.[A-Za-z_]\w*(?:\[\d+\])?)*', data['attribute'], re.ASCII):
        raise ValueError('Plain UUID/attribute endpoint required')
    value = node(data['uuid'])+'.'+data['attribute']
    if not cmds.objExists(value):
        raise ValueError('Snapshot plug missing '+value)
    return value


def writable(value, allow_curve=False):
    n = value.split('.', 1)[0]
    node(n, editable=True)
    if cmds.getAttr(value, lock=True):
        raise ValueError('Locked channel '+value)
    sources = cmds.listConnections(value, source=True, destination=False, plugs=True) or []
    if sources:
        if not allow_curve or len(sources) != 1:
            raise ValueError('Driven channel protected '+value)
        curve = sources[0].split('.', 1)[0]
        if not cmds.nodeType(curve).startswith('animCurveT'):
            raise ValueError('Only ordinary time animation can receive explicit keys')
        node(curve, editable=True)
        destinations = cmds.listConnections(curve+'.output', source=False, destination=True, plugs=True) or []
        if len(destinations) != 1:
            raise ValueError('Shared animation curve protected')
        input_nodes = cmds.listConnections(curve+'.input', source=True, destination=False) or []
        if input_nodes and any(cmds.nodeType(x) != 'time' for x in input_nodes):
            raise ValueError('Time-warped weight curve protected')
        for attribute in ('input', 'output'):
            if cmds.getAttr(curve+'.'+attribute, lock=True):
                raise ValueError('Locked animation curve channel')


def edges(n, all_outputs=False):
    pairs = cmds.listConnections(n, source=False, destination=True, connections=True, plugs=True, skipConversionNodes=False) or []
    result = []
    for a, b in zip(pairs[::2], pairs[1::2]):
        if all_outputs or a.split('.', 1)[1].startswith(('constraintTranslate', 'constraintRotate', 'constraintScale', 'constraintVector')):
            result.append({'source': endpoint(a), 'destination': endpoint(b)})
    return result


def info(value):
    n = node(value)
    kind = cmds.nodeType(n)
    if kind not in TYPES:
        raise ValueError('Supported native constraint required '+n)
    fn = getattr(cmds, kind)
    targets = fn(n, query=True, targetList=True) or []
    aliases = fn(n, query=True, weightAliasList=True) or []
    indices = cmds.getAttr(n+'.target', multiIndices=True) or []
    if len(targets) != len(aliases) or len(targets) != len(indices):
        raise ValueError('Unresolved native target/alias/index mapping')
    resolved = []
    for target, alias, index in zip(targets, aliases, indices):
        matrix = n+'.target['+str(index)+'].targetParentMatrix'
        connected = cmds.listConnections(matrix, source=True, destination=False) or [] if cmds.objExists(matrix) else []
        actual = node(connected[0] if len(connected) == 1 else target)
        resolved.append({'node': actual, 'uuid': identity(actual), 'alias': alias, 'index': index, 'weight_plug': n+'.'+alias, 'weight': cmds.getAttr(n+'.'+alias)})
    parent = cmds.listRelatives(n, parent=True, fullPath=True) or []
    if len(parent) != 1:
        raise ValueError('Constraint must have one actual constrained DAG parent')
    constrained = node(parent[0])
    return {'node': n, 'uuid': identity(n), 'type': kind, 'constrained': constrained, 'constrained_uuid': identity(constrained), 'targets': resolved, 'outputs': edges(n), 'all_outputs': edges(n, True)}


def discover(values):
    found = []
    for value in values:
        n = node(value)
        candidates = [n] if cmds.nodeType(n) in TYPES else (cmds.listConnections(n, source=True, destination=True, type='constraint') or [])
        for candidate in candidates:
            candidate = node(candidate)
            if candidate not in found and cmds.nodeType(candidate) in TYPES:
                found.append(candidate)
    return found


def weight(value):
    if not isinstance(value, str) or '.' not in value:
        raise ValueError('Actual constraint weight plug required')
    n, attribute = value.split('.', 1)
    data = info(n)
    for target in data['targets']:
        physical = 'target['+str(target['index'])+'].targetWeight'
        if attribute in (target['alias'], physical):
            return target['weight_plug'], data, target
    raise ValueError('Attribute is not a real target weight alias')


def snapshot(data):
    return {'constraint_uuid': data['uuid'], 'node': data['node'], 'type': data['type'], 'constrained_uuid': data['constrained_uuid'], 'target_uuids': [t['uuid'] for t in data['targets']], 'outputs': data['outputs'], 'reverse_uuids': []}


def snapshot_check(record):
    if not isinstance(record, dict) or set(record) != {'constraint_uuid', 'node', 'type', 'constrained_uuid', 'target_uuids', 'outputs', 'reverse_uuids'} or record['type'] not in TYPES or not isinstance(record['outputs'], list) or not 1 <= len(record['outputs']) <= 1000 or not isinstance(record['reverse_uuids'], list) or len(record['reverse_uuids']) > 1000:
        raise ValueError('Unsupported snapshot record')
    n = node(record['constraint_uuid'], editable=True)
    if cmds.nodeType(n) != record['type'] or identity(node(record['constrained_uuid'])) != info(n)['constrained_uuid']:
        raise ValueError('Snapshot belongs to different current scene nodes')
    actual_targets = [x['uuid'] for x in info(n)['targets']]
    if actual_targets != record['target_uuids']:
        raise ValueError('Snapshot target mapping changed')
    for edge in record['outputs']:
        if set(edge) != {'source', 'destination'} or edge['source']['uuid'] != record['constraint_uuid'] or not edge['source']['attribute'].startswith(('constraintTranslate', 'constraintRotate', 'constraintScale', 'constraintVector')):
            raise ValueError('Snapshot source must be a constraint output')
        src, dst = plug(edge['source']), plug(edge['destination'])
        destination_node, destination_attr = dst.split('.', 1)
        child = node(record['constrained_uuid'])
        expected_attr = edge['source']['attribute'][len('constraint'):]
        expected_attr = expected_attr[0].lower()+expected_attr[1:]
        if record['type'] == 'poleVectorConstraint':
            expected_attr = expected_attr.replace('vector', 'poleVector')
        if identity(destination_node) == record['constrained_uuid']:
            if cmds.attributeQuery(destination_attr, node=destination_node, longName=True) != expected_attr:
                raise ValueError('Snapshot does not match the native constrained channel')
        elif cmds.nodeType(destination_node) == 'pairBlend':
            output_attr = 'out'+expected_attr[0].upper()+expected_attr[1:]
            downstream = cmds.listConnections(destination_node+'.'+output_attr, source=False, destination=True, plugs=True) or []
            if not any(identity(node(x.split('.', 1)[0])) == record['constrained_uuid'] and cmds.attributeQuery(x.split('.', 1)[1], node=child, longName=True) == expected_attr for x in downstream):
                raise ValueError('Snapshot pairBlend must still feed the original constrained channel')
        else:
            raise ValueError('Snapshot restore only supports original direct/pairBlend channel outputs')
        node(dst.split('.', 1)[0], editable=True)
        if cmds.getAttr(dst, lock=True):
            raise ValueError('Restore destination locked')
        current = cmds.listConnections(dst, source=True, destination=False, plugs=True) or []
        if current and not cmds.isConnected(src, dst):
            raise ValueError('Restore never overwrites a new driver')
    for identity_value in record['reverse_uuids']:
        existing = cmds.ls(identity_value, long=True) or []
        if existing:
            reverse = info(existing[0])
            tag = existing[0]+'.stagingConstraintManagerOwner'
            if not cmds.objExists(tag) or cmds.getAttr(tag) != record['constraint_uuid']:
                raise ValueError('Snapshot inverse node is not owned by this operation')
            if reverse['constrained_uuid'] not in record['target_uuids'] or [t['uuid'] for t in reverse['targets']] != [record['constrained_uuid']]:
                raise ValueError('Recorded inverse constraint changed')
            node(existing[0], editable=True)
    return record


def output_path(value, new=False):
    p = Path(value).absolute()
    if p.suffix.lower() != '.json' or not p.parent.is_dir() or any(x.is_symlink() or getattr(x, 'is_junction', lambda: False)() for x in [p]+list(p.parents)):
        raise ValueError('JSON file in existing non-linked directory required')
    for part in p.parts[1:]:
        if ':' in part or part.rstrip(' .') != part or re.match(r'(?i)^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', part):
            raise ValueError('Unsafe Windows filename')
    if new and p.exists():
        raise FileExistsError('Existing snapshot protected')
    if not new and (not p.is_file() or p.stat().st_size > 5*1024*1024):
        raise ValueError('Bounded existing snapshot required')
    return p


def preflight(p):
    resources()
    action = p['action']
    if action == 'import_snapshot':
        raw = json.loads(output_path(p['path']).read_text(encoding='utf-8-sig'))
        if not isinstance(raw, dict) or set(raw) != {'schema', 'snapshots'} or raw['schema'] != 1 or not isinstance(raw['snapshots'], list) or not 1 <= len(raw['snapshots']) <= 1000:
            raise ValueError('Unsupported snapshot JSON')
        records = [snapshot_check(x) for x in raw['snapshots']]
        return {'action': action, 'records': records, 'scene_write': False, 'file_write': False, 'gui_acceptance': 'not_run'}
    if action == 'save_list':
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('Enable Undo before saving a scene list')
        name = p['list_name']+'_list'
        if cmds.objExists(name):
            raise ValueError('Existing scene list/name protected')
        return {'action': action, 'name': name, 'items': p['items'], 'scene_write': True, 'file_write': False, 'gui_acceptance': 'not_run'}
    objects = p['objects'] if 'objects' in p else (cmds.ls(selection=True, long=True) or [])
    constraint_nodes = p['constraints'] if 'constraints' in p else discover(objects)
    data = [info(n) for n in constraint_nodes]
    if len({d['uuid'] for d in data}) != len(data):
        raise ValueError('Duplicate constraint aliases')
    if action not in ('inspect', 'weights') and not data:
        raise ValueError('Explicit existing constraints/objects required')
    writes = action not in ('inspect', 'export_snapshot')
    if writes and not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before scene changes')
    for d in data:
        if writes:
            node(d['node'], editable=True)
            node(d['constrained'], editable=True)
    result = {'action': action, 'constraints': data, 'scene_write': writes, 'file_write': action == 'export_snapshot', 'gui_acceptance': 'not_run'}
    if action == 'weights':
        selected = [weight(x)[0] for x in p['selected_weights']]
        all_plugs = [weight(x)[0] for x in p.get('all_weights', p['selected_weights'])]
        if len(set(selected)) != len(selected) or len(set(all_plugs)) != len(all_plugs) or set(selected)-set(all_plugs):
            raise ValueError('Selected weights must be a unique subset of list weights')
        targets = all_plugs if p['mode'] == 'selected_one' else selected
        if p.get('constraints') and any(weight(x)[1]['uuid'] not in {d['uuid'] for d in data} for x in targets):
            raise ValueError('Weight outside explicit constraint scope')
        changes = []
        for value in targets:
            writable(value, allow_curve=p['keyframe'])
            number = (1. if value in selected else 0.) if p['mode'] == 'selected_one' else {'zero': 0., 'one': 1., 'custom': p['value']}[p['mode']]
            changes.append({'plug': value, 'value': number})
        result['changes'] = changes
    elif action in ('disconnect', 'reverse', 'rebuild', 'delete', 'remove_target'):
        for d in data:
            for edge in d['all_outputs']:
                dst = plug(edge['destination'])
                node(dst.split('.', 1)[0], editable=True)
                if cmds.getAttr(dst, lock=True):
                    raise ValueError('Locked destination channel')
            if action in ('disconnect', 'reverse', 'rebuild') and not d['outputs'] and d['uuid'] not in _snapshots:
                raise ValueError('No live outputs or owned snapshot to operate on')
        if action == 'reverse':
            for d in data:
                if d['type'] not in REVERSE_TYPES:
                    raise ValueError('Reverse supports original parent/point/orient/scale/aim types')
                for target in d['targets']:
                    n = node(target['uuid'], editable=True)
                    if n == d['constrained'] or n.startswith(d['constrained']+'|') or d['constrained'].startswith(n+'|'):
                        raise ValueError('Inverse related DAG targets would create a cycle')
                    attrs = ['sx', 'sy', 'sz'] if d['type'] == 'scaleConstraint' else ['rx', 'ry', 'rz'] if d['type'] in ('orientConstraint', 'aimConstraint') else ['tx', 'ty', 'tz'] if d['type'] == 'pointConstraint' else ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
                    for attr in attrs:
                        writable(n+'.'+attr)
                    if cmds.attributeQuery('offsetParentMatrix', node=n, exists=True):
                        writable(n+'.offsetParentMatrix')
                    pending = [n]+(cmds.listRelatives(n, allParents=True, fullPath=True) or [])
                    seen = set()
                    while pending:
                        candidate = node(pending.pop())
                        if identity(candidate) == d['constrained_uuid']:
                            raise ValueError('Inverse target already depends on original constrained object')
                        if candidate in seen:
                            continue
                        seen.add(candidate)
                        if len(seen) > 2000:
                            raise ValueError('Large inverse dependency graph needs manual review')
                        pending.extend(cmds.listConnections(candidate, source=True, destination=False) or [])
        if action == 'remove_target':
            if not p.get('selected_weights'):
                raise ValueError('Selected actual target weight plugs required')
            result['remove'] = []
            for value in p['selected_weights']:
                _, d, t = weight(value)
                if d['uuid'] not in {x['uuid'] for x in data}:
                    raise ValueError('Target plug outside explicit constraint scope')
                if len(d['targets']) <= 1:
                    raise ValueError('Use delete for final target; remove_target preserves a constraint')
                result['remove'].append({'constraint': d['node'], 'target': t['node'], 'constrained': d['constrained'], 'type': d['type']})
            for d in data:
                removed = [x['target'] for x in result['remove'] if x['constraint'] == d['node']]
                if len(removed) != len(set(removed)) or len(removed) >= len(d['targets']):
                    raise ValueError('Removal must leave a target and cannot repeat an alias')
    elif action in ('restore', 'export_snapshot'):
        records = []
        for d in data:
            if d['uuid'] not in _snapshots:
                raise ValueError('No owned disconnect/reverse snapshot')
            records.append(snapshot_check(_snapshots[d['uuid']]))
        result['records'] = records
        if action == 'export_snapshot':
            result['path'] = str(output_path(p['path'], new=True))
    elif action in ('rest', 'axis'):
        if cmds.about(batch=True):
            raise ValueError('Original Maya rest/axis menu procedure requires interactive Maya')
        for d in data:
            if not d['targets']:
                raise ValueError('Native axis/rest operation needs targets')
            siblings = [info(x)['uuid'] for x in discover([d['constrained']]) if info(x)['constrained_uuid'] == d['constrained_uuid']]
            if set(siblings)-{x['uuid'] for x in data}:
                raise ValueError('Native menu acts on all child constraints; include every constraint on that child')
    return result


def restore_record(record):
    snapshot_check(record)
    for identity_value in record['reverse_uuids']:
        existing = cmds.ls(identity_value, long=True) or []
        if existing:
            cmds.delete(existing[0])
    for edge in record['outputs']:
        src, dst = plug(edge['source']), plug(edge['destination'])
        if not cmds.isConnected(src, dst):
            cmds.connectAttr(src, dst)
    return node(record['constraint_uuid'])


def execute(p):
    plan = preflight(p)
    action = p['action']
    if action == 'inspect':
        return plan
    if action == 'import_snapshot':
        _snapshots.update({x['constraint_uuid']: x for x in plan['records']})
        return dict(plan, imported=len(plan['records']))
    if action == 'export_snapshot':
        with Path(plan['path']).open('x', encoding='utf-8', newline='\n') as stream:
            json.dump({'schema': 1, 'snapshots': plan['records']}, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        return plan
    selection = [identity(n) for n in cmds.ls(selection=True, long=True) or []]
    time = cmds.currentTime(query=True)
    auto = cmds.autoKeyframe(query=True, state=True)
    namespace = cmds.namespaceInfo(currentNamespace=True)
    results = []
    try:
        cmds.autoKeyframe(state=False)
        if action == 'weights':
            for change in plan['changes']:
                if p['keyframe']:
                    cmds.setKeyframe(change['plug'], value=change['value'])
                else:
                    cmds.setAttr(change['plug'], change['value'])
            return plan
        if action == 'save_list':
            n = cmds.spaceLocator(name=plan['name'])[0]
            cmds.addAttr(n, longName='notes', dataType='string')
            cmds.setAttr(n+'.notes', json.dumps({'schema': 1, 'items': p['items']}, ensure_ascii=False), type='string')
            return dict(plan, locator=n)
        if action == 'restore':
            return dict(plan, restored=[restore_record(x) for x in plan['records']])
        if action == 'remove_target':
            for row in plan['remove']:
                flags = {'edit': True, 'remove': True}
                if row['type'] in REVERSE_TYPES+('pointOnPolyConstraint',):
                    flags['maintainOffset'] = p['maintain_offset']
                getattr(cmds, row['type'])(row['target'], row['constraint'], **flags)
            return plan
        for d in plan['constraints']:
            if action == 'delete':
                cmds.delete(d['node'])
            elif action in ('disconnect', 'reverse'):
                record = _snapshots.get(d['uuid'])
                if record is None or d['outputs']:
                    record = snapshot(d)
                    _snapshots[d['uuid']] = record
                for edge in record['outputs']:
                    src, dst = plug(edge['source']), plug(edge['destination'])
                    if cmds.isConnected(src, dst):
                        cmds.disconnectAttr(src, dst)
                if action == 'reverse':
                    created = []
                    for target in d['targets']:
                        # Actual inverse direction: original constrained -> each original driver.
                        n = getattr(cmds, d['type'])(d['constrained'], target['node'], maintainOffset=p['maintain_offset'])[0]
                        cmds.addAttr(n, longName='stagingConstraintManagerOwner', dataType='string')
                        cmds.setAttr(n+'.stagingConstraintManagerOwner', d['uuid'], type='string')
                        created.append(identity(n))
                        record['reverse_uuids'].append(identity(n))
                    results.append({'original': d['node'], 'reverse_uuids': created})
                else:
                    results.append(record)
            elif action == 'rebuild':
                # Duplication preserves all native/custom attributes, target offsets,
                # interpolation and input animation connections before old node deletion.
                new = cmds.duplicate(d['node'], inputConnections=True, name=d['node'].split('|')[-1]+'_rebuilt')[0]
                new = node(new)
                for edge in d['all_outputs']:
                    dst = plug(edge['destination'])
                    src = new+'.'+edge['source']['attribute']
                    cmds.disconnectAttr(plug(edge['source']), dst)
                    cmds.connectAttr(src, dst)
                cmds.delete(d['node'])
                new = cmds.rename(new, d['node'].split('|')[-1])
                results.append({'original': d['node'], 'new': node(new), 'new_uuid': identity(new)})
            elif action == 'rest':
                cmds.select(d['constrained'], replace=True)
                mel.eval('SetRestPosition;')
            elif action == 'axis':
                cmds.select(d['constrained'], replace=True)
                mel.eval('doModifyConstraintAxes "1" {"1","1","1","'+str(int(p['maintain_offset']))+'"};')
        return dict(plan, results=results)
    finally:
        cmds.currentTime(time)
        cmds.autoKeyframe(state=auto)
        cmds.namespace(setNamespace=namespace)
        existing = [n for value in selection for n in (cmds.ls(value, long=True) or [])]
        cmds.select(existing, replace=True) if existing else cmds.select(clear=True)
