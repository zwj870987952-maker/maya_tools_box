from maya import cmds
from . import tool as module


class HighlightTool:
    def __init__(self,tool=None):
        self.tool=tool or module.NoHighlightTool(); self.window_name='mtbHighlightToolWindow'

    def get_active_panel(self):
        from .view import choose
        return choose()

    def create_ui(self):
        if cmds.window(self.window_name,exists=True):
            self.close_tool()
            if module.SESSION is not None: raise RuntimeError('Resolve active session error before replacing window')
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name,title='Highlight Tool Candidate',widthHeight=(300,130),closeCommand=self.close_tool)
        cmds.columnLayout(adjustableColumn=True)
        self.panel=cmds.textField(placeholderText='modelPanel（留空使用活动视图）')
        self.toggle_button=cmds.button(label='Stop Tool' if module.SESSION else 'Start Tool',command=self.toggle_tool)
        cmds.button(label='预检 Start/Stop',command=self.preflight)
        cmds.button(label='恢复最近停止会话的覆盖（Undo Stop 后）',command=lambda *_:self.call('recover'))
        cmds.scriptJob(uiDeleted=[self.window_name,self.close_tool],runOnce=True)
        cmds.showWindow(self.window_name); return self.window_name

    def call(self,action,dry=False):
        kwargs={}
        if action=='start':
            panel=cmds.textField(self.panel,query=True,text=True).strip()
            if panel: kwargs['panel']=panel
        result=self.tool.run(action=action,dry_run=dry,**kwargs); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        if hasattr(self,'toggle_button') and cmds.button(self.toggle_button,exists=True):
            cmds.button(self.toggle_button,edit=True,label='Stop Tool' if module.SESSION else 'Start Tool')
        return result

    def toggle_tool(self,*args): return self.call('stop' if module.SESSION else 'start')
    def start_tool(self,*args): return self.call('start')
    def stop_tool(self,*args): return self.call('stop')
    def setup_tool(self,*args): return self.start_tool()
    def selection_changed(self,*args): return self.call('refresh')
    def preflight(self,*args): return self.call('stop' if module.SESSION else 'start',True)
    def close_tool(self,*args):
        if module.SESSION is not None:
            result=self.call('stop')
            if not result.success:
                module.SESSION.remove_callbacks(); module.SESSION.faulted=True
                module.SESSION.last_error=result.message+'; callbacks detached on window close; resolve node and call stop via API'
            return result
