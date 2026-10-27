import re
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'match_ik_to_fk', 'match_fk_to_ik', 'bake_ik_to_fk', 'bake_fk_to_ik', 'spline_ik_to_fk', 'spline_fk_to_ik', 'open_ui']
DEFAULTS = {'action': 'inspect', 'control': '', 'start': None, 'end': None, 'allow_reference_edits': False}
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {'action': {'type': 'string', 'enum': ACTIONS, 'default': 'inspect'}, 'control': {'type': 'string', 'default': '', 'description': '明确CTRL_*_Hand/Foot或CTRL_*_Pinner；空读取唯一选择'}, 'start': {'type': ['integer', 'null']}, 'end': {'type': ['integer', 'null']}, 'allow_reference_edits': {'type': 'boolean', 'default': False}}}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or not isinstance(args['control'], str) or args['control'] and not re.fullmatch(r'[A-Za-z_][\w:]*', args['control'], re.ASCII) or type(args['allow_reference_edits']) is not bool:
        raise ValueError('action/control/bool无效；需要安全短名而非DAG路径/组件')
    for name in ('start', 'end'):
        if args[name] is not None and type(args[name]) is not int:
            raise ValueError(name + '须整数/null')
    if args['start'] is not None and args['end'] is not None and args['start'] > args['end']:
        raise ValueError('范围反转')
    return args


def plan(**kwargs):
    args = normalize(**kwargs)
    from maya import cmds as c
    from . import runtime as r
    if r._ACTIVE:
        raise ValueError('已有KF运行')
    if args['action'] == 'open_ui':
        if c.about(batch=True):
            raise ValueError('真实Maya GUI需要')
        return args
    chosen = [args['control']] if args['control'] else c.ls(selection=True) or []
    if len(chosen) != 1 or not re.fullmatch(r'[A-Za-z_][\w:]*', chosen[0], re.ASCII):
        raise ValueError('唯一明确短名控制器需要')
    node = chosen[0]
    if len(c.ls(node, long=True) or []) != 1 or c.nodeType(node) != 'transform' or len(c.ls(node, allPaths=True, long=True) or []) != 1:
        raise ValueError('唯一非实例transform需要')
    match = re.fullmatch(r'(?P<ns>[\w:]+):CTRL_(?P<side>.+)_(?P<limb>Hand|Foot|Pinner)', node, re.ASCII)
    if not match:
        raise ValueError('需要命名空间CTRL_*_Hand/Foot/Pinner')
    ns, side, limb = match['ns'], match['side'], match['limb']
    if not re.fullmatch(r'[A-Za-z_][\w:]*', ns, re.ASCII) or not re.fullmatch(r'[A-Za-z_][\w]*', side, re.ASCII):
        raise ValueError('命名空间/side无效')
    args.update(control=node, _namespace=ns, _limb=limb, _side=side)
    if args['action'] == 'inspect':
        return args
    if not args['allow_reference_edits']:
        raise ValueError('该工具专用于引用rig；明确allow_reference_edits=True后才可写')
    if not c.referenceQuery(node, isNodeReferenced=True) or not c.undoInfo(query=True, state=True) or c.play(query=True, state=True):
        raise ValueError('需要已引用rig、Undo开启、停止播放')
    if c.currentUnit(query=True, angle=True) != 'deg' or c.currentUnit(query=True, linear=True) != 'cm':
        raise ValueError('当前候选degree/cm')
    start = int(c.playbackOptions(query=True, minTime=True)) if args['start'] is None else args['start']
    end = int(c.playbackOptions(query=True, maxTime=True)) if args['end'] is None else args['end']
    if start > end or end - start > 10000:
        raise ValueError('范围反转/大于10001帧')
    args.update(start=start, end=end)
    destinations, reads = r.dependencies(args)
    reference = c.referenceQuery(node, referenceNode=True)
    for name in set(reads) | set(destinations):
        if len(c.ls(name, long=True) or []) != 1 or not c.referenceQuery(name, isNodeReferenced=True) or c.referenceQuery(name, referenceNode=True) != reference:
            raise ValueError('KF原rig依赖缺失/不同引用: ' + name)
    for name, attrs in destinations.items():
        if c.lockNode(name, query=True, lock=True)[0]:
            raise ValueError('目标对象锁: ' + name)
        for attr in attrs:
            plug = name + '.' + attr
            if not c.objExists(plug) or c.getAttr(plug, lock=True):
                raise ValueError('目标属性缺失/锁: ' + plug)
            for driver in c.listConnections(plug, source=True, destination=False) or []:
                if not c.nodeType(driver).startswith('animCurve'):
                    raise ValueError('目标外部驱动/层/约束: ' + plug)
                if c.referenceQuery(driver, isNodeReferenced=True) or c.lockNode(driver, query=True, lock=True)[0] or any(out != name for out in c.listConnections(driver + '.output', source=False, destination=True) or []):
                    raise ValueError('目标曲线引用/锁/共享: ' + plug)
    args.update(_destinations=destinations, _reads=reads)
    return args


class KFAnimRigTool(BaseMayaTool):
    tool_id = 'kf_animrig_ikfk'
    tool_name = 'KF Auto Rig IK/FK匹配 3.02'
    category = 'animation'
    version = '3.02-candidate.1'
    description = '完整原MEL手臂/普通腿/狗腿/高级样条匹配与UI，明确引用编辑、标准Undo、范围烘焙与助手保护。不会自动切pinner。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data={k: v for k, v in plan(**kwargs).items() if not k.startswith('_')}, dry_run=True, message='只读KF命名/原rig依赖/目标属性预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(plan(**kwargs)), warnings=['原rig匹配不自动切换IKFK/pinner；引用编辑与生产rig验收待完成'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
