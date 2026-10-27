"""Complete historical MEL UI, explicitly launched only in interactive Maya.

Its historical callbacks are kept for separate acceptance, not advertised as
the checked Python API. Source loading never launches an installer or a shelf.
"""
from pathlib import Path


def load_definitions():
    import maya.mel as mel
    path = Path(__file__).parent/'assets/legacy_timewarp.mel'
    mel.eval(path.read_text(encoding='utf-8'))
    return 'mtkRTlegacy_timeWarp'


def show_ui():
    import maya.cmds as cmds
    import maya.mel as mel
    if cmds.about(batch=True):
        raise RuntimeError('Historical MEL UI requires interactive Maya')
    load_definitions()
    mel.eval('mtkRTlegacy_timeWarp;')
    return {'window':'mtkRTlegacy_timeWarp','warnings':['Historical MEL callbacks require separate acceptance in a backup scene; use checked Python API for unattended scene operations']}


def connect_from_ui():
    from maya import mel
    from .ui_bridge import call
    controller = mel.eval('mtkRTlegacy_tw_getTimeWarpFromList()')
    return call(action='connect',controller=controller)
