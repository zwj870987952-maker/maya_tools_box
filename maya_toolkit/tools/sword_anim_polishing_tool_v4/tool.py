import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=('status','parent_in','begin_aim','begin_sword','begin_reverse','finish_setup','arc_polish','bake','bake_layer','euler_filter','select_group','delete_system','update_motion_trails','refresh_viewport','help','constraint_weights')
GROUPS=('source','aim_top','aim_side','base','all','path_source','path_locator','path_system')
PROPERTIES={'action':{'type':'string','enum':list(ACTIONS),'default':'status'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'session':{'type':'string'},'start':{'type':'integer'},'end':{'type':'integer'},'size':{'type':'number','minimum':0.01,'maximum':100,'default':1},'knots':{'type':'integer','minimum':2,'maximum':20,'default':3},'show_source':{'type':'boolean','default':False},'group':{'type':'string','enum':list(GROUPS)},'topic':{'type':'string','enum':['base','reverse','path','bake']}}


def normalize(**kwargs):
    if set(kwargs)-set(PROPERTIES):
        raise ValueError('Unknown parameters')
    p=dict(kwargs,action=kwargs.get('action','status'))
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    per={'parent_in':{'size','start','end'},'begin_aim':{'size','start','end'},'begin_sword':{'start','end'},'begin_reverse':{'size','start','end'},'finish_setup':set(),'arc_polish':{'knots','show_source'},'bake':{'start','end'},'bake_layer':{'start','end'},'select_group':{'group'},'help':{'topic'}}
    if set(kwargs)-{'action','objects','session'}-per.get(p['action'],set()):
        raise ValueError('Parameters do not apply to this action')
    for name,value in kwargs.items():
        d=PROPERTIES[name]
        if d['type']=='boolean' and type(value) is not bool:
            raise ValueError(name+' must be boolean')
        if d['type']=='integer' and (type(value) is not int or value<d.get('minimum',-1e10) or value>d.get('maximum',1e10)):
            raise ValueError(name+' must be an in-range integer')
        if d['type']=='number' and (type(value) not in (float,int) or not math.isfinite(value) or value<d['minimum'] or value>d['maximum']):
            raise ValueError(name+' must be in range')
        if d['type']=='string' and (not isinstance(value,str) or not value or ('enum' in d and value not in d['enum'])):
            raise ValueError(name+' is invalid')
        if d['type']=='array' and (not isinstance(value,list) or any(not isinstance(n,str) or not n for n in value) or len(value)!=len(set(value))):
            raise ValueError('Objects must be unique whole node names')
    for name in per.get(p['action'],set()):
        if 'default' in PROPERTIES[name]:
            p.setdefault(name,PROPERTIES[name]['default'])
    if p['action']=='select_group' and 'group' not in p:
        raise ValueError('Specify group')
    if p['action']=='help':
        p.setdefault('topic','base')
    if 'start' in p and 'end' in p and p['end']<=p['start']:
        raise ValueError('End must exceed start')
    return p


class SwordAnimPolishTool(BaseMayaTool):
    tool_id='sword_anim_polishing_tool_v4'
    tool_name='Sword Anim Polishing'
    category='animation'
    version='4-candidate.1'
    description='Complete licensed weapon Parent In/Aim/Sword/Reverse/Arc Polish and bake suite, with explicit setup completion, UUID scoped session and read-only preflight. Real Maya acceptance required.'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Sword read-only preflight',data=preflight(normalize(**kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from . import runtime
        p=normalize(**kwargs)
        try:
            return ToolResult.ok(message='Sword action complete; original source defects and real GUI remain unverified',data=runtime.execute(p))
        except Exception as exc:
            return ToolResult.fail(message='Sword action failed; Undo partial scene changes: '+str(exc),errors=[str(exc)])

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()

    def show_original_ui(self):
        from .runtime import show_original_ui
        return show_original_ui()
