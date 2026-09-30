import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, CHANNELS, SCHEMA
from . import files


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    if args['action'] in ('save_preset', 'load_preset'):
        args['file_path'] = str(files.path(args['file_path'], '.cgsk', args['action'] == 'save_preset', args['overwrite_file']))
        if args['action'] == 'load_preset':
            args['preset'] = files.load_preset(args['file_path'])
        return args
    from maya import cmds
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('Qt窗口/原生渐变需要真实Maya GUI')
        return args
    selected = cmds.ls(selection=True, long=True) or []
    name = args['object'] or (selected[0] if selected else '')
    found = cmds.ls(name, long=True) or []
    if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('需要唯一transform，实际仅第一个对象')
    node = found[0]
    args['object'] = node
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
        raise ValueError('目标引用/锁定')
    if args['action'] == 'cache':
        if not files.plugin_loaded():
            raise ValueError('请在Plugin Manager手动加载animImportExport')
        if cmds.attributeQuery(files.ATTR, node=node, exists=True):
            record = json.loads(cmds.getAttr(node + '.' + files.ATTR))
            if record.get('owner') != files.OWNER or record.get('uuid') != cmds.ls(node, uuid=True)[0] or cmds.getAttr(node + '.' + files.ATTR, lock=True):
                raise ValueError('cache属性非本候选可写记录')
        target = args['file_path'] or str(files.default_data_root() / 'cache' / (cmds.ls(node, uuid=True)[0] + '.anim'))
        args['file_path'] = str(files.path(target, '.anim', write=True, overwrite=args['overwrite_file']))
        if Path(args['file_path'] + '.json').exists() and not args['overwrite_file']:
            raise ValueError('cache sidecar已存在，覆盖需显式允许')
        return args
    for attr in CHANNELS:
        plug = node + '.' + attr
        if cmds.getAttr(plug, lock=True):
            raise ValueError('六TR中有锁定通道: ' + plug)
        for source in cmds.listConnections(plug, source=True, destination=False) or []:
            kind = cmds.nodeType(source)
            if not kind.startswith(('animCurve', 'animBlend')):
                raise ValueError('通道外部驱动: ' + source)
    if args['action'] in ('restore', 'clear') or args['overwrite'] or args['use_cache']:
        for plug in cmds.listAnimatable(node) or []:
            if cmds.keyframe(plug, query=True, keyframeCount=True) and cmds.getAttr(plug, lock=True):
                raise ValueError('清键会影响锁定属性: ' + plug)
    if args['action'] == 'clear' and not args['overwrite']:
        raise ValueError('clear需要overwrite=True显式确认全对象清键')
    if args['action'] == 'restore' or args['use_cache']:
        if not files.plugin_loaded():
            raise ValueError('请手动加载animImportExport再restore')
        args['cache_record'] = files.cache_record(node, args['file_path'])
    if args['action'] == 'apply':
        start = cmds.playbackOptions(query=True, minTime=True) if args['start'] is None else args['start']
        end = cmds.playbackOptions(query=True, maxTime=True) if args['end'] is None else args['end']
        if start > end:
            raise ValueError('start不能大于end')
        frames = list(range(int(start), int(end + 1.0), args['step']))
        if not frames or len(frames) > 100000:
            raise ValueError('采样范围为空或过大')
        if len(args['falloff_samples']) != len(frames):
            raise ValueError('apply需要每个整数采样帧一个falloff_samples；GUI使用原生渐变求值')
        if not any(args['amounts'].values()):
            raise ValueError('全amount为0时原空at会给额外属性打键，候选拒绝')
        args.update(start=start, end=end, frames=frames, normalization_denominator=end + 1.0 - start)
    return args


class CgShakeTool(BaseMayaTool):
    tool_id = 'cg_shake_py3'
    tool_name = 'CgShake 1.5'
    category = 'animation'
    version = '1.5-adapter'
    description = '原首选对象正向uniform随机扰动、原生渐变/完整UI、动画cache恢复和cgsk预设；外部文件显式保护。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读预检，不建UI/加载插件/建目录/写键文件', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'open_ui':
            from .bridge import show
            return ToolResult.ok(data=show())
        from .runtime import execute
        data = execute(args)
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
