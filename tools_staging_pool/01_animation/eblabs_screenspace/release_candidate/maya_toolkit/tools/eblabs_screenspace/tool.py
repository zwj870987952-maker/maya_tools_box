import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def resolve(name):
    from maya import cmds
    values = cmds.ls(name, long=True) or []
    if len(values) != 1 or not cmds.objectType(values[0], isAType='transform'):
        raise ValueError('需要唯一transform: ' + name)
    return values[0]


def channels(node, orientation, own_tokens=()):
    from maya import cmds
    from . import scene
    for attr in ['translate' + axis for axis in 'XYZ'] + (['rotate' + axis for axis in 'XYZ'] if orientation else []):
        plug = node + '.' + attr
        if cmds.getAttr(plug, lock=True) or not cmds.getAttr(plug, keyable=True):
            raise ValueError('目标TR需可打键且无锁: ' + plug)
        for source in cmds.listConnections(plug, source=True, destination=False) or []:
            if not cmds.nodeType(source).startswith('animCurve') and not any(scene.owned(source, token) for token in own_tokens):
                raise ValueError('目标有外部驱动: ' + source)


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    from . import scene, runtime
    if runtime._ACTIVE:
        raise ValueError('已有ScreenSpace运行中')
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('原MEL窗口需要真实GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    records = {scene.identity(n): (n, data) for n, data in scene.records()}
    if args['action'] != 'create':
        if not args['record_ids'] or any(uid not in records for uid in args['record_ids']):
            raise ValueError('需要明确owned record UUID数组')
        for uid in args['record_ids']:
            data = records[uid][1]
            scene.validate(data)
            if args['action'] != 'cleanup':
                control = scene.find(data['control_uuid'])
                if data['state'] != 'live' or not control:
                    raise ValueError('需要live rig')
                orientation = cmds.objExists(control + '.useOrientation') and cmds.getAttr(control + '.useOrientation')
                channels(scene.find(data['target_uuid']), orientation, [data['token']])
                keys = cmds.keyframe(control, query=True, timeChange=True) or []
                if not keys or max(keys) - min(keys) > 100000:
                    raise ValueError('控制器没有键或跨度过大')
                if not any(cmds.keyframe(control, attribute='translate' + axis, query=True, keyframeCount=True) for axis in 'XYZ'):
                    raise ValueError('原smart bake需要至少一个translate键')
                if orientation and not any(cmds.keyframe(control, attribute='rotate' + axis, query=True, keyframeCount=True) for axis in 'XYZ'):
                    raise ValueError('orientation需要控制器旋转键')
        return args
    if not args['camera']:
        raise ValueError('create需要明确camera')
    given = cmds.ls(args['camera'], long=True) or []
    if len(given) == 1 and cmds.nodeType(given[0]) == 'camera':
        given = cmds.listRelatives(given[0], parent=True, fullPath=True) or []
    if len(given) != 1:
        raise ValueError('camera不唯一')
    camera = resolve(given[0])
    shapes = cmds.listRelatives(camera, shapes=True, fullPath=True, type='camera') or []
    if len(shapes) != 1 or cmds.getAttr(shapes[0] + '.orthographic') or cmds.getAttr(shapes[0] + '.nearClipPlane') <= 0:
        raise ValueError('需要一个perspective camera shape，nearClipPlane>0')
    if len(cmds.ls(shapes[0], allPaths=True)) != 1:
        raise ValueError('实例camera不支持')
    objects = []
    for name in args['objects'] or cmds.ls(selection=True, long=True) or []:
        node = resolve(name)
        if node == camera:
            continue
        if scene.owned(node):
            raise ValueError('不接管owned screen控制器')
        scene.writable(node)
        channels(node, args['include_orientation'])
        if any(data['target_uuid'] == scene.identity(node) and data['state'] in ('live', 'working', 'failed') for _, data in records.values()):
            raise ValueError('目标已有未清理rig')
        keys = sorted(set(time for axis in 'XYZ' for time in (cmds.keyframe(node, attribute='translate' + axis, query=True, timeChange=True) or [])))
        if not keys or not all(math.isfinite(time) for time in keys) or max(keys) - min(keys) > 100000:
            raise ValueError('需要至少一个translation键且范围不过大')
        if node in objects or len(cmds.ls(node, allPaths=True)) != 1:
            raise ValueError('目标重复/实例')
        objects.append(node)
    if not objects:
        raise ValueError('需要动画目标对象')
    args.update(camera=camera, objects=objects)
    return args


class ScreenSpaceTool(BaseMayaTool):
    tool_id = 'eblabs_screenspace'
    tool_name = 'EB Labs 屏幕空间动画'
    category = 'animation'
    version = 'native-1.0.5-candidate.1'
    description = '完整原MEL投影/aim/depth/orientation rig与Smart/Full Bake及原UI，owned UUID映射和清理。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读camera/动画/TR/owned rig预检，不source或写buffer/clipboard', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from .runtime import execute
        data = execute(args)
        if data.get('errors'):
            result = ToolResult.fail(message='部分创建失败，请检查并Undo', data=data, errors=data['errors'])
            result.warnings = data['warnings']
            return result
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
