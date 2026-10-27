import json
from pathlib import Path

PACKAGE = Path(__file__).parent
_ACTIVE = False


def require_active():
    if not _ACTIVE:
        raise RuntimeError('请通过 LocalNudgeTool.run() 调用内部写场景过程')


def load_suite():
    import maya.mel as mel
    path = PACKAGE / 'runtime.mel'
    catalog = json.loads((PACKAGE / 'catalog.json').read_text(encoding='utf-8'))
    marker = catalog['runtime_procedures'][0]
    if not str(mel.eval('whatIs ' + marker + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
        mel.eval('source ' + json.dumps(path.as_posix(), ensure_ascii=False) + ';')
    for name in catalog['runtime_procedures']:
        if not str(mel.eval('whatIs ' + name + ';')).replace('\\', '/').casefold().endswith(path.as_posix().casefold()):
            raise RuntimeError('过程来源冲突: ' + name)
    return {'source': path.as_posix(), 'procedures': catalog['runtime_procedures']}


def execute(args):
    global _ACTIVE
    import maya.cmds as cmds
    import maya.mel as mel
    load_suite()
    selection = cmds.ls(selection=True, long=True) or []
    try:
        _ACTIVE = True
        mel.eval('global float $mtbLN_amount; global int $mtbLN_mods; $mtbLN_amount = ' + repr(float(args['amount'])) + '; $mtbLN_mods = ' + str(4 * int(args['ctrl']) + 8 * int(args['alt'])) + ';')
        cmds.select(args['objects'], replace=True)
        name = 'mtbLN_bh_localNudgeIt' if args['channel'] == 'translate' else 'mtbLN_bh_localNudgeRotIt'
        mel.eval(name + '(' + json.dumps(args['axis']) + ',' + json.dumps(args['direction']) + ');')
    finally:
        _ACTIVE = False
        existing = [node for node in selection if cmds.objExists(node)]
        cmds.select(existing, replace=True) if existing else cmds.select(clear=True)
