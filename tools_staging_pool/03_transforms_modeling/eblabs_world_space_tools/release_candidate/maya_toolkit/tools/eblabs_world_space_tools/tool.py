import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=['inventory','to_world','to_parent','to_local','ik_chain','create_paths','path_locator','rebuild_path','copy','snap','child_cog','parent_cog','gimbal','open_ui','open_beta','import_preferences','export_preferences','native_callback']
PROPS={'action':{'type':'string','enum':ACTIONS,'default':'inventory'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'attributes':{'type':'array','items':{'type':'string','enum':['tx','ty','tz','rx','ry','rz']},'uniqueItems':True},'start':{'type':'number'},'end':{'type':'number'},'on_keys':{'type':'boolean','default':True},'maintain_offset':{'type':'boolean','default':False},'spans':{'type':'integer','minimum':1,'maximum':200,'default':6},'path':{'type':'string'},'beta_root':{'type':'string'},'callback_ticket':{'type':'string'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS):
        raise ValueError('Unknown parameters')
    p=dict(kwargs)
    p.setdefault('action','inventory')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    for key,value in p.items():
        kind=PROPS[key]['type']
        if kind=='string' and (not isinstance(value,str) or not value):
            raise ValueError(key+' must be nonempty string')
        if kind=='array' and (not isinstance(value,list) or not value or any(not isinstance(x,str) or not x for x in value) or len(value)!=len(set(value))):
            raise ValueError(key+' requires unique nonempty string array')
        if kind=='boolean' and type(value) is not bool:
            raise ValueError(key+' requires bool')
        if kind=='number' and (type(value) not in (int,float) or not math.isfinite(value)):
            raise ValueError(key+' requires finite number')
        if kind=='integer' and (type(value) is not int or not 1<=value<=200):
            raise ValueError('spans must be int [1,200]')
    if 'attributes' in p and set(p['attributes'])-set(PROPS['attributes']['items']['enum']):
        raise ValueError('TR attributes only')
    if ('start' in p)!=('end' in p) or 'start' in p and (p['start']>p['end'] or p['end']-p['start']>10000):
        raise ValueError('Provide ordered paired start/end range <=10000 frames')
    space={'objects','attributes','start','end','on_keys'}
    allowed={'inventory':set(),'open_ui':set(),'open_beta':{'beta_root'},'import_preferences':{'path'},'export_preferences':{'path'},'native_callback':{'callback_ticket'},'to_world':space,'to_parent':space,'ik_chain':space,'to_local':{'objects','start','end','on_keys'},'copy':space|{'maintain_offset'},'rebuild_path':{'objects','spans'}}.get(p['action'],{'objects'})
    if set(p)-{'action'}-allowed:
        raise ValueError('Parameters do not apply to action')
    if p.get('on_keys') is False and 'start' not in p:
        raise ValueError('Baked operation requires explicit start/end')
    if p['action'] in ('import_preferences','export_preferences') and 'path' not in p or p['action']=='native_callback' and 'callback_ticket' not in p:
        raise ValueError('Required path/ticket absent')
    if p['action'] not in ('inventory','open_ui','open_beta','import_preferences','export_preferences','native_callback'):
        p.setdefault('attributes',['tx','ty','tz','rx','ry','rz'])
        p.setdefault('on_keys',True)
        p.setdefault('maintain_offset',False)
        p.setdefault('spans',6)
    return p


class WorldSpaceToolsTool(BaseMayaTool):
    tool_id='eblabs_world_space_tools'
    tool_name='EB Labs WorldSpaceTools 完整源码套件'
    category='animation'
    version='1.2.4-source-candidate.1'
    description='完整原世界/父级/局部/IK/路径空间、复制、COG与Gimbal源码/UI及资源；UUID作用域/安全清理/只读预检/Undo。Beta Hub缺原专有版本模块，真实GUI待验收。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(data=preflight(normalize(kwargs)),dry_run=True,message='Read-only source-suite scope/dependency plan')
        except Exception as e:
            return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        from .runtime import execute
        return ToolResult.ok(data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        result=self.run(action='open_ui')
        if not result.success:
            raise RuntimeError(result.message)
        return result.data
