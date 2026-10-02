"""Complete supplied native callbacks, owned shelf, lazy MEL execution."""
from pathlib import Path
import hashlib
import json
import re
from .file_guard import checked_path,require_new
HERE=Path(__file__).resolve().parent
SHELF='MTB_Malcolm341_Candidate'
TAG='maya_toolkit.malcolm341_mega_pack'
owned_shelf=None

def inventory():
    data=json.loads((HERE/'native/commands.json').read_text(encoding='utf8'))
    for row in data['buttons']:
        for c in row['callbacks']:
            if hashlib.sha256(c['command'].encode()).hexdigest()!=c['sha256']:raise RuntimeError('Native payload hash mismatch')
    return data

def lookup(button,event):
    row=next((r for r in inventory()['buttons'] if r['id']==button),None)
    if row is None:raise ValueError('Unknown button id')
    callback=next((c for c in row['callbacks'] if c['event']==event),None)
    if callback is None or not callback['command']:raise ValueError('No executable callback for this event')
    return row,callback

def metadata():
    d=inventory()
    return {'source_sha256':d['source_sha256'],'native_guard_counts':d['guard_counts'],
            'buttons':[{'id':r['id'],'label':r['label'],'description':r['annotation'],
                        'events':[{'event':c['event'],'label':c['label'],'effects':c['effects']}
                                  for c in r['callbacks'] if c['command']]} for r in d['buttons']],
            'gui_acceptance':'not_run','license':'Supplied paid pack; personal candidate, original notices retained'}

def temp_mode(button,event):
    if button not in ('button_006','button_007'):return None
    _,c=lookup(button,event)
    match=re.search(r'int \$mode = ([1-8]);',c['command'])
    if not match:raise ValueError('Native temporary transfer mode absent')
    return int(match.group(1))

def compile_guards():
    from maya import mel
    mel.eval((HERE/'native/guards.mel').read_text(encoding='utf8'))

def show_shelf():
    global owned_shelf
    from maya import cmds,mel
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    if cmds.shelfLayout(SHELF,exists=True):
        if not owned_shelf or not cmds.shelfLayout(owned_shelf,exists=True) or cmds.shelfLayout(owned_shelf,query=True,docTag=True)!=TAG:
            raise RuntimeError('A foreign shelf has this name; refusing overwrite')
        return owned_shelf
    top=mel.eval('$mtbM341ShelfTop = $gShelfTopLevel')
    old_parent=cmds.setParent(query=True)
    try:
        shelf=cmds.shelfLayout(SHELF,parent=top,docTag=TAG)
        owned_shelf=shelf
        cmds.setParent(shelf)
        mel.eval((HERE/'native/shelf.mel').read_text(encoding='utf8'))
        mel.eval('MTB_shelf_malcolm341_mega_pack();')
        children=cmds.shelfLayout(shelf,query=True,childArray=True) or []
        if len(children)!=49:raise RuntimeError('Expected 49 native buttons')
        cmds.tabLayout(top,edit=True,selectTab=shelf)
        return shelf
    except Exception:
        if owned_shelf and cmds.shelfLayout(owned_shelf,exists=True):cmds.deleteUI(owned_shelf)
        owned_shelf=None
        raise
    finally:
        if old_parent and cmds.layout(old_parent,exists=True):cmds.setParent(old_parent)

def close_shelf():
    global owned_shelf
    from maya import cmds
    if owned_shelf and cmds.shelfLayout(owned_shelf,exists=True):
        if cmds.shelfLayout(owned_shelf,query=True,docTag=True)!=TAG:raise RuntimeError('Shelf ownership changed')
        cmds.deleteUI(owned_shelf)
    owned_shelf=None

def run_native(button,event,file_path=None):
    from maya import cmds,mel
    from maya_toolkit.core.context import UndoChunkContext
    _,c=lookup(button,event); code=c['command'];mode=temp_mode(button,event)
    if mode and mode<=6:
        p=checked_path(file_path)
        if mode<=3:require_new(str(p))
        elif not p.is_file():raise FileNotFoundError(str(p))
        # Only trusted path literals in the transfer script are replaced. Input
        # is MEL-escaped; no arbitrary caller code is interpolated.
        quoted=json.dumps(p.as_posix(),ensure_ascii=False)
        parent=json.dumps(p.parent.as_posix(),ensure_ascii=False)
        code=re.sub(r'"(?:C:/MTB_m341_temp|/Users/Shared/MTB_m341_temp)/temp\.(?:ma|mlt|obj|fbx)"',lambda m:quoted,code)
        code=code.replace('"C:/MTB_m341_temp"',parent).replace('"/Users/Shared/MTB_m341_temp"',parent)
        code=code.replace('file  -ignoreVersion','file -executeScriptNodes false -ignoreVersion')
    compile_guards()
    before=cmds.ls(selection=True,long=True,flatten=True) or []
    with UndoChunkContext('Malcolm341_'+button+'_'+event):
        try:return mel.eval(code)
        finally:
            # Preserve the original selection for the proven pivot operation.
            # Other native tools intentionally produce a result selection.
            if button=='button_018' and event=='primary':
                cmds.select([n for n in before if cmds.objExists(n)],replace=True)

def dispatch(button,event):
    from maya import cmds
    from . import Malcolm341MegaPackTool
    row,c=lookup(button,event)
    mode=temp_mode(button,event);path=None
    if mode and mode<=6:
        ext={1:'ma',2:'obj',3:'fbx',4:'ma',5:'obj',6:'fbx'}[mode]
        chosen=cmds.fileDialog2(fileMode=0 if mode<=3 else 1,fileFilter='Native transfer (*.'+ext+')',caption='New output only' if mode<=3 else 'Import into backup scene')
        if not chosen:return None
        path=chosen[0]
    message='运行 '+row['label']+' / '+(c['label'] or event)+'。原功能可能修改场景、全局设置或文件。\n'
    message+='本候选已有文件导出拒绝覆盖；偏好/userSetup/快照删除保存副本，但文件与退出不由 Maya Undo 恢复。'
    if cmds.confirmDialog(title='Malcolm341 原功能',message=message,button=['执行','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')!='执行':return None
    result=Malcolm341MegaPackTool().run(action='run_button',button_id=button,event=event,file_path=path,confirm_native=True)
    if not result.success:cmds.warning(result.message)
    return result
