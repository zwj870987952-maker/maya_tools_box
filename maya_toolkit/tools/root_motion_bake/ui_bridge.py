"""Original native UI callbacks share full batch API and ambiguity-aware discovery."""
from .tool import RootMotionBakeTool


def populate(self):
    from maya import cmds
    from .runtime import discover
    info=discover()
    self.object_groups={str(i):g for i,g in enumerate(info['groups'])}
    if info['groups']:
        g=info['groups'][0]
        for field,key in ((self.root_field,'root'),(self.center_field,'center'),(self.ring_field,'ring')):
            cmds.textField(field,e=True,text=g[key] or '')
    if info['ambiguous']:
        cmds.warning('自动扫描有重复匹配，请手动明确Root/质心/大环')


def workflow(self,*args):
    from maya import cmds
    root=cmds.textField(self.root_field,q=True,text=True).strip()
    center=cmds.textField(self.center_field,q=True,text=True).strip()
    ring=cmds.textField(self.ring_field,q=True,text=True).strip()
    groups=[{'root':root,'center':center,'ring':ring or None}] if root or center or ring else None
    t,r=self.get_constraint_axes()
    selected=cmds.radioButtonGrp(self.time_range_radio,q=True,select=True)==2
    result=RootMotionBakeTool().run(action='bake',groups=groups,translate_axes=t,rotate_axes=r,maintain_offset=cmds.checkBox(self.maintain_offset_cb,q=True,value=True),time_range='selected' if selected else 'timeline')
    if not result.success:
        cmds.warning(result.message+': '+str(result.errors))
    else:
        cmds.confirmDialog(title='完成',message='约束烘焙完成，处理 {} 组对象。'.format(len(result.data['groups'])),button=['确定'])
    return result


def get_range(self):
    from maya import cmds
    from .runtime import time_range
    from .tool import normalize
    selected=cmds.radioButtonGrp(self.time_range_radio,q=True,select=True)==2
    return time_range(normalize(time_range='selected' if selected else 'timeline'))


def install(cls):
    cls.original_execute_workflow=cls.execute_workflow
    cls.original_auto_populate_objects=cls.auto_populate_objects
    cls.original_get_time_range=cls.get_time_range
    cls.original_set_relative_transform=cls.set_relative_transform
    cls.execute_workflow=workflow
    cls.auto_populate_objects=populate
    cls.get_time_range=get_range
    from .runtime import relative_on_layer
    cls.set_relative_transform=relative_on_layer
