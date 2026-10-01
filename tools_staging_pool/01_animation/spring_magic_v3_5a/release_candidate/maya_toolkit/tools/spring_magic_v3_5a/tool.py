"""Lazy framework adapter for the complete private Spring Magic engine."""
import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=('status','compute','add_capsule','remove_capsule','clear_collision','add_plane','add_wind','bind_controls','bake_controls','copy_pose','paste_pose','straight','bind_pose')
PROPERTIES={
    'action':{'type':'string','enum':list(ACTIONS),'default':'status'},
    'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},
    'session':{'type':'string','description':'Owned network node, optional if only one session exists'},
    'start':{'type':'integer'},'end':{'type':'integer'},
    'spring':{'type':'number','minimum':0,'maximum':1,'default':0.7},
    'twist':{'type':'number','minimum':0,'maximum':1,'default':0.7},
    'tension':{'type':'number','minimum':0,'maximum':1,'default':0.5},
    'extend':{'type':'number','minimum':0,'maximum':1,'default':0},
    'inertia':{'type':'number','minimum':0,'maximum':1,'default':0},
    'subdivision':{'type':'number','minimum':1,'maximum':100,'default':1},
    'loop':{'type':'boolean','default':False},'pose_match':{'type':'boolean','default':False},
    'collision':{'type':'boolean','default':False},'fast_move':{'type':'boolean','default':False},
    'clear_subframes':{'type':'boolean','default':True},'linked_chains':{'type':'boolean','default':False},
    'allow_key_cleanup':{'type':'boolean','default':False,'description':'Normal mode cuts all keyable channels in range, as in original'},
    'allow_bind_pose_hierarchy':{'type':'boolean','default':False,'description':'Allow original GoToBindPose to affect connected hierarchy'}
}


def normalize(**kwargs):
    unknown=set(kwargs)-set(PROPERTIES)
    if unknown:
        raise ValueError('Unknown arguments: '+str(sorted(unknown)))
    action=kwargs.get('action','status')
    if action not in ACTIONS:
        raise ValueError('Unknown action')
    common={'action','objects','session'}
    per={'compute':{'start','end','spring','twist','tension','extend','inertia','subdivision','loop','pose_match','collision','fast_move','clear_subframes','allow_key_cleanup'},'bind_controls':{'linked_chains'},'bake_controls':{'start','end'},'bind_pose':{'allow_bind_pose_hierarchy'}}
    if set(kwargs)-common-per.get(action,set()):
        raise ValueError('Arguments do not apply to this action')
    p=dict(kwargs,action=action)
    for name,value in kwargs.items():
        definition=PROPERTIES[name]
        kind=definition['type']
        if kind=='boolean' and type(value) is not bool:
            raise ValueError(name+' must be boolean')
        if kind=='integer' and type(value) is not int:
            raise ValueError(name+' must be integer')
        if kind=='number' and (type(value) not in (float,int) or not math.isfinite(value) or value<definition['minimum'] or value>definition['maximum']):
            raise ValueError(name+' is out of range')
        if kind=='string' and (not isinstance(value,str) or not value):
            raise ValueError(name+' must be nonempty string')
        if kind=='array' and (not isinstance(value,list) or any(not isinstance(x,str) or not x for x in value) or len(value)!=len(set(value))):
            raise ValueError('Objects must be unique node names')
    for name in per.get(action,set()):
        if 'default' in PROPERTIES[name]:
            p.setdefault(name,PROPERTIES[name]['default'])
    if 'start' in p and 'end' in p and p['end']<=p['start']:
        raise ValueError('End must exceed start')
    if action=='compute' and not p['pose_match'] and not p['allow_key_cleanup']:
        raise ValueError('Normal spring mode cuts all keyable parent/child keys in range; set allow_key_cleanup=True after backing up')
    if action=='bind_pose' and not p['allow_bind_pose_hierarchy']:
        raise ValueError('Bind pose affects connected hierarchy; set allow_bind_pose_hierarchy=True in a backup scene')
    return p


class SpringMagicTool(BaseMayaTool):
    tool_id='spring_magic_v3_5a'
    tool_name='Spring Magic 3.5a'
    category='animation'
    version='3.5a-candidate.1'
    description='Complete spring/twist/tension/inertia/extension, capsule/plane/wind collision, loop/pose-match, control bind/bake and pose utilities. Requires compatible PyMel; real Maya acceptance pending.'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from . import runtime
            plan=runtime.preflight(normalize(**kwargs))
            return ToolResult.ok(message='Read-only Spring Magic preflight',data=plan,dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from . import runtime
        p=normalize(**kwargs)
        runtime.preflight(p)
        if p['action']=='status':
            return ToolResult.ok(message='Dependency/ownership status',data=runtime.preflight(p))
        try:
            return ToolResult.ok(message='Spring Magic action complete; real GUI acceptance pending',data=runtime.execute(p))
        except Exception as exc:
            return ToolResult.fail(message='Spring Magic failed; Undo the last operation before continuing: '+str(exc),errors=[str(exc)])

    def show_ui(self,parent=None):
        from . import runtime
        runtime.require_pymel()
        from .native.ui import SpringMagicWidget
        self._window=SpringMagicWidget()
        self._window.show()
        return self._window
