import json
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def file_path(value, write=False, overwrite=False):
    path = Path(value)
    if not value or not path.is_absolute() or path.suffix.casefold() != '.json':
        raise ValueError('偏好需要绝对.json路径')
    path = path.resolve()
    if path.exists() and not path.is_file():
        raise ValueError('偏好路径不是文件')
    if write and path.exists() and not overwrite:
        raise ValueError('覆盖已有文件需overwrite_file=True')
    if not write and not path.is_file():
        raise ValueError('偏好文件不存在')
    return str(path)


def scope(objects, attributes, allow_driven=False):
    from maya import cmds
    nodes, curves = [], set()
    for name in objects:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('需要唯一transform/joint: ' + name)
        node = found[0]
        if cmds.referenceQuery(node, isNodeReferenced=True) or cmds.lockNode(node, query=True, lock=True)[0]:
            raise ValueError('对象引用/锁定: ' + node)
        if node in nodes:
            raise ValueError('对象UUID重复')
        nodes.append(node)
        attrs = attributes or cmds.listAttr(node, keyable=True, scalar=True, unlocked=True) or []
        for attr in attrs:
            plug = node + '.' + attr
            if not cmds.objExists(plug) or cmds.getAttr(plug, lock=True):
                raise ValueError('通道缺失/锁定: ' + plug)
            for source in cmds.listConnections(plug, source=True, destination=False) or []:
                kind = cmds.nodeType(source)
                if not allow_driven and not kind.startswith(('animCurve', 'animBlendNode', 'pairBlend')):
                    raise ValueError('外部驱动: ' + source)
        targets = [node] + (cmds.listRelatives(node, shapes=True, fullPath=True) or [])
        for target in targets:
            if cmds.referenceQuery(target, isNodeReferenced=True) or cmds.lockNode(target, query=True, lock=True)[0]:
                raise ValueError('shape引用/锁定')
            curves.update(cmds.ls(cmds.listHistory(target, pruneDagObjects=True) or [], type='animCurve') or [])
    # Traverse curve outputs: a shared curve may not alter external controls.
    allowed = {cmds.ls(n, uuid=True)[0] for n in nodes}
    allowed.update(cmds.ls(shape, uuid=True)[0] for n in nodes for shape in cmds.listRelatives(n, shapes=True, fullPath=True) or [])
    for curve in curves:
        if cmds.referenceQuery(curve, isNodeReferenced=True) or cmds.lockNode(curve, query=True, lock=True)[0]:
            raise ValueError('动画曲线引用/锁定')
        todo, visited = [curve], set()
        while todo:
            driver = todo.pop()
            uid = cmds.ls(driver, uuid=True)[0]
            if uid in visited:
                continue
            visited.add(uid)
            for target in cmds.listConnections(driver, source=False, destination=True) or []:
                tid = cmds.ls(target, uuid=True)[0]
                if tid in allowed:
                    continue
                kind = cmds.nodeType(target)
                if kind.startswith(('animBlendNode', 'pairBlend', 'unitConversion')):
                    todo.append(target)
                elif kind == 'animLayer':
                    continue
                else:
                    raise ValueError('动画曲线有外部使用者: ' + target)
    return nodes, list(curves)


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    if args['action'] in ('import_preferences', 'export_preferences'):
        args['file_path'] = file_path(args['file_path'], args['action'] == 'export_preferences', args['overwrite_file'])
        if args['action'] == 'import_preferences':
            value = json.loads(Path(args['file_path']).read_text(encoding='utf-8-sig'))
            if not isinstance(value, dict):
                raise ValueError('偏好根须object')
        return args
    from maya import cmds
    from . import runtime
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('完整原UI需要真实Maya GUI')
        return args
    if runtime._ACTIVE:
        raise ValueError('已有Whiskey运行中')
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Undo')
    if args['action'] == 'native_callback':
        item = runtime._CALLBACKS.get(args['callback_ticket'])
        if not item:
            raise ValueError('无有效原UI回调ticket')
        target, positional, keyword = item[1:]
        objects = keyword.get('objects') or keyword.get('selection') or (target.getSelected() if hasattr(target, 'getSelected') else None) or cmds.ls(selection=True, long=True) or []
    else:
        objects = args['objects'] or cmds.ls(selection=True, long=True) or []
    if not objects and args['action'] != 'set_tangent':
        # Some UI slider release callbacks are state-only when selection is empty.
        if args['action'] != 'native_callback':
            raise ValueError('需要明确选择对象')
    allow_driven = args['action'] == 'smash_bake' or (args['action'] == 'native_callback' and item[0].__name__ == 'smashBaker')
    args['objects'], args['curves'] = scope(objects, args['attributes'], allow_driven)
    if args['objects'] and args['attributes']:
        args['attributes'] = [cmds.attributeQuery(a, node=args['objects'][0], shortName=True) for a in args['attributes']]
    if args['action'] == 'slider' and args['slider_kind'] == 'inOut':
        matches = cmds.ls(args['camera'], long=True) if args['camera'] else []
        if len(matches) != 1:
            raise ValueError('inOut API需要唯一camera')
        camera = matches[0]
        if cmds.nodeType(camera) == 'camera':
            camera = (cmds.listRelatives(camera, parent=True, fullPath=True) or [None])[0]
        if not camera or not cmds.listRelatives(camera, shapes=True, type='camera'):
            raise ValueError('inOut参数不是相机')
        args['camera'] = camera
    if args['action'] == 'smash_bake':
        start = int(cmds.playbackOptions(query=True, animationStartTime=True)) if args['start'] is None else args['start']
        end = int(cmds.playbackOptions(query=True, animationEndTime=True)) if args['end'] is None else args['end']
        if start > end or end - start > 100000:
            raise ValueError('Smash范围反转/过大')
        args.update(start=start, end=end)
    if args['slider_kind'] == 'snapshot' and args['action'] == 'slider' and not args['snapshot_data']:
        raise ValueError('snapshot slider需要capture_snapshot结果')
    return args


class WhiskeyTool(BaseMayaTool):
    tool_id = 'eblabs_whiskey'
    tool_name = 'EB Labs Whiskey Pro完整套件'
    category = 'animation'
    version = '1.5.4-source-candidate.1'
    description = '原22类/272方法与完整widget/slider/曲线清理套件，标准API/原UI回调、Undo/作用域和显式偏好JSON。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读对象/曲线共享/文件预检，不导入原UI或写场景', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from .runtime import execute
        data = execute(args)
        if data.get('errors'):
            result = ToolResult.fail(message='原算法/写入发生失败，请检查并Undo', data=data, errors=data['errors'])
            result.warnings = data.get('warnings', [])
            return result
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
