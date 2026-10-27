from .runtime import require_scope, safe_layer_name
'\nMaya 约束烘焙工具\n功能：质心约束root，烘焙动画，创建动画层并记录相对位置\n作者：Assistant\n'
from .runtime import native_cmds as cmds
import maya.mel as mel
from functools import partial
import math

class ConstraintBakeTool:

    def __init__(self):
        self.window_name = 'mtkRootMotionBakeCandidateWindow'
        self.window_title = '约束烘焙工具'
        self.root_field = None
        self.center_field = None
        self.ring_field = None
        self.translate_x_cb = None
        self.translate_y_cb = None
        self.translate_z_cb = None
        self.rotate_x_cb = None
        self.rotate_y_cb = None
        self.rotate_z_cb = None
        self.maintain_offset_cb = None
        self.time_range_radio = None
        self.object_groups = {}
        self.create_ui()
        self.auto_populate_objects()

    def create_ui(self):
        """创建用户界面"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)
        self.window = cmds.window(self.window_name, title=self.window_title, widthHeight=(400, 400), resizeToFitChildren=True, sizeable=True)
        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=('left', 10))
        cmds.frameLayout(label='对象选择', collapsable=False, borderStyle='in')
        objects_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 200, 100), adjustableColumn=2)
        cmds.text(label='1. Root:', align='left')
        self.root_field = cmds.textField()
        cmds.button(label='选择', command=partial(self.select_object, self.root_field))
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 200, 100), adjustableColumn=2)
        cmds.text(label='2. 质心:', align='left')
        self.center_field = cmds.textField()
        cmds.button(label='选择', command=partial(self.select_object, self.center_field))
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 200, 100), adjustableColumn=2)
        cmds.text(label='3. 大环:', align='left')
        self.ring_field = cmds.textField()
        cmds.button(label='选择', command=partial(self.select_object, self.ring_field))
        cmds.setParent('..')
        cmds.separator(height=5)
        cmds.button(label='重新扫描对象', height=25, backgroundColor=[0.4, 0.4, 0.6], command=self.refresh_objects)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.frameLayout(label='约束轴选择', collapsable=False, borderStyle='in')
        constraint_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        cmds.text(label='位移约束轴:', align='left')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 120, 120))
        self.translate_x_cb = cmds.checkBox(label='X轴位移', value=False)
        self.translate_y_cb = cmds.checkBox(label='Y轴位移', value=False)
        self.translate_z_cb = cmds.checkBox(label='Z轴位移', value=True)
        cmds.setParent('..')
        cmds.text(label='旋转约束轴:', align='left')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 120, 120))
        self.rotate_x_cb = cmds.checkBox(label='X轴旋转', value=False)
        self.rotate_y_cb = cmds.checkBox(label='Y轴旋转', value=False)
        self.rotate_z_cb = cmds.checkBox(label='Z轴旋转', value=False)
        cmds.setParent('..')
        cmds.separator(height=10)
        self.maintain_offset_cb = cmds.checkBox(label='保持偏移', value=True)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.frameLayout(label='时间范围', collapsable=False, borderStyle='in')
        time_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
        self.time_range_radio = cmds.radioButtonGrp(numberOfRadioButtons=2, labelArray2=['当前时间轴范围', '当前框选范围'], select=1, columnWidth2=(150, 150))
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.separator(height=10)
        cmds.button(label='执行', height=30, backgroundColor=[0.3, 0.7, 0.3], command=self.execute_workflow)
        cmds.showWindow(self.window)

    def auto_populate_objects(self):
        """自动收录对象"""
        try:
            all_transforms = cmds.ls(type='transform')
            keywords = {'root': 'root', 'center': 'rootx_m', 'ring': 'main'}
            found_objects = {'root': [], 'center': [], 'ring': []}
            for obj in all_transforms:
                obj_lower = obj.lower()
                for key, keyword in keywords.items():
                    if keyword in obj_lower:
                        found_objects[key].append(obj)
            self.object_groups = {}
            namespace_groups = {}
            for category in ['root', 'center', 'ring']:
                for obj in found_objects[category]:
                    if ':' in obj:
                        namespace = obj.split(':')[0]
                    else:
                        namespace = 'default'
                    if namespace not in namespace_groups:
                        namespace_groups[namespace] = {'root': None, 'center': None, 'ring': None}
                    if namespace_groups[namespace][category] is None:
                        namespace_groups[namespace][category] = obj
            valid_groups = {}
            for namespace, group in namespace_groups.items():
                valid_count = sum((1 for obj in group.values() if obj is not None))
                if valid_count >= 2:
                    valid_groups[namespace] = group
            self.object_groups = valid_groups
            if valid_groups:
                first_group = list(valid_groups.values())[0]
                if first_group['root']:
                    cmds.textField(self.root_field, edit=True, text=first_group['root'])
                if first_group['center']:
                    cmds.textField(self.center_field, edit=True, text=first_group['center'])
                if first_group['ring']:
                    cmds.textField(self.ring_field, edit=True, text=first_group['ring'])
                print(f'自动找到 {len(valid_groups)} 组对象:')
                for namespace, group in valid_groups.items():
                    print(f'  空间名称: {namespace}')
                    print(f"    Root: {group['root']}")
                    print(f"    质心: {group['center']}")
                    print(f"    大环: {group['ring']}")
            else:
                print('未找到匹配的对象组合')
        except Exception as e:
            print(f'自动收录对象时出错: {str(e)}')

    def refresh_objects(self, *args):
        """刷新对象扫描"""
        cmds.textField(self.root_field, edit=True, text='')
        cmds.textField(self.center_field, edit=True, text='')
        cmds.textField(self.ring_field, edit=True, text='')
        self.auto_populate_objects()
        print('对象扫描已刷新')

    def select_object(self, text_field, *args):
        """选择对象并填入文本框"""
        selection = cmds.ls(selection=True)
        if selection:
            cmds.textField(text_field, edit=True, text=selection[0])
        else:
            cmds.warning('请先选择一个对象')

    def get_constraint_axes(self):
        """获取约束轴设置"""
        translate_axes = []
        rotate_axes = []
        if cmds.checkBox(self.translate_x_cb, query=True, value=True):
            translate_axes.append('x')
        if cmds.checkBox(self.translate_y_cb, query=True, value=True):
            translate_axes.append('y')
        if cmds.checkBox(self.translate_z_cb, query=True, value=True):
            translate_axes.append('z')
        if cmds.checkBox(self.rotate_x_cb, query=True, value=True):
            rotate_axes.append('x')
        if cmds.checkBox(self.rotate_y_cb, query=True, value=True):
            rotate_axes.append('y')
        if cmds.checkBox(self.rotate_z_cb, query=True, value=True):
            rotate_axes.append('z')
        return (translate_axes, rotate_axes)

    def get_time_range(self):
        """获取时间范围"""
        range_option = cmds.radioButtonGrp(self.time_range_radio, query=True, select=True)
        if range_option == 1:
            start_time = cmds.playbackOptions(query=True, minTime=True)
            end_time = cmds.playbackOptions(query=True, maxTime=True)
        else:
            start_time = cmds.playbackOptions(query=True, animationStartTime=True)
            end_time = cmds.playbackOptions(query=True, animationEndTime=True)
        return (int(start_time), int(end_time))

    def create_constraint(self, root_obj, center_obj, translate_axes, rotate_axes, maintain_offset=True):
        """创建约束"""
        require_scope()
        constraints = []
        if translate_axes:
            skip_translate = []
            for axis in ['x', 'y', 'z']:
                if axis not in translate_axes:
                    skip_translate.append(axis)
            if len(skip_translate) < 3:
                point_constraint = cmds.pointConstraint(center_obj, root_obj, skip=skip_translate, maintainOffset=maintain_offset)[0]
                constraints.append(point_constraint)
        if rotate_axes:
            skip_rotate = []
            for axis in ['x', 'y', 'z']:
                if axis not in rotate_axes:
                    skip_rotate.append(axis)
            if len(skip_rotate) < 3:
                orient_constraint = cmds.orientConstraint(center_obj, root_obj, skip=skip_rotate, maintainOffset=maintain_offset)[0]
                constraints.append(orient_constraint)
        return constraints

    def bake_animation(self, obj, start_time, end_time):
        """烘焙动画"""
        require_scope()
        cmds.bakeResults(obj, time=(start_time, end_time), sampleBy=1, oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=False, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False, bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False, shape=False)

    def get_relative_transform(self, child_obj, parent_obj):
        """获取子物体相对父物体的变换"""
        child_matrix = cmds.xform(child_obj, query=True, worldSpace=True, matrix=True)
        parent_matrix = cmds.xform(parent_obj, query=True, worldSpace=True, matrix=True)
        child_pos = cmds.xform(child_obj, query=True, worldSpace=True, translation=True)
        parent_pos = cmds.xform(parent_obj, query=True, worldSpace=True, translation=True)
        child_rot = cmds.xform(child_obj, query=True, worldSpace=True, rotation=True)
        parent_rot = cmds.xform(parent_obj, query=True, worldSpace=True, rotation=True)
        relative_pos = [child_pos[i] - parent_pos[i] for i in range(3)]
        relative_rot = [child_rot[i] - parent_rot[i] for i in range(3)]
        return (relative_pos, relative_rot)

    def set_relative_transform(self, child_obj, parent_obj, relative_pos, relative_rot):
        """设置子物体相对父物体的变换"""
        require_scope()
        parent_pos = cmds.xform(parent_obj, query=True, worldSpace=True, translation=True)
        parent_rot = cmds.xform(parent_obj, query=True, worldSpace=True, rotation=True)
        new_pos = [parent_pos[i] + relative_pos[i] for i in range(3)]
        new_rot = [parent_rot[i] + relative_rot[i] for i in range(3)]
        cmds.xform(child_obj, worldSpace=True, translation=new_pos)
        cmds.xform(child_obj, worldSpace=True, rotation=new_rot)

    def execute_workflow(self, *args):
        """执行完整工作流程"""
        try:
            translate_axes, rotate_axes = self.get_constraint_axes()
            if not translate_axes and (not rotate_axes):
                cmds.error('请至少选择一个约束轴')
                return
            maintain_offset = cmds.checkBox(self.maintain_offset_cb, query=True, value=True)
            start_time, end_time = self.get_time_range()
            groups_to_process = []
            root_obj = cmds.textField(self.root_field, query=True, text=True).strip()
            center_obj = cmds.textField(self.center_field, query=True, text=True).strip()
            ring_obj = cmds.textField(self.ring_field, query=True, text=True).strip()
            if root_obj or center_obj or ring_obj:
                if not root_obj or not center_obj or (not ring_obj):
                    cmds.error('请填入所有三个对象名称')
                    return
                for obj in [root_obj, center_obj, ring_obj]:
                    if not cmds.objExists(obj):
                        cmds.error(f"对象 '{obj}' 不存在")
                        return
                groups_to_process.append({'root': root_obj, 'center': center_obj, 'ring': ring_obj, 'namespace': 'manual'})
            else:
                if not self.object_groups:
                    cmds.error('没有找到可处理的对象组，请手动填入对象名称')
                    return
                for namespace, group in self.object_groups.items():
                    if group['root'] and group['center']:
                        groups_to_process.append({'root': group['root'], 'center': group['center'], 'ring': group['ring'], 'namespace': namespace})
            if not groups_to_process:
                cmds.error('没有找到可处理的对象组')
                return
            print(f'开始执行工作流程，共 {len(groups_to_process)} 组对象...')
            print(f'时间范围: {start_time} - {end_time}')
            for i, group in enumerate(groups_to_process, 1):
                print(f"\n处理第 {i} 组对象 (空间名称: {group['namespace']}):")
                print(f"  Root对象: {group['root']}")
                print(f"  质心对象: {group['center']}")
                print(f"  大环对象: {group['ring']}")
                self.process_single_group(group['root'], group['center'], group['ring'], translate_axes, rotate_axes, maintain_offset, start_time, end_time)
            print(f'\n所有工作流程执行完成！处理了 {len(groups_to_process)} 组对象。')
            cmds.confirmDialog(title='完成', message=f'约束烘焙工具执行完成！\n处理了 {len(groups_to_process)} 组对象。', button=['确定'])
        except Exception as e:
            cmds.error(f'执行过程中出现错误: {str(e)}')

    def process_single_group(self, root_obj, center_obj, ring_obj, translate_axes, rotate_axes, maintain_offset, start_time, end_time):
        """处理单个对象组"""
        require_scope()
        try:
            print('  第一步：创建约束...')
            constraints = self.create_constraint(root_obj, center_obj, translate_axes, rotate_axes, maintain_offset)
            print('  第二步：烘焙动画...')
            self.bake_animation(root_obj, start_time, end_time)
            for constraint in constraints:
                if cmds.objExists(constraint):
                    cmds.delete(constraint)
            if ring_obj and cmds.objExists(ring_obj):
                print('  第三步：创建动画层...')
                layer_name = safe_layer_name(root_obj)
                anim_layer = cmds.animLayer(layer_name)
                cmds.select(root_obj, replace=True)
                cmds.animLayer(anim_layer, edit=True, addSelectedObjects=True)
                cmds.currentTime(start_time)
                initial_pos, initial_rot = self.get_relative_transform(root_obj, ring_obj)
                cmds.animLayer(anim_layer, edit=True, selected=True, preferred=True)
                cmds.setKeyframe(root_obj, time=start_time)
                cmds.currentTime(end_time)
                self.set_relative_transform(root_obj, ring_obj, initial_pos, initial_rot)
                cmds.setKeyframe(root_obj, time=end_time)
            else:
                print('  跳过第三步：没有大环对象')
            print(f'  组 {root_obj} 处理完成！')
        except Exception as e:
            print(f'  处理组 {root_obj} 时出错: {str(e)}')
            raise e

def show_constraint_bake_tool():
    """显示约束烘焙工具"""
    return ConstraintBakeTool()

from .ui_bridge import install
install(ConstraintBakeTool)
