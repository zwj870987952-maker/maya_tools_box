"""Unknown nodes/plugins and explicit viewport callbacks; no PyMel dependency."""
from pathlib import Path
import json
from maya_toolkit.framework import BaseMayaTool, ToolResult

def _cmds():
    from maya import cmds
    return cmds

def normalize(values):
    allowed={'action','include_unknown_dag','remove_unknown_plugins','confirm_plugin_metadata_loss','unlock_nodes','callback_policy','confirm_all_callbacks'}
    if set(values)-allowed: raise ValueError('Unknown parameters')
    p=dict(action='inspect',include_unknown_dag=False,remove_unknown_plugins=False,confirm_plugin_metadata_loss=False,unlock_nodes=False,callback_policy='known',confirm_all_callbacks=False)
    p.update(values)
    if p['action'] not in ('inspect','clean') or p['callback_policy'] not in ('none','known','all'): raise ValueError('Invalid action/callback_policy')
    for key in allowed-{'action','callback_policy'}:
        if not isinstance(p[key],bool): raise ValueError('Boolean required: '+key)
    if p['callback_policy']=='all' and not p['confirm_all_callbacks']: raise ValueError('All ModelEditor callbacks requires confirm_all_callbacks=True')
    if p['remove_unknown_plugins'] and not p['confirm_plugin_metadata_loss']: raise ValueError('Unknown plugin removal is not reliably Undoable; back up scene and pass confirm_plugin_metadata_loss=True')
    return p

def plan(p):
    cmds=_cmds(); types=['unknown']+(['unknownDag','unknownTransform'] if p['include_unknown_dag'] else [])
    nodes=sorted(set(n for typ in types for n in (cmds.ls(type=typ,long=True) or [])))
    rows=[]
    for node in nodes:
        referenced=cmds.referenceQuery(node,isNodeReferenced=True)
        locked=bool(cmds.lockNode(node,query=True,lock=True)[0])
        default=bool(cmds.ls(node,defaultNodes=True))
        descendants=cmds.listRelatives(node,allDescendents=True,fullPath=True) or []
        row={'node':node,'uuid':cmds.ls(node,uuid=True)[0],'type':cmds.nodeType(node),'locked':locked,'referenced':referenced,'descendants':descendants}
        try: row['original_plugin']=cmds.unknownNode(node,query=True,plugin=True)
        except Exception: row['original_plugin']=None
        rows.append(row)
        if p['action']=='clean':
            if referenced or default: raise ValueError('Referenced/default unknown node refused: '+node)
            if locked and not p['unlock_nodes']: raise ValueError('Locked unknown node requires explicit unlock_nodes=True: '+node)
            if descendants: raise ValueError('Unknown DAG with descendants refused; isolate intended scope: '+node)
            from maya.api import OpenMaya as om
            selection=om.MSelectionList(); selection.add(node); obj=selection.getDependNode(0)
            if obj.hasFn(om.MFn.kDagNode) and len(om.MDagPath.getAllPathsTo(obj))>1: raise ValueError('Instanced unknown DAG refused')
    plugins=[]
    for name in sorted(cmds.unknownPlugin(query=True,list=True) or []):
        plugins.append({'name':name,'version':cmds.unknownPlugin(name,query=True,version=True),
                        'node_types':cmds.unknownPlugin(name,query=True,nodeTypes=True) or [],'data_types':cmds.unknownPlugin(name,query=True,dataTypes=True) or []})
    callbacks=[]
    if p['callback_policy']!='none' and not cmds.about(batch=True):
        for editor in sorted(set(cmds.lsUI(editors=True) or [])):
            if not cmds.modelEditor(editor,exists=True): continue
            callback=cmds.modelEditor(editor,query=True,editorChanged=True) or ''
            if callback and (p['callback_policy']=='all' or callback=='CgAbBlastPanelOptChangeCallback'):
                callbacks.append({'editor':editor,'callback':callback})
    if p['action']=='clean' and not cmds.undoInfo(query=True,state=True): raise ValueError('Enable Undo before cleanup')
    return {'nodes':rows,'unknown_plugins':plugins,'callbacks':callbacks,'options':p,
        'impact':'Unknown is missing-plugin metadata, not proof of junk/virus. Delete listed local nodes/connections with lifetime Undo; plugin removal NOT reliably Undoable; callbacks restore through owned command. No external files saved.'}

def cleanup(p):
    cmds=_cmds(); data=plan(p)
    path=Path(__file__).with_name('delete_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if 'mtbCleanJunkNodes' in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path: raise ValueError('Another candidate owns cleanup command; restart Maya')
            break
    else: cmds.loadPlugin(str(path),quiet=True)
    value=cmds.mtbCleanJunkNodes(json.dumps(p)); data=json.loads(value[0] if isinstance(value,list) else value)
    data['removed_plugins']=[]; data['plugin_errors']=[]
    if p['remove_unknown_plugins']:
        for row in data['unknown_plugins']:
            try: cmds.unknownPlugin(row['name'],remove=True); data['removed_plugins'].append(row['name'])
            except Exception as error: data['plugin_errors'].append({'plugin':row['name'],'error':str(error)})
    return data

class CleanJunkNodesTool(BaseMayaTool):
    tool_id='clean_junk_nodes'; tool_name='HM 未知节点、插件与回调清理'; category='scene_hygiene'
    description='完整未知节点/插件/ModelEditor回调清理；预检不修改，未知不等于垃圾'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','clean'],'default':'inspect'},
        'include_unknown_dag':{'type':'boolean','default':False},'remove_unknown_plugins':{'type':'boolean','default':False},
        'confirm_plugin_metadata_loss':{'type':'boolean','default':False},
        'unlock_nodes':{'type':'boolean','default':False},'callback_policy':{'type':'string','enum':['none','known','all'],'default':'known'},
        'confirm_all_callbacks':{'type':'boolean','default':False}}}
    def validate(self,**kwargs):
        try: return ToolResult.ok(message='清理范围预检完成',data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        p=normalize(kwargs); data=cleanup(p) if p['action']=='clean' else plan(p)
        if data.get('plugin_errors'): return ToolResult.fail(message='节点已清理，部分插件仍被使用；可Undo',data=data,errors=[r['error'] for r in data['plugin_errors']])
        return ToolResult.ok(message='未知数据'+('清理' if p['action']=='clean' else '查询')+'完成',data=data)
    def show_ui(self):
        from .ui import show_ui
        return show_ui()
