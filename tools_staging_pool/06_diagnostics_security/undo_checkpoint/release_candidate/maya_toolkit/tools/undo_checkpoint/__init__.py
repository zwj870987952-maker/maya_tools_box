"""Full Maya Undo checkpoints. Queue operations intentionally bypass outer UndoChunk."""
import time
from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import manager

class UndoCheckpointTool(BaseMayaTool):
    tool_id='undo_checkpoint';tool_name='Maya 多记录点与Undo恢复';category='scene_hygiene'
    description='唯一/多记录点、只读队列预检、批量Undo、原面板/独立快捷/Shelf；不恢复文件IO'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['inspect','create','restore','clear','show_ui','install_shelf'],'default':'inspect'},
        'name':{'type':'string','maxLength':256},'overwrite':{'type':'boolean','default':False},'target_id':{'type':'string'},
        'max_steps':{'type':'integer','minimum':1,'maximum':100000,'default':5000},'shelf_name':{'type':'string'}}}
    def plan(self,**kwargs):
        if set(kwargs)-set(self.parameters_schema['properties']):raise ValueError('Unknown parameters')
        action=kwargs.get('action','inspect')
        if action not in self.parameters_schema['properties']['action']['enum']:raise ValueError('Invalid action')
        if not isinstance(kwargs.get('overwrite',False),bool):raise ValueError('overwrite must be bool')
        if kwargs.get('name') is not None and (not isinstance(kwargs['name'],str) or len(kwargs['name'])>256):raise ValueError('name must be <=256 characters')
        cmds=manager._cmds()
        if action in ('create','restore') and not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Undo')
        if action=='restore':return {'action':action,**manager.restore_plan(kwargs.get('target_id'),kwargs.get('max_steps',5000))}
        if action in ('show_ui','install_shelf'):
            if cmds.about(batch=True):raise ValueError('Interactive Maya required')
            if action=='install_shelf':
                from .shelf import shelf_plan
                return {'action':action,**shelf_plan(kwargs.get('shelf_name'))}
        queue=manager.queue_snapshot();names={row['name'] for row in queue}
        return {'action':action,'checkpoints':[dict(item.to_dict(),in_undo_queue=manager.PREFIX+item.id in names) for item in manager.items],
                'undo_queue_entries':len(queue),'impact':'Session-only marker metadata; restore undoes later scene actions. Never restores external writes or non-undoable commands.'}
    def validate(self,**kwargs):
        try:return ToolResult.ok(message='记录点预检通过，未注册marker/未改Undo队列/未开窗',data=self.plan(**kwargs),dry_run=True)
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        plan=self.plan(**kwargs);action=plan['action']
        if action=='create':
            item=manager.manager.create_checkpoint(kwargs.get('name'),kwargs.get('overwrite',False))
            if item is None:return ToolResult.fail(message='未创建记录点')
            return ToolResult.ok(message='已创建Undo标记',data=item.to_dict())
        if action=='restore':
            ok,count,message=manager.manager.restore_to_checkpoint(kwargs.get('target_id'),kwargs.get('max_steps',5000))
            return (ToolResult.ok if ok else ToolResult.fail)(message=message,data={'undid_steps':count,'target_id':plan['checkpoint']['id']})
        if action=='clear':manager.manager.clear()
        elif action=='show_ui':self.show_ui()
        elif action=='install_shelf':
            from .shelf import install_to_shelf
            return ToolResult.ok(message='四个owned Shelf按钮已就绪（不自动保存偏好）',data=install_to_shelf(kwargs.get('shelf_name')))
        return ToolResult.ok(message='记录点'+action+'完成',data=plan)
    def run(self,dry_run=False,**kwargs):
        from maya_toolkit.core.maya_utils import ensure_maya_initialized
        ensure_maya_initialized();start=time.time()
        if not isinstance(dry_run,bool):return ToolResult.fail(message='dry_run must be boolean',tool_id=self.tool_id)
        result=self.validate(**kwargs)
        if result.success and not dry_run:
            try:result=self.execute(**kwargs)
            except Exception as error:result=ToolResult.fail(message=str(error),errors=[str(error)])
        result.tool_id=self.tool_id;result.dry_run=bool(dry_run);result.execution_time=round(time.time()-start,4)
        if not dry_run and kwargs.get('action') in ('create','restore','clear'):
            import sys,html
            ui=sys.modules.get(__name__+'.ui');window=getattr(ui,'_CURRENT_UI_INSTANCE',None) if ui else None
            if window is not None:
                try:window.refresh_table()
                except RuntimeError:pass
            cmds=manager._cmds()
            if not cmds.about(batch=True):
                try:cmds.inViewMessage(amg=html.escape(result.message),pos='topCenter',fade=True,fst=2000)
                except RuntimeError:pass
        return result
    def show_ui(self):
        from .ui import show
        return show()

def create_checkpoint_standalone(name='唯一记录点',overwrite=True):
    return UndoCheckpointTool().run(action='create',name=name,overwrite=overwrite)
def restore_checkpoint_standalone():return UndoCheckpointTool().run(action='restore')
def clear_checkpoint_standalone():return UndoCheckpointTool().run(action='clear')
