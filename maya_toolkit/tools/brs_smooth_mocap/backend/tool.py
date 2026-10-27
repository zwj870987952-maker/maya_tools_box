import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA

TR = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']


def writable(node, attrs):
    from maya import cmds
    from . import scene
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
        raise ValueError('目标引用或锁定: ' + node)
    for attr in attrs:
        plug = node + '.' + attr
        if cmds.getAttr(plug, lock=True):
            raise ValueError('目标通道锁定: ' + plug)
        for source in cmds.listConnections(plug, source=True, destination=False) or []:
            if not cmds.nodeType(source).startswith('animCurve') and not scene.owned(source):
                raise ValueError('目标外部驱动: ' + source)
    for con in cmds.listRelatives(node, type='constraint', fullPath=True) or []:
        if not scene.owned(con, 'constraint'):
            raise ValueError('目标外部约束: ' + con)


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    from . import scene
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原生窗口需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    scene.group()
    if args['action'] in ('create_guide', 'redirect'):
        if not scene.group():
            raise ValueError('没有本候选group')
        scene.guide()
        nodes = scene.locators()
        if not nodes:
            raise ValueError('group没有本候选locator')
        for node in nodes:
            scene.safe_hierarchy(node)
        if args['action'] == 'redirect':
            if not scene.guide():
                raise ValueError('先创建/调整guide')
            scene.safe_hierarchy(scene.guide())
            for node in nodes:
                writable(node, TR)
                keys = cmds.keyframe(node, attribute=TR, query=True, timeChange=True) or []
                if len(set(keys)) < 2:
                    raise ValueError('重定向locator需要两个以上时间键')
        args['objects'] = nodes
        return args
    names = args['objects'] or cmds.ls(selection=True, long=True) or []
    nodes = [scene.resolve(n) for n in names]
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError('需要明确不重复对象')
    eligibility = []
    for node in nodes:
        existing = scene.locator_for(node)
        if existing:
            scene.safe_hierarchy(existing)
        if args['action'] == 'apply':
            loc = scene.locator_for(node, required=True)
            keys = cmds.keyframe(loc, attribute=TR, query=True, timeChange=True) or []
            if len(set(keys)) < 2:
                raise ValueError('定位器时间键不足')
            # Original cutKey/keepKeyframe/snapKey affect all target keyed channels.
            writable(node, TR)
            extra_keys = set(cmds.listAnimatable(node) or []) - {node + '.' + attr for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']}
            for plug in extra_keys:
                if cmds.keyframe(plug, query=True, keyframeCount=True):
                    raise ValueError('原全通道round/cut/snap会影响额外动画属性，请用仅六TR通道副本: ' + plug)
        else:
            keys = cmds.keyframe(node, attribute=TR, query=True, timeChange=True) or []
            eligibility.append({'object': node, 'eligible': len(set(keys)) > 1})
            if args['constrain']:
                writable(node, (TR[:3] if args['translate'] else []) + (TR[3:] if args['rotate'] else []))
    args['objects'] = nodes
    args['eligibility'] = eligibility
    return args


class LocatorTransferTool(BaseMayaTool):
    tool_id = 'brs_loc_transfer'
    tool_name = 'BRS Locator Transfer'
    category = 'animation'
    version = '1.09-adapter'
    description = '原动画locator创建/回写/guide重定向、逐帧bake和稀疏键/breakdown；owned UUID和标准API。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过，不导入原入口/开窗/写场景', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from . import runtime
        data = runtime.execute(args)
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
