import json
from pathlib import Path
from . import scene

PACKAGE = Path(__file__).parent
PREF_FLAGS = ['f', 'pt', 'pc', 'chr', 'ft', 'mel', 'd', 'ut', 'un', 'vt', 'vn', 'uch', 'ucr', 'cht', 'es', 'mrt']
_ACTIVE = False
_DRAW = None


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部写场景过程仅允许 SpeedLinesTool.run()')


def preferences():
    cmds = scene.maya()
    return {key: cmds.nurbsToPolygonsPref(query=True, **{key: True}) for key in PREF_FLAGS}


def load_suite():
    import maya.mel as mel
    path = PACKAGE / 'runtime.mel'
    catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
    marker = catalog['runtime_procedures'][0]
    if not str(mel.eval('whatIs ' + marker + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    for name in catalog['runtime_procedures']:
        if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
            raise RuntimeError('MEL来源冲突: ' + name)
    return {'source': path.as_posix(), 'procedures': catalog['runtime_procedures']}


def remove_plane_only():
    require_active()
    cmds = scene.maya()
    plane = owned_draw_plane()
    if plane:
        cmds.makeLive(none=True)
        cmds.delete(plane)


def owned_draw_plane():
    if _DRAW:
        node = scene.find(_DRAW['uuid'])
        return scene.safe_plane(node) if node else None
    return scene.plane()


def stop_draw():
    global _DRAW
    cmds = scene.maya()
    plane = owned_draw_plane()
    data = scene.read_draw(plane) if plane else (_DRAW or {})
    if _DRAW:
        for key in ('job', 'undo_job'):
            if _DRAW.get(key) and cmds.scriptJob(exists=_DRAW[key]):
                cmds.scriptJob(kill=_DRAW[key], force=True)
    remove_plane_only()
    if data:
        live = [scene.find(value) for value in data.get('live', [])]
        live = [node for node in live if node]
        cmds.makeLive(live) if live else cmds.makeLive(none=True)
        if not cmds.about(batch=True):
            context = data.get('context', 'moveSuperContext')
            valid = isinstance(context, str) and bool(context) and cmds.contextInfo(context, exists=True)
            cmds.setToolTo(context if valid else 'moveSuperContext')
    _DRAW = None
    if cmds.button('mtbSL_bh_toggleDrawMode', exists=True):
        cmds.button('mtbSL_bh_toggleDrawMode', edit=True, label='Enter Drawing Mode', backgroundColor=[.2, .2, .2])


def execute(args):
    global _ACTIVE, _DRAW
    import maya.mel as mel
    cmds = scene.maya()
    load_suite()
    before = {scene.identity(node) for node in cmds.ls(long=True) or []}
    saved_selection = cmds.ls(selection=True, long=True) or []
    saved_time = cmds.currentTime(query=True)
    saved_preferences = preferences() if args['action'] == 'geometry' else None
    draw_state = {'context': cmds.currentCtx(), 'live': [scene.identity(node) for node in (cmds.ls(live=True, long=True) or [])]} if args['action'] == 'start_draw' else None
    result_selection = None
    success = False
    try:
        _ACTIVE = True
        mel.eval('global int $mtbSL_options[]; global int $mtbSL_consumeCurves; global string $mtbSL_camera; $mtbSL_options = {' + ','.join(str(int(args[key])) for key in ('high_detail', 'on_layer', 'hold_two')) + '}; $mtbSL_consumeCurves = ' + str(int(args['consume_curves'])) + '; $mtbSL_camera = ' + json.dumps(args['camera'], ensure_ascii=False) + ';')
        if args['action'] == 'stop_draw':
            stop_draw()
        elif args['action'] in ('start_draw', 'draw_depth', 'reset_depth'):
            cmds.textField('mtbSL_bh_SL_cameraField', edit=True, text=args['camera'])
            if args['action'] == 'start_draw':
                cmds.menuItem('mtbSL_bhsl_toolMode', edit=True, checkBox=args['ep_tool'])
                cmds.floatField('mtbSL_bhSL_depthField', edit=True, value=args['depth'])
                mel.eval('mtbSL_bh_drawPlane();')
                node = cmds.ls(scene.PLANE, long=True)[0]
                scene.write_draw(node, draw_state)
                _DRAW = dict(draw_state, uuid=scene.identity(node), job=None)
                if args['ep_tool']:
                    from .ui import tool_changed
                    _DRAW['job'] = cmds.scriptJob(runOnce=True, parent='mtbSL_bh_speedLinesUI', event=['ToolChanged', tool_changed])
                from .ui import undo_changed
                _DRAW['undo_job'] = cmds.scriptJob(parent='mtbSL_bh_speedLinesUI', event=['Undo', undo_changed])
                cmds.button('mtbSL_bh_toggleDrawMode', edit=True, label='Exit Drawing Mode', backgroundColor=[.7, .7, .7])
            elif args['action'] == 'draw_depth':
                cmds.floatSliderGrp('mtbSL_bhSL_drawDepthSlider', edit=True, value=args['depth'])
                mel.eval('mtbSL_bhSL_drawDepth();')
            else:
                mel.eval('mtbSL_bhSL_drawDepthReset();')
        else:
            cmds.select(args['objects'], replace=True)
            names = {'geometry': 'bh_geoFrom2Curves', 'flip': 'bh_reverseNormals', 'simplify': 'bh_simplify', 'smooth': 'bh_smoothCurves', 'key_visibility': 'bh_keyVisibility'}
            if args['action'] == 'geometry':
                mel.eval('mtbSL_bh_setUpConvertPrefs();')
            mel.eval('mtbSL_' + names[args['action']] + '();')
            if args['action'] == 'geometry':
                result_selection = cmds.ls(selection=True, long=True) or []
        success = True
        created = [node for node in cmds.ls(long=True) or [] if scene.identity(node) not in before]
        warnings = []
        if args['action'] == 'geometry' and args['consume_curves']:
            warnings.append('原流程删除两输入曲线；Maya Undo可撤回，转换偏好已恢复。')
        if args['action'] == 'key_visibility':
            warnings.append('原currentTime转整数，并写前后帧visibility键，可能覆盖已有键。')
        return {'action': args['action'], 'created_nodes': created, 'selection': cmds.ls(selection=True, long=True) or [],
                'draw_plane': scene.plane() if args['action'] in ('start_draw', 'draw_depth', 'reset_depth') else None,
                'owned_script_job': _DRAW.get('job') if _DRAW else None, 'warnings': warnings}
    finally:
        restore_errors = []
        def restore(callback):
            try:
                callback()
            except Exception as error:
                restore_errors.append(str(error))
        try:
            # An error after plane creation still records our own new node for stop/Undo.
            if args['action'] == 'start_draw' and not success:
                found = cmds.ls(scene.PLANE, long=True) or []
                if len(found) == 1 and scene.identity(found[0]) not in before:
                    scene.write_draw(found[0], draw_state)
                    _DRAW = dict(draw_state, uuid=scene.identity(found[0]), job=None)
                    stop_draw()
            if args['action'] == 'geometry' and args['on_layer'] and cmds.objExists(scene.LAYER) and scene.identity(scene.LAYER) not in before:
                scene.mark(scene.LAYER)
            if saved_preferences is not None:
                restore(lambda: cmds.nurbsToPolygonsPref(**saved_preferences))
            restore(lambda: cmds.currentTime(saved_time))
            if args['action'] not in ('start_draw', 'draw_depth', 'reset_depth') or not success:
                selection = result_selection if success and result_selection is not None else saved_selection
                existing = [node for node in selection if cmds.objExists(node)]
                restore(lambda: cmds.select(existing, replace=True) if existing else cmds.select(clear=True))
        finally:
            _ACTIVE = False
        if restore_errors:
            raise RuntimeError('恢复状态失败，请检查偏好/时间/选择并Undo: ' + '; '.join(restore_errors))
