"""BaseMayaTool contract for the unverified, locally staged Animo bundle."""
from maya_toolkit.framework import BaseMayaTool, ToolResult
from . import session


class AnimoTool(BaseMayaTool):
    tool_id = 'animo'
    tool_name = 'Animo 动画套件（待人工检验）'
    category = 'animation'
    version = '10.6.0-staging.1'
    description = '检索和调用 540 个固定脚本及 13 个套件入口；仅候选、未通过 Maya 检验。dry_run 不导入原工具或写场景/文件。'
    parameters_schema = {
        'type': 'object', 'additionalProperties': False,
        'properties': {
            'action': {'type': 'string', 'enum': list(session.ACTION_NAMES), 'default': 'inspect'},
            'operation_id': {'type': 'string', 'enum': [row['id'] for row in session.operations()],
                             'description': 'invoke 的固定白名单入口；用 catalog 查询，不接受文件路径/代码'},
            'objects': {'type': 'array', 'minItems': 1, 'maxItems': 4096, 'uniqueItems': True,
                        'items': {'type': 'string', 'minLength': 1},
                        'description': 'invoke 可选的有序节点数组；省略时保持原生选择。执行时会改变选择，保留原操作的最终选择'},
            'query': {'type': 'string', 'default': '', 'description': 'catalog 搜索名称、ID、中文用途'},
            'operation_category': {'type': 'string', 'default': '', 'description': 'catalog 的原始英文分类'},
            'offset': {'type': 'integer', 'minimum': 0, 'default': 0},
            'limit': {'type': 'integer', 'minimum': 1, 'maximum': 200, 'default': 50},
        },
    }

    def validate(self, **kwargs):
        try:
            _, data = session.preflight(kwargs)
            return ToolResult.ok(message='候选预检通过；未导入原生工具、修改选择/场景或写文件', data=data,
                                 warnings=['MAYA_MANUAL_CHECK_PENDING', '原生业务前提由具体入口检查，预检通过不等于执行成功'], dry_run=True)
        except (ValueError, OSError, TypeError) as exc:
            return ToolResult.fail(message='候选预检失败：' + str(exc), errors=[str(exc)], dry_run=True)

    def execute(self, **kwargs):
        args, report = session.preflight(kwargs)
        action = args['action']
        if action in ('inspect', 'catalog'):
            report['preflight_only'] = False
            return ToolResult.ok(message='返回候选结构信息', data=report)
        if action == 'show_ui':
            self.show_ui()
            return ToolResult.ok(message='打开候选人工检验面板', data={'state': 'review_ui_opened', 'maya_verified': False})
        if action == 'install_runtime':
            data = session.install_runtime(report['runtime_directory'])
            return ToolResult.ok(message='安装候选运行副本，未启动 Animo', data=data,
                                 warnings=['运行副本复制不受 Maya Undo 保护；未覆盖已有目录'])
        operation = session.find_operation('suite.toolbar') if action == 'launch_toolbar' else report['operation']
        data = session.invoke(operation, report['runtime_directory'], args['objects'])
        return ToolResult.ok(message='原生入口已分派，实际结果等待人工检查', data=data,
                             warnings=['原生工具可能自行提示/取消或延迟创建 UI；不能据此声称业务已成功',
                                       '文件、插件、UI、偏好与模块路径改变不受 Maya Undo 保护；失败不会自动回滚'])

    def show_ui(self, parent=None):
        from .ui import show
        return show(self, parent)
