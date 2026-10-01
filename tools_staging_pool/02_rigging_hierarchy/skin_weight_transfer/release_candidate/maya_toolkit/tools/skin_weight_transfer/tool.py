from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .algorithms import normalize


class SkinWeightTransferTool(BaseMayaTool):
    tool_id='skin_weight_transfer'
    tool_name='骨骼权重批量转移'
    category='rigging'
    version='1.0.0-candidate.1'
    description='Ordered tasks merge source joint weights into target across explicit or source-linked meshes, normalize all influences, optionally remove source influence. Undoable, read-only preflight; real Maya GUI acceptance pending.'
    parameters_schema={'type':'object','properties':{'action':{'type':'string','enum':['inspect','transfer'],'default':'transfer'},'tasks':{'type':'array','minItems':1,'maxItems':1000,'items':{'type':'object','properties':{'source_joint':{'type':'string'},'target_joint':{'type':'string'},'meshes':{'type':'array','minItems':1,'items':{'type':'string'},'uniqueItems':True},'remove_source':{'type':'boolean','default':False}},'required':['source_joint','target_joint'],'additionalProperties':False}},'task_text':{'type':'string','description':'source => target => mesh1,mesh2 => DelSkin; omit meshes for source-linked discovery'}},'oneOf':[{'required':['tasks']},{'required':['task_text']}],'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .operations import preflight
            return ToolResult.ok(message='Read-only complete ordered weight-transfer plan',data=preflight(normalize(kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .operations import execute
        return ToolResult.ok(message='Ordered weights merged; use Undo once to restore',data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()
