from maya import cmds
from . import native
from .tool import DEFAULTS
DRY=False


def bind(tool):
    def dispatch(settings):
        params={key:settings[key] for key in DEFAULTS if key in settings}
        if settings.get('object_pairs'): params['pairs']=[{'source':source,'target':target} for source,target in settings['object_pairs']]
        result=tool.run(dry_run=DRY,**params); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        elif not DRY: cmds.inViewMessage(amg='对齐完成；修改源对象',pos='topCenter',fade=True)
        return result
    def preflight():
        global DRY
        DRY=True
        try: return native.execute_alignment()
        finally: DRY=False
    native.execute_alignment_core=dispatch
    native.align_selected_objects=lambda settings=None:dispatch(settings or native.alignment_settings)
    native.candidate_preflight=preflight
    native.create_alignment_window()
    return native.WINDOW_NAME
