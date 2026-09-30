import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA
from . import scene

DRAW_ACTIONS = {'start_draw', 'draw_depth', 'reset_depth'}


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    cmds = scene.maya()
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原窗口需要真实 Maya GUI')
        if scene.plane():
            raise ValueError('请先结束绘画，再重开窗口')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    if args['action'] in DRAW_ACTIONS:
        if cmds.about(batch=True) or not cmds.window('mtbSL_bh_speedLinesUI', exists=True):
            raise ValueError('交互绘画需要已打开候选原窗口及真实 Maya GUI')
        if args['action'] == 'start_draw' and scene.plane():
            raise ValueError('已有绘画平面，请先 stop_draw')
        if args['action'] != 'start_draw' and not scene.plane():
            raise ValueError('没有本候选绘画平面')
        if args['action'] != 'start_draw' and scene.plane().rsplit('|', 1)[-1] != scene.PLANE:
            raise ValueError('绘画平面已重命名；请先stop_draw再重建，不按旧名改别的对象')
    if args['action'] in DRAW_ACTIONS | {'geometry'}:
        args['camera'] = scene.resolve(args['camera'])
        if cmds.nodeType(scene.shape(args['camera'])) != 'camera':
            raise ValueError('camera不是相机transform')
    if args['action'] == 'stop_draw':
        from .runtime import owned_draw_plane
        owned_draw_plane()
        return args
    if args['action'] in DRAW_ACTIONS:
        return args
    nodes = [scene.resolve(node) for node in (args['objects'] or cmds.ls(selection=True, long=True) or [])]
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError('需要明确且不重复的选择')
    if args['action'] == 'geometry' and len(nodes) != 2:
        raise ValueError('geometry恰需两条曲线')
    for node in nodes:
        if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
            raise ValueError('对象引用或锁定: ' + node)
        kind = cmds.nodeType(scene.shape(node)) if args['action'] != 'key_visibility' else None
        if args['action'] in ('geometry', 'smooth') and kind != 'nurbsCurve':
            raise ValueError('需要nurbsCurve')
        if args['action'] == 'flip' and kind != 'mesh':
            raise ValueError('flip需要mesh')
        if args['action'] == 'simplify' and kind not in ('mesh', 'nurbsCurve'):
            raise ValueError('simplify只支持mesh/curve')
        if args['action'] == 'simplify' and kind == 'nurbsCurve' and cmds.getAttr(scene.shape(node) + '.spans') < 2:
            raise ValueError('曲线spans太少，原折半重建不能生成有效span')
        if args['action'] == 'key_visibility':
            plug = node + '.visibility'
            if cmds.getAttr(plug, lock=True) or any(not cmds.nodeType(source).startswith('animCurve') for source in (cmds.listConnections(plug, source=True, destination=False) or [])):
                raise ValueError('visibility锁定或被外部驱动')
        if args['action'] == 'geometry' and args['consume_curves']:
            children = cmds.listRelatives(node, children=True, fullPath=True) or []
            if any(not cmds.objectType(child, isAType='shape') for child in children):
                raise ValueError('输入曲线下有其他子对象，拒绝一起删除')
            for item in [node] + children:
                consumers = cmds.listConnections(item, source=False, destination=True) or []
                if any(cmds.nodeType(consumer) not in ('shadingEngine', 'objectSet', 'displayLayer') for consumer in consumers):
                    raise ValueError('输入曲线有输出消费连接；consume_curves=False或使用独立副本')
    if args['action'] == 'geometry' and args['on_layer'] and cmds.objExists(scene.LAYER):
        if cmds.nodeType(scene.LAYER) != 'displayLayer' or not scene.owned(scene.LAYER):
            raise ValueError('候选display layer名称被外部对象占用，不改其成员')
    args['objects'] = nodes
    return args


class SpeedLinesTool(BaseMayaTool):
    tool_id = 'bh_speedlines'
    tool_name = 'bh_speedLines 速度线'
    category = 'animation'
    version = '1.02.1-adapter'
    description = '原两曲线生成速度线、简化/平滑/翻法线/可见性键和完整GUI交互绘画；owned live-plane/job。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过，不source或改转换偏好/绘画状态', data=plan(**kwargs), dry_run=True)
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
            # Original root also changed prefs; opening now only creates the UI.
            mel.eval('mtbSL_bh_speedLinesUI();')
            return ToolResult.ok(data=dict(data, window='mtbSL_bh_speedLinesUI'))
        data = runtime.execute(args)
        return ToolResult.ok(message='速度线操作完成', data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
