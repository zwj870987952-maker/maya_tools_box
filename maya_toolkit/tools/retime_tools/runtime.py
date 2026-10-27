"""Checked whole original business engine; no Qt construction in headless tests."""
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import re
import tempfile
import uuid

_depth = 0
_window = None
WRITE = {'addAttr','deleteAttr','setAttr','connectAttr','disconnectAttr','delete','createNode','curve','parent','rename','cutKey','pasteKey','setKeyframe','bakeResults','copyKey','select'}


class Commands:
    def __getattr__(self, name):
        import maya.cmds as cmds
        original = getattr(cmds, name)
        def checked(*a, **k):
            writing = name in WRITE or name in ('keyTangent','setInfinity') and not (k.get('q') or k.get('query'))
            if writing and not _depth:
                raise RuntimeError('Original scene writers require the checked Retime scope: ' + name)
            return original(*a, **k)
        return checked


engine_cmds = Commands()


class UICommands:
    def __getattr__(self, name):
        import maya.cmds as cmds
        if name == 'rename':
            def rename(node, new_name):
                from .ui_bridge import call
                return call(action='rename', controller=node, name=new_name)['controller']
            return rename
        if name in WRITE - {'select'}:
            return getattr(engine_cmds, name)
        return getattr(cmds, name)


ui_cmds = UICommands()


@contextmanager
def scope():
    global _depth
    import maya.cmds as cmds
    old = (cmds.ls(sl=True, long=True) or [], cmds.currentTime(q=True), cmds.autoKeyframe(q=True, state=True), cmds.namespaceInfo(currentNamespace=True, absoluteName=True))
    _depth += 1
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        yield
    finally:
        _depth -= 1
        cmds.currentTime(old[1])
        cmds.namespace(setNamespace=old[3])
        cmds.autoKeyframe(state=old[2])
        live = [n for n in old[0] if cmds.objExists(n)]
        cmds.select(live, replace=True) if live else cmds.select(clear=True)


def node(name):
    import maya.cmds as cmds
    found = cmds.ls(name, long=True) or []
    if len(found) != 1 or '.' in name:
        raise ValueError('Unique node required: ' + name)
    return found[0]


def local(name):
    import maya.cmds as cmds
    if cmds.referenceQuery(name, isNodeReferenced=True) or any(cmds.lockNode(name, q=True, lock=True) or []):
        raise ValueError('Referenced/locked node: ' + name)


def plug_free(plug, accept_anim=False):
    import maya.cmds as cmds
    local(plug.split('.')[0])
    if cmds.getAttr(plug, lock=True):
        raise ValueError('Locked plug: ' + plug)
    for upstream in cmds.listConnections(plug, s=True, d=False) or []:
        if not accept_anim or not cmds.nodeType(upstream).startswith('animCurveT'):
            raise ValueError('Unexpected driver: ' + plug)


def curves_for(nodes):
    import maya.cmds as cmds
    answer = set()
    for n in nodes:
        if cmds.nodeType(n).startswith('animCurveT'):
            answer.add(n)
        else:
            for h in cmds.listHistory(n, pruneDagObjects=False, leaf=False, levels=2) or []:
                if cmds.nodeType(h).startswith('animCurveT'):
                    answer.add(h)
    return sorted(answer)


def read_keys(path):
    p = Path(path).expanduser().resolve()
    if not p.is_file() or p.stat().st_size > 5_000_000 or p.suffix.lower() not in ('.json', '.txt', '.ascii'):
        raise ValueError('Existing bounded .json/.txt/.ascii input required')
    if p.suffix.lower() == '.json':
        data = json.loads(p.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            raise ValueError('Original JSON format is a frame:value object')
        rows = [(float(k), float(v)) for k,v in data.items()]
    else:
        rows = []
        for i, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(), 1):
            if not line.strip():
                continue
            values = line.split()
            if len(values) not in (1,2):
                raise ValueError('One or two columns required')
            rows.append((float(i), float(values[0])) if len(values)==1 else tuple(map(float,values)))
    if not 2 <= len(rows) <= 10000 or len({r[0] for r in rows}) != len(rows) or any(not all(math.isfinite(v) and abs(v)<=1e7 for v in r) for r in rows):
        raise ValueError('Unique finite key times and values required, 2..10000 rows')
    return str(p), sorted(rows)


def controller_keys(c):
    import maya.cmds as cmds
    attr = c+'.timeWarp_offline' if cmds.getAttr(c+'.retimeState') == 2 else c+'.timeWarp'
    t = cmds.keyframe(attr, q=True, timeChange=True) or []
    v = cmds.keyframe(attr, q=True, valueChange=True) or []
    return list(zip(t,v))


def prepare(o):
    import maya.cmds as cmds
    action = o['action']
    plan = {'action':action, 'controller':None, 'curves':[], 'nodes':[], 'files':[], 'warnings':[]}
    if o['curves'] is not None and action not in ('connect','disconnect','clean_subframes'):
        raise ValueError('curves subset is supported only for connect/disconnect/clean_subframes')
    if action in ('open_ui','open_legacy_ui','close_ui','inspect'):
        plan['controllers'] = [n for n in cmds.ls(type='transform',long=True) or [] if cmds.objExists(n+'.timeWarp') and cmds.objExists(n+'.retimeState')]
        if action in ('open_ui','open_legacy_ui') and cmds.about(batch=True):
            raise ValueError('Original Qt UI requires interactive Maya')
        return plan
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_:]*', o['name']) or '::' in o['name']:
        raise ValueError('Safe Maya controller name required')
    if action=='create':
        if cmds.playbackOptions(q=True, animationEndTime=True) <= cmds.playbackOptions(q=True, animationStartTime=True):
            raise ValueError('Nonempty animation range required')
        return plan
    if action=='import_curve':
        plan['file'], plan['keys'] = read_keys(o['file'])
        return plan
    c = None
    if action != 'clean_subframes' or o['controller']:
        if not o['controller']:
            raise ValueError('Explicit controller required')
        c = node(o['controller'])
        local(c)
        legacy = cmds.objExists(c+'.shuffleData') and not cmds.objExists(c+'.retimeState')
        attrs = ('timeWarp','timeWarp_offline','store') if action=='update_legacy' or legacy and action in ('connect','disconnect') else ('timeWarp','timeWarp_offline','retimeState','store')
        for attr in attrs:
            if not cmds.objExists(c+'.'+attr) or cmds.getAttr(c+'.'+attr,lock=True):
                raise ValueError('Incomplete or locked retime controller')
        for attr in ('timeWarp','timeWarp_offline'):
            for src in cmds.listConnections(c+'.'+attr, s=True, d=False, plugs=True) or []:
                if not (cmds.nodeType(src.split('.')[0]).startswith('animCurveT') or src.endswith('.outTime') and cmds.nodeType(src.split('.')[0])=='time'):
                    raise ValueError('Unexpected controller driver')
                driver = src.split('.')[0]
                if cmds.nodeType(driver).startswith('animCurveT'):
                    local(driver)
                    for dst in cmds.listConnections(driver+'.output',s=False,d=True,plugs=True) or []:
                        if node(dst.split('.')[0])!=c or not dst.endswith(('.timeWarp','.timeWarp_offline')):
                            raise ValueError('Warp curve is shared with external destination')
        plan['controller'] = c
        plan['curves'] = sorted(set(cmds.listConnections(c+'.timeWarp',s=False,d=True,type='animCurve') or []))
        for dst in cmds.listConnections(c+'.timeWarp',s=False,d=True,plugs=True) or []:
            if not dst.endswith('.input') or not cmds.nodeType(dst.split('.')[0]).startswith('animCurveT'):
                raise ValueError('Warp has an external consumer outside animation inputs')
    if (action=='clean_subframes' and not c) or action=='connect':
        plan['nodes'] = [node(n) for n in (o['nodes'] or cmds.ls(sl=True,long=True) or [])]
        plan['curves'] = [node(n) for n in o['curves']] if o['curves'] else curves_for(plan['nodes'])
        if c:
            plan['curves'] = [n for n in plan['curves'] if n not in (cmds.listConnections([c+'.timeWarp',c+'.timeWarp_offline'],s=True,d=False) or [])]
    elif o['curves'] is not None:
        requested = [node(n) for n in o['curves']]
        if not set(requested).issubset({node(n) for n in plan['curves']}):
            raise ValueError('Curves must be connected to this controller')
        plan['curves'] = requested
    if action in ('connect','disconnect','bake','shuffle','clean_subframes') and not plan['curves']:
        raise ValueError('No applicable animated curves')
    for curve in plan['curves']:
        local(curve)
        if not cmds.nodeType(curve).startswith('animCurveT') or cmds.getAttr(curve+'.input',lock=True):
            raise ValueError('Editable time-input animCurve required')
        for src in cmds.listConnections(curve+'.input',s=True,d=False,plugs=True) or []:
            if not (c and src.endswith('.timeWarp') and node(src.split('.')[0])==c or src.endswith('.outTime') and cmds.nodeType(src.split('.')[0])=='time'):
                raise ValueError('Would replace another time driver: '+curve)
        for destination in cmds.listConnections(curve+'.output',s=False,d=True,plugs=True) or []:
            kind = cmds.nodeType(destination.split('.')[0])
            if kind.startswith('animBlend') or kind.endswith('Constraint'):
                raise ValueError('Layer/constraint destinations require separate adapter')
            plug_free(destination, accept_anim=True)
    if c and (action in ('bake','shuffle') or action=='state' and o['state']=='Invert'):
        keys = controller_keys(c)
        if len(keys)<2 or keys[-1][0]-keys[0][0]>10000:
            raise ValueError('Bounded keyed warp required')
        if action in ('shuffle',) or o['state']=='Invert':
            if cmds.getAttr(c+'.retimeState') == 2:
                raise ValueError('Enable controller before inverse operations')
            values = [cmds.getAttr(c+'.timeWarp',time=keys[0][0]+i*(keys[-1][0]-keys[0][0])/max(1,math.ceil((keys[-1][0]-keys[0][0])*10))) for i in range(math.ceil((keys[-1][0]-keys[0][0])*10)+1)]
            deltas = [b-a for a,b in zip(values,values[1:])]
            if not (all(v>1e-10 for v in deltas) or all(v < -1e-10 for v in deltas)):
                raise ValueError('Holds/nonmonotonic warp has no unique inverse; use bake instead')
    if action=='state' and o['state']=='Delete':
        children = cmds.listRelatives(c, children=True, fullPath=True) or []
        if any(cmds.nodeType(n)!='nurbsCurve' for n in children):
            raise ValueError('Controller contains external DAG children')
        for child in children:
            local(child)
            if cmds.listConnections(child, s=False,d=True):
                raise ValueError('Controller shape has external consumers')
        external = cmds.listConnections(c, s=False,d=True,plugs=True,connections=True) or []
        for src,dst in zip(external[::2],external[1::2]):
            if not src.endswith('.timeWarp') or not dst.endswith('.input') or not cmds.nodeType(dst.split('.')[0]).startswith('animCurveT'):
                raise ValueError('Controller has external consumers')
    if action=='update_legacy' and (not cmds.objExists(c+'.shuffleData') or cmds.objExists(c+'.retimeState')):
        raise ValueError('Explicit legacy controller required')
    if action=='export_curve':
        p = Path(o['file']).expanduser().resolve()
        if not p.parent.is_dir() or p.suffix.lower() not in ('.json','.txt','.ascii') or p.exists() and (not o['overwrite'] or not p.is_file()):
            raise ValueError('Explicit existing parent; no overwrite by default')
        plan['file'] = str(p)
        plan['keys'] = controller_keys(c)
        if not plan['keys']:
            raise ValueError('No warp keys to export')
        plan['warnings'].append('File writes cannot be undone by Maya Undo')
    if action=='bake':
        plan['warnings'].append('Original bake uses preserveOutsideKeys=False; outside keys can be removed')
    return plan


def inverse_lookup(self, target):
    if target not in self.value_time_cache:
        results = []
        for section in self.sections:
            pairs = sorted(section.items())
            for (a,av),(b,bv) in zip(pairs,pairs[1:]):
                if min(av,bv)-1e-9 <= target <= max(av,bv)+1e-9 and abs(bv-av)>1e-12:
                    t = a+(target-av)/(bv-av)*(b-a)
                    # Derivative of original warp scales key value tangent slope.
                    if not any(abs(t-r[0])<1e-7 for r in results):
                        results.append((t,(bv-av)/(b-a)))
        self.value_time_cache[target] = results
    return self.value_time_cache[target]


def disconnect(c, curves):
    import maya.cmds as cmds
    times = cmds.ls(type='time') or []
    if len(times)!=1:
        raise ValueError('Unique time node required')
    for curve in curves:
        if cmds.isConnected(c+'.timeWarp',curve+'.input'):
            cmds.disconnectAttr(c+'.timeWarp',curve+'.input')
            cmds.connectAttr(times[0]+'.outTime',curve+'.input')


def execute(o, plan):
    global _window
    import maya.cmds as cmds
    from .engine import CoreFunctions as Core, RetimeStates, RetimeLookup, ShuffleKeys
    action = o['action']
    if action=='inspect':
        return plan
    if action=='open_legacy_ui':
        from .legacy_mel import show_ui
        return show_ui()
    if action=='open_ui':
        from .native import Window
        if _window is not None:
            _window.close()
            _window.deleteLater()
        _window = Window()
        _window.display()
        return {'window':'mtkRetimeCandidateWindow'}
    if action=='close_ui':
        if _window is not None:
            _window.close()
            _window.deleteLater()
            _window = None
        if cmds.window('mtkRTlegacy_timeWarp',exists=True):
            cmds.deleteUI('mtkRTlegacy_timeWarp',window=True)
        return {'closed':True}
    c = plan['controller']
    with scope():
        if action in ('create','import_curve'):
            c = Core.create_new_retime_controller_exec(o['name'])
            c = cmds.rename(c,o['name'])
            if action=='import_curve':
                cmds.cutKey(c+'.timeWarp',clear=True)
                for t,v in plan['keys']:
                    cmds.setKeyframe(c+'.timeWarp',time=t,value=v,inTangentType='linear',outTangentType='linear')
                for attr,value in (('pathToAscii',plan['file']),('shortName',Path(plan['file']).stem)):
                    cmds.addAttr(c,ln=attr,dt='string')
                    cmds.setAttr(c+'.'+attr,value,type='string')
        elif action=='connect':
            for curve in plan['curves']:
                if not cmds.isConnected(c+'.timeWarp',curve+'.input'):
                    cmds.connectAttr(c+'.timeWarp',curve+'.input',force=True)
        elif action=='disconnect':
            disconnect(c,plan['curves'])
        elif action=='state':
            if o['state'] in ('Disconnect','Delete'):
                disconnect(c,plan['curves'])
            Core.set_retime_controller_state(c,getattr(RetimeStates,o['state']))
            expected = RetimeStates.Enable if o['state'] in ('Reset','Disconnect') else getattr(RetimeStates,o['state'])
            if o['state']!='Delete' and cmds.getAttr(c+'.retimeState') != expected:
                raise RuntimeError('Original state transition fell back after an error; use Undo')
        elif action=='bake':
            Core.bake_retime_controller(c)
        elif action=='shuffle':
            original = RetimeLookup.getSingleKeyTimeLookup
            RetimeLookup.getSingleKeyTimeLookup = inverse_lookup
            before = set(cmds.ls(type='animCurve') or [])
            try:
                ShuffleKeys.process(c)
                disconnect(c,plan['curves'])
                if o['clean']:
                    Core.cleanSubframeKeys(curve_nodes=plan['curves'])
            finally:
                RetimeLookup.getSingleKeyTimeLookup = original
                # Only unconnected new temp curves created by this call.
                for temp in set(cmds.ls(type='animCurve') or [])-before:
                    if '_tempCurve' in temp and not cmds.listConnections(temp,s=False,d=True):
                        cmds.delete(temp)
        elif action=='clean_subframes':
            Core.cleanSubframeKeys(curve_nodes=plan['curves'])
        elif action=='rename':
            c = cmds.rename(c,o['name'])
        elif action=='update_legacy':
            Core.update_old_retime_curve(c)
        elif action=='export_curve':
            p = Path(plan['file'])
            content = json.dumps({str(t):v for t,v in plan['keys']},ensure_ascii=False,indent=2)+'\n' if p.suffix.lower()=='.json' else ''.join(f'{t:.17g} {v:.17g}\n' for t,v in plan['keys'])
            fd,tmp = tempfile.mkstemp(prefix='.retime_',dir=str(p.parent))
            try:
                with os.fdopen(fd,'w',encoding='utf-8',newline='\n') as f:
                    f.write(content)
                if o['overwrite']:
                    os.replace(tmp,p)
                else:
                    os.link(tmp,p)
            finally:
                if os.path.exists(tmp):
                    os.unlink(tmp)
    return {'controller':c if c and cmds.objExists(c) else None,'curves':plan['curves'],'file':plan.get('file'),'warnings':plan['warnings']}
