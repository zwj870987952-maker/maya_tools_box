"""Original 7-button GUI, backed by current scene session on every mutation."""
from maya import cmds
from .tool import PoseTransferRemoteTool


class SessionButtons:
    def __init__(self):
        self.root_controller=None
        self.controllers=None

    def call(self, **kw):
        result=PoseTransferRemoteTool().run(**kw)
        if not result.success:
            cmds.warning(result.message+': '+'; '.join(result.errors))
        return result

    def get_selected_root(self):
        selected=cmds.ls(sl=True,long=True) or []
        if len(selected)!=1:
            cmds.warning('请选择一个ROOT控制器')
            return False
        from .runtime import whole
        self.root_controller=whole(selected[0])
        self.controllers=None
        return True

    def get_all_controllers(self):
        if not self.root_controller:
            cmds.warning('先设置ROOT')
            return False
        result=self.call(action='detect',root=self.root_controller)
        if result.success:
            self.controllers=result.data['controllers']
        return result.success

    def manual_select_and_create_locators(self):
        if not self.root_controller:
            cmds.warning('先设置ROOT')
            return False
        result=cmds.confirmDialog(title='手动选择控制器',message='使用当前选择创建姿态定位器？',button=['确定','取消'],defaultButton='取消',cancelButton='取消',dismissString='取消')
        if result!='确定':
            return False
        selected=cmds.ls(sl=True,long=True) or []
        if not selected:
            return False
        self.controllers=selected
        return self.create_locators_and_record_pose()

    def create_locators_and_record_pose(self):
        return self.call(action='capture',root=self.root_controller,controllers=self.controllers).success

    def move_locators_to_new_root_position(self):
        return self.call(action='shift').success

    def apply_pose_from_locators(self):
        allow=cmds.checkBox('mtkPoseTransferCandidateAllowReferences',q=True,value=True)
        return self.call(action='apply',allow_reference_edits=allow).success

    def cleanup_locators(self):
        return self.call(action='cleanup').success
