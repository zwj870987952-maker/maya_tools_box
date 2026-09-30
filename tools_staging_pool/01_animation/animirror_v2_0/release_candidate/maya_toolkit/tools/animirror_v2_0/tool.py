"""Read-only preflight and ToolResult adapter for the complete original MEL suite."""
import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import SCHEMA, normalize
from . import state

PACKAGE = Path(__file__).resolve().parent


def resolve(name):
    cmds = state.maya()
    nodes = cmds.ls(name, long=True) or []
    if len(nodes) != 1 or not cmds.objectType(nodes[0], isAType='transform'):
        raise ValueError('对象缺失、重名或不是 transform: ' + name)
    return nodes[0]


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    cmds = state.maya()
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('打开窗口需要真实 Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启 Maya Undo')
    all_records = state.records()
    for record in all_records:
        state.owned_nodes(record)
    if args['action'] in ('clear', 'bake', 'mirror_bake'):
        state.safe_to_clear(all_records)
    if args['action'] == 'clear':
        args['record_count'] = len(all_records)
        return args
    if any(record['data']['failed'] for record in all_records):
        raise ValueError('已有失败镜像的部分辅助节点，请先 Undo 或 clear')
    if 'floatMath' not in cmds.allNodeTypes():
        raise ValueError('floatMath 不可用；请先在副本显式加载 Autodesk lookdevKit 插件，预检不会自动加载')
    if args['action'] in ('mirror', 'mirror_bake'):
        names = args['objects'] or cmds.ls(selection=True, long=True) or []
        if len(names) != 3:
            raise ValueError('请选择恰好三个 transform，顺序为中心、参考、目标')
        args['objects'] = [resolve(name) for name in names]
        if len(set(args['objects'])) != 3:
            raise ValueError('中心、参考、目标必须不同')
        center, source, target = args['objects']
        if center.startswith(target + '|') or source.startswith(target + '|') or target.startswith(source + '|'):
            raise ValueError('此祖先/后代关系可能产生循环，先在独立副本调整层级')
        if cmds.referenceQuery(target, isNodeReferenced=True):
            raise ValueError('目标为引用节点；请先准备非引用副本')
        if any(record['data']['inputs'][2] == state.identity(target) for record in all_records):
            raise ValueError('目标已有候选镜像，请先 bake、clear 或 Undo')
        for channel, enabled in (('translate', args['translations']), ('rotate', args['rotations'])):
            if not enabled:
                continue
            for axis in 'XYZ':
                plug = target + '.' + channel + axis
                if cmds.getAttr(plug, lock=True) or (cmds.listConnections(plug, source=True, destination=False) or []):
                    raise ValueError('目标通道锁定或已被驱动（包括现有动画曲线）: ' + plug)
    else:
        if not all_records:
            raise ValueError('没有累计镜像目标可烘焙')
        for record in all_records:
            target = state.find(record['data']['inputs'][2], required=True)
            if cmds.referenceQuery(target, isNodeReferenced=True):
                raise ValueError('镜像目标已变为引用节点')
    if args['start'] is None:
        start, end = cmds.playbackOptions(query=True, min=True), cmds.playbackOptions(query=True, max=True)
        if not cmds.about(batch=True):
            import maya.mel as mel
            slider = mel.eval('$mtbAV2_sliderQuery = $gPlayBackSlider;')
            selected = cmds.timeControl(slider, query=True, rangeArray=True)
            if selected[1] - selected[0] > 1:
                # Original range treats timeControl's returned upper bound as inclusive.
                start, end = selected
        args['start'], args['end'] = start, end
    args['record_count'] = len(all_records)
    return args


class AnimirrorV2Tool(BaseMayaTool):
    tool_id = 'animirror_v2_0'
    tool_name = 'AniMirror 动画镜像'
    category = 'animation'
    version = '2.0.1-adapter'
    description = '原 joint/floatMath 实时动画镜像、累计目标烘焙和安全清理；保留完整原窗口。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            args = plan(**kwargs)
            return ToolResult.ok(message='只读预检通过，不 source、不建辅助节点、不加载插件、不改 UI/选择/时间。', data=args, dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8')))
        from . import runtime
        data = runtime.open_ui() if args['action'] == 'open_ui' else runtime.execute(args)
        return ToolResult.ok(message='AniMirror 操作完成', data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui()
