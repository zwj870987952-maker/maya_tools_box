import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    from . import proxy, runtime
    if runtime._ACTIVE:
        raise ValueError('已有本工具运行中')
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('Dockable Qt UI需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    if args['action'] == 'cleanup':
        matches = [(n, data) for n, data in proxy.records() if proxy.identity(n) == args['record_id']]
        if len(matches) != 1:
            raise ValueError('cleanup需要明确本工具record UUID')
        proxy.validate_resources(matches[0][1], args['remove_layers'])
        return args
    if len(args['controllers']) != args['feet_number'] + 4:
        raise ValueError('控制器数量需要feet_number+4，顺序Master/feet/MainBody/Upperbody/Head')
    controllers = []
    for name in args['controllers']:
        values = cmds.ls(name, long=True) or []
        if len(values) != 1 or not cmds.objectType(values[0], isAType='transform'):
            raise ValueError('需要唯一transform/joint: ' + name)
        node = values[0]
        if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
            raise ValueError('控制器引用/锁定: ' + node)
        for attr in ('translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ'):
            plug = node + '.' + attr
            if cmds.getAttr(plug, lock=True):
                raise ValueError('TRS通道锁定: ' + plug)
            for driver in cmds.listConnections(plug, source=True, destination=False) or []:
                kind = cmds.nodeType(driver)
                if not kind.startswith(('animCurve', 'animBlendNode')):
                    raise ValueError('外部驱动需先解除: ' + driver)
        if args['bake']:
            for target in [node] + (cmds.listRelatives(node, shapes=True, fullPath=True) or []):
                if cmds.referenceQuery(target, isNodeReferenced=True) or cmds.lockNode(target, query=True, lock=True)[0]:
                    raise ValueError('烘焙控制器shape引用/锁定: ' + target)
                for attr in cmds.listAttr(target, keyable=True) or []:
                    plug = target + '.' + attr
                    if cmds.getAttr(plug, lock=True):
                        raise ValueError('整对象烘焙通道锁定: ' + plug)
                    for driver in cmds.listConnections(plug, source=True, destination=False) or []:
                        if not cmds.nodeType(driver).startswith(('animCurve', 'animBlendNode')):
                            raise ValueError('整对象烘焙通道有外部驱动: ' + plug)
        controllers.append(node)
    ids = [proxy.identity(n) for n in controllers]
    if len(set(ids)) != len(ids):
        raise ValueError('控制器UUID重复')
    for _, data in proxy.records():
        if set(ids) & set(data['controllers']) and data['state'] in ('working', 'live', 'failed'):
            raise ValueError('重叠控制器已有未清理cycle: ' + data['record_uuid'])
    root = cmds.animLayer(query=True, root=True)
    if root and not cmds.animLayer(root, query=True, selected=True):
        raise ValueError('请先选中BaseAnimation层；预检不会切换层')
    start = cmds.playbackOptions(query=True, minTime=True) if args['start'] is None else args['start']
    end = cmds.playbackOptions(query=True, maxTime=True) if args['end'] is None else args['end']
    if start >= end or end - start > 100000:
        raise ValueError('范围需要start<end且不超过100000帧')
    args.update(controllers=controllers, start=start, end=end)
    return args


class DirectionalCycleTool(BaseMayaTool):
    tool_id = 'directional_cycle_tool_v1_1'
    tool_name = '方向循环动画'
    category = 'animation'
    version = '1.1-candidate.1'
    description = '完整原左/右/后退循环、骨盆层、脚部反转及校正/反旋转，独立owned资源与原Dockable UI。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读角色/范围/动画层/owned资源预检', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'open_ui':
            from .bridge import show_window
            show_window()
            return ToolResult.ok(data={'window': 'mtbDCTWindow'})
        from .runtime import execute
        data = execute(args)
        if data.get('errors'):
            result = ToolResult.fail(message='执行失败，请检查并Undo', errors=data['errors'], data=data)
            result.warnings = data['warnings']
            return result
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
