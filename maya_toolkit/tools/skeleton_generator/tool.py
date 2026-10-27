import re
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs)-{'action','objects','suffix','select_result'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action','create')
    if p['action'] not in ('inspect','create'):
        raise ValueError('Choose inspect or create')
    if p['action']=='inspect' and set(p)!={'action'}:
        raise ValueError('inspect accepts no mutation arguments')
    p.setdefault('suffix','_copy')
    if not isinstance(p['suffix'],str) or not re.fullmatch(r'_[A-Za-z0-9_]{1,63}',p['suffix']):
        raise ValueError('Suffix must begin with underscore and contain 1..63 name characters')
    p.setdefault('select_result',True)
    if type(p['select_result']) is not bool:
        raise ValueError('select_result must be boolean')
    if 'objects' in p and (not isinstance(p['objects'],list) or not 1<=len(p['objects'])<=10000 or any(not isinstance(n,str) or not n.strip() or len(n)>4096 for n in p['objects']) or len(set(p['objects']))!=len(p['objects'])):
        raise ValueError('Nonempty unique whole object list required')
    return p


class SkeletonGeneratorTool(BaseMayaTool):
    tool_id = 'skeleton_generator'
    tool_name = '选区生成骨骼链'
    category = 'rigging'
    version = '1.0-candidate.1'
    description = 'Create posed joint forests from selected joints/locator transforms; selected immediate-parent edges only, world TR/radius/drawStyle, dry scope and Undo.'
    parameters_schema = {'type':'object','properties':{'action':{'type':'string','enum':['inspect','create'],'default':'create'},'objects':{'type':'array','items':{'type':'string'},'minItems':1,'maxItems':10000,'uniqueItems':True,'description':'Whole joints/locator transforms; omitted filters current selection as original; no automatic hierarchy expansion'},'suffix':{'type':'string','pattern':'^_[A-Za-z0-9_]{1,63}$','default':'_copy'},'select_result':{'type':'boolean','default':True}},'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .operations import plan
            return ToolResult.ok(message='只读骨架范围和命名预检',data=plan(normalize(**kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .operations import execute
        return ToolResult.ok(message='骨架创建完成',data=execute(normalize(**kwargs)))

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()
