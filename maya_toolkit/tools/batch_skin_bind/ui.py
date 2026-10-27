"""Original proxy UI plus explicit independent joint/mesh list capture."""
from maya import cmds
from .native_ui import CreateObjectsUI


class CandidateUI(CreateObjectsUI):
    def __init__(self, tool):
        super().__init__()
        self.tool = tool
        self.joints = []
        self.meshes = []

    def create_objects(self, *args):
        mode = ('joint', 'locator', 'cube')[cmds.optionMenu(self.object_type_option_menu, query=True, select=True) - 1]
        skin = cmds.checkBox(self.skinning_checkbox, query=True, value=True)
        result = self.tool.run(objects=cmds.ls(selection=True, long=True) or [], proxy_type=mode, skinning=skin, allow_source_key_removal=skin)
        if not result.success:
            cmds.warning(result.message + '; inspect and Undo any partial scene changes')
        return result

    def show_bind_ui(self, *args):
        name = 'stagingBatchJointMeshBind'
        if cmds.window(name, exists=True):
            cmds.deleteUI(name)
        cmds.window(name, title='Batch joint / mesh bind', widthHeight=(420, 320))
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='Capture ordered joints and meshes separately; one joint per mesh')
        self.joint_list = cmds.textScrollList(height=90)
        cmds.button(label='Capture joint selection', command=lambda *args: self._capture('joints'))
        self.mesh_list = cmds.textScrollList(height=90)
        cmds.button(label='Capture mesh selection', command=lambda *args: self._capture('meshes'))
        cmds.button(label='Bind pairs', command=self._bind)
        cmds.showWindow(name)

    def _capture(self, kind):
        values = cmds.ls(selection=True, long=True) or []
        setattr(self, kind, values)
        field = self.joint_list if kind == 'joints' else self.mesh_list
        cmds.textScrollList(field, edit=True, removeAll=True)
        if values:
            cmds.textScrollList(field, edit=True, append=values)

    def _bind(self, *args):
        if not self.joints or len(self.joints) != len(self.meshes):
            cmds.warning('Capture nonempty equal-length joint and mesh lists')
            return
        result = self.tool.run(action='bind', pairs=[{'joint': j, 'mesh': m} for j, m in zip(self.joints, self.meshes)])
        if not result.success:
            cmds.warning(result.message + '; inspect and Undo any partial binding')
        return result


def show_ui(tool):
    ui = CandidateUI(tool)
    ui.create_window()
    return ui
