import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA
from . import state


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    cmds = state.maya()
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原窗口需要实际 Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    nodes = args['objects'] or cmds.ls(selection=True, long=True) or []
    if not nodes:
        raise ValueError('请提供对象或选择')
    resolved = []
    for node in nodes:
        found = cmds.ls(node, long=True) or []
        if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('对象缺失、重名或非 transform: ' + node)
        resolved.append(found[0])
    if len(set(resolved)) != len(resolved):
        raise ValueError('对象不得重复')
    args['objects'] = resolved
    if args['start'] is None:
        args['start'], args['end'] = int(cmds.playbackOptions(query=True, min=True)), int(cmds.playbackOptions(query=True, max=True))
    for node in resolved:
        if args['action'] == 'create':
            continue  # Only read a controller to create a separate new locator.
        record = state.load(node)
        owned = state.safe(record)
        if record['failed'] and args['action'] != 'clear':
            raise ValueError('上次执行留下部分节点，请先 Undo 或 clear')
        controller = state.find(record['controller'])
        if args['action'] == 'attach':
            if any(cmds.nodeType(item) == 'aimConstraint' for item in owned):
                raise ValueError('Aim 已建立，请先 bake/clear/Undo 后再附着')
            writable = [(node, 'translate'), (node, 'rotate')]
            if args['keys_only'] and not cmds.keyframe(controller, query=True, time=(args['start'], args['end']), timeChange=True):
                raise ValueError('控制器范围内没有键；显式 keys_only=False 逐帧附着')
        elif args['action'] in ('aim', 'bake'):
            writable = [(controller, 'rotate')]
            has_aim = any(cmds.nodeType(item) == 'aimConstraint' for item in owned)
            if args['action'] == 'aim' and has_aim:
                raise ValueError('已有候选 Aim，拒绝重复建立')
            if args['action'] == 'bake' and not has_aim:
                raise ValueError('请先建立候选 Aim')
            if args['action'] == 'aim' and cmds.xform(node, query=True, worldSpace=True, translation=True) == cmds.xform(controller, query=True, worldSpace=True, translation=True):
                raise ValueError('请先把 Aim Locator 移离控制器位置')
            if args['action'] == 'bake' and args['keys_only'] and not cmds.keyframe(node, query=True, time=(args['start'], args['end']), timeChange=True):
                raise ValueError('定位器范围内没有键，拒绝删除旧旋转键后空烘焙')
        else:
            writable = []
        ids = {state.identity(item) for item in owned}
        for target, channel in writable:
            if cmds.referenceQuery(target, isNodeReferenced=True) or cmds.lockNode(target, query=True, lock=True)[0]:
                raise ValueError('写入对象引用或锁定')
            for attr in [channel] + [channel + axis for axis in 'XYZ']:
                plug = target + '.' + attr
                if cmds.getAttr(plug, lock=True):
                    raise ValueError('通道锁定: ' + plug)
                if any(state.identity(driver) not in ids and not cmds.nodeType(driver).startswith('animCurve') for driver in (cmds.listConnections(plug, source=True, destination=False) or [])):
                    raise ValueError('已有外部约束/表达式/动画层/混合驱动: ' + plug)
    return args


class BhAimTool(BaseMayaTool):
    tool_id = 'bh_aim_tools_v1_1'
    tool_name = 'bh_aimTools 定位器朝向'
    category = 'animation'
    version = '1.1.1-adapter'
    description = '完整原定位器创建、附着、Aim及关键帧/逐帧烘焙；显式旧键删除与候选所有权保护。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过，不 source 或改变 UI/场景', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from . import runtime
        if args['action'] == 'open_ui':
            import maya.mel as mel
            data = runtime.load_suite()
            mel.eval('mtbAim_bh_aimTools();')
            return ToolResult.ok(data=dict(data, window='mtbAim_bh_aimTools'))
        data = runtime.execute(args)
        return ToolResult.ok(message='bh_aimTools 操作完成', data=data, warnings=data['warnings'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
