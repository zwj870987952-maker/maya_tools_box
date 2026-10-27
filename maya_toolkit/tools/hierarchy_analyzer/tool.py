from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult


def normalize(**kwargs):
    if set(kwargs)-{'objects', 'include_hierarchy', 'include_constraints', 'include_graph', 'max_nodes', 'max_edges'}:
        raise ValueError('Unknown arguments')
    p = dict(kwargs)
    if 'objects' in p and (not isinstance(p['objects'], list) or not 1 <= len(p['objects']) <= 1000 or any(not isinstance(x, str) or not x for x in p['objects']) or len(set(p['objects'])) != len(p['objects'])):
        raise ValueError('Unique nonempty whole-node objects required')
    for name, default in (('include_hierarchy', True), ('include_constraints', True), ('include_graph', False)):
        p.setdefault(name, default)
        if type(p[name]) is not bool:
            raise ValueError(name+' must be boolean')
    for name, default, minimum, maximum in (('max_nodes', 5000, 1, 50000), ('max_edges', 100000, 1, 1000000)):
        p.setdefault(name, default)
        if type(p[name]) is not int or not minimum <= p[name] <= maximum:
            raise ValueError('Bounded integer '+name+' required')
    return p


class HierarchyAnalyzerTool(BaseMayaTool):
    tool_id = 'hierarchy_analyzer'
    tool_name = '层级与约束影响分析'
    category = 'rigging'
    version = '1.0.0-candidate.1'
    description = '只读分析完整 DAG 与原生约束的潜在影响、间接路径、稳定分层和结构环；保留原完整结果界面。不是完整 Maya DG 求值证明。'
    parameters_schema = {'type': 'object', 'properties': {'objects': {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True, 'minItems': 1, 'maxItems': 1000}, 'include_hierarchy': {'type': 'boolean', 'default': True}, 'include_constraints': {'type': 'boolean', 'default': True}, 'include_graph': {'type': 'boolean', 'default': False}, 'max_nodes': {'type': 'integer', 'minimum': 1, 'maximum': 50000, 'default': 5000}, 'max_edges': {'type': 'integer', 'minimum': 1, 'maximum': 1000000, 'default': 100000}}, 'additionalProperties': False}

    def validate(self, **kwargs):
        try:
            from .engine import analyze
            data = analyze(normalize(**kwargs))
            return ToolResult.ok(message='Read-only structural analysis complete', data=data, dry_run=True, warnings=data['warnings'])
        except Exception as exc:
            return ToolResult.fail(message=str(exc), errors=[str(exc)])

    def execute(self, **kwargs):
        from .engine import analyze
        data = analyze(normalize(**kwargs))
        return ToolResult.ok(message='Structural analysis complete; inspect valid/cycles/unresolved', data=data, warnings=data['warnings'])

    def show_ui(self, parent=None):
        from maya import cmds
        if cmds.about(batch=True):
            raise RuntimeError('Interactive Maya required for the result window')
        from .native_ui import main
        return main()
