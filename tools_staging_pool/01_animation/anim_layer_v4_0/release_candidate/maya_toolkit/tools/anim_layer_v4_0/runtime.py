"""Explicit intact MEL loading and guarded invocation; no import-time sourcing."""
import json
from .contracts import CATALOG, PACKAGE, mel_literal


def _origin(mel, procedure):
    return str(mel.eval('whatIs ' + json.dumps(procedure) + ';')).replace('\\', '/').casefold()


def load_suite(edition, force_reload=False, procedure=None):
    import maya.mel as mel
    path = PACKAGE / CATALOG['editions'][edition]['entry']
    marker = procedure or 'create_and_select_anim_layer'
    expected = path.as_posix().casefold()
    origin = _origin(mel, marker)
    if not force_reload and origin.endswith(expected):
        return {'edition': edition, 'source': path.as_posix(), 'source_executed': False, 'already_loaded': True}
    try:
        mel.eval('source ' + mel_literal(path.as_posix(), 'string') + ';')
    except Exception as error:
        raise RuntimeError('MEL source failed; global definitions/UI may already be changed: ' + str(error))
    if not _origin(mel, marker).endswith(expected):
        raise RuntimeError('Requested procedure was not loaded from this suite; check Maya MEL overrides')
    return {'edition': edition, 'source': path.as_posix(), 'source_executed': True, 'already_loaded': False}


def invoke(command, restore_runtime_state=True):
    import maya.cmds as cmds
    import maya.mel as mel
    previous_mode = cmds.evaluationManager(query=True, mode=True) if restore_runtime_state else None
    try:
        previous_suspend = cmds.refresh(query=True, suspend=True) if restore_runtime_state else None
    except Exception:
        previous_suspend = None
    restoration_errors = []
    result = None
    error = None
    try:
        result = mel.eval(command)
    except Exception as caught:
        error = str(caught)
    finally:
        if previous_mode:
            try:
                current_mode = cmds.evaluationManager(query=True, mode=True)
                if current_mode != previous_mode:
                    cmds.evaluationManager(mode=previous_mode[0])
            except Exception as caught:
                restoration_errors.append('evaluationManager: ' + str(caught))
        if previous_suspend is not None:
            try:
                if cmds.refresh(query=True, suspend=True) != previous_suspend:
                    cmds.refresh(suspend=previous_suspend)
            except Exception as caught:
                restoration_errors.append('refresh: ' + str(caught))
    return dict(return_value=result, error=error, restoration_errors=restoration_errors)
