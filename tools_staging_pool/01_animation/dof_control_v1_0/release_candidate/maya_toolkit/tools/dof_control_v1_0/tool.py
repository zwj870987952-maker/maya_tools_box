import json
import math
from pathlib import Path
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import normalize, SCHEMA


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    from . import scene, runtime
    if runtime._ACTIVE:
        raise ValueError('已有DOF回合运行中')
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('UI需要真实Maya GUI')
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Maya Undo')
    records = {scene.identity(n): (n, data) for n, data in scene.records()}
    if args['action'] in ('cleanup', 'set_template'):
        if not args['record_ids'] or any(uid not in records for uid in args['record_ids']):
            raise ValueError('需要明确本工具record UUID数组')
        for uid in args['record_ids']:
            data = records[uid][1]
            scene.validate(data)
            if args['action'] == 'set_template' and (not data['cube_uuid'] or not scene.find(data['cube_uuid'])):
                raise ValueError('cube缺失')
            if args['action'] == 'set_template':
                for shape in cmds.listRelatives(scene.find(data['cube_uuid']), shapes=True, fullPath=True) or []:
                    if cmds.getAttr(shape + '.template', lock=True) or not cmds.getAttr(shape + '.template', settable=True):
                        raise ValueError('模板属性不可写: ' + shape)
        return args
    given = args['cameras'] or cmds.ls(selection=True, long=True) or []
    cameras = []
    for name in given:
        found = cmds.ls(name, long=True) or []
        if len(found) != 1:
            raise ValueError('相机名称不唯一: ' + name)
        node = found[0]
        if cmds.nodeType(node) == 'camera':
            shapes = [node]
        elif cmds.objectType(node, isAType='transform'):
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True, type='camera') or []
        else:
            shapes = []
        if not shapes:
            raise ValueError('选择必须camera或直接camera transform: ' + name)
        for camera in shapes:
            if camera in cameras:
                continue
            parents = cmds.listRelatives(camera, parent=True, fullPath=True) or []
            if len(parents) != 1 or len(cmds.ls(camera, allPaths=True)) != 1:
                raise ValueError('不支持实例化camera')
            for candidate in (camera, parents[0]):
                scene.writable(candidate)
            if any(data['camera_uuid'] == scene.identity(camera) for _, data in records.values()):
                raise ValueError('相机已有DOF记录，请先cleanup')
            for attr in ('focusDistance', 'fStop'):
                plug = camera + '.' + attr
                if cmds.getAttr(plug, lock=True) or not cmds.getAttr(plug, settable=True) or scene.connection(plug):
                    raise ValueError('拒绝覆盖现有驱动/锁定通道: ' + plug)
                if not math.isfinite(cmds.getAttr(plug)):
                    raise ValueError('相机参数非有限数值')
            cameras.append(camera)
    if not cameras:
        raise ValueError('需要至少一台明确相机')
    args['cameras'] = cameras
    return args


class DofControlTool(BaseMayaTool):
    tool_id = 'dof_control_v1_0'
    tool_name = 'DOF焦距控制立方体'
    category = 'animation'
    version = '1.0-candidate.1'
    description = '原DOF cube/reverse/add图，TranslateZ焦距与ScaleZ fStop，持久owned安全清理/模板显示。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(message='只读相机/通道/owned记录检查，不source MEL或建节点', data=plan(**kwargs), dry_run=True)
        except Exception as error:
            return ToolResult.fail(message='预检失败: ' + str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        if args['action'] == 'open_ui':
            from .ui import show_window
            return ToolResult.ok(data={'window': show_window()})
        from .runtime import execute
        data = execute(args)
        if data.get('errors'):
            result = ToolResult.fail(message='DOF创建部分失败，请Undo', errors=data['errors'], data=data)
            result.warnings = data['warnings']
            return result
        return ToolResult.ok(data=data, warnings=data.get('warnings', []))

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data['window']
