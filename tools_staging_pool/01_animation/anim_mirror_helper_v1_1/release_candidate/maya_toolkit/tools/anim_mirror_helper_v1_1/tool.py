"""Framework gateway to the intact commercial MEL tool."""
import re
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import ACTIONS, ALIASES, CATALOG, HEADLESS, normalize, resources
from . import runtime

WARNINGS = ['Original catch/catchQuiet can conceal partial failures; inspect Script Editor and scene.',
            'Scene operations use one Undo chunk; MEL globals, original UI, clipboard and tool context are not scene Undo.',
            'Original UI and viewport callbacks execute original MEL directly; framework guards apply only to gateway calls.']


class AnimMirrorHelperTool(BaseMayaTool):
    tool_id = 'anim_mirror_helper_v1_1'
    tool_name = '动画镜像辅助'
    category = 'Animation'
    version = '1.1.1-adapter'
    description = 'Pavel Barnev 动画镜像系统：创建、连接、错帧重算、烘焙及删除；保留完整原始过程。'
    parameters_schema = dict(type='object', additionalProperties=False, properties={
        'action': dict(type='string', enum=ACTIONS, default='inventory'),
        'procedure': dict(type='string', enum=['']+sorted(CATALOG['procedures']), default=''),
        'arguments': dict(type='object', description='Original MEL parameter names; inventory provides exact signatures'),
        'force_reload': dict(type='boolean', default=False)})

    def validate(self, **kwargs):
        try:
            args, name, signature, command = normalize(kwargs)
            resources()
            data = dict(action=args['action'], procedure=name, command=command,
                        signature=signature, gui_acceptance=False, scene_write=args['action'] not in ('inventory','load','open_ui','copy_rotation'))
            if args['action']=='inventory':
                data.update(procedures=CATALOG['procedures'], actions=ALIASES, resources=CATALOG['resources'])
                return ToolResult.ok('原始资源和参数目录完整', data=data, dry_run=True)
            import maya.cmds as cmds
            if args['action']!='load' and name not in HEADLESS and cmds.about(batch=True):
                raise ValueError('Interactive Maya required for this operation; standalone is not GUI acceptance')
            if not cmds.undoInfo(query=True,state=True):
                raise ValueError('Enable Maya Undo before using the gateway')
            action = args['action']
            selection = cmds.ls(selection=True,long=True,flatten=True) or []
            data['selection'] = selection
            if action in ALIASES or action in ('bake_selected','mirror_rotation','zero_rotation'):
                if not selection:
                    raise ValueError('Select required transforms in the documented order')
                if any(not cmds.objectType(n,isAType='transform') for n in selection):
                    raise ValueError('Select whole transforms, not shapes or components')
                # Original internal helpers sometimes concatenate node names into eval strings.
                if any(re.search(r'[\s;"`{}()]', n) for n in selection):
                    raise ValueError('Original MEL helpers require simple Maya node paths')
                if action!='copy_rotation' and any(cmds.referenceQuery(n,isNodeReferenced=True) or cmds.lockNode(n,query=True,lock=True)[0] for n in selection):
                    raise ValueError('Selected nodes are referenced/locked; test on a writable duplicate rig')
                if action in ('attach_pairs','connect_attributes') and len(selection)%2:
                    raise ValueError('Select ordered mirror/control pairs (even number of transforms)')
                if action in ('copy_rotation','auto_connect','calculate','delete_system') and len(selection)!=1:
                    raise ValueError('This action requires exactly one selected transform')
                if action=='add_items' and len(selection)<2:
                    raise ValueError('Select added controls then the system locator last')
                if action in ('auto_connect','calculate','delete_system','add_items'):
                    locator = selection[-1]
                    nodes = cmds.listConnections(locator,source=True,destination=True) or []
                    if not any('mirror_barnev_system' in n and cmds.objExists(n+'.base_groupps') for n in nodes):
                        raise ValueError('Last selection is not connected to an original mirror system')
                if action=='bake_selected':
                    start, end = cmds.playbackOptions(query=True,animationStartTime=True), cmds.playbackOptions(query=True,animationEndTime=True)
                    if start>end:
                        raise ValueError('Animation range must increase')
                    data['animation_range'] = [start,end]
            return ToolResult.ok('只读预检通过；未加载 MEL 或修改场景', data=data, warnings=WARNINGS, dry_run=True)
        except Exception as error:
            return ToolResult.fail('预检失败', errors=[str(error)], dry_run=True)

    def execute(self, **kwargs):
        args, name, signature, command = normalize(kwargs)
        resources()
        if args['action']=='inventory':
            result = self.validate(**kwargs)
            result.dry_run = False
            return result
        loaded = runtime.load_suite(name or None,args['force_reload'])
        if args['action']=='load':
            return ToolResult.ok('原始 MEL 已显式加载', data=loaded, warnings=WARNINGS)
        outcome = runtime.invoke(command)
        data = dict(loaded=loaded, procedure=name, outcome=outcome, gui_acceptance=False)
        if outcome['error'] or outcome['runtime_state_errors']:
            return ToolResult.fail('原始操作或运行状态恢复失败；检查场景', data=data,
                                   errors=([outcome['error']] if outcome['error'] else [])+outcome['runtime_state_errors'])
        return ToolResult.ok('原始 MEL 调用返回；请核对场景效果', data=data, warnings=WARNINGS)

    def show_ui(self, parent=None):
        from .ui import show
        return show(self)
