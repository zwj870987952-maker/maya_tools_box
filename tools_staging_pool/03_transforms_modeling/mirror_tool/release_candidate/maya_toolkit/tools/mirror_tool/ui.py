from maya import cmds
from .native import MirrorTool
from .tool import opposite


class MirrorCandidateUI(MirrorTool):
    def __init__(self,tool):
        self.tool=tool; self.window_name='mtbMirrorCandidate'; self.window_title='镜像工具候选'
        self.left_identifier='_L'; self.right_identifier='_R'; self.create_ui()

    def parameters(self):
        self.update_naming_rules()
        return {'left':self.left_identifier,'right':self.right_identifier,'include_hierarchy':self.get_hierarchy_option(),'plane':self.get_mirror_plane(),'mode':self.get_mirror_function()}

    def execute_mirror(self,*args):
        result=self.tool.run(**self.parameters()); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        else: cmds.inViewMessage(amg='成功镜像 %d 个物体'%len(result.data['rows']),pos='midCenter',fade=True)
        return result

    def preflight(self,*args):
        result=self.tool.run(dry_run=True,**self.parameters()); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        return result

    def get_opposite_object(self,obj_name):
        self.update_naming_rules(); return opposite(obj_name,self.left_identifier,self.right_identifier)

    def mirror_transform(self,source_obj,target_obj,mirror_plane,mirror_function):
        return self.tool.run(pairs=[{'source':source_obj,'target':target_obj}],plane=mirror_plane,mode=mirror_function).success
