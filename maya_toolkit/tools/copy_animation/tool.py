import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, pair_data, SCHEMA


def config_path(value, write=False, overwrite=False):
    path = Path(value)
    if not value or not path.is_absolute() or path.suffix.casefold() != '.json':
        raise ValueError('配置需要绝对.json路径')
    path = path.resolve()
    if path.exists() and not path.is_file():
        raise ValueError('配置路径不是文件')
    if write and path.exists() and not overwrite:
        raise ValueError('文件已有，覆盖需overwrite_file=True')
    if not write and not path.is_file():
        raise ValueError('配置文件不存在')
    return path


def parse_config(data):
    if not isinstance(data, list):
        raise ValueError('配置根需要数组')
    result = []
    for value in data:
        if not isinstance(value, dict) or not isinstance(value.get('text'), str) or ' , ' not in value['text']:
            raise ValueError('配置需要原text: 源对象 , 目标对象')
        source, target = [name.strip() for name in value['text'].split(' , ', 1)]
        result.append(pair_data({'source': source, 'target': target, 'modes': value.get('modes', {})}))
    return result


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    if args['action'] in ('save_config', 'load_config'):
        path = config_path(args['file_path'], args['action'] == 'save_config', args['overwrite_file'])
        args['file_path'] = str(path)
        if args['action'] == 'load_config':
            args['pairs'] = parse_config(json.loads(path.read_text(encoding='utf-8-sig')))
        return args
    from maya import cmds
    from . import scene
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('完整Qt列表需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    scene.group()
    for name in scene.SETS.values():
        if cmds.objExists(name) and (cmds.nodeType(name) != 'objectSet' or not scene.owned(name)):
            raise ValueError('固定集合被外部占用: ' + name)
    if args['action'] == 'cleanup' and not args['pairs']:
        selected_records = scene.records()
        for node, data in selected_records:
            scene.validate_record(data)
        args['record_ids'] = [scene.identity(node) for node, _ in selected_records]
        return args
    if not args['pairs']:
        raise ValueError('需要至少一组明确pair')
    resolved, targets, record_ids = [], set(), []
    for pair in args['pairs']:
        pair = dict(pair)
        source, target = scene.resolve(pair['source']), scene.resolve(pair['target'])
        if source == target or target in targets:
            raise ValueError('源目标相同或重复写入目标')
        targets.add(target)
        record_node, data = scene.get_record(source, target)
        if data:
            scene.validate_record(data)
            record_ids.append(scene.identity(record_node))
        if args['action'] != 'cleanup':
            if cmds.referenceQuery(target, isNodeReferenced=True) or cmds.lockNode(target, query=True, lock=True)[0]:
                raise ValueError('目标引用/锁定')
            if args['action'] == 'execute':
                for channel, mode in pair['modes'].items():
                    if mode == 'none':
                        continue
                    attributes = (cmds.listAttr(source, keyable=True, userDefined=True) or []) if channel == 'other' else [channel + axis for axis in 'XYZ']
                    for attribute in attributes:
                        plug = target + '.' + attribute
                        if not cmds.objExists(plug):
                            continue
                        if cmds.getAttr(plug, lock=True):
                            raise ValueError('写入通道锁定: ' + plug)
                        for driver in cmds.listConnections(plug, source=True, destination=False) or []:
                            if not cmds.nodeType(driver).startswith('animCurve') and not (data and scene.owned(driver, data['token'])):
                                raise ValueError('目标外部驱动: ' + driver)
        pair.update(source=source, target=target)
        resolved.append(pair)
    args['pairs'], args['record_ids'] = resolved, record_ids
    if args['action'] == 'execute':
        start = int(cmds.playbackOptions(query=True, minTime=True)) if args['start'] is None else args['start']
        end = int(cmds.playbackOptions(query=True, maxTime=True)) if args['end'] is None else args['end']
        if start > end or end - start > 100000:
            raise ValueError('范围反转或过大')
        args.update(start=start, end=end)
    return args


class CopyAnimationTool(BaseMayaTool):
    tool_id = 'copy_animation'
    tool_name = '动画复制与自动对齐'
    category = 'animation'
    version = 'revised-adapter-1.0'
    description = '原帧对齐/maintainOffset约束/逐帧数值/无操作四模式，完整Qt配置UI，owned持久pair UUID。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读pair/通道/helper/文件预检，不建节点/开UI/写文件', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'open_ui':
            from .native_ui import show_window
            show_window()
            return ToolResult.ok(data={'window': 'mtbCA_copyAnimationAutoAlignWindow'})
        from .runtime import execute
        data = execute(args)
        if data.get('errors'):
            result = ToolResult.fail(message='部分写入失败，请检查并Undo', data=data, errors=data['errors'])
            result.warnings = data.get('warnings', [])
            return result
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
