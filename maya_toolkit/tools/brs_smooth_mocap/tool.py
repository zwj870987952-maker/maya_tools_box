import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def curve_plan(curves, selected_only):
    from maya import cmds
    rows = []
    for name in dict.fromkeys(curves):
        found = cmds.ls(name, long=True) or []
        if len(found) != 1 or cmds.nodeType(found[0]) not in ('animCurveTA', 'animCurveTL', 'animCurveTU'):
            raise ValueError('需要唯一时间驱动数值animCurve，拒绝time warp/非时间曲线: ' + name)
        curve = found[0]
        if cmds.referenceQuery(curve, isNodeReferenced=True) or cmds.lockNode(curve, query=True, lock=True)[0]:
            raise ValueError('曲线引用或锁定: ' + curve)
        for plug in cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []:
            node = plug.split('.', 1)[0]
            if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0] or cmds.getAttr(plug, lock=True):
                raise ValueError('曲线下游引用或锁定: ' + plug)
        times = cmds.keyframe(curve, query=True, timeChange=True, selected=selected_only) or []
        rows.append({'curve': curve, 'times': sorted(set(times)), 'eligible': len(set(times)) >= 3})
    return rows


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('窗口需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    if args['action'] == 'smooth_keys':
        names = args['curves'] or cmds.keyframe(query=True, name=True, selected=True) or []
        args['curve_plan'] = curve_plan(names, args['selected_only'])
        if not any(row['eligible'] for row in args['curve_plan']):
            raise ValueError('需要至少三个所选/全范围时间键')
        return args
    from .backend import scene
    from .backend.tool import writable, TR
    selected = cmds.ls(selection=True, long=True) or []
    root = scene.resolve(args['root_joint'] or (selected[0] if selected else ''))
    if cmds.nodeType(root) != 'joint':
        raise ValueError('root_joint需要joint')
    joints = (cmds.listRelatives(root, allDescendents=True, fullPath=True, type='joint') or []) + [root]
    eligible, skipped = [], []
    for joint in joints:
        times = cmds.keyframe(joint, attribute=TR, query=True, timeChange=True) or []
        if len(set(times)) < 2:
            skipped.append(joint)
            continue
        writable(joint, TR)
        loc = scene.locator_for(joint)
        if loc:
            scene.safe_hierarchy(loc)
        eligible.append(joint)
    if not eligible:
        raise ValueError('层级没有至少两个TR时间键的可处理joint')
    args.update(root_joint=root, joints=eligible, skipped=skipped)
    return args


class SmoothMocapTool(BaseMayaTool):
    tool_id = 'brs_smooth_mocap'
    tool_name = 'BRS Smooth Mocap'
    category = 'animation'
    version = 'legacy-adapter-1.0'
    description = '原三点平均快照平滑、strength-1循环、locator约束回烘六TR；另提供所选关键帧平滑。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检通过，不选择键/加载旧入口/写场景', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'open_ui':
            from .ui import show
            return ToolResult.ok(data={'window': show()})
        from .runtime import execute
        data = execute(args)
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
