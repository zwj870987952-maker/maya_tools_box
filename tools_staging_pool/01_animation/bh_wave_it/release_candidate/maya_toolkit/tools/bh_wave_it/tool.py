import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, values, SCHEMA


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原窗口需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    given = args['objects'] or cmds.ls(selection=True, long=True) or []
    nodes = []
    for name in given:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('对象非唯一transform: ' + name)
        node = found[0]
        if node in nodes or cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
            raise ValueError('对象重复/引用/锁定: ' + name)
        nodes.append(node)
    if not nodes:
        raise ValueError('需要有序对象数组或选择')
    channels = ['rotate' + axis for axis in args['rotate_axes']]
    if args['action'] != 'base_offset':
        channels += ['translate' + axis for axis in args['translate_axes']] + args['custom_attributes']
    if not channels:
        raise ValueError('未指定写入通道')
    operations = []
    computed = [-args['base_offset']] if args['action'] == 'base_offset' else values(args, len(nodes))
    for node, value in zip(nodes, computed):
        for attr in dict.fromkeys(channels):
            plug = node + '.' + attr
            if not cmds.objExists(plug) or cmds.getAttr(plug, type=True) not in ('double', 'float', 'doubleAngle', 'doubleLinear', 'long', 'short', 'byte', 'bool', 'enum'):
                raise ValueError('需要现存标量数值属性: ' + plug)
            if cmds.getAttr(plug, lock=True) or not cmds.getAttr(plug, settable=True):
                raise ValueError('通道不可写: ' + plug)
            if any(not cmds.nodeType(source).startswith('animCurve') for source in (cmds.listConnections(plug, source=True, destination=False) or [])):
                raise ValueError('通道外部驱动: ' + plug)
            operations.append({'plug': plug, 'before': cmds.getAttr(plug), 'computed_value': value})
    args['objects'] = nodes
    args['operations'] = operations
    return args


class WaveItTool(BaseMayaTool):
    tool_id = 'bh_wave_it'
    tool_name = 'bh_waveIt 波浪造型'
    category = 'animation'
    version = '1.09-adapter'
    description = '按有序选择覆盖旋转/位移/自定义标量属性，原S/C预设和首对象base offset，完整原UI。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读通道/顺序预检通过，不加载MEL或修改选择', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from . import runtime
        return ToolResult.ok(data=runtime.execute(args), warnings=['覆盖属性值，不显式打键；动画/autoKey及整数属性强制转换需实际验收。'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
