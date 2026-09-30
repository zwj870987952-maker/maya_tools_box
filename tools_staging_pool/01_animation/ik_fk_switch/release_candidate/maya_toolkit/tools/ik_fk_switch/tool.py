import importlib.util
import json
import math
from pathlib import Path
import re
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

CONTROLS = ('fkshldr', 'fkellbow', 'fkwrist', 'ikwrist', 'ikpv', 'switchCtrl')
ACTIONS = ['inventory', 'open_ui', 'store', 'load', 'records', 'match', 'switch', 'key', 'bake', 'export_store', 'import_store', 'native_callback']
DEFAULTS = dict.fromkeys(CONTROLS, '')
DEFAULTS.update(action='records', direction='to_ik', switchAttr='ikfk', switch0isfk=True, switchAttrRange=1, rotOffset=[0, 0, 0], side='R', limb='arm', bendKneeAxis='+X', record_id='', overwrite_store=False, allow_reference_edits=False, start=None, end=None, keys_only=False, file_path='', overwrite_file=False, callback_ticket='')
SCHEMA = {'type': 'object', 'properties': {**{n: {'type': 'string', 'default': ''} for n in CONTROLS}, 'action': {'type': 'string', 'enum': ACTIONS, 'default': 'records'}, 'direction': {'type': 'string', 'enum': ['to_ik', 'to_fk'], 'default': 'to_ik'}, 'switchAttr': {'type': 'string', 'default': 'ikfk'}, 'switchAttrRange': {'type': 'integer', 'enum': [1, 10], 'default': 1}, 'rotOffset': {'type': 'array', 'items': {'type': 'number'}, 'minItems': 3, 'maxItems': 3, 'default': [0, 0, 0]}, 'side': {'type': 'string', 'enum': ['R', 'L'], 'default': 'R'}, 'limb': {'type': 'string', 'enum': ['arm', 'leg'], 'default': 'arm'}, 'bendKneeAxis': {'type': 'string', 'enum': ['+X', '-X', '+Y', '-Y', '+Z', '-Z'], 'default': '+X'}, 'start': {'type': ['integer', 'null'], 'default': None}, 'end': {'type': ['integer', 'null'], 'default': None}, **{n: {'type': 'string', 'default': ''} for n in ('record_id', 'file_path', 'callback_ticket')}, **{n: {'type': 'boolean', 'default': DEFAULTS[n]} for n in ('switch0isfk', 'overwrite_store', 'allow_reference_edits', 'keys_only', 'overwrite_file')}}, 'additionalProperties': False}


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('未知参数')
    args = dict(DEFAULTS, **kwargs)
    if args['action'] not in ACTIONS or args['direction'] not in ('to_ik', 'to_fk') or args['side'] not in ('R', 'L') or args['limb'] not in ('arm', 'leg') or args['bendKneeAxis'] not in ('+X', '-X', '+Y', '-Y', '+Z', '-Z'):
        raise ValueError('action/direction/side/limb/bendKneeAxis无效')
    for name in CONTROLS + ('record_id', 'callback_ticket', 'switchAttr'):
        if not isinstance(args[name], str) or any(c in args[name] for c in '.*?[]\r\n'):
            raise ValueError(name + '须明确名称/UUID')
    if not re.fullmatch('[A-Za-z_][A-Za-z0-9_]*', args['switchAttr']):
        raise ValueError('switchAttr非法')
    for name in ('switch0isfk', 'overwrite_store', 'allow_reference_edits', 'keys_only', 'overwrite_file'):
        if type(args[name]) is not bool:
            raise ValueError(name + '须bool')
    if type(args['switchAttrRange']) is not int or args['switchAttrRange'] not in (1, 10):
        raise ValueError('switchAttrRange须1/10')
    if not isinstance(args['rotOffset'], list) or len(args['rotOffset']) != 3 or any(type(n) not in (int, float) or not math.isfinite(n) for n in args['rotOffset']):
        raise ValueError('rotOffset须三有限数值')
    for name in ('start', 'end'):
        if args[name] is not None and type(args[name]) is not int:
            raise ValueError(name + '须整数/null')
    if args['start'] is not None and args['end'] is not None and args['start'] > args['end']:
        raise ValueError('范围反转')
    if not isinstance(args['file_path'], str):
        raise ValueError('file_path须字符串')
    return args


def plan(**kwargs):
    args = normalize(**kwargs)
    if args['action'] == 'inventory':
        return args
    from maya import cmds
    from . import runtime
    if args['action'] == 'records':
        return args
    if args['action'] == 'open_ui':
        if cmds.about(batch=True):
            raise ValueError('完整原UI需要真实Maya GUI')
        if not importlib.util.find_spec('pymel'):
            raise ValueError('缺少目标Maya兼容pymel.core')
        return args
    if args['action'] in ('export_store', 'import_store'):
        path = Path(args['file_path'])
        if not args['file_path'] or not path.is_absolute() or path.suffix.lower() != '.json':
            raise ValueError('Store传输须绝对.json路径')
        path = path.resolve()
        if args['action'] == 'export_store':
            if path.exists() and (not path.is_file() or not args['overwrite_file']):
                raise ValueError('覆盖已有文件需overwrite_file=True')
            args['stores'] = runtime.export_data()
            if not args['stores']:
                raise ValueError('无自有Store')
        else:
            if not path.is_file():
                raise ValueError('Store文件不存在')
            value = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(value, dict) or value.get('format') != runtime.OWNER or not isinstance(value.get('stores'), list) or not value['stores']:
                raise ValueError('非候选Store JSON')
            if len(value['stores']) > 1000:
                raise ValueError('Store数量过大')
            args['stores'] = [plan(**dict(row, action='store', overwrite_store=args['overwrite_store'], allow_reference_edits=args['allow_reference_edits'])) for row in value['stores']]
            signatures = [(row['fkwrist'], row['side'], row['limb']) for row in args['stores']]
            if len(set(signatures)) != len(signatures):
                raise ValueError('重复Store槽位')
        args['file_path'] = str(path)
        return args
    if runtime._ACTIVE:
        raise ValueError('已有IKFK运行中')
    if args['action'] == 'native_callback':
        item = runtime._CALLBACKS.get(args['callback_ticket'])
        if not item:
            raise ValueError('无有效原UI回调ticket')
        args.update(item['fields'])
        args['require_native'] = True
    if args['record_id']:
        args.update(runtime.load_record(args['record_id'])['fields'])
    elif args['action'] == 'load':
        raise ValueError('load须明确record_id')
    controls = []
    for name in CONTROLS:
        found = cmds.ls(args[name], long=True) if args[name] else []
        if len(found) != 1 or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('须唯一transform/joint: ' + name)
        args[name] = found[0]
        controls.append(found[0])
    if len(set(controls[:5])) != 5:
        raise ValueError('五个IK/FK控制器须不同')
    switch = args['switchCtrl'] + '.' + args['switchAttr']
    if not cmds.objExists(switch) or cmds.getAttr(switch, type=True) not in ('double', 'float', 'long', 'short', 'byte', 'enum'):
        raise ValueError('Switch须已有数值属性')
    if args['action'] == 'load':
        return args
    if args['action'] in ('match', 'bake') or args.get('require_native'):
        if not importlib.util.find_spec('pymel'):
            raise ValueError('缺少目标Maya兼容pymel.core；原匹配/烘焙未运行')
    store_operation = args['action'] == 'store' or (args['action'] == 'native_callback' and item['function'].__name__ == 'saveIkFkCtrlsWin')
    if store_operation:
        if not cmds.undoInfo(query=True, state=True):
            raise ValueError('请开启Undo')
        if any(cmds.referenceQuery(n, isNodeReferenced=True) for n in controls) and not args['allow_reference_edits']:
            raise ValueError('Store的message连接也产生reference edits，须明确允许')
        existing = runtime.matching_store(args)
        if existing and not args['overwrite_store']:
            raise ValueError('已有自有Store，更新须overwrite_store=True')
        args['existing_store'] = existing
        return args
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('请开启Undo')
    for name, node in zip(CONTROLS, controls):
        if cmds.lockNode(node, query=True, lock=True)[0] or cmds.referenceQuery(node, isNodeReferenced=True) and not args['allow_reference_edits']:
            raise ValueError('控制器锁定/引用编辑未允许: ' + node)
        attrs = ('rx', 'ry', 'rz') if name.startswith('fk') else ('tx', 'ty', 'tz', 'rx', 'ry', 'rz') if name == 'ikwrist' else ('tx', 'ty', 'tz') if name == 'ikpv' else (args['switchAttr'],)
        for attr in attrs:
            plug = node + '.' + attr
            if cmds.getAttr(plug, lock=True):
                raise ValueError('所需通道锁定: ' + plug)
            for source in cmds.listConnections(plug, source=True, destination=False) or []:
                if not cmds.nodeType(source).startswith('animCurve'):
                    raise ValueError('控制器通道有外部驱动: ' + plug)
    for node in controls:
        for curve in cmds.ls(cmds.listHistory(node, pruneDagObjects=True) or [], type='animCurve') or []:
            if cmds.lockNode(curve, query=True, lock=True)[0] or cmds.referenceQuery(curve, isNodeReferenced=True):
                raise ValueError('动画曲线锁定/引用')
            for destination in cmds.listConnections(curve + '.output', source=False, destination=True) or []:
                if (cmds.ls(destination, long=True) or [''])[0] not in controls:
                    raise ValueError('动画曲线被外部共享')
    if args['action'] == 'bake':
        args['start'] = int(cmds.playbackOptions(query=True, minTime=True)) if args['start'] is None else args['start']
        args['end'] = int(cmds.playbackOptions(query=True, maxTime=True)) if args['end'] is None else args['end']
        if args['start'] > args['end'] or args['end'] - args['start'] > 10000:
            raise ValueError('Bake范围反转/过大')
        source = controls[3:5] if args['direction'] == 'to_fk' else controls[:3]
        frames = sorted(set(cmds.keyframe(source, query=True) or [])) if args['keys_only'] else list(range(args['start'], args['end'] + 1))
        args['frames'] = [t for t in frames if args['start'] <= t <= args['end']]
        if not args['frames']:
            raise ValueError('Bake无目标帧')
    return args


class IKFKTool(BaseMayaTool):
    tool_id = 'ik_fk_switch'
    tool_name = 'Universal IK FK PRO完整候选'
    category = 'animation'
    version = '3.0-candidate.1'
    description = '完整原匹配/Pole Vector/临时IK链/Pro UI/Bake，标准回调与自有Store记录和显式JSON传输；需兼容PyMel。'
    parameters_schema = SCHEMA

    def validate(self, **kwargs):
        try:
            return ToolResult.ok(data=plan(**kwargs), dry_run=True, message='只读参数/控制器/引用/共享/Store/覆盖/依赖预检')
        except Exception as error:
            return ToolResult.fail(message=str(error), errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args = plan(**kwargs)
        if args['action'] == 'inventory':
            return ToolResult.ok(data=json.loads((Path(__file__).parent / 'catalog.json').read_text(encoding='utf-8')))
        from .runtime import execute
        return ToolResult.ok(data=execute(args), warnings=['匹配/烘焙会临时清零/删改控制器key；先备份。失败请Undo；Store JSON文件写入不归Maya Undo。'])

    def show_ui(self, parent=None):
        result = self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
