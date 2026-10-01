from maya import cmds as real,mel as real_mel
from functools import wraps

WRITES={'setAttr','addAttr','deleteAttr','setKeyframe','cutKey','pasteKey','copyKey','bufferCurve','keyframe','keyTangent','filterCurve','connectAttr','disconnectAttr','delete','parent','parentConstraint','pointConstraint','orientConstraint','aimConstraint','scaleConstraint','circle','curve','group','spaceLocator','createNode','rebuildCurve','pathAnimation','move','rotate','xform','ikHandle','rename','sets'}
CREATES={'circle','curve','group','spaceLocator','createNode','parentConstraint','pointConstraint','orientConstraint','aimConstraint','scaleConstraint','ikHandle','pathAnimation','setKeyframe','pasteKey','rebuildCurve','bufferCurve'}


class Commands:
    def __getattr__(self,name):
        callback=getattr(real,name)
        @wraps(callback)
        def invoke(*args,**kwargs):
            from . import runtime as r
            query=kwargs.get('query') or kwargs.get('q')
            if name=='undoInfo':
                return callback(*args,**kwargs) if query else None
            if r._ACTIVE:
                if r._API and name=='channelBox' and query:
                    return r._PLAN.get('attributes',r.TR)
                if r._API and name=='timeControl' and query:
                    return '0:1'
                if name=='getPanel' and kwargs.get('withFocus'):
                    return None
                if name in ('waitCursor','progressBar'):
                    return None
            if name in WRITES and not query:
                try:
                    r.check_write(name,args,kwargs)
                    # Upstream concatenates full DAG paths into names. Maya names
                    # are basenames: preserve meaning without treating | as path.
                    for key in ('name','n'):
                        if key in kwargs and isinstance(kwargs[key],str):
                            kwargs[key]=kwargs[key].replace('|','_').replace(':','_').lstrip('_')
                    before=r.all_ids() if name in CREATES else None
                    result=callback(*args,**kwargs)
                    if before is not None:
                        r.register_created(before)
                    return result
                except Exception as e:
                    r._ERRORS.append(str(e)); raise
            return callback(*args,**kwargs)
        return invoke


class Mel:
    def eval(self,command):
        from . import runtime as r
        if r._ACTIVE and r._API and '$gPlayBackSlider' in command:
            return 'mtbWsHeadlessPlayback'
        if r._ACTIVE and r._API and '$gChannelBoxName' in command:
            return 'mtbWsHeadlessChannels'
        return real_mel.eval(command)


cmds,mel=Commands(),Mel()
