from functools import wraps
from pathlib import Path
import re
from maya import cmds as real,mel as real_mel

WRITES={'sets','group','addAttr','setAttr','delete','hide','showHidden','polyHole','polyOptions'}
UI={'window','deleteUI','iconTextButton','popupMenu','menuItem','menu','image','button','textField'}


def flatten(values):
    for v in values:
        if isinstance(v,(list,tuple,set)): yield from flatten(v)
        elif isinstance(v,str): yield v


class Commands:
    def __getattr__(self,name):
        fn=getattr(real,name)
        @wraps(fn)
        def invoke(*args,**kwargs):
            from . import runtime as r
            query=kwargs.get('query') or kwargs.get('q') or kwargs.get('exists') or kwargs.get('ex')
            if name in ('ls','listRelatives','filterExpand') and args and (args[0] is None or args[0]==[]): return []
            if name in UI:
                prefix='mtbFCM_'
                # All explicit native UI names use a private prefix, including
                # dynamic per-set controls. Anonymous Maya-generated ids stay.
                if args and isinstance(args[0],str) and not '|' in args[0] and not args[0].startswith(prefix):
                    args=(prefix+args[0],)+args[1:]
                for key in ('c','command','postMenuCommand'):
                    if key in kwargs and isinstance(kwargs[key],str):
                        text=kwargs[key].rstrip(',')
                        if text=="cmds.warning('Show or Hide all WIP')": text='ShowOrHideAllSetsButton()'
                        kwargs[key]=r.callback(text)
                if 'enterCommand' in kwargs and isinstance(kwargs['enterCommand'],str):
                    text=kwargs['enterCommand'].replace('\\"','"')
                    hit=re.fullmatch(r'cmds\.setFocus\("([^"\n]+)"\)',text)
                    if not hit: raise ValueError('Invalid native focus callback')
                    target=hit.group(1); kwargs['enterCommand']=lambda *unused: real.setFocus(target)
                for key in ('i','image','image1'):
                    value=kwargs.get(key)
                    if isinstance(value,str) and value.startswith('Icons_Hider/'):
                        leaf=value.rsplit('/',1)[-1].rsplit(':',1)[-1]
                        path=Path(__file__).with_name('upstream')/'Icons_Hider'/leaf
                        if not path.is_file(): raise ValueError('Original icon missing: '+leaf)
                        kwargs[key]=str(path)
                if real.about(batch=True):
                    # Isolated algorithm checks cannot create real native UI;
                    # actual show_ui is independently rejected by preflight.
                    if name=='window' and query: return False
                    if name in ('deleteUI','iconTextButton'): return None
            if name in ('hide','showHidden','polyHole','polyOptions') and (not args or args[0] is None or args[0]==[]): return None
            if name in WRITES and not query:
                try:
                    r.require_active()
                    if name=='setAttr' and args and isinstance(args[0],str) and args[0].startswith('.'):
                        args=(r.names(r.current_system())[r.SETTINGS]+args[0],)+args[1:]
                    if name=='group' or name=='sets' and (kwargs.get('empty') or kwargs.get('em')):
                        target=kwargs.get('name') or kwargs.get('n')
                        if target not in r.names(r.current_system()).values() or real.objExists(target): raise ValueError('Only exact new private system nodes may be created')
                        result=fn(*args,**kwargs)
                        real.addAttr(result,longName=r.OWNER,dataType='string'); real.setAttr(result+'.'+r.OWNER,r.current_system(),type='string')
                        uid=real.ls(result,uuid=True)[0]; r._ALLOWED.add(uid); r._PLAN['owned_ids'].append(uid)
                        return result
                    values=list(flatten(args[:1] if name in ('setAttr','addAttr') else args))
                    if name=='sets':
                        target=kwargs.get('forceElement') or kwargs.get('fe') or kwargs.get('remove') or kwargs.get('rm')
                        if target:
                            values.append(target)
                            if not args or args[0] is None or args[0]==[]:
                                if args: return None
                                values+=real.ls(selection=True,long=True,flatten=True) or []
                    if name=='delete' and not values: raise ValueError('No implicit delete')
                    for value in values:
                        if name in ('setAttr','addAttr'): value=value.split('.',1)[0]
                        match,node,uid=r.resolve(value)
                        if uid not in r._ALLOWED: raise ValueError('Write outside preflighted Hider scope: '+value)
                        if name=='delete' and uid not in r._PLAN['owned_ids']: raise ValueError('Only private system set/settings nodes may be deleted')
                        if name=='delete':
                            for child in real.listRelatives(node,allDescendents=True,fullPath=True) or []:
                                if real.ls(child,uuid=True)[0] not in r._PLAN['owned_ids']: raise ValueError('Deletion contains foreign child')
                            for dest in real.listConnections(node,source=False,destination=True) or []:
                                if real.ls(dest,uuid=True)[0] not in r._PLAN['owned_ids']: raise ValueError('Deletion contains foreign consumer')
                        if real.referenceQuery(node,isNodeReferenced=True) or any(real.lockNode(node,query=True,lock=True) or []): raise ValueError('Referenced/locked writable node')
                    return fn(*args,**kwargs)
                except Exception as e:
                    r._ERRORS.append(str(e)); raise
            return fn(*args,**kwargs)
        return invoke


cmds=Commands()
mel=real_mel
