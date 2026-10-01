from maya_toolkit.framework.base_tool import BaseMayaTool
from maya_toolkit.framework.models import ToolResult

ATTRS=('overrideEnabled','overrideShading')
SESSION=None
RECOVERY=None
PROPS={'action':{'type':'string','enum':['start','stop','refresh','status','recover'],'default':'status'},'panel':{'type':'string'}}


def normalize(kwargs):
    if set(kwargs)-set(PROPS): raise ValueError('Unknown arguments')
    p=dict(action='status'); p.update(kwargs)
    if p['action'] not in PROPS['action']['enum']: raise ValueError('Unknown action')
    if 'panel' in p and (not isinstance(p['panel'],str) or not p['panel'] or p['action']!='start'): raise ValueError('panel is a nonempty start-only string')
    return p


def shape(value):
    from maya import cmds
    from maya.api import OpenMaya as om
    matches=cmds.ls(value,long=True) or []
    if len(matches)!=1: raise ValueError('Missing/ambiguous shape')
    n=matches[0]; selection=om.MSelectionList(); selection.add(n)
    if not cmds.objectType(n,isAType='shape') or len(om.MDagPath.getAllPathsTo(selection.getDependNode(0)))!=1: raise ValueError('Non-instanced shape required')
    if cmds.referenceQuery(n,isNodeReferenced=True) or any(cmds.lockNode(n,query=True,lock=True) or []): raise ValueError('Referenced/locked shape')
    for attr in ATTRS:
        plug=n+'.'+attr
        if not cmds.objExists(plug) or cmds.getAttr(plug,lock=True) or cmds.listConnections(plug,source=True,destination=False): raise ValueError('Missing/locked/driven override attribute')
    return n,cmds.ls(n,uuid=True)[0],tuple(bool(cmds.getAttr(n+'.'+a)) for a in ATTRS)


def selected_shapes():
    from maya import cmds
    from maya.api import OpenMaya as om
    values=cmds.ls(selection=True,long=True,flatten=True) or []
    if not values: return []
    n=values[0].split('.',1)[0]; matches=cmds.ls(n,long=True) or []
    if len(matches)!=1: raise ValueError('First selected node missing/ambiguous')
    selection=om.MSelectionList(); selection.add(matches[0]); obj=selection.getDependNode(0)
    if not obj.hasFn(om.MFn.kDagNode) or len(om.MDagPath.getAllPathsTo(obj))!=1: raise ValueError('Non-instanced first DAG selection required')
    shapes=[matches[0]] if cmds.objectType(matches[0],isAType='shape') else cmds.listRelatives(matches[0],shapes=True,fullPath=True,noIntermediate=True) or []
    return [shape(s) for s in shapes]


def journal_plan(session):
    from maya import cmds
    rows=[]
    for uid,before in session.original.items():
        nodes=cmds.ls(uid,long=True) or []
        if not nodes: continue
        n,current_uid,current=shape(nodes[0])
        if current not in (before,(True,False)): raise ValueError('Shape override edited outside session; restore refused')
        rows.append({'uuid':uid,'node':n,'before':list(before),'current':list(current)})
    return rows


class HighlightSession:
    def __init__(self,tool,panel,sel_state):
        from maya import cmds
        from . import view
        self.tool=tool; self.panel=panel; self.sel_state=sel_state
        modes=view.selection_state(); self.object_mode=modes['object']; self.component_mode=modes['component']
        if not (self.object_mode or self.component_mode): raise ValueError('Object/component selection mode required')
        self.facet=modes['facet']
        self.original={}; self.current=[]; self.callbacks=[]; self.busy=False; self.faulted=False; self.events=0; self.last_error=None

    def selection_changed(self,*args):
        from maya.api import OpenMaya as om
        if om.MGlobal.isUndoing() or om.MGlobal.isRedoing():
            self.faulted=True; self.last_error='Selection event during Undo/Redo; stop session before restarting'; return
        if self.busy or self.faulted: return
        self.events+=1
        result=self.tool.run(action='refresh')
        if not result.success:
            from maya import cmds
            self.last_error=result.message; cmds.warning(result.message)

    def undo_changed(self,*args):
        if not self.busy: self.faulted=True; self.last_error='Undo/Redo observed; stop session before restarting'

    def scene_close(self,*args):
        global SESSION,RECOVERY
        from maya import cmds
        from . import view
        self.busy=True
        self.remove_callbacks()
        try:
            if view.exists(self.panel): view.apply(self.panel,self.sel_state)
            view.selection_apply(self.object_mode,self.facet)
        finally: SESSION=None; RECOVERY=None
        # Maya is replacing/closing the scene. Never modify outgoing scene
        # nodes from a scene-change callback or retain stale UUID references.

    def install(self):
        from maya.api import OpenMaya as om
        try:
            self.callbacks.append(om.MEventMessage.addEventCallback('SelectionChanged',self.selection_changed))
            for event in ('Undo','Redo'): self.callbacks.append(om.MEventMessage.addEventCallback(event,self.undo_changed))
            for message in (om.MSceneMessage.kBeforeNew,om.MSceneMessage.kBeforeOpen,om.MSceneMessage.kMayaExiting):
                self.callbacks.append(om.MSceneMessage.addCallback(message,self.scene_close))
        except Exception:
            self.remove_callbacks(); raise

    def remove_callbacks(self):
        from maya.api import OpenMaya as om
        errors=[]
        for callback in list(self.callbacks):
            try: om.MMessage.removeCallback(callback); self.callbacks.remove(callback)
            except Exception as e: errors.append(str(e))
        if errors: raise RuntimeError('Callback cleanup failed: '+'; '.join(errors))


def plan(p):
    from maya import cmds
    from . import view
    if p['action']=='status':
        return {'active':SESSION is not None,'panel':SESSION.panel if SESSION else None,'callbacks':len(SESSION.callbacks) if SESSION else 0,'faulted':SESSION.faulted if SESSION else False,'last_error':SESSION.last_error if SESSION else None,'selection_events':SESSION.events if SESSION else 0,'last_stop_recoverable':RECOVERY is not None}
    if not cmds.undoInfo(query=True,state=True): raise ValueError('Undo must be enabled')
    if p['action']=='recover':
        if SESSION is not None or RECOVERY is None: raise ValueError('Recover requires stopped session retained in this Maya process')
        return {'restore_rows':journal_plan(RECOVERY)}
    if p['action']=='start':
        if SESSION is not None: raise ValueError('Session already active; stop it first')
        panel=view.choose(p.get('panel'))
        modes=view.selection_state()
        if not (modes['object'] or modes['component']): raise ValueError('Object/component mode required')
        return {'panel':panel,'original_highlight':view.state(panel),'selection':selected_shapes()}
    if SESSION is None: raise ValueError('No active candidate session')
    rows=journal_plan(SESSION)
    if p['action']=='refresh':
        if SESSION.faulted: raise ValueError('Undo/Redo invalidated session; stop before restarting')
        if not view.exists(SESSION.panel): raise ValueError('Active modelPanel closed; stop session')
        selected=selected_shapes()
        return {'restore_rows':rows,'selection':selected}
    return {'restore_rows':rows,'panel_exists':view.exists(SESSION.panel)}


def set_values(n,values):
    from maya import cmds
    for attr,value in zip(ATTRS,values): cmds.setAttr(n+'.'+attr,value)


class NoHighlightTool(BaseMayaTool):
    tool_id='no_highlight_v2'; tool_name='取消选择高亮 v2'; category='modeling_surfacing'; version='2.0-candidate.1'
    description='完整Start/Stop/SelectionChanged工具：指定视图取消高亮并切面模式，保存逐shape原override，停止/关闭UI移除回调并恢复。'
    parameters_schema={'type':'object','properties':PROPS,'additionalProperties':False}

    def validate(self,**kwargs):
        try: return ToolResult.ok(data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e: return ToolResult.fail(message=str(e),errors=[str(e)])

    def execute(self,**kwargs):
        global SESSION,RECOVERY
        from maya import cmds
        from . import view
        p=normalize(kwargs); scope=plan(p)
        if p['action']=='status': return ToolResult.ok(data=scope)
        if p['action']=='recover':
            for row in scope['restore_rows']: set_values(row['node'],row['before'])
            return ToolResult.ok(data={'recovered':scope['restore_rows'],'callbacks':0})
        if p['action']=='start':
            session=HighlightSession(self,scope['panel'],scope['original_highlight']); SESSION=session; session.busy=True
            try:
                view.apply(session.panel,False); view.selection_apply(False,True)
                session.install()
                # Also process selection already present before starting.
                for n,uid,before in scope['selection']:
                    session.original[uid]=before; set_values(n,(True,False)); session.current.append(uid)
            except Exception:
                session.remove_callbacks()
                for row in journal_plan(session): set_values(row['node'],row['before'])
                if view.exists(session.panel): view.apply(session.panel,session.sel_state)
                view.selection_apply(session.object_mode,session.facet); SESSION=None; raise
            finally: session.busy=False
            return ToolResult.ok(data=plan({'action':'status'}))
        session=SESSION; session.busy=True
        try:
            if p['action']=='refresh':
                for row in scope['restore_rows']:
                    if row['uuid'] in session.current: set_values(row['node'],row['before'])
                session.current=[]
                for n,uid,before in scope['selection']:
                    if uid not in session.original: session.original[uid]=before
                    set_values(n,(True,False)); session.current.append(uid)
                return ToolResult.ok(data={'highlighted_uuids':session.current,'tracked_uuids':list(session.original)})
            session.remove_callbacks()
            for row in scope['restore_rows']: set_values(row['node'],row['before'])
            if scope['panel_exists']: view.apply(session.panel,session.sel_state)
            view.selection_apply(session.object_mode,session.facet); SESSION=None; RECOVERY=session
            return ToolResult.ok(data={'stopped':True,'restored':scope['restore_rows'],'callbacks':0})
        finally: session.busy=False

    def show_ui(self,parent=None):
        from maya import cmds
        if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
        from .ui import HighlightTool
        return HighlightTool(self).create_ui()
