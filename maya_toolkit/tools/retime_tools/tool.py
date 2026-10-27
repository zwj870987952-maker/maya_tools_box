import traceback
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ['inspect', 'create', 'connect', 'disconnect', 'state', 'bake', 'shuffle', 'clean_subframes', 'rename', 'update_legacy', 'import_curve', 'export_curve', 'open_ui', 'open_legacy_ui', 'close_ui']
DEFAULTS = dict(action='inspect', controller=None, nodes=None, curves=None, state='Enable', name='retime_controller', file=None, overwrite=False, clean=False)


def normalize(**kwargs):
    if set(kwargs) - set(DEFAULTS):
        raise ValueError('Unknown parameters')
    o = dict(DEFAULTS, **kwargs)
    if o['action'] not in ACTIONS or o['state'] not in ['Enable', 'Disable', 'Reset', 'Invert', 'Disconnect', 'Delete']:
        raise ValueError('Invalid action/state')
    for k in ('overwrite', 'clean'):
        if type(o[k]) is not bool:
            raise ValueError(k + ' must be boolean')
    for k in ('controller', 'name', 'file'):
        if o[k] is not None and (not isinstance(o[k], str) or not o[k] or '\0' in o[k] or len(o[k]) > 4096):
            raise ValueError('Invalid ' + k)
    for k in ('nodes', 'curves'):
        v = o[k]
        if v is not None and (not isinstance(v, list) or not 1 <= len(v) <= 2000 or any(not isinstance(x, str) or not x or '\0' in x for x in v) or len(set(v)) != len(v)):
            raise ValueError('Invalid ' + k)
    return o


class RetimeToolsTool(BaseMayaTool):
    tool_id = 'retime_tools'
    tool_name = 'eblabs Retime Tools 动画重定时'
    category = 'animation'
    description = '原始完整 Qt 界面及控制曲线/启停反转/连接/烘焙/洗牌/子帧清理；附明确文件导入导出，真实Maya待验。'
    version = '1.0-candidate.1'
    parameters_schema = {'type':'object', 'properties':{
        'action':{'type':'string','enum':ACTIONS,'default':'inspect'},
        'controller':{'type':'string'}, 'name':{'type':'string','default':'retime_controller'},
        'nodes':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':2000,'uniqueItems':True},
        'curves':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':2000,'uniqueItems':True},
        'state':{'type':'string','enum':['Enable','Disable','Reset','Invert','Disconnect','Delete']},
        'file':{'type':'string'}, 'overwrite':{'type':'boolean','default':False}, 'clean':{'type':'boolean','default':False}},'additionalProperties':False}

    def validate(self, **kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过', data=prepare(normalize(**kwargs)), dry_run=True)
        except Exception as e:
            return ToolResult.fail('Retime预检失败', errors=str(e), dry_run=True)

    def execute(self, **kwargs):
        try:
            from .runtime import execute, prepare
            o = normalize(**kwargs)
            return ToolResult.ok('Retime操作完成', data=execute(o, prepare(o)))
        except Exception as e:
            return ToolResult.fail('Retime执行失败；已写场景可Undo，文件写入不可Undo', errors=[str(e),traceback.format_exc()])

    def show_ui(self, parent=None):
        return self.run(action='open_ui')
