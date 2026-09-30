"""Run the complete original MEL algorithms under one explicit candidate context."""
import json
from pathlib import Path
from . import state

PACKAGE = Path(__file__).parent
_ACTIVE = None


def require_active():
    if _ACTIVE is None:
        raise RuntimeError('内部写场景 MEL 仅允许通过 BhAimTool.run() 调用')


def load_suite():
    import maya.mel as mel
    path = PACKAGE / 'runtime.mel'
    catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
    marker = catalog['runtime_procedures'][0]
    if not str(mel.eval('whatIs ' + marker + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    for name in catalog['runtime_procedures']:
        if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
            raise RuntimeError('MEL 来源冲突: ' + name)
    return {'procedures': catalog['runtime_procedures'], 'source': path.as_posix()}


def capture_active():
    require_active()
    record = _ACTIVE['record']
    if record:
        state.capture(record, _ACTIVE['before'])
    return record


def delete_parent_constraints():
    cmds = state.maya()
    record = capture_active()
    locator = state.find(record['locator'])
    nodes = cmds.listRelatives(locator, type='parentConstraint', fullPath=True) or []
    ids = {state.identity(node) for node in state.owned(record)}
    if any(state.identity(node) not in ids for node in nodes):
        raise RuntimeError('不删除外部 parentConstraint')
    values = [state.identity(node) for node in nodes]
    for value in values:
        node = state.find(value)
        if cmds.listRelatives(node, parent=True):
            cmds.parent(node, world=True)
        cmds.delete(state.find(value))


def delete_locator():
    cmds = state.maya()
    record = capture_active()
    nodes = state.safe(record)
    # Detach owned constraints before deleting locators, protecting empty controls.
    ids = [state.identity(node) for node in nodes if cmds.nodeType(node).endswith('Constraint')]
    for value in ids:
        node = state.find(value)
        if node:
            if cmds.listRelatives(node, parent=True):
                cmds.parent(node, world=True)
            cmds.delete(state.find(value))
    locator = state.find(record['locator'])
    if locator:
        cmds.delete(locator)


def execute(args):
    global _ACTIVE
    import maya.mel as mel
    cmds = state.maya()
    load_suite()
    saved_time = cmds.currentTime(query=True)
    selection = cmds.ls(selection=True, long=True) or []
    saved_range = [cmds.playbackOptions(query=True, **{key: True}) for key in ('min', 'max', 'animationStartTime', 'animationEndTime')]
    refresh = cmds.refresh(query=True, suspend=True)
    evaluation = cmds.evaluationManager(query=True, mode=True)[0]
    cache = bool(mel.eval('evaluator -q -name "cache";'))
    results = []
    success = False
    try:
        cmds.playbackOptions(min=args['start'], max=args['end'])
        mel.eval('global int $mtbAim_keysOnly; global int $mtbAim_deleteKeys; $mtbAim_keysOnly = ' + str(int(args['keys_only'])) + '; $mtbAim_deleteKeys = ' + str(int(args['delete_rotation_keys'])) + ';')
        for node in args['objects']:
            before = {state.identity(item) for item in cmds.ls(long=True) or []}
            record = None if args['action'] == 'create' else state.load(node)
            _ACTIVE = {'before': before, 'record': record}
            cmds.select(node, replace=True)
            error = None
            try:
                if args['action'] == 'clear':
                    delete_locator()
                else:
                    commands = {'create': 'mtbAim_bh_createAimLoc', 'attach': 'mtbAim_bh_attachLoc', 'aim': 'mtbAim_bh_aimCtrlAtLoc', 'bake': 'mtbAim_bh_bakeFromAimLoc'}
                    mel.eval(commands[args['action']] + '();')
                if args['action'] == 'create':
                    locators = [item for item in cmds.ls(type='transform', long=True) or [] if state.identity(item) not in before and cmds.attributeQuery('ctrl', node=item, exists=True)]
                    if len(locators) != 1:
                        raise RuntimeError('未创建唯一 Aim Locator')
                    record = state.create(locators[0], node)
                    _ACTIVE['record'] = record
                if record:
                    record['stage'] = args['action']
            except Exception as caught:
                error = caught
                raise
            finally:
                if record and state.find(record['locator']):
                    record['failed'] = error is not None
                    capture_active()
            results.append({'locator_uuid': record['locator'], 'locator': state.find(record['locator']),
                            'controller': state.find(record['controller']),
                            'retained_blend_nodes': [state.find(row['uuid']) for row in record['owned'] if row['type'] == 'pairBlend' and state.find(row['uuid'])]})
        success = True
        return {'action': args['action'], 'range': [args['start'], args['end']], 'items': results,
                'warnings': ['Maya pairBlend/混合属性按原流程可能保留；检查实际动画，不自动删除原动画曲线。'] if any(row['retained_blend_nodes'] for row in results) else []}
    finally:
        _ACTIVE = None
        mel.eval('evaluator -name "cache" -enable ' + str(int(cache)) + ';')
        cmds.evaluationManager(mode=evaluation)
        cmds.refresh(suspend=refresh)
        cmds.playbackOptions(min=saved_range[0], max=saved_range[1], animationStartTime=saved_range[2], animationEndTime=saved_range[3])
        cmds.currentTime(saved_time)
        selected = [row['locator'] if args['action'] == 'create' else row['controller'] for row in results] if success and args['action'] in ('create', 'bake') else selection
        selected = [node for node in selected if node and cmds.objExists(node)]
        cmds.select(selected, replace=True) if selected else cmds.select(clear=True)
