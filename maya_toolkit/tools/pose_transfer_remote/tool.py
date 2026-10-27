from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS = dict(action='inspect', root=None, controllers=None, control_set=None, allow_reference_edits=False)
ACTIONS = ['inspect', 'detect', 'capture', 'shift', 'apply', 'cleanup', 'open_ui', 'close_ui']


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('Unknown parameters')
    o = dict(DEFAULTS)
    o.update(kwargs)
    if o['action'] not in ACTIONS or type(o['allow_reference_edits']) is not bool:
        raise ValueError('Invalid action/reference flag')
    for k in ('root', 'control_set'):
        if o[k] is not None and (not isinstance(o[k], str) or not o[k] or '\0' in o[k] or len(o[k]) > 2048):
            raise ValueError('Invalid ' + k)
    c = o['controllers']
    if c is not None and (not isinstance(c, list) or not 1 <= len(c) <= 1000 or any(not isinstance(n, str) or not n or '\0' in n or len(n) > 2048 for n in c) or len(set(c)) != len(c)):
        raise ValueError('controllers must be unique bounded strings')
    return o


class PoseTransferRemoteTool(BaseMayaTool):
    tool_id = 'pose_transfer_remote'
    tool_name = 'Pose Transfer ROOT平移姿态迁移'
    category = 'animation'
    version = '1.0-candidate.1'
    description = '完整原定位器姿态记录/ROOT平移/世界matrix应用与清理，UUID会话可Undo恢复，真人Maya待验。'
    parameters_schema = {'type':'object','properties':{
        'action':{'type':'string','enum':ACTIONS,'default':'inspect'},
        'root':{'type':'string'},'control_set':{'type':'string'},
        'controllers':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':1000,'uniqueItems':True},
        'allow_reference_edits':{'type':'boolean','default':False}},'additionalProperties':False}

    def validate(self, **kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过', data=prepare(normalize(**kwargs)), dry_run=True)
        except Exception as e:
            return ToolResult.fail('Pose Transfer 预检失败', errors=str(e), dry_run=True)

    def execute(self, **kwargs):
        try:
            from .runtime import execute, prepare
            o = normalize(**kwargs)
            return execute(o, prepare(o))
        except Exception as e:
            return ToolResult.fail('Pose Transfer 执行失败；已写场景可一次Undo', errors=str(e))

    def show_ui(self, parent=None):
        return self.run(action='open_ui')
