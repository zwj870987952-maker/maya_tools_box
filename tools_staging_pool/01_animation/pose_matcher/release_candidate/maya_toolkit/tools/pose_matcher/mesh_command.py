"""Load our undoable mesh command only for a real mesh write, never dry_run."""
import json
from pathlib import Path
from maya import cmds

COMMAND = 'mtkPoseCandidateMesh'
PLUGIN = Path(__file__).with_name('mesh_plugin.py')


def create(v, uv, vt, vn, name):
    from .runtime import require_scope
    require_scope()
    path = str(PLUGIN.resolve())
    if not cmds.pluginInfo(path, q=True, loaded=True):
        if hasattr(cmds, COMMAND):
            raise ValueError('Private mesh command name is already registered')
        cmds.loadPlugin(path, quiet=True)
    payload = dict(v=v.tolist(), uv=uv.tolist(), vt=vt.tolist(), vn=vn.tolist(), name=name)
    result = getattr(cmds, COMMAND)(json.dumps(payload, allow_nan=False, ensure_ascii=True))
    if isinstance(result, (list, tuple)) and len(result) == 1:
        result = result[0]
    if not isinstance(result, str) or not cmds.objExists(result):
        raise ValueError('Mesh command did not return one existing transform')
    return result
