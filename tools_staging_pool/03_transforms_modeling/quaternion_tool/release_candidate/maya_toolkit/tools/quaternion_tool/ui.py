from maya import cmds
from .native import QuaternionToolUI,Quaternion


class QuaternionCandidateUI(QuaternionToolUI):
    def __init__(self,tool):
        self.tool=tool; self.window_name='mtbQuaternionToolWindow'; self.title='四元数工具候选'; self.size=(400,600)
        self.current_quaternion=Quaternion(); self.create_ui()

    def read(self,*fields): return [cmds.floatField(getattr(self,f),query=True,value=True) for f in fields]

    def invoke(self,action,dry=False,**kwargs):
        result=self.tool.run(action=action,dry_run=dry,**kwargs); print(result.to_dict())
        if not result.success: cmds.warning(result.message)
        return result

    def create(self,action,**kwargs):
        result=self.invoke(action,**kwargs)
        if result.success:
            self.current_quaternion=Quaternion(result.data['quaternion'])
            cmds.textField(self.current_quat_text,edit=True,text=str(self.current_quaternion))
        return result

    def create_from_euler(self,*args): return self.create('from_euler',euler=self.read('euler_x','euler_y','euler_z'))
    def create_from_axis_angle(self,*args): return self.create('from_axis_angle',axis=self.read('axis_x','axis_y','axis_z'),angle=self.read('angle')[0])
    def create_from_vector(self,*args): return self.create('from_components',quaternion=self.read('quat_x','quat_y','quat_z','quat_w'))
    def create_from_to_rotation(self,*args): return self.create('from_to',from_direction=self.read('from_x','from_y','from_z'),to_direction=self.read('to_x','to_y','to_z'))

    def rotate_vector(self,*args):
        result=self.invoke('rotate_vector',quaternion=self.current_quaternion.xyzw(),vector=self.read('vec_x','vec_y','vec_z'))
        if result.success: cmds.textField(self.rotated_vector,edit=True,text=' '.join('%.4f'%v for v in result.data['rotated_vector']))
        return result

    def get_euler(self,*args):
        result=self.invoke('to_euler',quaternion=self.current_quaternion.xyzw())
        if result.success: cmds.textField(self.euler_result,edit=True,text=' '.join('%.2f'%v for v in result.data['euler_degrees']))
        return result

    def apply_to_selection(self,*args): return self.invoke('apply',quaternion=self.current_quaternion.xyzw())
    def preflight(self,*args): return self.invoke('apply',True,quaternion=self.current_quaternion.xyzw())
