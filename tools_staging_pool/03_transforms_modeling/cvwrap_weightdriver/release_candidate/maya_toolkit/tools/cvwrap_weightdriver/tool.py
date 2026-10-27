"""Accurate runtime adapter for the complete retained third-party suite."""
import math
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS=['status','load_plugin','create_wrap','rebind','import_binding','export_binding','paint_wrap','cvwrap_options','cvwrap_rebind_ui','weightdriver_editor','rbf_manager','mgear_menu']
PROPERTIES={'action':{'type':'string','enum':ACTIONS,'default':'status'},'objects':{'type':'array','items':{'type':'string'},'uniqueItems':True},'faces':{'type':'array','items':{'type':'string'},'uniqueItems':True},'wrap':{'type':'string'},'radius':{'type':'number','minimum':0,'maximum':100,'default':0.1},'name':{'type':'string','default':'cvWrap#'},'new_bind_mesh':{'type':'boolean','default':False},'path':{'type':'string'},'plugin':{'type':'string','enum':['cvwrap','weightDriver','mgear_solvers']}}


def normalize(kwargs):
    if set(kwargs)-set(PROPERTIES):
        raise ValueError('Unknown arguments')
    p=dict(kwargs)
    p.setdefault('action','status')
    if p['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    fields={'status':set(),'load_plugin':{'plugin','path'},'create_wrap':{'objects','radius','name','new_bind_mesh','path'},'rebind':{'objects','faces','wrap','radius'},'import_binding':{'wrap','path'},'export_binding':{'wrap','path'},'paint_wrap':{'wrap'},'cvwrap_options':set(),'cvwrap_rebind_ui':set(),'weightdriver_editor':set(),'rbf_manager':set(),'mgear_menu':set()}
    if set(p)-{'action'}-fields[p['action']]:
        raise ValueError('Arguments do not apply to action')
    for name,value in p.items():
        kind=PROPERTIES[name]['type']
        if kind=='array' and (not isinstance(value,list) or not value or any(not isinstance(n,str) or not n for n in value) or len(value)!=len(set(value))):
            raise ValueError(name+' must contain distinct nonempty names')
        if kind=='string' and (not isinstance(value,str) or not value):
            raise ValueError(name+' must be a nonempty string')
        if kind=='boolean' and type(value) is not bool:
            raise ValueError(name+' must be boolean')
        if kind=='number' and (type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=100):
            raise ValueError('radius must be finite [0,100]')
    if p['action']=='load_plugin' and (p.get('plugin') not in PROPERTIES['plugin']['enum'] or 'path' not in p):
        raise ValueError('Provide known plugin and absolute compatible binary path')
    if p['action'] in ('create_wrap','rebind'):
        p.setdefault('radius',0.1)
    if p['action']=='create_wrap':
        p.setdefault('name','cvWrap#')
        p.setdefault('new_bind_mesh',False)
    if p['action'] in ('import_binding','export_binding') and ('wrap' not in p or 'path' not in p):
        raise ValueError('wrap and path required')
    if p['action'] in ('rebind','paint_wrap') and 'wrap' not in p:
        raise ValueError('wrap required')
    if p['action']=='rebind' and ('objects' not in p or 'faces' not in p):
        raise ValueError('Explicit driven components and target faces required')
    return p


class CvWrapWeightDriverTool(BaseMayaTool):
    tool_id='cvwrap_weightdriver'
    tool_name='cvWrap / weightDriver / mGear 4.0.9'
    category='modeling_surfacing'
    version='4.0.9-candidate.1'
    description='Complete supplied third-party cvWrap/weightDriver/mGear suite, with accurate native plugin dependency checks, wrap create/rebind/paint/binding IO and original editors/menus. Compatible native plugins and PyMel required; real Maya acceptance pending.'
    parameters_schema={'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self,**kwargs):
        try:
            from .runtime import preflight
            return ToolResult.ok(message='Read-only suite dependency/scope plan',data=preflight(normalize(kwargs)),dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self,**kwargs):
        from .runtime import execute
        return ToolResult.ok(message='Third-party suite action; native/GUI acceptance must be recorded separately',data=execute(normalize(kwargs)))

    def show_ui(self,parent=None):
        from .ui import show_ui
        return show_ui()
