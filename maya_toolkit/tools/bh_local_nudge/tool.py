import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    import maya.cmds as cmds
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原窗口需要真实 Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    nodes = args['objects'] or cmds.ls(selection=True, long=True) or []
    if not nodes:
        raise ValueError('请选择或提供 transform')
    plans = []
    for node in nodes:
        found = cmds.ls(node, long=True) or []
        if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('对象缺失、重名或非 transform: ' + node)
        node = found[0]
        plug = node + '.' + args['channel'] + args['axis']
        if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0] or cmds.getAttr(plug, lock=True):
            raise ValueError('对象引用/节点或通道锁定: ' + plug)
        drivers = cmds.listConnections(plug, source=True, destination=False) or []
        if any(not cmds.nodeType(driver).startswith('animCurve') for driver in drivers):
            raise ValueError('已有外部驱动/动画层/约束: ' + plug)
        before = cmds.getAttr(plug)
        if not math.isfinite(before + args['delta']):
            raise ValueError('结果超出有限数值')
        plans.append({'node': node, 'plug': plug, 'before': before, 'after': before + args['delta'], 'animated': bool(drivers)})
    if len({item['node'] for item in plans}) != len(plans):
        raise ValueError('对象不得重复')
    args['objects'] = [item['node'] for item in plans]
    args['changes'] = plans
    return args


class LocalNudgeTool(BaseMayaTool):
    tool_id = 'bh_local_nudge'
    tool_name = 'bh_localNudge 局部属性微调'
    category = 'animation'
    version = '1.03.1-adapter'
    description = '原局部平移/旋转属性加减；CTRL半值、ALT四分之一，完整原生界面。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过，不 source/改值/开窗', data=plan(**kwargs), dry_run=True)
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
            mel.eval('mtbLN_bh_localNudge();')
            return ToolResult.ok(data=dict(data, window='mtbLN_localNudgeUI'))
        runtime.execute(args)
        import maya.cmds as cmds
        for item in args['changes']:
            item['expected_after'] = item['after']
            item['after'] = cmds.getAttr(item['plug'])
        warnings = ['原流程不显式打键；已有动画和autoKey状态的实际持续效果需检查。'] if any(item['animated'] for item in args['changes']) else []
        return ToolResult.ok(message='局部属性微调完成', data={'changes': args['changes'], 'delta': args['delta']}, warnings=warnings)

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
