"""Explicit original-source loading; restore runtime switches even after MEL errors."""
from .contracts import PACKAGE, CATALOG, mel_literal


def load_suite(procedure=None, force_reload=False):
    import maya.mel as mel
    path = PACKAGE/CATALOG['entry']
    marker = procedure or 'Mirror_tool_menue'
    def origin():
        return str(mel.eval('whatIs '+mel_literal(marker,'string')+';')).replace('\\','/').casefold()
    already = origin().endswith(path.as_posix().casefold())
    if force_reload or not already:
        try:
            mel.eval('source '+mel_literal(path.as_posix(),'string')+';')
        except Exception as error:
            raise RuntimeError('Original MEL source failed; definitions may be partially loaded: '+str(error))
    if not origin().endswith(path.as_posix().casefold()):
        raise RuntimeError('Procedure is overridden or missing after sourcing')
    # Installer does the same assignment; no shelf installer is executed.
    icon = PACKAGE/'upstream/icons/mirror_tool.bmp'
    mel.eval('global string $mirror_tool_icon_path; $mirror_tool_icon_path='+mel_literal(icon.as_posix(),'string')+';')
    return dict(source=path.as_posix(), icon=icon.as_posix(), source_executed=force_reload or not already)


def invoke(command):
    import maya.cmds as cmds
    import maya.mel as mel
    snapshots = [('evaluation', lambda:cmds.evaluationManager(query=True,mode=True), lambda v:cmds.evaluationManager(mode=v[0])),
                 ('refresh', lambda:cmds.refresh(query=True,suspend=True), lambda v:cmds.refresh(suspend=v))]
    if not cmds.about(batch=True):
        snapshots.append(('timeSlider', lambda:mel.eval('isTimeSliderVisible();'), lambda v:mel.eval('setTimeSliderVisible '+str(int(v))+';')))
    saved, errors = [], []
    for label, read, write in snapshots:
        try:
            saved.append((label, read, write, read()))
        except Exception as error:
            errors.append('Snapshot '+label+': '+str(error))
    value, error = None, None
    try:
        value = mel.eval(command)
        # Maya returns a vector as a tuple; ToolResult JSON expects array.
        if isinstance(value, tuple):
            value = list(value)
    except Exception as caught:
        error = str(caught)
    finally:
        for label, read, write, old in saved:
            try:
                if read()!=old:
                    write(old)
            except Exception as caught:
                errors.append('Restore '+label+': '+str(caught))
    return dict(return_value=value, error=error, runtime_state_errors=errors)
