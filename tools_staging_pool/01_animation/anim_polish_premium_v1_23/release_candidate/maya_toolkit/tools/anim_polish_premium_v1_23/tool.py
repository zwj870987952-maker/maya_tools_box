"""Full suite dispatcher: lazy imports, read-only validation and unified scene Undo."""
import ast
import json
from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult
from .contracts import CATALOG, HEADLESS, API_FUNCTIONS, NODE_PARAMS, ARRAY_PARAMS, normalize, resources
from .file_guards import cache_path,node_list
from . import runtime,state

WARNINGS = ['Original exception swallowing may hide partial failure; check scene and Script Editor.',
            'Scene calls use UndoChunk; exported cache files and JSON settings/clipboard cannot be reverted by Maya Undo.',
            'Original UI callbacks use repaired vendor code, not framework validate/finally.']


class AnimPolishTool(BaseMayaTool):
    tool_id = 'anim_polish_premium_v1_23'
    tool_name = 'AnimPolish 动画变形润色'
    category = 'Animation'
    version = '1.23.1-adapter'
    description = '完整 AnimPolish：Sculpt/P2P、Wrap、Subdue、Grow/Shrink、Iron、Sticky Mod、缓存和辅助功能。'
    parameters_schema = dict(type='object',additionalProperties=False,properties={
        'action':dict(type='string',enum=['inventory','open_ui','invoke'],default='inventory'),
        'function':dict(type='string',enum=['']+API_FUNCTIONS,default=''),
        'arguments':dict(type='object',description='Original function keyword arguments; exact signature from inventory'),
        'dock':dict(type='integer',enum=[0,1],default=0)})

    def validate(self,**kwargs):
        try:
            args,fn,bound = normalize(kwargs)
            resources()
            data = dict(action=args['action'],function=args['function'],arguments=bound,gui_acceptance=False)
            if args['action']=='inventory':
                data.update(functions=CATALOG['functions'],resources=CATALOG['resources'])
                return ToolResult.ok('完整目录与原始素材校验通过',data=data,dry_run=True)
            import maya.cmds as cmds
            if not cmds.undoInfo(query=True,state=True):
                raise ValueError('Enable Undo before executing the suite')
            function = args['function']
            paint = bool(bound.get('verts') or bound.get('floodverts'))
            if cmds.about(batch=True) and (args['action']=='open_ui' or function not in HEADLESS or paint or bound.get('editMode')):
                raise ValueError('Interactive Maya required for this UI/paint/Channel Box workflow')
            # Check declared node parameters without importing/reloading vendor business code.
            nodes = []
            for key,value in bound.items():
                if key in NODE_PARAMS and isinstance(value,str) and value:
                    nodes.append(value)
                elif key in ARRAY_PARAMS and isinstance(value,(str,list)) and value:
                    values = ast.literal_eval(value) if isinstance(value,str) else value
                    if not isinstance(values,list) or any(not isinstance(n,str) for n in values):
                        raise ValueError(key+' requires a list of node/component names')
                    nodes.extend(values)
            for node in nodes:
                if not cmds.objExists(node):
                    raise ValueError('Missing scene input: '+node)
            selection = cmds.ls(selection=True,flatten=True,long=True) or []
            data['selection'] = selection
            if function.endswith('_sel') or function in ('smoothPreview.run','subdue.run','copyPasteAttrs.copy','copyPasteAttrs.paste','caching.swap','caching.delete'):
                if not selection:
                    raise ValueError('Select the objects/components required by the original workflow')
            if function.startswith('copyPasteAttrs.'):
                if function.endswith('.copy') and len(selection)!=1:
                    raise ValueError('Copy requires one selected object')
                directory = state.data_directory(bound.get('path',''))
                data['state_directory'] = directory.as_posix()
                if function.endswith('.paste'):
                    source = directory/'attributes.json'
                    clipboard = json.loads(source.read_text(encoding='utf-8'))
                    if clipboard.get('version')!=1 or not isinstance(clipboard.get('attributes'),list):
                        raise ValueError('Invalid clipboard JSON')
            if function in ('caching.exp_geos','caching.exp_cams','caching.imp_geos','caching.imp_cams','caching.swap'):
                leaf = 'cameras.ma' if function.endswith(('exp_cams','imp_cams')) else 'geometry.abc'
                writing = function.startswith('caching.exp_')
                directory,target = cache_path(bound['path'],leaf,writing)
                data.update(file=target.as_posix(),file_write=writing,file_undo=False)
                plugin = ('AbcExport' if writing else 'AbcImport') if leaf=='geometry.abc' and function!='caching.swap' else None
                if plugin and not cmds.pluginInfo(plugin,query=True,loaded=True):
                    raise ValueError('Load '+plugin+' explicitly before cache operations')
                if writing:
                    key = 'geos' if leaf=='geometry.abc' else 'cams'
                    node_list(bound[key])
            if function=='subdue.run' and cmds.evaluationManager(query=True,mode=True)[0]!='off':
                raise ValueError('Subdue requires DG/off evaluation; preflight never changes it')
            if function=='subdue.run':
                data.update(file_write=True,file_undo=False,cache_parent=(state.data_directory()/'subdue_cache').as_posix())
            if function in ('quickBake.run','quickBake.run_sel','quickBake.rivet','quickBake.rivet_sel','quickBake.plane','quickBake.plane_sel'):
                data['bake_range'] = [cmds.playbackOptions(query=True,minTime=True),cmds.playbackOptions(query=True,maxTime=True)]
            return ToolResult.ok('只读预检通过；未导入业务模块或写场景/文件',data=data,warnings=WARNINGS,dry_run=True)
        except Exception as error:
            return ToolResult.fail('预检失败',errors=[str(error)],dry_run=True)

    def execute(self,**kwargs):
        args,fn,bound = normalize(kwargs)
        resources()
        if args['action']=='inventory':
            result = self.validate(**kwargs)
            result.dry_run = False
            return result
        if args['action']=='open_ui':
            fn,bound = dict(module='ui',name='ui'),dict(dock=args['dock'])
        outcome = runtime.invoke(fn['module'],fn['name'],bound)
        data = dict(function=fn['module']+'.'+fn['name'],outcome=outcome,gui_acceptance=False)
        if outcome['error'] or outcome['runtime_state_errors']:
            return ToolResult.fail('操作或运行状态恢复失败；检查部分变动',errors=([outcome['error']] if outcome['error'] else [])+outcome['runtime_state_errors'],data=data)
        return ToolResult.ok('AnimPolish 调用返回；核对实际变形结果',data=data,warnings=WARNINGS)

    def show_ui(self,parent=None):
        from .ui import show
        return show(self)
