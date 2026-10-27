import maya.cmds as cmds
import maya.mel as mel
import os
import json
import tempfile

class RelationshipTool:

    def __init__(self):
        self.window_name = 'RelationshipToolWindow'
        self.world_coordinate_mode = False
        self.world_transform_data = {}
        self.world_space_btn = None
        self.DEFAULT_MAX_ATTEMPTS = 6
        self.DEFAULT_FULL_CHECK_ATTEMPTS = 6
        self.TEMP_FILE_NAME = 'maya_world_transform_data.json'
        self.setup_ui()

    def get_temp_file_path(self):
        """获取临时文件路径"""
        temp_dir = tempfile.gettempdir()
        return os.path.join(temp_dir, self.TEMP_FILE_NAME)

    def setup_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        self.window = cmds.window(self.window_name, title='Relationship Tools', widthHeight=(200, 100), sizeable=True, resizeToFitChildren=True)
        self.main_layout = cmds.columnLayout(adj=True, rowSpacing=5)
        self.marking_frame = cmds.frameLayout(label='Marking Operations', collapsable=True, marginWidth=10, parent=self.main_layout, collapseCommand=self.adjust_window_size, expandCommand=self.adjust_window_size)
        inner1 = cmds.columnLayout(adj=True)
        form1 = cmds.formLayout(parent=inner1)
        self.create_equal_two_buttons(form1, {'label': 'Mark', 'command': self.mark_action, 'bgc': [0.4, 0.7, 0.4], 'annotation': '标记选择对象'}, {'label': 'Mark Foot', 'command': self.mark_foot_action, 'bgc': [1.0, 0.7, 0.4], 'annotation': '标记足部对象'})
        cmds.setParent('..')
        form2 = cmds.formLayout(parent=inner1)
        self.create_equal_two_buttons(form2, {'label': 'Mark Ani', 'command': self.mark_ani_action, 'bgc': [0.5, 0.7, 1.0], 'annotation': '标记动画控制器'}, {'label': 'World Space', 'command': self.world_space_action, 'bgc': [1.0, 1.0, 0.6], 'annotation': '复制选中对象的世界坐标'})
        cmds.setParent('..')
        cmds.setParent('..')
        self.keyframe_frame = cmds.frameLayout(label='Keyframe Operations', collapsable=True, marginWidth=10, parent=self.main_layout, collapseCommand=self.adjust_window_size, expandCommand=self.adjust_window_size)
        inner2 = cmds.columnLayout(adj=True)
        form3 = cmds.formLayout(parent=inner2)
        self.create_equal_two_buttons(form3, {'label': 'One Step', 'command': self.one_step_action, 'bgc': [0.6, 0.6, 0.6], 'annotation': '执行单步操作'}, {'label': 'More Step', 'command': self.more_step_action, 'bgc': [0.6, 0.6, 0.6], 'annotation': '执行多步操作'})
        cmds.setParent('..')
        cmds.setParent('..')
        self.options_frame = cmds.frameLayout(label='Options', collapsable=True, marginWidth=10, parent=self.main_layout, collapseCommand=self.adjust_window_size, expandCommand=self.adjust_window_size)
        options_grid = cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(95, 30))
        self.translate_checkbox = cmds.checkBox(label='Translate', value=True)
        self.rotate_checkbox = cmds.checkBox(label='Rotate', value=True)
        self.bake_checkbox = cmds.checkBox(label='Bake Ani', value=True, annotation='勾选时使用完整时间范围并应用步长优化，不勾选时只在有关键帧的帧上执行', changeCommand=self.toggle_step_field)
        step_row = cmds.rowLayout(numberOfColumns=2, columnAttach=[(1, 'left', 0), (2, 'left', 0)], columnWidth2=(35, 30))
        cmds.text(label='Step:', align='left')
        self.frame_step = cmds.intField(value=1, minValue=1, width=20, enable=True)
        cmds.setParent('..')
        self.world_coords_checkbox = cmds.checkBox(label='World Coords', value=False, annotation='启用后One Step和More Step将使用世界坐标模式')
        cmds.text(label='', enable=False)
        self.anim_layer_checkbox = cmds.checkBox(label='Layer', value=False, annotation='勾选后会创建新动画层执行操作')
        cmds.text(label='', enable=False)
        cmds.setParent('..')
        cmds.setParent('..')
        self.alignment_frame = cmds.frameLayout(label='Alignment', collapsable=True, marginWidth=10, parent=self.main_layout, collapseCommand=self.adjust_window_size, expandCommand=self.adjust_window_size)
        inner3 = cmds.columnLayout(adj=True)
        form4 = cmds.formLayout(parent=inner3)
        self.create_equal_two_buttons(form4, {'label': 'Align Objects', 'command': self.align_objects_action, 'bgc': [0.6, 0.6, 0.6], 'annotation': '对齐选择对象'}, {'label': 'Delete Marks', 'command': self.delete_marks_action, 'bgc': [0.9, 0.3, 0.3], 'annotation': '删除所有标记'})
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.button(label='by ZWJ', bgc=[0.4, 0.4, 0.4], command=self.by_zwj_action, parent=self.main_layout)
        cmds.showWindow(self.window)
        cmds.setFocus(self.main_layout)
        self.adjust_window_size()

    def create_equal_two_buttons(self, parent, btn1_info, btn2_info):
        """
        在给定的 formLayout parent 中创建两个按钮，使它们左右等分，并在中间和上下都留出间隙。
        """
        gap_percent = 1
        vertical_gap = 2
        btn1 = cmds.button(parent=parent, label=btn1_info.get('label', ''), command=btn1_info.get('command'), height=30, bgc=btn1_info.get('bgc', [0.5, 0.5, 0.5]), annotation=btn1_info.get('annotation', ''))
        btn2 = cmds.button(parent=parent, label=btn2_info.get('label', ''), command=btn2_info.get('command'), height=30, bgc=btn2_info.get('bgc', [0.5, 0.5, 0.5]), annotation=btn2_info.get('annotation', ''))
        if btn2_info.get('label') == 'World Space':
            self.world_space_btn = btn2
        cmds.formLayout(parent, edit=True, attachForm=[(btn1, 'top', vertical_gap), (btn1, 'left', 0), (btn1, 'bottom', vertical_gap), (btn2, 'top', vertical_gap), (btn2, 'right', 0), (btn2, 'bottom', vertical_gap)], attachPosition=[(btn1, 'right', 0, 50 - gap_percent), (btn2, 'left', 0, 50 + gap_percent)])

    def adjust_window_size(self, *args):
        """调整窗口大小以适应当前内容"""
        cmds.refresh()
        cmds.evalDeferred(lambda: cmds.window(self.window, edit=True, resizeToFitChildren=True))

    def toggle_step_field(self, *args):
        """根据Bake Ani选项状态切换Step字段的可用性"""
        is_bake_enabled = self.option('bake')
        cmds.intField(self.frame_step, edit=True, enable=is_bake_enabled)

    def create_locator(self, name, position, rotation):
        """创建一个定位器并设置其位置和旋转"""
        locator = cmds.spaceLocator(name=name)[0]
        cmds.xform(locator, translation=position, rotation=rotation)
        return locator

    def cleanup_scene(self):
        """清理场景中已存在的定位器"""
        existing_locators = cmds.ls('*:*_locatorPar', type='transform') + cmds.ls('*_locatorPar', type='transform') + cmds.ls('*:*_locatorTag', type='transform') + cmds.ls('*_locatorTag', type='transform')
        if existing_locators:
            cmds.delete(existing_locators)
            cmds.warning('已清理{}个定位器'.format(len(existing_locators)))

    def lock_and_hide(self, locators):
        """锁定并隐藏定位器的属性"""
        for loc in locators:
            for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
                cmds.setAttr('{}.{}'.format(loc, attr), lock=True)
            cmds.setAttr('{}.visibility'.format(loc), False)

    def parent_constraint(self, child, parent):
        """创建父级约束"""
        cmds.parentConstraint(parent, child, maintainOffset=False)

    def get_time_range(self):
        """获取当前时间范围"""
        playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
        if cmds.timeControl(playback_slider, query=True, rangeVisible=True):
            time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            return (int(time_range[0]), int(time_range[1]))
        else:
            start = int(cmds.playbackOptions(query=True, minTime=True))
            end = int(cmds.playbackOptions(query=True, maxTime=True)) + 1
            return (start, end)

    def get_attribute_options(self):
        """获取UI属性选项"""
        trans_opt = self.option('translate')
        rot_opt = self.option('rotate')
        translate_attrs = ['translateX', 'translateY', 'translateZ'] if trans_opt else []
        rotate_attrs = ['rotateX', 'rotateY', 'rotateZ'] if rot_opt else []
        keyframe_attrs = translate_attrs + rotate_attrs
        return (trans_opt, rot_opt, keyframe_attrs)

    def apply_transform_with_options(self, source_obj, target_obj, set_keyframe=False):
        """根据位移和旋转选项应用变换

        Args:
            source_obj: 源对象（提供变换数据）
            target_obj: 目标对象（接收变换）
            set_keyframe: 是否设置关键帧

        Returns:
            tuple: (trans_opt, rot_opt) 表示使用的变换选项
        """
        trans_opt, rot_opt, keyframe_attrs = self.get_attribute_options()
        if trans_opt:
            cmds.matchTransform(target_obj, source_obj, pos=True)
        if rot_opt:
            cmds.matchTransform(target_obj, source_obj, rot=True)
        if set_keyframe and keyframe_attrs:
            cmds.setKeyframe(target_obj, attribute=keyframe_attrs)
        return (trans_opt, rot_opt)

    def get_frame_step(self):
        """获取帧步长"""
        return self.option('step')

    def with_performance_optimization(self, func, *args, **kwargs):
        """性能优化包装器"""
        current_eval_mode = cmds.evaluationManager(query=True, mode=True)[0]
        cmds.evaluationManager(mode='off')
        cmds.refresh(suspend=True)
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            cmds.refresh(suspend=False)
            cmds.evaluationManager(mode=current_eval_mode)

    def optimize_keyframes(self, objects, start_frame, end_frame):
        """优化关键帧，按帧步长删除不必要的关键帧"""
        try:
            bake_enabled = self.option('bake')
            if not bake_enabled:
                return
            frame_step = self.get_frame_step()
            if frame_step <= 1:
                return
            valid_objects = [obj for obj in objects if cmds.objExists(obj)]
            if not valid_objects:
                return
            for frame in range(int(start_frame + 1), int(end_frame)):
                if frame % frame_step != 0:
                    cmds.cutKey(valid_objects, time=(frame, frame), clear=True)
        except Exception as e:
            cmds.warning('优化关键帧时出错: {}'.format(str(e)))

    def create_locator_system(self, parent_obj, child_objs):
        """创建定位器系统"""
        parent_short_name = cmds.ls(parent_obj, shortNames=True)[0]
        locator_par = self.create_locator(parent_short_name + '_locatorPar', [0, 0, 0], [0, 0, 0])
        cmds.matchTransform(locator_par, parent_obj, pos=True, rot=True)
        self.parent_constraint(locator_par, parent_obj)
        locator_tags = []
        for obj in child_objs:
            short_name = cmds.ls(obj, shortNames=True)[0]
            loc_name = short_name + '_locatorTag'
            loc_tag = self.create_locator(loc_name, [0, 0, 0], [0, 0, 0])
            cmds.matchTransform(loc_tag, obj, pos=True, rot=True)
            cmds.parent(loc_tag, locator_par)
            locator_tags.append(loc_tag)
        return (locator_par, locator_tags)

    def match_object_to_locator(self, obj, locator, trans_opt=None, rot_opt=None, keyframe_attrs=None):
        """将对象匹配到定位器的位置和旋转"""
        if trans_opt is None or rot_opt is None:
            trans_opt, rot_opt, keyframe_attrs = self.get_attribute_options()
        if trans_opt:
            cmds.matchTransform(obj, locator, pos=True)
        if rot_opt:
            cmds.matchTransform(obj, locator, rot=True)
        if keyframe_attrs:
            cmds.setKeyframe(obj, attribute=keyframe_attrs)

    def match_locator_to_object(self, locator, obj, keyframe_attrs=None):
        """将定位器匹配到对象的位置和旋转"""
        cmds.matchTransform(locator, obj, pos=True, rot=True)
        if keyframe_attrs:
            cmds.setKeyframe(locator, attribute=keyframe_attrs)

    def get_objects_and_locators(self, selection):
        """获取需要处理的对象和对应的定位器"""
        objects_to_process = []
        locator_map = {}
        if not selection:
            locator_tags = cmds.ls('*:*_locatorTag', type='transform') + cmds.ls('*_locatorTag', type='transform')
            if not locator_tags:
                cmds.warning('未找到任何定位器')
                return ([], {})
            for locator in locator_tags:
                if ':' in locator:
                    namespace = locator.rsplit(':', 1)[0] + ':'
                    base_name = locator.split(':')[-1]
                    obj_name = base_name.replace('_locatorTag', '')
                    full_obj_name = namespace + obj_name
                    if cmds.objExists(full_obj_name):
                        objects_to_process.append(full_obj_name)
                        locator_map[full_obj_name] = locator
                else:
                    obj_name = locator.replace('_locatorTag', '')
                    if cmds.objExists(obj_name):
                        objects_to_process.append(obj_name)
                        locator_map[obj_name] = locator
        else:
            for obj in selection:
                if ':' in obj:
                    namespace = obj.rsplit(':', 1)[0] + ':'
                    short_name = obj.split(':')[-1]
                    locator_name = namespace + short_name + '_locatorTag'
                else:
                    short_name = cmds.ls(obj, shortNames=True)[0]
                    locator_name = short_name + '_locatorTag'
                if cmds.objExists(locator_name):
                    objects_to_process.append(obj)
                    locator_map[obj] = locator_name
                else:
                    cmds.warning('未找到 {}，跳过匹配'.format(locator_name))
        if objects_to_process:
            cmds.warning('找到{}个需要处理的对象'.format(len(objects_to_process)))
        return (objects_to_process, locator_map)

    def get_object_keyframes(self, obj):
        """获取对象的所有关键帧时间"""
        keyframes = set()
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']:
            if cmds.objExists(f'{obj}.{attr}'):
                attr_keyframes = cmds.keyframe(obj, attribute=attr, query=True, timeChange=True)
                if attr_keyframes:
                    keyframes.update(attr_keyframes)
        if not keyframes:
            connections = cmds.listConnections(obj, type='animCurve') or []
            for curve in connections:
                curve_keyframes = cmds.keyframe(curve, query=True, timeChange=True)
                if curve_keyframes:
                    keyframes.update(curve_keyframes)
        result = sorted(list(keyframes))
        if result:
            print(f'找到对象 {obj} 的 {len(result)} 个关键帧')
        return result

    def sort_objects_by_hierarchy(self, objects):
        """按层级深度排序对象列表，优先处理上层级对象"""
        depth_map = {}
        for obj in objects:
            parents = cmds.listRelatives(obj, parent=True, fullPath=True) or []
            depth = 0
            while parents:
                depth += 1
                parents = cmds.listRelatives(parents[0], parent=True, fullPath=True) or []
            depth_map[obj] = depth
        return sorted(objects, key=lambda x: depth_map.get(x, 0))

    def mark_action(self, *args):
        """标记选中的对象，创建定位器系统"""
        self.cleanup_scene()
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning('请先选择物体')
            return
        parent_obj = selected[-1]
        child_objs = selected[:-1]
        if not child_objs:
            cmds.warning('至少需要选择两个物体')
            return
        locator_par, locator_tags = self.create_locator_system(parent_obj, child_objs)
        self.lock_and_hide([locator_par] + locator_tags)
        cmds.select(child_objs, replace=True)

    def one_step_action(self, *args):
        """执行单步对齐或粘贴操作"""
        self.process_step_operation(is_more_step=False)

    def more_step_action(self, *args):
        """执行多步对齐或粘贴操作"""
        self.process_step_operation(is_more_step=True)

    def process_step_operation(self, is_more_step=False):
        """统一的步骤处理框架

        Args:
            is_more_step: 是否是多步操作
        """
        world_coords_mode = self.option('world_coords')
        if world_coords_mode:
            if is_more_step:
                self.paste_world_transform_multiple()
            else:
                self.paste_world_transform_single()
            cmds.currentTime(cmds.currentTime(query=True) + 1, update=True)
        else:
            selection = cmds.ls(selection=True)
            objects_to_process, locator_map = self.get_objects_and_locators(selection)
            if not objects_to_process:
                return
            sorted_objects = self.sort_objects_by_hierarchy(objects_to_process)
            if is_more_step:
                self.perform_more_step_operation(sorted_objects, locator_map)
            else:
                self.perform_single_step_operation(sorted_objects, locator_map)
            cmds.currentTime(cmds.currentTime(query=True) + 1, update=True)
            if objects_to_process:
                cmds.select(objects_to_process, replace=True)

    def perform_single_step_operation(self, sorted_objects, locator_map):
        """执行单步操作的实现"""
        _, _, keyframe_attrs = self.get_attribute_options()

        def perform_one_step():
            max_attempts = self.DEFAULT_MAX_ATTEMPTS
            full_check_attempts = self.DEFAULT_FULL_CHECK_ATTEMPTS
            for attempt in range(max_attempts):
                all_success = True
                for obj in sorted_objects:
                    locator = locator_map[obj]
                    trans_opt, rot_opt = self.apply_transform_with_options(locator, obj, set_keyframe=False)
                    failed = False
                    if trans_opt:
                        obj_pos = cmds.xform(obj, q=True, ws=True, t=True)
                        loc_pos = cmds.xform(locator, q=True, ws=True, t=True)
                        if not self.is_close(obj_pos, loc_pos):
                            failed = True
                    if rot_opt and attempt < full_check_attempts:
                        obj_rot = cmds.xform(obj, q=True, ws=True, ro=True)
                        loc_rot = cmds.xform(locator, q=True, ws=True, ro=True)
                        if not self.angle_close(obj_rot, loc_rot):
                            failed = True
                    if failed:
                        all_success = False
                if all_success or attempt == max_attempts - 1:
                    if keyframe_attrs:
                        cmds.setKeyframe(sorted_objects, attribute=keyframe_attrs)
                    break
        self.use_anim_layer_if_enabled(sorted_objects, perform_one_step)

    def perform_more_step_operation(self, sorted_objects, locator_map):
        """执行多步操作的实现"""
        bake_ani = self.option('bake')
        if bake_ani:
            start, end = self.get_time_range()
            frames_to_process = list(range(start, end))
            cmds.inViewMessage(message='以时间范围{}到{}执行'.format(start, end), position='topCenter', fade=True)
        else:
            locator_pars = cmds.ls('*:*_locatorPar', type='transform') + cmds.ls('*_locatorPar', type='transform')
            if not locator_pars:
                cmds.warning('找不到定位器父级，无法获取关键帧信息。将使用完整时间范围')
                start, end = self.get_time_range()
                frames_to_process = list(range(start, end))
            else:
                all_keyframes = set()
                found_objects = []
                for locator_par in locator_pars:
                    parent_obj_name = ''
                    if ':' in locator_par:
                        namespace = locator_par.rsplit(':', 1)[0] + ':'
                        base_name = locator_par.split(':')[-1]
                        obj_base_name = base_name.replace('_locatorPar', '')
                        parent_obj_name = namespace + obj_base_name
                    else:
                        obj_base_name = locator_par.replace('_locatorPar', '')
                        parent_obj_name = obj_base_name
                    if cmds.objExists(parent_obj_name):
                        found_objects.append(parent_obj_name)
                        keyframes = self.get_object_keyframes(parent_obj_name)
                        if keyframes:
                            all_keyframes.update(keyframes)
                if not all_keyframes:
                    cmds.warning('源物体没有关键帧。将使用完整时间范围')
                    start, end = self.get_time_range()
                    frames_to_process = list(range(start, end))
                else:
                    frames_to_process = sorted(list(all_keyframes))
                    start, end = (min(frames_to_process), max(frames_to_process))
                    cmds.inViewMessage(message='在{}个关键帧上执行（来自{}个对象）'.format(len(frames_to_process), len(found_objects)), position='topCenter', fade=True)

        def perform_more_step():
            self.with_performance_optimization(self._perform_multi_step_process, sorted_objects, locator_map, frames_to_process)
        self.use_anim_layer_if_enabled(sorted_objects, perform_more_step)

    def _perform_multi_step_process(self, sorted_objects, locator_map, frames_to_process):
        """执行多步处理的内部方法"""
        _, _, keyframe_attrs = self.get_attribute_options()
        if not frames_to_process:
            return
        start, end = (min(frames_to_process), max(frames_to_process))
        for frame in frames_to_process:
            cmds.currentTime(frame, update=True)
            max_attempts = self.DEFAULT_MAX_ATTEMPTS
            full_check_attempts = self.DEFAULT_FULL_CHECK_ATTEMPTS
            for attempt in range(max_attempts):
                all_success = True
                for obj in sorted_objects:
                    locator = locator_map[obj]
                    trans_opt, rot_opt = self.apply_transform_with_options(locator, obj, set_keyframe=False)
                    failed = False
                    if trans_opt:
                        obj_pos = cmds.xform(obj, q=True, ws=True, t=True)
                        loc_pos = cmds.xform(locator, q=True, ws=True, t=True)
                        if not self.is_close(obj_pos, loc_pos):
                            failed = True
                    if rot_opt and attempt < full_check_attempts:
                        obj_rot = cmds.xform(obj, q=True, ws=True, ro=True)
                        loc_rot = cmds.xform(locator, q=True, ws=True, ro=True)
                        if not self.angle_close(obj_rot, loc_rot):
                            failed = True
                    if failed:
                        all_success = False
                if all_success or attempt == max_attempts - 1:
                    if keyframe_attrs:
                        cmds.setKeyframe(sorted_objects, attribute=keyframe_attrs)
                    break
        self.optimize_keyframes(sorted_objects, start, end)

    def _perform_mark_ani(self, child_objs, locator_tags, start, end):
        """执行动画标记的内部方法"""
        keyframe_attrs = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ']
        for frame in range(start, end + 1):
            cmds.currentTime(frame, update=True)
            for loc_tag, obj in zip(locator_tags, child_objs):
                self.match_locator_to_object(loc_tag, obj)
            if locator_tags:
                cmds.setKeyframe(locator_tags, attribute=keyframe_attrs)
        self.optimize_keyframes(locator_tags, start, end)

    def mark_ani_action(self, *args):
        """标记动画，为动画控制器创建定位器并记录动画轨迹"""
        self.cleanup_scene()
        selected = cmds.ls(selection=True, long=True)
        if len(selected) < 2:
            cmds.warning('请至少选择两个物体')
            return
        parent_obj = selected[-1]
        child_objs = selected[:-1]
        parent_short_name = cmds.ls(parent_obj, shortNames=True)[0]
        locator_par = self.create_locator(parent_short_name + '_locatorPar', [0, 0, 0], [0, 0, 0])
        cmds.matchTransform(locator_par, parent_obj, pos=True, rot=True)
        self.parent_constraint(locator_par, parent_obj)
        locator_tags = []
        start, end = self.get_time_range()
        for obj in child_objs:
            short_name = cmds.ls(obj, shortNames=True)[0]
            loc_name = short_name + '_locatorTag'
            loc_tag = self.create_locator(loc_name, [0, 0, 0], [0, 0, 0])
            cmds.parent(loc_tag, locator_par)
            locator_tags.append(loc_tag)
        self.with_performance_optimization(self._perform_mark_ani, child_objs, locator_tags, start, end)
        self.lock_and_hide([locator_par] + locator_tags)

    def _perform_world_space(self, child_objs, start, end):
        """执行世界空间转换的内部方法"""
        locator_tags = []
        for obj in child_objs:
            short_name = cmds.ls(obj, shortNames=True)[0]
            loc_name = short_name + '_locatorTag'
            loc_tag = self.create_locator(loc_name, [0, 0, 0], [0, 0, 0])
            locator_tags.append(loc_tag)
            for frame in range(start, end + 1):
                cmds.currentTime(frame, update=True)
                self.match_locator_to_object(loc_tag, obj)
                if frame == start:
                    cmds.setKeyframe(loc_tag, attribute=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ'])
        return locator_tags

    def world_space_action(self, *args):
        """复制选中对象的世界坐标"""
        self.copy_world_transform()

    def copy_world_transform(self):
        """复制选中对象的世界坐标"""
        self.world_transform_data = {}
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning('请先选择至少一个对象')
            return
        for obj in selected:
            short_name = cmds.ls(obj, shortNames=True)[0]
            pos = cmds.xform(obj, q=True, ws=True, t=True)
            rot = cmds.xform(obj, q=True, ws=True, ro=True)
            self.world_transform_data[obj] = {'pos': pos, 'rot': rot, 'short_name': short_name}
        temp_file = self.get_temp_file_path()
        try:
            with open(temp_file, 'w') as f:
                json.dump(self.world_transform_data, f)
            print(f'已复制 {len(selected)} 个对象的世界坐标，并保存到: {temp_file}')
        except Exception as e:
            cmds.warning(f'保存到临时文件失败: {e}')

    def mark_foot_action(self, *args):
        """标记足部对象"""
        self.cleanup_scene()
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning('请先选择物体')
            return
        locator_par = self.create_locator('foot_locatorPar', [0, 0, 0], [0, 0, 0])
        locator_tags = []
        for obj in selected:
            short_name = cmds.ls(obj, shortNames=True)[0]
            loc_name = short_name + '_locatorTag'
            loc_tag = self.create_locator(loc_name, [0, 0, 0], [0, 0, 0])
            cmds.matchTransform(loc_tag, obj, pos=True, rot=True)
            cmds.parent(loc_tag, locator_par)
            locator_tags.append(loc_tag)
        self.lock_and_hide([locator_par] + locator_tags)
        cmds.select(clear=True)

    def align_objects_action(self, *args):
        """对齐选择的对象"""
        selection = cmds.ls(selection=True)
        if not selection:
            cmds.warning('请选择物体进行对齐')
            return
        if len(selection) < 2:
            cmds.warning('请至少选择两个物体进行对齐，最后选择的物体为目标')
            return
        target_obj = selection[-1]
        source_objs = selection[:-1]
        trans_opt, rot_opt, keyframe_attrs = self.get_attribute_options()
        playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
        has_time_range = cmds.timeControl(playback_slider, query=True, rangeVisible=True)
        if has_time_range:
            time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            start_frame, end_frame = (int(time_range[0]), int(time_range[1]))
            bake_ani = self.option('bake')
            if bake_ani:
                frames_to_process = list(range(start_frame, end_frame))
                cmds.inViewMessage(message='以时间范围{}到{}执行'.format(start_frame, end_frame - 1), position='topCenter', fade=True)
            else:
                all_keyframes = set()
                target_keyframes = []
                if cmds.objExists(target_obj):
                    target_kfs = self.get_object_keyframes(target_obj)
                    target_keyframes = [kf for kf in target_kfs if start_frame <= kf < end_frame]
                    cmds.warning(f'目标对象 {target_obj} 在选定范围内有 {len(target_keyframes)} 个关键帧')
                for obj in source_objs:
                    keyframes = self.get_object_keyframes(obj)
                    filtered_keyframes = []
                    if keyframes:
                        for kf in keyframes:
                            if start_frame <= kf < end_frame:
                                filtered_keyframes.append(kf)
                                all_keyframes.add(kf)
                    cmds.warning(f'源对象 {obj} 在选定范围内找到 {len(filtered_keyframes)} 个关键帧')
                if target_keyframes:
                    all_keyframes.update(target_keyframes)
                    cmds.warning('同时包含目标对象的关键帧')
                if not all_keyframes:
                    cmds.warning('选择范围内没有关键帧，将使用完整时间范围')
                    frames_to_process = list(range(start_frame, end_frame))
                else:
                    frames_to_process = sorted(list(all_keyframes))
                    cmds.warning(f'总计找到 {len(frames_to_process)} 个唯一关键帧，时间范围从 {min(frames_to_process)} 到 {max(frames_to_process)}')
                    cmds.inViewMessage(message='在{}个关键帧上执行'.format(len(frames_to_process)), position='topCenter', fade=True)

            def perform_multi_frame_align():
                self.with_performance_optimization(self._perform_multi_frame_align, target_obj, source_objs, frames_to_process, trans_opt, rot_opt, keyframe_attrs)
            self.use_anim_layer_if_enabled(source_objs, perform_multi_frame_align)
            if bake_ani:
                cmds.inViewMessage(message='已在时间范围{}到{}内对齐对象'.format(start_frame, end_frame - 1), position='topCenter', fade=True)
            else:
                cmds.inViewMessage(message='已在{}个关键帧上对齐对象'.format(len(frames_to_process)), position='topCenter', fade=True)
        else:

            def perform_single_frame_align():
                self._perform_single_frame_align(target_obj, source_objs, trans_opt, rot_opt)
            self.use_anim_layer_if_enabled(source_objs, perform_single_frame_align)
        cmds.select(selection)

    def _perform_multi_frame_align(self, target_obj, source_objs, frames_to_process, trans_opt, rot_opt, keyframe_attrs):
        """执行多帧对齐操作"""
        sorted_source_objs = self.sort_objects_by_hierarchy(source_objs)
        if not frames_to_process:
            cmds.warning('没有找到需要处理的帧')
            return
        cmds.warning(f'将在{len(frames_to_process)}个帧上执行多帧对齐')
        for frame in frames_to_process:
            cmds.currentTime(frame, update=True)
            self._perform_single_frame_align(target_obj, sorted_source_objs, trans_opt, rot_opt)
            if keyframe_attrs:
                cmds.setKeyframe(sorted_source_objs, attribute=keyframe_attrs)
        if len(frames_to_process) > 1:
            start, end = (min(frames_to_process), max(frames_to_process))
            bake_ani = self.option('bake')
            if bake_ani:
                cmds.warning(f'正在优化关键帧，从{start}到{end}')
                self.optimize_keyframes(sorted_source_objs, start, end)
            else:
                cmds.warning('跳过关键帧优化（Bake Ani未启用）')

    def _perform_single_frame_align(self, target_obj, source_objs, trans_opt, rot_opt):
        """执行单帧对齐操作"""
        for obj in source_objs:
            if trans_opt:
                cmds.matchTransform(obj, target_obj, pos=True)
            if rot_opt:
                cmds.matchTransform(obj, target_obj, rot=True)

    def delete_marks_action(self, *args):
        """删除场景中的所有标记"""
        self.cleanup_scene()

    def by_zwj_action(self, *args):
        """显示作者信息"""
        cmds.confirmDialog(title='关于', message='Relationship Tools v15\n作者: ZWJ', button=['确定'], defaultButton='确定')

    def is_close(self, a, b, tol=0.01):
        """位置判断"""
        return all((abs(x - y) < tol for x, y in zip(a, b)))

    def angle_close(self, a, b, tol=0.01):
        """旋转判断，自动归一化"""

        def norm_angle(x):
            x = x % 360
            if x > 180:
                x -= 360
            return x
        return all((abs(norm_angle(x) - norm_angle(y)) < tol for x, y in zip(a, b)))

    def load_world_transform_data(self):
        """从临时文件加载世界坐标数据"""
        temp_file = self.get_temp_file_path()
        if os.path.exists(temp_file):
            try:
                with open(temp_file, 'r') as f:
                    self.world_transform_data = json.load(f)
                return True
            except Exception as e:
                cmds.warning(f'从临时文件加载数据失败: {e}')
        return False

    def paste_world_transform_single(self):
        """在当前帧粘贴世界坐标（单帧）"""
        if not self.load_world_transform_data():
            cmds.warning('没有可用的世界坐标数据，请先复制')
            return
        selected = cmds.ls(selection=True, long=True)
        objects_to_process = {}
        if selected:
            for obj in selected:
                if obj in self.world_transform_data:
                    objects_to_process[obj] = self.world_transform_data[obj]
        else:
            for obj, data in self.world_transform_data.items():
                if cmds.objExists(obj):
                    objects_to_process[obj] = data
        if not objects_to_process:
            cmds.warning('没有找到可处理的对象')
            return
        sorted_objects = self.sort_objects_by_hierarchy(list(objects_to_process.keys()))
        trans_opt, rot_opt, keyframe_attrs = self.get_attribute_options()

        def perform_paste():
            self._paste_world_transform_to_objects(sorted_objects, objects_to_process, trans_opt, rot_opt, keyframe_attrs)
        self.use_anim_layer_if_enabled(sorted_objects, perform_paste)
        if sorted_objects:
            cmds.select(sorted_objects, replace=True)

    def paste_world_transform_multiple(self):
        """在多个帧上粘贴世界坐标"""
        if not self.load_world_transform_data():
            cmds.warning('没有可用的世界坐标数据，请先复制')
            return
        selected = cmds.ls(selection=True, long=True)
        objects_to_process = {}
        if selected:
            for obj in selected:
                if obj in self.world_transform_data:
                    objects_to_process[obj] = self.world_transform_data[obj]
        else:
            for obj, data in self.world_transform_data.items():
                if cmds.objExists(obj):
                    objects_to_process[obj] = data
        if not objects_to_process:
            cmds.warning('没有找到可处理的对象')
            return
        sorted_objects = self.sort_objects_by_hierarchy(list(objects_to_process.keys()))
        frames_to_process = self._get_frames_to_process()

        def perform_paste_multiple():
            self.with_performance_optimization(self._perform_multi_step_paste, sorted_objects, objects_to_process, frames_to_process)
        self.use_anim_layer_if_enabled(sorted_objects, perform_paste_multiple)
        if sorted_objects:
            cmds.select(sorted_objects, replace=True)

    def _get_frames_to_process(self):
        """获取需要处理的帧列表，基于UI选项和时间范围"""
        bake_ani = self.option('bake')
        playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
        has_time_range = cmds.timeControl(playback_slider, query=True, rangeVisible=True)
        if has_time_range:
            time_range = cmds.timeControl(playback_slider, query=True, rangeArray=True)
            start_frame, end_frame = (int(time_range[0]), int(time_range[1]))
            cmds.warning(f'检测到时间轴选择范围: {start_frame} 到 {end_frame}')
        else:
            start_frame = int(cmds.playbackOptions(query=True, minTime=True))
            end_frame = int(cmds.playbackOptions(query=True, maxTime=True)) + 1
            cmds.warning(f'使用完整时间范围: {start_frame} 到 {end_frame}')
        if bake_ani:
            frames_to_process = list(range(start_frame, end_frame))
            cmds.inViewMessage(message='以时间范围{}到{}执行'.format(start_frame, end_frame - 1), position='topCenter', fade=True)
        else:
            all_keyframes = set()
            selected = cmds.ls(selection=True, long=True)
            object_keyframe_counts = {}
            objects_to_check = selected if selected else cmds.ls(assemblies=True)
            for obj in objects_to_check:
                keyframes = self.get_object_keyframes(obj)
                filtered_keyframes = []
                if keyframes:
                    for kf in keyframes:
                        if start_frame <= kf < end_frame:
                            filtered_keyframes.append(kf)
                            all_keyframes.add(kf)
                object_keyframe_counts[obj] = len(filtered_keyframes)
                if filtered_keyframes:
                    cmds.warning(f'对象 {obj} 在选定范围内找到 {len(filtered_keyframes)} 个关键帧')
            if not all_keyframes:
                cmds.warning('选择范围内没有关键帧，将使用完整时间范围')
                frames_to_process = list(range(start_frame, end_frame))
            else:
                frames_to_process = sorted(list(all_keyframes))
                cmds.warning(f'总计找到 {len(frames_to_process)} 个唯一关键帧，时间范围从 {min(frames_to_process)} 到 {max(frames_to_process)}')
                cmds.inViewMessage(message='在{}个关键帧上执行'.format(len(frames_to_process)), position='topCenter', fade=True)
        return frames_to_process

    def _perform_multi_step_paste(self, sorted_objects, objects_data, frames_to_process):
        """执行多帧世界坐标粘贴的内部方法"""
        if not frames_to_process:
            cmds.warning('没有找到需要处理的帧')
            return
        cmds.warning(f'将在{len(frames_to_process)}个帧上执行世界坐标粘贴')
        trans_opt, rot_opt, keyframe_attrs = self.get_attribute_options()
        if len(frames_to_process) > 1:
            start, end = (min(frames_to_process), max(frames_to_process))
            cmds.warning(f'处理帧范围: {start} 到 {end}')
        for frame in frames_to_process:
            cmds.currentTime(frame, update=True)
            self._paste_world_transform_to_objects(sorted_objects, objects_data, trans_opt, rot_opt, keyframe_attrs)
        if len(frames_to_process) > 1:
            start, end = (min(frames_to_process), max(frames_to_process))
            bake_ani = self.option('bake')
            if bake_ani:
                cmds.warning(f'正在优化关键帧，从{start}到{end}')
                self.optimize_keyframes(sorted_objects, start, end)
            else:
                cmds.warning('跳过关键帧优化（Bake Ani未启用）')

    def _paste_world_transform_to_objects(self, sorted_objects, objects_data, trans_opt, rot_opt, keyframe_attrs):
        """将世界坐标粘贴到对象，支持多次尝试"""
        max_attempts = self.DEFAULT_MAX_ATTEMPTS
        full_check_attempts = self.DEFAULT_FULL_CHECK_ATTEMPTS
        for attempt in range(max_attempts):
            all_success = True
            for obj in sorted_objects:
                if obj not in objects_data:
                    continue
                data = objects_data[obj]
                if trans_opt:
                    cmds.xform(obj, ws=True, t=data['pos'])
                if rot_opt:
                    cmds.xform(obj, ws=True, ro=data['rot'])
                failed = False
                if trans_opt:
                    cur_pos = cmds.xform(obj, q=True, ws=True, t=True)
                    if not self.is_close(cur_pos, data['pos']):
                        failed = True
                if rot_opt and attempt < full_check_attempts:
                    cur_rot = cmds.xform(obj, q=True, ws=True, ro=True)
                    if not self.angle_close(cur_rot, data['rot']):
                        failed = True
                if failed:
                    all_success = False
            if all_success or attempt == max_attempts - 1:
                if keyframe_attrs:
                    cmds.setKeyframe(sorted_objects, attribute=keyframe_attrs)
                break

    def create_anim_layer(self, objects, layer_name=None):
        """创建新的动画层并将对象添加到其中

        Args:
            objects: 要添加到动画层的对象列表
            layer_name: 动画层名称，如果不提供则自动生成

        Returns:
            创建的动画层名称
        """
        if not objects:
            return None
        if layer_name is None:
            existing_layers = cmds.ls('RTL_Layer_*')
            max_num = 0
            for layer in existing_layers:
                try:
                    num = int(layer.split('_')[-1])
                    max_num = max(max_num, num)
                except:
                    pass
            layer_name = f'RTL_Layer_{max_num + 1}'
        counter = 1
        base_name = layer_name
        while cmds.animLayer(layer_name, query=True, exists=True):
            layer_name = f'{base_name}_{counter}'
            counter += 1
        cmds.animLayer(layer_name)
        original_selection = cmds.ls(selection=True)
        cmds.select(objects, replace=True)
        cmds.animLayer(layer_name, edit=True, addSelectedObjects=True)
        if original_selection:
            cmds.select(original_selection, replace=True)
        else:
            cmds.select(clear=True)
        cmds.animLayer(layer_name, edit=True, preferred=True, selected=True)
        return layer_name

    def use_anim_layer_if_enabled(self, objects, func, *args, **kwargs):
        """如果启用了动画层选项，创建新动画层并在其中执行函数

        Args:
            objects: 要添加到动画层的对象
            func: 要执行的函数
            *args, **kwargs: 传递给函数的参数

        Returns:
            函数的返回值
        """
        use_anim_layer = self.option('layer')
        if not use_anim_layer or not objects:
            return func(*args, **kwargs)
        layer_name = self.create_anim_layer(objects)
        if not layer_name:
            return func(*args, **kwargs)
        try:
            cmds.animLayer(layer_name, edit=True, preferred=True, selected=True)
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            cmds.warning(f'在动画层中执行操作时出错: {e}')
            return func(*args, **kwargs)
