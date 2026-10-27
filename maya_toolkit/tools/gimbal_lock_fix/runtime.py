import math

_ACTIVE = False
_CURVES = set()


def shortest_angle(first, second):
    a = (first.x, first.y, first.z, first.w)
    b = (second.x, second.y, second.z, second.w)
    norm = math.sqrt(sum(v * v for v in a) * sum(v * v for v in b))
    if not math.isfinite(norm) or norm <= 0:
        raise ValueError('四元数无有效归一化长度')
    dot = abs(sum(x * y for x, y in zip(a, b)) / norm)
    return 2 * math.acos(min(1.0, max(0.0, dot)))


def require_active():
    if not _ACTIVE:
        raise RuntimeError('写入必须经过标准GimbalFixTool.run')


def execute(args):
    global _ACTIVE, _CURVES
    from maya import cmds
    from . import native
    if args['action'] == 'open_ui':
        native.create_gimbal_fix_ui()
        return {'window': 'mtbGimbalFixerUI'}
    if _ACTIVE:
        raise RuntimeError('已有修复在运行')
    current = cmds.currentTime(query=True)
    selected = cmds.ls(selection=True, long=True) or []
    auto = cmds.autoKeyframe(query=True, state=True)
    _ACTIVE, _CURVES = True, {c for p in args['plans'] for c in p['curves']}
    result = []
    try:
        if args['action'] == 'fix':
            cmds.autoKeyframe(state=False)
        algorithm = native._Algorithm()
        for item in args['plans']:
            if args['action'] == 'detect':
                ranges = algorithm.detect_gimbal_issues(item['object'], args['threshold'])
                result.append({'object': item['object'], 'problem_ranges': ranges, 'rotation_order': item['rotation_order']})
            else:
                fixed = algorithm.fix_animation_curves(item['object'], item['start'], item['end'], args['samples_per_frame'])
                if not fixed:
                    raise RuntimeError('原算法未完成修复: ' + item['object'])
                result.append({'object': item['object'], 'fixed': fixed, 'sample_count': item['sample_count'], 'curves': item['curves']})
        return {'action': args['action'], 'results': result}
    finally:
        try:
            if args['action'] == 'fix':
                if cmds.currentTime(query=True) != current:
                    cmds.currentTime(current)
                if (cmds.ls(selection=True, long=True) or []) != selected:
                    cmds.select(selected, replace=True) if selected else cmds.select(clear=True)
                cmds.autoKeyframe(state=auto)
        finally:
            _ACTIVE, _CURVES = False, set()
