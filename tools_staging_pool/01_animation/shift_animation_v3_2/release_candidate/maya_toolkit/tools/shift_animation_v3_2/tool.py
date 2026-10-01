import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=('status','analyze_curve','match','extract','auto_path','create_path','apply_path','create_circle','apply_circle','root_motion','lock_curve','unlock_curve','project_curve','curve_controls','arrange_controls','delete_controls','euler_filter','refresh_viewport')
LAYER_ACTIONS={'match','extract','auto_path','create_path','create_circle','root_motion'}
PATH_ACTIONS={'apply_path','apply_circle'}
CURVE_ACTIONS={'lock_curve','unlock_curve','project_curve','curve_controls','arrange_controls','delete_controls'}
PROPERTIES={
    'action':{'type':'string','enum':list(ACTIONS),'default':'status'},
    'session':{'type':'string','description':'Candidate session UUID/name; required when multiple sessions exist'},
    'layer':{'type':'string','description':'Explicit non-base animation layer or exactly one selected layer'},
    'objects':{'type':'array','items':{'type':'string'},'minItems':1,'uniqueItems':True,'description':'Whole controls/curves; default original ordered Maya selection for utilities'},
    'curve_object':{'type':'string','description':'Moving transform from which to construct a path; empty uses vendor auto detection'},
    'cv_count':{'type':'integer','minimum':1,'default':5},
    'easing':{'type':'integer','minimum':0,'default':10},
    'flat':{'type':'boolean','default':True},
    'vertical_independent':{'type':'boolean','default':True},
    'main':{'type':'string','description':'Root-motion main control'},
    'pelvis':{'type':'string','description':'Root-motion pelvis control'},
    'rotate':{'type':'boolean','default':False},
    'allow_attribute_cleanup':{'type':'boolean','default':False,'description':'Permit the original path/root-motion algorithm to remove ALL user-defined attributes from involved controls; backup and inspect first'},
    'curve':{'type':'string','description':'Existing time animation curve for read-only analysis'},
    'start_value':{'type':'number','default':0},
    'end_value':{'type':'number','default':1},
    'relative':{'type':'boolean','default':True},
}


def normalize(**kwargs):
    if set(kwargs)-set(PROPERTIES):
        raise ValueError('Unknown arguments')
    out=dict(kwargs)
    action=out.setdefault('action','status')
    if action not in ACTIONS:
        raise ValueError('Unknown action')
    for k in ('session','layer','main','pelvis','curve'):
        if k in out and (not isinstance(out[k],str) or not out[k].strip()):
            raise ValueError(k+' must be nonempty string')
    if 'curve_object' in out and not isinstance(out['curve_object'],str):
        raise ValueError('curve_object must be string')
    for k in ('flat','vertical_independent','rotate','relative','allow_attribute_cleanup'):
        if k in out and type(out[k]) is not bool:
            raise ValueError(k+' must be bool')
    for k,minimum in (('cv_count',1),('easing',0)):
        if k in out and (type(out[k]) is not int or out[k]<minimum):
            raise ValueError(k+' must be a valid integer')
    for k in ('start_value','end_value'):
        if k in out and (type(out[k]) not in (int,float) or not math.isfinite(out[k])):
            raise ValueError(k+' must be finite')
    if 'objects' in out:
        if not isinstance(out['objects'],list) or not out['objects'] or any(not isinstance(n,str) or not n.strip() for n in out['objects']) or len(set(out['objects']))!=len(out['objects']):
            raise ValueError('objects must be nonempty unique names')
    allowed={'action','session'}
    if action in LAYER_ACTIONS:
        allowed.add('layer')
    if action in CURVE_ACTIONS or action in ('euler_filter','extract'):
        allowed.add('objects')
    if action in ('create_path','auto_path'):
        allowed.update(('curve_object','cv_count','flat'))
    if action=='create_circle':
        allowed.add('curve_object')
    if action in ('auto_path','apply_path'):
        allowed.update(('easing','vertical_independent'))
    if action in ('auto_path','root_motion','apply_path','apply_circle'):
        allowed.add('allow_attribute_cleanup')
    if action=='root_motion':
        allowed.update(('main','pelvis','rotate','flat'))
        if not out.get('main') or not out.get('pelvis'):
            raise ValueError('root_motion requires main and pelvis')
    if action=='analyze_curve':
        allowed.update(('curve','start_value','end_value','relative'))
        if not out.get('curve'):
            raise ValueError('analyze_curve requires curve')
    if set(out)-allowed:
        raise ValueError('Arguments do not apply to this action: '+', '.join(sorted(set(out)-allowed)))
    return out


class ShiftAnimationTool(BaseMayaTool):
    tool_id='shift_animation_v3_2'
    tool_name='Shift Animation v3.2 动画移动候选'
    category='animation'
    version='3.2-candidate.1'
    description='完整原版 MATCH、AUTOPATH、手工路径、圆形行走、Root Motion 和曲线工具的外围适配；不修改授权 MEL。原算法属性清理影响须明确允许。真实 Maya 全流程待验收。'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            plan=preflight(normalize(**kwargs))
            data={k:v for k,v in plan.items() if k!='ledger'}
            return ToolResult.ok(message='输入及资源只读预检通过；原生完整算法待真实 Maya 验收',data=data,dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Shift Animation 操作完成；请核对输出动画层与原算法影响',data=execute(normalize(**kwargs)))

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()

    def show_original_ui(self):
        """Explicit original vendor UI for comparison in a backup scene only."""
        from .runtime import load_vendor
        import maya.cmds as cmds
        import maya.mel as mel
        if cmds.about(batch=True):
            raise RuntimeError('Original UI requires interactive Maya')
        if cmds.window('mtkShiftCandidateWindow',exists=True):
            raise RuntimeError('Close the candidate UI before opening original UI')
        if cmds.window('SHIFTING_animation',exists=True):
            raise RuntimeError('Original window already exists; use or close it')
        load_vendor()
        mel.eval('SHIFTING_animation_menue();')
        return 'SHIFTING_animation'
