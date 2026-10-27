import json
from pathlib import Path

_ACTIVE = False
_BASE = set()
_WRITES = {}
_LOADED_HASH = None


def mc():
    from maya import cmds
    return cmds


def identity(n):
    c = mc()
    ref = c.referenceQuery(n, referenceNode=True) if c.referenceQuery(n, isNodeReferenced=True) else None
    return c.ls(n, uuid=True)[0], c.ls(ref, uuid=True)[0] if ref else ''


def nodes():
    return {identity(n): n for n in mc().ls(long=True) or []}


def is_active():
    return int(_ACTIVE)


def require_active():
    if not _ACTIVE:
        raise RuntimeError('写入须经KFAnimRigTool.run')


def check_nodes(names):
    require_active()
    current = nodes()
    for n in names.split(','):
        if not n:
            continue
        key = identity(n.split('.', 1)[0])
        if key in _BASE and key not in _WRITES:
            raise ValueError('MEL目标超出已预检控制器: ' + n)
        if key not in current:
            raise ValueError('对象已失效')


def check_attr(plug):
    require_active()
    n, attr = plug.split('.', 1)
    check_nodes(n)
    key = identity(n)
    if key in _WRITES and attr not in _WRITES[key]:
        raise ValueError('MEL属性超出已预检范围: ' + plug)


def delete_helpers(names):
    require_active()
    c = mc()
    current = nodes()
    own = set(current) - _BASE
    targets = [n for n in names.split(',') if n and c.objExists(n)]
    for n in targets:
        if identity(n) not in own:
            raise ValueError('不删除原场景节点: ' + n)
        for child in c.listRelatives(n, allDescendents=True, fullPath=True) or []:
            if identity(child) not in own:
                raise ValueError('助手混入外部后代')
        for consumer in c.listConnections(n, source=False, destination=True) or []:
            if identity(consumer) in own:
                continue
            # Temporary constraints may legitimately drive the verified KF controls.
            if c.nodeType(n).endswith('Constraint') and identity(consumer) in _WRITES:
                continue
            if c.nodeType(consumer) in ('objectSet', 'shadingEngine'):
                continue
            raise ValueError('助手有外部输出，保留后请Undo')
    if targets:
        c.delete(targets)


def dependencies(args):
    c = mc()
    ns, side, limb = args['_namespace'] + ':', args['_side'], args['_limb']
    action = args['action']
    ik = action.endswith('ik_to_fk')
    reads, writes = [], {}
    tr = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    if limb == 'Pinner':
        if not action.startswith('spline_'):
            raise ValueError('Pinner须spline动作')
        count = c.getAttr(args['control'] + '.jointNum')
        if type(count) is not int or not 2 <= count <= 1000:
            raise ValueError('jointNum须2..1000整数')
        if ik:
            curve = ns + side + '_IKcurve'
            if not c.objExists(curve):
                raise ValueError('缺KF样条曲线')
            shapes = c.listRelatives(curve, shapes=True, fullPath=True) or []
            if len(shapes) != 1 or c.nodeType(shapes[0]) != 'nurbsCurve':
                raise ValueError('需要KF样条shape')
            ncv = c.getAttr(shapes[0] + '.spans') + (c.getAttr(shapes[0] + '.degree') if c.getAttr(shapes[0] + '.form') == 0 else 0)
            reads = [curve] + [ns + 'CTRL_' + side + '_' + str(i) for i in range(count + 1)]
            writes = {ns + 'CTRL_' + side + '_Clus_' + str(i): ['tx', 'ty', 'tz'] for i in range(ncv)}
        else:
            reads = [ns + 'rig_IK_' + side + '_' + str(i) for i in range(count + 1)]
            writes = {ns + 'CTRL_' + side + '_' + str(i): tr + ['sx', 'sy', 'sz'] for i in range(count + 1)}
            writes[ns + 'CTRL_' + side + '_0'] += ['allRotX', 'allRotY', 'allRotZ', 'allLength']
        return writes, reads
    if action.startswith('spline_'):
        raise ValueError('样条动作须Pinner')
    hand = limb == 'Hand'
    dog = not hand and c.attributeQuery('shinRoll', node=args['control'], exists=True)
    bones = ['Shoulder', 'Elbow', 'Wrist'] if hand else ['Hip', 'Knee', 'Shin', 'Ankle', 'Toe'] if dog else ['Hip', 'Knee', 'Ankle', 'Toe']
    fks = [ns + 'CTRL_FK_' + side + '_' + b for b in bones]
    pole = ns + 'CTRL_' + side + ('_ElbowPole' if hand else '_KneePole')
    if ik:
        reads = fks
        writes = {args['control']: tr, pole: ['tx', 'ty', 'tz']}
        if not hand:
            writes[args['control']] += [base + axis for base in ('toe', 'ankle', 'ball', 'toeTip', 'outer', 'inner', 'heel', 'heelTip') for axis in 'XYZ'] + ['toeRoll']
        if dog:
            writes[args['control']] += ['shinRoll', 'limbLen', 'upperLen', 'midLen', 'lowLen']
            writes[ns + 'CTRL_' + side + '_Ind_KneePole'] = ['tx', 'ty', 'tz']
            independent = ns + 'CTRL_' + side + ('_Iso_Trans_IK' if c.objExists(ns + 'CTRL_' + side + '_Iso_Trans_IK') else 'Iso_IK')
            writes[independent] = ['tx', 'ty', 'tz']
            match = ns + 'rig_' + side + '_Foot_IKFK_Match'
            if c.objExists(match):
                reads.append(match)
    else:
        writes = {n: ['rx', 'ry', 'rz'] for n in fks}
        if dog:
            reads = [ns + 'rig_' + side + '_' + b for b in ('Ind_Hip_IK', 'Ind_Knee_IK', 'Shin_FKNull', 'Ankle_IK', 'Toe_IK')]
            writes = {n: tr for n in fks}
        else:
            writes[fks[1]].append('stretch')
            writes[fks[2]].append('stretch')
            reads = [ns + 'rig_' + side + '_' + b + '_IK' for b in bones[:3]]
            reads += [ns + 'rig_' + side + ('_' if hand else '__Leg_') + b + '_Org_MD' for b in ('elbow', 'wrist')]
            if not hand:
                reads.append(ns + side + 'Leg_Toe')
            for md in reads:
                if md.endswith('_Org_MD') and (not c.objExists(md + '.input1X') or abs(c.getAttr(md + '.input1X')) < 1e-12):
                    raise ValueError('KF原长度来源缺失/零')
    return writes, reads


def load_native():
    global _LOADED_HASH
    import hashlib
    from maya import mel
    path = Path(__file__).parent / 'native.mel'
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if _LOADED_HASH != digest:
        mel.eval(path.read_text(encoding='utf-8'))
        _LOADED_HASH = digest


def invoke(action):
    from .tool import KFAnimRigTool
    c = mc()
    if c.confirmDialog(title='KF referenced rig edits', message='Match writes referenced KF rig controls. Continue in backup scene?', button=['Yes', 'No'], defaultButton='No') != 'Yes':
        return None
    result = KFAnimRigTool().run(action=action, allow_reference_edits=True)
    if not result.success:
        raise RuntimeError(result.message)
    return result.data


def invoke_timeline(which):
    return invoke('bake_ik_to_fk' if int(which) == 0 else 'bake_fk_to_ik')


def execute(args):
    global _ACTIVE, _BASE, _WRITES
    c = mc()
    if args['action'] == 'inspect':
        return {'control': args['control'], 'limb': args['_limb'], 'namespace': args['_namespace'], 'referenced': c.referenceQuery(args['control'], isNodeReferenced=True), 'requires_original_kf_rig': True, 'switches_pinner': False}
    load_native()
    from maya import mel
    if args['action'] == 'open_ui':
        mel.eval('mtbKF_kfAnimRig_IKFK();')
        return {'window': 'mtbKF_RigMatchWin'}
    current, auto, selection, ns = c.currentTime(query=True), c.autoKeyframe(query=True, state=True), c.ls(selection=True, long=True) or [], c.namespaceInfo(currentNamespace=True)
    _BASE = set(nodes())
    _WRITES = {identity(n): attrs for n, attrs in args['_destinations'].items()}
    _ACTIVE = True
    action = args['action']
    proc = 'matchIKtoFKTen' if action == 'spline_ik_to_fk' else 'matchFKtoIKTen' if action == 'spline_fk_to_ik' else 'matchIKtoFK' if action.endswith('ik_to_fk') else 'matchFKtoIK'
    try:
        c.autoKeyframe(state=False)
        c.namespace(setNamespace=':')
        frames = range(args['start'], args['end'] + 1) if action.startswith('bake_') else [current]
        for frame in frames:
            if c.currentTime(query=True) != frame:
                c.currentTime(frame)
            c.select(args['control'], replace=True)
            mel.eval('mtbKF_' + proc + '();')
            if action.startswith('bake_'):
                for n, attrs in args['_destinations'].items():
                    c.setKeyframe(n, attribute=attrs, time=frame)
        return {'matched': args['control'], 'procedure': proc, 'targets': args['_destinations'], 'frame_count': len(frames), 'switches_pinner': False}
    finally:
        try:
            fresh = {key: n for key, n in nodes().items() if key not in _BASE}
            # Do not delete target animation curves or blends implicitly created by Maya.
            disposable = [n for n in fresh.values() if c.nodeType(n) in ('transform', 'parentConstraint', 'pointConstraint', 'rebuildCurve')]
            if disposable:
                roots = [n for n in disposable if not any(n.startswith(other + '|') for other in disposable if n != other)]
                delete_helpers(','.join(roots))
        finally:
            try:
                if c.currentTime(query=True) != current:
                    c.currentTime(current)
                if (c.ls(selection=True, long=True) or []) != selection:
                    c.select(selection, replace=True) if selection else c.select(clear=True)
                c.namespace(setNamespace=ns)
                c.autoKeyframe(state=auto)
            finally:
                _ACTIVE, _BASE, _WRITES = False, set(), {}
