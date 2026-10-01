import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=['inspect','initialize','add','remove','clear','hide','show','toggle','hide_all','show_all','clear_body','clear_extra','cleanup','mirror','unlock_visible','unlock_meshes','lock_selection','show_faces','export_sets','import_sets','open_ui','native_callback']
SETS=['Head_Hider','Torso_Hider','Arm_R_Hider','Arm_L_Hider','Leg_R_Hider','Leg_L_Hider','Extra_One_Hider','Extra_Two_Hider','Extra_Three_Hider']
PROPS={'action':{'type':'string','enum':ACTIONS,'default':'inspect'},'system':{'type':'string','default':'mtbFCM'},'set':{'type':'string','enum':SETS,'default':'Head_Hider'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'shape_mode':{'type':'boolean','default':False},'path':{'type':'string'},'mirror_tolerance':{'type':'number','exclusiveMinimum':0,'maximum':1,'default':0.0001},'callback_ticket':{'type':'string'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(kwargs); p.setdefault('action','inspect'); p.setdefault('system','mtbFCM')
    if p['action'] not in ACTIONS: raise ValueError('Unknown action')
    for key,value in p.items():
        kind=PROPS[key]['type']
        if kind=='string' and (not isinstance(value,str) or not value): raise ValueError(key+' requires nonempty string')
        if kind=='array' and (not isinstance(value,list) or not value or any(not isinstance(n,str) or not n for n in value) or len(value)!=len(set(value))): raise ValueError('Explicit unique object/component names required')
        if kind=='boolean' and type(value) is not bool: raise ValueError('shape_mode requires bool')
        if kind=='number' and (type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=1): raise ValueError('Finite mirror tolerance (0,1] required')
    if 'set' in p and p['set'] not in SETS: raise ValueError('Unknown set')
    fields={'add':{'set','objects','shape_mode'},'remove':{'set','objects'},'clear':{'set'},'hide':{'set'},'show':{'set'},'toggle':{'set'},'lock_selection':{'objects'},'mirror':{'mirror_tolerance'},'export_sets':{'path'},'import_sets':{'path'},'native_callback':{'callback_ticket'}}.get(p['action'],set())
    if set(p)-{'action','system'}-fields: raise ValueError('Arguments do not apply to action')
    if p['action'] in ('export_sets','import_sets') and 'path' not in p or p['action']=='native_callback' and 'callback_ticket' not in p: raise ValueError('Missing path/ticket')
    if p['action'] in ('add','remove','clear','hide','show','toggle'): p.setdefault('set','Head_Hider')
    if p['action']=='add': p.setdefault('shape_mode',False)
    if p['action']=='mirror': p.setdefault('mirror_tolerance',0.0001)
    return p


class FcmHiderTool(BaseMayaTool):
    tool_id='fcm_hider'; tool_name='FCM Hider 完整集合显示工具'
    category='modeling_surfacing'; version='2.0-candidate.1'
    description='原完整身体/额外集合、对象/shape/面显示、镜像、选择/锁与全部UI，私有系统owner和JSON安全IO，真实Maya GUI待验收。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(data=preflight(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        result=self.run(action='open_ui')
        if not result.success: raise RuntimeError(result.message)
        return result.data
