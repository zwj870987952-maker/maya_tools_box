"""Scene operations separated from Qt; metadata and constraints have explicit ownership."""
import json
import uuid
from pathlib import Path
from .contracts import pairs as normalize_pairs

OWNER = 'maya_toolkit.animation_retarget.v1'
SCALARS = {'bool', 'byte', 'char', 'short', 'long', 'float', 'double', 'doubleAngle', 'doubleLinear', 'enum'}
VECTORS = {'double2', 'double3', 'float2', 'float3', 'long2', 'long3', 'short2', 'short3'}
TRS = [channel + axis for channel in ('translate', 'rotate', 'scale') for axis in 'XYZ']


def maya():
    import maya.cmds as cmds
    return cmds


def resolve(name):
    cmds = maya()
    found = cmds.ls(name, long=True) or []
    if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('对象缺失、重名或不是 transform: ' + name)
    return found[0]


def node_uuid(node):
    return maya().ls(node, uuid=True)[0]


def by_uuid(value):
    found = maya().ls(value, long=True) or []
    if len(found) != 1:
        raise ValueError('记录中的对象已删除或 UUID 无效: ' + value)
    return found[0]


def string_attr(node, attr, value):
    cmds = maya()
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType='string')
    cmds.setAttr(node + '.' + attr, value, type='string')


def read_owned():
    cmds = maya()
    records = []
    for node in cmds.ls(type='network') or []:
        if not cmds.attributeQuery('retargetOwner', node=node, exists=True) or cmds.getAttr(node + '.retargetOwner') != OWNER:
            continue
        data = json.loads(cmds.getAttr(node + '.retargetData'))
        if data.get('version') != 1 or not isinstance(data.get('constraints'), list):
            raise ValueError('候选信息节点格式损坏: ' + node)
        pair = normalize_pairs([data['pair']])[0]
        pair['source'] = by_uuid(data['source_uuid'])
        pair['target'] = by_uuid(data['target_uuid'])
        records.append({'node': node, 'data': data, 'pair': pair, 'legacy': False})
    return records


def legacy_pose(value):
    pose = json.loads(value)
    result = {attr: {'type': 'double', 'value': pose[attr]} for attr in TRS if attr in pose}
    # Original comma/colon serialization cannot recover strings containing separators.
    # Preserve scalar numbers and plain strings only; never eval legacy data.
    for field in pose.get('otherAttributes', '').split(','):
        if ':' not in field:
            continue
        attr, raw = field.split(':', 1)
        try:
            result[attr] = {'legacy': True, 'value': float(raw)}
        except ValueError:
            result[attr] = {'legacy': True, 'value': raw}
    return result


def records(include_legacy=True):
    cmds = maya()
    result = read_owned()
    existing = {(row['pair']['source'], row['pair']['target']) for row in result}
    if include_legacy and cmds.objExists('|Rematch|RematchInfo'):
        node = '|Rematch|RematchInfo'
        for attr in cmds.listAttr(node, userDefined=True) or []:
            if not attr.endswith('_pairInfo'):
                continue
            base = attr[:-9]
            pair = normalize_pairs([{'text': cmds.getAttr(node + '.' + attr), 'modes': json.loads(cmds.getAttr(node + '.' + base + '_modes'))}])[0]
            pair['source'], pair['target'] = resolve(pair['source']), resolve(pair['target'])
            if (pair['source'], pair['target']) in existing:
                continue
            result.append({'node': node, 'pair': pair, 'legacy': True, 'data': {
                'source_pose': legacy_pose(cmds.getAttr(node + '.' + base + '_sourcePose')),
                'target_pose': legacy_pose(cmds.getAttr(node + '.' + base + '_targetPose')), 'constraints': []}})
    return result


def attributes(node, channel):
    cmds = maya()
    if channel != 'other':
        return [channel + axis for axis in 'XYZ']
    result = []
    for attr in cmds.listAttr(node, userDefined=True, keyable=True) or []:
        children = cmds.attributeQuery(attr, node=node, listChildren=True) or []
        result.extend(children or [attr])
    return list(dict.fromkeys(result))


def pose(node):
    cmds = maya()
    result, skipped = {}, []
    for attr in list(dict.fromkeys(TRS + (cmds.listAttr(node, userDefined=True) or []))):
        plug = node + '.' + attr
        try:
            kind = cmds.getAttr(plug, type=True)
            if cmds.attributeQuery(attr, node=node, multi=True) or kind not in SCALARS | VECTORS | {'string', 'matrix'}:
                skipped.append(plug)
                continue
            value = cmds.getAttr(plug)
            if kind in VECTORS and value:
                value = value[0]
            json.dumps(value, allow_nan=False)
            result[attr] = {'type': kind, 'value': value}
        except Exception:
            skipped.append(plug)
    return result, skipped


def active_constraints(record):
    cmds = maya()
    nodes = []
    for identity in record['data']['constraints']:
        found = cmds.ls(identity, long=True) or []
        if not found:
            continue
        node = found[0]
        if not cmds.objectType(node, isAType='constraint') or not cmds.attributeQuery('retargetOwner', node=node, exists=True) or cmds.getAttr(node + '.retargetOwner') != OWNER:
            raise ValueError('记录中的约束不属于本候选: ' + node)
        if not cmds.attributeQuery('retargetPair', node=node, exists=True) or cmds.getAttr(node + '.retargetPair') != record['data']['pair_id']:
            raise ValueError('约束配对身份不匹配: ' + node)
        # Verify the constraint still drives this record's original target.
        targets = cmds.listConnections(node, source=False, destination=True, type='transform') or []
        if record['data']['target_uuid'] not in {node_uuid(target) for target in targets}:
            raise ValueError('约束输出已被重接，拒绝自动删除: ' + node)
        nodes.append(node)
    return nodes


def plan(args):
    cmds = maya()
    action = args['action']
    if action in ('save_config', 'load_config'):
        return args
    args = dict(args, pairs=[dict(row, source=resolve(row['source']), target=resolve(row['target'])) for row in args['pairs']])
    if any(row['source'] == row['target'] for row in args['pairs']):
        raise ValueError('不同名称实际指向同一对象')
    if action != 'load_scene' and not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    if action in ('load_scene', 'restore_pose'):
        selected = {(row['source'], row['target']) for row in args['pairs']}
        found = [record for record in records() if not selected or (record['pair']['source'], record['pair']['target']) in selected]
        if action == 'restore_pose' and (not found or (selected and len(found) != len(selected))):
            raise ValueError('没有找到所选配对的完整姿态记录')
        args['records'] = found
        return args
    if len({row['target'] for row in args['pairs']}) != len(args['pairs']):
        raise ValueError('每次调用只能有一个源驱动每个目标')
    # Reject dependency cycles and ancestor/descendant constraints before scene writes.
    edges = {row['target']: row['source'] for row in args['pairs']}
    for target in edges:
        visited, cursor = set(), target
        while cursor in edges:
            if cursor in visited:
                raise ValueError('配对形成循环依赖')
            visited.add(cursor)
            cursor = edges[cursor]
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    owned = read_owned()
    for row in args['pairs']:
        if action == 'align':
            if row['source'].startswith(row['target'] + '|') or row['target'].startswith(row['source'] + '|'):
                raise ValueError('约束配对不能为祖先与后代')
            for record in owned:
                if record['pair']['target'] == row['target'] and active_constraints(record):
                    raise ValueError('目标已有候选约束；先烘焙后重新对位')
        for channel, mode in row['modes'].items():
            if mode == 'none' or action == 'bake' or (action == 'numeric_copy' and mode != 'numeric'):
                continue
            for attr in attributes(row['source'], channel):
                plug = row['target'] + '.' + attr
                if not cmds.objExists(plug):
                    continue  # Missing custom attributes are reported by execution.
                if cmds.getAttr(plug, lock=True):
                    raise ValueError('目标通道锁定: ' + plug)
                if cmds.referenceQuery(row['target'], isNodeReferenced=True) and mode == 'constraint':
                    raise ValueError('约束目标为引用节点，请先在副本中处理')
                drivers = cmds.listConnections(plug, source=True, destination=False) or []
                if any(not cmds.nodeType(driver).startswith('animCurve') for driver in drivers):
                    raise ValueError('目标通道已有非动画曲线驱动: ' + plug)
    if args['start'] is None:
        args['start'] = int(cmds.playbackOptions(query=True, min=True))
        args['end'] = int(cmds.playbackOptions(query=True, max=True))
    return args


def numeric_copy(rows, start, end):
    cmds = maya()
    operations = [row for row in rows if 'numeric' in row['modes'].values()]
    frames = sorted({frame for row in operations for frame in (cmds.keyframe(row['source'], query=True, timeChange=True) or []) if start <= frame <= end})
    warnings, keyed = [], []
    for frame in frames:
        cmds.currentTime(frame)
        for row in operations:
            for channel, mode in row['modes'].items():
                if mode != 'numeric':
                    continue
                for attr in attributes(row['source'], channel):
                    source, target = row['source'] + '.' + attr, row['target'] + '.' + attr
                    if not cmds.objExists(target) or cmds.getAttr(source, type=True) not in SCALARS or cmds.getAttr(target, type=True) not in SCALARS:
                        warnings.append('缺失或不可关键帧属性: ' + target)
                        continue
                    cmds.setKeyframe(target, time=frame, value=cmds.getAttr(source, time=frame))
                    keyed.append({'plug': target, 'frame': frame})
    return {'frames': frames, 'keyed': keyed, 'warnings': list(dict.fromkeys(warnings))}


def align(args):
    cmds = maya()
    constraint_nodes, warnings, info_nodes = [], [], []
    for row in args['pairs']:
        # Snapshot before either constraints or numeric copies are applied.
        source_pose, skipped_a = pose(row['source'])
        target_pose, skipped_b = pose(row['target'])
        warnings.extend('姿态未支持属性: ' + plug for plug in skipped_a + skipped_b)
        matches = [rec for rec in read_owned() if rec['pair']['source'] == row['source'] and rec['pair']['target'] == row['target']]
        if len(matches) > 1:
            raise ValueError('重复候选信息节点，请先在副本中检查')
        node = matches[0]['node'] if matches else cmds.createNode('network', name='animationRetargetInfo')
        pair_id = matches[0]['data']['pair_id'] if matches else uuid.uuid4().hex
        created = []
        for channel, command in (('translate', cmds.pointConstraint), ('rotate', cmds.orientConstraint), ('scale', cmds.scaleConstraint)):
            if row['modes'][channel] == 'constraint':
                for constraint in command(row['source'], row['target'], maintainOffset=True):
                    string_attr(constraint, 'retargetOwner', OWNER)
                    string_attr(constraint, 'retargetPair', pair_id)
                    created.append(constraint)
        data = {'version': 1, 'pair_id': pair_id, 'pair': row, 'source_uuid': node_uuid(row['source']), 'target_uuid': node_uuid(row['target']),
                'source_pose': source_pose, 'target_pose': target_pose, 'constraints': [node_uuid(node) for node in created]}
        string_attr(node, 'retargetOwner', OWNER)
        string_attr(node, 'retargetData', json.dumps(data, ensure_ascii=False, allow_nan=False))
        info_nodes.append(node)
        constraint_nodes.extend(created)
    result = numeric_copy(args['pairs'], args['start'], args['end'])
    result.update(constraints=constraint_nodes, info_nodes=info_nodes, warnings=warnings + result['warnings'])
    return result


def bake(args):
    cmds = maya()
    targets = [row['target'] for row in args['pairs']]
    selected = {node_uuid(node) for node in targets}
    deletion = [node for record in read_owned() if record['data']['target_uuid'] in selected for node in active_constraints(record)]
    options = {'time': (args['start'], args['end']), 'simulation': True}
    if args['smart']:
        options.update(sampleBy=1, oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                       sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
                       bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False, shape=True, smart=True)
    cmds.bakeResults(targets, **options)
    if deletion:
        cmds.delete(deletion)
    return {'targets': targets, 'deleted_owned_constraints': deletion, 'smart': args['smart'], 'range': [args['start'], args['end']],
            'warnings': ['烘焙覆盖目标所有可烘焙通道；none 模式不限制烘焙范围。']}


def restore_pose(args):
    cmds = maya()
    restored, skipped = [], []
    for record in args['records']:
        for side in ('source', 'target'):
            node = record['pair'][side]
            for attr, entry in record['data'][side + '_pose'].items():
                plug = node + '.' + attr
                if not cmds.objExists(plug) or not cmds.getAttr(plug, settable=True):
                    skipped.append(plug)
                    continue
                kind = cmds.getAttr(plug, type=True)
                if not entry.get('legacy') and kind != entry['type'] and not (attr in TRS and entry['type'] == 'double'):
                    skipped.append(plug)
                    continue
                value = entry['value']
                try:
                    if kind == 'string' and isinstance(value, str):
                        cmds.setAttr(plug, value, type='string')
                    elif kind in SCALARS and type(value) in (bool, int, float):
                        cmds.setAttr(plug, value)
                    elif kind in VECTORS | {'matrix'} and isinstance(value, (list, tuple)):
                        cmds.setAttr(plug, *value, type=kind)
                    else:
                        skipped.append(plug)
                        continue
                    restored.append(plug)
                except Exception:
                    skipped.append(plug)
    return {'restored': restored, 'skipped': skipped, 'warnings': ['跳过锁定、被驱动、不匹配或无法恢复的属性: ' + plug for plug in skipped]}


def execute(args):
    action = args['action']
    if action == 'save_config':
        # Exclusive creation protects against collisions occurring after preflight.
        rows = [{'text': row['source'] + ' , ' + row['target'], 'modes': row['modes']} for row in args['pairs']]
        with Path(args['path']).open('x', encoding='utf-8', newline='\n') as handle:
            json.dump(rows, handle, ensure_ascii=False, indent=2, allow_nan=False)
        return {'path': args['path'], 'pairs': args['pairs'], 'warnings': ['配置文件写入不能由 Maya Undo 撤回。']}
    if action == 'load_config':
        from .contracts import normalize
        return {'pairs': normalize(action='load_config', path=args['path'])['pairs']}
    if action == 'load_scene':
        return {'pairs': [record['pair'] for record in args['records']], 'legacy_records': sum(record['legacy'] for record in args['records']),
                'warnings': ['旧姿态的逗号/冒号序列化有不可恢复的歧义。'] if any(record['legacy'] for record in args['records']) else []}
    cmds = maya()
    current_time = cmds.currentTime(query=True)
    selected = cmds.ls(selection=True, long=True) or []
    try:
        if action == 'align':
            return align(args)
        if action == 'numeric_copy':
            return numeric_copy(args['pairs'], args['start'], args['end'])
        if action == 'bake':
            return bake(args)
        if action == 'restore_pose':
            return restore_pose(args)
        raise ValueError('未知操作')
    finally:
        cmds.currentTime(current_time)
        live = [node for node in selected if cmds.objExists(node)]
        cmds.select(live, replace=True) if live else cmds.select(clear=True)
