import math
import traceback
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

DEFAULTS=dict(action='inspect',groups=None,translate_axes=['z'],rotate_axes=[],maintain_offset=True,start=None,end=None,time_range='timeline',snapshot_center=True)
ACTIONS=['inspect','discover','bake','open_ui','close_ui']


def normalize(**kwargs):
    if set(kwargs)-set(DEFAULTS):
        raise ValueError('Unknown parameters')
    o=dict(DEFAULTS,**kwargs)
    if o['action'] not in ACTIONS or o['time_range'] not in ('timeline','selected','animation','explicit'):
        raise ValueError('Invalid action/time_range')
    for k in ('maintain_offset','snapshot_center'):
        if type(o[k]) is not bool:
            raise ValueError(k+' must be boolean')
    for k in ('translate_axes','rotate_axes'):
        v=o[k]
        if not isinstance(v,list) or any(x not in ('x','y','z') for x in v) or len(v)!=len(set(v)):
            raise ValueError('Axes must be unique x/y/z')
    for k in ('start','end'):
        v=o[k]
        if v is not None and (type(v) not in (int,float) or not math.isfinite(v) or abs(v)>1e6):
            raise ValueError('Invalid frame: '+k)
    if (o['start'] is None)!=(o['end'] is None):
        raise ValueError('start and end must be supplied together')
    if o['time_range']=='explicit' and o['start'] is None:
        raise ValueError('Explicit start/end required')
    if o['groups'] is not None:
        if not isinstance(o['groups'],list) or not 1<=len(o['groups'])<=100:
            raise ValueError('groups must be 1..100 objects')
        for g in o['groups']:
            if not isinstance(g,dict) or set(g)-{'root','center','ring'} or not g.get('root') or not g.get('center'):
                raise ValueError('Each group needs root/center and optional ring')
            for k,v in g.items():
                if v is not None and (not isinstance(v,str) or not v or '\0' in v or len(v)>2048):
                    raise ValueError('Invalid group node')
    return o


class RootMotionBakeTool(BaseMayaTool):
    tool_id='root_motion_bake'
    tool_name='Root Motion 约束烘焙与偏移层'
    category='animation'
    version='1.0-candidate.1'
    description='完整原质心约束Root、烘焙与大环世界位置/Euler相对偏移层；全组预检与临时快照，真实Maya待验。'
    parameters_schema={'type':'object','properties':{
        'action':{'type':'string','enum':ACTIONS,'default':'inspect'},
        'groups':{'type':'array','minItems':1,'maxItems':100,'items':{'type':'object','properties':{'root':{'type':'string'},'center':{'type':'string'},'ring':{'type':['string','null']}},'required':['root','center'],'additionalProperties':False}},
        'translate_axes':{'type':'array','items':{'type':'string','enum':['x','y','z']},'uniqueItems':True,'default':['z']},
        'rotate_axes':{'type':'array','items':{'type':'string','enum':['x','y','z']},'uniqueItems':True,'default':[]},
        'maintain_offset':{'type':'boolean','default':True},'snapshot_center':{'type':'boolean','default':True},
        'start':{'type':'number'},'end':{'type':'number'},'time_range':{'type':'string','enum':['timeline','selected','animation','explicit'],'default':'timeline'}},'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import prepare
            return ToolResult.ok('只读预检通过',data=prepare(normalize(**kwargs)),dry_run=True)
        except Exception as e:
            return ToolResult.fail('Root Motion预检失败',errors=str(e),dry_run=True)

    def execute(self,**kwargs):
        try:
            from .runtime import execute,prepare
            o=normalize(**kwargs)
            return ToolResult.ok('Root Motion操作完成',data=execute(o,prepare(o)))
        except Exception as e:
            return ToolResult.fail('Root Motion执行失败；临时对象会清理，已写动画可Undo',errors=[str(e),traceback.format_exc()])

    def show_ui(self,parent=None):
        return self.run(action='open_ui')
