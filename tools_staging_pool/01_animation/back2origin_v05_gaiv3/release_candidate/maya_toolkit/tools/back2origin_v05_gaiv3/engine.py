"""Original algorithms with argument-based orchestration and restored runtime state."""
from .contracts import normalize

KEYWORDS = {'root_control': ['RootX_M'], 'ik_controls': ['IKLeg_R', 'IKLeg_L'],
            'pv_controls': ['PoleLeg_R', 'PoleLeg_L'], 'other_controls': [], 'global_control': ['Main']}


def maya():
    import maya.cmds as cmds
    return cmds


def discover(namespace=None):
    cmds = maya()
    result = {role: [] for role in KEYWORDS}
    namespaces = {''}
    for node in sorted(cmds.ls(type='transform', long=True) or []):
        leaf = node.rsplit('|', 1)[-1]
        ns, unused_separator, name = leaf.rpartition(':')
        for role, words in KEYWORDS.items():
            if any(name.casefold() == word.casefold() for word in words):
                namespaces.add(ns)
                if namespace is None or namespace == ns:
                    result[role].append(node)
    ambiguous = [role for role in ('root_control', 'global_control') if len(result[role]) > 1]
    return {'matches': result, 'namespaces': sorted(namespaces), 'ambiguous': ambiguous}


def resolve(node):
    if not node or any(char in node for char in '.*?[]\n\r'):
        raise ValueError('需要明确 transform 名称: ' + str(node))
    cmds = maya()
    found = cmds.ls(node, long=True) or []
    if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('对象缺失、重名或非 transform: ' + node)
    return found[0]


def writable(node, axes):
    cmds = maya()
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
        raise ValueError('写入目标引用或节点锁定: ' + node)
    for attr in ['translate'] + ['translate' + axis for axis in axes]:
        plug = node + '.' + attr
        if cmds.getAttr(plug, lock=True):
            raise ValueError('位移通道锁定: ' + plug)
        incoming = cmds.listConnections(plug, source=True, destination=False) or []
        if any(not cmds.nodeType(driver).startswith('animCurve') for driver in incoming):
            raise ValueError('位移已有非动画曲线驱动（动画层/约束需先准备副本）: ' + plug)


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] in ('inventory', 'discover'):
        return args
    cmds = maya()
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原生窗口需要真实 Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    args['root_control'] = resolve(args['root_control'])
    if args['global_control']:
        args['global_control'] = resolve(args['global_control'])
    elif args['action'] == 'reverse':
        raise ValueError('reverse 必须提供 global_control')
    for role in ('ik_controls', 'pv_controls', 'other_controls'):
        args[role] = [resolve(node) for node in args[role]]
    nodes = [args['root_control']] + ([args['global_control']] if args['global_control'] else []) + sum((args[role] for role in ('ik_controls', 'pv_controls', 'other_controls')), [])
    if len(set(nodes)) != len(nodes):
        raise ValueError('各角色对象不得重复')
    for node in nodes:
        # Original thinning cuts translate on all three axes when step > 1.
        axes = args['channels'] if node in (args['root_control'], args['global_control']) and args['frame_step'] == 1 else 'XYZ'
        writable(node, axes)
    if args['start'] is None:
        args['start'], args['end'] = int(cmds.playbackOptions(query=True, min=True)), int(cmds.playbackOptions(query=True, max=True))
    if args['start'] > args['end']:
        raise ValueError('无效播放范围')
    args['objects'] = nodes
    return args


def execute(args):
    cmds = maya()
    from . import algorithms as original
    from .reverse import reverse
    saved_time = cmds.currentTime(query=True)
    saved_selection = cmds.ls(selection=True, long=True) or []
    saved_eval = cmds.evaluationManager(query=True, mode=True)[0]
    saved_refresh = cmds.refresh(query=True, suspend=True)
    saved_range = [cmds.playbackOptions(query=True, **{flag: True}) for flag in ('min', 'max', 'animationStartTime', 'animationEndTime')]
    try:
        cmds.evaluationManager(mode='off')
        cmds.refresh(suspend=True)
        root, global_node = args['root_control'], args['global_control']
        ik, pv, other = (args[name] for name in ('ik_controls', 'pv_controls', 'other_controls'))
        start, end = args['start'], args['end']
        if args['action'] == 'reverse':
            reverse(args)
        else:
            ik_pos, pv_pos = original.calculate_ik_positions(root, ik, pv, start, end)
            other_pos = original.calculate_other_positions(root, other, start, end)
            root_pos = original.calculate_root_world_positions(root, args['channels'], start, end)
            original.zero_out_root_control(root, args['channels'], start, end)
            original.reapply_ik_positions(ik, pv, ik_pos, pv_pos, root, start, end)
            original.reapply_other_positions(other, other_pos, root, start, end)
            original.reapply_root_world_positions(global_node, root_pos, args['channels'], start, end)
            original.optimize_keyframes(root, global_node, ik, pv, other, args['frame_step'], start, end)
        warnings = ['原帧步长按绝对 frame % step 删 translate 键；大于1时含未选的平移轴。'] if args['frame_step'] > 1 else []
        if not global_node:
            warnings.append('未提供 global_control：只归零 root 并重采样其他控制器，不保存位移动量。')
        return {'action': args['action'], 'objects': args['objects'], 'range': [start, end], 'sampled_frames': end - start + 1, 'frame_step': args['frame_step'], 'warnings': warnings}
    finally:
        cmds.playbackOptions(min=saved_range[0], max=saved_range[1], animationStartTime=saved_range[2], animationEndTime=saved_range[3])
        cmds.currentTime(saved_time)
        existing = [node for node in saved_selection if cmds.objExists(node)]
        cmds.select(existing, replace=True) if existing else cmds.select(clear=True)
        cmds.refresh(suspend=saved_refresh)
        cmds.evaluationManager(mode=saved_eval)
