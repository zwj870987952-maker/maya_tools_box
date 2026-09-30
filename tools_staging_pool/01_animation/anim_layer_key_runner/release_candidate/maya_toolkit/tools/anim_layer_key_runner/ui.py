"""Native UI callbacks dispatch through the standard framework contract."""
import maya.cmds as cmds
from .native_ui import AnimLayerKeyRunnerUI as NativeUI


class AnimLayerKeyRunnerUI(NativeUI):
    def __init__(self, tool):
        super().__init__()
        self.tool = tool

    def _dispatch(self, dry_run):
        args = dict(command=cmds.textField(self.cmd_field, query=True, text=True),
                    language='python' if cmds.radioButton(self.py_radio, query=True, select=True) else 'mel',
                    layer=self._get_ui_layer_target(),
                    only_in_playback=cmds.checkBox(self.range_checkbox, query=True, value=True))
        result = self.tool.run(dry_run=dry_run, **args)
        cmds.text(self.info_text, edit=True, label=result.message)
        print(result.to_json())
        if dry_run or not result.success:
            cmds.confirmDialog(title='关键帧预检' if dry_run else '执行报告',
                               message=result.message + '\n' + str(result.data.get('frames', [])) + '\n' + '\n'.join(result.errors),
                               button=['确定'])

    def _on_inspect(self, *_):
        self._dispatch(True)

    def _on_execute(self, *_):
        self._dispatch(False)


def show_ui(tool=None):
    if cmds.about(batch=True):
        raise RuntimeError('Open the window in interactive Maya')
    if tool is None:
        from .tool import AnimLayerKeyRunnerTool
        tool = AnimLayerKeyRunnerTool()
    ui = AnimLayerKeyRunnerUI(tool)
    ui.show()
    return ui
