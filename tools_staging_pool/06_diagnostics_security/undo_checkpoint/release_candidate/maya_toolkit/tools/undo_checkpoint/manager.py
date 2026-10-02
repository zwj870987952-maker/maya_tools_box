"""Named native Undo marker chunks and read-only queue presence checks."""
from pathlib import Path
import json
import re
import time
import uuid

PREFIX='mtbCheckpoint_'
COMMAND='mtbUndoCheckpointMarker'
items=[]
applied={}
last_undone=None

def _cmds():
    from maya import cmds
    return cmds

def parse_queue(messages):
    rows=[]
    for message in messages:
        for line in message.splitlines():
            match=re.fullmatch(r'\s*(\d+):\s*(.*?)\s*',line)
            if match:rows.append({'index':int(match.group(1)),'name':match.group(2)})
    if rows and [r['index'] for r in rows]!=list(range(len(rows))):raise RuntimeError('Unrecognized native Undo queue order; no rollback performed')
    return rows

def queue_snapshot():
    cmds=_cmds()
    if cmds.undoInfo(query=True,undoQueueEmpty=True):return []
    from maya.api import OpenMaya as om
    messages=[]
    def capture(message,kind,data):
        if re.match(r'^\s*\d+:',message):messages.append(message)
    # Maya 2025's Boolean-returning filter callback crashed during CPython teardown.
    # Plain output callbacks return None and leave console display untouched.
    handle=om.MCommandMessage.addCommandOutputCallback(capture)
    try:cmds.undoInfo(query=True,printQueue=True)
    finally:om.MMessage.removeCallback(handle)
    rows=parse_queue(messages)
    if not rows:raise RuntimeError('Unable to read native Undo queue; refusing speculative Undo')
    if len(rows)>100000:raise ValueError('Undo queue exceeds 100000 entries')
    return rows

class CheckpointItem:
    def __init__(self,identifier,name):
        self.id,self.name=identifier,name;self.time_str=time.strftime('%H:%M:%S')
    @property
    def status(self):return '有效 (Active)' if applied.get(self.id) else '已回退/失效 (Undone)'
    def to_dict(self):return {'id':self.id,'name':self.name,'time':self.time_str,'status':self.status}

def register_command():
    cmds=_cmds();path=Path(__file__).with_name('marker_command.py').resolve()
    for plugin in cmds.pluginInfo(query=True,listPlugins=True) or []:
        if COMMAND in (cmds.pluginInfo(plugin,query=True,command=True) or []):
            if Path(cmds.pluginInfo(plugin,query=True,path=True)).resolve()!=path:raise RuntimeError('Another candidate owns marker command; restart Maya')
            return
    cmds.loadPlugin(str(path),quiet=True)

def available():
    queue=queue_snapshot();names={r['name'] for r in queue}
    return [item for item in items if applied.get(item.id) and PREFIX+item.id in names]

def restore_plan(target_id=None,max_steps=5000):
    cmds=_cmds()
    if not cmds.undoInfo(query=True,state=True):raise ValueError('Enable Maya Undo')
    if not isinstance(max_steps,int) or isinstance(max_steps,bool) or not 1<=max_steps<=100000:raise ValueError('max_steps must be 1..100000')
    if target_id:
        target=next((item for item in items if item.id==target_id),None)
    else:
        candidates=available();target=candidates[-1] if candidates else None
    if target is None or not applied.get(target.id):raise ValueError('No active checkpoint with this ID')
    queue=queue_snapshot();matches=[i for i,row in enumerate(queue) if row['name']==PREFIX+target.id]
    if len(matches)!=1:raise ValueError('Checkpoint marker is absent/ambiguous in Undo queue; no Undo performed')
    steps=len(queue)-matches[0]
    if steps>max_steps:raise ValueError('Target requires '+str(steps)+' Undo steps, exceeding max_steps; no partial rollback')
    return {'checkpoint':target.to_dict(),'steps':steps,'queue':queue,'impact':'Undo all later operations, including the marker; file IO/non-undoable operations are not reverted'}

class Manager:
    @property
    def checkpoints(self):return items
    def create_checkpoint(self,name=None,overwrite=False):
        cmds=_cmds()
        if not cmds.undoInfo(query=True,state=True):cmds.warning('Enable Maya Undo before creating checkpoint');return None
        if not isinstance(overwrite,bool):raise ValueError('overwrite must be boolean')
        if name is not None and (not isinstance(name,str) or len(name)>256):raise ValueError('name must be a string <=256 characters')
        register_command();identifier='cp_'+uuid.uuid4().hex;item=CheckpointItem(identifier,(name or '').strip() or ('唯一记录点' if overwrite else '记录点_'+time.strftime('%H%M%S')))
        if overwrite:self.clear()
        items.append(item);applied[identifier]=True
        cmds.undoInfo(openChunk=True,chunkName=PREFIX+identifier)
        try:getattr(cmds,COMMAND)(json.dumps({'id':identifier,'name':item.name}))
        except Exception:items.remove(item);applied.pop(identifier,None);raise
        finally:cmds.undoInfo(closeChunk=True)
        if not any(row['name']==PREFIX+identifier for row in queue_snapshot()):
            applied[identifier]=False
            raise RuntimeError('Checkpoint nested in another open chunk; marker not independently visible. Call outside an existing Undo chunk')
        return item
    def get_latest_active_checkpoint(self):
        found=available();return found[-1] if found else None
    def restore_to_checkpoint(self,target_id=None,max_steps=5000):
        global last_undone
        cmds=_cmds()
        try:plan=restore_plan(target_id,max_steps)
        except Exception as error:return False,0,str(error)
        # The full ordered queue is checked immediately before each Undo.
        expected=plan['queue'];last_undone=None;count=0
        suspended=bool(cmds.refresh(query=True,suspend=True)) if not cmds.about(batch=True) else False
        if not cmds.about(batch=True):cmds.refresh(suspend=True)
        try:
            while expected:
                current=queue_snapshot()
                if current!=expected:return False,count,'Undo queue changed unexpectedly; stopped before next step'
                cmds.undo();count+=1;expected=expected[:-1]
                if last_undone==plan['checkpoint']['id']:return True,count,'成功回退 '+str(count)+' 步到 '+plan['checkpoint']['name']
                if count>=plan['steps']:return False,count,'Marker command was not reached as predicted; stopped'
        except Exception as error:return False,count,'Undo failed after '+str(count)+' steps: '+str(error)
        finally:
            if not cmds.about(batch=True):cmds.refresh(suspend=suspended)
        return False,count,'Target not reached'
    def clear(self):
        global last_undone
        items.clear();applied.clear();last_undone=None
    def get_checkpoint_name(self,identifier):
        return next((item.name for item in items if item.id==identifier),identifier)
manager=Manager()
