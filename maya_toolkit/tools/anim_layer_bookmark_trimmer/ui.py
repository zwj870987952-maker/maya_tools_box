"""Original native Maya controls, with all actions routed through BaseMayaTool."""
import maya.cmds as cmds
from .native_ui import BookmarkTrimmerUI as NativeUI


class BookmarkTrimmerUI(NativeUI):
    def __init__(self, tool):
        super().__init__()
        self.tool = tool

    def _dispatch(self, action, dry_run):
        t, r, s, other, priority = self._get_channel_settings()
        args = dict(action=action, layer=self._get_selected_layer(), scope=self._get_scope(),
                    include_translate=t, include_rotate=r, include_scale=s,
                    include_others=other, channel_box_priority=priority)
        if action == 'trim':
            args['ensure_keys_at_bounds'] = cmds.checkBox(self.ensure_keys_cb, query=True, value=True)
        else:
            args.update(mode=self._get_opt_mode(),
                        strength=cmds.floatSliderGrp(self.strength_slider, query=True, value=True),
                        bias=cmds.floatSliderGrp(self.bias_slider, query=True, value=True),
                        ease_bounds=cmds.checkBox(self.ease_bounds_cb, query=True, value=True))
        result = self.tool.run(dry_run=dry_run, **args)
        self._log(result.message + ('\n' + '\n'.join(result.warnings) if result.warnings else ''))

    def _on_dry_run_trim_clicked(self, *args):
        self._dispatch('trim', True)

    def _on_trim_clicked(self, *args):
        self._dispatch('trim', False)

    def _on_dry_run_optimize_clicked(self, *args):
        self._dispatch('optimize', True)

    def _on_optimize_clicked(self, *args):
        self._dispatch('optimize', False)


def show_ui(tool):
    if cmds.about(batch=True):
        raise RuntimeError('Open this UI in an interactive Maya session')
    # Explicit preparation at UI launch, never inside validate/dry_run.
    if not cmds.pluginInfo('timeSliderBookmark', query=True, loaded=True):
        cmds.loadPlugin('timeSliderBookmark')
    ui = BookmarkTrimmerUI(tool)
    ui.show()
    return ui
