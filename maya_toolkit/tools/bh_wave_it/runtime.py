import json
from pathlib import Path

PACKAGE = Path(__file__).parent
_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('内部写场景过程仅允许WaveItTool.run()')


def load_suite():
    import maya.mel as mel
    path = PACKAGE / 'runtime.mel'
    names = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))['runtime_procedures']
    if not str(mel.eval('whatIs ' + names[0] + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    for name in names:
        if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
            raise RuntimeError('MEL来源冲突: ' + name)
    return {'source': path.as_posix(), 'procedures': names}


def execute(args):
    global _ACTIVE
    from maya import cmds, mel
    info = load_suite()
    if args['action'] == 'open_ui':
        mel.eval('mtbWI_bh_waveIt();')
        return dict(info, window='mtbWI_waveItUI')
    saved = cmds.ls(selection=True, long=True) or []
    time = cmds.currentTime(query=True)
    try:
        _ACTIVE = True
        # Use exact argument order, independent of Maya active-selection ordering.
        objects = '{' + ','.join(json.dumps(n, ensure_ascii=False) for n in args['objects']) + '}'
        attrs = '{' + ','.join(json.dumps(n) for n in args['custom_attributes']) + '}'
        flags = [axis in args['rotate_axes'] for axis in 'XYZ'] + [axis in args['translate_axes'] for axis in 'XYZ'] + [bool(args['custom_attributes'])]
        numeric = [args[k] for k in ('amplitude', 'frequency', 'phase', 'base_offset')]
        # Effective preset/invert values were already normalized; invoke waveVal directly.
        mel.eval('global string $mtbWI_objects[]; global string $mtbWI_attrs[]; global int $mtbWI_flags[]; global float $mtbWI_values[]; $mtbWI_objects=' + objects + '; $mtbWI_attrs=' + attrs + '; $mtbWI_flags={' + ','.join(str(int(v)) for v in flags) + '}; $mtbWI_values={' + ','.join(str(float(v)) for v in numeric) + '};')
        mel.eval('mtbWI_' + ('bh_baseOffset' if args['action'] == 'base_offset' else 'bh_waveVal') + '();')
        rows = [dict(row, after=cmds.getAttr(row['plug'])) for row in args['operations']]
        return {'action': args['action'], 'ordered_objects': args['objects'], 'operations': rows, 'effective_frequency': args['frequency'], 'effective_phase': args['phase']}
    finally:
        errors = []
        try:
            for callback in (lambda: cmds.currentTime(time), lambda: cmds.select([n for n in saved if cmds.objExists(n)], replace=True) if saved else cmds.select(clear=True)):
                try:
                    callback()
                except Exception as error:
                    errors.append(str(error))
        finally:
            _ACTIVE = False
        if errors:
            raise RuntimeError('恢复时间/选择失败，请检查并Undo: ' + '; '.join(errors))
