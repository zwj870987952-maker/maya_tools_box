"""Original controls with generation, clear and inspection routed through the API."""
import maya.cmds as cmds
from .native_ui import AnimLayerBookmarkUI as NativeUI


class AnimLayerBookmarkUI(NativeUI):
    def __init__(self, tool):
        super().__init__()
        self.tool = tool

    def _args(self):
        return dict(layer=self._get_selected_layer_mode(), palette_name=self._get_selected_palette_key(),
                    prefix=cmds.textField(self.prefix_field, query=True, text=True) or 'BM',
                    clear_existing=cmds.checkBox(self.clear_checkbox, query=True, value=True))

    def _report(self, result):
        self._set_status(result.message)
        print(result.to_json())

    def _on_inspect_keys(self, *_):
        args = self._args()
        inspection = self.tool.run(dry_run=True, action='inspect', **args)
        self._report(inspection)
        if inspection.success and len(inspection.data['keyframes']) >= 2:
            # Also show creation/deletion guards; a failed plan is never hidden.
            self._report(self.tool.run(dry_run=True, **args))

    def _on_clear_all(self, *_):
        self._report(self.tool.run(action='clear'))

    def _on_execute(self, *_):
        self._report(self.tool.run(**self._args()))


def show_ui(tool=None):
    if cmds.about(batch=True):
        raise RuntimeError('Open this window in an interactive Maya session')
    if not cmds.pluginInfo('timeSliderBookmark', query=True, loaded=True):
        cmds.loadPlugin('timeSliderBookmark')
    if tool is None:
        from .tool import AnimLayerKeyframeBookmarkTool
        tool = AnimLayerKeyframeBookmarkTool()
    ui = AnimLayerBookmarkUI(tool)
    ui.show()
    return ui
