import math

from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ACTIONS = ('status','add_mesh','remove_mesh','remove_all','set_enabled','set_key','delete_key','delete_all_keys','begin_sculpt','end_sculpt','reset_shape','step_key','inspect_legacy','adopt_legacy')
PROPERTIES = {
    'action':{'type':'string','enum':list(ACTIONS),'default':'status'},
    'session':{'type':'string','description':'Candidate session UUID or unambiguous network name'},
    'layer_id':{'type':'string','description':'Persistent corrective layer id returned by add_mesh'},
    'mesh':{'type':'string','description':'Whole mesh/transform for add_mesh; otherwise exactly one selected mesh'},
    'frame':{'type':'number','description':'Explicit key/sculpt frame; default current Maya time'},
    'enabled':{'type':'boolean','description':'Required for set_enabled'},
    'direction':{'type':'string','enum':['prev','next'],'description':'Required for step_key'},
    'legacy_node':{'type':'string','default':'sat','description':'Read-only old SAT network or explicit adoption source'},
    'accept_legacy_ownership':{'type':'boolean','default':False,'description':'Explicitly transfer exclusive legacy deformer/driver ownership; backup first'}
}


def normalize(**kwargs):
    extra = set(kwargs)-set(PROPERTIES)
    if extra:
        raise ValueError('Unknown arguments: '+', '.join(sorted(extra)))
    value = dict(kwargs)
    value.setdefault('action','status')
    if value['action'] not in ACTIONS:
        raise ValueError('Unknown action')
    for key in ('session','layer_id','mesh','legacy_node'):
        if key in value and (not isinstance(value[key],str) or not value[key].strip()):
            raise ValueError(key+' must be a nonempty string')
    if 'frame' in value and (type(value['frame']) not in (int,float) or not math.isfinite(value['frame'])):
        raise ValueError('frame must be finite')
    for key in ('enabled','accept_legacy_ownership'):
        if key in value and type(value[key]) is not bool:
            raise ValueError(key+' must be boolean')
    if 'direction' in value and value['direction'] not in ('prev','next'):
        raise ValueError('direction must be prev/next')
    if value['action']=='set_enabled' and 'enabled' not in value:
        raise ValueError('set_enabled requires enabled')
    if value['action']=='step_key' and 'direction' not in value:
        raise ValueError('step_key requires direction')
    if value['action']=='adopt_legacy' and value.get('accept_legacy_ownership') is not True:
        raise ValueError('Adoption requires accept_legacy_ownership=True and a backup scene')
    allowed = {'session','action'}
    if value['action']=='add_mesh':
        allowed.add('mesh')
    elif value['action'] in ('inspect_legacy','adopt_legacy'):
        allowed.update(('legacy_node','accept_legacy_ownership'))
    elif value['action'] not in ('status','remove_all'):
        allowed.add('layer_id')
    if value['action'] in ('set_key','delete_key','begin_sculpt'):
        allowed.add('frame')
    if value['action']=='set_enabled':
        allowed.add('enabled')
    if value['action']=='step_key':
        allowed.add('direction')
    if set(value)-allowed:
        raise ValueError('Arguments do not apply to this action: '+', '.join(sorted(set(value)-allowed)))
    return value


class ShapeAnimationTool(BaseMayaTool):
    tool_id = 'shape_animation_tool'
    tool_name = 'Shape Animation Tool 修型动画候选'
    category = 'animation'
    version = '2.0-candidate.1'
    description = '完整成对 blendShape 修型目标、关键帧、雕刻和网格拾取；支持持久 UUID 会话和显式旧数据接管。雕刻模式须调用 end_sculpt 完成；真实 GUI 待验收。'
    parameters_schema = {'type':'object','properties':PROPERTIES,'additionalProperties':False}

    def validate(self, **kwargs):
        try:
            options = normalize(**kwargs)
            from .runtime import preflight
            engine,value = preflight(options)
            data = {'action':options['action'],'session':engine.sid,'scene_write':options['action'] not in ('status','inspect_legacy'),'pending_sculpt':bool(engine.data['editing']),'file_write':False}
            if options['action']=='inspect_legacy':
                data['legacy_layers']=value
            return ToolResult.ok(message='参数与场景预检通过；真实 Maya GUI 待验收',data=data,dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc),errors=[str(exc)])

    def execute(self, **kwargs):
        from .runtime import execute
        return ToolResult.ok(message='修型动画操作完成；请在备份场景验收',data=execute(normalize(**kwargs)))

    def show_ui(self, parent=None):
        from .ui_bridge import show_ui
        return show_ui(parent)
