from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs) - {'action', 'objects'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    p.setdefault('action', 'disable')
    if p['action'] not in ('inspect', 'disable'):
        raise ValueError('Choose inspect or disable')
    if p['action'] == 'inspect' and 'objects' in p:
        raise ValueError('inspect takes no object arguments')
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 10000 or any(not isinstance(n, str) or not n.strip() or len(n) > 4096 for n in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Nonempty unique whole joint list required')
    return p


class SegmentScaleFixTool(BaseMayaTool):
    tool_id = 'segment_scale_fix'
    tool_name = '关闭骨骼分段比例补偿'
    category = 'rigging'
    version = '1.0-candidate.1'
    description = 'Disable segmentScaleCompensate on selected or explicit joints; read-only preflight, single Undo, real Maya acceptance pending.'
    parameters_schema = {'type': 'object', 'properties': {'action': {'type': 'string', 'enum': ['inspect', 'disable'], 'default': 'disable'}, 'objects': {'type': 'array', 'items': {'type': 'string'}, 'minItems': 1, 'maxItems': 10000, 'uniqueItems': True, 'description': 'Whole joints only; omitted uses selected joints, no hierarchy expansion'}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .operations import plan
            return ToolResult.ok(message='只读关节属性预检', data=plan(normalize(**kwargs)), dry_run=True)
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .operations import plan, apply
        p = normalize(**kwargs)
        result = plan(p)
        if p['action'] == 'disable':
            apply(result)
        return ToolResult.ok(message='分段比例补偿操作完成', data=result)

    def show_ui(self, parent=None):
        from .ui import show_ui
        return show_ui()
